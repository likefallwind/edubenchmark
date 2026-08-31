#!/usr/bin/env python3
"""Derive per-model (task x metric) means from the imported EduBench raw scores.

The colleague-run EduBench results under
``reports/eval/edubench/judge-deepseek-v3.2/<model>/`` are immutable inputs
(see CLAUDE.md).  This script only READS ``scored.jsonl`` and
writes derived, regenerable artifacts to ``reports/eval/edubench/_metrics/`` so
the rebenchmark aggregation can consume EduBench at the same granularity and in
the same "one row per (benchmark, subdimension, model)" shape as every other
benchmark (mapping v2 / R1: metric-level cells instead of task means).

Outputs (idempotent, overwritten on each run):
- ``task_metric_means.jsonl``: one row per (model, task, metric) with
  ``n / mean / sd``; ``task == "ALL"`` rows pool all five tasks.  Two
  special composite metrics pool the clarity_concision_inspiration +
  scenario_element_integration pair (per-item mean of the two metrics,
  then mean over items): ``tmg_pcc_composite`` over TMG/PCC items for the
  P18 artifact_generation cell, and ``qg_composite`` over QG items for
  the P23 item_generation cell (mapping v4/R18 split QG out of P18; the
  legacy pooled ``artifact_composite`` row is no longer emitted).
- ``README.md``: provenance note.

Usage: python scripts/build_edubench_metric_summaries.py
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from eval.judge_dirs import find_judge_dir, is_judge_dir  # noqa: E402

HISTORICAL_JUDGE = "deepseek-v3.2"
EDUBENCH_DIR = ROOT / "reports" / "eval" / "edubench"
SOURCE_DIR = find_judge_dir(EDUBENCH_DIR, HISTORICAL_JUDGE)
OUT_DIR = EDUBENCH_DIR / "_metrics"

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
EXPRESSION_METRICS = ("clarity_concision_inspiration", "scenario_element_integration")
CORRECTNESS_METRICS = ("domain_knowledge_accuracy", "basic_factual_accuracy")
# (composite metric name, task label, member tasks, member metrics).
# R18/R19: QG feeds the item-generation P, TMG/PCC the artifact P (P 编号见 v6 JSON)。
# R23: qg_correctness_composite 新增——把"生成题目的内容正确性"从零覆盖变部分覆盖。
COMPOSITES = (
    ("tmg_pcc_composite", "TMG/PCC", {"TMG", "PCC"}, EXPRESSION_METRICS),
    ("qg_composite", "QG", {"QG"}, EXPRESSION_METRICS),
    ("qg_correctness_composite", "QG", {"QG"}, CORRECTNESS_METRICS),
)


def judge_of(mdir: Path) -> str:
    """Who judged this run. summary.json's top-level field is authoritative;
    the colleague's imported dirs predate that field and are all deepseek-v3.2."""
    summary = mdir / "summary.json"
    if summary.exists():
        try:
            judge = json.loads(summary.read_text(encoding="utf-8")).get("judge_model")
        except json.JSONDecodeError:
            judge = None
        if judge:
            return str(judge).split(" ")[0]
    if SOURCE_DIR in mdir.parents:
        return "deepseek-v3.2"
    return "unknown"


def model_dirs() -> list[tuple[Path, str]]:
    """All EduBench runs with per-item judge scores, as (dir, judge).

    Two locations, deliberately both:
    - ``judge-deepseek-v3.2/``: the colleague's 12-model run (论文口径裁判).
    - ``judge-minimax3/`` 等：新标准跑分，裁判 MiniMax-M3。

    2026-08-17：原来只扫前者，于是 harness 自己跑的模型在 edubench 上永远零证据
    ——Qwen3.5-4B 的好跑分（M3 判，3,795 题）在顶层，而它在 `judge-deepseek-v3.2/`
    下那份是 v3.2 中继故障期的废跑（scored=0），两头落空，P12 出题能力整个没分。
    裁判混用是已知的、当前接受的口径（用户裁决 2026-08-17：现阶段先混着用，
    但必须标注清楚），所以每行都带上 `judge`，下游取分把它写进 notes。

    优先级：``judge-deepseek-v3.2/`` 在前，其余裁判目录在后。同名模型两处都有时（glm-5.2、
    Qwen3.5-4B），调用方按「先产出行的那份胜出」去重——**不能按目录名去重**，因为
    `judge-deepseek-v3.2/Qwen-Qwen3.5-4B` 是个 scored=0 的废跑，按名字挡掉顶层那份
    就会把这个模型的 edubench 证据全部抹掉。
    """
    dirs: list[tuple[Path, str]] = []
    # 历史裁判目录在前（见上面的优先级说明），其余裁判目录按名字跟在后面。
    ordered = [SOURCE_DIR] + [
        d
        for d in sorted(EDUBENCH_DIR.iterdir())
        if d.is_dir() and is_judge_dir(d.name) and d != SOURCE_DIR
    ]
    for judge_dir in ordered:
        if not judge_dir.is_dir():
            continue
        for p in sorted(judge_dir.iterdir()):
            if p.is_dir() and (p / "scored.jsonl").exists():
                dirs.append((p, judge_of(p)))
    return dirs


