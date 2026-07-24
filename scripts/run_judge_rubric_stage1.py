#!/usr/bin/env python3
"""Stage 1: structured rubric + diagnosis-driven typed edits, one dimension at a time.

Plan: doc/rubric_evolution_plan_2026-07-06.md (Stage 1/2). One invocation runs
one evolution ROUND for one (benchmark, dimension):

1. propose  — a reflection model reads the aggregated diagnosis
   (build_judge_stage1_assets.py) plus the current rubric and emits typed edit
   proposals targeting specific confusion cells; a fixed ``dpfs_cal`` anchor
   candidate is always injected in round 1 as the calibration reference line.
2. screen   — every candidate is judged on the frozen ~150-item screening
   slice; candidates whose paired macro-kappa diff vs the incumbent is <= 0
   are eliminated; the top ``--survivors`` advance.
3. full     — survivors run the full ~600-item eval slice; a candidate is
   ACCEPTED only if the cluster-bootstrap paired diff CI vs the incumbent
   excludes 0 and its unparsed rate does not regress (>1pp). The best accepted
   candidate becomes the new incumbent (per-dimension gating: other
   dimensions keep rubric v1 untouched).

Rubric = structured object {definition_override, label_criteria per label,
clauses[], anchor_block}; edits are typed operators
(set_label_criterion / add_clause / drop_clause / edit_definition /
add_anchor_block / remove_anchor_block), so every accepted change is
auditable and reversible. Ledger rows carry edits + effect sizes + CI +
prompt sha256.

Protocol guards: dev-only (asserted); reflection sees only the diagnosis pool;
anchors come from pool conversations, never the eval slice; the incumbent v1
labels come from the judge's cached full run (no duplicate spend).

Usage (judge defaults to MiniMax-M3 — needs MINIMAX_API_KEY; reflection
defaults to glm-5.2 — needs API_GATEWAY):
    python scripts/run_judge_rubric_stage1.py --benchmark mrbench --dimension Providing_Guidance --round 1
    python scripts/run_judge_rubric_stage1.py --benchmark bea2025 --dimension Providing_Guidance --round 1 --concurrency 6
"""

from __future__ import annotations

import argparse
import copy
import json
import os
import random
import threading
import time
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from itertools import product

from build_judge_stage1_assets import make_diagnosis, stage1_out_base
from eval.base import prompt_sha256
from eval.predictions_io import read_predictions
from eval.providers import build_client
from eval.stats import cluster_bootstrap_diff_ci, kappa_stat
from run_judge_rubric_variants import adapter_bits, anchor_block, load_items

ROOT = Path(__file__).resolve().parents[1]
META_DIR = ROOT / "data" / "judge_meta_eval_v1"
SLICE_DIR = META_DIR / "stage1_slices"

SEED = 20260707
K_ANCHORS = 6
MAX_EXTRA_TEMPLATE_CHARS = 7000
JUDGE_MODEL = os.environ.get("STAGE1_JUDGE_MODEL", "MiniMax-M3")
REFLECT_MODEL = os.environ.get("STAGE1_REFLECT_MODEL", "glm-5.2")
JUDGE_SLUGS = {"MiniMax-M3": "minimax3", "glm-5.2": "glm-5.2", "deepseek-v4-pro": "deepseek-v4-pro"}
# State is judge-keyed: the M3 pilot keeps its original stage1/ layout, other
# judges (e.g. STAGE1_JUDGE_MODEL=glm-5.2) get stage1_<slug>/ — run
# build_judge_stage1_assets.py --judge-slug <slug> first to seed diagnosis.json.
# STAGE1_OUT_SLUG isolates a fresh state dir (e.g. minimax3_full for the
# full-Stage-2-spec M3 rerun) while cached v1 labels still come from the
# judge's own slug.
OUT_BASE = stage1_out_base(os.environ.get("STAGE1_OUT_SLUG", JUDGE_SLUGS[JUDGE_MODEL]))
BASELINE_DIRS = {"mrbench": "mrbench_judge", "bea2025": "bea2025_judge"}

OPERATOR_DOC = """Allowed edit operators (each proposal = 1-3 edits):
- {"op": "set_label_criterion", "label": "<one of the dimension's labels>", "text": "<one-sentence behavioral criterion: what a reply must DO to earn this label>"}
- {"op": "add_clause", "text": "<one boundary-clarification rule targeting a specific confusion, e.g. how to decide between two labels in a described situation>"}
- {"op": "drop_clause", "id": "<existing clause id>"}
- {"op": "edit_definition", "text": "<replacement one-or-two-sentence definition of the dimension>"}
- {"op": "add_anchor_block", "calibrated": true}
- {"op": "remove_anchor_block"}"""


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    if not path.exists():
        return rows
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _write_json(path: Path, obj: Any) -> None:
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def empty_rubric(benchmark: str, dim: str) -> dict[str, Any]:
    return {
        "benchmark": benchmark,
        "dimension": dim,
        "version": "v1",
        "definition_override": None,
        "label_criteria": {},
        "clauses": [],
        "anchor_block": None,
    }


