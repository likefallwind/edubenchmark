"""OlympiadBench adapter (D05: olympiad-level math & physics reasoning).

Source: ``sources/datasets/olympiadbench/data/OE_*.jsonl`` (+ ``images/``) produced
by ``scripts/eval/data/fetch_eval_datasets.py`` from ``Hothan/OlympiadBench``.
Only the open-ended (OE) configs are loaded — both text-only (TO) and multimodal
(MM); theorem-proving (TP) configs need human grading and are excluded.

The prompt is ported from the official ``inference/code/evaluators/evaluator.py``
(``make_prompt`` / ``get_answer_type_text``), which asks for the final answer in
``\\boxed{}``. Scoring uses the official symbolic judge
``eval/auto_scoring_judge.py`` (``AutoScoringJudge``, sympy + LaTeX parsing),
loaded directly so results match the paper's automated pipeline.
"""

from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path
from typing import Any

from ..base import ROOT, BenchmarkAdapter
from ..minimax_client import MiniMaxClient


DATA_DIR = ROOT / "sources" / "datasets" / "olympiadbench" / "data"
DATASET_DIR = ROOT / "sources" / "datasets" / "olympiadbench"
JUDGE_FILE = DATASET_DIR / "eval" / "auto_scoring_judge.py"

CN_ANSWER_TYPE = {"Numerical": "数值", "Expression": "表达式", "Equation": "方程", "Interval": "区间"}
EN_ANSWER_TYPE = {
    "Numerical": "a numerical value", "Expression": "an expression",
    "Equation": "an equation", "Interval": "an interval",
}


