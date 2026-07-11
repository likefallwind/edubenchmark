#!/usr/bin/env python3
"""Build the fixed, difficulty-stratified item list for the P08 calibration run.

Rationale (see ``doc/p08_calibration_eval_plan_2026-07-11.md`` §1.2): random
sampling wastes the calibration signal because most items are answered correctly
by every model (ceval ~81% all-correct, problem_solving ~94%). We therefore
stratify by **ensemble difficulty** computed from the per-item correctness that
already exists in ``reports/eval/<bench>/<model>/scored.jsonl``:

  * easy   = 0 models wrong          (calibration needs a high-confidence /
                                       correct control band)
  * mixed  = 1..k-1 models wrong     (highest-information layer: models disagree)
  * hard   = all k models wrong      (pushes the hard region; also a bad-gold
                                       suspect zone flagged for spot check)

**Fairness**: difficulty comes from the *ensemble* of past model runs, never from
the model under test's own errors, and every model then runs the exact same fixed
list via ``--item-list``. This keeps cross-model comparison clean.

Output composite item ids are namespaced ``<source>::<native_item_id>`` so the
``p08_calibration`` composite adapter can route each item back to its delegate.

Idempotent: fixed seed, writes ``item_list_v1.txt`` + ``item_list_v1_manifest.json``.
"""

from __future__ import annotations

import argparse
import json
import random
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
EVAL_DIR = ROOT / "reports" / "eval"
OUT_DIR = ROOT / "data" / "p08_calibration"

# Runs with fewer than this many scored rows are smoke tests, not full runs;
# their spotty coverage would distort the ensemble difficulty estimate.
MIN_RUN_SIZE = 100
# An item needs correctness from at least this many models for its difficulty to
# be trustworthy (k>=3 so "all wrong" is not a single-model fluke).
MIN_MODELS_PER_ITEM = 3

# source name -> (report dir under reports/eval, quota, per-item language).
# ``lang="item"`` means the language is read per-item from the source's own meta
# (agieval mixes zh/en); a fixed string applies to the whole source.
SOURCES: dict[str, dict[str, Any]] = {
    "ceval": {"report_dir": "ceval", "quota": 200, "lang": "zh"},
    "mmlu_pro": {"report_dir": "mmlu_pro", "quota": 150, "lang": "en"},
    "agieval": {"report_dir": "agieval", "quota": 100, "lang": "item"},
    "mtb_problem_solving": {"report_dir": "mathtutorbench_problem_solving", "quota": 100, "lang": "en"},
    # olympiadbench is optional (needs the antlr venv for scoring); off by default.
}

