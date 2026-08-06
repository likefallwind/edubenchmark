#!/usr/bin/env python3
"""Random / trivial-strategy baselines for every benchmark in the eval harness.

Why this exists: `reports/eval/` holds dozens of scores with no floor to read
them against.  A 25% on a four-option MCQ is nothing; a 5.0 on `p07_selfcheck`
is what a model that never changes its answer gets for free.  Until now only
`mooccube_prereq` recorded a chance level (`MCQ_CHANCE`); everything else was
read raw.

Three layers of floor, because uniform random is *not* the binding floor for
about half of these benchmarks:

  L1 uniform_random   - uniform over the item's own answer space
  L2 trivial strategy - the best answer-independent constant strategy
                        (prior_random / majority_constant / always_abstain /
                        never_change ...).  For skewed label sets this sits far
                        above L1.
  L3 degenerate reply - a junk generation scored by the real judge.  Not here;
                        it needs API calls, see scripts/run_degenerate_baseline.py.

Method: rather than re-deriving each benchmark's metric by hand, we drive the
*real* `adapter.score()` and `adapter.extra_summary()` with synthetic answers.
That way RFS partial credit, macro-F1, QWK and friends all come out of the same
code path the real runs use.  Closed forms are kept only as cross-checks
(`--validate-only`).

Outputs `data/benchmark_baselines_v1.json`.  Idempotent; safe to rerun.
"""

from __future__ import annotations

import argparse
import json
import random
import statistics
import string
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from eval.benchmarks import available_benchmarks, get_adapter  # noqa: E402

OUT_PATH = ROOT / "data" / "benchmark_baselines_v1.json"
SEED = 20260804

LETTERS = "ABCDEFGHIJ"

# A response that is fluent, well-formed and completely content-free.  Used as
# the "generic" floor for rule checkers that reward form over substance.
GENERIC_TEXT = (
    "That is a great question, and it is worth working through carefully. "
    "Let us take it one step at a time. First, think about what the problem is "
    "really asking you to find. Then consider which facts you already have and "
    "which you still need. Try writing down your reasoning as you go, so you can "
    "check each step. What do you think the first step should be?"
)


# --------------------------------------------------------------------------
# generic answer-space helpers
# --------------------------------------------------------------------------


def _nonempty_subsets(letters: str) -> list[frozenset[str]]:
    out: list[frozenset[str]] = []
    for mask in range(1, 1 << len(letters)):
        out.append(frozenset(letters[i] for i in range(len(letters)) if mask & (1 << i)))
    return out


def _sample_from(counter: Counter, rng: random.Random) -> Any:
    """Draw from an empirical distribution (the 'guess from the prior' policy)."""
    population = list(counter)
    weights = [counter[k] for k in population]
    return rng.choices(population, weights=weights, k=1)[0]


def _modal(counter: Counter) -> Any:
    return counter.most_common(1)[0][0]


# --------------------------------------------------------------------------
# baseline specification
# --------------------------------------------------------------------------

# Policy signature: fn(item, rng, ctx) -> extracted string, exactly as the
# runner would hand it to adapter.score().
Policy = Callable[[dict, random.Random, dict], str]


class Spec:
    def __init__(
        self,
        *,
        headline: str,
        policies: dict[str, Policy],
        deterministic: tuple[str, ...] = (),
        context: Callable[[list[dict]], dict] | None = None,
        sample: int | None = None,
        trials: int | None = None,
        note: str = "",
        analytic: Callable[[list[dict]], dict] | None = None,
        item_list: Path | None = None,
    ) -> None:
        self.headline = headline
        self.policies = policies
        self.deterministic = deterministic
        self.context = context
        self.sample = sample
        self.trials = trials
        self.note = note
        self.analytic = analytic
        # Benchmarks the real runs pin to a fixed item list must be simulated on
        # that same list, or the floor answers a different question than the
        # scores it is meant to anchor.
        self.item_list = item_list


# Benchmarks whose score() consumes a judge verdict rather than a parseable
# answer: uniform random is undefined and the only meaningful floor is a
# degenerate generation scored by the real judge (layer L3).
#   name: (headline, scale_floor, reason)
#
# ``scale_floor`` is the score an arbitrarily bad reply cannot go below — the
# bottom of the rating scale itself. It is NOT always 0: EduBench's judge rates
# 1-10, so pure gibberish still scores 1.0, and any "how far above chance is
# this model" arithmetic that assumes 0 overstates the gap by a whole point.
# ``None`` means the floor depends on the judge's behaviour rather than the
# scale, and only the measured L3 `random` variant can supply it.
JUDGE_ONLY = {
    "edubench": (
        "extra:overall.mean_overall_score",
        1.0,
        "12 维 1-10 量表由固定 judge 打分。乱码的期望是刻度下限 1.0，不是 0",
    ),
    "mmtutorbench": ("extra:average_total_score_0_to_6", 0.0, "6 个二元 rubric 由固定 judge 打分，全 0 即 0/6"),
    "tutorbench": (
        "extra:arr_w_x100",
        None,
        "加权 rubric（critical +5 / not_critical +1 / critical_negative −5），"
        "ARR_w 理论上可为负，所以刻度下限无法先验给出，只能实测。"
        "实测乱码落在 +2.54：judge 并没有触发那些 −5 的 critical_negative 项，"
        "乱码只是拿不到分而不是被扣分",
    ),
    "k12vista": ("extra:official_score", 0.0, "逐空 0/1 由 judge 判定；其中的选择题子集会给随机作答少量命中"),
    "mrbench_tutor": ("extra:pass_rate", 0.0, "生成 + 固定 judge 打 8 维标签，pass 要求三个关键维度全 Yes"),
    "bea2025_tutor": ("extra:pass_rate", 0.0, "生成 + 固定 judge 打 4 维标签，同上"),
    # headline 原本是 accuracy，但那是 judge 输出的解析成功率而非能力分：score() 里
    # 四维都被 clamp 进 [1,5]，只有 judge 的 JSON 解析不出来才记 0，所以乱码同样得 1.0。
    # 改用四维均值，与聚合管线实际取用的 judge_scores 同源。adapter 的 correct 保持
    # 原样——audit_eval_artifacts.py 拿它当 judge 解析故障的探针，那个用法是成立的。
    "longtutor_teaching": (
        "extra:judge_scores.average",
        1.0,
        "judge 打 4 维 1-5 分，刻度下限 1（归一时按 (raw−1)/4 扣掉）。"
        "⚠ 不要用它的 accuracy：那只是「四个分数都成功解析且非 0」，实跑 0.999-1.000，"
        "1001 题里唯一那次失败是 judge 把 appropriateness 拼成了 appropriance",
    ),
    "longtutor_evidence": ("accuracy", 0.0, "judge 判语义等价 CORRECT/INCORRECT，乱码必判 INCORRECT"),
    "eduguard_adversarial": (
        "extra:overall.asr",
        None,
        "⚠ 越狱攻击成功与否由内容决定，无 chance level；地板在另一头——全部拒答 = ASR 0 = 满分。"
        "乱码既非越狱成功也非合格拒答，落点只能实测",
    ),
    "mmtutorbench_judge_calibration": (None, None, "无公开人类金标，adapter 本身不产出题目"),
    # Not a BenchmarkAdapter: it has its own pipeline in
    # scripts/eval/build_eduillustrate_report.py, so get_adapter() cannot reach it.
    "eduillustrate": (
        "extra:overall_mean_all_items",
        0.0,
        "8 维 0-5 Likert 由 judge 打分；独立管线（scripts/eval/build_eduillustrate_report.py），不在 adapter 注册表里",
    ),
}


