#!/usr/bin/env python3
"""Stage 1 offline assets: frozen per-dimension eval slices + judge diagnosis.

Plan: doc/rubric_evolution_plan_2026-07-06.md (Stage 1). Pilot targets are the
calibration-immune dimensions (Stage 0a remap gain = 0 for every judge):
mrbench/Providing_Guidance, mrbench/Coherence, bea2025/Providing_Guidance.

For each (benchmark, dimension) this script freezes, dev-only and
dialogue-grouped (a conversation is never split across pools):

- ``data/judge_meta_eval_v1/stage1_slices/<bench>__<dim>__eval.txt``   the
  judgment slice every candidate rubric is scored on (~600 items);
- ``data/judge_meta_eval_v1/stage1_slices/<bench>__<dim>__screen.txt`` a
  ~150-item screening subset (subset of eval, by conversation) for the
  successive-halving first pass;
- ``reports/eval/_judge_rubric/stage1/<bench>__<dim>/diagnosis.json``
  aggregated diagnosis of the pilot judge's cached v1 run on the DIAGNOSIS
  POOL (dev minus eval-slice conversations, so reflection never sees the
  judgment slice): confusion matrix, label marginals, and per-confusion-cell
  error samples carrying the judge's own reasoning.

Test split is never read for decisions; existing meta-eval files are not
modified (new files only). Idempotent: seeded sampling, byte-stable output.

Usage:
    python scripts/build_judge_stage1_assets.py            # uses cached minimax3 v1 run
    python scripts/build_judge_stage1_assets.py --judge-slug glm-5.2
"""

from __future__ import annotations

import argparse
import json
import random
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from eval.predictions_io import read_predictions

ROOT = Path(__file__).resolve().parents[1]
META_DIR = ROOT / "data" / "judge_meta_eval_v1"
SLICE_DIR = META_DIR / "stage1_slices"


def stage1_out_base(judge_slug: str) -> Path:
    """Judge-keyed state base. The M3 pilot predates judge-keyed dirs and keeps
    its original ``stage1/`` layout; every other judge gets ``stage1_<slug>/``."""
    name = "stage1" if judge_slug == "minimax3" else f"stage1_{judge_slug}"
    return ROOT / "reports" / "eval" / "_judge_rubric" / name

SEED = 20260707
EVAL_TARGET_ITEMS = 600
SCREEN_TARGET_ITEMS = 150
# Stage 2 upgrade: a larger screening slice (same prefix order, so the 150-item
# slice is a subset) — 157-item screens mis-ranked candidates 5 times in the
# pilot (winner's curse), see plan appendix 1.
SCREEN2_TARGET_ITEMS = 250
EXAMPLES_PER_CELL = 8
CONTEXT_TAIL_CHARS = 500
REASONING_TAIL_CHARS = 700

TARGETS = [
    ("mrbench", "Providing_Guidance"),
    ("mrbench", "Coherence"),
    ("bea2025", "Providing_Guidance"),
]
BASELINE_DIRS = {"mrbench": "mrbench_judge", "bea2025": "bea2025_judge"}


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def make_diagnosis(
    pool_items: list[dict[str, Any]],
    labels_by_id: dict[str, str],
    raw_by_id: dict[str, dict[str, Any]],
    contexts: dict[str, str],
    meta: dict[str, Any],
) -> dict[str, Any]:
    """Aggregate judge-vs-human diagnosis over ``pool_items`` (which must all
    have a label in ``labels_by_id``): confusion matrix, marginals, and
    per-confusion-cell error samples carrying the judge's own reasoning.
    Reused by the evolution runner's adaptive re-diagnosis (Stage 2)."""
    confusion: dict[str, Counter] = defaultdict(Counter)
    for it in pool_items:
        confusion[it["human_label"]][labels_by_id[it["native_item_id"]]] += 1

    cells: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for it in sorted(pool_items, key=lambda x: x["native_item_id"]):
        gold, pred = it["human_label"], labels_by_id[it["native_item_id"]]
        if gold == pred:
            continue
        cell = f"human={gold} | judge={pred}"
        if len(cells[cell]) >= EXAMPLES_PER_CELL:
            continue
        row = raw_by_id.get(it["native_item_id"], {})
        cells[cell].append(
            {
                "item_id": it["native_item_id"],
                "conversation_tail": str(contexts.get(it["conversation_id"], ""))[-CONTEXT_TAIL_CHARS:],
                "tutor_reply": it["response"],
                "human_label": gold,
                "judge_label": pred,
                "judge_reasoning": str(row.get("reasoning") or row.get("response") or "")[-REASONING_TAIL_CHARS:],
            }
        )

    n_pool = len(pool_items)
    return {
        **meta,
        "n_pool_items": n_pool,
        "agreement_rate": round(
            sum(confusion[g][g] for g in confusion) / n_pool, 4
        ) if n_pool else None,
        "human_marginals": {
            lab: round(cnt / n_pool, 4)
            for lab, cnt in sorted(Counter(it["human_label"] for it in pool_items).items())
        },
        "judge_marginals": {
            lab: round(cnt / n_pool, 4)
            for lab, cnt in sorted(Counter(labels_by_id[it["native_item_id"]] for it in pool_items).items())
        },
        "confusion_matrix": {g: dict(sorted(c.items())) for g, c in sorted(confusion.items())},
        "error_examples_by_cell": {k: v for k, v in sorted(cells.items())},
    }