def apply_edits(rubric: dict[str, Any], edits: list[dict[str, Any]], labels: tuple[str, ...]) -> dict[str, Any]:
    r = copy.deepcopy(rubric)
    for e in edits:
        op = e.get("op")
        if op == "set_label_criterion":
            if e["label"] not in labels:
                raise ValueError(f"unknown label {e['label']!r}")
            r["label_criteria"][e["label"]] = str(e["text"]).strip()
        elif op == "add_clause":
            cid = f"c{1 + max([int(c['id'][1:]) for c in r['clauses']] or [0])}"
            r["clauses"].append({"id": cid, "text": str(e["text"]).strip()})
        elif op == "drop_clause":
            before = len(r["clauses"])
            r["clauses"] = [c for c in r["clauses"] if c["id"] != e["id"]]
            if len(r["clauses"]) == before:
                raise ValueError(f"no clause {e['id']!r}")
        elif op == "edit_definition":
            r["definition_override"] = str(e["text"]).strip()
        elif op == "add_anchor_block":
            r["anchor_block"] = {"k": K_ANCHORS, "calibrated": bool(e.get("calibrated", True))}
        elif op == "remove_anchor_block":
            r["anchor_block"] = None
        else:
            raise ValueError(f"unknown op {op!r}")
    return r


class Renderer:
    """Renders a structured rubric into a judge prompt. With an empty rubric the
    output is byte-identical to the adapter's v1 prompt (asserted at init)."""

    def __init__(self, benchmark: str, dim: str, big_screen: bool = False):
        self.benchmark, self.dim = benchmark, dim
        self.dims, self.judge_prompt, self.normalize = adapter_bits(benchmark)
        self.cfg = self.dims[dim]
        self.labels: tuple[str, ...] = tuple(self.cfg["labels"])
        items, self.contexts = load_items(benchmark)
        self.items = [it for it in items if str(it["dimension"]) == dim and it["split"] == "dev"]
        assert all(it["split"] == "dev" for it in self.items)

        screen_name = "__screen250.txt" if big_screen else "__screen.txt"
        eval_ids = (SLICE_DIR / f"{benchmark}__{dim}__eval.txt").read_text(encoding="utf-8").split()
        screen_ids = (SLICE_DIR / f"{benchmark}__{dim}{screen_name}").read_text(encoding="utf-8").split()
        self.eval_ids, self.screen_ids = set(eval_ids), set(screen_ids)
        by_id = {it["native_item_id"]: it for it in self.items}
        self.eval_items = [by_id[i] for i in sorted(self.eval_ids)]
        eval_convs = {it["conversation_id"] for it in self.eval_items}
        self.pool = [it for it in self.items if it["conversation_id"] not in eval_convs]

        # DPFS anchors + marginals from the pool only (never the eval slice).
        rng = random.Random(f"{SEED}:{benchmark}:{dim}:anchors")
        by_label: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for it in self.pool:
            by_label[it["human_label"]].append(it)
        total = len(self.pool)
        self.marginals = {lab: len(rows) / total for lab, rows in sorted(by_label.items())}
        quotas = {lab: K_ANCHORS * len(rows) / total for lab, rows in by_label.items()}
        counts = {lab: int(q) for lab, q in quotas.items()}
        for lab in sorted(quotas, key=lambda l: -(quotas[l] - counts[l])):
            if sum(counts.values()) >= K_ANCHORS:
                break
            counts[lab] += 1
        chosen: list[dict[str, Any]] = []
        for lab in sorted(counts):
            rows = sorted(by_label[lab], key=lambda it: it["native_item_id"])
            compact = [it for it in rows if 8 <= len(str(it["response"]).split()) <= 80] or rows
            chosen.extend(rng.sample(compact, min(counts[lab], len(compact))))
        rng.shuffle(chosen)
        for a in chosen:
            assert a["native_item_id"] not in self.eval_ids, "anchor leaked from eval slice"
        self.anchors = chosen

        base = self.judge_prompt(dim, "{conversation_history}", "{response}")
        assert self.render_template(empty_rubric(benchmark, dim)) == base, "v1 render mismatch"
        self.v1_template_len = len(base)

    def _extras(self, rubric: dict[str, Any]) -> str:
        parts: list[str] = []
        if rubric["label_criteria"]:
            parts.append("Label criteria:")
            for lab in self.labels:
                if rubric["label_criteria"].get(lab):
                    parts.append(f"- \"{lab}\": {rubric['label_criteria'][lab]}")
        if rubric["clauses"]:
            parts.append("Additional judging rules:")
            for c in rubric["clauses"]:
                parts.append(f"- {c['text']}")
        return "\n".join(parts)

    def render(self, rubric: dict[str, Any], conversation_history: str, response: str) -> str:
        base = self.judge_prompt(self.dim, conversation_history, response)
        if rubric["definition_override"]:
            orig = self.cfg["definition"]
            assert orig in base
            base = base.replace(orig, rubric["definition_override"], 1)
        extras = self._extras(rubric)
        if extras:
            head, tail = base.rsplit("\n\nChoose", 1)
            base = f"{head}\n\n{extras}\n\nChoose{tail}"
        if rubric["anchor_block"]:
            marg = self.marginals if rubric["anchor_block"].get("calibrated") else None
            block = anchor_block(self.cfg, self.anchors, self.contexts, marg)
            base = f"{block}\nNow judge the following case.\n\n{base}"
        return base

    def render_template(self, rubric: dict[str, Any]) -> str:
        return self.render(rubric, "{conversation_history}", "{response}")