# --------------------------------------------------------------------------
# per-benchmark policies
# --------------------------------------------------------------------------


def _gold_counter(items: list[dict], key: Callable[[dict], Any] = lambda it: it["gold"]) -> dict:
    return {"gold_counts": Counter(key(it) for it in items)}


# ---- plain single-choice MCQ ---------------------------------------------


def _mcq_k(item: dict) -> int:
    opts = item["meta"].get("options") or []
    if isinstance(opts, dict):
        opts = [v for v in opts.values() if v not in (None, "")]
    else:
        opts = [o for o in opts if o not in (None, "", "N/A")]
    return len(opts) or 4


def p_mcq_uniform(item: dict, rng: random.Random, ctx: dict) -> str:
    return LETTERS[rng.randrange(_mcq_k(item))]


def p_gold_prior(item: dict, rng: random.Random, ctx: dict) -> str:
    return str(_sample_from(ctx["gold_counts"], rng))


def p_gold_majority(item: dict, rng: random.Random, ctx: dict) -> str:
    return str(_modal(ctx["gold_counts"]))


def _fixed_letters(letters: str) -> Policy:
    def _p(item: dict, rng: random.Random, ctx: dict) -> str:
        return letters[rng.randrange(len(letters))]

    return _p


# ---- agieval (mixed) ------------------------------------------------------


def p_agieval_uniform(item: dict, rng: random.Random, ctx: dict) -> str:
    meta = item["meta"]
    if meta["question_type"] == "cloze":
        return ""
    k = len(meta.get("options") or []) or 4
    if meta.get("is_multi"):
        # uniform over the non-empty subsets of the available letters
        pool = LETTERS[:k]
        size = rng.randrange(1, len(pool) + 1)
        return "".join(sorted(rng.sample(pool, size)))
    return LETTERS[rng.randrange(k)]


def p_agieval_single_letter(item: dict, rng: random.Random, ctx: dict) -> str:
    """Same as uniform but always emits exactly one letter, including on the
    three nominally-multi tasks whose local gold sets are all size 1."""
    meta = item["meta"]
    if meta["question_type"] == "cloze":
        return ""
    return LETTERS[rng.randrange(len(meta.get("options") or []) or 4)]


# ---- mathvista ------------------------------------------------------------


def _mv_ctx(items: list[dict]) -> dict:
    free = Counter(
        str(it["gold"]) for it in items if it["meta"].get("question_type") != "multi_choice"
    )
    return {"free_gold": free}


def p_mathvista_uniform(item: dict, rng: random.Random, ctx: dict) -> str:
    meta = item["meta"]
    if meta.get("question_type") == "multi_choice":
        choices = meta.get("choices") or []
        return str(choices[rng.randrange(len(choices))]) if choices else ""
    return ""  # free-form: a uniform draw over the reals never hits


def p_mathvista_prior(item: dict, rng: random.Random, ctx: dict) -> str:
    meta = item["meta"]
    if meta.get("question_type") == "multi_choice":
        return p_mathvista_uniform(item, rng, ctx)
    return str(_sample_from(ctx["free_gold"], rng))


# ---- set-valued (eduguard_sata, k12bench) ---------------------------------

_SATA_SUBSETS = _nonempty_subsets("ABCDE")
_K12_SUBSETS = _nonempty_subsets("ABCD")


def _set_ctx(parse: Callable[[dict], frozenset]) -> Callable[[list[dict]], dict]:
    def _ctx(items: list[dict]) -> dict:
        return {"gold_sets": Counter(parse(it) for it in items)}

    return _ctx


def _sata_gold(item: dict) -> frozenset:
    return frozenset(a.strip().upper() for a in str(item["gold"]).split(",") if a.strip())


def _k12_gold(item: dict) -> frozenset:
    return frozenset(item["gold"])


def _p_subset_uniform(subsets: list[frozenset]) -> Policy:
    def _p(item: dict, rng: random.Random, ctx: dict) -> str:
        return ",".join(sorted(subsets[rng.randrange(len(subsets))]))

    return _p


def _p_subset_single(letters: str) -> Policy:
    def _p(item: dict, rng: random.Random, ctx: dict) -> str:
        return letters[rng.randrange(len(letters))]

    return _p


def p_set_prior(item: dict, rng: random.Random, ctx: dict) -> str:
    return ",".join(sorted(_sample_from(ctx["gold_sets"], rng)))


def p_set_majority(item: dict, rng: random.Random, ctx: dict) -> str:
    return ",".join(sorted(_modal(ctx["gold_sets"])))


# ---- per-dimension label sets (mrbench_judge / bea2025_judge) -------------


def _dim_ctx(items: list[dict]) -> dict:
    per_dim: dict[str, Counter] = {}
    for it in items:
        dim = it["meta"]["dimension"]
        per_dim.setdefault(dim, Counter())[it["gold"]] += 1
    return {"per_dim": per_dim}


def _dim_labels(item: dict, ctx: dict) -> list:
    return sorted(ctx["per_dim"][item["meta"]["dimension"]])


def p_dim_uniform(item: dict, rng: random.Random, ctx: dict) -> str:
    labels = _dim_labels(item, ctx)
    return str(labels[rng.randrange(len(labels))])


