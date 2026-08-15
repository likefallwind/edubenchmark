#!/usr/bin/env python3
"""Calibrate the rubric-derived human estimate against a known human value.

The open question this answers: **if a benchmark's paper reports no human score,
can we estimate one from its rubric?** The method is a modified-Angoff standard
setting — for every rubric criterion, estimate the probability that a competent
human would satisfy it, then aggregate with the benchmark's own formula. That
gives a number; whether the number means anything is an empirical question, and
this script is the experiment that settles it.

Design constraints, each of which exists because dropping it would make the
result uninterpretable:

* **Blind.** The estimator sees the rubric, the student's question and the
  images. It never sees a model response, the dataset's reference answer, or the
  published human value. Anything else and we are measuring recall, not
  estimation.
* **Probabilities, not scores.** Per-criterion P(a competent human satisfies
  this) aggregates linearly into the benchmark's own headline; a 0-6 guess does
  not decompose.
* **The estimator must not be the judge, nor its family.** MMTutorBench's judge
  is MiniMax-M3, so MiniMax models are refused here — otherwise the experiment
  measures a model family agreeing with itself.
* **A novice control is mandatory.** The same procedure is run for "a novice
  teacher". If expert and novice come out the same, the procedure is not
  tracking competence at all and the whole method fails, regardless of how close
  the expert number lands. This control can falsify the method on its own.
* **The verdict thresholds are fixed in code before the run** (`VERDICT_BAND`),
  so a near miss cannot be re-read as a pass after the fact.

Aggregation reuses the adapter's own dimension list and weighting, matching the
convention in `build_benchmark_baselines.py`: drive the real scoring path with
synthetic inputs rather than re-deriving the formula by hand.

Outputs `reports/eval/_baseline/_rubric_estimate_calibration/<benchmark>/`.
"""

from __future__ import annotations

import argparse
import concurrent.futures as futures
import json
import random
import statistics
import sys
import threading
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from eval.benchmarks import get_adapter  # noqa: E402
from eval.minimax_client import image_part, text_part  # noqa: E402
from eval.providers import build_client  # noqa: E402

OUT_ROOT = ROOT / "reports" / "eval" / "_baseline" / "_rubric_estimate_calibration"

# Absolute error, on the benchmark headline's own scale normalised to 0-1, at
# which the method is judged usable. Fixed before the run — see module docstring.
VERDICT_BAND = 0.10
# The novice control must land at least this far below the expert condition,
# otherwise the procedure is not discriminating competence.
MIN_EXPERT_NOVICE_SEPARATION = 0.05

# Estimator models must not share a family with the benchmark's judge.
FORBIDDEN_ESTIMATOR_PREFIXES = ("minimax",)

PERSONAS = {
    "expert": (
        "a COMPETENT, EXPERIENCED human mathematics tutor: formally trained, several "
        "years of one-to-one tutoring experience, working without time pressure, with "
        "full sight of the student's work and the images"
    ),
    "novice": (
        "a NOVICE human tutor: a beginning teaching assistant with subject knowledge but "
        "little tutoring practice, working without time pressure, with full sight of the "
        "student's work and the images"
    ),
}

# Known human values to calibrate against, on the benchmark's headline scale.
CALIBRATION_TRUTH: dict[str, dict[str, Any]] = {
    "mmtutorbench": {
        "headline": "paper_weighted_score_0_to_6",
        "scale_max": 6.0,
        "human_value": 5.85,
        "human_per_dimension": {
            "insight_identification": 0.97,
            "operation_prescription": 0.97,
            "operation_execution": 0.97,
            "solution_scope_control": 0.97,
            "brevity": 0.98,
            "coherence": 0.98,
        },
        "source": "MMTutorBench (arXiv:2510.23477), human row: total 5.85 over six equally weighted binary dimensions",
        "truth_caveat": (
            "论文的 5.85 是人类回复经它自己的 GPT-o4-mini rubric judge 打出来的。"
            "我们估的是「人类满足每条 criterion 的概率」，同样以 rubric 为准绳，"
            "所以这个对比检验的是「rubric 估计能否复现 rubric 式人类评测」。"
            "六维都是 0/1 二元判定，比 1-10 量表的 judge 漂移小，但跨 judge 的残差仍在。"
        ),
    },
}


