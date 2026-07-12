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

import hashlib
from pathlib import Path
from typing import Any

from .minimax_client import MiniMaxClient, image_part, text_part


ROOT = Path(__file__).resolve().parents[2]


def prompt_sha256(*templates: str) -> str:
    """Fingerprint of judge-prompt template text (rendered with placeholder
    fields, joined in a fixed order) so any rubric wording change is
    attributable in summary.json."""
    return hashlib.sha256("\n␞\n".join(templates).encode("utf-8")).hexdigest()


class BenchmarkAdapter:
    name: str = ""

    # Name of the model being evaluated; set by eval_benchmark.py after
    # construction. Adapters that must call the model-under-test outside the
    # prediction phase (e.g. p07_selfcheck's round-2 turn) read this — the
    # ``client`` handed to extract_answer is the *extractor*, a different model.
    model_under_test: str | None = None

    # Report metadata: shown in the HTML eval report's "benchmark intro" section.
    # Override in subclasses. ``description`` may contain blank-line-separated
    # paragraphs (rendered as <p>); keep it concise (2-4 short paragraphs).
    title: str = ""
    homepage: str = ""
    description: str = ""

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

    def extra_summary(self, scored: list[dict[str, Any]]) -> dict[str, Any]:
        """Benchmark-specific metrics beyond accuracy (e.g. RFS, ASR).

        Receives the scored rows; the result is written into ``summary.json``
        under ``extra_metrics``. Default: none.
        """
        return {}

    def judge_prompt_provenance(self) -> dict[str, Any]:
        """Version + hash of the LLM-judge rubric prompt(s), if this benchmark
        uses one. Written top-level into ``summary.json`` so rubric changes are
        attributable across runs. Default: none (rule-scored benchmarks).

        Override to return ``{"judge_prompt_version": "v1",
        "judge_prompt_sha256": <hex or {name: hex}>}``.
        """
        return {}