def p_dim_prior(item: dict, rng: random.Random, ctx: dict) -> str:
    return str(_sample_from(ctx["per_dim"][item["meta"]["dimension"]], rng))


def p_dim_majority(item: dict, rng: random.Random, ctx: dict) -> str:
    return str(_modal(ctx["per_dim"][item["meta"]["dimension"]]))


# ---- mathtutorbench --------------------------------------------------------


def p_yesno_uniform(item: dict, rng: random.Random, ctx: dict) -> str:
    return rng.choice(["Yes", "No"])


def p_const(value: str) -> Policy:
    def _p(item: dict, rng: random.Random, ctx: dict) -> str:
        return value

    return _p


def p_int_prior(item: dict, rng: random.Random, ctx: dict) -> str:
    return str(_sample_from(ctx["gold_counts"], rng))


def p_ab_uniform(item: dict, rng: random.Random, ctx: dict) -> str:
    return rng.choice(["A", "B"])


# ---- asap_2 ---------------------------------------------------------------


def _asap_ctx(items: list[dict]) -> dict:
    return {"gold_counts": Counter(int(it["gold"]) for it in items if it["gold"] is not None)}


def p_asap_uniform(item: dict, rng: random.Random, ctx: dict) -> str:
    lo, hi = int(item["meta"]["min_score"]), int(item["meta"]["max_score"])
    return str(rng.randint(lo, hi))


# ---- p08_abstention --------------------------------------------------------


def p_abstain_all(item: dict, rng: random.Random, ctx: dict) -> str:
    return "unanswerable"


def p_answer_all(item: dict, rng: random.Random, ctx: dict) -> str:
    return str(_sample_from(ctx["gold_counts"], rng))


def p_abstain_coin(item: dict, rng: random.Random, ctx: dict) -> str:
    return "unanswerable" if rng.random() < 0.5 else str(_sample_from(ctx["gold_counts"], rng))


def _umwp_ctx(items: list[dict]) -> dict:
    nums = Counter(
        str(it["gold"]) for it in items if it["meta"].get("answerable") and it["gold"] is not None
    )
    return {"gold_counts": nums or Counter({"42": 1})}


# ---- mooccube --------------------------------------------------------------


def p_mooccube_random(item: dict, rng: random.Random, ctx: dict) -> str:
    row = item["meta"]
    if row["task"] == "mcq":
        return "ABCD"[rng.randrange(4)]
    names = [c["name"] for c in row["concepts"]]
    order = names[:]
    rng.shuffle(order)
    return " -> ".join(order)


# ---- ifeval / olympiadbench ------------------------------------------------


def p_text_generic(item: dict, rng: random.Random, ctx: dict) -> str:
    return GENERIC_TEXT


def p_text_empty(item: dict, rng: random.Random, ctx: dict) -> str:
    return ""


def p_text_random(item: dict, rng: random.Random, ctx: dict) -> str:
    """Uniform random tokens — the L1 sample for a free-text answer space.

    Same recipe as ``run_reference_baseline._random_text`` so the simulated and
    the judge-scored halves of L1 mean the same thing.
    """
    alphabet = string.ascii_lowercase + "  "
    words = [
        "".join(rng.choice(alphabet) for _ in range(rng.randint(2, 9))).strip()
        for _ in range(rng.randint(30, 70))
    ]
    return " ".join(w for w in words if w)


def p_boxed_prior(item: dict, rng: random.Random, ctx: dict) -> str:
    return "\\boxed{" + str(rng.randint(0, 100)) + "}"


# ---- p07 / p08_calibration (delegate composites) ---------------------------

# Both adapters wrap the same four exact-match delegates and their ``score()``
# consumes a JSON envelope, so L1 is simulable: sample each delegate's own
# answer space uniformly and pack the envelope the runner would have built.


def _delegate_uniform(orig: dict, src: str, rng: random.Random) -> str:
    if src == "ceval":
        return "ABCD"[rng.randrange(4)]
    if src == "mmlu_pro":
        return LETTERS[rng.randrange(_mcq_k(orig))]
    if src == "agieval":
        return p_agieval_uniform(orig, rng, {})
    # mtb_problem_solving: open numeric answer, uniform over the reals never
    # lands on gold — a random integer is the closest realizable draw.
    return str(rng.randint(0, 999))


def p_p08_calib_uniform(item: dict, rng: random.Random, ctx: dict) -> str:
    meta = item["meta"]
    answer = _delegate_uniform(meta["delegate_item"], meta["source_benchmark"], rng)
    return json.dumps({"a": answer, "c": rng.randint(0, 100)}, ensure_ascii=False)


def p_p07_uniform(item: dict, rng: random.Random, ctx: dict) -> str:
    meta = item["meta"]
    src, orig = meta["source_benchmark"], meta["delegate_item"]
    return json.dumps(
        {"r1": _delegate_uniform(orig, src, rng), "r2": _delegate_uniform(orig, src, rng)},
        ensure_ascii=False,
    )


# --------------------------------------------------------------------------
# the registry
# --------------------------------------------------------------------------

