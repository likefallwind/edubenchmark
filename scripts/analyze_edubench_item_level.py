#!/usr/bin/env python3
"""Item-level analysis of EduBench judge dimension scores.

Reads reports/eval/edubench/_judge-deepseek-v3.2/<model>/scored.jsonl
(11 models x 3,797 items x
12 judge metrics) and produces evidence for mapping v2 (R1/R13):

1. Within-model item-level Spearman between the 12 metrics (halo check with
   n=3,797 instead of n=11 model-level points).
2. Same correlations computed within (model, task) to control task mix.
3. Task x metric variance profile: metrics a judge scores near-constant on a
   task carry no information there and should not be mapped from that task.
4. Task x metric cell means per model -> cross-model discrimination (SD) per
   cell, the input for fine-grained (task, metric) -> P mapping.

Outputs reports/eval/edubench/_analysis/item_level_analysis.{json,md}.
Stdlib only; Spearman uses average ranks.
"""

from __future__ import annotations

import json
import math
from collections import defaultdict
from pathlib import Path
from statistics import fmean, stdev

ROOT = Path(__file__).resolve().parents[1]
EVAL_DIR = ROOT / "reports" / "eval" / "edubench"
SOURCE_DIR = EVAL_DIR / "_judge-deepseek-v3.2"
OUT_DIR = EVAL_DIR / "_analysis"

METRICS = [
    "instruction_following",
    "tone_style_consistency",
    "content_relevance_scope_control",
    "scenario_element_integration",
    "basic_factual_accuracy",
    "domain_knowledge_accuracy",
    "reasoning_process_rigor",
    "error_identification_correction_accuracy",
    "clarity_concision_inspiration",
    "motivation_guidance_positive_feedback",
    "personalized_adaptation_learning_support",
    "higher_order_thinking_ability_development",
]

METRIC_ZH = {
    "instruction_following": "指令遵循",
    "tone_style_consistency": "语气与风格一致性",
    "content_relevance_scope_control": "内容相关性与范围控制",
    "scenario_element_integration": "场景元素整合",
    "basic_factual_accuracy": "基础事实准确性",
    "domain_knowledge_accuracy": "领域知识准确性",
    "reasoning_process_rigor": "推理过程严密性",
    "error_identification_correction_accuracy": "错误识别与纠正",
    "clarity_concision_inspiration": "表达清晰度与启发性",
    "motivation_guidance_positive_feedback": "动机引导与正向反馈",
    "personalized_adaptation_learning_support": "个性化适应与学习支持",
    "higher_order_thinking_ability_development": "高阶思维能力培养",
}


def rankdata(values: list[float]) -> list[float]:
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        avg = (i + j) / 2 + 1
        for k in range(i, j + 1):
            ranks[order[k]] = avg
        i = j + 1
    return ranks


