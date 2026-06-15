"""Generic evaluation loop: predict -> extract -> score -> report.

Resumable and incremental: ``predictions.jsonl`` and ``extractions.jsonl`` are
keyed by ``item_id``; already-completed items are skipped on rerun. Each
completed item is appended to disk immediately (never a full-file rewrite), so
a crash mid-run loses nothing. Retried items append a fresh row; readers
dedupe via ``_index_by_item`` where the last row per ``item_id`` wins.
"""

from __future__ import annotations

import json
import time
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


def _index_by_item(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(r["item_id"]): r for r in rows if r.get("item_id") is not None}


def _reason(error: str | None, limit: int = 300) -> str:
    """Render an error string as a ` reason=...` suffix for the run log (eval.log)."""
    if not error:
        return ""
    text = " ".join(str(error).split())
    return f" reason={text[:limit]!r}"


def _is_rate_limit_error(error: str | None) -> bool:
    """Heuristic: does this error string look like API throttling (vs. a real bug)?

    Covers HTTP 429 and the MiniMax ``base_resp`` rate-limit status codes 1002
    (QPS/concurrency limit) and 1039 (TPM limit), plus generic phrasings.
    """
    if not error:
        return False
    low = error.lower()
    if "http 429" in low or "too many requests" in low or "rate limit" in low or "限流" in low:
        return True
    return "base_resp 1002" in low or "base_resp 1039" in low


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


def _predict_one(
    adapter: BenchmarkAdapter,
    item: dict[str, Any],
    client: MiniMaxClient,
    model: str,
    timeout: int,
    retries: int,
    retry_sleep: float,
    max_tokens: int | None,
) -> dict[str, Any]:
    messages = adapter.build_messages(item)
    started = time.time()
    client.reset_usage_window()
    response = ""
    error: str | None = None
    attempts = 0
    for attempt in range(retries + 1):
        attempts = attempt + 1
        try:
            response = client.chat(messages, model=model, max_tokens=max_tokens, timeout=timeout)
            error = None
        except Exception as exc:  # noqa: BLE001 - record and retry
            response = ""
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
    }
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
) -> dict[str, dict[str, Any]]:
    # Treat errored / empty predictions as not-done so reruns retry only those.
    existing = {
        k: v
        for k, v in _index_by_item(read_jsonl(out_path)).items()
        if str(v.get("response") or "").strip() and not v.get("error") and not v.get("empty_response")
    }
    pending = [it for it in items if str(it["item_id"]) not in existing]
    rows = list(existing.values())
    print(f"predictions: {len(existing)} cached, {len(pending)} to run")

    guard = RateLimitGuard(rate_limit_threshold, rate_limit_sleep, rate_limit_max_retries)
    concurrency = max(1, concurrency)
    completed = 0
    if concurrency == 1:
        idx = 0
        while idx < len(pending):
            item = pending[idx]
            idx += 1
            row = _predict_one(adapter, item, client, model, timeout, retries, retry_sleep, max_tokens)
            if _is_rate_limit_error(row.get("error")):
                if guard.on_rate_limit(str(row["item_id"])):
                    pending.append(item)
                    print(f"predict item={row['item_id']} rate-limited -> re-queued{_reason(row.get('error'))}")
                    continue
            else:
                guard.reset_streak()
            rows.append(row)
            append_jsonl(out_path, row)
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
                        _predict_one, adapter, item, client, model, timeout, retries, retry_sleep, max_tokens
                    )
                    in_flight[future] = item
                    idx += 1
                    if sleep_seconds:
                        time.sleep(sleep_seconds)
                done, _ = wait(in_flight, return_when=FIRST_COMPLETED)
                for future in done:
                    item = in_flight.pop(future)
                    row = future.result()
                    if _is_rate_limit_error(row.get("error")):
                        if guard.on_rate_limit(str(row["item_id"])):
                            pending.append(item)
                            print(f"predict item={row['item_id']} rate-limited -> re-queued{_reason(row.get('error'))}")
                            continue
                    else:
                        guard.reset_streak()
                    rows.append(row)
                    append_jsonl(out_path, row)
                    completed += 1
                    status = "error" if row.get("error") else ("empty" if row.get("empty_response") else "ok")
                    detail = _reason(row.get("error")) if status == "error" else ""
                    print(f"predict {completed}/{len(pending)} item={row['item_id']} status={status}{detail}")
    return _index_by_item(rows)


def _extract_one(
    adapter: BenchmarkAdapter,
    item: dict[str, Any],
    response: str,
    client: MiniMaxClient,
    extractor_model: str,
) -> dict[str, Any]:
    item_id = str(item["item_id"])
    client.reset_usage_window()
    try:
        extracted = adapter.extract_answer(item, response, client, extractor_model)
        return {
            "item_id": item_id,
            "extracted": extracted,
            "extractor_model": extractor_model,
            "usage": client.read_usage_window(),
        }
    except Exception as exc:  # noqa: BLE001
        return {"item_id": item_id, "extracted": "", "error": str(exc)}