def build_target(benchmark: str, dim: str, judge_slug: str, out_slug: str | None = None) -> dict[str, Any]:
    items = [
        r
        for r in _read_jsonl(META_DIR / "items.jsonl")
        if r["source_benchmark"] == benchmark and str(r["dimension"]) == dim and r["split"] == "dev"
    ]
    contexts = {
        r["conversation_id"]: r["context"]
        for r in _read_jsonl(META_DIR / "contexts.jsonl")
        if r["source_benchmark"] == benchmark
    }
    by_conv: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for it in items:
        by_conv[it["conversation_id"]].append(it)

    convs = sorted(by_conv)
    rng = random.Random(f"{SEED}:{benchmark}:{dim}")
    rng.shuffle(convs)

    eval_convs: list[str] = []
    n = 0
    for c in convs:
        if n >= EVAL_TARGET_ITEMS:
            break
        eval_convs.append(c)
        n += len(by_conv[c])
    screen_convs: list[str] = []
    n = 0
    for c in eval_convs:
        if n >= SCREEN_TARGET_ITEMS:
            break
        screen_convs.append(c)
        n += len(by_conv[c])
    screen2_convs: list[str] = []
    n = 0
    for c in eval_convs:
        if n >= SCREEN2_TARGET_ITEMS:
            break
        screen2_convs.append(c)
        n += len(by_conv[c])
    pool_convs = [c for c in convs if c not in set(eval_convs)]
    assert not set(eval_convs) & set(pool_convs), "eval/pool conversation overlap"
    assert set(screen_convs) <= set(eval_convs), "screen must be a subset of eval"

    eval_ids = sorted(it["native_item_id"] for c in eval_convs for it in by_conv[c])
    screen_ids = sorted(it["native_item_id"] for c in screen_convs for it in by_conv[c])
    screen2_ids = sorted(it["native_item_id"] for c in screen2_convs for it in by_conv[c])

    SLICE_DIR.mkdir(parents=True, exist_ok=True)
    stem = f"{benchmark}__{dim}"
    (SLICE_DIR / f"{stem}__eval.txt").write_text("\n".join(eval_ids) + "\n", encoding="utf-8")
    (SLICE_DIR / f"{stem}__screen.txt").write_text("\n".join(screen_ids) + "\n", encoding="utf-8")
    (SLICE_DIR / f"{stem}__screen250.txt").write_text("\n".join(screen2_ids) + "\n", encoding="utf-8")

    # ---- diagnosis on the pool, from the judge's cached v1 full run ----
    run_dir = ROOT / "reports" / "eval" / BASELINE_DIRS[benchmark] / judge_slug
    scored = {
        str(r["item_id"]): str(r["pred_label"])
        for r in _read_jsonl(run_dir / "scored.jsonl")
        if r.get("score_status") == "scored" and "pred_label" in r and str(r.get("dimension")) == dim
    }
    raw = {
        str(r["item_id"]): r
        for r in read_predictions(run_dir)
        if str(r["item_id"]) in scored
    }

    pool_items = [it for c in pool_convs for it in by_conv[c] if it["native_item_id"] in scored]
    diagnosis = make_diagnosis(
        pool_items,
        scored,
        raw,
        contexts,
        {
            "stage": "stage1 diagnosis",
            "plan": "doc/rubric_evolution_plan_2026-07-06.md",
            "benchmark": benchmark,
            "dimension": dim,
            "judge_slug": judge_slug,
            "seed": SEED,
            "pool": "dev minus eval-slice conversations (reflection never sees the judgment slice)",
            "n_pool_conversations": len(pool_convs),
            "n_eval_items": len(eval_ids),
            "n_eval_conversations": len(eval_convs),
            "n_screen_items": len(screen_ids),
        },
    )
    out_dir = stage1_out_base(out_slug or judge_slug) / stem
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "diagnosis.json").write_text(
        json.dumps(diagnosis, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return diagnosis


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--judge-slug", default="minimax3", help="cached v1 run directory name")
    parser.add_argument("--out-slug", default=None,
                        help="state dir slug (default: judge-slug); use to isolate a rerun, e.g. minimax3_full")
    args = parser.parse_args()
    for benchmark, dim in TARGETS:
        d = build_target(benchmark, dim, args.judge_slug, args.out_slug)
        print(
            f"{benchmark}/{dim}: eval={d['n_eval_items']} items/{d['n_eval_conversations']} convs "
            f"screen={d['n_screen_items']} pool={d['n_pool_items']} "
            f"agreement={d['agreement_rate']} judge_marginals={d['judge_marginals']}"
        )


if __name__ == "__main__":
    main()
