#!/usr/bin/env python3
"""Build intermediate artifacts for atomic-ability rebenchmark analysis.

This script is intentionally conservative: it does not compute a final radar
score yet. It creates the auditable middle layer needed before scoring:

- inclusion policy
- benchmark/subdimension to P01-P22 mapping
- metric normalization rules
- current eval-run inventory with inclusion/exclusion flags
- open calibration questions
"""

from __future__ import annotations

import html
import json
import re
import statistics
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "atomic_ability_rebenchmark"
EVAL_DIR = ROOT / "reports" / "eval"
OTHER_DIR = ROOT / "otherbenchmark"

EDUGUARD_P2_PRIMARY_JUDGE = "deepseek-v3.2 judge"
# R23：judge 类 benchmark 不再全局排除——P10「主观题评价能力」的被测构念就是判卷能力，
# 在该 P 上 judge 数据构念对口应当计分（R19 已判定 rel 0.45 并正式入列，R20 全局规则一刀切
# 把它永久化了）。排除改由格级 cell["excluded"] 标记承担，构念错位的挂载（原 P09c/P17a）
# 已在 v6 JSON 中直接删除。名单保留为空以备将来 benchmark 级排除之需。
EXCLUDED_SCORING_BENCHMARKS: set[str] = set()

# 走 gateway 收到图不报错但看不见的模型（见记忆 gateway-model-vision-capability，
# 实测 2026-07）；其多模态子集分数是盲答废分，不得作为视觉证据（R22）。
BLIND_VISION_MODELS = {"deepseek-v4-pro"}

# 发布面板（与 build_atomic_ability_html_report.py 的 RELEASE_MODELS 保持一致）。
# R26 缺测处理只对这些模型逐格判定，顺路导入的外围模型不铺行。
PANEL_MODEL_KEYS = (
    "minimax-m3",
    "minimax-m2.7",
    "deepseek-v4-pro",
    "glm-5.2",
    "doubao-seed-2-0-pro",
    # 2026-08-17 加入发布面板（与 RELEASE_MODELS 同步）。vision=True，所以不会
    # 产生 capability_gap 零分格，缺的格子一律记 untested。
    "qwen-qwen3-5-4b",
)

# ---------------------------------------------------------------------------
# R26（2026-08-04，用户裁决）：废除 R22 的「缺格取该格已测模型最低分顶替」。
#
# 那条规则把两种性质完全不同的空白揉成了一个数字：没排上队跑（测量缺口）和
# 模型压根干不了这件事（能力缺失）。顶替值既不是该模型的成绩，也不是诚实的
# 空白——它让 MiniMax-M2.7/GLM-5.2/DeepSeek-V4-Pro 的 P03 多模态理解拿到了
# 5.08 分，而这三个模型连图都收不进去。
#
# 新口径，缺格分两类：
#   1) untested（未测过）：没跑过，不计分、不进分母，写进
#      09_atomic_p_untested_cells.jsonl，报告里显式写「未测过」。
#      P 分数因此可能为 None——那就是「未测过」，不是 0。
#   2) capability_gap（能力不具备）：模型缺该格必需的输入/输出能力（当前只有
#      视觉一项），跑不了不是排期问题而是能力问题，记 0 分并进聚合。
#
# 判定落在 **benchmark 格子** 上，不落在 P 上（用户裁决 2026-08-04）：某个格子
# 因能力缺失跑不了就是 0 分，这个 0 按 doc/atomic_ability_mapping_v6_2026-07-19.md
# 的常规权重规则（相关度 × 置信度、facet 内加权、跨 facet 等权）传导到它挂载的
# 每一个 P。所以 mathvista/k12vista 这类既挂 P03 又搭车挂 P05/P06 的格，0 分会
# 同时进这几个 P——这是刻意的，不做构念范围的特殊豁免。
#
# 但 2) 的前提是「真的跑不了」：只有整套题都必须有该能力才能作答的格子才算
# （REQUIRE_ALL）。部分题需要视觉、文本模型仍能拿到真实非零分的格子标
# REQUIRE_PARTIAL，按未测过处理——那里的 0 是测量假象，不是能力差距。
# ---------------------------------------------------------------------------

REQUIRE_ALL = "required_all"
REQUIRE_PARTIAL = "required_partial"

# 模型能力探测结果。True 有 / False 没有 / None 未探测（未探测一律不判 0）。
# 视觉一列来自 2026-07-13 用 K12Vista 真题图逐个探测（记忆
# gateway-model-vision-capability）：deepseek-v4-pro 收图不报错但回「你没有上传
# 图片」，glm-5.2 网关直接 400，MiniMax-M2.7 纯文本。
MODEL_CAPABILITIES: dict[str, dict[str, bool | None]] = {
    "minimax-m3": {"vision": True},
    "minimax-m2.7": {"vision": False},
    "glm-5.2": {"vision": False},
    "deepseek-v4-pro": {"vision": False},
    "doubao-seed-2-0-pro": {"vision": True},
    "doubao-seed-2-0-lite": {"vision": True},
    "kimi-k2-6": {"vision": True},
    # 2026-08-10 实测自建 vLLM 部署（记忆 vllm-selfhosted-qwen35-4b）：架构是
    # Qwen3_5ForConditionalGeneration，带 vision_config，vLLM 启动日志确认视觉塔已加载
    # （MMEncoderAttention + 16384 token 编码器缓存）。两张自造数字图 7492/3185 都读对，
    # mathvista 走 harness 三题全部 status=ok 且 prompt_tokens 随图大小变化。
    "qwen-qwen3-5-4b": {"vision": True},
    # Qwen3-8B 是纯文本模型：SiliconFlow 喂图直接返回 code 20041 The model is not a VLM。
    "qwen-qwen3-8b": {"vision": False},
}

# 格子对模型能力的硬性要求。键可以是 benchmark_id，也可以是
# (benchmark_id, subdimension)——后者更具体、优先匹配（olympiadbench 总分混模态，
# 但它的多模态子集那一格是纯图题）。
CELL_CAPABILITY_REQUIREMENTS: dict[Any, tuple[str, str]] = {
    "mathvista": ("vision", REQUIRE_ALL),
    "k12vista": ("vision", REQUIRE_ALL),
    "mmtutorbench": ("vision", REQUIRE_ALL),
    # eduillustrate 也吃图，别被"输出 Manim 代码"骗了：230/230 道题都带 base64 题图，
    # 生成链路在出提纲（explanation_planner.py:168/271）和写代码（code_generator.py:443/564/582）
    # 两处都把图发给被测模型；题干文本只有 question，`img_caption` 不进 prompt，
    # 图是图形条件的唯一来源。8 个判分维度里还有 4 个是视觉侧。
    "eduillustrate": ("vision", REQUIRE_ALL),
    # olympiadbench 的多模态子集看着像硬门槛，其实不是：R22 的盲测对照发现看不见图的
    # deepseek-v4-pro 在该子集拿 0.658、明眼的 M3 拿 0.681——题干文本自带足够信息，
    # 盲模型照样能作答。所以这不是「能力缺失跑不了」，标 PARTIAL 走未测过；那份盲答
    # 分本身另有 BLIND_VISION_MODELS 按废分丢弃。
    "olympiadbench": ("vision", REQUIRE_PARTIAL),
    # TutorBench Fair815 只有一部分题带图，纯文本的 qwen3.5-27B / gpt-5.5 都有真实分数。
    "tutorbench": ("vision", REQUIRE_PARTIAL),
}


def cell_capability_requirement(benchmark_id: str, subdimension: str) -> tuple[str, str] | None:
    """Return (capability, strictness) required by this cell, if any."""
    return CELL_CAPABILITY_REQUIREMENTS.get((benchmark_id, subdimension)) or CELL_CAPABILITY_REQUIREMENTS.get(
        benchmark_id
    )


def missing_cell_verdict(model_key: str, benchmark_id: str, subdimension: str) -> tuple[str, str, str]:
    """Classify why `model_key` has no score for this cell.

    Returns ``(status, capability, reason)`` where status is ``capability_gap``
    (score 0, counts) or ``untested`` (no score, does not count).
    """
    requirement = cell_capability_requirement(benchmark_id, subdimension)
    if requirement is None:
        return "untested", "", "该格无能力门槛，缺分数纯属未测"
    capability, strictness = requirement
    has = MODEL_CAPABILITIES.get(model_key, {}).get(capability)
    if has is not False:
        note = "能力未探测" if has is None else "具备该能力"
        return "untested", capability, f"{note}，缺分数属未测"
    if strictness != REQUIRE_ALL:
        return (
            "untested",
            capability,
            f"缺 {capability}，但该格只有部分题需要该能力，记 0 会低估真实水平——按未测过处理",
        )
    return "capability_gap", capability, f"该格全部题目需要 {capability}，模型不具备，记 0 分"

# R20 (2026-07-18): P codes follow the v5 doc scheme (P01-P20, no tombstones);
# the four-level evidence_tier system is removed — discounting lives solely in
# default_benchmark_weight (confidence) and cell weight (relevance).  Judge
# tasks stay out of scoring via EXCLUDED_SCORING_BENCHMARKS + zero confidence
# weight + the cells' explicit "excluded" marker.
#
# R25 (2026-07-19): both weights become rule-derived, not hand-tuned.
#   relevance (cell weight, in the JSON): five tiers 1.0 / 0.8 / 0.5 / 0.2 / 0
#     (0 = not mounted, an exclusion rather than a weight).
#   confidence (default_benchmark_weight, below): start at 1.0, two factors
#     deduct 0.15 each —
#       scoring method: objective rule scoring deducts nothing; LLM-as-judge
#         deducts.  Classify by the *actual* scoring path, not the benchmark's
#         nominal description: an LLM that only extracts an answer which a rule
#         then compares against gold stays objective (mmlu_pro fallback,
#         eduguard_sata verbose replies, mathvista's official protocol);
#         longtutor_evidence emits CORRECT/INCORRECT itself, so it is a judge.
#       quality: externally vetted data and gold (official release, peer review,
#         human annotation) deducts nothing; self-built and self-judged, with
#         gold vetted only in-repo, deducts.
#   Result is four values: 1.0 / 0.85 / 0.7, plus the single exception
#   edubench·error_identification_correction_accuracy = 0.3 (R23).  Contamination
#   risk and measured judge noise (judge-swap, kappa, BLEU validity) are
#   deliberately kept out of the weights and live in rationale notes only.

ABILITY_PRIORITY = {
    "P01": 0.45,
    "P02": 0.65,
    "P03": 0.70,
    "P05": 0.55,
    "P06": 0.65,
    "P07": 0.75,
    "P08": 0.95,
    "P09": 0.95,
    "P10": 0.95,
    "P11": 0.90,
    "P12": 0.90,
    "P13": 0.90,
    "P14": 0.95,
    "P15": 0.95,
    "P16": 0.95,
    "P04": 0.90,
    "P17": 0.90,
    "P18": 0.95,
    "P19": 1.00,
    "P20": 0.95,
}

# R24 编号迁移后：P02 长上下文 / P09 工具 / P13 画像 / P15 路径 / P04 多模态生成 / P19 处置 / P20 诚信
P_GAP_BONUS = {"P02", "P09", "P13", "P15", "P04", "P19", "P20"}


P_GROUPS = {
    "P01": ("SRG", "指令与约束遵循"),
    "P02": ("SRG", "长上下文与证据定位"),
    "P03": ("SRG", "多模态理解"),
    "P05": ("FDR", "知识调用与掌握"),
    "P06": ("FDR", "推理与生成"),
    "P07": ("FDR", "自我校验与修正"),
    "P08": ("FDR", "置信度校准与弃答"),
    "P09": ("FDR", "工具使用与长程智能体执行"),
    "P10": ("LAD", "错误诊断"),
    "P11": ("LAD", "主观题评价能力"),
    "P12": ("LAD", "命题与作业设计"),
    "P13": ("CLM", "学习者画像建模"),
    "P14": ("CLM", "个性化教学策略选择"),
    "P15": ("CLM", "学习路径规划（知识结构层）"),
    "P16": ("CLM", "适配性解释与反馈生成"),
    "P04": ("SRG", "多模态生成"),  # R23 改制 + R24 迁号（原 P16）
    "P17": ("CEG", "教育角色边界判断"),
    "P18": ("CEG", "学生风险识别"),
    "P19": ("CEG", "安全处置选择"),
    "P20": ("CEG", "学术诚信与作答真实性判定"),
}


MEASUREMENT_MODEL_PATH = ROOT / "data" / "mapping_measurement_model_v6.json"

