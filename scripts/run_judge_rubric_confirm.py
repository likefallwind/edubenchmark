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
    # glm-5.2 experiment (STAGE1_JUDGE_MODEL=glm-5.2 — OUT_BASE resolves to
    # stage1_glm-5.2/): mrbench PG borderline near-miss at line closure. The
    # incumbent r1p2's subsample labels are cached from rediagnosis; round-2 and
    # round-3 diagnoses share the same subsample + incumbent, so their example
    # sets are excluded together.
    "glm_mrbench_pg_r3p3": {
        "benchmark": "mrbench",
        "dimension": "Providing_Guidance",
        "candidate_round": 3,
        "candidate_id": "r3p3",
        "incumbent": "current",
        "conf_source": "rediag_subsample",
        "exclude_example_files": [
            "diagnosis.json", "round2/diagnosis_used.json", "round3/diagnosis_used.json",
        ],
    },
    # Pure-M3 self-evolution arm (STAGE1_JUDGE_MODEL=MiniMax-M3,
    # STAGE1_OUT_SLUG=minimax3_self): Coherence closed round 2 with r2p3 at
    # +0.058 [-0.011, 0.132] — inside the near-miss band set by the glm r2p5
    # precedent (-0.016). Incumbent is still v1 (line never accepted), so the
    # confirmation set is the pool remainder and incumbent labels are the
    # cached v1 full run (zero extra calls), like bea2025_pg_r3p5.
    "m3self_mrbench_coh_r2p3": {
        "benchmark": "mrbench",
        "dimension": "Coherence",
        "candidate_round": 2,
        "candidate_id": "r2p3",
        "incumbent": "v1",
        "conf_source": "pool_remainder",
        "exclude_example_files": [
            "diagnosis.json", "round1/diagnosis_used.json", "round2/diagnosis_used.json",
        ],
    },
    # deepseek-v4-pro self-evolution arm (STAGE1_JUDGE_MODEL=deepseek-v4-pro):
    # Coherence closed round 2 with two candidates in the near-miss band,
    # r2p5 +0.042 [-0.006, 0.096] and r2p6 +0.042 [-0.013, 0.096]. Same
    # v1-incumbent pool-remainder setup as above.
    "dsv4_mrbench_coh_r2p5": {
        "benchmark": "mrbench",
        "dimension": "Coherence",
        "candidate_round": 2,
        "candidate_id": "r2p5",
        "incumbent": "v1",
        "conf_source": "pool_remainder",
        "exclude_example_files": [
            "diagnosis.json", "round1/diagnosis_used.json", "round2/diagnosis_used.json",
        ],
    },
    "dsv4_mrbench_coh_r2p6": {
        "benchmark": "mrbench",
        "dimension": "Coherence",
        "candidate_round": 2,
        "candidate_id": "r2p6",
        "incumbent": "v1",
        "conf_source": "pool_remainder",
        "exclude_example_files": [
            "diagnosis.json", "round1/diagnosis_used.json", "round2/diagnosis_used.json",
        ],
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
