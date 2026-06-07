"""MMLU-Pro adapter (D01: general-subject knowledge + complex MCQ reasoning).

Source: ``sources/datasets/mmlu_pro/test.jsonl`` produced by
``scripts/eval/data/fetch_eval_datasets.py`` from the public mirror
``TIGER-Lab/MMLU-Pro`` (12,032 test items, up to 10 options per question,
14 categories).

Prompt is zero-shot chain-of-thought ending in ``The answer is (X)``. Answer
extraction ports the official MMLU-Pro regex (``answer is (X)`` -> ``answer: X``
-> last standalone capital), with an LLM fallback for messy responses. Scoring is
exact letter match against the gold option.
"""

from __future__ import annotations

import json
import re
import string
from typing import Any

from ..base import ROOT, BenchmarkAdapter
from ..minimax_client import MiniMaxClient


DATA_FILE = ROOT / "sources" / "datasets" / "mmlu_pro" / "test.jsonl"
LETTERS = string.ascii_uppercase  # A, B, C, ...


class MMLUProAdapter(BenchmarkAdapter):
    name = "mmlu_pro"
    title = "MMLU-Pro：通用学科知识与复杂选择题推理"
    homepage = "https://github.com/TIGER-AI-Lab/MMLU-Pro"
    description = (
        "MMLU-Pro 是 MMLU 的增强版，覆盖 14 个学科/专业领域，把选项从 4 个扩展到最多"
        "10 个，并替换掉过易、易猜的题目，更强调多步推理而非纯记忆。对应本仓库能力维度"
        "D01（通用学科知识与复杂推理）。\n\n"
        "本次使用官方 test 划分（12,032 题）。提示采用零样本思维链，要求模型先推理、"
        "再在最后一行给出 `The answer is (X)`。\n\n"
        "答案抽取沿用官方正则（依次匹配 `answer is (X)`、`answer: X`、末尾独立大写字母），"
        "失败时由 LLM 兜底抽取；判分为与标准选项字母精确匹配，并按学科分桶统计。"
    )

    def load_items(self, limit: int | None = None, offset: int = 0) -> list[dict[str, Any]]:
        rows = []
        with DATA_FILE.open(encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    rows.append(json.loads(line))
        rows = rows[offset : offset + limit if limit is not None else None]
        items = []
        for row in rows:
            options = list(row.get("options") or [])
            items.append(
                {
                    "item_id": str(row.get("question_id")),
                    "text": self._format_prompt(row.get("question", ""), options),
                    "image_paths": [],
                    "gold": row.get("answer"),
                    "meta": {
                        "options": options,
                        "category": row.get("category"),
                        "src": row.get("src"),
                    },
                }
            )
        return items

    @staticmethod
    def _format_prompt(question: str, options: list[str]) -> str:
        lines = [f"Question: {question}", "Options:"]
        for i, opt in enumerate(options):
            lines.append(f"{LETTERS[i]}. {opt}")
        lines.append(
            "\nThink step by step, then end your response with a line of the exact form "
            '"The answer is (X)" where X is the letter of the correct option.'
        )
        return "\n".join(lines)

    # --- answer extraction (ported from official MMLU-Pro evaluate script) -----

    @staticmethod
    def _regex_extract(text: str, n_options: int) -> str:
        valid = set(LETTERS[:n_options]) if n_options else set(LETTERS[:10])
        for pattern in (r"answer is \(?([A-J])\)?", r".*[aA]nswer:\s*\(?([A-J])\)?"):
            match = re.search(pattern, text)
            if match and match.group(1) in valid:
                return match.group(1)
        # last standalone capital letter among the valid range
        candidates = re.findall(r"\b([A-J])\b", text)
        for letter in reversed(candidates):
            if letter in valid:
                return letter
        return ""

    def extract_answer(self, item: dict[str, Any], response: str, client: MiniMaxClient, model: str) -> str:
        response = (response or "").strip()
        if not response:
            return ""
        n_options = len(item["meta"].get("options") or [])
        letter = self._regex_extract(response, n_options)
        if letter:
            return letter
        # LLM fallback: give the model the response and ask only for the letter.
        prompt = (
            "Extract the single multiple-choice answer letter the response settles on. "
            "Reply with just one capital letter (A-J), nothing else.\n\n"
            f"Response:\n{response}\n\nAnswer letter:"
        )
        extracted = client.chat([{"role": "user", "content": prompt}], model=model, max_tokens=1024)
        return self._regex_extract(extracted.strip(), n_options) or extracted.strip()[:1].upper()

    def score(self, extracted: str, item: dict[str, Any]) -> dict[str, Any]:
        normalized = (extracted or "").strip().upper()[:1]
        gold = item.get("gold")
        correct = bool(normalized) and normalized == str(gold).strip().upper()
        return {"correct": correct, "normalized": normalized, "gold": gold}

    def buckets(self, item: dict[str, Any]) -> dict[str, str]:
        return {"category": str(item["meta"].get("category"))}
