"""MRBench adapters (C4 deep test: 教学反馈质量 / 错误诊断, D11/D12/D13).

Source: ``sources/datasets/mrbench/MRBench_V2.json`` downloaded by
``scripts/eval/data/fetch_eval_datasets.py --benchmark mrbench`` from
https://github.com/kaushal0494/UnifyingAITutorEvaluation (NAACL 2025,
*Unifying AI Tutor Evaluation: An Evaluation Taxonomy for Pedagogical Ability
Assessment of LLM-Powered AI Tutors*).

MRBench couples each tutor-student dialogue with several models' tutor replies
(Expert, Novice, GPT4, Sonnet, Gemini, Llama-3.1-8B/405B, Mistral, Phi3), each
reply human-annotated on 8 pedagogical dimensions with a 3-way label. This
module exposes two adapters that reuse the existing eval pipeline:

- ``mrbench_judge`` (Step 1 — LLM-as-judge calibration): the **model under test
  IS the judge** (like ``mathtutorbench_judge_calibration``). One item per
  (response × dimension); the judge labels that single dimension; we score the
  label against the human gold and report per-dimension agreement / macro-F1 /
  Cohen's kappa — i.e. how human-like the judge is. No extra judge infra.
- ``mrbench_tutor`` (Step 2 — generation + judge scoring): the model under test
  *generates* the next tutor reply for each dialogue; a **fixed judge**
  (``MRBENCH_JUDGE_MODEL``, default ``glm-5.2``, decoupled from
  ``--extractor-model`` like ``eduguard_adversarial``) then labels the 8
  dimensions of that generated reply, using the v2 rubric (Providing_Guidance
  carries a Stage-3-validated evolved criterion; other dims == v1). Headline metric = pedagogical pass rate
  (key dimensions all "Yes"); full per-dimension label distribution lands in
  ``summary.json`` → ``extra_metrics``.
"""

from __future__ import annotations

import json
import os
import re
import time
from collections import Counter, defaultdict
from typing import Any

from ..base import ROOT, BenchmarkAdapter, prompt_sha256
from ..minimax_client import MiniMaxClient
from ..providers import extraction_max_tokens
from ..scoring import cohen_kappa, multiclass_f1


DATA = ROOT / "sources" / "datasets" / "mrbench" / "MRBench_V2.json"
HOMEPAGE = "https://github.com/kaushal0494/UnifyingAITutorEvaluation"

# Version of the per-dimension judge rubric prompt (_judge_prompt). Bump on any
# wording change; summary.json records it plus the template hash.
JUDGE_PROMPT_VERSION = "v1"

# A judge reply longer than this is treated as verbose reasoning that the plain
# label normalizer may mis-read, so it is routed through the extractor model
# (mirrors mathtutorbench / eduguard_sata long-response branches).
VERBOSE_LEN = 80

