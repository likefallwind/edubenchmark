"""MathTutorBench adapters (C4 deep test: 过程评分 / 反馈质量, D11; 错误诊断与反馈 D12/D13).

Source: a local clone of https://github.com/eth-lre/mathtutorbench (EMNLP 2025,
arXiv 2502.18940) under ``sources/datasets/mathtutorbench/``. MathTutorBench
measures open-ended *pedagogical* capability of LLM tutors across 7 tasks (+2
"hard" variants). This module ports the official scoring (under ``tasks/`` and
``dataloaders/``) — reimplemented with the standard library only, matching how
MathVista/AGIEval/OlympiadBench port their official evaluators — and adds an
LLM-as-judge replacement for the two open-ended tasks that the paper scores with
a trained 1.5B reward model (GPU + HF weights), which this harness does not run.

Run ``python scripts/eval/data/fetch_eval_datasets.py --benchmark mathtutorbench``
first to materialize the JSONL data.

Registered adapters (each a separate ``--benchmark`` with its own report dir):

Closed-form (deterministic, no judge — extraction is a regex with an LLM fallback
only for verbose reasoning outputs):
  - ``mathtutorbench_problem_solving``      GSM8K main: exact-match final answer.
  - ``mathtutorbench_socratic``             GSM8K socratic: SacreBLEU vs refs.
  - ``mathtutorbench_solution_correctness`` stepverify: Yes/No → accuracy + P/R/F1.
  - ``mathtutorbench_mistake_location``     stepverify: step number → F1 micro/macro/weighted.
  - ``mathtutorbench_mistake_correction``   stepverify: numeric final answer accuracy.

Open-ended pedagogical (LLM-as-judge pairwise win-rate vs the ground-truth teacher
utterance, using the official reward-model rubric, position-swapped to debias):
  - ``mathtutorbench_scaffolding`` / ``_hard``  (mathdial_bridge[_hard].json)
  - ``mathtutorbench_pedagogy``    / ``_hard``

Judge selection (done first; the *model under test is itself the candidate judge*,
so it needs no judge infra — it reuses the predict→extract→score flow):
  - ``mathtutorbench_judge_calibration``  pedagogical-rewardmodel-data test split;
    the judge picks the better of an expert positive/negative pair. Accuracy =
    agreement with human preference (comparable to the reward model's win-rate).

The fixed judge for the win-rate tasks is ``MATHTUTORBENCH_JUDGE_MODEL`` (default
``MiniMax-M3``), decoupled from ``--extractor-model`` like ``eduguard_adversarial``.
"""

from __future__ import annotations

import json
import os
import re
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from ..base import ROOT, BenchmarkAdapter, prompt_sha256
from ..minimax_client import MiniMaxClient
from ..providers import extraction_max_tokens
from ..scoring import binary_prf1, multiclass_f1


CLONE = ROOT / "sources" / "datasets" / "mathtutorbench"
DATA = CLONE / "data"
BRIDGE_DIR = CLONE / "datasets"
HOMEPAGE = "https://github.com/eth-lre/mathtutorbench"

# Version of the pairwise judge prompt (REWARD_RUBRIC + _pairwise_prompt),
# shared by the win-rate tasks and judge calibration. Bump on any wording
# change; summary.json records it plus the template hash.
JUDGE_PROMPT_VERSION = "v1"


def _pairwise_judge_provenance() -> dict[str, Any]:
    placeholder_meta = {
        "problem": "{problem}",
        "reference_solution": "{reference_solution}",
        "dialog_history": "{dialog_history}",
    }
    template = _WinRateBase._pairwise_prompt(placeholder_meta, "{response_a}", "{response_b}")
    return {
        "judge_prompt_version": JUDGE_PROMPT_VERSION,
        "judge_prompt_sha256": prompt_sha256(template),
    }

# The official reward model's grading rubric, verbatim from
# reward_model/compute_scaffolding_score.py:SYSTEM_PROMPT. Reused to ground both
# the judge-calibration and the win-rate LLM-as-judge so the LLM judge optimizes
# the same pedagogical criteria as the trained reward model it replaces.
REWARD_RUBRIC = (
    "Judge the pedagogical quality of the responses provided by two teachers. "
    "Focus on the quality of the scaffolding guidance, correctness, and "
    "actionability of the feedback through nudges, questions and hints. Do not "
    "give high scores for revealing the full answer."
)

# A response longer than this is treated as verbose reasoning: the official
# regex parsers over-capture on it, so we route it through the extractor model
# (mirrors eduguard_sata's long-response branch).
VERBOSE_LEN = 80


def _read_jsonl(path) -> list[dict[str, Any]]:
    if not path.exists():
        raise SystemExit(
            f"missing {path}; run: python scripts/eval/data/fetch_eval_datasets.py --benchmark mathtutorbench"
        )
    rows = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _read_json(path) -> list[dict[str, Any]]:
    if not path.exists():
        raise SystemExit(f"missing {path}; expected it inside the mathtutorbench clone")
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def _llm_extract(client: MiniMaxClient, model: str, instruction: str, response: str) -> str:
    """Ask the extractor model to isolate a final answer from a verbose response."""
    prompt = f"{instruction}\n\nModel response:\n---\n{response}\n---\n\nAnswer:"
    return client.chat(
        [{"role": "user", "content": prompt}],
        model=model,
        max_tokens=extraction_max_tokens(model, 512),
    )


