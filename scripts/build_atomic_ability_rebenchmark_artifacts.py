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
OUT = ROOT / "reports" / "atomic_ability_rebenchmark_2026-07-08"
EVAL_DIR = ROOT / "reports" / "eval"
OTHER_DIR = ROOT / "otherbenchmark"

EDUGUARD_P2_PRIMARY_JUDGE = "deepseek-v3.2 judge"
EXCLUDED_SCORING_BENCHMARKS = {"bea2025_judge", "mrbench_judge"}
FOUNDATION_GATE_FACTOR = 0.45

ABILITY_PRIORITY = {
    "P01": 0.45,
    "P02": 0.65,
    "P03": 0.70,
    "P04": 0.90,
    "P05": 0.55,
    "P06": 0.65,
    "P07": 0.75,
    "P08": 0.95,
    "P09": 0.95,
    "P10": 0.90,
    "P11": 0.85,
    "P12": 0.90,
    "P13": 0.95,
    "P14": 0.90,
    "P15": 0.95,
    "P16": 0.90,
    "P17": 0.95,
    "P18": 0.95,
    "P19": 0.95,
    "P20": 0.90,
    "P21": 0.95,
    "P22": 1.00,
}

TIER_IMPORTANCE_FACTOR = {
    "education_core": 1.00,
    "diagnostic": 0.75,
    "foundation_gate": 0.45,
    "excluded_judge_task": 0.08,
}

P_GAP_BONUS = {"P04", "P08", "P09", "P10", "P15", "P16", "P19", "P22"}


P_GROUPS = {
    "P01": ("SRG", "指令与约束遵循"),
    "P02": ("SRG", "长上下文与证据定位"),
    "P03": ("SRG", "常规多模态感知"),
    "P04": ("SRG", "复杂多模态理解"),
    "P05": ("FDR", "知识调用与掌握"),
    "P06": ("FDR", "推理与生成"),
    "P07": ("FDR", "自我校验与修正"),
    "P08": ("FDR", "置信度校准与弃答"),
    "P09": ("FDR", "工具使用与长程智能体执行"),
    "P10": ("FDR", "多模态教学产物生成"),
    "P11": ("LAD", "作答正误判定"),
    "P12": ("LAD", "错误位置定位"),
    "P13": ("LAD", "错因归因"),
    "P14": ("LAD", "Rubric 映射评分"),
    "P15": ("LAD", "学术诚信与作答真实性判定"),
    "P16": ("CLM", "学习者画像建模"),
    "P17": ("CLM", "个性化教学策略选择"),
    "P18": ("CLM", "适配性解释与反馈生成"),
    "P19": ("CLM", "学习路径规划"),
    "P20": ("CEG", "教育角色边界判断"),
    "P21": ("CEG", "学生风险识别"),
    "P22": ("CEG", "安全处置选择"),
}


def ability_weights(*items: tuple[str, float]) -> list[dict[str, Any]]:
    total = round(sum(w for _, w in items), 6)
    if abs(total - 1.0) > 1e-6:
        raise ValueError(f"ability weights must sum to 1, got {total}: {items}")
    rows = []
    for code, weight in items:
        group, name = P_GROUPS[code]
        rows.append({"p_code": code, "p_name": name, "group": group, "weight": weight})
    return rows


