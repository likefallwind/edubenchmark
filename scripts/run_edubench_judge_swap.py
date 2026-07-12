#!/usr/bin/env python3
"""M2 judge-swap experiment for EduBench (mapping validation plan §2.5).

The original EduBench run (reports/eval/edubench/) was judged once by
deepseek-v3.2. This script re-judges a stratified sample of the *same*
responses with second/third judges and measures inter-judge agreement, to
decide whether cross-family low correlations reflect real construct
differences (-> revise mapping) or judge variance (-> judge governance).

Phases (all resumable / idempotent):
  --sample            build _judge_swap/samples.jsonl (50 responses x 5 tasks,
                      round-robin over the 11 models, seed fixed)
  --judge MODEL       re-judge every sample with MODEL (appends to
                      _judge_swap/judgments_<slug>.jsonl, skips done ids)
  --analyze           per-metric + overall + model-level agreement between the
                      original judge and each new judge -> agreement.{json,md}

The rubric prompt is reconstructed from the official EduBench paper's 12
principle definitions (arXiv:2505.16160; the colleague's exact judge prompt
was not shipped with the data). Judge identity AND prompt wording therefore
both vary vs. the original judgments — agreement numbers are a joint
robustness test, which is the stricter reading M2 needs.
"""

from __future__ import annotations

import argparse
import json
import math
import random
import re
import sys
import threading
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from statistics import fmean

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from eval.providers import build_client, model_slug  # noqa: E402

EVAL_DIR = ROOT / "reports" / "eval" / "edubench"
OUT_DIR = EVAL_DIR / "_judge_swap"
TASKS = ["IP", "PCC", "PLS", "QG", "TMG"]
PER_TASK = 50
SEED = 20260712

METRICS = [
    "instruction_following",
    "tone_style_consistency",
    "content_relevance_scope_control",
    "scenario_element_integration",
    "basic_factual_accuracy",
    "domain_knowledge_accuracy",
    "reasoning_process_rigor",
    "error_identification_correction_accuracy",
    "clarity_concision_inspiration",
    "motivation_guidance_positive_feedback",
    "personalized_adaptation_learning_support",
    "higher_order_thinking_ability_development",
]

# Official EduBench principle definitions (paper section 3 / appendix F).
METRIC_DEFS = {
    "instruction_following": (
        "Instruction Following & Task Completion: whether the response properly "
        "executes the assigned task and adheres to the given instructions within "
        "the educational context."
    ),
    "tone_style_consistency": (
        "Role & Tone Consistency: alignment between the response's communication "
        "style and the persona/tone the scenario requires."
    ),
    "content_relevance_scope_control": (
        "Content Relevance & Scope Control: whether the information stays focused "
        "on the scenario requirements without unnecessary digressions."
    ),
    "scenario_element_integration": (
        "Scenario Element Integration: how well context-specific details and "
        "educational elements relevant to this scenario are incorporated."
    ),
    "basic_factual_accuracy": (
        "Basic Factual Accuracy: correctness of the factual information presented."
    ),
    "domain_knowledge_accuracy": (
        "Domain Knowledge Accuracy: correctness of specialized subject-matter "
        "content within the academic discipline."
    ),
    "reasoning_process_rigor": (
        "Reasoning Process Rigor: logical soundness of the reasoning applied to "
        "problems and explanations."
    ),
    "error_identification_correction_accuracy": (
        "Error Identification & Correction Precision: accuracy in detecting "
        "mistakes and the quality of proposed corrections."
    ),
    "clarity_concision_inspiration": (
        "Clarity, Simplicity & Inspiration: communicative clarity, simplicity, and "
        "capacity to motivate learner engagement."
    ),
    "motivation_guidance_positive_feedback": (
        "Motivation, Guidance & Positive Feedback: encouragement, directional "
        "support, and constructive feedback quality."
    ),
    "personalized_adaptation_learning_support": (
        "Personalization, Adaptation & Learning Support: tailoring to individual "
        "learner needs and supportive scaffolding."
    ),
    "higher_order_thinking_ability_development": (
        "Higher-Order Thinking & Skill Development: encouragement of critical "
        "analysis and competency advancement."
    ),
}