# Target share of each difficulty layer within a source's quota. Overflow from a
# short layer cascades mixed -> easy so total quota is still met.
LAYER_RATIO = {"easy": 0.30, "mixed": 0.50, "hard": 0.20}


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _last_by_item(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Dedup scored rows by item_id, last row wins (matches runner semantics)."""
    idx: dict[str, dict[str, Any]] = {}
    for r in rows:
        iid = r.get("item_id")
        if iid is not None:
            idx[str(iid)] = r
    return idx


def collect_difficulty(report_dir: str) -> tuple[dict[str, dict[str, Any]], list[str]]:
    """Scan every full scored.jsonl for one benchmark; return per-item ensemble
    difficulty plus the list of contributing run paths (for the manifest)."""
    bench_dir = EVAL_DIR / report_dir
    n_wrong: dict[str, int] = defaultdict(int)
    n_models: dict[str, int] = defaultdict(int)
    # keep one representative bucket set per item for within-layer coverage spread
    bucket_of: dict[str, str] = {}
    used_runs: list[str] = []
    if not bench_dir.exists():
        return {}, used_runs
    for scored in sorted(bench_dir.glob("*/scored.jsonl")):
        rows = _read_jsonl(scored)
        graded = [r for r in _last_by_item(rows).values() if "correct" in r and r.get("score_status") == "scored"]
        if len(graded) < MIN_RUN_SIZE:
            continue
        used_runs.append(str(scored.relative_to(ROOT)))
        for r in graded:
            iid = str(r["item_id"])
            n_models[iid] += 1
            if not r.get("correct"):
                n_wrong[iid] += 1
            if iid not in bucket_of:
                b = r.get("buckets") or {}
                # prefer a coarse subject/category/task key for coverage spread
                key = b.get("category") or b.get("subject") or b.get("task") or "_"
                bucket_of[iid] = str(key)
    difficulty: dict[str, dict[str, Any]] = {}
    for iid, k in n_models.items():
        if k < MIN_MODELS_PER_ITEM:
            continue
        wrong = n_wrong[iid]
        if wrong == 0:
            layer = "easy"
        elif wrong >= k:
            layer = "hard"
        else:
            layer = "mixed"
        difficulty[iid] = {
            "n_models": k,
            "n_wrong": wrong,
            "difficulty": round(wrong / k, 3),
            "layer": layer,
            "bucket": bucket_of.get(iid, "_"),
        }
    return difficulty, used_runs


def _round_robin_by_bucket(items: list[str], meta: dict[str, dict[str, Any]], rng: random.Random) -> list[str]:
    """Order items so consecutive picks spread across buckets (subject coverage)."""
    by_bucket: dict[str, list[str]] = defaultdict(list)
    for iid in items:
        by_bucket[meta[iid]["bucket"]].append(iid)
    for lst in by_bucket.values():
        rng.shuffle(lst)
    buckets = sorted(by_bucket)
    rng.shuffle(buckets)
    ordered: list[str] = []
    while any(by_bucket[b] for b in buckets):
        for b in buckets:
            if by_bucket[b]:
                ordered.append(by_bucket[b].pop())
    return ordered


def sample_source(source: str, quota: int, difficulty: dict[str, dict[str, Any]], rng: random.Random) -> list[str]:
    """Stratified sample of native item ids for one source, cascading overflow."""
    by_layer: dict[str, list[str]] = {"easy": [], "mixed": [], "hard": []}
    for iid, d in difficulty.items():
        by_layer[d["layer"]].append(iid)
    targets = {layer: int(round(quota * ratio)) for layer, ratio in LAYER_RATIO.items()}

    picked: list[str] = []
    leftover_pool: list[str] = []
    # Pull hard and mixed first (scarce, high value), then easy; cascade shortfall.
    for layer in ("hard", "mixed", "easy"):
        pool = _round_robin_by_bucket(by_layer[layer], difficulty, rng)
        want = targets[layer]
        take = pool[:want]
        picked.extend(take)
        leftover_pool.extend(pool[want:])
    # Top up to quota from whatever is left (prefer harder leftovers first).
    if len(picked) < quota:
        leftover_pool.sort(key=lambda iid: difficulty[iid]["difficulty"], reverse=True)
        for iid in leftover_pool:
            if len(picked) >= quota:
                break
            picked.append(iid)
    return picked[:quota]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--seed", type=int, default=20260711)
    parser.add_argument("--out", type=Path, default=OUT_DIR / "item_list_v1.txt")
    parser.add_argument(
        "--source",
        action="append",
        default=None,
        help="restrict to specific source(s); default = all configured sources",
    )
    args = parser.parse_args()

    rng = random.Random(args.seed)
    wanted = set(args.source) if args.source else set(SOURCES)

    composite_ids: list[str] = []
    manifest: dict[str, Any] = {
        "generated": date.today().isoformat(),
        "seed": args.seed,
        "layer_ratio": LAYER_RATIO,
        "min_run_size": MIN_RUN_SIZE,
        "min_models_per_item": MIN_MODELS_PER_ITEM,
        "sources": {},
    }
    per_id_layer: dict[str, dict[str, Any]] = {}

    for source, cfg in SOURCES.items():
        if source not in wanted:
            continue
        difficulty, used_runs = collect_difficulty(cfg["report_dir"])
        if not difficulty:
            print(f"!! {source}: no full scored.jsonl runs found under reports/eval/{cfg['report_dir']}; skipping")
            manifest["sources"][source] = {"quota": cfg["quota"], "available": 0, "used_runs": used_runs}
            continue
        picked = sample_source(source, cfg["quota"], difficulty, rng)
        layer_counts: dict[str, int] = defaultdict(int)
        for iid in picked:
            layer_counts[difficulty[iid]["layer"]] += 1
            cid = f"{source}::{iid}"
            composite_ids.append(cid)
            per_id_layer[cid] = {
                "source": source,
                "native_id": iid,
                **difficulty[iid],
            }
        manifest["sources"][source] = {
            "quota": cfg["quota"],
            "report_dir": cfg["report_dir"],
            "available": len(difficulty),
            "available_by_layer": {
                layer: sum(1 for d in difficulty.values() if d["layer"] == layer)
                for layer in ("easy", "mixed", "hard")
            },
            "sampled": len(picked),
            "sampled_by_layer": dict(layer_counts),
            "used_runs": used_runs,
        }
        print(
            f"{source}: sampled {len(picked)}/{cfg['quota']} "
            f"(easy={layer_counts['easy']} mixed={layer_counts['mixed']} hard={layer_counts['hard']}) "
            f"from {len(difficulty)} graded items across {len(used_runs)} runs"
        )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(composite_ids) + "\n", encoding="utf-8")
    manifest["total_items"] = len(composite_ids)
    manifest_path = args.out.with_name(args.out.stem + "_manifest.json")
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    # Per-item layer map lets the report/analysis recover difficulty without
    # re-scanning every scored.jsonl.
    layer_path = args.out.with_name(args.out.stem + "_layers.json")
    layer_path.write_text(json.dumps(per_id_layer, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"\nwrote {len(composite_ids)} composite ids -> {args.out}")
    print(f"manifest -> {manifest_path}")
    print(f"layer map -> {layer_path}")


if __name__ == "__main__":
    main()
