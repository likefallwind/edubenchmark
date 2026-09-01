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
from eval.judge_dirs import judge_dir_name
from eval.providers import PROVIDERS, build_client, model_slug, resolve_model_params, resolve_provider
from eval.runner import run
from eval.suites import (
    SELECTION_SUITES,
    SUITES,
    federated_run_dirs,
    fixed_full_entry,
    load_manifest,
    run_dir,
    suite_item_list,
)


ROOT = Path(__file__).resolve().parents[1]


def _write_run_start_summary(
    out_dir: Path,
    *,
    benchmark: str,
    model: str,
    extractor_model: str,
    judge_model: str | None,
    judge_provenance: dict,
    generation_params: dict | None = None,
    no_images: bool = False,
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
            "每个裁判有自己的 judge-<judge>/ 目录；换裁判请让它自动分目录，或指定别的 --out-dir"
        )

    # Same hazard as mixing judges: predictions made with and without images are
    # different measurements and must never share a predictions.jsonl cache.
    requested_variant = "no_images" if no_images else "standard"
    previous_variant = existing.get("input_variant")
    if previous_variant and str(previous_variant) != requested_variant:
        raise SystemExit(
            f"refusing to mix input variants in {out_dir}: existing={previous_variant}, "
            f"requested={requested_variant}; the cached predictions were made under the other "
            "variant. Use the automatic _noimage/ directory or a different --out-dir."
        )

    started_at = datetime.now(timezone.utc).isoformat()
    metadata = {
        "benchmark": benchmark,
        "model": model,
        "extractor_model": extractor_model,
        "judge_model": judge_model,
        "input_variant": requested_variant,
        "run_status": "running",
        "started_at": started_at,
        # Recorded so a finished run can always be told apart from one made under
        # different sampling settings; "provider_default" means the field was omitted.
        "generation_params": generation_params or {},
        **judge_provenance,
    }
    if no_images:
        metadata["input_variant_note"] = (
            "图片已全部withheld，仅发送文本。分数是文本降级代理值，不代表该模型的多模态能力，"
            "也不可与标准 run 或视觉模型的成绩比较（图必需的题目在此变体下本就无解）。"
        )
    existing.pop("completed_at", None)
    existing.update(metadata)
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(existing, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)
    return {k: v for k, v in metadata.items() if k != "run_status"}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--benchmark", required=True, help=f"one of: {', '.join(available_benchmarks())}")
    parser.add_argument(
        "--suite",
        choices=SUITES,
        default="full",
        help="measurement suite (default full); mini/frontier resolve their frozen item lists",
    )
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
    parser.add_argument(
        "--temperature",
        type=float,
        default=(float(os.environ["TEMPERATURE"]) if os.environ.get("TEMPERATURE") else None),
        help=(
            "sampling temperature for the prediction model (env TEMPERATURE). "
            "Unset = omit the field and inherit the backend default (~1.0 for most "
            "OpenAI-compatible relays, but lower for some GLM routes); this is what "
            "every historical run in this repo did. Pass 0 for greedy, reproducible "
            "decoding when a run must be comparable with an external greedy-decoded run."
        ),
    )
    parser.add_argument(
        "--no-images",
        action="store_true",
        help=(
            "withhold every image from the model, sending text only. For probing a "
            "text-only model on a multimodal benchmark (e.g. glm-5.2, which 400s on "
            "image input). The resulting score is a DEGRADED PROXY, not a capability "
            "measure: items whose image carries essential information become "
            "unanswerable, so this is never comparable with a standard run nor with "
            "a vision model's score. Output is forced into a _noimage/ directory."
        ),
    )
    parser.add_argument("--skip-extract", action="store_true", help="only generate predictions, no extract/score")
    parser.add_argument("--score-only", action="store_true", help="reuse existing predictions; extract + score only")
    parser.add_argument("--dry-run", action="store_true", help="print constructed messages, no API calls")
    args = parser.parse_args()

    if args.suite != "full" and args.item_list is not None:
        parser.error("--suite mini_v2/frontier_v1 is mutually exclusive with --item-list")
    if args.suite != "full" and args.out_dir is not None:
        parser.error("--suite owns its result directory and is mutually exclusive with --out-dir")

    suite_manifest = None
    suite_fixed_full = None
    if args.suite in SELECTION_SUITES:
        suite_manifest = load_manifest(args.suite)
        suite_path = suite_item_list(args.suite, args.benchmark)
        suite_fixed_full = fixed_full_entry(args.suite, args.benchmark)
        if suite_path is not None:
            if "--limit" in sys.argv or "--offset" in sys.argv:
                parser.error("--suite mini_v2/frontier_v1 is mutually exclusive with --limit/--offset")
            args.item_list = suite_path
        elif suite_fixed_full:
            args.limit = 0
            args.offset = 0
        else:
            parser.error(f"benchmark {args.benchmark!r} is not a member of suite {args.suite!r}")

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
        if len(item_ids) != len(set(item_ids)):
            parser.error(f"--item-list {args.item_list} contains duplicate item_id values")
        try:
            list_path = str(args.item_list.resolve().relative_to(ROOT))
        except ValueError:
            list_path = str(args.item_list)
        item_list_info = {
            "item_list": list_path,
            "item_list_sha256": hashlib.sha256(raw.encode("utf-8")).hexdigest(),
            "item_list_count": len(item_ids),
        }
        if args.suite != "full":
            item_list_info.update(
                {
                    "suite": args.suite,
                    "suite_version": suite_manifest.get("version"),
                    "suite_manifest": str(
                        (ROOT / "data" / ("mini_selection_v2" if args.suite == "mini_v2" else "frontier_selection_v1") / "selection_manifest.json").relative_to(ROOT)
                    ),
                }
            )
    limit = None if args.limit is not None and args.limit <= 0 else args.limit
    extractor_model = args.extractor_model
    judge_model = adapter.resolved_judge_model(extractor_model)

    # Every judge gets its own namespace, the default one included: with several
    # judges in rotation a bare <model>/ directory would be unreadable without
    # knowing which judge was default when the run was made. Rule-scored
    # benchmarks have no judge and keep the plain <benchmark>/<model>/ shape.
    base_dir = ROOT / "reports" / "eval" / args.benchmark
    if args.suite in SELECTION_SUITES and not suite_fixed_full:
        out_dir = run_dir(
            args.suite,
            args.benchmark,
            model_slug(args.model),
            judge_model,
            variant="noimage" if args.no_images else None,
        )
    elif args.out_dir is not None:
        out_dir = args.out_dir
    elif judge_model:
        out_dir = base_dir / judge_dir_name(judge_model) / model_slug(args.model)
    else:
        out_dir = base_dir / model_slug(args.model)

    # --out-dir must not be a way to drop a judged run into the canonical result
    # tree without naming its judge: the whole point of judge-<judge>/ is that a
    # path can be read without knowing which judge was default that week.
    # Isolation trees (_baseline, _noimage, _smoke, _judge_rubric, ...) keep their
    # leading underscore and are exempt — they are already outside the model
    # tables, and run_reference_baseline.py legitimately writes into _baseline/.
    if args.out_dir is not None and judge_model:
        resolved = out_dir.resolve()
        eval_root = (ROOT / "reports" / "eval").resolve()
        inside_eval_tree = resolved == eval_root or eval_root in resolved.parents
        rel_parts = resolved.parts[len(eval_root.parts):] if inside_eval_tree else ()
        isolated = any(part.startswith("_") for part in rel_parts)
        named = any(part.startswith("judge-") for part in rel_parts)
        if inside_eval_tree and not isolated and not named:
            parser.error(
                f"--out-dir would hide the judge of a judged run: {out_dir}\n"
                f"This benchmark is scored by {judge_model}, so its results belong in "
                f"reports/eval/{args.benchmark}/{judge_dir_name(judge_model)}/<model>/. "
                "Drop --out-dir to get that path, include a judge-<judge> segment, use an "
                "underscore-prefixed isolation dir, or point --out-dir outside reports/eval/."
            )

    # A no-images run must never land in the canonical result tree: its score is a
    # degraded proxy and would be read as the model's real score. Auto-isolate the
    # default path, and refuse an explicit --out-dir that points back into
    # reports/eval/ without the marker.
    if args.no_images:
        if args.suite in SELECTION_SUITES and not suite_fixed_full:
            pass
        elif args.out_dir is None:
            out_dir = base_dir / "_noimage" / out_dir.relative_to(base_dir)
        else:
            resolved = out_dir.resolve()
            eval_root = (ROOT / "reports" / "eval").resolve()
            inside_eval_tree = resolved == eval_root or eval_root in resolved.parents
            if inside_eval_tree and "_noimage" not in resolved.parts:
                parser.error(
                    f"--no-images refuses to write into the canonical result tree: {out_dir}\n"
                    "Its score is a degraded proxy and must not sit where a standard run's is read. "
                    "Drop --out-dir to get the automatic _noimage/ path, include a _noimage segment, "
                    "or point --out-dir outside reports/eval/."
                )

    run_metadata = {}
    if not args.dry_run:
        run_metadata = _write_run_start_summary(
            out_dir,
            benchmark=args.benchmark,
            model=args.model,
            extractor_model=extractor_model,
            judge_model=judge_model,
            judge_provenance=adapter.judge_prompt_provenance(),
            generation_params={
                "temperature": "provider_default" if args.temperature is None else args.temperature,
                "max_tokens": "uncapped" if args.max_tokens is None else args.max_tokens,
            },
            no_images=args.no_images,
        )
        run_metadata["suite"] = "full" if suite_fixed_full else args.suite
        if suite_fixed_full:
            run_metadata["requested_suite"] = args.suite
            run_metadata["fixed_full_anchor"] = True

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
            temperature=args.temperature,
        )
        extractor_client = build_client(extractor_model, timeout=args.timeout)

    provider_spec = PROVIDERS[args.provider] if args.provider else resolve_provider(args.model)
    effective_provider = provider_spec.name
    effective_base_url = args.base_url or provider_spec.resolved_base_url()
    effective_chat_path = args.chat_path or provider_spec.chat_path
    effective_params = resolve_model_params(args.model, effective_provider)
    if args.temperature is not None:
        effective_params["temperature"] = args.temperature
    prediction_identity_context = {
        "schema_version": 1,
        "benchmark": args.benchmark,
        "model": args.model,
        "provider": effective_provider,
        "base_url": effective_base_url,
        "chat_path": effective_chat_path,
        "generation_params": effective_params,
        "max_tokens": args.max_tokens,
        "input_variant": "no_images" if args.no_images else "standard",
    }
    extractor_provider_spec = resolve_provider(extractor_model)
    extraction_identity_context = {
        "schema_version": 1,
        "benchmark": args.benchmark,
        "extractor_model": extractor_model,
        "extractor_provider": extractor_provider_spec.name,
        "extractor_base_url": extractor_provider_spec.resolved_base_url(),
        "extractor_chat_path": extractor_provider_spec.chat_path,
        "extractor_params": resolve_model_params(extractor_model, extractor_provider_spec.name),
        "judge_model": judge_model,
        "extraction_cache_version": getattr(adapter, "extraction_cache_version", None),
        "judge_provenance": adapter.judge_prompt_provenance(),
    }
    run_metadata.update(
        {
            "prediction_identity_schema": 1,
            "prediction_provider": effective_provider,
            "prediction_base_url": effective_base_url,
            "prediction_chat_path": effective_chat_path,
            "extraction_identity_schema": 1,
        }
    )
    reuse_dirs = federated_run_dirs(
        args.benchmark,
        model_slug(args.model),
        variant="noimage" if args.no_images else None,
    )

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
        no_images=args.no_images,
        prediction_identity_context=prediction_identity_context,
        extraction_identity_context=extraction_identity_context,
        reuse_dirs=reuse_dirs,
    )

    if summary:
        acc = summary.get("accuracy")
        print(f"\nbenchmark={summary['benchmark']} model={summary['model']}")
        print(f"scored={summary['scored']}/{summary['total_items']} accuracy={'n/a' if acc is None else f'{acc:.3f}'}")
        print(f"report={out_dir / 'report.html'}")
        if (
            (args.suite == "full" or suite_fixed_full)
            and not args.skip_extract
            and not args.no_images
        ):
            from materialize_eval_suites import materialize_benchmark

            for selection_suite in SELECTION_SUITES:
                if (
                    suite_item_list(selection_suite, args.benchmark) is None
                    and not fixed_full_entry(selection_suite, args.benchmark)
                ):
                    continue
                try:
                    view = materialize_benchmark(out_dir, selection_suite, args.benchmark)
                    print(
                        f"materialized {selection_suite}: "
                        f"{view.get('run_status')} {view.get('scored')}/{view.get('total_items')}"
                    )
                except Exception as exc:  # noqa: BLE001 - Full result remains valid
                    print(f"warning: could not materialize {selection_suite}: {exc}", file=sys.stderr)


if __name__ == "__main__":
    main()
