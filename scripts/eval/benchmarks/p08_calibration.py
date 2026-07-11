"""P08 calibration adapter (置信度校准, zero new gold labels).

Measures whether a model's *self-reported confidence* tracks its actual
correctness — the operationalization of P08's "自信地教错" failure mode (see
``doc/p08_calibration_eval_plan_2026-07-11.md`` §1). It reuses existing
exact-match / rule-scored benchmarks (ceval, mmlu_pro, agieval,
mathtutorbench_problem_solving) so no new annotation is needed:

  1. append a fixed confidence-elicitation suffix to each delegate prompt;
  2. the delegate's own ``extract_answer`` / ``score`` decide correctness;
  3. the model's verbalized confidence is parsed separately;
  4. ``extra_summary`` computes CWR / ECE / Brier / AUROC / selective accuracy
     and a headline ``score_10 = 10 * [0.5*(1-CWR) + 0.5*AUROC]``.

Items are selected by the difficulty-stratified sampler
``scripts/eval/data/build_p08_item_list.py`` and pinned via ``--item-list``
(composite ids ``<source>::<native_id>``), so every model runs the same set and
the ensemble difficulty never leaks the model-under-test's own errors.

ceval is run **0-shot** here (its official 5-shot answer-only protocol primes a
bare letter, which fights the confidence format); this run does **not** back-fill
ceval's own P05/P06 evidence.
"""

from __future__ import annotations

import json
import math
import re
from typing import Any

from ..base import BenchmarkAdapter
from ..minimax_client import MiniMaxClient, text_part
from .agieval import AGIEvalAdapter
from .ceval import CEvalAdapter
from .mathtutorbench import MTBProblemSolving
from .mmlu_pro import MMLUProAdapter

# source name -> (delegate class, per-source language or "item").
_SOURCES: dict[str, dict[str, Any]] = {
    "ceval": {"cls": CEvalAdapter, "lang": "zh", "zero_shot": True},
    "mmlu_pro": {"cls": MMLUProAdapter, "lang": "en"},
    "agieval": {"cls": AGIEvalAdapter, "lang": "item"},
    "mtb_problem_solving": {"cls": MTBProblemSolving, "lang": "en"},
}

_SUFFIX_ZH = (
    "\n\n给出答案后，请在最后另起一行给出你对该答案正确性的置信度"
    "（0-100 的整数，越高表示越确定）。该行格式严格为：\n置信度: <0-100 的整数>"
)
_SUFFIX_EN = (
    "\n\nAfter giving your answer, add a final line reporting your confidence that "
    "the answer is correct, as an integer from 0 to 100 (higher = more certain). "
    "Format that line exactly as:\nConfidence: <0-100>"
)

_CONF_RE = re.compile(r"(?:置信度|信心|confidence)\D{0,6}(\d{1,3})", re.IGNORECASE)
_ANSWER_LINE_RE = re.compile(r"^\s*(?:答案|answer)\s*[:：]\s*(.+?)\s*$", re.IGNORECASE | re.MULTILINE)

_CEVAL_LETTERS = ("A", "B", "C", "D")


def parse_confidence(response: str) -> int | None:
    """Last verbalized confidence 0-100 in the response, or None if unparsable.

    We take the *last* match so a stray number in the reasoning is overridden by
    the final ``Confidence:`` line. Values outside 0-100 are rejected (None), not
    clamped, so a malformed reply is counted as unparsed rather than silently
    coerced (which would bias ECE)."""
    matches = _CONF_RE.findall(response or "")
    if not matches:
        return None
    val = int(matches[-1])
    return val if 0 <= val <= 100 else None


def _answer_source(response: str) -> str:
    """Prefer an explicit ``答案:/Answer:`` line as the answer text; otherwise the
    whole response (so the delegate's native format parsing still applies)."""
    m = None
    for m in _ANSWER_LINE_RE.finditer(response or ""):
        pass  # keep the last one
    return m.group(1) if m else (response or "")