# ---------------------------------------------------------------------------
# Shared StepVerify formatting (ported verbatim from the official
# tasks/{solution_correctness,mistake_location,mistake_correction}.py
# _format_dataset). NOTE: the official code joins student steps with the literal
# two-character separator "\\n" (not a newline); replicated for leaderboard
# comparability.
# ---------------------------------------------------------------------------


def _format_stepverify(rows: list[dict[str, Any]], twins: bool) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for ex in rows:
        conv = ex.get("dialog_history") or []
        formatted, cutoff = [], len(conv)
        for i, turn in enumerate(conv):
            if turn.get("user") == "Student":
                cutoff = i
                break
            formatted.append(f"Teacher: {turn['text']}")
        dialog_str = "\n".join(formatted)
        student_chat = conv[cutoff]["text"] if cutoff < len(conv) else ""

        incorrect = ex.get("student_incorrect_solution") or []
        out.append(
            {
                "question": ex["problem"],
                "student_solution": "\\n".join(
                    f"Step {i + 1} - {s}" for i, s in enumerate(incorrect[:-1])
                ),
                "is_error": True,
                "error_step": int(ex["incorrect_index"]) + 1,
                "dialog_history": dialog_str,
                "student_chat_solution": student_chat,
                "reference_solution": ex["reference_solution"],
            }
        )
        if not twins:
            continue
        ref_steps = ex["reference_solution"].split("\n")[:-1]
        out.append(
            {
                "question": ex["problem"],
                "student_solution": "\\n".join(
                    f"Step {i + 1} - {s}" for i, s in enumerate(ref_steps)
                ),
                "is_error": False,
                "error_step": 0,
                "dialog_history": dialog_str,
                "student_chat_solution": ex.get("student_correct_response", ""),
                "reference_solution": ex["reference_solution"],
            }
        )
    return out


# ---------------------------------------------------------------------------
# StepVerify tasks
# ---------------------------------------------------------------------------

# few-shot blocks ported from configs/*.yaml
_SHOTS_SOLUTION = (
    "Problem: Natalia sold clips to 48 of her friends in April, and then she sold half as many clips in May. "
    "How many clips did Natalia sell altogether in April and May?\n"
    "Student Solution: I started by calculating clips in May which is 48/2 = 24. Then I sum this up, so she "
    "sold 48+24 = 72 clips in April and May together.\n"
    "Q: Is the Student Solution incorrect? Write 'Yes' if it is incorrect, or 'No' if it is correct.\n"
    "A: No"
)

_SHOTS_LOCATION = (
    "Problem: Natalia sold clips to 48 of her friends in April, and then she sold half as many clips in May. "
    "How many clips did Natalia sell altogether in April and May?\n"
    "Student Solution: Step 1 - She sold 48/2 = 24 clips in May.\n"
    "Step 2 - Natalia sold 48+24 = 72 clips in April and May together.\n"
    "Q: Is the Student Solution incorrect? Write only the step number with the first error or 0 if no error is found.\n"
    "A: 0\n"
    "Problem: Natalia sold clips to 48 of her friends in April, and then she sold half as many clips in May. "
    "How many clips did Natalia sell altogether in April and May?\n"
    "Student Solution: Step 1 - Natalia sold 48 clips in April.\n"
    "Step 2 - She sold 48*2 = 96 clips in May.\n"
    "Step 3 - She sold 48+96 = 144 clips in April and May together.\n"
    "Q: Is the Student Solution incorrect? Write only the step number with the first error or 0 if no error is found.\n"
    "A: 2"
)