MAPPINGS: list[dict[str, Any]] = [
    {
        "benchmark_id": "mmlu_pro",
        "benchmark_name": "MMLU-Pro",
        "subdimension": "overall/category accuracy",
        "evidence_tier": "foundation_gate",
        "source_scope": "repo_eval",
        "metric_family": "accuracy",
        "score_direction": "higher_better",
        "default_benchmark_weight": 0.35,
        "abilities": ability_weights(("P05", 0.60), ("P06", 0.30), ("P01", 0.10)),
        "rationale": "基础学科知识与选择题答题能力，主要验证 LLM 答题门槛，不应主导教育能力雷达图。",
    },
    {
        "benchmark_id": "ceval",
        "benchmark_name": "C-EVAL",
        "subdimension": "overall/category/subject accuracy",
        "evidence_tier": "foundation_gate",
        "source_scope": "repo_eval",
        "metric_family": "accuracy",
        "score_direction": "higher_better",
        "default_benchmark_weight": 0.35,
        "abilities": ability_weights(("P05", 0.60), ("P06", 0.25), ("P01", 0.15)),
        "rationale": "中文考试与学科知识，属于基础答题门槛；对应知识调用、推理和选项约束遵循。",
    },
    {
        "benchmark_id": "agieval",
        "benchmark_name": "AGIEval",
        "subdimension": "overall/task/language/question_type accuracy",
        "evidence_tier": "foundation_gate",
        "source_scope": "repo_eval",
        "metric_family": "accuracy",
        "score_direction": "higher_better",
        "default_benchmark_weight": 0.40,
        "abilities": ability_weights(("P06", 0.45), ("P05", 0.35), ("P01", 0.20)),
        "rationale": "标准化考试推理与答题，仍是 LLM 答题能力门槛；更偏 P06。",
    },
    {
        "benchmark_id": "olympiadbench",
        "benchmark_name": "OlympiadBench",
        "subdimension": "overall/subject/language/modality accuracy",
        "evidence_tier": "foundation_gate",
        "source_scope": "repo_eval",
        "metric_family": "accuracy",
        "score_direction": "higher_better",
        "default_benchmark_weight": 0.55,
        "abilities": ability_weights(("P06", 0.55), ("P05", 0.25), ("P03", 0.20)),
        "rationale": "高难学科推理和多模态竞赛题，答题能力未完全饱和；仍作为门槛/诊断而非教育核心。",
    },
    {
        "benchmark_id": "mathvista",
        "benchmark_name": "MathVista",
        "subdimension": "task/question_type/answer_type accuracy",
        "evidence_tier": "diagnostic",
        "source_scope": "repo_eval",
        "metric_family": "accuracy",
        "score_direction": "higher_better",
        "default_benchmark_weight": 0.70,
        "abilities": ability_weights(("P03", 0.35), ("P06", 0.45), ("P05", 0.20)),
        "rationale": "静态图文数学题，主要测常规多模态感知、数学推理和知识调用。",
    },
    {
        "benchmark_id": "pedagogy_benchmark",
        "benchmark_name": "Pedagogy Benchmark",
        "subdimension": "CDPK teaching knowledge selection",
        "evidence_tier": "education_core",
        "source_scope": "otherbenchmark",
        "metric_family": "accuracy",
        "score_direction": "higher_better",
        "default_benchmark_weight": 0.80,
        "abilities": ability_weights(("P05", 0.45), ("P17", 0.35), ("P06", 0.20)),
        "rationale": "教学法知识选择题，既有教育知识，也有教学策略选择和形式推理。",
    },
    {
        "benchmark_id": "pedagogy_benchmark",
        "benchmark_name": "Pedagogy Benchmark",
        "subdimension": "SEND special education needs selection",
        "evidence_tier": "education_core",
        "source_scope": "otherbenchmark",
        "metric_family": "accuracy",
        "score_direction": "higher_better",
        "default_benchmark_weight": 0.80,
        "abilities": ability_weights(("P05", 0.35), ("P16", 0.35), ("P17", 0.30)),
        "rationale": "特殊教育需求判断更依赖学习者画像和干预策略选择。",
    },
    {
        "benchmark_id": "pedagogy_benchmark",
        "benchmark_name": "Pedagogy Benchmark",
        "subdimension": "CDPK/SEND aggregate from 0701 card",
        "evidence_tier": "education_core",
        "source_scope": "otherbenchmark",
        "metric_family": "accuracy_percent",
        "score_direction": "higher_better",
        "default_benchmark_weight": 0.80,
        "abilities": ability_weights(("P05", 0.40), ("P17", 0.30), ("P16", 0.30)),
        "rationale": "0701 只有 Pedagogy 聚合卡片时使用，合并教学法知识、特殊教育需求画像和策略选择。",
    },
    {
        "benchmark_id": "asap_2",
        "benchmark_name": "ASAP 2.0",
        "subdimension": "essay holistic QWK",
        "evidence_tier": "education_core",
        "source_scope": "otherbenchmark",
        "metric_family": "qwk_0_to_100",
        "score_direction": "higher_better",
        "default_benchmark_weight": 0.80,
        "abilities": ability_weights(("P14", 0.65), ("P02", 0.20), ("P05", 0.15)),
        "rationale": "作文评分一致性主要是 rubric 映射评分，同时需要定位文本证据与写作知识。",
    },
    {
        "benchmark_id": "sas_bench",
        "benchmark_name": "SAS-Bench",
        "subdimension": "QWK holistic total score",
        "evidence_tier": "education_core",
        "source_scope": "otherbenchmark",
        "metric_family": "score_0_to_100",
        "score_direction": "higher_better",
        "default_benchmark_weight": 0.90,
        "abilities": ability_weights(("P14", 0.70), ("P02", 0.15), ("P05", 0.15)),
        "rationale": "总分评分一致性主测 rubric 映射评分。",
    },
    {
        "benchmark_id": "sas_bench",
        "benchmark_name": "SAS-Bench",
        "subdimension": "CCS step scoring consistency",
        "evidence_tier": "education_core",
        "source_scope": "otherbenchmark",
        "metric_family": "score_0_to_100",
        "score_direction": "higher_better",
        "default_benchmark_weight": 0.95,
        "abilities": ability_weights(("P14", 0.55), ("P12", 0.25), ("P02", 0.20)),
        "rationale": "分步踩分同时涉及 rubric 映射、错误位置/步骤定位和证据定位。",
    },
    {
        "benchmark_id": "sas_bench",
        "benchmark_name": "SAS-Bench",
        "subdimension": "ECS error-cause consistency",
        "evidence_tier": "education_core",
        "source_scope": "otherbenchmark",
        "metric_family": "score_0_to_100",
        "score_direction": "higher_better",
        "default_benchmark_weight": 1.00,
        "abilities": ability_weights(("P13", 0.70), ("P05", 0.20), ("P06", 0.10)),
        "rationale": "错因诊断准确度主测错因归因。",
    },
    {
        "benchmark_id": "edubench",
        "benchmark_name": "EduBench",
        "subdimension": "IP idea provision / heuristic answer",
        "evidence_tier": "education_core",
        "source_scope": "otherbenchmark",
        "metric_family": "likert_0_to_10",
        "score_direction": "higher_better",
        "default_benchmark_weight": 0.80,
        "abilities": ability_weights(("P17", 0.40), ("P18", 0.35), ("P05", 0.25)),
        "rationale": "启发式解答主要是教学策略选择与适配性解释。",
    },
    {
        "benchmark_id": "edubench",
        "benchmark_name": "EduBench",
        "subdimension": "PCC pedagogical/personalized content creation",
        "evidence_tier": "education_core",
        "source_scope": "otherbenchmark",
        "metric_family": "likert_0_to_10",
        "score_direction": "higher_better",
        "default_benchmark_weight": 0.80,
        "abilities": ability_weights(("P18", 0.45), ("P17", 0.30), ("P05", 0.25)),
        "rationale": "教育内容生成以反馈解释和策略适配为主，当前多为纯文本，不直接等同 P10。",
    },
    {
        "benchmark_id": "edubench",
        "benchmark_name": "EduBench",
        "subdimension": "PLS personalized learning support",
        "evidence_tier": "education_core",
        "source_scope": "otherbenchmark",
        "metric_family": "likert_0_to_10",
        "score_direction": "higher_better",
        "default_benchmark_weight": 0.85,
        "abilities": ability_weights(("P16", 0.30), ("P17", 0.45), ("P18", 0.25)),
        "rationale": "个性化学习支持以学习者画像、干预策略和适配反馈为主。",
    },
    {
        "benchmark_id": "edubench",
        "benchmark_name": "EduBench",
        "subdimension": "QG question generation",
        "evidence_tier": "education_core",
        "source_scope": "otherbenchmark",
        "metric_family": "likert_0_to_10",
        "score_direction": "higher_better",
        "default_benchmark_weight": 0.75,
        "abilities": ability_weights(("P18", 0.35), ("P06", 0.35), ("P05", 0.30)),
        "rationale": "题目生成是教育约束下的推理生成和适配解释，不是非文本多模态产物。",
    },
    {
        "benchmark_id": "edubench",
        "benchmark_name": "EduBench",
        "subdimension": "TMG teaching material generation",
        "evidence_tier": "education_core",
        "source_scope": "otherbenchmark",
        "metric_family": "likert_0_to_10",
        "score_direction": "higher_better",
        "default_benchmark_weight": 0.75,
        "abilities": ability_weights(("P18", 0.40), ("P05", 0.35), ("P06", 0.25)),
        "rationale": "教学材料生成主要看教育解释、领域知识和生成推理；若包含图示再另映射 P10。",
    },
    {
        "benchmark_id": "tutorbench",
        "benchmark_name": "TutorBench",
        "subdimension": "Fair815 multimodal tutor quality",
        "evidence_tier": "education_core",
        "source_scope": "otherbenchmark",
        "metric_family": "score_0_to_100",
        "score_direction": "higher_better",
        "default_benchmark_weight": 1.00,
        "abilities": ability_weights(("P18", 0.40), ("P17", 0.35), ("P03", 0.25)),
        "rationale": "真实多模态 tutor 质量综合考察反馈生成、策略选择和图文感知。",
    },
    {
        "benchmark_id": "mathtutorbench_problem_solving",
        "benchmark_name": "MathTutorBench",
        "subdimension": "Problem Solving",
        "evidence_tier": "foundation_gate",
        "source_scope": "repo_eval",
        "metric_family": "accuracy",
        "score_direction": "higher_better",
        "default_benchmark_weight": 0.45,
        "abilities": ability_weights(("P06", 0.60), ("P05", 0.30), ("P07", 0.10)),
        "rationale": "数学求解门槛，重要但不能证明会辅导。",
    },
    {
        "benchmark_id": "mathtutorbench_solution_correctness",
        "benchmark_name": "MathTutorBench",
        "subdimension": "Solution Correctness",
        "evidence_tier": "education_core",
        "source_scope": "repo_eval",
        "metric_family": "accuracy_or_f1",
        "score_direction": "higher_better",
        "default_benchmark_weight": 0.85,
        "abilities": ability_weights(("P11", 0.60), ("P07", 0.25), ("P02", 0.15)),
        "rationale": "给定参考/学生解判断正确性，主测作答正误判定。",
    },
    {
        "benchmark_id": "mathtutorbench_mistake_location",
        "benchmark_name": "MathTutorBench",
        "subdimension": "Mistake Location",
        "evidence_tier": "education_core",
        "source_scope": "repo_eval",
        "metric_family": "accuracy_or_f1",
        "score_direction": "higher_better",
        "default_benchmark_weight": 1.00,
        "abilities": ability_weights(("P12", 0.70), ("P02", 0.20), ("P11", 0.10)),
        "rationale": "错误位置定位是 P12 的直接测量。",
    },
    {
        "benchmark_id": "mathtutorbench_mistake_correction",
        "benchmark_name": "MathTutorBench",
        "subdimension": "Mistake Correction",
        "evidence_tier": "education_core",
        "source_scope": "repo_eval",
        "metric_family": "accuracy",
        "score_direction": "higher_better",
        "default_benchmark_weight": 0.90,
        "abilities": ability_weights(("P13", 0.45), ("P18", 0.35), ("P06", 0.20)),
        "rationale": "纠错需要识别错因并生成可用修正/反馈。",
    },
    {
        "benchmark_id": "mathtutorbench_pedagogy",
        "benchmark_name": "MathTutorBench",
        "subdimension": "Pedagogy IF",
        "evidence_tier": "education_core",
        "source_scope": "repo_eval",
        "metric_family": "win_rate_or_accuracy",
        "score_direction": "higher_better",
        "default_benchmark_weight": 0.95,
        "abilities": ability_weights(("P17", 0.45), ("P18", 0.30), ("P05", 0.25)),
        "rationale": "教学法指令遵循主测策略选择和适配反馈。",
    },
    {
        "benchmark_id": "mathtutorbench_pedagogy_hard",
        "benchmark_name": "MathTutorBench",
        "subdimension": "Pedagogy IF hard",
        "evidence_tier": "education_core",
        "source_scope": "repo_eval",
        "metric_family": "win_rate_or_accuracy",
        "score_direction": "higher_better",
        "default_benchmark_weight": 1.00,
        "abilities": ability_weights(("P17", 0.45), ("P18", 0.30), ("P05", 0.25)),
        "rationale": "hard 子集较有区分度，权重略高。",
    },
    {
        "benchmark_id": "mathtutorbench_scaffolding",
        "benchmark_name": "MathTutorBench",
        "subdimension": "Scaffolding",
        "evidence_tier": "education_core",
        "source_scope": "repo_eval",
        "metric_family": "win_rate_or_accuracy",
        "score_direction": "higher_better",
        "default_benchmark_weight": 1.00,
        "abilities": ability_weights(("P17", 0.50), ("P18", 0.35), ("P05", 0.15)),
        "rationale": "脚手架主测下一步教学干预选择与反馈生成。",
    },
    {
        "benchmark_id": "mathtutorbench_scaffolding_hard",
        "benchmark_name": "MathTutorBench",
        "subdimension": "Scaffolding hard",
        "evidence_tier": "education_core",
        "source_scope": "repo_eval",
        "metric_family": "win_rate_or_accuracy",
        "score_direction": "higher_better",
        "default_benchmark_weight": 1.00,
        "abilities": ability_weights(("P17", 0.50), ("P18", 0.35), ("P05", 0.15)),
        "rationale": "hard 子集仍主测教学干预与反馈。",
    },
    {
        "benchmark_id": "mathtutorbench_socratic",
        "benchmark_name": "MathTutorBench",
        "subdimension": "Socratic Questioning",
        "evidence_tier": "education_core",
        "source_scope": "repo_eval",
        "metric_family": "bleu_0_to_1",
        "score_direction": "higher_better",
        "default_benchmark_weight": 0.60,
        "abilities": ability_weights(("P17", 0.65), ("P18", 0.35)),
        "rationale": "生成引导性提问、与教师金标问题比 BLEU，是 P17a（提问式干预）的测量来源"
        "（R11 补挂，2026-07-12；按拆分准入规则提问不单列子能力）。BLEU 对合理的不同问法会误罚，权重保守。",
    },
    {
        "benchmark_id": "bea2025_judge",
        "benchmark_name": "BEA 2025 Judge",
        "subdimension": "judge labels: mistake/guidance/actionability",
        "evidence_tier": "excluded_judge_task",
        "source_scope": "repo_eval",
        "metric_family": "accuracy",
        "score_direction": "higher_better",
        "default_benchmark_weight": 0.00,
        "abilities": ability_weights(("P14", 0.45), ("P13", 0.30), ("P11", 0.25)),
        "rationale": "作为教育评判者可映射到 rubric/错因/正误判断，但本轮按用户口径先排除 judge task，不进入 P-score。",
    },
    {
        "benchmark_id": "bea2025_tutor",
        "benchmark_name": "BEA 2025 Tutor",
        "subdimension": "pedagogical pass rate",
        "evidence_tier": "education_core",
        "source_scope": "repo_eval",
        "metric_family": "pass_rate",
        "score_direction": "higher_better",
        "default_benchmark_weight": 0.90,
        "abilities": ability_weights(("P18", 0.45), ("P17", 0.30), ("P13", 0.25)),
        "rationale": "生成 tutor 回复，强调可行动指导、反馈生成和错因识别。",
    },
    {
        "benchmark_id": "mrbench_judge",
        "benchmark_name": "MRBench Judge",
        "subdimension": "8-dimension tutor response judging",
        "evidence_tier": "excluded_judge_task",
        "source_scope": "repo_eval",
        "metric_family": "accuracy",
        "score_direction": "higher_better",
        "default_benchmark_weight": 0.00,
        "abilities": ability_weights(("P14", 0.45), ("P13", 0.25), ("P20", 0.30)),
        "rationale": "多维 tutor 回复评判可映射到评分/错因/边界，但本轮按用户口径先排除 judge task，不进入 P-score。",
    },
    {
        "benchmark_id": "mrbench_tutor",
        "benchmark_name": "MRBench Tutor",
        "subdimension": "8-dimension tutor pass rate",
        "evidence_tier": "education_core",
        "source_scope": "repo_eval",
        "metric_family": "pass_rate",
        "score_direction": "higher_better",
        "default_benchmark_weight": 0.80,
        "abilities": ability_weights(("P18", 0.45), ("P17", 0.30), ("P20", 0.25)),
        "rationale": "tutor 回复生成同时考查指导、反馈和不泄题/角色边界。",
    },
    {
        "benchmark_id": "eduguard_sata",
        "benchmark_name": "EduGuard-Bench P1",
        "subdimension": "Teaching Harm / SATA RFS",
        "evidence_tier": "education_core",
        "source_scope": "repo_eval_and_otherbenchmark",
        "metric_family": "rfs_0_to_1",
        "score_direction": "higher_better",
        "default_benchmark_weight": 1.00,
        "abilities": ability_weights(("P20", 0.35), ("P21", 0.30), ("P22", 0.35)),
        "rationale": "教学伤害全选题同时测试角色边界、风险识别和处置选择。",
    },
    {
        "benchmark_id": "eduguard_adversarial",
        "benchmark_name": "EduGuard-Bench P2",
        "subdimension": "Adversarial Safety ASR",
        "evidence_tier": "education_core",
        "source_scope": "repo_eval_and_otherbenchmark",
        "metric_family": "asr_0_to_1_lower_better",
        "score_direction": "lower_better",
        "default_benchmark_weight": 1.00,
        "abilities": ability_weights(("P22", 0.45), ("P20", 0.30), ("P21", 0.25)),
        "rationale": "对抗安全主要测安全处置，同时需要识别风险和维持教育角色边界。",
    },
    {
        "benchmark_id": "eduguard_adversarial",
        "benchmark_name": "EduGuard-Bench P2",
        "subdimension": "Refusal quality distribution",
        "evidence_tier": "diagnostic",
        "source_scope": "repo_eval_and_otherbenchmark",
        "metric_family": "share_0_to_1",
        "score_direction": "higher_better",
        "default_benchmark_weight": 0.70,
        "abilities": ability_weights(("P22", 0.60), ("P18", 0.25), ("P20", 0.15)),
        "rationale": "教育型拒答是处置选择和教育性重定向质量。",
    },
    {
        "benchmark_id": "eduillustrate",
        "benchmark_name": "EduIllustrate",
        "subdimension": "8-dim 0-5 visual explanation score",
        "evidence_tier": "diagnostic",
        "source_scope": "repo_eval",
        "metric_family": "likert_0_to_5",
        "score_direction": "higher_better",
        "default_benchmark_weight": 0.85,
        "abilities": ability_weights(("P10", 0.45), ("P03", 0.25), ("P18", 0.30)),
        "rationale": "教学图示/图文协同生成直接测多模态教学产物生成。",
    },
    {
        "benchmark_id": "mmtutorbench",
        "benchmark_name": "MMTutorBench",
        "subdimension": "multimodal tutor score",
        "evidence_tier": "diagnostic",
        "source_scope": "repo_eval",
        "metric_family": "score_0_to_6",
        "score_direction": "higher_better",
        "default_benchmark_weight": 0.90,
        "abilities": ability_weights(("P03", 0.30), ("P18", 0.40), ("P17", 0.30)),
        "rationale": "多模态 tutor 综合测图文感知、反馈生成和策略选择；当前小样本默认排除主图。",
    },
    {
        "benchmark_id": "p07_selfcheck",
        "benchmark_name": "P07 两轮自查",
        "subdimension": "two-round self-check (fix/break rate)",
        "evidence_tier": "diagnostic",
        "source_scope": "repo_eval",
        "metric_family": "composite_0_to_10",
        "score_direction": "higher_better",
        "default_benchmark_weight": 0.85,
        "abilities": ability_weights(("P07", 0.85), ("P08", 0.15)),
        "rationale": (
            "两轮自查协议（先答题、再无提示复查），P07 的首个直接测量（2026-07-12 缺口填补）；"
            "headline=0.5×改对率+0.5×(1−改错率)，与第一轮正确率解耦。复查时对自身答案的把握"
            "与校准相通，P08 占 0.15。"
        ),
    },
    {
        "benchmark_id": "p08_calibration",
        "benchmark_name": "P08 置信度校准",
        "subdimension": "calibration composite (CWR/AUROC)",
        "evidence_tier": "diagnostic",
        "source_scope": "repo_eval",
        "metric_family": "composite_0_to_10",
        "score_direction": "higher_better",
        "default_benchmark_weight": 0.85,
        "abilities": ability_weights(("P08", 0.80), ("P07", 0.20)),
        "rationale": (
            "复用 exact-match benchmark + verbalized confidence，测“自信地教错”"
            "（CWR）与“知道自己不知道”（AUROC）；自报置信度带少量自检成分故 P07 占 0.20。"
        ),
    },
    {
        "benchmark_id": "p08_abstention",
        "benchmark_name": "P08 能力性弃答",
        "subdimension": "balanced abstention score",
        "evidence_tier": "diagnostic",
        "source_scope": "repo_eval",
        "metric_family": "composite_0_to_10",
        "score_direction": "higher_better",
        "default_benchmark_weight": 0.85,
        "abilities": ability_weights(("P08", 0.85), ("P01", 0.15)),
        "rationale": (
            "公开弃答数据集（UMWP/TreeCut）测对不可答题能否说“不会”；识别并按格式声明"
            "带少量指令遵循成分故 P01 占 0.15。与 p08_calibration 共同构成 P08 两半证据。"
        ),
    },
]


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
        ("Pedagogy Accuracy", "pedagogy_benchmark", "Pedagogy Benchmark", "CDPK/SEND aggregate from 0701 card", "accuracy_percent", "scoring_candidate"),
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
    }
    return aliases.get(key, key)


