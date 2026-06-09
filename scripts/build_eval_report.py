#!/usr/bin/env python3
"""Rebuild the rich HTML eval report from an existing run directory.

No API calls: it reads ``scored.jsonl`` (+ ``summary.json`` if present) from a
finished run, re-loads the benchmark items for question text / images, and
re-renders ``report.html`` with the benchmark intro, sample questions, status
breakdown, and a wrong-answer gallery. Use it to enrich an old run's report or
to tune how many samples / wrong examples are shown.

Examples:
    # Rebuild in place (overwrites report.html in the run dir).
    python scripts/build_eval_report.py \\
        --benchmark mathvista --run-dir reports/eval/mathvista

    # Show more wrong examples, write to a separate file.
    python scripts/build_eval_report.py \\
        --benchmark mathvista --run-dir reports/eval/mathvista \\
        --num-wrong 10 --out report_full.html
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from eval.benchmarks import available_benchmarks, get_adapter
from eval.report import build_summary, read_jsonl, write_report

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--benchmark", required=True, help=f"one of: {', '.join(available_benchmarks())}")
    parser.add_argument("--run-dir", type=Path, required=True, help="run dir, e.g. reports/eval/mathvista")
    parser.add_argument("--out", default="report.html", help="output filename (relative to run-dir) or absolute path")
    parser.add_argument("--num-samples", type=int, default=2, help="example questions to show (default 2)")
    parser.add_argument("--num-wrong", type=int, default=6, help="wrong-answer examples to show (default 6)")
    args = parser.parse_args()

    run_dir = args.run_dir if args.run_dir.is_absolute() else (ROOT / args.run_dir)
    scored_path = run_dir / "scored.jsonl"
    if not scored_path.exists():
        raise SystemExit(f"no scored.jsonl in {run_dir} — run the eval first")

    adapter = get_adapter(args.benchmark)
    scored = read_jsonl(scored_path)
    items = adapter.load_items(limit=None)
    items_by_id = {str(it["item_id"]): it for it in items}

    summary_path = run_dir / "summary.json"
    if summary_path.exists():
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
    else:
        bucket_keys = list(adapter.buckets(items[0]).keys()) if items else []
        summary = build_summary(adapter.name, scored[0].get("model", "?") if scored else "?", scored, bucket_keys)

    out_path = Path(args.out) if Path(args.out).is_absolute() else (run_dir / args.out)
    write_report(
        out_path, summary, scored, items_by_id, adapter,
        num_samples=args.num_samples, num_wrong=args.num_wrong,
    )
    acc = summary.get("accuracy")
    print(f"wrote {out_path}  (accuracy={'n/a' if acc is None else f'{acc:.3f}'}, items={summary.get('total_items')})")


if __name__ == "__main__":
    main()