def run_extractions(
    adapter: BenchmarkAdapter,
    items: list[dict[str, Any]],
    predictions: dict[str, dict[str, Any]],
    client: MiniMaxClient,
    out_path: Path,
    extractor_model: str,
    concurrency: int = 1,
    rate_limit_threshold: int = 10,
    rate_limit_sleep: float = 1800.0,
    rate_limit_max_retries: int = 3,
) -> dict[str, dict[str, Any]]:
    # Treat errored / empty extractions as not-done so reruns retry only those.
    existing = {
        k: v
        for k, v in _index_by_item(read_jsonl(out_path)).items()
        if str(v.get("extracted") or "").strip() and not v.get("error")
    }
    rows = list(existing.values())
    pending: list[tuple[dict[str, Any], str]] = []
    for item in items:
        item_id = str(item["item_id"])
        if item_id in existing:
            continue
        pred = predictions.get(item_id)
        if not pred or not str(pred.get("response") or "").strip():
            continue
        pending.append((item, str(pred["response"])))
    total = len(pending)
    print(f"extractions: {len(existing)} cached, {total} to run")

    guard = RateLimitGuard(rate_limit_threshold, rate_limit_sleep, rate_limit_max_retries)
    concurrency = max(1, concurrency)
    if concurrency == 1:
        n = 0
        while n < len(pending):
            item, response = pending[n]
            n += 1
            row = _extract_one(adapter, item, response, client, extractor_model)
            if _is_rate_limit_error(row.get("error")):
                if guard.on_rate_limit(str(row["item_id"])):
                    pending.append((item, response))
                    print(f"extract item={row['item_id']} rate-limited -> re-queued{_reason(row.get('error'))}")
                    continue
            else:
                guard.reset_streak()
            rows.append(row)
            append_jsonl(out_path, row)
            detail = f"ERROR{_reason(row.get('error'))}" if row.get("error") else f"-> {str(row.get('extracted'))[:40]!r}"
            print(f"extract {n}/{total} item={row['item_id']} {detail}")
    else:
        completed = 0
        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            in_flight: dict[Any, tuple[dict[str, Any], str]] = {}
            idx = 0
            while idx < len(pending) or in_flight:
                while idx < len(pending) and len(in_flight) < concurrency:
                    item, response = pending[idx]
                    future = executor.submit(_extract_one, adapter, item, response, client, extractor_model)
                    in_flight[future] = (item, response)
                    idx += 1
                done, _ = wait(in_flight, return_when=FIRST_COMPLETED)
                for future in done:
                    item, response = in_flight.pop(future)
                    row = future.result()
                    if _is_rate_limit_error(row.get("error")):
                        if guard.on_rate_limit(str(row["item_id"])):
                            pending.append((item, response))
                            print(f"extract item={row['item_id']} rate-limited -> re-queued{_reason(row.get('error'))}")
                            continue
                    else:
                        guard.reset_streak()
                    rows.append(row)
                    append_jsonl(out_path, row)
                    completed += 1
                    detail = f"ERROR{_reason(row.get('error'))}" if row.get("error") else f"-> {str(row.get('extracted'))[:40]!r}"
                    print(f"extract {completed}/{total} item={row['item_id']} {detail}")
    return _index_by_item(rows)


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
        extracted = str(ext.get("extracted") or "")
        result = adapter.score(extracted, item)
        row.update(
            score_status="scored",
            correct=bool(result["correct"]),
            extracted=extracted,
            normalized=result["normalized"],
            gold=result["gold"],
            response=pred.get("response"),
        )
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
) -> dict[str, Any]:
    items = adapter.load_items(limit=limit, offset=offset)
    print(f"loaded {len(items)} items for benchmark={adapter.name}")
    out_dir.mkdir(parents=True, exist_ok=True)

    if dry_run:
        for item in items[:3]:
            print(f"\n=== item {item['item_id']} (images={len(item.get('image_paths') or [])}) ===")
            print(json.dumps(_truncate_messages(adapter.build_messages(item)), ensure_ascii=False, indent=2)[:2000])
        return {}

    client = client or MiniMaxClient(model=model, timeout=timeout)
    # Extraction/judge uses its own client+model (default: same as predictions)
    # so the prediction model can live on a different endpoint than the extractor
    # (e.g. predict via a gateway model, extract via MiniMax-M2.7 on MiniMax).
    extractor_client = extractor_client or client
    predictions_path = out_dir / "predictions.jsonl"
    extractions_path = out_dir / "extractions.jsonl"

    if score_only:
        predictions = _index_by_item(read_jsonl(predictions_path))
    else:
        predictions = run_predictions(
            adapter, items, client, predictions_path, model,
            concurrency, sleep_seconds, timeout, retries, retry_sleep, max_tokens,
            rate_limit_threshold=rate_limit_threshold,
            rate_limit_sleep=rate_limit_sleep,
            rate_limit_max_retries=rate_limit_max_retries,
        )

    if skip_extract:
        extractions: dict[str, dict[str, Any]] = {}
    else:
        extractions = run_extractions(
            adapter, items, predictions, extractor_client, extractions_path, extractor_model,
            concurrency=extract_concurrency,
            rate_limit_threshold=rate_limit_threshold,
            rate_limit_sleep=rate_limit_sleep,
            rate_limit_max_retries=rate_limit_max_retries,
        )

    scored = run_scoring(adapter, items, predictions, extractions)
    write_jsonl(out_dir / "scored.jsonl", scored)

    bucket_keys = list(adapter.buckets(items[0]).keys()) if items else []
    summary = build_summary(adapter.name, model, scored, bucket_keys)
    summary["extractor_model"] = extractor_model
    summary["token_usage"] = aggregate_token_usage(predictions, extractions)
    extra_metrics = adapter.extra_summary(scored)
    if extra_metrics:
        summary["extra_metrics"] = extra_metrics
    (out_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    items_by_id = {str(it["item_id"]): it for it in items}
    write_report(out_dir / "report.html", summary, scored, items_by_id, adapter)
    return summary