def normalize_score(metric: str, value: float) -> float | None:
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
    if metric is not None:
        for row in candidates:
            if row["metric_family"] == metric:
                return row
        if metric == "accuracy" and candidates:
            for row in candidates:
                if row["metric_family"] in {"accuracy", "accuracy_or_f1", "win_rate_or_accuracy"}:
                    return row
    return candidates[0] if candidates else None


def extract_primary_metric(summary: dict[str, Any]) -> tuple[str, float | None]:
    extra = summary.get("extra_metrics") or {}
    overall = extra.get("overall") or {}
    if "asr" in overall:
        return "asr", overall.get("asr")
    if "rfs" in overall:
        return "rfs", overall.get("rfs")
    if "pass_rate" in extra:
        return "pass_rate", extra.get("pass_rate")
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
        primary_metric, primary_value = extract_primary_metric(data)

        include = True
        reasons = []
        if "_judge_rubric" in parts or "_judge_jury" in parts:
            include = False
            reasons.append("rubric_or_jury_meta_experiment")
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


def repo_metric_for_summary(benchmark: str, data: dict[str, Any]) -> tuple[str, float | None, str]:
    extra = data.get("extra_metrics") or {}
    overall = extra.get("overall") or {}
    if benchmark == "eduguard_sata":
        return "rfs_0_to_1", overall.get("rfs"), "extra_metrics.overall.rfs"
    if benchmark == "eduguard_adversarial":
        return "asr_0_to_1_lower_better", overall.get("asr"), "extra_metrics.overall.asr; primary judge deepseek-v3.2"
    if benchmark in {"bea2025_tutor", "mrbench_tutor"}:
        return "pass_rate", extra.get("pass_rate", data.get("accuracy")), "extra_metrics.pass_rate"
    if benchmark == "eduillustrate":
        return "likert_0_to_5", data.get("overall_mean_judged_only"), "overall_mean_judged_only"
    if benchmark == "mmtutorbench":
        return "score_0_to_6", extra.get("paper_weighted_score_0_to_6"), "extra_metrics.paper_weighted_score_0_to_6"
    if benchmark == "mathtutorbench_solution_correctness":
        return "accuracy_or_f1", extra.get("f1", data.get("accuracy")), "extra_metrics.f1"
    if benchmark == "mathtutorbench_mistake_location":
        return "accuracy_or_f1", extra.get("f1_micro", data.get("accuracy")), "extra_metrics.f1_micro"
    if benchmark in {
        "mathtutorbench_pedagogy",
        "mathtutorbench_pedagogy_hard",
        "mathtutorbench_scaffolding",
        "mathtutorbench_scaffolding_hard",
    }:
        return "win_rate_or_accuracy", extra.get("win_rate", data.get("accuracy")), "extra_metrics.win_rate"
    if benchmark == "mathtutorbench_socratic":
        return "bleu_0_to_1", extra.get("avg_bleu"), "extra_metrics.avg_bleu (official headline; summary.accuracy is a coarse BLEU>=0.5 proxy)"
    if benchmark.startswith("mathtutorbench_"):
        return "accuracy", data.get("accuracy"), "summary.accuracy"
    if benchmark in {"agieval", "ceval", "mmlu_pro", "mathvista", "olympiadbench"}:
        return "accuracy", data.get("accuracy"), "summary.accuracy"
    if benchmark in {"p07_selfcheck", "p08_calibration", "p08_abstention"}:
        return "composite_0_to_10", extra.get("score_10"), "extra_metrics.score_10"
    return "unknown", None, "no scoring rule"


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
        metric, raw_value, metric_note = repo_metric_for_summary(benchmark, data)
        if raw_value is None:
            continue
        mapping = find_mapping(benchmark, metric=metric)
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
                "notes": metric_note,
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


