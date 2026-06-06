#!/usr/bin/env python3
"""Run or score the RE_BENCHMARK_V1 pilot package.

The runner currently supports:
- prompt export for model inference systems,
- exact-match scoring for automatically scoreable text items,
- judge-needed accounting for rubric, multimodal, code, and safety items.

Predictions JSONL format:
{"item_id": "...", "response": "...", "model": "optional"}
or
{"pilot_item_id": "...", "response": "...", "model": "optional"}
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import time
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from functools import lru_cache
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ITEMS = ROOT / "data" / "re_benchmark_v1" / "pilot_items.jsonl"
DEFAULT_PROMPTS = ROOT / "data" / "re_benchmark_v1" / "pilot_prompts.jsonl"
DEFAULT_REPORT_DIR = ROOT / "reports" / "re_benchmark_v1"
MINIMAX_DEFAULT_MODEL = "MiniMax-M2.7"
MINIMAX_BASE_URL = "https://api.minimaxi.com/anthropic"
OPTION_LABELS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows = []
    with path.open(encoding="utf-8", errors="ignore") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def normalize_answer(text: Any) -> str:
    text = "" if text is None else str(text)
    text = text.strip().lower()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"^[\"'`]+|[\"'`]+$", "", text)
    text = re.sub(r"^(answer|final answer)\s*[:：]\s*", "", text)
    return text.strip()


def exact_match(response: str, gold: str) -> bool:
    pred = normalize_answer(response)
    expected = normalize_answer(gold)
    if not pred or not expected:
        return False
    if pred == expected:
        return True
    # Common MCQ outputs: "A", "A.", "(A)", or option text embedded in a short answer.
    pred_clean = re.sub(r"[^a-z0-9\u4e00-\u9fff.+\\/ -]", "", pred).strip()
    expected_clean = re.sub(r"[^a-z0-9\u4e00-\u9fff.+\\/ -]", "", expected).strip()
    return pred_clean == expected_clean


def extract_option_or_short_answer(response: str) -> str:
    """Return a compact answer for auto scoring while preserving raw responses elsewhere."""
    text = normalize_answer(response)
    match = re.search(r"^\(?([a-j])\)?(?:[.)、\s]|$)", text, re.I)
    if match:
        return match.group(1).upper()
    match = re.search(
        r"(?:final answer|答案|(?<!choices )answer)(?:\s+(?:is|为))?\s*[:：]\s*\(?([a-j])\)?(?:[.)、\s]|$)",
        text,
        re.I,
    )
    if match:
        return match.group(1).upper()
    option_mentions = re.findall(
        r"(?:final answer|答案|(?<!choices )answer|option|choice|letter)(?:\s+(?:is|为))?\s*[:：]?\s*\(?([a-j])\)?(?:[.)、\s]|$)",
        text,
        re.I,
    )
    if option_mentions:
        return option_mentions[-1].upper()
    numeric_matches = re.findall(
        r"(?:final answer|答案|(?<!choices )answer|thus answer)(?:\s+(?:is|为))?\s*[:：]?\s*([+-]?\d+(?:\.\d+)?)",
        text,
        re.I,
    )
    if numeric_matches:
        return numeric_matches[-1]
    if len(text) <= 40:
        match = re.search(r"\b([a-j])\b", text, re.I)
        if match:
            return match.group(1).upper()
        numeric = re.search(r"[+-]?\d+(?:\.\d+)?", text)
        if numeric:
            return numeric.group(0)
    return response.strip()


def letter_only_response(response: str) -> bool:
    return bool(re.fullmatch(r"\s*\(?[A-J]\)?[.)、]?\s*", response or "", flags=re.I))


def protocol_only_item(item: dict[str, Any]) -> bool:
    return item.get("benchmark_id") in {"statics2011", "ednet"} or item.get("runner_status") == "protocol_only_not_llm_prompt"


def auto_scoreable(item: dict[str, Any]) -> bool:
    return item.get("runner_status") == "auto_exact_match_candidate" and not protocol_only_item(item)


@lru_cache(maxsize=256)
def read_jsonl_row(path_text: str, row_index: int) -> dict[str, Any]:
    path = ROOT / path_text
    with path.open(encoding="utf-8", errors="ignore") as fh:
        for idx, line in enumerate(fh):
            if idx == row_index:
                return json.loads(line)
    return {}


@lru_cache(maxsize=256)
def read_parquet_row(path_text: str, row_index: int) -> dict[str, Any]:
    try:
        import pandas as pd
    except Exception:
        return {}
    path = ROOT / path_text
    try:
        row = pd.read_parquet(path).iloc[row_index].to_dict()
    except Exception:
        return {}
    if "choices" in row and hasattr(row["choices"], "tolist"):
        row["choices"] = row["choices"].tolist()
    if "answer" in row:
        try:
            row["answer"] = int(row["answer"])
        except Exception:
            pass
    return row


def strip_option_prefix(text: Any) -> str:
    return re.sub(r"^\s*\(?[A-Z]\)?[.)、：:\s]*", "", str(text)).strip()


def mcq_spec(item: dict[str, Any]) -> dict[str, Any] | None:
    benchmark_id = item.get("benchmark_id")
    source_file = str(item.get("source_file") or "")
    try:
        row_index = int(item.get("source_row_or_key"))
    except Exception:
        row_index = -1

    if benchmark_id == "mmlu" and source_file.endswith(".parquet") and row_index >= 0:
        row = read_parquet_row(source_file, row_index)
        choices = [str(choice) for choice in row.get("choices") or []]
        answer = row.get("answer")
        if choices and isinstance(answer, int) and 0 <= answer < len(choices):
            return {
                "question": str(row.get("question") or item.get("question") or ""),
                "choices": choices,
                "correct_label": OPTION_LABELS[answer],
                "correct_text": choices[answer],
                "source": "mmlu_parquet",
            }

    if benchmark_id == "agieval" and source_file.endswith(".jsonl") and row_index >= 0:
        row = read_jsonl_row(source_file, row_index)
        raw_options = row.get("options") or []
        choices = [strip_option_prefix(option) for option in raw_options]
        label = str(row.get("label") or item.get("answer_or_rubric") or "").strip().upper()
        question = str(row.get("question") or item.get("question") or "")
        passage = str(row.get("passage") or "").strip()
        if passage:
            question = f"{passage}\n\n{question}"
        if choices and label:
            return {
                "question": question,
                "choices": choices,
                "correct_label": label,
                "correct_text": choices[OPTION_LABELS.index(label)] if label in OPTION_LABELS[: len(choices)] else "",
                "source": "agieval_jsonl",
            }

    return None


def answer_matches_item(extracted: str, item: dict[str, Any]) -> bool:
    spec = mcq_spec(item)
    if spec:
        return exact_match(extracted, spec.get("correct_label", "")) or exact_match(extracted, spec.get("correct_text", ""))
    return exact_match(extracted, str(item.get("answer_or_rubric", "")))


def load_predictions(path: Path) -> dict[str, dict[str, Any]]:
    predictions = {}
    for row in read_jsonl(path):
        key = row.get("pilot_item_id") or row.get("item_id")
        if key:
            predictions[str(key)] = row
    return predictions


def score_items(items: list[dict[str, Any]], predictions: dict[str, dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    scored = []
    counters = Counter()
    by_category: dict[str, Counter] = defaultdict(Counter)
    by_runner: dict[str, Counter] = defaultdict(Counter)

    for item in items:
        pred = predictions.get(item["pilot_item_id"]) or predictions.get(item["item_id"])
        row = {
            "pilot_item_id": item["pilot_item_id"],
            "item_id": item["item_id"],
            "category_id": item["category_id"],
            "benchmark_id": item["benchmark_id"],
            "runner_status": item["runner_status"],
            "score_status": "missing_prediction",
            "score": None,
            "model": pred.get("model") if pred else None,
        }
        if pred is None:
            counters["missing_prediction"] += 1
            by_category[item["category_id"]]["missing_prediction"] += 1
            by_runner[item["runner_status"]]["missing_prediction"] += 1
        elif protocol_only_item(item):
            row["score_status"] = "protocol_required"
            row["response"] = pred.get("response", "")
            counters["protocol_required"] += 1
            by_category[item["category_id"]]["protocol_required"] += 1
            by_runner[item["runner_status"]]["protocol_required"] += 1
        elif auto_scoreable(item):
            extracted = extract_option_or_short_answer(str(pred.get("response", "")))
            correct = answer_matches_item(str(extracted), item)
            spec = mcq_spec(item)
            row["score_status"] = "auto_scored"
            row["score"] = 1.0 if correct else 0.0
            row["response"] = pred.get("response", "")
            row["extracted_answer"] = extracted
            if spec:
                row["format_ok"] = letter_only_response(str(pred.get("response", "")))
                row["correct_label"] = spec.get("correct_label")
                row["correct_text"] = spec.get("correct_text")
            counters["auto_scored"] += 1
            counters["correct" if correct else "incorrect"] += 1
            by_category[item["category_id"]]["auto_scored"] += 1
            by_category[item["category_id"]]["correct" if correct else "incorrect"] += 1
            by_runner[item["runner_status"]]["auto_scored"] += 1
        else:
            row["score_status"] = "judge_required"
            row["response"] = pred.get("response", "")
            counters["judge_required"] += 1
            by_category[item["category_id"]]["judge_required"] += 1
            by_runner[item["runner_status"]]["judge_required"] += 1
        scored.append(row)

    auto_scored = counters["auto_scored"]
    summary = {
        "total_items": len(items),
        "total_predictions": len(predictions),
        "auto_scored": auto_scored,
        "accuracy_auto_scored": counters["correct"] / auto_scored if auto_scored else None,
        "counts": dict(counters),
        "by_category": {k: dict(v) for k, v in sorted(by_category.items())},
        "by_runner_status": {k: dict(v) for k, v in sorted(by_runner.items())},
    }
    return scored, summary


def export_prompts(items: list[dict[str, Any]], path: Path) -> None:
    write_jsonl(path, build_prompt_rows(items))


def minimax_max_tokens(item: dict[str, Any]) -> int | None:
    # MiniMax M2.7 may spend the whole requested output budget on thinking
    # blocks before emitting a final text block. For benchmark testing, omit
    # max_tokens entirely and let the endpoint stop at end_turn; wall-clock
    # timeout still limits runaway calls.
    return None


def select_minimax_items(items: list[dict[str, Any]], limit: int, selection: str) -> list[dict[str, Any]]:
    if selection == "all":
        runnable = list(items)
    elif selection == "text":
        runnable = [
            item
            for item in items
            if item.get("runner_status") in {"auto_exact_match_candidate", "needs_llm_or_human_judge"}
        ]
    else:
        runnable = [
            item
            for item in items
            if item.get("runner_status") in {"auto_exact_match_candidate", "needs_llm_or_human_judge"}
            and item.get("category_id") != "C3"
        ]
    buckets: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for item in runnable:
        buckets[(item["category_id"], item["benchmark_id"])].append(item)
    selected: list[dict[str, Any]] = []
    keys = sorted(buckets)
    while len(selected) < limit and any(buckets.values()):
        for key in keys:
            if buckets[key]:
                selected.append(buckets[key].pop(0))
                if len(selected) >= limit:
                    break
    return selected


def call_minimax(prompt: str, model: str, max_tokens: int | None, timeout: int = 90, system_prompt: str | None = None) -> str:
    api_key = os.environ.get("MINIMAX_API_KEY")
    if not api_key:
        raise RuntimeError("MINIMAX_API_KEY is not set")
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
    }
    if max_tokens is not None:
        payload["max_tokens"] = max_tokens
    if system_prompt:
        payload["system"] = system_prompt
    request = urllib.request.Request(
        f"{MINIMAX_BASE_URL}/v1/messages",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"MiniMax HTTP {exc.code}: {body[:500]}") from exc
    content = data.get("content", [])
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                parts.append(str(block.get("text", "")))
            elif isinstance(block, str):
                parts.append(block)
        return "\n".join(part for part in parts if part).strip()
    return str(content).strip()


def build_minimax_prediction_row(
    item: dict[str, Any],
    prompt: str,
    model: str,
    timeout: int,
    retries: int,
    retry_sleep: float,
) -> dict[str, Any]:
    started = time.time()
    response = ""
    error = None
    attempts = 0
    for attempt in range(retries + 1):
        attempts = attempt + 1
        try:
            response = call_minimax(
                prompt,
                model,
                minimax_max_tokens(item),
                timeout=timeout,
            )
            error = None
        except Exception as exc:
            response = ""
            error = str(exc)
        if response.strip():
            break
        if attempt < retries and retry_sleep:
            time.sleep(retry_sleep * (attempt + 1))
    row = {
        "pilot_item_id": item["pilot_item_id"],
        "item_id": item["item_id"],
        "category_id": item["category_id"],
        "benchmark_id": item["benchmark_id"],
        "runner_status": item["runner_status"],
        "model": model,
        "response": response,
        "extracted_answer": extract_option_or_short_answer(response) if auto_scoreable(item) else None,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "latency_seconds": round(time.time() - started, 3),
        "attempts": attempts,
    }
    if not response.strip() and error is None:
        row["empty_response"] = True
    if error:
        row["error"] = error
    return row


def run_minimax_smoke(
    items: list[dict[str, Any]],
    out_path: Path,
    model: str,
    limit: int,
    sleep_seconds: float,
    concurrency: int,
    timeout: int,
    retries: int,
    retry_sleep: float,
    retry_empty_existing: bool,
    selection: str,
) -> list[dict[str, Any]]:
    prompts_by_id = {row["pilot_item_id"]: row["prompt"] for row in build_prompt_rows(items)}
    existing_all = load_predictions(out_path)
    if retry_empty_existing:
        existing = {
            key: row
            for key, row in existing_all.items()
            if str(row.get("response") or "").strip() and not row.get("error") and not row.get("empty_response")
        }
    else:
        existing = existing_all
    selected = select_minimax_items(items, limit, selection)
    rows = list(existing.values())
    pending_items = [item for item in selected if item["pilot_item_id"] not in existing]
    concurrency = max(1, min(2, concurrency))
    if concurrency == 1:
        for idx, item in enumerate(pending_items, 1):
            row = build_minimax_prediction_row(
                item,
                prompts_by_id[item["pilot_item_id"]],
                model,
                timeout,
                retries,
                retry_sleep,
            )
            rows.append(row)
            write_jsonl(out_path, rows)
            status = "error" if row.get("error") else "ok"
            print(f"minimax_smoke={idx}/{len(pending_items)} item={item['pilot_item_id']} benchmark={item['benchmark_id']} status={status}")
            if sleep_seconds:
                time.sleep(sleep_seconds)
        return rows

    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        in_flight = {}
        next_index = 0
        completed = 0
        while next_index < len(pending_items) or in_flight:
            while next_index < len(pending_items) and len(in_flight) < concurrency:
                item = pending_items[next_index]
                future = executor.submit(
                    build_minimax_prediction_row,
                    item,
                    prompts_by_id[item["pilot_item_id"]],
                    model,
                    timeout,
                    retries,
                    retry_sleep,
                )
                in_flight[future] = item
                next_index += 1
                if sleep_seconds:
                    time.sleep(sleep_seconds)
            done, _ = wait(in_flight, return_when=FIRST_COMPLETED)
            for future in done:
                item = in_flight.pop(future)
                completed += 1
                row = future.result()
                rows.append(row)
                write_jsonl(out_path, rows)
                status = "error" if row.get("error") else "ok"
                print(
                    f"minimax_smoke={completed}/{len(pending_items)} "
                    f"item={item['pilot_item_id']} benchmark={item['benchmark_id']} status={status}"
                )
    return rows


def build_prompt_rows(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    prompts = []
    for item in items:
        prompt, prompt_style, prompt_source = build_prompt_for_item(item)
        prompts.append(
            {
                "pilot_item_id": item["pilot_item_id"],
                "item_id": item["item_id"],
                "category_id": item["category_id"],
                "benchmark_id": item["benchmark_id"],
                "runner_status": item["runner_status"],
                "prompt_style": prompt_style,
                "prompt_source": prompt_source,
                "prompt": prompt,
            }
        )
    return prompts


def build_prompt_for_item(item: dict[str, Any]) -> tuple[str, str, str]:
    if protocol_only_item(item):
        return (
            "This item is a knowledge-tracing / learner-modeling protocol record, not a direct LLM prompt.\n"
            "Do not treat this as a benchmark question with a single answer.\n\n"
            f"Protocol description:\n{item.get('question', '')}\n\n"
            "Expected evaluation: run the dataset protocol and report metrics such as AUC, ACC, NLL, or RMSE.",
            "protocol_notice",
            "runner_generated_protocol_guard",
        )

    spec = mcq_spec(item)
    if auto_scoreable(item) and spec:
        option_lines = []
        for idx, choice in enumerate(spec["choices"]):
            option_lines.append(f"{OPTION_LABELS[idx]}. {choice}")
        return (
            "Answer the following multiple-choice question.\n"
            "Return only the option letter. Do not explain.\n\n"
            f"Question:\n{spec['question']}\n\n"
            "Options:\n"
            + "\n".join(option_lines)
            + "\n\nAnswer:",
            "official_data_mcq_letter_only",
            spec["source"],
        )

    if auto_scoreable(item):
        return (
            "Answer the following question.\n"
            "Return only the final answer. Do not explain.\n\n"
            f"Question:\n{item.get('question', '')}\n\nAnswer:",
            "short_answer_only",
            "item_question",
        )

    if item.get("runner_status") == "needs_multimodal_adapter":
        return (
            "This benchmark item requires image or multimodal input, but this run is text-only.\n"
            "If the image is not available in the prompt, reply exactly: IMAGE_INPUT_REQUIRED.\n\n"
            f"Question metadata:\n{item.get('question', '')}",
            "multimodal_text_only_guard",
            "item_question_without_media",
        )

    if item.get("runner_status") == "needs_code_or_program_runner":
        tests = ""
        try:
            rubric = json.loads(str(item.get("answer_or_rubric") or "{}"))
            if rubric.get("tests"):
                tests = "\n\nUnit tests the solution should pass:\n" + "\n".join(str(test) for test in rubric["tests"])
        except Exception:
            pass
        return (
            "Write a Python solution for the following programming task.\n"
            "Return only the code. Do not include analysis or prose.\n\n"
            f"Task:\n{item.get('question', '')}"
            f"{tests}",
            "code_generation_tests",
            "item_question_plus_tests",
        )

    question = str(item.get("question", ""))
    if item.get("benchmark_id") == "eduguard_bench" and (
        "Please reply only" in question or "Teacher Role-play Prompt" in question
    ):
        return (
            question,
            "benchmark_embedded_instruction",
            "item_question_contains_instruction",
        )

    return (
        "Complete the following education benchmark task.\n"
        "Return the response requested by the task. Do not include meta-commentary about being evaluated.\n\n"
        f"Task:\n{question}",
        "open_ended_task_only",
        "item_question",
    )


def write_report(path: Path, summary: dict[str, Any], scored: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    category_rows = []
    for category, counts in summary["by_category"].items():
        category_rows.append(
            "<tr>"
            f"<td>{esc(category)}</td>"
            f"<td>{counts.get('auto_scored', 0)}</td>"
            f"<td>{counts.get('correct', 0)}</td>"
            f"<td>{counts.get('incorrect', 0)}</td>"
            f"<td>{counts.get('judge_required', 0)}</td>"
            f"<td>{counts.get('protocol_required', 0)}</td>"
            f"<td>{counts.get('missing_prediction', 0)}</td>"
            "</tr>"
        )
    runner_rows = []
    for status, counts in summary["by_runner_status"].items():
        runner_rows.append(
            "<tr>"
            f"<td>{esc(status)}</td>"
            f"<td>{sum(counts.values())}</td>"
            f"<td>{counts.get('auto_scored', 0)}</td>"
            f"<td>{counts.get('judge_required', 0)}</td>"
            f"<td>{counts.get('protocol_required', 0)}</td>"
            f"<td>{counts.get('missing_prediction', 0)}</td>"
            "</tr>"
        )
    accuracy = summary["accuracy_auto_scored"]
    accuracy_text = "n/a" if accuracy is None else f"{accuracy:.3f}"
    html_text = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>RE_BENCHMARK_V1 Run Report</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans SC", sans-serif; margin: 0; background: #f4f6fb; color: #182033; }}
    main {{ max-width: 980px; margin: 0 auto; padding: 32px 22px 50px; }}
    header, section {{ background: white; border: 1px solid #dbe2ef; border-radius: 8px; padding: 22px; margin-bottom: 16px; }}
    h1 {{ margin: 0 0 8px; }}
    table {{ width: 100%; border-collapse: collapse; }}
    th, td {{ padding: 9px 10px; border-bottom: 1px solid #dbe2ef; text-align: left; }}
    th {{ background: #f7f9fd; }}
    code {{ background: #eef2f8; padding: 2px 4px; border-radius: 4px; }}
  </style>
</head>
<body>
<main>
  <header>
    <h1>RE_BENCHMARK_V1 Run Report</h1>
    <p>Total items: <strong>{summary['total_items']}</strong>. Predictions: <strong>{summary['total_predictions']}</strong>. Auto-scored accuracy: <strong>{accuracy_text}</strong>.</p>
  </header>
  <section>
    <h2>By Category</h2>
    <table><thead><tr><th>Category</th><th>Auto scored</th><th>Correct</th><th>Incorrect</th><th>Judge required</th><th>Protocol</th><th>Missing</th></tr></thead><tbody>{''.join(category_rows)}</tbody></table>
  </section>
  <section>
    <h2>By Runner Status</h2>
    <table><thead><tr><th>Status</th><th>Total</th><th>Auto scored</th><th>Judge required</th><th>Protocol</th><th>Missing</th></tr></thead><tbody>{''.join(runner_rows)}</tbody></table>
  </section>
</main>
</body>
</html>
"""
    path.write_text(html_text, encoding="utf-8")


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--items", type=Path, default=DEFAULT_ITEMS)
    parser.add_argument("--predictions", type=Path)
    parser.add_argument("--export-prompts", type=Path, default=DEFAULT_PROMPTS)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_REPORT_DIR)
    parser.add_argument("--run-minimax-smoke", action="store_true")
    parser.add_argument("--minimax-model", default=MINIMAX_DEFAULT_MODEL)
    parser.add_argument("--minimax-limit", type=int, default=24)
    parser.add_argument("--minimax-sleep", type=float, default=0.2)
    parser.add_argument("--minimax-concurrency", type=int, default=2)
    parser.add_argument("--minimax-timeout", type=int, default=90)
    parser.add_argument("--minimax-retries", type=int, default=2)
    parser.add_argument("--minimax-retry-sleep", type=float, default=1.0)
    parser.add_argument("--retry-empty-existing", action="store_true")
    parser.add_argument("--minimax-selection", choices=["smoke", "text", "all"], default="smoke")
    args = parser.parse_args()

    items = read_jsonl(args.items)
    if not items:
        raise SystemExit(f"No pilot items found at {args.items}. Run scripts/build_re_benchmark_v1.py first.")

    if args.export_prompts:
        export_prompts(items, args.export_prompts)
        print(f"exported_prompts={len(items)} {display_path(args.export_prompts)}")

    predictions_path = args.predictions
    if args.run_minimax_smoke:
        predictions_path = predictions_path or args.out_dir / "minimax_predictions.jsonl"
        run_minimax_smoke(
            items,
            predictions_path,
            args.minimax_model,
            args.minimax_limit,
            args.minimax_sleep,
            args.minimax_concurrency,
            args.minimax_timeout,
            args.minimax_retries,
            args.minimax_retry_sleep,
            args.retry_empty_existing,
            args.minimax_selection,
        )

    predictions = load_predictions(predictions_path) if predictions_path else {}
    scored, summary = score_items(items, predictions)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_json(args.out_dir / "run_summary.json", summary)
    write_jsonl(args.out_dir / "scored_items.jsonl", scored)
    write_report(args.out_dir / "run_report.html", summary, scored)
    if predictions_path and predictions_path.name == "minimax_predictions.jsonl":
        write_jsonl(args.out_dir / "minimax_auto_scores.jsonl", scored)

    print(f"items={summary['total_items']}")
    print(f"predictions={summary['total_predictions']}")
    print(f"auto_scored={summary['auto_scored']}")
    print(f"run_summary={display_path(args.out_dir / 'run_summary.json')}")
    print(f"run_report={display_path(args.out_dir / 'run_report.html')}")


if __name__ == "__main__":
    main()
