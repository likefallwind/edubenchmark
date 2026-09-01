"""Generic evaluation loop: predict -> extract -> score -> report.

Resumable and incremental: ``predictions.jsonl`` and ``extractions.jsonl`` are
keyed by ``item_id``; already-completed items are skipped on rerun. Each
completed item is appended to disk immediately (never a full-file rewrite), so
a crash mid-run loses nothing. Retried items append a fresh row; readers
dedupe via ``_index_by_item`` where the last row per ``item_id`` wins.
"""

from __future__ import annotations

import json
import hashlib
import time
from datetime import datetime, timezone
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from pathlib import Path
from typing import Any

from .base import BenchmarkAdapter
from .minimax_client import MiniMaxClient
from .report import (
    aggregate_token_usage,
    append_jsonl,
    build_summary,
    read_jsonl,
    write_jsonl,
    write_report,
)
from .predictions_io import append_prediction, read_predictions, write_predictions


def _index_by_item(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(r["item_id"]): r for r in rows if r.get("item_id") is not None}


def _sha256_json(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def prediction_fingerprints(
    adapter: BenchmarkAdapter,
    item: dict[str, Any],
    identity_context: dict[str, Any],
    no_images: bool = False,
) -> tuple[str, str, list[dict[str, Any]]]:
    """Fingerprint the exact rendered request and its measurement identity."""
    messages = adapter.build_messages(item)
    if no_images:
        messages = strip_image_parts(messages)
    item_fingerprint = _sha256_json({"item_id": str(item["item_id"]), "messages": messages})
    identity = _sha256_json({**identity_context, "item_fingerprint": item_fingerprint})
    return item_fingerprint, identity, messages


def extraction_identity(
    prediction: dict[str, Any],
    identity_context: dict[str, Any],
) -> str:
    return _sha256_json(
        {
            **identity_context,
            "prediction_identity_sha256": prediction.get("prediction_identity_sha256"),
            "response_sha256": hashlib.sha256(
                str(prediction.get("response") or "").encode("utf-8")
            ).hexdigest(),
        }
    )


def _reason(error: str | None, limit: int = 300) -> str:
    """Render an error string as a ` reason=...` suffix for the run log (eval.log)."""
    if not error:
        return ""
    text = " ".join(str(error).split())
    return f" reason={text[:limit]!r}"


def _is_rate_limit_error(error: str | None) -> bool:
    """Heuristic: does this error string look like API throttling (vs. a real bug)?

    Covers HTTP 429 and the MiniMax ``base_resp`` rate-limit status codes 1002
    (QPS/concurrency limit), 1039 (TPM limit), and 2062 (Token Plan rate limit),
    plus generic English/Chinese phrasings.
    """
    if not error:
        return False
    low = error.lower()
    if "http 429" in low or "too many requests" in low or "rate limit" in low:
        return True
    # MiniMax surfaces throttling in Chinese: "限流" (throttled) and the Token
    # Plan quota message "已达到 Token Plan 速率限制".
    if "限流" in error or "速率限制" in error or "token plan" in low:
        return True
    return "base_resp 1002" in low or "base_resp 1039" in low or "base_resp 2062" in low


class RateLimitGuard:
    """Detect sustained throttling and wait it out instead of burning items.

    A single 429 is transient; ``threshold`` of them in a row (with no success
    in between) means the API is throttling us, so sleeping ``sleep_seconds``
    (default 30 min) and retrying is far more productive than recording the
    whole batch as errors. Any non-rate-limit result resets the streak.

    Rate-limited items are re-queued for another attempt, capped at
    ``max_retries`` per item so a mis-classified persistent error cannot loop
    forever.
    """

    def __init__(self, threshold: int, sleep_seconds: float, max_retries: int) -> None:
        self.threshold = max(1, threshold)
        self.sleep_seconds = sleep_seconds
        self.max_retries = max(0, max_retries)
        self.streak = 0
        self._retries: dict[str, int] = {}

    def reset_streak(self) -> None:
        """Call on any non-rate-limit result (success or other error)."""
        self.streak = 0

    def on_rate_limit(self, item_id: str) -> bool:
        """Record a rate-limit error. Returns True if the item should be re-queued.

        Sleeps once the consecutive-error streak reaches ``threshold``.
        """
        self.streak += 1
        if self.streak >= self.threshold:
            mins = self.sleep_seconds / 60
            print(
                f"!! {self.streak} consecutive rate-limit errors — likely throttled; "
                f"sleeping {mins:.0f} min then retrying",
                flush=True,
            )
            time.sleep(self.sleep_seconds)
            self.streak = 0
        seen = self._retries.get(item_id, 0)
        if seen >= self.max_retries:
            return False
        self._retries[item_id] = seen + 1
        return True


def _truncate_messages(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Replace base64 image payloads with a short placeholder for printing."""
    safe = []
    for message in messages:
        content = message.get("content")
        if isinstance(content, list):
            parts = []
            for part in content:
                if part.get("type") == "image_url":
                    url = (part.get("image_url") or {}).get("url", "")
                    parts.append({"type": "image_url", "image_url": {"url": f"<{len(url)} chars base64>"}})
                else:
                    parts.append(part)
            safe.append({"role": message.get("role"), "content": parts})
        else:
            safe.append(message)
    return safe


def strip_image_parts(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Drop every ``image_url`` content part, leaving the text as-is.

    Applied *after* ``build_messages`` so it covers all adapters uniformly —
    including the eight that override ``build_messages`` (k12vista and
    mmtutorbench among them), which a flag inside ``BenchmarkAdapter`` would
    silently miss. Opt-in only (``--no-images``); see that flag's help text for
    why the resulting scores are a degraded proxy and not a capability measure.
    """
    stripped = []
    for message in messages:
        content = message.get("content")
        if isinstance(content, list):
            parts = [p for p in content if p.get("type") != "image_url"]
            stripped.append({**message, "content": parts})
        else:
            stripped.append(message)
    return stripped


def _predict_one(
    adapter: BenchmarkAdapter,
    item: dict[str, Any],
    client: MiniMaxClient,
    model: str,
    timeout: int,
    retries: int,
    retry_sleep: float,
    max_tokens: int | None,
    no_images: bool = False,
    identity_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    item_fingerprint, identity, messages = prediction_fingerprints(
        adapter, item, identity_context or {}, no_images
    )
    started = time.time()
    client.reset_usage_window()
    response = ""
    reasoning = ""
    error: str | None = None
    attempts = 0
    for attempt in range(retries + 1):
        attempts = attempt + 1
        try:
            response = client.chat(messages, model=model, max_tokens=max_tokens, timeout=timeout)
            reasoning = client.read_last_reasoning()
            error = None
        except Exception as exc:  # noqa: BLE001 - record and retry
            response = ""
            reasoning = ""
            error = str(exc)
        if response.strip():
            break
        if attempt < retries and retry_sleep:
            time.sleep(retry_sleep * (attempt + 1))
    row = {
        "item_id": str(item["item_id"]),
        "model": model,
        "response": response,
        "latency_seconds": round(time.time() - started, 3),
        "attempts": attempts,
        "usage": client.read_usage_window(),
        "item_fingerprint": item_fingerprint,
        "prediction_identity_sha256": identity,
    }
    # Preserve the model's chain-of-thought when the provider returns it. On the
    # streaming path (harness default) this includes gpt-5.5 via LIGHTER as well
    # as MiniMax-M3 / DeepSeek-R1 / GLM; when no text is returned, the
    # reasoning_tokens count in ``usage`` is still the trace of the thinking.
    if reasoning:
        row["reasoning"] = reasoning
    if error:
        row["error"] = error
    elif not response.strip():
        row["empty_response"] = True
    return row


def run_predictions(
    adapter: BenchmarkAdapter,
    items: list[dict[str, Any]],
    client: MiniMaxClient,
    out_path: Path,
    model: str,
    concurrency: int,
    sleep_seconds: float,
    timeout: int,
    retries: int,
    retry_sleep: float,
    max_tokens: int | None,
    rate_limit_threshold: int = 10,
    rate_limit_sleep: float = 1800.0,
    rate_limit_max_retries: int = 3,
    no_images: bool = False,
    identity_context: dict[str, Any] | None = None,
    reuse_dirs: list[Path] | None = None,
    allow_new: bool = True,
) -> tuple[dict[str, dict[str, Any]], dict[str, int]]:
    # Treat errored / empty predictions as not-done so reruns retry only those.
    identity_context = identity_context or {}
    expected = {
        str(item["item_id"]): prediction_fingerprints(adapter, item, identity_context, no_images)[:2]
        for item in items
    }

    def valid(row: dict[str, Any], *, cross_dir: bool) -> bool:
        item_id = str(row.get("item_id"))
        if not str(row.get("response") or "").strip() or row.get("error") or row.get("empty_response"):
            return False
        stored = row.get("prediction_identity_sha256")
        if cross_dir and not stored:
            return False
        return not stored or stored == expected.get(item_id, (None, None))[1]

    existing = {
        k: v
        for k, v in _index_by_item(read_predictions(out_path)).items()
        if k in expected and valid(v, cross_dir=False)
    }
    reused = 0
    target_dir = out_path.parent.resolve()
    for source_dir in reuse_dirs or []:
        source_dir = source_dir.resolve()
        if source_dir == target_dir:
            continue
        for item_id, row in _index_by_item(read_predictions(source_dir)).items():
            if item_id in existing or item_id not in expected or not valid(row, cross_dir=True):
                continue
            existing[item_id] = {**row, "reused_from": str(source_dir)}
            reused += 1
    pending = [it for it in items if str(it["item_id"]) not in existing]
    missing_without_calls = len(pending) if not allow_new else 0
    if not allow_new:
        pending = []
    rows = list(existing.values())
    print(f"predictions: {len(existing)} cached, {len(pending)} to run")

    guard = RateLimitGuard(rate_limit_threshold, rate_limit_sleep, rate_limit_max_retries)
    concurrency = max(1, concurrency)
    completed = 0
    api_calls = 0
    if concurrency == 1:
        idx = 0
        while idx < len(pending):
            item = pending[idx]
            idx += 1
            row = _predict_one(
                adapter, item, client, model, timeout, retries, retry_sleep, max_tokens, no_images,
                identity_context,
            )
            api_calls += int(row.get("attempts") or 1)
            if _is_rate_limit_error(row.get("error")):
                if guard.on_rate_limit(str(row["item_id"])):
                    pending.append(item)
                    print(f"predict item={row['item_id']} rate-limited -> re-queued{_reason(row.get('error'))}")
                    continue
            else:
                guard.reset_streak()
            rows.append(row)
            append_prediction(out_path, row)
            completed += 1
            status = "error" if row.get("error") else ("empty" if row.get("empty_response") else "ok")
            detail = _reason(row.get("error")) if status == "error" else ""
            print(f"predict {completed}/{len(pending)} item={row['item_id']} status={status}{detail}")
            if sleep_seconds:
                time.sleep(sleep_seconds)
    else:
        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            in_flight: dict[Any, dict[str, Any]] = {}
            idx = 0
            while idx < len(pending) or in_flight:
                while idx < len(pending) and len(in_flight) < concurrency:
                    item = pending[idx]
                    future = executor.submit(
                        _predict_one, adapter, item, client, model, timeout, retries, retry_sleep,
                        max_tokens, no_images, identity_context,
                    )
                    in_flight[future] = item
                    idx += 1
                    if sleep_seconds:
                        time.sleep(sleep_seconds)
                done, _ = wait(in_flight, return_when=FIRST_COMPLETED)
                for future in done:
                    item = in_flight.pop(future)
                    row = future.result()
                    api_calls += int(row.get("attempts") or 1)
                    if _is_rate_limit_error(row.get("error")):
                        if guard.on_rate_limit(str(row["item_id"])):
                            pending.append(item)
                            print(f"predict item={row['item_id']} rate-limited -> re-queued{_reason(row.get('error'))}")
                            continue
                    else:
                        guard.reset_streak()
                    rows.append(row)
                    append_prediction(out_path, row)
                    completed += 1
                    status = "error" if row.get("error") else ("empty" if row.get("empty_response") else "ok")
                    detail = _reason(row.get("error")) if status == "error" else ""
                    print(f"predict {completed}/{len(pending)} item={row['item_id']} status={status}{detail}")
    # Re-pack authoritatively: the hot loop rolls shards as it appends, so each
    # one already fits GitHub's 100 MB limit; write_predictions evens them out
    # and consolidates any shards left by a prior finalized run.
    write_predictions(out_path, rows)
    return _index_by_item(rows), {
        "cached_in_target": len(existing) - reused,
        "reused_cross_suite": reused,
        "new_prediction_items": completed,
        "new_prediction_calls": api_calls,
        "missing_prediction_items": missing_without_calls,
    }


def _extract_one(
    adapter: BenchmarkAdapter,
    item: dict[str, Any],
    prediction: dict[str, Any],
    client: MiniMaxClient,
    extractor_model: str,
    judge_model: str | None,
    identity_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    item_id = str(item["item_id"])
    client.reset_usage_window()
    row: dict[str, Any] = {
        "item_id": item_id,
        "extractor_model": extractor_model,
        "judge_model": judge_model,
    }
    cache_version = getattr(adapter, "extraction_cache_version", None)
    if cache_version:
        row["extraction_cache_version"] = str(cache_version)
    row["extraction_identity_sha256"] = extraction_identity(
        prediction=prediction, identity_context=identity_context or {}
    )
    try:
        extracted = adapter.extract_answer(
            item, str(prediction.get("response") or ""), client, extractor_model
        )
        row.update({"extracted": extracted, "usage": client.read_usage_window()})
    except Exception as exc:  # noqa: BLE001
        row.update({"extracted": "", "error": str(exc)})
    return row


def run_extractions(
    adapter: BenchmarkAdapter,
    items: list[dict[str, Any]],
    predictions: dict[str, dict[str, Any]],
    client: MiniMaxClient,
    out_path: Path,
    extractor_model: str,
    judge_model: str | None = None,
    concurrency: int = 1,
    rate_limit_threshold: int = 10,
    rate_limit_sleep: float = 1800.0,
    rate_limit_max_retries: int = 3,
    identity_context: dict[str, Any] | None = None,
    reuse_dirs: list[Path] | None = None,
) -> tuple[dict[str, dict[str, Any]], dict[str, int]]:
    # Treat errored / empty extractions as not-done so reruns retry only those.
    cache_version = getattr(adapter, "extraction_cache_version", None)
    identity_context = identity_context or {}
    expected = {
        item_id: extraction_identity(prediction, identity_context)
        for item_id, prediction in predictions.items()
    }

    def valid(row: dict[str, Any], *, cross_dir: bool) -> bool:
        item_id = str(row.get("item_id"))
        if not str(row.get("extracted") or "").strip() or row.get("error"):
            return False
        if str(row.get("extractor_model") or "") != str(extractor_model):
            return False
        if row.get("judge_model") not in (None, "") and str(row.get("judge_model")) != str(judge_model):
            return False
        if cache_version and str(row.get("extraction_cache_version") or "") != str(cache_version):
            return False
        stored = row.get("extraction_identity_sha256")
        if cross_dir and not stored:
            return False
        return not stored or stored == expected.get(item_id)

    existing = {
        k: v
        for k, v in _index_by_item(read_jsonl(out_path)).items()
        if k in expected and valid(v, cross_dir=False)
    }
    reused = 0
    target_dir = out_path.parent.resolve()
    for source_dir in reuse_dirs or []:
        source_dir = source_dir.resolve()
        if source_dir == target_dir:
            continue
        for item_id, row in _index_by_item(read_jsonl(source_dir / "extractions.jsonl")).items():
            if item_id in existing or item_id not in expected or not valid(row, cross_dir=True):
                continue
            existing[item_id] = {**row, "reused_from": str(source_dir)}
            reused += 1
    rows = list(existing.values())
    pending: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for item in items:
        item_id = str(item["item_id"])
        if item_id in existing:
            continue
        pred = predictions.get(item_id)
        if not pred or not str(pred.get("response") or "").strip():
            continue
        pending.append((item, pred))
    total = len(pending)
    print(f"extractions: {len(existing)} cached, {total} to run")

    guard = RateLimitGuard(rate_limit_threshold, rate_limit_sleep, rate_limit_max_retries)
    concurrency = max(1, concurrency)
    completed = 0
    api_calls = 0
    if concurrency == 1:
        n = 0
        while n < len(pending):
            item, prediction = pending[n]
            n += 1
            row = _extract_one(
                adapter, item, prediction, client, extractor_model, judge_model, identity_context
            )
            api_calls += 1
            if _is_rate_limit_error(row.get("error")):
                if guard.on_rate_limit(str(row["item_id"])):
                    pending.append((item, prediction))
                    print(f"extract item={row['item_id']} rate-limited -> re-queued{_reason(row.get('error'))}")
                    continue
            else:
                guard.reset_streak()
            rows.append(row)
            append_jsonl(out_path, row)
            completed += 1
            detail = f"ERROR{_reason(row.get('error'))}" if row.get("error") else f"-> {str(row.get('extracted'))[:40]!r}"
            print(f"extract {n}/{total} item={row['item_id']} {detail}")
    else:
        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            in_flight: dict[Any, tuple[dict[str, Any], dict[str, Any]]] = {}
            idx = 0
            while idx < len(pending) or in_flight:
                while idx < len(pending) and len(in_flight) < concurrency:
                    item, prediction = pending[idx]
                    future = executor.submit(
                        _extract_one, adapter, item, prediction, client, extractor_model,
                        judge_model, identity_context,
                    )
                    in_flight[future] = (item, prediction)
                    idx += 1
                done, _ = wait(in_flight, return_when=FIRST_COMPLETED)
                for future in done:
                    item, prediction = in_flight.pop(future)
                    row = future.result()
                    api_calls += 1
                    if _is_rate_limit_error(row.get("error")):
                        if guard.on_rate_limit(str(row["item_id"])):
                            pending.append((item, prediction))
                            print(f"extract item={row['item_id']} rate-limited -> re-queued{_reason(row.get('error'))}")
                            continue
                    else:
                        guard.reset_streak()
                    rows.append(row)
                    append_jsonl(out_path, row)
                    completed += 1
                    detail = f"ERROR{_reason(row.get('error'))}" if row.get("error") else f"-> {str(row.get('extracted'))[:40]!r}"
                    print(f"extract {completed}/{total} item={row['item_id']} {detail}")
    write_jsonl(out_path, rows)
    return _index_by_item(rows), {
        "cached_in_target": len(existing) - reused,
        "reused_cross_suite": reused,
        "new_extraction_items": completed,
        "new_extraction_calls": api_calls,
    }


def run_scoring(
    adapter: BenchmarkAdapter,
    items: list[dict[str, Any]],
    predictions: dict[str, dict[str, Any]],
    extractions: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    scored = []
    for item in items:
        item_id = str(item["item_id"])
        pred = predictions.get(item_id)
        row: dict[str, Any] = {"item_id": item_id, "buckets": adapter.buckets(item)}
        if not pred or not str(pred.get("response") or "").strip():
            row["score_status"] = "no_prediction"
            if pred and pred.get("error"):
                row["error"] = pred["error"]
            elif pred and pred.get("empty_response"):
                row["empty_response"] = True
            scored.append(row)
            continue
        ext = extractions.get(item_id)
        if ext is None:
            row["score_status"] = "no_extraction"
            row["response"] = pred.get("response")
            scored.append(row)
            continue
        if ext.get("error"):
            # An errored extraction (e.g. a judge/API call that failed) must never
            # be scored as a wrong answer — that would penalise the model for our
            # infrastructure failing. Mark it out of the denominator; a rerun will
            # retry it because run_extractions treats errored rows as not-done.
            row["score_status"] = "extraction_error"
            row["error"] = ext["error"]
            row["response"] = pred.get("response")
            if ext.get("judge_model"):
                row["judge_model"] = ext["judge_model"]
            scored.append(row)
            continue
        extracted = str(ext.get("extracted") or "")
        result = adapter.score(extracted, item)
        correct_value = result["correct"]
        row.update(
            score_status="scored",
            # Open-ended rubric benchmarks have a valid continuous score but no
            # meaningful binary correctness label.  Preserve None instead of
            # silently turning every response into an incorrect answer.
            correct=(bool(correct_value) if correct_value is not None else None),
            extracted=extracted,
            normalized=result["normalized"],
            gold=result["gold"],
            response=pred.get("response"),
        )
        if ext.get("judge_model"):
            row["judge_model"] = ext["judge_model"]
        # Carry adapter-specific score fields (e.g. rfs, outcome) into the row.
        reserved = {"correct", "normalized", "gold"} | set(row)
        row.update({k: v for k, v in result.items() if k not in reserved})
        scored.append(row)
    return scored


def run(
    adapter: BenchmarkAdapter,
    out_dir: Path,
    model: str,
    extractor_model: str,
    judge_model: str | None,
    limit: int | None,
    offset: int,
    concurrency: int,
    sleep_seconds: float,
    timeout: int,
    retries: int,
    retry_sleep: float,
    max_tokens: int | None,
    skip_extract: bool,
    score_only: bool,
    dry_run: bool,
    client: MiniMaxClient | None = None,
    extractor_client: MiniMaxClient | None = None,
    extract_concurrency: int = 1,
    rate_limit_threshold: int = 10,
    rate_limit_sleep: float = 1800.0,
    rate_limit_max_retries: int = 3,
    item_ids: list[str] | None = None,
    item_list_info: dict[str, Any] | None = None,
    run_metadata: dict[str, Any] | None = None,
    no_images: bool = False,
    prediction_identity_context: dict[str, Any] | None = None,
    extraction_identity_context: dict[str, Any] | None = None,
    reuse_dirs: list[Path] | None = None,
) -> dict[str, Any]:
    if item_ids is not None:
        # Fixed-list mode (--item-list): load everything, keep exactly the
        # listed items. Every listed id must exist — a typo'd list silently
        # shrinking the run would corrupt cross-model comparability.
        all_items = adapter.load_items(limit=None, offset=0)
        wanted = set(item_ids)
        items = [it for it in all_items if str(it["item_id"]) in wanted]
        missing = wanted - {str(it["item_id"]) for it in items}
        if missing:
            raise SystemExit(
                f"--item-list: {len(missing)} ids not found in {adapter.name}, "
                f"e.g. {sorted(missing)[:3]}"
            )
    else:
        items = adapter.load_items(limit=limit, offset=offset)
    loaded_ids = [str(item["item_id"]) for item in items]
    if len(loaded_ids) != len(set(loaded_ids)):
        raise SystemExit(f"{adapter.name}: loaded duplicate item_id values")
    print(f"loaded {len(items)} items for benchmark={adapter.name}")
    out_dir.mkdir(parents=True, exist_ok=True)

    if dry_run:
        for item in items[:3]:
            n_images = len(item.get("image_paths") or [])
            note = " [--no-images: withheld]" if no_images and n_images else ""
            print(f"\n=== item {item['item_id']} (images={n_images}{note}) ===")
            messages = adapter.build_messages(item)
            if no_images:
                messages = strip_image_parts(messages)
            print(json.dumps(_truncate_messages(messages), ensure_ascii=False, indent=2)[:2000])
        return {}

    client = client or MiniMaxClient(model=model, timeout=timeout)
    # Extraction/judge uses its own client+model (default: same as predictions)
    # so the prediction model can live on a different endpoint than the extractor
    # (e.g. predict via a gateway model, extract via MiniMax-M2.7 on MiniMax).
    extractor_client = extractor_client or client
    predictions_path = out_dir / "predictions.jsonl"
    extractions_path = out_dir / "extractions.jsonl"

    if score_only:
        predictions, prediction_stats = run_predictions(
            adapter, items, client, predictions_path, model,
            concurrency, sleep_seconds, timeout, retries, retry_sleep, max_tokens,
            rate_limit_threshold=rate_limit_threshold,
            rate_limit_sleep=rate_limit_sleep,
            rate_limit_max_retries=rate_limit_max_retries,
            no_images=no_images,
            identity_context=prediction_identity_context,
            reuse_dirs=reuse_dirs,
            allow_new=False,
        )
    else:
        predictions, prediction_stats = run_predictions(
            adapter, items, client, predictions_path, model,
            concurrency, sleep_seconds, timeout, retries, retry_sleep, max_tokens,
            rate_limit_threshold=rate_limit_threshold,
            rate_limit_sleep=rate_limit_sleep,
            rate_limit_max_retries=rate_limit_max_retries,
            no_images=no_images,
            identity_context=prediction_identity_context,
            reuse_dirs=reuse_dirs,
        )

    if skip_extract:
        extractions: dict[str, dict[str, Any]] = {}
        extraction_stats = {
            "cached_in_target": 0,
            "reused_cross_suite": 0,
            "new_extraction_calls": 0,
            "new_extraction_items": 0,
        }
    else:
        extractions, extraction_stats = run_extractions(
            adapter, items, predictions, extractor_client, extractions_path, extractor_model,
            judge_model=judge_model,
            concurrency=extract_concurrency,
            rate_limit_threshold=rate_limit_threshold,
            rate_limit_sleep=rate_limit_sleep,
            rate_limit_max_retries=rate_limit_max_retries,
            identity_context=extraction_identity_context,
            reuse_dirs=reuse_dirs,
        )

    scored = run_scoring(adapter, items, predictions, extractions)
    write_jsonl(out_dir / "scored.jsonl", scored)

    bucket_keys = list(adapter.buckets(items[0]).keys()) if items else []
    summary = build_summary(adapter.name, model, scored, bucket_keys)
    summary["extractor_model"] = extractor_model
    summary["judge_model"] = judge_model
    if item_list_info:
        summary.update(item_list_info)
    summary["token_usage"] = aggregate_token_usage(predictions, extractions)
    summary["execution_stats"] = {
        "predictions": prediction_stats,
        "extractions": extraction_stats,
    }
    extra_metrics = adapter.extra_summary(scored)
    if extra_metrics:
        summary["extra_metrics"] = extra_metrics
    summary.update(adapter.judge_prompt_provenance())
    if run_metadata:
        summary.update(run_metadata)
    summary["run_status"] = "complete"
    summary["completed_at"] = datetime.now(timezone.utc).isoformat()
    (out_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    items_by_id = {str(it["item_id"]): it for it in items}
    write_report(out_dir / "report.html", summary, scored, items_by_id, adapter)
    return summary