JUDGE_PROMPT = """You are an expert evaluator of AI systems used in education. You will see the task that was given to an AI model and the model's response. Score the response on 12 metrics, each an integer from 1 (very poor) to 10 (excellent). Judge only what is in the response; if a metric is barely elicited by this task, score how well the response handles that aspect where applicable.

[TASK GIVEN TO THE MODEL]
{prompt}

[MODEL RESPONSE]
{response}

Metrics (score each):
{metric_list}

Return ONLY a JSON object, no other text:
{{"scores": {{{score_keys}}}, "rationale": "<2-3 sentence justification>"}}"""


def read_jsonl(path: Path):
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                yield json.loads(line)


def sample_id(item_id: str, model: str) -> str:
    return f"{item_id}::{model}"


def build_samples() -> None:
    models = sorted(
        d.name
        for d in EVAL_DIR.iterdir()
        if d.is_dir() and not d.name.startswith("_") and (d.name != "_judge_swap")
        and (d / "scored.jsonl").is_file()
    )
    prompts: dict[tuple[str, str], str] = {}
    rows_by_task: dict[str, list[dict]] = defaultdict(list)
    for model in models:
        for rec in read_jsonl(EVAL_DIR / model / "predictions.jsonl"):
            prompts[(rec["item_id"], model)] = (rec.get("metadata") or {}).get(
                "prompt", ""
            )
        for rec in read_jsonl(EVAL_DIR / model / "scored.jsonl"):
            task = (rec.get("buckets") or {}).get("task")
            if task not in TASKS:
                continue
            dims = rec.get("dimension_scores") or {}
            clean = {
                m: float(dims[m])
                for m in METRICS
                if isinstance(dims.get(m), (int, float)) and math.isfinite(float(dims[m]))
            }
            if len(clean) < len(METRICS):
                continue
            rows_by_task[task].append(
                {
                    "sample_id": sample_id(rec["item_id"], model),
                    "item_id": rec["item_id"],
                    "model": model,
                    "task": task,
                    "lang": (rec.get("buckets") or {}).get("lang"),
                    "prompt": prompts.get((rec["item_id"], model), ""),
                    "response": rec.get("response", ""),
                    "orig_judge": rec.get("judge_model"),
                    "orig_scores": clean,
                }
            )
    rng = random.Random(SEED)
    samples = []
    for task in TASKS:
        by_model: dict[str, list[dict]] = defaultdict(list)
        for row in rows_by_task[task]:
            if row["prompt"] and row["response"]:
                by_model[row["model"]].append(row)
        for rows in by_model.values():
            rng.shuffle(rows)
        # round-robin across models until PER_TASK collected
        picked, idx = [], 0
        model_cycle = sorted(by_model)
        while len(picked) < PER_TASK and any(by_model[m] for m in model_cycle):
            m = model_cycle[idx % len(model_cycle)]
            idx += 1
            if by_model[m]:
                picked.append(by_model[m].pop())
        samples.extend(picked)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / "samples.jsonl"
    with out.open("w", encoding="utf-8") as handle:
        for row in samples:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    per_task = defaultdict(int)
    per_model = defaultdict(int)
    for row in samples:
        per_task[row["task"]] += 1
        per_model[row["model"]] += 1
    print(f"wrote {len(samples)} samples to {out}")
    print("per task:", dict(per_task))
    print("per model:", dict(sorted(per_model.items())))


def build_judge_prompt(row: dict) -> str:
    metric_list = "\n".join(
        f"{i + 1}. {m} — {METRIC_DEFS[m]}" for i, m in enumerate(METRICS)
    )
    score_keys = ", ".join(f'"{m}": <int>' for m in METRICS)
    return JUDGE_PROMPT.format(
        prompt=row["prompt"],
        response=row["response"],
        metric_list=metric_list,
        score_keys=score_keys,
    )


def parse_judge_output(text: str) -> dict | None:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None
    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError:
        return None
    scores = data.get("scores")
    if not isinstance(scores, dict):
        return None
    clean = {}
    for m in METRICS:
        v = scores.get(m)
        if isinstance(v, (int, float)) and 0 <= float(v) <= 10:
            clean[m] = float(v)
    if len(clean) < len(METRICS):
        return None
    return {"scores": clean, "rationale": str(data.get("rationale", ""))[:2000]}