class MTBSolutionCorrectness(BenchmarkAdapter):
    name = "mathtutorbench_solution_correctness"
    title = "MathTutorBench · Student Solution Correctness"
    homepage = HOMEPAGE
    description = (
        "判断学生解答是否正确（Yes/No 二分类）。数据来自 eth-nlped/stepverify，每题展开为"
        "“含错误”与“正确（参考解）”两条样本。移植官方 tasks/solution_correctness.py 的"
        " parse_response（在回复中找 yes/no）与评分；正确率即官方 accuracy，"
        "extra_metrics 另给 precision/recall/F1（正类=判定为错误）。对应 D12（错误诊断）。"
    )

    def load_items(self, limit: int | None = None, offset: int = 0) -> list[dict[str, Any]]:
        items = []
        for idx, ex in enumerate(_format_stepverify(_read_jsonl(DATA / "stepverify.jsonl"), twins=True)):
            text = (
                "You are an experienced math teacher. Your goal is to identify the correctness of the "
                "Student's Solution to a Problem.\n"
                f"{_SHOTS_SOLUTION}\n\n"
                f"Problem: {ex['question']}\n"
                "Conversation:\n"
                f"{ex['dialog_history']}\n"
                f"Student: {ex['student_chat_solution']}\n"
                "Q: Is the Student Solution incorrect? Write 'Yes' if it is incorrect, or 'No' if it is correct.\n"
                "A:"
            )
            items.append(
                {
                    "item_id": f"sc-{idx}",
                    "text": text,
                    "image_paths": [],
                    "gold": "Yes" if ex["is_error"] else "No",
                    "meta": {"is_error": ex["is_error"], "error_category": None},
                }
            )
        return items[offset : offset + limit if limit is not None else None]

    @staticmethod
    def _parse(response: str) -> str:
        low = (response or "").strip().lower()
        # Official parse_response: 'yes'->incorrect, 'no'->correct, default incorrect.
        if "yes" in low:
            return "Yes"
        if "no" in low:
            return "No"
        return "Yes"

    def extract_answer(self, item, response, client, model):
        response = (response or "").strip()
        if len(response) > VERBOSE_LEN:
            response = _llm_extract(
                client, model,
                "The text below is a teacher judging whether a student's solution is incorrect. "
                "Output only 'Yes' (incorrect) or 'No' (correct).",
                response,
            )
        return self._parse(response)

    def score(self, extracted, item):
        pred = self._parse(extracted)
        gold = item["gold"]
        return {
            "correct": pred == gold,
            "normalized": pred,
            "gold": gold,
            "pred_label": pred == "Yes",
            "gold_label": gold == "Yes",
        }

    def buckets(self, item):
        return {"is_error": "error" if item["meta"]["is_error"] else "correct"}

    def extra_summary(self, scored):
        rows = [r for r in scored if r.get("score_status") == "scored"]
        if not rows:
            return {}
        targets = [bool(r.get("gold_label")) for r in rows]
        preds = [bool(r.get("pred_label")) for r in rows]
        m = binary_prf1(targets, preds)
        return {
            "official_metric": "accuracy / precision / recall / f1 (pos=incorrect)",
            "n": len(rows),
            **{k: round(v, 4) for k, v in m.items()},
        }


class MTBMistakeLocation(BenchmarkAdapter):
    name = "mathtutorbench_mistake_location"
    title = "MathTutorBench · Mistake Location"
    homepage = HOMEPAGE
    description = (
        "定位学生解答中第一处错误的步骤号（0 表示无错误）。数据 eth-nlped/stepverify，"
        "每题展开为含错误/正确两条样本。移植官方 tasks/mistake_location.py：parse_response "
        "取回复中的首个整数，评分用步骤号 F1（micro/macro/weighted）。报告“正确率”为步骤号"
        "完全匹配率，官方 F1 见 extra_metrics。对应 D12（错误定位）。"
    )

    def load_items(self, limit: int | None = None, offset: int = 0) -> list[dict[str, Any]]:
        items = []
        for idx, ex in enumerate(_format_stepverify(_read_jsonl(DATA / "stepverify.jsonl"), twins=True)):
            text = (
                "You are an experienced math teacher. Your goal is to identify the step of the first "
                "mistake in the Student's Solution to a Problem.\n"
                f"{_SHOTS_LOCATION}\n\n"
                f"Problem: {ex['question']}\n"
                f"Student Solution: {ex['student_solution']}\n"
                "Q: Is the Student Solution incorrect? Write only the step number with the first error or 0 "
                "if no error is found.\n"
                "A:"
            )
            items.append(
                {
                    "item_id": f"ml-{idx}",
                    "text": text,
                    "image_paths": [],
                    "gold": int(ex["error_step"]),
                    "meta": {"is_error": ex["is_error"]},
                }
            )
        return items[offset : offset + limit if limit is not None else None]

    @staticmethod
    def _parse(response: str) -> int:
        m = re.search(r"\d+", response or "")
        return int(m.group()) if m else 0

    def extract_answer(self, item, response, client, model):
        response = (response or "").strip()
        if len(response) > VERBOSE_LEN:
            response = _llm_extract(
                client, model,
                "The text below is a teacher identifying the first wrong step in a student's solution. "
                "Output only the step number as a single integer (0 if no error).",
                response,
            )
        return str(self._parse(response))

    def score(self, extracted, item):
        pred = self._parse(extracted)
        gold = int(item["gold"])
        return {
            "correct": pred == gold,
            "normalized": pred,
            "gold": gold,
            "step_pred": pred,
            "step_gold": gold,
        }

    def buckets(self, item):
        return {"is_error": "error" if item["meta"]["is_error"] else "correct"}

    def extra_summary(self, scored):
        rows = [r for r in scored if r.get("score_status") == "scored"]
        if not rows:
            return {}
        targets = [int(r.get("step_gold")) for r in rows]
        preds = [int(r.get("step_pred")) for r in rows]
        m = multiclass_f1(targets, preds)
        return {
            "official_metric": "f1_micro / f1_macro / f1_weighted over step numbers",
            "n": len(rows),
            **{k: round(v, 4) for k, v in m.items()},
        }


