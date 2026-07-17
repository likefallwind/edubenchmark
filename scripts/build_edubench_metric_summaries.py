#!/usr/bin/env python3
"""Derive per-model (task x metric) means from the imported EduBench raw scores.

The colleague-run EduBench results under ``reports/eval/edubench/<model>/`` are
immutable inputs (see CLAUDE.md).  This script only READS ``scored.jsonl`` and
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
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EDUBENCH_DIR = ROOT / "reports" / "eval" / "edubench"
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
COMPOSITE_METRICS = ("clarity_concision_inspiration", "scenario_element_integration")
# (composite metric name, task label, member tasks); R18/R19: QG feeds P23, TMG/PCC feed P18
COMPOSITES = (
    ("tmg_pcc_composite", "TMG/PCC", {"TMG", "PCC"}),
    ("qg_composite", "QG", {"QG"}),
)


def model_dirs() -> list[Path]:
    return sorted(
        p for p in EDUBENCH_DIR.iterdir()
        if p.is_dir() and not p.name.startswith("_") and (p / "scored.jsonl").exists()
    )


def stats(values: list[float]) -> dict[str, float | int]:
    n = len(values)
    mean = sum(values) / n
    sd = math.sqrt(sum((v - mean) ** 2 for v in values) / n) if n > 1 else 0.0
    return {"n": n, "mean": round(mean, 4), "sd": round(sd, 4)}


def main() -> None:
    rows: list[dict] = []
    for mdir in model_dirs():
        model = mdir.name
        by_cell: dict[tuple[str, str], list[float]] = {}
        composite_values: dict[str, list[float]] = {name: [] for name, _, _ in COMPOSITES}
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
                pair = [
                    float(dims[m])
                    for m in COMPOSITE_METRICS
                    if dims.get(m) is not None and not math.isnan(float(dims[m]))
                ]
                if pair:
                    for name, _, member_tasks in COMPOSITES:
                        if task in member_tasks:
                            composite_values[name].append(sum(pair) / len(pair))
        for (task, metric), values in sorted(by_cell.items()):
            rows.append({"model": model, "task": task, "metric": metric, **stats(values)})
        for name, task_label, _ in COMPOSITES:
            if composite_values[name]:
                rows.append({"model": model, "task": task_label, "metric": name, **stats(composite_values[name])})
        counts = " ".join(f"{name}_n={len(composite_values[name])}" for name, _, _ in COMPOSITES)
        print(f"{model}: items={n_items} cells={len(by_cell)} {counts}")

    OUT_DIR.mkdir(exist_ok=True)
    out = OUT_DIR / "task_metric_means.jsonl"
    out.write_text(
        "\n".join(json.dumps(r, ensure_ascii=False, sort_keys=True) for r in rows) + "\n",
        encoding="utf-8",
    )
    (OUT_DIR / "README.md").write_text(
        "# EduBench 指标级派生分数（生成物，勿手改）\n\n"
        "由 `scripts/build_edubench_metric_summaries.py` 从各模型目录的 `scored.jsonl`"
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
