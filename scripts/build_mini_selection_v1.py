#!/usr/bin/env python3
"""Build the mini_v1 curated item selection (offline, idempotent, fixed seed).

Reads the full per-item ``reports/eval/<benchmark>/<model>/scored.jsonl`` panels
(read-only), estimates per-item difficulty (cross-model mean score) and
discrimination (cross-model disagreement), then draws a stratified sample per
benchmark.  Strata = the aggregation-consumed content bucket x difficulty
quintile; sampling is proportional-random with discrimination as a gentle
within-stratum priority (never a hard filter).

Outputs (nothing outside ``data/mini_selection_v1/`` is touched):
- ``data/mini_selection_v1/<benchmark>_items_v1.txt`` -- one native item_id per
  line, compatible with ``eval_benchmark.py --item-list``.
- ``data/mini_selection_v1/selection_manifest.json`` -- seed, per-benchmark tier
  and rate, per-stratum quotas, per-cell item counts, and the model faces that
  participated in the difficulty estimate.

Design reference: ``doc/mini_selection_plan_2026-07-19.md`` (sections 3-4 and the
per-benchmark hard constraints).  This script performs ZERO API calls.

Run: ``python3 scripts/build_mini_selection_v1.py``
"""

from __future__ import annotations

import hashlib
import json
import math
import statistics
import sys
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

# canonical_model is stdlib-only inside the aggregation module; reuse it so the
# panel-face dedupe and the panel model keys match the aggregation exactly.
from build_atomic_ability_rebenchmark_artifacts import canonical_model  # noqa: E402

EVAL_DIR = ROOT / "reports" / "eval"
OUT_DIR = ROOT / "data" / "mini_selection_v1"

SEED = 20260719
N_DIFF_BINS = 5
# Content groups smaller than this are pooled into a single "other" group before
# allocation.  Without pooling, a long tail of tiny levels (mathtutorbench topics:
# ~95 levels, most with 1-7 items) soaks up quota and crushes the dominant level's
# share -- the -42pp distortion measured in round 1.
RARE_GROUP_MIN = 20
# Split a content group by difficulty only when it can carry the bins.
DIFF_SPLIT_MIN = 25
# Every mini list must clear the aggregation's global exclusion guard
# (inventory_eval_runs drops any run with scored/total < 100); keep margin.
MIN_TOTAL_ITEMS = 150
# A benchmark needs at least this many distinct model faces before the
# difficulty/discrimination signal is trusted; below it we degrade to pure
# content stratification (plan section 3: k12vista/mathvista/mmtutorbench).
MIN_FACES_FOR_DIFFICULTY = 3


def sha_rng_seed(*parts: str) -> int:
    h = hashlib.sha256(("|".join([str(SEED), *parts])).encode("utf-8")).hexdigest()
    return int(h[:16], 16)