# The 8 dimensions, in the dataset's annotation order. Each carries the exact
# canonical label set found in MRBench_V2.json plus a concise definition ported
# from the paper's evaluation taxonomy (§3). ``labels`` is also the option list
# offered to the judge, so it must match the human gold strings verbatim.
DIMENSIONS: dict[str, dict[str, Any]] = {
    "Mistake_Identification": {
        "title": "Mistake Identification",
        "labels": ("Yes", "To some extent", "No"),
        "definition": (
            "Has the tutor recognized that the student made a mistake (or that the "
            "student's latest turn contains an error)?"
        ),
    },
    "Mistake_Location": {
        "title": "Mistake Location",
        "labels": ("Yes", "To some extent", "No"),
        "definition": (
            "Does the tutor's reply point to where exactly the mistake is — the "
            "specific step, quantity, or place the student went wrong?"
        ),
    },
    "Revealing_of_the_Answer": {
        "title": "Revealing of the Answer",
        "labels": ("No", "Yes (and the answer is correct)", "Yes (but the answer is incorrect)"),
        "definition": (
            "Does the tutor reveal the final answer to the student? Choose 'No' if it "
            "does not; otherwise whether the revealed answer is correct or incorrect."
        ),
    },
    "Providing_Guidance": {
        "title": "Providing Guidance",
        "labels": ("Yes", "To some extent", "No"),
        "definition": (
            "Does the tutor provide correct and relevant guidance — a hint, an "
            "explanation, a worked example, a clarifying question, etc.?"
        ),
    },
    "Actionability": {
        "title": "Actionability",
        "labels": ("Yes", "To some extent", "No"),
        "definition": (
            "Is it clear from the tutor's reply what the student should do next? Does "
            "it give the student a concrete next action rather than a dead end?"
        ),
    },
    "Coherence": {
        "title": "Coherence",
        "labels": ("Yes", "To some extent", "No"),
        "definition": (
            "Is the tutor's reply logically coherent with the conversation so far and "
            "internally self-consistent (not contradictory or off-topic)?"
        ),
    },
    "Tutor_Tone": {
        "title": "Tutor Tone",
        "labels": ("Encouraging", "Neutral", "Offensive"),
        "definition": "What is the overall tone of the tutor's reply?",
    },
    "humanlikeness": {
        "title": "Humanlikeness",
        "labels": ("Yes", "To some extent", "No"),
        "definition": (
            "Does the tutor's reply sound natural and human, as opposed to robotic, "
            "templated, or artificial?"
        ),
    },
}

# Dimensions whose "Yes" jointly defines a pedagogically sound reply, used for
# the Step-2 headline pass rate. A coarse proxy (Mistake_* only applies when the
# student actually erred); the full per-dimension distribution is the richer
# signal and lives in extra_metrics.
KEY_DIMENSIONS = ("Mistake_Identification", "Providing_Guidance", "Actionability")


def _read_entries() -> list[dict[str, Any]]:
    if not DATA.exists():
        raise SystemExit(
            f"missing {DATA}; run: python scripts/eval/data/fetch_eval_datasets.py --benchmark mrbench"
        )
    with DATA.open(encoding="utf-8") as fh:
        return json.load(fh)


def _normalize_label(dim: str, text: str) -> str:
    """Map a judge's free-text answer to one of ``dim``'s canonical labels.

    Returns ``"unparsed"`` when nothing matches (tracked in the report so a high
    unparsed rate flags a prompt/format problem).
    """
    low = (text or "").strip().lower()
    if not low:
        return "unparsed"
    if dim == "Revealing_of_the_Answer":
        has_yes = re.search(r"\byes\b", low) is not None
        if "incorrect" in low:
            return "Yes (but the answer is incorrect)"
        if "correct" in low and has_yes:
            return "Yes (and the answer is correct)"
        if re.search(r"\bno\b", low) and not has_yes:
            return "No"
        if has_yes:
            return "Yes (and the answer is correct)"
        if re.search(r"\bno\b", low):
            return "No"
        return "unparsed"
    if dim == "Tutor_Tone":
        for lab in ("Offensive", "Encouraging", "Neutral"):
            if lab.lower() in low:
                return lab
        return "unparsed"
    # Default 3-way Yes / To some extent / No (also covers humanlikeness).
    if re.search(r"to some extent|some extent|partial|somewhat|partly", low):
        return "To some extent"
    if re.search(r"\byes\b", low):
        return "Yes"
    if re.search(r"\bno\b", low):
        return "No"
    return "unparsed"


def _judge_prompt(dim: str, conversation_history: str, response: str) -> str:
    cfg = DIMENSIONS[dim]
    options = " / ".join(cfg["labels"])
    return (
        "You are an expert evaluator of AI math tutors. Judge a single tutor reply "
        "on one pedagogical dimension.\n\n"
        f"Conversation so far:\n{conversation_history}\n\n"
        f"Tutor reply to evaluate:\n{response}\n\n"
        f"Dimension — {cfg['title']}: {cfg['definition']}\n\n"
        f"Choose the single option that best fits. Answer with exactly one of the "
        f"following and nothing else: {options}"
    )


