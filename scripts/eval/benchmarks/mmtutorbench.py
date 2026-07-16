"""MMTutorBench adapter (multimodal math tutoring, rubric LLM-as-judge).

Source: ``sources/datasets/mmtutorbench/mmtutorbench.jsonl`` downloaded by
``scripts/eval/data/fetch_eval_datasets.py --benchmark mmtutorbench`` from
https://huggingface.co/datasets/Tangchiu/mmtutorbench.

Each item provides previous keyframes plus the current keyframe, a student
question, a reference answer split into key detail / operation / next step, and
a per-instance rubric with six binary criteria. The model under test generates
a structured tutoring response; a fixed judge model (``MMTUTORBENCH_JUDGE_MODEL``,
default ``MiniMax-M3``) scores the response from 0 to 6.
"""

from __future__ import annotations

import json
import os
import re
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from ..base import ROOT, BenchmarkAdapter, prompt_sha256
from ..minimax_client import MiniMaxClient, image_part, text_part
from ..providers import build_client, extraction_max_tokens


DATA_DIR = ROOT / "sources" / "datasets" / "mmtutorbench"
DATA = DATA_DIR / "mmtutorbench.jsonl"
MANIFEST = DATA_DIR / "data_manifest.json"
HOMEPAGE = "https://huggingface.co/datasets/Tangchiu/mmtutorbench"

DEFAULT_JUDGE_MODEL = "MiniMax-M3"
JUDGE_MODEL_ENV = "MMTUTORBENCH_JUDGE_MODEL"

DIMENSIONS = (
    "insight_identification",
    "operation_prescription",
    "operation_execution",
    "solution_scope_control",
    "brevity",
    "coherence",
)


def _read_rows() -> list[dict[str, Any]]:
    if not DATA.exists():
        raise SystemExit(
            f"missing {DATA}; run: python scripts/eval/data/fetch_eval_datasets.py --benchmark mmtutorbench"
        )
    rows: list[dict[str, Any]] = []
    with DATA.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _read_manifest() -> dict[str, Any]:
    if MANIFEST.exists():
        return json.loads(MANIFEST.read_text(encoding="utf-8"))
    return {}


def _image_paths(row: dict[str, Any]) -> list[Path]:
    paths: list[Path] = []
    for rel in row.get("prev_img") or []:
        if rel:
            paths.append(DATA_DIR / str(rel))
    if row.get("img"):
        paths.append(DATA_DIR / str(row["img"]))
    return paths


def _parse_scores(text: str) -> dict[str, int]:
    """Parse a judge reply into the six 0/1 scores."""
    raw = (text or "").strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.IGNORECASE)
        raw = re.sub(r"\s*```$", "", raw)
    obj: Any = None
    try:
        obj = json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", raw, flags=re.DOTALL)
        if match:
            try:
                obj = json.loads(match.group(0))
            except json.JSONDecodeError:
                obj = None
    if isinstance(obj, dict) and isinstance(obj.get("evaluation_scores"), dict):
        obj = obj["evaluation_scores"]
    scores: dict[str, int] = {}
    for dim in DIMENSIONS:
        value = obj.get(dim) if isinstance(obj, dict) else None
        if isinstance(value, bool):
            scores[dim] = int(value)
        elif isinstance(value, (int, float)) and value in (0, 1):
            scores[dim] = int(value)
        else:
            match = re.search(rf'"{re.escape(dim)}"\s*:\s*([01])', raw)
            if match:
                scores[dim] = int(match.group(1))
    return scores


# Version of the rubric judge prompt (_judge_prompt). Bump on any wording
# change; summary.json records it plus the template hash (rendered with
# placeholder fields — the per-item rubric criteria come from the dataset).
JUDGE_PROMPT_VERSION = "v1"