SPECS: dict[str, Spec] = {
    "mmlu_pro": Spec(
        headline="accuracy",
        context=_gold_counter,
        policies={
            "uniform_random": p_mcq_uniform,
            "prior_random": p_gold_prior,
            "majority_constant": p_gold_majority,
        },
        deterministic=("majority_constant",),
        note="选项数不固定（3-10），逐题 1/k 才是正确的 chance；固定按 1/10 算会低估。",
    ),
    "ceval": Spec(
        headline="accuracy",
        context=_gold_counter,
        policies={
            "uniform_random": _fixed_letters("ABCD"),
            "prior_random": p_gold_prior,
            "majority_constant": p_gold_majority,
        },
        deterministic=("majority_constant",),
        note="固定 4 选 1。抽取兜底取最后一个 A-D 字母，空答率极低，实测随机会贴近理论值。",
    ),
    "agieval": Spec(
        headline="accuracy",
        policies={
            "uniform_random": p_agieval_uniform,
            "single_letter_random": p_agieval_single_letter,
        },
        note=(
            "混合题型：5选1 / 4选1 / 名义多选 / 数学填空。"
            "本地 jec-qa 与 gaokao-physics 的 gold 集合实际全是 size=1，"
            "但抽取端仍是集合语义，多吐一个字母即判错——两种策略都报。"
        ),
    ),
    "mathvista": Spec(
        headline="accuracy",
        context=_mv_ctx,
        policies={
            "uniform_random": p_mathvista_uniform,
            "prior_random": p_mathvista_prior,
        },
        note=(
            "MC 540 题（选项 2-8 个）+ free-form 460 题。"
            "uniform_random 对 free-form 记 0，应复现官方论文公布的 Random chance 17.9%。"
        ),
    ),
    "pedagogy_benchmark": Spec(
        headline="accuracy",
        context=_gold_counter,
        policies={
            "uniform_random": p_mcq_uniform,
            "prior_random": p_gold_prior,
            "majority_constant": p_gold_majority,
        },
        deterministic=("majority_constant",),
        note=(
            "全部 4 选 1。注意官方 REPAT 解析很严，随机*文本*会掉进 bad_format 记 0，"
            "所以真实的乱答得分低于这里的 0.25——这里模拟的是「随机但格式正确」。"
        ),
    ),
    "eduguard_sata": Spec(
        headline="extra:overall.rfs",
        context=_set_ctx(_sata_gold),
        policies={
            "uniform_random": _p_subset_uniform(_SATA_SUBSETS),
            "single_letter_random": _p_subset_single("ABCDE"),
            "prior_random": p_set_prior,
            "majority_constant": p_set_majority,
        },
        deterministic=("majority_constant",),
        note="RFS 有 0/0.5/1 三档：全对 1，非空真子集 0.5，含错选 0。",
        analytic=lambda items: _sata_closed_form(items),
    ),
    "k12bench": Spec(
        headline="accuracy",
        context=_set_ctx(_k12_gold),
        policies={
            "uniform_random": _p_subset_uniform(_K12_SUBSETS),
            "single_letter_random": _p_subset_single("ABCD"),
            "prior_random": p_set_prior,
            "majority_constant": p_set_majority,
        },
        deterministic=("majority_constant",),
        note="4 选 N，headline accuracy 是 exact match；extra.overall.macro_f1 是部分分口径。",
    ),
    "mrbench_judge": Spec(
        headline="extra:macro_over_dimensions.f1_macro",
        context=_dim_ctx,
        policies={
            "uniform_random": p_dim_uniform,
            "prior_random": p_dim_prior,
            "majority_constant": p_dim_majority,
        },
        deterministic=("majority_constant",),
        note=(
            "8 维 × 1,655 条。gold 极不平衡（humanlikeness Yes 占 .88）。"
            "majority_constant 的 accuracy 会远高于 uniform，但 macro-F1 依然很低——"
            "这正是仓库把 headline 定为 macro-F1 的理由。"
        ),
    ),
    "bea2025_judge": Spec(
        headline="extra:recommended_judge_score",
        context=_dim_ctx,
        policies={
            "uniform_random": p_dim_uniform,
            "prior_random": p_dim_prior,
            "majority_constant": p_dim_majority,
        },
        deterministic=("majority_constant",),
        note="4 维 × 2,476 条，标签固定 Yes / To some extent / No。",
    ),
    "longtutor_diagnosis": Spec(
        headline="extra:f1_macro",
        context=_gold_counter,
        policies={
            "uniform_random": lambda it, rng, ctx: str(
                sorted(ctx["gold_counts"])[rng.randrange(len(ctx["gold_counts"]))]
            ),
            "prior_random": p_gold_prior,
            "majority_constant": p_gold_majority,
        },
        deterministic=("majority_constant",),
        note="4 类单选，headline 用 macro-F1（类别不平衡）。",
    ),
    "mathtutorbench_solution_correctness": Spec(
        headline="extra:f1",
        context=_gold_counter,
        policies={
            "uniform_random": p_yesno_uniform,
            "always_yes": p_const("Yes"),
            "always_no": p_const("No"),
        },
        deterministic=("always_yes", "always_no"),
        note="twins 设计使 gold 严格 50/50；官方解析器解析失败默认返回 Yes，故「全 Yes」是真实退化路径。",
    ),
    "mathtutorbench_mistake_location": Spec(
        headline="extra:f1_micro",
        context=_gold_counter,
        policies={
            "uniform_random": lambda it, rng, ctx: str(
                sorted(ctx["gold_counts"])[rng.randrange(len(ctx["gold_counts"]))]
            ),
            "prior_random": p_int_prior,
            "always_zero": p_const("0"),
        },
        deterministic=("always_zero",),
        note="twins 设计使 50% 的 gold=0；官方解析器找不到数字时默认 0，「全 0」是真实退化路径。",
    ),
    "mathtutorbench_judge_calibration": Spec(
        headline="accuracy",
        policies={
            "uniform_random": p_ab_uniform,
            "always_a": p_const("A"),
            "always_b": p_const("B"),
        },
        deterministic=("always_a", "always_b"),
        note="双顺序（#ab/#ba）设计：随机与固定位置偏好都恰好 0.50，要看 position_consistency 才能区分。",
    ),
    "mathtutorbench_problem_solving": Spec(
        headline="accuracy",
        context=_gold_counter,
        policies={"prior_random": p_int_prior},
        note="开放数值答案，随机 ≈ 0；prior_random 是「按答案先验瞎猜」的上界。",
    ),
    "mathtutorbench_mistake_correction": Spec(
        headline="accuracy",
        context=_gold_counter,
        policies={"prior_random": p_int_prior},
        note="开放数值答案，随机 ≈ 0；prior_random 是「按答案先验瞎猜」的上界。",
    ),
    "mooccube_prereq": Spec(
        headline="extra:score_10",
        policies={"uniform_random": p_mooccube_random},
        note="唯一已内建 chance correction 的 benchmark；随机作答的 score_10 应当回到 0。",
    ),
    "asap_2": Spec(
        headline="extra:overall.qwk",
        context=_asap_ctx,
        policies={
            "uniform_random": p_asap_uniform,
            "prior_random": p_gold_prior,
            "majority_constant": p_gold_majority,
        },
        deterministic=("majority_constant",),
        note=(
            "QWK 本身就是 chance-corrected：随机评分与常数评分的 QWK 都应为 0。"
            "但诊断量 exact/adjacent agreement 的「白痴基线」很高，报告里必须一起标出。"
        ),
    ),
    "ifeval": Spec(
        headline="extra:prompt_strict_accuracy",
        policies={
            "random_text": p_text_random,
            "generic_text": p_text_generic,
            "empty": p_text_empty,
        },
        deterministic=("generic_text", "empty"),
        trials=10,
        note=(
            "答案空间是自由文本，其均匀抽样就是随机 token，所以 L1 是能测的。"
            "⚠ 实测 random_text(0.118) 反而高于 generic_text(0.056)——纯形式约束"
            "（全小写、不许出现逗号、字数下限）乱码全中，而一段像样的中文/英文散文会违反，"
            "所以这里最强的「与题无关策略」就是乱码本身，L1 高于 L2。"
        ),
    ),
    "p08_abstention": Spec(
        headline="extra:score_10",
        context=_umwp_ctx,
        policies={
            "always_abstain": p_abstain_all,
            "always_answer": p_answer_all,
            "coin_flip": p_abstain_coin,
        },
        deterministic=("always_abstain",),
        note=(
            "⚠ headline score_10 = 10×(弃答recall + 可答作答率)/2 —— "
            "全弃答、全作答、抛硬币三种策略的期望值都恰好 5.0。"
            "这个指标对任何与题目无关的策略恒等于 5，必须单列说明。"
        ),
    ),
    "olympiadbench": Spec(
        headline="accuracy",
        policies={"random_number": p_boxed_prior},
        sample=300,
        trials=1,
        note="开放数值/符号答案，随机 ≈ 0。sympy 判定很慢，只在 300 题样本上做经验确认。",
    ),
    # p07 / p08_calibration are composites over the same four exact-match
    # delegates. Their *trivial-strategy* floors are closed forms (below, in
    # ANALYTIC_ONLY), but L1 is not: sampling both rounds / the confidence
    # uniformly is a real draw the delegates can score, and the answer it gives
    # — 10x the delegate mix's chance level — is not the 0 you would guess.
    "p07_selfcheck": Spec(
        headline="extra:score_10",
        policies={"uniform_random": p_p07_uniform},
        item_list=ROOT / "data" / "p08_calibration" / "item_list_v1.txt",
        note=(
            "两轮都均匀乱答：fix_rate 与 break_rate 同时趋近 chance 与 1−chance，"
            "score_10 收敛到 10×chance，远低于 never_change 的 5.0。"
        ),
    ),
    "p08_calibration": Spec(
        headline="extra:score_10",
        policies={"uniform_random": p_p08_calib_uniform},
        item_list=ROOT / "data" / "p08_calibration" / "item_list_v1.txt",
        note=(
            "答案与置信度都均匀随机：AUROC 回到 0.5，固定贡献 2.5 分；"
            "CWR@90 不是 1——均匀置信度把约一成题推过 90 分线，其中仍有 chance 比例答对，"
            "CWR 落在 0.84 左右，另一半再给约 0.8 分。合计 3.3，"
            "既不是 0 也不到 never_high_confidence 的 5.0。"
        ),
    ),
}