def spearman(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) < 3:
        return None
    rx, ry = rankdata(xs), rankdata(ys)
    mx, my = fmean(rx), fmean(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    dx = math.sqrt(sum((a - mx) ** 2 for a in rx))
    dy = math.sqrt(sum((b - my) ** 2 for b in ry))
    if dx == 0 or dy == 0:
        return None
    return num / (dx * dy)


def load_rows() -> dict[str, list[dict]]:
    per_model: dict[str, list[dict]] = {}
    for model_dir in sorted(SOURCE_DIR.iterdir()):
        scored = model_dir / "scored.jsonl"
        if not scored.is_file():
            continue
        rows = []
        with scored.open(encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                rec = json.loads(line)
                dims = rec.get("dimension_scores") or {}
                if not dims:
                    continue
                rows.append(
                    {
                        "item_id": rec["item_id"],
                        "task": (rec.get("buckets") or {}).get("task", "unknown"),
                        "lang": (rec.get("buckets") or {}).get("lang", "unknown"),
                        "dims": {
                            m: (
                                float(dims[m])
                                if isinstance(dims.get(m), (int, float))
                                and math.isfinite(float(dims[m]))
                                else None
                            )
                            for m in METRICS
                        },
                    }
                )
        if rows:
            per_model[model_dir.name] = rows
    return per_model


def pairwise_matrix(rows: list[dict]) -> dict[tuple[str, str], float | None]:
    out: dict[tuple[str, str], float | None] = {}
    for i, a in enumerate(METRICS):
        for b in METRICS[i + 1 :]:
            xs, ys = [], []
            for row in rows:
                va, vb = row["dims"].get(a), row["dims"].get(b)
                if va is not None and vb is not None:
                    xs.append(va)
                    ys.append(vb)
            out[(a, b)] = spearman(xs, ys)
    return out


def main() -> None:
    per_model = load_rows()
    models = sorted(per_model)
    print(f"models={len(models)} rows_per_model={[len(per_model[m]) for m in models]}")

    tasks = sorted({row["task"] for rows in per_model.values() for row in rows})

    # 1. within-model item-level metric x metric Spearman, averaged over models
    per_model_matrices = {m: pairwise_matrix(per_model[m]) for m in models}
    avg_matrix: dict[str, dict[str, float | None]] = {a: {} for a in METRICS}
    for i, a in enumerate(METRICS):
        for b in METRICS[i + 1 :]:
            vals = [per_model_matrices[m][(a, b)] for m in models]
            vals = [v for v in vals if v is not None]
            avg = fmean(vals) if vals else None
            avg_matrix[a][b] = avg
            avg_matrix[b][a] = avg

    # 2. within (model, task) for every pair, weighted by n, then averaged
    within_task: dict[tuple[str, str], float | None] = {}
    for i, a in enumerate(METRICS):
        for b in METRICS[i + 1 :]:
            vals = []
            for m in models:
                by_task: dict[str, list[dict]] = defaultdict(list)
                for row in per_model[m]:
                    by_task[row["task"]].append(row)
                for trows in by_task.values():
                    xs = [r["dims"][a] for r in trows if r["dims"][a] is not None and r["dims"][b] is not None]
                    ys = [r["dims"][b] for r in trows if r["dims"][a] is not None and r["dims"][b] is not None]
                    rho = spearman(xs, ys)
                    if rho is not None:
                        vals.append(rho)
            within_task[(a, b)] = fmean(vals) if vals else None

    # 3. task x metric variance profile (item-level SD within model, averaged)
    task_metric_sd: dict[str, dict[str, float]] = {t: {} for t in tasks}
    task_metric_mean: dict[str, dict[str, float]] = {t: {} for t in tasks}
    task_n: dict[str, int] = {}
    for t in tasks:
        for metric in METRICS:
            sds, means = [], []
            for m in models:
                vals = [
                    r["dims"][metric]
                    for r in per_model[m]
                    if r["task"] == t and r["dims"][metric] is not None
                ]
                if len(vals) >= 3:
                    sds.append(stdev(vals))
                    means.append(fmean(vals))
            if sds:
                task_metric_sd[t][metric] = fmean(sds)
                task_metric_mean[t][metric] = fmean(means)
        task_n[t] = sum(1 for r in per_model[models[0]] if r["task"] == t)

    # 4. task x metric cell means per model -> cross-model discrimination
    cell_scores: dict[tuple[str, str], dict[str, float]] = {}
    for t in tasks:
        for metric in METRICS:
            per: dict[str, float] = {}
            for m in models:
                vals = [
                    r["dims"][metric]
                    for r in per_model[m]
                    if r["task"] == t and r["dims"][metric] is not None
                ]
                if vals:
                    per[m] = fmean(vals)
            if len(per) == len(models):
                cell_scores[(t, metric)] = per
    cell_stats = {
        f"{t}|{metric}": {
            "mean": round(fmean(per.values()), 3),
            "sd": round(stdev(per.values()), 3),
            "min": round(min(per.values()), 3),
            "max": round(max(per.values()), 3),
        }
        for (t, metric), per in cell_scores.items()
    }

    # key pair summaries
    def pair(a: str, b: str) -> dict:
        vals = [per_model_matrices[m][(a, b)] if (a, b) in per_model_matrices[m] else per_model_matrices[m][(b, a)] for m in models]
        vals = [v for v in vals if v is not None]
        return {
            "item_level_mean": round(fmean(vals), 3) if vals else None,
            "item_level_range": [round(min(vals), 3), round(max(vals), 3)] if vals else None,
            "within_task_mean": round(within_task.get((a, b), within_task.get((b, a))) or 0, 3),
        }

    key_pairs = {
        "instruction_following__domain_knowledge_accuracy": pair(
            "instruction_following", "domain_knowledge_accuracy"
        ),
        "instruction_following__basic_factual_accuracy": pair(
            "instruction_following", "basic_factual_accuracy"
        ),
        "error_identification__domain_knowledge": pair(
            "error_identification_correction_accuracy", "domain_knowledge_accuracy"
        ),
        "error_identification__higher_order_thinking": pair(
            "error_identification_correction_accuracy",
            "higher_order_thinking_ability_development",
        ),
        "motivation__personalization": pair(
            "motivation_guidance_positive_feedback",
            "personalized_adaptation_learning_support",
        ),
    }

    # mean absolute inter-metric correlation (halo magnitude) item level
    all_avgs = [v for a in METRICS for b, v in avg_matrix[a].items() if v is not None]
    halo_item = fmean(all_avgs) / 1  # each pair counted twice, mean unaffected

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "models": models,
        "n_items_per_model": {m: len(per_model[m]) for m in models},
        "tasks": {t: task_n[t] for t in tasks},
        "item_level_metric_spearman_avg_over_models": {
            a: {b: (round(v, 3) if v is not None else None) for b, v in avg_matrix[a].items()}
            for a in METRICS
        },
        "within_model_task_spearman": {
            f"{a}|{b}": (round(v, 3) if v is not None else None)
            for (a, b), v in within_task.items()
        },
        "task_metric_item_sd": {
            t: {m: round(v, 3) for m, v in task_metric_sd[t].items()} for t in tasks
        },
        "task_metric_item_mean": {
            t: {m: round(v, 3) for m, v in task_metric_mean[t].items()} for t in tasks
        },
        "cell_cross_model_stats": cell_stats,
        "key_pairs": key_pairs,
        "mean_inter_metric_item_rho": round(halo_item, 3),
    }
    (OUT_DIR / "item_level_analysis.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8"
    )

    # markdown report
    lines = [
        "# EduBench 逐题级指标分析（2026-07-12）",
        "",
        f"数据：{len(models)} 个模型 × 每模型 {len(per_model[models[0]])} 题 × 12 个裁判指标（裁判 deepseek-v3.2）。",
        "来源 `reports/eval/edubench/_judge-deepseek-v3.2/<model>/scored.jsonl`，脚本 `scripts/analyze_edubench_item_level.py`。",
        "",
        "## 任务分布",
        "",
        "| 任务 | 题数/模型 |",
        "|---|---|",
    ]
    for t in tasks:
        lines.append(f"| {t} | {task_n[t]} |")
    lines += [
        "",
        "## 指标间题级 Spearman（先在每个模型内部跨题算，再对 11 个模型取平均）",
        "",
        "| 指标 | " + " | ".join(METRIC_ZH[m][:4] for m in METRICS) + " |",
        "|---|" + "---|" * len(METRICS),
    ]
    for a in METRICS:
        cells = []
        for b in METRICS:
            if a == b:
                cells.append("—")
            else:
                v = avg_matrix[a].get(b)
                cells.append(f"{v:.2f}" if v is not None else "")
        lines.append(f"| {METRIC_ZH[a]} | " + " | ".join(cells) + " |")
    lines += [
        "",
        f"全部 66 对的平均题级 ρ = **{halo_item:.3f}**。",
        "",
        "## 关键指标对（题级 vs 控制任务后）",
        "",
        "| 指标对 | 题级平均 ρ | 模型间范围 | 任务内平均 ρ |",
        "|---|---|---|---|",
    ]
    zh_pair_names = {
        "instruction_following__domain_knowledge_accuracy": "指令遵循 × 领域知识",
        "instruction_following__basic_factual_accuracy": "指令遵循 × 基础事实",
        "error_identification__domain_knowledge": "错误识别 × 领域知识",
        "error_identification__higher_order_thinking": "错误识别 × 高阶思维",
        "motivation__personalization": "动机引导 × 个性化",
    }
    for key, zh in zh_pair_names.items():
        p = key_pairs[key]
        rng = p["item_level_range"]
        lines.append(
            f"| {zh} | {p['item_level_mean']} | [{rng[0]}, {rng[1]}] | {p['within_task_mean']} |"
        )
    lines += [
        "",
        "## 任务 × 指标：题级 SD（裁判在该任务上是否真用这个指标区分回答）",
        "",
        "SD < 0.5 视为“该指标在该任务上几乎不区分”（加粗标出）。",
        "",
        "| 任务 | " + " | ".join(METRIC_ZH[m][:4] for m in METRICS) + " |",
        "|---|" + "---|" * len(METRICS),
    ]
    for t in tasks:
        cells = []
        for metric in METRICS:
            v = task_metric_sd[t].get(metric)
            if v is None:
                cells.append("")
            elif v < 0.5:
                cells.append(f"**{v:.2f}**")
            else:
                cells.append(f"{v:.2f}")
        lines.append(f"| {t} | " + " | ".join(cells) + " |")
    lines += [
        "",
        "## 任务 × 指标格子的跨模型区分度（11 模型的格子均分的 SD）",
        "",
        "跨模型 SD ≥ 0.3 的格子（够拉开模型排名，可作映射 v2 的候选测量单元）：",
        "",
        "| 任务 | 指标 | 均值 | 跨模型 SD | min | max |",
        "|---|---|---|---|---|---|",
    ]
    good = sorted(
        ((k, s) for k, s in cell_stats.items() if s["sd"] >= 0.3),
        key=lambda kv: -kv[1]["sd"],
    )
    for k, s in good:
        t, metric = k.split("|")
        lines.append(
            f"| {t} | {METRIC_ZH[metric]} | {s['mean']} | {s['sd']} | {s['min']} | {s['max']} |"
        )
    lines += [
        "",
        f"共 {len(cell_stats)} 个完整格子，其中 {len(good)} 个跨模型 SD ≥ 0.3。",
        "",
    ]
    (OUT_DIR / "item_level_analysis.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT_DIR}/item_level_analysis.json and .md")
    print("key pairs:", json.dumps(key_pairs, ensure_ascii=False, indent=1))
    print("mean inter-metric item rho:", round(halo_item, 3))


if __name__ == "__main__":
    main()