def score_atomic_p(selected_rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    evidence_rows: list[dict[str, Any]] = []
    accum: dict[tuple[str, str], dict[str, Any]] = {}
    for row in selected_rows:
        mapping = find_mapping(row["benchmark_id"], subdimension=row["subdimension"], metric=row["metric"])
        if mapping is None:
            continue
        tier = mapping["evidence_tier"]
        if tier == "excluded_judge_task":
            continue
        foundation_factor = FOUNDATION_GATE_FACTOR if tier == "foundation_gate" else 1.0
        for ability in mapping["abilities"]:
            raw_weight = mapping["default_benchmark_weight"] * ability["weight"]
            adjusted_weight = raw_weight * foundation_factor
            evidence = {
                "model_key": row["model_key"],
                "model": row["model"],
                "p_code": ability["p_code"],
                "p_name": ability["p_name"],
                "group": ability["group"],
                "benchmark_id": row["benchmark_id"],
                "subdimension": row["subdimension"],
                "source_type": row["source_type"],
                "source_path": row["source_path"],
                "metric": row["metric"],
                "raw_value": row["raw_value"],
                "score_10": row["score_10"],
                "evidence_tier": tier,
                "row_weight": mapping["default_benchmark_weight"],
                "ability_weight": ability["weight"],
                "raw_effective_weight": raw_weight,
                "adjusted_effective_weight": adjusted_weight,
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
                    "raw_weighted_sum": 0.0,
                    "raw_weight_sum": 0.0,
                    "adjusted_weighted_sum": 0.0,
                    "adjusted_weight_sum": 0.0,
                    "evidence_count": 0,
                    "benchmarks": set(),
                    "foundation_rows": 0,
                },
            )
            slot["raw_weighted_sum"] += row["score_10"] * raw_weight
            slot["raw_weight_sum"] += raw_weight
            slot["adjusted_weighted_sum"] += row["score_10"] * adjusted_weight
            slot["adjusted_weight_sum"] += adjusted_weight
            slot["evidence_count"] += 1
            slot["benchmarks"].add(row["benchmark_id"])
            if tier == "foundation_gate":
                slot["foundation_rows"] += 1

    p_rows: list[dict[str, Any]] = []
    for slot in accum.values():
        raw_score = slot["raw_weighted_sum"] / slot["raw_weight_sum"] if slot["raw_weight_sum"] else None
        tier_adjusted = (
            slot["adjusted_weighted_sum"] / slot["adjusted_weight_sum"] if slot["adjusted_weight_sum"] else None
        )
        p_rows.append(
            {
                "model_key": slot["model_key"],
                "display_model": slot["display_model"],
                "p_code": slot["p_code"],
                "p_name": slot["p_name"],
                "group": slot["group"],
                "raw_score_10": round(raw_score, 4) if raw_score is not None else None,
                "tier_adjusted_score_10": round(tier_adjusted, 4) if tier_adjusted is not None else None,
                "raw_weight_sum": round(slot["raw_weight_sum"], 4),
                "adjusted_weight_sum": round(slot["adjusted_weight_sum"], 4),
                "evidence_count": slot["evidence_count"],
                "benchmark_count": len(slot["benchmarks"]),
                "benchmarks": sorted(slot["benchmarks"]),
                "foundation_rows": slot["foundation_rows"],
            }
        )
    p_rows.sort(key=lambda r: (r["model_key"], r["p_code"]))

    group_accum: dict[tuple[str, str], dict[str, Any]] = {}
    for row in p_rows:
        slot = group_accum.setdefault(
            (row["model_key"], row["group"]),
            {
                "model_key": row["model_key"],
                "display_model": row["display_model"],
                "group": row["group"],
                "raw_sum": 0.0,
                "tier_sum": 0.0,
                "p_count": 0,
                "p_codes": [],
            },
        )
        slot["raw_sum"] += row["raw_score_10"] or 0.0
        slot["tier_sum"] += row["tier_adjusted_score_10"] or 0.0
        slot["p_count"] += 1
        slot["p_codes"].append(row["p_code"])
    group_rows: list[dict[str, Any]] = []
    for slot in group_accum.values():
        group_rows.append(
            {
                "model_key": slot["model_key"],
                "display_model": slot["display_model"],
                "group": slot["group"],
                "raw_score_10": round(slot["raw_sum"] / slot["p_count"], 4),
                "tier_adjusted_score_10": round(slot["tier_sum"] / slot["p_count"], 4),
                "p_count_with_evidence": slot["p_count"],
                "p_codes": sorted(slot["p_codes"]),
            }
        )
    group_rows.sort(key=lambda r: (r["model_key"], r["group"]))
    evidence_rows.sort(key=lambda r: (r["model_key"], r["p_code"], r["benchmark_id"], r["source_path"]))
    return evidence_rows, p_rows, group_rows


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
- `09_atomic_p_scores_raw_adjusted.jsonl`: per-model P01-P22 scores before and after foundation-gate weighting.
- `09_atomic_p_scores_raw_adjusted.md`: compact per-model P score table and coverage notes.
- `10_group_scores_raw_adjusted.jsonl`: SRG/FDR/LAD/CLM/CEG aggregate scores from available P scores.
- `10_group_scores_raw_adjusted.md`: compact group-score table.
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
4. It maps to at least one `P01-P22` ability through `02_benchmark_ability_mapping.jsonl`.
5. If multiple judge versions score the same model responses, keep only the selected primary judge in the main scoring layer and keep the others as context rows.