class MTBMistakeCorrection(BenchmarkAdapter):
    name = "mathtutorbench_mistake_correction"
    title = "MathTutorBench · Mistake Correction"
    homepage = HOMEPAGE
    description = (
        "给定含错误的对话与题目，生成完整正确解并在 'Final Answer:' 后给出最终答案。数据 "
        "eth-nlped/stepverify（仅取含错误样本）。移植官方 tasks/mistake_correction.py：从回复"
        "解析 Final Answer / 末尾数字，与参考解最终数字按 |Δ|<1e-6 比较。正确率即官方 "
        "accuracy。对应 D13（纠错与反馈）。"
    )

    def load_items(self, limit: int | None = None, offset: int = 0) -> list[dict[str, Any]]:
        items = []
        for idx, ex in enumerate(_format_stepverify(_read_jsonl(DATA / "stepverify.jsonl"), twins=False)):
            text = (
                "You are a helpful math tutor assisting a student. Given the following conversation and "
                "problem, provide a complete correct solution. Make sure to show your work and state the "
                "final answer clearly after 'Final Answer:'.\n"
                f"Problem: {ex['question']}\n"
                "Conversation:\n"
                f"{ex['dialog_history']}\n"
                f"Student: {ex['student_chat_solution']}\n"
                "Teacher: "
            )
            gold = ex["reference_solution"].split("\n")[-1].replace(",", "").strip()
            items.append(
                {
                    "item_id": f"mc-{idx}",
                    "text": text,
                    "image_paths": [],
                    "gold": gold,
                    "meta": {},
                }
            )
        return items[offset : offset + limit if limit is not None else None]

    @staticmethod
    def _parse(response: str):
        if not response:
            return None
        m = re.search(r"Final Answer:\s*\$?([-,\d]*\.?\d+)", response)
        if m:
            try:
                return float(m.group(1).replace(",", ""))
            except ValueError:
                return None
        nums = re.findall(r"\$?([-,\d]*\.?\d+)", response)
        if nums:
            try:
                return float(nums[-1].replace(",", ""))
            except ValueError:
                return None
        return None

    def extract_answer(self, item, response, client, model):
        # The official parser handles long solutions fine (anchored on 'Final
        # Answer:'); only fall back if no number is found at all.
        parsed = self._parse(response or "")
        if parsed is None and (response or "").strip():
            response = _llm_extract(
                client, model,
                "The text below is a worked math solution. Output only the final numeric answer.",
                response,
            )
            parsed = self._parse(response)
        return "" if parsed is None else repr(parsed)

    def score(self, extracted, item):
        try:
            pred = float(extracted) if extracted else None
        except ValueError:
            pred = None
        try:
            gold = float(str(item["gold"]).replace(",", ""))
        except ValueError:
            gold = None
        correct = pred is not None and gold is not None and abs(pred - gold) < 1e-6
        return {"correct": correct, "normalized": pred, "gold": item["gold"]}


# ---------------------------------------------------------------------------
# GSM8K tasks
# ---------------------------------------------------------------------------

_SHOTS_PROBLEM = (
    "Question: Janet's ducks lay 16 eggs per day. She eats three for breakfast every morning and sells the "
    "rest at the farmers market daily for $2 per egg. How much in dollars does she make per day at the "
    "farmers market?\n"
    "Answer: Janet sells 16-3 = 13 eggs. Janet makes 13*2 = 26 dollars per day at the farmers' market. "
    "Final answer: 26\n"
    "Question: Natalie sold clips to 48 of her friends in April, and then she sold half as many clips in May. "
    "How many clips did Natalie sell in all?\n"
    "Answer: Natalia sold 48/2 = 24 clips in May. Natalia sold 48+24 = 72 clips altogether in April and May. "
    "Final answer: 72"
)

_SHOTS_SOCRATIC = (
    "Problem: Janet's ducks lay 16 eggs per day. She eats three for breakfast every morning and sells the "
    "rest at the farmers market daily for $2 per egg. How much in dollars does she make per day at the "
    "farmers market?\n"
    "Questions: How many eggs does Janet sell? How much does Janet make at the farmers' market?"
)


