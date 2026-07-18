"""ASAP 2.0 adapter (essay scoring: model-as-rater against human holistic scores).

Source: ``sources/datasets/asap_2/data/essays.jsonl`` produced by
``scripts/eval/data/fetch_eval_datasets.py`` from the authors' repo
``github.com/scrosseye/ASAP_2.0`` (Crossley et al., ASAP 2.0 — an extension of
the PERSUADE corpus). 24,728 source-based argumentative essays by US grade 6-10
students, each holistically scored 1-6 by trained human raters.

We score the **official test split (7,421 essays, 5 prompts)**; the repo's
17,307-essay train split is materialized but not scored by default. This is the
same item set an earlier external run used, so results are comparable per item.

Headline metric is **quadratic weighted kappa** against the human score, the
standard agreement statistic for ordinal essay scoring — a 1-point miss costs
far less than a 4-point one. QWK is a *population* statistic, not a per-item
one, so ``score()`` records the rating pair and leaves ``correct`` unset; the
framework then reports ``accuracy: null`` and ``extra_summary`` computes QWK
overall and per prompt. Exact and adjacent (within-1) agreement are reported
alongside as readable diagnostics.

**Prompt provenance matters here.** ASAP 2.0 is a corpus, not an LLM benchmark:
it ships human scores, the official train/test split and the official holistic
rubric, but *no* official LLM prompting protocol. So the rubric text
(``data/rubric.txt``, extracted from the repo's ``asap_scoring_rubric.docx``)
and the per-prompt writing task (the corpus's own ``assignment`` column) are
upstream and verbatim, while the surrounding scoring instruction is ours. Do
not present ASAP 2.0 QWK as an official leaderboard number.

The rubric is 1-6 for every prompt. Some prompts happen to have no 6s in the
test split; that is a property of the sample, not a per-prompt scale, so the
prompt always states 1-6 rather than leaking the observed range.

``WITH_SOURCE=1`` additionally supplies the source article(s) the students read,
which is the condition human raters worked under. Availability is partial: the
"Facial action coding system" article (1,840 of the 7,421 test essays) is
withheld upstream as "Copyright Restricted", so that prompt runs without it
either way and ``extra_summary`` reports QWK split by source availability so
the two conditions are never silently mixed.
"""

from __future__ import annotations

import json
import os
import re
from collections import defaultdict
from pathlib import Path
from statistics import fmean
from typing import Any

from ..base import ROOT, BenchmarkAdapter, prompt_sha256
from ..minimax_client import MiniMaxClient
from ..scoring import quadratic_weighted_kappa


DATA_DIR = ROOT / "sources" / "datasets" / "asap_2" / "data"
ESSAYS_FILE = DATA_DIR / "essays.jsonl"
RUBRIC_FILE = DATA_DIR / "rubric.txt"
SOURCE_TEXTS_FILE = DATA_DIR / "source_texts.json"

MIN_SCORE = 1
MAX_SCORE = 6
PROMPT_VERSION = "v1"

# Ours, not official — ASAP 2.0 ships no LLM protocol. The rubric and the
# writing task are injected verbatim from upstream.
SCORING_PROMPT = """You are an experienced rater scoring student essays for a US state writing assessment.

The student read one or more source articles and responded to this assignment:

{assignment}
{source_block}
Score the essay below holistically using the official rubric.

OFFICIAL RUBRIC
{rubric}

STUDENT ESSAY
{essay}

Assign a single holistic score from {min_score} to {max_score}. Judge the essay against the rubric as written, not against the other essays you have seen. Do not adjust for the student's grade level.

Respond with only the integer score. Output nothing else."""

SOURCE_BLOCK = """
The student had access to this source material:

{sources}
"""