def load_incumbent(state_dir: Path, rnd: Renderer, benchmark: str) -> tuple[dict[str, Any], dict[str, str]]:
    """Current rubric + its labels on the eval slice. v1 labels come from the
    judge's cached full run; accepted candidates store their own."""
    rubric_path = state_dir / "rubric_current.json"
    if rubric_path.exists():
        rubric = json.loads(rubric_path.read_text(encoding="utf-8"))
        labels = {
            r["item_id"]: r["label"] for r in _read_jsonl(state_dir / "incumbent_responses.jsonl")
        }
        return rubric, labels
    slug = JUDGE_SLUGS[JUDGE_MODEL]
    scored = ROOT / "reports" / "eval" / BASELINE_DIRS[benchmark] / slug / "scored.jsonl"
    labels = {
        str(r["item_id"]): str(r["pred_label"])
        for r in _read_jsonl(scored)
        if r.get("score_status") == "scored" and "pred_label" in r and str(r["item_id"]) in rnd.eval_ids
    }
    if not labels:
        raise SystemExit(f"no cached v1 labels for {JUDGE_MODEL} under {scored}")
    return empty_rubric(benchmark, rnd.dim), labels


def reflection_prompt(
    rnd: Renderer, rubric: dict[str, Any], diagnosis: dict[str, Any], n: int, prior: str = ""
) -> str:
    cells = []
    for cell, examples in diagnosis["error_examples_by_cell"].items():
        exs = []
        for ex in examples[:4]:
            exs.append(
                f"  - Tutor reply: {str(ex['tutor_reply'])[:400]}\n"
                f"    Judge's reasoning (excerpt): {str(ex['judge_reasoning'])[-400:]}"
            )
        cells.append(f"Confusion cell {cell}:\n" + "\n".join(exs))
    return (
        "You are improving the rubric prompt of an LLM judge that labels AI tutor replies "
        f"on the pedagogical dimension \"{rnd.cfg['title']}\" with one of: "
        f"{' / '.join(rnd.labels)}.\n\n"
        f"Current dimension definition: {rubric['definition_override'] or rnd.cfg['definition']}\n"
        f"Current rubric additions (JSON): {json.dumps({k: rubric[k] for k in ('label_criteria', 'clauses', 'anchor_block')}, ensure_ascii=False)}\n\n"
        "Measured disagreement with expert human annotators on a held-out pool "
        f"(agreement rate {diagnosis['agreement_rate']}):\n"
        f"Human label marginals: {json.dumps(diagnosis['human_marginals'])}\n"
        f"Judge label marginals: {json.dumps(diagnosis['judge_marginals'])}\n"
        f"Confusion matrix (rows = human, cols = judge): {json.dumps(diagnosis['confusion_matrix'])}\n\n"
        "Real disagreement examples with the judge's own reasoning:\n\n"
        + "\n\n".join(cells)
        + (
            "\n\nPreviously tested proposals and their measured outcomes — do NOT repeat "
            "failed ideas; refining a near-miss is allowed:\n" + prior
            if prior
            else ""
        )
        + "\n\n"
        + OPERATOR_DOC
        + f"\n\nPropose exactly {n} DISTINCT edit proposals. Each proposal must target a specific "
        "confusion cell visible above (say which in \"note\") and change how the judge decides "
        "that boundary. Criteria and clauses must be behavioral (what the reply does), not "
        "restatements of the label names. Keep each text under 60 words.\n\n"
        "Output ONLY a JSON array, no markdown fences, of objects: "
        '{"note": "<which cell this targets and why>", "edits": [<1-3 operator objects>]}'
    )


