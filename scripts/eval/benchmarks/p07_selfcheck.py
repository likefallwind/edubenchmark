"""P07 self-check adapter (两轮自查协议, zero new data).

Operationalizes P07 (自我校验与修正) as the standard intrinsic self-correction
protocol: the model answers a question (round 1), then — with no external
feedback and no hint that anything is wrong — is asked to re-examine its own
answer (round 2). Rule scoring on both rounds separates four outcomes:

  wrong -> right   (fixed:   real self-correction)
  right -> wrong   (broken:  harmful second-guessing)
  right -> right / wrong -> wrong (kept)

Reuses the P08 delegate stack (ceval 0-shot / mmlu_pro / agieval /
mtb_problem_solving) and the same pinned difficulty-stratified item list
(``data/p08_calibration/item_list_v1.txt``), so P07 and P08 are measured on the
same items with clean exact-match scoring and zero new annotation.

Mechanics: round 1 is the normal prediction phase. Round 2 happens inside
``extract_answer`` — it calls the *model under test* again (the harness sets
``adapter.model_under_test``; the ``client`` argument is the extractor, a
different model) with the original conversation plus a fixed re-check turn.
Both rounds are reduced to answers by the delegate's own extractor and scored
by the delegate's own ``score``.

Headline: ``score_10 = 10 * [0.5*fix_rate + 0.5*(1-break_rate)]`` — rewards
fixing real errors and not corrupting correct answers; independent of raw
round-1 accuracy by construction (both terms condition on round-1 status).
"""

from __future__ import annotations

import json
import threading
from typing import Any

from ..base import BenchmarkAdapter
from ..minimax_client import MiniMaxClient, text_part
from ..providers import build_client
from .p08_calibration import _SOURCES, P08CalibrationAdapter

_CHECK_ZH = (
    "请重新检查你刚才的解答：逐步验证其中的推理和计算。"
    "如果发现错误，请改正并给出新的答案；如果确认无误，请保持原答案。"
    "最后以与之前相同的格式给出最终答案。"
)
_CHECK_EN = (
    "Please re-examine your previous answer: verify the reasoning and any "
    "calculations step by step. If you find an error, correct it and give the "
    "new answer; if you confirm it is correct, keep it. State your final "
    "answer in the same format as before."
)


