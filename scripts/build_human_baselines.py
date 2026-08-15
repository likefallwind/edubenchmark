#!/usr/bin/env python3
"""Human-performance anchors for the benchmarks in `reports/eval/`.

Companion to `build_benchmark_baselines.py` (which supplies the floors). This
one supplies the ceilings — and the honest answer is that for most benchmarks
there isn't one. The rule here is: **never invent a number.** A benchmark whose
paper reports no human performance gets `value: null` plus an `evidence` note
saying which paper was checked and what it did or did not say, so nobody has to
re-do the search.

**Two different questions, two separate tables.** "人能拿多少分" and "多少分算
能用" are not the same number and must never be merged into one column:

  * `literature` / `computed_from_local_data` — 人类参照锚. What a human scored,
    or would score, on this item set.
  * `usability_thresholds` — 可用门槛. The line a *system* has to clear before
    the field considers it deployable, regardless of where humans land. Some
    come from measurement standards (AES QWK ≥ 0.70), some from the dataset's
    own inter-annotator agreement, some from the construct itself (a pairwise
    win rate of 0.5 = tied with the expert teacher). Only entries with a real
    citation get a number; the rest carry `value: null` plus the reason.

A benchmark will usually have one of the two, rarely both — that is expected,
and the report prints the empty side as an explicit blank rather than hiding it.

Two sources of anchors:

1. **Computed locally.** MRBench and the BEA 2025 dev set both ship an
   ``Expert`` (and partial ``Novice``) human tutor response per dialogue, with
   the same human annotations used as gold. Running the adapters' own label
   normalisation over those gives a human tutor score on *our* headline metric,
   on *our* item set. That is the strongest anchor available anywhere in this
   repo.

   Caveat, and it is a big one: those labels come from **human annotators**,
   while our models' pass rates come from an **LLM judge**. Same metric, different
   rater. To close that gap, `scripts/run_reference_baseline.py --variant expert`
   re-scores the very same Expert responses with our fixed judge; only then are
   the two directly comparable.

2. **Curated from the literature**, each entry carrying a comparability grade:

     A  same benchmark, same split, same metric — directly comparable
     B  same benchmark, but different split / subset / scoring protocol
     C  institutional proxy (exam pass mark, population mean), not item-level
     D  context only (SOTA system score, judge-reliability stat, other benchmark)
        — never stored as a human score, only under `context_anchors`

Outputs `data/benchmark_human_baselines_v1.json`. Idempotent.
"""

from __future__ import annotations

import argparse
import collections
import json
import statistics
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

OUT_PATH = ROOT / "data" / "benchmark_human_baselines_v1.json"
MRBENCH_FILE = ROOT / "sources" / "datasets" / "mrbench" / "MRBench_V2.json"
BEA_DEV_FILE = ROOT / "sources" / "datasets" / "bea2025" / "mrbench_v3_devset.json"


# --------------------------------------------------------------------------
# 1. locally computed human tutor references
# --------------------------------------------------------------------------


def _mrbench_reference() -> dict[str, Any]:
    from eval.benchmarks.mrbench import DIMENSIONS, KEY_DIMENSIONS, _normalize_label

    rows = json.loads(MRBENCH_FILE.read_text(encoding="utf-8"))
    out: dict[str, Any] = {}
    for tutor in ("Expert", "Novice"):
        labelled = []
        for row in rows:
            resp = (row.get("anno_llm_responses") or {}).get(tutor)
            if not resp:
                continue
            ann = resp.get("annotation") or {}
            labelled.append({d: _normalize_label(d, str(ann.get(d, ""))) for d in DIMENSIONS})
        if not labelled:
            continue
        n = len(labelled)
        passed = sum(1 for lab in labelled if all(lab.get(d) == "Yes" for d in KEY_DIMENSIONS))
        out[tutor] = {
            "n": n,
            "pass_rate": round(passed / n, 4),
            "per_dimension_yes_share": {
                d: round(sum(1 for lab in labelled if lab[d] == "Yes") / n, 4) for d in DIMENSIONS
            },
            "per_dimension_distribution": {
                d: dict(collections.Counter(lab[d] for lab in labelled)) for d in DIMENSIONS
            },
        }
    return out


def _bea_reference() -> dict[str, Any]:
    from eval.benchmarks.bea2025 import DIMENSIONS, KEY_DIMENSIONS, _normalize_label

    rows = json.loads(BEA_DEV_FILE.read_text(encoding="utf-8"))
    out: dict[str, Any] = {}
    for tutor in ("Expert", "Novice"):
        labelled = []
        for row in rows:
            resp = (row.get("tutor_responses") or {}).get(tutor)
            if not resp:
                continue
            ann = resp.get("annotation") or {}
            labelled.append({d: _normalize_label(str(ann.get(d, ""))) for d in DIMENSIONS})
        if not labelled:
            continue
        n = len(labelled)
        passed = sum(1 for lab in labelled if all(lab.get(d) == "Yes" for d in KEY_DIMENSIONS))
        out[tutor] = {
            "n": n,
            "pass_rate": round(passed / n, 4),
            "per_dimension_yes_share": {
                d: round(sum(1 for lab in labelled if lab[d] == "Yes") / n, 4) for d in DIMENSIONS
            },
            "per_dimension_distribution": {
                d: dict(collections.Counter(lab[d] for lab in labelled)) for d in DIMENSIONS
            },
        }
    return out


COMPUTED_NOTE = (
    "由本地数据集自带的 Expert / Novice 人类教师回复 + 人类标注金标算出，"
    "用的是 adapter 自己的标签归一与 KEY_DIMENSIONS 判定，因此与我们的 pass_rate 同口径同题集。"
    "唯一的口径差：这里的标签来自人类标注者，我们模型的标签来自 LLM judge。"
    "跑 scripts/run_reference_baseline.py --variant expert 用同一个 judge 复评后才严格可比。"
)


# --------------------------------------------------------------------------
# 2. curated literature table
# --------------------------------------------------------------------------

