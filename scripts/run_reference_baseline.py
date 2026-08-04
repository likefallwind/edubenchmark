#!/usr/bin/env python3
"""Floors and human ceilings for judge-scored benchmarks (baseline layer L3).

For a benchmark whose score comes out of an LLM judge, "random guessing" has no
meaning — there is no answer space to sample from.  The only way to find the
floor is to feed the *real* judge a reply that contains no work, and see what it
gives.  Same trick, opposite direction, gets a ceiling: MRBench and the BEA 2025
dev set ship a human ``Expert`` tutor reply per dialogue, so re-scoring those
through our judge yields a human anchor measured by the same instrument as the
models.

Variants
--------
  refusal   "抱歉，我不确定。" — the most conservative possible reply
  echo      parrots the conversation/question back, no new content
  generic   fluent, encouraging, entirely content-free tutoring boilerplate.
            The important one: it probes whether the judge rewards *tone* over
            substance.
  expert    the dataset's human expert tutor reply   (mrbench_tutor / bea2025_tutor)
  novice    the dataset's human novice tutor reply   (mrbench_tutor / bea2025_tutor)

There is deliberately no ``empty`` variant: ``run_scoring`` classifies a blank
response as ``no_prediction`` and drops it from the denominator, so an empty
reply produces no score at all rather than a floor.

Mechanics: writes a synthetic ``predictions.jsonl``, then hands off to
``scripts/eval_benchmark.py --score-only``, which runs each adapter's real
``extract_answer`` — and for these benchmarks the judge call lives inside
``extract_answer``, so the judging path is exactly the production one.

Output is isolated under ``reports/eval/_baseline/<benchmark>/<variant>/`` so it
can never collide with, or be mistaken for, a real model run.  (CLAUDE.md: a
``--model`` matching an existing directory reuses its predictions as cache and
overwrites the scored artifacts.)

Costs API quota.  Defaults to 40 items; check the judge model matches the run
you intend to compare against before scaling up.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from eval.benchmarks import get_adapter  # noqa: E402
from eval.predictions_io import write_predictions  # noqa: E402

BASE_OUT = ROOT / "reports" / "eval" / "_baseline"
SEED = 20260804

REFUSAL_TEXT = "抱歉，我不确定。/ Sorry, I am not sure about this one."

GENERIC_TEXT = (
    "That's a really good question, and it's worth working through carefully. "
    "Let's take it one step at a time. First, think about what the problem is "
    "actually asking you to find. Then look at what you already know and what "
    "is still missing. Try writing down your reasoning as you go, so you can "
    "check each step against the one before it. You're on the right track — "
    "what do you think the first step should be?"
)


# --------------------------------------------------------------------------
# reference (human) responses, pulled from the raw datasets
# --------------------------------------------------------------------------


def _mrbench_reference_texts(tutor: str) -> dict[str, str]:
    path = ROOT / "sources" / "datasets" / "mrbench" / "MRBench_V2.json"
    rows = json.loads(path.read_text(encoding="utf-8"))
    out: dict[str, str] = {}
    for idx, entry in enumerate(rows):
        resp = (entry.get("anno_llm_responses") or {}).get(tutor) or {}
        text = str(resp.get("response") or "").strip()
        if text:
            out[f"c{idx}"] = text
    return out


def _bea_reference_texts(tutor: str) -> dict[str, str]:
    path = ROOT / "sources" / "datasets" / "bea2025" / "mrbench_v3_devset.json"
    rows = json.loads(path.read_text(encoding="utf-8"))
    out: dict[str, str] = {}
    for idx, entry in enumerate(rows):
        resp = (entry.get("tutor_responses") or {}).get(tutor) or {}
        text = str(resp.get("response") or "").strip()
        if text:
            out[f"c{idx}"] = text
    return out


REFERENCE_SOURCES: dict[str, Callable[[str], dict[str, str]]] = {
    "mrbench_tutor": _mrbench_reference_texts,
    "bea2025_tutor": _bea_reference_texts,
}


# --------------------------------------------------------------------------
# variants
# --------------------------------------------------------------------------


def _echo_text(item: dict[str, Any]) -> str:
    """Parrot the input back with no new content."""
    meta = item.get("meta") or {}
    source = str(meta.get("conversation_history") or meta.get("question") or item.get("text") or "")
    tail = "\n".join([ln for ln in source.strip().split("\n") if ln.strip()][-3:])
    return tail or "Let's look at what you just said again."


VARIANTS = {
    "refusal": lambda item, ref: REFUSAL_TEXT,
    "echo": lambda item, ref: _echo_text(item),
    "generic": lambda item, ref: GENERIC_TEXT,
    "expert": lambda item, ref: ref.get(str(item["item_id"]), ""),
    "novice": lambda item, ref: ref.get(str(item["item_id"]), ""),
}

DEGENERATE = ("refusal", "echo", "generic")
REFERENCE = ("expert", "novice")


# --------------------------------------------------------------------------


def _judge_of_existing_run(benchmark: str, model_slug: str | None) -> str | None:
    """The judge a real run used, so the baseline can be pinned to match it.

    Picks the *largest finished* run, not the first one on disk: several
    benchmarks keep a handful-of-items smoke run beside the full ones (and
    EduBench's real 12-model set lives under ``_judge-deepseek-v3.2/``), so
    taking whatever sorts first reads the judge off the wrong run.
    """
    base = ROOT / "reports" / "eval" / benchmark
    if not base.is_dir():
        return None
    if model_slug:
        candidates = [base / model_slug]
    else:
        candidates = [p for p in base.iterdir() if p.is_dir()]
        for judge_dir in [p for p in candidates if p.name.startswith("_judge-")]:
            candidates += [p for p in judge_dir.iterdir() if p.is_dir()]
    best: tuple[int, str] | None = None
    for cand in candidates:
        path = cand / "summary.json"
        if not path.exists():
            continue
        try:
            summary = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        if summary.get("run_status") == "running":
            continue
        # Same fallback as the run-start guard in eval_benchmark.py: older runs
        # left the top-level field null and only recorded the judge inside
        # extra_metrics.  Missing this is how a baseline silently gets judged by
        # a different model than the run it is meant to anchor.
        judge = summary.get("judge_model")
        if not judge and isinstance(summary.get("extra_metrics"), dict):
            judge = summary["extra_metrics"].get("judge_model")
        if not judge:
            continue
        scored = int(summary.get("scored") or 0)
        if best is None or scored > best[0]:
            best = (scored, str(judge))
    return best[1] if best else None


def _select_items(adapter, limit: int) -> list[dict[str, Any]]:
    import random

    items = adapter.load_items()
    if limit and len(items) > limit:
        rng = random.Random(SEED)
        picked = sorted(rng.sample(range(len(items)), limit))
        items = [items[i] for i in picked]
    return items


def run_variant(
    benchmark: str,
    variant: str,
    limit: int,
    extractor_model: str,
    extract_concurrency: int,
    compare_run: str | None,
    dry_run: bool,
) -> int:
    adapter = get_adapter(benchmark)

    reference: dict[str, str] = {}
    if variant in REFERENCE:
        loader = REFERENCE_SOURCES.get(benchmark)
        if loader is None:
            print(f"  SKIP {benchmark}/{variant}: 该 benchmark 没有自带人类参照回复")
            return 0
        reference = loader(variant.capitalize())
        if not reference:
            print(f"  SKIP {benchmark}/{variant}: 数据集里没有 {variant.capitalize()} 条目")
            return 0

    items = _select_items(adapter, limit)
    if variant in REFERENCE:
        items = [it for it in items if reference.get(str(it["item_id"]))]
        if not items:
            print(f"  SKIP {benchmark}/{variant}: 抽样到的题目都没有 {variant} 回复")
            return 0

    out_dir = BASE_OUT / benchmark / variant
    out_dir.mkdir(parents=True, exist_ok=True)

    make = VARIANTS[variant]
    model_tag = f"_baseline_{variant}"
    rows = [
        {
            "item_id": str(item["item_id"]),
            "response": make(item, reference),
            "model": model_tag,
        }
        for item in items
    ]
    rows = [r for r in rows if r["response"].strip()]
    if not rows:
        print(f"  SKIP {benchmark}/{variant}: 没有产出任何非空回复")
        return 0

    item_list = out_dir / "item_list.txt"
    item_list.write_text("\n".join(r["item_id"] for r in rows) + "\n", encoding="utf-8")

    expected_judge = _judge_of_existing_run(benchmark, compare_run)
    resolved_judge = adapter.resolved_judge_model(extractor_model)
    if expected_judge and resolved_judge and expected_judge != resolved_judge:
        print(
            f"  !! judge 不一致：正式 run 用 {expected_judge}，本次会用 {resolved_judge}。"
            f"两边不可比——先把对应的 *_JUDGE_MODEL 环境变量设成 {expected_judge} 再跑。"
        )
        return 1

    print(f"  {benchmark}/{variant}: {len(rows)} 题 → {out_dir}  judge={resolved_judge}")
    if dry_run:
        print(f"    (dry-run) 示例回复: {rows[0]['response'][:120]!r}")
        return 0

    write_predictions(out_dir / "predictions.jsonl", rows)
    (out_dir / "baseline_meta.json").write_text(
        json.dumps(
            {
                "benchmark": benchmark,
                "variant": variant,
                "layer": "L3_reference" if variant in REFERENCE else "L3_degenerate",
                "n_items": len(rows),
                "seed": SEED,
                "judge_model": resolved_judge,
                "judge_model_of_real_run": expected_judge,
                "note": (
                    "人类参照回复，由数据集自带并用我们的 judge 复评——与模型分同一把尺"
                    if variant in REFERENCE
                    else "与题目无关的退化回复，用于量出 judge 打分的地板"
                ),
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    cmd = [
        sys.executable,
        str(ROOT / "scripts" / "eval_benchmark.py"),
        "--benchmark",
        benchmark,
        "--model",
        model_tag,
        "--out-dir",
        str(out_dir),
        "--item-list",
        str(item_list),
        "--extractor-model",
        extractor_model,
        "--extract-concurrency",
        str(extract_concurrency),
        "--score-only",
    ]
    return subprocess.call(cmd, cwd=str(ROOT), env=os.environ.copy())


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--benchmark", action="append", required=True, help="benchmark 名（可重复）")
    ap.add_argument(
        "--variant",
        action="append",
        choices=sorted(VARIANTS),
        help=f"默认跑退化三件套 {DEGENERATE}；expert/novice 仅 mrbench_tutor / bea2025_tutor 可用",
    )
    ap.add_argument("--limit", type=int, default=40, help="每个变体的题数（默认 40）")
    ap.add_argument("--extractor-model", default="MiniMax-M2.7")
    ap.add_argument("--extract-concurrency", type=int, default=4)
    ap.add_argument(
        "--compare-run",
        default=None,
        help="正式 run 的模型目录名，用来核对 judge 是否一致（默认取该 benchmark 下任一已完成 run）",
    )
    ap.add_argument("--dry-run", action="store_true", help="只打印计划与样例回复，不写文件、不调 API")
    args = ap.parse_args()

    variants = args.variant or list(DEGENERATE)
    failures = 0
    for benchmark in args.benchmark:
        print(f"[{benchmark}]")
        for variant in variants:
            rc = run_variant(
                benchmark,
                variant,
                args.limit,
                args.extractor_model,
                args.extract_concurrency,
                args.compare_run,
                args.dry_run,
            )
            if rc:
                failures += 1
                print(f"  FAILED {benchmark}/{variant} (rc={rc})")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