class P08CalibrationAdapter(BenchmarkAdapter):
    name = "p08_calibration"
    title = "P08 置信度校准（复用 exact-match benchmark + verbalized confidence）"
    homepage = ""
    description = (
        "P08（置信度校准与弃答）的 v1：零新增标注。复用 ceval / mmlu_pro / agieval / "
        "mathtutorbench_problem_solving 的既有判分，在原题后追加置信度诱导，测模型自报置信度"
        "与实际对错的一致性——即“自信地教错”这一最致命失效模式的直接测量。\n\n"
        "题目由难度分层抽样器（依据既有 scored.jsonl 的集成难度，easy/mixed/hard≈30/50/20）"
        "固定成一份 item_list，所有模型经 --item-list 跑同一套题，保证跨模型可比与公平"
        "（难度来自历史模型集成，绝不用被测模型自身错题）。\n\n"
        "指标：CWR（高置信错答率）、ECE、Brier、AUROC、选择性准确率；headline "
        "score_10 = 10×[0.5×(1−CWR)+0.5×AUROC]，与纯正确率可分离。难度加权集上的绝对值"
        "仅用于模型间相对比较，不作自然分布下的绝对宣称。"
    )

    def __init__(self) -> None:
        self._delegates: dict[str, BenchmarkAdapter] = {
            src: cfg["cls"]() for src, cfg in _SOURCES.items()
        }

    # --- item loading: union of delegates, namespaced ids ----------------------

    def load_items(self, limit: int | None = None, offset: int = 0) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        for src, cfg in _SOURCES.items():
            delegate = self._delegates[src]
            try:
                native = delegate.load_items(limit=None, offset=0)
            except SystemExit:
                # delegate data not materialized; skip this source gracefully
                continue
            for orig in native:
                lang = cfg["lang"]
                if lang == "item":
                    lang = str((orig.get("meta") or {}).get("language") or "en")
                items.append(
                    {
                        "item_id": f"{src}::{orig['item_id']}",
                        "text": orig.get("text", ""),
                        "image_paths": [],
                        "gold": orig.get("gold"),
                        "meta": {
                            "source_benchmark": src,
                            "lang": lang,
                            "delegate_item": orig,
                        },
                    }
                )
        return items[offset : offset + limit if limit is not None else None]

    # --- prompt: delegate build + confidence suffix ----------------------------

    def _ceval_zero_shot(self, orig: dict[str, Any]) -> list[dict[str, Any]]:
        meta = orig.get("meta") or {}
        subject_zh = meta.get("subject_zh") or ""
        instruction = f"以下是中国关于{subject_zh}考试的单项选择题，请选出其中的正确答案。"
        question = orig.get("text", "").rsplit("\n答案：", 1)[0]
        user = (
            f"{instruction}\n\n{question}\n\n"
            "请先给出正确选项字母（A/B/C/D）。"
        )
        return [{"role": "user", "content": user}]

    def build_messages(self, item: dict[str, Any]) -> list[dict[str, Any]]:
        meta = item["meta"]
        src = meta["source_benchmark"]
        orig = meta["delegate_item"]
        if _SOURCES[src].get("zero_shot"):
            messages = self._ceval_zero_shot(orig)
        else:
            messages = self._delegates[src].build_messages(orig)
        suffix = _SUFFIX_ZH if meta["lang"] == "zh" else _SUFFIX_EN
        self._append_suffix(messages, suffix)
        return messages

    @staticmethod
    def _append_suffix(messages: list[dict[str, Any]], suffix: str) -> None:
        """Append the confidence suffix to the final user turn, handling both
        string and content-list message shapes used across delegates."""
        for msg in reversed(messages):
            if msg.get("role") != "user":
                continue
            content = msg.get("content")
            if isinstance(content, str):
                msg["content"] = content + suffix
            elif isinstance(content, list):
                content.append(text_part(suffix))
            else:
                msg["content"] = suffix
            return
        messages.append({"role": "user", "content": suffix})

    # --- extraction: delegate answer + parsed confidence, packed together ------

    def extract_answer(self, item: dict[str, Any], response: str, client: MiniMaxClient, model: str) -> str:
        meta = item["meta"]
        orig = meta["delegate_item"]
        delegate = self._delegates[meta["source_benchmark"]]
        confidence = parse_confidence(response)
        ans_src = _answer_source(response)
        try:
            answer = delegate.extract_answer(orig, ans_src, client, model)
        except Exception:
            answer = ""
        return json.dumps({"a": answer, "c": confidence}, ensure_ascii=False)

    # --- scoring: delegate correctness + confidence ----------------------------

    def score(self, extracted: str, item: dict[str, Any]) -> dict[str, Any]:
        try:
            data = json.loads(extracted) if extracted.strip().startswith("{") else {"a": extracted, "c": None}
        except (json.JSONDecodeError, AttributeError):
            data = {"a": extracted, "c": None}
        meta = item["meta"]
        orig = meta["delegate_item"]
        delegate = self._delegates[meta["source_benchmark"]]
        result = delegate.score(str(data.get("a") or ""), orig)
        result["confidence"] = data.get("c")
        result["source_benchmark"] = meta["source_benchmark"]
        return result

    def buckets(self, item: dict[str, Any]) -> dict[str, str]:
        meta = item["meta"]
        return {"source_benchmark": meta["source_benchmark"], "language": meta["lang"]}

    # --- calibration metrics ---------------------------------------------------

    def extra_summary(self, scored: list[dict[str, Any]]) -> dict[str, Any]:
        graded = [r for r in scored if r.get("score_status") == "scored"]
        if not graded:
            return {}
        pairs = [
            (int(r["confidence"]), bool(r.get("correct")))
            for r in graded
            if r.get("confidence") is not None
        ]
        unparsed = sum(1 for r in graded if r.get("confidence") is None)
        out: dict[str, Any] = {
            "n_scored": len(graded),
            "n_with_confidence": len(pairs),
            "confidence_unparsed_rate": round(unparsed / len(graded), 4),
            "accuracy": round(sum(1 for r in graded if r.get("correct")) / len(graded), 4),
        }
        if unparsed / len(graded) > 0.10:
            out["confidence_protocol_warning"] = (
                "unparsed confidence rate > 10% — protocol may not fit this model; inspect samples"
            )
        if not pairs:
            out["headline"] = "no_confidence_parsed"
            return out

        confs = [c for c, _ in pairs]
        corrects = [y for _, y in pairs]
        cwr = _cwr(pairs, threshold=90)
        auroc = _auroc(confs, corrects)
        out.update(
            confidence_mean=round(sum(confs) / len(confs), 2),
            confidence_std=round(_std(confs), 2),
            confidence_histogram=_histogram(confs),
            cwr_at_90=None if cwr is None else round(cwr, 4),
            n_high_confidence=sum(1 for c in confs if c >= 90),
            ece_10bin=round(_ece(pairs), 4),
            brier=round(_brier(pairs), 4),
            auroc=None if auroc is None else round(auroc, 4),
            selective_accuracy=_selective_accuracy(pairs),
            by_source=_by_source(graded),
        )
        # headline: penalize confident-wrong (CWR), reward knowing-what-you-dont
        # (AUROC). If no high-confidence items exist CWR is undefined -> fall back
        # to AUROC alone and flag it.
        auroc_term = 0.5 if auroc is None else auroc
        if cwr is None:
            score_10 = 10.0 * auroc_term
            out["headline_note"] = "no items with confidence>=90; CWR undefined, headline = 10*AUROC"
        else:
            score_10 = 10.0 * (0.5 * (1 - cwr) + 0.5 * auroc_term)
        out["headline_metric"] = "score_10 = 10 * [0.5*(1-CWR@90) + 0.5*AUROC]"
        out["score_10"] = round(score_10, 3)
        return out


