"""TutorBench adapter (real STEM tutoring, per-rubric LLM-as-judge).

Source: ``sources/datasets/tutorbench/tutorbench.jsonl`` + ``images/`` produced
by ``scripts/eval/data/fetch_eval_datasets.py --benchmark tutorbench`` from
https://huggingface.co/datasets/ScaleAI/TutorBench (paper arXiv:2510.02663).

1,473 samples span three tutoring use cases -- adaptive explanation (UC1),
assessment & feedback (UC2), active-learning hints (UC3) -- each text-only or
multimodal. Every sample carries expert-written rubric criteria with a severity
weight (critical=+5, not_critical=+1, critical_negative=-5). The model under
test produces a tutoring reply; a fixed LLM judge (``TUTORBENCH_JUDGE_MODEL``,
default ``MiniMax-M3``) rates each criterion pass/fail, and the headline is the
weighted average rubric rating ARR_w (paper Eq. 1).

Provenance note: the official paper judges with Claude Sonnet 4 and the internal
"Fair815" leaderboard used a 815-sample fair subset that is *not* shipped with
the public release. This adapter scores the full public set with a configurable
judge, so its numbers are a faithful re-implementation of the official protocol,
**not** a reproduction of the imported Fair815 leaderboard values -- do not
present them as comparable to those.
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


DATA_DIR = ROOT / "sources" / "datasets" / "tutorbench"
DATA = DATA_DIR / "tutorbench.jsonl"
MANIFEST = DATA_DIR / "data_manifest.json"
HOMEPAGE = "https://huggingface.co/datasets/ScaleAI/TutorBench"

DEFAULT_JUDGE_MODEL = "MiniMax-M3"
JUDGE_MODEL_ENV = "TUTORBENCH_JUDGE_MODEL"

# Verbatim system prompts from the paper appendix (Sec. A, "system prompt used
# for each use case"), keyed by (use_case, modality).
SYSTEM_PROMPTS = {
    (1, "text"): (
        "You are an AI tutor helping a high school student understand a concept. "
        "Answer their question clearly and adjust your explanation based on what "
        "the student says they're confused about."
    ),
    (1, "multimodal"): (
        "You are an AI tutor helping a high school student understand a concept. "
        "Answer their question clearly and adjust your explanation based on what "
        "the student says they're confused about."
    ),
    (2, "text"): (
        "You are an AI tutor reviewing a student's answer to a question. Evaluate "
        "whether it is correct, identify any mistakes, and explain your reasoning "
        "clearly. Provide an assessment of the student incorrect solution in the "
        "first response"
    ),
    (2, "multimodal"): (
        "You are an AI tutor reviewing a student's answer to a question. Evaluate "
        "whether it is correct, identify any mistakes, and explain your reasoning "
        "clearly. Provide an assessment of the student incorrect solution present "
        "in the image."
    ),
    (3, "text"): (
        "You are an AI tutor helping a student who got stuck partway through a "
        "problem. Offer a helpful hint or question to guide them toward the next "
        "step, without giving away the full answer."
    ),
    (3, "multimodal"): (
        "You are an AI tutor helping a student who got stuck partway through a "
        "problem. Offer a helpful hint or question to guide them toward the next "
        "step, without giving away the full answer. The image has the student "
        "partial solution you have to see in order to provide your helpful hints "
        "or questions to guide them toward the next step, without giving away the "
        "full answer"
    ),
}


def _read_rows() -> list[dict[str, Any]]:
    if not DATA.exists():
        raise SystemExit(
            f"missing {DATA}; run: python scripts/eval/data/fetch_eval_datasets.py --benchmark tutorbench"
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


# Version of the per-rubric judge prompt (_judge_prompt). Bump on any wording
# change; summary.json records it plus the template hash.
JUDGE_PROMPT_VERSION = "v1"


def _judge_prompt_provenance() -> dict[str, Any]:
    placeholder_item = {
        "meta": {
            "use_case": 1,
            "modality": "text",
            "context_for_judge": "{context}",
            "rubrics": [{"criteria": "{criterion}", "weight": 5}],
        }
    }
    return {
        "judge_prompt_version": JUDGE_PROMPT_VERSION,
        "judge_prompt_sha256": prompt_sha256(_judge_prompt(placeholder_item, "{response}")),
    }


_USE_CASE_TASK = {
    1: "answering the student's follow-up question with an adaptive explanation",
    2: "assessing the student's solution and giving feedback",
    3: "offering a hint or guiding question WITHOUT revealing the full answer",
}


def _judge_prompt(item: dict[str, Any], model_response: str) -> str:
    meta = item["meta"]
    criteria_lines = []
    for idx, r in enumerate(meta["rubrics"]):
        criteria_lines.append(f"{idx + 1}. {r.get('criteria')}")
    task = _USE_CASE_TASK.get(int(meta.get("use_case") or 0), "tutoring the student")
    return (
        "You are an expert evaluator grading an AI tutor's response against a set "
        "of sample-specific rubric criteria. The tutor's task was: " + task + ".\n\n"
        "### Tutoring context (question, prior turns, and student work):\n"
        f"{meta['context_for_judge']}\n\n"
        "### AI tutor's response to grade:\n"
        f"{model_response}\n\n"
        "### Rubric criteria:\n"
        + "\n".join(criteria_lines)
        + "\n\n"
        "For EACH criterion, decide whether the response SATISFIES it. Output 1 if "
        "the response satisfies the criterion, 0 if it does not. Note that some "
        "criteria are phrased as prohibitions (e.g. 'must not reveal the final "
        "answer'); such a criterion is satisfied (1) when the response correctly "
        "avoids the prohibited behavior.\n\n"
        "Return exactly this JSON shape and nothing else. The 'ratings' array must "
        "have one 0/1 entry per criterion, in the same order as listed above:\n"
        "{\n"
        '  "ratings": [1, 0, 1]\n'
        "}"
    )


def _parse_ratings(text: str, n: int) -> list[int] | None:
    """Parse a judge reply into a list of n 0/1 ratings; None if incomplete."""
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
    ratings = obj.get("ratings") if isinstance(obj, dict) else None
    if not isinstance(ratings, list):
        # last resort: pull a bare bracketed list of 0/1s
        match = re.search(r"\[([\s0-1,]+)\]", raw)
        if match:
            ratings = [int(x) for x in re.findall(r"[01]", match.group(1))]
        else:
            return None
    clean: list[int] = []
    for v in ratings:
        if isinstance(v, bool):
            clean.append(int(v))
        elif isinstance(v, (int, float)) and v in (0, 1):
            clean.append(int(v))
        else:
            return None
    return clean if len(clean) == n else None


def _arr_w(ratings: list[int], weights: list[int]) -> dict[str, float] | None:
    """Per-item metrics from pass/fail ratings and severity weights.

    - simple_pass: unweighted satisfaction rate over all rubrics.
    - weighted_positive: positive-weighted satisfaction, ignoring negatives.
    - arr_w: official ARR_w (paper Eq. 1). A negative-weight rubric is a
      prohibition; violating it (rating 0) subtracts |w|, complying (rating 1)
      adds nothing. Denominator is the sum of positive weights only, so ARR_w
      <= 1 and can dip below 0.
    - weighted_shifted: arr_w rescaled from its theoretical [lb, 1] range to
      [0, 1] (lb = sum(neg weights)/sum(pos weights)); the closest analog to the
      internal Fair815 "Weighted Shifted" ranking metric.
    """
    pos = sum(w for w in weights if w > 0)
    if pos <= 0:
        return None
    num = 0.0
    pass_pos = 0.0
    for r, w in zip(ratings, weights):
        if w > 0:
            num += w * r
            pass_pos += w * r
        else:  # prohibition: penalty applies when violated (r == 0)
            num += w * (1 - r)
    arr = num / pos
    neg = sum(w for w in weights if w < 0)
    lb = neg / pos  # theoretical minimum of arr
    shifted = (arr - lb) / (1 - lb) if (1 - lb) != 0 else arr
    return {
        "simple_pass": sum(ratings) / len(ratings),
        "weighted_positive": pass_pos / pos,
        "arr_w": arr,
        "weighted_shifted": shifted,
    }


class TutorBenchAdapter(BenchmarkAdapter):
    name = "tutorbench"
    title = "TutorBench · Real STEM Tutoring (rubric LLM-as-judge)"
    homepage = HOMEPAGE
    canonical_judge_model = DEFAULT_JUDGE_MODEL
    description = (
        "TutorBench (ScaleAI) evaluates LLM tutoring on real STEM tasks across three "
        "use cases -- adaptive explanation, assessment & feedback, and active-learning "
        "hint generation -- in text-only and multimodal form. Each sample carries "
        "expert-written rubric criteria weighted by severity (critical +5, not_critical "
        "+1, critical_negative -5).\n\n"
        "The model under test produces a tutoring reply; a fixed LLM judge "
        "(TUTORBENCH_JUDGE_MODEL, default MiniMax-M3) rates every criterion pass/fail. "
        "The headline is the weighted average rubric rating ARR_w (paper Eq. 1); "
        "simple pass rate, positive-weighted rate, and a shifted variant are reported "
        "alongside.\n\n"
        "This is a faithful re-implementation of the official protocol on the full "
        "public set, not a reproduction of the internal Fair815 leaderboard (Claude "
        "Sonnet 4 judge, private 815-sample subset) -- numbers are not comparable to those."
    )

    def load_items(self, limit: int | None = None, offset: int = 0) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        for row in _read_rows():
            uc = int(row.get("use_case") or 0)
            modality = str(row.get("modality") or "text")
            rubrics = row.get("rubrics") or []
            if not rubrics:
                continue
            image_paths: list[Path] = []
            rel = row.get("image")
            if modality == "multimodal" and rel:
                p = DATA_DIR / str(rel)
                if p.is_file():
                    image_paths.append(p)
            context = self._context_for_judge(row)
            items.append(
                {
                    "item_id": str(row.get("task_id")),
                    "text": context,
                    "image_paths": image_paths,
                    "gold": "rubric_weighted",
                    "meta": {
                        "use_case": uc,
                        "modality": modality,
                        "subject": row.get("subject"),
                        "prompt": row.get("prompt") or "",
                        "initial_explanation": row.get("initial_explanation") or "",
                        "follow_up_prompt": row.get("follow_up_prompt") or "",
                        "bloom_taxonomy": row.get("bloom_taxonomy"),
                        "rubrics": rubrics,
                        "n_rubrics": len(rubrics),
                        "context_for_judge": context,
                        "has_local_image": bool(image_paths),
                    },
                }
            )
        return items[offset : offset + limit if limit is not None else None]

    @staticmethod
    def _context_for_judge(row: dict[str, Any]) -> str:
        """Plain-text rendering of the tutoring context handed to the judge."""
        uc = int(row.get("use_case") or 0)
        modality = str(row.get("modality") or "text")
        prompt = row.get("prompt") or ""
        follow_up = row.get("follow_up_prompt") or ""
        initial = row.get("initial_explanation") or ""
        img_note = "\n[An image was attached to the student's message.]" if modality == "multimodal" else ""
        if uc == 1:
            return (
                f"Initial question:\n{prompt}{img_note}\n\n"
                f"Tutor's initial explanation:\n{initial}\n\n"
                f"Student's follow-up:\n{follow_up}"
            )
        if uc == 2:
            work = f"\n\nStudent's solution:\n{follow_up}" if follow_up.strip() else (
                "\n\n[The student's solution is shown in the attached image.]" if modality == "multimodal" else ""
            )
            return f"Question:\n{prompt}{img_note}{work}"
        # uc == 3
        work = f"\n\nStudent's work so far:\n{follow_up}" if follow_up.strip() else (
            "\n\n[The student's partial work is shown in the attached image.]" if modality == "multimodal" else ""
        )
        return f"Problem:\n{prompt}{img_note}{work}"

    def build_messages(self, item: dict[str, Any]) -> list[dict[str, Any]]:
        meta = item["meta"]
        uc = int(meta["use_case"])
        modality = str(meta["modality"])
        system = SYSTEM_PROMPTS[(uc, modality)]
        prompt = meta["prompt"]
        follow_up = meta["follow_up_prompt"]
        image = [Path(p) for p in item.get("image_paths") or []]
        messages: list[dict[str, Any]] = [{"role": "system", "content": system}]

        if uc == 1:
            # Native multi-turn dialogue: question -> tutor explanation -> follow-up.
            user1: list[dict[str, Any]] = [text_part(prompt)]
            for p in image:
                user1.append(image_part(p))
            messages.append({"role": "user", "content": user1})
            messages.append({"role": "assistant", "content": meta["initial_explanation"]})
            messages.append({"role": "user", "content": [text_part(follow_up)]})
            return messages

        if uc == 2:
            if follow_up.strip():
                text = f"Question:\n{prompt}\n\nStudent's solution to assess:\n{follow_up}"
            else:
                text = f"Question:\n{prompt}\n\n(The student's solution is in the attached image.)"
        else:  # uc == 3
            if follow_up.strip():
                text = f"Problem:\n{prompt}\n\nMy work so far:\n{follow_up}"
            else:
                text = f"Problem:\n{prompt}\n\n(My partial work is in the attached image.)"
        content: list[dict[str, Any]] = [text_part(text)]
        for p in image:
            content.append(image_part(p))
        messages.append({"role": "user", "content": content})
        return messages

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
        n = item["meta"]["n_rubrics"]
        prompt = _judge_prompt(item, response or "")
        reply = ""
        ratings: list[int] | None = None
        for attempt in range(3):
            try:
                reply = judge_client.chat(
                    [{"role": "user", "content": prompt}],
                    model=judge_model,
                    max_tokens=extraction_max_tokens(judge_model, 4096),
                )
                ratings = _parse_ratings(reply, n)
                if ratings is not None:
                    break
            except Exception:  # noqa: BLE001 - retry transient judge failures
                pass
            time.sleep(1.5 * (attempt + 1))
        return json.dumps(
            {
                "judge_model": judge_model,
                "ratings": ratings,
                "n_rubrics": n,
                "raw_judge_response": reply if ratings is None else "",
            },
            ensure_ascii=False,
        )

    def score(self, extracted, item):
        try:
            payload = json.loads(extracted)
        except (json.JSONDecodeError, TypeError):
            payload = {}
        ratings = payload.get("ratings") if isinstance(payload, dict) else None
        weights = [int(r.get("weight")) for r in item["meta"]["rubrics"]]
        metrics = None
        if isinstance(ratings, list) and len(ratings) == len(weights):
            metrics = _arr_w([int(x) for x in ratings], weights)
        if metrics is None:
            return {
                "correct": None,
                "normalized": None,
                "gold": "rubric_weighted",
                "parse_complete": False,
                "judge_model": payload.get("judge_model"),
            }
        return {
            "correct": None,  # ARR_w is a population statistic, not per-item right/wrong
            "normalized": round(metrics["arr_w"], 6),
            "gold": "rubric_weighted",
            "parse_complete": True,
            "simple_pass": round(metrics["simple_pass"], 6),
            "weighted_positive": round(metrics["weighted_positive"], 6),
            "arr_w": round(metrics["arr_w"], 6),
            "weighted_shifted": round(metrics["weighted_shifted"], 6),
            "n_passed": sum(int(x) for x in ratings),
            "n_rubrics": len(weights),
            "judge_model": payload.get("judge_model"),
        }

    def buckets(self, item):
        meta = item["meta"]
        return {
            "use_case": f"UC{meta.get('use_case')}",
            "modality": str(meta.get("modality")),
            "subject": str(meta.get("subject")),
        }

    def judge_prompt_provenance(self):
        return _judge_prompt_provenance()

    def extra_summary(self, scored):
        judge_model = os.environ.get(JUDGE_MODEL_ENV) or DEFAULT_JUDGE_MODEL
        rows = [
            r
            for r in scored
            if r.get("score_status") == "scored" and r.get("parse_complete")
        ]
        n_total = sum(1 for r in scored if r.get("score_status") == "scored")
        if not rows:
            return {"judge_model": judge_model, "n": 0, "n_parse_failed": n_total}

        def _mean(key: str) -> float:
            return round(sum(float(r[key]) for r in rows) / len(rows), 4)

        def _pct(key: str) -> float:
            return round(100.0 * sum(float(r[key]) for r in rows) / len(rows), 2)

        # Per-bucket ARR_w (x100), matching the paper's per-category reporting.
        by_uc: dict[str, list[float]] = defaultdict(list)
        by_modality: dict[str, list[float]] = defaultdict(list)
        by_subject: dict[str, list[float]] = defaultdict(list)
        for r in rows:
            b = r.get("buckets") or {}
            by_uc[str(b.get("use_case"))].append(float(r["arr_w"]))
            by_modality[str(b.get("modality"))].append(float(r["arr_w"]))
            by_subject[str(b.get("subject"))].append(float(r["arr_w"]))

        def _grouped(d: dict[str, list[float]]) -> dict[str, float]:
            return {k: round(100.0 * sum(v) / len(v), 2) for k, v in sorted(d.items())}

        return {
            "judge_model": judge_model,
            "n": len(rows),
            "n_parse_failed": n_total - len(rows),
            # Headline: official weighted average rubric rating, x100.
            "arr_w_x100": _pct("arr_w"),
            "simple_pass_x100": _pct("simple_pass"),
            "weighted_positive_x100": _pct("weighted_positive"),
            "weighted_shifted_x100": _pct("weighted_shifted"),
            "arr_w_mean": _mean("arr_w"),
            "arr_w_x100_by_use_case": _grouped(by_uc),
            "arr_w_x100_by_modality": _grouped(by_modality),
            "arr_w_x100_by_subject": _grouped(by_subject),
            "metric_note": (
                "arr_w is the official ARR_w (paper Eq. 1) as a percentage; "
                "weighted_shifted rescales it to [0,1] against its per-item lower "
                "bound and is the closest analog to the internal Fair815 ranking "
                "metric (not identical -- different judge and sample subset)."
            ),
        }
