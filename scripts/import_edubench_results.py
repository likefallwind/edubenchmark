#!/usr/bin/env python3
"""Import standalone EduBench results into the standard reports/eval layout.

The source directory is treated as immutable. Per-model predictions and judge
records are joined by sample_id and written beneath
reports/eval/edubench/_judge-deepseek-v3.2 because the imported runs use the
historical deepseek-v3.2 judge rather than the repository-standard MiniMax-M3
judge.
EduBench uses continuous 0-10 judge scores, so accuracy/correct are deliberately
left null rather than inventing a binary threshold.
"""

from __future__ import annotations

import argparse
import csv
import html
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path
from statistics import fmean, stdev
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
HISTORICAL_JUDGE_SLUG = "deepseek-v3.2"
BUCKET_KEYS = ("lang", "task", "scenario", "subject", "difficulty")
DIMENSION_ALIASES = {
    "higher_order_ththinking_ability_development": "higher_order_thinking_ability_development",
    "basic_factural_accuracy": "basic_factual_accuracy",
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


def model_slug(name: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", name.strip()).strip("-")
    return slug or "model"


def judgment_path(source_dir: Path, model: str) -> Path:
    candidates = [
        source_dir / f"judgments_ds_{model}.jsonl",
        source_dir / f"judgments_ds_{model.replace('-', '')}.jsonl",
        source_dir / f"judgments_ds_{model.replace('glm-', 'glm')}.jsonl",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError(f"no judgment file found for model {model}")


def mean_ci(values: list[float]) -> dict[str, float | int | None]:
    values = [float(value) for value in values if isinstance(value, (int, float)) and math.isfinite(value)]
    if not values:
        return {"n": 0, "mean": None, "ci_lower": None, "ci_upper": None}
    mean = fmean(values)
    margin = 0.0 if len(values) < 2 else 1.96 * stdev(values) / math.sqrt(len(values))
    return {
        "n": len(values),
        "mean": mean,
        "ci_lower": max(0.0, mean - margin),
        "ci_upper": min(10.0, mean + margin),
    }


def grouped_metrics(rows: list[dict[str, Any]], key: str) -> dict[str, dict[str, float | int | None]]:
    values: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        if row["score_status"] == "scored":
            values[str(row["buckets"].get(key) or "unknown")].append(row["score"])
    return {group: mean_ci(scores) for group, scores in sorted(values.items())}


def dimension_metrics(rows: list[dict[str, Any]]) -> dict[str, dict[str, float | int | None]]:
    values: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        if row["score_status"] != "scored":
            continue
        for dimension, score in row.get("dimension_scores", {}).items():
            if isinstance(score, (int, float)):
                values[dimension].append(float(score))
    return {dimension: mean_ci(scores) for dimension, scores in sorted(values.items())}


def recover_dimension_scores(judgment: dict[str, Any]) -> tuple[dict[str, Any], int, int]:
    scores = dict(judgment.get("scores") or {})
    raw = judgment.get("raw_judge_output") or ""
    recovered = 0
    for alias, canonical in DIMENSION_ALIASES.items():
        current = scores.get(canonical)
        if isinstance(current, (int, float)) and math.isfinite(current):
            continue
        match = re.search(rf'"{re.escape(alias)}"\s*:\s*(-?\d+(?:\.\d+)?)', raw)
        if match:
            scores[canonical] = float(match.group(1))
            recovered += 1
    unresolved = sum(
        1 for value in scores.values()
        if isinstance(value, float) and not math.isfinite(value)
    )
    return scores, recovered, unresolved


def render_report(summary: dict[str, Any]) -> str:
    esc = lambda value: html.escape(str(value))
    extra = summary["extra_metrics"]
    overall = extra["overall"]

    def metric(value: Any) -> str:
        return "n/a" if value is None else f"{value:.3f}"

    def table(title: str, rows: dict[str, dict[str, Any]]) -> str:
        body = []
        for label, stats in rows.items():
            interval = "n/a" if stats["mean"] is None else f"{stats['ci_lower']:.3f} - {stats['ci_upper']:.3f}"
            body.append(
                f"<tr><td>{esc(label)}</td><td class='num'>{stats['n']}</td>"
                f"<td class='num'>{metric(stats['mean'])}</td><td class='num'>{interval}</td></tr>"
            )
        return (
            f"<section><h2>{esc(title)}</h2><table><thead><tr><th>Group</th><th>N</th>"
            "<th>Mean (0-10)</th><th>95% CI</th></tr></thead><tbody>"
            + "".join(body) + "</tbody></table></section>"
        )

    sections = [table("Dimension scores", extra["dimension_means"])]
    for key in BUCKET_KEYS:
        sections.append(table(f"By {key}", summary["by_bucket"][key]))
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>EduBench - {esc(summary['model'])}</title><style>
:root{{--ink:#17211b;--muted:#657068;--paper:#f6f1e7;--accent:#b64b2a;--line:#d7cdbd}}
*{{box-sizing:border-box}}body{{margin:0;background:linear-gradient(135deg,#efe6d6,#f9f6ef 55%,#e7eee5);color:var(--ink);font:15px/1.55 Georgia,'Times New Roman',serif}}
main{{max-width:1120px;margin:auto;padding:48px 24px 80px}}header{{border-top:8px solid var(--accent);padding:24px 0 16px}}h1{{font-size:clamp(34px,6vw,68px);line-height:.95;margin:0}}.sub{{color:var(--muted);margin-top:12px}}.cards{{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin:26px 0}}.card{{background:#fff9;border:1px solid var(--line);padding:18px}}.value{{font-size:30px;color:var(--accent)}}section{{margin-top:36px}}h2{{border-bottom:2px solid var(--ink);padding-bottom:6px}}table{{width:100%;border-collapse:collapse;background:#fffc}}th,td{{padding:9px 11px;border-bottom:1px solid var(--line);text-align:left}}th{{background:#ede5d6}}.num{{text-align:right;font-variant-numeric:tabular-nums}}.note{{color:var(--muted)}}
@media(max-width:700px){{.cards{{grid-template-columns:1fr}}table{{font-size:13px}}th,td{{padding:7px 5px}}}}
</style></head><body><main><header><h1>EduBench</h1><p class="sub">Model: {esc(summary['model'])} | Judge: {esc(extra['judge_model'] or 'unknown')}</p></header>
<div class="cards"><div class="card"><div class="value">{metric(overall['mean_overall_score'])}</div>Mean overall score</div><div class="card"><div class="value">{metric(overall['mean_scenario_score'])}</div>Mean scenario score</div><div class="card"><div class="value">{summary['scored']} / {summary['total_items']}</div>Scored items</div></div>
<p class="note">Scores are continuous LLM-as-Judge ratings on a 0-10 scale. They are not converted to accuracy. Confidence intervals use a normal 95% approximation.</p>
{''.join(sections)}</main></body></html>"""


def import_model(source_dir: Path, output_dir: Path, prediction_path: Path) -> dict[str, Any]:
    source_model = prediction_path.stem.removeprefix("predictions_")
    slug = model_slug(source_model)
    judgments_file = judgment_path(source_dir, source_model)
    judgments: dict[str, dict[str, Any]] = {}
    duplicate_judgments = 0
    for judgment in read_jsonl(judgments_file):
        item_id = str(judgment["sample_id"])
        if item_id in judgments:
            duplicate_judgments += 1
        judgments[item_id] = judgment

    predictions: list[dict[str, Any]] = []
    scored: list[dict[str, Any]] = []
    seen_predictions: Counter[str] = Counter()
    matched_ids: set[str] = set()
    recovered_dimension_scores = 0
    unresolved_dimension_scores = 0
    for prediction in read_jsonl(prediction_path):
        item_id = str(prediction["sample_id"])
        seen_predictions[item_id] += 1
        judgment = judgments.get(item_id)
        metadata = {key: prediction.get(key) for key in BUCKET_KEYS}
        metadata.update({"prompt": prediction.get("prompt"), "created_at": prediction.get("created_at")})
        predictions.append({"item_id": item_id, "model": slug, "response": prediction.get("response"), "metadata": metadata})
        if judgment:
            matched_ids.add(item_id)
            score = judgment.get("overall_score")
            status = "scored" if isinstance(score, (int, float)) else "invalid_judgment"
            dimension_scores, recovered, unresolved = recover_dimension_scores(judgment)
            recovered_dimension_scores += recovered
            unresolved_dimension_scores += unresolved
            row = {
                "item_id": item_id,
                "model": slug,
                "buckets": {key: prediction.get(key) for key in BUCKET_KEYS},
                "score_status": status,
                "score": float(score) if status == "scored" else None,
                "scenario_score": judgment.get("scenario_score"),
                "dimension_scores": dimension_scores,
                "judge_model": judgment.get("judge_model"),
                "rationale": judgment.get("rationale"),
                "raw_judge_output": judgment.get("raw_judge_output"),
                "response": prediction.get("response"),
                "prediction_created_at": prediction.get("created_at"),
                "judgment_created_at": judgment.get("created_at"),
            }
        else:
            row = {
                "item_id": item_id, "model": slug,
                "buckets": {key: prediction.get(key) for key in BUCKET_KEYS},
                "score_status": "missing_judgment", "score": None,
                "response": prediction.get("response"),
            }
        scored.append(row)

    status_counts = Counter(row["score_status"] for row in scored)
    valid = [row for row in scored if row["score_status"] == "scored"]
    overall_scores = [row["score"] for row in valid]
    scenario_scores = [float(row["scenario_score"]) for row in valid if isinstance(row.get("scenario_score"), (int, float))]
    judge_models = sorted({row.get("judge_model") for row in valid if row.get("judge_model")})
    summary = {
        "benchmark": "edubench",
        "model": slug,
        "total_items": len(predictions),
        "scored": len(valid),
        "correct": None,
        "accuracy": None,
        "status_counts": dict(sorted(status_counts.items())),
        "by_bucket": {key: grouped_metrics(scored, key) for key in BUCKET_KEYS},
        "extractor_model": None,
        "token_usage": {"prediction": None, "extraction": None, "total_tokens": None},
        "extra_metrics": {
            "metric_note": "Continuous LLM-as-Judge scores on a 0-10 scale; not accuracy.",
            "overall": {
                "mean_overall_score": mean_ci(overall_scores)["mean"],
                "mean_scenario_score": mean_ci(scenario_scores)["mean"],
            },
            "overall_score": mean_ci(overall_scores),
            "scenario_score": mean_ci(scenario_scores),
            "dimension_means": dimension_metrics(scored),
            "judge_model": judge_models[0] if len(judge_models) == 1 else judge_models,
            "audit": {
                "prediction_rows": len(predictions),
                "judgment_rows": len(judgments),
                "matched_rows": len(matched_ids),
                "missing_judgments": len(predictions) - len(matched_ids),
                "orphan_judgments": len(set(judgments) - matched_ids),
                "duplicate_prediction_ids": sum(count - 1 for count in seen_predictions.values() if count > 1),
                "duplicate_judgment_ids": duplicate_judgments,
                "recovered_dimension_scores": recovered_dimension_scores,
                "unresolved_dimension_scores": unresolved_dimension_scores,
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
    parser.add_argument("--source-dir", type=Path, default=ROOT / "edubench-results")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "reports" / "eval" / "edubench" / f"_judge-{HISTORICAL_JUDGE_SLUG}",
    )
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    summaries = []
    for prediction_path in sorted(args.source_dir.glob("predictions_*.jsonl")):
        summary = import_model(args.source_dir, args.output_dir, prediction_path)
        summaries.append(summary)
        audit = summary["extra_metrics"]["audit"]
        print(f"{summary['model']}: {summary['scored']}/{summary['total_items']} scored; missing={audit['missing_judgments']}; orphan={audit['orphan_judgments']}")

    csv_path = args.output_dir / "summary.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["model", "scored", "total_items", "mean_overall_score", "mean_scenario_score", "missing_judgments", "orphan_judgments"])
        for summary in summaries:
            overall = summary["extra_metrics"]["overall"]
            audit = summary["extra_metrics"]["audit"]
            writer.writerow([summary["model"], summary["scored"], summary["total_items"], overall["mean_overall_score"], overall["mean_scenario_score"], audit["missing_judgments"], audit["orphan_judgments"]])
    print(f"imported {len(summaries)} models -> {args.output_dir}")


if __name__ == "__main__":
    main()
