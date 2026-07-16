#!/usr/bin/env python3
"""Offline robustness audit for the teaching-judge rubric experiments.

This script never calls a model and never opens the sealed test for selection.
It reuses cached labels to produce:

1. one-sided paired cluster-bootstrap p-values with Holm and BH corrections;
2. conversation-level repeated-fold and leave-one-cluster-out stability audits;
3. a transparent factorial-style evidence table for diagnosis, constrained edits,
   and significance gating;
4. a multi-proposal-seed summary when isolated replication arms exist.

Outputs:
  reports/eval/_judge_rubric/robustness_audit/summary.json
  reports/eval/_judge_rubric/robustness_audit/report.md
"""

from __future__ import annotations

import argparse
import json
import math
import random
from collections import defaultdict
from pathlib import Path
from statistics import median
from typing import Any, Callable

from eval.stats import kappa_stat
from run_judge_rubric_variants import adapter_bits

ROOT = Path(__file__).resolve().parents[1]
META = ROOT / "data" / "judge_meta_eval_v1"
SLICES = META / "stage1_slices"
RUBRIC_ROOT = ROOT / "reports" / "eval" / "_judge_rubric"
OUT_DIR = RUBRIC_ROOT / "robustness_audit"

LINE_SPECS = (
    ("mrbench", "Providing_Guidance"),
    ("mrbench", "Coherence"),
    ("bea2025", "Providing_Guidance"),
)
BASELINE_DIRS = {"mrbench": "mrbench_judge", "bea2025": "bea2025_judge"}
PRIMARY_STATES = (
    ("stage1_glm-5.2", "glm-5.2", "glm_full"),
    ("stage1_glm-5.2_nodiag", "glm-5.2", "glm_nodiag"),
    ("stage1_minimax3_self", "minimax3", "m3_self"),
    ("stage1_deepseek-v4-pro", "deepseek-v4-pro", "dsv4_self"),
)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def quantile(values: list[float], q: float) -> float | None:
    if not values:
        return None
    xs = sorted(values)
    pos = (len(xs) - 1) * q
    lo, hi = math.floor(pos), math.ceil(pos)
    if lo == hi:
        return xs[lo]
    return xs[lo] * (hi - pos) + xs[hi] * (pos - lo)


def rounded(value: float | None) -> float | None:
    return None if value is None else round(value, 4)


def load_items(benchmark: str, dimension: str, split: str) -> dict[str, dict[str, Any]]:
    return {
        str(row["native_item_id"]): row
        for row in read_jsonl(META / "items.jsonl")
        if row["source_benchmark"] == benchmark
        and str(row["dimension"]) == dimension
        and row["split"] == split
    }


def eval_ids(benchmark: str, dimension: str) -> set[str]:
    path = SLICES / f"{benchmark}__{dimension}__eval.txt"
    return set(path.read_text(encoding="utf-8").split())


def normalizer(benchmark: str) -> Callable[[str, str], str]:
    return adapter_bits(benchmark)[2]


def baseline_labels(
    benchmark: str, dimension: str, judge_slug: str, ids: set[str]
) -> dict[str, str]:
    path = ROOT / "reports" / "eval" / BASELINE_DIRS[benchmark] / judge_slug / "scored.jsonl"
    return {
        str(row["item_id"]): str(row["pred_label"])
        for row in read_jsonl(path)
        if row.get("score_status") == "scored"
        and str(row.get("dimension")) == dimension
        and str(row["item_id"]) in ids
        and row.get("pred_label") is not None
    }


def response_labels(
    path: Path, benchmark: str, dimension: str, ids: set[str]
) -> dict[str, str]:
    normalize = normalizer(benchmark)
    labels: dict[str, str] = {}
    for row in read_jsonl(path):
        item_id = str(row.get("item_id"))
        response = str(row.get("response") or "")
        if item_id in ids and response.strip():
            labels[item_id] = normalize(dimension, response)
    return labels


def paired_rows(
    items: dict[str, dict[str, Any]], candidate: dict[str, str], incumbent: dict[str, str]
) -> list[tuple[str, str, str, str]]:
    rows = []
    for item_id, item in items.items():
        if item_id in candidate and item_id in incumbent:
            rows.append(
                (
                    str(item["conversation_id"]),
                    str(item["human_label"]),
                    candidate[item_id],
                    incumbent[item_id],
                )
            )
    return rows


