#!/usr/bin/env python3
"""Import a standalone SAS-Bench run into the standard reports/eval layout.

The source directory (`otherbenchmark/sas-bench`, produced by a colleague's own
runner) is treated as immutable. Per-model item rows and the raw grader output
are joined by item id and written beneath reports/eval/sas_bench.

SAS-Bench asks the model to *grade* a student's step-by-step answer, so the
"prediction" is a grading decision: a holistic score plus a per-step score and
error-cause list. The headline metrics (QWK / CCS / ECS) are population
statistics over a subtask, not per-item scores, so accuracy/correct are left
null rather than inventing a binary threshold.

Metric provenance: QWK/CCS/ECS are carried from the run logs, which is what the
0630 report tabulated. QWK is independently recomputed here from manual_label
vs pred_label as an audit check. CCS/ECS are NOT recomputed here: a step-level
QWK reimplementation lands close to but not exactly on the logged CCS, so the
logged values stay authoritative and audit.ccs_ecs_independently_verified
records that they are unverified.

That flag is a TODO, not a dead end: the official scorer IS available locally at
sources/datasets/sas_bench (utils/collaborative_consistency_score.py,
utils/errors_consistency_score.py, driven by sas_pipelines/3_compute_ccs.py and
4_compute_ecs.py). Wiring those in would verify CCS/ECS the same way QWK is
verified now.
"""

from __future__ import annotations

import argparse
import csv
import html
import json
import re
from collections import Counter
from pathlib import Path
from statistics import fmean
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
BUCKET_KEYS = ("task", "subject", "question_type")
METRIC_KEYS = ("qwk", "ccs", "ecs")
ECS_BREAKDOWN_KEYS = ("ecs_low", "ecs_medium", "ecs_high")

# Source run-log per model directory. The logs end with a JSON block holding the
# per-subtask n/qwk/ccs/ecs produced by the colleague's scorer.
LOG_BY_MODEL = {
    "deepseek-v4-pro": "deepseek.log",
    "doubao-seed-2.0-pro": "doubao-pro.log",
    "glm-5.1": "glm.log",
    "gpt-5.4": "gpt.log",
    "kimi-k2.6": "kimi.log",
    "minimax-m2.7": "minimax-m2.7.log",
    "minimax-m3": "minimax-m3.log",
}


def read_jsonl(path: Path) -> Iterable[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if line.strip():
                try:
                    yield json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(f"{path}:{line_number}: invalid JSON: {exc}") from exc


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def model_slug(source_dir_name: str) -> str:
    name = source_dir_name.removeprefix("SAS-Bench_").removesuffix("_Scored")
    return name.replace("_", "-").lower()


def split_task(task: str) -> tuple[str, str]:
    """`0_Physics_ShortAns` -> ("Physics", "ShortAns")."""
    parts = task.split("_", 2)
    return (parts[1], parts[2]) if len(parts) >= 3 else ("unknown", "unknown")


def read_raw_grader_output(path: Path) -> dict[str, str]:
    """`*_scored.jsonl` is TSV: item id, tab, JSON-encoded raw grader text."""
    raw: dict[str, str] = {}
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            item_id, _, payload = line.rstrip("\n").partition("\t")
            if not payload:
                raise ValueError(f"{path}:{line_number}: expected id<TAB>payload")
            try:
                raw[item_id] = json.loads(payload)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number}: invalid JSON payload: {exc}") from exc
    return raw


def parse_log_metrics(path: Path) -> dict[str, dict[str, float]]:
    text = path.read_text(encoding="utf-8", errors="replace")
    start = text.rfind("\n{\n")
    if start < 0:
        raise ValueError(f"{path}: no trailing JSON metric block found")
    return json.loads(text[start:])


