"""EduBench adapter for the repository's comparable 3,797-item prompt set.

The prompt set comes from the already-imported colleague run under
``reports/eval/edubench``.  It contains five English EduBench scenarios (IP,
QG, TMG, PLS, PCC) and stable item IDs shared by the existing 11 model runs.
Using those prompts keeps newly evaluated models directly comparable.

The scoring protocol follows the official EduBench paper/repository: an LLM
judge assigns 0-10 scores on the 12 educational dimensions, while each task's
scenario score averages only the dynamically allocated dimensions.  The
headline is a continuous 12-dimension mean, never binary accuracy.
"""

from __future__ import annotations

import json
import math
import os
import re
import time
from collections import defaultdict
from pathlib import Path
from statistics import fmean, stdev
from typing import Any

from ..base import ROOT, BenchmarkAdapter, prompt_sha256
from ..minimax_client import MiniMaxClient
from ..predictions_io import predictions_exist, read_predictions
from ..providers import (
    build_client,
    extraction_max_tokens,
    resolve_model_params,
    resolve_provider,
)


HOMEPAGE = "https://github.com/ybai-nlp/EduBench"
# The 11 imported runs were all judged by deepseek-v3.2 (via the ZGC relay), and a
# judge swap changes most dimension scores (see scripts/run_edubench_judge_swap.py),
# so the judge is pinned here to stay comparable with them. This default is local to
# the EduBench adapter; every other benchmark keeps its own DEFAULT_JUDGE_MODEL.
DEFAULT_JUDGE_MODEL = "deepseek-v3.2"
JUDGE_MODEL_ENV = "EDUBENCH_JUDGE_MODEL"

# Judging is greedy so a rerun reproduces its own scores; the imported runs were
# produced the same way.
JUDGE_TEMPERATURE = 0.0

# Verbatim from the colleague runner's predict_one().
PREDICT_SYSTEM_PROMPT = "You are a helpful educational assistant."

# Prefer the historical MiniMax-M3 prompt export because it is complete and
# preserves the stable IDs used by all imported runs.  Responses are never read.
PROMPT_SOURCE = (
    ROOT
    / "reports"
    / "eval"
    / "edubench"
    / "_judge-deepseek-v3.2"
    / "minimax-m3"
    / "predictions.jsonl"
)

DIMENSIONS = (
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
)

METRIC_DEFS = {
    "instruction_following": "Instruction Following & Task Completion: executes the task and follows its format and constraints.",
    "tone_style_consistency": "Role & Tone Consistency: uses a role, tone, and expertise level appropriate to the learner and scenario.",
    "content_relevance_scope_control": "Content Relevance & Scope Control: stays focused, relevant, and within the requested subject and level.",
    "scenario_element_integration": "Scenario Element Integration: incorporates the learner, context, and educational elements supplied in the task.",
    "basic_factual_accuracy": "Basic Factual Accuracy: presents correct factual information.",
    "domain_knowledge_accuracy": "Domain Knowledge Accuracy: uses accurate specialized knowledge for the academic domain.",
    "reasoning_process_rigor": "Reasoning Process Rigor: uses logically sound reasoning and explanations.",
    "error_identification_correction_accuracy": "Error Identification & Correction Precision: detects, localizes, and corrects errors accurately when applicable.",
    "clarity_concision_inspiration": "Clarity, Simplicity & Inspiration: communicates clearly and accessibly while supporting engagement.",
    "motivation_guidance_positive_feedback": "Motivation, Guidance & Positive Feedback: gives constructive encouragement and useful guidance.",
    "personalized_adaptation_learning_support": "Personalization, Adaptation & Learning Support: adapts to learner background, proficiency, and needs.",
    "higher_order_thinking_ability_development": "Higher-Order Thinking & Skill Development: promotes analysis, problem solving, creativity, or transfer.",
}