# value 一律用该 benchmark 的 headline 原始标度（不是 0-10 归一分）。
LITERATURE: dict[str, dict[str, Any]] = {
    "mathvista": {
        "headline": "accuracy",
        "human": {
            "value": 0.603,
            "grade": "A",
            "population": "AMT 标注员，高中及以上学历",
            "source": "MathVista (ICLR 2024), arXiv:2310.02255；官方 repo lupantech/MathVista 榜单",
            "note": (
                "论文的人类评测就在 testmini 1,000 题上做，与我们的评测集完全一致。"
                "论文另给 5 类任务与 7 类技能的人类拆分（见 per_task）；"
                "任务维度与我们的 by_bucket.task 同名可直接对齐，技能维度我们还没建 bucket。"
                "读拆分时记住标注协议：每人 20 分钟做 5 题，几何题的 48.4% 是没时间算，不是算不出。"
            ),
        },
        "context_anchors": [
            {
                "label": "官方公布的 Random chance",
                "value": 0.179,
                "note": "与 build_benchmark_baselines.py 模拟出的 0.1792 吻合，可作为随机基线方法论的交叉验证。",
            }
        ],
        "evidence": "论文与官方 repo 均明确给出 Human performance 60.3% 与 Random chance 17.9%。",
    },
    "agieval": {
        "headline": "accuracy",
        "human": {
            "value": 0.670,
            "grade": "B",
            "population": "真实考生（LSAT / SAT / 高考 / 司法考试），50 百分位",
            "source": "AGIEval (NAACL 2024 Findings), arXiv:2304.06364；仓库 data/exhaustive_2026-05-13/results.jsonl 已收录",
            "note": (
                "0.670 是论文自己列的总均值，不要拿它和我们的总 accuracy 并列——"
                "我们跑的 7,272 题里 MATH(1,000) 没有人类分。"
                "论文对其余 20 个子任务逐个给了人类均分与前 1% 分（见 per_task），"
                "按我们的题数加权重算才是可比的口径，那条路径由 build_human_baseline_report.py 完成。"
            ),
            "reading_blocked": "⚠ 总分口径不可比，看「逐任务对齐」那一节的加权值，不要看这一行。",
        },
        "context_anchors": [
            {"label": "Human top（前 1%）", "value": 0.910, "note": "同一来源，zero-shot 设定。"}
        ],
        "evidence": (
            "官方 repo README 的榜单不含人类行；人类分在论文正文 Table 2/3，"
            "论文说明其来源是把真实考试 50 百分位与前 1% 考生的分数折算成正确率，"
            "不是为本题集单独组织的人类实验。"
        ),
    },
    "mmtutorbench": {
        "headline": "extra:average_total_score_0_to_6",
        "human": {
            "value": 5.85,
            "grade": "B",
            "population": "专家标注员",
            "source": "MMTutorBench (ACL 2026), arXiv:2510.23477",
            "note": (
                "两处不可比：(1) 人类只在 66 题子集上评，我们跑 770 行；"
                "(2) 人类回复由论文的 GPT-o4-mini rubric judge 打分，我们的固定 judge 是 MiniMax-M3。"
                "judge 不同会整体平移分数，跨 judge 直接比会误判。"
            ),
            "reading_blocked": (
                "⚠ 跨 judge 不可比：人类 5.85 由论文的 GPT-o4-mini 打，我们的分由 MiniMax-M3 打，"
                "而且人类只评了 66 题子集。这条差距不能读成能力差。"
            ),
        },
        "context_anchors": [
            {"label": "论文最强模型 Gemini-2.5-Pro", "value": 4.69, "note": "同一 judge 口径。"}
        ],
        "evidence": "论文 human 行给出 total 5.85，六维分别 0.97/0.97/0.97/0.97/0.98/0.98。",
    },
    "pedagogy_benchmark": {
        "headline": "accuracy",
        "human": {
            "value": None,
            "grade": None,
            "source": "Benchmarking the Pedagogical Knowledge of LLMs, arXiv:2506.18710",
            "note": (
                "论文原话：Question-level human results are not available for these exams。"
                "他们那个 ~50% 是把每道题赋以其来源试卷的平均正确率再取平均得到的，"
                "所以题级估计其实存在——但这个字段没随数据发布，"
                "本地 questions.jsonl 只有 year / category / education_level。"
                "2026-08-15 决定：不去找作者要，按没有处理。"
            ),
        },
        "context_anchors": [
            {
                "label": "智利教师专业发展考试人群均分（制度性代理，grade C）",
                "value": 0.50,
                "note": (
                    "2017-2021 共 25,000+ 名受训教师的平均预期得分，非本题集实测。"
                    "论文自己也提醒 this is only an estimate, and any interpretation "
                    "should be made with caution。"
                ),
            }
        ],
        "evidence": "已查论文正文：给出人群均分约 50% 及其推导方式，同时明确声明无题级人类结果。",
    },
    "mrbench_judge": {
        "headline": "extra:macro_over_dimensions.f1_macro",
        "human": {
            "value": None,
            "grade": None,
            "source": "Unifying AI Tutor Evaluation / MRBench, arXiv:2412.09416",
            "note": "论文未给「人类当 judge 复现金标」的 macro-F1，只给一致性统计量。",
        },
        "context_anchors": [
            {
                "label": "标注者间 Cohen's kappa（人类判分的一致性上限，对应 macro_over_dimensions.cohen_kappa）",
                "value": 0.71,
                "note": (
                    "论文报总体 kappa 0.71（substantial），试点阶段 Fleiss kappa 0.65。"
                    "我们最好的模型 kappa 约 0.41（glm-5.2），离人类互评一致性还有明显距离——"
                    "这是这个 benchmark 上最有意义的人类锚。"
                ),
            }
        ],
        "evidence": "论文正文给出总体 kappa 0.71 与试点 Fleiss 0.65，未按维度拆分。",
    },
    "mrbench_tutor": {
        "headline": "extra:pass_rate",
        "human": {
            "value": None,  # filled from the computed section at build time
            "grade": "B",
            "source": "本地 MRBench_V2.json 自带的 Expert 教师回复 + 人类标注",
            "note": COMPUTED_NOTE,
            "reading_blocked": (
                "⚠ 不要读成「模型超过人类专家」：我们给被测模型的 prompt 逐条列出了 judge 的评分维度，"
                "人类教师没有这份清单。修掉泄题之前这一行的对比无效。"
            ),
        },
        "context_anchors": [
            {
                "label": "论文报告的专家教师逐维得分",
                "value": None,
                "note": (
                    "Mistake identification 76.04 / Mistake location 63.02 / Revealing answer 90.62 / "
                    "Providing guidance 67.19 / Actionability 76.04 / Coherence 79.17 / "
                    "Tutor tone 92.19 / Human-likeness 87.50（arXiv:2412.09416）。"
                    "论文同时指出多数维度上最强 LLM 已超过专家教师。"
                ),
            }
        ],
        "evidence": "Expert 分数由本地数据直接算出，见 computed 段。",
    },
    "bea2025_tutor": {
        "headline": "extra:pass_rate",
        "human": {
            "value": None,  # filled from the computed section at build time
            "grade": "B",
            "source": "本地 mrbench_v3_devset.json 自带的 Expert 教师回复 + 人类标注",
            "note": COMPUTED_NOTE,
            "reading_blocked": (
                "⚠ 同 mrbench_tutor：prompt 泄了评分维度，「模型超过人类专家」的读法不成立。"
            ),
        },
        "context_anchors": [],
        "evidence": "Expert 分数由本地数据直接算出，见 computed 段。",
    },
    "bea2025_judge": {
        "headline": "extra:recommended_judge_score",
        "human": {
            "value": None,
            "grade": None,
            "source": "Findings of the BEA 2025 Shared Task, arXiv:2507.10579",
            "note": "共享任务的金标即人类标注本身，论文未单独报「人类复现金标」的 macro-F1。",
        },
        "context_anchors": [
            {
                "label": "标注者间 Fleiss kappa（人类判分的一致性上限）",
                "value": 0.65,
                "note": (
                    "dev 集 200 段对话由 4 名标注者标，平均 Fleiss kappa 0.65（substantial）；"
                    "另有 83 条回复由 6 名组织者复标，Fleiss kappa 0.64。"
                    "这是本 benchmark 上唯一的人类侧硬数字，对应我们的 "
                    "extra_metrics.macro_over_dimensions.cohen_kappa。"
                ),
            },
            {
                "label": "最佳参赛系统 macro-F1（专用系统锚，grade D，非人类）",
                "value": None,
                "note": (
                    "四个赛道 exact macro-F1 最好成绩：Mistake Identification 0.7181(BJTU)、"
                    "Actionability 0.7085(bea-jh)、Mistake Location 0.5983(BLCU-ICALL)、"
                    "Providing Guidance 0.5834(MSA)；lenient 口径为 0.9185 / 0.8659 / 0.8404 / 0.7860。"
                    "50+ 支队伍参赛。我们最好的 recommended_judge_score 是 0.549（glm-5.2），"
                    "在专用微调系统的区间下沿。"
                ),
            },
            {
                "label": "人类教师回复在 tutor identification 赛道的可辨识度",
                "value": None,
                "note": "专家教师 79.1%、新手教师 66.5%——这是「认得出是人写的」，不是教学质量分。",
            },
        ],
        "evidence": "已查 Findings 论文：给出标注者一致性、各赛道最佳系统分与参赛规模，未给人类判分基线。",
    },
    "tutorbench": {
        "headline": "extra:arr_w_x100",
        "human": {
            "value": None,
            "grade": None,
            "source": "TutorBench (Scale AI), arXiv:2510.02663",
            "note": (
                "论文未报人类专家在 ARR_w 上的得分。"
                "本来还有一条路：论文说每条样本都配了专家写的 golden tutoring response，"
                "把它过我们自己的 judge 就能得到同管线人类分——但公开发布的 "
                "sources/datasets/tutorbench/tutorbench.jsonl 只有 rubrics，没有那条参考回复"
                "（字段只有 prompt / initial_explanation / follow_up_prompt / rubrics / image 等）。"
                "这条路在本地走不通。"
            ),
        },
        "context_anchors": [
            {
                "label": "judge 可靠性（grade D）",
                "value": None,
                "note": (
                    "LLM judge 与人类一致率 0.78，人类互评一致率 0.75；"
                    "judge 对多数投票的 F1 0.82，最强单个人类专家 0.91。"
                    "另：论文最强模型 Gemini 2.5 Pro ARR_w 55.65%，无前沿模型超过 56%。"
                    "注意我们的 judge 是 MiniMax-M3、论文用 Claude Sonnet 4 且只评 Fair815 子集，不可直接对标。"
                ),
            }
        ],
        "evidence": "已查论文：只有 judge-人类一致性与模型分，无人类作答分。",
    },
    "olympiadbench": {
        "headline": "accuracy",
        "human": {
            "value": None,
            "grade": None,
            "source": "OlympiadBench (ACL 2024), arXiv:2402.14008",
            "note": (
                "已核：论文全文未给人类表现分。摘要里的 expert-level annotations 指的是标注过程，"
                "不是人类作答基线。网上流传的「人类专家 >90%」没有论文出处，不采用。"
            ),
        },
        "context_anchors": [
            {
                "label": "论文最强模型 GPT-4V",
                "value": 0.1797,
                "note": (
                    "对照我们实跑的 0.716-0.766：两年模型进步 + 我们只跑 OE 子集（跳过 TP 证明题），"
                    "协议差异巨大，不要拿论文数当难度参照。"
                ),
            }
        ],
        "evidence": "已查 arXiv:2402.14008 摘要与正文：无人类基线，仅有定性表述。",
    },
    "sas_bench": {
        "headline": "extra:overall.qwk",
        "human": {
            "value": None,
            "grade": None,
            "source": "SAS-Bench, arXiv:2505.07247",
            "note": (
                "已核：论文未报标注者间一致性，也没有人类-人类 QWK。"
                "18 位学科专家分两组标注 + 分歧讨论重标，但无量化一致性统计。"
            ),
        },
        "context_anchors": [
            {
                "label": "论文最强模型",
                "value": None,
                "note": "Deepseek-V3 平均 CCS 74.11%，Deepseek-R1 平均 ECS 55.90%。",
            }
        ],
        "evidence": "已查 arXiv:2505.07247 全文：明确无 inter-annotator agreement 数字。",
    },
    "asap_2": {
        "headline": "extra:overall.qwk",
        "human": {
            "value": None,
            "grade": None,
            "source": "ASAP 2.0 corpus paper (Crossley et al., Assessing Writing, 2025)",
            "note": (
                "已核：语料由两组评分员打分，但 (1) 公开发布的 CSV 只保留合议后的单一 score 列，"
                "本地算不出人类互评 QWK；(2) 语料论文在 ScienceDirect 付费墙后（HTTP 403），拿不到数字。"
                "在拿到论文前如实留空。"
            ),
        },
        "context_anchors": [
            {
                "label": "AES 领域的人类互评 QWK 常规区间（grade D）",
                "value": None,
                "note": (
                    "跨数据集约 0.61-0.97；领域内把机器-人类 QWK ≥ 0.70 视为可接受门槛。"
                    "我们实跑 0.473-0.611，整体低于该门槛——这是有意义的定性结论，"
                    "但 0.61-0.97 这个区间不是 ASAP 2.0 的数，不能当人类基线用。"
                ),
            }
        ],
        "evidence": "已查 GitHub README 与语料论文页：README 未给一致性数字，论文 403。",
    },
    "ceval": {
        "headline": "accuracy",
        "human": {
            "value": None,
            "grade": None,
            "source": "C-Eval (NeurIPS 2023 D&B), arXiv:2305.08322",
            "note": "已核：论文未报人类表现，只报模型分（当时仅 GPT-4 超过 60%）。",
        },
        "context_anchors": [],
        "evidence": "已查论文与 NeurIPS 版：无 human 行。",
    },
    "mmlu_pro": {
        "headline": "accuracy",
        "human": {
            "value": None,
            "grade": None,
            "source": "MMLU-Pro (NeurIPS 2024 D&B)",
            "note": (
                "已核：论文未报人类表现。常被引用的 89.8% 是原版 MMLU 论文对众包标注员的"
                "估计值，既是另一个 benchmark（4 选 1，题目也不同），本身也不可靠，不外推。"
            ),
        },
        "context_anchors": [],
        "evidence": "已查论文：无 human 行；MMLU 的 89.8% 出自 arXiv:2009.03300，属另一 benchmark。",
    },
    "eduguard_sata": {
        "headline": "extra:overall.rfs",
        "human": {
            "value": None,
            "grade": None,
            "source": "EduGuardBench, arXiv:2511.06890",
            "note": "已核：SATA 金标由外部专家团设计，论文未让人类作答，无人类 RFS。",
        },
        "context_anchors": [],
        "evidence": "已查论文：只有 judge 与人类的校准 kappa，无人类作答分。",
    },
    "eduguard_adversarial": {
        "headline": "extra:overall.asr",
        "human": {
            "value": None,
            "grade": None,
            "source": "EduGuardBench, arXiv:2511.06890",
            "note": "越狱抵抗力没有「人类基线」这个概念；地板在另一头——全部拒答即 ASR 0。",
        },
        "context_anchors": [
            {
                "label": "judge 与人类标注的校准（grade D）",
                "value": None,
                "note": (
                    "论文选 DeepSeek-V3 当 judge，与人类一致性 Cohen's kappa 0.882（有害性二分类）"
                    "与 0.874（拒答质量三分类）。我们默认 judge 是 MiniMax-M3，未做同等校准。"
                ),
            }
        ],
        "evidence": "已查论文：给出 judge 校准 kappa，无人类 ASR。",
    },
    "k12bench": {
        "headline": "accuracy",
        "human": {
            "value": None,
            "grade": None,
            "source": "K12-KGraph, arXiv:2605.09635",
            "note": "已核：题目由课程知识图谱自动派生，论文未做人类作答实验。",
        },
        "context_anchors": [
            {
                "label": "论文报告的模型区间",
                "value": None,
                "note": (
                    "Gemini-3-Flash 57% exact match，最强开源 Gemma-4-31B-IT 46%。"
                    "我们实跑 minimax3 0.500，落在这个区间内，可作为接入正确性的旁证。"
                ),
            }
        ],
        "evidence": "已查论文与项目页：无 human baseline。",
    },
    "k12vista": {
        "headline": "extra:official_score",
        "human": {
            "value": None,
            "grade": None,
            "source": "K12Vista, arXiv:2506.01676",
            "note": "已核：论文重点在 K12-PEM 过程评估模型与人工标注的 K12-PEBench，未给人类答题基线。",
        },
        "context_anchors": [],
        "evidence": "已查论文摘要与项目页：无 human 作答分。",
    },
    "ifeval": {
        "headline": "extra:prompt_strict_accuracy",
        "human": {
            "value": None,
            "grade": "C",
            "source": "IFEval, Google Research",
            "note": (
                "构造性上限：指令都是可程序化验证的（字数、格式、禁用词等），"
                "认真执行的人类接近 1.0。这是设计推论而非实测，标为 grade C，不要当实测人类分用。"
            ),
        },
        "context_anchors": [
            {
                "label": "内容无关的通用文本地板",
                "value": None,
                "note": "见 benchmark_baselines_v1.json：generic_text 策略 prompt-strict 约 0.056。",
            }
        ],
        "evidence": "论文无人类实验；此处只记构造性上限。",
    },
    "p08_abstention": {
        "headline": "extra:score_10",
        "human": {
            "value": 0.9316,
            "metric": "extra:abstention_f1",
            "grade": "B",
            "population": "5 名志愿者",
            "source": "UMWP / Benchmarking Hallucination in LLMs based on Unanswerable Math Word Problem (LREC-COLING 2024), arXiv:2403.03558",
            "note": (
                "⚠ 这个数不在 headline 的标度上。我们的 score_10 是仓库自建复合指标，"
                "对任何与题无关的策略都恒等于 5.0，没有人类对照概念；"
                "但题源 UMWP 的原生指标（以「不可答」为正类的 F1）我们本来就在算，"
                "字段是 extra_metrics.abstention_f1，可以直接对上人类的 93.16%。"
                "口径差：论文用 instruction 输入形式，等于提前告诉受试者存在不可答题；"
                "我们的 prompt 故意不提示（提示了会诱发全弃答），所以我们这边更难，差距可能被高估。"
                "另：人类只做了按类别分层抽的 200 题，我们跑 5,200 题全量。"
            ),
            "reading_blocked": (
                "⚠ 我们的 prompt 不提示存在不可答题，论文提示了，我们这边更难；"
                "差距是上界，不要读成「模型比人差这么多」。"
            ),
        },
        "context_anchors": [
            {
                "label": "论文最强模型 GPT-4（同 F1 口径）",
                "value": 0.8524,
                "note": "论文里人类领先最强模型约 8 个百分点。我们实跑的 abstention_f1 见报告表。",
            }
        ],
        "evidence": "已查论文：人类基线为 5 名志愿者在 200 题上的平均 F1 = 93.16%（instruction 输入形式）。",
    },
    "edubench": {
        "headline": "extra:overall.mean_overall_score",
        "human": {
            "value": None,
            "grade": None,
            "source": "EduBench (arXiv:2505.16160), github.com/ybai-nlp/EduBench",
            "note": (
                "无人类作答分：评分完全靠 LLM judge 打 12 维 1-10 分，"
                "论文与仓库都没有让人类写回答再评的实验。量表下限是 1，地板靠退化回复实测。"
            ),
        },
        "context_anchors": [
            {
                "label": "judge 相对人类标注的系统性通胀（grade D，但读分时必须挂上）",
                "value": None,
                "note": (
                    "论文的人类评测只有 198 条样本（中英各 99）、且只有 1 名标注者"
                    "（作者自己说 due to cost constraints ... may limit the reliability）。"
                    "与 judge 的 Kendall's W：DeepSeek-V3 / R1 / QwQ-Plus 均为 0.63，GPT-4o 只有 0.56。"
                    "论文明确指出模型 judge 在指标级与场景级都比人类高约 1 分。"
                    "我们实跑区间 7.47-8.48，按这个修正，人类观感大致在 6.5-7.5。"
                ),
            }
        ],
        "evidence": "已查论文正文与 Table 5：给出人类评测规模、Kendall's W 与「高约 1 分」的结论，无人类得分行。",
    },
}

