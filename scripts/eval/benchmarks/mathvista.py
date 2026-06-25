"""MathVista adapter (D06: multimodal math reasoning).

Source: ``sources/datasets/mathvista`` (official repo checkout). Uses the
``testmini`` split (1000 items), the pre-built per-pid ``query`` text, and local
images downloaded via ``data/images.zip``. Answer extraction and scoring follow
the official ``evaluation/`` pipeline (LLM extraction + answer-type normalization).
"""

from __future__ import annotations

import json
from typing import Any

from ..base import ROOT, BenchmarkAdapter
from ..minimax_client import MiniMaxClient
from ..providers import extraction_max_tokens
from ..scoring import normalize_extracted_answer, safe_equal


DATA_DIR = ROOT / "sources" / "datasets" / "mathvista" / "data"
DEMO_PROMPT_FILE = ROOT / "sources" / "datasets" / "mathvista" / "evaluation" / "prompts" / "ext_ans.py"


def _load_demo_prompt() -> str:
    """Load the official answer-extraction few-shot prompt from the repo file."""
    namespace: dict[str, Any] = {}
    exec(compile(DEMO_PROMPT_FILE.read_text(encoding="utf-8"), str(DEMO_PROMPT_FILE), "exec"), namespace)
    return str(namespace["demo_prompt"]).strip()


class MathVistaAdapter(BenchmarkAdapter):
    name = "mathvista"
    title = "MathVista：多模态数学推理基准"
    homepage = "https://mathvista.github.io/"
    description = (
        "MathVista 评测视觉语境下的数学推理能力，题目把图表、几何图形、函数曲线、"
        "自然/学术图片等视觉信息与数学问题结合，模型必须先看懂图、再完成推理与计算。"
        "对应本仓库能力维度 D06（多模态教育理解）。\n\n"
        "本次使用官方 testmini 划分（1000 题），题型分为选择题（multi_choice）与"
        "自由作答（free_form），答案类型涵盖整数、浮点数、文本与列表，并按任务"
        "（几何求解、图表问答、数学应用题、教材问答、视觉问答）分桶统计。\n\n"
        "答案抽取与判分沿用官方 evaluation 流程：先走快速路径，再由 LLM 从模型自由"
        "作答中抽取最终答案，最后做答案类型归一化与就近选项匹配。"
    )

    def __init__(self) -> None:
        self._demo_prompt: str | None = None

    @property
    def demo_prompt(self) -> str:
        if self._demo_prompt is None:
            self._demo_prompt = _load_demo_prompt()
        return self._demo_prompt

    def load_items(self, limit: int | None = None, offset: int = 0) -> list[dict[str, Any]]:
        problems = json.loads((DATA_DIR / "testmini.json").read_text(encoding="utf-8"))
        queries = json.loads((DATA_DIR / "query.json").read_text(encoding="utf-8"))
        pids = sorted(problems, key=lambda p: int(p) if str(p).isdigit() else str(p))
        pids = pids[offset : offset + limit if limit is not None else None]
        items = []
        for pid in pids:
            problem = problems[pid]
            image_rel = problem.get("image")
            image_paths = [DATA_DIR / image_rel] if image_rel else []
            items.append(
                {
                    "item_id": str(pid),
                    "text": queries.get(pid, problem.get("question", "")),
                    "image_paths": image_paths,
                    "gold": problem.get("answer"),
                    "meta": {
                        "query": queries.get(pid, ""),
                        "question_type": problem.get("question_type"),
                        "answer_type": problem.get("answer_type"),
                        "choices": problem.get("choices"),
                        "precision": problem.get("precision"),
                        "task": (problem.get("metadata") or {}).get("task"),
                    },
                }
            )
        return items

    def extract_answer(self, item: dict[str, Any], response: str, client: MiniMaxClient, model: str) -> str:
        """Mirror MathVista's ``extract_answer``: quick paths, then LLM fallback."""
        meta = item["meta"]
        question_type = meta.get("question_type")
        answer_type = meta.get("answer_type")
        choices = meta.get("choices") or []
        response = (response or "").strip()
        if not response:
            return ""

        if question_type == "multi_choice" and response in choices:
            return response
        if answer_type == "integer":
            try:
                return str(int(response))
            except Exception:
                pass
        if answer_type == "float":
            try:
                return str(float(response))
            except Exception:
                pass

        full_prompt = f"{self.demo_prompt}\n\n{meta.get('query', item['text'])}\n\n{response}\n\nExtracted answer: "
        # Headroom for reasoning models (e.g. MiniMax-M3) that spend output budget
        # on reasoning_content before emitting the final answer text; models with
        # a hidden reasoning phase (e.g. gpt-5.5) run uncapped so it never starves.
        extraction = client.chat(
            [{"role": "user", "content": full_prompt}],
            model=model,
            max_tokens=extraction_max_tokens(model, 1024),
        )
        return extraction.strip()

    def score(self, extracted: str, item: dict[str, Any]) -> dict[str, Any]:
        meta = item["meta"]
        normalized = normalize_extracted_answer(
            extracted,
            meta.get("choices"),
            meta.get("question_type"),
            meta.get("answer_type"),
            meta.get("precision"),
        )
        gold = item.get("gold")
        correct = safe_equal(normalized, gold)
        return {"correct": correct, "normalized": normalized, "gold": gold}

    def buckets(self, item: dict[str, Any]) -> dict[str, str]:
        meta = item["meta"]
        return {
            "question_type": str(meta.get("question_type")),
            "answer_type": str(meta.get("answer_type")),
            "task": str(meta.get("task")),
        }
