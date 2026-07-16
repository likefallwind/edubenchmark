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
  ``n / mean / sd``; ``task == "ALL"`` rows pool all five tasks, and the
  special metric ``artifact_composite`` pools QG/TMG/PCC items over the
  clarity_concision_inspiration + scenario_element_integration pair
  (per-item mean of the two metrics, then mean over items) for the P18
  artifact_generation cell.
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
ARTIFACT_TASKS = {"QG", "TMG", "PCC"}
ARTIFACT_METRICS = ("clarity_concision_inspiration", "scenario_element_integration")
ARTIFACT_METRIC_NAME = "artifact_composite"


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
        artifact_values: list[float] = []
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
                if task in ARTIFACT_TASKS:
                    pair = [
                        float(dims[m])
                        for m in ARTIFACT_METRICS
                        if dims.get(m) is not None and not math.isnan(float(dims[m]))
                    ]
                    if pair:
                        artifact_values.append(sum(pair) / len(pair))
        for (task, metric), values in sorted(by_cell.items()):
            rows.append({"model": model, "task": task, "metric": metric, **stats(values)})
        if artifact_values:
            rows.append({"model": model, "task": "QG/TMG/PCC", "metric": ARTIFACT_METRIC_NAME, **stats(artifact_values)})
        print(f"{model}: items={n_items} cells={len(by_cell)} artifact_n={len(artifact_values)}")

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
        "- `metric == \"artifact_composite\"`（task=QG/TMG/PCC）：三个产物类任务上 "
        "clarity_concision_inspiration + scenario_element_integration 的逐题两指标均值再取均值，"
        "对应 P18 教学产物生成 facet 的 task×metric 复合格子。\n"
        "- `sd` 为题级标准差，供 13 号检查的死格子（SD<0.5）判定参考。\n",
        encoding="utf-8",
    )
    print(f"rows: {len(rows)} -> {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
