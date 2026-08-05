#!/usr/bin/env python3
"""Human-performance anchors for the benchmarks in `reports/eval/`.

Companion to `build_benchmark_baselines.py` (which supplies the floors). This
one supplies the ceilings — and the honest answer is that for most benchmarks
there isn't one. The rule here is: **never invent a number.** A benchmark whose
paper reports no human performance gets `value: null` plus an `evidence` note
saying which paper was checked and what it did or did not say, so nobody has to
re-do the search.

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
            "note": "论文的人类评测就在 testmini 1,000 题上做，与我们的评测集完全一致。",
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
            "population": "真实考生（LSAT / SAT / 高考），50 百分位",
            "source": "AGIEval (NAACL 2024 Findings), arXiv:2304.06364；仓库 data/exhaustive_2026-05-13/results.jsonl 已收录",
            "note": (
                "论文只对 LSAT / SAT / Gaokao 这些真人考试子集给出人类分，"
                "而我们跑的 7,272 题还包含 MATH(1,000) 等无人类分的任务，"
                "所以 0.670 不能直接和我们的总 accuracy 并列，只能逐 task 对齐后使用。"
            ),
        },
        "context_anchors": [
            {"label": "Human top（前 1%）", "value": 0.910, "note": "同一来源，zero-shot 设定。"}
        ],
        "evidence": "官方 repo README 的榜单不含人类行；人类分在论文正文表格里，仓库证据库已抄录 avg 67.0 / top 91.0。",
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
            "note": "论文明说无题级人类结果，无法量化人类在这 1,119 题上的正确率。",
        },
        "context_anchors": [
            {
                "label": "智利教师专业发展考试人群均分（制度性代理，grade C）",
                "value": 0.50,
                "note": "2017-2021 共 25,000+ 名受训教师的平均预期得分，非本题集实测。",
            }
        ],
        "evidence": "已查论文：给出人群均分约 50%，同时明确声明 question-level human results are not available。",
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
                "label": "最佳参赛系统 macro-F1 区间（专用系统锚，grade D，非人类）",
                "value": None,
                "note": (
                    "四个教学能力赛道三分类 macro-F1 最好成绩在 58.34（Providing Guidance）"
                    "到 71.81（Mistake Identification）之间，50+ 支队伍参赛。"
                    "我们最好的 recommended_judge_score 是 0.549（glm-5.2），"
                    "在专用微调系统的区间下沿。"
                ),
            }
        ],
        "evidence": "已查 Findings 论文：给出各赛道最佳系统分与参赛规模，未给人类基线。",
    },
    "tutorbench": {
        "headline": "extra:arr_w_x100",
        "human": {
            "value": None,
            "grade": None,
            "source": "TutorBench (Scale AI), arXiv:2510.02663",
            "note": "论文未报人类专家在 ARR_w 上的得分。",
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
}

# Self-built or repo-internal item sets: there is no external human study to look
# up, and inventing one would be worse than an honest blank.
SELF_BUILT: dict[str, str] = {
    "edubench": "外部数据集（github.com/ybai-nlp/EduBench），但评分完全靠 LLM judge 打 12 维 1-10 分，论文与仓库均无人类得分；量表下限是 1，需靠退化基线定地板。",
    "eduillustrate": "仓库自建题集 + 自建 judge rubric，无外部人类参照。",
    "longtutor_evidence": "仓库自建，无外部人类参照。",
    "longtutor_diagnosis": "仓库自建，无外部人类参照。",
    "longtutor_teaching": "仓库自建，无外部人类参照；且其 accuracy 实为解析成功率（实跑 0.999-1.000），无区分度。",
    "mooccube_prereq": "仓库自建（基于 MOOCCube 图谱派生），无外部人类参照；已内建 chance correction。",
    "p07_selfcheck": "仓库自建复合指标，无人类对照概念；平凡策略地板 5.0/10。",
    "p08_calibration": "仓库自建复合指标，无人类对照概念；平凡策略地板 5.0/10。",
    "p08_abstention": "题目来自 UMWP（github.com/Yuki-Asuuna/UMWP），但 headline 是仓库自建复合指标，无人类对照；任何与题无关的策略都恰好 5.0/10。",
    "mmtutorbench_judge_calibration": "公开 JSONL 无 per-item 人类金标，adapter 本身不产出题目。",
    "mathtutorbench_judge_calibration": "官方 A/B 偏好对，金标即人类偏好，无「人类得分」概念。",
    "mathtutorbench_problem_solving": "GSM8K 派生，官方无人类基线（GSM8K 原论文的人类基线针对完整数据集，非此子集）。",
    "mathtutorbench_mistake_correction": "同上。",
    "mathtutorbench_socratic": "BLEU 对参考问句，人类改述同样拿不到高 BLEU，该指标无人类上限意义。",
    "mathtutorbench_mistake_location": "标注金标即人类判断，论文未报人类复现分。",
    "mathtutorbench_solution_correctness": "同上。",
    "mathtutorbench_pedagogy": "与金标教师回应成对比较，win_rate 0.5 即「与专家教师打平」——该基准的人类锚天然是 0.5。",
    "mathtutorbench_pedagogy_hard": "同上，人类锚 = win_rate 0.5。",
    "mathtutorbench_scaffolding": "同上，人类锚 = win_rate 0.5。",
    "mathtutorbench_scaffolding_hard": "同上，人类锚 = win_rate 0.5。",
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
        "version": "v1",
        "generated_by": "scripts/build_human_baselines.py",
        "schema_notes": {
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
        "no_external_human_reference": SELF_BUILT,
        "coverage": {
            "with_human_value": sum(
                1 for e in literature.values() if (e.get("human") or {}).get("value") is not None
            ),
            "literature_entries": len(literature),
            "no_external_reference": len(SELF_BUILT),
            "by_grade": dict(graded),
        },
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {args.out}")
    print(f"  有人类数值的 benchmark: {payload['coverage']['with_human_value']}/{len(literature)}")
    print(f"  按可比性分级: {dict(graded)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