# ---------------------------------------------------------------------------
# Two scenario->dimension tables. Only ``scenario_score`` depends on the choice;
# ``overall_score`` is the mean of all 12 dimensions and is table-independent.
#
# OFFICIAL is the correct one. It is not a reading of the paper prose: every row
# of the released ``sampled_data`` carries an explicit ``evaluation_metrics`` list
# naming that scenario's dimensions by number, and these five tuples reproduce
# those lists exactly, set-for-set, including the two no one would guess (PLS has
# only 3 dimensions, IP has 8). Reverify with:
#
#   sources/datasets/edubench/data/all_data/sampled_data/en_data_sampled.jsonl
#   PLS==student_profile  PCC==design  QG==question_gen  IP==helper  TMG==material
#
# COLLEAGUE is wrong, and is the default anyway. The 11 imported runs under
# reports/eval/edubench/_judge-deepseek-v3.2/ were scored with it, so reproducing
# it is what makes a newly evaluated model comparable with them. Their runner
# admits it was improvised ("the README does not publish a machine-readable
# mapping, so we use the natural mapping implied by scenario semantics") and its
# own comment claims 4 dimensions per scenario while the table lists 5-6; the
# real counts are 3 to 8. Being wrong the same way beats being right differently.
#
# Selected by EDUBENCH_METRIC_VARIANT; results across variants are NOT comparable.
OFFICIAL_TASK_DIMENSIONS = {
    "PLS": (
        "instruction_following",
        "scenario_element_integration",
        "personalized_adaptation_learning_support",
    ),
    "PCC": (
        "instruction_following",
        "content_relevance_scope_control",
        "scenario_element_integration",
        "personalized_adaptation_learning_support",
        "higher_order_thinking_ability_development",
    ),
    "QG": (
        "instruction_following",
        "content_relevance_scope_control",
        "basic_factual_accuracy",
        "domain_knowledge_accuracy",
        "clarity_concision_inspiration",
        "higher_order_thinking_ability_development",
    ),
    "IP": (
        "instruction_following",
        "content_relevance_scope_control",
        "scenario_element_integration",
        "basic_factual_accuracy",
        "domain_knowledge_accuracy",
        "reasoning_process_rigor",
        "clarity_concision_inspiration",
        "higher_order_thinking_ability_development",
    ),
    "TMG": (
        "instruction_following",
        "tone_style_consistency",
        "content_relevance_scope_control",
        "basic_factual_accuracy",
        "domain_knowledge_accuracy",
        "clarity_concision_inspiration",
        "higher_order_thinking_ability_development",
    ),
}

# Verbatim TASK_RECOMMENDED_METRICS from the colleague runner (five evaluated
# tasks only). Do not "fix" these to match OFFICIAL_TASK_DIMENSIONS: that would
# silently break comparability with every imported run.
COLLEAGUE_TASK_DIMENSIONS = {
    "IP": (
        "instruction_following",
        "content_relevance_scope_control",
        "reasoning_process_rigor",
        "clarity_concision_inspiration",
        "higher_order_thinking_ability_development",
    ),
    "PLS": (
        "scenario_element_integration",
        "personalized_adaptation_learning_support",
        "motivation_guidance_positive_feedback",
        "clarity_concision_inspiration",
        "higher_order_thinking_ability_development",
    ),
    "QG": (
        "instruction_following",
        "domain_knowledge_accuracy",
        "reasoning_process_rigor",
        "clarity_concision_inspiration",
        "higher_order_thinking_ability_development",
    ),
    "TMG": (
        "instruction_following",
        "scenario_element_integration",
        "domain_knowledge_accuracy",
        "clarity_concision_inspiration",
        "higher_order_thinking_ability_development",
    ),
    "PCC": (
        "scenario_element_integration",
        "domain_knowledge_accuracy",
        "clarity_concision_inspiration",
        "personalized_adaptation_learning_support",
        "higher_order_thinking_ability_development",
    ),
}

METRIC_VARIANT_ENV = "EDUBENCH_METRIC_VARIANT"
METRIC_VARIANTS = {
    "colleague": COLLEAGUE_TASK_DIMENSIONS,
    "official": OFFICIAL_TASK_DIMENSIONS,
}
DEFAULT_METRIC_VARIANT = "colleague"


