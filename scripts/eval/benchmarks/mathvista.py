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
        # on reasoning_content before emitting the final answer text.
        extraction = client.chat(
            [{"role": "user", "content": full_prompt}],
            model=model,
            max_tokens=1024,
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
