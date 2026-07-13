"""K12Vista adapter (P04 复杂多模态理解 / 中文 K12 学科图文推理).

Source: ``lipku1999/K12-Vista`` (33,660 items, five subjects × grades 6/9/12,
three question types) + the official code checkout under
``sources/datasets/k12vista/`` (github.com/lichongod/K12Vista, arXiv 2506.01676).

Protocol is ported from the official repo, not reinvented:

* **Prompt** — ``prompt.py::infer_prompt['directly_infer_prompt'][type]``, one
  per question type. The official runner strips the ``<image>`` placeholder from
  the question and puts the image *before* the text (``models/vllminfer.py``); we
  do the same.
* **Scoring** — ``prompt.py::eval_prompt['directly_eval_prompt'][type]`` drives an
  LLM judge that extracts the reference-answer list and the student-answer list
  blank by blank and emits a 0/1 list. Item score = mean of that list, i.e.
  **partial credit per blank** (``models/K12_PEM_judgemodel.py``). The official
  judge is Qwen2.5-VL-72B or the fine-tuned K12-PEM; both are GPU-served, so here
  the judge is an API model (``K12VISTA_JUDGE_MODEL``, else the extractor model) —
  the rubric text is unchanged but the judge is *not* the official one, and the
  judge itself is unvalidated against human labels. Declare that in any report.

Headline ``accuracy`` is the strict full-credit rate (every blank right); the
official partial-credit mean is ``extra_metrics.official_score`` (with
``score_10`` = 10× that for the capability aggregation).

Items are the pinned 300-item stratified sample (``data/k12vista/item_list_v1.txt``);
see ``scripts/eval/data/build_k12vista_sample.py``.
"""

from __future__ import annotations

import ast
import json
import os
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

from ..base import ROOT, BenchmarkAdapter, prompt_sha256
from ..minimax_client import MiniMaxClient, image_part, text_part
from ..providers import build_client, extraction_max_tokens


SRC_DIR = ROOT / "sources" / "datasets" / "k12vista"
PROMPT_FILE = SRC_DIR / "K12_Vista" / "code" / "prompt.py"
SAMPLE_JSONL = SRC_DIR / "K12_Vista" / "data" / "sample_v1.jsonl"
IMAGE_DIR = SRC_DIR / "images"
ITEM_LIST = ROOT / "data" / "k12vista" / "item_list_v1.txt"

JUDGE_MODEL_ENV = "K12VISTA_JUDGE_MODEL"


def _load_official_prompts() -> tuple[dict[str, str], dict[str, str]]:
    """Load the official infer/eval prompt tables straight from the repo file."""
    if not PROMPT_FILE.exists():
        raise SystemExit(
            f"missing {PROMPT_FILE}\n"
            "run: python scripts/eval/data/fetch_eval_datasets.py --benchmark k12vista"
        )
    namespace: dict[str, Any] = {}
    exec(compile(PROMPT_FILE.read_text(encoding="utf-8"), str(PROMPT_FILE), "exec"), namespace)
    return namespace["infer_prompt"]["directly_infer_prompt"], namespace["eval_prompt"]["directly_eval_prompt"]