def _judge_prompt_provenance() -> dict[str, Any]:
    placeholder_item = {
        "meta": {
            "rubric": {"task_description": "{task_description}", "evaluation_criteria": []},
            "question": "{question}",
        },
        "gold": "{reference_answer}",
    }
    return {
        "judge_prompt_version": JUDGE_PROMPT_VERSION,
        "judge_prompt_sha256": prompt_sha256(_judge_prompt(placeholder_item, "{response}")),
    }


def _judge_prompt(item: dict[str, Any], model_response: str) -> str:
    rubric = item["meta"]["rubric"]
    criteria = []
    for c in rubric.get("evaluation_criteria") or []:
        criteria.append(
            f"Criterion: {c.get('criterion')} (ID: {c.get('id')})\n"
            f"- Score 1 if: {c.get('condition_for_1')}\n"
            f"- Score 0 if: {c.get('condition_for_0')}"
        )
    return (
        "### Task Description:\n"
        "Your task is to act as an expert evaluator of an AI-powered math tutor's response. "
        "Evaluate the response against the per-instance rubric and return one final JSON object.\n\n"
        f"### Student's Question:\n{item['meta']['question']}\n\n"
        f"### Reference Tutoring Answer:\n{item['gold']}\n\n"
        f"### AI's Response (The Next Step):\n{model_response}\n\n"
        f"### Scoring Rubric:\nTask Description: {rubric.get('task_description')}\n\n"
        "Criteria:\n\n"
        + "\n\n".join(criteria)
        + "\n\n"
        'Note: When scoring "insight_identification", "operation_prescription", '
        'and "operation_execution", strictly follow the one-to-one correspondence '
        "between the response section and that rubric criterion.\n\n"
        "Return exactly this JSON shape and no text outside JSON:\n"
        "{\n"
        '  "reasoning": "brief justification for each score",\n'
        '  "evaluation_scores": {\n'
        '    "insight_identification": 0,\n'
        '    "operation_prescription": 0,\n'
        '    "operation_execution": 0,\n'
        '    "solution_scope_control": 0,\n'
        '    "brevity": 0,\n'
        '    "coherence": 0\n'
        "  }\n"
        "}"
    )


