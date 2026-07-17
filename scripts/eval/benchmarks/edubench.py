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
from ..providers import build_client, extraction_max_tokens


HOMEPAGE = "https://github.com/ybai-nlp/EduBench"
DEFAULT_JUDGE_MODEL = "deepseek-v3.2"
JUDGE_MODEL_ENV = "EDUBENCH_JUDGE_MODEL"

# Prefer the historical MiniMax-M3 prompt export because it is complete and
# preserves the stable IDs used by all imported runs.  Responses are never read.
PROMPT_SOURCE = ROOT / "reports" / "eval" / "edubench" / "minimax-m3" / "predictions.jsonl"

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

# Official dynamic metric allocation, recovered from the released bilingual
# sampled_data evaluation_metrics fields (paper Appendix E.4 / Table 7).
TASK_DIMENSIONS = {
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

JUDGE_PROMPT_VERSION = "v1-reconstructed-official-dimensions"


def _judge_prompt(item: dict[str, Any], response: str) -> str:
    metric_list = "\n".join(
        f"{idx}. {name}: {METRIC_DEFS[name]}" for idx, name in enumerate(DIMENSIONS, 1)
    )
    score_keys = ", ".join(f'"{name}": <integer 0-10>' for name in DIMENSIONS)
    task = item["meta"]["task"]
    applicable = ", ".join(TASK_DIMENSIONS[task])
    return (
        "You are an expert evaluator of AI systems used in education. Evaluate the model response "
        "against the educational task below. Score every metric independently with an integer from "
        "0 (completely fails) to 10 (excellent). Do not reward verbosity. For dimensions only weakly "
        "elicited by the task, assess only the relevant evidence and explain limited applicability.\n\n"
        f"Scenario: {TASK_NAMES[task]} ({task})\n"
        f"Scenario-applicable metrics used for the scenario score: {applicable}\n\n"
        f"[TASK GIVEN TO THE MODEL]\n{item['text']}\n\n"
        f"[MODEL RESPONSE]\n{response}\n\n"
        f"[METRICS]\n{metric_list}\n\n"
        "Return ONLY one JSON object with exactly this schema:\n"
        f'{{"scores": {{{score_keys}}}, "rationale": "<concise evidence-based justification>"}}'
    )


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
    scores: dict[str, float] = {}
    for dimension in DIMENSIONS:
        value = source.get(dimension)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return None
        value = float(value)
        if not math.isfinite(value) or not 0 <= value <= 10:
            return None
        scores[dimension] = value
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
    canonical_judge_model = DEFAULT_JUDGE_MODEL
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
        if not PROMPT_SOURCE.is_file():
            raise SystemExit(
                f"missing canonical EduBench prompt source {PROMPT_SOURCE}; "
                "restore the imported EduBench artifacts before running the adapter"
            )
        items: list[dict[str, Any]] = []
        seen: set[str] = set()
        with PROMPT_SOURCE.open(encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, 1):
                if not line.strip():
                    continue
                row = json.loads(line)
                item_id = str(row.get("item_id") or "")
                meta = row.get("metadata") or {}
                lang = str(meta.get("lang") or "en")
                if self.language != "both" and lang != self.language:
                    continue
                task = str(meta.get("task") or "")
                prompt = str(meta.get("prompt") or "")
                if not item_id or not prompt or task not in TASK_DIMENSIONS:
                    raise SystemExit(f"invalid EduBench prompt row {PROMPT_SOURCE}:{line_number}")
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
                            "applicable_dimensions": list(TASK_DIMENSIONS[task]),
                            "prompt_source": str(PROMPT_SOURCE.relative_to(ROOT)),
                        },
                    }
                )
        if self.language == "zh" and not items:
            raise SystemExit("the comparable 3,797-item EduBench prompt set is English-only")
        return items[offset : offset + limit if limit is not None else None]

    def _resolve_judge(self, extractor_client: MiniMaxClient, extractor_model: str) -> tuple[MiniMaxClient, str]:
        judge_model = os.environ.get(JUDGE_MODEL_ENV) or DEFAULT_JUDGE_MODEL
        if judge_model == extractor_model:
            return extractor_client, judge_model
        cached = getattr(self, "_judge_client", None)
        if cached is None or self._judge_client_model != judge_model:
            self._judge_client = build_client(judge_model)
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
                    [{"role": "user", "content": prompt}],
                    model=judge_model,
                    max_tokens=extraction_max_tokens(judge_model, 2048),
                )
                parsed = _parse_judgment(last_reply)
                if parsed is not None:
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
        scores = payload["scores"]
        task = item["meta"]["task"]
        overall_score = fmean(float(scores[dimension]) for dimension in DIMENSIONS)
        scenario_score = fmean(float(scores[dimension]) for dimension in TASK_DIMENSIONS[task])
        return {
            "correct": None,
            "normalized": overall_score,
            "gold": "continuous_rubric_score_0_to_10",
            "score": overall_score,
            "overall_score": overall_score,
            "scenario_score": scenario_score,
            "dimension_scores": scores,
            "applicable_dimensions": list(TASK_DIMENSIONS[task]),
            "judge_model": payload.get("judge_model"),
            "rationale": payload.get("rationale"),
            "raw_judge_output": payload.get("raw_judge_response"),
        }

    def buckets(self, item):
        meta = item["meta"]
        return {key: str(meta.get(key) or "unknown") for key in ("lang", "task", "scenario", "subject", "difficulty")}

    def judge_prompt_provenance(self):
        templates = [
            _judge_prompt({"text": "{prompt}", "meta": {"task": task}}, "{response}")
            for task in TASK_DIMENSIONS
        ]
        return {
            "judge_prompt_version": JUDGE_PROMPT_VERSION,
            "judge_prompt_sha256": prompt_sha256(*templates),
            "metric_allocation_source": "EduBench paper Appendix E.4 / released sampled_data evaluation_metrics",
            "judge_prompt_note": (
                "Reconstructed from the official 12 dimension definitions; the exact colleague-run "
                "judge prompt was not shipped, so same-judge results are comparable but not a byte-for-byte protocol replay."
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
            "metric_note": "Continuous LLM-as-Judge scores on a 0-10 scale; not accuracy.",
            "headline_metric": "mean_overall_score",
            "overall": {
                "mean_overall_score": overall_stats["mean"],
                "mean_scenario_score": scenario_stats["mean"],
            },
            "overall_score": overall_stats,
            "scenario_score": scenario_stats,
            "dimension_means": {key: _mean_ci(values) for key, values in sorted(by_dimension.items())},
            "task_scenario_means": {key: _mean_ci(values) for key, values in sorted(by_task.items())},
            "task_dimensions": {key: list(value) for key, value in TASK_DIMENSIONS.items()},
            "judge_model": judge_model,
            "n": len(rows),
        }
