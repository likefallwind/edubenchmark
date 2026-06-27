"""C-Eval adapter (D01: Chinese multi-discipline exam knowledge, MCQ).

Source: ``sources/datasets/ceval/data/{val,dev}.jsonl`` produced by
``scripts/eval/data/fetch_eval_datasets.py`` from the HuggingFace repo
``ceval/ceval-exam``. C-Eval is a Chinese multiple-choice exam spanning 52
subjects (STEM / Social Science / Humanities / Other) with four options
(A/B/C/D). We score the labeled ``val`` split (1,346 items) because the
official ``test`` split withholds its answers for the leaderboard.

This adapter follows the **official 5-shot answer-only** protocol (ported from
the repo's ``code/evaluator_series/evaluators/chatgpt.py`` /
``minimax.py``): each subject's 5 ``dev`` exemplars are supplied as
user/assistant turns whose assistant reply is the bare gold letter, then the
test question is asked the same way (ending in ``答案：``). The few-shot
conditioning makes the model emit a single letter, so there is **no LLM-based
answer extraction** — scoring reads the leading option letter and exact-matches
the gold, exactly like the official ``response[0] == answer`` check. Results are
bucketed by category and subject.

One model-specific adaptation: reasoning models such as MiniMax-M3 tend to emit
an empty thinking block and stop (empty content) under pure answer-only few-shot,
so the final question turn carries a single-letter output constraint
(``ANSWER_HINT``). This stays answer-only (no CoT / no extraction) and is
harmless to non-reasoning models; see the constant's note.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from ..base import ROOT, BenchmarkAdapter
from ..minimax_client import MiniMaxClient


DATA_DIR = ROOT / "sources" / "datasets" / "ceval" / "data"
VAL_FILE = DATA_DIR / "val.jsonl"
DEV_FILE = DATA_DIR / "dev.jsonl"
LETTERS = ["A", "B", "C", "D"]
N_SHOT = 5
# Reasoning models (e.g. MiniMax-M3) tend to emit an empty thinking block and
# stop when the few-shot exemplars reply with a bare letter, returning empty
# content ~80% of the time. A single-letter output constraint on the final turn
# fixes this (an instruction in the system message does not) while staying
# answer-only — no CoT, no LLM extraction. Harmless to non-reasoning models.
ANSWER_HINT = "（请只输出一个选项字母 A、B、C 或 D，不要输出任何其他内容。）"


class CEvalAdapter(BenchmarkAdapter):
    name = "ceval"
    title = "C-Eval：中文多学科考试知识（选择题，5-shot answer-only）"
    homepage = "https://github.com/hkust-nlp/ceval"
    description = (
        "C-Eval 是覆盖 52 个学科、四个难度层级的中文多项选择评测，分为 STEM、社会科学、"
        "人文、其他四大类。每题为四选一（A/B/C/D）。对应本仓库能力维度 D01"
        "（通用学科知识与推理），用于衡量模型的中文本土学科知识，属 sanity check。\n\n"
        "本次使用带公开标签的 val 划分（1,346 题）；官方 test 划分不公开答案、需提交"
        "排行榜，故不在本地评测范围内。评测采用官方 **5-shot answer-only** 协议：每个学科"
        "取 dev 集的 5 个示例作为 user/assistant 多轮对话（assistant 回复即标准字母），再以"
        "相同格式（结尾为「答案：」）提问。\n\n"
        "由于 few-shot 已把输出约束为单个字母，本适配器**不做 LLM 答案抽取**，直接读取回复"
        "首个选项字母与标准答案精确匹配（等价官方 `response[0] == answer`），并按学科大类与"
        "具体学科分桶统计。"
    )

    def __init__(self) -> None:
        self._fewshot: dict[str, list[dict[str, Any]]] = {}

    # --- data loading -----------------------------------------------------------

    @staticmethod
    def _read_jsonl(path: Path) -> list[dict[str, Any]]:
        rows = []
        with path.open(encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    rows.append(json.loads(line))
        return rows

    def _load_fewshot(self) -> None:
        """Group dev exemplars by subject, keeping the first N_SHOT each."""
        if self._fewshot:
            return
        for row in self._read_jsonl(DEV_FILE):
            self._fewshot.setdefault(row["subject"], []).append(row)
        for subject, rows in self._fewshot.items():
            self._fewshot[subject] = rows[:N_SHOT]

    def load_items(self, limit: int | None = None, offset: int = 0) -> list[dict[str, Any]]:
        self._load_fewshot()
        rows = self._read_jsonl(VAL_FILE)
        rows = rows[offset : offset + limit if limit is not None else None]
        items = []
        for row in rows:
            options = {letter: row.get(letter, "") for letter in LETTERS}
            items.append(
                {
                    "item_id": str(row.get("item_id")),
                    "text": self._format_question(row.get("question", ""), options),
                    "image_paths": [],
                    "gold": row.get("answer"),
                    "meta": {
                        "options": options,
                        "subject": row.get("subject"),
                        "subject_zh": row.get("subject_zh"),
                        "category": row.get("category"),
                    },
                }
            )
        return items

    @staticmethod
    def _format_question(question: str, options: dict[str, str]) -> str:
        example = question
        for letter in LETTERS:
            example += f"\n{letter}. {options.get(letter, '')}"
        example += "\n答案："
        return example

    # --- few-shot prompt construction (ported from official chatgpt.py) ---------

    def build_messages(self, item: dict[str, Any]) -> list[dict[str, Any]]:
        subject_zh = item["meta"].get("subject_zh") or ""
        subject = item["meta"].get("subject") or ""
        instruction = f"以下是中国关于{subject_zh}考试的单项选择题，请选出其中的正确答案。"
        messages: list[dict[str, Any]] = [
            {"role": "system", "content": f"你是一个中文人工智能助手，{instruction}"}
        ]
        shots = self._fewshot.get(subject, [])
        for i, shot in enumerate(shots):
            options = {letter: shot.get(letter, "") for letter in LETTERS}
            user = self._format_question(shot.get("question", ""), options)
            if i == 0:
                user = f"{instruction}\n\n{user}"
            messages.append({"role": "user", "content": user})
            messages.append({"role": "assistant", "content": str(shot.get("answer", "")).strip()})
        messages.append({"role": "user", "content": f"{item['text']}{ANSWER_HINT}"})
        return messages

    # --- answer reading (no LLM call: few-shot output is a bare letter) ----------

    def extract_answer(self, item: dict[str, Any], response: str, client: MiniMaxClient, model: str) -> str:
        response = (response or "").strip()
        if not response:
            return ""
        # Official answer-only check uses response[0]; honor that for clean output,
        # and fall back to the last A-D letter if the model prepended any text.
        if response[0] in LETTERS:
            return response[0]
        candidates = re.findall(r"[ABCD]", response)
        return candidates[-1] if candidates else ""

    def score(self, extracted: str, item: dict[str, Any]) -> dict[str, Any]:
        normalized = (extracted or "").strip().upper()[:1]
        gold = item.get("gold")
        correct = bool(normalized) and normalized == str(gold).strip().upper()
        return {"correct": correct, "normalized": normalized, "gold": gold}

    def buckets(self, item: dict[str, Any]) -> dict[str, str]:
        return {
            "category": str(item["meta"].get("category")),
            "subject": str(item["meta"].get("subject")),
        }