class MMTutorBenchAdapter(BenchmarkAdapter):
    name = "mmtutorbench"
    title = "MMTutorBench · Multimodal Math Tutoring"
    homepage = HOMEPAGE
    description = (
        "MMTutorBench evaluates multimodal math tutoring: the model sees previous "
        "keyframe images, the current keyframe image, and a student's question, then "
        "must provide next-step guidance rather than a full solution. The response is "
        "structured into Insight Discovery, Operation Formulation, and Operation Execution.\n\n"
        "Scoring uses the dataset's per-instance rubric with six binary criteria: "
        "insight_identification, operation_prescription, operation_execution, "
        "solution_scope_control, brevity, and coherence. A fixed LLM judge is selected "
        "with MMTUTORBENCH_JUDGE_MODEL (default MiniMax-M3); total score is 0-6."
    )

    def load_items(self, limit: int | None = None, offset: int = 0) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        for idx, row in enumerate(_read_rows()):
            image_paths = _image_paths(row)
            missing = [str(p) for p in image_paths if not p.is_file()]
            if missing:
                raise SystemExit(
                    "missing MMTutorBench image(s); run: "
                    "python scripts/eval/data/fetch_eval_datasets.py --benchmark mmtutorbench\n"
                    + "\n".join(missing[:5])
                )
            question = row.get("question") or ""
            text = (
                "You are a precise and logical math tutor who guides students step by step.\n\n"
                "A student is working on math homework but got stuck after completing a few steps. "
                "You are given previous images in chronological order, the current image, and the "
                "student's question. Identify the student's point of confusion and provide guidance "
                "on the single next key step. Do not reveal a lengthy full solution or multiple "
                "subsequent steps.\n\n"
                "Your response must use exactly these three sections:\n"
                "- [Insight Discovery]: extract the key detail in the student's current state and explain why it matters.\n"
                "- [Operation Formulation]: state the very next critical mathematical operation the student should perform.\n"
                "- [Operation Execution]: execute only that key operation and give the immediate result.\n\n"
                f"Student's question:\n{question}"
            )
            items.append(
                {
                    "item_id": str(row.get("instance_id") or f"mmtb-{idx}"),
                    "text": text,
                    "image_paths": image_paths,
                    "gold": row.get("answer"),
                    "meta": {
                        "question": question,
                        "rubric": row.get("rubric") or {},
                        "domain": row.get("domain") or "unknown",
                        "category": row.get("category") or "unknown",
                        "difficulty_score": row.get("difficulty_score"),
                        "video_id": row.get("video_id"),
                        "uploader_id": row.get("uploader_id"),
                        "pic_num": row.get("pic_num"),
                        "current_image": row.get("img"),
                        "previous_images": row.get("prev_img") or [],
                    },
                }
            )
        return items[offset : offset + limit if limit is not None else None]

    def build_messages(self, item: dict[str, Any]) -> list[dict[str, Any]]:
        content: list[dict[str, Any]] = [text_part(item["text"])]
        paths = [Path(p) for p in item.get("image_paths") or []]
        prev_count = max(0, len(paths) - 1)
        for idx, path in enumerate(paths):
            label = f"Previous image {idx + 1} of {prev_count}" if idx < prev_count else "Current image"
            content.append(text_part(label))
            content.append(image_part(path))
        return [{"role": "user", "content": content}]

    def _resolve_judge(self, extractor_client: MiniMaxClient, extractor_model: str) -> tuple[MiniMaxClient, str]:
        judge_model = os.environ.get(JUDGE_MODEL_ENV) or DEFAULT_JUDGE_MODEL
        if judge_model == extractor_model:
            return extractor_client, judge_model
        cached = getattr(self, "_judge_client", None)
        if cached is None or self._judge_client_model != judge_model:
            self._judge_client = build_client(judge_model)
            self._judge_client_model = judge_model
        return self._judge_client, judge_model

    def resolved_judge_model(self, extractor_model: str) -> str | None:
        return os.environ.get(JUDGE_MODEL_ENV) or DEFAULT_JUDGE_MODEL

    def extract_answer(self, item, response, client, model):
        judge_client, judge_model = self._resolve_judge(client, model)
        prompt = _judge_prompt(item, response or "")
        reply = ""
        scores: dict[str, int] = {}
        for attempt in range(3):
            try:
                reply = judge_client.chat(
                    [{"role": "user", "content": prompt}],
                    model=judge_model,
                    max_tokens=extraction_max_tokens(judge_model, 2048),
                )
                scores = _parse_scores(reply)
                if all(dim in scores for dim in DIMENSIONS):
                    break
            except Exception:  # noqa: BLE001 - retry transient judge failures
                pass
            time.sleep(1.5 * (attempt + 1))
        return json.dumps(
            {
                "judge_model": judge_model,
                "scores": {dim: scores.get(dim) for dim in DIMENSIONS},
                "raw_judge_response": reply,
            },
            ensure_ascii=False,
        )

    def score(self, extracted, item):
        try:
            payload = json.loads(extracted)
        except (json.JSONDecodeError, TypeError):
            payload = {}
        scores = payload.get("scores") if isinstance(payload, dict) else {}
        clean_scores = {
            dim: int(scores[dim])
            for dim in DIMENSIONS
            if isinstance(scores, dict) and scores.get(dim) in (0, 1)
        }
        total = sum(clean_scores.values()) if len(clean_scores) == len(DIMENSIONS) else None
        return {
            "correct": total == len(DIMENSIONS),
            "normalized": total,
            "gold": "rubric_score_0_to_6",
            "total_score": total,
            "dimension_scores": clean_scores,
            "judge_model": payload.get("judge_model"),
            "parse_complete": len(clean_scores) == len(DIMENSIONS),
        }

    def buckets(self, item):
        return {
            "domain": str(item["meta"].get("domain")),
            "category": str(item["meta"].get("category")),
            "difficulty": str(item["meta"].get("difficulty_score")),
        }

    def judge_prompt_provenance(self):
        return _judge_prompt_provenance()

    def extra_summary(self, scored):
        rows = [r for r in scored if r.get("score_status") == "scored"]
        judge_model = os.environ.get(JUDGE_MODEL_ENV) or DEFAULT_JUDGE_MODEL
        if not rows:
            return {"judge_model": judge_model, "n": 0}
        scored_with_total = [r for r in rows if isinstance(r.get("total_score"), int)]
        per_dim: dict[str, float | None] = {}
        zero_counts: dict[str, int] = {}
        for dim in DIMENSIONS:
            vals = [
                int((r.get("dimension_scores") or {}).get(dim))
                for r in rows
                if isinstance((r.get("dimension_scores") or {}).get(dim), int)
            ]
            per_dim[dim] = round(sum(vals) / len(vals), 4) if vals else None
            zero_counts[dim] = sum(1 for v in vals if v == 0)
        avg_total = (
            round(sum(int(r["total_score"]) for r in scored_with_total) / len(scored_with_total), 4)
            if scored_with_total
            else None
        )
        # The paper reports Avg. as the sum/mean of six equally weighted binary
        # dimensions on a 0-6 scale, plus per-dimension means.
        paper_weighted_score = (
            round(sum(float(per_dim[d]) for d in DIMENSIONS if per_dim[d] is not None), 4)
            if all(per_dim[d] is not None for d in DIMENSIONS)
            else None
        )
        totals = Counter(str(r.get("total_score")) for r in scored_with_total)
        return {
            "judge_model": judge_model,
            "n": len(rows),
            "parse_complete": sum(1 for r in rows if r.get("parse_complete")),
            "average_total_score_0_to_6": avg_total,
            "paper_weighted_score_0_to_6": paper_weighted_score,
            "paper_weighting": "equal weight over the six binary rubric dimensions; same as Table 3 Avg.",
            "dimension_means": per_dim,
            "zero_counts_by_dimension": zero_counts,
            "total_score_distribution": dict(sorted(totals.items())),
        }


