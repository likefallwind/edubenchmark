"""BEA 2025 Shared Task adapters.

Source data is materialized by:

    python scripts/eval/data/fetch_eval_datasets.py --benchmark bea2025

The official BEA 2025 task evaluates pedagogical quality of AI tutor responses
for math dialogues across four tracks: Mistake Identification, Mistake
Location, Providing Guidance, and Actionability. The public dev split includes
human labels; the public test split does not, so local scoring uses dev labels
only and does not claim CodaBench leaderboard equivalence.
"""

from __future__ import annotations

import json
import os
import re
import time
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from ..base import ROOT, BenchmarkAdapter, prompt_sha256
from ..minimax_client import MiniMaxClient
from ..providers import extraction_max_tokens
from ..scoring import cohen_kappa, multiclass_f1


DATA_DIR = ROOT / "sources" / "datasets" / "bea2025"
DEV_PATH = DATA_DIR / "mrbench_v3_devset.json"
TEST_PATH = DATA_DIR / "mrbench_v3_testset.json"
HOMEPAGE = "https://sig-edu.org/sharedtask/2025"
DATA_REPO = "https://github.com/kaushal0494/UnifyingAITutorEvaluation/tree/main/BEA_Shared_Task_2025_Datasets"

# Production judge switched MiniMax-M3 -> glm-5.2 (2026-07-10, 待决项③a): glm-5.2
# is the best single judge on the dimension-label lines (judge_research 附录 0).
# Rubric stays v1: the self-evolved bea2025/Providing_Guidance rubric did NOT
# replicate on the sealed test split (rubric_evolution_plan 附录 4: dev +0.092 sig
# -> test -0.012 ns), so only the judge MODEL changes here, not the prompt.
# Override per-run with BEA2025_JUDGE_MODEL.
DEFAULT_JUDGE_MODEL = "glm-5.2"
JUDGE_MODEL_ENV = "BEA2025_JUDGE_MODEL"
VERBOSE_LEN = 80

# Version of the per-dimension judge rubric prompt (_judge_prompt). Bump on any
# wording change; summary.json records it plus the template hash.
JUDGE_PROMPT_VERSION = "v1"

DIMENSIONS: dict[str, dict[str, str]] = {
    "Mistake_Identification": {
        "title": "Mistake Identification",
        "definition": (
            "Does the tutor recognize that the student's latest answer or reasoning "
            "contains a mistake or confusion?"
        ),
    },
    "Mistake_Location": {
        "title": "Mistake Location",
        "definition": (
            "Does the tutor accurately point to the genuine mistake and its location "
            "in the student's solution?"
        ),
    },
    "Providing_Guidance": {
        "title": "Providing Guidance",
        "definition": (
            "Does the tutor provide correct and relevant guidance, such as a hint, "
            "explanation, elaboration, example, or supporting question?"
        ),
    },
    "Actionability": {
        "title": "Actionability",
        "definition": (
            "Is it clear from the tutor response what the student should do next, "
            "rather than leaving a vague or conversation-stopping response?"
        ),
    },
}
LABELS = ("Yes", "To some extent", "No")
KEY_DIMENSIONS = ("Mistake_Identification", "Providing_Guidance", "Actionability")


def _read_json_list(path: Any) -> list[dict[str, Any]]:
    path = path
    if not path.exists():
        raise SystemExit(
            f"missing {path}; run: python scripts/eval/data/fetch_eval_datasets.py --benchmark bea2025"
        )
    with path.open(encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, list):
        raise SystemExit(f"unexpected BEA 2025 payload in {path}: expected a JSON list")
    return data


def _conversation(entry: dict[str, Any]) -> str:
    return str(entry.get("conversation_history") or entry.get("conversation history") or "").strip()


def _sanitize_id(text: Any) -> str:
    safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", str(text)).strip("_")
    return safe or "unknown"