# Self-built or repo-internal item sets: there is no external human study to look
# up, and inventing one would be worse than an honest blank.
SELF_BUILT: dict[str, str] = {
    "eduillustrate": "仓库自建题集 + 自建 judge rubric，无外部人类参照。",
    "longtutor_evidence": "仓库自建，无外部人类参照。",
    "longtutor_diagnosis": "仓库自建，无外部人类参照。",
    "longtutor_teaching": "仓库自建，无外部人类参照；且其 accuracy 实为解析成功率（实跑 0.999-1.000），无区分度。",
    "mooccube_prereq": "仓库自建（基于 MOOCCube 图谱派生），无外部人类参照；已内建 chance correction。",
    "p07_selfcheck": "仓库自建复合指标，无人类对照概念；平凡策略地板 5.0/10。",
    "p08_calibration": "仓库自建复合指标，无人类对照概念；平凡策略地板 5.0/10。",
    "mmtutorbench_judge_calibration": "公开 JSONL 无 per-item 人类金标，adapter 本身不产出题目。",
    "mathtutorbench_judge_calibration": (
        "官方 A/B 偏好对（teacher_response_positive = 专家改写，negative = 新手原话），"
        "金标即人类偏好，无「人类得分」概念。可比的是专用系统锚：论文自己微调的 "
        "Qwen2.5-1.5B 奖励模型区分专家/新手的准确率是 0.84，我们实跑 0.810-0.844，已经同水平。"
    ),
    "mathtutorbench_problem_solving": "GSM8K 派生，官方无人类基线（GSM8K 原论文的人类基线针对完整数据集，非此子集）。",
    "mathtutorbench_mistake_correction": "同上。",
    "mathtutorbench_socratic": "BLEU 对参考问句，人类改述同样拿不到高 BLEU，该指标无人类上限意义。",
    "mathtutorbench_mistake_location": "标注金标即人类判断，论文未报人类复现分。",
    "mathtutorbench_solution_correctness": "同上。",
    "mathtutorbench_pedagogy": (
        "与金标教师回应成对比较，win_rate 0.5 即「与专家教师打平」——该基准的专家锚天然是 0.5。"
        "还差一个下锚：data/pref_test.jsonl 每条都带 teacher_response_negative（新手教师原话），"
        "拿它当被测回复跑一遍就能得到「新手教师 win_rate」，"
        "让跌破 0.5 的模型有「相当于新手 / 不如新手」的落点。未跑。"
    ),
    "mathtutorbench_pedagogy_hard": "同上，专家锚 = win_rate 0.5，新手锚未跑。",
    "mathtutorbench_scaffolding": "同上，专家锚 = win_rate 0.5，新手锚未跑（这个任务 7 个模型有 5 个跌破 0.5，最需要下锚）。",
    "mathtutorbench_scaffolding_hard": "同上，专家锚 = win_rate 0.5，新手锚未跑（6/7 跌破）。",
}