# --- metric helpers (stdlib only) ---------------------------------------------


def _std(xs: list[float]) -> float:
    if len(xs) < 2:
        return 0.0
    mean = sum(xs) / len(xs)
    return math.sqrt(sum((x - mean) ** 2 for x in xs) / len(xs))


def _histogram(confs: list[int], n_bins: int = 10) -> dict[str, int]:
    hist = {f"{10 * b}-{10 * b + 9}": 0 for b in range(n_bins)}
    keys = list(hist)
    for c in confs:
        b = min(c // 10, n_bins - 1)
        hist[keys[b]] += 1
    return hist


def _cwr(pairs: list[tuple[int, bool]], threshold: int = 90) -> float | None:
    high = [y for c, y in pairs if c >= threshold]
    if not high:
        return None
    return sum(1 for y in high if not y) / len(high)


def _ece(pairs: list[tuple[int, bool]], n_bins: int = 10) -> float:
    n = len(pairs)
    total = 0.0
    for b in range(n_bins):
        lo, hi = b / n_bins, (b + 1) / n_bins
        # last bin is closed on the right so confidence 100 lands in [0.9, 1.0]
        in_bin = [
            (c / 100.0, y)
            for c, y in pairs
            if (lo <= c / 100.0 < hi) or (b == n_bins - 1 and c / 100.0 == 1.0)
        ]
        if not in_bin:
            continue
        acc = sum(1 for _, y in in_bin if y) / len(in_bin)
        conf = sum(p for p, _ in in_bin) / len(in_bin)
        total += (len(in_bin) / n) * abs(acc - conf)
    return total


def _brier(pairs: list[tuple[int, bool]]) -> float:
    return sum((c / 100.0 - (1.0 if y else 0.0)) ** 2 for c, y in pairs) / len(pairs)


def _auroc(confs: list[int], corrects: list[bool]) -> float | None:
    """AUROC of confidence discriminating correct (positive) from wrong, via the
    Mann-Whitney rank statistic with average ranks for ties."""
    pos = sum(1 for y in corrects if y)
    neg = len(corrects) - pos
    if pos == 0 or neg == 0:
        return None
    order = sorted(range(len(confs)), key=lambda i: confs[i])
    ranks = [0.0] * len(confs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and confs[order[j + 1]] == confs[order[i]]:
            j += 1
        avg_rank = (i + j) / 2.0 + 1.0  # ranks are 1-based
        for k in range(i, j + 1):
            ranks[order[k]] = avg_rank
        i = j + 1
    sum_ranks_pos = sum(ranks[i] for i in range(len(confs)) if corrects[i])
    return (sum_ranks_pos - pos * (pos + 1) / 2.0) / (pos * neg)


def _selective_accuracy(pairs: list[tuple[int, bool]]) -> dict[str, float | None]:
    """Accuracy when keeping the top X% most-confident items (deployment: route
    low-confidence answers to a human)."""
    ordered = sorted(pairs, key=lambda p: p[0], reverse=True)
    out: dict[str, float | None] = {}
    for cov in (0.9, 0.8, 0.7):
        k = max(1, int(round(len(ordered) * cov)))
        kept = ordered[:k]
        out[f"coverage_{int(cov * 100)}"] = round(sum(1 for _, y in kept if y) / len(kept), 4)
    return out


def _by_source(graded: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    by: dict[str, list[dict[str, Any]]] = {}
    for r in graded:
        by.setdefault(str(r.get("source_benchmark") or (r.get("buckets") or {}).get("source_benchmark") or "?"), []).append(r)
    out: dict[str, dict[str, Any]] = {}
    for src, rows in sorted(by.items()):
        pairs = [(int(r["confidence"]), bool(r.get("correct"))) for r in rows if r.get("confidence") is not None]
        cwr = _cwr(pairs) if pairs else None
        auroc = _auroc([c for c, _ in pairs], [y for _, y in pairs]) if pairs else None
        out[src] = {
            "n": len(rows),
            "accuracy": round(sum(1 for r in rows if r.get("correct")) / len(rows), 4),
            "n_with_confidence": len(pairs),
            "cwr_at_90": None if cwr is None else round(cwr, 4),
            "auroc": None if auroc is None else round(auroc, 4),
        }
    return out
