#!/usr/bin/env python3
"""Generate full-model responses for EduEquity without judging them.

This runner keeps the prediction stage of the earlier ``run_edubench.py``
workflow: an OpenAI-compatible chat call, identical decoding settings across
items, concurrent execution, retries, incremental JSONL writes, and resumable
runs.  Dataset construction and LLM-as-a-Judge scoring are deliberately out of
scope here.

By default the script evaluates every row in
``data/eduequity/eduequity_prompts_flat_zh.jsonl`` (400 counterfactual pairs,
800 prompts).  Outputs for different models are isolated under
``reports/eval/eduequity/<model-slug>/``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from eval.minimax_client import MiniMaxClient
from eval.predictions_io import append_prediction, read_predictions, write_predictions
from eval.providers import PROVIDERS, build_client, model_slug, resolve_provider


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "data" / "eduequity" / "eduequity_prompts_flat_zh.jsonl"
DEFAULT_OUTPUT_ROOT = ROOT / "reports" / "eval" / "eduequity"

# Kept verbatim from the previous EduBench prediction implementation so the
# model receives the same educational-assistant role instruction.
DEFAULT_SYSTEM_PROMPT = "You are a helpful educational assistant."

REQUIRED_FIELDS = {
    "sample_id",
    "pair_id",
    "seed_id",
    "side",
    "edubench_task",
    "identity_axis",
    "prompt",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def prompt_sha256(system_prompt: str, prompt: str) -> str:
    payload = f"{system_prompt}\n\u241e\n{prompt}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def selection_sha256(rows: list[dict[str, Any]]) -> str:
    sample_ids = "\n".join(str(row["sample_id"]) for row in rows)
    return hashlib.sha256(sample_ids.encode("utf-8")).hexdigest()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid JSON at {path}:{line_number}: {exc}") from exc
            if not isinstance(row, dict):
                raise ValueError(f"expected a JSON object at {path}:{line_number}")
            missing = REQUIRED_FIELDS - row.keys()
            if missing:
                raise ValueError(
                    f"missing fields at {path}:{line_number}: {', '.join(sorted(missing))}"
                )
            rows.append(row)
    return rows


def validate_and_select_pairs(
    rows: list[dict[str, Any]],
    *,
    offset_pairs: int = 0,
    limit_pairs: int | None = None,
) -> list[dict[str, Any]]:
    """Validate A/B completeness and select whole pairs without splitting them."""
    sample_ids: set[str] = set()
    pair_order: list[str] = []
    by_pair: dict[str, list[dict[str, Any]]] = {}

    for row in rows:
        sample_id = str(row["sample_id"])
        pair_id = str(row["pair_id"])
        if sample_id in sample_ids:
            raise ValueError(f"duplicate sample_id: {sample_id}")
        sample_ids.add(sample_id)
        if pair_id not in by_pair:
            pair_order.append(pair_id)
            by_pair[pair_id] = []
        by_pair[pair_id].append(row)

    for pair_id, pair_rows in by_pair.items():
        sides = [str(row["side"]) for row in pair_rows]
        if len(pair_rows) != 2 or set(sides) != {"A", "B"}:
            raise ValueError(
                f"pair {pair_id} must contain exactly one A and one B row; got sides={sides}"
            )

    if offset_pairs < 0:
        raise ValueError("offset_pairs must be non-negative")
    selected_pair_ids = pair_order[offset_pairs:]
    if limit_pairs is not None:
        if limit_pairs < 0:
            raise ValueError("limit_pairs must be non-negative")
        selected_pair_ids = selected_pair_ids[:limit_pairs]
    selected = set(selected_pair_ids)
    return [row for row in rows if str(row["pair_id"]) in selected]


def parse_models(value: str) -> list[str]:
    models = [part.strip() for part in value.split(",") if part.strip()]
    if not models:
        raise argparse.ArgumentTypeError("--models must contain at least one model")
    if len(models) != len(set(models)):
        raise argparse.ArgumentTypeError("--models contains duplicate model names")
    return models


def prediction_succeeded(row: dict[str, Any]) -> bool:
    return bool(str(row.get("response") or "").strip()) and not row.get("error")


def latest_by_item(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {
        str(row["item_id"]): row
        for row in rows
        if row.get("item_id") is not None
    }


def build_messages(row: dict[str, Any], system_prompt: str) -> list[dict[str, str]]:
    """Reuse the previous EduBench two-message prediction format."""
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": str(row["prompt"])},
    ]


def generate_one(
    client: MiniMaxClient,
    model: str,
    row: dict[str, Any],
    *,
    system_prompt: str,
    timeout: int,
    retries: int,
    retry_sleep: float,
    max_tokens: int | None,
    save_reasoning: bool,
) -> dict[str, Any]:
    started = time.time()
    response = ""
    reasoning = ""
    error: str | None = None
    attempts = 0
    client.reset_usage_window()

    for attempt in range(retries + 1):
        attempts = attempt + 1
        try:
            response = client.chat(
                build_messages(row, system_prompt),
                model=model,
                max_tokens=max_tokens,
                timeout=timeout,
            )
            reasoning = client.read_last_reasoning()
            error = None
        except Exception as exc:  # noqa: BLE001 - persist failures for resumability
            response = ""
            reasoning = ""
            error = str(exc)
        if response.strip():
            break
        if attempt < retries and retry_sleep:
            time.sleep(retry_sleep * (2**attempt))

    result: dict[str, Any] = {
        "item_id": str(row["sample_id"]),
        "sample_id": str(row["sample_id"]),
        "pair_id": str(row["pair_id"]),
        "seed_id": str(row["seed_id"]),
        "side": str(row["side"]),
        "benchmark": "eduequity",
        "edubench_task": str(row["edubench_task"]),
        "subject": row.get("subject"),
        "education_level": row.get("education_level"),
        "identity_axis": str(row["identity_axis"]),
        "identity_label": row.get("identity_label"),
        "identity_value_zh": row.get("identity_value_zh"),
        "model": model,
        "system_prompt": system_prompt,
        "prompt": str(row["prompt"]),
        "prompt_sha256": prompt_sha256(system_prompt, str(row["prompt"])),
        "response": response,
        "latency_seconds": round(time.time() - started, 3),
        "attempts": attempts,
        "usage": client.read_usage_window(),
        "created_at": utc_now(),
    }
    if save_reasoning and reasoning:
        result["reasoning"] = reasoning
    if error:
        result["error"] = error
    elif not response.strip():
        result["empty_response"] = True
    return result


def write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(path)


def ensure_compatible_run(
    summary_path: Path,
    *,
    model: str,
    input_sha256: str,
    selected_sample_ids_sha256: str,
    system_prompt: str,
    provider_name: str,
    base_url: str,
    chat_path: str,
    temperature: float | None,
    max_tokens: int | None,
) -> None:
    """Refuse to append responses generated under a different configuration."""
    if not summary_path.exists():
        return
    try:
        prior = json.loads(summary_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise RuntimeError(f"cannot read existing run summary: {summary_path}") from exc
    checks = {
        "model": model,
        "input_sha256": input_sha256,
        "selected_sample_ids_sha256": selected_sample_ids_sha256,
        "system_prompt": system_prompt,
        "provider": provider_name,
        "base_url": base_url,
        "chat_path": chat_path,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    mismatches = [key for key, value in checks.items() if prior.get(key) != value]
    if mismatches:
        details = ", ".join(
            f"{key}: existing={prior.get(key)!r}, requested={checks[key]!r}"
            for key in mismatches
        )
        raise RuntimeError(
            f"refusing to mix incompatible predictions in {summary_path.parent}: {details}. "
            "Use a different --output-root."
        )


def run_model(
    model: str,
    selected_rows: list[dict[str, Any]],
    *,
    input_path: Path,
    input_sha256: str,
    output_root: Path,
    system_prompt: str,
    provider: str | None,
    base_url: str | None,
    api_key: str | None,
    api_key_env: str | None,
    chat_path: str | None,
    temperature: float | None,
    max_tokens: int | None,
    timeout: int,
    retries: int,
    retry_sleep: float,
    concurrency: int,
    resume: bool,
    save_reasoning: bool,
) -> dict[str, Any]:
    out_dir = output_root / model_slug(model)
    predictions_path = out_dir / "predictions.jsonl"
    summary_path = out_dir / "generation_summary.json"
    selected_ids_hash = selection_sha256(selected_rows)
    resolved_provider = PROVIDERS[provider] if provider else resolve_provider(model)
    resolved_base_url = base_url or resolved_provider.resolved_base_url()
    resolved_chat_path = chat_path or resolved_provider.chat_path

    ensure_compatible_run(
        summary_path,
        model=model,
        input_sha256=input_sha256,
        selected_sample_ids_sha256=selected_ids_hash,
        system_prompt=system_prompt,
        provider_name=resolved_provider.name,
        base_url=resolved_base_url,
        chat_path=resolved_chat_path,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    previous_rows = read_predictions(predictions_path)
    latest = latest_by_item(previous_rows)
    expected_ids = {str(row["sample_id"]) for row in selected_rows}
    pending = [
        row
        for row in selected_rows
        if not (
            resume
            and str(row["sample_id"]) in latest
            and prediction_succeeded(latest[str(row["sample_id"])])
        )
    ]

    started_at = utc_now()
    running_summary = {
        "benchmark": "eduequity",
        "stage": "generation_only",
        "judge_implemented": False,
        "model": model,
        "input": str(input_path),
        "input_sha256": input_sha256,
        "selected_sample_ids_sha256": selected_ids_hash,
        "system_prompt": system_prompt,
        "provider": resolved_provider.name,
        "base_url": resolved_base_url,
        "chat_path": resolved_chat_path,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "selected_pairs": len({str(row["pair_id"]) for row in selected_rows}),
        "selected_prompts": len(selected_rows),
        "pending_prompts_at_start": len(pending),
        "run_status": "running",
        "started_at": started_at,
    }
    write_json_atomic(summary_path, running_summary)

    print(
        f"model={model} selected={len(selected_rows)} pending={len(pending)} "
        f"cached_success={len(selected_rows) - len(pending)}"
    )
    if pending:
        client = build_client(
            model,
            timeout=timeout,
            provider=provider,
            base_url=base_url,
            api_key=api_key,
            api_key_env=api_key_env,
            chat_path=chat_path,
            temperature=temperature,
        )
        with ThreadPoolExecutor(max_workers=max(1, concurrency)) as executor:
            future_to_row = {
                executor.submit(
                    generate_one,
                    client,
                    model,
                    row,
                    system_prompt=system_prompt,
                    timeout=timeout,
                    retries=retries,
                    retry_sleep=retry_sleep,
                    max_tokens=max_tokens,
                    save_reasoning=save_reasoning,
                ): row
                for row in pending
            }
            for completed, future in enumerate(as_completed(future_to_row), start=1):
                result = future.result()
                append_prediction(predictions_path, result)
                latest[str(result["item_id"])] = result
                status = "ok" if prediction_succeeded(result) else "error"
                print(
                    f"generate {completed}/{len(pending)} model={model} "
                    f"item={result['item_id']} status={status}"
                )

    # Canonicalize to one latest row per selected item and restore dataset order.
    selected_item_ids = [str(row["sample_id"]) for row in selected_rows]
    canonical = [latest[item_id] for item_id in selected_item_ids if item_id in latest]
    write_predictions(predictions_path, canonical)
    successful = sum(prediction_succeeded(row) for row in canonical)
    empty = sum(bool(row.get("empty_response")) for row in canonical)
    errors = sum(bool(row.get("error")) for row in canonical)
    missing = len(expected_ids - set(latest))
    summary = {
        **running_summary,
        "run_status": "complete" if successful == len(selected_rows) else "incomplete",
        "completed_at": utc_now(),
        "successful_prompts": successful,
        "empty_prompts": empty,
        "error_prompts": errors,
        "missing_prompts": missing,
        "predictions": str(predictions_path),
    }
    write_json_atomic(summary_path, summary)
    print(
        f"saved model={model} success={successful}/{len(selected_rows)} "
        f"errors={errors} empty={empty} -> {predictions_path}"
    )
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate full EduEquity model responses; no LLM-as-a-Judge scoring."
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--models", type=parse_models, required=True, help="comma-separated model names")
    parser.add_argument("--system-prompt", default=DEFAULT_SYSTEM_PROMPT)
    parser.add_argument("--provider", choices=sorted(PROVIDERS), default=None)
    parser.add_argument("--base-url", default=None)
    parser.add_argument(
        "--api-key",
        default=None,
        help="API key passed at runtime; not persisted (environment variables are safer)",
    )
    parser.add_argument("--api-key-env", default=None)
    parser.add_argument("--chat-path", default=None)
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.0,
        help="greedy decoding by default, matching the previous EduBench runner",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=None,
        help="default uncapped; only set when an endpoint explicitly requires it",
    )
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--retry-sleep", type=float, default=1.0)
    parser.add_argument("--concurrency", type=int, default=4)
    parser.add_argument("--offset-pairs", type=int, default=0)
    parser.add_argument(
        "--limit-pairs",
        type=int,
        default=None,
        help="debugging only; unset runs all 400 pairs / 800 prompts",
    )
    parser.add_argument(
        "--no-resume",
        action="store_true",
        help="regenerate every selected prompt instead of skipping successful cached rows",
    )
    parser.add_argument(
        "--save-reasoning",
        action="store_true",
        help="persist provider-returned reasoning_content when available",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="validate input and print the first two complete pairs without API calls",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    rows = read_jsonl(args.input)
    selected_rows = validate_and_select_pairs(
        rows,
        offset_pairs=args.offset_pairs,
        limit_pairs=args.limit_pairs,
    )
    pair_count = len({str(row["pair_id"]) for row in selected_rows})
    print(
        f"validated input={args.input} rows={len(rows)}; "
        f"selected_pairs={pair_count} selected_prompts={len(selected_rows)}"
    )
    if args.dry_run:
        preview_pair_ids = []
        for row in selected_rows:
            pair_id = str(row["pair_id"])
            if pair_id not in preview_pair_ids:
                preview_pair_ids.append(pair_id)
            if len(preview_pair_ids) == 2:
                break
        preview = [row for row in selected_rows if str(row["pair_id"]) in preview_pair_ids]
        print(json.dumps(preview, ensure_ascii=False, indent=2))
        return

    source_hash = file_sha256(args.input)
    for model in args.models:
        run_model(
            model,
            selected_rows,
            input_path=args.input,
            input_sha256=source_hash,
            output_root=args.output_root,
            system_prompt=args.system_prompt,
            provider=args.provider,
            base_url=args.base_url,
            api_key=args.api_key,
            api_key_env=args.api_key_env,
            chat_path=args.chat_path,
            temperature=args.temperature,
            max_tokens=args.max_tokens,
            timeout=args.timeout,
            retries=args.retries,
            retry_sleep=args.retry_sleep,
            concurrency=args.concurrency,
            resume=not args.no_resume,
            save_reasoning=args.save_reasoning,
        )


if __name__ == "__main__":
    main()
