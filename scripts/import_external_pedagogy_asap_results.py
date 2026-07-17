#!/usr/bin/env python3
"""Normalize the 2026-07-17 external Pedagogy and ASAP 2.0 results.

The source package is immutable and model-first.  This importer writes the
repository's benchmark-first layout and deliberately removes duplicated API
envelopes from the large raw files while retaining the model response, parsed
prediction, gold label, scoring status, retry count, usage, and source checksum.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "otherbenchmark" / "benchmark_raw_results_by_model_20260717"
DEFAULT_OUTPUT = ROOT / "reports" / "eval"
BENCHMARKS = {
    "pedagogy": ("pedagogy_benchmark", "Pedagogy Benchmark", "accuracy"),
    "asap2": ("asap_2", "ASAP 2.0", "qwk"),
}


def read_jsonl(path: Path) -> Iterable[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number}: invalid JSON: {exc}") from exc


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def model_slug(name: str) -> str:
    if name == "MiniMax-M3":
        return "minimax3"
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", name.strip()).strip("-")
    return slug or "model"


def item_id(benchmark: str, row: dict[str, Any]) -> str:
    if benchmark == "pedagogy":
        task = str(row.get("benchmark", "pedagogy")).removeprefix("pedagogy/")
        return f"{task}:{row.get('category')}:{row.get('local_index')}"
    return str(row["essay_id"])


def weighted_kappa(gold: list[int], predicted: list[int]) -> float | None:
    """Quadratic weighted Cohen kappa, implemented without third-party deps."""
    if not gold or len(gold) != len(predicted):
        return None
    labels = list(range(min(gold + predicted), max(gold + predicted) + 1))
    if len(labels) < 2:
        return 1.0
    index = {label: i for i, label in enumerate(labels)}
    observed = [[0] * len(labels) for _ in labels]
    gold_counts = [0] * len(labels)
    pred_counts = [0] * len(labels)
    for actual, guess in zip(gold, predicted):
        i, j = index[actual], index[guess]
        observed[i][j] += 1
        gold_counts[i] += 1
        pred_counts[j] += 1
    denominator = float((len(labels) - 1) ** 2)
    observed_weighted = 0.0
    expected_weighted = 0.0
    n = len(gold)
    for i in range(len(labels)):
        for j in range(len(labels)):
            weight = (i - j) ** 2 / denominator
            observed_weighted += weight * observed[i][j] / n
            expected_weighted += weight * gold_counts[i] * pred_counts[j] / (n * n)
    if expected_weighted == 0:
        return 1.0 if observed_weighted == 0 else None
    return 1.0 - observed_weighted / expected_weighted


def usage_from(row: dict[str, Any]) -> dict[str, int]:
    usage = {
        "prompt_tokens": int(row.get("usage_prompt_tokens") or 0),
        "completion_tokens": int(row.get("usage_completion_tokens") or 0),
        "reasoning_tokens": int(row.get("usage_reasoning_tokens") or 0),
        "total_tokens": int(row.get("usage_total_tokens") or 0),
    }
    return usage


def sum_usage(rows: list[dict[str, Any]]) -> dict[str, int]:
    keys = ("prompt_tokens", "completion_tokens", "reasoning_tokens", "total_tokens")
    total = {key: 0 for key in keys}
    for row in rows:
        usage = row["usage"]
        for key in keys:
            total[key] += usage[key]
    total["calls"] = sum(int(row.get("n_attempts") or 0) for row in rows)
    total["items_with_usage"] = sum(row["usage"]["total_tokens"] > 0 for row in rows)
    return total


def accuracy_bucket(rows: list[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[str(row["buckets"].get(key) or "unknown")].append(row)
    result = {}
    for label, values in sorted(groups.items()):
        scored = [row for row in values if row["score_status"] == "scored"]
        correct = sum(row["correct"] is True for row in scored)
        result[label] = {
            "total": len(values), "scored": len(scored), "correct": correct,
            "accuracy": correct / len(scored) if scored else None,
        }
    return result


def qwk_bucket(rows: list[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[str(row["buckets"].get(key) or "unknown")].append(row)
    result = {}
    for label, values in sorted(groups.items()):
        scored = [row for row in values if row["score_status"] == "scored"]
        result[label] = {
            "total": len(values),
            "scored": len(scored),
            "qwk": weighted_kappa(
                [int(row["gold"]) for row in scored],
                [int(row["extracted"]) for row in scored],
            ),
        }
    return result


def render_report(summary: dict[str, Any]) -> str:
    esc = lambda value: html.escape(str(value))
    metric_name = summary["primary_metric"]["name"].upper()
    metric = summary["primary_metric"]["value"]
    metric_text = "n/a" if metric is None else f"{metric:.4f}"
    bucket_key = next(iter(summary["by_bucket"]), None)
    bucket_rows = []
    if bucket_key:
        for label, stats in summary["by_bucket"][bucket_key].items():
            value = stats.get(summary["primary_metric"]["name"])
            value_text = "n/a" if value is None else f"{value:.4f}"
            bucket_rows.append(
                f"<tr><td>{esc(label)}</td><td>{stats['scored']}/{stats['total']}</td>"
                f"<td>{value_text}</td></tr>"
            )
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(summary['benchmark'])} - {esc(summary['model'])}</title>
<style>body{{font:15px/1.5 system-ui,sans-serif;max-width:980px;margin:40px auto;padding:0 20px;color:#17202a}}h1{{margin-bottom:4px}}.note{{color:#687078}}.cards{{display:flex;gap:14px;margin:24px 0}}.card{{border:1px solid #d8dde3;border-radius:8px;padding:16px;min-width:180px}}.value{{font-size:30px;font-weight:700}}table{{border-collapse:collapse;width:100%}}th,td{{border-bottom:1px solid #ddd;padding:8px;text-align:left}}</style></head>
<body><h1>{esc(summary['benchmark'])}</h1><div class="note">Imported external run · model {esc(summary['model'])}</div>
<div class="cards"><div class="card"><div class="value">{metric_text}</div>{metric_name}</div><div class="card"><div class="value">{summary['scored']}/{summary['total_items']}</div>Scored</div></div>
<p class="note">Source: {esc(summary['provenance']['source_file'])}<br>SHA-256: {esc(summary['provenance']['source_sha256'])}</p>
<h2>By {esc(bucket_key or 'bucket')}</h2><table><tr><th>Group</th><th>Scored/Total</th><th>{metric_name}</th></tr>{''.join(bucket_rows)}</table></body></html>"""