# --------------------------------------------------------------------------
# 3. per-task human tables
# --------------------------------------------------------------------------

# 论文给了逐任务人类分的 benchmark。key 必须与我们 summary.json 的
# by_bucket.<bucket> 键名逐字一致，否则 join 会静默漏项——报告脚本会检查。
# 这里只放论文的原始数字；按我们题数加权的合成值在 build_human_baseline_report.py
# 里算，因为那要读我们自己的 run。
PER_TASK_HUMAN: dict[str, dict[str, Any]] = {
    "agieval": {
        "bucket": "task",
        "metric": "accuracy",
        "source": "AGIEval, arXiv:2304.06364, Table 2/3",
        "population": "真实考生分数分布折算：avg = 50 百分位，top = 前 1%",
        "values": {
            "lsat-ar": {"avg": 0.56, "top": 0.91},
            "lsat-lr": {"avg": 0.56, "top": 0.91},
            "lsat-rc": {"avg": 0.56, "top": 0.91},
            "sat-math": {"avg": 0.66, "top": 0.94},
            "sat-en": {"avg": 0.66, "top": 0.94},
            "sat-en-without-passage": {"avg": 0.66, "top": 0.94},
            "logiqa-en": {"avg": 0.86, "top": 0.95},
            "logiqa-zh": {"avg": 0.88, "top": 0.96},
            "aqua-rat": {"avg": 0.85, "top": 1.00},
            "gaokao-chinese": {"avg": 0.65, "top": 0.85},
            "gaokao-english": {"avg": 0.69, "top": 0.91},
            "gaokao-geography": {"avg": 0.65, "top": 0.85},
            "gaokao-history": {"avg": 0.64, "top": 0.85},
            "gaokao-biology": {"avg": 0.68, "top": 0.89},
            "gaokao-chemistry": {"avg": 0.66, "top": 0.86},
            "gaokao-physics": {"avg": 0.71, "top": 0.94},
            "gaokao-mathqa": {"avg": 0.73, "top": 0.96},
            "gaokao-mathcloze": {"avg": 0.73, "top": 0.96},
            "jec-qa-kd": {"avg": 0.71, "top": 0.78},
            "jec-qa-ca": {"avg": 0.58, "top": 0.85},
        },
        "excluded": {
            "math": "MATH 子集不是真人考试，论文无人类分；加权时必须排除（约 1,000 题）。",
        },
        "caveats": [
            "同一场考试的三个 LSAT 子任务共用一个人类分（56/91），SAT 三个子任务共用 66/94——"
            "这是考试级折算，不是子任务级实测。",
            "sat-en-without-passage 是「不给原文」的消融设定，人类那 0.66 是给原文考出来的，"
            "这一格模型吃亏，差值不要当能力差读。",
        ],
    },
    "mathvista": {
        "bucket": "task",
        "metric": "accuracy",
        "source": "MathVista (ICLR 2024), arXiv:2310.02255, Table 2",
        "population": "AMT 标注员，高中及以上学历，20 分钟做 5 题",
        "values": {
            "figure question answering": {"avg": 0.597},
            "geometry problem solving": {"avg": 0.484},
            "math word problem": {"avg": 0.730},
            "textbook question answering": {"avg": 0.632},
            "visual question answering": {"avg": 0.559},
        },
        "excluded": {},
        "caveats": [
            "限时协议：几何题人类只有 48.4%，是没时间算，不是算不出。"
            "模型在这一格 98% 不代表几何能力超人。",
        ],
        "unjoined_reference": {
            "note": (
                "论文还给了 7 类数学技能的人类分，但我们的 mathvista adapter 没建 skill bucket，"
                "现在 join 不上。要用得给 adapter 加一个 skills bucket 再 --score-only 重跑打分"
                "（不花 API 额度）。"
            ),
            "by_skill": {
                "ALG 代数": 0.509,
                "ARI 算术": 0.592,
                "GEO 几何": 0.514,
                "LOG 逻辑": 0.407,
                "NUM 数值常识": 0.538,
                "SCI 科学": 0.649,
                "STA 统计": 0.639,
            },
        },
    },
}