def _normalize_label(text: str) -> str:
    low = (text or "").strip().lower()
    if not low:
        return "unparsed"
    if re.search(r"to some extent|some extent|partial|partly|somewhat", low):
        return "To some extent"
    if re.search(r"\byes\b", low):
        return "Yes"
    if re.search(r"\bno\b", low):
        return "No"
    return "unparsed"


def _lenient(label: str) -> str:
    if label in {"Yes", "To some extent"}:
        return "Yes + To some extent"
    if label == "No":
        return "No"
    return "unparsed"


def _judge_prompt(dim: str, conversation_history: str, response: str) -> str:
    cfg = DIMENSIONS[dim]
    return (
        "You are an expert evaluator for the BEA 2025 shared task on pedagogical "
        "ability assessment of AI tutors. Judge one tutor response for one "
        "dimension.\n\n"
        f"Conversation context:\n{conversation_history}\n\n"
        f"Tutor response to evaluate:\n{response}\n\n"
        f"Dimension - {cfg['title']}: {cfg['definition']}\n\n"
        "Choose exactly one label: Yes / To some extent / No.\n"
        "Answer with the label only, no explanation."
    )


def _judge_prompt_provenance() -> dict[str, Any]:
    templates = [_judge_prompt(dim, "{conversation_history}", "{response}") for dim in DIMENSIONS]
    return {
        "judge_prompt_version": JUDGE_PROMPT_VERSION,
        "judge_prompt_sha256": prompt_sha256(*templates),
    }


def _llm_extract(client: MiniMaxClient, model: str, response: str) -> str:
    prompt = (
        "The text below is a BEA 2025 evaluator judgement. Extract exactly one "
        "label from this set and output only that label: Yes / To some extent / No.\n\n"
        f"Text:\n---\n{response}\n---\n\nLabel:"
    )
    return client.chat(
        [{"role": "user", "content": prompt}],
        model=model,
        max_tokens=extraction_max_tokens(model, 256),
    )


def _mean(xs: list[float]) -> float | None:
    return round(sum(xs) / len(xs), 4) if xs else None


def _kappa_or_none(golds: list[str], preds: list[str]) -> float | None:
    if len(set(golds)) < 2 or len(set(preds)) < 2:
        return None
    return round(cohen_kappa(golds, preds), 4)


def _classification_metrics(golds: list[str], preds: list[str]) -> dict[str, Any]:
    exact_acc = sum(1 for g, p in zip(golds, preds) if g == p) / len(golds)
    exact_f1 = multiclass_f1(golds, preds)["f1_macro"]
    lenient_golds = [_lenient(g) for g in golds]
    lenient_preds = [_lenient(p) for p in preds]
    lenient_acc = sum(1 for g, p in zip(lenient_golds, lenient_preds) if g == p) / len(golds)
    lenient_f1 = multiclass_f1(lenient_golds, lenient_preds)["f1_macro"]
    unparsed = sum(1 for p in preds if p == "unparsed")
    return {
        "n": len(golds),
        "exact_accuracy": round(exact_acc, 4),
        "exact_macro_f1": round(exact_f1, 4),
        "lenient_accuracy": round(lenient_acc, 4),
        "lenient_macro_f1": round(lenient_f1, 4),
        "cohen_kappa": _kappa_or_none(golds, preds),
        "unparsed": unparsed,
        "unparsed_rate": round(unparsed / len(golds), 4),
        "gold_distribution": dict(sorted(Counter(golds).items())),
        "pred_distribution": dict(sorted(Counter(preds).items())),
    }


def _resolve_judge_client(self: Any, extractor_client: MiniMaxClient, extractor_model: str) -> tuple[MiniMaxClient, str]:
    judge_model = os.environ.get(JUDGE_MODEL_ENV) or os.environ.get("JUDGE_MODEL") or DEFAULT_JUDGE_MODEL
    if judge_model == extractor_model:
        return extractor_client, judge_model
    cached = getattr(self, "_judge_client", None)
    if cached is None or getattr(self, "_judge_client_model", None) != judge_model:
        from ..providers import build_client

        self._judge_client = build_client(judge_model)
        self._judge_client_model = judge_model
    return self._judge_client, judge_model