def metric_variant() -> str:
    variant = (os.environ.get(METRIC_VARIANT_ENV) or DEFAULT_METRIC_VARIANT).strip().lower()
    if variant not in METRIC_VARIANTS:
        raise SystemExit(
            f"{METRIC_VARIANT_ENV}={variant!r} is not one of {sorted(METRIC_VARIANTS)}"
        )
    return variant


def task_dimensions() -> dict[str, tuple[str, ...]]:
    """The active scenario->dimension table (see the two tables above)."""
    return METRIC_VARIANTS[metric_variant()]


TASK_NAMES = {
    "IP": "Idea Provision",
    "QG": "Question Generation",
    "TMG": "Teaching Material Generation",
    "PLS": "Personalized Learning Support",
    "PCC": "Personalized Content Creation",
}

ALIASES = {
    "higher_order_ththinking_ability_development": "higher_order_thinking_ability_development",
    "basic_factural_accuracy": "basic_factual_accuracy",
}

JUDGE_PROMPT_VERSION = "v2-colleague-runner-rubric"
SCORE_SCALE = 10

# The 12-dimension banded rubric, transcribed verbatim from the colleague runner's
# ``judge_prompt`` (which describes it as a reproduction of the EduBench paper
# appendix). The bands matter: without the per-score anchors a judge drifts toward
# the middle of the scale, so this text is part of what makes a new run comparable
# with the imported ones. ``{score_scale}`` is the only placeholder.
_RUBRICS_TEMPLATE = """
[Evaluation Rubrics & Specific Scoring Details]
Please evaluate the model's response based on the following 12 dimensions. Assign a score from 1 to {score_scale} for each dimension based EXPLICITLY on the criteria below.

**Group 1: Instructional Quality**

1. instruction_following (Instruction Following & Task Completion)
Description: Did it fully understand and execute the user’s instruction? Was the core task completed? Is the output formatting correct?
• 9-10: Fully understood and precisely executed all instructions; achieved core task with perfect accuracy; output format is fully compliant.
• 7-8: Accurately understood main instructions and correctly completed the task; core goals are well achieved; format is mostly correct with only minor omissions or deviations.
• 5-6: Understood the general intent but may miss some details; task largely completed but with some inaccuracies or omissions; formatting attempts present but with notable flaws.
• 3-4: Misunderstood part of the instruction; low task completion or major errors; formatting mostly incorrect.
• 1-2: Completely misunderstood or ignored instructions; task not completed or totally incorrect; formatting is chaotic or irrelevant.

2. tone_style_consistency (Role & Tone Consistency)
Description: Does the language style, tone, and level of professionalism match the assigned role and the target learner group?
• 9-10: Excellent role-playing; language style, professionalism, and tone are perfectly aligned with the assumed role and audience.
• 7-8: Role and tone are mostly consistent and appropriate for the scenario, with minor deviation in individual expressions.
• 5-6: Attempts to match the role and tone can be seen, but overall consistency is weak; some expressions are disconnected.
• 3-4: Significant mismatch in role and tone; comes across as unnatural or inconsistent.
• 1-2: No reflection of assigned role/tone; expression entirely inconsistent with the scenario.

3. content_relevance_scope_control (Content Relevance & Scope Control)
Description: Is the content tightly aligned with the specified topic, theme, or question? Is it kept within the specified difficulty level, scenario, or scope?
• 9-10: Highly relevant to the specified topic/question; strictly within required difficulty/scope without redundant information.
• 7-8: Overall relevance is high; scope control is good with possibly a small amount of slightly off-topic information.
• 5-6: Mostly relevant, but includes some off-topic or out-of-scope content; scope control needs improvement.
• 3-4: Poor relevance; includes a significant amount of irrelevant information or is largely outside scope.
• 1-2: Content is largely irrelevant or completely outside the specified scope.

4. scenario_element_integration (Scenario Element Integration)
Description: Did it effectively use scenario-specific information (e.g., previous student answers, learning preferences)?
• 9-10: Fully integrated all key scenario elements; output is highly personalized and well-matched to the teaching context.
• 7-8: Used major scenario elements effectively; response is targeted, possibly overlooks minor details.
• 5-6: Some use of scenario information, but integration is shallow; personalization is average.
• 3-4: Only surface-level reference to scenario information; did not integrate core elements effectively.
• 1-2: Completely ignored scenario-specific information; output is generic, templated, and irrelevant.

**Group 2: Content Accuracy**

5. basic_factual_accuracy (Basic Factual Accuracy)
Description: Are objective facts such as concept definitions, formulas, dates, terminology, correctly presented?
• 9-10: All stated factual elements are completely accurate.
• 7-8: Vast majority of facts are correct; possibly contains very minor, non-critical typos or omissions.
• 5-6: Most facts are correct, but there are some notable factual errors that require review.
• 3-4: Contains several or key factual inaccuracies; information is not trustworthy.
• 1-2: Riddled with factual errors; information is completely incorrect or misleading.

6. domain_knowledge_accuracy (Domain Knowledge Accuracy)
Description: Is the use of subject matter knowledge not only correct but also appropriately specialized and aligned with domain standards?
• 9-10: Subject matter application is accurate, shows appropriate depth and rigor; adheres to standards.
• 7-8: Proper use of professional knowledge reflecting proficiency; minor shortcomings in depth.
• 5-6: Basic accuracy in subject knowledge, but somewhat surface-level or lacking rigor; some confusion of non-core concepts.
• 3-4: Significant errors or major omission in subject-specific content; lacks professionalism.
• 1-2: Serious domain errors; completely incorrect or misleading; does not meet professional standards.

7. reasoning_process_rigor (Reasoning Process Rigor)
Description: For content requiring reasoning, is the logical flow complete and sound?
• 9-10: Reasoning is complete, clear, and rigorous; all steps are correct; arguments are strong.
• 7-8: Reasoning is largely correct and logically coherent with minor issues in individual steps.
• 5-6: Reasoning is visible but contains unclear logic, missing steps, or insufficient argumentation.
• 3-4: Reasoning has major logical flaws, confusion in steps, or critical omissions; reliability is low.
• 1-2: Virtually no valid reasoning; logic is chaotic; steps are incorrect or irrelevant.

8. error_identification_correction_accuracy (Error Identification & Correction Precision)
Description: In error correction scenarios, are errors precisely identified? Are the corrections correct and optimal?
• 9-10: Precisely identified all errors; provided completely correct, clear, and optimal correction suggestions.
• 7-8: Correctly located most major errors; suggestions are generally accurate and effective with minor omissions.
• 5-6: Identified some errors but with clear omissions or false positives; suggestions are partially correct.
• 3-4: Inaccurate error detection with critical omissions or false positives; suggestions contain errors.
• 1-2: Completely failed to detect errors; provided entirely incorrect or misleading advice.

**Group 3: Pedagogical Effectiveness**

9. clarity_concision_inspiration (Clarity, Simplicity & Inspiration)
Description: Are explanations clear, concise, and easy for the target learners to understand? Is the delivery inspiring?
• 9-10: Extremely clear and concise explanations; fully accessible; vibrant delivery that inspires deep thought.
• 7-8: Clear and easy to understand; appropriate for learner level; somewhat thought-provoking.
• 5-6: Generally understandable but may be wordy, complex, or dull; limited inspirational impact.
• 3-4: Lacks clarity; uses excessive jargon; difficult to comprehend; uninspiring.
• 1-2: Confusing and hard to follow; disregards learner needs; offers no inspiration.

10. motivation_guidance_positive_feedback (Motivation, Guidance & Positive Feedback)
Description: Does the interaction provide encouragement and support? Is constructive language used? Does it guide thinking?
• 9-10: Strongly supportive; uses constructive language; offers highly effective heuristic guidance instead of simply giving answers.
• 7-8: Generally supportive tone; provides useful guidance though occasionally too direct.
• 5-6: Mix of encouragement and neutral/critical language; guidance is inconsistent or overly direct.
• 3-4: Lacks encouragement; language is neutral/mildly negative; rarely guides, often just answers.
• 1-2: Negative or discouraging tone; no motivation; fails to guide or gives misleading suggestions.

11. personalized_adaptation_learning_support (Personalization, Adaptation & Learning Support)
Description: Can it provide differentiated content/feedback based on a student’s level/needs? Does it recommend learning paths?
• 9-10: Highly personalized content/advice; resource suggestions are accurate, practical, and valuable.
• 7-8: Demonstrates some adaptation; provides relevant learning advice with good utility.
• 5-6: Attempts personalization but with limited effectiveness; recommendations are generic.
• 3-4: Little to no personalization; output is the same for everyone; learning support is insufficient.
• 1-2: No personalization; output conflicts with student needs; offers no learning support.

12. higher_order_thinking_ability_development (Higher-Order Thinking & Skill Development)
Description: Does the interaction help foster students’ critical thinking, creativity, or problem-solving?
• 9-10: Skillfully designed to promote critical/creative thinking, problem-solving (e.g., open-ended questions, case studies).
• 7-8: Includes guiding questions or moderately challenging tasks that positively support higher-order thinking.
• 5-6: Some attempt to encourage higher-order thinking, but limited in depth; focused on rote understanding.
• 3-4: Interaction mostly revolves around memory and comprehension; rarely addresses higher-order tasks.
• 1-2: Completely ignores higher-order skill development; encourages rote memorization; inhibits thinking flexibility.
"""


