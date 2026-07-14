"""LongTutor: long-history personalized tutoring (ACL 2026).

Three separate adapters preserve the benchmark's native metric boundaries:
semantic evidence accuracy, diagnosis accuracy/macro-F1, and rubric-judged
teaching quality.  This is offline history replay, not a longitudinal learning-
gain experiment.
"""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from typing import Any

from ..base import ROOT, BenchmarkAdapter, prompt_sha256
from ..minimax_client import MiniMaxClient
from ..scoring import multiclass_f1


BASE = ROOT / "sources" / "datasets" / "longtutor"
DATA = BASE / "data" / "XES3G5M"
FEATURES = DATA / "history_features_lastq_scale.jsonl"
GOLD = DATA / "human_an_updated.jsonl"
HOMEPAGE = "https://github.com/liano3/LongTutor"
DIAGNOSES = {"Recall Failure", "Conceptual Gap", "Procedural Error", "Transfer Deficit"}
MEMORY_TYPES = ["Information Extraction", "Multi-session Reasoning", "Hallucination Check"]
JUDGE_VERSION = "v2"
EVIDENCE_JUDGE_TEMPLATE = """Determine whether the candidate answer is semantically equivalent to the reference answer.
Unknown is correct only when both answers indicate that the requested fact is unsupported.
Ignore differences in wording, punctuation, and units that do not change the answer.
Return exactly CORRECT or INCORRECT.

Question: {query}
Reference: {gold}
Candidate: {candidate}"""
TEACHING_JUDGE_TEMPLATE = """You are a strict education evaluator. Score the candidate from 1 to 5 on each dimension: history_utilization, strategy_alignment, coherence, appropriateness. Consider the supplied gold diagnosis and strategy but do not require lexical overlap with the reference. Return JSON only.

Context:
{context}
Gold diagnosis: {diagnosis}
Gold strategy: {strategy}
Reference teaching: {gold}
Candidate: {candidate}"""


