#!/usr/bin/env python3
"""Profile completed evaluation predictions by benchmark task and model.

The harness stores API-reported usage per logical item.  This report deliberately
does not invent a tokenizer: provider token counts are authoritative, especially
for multimodal and reasoning requests.  For legacy rows it reports an unknown
finish reason rather than guessing whether a response was generation-truncated.
"""

from __future__ import annotations

import argparse
import json
import math
import re
from collections import defaultdict
from pathlib import Path
from typing import Any


def percentile(values: list[int], p: float) -> int | None:
    if not values:
        return None
    ordered = sorted(values)
    # Nearest-rank avoids interpolated, fractional token counts and is robust
    # for small benchmark samples.
    return ordered[max(0, math.ceil(p * len(ordered)) - 1)]


def describe(values: list[int]) -> str:
    if not values:
        return "NA"
    return "/".join(str(percentile(values, p)) for p in (0.50, 0.95, 0.99)) + f"/{max(values)}"


def rows_from_run(run_dir: Path, filename: str) -> list[dict[str, Any]]:
    path = run_dir / filename
    latest: dict[str, dict[str, Any]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        item_id = row.get("item_id")
        if item_id is not None:
            latest[str(item_id)] = row
    return list(latest.values())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("reports/eval"))
    parser.add_argument("--include-support", action="store_true", help="include underscore-prefixed support runs")
    parser.add_argument("--output", type=Path, help="write the Markdown report to this path instead of stdout")
    args = parser.parse_args()

    groups: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for summary_path in args.root.rglob("summary.json"):
        relative = summary_path.relative_to(args.root)
        if not args.include_support and any(part.startswith("_") for part in relative.parts):
            continue
        run_dir = summary_path.parent
        predictions = run_dir / "predictions.jsonl"
        if not predictions.exists():
            continue
        try:
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if summary.get("run_status") != "complete":
            continue
        task = str(summary.get("benchmark") or relative.parts[0])
        for filename, phase, model_key in (
            ("predictions.jsonl", "prediction", "model"),
            ("extractions.jsonl", "extraction/judge", "extractor_model"),
        ):
            if not (run_dir / filename).exists():
                continue
            for row in rows_from_run(run_dir, filename):
                row["_run"] = str(run_dir)
                model = row.get(model_key) or (summary.get("model") if phase == "prediction" else "unknown")
                groups[(task, phase, str(model))].append(row)

    lines = [
        "# Evaluation request profile",
        "",
        "## Scope and interpretation",
        "",
        "- Includes completed, non-support runs under `reports/eval/`, with prediction and extraction/judge traffic reported separately.",
        "- Each `p50/p95/p99/max` cell is API-reported tokens across completed logical item rows; retries are accumulated within a row.",
        "- `answer` is completion minus billed reasoning tokens. `NA` means the provider did not expose enough information to separate the two.",
        "- `length-stop` counts provider-reported generation-limit completion reasons. `overlength-error` counts errors whose recorded message explicitly indicates a context/token-length rejection. Historic runs did not persist `finish_reason`; `unknown-stop` is therefore not evidence of normal completion.",
        "- `calls est.` uses provider-reported calls where present and falls back to recorded attempts for older artifacts. `largest round` is the largest completed run observed for that task/model/phase, not a planned workload.",
        "- `token usage (in/out/reason/total)` is the aggregate API-reported usage across all observed rows in that group. It excludes rows for which a provider did not report token usage.",
        "",
        "## Capacity planning",
        "",
        "For a target completion time of `T` seconds, use `ceil(largest round × P95 latency / T)` as a conservative starting concurrency for each phase. Apply the provider's own concurrency ceiling, and plan prediction and extraction/judge separately; an LLM-judged benchmark cannot finish faster than its slower phase. `NA` latency means the historic artifact did not record it, so a small live smoke run is needed before estimating its wall time.",
        "",
        "## Per-task and per-model profile",
        "",
        "| Task | Phase | Model | observed rows / largest round | input p50/p95/p99/max | output p50/p95/p99/max | reasoning p50/p95/p99/max | answer p50/p95/p99/max | total p50/p95/p99/max | token usage (in/out/reason/total) | latency p50/p95/p99/max s | calls est. | errors | overlength-error | length-stop | unknown-stop | CoT tokens unavailable |",
        "|---|---|---|---:|---|---|---|---|---|---|---|---|---:|---:|---:|---:|---:|",
    ]
    for (task, phase, model), rows in sorted(groups.items()):
        measured = [(r, r["usage"]) for r in rows if isinstance(r.get("usage"), dict)
                    and int((r.get("usage") or {}).get("total_tokens") or 0) > 0]
        usages = [usage for _, usage in measured]
        inputs = [int(u["prompt_tokens"]) for u in usages if isinstance(u.get("prompt_tokens"), (int, float))]
        outputs = [int(u["completion_tokens"]) for u in usages if isinstance(u.get("completion_tokens"), (int, float))]
        reasoning = [int(u["reasoning_tokens"]) for r, u in measured
                     if isinstance(u.get("reasoning_tokens"), (int, float))
                     and (int(u["reasoning_tokens"]) > 0 or not r.get("reasoning"))]
        answers = [max(0, int(u["completion_tokens"]) - int(u["reasoning_tokens"])) for r, u in measured
                   if isinstance(u.get("completion_tokens"), (int, float))
                   and isinstance(u.get("reasoning_tokens"), (int, float))
                   and (int(u["reasoning_tokens"]) > 0 or not r.get("reasoning"))]
        totals = [int(u["total_tokens"]) for u in usages if isinstance(u.get("total_tokens"), (int, float))]
        usage_totals = "/".join(f"{sum(int(u.get(field) or 0) for u in usages):,}" for field in
                                 ("prompt_tokens", "completion_tokens", "reasoning_tokens", "total_tokens"))
        calls = sum(max(int((r.get("usage") or {}).get("calls") or 0), int(r.get("attempts") or 1)) for r in rows)
        latency = [round(float(r["latency_seconds"])) for r in rows if isinstance(r.get("latency_seconds"), (int, float))]
        run_sizes: dict[str, int] = defaultdict(int)
        for row in rows:
            run_sizes[row["_run"]] += 1
        largest_round = max(run_sizes.values(), default=0)
        reasons = [reason for r in rows for reason in (r.get("finish_reasons") or [])]
        length_stops = sum(str(reason).lower() in {"length", "max_tokens", "token_limit"} for reason in reasons)
        # Pre-instrumentation records have no finish_reasons field at all; each
        # completed call is consequently unknown, not an observed normal stop.
        unknown_stops = max(0, calls - len(reasons)) + sum(reason is None for reason in reasons)
        errors = sum(bool(r.get("error")) for r in rows)
        overlength_errors = sum(bool(re.search(
            r"context.{0,30}(length|window)|token.{0,30}(limit|length)|input.{0,30}too long|maximum context|max context",
            str(r.get("error") or ""), re.IGNORECASE,
        )) for r in rows)
        cot_unavailable = sum(bool(r.get("reasoning")) and int((r.get("usage") or {}).get("reasoning_tokens") or 0) == 0 for r in rows)
        lines.append(f"| {task} | {phase} | {model} | {len(rows)} / {largest_round} | {describe(inputs)} | {describe(outputs)} | {describe(reasoning)} | {describe(answers)} | {describe(totals)} | {usage_totals} | {describe(latency)} | {calls} | {errors} | {overlength_errors} | {length_stops} | {unknown_stops} | {cot_unavailable} |")

    report = "\n".join(lines) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report, encoding="utf-8")
    else:
        print(report, end="")


if __name__ == "__main__":
    main()