def _estimate_prompt(item: dict[str, Any], persona_key: str) -> str:
    rubric = item["meta"]["rubric"]
    lines = [
        "You are performing a standard-setting exercise (modified Angoff method) for an "
        "educational benchmark. You are NOT solving the problem and you are NOT grading "
        "any candidate answer — no candidate answer exists here.",
        "",
        f"Estimate what {PERSONAS[persona_key]} would achieve.",
        "",
        "You are given: the student's question, the accompanying image(s), and the rubric "
        "that a grader would apply to a tutoring response. For EACH rubric criterion, "
        "estimate the probability, between 0.00 and 1.00, that a response written by that "
        "person would satisfy the criterion's condition_for_1.",
        "",
        "Judge each criterion independently and on its own terms. Some criteria are about "
        "getting the mathematics right; others are about brevity, scope control or "
        "coherence, where a knowledgeable person can still fail. Do not assume a competent "
        "human satisfies everything — estimate honestly, including probabilities well below "
        "1.0 where the criterion is genuinely demanding or easy to violate.",
        "",
        f"### Task description given to the grader\n{rubric.get('task_description')}",
        "",
        "### Rubric criteria",
    ]
    for crit in rubric.get("evaluation_criteria") or []:
        lines += [
            f"- id: {crit.get('id')}",
            f"  criterion: {crit.get('criterion')}",
            f"  condition_for_1: {crit.get('condition_for_1')}",
            f"  condition_for_0: {crit.get('condition_for_0')}",
        ]
    ids = [str(c.get("id")) for c in rubric.get("evaluation_criteria") or []]
    lines += [
        "",
        f"### Student's question\n{item['meta'].get('question')}",
        "",
        "Return ONE JSON object and nothing else, mapping every criterion id to your "
        "probability estimate, plus a one-sentence rationale:",
        "{" + ", ".join(f'"{i}": <0.00-1.00>' for i in ids) + ', "rationale": "..."}',
    ]
    return "\n".join(lines)


def _parse_probs(reply: str, ids: list[str]) -> dict[str, float] | None:
    start, end = reply.find("{"), reply.rfind("}")
    if start < 0 or end <= start:
        return None
    try:
        obj = json.loads(reply[start : end + 1])
    except json.JSONDecodeError:
        return None
    out: dict[str, float] = {}
    for key in ids:
        value = obj.get(key)
        if not isinstance(value, (int, float)):
            return None
        out[key] = max(0.0, min(1.0, float(value)))
    return out