# Benchmarks whose floor is a formula, not a simulation.
ANALYTIC_ONLY: dict[str, dict[str, Any]] = {
    "p07_selfcheck": {
        "headline": "extra:score_10",
        "floors": {
            "never_change": {
                "value": 5.0,
                "derivation": (
                    "score_10 = 10×[0.5×fix_rate + 0.5×(1−break_rate)]；"
                    "一个从不修改答案的模型 fix_rate=0、break_rate=0 → 10×0.5 = 5.0"
                ),
            },
        },
        # 实跑区间由 build_baseline_report.py 从 reports/eval 现算，不在这里写死。
        # L1（两轮都乱答）以前挂在这里且值为 None，现在改由 SPECS 实测，见上。
        "note": "⚠ 地板是 5.0/10 而不是 0，且与第一轮正确率解耦。实测所有模型都紧贴这条线。",
    },
    "p08_calibration": {
        "headline": "extra:score_10",
        "floors": {
            "never_high_confidence": {
                "value": 5.0,
                "derivation": (
                    "score_10 = 10×[0.5×(1−CWR@90) + 0.5×AUROC]；"
                    "从不给出 ≥90 的置信度时 CWR 未定义而退化为 10×AUROC，"
                    "随机置信度 AUROC=0.5 → 5.0"
                ),
            }
        },
        "note": "⚠ 地板 5.0/10，与答题正确率解耦。",
    },
    "sas_bench": {
        "headline": "extra:overall.qwk",
        # Split L1 from L2 even though both are 0: they are different claims
        # (uniform draw vs. best constant strategy) that happen to coincide,
        # and collapsing them hides that the coincidence is what QWK guarantees.
        "floors": {
            "random_rating": {
                "value": 0.0,
                "derivation": "QWK/CCS/ECS 都是 chance-corrected 一致性统计量，随机评分的期望是 0",
            },
            "constant_rating": {
                "value": 0.0,
                "derivation": "同理，恒定给同一个分数的评分者与人类的一致性也是 0",
            },
        },
        "note": "0-100 标度，故随机基线为 0（分）。structured exact match 的 accuracy 随机 ≈ 0。",
    },
    # Pairwise comparison against a gold teacher reply, judged in both orders.
    # Uniform random IS well defined here — a judge choosing at random picks the
    # generated reply half the time — so these belong with the closed forms, not
    # with the "no chance level" group.
    **{
        task: {
            "headline": "extra:win_rate",
            "floors": {
                "random_judge": {
                    "value": 0.5,
                    "derivation": (
                        "与金标教师回应成对比较，位置交换两轮取平均。"
                        "随机选择时 win_score 期望 = 0.5（(0,1) 与 (1,0) 各 1/4，平局 0.5 占 1/2）"
                    ),
                },
                "random_judge_strict": {
                    "value": 0.25,
                    # Scores a different statistic than the headline, so it must
                    # never be picked as this benchmark's floor.
                    "metric": "extra:strict_win_rate",
                    "derivation": "strict_win_rate = share(win_score > 0.5) = 1/4",
                },
            },
            "note": (
                "⚠ win_rate 0.5 的含义是「与专家教师打平」，既是随机地板也是人类锚。"
                "低于 0.5 才说明比金标教师差。"
            ),
        }
        for task in (
            "mathtutorbench_pedagogy",
            "mathtutorbench_pedagogy_hard",
            "mathtutorbench_scaffolding",
            "mathtutorbench_scaffolding_hard",
        )
    },
    "mathtutorbench_socratic": {
        "headline": "extra:avg_bleu",
        "floors": {
            "random_text": {
                "value": 0.0,
                "derivation": "与参考问句的 sentence-BLEU，随机文本期望 ≈ 0",
            }
        },
        "note": "correct = bleu ≥ 0.5 只是粗代理，headline 看 avg_bleu；人类改述同样拿不到高 BLEU，该指标没有有意义的上限。",
    },
}


