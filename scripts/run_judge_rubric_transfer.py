#!/usr/bin/env python3
"""Cross-judge rubric transfer matrix (judge research report §9.4 #1).

Question: the three self-evolution arms (glm-5.2 / MiniMax-M3 / deepseek-v4-pro)
each accepted a rubric edit on mrbench/Providing_Guidance, and the three
prescriptions converged on the same confusion cell. Does that mean they fixed a
gap in the TASK's rubric (so one judge's edit helps another judge), or three
judge-specific quirks that merely look alike?

Design: 3 rubrics x 3 judges on one shared item set.
- Item set: the mrbench/PG diagnosis-pool subsample (~605 items), disjoint from
  the eval slice that SELECTED every one of these rubrics, minus the union of
  error examples any arm's reflection model ever saw. So no cell is scored on
  data that picked its rubric.
- Incumbent per judge: that judge's v1 (empty-rubric) labels from its cached
  baseline run — zero extra calls, and the natural per-judge control.
- Each cell reports the judge's kappa under the rubric and the paired
  cluster-bootstrap CI of (rubric - v1) for that judge.

Reading the matrix: the DIAGONAL is each arm's own (already known, selected)
gain, re-measured on held-out pool items. The OFF-DIAGONAL is the claim under
test — positive off-diagonal cells mean the edit transfers, i.e. it repairs a
task-level rubric gap rather than one model's private quirk.

Usage:
    python3 run_judge_rubric_transfer.py --concurrency 6
    python3 run_judge_rubric_transfer.py --judges glm-5.2 --limit 20   # smoke
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import run_judge_rubric_stage1 as st
from eval.base import prompt_sha256
from eval.providers import build_client
from build_judge_stage1_assets import stage1_out_base
from run_judge_rubric_stage1 import (
    ROOT,
    Renderer,
    _read_jsonl,
    _write_json,
    cached_v1_pool_data,
    empty_rubric,
    paired_eval,
    pool_subsample,
    run_candidate,
)

BENCHMARK, DIMENSION = "mrbench", "Providing_Guidance"
OUT_DIR = ROOT / "reports" / "eval" / "_judge_rubric" / "transfer_matrix"

# Rubric sources: the accepted PG rubric of each self-evolution arm, with the
# state dir it lives in and the diagnosis files whose error examples its
# reflection model saw (excluded from the item set, for every arm).
ARMS: dict[str, dict[str, Any]] = {
    "glm": {
        "state_slug": "glm-5.2",
        "judge": "glm-5.2",
        "diagnosis_files": [
            "diagnosis.json", "round1/diagnosis_used.json",
            "round2/diagnosis_used.json", "round3/diagnosis_used.json",
        ],
    },
    "m3self": {
        "state_slug": "minimax3_self",
        "judge": "MiniMax-M3",
        "diagnosis_files": [
            "diagnosis.json", "round1/diagnosis_used.json", "round2/diagnosis_used.json",
        ],
    },
    # P5 ablation arm (--no-diagnosis): its reflection model saw NO error
    # examples at all, so it contributes no exclusions. Included here to compare
    # the diagnosis-driven rubric against the diagnosis-free one on data that
    # selected neither.
    "glm_nodiag": {
        "state_slug": "glm-5.2_nodiag",
        "judge": "glm-5.2",
        "diagnosis_files": [],
    },
    "dsv4": {
        "state_slug": "deepseek-v4-pro",
        "judge": "deepseek-v4-pro",
        "diagnosis_files": [
            "diagnosis.json", "round1/diagnosis_used.json",
            "round2/diagnosis_used.json", "round3/diagnosis_used.json",
        ],
    },
}
JUDGES = ["glm-5.2", "MiniMax-M3", "deepseek-v4-pro"]
JUDGE_DIR_SLUG = {"glm-5.2": "glm-5.2", "MiniMax-M3": "minimax3", "deepseek-v4-pro": "deepseek-v4-pro"}


def state_dir(arm: str) -> Path:
    return stage1_out_base(ARMS[arm]["state_slug"]) / f"{BENCHMARK}__{DIMENSION}"


def seen_example_ids() -> set[str]:
    """Every pool item any arm's reflection model was shown as an error example."""
    ids: set[str] = set()
    for arm, spec in ARMS.items():
        for rel in spec["diagnosis_files"]:
            path = state_dir(arm) / rel
            if not path.exists():
                continue
            d = json.loads(path.read_text(encoding="utf-8"))
            for cell in d["error_examples_by_cell"].values():
                ids.update(e["item_id"] for e in cell)
    return ids