class P07SelfCheckAdapter(BenchmarkAdapter):
    name = "p07_selfcheck"
    title = "P07 两轮自查（先答题，再无提示复查，看改对率 vs 改错率）"
    homepage = ""
    description = (
        "P07（自我校验与修正）的直接测量：标准 intrinsic self-correction 协议。"
        "第一轮正常答题；第二轮在同一对话里固定追问“请重新检查你的解答”（不暗示对错），"
        "规则判分分离四种结果：错改对（真自查）、对改错（有害的自我怀疑）、保持不变。\n\n"
        "复用 P08 的 delegate（ceval 0-shot / mmlu_pro / agieval / mtb_problem_solving）"
        "和同一份难度分层 item_list，零新增标注，且 P07/P08 在同一套题上可比。\n\n"
        "headline score_10 = 10×[0.5×改对率 + 0.5×(1−改错率)]，两项都以第一轮状态为条件，"
        "构造上与第一轮正确率解耦（不奖励“题目本来就会”）。"
    )

    def __init__(self) -> None:
        self._p08 = P08CalibrationAdapter()
        self._delegates = self._p08._delegates
        self._mut_client: MiniMaxClient | None = None
        self._mut_lock = threading.Lock()

    # --- items & round-1 prompt: plain delegate protocol -----------------------

    def load_items(self, limit: int | None = None, offset: int = 0) -> list[dict[str, Any]]:
        return self._p08.load_items(limit=limit, offset=offset)

    def build_messages(self, item: dict[str, Any]) -> list[dict[str, Any]]:
        meta = item["meta"]
        src = meta["source_benchmark"]
        orig = meta["delegate_item"]
        if _SOURCES[src].get("zero_shot"):
            return self._p08._ceval_zero_shot(orig)
        return self._delegates[src].build_messages(orig)

    # --- round 2: re-check call to the model under test ------------------------

    def _model_client(self) -> MiniMaxClient:
        with self._mut_lock:
            if self._mut_client is None:
                model = getattr(self, "model_under_test", None)
                if not model:
                    raise RuntimeError(
                        "p07_selfcheck needs the model under test for the round-2 "
                        "re-check call; run via scripts/eval_benchmark.py (it sets "
                        "adapter.model_under_test)"
                    )
                self._mut_client = build_client(model, timeout=300)
            return self._mut_client

    def extract_answer(self, item: dict[str, Any], response: str, client: MiniMaxClient, model: str) -> str:
        meta = item["meta"]
        orig = meta["delegate_item"]
        delegate = self._delegates[meta["source_benchmark"]]
        check = _CHECK_ZH if meta["lang"] == "zh" else _CHECK_EN
        messages = self.build_messages(item) + [
            {"role": "assistant", "content": response},
            {"role": "user", "content": check},
        ]
        mut = self._model_client()
        r2_response = ""
        last_error = ""
        for _ in range(3):
            try:
                r2_response = mut.chat(messages)
                if r2_response:
                    break
            except Exception as exc:  # noqa: BLE001
                last_error = str(exc)[:300]
        try:
            r1 = delegate.extract_answer(orig, response, client, model)
        except Exception:
            r1 = ""
        r2 = ""
        if r2_response:
            try:
                r2 = delegate.extract_answer(orig, r2_response, client, model)
            except Exception:
                r2 = ""
        return json.dumps(
            {"r1": r1, "r2": r2, "r2_response": r2_response, "r2_error": last_error if not r2_response else ""},
            ensure_ascii=False,
        )

    # --- scoring: both rounds via the delegate ---------------------------------

    def score(self, extracted: str, item: dict[str, Any]) -> dict[str, Any]:
        try:
            data = json.loads(extracted)
        except (json.JSONDecodeError, TypeError):
            data = {"r1": extracted, "r2": ""}
        meta = item["meta"]
        orig = meta["delegate_item"]
        delegate = self._delegates[meta["source_benchmark"]]
        res1 = delegate.score(str(data.get("r1") or ""), orig)
        res2 = delegate.score(str(data.get("r2") or ""), orig)
        r2_missing = not (data.get("r2") or "").strip() and not (data.get("r2_response") or "").strip()
        return {
            # headline "correct" = after self-check (round 2)
            "correct": bool(res2["correct"]),
            "normalized": res2["normalized"],
            "gold": res2["gold"],
            "r1_correct": bool(res1["correct"]),
            "r1_normalized": res1["normalized"],
            "changed": res1["normalized"] != res2["normalized"],
            "r2_missing": r2_missing,
            "source_benchmark": meta["source_benchmark"],
        }

    def buckets(self, item: dict[str, Any]) -> dict[str, str]:
        return self._p08.buckets(item)

    # --- self-correction metrics ------------------------------------------------

    def extra_summary(self, scored: list[dict[str, Any]]) -> dict[str, Any]:
        graded = [
            r for r in scored
            if r.get("score_status") == "scored" and not r.get("r2_missing")
        ]
        missing = sum(1 for r in scored if r.get("r2_missing"))
        if not graded:
            return {"headline": "no_round2_responses", "n_round2_missing": missing}
        n = len(graded)
        r1_right = [r for r in graded if r.get("r1_correct")]
        r1_wrong = [r for r in graded if not r.get("r1_correct")]
        fixed = sum(1 for r in r1_wrong if r.get("correct"))
        broken = sum(1 for r in r1_right if not r.get("correct"))
        fix_rate = fixed / len(r1_wrong) if r1_wrong else None
        break_rate = broken / len(r1_right) if r1_right else None
        out: dict[str, Any] = {
            "n_scored_both_rounds": n,
            "n_round2_missing": missing,
            "r1_accuracy": round(len(r1_right) / n, 4),
            "r2_accuracy": round(sum(1 for r in graded if r.get("correct")) / n, 4),
            "net_gain": round((sum(1 for r in graded if r.get("correct")) - len(r1_right)) / n, 4),
            "change_rate": round(sum(1 for r in graded if r.get("changed")) / n, 4),
            "n_r1_wrong": len(r1_wrong),
            "n_fixed_wrong_to_right": fixed,
            "fix_rate": round(fix_rate, 4) if fix_rate is not None else None,
            "n_r1_right": len(r1_right),
            "n_broken_right_to_wrong": broken,
            "break_rate": round(break_rate, 4) if break_rate is not None else None,
        }
        if fix_rate is not None and break_rate is not None:
            out["score_10"] = round(10 * (0.5 * fix_rate + 0.5 * (1 - break_rate)), 3)
        by_src: dict[str, dict[str, int]] = {}
        for r in graded:
            slot = by_src.setdefault(
                str(r.get("source_benchmark")),
                {"n": 0, "r1_correct": 0, "r2_correct": 0, "fixed": 0, "broken": 0},
            )
            slot["n"] += 1
            slot["r1_correct"] += bool(r.get("r1_correct"))
            slot["r2_correct"] += bool(r.get("correct"))
            slot["fixed"] += bool(not r.get("r1_correct") and r.get("correct"))
            slot["broken"] += bool(r.get("r1_correct") and not r.get("correct"))
        out["by_source"] = by_src
        return out
