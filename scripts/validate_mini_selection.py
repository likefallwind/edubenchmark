#!/usr/bin/env python3
"""Offline validation of the mini_v1 curated selection (zero API calls).

For every model face with full per-item results, recompute each aggregation-
consumed cell's score on the mini subset and compare with the full-set score,
then re-run the *published* aggregation to compare P scores.  Produces the five
acceptance results from ``doc/mini_selection_plan_2026-07-19.md`` section 5:

  1. per-cell |dscore_10 (mini - full)| <= 0.3
  2. per-P    |d| <= 0.2
  3. model-ranking Kendall tau >= 0.9 (per cell and per P)
  4. leave-one-out drift on the held-out model
  5. bootstrap 95% CI half-width (QWK/macro-F1 cells <= 0.5 on the 0-10 scale
     == 0.05 raw; accuracy cells <= 0.2 == 2pp)

The recompute path reuses the benchmark adapters' own ``extra_summary`` plus the
aggregation's ``repo_metric_rows`` / ``normalize_score`` / ``score_atomic_p``, so
"self-calibration" (full recompute vs the published 08/09/10 artifacts) is a real
check that the recompute matches the pipeline.

Reads only ``reports/eval/`` (never writes there); all output goes to
``reports/mini_selection_v1/``.  Run with the miniconda interpreter (the adapters
need pandas/sacrebleu etc.):

    /home/likefallwind/miniconda3/bin/python scripts/validate_mini_selection.py
"""

from __future__ import annotations

import html
import json
import math
import random
import statistics
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_atomic_ability_rebenchmark_artifacts as agg  # noqa: E402
import build_mini_selection_v1 as bm  # noqa: E402
from eval.benchmarks import get_adapter  # noqa: E402
from eval.report import build_summary  # noqa: E402

REBENCH = ROOT / "reports" / "atomic_ability_rebenchmark_2026-07-08"
OUT_DIR = ROOT / "reports" / "mini_selection_v1"

SELFCAL_TOL = 0.01       # counts as reproducing the published number
SELFCAL_NEAR_TOL = 0.05  # rounding / import-protocol noise, reported not asserted
CELL_DELTA_THRESHOLD = 0.3
P_DELTA_THRESHOLD = 0.2
TAU_THRESHOLD = 0.9
LOO_RELAX = 0.4  # plan section 5.4 allows individual cells to relax to 0.4 under LOO
BOOTSTRAP_B = 300
CI_ACC_THRESHOLD = 0.2   # 2pp on the 0-10 scale (legacy absolute view, retained)
CI_STAT_THRESHOLD = 0.5  # 0.05 raw QWK/macro-F1 on the 0-10 scale (legacy)
# Relative CI criterion: measured CI inflation divided by the inflation pure
# random sampling would already produce, sqrt(N_full/N_mini).  1.0 means the
# stratified sample is exactly as efficient as random; 1.3 allows a 30% loss,
# which is roughly the spread bootstrap noise alone puts on this ratio at
# B=300 for the cell sizes here.
CI_EFFICIENCY_THRESHOLD = 1.3

# Cells whose metric is a population statistic (QWK/macro-F1/ASR): CI uses the
# looser 0.5 threshold; everything else is a per-item mean (accuracy family).
STAT_SUBDIMS = {
    "essay holistic QWK",
    "QWK holistic total score",
    "CCS step scoring consistency",
    "ECS error-cause consistency",
    "judge labels: mistake/guidance/actionability",
    "8-dimension tutor response judging",
    "Adversarial Safety ASR",
    "four-category knowledge-state diagnosis macro-F1",
}

EDUBENCH_METRICS = [
    "instruction_following", "tone_style_consistency", "content_relevance_scope_control",
    "scenario_element_integration", "basic_factual_accuracy", "domain_knowledge_accuracy",
    "reasoning_process_rigor", "error_identification_correction_accuracy",
    "clarity_concision_inspiration", "motivation_guidance_positive_feedback",
    "personalized_adaptation_learning_support", "higher_order_thinking_ability_development",
]
_EXPR = ("clarity_concision_inspiration", "scenario_element_integration")
_CORR = ("domain_knowledge_accuracy", "basic_factual_accuracy")


# --------------------------------------------------------------------------- #
# Cell recomputation
# --------------------------------------------------------------------------- #

def _edubench_cells(rows: list[dict[str, Any]]) -> dict[str, float]:
    by: dict[str, list[float]] = {}
    comp = {"tmg_pcc": [], "qg": [], "qgc": []}
    for r in rows:
        if r.get("score_status") != "scored":
            continue
        dims = r.get("dimension_scores") or {}
        task = (r.get("buckets") or {}).get("task", "unknown")
        for m in EDUBENCH_METRICS:
            v = dims.get(m)
            if v is not None and not math.isnan(float(v)):
                by.setdefault(m, []).append(float(v))

        def pair(ms):
            p = [float(dims[m]) for m in ms if dims.get(m) is not None and not math.isnan(float(dims[m]))]
            return sum(p) / len(p) if p else None

        if task in {"TMG", "PCC"}:
            x = pair(_EXPR)
            if x is not None:
                comp["tmg_pcc"].append(x)
        if task == "QG":
            x = pair(_EXPR)
            if x is not None:
                comp["qg"].append(x)
            y = pair(_CORR)
            if y is not None:
                comp["qgc"].append(y)
    out: dict[str, float] = {}
    for m, vs in by.items():
        out[f"{m} (metric)"] = sum(vs) / len(vs)  # likert_0_to_10 identity
    if comp["tmg_pcc"]:
        out["TMG/PCC × clarity_concision_inspiration + scenario_element_integration (task×metric)"] = (
            sum(comp["tmg_pcc"]) / len(comp["tmg_pcc"]))
    if comp["qg"]:
        out["QG × clarity_concision_inspiration + scenario_element_integration (task×metric)"] = (
            sum(comp["qg"]) / len(comp["qg"]))
    if comp["qgc"]:
        out["QG × domain_knowledge_accuracy + basic_factual_accuracy (task×metric)"] = (
            sum(comp["qgc"]) / len(comp["qgc"]))
    return out


def _to_int(x):
    if isinstance(x, int):
        return x
    if isinstance(x, str) and x.strip().lstrip("-").isdigit():
        return int(x)
    return None


