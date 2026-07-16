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
        normalized = row.get("label") or row.get("pred_label")
        if item_id in ids and normalized is not None:
            labels[item_id] = str(normalized)
            continue
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


def render_method_report(summary: dict[str, Any]) -> str:
    stage3 = {
        (row["judge"], row["benchmark"], row["dimension"]): row
        for row in summary["stage3_tests"]
    }
    stability = {
        (row["benchmark"], row["dimension"]): row
        for row in summary["stability"]
    }
    glm_pg = stage3[("glm-5.2", "mrbench", "Providing_Guidance")]
    m3_pg = stage3[("minimax3", "mrbench", "Providing_Guidance")]
    glm_coh = stage3[("glm-5.2", "mrbench", "Coherence")]
    glm_bea = stage3[("glm-5.2", "bea2025", "Providing_Guidance")]

    accepted = [row for row in summary["candidate_tests"] if row["accepted"]]
    accepted_holm_round = sum(row["holm_significant_0_05"] for row in accepted)
    accepted_holm_arm = sum(row["p_holm_across_arm"] < 0.05 for row in accepted)
    glm_full = [row for row in accepted if row["arm"] == "glm_full"]
    glm_nodiag = [row for row in accepted if row["arm"] == "glm_nodiag"]

    def fmt(value: float | None, digits: int = 4) -> str:
        return "n/a" if value is None else f"{value:.{digits}f}"

    lines = [
        "# 统计门控的教学裁判 Rubric 自进化：主要方法、实证贡献与论文边界",
        "",
        "> 日期：2026-07-16  ",
        "> 研究对象：LLM-as-Judge 教学裁判  ",
        "> 数据边界：复用已有专家金标，不新增真人标注；封存 test 不重新参与选择",
        "",
        "## 执行摘要",
        "",
        "本研究提出一套面向教学对话裁判的 rubric 自进化流程：把 rubric 表示为可审计的结构对象，"
        "限制模型每次只能执行小范围类型化编辑；先用诊断池产生候选，再用独立筛选片排序，最后在冻结"
        "评估片上通过对话簇配对 bootstrap 验收，并把所有失败和验收结果写入 ledger。最终只允许通过"
        "封存 test 的 rubric 进入生产。",
        "",
        "研究最重要的结果不是“prompt 可以被优化”，而是识别出两类性质不同的过拟合：筛选片上的"
        "选择噪声可以被分阶段统计门拦截；dev 分布特异性即使在 dev 上显著，也只能由真正封存的 test"
        "发现。glm-5.2 的三条 dev 显著改进只有 MRBench/Providing_Guidance 在 test 复现；同一维度上"
        "MiniMax-M3 的独立 rubric 也通过 test，因此该维度的任务级缺口是当前最坚实的单点结论。",
        "",
        "新增稳健性审计进一步对所有 full-slice 候选重算单侧配对 cluster-bootstrap p 值，并分别进行"
        "轮内 Holm、实验臂内 Holm 和 BH 校正；同时对 glm 最终 rubric 做 200 次五折对话级重分割和"
        "leave-one-conversation-out 审计。这些分析完全复用缓存，不调用新模型，也不重新选择 test。",
        "",
        "## 1. 研究问题",
        "",
        "1. 教学裁判与人类专家的一致性是否足以支撑教育模型评测？",
        "2. 多裁判投票、标签校准、few-shot 锚例和 rubric 编辑分别能修复什么问题？",
        "3. 如何自动修改 rubric，同时避免自由重写、选择噪声和 dev 过拟合？",
        "4. 一个裁判产生的 rubric 能否迁移给另一个裁判？",
        "5. rubric 改进是否会改变下游模型排名和绝对分数？",
        "",
        "## 2. 数据与统计协议",
        "",
        "元评测集包含 24,108 条已有专家标注判例，来源为 MRBench、BEA 2025 和 MathTutorBench。"
        "MRBench 与 BEA 存在共享对话和同源标注，因此所有 dev/test 切分均以 conversation_id 为单位，"
        "重叠对话整体归入同一侧。该设计避免同一教学对话衍生的多个维度或多个 tutor 回复跨切片泄漏。",
        "",
        "主指标为 Cohen's kappa。所有候选比较均在同一题集上与 incumbent 配对，并以对话为 cluster"
        "重采样。新增审计使用单侧 bootstrap p 值回答“候选是否优于 incumbent”，同时报告 Holm"
        "家族错误率控制与 BH 探索性控制。重复对话分割仅作为稳定性诊断，不冒充新的独立 test。",
        "",
        "## 3. 主要方法",
        "",
        "### 3.1 结构化 rubric 与受限编辑",
        "",
        "rubric 由维度定义覆盖、各标签行为判据、边界条款和锚例块组成。候选只能使用"
        "`set_label_criterion`、`add_clause`、`drop_clause`、`edit_definition`、"
        "`add_anchor_block`、`remove_anchor_block` 六类操作。每次提交保留编辑内容、prompt hash、"
        "目标混淆格和效果量，因此可以回滚和追责。",
        "",
        "### 3.2 诊断驱动提案",
        "",
        "反思模型读取人类标签与当前裁判的混淆矩阵、典型错例和裁判 reasoning，针对具体标签边界"
        "生成候选。去诊断臂保留相同结构、筛选片、评估片、预算与统计门，只移除混淆矩阵和错例。"
        "该消融表明诊断不是获得 within-judge dev 提升的必要条件，但迁移矩阵显示它可能帮助候选"
        "从裁判特异补丁转向任务级规则。后者仍应作为中等强度、待扩展的结论。",
        "",
        "### 3.3 三段数据纪律",
        "",
        "诊断池只负责暴露系统性错误；约 250 题的筛选片只负责候选排序；约 600 题的冻结评估片"
        "负责显著性验收。点估计为正但未过线的近失候选只能到选择过程未接触的确认集复验，禁止在"
        "原切片反复测试。最终生产切换还必须通过只打开一次的 test。",
        "",
        "### 3.4 失败 ledger 与回归检查",
        "",
        "每轮记录全部候选及失败原因，下一轮避免重复无效处方。已接受编辑会被逐条摘除重算边际"
        "贡献，并检查 unparsed 率、prompt 长度和残余标签重映射空间。ledger 的独立因果贡献目前只有"
        "案例证据，不作为已被严格消融证明的核心贡献。",
        "",
        "## 4. 核心结果",
        "",
        "### 4.1 多裁判和低成本校准",
        "",
        "三裁判陪审团在 MRBench、BEA 和 MathTutorBench 上均未显著超过最佳单裁判。标签重映射和"
        "分布保持锚例能修复部分整体偏严，但 Providing_Guidance 对这些低成本手段基本免疫，说明"
        "存在需要语义 rubric 编辑的缺口。",
        "",
        "### 4.2 三裁判自进化",
        "",
        "同规格自进化中，glm-5.2 在第一轮三条线均产生 dev 显著验收；MiniMax-M3 在三条线中验收"
        "一条；deepseek-v4-pro 在第二轮验收一条。该结果支持流程可以适配多个裁判，但不能表述为"
        "所有任务、所有裁判都稳定有效，因为后两者的大部分结果只有 dev 证据。",
        "",
        "### 4.3 封存 test 与多重检验敏感性",
        "",
        "| 裁判 | 任务线 | test Delta kappa | 单侧 p | 四线 Holm p | 结论 |",
        "|---|---|---:|---:|---:|---|",
        f"| glm-5.2 | MRBench/Providing_Guidance | {glm_pg['bootstrap']['point']:+.4f} | "
        f"{glm_pg['bootstrap']['p_one_sided']:.4f} | {glm_pg['p_holm_across_four_test_lines']:.4f} | "
        f"{'通过' if glm_pg['holm_significant_0_05'] else '未通过'} |",
        f"| MiniMax-M3 | MRBench/Providing_Guidance | {m3_pg['bootstrap']['point']:+.4f} | "
        f"{m3_pg['bootstrap']['p_one_sided']:.4f} | {m3_pg['p_holm_across_four_test_lines']:.4f} | "
        f"{'通过' if m3_pg['holm_significant_0_05'] else '未通过'} |",
        f"| glm-5.2 | MRBench/Coherence | {glm_coh['bootstrap']['point']:+.4f} | "
        f"{glm_coh['bootstrap']['p_one_sided']:.4f} | {glm_coh['p_holm_across_four_test_lines']:.4f} | 未通过 |",
        f"| glm-5.2 | BEA/Providing_Guidance | {glm_bea['bootstrap']['point']:+.4f} | "
        f"{glm_bea['bootstrap']['p_one_sided']:.4f} | {glm_bea['p_holm_across_four_test_lines']:.4f} | 未通过 |",
        "",
        "test 上 glm 三条 dev 显著线仅一条复现；MiniMax-M3 在同一任务维度的独立 rubric 也复现。"
        "经过四条 test 结果的 Holm 校正后，表中明确标记哪些结论仍能维持家族错误率控制。论文应以"
        "校正后状态为主，未经校正 CI 作为效果量区间保留。",
        "",
        "### 4.4 对话级稳定性",
        "",
        "| 任务线 | 全体 Delta kappa | 重复折正向比例 | 折内 p10-p90 | 留一对话范围 |",
        "|---|---:|---:|---:|---:|",
    ]
    for key in LINE_SPECS:
        row = stability[key]
        folds = row["repeated_folds"]
        jack = row["leave_one_conversation_out"]
        lines.append(
            f"| {key[0]}/{key[1]} | {row['overall_point']:+.4f} | {folds['positive_fraction']:.3f} | "
            f"{folds['p10']:+.4f} 至 {folds['p90']:+.4f} | {jack['min']:+.4f} 至 {jack['max']:+.4f} |"
        )
    lines.extend(
        [
            "",
            "重复折结果显示的是同一 eval 分布内部的稳健性，而不是外部泛化。它可以判断效果是否由"
            "少数对话驱动；不能替代已经使用过的 test，也不能把失败的 test 结果翻回正结论。",
            "",
            "### 4.5 消融与归因",
            "",
            "| 方法族 | 诊断 | 受限编辑 | 两段统计门 | 三线结果 |",
            "|---|---:|---:|---:|---|",
            "| 完整方法 | 是 | 是 | 是 | 3/3 dev 显著 |",
            "| 去诊断 | 否 | 是 | 是 | 2/3 dev 显著 |",
            "| 生成-K | 否 | 否 | 否 | 0/3 显著 |",
            "| GEPA-style greedy | 原始错例 | 否 | 否 | 0/3 显著，1 条显著变差 |",
            "| 手工结构化 rubric | 否 | 部分 | 否 | 0/3 显著 |",
            "",
            "这是一组较完整的多臂消融，加上严格的 P5 去诊断单成分消融；但它不是受限编辑与统计门的"
            "完整 factorial 2x2。当前可以主张“受限编辑和分阶段验收的组合优于所测试替代方案”，不能"
            "分别宣称两者的独立因果贡献已经被四格实验完全识别。原文中的“GEPA 原味”统一改称"
            "“GEPA-style greedy”，因为仓库实现没有复刻 Genetic-Pareto 的完整 Pareto frontier。",
            "",
            f"新增 multiplicity audit 共审计 {len(summary['candidate_tests'])} 个进入 full-slice 的候选。"
            f"在 {len(accepted)} 个被原协议接受的候选中，{accepted_holm_round} 个通过轮内 Holm，"
            f"{accepted_holm_arm} 个通过整个实验臂 Holm。完整逐候选结果见稳健性审计产物。",
            "",
            "### 4.6 跨裁判迁移",
            "",
            "三条诊断驱动 MRBench/Providing_Guidance rubric 的六个跨裁判格全部为正，其中四格显著；"
            "去诊断 rubric 对自身 glm 有效，但迁移到 M3 和 dsv4 后为 -0.004 和 -0.046。该结果支持"
            "“诊断可能促进跨裁判迁移”，但去诊断只有一条 rubric、两个迁移格，不能写成普遍定律。",
            "",
            "### 4.7 下游影响",
            "",
            "v1 与通过 test 的 v2 rubric 对三个被测模型各重判 200 题，模型排序保持 glm-5.2 > minimax3"
            "> MiniMax-M2.7；绝对通过率下降 1.5-4.5 个百分点，模型极差从 0.065 扩大到 0.095。"
            "可以主张 rubric 版本会影响绝对分及分数间距；由于缺少下游人类排序金标，不把“间距扩大”"
            "直接等同于“排名更正确”。",
            "",
            "## 5. 主要贡献",
            "",
            "### 贡献一：面向教学裁判的可审计 rubric 自进化流程",
            "",
            "研究把自由 prompt 重写改造成类型化、小步、可回滚的 rubric 编辑，并把诊断、筛选、验收、"
            "确认和 test 置于不同数据角色中。相比只报告优化后分数，这套流程保留了完整失败轨迹和"
            "prompt provenance，适合教育评测这种需要解释评分标准的场景。",
            "",
            "### 贡献二：实证区分两层过拟合",
            "",
            "13 次筛选冠军缩水和 6 次近失独立确认失败展示了选择噪声；两条 dev 显著 rubric 在 test"
            "归零展示了分布特异性。两者需要不同防线：前者可以靠独立筛选、配对统计和确认集缓解，"
            "后者必须依赖真正封存或外部的数据。",
            "",
            "### 贡献三：发现并验证一个教学维度的任务级 rubric 缺口",
            "",
            "MRBench/Providing_Guidance 在 glm 和 M3 两个裁判上分别通过 test，且诊断驱动 rubric 可跨"
            "三裁判迁移。安全结论是该维度对“带错误但仍在引导”“部分正确的支架”边界描述不足；"
            "该结论不外推到所有教育维度。",
            "",
            "### 贡献四：负结果和证据分级",
            "",
            "多裁判投票不优于最佳单裁判，通用校准修不动关键语义维度，GEPA-style 自由重写出现"
            "显著劣化，dev 显著不保证 test 复现。这些负结果共同给出一套生产切换纪律：按维度验收、"
            "按证据上线、绝对分不跨 rubric 版本比较。",
            "",
            "### 贡献五：不新增真人标注的再利用范式",
            "",
            "研究没有把“零新增标注”包装成无监督；监督信号来自已有专家金标。贡献在于重新组织已有"
            "标注，使同一资产分别承担诊断、筛选、验收和终验角色，从而降低研究与生产校准成本。",
            "",
            "## 6. 论文可安全主张的结论",
            "",
            "1. 受限编辑与分阶段统计验收组成的完整流程，在三条教学裁判线上优于本研究测试的手工、"
            "生成-K 和 GEPA-style greedy 替代方案。",
            "2. 去诊断仍可获得 within-judge dev 提升，因此诊断不是获得局部提升的必要条件。",
            "3. 诊断驱动 rubric 的迁移结果优于当前唯一的去诊断 rubric，提供了诊断促进迁移的初步证据。",
            "4. dev 显著无法排除数据分布特异性；生产 rubric 必须逐线通过封存或外部终验。",
            "5. MRBench/Providing_Guidance 的评分边界存在被两个裁判 test 结果支持的可修复缺口。",
            "",
            "## 7. 不应写成已证实的结论",
            "",
            "1. 不写“方法在所有教育任务和所有裁判上普适”。",
            "2. 不写“受限编辑与统计门各自的独立因果贡献已由严格 2x2 证明”。",
            "3. 不写“诊断必然带来跨裁判迁移”；当前是单一去诊断 rubric 的中等强度证据。",
            "4. 不写“最弱裁判通常写出最好 rubric”；当前只是一项反直觉观察。",
            "5. 不写“下游排名变得更正确”；目前只观察到排序不变、绝对分和间距改变。",
            "6. 不写“零假验收”；应写统计门过滤大量选择噪声，而 test 又拒绝两条 dev 特异改动。",
            "",
            "## 8. 限制与可行的后续工作",
            "",
            "1. 人类金标主要来自英文数学 tutoring，且 MRBench 与 BEA 标注同源；缺少独立标注团队、"
            "中文和其他学科复现。真人双标困难时，这项可以作为明确 limitation，不阻塞当前论文。",
            "2. test 独立单位为 49 或 75 段对话，效果区间仍较宽；不能用题目条数替代对话簇数量。",
            "3. 多 proposal-seed 全量复验会新增约 1.4 万次 gateway 判分。实测当前 gateway 40 分钟"
            "约完成 600 次，因成本与耗时停止，不纳入证据；未完成实验不写成结果。",
            "4. 严格 factorial 仍缺“自由编辑 + 相同统计门”和“受限编辑 + 无统计门”的同候选池对照。"
            "若未来补做，应优先复用候选与缓存，避免把候选质量差异混入门控效应。",
            "5. 可以在不新增真人标注的条件下继续做多对话切分、模型调用重复性和其他公开金标任务迁移；"
            "这些分析不能替代真正外部数据，但能量化当前结论对切分与调用随机性的敏感性。",
            "",
            "## 9. 建议论文定位",
            "",
            "建议标题：**Beyond Dev Significance: Statistically Gated Rubric Evolution for Educational LLM Judges**。",
            "",
            "论文主线应围绕“教学裁判 rubric 如何被优化、如何被验收，以及为什么 dev 显著仍不够”展开。"
            "自动生成 rubric 本身不是核心新意；真正的区分点是教育场景、受限可审计编辑、证据分级和两层"
            "过拟合的实测。当前证据足以形成独立论文；新增真人标注是增强项而非写作前置条件。",
            "",
            "## 10. 产物索引",
            "",
            "- 权威全程记录：`doc/judge_research_full_report_2026-07-11.md`",
            "- 原始方法与实验附录：`doc/rubric_evolution_plan_2026-07-06.md`",
            "- 稳健性审计脚本：`scripts/analyze_judge_rubric_robustness.py`",
            "- 稳健性机器结果：`reports/eval/_judge_rubric/robustness_audit/summary.json`",
            "- 稳健性可读报告：`reports/eval/_judge_rubric/robustness_audit/report.md`",
            "- test 终验：`reports/eval/_judge_rubric/stage1_glm-5.2/*/stage3/summary.json`",
            "- 跨裁判迁移：`reports/eval/_judge_rubric/transfer_matrix/summary.json`",
            "- 下游重判：`reports/eval/_judge_rubric/downstream_ranking/summary.json`",
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
    method_report = ROOT / "doc" / "judge_rubric_evolution_method_and_contributions_2026-07-16.md"
    method_report.write_text(render_method_report(summary), encoding="utf-8")
    print(f"wrote {OUT_DIR / 'summary.json'}")
    print(f"wrote {OUT_DIR / 'report.md'}")
    print(f"wrote {method_report}")


if __name__ == "__main__":
    main()