# Benchmark-level metadata joined onto measurement-model cells to form MAPPINGS
# rows.  Ability weights and facets live in
# ``data/mapping_measurement_model_v6.json`` (single source of truth,
# adjudicated 2026-07-15/16/17; R17 merged P11/P12/P13 into P11, R18 added
# P23, R19 re-adjudicated facet structures across ten Ps); this table only
# carries what the JSON deliberately does not: display name, ingestion scope,
# metric family per subdimension ("*" = all subdimensions), benchmark-level
# confidence weight (with per-subdimension overrides), and the benchmark-level
# rationale.
#
# Since R25 every default_benchmark_weight is derived from the two-factor rule
# documented above, so it must not be hand-tuned per benchmark: to change one,
# change its scoring-method or quality classification and say why.  Exactly one
# per-subdimension override survives (edubench error_identification, R23); the
# rest were folded into the benchmark-level rule values.
BENCHMARK_META: dict[str, dict[str, Any]] = {
    "mmlu_pro": {
        "benchmark_name": "MMLU-Pro",
        "source_scope": "repo_eval",
        "score_direction": "higher_better",
        "default_benchmark_weight": 1.0,
        "metric_family": {"*": "accuracy"},
        "rationale": "基础学科知识与选择题答题能力，主要验证 LLM 答题门槛，不应主导教育能力雷达图。R22：0.35→0.7——精确匹配判分最硬却被压到低于裁判天花板分的 edubench，倒挂；护栏由映射结构（不挂教育侧 P）承担。",
    },
    "ceval": {
        "benchmark_name": "C-EVAL",
        "source_scope": "repo_eval",
        "score_direction": "higher_better",
        "default_benchmark_weight": 1.0,
        "metric_family": {"*": "accuracy"},
        "rationale": "中文考试与学科知识，属于基础答题门槛；对应知识调用、推理和选项约束遵循。R22：0.35→0.7，与 mmlu_pro 同批调整（判分硬度倒挂修正）。",
    },
    "agieval": {
        "benchmark_name": "AGIEval",
        "source_scope": "repo_eval",
        "score_direction": "higher_better",
        "default_benchmark_weight": 1.0,
        "metric_family": {"*": "accuracy"},
        "rationale": "标准化考试推理与答题，仍是 LLM 答题能力门槛。R22：0.4→0.7，与 mmlu/ceval 同族（考试 MCQ、官方解析、精确匹配）跟随同档。",
    },
    "olympiadbench": {
        "benchmark_name": "OlympiadBench",
        "source_scope": "repo_eval",
        "score_direction": "higher_better",
        "default_benchmark_weight": 1.0,
        "metric_family": {"*": "accuracy"},
        "rationale": "高难学科推理和多模态竞赛题，答题能力未完全饱和；仍作为门槛/诊断而非教育核心。R22：0.55→0.7——解题簇唯一未饱和、真正承担区分度的证据不应压最低档；污染风险低于 mmlu。",
    },
    "mathvista": {
        "benchmark_name": "MathVista",
        "source_scope": "repo_eval",
        "score_direction": "higher_better",
        "default_benchmark_weight": 1.0,
        "metric_family": {"*": "accuracy"},
        "rationale": "静态图文数学题，主要测多模态理解（解题图像 facet）、数学推理和知识调用。",
    },
    "pedagogy_benchmark": {
        "benchmark_name": "Pedagogy Benchmark",
        "source_scope": "otherbenchmark",
        "score_direction": "higher_better",
        "default_benchmark_weight": 1.0,
        "metric_family": {
            "CDPK teaching knowledge selection": "accuracy",
            "SEND special education needs selection": "accuracy",
            "CDPK/SEND aggregate from 0701 card": "accuracy_percent",
        },
        "rationale": "教学法知识选择题，既有教育知识，也有教学策略选择；R8 裁决后不再挂 P06。",
    },
    "asap_2": {
        "benchmark_name": "ASAP 2.0",
        "source_scope": "otherbenchmark",
        "score_direction": "higher_better",
        "default_benchmark_weight": 1.0,
        "metric_family": {"*": "qwk_0_to_100"},
        "rationale": "作文评分一致性主要是主观题 rubric 评分（学业作答 facet），同时需要定位文本证据与写作知识。",
    },
    "sas_bench": {
        "benchmark_name": "SAS-Bench",
        "source_scope": "otherbenchmark",
        "score_direction": "higher_better",
        "default_benchmark_weight": 1.0,
        "metric_family": {"*": "score_0_to_100"},
        "rationale": "简答题评分三指标：QWK 总分评分一致性、CCS 分步踩分、ECS 错因诊断一致性（P11c 核心锚）。",
    },
    "edubench": {
        "benchmark_name": "EduBench",
        "source_scope": "otherbenchmark",
        "score_direction": "higher_better",
        "default_benchmark_weight": 0.85,
        "benchmark_weight_overrides": {
            # R25 唯一例外（R23 裁决）：换裁判 ρ≤0.14，全仓噪声最实锤的格。
            "error_identification_correction_accuracy (metric)": 0.3,
        },
        "metric_family": {"*": "likert_0_to_10"},
        "rationale": (
            "R1 裁决：不再按 5 任务均分挂 P，改按 12 个原生裁判指标逐维度取分"
            "（instruction_following / content_relevance_scope_control 两指标无独立信息不挂）。"
            "数据源是同事的逐题原始判分（reports/eval/edubench/，裁判 deepseek-v3.2，原论文设定），"
            "指标级均值由 scripts/build_edubench_metric_summaries.py 派生到 _metrics/。"
            "方法学注记：error_identification_correction_accuracy 换裁判 ρ≤0.14；知识类指标天花板，门槛性质。"
        ),
    },
    "tutorbench": {
        "benchmark_name": "TutorBench",
        "source_scope": "otherbenchmark",
        "score_direction": "higher_better",
        "default_benchmark_weight": 0.85,
        "metric_family": {"*": "score_0_to_100"},
        "rationale": "真实多模态 tutor 质量综合考察反馈生成、策略选择和图文感知。R22：1.0→0.8——分数混教学回复质量方差（P03 facet 注记的代理性质）且模型面与主面板不重叠，满置信不自洽。",
    },
    "mathtutorbench_problem_solving": {
        "benchmark_name": "MathTutorBench",
        "source_scope": "repo_eval",
        "score_direction": "higher_better",
        "default_benchmark_weight": 1.0,
        "metric_family": {"*": "accuracy"},
        "rationale": "数学求解门槛，重要但不能证明会辅导。",
    },
    "mathtutorbench_solution_correctness": {
        "benchmark_name": "MathTutorBench",
        "source_scope": "repo_eval",
        "score_direction": "higher_better",
        "default_benchmark_weight": 1.0,
        "metric_family": {"*": "accuracy_or_f1"},
        "rationale": "给定参考/学生解判断正确性，主测作答正误判定。",
    },
    "mathtutorbench_mistake_location": {
        "benchmark_name": "MathTutorBench",
        "source_scope": "repo_eval",
        "score_direction": "higher_better",
        "default_benchmark_weight": 1.0,
        "metric_family": {"*": "accuracy_or_f1"},
        "rationale": "错误位置定位是 P11b（原 P12）的直接测量。",
    },
    "mathtutorbench_mistake_correction": {
        "benchmark_name": "MathTutorBench",
        "source_scope": "repo_eval",
        "score_direction": "higher_better",
        "default_benchmark_weight": 1.0,
        "metric_family": {"*": "accuracy"},
        "rationale": "纠错需要识别错因并生成可用修正/反馈；R6 裁决错因归因（原 P13，现 P11c）权重 0.45→0.20（只测改对与否）。",
    },
    "mathtutorbench_pedagogy": {
        "benchmark_name": "MathTutorBench",
        "source_scope": "repo_eval",
        "score_direction": "higher_better",
        "default_benchmark_weight": 0.85,
        "metric_family": {"*": "win_rate_or_accuracy"},
        "rationale": "教学法指令遵循主测策略选择和适配反馈。",
    },
    "mathtutorbench_pedagogy_hard": {
        "benchmark_name": "MathTutorBench",
        "source_scope": "repo_eval",
        "score_direction": "higher_better",
        "default_benchmark_weight": 0.85,
        "metric_family": {"*": "win_rate_or_accuracy"},
        "rationale": "hard 子集较有区分度，权重略高。",
    },
    "mathtutorbench_scaffolding": {
        "benchmark_name": "MathTutorBench",
        "source_scope": "repo_eval",
        "score_direction": "higher_better",
        "default_benchmark_weight": 0.85,
        "metric_family": {"*": "win_rate_or_accuracy"},
        "rationale": "脚手架主测下一步教学干预选择与反馈生成。",
    },
    "mathtutorbench_scaffolding_hard": {
        "benchmark_name": "MathTutorBench",
        "source_scope": "repo_eval",
        "score_direction": "higher_better",
        "default_benchmark_weight": 0.85,
        "metric_family": {"*": "win_rate_or_accuracy"},
        "rationale": "hard 子集仍主测教学干预与反馈。",
    },
    "mathtutorbench_socratic": {
        "benchmark_name": "MathTutorBench",
        "source_scope": "repo_eval",
        "score_direction": "higher_better",
        "default_benchmark_weight": 1.0,
        "metric_family": {"*": "bleu_0_to_1"},
        "rationale": (
            "生成引导性提问、与教师金标问题比 BLEU，是 P17a（提问式干预）的测量来源"
            "（R11 补挂，2026-07-12；按拆分准入规则提问不单列子能力）。BLEU 对合理的不同问法会误罚，权重保守。"
        ),
    },
    "bea2025_judge": {
        "benchmark_name": "BEA 2025 Judge",
        "source_scope": "repo_eval",
        "score_direction": "higher_better",
        "default_benchmark_weight": 1.0,
        "metric_family": {"*": "accuracy"},
        "rationale": (
            "作为教育评判者逐维度标注 tutor 回复，与人类标注算一致率/macro-F1/kappa。"
            "R23：仅在「主观题评价能力」P 计分（该 P 的被测构念就是判卷能力；见 mrbench_judge 条目）。"
            "取分用 extra_metrics.recommended_judge_score（官方口径：四维 exact macro-F1 均值，"
            "抗类别不平衡，优于裸 accuracy）。置信 0.0→0.75。"
        ),
    },
    "bea2025_tutor": {
        "benchmark_name": "BEA 2025 Tutor",
        "source_scope": "repo_eval",
        "score_direction": "higher_better",
        "default_benchmark_weight": 0.85,
        "metric_family": {"*": "share_0_to_1"},
        "rationale": (
            "生成 tutor 回复、固定裁判逐维度标注。R2 裁决：复合 pass rate 换单维度 Yes 占比"
            "（Mistake_Identification→P11c、Providing_Guidance→P17、Actionability→P18 减半权重，κ 0.22 校准弱）。"
            "仅 3 个模型面（缺 deepseek-v4-pro / doubao-seed-2.0-pro 生成，2026-07-16 决定不补跑）。"
        ),
    },
    "mrbench_judge": {
        "benchmark_name": "MRBench Judge",
        "source_scope": "repo_eval",
        "score_direction": "higher_better",
        "default_benchmark_weight": 1.0,
        "metric_family": {"*": "accuracy"},
        "rationale": (
            "多维 tutor 回复评判（被测模型自己当裁判，与人类标注算一致率/macro-F1/kappa）。"
            "R23：仅在 P10「主观题评价能力」计分——该 P 的被测构念就是判卷能力，"
            "与已计分的 sas_bench CCS 同属『按维度分解评判 + 与人类标注算一致性』这类操作"
            "（R19 定的 facet 划分轴是评分操作类型，不是评分对象）。"
            "置信 0.0→0.75：人类标注锚定的一致率统计，与 CCS 0.95、asap_2 0.8 同族，"
            "因裁判协议自身噪声折价一档。构念错位的原 P09c/P17a 挂载已删除。"
        ),
    },
    "mrbench_tutor": {
        "benchmark_name": "MRBench Tutor",
        "source_scope": "repo_eval",
        "score_direction": "higher_better",
        "default_benchmark_weight": 0.85,
        "metric_family": {"*": "share_0_to_1"},
        "rationale": (
            "tutor 回复生成、固定裁判 8 维标注。R2 裁决：复合 pass rate 换单维度分"
            "（Mistake_Identification/Providing_Guidance/Actionability 用 Yes 占比）。"
            "R19：Tutor_Tone 一份标注取两个统计量——P20 边界用 1−Offensive，"
            "P18 语气支持用 Encouraging 占比（替换原 Encouraging+0.5×Neutral 单格，去重）。"
            "仅 3 个模型面（2026-07-16 决定不补跑）。"
        ),
    },
    "eduguard_sata": {
        "benchmark_name": "EduGuard-Bench P1",
        "source_scope": "repo_eval_and_otherbenchmark",
        "score_direction": "higher_better",
        "default_benchmark_weight": 1.0,
        "metric_family": {"*": "rfs_0_to_1"},
        "rationale": "教学伤害全选题同时测试角色边界、风险识别和处置选择；R10：三 P 知识 facet 同源，不构成互证。",
    },
    "eduguard_adversarial": {
        "benchmark_name": "EduGuard-Bench P2",
        "source_scope": "repo_eval_and_otherbenchmark",
        "score_direction": "lower_better",
        "default_benchmark_weight": 0.85,  # R23: 0.7→0.8
        "metric_family": {
            "Adversarial Safety ASR": "asr_0_to_1_lower_better",
            "Refusal quality distribution": "share_0_to_1",
        },
        "rationale": "对抗安全主要测安全处置（R7：拒答质量主挂 P22，P18 副挂降 0.10），同时需要识别风险和维持教育角色边界。",
    },
    "eduillustrate": {
        "benchmark_name": "EduIllustrate",
        "source_scope": "repo_eval",
        "score_direction": "higher_better",
        "default_benchmark_weight": 0.7,
        "metric_family": {"*": "likert_0_to_5"},
        "rationale": "教学图示/图文协同生成直接测多模态教学产物生成；R5 后不再挂 P03（理解侧）。",
    },
    "mmtutorbench": {
        "benchmark_name": "MMTutorBench",
        "source_scope": "repo_eval",
        "score_direction": "higher_better",
        "default_benchmark_weight": 0.85,
        "metric_family": {"*": "score_0_to_6"},
        "rationale": "多模态 tutor 综合测图文感知、反馈生成和策略选择；当前小样本默认排除主图。",
    },
    "ifeval": {
        "benchmark_name": "IFEval",
        "source_scope": "repo_eval",
        "score_direction": "higher_better",
        "default_benchmark_weight": 1.0,
        "metric_family": {"*": "accuracy"},
        "rationale": (
            "可验证指令的规则判分（官方 checker，无裁判），P01 的首个直接测量"
            "（2026-07-12 缺口填补，R13：edubench 裁判打的指令遵循分在模型排名上无独立信息量）。"
            "通用指令非教育语境，作 P01 操作基座的门槛证据。"
        ),
    },
    "k12vista": {
        "benchmark_name": "K12Vista",
        "source_scope": "repo_eval",
        "score_direction": "higher_better",
        "default_benchmark_weight": 0.85,
        "metric_family": {"*": "composite_0_to_10"},
        "rationale": (
            "中文 K12 图文学科题（五学科×三学段，固定 300 题分层抽样）。R15 裁决：挂 P03 学科图表 facet 0.55"
            "（P03/P04 合并后难度不再分 P）；判分用官方 rubric 的 LLM 裁判逐空 0/1，裁判未校准、"
            "仅 4 个视觉模型可跑——参考值。"
        ),
    },
    "mooccube_prereq": {
        "benchmark_name": "MOOCCube 先修关系推理",
        "source_scope": "repo_eval",
        "score_direction": "higher_better",
        "default_benchmark_weight": 0.85,
        "metric_family": {"*": "composite_0_to_10"},
        "rationale": (
            "MOOCCube（ACL 2020，学堂在线）905 条专家先修边当金标，200 道先修选择 + 100 道排序，"
            "100% 规则判分，P19（知识结构层路径规划）的首个测量。R16 裁决：P19 0.70 / P05 0.20 / P06 0.10；"
            "自建协议、无公开基线，benchmark weight 压到 0.70，参考值；"
            "『按学习者状态定制路径』是 P16×P19 组合能力，不设 P19b。"
        ),
    },
    "p07_selfcheck": {
        "benchmark_name": "P07 两轮自查",
        "source_scope": "repo_eval",
        "score_direction": "higher_better",
        "default_benchmark_weight": 0.85,
        "metric_family": {"*": "composite_0_to_10"},
        "rationale": (
            "两轮自查协议（先答题、再无提示复查），P07 的首个直接测量（2026-07-12 缺口填补）；"
            "headline=0.5×改对率+0.5×(1−改错率)，与第一轮正确率解耦。复查时对自身答案的把握"
            "与校准相通，P08 占 0.15。"
        ),
    },
    "p08_calibration": {
        "benchmark_name": "P08 置信度校准",
        "source_scope": "repo_eval",
        "score_direction": "higher_better",
        "default_benchmark_weight": 0.85,
        "metric_family": {"*": "composite_0_to_10"},
        "rationale": (
            "复用 exact-match benchmark + verbalized confidence，测“自信地教错”"
            "（CWR）与“知道自己不知道”（AUROC）；自报置信度带少量自检成分故 P07 占 0.20。"
        ),
    },
    "p08_abstention": {
        "benchmark_name": "P08 能力性弃答",
        "source_scope": "repo_eval",
        "score_direction": "higher_better",
        "default_benchmark_weight": 0.85,
        "metric_family": {"*": "composite_0_to_10"},
        "rationale": (
            "公开弃答数据集（UMWP/TreeCut）测对不可答题能否说“不会”；识别并按格式声明"
            "带少量指令遵循成分故 P01 占 0.15。与 p08_calibration 共同构成 P08 两半证据。"
        ),
    },
    "longtutor_evidence": {
        "benchmark_name": "LongTutor 证据抽取",
        "source_scope": "repo_eval",
        "score_direction": "higher_better",
        "default_benchmark_weight": 0.7,
        "metric_family": {"*": "accuracy"},
        "rationale": (
            "长学生历史（约 200 条作答记录）上的单记录提取/跨 session 推理/幻觉检查，规则+语义等价裁判。"
            "R21(2026-07-19)：按 memory_type 拆三格等权直接测量（单记录提取近天花板 0.93–0.97，"
            "跨 session 推理 0.60–0.70 与幻觉检查 0.61–0.75 才有区分度）；"
            "四模型面（M2.7 补跑后）总分 0.71–0.81 已拉开，区分度红旗解除。"
        ),
    },
    "longtutor_diagnosis": {
        "benchmark_name": "LongTutor 知识状态诊断",
        "source_scope": "repo_eval",
        "score_direction": "higher_better",
        "default_benchmark_weight": 0.85,
        "metric_family": {"*": "accuracy_or_f1"},
        "rationale": (
            "从交互历史推断学生知识状态（四类认知层失败机制），headline macro-F1。"
            "2026-07-16 裁决：P16a『知识状态估计』主挂 0.30（参考值）+ P11c（原 P13）副挂 0.10，P11b（原 P12）排除"
            "（输入无解题步骤）。注记：类别不平衡（多数类基线 acc 0.506 > 模型 0.35-0.44）；"
            "金标为特征决策矩阵+人工修订，非独立盲标。"
        ),
    },
    "longtutor_teaching": {
        "benchmark_name": "LongTutor 教学动作",
        "source_scope": "repo_eval",
        "score_direction": "higher_better",
        "default_benchmark_weight": 0.7,
        "metric_family": {"*": "likert_1_to_5"},
        "rationale": (
            "生成利用具体历史证据的教学反馈，固定裁判四维 1-5 分。2026-07-16 裁决：挂 P17 执行 facet 0.30，"
            "取 strategy_alignment + history_utilization 两维均值（coherence/appropriateness 不入分）；"
            "三模型 valid 1001、strategy_alignment 3.68-4.13 有区分度；3 模型面不补跑。"
        ),
    },
}


def _build_mappings() -> list[dict[str, Any]]:
    """Flatten the adjudicated measurement model (P -> facet -> cells) into
    benchmark-first MAPPINGS rows keyed by (benchmark_id, subdimension).

    Cell weights are used as-is as within-P ability weights (facet-relative,
    deliberately not normalized to 1 — P scores are weighted means, so only
    relative magnitude matters); each ability entry carries its facet so the
    aggregation can average within facets first (formative structure)."""
    doc = json.loads(MEASUREMENT_MODEL_PATH.read_text(encoding="utf-8"))
    grouped: dict[tuple[str, str], dict[str, Any]] = {}
    for ability in doc["abilities"]:
        for facet in ability.get("facets", []):
            for cell in facet.get("cells", []):
                benchmark_id = cell["benchmark_id"]
                meta = BENCHMARK_META.get(benchmark_id)
                if meta is None:
                    raise SystemExit(f"BENCHMARK_META missing entry for {benchmark_id}")
                key = (benchmark_id, cell["subdimension"])
                row = grouped.get(key)
                if row is None:
                    families = meta["metric_family"]
                    family = families.get(cell["subdimension"]) or families.get("*")
                    if family is None:
                        raise SystemExit(f"metric_family missing for {key}")
                    overrides = meta.get("benchmark_weight_overrides", {})
                    row = grouped[key] = {
                        "benchmark_id": benchmark_id,
                        "benchmark_name": meta["benchmark_name"],
                        "subdimension": cell["subdimension"],
                        "excluded": cell.get("excluded"),
                        "source_scope": meta["source_scope"],
                        "metric_family": family,
                        "score_direction": meta["score_direction"],
                        "default_benchmark_weight": overrides.get(
                            cell["subdimension"], meta["default_benchmark_weight"]
                        ),
                        "abilities": [],
                        "rationale": meta["rationale"],
                    }
                group, name = P_GROUPS[ability["p_code"]]
                row["abilities"].append(
                    {
                        "p_code": ability["p_code"],
                        "p_name": name,
                        "group": group,
                        "weight": cell["weight"],
                        "facet_id": facet["facet_id"],
                        "facet_name": facet.get("facet_name", facet["facet_id"]),
                        "excluded": cell.get("excluded"),
                        "cell_rationale": cell.get("revision_rationale", ""),
                    }
                )
    return [grouped[key] for key in sorted(grouped)]


MAPPINGS: list[dict[str, Any]] = _build_mappings()


NORMALIZATION = [
    ("accuracy_percent", "higher_better", "score_10 = percent / 10"),
    ("accuracy", "higher_better", "score_10 = accuracy * 10"),
    ("pass_rate", "higher_better", "score_10 = pass_rate * 10"),
    ("rfs_0_to_1", "higher_better", "score_10 = rfs * 10"),
    ("asr_0_to_1_lower_better", "lower_better", "score_10 = (1 - asr) * 10"),
    ("score_0_to_100", "higher_better", "score_10 = raw / 10"),
    ("qwk_0_to_100", "higher_better", "score_10 = qwk / 10"),
    ("mean_0_to_10", "higher_better", "score_10 = raw"),
    ("likert_0_to_10", "higher_better", "score_10 = raw"),
    ("likert_0_to_5", "higher_better", "score_10 = raw * 2"),
    ("score_0_to_6", "higher_better", "score_10 = raw / 6 * 10"),
    ("accuracy_or_f1", "higher_better", "prefer official f1/accuracy in extra_metrics when present; else accuracy * 10"),
    ("win_rate_or_accuracy", "higher_better", "prefer win_rate/strict_win_rate when present; else accuracy * 10"),
    ("share_0_to_1", "higher_better", "score_10 = share * 10"),
    ("bleu_0_to_1", "higher_better", "score_10 = bleu * 10 (absolute level is low by construction; rank information only)"),
    ("likert_1_to_5", "higher_better", "score_10 = (raw - 1) / 4 * 10 (judge scale where 1 is the floor, e.g. longtutor_teaching)"),
    ("composite_0_to_10", "higher_better", "score_10 = raw (adapter already emits a 0-10 headline, e.g. P08 calibration/abstention)"),
    ("legacy_axis_0_to_100", "higher_better", "score_10 = raw / 10; context only, not used for P scoring"),
]


def dump_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text("\n".join(json.dumps(r, ensure_ascii=False, sort_keys=True) for r in rows) + "\n", encoding="utf-8")


def strip_tags(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text)
    return html.unescape(text).strip()


def parse_markdown_table(lines: list[str], start_index: int) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in lines[start_index:]:
        if not line.strip():
            if rows:
                break
            continue
        if not line.lstrip().startswith("|"):
            if rows:
                break
            continue
        cells = [c.strip().strip("*") for c in line.strip().strip("|").split("|")]
        if set(cells[0].replace(":", "").replace("-", "").strip()) <= {""}:
            continue
        if all(set(c.replace(":", "").replace("-", "").strip()) <= {""} for c in cells):
            continue
        rows.append(cells)
    if rows and all(cells in {"排名", "模型名称", "模型", "得分", "综合得分 (Mean)", "QWK (打分准确度)", "CCS (分步踩分准确度)", "ECS (错因诊断准确度)"} for cells in rows[0]):
        return rows[1:]
    return rows[1:] if rows else rows


def add_score(
    rows: list[dict[str, Any]],
    *,
    source_path: str,
    benchmark_id: str,
    benchmark_name: str,
    subdimension: str,
    model: str,
    metric: str,
    value: float,
    notes: str = "",
    score_role: str = "scoring_candidate",
    judge_model: str = "rule_or_unknown",
) -> None:
    rows.append(
        {
            "source_path": source_path,
            "benchmark_id": benchmark_id,
            "benchmark_name": benchmark_name,
            "subdimension": subdimension,
            "model": model,
            "metric": metric,
            "raw_value": value,
            "notes": notes,
            "score_role": score_role,
            "judge_model": judge_model,
        }
    )


def parse_edubench_scores(rows: list[dict[str, Any]]) -> None:
    path = OTHER_DIR / "edubench-0625.md"
    if not path.exists():
        return
    lines = path.read_text(encoding="utf-8").splitlines()
    current_subdimension: str | None = None
    subdim_by_heading = {
        "启发式解答": "IP idea provision / heuristic answer",
        "个性化内容生成": "PCC pedagogical/personalized content creation",
        "个性化学习支持": "PLS personalized learning support",
        "题目生成": "QG question generation",
        "教学材料生成": "TMG teaching material generation",
    }
    for i, line in enumerate(lines):
        if line.startswith("### "):
            current_subdimension = None
            for marker, subdim in subdim_by_heading.items():
                if marker in line:
                    current_subdimension = subdim
                    break
        if current_subdimension and line.strip().startswith("| 排名 | 模型 | 得分 |"):
            for cells in parse_markdown_table(lines, i):
                if len(cells) >= 3 and cells[0] != "排名":
                    try:
                        value = float(cells[2])
                    except ValueError:
                        continue
                    add_score(
                        rows,
                        source_path=path.relative_to(ROOT).as_posix(),
                        benchmark_id="edubench",
                        benchmark_name="EduBench",
                        subdimension=current_subdimension,
                        model=cells[1],
                        metric="mean_0_to_10",
                        value=value,
                        notes="v1 任务级均分；映射 v2（R1）改按指标级取分后仅作上下文保留",
                        score_role="legacy_context",
                    )


def parse_edubench_metric_scores(rows: list[dict[str, Any]]) -> None:
    """Ingest metric-level EduBench means derived by
    ``scripts/build_edubench_metric_summaries.py`` (mapping v2 / R1: one cell
    per judge metric pooled over tasks, plus two task×metric composites —
    TMG/PCC for the P18 artifact facet and QG for the P23 item_generation
    facet, split per R18)."""
    path = EVAL_DIR / "edubench" / "_metrics" / "task_metric_means.jsonl"
    if not path.exists():
        return
    composite_subdimensions = {
        "tmg_pcc_composite": (
            "TMG/PCC × clarity_concision_inspiration + scenario_element_integration (task×metric)"
        ),
        "qg_composite": (
            "QG × clarity_concision_inspiration + scenario_element_integration (task×metric)"
        ),
        # R23：出题内容正确性（裁判逐题核对学科内容对错）
        "qg_correctness_composite": (
            "QG × domain_knowledge_accuracy + basic_factual_accuracy (task×metric)"
        ),
    }
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            if row["metric"] in composite_subdimensions:
                subdimension = composite_subdimensions[row["metric"]]
            elif row["task"] == "ALL":
                subdimension = f"{row['metric']} (metric)"
            else:
                continue
            add_score(
                rows,
                source_path=path.relative_to(ROOT).as_posix(),
                benchmark_id="edubench",
                benchmark_name="EduBench",
                subdimension=subdimension,
                model=row["model"],
                metric="likert_0_to_10",
                value=float(row["mean"]),
                notes=(
                    f"题级均值 n={row['n']} sd={row['sd']}；裁判 {row.get('judge', 'deepseek-v3.2')}"
                    + ("（同事原始判分，论文口径）" if row.get("judge", "deepseek-v3.2") == "deepseek-v3.2" else "")
                ),
                judge_model=row.get("judge", "deepseek-v3.2"),
            )