class MMTutorBenchJudgeCalibrationAdapter(BenchmarkAdapter):
    name = "mmtutorbench_judge_calibration"
    title = "MMTutorBench · Judge Calibration Status"
    homepage = HOMEPAGE
    description = (
        "Calibration hook for checking a candidate judge against public per-item human/expert scores. "
        "The currently published HuggingFace JSONL exposes rubrics and reference answers, but no "
        "per-item human gold scores, so this adapter intentionally does not fabricate calibration metrics."
    )

    def load_items(self, limit: int | None = None, offset: int = 0) -> list[dict[str, Any]]:
        manifest = _read_manifest()
        if manifest.get("has_public_human_gold"):
            raise SystemExit(
                "MMTutorBench manifest reports possible human-score fields, but this adapter does not know "
                "their schema yet. Inspect sources/datasets/mmtutorbench/data_manifest.json before calibration."
            )
        return []

    def extract_answer(self, item, response, client, model):
        return ""

    def score(self, extracted, item):
        return {"correct": False, "normalized": None, "gold": None}

    def extra_summary(self, scored):
        manifest = _read_manifest()
        return {
            "status": "not_run",
            "reason": "no public per-item human/expert gold scores found in MMTutorBench JSONL",
            "candidate_judge_model": os.environ.get(JUDGE_MODEL_ENV) or DEFAULT_JUDGE_MODEL,
            "manifest_human_score_fields": manifest.get("human_score_fields", []),
            "has_public_human_gold": bool(manifest.get("has_public_human_gold")),
        }
