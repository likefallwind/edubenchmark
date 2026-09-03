"""K12-Bench adapter (P15 学习路径规划·知识结构层): curriculum cognition.

Source: ``sources/datasets/k12bench/data/{prereq,locate,neighbor,ground,evidence}.jsonl``
produced by ``scripts/eval/data/fetch_eval_datasets.py --benchmark k12bench`` from
the HuggingFace dataset ``lhpku20010120/K12-KGraph`` (Liang et al. 2026,
arXiv:2605.09635, CC BY-NC-SA 4.0).

K12-Bench is 23,640 four-option **multi-select** MCQ derived from a
curriculum-aligned knowledge graph over People's Education Press K-12 textbooks
(math / physics / chemistry / biology). It probes *curriculum cognition* — the
structure of curricular knowledge, which the paper explicitly separates from the
factual recall measured by C-Eval / CMMLU. Five task families:

  - ``prereq``  (先修闭包 + 直接后继): prerequisite dependency structure
  - ``locate``  (跨章首次出现 + 章节先修): cross-chapter curriculum positioning
  - ``neighbor``(is_a / relates_to 相关概念): concept taxonomy / semantic graph
  - ``ground``  (概念 ↔ 习题): which concepts an exercise assesses, and vice versa
  - ``evidence``(概念 ↔ 实验 验证链): experiment-concept verification links

Text-only, no images. Rule-scored (no LLM judge): each item's gold is a set of
option letters; scoring is instance-level precision/recall/F1 over label sets
plus Exact Match, following the official metric. The framework's headline
``accuracy`` is Exact Match (per-instance all-or-nothing); the (graded)
instance-level Macro-F1 that the panel mounts lives in ``summary.json`` →
``extra_metrics``, reported overall and per task family.

Since the paper's prompt asks for a bare option-letter set (``A`` or ``A,C``),
short replies are parsed directly; only verbose replies fall back to the
extractor model. No answer-key text ever leaks into the prompt.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from ..base import ROOT, BenchmarkAdapter
from ..minimax_client import MiniMaxClient
from ..providers import extraction_max_tokens
from ..scoring import set_prf


DATA_DIR = ROOT / "sources" / "datasets" / "k12bench" / "data"
TASK_FAMILIES = ["prereq", "locate", "neighbor", "ground", "evidence"]
LETTERS = ["A", "B", "C", "D"]
# The mounted (graded) metric per the P15 mapping cells. Relevance weights live in
# data/mapping_measurement_model_v6.json; kept here only as documentation.
MOUNTED_ON_P15 = {"prereq": 1.0, "locate": 0.8, "neighbor": 0.5, "ground": 0.5, "evidence": 0.5}

# Ported from the K12-Bench evaluation prompt (§ prompt): a K-12 teaching expert
# who returns only the set of correct option letters.
SYSTEM_PROMPT = "你是一位K-12教学专家，请判断以下多项选择题的正确选项。"
ANSWER_INSTRUCTION = (
    "请输出所有正确选项的字母，多个用英文逗号分隔（例如：A 或 A,C）。"
    "只允许输出大写字母 A、B、C、D，不要输出任何解释或其他文字。"
)


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise SystemExit(
            f"missing {path}; run: python scripts/eval/data/fetch_eval_datasets.py --benchmark k12bench"
        )
    rows = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _subject(item_id: str) -> str:
    """Subject token embedded in the id, e.g. ``biology_7a_rjb_cpt13`` -> biology."""
    tail = item_id.split("::")[-1]
    return tail.split("_")[0] or "unknown"


class K12BenchAdapter(BenchmarkAdapter):
    name = "k12bench"
    title = "K12-Bench：课程认知（知识结构层，多选题）"
    homepage = "https://github.com/haolpku/K12-Dataset"
    description = (
        "K12-Bench（Liang et al. 2026, arXiv:2605.09635）是从人教版 K-12 数理化生教材构建的"
        "课程对齐知识图谱派生出的 23,640 道四选多选题，考察“课程认知”——先修链、概念分类、"
        "实验-概念链、跨章定位等课程知识结构；论文明确将其与 C-Eval/CMMLU 的事实召回区分开。"
        "对应本仓库 P15（学习路径规划·知识结构层）。\n\n"
        "五个任务族：prereq（先修闭包+直接后继）、locate（跨章首次出现+章节先修）、"
        "neighbor（概念分类/相关）、ground（概念↔习题）、evidence（概念↔实验验证链）。纯文本、无图。\n\n"
        "规则判分、无 LLM 裁判：每题标准答案是一组选项字母，按 instance-level 精确率/召回率/F1"
        "（集合交并）与 Exact Match 计分。报告顶栏“正确率”为 Exact Match（整题全对才算对）；"
        "面板挂载的分级指标 instance-level Macro-F1 见 summary.json 的 extra_metrics（总体 + 分任务族）。"
    )

    def __init__(self, families: list[str] | None = None) -> None:
        self.families = families or TASK_FAMILIES

    def load_items(self, limit: int | None = None, offset: int = 0) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        # ``ground.jsonl`` gives 630 source ids to two derived questions each: a
        # "core concept" variant and a "knowledge/method" variant that differ in
        # question, options and gold. Both are real questions, so neither may be
        # dropped -- but a shared item_id collapses them in every dict keyed by it
        # (resume cache, the extraction/scoring index, suite materialisation,
        # cross-suite reuse), which used to score one model answer against both
        # golds and made the first of each pair look ~90% wrong. Suffix repeats so
        # every item is individually addressable. The first occurrence keeps the
        # raw id, so frozen item lists and earlier runs still resolve to the same
        # question.
        seen: dict[str, int] = {}
        for family in self.families:
            for row in _read_jsonl(DATA_DIR / f"{family}.jsonl"):
                raw_id = str(row["id"])
                nth = seen[raw_id] = seen.get(raw_id, 0) + 1
                options = {k: row["options"].get(k, "") for k in LETTERS}
                gold = sorted(a.strip().upper() for a in row["answer"] if a.strip())
                items.append(
                    {
                        "item_id": raw_id if nth == 1 else f"{raw_id}#{nth}",
                        "text": self._format_question(row["question"], options),
                        "image_paths": [],
                        "gold": gold,
                        "meta": {
                            "options": options,
                            "task_family": family,
                            "subtask": row.get("subtask", family),
                            "subject": _subject(raw_id),
                        },
                    }
                )
        # Interleave families so a small --limit samples across all five, not just
        # the first (prereq) family.
        items = _round_robin(items, key=lambda it: it["meta"]["task_family"])
        return items[offset : offset + limit if limit is not None else None]

    @staticmethod
    def _format_question(question: str, options: dict[str, str]) -> str:
        lines = [question]
        for letter in LETTERS:
            lines.append(f"{letter}. {options.get(letter, '')}")
        lines.append(ANSWER_INSTRUCTION)
        return "\n".join(lines)

    def build_messages(self, item: dict[str, Any]) -> list[dict[str, Any]]:
        return [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": item["text"]},
        ]

    @staticmethod
    def _parse_letters(text: str) -> set[str]:
        text = (text or "").replace("；", ",").replace(";", ",").replace("、", ",")
        return {m for m in re.findall(r"[ABCD]", text.upper())}

    def extract_answer(self, item: dict[str, Any], response: str, client: MiniMaxClient, model: str) -> str:
        response = (response or "").strip()
        if not response:
            return ""
        # The prompt asks for a bare letter set; short replies are parsed directly.
        if len(response) <= 32:
            return ",".join(sorted(self._parse_letters(response)))
        # Verbose reasoning replies mention rejected options too, so a bare regex
        # over-captures; let the extractor model isolate the final selection.
        prompt = (
            "下面是模型对一道四选多选题（选项 A-D）的作答。只输出模型最终选择的选项字母，"
            "多个用英文逗号分隔（例如 A,C），不要输出其他文字。\n\n"
            f"模型作答：\n---\n{response}\n---\n\n最终选择的字母："
        )
        extracted = client.chat(
            [{"role": "user", "content": prompt}],
            model=model,
            max_tokens=extraction_max_tokens(model, 512),
        )
        return ",".join(sorted(self._parse_letters(extracted)))

    def score(self, extracted: str, item: dict[str, Any]) -> dict[str, Any]:
        gold = {a for a in item["gold"]}
        pred = {a for a in (extracted or "").split(",") if a}
        prf = set_prf(gold, pred)
        return {
            "correct": bool(prf["exact"]),
            "normalized": ",".join(sorted(pred)),
            "gold": ",".join(sorted(gold)),
            "f1": prf["f1"],
            "precision": prf["precision"],
            "recall": prf["recall"],
        }

    def buckets(self, item: dict[str, Any]) -> dict[str, str]:
        return {
            "task_family": item["meta"]["task_family"],
            "subject": item["meta"]["subject"],
        }

    def extra_summary(self, scored: list[dict[str, Any]]) -> dict[str, Any]:
        def stats(rows: list[dict[str, Any]]) -> dict[str, Any]:
            if not rows:
                return {"n": 0}
            n = len(rows)
            return {
                "n": n,
                "exact_match": round(sum(1 for r in rows if r.get("correct")) / n, 4),
                "macro_f1": round(sum(float(r.get("f1") or 0.0) for r in rows) / n, 4),
                "precision": round(sum(float(r.get("precision") or 0.0) for r in rows) / n, 4),
                "recall": round(sum(float(r.get("recall") or 0.0) for r in rows) / n, 4),
            }

        counted = [r for r in scored if r.get("score_status") == "scored"]
        result: dict[str, Any] = {
            "metric_note": "headline accuracy = Exact Match; macro_f1 = instance-level Macro-F1 (the panel-mounted metric)",
            "mounted_on": "P15 学习路径规划（知识结构层）",
            "overall": stats(counted),
        }
        for family in TASK_FAMILIES:
            rows = [r for r in counted if (r.get("buckets") or {}).get("task_family") == family]
            if rows:
                fam_stats = stats(rows)
                fam_stats["p15_relevance_weight"] = MOUNTED_ON_P15.get(family)
                result[f"task_family={family}"] = fam_stats
        return result


def _round_robin(items: list[dict[str, Any]], key) -> list[dict[str, Any]]:
    """Interleave items by group key so ``--limit`` samples across all groups."""
    from collections import OrderedDict

    groups: "OrderedDict[str, list[dict[str, Any]]]" = OrderedDict()
    for it in items:
        groups.setdefault(key(it), []).append(it)
    out: list[dict[str, Any]] = []
    lists = list(groups.values())
    i = 0
    while any(i < len(lst) for lst in lists):
        for lst in lists:
            if i < len(lst):
                out.append(lst[i])
        i += 1
    return out