def _judge_system_prompt() -> str:
    return "You are a strict educational evaluation expert. Return valid JSON only."


def _judge_prompt(item: dict[str, Any], response: str, score_scale: int = SCORE_SCALE) -> str:
    """Reproduce the colleague runner's judge prompt for one (item, response).

    Field order, wording, and the trailing JSON schema are kept as-is; the only
    substitution is this repo's item schema for their prediction-row schema.
    """
    meta = item["meta"]
    task = meta["task"]
    recommended = ", ".join(task_dimensions()[task])
    rubrics_text = _RUBRICS_TEMPLATE.replace("{score_scale}", str(score_scale))
    score_lines = ",\n".join(f'    "{name}": <number>' for name in DIMENSIONS)
    return f"""You are an expert evaluating an LLM response for EduBench, a benchmark for educational scenarios.

Use the official EduBench Evaluation Rubrics provided below. Score every metric from 1 to {score_scale}.

Scenario: {task} ({meta.get('scenario') or TASK_NAMES[task]})
Language: {meta.get('lang', 'en')}
Subject: {meta.get('subject', 'unknown')}
Difficulty: {meta.get('difficulty', 'unknown')}

{rubrics_text}

Metrics especially relevant to this scenario (Pay special attention to these):
{recommended}

Input prompt:
{item['text']}

Model response:
{response}

Return ONLY valid JSON with this exact structure:
{{
  "scores": {{
{score_lines}
  }},
  "scenario_score": <average over scenario-relevant metrics>,
  "overall_score": <average over all 12 metrics>,
  "rationale": "brief explanation based strictly on the detailed 1-{score_scale} rubrics above"
}}
"""