def seed_diagonal_cache(arm: str, rubric: dict[str, Any], cell_resp: Path) -> int:
    """The arm's own run of its own rubric over the same pool subsample is
    already cached under pool_<version>/ — reuse it instead of re-judging."""
    src = state_dir(arm) / f"pool_{rubric['version']}" / "responses.jsonl"
    if not src.exists() or cell_resp.exists():
        return 0
    rows = [r for r in _read_jsonl(src) if str(r.get("response") or "").strip()]
    if not rows:
        return 0
    cell_resp.parent.mkdir(parents=True, exist_ok=True)
    with cell_resp.open("w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    return len(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--judges", default=",".join(JUDGES), help="comma-separated judge models")
    parser.add_argument("--rubrics", default=",".join(ARMS), help="comma-separated arm keys")
    parser.add_argument("--limit", type=int, default=0, help="cap items (smoke tests only)")
    parser.add_argument("--concurrency", type=int, default=6)
    parser.add_argument("--retries", type=int, default=4)
    parser.add_argument("--n-boot", type=int, default=1000)
    args = parser.parse_args()

    judges = [j.strip() for j in args.judges.split(",") if j.strip()]
    arms = [a.strip() for a in args.rubrics.split(",") if a.strip()]
    rnd = Renderer(BENCHMARK, DIMENSION)

    excluded = seen_example_ids()
    items = [it for it in pool_subsample(rnd) if it["native_item_id"] not in excluded]
    if args.limit:
        items = items[: args.limit]
    ids = {it["native_item_id"] for it in items}
    assert not ids & rnd.eval_ids, "item set overlaps the selection slice"
    print(f"items={len(items)} (excluded {len(excluded)} reflection-seen examples)")

    rubrics = {
        arm: json.loads((state_dir(arm) / "rubric_current.json").read_text(encoding="utf-8"))
        for arm in arms
    }
    rubrics["v1"] = empty_rubric(BENCHMARK, DIMENSION)
    for arm in arms:
        print(f"  rubric[{arm}] = {rubrics[arm]['version']} (from {ARMS[arm]['judge']}'s arm)")

    cells: list[dict[str, Any]] = []
    for judge in judges:
        # run_candidate / cached_v1_pool_data read the module-level JUDGE_MODEL
        # at call time, so rebinding it retargets the judge for this loop.
        st.JUDGE_MODEL = judge
        client = build_client(judge)
        v1_labels, _ = cached_v1_pool_data(BENCHMARK, ids)
        if len(v1_labels) < 0.9 * len(ids):
            raise SystemExit(f"{judge}: only {len(v1_labels)}/{len(ids)} cached v1 pool labels")
        for arm in arms:
            rubric = rubrics[arm]
            cell_dir = OUT_DIR / f"{JUDGE_DIR_SLUG[judge]}__{arm}"
            resp = cell_dir / "responses.jsonl"
            own = ARMS[arm]["judge"] == judge
            if own:
                seeded = seed_diagonal_cache(arm, rubric, resp)
                if seeded:
                    print(f"  [{judge} x {arm}] seeded {seeded} cached rows from the arm's own pool run")
            print(f"[{judge} x {arm}] {'(own rubric)' if own else 'TRANSFER'} judging {len(items)} items")
            labels = run_candidate(rnd, rubric, items, resp, client, args.concurrency, args.retries)
            res = paired_eval(rnd, labels, v1_labels, ids, args.n_boot, items=items)
            cells.append({
                "judge": judge,
                "rubric_arm": arm,
                "rubric_version": rubric["version"],
                "own_rubric": own,
                "prompt_sha256": prompt_sha256(rnd.render_template(rubric)),
                "kappa_v1": res["point_b"],
                "kappa_rubric": res["point_a"],
                "diff": res["point"],
                "ci_low": res["ci_low"],
                "ci_high": res["ci_high"],
                "significant": res["significant"],
                "n_paired": res["n_paired"],
                "unparsed_rate": res["unparsed_rate_candidate"],
            })
            c = cells[-1]
            print(
                f"  -> v1 {c['kappa_v1']} -> {c['kappa_rubric']} "
                f"(diff {c['diff']} [{c['ci_low']}, {c['ci_high']}] sig={c['significant']}, n={c['n_paired']})"
            )
            _write_json(OUT_DIR / "summary.json", {
                "experiment": "cross-judge rubric transfer matrix (report §9.4 #1)",
                "benchmark": BENCHMARK,
                "dimension": DIMENSION,
                "item_set": "mrbench/PG diagnosis-pool subsample minus all reflection-seen error examples",
                "n_items": len(items),
                "n_excluded_examples": len(excluded),
                "judges": judges,
                "rubric_arms": {a: rubrics[a]["version"] for a in arms},
                "cells": cells,
            })

    print("\n=== transfer matrix (paired diff vs each judge's own v1) ===")
    header = f"{'judge':<18}" + "".join(f"{a:>22}" for a in arms)
    print(header)
    for judge in judges:
        row = f"{judge:<18}"
        for arm in arms:
            c = next((x for x in cells if x["judge"] == judge and x["rubric_arm"] == arm), None)
            if c is None:
                row += f"{'-':>22}"
                continue
            mark = "*" if c["significant"] else " "
            tag = "own" if c["own_rubric"] else "xfer"
            row += f"{c['diff']:>+12.4f}{mark} {tag:>7}"
        print(row)
    print(f"\nwrote {OUT_DIR / 'summary.json'}")


if __name__ == "__main__":
    main()