## Excluded by default

- Small samples and smoke tests: `total_items < 100`.
- Judge/rubric calibration: paths under `_judge_rubric`, `_judge_jury`, and benchmark ids containing `judge_calibration`.
- Backup directories such as `selfjudge_backup_*`.
- Protocol-only/data-resource rows without model scores.
- BEA/MRBench judge tasks: `bea2025_judge` and `mrbench_judge` are excluded in this pass. Tutor-generation tasks remain eligible.
- EduGuard P2 rows not judged by `deepseek-v3.2` are excluded from the repo scoring layer and preserved only as context.

## Foundation gate handling

MMLU-Pro, C-EVAL, AGIEval, OlympiadBench, and MathTutorBench problem-solving
style results are not ignored. They map mostly to `P05` and `P06`, with smaller
`P01/P03/P07` components. However, they are tagged as `foundation_gate` and
their effective weight is multiplied by 0.45 in adjusted scoring because high
answer accuracy does not prove teaching, diagnosis, personalization, or safety
capability.

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
        "| Benchmark | Subdimension | Tier | Metric | Default weight | P weights | Rationale |",
        "|---|---|---|---|---:|---|---|",
    ]
    for row in MAPPINGS:
        pweights = ", ".join(f"{a['p_code']} {a['weight']:.2f}" for a in row["abilities"])
        lines.append(
            "| {benchmark_name} (`{benchmark_id}`) | {subdimension} | {evidence_tier} | {metric_family} | {default_benchmark_weight:.2f} | {pweights} | {rationale} |".format(
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
            "3. `raw_score_10`: weighted average over evidence rows using default benchmark weights.",
            f"4. `tier_adjusted_score_10`: same weighted average after multiplying `foundation_gate` evidence by {FOUNDATION_GATE_FACTOR:.2f}.",
            "5. Report coverage separately per model/P ability: number of contributing rows, total effective weight, and benchmark families.",
            "6. Aggregate P abilities to SRG/FDR/LAD/CLM/CEG only after P-level scores are available. Missing P abilities are not imputed.",
            "",
            "## Resolved scoring choices in this pass",
            "",
            "- `foundation_gate` contributes to SRG/FDR through P scores at reduced effective weight.",
            "- EduGuard P2 uses `deepseek-v3.2` judge as the primary scoring judge.",
            "- BEA/MRBench judge tasks are excluded; BEA/MRBench tutor tasks remain eligible.",
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


def write_atomic_scores(p_rows: list[dict[str, Any]], evidence_rows: list[dict[str, Any]]) -> None:
    dump_jsonl(OUT / "09_atomic_p_score_evidence.jsonl", evidence_rows)
    dump_jsonl(OUT / "09_atomic_p_scores_raw_adjusted.jsonl", p_rows)
    covered = sorted({row["p_code"] for row in p_rows})
    missing = [code for code in P_GROUPS if code not in covered]
    lines = [
        "# Atomic P Scores: Raw And Adjusted",
        "",
        f"P-score rows: {len(p_rows)}",
        f"Covered P codes: {', '.join(covered) if covered else 'none'}",
        f"Missing P codes: {', '.join(missing) if missing else 'none'}",
        "",
        "`raw_score_10` uses default benchmark weights. `tier_adjusted_score_10` reduces foundation-gate evidence. Coverage completeness is reported separately and is not folded back into the score.",
        "",
        "## Sample Scores",
        "",
        "| Model key | P | Group | Raw | Tier adjusted | Evidence | Weight raw/adj | Benchmarks |",
        "|---|---|---|---:|---:|---:|---:|---|",
    ]
    for row in p_rows[:120]:
        lines.append(
            f"| `{row['model_key']}` | `{row['p_code']}` {row['p_name']} | {row['group']} | {row['raw_score_10']} | {row['tier_adjusted_score_10']} | {row['evidence_count']} | {row['raw_weight_sum']}/{row['adjusted_weight_sum']} | {', '.join(row['benchmarks'])} |"
        )
    lines.extend(
        [
            "",
            "## Coverage Notes",
            "",
            "- `P21` and `P22` are covered through EduGuard P1/P2 safety evidence.",
            "- `P09` has no current benchmark mapping in this pass.",
            "- `P15` has no current benchmark mapping after BEA/MRBench judge-task exclusion.",
            "- `P04`, `P08`, and `P19` remain sparse/absent unless proxy mappings are approved.",
            "- The v3 atomic list is `P01-P22`; no `P0` code exists in the current spec.",
            "",
            "Full P rows are in `09_atomic_p_scores_raw_adjusted.jsonl`; allocated evidence rows are in `09_atomic_p_score_evidence.jsonl`.",
        ]
    )
    (OUT / "09_atomic_p_scores_raw_adjusted.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_group_scores(group_rows: list[dict[str, Any]]) -> None:
    dump_jsonl(OUT / "10_group_scores_raw_adjusted.jsonl", group_rows)
    lines = [
        "# Group Scores: Raw And Adjusted",
        "",
        "These are provisional SRG/FDR/LAD/CLM/CEG aggregates from currently covered P abilities only. Missing P abilities are not imputed here.",
        "",
        "| Model key | Group | Raw | Tier adjusted | P count | P codes |",
        "|---|---|---:|---:|---:|---|",
    ]
    for row in group_rows:
        lines.append(
            f"| `{row['model_key']}` | {row['group']} | {row['raw_score_10']} | {row['tier_adjusted_score_10']} | {row['p_count_with_evidence']} | {', '.join(row['p_codes'])} |"
        )
    (OUT / "10_group_scores_raw_adjusted.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


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
    covered = sorted({row["p_code"] for row in p_rows})
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
        "SRG": "符号表征与情境锚定",
        "FDR": "领域形式推理与可靠执行",
        "LAD": "学习评价与错误诊断",
        "CLM": "认知建模与教学规划",
        "CEG": "约束性教育生成",
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
                    "evidence_tier": mapping["evidence_tier"],
                    "metric_family": mapping["metric_family"],
                    "benchmark_weight": mapping["default_benchmark_weight"],
                    "rationale": mapping["rationale"],
                }
            )
    all_benchmark_dims = sorted({(row["benchmark_id"], row["subdimension"]) for row in selected_score_rows})
    coverage_rows: list[dict[str, Any]] = []
    for model in models:
        model_score_rows = [row for row in selected_score_rows if row["model_key"] == model]
        model_p_rows = [row for row in p_rows if row["model_key"] == model]
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
                "adjusted_weight_sum": round(sum(float(row["adjusted_weight_sum"]) for row in model_p_rows), 4),
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
  <p class="hero-sub">基于本仓库评测与 <code>otherbenchmark/</code> 结果，将 benchmark/subdimension 映射到 <code>doc/atomic_ability_principle_audit_v3.md</code> 的 P01-P22 原子能力，并聚合到 SRG/FDR/LAD/CLM/CEG 五大维度。模型选择与分数版本切换逻辑保持可交互。</p>
</header>
  <section class="summary">
    <div class="kpi"><div class="v">{len(MAPPINGS)}</div><div class="l">benchmark / 维度映射行</div></div>
    <div class="kpi"><div class="v">{sum(1 for r in eval_rows if r['main_inclusion'] == 'include_candidate')}</div><div class="l">本仓库可计分候选 run</div></div>
    <div class="kpi"><div class="v">{len(other_rows)}</div><div class="l">otherbenchmark 原始分数行</div></div>
    <div class="kpi"><div class="v">{len(selected_score_rows)}</div><div class="l">去重后的计分证据行</div></div>
    <div class="kpi"><div class="v">{len(covered)}/22</div><div class="l">已覆盖 P 级原子能力</div></div>
  </section>

  <section class="panel">
    <h2>评分口径</h2>
    <div class="chips">
      <span class="chip">foundation_gate 调整权重 × {FOUNDATION_GATE_FACTOR:.2f}</span>
      <span class="chip">EduGuard P2 主裁判：{EDUGUARD_P2_PRIMARY_JUDGE}</span>
      <span class="chip">BEA/MRBench judge task 已排除</span>
      <span class="chip">EduIllustrate full-230 已纳入</span>
      <span class="chip">MiniMax-M3 优先 minimax3/full-scored run</span>
    </div>
    <div class="note">未覆盖或极弱覆盖的 P code：<b>{", ".join(missing)}</b>。P21/P22 当前主要由 EduGuard 安全证据覆盖。当前 atomic list 为 P01-P22，不存在 P0。</div>
  </section>

  <section class="panel">
    <h2>最终分数计算公式</h2>
    <div class="formula-grid">
      <div class="formula">
        <b>1. 原始指标归一化到 10 分制</b>
        <code>accuracy/pass_rate/rfs: score10 = value × 10<br>ASR: score10 = (1 - ASR) × 10<br>0-100 指标: score10 = value / 10<br>0-5 指标: score10 = value × 2<br>0-6 指标: score10 = value / 6 × 10</code>
      </div>
      <div class="formula">
        <b>2. benchmark 分数分配到 P 能力</b>
        <code>raw_effective_weight = benchmark_weight × ability_weight<br>P_raw = Σ(score10 × raw_effective_weight) / Σ(raw_effective_weight)</code>
      </div>
      <div class="formula">
        <b>3. 证据层调整分</b>
        <code>foundation_gate: adjusted_weight = raw_weight × {FOUNDATION_GATE_FACTOR:.2f}<br>P_tier = Σ(score10 × adjusted_weight) / Σ(adjusted_weight)<br>其中 foundation_gate 主要是基础答题/学科门槛类 benchmark。</code>
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
        <thead><tr><th>P</th><th>Benchmark</th><th>细分维度</th><th>证据层级</th><th>指标族</th><th class="num">benchmark 权重</th><th class="num">能力权重</th><th>映射理由</th></tr></thead>
        <tbody></tbody>
      </table>
    </div>
  </section>

  <div class="toolbar">
    <div>
      <label for="modelSelect">选择模型</label>
      <select id="modelSelect"></select>
    </div>
    <div>
      <label>分数版本</label>
      <div class="seg" id="scoreMode">
        <button data-mode="raw_score_10">原始</button>
        <button data-mode="tier_adjusted_score_10" class="active">证据层调整</button>
      </div>
    </div>
  </div>

  <section class="grid">
    <div class="panel">
      <h2>五维能力雷达图</h2>
      <div class="radar-wrap"><canvas id="radar" width="720" height="720"></canvas></div>
      <div class="axis-list" id="axisCards"></div>
    </div>
    <div class="panel">
      <h2>P01-P22 原子能力明细</h2>
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
    本报告由 <span class="mono">reports/atomic_ability_rebenchmark_2026-07-08/</span> 中间产物生成；生成脚本：<span class="mono">scripts/build_atomic_ability_rebenchmark_artifacts.py</span>。
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
let scoreMode = 'tier_adjusted_score_10';
let selectedPForMapping = 'ALL';
let selectedBenchmarkView = 'ALL';

function fmt(v) {{ return v === null || v === undefined ? '—' : Number(v).toFixed(2); }}
function esc(s) {{ return String(s ?? '').replace(/[&<>"']/g, c => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[c])); }}
function scoreFor(row) {{ return row ? row[scoreMode] : null; }}

function initModelSelect() {{
  const models = [...new Set(pRows.map(r => r.model_key))].sort();
  const sel = document.getElementById('modelSelect');
  sel.innerHTML = models.map(m => `<option value="${{esc(m)}}">${{esc(m)}}</option>`).join('');
  sel.value = selectedModel;
  sel.addEventListener('change', () => {{ selectedModel = sel.value; render(); }});
  document.querySelectorAll('#scoreMode button').forEach(btn => {{
    btn.addEventListener('click', () => {{
      document.querySelectorAll('#scoreMode button').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      scoreMode = btn.dataset.mode;
      render();
    }});
  }});

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
    return `<tr>
      <td><b>${{meta.p_code}}</b> ${{esc(meta.p_name)}}</td>
      <td>${{meta.group}}</td>
      <td class="num"><b>${{fmt(score)}}</b><div class="barbox"><div class="bar" style="width:${{pct}}%"></div></div></td>
      <td class="num">${{r ? r.evidence_count : 0}}</td>
      <td><div class="small">${{r ? esc(r.benchmarks.join(', ')) : '无证据'}}</div></td>
    </tr>`;
  }}).join('');
}}

function renderEvidenceTable() {{
  const rows = evidenceRows.filter(r => r.model_key === selectedModel).slice(0, 220);
  document.querySelector('#evidenceTable tbody').innerHTML = rows.map(r => `<tr>
    <td>${{r.p_code}}</td>
    <td>${{esc(r.benchmark_id)}}<div class="small">${{esc(r.subdimension)}}</div></td>
    <td>${{esc(r.metric)}}</td>
    <td class="num">${{fmt(r.score_10)}}</td>
    <td class="num">${{Number(r.adjusted_effective_weight).toFixed(3)}}</td>
    <td><span class="mono">${{esc(r.source_path)}}</span></td>
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
      <td class="num">${{Number(r.adjusted_weight_sum).toFixed(2)}}</td>
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
    <td>${{esc(r.evidence_tier)}}</td>
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
        tier_factor = TIER_IMPORTANCE_FACTOR.get(mapping["evidence_tier"], 0.60)
        p_relevance_score = 100.0 * ability_priority
        importance_score = 100.0 * mapping["default_benchmark_weight"] * ability_priority * tier_factor

        model_coverage = len(model_keys) / model_target if model_target else 0.0
        p_gap = statistics.mean(
            1.0 - clamp(p_model_counts.get(ability["p_code"], 0) / 4.0)
            for ability in mapping["abilities"]
        )
        coverage_gap = 0.60 * (1.0 - clamp(model_coverage)) + 0.40 * p_gap

        priority_score = importance_score * (0.58 * unsolved_index + 0.32 * coverage_gap + 0.10)
        if mapping["evidence_tier"] == "excluded_judge_task":
            priority_score *= 0.10

        if mapping["evidence_tier"] == "excluded_judge_task":
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
        elif mapping["evidence_tier"] == "foundation_gate":
            recommendation = "降为门槛项"
            rationale = "主要测基础答题能力，高分不能证明教学、诊断、个性化或安全。"
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
                "evidence_tier": mapping["evidence_tier"],
                "metric_family": mapping["metric_family"],
                "p_codes": [ability["p_code"] for ability in mapping["abilities"]],
                "p_weights": [
                    f"{ability['p_code']} {ability['weight']:.2f}" for ability in mapping["abilities"]
                ],
                "groups": sorted({ability["group"] for ability in mapping["abilities"]}),
                "benchmark_weight": mapping["default_benchmark_weight"],
                "p_relevance_score": round(p_relevance_score, 2),
                "tier_factor": tier_factor,
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
      <div><b>重要性</b><br><code>I = 100 × benchmark_weight × tier_factor × Σ(P_priority × P_weight)</code><br><span class="small">education_core=1.00，diagnostic=0.75，foundation_gate=0.45；P08/P09/P10/P15/P16/P19/P22 等覆盖洼地提高 P_priority。</span></div>
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
        <input id="search" placeholder="例如 MathTutorBench、P13、安全、门槛">
      </div>
      <div>
        <label for="recFilter">建议档位</label>
        <select id="recFilter"><option value="ALL">全部</option></select>
      </div>
      <div>
        <label for="tierFilter">证据层级</label>
        <select id="tierFilter"><option value="ALL">全部</option></select>
      </div>
    </div>
    <div class="table-wrap">
      <table id="priorityTable">
        <thead><tr><th>建议</th><th>Benchmark</th><th>P 能力</th><th class="num">优先级</th><th class="num">重要性</th><th class="num">未解决</th><th class="num">覆盖缺口</th><th class="num">best / median</th><th class="num">模型数</th><th>判断理由</th></tr></thead>
        <tbody></tbody>
      </table>
    </div>
  </section>

  <footer class="small">数据源：<span class="mono">08_selected_score_evidence.jsonl</span>、<span class="mono">02_benchmark_ability_mapping.jsonl</span>、<span class="mono">09_atomic_p_scores_raw_adjusted.jsonl</span>。机器可读排序：<span class="mono">12_benchmark_priority_analysis.jsonl</span>。</footer>
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
  const tiers = [...new Set(rows.map(r => r.evidence_tier))];
  document.getElementById('recFilter').innerHTML += recs.map(v => `<option value="${{esc(v)}}">${{esc(v)}}</option>`).join('');
  document.getElementById('tierFilter').innerHTML += tiers.map(v => `<option value="${{esc(v)}}">${{esc(v)}}</option>`).join('');
  document.getElementById('search').addEventListener('input', renderTable);
  document.getElementById('recFilter').addEventListener('change', renderTable);
  document.getElementById('tierFilter').addEventListener('change', renderTable);
}}
function renderTable() {{
  const q = document.getElementById('search').value.trim().toLowerCase();
  const rec = document.getElementById('recFilter').value;
  const tier = document.getElementById('tierFilter').value;
  const data = rows.filter(r => {{
    if (rec !== 'ALL' && r.recommendation !== rec) return false;
    if (tier !== 'ALL' && r.evidence_tier !== tier) return false;
    if (!q) return true;
    return JSON.stringify([r.benchmark_name,r.benchmark_id,r.subdimension,r.p_codes,r.rationale,r.mapping_rationale]).toLowerCase().includes(q);
  }});
  document.querySelector('#priorityTable tbody').innerHTML = data.map(r => `<tr>
    <td><span class="tag ${{tagClass(r.recommendation)}}">${{esc(r.recommendation)}}</span><div class="small">${{esc(r.quadrant)}}</div></td>
    <td><b>${{esc(r.benchmark_name)}}</b><div class="mono small">${{esc(r.benchmark_id)}}</div><div class="small">${{esc(r.subdimension)}}</div><div class="small">${{esc(r.evidence_tier)}}</div></td>
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
    tier = row["evidence_tier"]
    if tier == "excluded_judge_task":
        return "先排除"
    if avg is None:
        return "高相关但缺跑分" if relevance >= 45 else "暂不判断"
    if tier == "foundation_gate":
        return "门槛保留" if avg < 8.5 else "低频门槛"
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
                "tiers": set(),
                "recommendations": [],
            },
        )
        slot["subdimensions"] += 1
        if row["all_model_average_score_10"] is not None:
            slot["scores"].append(row["all_model_average_score_10"])
        slot["relevance"].append(row["importance_score"])
        slot["p_codes"].update(row["p_codes"])
        slot["tiers"].add(row["evidence_tier"])
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
                "tiers": sorted(slot["tiers"]),
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
        "2. **原子能力有效相关性**：只由 mapping 决定，不看模型表现。公式：`100 × benchmark_weight × tier_factor × Σ(P_priority × ability_weight)`。其中 `tier_factor`: education_core=1.00, diagnostic=0.75, foundation_gate=0.45, excluded_judge_task=0.08。",
        "",
        "辅助列：`P 相关性` 是不乘 benchmark/tier 的纯 P 能力相关性；`tier` 表示证据直接性。基础答题类通常会因为 `foundation_gate` 被降权。",
        "",
        "## 先看结论排序",
        "",
        "| 建议 | Benchmark | Subdimension | 所有模型平均分 | 原子能力有效相关性 | P 相关性 | tier | 模型数 | P 映射 |",
        "|---|---|---|---:|---:|---:|---|---:|---|",
    ]
    for row in ranked:
        lines.append(
            f"| {simple_portfolio_recommendation(row)} | `{row['benchmark_id']}` {row['benchmark_name']} | {row['subdimension']} | {fmt(row['all_model_average_score_10'])} | {fmt(row['importance_score'])} | {fmt(row['p_relevance_score'])} | {row['evidence_tier']} | {row['model_count']} | {', '.join(row['p_weights'])} |"
        )

    lines.extend(
        [
            "",
            "## 按 benchmark 聚合",
            "",
            "聚合口径：同一 benchmark 的多个 subdimension 先各自计算平均分和相关性，再在 benchmark 内做简单平均；只用于概览，具体判断仍看上面的 subdimension 明细。",
            "",
            "| 建议 | Benchmark | Subdimension 数 | benchmark 平均分 | 平均原子相关性 | tier | P 覆盖 |",
            "|---|---|---:|---:|---:|---|---|",
        ]
    )
    for row in group_rows:
        lines.append(
            f"| {row['recommendation']} | `{row['benchmark_id']}` {row['benchmark_name']} | {row['subdimensions']} | {fmt(row['avg_score'])} | {fmt(row['avg_relevance'])} | {', '.join(row['tiers'])} | {', '.join(row['p_codes'])} |"
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

- `foundation_gate` contributes to SRG/FDR through P-level scores at reduced effective weight.
- EduGuard P2 uses `deepseek-v3.2` judge as primary.
- BEA/MRBench judge tasks are excluded.
- EduIllustrate full-230 runs are included; 5-item runs are excluded.
- MiniMax-M3 canonical policy prefers included `minimax3/` or fuller-scored runs.

Remaining review points:

1. The v3 atomic list has `P01-P22`; there is no `P0`. If the request meant a specific ability, confirm whether it means `P01` or another P code.
2. Current evidence may still be sparse or absent for `P04`, `P08`, `P09`, `P15`, and `P19`. Confirm whether to leave them blank/low-coverage or add proxy mappings.
3. `P21/P22` are covered mainly by EduGuard safety evidence. Confirm whether that is sufficient, or whether to require student-risk-specific datasets.
4. For cross-model comparison, decide whether to add a strict `common-evidence` mode that only compares models on shared benchmark/subdimension coverage.
"""
    (OUT / "06_open_calibration_questions.md").write_text(text, encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    eval_rows = inventory_eval_runs()
    other_rows = inventory_otherbenchmark_scores()
    score_candidates = build_repo_score_candidates(eval_rows) + build_other_score_candidates(other_rows)
    selected_score_rows, duplicate_rows = dedupe_score_candidates(score_candidates)
    minimax_rows = minimax_conflict_report(eval_rows)
    evidence_rows, p_rows, group_rows = score_atomic_p(selected_score_rows)
    write_readme()
    write_inclusion_policy()
    write_mapping_files()
    write_normalization()
    write_inventory(eval_rows)
    write_otherbenchmark_scores(other_rows)
    write_deduplication_report(duplicate_rows, minimax_rows)
    write_score_evidence(selected_score_rows)
    write_atomic_scores(p_rows, evidence_rows)
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
    print("html: 11_atomic_ability_rebenchmark_report.html")
    print("priority html: 12_benchmark_priority_report.html")


if __name__ == "__main__":
    main()