# --------------------------------------------------------------------------
# which number is L1
# --------------------------------------------------------------------------

# Headlines where a *lower* score is the good direction. An L1 of 0 on one of
# these is the ceiling, not the floor, and must never be read as "random does
# badly here".
LOWER_IS_BETTER = {"extra:overall.asr"}

# L1 is "uniform over the item's own answer space". Which concrete number that
# is varies by how the answer space is shaped, and reading it off the policy
# named `uniform_random` was wrong for a third of the set: p08_abstention's
# uniform draw is `coin_flip`, the pairwise-comparison tasks derive theirs, and
# a generation task's uniform draw is gibberish — i.e. the L3 `random` variant.
# This table says, per benchmark, where the L1 number comes from. Absent entries
# default to the simulated policy `uniform_random`.
#
#   {"policy": name}                 -> simulated, read that policy's headline
#   {"value": x, "derivation": ...}  -> closed form, uniform sampling has a
#                                       provable expectation and simulating it
#                                       would only add noise
#   {"source": "L3:random"}          -> measured by run_reference_baseline.py;
#                                       resolved at report time from
#                                       reports/eval/_baseline/<b>/random/
#   {"defined": False, ...}          -> genuinely undefined, not skipped
_OPEN_SPACE = (
    "答案是任意实数或 LaTeX 表达式，在其上均匀抽样命中 gold 的概率测度为 0。"
    "prior_random（按数据集答案分布猜）是更强的替代策略，不是 L1。"
)

L1_SOURCE: dict[str, dict[str, Any]] = {
    "p08_abstention": {"policy": "coin_flip"},
    "ifeval": {"policy": "random_text"},
    "olympiadbench": {"value": 0.0, "derivation": _OPEN_SPACE},
    "mathtutorbench_problem_solving": {"value": 0.0, "derivation": _OPEN_SPACE},
    "mathtutorbench_mistake_correction": {"value": 0.0, "derivation": _OPEN_SPACE},
    "sas_bench": {
        "value": 0.0,
        "floor_key": "random_rating",
        "derivation": "QWK/CCS/ECS 都是 chance-corrected 一致性统计量，随机评分的期望恒为 0",
    },
    "mathtutorbench_socratic": {
        "value": 0.0,
        "floor_key": "random_text",
        "derivation": "与参考问句的 sentence-BLEU，随机文本的期望 ≈ 0",
    },
    **{
        task: {
            "value": 0.5,
            "floor_key": "random_judge",
            "derivation": (
                "答案空间是「二选一」而不是自由文本：随机 judge 有一半概率选中被测回复，"
                "位置交换两轮取平均后 win_score 期望 = 0.5"
            ),
        }
        for task in (
            "mathtutorbench_pedagogy",
            "mathtutorbench_pedagogy_hard",
            "mathtutorbench_scaffolding",
            "mathtutorbench_scaffolding_hard",
        )
    },
    **{
        name: {
            "source": "L3:random",
            "derivation": (
                "生成任务的答案空间是 token 序列，其均匀抽样就是乱码；"
                "该乱码交给真实 judge 打出的分即本 benchmark 的 L1，由 L3 的 random 变体实测"
            ),
        }
        for name in JUDGE_ONLY
        if name != "mmtutorbench_judge_calibration"
    },
    "mmtutorbench_judge_calibration": {
        "defined": False,
        "derivation": "无公开人类金标，adapter 本身不产出题目，没有可抽样的答案空间",
    },
    # Two of the judge-scored set do not need the API run: their floor follows
    # from what the judge is asked to emit.
    "eduillustrate": {
        "value": 0.0,
        "derivation": (
            "被测模型交付的是 Manim 代码，乱码不可能编译通过，8 个 0-5 Likert 维度全部记 0。"
            "刻度下限与随机期望在这里重合，不必实测"
        ),
    },
    "longtutor_teaching": {
        "value": 1.0,
        "derivation": (
            "四维 1-5 量表的刻度下限。judge prompt 明确写 “Score from 1 to 5”，"
            "score() 又把每维 clamp 进 [1,5]，所以乱码最低也只能落在 1.0（归一后为 0）。"
            "实跑约 3.9。"
            "⚠ 旧 headline 是 accuracy，那是 all(scores.values())——只有 judge 的 JSON "
            "解析失败才记 0，乱码同样拿 1.0 满分；1001 题里唯一那次失败是 judge 把 "
            "appropriateness 拼成了 appropriance。聚合管线取的一直是 judge_scores，未受影响"
        ),
    },
}


def _l1_block(name: str, headline: str | None, policies: dict[str, Any] | None = None) -> dict[str, Any]:
    """The `l1` field written next to every benchmark, whatever section it is in."""
    spec = L1_SOURCE.get(name, {"policy": "uniform_random"})
    block: dict[str, Any] = {"defined": spec.get("defined", True)}
    if "policy" in spec:
        entry = (policies or {}).get(spec["policy"]) or {}
        block["source"] = f"simulated:{spec['policy']}"
        block["value"] = entry.get("headline_mean")
        if not entry:
            block["defined"] = False
            block["derivation"] = f"策略 {spec['policy']} 未产出（benchmark 被跳过）"
    elif "source" in spec:
        block["source"] = spec["source"]
        block["value"] = None  # resolved from reports/eval/_baseline at report time
    else:
        block["source"] = "analytic"
        block["value"] = spec.get("value")
        # Names the `floors` entry this L1 came from, so the report can leave it
        # out of the L2 candidates instead of printing one number in both columns.
        if spec.get("floor_key"):
            block["floor_key"] = spec["floor_key"]
    if spec.get("derivation"):
        block["derivation"] = spec["derivation"]
    if headline in LOWER_IS_BETTER:
        block["direction"] = "lower_is_better"
        block["direction_note"] = "headline 越低越好，这个 L1 落在满分那一头，不是地板"
    # A headline can land at the ceiling for a reason other than its direction —
    # longtutor_teaching's accuracy is a parse-success rate, so gibberish scores
    # 1.0 too. Same warning marker, different cause.
    if spec.get("caveat"):
        block["caveat"] = spec["caveat"]
    return block