def quadratic_weighted_kappa(gold: list[int], pred: list[int]) -> float | None:
    if not gold:
        return None
    lo = min(min(gold), min(pred))
    hi = max(max(gold), max(pred))
    values = list(range(lo, hi + 1))
    index = {value: i for i, value in enumerate(values)}
    size = len(values)
    if size < 2:
        return None
    observed = [[0] * size for _ in range(size)]
    gold_hist = [0] * size
    pred_hist = [0] * size
    for g, p in zip(gold, pred):
        observed[index[g]][index[p]] += 1
        gold_hist[index[g]] += 1
        pred_hist[index[p]] += 1
    total = len(gold)
    numerator = denominator = 0.0
    for i in range(size):
        for j in range(size):
            weight = ((i - j) ** 2) / ((size - 1) ** 2)
            numerator += weight * observed[i][j]
            denominator += weight * gold_hist[i] * pred_hist[j] / total
    return 1.0 - numerator / denominator if denominator else None


def as_int(value: Any) -> int | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return int(round(value))


def render_report(summary: dict[str, Any]) -> str:
    esc = lambda value: html.escape(str(value))
    extra = summary["extra_metrics"]
    overall = extra["overall"]

    def metric(value: Any) -> str:
        return "n/a" if value is None else f"{value:.2f}"

    rows = []
    for task, stats in extra["by_task"].items():
        rows.append(
            f"<tr><td>{esc(task)}</td><td class='num'>{stats['n']}</td>"
            f"<td class='num'>{metric(stats['qwk'])}</td>"
            f"<td class='num'>{metric(stats['ccs'])}</td>"
            f"<td class='num'>{metric(stats['ecs'])}</td></tr>"
        )
    audit = extra["audit"]
    delta = audit["qwk_recompute_max_abs_delta"]
    verify = (
        f"QWK independently recomputed from manual_label vs pred_label; "
        f"max |delta| vs run log = {delta:.4f} over {audit['qwk_recomputed_tasks']} subtasks."
        if delta is not None else "QWK recomputation unavailable."
    )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>SAS-Bench - {esc(summary['model'])}</title><style>