def effect(rows: list[tuple[str, str, str, str]]) -> float | None:
    cand = kappa_stat([(gold, a) for _, gold, a, _ in rows])
    inc = kappa_stat([(gold, b) for _, gold, _, b in rows])
    return None if cand is None or inc is None else cand - inc


def bootstrap_test(
    rows: list[tuple[str, str, str, str]], n_boot: int, seed: int
) -> dict[str, Any]:
    grouped: dict[str, list[tuple[str, str, str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row[0]].append(row)
    clusters = list(grouped.values())
    point = effect(rows)
    rng = random.Random(seed)
    diffs: list[float] = []
    for _ in range(n_boot):
        sample: list[tuple[str, str, str, str]] = []
        for _ in clusters:
            sample.extend(clusters[rng.randrange(len(clusters))])
        value = effect(sample)
        if value is not None:
            diffs.append(value)
    p_one_sided = (1 + sum(value <= 0 for value in diffs)) / (len(diffs) + 1)
    return {
        "point": rounded(point),
        "ci_low": rounded(quantile(diffs, 0.025)),
        "ci_high": rounded(quantile(diffs, 0.975)),
        "p_one_sided": round(p_one_sided, 6),
        "n_boot": n_boot,
        "n_items": len(rows),
        "n_clusters": len(clusters),
    }


def holm(p_values: list[float]) -> list[float]:
    m = len(p_values)
    order = sorted(range(m), key=p_values.__getitem__)
    adjusted = [1.0] * m
    running = 0.0
    for rank, index in enumerate(order):
        running = max(running, (m - rank) * p_values[index])
        adjusted[index] = min(1.0, running)
    return adjusted


def benjamini_hochberg(p_values: list[float]) -> list[float]:
    m = len(p_values)
    order = sorted(range(m), key=p_values.__getitem__)
    adjusted = [1.0] * m
    running = 1.0
    for rank in range(m, 0, -1):
        index = order[rank - 1]
        running = min(running, p_values[index] * m / rank)
        adjusted[index] = min(1.0, running)
    return adjusted


def apply_corrections(records: list[dict[str, Any]], family_key: str) -> None:
    families: dict[str, list[int]] = defaultdict(list)
    for index, record in enumerate(records):
        families[str(record[family_key])].append(index)
    for indexes in families.values():
        ps = [float(records[index]["bootstrap"]["p_one_sided"]) for index in indexes]
        for index, h, q in zip(indexes, holm(ps), benjamini_hochberg(ps)):
            records[index]["p_holm"] = round(h, 6)
            records[index]["q_bh"] = round(q, 6)
            records[index]["holm_significant_0_05"] = h < 0.05


def round_number(path: Path) -> int:
    return int(path.name.removeprefix("round"))


def audit_state(
    state_name: str, judge_slug: str, arm_name: str, n_boot: int
) -> list[dict[str, Any]]:
    state_base = RUBRIC_ROOT / state_name
    records: list[dict[str, Any]] = []
    if not state_base.exists():
        return records
    for benchmark, dimension in LINE_SPECS:
        state_dir = state_base / f"{benchmark}__{dimension}"
        if not state_dir.exists():
            continue
        ids = eval_ids(benchmark, dimension)
        items_all = load_items(benchmark, dimension, "dev")
        items = {item_id: items_all[item_id] for item_id in ids if item_id in items_all}
        incumbent = baseline_labels(benchmark, dimension, judge_slug, ids)
        for round_dir in sorted(state_dir.glob("round[0-9]*"), key=round_number):
            summary_path = round_dir / "summary.json"
            if not summary_path.exists():
                continue
            summary = read_json(summary_path)
            finals = summary.get("finals") or []
            round_records: list[dict[str, Any]] = []
            for final in finals:
                candidate_id = str(final["id"])
                candidate = response_labels(
                    round_dir / f"cand_{candidate_id}" / "responses.jsonl",
                    benchmark,
                    dimension,
                    ids,
                )
                rows = paired_rows(items, candidate, incumbent)
                if not rows:
                    continue
                record = {
                    "arm": arm_name,
                    "state": state_name,
                    "benchmark": benchmark,
                    "dimension": dimension,
                    "round": int(summary["round"]),
                    "candidate": candidate_id,
                    "accepted": summary.get("winner") == candidate_id,
                    "original_full": final.get("full"),
                    "family_round": f"{arm_name}:{benchmark}:{dimension}:r{summary['round']}",
                    "family_arm": arm_name,
                    "bootstrap": bootstrap_test(
                        rows,
                        n_boot,
                        seed=20260716 + len(records) * 101 + len(round_records),
                    ),
                }
                records.append(record)
                round_records.append(record)
            winner = summary.get("winner")
            if winner:
                incumbent = response_labels(
                    round_dir / f"cand_{winner}" / "responses.jsonl",
                    benchmark,
                    dimension,
                    ids,
                )
    apply_corrections(records, "family_round")
    arm_ps = [float(record["bootstrap"]["p_one_sided"]) for record in records]
    if arm_ps:
        for record, h, q in zip(records, holm(arm_ps), benjamini_hochberg(arm_ps)):
            record["p_holm_across_arm"] = round(h, 6)
            record["q_bh_across_arm"] = round(q, 6)
    return records


def stability_audit(n_repeats: int, folds: int) -> list[dict[str, Any]]:
    results = []
    state_base = RUBRIC_ROOT / "stage1_glm-5.2"
    for benchmark, dimension in LINE_SPECS:
        state_dir = state_base / f"{benchmark}__{dimension}"
        ids = eval_ids(benchmark, dimension)
        items_all = load_items(benchmark, dimension, "dev")
        items = {item_id: items_all[item_id] for item_id in ids if item_id in items_all}
        incumbent = baseline_labels(benchmark, dimension, "glm-5.2", ids)
        candidate = response_labels(
            state_dir / "incumbent_responses.jsonl", benchmark, dimension, ids
        )
        rows = paired_rows(items, candidate, incumbent)
        grouped: dict[str, list[tuple[str, str, str, str]]] = defaultdict(list)
        for row in rows:
            grouped[row[0]].append(row)
        conversations = sorted(grouped)
        rng = random.Random(f"20260716:{benchmark}:{dimension}:folds")
        fold_effects: list[float] = []
        for _ in range(n_repeats):
            shuffled = conversations[:]
            rng.shuffle(shuffled)
            buckets = [[] for _ in range(folds)]
            for index, conversation in enumerate(shuffled):
                buckets[index % folds].append(conversation)
            for bucket in buckets:
                sample = [row for conversation in bucket for row in grouped[conversation]]
                value = effect(sample)
                if value is not None:
                    fold_effects.append(value)
        jackknife: list[float] = []
        for held_out in conversations:
            sample = [row for conversation, cluster in grouped.items() if conversation != held_out for row in cluster]
            value = effect(sample)
            if value is not None:
                jackknife.append(value)
        results.append(
            {
                "benchmark": benchmark,
                "dimension": dimension,
                "overall_point": rounded(effect(rows)),
                "n_items": len(rows),
                "n_conversations": len(conversations),
                "repeated_folds": {
                    "n_repeats": n_repeats,
                    "folds": folds,
                    "n_fold_estimates": len(fold_effects),
                    "positive_fraction": round(sum(value > 0 for value in fold_effects) / len(fold_effects), 4),
                    "median": rounded(median(fold_effects)),
                    "p10": rounded(quantile(fold_effects, 0.10)),
                    "p90": rounded(quantile(fold_effects, 0.90)),
                    "min": rounded(min(fold_effects)),
                    "max": rounded(max(fold_effects)),
                },
                "leave_one_conversation_out": {
                    "n_estimates": len(jackknife),
                    "positive_fraction": round(sum(value > 0 for value in jackknife) / len(jackknife), 4),
                    "min": rounded(min(jackknife)),
                    "max": rounded(max(jackknife)),
                },
            }
        )
    return results


def factorial_evidence() -> list[dict[str, Any]]:
    rows = []
    for benchmark, dimension in LINE_SPECS:
        full = read_json(
            RUBRIC_ROOT / "stage1_glm-5.2" / f"{benchmark}__{dimension}" / "round1" / "summary.json"
        )
        nodiag = read_json(
            RUBRIC_ROOT / "stage1_glm-5.2_nodiag" / f"{benchmark}__{dimension}" / "round1" / "summary.json"
        )
        ablation = read_json(
            RUBRIC_ROOT / "stage1_glm-5.2" / f"{benchmark}__{dimension}" / "ablation" / "summary.json"
        )
        full_winner = next(
            (entry for entry in full.get("finals", []) if entry["id"] == full.get("winner")), None
        )
        nodiag_winner = next(
            (entry for entry in nodiag.get("finals", []) if entry["id"] == nodiag.get("winner")), None
        )
        rows.append(
            {
                "benchmark": benchmark,
                "dimension": dimension,
                "cells": {
                    "diagnosis_constrained_gated": (full_winner or {}).get("full"),
                    "no_diagnosis_constrained_gated": (nodiag_winner or {}).get("full"),
                    "no_diagnosis_free_ungated_genk": ablation["baselines"]["genk"]["naive_best"]["result_vs_v1"],
                    "raw_error_free_ungated_gepa_style": ablation["baselines"]["gepa"]["result_vs_v1"],
                    "manual_structured_ungated": ablation["baselines"]["manual"]["result_vs_v1"],
                },
                "strict_factorial_complete": False,
                "missing_strict_cells": [
                    "diagnosis + free edit + identical gate",
                    "diagnosis + constrained edit + no gate with identical proposal pool",
                ],
            }
        )
    return rows


def seed_replications() -> dict[str, Any]:
    arms: dict[str, list[dict[str, Any]]] = {"full": [], "no_diagnosis": []}
    specs = [
        ("full", "stage1_glm-5.2", "original"),
        ("no_diagnosis", "stage1_glm-5.2_nodiag", "original"),
    ]
    specs.extend(
        ("no_diagnosis" if "nodiag" in path.name else "full", path.name, path.name)
        for path in sorted(RUBRIC_ROOT.glob("stage1_glm-5.2*seed*"))
        if path.is_dir()
    )
    for arm, state_name, seed_label in specs:
        path = RUBRIC_ROOT / state_name / "mrbench__Providing_Guidance" / "round1" / "summary.json"
        if not path.exists():
            continue
        summary = read_json(path)
        winner = next(
            (entry for entry in summary.get("finals", []) if entry["id"] == summary.get("winner")), None
        )
        arms[arm].append(
            {
                "state": state_name,
                "seed": summary.get("proposal_seed") or seed_label,
                "winner": summary.get("winner"),
                "accepted": winner is not None,
                "effect": None if winner is None else winner["full"]["point"],
                "ci_low": None if winner is None else winner["full"]["ci_low"],
                "ci_high": None if winner is None else winner["full"]["ci_high"],
            }
        )
    return {
        arm: {
            "runs": runs,
            "n_runs": len(runs),
            "acceptance_rate": None if not runs else round(sum(row["accepted"] for row in runs) / len(runs), 4),
            "accepted_effect_median": rounded(median([row["effect"] for row in runs if row["effect"] is not None]))
            if any(row["effect"] is not None for row in runs)
            else None,
        }
        for arm, runs in arms.items()
    }


def stage3_multiplicity(n_boot: int) -> list[dict[str, Any]]:
    specs = (
        ("stage1_glm-5.2", "glm-5.2", "mrbench", "Providing_Guidance"),
        ("stage1_glm-5.2", "glm-5.2", "mrbench", "Coherence"),
        ("stage1_glm-5.2", "glm-5.2", "bea2025", "Providing_Guidance"),
        ("stage1", "minimax3", "mrbench", "Providing_Guidance"),
    )
    records = []
    for state_name, judge_slug, benchmark, dimension in specs:
        state_dir = RUBRIC_ROOT / state_name / f"{benchmark}__{dimension}" / "stage3"
        summary = read_json(state_dir / "summary.json")
        ids = {item_id for item_id in load_items(benchmark, dimension, "test")}
        items = load_items(benchmark, dimension, "test")
        candidate = response_labels(
            state_dir / str(summary["evolved_version"]) / "responses.jsonl",
            benchmark,
            dimension,
            ids,
        )
        incumbent = response_labels(state_dir / "v1" / "responses.jsonl", benchmark, dimension, ids)
        rows = paired_rows(items, candidate, incumbent)
        records.append(
            {
                "state": state_name,
                "judge": judge_slug,
                "benchmark": benchmark,
                "dimension": dimension,
                "bootstrap": bootstrap_test(rows, n_boot, 20260716 + len(records) * 997),
            }
        )
    ps = [record["bootstrap"]["p_one_sided"] for record in records]
    for record, h, q in zip(records, holm(ps), benjamini_hochberg(ps)):
        record["p_holm_across_four_test_lines"] = round(h, 6)
        record["q_bh_across_four_test_lines"] = round(q, 6)
        record["holm_significant_0_05"] = h < 0.05
    return records


def render_report(summary: dict[str, Any]) -> str:
    lines = [
        "# Teaching-judge rubric robustness audit",
        "",
        "> Offline reanalysis only. No new human labels and no model calls are used by this audit.",
        "",
        "## 1. Multiplicity-corrected accepted candidates",
        "",
        "| Arm | Line | Round | Candidate | Delta kappa | p | Holm within round | Holm across arm |",
        "|---|---|---:|---|---:|---:|---:|---:|",
    ]
    for row in summary["candidate_tests"]:
        if not row["accepted"]:
            continue
        line = f"{row['benchmark']}/{row['dimension']}"
        lines.append(
            f"| {row['arm']} | {line} | {row['round']} | {row['candidate']} | "
            f"{row['bootstrap']['point']:+.4f} | {row['bootstrap']['p_one_sided']:.4f} | "
            f"{row['p_holm']:.4f} | {row['p_holm_across_arm']:.4f} |"
        )
    lines.extend(
        [
            "",
            "## 2. Sealed-test multiplicity sensitivity",
            "",
            "| Judge | Line | Delta kappa | p | Holm across four | Survives |",
            "|---|---|---:|---:|---:|---:|",
        ]
    )
    for row in summary["stage3_tests"]:
        lines.append(
            f"| {row['judge']} | {row['benchmark']}/{row['dimension']} | "
            f"{row['bootstrap']['point']:+.4f} | {row['bootstrap']['p_one_sided']:.4f} | "
            f"{row['p_holm_across_four_test_lines']:.4f} | "
            f"{'yes' if row['holm_significant_0_05'] else 'no'} |"
        )
    lines.extend(
        [
            "",
            "## 3. Conversation-level stability",
            "",
            "| Line | Overall delta | Positive repeated folds | Fold p10 to p90 | Leave-one-conversation-out range |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for row in summary["stability"]:
        fold = row["repeated_folds"]
        jack = row["leave_one_conversation_out"]
        lines.append(
            f"| {row['benchmark']}/{row['dimension']} | {row['overall_point']:+.4f} | "
            f"{fold['positive_fraction']:.3f} | {fold['p10']:+.4f} to {fold['p90']:+.4f} | "
            f"{jack['min']:+.4f} to {jack['max']:+.4f} |"
        )
    lines.extend(
        [
            "",
            "## 4. Factorial-style evidence boundary",
            "",
            "The repository contains a broad four-family ablation plus a strict P5 removal. "
            "It is not a complete factorial isolation of constrained editing and significance gating; "
            "the missing cells are recorded in `summary.json` rather than inferred away.",
            "",
            "## 5. Proposal-seed replication",
            "",
        ]
    )
    for arm, result in summary["proposal_seed_replications"].items():
        lines.append(
            f"- `{arm}`: {result['n_runs']} runs; acceptance rate "
            f"{result['acceptance_rate']}; median accepted effect {result['accepted_effect_median']}."
        )
    lines.extend(
        [
            "",
            "## Interpretation rule",
            "",
            "- Holm-corrected results support family-wise claims.",
            "- BH-corrected results support explicitly labeled exploratory claims.",
            "- Repeated-fold results are stability diagnostics, not new independent test evidence.",
            "- The sealed test remains untouched by selection; its four pre-existing lines are only re-scored offline.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n-boot", type=int, default=5000)
    parser.add_argument("--fold-repeats", type=int, default=200)
    parser.add_argument("--folds", type=int, default=5)
    args = parser.parse_args()

    candidate_tests: list[dict[str, Any]] = []
    for state_name, judge_slug, arm_name in PRIMARY_STATES:
        candidate_tests.extend(audit_state(state_name, judge_slug, arm_name, args.n_boot))
    summary = {
        "generated_by": "scripts/analyze_judge_rubric_robustness.py",
        "analysis_date": "2026-07-16",
        "no_model_calls": True,
        "no_new_human_labels": True,
        "candidate_tests": candidate_tests,
        "stage3_tests": stage3_multiplicity(args.n_boot),
        "stability": stability_audit(args.fold_repeats, args.folds),
        "factorial_evidence": factorial_evidence(),
        "proposal_seed_replications": seed_replications(),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_json(OUT_DIR / "summary.json", summary)
    (OUT_DIR / "report.md").write_text(render_report(summary), encoding="utf-8")
    print(f"wrote {OUT_DIR / 'summary.json'}")
    print(f"wrote {OUT_DIR / 'report.md'}")


if __name__ == "__main__":
    main()