def _judge_prompt_provenance() -> dict[str, Any]:
    templates = [_judge_prompt(dim, "{conversation_history}", "{response}") for dim in DIMENSIONS]
    return {
        "judge_prompt_version": JUDGE_PROMPT_VERSION,
        "judge_prompt_sha256": prompt_sha256(*templates),
    }


# Stage-3-validated evolved rubric addenda (doc/rubric_evolution_plan_2026-07-06.md
# 附录 4). A dimension appears here only if its self-evolved rubric replicated on
# the SEALED test split — Providing_Guidance: glm-5.2 test kappa 0.394 -> 0.508
# (+0.115, sig). These addenda are applied to the FIXED PRODUCTION judge in
# mrbench_tutor ONLY; the mrbench_judge calibration benchmark keeps the v1 prompt
# (it measures a candidate model's judging ability against a fixed rubric, so its
# prompt must not drift). The injection format mirrors the stage1 Renderer._extras
# byte-for-byte, so the shipped production prompt == the prompt validated on test.
_EVOLVED_LABEL_CRITERIA: dict[str, dict[str, str]] = {
    "Providing_Guidance": {
        "To some extent": (
            "The tutor attempts to provide a relevant hint or explanation but "
            "misdiagnoses the student's error or contains a minor flaw, failing "
            "to fully guide the student to the correct solution."
        ),
    },
}
# Bumped because the production (tutor) judge prompt now differs from v1 for the
# evolved dimension(s); all other dimensions remain byte-identical to v1.
PRODUCTION_JUDGE_PROMPT_VERSION = "v2"


def _evolved_judge_prompt(dim: str, conversation_history: str, response: str) -> str:
    """Production judge prompt: v1 base + Stage-3-validated label criteria for the
    evolved dimensions (byte-identical to the stage1 Renderer's evolved render)."""
    base = _judge_prompt(dim, conversation_history, response)
    crit = _EVOLVED_LABEL_CRITERIA.get(dim)
    if not crit:
        return base
    lines = ["Label criteria:"]
    for lab in DIMENSIONS[dim]["labels"]:
        if lab in crit:
            lines.append(f'- "{lab}": {crit[lab]}')
    extras = "\n".join(lines)
    head, tail = base.rsplit("\n\nChoose", 1)
    return f"{head}\n\n{extras}\n\nChoose{tail}"


def _tutor_judge_prompt_provenance() -> dict[str, Any]:
    templates = [_evolved_judge_prompt(dim, "{conversation_history}", "{response}") for dim in DIMENSIONS]
    return {
        "judge_prompt_version": PRODUCTION_JUDGE_PROMPT_VERSION,
        "judge_prompt_sha256": prompt_sha256(*templates),
        "evolved_dimensions": sorted(_EVOLVED_LABEL_CRITERIA),
        "evolved_rubric_source": "doc/rubric_evolution_plan_2026-07-06.md 附录 4",
    }


def _llm_extract(client: MiniMaxClient, model: str, instruction: str, response: str) -> str:
    prompt = f"{instruction}\n\nText:\n---\n{response}\n---\n\nAnswer:"
    return client.chat(
        [{"role": "user", "content": prompt}],
        model=model,
        max_tokens=extraction_max_tokens(model, 512),
    )


# ---------------------------------------------------------------------------
# Step 1: LLM-as-judge calibration — model under test IS the judge
# ---------------------------------------------------------------------------