:root{{--ink:#17211b;--muted:#657068;--paper:#f6f1e7;--accent:#b64b2a;--line:#d7cdbd}}
*{{box-sizing:border-box}}body{{margin:0;background:linear-gradient(135deg,#efe6d6,#f9f6ef 55%,#e7eee5);color:var(--ink);font:15px/1.55 Georgia,'Times New Roman',serif}}
main{{max-width:1120px;margin:auto;padding:48px 24px 80px}}header{{border-top:8px solid var(--accent);padding:24px 0 16px}}h1{{font-size:clamp(34px,6vw,68px);line-height:.95;margin:0}}.sub{{color:var(--muted);margin-top:12px}}.cards{{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin:26px 0}}.card{{background:#fff9;border:1px solid var(--line);padding:18px}}.value{{font-size:30px;color:var(--accent)}}section{{margin-top:36px}}h2{{border-bottom:2px solid var(--ink);padding-bottom:6px}}table{{width:100%;border-collapse:collapse;background:#fffc}}th,td{{padding:9px 11px;border-bottom:1px solid var(--line);text-align:left}}th{{background:#ede5d6}}.num{{text-align:right;font-variant-numeric:tabular-nums}}.note{{color:var(--muted)}}
@media(max-width:700px){{.cards{{grid-template-columns:1fr}}table{{font-size:13px}}th,td{{padding:7px 5px}}}}
</style></head><body><main><header><h1>SAS-Bench</h1><p class="sub">Model: {esc(summary['model'])} | Role: grader of student step-by-step answers</p></header>
<div class="cards"><div class="card"><div class="value">{metric(overall['qwk'])}</div>QWK (holistic total score)</div><div class="card"><div class="value">{metric(overall['ccs'])}</div>CCS (step scoring consistency)</div><div class="card"><div class="value">{metric(overall['ecs'])}</div>ECS (error-cause consistency)</div></div>
<p class="note">Headline values are the unweighted mean over the {len(extra['by_task'])} subtasks, on a 0-100 scale; this is the aggregation the 0630 report used. They are agreement statistics against human expert labels, not accuracy. {esc(verify)} CCS/ECS are carried from the run log and are not independently reproduced here.</p>
<section><h2>By subtask</h2><table><thead><tr><th>Subtask</th><th>N</th><th>QWK</th><th>CCS</th><th>ECS</th></tr></thead><tbody>{''.join(rows)}</tbody></table></section>
</main></body></html>"""


def import_model(source_dir: Path, output_dir: Path, model_dir: Path) -> dict[str, Any]:
    slug = model_slug(model_dir.name)
    log_name = LOG_BY_MODEL.get(slug)
    if log_name is None:
        raise KeyError(f"no run log mapped for model {slug}")
    log_metrics = parse_log_metrics(source_dir / log_name)

    predictions: list[dict[str, Any]] = []
    scored: list[dict[str, Any]] = []
    seen_ids: Counter[str] = Counter()
    missing_raw = 0
    by_task: dict[str, dict[str, Any]] = {}
    qwk_deltas: list[float] = []

    for prediction_path in sorted(
        model_dir.glob("*_prediction.jsonl"),
        key=lambda path: int(path.name.split("_", 1)[0]),
    ):
        task = prediction_path.name.removesuffix("_prediction.jsonl")
        subject, question_type = split_task(task)
        raw_outputs = read_raw_grader_output(model_dir / f"{task}_scored.jsonl")
        gold_totals: list[int] = []
        pred_totals: list[int] = []

        for row in read_jsonl(prediction_path):
            item_id = str(row["id"])
            seen_ids[item_id] += 1
            raw_output = raw_outputs.get(item_id)
            if raw_output is None:
                missing_raw += 1
            buckets = {"task": task, "subject": subject, "question_type": question_type}
            gold_steps = row.get("steps") or []
            pred_steps = row.get("pred_steps") or []

            # The full source item is preserved verbatim: stem, reference answer,
            # worked analysis, the student's step-by-step response, and the human
            # expert labels. Re-scoring or swapping the grader needs all of it.
            predictions.append(
                {
                    "item_id": item_id,
                    "model": slug,
                    "response": raw_output,
                    "metadata": {
                        **buckets,
                        "question": row.get("question"),
                        "reference": row.get("reference"),
                        "analysis": row.get("analysis"),
                        "total": row.get("total"),
                        "manual_label": row.get("manual_label"),
                        "steps": gold_steps,
                    },
                }
            )

            manual_label = as_int(row.get("manual_label"))
            pred_label = as_int(row.get("pred_label"))
            if manual_label is not None and pred_label is not None:
                gold_totals.append(manual_label)
                pred_totals.append(pred_label)
                status = "scored"
            else:
                status = "invalid_grading"
            scored.append(
                {
                    "item_id": item_id,
                    "model": slug,
                    "buckets": buckets,
                    "score_status": status,
                    "total": row.get("total"),
                    "manual_label": row.get("manual_label"),
                    "pred_label": row.get("pred_label"),
                    "step_gold": [
                        {"label": step.get("label"), "errors": step.get("errors") or []}
                        for step in gold_steps
                    ],
                    "step_pred": [
                        {"step_score": step.get("step_score"), "errors": step.get("errors") or []}
                        for step in pred_steps
                    ],
                    "step_count_match": len(gold_steps) == len(pred_steps),
                    "raw_grader_output": raw_output,
                }
            )

        logged = log_metrics.get(task, {})
        recomputed = quadratic_weighted_kappa(gold_totals, pred_totals)
        logged_qwk = logged.get("qwk")
        if recomputed is not None and isinstance(logged_qwk, (int, float)):
            qwk_deltas.append(abs(recomputed * 100.0 - logged_qwk * 100.0))
        by_task[task] = {
            "n": logged.get("n"),
            "n_imported": len(gold_totals),
            **{key: (logged[key] * 100.0 if isinstance(logged.get(key), (int, float)) else None) for key in METRIC_KEYS},
            **{key: (logged[key] * 100.0 if isinstance(logged.get(key), (int, float)) else None) for key in ECS_BREAKDOWN_KEYS},
            "qwk_recomputed": recomputed * 100.0 if recomputed is not None else None,
        }

    def macro(key: str) -> float | None:
        values = [stats[key] for stats in by_task.values() if stats[key] is not None]
        return fmean(values) if values else None

    status_counts = Counter(row["score_status"] for row in scored)
    summary = {
        "benchmark": "sas_bench",
        "model": slug,
        "total_items": len(predictions),
        "scored": status_counts.get("scored", 0),
        "correct": None,
        "accuracy": None,
        "status_counts": dict(sorted(status_counts.items())),
        "by_bucket": {
            "task": {
                task: {"n": stats["n_imported"], **{key: stats[key] for key in METRIC_KEYS}}
                for task, stats in by_task.items()
            }
        },
        "extractor_model": None,
        "judge_model": None,
        "token_usage": {"prediction": None, "extraction": None, "total_tokens": None},
        "extra_metrics": {
            "metric_note": (
                "QWK/CCS/ECS are agreement statistics against human expert labels on a "
                "0-100 scale, computed per subtask over the item population; they are not "
                "accuracy and there is no per-item score."
            ),
            "headline_metric": "unweighted mean of the per-subtask value over all subtasks (the 0630 report's aggregation)",
            "overall": {key: macro(key) for key in METRIC_KEYS},
            "overall_ecs_breakdown": {key: macro(key) for key in ECS_BREAKDOWN_KEYS},
            "by_task": by_task,
            "audit": {
                "prediction_rows": len(predictions),
                "raw_grader_rows": len(predictions) - missing_raw,
                "missing_raw_grader_output": missing_raw,
                "duplicate_item_ids": sum(count - 1 for count in seen_ids.values() if count > 1),
                "step_count_mismatches": sum(1 for row in scored if not row["step_count_match"]),
                "qwk_recomputed_tasks": len(qwk_deltas),
                "qwk_recompute_max_abs_delta": max(qwk_deltas) if qwk_deltas else None,
                "ccs_ecs_independently_verified": False,
                "metric_provenance": f"otherbenchmark/sas-bench/{log_name} (colleague's run log)",
            },
        },
    }

    run_dir = output_dir / slug
    run_dir.mkdir(parents=True, exist_ok=True)
    write_jsonl(run_dir / "predictions.jsonl", predictions)
    write_jsonl(run_dir / "scored.jsonl", scored)
    (run_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (run_dir / "report.html").write_text(render_report(summary) + "\n", encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, default=ROOT / "otherbenchmark" / "sas-bench")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "reports" / "eval" / "sas_bench")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    summaries = []
    for model_dir in sorted(args.source_dir.glob("SAS-Bench_*_Scored")):
        summary = import_model(args.source_dir, args.output_dir, model_dir)
        summaries.append(summary)
        overall = summary["extra_metrics"]["overall"]
        audit = summary["extra_metrics"]["audit"]
        print(
            f"{summary['model']}: {summary['scored']}/{summary['total_items']} scored; "
            f"qwk={overall['qwk']:.2f} ccs={overall['ccs']:.2f} ecs={overall['ecs']:.2f}; "
            f"qwk_recompute_max_delta={audit['qwk_recompute_max_abs_delta']:.4f}"
        )

    csv_path = args.output_dir / "summary.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["model", "scored", "total_items", "qwk", "ccs", "ecs"])
        for summary in summaries:
            overall = summary["extra_metrics"]["overall"]
            writer.writerow(
                [summary["model"], summary["scored"], summary["total_items"],
                 overall["qwk"], overall["ccs"], overall["ecs"]]
            )
    print(f"imported {len(summaries)} models -> {args.output_dir}")


if __name__ == "__main__":
    main()