def _load_judge():
    spec = importlib.util.spec_from_file_location("olympiad_judge", JUDGE_FILE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.AutoScoringJudge


def _single_answer_type_text(answer_type: str, is_chinese: bool) -> str:
    if "-" in answer_type:
        answer_type = answer_type[: answer_type.find("-")]
    for t in ("Numerical", "Expression", "Equation", "Interval"):
        if t in answer_type:
            return CN_ANSWER_TYPE[t] if is_chinese else EN_ANSWER_TYPE[t]
    return ""


def _answer_type_text(answer_type: str, is_chinese: bool, multiple: bool) -> str:
    """Port of evaluator.get_answer_type_text (open-ended branch)."""
    if not answer_type or "Need_human_evaluate" in answer_type or "Tuple" in answer_type:
        return ""
    if not multiple:
        text = _single_answer_type_text(answer_type, is_chinese)
        return f"，答案类型为{text}" if is_chinese else f"The answer of The problem should be {text}. "
    types = [t for t in answer_type.split(",")] if "," in answer_type else [answer_type]
    texts = [_single_answer_type_text(t, is_chinese) for t in types]
    if len(set(texts)) == 1:
        text = texts[0]
        return (
            f"，题目有多个答案，答案类型均为{text}" if is_chinese
            else f"The problem has multiple answers, each of them should be {text}. "
        )
    if is_chinese:
        return "，题目有多个答案，答案类型分别为" + "、".join(texts)
    return "The problem has multiple answers, with the answers in order being " + ", ".join(texts) + ". "


def _last_boxed(text: str) -> str:
    idx = text.rfind("\\boxed")
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
                return text[i + 1 : j]
    return ""


class OlympiadBenchAdapter(BenchmarkAdapter):
    name = "olympiadbench"
    title = "OlympiadBench：奥赛级数学与物理推理"
    homepage = "https://github.com/OpenBMB/OlympiadBench"
    description = (
        "OlympiadBench 收录国际/中国奥赛与高考的奥赛级数学、物理难题，中英双语、含部分图示，"
        "评测模型的高阶科学推理与长链计算能力。对应本仓库能力维度 D05（高阶学科推理）。\n\n"
        "本次加载开放题（OE）配置，含纯文本（TO）与多模态（MM），排除需人工评阅的证明题（TP）。"
        "提示沿用官方 make_prompt，要求模型用 \\boxed{} 给出最终答案。\n\n"
        "判分使用官方符号判分器 AutoScoringJudge（sympy + LaTeX 解析，含数值容差与表达式/方程/"
        "区间等价），按学科、语言、模态、答案类型分桶统计。"
    )

    def __init__(self, data_dir: Path | None = None) -> None:
        self._data_dir = data_dir or DATA_DIR
        self._judge = None

    @property
    def judge(self):
        if self._judge is None:
            self._judge = _load_judge()()
        return self._judge

    def load_items(self, limit: int | None = None, offset: int = 0) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        for path in sorted(self._data_dir.glob("OE_*.jsonl")):
            with path.open(encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    row = json.loads(line)
                    is_chinese = (row.get("language") or "").lower().startswith("chinese")
                    is_math = (row.get("subject") or "").lower().startswith("math")
                    image_paths = [DATASET_DIR / rel for rel in (row.get("image_paths") or [])]
                    items.append(
                        {
                            "item_id": f"{row.get('config')}-{row.get('id')}",
                            "text": self._build_text(row, is_chinese, is_math),
                            "image_paths": image_paths,
                            "gold": row.get("final_answer") or [],
                            "meta": {
                                "answer_type": row.get("answer_type") or "",
                                "is_multiple_answer": bool(row.get("is_multiple_answer")),
                                "unit": row.get("unit"),
                                "error": row.get("error"),
                                "subject": row.get("subject"),
                                "language": "zh" if is_chinese else "en",
                                "modality": "MM" if image_paths else "TO",
                            },
                        }
                    )
        return items[offset : offset + limit if limit is not None else None]

    def _build_text(self, row: dict[str, Any], is_chinese: bool, is_math: bool) -> str:
        prompt = self._make_prompt(row, is_chinese, is_math)
        question = row.get("question") or ""
        context = row.get("context")
        if not is_math and context:
            return f"{prompt}\n{context}\n{question}"
        return f"{prompt}\n{question}"

    @staticmethod
    def _make_prompt(row: dict[str, Any], is_chinese: bool, is_math: bool) -> str:
        answer_type = row.get("answer_type") or ""
        multiple = bool(row.get("is_multiple_answer"))
        unit = row.get("unit")
        if is_chinese:
            subject = "数学" if is_math else "物理"
            box = "\\boxed{用英文逗号连接的多个答案}" if multiple else "\\boxed{答案}"
            unit_text = ""
            if unit:
                box += "(单位)"
                unit_text = "，注意答案的单位不要放在\\boxed{}中"
            atype = _answer_type_text(answer_type, True, multiple)
            return (
                f"以下是中国{subject}竞赛中的解答题{atype}。请根据题目的要求和所提供的信息计算得出答案。"
                f"解答过程和结果中使用的变量和公式请使用LaTeX格式表示。"
                f"请在最后以“所以最终答案是{box}。”显式给出结果{unit_text}。"
            )
        subject = "Math" if is_math else "Physics"
        box = "\\boxed{multiple answers connected with commas}" if multiple else "\\boxed{answer}"
        unit_text = ""
        if unit:
            box += "(unit)"
            unit_text = ", note that the unit of the answer should not be included in \\boxed{}"
        atype = _answer_type_text(answer_type, False, multiple)
        return (
            f"The following is an open-ended problem from an International {subject} competition. {atype}"
            f"Please calculate the answer according to the given requirements and the information provided. "
            f"Please use LaTeX format to represent the variables and formulas used in the solution process "
            f'and results. Please end your solution with "So the final answer is {box}." '
            f"and give the result explicitly{unit_text}."
        )

    def extract_answer(self, item: dict[str, Any], response: str, client: MiniMaxClient, model: str) -> str:
        response = (response or "").strip()
        if not response:
            return ""
        boxed = _last_boxed(response)
        # Re-wrap so the judge's own boxed extractor sees it identically; if there
        # is no \boxed, hand the judge the last lines so it can fall back to $...$.
        if boxed:
            return "\\boxed{" + boxed + "}"
        return "\n".join(response.split("\n")[-3:])

    def score(self, extracted: str, item: dict[str, Any]) -> dict[str, Any]:
        meta = item["meta"]
        gold_list = item.get("gold") or []
        gold = ",".join(str(g) for g in gold_list) if isinstance(gold_list, list) else str(gold_list)
        try:
            precision = float(meta.get("error")) if meta.get("error") not in (None, "") else 1e-8
        except (TypeError, ValueError):
            precision = 1e-8
        try:
            correct = bool(self.judge.judge(gold, extracted, precision))
        except Exception:
            correct = False
        return {"correct": correct, "normalized": _last_boxed(extracted) or extracted, "gold": gold}

    def buckets(self, item: dict[str, Any]) -> dict[str, str]:
        meta = item["meta"]
        return {
            "subject": str(meta.get("subject")),
            "language": str(meta.get("language")),
            "modality": str(meta.get("modality")),
            "answer_type": str(meta.get("answer_type")),
        }