class MRBenchJudgeAdapter(BenchmarkAdapter):
    name = "mrbench_judge"
    title = "MRBench · Step 1 LLM-as-judge 校准（与人类标注一致性）"
    homepage = HOMEPAGE
    description = (
        "MRBench（NAACL 2025 Unifying AI Tutor Evaluation）的 LLM-as-judge 校准：被测 "
        "--model 本身充当裁判，对数据集中已有人工标注的 tutor 回复逐维度（8 个教学维度）"
        "打标，衡量裁判与人类标注的一致程度。每 (回复 × 维度) 拆成一道题，gold 为该维度的"
        "人工标签，裁判输出三分类标签后与 gold 比对。对应能力维度 D11/D12/D13（C4 深度测试）。\n\n"
        "8 个维度：Mistake Identification / Mistake Location / Revealing of the Answer / "
        "Providing Guidance / Actionability / Coherence / Tutor Tone / Humanlikeness。"
        "Revealing 三档为 No / Yes(correct) / Yes(incorrect)，Tutor Tone 为 "
        "Encouraging/Neutral/Offensive，其余为 Yes / To some extent / No。\n\n"
        "报告“正确率”即逐维度逐题一致率（micro accuracy）；summary.json 的 extra_metrics "
        "按维度给 agreement(accuracy)、macro-F1 与 Cohen's kappa，并给跨维度 macro 平均——"
        "这就是“裁判有多像人”。裁判输出无法归一的记 unparsed（占比应很低）。"
    )

    def load_items(self, limit: int | None = None, offset: int = 0) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        for idx, entry in enumerate(_read_entries()):
            conv = entry.get("conversation_history") or ""
            data = entry.get("Data")
            cid = entry.get("conversation_id", idx)
            for model_name, payload in (entry.get("anno_llm_responses") or {}).items():
                response = (payload or {}).get("response") or ""
                annotation = (payload or {}).get("annotation") or {}
                if not response.strip():
                    continue
                # dimension-major within each (entry, model) so a small --limit
                # naturally covers all 8 dimensions.
                for dim in DIMENSIONS:
                    gold = annotation.get(dim)
                    if gold not in DIMENSIONS[dim]["labels"]:
                        continue  # missing / out-of-vocab human label — skip
                    items.append(
                        {
                            "item_id": f"c{idx}-{model_name}-{dim}",
                            "text": _judge_prompt(dim, conv, response),
                            "image_paths": [],
                            "gold": gold,
                            "meta": {
                                "dimension": dim,
                                "src_model": model_name,
                                "data": data,
                                "conversation_id": cid,
                            },
                        }
                    )
        return items[offset : offset + limit if limit is not None else None]

    def extract_answer(self, item, response, client, model):
        dim = item["meta"]["dimension"]
        resp = (response or "").strip()
        label = _normalize_label(dim, resp)
        if label == "unparsed" and resp and len(resp) > VERBOSE_LEN:
            options = " / ".join(DIMENSIONS[dim]["labels"])
            resp2 = _llm_extract(
                client, model,
                f"The text below is an evaluation judgement. Output only the chosen "
                f"option, exactly one of: {options}.",
                resp,
            )
            label = _normalize_label(dim, resp2)
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
        return {"dimension": item["meta"]["dimension"], "data": str(item["meta"].get("data"))}

    def judge_prompt_provenance(self):
        return _judge_prompt_provenance()

    def extra_summary(self, scored):
        rows = [r for r in scored if r.get("score_status") == "scored"]
        if not rows:
            return {}
        by_dim: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for r in rows:
            by_dim[str(r.get("dimension"))].append(r)

        per_dim: dict[str, Any] = {}
        acc_list, f1_list, kappa_list = [], [], []
        for dim in DIMENSIONS:
            drows = by_dim.get(dim)
            if not drows:
                continue
            golds = [str(r.get("gold_label")) for r in drows]
            preds = [str(r.get("pred_label")) for r in drows]
            agreement = sum(1 for g, p in zip(golds, preds) if g == p) / len(drows)
            f1 = multiclass_f1(golds, preds)["f1_macro"]
            kappa = cohen_kappa(golds, preds)
            unparsed = sum(1 for p in preds if p == "unparsed")
            per_dim[dim] = {
                "n": len(drows),
                "agreement": round(agreement, 4),
                "f1_macro": round(f1, 4),
                "cohen_kappa": round(kappa, 4),
                "unparsed": unparsed,
            }
            acc_list.append(agreement)
            f1_list.append(f1)
            kappa_list.append(kappa)

        def _mean(xs):
            return round(sum(xs) / len(xs), 4) if xs else None

        return {
            "metric": "per-dimension agreement with human gold (accuracy), macro-F1, Cohen's kappa",
            "n_items": len(rows),
            "macro_over_dimensions": {
                "agreement": _mean(acc_list),
                "f1_macro": _mean(f1_list),
                "cohen_kappa": _mean(kappa_list),
            },
            "per_dimension": per_dim,
        }