def _parse_judgment(text: str) -> dict[str, Any] | None:
    raw = (text or "").strip()
    candidates = [raw]
    match = re.search(r"\{.*\}", raw, flags=re.DOTALL)
    if match and match.group(0) != raw:
        candidates.append(match.group(0))
    payload: Any = None
    for candidate in candidates:
        try:
            payload = json.loads(candidate)
            break
        except json.JSONDecodeError:
            continue
    if not isinstance(payload, dict):
        return None
    source = payload.get("scores") or payload.get("detailed_scores")
    if not isinstance(source, dict):
        return None
    source = {ALIASES.get(str(key), str(key)): value for key, value in source.items()}
    # Colleague-runner tolerance (their ``coerce_score``): an unusable dimension
    # becomes NaN and is skipped when averaging, and out-of-range values are
    # clamped into [1, SCORE_SCALE] rather than rejected. Only a reply with no
    # usable dimension at all fails, so the two runs keep the same denominator.
    scores: dict[str, float] = {}
    for dimension in DIMENSIONS:
        value = source.get(dimension)
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)):
            scores[dimension] = math.nan
            continue
        scores[dimension] = max(1.0, min(float(SCORE_SCALE), float(value)))
    if all(math.isnan(value) for value in scores.values()):
        return None
    return {"scores": scores, "rationale": str(payload.get("rationale") or payload.get("reason") or "")[:4000]}


