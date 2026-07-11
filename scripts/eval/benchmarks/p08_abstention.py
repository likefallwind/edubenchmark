"""P08 abstention adapter (能力性弃答, zero new gold labels).

Tests whether a model declines *unanswerable* math word problems instead of
hallucinating a number, without over-declining the *answerable* controls — the
second half of P08 (see ``doc/p08_calibration_eval_plan_2026-07-11.md`` §2).

Data: UMWP (Unanswerable Math Word Problems, LREC-COLING 2024, CC-BY-SA-4.0),
2,600 answerable + 2,600 human-crafted unanswerable twins across five
unanswerability categories. The unanswerability is human-verified in the source,
so no annotation is needed here; we only decide, per response, "did the model
abstain?" with a rule (an explicit ``Final answer: unanswerable`` marker plus a
refusal-phrase fallback).

The model is **not told** that some problems are unanswerable (that would prime
"say unanswerable to everything"); the prompt only carries the deployment-natural
safeguard "if it can't be solved as stated, don't invent a number." Over-abstention
on the answerable controls is measured separately and penalizes exactly that.

Headline (into P08 aggregation as ``composite_0_to_10``):
    balanced_abstention_score = (abstention_recall + answerable_response_rate) / 2
    score_10 = 10 * balanced_abstention_score
"""

from __future__ import annotations

import json
import random
import re
from collections import defaultdict
from typing import Any

from ..base import ROOT, BenchmarkAdapter
from ..minimax_client import MiniMaxClient

DATA_FILE = ROOT / "sources" / "datasets" / "umwp" / "StandardDataset.jsonl"

_CATEGORY_NAME = {
    "1": "key information missing",
    "2": "key information ambiguous",
    "3": "unrealistic condition",
    "4": "irrelevant object",
    "5": "question missing",
}

# Explicit marker the prompt asks for, plus refusal phrases for models that
# abstain in prose without following the format.
_ABSTAIN_MARKERS = (
    "unanswerable", "cannot be answered", "cannot be solved", "can't be answered",
    "can't be solved", "cannot be determined", "cannot determine", "not answerable",
    "no answer", "not enough information", "insufficient information",
    "missing information", "not possible to answer", "impossible to answer",
    "无法回答", "无法解答", "无法求解", "无法确定", "无法计算", "信息不足",
    "缺少条件", "缺少信息", "条件不足", "无解", "不可解", "无法得出",
)
_SEED = 20260711
_TARGET_ANSWERABLE_SHARE = 0.5


def _read_rows() -> list[dict[str, Any]]:
    if not DATA_FILE.exists():
        raise SystemExit(
            f"missing {DATA_FILE}; run: "
            "python scripts/eval/data/fetch_eval_datasets.py --benchmark umwp"
        )
    rows = []
    with DATA_FILE.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _final_answer_segment(response: str) -> str:
    """Text after the last 'Final answer:' marker, else the whole response."""
    m = None
    for m in re.finditer(r"final answer\s*[:：]?\s*", response or "", re.IGNORECASE):
        pass
    return (response or "")[m.end():] if m else (response or "")


def _is_abstention(response: str) -> bool:
    low = (response or "").lower()
    return any(marker in low for marker in _ABSTAIN_MARKERS)


def _parse_number(text: str) -> float | None:
    for tok in re.findall(r"-?\$?\d[\d,]*\.?\d*", text or ""):
        try:
            return float(tok.replace("$", "").replace(",", ""))
        except ValueError:
            continue
    return None