def _read_jsonl(path) -> list[dict[str, Any]]:
    if not path.exists():
        raise SystemExit(
            f"missing {path}; run fetch_eval_datasets.py --benchmark longtutor, then prepare_longtutor.py"
        )
    with path.open(encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def _sample_key(row: dict[str, Any]) -> str:
    digest = hashlib.sha256(str(row.get("question_info", "")).encode()).hexdigest()
    return f"{row.get('uid', '')}||{digest}"


def _joined() -> list[tuple[str, dict[str, Any], dict[str, Any]]]:
    gold = {str(row.get("_key")): row for row in _read_jsonl(GOLD) if row.get("_key")}
    joined = []
    for feature in _read_jsonl(FEATURES):
        key = _sample_key(feature)
        if key in gold:
            joined.append((key, feature, gold[key]))
    if not joined:
        raise SystemExit("LongTutor features have no rows matching human gold; rerun prepare_longtutor.py --force")
    return joined


def _context(feature: dict[str, Any]) -> str:
    history = list(feature.get("history_info") or [])[-200:]
    return (
        "### INTERACTION HISTORY\n"
        + json.dumps(history, ensure_ascii=False)
        + "\n\n### CURRENT QUESTION\n"
        + str(feature.get("question_info", ""))
    )


def _json_from_text(text: str) -> Any:
    match = re.search(r"\{.*\}", text, re.S)
    if not match:
        return None


def _normalize_answer(text: Any) -> str:
    value = unicodedata.normalize("NFKC", str(text or "")).strip().lower()
    value = re.sub(r"\s+", "", value)
    return re.sub(r"[，。！？；：、,.!?;:'\"“”‘’（）()\[\]{}]", "", value)
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None


class LongTutorEvidenceAdapter(BenchmarkAdapter):
    name = "longtutor_evidence"
    title = "LongTutor - Historical Evidence Acquisition"
    homepage = HOMEPAGE
    description = (
        "基于跨度超过 7 天的学生历史，分别测量单记录信息提取、跨 session 推理和幻觉检查。"
        "主指标为语义正确率；这是离线长历史重放，不代表真实长期学习增益。"
    )
    extraction_cache_version = "longtutor-evidence-v2"

    def load_items(self, limit=None, offset=0):
        items = []
        for key, feature, gold in _joined():
            for idx, query in enumerate(gold.get("memory") or []):
                items.append({
                    "item_id": f"{key}::Q{idx + 1}",
                    "text": f"{_context(feature)}\n\nQuestion: {query.get('query', '')}\nAnswer concisely. If unsupported, answer Unknown.",
                    "image_paths": [],
                    "gold": str(query.get("answer", "")),
                    "meta": {
                        "memory_type": MEMORY_TYPES[idx] if idx < 3 else f"Q{idx + 1}",
                        "query": str(query.get("query", "")),
                    },
                })
        return items[offset : None if limit is None else offset + limit]

    def extract_answer(self, item, response, client: MiniMaxClient, model):
        if _normalize_answer(response) == _normalize_answer(item["gold"]):
            return "CORRECT_EXACT"
        prompt = EVIDENCE_JUDGE_TEMPLATE.format(
            query=item["meta"]["query"], gold=item["gold"], candidate=response
        )
        return client.chat(
            [{"role": "user", "content": prompt}],
            model=model,
            max_tokens=None,
        ).strip().upper()

    def score(self, extracted, item):
        ok = extracted.startswith("CORRECT") and not extracted.startswith("INCORRECT")
        return {"correct": ok, "normalized": extracted, "gold": item["gold"]}

    def buckets(self, item):
        return {"memory_type": item["meta"]["memory_type"]}

    def judge_prompt_provenance(self):
        return {"judge_prompt_version": JUDGE_VERSION, "judge_prompt_sha256": prompt_sha256(EVIDENCE_JUDGE_TEMPLATE)}


class LongTutorDiagnosisAdapter(BenchmarkAdapter):
    name = "longtutor_diagnosis"
    title = "LongTutor - Knowledge State Diagnosis"
    homepage = HOMEPAGE
    description = "根据长历史将当前错误归因为四类知识状态；主指标为 Macro-F1，Accuracy 作为辅助指标。"

    def load_items(self, limit=None, offset=0):
        items = []
        labels = ", ".join(sorted(DIAGNOSES))
        for key, feature, gold in _joined():
            items.append({
                "item_id": key,
                "text": f"{_context(feature)}\n\nChoose exactly one diagnosis: {labels}. Return the label only.",
                "image_paths": [], "gold": gold.get("diagnosis", ""),
                "meta": {"diagnosis": gold.get("diagnosis", "")},
            })
        return items[offset : None if limit is None else offset + limit]

    def extract_answer(self, item, response, client, model):
        low = response.lower()
        found = [label for label in DIAGNOSES if label.lower() in low]
        return found[0] if len(found) == 1 else "NO_LABEL"

    def score(self, extracted, item):
        return {"correct": extracted == item["gold"], "normalized": extracted, "gold": item["gold"]}

    def buckets(self, item):
        return {"diagnosis": item["gold"]}

    def extra_summary(self, scored):
        return multiclass_f1([row.get("gold") for row in scored], [row.get("normalized") for row in scored])


class LongTutorTeachingAdapter(BenchmarkAdapter):
    name = "longtutor_teaching"
    title = "LongTutor - History-aware Teaching Action"
    homepage = HOMEPAGE
    description = (
        "生成利用具体历史证据的自适应教学反馈，由 MiniMax-M3 按 History Utilization、Strategy Alignment、"
        "Coherence、Appropriateness 四维 1-5 分评审。"
    )
    extraction_cache_version = "longtutor-teaching-v2"

    def load_items(self, limit=None, offset=0):
        items = []
        for key, feature, gold in _joined():
            items.append({
                "item_id": key,
                "text": f"{_context(feature)}\n\nProvide concise personalized tutoring. Use specific history, diagnose implicitly, scaffold without revealing the full answer.",
                "image_paths": [], "gold": gold.get("content", ""),
                "meta": {"diagnosis": gold.get("diagnosis", ""), "strategy": gold.get("strategy", "")},
            })
        return items[offset : None if limit is None else offset + limit]

    def extract_answer(self, item, response, client: MiniMaxClient, model):
        prompt = TEACHING_JUDGE_TEMPLATE.format(
            context=item["text"],
            diagnosis=item["meta"]["diagnosis"],
            strategy=item["meta"]["strategy"],
            gold=item["gold"],
            candidate=response,
        )
        return client.chat(
            [{"role": "user", "content": prompt}],
            model=model,
            max_tokens=None,
        )

    def score(self, extracted, item):
        parsed = _json_from_text(extracted) or {}
        keys = ["history_utilization", "strategy_alignment", "coherence", "appropriateness"]
        scores = {}
        for key in keys:
            try:
                scores[key] = max(1, min(5, int(parsed[key])))
            except (KeyError, TypeError, ValueError):
                scores[key] = 0
        valid = all(scores.values())
        return {"correct": valid, "normalized": scores, "gold": item["gold"]}

    def buckets(self, item):
        return {"diagnosis": item["meta"]["diagnosis"], "strategy": item["meta"]["strategy"]}

    def extra_summary(self, scored):
        keys = ["history_utilization", "strategy_alignment", "coherence", "appropriateness"]
        valid = [row.get("normalized") for row in scored if isinstance(row.get("normalized"), dict)]
        averages = {key: round(sum(row.get(key, 0) for row in valid) / len(valid), 3) if valid else 0.0 for key in keys}
        averages["average"] = round(sum(averages.values()) / len(keys), 3)
        return {"judge_scores": averages, "valid_judgements": len(valid)}

    def judge_prompt_provenance(self):
        return {"judge_prompt_version": JUDGE_VERSION, "judge_prompt_sha256": prompt_sha256(TEACHING_JUDGE_TEMPLATE)}