class MTBProblemSolving(BenchmarkAdapter):
    name = "mathtutorbench_problem_solving"
    title = "MathTutorBench · Problem Solving (gate)"
    homepage = HOMEPAGE
    description = (
        "GSM8K 解题（gate 项，检验基础数学能力，非教学能力）。移植官方 problem_solving 配置："
        "few-shot 提示后取 'Final answer' 后的数字，与 GSM8K 金标（'### '后数字）精确匹配。"
        "正确率即官方 accuracy。对应 D06/D01 类基础能力，仅作门槛。"
    )

    def load_items(self, limit: int | None = None, offset: int = 0) -> list[dict[str, Any]]:
        items = []
        for idx, ex in enumerate(_read_jsonl(DATA / "gsm8k_main.jsonl")):
            text = (
                "You are a helpful math tutor. Solve the question step-by-step. Provide your final answer "
                "after 'Final answer'.\n"
                f"{_SHOTS_PROBLEM}\n\n"
                f"Question: {ex['question']}\n"
                "Answer:"
            )
            gold = ex["answer"].split("### ")[-1].replace(",", "").strip()
            items.append(
                {"item_id": f"ps-{idx}", "text": text, "image_paths": [], "gold": gold, "meta": {}}
            )
        return items[offset : offset + limit if limit is not None else None]

    @staticmethod
    def _parse(response: str):
        if not response:
            return None
        m = re.search(r"[Ff]inal answer[:\s]*\$?([-,\d]*\.?\d+)", response)
        if m:
            try:
                return float(m.group(1).replace(",", ""))
            except ValueError:
                return None
        nums = re.findall(r"\$?([-,\d]*\.?\d+)", response)
        if nums:
            try:
                return float(nums[-1].replace(",", ""))
            except ValueError:
                return None
        return None

    def extract_answer(self, item, response, client, model):
        parsed = self._parse(response or "")
        if parsed is None and (response or "").strip():
            response = _llm_extract(
                client, model,
                "The text below solves a math word problem. Output only the final numeric answer.",
                response,
            )
            parsed = self._parse(response)
        return "" if parsed is None else repr(parsed)

    def score(self, extracted, item):
        try:
            pred = float(extracted) if extracted else None
        except ValueError:
            pred = None
        try:
            gold = float(str(item["gold"]).replace(",", ""))
        except ValueError:
            gold = None
        correct = pred is not None and gold is not None and abs(pred - gold) < 1e-6
        return {"correct": correct, "normalized": pred, "gold": item["gold"]}


class MTBSocratic(BenchmarkAdapter):
    name = "mathtutorbench_socratic"
    title = "MathTutorBench · Socratic Questioning"
    homepage = HOMEPAGE
    description = (
        "苏格拉底式提问：为题目生成一串引导性问题。数据 GSM8K socratic。移植官方 "
        "tasks/socratic_questioning.py：与金标问题（按 ' ** ' 切分取问句）做 SacreBLEU，取最佳匹配。"
        "官方用 completion + stop=['\\n'] 截成单行，chat 框架无 stop，故抽取阶段取回复首行非空内容"
        "以对齐官方口径。报告“正确率”为 BLEU≥0.5 的粗略占比，官方均值 BLEU 见 extra_metrics。"
        "对应 D13（启发式提问）。需要 sacrebleu。"
    )

    @staticmethod
    def _gt_questions(answer: str) -> list[str]:
        questions = []
        for line in (answer or "").split("\n"):
            if len(line.split(" ** ")) == 2:
                questions.append(line.split(" ** ")[0])
        return questions

    def load_items(self, limit: int | None = None, offset: int = 0) -> list[dict[str, Any]]:
        items = []
        for idx, ex in enumerate(_read_jsonl(DATA / "gsm8k_socratic.jsonl")):
            text = (
                "You are a helpful math tutor generating step-by-step questions. Generate only a list of "
                "questions on one line.\n"
                f"{_SHOTS_SOCRATIC}\n\n"
                f"Problem: {ex['question']}\n"
                "Questions:"
            )
            items.append(
                {
                    "item_id": f"soc-{idx}",
                    "text": text,
                    "image_paths": [],
                    "gold": ex["answer"],
                    "meta": {},
                }
            )
        return items[offset : offset + limit if limit is not None else None]

    def extract_answer(self, item, response, client, model):
        # Official runs this as a completion with stop=["Problem:", "\n"], so the
        # model emits a single line of questions. The chat harness sends no stop,
        # so a verbose/reasoning model would spill many lines and inflate the
        # best-match BLEU. Mimic the official cutoff by taking the first non-empty
        # line of the answer (reasoning models keep the answer in `content`, so
        # its first line is the questions list). No LLM call.
        first = ""
        for line in (response or "").split("\n"):
            if line.strip():
                first = line.strip()
                break
        # chat models sometimes echo the "Questions:" label the completion prompt omits
        if first.lower().startswith("questions:"):
            first = first.split(":", 1)[1].strip()
        return first

    def score(self, extracted, item):
        try:
            import sacrebleu
        except ImportError as exc:  # pragma: no cover - actionable hint
            raise SystemExit(
                "mathtutorbench_socratic needs the `sacrebleu` package (the official metric). "
                "Install it: pip install sacrebleu"
            ) from exc
        refs = self._gt_questions(item["gold"])
        preds = [ln.strip() for ln in (extracted or "").split("\n") if ln.strip()]
        if not refs or not preds:
            return {"correct": False, "normalized": 0.0, "gold": len(refs), "bleu": 0.0}
        best = max(sacrebleu.sentence_bleu(p, refs).score for p in preds)
        bleu = best / 100.0
        return {"correct": bleu >= 0.5, "normalized": round(bleu, 4), "gold": len(refs), "bleu": bleu}

    def extra_summary(self, scored):
        rows = [r for r in scored if r.get("score_status") == "scored"]
        if not rows:
            return {}
        bleus = [float(r.get("bleu") or 0.0) for r in rows]
        return {
            "official_metric": "mean best-match SacreBLEU (0-1)",
            "n": len(rows),
            "avg_bleu": round(sum(bleus) / len(bleus), 4),
            "note": "report accuracy is a coarse BLEU>=0.5 proxy; avg_bleu is the official headline metric",
        }