def read_scored(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


# --------------------------------------------------------------------------- #
# Per-item signal + content-stratum extractors.
#
# ``signal`` returns a per-item numeric score (higher = the model did better) or
# None when the item was not scored for that face.  It drives both difficulty
# (cross-face mean) and discrimination (cross-face variance).  ``strata`` returns
# the categorical content bucket for the item (a tuple); difficulty binning is
# layered on top.  Both read only fields already present in scored.jsonl.
# --------------------------------------------------------------------------- #


def _b(item: dict[str, Any], key: str, default: str = "?") -> str:
    return str((item.get("buckets") or {}).get(key, default))


def sig_correct(item: dict[str, Any]) -> float | None:
    if item.get("score_status") != "scored":
        return None
    c = item.get("correct")
    if isinstance(c, bool):
        return 1.0 if c else 0.0
    return None


def sig_rfs(item: dict[str, Any]) -> float | None:
    if item.get("score_status") != "scored":
        return None
    v = item.get("rfs")
    return float(v) if isinstance(v, (int, float)) else None


def sig_adversarial(item: dict[str, Any]) -> float | None:
    if item.get("score_status") != "scored":
        return None
    lab = item.get("final_label")
    if lab is None:
        return None
    return 1.0 if lab != "attack_success" else 0.0


def sig_win(item: dict[str, Any]) -> float | None:
    if item.get("score_status") != "scored":
        return None
    v = item.get("win_score")
    return float(v) if isinstance(v, (int, float)) else None


def sig_bleu(item: dict[str, Any]) -> float | None:
    if item.get("score_status") != "scored":
        return None
    v = item.get("bleu")
    return float(v) if isinstance(v, (int, float)) else None


def sig_k12(item: dict[str, Any]) -> float | None:
    if item.get("score_status") != "scored":
        return None
    sc, n = item.get("item_score"), item.get("n_blanks")
    if isinstance(sc, (int, float)) and isinstance(n, (int, float)) and n:
        return float(sc) / float(n)
    return None


def sig_mmtutor(item: dict[str, Any]) -> float | None:
    if item.get("score_status") != "scored":
        return None
    v = item.get("total_score")
    return float(v) / 6.0 if isinstance(v, (int, float)) else None


def sig_edubench(item: dict[str, Any]) -> float | None:
    if item.get("score_status") != "scored":
        return None
    v = item.get("score")
    return float(v) / 10.0 if isinstance(v, (int, float)) else None


def sig_teaching(item: dict[str, Any]) -> float | None:
    if item.get("score_status") != "scored":
        return None
    parsed = _parse_teaching(item)
    if parsed is None:
        return None
    return (parsed - 1.0) / 4.0


def sig_asap(item: dict[str, Any]) -> float | None:
    if item.get("score_status") != "scored":
        return None
    pred, gold = item.get("normalized"), item.get("gold")
    if isinstance(pred, int) and isinstance(gold, int):
        # Closeness to the human score (0..1); higher = easier for the rater.
        return 1.0 - min(1.0, abs(pred - gold) / 5.0)
    return None


def _parse_teaching(item: dict[str, Any]) -> float | None:
    raw = item.get("extracted")
    if not isinstance(raw, str):
        return None
    txt = raw.strip()
    if txt.startswith("```"):
        txt = txt.strip("`")
        if txt.lstrip().startswith("json"):
            txt = txt.lstrip()[4:]
    try:
        obj = json.loads(txt)
    except Exception:
        return None
    sa, hu = obj.get("strategy_alignment"), obj.get("history_utilization")
    if isinstance(sa, (int, float)) and isinstance(hu, (int, float)):
        return (float(sa) + float(hu)) / 2.0
    return None


# --------------------------------------------------------------------------- #
# Benchmark registry.  ``panel_subdir`` overrides the default face location.
# ``full_set`` C-tier benchmarks carry no item list (MINI mode runs them whole)
# but are recorded in the manifest.
# --------------------------------------------------------------------------- #


class Bench:
    """One curated benchmark.

    ``axes`` names each component of the tuple ``strata`` returns and classifies
    it, which decides how the allocator treats it:

    - ``proportional``: the consumed metric is a pooled mean over items, so its
      value moves when the composition moves.  These axes are reproduced at
      population share by largest-remainder allocation and get NO minimum floor
      -- a floor here silently rewrites the metric (this is what broke
      longtutor_diagnosis's macro-F1 and mathtutorbench_scaffolding's win-rate).
    - ``coverage``: the metric is computed *within* each level and then macro-
      averaged (or reported per level), so across-level composition does not
      enter the score, but each level needs enough items to be stable.  Only
      these may carry a floor, and it is kept small.
    """

    def __init__(
        self,
        bid: str,
        tier: str,
        rate: float,
        signal: Callable[[dict[str, Any]], float | None] | None,
        strata: Callable[[dict[str, Any]], tuple] | None,
        cells: list[str],
        axes: tuple[tuple[str, str], ...] = (),
        panel_subdir: str | None = None,
        coverage_floor: dict[str, int] | None = None,
    ) -> None:
        self.bid = bid
        self.tier = tier
        self.rate = rate
        self.signal = signal
        self.strata = strata
        self.cells = cells
        self.axes = axes
        self.panel_subdir = panel_subdir
        # axis_name -> minimum items per level of that axis (coverage axes only).
        self.coverage_floor = coverage_floor or {}

    def panel_base(self) -> Path:
        base = EVAL_DIR / self.bid
        if self.panel_subdir:
            base = base / self.panel_subdir
        return base


# Content-stratum extractors (plan section 3 hard constraints).
def st_mmlu(i):
    return (_b(i, "category"),)


def st_agieval(i):
    return (_b(i, "task"), _b(i, "question_type"))


def st_ceval(i):
    return (_b(i, "category"),)


def st_olympiad(i):
    return (_b(i, "modality"), _b(i, "subject"), _b(i, "language"))


def st_mathvista(i):
    return (_b(i, "task"), _b(i, "answer_type"))


def st_ifeval(i):
    return (str(i.get("n_instructions", "?")),)


def st_pedagogy(i):
    return (_b(i, "category"),)


def st_asap(i):
    prompt = _b(i, "prompt")
    gold = i.get("gold")
    band = str(gold) if isinstance(gold, int) else "na"
    src = _b(i, "source_used", "none")
    return (prompt, src, band)


def st_sas(i):
    return (_b(i, "subject"), _b(i, "question_type"))


def st_sata(i):
    return (_b(i, "language"), _b(i, "scenario"))


def st_adversarial(i):
    return (_b(i, "category"),)


def st_judge(i):
    # dimension x gold label -- keep macro-F1's class balance (plan section 3).
    return (str(i.get("dimension", _b(i, "dimension"))), str(i.get("gold_label", "?")))


def st_lt_evidence(i):
    return (_b(i, "memory_type"),)


def st_lt_diagnosis(i):
    return (_b(i, "diagnosis"),)


def st_lt_teaching(i):
    return (_b(i, "diagnosis"),)


def st_mtb_topic(i):
    return (_b(i, "topic", "all"),)


def st_mtb_error(i):
    return (_b(i, "is_error", "all"),)


def st_none(i):
    return ("all",)


def st_k12(i):
    subj = _b(i, "subject")
    group = "math" if subj.startswith("math") else "science"
    return (group, _b(i, "grade"), _b(i, "type"))


def st_mmtutor(i):
    return (_b(i, "domain"), _b(i, "category"))


def st_edubench(i):
    return (_b(i, "task"),)


P = "proportional"
C = "coverage"

BENCHES: list[Bench] = [
    # ---- Tier A (hard cut, ~12%) ----
    Bench("mmlu_pro", "A", 0.12, sig_correct, st_mmlu, ["overall/category accuracy"],
          axes=(("category", P),)),
    Bench("agieval", "A", 0.12, sig_correct, st_agieval, ["overall/task/language/question_type accuracy"],
          axes=(("task", P), ("question_type", P))),
    Bench("olympiadbench", "A", 0.12, sig_correct, st_olympiad,
          ["overall/subject/language/modality accuracy", "multimodal-subset accuracy"],
          # modality also carves out the P03 multimodal cell, but the overall cell
          # pools it, so it must stay at population share.
          axes=(("modality", P), ("subject", P), ("language", P))),
    Bench("asap_2", "A", 0.12, sig_asap, st_asap, ["essay holistic QWK"],
          # QWK is also reported per prompt, so prompt carries a coverage floor;
          # the human-score band drives QWK directly and must stay proportional.
          axes=(("prompt", C), ("source_used", P), ("gold_band", P)),
          coverage_floor={"prompt": 150}),
    Bench("sas_bench", "A", 0.12, sig_correct, st_sas,
          ["QWK holistic total score", "CCS step scoring consistency", "ECS error-cause consistency"],
          # All three statistics are computed per subtask then macro-averaged, so
          # subject/question_type (= the subtask) is a coverage axis.
          axes=(("subject", C), ("question_type", C))),
    Bench("eduguard_sata", "A", 0.12, sig_rfs, st_sata, ["Teaching Harm / SATA RFS"],
          axes=(("language", P), ("scenario", P))),
    Bench("bea2025_judge", "A", 0.12, sig_correct, st_judge,
          ["judge labels: mistake/guidance/actionability"],
          # macro-F1 is averaged over dimensions (coverage) but is computed across
          # the gold label classes, so gold_label must keep population share.
          axes=(("dimension", C), ("gold_label", P))),
    Bench("mrbench_judge", "A", 0.12, sig_correct, st_judge,
          ["8-dimension tutor response judging"],
          axes=(("dimension", C), ("gold_label", P))),
    Bench("edubench", "A", 0.12, sig_edubench, st_edubench,
          ["<edubench-metric-cells>"], axes=(("task", P),), panel_subdir="_judge-deepseek-v3.2"),
    Bench("longtutor_evidence", "A", 0.12, sig_correct, st_lt_evidence,
          ["Information Extraction accuracy", "Multi-session Reasoning accuracy", "Hallucination Check accuracy"],
          # Each memory_type is its own consumed cell (accuracy within the level),
          # so composition across levels does not enter any score.
          axes=(("memory_type", C),)),
    Bench("longtutor_diagnosis", "A", 0.12, sig_correct, st_lt_diagnosis,
          ["four-category knowledge-state diagnosis macro-F1"],
          # The headline IS macro-F1 over these gold classes: equalizing them
          # rewrites the metric. Strictly proportional, no floor.
          axes=(("diagnosis", P),)),
    Bench("longtutor_teaching", "A", 0.12, sig_teaching, st_lt_teaching,
          ["judge dims: strategy_alignment + history_utilization (1-5)"],
          axes=(("diagnosis", P),)),
    Bench("mathtutorbench_problem_solving", "A", 0.12, sig_correct, st_none, ["Problem Solving"],
          axes=(("all", P),)),
    Bench("mathtutorbench_solution_correctness", "A", 0.12, sig_correct, st_mtb_error, ["Solution Correctness"],
          axes=(("is_error", P),)),
    Bench("mathtutorbench_mistake_location", "A", 0.12, sig_correct, st_mtb_error, ["Mistake Location"],
          axes=(("is_error", P),)),
    Bench("mathtutorbench_mistake_correction", "A", 0.12, sig_correct, st_none, ["Mistake Correction"],
          axes=(("all", P),)),
    Bench("mathtutorbench_socratic", "A", 0.12, sig_bleu, st_none, ["Socratic Questioning"],
          axes=(("all", P),)),
    Bench("mathtutorbench_pedagogy", "A", 0.12, sig_win, st_mtb_topic, ["Pedagogy IF"],
          # win_rate is a pooled mean and topic is a ~95-level long tail: this is
          # the axis that suffered the -42pp distortion. Proportional + pooling.
          axes=(("topic", P),)),
    Bench("mathtutorbench_scaffolding", "A", 0.12, sig_win, st_mtb_topic, ["Scaffolding"],
          axes=(("topic", P),)),
    # ---- Tier B (mild cut, ~40%) ----
    Bench("ceval", "B", 0.40, sig_correct, st_ceval, ["overall/category/subject accuracy"],
          axes=(("category", P),)),
    # 0.60, not 0.40: the aggregation drops pedagogy entirely below 600 scored
    # items (and below 8 categories), so a 40% list would be silently zero-evidence.
    Bench("pedagogy_benchmark", "B", 0.60, sig_correct, st_pedagogy,
          ["CDPK teaching knowledge selection", "SEND special education needs selection"],
          axes=(("category", P),)),
    Bench("mathvista", "B", 0.40, sig_correct, st_mathvista, ["task/question_type/answer_type accuracy"],
          axes=(("task", P), ("answer_type", P))),
    Bench("eduguard_adversarial", "B", 0.40, sig_adversarial, st_adversarial,
          ["Adversarial Safety ASR", "Refusal quality distribution"],
          axes=(("category", P),), panel_subdir="_judge-deepseek-v3.2"),
    Bench("ifeval", "B", 0.40, sig_correct, st_ifeval, ["prompt-level strict accuracy"],
          axes=(("n_instructions", P),)),
    Bench("mmtutorbench", "B", 0.40, sig_mmtutor, st_mmtutor, ["multimodal tutor score"],
          axes=(("domain", P), ("category", P))),
    Bench("k12vista", "B", 0.40, sig_k12, st_k12,
          ["official partial-credit score (per-blank 0/1 mean)", "math problem-figure subset score",
           "science/geo subject-chart subset score"],
          axes=(("subject_group", P), ("grade", P), ("type", P))),
]

# Tier C (full set, no list -- MINI mode runs whole but into the mini tree).
C_TIER_FULL_SET = [
    "p07_selfcheck", "p08_calibration", "p08_abstention", "mooccube_prereq",
    "mrbench_tutor", "bea2025_tutor", "eduillustrate",
    "mathtutorbench_pedagogy_hard", "mathtutorbench_scaffolding_hard",
    "mathtutorbench_judge_calibration", "mmtutorbench_judge_calibration",
]

# tutorbench is consumed by the mapping but has no per-item repo run (its score is
# parsed from the 0701 otherbenchmark HTML card), so it cannot be curated here.
NOT_SELECTABLE = ["tutorbench"]


def discover_faces(bench: Bench) -> list[dict[str, Any]]:
    """Return one entry per distinct panel model face at full item count.

    Duplicates of the same canonical model (e.g. a dated dir and a slug dir that
    are both MiniMax-M3) are collapsed to one, matching the aggregation's panel.
    """
    base = bench.panel_base()
    if not base.exists():
        return []
    candidates = []
    for d in sorted(base.iterdir()):
        if not d.is_dir() or d.name.startswith("_"):
            continue
        scored = d / "scored.jsonl"
        if not scored.exists():
            continue
        n = sum(1 for _ in scored.open(encoding="utf-8"))
        model = d.name
        summ = d / "summary.json"
        if summ.exists():
            try:
                model = json.loads(summ.read_text(encoding="utf-8")).get("model") or d.name
            except json.JSONDecodeError:
                pass
        candidates.append({"dir": d, "name": d.name, "lines": n, "model": model,
                            "model_key": canonical_model(model)})
    if not candidates:
        return []
    full = max(c["lines"] for c in candidates)
    full_faces = [c for c in candidates if c["lines"] == full]
    # Dedupe by canonical model; prefer the slug dir over a dated snapshot dir.
    by_key: dict[str, dict[str, Any]] = {}
    for c in sorted(full_faces, key=lambda x: (x["name"][:1].isdigit(), x["name"])):
        by_key.setdefault(c["model_key"], c)
    return [by_key[k] for k in sorted(by_key)]


def weighted_sample(items: list[str], k: int, disc: dict[str, float], seed_str: str) -> list[str]:
    """Proportional-random pick of k items, discrimination as a gentle priority.

    Efraimidis-Spirakis weighted sampling without replacement with weight
    ``1 + 0.5 * normalized_discrimination`` -- higher-disagreement items are
    mildly favoured but never hard-filtered.  Fully determined by the seed.
    """
    if k >= len(items):
        return sorted(items)
    import random

    rng = random.Random(sha_rng_seed(seed_str))
    mx = max((disc.get(i, 0.0) for i in items), default=0.0) or 1.0
    keyed = []
    for it in sorted(items):
        w = 1.0 + 0.5 * (disc.get(it, 0.0) / mx)
        u = rng.random()
        keyed.append((u ** (1.0 / w), it))
    keyed.sort(reverse=True)
    return sorted(it for _, it in keyed[:k])


def largest_remainder(sizes: dict[Any, int], target: int) -> dict[Any, int]:
    """Allocate ``target`` items across strata in proportion to their size.

    Largest-remainder (Hare quota): floor each exact share, then hand the leftover
    seats to the largest fractional remainders.  Ties break on the stringified key
    so the result is fully deterministic.  Allocations are capped at stratum size
    and the freed remainder is redistributed, so the total is met exactly whenever
    the population allows it.
    """
    total = sum(sizes.values())
    if target >= total:
        return dict(sizes)
    if target <= 0 or total == 0:
        return {k: 0 for k in sizes}

    alloc: dict[Any, int] = {}
    active = dict(sizes)
    assigned = 0
    while True:
        pool = target - assigned
        denom = sum(active.values())
        if not active or pool <= 0 or denom == 0:
            break
        exact = {k: pool * n / denom for k, n in active.items()}
        base = {k: int(math.floor(v)) for k, v in exact.items()}
        leftover = pool - sum(base.values())
        order = sorted(active, key=lambda k: (-(exact[k] - base[k]), str(k)))
        for k in order[:leftover]:
            base[k] += 1
        # Cap at stratum size; anything capped is finalized and its surplus is
        # redistributed among the strata that still have room.
        capped = {k: v for k, v in base.items() if v >= active[k]}
        if capped:
            for k in capped:
                alloc[k] = active[k]
                assigned += active[k]
                del active[k]
            continue
        for k, v in base.items():
            alloc[k] = v
            assigned += v
        break
    for k in sizes:
        alloc.setdefault(k, 0)
    return alloc


def quantile_bins(values: list[float], n_bins: int) -> list[float]:
    """Return ``n_bins - 1`` interior cut points for equal-frequency bins."""
    if not values:
        return []
    s = sorted(values)
    cuts = []
    for b in range(1, n_bins):
        idx = int(round(b * len(s) / n_bins))
        idx = min(max(idx, 0), len(s) - 1)
        cuts.append(s[idx])
    return cuts


def bin_of(value: float, cuts: list[float]) -> int:
    lo = 0
    for c in cuts:
        if value <= c:
            return lo
        lo += 1
    return lo


def select_benchmark(
    bench: Bench,
    exclude_model_key: str | None = None,
    rate_override: float | None = None,
) -> dict[str, Any] | None:
    """Select the mini subset for one benchmark.

    ``exclude_model_key`` drops that model face from the *difficulty/discrimination
    estimate only* (the item universe is unchanged) -- used by the leave-one-out
    validation.  ``rate_override`` replaces the tier sampling rate -- used by the
    auto-retighten loop when a cell fails acceptance.
    """
    faces = discover_faces(bench)
    if not faces:
        return None
    rate = rate_override if rate_override is not None else bench.rate
    full_count = faces[0]["lines"]
    diff_faces = [f for f in faces if f["model_key"] != exclude_model_key]

    # Read each face into item_id -> signal; also keep a representative row for
    # bucket/label extraction (buckets are identical across faces).
    per_face_signal: list[dict[str, float | None]] = []
    rep_row: dict[str, dict[str, Any]] = {}
    for face in faces:
        rows = read_scored(face["dir"] / "scored.jsonl")
        sig_map: dict[str, float | None] = {}
        for r in rows:
            iid = str(r["item_id"])
            sig_map[iid] = bench.signal(r) if bench.signal else None
            rep_row.setdefault(iid, r)
        per_face_signal.append({"model_key": face["model_key"], "sig": sig_map})

    item_ids = sorted(rep_row)
    use_difficulty = len(diff_faces) >= MIN_FACES_FOR_DIFFICULTY

    difficulty: dict[str, float | None] = {}
    disc: dict[str, float] = {}
    for iid in item_ids:
        vals = [m["sig"].get(iid) for m in per_face_signal if m["model_key"] != exclude_model_key]
        vals = [v for v in vals if v is not None]
        difficulty[iid] = statistics.fmean(vals) if vals else None
        disc[iid] = statistics.pvariance(vals) if len(vals) >= 2 else 0.0

    # content stratum -> list of item_ids
    content: dict[tuple, list[str]] = {}
    for iid in item_ids:
        content.setdefault(bench.strata(rep_row[iid]), []).append(iid)

    # Pool rare content groups so the long tail cannot soak up quota.
    pooled: dict[tuple, list[str]] = {}
    n_pooled_groups = 0
    for ckey, ids in sorted(content.items(), key=lambda kv: tuple(map(str, kv[0]))):
        if len(ids) < RARE_GROUP_MIN:
            pooled.setdefault(("__other__",), []).extend(ids)
            n_pooled_groups += 1
        else:
            pooled[ckey] = ids

    # Layer difficulty quintiles inside each sufficiently large content group.
    # Bins are equal-frequency, so proportional allocation across them preserves
    # the difficulty profile as well as the content profile.
    strata: dict[tuple, list[str]] = {}
    for ckey, ids in pooled.items():
        diff_vals = [difficulty[i] for i in ids if difficulty[i] is not None]
        if use_difficulty and len(ids) >= DIFF_SPLIT_MIN and len(set(diff_vals)) > 1:
            cuts = quantile_bins(diff_vals, N_DIFF_BINS)
            for i in ids:
                d = difficulty[i]
                b = bin_of(d, cuts) if d is not None else "na"
                strata.setdefault(ckey + (f"d{b}",), []).append(i)
        else:
            strata.setdefault(ckey + ("d*",), []).extend(ids)

    # Strict proportional allocation to the benchmark's target size.  No
    # per-stratum floor: on a proportional axis a floor is exactly the bias that
    # broke round 1.
    target = max(round(rate * len(item_ids)), min(MIN_TOTAL_ITEMS, len(item_ids)))
    sizes = {k: len(v) for k, v in strata.items()}
    quota = largest_remainder(sizes, target)

    selected: set[str] = set()
    stratum_report = []
    for skey in sorted(strata, key=lambda t: tuple(map(str, t))):
        ids = strata[skey]
        k = quota[skey]
        picked = weighted_sample(ids, k, disc, f"{bench.bid}|{'/'.join(map(str, skey))}") if k else []
        selected.update(picked)
        stratum_report.append({"stratum": "/".join(map(str, skey)),
                               "n_total": len(ids), "n_selected": len(picked)})

    # Coverage-axis floors only (never a proportional axis).
    for axis_name, floor in sorted(bench.coverage_floor.items()):
        by_level: dict[str, list[str]] = {}
        for iid in item_ids:
            by_level.setdefault(_b(rep_row[iid], axis_name), []).append(iid)
        for level, ids in sorted(by_level.items()):
            have = [i for i in ids if i in selected]
            if len(have) < floor:
                need = min(floor, len(ids)) - len(have)
                pool = [i for i in ids if i not in selected]
                selected.update(weighted_sample(pool, need, disc, f"{bench.bid}|floor|{axis_name}|{level}"))

    composition = composition_report(bench, rep_row, item_ids, selected)

    # Per-cell counts (how many selected items land in each consumed cell).
    cell_counts = per_cell_counts(bench, rep_row, selected)

    return {
        "benchmark": bench.bid,
        "tier": bench.tier,
        "rate": rate,
        "full_count": full_count,
        "selected_count": len(selected),
        "n_faces": len(faces),
        "difficulty_estimated": use_difficulty,
        "panel_models": [f["model_key"] for f in faces],
        "consumed_cells": bench.cells,
        "allocation": "largest_remainder_proportional",
        "axes": [{"axis": n, "kind": k} for n, k in bench.axes],
        "coverage_floor": bench.coverage_floor,
        "rare_group_min": RARE_GROUP_MIN,
        "n_pooled_rare_groups": n_pooled_groups,
        "n_strata": len(strata),
        "composition": composition,
        "max_abs_shift_pp_proportional_axes": round(
            max([v["max_abs_shift_pp"] for v in composition.values() if v["kind"] == "proportional"],
                default=0.0), 3),
        "strata": stratum_report,
        "cell_selected_counts": cell_counts,
        "selected_ids": sorted(selected),
    }


def composition_report(bench: Bench, rep_row: dict[str, dict[str, Any]],
                       item_ids: list[str], selected: set[str]) -> dict[str, Any]:
    """Population vs mini share per axis level, in percentage points.

    ``max_abs_shift_pp`` on a proportional axis is the headline fidelity number:
    it is the largest amount by which the curated subset misrepresents the
    population on an axis the metric actually depends on."""
    out: dict[str, Any] = {}
    for idx, (axis_name, kind) in enumerate(bench.axes):
        full_c: dict[str, int] = {}
        mini_c: dict[str, int] = {}
        for iid in item_ids:
            key = bench.strata(rep_row[iid])
            level = str(key[idx]) if idx < len(key) else "?"
            full_c[level] = full_c.get(level, 0) + 1
            if iid in selected:
                mini_c[level] = mini_c.get(level, 0) + 1
        nf, nm = len(item_ids), len(selected)
        levels = []
        worst = 0.0
        for level in sorted(full_c):
            fp = 100.0 * full_c[level] / nf if nf else 0.0
            mp = 100.0 * mini_c.get(level, 0) / nm if nm else 0.0
            worst = max(worst, abs(mp - fp))
            levels.append({"level": level, "full_pct": round(fp, 3),
                           "mini_pct": round(mp, 3), "shift_pp": round(mp - fp, 3)})
        out[axis_name] = {
            "kind": kind,
            "n_levels": len(full_c),
            "max_abs_shift_pp": round(worst, 3),
            "levels": levels if len(levels) <= 12 else
                      sorted(levels, key=lambda x: -abs(x["shift_pp"]))[:12],
        }
    return out


def per_cell_counts(bench: Bench, rep_row: dict[str, dict[str, Any]], selected: set[str]) -> dict[str, int]:
    """Count selected items per consumed cell (cells that partition the item pool
    -- olympiadbench MM, k12vista subject groups, pedagogy CDPK/SEND -- get the
    subset count; whole-benchmark cells get the total)."""
    counts: dict[str, int] = {}
    sel_rows = [rep_row[i] for i in selected]
    if bench.bid == "olympiadbench":
        counts["overall/subject/language/modality accuracy"] = len(sel_rows)
        counts["multimodal-subset accuracy"] = sum(1 for r in sel_rows if _b(r, "modality") == "MM")
    elif bench.bid == "k12vista":
        counts["official partial-credit score (per-blank 0/1 mean)"] = len(sel_rows)
        counts["math problem-figure subset score"] = sum(1 for r in sel_rows if _b(r, "subject").startswith("math"))
        counts["science/geo subject-chart subset score"] = sum(1 for r in sel_rows if not _b(r, "subject").startswith("math"))
    elif bench.bid == "pedagogy_benchmark":
        counts["SEND special education needs selection"] = sum(1 for r in sel_rows if _b(r, "category") == "CDPK_send")
        counts["CDPK teaching knowledge selection"] = sum(1 for r in sel_rows if _b(r, "category") != "CDPK_send")
    else:
        for c in bench.cells:
            counts[c] = len(sel_rows)
    return counts


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest: dict[str, Any] = {
        "version": "mini_v1",
        "seed": SEED,
        "difficulty_bins": N_DIFF_BINS,
        "min_faces_for_difficulty": MIN_FACES_FOR_DIFFICULTY,
        "generated_by": "scripts/build_mini_selection_v1.py",
        "note": (
            "Curated item selection for daily evaluation; the full set is retained "
            "for calibration. Strata = aggregation-consumed content bucket x "
            "difficulty quintile; proportional-random sampling with discrimination "
            "as a gentle within-stratum priority. Zero API calls."
        ),
        "benchmarks": {},
        "full_set_tier_c": [],
        "not_selectable": [],
    }

    total_full = 0
    total_mini = 0
    for bench in BENCHES:
        result = select_benchmark(bench)
        if result is None:
            print(f"[skip] {bench.bid}: no full-panel faces found")
            continue
        ids = result.pop("selected_ids")
        list_path = OUT_DIR / f"{bench.bid}_items_v1.txt"
        list_path.write_text("\n".join(ids) + "\n", encoding="utf-8")
        result["item_list"] = list_path.relative_to(ROOT).as_posix()
        result["item_list_sha256"] = hashlib.sha256(
            (("\n".join(ids) + "\n").encode("utf-8"))
        ).hexdigest()
        manifest["benchmarks"][bench.bid] = result
        total_full += result["full_count"]
        total_mini += result["selected_count"]
        frac = result["selected_count"] / result["full_count"] if result["full_count"] else 0.0
        print(f"[{bench.tier}] {bench.bid:32s} {result['selected_count']:6d}/{result['full_count']:6d} "
              f"= {frac:5.1%}  strata={result['n_strata']} faces={result['n_faces']}")

    for bid in C_TIER_FULL_SET:
        manifest["full_set_tier_c"].append({"benchmark": bid, "tier": "C", "full_set": True})
    for bid in NOT_SELECTABLE:
        manifest["not_selectable"].append({"benchmark": bid,
                                           "reason": "no per-item repo run (scored from otherbenchmark HTML card)"})

    manifest["totals"] = {
        "curated_benchmarks": len(manifest["benchmarks"]),
        "full_items_curated_benchmarks": total_full,
        "mini_items_curated_benchmarks": total_mini,
        "mini_fraction_curated_benchmarks": round(total_mini / total_full, 4) if total_full else None,
    }

    manifest_path = OUT_DIR / "selection_manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"\nCurated {total_mini}/{total_full} items across {len(manifest['benchmarks'])} benchmarks "
          f"({total_mini / total_full:.1%} of their full item count)")
    print(f"manifest -> {manifest_path.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