def _judge_one(client: MiniMaxClient, model: str, dim: str, conv: str, response: str) -> str:
    prompt = _judge_prompt(dim, conv, response)
    last_error: Exception = RuntimeError(f"judge failed for dim={dim}")
    for attempt in range(3):
        try:
            reply = client.chat(
                [{"role": "user", "content": prompt}],
                model=model,
                max_tokens=extraction_max_tokens(model, 512),
            )
        except Exception as exc:  # noqa: BLE001 - retry transient judge/API failures
            last_error = exc
            time.sleep(1.5 * (attempt + 1))
            continue
        if not (reply or "").strip():
            last_error = RuntimeError(f"judge returned empty reply for dim={dim}")
            time.sleep(1.5 * (attempt + 1))
            continue
        label = _normalize_label(reply)
        if label != "unparsed":
            return label
        # Non-empty but unmappable: retry, then raise rather than bake an
        # "unparsed" sentinel that would score as a fake fail.
        last_error = RuntimeError(f"judge reply unmappable for dim={dim}: {reply[:120]!r}")
        time.sleep(1.5 * (attempt + 1))
    raise last_error


class BEA2025JudgeAdapter(BenchmarkAdapter):
    name = "bea2025_judge"
    title = "BEA 2025 · Judge calibration against human annotations"
    homepage = HOMEPAGE
    description = (
        "BEA 2025 Shared Task: Pedagogical Ability Assessment of AI-powered Tutors. "
        "The candidate --model is the judge: it labels existing dev-set tutor "
        "responses on four dimensions, then local scoring compares those labels "
        "with the released human annotations.\n\n"
        "Dimensions: Mistake Identification, Mistake Location, Providing Guidance, "
        "and Actionability. The headline accuracy is exact agreement with human "
        "labels. extra_metrics includes exact and lenient accuracy/macro-F1 per "
        "dimension, Cohen's kappa where label support allows, unparsed-rate, and "
        "a recommended judge score averaging exact macro-F1 across dimensions."
    )

    def load_items(self, limit: int | None = None, offset: int = 0) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        for idx, entry in enumerate(_read_json_list(DEV_PATH)):
            conv = _conversation(entry)
            cid = entry.get("conversation_id", idx)
            for tutor_id, payload in (entry.get("tutor_responses") or {}).items():
                response = str((payload or {}).get("response") or "").strip()
                annotation = (payload or {}).get("annotation") or {}
                if not response:
                    continue
                for dim in DIMENSIONS:
                    gold = annotation.get(dim)
                    if gold not in LABELS:
                        continue
                    items.append(
                        {
                            "item_id": f"c{idx}-{_sanitize_id(tutor_id)}-{dim}",
                            "text": _judge_prompt(dim, conv, response),
                            "image_paths": [],
                            "gold": gold,
                            "meta": {
                                "conversation_id": cid,
                                "dimension": dim,
                                "tutor_id": tutor_id,
                            },
                        }
                    )
        return items[offset : offset + limit if limit is not None else None]

    def extract_answer(self, item, response, client, model):
        label = _normalize_label(response)
        if label == "unparsed" and response and len(response) > VERBOSE_LEN:
            label = _normalize_label(_llm_extract(client, model, response))
        return label

    def score(self, extracted, item):
        pred = extracted or "unparsed"
        gold = item["gold"]
        return {
            "correct": pred == gold,
            "normalized": pred,
            "gold": gold,
            "dimension": item["meta"]["dimension"],
            "pred_label": pred,
            "gold_label": gold,
        }

    def buckets(self, item):
        return {
            "dimension": item["meta"]["dimension"],
            "tutor_id": str(item["meta"].get("tutor_id")),
        }

    def judge_prompt_provenance(self):
        return _judge_prompt_provenance()

    def extra_summary(self, scored):
        rows = [r for r in scored if r.get("score_status") == "scored"]
        if not rows:
            return {}
        by_dim: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in rows:
            by_dim[str(row.get("dimension"))].append(row)

        per_dim: dict[str, Any] = {}
        exact_accs: list[float] = []
        exact_f1s: list[float] = []
        lenient_accs: list[float] = []
        lenient_f1s: list[float] = []
        kappas: list[float] = []
        for dim in DIMENSIONS:
            drows = by_dim.get(dim) or []
            if not drows:
                continue
            golds = [str(r.get("gold_label")) for r in drows]
            preds = [str(r.get("pred_label")) for r in drows]
            metrics = _classification_metrics(golds, preds)
            per_dim[dim] = metrics
            exact_accs.append(metrics["exact_accuracy"])
            exact_f1s.append(metrics["exact_macro_f1"])
            lenient_accs.append(metrics["lenient_accuracy"])
            lenient_f1s.append(metrics["lenient_macro_f1"])
            if metrics["cohen_kappa"] is not None:
                kappas.append(metrics["cohen_kappa"])

        all_golds = [str(r.get("gold_label")) for r in rows]
        all_preds = [str(r.get("pred_label")) for r in rows]
        unparsed_total = sum(1 for p in all_preds if p == "unparsed")
        return {
            "metric_note": (
                "Local dev-set judge calibration. Exact labels use Yes / To some extent / No; "
                "lenient labels merge Yes and To some extent, matching BEA tracks 1-4."
            ),
            "n_items": len(rows),
            "unparsed_rate": round(unparsed_total / len(rows), 4),
            "recommended_judge_score": _mean(exact_f1s),
            "recommended_judge_metric": "mean exact_macro_f1 over the four BEA dimensions",
            "macro_over_dimensions": {
                "exact_accuracy": _mean(exact_accs),
                "exact_macro_f1": _mean(exact_f1s),
                "lenient_accuracy": _mean(lenient_accs),
                "lenient_macro_f1": _mean(lenient_f1s),
                "cohen_kappa": _mean(kappas),
            },
            "overall_micro": _classification_metrics(all_golds, all_preds),
            "per_dimension": per_dim,
        }