class K12VistaAdapter(BenchmarkAdapter):
    name = "k12vista"
    title = "K12Vista：中文 K12 多模态学科理解与推理"
    homepage = "https://github.com/lichongod/K12Vista"
    description = (
        "K12Vista 是目前规模最大的中文 K12 多模态学科基准：33,660 道题，覆盖数学、物理、"
        "化学、生物、地理五个学科与小学/初中/高中三个学段，题型含选择题、填空题、问答题，"
        "每题都带一张学科图（几何图、电路图、实验装置、函数曲线、地图等），必须先看懂图才能作答。"
        "对应本仓库能力 P04（复杂多模态理解），也是中文多模态的短板补位。\n\n"
        "本次评测使用固定抽样题单（300 题，按题型×学科×难度分层，见 "
        "data/k12vista/item_list_v1.txt），所有模型跑同一份题，保证横向可比。\n\n"
        "提示词与判分口径均照搬官方仓库：作答走官方 directly_infer_prompt（按题型分三种），"
        "判分走官方 directly_eval_prompt——裁判逐空提取参考答案与学生答案并给 0/1，"
        "题分＝各空得分均值（多空题部分给分）。表头 accuracy 是严格全对率，官方口径的"
        "部分给分均值在 extra_metrics.official_score。\n\n"
        "注意：官方裁判是 GPU 部署的 Qwen2.5-VL-72B / K12-PEM，本地无法复现，此处改用 API 裁判"
        "（K12VISTA_JUDGE_MODEL），rubric 文本未改但裁判模型不是官方那一个，且该裁判未经人工金标校准。"
    )

    def __init__(self) -> None:
        self._infer_prompts: dict[str, str] | None = None
        self._eval_prompts: dict[str, str] | None = None
        self._judge_client: MiniMaxClient | None = None
        self._judge_model: str | None = None

    def _prompts(self) -> tuple[dict[str, str], dict[str, str]]:
        if self._infer_prompts is None or self._eval_prompts is None:
            self._infer_prompts, self._eval_prompts = _load_official_prompts()
        return self._infer_prompts, self._eval_prompts

    def load_items(self, limit: int | None = None, offset: int = 0) -> list[dict[str, Any]]:
        if not SAMPLE_JSONL.exists():
            raise SystemExit(
                f"missing {SAMPLE_JSONL}\n"
                "run: python scripts/eval/data/build_k12vista_sample.py --size 300"
            )
        pinned = [ln.strip() for ln in ITEM_LIST.read_text(encoding="utf-8").splitlines() if ln.strip()]
        order = {h: i for i, h in enumerate(pinned)}
        records = {}
        with SAMPLE_JSONL.open(encoding="utf-8") as fh:
            for line in fh:
                rec = json.loads(line)
                records[rec["hash_id"]] = rec

        infer_prompts, _ = self._prompts()
        items: list[dict[str, Any]] = []
        for hash_id in sorted(records, key=lambda h: order.get(h, len(order))):
            rec = records[hash_id]
            qtype = rec["type"]
            # Official: format the question into the per-type template, then drop
            # the <image> placeholder (the image travels as its own content part).
            text = infer_prompts[qtype].format(question=rec["question"]).replace("<image>", "")
            image = IMAGE_DIR / f"{hash_id}.jpg"
            answer = rec["format_answer"]
            items.append(
                {
                    "item_id": hash_id,
                    "text": text,
                    "image_paths": [image] if image.exists() else [],
                    "gold": answer["ground_truth"],
                    "meta": {
                        "question": rec["question"],
                        "type": qtype,
                        "subject": rec["subject"],
                        "grade": rec["subject"].split("-")[-1],
                        "difficulty": rec.get("difficulty", ""),
                        "solution": answer.get("format_solution", []),
                        "knowledge_point": rec.get("knowledge_point", []),
                    },
                }
            )
        return items[offset : offset + limit if limit is not None else None]

    def build_messages(self, item: dict[str, Any]) -> list[dict[str, Any]]:
        # Official order: image first, then the prompt text.
        content: list[dict[str, Any]] = [image_part(Path(p)) for p in item.get("image_paths") or []]
        content.append(text_part(item["text"]))
        return [{"role": "user", "content": content}]

    def _judge(self, extractor: MiniMaxClient, extractor_model: str) -> tuple[MiniMaxClient, str]:
        """Judge model is decoupled from the model under test (like eduguard_adversarial)."""
        if self._judge_client is None:
            model = os.environ.get(JUDGE_MODEL_ENV) or os.environ.get("JUDGE_MODEL") or extractor_model
            self._judge_model = model
            self._judge_client = extractor if model == extractor_model else build_client(model)
        return self._judge_client, str(self._judge_model)

    @staticmethod
    def _parse_evaluation(reply: str) -> list[Any] | None:
        """Official parse: the judge wraps a 3-element python list in <evaluation> tags."""
        match = re.search(r"<evaluation>(.*?)</evaluation>", reply or "", re.S)
        blob = match.group(1) if match else (reply or "")
        start, end = blob.find("["), blob.rfind("]")
        if start == -1 or end <= start:
            return None
        try:
            parsed = ast.literal_eval(blob[start : end + 1])
        except (ValueError, SyntaxError):
            return None
        if not isinstance(parsed, list) or len(parsed) != 3 or not isinstance(parsed[2], list):
            return None
        return parsed

    def extract_answer(self, item: dict[str, Any], response: str, client: MiniMaxClient, model: str) -> str:
        meta = item["meta"]
        _, eval_prompts = self._prompts()
        judge_client, judge_model = self._judge(client, model)
        prompt = eval_prompts[meta["type"]].format(
            question=meta["question"],
            answer=item["gold"],
            solution=meta["solution"],
            student_answer=(response or "").strip(),
        )
        reply = judge_client.chat(
            [{"role": "user", "content": prompt}],
            model=judge_model,
            max_tokens=extraction_max_tokens(judge_model, 2048),
        )
        parsed = self._parse_evaluation(reply)
        if parsed is None:
            return json.dumps({"score": 0.0, "unparsed": True, "judge_model": judge_model}, ensure_ascii=False)

        refs, student, marks = parsed
        # Official K12_PEM_judgemodel: every mark must be 0/1, score = mean(marks).
        try:
            values = [int(m) for m in marks]
        except (TypeError, ValueError):
            return json.dumps({"score": 0.0, "unparsed": True, "judge_model": judge_model}, ensure_ascii=False)
        if not values or any(v not in (0, 1) for v in values):
            return json.dumps({"score": 0.0, "unparsed": True, "judge_model": judge_model}, ensure_ascii=False)

        return json.dumps(
            {
                "score": sum(values) / len(values),
                "marks": values,
                "refs": refs,
                "student": student,
                "unparsed": False,
                "judge_model": judge_model,
            },
            ensure_ascii=False,
        )

    def score(self, extracted: str, item: dict[str, Any]) -> dict[str, Any]:
        try:
            judgement = json.loads(extracted)
        except (json.JSONDecodeError, TypeError):
            judgement = {"score": 0.0, "unparsed": True}
        value = float(judgement.get("score") or 0.0)
        return {
            # Headline accuracy = strict full credit (every blank right).
            "correct": value >= 1.0,
            "normalized": judgement.get("student"),
            "gold": item.get("gold"),
            "item_score": value,
            "n_blanks": len(judgement.get("marks") or []),
            "unparsed": bool(judgement.get("unparsed")),
            "judge_model": judgement.get("judge_model"),
        }

    def buckets(self, item: dict[str, Any]) -> dict[str, str]:
        meta = item["meta"]
        return {
            "type": str(meta.get("type")),
            "subject": str(meta.get("subject")),
            "grade": str(meta.get("grade")),
            "difficulty": str(meta.get("difficulty")),
        }

    def extra_summary(self, scored: list[dict[str, Any]]) -> dict[str, Any]:
        # Same denominator as the runner's headline accuracy: rows that actually
        # got judged. API failures are reported separately, not scored as zeros.
        rows = [r for r in scored if r.get("score_status") == "scored"]
        if not rows:
            return {}

        def mean(subset: list[dict[str, Any]]) -> float:
            return round(sum(float(r.get("item_score") or 0.0) for r in subset) / len(subset), 4)

        by: dict[str, dict[str, list[dict[str, Any]]]] = {
            axis: defaultdict(list) for axis in ("type", "subject", "grade", "difficulty")
        }
        for row in rows:
            buckets = row.get("buckets") or {}
            for axis in by:
                by[axis][str(buckets.get(axis))].append(row)

        official = mean(rows)
        return {
            # Official K12Vista metric: mean per-blank partial credit.
            "official_score": official,
            "score_10": round(official * 10, 3),
            "n_scored": len(rows),
            "full_credit_rate": round(sum(bool(r.get("correct")) for r in rows) / len(rows), 4),
            "unparsed_rate": round(sum(bool(r.get("unparsed")) for r in rows) / len(rows), 4),
            "judge_model": next((r.get("judge_model") for r in rows if r.get("judge_model")), None),
            "by_type": {k: {"n": len(v), "score": mean(v)} for k, v in sorted(by["type"].items())},
            "by_subject": {k: {"n": len(v), "score": mean(v)} for k, v in sorted(by["subject"].items())},
            "by_grade": {k: {"n": len(v), "score": mean(v)} for k, v in sorted(by["grade"].items())},
            "by_difficulty": {k: {"n": len(v), "score": mean(v)} for k, v in sorted(by["difficulty"].items())},
        }

    def judge_prompt_provenance(self) -> dict[str, Any]:
        _, eval_prompts = self._prompts()
        return {
            "judge_prompt_version": "k12vista-official-directly_eval_prompt",
            "judge_prompt_sha256": {
                qtype: prompt_sha256(template) for qtype, template in sorted(eval_prompts.items())
            },
        }