def convert_rows(benchmark: str, source_rows: list[dict[str, Any]], model: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    predictions = []
    scored = []
    for source in source_rows:
        iid = item_id(benchmark, source)
        usage = usage_from(source)
        prediction = {
            "item_id": iid,
            "model": model,
            "response": source.get("raw_response"),
            "extracted": source.get("prediction"),
            "bad_format": bool(source.get("bad_format")),
            "attempts": int(source.get("n_attempts") or 0),
            "error": source.get("error") or "",
            "usage": usage,
        }
        predictions.append(prediction)
        if benchmark == "pedagogy":
            buckets = {
                "task": str(source.get("benchmark", "")).removeprefix("pedagogy/"),
                "category": source.get("category"),
            }
            valid = source.get("prediction") is not None and not source.get("error")
            correct = bool(source.get("correct")) if valid else None
        else:
            buckets = {"prompt": source.get("prompt_name"), "split": source.get("split")}
            valid = isinstance(source.get("prediction"), int) and not source.get("error")
            correct = None
        scored.append({
            "item_id": iid,
            "model": model,
            "buckets": buckets,
            "score_status": "scored" if valid else "error",
            "correct": correct,
            "extracted": source.get("prediction"),
            "normalized": source.get("prediction"),
            "gold": source.get("gold"),
            "response": source.get("raw_response"),
            "bad_format": bool(source.get("bad_format")),
            "attempts": int(source.get("n_attempts") or 0),
            "error": source.get("error") or "",
            "usage": usage,
        })
    return predictions, scored


def import_run(source_file: Path, benchmark: str, model_name: str, output_root: Path) -> dict[str, Any]:
    benchmark_id, _title, metric_name = BENCHMARKS[benchmark]
    slug = model_slug(model_name)
    source_rows = list(read_jsonl(source_file))
    predictions, scored = convert_rows(benchmark, source_rows, model_name)
    ids = [row["item_id"] for row in scored]
    duplicate_ids = sum(count - 1 for count in Counter(ids).values() if count > 1)
    if duplicate_ids:
        raise ValueError(f"{source_file}: {duplicate_ids} duplicate item IDs")
    valid = [row for row in scored if row["score_status"] == "scored"]
    if benchmark == "pedagogy":
        correct = sum(row["correct"] is True for row in valid)
        metric_value = correct / len(valid) if valid else None
        by_bucket = {
            "task": accuracy_bucket(scored, "task"),
            "category": accuracy_bucket(scored, "category"),
        }
        accuracy = metric_value
    else:
        correct = None
        metric_value = weighted_kappa(
            [int(row["gold"]) for row in valid],
            [int(row["extracted"]) for row in valid],
        )
        by_bucket = {"prompt": qwk_bucket(scored, "prompt")}
        accuracy = None
    status_counts = Counter(row["score_status"] for row in scored)
    summary = {
        "benchmark": benchmark_id,
        "model": model_name,
        "total_items": len(scored),
        "scored": len(valid),
        "correct": correct,
        "accuracy": accuracy,
        "status_counts": dict(sorted(status_counts.items())),
        "by_bucket": by_bucket,
        "extractor_model": None,
        "token_usage": {"prediction": sum_usage(predictions), "extraction": None, "total_tokens": sum_usage(predictions)["total_tokens"]},
        "primary_metric": {"name": metric_name, "value": metric_value},
        "extra_metrics": {
            "overall": {metric_name: metric_value},
            "bad_format_rate": sum(row["bad_format"] for row in scored) / len(scored) if scored else None,
            "retry_attempts": sum(max(0, row["attempts"] - 1) for row in scored),
            "estimated_usd": sum(float(row.get("estimated_usd") or 0) for row in source_rows),
            "metric_note": "ASAP 2.0 uses quadratic weighted kappa; accuracy is intentionally null." if benchmark == "asap2" else "Pedagogy Benchmark multiple-choice accuracy.",
        },
        "provenance": {
            "imported_from_external_package": True,
            "package_date": "2026-07-17",
            "source_file": str(source_file.relative_to(ROOT)),
            "source_sha256": sha256(source_file),
            "source_rows": len(source_rows),
            "duplicate_item_ids": duplicate_ids,
            "normalization": "Removed duplicated API envelopes; retained raw model response, parsed prediction, gold, score status, retries, usage, and errors.",
        },
    }
    run_dir = output_root / benchmark_id / slug
    run_dir.mkdir(parents=True, exist_ok=True)
    write_jsonl(run_dir / "predictions.jsonl", predictions)
    write_jsonl(run_dir / "scored.jsonl", scored)
    (run_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (run_dir / "report.html").write_text(render_report(summary) + "\n", encoding="utf-8")
    return summary


def write_benchmark_index(output_root: Path, benchmark: str, summaries: list[dict[str, Any]]) -> None:
    benchmark_id, title, metric_name = BENCHMARKS[benchmark]
    bench_dir = output_root / benchmark_id
    with (bench_dir / "summary.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["model", "total_items", "scored", metric_name, "bad_format_rate", "total_tokens", "estimated_usd", "source_file", "source_sha256"])
        for summary in sorted(summaries, key=lambda row: row["model"].lower()):
            writer.writerow([
                summary["model"], summary["total_items"], summary["scored"], summary["primary_metric"]["value"],
                summary["extra_metrics"]["bad_format_rate"], summary["token_usage"]["total_tokens"],
                summary["extra_metrics"]["estimated_usd"], summary["provenance"]["source_file"], summary["provenance"]["source_sha256"],
            ])
    note = "Accuracy over 1,119 multiple-choice items." if benchmark == "pedagogy" else "Quadratic weighted kappa (QWK) over the ASAP 2.0 test split; invalid/error rows are excluded from QWK and remain visible in status counts."
    (bench_dir / "README.md").write_text(
        f"# {title} — imported evaluation artifacts\n\n"
        "These runs were produced by another team and imported from "
        "`otherbenchmark/benchmark_raw_results_by_model_20260717/`. The source package is treated as immutable.\n\n"
        f"Primary metric: {note}\n\n"
        "Each model directory contains `predictions.jsonl`, `scored.jsonl`, `summary.json`, and `report.html`. "
        "The normalized JSONL keeps raw model text and all scoring-relevant fields, but omits duplicated nested API response envelopes. "
        "`summary.json` records the original path and SHA-256 for traceability.\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    source = args.source.resolve()
    output_root = args.output_root.resolve()
    if not (source / "runs").is_dir():
        raise SystemExit(f"missing source runs directory: {source / 'runs'}")
    imported: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for model_dir in sorted(path for path in (source / "runs").iterdir() if path.is_dir()):
        for benchmark in BENCHMARKS:
            details = model_dir / f"{benchmark}_details.jsonl"
            if not details.exists():
                continue
            summary = import_run(details, benchmark, model_dir.name, output_root)
            imported[benchmark].append(summary)
            print(f"{summary['benchmark']}/{model_slug(summary['model'])}: {summary['scored']}/{summary['total_items']} {summary['primary_metric']['name']}={summary['primary_metric']['value']}")
    for benchmark, summaries in imported.items():
        write_benchmark_index(output_root, benchmark, summaries)
    print(f"imported {sum(map(len, imported.values()))} model-runs into {output_root}")


if __name__ == "__main__":
    main()