def parse_sas_scores(rows: list[dict[str, Any]]) -> None:
    path = OTHER_DIR / "sas-bench-result0630.md"
    if not path.exists():
        return
    lines = path.read_text(encoding="utf-8").splitlines()
    for i, line in enumerate(lines):
        if line.strip().startswith("| 模型 | QWK"):
            for cells in parse_markdown_table(lines, i):
                if len(cells) >= 4 and cells[0] != "模型":
                    model = cells[0]
                    for subdim, metric, value_text in [
                        ("QWK holistic total score", "qwk_0_to_100", cells[1]),
                        ("CCS step scoring consistency", "score_0_to_100", cells[2]),
                        ("ECS error-cause consistency", "score_0_to_100", cells[3]),
                    ]:
                        try:
                            value = float(value_text)
                        except ValueError:
                            continue
                        add_score(
                            rows,
                            source_path=path.relative_to(ROOT).as_posix(),
                            benchmark_id="sas_bench",
                            benchmark_name="SAS-Bench",
                            subdimension=subdim,
                            model=model,
                            metric=metric,
                            value=value,
                        )
            break


def parse_rebenchmark_0701_scores(rows: list[dict[str, Any]]) -> None:
    path = OTHER_DIR / "rebenchmark-summary-0701.html"
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    card_specs = [
        # R22：0701 聚合卡退役为纯参考——同一考试同一协议的旧快照，repo 全量跑分
        # 接入 CDPK/SEND 两格后留它会同信号双算。
        ("Pedagogy Accuracy", "pedagogy_benchmark", "Pedagogy Benchmark", "CDPK/SEND aggregate from 0701 card", "accuracy_percent", "legacy_context"),
        ("ASAP 2.0 QWK", "asap_2", "ASAP 2.0", "essay holistic QWK", "qwk_0_to_100", "scoring_candidate"),
        ("EduBench Mean", "edubench", "EduBench", "overall mean aggregate from 0701 card", "mean_0_to_10", "legacy_context"),
        ("TutorBench Fair815", "tutorbench", "TutorBench", "Fair815 multimodal tutor quality", "score_0_to_100", "scoring_candidate"),
        ("EduGuard P1 Teaching Harm", "eduguard_sata", "EduGuard-Bench P1", "Teaching Harm / SATA RFS", "score_0_to_100", "legacy_context"),
    ]
    for title_marker, benchmark_id, benchmark_name, subdimension, metric, score_role in card_specs:
        title_pos = text.find(title_marker)
        if title_pos < 0:
            continue
        next_card = text.find('<div class="card"><h3>', title_pos + 1)
        block = text[title_pos: next_card if next_card > 0 else len(text)]
        for model_html, value_text in re.findall(
            r'<div class="bar-label">(.+?)</div>\s*<div class="bar-track">.*?</div>\s*<div class="bar-value">([^<]+)</div>',
            block,
            flags=re.S,
        ):
            model = strip_tags(model_html)
            try:
                value = float(value_text.strip().rstrip("%"))
            except ValueError:
                continue
            add_score(
                rows,
                source_path=path.relative_to(ROOT).as_posix(),
                benchmark_id=benchmark_id,
                benchmark_name=benchmark_name,
                subdimension=subdimension,
                model=model,
                metric=metric,
                value=value,
                notes="parsed from 0701 summary card",
                score_role=score_role,
            )
    # SAS-Bench compact QWK/CCS/ECS table in 0701; kept as legacy context
    # because `otherbenchmark/sas-bench-result0630.md` is the fuller source.
    sas_pos = text.find("SAS-Bench 三指标")
    if sas_pos >= 0:
        next_card = text.find('<div class="card"><h3>', sas_pos + 1)
        block = text[sas_pos: next_card if next_card > 0 else len(text)]
        for row in re.findall(r'<div class="metric-row">(.*?)</div>\s*</div>', block, flags=re.S):
            name_match = re.search(r'<div class="metric-name">(.+?)</div>', row, flags=re.S)
            if not name_match:
                continue
            values = re.findall(r"<b>([-0-9.]+)</b>", row)
            if len(values) < 3:
                continue
            model = strip_tags(name_match.group(1))
            for subdim, metric, value_text in [
                ("QWK holistic total score", "qwk_0_to_100", values[0]),
                ("CCS step scoring consistency", "score_0_to_100", values[1]),
                ("ECS error-cause consistency", "score_0_to_100", values[2]),
            ]:
                add_score(
                    rows,
                    source_path=path.relative_to(ROOT).as_posix(),
                    benchmark_id="sas_bench",
                    benchmark_name="SAS-Bench",
                    subdimension=subdim,
                    model=model,
                    metric=metric,
                    value=float(value_text),
                    notes="parsed from 0701 compact SAS card",
                    score_role="legacy_context",
                )
    # EduGuard P2 dual-judge compact table in 0701; kept as legacy context
    # because `eduguard_overall_report.html` is the fuller source and final
    # policy uses deepseek-v3.2 judge.
    p2_pos = text.find("EduGuard P2 Adversarial Safety")
    if p2_pos >= 0:
        next_section = text.find("</section>", p2_pos)
        block = text[p2_pos: next_section if next_section > 0 else len(text)]
        for row in re.findall(r'<div class="metric-row asr [^"]+">(.*?)</div>\s*</div>', block, flags=re.S):
            name_match = re.search(r'<div class="metric-name">(.+?)</div>', row, flags=re.S)
            values = re.findall(r"<b>([-0-9.]+)%</b>", row)
            if not name_match or len(values) < 2:
                continue
            model = strip_tags(name_match.group(1))
            for judge_note, value_text in [("MiniMax-M3 judge", values[0]), ("deepseek-v3.2 judge", values[1])]:
                add_score(
                    rows,
                    source_path=path.relative_to(ROOT).as_posix(),
                    benchmark_id="eduguard_adversarial",
                    benchmark_name="EduGuard-Bench P2",
                    subdimension="Adversarial Safety ASR",
                    model=model,
                    metric="asr_0_to_1_lower_better",
                    value=float(value_text) / 100.0,
                    notes=f"parsed from 0701 compact P2 card; {judge_note}",
                    score_role="legacy_context",
                )
    # Preserve the legacy radar numbers as context only; these are not used for
    # P-score because the current authoritative spec is P01-P22, not old P01-P20.
    for tr in re.findall(r"<tr><td>([^<]+)</td><td>([-0-9.]+)</td><td>([-0-9.]+)</td><td>([-0-9.]+)</td><td>([-0-9.]+)</td><td>([-0-9.]+)</td><td>([-0-9.]+)</td></tr>", text):
        model, srg, fdr, lad, clm, ceg, cov = tr
        for axis, value_text in [("SRG", srg), ("FDR", fdr), ("LAD", lad), ("CLM", clm), ("CEG", ceg)]:
            add_score(
                rows,
                source_path=path.relative_to(ROOT).as_posix(),
                benchmark_id="legacy_radar_0701",
                benchmark_name="Legacy 0701 Radar",
                subdimension=f"{axis} legacy radar axis",
                model=model,
                metric="legacy_axis_0_to_100",
                value=float(value_text),
                notes=f"legacy radar context only; avg_cov={cov}",
                score_role="legacy_context",
            )


def parse_eduguard_scores(rows: list[dict[str, Any]]) -> None:
    path = OTHER_DIR / "eduguard_overall_report.html"
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    # P1 RFS table.
    start = text.find("3.1 本轮模型")
    end = text.find("3.2 原论文模型", start)
    block = text[start:end if end > 0 else len(text)]
    for tr in re.findall(r"<tr>(.*?)</tr>", block, flags=re.S):
        cells = [strip_tags(c) for c in re.findall(r"<td[^>]*>(.*?)</td>", tr, flags=re.S)]
        if len(cells) >= 3 and cells[0].isdigit():
            try:
                value = float(cells[2])
            except ValueError:
                continue
            add_score(
                rows,
                source_path=path.relative_to(ROOT).as_posix(),
                benchmark_id="eduguard_sata",
                benchmark_name="EduGuard-Bench P1",
                subdimension="Teaching Harm / SATA RFS",
                model=cells[1],
                metric="rfs_0_to_1",
                value=value,
            )
    # P2 total-ASR table in section 4.6. This is the only place that has the
    # intended side-by-side MiniMax-M3 vs deepseek-v3.2 overall ASR rows.
    start = text.find("M3 判 ASR")
    if start >= 0:
        end = text.find("</table>", start)
        block = text[start: end if end > 0 else len(text)]
        for tr in re.findall(r"<tr>(.*?)</tr>", block, flags=re.S):
            cells = [strip_tags(c) for c in re.findall(r"<td[^>]*>(.*?)</td>", tr, flags=re.S)]
            if len(cells) >= 4 and cells[0].isdigit():
                model = cells[1]
                for note, value_text in [
                    ("MiniMax-M3 judge", cells[2]),
                    ("deepseek-v3.2 judge", cells[3]),
                ]:
                    try:
                        value = float(value_text.rstrip("%")) / 100.0
                    except ValueError:
                        continue
                    add_score(
                        rows,
                        source_path=path.relative_to(ROOT).as_posix(),
                        benchmark_id="eduguard_adversarial",
                        benchmark_name="EduGuard-Bench P2",
                        subdimension="Adversarial Safety ASR",
                        model=model,
                        metric="asr_0_to_1_lower_better",
                        value=value,
                        notes=note,
                        score_role="scoring_candidate" if note == EDUGUARD_P2_PRIMARY_JUDGE else "legacy_context",
                    )


def inventory_otherbenchmark_scores() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    parse_edubench_scores(rows)
    parse_edubench_metric_scores(rows)
    parse_sas_scores(rows)
    parse_rebenchmark_0701_scores(rows)
    parse_eduguard_scores(rows)
    rows.sort(key=lambda r: (r["benchmark_id"], r["subdimension"], r["model"], r["notes"]))
    return rows


def canonical_model(model: str) -> str:
    key = model.strip().lower()
    key = key.replace("claude sonnet", "claude-sonnet")
    key = key.replace(" ", "-").replace("_", "-").replace(".", "-")
    key = re.sub(r"[^a-z0-9+-]+", "-", key)
    key = re.sub(r"-+", "-", key).strip("-")
    aliases = {
        "gpt-5-4": "gpt-5.4",
        "gpt-5-5": "gpt-5.5",
        "claude-sonnet-4-6": "claude-sonnet-4.6",
        "qwen3-7-max": "qwen3.7-max",
        "glm-5-1": "glm-5.1",
        "glm-5-2": "glm-5.2",
        "minimax-m2-7": "minimax-m2.7",
        "minimax-m3": "minimax-m3",
        # 带日期后缀的快照版本归一到面板键（R23：doubao 的 pedagogy 跑分目录
        # 是 doubao-seed-2-0-pro-260215，不归一会让面板键拿替代值、真分挂幽灵键）
        "doubao-seed-2-0-pro-260215": "doubao-seed-2-0-pro",
    }
    return aliases.get(key, key)


def normalize_score(metric: str, value: float) -> float | None:
    if value != value:  # NaN guard: min/max clamping would silently turn NaN into 10.0
        return None
    if metric in {"accuracy", "pass_rate", "rfs_0_to_1", "accuracy_or_f1", "win_rate_or_accuracy", "share_0_to_1"}:
        return value * 10.0
    if metric == "asr_0_to_1_lower_better":
        return (1.0 - value) * 10.0
    if metric in {"accuracy_percent", "score_0_to_100", "qwk_0_to_100", "legacy_axis_0_to_100"}:
        return value / 10.0
    if metric in {"mean_0_to_10", "likert_0_to_10"}:
        return value
    if metric == "likert_0_to_5":
        return value * 2.0
    if metric == "likert_1_to_5":
        return (value - 1.0) / 4.0 * 10.0
    if metric == "score_0_to_6":
        return value / 6.0 * 10.0
    if metric == "composite_0_to_10":
        return value
    if metric == "bleu_0_to_1":
        return value * 10.0
    return None


def mapping_by_benchmark() -> dict[str, dict[str, Any]]:
    return {row["benchmark_id"]: row for row in MAPPINGS}


def find_mapping(benchmark_id: str, subdimension: str | None = None, metric: str | None = None) -> dict[str, Any] | None:
    candidates = [row for row in MAPPINGS if row["benchmark_id"] == benchmark_id]
    if subdimension is not None:
        for row in candidates:
            if row["subdimension"] == subdimension:
                return row
        # A benchmark with several mapped subdimensions must match exactly:
        # falling back to an arbitrary row would silently mis-assign scores
        # (e.g. legacy edubench task-level rows onto v2 metric-level cells).
        if len(candidates) > 1:
            return None
    if metric is not None:
        for row in candidates:
            if row["metric_family"] == metric:
                return row
        if metric == "accuracy" and candidates:
            for row in candidates:
                if row["metric_family"] in {"accuracy", "accuracy_or_f1", "win_rate_or_accuracy"}:
                    return row
    return candidates[0] if len(candidates) == 1 else None


def extract_primary_metric(summary: dict[str, Any]) -> tuple[str, float | None]:
    extra = summary.get("extra_metrics") or {}
    overall = extra.get("overall") or {}
    if "asr" in overall:
        return "asr", overall.get("asr")
    if "rfs" in overall:
        return "rfs", overall.get("rfs")
    if "pass_rate" in extra:
        return "pass_rate", extra.get("pass_rate")
    if "overall_mean_all_items" in summary:
        # 渲染/执行失败的题按 0 分计入分母（用户裁决 2026-08-17，见 eduillustrate 分支）。
        return "overall_mean_all_items", summary.get("overall_mean_all_items")
    if "overall_mean_judged_only" in summary:
        return "overall_mean_judged_only", summary.get("overall_mean_judged_only")
    if "accuracy" in summary:
        return "accuracy", summary.get("accuracy")
    return "unknown", None


def inventory_eval_runs() -> list[dict[str, Any]]:
    rows = []
    for path in sorted(EVAL_DIR.glob("**/summary.json")):
        rel = path.relative_to(ROOT).as_posix()
        parts = path.parts
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue

        benchmark = data.get("benchmark") or path.relative_to(EVAL_DIR).parts[0]
        model = data.get("model") or ""
        scored = data.get("scored") or data.get("judged") or 0
        total = data.get("total_items") or 0
        if benchmark == "eduillustrate":
            # 2026-08-17 用户裁决：渲染失败不是「没测到」，是这道题拿 0 分——模型
            # 写不出跑得通的 Manim 代码本身就是被测能力的一部分。所以样本量按
            # total_items（230）算，不按 judged 算，否则渲染失败越多反而越容易被
            # 「样本不足 100」挡掉，失败率高的模型直接从 P04 消失。
            # Qwen3.5-4B 就是这么丢的：230 题里 138 题渲染失败，judged 只剩 92。
            scored = total or scored
        primary_metric, primary_value = extract_primary_metric(data)

        include = True
        reasons = []
        if "_judge_rubric" in parts or "_judge_jury" in parts:
            include = False
            reasons.append("rubric_or_jury_meta_experiment")
        if "_baseline" in parts:
            # reports/eval/_baseline/ 装的是地板与人类锚（run_reference_baseline.py）：
            # refusal/echo/generic/random 是退化回复，expert/novice/gpt4/sonnet/
            # llama31405b 是数据集自带的人类或外部模型回复。它们都不是被测模型，
            # 归宿是 doc/benchmark_baselines_*.md 和 doc/benchmark_human_baselines_*.md。
            # 之前只是靠「题量不足 100」把退化基线挡在外面，expert 那几个满量的
            # 已经漏进面板当模型行了——按目录显式排除。
            include = False
            reasons.append("reference_baseline_not_a_model")
        if "selfjudge_backup_20260616_100151" in parts:
            include = False
            reasons.append("backup_duplicate")
        if "judge_calibration" in benchmark:
            include = False
            reasons.append("judge_calibration_excluded")
        if benchmark in EXCLUDED_SCORING_BENCHMARKS:
            include = False
            reasons.append("user_excluded_judge_task")
        if benchmark == "eduguard_adversarial" and "_judge-deepseek-v3.2" not in rel:
            include = False
            reasons.append("eduguard_p2_non_primary_judge")
        observed_items = scored or total
        if observed_items and observed_items < 100:
            include = False
            reasons.append("small_scored_sample_under_100")
        if total and total < 100:
            include = False
            reasons.append("small_total_under_100")
        if not total:
            include = False
            reasons.append("missing_or_zero_total")
        if not observed_items:
            include = False
            reasons.append("missing_or_zero_scored")
        if not model:
            include = False
            reasons.append("missing_model")

        rows.append(
            {
                "path": rel,
                "benchmark": benchmark,
                "model": model,
                "scored": scored,
                "total_items": total,
                "primary_metric": primary_metric,
                "primary_value": primary_value,
                "main_inclusion": "include_candidate" if include else "exclude_from_main",
                "reasons": reasons,
            }
        )
    return rows