# ---------------------------------------------------------------------------
# Step 2: generation + fixed-judge scoring
# ---------------------------------------------------------------------------

# Production judge switched MiniMax-M3 -> glm-5.2 (2026-07-10, 待决项③a): glm-5.2
# is the best single judge on the dimension-label lines (judge_research 附录 0:
# test kappa mrbench 0.438 / bea2025 0.406, both above dsv4-pro; M3 is the weakest
# candidate). Override per-run with MRBENCH_JUDGE_MODEL.
DEFAULT_JUDGE_MODEL = "glm-5.2"
JUDGE_MODEL_ENV = "MRBENCH_JUDGE_MODEL"


class MRBenchTutorAdapter(BenchmarkAdapter):
    name = "mrbench_tutor"
    title = "MRBench · Step 2 生成 tutor 回复 + LLM-as-judge 打分"
    homepage = HOMEPAGE
    description = (
        "MRBench Step 2：被测 --model 为每条 tutor-student 对话生成下一句教师回应（引导式、"
        "不直接给答案），再由固定裁判在 8 个教学维度上逐维打标，得到该模型的教学能力画像。"
        "对应能力维度 D11/D12/D13（C4 深度测试）。\n\n"
        "裁判模型固定为 MRBENCH_JUDGE_MODEL（默认 glm-5.2，最佳单裁判；与 --extractor-model/"
        "被测模型解耦，避免 self-judging 偏置），逐维度判定 prompt 为 v2（仅 Providing_Guidance "
        "带 Stage-3 验证过的进化标签准则，其余维度与 v1 一致；标签归一同 Step 1）。\n\n"
        "报告“正确率”为教学合格率：关键维度（Mistake Identification / Providing Guidance / "
        "Actionability）同时为 Yes 的比例（粗粒度代理）。summary.json 的 extra_metrics 给每个"
        "维度的标签分布（Yes / To some extent / No 等占比），是更完整的信号。"
    )

    def load_items(self, limit: int | None = None, offset: int = 0) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        for idx, entry in enumerate(_read_entries()):
            conv = entry.get("conversation_history") or ""
            if not conv.strip():
                continue
            gt = entry.get("Ground_Truth_Solution") or ""
            text = (
                "You are an experienced, supportive math tutor. Read the tutor-student "
                "conversation below and write ONLY the tutor's next reply.\n"
                "Guidelines: identify and locate any mistake the student made, give a "
                "helpful hint or explanation, and make the next step clear. Do NOT reveal "
                "the final answer outright. Keep it concise (1-3 sentences), encouraging, "
                "and natural.\n\n"
                f"Reference solution (for your understanding only — do not quote it verbatim):\n{gt}\n\n"
                f"Conversation so far:\n{conv}\n\n"
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
                        "data": entry.get("Data"),
                        "topic": entry.get("Topic") or "Not Available",
                    },
                }
            )
        return items[offset : offset + limit if limit is not None else None]

    # --- fixed judge resolution (decoupled from the model under test) ----------

    def resolved_judge_model(self, extractor_model: str) -> str | None:
        return os.environ.get(JUDGE_MODEL_ENV) or DEFAULT_JUDGE_MODEL

    def _resolve_judge(self, extractor_client: MiniMaxClient, extractor_model: str):
        judge_model = os.environ.get(JUDGE_MODEL_ENV) or DEFAULT_JUDGE_MODEL
        if judge_model == extractor_model:
            return extractor_client, judge_model
        cached = getattr(self, "_judge_client", None)
        if cached is None or self._judge_client_model != judge_model:
            from ..providers import build_client

            self._judge_client = build_client(judge_model)
            self._judge_client_model = judge_model
        return self._judge_client, judge_model

    @staticmethod
    def _judge_one(client: MiniMaxClient, model: str, dim: str, conv: str, response: str) -> str:
        """Return the judge's raw reply for one dimension.

        The raw text is stored verbatim by ``extract_answer`` and parsed later in
        ``score`` (like longtutor), so a parsing bug is rescore-recoverable and no
        judge output is ever discarded. Raises on API error / empty reply so the
        row is recorded as a retriable error rather than a fake fail.
        """
        prompt = _evolved_judge_prompt(dim, conv, response)
        last_error: Exception = RuntimeError(f"judge failed for dim={dim}")
        for attempt in range(3):
            try:
                reply = client.chat(
                    [{"role": "user", "content": prompt}],
                    model=model,
                    max_tokens=extraction_max_tokens(model, 1024),
                )
            except Exception as exc:  # noqa: BLE001 - retry transient judge/API failures
                last_error = exc
                time.sleep(1.5 * (attempt + 1))
                continue
            if (reply or "").strip():
                return reply.strip()
            last_error = RuntimeError(f"judge returned empty reply for dim={dim}")
            time.sleep(1.5 * (attempt + 1))
        raise last_error

    def extract_answer(self, item, response, client, model):
        client, model = self._resolve_judge(client, model)
        conv = item["meta"]["conversation_history"]
        generated = (response or "").strip()
        dims = list(DIMENSIONS)
        # Sequential on purpose: the runner already parallelises across items via
        # --extract-concurrency, so fanning the 8 dimensions out in parallel here
        # would multiply the real judge concurrency by 8 (6 -> 48) and trip the
        # judge API's rate limit.
        raws = [self._judge_one(client, model, d, conv, generated) for d in dims]
        # Store the judge's raw reply per dimension; parsing happens in score().
        result = {dim: raw for dim, raw in zip(dims, raws)}
        result["judge_model"] = model
        return json.dumps(result, ensure_ascii=False)

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
            {d: _normalize_label(d, str(raw.get(d, ""))) for d in DIMENSIONS}
            if isinstance(raw, dict) and raw
            else {}
        )
        passed = bool(labels) and all(labels.get(d) == "Yes" for d in KEY_DIMENSIONS)
        return {
            "correct": passed,
            "normalized": "pass" if passed else "fail",
            "gold": "pedagogical",
            "judge_labels": labels,
            "judge_model": judge_model,
        }

    def buckets(self, item):
        return {"data": str(item["meta"].get("data")), "topic": str(item["meta"].get("topic"))}

    def judge_prompt_provenance(self):
        return _tutor_judge_prompt_provenance()

    def extra_summary(self, scored):
        rows = [r for r in scored if r.get("score_status") == "scored"]
        judge_model = os.environ.get(JUDGE_MODEL_ENV) or DEFAULT_JUDGE_MODEL
        if not rows:
            return {"judge_model": judge_model, "n": 0}
        per_dim: dict[str, Any] = {}
        for dim in DIMENSIONS:
            dist = Counter(
                str((r.get("judge_labels") or {}).get(dim, "unparsed")) for r in rows
            )
            per_dim[dim] = {
                lab: {"count": c, "share": round(c / len(rows), 4)}
                for lab, c in sorted(dist.items(), key=lambda kv: (-kv[1], kv[0]))
            }
        # A row whose judge reply cannot be mapped on a key dimension is genuinely
        # unparseable (rare); keep it out of the pass-rate denominator rather than
        # counting it as a fail, and report it separately.
        def _key_unparseable(r):
            labs = r.get("judge_labels") or {}
            return any(labs.get(d) == "unparsed" for d in KEY_DIMENSIONS)

        parseable = [r for r in rows if not _key_unparseable(r)]
        passed = sum(1 for r in parseable if r.get("correct"))
        return {
            "judge_model": judge_model,
            "judge_protocol": "fixed LLM-as-judge, per-dimension single label (8 dimensions)",
            "headline_metric": f"pedagogical pass rate = all of {KEY_DIMENSIONS} == 'Yes'",
            "n": len(parseable),
            "n_unparseable_key_dim": len(rows) - len(parseable),
            "pass_rate": round(passed / len(parseable), 4) if parseable else None,
            "per_dimension_distribution": per_dim,
        }