def run_judge(judge_model: str, concurrency: int, max_tokens: int | None) -> None:
    samples = list(read_jsonl(OUT_DIR / "samples.jsonl"))
    out_path = OUT_DIR / f"judgments_{model_slug(judge_model)}.jsonl"
    done = set()
    if out_path.exists():
        for rec in read_jsonl(out_path):
            if rec.get("scores"):
                done.add(rec["sample_id"])
    todo = [s for s in samples if s["sample_id"] not in done]
    print(f"judge={judge_model} total={len(samples)} done={len(done)} todo={len(todo)}")
    if not todo:
        return
    client = build_client(judge_model, timeout=300)
    lock = threading.Lock()
    failures = 0

    def one(row: dict) -> dict | None:
        prompt = build_judge_prompt(row)
        for attempt in range(3):
            try:
                text = client.chat(
                    [{"role": "user", "content": prompt}], max_tokens=max_tokens
                )
            except Exception as exc:  # noqa: BLE001
                if attempt == 2:
                    print(f"FAIL {row['sample_id']}: {exc}")
                    return None
                continue
            parsed = parse_judge_output(text)
            if parsed:
                return {
                    "sample_id": row["sample_id"],
                    "judge_model": judge_model,
                    "scores": parsed["scores"],
                    "rationale": parsed["rationale"],
                }
            if attempt == 2:
                print(f"UNPARSED {row['sample_id']}: {text[:200]!r}")
        return None

    with out_path.open("a", encoding="utf-8") as handle:
        with ThreadPoolExecutor(max_workers=concurrency) as pool:
            futures = {pool.submit(one, row): row for row in todo}
            finished = 0
            for future in as_completed(futures):
                rec = future.result()
                finished += 1
                if rec is None:
                    failures += 1
                    continue
                with lock:
                    handle.write(json.dumps(rec, ensure_ascii=False) + "\n")
                    handle.flush()
                if finished % 25 == 0:
                    print(f"  {finished}/{len(todo)} done ({failures} failed)")
    print(f"judge={judge_model} finished, failures={failures}")


# ---------- agreement analysis ----------

def rankdata(values: list[float]) -> list[float]:
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        avg = (i + j) / 2 + 1
        for k in range(i, j + 1):
            ranks[order[k]] = avg
        i = j + 1
    return ranks