def _prep_asap(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    for r in rows:
        n = _to_int(r.get("normalized"))
        g = _to_int(r.get("gold"))
        r["normalized"] = n
        r["gold"] = g
        if n is not None and g is not None:
            r["exact"] = (n == g)
            r["adjacent"] = abs(n - g) <= 1
        else:
            r["exact"] = False
            r["adjacent"] = False
    return rows


def _clean_sas(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Some imported SAS faces persist step errors as dicts; the official _ecs
    port mixes ``str(error)`` and raw ``error`` lookups and chokes on non-strings.
    Stringify error entries consistently (applied to full and subset alike, so
    per-cell drift stays apples-to-apples)."""
    out = []
    for r in rows:
        r = dict(r)
        for key in ("step_gold", "step_pred"):
            steps = r.get(key)
            if isinstance(steps, list):
                new_steps = []
                for step in steps:
                    if isinstance(step, dict):
                        step = dict(step)
                        errs = step.get("errors")
                        if isinstance(errs, list):
                            step["errors"] = [e if isinstance(e, str) else json.dumps(e, ensure_ascii=False, sort_keys=True) for e in errs]
                    new_steps.append(step)
                r[key] = new_steps
        out.append(r)
    return out


_ADAPTER_CACHE: dict[str, Any] = {}


def _adapter(bid: str):
    if bid not in _ADAPTER_CACHE:
        _ADAPTER_CACHE[bid] = get_adapter(bid)
    return _ADAPTER_CACHE[bid]


def recompute_from_rows(bid: str, rows: list[dict[str, Any]]) -> dict[str, float]:
    """Map a list of scored rows to {consumed subdimension: score_10}."""
    if not rows:
        return {}
    if bid == "edubench":
        raw = _edubench_cells(rows)
        out = {}
        for sub, val in raw.items():
            mp = agg.find_mapping(bid, subdimension=sub, metric="likert_0_to_10")
            if mp is not None:
                s10 = agg.normalize_score("likert_0_to_10", float(val))
                if s10 is not None:
                    out[mp["subdimension"]] = max(0.0, min(10.0, s10))
        return out

    ad = _adapter(bid)
    if bid == "asap_2":
        rows = _prep_asap(list(rows))
    elif bid == "sas_bench":
        rows = _clean_sas(rows)
    model = "recompute"
    bk = list((rows[0].get("buckets") or {}).keys())
    summ = build_summary(bid, model, rows, bk)
    ex = ad.extra_summary(rows)
    if ex:
        summ["extra_metrics"] = ex
    out: dict[str, float] = {}
    for mr in agg.repo_metric_rows(bid, summ):
        mp = agg.find_mapping(bid, subdimension=mr["subdimension"], metric=mr["metric"])
        if mp is None:
            continue
        s10 = agg.normalize_score(mr["metric"], float(mr["value"]))
        if s10 is None:
            continue
        out[mp["subdimension"]] = max(0.0, min(10.0, s10))
    return out


def recompute_cells(bid: str, face_dir: Path, subset_ids: set[str] | None) -> dict[str, float]:
    rows = bm.read_scored(face_dir / "scored.jsonl")
    if subset_ids is not None:
        rows = [r for r in rows if str(r["item_id"]) in subset_ids]
    return recompute_from_rows(bid, rows)


# --------------------------------------------------------------------------- #
# Stats helpers (stdlib only)
# --------------------------------------------------------------------------- #

def kendall_tau(x: list[float], y: list[float]) -> float | None:
    """Kendall tau-b for paired ranking of models. None if < 3 pairs."""
    n = len(x)
    if n < 3:
        return None
    conc = disc = tx = ty = 0
    for i in range(n):
        for j in range(i + 1, n):
            dx = x[i] - x[j]
            dy = y[i] - y[j]
            if dx == 0 and dy == 0:
                continue
            if dx == 0:
                tx += 1
                continue
            if dy == 0:
                ty += 1
                continue
            if (dx > 0) == (dy > 0):
                conc += 1
            else:
                disc += 1
    n0 = n * (n - 1) / 2
    denom = math.sqrt((n0 - tx) * (n0 - ty))
    if denom == 0:
        return None
    return (conc - disc) / denom


def kendall_tau_meaningful(full: list[float], mini: list[float], noise: float | None):
    """Kendall tau counting only model pairs the full set can actually separate.

    Round-2 decision: plain tau over all pairs punishes swaps between models whose
    full-set scores differ by less than the measurement noise -- a coin flip we
    have no business calling a failure -- and at n=9 a single adjacent swap already
    drops tau to 0.889, so the 0.9 gate effectively demanded zero swaps.  A pair is
    "meaningful" when the full-set gap exceeds the cell's own bootstrap CI
    half-width.  Returns (tau, n_meaningful_pairs, n_pairs_total).
    """
    n = len(full)
    total_pairs = n * (n - 1) // 2
    if noise is None or n < 2:
        return None, 0, total_pairs
    conc = disc = 0
    for i in range(n):
        for j in range(i + 1, n):
            gap = full[i] - full[j]
            if abs(gap) <= noise:
                continue  # statistically indistinguishable on the full set
            d = mini[i] - mini[j]
            if d == 0:
                continue
            if (gap > 0) == (d > 0):
                conc += 1
            else:
                disc += 1
    meaningful = conc + disc
    if meaningful == 0:
        return None, 0, total_pairs
    return (conc - disc) / meaningful, meaningful, total_pairs


def p_noise_scales(evidence_rows: list[dict[str, Any]],
                   cell_ci: dict[tuple[str, str], float]) -> dict[tuple[str, str], dict[str, Any]]:
    """Propagate per-cell sampling CIs through the aggregation into a per-P noise scale.

    The aggregation is exactly
        P = mean over facets of ( sum_c w_c * s_c / sum_c w_c ),
    so d(P)/d(s_c) = (1/F) * w_c / W_facet.  First-order propagation with
    independent cells gives
        noise_P = sqrt( sum_c ( coef_c * CI_c )^2 ).

    Cells from benchmarks the curation does not touch contribute 0 by
    construction: they are byte-identical between the mini and full runs, so they
    cannot contribute to mini-vs-full drift.  Cells whose bootstrap CI could not
    be computed also contribute 0 and are counted in ``cells_without_ci``.

    Independence is the one assumption here.  Cells that share items (sas
    QWK/CCS/ECS) are positively correlated, so the true noise is larger than this
    estimate -- which makes the resulting tau criterion STRICTER, not looser
    (a smaller noise scale admits more pairs as separable).  That is the
    conservative direction, so the assumption cannot inflate a pass.
    """
    by_model_p: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for ev in evidence_rows:
        by_model_p.setdefault((ev["model_key"], ev["p_code"]), []).append(ev)

    out: dict[tuple[str, str], dict[str, Any]] = {}
    for key, evs in by_model_p.items():
        facet_w: dict[str, float] = {}
        for ev in evs:
            facet_w[ev["facet_id"]] = facet_w.get(ev["facet_id"], 0.0) + ev["effective_weight"]
        n_facets = len([f for f, w in facet_w.items() if w])
        if not n_facets:
            continue
        var = 0.0
        missing = 0
        imputed_w = 0.0
        total_w = 0.0
        for ev in evs:
            wf = facet_w.get(ev["facet_id"], 0.0)
            if not wf:
                continue
            total_w += ev["effective_weight"]
            if ev.get("imputed"):
                imputed_w += ev["effective_weight"]
            coef = (1.0 / n_facets) * ev["effective_weight"] / wf
            ci = cell_ci.get((ev["benchmark_id"], ev["subdimension"]))
            if ci is None:
                # Curated cell with no CI estimate -> counted; uncurated cell ->
                # genuinely zero drift, not missing.
                if (ev["benchmark_id"], ev["subdimension"]) in CURATED_CELLS:
                    missing += 1
                continue
            var += (coef * ci) ** 2
        out[key] = {
            "noise": math.sqrt(var),
            "cells_without_ci": missing,
            "imputed_weight_share": (imputed_w / total_w) if total_w else 0.0,
        }
    return out


CURATED_CELLS: set[tuple[str, str]] = set()


def bootstrap_ci_halfwidth(bid: str, subset_rows: list[dict[str, Any]], subdim: str, b: int) -> float | None:
    """95% CI half-width of a cell's score_10 under item resampling of the mini
    subset (score_10 units; == raw*10 for QWK/macro-F1, == pp/10 for accuracy)."""
    if len(subset_rows) < 5:
        return None
    rng = random.Random(bm.sha_rng_seed("bootstrap", bid, subdim))
    vals: list[float] = []
    n = len(subset_rows)
    for _ in range(b):
        sample = [subset_rows[rng.randrange(n)] for _ in range(n)]
        cells = recompute_from_rows(bid, sample)
        if subdim in cells:
            vals.append(cells[subdim])
    if len(vals) < b * 0.5:
        return None
    vals.sort()
    lo = vals[int(0.025 * len(vals))]
    hi = vals[min(len(vals) - 1, int(0.975 * len(vals)))]
    return (hi - lo) / 2.0


# --------------------------------------------------------------------------- #
# Main validation
# --------------------------------------------------------------------------- #

def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(l) for l in path.open(encoding="utf-8") if l.strip()]


def face_is_native(face_dir: Path) -> bool:
    """True when this face was produced by this repo's runner (summary.json carries
    the runner's lifecycle fields).  Imported colleague faces carry externally
    computed metrics that a per-item recompute cannot be expected to reproduce."""
    summ = face_dir / "summary.json"
    if not summ.exists():
        return False
    try:
        data = json.loads(summ.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    return any(k in data for k in ("run_status", "started_at", "completed_at"))


def cell_recompute_all(benches, subset_map):
    """Return full[cell][mk] and mini[cell][mk] recomputed score_10, plus the
    mini subset rows of a representative face per (bench) for bootstrap."""
    full: dict[str, dict[str, float]] = {}
    mini: dict[str, dict[str, float]] = {}
    boot_rows: dict[str, list[dict[str, Any]]] = {}
    face_index: dict[str, list[tuple[str, Path]]] = {}
    face_native: dict[tuple[str, str], bool] = {}
    for bench in benches:
        subset_ids = subset_map.get(bench.bid)
        if subset_ids is None:
            continue
        faces = bm.discover_faces(bench)
        face_index[bench.bid] = [(f["model_key"], f["dir"]) for f in faces]
        for f in faces:
            mk = f["model_key"]
            face_native[(bench.bid, mk)] = face_is_native(f["dir"])
            fc = recompute_cells(bench.bid, f["dir"], None)
            mc = recompute_cells(bench.bid, f["dir"], subset_ids)
            for sub, v in fc.items():
                full.setdefault(sub, {})[mk] = v
            for sub, v in mc.items():
                mini.setdefault(sub, {})[mk] = v
        # representative face for bootstrap: prefer minimax3, else first
        rep = next((f for f in faces if f["model_key"] == "minimax-m3"), faces[0] if faces else None)
        if rep is not None:
            rows = bm.read_scored(rep["dir"] / "scored.jsonl")
            boot_rows[bench.bid] = {
                "full": rows,
                "mini": [r for r in rows if str(r["item_id"]) in subset_ids],
            }
    return full, mini, boot_rows, face_index, face_native


def subdim_to_bench(benches) -> dict[str, str]:
    m = {}
    for bench in benches:
        if bench.bid == "edubench":
            for l in load_jsonl(REBENCH / "08_selected_score_evidence.jsonl"):
                if l["benchmark_id"] == "edubench":
                    m[l["subdimension"]] = "edubench"
        else:
            for c in bench.cells:
                m[c] = bench.bid
    return m


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((ROOT / "data" / "mini_selection_v1" / "selection_manifest.json").read_text())
    curated = {b: manifest["benchmarks"][b] for b in manifest["benchmarks"]}
    benches = [b for b in bm.BENCHES if b.bid in curated]
    subset_map = {}
    for b in benches:
        list_path = ROOT / "data" / "mini_selection_v1" / f"{b.bid}_items_v1.txt"
        ids = [ln.strip() for ln in list_path.read_text(encoding="utf-8").splitlines() if ln.strip()]
        subset_map[b.bid] = set(ids)

    pub08 = load_jsonl(REBENCH / "08_selected_score_evidence.jsonl")
    pub09 = load_jsonl(REBENCH / "09_atomic_p_scores.jsonl")
    pub10 = load_jsonl(REBENCH / "10_group_scores.jsonl")
    pub_cell = {(r["model_key"], r["benchmark_id"], r["subdimension"]): r["score_10"] for r in pub08}
    pub_cell_src = {(r["model_key"], r["benchmark_id"], r["subdimension"]): r["source_type"] for r in pub08}

    # ---- (0) Self-calibration: reuse score_atomic_p on the published evidence.
    # NB: score_atomic_p returns (evidence_rows, p_rows, group_rows) -- unpacking
    # the first slot as P rows silently yields per-cell evidence instead, which
    # makes every P look like a single cell's score.
    _full_evidence, full_p_rows, full_group_rows = agg.score_atomic_p(pub08)
    pub_p = {(r["model_key"], r["p_code"]): r["score_10"] for r in pub09}
    recomp_p = {(r["model_key"], r["p_code"]): r["score_10"] for r in full_p_rows}
    p_selfcal_maxdiff = max(
        (abs((pub_p[k] or 0) - (recomp_p.get(k) or 0)) for k in pub_p if pub_p[k] is not None),
        default=0.0,
    )

    # ---- Cell recompute (full + mini) for every curated cell x model face.
    full_cells, mini_cells, boot_rows, face_index, face_native = cell_recompute_all(benches, subset_map)
    sub2bench = subdim_to_bench(benches)

    # ---- Cell self-calibration: my full recompute vs published 08.
    # A cell/face is only expected to tie when the published number came from a
    # face this repo's runner actually produced.  Imported colleague faces carry
    # externally computed metrics (and asap_2's published score comes from the
    # 0701 HTML card, not the repo run), so those are reported, not asserted.
    cell_selfcal = []
    for sub, mk_vals in sorted(full_cells.items()):
        bid = sub2bench.get(sub, "?")
        for mk, val in sorted(mk_vals.items()):
            pub = pub_cell.get((mk, bid, sub))
            src = pub_cell_src.get((mk, bid, sub))
            native = face_native.get((bid, mk), False)
            gap = abs(pub - val) if pub is not None else None
            # Classify by the ACTUAL gap; provenance only explains a gap, it does
            # not excuse one in advance (most imported faces reconcile exactly).
            if gap is None:
                status, reason = "no_published_value", "no published row for this model face"
            elif gap <= SELFCAL_TOL:
                status, reason = "reconciled", None
            elif gap <= SELFCAL_NEAR_TOL:
                status = "near_reconciled"
                reason = ("imported face; this metric depends only on labels the import "
                          "preserved, so it lands within rounding/protocol noise")
            else:
                status = "unreconciled"
                if bid == "asap_2":
                    reason = "published value comes from the 0701 otherbenchmark HTML card, not the repo run"
                elif not native:
                    reason = ("imported face: published metric was computed externally by the "
                              "colleague's scorer; this repo's port cannot reproduce it from the "
                              "converted per-item data")
                else:
                    reason = "unexplained: natively-run face that does not reproduce"
            cell_selfcal.append({
                "benchmark": bid, "subdimension": sub, "model_key": mk,
                "recompute": round(val, 4), "published": pub,
                "published_source": src, "face": "native" if native else "imported",
                "gap": round(gap, 4) if gap is not None else None,
                "status": status, "untied_reason": reason,
                "tied_to_published": status in ("reconciled", "near_reconciled"),
            })
    reconciled = [c for c in cell_selfcal if c["status"] == "reconciled"]
    near = [c for c in cell_selfcal if c["status"] == "near_reconciled"]
    untied = [c for c in cell_selfcal if c["status"] == "unreconciled"]
    cell_selfcal_maxgap = max((c["gap"] for c in reconciled), default=0.0)

    # ---- (1) per-cell delta + (3) per-cell tau.
    cell_results = []
    for sub in sorted(full_cells):
        bid = sub2bench.get(sub, "?")
        mks = sorted(set(full_cells[sub]) & set(mini_cells.get(sub, {})))
        deltas = {mk: mini_cells[sub][mk] - full_cells[sub][mk] for mk in mks}
        max_abs = max((abs(d) for d in deltas.values()), default=0.0)
        fx = [full_cells[sub][mk] for mk in mks]
        mx = [mini_cells[sub][mk] for mk in mks]
        tau = kendall_tau(fx, mx)
        cell_results.append({
            "benchmark": bid, "subdimension": sub, "n_models": len(mks),
            "max_abs_delta": round(max_abs, 4),
            "pass_delta": max_abs <= CELL_DELTA_THRESHOLD,
            "tau": round(tau, 4) if tau is not None else None,
            "pass_tau": (tau is None) or (tau >= TAU_THRESHOLD),
            "per_model": {mk: {"full": round(full_cells[sub][mk], 4),
                               "mini": round(mini_cells[sub][mk], 4),
                               "delta": round(deltas[mk], 4)} for mk in mks},
        })

    # ---- (2) per-P delta + tau: swap curated cell score_10 into the published
    # evidence, re-run score_atomic_p, compare P scores.
    # Both sides must come from the SAME recompute, otherwise a cell whose
    # published value was computed externally (imported sas CCS/ECS) contributes
    # its provenance offset to the "drift" instead of the sampling effect.
    def swap(source: dict[str, dict[str, float]]) -> list[dict[str, Any]]:
        out = []
        for r in pub08:
            r2 = dict(r)
            key = r["subdimension"]
            mk = r["model_key"]
            if key in source and mk in source[key] and r["benchmark_id"] == sub2bench.get(key):
                r2["score_10"] = source[key][mk]
            out.append(r2)
        return out

    _fe, full_swapped_p_rows, full_swapped_group_rows = agg.score_atomic_p(swap(full_cells))
    _mini_evidence, mini_p_rows, mini_group_rows = agg.score_atomic_p(swap(mini_cells))
    baseline_p = {(r["model_key"], r["p_code"]): r["score_10"] for r in full_swapped_p_rows}
    mini_p = {(r["model_key"], r["p_code"]): r["score_10"] for r in mini_p_rows}
    full_group_rows = full_swapped_group_rows

    p_results = []
    p_codes = sorted({k[1] for k in baseline_p})
    for pc in p_codes:
        mks = sorted({k[0] for k in baseline_p if k[1] == pc and baseline_p[(k[0], pc)] is not None})
        rows = []
        fv = []
        mvv = []
        mks_used = []
        max_abs = 0.0
        for mk in mks:
            f = baseline_p.get((mk, pc))
            m = mini_p.get((mk, pc))
            if f is None or m is None:
                continue
            d = m - f
            max_abs = max(max_abs, abs(d))
            rows.append({"model_key": mk, "full": round(f, 4), "mini": round(m, 4), "delta": round(d, 4)})
            fv.append(f)
            mvv.append(m)
            mks_used.append(mk)
        tau = kendall_tau(fv, mvv)
        p_results.append({
            "p_code": pc, "n_models": len(rows),
            "max_abs_delta": round(max_abs, 4),
            "pass_delta": max_abs <= P_DELTA_THRESHOLD,
            # raw all-pairs tau, retained for audit
            "tau_raw": round(tau, 4) if tau is not None else None,
            "pass_tau_raw": (tau is None) or (tau >= TAU_THRESHOLD),
            "tau": round(tau, 4) if tau is not None else None,
            "pass_tau": (tau is None) or (tau >= TAU_THRESHOLD),
            "per_model": rows,
            "_model_keys": mks_used,
        })

    # ---- (4) Leave-one-out (benches with >= MIN_FACES_FOR_DIFFICULTY faces).
    loo_results = []
    loo_worst = {"benchmark": None, "subdimension": None, "model_key": None, "delta": 0.0}
    for bench in benches:
        faces = bm.discover_faces(bench)
        if len(faces) < bm.MIN_FACES_FOR_DIFFICULTY:
            continue
        for f in faces:
            mk = f["model_key"]
            res = bm.select_benchmark(bench, exclude_model_key=mk)
            if res is None:
                continue
            loo_ids = set(res["selected_ids"])
            full_c = recompute_cells(bench.bid, f["dir"], None)
            loo_c = recompute_cells(bench.bid, f["dir"], loo_ids)
            for sub in sorted(set(full_c) & set(loo_c)):
                d = loo_c[sub] - full_c[sub]
                loo_results.append({"benchmark": bench.bid, "subdimension": sub,
                                    "held_out_model": mk, "delta": round(d, 4),
                                    "pass": abs(d) <= LOO_RELAX})
                if abs(d) > abs(loo_worst["delta"]):
                    loo_worst = {"benchmark": bench.bid, "subdimension": sub,
                                 "model_key": mk, "delta": round(d, 4)}

    # ---- (5) Bootstrap CI, RELATIVE criterion (round-2 decision).
    # The absolute thresholds were mis-specified: 13 cells needed more items than
    # the benchmark contains, i.e. the FULL set fails them too, so they measured
    # the benchmark's intrinsic precision rather than the curation's fidelity.
    # We now bootstrap both the full and the mini set and ask whether stratified
    # sampling did worse than plain random sampling would have:
    #     ratio       = mini_CI / full_CI
    #     theoretical = sqrt(N_full / N_mini)   (pure random sampling)
    #     efficiency  = ratio / theoretical     (1.0 = as good as random, <1 better)
    # Full-vs-itself is identically 1.0, so the criterion is self-consistent.
    # Absolute half-widths are retained alongside so nothing is hidden.
    ci_results = []
    for sub in sorted(full_cells):
        bid = sub2bench.get(sub, "?")
        rows = boot_rows.get(bid)
        if not rows:
            continue
        # For partitioned cells, restrict rows to the cell's own subset.
        cell_rows = _cell_subset_rows(bid, sub, rows["mini"])
        cell_rows_full = _cell_subset_rows(bid, sub, rows["full"])
        hw = bootstrap_ci_halfwidth(bid, cell_rows, sub, BOOTSTRAP_B)
        hw_full = bootstrap_ci_halfwidth(bid, cell_rows_full, sub, BOOTSTRAP_B)
        ratio = (hw / hw_full) if (hw is not None and hw_full) else None
        theoretical = (math.sqrt(len(cell_rows_full) / len(cell_rows))
                       if cell_rows and cell_rows_full else None)
        efficiency = (ratio / theoretical) if (ratio is not None and theoretical) else None
        threshold = CI_STAT_THRESHOLD if sub in STAT_SUBDIMS else CI_ACC_THRESHOLD
        # A cell whose CI could not be computed is NOT a pass -- reporting it as
        # one hides the fact that we have no precision estimate for it.
        ci_results.append({
            "benchmark": bid, "subdimension": sub,
            "kind": "stat" if sub in STAT_SUBDIMS else "accuracy/mean",
            "n_items": len(cell_rows), "n_items_full": len(cell_rows_full),
            # --- raw absolute values, kept on purpose so the old view stays auditable
            "ci_halfwidth_score10": round(hw, 4) if hw is not None else None,
            "ci_halfwidth_full_score10": round(hw_full, 4) if hw_full is not None else None,
            "abs_threshold": threshold,
            "pass_abs_legacy": hw is not None and hw <= threshold,
            "n_needed_for_abs_threshold": (
                None if hw is None or hw <= threshold
                else int(round(len(cell_rows) * (hw / threshold) ** 2))
            ),
            # --- relative criterion (the one that now gates)
            "ci_ratio_mini_over_full": round(ratio, 4) if ratio is not None else None,
            "ci_ratio_theoretical": round(theoretical, 4) if theoretical is not None else None,
            "sampling_efficiency": round(efficiency, 4) if efficiency is not None else None,
            "efficiency_threshold": CI_EFFICIENCY_THRESHOLD,
            "status": "computed" if efficiency is not None else "not_computed",
            "pass": efficiency is not None and efficiency <= CI_EFFICIENCY_THRESHOLD,
        })

    # ---- Criterion 3 (revised): recompute tau over separable pairs only, using
    # each cell's full-set CI half-width as the noise scale.  The raw tau stays.
    noise_by_cell = {(c["benchmark"], c["subdimension"]): c["ci_halfwidth_full_score10"]
                     for c in ci_results}
    for c in cell_results:
        noise = noise_by_cell.get((c["benchmark"], c["subdimension"]))
        mks = sorted(c["per_model"])
        fv = [c["per_model"][mk]["full"] for mk in mks]
        mv = [c["per_model"][mk]["mini"] for mk in mks]
        tau_m, n_pairs, n_total = kendall_tau_meaningful(fv, mv, noise)
        c["tau_raw"] = c["tau"]
        c["pass_tau_raw"] = c["pass_tau"]
        c["noise_scale_score10"] = noise
        c["tau_meaningful"] = round(tau_m, 4) if tau_m is not None else None
        c["n_separable_pairs"] = n_pairs
        c["n_pairs_total"] = n_total
        c["pass_tau"] = (tau_m is None) or (tau_m >= TAU_THRESHOLD)
        c["tau_status"] = "no_separable_pairs" if tau_m is None else "computed"

    # ---- Criterion 3 at the P level (round-4 fix): same separable-pairs rule as
    # the cell level.  The all-pairs tau was reporting noise -- P04 scored
    # maxDelta 0.000 yet tau 0.714, because three models carry identical imputed
    # values and the tie was being ordered arbitrarily.
    global CURATED_CELLS
    CURATED_CELLS = {(c["benchmark"], c["subdimension"]) for c in ci_results}
    cell_ci_full = {(c["benchmark"], c["subdimension"]): c["ci_halfwidth_full_score10"]
                    for c in ci_results if c["ci_halfwidth_full_score10"] is not None}
    noise_map = p_noise_scales(_fe, cell_ci_full)

    for p in p_results:
        pc = p["p_code"]
        mks = p.pop("_model_keys")
        fv = [r["full"] for r in p["per_model"]]
        mv = [r["mini"] for r in p["per_model"]]
        infos = [noise_map.get((mk, pc), {}) for mk in mks]
        # One scale per P: the largest per-model propagated noise, so a pair is
        # only called separable when it clears the noisier of the two members.
        noise = max([i.get("noise", 0.0) for i in infos], default=0.0)
        tau_m, n_pairs, n_total = kendall_tau_meaningful(fv, mv, noise)
        imp = [i.get("imputed_weight_share", 0.0) for i in infos]
        # Missing-data substitution only ever targets the RELEASE panel
        # (agg.PANEL_MODEL_KEYS), so rankability must be judged on those faces,
        # not diluted by peripheral models that were never imputation targets.
        # P03/P04 look fine at 3/10 overall but are 3/5 of the actual panel.
        panel_shares = {mk: i.get("imputed_weight_share", 0.0)
                        for mk, i in zip(mks, infos) if mk in agg.PANEL_MODEL_KEYS}
        p["panel_models_present"] = len(panel_shares)
        p["panel_imputed_dominated"] = sorted(mk for mk, v in panel_shares.items() if v >= 0.5)
        # Every non-zero share, named -- summary statistics hide this.
        p["imputed_share_by_model"] = {mk: round(i.get("imputed_weight_share", 0.0), 4)
                                       for mk, i in zip(mks, infos)
                                       if i.get("imputed_weight_share", 0.0) > 0}
        # Faces whose P score is dominated by the aggregation's missing-data
        # substitute (the minimum score of the models that WERE measured on that
        # cell).  Several such faces receive byte-identical placeholder scores, so
        # they are mutually unrankable and their absolute score is not a
        # measurement of that model at all.  Must be named, not averaged away.
        p["imputed_dominated_models"] = [mk for mk, i in zip(mks, infos)
                                         if i.get("imputed_weight_share", 0.0) >= 0.5]
        p["noise_scale_score10"] = round(noise, 4)
        p["cells_without_ci"] = sum(i.get("cells_without_ci", 0) for i in infos)
        p["tau_meaningful"] = round(tau_m, 4) if tau_m is not None else None
        p["n_separable_pairs"] = n_pairs
        p["n_pairs_total"] = n_total
        p["pass_tau"] = (tau_m is None) or (tau_m >= TAU_THRESHOLD)
        p["tau_status"] = "no_separable_pairs" if tau_m is None else "computed"
        p["max_imputed_weight_share"] = round(max(imp, default=0.0), 4)
        p["median_imputed_weight_share"] = round(statistics.median(imp) if imp else 0.0, 4)
        p["n_models_majority_imputed"] = sum(1 for x in imp if x >= 0.5)
        p["benchmarks"] = sorted({ev["benchmark_id"] for ev in _fe if ev["p_code"] == pc})

    assign_p_labels(p_results)

    summary = assemble_summary(
        manifest, curated, cell_results, p_results, loo_results, loo_worst,
        ci_results, cell_selfcal, cell_selfcal_maxgap, p_selfcal_maxdiff,
        full_group_rows, mini_group_rows, pub10, untied,
    )
    (OUT_DIR / "validation_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(summary)
    write_html(summary)
    print_console(summary)


def _cell_subset_rows(bid: str, sub: str, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if bid == "olympiadbench" and sub == "multimodal-subset accuracy":
        return [r for r in rows if (r.get("buckets") or {}).get("modality") == "MM"]
    if bid == "k12vista" and sub == "math problem-figure subset score":
        return [r for r in rows if str((r.get("buckets") or {}).get("subject", "")).startswith("math")]
    if bid == "k12vista" and sub == "science/geo subject-chart subset score":
        return [r for r in rows if not str((r.get("buckets") or {}).get("subject", "")).startswith("math")]
    if bid == "pedagogy_benchmark" and sub == "SEND special education needs selection":
        return [r for r in rows if (r.get("buckets") or {}).get("category") == "CDPK_send"]
    if bid == "pedagogy_benchmark" and sub == "CDPK teaching knowledge selection":
        return [r for r in rows if (r.get("buckets") or {}).get("category") != "CDPK_send"]
    return rows


LABELS = {
    "rank_usable": "可用于排名",
    "score_only": "仅可用于绝对分",
    "needs_full": "需跑全量",
    "not_rankable_by_construction": "本就不可排名",
}


def assign_p_labels(p_results: list[dict[str, Any]]) -> None:
    """Tag each P for how a mini-run panel may be read.

    Rules are applied in order and every tag records the numbers behind it.  The
    first tag is a property of the evidence base, NOT of the curation: a P whose
    panel scores are mostly imputed placeholders, or whose only evidence is a
    single cell shared with other Ps, cannot be ranked even on a full run, so
    labelling it is the honest action -- adding items would not help and is
    forbidden anyway.
    """
    for p in p_results:
        pc = p["p_code"]
        reasons: list[str] = []
        label: str | None = None

        # (0) Not rankable regardless of curation.
        imputed = p.get("imputed_dominated_models") or []
        panel_imp = p.get("panel_imputed_dominated") or []
        n_panel = p.get("panel_models_present") or 0
        if n_panel and len(panel_imp) * 2 >= n_panel:
            label = "not_rankable_by_construction"
            reasons.append(
                f"发布面板 {n_panel} 个模型面里有 {len(panel_imp)} 个是缺测替代值（"
                + "、".join(f"`{m}`" for m in panel_imp)
                + "）：替代值统一取该格已测模型的最低分，这些面因此拿到完全相同的分数，"
                "面板过半不可分辨，名次本就不存在——与精选无关，跑全量也一样")
        elif len(p["benchmarks"]) == 1:
            label = "not_rankable_by_construction"
            reasons.append(
                f"证据只来自单一 benchmark（{p['benchmarks'][0]}），无独立来源可交叉验证；"
                "全量同样如此，精选不改变这一点")
        elif p["tau_status"] == "no_separable_pairs":
            label = "not_rankable_by_construction"
            reasons.append(
                f"全量分数在噪声尺度 {p['noise_scale_score10']} 内无任何可分辨的模型对"
                f"（{p['n_pairs_total']} 对全部不可分辨）：全量自己就排不出名次")

        # (1) Score fidelity, then (2) rank fidelity.
        if label is None:
            if not p["pass_delta"] and p["max_abs_delta"] > 1.5 * P_DELTA_THRESHOLD:
                label = "needs_full"
                reasons.append(
                    f"精选与全量的 P 分最大差 {p['max_abs_delta']} 明显超出 {P_DELTA_THRESHOLD} 判据，绝对分不可信")
            elif p["pass_tau"]:
                label = "rank_usable"
                reasons.append(
                    f"绝对分最大差 {p['max_abs_delta']}（判据 {P_DELTA_THRESHOLD}"
                    f"{'，略超但在噪声尺度内' if not p['pass_delta'] else ''}）；"
                    f"{p['n_separable_pairs']}/{p['n_pairs_total']} 个可分辨模型对的名次 τ={p['tau_meaningful']}")
            else:
                label = "score_only"
                reasons.append(
                    f"绝对分最大差 {p['max_abs_delta']} 可接受，但 {p['n_separable_pairs']} 个可分辨模型对中出现翻转"
                    f"（τ={p['tau_meaningful']} < {TAU_THRESHOLD}），名次要谨慎")

        # Mandatory caveat whenever ANY face is a placeholder, whatever the label:
        # those faces must be dropped before reading scores or ranks.
        if imputed and label != "not_rankable_by_construction":
            reasons.append(
                f"**必须排除这 {len(imputed)} 个模型面再读分/排名**（缺测替代值，非真实测量，彼此同分）："
                + "、".join(f"`{m}`" for m in imputed))

        if p["cells_without_ci"]:
            reasons.append(
                f"注意：{p['cells_without_ci']} 个精选格没有 CI 估计（bootstrap 无法计算），"
                "噪声尺度被低估，判据因此偏严")

        p["usability_label"] = label
        p["usability_label_zh"] = LABELS[label]
        p["usability_reasons"] = reasons


def assemble_summary(manifest, curated, cell_results, p_results, loo_results, loo_worst,
                     ci_results, cell_selfcal, cell_selfcal_maxgap, p_selfcal_maxdiff,
                     full_group_rows, mini_group_rows, pub10, untied):
    cell_fail_delta = [c for c in cell_results if not c["pass_delta"]]
    cell_fail_tau = [c for c in cell_results if not c["pass_tau"]]
    cell_fail_tau_raw = [c for c in cell_results if not c.get("pass_tau_raw", True)]
    ci_fail_abs = [c for c in ci_results if not c.get("pass_abs_legacy", False)]
    p_fail_delta = [p for p in p_results if not p["pass_delta"]]
    p_fail_tau = [p for p in p_results if not p["pass_tau"]]
    p_fail_tau_raw = [p for p in p_results if not p.get("pass_tau_raw", True)]
    loo_fail = [l for l in loo_results if not l["pass"]]
    ci_fail = [c for c in ci_results if not c["pass"]]

    total_full = sum(v["full_count"] for v in curated.values())
    total_mini = sum(v["selected_count"] for v in curated.values())

    return {
        "generated_by": "scripts/validate_mini_selection.py",
        "seed": manifest["seed"],
        "acceptance_thresholds": {
            "cell_abs_delta": CELL_DELTA_THRESHOLD, "p_abs_delta": P_DELTA_THRESHOLD,
            "kendall_tau": TAU_THRESHOLD, "loo_relax": LOO_RELAX,
            "ci_accuracy": CI_ACC_THRESHOLD, "ci_stat": CI_STAT_THRESHOLD,
        },
        "self_calibration": {
            "n_records_compared": len([c for c in cell_selfcal if c["gap"] is not None]),
            "n_reconciled": len([c for c in cell_selfcal if c["status"] == "reconciled"]),
            "n_near_reconciled": len([c for c in cell_selfcal if c["status"] == "near_reconciled"]),
            "n_cells_tied": len([c for c in cell_selfcal if c["tied_to_published"]]),
            "cell_recompute_vs_published_maxgap": round(cell_selfcal_maxgap, 4),
            "cell_recompute_tie_ok": cell_selfcal_maxgap <= SELFCAL_TOL,
            "p_score_reuse_vs_published_maxdiff": round(p_selfcal_maxdiff, 4),
            "p_score_reuse_ok": p_selfcal_maxdiff <= 0.01,
            "n_cells_untied": len(untied),
            "untied_cells": [
                {"benchmark": c["benchmark"], "subdimension": c["subdimension"],
                 "model_key": c["model_key"], "face": c["face"],
                 "recompute": c["recompute"], "published": c["published"],
                 "gap": c["gap"], "reason": c["untied_reason"]}
                for c in sorted(untied, key=lambda x: -x["gap"])
            ],
            "note": ("P 分是直接复用聚合脚本的 score_atomic_p 跑在已发布 08 证据上重算的，"
                     "不是复刻实现；逐格分数按实际差值分档，导入面能对上的照样算对上，"
                     "对不上的单列并注明原因。"),
        },
        "totals": {
            "curated_benchmarks": len(curated),
            "full_items": total_full, "mini_items": total_mini,
            "mini_fraction": round(total_mini / total_full, 4) if total_full else None,
        },
        "acceptance_matrix": {
            "cell_delta": {"total": len(cell_results), "pass": len(cell_results) - len(cell_fail_delta),
                           "fail": len(cell_fail_delta)},
            "cell_tau": {"total": len([c for c in cell_results if c.get("tau_meaningful") is not None]),
                         "fail": len(cell_fail_tau),
                         "criterion": "kendall tau over separable model pairs only (revised)"},
            "cell_tau_raw_legacy": {"total": len([c for c in cell_results if c["tau_raw"] is not None]),
                                    "fail": len(cell_fail_tau_raw),
                                    "criterion": "kendall tau over all pairs (superseded, kept for audit)"},
            "p_delta": {"total": len(p_results), "fail": len(p_fail_delta)},
            "p_tau": {"total": len([p for p in p_results if p.get("tau_meaningful") is not None]),
                      "fail": len(p_fail_tau),
                      "criterion": "kendall tau over separable P pairs only (revised)"},
            "p_tau_raw_legacy": {"total": len([p for p in p_results if p.get("tau_raw") is not None]),
                                 "fail": len(p_fail_tau_raw),
                                 "criterion": "kendall tau over all pairs (superseded, kept for audit)"},
            "loo": {"total": len(loo_results), "fail": len(loo_fail)},
            "ci": {"total": len([c for c in ci_results if c["status"] == "computed"]),
                   "fail": len([c for c in ci_fail if c["status"] == "computed"]),
                   "not_computed": len([c for c in ci_results if c["status"] == "not_computed"]),
                   "criterion": f"sampling efficiency = (mini_CI/full_CI)/sqrt(N_full/N_mini) <= {CI_EFFICIENCY_THRESHOLD} (revised)"},
            "ci_abs_legacy": {"total": len(ci_results), "fail": len(ci_fail_abs),
                              "criterion": "absolute CI half-width (superseded: 13 cells needed more items than the benchmark has, so the full set fails it too)"},
        },
        # Cells the user has explicitly accepted (round 2): the residual drift is
        # sampling noise, not bias, so they are annotated rather than topped up.
        # Adding items to make an acceptance metric look better is forbidden.
        "accepted_drift": [
            {"benchmark": c["benchmark"], "subdimension": c["subdimension"],
             "max_abs_delta": c["max_abs_delta"],
             "ci_halfwidth_score10": next((x["ci_halfwidth_score10"] for x in ci_results
                                           if x["benchmark"] == c["benchmark"]
                                           and x["subdimension"] == c["subdimension"]), None),
             "delta_over_ci": (round(c["max_abs_delta"] / hw, 2)
                               if (hw := next((x["ci_halfwidth_score10"] for x in ci_results
                                               if x["benchmark"] == c["benchmark"]
                                               and x["subdimension"] == c["subdimension"]), None))
                               else None),
             "note": "panel entries from this cell must carry a mini_v1 drift annotation"}
            for c in cell_fail_delta
        ],
        "p_usability_labels": [
            {"p_code": p["p_code"], "label": p["usability_label"], "label_zh": p["usability_label_zh"],
             "reasons": p["usability_reasons"], "n_models": p["n_models"],
             "max_abs_delta": p["max_abs_delta"], "tau_meaningful": p.get("tau_meaningful"),
             "tau_raw": p.get("tau_raw"), "n_separable_pairs": p.get("n_separable_pairs"),
             "n_pairs_total": p.get("n_pairs_total"), "noise_scale_score10": p.get("noise_scale_score10"),
             "median_imputed_weight_share": p.get("median_imputed_weight_share"),
             "imputed_dominated_models": p.get("imputed_dominated_models"),
             "panel_models_present": p.get("panel_models_present"),
             "panel_imputed_dominated": p.get("panel_imputed_dominated"),
             "imputed_share_by_model": p.get("imputed_share_by_model"),
             "benchmarks": p.get("benchmarks")}
            for p in sorted(p_results, key=lambda x: x["p_code"])
        ],
        "loo_worst": loo_worst,
        "failures": {
            "cell_delta": cell_fail_delta,
            "cell_tau": [{"benchmark": c["benchmark"], "subdimension": c["subdimension"],
                          "tau": c["tau"], "n_models": c["n_models"]} for c in cell_fail_tau],
            "p_delta": p_fail_delta,
            "p_tau": [{"p_code": p["p_code"], "tau": p["tau"], "n_models": p["n_models"]} for p in p_fail_tau],
            "loo": loo_fail,
            "ci": ci_fail,
        },
        "cell_results": cell_results,
        "p_results": p_results,
        "ci_results": ci_results,
        "cell_self_calibration": cell_selfcal,
        "group_scores": {
            "full": [{"model_key": r["model_key"], "group": r["group"], "score_10": r["score_10"]} for r in full_group_rows],
            "mini": [{"model_key": r["model_key"], "group": r["group"], "score_10": r["score_10"]} for r in mini_group_rows],
        },
    }


def _md_bool(ok: bool) -> str:
    return "通过" if ok else "**未通过**"


def _untied_section(s: dict[str, Any]) -> str:
    untied = s["self_calibration"]["untied_cells"]
    if not untied:
        return "无。所有格都能与已发布产物对上。\n"
    from collections import defaultdict
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for c in untied:
        groups[(c["benchmark"], c["reason"])].append(c)
    sc = s["self_calibration"]
    lines = [
        f"共比对 **{sc['n_records_compared']}** 条（格 × 模型面）：**{sc['n_reconciled']}** 条逐位对上"
        f"（差 ≤ {SELFCAL_TOL}），**{sc['n_near_reconciled']}** 条落在舍入/导入协议噪声内"
        f"（差 ≤ {SELFCAL_NEAR_TOL}），**{len(untied)}** 条对不上。",
        "",
        "对不上的这些格，已发布分数不是本仓库判分器算出来的，逐题重算复现不了它们，属于既有产物的口径问题，",
        "不是本次抽样引入的误差。它们的**精选 vs 全量漂移仍然有效**（两侧都用同一套重算），",
        "只是**绝对分无法与已发布值对账**。",
        "",
        "| benchmark | 格 | 模型面数 | 最大差 | 原因 |",
        "|---|---|---:|---:|---|",
    ]
    for (bid, reason), rows in sorted(groups.items(), key=lambda kv: -max(r["gap"] for r in kv[1])):
        subs = sorted({r["subdimension"] for r in rows})
        mx = max(r["gap"] for r in rows)
        lines.append(f"| `{bid}` | {', '.join(sub[:34] for sub in subs)} | {len(rows)} | {mx:.4f} | {reason} |")
    lines.append("")
    lines.append("证据：sas_bench 唯一一个由本仓库原生跑出来的模型面（`glm-5.2`）三个格全部**逐位对上（差 0.0000）**；")
    lines.append("导入面的 QWK 也只差 0.003–0.04（QWK 只依赖导入时忠实保留的总分标签）。")
    lines.append("差异集中在 CCS/ECS，这两个指标依赖导入过程未能等价保留的步骤级错因标注，")
    lines.append("因此是系统性偏移（CCS +0.55~0.67、ECS +1.39~2.28），不是随机噪声，也不是重算 bug。")
    lines.append("")
    return "\n".join(lines)


def write_markdown(s: dict[str, Any]) -> None:
    am = s["acceptance_matrix"]
    lines = [
        "# 精选题集 mini_v1 离线验证报告",
        "",
        f"随机种子 `{s['seed']}`；本报告全程零 API 调用，只读取 `reports/eval/` 的全量逐题结果。",
        "",
        "## 一、自校准（重算逻辑是否可信）",
        "",
        "先用全量题目重算每个消费格与每个 P 分，与已发布的 `09/10` 产物对账，对得上才说明重算逻辑正确。",
        "",
        f"- 逐格全量重算 vs 已发布 `08` 的最大差：**{s['self_calibration']['cell_recompute_vs_published_maxgap']}**"
        f"（{'对上' if s['self_calibration']['cell_recompute_tie_ok'] else '未对上'}，阈值 0.01）。",
        f"- 复用聚合脚本 `score_atomic_p` 重算 P 分 vs 已发布 `09` 的最大差：**{s['self_calibration']['p_score_reuse_vs_published_maxdiff']}**"
        f"（{'对上' if s['self_calibration']['p_score_reuse_ok'] else '未对上'}）。",
        f"- 已对账的格×模型面共 **{s['self_calibration']['n_cells_tied']}** 个。",
        f"- 说明：{s['self_calibration']['note']}",
        "",
        "### 无法对账的格（单列，不混进通过项）",
        "",
        _untied_section(s),
        "## 二、总量",
        "",
        f"精选合计 **{s['totals']['mini_items']}** 题 / 全量 **{s['totals']['full_items']}** 题 = "
        f"**{s['totals']['mini_fraction']:.1%}**（这 {s['totals']['curated_benchmarks']} 个可精选 benchmark）。",
        "",
        "## 三、验收五项结果矩阵",
        "",
        "标准 1/2/4 不变；标准 3 与 5 本轮改为相对判据（依据见下），**原始绝对值一并保留**，",
        "两套判据并列呈现，避免改标准把矩阵改好看。",
        "",
        "| 项 | 判据 | 总数 | 未通过 |",
        "|---|---|---:|---:|",
        f"| 1 逐格绝对分漂移 | \\|Δ\\|≤{CELL_DELTA_THRESHOLD} | {am['cell_delta']['total']} | {am['cell_delta']['fail']} |",
        f"| 2 逐 P 绝对分漂移 | \\|Δ\\|≤{P_DELTA_THRESHOLD} | {am['p_delta']['total']} | {am['p_delta']['fail']} |",
        f"| 3a 逐格排名 τ（**新**：只算可区分的模型对） | τ≥{TAU_THRESHOLD} | {am['cell_tau']['total']} | {am['cell_tau']['fail']} |",
        f"| 3a' 逐格排名 τ（旧：全部模型对，留档） | τ≥{TAU_THRESHOLD} | {am['cell_tau_raw_legacy']['total']} | {am['cell_tau_raw_legacy']['fail']} |",
        f"| 3b 逐 P 排名 τ（**新**：只算可区分的模型对） | τ≥{TAU_THRESHOLD} | {am['p_tau']['total']} | {am['p_tau']['fail']} |",
        f"| 3b' 逐 P 排名 τ（旧：全部模型对，留档） | τ≥{TAU_THRESHOLD} | {am['p_tau_raw_legacy']['total']} | {am['p_tau_raw_legacy']['fail']} |",
        f"| 4 留一法漂移 | \\|Δ\\|≤{LOO_RELAX} | {am['loo']['total']} | {am['loo']['fail']} |",
        f"| 5 抽样效率（**新**：实测CI膨胀/理论膨胀） | ≤{CI_EFFICIENCY_THRESHOLD} | {am['ci']['total']} | {am['ci']['fail']} |",
        f"| 5' bootstrap CI 绝对半宽（旧，留档） | acc≤{CI_ACC_THRESHOLD} / stat≤{CI_STAT_THRESHOLD} | {am['ci_abs_legacy']['total']} | {am['ci_abs_legacy']['fail']} |",
        "",
        "**标准 3 为什么改**：旧判据在 n=9 时一次相邻换位就掉到 0.889，实际等于要求零换位；",
        "而且会把分数统计上无法区分的模型换位也判为失败。新判据只统计**全量分差超过该格 CI 半宽**的模型对，",
        "分差在噪声内的换位不计。",
        "",
        "**标准 5 为什么改**：旧的绝对门槛已证实错配 —— 13 个格所需样本量超过 benchmark 全量本身",
        "（longtutor_evidence 幻觉检查需 6,051 题、该格全量只有 1,001），即**跑全量也过不了**，",
        "它衡量的是 benchmark 自身精度而非精选保真度。新判据同时 bootstrap 全量与精选，比较",
        "`实测比值 / 理论比值`，理论值 `sqrt(N_full/N_mini)` 是纯随机抽样必然产生的膨胀；",
        f"接近 1.0 表示分层抽样与随机抽样一样有效，明显大于 1 才是真问题（阈值 {CI_EFFICIENCY_THRESHOLD}）。",
        "全量与自身比恒等于 1.0，逻辑自洽。",
        "",
        f"留一法最差漂移：benchmark `{s['loo_worst']['benchmark']}` · 格 `{s['loo_worst']['subdimension']}` · "
        f"留出模型 `{s['loo_worst']['model_key']}` · Δ={s['loo_worst']['delta']}。",
        "",
    ]
    # failing lists
    fails = s["failures"]
    if any(fails[k] for k in fails):
        lines.append("## 四、未通过明细")
        lines.append("")
        for label, key, fmt in [
            ("逐格 |Δ|>阈", "cell_delta", lambda c: f"`{c['benchmark']}` · {c['subdimension']} · maxΔ={c['max_abs_delta']}"),
            ("逐格 τ<0.9", "cell_tau", lambda c: f"`{c['benchmark']}` · {c['subdimension']} · τ={c['tau']} (n={c['n_models']})"),
            ("逐 P |Δ|>阈", "p_delta", lambda c: f"`{c['p_code']}` · maxΔ={c['max_abs_delta']}"),
            ("逐 P τ<0.9", "p_tau", lambda c: f"`{c['p_code']}` · τ={c['tau']} (n={c['n_models']})"),
            ("留一法", "loo", lambda c: f"`{c['benchmark']}` · {c['subdimension']} · 留出 {c['held_out_model']} · Δ={c['delta']}"),
            ("bootstrap CI 抽样效率", "ci", lambda c: (
                f"`{c['benchmark']}` · {c['subdimension']} · 效率={c['sampling_efficiency']} "
                f"(阈 {c['efficiency_threshold']};精选半宽 {c['ci_halfwidth_score10']} / 全量半宽 "
                f"{c['ci_halfwidth_full_score10']} = {c['ci_ratio_mini_over_full']}，理论 {c['ci_ratio_theoretical']})")),
        ]:
            if fails[key]:
                lines.append(f"### {label}（{len(fails[key])}）")
                lines.append("")
                for c in fails[key][:40]:
                    lines.append(f"- {fmt(c)}")
                lines.append("")
    else:
        lines.append("## 四、未通过明细")
        lines.append("")
        lines.append("五项全部通过，无未通过格/ P。")
        lines.append("")

    # ---- per-P usability labels (round 4)
    labels = s.get("p_usability_labels") or []
    lines.append("## 五、逐 P 可用性标签（读 mini 面板前先看这张表）")
    lines.append("")
    lines.append("这张表回答的是「这个 P 的 mini 分数能怎么用」。**发现某个 P 表现不好时，正确动作是给它贴准确的标签，")
    lines.append("不是给它加题** —— 照着当前 5–12 个模型的分数去补题，就是在拟合这批模型，正是留一法要防的毛病。")
    lines.append("")
    lines.append("| 标签 | 含义 |")
    lines.append("|---|---|")
    lines.append("| 可用于排名 | 绝对分与名次都保真，可直接读 |")
    lines.append("| 仅可用于绝对分 | 分数可信，但可分辨的模型对里有翻转，名次要谨慎 |")
    lines.append("| 需跑全量 | 精选的绝对分就不可信，结论必须回全量 |")
    lines.append("| 本就不可排名 | 全量也排不出（替代值主导 / 证据同源单源），与精选无关 |")
    lines.append("")
    order = {"rank_usable": 0, "score_only": 1, "needs_full": 2, "not_rankable_by_construction": 3}
    lines.append("| P | 标签 | 模型数 | 面板面 | 面板中替代值面 | maxΔ | τ新 | 可分辨对 | τ旧 | 噪声尺度 | 依据 |")
    lines.append("|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|")
    for L in sorted(labels, key=lambda x: (order.get(x["label"], 9), x["p_code"])):
        lines.append(
            f"| `{L['p_code']}` | **{L['label_zh']}** | {L['n_models']} | {L.get('panel_models_present')} | {len(L.get('panel_imputed_dominated') or [])} | "
            f"{L['max_abs_delta']} | "
            f"{L['tau_meaningful'] if L['tau_meaningful'] is not None else '—'} | "
            f"{L['n_separable_pairs']}/{L['n_pairs_total']} | "
            f"{L['tau_raw'] if L['tau_raw'] is not None else '—'} | {L['noise_scale_score10']} | "
            f"{'；'.join(L['reasons'])} |")
    lines.append("")
    # ---- explicit imputed-share listing (never hide this behind a summary stat)
    lines.append("### 替代值（imputed）占比：逐 P 逐模型列出")
    lines.append("")
    lines.append("聚合对发布面板缺测的格会用「该格已测模型的最低分」顶上并标 imputed。**这不是对该模型的测量**，")
    lines.append("而且多个模型会因此拿到完全相同的分数。汇总统计（如中位数）会把这件事盖掉——3/10 个面是替代值时中位数仍是 0%——")
    lines.append("所以这里逐个列出，凡占比 >0 的都点名。读 mini 面板（以及读全量面板）前，这些面必须先排除。")
    lines.append("")
    rows_imp = []
    for L in sorted(labels, key=lambda x: x["p_code"]):
        shares = L.get("imputed_share_by_model") or {}
        for mk, v in sorted(shares.items(), key=lambda kv: -kv[1]):
            panel = "是" if mk in (L.get("panel_imputed_dominated") or []) or v >= 0.5 else ""
            rows_imp.append((L["p_code"], mk, v, panel))
    if rows_imp:
        lines.append("| P | 模型面 | 替代值权重占比 | 该面是否已被替代值主导(≥50%) |")
        lines.append("|---|---|---:|---|")
        for pc, mk, v, panel in rows_imp:
            lines.append(f"| `{pc}` | `{mk}` | {v:.0%} | {panel} |")
    else:
        lines.append("（本轮无替代值）")
    lines.append("")
    lines.append("**P 级噪声尺度怎么来的**：把每个格的 bootstrap CI 半宽按聚合公式")
    lines.append("`P = facet 等权平均( facet 内 有效权重加权平均 )` 做一阶误差传播，")
    lines.append("`噪声 = sqrt( Σ (系数 × 格CI)^2 )`。精选不触碰的格（全量原样）贡献 0，因为它们在精选与全量之间逐字节相同，")
    lines.append("不可能产生漂移。共享题面的格之间是正相关，独立假设会**低估**噪声，也就是让判据**更严**而非更松。")
    lines.append("")

    # ---- accepted drift (user decision, round 2)
    acc = s.get("accepted_drift") or []
    lines.append("## 六、已接受的漂移（用户裁决：不加题，带注记进面板）")
    lines.append("")
    if not acc:
        lines.append("无。")
    else:
        lines.append("这些格 |Δ| 超过 0.3，但残差在噪声量级内（maxΔ / CI 半宽约 0.4–1.1），")
        lines.append("即漂移来自抽样方差而非系统偏差。用户已裁决**不加题**（加题会推高总占比，")
        lines.append("且为了让指标好看而加题是被明确禁止的）。这些格将来进面板时必须带 mini_v1 漂移注记。")
        lines.append("")
        lines.append("| benchmark | 格 | maxΔ | CI半宽 | Δ/CI |")
        lines.append("|---|---|---:|---:|---:|")
        for c in sorted(acc, key=lambda x: -x["max_abs_delta"]):
            lines.append(f"| `{c['benchmark']}` | {c['subdimension'][:44]} | {c['max_abs_delta']} | "
                         f"{c['ci_halfwidth_score10'] if c['ci_halfwidth_score10'] is not None else '—'} | "
                         f"{c['delta_over_ci'] if c['delta_over_ci'] is not None else '—'} |")
    lines.append("")

    lines.append("## 七、逐格漂移与排名（新旧判据并列）")
    lines.append("")
    lines.append("| benchmark | 格 | 模型数 | maxΔ | τ新(可区分对) | 可区分对数 | τ旧(全部对) | CI半宽精选 | CI半宽全量 | 抽样效率 |")
    lines.append("|---|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    ci_by = {(c["benchmark"], c["subdimension"]): c for c in s["ci_results"]}
    for c in sorted(s["cell_results"], key=lambda x: -x["max_abs_delta"]):
        ci = ci_by.get((c["benchmark"], c["subdimension"]), {})
        def g(k):
            v = ci.get(k)
            return v if v is not None else "—"
        tm = c.get("tau_meaningful")
        tr = c.get("tau_raw")
        lines.append(
            f"| `{c['benchmark']}` | {c['subdimension'][:40]} | {c['n_models']} | {c['max_abs_delta']} | "
            f"{tm if tm is not None else '—'} | {c.get('n_separable_pairs', '—')}/{c.get('n_pairs_total', '—')} | "
            f"{tr if tr is not None else '—'} | {g('ci_halfwidth_score10')} | {g('ci_halfwidth_full_score10')} | "
            f"{g('sampling_efficiency')} |")
    lines.append("")
    (OUT_DIR / "validation_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_html(s: dict[str, Any]) -> None:
    am = s["acceptance_matrix"]

    def esc(x):
        return html.escape(str(x))

    ci_by = {(c["benchmark"], c["subdimension"]): c for c in s["ci_results"]}

    def _g(c, k):
        v = ci_by.get((c["benchmark"], c["subdimension"]), {}).get(k)
        return v if v is not None else "—"

    rows_cells = "".join(
        f"<tr><td>{esc(c['benchmark'])}</td><td>{esc(c['subdimension'])}</td><td>{c['n_models']}</td>"
        f"<td class='{'bad' if not c['pass_delta'] else 'ok'}'>{c['max_abs_delta']}</td>"
        f"<td class='{'bad' if not c['pass_tau'] else 'ok'}'>"
        f"{c.get('tau_meaningful') if c.get('tau_meaningful') is not None else '—'}</td>"
        f"<td>{c.get('n_separable_pairs','—')}/{c.get('n_pairs_total','—')}</td>"
        f"<td class='muted'>{c.get('tau_raw') if c.get('tau_raw') is not None else '—'}</td>"
        f"<td>{_g(c,'ci_halfwidth_score10')}</td><td>{_g(c,'ci_halfwidth_full_score10')}</td>"
        f"<td>{_g(c,'sampling_efficiency')}</td></tr>"
        for c in sorted(s["cell_results"], key=lambda x: -x["max_abs_delta"])
    )
    acc = s.get("accepted_drift") or []
    rows_acc = "".join(
        f"<tr><td>{esc(a['benchmark'])}</td><td>{esc(a['subdimension'])}</td>"
        f"<td>{a['max_abs_delta']}</td>"
        f"<td>{a['ci_halfwidth_score10'] if a['ci_halfwidth_score10'] is not None else '—'}</td>"
        f"<td>{a['delta_over_ci'] if a['delta_over_ci'] is not None else '—'}</td></tr>"
        for a in sorted(acc, key=lambda x: -x["max_abs_delta"])
    ) or "<tr><td colspan=5>无</td></tr>"
    rows_p = "".join(
        f"<tr><td>{esc(p['p_code'])}</td><td>{p['n_models']}</td>"
        f"<td class='{'bad' if not p['pass_delta'] else 'ok'}'>{p['max_abs_delta']}</td>"
        f"<td class='{'bad' if not p['pass_tau'] else 'ok'}'>{p['tau'] if p['tau'] is not None else '—'}</td></tr>"
        for p in sorted(s["p_results"], key=lambda x: x["p_code"])
    )
    sc = s["self_calibration"]
    tot = s["totals"]
    doc = f"""<!DOCTYPE html><html lang=zh><head><meta charset=utf-8>
<title>mini_v1 离线验证</title><style>
body{{font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;margin:2rem auto;max-width:1080px;padding:0 1rem;color:#1a1a1a;line-height:1.5}}
h1{{font-size:1.5rem}} h2{{font-size:1.15rem;margin-top:2rem;border-bottom:1px solid #ddd;padding-bottom:.3rem}}
table{{border-collapse:collapse;width:100%;font-size:.86rem;margin:.6rem 0}}
th,td{{border:1px solid #ddd;padding:.3rem .5rem;text-align:left}} th{{background:#f5f5f5}}
td.ok{{color:#137333}} .muted{{color:#70757a}} .note{{font-size:.85rem;color:#5f6368;background:#f8f9fa;padding:.6rem .8rem;border-left:3px solid #dadce0}} td.bad{{background:#fce8e6;color:#c5221f;font-weight:600}}
.metric{{display:inline-block;background:#f1f3f4;border-radius:6px;padding:.5rem .8rem;margin:.3rem .4rem .3rem 0}}
.metric b{{font-size:1.2rem;display:block}} .good{{color:#137333}} .warn{{color:#c5221f}}
</style></head><body>
<h1>精选题集 mini_v1 离线验证报告</h1>
<p>随机种子 <code>{s['seed']}</code>。全程零 API 调用，只读 <code>reports/eval/</code> 全量逐题结果。</p>
<div>
<span class=metric>精选/全量<b>{tot['mini_items']}/{tot['full_items']}</b>{tot['mini_fraction']:.1%}</span>
<span class=metric>自校准·逐格最大差<b class="{'good' if sc['cell_recompute_tie_ok'] else 'warn'}">{sc['cell_recompute_vs_published_maxgap']}</b>阈 0.01</span>
<span class=metric>自校准·P分最大差<b class="{'good' if sc['p_score_reuse_ok'] else 'warn'}">{sc['p_score_reuse_vs_published_maxdiff']}</b>阈 0.01</span>
</div>
<h2>验收五项矩阵</h2>
<table><tr><th>项</th><th>判据</th><th>总数</th><th>未通过</th></tr>
<tr><td>1 逐格 |Δ|</td><td>≤{CELL_DELTA_THRESHOLD}</td><td>{am['cell_delta']['total']}</td><td class="{'bad' if am['cell_delta']['fail'] else 'ok'}">{am['cell_delta']['fail']}</td></tr>
<tr><td>2 逐 P |Δ|</td><td>≤{P_DELTA_THRESHOLD}</td><td>{am['p_delta']['total']}</td><td class="{'bad' if am['p_delta']['fail'] else 'ok'}">{am['p_delta']['fail']}</td></tr>
<tr><td>3a 逐格 τ <b>新</b>(只算可区分的模型对)</td><td>≥{TAU_THRESHOLD}</td><td>{am['cell_tau']['total']}</td><td class="{'bad' if am['cell_tau']['fail'] else 'ok'}">{am['cell_tau']['fail']}</td></tr>
<tr class=muted><td>3a' 逐格 τ 旧(全部模型对，留档)</td><td>≥{TAU_THRESHOLD}</td><td>{am['cell_tau_raw_legacy']['total']}</td><td>{am['cell_tau_raw_legacy']['fail']}</td></tr>
<tr><td>3b 逐 P τ</td><td>≥{TAU_THRESHOLD}</td><td>{am['p_tau']['total']}</td><td class="{'bad' if am['p_tau']['fail'] else 'ok'}">{am['p_tau']['fail']}</td></tr>
<tr><td>4 留一法</td><td>≤{LOO_RELAX}</td><td>{am['loo']['total']}</td><td class="{'bad' if am['loo']['fail'] else 'ok'}">{am['loo']['fail']}</td></tr>
<tr><td>5 抽样效率 <b>新</b> (实测CI膨胀/理论膨胀)</td><td>≤{CI_EFFICIENCY_THRESHOLD}</td><td>{am['ci']['total']}</td><td class="{'bad' if am['ci']['fail'] else 'ok'}">{am['ci']['fail']}</td></tr>
<tr class=muted><td>5' bootstrap CI 绝对半宽 旧(留档)</td><td>acc≤{CI_ACC_THRESHOLD}/stat≤{CI_STAT_THRESHOLD}</td><td>{am['ci_abs_legacy']['total']}</td><td>{am['ci_abs_legacy']['fail']}</td></tr>
</table>
<p class=note>标准 3/5 本轮改为相对判据：旧 τ 在 n=9 时一次相邻换位即掉到 0.889（等于要求零换位），且会把统计上无法区分的模型换位判为失败；
旧 CI 绝对门槛有 13 个格所需样本量超过 benchmark 全量本身，跑全量也过不了。原始绝对值全部保留在上表与下表中。</p>
<h2>已接受的漂移（用户裁决：不加题，带注记进面板）</h2>
<table><tr><th>benchmark</th><th>格</th><th>maxΔ</th><th>CI半宽</th><th>Δ/CI</th></tr>{rows_acc}</table>
<p>留一法最差漂移：<code>{esc(s['loo_worst']['benchmark'])}</code> · {esc(s['loo_worst']['subdimension'])} · 留出 <code>{esc(s['loo_worst']['model_key'])}</code> · Δ={s['loo_worst']['delta']}。</p>
<h2>逐 P 漂移与排名一致性</h2>
<table><tr><th>P</th><th>模型数</th><th>maxΔ</th><th>τ</th></tr>{rows_p}</table>
<h2>逐格漂移与排名一致性（按 maxΔ 降序，新旧判据并列）</h2>
<table><tr><th>benchmark</th><th>格</th><th>模型数</th><th>maxΔ</th><th>τ新</th><th>可区分对</th><th>τ旧</th><th>CI半宽<br>精选</th><th>CI半宽<br>全量</th><th>抽样效率</th></tr>{rows_cells}</table>
</body></html>"""
    (OUT_DIR / "validation_report.html").write_text(doc, encoding="utf-8")


def print_console(s: dict[str, Any]) -> None:
    am = s["acceptance_matrix"]
    sc = s["self_calibration"]
    print("=== mini_v1 validation ===")
    print(f"self-cal cell maxgap={sc['cell_recompute_vs_published_maxgap']} (ok={sc['cell_recompute_tie_ok']}) "
          f"P maxdiff={sc['p_score_reuse_vs_published_maxdiff']} (ok={sc['p_score_reuse_ok']})")
    print(f"mini fraction: {s['totals']['mini_items']}/{s['totals']['full_items']} = {s['totals']['mini_fraction']:.1%}")
    for k in ("cell_delta", "p_delta", "cell_tau", "p_tau", "loo", "ci"):
        print(f"  {k:10s}: total={am[k].get('total')} fail={am[k].get('fail')}")
    print(f"loo worst: {s['loo_worst']}")


if __name__ == "__main__":
    main()