def reflection_prompt_nodiag(
    rnd: Renderer, rubric: dict[str, Any], n: int, prior: str = ""
) -> str:
    """P5 ablation: the same proposal step with the diagnosis removed.

    Everything the full method gives the reflection model is kept — the same
    typed operators, the same length budget, the same failure ledger — EXCEPT
    the measured confusion matrix, the label marginals and the real error
    examples. What survives is a strong LLM writing rubric edits from the
    dimension definition alone. Screening, the frozen eval slice and the
    significance gate are unchanged, so acceptance counts are directly
    comparable to the full method's.
    """
    return (
        "You are improving the rubric prompt of an LLM judge that labels AI tutor replies "
        f"on the pedagogical dimension \"{rnd.cfg['title']}\" with one of: "
        f"{' / '.join(rnd.labels)}.\n\n"
        f"Current dimension definition: {rubric['definition_override'] or rnd.cfg['definition']}\n"
        f"Current rubric additions (JSON): {json.dumps({k: rubric[k] for k in ('label_criteria', 'clauses', 'anchor_block')}, ensure_ascii=False)}\n\n"
        "The judge is scored by its agreement (Cohen's kappa) with expert human annotators. "
        "Your edits should make the judge's labels match expert human judgement more often.\n"
        + (
            "\nPreviously tested proposals and their measured outcomes — do NOT repeat "
            "failed ideas; refining a near-miss is allowed:\n" + prior
            if prior
            else ""
        )
        + "\n\n"
        + OPERATOR_DOC
        + f"\n\nPropose exactly {n} DISTINCT edit proposals. Each proposal must target a specific "
        "label boundary you believe the judge gets wrong (say which in \"note\") and change how "
        "the judge decides that boundary. Criteria and clauses must be behavioral (what the reply "
        "does), not restatements of the label names. Keep each text under 60 words.\n\n"
        "Output ONLY a JSON array, no markdown fences, of objects: "
        '{"note": "<which boundary this targets and why>", "edits": [<1-3 operator objects>]}'
    )


def parse_proposals(text: str) -> list[dict[str, Any]]:
    start, end = text.find("["), text.rfind("]")
    if start < 0 or end <= start:
        raise ValueError("no JSON array found")
    arr = json.loads(text[start : end + 1])
    if not isinstance(arr, list):
        raise ValueError("not a list")
    out = []
    for p in arr:
        if isinstance(p, dict) and isinstance(p.get("edits"), list) and p["edits"]:
            out.append({"note": str(p.get("note", "")), "edits": p["edits"][:3]})
    return out


def run_candidate(
    rnd: Renderer,
    rubric: dict[str, Any],
    items: list[dict[str, Any]],
    resp_path: Path,
    client: Any,
    concurrency: int,
    retries: int,
) -> dict[str, str]:
    """Judge ``items`` under ``rubric``; resumable via responses.jsonl.
    Returns item_id -> normalized label for all cached+new non-empty rows."""
    item_ids = {it["native_item_id"] for it in items}
    done = {r["item_id"]: r for r in _read_jsonl(resp_path) if str(r.get("response") or "").strip()}
    todo = [it for it in items if it["native_item_id"] not in done]
    # Circuit breaker: a long run of consecutive failures means the provider is
    # down or the quota is exhausted (MiniMax base_resp 2056) — abort instead of
    # burning retries on every remaining item. Empty rows are not cached, so a
    # rerun resumes exactly here.
    consecutive_failures = [0]
    lock = threading.Lock()

    def call(it: dict[str, Any]) -> dict[str, Any]:
        prompt = rnd.render(rubric, rnd.contexts.get(it["conversation_id"], ""), it["response"])
        started, error, text = time.time(), None, ""
        for attempt in range(retries):
            try:
                # No max_tokens cap (glm/M3 reasoning may starve the answer).
                text = client.chat([{"role": "user", "content": prompt}], model=JUDGE_MODEL)
                error = None
                if text.strip():
                    break
            except Exception as exc:  # noqa: BLE001
                error = str(exc)
            time.sleep(2.0 * (attempt + 1))
        row = {"item_id": it["native_item_id"], "response": text, "latency_seconds": round(time.time() - started, 2)}
        if error:
            row["error"] = error
        with lock:
            consecutive_failures[0] = consecutive_failures[0] + 1 if not text.strip() else 0
            if consecutive_failures[0] >= 25:
                raise SystemExit(f"aborting: 25 consecutive failed judge calls (last: {error})")
        return row

    if todo:
        resp_path.parent.mkdir(parents=True, exist_ok=True)
        completed = 0
        with ThreadPoolExecutor(max_workers=concurrency) as pool, resp_path.open("a", encoding="utf-8") as fh:
            for row in pool.map(call, todo):
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")
                fh.flush()
                completed += 1
                if completed % 50 == 0 or row.get("error"):
                    print(f"    {completed}/{len(todo)} last={row['item_id']} err={row.get('error')}")
        done = {r["item_id"]: r for r in _read_jsonl(resp_path) if str(r.get("response") or "").strip()}
    return {
        iid: rnd.normalize(rnd.dim, r["response"]) for iid, r in done.items() if iid in item_ids
    }