def stats(values: list[float]) -> dict[str, float | int]:
    n = len(values)
    mean = sum(values) / n
    sd = math.sqrt(sum((v - mean) ** 2 for v in values) / n) if n > 1 else 0.0
    return {"n": n, "mean": round(mean, 4), "sd": round(sd, 4)}


def main() -> None:
    rows: list[dict] = []
    # R27：键从 model 改成 (model, judge)。原来按模型去重、"先产出行的那份胜出",
    # 于是同一模型被多个判官判过时只有一份能出行——判官在下游进了取分键也没用,
    # 上游根本不喂第二份。判官视图要求每个判官各自完整,所以这里必须全量产出。
    # `by_cell` 非空才认领这一档保持不变:它挡的是 scored=0 的废跑,与判官无关。
    emitted: dict[tuple[str, str], bool] = {}
    for mdir, judge in model_dirs():
        model = mdir.name
        if (model, judge) in emitted:
            print(f"{model}: 跳过 {mdir.relative_to(EDUBENCH_DIR)}（judge={judge} 已产出）")
            continue
        by_cell: dict[tuple[str, str], list[float]] = {}
        composite_values: dict[str, list[float]] = {name: [] for name, _, _, _ in COMPOSITES}
        n_items = 0
        with (mdir / "scored.jsonl").open(encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                row = json.loads(line)
                if row.get("score_status") != "scored":
                    continue
                dims = row.get("dimension_scores") or {}
                task = (row.get("buckets") or {}).get("task", "unknown")
                n_items += 1
                for metric in METRICS:
                    value = dims.get(metric)
                    if value is None or math.isnan(float(value)):
                        continue
                    value = float(value)
                    by_cell.setdefault((task, metric), []).append(value)
                    by_cell.setdefault(("ALL", metric), []).append(value)
                for name, _, member_tasks, member_metrics in COMPOSITES:
                    if task not in member_tasks:
                        continue
                    pair = [
                        float(dims[m])
                        for m in member_metrics
                        if dims.get(m) is not None and not math.isnan(float(dims[m]))
                    ]
                    if pair:
                        composite_values[name].append(sum(pair) / len(pair))
        for (task, metric), values in sorted(by_cell.items()):
            rows.append({"model": model, "judge": judge, "task": task, "metric": metric, **stats(values)})
        for name, task_label, _, _ in COMPOSITES:
            if composite_values[name]:
                rows.append(
                    {"model": model, "judge": judge, "task": task_label, "metric": name, **stats(composite_values[name])}
                )
        if by_cell:
            emitted[(model, judge)] = True
        counts = " ".join(f"{name}_n={len(composite_values[name])}" for name, _, _, _ in COMPOSITES)
        print(f"{model}: judge={judge} items={n_items} cells={len(by_cell)} {counts}")

    OUT_DIR.mkdir(exist_ok=True)
    out = OUT_DIR / "task_metric_means.jsonl"
    out.write_text(
        "\n".join(json.dumps(r, ensure_ascii=False, sort_keys=True) for r in rows) + "\n",
        encoding="utf-8",
    )
    (OUT_DIR / "README.md").write_text(
        "# EduBench 指标级派生分数（生成物，勿手改）\n\n"
        "由 `scripts/build_edubench_metric_summaries.py` 从 `judge-deepseek-v3.2/` 各模型目录的 `scored.jsonl`"
        "（同事原始判分，只读不改）派生：每行一个 (model, task, metric) 的 n/mean/sd。\n\n"
        "- `task == \"ALL\"`：五任务合并的指标均值——映射 v2 中 `<metric> (metric)` 格子的取分来源。\n"
        "- `metric == \"tmg_pcc_composite\"`（task=TMG/PCC）与 `metric == \"qg_composite\"`（task=QG）："
        "对应任务上 clarity_concision_inspiration + scenario_element_integration 的逐题两指标均值再取均值，"
        "分别对应 P18 教学产物生成与 P23 题目生成的 task×metric 复合格子"
        "（R18 拆分 QG→P23 后原 artifact_composite 不再产出）。\n"
        "- `sd` 为题级标准差，供 13 号检查的死格子（SD<0.5）判定参考。\n",
        encoding="utf-8",
    )
    print(f"rows: {len(rows)} -> {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
