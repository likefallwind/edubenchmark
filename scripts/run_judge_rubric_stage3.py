#!/usr/bin/env python3
"""Stage 3 final validation of an accepted rubric on the sealed TEST split.

Every earlier stage (0/1/2 + ablation) selected and confirmed rubrics on the
dev split only; the test split's human labels were frozen and never read
(protocol rule §4.1). Stage 3 is the FIRST and ONLY time an accepted rubric
touches test: run the incumbent v1 prompt and the evolved rubric on the same
test slice, score each against the human gold, and report the cluster-bootstrap
paired diff CI. A significant positive diff here (not just on dev) is what the
production judge switch / ``JUDGE_PROMPT_VERSION=v2`` bump is gated on.

The judge model + which line's evolved rubric is validated are both taken from
the environment exactly like the stage1 runner: STAGE1_JUDGE_MODEL selects the
judge and (via OUT_BASE) which state dir holds the ``rubric_current.json`` under
test. So::

    STAGE1_JUDGE_MODEL=glm-5.2   python scripts/run_judge_rubric_stage3.py --benchmark mrbench  --dimension Providing_Guidance
    STAGE1_JUDGE_MODEL=glm-5.2   python scripts/run_judge_rubric_stage3.py --benchmark mrbench  --dimension Coherence
    STAGE1_JUDGE_MODEL=glm-5.2   python scripts/run_judge_rubric_stage3.py --benchmark bea2025  --dimension Providing_Guidance
    STAGE1_JUDGE_MODEL=MiniMax-M3 python scripts/run_judge_rubric_stage3.py --benchmark mrbench --dimension Providing_Guidance

validates the three glm-5.2 lines (and the M3 pilot line) respectively. Output
goes to ``OUT_BASE/<benchmark>__<dimension>/stage3/``. Resumable: v1 and evolved
responses are cached per item like everywhere else.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from eval.base import prompt_sha256
from eval.providers import build_client
from eval.stats import kappa_stat
from run_judge_rubric_stage1 import (
    JUDGE_MODEL,
    OUT_BASE,
    Renderer,
    _write_json,
    empty_rubric,
    paired_eval,
    run_candidate,
)
from run_judge_rubric_variants import load_items


def _kappa_vs_human(labels: dict[str, str], items: list[dict[str, Any]]) -> float | None:
    pairs = [
        (it["human_label"], labels[it["native_item_id"]])
        for it in items
        if it["native_item_id"] in labels
    ]
    return kappa_stat(pairs)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--benchmark", required=True)
    parser.add_argument("--dimension", required=True)
    parser.add_argument("--concurrency", type=int, default=6)
    parser.add_argument("--retries", type=int, default=4)
    parser.add_argument("--n-boot", type=int, default=1000)
    args = parser.parse_args()

    benchmark, dim = args.benchmark, args.dimension
    rnd = Renderer(benchmark, dim)  # dev-derived render machinery + full contexts
    state_dir = OUT_BASE / f"{benchmark}__{dim}"
    rubric_path = state_dir / "rubric_current.json"
    evolved = json.loads(rubric_path.read_text(encoding="utf-8"))
    v1 = empty_rubric(benchmark, dim)

    # TEST slice: same benchmark/dimension, split == test. Sealed until now.
    all_items, _ = load_items(benchmark)
    test_items = [
        it for it in all_items if str(it["dimension"]) == dim and it["split"] == "test"
    ]
    assert test_items, "no test items for this line"
    assert all(it.get("human_label") for it in test_items), "test items missing human gold"
    test_ids = {it["native_item_id"] for it in test_items}
    # Leakage guards: test never overlaps any dev slice the search ever saw.
    assert not (test_ids & rnd.eval_ids), "test overlaps the dev eval slice"
    pool_ids = {it["native_item_id"] for it in rnd.pool}
    assert not (test_ids & pool_ids), "test overlaps the dev diagnosis/anchor pool"
    assert not any(it["conversation_id"] in {p["conversation_id"] for p in rnd.pool} for it in test_items), \
        "test conversation overlaps a dev pool conversation"

    out_dir = state_dir / "stage3"
    client = build_client(JUDGE_MODEL)
    n_convs = len({it["conversation_id"] for it in test_items})
    print(
        f"stage3 {benchmark}/{dim}: judge={JUDGE_MODEL} evolved={evolved['version']} "
        f"test_items={len(test_items)} test_convs={n_convs}"
    )

    # Incumbent v1 on test (byte-identical to the adapter's shipped prompt).
    v1_labels = run_candidate(
        rnd, v1, test_items, out_dir / "v1" / "responses.jsonl",
        client, args.concurrency, args.retries,
    )
    # Evolved rubric on test.
    cand_labels = run_candidate(
        rnd, evolved, test_items, out_dir / f"{evolved['version']}" / "responses.jsonl",
        client, args.concurrency, args.retries,
    )

    res = paired_eval(rnd, cand_labels, v1_labels, test_ids, args.n_boot, items=test_items)
    summary = {
        "stage": "stage3 test-split final validation",
        "plan": "doc/rubric_evolution_plan_2026-07-06.md §Stage 3",
        "benchmark": benchmark,
        "dimension": dim,
        "judge_model": JUDGE_MODEL,
        "evolved_version": evolved["version"],
        "v1_prompt_sha256": prompt_sha256(rnd.render_template(v1)),
        "evolved_prompt_sha256": prompt_sha256(rnd.render_template(evolved)),
        "n_test_items": len(test_items),
        "n_test_conversations": len({it["conversation_id"] for it in test_items}),
        "kappa_v1_test": _kappa_vs_human(v1_labels, test_items),
        "kappa_evolved_test": _kappa_vs_human(cand_labels, test_items),
        "paired_vs_v1": res,
    }
    _write_json(out_dir / "summary.json", summary)
    print(
        f"stage3 result: v1 {res['point_b']} -> evolved {res['point_a']} "
        f"(diff {res['point']} [{res['ci_low']}, {res['ci_high']}] "
        f"sig={res['significant']}, n={res['n_paired']})"
    )
    print(f"wrote {out_dir / 'summary.json'}")


if __name__ == "__main__":
    main()