# ---------------------------------------------------------------------------
# Open-ended pedagogical tasks — LLM-as-judge pairwise win-rate
# ---------------------------------------------------------------------------

DEFAULT_JUDGE_MODEL = "MiniMax-M3"
JUDGE_MODEL_ENV = "MATHTUTORBENCH_JUDGE_MODEL"


def _format_bridge(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Port of dataloaders/mathbridge.py: drop the final teacher turn; that turn
    is the ground-truth response the model must match/beat."""
    out = []
    for ex in rows:
        conv = ex.get("dialog_history") or []
        cutoff = len(conv) - 1
        formatted = [
            f"{'Student' if t.get('user') == 'Student' else 'Teacher'}: {t['text']}" for t in conv
        ]
        if len(formatted) > 1:
            formatted = formatted[:-1]
        if cutoff < 0:
            continue
        out.append(
            {
                "problem": ex["problem"],
                "dialog_history": "\n".join(formatted),
                "ground_truth_response": conv[cutoff].get("text", ""),
                "reference_solution": ex.get("reference_solution", ""),
                "topic": ex.get("topic", "Math Word Problem"),
            }
        )
    return out


class _WinRateBase(BenchmarkAdapter):
    """Shared LLM-as-judge pairwise win-rate logic for scaffolding / pedagogy.

    Subclasses set ``name``, ``title``, ``description``, ``SOURCE`` (bridge json
    filename) and ``TUTOR_PROMPT`` (the system prompt sent to the model).
    """

    SOURCE = ""
    TUTOR_PROMPT = ""
    JUDGE_SWAP = True  # run both A/B orderings to debias position
    homepage = HOMEPAGE

    def load_items(self, limit: int | None = None, offset: int = 0) -> list[dict[str, Any]]:
        items = []
        for idx, ex in enumerate(_format_bridge(_read_json(BRIDGE_DIR / self.SOURCE))):
            text = (
                f"{self.TUTOR_PROMPT}\n"
                f"Problem: {ex['problem']}\n"
                "Conversation:\n"
                f"{ex['dialog_history']}\n"
                "Teacher (maximum two sentences): "
            )
            items.append(
                {
                    "item_id": f"{self.name.split('_')[-1]}-{idx}",
                    "text": text,
                    "image_paths": [],
                    "gold": "win",
                    "meta": {
                        "problem": ex["problem"],
                        "dialog_history": ex["dialog_history"],
                        "reference_solution": ex["reference_solution"],
                        "ground_truth_response": ex["ground_truth_response"],
                        "topic": ex["topic"],
                    },
                }
            )
        return items[offset : offset + limit if limit is not None else None]

    # --- judge resolution (fixed, decoupled from the model under test) ---------

    def _resolve_judge(self, extractor_client: MiniMaxClient, extractor_model: str):
        judge_model = os.environ.get(JUDGE_MODEL_ENV) or DEFAULT_JUDGE_MODEL
        if judge_model == extractor_model:
            return extractor_client, judge_model
        cached = getattr(self, "_judge_client", None)
        if cached is None or self._judge_client_model != judge_model:
            from ..providers import build_client

            self._judge_client = build_client(judge_model)
            self._judge_client_model = judge_model
        return self._judge_client, judge_model

    @staticmethod
    def _pairwise_prompt(meta: dict[str, Any], resp_a: str, resp_b: str) -> str:
        return (
            f"{REWARD_RUBRIC}\n\n"
            f"Problem: {meta['problem']}\n"
            f"Reference Solution: {meta['reference_solution']}\n"
            "Conversation so far:\n"
            f"{meta['dialog_history']}\n\n"
            "Two candidate teacher responses for the next turn:\n"
            f"[Response A]\n{resp_a}\n\n"
            f"[Response B]\n{resp_b}\n\n"
            "Which response is pedagogically better according to the criteria above? "
            "Answer with a single letter only: 'A' or 'B'."
        )

    @staticmethod
    def _vote_letter(client: MiniMaxClient, model: str, prompt: str) -> str | None:
        for attempt in range(3):
            try:
                reply = client.chat(
                    [{"role": "user", "content": prompt}],
                    model=model,
                    max_tokens=extraction_max_tokens(model, 512),
                )
                letters = re.findall(r"\b([AB])\b", (reply or "").upper())
                if letters:
                    return letters[0]
            except Exception:  # noqa: BLE001 - retry transient judge failures
                pass
            time.sleep(1.5 * (attempt + 1))
        return None

    def extract_answer(self, item, response, client, model):
        client, model = self._resolve_judge(client, model)
        meta = item["meta"]
        gen = (response or "").strip()
        gt = meta["ground_truth_response"]
        votes: list[str] = []
        gen_wins = 0.0
        rounds = 0
        # Order 1: A=generated, B=ground truth
        v1 = self._vote_letter(client, model, self._pairwise_prompt(meta, gen, gt))
        if v1 is not None:
            votes.append(f"AgenBgt:{v1}")
            gen_wins += 1.0 if v1 == "A" else 0.0
            rounds += 1
        if self.JUDGE_SWAP:
            # Order 2: A=ground truth, B=generated
            v2 = self._vote_letter(client, model, self._pairwise_prompt(meta, gt, gen))
            if v2 is not None:
                votes.append(f"AgtBgen:{v2}")
                gen_wins += 1.0 if v2 == "B" else 0.0
                rounds += 1
        win_score = (gen_wins / rounds) if rounds else None
        return json.dumps(
            {"win_score": win_score, "votes": votes, "judge_model": model}, ensure_ascii=False
        )

    def score(self, extracted, item):
        try:
            j = json.loads(extracted)
        except (json.JSONDecodeError, TypeError):
            j = {}
        ws = j.get("win_score")
        return {
            "correct": ws is not None and ws > 0.5,
            "normalized": ws if ws is not None else "judge_error",
            "gold": "win",
            "win_score": ws,
            "judge_model": j.get("judge_model"),
        }

    def buckets(self, item):
        return {"topic": item["meta"]["topic"]}

    def judge_prompt_provenance(self):
        return _pairwise_judge_provenance()

    def extra_summary(self, scored):
        rows = [r for r in scored if r.get("score_status") == "scored" and r.get("win_score") is not None]
        judge_model = os.environ.get(JUDGE_MODEL_ENV) or DEFAULT_JUDGE_MODEL
        if not rows:
            return {"judge_model": judge_model, "n_judged": 0}
        scores = [float(r["win_score"]) for r in rows]
        strict = sum(1 for s in scores if s > 0.5)
        return {
            "judge_model": judge_model,
            "judge_protocol": "LLM-as-judge pairwise vs ground truth, position-swapped (2 orderings)",
            "official_analog": "reward-model win-rate of generated over ground-truth teacher utterance",
            "n_judged": len(rows),
            "win_rate": round(sum(scores) / len(scores), 4),
            "strict_win_rate": round(strict / len(rows), 4),
        }


class MTBScaffolding(_WinRateBase):
    name = "mathtutorbench_scaffolding"
    title = "MathTutorBench · Scaffolding Generation (LLM-judge win-rate)"
    SOURCE = "mathdial_bridge.json"
    TUTOR_PROMPT = (
        "You are an experienced math teacher and you are going to respond to a student in a useful and "
        "caring way. The student is trying to solve the following problem."
    )
    description = (
        "脚手架式回应生成：模型为对话生成下一句教师回应，由 LLM 裁判按官方 reward-model 评分准则"
        "与金标教师回应做成对比较（位置交换去偏），win-rate 即模型回应优于金标的比例——替代官方需"
        " GPU 的 1.5B 偏好奖励模型。裁判模型默认 MiniMax-M3（MATHTUTORBENCH_JUDGE_MODEL 可覆盖）。"
        "对应 D11/D13（反馈质量）。"
    )


class MTBPedagogy(_WinRateBase):
    name = "mathtutorbench_pedagogy"
    title = "MathTutorBench · Pedagogy Following (LLM-judge win-rate)"
    SOURCE = "mathdial_bridge.json"
    TUTOR_PROMPT = (
        "Be a friendly, supportive tutor. Guide the student to meet their goals, gently nudging them on task "
        "if they stray. Ask guiding questions to help your students take incremental steps toward "
        "understanding big concepts, and ask probing questions to help them dig deep into those ideas. Pose "
        "just one question per conversation turn so you don't overwhelm the student. Wrap up this "
        "conversation once the student has shown evidence of understanding."
    )
    description = (
        "教学法遵循：在 LearnLM 风格的教学指令下生成下一句教师回应，LLM 裁判与金标做成对比较"
        "（位置交换），win-rate 衡量教学指令遵循质量。替代官方 1.5B 奖励模型。裁判默认 MiniMax-M3。"
        "对应 D11/D13。"
    )


class MTBScaffoldingHard(MTBScaffolding):
    name = "mathtutorbench_scaffolding_hard"
    title = "MathTutorBench · Scaffolding Generation Hard (LLM-judge win-rate)"
    SOURCE = "mathdial_bridge_hard.json"
    description = (
        "Scaffolding Generation 的 hard 子集（更难的对话），评分同 mathtutorbench_scaffolding。"
    )


class MTBPedagogyHard(MTBPedagogy):
    name = "mathtutorbench_pedagogy_hard"
    title = "MathTutorBench · Pedagogy Following Hard (LLM-judge win-rate)"
    SOURCE = "mathdial_bridge_hard.json"
    description = (
        "Pedagogy Following 的 hard 子集，评分同 mathtutorbench_pedagogy。"
    )


# ---------------------------------------------------------------------------
# Judge selection / calibration — the model under test IS the candidate judge
# ---------------------------------------------------------------------------


class MTBJudgeCalibration(BenchmarkAdapter):
    name = "mathtutorbench_judge_calibration"
    title = "MathTutorBench · Judge Calibration (选 LLM 裁判)"
    homepage = HOMEPAGE
    description = (
        "裁判选择评测：用论文开源的偏好数据集 dmacjam/pedagogical-rewardmodel-data 的 test 划分"
        "（482 对专家标注的 positive/negative 教师回应）来衡量各候选 LLM 裁判与人类偏好的一致率。"
        "被测模型本身即裁判（--model 指定候选裁判），无需额外裁判设施。每对题以两种顺序各出一题"
        "（#ab / #ba）以暴露位置偏置；正确=裁判选中 positive 所在位置。报告 accuracy（一致率，可与"
        "奖励模型 win-rate 对比）与位置一致率（extra_metrics）。一致率最高者用作 win-rate 任务的"
        "生产裁判（MATHTUTORBENCH_JUDGE_MODEL）。"
    )

    def load_items(self, limit: int | None = None, offset: int = 0) -> list[dict[str, Any]]:
        items = []
        for idx, ex in enumerate(_read_jsonl(DATA / "pref_test.jsonl")):
            pos = ex.get("teacher_response_positive", "")
            neg = ex.get("teacher_response_negative", "")
            conv = ex.get("dialog_history") or []
            dialog = "\n".join(
                f"{'Student' if t.get('user') == 'Student' else 'Teacher'}: {t.get('text', '')}" for t in conv
            )
            meta_common = {
                "problem": ex.get("problem", ""),
                "reference_solution": ex.get("reference_solution", ""),
                "dialog_history": dialog,
            }
            # #ab: A=positive, B=negative ; #ba: A=negative, B=positive
            for tag, a, b, positive_letter in (("ab", pos, neg, "A"), ("ba", neg, pos, "B")):
                items.append(
                    {
                        "item_id": f"cal-{idx}#{tag}",
                        "text": self._pairwise_prompt(meta_common, a, b),
                        "image_paths": [],
                        "gold": positive_letter,
                        "meta": {"pair_id": f"cal-{idx}", "order": tag, "positive_letter": positive_letter},
                    }
                )
        return items[offset : offset + limit if limit is not None else None]

    @staticmethod
    def _pairwise_prompt(meta: dict[str, Any], resp_a: str, resp_b: str) -> str:
        return _WinRateBase._pairwise_prompt(meta, resp_a, resp_b)

    @staticmethod
    def _parse_letter(text: str) -> str:
        letters = re.findall(r"\b([AB])\b", (text or "").upper())
        return letters[0] if letters else ""

    def extract_answer(self, item, response, client, model):
        response = (response or "").strip()
        letter = self._parse_letter(response)
        if not letter and response and len(response) > VERBOSE_LEN:
            response = _llm_extract(
                client, model,
                "The text below chooses between Response A and Response B. Output only the chosen letter: A or B.",
                response,
            )
            letter = self._parse_letter(response)
        return letter

    def score(self, extracted, item):
        pred = self._parse_letter(extracted)
        gold = item["gold"]
        return {
            "correct": pred == gold,
            "normalized": pred or "no_choice",
            "gold": gold,
            "pair_id": item["meta"]["pair_id"],
            "order": item["meta"]["order"],
            "chose_positive": pred == gold,
        }

    def buckets(self, item):
        return {"order": item["meta"]["order"]}

    def judge_prompt_provenance(self):
        return _pairwise_judge_provenance()

    def extra_summary(self, scored):
        rows = [r for r in scored if r.get("score_status") == "scored"]
        if not rows:
            return {}
        n = len(rows)
        agree = sum(1 for r in rows if r.get("chose_positive"))
        # position consistency: per pair, did #ab and #ba agree on the same response?
        by_pair: dict[str, dict[str, str]] = {}
        for r in rows:
            by_pair.setdefault(r["pair_id"], {})[r["order"]] = r.get("normalized") or ""
        # In #ab, choosing "A" means positive; in #ba, choosing "B" means positive.
        consistent = 0
        complete = 0
        for choices in by_pair.values():
            if "ab" in choices and "ba" in choices and choices["ab"] in ("A", "B") and choices["ba"] in ("A", "B"):
                complete += 1
                ab_positive = choices["ab"] == "A"
                ba_positive = choices["ba"] == "B"
                if ab_positive == ba_positive:
                    consistent += 1
        return {
            "metric": "agreement with expert positive (accuracy); higher = better judge",
            "n_items": n,
            "agreement": round(agree / n, 4),
            "n_pairs_complete": complete,
            "position_consistency": round(consistent / complete, 4) if complete else None,
        }