def run_condition(
    items: list[dict[str, Any]],
    dimensions: list[str],
    estimator: str,
    persona_key: str,
    concurrency: int,
    with_images: bool,
) -> dict[str, Any]:
    client = build_client(estimator)
    lock = threading.Lock()
    rows: list[dict[str, Any]] = []
    failures: list[str] = []

    def one(item: dict[str, Any]) -> None:
        content: list[dict[str, Any]] = [text_part(_estimate_prompt(item, persona_key))]
        if with_images:
            for path in item.get("image_paths") or []:
                content.append(image_part(Path(path)))
        try:
            reply = client.chat([{"role": "user", "content": content}], model=estimator)
        except Exception as exc:  # noqa: BLE001 - record and continue; one item must not kill the run
            with lock:
                failures.append(f"{item['item_id']}: {type(exc).__name__}: {exc}")
            return
        probs = _parse_probs(reply, dimensions)
        with lock:
            if probs is None:
                failures.append(f"{item['item_id']}: unparsed reply")
            else:
                rows.append({"item_id": item["item_id"], "probs": probs})

    with futures.ThreadPoolExecutor(max_workers=concurrency) as pool:
        list(pool.map(one, items))

    if not rows:
        return {"estimator": estimator, "condition": persona_key, "n": 0, "failures": failures}

    # Same aggregation as MMTutorBenchAdapter.extra_summary: per-dimension mean,
    # summed over the six equally weighted binary dimensions.
    per_dim = {d: statistics.fmean(r["probs"][d] for r in rows) for d in dimensions}
    return {
        "estimator": estimator,
        "condition": persona_key,
        "n": len(rows),
        "n_failed": len(failures),
        "per_dimension_estimate": {d: round(v, 4) for d, v in per_dim.items()},
        "predicted_headline": round(sum(per_dim.values()), 4),
        "per_dimension_sd": {
            d: round(statistics.pstdev([r["probs"][d] for r in rows]), 4) for d in dimensions
        },
        "failures": failures[:10],
        "rows": rows,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--benchmark", default="mmtutorbench", choices=sorted(CALIBRATION_TRUTH))
    ap.add_argument("--limit", type=int, default=50, help="sampled items (seeded, reproducible)")
    ap.add_argument("--seed", type=int, default=20260815)
    ap.add_argument(
        "--estimator-model",
        action="append",
        default=None,
        help="repeatable; must not share a family with the benchmark judge",
    )
    ap.add_argument("--concurrency", type=int, default=6)
    ap.add_argument("--no-images", action="store_true", help="ablation: withhold images from the estimator")
    ap.add_argument("--out-dir", type=Path, default=None)
    args = ap.parse_args()

    # Both must be vision-capable — the human being modelled sees the figures, so
    # an estimator that cannot is answering a different question. Two vendors, so
    # the spread across them is real disagreement rather than one house style.
    # doubao-seed-2.1-turbo is not in the gateway's /models listing but serves
    # fine (verified 2026-08-15, routes to doubao-seed-2-1-turbo-260628); that
    # listing has been wrong in both directions before.
    estimators = args.estimator_model or ["doubao-seed-2.1-turbo", "kimi-k2.6"]
    for name in estimators:
        if name.lower().startswith(FORBIDDEN_ESTIMATOR_PREFIXES):
            raise SystemExit(
                f"refusing estimator {name}: same family as the benchmark judge, "
                "the calibration would measure self-agreement"
            )

    truth = CALIBRATION_TRUTH[args.benchmark]
    adapter = get_adapter(args.benchmark)
    all_items = adapter.load_items()
    rng = random.Random(args.seed)
    items = rng.sample(all_items, min(args.limit, len(all_items)))
    dimensions = [str(c.get("id")) for c in (items[0]["meta"]["rubric"].get("evaluation_criteria") or [])]

    out_dir = args.out_dir or (OUT_ROOT / args.benchmark)
    out_dir.mkdir(parents=True, exist_ok=True)

    conditions: list[dict[str, Any]] = []
    for estimator in estimators:
        for persona in ("expert", "novice"):
            print(f"[run] {estimator} / {persona} / {len(items)} items / conc={args.concurrency}")
            result = run_condition(
                items, dimensions, estimator, persona, args.concurrency, not args.no_images
            )
            print(
                f"       n={result.get('n')} failed={result.get('n_failed')} "
                f"predicted={result.get('predicted_headline')}"
            )
            conditions.append(result)

    with (out_dir / "estimates.jsonl").open("w", encoding="utf-8") as fh:
        for cond in conditions:
            for row in cond.pop("rows", []):
                fh.write(
                    json.dumps(
                        {"estimator": cond["estimator"], "condition": cond["condition"], **row},
                        ensure_ascii=False,
                    )
                    + "\n"
                )

    scale = float(truth["scale_max"])
    experts = [c for c in conditions if c["condition"] == "expert" and c.get("n")]
    novices = [c for c in conditions if c["condition"] == "novice" and c.get("n")]
    errors = [(c["predicted_headline"] - truth["human_value"]) / scale for c in experts]
    separations = [
        (e["predicted_headline"] - n["predicted_headline"]) / scale
        for e in experts
        for n in novices
        if e["estimator"] == n["estimator"]
    ]

    if not experts:
        verdict, why = "inconclusive", "专家条件没有任何可用估计，全部失败或无法解析。"
    elif separations and max(separations) < MIN_EXPERT_NOVICE_SEPARATION:
        verdict, why = (
            "rejected",
            f"新手对照没分开（最大间隔 {max(separations):.4f} < {MIN_EXPERT_NOVICE_SEPARATION}）——"
            "该程序没有在区分能力水平，主结果再准也不能用。",
        )
    elif all(abs(e) <= VERDICT_BAND for e in errors):
        verdict, why = "passed", f"专家条件全部落在 ±{VERDICT_BAND} 带内，且新手对照分得开。"
    elif len(errors) > 1 and (all(e > 0 for e in errors) or all(e < 0 for e in errors)):
        verdict, why = (
            "conditional",
            f"误差同号（{[round(e, 4) for e in errors]}），存在系统性偏差；"
            "可用但必须带修正项与误差棒。",
        )
    else:
        verdict, why = (
            "rejected",
            f"误差超出 ±{VERDICT_BAND} 且无一致方向（{[round(e, 4) for e in errors]}），无法修正。",
        )

    summary = {
        "benchmark": args.benchmark,
        "method": "modified Angoff standard setting over the benchmark's own rubric",
        "generated_by": "scripts/run_rubric_estimate_calibration.py",
        "blind": "估计器只见 rubric + 题目 + 图，未见任何模型回复、参考答案或论文数值",
        "n_items": len(items),
        "seed": args.seed,
        "with_images": not args.no_images,
        "estimators": estimators,
        "judge_not_used": "校准不经过 judge；估计器与 benchmark judge 不同族（见 FORBIDDEN_ESTIMATOR_PREFIXES）",
        "truth": truth,
        "conditions": conditions,
        "expert_error_normalised": [round(e, 4) for e in errors],
        "expert_novice_separation_normalised": [round(s, 4) for s in separations],
        "verdict_band": VERDICT_BAND,
        "min_expert_novice_separation": MIN_EXPERT_NOVICE_SEPARATION,
        "verdict": verdict,
        "verdict_reason": why,
    }
    (out_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"\nwrote {out_dir}/summary.json")
    print(f"  真值 {truth['human_value']} / {scale}")
    for cond in conditions:
        print(
            f"  {cond['estimator']:24s} {cond['condition']:7s} "
            f"predicted={cond.get('predicted_headline')} n={cond.get('n')}"
        )
    print(f"  判定: {verdict} — {why}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