class BEA2025TutorAdapter(BenchmarkAdapter):
    name = "bea2025_tutor"
    title = "BEA 2025 · Generate tutor response + fixed-judge scoring"
    homepage = HOMEPAGE
    description = (
        "BEA 2025 tutor-generation smoke test: the tested --model generates the "
        "next tutor reply from each dev-set dialogue context. A fixed judge from "
        "BEA2025_JUDGE_MODEL or JUDGE_MODEL labels the generated reply on the same "
        "four BEA dimensions.\n\n"
        "The headline accuracy is a local pedagogical pass rate: Mistake "
        "Identification, Providing Guidance, and Actionability must all be judged "
        "Yes. This is a practical harness metric, not an official BEA leaderboard "
        "metric; the public test labels are hidden and require official evaluation."
    )

    def load_items(self, limit: int | None = None, offset: int = 0) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        for idx, entry in enumerate(_read_json_list(DEV_PATH)):
            conv = _conversation(entry)
            if not conv:
                continue
            text = (
                "You are an experienced, supportive math tutor. Read the conversation "
                "context and write ONLY the tutor's next reply.\n"
                "Guidelines: identify any student mistake or confusion, locate the "
                "issue when possible, give correct and relevant guidance, and make "
                "the next step clear. Avoid simply revealing the final answer. Keep "
                "the reply concise, natural, and encouraging.\n\n"
                f"Conversation context:\n{conv}\n\n"
                "Tutor's next reply:"
            )
            items.append(
                {
                    "item_id": f"c{idx}",
                    "text": text,
                    "image_paths": [],
                    "gold": "pedagogical",
                    "meta": {
                        "conversation_id": entry.get("conversation_id", idx),
                        "conversation_history": conv,
                    },
                }
            )
        return items[offset : offset + limit if limit is not None else None]

    def extract_answer(self, item, response, client, model):
        judge_client, judge_model = _resolve_judge_client(self, client, model)
        conv = item["meta"]["conversation_history"]
        generated = (response or "").strip()
        dims = list(DIMENSIONS)
        with ThreadPoolExecutor(max_workers=len(dims)) as pool:
            raws = list(pool.map(lambda d: _judge_one(judge_client, judge_model, d, conv, generated), dims))
        # Store the judge's raw reply per dimension; parsing happens in score().
        result = {dim: raw for dim, raw in zip(dims, raws)}
        result["judge_model"] = judge_model
        return json.dumps(result, ensure_ascii=False)

    def resolved_judge_model(self, extractor_model: str) -> str | None:
        return os.environ.get(JUDGE_MODEL_ENV) or os.environ.get("JUDGE_MODEL") or DEFAULT_JUDGE_MODEL

    def score(self, extracted, item):
        try:
            raw = json.loads(extracted)
        except (json.JSONDecodeError, TypeError):
            raw = {}
        judge_model = raw.pop("judge_model", None) if isinstance(raw, dict) else None
        # ``raw`` holds either the judge's raw reply per dimension (current format)
        # or already-normalized labels (legacy rows); _normalize_label is idempotent
        # on canonical labels, so both parse correctly here.
        labels = (
            {dim: _normalize_label(str(raw.get(dim, ""))) for dim in DIMENSIONS}
            if isinstance(raw, dict) and raw
            else {}
        )
        passed = bool(labels) and all(labels.get(dim) == "Yes" for dim in KEY_DIMENSIONS)
        return {
            "correct": passed,
            "normalized": "pass" if passed else "fail",
            "gold": "pedagogical",
            "judge_labels": labels,
            "judge_model": judge_model,
        }

    def buckets(self, item):
        return {"conversation_id": str(item["meta"].get("conversation_id"))}

    def judge_prompt_provenance(self):
        return _judge_prompt_provenance()

    def extra_summary(self, scored):
        rows = [r for r in scored if r.get("score_status") == "scored"]
        judge_model = os.environ.get(JUDGE_MODEL_ENV) or os.environ.get("JUDGE_MODEL") or DEFAULT_JUDGE_MODEL
        if not rows:
            return {"judge_model": judge_model, "n": 0}
        per_dim: dict[str, Any] = {}
        for dim in DIMENSIONS:
            dist = Counter(str((r.get("judge_labels") or {}).get(dim, "unparsed")) for r in rows)
            per_dim[dim] = {
                lab: {"count": count, "share": round(count / len(rows), 4)}
                for lab, count in sorted(dist.items(), key=lambda kv: (-kv[1], kv[0]))
            }
        # Keep genuinely-unparseable key-dim rows out of the pass-rate denominator
        # rather than counting them as fails; report them separately.
        def _key_unparseable(r):
            labs = r.get("judge_labels") or {}
            return any(labs.get(dim) == "unparsed" for dim in KEY_DIMENSIONS)

        parseable = [r for r in rows if not _key_unparseable(r)]
        passed = sum(1 for r in parseable if r.get("correct"))
        return {
            "judge_model": judge_model,
            "judge_protocol": "fixed LLM-as-judge, one label per BEA dimension",
            "headline_metric": f"pedagogical pass rate = all of {KEY_DIMENSIONS} == 'Yes'",
            "official_equivalence": (
                "Not an official BEA leaderboard score; public test labels are hidden "
                "and CodaBench/official labels are required for official scoring."
            ),
            "n": len(parseable),
            "n_unparseable_key_dim": len(rows) - len(parseable),
            "pass_rate": round(passed / len(parseable), 4) if parseable else None,
            "per_dimension_distribution": per_dim,
        }
