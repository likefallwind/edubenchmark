"""Generic evaluation loop: predict -> extract -> score -> report.

Resumable and incremental: ``predictions.jsonl`` and ``extractions.jsonl`` are
keyed by ``item_id``; already-completed items are skipped on rerun. Each phase
writes to disk as it goes so a crash mid-run loses nothing.
"""

from __future__ import annotations

import json
import time
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from pathlib import Path
from typing import Any

from .base import BenchmarkAdapter
from .minimax_client import MiniMaxClient
from .report import build_summary, read_jsonl, write_jsonl, write_report


def _index_by_item(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(r["item_id"]): r for r in rows if r.get("item_id") is not None}


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

    concurrency = max(1, concurrency)
    completed = 0
    if concurrency == 1:
        for item in pending:
            row = _predict_one(adapter, item, client, model, timeout, retries, retry_sleep, max_tokens)
            rows.append(row)
            write_jsonl(out_path, rows)
            completed += 1
            status = "error" if row.get("error") else ("empty" if row.get("empty_response") else "ok")
            print(f"predict {completed}/{len(pending)} item={row['item_id']} status={status}")
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
                    in_flight.pop(future)
                    row = future.result()
                    rows.append(row)
                    write_jsonl(out_path, rows)
                    completed += 1
                    status = "error" if row.get("error") else ("empty" if row.get("empty_response") else "ok")
                    print(f"predict {completed}/{len(pending)} item={row['item_id']} status={status}")
    return _index_by_item(rows)


def _extract_one(
    adapter: BenchmarkAdapter,
    item: dict[str, Any],
    response: str,
    client: MiniMaxClient,
    extractor_model: str,
) -> dict[str, Any]:
    item_id = str(item["item_id"])
    try:
        extracted = adapter.extract_answer(item, response, client, extractor_model)
        return {"item_id": item_id, "extracted": extracted, "extractor_model": extractor_model}
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

    concurrency = max(1, concurrency)
    if concurrency == 1:
        for n, (item, response) in enumerate(pending, 1):
            row = _extract_one(adapter, item, response, client, extractor_model)
            rows.append(row)
            write_jsonl(out_path, rows)
            print(f"extract {n}/{total} item={row['item_id']} -> {str(row.get('extracted'))[:40]!r}")
    else:
        completed = 0
        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            in_flight: dict[Any, str] = {}
            idx = 0
            while idx < len(pending) or in_flight:
                while idx < len(pending) and len(in_flight) < concurrency:
                    item, response = pending[idx]
                    future = executor.submit(_extract_one, adapter, item, response, client, extractor_model)
                    in_flight[future] = str(item["item_id"])
                    idx += 1
                done, _ = wait(in_flight, return_when=FIRST_COMPLETED)
                for future in done:
                    in_flight.pop(future)
                    row = future.result()
                    rows.append(row)
                    write_jsonl(out_path, rows)
                    completed += 1
                    print(f"extract {completed}/{total} item={row['item_id']} -> {str(row.get('extracted'))[:40]!r}")
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
    extract_concurrency: int = 1,
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
    predictions_path = out_dir / "predictions.jsonl"
    extractions_path = out_dir / "extractions.jsonl"

    if score_only:
        predictions = _index_by_item(read_jsonl(predictions_path))
    else:
        predictions = run_predictions(
            adapter, items, client, predictions_path, model,
            concurrency, sleep_seconds, timeout, retries, retry_sleep, max_tokens,
        )

    if skip_extract:
        extractions: dict[str, dict[str, Any]] = {}
    else:
        extractions = run_extractions(
            adapter, items, predictions, client, extractions_path, extractor_model,
            concurrency=extract_concurrency,
        )

    scored = run_scoring(adapter, items, predictions, extractions)
    write_jsonl(out_dir / "scored.jsonl", scored)

    bucket_keys = list(adapter.buckets(items[0]).keys()) if items else []
    summary = build_summary(adapter.name, model, scored, bucket_keys)
    summary["extractor_model"] = extractor_model
    extra_metrics = adapter.extra_summary(scored)
    if extra_metrics:
        summary["extra_metrics"] = extra_metrics
    (out_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    items_by_id = {str(it["item_id"]): it for it in items}
    write_report(out_dir / "report.html", summary, scored, items_by_id, adapter)
    return summary
