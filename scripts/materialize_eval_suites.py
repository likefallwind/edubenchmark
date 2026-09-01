#!/usr/bin/env python3
"""Materialize mini_v2/frontier_v1 views from completed Full evidence.

This command never calls a model or judge. It filters a completed Full run by
the frozen suite item list, recomputes benchmark-native aggregates, and writes a
standalone suite result tree with explicit source provenance.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from eval.predictions_io import read_predictions, write_predictions  # noqa: E402
from eval.providers import model_slug  # noqa: E402
from eval.report import (  # noqa: E402
    aggregate_token_usage,
    build_summary,
    read_jsonl,
    write_jsonl,
    write_report,
)
from eval.suites import (  # noqa: E402
    SELECTION_SUITES,
    fixed_full_entry,
    load_manifest,
    run_dir,
    suite_item_list,
)


def _rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def _copy_if_present(source: Path, target: Path) -> None:
    if source.is_file():
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


def _fixed_full_view(
    source_dir: Path, target_dir: Path, suite: str, benchmark: str
) -> dict[str, Any]:
    source_summary = json.loads((source_dir / "summary.json").read_text(encoding="utf-8"))
    target_dir.mkdir(parents=True, exist_ok=True)
    predictions = read_predictions(source_dir)
    if predictions:
        write_predictions(target_dir, predictions)
    for name in ("extractions.jsonl", "scored.jsonl", "report.html", "pairwise_judgments.jsonl"):
        _copy_if_present(source_dir / name, target_dir / name)
    fixed = fixed_full_entry(suite, benchmark) or {}
    expected = int(fixed.get("count") or 0)
    complete = source_summary.get("run_status") in (None, "complete")
    complete = complete and int(source_summary.get("total_items") or 0) == expected
    if benchmark == "eduillustrate":
        complete = complete and (
            int(source_summary.get("judged") or 0)
            + int(source_summary.get("render_failures") or 0)
            == expected
        )
    summary = {
        **source_summary,
        "suite": suite,
        "suite_version": load_manifest(suite).get("version"),
        "fixed_full_anchor": True,
        "materialized_from": _rel(source_dir),
        "materialized_at": datetime.now(timezone.utc).isoformat(),
        "expected_suite_items": expected,
        "run_status": "complete" if complete else "incomplete",
    }
    if not complete:
        summary.pop("completed_at", None)
    (target_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    report_path = target_dir / "report.html"
    if report_path.is_file():
        report = report_path.read_text(encoding="utf-8", errors="ignore")
        label = (
            f"<section style='border:2px solid #b7791f;padding:1rem;margin:1rem'>"
            f"<strong>测量套件：{suite}</strong> · fixed-full anchor；"
            "该套件结果与同一次 Full 测量相同，不是一次重复模型调用。</section>"
        )
        marker = "<main>" if "<main>" in report else "<body>"
        report = report.replace(marker, marker + label, 1)
        report_path.write_text(report, encoding="utf-8")
    return summary


def _get_adapter(benchmark: str):
    """Load adapters lazily so fixed-full workflows need no adapter extras."""
    from eval.benchmarks import get_adapter

    return get_adapter(benchmark)


def materialize_benchmark(source_dir: Path, suite: str, benchmark: str) -> dict[str, Any]:
    """Create one suite view from one completed Full result directory."""
    source_dir = source_dir.resolve()
    summary_path = source_dir / "summary.json"
    if not summary_path.is_file():
        raise FileNotFoundError(f"missing Full summary: {summary_path}")
    source_summary = json.loads(summary_path.read_text(encoding="utf-8"))
    if source_summary.get("run_status") not in (None, "complete"):
        raise ValueError(f"Full run is not complete: {source_dir}")

    model = str(source_summary.get("model") or source_dir.name)
    judge_model = source_summary.get("judge_model")
    target_dir = run_dir(suite, benchmark, model_slug(model), judge_model)
    if fixed_full_entry(suite, benchmark):
        return _fixed_full_view(source_dir, target_dir, suite, benchmark)

    item_list = suite_item_list(suite, benchmark)
    if item_list is None:
        raise ValueError(f"{benchmark!r} is not in {suite!r}")
    raw_list = item_list.read_text(encoding="utf-8")
    item_ids = [line.strip() for line in raw_list.splitlines() if line.strip()]
    wanted = set(item_ids)
    adapter = _get_adapter(benchmark)
    all_items = adapter.load_items(limit=None, offset=0)
    items = [item for item in all_items if str(item["item_id"]) in wanted]
    missing_dataset = wanted - {str(item["item_id"]) for item in items}
    if missing_dataset:
        raise ValueError(f"{benchmark}: {len(missing_dataset)} suite ids missing from dataset")

    predictions = {str(row["item_id"]): row for row in read_predictions(source_dir) if row.get("item_id") is not None}
    extractions = {str(row["item_id"]): row for row in read_jsonl(source_dir / "extractions.jsonl") if row.get("item_id") is not None}
    scored = {str(row["item_id"]): row for row in read_jsonl(source_dir / "scored.jsonl") if row.get("item_id") is not None}
    selected_predictions = [predictions[item_id] for item_id in item_ids if item_id in predictions]
    selected_extractions = [extractions[item_id] for item_id in item_ids if item_id in extractions]
    selected_scored = [scored[item_id] for item_id in item_ids if item_id in scored]
    missing_predictions = [item_id for item_id in item_ids if item_id not in predictions]
    missing_extractions = [item_id for item_id in item_ids if item_id not in extractions]
    missing_scored = [item_id for item_id in item_ids if item_id not in scored]
    missing = list(
        dict.fromkeys(missing_predictions + missing_extractions + missing_scored)
    )

    target_dir.mkdir(parents=True, exist_ok=True)
    write_predictions(target_dir, selected_predictions)
    write_jsonl(target_dir / "extractions.jsonl", selected_extractions)
    write_jsonl(target_dir / "scored.jsonl", selected_scored)

    bucket_keys = list(adapter.buckets(items[0]).keys()) if items else []
    summary = build_summary(benchmark, model, selected_scored, bucket_keys)
    summary.update(
        {
            "extractor_model": source_summary.get("extractor_model"),
            "judge_model": judge_model,
            "suite": suite,
            "suite_version": load_manifest(suite).get("version"),
            "suite_manifest": _rel(item_list.parent / "selection_manifest.json"),
            "item_list": _rel(item_list),
            "item_list_sha256": hashlib.sha256(raw_list.encode("utf-8")).hexdigest(),
            "item_list_count": len(item_ids),
            "materialized_from": _rel(source_dir),
            "materialized_at": datetime.now(timezone.utc).isoformat(),
            "missing_item_count": len(missing),
            "missing_item_ids": missing,
            "missing_prediction_count": len(missing_predictions),
            "missing_extraction_count": len(missing_extractions),
            "missing_scored_count": len(missing_scored),
            "run_status": "complete" if not missing else "incomplete",
            "token_usage": aggregate_token_usage(selected_predictions, selected_extractions),
            "execution_stats": {
                "predictions": {"cached_in_target": 0, "reused_cross_suite": len(selected_predictions), "new_prediction_calls": 0},
                "extractions": {"cached_in_target": 0, "reused_cross_suite": len(selected_extractions), "new_extraction_calls": 0},
            },
        }
    )
    for key in ("input_variant", "generation_params", "judge_prompt_version", "judge_prompt_sha256"):
        if key in source_summary:
            summary[key] = source_summary[key]
    extra_metrics = adapter.extra_summary(selected_scored)
    if extra_metrics:
        summary["extra_metrics"] = extra_metrics
    if not missing:
        summary["completed_at"] = datetime.now(timezone.utc).isoformat()
    (target_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    items_by_id = {str(item["item_id"]): item for item in items}
    write_report(target_dir / "report.html", summary, selected_scored, items_by_id, adapter)
    return summary


def _full_source_dirs(benchmark: str, slug: str) -> list[Path]:
    base = ROOT / "reports" / "eval" / benchmark
    found = []
    if (base / slug / "summary.json").is_file():
        found.append(base / slug)
    if base.is_dir():
        found.extend(sorted(p / slug for p in base.glob("judge-*") if (p / slug / "summary.json").is_file()))
    return found


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True)
    parser.add_argument("--suites", nargs="+", choices=SELECTION_SUITES, default=list(SELECTION_SUITES))
    parser.add_argument("--benchmarks", nargs="*", default=None)
    args = parser.parse_args()
    benchmarks = args.benchmarks or sorted(
        set().union(*(set(load_manifest(suite).get("benchmarks", {})) | {row["benchmark"] for row in load_manifest(suite).get("fixed_full", [])} for suite in args.suites))
    )
    from eval.benchmarks import available_benchmarks

    adapter_names = set(available_benchmarks())
    failures = []
    for benchmark in benchmarks:
        sources = _full_source_dirs(benchmark, model_slug(args.model))
        if not sources:
            failures.append(f"{benchmark}: no completed Full source found")
            continue
        for source in sources:
            for suite in args.suites:
                if suite_item_list(suite, benchmark) is None and not fixed_full_entry(suite, benchmark):
                    continue
                if benchmark not in adapter_names and not fixed_full_entry(suite, benchmark):
                    failures.append(f"{benchmark}: no adapter")
                    continue
                try:
                    summary = materialize_benchmark(source, suite, benchmark)
                    print(f"{suite}/{benchmark}/{source.name}: {summary.get('run_status')} {summary.get('scored')}/{summary.get('total_items')}")
                except Exception as exc:  # noqa: BLE001 - batch command reports every failure
                    failures.append(f"{suite}/{benchmark}/{source.name}: {exc}")
    if failures:
        print("materialization warnings:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)


if __name__ == "__main__":
    main()
