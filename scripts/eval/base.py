"""Benchmark adapter interface.

An ``Item`` is the framework's normalized unit of work:

    {
        "item_id": str,                 # stable id (e.g. MathVista pid)
        "text": str,                    # prompt text shown to the model
        "image_paths": list[Path],      # local images to attach (may be empty)
        "gold": Any,                    # ground-truth answer for scoring
        "meta": dict,                   # adapter-specific fields used by score()
    }

Each benchmark subclasses ``BenchmarkAdapter`` and implements the five methods
below. The generic runner orchestrates the rest.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .minimax_client import MiniMaxClient, image_part, text_part


ROOT = Path(__file__).resolve().parents[2]


class BenchmarkAdapter:
    name: str = ""

    def load_items(self, limit: int | None = None, offset: int = 0) -> list[dict[str, Any]]:
        raise NotImplementedError

    def build_messages(self, item: dict[str, Any]) -> list[dict[str, Any]]:
        """Default: one user turn with the text followed by any images."""
        content: list[dict[str, Any]] = [text_part(item["text"])]
        for path in item.get("image_paths") or []:
            content.append(image_part(Path(path)))
        return [{"role": "user", "content": content}]

    def extract_answer(self, item: dict[str, Any], response: str, client: MiniMaxClient, model: str) -> str:
        """Reduce a free-form model response to a compact answer string."""
        raise NotImplementedError

    def score(self, extracted: str, item: dict[str, Any]) -> dict[str, Any]:
        """Return {"correct": bool, "normalized": Any, "gold": Any}."""
        raise NotImplementedError

    def buckets(self, item: dict[str, Any]) -> dict[str, str]:
        """Grouping keys for the report (e.g. question_type, answer_type)."""
        return {}