def repo_metric_rows(benchmark: str, data: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract score rows from one summary.json.

    Returns a list of ``{"subdimension", "metric", "value", "note"}`` rows so a
    single summary can feed several mapped subdimensions (mapping v2: bea/mrbench
    per-dimension scores, eduguard ASR + refusal quality, ...).  ``subdimension``
    is None for single-subdimension benchmarks (resolved via metric family)."""
    extra = data.get("extra_metrics") or {}
    overall = extra.get("overall") or {}
    rows: list[dict[str, Any]] = []

    def add(subdimension: str | None, metric: str, value: Any, note: str) -> None:
        if value is None:
            return
        rows.append({"subdimension": subdimension, "metric": metric, "value": float(value), "note": note})

    if benchmark == "eduguard_sata":
        add(None, "rfs_0_to_1", overall.get("rfs"), "extra_metrics.overall.rfs")
        return rows
    if benchmark == "eduguard_adversarial":
        add(
            "Adversarial Safety ASR",
            "asr_0_to_1_lower_better",
            overall.get("asr"),
            "extra_metrics.overall.asr; primary judge deepseek-v3.2",
        )
        refusal = (overall.get("refusal_quality_distribution") or {}).get("educational_refusal") or {}
        add(
            "Refusal quality distribution",
            "share_0_to_1",
            refusal.get("share_of_refusals"),
            "extra_metrics.overall.refusal_quality_distribution.educational_refusal.share_of_refusals",
        )
        return rows
    if benchmark in {"bea2025_tutor", "mrbench_tutor"}:
        dist = extra.get("per_dimension_distribution") or {}
        for dim in ("Mistake_Identification", "Providing_Guidance", "Actionability"):
            share = ((dist.get(dim) or {}).get("Yes") or {}).get("share")
            add(
                f"dimension: {dim}",
                "share_0_to_1",
                share,
                f"extra_metrics.per_dimension_distribution.{dim}.Yes.share（R2 单维度分）",
            )
        if benchmark == "mrbench_tutor":
            tone = dist.get("Tutor_Tone") or {}
            encouraging = ((tone.get("Encouraging") or {}).get("share"))
            neutral = ((tone.get("Neutral") or {}).get("share"))
            offensive = ((tone.get("Offensive") or {}).get("share"))
            if encouraging is not None or neutral is not None or offensive is not None:
                # R19: one annotation, two statistics — P20 boundary facet takes
                # non-offensive share, P18 tone_support facet takes encouraging
                # share (dedup vs the old Encouraging+0.5×Neutral single cell).
                add(
                    "dimension: Tutor_Tone (non-offensive)",
                    "share_0_to_1",
                    1.0 - (offensive or 0.0),
                    "1 − Offensive share（R19：P20 边界构念只取越界信号）",
                )
                add(
                    "dimension: Tutor_Tone (encouraging share)",
                    "share_0_to_1",
                    encouraging or 0.0,
                    "Encouraging share（R19：P18 语气支持 facet 副挂）",
                )
        return rows
    if benchmark == "olympiadbench":
        # R22：P03 改取多模态子集，P04/P05 仍取全量。看不见图的模型在 MM 子集上的
        # 分数是盲答废分，跳过——R26 起判据统一到 MODEL_CAPABILITIES 的 vision 一列，
        # 并补上 --no-images 文本降级 run（summary.input_variant == "no_images"）：
        # 那份分数按 harness 自己的声明就是降级代理值，不是多模态能力的测量。
        add(
            "overall/subject/language/modality accuracy",
            "accuracy",
            data.get("accuracy"),
            "summary.accuracy（全量，P04/P05 用）",
        )
        model_key = canonical_model(data.get("model") or "")
        blind = (
            model_key in BLIND_VISION_MODELS
            or MODEL_CAPABILITIES.get(model_key, {}).get("vision") is False
            or data.get("input_variant") == "no_images"
        )
        mm = ((data.get("by_bucket") or {}).get("modality") or {}).get("MM") or {}
        if not blind and mm.get("accuracy") is not None:
            add(
                "multimodal-subset accuracy",
                "accuracy",
                mm.get("accuracy"),
                "by_bucket.modality.MM.accuracy（仅带图题，P03 用）",
            )
        return rows
    if benchmark == "k12vista":
        # R22：P03 按学科拆两格（math=解题图像 / 理化生地=学科图表），
        # P04/P05 仍取整体 score_10。分桶分数在 extra_metrics.by_subject（0–1）。
        add(
            "official partial-credit score (per-blank 0/1 mean)",
            "composite_0_to_10",
            extra.get("score_10"),
            "extra_metrics.score_10（整体，P04/P05 用）",
        )
        by_subject = extra.get("by_subject") or {}
        groups = {
            "math problem-figure subset score": lambda s: s.startswith("math"),
            "science/geo subject-chart subset score": lambda s: not s.startswith("math"),
        }
        for subdimension, pred in groups.items():
            total_n = 0
            total_score = 0.0
            for subject, stats in by_subject.items():
                if not pred(subject):
                    continue
                n = stats.get("n") or 0
                score = stats.get("score")
                if score is None or not n:
                    continue
                total_n += n
                total_score += float(score) * n
            if total_n:
                add(
                    subdimension,
                    "composite_0_to_10",
                    10.0 * total_score / total_n,
                    f"extra_metrics.by_subject 按 n 加权（{total_n} 题，P03 用）",
                )
        return rows
    if benchmark == "pedagogy_benchmark":
        # R22：修复取数缺口——此前无本分支，1,119 题完整跑分被静默丢弃，
        # CDPK/SEND 两格长期零证据。SEND=CDPK_send 类，CDPK=其余 7 类合并。
        # 冒烟跑（如 glm-5.2 的 20 题）不足以代表 8 类，跳过。
        categories = (data.get("by_bucket") or {}).get("category") or {}
        if (data.get("scored") or 0) < 600 or len(categories) < 8:
            return rows
        # 优先走 by_bucket.task 的 cdpk/send 两桶：导入版和 harness 自跑版都有它，
        # 且切分口径完全一致（899/220）。category 桶两边命名不同——同事导入版是
        # CDPK_send/CDPK_maths…，harness 适配器发的是 HF 原始类名 SEND/Maths…
        # （COLLEAGUE_CATEGORY_KEYS 只用在 item_id 上，没落到 bucket）。原来只认
        # CDPK_send，harness 跑出来的模型会静默丢掉 SEND 格，而且 SEND 的题会被
        # 算进 CDPK 格里污染分母。
        tasks = (data.get("by_bucket") or {}).get("task") or {}
        cdpk = tasks.get("cdpk") or {}
        send = tasks.get("send") or {}
        source_note = "by_bucket.task"
        if not (cdpk.get("total") and send.get("total")):
            send = categories.get("CDPK_send") or categories.get("SEND") or {}
            send_keys = {"CDPK_send", "SEND"}
            cdpk = {
                "total": sum(v.get("total", 0) for k, v in categories.items() if k not in send_keys),
                "correct": sum(v.get("correct", 0) for k, v in categories.items() if k not in send_keys),
            }
            source_note = "by_bucket.category 除 SEND 外 7 类合并"
        if cdpk.get("total"):
            add(
                "CDPK teaching knowledge selection",
                "accuracy",
                (cdpk.get("correct") or 0) / cdpk["total"],
                f"{source_note}（{cdpk['total']} 题）",
            )
        if send.get("total"):
            add(
                "SEND special education needs selection",
                "accuracy",
                (send.get("correct") or 0) / send["total"],
                f"{source_note} SEND（{send['total']} 题）",
            )
        return rows
    if benchmark == "sas_bench":
        # 三个指标同出一份 summary：QWK 判总分、CCS 判分步、ECS 判错因。
        # metric 名必须与 parse_sas_scores 的 md 行一致，否则 dedupe 认不出是同一格，
        # 两份来源会各留一行变成重复计数。
        for subdimension, metric, key, note in (
            ("QWK holistic total score", "qwk_0_to_100", "qwk", "extra_metrics.overall.qwk（12 子任务等权均值）"),
            ("CCS step scoring consistency", "score_0_to_100", "ccs", "extra_metrics.overall.ccs（12 子任务等权均值）"),
            ("ECS error-cause consistency", "score_0_to_100", "ecs", "extra_metrics.overall.ecs（12 子任务等权均值）"),
        ):
            add(subdimension, metric, overall.get(key), note)
        return rows
    if benchmark == "longtutor_evidence":
        # R21：按 memory_type 拆三格（各 1,001 题）。子维度名必须与映射格
        # subdimension 完全一致，聚合按精确字符串匹配。
        memory_buckets = ((data.get("by_bucket") or {}).get("memory_type")) or {}
        for bucket, subdimension in (
            ("Information Extraction", "Information Extraction accuracy"),
            ("Multi-session Reasoning", "Multi-session Reasoning accuracy"),
            ("Hallucination Check", "Hallucination Check accuracy"),
        ):
            add(
                subdimension,
                "accuracy",
                (memory_buckets.get(bucket) or {}).get("accuracy"),
                f"by_bucket.memory_type['{bucket}'].accuracy（精确匹配+语义等价裁判）",
            )
        return rows
    if benchmark == "longtutor_diagnosis":
        add(None, "accuracy_or_f1", extra.get("f1_macro"), "extra_metrics.f1_macro（headline，类别不平衡故不用 accuracy）")
        return rows
    if benchmark == "longtutor_teaching":
        judge_scores = extra.get("judge_scores") or {}
        strategy = judge_scores.get("strategy_alignment")
        history = judge_scores.get("history_utilization")
        if strategy and history:
            add(
                None,
                "likert_1_to_5",
                (float(strategy) + float(history)) / 2.0,
                "mean(judge_scores.strategy_alignment, history_utilization)；coherence/appropriateness 不入分",
            )
        return rows

    def single(metric: str, value: Any, note: str) -> list[dict[str, Any]]:
        add(None, metric, value, note)
        return rows

    return _repo_single_metric(benchmark, data, extra, single)


def _repo_single_metric(benchmark, data, extra, single):
    # R23：judge 类不再全局排除——「主观题评价能力」P 的被测构念就是判卷能力。
    # 取分一律用抗类别不平衡的 macro-F1 口径，而非裸 accuracy（多数类占比高会虚高）。
    if benchmark == "bea2025_judge":
        return single(
            "accuracy",
            extra.get("recommended_judge_score"),
            "extra_metrics.recommended_judge_score（官方口径：四维 exact macro-F1 均值）",
        )
    if benchmark == "mrbench_judge":
        macro = extra.get("macro_over_dimensions") or {}
        return single(
            "accuracy",
            macro.get("f1_macro"),
            "extra_metrics.macro_over_dimensions.f1_macro（8 维 macro-F1 的跨维均值）",
        )
    if benchmark == "eduillustrate":
        # 取 all_items 而不是 judged_only（用户裁决 2026-08-17）：渲染失败计 0 分入分母。
        # judged_only 会把「代码跑不通」洗成缺测，等于奖励生成不出可执行产物的模型。
        value = data.get("overall_mean_all_items")
        if value is None:
            value = data.get("overall_mean_judged_only")
        return single("likert_0_to_5", value, "overall_mean_all_items（渲染失败按 0 分计入 230 题分母）")
    if benchmark == "mmtutorbench":
        return single("score_0_to_6", extra.get("paper_weighted_score_0_to_6"), "extra_metrics.paper_weighted_score_0_to_6")
    if benchmark == "mathtutorbench_solution_correctness":
        return single("accuracy_or_f1", extra.get("f1", data.get("accuracy")), "extra_metrics.f1")
    if benchmark == "mathtutorbench_mistake_location":
        return single("accuracy_or_f1", extra.get("f1_micro", data.get("accuracy")), "extra_metrics.f1_micro")
    if benchmark in {
        "mathtutorbench_pedagogy",
        "mathtutorbench_pedagogy_hard",
        "mathtutorbench_scaffolding",
        "mathtutorbench_scaffolding_hard",
    }:
        return single("win_rate_or_accuracy", extra.get("win_rate", data.get("accuracy")), "extra_metrics.win_rate")
    if benchmark == "mathtutorbench_socratic":
        return single("bleu_0_to_1", extra.get("avg_bleu"), "extra_metrics.avg_bleu (official headline; summary.accuracy is a coarse BLEU>=0.5 proxy)")
    if benchmark.startswith("mathtutorbench_"):
        return single("accuracy", data.get("accuracy"), "summary.accuracy")
    if benchmark in {"agieval", "ceval", "mmlu_pro", "mathvista", "ifeval"}:
        return single("accuracy", data.get("accuracy"), "summary.accuracy")
    if benchmark in {
        "p07_selfcheck",
        "p08_calibration",
        "p08_abstention",
        "mooccube_prereq",
    }:
        return single("composite_0_to_10", extra.get("score_10"), "extra_metrics.score_10")
    return []


_JUDGE_CACHE: dict[str, str] = {}


def resolve_judge_model(run_dir: Path, data: dict[str, Any]) -> str:
    """Who judged this run.

    `summary.json` 的顶层 `judge_model` 是后加的字段，早期跑分没有它——但逐题
    `extractions.jsonl` 里一直写着 `judge_model`，那才是权威来源。别看目录名猜：
    `mrbench_tutor/minimax3/` 是「被测模型叫 minimax3」，跟裁判是谁无关。

    返回 `"rule"` 表示这个 benchmark 不用裁判（规则判分），`"unknown"` 表示查不到。
    """
    key = run_dir.as_posix()
    if key in _JUDGE_CACHE:
        return _JUDGE_CACHE[key]
    judge = data.get("judge_model")
    if not judge:
        extractions = run_dir / "extractions.jsonl"
        if extractions.exists():
            with extractions.open(encoding="utf-8") as fh:
                for index, line in enumerate(fh):
                    if index > 50:
                        break
                    try:
                        extracted = json.loads(json.loads(line).get("extracted") or "{}")
                    except (json.JSONDecodeError, TypeError):
                        continue
                    if isinstance(extracted, dict) and extracted.get("judge_model"):
                        judge = extracted["judge_model"]
                        break
    if not judge and "_judge-deepseek-v3.2" in key:
        judge = "deepseek-v3.2"
    judge = str(judge).split(" ")[0] if judge else "rule_or_unknown"
    _JUDGE_CACHE[key] = judge
    return judge


def build_repo_score_candidates(eval_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    mapped_benchmarks = {row["benchmark_id"] for row in MAPPINGS}
    rows: list[dict[str, Any]] = []
    for inv in eval_rows:
        benchmark = inv["benchmark"]
        if benchmark not in mapped_benchmarks:
            continue
        if inv["main_inclusion"] != "include_candidate":
            continue
        path = ROOT / inv["path"]
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        for metric_row in repo_metric_rows(benchmark, data):
            metric = metric_row["metric"]
            raw_value = metric_row["value"]
            mapping = find_mapping(benchmark, subdimension=metric_row["subdimension"], metric=metric)
            if mapping is None:
                continue
            score_10 = normalize_score(metric, float(raw_value))
            if score_10 is None:
                continue
            model = data.get("model") or inv["model"]
            rows.append(
                {
                    "source_type": "repo_eval",
                    "source_path": inv["path"],
                    "benchmark_id": benchmark,
                    "benchmark_name": mapping["benchmark_name"],
                    "subdimension": mapping["subdimension"],
                    "model": model,
                    "model_key": canonical_model(model),
                    "metric": metric,
                    "raw_value": float(raw_value),
                    "score_10": max(0.0, min(10.0, score_10)),
                    "score_role": "scoring_candidate",
                    "notes": metric_row["note"],
                    "judge_model": resolve_judge_model(path.parent, data),
                    "total_items": inv["total_items"],
                    "scored": inv["scored"],
                }
            )
    return rows


def build_other_score_candidates(other_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in other_rows:
        if row.get("score_role") != "scoring_candidate":
            continue
        benchmark = row["benchmark_id"]
        mapping = find_mapping(benchmark, subdimension=row["subdimension"], metric=row["metric"])
        if mapping is None:
            continue
        score_10 = normalize_score(row["metric"], float(row["raw_value"]))
        if score_10 is None:
            continue
        rows.append(
            {
                "source_type": "otherbenchmark",
                "source_path": row["source_path"],
                "benchmark_id": benchmark,
                "benchmark_name": row["benchmark_name"],
                "subdimension": row["subdimension"],
                "model": row["model"],
                "model_key": canonical_model(row["model"]),
                "metric": row["metric"],
                "raw_value": float(row["raw_value"]),
                "score_10": max(0.0, min(10.0, score_10)),
                "score_role": row["score_role"],
                "notes": row.get("notes", ""),
                "judge_model": row.get("judge_model", "rule_or_unknown"),
                "total_items": None,
                "scored": None,
            }
        )
    return rows


def candidate_rank(row: dict[str, Any]) -> tuple[int, int, int, int, str]:
    path = row["source_path"]
    source_rank = 2 if row["source_type"] == "repo_eval" else 1
    minimax_rank = 1 if "/minimax3/" in path or path.endswith("/minimax3/summary.json") else 0
    scored = int(row.get("scored") or 0)
    total = int(row.get("total_items") or 0)
    return (source_rank, minimax_rank, scored, total, path)


def dedupe_score_candidates(candidates: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    grouped: dict[tuple[str, str, str, str], list[dict[str, Any]]] = {}
    for row in candidates:
        key = (row["benchmark_id"], row["subdimension"], row["model_key"], row["metric"])
        grouped.setdefault(key, []).append(row)

    selected: list[dict[str, Any]] = []
    report: list[dict[str, Any]] = []
    for key, group in sorted(grouped.items()):
        ranked = sorted(group, key=candidate_rank, reverse=True)
        chosen_row = ranked[0]
        chosen = dict(chosen_row)
        chosen["dedupe_status"] = "selected"
        selected.append(chosen)
        if len(group) > 1:
            for row in ranked:
                report.append(
                    {
                        "benchmark_id": key[0],
                        "subdimension": key[1],
                        "model_key": key[2],
                        "metric": key[3],
                        "status": "selected" if row is chosen_row else "rejected",
                        "source_type": row["source_type"],
                        "source_path": row["source_path"],
                        "model": row["model"],
                        "raw_value": row["raw_value"],
                        "score_10": row["score_10"],
                        "notes": row.get("notes", ""),
                    }
                )
    selected.sort(key=lambda r: (r["model_key"], r["benchmark_id"], r["subdimension"], r["source_path"]))
    return selected, report


def minimax_conflict_report(eval_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    by_bench: dict[str, list[dict[str, Any]]] = {}
    for row in eval_rows:
        if canonical_model(row["model"]) == "minimax-m3":
            by_bench.setdefault(row["benchmark"], []).append(row)
    for benchmark, group in sorted(by_bench.items()):
        if len(group) < 2:
            continue
        chosen = sorted(
            [r for r in group if r["main_inclusion"] == "include_candidate"] or group,
            key=lambda r: (
                1 if "/minimax3/" in r["path"] or r["path"].endswith("/minimax3/summary.json") else 0,
                int(r.get("scored") or 0),
                int(r.get("total_items") or 0),
                r["path"],
            ),
            reverse=True,
        )[0]
        for row in sorted(group, key=lambda r: r["path"]):
            rows.append(
                {
                    "benchmark": benchmark,
                    "path": row["path"],
                    "model": row["model"],
                    "primary_metric": row["primary_metric"],
                    "primary_value": row["primary_value"],
                    "scored": row["scored"],
                    "total_items": row["total_items"],
                    "main_inclusion": row["main_inclusion"],
                    "reasons": row["reasons"],
                    "canonical_status": "selected" if row["path"] == chosen["path"] else "not_selected",
                    "canonical_reason": "prefer included minimax3/full-scored run when present",
                }
            )
    return rows


def score_atomic_p(
    selected_rows: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    evidence_rows: list[dict[str, Any]] = []
    accum: dict[tuple[str, str], dict[str, Any]] = {}
    for row in selected_rows:
        if row["benchmark_id"] in EXCLUDED_SCORING_BENCHMARKS:
            continue
        mapping = find_mapping(row["benchmark_id"], subdimension=row["subdimension"], metric=row["metric"])
        if mapping is None:
            continue
        for ability in mapping["abilities"]:
            if ability.get("excluded"):
                continue
            raw_weight = mapping["default_benchmark_weight"] * ability["weight"]
            evidence = {
                "model_key": row["model_key"],
                "model": row["model"],
                "p_code": ability["p_code"],
                "p_name": ability["p_name"],
                "group": ability["group"],
                "facet_id": ability["facet_id"],
                "facet_name": ability["facet_name"],
                "benchmark_id": row["benchmark_id"],
                "subdimension": row["subdimension"],
                "source_type": row["source_type"],
                "source_path": row["source_path"],
                "metric": row["metric"],
                "raw_value": row["raw_value"],
                "score_10": row["score_10"],
                "judge_model": row.get("judge_model", "rule_or_unknown"),
                "row_weight": mapping["default_benchmark_weight"],
                "ability_weight": ability["weight"],
                "effective_weight": raw_weight,
            }
            evidence_rows.append(evidence)
            slot = accum.setdefault(
                (row["model_key"], ability["p_code"]),
                {
                    "model_key": row["model_key"],
                    "display_model": row["model"],
                    "p_code": ability["p_code"],
                    "p_name": ability["p_name"],
                    "group": ability["group"],
                    "facets": {},
                    "evidence_count": 0,
                    "benchmarks": set(),
                    "judges": set(),
                },
            )
            facet_slot = slot["facets"].setdefault(
                ability["facet_id"],
                {"weighted_sum": 0.0, "weight_sum": 0.0},
            )
            facet_slot["weighted_sum"] += row["score_10"] * raw_weight
            facet_slot["weight_sum"] += raw_weight
            slot["evidence_count"] += 1
            slot["benchmarks"].add(row["benchmark_id"])
            judge = row.get("judge_model") or ""
            if judge and judge != "rule_or_unknown":
                slot["judges"].add(judge)

    # R26 缺测处理（用户裁决 2026-08-04，取代 R22 的最低分顶替）：发布面板模型
    # 缺某格时不再借别人的分数，改为按 missing_cell_verdict() 分成两类——
    # 能力不具备记 0 分进聚合，其余记「未测过」不进分母。详见文件顶部的口径说明。
    cell_faces: dict[tuple[str, str, str, str], dict[str, dict[str, Any]]] = {}
    for ev in evidence_rows:
        key = (ev["p_code"], ev["facet_id"], ev["benchmark_id"], ev["subdimension"])
        cell_faces.setdefault(key, {})[ev["model_key"]] = ev
    zero_rows: list[dict[str, Any]] = []
    untested_rows: list[dict[str, Any]] = []
    for faces in cell_faces.values():
        template = next(iter(faces.values()))
        for model_key in PANEL_MODEL_KEYS:
            if model_key in faces:
                continue
            status, capability, reason = missing_cell_verdict(
                model_key, template["benchmark_id"], template["subdimension"]
            )
            row = dict(template)
            row.update(
                {
                    "model_key": model_key,
                    "model": model_key,
                    "raw_value": None,
                    # 这一行不是任何一次 run 的产物，别留别人的 summary 路径冒充出处，
                    # 裁判同理——模板行的 judge_model 是别的模型那次跑分的裁判。
                    "source_path": "",
                    "judge_model": "",
                    "coverage_status": status,
                    "missing_capability": capability,
                    "coverage_reason": reason,
                    "tested_faces": len(faces),
                }
            )
            if status == "capability_gap":
                row.update({"source_type": "capability_gap_zero", "score_10": 0.0})
                zero_rows.append(row)
            else:
                row.update({"source_type": "untested", "score_10": None})
                untested_rows.append(row)
    for ev in zero_rows:
        evidence_rows.append(ev)
        slot = accum.setdefault(
            (ev["model_key"], ev["p_code"]),
            {
                "model_key": ev["model_key"],
                "display_model": ev["model"],
                "p_code": ev["p_code"],
                "p_name": ev["p_name"],
                "group": ev["group"],
                "facets": {},
                "evidence_count": 0,
                "benchmarks": set(),
                "judges": set(),
            },
        )
        facet_slot = slot["facets"].setdefault(
            ev["facet_id"],
            {"weighted_sum": 0.0, "weight_sum": 0.0},
        )
        facet_slot["weight_sum"] += ev["effective_weight"]  # score 为 0，weighted_sum 不变
        facet_slot["zero_weight_sum"] = facet_slot.get("zero_weight_sum", 0.0) + ev["effective_weight"]
        slot["evidence_count"] += 1
        slot["benchmarks"].add(ev["benchmark_id"])
        slot["capability_zero_count"] = slot.get("capability_zero_count", 0) + 1
    # 未测过的格子只登记，不进任何分母；单独出一份清单供报告直接引用。
    untested_by_slot: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for ev in untested_rows:
        untested_by_slot.setdefault((ev["model_key"], ev["p_code"]), []).append(ev)
    untested_rows.sort(key=lambda r: (r["model_key"], r["p_code"], r["benchmark_id"], r["subdimension"]))

    # 聚合方向（R20 后单一口径）：facet 内按 相关度×置信 有效权重加权平均，
    # P 分数 = 有证据 facet 的等权平均（formative 声明；reflective P 只有一个
    # core facet，退化为整体加权平均）。
    p_rows: list[dict[str, Any]] = []
    for slot in accum.values():
        facet_means = [f["weighted_sum"] / f["weight_sum"] for f in slot["facets"].values() if f["weight_sum"]]
        score = sum(facet_means) / len(facet_means) if facet_means else None
        weight_sum = sum(f["weight_sum"] for f in slot["facets"].values())
        zero_weight = sum(f.get("zero_weight_sum", 0.0) for f in slot["facets"].values())
        untested = untested_by_slot.pop((slot["model_key"], slot["p_code"]), [])
        p_rows.append(
            {
                "model_key": slot["model_key"],
                "display_model": slot["display_model"],
                "p_code": slot["p_code"],
                "p_name": slot["p_name"],
                "group": slot["group"],
                "score_10": round(score, 4) if score is not None else None,
                "coverage_status": "scored" if score is not None else "untested",
                "weight_sum": round(weight_sum, 4),
                "facet_count_with_evidence": len(facet_means),
                "facet_scores": {
                    facet_id: round(f["weighted_sum"] / f["weight_sum"], 4)
                    for facet_id, f in sorted(slot["facets"].items())
                    if f["weight_sum"]
                },
                "evidence_count": slot["evidence_count"],
                "benchmark_count": len(slot["benchmarks"]),
                "benchmarks": sorted(slot["benchmarks"]),
                # 判分模型清单（用户裁决 2026-08-17：裁判现阶段混用，但必须标注）。
                # 空 = 这个 P 的取分格全是规则判分，不经裁判。
                "judge_models": sorted(slot.get("judges") or ()),
                "capability_zero_count": slot.get("capability_zero_count", 0),
                "capability_zero_weight_share": round(zero_weight / weight_sum, 4) if weight_sum else 0.0,
                "untested_cell_count": len(untested),
                "untested_cells": sorted({f'{r["benchmark_id"]} · {r["subdimension"]}' for r in untested}),
            }
        )
    # 一条实测证据都没有、只剩未测格的 (模型, P)：仍然出行，score_10=None，
    # 这样报告读到的是「未测过」而不是这个模型面根本不存在。
    for (model_key, p_code), rows in untested_by_slot.items():
        template = rows[0]
        p_rows.append(
            {
                "model_key": model_key,
                "display_model": model_key,
                "p_code": p_code,
                "p_name": template["p_name"],
                "group": template["group"],
                "score_10": None,
                "coverage_status": "untested",
                "weight_sum": 0.0,
                "facet_count_with_evidence": 0,
                "facet_scores": {},
                "evidence_count": 0,
                "benchmark_count": 0,
                "benchmarks": [],
                "capability_zero_count": 0,
                "capability_zero_weight_share": 0.0,
                "untested_cell_count": len(rows),
                "untested_cells": sorted({f'{r["benchmark_id"]} · {r["subdimension"]}' for r in rows}),
            }
        )
    p_rows.sort(key=lambda r: (r["model_key"], r["p_code"]))

    group_accum: dict[tuple[str, str], dict[str, Any]] = {}
    for row in p_rows:
        if row["score_10"] is None:
            continue
        slot = group_accum.setdefault(
            (row["model_key"], row["group"]),
            {
                "model_key": row["model_key"],
                "display_model": row["display_model"],
                "group": row["group"],
                "score_sum": 0.0,
                "p_count": 0,
                "p_codes": [],
            },
        )
        slot["score_sum"] += row["score_10"]
        slot["p_count"] += 1
        slot["p_codes"].append(row["p_code"])
    group_rows: list[dict[str, Any]] = []
    for slot in group_accum.values():
        group_rows.append(
            {
                "model_key": slot["model_key"],
                "display_model": slot["display_model"],
                "group": slot["group"],
                "score_10": round(slot["score_sum"] / slot["p_count"], 4),
                "p_count_with_evidence": slot["p_count"],
                "p_codes": sorted(slot["p_codes"]),
            }
        )
    group_rows.sort(key=lambda r: (r["model_key"], r["group"]))
    evidence_rows.sort(key=lambda r: (r["model_key"], r["p_code"], r["benchmark_id"], r["source_path"]))
    return evidence_rows, p_rows, group_rows, untested_rows


def write_readme() -> None:
    text = """# Atomic Ability Rebenchmark Artifacts

Date: 2026-07-08

This directory stores the auditable intermediate artifacts for rebuilding the
education rebenchmark around `doc/atomic_ability_principle_audit_v3.md`.

Files:

- `01_inclusion_policy.md`: what is included/excluded from the main scoring layer.
- `02_benchmark_ability_mapping.jsonl`: machine-readable benchmark/subdimension to P01-P22 mapping.
- `02_benchmark_ability_mapping.md`: human-readable mapping table for review.
- `03_metric_normalization.md`: normalization and aggregation rules before any radar chart.
- `04_eval_run_inventory.jsonl`: current `reports/eval/**/summary.json` inventory with inclusion flags.
- `04_eval_run_inventory.md`: compact inventory summary.
- `05_otherbenchmark_score_inventory.jsonl`: parsed score rows from `otherbenchmark/`.
- `05_otherbenchmark_score_inventory.md`: compact parsed-score summary.
- `06_open_calibration_questions.md`: remaining decisions that should be reviewed before final HTML scoring.
- `07_run_deduplication_report.jsonl`: duplicate/canonical scoring decisions.
- `07_run_deduplication_report.md`: human-readable duplicate/canonical scoring decisions.
- `08_selected_score_evidence.jsonl`: canonical normalized benchmark score rows used for P scoring.
- `09_atomic_p_scores.jsonl`: per-model P01-P20 scores (relevance × confidence weights, no tier factor; both weights rule-derived since R25).
- `09_atomic_p_scores.md`: compact per-model P score table and coverage notes.
- `09_atomic_p_untested_cells.jsonl`: cells a panel model never ran (R26). These are
  reported as 未测过 and are deliberately excluded from every score and denominator —
  they are *not* filled with a substitute value. Cells the model cannot run because it
  lacks a required capability (e.g. no vision) are not here; they score 0 in
  `09_atomic_p_score_evidence.jsonl` with `source_type: capability_gap_zero`.
- `10_group_scores.jsonl`: SRG/FDR/LAD/CLM/CEG aggregate scores from available P scores.
- `10_group_scores.md`: compact group-score table.
- `11_atomic_ability_rebenchmark_report.html`: self-contained interactive HTML report.
- `12_benchmark_priority_analysis.jsonl`: benchmark/subdimension priority analysis for deciding what to keep, downweight, or skip.
- `12_benchmark_priority_report.html`: self-contained HTML triage report for benchmark portfolio decisions.
- `12_benchmark_portfolio_review.md`: Markdown-first two-indicator benchmark review table.

The final HTML should be generated only after the mapping and inclusion policy
are calibrated. Small-sample runs and judge-calibration runs are excluded from
the main scoring layer by default.
"""
    (OUT / "README.md").write_text(text, encoding="utf-8")


def write_inclusion_policy() -> None:
    text = """# Inclusion Policy

## Main scoring layer

Include a model-run only when all conditions hold:

1. It is a benchmark/model result, not a judge calibration, jury calibration, rubric prompt experiment, or backup copy.
2. It has a concrete model name and a non-zero `total_items`.
3. It has at least 100 total items, unless a human explicitly promotes the run after inspection.
4. It maps to at least one `P01-P20` ability through `02_benchmark_ability_mapping.jsonl`.
5. If multiple judge versions score the same model responses, keep only the selected primary judge in the main scoring layer and keep the others as context rows.

## Excluded by default

- Small samples and smoke tests: `total_items < 100`.
- Judge/rubric calibration: paths under `_judge_rubric`, `_judge_jury`, and benchmark ids containing `judge_calibration`.
- Backup directories such as `selfjudge_backup_*`.
- Protocol-only/data-resource rows without model scores.
- BEA/MRBench judge tasks: `bea2025_judge` and `mrbench_judge` are excluded in this pass. Tutor-generation tasks remain eligible.
- EduGuard P2 rows not judged by `deepseek-v3.2` are excluded from the repo scoring layer and preserved only as context.

## General-benchmark handling (R20)

MMLU-Pro, C-EVAL, AGIEval, OlympiadBench, and MathTutorBench problem-solving
style results map mostly to `P04` and `P05` (knowledge and reasoning), where
answering IS the construct. The former foundation-gate ×0.45 tier factor was
removed in R20: high answer accuracy still cannot dominate the education-side
abilities because general benchmarks are simply not mounted on education Ps.
Since R25 the guardrail is carried entirely by that structural constraint plus
per-cell relevance — confidence is rule-derived and no longer discounts a
benchmark for being general, so these exam-style benchmarks sit at 1.0
(objective scoring + externally vetted data).

EduIllustrate full-230 runs are included when `total_items >= 100`; 5-item
smoke/calibration runs remain excluded.
"""
    (OUT / "01_inclusion_policy.md").write_text(text, encoding="utf-8")


def write_mapping_files() -> None:
    dump_jsonl(OUT / "02_benchmark_ability_mapping.jsonl", MAPPINGS)
    lines = [
        "# Benchmark To Atomic Ability Mapping",
        "",
        "Each row maps one benchmark subdimension to 1-3 P abilities. Weights sum to 1 within the row.",
        "",
        "| Benchmark | Subdimension | Metric | Default weight | P weights | Rationale |",
        "|---|---|---|---:|---|---|",
    ]
    for row in MAPPINGS:
        pweights = ", ".join(f"{a['p_code']} {a['weight']:.2f}" for a in row["abilities"])
        lines.append(
            "| {benchmark_name} (`{benchmark_id}`) | {subdimension} | {metric_family} | {default_benchmark_weight:.2f} | {pweights} | {rationale} |".format(
                **row,
                pweights=pweights,
            )
        )
    (OUT / "02_benchmark_ability_mapping.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_normalization() -> None:
    lines = [
        "# Metric Normalization And Aggregation",
        "",
        "All benchmark-native metrics are first normalized to a 0-10 scale.",
        "",
        "| Metric family | Direction | Rule |",
        "|---|---|---|",
    ]
    for metric, direction, rule in NORMALIZATION:
        lines.append(f"| `{metric}` | {direction} | `{rule}` |")
    lines.extend(
        [
            "",
            "## Aggregation order",
            "",
            "1. Normalize each benchmark subdimension score to 0-10.",
            "2. Allocate that score to P abilities using `02_benchmark_ability_mapping.jsonl` weights.",
            "3. `score_10`: facet-level weighted average with effective weight = relevance × confidence (five relevance tiers + the two-factor confidence rule, R25); P score = equal-weight mean over facets with evidence.",
            "4. Report coverage separately per model/P ability: number of contributing rows, total effective weight, and benchmark families.",
            "5. Aggregate P abilities to SRG/FDR/LAD/CLM/CEG only after P-level scores are available. Missing P abilities are not imputed.",
            "",
            "## Resolved scoring choices in this pass",
            "",
            "- R20: the four-level evidence-tier system (and the foundation-gate ×0.45 factor) is removed; general benchmarks are constrained structurally (not mounted on education Ps).",
            "- R25: relevance uses five tiers (1.0/0.8/0.5/0.2/0); confidence is derived from two factors — scoring method (objective / LLM-judge) and data quality (externally vetted / self-built) — each -0.15.",
            "- EduGuard P2 uses `deepseek-v3.2` judge as the primary scoring judge.",
            "- R23: BEA/MRBench judge tasks are scored (only on the subjective-scoring P, whose construct IS judging ability); exclusion is carried per cell, not by a global list.",
            "- EduIllustrate full-230 runs are eligible; small 5-item runs are excluded.",
        ]
    )
    (OUT / "03_metric_normalization.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_inventory(rows: list[dict[str, Any]]) -> None:
    dump_jsonl(OUT / "04_eval_run_inventory.jsonl", rows)
    include = [r for r in rows if r["main_inclusion"] == "include_candidate"]
    exclude = [r for r in rows if r["main_inclusion"] != "include_candidate"]
    by_bench: dict[str, dict[str, int]] = {}
    for r in rows:
        slot = by_bench.setdefault(r["benchmark"], {"include_candidate": 0, "exclude_from_main": 0})
        slot[r["main_inclusion"]] += 1
    lines = [
        "# Eval Run Inventory",
        "",
        f"Total summary files scanned: {len(rows)}",
        f"Included candidates: {len(include)}",
        f"Excluded from main: {len(exclude)}",
        "",
        "| Benchmark | Include candidates | Excluded |",
        "|---|---:|---:|",
    ]
    for bench, counts in sorted(by_bench.items()):
        lines.append(f"| `{bench}` | {counts['include_candidate']} | {counts['exclude_from_main']} |")
    lines.extend(
        [
            "",
            "Detailed per-run records are in `04_eval_run_inventory.jsonl`.",
            "",
            "Important: `include_candidate` means eligible for the next scoring pass, not final acceptance.",
            "Duplicate model-runs and judge variants still need a final de-duplication policy before scoring.",
        ]
    )
    (OUT / "04_eval_run_inventory.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_otherbenchmark_scores(rows: list[dict[str, Any]]) -> None:
    dump_jsonl(OUT / "05_otherbenchmark_score_inventory.jsonl", rows)
    by_bench: dict[str, int] = {}
    by_metric: dict[str, int] = {}
    by_role: dict[str, int] = {}
    for row in rows:
        by_bench[row["benchmark_id"]] = by_bench.get(row["benchmark_id"], 0) + 1
        by_metric[row["metric"]] = by_metric.get(row["metric"], 0) + 1
        role = row.get("score_role", "scoring_candidate")
        by_role[role] = by_role.get(role, 0) + 1
    lines = [
        "# Otherbenchmark Score Inventory",
        "",
        f"Parsed score rows: {len(rows)}",
        "",
        "## By Score Role",
        "",
        "| Role | Rows |",
        "|---|---:|",
    ]
    for role, n in sorted(by_role.items()):
        lines.append(f"| `{role}` | {n} |")
    lines.extend(
        [
            "",
            "`scoring_candidate` rows are eligible for the P-score layer. `legacy_context` rows are stored for audit only.",
            "",
            "## By Benchmark",
            "",
            "| Benchmark | Rows |",
            "|---|---:|",
        ]
    )
    for bench, n in sorted(by_bench.items()):
        lines.append(f"| `{bench}` | {n} |")
    lines.extend(["", "## By Metric", "", "| Metric | Rows |", "|---|---:|"])
    for metric, n in sorted(by_metric.items()):
        lines.append(f"| `{metric}` | {n} |")
    lines.extend(
        [
            "",
            "## Sample Rows",
            "",
            "| Benchmark | Role | Subdimension | Model | Metric | Raw value | Notes |",
            "|---|---|---|---|---|---:|---|",
        ]
    )
    for row in rows[:40]:
        lines.append(
            f"| `{row['benchmark_id']}` | `{row.get('score_role', 'scoring_candidate')}` | {row['subdimension']} | {row['model']} | `{row['metric']}` | {row['raw_value']} | {row['notes']} |"
        )
    lines.append("")
    lines.append("Full parsed rows are in `05_otherbenchmark_score_inventory.jsonl`.")
    (OUT / "05_otherbenchmark_score_inventory.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_deduplication_report(dedupe_rows: list[dict[str, Any]], minimax_rows: list[dict[str, Any]]) -> None:
    dump_jsonl(OUT / "07_run_deduplication_report.jsonl", dedupe_rows + minimax_rows)
    lines = [
        "# Run Deduplication Report",
        "",
        "Canonical scoring rules:",
        "",
        "1. Keep only `score_role=scoring_candidate` rows for P scoring.",
        "2. Prefer repo `summary.json` over derived HTML/Markdown report rows when the same benchmark/model/subdimension is duplicated.",
        "3. For MiniMax-M3 conflicts, prefer included `minimax3/` paths and fuller-scored runs.",
        "4. EduGuard P2 keeps only `deepseek-v3.2` judge rows in main scoring.",
        "",
        f"Duplicate score groups recorded: {len(dedupe_rows)}",
        f"MiniMax-M3 path-conflict rows recorded: {len(minimax_rows)}",
        "",
        "## Duplicate Score Rows",
        "",
        "| Status | Benchmark | Model key | Source | Score | Path |",
        "|---|---|---|---|---:|---|",
    ]
    for row in dedupe_rows[:80]:
        lines.append(
            f"| {row['status']} | `{row['benchmark_id']}` | `{row['model_key']}` | {row['source_type']} | {row['score_10']:.4f} | `{row['source_path']}` |"
        )
    lines.extend(
        [
            "",
            "## MiniMax-M3 Path Conflicts",
            "",
            "| Status | Benchmark | Metric | Value | Scored/Total | Inclusion | Path |",
            "|---|---|---|---:|---:|---|---|",
        ]
    )
    for row in minimax_rows[:80]:
        lines.append(
            f"| {row['canonical_status']} | `{row['benchmark']}` | `{row['primary_metric']}` | {row['primary_value']} | {row['scored']}/{row['total_items']} | {row['main_inclusion']} | `{row['path']}` |"
        )
    lines.append("")
    lines.append("Full records are in `07_run_deduplication_report.jsonl`.")
    (OUT / "07_run_deduplication_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_score_evidence(rows: list[dict[str, Any]]) -> None:
    dump_jsonl(OUT / "08_selected_score_evidence.jsonl", rows)
    by_source: dict[str, int] = {}
    by_bench: dict[str, int] = {}
    for row in rows:
        by_source[row["source_type"]] = by_source.get(row["source_type"], 0) + 1
        by_bench[row["benchmark_id"]] = by_bench.get(row["benchmark_id"], 0) + 1
    lines = [
        "# Selected Score Evidence",
        "",
        f"Canonical normalized score rows used for P scoring: {len(rows)}",
        "",
        "## By Source",
        "",
        "| Source | Rows |",
        "|---|---:|",
    ]
    for source, n in sorted(by_source.items()):
        lines.append(f"| `{source}` | {n} |")
    lines.extend(["", "## By Benchmark", "", "| Benchmark | Rows |", "|---|---:|"])
    for bench, n in sorted(by_bench.items()):
        lines.append(f"| `{bench}` | {n} |")
    lines.extend(
        [
            "",
            "## Sample Rows",
            "",
            "| Benchmark | Model key | Metric | Raw | Score 0-10 | Source |",
            "|---|---|---|---:|---:|---|",
        ]
    )
    for row in rows[:80]:
        lines.append(
            f"| `{row['benchmark_id']}` | `{row['model_key']}` | `{row['metric']}` | {row['raw_value']} | {row['score_10']:.4f} | `{row['source_path']}` |"
        )
    lines.append("")
    lines.append("Full selected rows are in `08_selected_score_evidence.jsonl`.")
    (OUT / "08_selected_score_evidence.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_atomic_scores(
    p_rows: list[dict[str, Any]],
    evidence_rows: list[dict[str, Any]],
    untested_rows: list[dict[str, Any]],
) -> None:
    dump_jsonl(OUT / "09_atomic_p_score_evidence.jsonl", evidence_rows)
    dump_jsonl(OUT / "09_atomic_p_scores.jsonl", p_rows)
    dump_jsonl(OUT / "09_atomic_p_untested_cells.jsonl", untested_rows)
    covered = sorted({row["p_code"] for row in p_rows if row["score_10"] is not None})
    missing = [code for code in P_GROUPS if code not in covered]
    n_untested_p = sum(1 for row in p_rows if row["score_10"] is None)
    n_zero_cells = sum(1 for row in evidence_rows if row.get("source_type") == "capability_gap_zero")
    lines = [
        "# Atomic P Scores",
        "",
        f"P-score rows: {len(p_rows)}",
        f"Covered P codes: {', '.join(covered) if covered else 'none'}",
        f"Missing P codes: {', '.join(missing) if missing else 'none'}",
        f"P rows reported as 未测过 (score_10 = null): {n_untested_p}",
        f"Capability-gap zero cells (score_10 = 0, counted): {n_zero_cells}",
        f"Untested cells (not counted; see `09_atomic_p_untested_cells.jsonl`): {len(untested_rows)}",
        "",
        "`score_10`: facet-weighted average with effective weight = relevance × confidence (R25 rule-derived weights). Coverage completeness is reported separately and is not folded back into the score.",
        "",
        "## Missing-cell policy (R26, 2026-08-04)",
        "",
        "The R22 rule -- fill a panel model's missing cell with the lowest score any tested",
        "model got there -- is **removed**. A missing cell is now classified:",
        "",
        "- `untested`: never run. No score, no denominator, reported as 未测过. A P whose",
        "  cells are all untested gets `score_10: null`, **not** 0.",
        "- `capability_gap`: the model lacks a capability the cell requires for *every* item",
        "  (vision only so far; see `MODEL_CAPABILITIES` / `CELL_CAPABILITY_REQUIREMENTS`).",
        "  That is a real capability gap rather than a scheduling gap, so it scores **0** and counts.",
        "",
        "Cells where only *some* items need the capability (tutorbench, olympiadbench overall)",
        "stay `untested`: a text-only model earns a genuine non-zero score there, so 0 would be",
        "a measurement artifact rather than a capability difference.",
        "",
        "## Sample Scores",
        "",
        "| Model key | P | Group | Score | Evidence | 0-score cells | Untested cells | Weight sum | Benchmarks |",
        "|---|---|---|---:|---:|---:|---:|---:|---|",
    ]
    for row in p_rows[:120]:
        score = "未测过" if row["score_10"] is None else row["score_10"]
        lines.append(
            f"| `{row['model_key']}` | `{row['p_code']}` {row['p_name']} | {row['group']} | {score} "
            f"| {row['evidence_count']} | {row['capability_zero_count']} | {row['untested_cell_count']} "
            f"| {row['weight_sum']} | {', '.join(row['benchmarks'])} |"
        )
    lines.extend(
        [
            "",
            "## Coverage Notes",
            "",
            "- `P17`-`P19` are covered through EduGuard P1/P2 safety evidence.",
            "- `P08` (tool use / long-horizon) and `P20` (academic integrity) are declared domain gaps; `P16`/`P14` are single-source and `P12` covers 2 of 4 declared sub-abilities; `P18` has zero independent evidence (shared-SATA single cell) and `P11` is expression-quality-only.",
            "- The atomic list is `P01-P20` (R20 doc-scheme renumbering, no tombstones).",
            "",
            "Full P rows are in `09_atomic_p_scores.jsonl`; allocated evidence rows are in `09_atomic_p_score_evidence.jsonl`.",
        ]
    )
    (OUT / "09_atomic_p_scores.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_group_scores(group_rows: list[dict[str, Any]]) -> None:
    dump_jsonl(OUT / "10_group_scores.jsonl", group_rows)
    lines = [
        "# Group Scores",
        "",
        "These are provisional SRG/FDR/LAD/CLM/CEG aggregates from P abilities that have a score. Untested P abilities are left out of the average (never substituted, never zeroed); capability-gap P abilities score 0 and are included.",
        "",
        "| Model key | Group | Score | P count | P codes |",
        "|---|---|---:|---:|---|",
    ]
    for row in group_rows:
        lines.append(
            f"| `{row['model_key']}` | {row['group']} | {row['score_10']} | {row['p_count_with_evidence']} | {', '.join(row['p_codes'])} |"
        )
    (OUT / "10_group_scores.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def json_payload(rows: Any) -> str:
    return json.dumps(rows, ensure_ascii=False, sort_keys=True).replace("</", "<\\/")


def write_final_html(
    *,
    eval_rows: list[dict[str, Any]],
    other_rows: list[dict[str, Any]],
    selected_score_rows: list[dict[str, Any]],
    evidence_rows: list[dict[str, Any]],
    p_rows: list[dict[str, Any]],
    group_rows: list[dict[str, Any]],
    duplicate_rows: list[dict[str, Any]],
    minimax_rows: list[dict[str, Any]],
) -> None:
    # 未测过的 P 行（score_10=None）不算覆盖，否则「有数据的能力数」会把空白算进去。
    covered = sorted({row["p_code"] for row in p_rows if row["score_10"] is not None})
    missing = [code for code in P_GROUPS if code not in covered]
    by_source: dict[str, int] = {}
    for row in selected_score_rows:
        by_source[row["source_type"]] = by_source.get(row["source_type"], 0) + 1
    other_roles: dict[str, int] = {}
    for row in other_rows:
        role = row.get("score_role", "scoring_candidate")
        other_roles[role] = other_roles.get(role, 0) + 1

    models = sorted({row["model_key"] for row in p_rows})
    default_model = "minimax-m3" if "minimax-m3" in models else (models[0] if models else "")
    axis_order = ["SRG", "FDR", "LAD", "CLM", "CEG"]
    axis_labels = {
        "SRG": "任务理解与多模态交互",
        "FDR": "知识推理与可靠执行",
        "LAD": "学习诊断与教育测评",
        "CLM": "学习者建模与适应性教学",
        "CEG": "教育安全与学术规范",
    }
    p_meta = [
        {"p_code": code, "group": group, "p_name": name}
        for code, (group, name) in P_GROUPS.items()
    ]
    p_mapping_rows: list[dict[str, Any]] = []
    for mapping in MAPPINGS:
        for ability in mapping["abilities"]:
            p_mapping_rows.append(
                {
                    "p_code": ability["p_code"],
                    "p_name": ability["p_name"],
                    "group": ability["group"],
                    "ability_weight": ability["weight"],
                    "benchmark_id": mapping["benchmark_id"],
                    "benchmark_name": mapping["benchmark_name"],
                    "subdimension": mapping["subdimension"],
                    "metric_family": mapping["metric_family"],
                    "benchmark_weight": mapping["default_benchmark_weight"],
                    "rationale": mapping["rationale"],
                }
            )
    all_benchmark_dims = sorted({(row["benchmark_id"], row["subdimension"]) for row in selected_score_rows})
    coverage_rows: list[dict[str, Any]] = []
    for model in models:
        model_score_rows = [row for row in selected_score_rows if row["model_key"] == model]
        model_p_rows = [row for row in p_rows if row["model_key"] == model and row["score_10"] is not None]
        covered_dims = sorted({(row["benchmark_id"], row["subdimension"]) for row in model_score_rows})
        covered_p = sorted({row["p_code"] for row in model_p_rows})
        missing_p = [code for code in P_GROUPS if code not in covered_p]
        coverage_rows.append(
            {
                "model_key": model,
                "score_row_count": len(model_score_rows),
                "benchmark_dimension_count": len(covered_dims),
                "benchmark_dimension_total": len(all_benchmark_dims),
                "benchmark_dimension_coverage": round(len(covered_dims) / len(all_benchmark_dims), 4) if all_benchmark_dims else 0,
                "p_count": len(covered_p),
                "p_total": len(P_GROUPS),
                "p_coverage": round(len(covered_p) / len(P_GROUPS), 4),
                "weight_sum": round(sum(float(row["weight_sum"]) for row in model_p_rows), 4),
                "covered_p": covered_p,
                "missing_p": missing_p,
                "covered_benchmark_dimensions": [f"{bench} / {subdim}" for bench, subdim in covered_dims],
            }
        )

    html_text = f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>原子能力 Rebenchmark 可视化报告</title>
<style>
:root {{
  --paper:#fbf5e8; --ink:#14213d; --muted:#657084; --line:#dfd4bf; --panel:#fffaf0;
  --teal:#0f766e; --blue:#2F80ED; --orange:#F2994A; --green:#27AE60; --purple:#9B51E0; --red:#EB5757;
  --shadow:0 18px 50px rgba(20,33,61,.10); --radius:22px;
}}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:
  radial-gradient(circle at 8% 6%, rgba(242,153,74,.22), transparent 28%),
  radial-gradient(circle at 86% 10%, rgba(47,128,237,.18), transparent 30%),
  linear-gradient(135deg,#fff9ec 0%,#f8f0df 48%,#eef6f3 100%);
  color:var(--ink); font-family:"Avenir Next","PingFang SC","Hiragino Sans GB","Microsoft YaHei",Arial,sans-serif; line-height:1.55; }}
main {{ width:min(1440px,94vw); margin:0 auto; padding:36px 0 80px; }}
header.hero {{ position:relative; padding:44px; border:1px solid rgba(20,33,61,.12); border-radius:32px; background:rgba(255,250,240,.82); box-shadow:var(--shadow); overflow:hidden; }}
header.hero:after {{ content:""; position:absolute; right:-120px; top:-120px; width:380px; height:380px; border-radius:50%; background:conic-gradient(from 90deg,var(--blue),var(--green),var(--orange),var(--red),var(--blue)); opacity:.14; }}
.eyebrow {{ margin:0 0 12px; text-transform:uppercase; letter-spacing:.18em; font-size:12px; font-weight:800; color:var(--teal); }}
header.hero h1 {{ font-family:"Optima","Palatino Linotype","Songti SC",serif; font-size:clamp(30px,3.8vw,54px); line-height:1.06; margin:0 0 18px; max-width:1120px; letter-spacing:0; }}
header.hero p.hero-sub {{ font-size:17px; color:#3c485c; max-width:1040px; margin:0; }}
.summary {{ display:grid; grid-template-columns:repeat(5,minmax(150px,1fr)); gap:12px; margin:16px 0 18px; }}
.kpi {{ background:rgba(255,255,255,.68); border:1px solid rgba(20,33,61,.10); border-radius:20px; padding:18px 18px; }}
.kpi .v {{ font-size:30px; line-height:1; font-weight:850; color:var(--ink); }}
.kpi .l {{ color:var(--muted); font-size:12.5px; }}
.toolbar {{ display:grid; grid-template-columns: minmax(260px, 1fr) 310px; gap:12px; align-items:end; margin:14px 0; }}
label {{ display:block; font-size:12px; color:var(--muted); margin-bottom:5px; }}
select, .seg {{ width:100%; border:1px solid rgba(20,33,61,.12); background:rgba(255,255,255,.82); border-radius:14px; min-height:42px; padding:8px 10px; color:var(--ink); }}
.seg {{ display:flex; gap:6px; padding:4px; }}
.seg button {{ flex:1; border:0; border-radius:6px; background:transparent; color:var(--muted); font-weight:650; cursor:pointer; }}
.seg button.active {{ background:#dff4eb; color:#0d6b44; }}
.grid {{ display:grid; grid-template-columns: minmax(420px, 0.9fr) minmax(520px, 1.1fr); gap:16px; align-items:start; }}
.panel {{ margin-top:18px; background:rgba(255,250,240,.74); border:1px solid rgba(20,33,61,.11); border-radius:28px; padding:22px; box-shadow:0 12px 32px rgba(20,33,61,.07); }}
.panel h2 {{ font-family:"Optima","Palatino Linotype","Songti SC",serif; margin:0 0 14px; font-size:26px; letter-spacing:0; }}
.radar-wrap {{ display:grid; place-items:center; min-height:420px; }}
canvas {{ width:min(100%, 520px); max-width:520px; aspect-ratio:1; background:#fff; border-radius:24px; border:1px solid rgba(20,33,61,.08); }}
.axis-list {{ display:grid; grid-template-columns:repeat(5,1fr); gap:8px; margin-top:8px; }}
.axis {{ border:1px solid rgba(20,33,61,.10); border-radius:18px; padding:12px; background:rgba(255,255,255,.72); min-height:92px; }}
.axis .code {{ font-weight:750; }}
.axis .score {{ font-size:22px; color:var(--blue); font-weight:750; }}
.axis .small {{ color:var(--muted); font-size:12px; }}
table {{ width:100%; border-collapse:collapse; font-size:13px; }}
th, td {{ border-bottom:1px solid rgba(20,33,61,.09); padding:9px 11px; text-align:left; vertical-align:top; }}
th {{ background:#f6ead2; color:#2e3a50; font-size:12px; position:sticky; top:0; z-index:1; }}
td.num, th.num {{ text-align:right; font-variant-numeric:tabular-nums; }}
.table-wrap {{ max-height:540px; overflow:auto; border:1px solid rgba(20,33,61,.10); border-radius:18px; background:rgba(255,255,255,.55); }}
.note {{ background:rgba(15,118,110,.08); border-left:5px solid var(--teal); border-radius:14px; padding:14px 16px; color:#304159; margin:14px 0; }}
.chips {{ display:flex; gap:7px; flex-wrap:wrap; }}
.chip {{ display:inline-block; border:1px solid rgba(20,33,61,.10); background:rgba(255,255,255,.70); border-radius:999px; padding:5px 10px; font-size:12px; color:var(--muted); font-weight:700; }}
.twocol {{ display:grid; grid-template-columns:1fr 1fr; gap:16px; margin-top:16px; }}
.mono {{ font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace; font-size:12px; }}
.barbox {{ height:8px; background:#eadfc9; border-radius:999px; overflow:hidden; min-width:70px; }}
.bar {{ height:100%; background:linear-gradient(90deg,var(--blue),#00a6a6); }}
.formula-grid {{ display:grid; grid-template-columns:repeat(2,1fr); gap:14px; }}
.formula {{ background:rgba(255,255,255,.70); border:1px solid rgba(20,33,61,.10); border-radius:18px; padding:14px 15px; }}
.formula b {{ display:block; margin-bottom:6px; color:#20304b; }}
.formula code {{ display:block; white-space:normal; background:#fff6df; border:1px solid #ead9a9; border-radius:10px; padding:9px; color:#5f4211; }}
.inline-controls {{ display:grid; grid-template-columns:minmax(220px,320px) 1fr; gap:12px; align-items:end; margin-bottom:12px; }}
footer {{ color:var(--muted); font-size:12px; padding:22px 0 6px; }}
@media (max-width:980px) {{
  .summary {{ grid-template-columns:repeat(2,1fr); }}
  .toolbar, .grid, .twocol, .formula-grid, .inline-controls {{ grid-template-columns:1fr; }}
  .axis-list {{ grid-template-columns:repeat(2,1fr); }}
}}
</style>
</head>
<body>
<main>
<header class="hero">
  <p class="eyebrow">Capability-Oriented Rebenchmark · 2026</p>
  <h1>原子能力 Rebenchmark 可视化报告</h1>
  <p class="hero-sub">基于本仓库评测与 <code>otherbenchmark/</code> 结果，将 benchmark/subdimension 映射到定稿映射 v6（<code>data/mapping_measurement_model_v6.json</code>）的 P01-P20 原子能力，并聚合到 SRG/FDR/LAD/CLM/CEG 五大维度。模型选择与分数版本切换逻辑保持可交互。</p>
</header>
  <section class="summary">
    <div class="kpi"><div class="v">{len(MAPPINGS)}</div><div class="l">benchmark / 维度映射行</div></div>
    <div class="kpi"><div class="v">{sum(1 for r in eval_rows if r['main_inclusion'] == 'include_candidate')}</div><div class="l">本仓库可计分候选 run</div></div>
    <div class="kpi"><div class="v">{len(other_rows)}</div><div class="l">otherbenchmark 原始分数行</div></div>
    <div class="kpi"><div class="v">{len(selected_score_rows)}</div><div class="l">去重后的计分证据行</div></div>
    <div class="kpi"><div class="v">{len(covered)}/20</div><div class="l">已覆盖 P 级原子能力</div></div>
  </section>

  <section class="panel">
    <h2>评分口径</h2>
    <div class="chips">
      <span class="chip">R20：证据四档已废除，权重 = 相关度 × 置信</span>
      <span class="chip">EduGuard P2 主裁判：{EDUGUARD_P2_PRIMARY_JUDGE}</span>
      <span class="chip">BEA/MRBench judge task 已排除</span>
      <span class="chip">EduIllustrate full-230 已纳入</span>
      <span class="chip">MiniMax-M3 优先 minimax3/full-scored run</span>
    </div>
    <div class="note">未覆盖或极弱覆盖的 P code：<b>{", ".join(missing)}</b>。P17-P19 当前主要由 EduGuard 安全证据覆盖。当前 atomic list 为 P01-P20（R20 文档口径编号）。</div>
  </section>

  <section class="panel">
    <h2>最终分数计算公式</h2>
    <div class="formula-grid">
      <div class="formula">
        <b>1. 原始指标归一化到 10 分制</b>
        <code>accuracy/pass_rate/rfs: score10 = value × 10<br>ASR: score10 = (1 - ASR) × 10<br>0-100 指标: score10 = value / 10<br>0-5 指标: score10 = value × 2<br>0-6 指标: score10 = value / 6 × 10</code>
      </div>
      <div class="formula">
        <b>2. benchmark 分数分配到 P 能力（facet 内加权，跨 facet 等权）</b>
        <code>effective_weight = benchmark_weight × ability_weight<br>facet = Σ(score10 × effective_weight) / Σ(effective_weight)<br>P = mean(有证据 facet)</code>
      </div>
    </div>
    <div class="note">当前 HTML 不再把覆盖惩罚折入主分数。覆盖问题改为单独展示“覆盖完整度”，避免把“没测”混同为“能力差”。五大维度分数是在每个模型已有 P 能力分数上求平均；缺失 P 不做插补。</div>
  </section>

  <section class="panel">
    <h2>P 能力与 benchmark 对应关系</h2>
    <div class="inline-controls">
      <div>
        <label for="pMapSelect">选择 P 能力</label>
        <select id="pMapSelect"></select>
      </div>
      <div class="note" style="margin:0">一个 benchmark/subdimension 可映射到 1-3 个 P 能力；表中的“能力权重”是在该 benchmark 维度内分给该 P 的比例。</div>
    </div>
    <div class="table-wrap">
      <table id="pMapTable">
        <thead><tr><th>P</th><th>Benchmark</th><th>细分维度</th><th>指标族</th><th class="num">benchmark 权重</th><th class="num">能力权重</th><th>映射理由</th></tr></thead>
        <tbody></tbody>
      </table>
    </div>
  </section>

  <div class="toolbar">
    <div>
      <label for="modelSelect">选择模型</label>
      <select id="modelSelect"></select>
    </div>
  </div>

  <section class="grid">
    <div class="panel">
      <h2>五维能力雷达图</h2>
      <div class="radar-wrap"><canvas id="radar" width="720" height="720"></canvas></div>
      <div class="axis-list" id="axisCards"></div>
    </div>
    <div class="panel">
      <h2>P01-P20 原子能力明细</h2>
      <div class="table-wrap">
        <table id="pTable">
          <thead><tr><th>P</th><th>大类</th><th class="num">当前分数</th><th class="num">证据数</th><th>Benchmark</th></tr></thead>
          <tbody></tbody>
        </table>
      </div>
    </div>
  </section>

  <section class="twocol">
    <div class="panel">
      <h2>当前模型证据分配</h2>
      <div class="table-wrap">
        <table id="evidenceTable">
          <thead><tr><th>P</th><th>Benchmark</th><th>指标</th><th class="num">10 分制</th><th class="num">调整权重</th><th>来源</th></tr></thead>
          <tbody></tbody>
        </table>
      </div>
    </div>
    <div class="panel">
      <h2>覆盖与来源结构</h2>
      <table>
        <tbody>
          <tr><th>本仓库 canonical 行</th><td class="num">{by_source.get('repo_eval', 0)}</td></tr>
          <tr><th>otherbenchmark canonical 行</th><td class="num">{by_source.get('otherbenchmark', 0)}</td></tr>
          <tr><th>otherbenchmark 可计分 / 上下文</th><td class="num">{other_roles.get('scoring_candidate', 0)} / {other_roles.get('legacy_context', 0)}</td></tr>
          <tr><th>已审计重复行</th><td class="num">{len(duplicate_rows)}</td></tr>
          <tr><th>MiniMax-M3 冲突行</th><td class="num">{len(minimax_rows)}</td></tr>
        </tbody>
      </table>
      <div class="note">雷达图只聚合已有 P 证据，不对缺失 P code 做插补。不同模型跑过的 benchmark 不完全一致，因此横向比较时必须同时看下面的覆盖完整度。</div>
    </div>
  </section>

  <section class="panel">
    <h2>模型覆盖完整度</h2>
    <div class="note">覆盖完整度不是能力分。它描述每个模型实际跑过多少 benchmark/subdimension、覆盖多少 P 能力，以及还有哪些 P 缺失。模型之间 benchmark 集合不一致时，应优先查看这一表再解释雷达图。</div>
    <div class="table-wrap">
      <table id="coverageTable">
        <thead><tr><th>模型</th><th class="num">分数行</th><th class="num">benchmark 维度覆盖</th><th class="num">P 覆盖</th><th class="num">有效权重和</th><th>缺失 P</th><th>覆盖 benchmark 维度</th></tr></thead>
        <tbody></tbody>
      </table>
    </div>
  </section>

  <section class="panel">
    <h2>按 benchmark 查看模型表现</h2>
    <div class="inline-controls">
      <div>
        <label for="benchSelect">选择 benchmark / 细分维度</label>
        <select id="benchSelect"></select>
      </div>
      <div class="note" style="margin:0">这里展示进入最终计算的 canonical score rows；重复 report/repo 行、legacy radar 行、小样本和被排除 judge task 不在此表中。</div>
    </div>
    <div class="table-wrap">
      <table id="benchmarkTable">
        <thead><tr><th>模型</th><th>Benchmark</th><th>细分维度</th><th>指标</th><th class="num">原始值</th><th class="num">10 分制</th><th>来源</th></tr></thead>
        <tbody></tbody>
      </table>
    </div>
  </section>

  <section class="panel" style="margin-top:16px">
    <h2>五大维度分数全表</h2>
    <div class="table-wrap">
      <table id="groupTable">
        <thead><tr><th>模型</th><th>大类</th><th class="num">当前分数</th><th class="num">P 数</th><th>P code</th></tr></thead>
        <tbody></tbody>
      </table>
    </div>
  </section>

  <footer>
    本报告由 <span class="mono">reports/atomic_ability_rebenchmark/</span> 中间产物生成；生成脚本：<span class="mono">scripts/build_atomic_ability_rebenchmark_artifacts.py</span>。
  </footer>
</main>

<script id="pRows" type="application/json">{json_payload(p_rows)}</script>
<script id="groupRows" type="application/json">{json_payload(group_rows)}</script>
<script id="evidenceRows" type="application/json">{json_payload(evidence_rows)}</script>
<script id="pMeta" type="application/json">{json_payload(p_meta)}</script>
<script id="selectedScoreRows" type="application/json">{json_payload(selected_score_rows)}</script>
<script id="pMappingRows" type="application/json">{json_payload(p_mapping_rows)}</script>
<script id="coverageRows" type="application/json">{json_payload(coverage_rows)}</script>
<script>
const pRows = JSON.parse(document.getElementById('pRows').textContent);
const groupRows = JSON.parse(document.getElementById('groupRows').textContent);
const evidenceRows = JSON.parse(document.getElementById('evidenceRows').textContent);
const pMeta = JSON.parse(document.getElementById('pMeta').textContent);
const selectedScoreRows = JSON.parse(document.getElementById('selectedScoreRows').textContent);
const pMappingRows = JSON.parse(document.getElementById('pMappingRows').textContent);
const coverageRows = JSON.parse(document.getElementById('coverageRows').textContent);
const axes = {json_payload(axis_order)};
const axisLabels = {json_payload(axis_labels)};
let selectedModel = {json_payload(default_model)};
let selectedPForMapping = 'ALL';
let selectedBenchmarkView = 'ALL';

function fmt(v) {{ return v === null || v === undefined ? '—' : Number(v).toFixed(2); }}
function esc(s) {{ return String(s ?? '').replace(/[&<>"']/g, c => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[c])); }}
function scoreFor(row) {{ return row ? row.score_10 : null; }}

function initModelSelect() {{
  const models = [...new Set(pRows.map(r => r.model_key))].sort();
  const sel = document.getElementById('modelSelect');
  sel.innerHTML = models.map(m => `<option value="${{esc(m)}}">${{esc(m)}}</option>`).join('');
  sel.value = selectedModel;
  sel.addEventListener('change', () => {{ selectedModel = sel.value; render(); }});

  const pSelect = document.getElementById('pMapSelect');
  pSelect.innerHTML = '<option value="ALL">全部 P 能力</option>' + pMeta.map(p => `<option value="${{p.p_code}}">${{p.p_code}} · ${{esc(p.p_name)}}</option>`).join('');
  pSelect.value = selectedPForMapping;
  pSelect.addEventListener('change', () => {{ selectedPForMapping = pSelect.value; renderPMappingTable(); }});

  const benchSelect = document.getElementById('benchSelect');
  const benchKeys = [...new Set(selectedScoreRows.map(r => `${{r.benchmark_id}}|||${{r.subdimension}}`))].sort();
  benchSelect.innerHTML = '<option value="ALL">全部 benchmark 维度</option>' + benchKeys.map(key => {{
    const [b, s] = key.split('|||');
    return `<option value="${{esc(key)}}">${{esc(b)}} · ${{esc(s)}}</option>`;
  }}).join('');
  benchSelect.value = selectedBenchmarkView;
  benchSelect.addEventListener('change', () => {{ selectedBenchmarkView = benchSelect.value; renderBenchmarkTable(); }});
}}

function modelGroupRows() {{
  return groupRows.filter(r => r.model_key === selectedModel);
}}

function drawRadar() {{
  const canvas = document.getElementById('radar');
  const ctx = canvas.getContext('2d');
  const w = canvas.width, h = canvas.height;
  ctx.clearRect(0,0,w,h);
  const cx = w/2, cy = h/2 + 8, radius = 255;
  const rows = modelGroupRows();
  const byAxis = new Map(rows.map(r => [r.group, r]));

  ctx.font = '22px -apple-system, Segoe UI, sans-serif';
  ctx.textAlign = 'center';
  ctx.fillStyle = '#13201b';
  ctx.fillText(selectedModel, cx, 38);

  for (let ring=1; ring<=5; ring++) {{
    const r = radius * ring / 5;
    ctx.beginPath();
    axes.forEach((axis, i) => {{
      const a = -Math.PI/2 + i * 2*Math.PI/axes.length;
      const x = cx + Math.cos(a)*r, y = cy + Math.sin(a)*r;
      if (i === 0) ctx.moveTo(x,y); else ctx.lineTo(x,y);
    }});
    ctx.closePath();
    ctx.strokeStyle = ring === 5 ? '#b8c8bf' : '#dde7e1';
    ctx.lineWidth = ring === 5 ? 1.4 : 1;
    ctx.stroke();
  }}

  axes.forEach((axis, i) => {{
    const a = -Math.PI/2 + i * 2*Math.PI/axes.length;
    ctx.beginPath();
    ctx.moveTo(cx, cy);
    ctx.lineTo(cx + Math.cos(a)*radius, cy + Math.sin(a)*radius);
    ctx.strokeStyle = '#d9e3dd';
    ctx.stroke();
    const lx = cx + Math.cos(a)*(radius+52), ly = cy + Math.sin(a)*(radius+46);
    ctx.fillStyle = '#17362a';
    ctx.font = '18px -apple-system, Segoe UI, sans-serif';
    ctx.fillText(axis, lx, ly);
    const score = byAxis.has(axis) ? scoreFor(byAxis.get(axis)) : null;
    ctx.fillStyle = score == null ? '#98a59d' : '#2b6fae';
    ctx.font = '14px ui-monospace, SFMono-Regular, Menlo, monospace';
    ctx.fillText(score == null ? '无证据' : fmt(score), lx, ly + 20);
  }});

  ctx.beginPath();
  axes.forEach((axis, i) => {{
    const score = byAxis.has(axis) ? (scoreFor(byAxis.get(axis)) || 0) : 0;
    const r = radius * Math.max(0, Math.min(10, score)) / 10;
    const a = -Math.PI/2 + i * 2*Math.PI/axes.length;
    const x = cx + Math.cos(a)*r, y = cy + Math.sin(a)*r;
    if (i === 0) ctx.moveTo(x,y); else ctx.lineTo(x,y);
  }});
  ctx.closePath();
  ctx.fillStyle = 'rgba(47,125,84,.22)';
  ctx.strokeStyle = '#2f7d54';
  ctx.lineWidth = 3;
  ctx.fill();
  ctx.stroke();
}}

function renderAxisCards() {{
  const byAxis = new Map(modelGroupRows().map(r => [r.group, r]));
  document.getElementById('axisCards').innerHTML = axes.map(axis => {{
    const row = byAxis.get(axis);
    const score = row ? scoreFor(row) : null;
    return `<div class="axis"><div class="code">${{axis}}</div><div class="score">${{fmt(score)}}</div><div class="small">${{esc(axisLabels[axis])}}</div><div class="small">P code：${{row ? esc(row.p_codes.join(', ')) : '无'}}</div></div>`;
  }}).join('');
}}

function renderPTable() {{
  const rows = pRows.filter(r => r.model_key === selectedModel);
  const have = new Map(rows.map(r => [r.p_code, r]));
  const body = document.querySelector('#pTable tbody');
  body.innerHTML = pMeta.map(meta => {{
    const r = have.get(meta.p_code);
    const score = r ? scoreFor(r) : null;
    const pct = score == null ? 0 : Math.max(0, Math.min(100, score * 10));
    // R26：分数为空 = 未测过，不是 0；能力不具备的格已经以 0 分计入 score。
    const cell = score == null ? '<span class="small">未测过</span>' : `<b>${{fmt(score)}}</b>`;
    const zeroNote = r && r.capability_zero_count
      ? `<div class="small">含 ${{r.capability_zero_count}} 个「能力不具备记 0 分」的格</div>` : '';
    const untestedNote = r && r.untested_cell_count
      ? `<div class="small">另有 ${{r.untested_cell_count}} 个格未测过（未计入分母）</div>` : '';
    return `<tr>
      <td><b>${{meta.p_code}}</b> ${{esc(meta.p_name)}}</td>
      <td>${{meta.group}}</td>
      <td class="num">${{cell}}<div class="barbox"><div class="bar" style="width:${{pct}}%"></div></div></td>
      <td class="num">${{r ? r.evidence_count : 0}}</td>
      <td><div class="small">${{r && r.benchmarks.length ? esc(r.benchmarks.join(', ')) : '无证据'}}</div>${{zeroNote}}${{untestedNote}}</td>
    </tr>`;
  }}).join('');
}}

function renderEvidenceTable() {{
  const rows = evidenceRows.filter(r => r.model_key === selectedModel).slice(0, 220);
  document.querySelector('#evidenceTable tbody').innerHTML = rows.map(r => `<tr>
    <td>${{r.p_code}}</td>
    <td>${{esc(r.benchmark_id)}}<div class="small">${{esc(r.subdimension)}}</div></td>
    <td>${{esc(r.metric)}}</td>
    <td class="num">${{fmt(r.score_10)}}${{r.source_type === 'capability_gap_zero' ? '<div class="small">能力不具备</div>' : ''}}</td>
    <td class="num">${{Number(r.effective_weight).toFixed(3)}}</td>
    <td><span class="mono">${{r.source_type === 'capability_gap_zero' ? esc(r.coverage_reason || '') : esc(r.source_path)}}</span></td>
  </tr>`).join('');
}}

function renderGroupTable() {{
  const rows = groupRows.slice().sort((a,b) => a.model_key.localeCompare(b.model_key) || axes.indexOf(a.group)-axes.indexOf(b.group));
  document.querySelector('#groupTable tbody').innerHTML = rows.map(r => {{
    const score = scoreFor(r);
    const pct = score == null ? 0 : Math.max(0, Math.min(100, score * 10));
    return `<tr>
      <td>${{esc(r.model_key)}}</td><td>${{r.group}}</td>
      <td class="num"><b>${{fmt(score)}}</b><div class="barbox"><div class="bar" style="width:${{pct}}%"></div></div></td>
      <td class="num">${{r.p_count_with_evidence}}</td>
      <td>${{esc(r.p_codes.join(', '))}}</td>
    </tr>`;
  }}).join('');
}}

function renderCoverageTable() {{
  const rows = coverageRows.slice().sort((a,b) => b.p_coverage - a.p_coverage || b.benchmark_dimension_coverage - a.benchmark_dimension_coverage || a.model_key.localeCompare(b.model_key));
  document.querySelector('#coverageTable tbody').innerHTML = rows.map(r => {{
    const benchPct = Math.max(0, Math.min(100, Number(r.benchmark_dimension_coverage || 0) * 100));
    const pPct = Math.max(0, Math.min(100, Number(r.p_coverage || 0) * 100));
    return `<tr>
      <td><b>${{esc(r.model_key)}}</b></td>
      <td class="num">${{r.score_row_count}}</td>
      <td class="num"><b>${{r.benchmark_dimension_count}}/${{r.benchmark_dimension_total}}</b><div class="barbox"><div class="bar" style="width:${{benchPct}}%"></div></div></td>
      <td class="num"><b>${{r.p_count}}/${{r.p_total}}</b><div class="barbox"><div class="bar" style="width:${{pPct}}%"></div></div></td>
      <td class="num">${{Number(r.weight_sum).toFixed(2)}}</td>
      <td>${{r.missing_p.length ? esc(r.missing_p.join(', ')) : '无'}}</td>
      <td><div class="small">${{esc(r.covered_benchmark_dimensions.join('; '))}}</div></td>
    </tr>`;
  }}).join('');
}}

function renderPMappingTable() {{
  const rows = pMappingRows
    .filter(r => selectedPForMapping === 'ALL' || r.p_code === selectedPForMapping)
    .sort((a,b) => a.p_code.localeCompare(b.p_code) || a.benchmark_id.localeCompare(b.benchmark_id) || a.subdimension.localeCompare(b.subdimension));
  document.querySelector('#pMapTable tbody').innerHTML = rows.map(r => `<tr>
    <td><b>${{r.p_code}}</b><div class="small">${{esc(r.p_name)}}</div></td>
    <td>${{esc(r.benchmark_name)}}<div class="mono">${{esc(r.benchmark_id)}}</div></td>
    <td>${{esc(r.subdimension)}}</td>
    <td>${{esc(r.metric_family)}}</td>
    <td class="num">${{Number(r.benchmark_weight).toFixed(2)}}</td>
    <td class="num">${{Number(r.ability_weight).toFixed(2)}}</td>
    <td>${{esc(r.rationale)}}</td>
  </tr>`).join('');
}}

function renderBenchmarkTable() {{
  const rows = selectedScoreRows
    .filter(r => selectedBenchmarkView === 'ALL' || `${{r.benchmark_id}}|||${{r.subdimension}}` === selectedBenchmarkView)
    .sort((a,b) => a.benchmark_id.localeCompare(b.benchmark_id) || a.subdimension.localeCompare(b.subdimension) || b.score_10 - a.score_10 || a.model_key.localeCompare(b.model_key));
  document.querySelector('#benchmarkTable tbody').innerHTML = rows.map(r => {{
    const pct = Math.max(0, Math.min(100, Number(r.score_10 || 0) * 10));
    return `<tr>
      <td><b>${{esc(r.model_key)}}</b><div class="small">${{esc(r.model)}}</div></td>
      <td>${{esc(r.benchmark_id)}}</td>
      <td>${{esc(r.subdimension)}}</td>
      <td>${{esc(r.metric)}}</td>
      <td class="num">${{Number(r.raw_value).toFixed(4)}}</td>
      <td class="num"><b>${{fmt(r.score_10)}}</b><div class="barbox"><div class="bar" style="width:${{pct}}%"></div></div></td>
      <td><span class="mono">${{esc(r.source_path)}}</span></td>
    </tr>`;
  }}).join('');
}}

function render() {{
  drawRadar();
  renderAxisCards();
  renderPTable();
  renderEvidenceTable();
  renderGroupTable();
  renderCoverageTable();
  renderPMappingTable();
  renderBenchmarkTable();
}}

initModelSelect();
render();
</script>
</body>
</html>
"""
    (OUT / "11_atomic_ability_rebenchmark_report.html").write_text(html_text, encoding="utf-8")


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def analyze_benchmark_priorities(
    selected_score_rows: list[dict[str, Any]],
    p_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    total_models = len({row["model_key"] for row in selected_score_rows}) or 1
    model_target = min(8, total_models)
    p_model_counts: dict[str, int] = {}
    for row in p_rows:
        if row["score_10"] is None:  # 未测过不算一个模型面
            continue
        p_model_counts[row["p_code"]] = p_model_counts.get(row["p_code"], 0) + 1

    rows: list[dict[str, Any]] = []
    for mapping in MAPPINGS:
        matches = [
            row
            for row in selected_score_rows
            if row["benchmark_id"] == mapping["benchmark_id"] and row["subdimension"] == mapping["subdimension"]
        ]
        scores = [float(row["score_10"]) for row in matches]
        model_keys = sorted({row["model_key"] for row in matches})
        best_score = max(scores) if scores else None
        median_score = statistics.median(scores) if scores else None
        mean_score = statistics.mean(scores) if scores else None

        if scores:
            best_gap = clamp((9.0 - (best_score or 0.0)) / 9.0)
            median_gap = clamp((8.0 - (median_score or 0.0)) / 8.0)
            unsolved_index = 0.60 * best_gap + 0.40 * median_gap
            score_status = "基本解决" if best_score >= 8.8 and median_score >= 7.5 else "仍有区分度"
            if best_score < 7.5 or median_score < 6.2:
                score_status = "明显未解决"
        else:
            unsolved_index = 0.70
            score_status = "缺少当前跑分"

        ability_priority = sum(
            ability["weight"] * ABILITY_PRIORITY.get(ability["p_code"], 0.75)
            for ability in mapping["abilities"]
        )
        if any(ability["p_code"] in P_GAP_BONUS for ability in mapping["abilities"]):
            ability_priority = min(1.0, ability_priority + 0.06)
        excluded = bool(mapping.get("excluded")) or mapping["benchmark_id"] in EXCLUDED_SCORING_BENCHMARKS
        p_relevance_score = 100.0 * ability_priority
        importance_score = 100.0 * mapping["default_benchmark_weight"] * ability_priority

        model_coverage = len(model_keys) / model_target if model_target else 0.0
        p_gap = statistics.mean(
            1.0 - clamp(p_model_counts.get(ability["p_code"], 0) / 4.0)
            for ability in mapping["abilities"]
        )
        coverage_gap = 0.60 * (1.0 - clamp(model_coverage)) + 0.40 * p_gap

        priority_score = importance_score * (0.58 * unsolved_index + 0.32 * coverage_gap + 0.10)
        if excluded:
            priority_score *= 0.10

        if excluded:
            recommendation = "先不看"
            rationale = "本轮明确排除 judge task，避免把裁判能力混入模型教育能力。"
        elif priority_score >= 35 and importance_score >= 50:
            recommendation = "优先继续做"
            rationale = "重要性高，且当前最好分/中位数或覆盖仍显示明显空间。"
        elif importance_score >= 55 and unsolved_index < 0.18 and coverage_gap < 0.30:
            recommendation = "重要但可降频"
            rationale = "对应教育核心能力，但当前前沿模型表现较高且覆盖相对够用。"
        elif importance_score >= 45:
            recommendation = "值得保留/补跑"
            rationale = "能力相关性较强，适合保留为主榜或分项诊断。"
        elif priority_score >= 25:
            recommendation = "诊断性保留"
            rationale = "不是主排序核心，但能解释特定能力短板或补覆盖。"
        else:
            recommendation = "不必重点看"
            rationale = "当前重要性、区分度或可解释增量都偏低。"

        quadrant = "高重要/高缺口"
        if importance_score >= 55 and unsolved_index < 0.25:
            quadrant = "高重要/低缺口"
        elif importance_score < 55 and unsolved_index >= 0.25:
            quadrant = "低重要/高缺口"
        elif importance_score < 55 and unsolved_index < 0.25:
            quadrant = "低重要/低缺口"

        rows.append(
            {
                "benchmark_id": mapping["benchmark_id"],
                "benchmark_name": mapping["benchmark_name"],
                "subdimension": mapping["subdimension"],
                "excluded": excluded,
                "metric_family": mapping["metric_family"],
                "p_codes": [ability["p_code"] for ability in mapping["abilities"]],
                "p_weights": [
                    f"{ability['p_code']} {ability['weight']:.2f}" for ability in mapping["abilities"]
                ],
                "groups": sorted({ability["group"] for ability in mapping["abilities"]}),
                "benchmark_weight": mapping["default_benchmark_weight"],
                "p_relevance_score": round(p_relevance_score, 2),
                "all_model_average_score_10": round(mean_score, 4) if mean_score is not None else None,
                "importance_score": round(importance_score, 2),
                "unsolved_index": round(unsolved_index, 4),
                "coverage_gap": round(coverage_gap, 4),
                "priority_score": round(priority_score, 2),
                "best_score_10": round(best_score, 4) if best_score is not None else None,
                "median_score_10": round(median_score, 4) if median_score is not None else None,
                "mean_score_10": round(mean_score, 4) if mean_score is not None else None,
                "model_count": len(model_keys),
                "score_row_count": len(matches),
                "score_status": score_status,
                "recommendation": recommendation,
                "quadrant": quadrant,
                "rationale": rationale,
                "mapping_rationale": mapping["rationale"],
                "models": model_keys,
            }
        )
    rows.sort(key=lambda row: (row["recommendation"] != "优先继续做", -row["priority_score"], -row["importance_score"]))
    return rows


def write_benchmark_priority_report(priority_rows: list[dict[str, Any]]) -> None:
    dump_jsonl(OUT / "12_benchmark_priority_analysis.jsonl", priority_rows)
    buckets: dict[str, int] = {}
    for row in priority_rows:
        buckets[row["recommendation"]] = buckets.get(row["recommendation"], 0) + 1
    top_rows = [row for row in priority_rows if row["recommendation"] == "优先继续做"][:8]
    down_rows = [
        row
        for row in priority_rows
        if row["recommendation"] in {"先不看", "降为门槛项", "不必重点看", "重要但可降频"}
    ][:10]

    html_text = f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Benchmark 优先级分析</title>
<style>
:root {{ --bg:#f7f3ea; --panel:#fffdf7; --ink:#162033; --muted:#667085; --line:#ded6c8; --blue:#2f80ed; --green:#219653; --orange:#f2994a; --red:#d94f45; --teal:#0f766e; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:linear-gradient(135deg,#fffaf0,#edf6f2); color:var(--ink); font-family:"Avenir Next","PingFang SC","Microsoft YaHei",Arial,sans-serif; line-height:1.55; }}
main {{ width:min(1440px,94vw); margin:0 auto; padding:34px 0 76px; }}
.hero {{ border:1px solid rgba(22,32,51,.12); background:rgba(255,253,247,.86); border-radius:28px; padding:34px 38px; box-shadow:0 18px 48px rgba(22,32,51,.08); }}
.eyebrow {{ margin:0 0 10px; color:var(--teal); text-transform:uppercase; letter-spacing:.16em; font-size:12px; font-weight:800; }}
h1 {{ font-family:"Optima","Songti SC",serif; font-size:clamp(30px,4vw,52px); line-height:1.08; margin:0 0 14px; letter-spacing:0; }}
h2 {{ font-family:"Optima","Songti SC",serif; font-size:26px; margin:0 0 14px; letter-spacing:0; }}
.sub {{ max-width:1040px; color:#38465b; font-size:16px; margin:0; }}
.kpis {{ display:grid; grid-template-columns:repeat(6,1fr); gap:12px; margin:16px 0; }}
.kpi {{ border:1px solid rgba(22,32,51,.10); background:rgba(255,255,255,.70); border-radius:8px; padding:15px; }}
.kpi .v {{ font-size:28px; font-weight:850; line-height:1; }}
.kpi .l {{ font-size:12px; color:var(--muted); margin-top:4px; }}
.panel {{ margin-top:16px; border:1px solid rgba(22,32,51,.11); background:rgba(255,253,247,.78); border-radius:14px; padding:20px; box-shadow:0 10px 28px rgba(22,32,51,.05); }}
.note {{ border-left:5px solid var(--teal); background:rgba(15,118,110,.08); border-radius:8px; padding:12px 14px; color:#314057; margin:12px 0; }}
.formula {{ display:grid; grid-template-columns:repeat(3,1fr); gap:12px; }}
.formula div {{ border:1px solid rgba(22,32,51,.10); background:rgba(255,255,255,.72); border-radius:8px; padding:13px; }}
code {{ font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace; font-size:12px; }}
.controls {{ display:grid; grid-template-columns:1fr 220px 220px; gap:10px; margin-bottom:12px; align-items:end; }}
label {{ display:block; color:var(--muted); font-size:12px; margin-bottom:5px; }}
input, select {{ width:100%; min-height:40px; border:1px solid rgba(22,32,51,.14); border-radius:8px; background:white; color:var(--ink); padding:8px 10px; }}
.table-wrap {{ max-height:690px; overflow:auto; border:1px solid rgba(22,32,51,.10); border-radius:10px; background:white; }}
table {{ width:100%; border-collapse:collapse; font-size:13px; }}
th, td {{ padding:9px 10px; border-bottom:1px solid rgba(22,32,51,.08); text-align:left; vertical-align:top; }}
th {{ position:sticky; top:0; z-index:1; background:#f2e5cf; font-size:12px; color:#29354a; }}
.num {{ text-align:right; font-variant-numeric:tabular-nums; }}
.barbox {{ height:7px; background:#e9dfcf; border-radius:999px; overflow:hidden; min-width:72px; margin-top:4px; }}
.bar {{ height:100%; background:linear-gradient(90deg,var(--blue),#00a6a6); }}
.tag {{ display:inline-block; padding:3px 8px; border-radius:999px; font-size:12px; font-weight:750; border:1px solid rgba(22,32,51,.10); background:#fff; white-space:nowrap; }}
.tag.hot {{ color:#8a2f12; background:#fff0df; }}
.tag.keep {{ color:#075e4f; background:#e7f6f2; }}
.tag.down {{ color:#606a78; background:#f3f4f6; }}
.grid2 {{ display:grid; grid-template-columns:1fr 1fr; gap:14px; }}
.mini-list {{ display:grid; gap:8px; }}
.mini {{ border:1px solid rgba(22,32,51,.10); background:white; border-radius:8px; padding:12px; }}
.mini b {{ display:block; margin-bottom:4px; }}
.small {{ color:var(--muted); font-size:12px; }}
.mono {{ font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace; }}
@media (max-width:980px) {{ .kpis {{ grid-template-columns:repeat(2,1fr); }} .formula,.controls,.grid2 {{ grid-template-columns:1fr; }} }}
</style>
</head>
<body>
<main>
  <section class="hero">
    <p class="eyebrow">Benchmark Portfolio Triage</p>
    <h1>哪些 benchmark 还值得继续做</h1>
    <p class="sub">判断标准分两层：一是它映射到的原子能力是否重要，二是当前模型是否还没解决好。基础答题门槛项不删除，但降为低频 gate；教育核心、覆盖洼地、仍有区分度的 benchmark 优先保留或补跑。</p>
  </section>

  <section class="kpis">
    <div class="kpi"><div class="v">{len(priority_rows)}</div><div class="l">benchmark / 细分维度</div></div>
    <div class="kpi"><div class="v">{buckets.get('优先继续做', 0)}</div><div class="l">优先继续做</div></div>
    <div class="kpi"><div class="v">{buckets.get('值得保留/补跑', 0)}</div><div class="l">值得保留/补跑</div></div>
    <div class="kpi"><div class="v">{buckets.get('诊断性保留', 0)}</div><div class="l">诊断性保留</div></div>
    <div class="kpi"><div class="v">{buckets.get('降为门槛项', 0)}</div><div class="l">降为门槛项</div></div>
    <div class="kpi"><div class="v">{buckets.get('先不看', 0) + buckets.get('不必重点看', 0)}</div><div class="l">先不重点看</div></div>
  </section>

  <section class="panel">
    <h2>计算口径</h2>
    <div class="formula">
      <div><b>重要性</b><br><code>I = 100 × benchmark_weight × Σ(P_priority × P_weight)</code><br><span class="small">R20 起无 tier 因子；P02/P08/P12/P14/P16/P19/P20 等覆盖洼地提高 P_priority。</span></div>
      <div><b>尚未解决程度</b><br><code>G = 0.6 × max(0,(9-best)/9) + 0.4 × max(0,(8-median)/8)</code><br><span class="small">best 看是否已有前沿模型能做，median 看是否仍能区分多数模型；无当前跑分按未知缺口处理。</span></div>
      <div><b>继续投入优先级</b><br><code>Priority = I × (0.58 × G + 0.32 × coverage_gap + 0.10)</code><br><span class="small">coverage_gap 来自模型覆盖不足和对应 P 能力覆盖稀缺；它只影响“是否该补测”，不折入模型能力分。</span></div>
    </div>
    <div class="note">这个报告不是说某个 benchmark 永久没用，而是给当前 rebenchmark 阶段排序：哪些要仔细看、哪些只做 gate、哪些先别投入分析时间。</div>
  </section>

  <section class="grid2">
    <div class="panel">
      <h2>最值得继续做</h2>
      <div class="mini-list" id="topList"></div>
    </div>
    <div class="panel">
      <h2>可降频或先不看</h2>
      <div class="mini-list" id="downList"></div>
    </div>
  </section>

  <section class="panel">
    <h2>完整排序表</h2>
    <div class="controls">
      <div>
        <label for="search">搜索 benchmark / P code / 理由</label>
        <input id="search" placeholder="例如 MathTutorBench、P11、安全、门槛">
      </div>
      <div>
        <label for="recFilter">建议档位</label>
        <select id="recFilter"><option value="ALL">全部</option></select>
      </div>
    </div>
    <div class="table-wrap">
      <table id="priorityTable">
        <thead><tr><th>建议</th><th>Benchmark</th><th>P 能力</th><th class="num">优先级</th><th class="num">重要性</th><th class="num">未解决</th><th class="num">覆盖缺口</th><th class="num">best / median</th><th class="num">模型数</th><th>判断理由</th></tr></thead>
        <tbody></tbody>
      </table>
    </div>
  </section>

  <footer class="small">数据源：<span class="mono">08_selected_score_evidence.jsonl</span>、<span class="mono">02_benchmark_ability_mapping.jsonl</span>、<span class="mono">09_atomic_p_scores.jsonl</span>。机器可读排序：<span class="mono">12_benchmark_priority_analysis.jsonl</span>。</footer>
</main>
<script id="priorityRows" type="application/json">{json_payload(priority_rows)}</script>
<script id="topRows" type="application/json">{json_payload(top_rows)}</script>
<script id="downRows" type="application/json">{json_payload(down_rows)}</script>
<script>
const rows = JSON.parse(document.getElementById('priorityRows').textContent);
const topRows = JSON.parse(document.getElementById('topRows').textContent);
const downRows = JSON.parse(document.getElementById('downRows').textContent);
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[c]));
const fmt = v => v == null ? '—' : Number(v).toFixed(2);
const pct = v => Math.max(0, Math.min(100, Number(v || 0)));
function tagClass(rec) {{
  if (rec === '优先继续做') return 'hot';
  if (rec === '值得保留/补跑' || rec === '诊断性保留') return 'keep';
  return 'down';
}}
function renderMini(target, data) {{
  document.getElementById(target).innerHTML = data.map(r => `<div class="mini">
    <b>${{esc(r.benchmark_name)}} <span class="small">${{esc(r.subdimension)}}</span></b>
    <span class="tag ${{tagClass(r.recommendation)}}">${{esc(r.recommendation)}}</span>
    <span class="small">优先级 ${{fmt(r.priority_score)}} / 重要性 ${{fmt(r.importance_score)}} / 未解决 ${{fmt(r.unsolved_index * 100)}}%</span>
    <div class="small">P：${{esc(r.p_weights.join(', '))}}</div>
    <div class="small">${{esc(r.rationale)}}</div>
  </div>`).join('');
}}
function initFilters() {{
  const recs = [...new Set(rows.map(r => r.recommendation))];
  document.getElementById('recFilter').innerHTML += recs.map(v => `<option value="${{esc(v)}}">${{esc(v)}}</option>`).join('');
  document.getElementById('search').addEventListener('input', renderTable);
  document.getElementById('recFilter').addEventListener('change', renderTable);
}}
function renderTable() {{
  const q = document.getElementById('search').value.trim().toLowerCase();
  const rec = document.getElementById('recFilter').value;
  const data = rows.filter(r => {{
    if (rec !== 'ALL' && r.recommendation !== rec) return false;
    if (!q) return true;
    return JSON.stringify([r.benchmark_name,r.benchmark_id,r.subdimension,r.p_codes,r.rationale,r.mapping_rationale]).toLowerCase().includes(q);
  }});
  document.querySelector('#priorityTable tbody').innerHTML = data.map(r => `<tr>
    <td><span class="tag ${{tagClass(r.recommendation)}}">${{esc(r.recommendation)}}</span><div class="small">${{esc(r.quadrant)}}</div></td>
    <td><b>${{esc(r.benchmark_name)}}</b><div class="mono small">${{esc(r.benchmark_id)}}</div><div class="small">${{esc(r.subdimension)}}</div></td>
    <td>${{esc(r.p_weights.join(', '))}}<div class="small">${{esc(r.groups.join(', '))}}</div></td>
    <td class="num"><b>${{fmt(r.priority_score)}}</b><div class="barbox"><div class="bar" style="width:${{pct(r.priority_score)}}%"></div></div></td>
    <td class="num">${{fmt(r.importance_score)}}<div class="barbox"><div class="bar" style="width:${{pct(r.importance_score)}}%"></div></div></td>
    <td class="num">${{fmt(r.unsolved_index * 100)}}%</td>
    <td class="num">${{fmt(r.coverage_gap * 100)}}%</td>
    <td class="num">${{fmt(r.best_score_10)}} / ${{fmt(r.median_score_10)}}<div class="small">${{esc(r.score_status)}}</div></td>
    <td class="num">${{r.model_count}}<div class="small">${{r.score_row_count}} rows</div></td>
    <td>${{esc(r.rationale)}}<div class="small">${{esc(r.mapping_rationale)}}</div></td>
  </tr>`).join('');
}}
renderMini('topList', topRows);
renderMini('downList', downRows);
initFilters();
renderTable();
</script>
</body>
</html>
"""
    (OUT / "12_benchmark_priority_report.html").write_text(html_text, encoding="utf-8")


def simple_portfolio_recommendation(row: dict[str, Any]) -> str:
    avg = row["all_model_average_score_10"]
    relevance = row["importance_score"]
    if row.get("excluded"):
        return "先排除"
    if avg is None:
        return "高相关但缺跑分" if relevance >= 45 else "暂不判断"
    if relevance >= 55 and avg < 6.5:
        return "优先继续做"
    if relevance >= 55 and avg < 7.5:
        return "值得继续做"
    if relevance >= 55:
        return "重要但可降频"
    if avg < 6.5:
        return "诊断保留"
    return "不必重点看"


def write_benchmark_portfolio_markdown(priority_rows: list[dict[str, Any]]) -> None:
    def fmt(value: Any) -> str:
        return "NA" if value is None else f"{float(value):.2f}"

    rows = sorted(priority_rows, key=lambda r: (r["benchmark_id"], r["subdimension"]))
    ranked = sorted(
        rows,
        key=lambda r: (
            simple_portfolio_recommendation(r) not in {"优先继续做", "值得继续做", "高相关但缺跑分"},
            -(r["importance_score"] or 0),
            r["all_model_average_score_10"] if r["all_model_average_score_10"] is not None else 99,
            r["benchmark_id"],
        ),
    )

    benchmark_groups: dict[str, dict[str, Any]] = {}
    for row in rows:
        slot = benchmark_groups.setdefault(
            row["benchmark_id"],
            {
                "benchmark_name": row["benchmark_name"],
                "scores": [],
                "relevance": [],
                "subdimensions": 0,
                "p_codes": set(),
                "recommendations": [],
            },
        )
        slot["subdimensions"] += 1
        if row["all_model_average_score_10"] is not None:
            slot["scores"].append(row["all_model_average_score_10"])
        slot["relevance"].append(row["importance_score"])
        slot["p_codes"].update(row["p_codes"])
        slot["recommendations"].append(simple_portfolio_recommendation(row))

    group_rows = []
    for benchmark_id, slot in benchmark_groups.items():
        avg_score = statistics.mean(slot["scores"]) if slot["scores"] else None
        avg_relevance = statistics.mean(slot["relevance"]) if slot["relevance"] else None
        rec_counts = {rec: slot["recommendations"].count(rec) for rec in set(slot["recommendations"])}
        preferred_rec = sorted(rec_counts.items(), key=lambda item: (-item[1], item[0]))[0][0]
        group_rows.append(
            {
                "benchmark_id": benchmark_id,
                "benchmark_name": slot["benchmark_name"],
                "avg_score": avg_score,
                "avg_relevance": avg_relevance,
                "subdimensions": slot["subdimensions"],
                "p_codes": sorted(slot["p_codes"]),
                "recommendation": preferred_rec,
            }
        )
    group_rows.sort(
        key=lambda r: (
            r["recommendation"] not in {"优先继续做", "值得继续做", "高相关但缺跑分"},
            -(r["avg_relevance"] or 0),
            r["avg_score"] if r["avg_score"] is not None else 99,
            r["benchmark_id"],
        )
    )

    lines = [
        "# Benchmark Portfolio Review",
        "",
        "目的：先用两个直观指标判断当前 benchmark 是否还值得继续重点做。",
        "",
        "## 两个主指标",
        "",
        "1. **所有模型平均分**：对进入最终计算的 canonical score rows，在同一个 benchmark/subdimension 下跨模型取 `score_10` 平均。分数越高，说明当前模型整体越接近解决；分数越低，越有继续区分模型的价值。`NA` 表示该 mapping 目前没有进入最终计分的模型结果。",
        "2. **原子能力有效相关性**：只由 mapping 决定，不看模型表现。公式（R20，无 tier 因子）：`100 × benchmark_weight × Σ(P_priority × ability_weight)`。",
        "",
        "辅助列：`P 相关性` 是不乘 benchmark 置信权重的纯 P 能力相关性。",
        "",
        "## 先看结论排序",
        "",
        "| 建议 | Benchmark | Subdimension | 所有模型平均分 | 原子能力有效相关性 | P 相关性 | 模型数 | P 映射 |",
        "|---|---|---|---:|---:|---:|---:|---|",
    ]
    for row in ranked:
        lines.append(
            f"| {simple_portfolio_recommendation(row)} | `{row['benchmark_id']}` {row['benchmark_name']} | {row['subdimension']} | {fmt(row['all_model_average_score_10'])} | {fmt(row['importance_score'])} | {fmt(row['p_relevance_score'])} | {row['model_count']} | {', '.join(row['p_weights'])} |"
        )

    lines.extend(
        [
            "",
            "## 按 benchmark 聚合",
            "",
            "聚合口径：同一 benchmark 的多个 subdimension 先各自计算平均分和相关性，再在 benchmark 内做简单平均；只用于概览，具体判断仍看上面的 subdimension 明细。",
            "",
            "| 建议 | Benchmark | Subdimension 数 | benchmark 平均分 | 平均原子相关性 | P 覆盖 |",
            "|---|---|---:|---:|---:|---|",
        ]
    )
    for row in group_rows:
        lines.append(
            f"| {row['recommendation']} | `{row['benchmark_id']}` {row['benchmark_name']} | {row['subdimensions']} | {fmt(row['avg_score'])} | {fmt(row['avg_relevance'])} | {', '.join(row['p_codes'])} |"
        )

    lines.extend(
        [
            "",
            "## 校准提示",
            "",
            "- `所有模型平均分` 高但 `原子能力有效相关性` 低：通常不需要重点看，适合做门槛或背景参考。",
            "- `所有模型平均分` 低且 `原子能力有效相关性` 高：优先继续做，因为它既重要又还没被解决好。",
            "- `NA` 且相关性高：说明 mapping 认为它重要，但当前主计分层缺结果，应该优先补跑或确认数据源。",
            "- foundation gate 不等于没用，只是不应主导教育能力判断；它更适合筛掉基础能力不足的模型。",
        ]
    )
    (OUT / "12_benchmark_portfolio_review.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_open_questions() -> None:
    text = """# Open Calibration Questions

Resolved in this pass:

- R20: the four-level evidence-tier system is removed; scoring weight = relevance × confidence only.
- R25: both weights become rule-derived — relevance in five tiers (1.0/0.8/0.5/0.2/0), confidence from two factors (objective vs LLM-judge scoring; externally vetted vs self-built data), giving 1.0/0.85/0.7 plus one documented exception.
- R20: P codes renumbered to the doc scheme `P01-P20` (no tombstones).
- EduGuard P2 uses `deepseek-v3.2` judge as primary.
- R23: BEA/MRBench judge tasks are scored on the subjective-scoring P (its construct IS judging ability); `EXCLUDED_SCORING_BENCHMARKS` is now empty and exclusion is carried by per-cell `excluded` markers.
- EduIllustrate full-230 runs are included; 5-item runs are excluded.
- MiniMax-M3 canonical policy prefers included `minimax3/` or fuller-scored runs.

Remaining review points:

1. `P08` (tool use / long-horizon) and `P20` (academic integrity) are declared domain gaps (report them honestly as uncovered); `P16`/`P14` are single-source reference values and `P12` covers 2 of 4 declared sub-abilities.
2. `P17-P19` are covered mainly by EduGuard safety evidence. Confirm whether that is sufficient, or whether to require student-risk-specific datasets.
3. For cross-model comparison, decide whether to add a strict `common-evidence` mode that only compares models on shared benchmark/subdimension coverage.
"""
    (OUT / "06_open_calibration_questions.md").write_text(text, encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    eval_rows = inventory_eval_runs()
    other_rows = inventory_otherbenchmark_scores()
    score_candidates = build_repo_score_candidates(eval_rows) + build_other_score_candidates(other_rows)
    selected_score_rows, duplicate_rows = dedupe_score_candidates(score_candidates)
    minimax_rows = minimax_conflict_report(eval_rows)
    evidence_rows, p_rows, group_rows, untested_rows = score_atomic_p(selected_score_rows)
    write_readme()
    write_inclusion_policy()
    write_mapping_files()
    write_normalization()
    write_inventory(eval_rows)
    write_otherbenchmark_scores(other_rows)
    write_deduplication_report(duplicate_rows, minimax_rows)
    write_score_evidence(selected_score_rows)
    write_atomic_scores(p_rows, evidence_rows, untested_rows)
    write_group_scores(group_rows)
    priority_rows = analyze_benchmark_priorities(selected_score_rows, p_rows)
    write_final_html(
        eval_rows=eval_rows,
        other_rows=other_rows,
        selected_score_rows=selected_score_rows,
        evidence_rows=evidence_rows,
        p_rows=p_rows,
        group_rows=group_rows,
        duplicate_rows=duplicate_rows,
        minimax_rows=minimax_rows,
    )
    write_benchmark_priority_report(priority_rows)
    write_benchmark_portfolio_markdown(priority_rows)
    write_open_questions()
    print(f"wrote artifacts to {OUT}")
    print(f"mapping rows: {len(MAPPINGS)}")
    print(f"eval summaries: {len(eval_rows)}")
    print(f"include candidates: {sum(1 for r in eval_rows if r['main_inclusion'] == 'include_candidate')}")
    print(f"otherbenchmark score rows: {len(other_rows)}")
    print(f"score candidates: {len(score_candidates)}")
    print(f"selected score rows: {len(selected_score_rows)}")
    print(f"p score rows: {len(p_rows)}")
    print(f"  of which 未测过 (score_10=null): {sum(1 for r in p_rows if r['score_10'] is None)}")
    print(f"capability-gap zero cells: {sum(1 for r in evidence_rows if r.get('source_type') == 'capability_gap_zero')}")
    print(f"untested cells: {len(untested_rows)}")
    print("html: 11_atomic_ability_rebenchmark_report.html")
    print("priority html: 12_benchmark_priority_report.html")


if __name__ == "__main__":
    main()
