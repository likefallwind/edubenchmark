#!/usr/bin/env python3
"""Evaluate one benchmark against an API model (MiniMax to start).

Pipeline: load items -> call model (text [+ images]) -> LLM answer extraction
-> score -> write reports under reports/eval/<benchmark>/.

Examples:
    # Dry run: print the constructed messages for 3 items, no API calls.
    python scripts/eval_benchmark.py --benchmark mathvista --limit 3 --dry-run

    # Small sample against MiniMax-M3 (vision); reads MINIMAX_API_KEY from env.
    MINIMAX_API_KEY=... python scripts/eval_benchmark.py \\
        --benchmark mathvista --limit 30 --model MiniMax-M3 --concurrency 2

    # Re-score existing predictions without re-querying the model.
    python scripts/eval_benchmark.py --benchmark mathvista --limit 30 --score-only
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from eval.benchmarks import available_benchmarks, get_adapter
from eval.minimax_client import DEFAULT_MODEL
from eval.providers import PROVIDERS, build_client, model_slug
from eval.runner import run


ROOT = Path(__file__).resolve().parents[1]
CANONICAL_JUDGE_MODEL = "MiniMax-M3"


def _write_run_start_summary(
    out_dir: Path,
    *,
    benchmark: str,
    model: str,
    extractor_model: str,
    judge_model: str | None,
    judge_provenance: dict,
) -> dict:
    """Persist run identity before clients, datasets, or predictions can fail."""
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "summary.json"
    existing: dict = {}
    if path.exists():
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                existing = loaded
        except (json.JSONDecodeError, OSError):
            pass

    previous_judge = existing.get("judge_model")
    if not previous_judge and isinstance(existing.get("extra_metrics"), dict):
        previous_judge = existing["extra_metrics"].get("judge_model")
    if previous_judge and judge_model and str(previous_judge) != str(judge_model):
        raise SystemExit(
            f"refusing to mix judge models in {out_dir}: existing={previous_judge}, requested={judge_model}; "
            "use the automatic _judge-<model>/ directory or a different --out-dir"
        )

    started_at = datetime.now(timezone.utc).isoformat()
    metadata = {
        "benchmark": benchmark,
        "model": model,
        "extractor_model": extractor_model,
        "judge_model": judge_model,
        "run_status": "running",
        "started_at": started_at,
        **judge_provenance,
    }
    existing.pop("completed_at", None)
    existing.update(metadata)
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(existing, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)
    return {k: v for k, v in metadata.items() if k != "run_status"}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--benchmark", required=True, help=f"one of: {', '.join(available_benchmarks())}")
    parser.add_argument("--limit", type=int, default=30, help="number of items (default 30; 0/negative = all)")
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument(
        "--item-list",
        type=Path,
        default=None,
        help=(
            "file with one native item_id per line; run exactly these items "
            "(mutually exclusive with --limit/--offset). The list path, sha256 "
            "and count are recorded in summary.json for sampling provenance."
        ),
    )
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument(
        "--extractor-model",
        default="MiniMax-M2.7",
        help="model for answer extraction; text-only step so a cheaper text model is fine (default: MiniMax-M2.7)",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="output directory (default: reports/eval/<benchmark>/<model-slug>)",
    )
    parser.add_argument(
        "--provider",
        choices=sorted(PROVIDERS),
        default=None,
        help="force the prediction provider (default: resolved from --model; minimax/gateway)",
    )
    parser.add_argument("--base-url", default=None, help="override prediction provider base URL")
    parser.add_argument("--api-key-env", default=None, help="override env var holding the prediction API key")
    parser.add_argument("--chat-path", default=None, help="override prediction chat path (e.g. /chat/completions)")
    parser.add_argument("--concurrency", type=int, default=4)
    parser.add_argument(
        "--extract-concurrency",
        type=int,
        default=1,
        help="parallel extraction/judge calls (default 1; raise for LLM-judge benchmarks like eduguard_adversarial)",
    )
    parser.add_argument(
        "--language",
        choices=["en", "zh", "both"],
        default="both",
        help="dataset language for bilingual benchmarks (currently eduguard_sata; default both)",
    )
    parser.add_argument("--sleep", type=float, default=0.2)
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--retry-sleep", type=float, default=1.0)
    parser.add_argument(
        "--rate-limit-threshold",
        type=int,
        default=int(os.environ.get("RATE_LIMIT_THRESHOLD", "10")),
        help="consecutive rate-limit (429/throttle) errors before sleeping (env RATE_LIMIT_THRESHOLD; default 10)",
    )
    parser.add_argument(
        "--rate-limit-sleep",
        type=float,
        default=float(os.environ.get("RATE_LIMIT_SLEEP", "1800")),
        help="seconds to sleep when throttling is detected (env RATE_LIMIT_SLEEP; default 1800 = 30 min)",
    )
    parser.add_argument(
        "--rate-limit-max-retries",
        type=int,
        default=int(os.environ.get("RATE_LIMIT_MAX_RETRIES", "3")),
        help="max times a single rate-limited item is re-queued (env RATE_LIMIT_MAX_RETRIES; default 3)",
    )
    parser.add_argument("--max-tokens", type=int, default=None)
    parser.add_argument("--skip-extract", action="store_true", help="only generate predictions, no extract/score")
    parser.add_argument("--score-only", action="store_true", help="reuse existing predictions; extract + score only")
    parser.add_argument("--dry-run", action="store_true", help="print constructed messages, no API calls")
    args = parser.parse_args()

    adapter = get_adapter(args.benchmark)
    if hasattr(adapter, "language"):
        adapter.language = args.language
    # Adapters that call the model-under-test outside the prediction phase
    # (e.g. p07_selfcheck's round-2 revision call) need its name; the extractor
    # client passed to extract_answer is a different model.
    adapter.model_under_test = args.model

    item_ids = None
    item_list_info = None
    if args.item_list is not None:
        if "--limit" in sys.argv or "--offset" in sys.argv:
            parser.error("--item-list is mutually exclusive with --limit/--offset")
        raw = args.item_list.read_text(encoding="utf-8")
        item_ids = [line.strip() for line in raw.splitlines() if line.strip()]
        if not item_ids:
            parser.error(f"--item-list {args.item_list} is empty")
        try:
            list_path = str(args.item_list.resolve().relative_to(ROOT))
        except ValueError:
            list_path = str(args.item_list)
        item_list_info = {
            "item_list": list_path,
            "item_list_sha256": hashlib.sha256(raw.encode("utf-8")).hexdigest(),
            "item_list_count": len(item_ids),
        }
    limit = None if args.limit is not None and args.limit <= 0 else args.limit
    extractor_model = args.extractor_model
    judge_model = adapter.resolved_judge_model(extractor_model)

    # The benchmark's canonical judge uses the ordinary model directory;
    # alternate judges get their own namespace so scoring caches and summaries
    # can never overwrite one another. Most adapters inherit MiniMax-M3, while
    # an adapter may name its established historical judge explicitly.
    base_dir = ROOT / "reports" / "eval" / args.benchmark
    canonical_judge = adapter.canonical_judge_model or CANONICAL_JUDGE_MODEL
    if args.out_dir is not None:
        out_dir = args.out_dir
    elif judge_model and model_slug(judge_model) != model_slug(canonical_judge):
        out_dir = base_dir / f"_judge-{model_slug(judge_model)}" / model_slug(args.model)
    else:
        out_dir = base_dir / model_slug(args.model)

    run_metadata = {}
    if not args.dry_run:
        run_metadata = _write_run_start_summary(
            out_dir,
            benchmark=args.benchmark,
            model=args.model,
            extractor_model=extractor_model,
            judge_model=judge_model,
            judge_provenance=adapter.judge_prompt_provenance(),
        )

    # Predictions and extraction use separate clients: the prediction model may
    # live on the gateway while the extractor (MiniMax-M2.7) stays on MiniMax.
    if args.dry_run:
        client = None
        extractor_client = None
    else:
        client = build_client(
            args.model,
            timeout=args.timeout,
            provider=args.provider,
            base_url=args.base_url,
            api_key_env=args.api_key_env,
            chat_path=args.chat_path,
        )
        extractor_client = build_client(extractor_model, timeout=args.timeout)

    summary = run(
        adapter=adapter,
        out_dir=out_dir,
        model=args.model,
        extractor_model=extractor_model,
        judge_model=judge_model,
        limit=limit,
        offset=args.offset,
        concurrency=args.concurrency,
        sleep_seconds=args.sleep,
        timeout=args.timeout,
        retries=args.retries,
        retry_sleep=args.retry_sleep,
        max_tokens=args.max_tokens,
        skip_extract=args.skip_extract,
        score_only=args.score_only,
        dry_run=args.dry_run,
        client=client,
        extractor_client=extractor_client,
        extract_concurrency=args.extract_concurrency,
        rate_limit_threshold=args.rate_limit_threshold,
        rate_limit_sleep=args.rate_limit_sleep,
        rate_limit_max_retries=args.rate_limit_max_retries,
        item_ids=item_ids,
        item_list_info=item_list_info,
        run_metadata=run_metadata,
    )

    if summary:
        acc = summary.get("accuracy")
        print(f"\nbenchmark={summary['benchmark']} model={summary['model']}")
        print(f"scored={summary['scored']}/{summary['total_items']} accuracy={'n/a' if acc is None else f'{acc:.3f}'}")
        print(f"report={out_dir / 'report.html'}")


if __name__ == "__main__":
    main()