def _sata_closed_form(items: list[dict]) -> dict:
    """E[RFS] when guessing a uniformly random non-empty subset of {A..E}."""
    sizes = Counter(len(_sata_gold(it)) for it in items)
    n = sum(sizes.values())
    denom = 2**5 - 1
    exp = sum(cnt * ((1 + 0.5 * (2**g - 2)) / denom) for g, cnt in sizes.items()) / n
    return {
        "value": round(exp, 6),
        "derivation": (
            f"gold 集合大小分布 {dict(sorted(sizes.items()))}；"
            f"E[RFS|g] = (1 + 0.5×(2^g − 2)) / 31，按分布加权"
        ),
    }


# --------------------------------------------------------------------------
# simulation engine
# --------------------------------------------------------------------------


def _dig(obj: Any, path: str) -> Any:
    for part in path.split("."):
        if not isinstance(obj, dict) or part not in obj:
            return None
        obj = obj[part]
    return obj


def _headline_value(headline: str, accuracy: float | None, extra: dict) -> float | None:
    if headline == "accuracy":
        return accuracy
    value = _dig(extra, headline.split(":", 1)[1])
    return float(value) if isinstance(value, (int, float)) else None


def _score_once(adapter, items: list[dict], policy: Policy, rng: random.Random, ctx: dict):
    rows = []
    for item in items:
        extracted = policy(item, rng, ctx)
        result = adapter.score(extracted, item)
        correct = result["correct"]
        row = {
            "item_id": str(item["item_id"]),
            "buckets": adapter.buckets(item),
            "score_status": "scored",
            "correct": bool(correct) if correct is not None else None,
            "extracted": extracted,
            "normalized": result["normalized"],
            "gold": result["gold"],
            "response": extracted,
        }
        reserved = {"correct", "normalized", "gold"} | set(row)
        row.update({k: v for k, v in result.items() if k not in reserved})
        rows.append(row)
    bools = [r["correct"] for r in rows if isinstance(r["correct"], bool)]
    accuracy = (sum(bools) / len(bools)) if bools else None
    extra = adapter.extra_summary(rows) or {}
    return accuracy, extra


