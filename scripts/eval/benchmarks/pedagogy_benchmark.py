"""Pedagogy Benchmark adapter (D11/D14: pedagogical knowledge, MCQ).

Source: ``sources/datasets/pedagogy_benchmark/data/questions.jsonl`` produced by
``scripts/eval/data/fetch_eval_datasets.py`` from the **gated** HuggingFace repo
``AI-for-Education/pedagogy-benchmark``. 1,143 English multiple-choice questions
drawn from Chilean Ministry of Education teacher qualification exams (translated
from Spanish), split into two benchmarks:

- **CDPK** (920 items): cross-domain pedagogical knowledge across creative arts,
  general PK, literacy, maths, science, social studies, technology.
- **SEND** (223 items): special educational needs and disabilities.

Prompting and answer parsing are **ported from the official repo**
(``AI-for-Education/pedagogy-benchmark``, ``src/cdpk/benchmark_answers.py``),
which ships two prompt variants:

- ``gen_prompt`` — 3-shot, for ordinary models.
- ``gen_prompt_reasoning_models`` — zero-shot, for reasoning models.

``PROMPT_VARIANT`` (env) forces one of ``auto`` / ``fewshot`` / ``zeroshot``;
``auto`` (default) picks zero-shot for reasoning models and 3-shot otherwise,
mirroring the official split, and records the choice in ``summary.json``.

**The scored set is 1,119, not 1,143.** Every official question config declares
``example_rows: [0, 1, 2]``, and the HF release merges the upstream dev and test
CSVs into a single category-grouped file. So the first three rows of each of the
8 categories are the few-shot exemplars: 1,143 - 8x3 = 1,119 scored items, which
matches the official scored set. Scoring the exemplars would leak under the
3-shot variant (the model is shown the item with its answer, then asked that same
item). ``load_items`` drops rows the fetcher tagged ``is_exemplar``;
``INCLUDE_EXEMPLARS=1`` overrides that and is refused under the 3-shot variant.

Options may run A..G per the official ``choices`` list, though every item in the
current HF release has exactly four. Answer parsing uses the official ``REPAT``
regexes verbatim,
including their per-model tolerances (DeepSeek-R1 think blocks, Llama 4 step
headers, Claude 4 trailing letters), so there is **no LLM answer extraction**.
Responses that match none of them are counted as ``bad_format`` — the official
run excludes any model whose bad-format rate exceeds 5%, which we surface as a
summary flag rather than enforcing.

Note the paper states all 1,143 questions are text-only; there are no images.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

from ..base import ROOT, BenchmarkAdapter, prompt_sha256
from ..minimax_client import MiniMaxClient


DATA_DIR = ROOT / "sources" / "datasets" / "pedagogy_benchmark" / "data"
QUESTIONS_FILE = DATA_DIR / "questions.jsonl"
EXAMPLES_FILE = DATA_DIR / "examples.jsonl"

LETTERS = list("ABCDEFG")
N_SHOT = 3
PROMPT_VERSION = "official-v1"

# Verbatim from the official src/cdpk/benchmark_answers.py REPAT, including the
# per-model tolerances. Order matters: the first match wins.
REPAT = [
    r"^\s*([ABCDEFG])(?:[\.(?:\s*\n)]+.*)*$",
    r"^<think>[\s\S]*?</think>[\s\S]*?([ABCDEFG])$",  # for deepseek R1
    r"^## Step 1[\s\S]*?([ABCDEFG])[\.\s]*$",  # for llama 4
    r'[\s\S]*\n([A-G])"?$',  # for claude 4
]
REQ = [re.compile(pattern) for pattern in REPAT]

# Official gen_prompt / gen_prompt_reasoning_models tails.
FEWSHOT_HEADER = "The following are example multiple choice questions (with answers).\n\n"
FEWSHOT_LEAD = "Answer the following real question using same answer format: \n"
FEWSHOT_TAIL = (
    "\n\nOnly answer the real question."
    "\n\nOnly provide the letter for your answer."
    "\n\nStop exactly after the letter."
)
ZEROSHOT_LEAD = "Answer the following question using the answer format specified below: \n"
ZEROSHOT_TAIL = "\n\nOnly provide the letter for your answer.\n\nStop exactly after the letter."

# Models routed to the official zero-shot variant under PROMPT_VARIANT=auto.
# Substring match, lowercased. Reasoning models emit a thinking block before the
# letter, which is exactly what the official reasoning-model branch expects.
REASONING_MODEL_HINTS = (
    "minimax-m",
    "deepseek-r",
    "deepseek-v4",
    "glm-5",
    "gpt-5",
    "o1",
    "o3",
    "qwen3",
    "kimi-k",
    "doubao-seed",
    "claude-opus-4",
    "claude-sonnet-4",
    # Generic marker for explicit reasoning variants, e.g. deepseek-v3.2-think.
    # Also catches "-thinking", which is the same thing.
    "-think",
)


def _is_reasoning_model(model: str | None) -> bool:
    name = (model or "").lower()
    return any(hint in name for hint in REASONING_MODEL_HINTS)


class PedagogyBenchmarkAdapter(BenchmarkAdapter):
    name = "pedagogy_benchmark"
    title = "Pedagogy Benchmark：教师资格考试的教学法知识（选择题）"
    homepage = "https://github.com/AI-for-Education/pedagogy-benchmark"
    description = (
        "Pedagogy Benchmark 取自智利教育部教师专业发展考试的多项选择题（西班牙语原题译为英文），"
        "共 1,143 题，分为 CDPK（跨学科教学法知识，920 题）与 SEND（特殊教育需要与障碍，223 题）"
        "两个子基准，覆盖教学策略、评估方法、学生理解、教育理论、课堂管理等教学法子领域。"
        "与考察学科内容知识的通用基准不同，它直接测量「怎么教」而非「教什么」。\n\n"
        "提示词与答案解析均移植自官方仓库 src/cdpk/benchmark_answers.py：官方提供 3-shot"
        "（gen_prompt）与零样本（gen_prompt_reasoning_models，面向推理模型）两个变体，本适配器"
        "默认按模型自动选择并在 summary 中记录实际使用的变体。3-shot 所需的示例题来自上游仓库"
        "DVC 管理的 data/Chile/ 目录，不在 HF 数据集内；缺失时本适配器直接报错，不会静默退化为零样本。\n\n"
        "选项范围为 A–G（少数题目多于四个选项）。答案解析直接使用官方 REPAT 正则（含对 DeepSeek-R1、"
        "Llama 4、Claude 4 的格式容差），**不调用 LLM 抽取**；无法解析的回复计为 bad_format。"
        "官方做法是剔除 bad_format 率超过 5% 的模型，本适配器只在 summary 中给出该标志，不自动剔除。"
    )

    def __init__(self) -> None:
        self._examples: dict[str, list[dict[str, Any]]] = {}
        self._variant: str | None = None

    # --- data loading -----------------------------------------------------------

    @staticmethod
    def _read_jsonl(path: Path) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        with path.open(encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    rows.append(json.loads(line))
        return rows

    def _resolve_variant(self) -> str:
        """Decide between the official 3-shot and zero-shot prompt variants."""
        if self._variant is not None:
            return self._variant
        requested = (os.environ.get("PROMPT_VARIANT") or "auto").strip().lower()
        if requested not in ("auto", "fewshot", "zeroshot"):
            raise SystemExit(
                f"PROMPT_VARIANT must be auto/fewshot/zeroshot, got {requested!r}"
            )
        if requested == "auto":
            requested = "zeroshot" if _is_reasoning_model(self.model_under_test) else "fewshot"
        if requested == "fewshot":
            self._load_examples()
        self._variant = requested
        return requested

    def _load_examples(self) -> None:
        if self._examples:
            return
        if not EXAMPLES_FILE.exists():
            raise SystemExit(
                f"missing {EXAMPLES_FILE}; re-run "
                "`python scripts/eval/data/fetch_eval_datasets.py --benchmark pedagogy_benchmark --force` "
                "to regenerate the official 3-shot exemplars (first 3 rows of each category)"
            )
        for row in self._read_jsonl(EXAMPLES_FILE):
            self._examples.setdefault(str(row.get("category")), []).append(row)
        for rows in self._examples.values():
            rows.sort(key=lambda r: r.get("category_index", 0))

    def load_items(self, limit: int | None = None, offset: int = 0) -> list[dict[str, Any]]:
        if not QUESTIONS_FILE.exists():
            raise SystemExit(
                f"missing {QUESTIONS_FILE}; run "
                "`python scripts/eval/data/fetch_eval_datasets.py --benchmark pedagogy_benchmark` "
                "(the dataset is gated: accept the terms and export HF_TOKEN first)"
            )
        rows = self._read_jsonl(QUESTIONS_FILE)

        # Official example_rows [0,1,2] per category are prompt exemplars, not
        # scored items: 1,143 - 8x3 = 1,119. Including them under the 3-shot
        # variant would show the model the answer before asking the question.
        include_exemplars = os.environ.get("INCLUDE_EXEMPLARS", "").strip() in ("1", "true", "yes")
        if include_exemplars and self._resolve_variant() == "fewshot":
            raise SystemExit(
                "INCLUDE_EXEMPLARS=1 is refused under the 3-shot variant: those 24 items appear "
                "in the prompt with their answers, so scoring them measures copying, not knowledge. "
                "Use PROMPT_VARIANT=zeroshot if you want the full 1,143."
            )
        if not include_exemplars:
            rows = [row for row in rows if not row.get("is_exemplar")]

        rows = rows[offset:]
        if limit:
            rows = rows[:limit]
        items: list[dict[str, Any]] = []
        for row in rows:
            options = {k: v for k, v in (row.get("options") or {}).items() if v not in (None, "")}
            items.append(
                {
                    "item_id": row["item_id"],
                    "text": "",  # built per-call in build_messages (variant-dependent)
                    "image_paths": [],
                    "gold": str(row.get("correct_answer") or "").strip().upper(),
                    "meta": {
                        "task": row.get("task"),
                        "question": row.get("question"),
                        "options": options,
                        "category": row.get("category"),
                        "secondary_category": row.get("secondary_category"),
                        "pedagogical_subdomain": row.get("pedagogical_subdomain"),
                        "age_group": row.get("age_group"),
                        "education_level": row.get("education_level"),
                    },
                }
            )
        return items

    # --- prompting (ported from official gen_prompt / gen_prompt_reasoning_models) ---

    @staticmethod
    def _format_question(question: str, options: dict[str, Any]) -> str:
        """Official format_questions: question, then '\\n{letter}. {option}'."""
        text = str(question or "")
        for letter in LETTERS:
            if letter in options:
                text += "\n{}. {}".format(letter, options[letter])
        return text

    def _example_block(self, category: str | None) -> str:
        rows = self._examples.get(str(category)) or []
        if not rows:
            raise SystemExit(
                f"no few-shot exemplars for category {category!r} in {EXAMPLES_FILE}; "
                "re-fetch with --force, or set PROMPT_VARIANT=zeroshot"
            )
        block = ""
        for row in rows[:N_SHOT]:
            block += self._format_question(row.get("question"), row.get("options") or {})
            block += "\n{}\n\n".format(row.get("correct_answer"))
        return block

    def build_messages(self, item: dict[str, Any]) -> list[dict[str, Any]]:
        meta = item["meta"]
        question = self._format_question(meta["question"], meta["options"])
        if self._resolve_variant() == "zeroshot":
            prompt = ZEROSHOT_LEAD + question + ZEROSHOT_TAIL
        else:
            prompt = FEWSHOT_HEADER + self._example_block(meta.get("category"))
            prompt += FEWSHOT_LEAD + question + FEWSHOT_TAIL
        return [{"role": "user", "content": prompt}]

    # --- scoring (ported from official clean_resps) ------------------------------

    @staticmethod
    def _clean_resp(response: str) -> str | None:
        """Official clean_resps: first matching REPAT group, else None."""
        if response is None:
            return None
        for pattern in REQ:
            match = pattern.match(response)
            if match is not None:
                groups = match.groups()
                return groups[0] if groups else None
        return None

    def extract_answer(
        self, item: dict[str, Any], response: str, client: MiniMaxClient, model: str
    ) -> str:
        # Rule-based only, exactly like the official runner. A trailing strip is
        # the one liberty taken: providers vary on trailing whitespace, and the
        # official regexes anchor on end-of-string.
        return self._clean_resp((response or "").strip()) or ""

    def score(self, extracted: str, item: dict[str, Any]) -> dict[str, Any]:
        normalized = (extracted or "").strip().upper()
        gold = str(item["gold"]).strip().upper()
        return {
            "correct": bool(normalized) and normalized == gold,
            "normalized": normalized,
            "gold": gold,
            "bad_format": not normalized,
        }

    def buckets(self, item: dict[str, Any]) -> dict[str, str]:
        meta = item["meta"]
        return {
            "task": str(meta.get("task")),
            "category": str(meta.get("category")),
            "pedagogical_subdomain": str(meta.get("pedagogical_subdomain")),
        }

    def extra_summary(self, scored: list[dict[str, Any]]) -> dict[str, Any]:
        total = len(scored)
        bad = sum(1 for row in scored if row.get("bad_format"))
        bad_rate = bad / total if total else 0.0
        variant = self._variant or "unresolved"
        return {
            "metric_note": (
                "Accuracy over multiple-choice items, official rule-based parsing "
                "(src/cdpk/benchmark_answers.py REPAT). No LLM extraction."
            ),
            "prompt_variant": variant,
            "prompt_variant_source": (
                "official gen_prompt_reasoning_models (zero-shot)"
                if variant == "zeroshot"
                else "official gen_prompt (3-shot)"
            ),
            "bad_format_rate": bad_rate,
            "bad_format_count": bad,
            "official_exclusion_threshold": 0.05,
            "exceeds_official_bad_format_threshold": bad_rate > 0.05,
            "audit": {
                "metric_protocol": "in-repo port of AI-for-Education/pedagogy-benchmark",
                "prompt_version": PROMPT_VERSION,
                "prompt_sha256": prompt_sha256(
                    FEWSHOT_HEADER + FEWSHOT_LEAD + FEWSHOT_TAIL,
                    ZEROSHOT_LEAD + ZEROSHOT_TAIL,
                ),
                "n_shot": N_SHOT if variant == "fewshot" else 0,
                "scored_rows": total,
            },
        }
