"""AGIEval adapter (D03: standardized / qualification-exam reasoning).

Source: ``sources/datasets/agieval/data/v1_1/*.jsonl`` (official repo checkout).
Covers human-exam tasks (Gaokao, SAT, LSAT, LogiQA, AQuA-RAT, JEC-QA, plus
competition MATH). Two task families:

  * multiple-choice (``*_qa``): gold is an option letter (or a letter set for the
    multi-answer tasks jec-qa-*, gaokao-physics).
  * math cloze (``math``, ``gaokao-mathcloze``): gold is a free-form answer scored
    by mathematical equivalence.

The choice-letter extraction mirrors the official ``src/post_process.py`` and the
math equivalence check dynamically loads the official ``src/math_equivalence.py``
(pure standard library) so scores stay comparable, while avoiding AGIEval's
``tiktoken``/``pandas`` import chain in ``dataset_loader.py``.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from ..base import ROOT, BenchmarkAdapter
from ..minimax_client import MiniMaxClient


DATA_DIR = ROOT / "sources" / "datasets" / "agieval" / "data" / "v1_1"
MATH_EQUIV_FILE = ROOT / "sources" / "datasets" / "agieval" / "src" / "math_equivalence.py"

# Task families, mirrored from agieval/src/dataset_loader.py.
ENGLISH_QA = [
    "lsat-ar", "lsat-lr", "lsat-rc", "logiqa-en", "sat-math", "sat-en",
    "aqua-rat", "sat-en-without-passage", "gaokao-english",
]
CHINESE_QA = [
    "logiqa-zh", "jec-qa-kd", "jec-qa-ca", "gaokao-chinese", "gaokao-geography",
    "gaokao-history", "gaokao-biology", "gaokao-chemistry", "gaokao-physics",
    "gaokao-mathqa",
]
ENGLISH_CLOZE = ["math"]
CHINESE_CLOZE = ["gaokao-mathcloze"]
MULTI_CHOICE = {"jec-qa-kd", "jec-qa-ca", "gaokao-physics"}
MATH_TASKS = set(ENGLISH_CLOZE) | set(CHINESE_CLOZE)
ALL_TASKS = ENGLISH_QA + CHINESE_QA + ENGLISH_CLOZE + CHINESE_CLOZE


def _load_is_equiv():
    """Load the official ``is_equiv`` from math_equivalence.py (stdlib only)."""
    namespace: dict[str, Any] = {}
    exec(compile(MATH_EQUIV_FILE.read_text(encoding="utf-8"), str(MATH_EQUIV_FILE), "exec"), namespace)
    return namespace["is_equiv"]


def _last_boxed(text: str) -> str:
    """Extract the content of the last ``\\boxed{...}`` with brace matching."""
    idx = text.rfind("\\boxed")
    if idx < 0:
        idx = text.rfind("\\fbox")
    if idx < 0:
        return ""
    i = text.find("{", idx)
    if i < 0:
        return ""
    depth = 0
    for j in range(i, len(text)):
        if text[j] == "{":
            depth += 1
        elif text[j] == "}":
            depth -= 1
            if depth == 0:
                inner = text[i + 1 : j]
                return inner.split("=")[-1].strip() if "=" in inner else inner.strip()
    return ""


def _letters(text: str) -> list[str]:
    return re.findall(r"[A-G]", text.upper())


class AGIEvalAdapter(BenchmarkAdapter):
    name = "agieval"
    title = "AGIEval：标准化与资格考试推理"
    homepage = "https://github.com/ruixiangcui/AGIEval"
    description = (
        "AGIEval 取材于人类标准化/资格考试（高考、SAT、LSAT、GRE、法考、公务员考试、"
        "竞赛 MATH 等），评测模型在真实考试情境下的推理能力。对应本仓库能力维度 D03"
        "（标准化与资格考试推理）。\n\n"
        "本次覆盖 21 个任务，分为选择题（gold 为选项字母；jec-qa、gaokao-physics 为多选）"
        "与数学填空（gold 为自由作答）。提示采用零样本思维链，要求模型先推理、再显式给出"
        "最终答案。\n\n"
        "选择题抽取沿用官方 post_process 取字母逻辑，数学题动态加载官方 math_equivalence"
        "做等价判定；按任务、语言、题型分桶统计。"
    )

    def __init__(self, tasks: list[str] | None = None) -> None:
        self.tasks = tasks or ALL_TASKS
        self._is_equiv = None

    @property
    def is_equiv(self):
        if self._is_equiv is None:
            self._is_equiv = _load_is_equiv()
        return self._is_equiv

    def load_items(self, limit: int | None = None, offset: int = 0) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        for task in self.tasks:
            path = DATA_DIR / f"{task}.jsonl"
            if not path.exists():
                continue
            language = "en" if task in ENGLISH_QA or task in ENGLISH_CLOZE else "zh"
            is_math = task in MATH_TASKS
            with path.open(encoding="utf-8") as fh:
                for n, line in enumerate(fh):
                    line = line.strip()
                    if not line:
                        continue
                    row = json.loads(line)
                    passage = row.get("passage") or ""
                    options = row.get("options") or []
                    gold = row.get("answer") if is_math else row.get("label")
                    items.append(
                        {
                            "item_id": f"{task}-{n}",
                            "text": self._format_prompt(passage, row.get("question", ""), options, language, is_math),
                            "image_paths": [],
                            "gold": gold,
                            "meta": {
                                "task": task,
                                "language": language,
                                "question_type": "cloze" if is_math else "qa",
                                "is_multi": task in MULTI_CHOICE,
                                "options": options,
                            },
                        }
                    )
        return items[offset : offset + limit if limit is not None else None]

    @staticmethod
    def _format_prompt(passage: str, question: str, options: list[str], language: str, is_math: bool) -> str:
        head = (passage + "\n") if passage else ""
        if is_math:
            if language == "zh":
                return f"{head}问题：{question}\n请逐步推导，并在最后用 \\boxed{{}} 给出最终答案。"
            return f"{head}Question: {question}\nReason step by step, then give the final answer in \\boxed{{}}."
        opts = " ".join(options)
        if language == "zh":
            return (
                f"{head}问题：{question}\n选项：{opts}\n"
                "请逐步思考，并在最后一行给出“答案是X”（多选时给出所有正确选项字母）。"
            )
        return (
            f"{head}Question: {question}\nAnswer Choices: {opts}\n"
            "Think step by step, then end with a line \"The answer is X\" "
            "(give all correct option letters if multiple)."
        )

    def extract_answer(self, item: dict[str, Any], response: str, client: MiniMaxClient, model: str) -> str:
        response = (response or "").strip()
        if not response:
            return ""
        meta = item["meta"]
        if meta["question_type"] == "cloze":
            boxed = _last_boxed(response)
            if boxed:
                return boxed
            for marker in ("答案是", "The answer is therefore", "The answer is", "answer is", "答案为"):
                if marker in response:
                    tail = response.rsplit(marker, 1)[1].strip()
                    return tail.strip(" .。:：$").split("\n")[0].strip()
            return response.split("\n")[-1].strip()

        # multiple-choice: prefer the marker line, then any letters in it.
        last_line = next((ln for ln in reversed(response.split("\n")) if ln.strip()), "")
        pattern = r"答案是.*?([A-G])" if meta["language"] == "zh" else r"answer is\s*\(?([A-G])"
        marked = re.search(pattern, response, re.IGNORECASE)
        scope = last_line if _letters(last_line) else response
        letters = _letters(scope)
        if meta["is_multi"]:
            return "".join(sorted(set(letters)))
        if marked:
            return marked.group(1).upper()
        return letters[-1] if letters else ""

    def score(self, extracted: str, item: dict[str, Any]) -> dict[str, Any]:
        meta = item["meta"]
        gold = item.get("gold")
        if meta["question_type"] == "cloze":
            try:
                correct = bool(self.is_equiv(str(extracted), str(gold)))
            except Exception:
                correct = False
            return {"correct": correct, "normalized": extracted, "gold": gold}
        gold_set = set(_letters(str(gold or "")))
        pred_set = set(_letters(str(extracted or "")))
        correct = bool(pred_set) and pred_set == gold_set
        return {"correct": correct, "normalized": "".join(sorted(pred_set)), "gold": gold}

    def buckets(self, item: dict[str, Any]) -> dict[str, str]:
        meta = item["meta"]
        return {
            "task": str(meta.get("task")),
            "language": str(meta.get("language")),
            "question_type": str(meta.get("question_type")),
        }