# --------------------------------------------------------------------------
# 4. usability thresholds — "多少分算能用"，与人类分是两回事
# --------------------------------------------------------------------------

# kind:
#   field_standard   测量学/行业公认的上线门槛，有正式出处
#   inter_annotator  数据集自带的人类标注者一致性，既是人类上限也是可用线
#   construct        指标构造本身决定的分界（成对胜率 0.5 = 与专家打平）
#   institutional    考试及格线一类的制度性代理，粒度粗，只作参考
#   none             确认没有公认门槛，写清为什么
#
# metric 缺省等于该 benchmark 的 headline；填了就表示门槛落在另一个字段上。
# scale 是把门槛换算到我们 summary 字段标度的乘数（如 QWK 以 0-100 记录时为 100）。
USABILITY: dict[str, dict[str, Any]] = {
    "asap_2": {
        "kind": "field_standard",
        "metric": "extra:overall.qwk",
        "scale": 1.0,
        "operator": ">=",
        "value": 0.70,
        "label": "自动作文评分上线门槛 QWK ≥ 0.70",
        "source": (
            "Williamson, Xi & Breyer (2012), A Framework for Evaluation and Use of "
            "Automated Scoring, Educational Measurement 31(1):2-13；ACT CRASE 技术报告 "
            "R2304 (2023) 沿用同一条"
        ),
        "note": (
            "同一框架还有第二条：若人类互评 QWK 更高，机器-人类 QWK 与它的差距应 ≤ 0.10。"
            "ASAP 2.0 没发布双评分员原始分（本地 csv 只有合议后的单一 score 列），"
            "第二条本地无法检验，只能查第一条。"
        ),
    },
    "sas_bench": {
        "kind": "field_standard",
        "metric": "extra:overall.qwk",
        "scale": 100.0,
        "operator": ">=",
        "value": 0.70,
        "label": "自动评分上线门槛 QWK ≥ 0.70（该 benchmark 的 qwk 字段以 0-100 记）",
        "source": "同 asap_2：Williamson, Xi & Breyer (2012)",
        "note": (
            "门槛本身是通用的自动评分标准，不是 SAS-Bench 论文提出的。"
            "SAS-Bench 论文没报标注者一致性，所以第二条（与人类互评差 ≤ 0.10）同样无法检验。"
        ),
    },
    "mrbench_judge": {
        "kind": "inter_annotator",
        "metric": "extra:macro_over_dimensions.cohen_kappa",
        "scale": 1.0,
        "operator": ">=",
        "value": 0.61,
        "label": "判分一致性 kappa ≥ 0.61（Landis & Koch 的 substantial 档）",
        "source": "Landis & Koch (1977) 的一致性分档；数据集自带的人类锚见 note",
        "note": (
            "这个 benchmark 上「能用」= 当裁判时和人类标注者的一致性够高，"
            "所以门槛落在 kappa 上而不是 headline 的 macro-F1 上。"
            "真正的人类上限是数据集自己的标注者一致性 Cohen's kappa 0.71"
            "（试点阶段 Fleiss 0.65），0.61 只是「勉强能用」的下界。"
        ),
        "human_ceiling": 0.71,
    },
    "bea2025_judge": {
        "kind": "inter_annotator",
        "metric": "extra:macro_over_dimensions.cohen_kappa",
        "scale": 1.0,
        "operator": ">=",
        "value": 0.61,
        "label": "判分一致性 kappa ≥ 0.61（Landis & Koch 的 substantial 档）",
        "source": "Landis & Koch (1977)；人类锚见 note",
        "note": (
            "人类上限是 dev 集 4 名标注者的平均 Fleiss kappa 0.65"
            "（组织者复标子集 0.64）。注意 Fleiss(多标注者) 与我们算的 Cohen(两方) 不是同一个统计量，"
            "量级可比、定义不同，别当成同一把尺子上的刻度。"
        ),
        "human_ceiling": 0.65,
    },
    "mathtutorbench_pedagogy": {
        "kind": "construct",
        "metric": "extra:win_rate",
        "scale": 1.0,
        "operator": ">=",
        "value": 0.50,
        "label": "与专家教师回应打平 = win_rate 0.5",
        "source": "指标构造：与金标专家教师回应的成对胜率",
        "note": "0.5 同时是人类锚和可用线——低于它就是在这项上不如专家教师。",
    },
    "mathtutorbench_pedagogy_hard": {
        "kind": "construct",
        "metric": "extra:win_rate",
        "scale": 1.0,
        "operator": ">=",
        "value": 0.50,
        "label": "与专家教师回应打平 = win_rate 0.5",
        "source": "指标构造",
        "note": "同 mathtutorbench_pedagogy。",
    },
    "mathtutorbench_scaffolding": {
        "kind": "construct",
        "metric": "extra:win_rate",
        "scale": 1.0,
        "operator": ">=",
        "value": 0.50,
        "label": "与专家教师回应打平 = win_rate 0.5",
        "source": "指标构造",
        "note": "同 mathtutorbench_pedagogy。这个任务多数模型跌破 0.5，是全套里少数结论明确为负的地方。",
    },
    "mathtutorbench_scaffolding_hard": {
        "kind": "construct",
        "metric": "extra:win_rate",
        "scale": 1.0,
        "operator": ">=",
        "value": 0.50,
        "label": "与专家教师回应打平 = win_rate 0.5",
        "source": "指标构造",
        "note": "同上。",
    },
    "mathtutorbench_judge_calibration": {
        "kind": "field_standard",
        "metric": "accuracy",
        "scale": 1.0,
        "operator": ">=",
        "value": 0.84,
        "label": "追平论文专用奖励模型的 0.84",
        "source": "MathTutorBench, arXiv:2502.18940：微调 Qwen2.5-1.5B 区分专家/新手教师回复的最好准确率 0.84",
        "note": (
            "这是专用系统锚不是人类锚——金标本身就是人类偏好，人类复现分没有意义。"
            "拿它当可用线的理由：低于专用小模型就没必要用通用大模型做这件事。"
        ),
    },
    "p08_abstention": {
        "kind": "field_standard",
        "metric": "extra:abstention_f1",
        "scale": 1.0,
        "operator": ">=",
        "value": 0.9316,
        "label": "追平 UMWP 的人类志愿者 F1 93.16%",
        "source": "UMWP, arXiv:2403.03558",
        "note": (
            "这一条人类锚和可用线重合：拒答该不该拒，人做得对就是标准。"
            "口径差见 literature.p08_abstention。"
        ),
    },
    "ceval": {
        "kind": "institutional",
        "metric": "accuracy",
        "scale": 1.0,
        "operator": ">=",
        "value": 0.60,
        "label": "中国考试通行及格线 60%",
        "source": "制度性代理，非本题集实测；C-Eval 论文无人类行",
        "note": (
            "粒度很粗：C-Eval 混了初中到专业资格四个难度层，各层及格线并不相同，"
            "而且 4 选 1 的随机地板就有 0.25。只当「明显不及格」的粗筛，不要当能力刻度。"
        ),
    },
    "eduguard_adversarial": {
        "kind": "none",
        "metric": "extra:overall.asr",
        "value": None,
        "label": "无公认门槛",
        "source": "EduGuardBench, arXiv:2511.06890",
        "note": (
            "越狱抵抗没有行业通行的可接受 ASR 数值，任何 5% 之类的线都是我们自己拍的。"
            "该指标越低越好，理想值 0；论文只给了 judge 与人类标注的校准 kappa"
            "（有害性 0.882 / 拒答质量 0.874），那是 judge 质量不是模型可用线。"
        ),
    },
    "ifeval": {
        "kind": "none",
        "metric": "extra:prompt_strict_accuracy",
        "value": None,
        "label": "无公认门槛",
        "source": "IFEval",
        "note": (
            "指令都可程序化验证，认真执行的人接近 1.0，但那是构造性上限不是实测；"
            "业界也没有「指令遵循到几分算能上线」的标准。留空。"
        ),
    },
    "tutorbench": {
        "kind": "none",
        "metric": "extra:arr_w_x100",
        "value": None,
        "label": "无公认门槛",
        "source": "TutorBench, arXiv:2510.02663",
        "note": (
            "论文只给 judge 质量（judge-人类一致 0.78、人类互评 0.75、最强单个专家 F1 0.91、"
            "judge 对多数投票 F1 0.82）和模型分（Gemini 2.5 Pro ARR_w 55.65，无前沿模型过 56），"
            "没有可用线；本地又没有专家参考回复可以过我们的 judge。"
        ),
    },
    "edubench": {
        "kind": "none",
        "metric": "extra:overall.mean_overall_score",
        "value": None,
        "label": "无公认门槛（且 judge 有约 +1 分通胀）",
        "source": "EduBench, arXiv:2505.16160",
        "note": (
            "1-10 的 judge 量表没有校准过的可用线。读分前先扣掉论文自报的约 1 分 judge 通胀，"
            "而且那个结论只建立在 198 条样本、1 名标注者上，本身也不牢。"
        ),
    },
}