def _mean_ci(values: list[float]) -> dict[str, float | int | None]:
    clean = [float(value) for value in values if math.isfinite(float(value))]
    if not clean:
        return {"n": 0, "mean": None, "ci_lower": None, "ci_upper": None}
    mean = fmean(clean)
    margin = 0.0 if len(clean) < 2 else 1.96 * stdev(clean) / math.sqrt(len(clean))
    return {
        "n": len(clean),
        "mean": mean,
        "ci_lower": max(0.0, mean - margin),
        "ci_upper": min(10.0, mean + margin),
    }


class EduBenchAdapter(BenchmarkAdapter):
    name = "edubench"
    title = "EduBench · Diverse Educational Scenarios"
    homepage = HOMEPAGE
    description = (
        "EduBench evaluates open-ended generation in diverse educational scenarios. This adapter "
        "uses the repository's existing 3,797-item English prompt set (IP, QG, TMG, PLS, PCC) so "
        "new runs share stable item IDs with the 11 imported colleague runs.\n\n"
        "A fixed LLM judge scores all 12 official dimensions from 0 to 10. The headline is the mean "
        "of the 12 dimensions; scenario_score averages only the task-applicable official dimensions. "
        "These are continuous judged scores, not correctness or accuracy. The rubric prompt is "
        "reconstructed from the paper because neither upstream nor the colleague artifacts contain "
        "the exact original evaluator prompt."
    )
    language = "both"

    def load_items(self, limit: int | None = None, offset: int = 0) -> list[dict[str, Any]]:
        if not predictions_exist(PROMPT_SOURCE):
            raise SystemExit(
                f"missing canonical EduBench prompt source {PROMPT_SOURCE}; "
                "restore the imported EduBench artifacts before running the adapter"
            )
        items: list[dict[str, Any]] = []
        seen: set[str] = set()
        active_table = task_dimensions()
        for row_number, row in enumerate(read_predictions(PROMPT_SOURCE), 1):
            item_id = str(row.get("item_id") or "")
            meta = row.get("metadata") or {}
            lang = str(meta.get("lang") or "en")
            if self.language != "both" and lang != self.language:
                continue
            task = str(meta.get("task") or "")
            prompt = str(meta.get("prompt") or "")
            if not item_id or not prompt or task not in OFFICIAL_TASK_DIMENSIONS:
                raise SystemExit(f"invalid EduBench prompt row {PROMPT_SOURCE}:{row_number}")
            if item_id in seen:
                raise SystemExit(f"duplicate EduBench item_id {item_id} in {PROMPT_SOURCE}")
            seen.add(item_id)
            items.append(
                {
                    "item_id": item_id,
                    "text": prompt,
                    "image_paths": [],
                    "gold": "continuous_rubric_score_0_to_10",
                    "meta": {
                        "lang": lang,
                        "task": task,
                        "scenario": meta.get("scenario") or TASK_NAMES[task],
                        "subject": meta.get("subject") or "unknown",
                        "difficulty": meta.get("difficulty") or "unknown",
                        "applicable_dimensions": list(active_table[task]),
                        "prompt_source": str(PROMPT_SOURCE.relative_to(ROOT)),
                    },
                }
            )
        if self.language == "zh" and not items:
            raise SystemExit("the comparable 3,797-item EduBench prompt set is English-only")
        return items[offset : offset + limit if limit is not None else None]

    def build_messages(self, item):
        """Prepend the colleague runner's system prompt.

        Their ``predict_one`` sends this exact system turn before the task, so a
        model evaluated here sees the same framing as the imported runs. EduBench
        items are text-only, hence no image parts.
        """
        return [
            {"role": "system", "content": PREDICT_SYSTEM_PROMPT},
            {"role": "user", "content": item["text"]},
        ]

    def _resolve_judge(self, extractor_client: MiniMaxClient, extractor_model: str) -> tuple[MiniMaxClient, str]:
        """Always build a dedicated judge client.

        It deliberately does *not* reuse ``extractor_client`` even when the judge and
        extractor happen to be the same model: the shared client carries neither
        ``temperature=0`` nor the forced-JSON response format, so reusing it would
        silently judge under different settings than the imported runs.
        """
        judge_model = os.environ.get(JUDGE_MODEL_ENV) or DEFAULT_JUDGE_MODEL
        cached = getattr(self, "_judge_client", None)
        if cached is None or self._judge_client_model != judge_model:
            params = dict(resolve_model_params(judge_model, resolve_provider(judge_model).name))
            params["response_format"] = {"type": "json_object"}
            self._judge_client = build_client(
                judge_model,
                temperature=JUDGE_TEMPERATURE,
                extra_params=params,
            )
            self._judge_client_model = judge_model
        return self._judge_client, judge_model

    def resolved_judge_model(self, extractor_model: str) -> str | None:
        return os.environ.get(JUDGE_MODEL_ENV) or DEFAULT_JUDGE_MODEL

    def extract_answer(self, item, response, client, model):
        judge_client, judge_model = self._resolve_judge(client, model)
        prompt = _judge_prompt(item, response or "")
        last_reply = ""
        last_error: Exception | None = None
        for attempt in range(3):
            try:
                last_reply = judge_client.chat(
                    [
                        {"role": "system", "content": _judge_system_prompt()},
                        {"role": "user", "content": prompt},
                    ],
                    model=judge_model,
                    max_tokens=extraction_max_tokens(judge_model, 2048),
                )
                parsed = _parse_judgment(last_reply)
                if parsed is not None:
                    # NaN would serialise as a bare ``NaN`` token, which is not valid
                    # JSON; unusable dimensions travel as null and score() reads them
                    # back as NaN so they are skipped when averaging.
                    parsed["scores"] = {
                        key: (None if math.isnan(value) else value)
                        for key, value in parsed["scores"].items()
                    }
                    return json.dumps(
                        {"judge_model": judge_model, **parsed, "raw_judge_response": last_reply},
                        ensure_ascii=False,
                    )
            except Exception as exc:  # noqa: BLE001 - retry transient judge/provider failures
                last_error = exc
            if attempt < 2:
                time.sleep(1.5 * (attempt + 1))
        if last_error is not None and not last_reply:
            raise RuntimeError(f"EduBench judge failed after 3 attempts: {last_error}") from last_error
        raise RuntimeError(f"EduBench judge returned unparseable scores: {last_reply[:300]!r}")

    def score(self, extracted, item):
        payload = json.loads(extracted)
        scores = {
            key: (math.nan if value is None else float(value))
            for key, value in payload["scores"].items()
        }
        task = item["meta"]["task"]
        active = task_dimensions()

        def _mean_skip_nan(names) -> float:
            usable = [scores[name] for name in names if not math.isnan(scores.get(name, math.nan))]
            return fmean(usable) if usable else math.nan

        overall_score = _mean_skip_nan(DIMENSIONS)
        scenario_score = _mean_skip_nan(active[task])
        # The colleague runner falls back to the overall mean when no scenario
        # dimension survived, rather than dropping the row.
        if math.isnan(scenario_score):
            scenario_score = overall_score
        return {
            "correct": None,
            "normalized": overall_score,
            "gold": "continuous_rubric_score_0_to_10",
            "score": overall_score,
            "overall_score": overall_score,
            "scenario_score": scenario_score,
            # NaN is not valid JSON, so an unusable dimension is written as null;
            # the means above already skipped it exactly as the colleague runner does.
            "dimension_scores": {k: (None if math.isnan(v) else v) for k, v in scores.items()},
            "metric_variant": metric_variant(),
            "applicable_dimensions": list(active[task]),
            "judge_model": payload.get("judge_model"),
            "rationale": payload.get("rationale"),
            "raw_judge_output": payload.get("raw_judge_response"),
        }

    def buckets(self, item):
        meta = item["meta"]
        return {key: str(meta.get(key) or "unknown") for key in ("lang", "task", "scenario", "subject", "difficulty")}

    def judge_prompt_provenance(self):
        templates = [
            _judge_prompt(
                {
                    "text": "{prompt}",
                    "meta": {
                        "task": task,
                        "scenario": TASK_NAMES[task],
                        "lang": "{lang}",
                        "subject": "{subject}",
                        "difficulty": "{difficulty}",
                    },
                },
                "{response}",
            )
            for task in sorted(task_dimensions())
        ]
        variant = metric_variant()
        return {
            "judge_prompt_version": JUDGE_PROMPT_VERSION,
            "judge_prompt_sha256": prompt_sha256(*templates),
            "metric_variant": variant,
            "metric_allocation_source": (
                "colleague runner TASK_RECOMMENDED_METRICS (improvised; reproduced for comparability)"
                if variant == "colleague"
                else "released sampled_data evaluation_metrics fields (verified set-for-set)"
            ),
            "judge_prompt_note": (
                "Byte-identical to the colleague runner's judge_prompt, verified against all 3,797 "
                "prompts of the imported run. Judge system prompt, temperature 0, and forced-JSON "
                "response format also match, so scores are directly comparable with the imported runs."
            ),
            "prompt_set_source": str(PROMPT_SOURCE.relative_to(ROOT)),
            "prompt_set_note": "Comparable 3,797-item colleague prompt export; not the official 198-item human-evaluation sample.",
        }

    def extra_summary(self, scored):
        rows = [row for row in scored if row.get("score_status") == "scored" and isinstance(row.get("overall_score"), (int, float))]
        judge_model = os.environ.get(JUDGE_MODEL_ENV) or DEFAULT_JUDGE_MODEL
        overall = [float(row["overall_score"]) for row in rows]
        scenario = [float(row["scenario_score"]) for row in rows]
        by_dimension: dict[str, list[float]] = defaultdict(list)
        by_task: dict[str, list[float]] = defaultdict(list)
        for row in rows:
            for dimension, value in (row.get("dimension_scores") or {}).items():
                if dimension in DIMENSIONS and isinstance(value, (int, float)):
                    by_dimension[dimension].append(float(value))
            by_task[str((row.get("buckets") or {}).get("task") or "unknown")].append(float(row["scenario_score"]))
        overall_stats = _mean_ci(overall)
        scenario_stats = _mean_ci(scenario)
        return {
            "metric_note": "Continuous LLM-as-Judge scores on a 1-10 scale; not accuracy.",
            "metric_variant": metric_variant(),
            "headline_metric": "mean_overall_score",
            "overall": {
                "mean_overall_score": overall_stats["mean"],
                "mean_scenario_score": scenario_stats["mean"],
            },
            "overall_score": overall_stats,
            "scenario_score": scenario_stats,
            "dimension_means": {key: _mean_ci(values) for key, values in sorted(by_dimension.items())},
            "task_scenario_means": {key: _mean_ci(values) for key, values in sorted(by_task.items())},
            "metric_variant": metric_variant(),
            "task_dimensions": {key: list(value) for key, value in task_dimensions().items()},
            "judge_model": judge_model,
            "n": len(rows),
        }