def spearman(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) < 3:
        return None
    rx, ry = rankdata(xs), rankdata(ys)
    mx, my = fmean(rx), fmean(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    dx = math.sqrt(sum((a - mx) ** 2 for a in rx))
    dy = math.sqrt(sum((b - my) ** 2 for b in ry))
    if dx == 0 or dy == 0:
        return None
    return num / (dx * dy)


def quadratic_weighted_kappa(xs: list[float], ys: list[float]) -> float | None:
    """QWK on integer 1-10 scores."""
    if len(xs) < 3:
        return None
    cats = list(range(0, 11))
    n = len(cats)
    xi = [min(10, max(0, round(v))) for v in xs]
    yi = [min(10, max(0, round(v))) for v in ys]
    obs = [[0.0] * n for _ in range(n)]
    for a, b in zip(xi, yi):
        obs[a][b] += 1
    total = len(xi)
    hist_x = [xi.count(c) for c in cats]
    hist_y = [yi.count(c) for c in cats]
    num = den = 0.0
    for i in range(n):
        for j in range(n):
            w = ((i - j) ** 2) / ((n - 1) ** 2)
            expected = hist_x[i] * hist_y[j] / total
            num += w * obs[i][j]
            den += w * expected
    if den == 0:
        return None
    return 1 - num / den


def analyze() -> None:
    samples = {row["sample_id"]: row for row in read_jsonl(OUT_DIR / "samples.jsonl")}
    judges: dict[str, dict[str, dict]] = {}
    for path in sorted(OUT_DIR.glob("judgments_*.jsonl")):
        name = path.stem.removeprefix("judgments_")
        judges[name] = {rec["sample_id"]: rec["scores"] for rec in read_jsonl(path)}
    if not judges:
        print("no judgments yet")
        return
    orig_name = next(iter({row["orig_judge"] for row in samples.values()}))

    def scores_of(source: str, sid: str) -> dict | None:
        if source == "original":
            return samples[sid]["orig_scores"]
        return judges.get(source, {}).get(sid)

    sources = ["original"] + sorted(judges)
    pairs = [(a, b) for i, a in enumerate(sources) for b in sources[i + 1 :]]

    result: dict = {
        "n_samples": len(samples),
        "original_judge": orig_name,
        "new_judges": {name: len(scored) for name, scored in judges.items()},
        "pairs": {},
    }
    md = [
        "# EduBench 换裁判实验（M2，2026-07-12）",
        "",
        f"样本：{len(samples)} 条 response（5 任务 × 每任务 {PER_TASK}，横跨 11 个被测模型），"
        f"原裁判 {orig_name}，新裁判 {', '.join(sorted(judges))}。",
        "rubric 按论文官方 12 指标定义重建（同事原始判分 prompt 未随数据提供），"
        "所以对比原裁判的一致性是\"裁判+prompt 同时更换\"的联合稳健性，读数会偏严。",
        "",
    ]
    for a, b in pairs:
        common = [
            sid
            for sid in samples
            if scores_of(a, sid) and scores_of(b, sid)
        ]
        per_metric = {}
        for metric in METRICS:
            xs = [scores_of(a, sid)[metric] for sid in common]
            ys = [scores_of(b, sid)[metric] for sid in common]
            per_metric[metric] = {
                "spearman": round(spearman(xs, ys), 3) if spearman(xs, ys) is not None else None,
                "qwk": round(quadratic_weighted_kappa(xs, ys), 3)
                if quadratic_weighted_kappa(xs, ys) is not None
                else None,
                "mean_a": round(fmean(xs), 2) if xs else None,
                "mean_b": round(fmean(ys), 2) if ys else None,
            }
        overall_x = [fmean([scores_of(a, sid)[m] for m in METRICS]) for sid in common]
        overall_y = [fmean([scores_of(b, sid)[m] for m in METRICS]) for sid in common]
        overall = {
            "spearman": round(spearman(overall_x, overall_y), 3),
            "n": len(common),
        }
        # model-level ranking agreement (mean overall score per tested model)
        per_model_a: dict[str, list[float]] = defaultdict(list)
        per_model_b: dict[str, list[float]] = defaultdict(list)
        for sid, ox, oy in zip(common, overall_x, overall_y):
            per_model_a[samples[sid]["model"]].append(ox)
            per_model_b[samples[sid]["model"]].append(oy)
        models = sorted(per_model_a)
        model_rank_rho = spearman(
            [fmean(per_model_a[m]) for m in models],
            [fmean(per_model_b[m]) for m in models],
        )
        key = f"{a}__vs__{b}"
        result["pairs"][key] = {
            "n_common": len(common),
            "overall_response_spearman": overall["spearman"],
            "model_rank_spearman_n11": round(model_rank_rho, 3)
            if model_rank_rho is not None
            else None,
            "per_metric": per_metric,
        }
        md += [
            f"## {a} vs {b}（n={len(common)}）",
            "",
            f"- response 级总分 Spearman：**{overall['spearman']}**",
            f"- 模型排名级 Spearman（{len(models)} 模型）：**{round(model_rank_rho, 3) if model_rank_rho is not None else '—'}**",
            "",
            "| 指标 | response 级 ρ | QWK | 均分 A | 均分 B |",
            "|---|---|---|---|---|",
        ]
        for metric in METRICS:
            pm = per_metric[metric]
            md.append(
                f"| {metric} | {pm['spearman']} | {pm['qwk']} | {pm['mean_a']} | {pm['mean_b']} |"
            )
        md.append("")

    (OUT_DIR / "agreement.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    (OUT_DIR / "agreement.md").write_text("\n".join(md), encoding="utf-8")
    print(f"wrote {OUT_DIR}/agreement.json and .md")
    for key, pair in result["pairs"].items():
        print(
            key,
            "overall_rho=", pair["overall_response_spearman"],
            "model_rank_rho=", pair["model_rank_spearman_n11"],
        )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sample", action="store_true")
    parser.add_argument("--judge", help="judge model name, e.g. deepseek-v4-pro / glm-5.1")
    parser.add_argument("--analyze", action="store_true")
    parser.add_argument("--concurrency", type=int, default=4)
    parser.add_argument("--max-tokens", type=int, default=None)
    args = parser.parse_args()
    if args.sample:
        build_samples()
    if args.judge:
        run_judge(args.judge, args.concurrency, args.max_tokens)
    if args.analyze:
        analyze()
    if not (args.sample or args.judge or args.analyze):
        parser.print_help()


if __name__ == "__main__":
    main()