def _paired_judge_gap(
    benchmark: str, raw_path: Path, resp_key: str, dims, keys, norm, per_dim_norm: bool
) -> dict[str, Any] | None:
    """Human annotation vs our LLM judge on the *same* expert replies.

    The human `pass_rate` in this file comes from human annotators; a model's
    comes from an LLM judge. Comparing them directly is only fair if the two
    raters agree — so re-score the identical items the `expert` baseline run
    used and report the gap. If it is large, the benchmark's headline is partly
    measuring the judge's stylistic preferences, not teaching quality.
    """
    item_list = ROOT / "reports" / "eval" / "_baseline" / benchmark / "expert" / "item_list.txt"
    summary_path = ROOT / "reports" / "eval" / "_baseline" / benchmark / "expert" / "summary.json"
    if not (item_list.exists() and summary_path.exists() and raw_path.exists()):
        return None
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    if summary.get("run_status") != "complete":
        return None
    extra = summary.get("extra_metrics") or {}
    wanted = set(item_list.read_text(encoding="utf-8").split())

    labelled = []
    for idx, entry in enumerate(json.loads(raw_path.read_text(encoding="utf-8"))):
        if f"c{idx}" not in wanted:
            continue
        ann = ((entry.get(resp_key) or {}).get("Expert") or {}).get("annotation") or {}
        labelled.append(
            {d: (norm(d, str(ann.get(d, ""))) if per_dim_norm else norm(str(ann.get(d, "")))) for d in dims}
        )
    if not labelled:
        return None
    n = len(labelled)
    human_pass = sum(1 for lab in labelled if all(lab.get(k) == "Yes" for k in keys)) / n

    dist = extra.get("per_dimension_distribution") or {}

    def judge_yes(dim: str):
        cell = (dist.get(dim) or {}).get("Yes")
        return cell.get("share") if isinstance(cell, dict) else cell

    return {
        "n_items": n,
        "judge_model": extra.get("judge_model"),
        "human_annotator_pass_rate": round(human_pass, 4),
        "our_judge_pass_rate": extra.get("pass_rate"),
        "per_key_dimension_yes_share": {
            dim: {
                "human_annotator": round(sum(1 for lab in labelled if lab[dim] == "Yes") / n, 4),
                "our_judge": judge_yes(dim),
            }
            for dim in keys
        },
    }