def paired_eval(
    rnd: Renderer,
    cand_labels: dict[str, str],
    inc_labels: dict[str, str],
    item_ids: set[str],
    n_boot: int,
    items: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    rows = []
    for it in (items if items is not None else rnd.eval_items):
        nid = it["native_item_id"]
        if nid in item_ids and nid in cand_labels and nid in inc_labels:
            rows.append((it["conversation_id"], {"gold": it["human_label"], "a": cand_labels[nid], "b": inc_labels[nid]}))
    if not rows:
        return {
            "point": None, "point_a": None, "point_b": None, "ci_low": None, "ci_high": None,
            "significant": False, "n_paired": 0,
            "unparsed_rate_candidate": None, "unparsed_rate_incumbent": None,
        }
    diff = cluster_bootstrap_diff_ci(
        rows,
        lambda ps: kappa_stat([(p["gold"], p["a"]) for p in ps]),
        lambda ps: kappa_stat([(p["gold"], p["b"]) for p in ps]),
        n_boot=n_boot,
    )
    diff["n_paired"] = len(rows)
    diff["unparsed_rate_candidate"] = round(
        sum(p["a"] == "unparsed" for _, p in rows) / len(rows), 4
    ) if rows else None
    diff["unparsed_rate_incumbent"] = round(
        sum(p["b"] == "unparsed" for _, p in rows) / len(rows), 4
    ) if rows else None
    return diff


def pool_subsample(rnd: Renderer, target: int = 600) -> list[dict[str, Any]]:
    """Deterministic conversation-grouped subsample of the diagnosis pool.
    Constant across rounds so incumbent pool responses are reusable."""
    by_conv: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for it in rnd.pool:
        by_conv[it["conversation_id"]].append(it)
    convs = sorted(by_conv)
    random.Random(f"{SEED}:{rnd.benchmark}:{rnd.dim}:rediag").shuffle(convs)
    out: list[dict[str, Any]] = []
    for c in convs:
        if len(out) >= target:
            break
        out.extend(by_conv[c])
    return out


def cached_v1_pool_data(benchmark: str, ids: set[str]) -> tuple[dict[str, str], dict[str, dict[str, Any]]]:
    """v1 labels + raw rows for pool items from the judge's cached full run."""
    run_dir = ROOT / "reports" / "eval" / BASELINE_DIRS[benchmark] / JUDGE_SLUGS[JUDGE_MODEL]
    labels = {
        str(r["item_id"]): str(r["pred_label"])
        for r in _read_jsonl(run_dir / "scored.jsonl")
        if r.get("score_status") == "scored" and "pred_label" in r and str(r["item_id"]) in ids
    }
    raw = {str(r["item_id"]): r for r in read_predictions(run_dir) if str(r["item_id"]) in labels}
    return labels, raw


def learn_remap(pairs: list[tuple[str, str]], labels: tuple[str, ...]) -> dict[str, str]:
    """Best post-hoc source->target label mapping by kappa on the learn pool
    (exhaustive, ties -> fewest changes) — Stage 0a stacked on the incumbent."""
    preds = sorted({p for _, p in pairs})
    best_key, best_map = None, {p: p for p in preds}
    for combo in product(labels, repeat=len(preds)):
        mapping = dict(zip(preds, combo))
        k = kappa_stat([(g, mapping[p]) for g, p in pairs])
        if k is None:
            continue
        key = (k, -sum(1 for p in preds if mapping[p] != p))
        if best_key is None or key > best_key:
            best_key, best_map = key, mapping
    return best_map


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--benchmark", required=True, choices=sorted(BASELINE_DIRS))
    parser.add_argument("--dimension", required=True)
    parser.add_argument("--round", type=int, required=True)
    parser.add_argument("--concurrency", type=int, default=6)
    parser.add_argument("--retries", type=int, default=4)
    parser.add_argument("--n-candidates", type=int, default=6, help="reflection proposals per round")
    parser.add_argument("--survivors", type=int, default=3)
    parser.add_argument("--n-boot-screen", type=int, default=200)
    parser.add_argument("--n-boot-full", type=int, default=1000)
    parser.add_argument("--limit", type=int, default=0, help="cap screen items (smoke tests only)")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--big-screen", action="store_true", help="use the 250-item screening slice")
    parser.add_argument("--rediagnose", action="store_true",
                        help="adaptive re-diagnosis: label a pool subsample with the incumbent "
                             "rubric (v1 = free from cache) and reflect on THAT confusion; also "
                             "reports the Stage-0a remap stacked on the incumbent")
    parser.add_argument("--pool-target", type=int, default=600)
    parser.add_argument("--no-diagnosis", action="store_true",
                        help="P5 ablation: propose edits WITHOUT the confusion matrix / error "
                             "examples (everything else — typed edits, screening, eval slice, "
                             "significance gate, ledger — unchanged). Use a separate state dir "
                             "via STAGE1_OUT_SLUG, e.g. glm-5.2_nodiag")
    parser.add_argument("--proposal-seed", default="",
                        help="replication nonce appended only to the reflection prompt; combine "
                             "with an isolated STAGE1_OUT_SLUG for independent proposal runs")
    args = parser.parse_args()
    if args.no_diagnosis and args.rediagnose:
        raise SystemExit("--no-diagnosis and --rediagnose are mutually exclusive")

    rnd = Renderer(args.benchmark, args.dimension, big_screen=args.big_screen)
    state_dir = OUT_BASE / f"{args.benchmark}__{args.dimension}"
    round_dir = state_dir / f"round{args.round}"
    round_dir.mkdir(parents=True, exist_ok=True)
    diagnosis = (
        {} if args.no_diagnosis
        else json.loads((state_dir / "diagnosis.json").read_text(encoding="utf-8"))
    )
    incumbent, inc_labels = load_incumbent(state_dir, rnd, args.benchmark)
    history = incumbent.get("history", [])
    print(
        f"{args.benchmark}/{args.dimension} round {args.round}: judge={JUDGE_MODEL} "
        f"incumbent={incumbent['version']} eval={len(rnd.eval_ids)} screen={len(rnd.screen_ids)} "
        f"incumbent_labels={len(inc_labels)}"
    )
    client = None if args.dry_run else build_client(JUDGE_MODEL)

    # ---- adaptive re-diagnosis + remap stacking (Stage 2) ----
    remap_stacked = None
    if args.rediagnose:
        sub = pool_subsample(rnd, args.pool_target)
        sub_ids = {it["native_item_id"] for it in sub}
        if incumbent["version"] == "v1":
            pool_labels, pool_raw = cached_v1_pool_data(args.benchmark, sub_ids)
        elif args.dry_run:
            raise SystemExit("--rediagnose --dry-run needs API calls for a non-v1 incumbent")
        else:
            pool_dir = state_dir / f"pool_{incumbent['version']}"
            pool_labels = run_candidate(
                rnd, incumbent, sub, pool_dir / "responses.jsonl", client, args.concurrency, args.retries
            )
            pool_raw = {r["item_id"]: r for r in _read_jsonl(pool_dir / "responses.jsonl")}
        sub_scored = [it for it in sub if it["native_item_id"] in pool_labels]
        diagnosis = make_diagnosis(
            sub_scored, pool_labels, pool_raw, rnd.contexts,
            {
                "stage": "stage2 adaptive re-diagnosis",
                "benchmark": args.benchmark,
                "dimension": args.dimension,
                "incumbent_version": incumbent["version"],
                "round": args.round,
                "pool": "diagnosis-pool subsample labeled by the incumbent rubric",
            },
        )
        _write_json(round_dir / "diagnosis_used.json", diagnosis)
        pairs = [(it["human_label"], pool_labels[it["native_item_id"]]) for it in sub_scored]
        mapping = learn_remap(pairs, rnd.labels)
        nontrivial = {k: v for k, v in mapping.items() if k != v}
        if nontrivial:
            remapped = {iid: mapping.get(lab, lab) for iid, lab in inc_labels.items()}
            res = paired_eval(rnd, remapped, inc_labels, rnd.eval_ids, args.n_boot_full)
            remap_stacked = {"mapping": nontrivial, **{k: res[k] for k in ("point", "point_a", "point_b", "ci_low", "ci_high", "significant", "n_paired")}}
        else:
            remap_stacked = {"mapping": {}, "note": "identity mapping optimal on pool"}
        print(
            f"  rediagnosis: pool={len(sub_scored)} agreement={diagnosis['agreement_rate']} "
            f"remap_stacked={remap_stacked.get('mapping')} diff={remap_stacked.get('point')}"
        )

    # ---- propose ----
    cand_path = round_dir / "candidates.json"
    if cand_path.exists():
        candidates = json.loads(cand_path.read_text(encoding="utf-8"))
    else:
        prior = "\n".join(
            f"- {json.dumps(r['edits'], ensure_ascii=False)[:220]} -> "
            + (
                "ACCEPTED"
                if r.get("accepted")
                else (
                    f"full-slice diff {r['full']['point']} (not significant)"
                    if r.get("full")
                    else f"eliminated at screening (diff {r['screen']['point']})"
                )
            )
            for r in _read_jsonl(state_dir / "ledger.jsonl")[-12:]
        )
        prompt = (
            reflection_prompt_nodiag(rnd, incumbent, args.n_candidates, prior)
            if args.no_diagnosis
            else reflection_prompt(rnd, incumbent, diagnosis, args.n_candidates, prior)
        )
        if args.proposal_seed:
            prompt += (
                "\n\nIndependent replication nonce: " + args.proposal_seed
                + ". Generate a fresh, diverse proposal set for this replication. "
                  "Do not mention the nonce in the proposals."
            )
        if args.dry_run:
            print("---- reflection prompt ----")
            print(prompt[:4000])
            print("---- v1 rendered judge prompt (template) ----")
            print(rnd.render_template(incumbent)[:2000])
            return
        reflect = build_client(REFLECT_MODEL)
        proposals: list[dict[str, Any]] = []
        raw_all = []
        for attempt in range(3):
            raw = reflect.chat([{"role": "user", "content": prompt}], model=REFLECT_MODEL)
            raw_all.append(raw)
            try:
                proposals = parse_proposals(raw)
            except ValueError:
                proposals = []
            if proposals:
                break
        (round_dir / "reflection_raw.txt").write_text("\n\n=====\n\n".join(raw_all), encoding="utf-8")
        if not proposals:
            raise SystemExit("reflection produced no parseable proposals after 3 attempts")

        candidates, seen = [], set()
        if args.round == 1 and incumbent["anchor_block"] is None:
            candidates.append(
                {"id": "dpfs_cal", "note": "Stage 0b calibration reference",
                 "edits": [{"op": "add_anchor_block", "calibrated": True}]}
            )
        for i, p in enumerate(proposals, 1):
            cid = f"r{args.round}p{i}"
            try:
                rub = apply_edits(incumbent, p["edits"], rnd.labels)
                tmpl = rnd.render_template(rub)
            except (ValueError, KeyError, AssertionError) as exc:
                print(f"  skip {cid}: invalid edits ({exc})")
                continue
            if len(tmpl) > rnd.v1_template_len + MAX_EXTRA_TEMPLATE_CHARS:
                print(f"  skip {cid}: over length budget")
                continue
            h = prompt_sha256(tmpl)
            if h in seen:
                continue
            seen.add(h)
            candidates.append({"id": cid, "note": p["note"], "edits": p["edits"], "prompt_sha256": h})
        _write_json(cand_path, candidates)
    print(f"candidates: {[c['id'] for c in candidates]}")

    if args.dry_run:
        return

    # ---- regression check: each accepted edit still earns its keep ----
    regression = []
    if history:
        v1_screen_labels, _ = cached_v1_pool_data(args.benchmark, rnd.screen_ids)
        for h in history:
            rub_min = empty_rubric(args.benchmark, args.dimension)
            for other in history:
                if other["id"] != h["id"]:
                    rub_min = apply_edits(rub_min, other["edits"], rnd.labels)
            if rnd.render_template(rub_min) == rnd.render_template(empty_rubric(args.benchmark, args.dimension)):
                abl_labels: dict[str, str] = v1_screen_labels
            else:
                abl_labels = run_candidate(
                    rnd, rub_min,
                    [it for it in rnd.eval_items if it["native_item_id"] in rnd.screen_ids],
                    round_dir / f"ablate_{h['id']}" / "responses.jsonl",
                    client, args.concurrency, args.retries,
                )
            res = paired_eval(rnd, abl_labels, inc_labels, rnd.screen_ids, args.n_boot_screen)
            flag = bool(res["point"] and res["point"] > 0.02)
            regression.append({"ablated": h["id"], "ablation_minus_incumbent": res["point"],
                               "screen_n": res["n_paired"], "harmful_flag": flag})
            if flag:
                print(f"  WARNING regression: removing {h['id']} IMPROVES screen kappa by {res['point']}")

    # ---- screen ----
    screen_ids = set(sorted(rnd.screen_ids)[: args.limit]) if args.limit else rnd.screen_ids
    screen_items = [it for it in rnd.eval_items if it["native_item_id"] in screen_ids]
    screened = []
    for c in candidates:
        rub = apply_edits(incumbent, c["edits"], rnd.labels)
        print(f"  screening {c['id']} ({c['note'][:70]})")
        labels = run_candidate(
            rnd, rub, screen_items, round_dir / f"cand_{c['id']}" / "responses.jsonl",
            client, args.concurrency, args.retries,
        )
        res = paired_eval(rnd, labels, inc_labels, screen_ids, args.n_boot_screen)
        screened.append({**c, "screen": res})
        print(
            f"    screen kappa {res['point_b']} -> {res['point_a']} (diff {res['point']}, n={res['n_paired']})"
        )
    if args.limit:
        _write_json(round_dir / "summary_smoke.json", {"limit": args.limit, "screened": screened})
        print("smoke run (--limit) — stopping before full phase")
        return

    survivors = sorted(
        [c for c in screened if (c["screen"]["point"] or 0) > 0],
        key=lambda c: -(c["screen"]["point"] or 0),
    )[: args.survivors]
    print(f"survivors: {[c['id'] for c in survivors]}")

    # ---- full ----
    finals = []
    for c in survivors:
        rub = apply_edits(incumbent, c["edits"], rnd.labels)
        print(f"  full-slice {c['id']}")
        labels = run_candidate(
            rnd, rub, rnd.eval_items, round_dir / f"cand_{c['id']}" / "responses.jsonl",
            client, args.concurrency, args.retries,
        )
        res = paired_eval(rnd, labels, inc_labels, rnd.eval_ids, args.n_boot_full)
        guard_ok = (res["unparsed_rate_candidate"] or 0) <= (res["unparsed_rate_incumbent"] or 0) + 0.01
        accepted_eligible = bool(res["significant"]) and (res["point"] or 0) > 0 and guard_ok
        finals.append({**c, "full": res, "unparsed_guard_ok": guard_ok, "accept_eligible": accepted_eligible, "labels": labels})
        print(
            f"    full kappa {res['point_b']} -> {res['point_a']} "
            f"(diff {res['point']} [{res['ci_low']}, {res['ci_high']}] sig={res['significant']}, n={res['n_paired']})"
        )

    winner = max(
        (c for c in finals if c["accept_eligible"]), key=lambda c: c["full"]["point"], default=None
    )
    ledger_path = state_dir / "ledger.jsonl"
    with ledger_path.open("a", encoding="utf-8") as fh:
        for c in screened:
            final = next((f for f in finals if f["id"] == c["id"]), None)
            fh.write(json.dumps({
                "round": args.round,
                "id": c["id"],
                "note": c["note"],
                "edits": c["edits"],
                "prompt_sha256": c.get("prompt_sha256"),
                "judge_model": JUDGE_MODEL,
                "reflect_model": REFLECT_MODEL,
                "screen": c["screen"],
                "full": (final or {}).get("full"),
                "accepted": bool(winner and winner["id"] == c["id"]),
            }, ensure_ascii=False) + "\n")

    if winner:
        new_rubric = apply_edits(incumbent, winner["edits"], rnd.labels)
        new_rubric["version"] = f"stage1-r{args.round}-{winner['id']}"
        new_rubric["history"] = history + [
            {"round": args.round, "id": winner["id"], "edits": winner["edits"]}
        ]
        _write_json(state_dir / "rubric_current.json", new_rubric)
        with (state_dir / "incumbent_responses.jsonl").open("w", encoding="utf-8") as fh:
            for iid in sorted(winner["labels"]):
                fh.write(json.dumps({"item_id": iid, "label": winner["labels"][iid]}, ensure_ascii=False) + "\n")

    _write_json(round_dir / "summary.json", {
        "stage": "stage1 evolution round",
        "plan": "doc/rubric_evolution_plan_2026-07-06.md",
        "benchmark": args.benchmark,
        "dimension": args.dimension,
        "round": args.round,
        "judge_model": JUDGE_MODEL,
        "reflect_model": REFLECT_MODEL,
        "incumbent_version": incumbent["version"],
        "big_screen": args.big_screen,
        "rediagnose": args.rediagnose,
        "no_diagnosis": args.no_diagnosis,
        "proposal_seed": args.proposal_seed or None,
        "remap_stacked": remap_stacked,
        "regression": regression,
        "candidates": [{k: v for k, v in c.items() if k != "labels"} for c in screened],
        "finals": [{k: v for k, v in c.items() if k != "labels"} for c in finals],
        "winner": winner["id"] if winner else None,
        "new_version": f"stage1-r{args.round}-{winner['id']}" if winner else None,
    })
    print(
        f"\nround {args.round} result: winner={winner['id'] if winner else 'none (incumbent stands)'}"
        + (f" diff {winner['full']['point']} [{winner['full']['ci_low']}, {winner['full']['ci_high']}]" if winner else "")
    )
    print(f"wrote {round_dir / 'summary.json'}")


if __name__ == "__main__":
    main()