class ASAP2Adapter(BenchmarkAdapter):
    name = "asap_2"
    title = "ASAP 2.0：学生议论文整体评分（模型充当评分员，QWK 对齐人工评分）"
    homepage = "https://github.com/scrosseye/ASAP_2.0"
    description = (
        "ASAP 2.0 收录美国 6–10 年级学生的源材料议论文共 24,728 篇，每篇由受训人工评分员按"
        "统一整体量规打 1–6 分。本适配器让被测模型充当评分员，用**二次加权 kappa（QWK）**"
        "衡量它与人工评分的一致程度——这是序数评分任务的标准指标，差 1 分的代价远小于差 4 分。\n\n"
        "评测使用作者仓库中的**官方 test 划分（7,421 篇，5 个 prompt）**；官方 train 划分"
        "（17,307 篇）一并落盘但默认不计分。QWK 是群体统计量而非逐题指标，因此逐题只记录"
        "「模型分/人工分」这一对评分，summary 中 accuracy 显式为 null，QWK 在总体与各 prompt "
        "层面汇总，另附精确一致率与相邻一致率（差 1 分以内）作为可读诊断。\n\n"
        "**提示词来源需要说明：ASAP 2.0 是语料库而非 LLM 评测基准**——它提供人工评分、官方"
        "train/test 划分和官方评分量规，但没有官方的 LLM 提示协议。因此量规原文（取自仓库的"
        "asap_scoring_rubric.docx）与各 prompt 的写作任务（语料自带的 assignment 列）均为上游"
        "原文照录，外围的评分指令是本仓库自拟的。该 QWK 不等同于任何官方排行榜成绩。\n\n"
        "量规对所有 prompt 统一为 1–6 分。部分 prompt 在 test 划分中恰好没有 6 分，那是样本"
        "分布而非该题的分数上限，故提示词一律写 1–6，不把观测区间喂给模型。设置 WITH_SOURCE=1 "
        "可附上学生当时阅读的源文章（更接近人工评分员的条件）；但 Facial action coding system "
        "一题的源文章被上游以版权原因扣留（涉及 7,421 篇中的 1,840 篇），该题无论如何都没有源文，"
        "summary 会按源文可得性分组报告 QWK，避免两种条件被悄悄混在一起。"
    )

    def __init__(self) -> None:
        self._rubric: str | None = None
        self._source_texts: dict[str, list[str]] | None = None

    # --- data loading -----------------------------------------------------------

    def _load_rubric(self) -> str:
        if self._rubric is None:
            if not RUBRIC_FILE.exists():
                raise SystemExit(
                    f"missing {RUBRIC_FILE}; run "
                    "`python scripts/eval/data/fetch_eval_datasets.py --benchmark asap_2`"
                )
            self._rubric = RUBRIC_FILE.read_text(encoding="utf-8").strip()
        return self._rubric

    def _load_source_texts(self) -> dict[str, list[str]]:
        if self._source_texts is None:
            if SOURCE_TEXTS_FILE.exists():
                self._source_texts = json.loads(SOURCE_TEXTS_FILE.read_text(encoding="utf-8"))
            else:
                self._source_texts = {}
        return self._source_texts

    @staticmethod
    def _with_source() -> bool:
        return os.environ.get("WITH_SOURCE", "").strip() in ("1", "true", "yes")

    def load_items(self, limit: int | None = None, offset: int = 0) -> list[dict[str, Any]]:
        if not ESSAYS_FILE.exists():
            raise SystemExit(
                f"missing {ESSAYS_FILE}; run "
                "`python scripts/eval/data/fetch_eval_datasets.py --benchmark asap_2`"
            )
        wanted_split = (os.environ.get("SPLIT") or "test").strip().lower()
        source_texts = self._load_source_texts() if self._with_source() else {}

        rows: list[dict[str, Any]] = []
        with ESSAYS_FILE.open(encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                row = json.loads(line)
                if wanted_split != "all" and str(row.get("split")) != wanted_split:
                    continue
                rows.append(row)

        rows = rows[offset:]
        if limit:
            rows = rows[:limit]

        items: list[dict[str, Any]] = []
        for row in rows:
            prompt_name = str(row.get("prompt_name"))
            sources = source_texts.get(prompt_name) or []
            items.append(
                {
                    "item_id": row["item_id"],
                    "text": "",  # built in build_messages
                    "image_paths": [],
                    "gold": row.get("score"),
                    "meta": {
                        "split": row.get("split"),
                        "prompt_name": prompt_name,
                        "assignment": row.get("assignment"),
                        "full_text": row.get("full_text"),
                        "grade_level": row.get("grade_level"),
                        "essay_word_count": row.get("essay_word_count"),
                        "sources": sources,
                        "source_used": bool(sources),
                    },
                }
            )
        return items

    # --- prompting --------------------------------------------------------------

    def build_messages(self, item: dict[str, Any]) -> list[dict[str, Any]]:
        meta = item["meta"]
        sources = meta.get("sources") or []
        source_block = ""
        if sources:
            joined = "\n\n---\n\n".join(str(text).strip() for text in sources)
            source_block = SOURCE_BLOCK.format(sources=joined)
        prompt = SCORING_PROMPT.format(
            assignment=str(meta.get("assignment") or "").strip(),
            source_block=source_block,
            rubric=self._load_rubric(),
            essay=str(meta.get("full_text") or "").strip(),
            min_score=MIN_SCORE,
            max_score=MAX_SCORE,
        )
        return [{"role": "user", "content": prompt}]

    # --- scoring ----------------------------------------------------------------

    @staticmethod
    def _parse_score(response: str) -> int | None:
        """First in-range integer in the reply, else None.

        Models overwhelmingly answer with a bare digit as instructed. We take
        the first integer token so a stray "Score: 4" still parses, but reject
        out-of-range values rather than clamping them — a 0 or an 8 means the
        model did not follow the rubric scale and should count as bad format,
        not as a boundary score that flatters the agreement statistic.
        """
        if not response:
            return None
        for token in re.findall(r"-?\d+", str(response)):
            value = int(token)
            if MIN_SCORE <= value <= MAX_SCORE:
                return value
            return None
        return None

    def extract_answer(
        self, item: dict[str, Any], response: str, client: MiniMaxClient, model: str
    ) -> str:
        # Rule-based: the prompt asks for a bare integer, so no extractor LLM.
        parsed = self._parse_score(response)
        return "" if parsed is None else str(parsed)

    def score(self, extracted: str, item: dict[str, Any]) -> dict[str, Any]:
        parsed = self._parse_score(extracted)
        gold = item["gold"]
        gold_int = int(gold) if gold is not None else None
        return {
            # QWK is a population statistic; there is no per-item "correct".
            # Leaving this non-bool makes the framework report accuracy: null.
            "correct": None,
            "normalized": parsed,
            "gold": gold_int,
            "bad_format": parsed is None,
            "exact": (parsed is not None and parsed == gold_int),
            "adjacent": (
                parsed is not None and gold_int is not None and abs(parsed - gold_int) <= 1
            ),
        }

    def buckets(self, item: dict[str, Any]) -> dict[str, str]:
        meta = item["meta"]
        return {
            "prompt": str(meta.get("prompt_name")),
            "split": str(meta.get("split")),
            "source_used": "with_source" if meta.get("source_used") else "no_source",
        }

    # --- population metrics -----------------------------------------------------

    @staticmethod
    def _pairs(rows: list[dict[str, Any]]) -> tuple[list[int], list[int]]:
        gold = [r["gold"] for r in rows]
        pred = [r["normalized"] for r in rows]
        return gold, pred

    def _stats(self, rows: list[dict[str, Any]]) -> dict[str, Any]:
        usable = [
            r
            for r in rows
            if isinstance(r.get("normalized"), int) and isinstance(r.get("gold"), int)
        ]
        if not usable:
            return {"n": len(rows), "scorable": 0, "qwk": None}
        gold, pred = self._pairs(usable)
        return {
            "n": len(rows),
            "scorable": len(usable),
            "qwk": quadratic_weighted_kappa(gold, pred),
            "exact_agreement": fmean(1.0 if r["exact"] else 0.0 for r in usable),
            "adjacent_agreement": fmean(1.0 if r["adjacent"] else 0.0 for r in usable),
            "mean_pred": fmean(pred),
            "mean_gold": fmean(gold),
            # Positive = model scores more generously than the human raters.
            "mean_bias": fmean(pred) - fmean(gold),
        }

    def extra_summary(self, scored: list[dict[str, Any]]) -> dict[str, Any]:
        rows = [r for r in scored if r.get("score_status") == "scored"]
        overall = self._stats(rows)

        by_prompt: dict[str, dict[str, Any]] = {}
        grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in rows:
            grouped[str((row.get("buckets") or {}).get("prompt"))].append(row)
        for prompt in sorted(grouped):
            by_prompt[prompt] = self._stats(grouped[prompt])

        # Never let the with-source and no-source conditions blend silently.
        by_source: dict[str, dict[str, Any]] = {}
        grouped_src: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in rows:
            grouped_src[str((row.get("buckets") or {}).get("source_used"))].append(row)
        for condition in sorted(grouped_src):
            by_source[condition] = self._stats(grouped_src[condition])

        bad = sum(1 for r in rows if r.get("bad_format"))
        return {
            "metric_note": (
                "Headline is quadratic weighted kappa against human holistic scores over the "
                "official 7,421-essay test split — a population agreement statistic, not "
                "per-item accuracy (accuracy is null by design). Unparsed or out-of-range "
                "replies are excluded from QWK and counted as bad_format."
            ),
            "headline_metric": "qwk",
            "overall": overall,
            "by_prompt": by_prompt,
            "by_source_condition": by_source,
            "bad_format_rate": (bad / len(rows)) if rows else 0.0,
            "bad_format_count": bad,
            "audit": {
                "split": os.environ.get("SPLIT", "test"),
                "with_source": self._with_source(),
                "rubric_source": "official asap_scoring_rubric.docx (verbatim)",
                "assignment_source": "corpus 'assignment' column (verbatim)",
                "scoring_instruction_source": (
                    "in-repo; ASAP 2.0 defines no official LLM prompting protocol"
                ),
                "prompt_version": PROMPT_VERSION,
                "prompt_sha256": prompt_sha256(SCORING_PROMPT, SOURCE_BLOCK),
                "score_range": [MIN_SCORE, MAX_SCORE],
                "scored_rows": len(rows),
            },
        }