def cross_tutor_gap(judge_run: str = "minimax3") -> dict[str, Any] | None:
    """Judge-vs-human gap for every tutor in MRBench, not just the human expert.

    Free: `mrbench_judge` already had the model label all 1,655 (response x
    dimension) pairs against the human gold, covering all nine tutors. Reading
    it back tells us whether the judge is uniquely harsh on the *human* expert
    (a style bias) or merely stricter than human annotators across the board.
    It is the latter — which is why the "the judge prefers verbose LLM prose"
    reading does not survive contact with the data.

    Caveat: mrbench_judge uses the v1 rubric prompt while mrbench_tutor uses the
    evolved v2 one, so the absolute pass rates here are not interchangeable with
    the tutor runs; the per-tutor *ordering* and the sign of the gap are.
    """
    import math

    path = ROOT / "reports" / "eval" / "mrbench_judge" / judge_run / "scored.jsonl"
    if not (path.exists() and MRBENCH_FILE.exists()):
        return None
    from eval.benchmarks.mrbench import KEY_DIMENSIONS

    by_tutor: dict[str, dict[str, dict[str, tuple]]] = {}
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            row = json.loads(line)
            if row.get("score_status") != "scored":
                continue
            parts = str(row["item_id"]).split("-")
            if len(parts) < 3:
                continue
            conv, tutor, dim = parts[0], "-".join(parts[1:-1]), parts[-1]
            by_tutor.setdefault(tutor, {}).setdefault(conv, {})[dim] = (
                row.get("pred_label"),
                row.get("gold_label"),
            )

    lengths: dict[str, list[int]] = {}
    for entry in json.loads(MRBENCH_FILE.read_text(encoding="utf-8")):
        for tutor, payload in (entry.get("anno_llm_responses") or {}).items():
            text = str((payload or {}).get("response") or "").strip()
            if text:
                lengths.setdefault(tutor, []).append(len(text.split()))

    results: dict[str, Any] = {}
    for tutor, convs in by_tutor.items():
        usable = [d for d in convs.values() if all(k in d for k in KEY_DIMENSIONS)]
        if len(usable) < 20:
            continue
        n = len(usable)
        human = sum(1 for d in usable if all(d[k][1] == "Yes" for k in KEY_DIMENSIONS)) / n
        judge = sum(1 for d in usable if all(d[k][0] == "Yes" for k in KEY_DIMENSIONS)) / n
        words = lengths.get(tutor) or [0]
        results[tutor] = {
            "n": n,
            "median_words": statistics.median(words),
            "human_annotator_pass_rate": round(human, 4),
            "judge_pass_rate": round(judge, 4),
            "gap": round(judge - human, 4),
        }

    xs = [v["median_words"] for v in results.values()]
    ys = [v["gap"] for v in results.values()]
    corr = None
    if len(xs) > 2:
        mx, my = statistics.mean(xs), statistics.mean(ys)
        den = math.sqrt(sum((a - mx) ** 2 for a in xs) * sum((b - my) ** 2 for b in ys))
        if den:
            corr = round(sum((a - mx) * (b - my) for a, b in zip(xs, ys)) / den, 3)

    return {
        "judge_model_run": judge_run,
        "prompt_caveat": "mrbench_judge 用 v1 rubric，mrbench_tutor 用 v2；绝对值不可互换，方向与排序可比",
        "per_tutor": dict(sorted(results.items(), key=lambda kv: kv[1]["median_words"])),
        "length_vs_gap_pearson_r": corr,
        "reading": (
            "judge 对所有 tutor 都比人类标注者严（gap 普遍为负），并非只针对人类专家；"
            "长度与 gap 的相关很弱且方向与「judge 偏好冗长」假说相反，该假说不成立。"
        ),
    }


