#!/usr/bin/env python3
"""Independent confirmation of near-miss rubric candidates on held-out pool data.

A candidate that repeatedly lands just short of significance on the frozen eval
slice (which SELECTED it) gets one confirmation test on diagnosis-pool items the
selection never touched — selection data and confirmation data are disjoint, so
this is a clean second look, not a re-roll of the same dice. Items whose human
labels were exposed to the reflection model (diagnosis error examples) are
excluded.

Confirmations are declared in CONFIRMS; each runs the candidate rubric on the
confirmation items (resumable), pairs it against the incumbent's labels there
(cached where possible), and reports the cluster-bootstrap paired diff CI.

Usage:
    python scripts/run_judge_rubric_confirm.py --confirm mrbench_pg_r2p3
    python scripts/run_judge_rubric_confirm.py --confirm bea2025_pg_r3p5 --concurrency 5
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from eval.base import prompt_sha256
from eval.providers import build_client
from run_judge_rubric_stage1 import (
    JUDGE_MODEL,
    OUT_BASE,
    Renderer,
    _read_jsonl,
    _write_json,
    apply_edits,
    cached_v1_pool_data,
    empty_rubric,
    paired_eval,
    pool_subsample,
    run_candidate,
)

# incumbent "current" = rubric_current.json (its pool labels come from the
# adaptive-rediagnosis run); incumbent "v1" = cached full run, zero extra calls.
CONFIRMS: dict[str, dict[str, Any]] = {
    "mrbench_pg_r2p3": {
        "benchmark": "mrbench",
        "dimension": "Providing_Guidance",
        "candidate_round": 2,
        "candidate_id": "r2p3",
        "incumbent": "current",
        # r2p3 was proposed from the static v1 diagnosis; its confirmation set is
        # the rediagnosis pool subsample (incumbent labels cached) minus those
        # reflection-seen examples.
        "conf_source": "rediag_subsample",
        "exclude_example_files": ["diagnosis.json"],
    },
    "bea2025_pg_r3p5": {
        "benchmark": "bea2025",
        "dimension": "Providing_Guidance",
        "candidate_round": 3,
        "candidate_id": "r3p5",
        "incumbent": "v1",
        # r3p5 was proposed from the round-3 rediagnosis subsample; confirm on
        # the pool REMAINDER (fully disjoint), minus every example ever shown.
        "conf_source": "pool_remainder",
        "exclude_example_files": ["diagnosis.json", "round3/diagnosis_used.json"],
    },
}


def example_ids(state_dir: Path, rel_paths: list[str]) -> set[str]:
    ids: set[str] = set()
    for rel in rel_paths:
        d = json.loads((state_dir / rel).read_text(encoding="utf-8"))
        for cell in d["error_examples_by_cell"].values():
            ids.update(e["item_id"] for e in cell)
    return ids


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--confirm", required=True, choices=sorted(CONFIRMS))
    parser.add_argument("--concurrency", type=int, default=5)
    parser.add_argument("--retries", type=int, default=4)
    parser.add_argument("--n-boot", type=int, default=1000)
    args = parser.parse_args()

    spec = CONFIRMS[args.confirm]
    rnd = Renderer(spec["benchmark"], spec["dimension"])
    state_dir = OUT_BASE / f"{spec['benchmark']}__{spec['dimension']}"
    ledger = _read_jsonl(state_dir / "ledger.jsonl")
    cand_row = next(
        r for r in ledger if r["id"] == spec["candidate_id"] and r["round"] == spec["candidate_round"]
    )
    excluded = example_ids(state_dir, spec["exclude_example_files"])

    sub = pool_subsample(rnd)
    sub_ids = {it["native_item_id"] for it in sub}
    client = build_client(JUDGE_MODEL)
    if spec["incumbent"] == "current":
        base = json.loads((state_dir / "rubric_current.json").read_text(encoding="utf-8"))
        assert spec["conf_source"] == "rediag_subsample"
        conf_items = [it for it in sub if it["native_item_id"] not in excluded]
        inc_labels = run_candidate(
            rnd, base, conf_items, state_dir / f"pool_{base['version']}" / "responses.jsonl",
            client, args.concurrency, args.retries,
        )
    else:
        base = empty_rubric(spec["benchmark"], spec["dimension"])
        assert spec["conf_source"] == "pool_remainder"
        conf_items = [
            it for it in rnd.pool
            if it["native_item_id"] not in sub_ids and it["native_item_id"] not in excluded
        ]
        inc_labels, _ = cached_v1_pool_data(
            spec["benchmark"], {it["native_item_id"] for it in conf_items}
        )
    conf_ids = {it["native_item_id"] for it in conf_items}
    assert not conf_ids & rnd.eval_ids, "confirmation set overlaps the selection slice"

    rubric = apply_edits(base, cand_row["edits"], rnd.labels)
    out_dir = state_dir / f"confirm_{spec['candidate_id']}"
    print(
        f"{args.confirm}: base={base['version']} candidate={spec['candidate_id']} "
        f"conf_items={len(conf_items)} excluded_examples={len(excluded & (sub_ids | conf_ids))}"
    )
    cand_labels = run_candidate(
        rnd, rubric, conf_items, out_dir / "responses.jsonl", client, args.concurrency, args.retries
    )
    res = paired_eval(rnd, cand_labels, inc_labels, conf_ids, args.n_boot, items=conf_items)

    summary = {
        "stage": "stage2 independent confirmation",
        "plan": "doc/rubric_evolution_plan_2026-07-06.md",
        "confirm": args.confirm,
        "judge_model": JUDGE_MODEL,
        "base_version": base["version"],
        "candidate": {k: cand_row[k] for k in ("round", "id", "note", "edits")},
        "selection_result_on_eval_slice": cand_row.get("full"),
        "confirmation_prompt_sha256": prompt_sha256(rnd.render_template(rubric)),
        "n_confirmation_items": len(conf_items),
        "excluded_reflection_examples": sorted(excluded),
        "confirmation": res,
    }
    _write_json(out_dir / "summary.json", summary)
    print(
        f"confirmation: incumbent {res['point_b']} -> candidate {res['point_a']} "
        f"(diff {res['point']} [{res['ci_low']}, {res['ci_high']}] sig={res['significant']}, n={res['n_paired']})"
    )
    print(f"wrote {out_dir / 'summary.json'}")


if __name__ == "__main__":
    main()