def _auto_trials(n_items: int) -> int:
    if n_items <= 0:
        return 1
    return max(5, min(60, 120_000 // max(n_items, 1)))


def run_benchmark(name: str, spec: Spec, verbose: bool = True) -> dict[str, Any]:
    adapter = get_adapter(name)
    items = adapter.load_items()
    if spec.item_list:
        wanted = {
            line.strip()
            for line in spec.item_list.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith("#")
        }
        items = [it for it in items if str(it["item_id"]) in wanted]
        if not items:
            raise SystemExit(f"item_list {spec.item_list} 与 {name} 的题目 id 无交集")
    n_full = len(items)
    if spec.sample and n_full > spec.sample:
        rng = random.Random(SEED)
        items = rng.sample(items, spec.sample)
    ctx = spec.context(items) if spec.context else {}
    trials = spec.trials or _auto_trials(len(items))

    out: dict[str, Any] = {
        "n_items": n_full,
        "n_simulated": len(items),
        "headline": spec.headline,
        "trials": trials,
        "note": spec.note,
        "policies": {},
    }
    if spec.sample and n_full > spec.sample:
        out["sampling_note"] = f"在 {spec.sample} 题随机样本上模拟（全集 {n_full}），seed={SEED}"

    for pname, policy in spec.policies.items():
        n_trials = 1 if pname in spec.deterministic else trials
        headline_vals: list[float] = []
        acc_vals: list[float] = []
        last_extra: dict = {}
        for t in range(n_trials):
            rng = random.Random(SEED + t)
            accuracy, extra = _score_once(adapter, items, policy, rng, ctx)
            last_extra = extra
            if accuracy is not None:
                acc_vals.append(accuracy)
            hv = _headline_value(spec.headline, accuracy, extra)
            if hv is not None:
                headline_vals.append(hv)
        entry: dict[str, Any] = {
            "trials": n_trials,
            "deterministic": pname in spec.deterministic,
        }
        if headline_vals:
            entry["headline_mean"] = round(statistics.fmean(headline_vals), 6)
            if len(headline_vals) > 1:
                entry["headline_stdev"] = round(statistics.stdev(headline_vals), 6)
                entry["headline_min"] = round(min(headline_vals), 6)
                entry["headline_max"] = round(max(headline_vals), 6)
        else:
            entry["headline_mean"] = None
        if acc_vals:
            entry["accuracy_mean"] = round(statistics.fmean(acc_vals), 6)
        entry["extra_metrics_last_trial"] = _trim(last_extra)
        out["policies"][pname] = entry
        if verbose:
            print(f"    {pname:24s} headline={entry['headline_mean']} acc={entry.get('accuracy_mean')}")

    if spec.analytic:
        out["closed_form"] = spec.analytic(items)
        cf = out["closed_form"].get("value")
        sim = (out["policies"].get("uniform_random") or {}).get("headline_mean")
        if cf is not None and sim is not None:
            out["closed_form"]["abs_diff_vs_simulation"] = round(abs(cf - sim), 6)
    return out


_TRIM_KEYS = {"by_task", "per_dimension", "abstention_recall_by_category", "by_bucket"}


def _trim(extra: dict) -> dict:
    """Keep summary-level numbers; drop the long per-bucket tables."""
    return {k: v for k, v in (extra or {}).items() if k not in _TRIM_KEYS}


# --------------------------------------------------------------------------
# regression assertions (the plan's verification table)
# --------------------------------------------------------------------------

ASSERTIONS: list[tuple[str, str, str, float, float]] = [
    # (benchmark, policy, field, expected, tolerance)
    ("mathvista", "uniform_random", "headline_mean", 0.1790, 0.006),
    ("mmlu_pro", "uniform_random", "headline_mean", 0.1109, 0.006),
    ("ceval", "uniform_random", "headline_mean", 0.2500, 0.015),
    ("pedagogy_benchmark", "uniform_random", "headline_mean", 0.2500, 0.020),
    ("eduguard_sata", "uniform_random", "headline_mean", 0.0997, 0.006),
    ("mathtutorbench_judge_calibration", "uniform_random", "headline_mean", 0.5000, 0.030),
    ("mathtutorbench_solution_correctness", "uniform_random", "accuracy_mean", 0.5000, 0.030),
    ("p08_abstention", "always_abstain", "headline_mean", 5.0, 0.001),
    ("p08_abstention", "always_answer", "headline_mean", 5.0, 0.60),
    ("mooccube_prereq", "uniform_random", "headline_mean", 0.0, 0.35),
    # p08_abstention's uniform draw is coin_flip, and this headline is constant
    # under any content-independent strategy — that is the whole warning.
    ("p08_abstention", "coin_flip", "headline_mean", 5.0, 0.10),
    # AUROC of a random confidence is 0.5, worth a flat 2.5 points. The other
    # half is 5x(1-CWR@90), and CWR is not 1: a uniform confidence puts ~10% of
    # items over the threshold and the delegate mix's chance level (~0.16) still
    # gets some of those right, so CWR lands near 0.84 and the term pays ~0.8.
    # Nowhere near 0, and nowhere near the 5.0 trivial-strategy floor either.
    ("p08_calibration", "uniform_random", "headline_mean", 3.32, 0.45),
    # 10 x the delegate mix's chance level, not 0.
    ("p07_selfcheck", "uniform_random", "headline_mean", 1.85, 0.60),
]


def check_assertions(results: dict[str, Any], scope: set[str] | None = None) -> list[str]:
    """Check the regression table. ``scope`` limits it to the benchmarks this
    invocation actually attempted, so a ``--benchmark`` subset run does not
    report the untouched ones as failures."""
    failures = []
    for bench, policy, field, expected, tol in ASSERTIONS:
        if scope is not None and bench not in scope:
            continue
        entry = ((results.get(bench) or {}).get("policies") or {}).get(policy)
        if entry is None:
            failures.append(f"{bench}/{policy}: 未产出（benchmark 被跳过或策略名不符）")
            continue
        got = entry.get(field)
        if got is None:
            failures.append(f"{bench}/{policy}.{field}: None")
        elif abs(got - expected) > tol:
            failures.append(f"{bench}/{policy}.{field}: 期望 {expected}±{tol}，实得 {got}")
    return failures


# --------------------------------------------------------------------------


def _pin_langdetect() -> None:
    """Make IFEval's language checks reproducible.

    The vendored official checker calls ``langdetect.detect`` unseeded, so the
    ifeval floor drifted by ~0.0006 between otherwise identical runs — enough to
    make this "idempotent" script rewrite its own output every time. Seeding the
    factory costs nothing and only affects this process.
    """
    try:
        import langdetect

        langdetect.DetectorFactory.seed = 0
    except ImportError:
        pass


def main() -> int:
    _pin_langdetect()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--benchmark", action="append", help="只跑指定 benchmark（可重复）")
    ap.add_argument("--validate-only", action="store_true", help="跑回归断言，不写文件")
    ap.add_argument(
        "--merge",
        action="store_true",
        help=(
            "把本次结果并入已有的 --out 文件，而不是整份重写。"
            "olympiadbench 必须在带 antlr4==4.11 的独立环境里跑，只能靠这个合并回来。"
        ),
    )
    ap.add_argument("--out", type=Path, default=OUT_PATH)
    args = ap.parse_args()

    wanted = set(args.benchmark or SPECS)
    results: dict[str, Any] = {}
    skipped: dict[str, str] = {}

    for name in SPECS:
        if name not in wanted:
            continue
        print(f"[{name}]")
        try:
            results[name] = run_benchmark(name, SPECS[name])
        except SystemExit as exc:
            skipped[name] = f"数据缺失或环境不满足：{exc}"
            print(f"    SKIP {exc}")
        except Exception as exc:  # noqa: BLE001 - report and continue
            skipped[name] = f"{type(exc).__name__}: {exc}"
            print(f"    SKIP {type(exc).__name__}: {exc}")

    if args.merge and args.out.exists():
        previous = json.loads(args.out.read_text(encoding="utf-8"))
        merged = dict(previous.get("simulated") or {})
        merged.update(results)
        results = merged
        skipped = {k: v for k, v in {**(previous.get("skipped") or {}), **skipped}.items() if k not in results}
        wanted = wanted | set(previous.get("simulated") or {})

    failures = check_assertions(results, scope=wanted)
    if args.validate_only:
        for f in failures:
            print(f"FAIL {f}")
        print(f"\n{len(ASSERTIONS) - len(failures)}/{len(ASSERTIONS)} 断言通过")
        return 1 if failures else 0

    for name, entry in results.items():
        entry["l1"] = _l1_block(name, entry.get("headline"), entry.get("policies"))
    # p07_selfcheck / p08_calibration keep their closed-form L2 floors here but
    # their L1 is simulated, so it lives in `simulated` — emitting a second l1
    # block here would only give readers two places to disagree.
    analytic = {
        name: info if name in results else {**info, "l1": _l1_block(name, info.get("headline"))}
        for name, info in ANALYTIC_ONLY.items()
    }
    judge = {
        name: {
            "headline": headline,
            "scale_floor": scale_floor,
            "reason": reason,
            "floor": "requires_degenerate_run",
            "l1": _l1_block(name, headline),
        }
        for name, (headline, scale_floor, reason) in JUDGE_ONLY.items()
    }

    payload = {
        "version": "v1",
        "generated_by": "scripts/build_benchmark_baselines.py",
        "seed": SEED,
        "schema_notes": {
            "layers": {
                "L1_uniform_random": "在题目自身答案空间上均匀抽样",
                "L2_trivial_strategy": "与题目内容无关的最优常数策略（prior_random / majority_constant / always_* ）",
                "L3_degenerate_reply": "退化生成交给真实 judge 打分，见 scripts/run_degenerate_baseline.py",
            },
            "l1_field": (
                "每个 benchmark 都带一个 l1 块，说明它的 L1 是哪个数、怎么来的："
                "source=simulated:<policy> 直接读该策略；source=analytic 是闭式；"
                "source=L3:random 由 reports/eval/_baseline/<b>/random/ 实测，写报告时解析；"
                "defined=false 才是真的没有定义。别再靠 policy 名叫不叫 uniform_random 来判断。"
            ),
            "headline": "'accuracy' 或 'extra:<dotted path into summary.json 的 extra_metrics>'",
            "warning": "L1 对约一半 benchmark 不是真正的地板，读 L2 与 note 字段。",
        },
        "simulated": results,
        "analytic_only": analytic,
        "judge_only": judge,
        "skipped": skipped,
        "assertion_failures": failures,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"\nwrote {args.out}")
    if failures:
        print("断言未全部通过：")
        for f in failures:
            print(f"  FAIL {f}")
    missing = sorted(set(available_benchmarks()) - set(SPECS) - set(ANALYTIC_ONLY) - set(JUDGE_ONLY))
    if missing:
        print(f"未覆盖的 benchmark（需补 spec）：{', '.join(missing)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