def judge_calibration() -> dict[str, Any]:
    from eval.benchmarks.bea2025 import DIMENSIONS as BD, KEY_DIMENSIONS as BK, _normalize_label as bnorm
    from eval.benchmarks.mrbench import DIMENSIONS as MD, KEY_DIMENSIONS as MK, _normalize_label as mnorm

    out: dict[str, Any] = {}
    got = _paired_judge_gap("mrbench_tutor", MRBENCH_FILE, "anno_llm_responses", MD, MK, mnorm, True)
    if got:
        out["mrbench_tutor"] = got
    got = _paired_judge_gap("bea2025_tutor", BEA_DEV_FILE, "tutor_responses", BD, BK, bnorm, False)
    if got:
        out["bea2025_tutor"] = got
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, default=OUT_PATH)
    args = ap.parse_args()

    computed: dict[str, Any] = {}
    if MRBENCH_FILE.exists():
        computed["mrbench_tutor"] = _mrbench_reference()
    if BEA_DEV_FILE.exists():
        computed["bea2025_tutor"] = _bea_reference()

    literature = json.loads(json.dumps(LITERATURE, ensure_ascii=False))
    for bench in ("mrbench_tutor", "bea2025_tutor"):
        expert = (computed.get(bench) or {}).get("Expert")
        if expert and bench in literature:
            literature[bench]["human"]["value"] = expert["pass_rate"]
            literature[bench]["human"]["n"] = expert["n"]

    graded = collections.Counter()
    for entry in literature.values():
        human = entry.get("human") or {}
        graded[human.get("grade") if human.get("value") is not None else "null"] += 1

    payload = {
        "version": "v2",
        "generated_by": "scripts/build_human_baselines.py",
        "schema_notes": {
            "two_tables": (
                "人类参照锚（literature / computed_from_local_data / per_task_human）与"
                "可用门槛（usability_thresholds）是两个不同的问题，分开存、分开读，永远不要合成一列。"
                "多数 benchmark 只有其中一边。"
            ),
            "grades": {
                "A": "同 benchmark、同 split、同指标，直接可比",
                "B": "同 benchmark 但 split / 子集 / 评分协议有差异，需换算或只能定性对照",
                "C": "制度性代理（考试及格线、人群均分）或构造性上限，非题级实测",
                "D": "仅作语境（SOTA 系统分、judge 可靠性、其他 benchmark），绝不当人类基线，只进 context_anchors",
            },
            "value_scale": "一律用该 benchmark headline 的原始标度，不是 0-10 归一分",
            "policy": "查不到就留 null，并在 evidence 里写清查了哪篇、结论是什么。不外推、不代用。",
        },
        "computed_from_local_data": {
            "note": COMPUTED_NOTE,
            "results": computed,
        },
        "judge_calibration_vs_human_annotators": {
            "note": (
                "同一批专家教师回复，人类标注者判 vs 我们的 LLM judge 判。"
                "差距越大，说明该 benchmark 的 headline 越是在测「像不像 LLM 的写法」而不是教学质量。"
            ),
            "results": judge_calibration(),
            "cross_tutor_control": cross_tutor_gap(),
        },
        "literature": literature,
        "per_task_human": PER_TASK_HUMAN,
        "usability_thresholds": USABILITY,
        "no_external_human_reference": SELF_BUILT,
        "coverage": {
            "with_human_value": sum(
                1 for e in literature.values() if (e.get("human") or {}).get("value") is not None
            ),
            "literature_entries": len(literature),
            "per_task_entries": len(PER_TASK_HUMAN),
            "usability_entries": len(USABILITY),
            "usability_with_value": sum(1 for e in USABILITY.values() if e.get("value") is not None),
            "no_external_reference": len(SELF_BUILT),
            "by_grade": dict(graded),
        },
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {args.out}")
    cov = payload["coverage"]
    print(f"  有人类数值的 benchmark: {cov['with_human_value']}/{len(literature)}")
    print(f"  按可比性分级: {dict(graded)}")
    print(f"  逐任务人类分: {cov['per_task_entries']} 个 benchmark")
    print(f"  有可用门槛的: {cov['usability_with_value']}/{cov['usability_entries']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