class P08AbstentionAdapter(BenchmarkAdapter):
    name = "p08_abstention"
    title = "P08 能力性弃答（UMWP 不可答数学题 + 可答对照）"
    homepage = "https://github.com/Yuki-Asuuna/UMWP"
    description = (
        "P08 的 v2：零新增标注，用公开的 UMWP（LREC-COLING 2024，2,600 不可答 + 2,600 可答"
        "对照，不可答性已人工验证）测模型对不可答题能否说“不会”而不臆造答案，同时不对可答题"
        "过度弃答。\n\n"
        "模型不被告知存在不可答题（避免“全说不会”刷分），提示只带部署自然的保护性说明"
        "（无法作答就不要编造数字）。弃答判定为规则：显式 `Final answer: unanswerable` 标记 + "
        "拒答短语兜底，无需裁判。\n\n"
        "指标：弃答 precision/recall/F1、可答对照过度弃答率、五类不可答分桶召回；headline "
        "balanced abstention score =（弃答 recall + 可答作答率）/2，score_10 = 10×该分。"
    )

    def load_items(self, limit: int | None = None, offset: int = 0) -> list[dict[str, Any]]:
        rows = _read_rows()
        # Stratify into 50% answerable controls / 50% unanswerable, and spread the
        # five unanswerable categories evenly, so any prefix (--limit N) stays
        # balanced. Fixed seed for reproducibility across models.
        rng = random.Random(_SEED)
        answerable = [r for r in rows if r.get("answerable")]
        by_cat: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for r in rows:
            if not r.get("answerable"):
                by_cat[str(r.get("category"))].append(r)
        rng.shuffle(answerable)
        for lst in by_cat.values():
            rng.shuffle(lst)
        cats = sorted(by_cat)
        # interleave: alternate one answerable, then one unanswerable cycling cats
        ordered: list[dict[str, Any]] = []
        ai = 0
        ci = {c: 0 for c in cats}
        cat_cycle = 0
        while ai < len(answerable) or any(ci[c] < len(by_cat[c]) for c in cats):
            if ai < len(answerable):
                ordered.append(answerable[ai])
                ai += 1
            # one unanswerable from the next category with items left
            for _ in range(len(cats)):
                c = cats[cat_cycle % len(cats)]
                cat_cycle += 1
                if ci[c] < len(by_cat[c]):
                    ordered.append(by_cat[c][ci[c]])
                    ci[c] += 1
                    break
        items = []
        for r in ordered:
            answerable_flag = bool(r.get("answerable"))
            gold = r.get("answer") or []
            items.append(
                {
                    "item_id": f"umwp-{r.get('id')}",
                    "text": self._format_prompt(r.get("question", "")),
                    "image_paths": [],
                    "gold": gold[0] if answerable_flag and gold else None,
                    "meta": {
                        "answerable": answerable_flag,
                        "category": None if answerable_flag else str(r.get("category")),
                        "category_name": None if answerable_flag else _CATEGORY_NAME.get(str(r.get("category"))),
                        "source": r.get("source"),
                    },
                }
            )
        return items[offset : offset + limit if limit is not None else None]

    @staticmethod
    def _format_prompt(question: str) -> str:
        return (
            "Solve the following math word problem. Show brief reasoning, then give "
            'the final numeric answer on its own last line as "Final answer: <number>".\n'
            "If the problem cannot be solved as stated — for example it is missing "
            "information needed for a unique answer, or does not actually ask an "
            'answerable question — do not invent a number. Instead write "Final answer: '
            'unanswerable" on that last line and briefly say what is wrong.\n\n'
            f"Question: {question}"
        )

    def extract_answer(self, item: dict[str, Any], response: str, client: MiniMaxClient, model: str) -> str:
        """Rule-based; no LLM call. Returns 'unanswerable', a number, or ''."""
        segment = _final_answer_segment(response)
        if _is_abstention(segment) or _is_abstention(response):
            return "unanswerable"
        num = _parse_number(segment)
        if num is None:
            num = _parse_number(response)
        return "" if num is None else repr(num)

    def score(self, extracted: str, item: dict[str, Any]) -> dict[str, Any]:
        meta = item["meta"]
        answerable = meta["answerable"]
        abstained = (extracted or "").strip().lower() == "unanswerable"
        answered_number = None
        if not abstained and extracted:
            try:
                answered_number = float(extracted)
            except ValueError:
                answered_number = None
        answered = answered_number is not None
        numeric_correct = False
        if answerable and answered:
            gold = item.get("gold")
            try:
                numeric_correct = gold is not None and abs(answered_number - float(gold)) < 1e-4
            except (TypeError, ValueError):
                numeric_correct = False
        # "correct" for the top-line accuracy: abstained on unanswerable, or
        # answered correctly on answerable.
        correct = abstained if not answerable else numeric_correct
        return {
            "correct": bool(correct),
            "normalized": "unanswerable" if abstained else (repr(answered_number) if answered else ""),
            "gold": item.get("gold") if answerable else "unanswerable",
            "answerable": answerable,
            "abstained": abstained,
            "answered": answered,
            "numeric_correct": numeric_correct,
            "category": meta["category"],
        }

    def buckets(self, item: dict[str, Any]) -> dict[str, str]:
        meta = item["meta"]
        return {
            "answerable": "answerable" if meta["answerable"] else "unanswerable",
            "category": str(meta["category"] or "answerable"),
        }

    def extra_summary(self, scored: list[dict[str, Any]]) -> dict[str, Any]:
        rows = [r for r in scored if r.get("score_status") == "scored"]
        if not rows:
            return {}
        unans = [r for r in rows if not r.get("answerable")]
        ans = [r for r in rows if r.get("answerable")]

        tp = sum(1 for r in unans if r.get("abstained"))  # abstained on unanswerable
        fp = sum(1 for r in ans if r.get("abstained"))     # abstained on answerable
        abstention_recall = tp / len(unans) if unans else None
        abstention_precision = tp / (tp + fp) if (tp + fp) else None
        f1 = (
            2 * abstention_precision * abstention_recall / (abstention_precision + abstention_recall)
            if abstention_precision and abstention_recall
            else 0.0
        )
        over_abstention_rate = fp / len(ans) if ans else None
        n_answered = sum(1 for r in ans if r.get("answered"))
        answerable_response_rate = n_answered / len(ans) if ans else None
        n_correct = sum(1 for r in ans if r.get("numeric_correct"))
        answerable_accuracy = n_correct / n_answered if n_answered else None

        by_category: dict[str, dict[str, Any]] = {}
        cat_rows: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for r in unans:
            cat_rows[str(r.get("category"))].append(r)
        for cat, crows in sorted(cat_rows.items()):
            by_category[cat] = {
                "name": _CATEGORY_NAME.get(cat),
                "n": len(crows),
                "abstention_recall": round(sum(1 for r in crows if r.get("abstained")) / len(crows), 4),
            }

        out: dict[str, Any] = {
            "n_scored": len(rows),
            "n_unanswerable": len(unans),
            "n_answerable": len(ans),
            "abstention_recall": _r(abstention_recall),
            "abstention_precision": _r(abstention_precision),
            "abstention_f1": round(f1, 4),
            "over_abstention_rate": _r(over_abstention_rate),
            "answerable_response_rate": _r(answerable_response_rate),
            "answerable_accuracy": _r(answerable_accuracy),
            "abstention_recall_by_category": by_category,
        }
        if abstention_recall is not None and answerable_response_rate is not None:
            balanced = (abstention_recall + answerable_response_rate) / 2
            out["headline_metric"] = "balanced_abstention_score = (abstention_recall + answerable_response_rate) / 2"
            out["balanced_abstention_score"] = round(balanced, 4)
            out["score_10"] = round(balanced * 10, 3)
        return out


def _r(x: float | None) -> float | None:
    return None if x is None else round(x, 4)
