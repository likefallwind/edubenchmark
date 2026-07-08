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
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "atomic_ability_rebenchmark_2026-07-08"
EVAL_DIR = ROOT / "reports" / "eval"
OTHER_DIR = ROOT / "otherbenchmark"

EDUGUARD_P2_PRIMARY_JUDGE = "deepseek-v3.2 judge"
EXCLUDED_SCORING_BENCHMARKS = {"bea2025_judge", "mrbench_judge"}
FOUNDATION_GATE_FACTOR = 0.45
SHRINKAGE_K = 1.0


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
        if total and total < 100:
            include = False
            reasons.append("small_sample_under_100")
        if not total:
            include = False
            reasons.append("missing_or_zero_total")
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
    if benchmark.startswith("mathtutorbench_"):
        return "accuracy", data.get("accuracy"), "summary.accuracy"
    if benchmark in {"agieval", "ceval", "mmlu_pro", "mathvista", "olympiadbench"}:
        return "accuracy", data.get("accuracy"), "summary.accuracy"
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
        coverage_adjusted = None
        if tier_adjusted is not None:
            coverage_adjusted = (slot["adjusted_weighted_sum"] + 5.0 * SHRINKAGE_K) / (
                slot["adjusted_weight_sum"] + SHRINKAGE_K
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
                "coverage_adjusted_score_10": round(coverage_adjusted, 4) if coverage_adjusted is not None else None,
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
                "coverage_sum": 0.0,
                "p_count": 0,
                "p_codes": [],
            },
        )
        slot["raw_sum"] += row["raw_score_10"] or 0.0
        slot["tier_sum"] += row["tier_adjusted_score_10"] or 0.0
        slot["coverage_sum"] += row["coverage_adjusted_score_10"] or 0.0
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
                "coverage_adjusted_score_10": round(slot["coverage_sum"] / slot["p_count"], 4),
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
- `09_atomic_p_scores_raw_adjusted.jsonl`: per-model P01-P22 scores before and after weighting/coverage adjustment.
- `09_atomic_p_scores_raw_adjusted.md`: compact per-model P score table and coverage notes.
- `10_group_scores_raw_adjusted.jsonl`: SRG/FDR/LAD/CLM/CEG aggregate scores from available P scores.
- `10_group_scores_raw_adjusted.md`: compact group-score table.

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
            f"5. `coverage_adjusted_score_10`: shrink tier-adjusted evidence toward a neutral prior of 5.0 with K={SHRINKAGE_K:.1f}, so sparse P abilities are visible.",
            "6. Report coverage per P ability: number of contributing rows, total effective weight, and benchmark families.",
            "7. Aggregate P abilities to SRG/FDR/LAD/CLM/CEG only after P-level scores are available.",
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
        "`raw_score_10` uses default benchmark weights. `tier_adjusted_score_10` reduces foundation-gate evidence. `coverage_adjusted_score_10` additionally shrinks sparse evidence toward 5.0.",
        "",
        "## Sample Scores",
        "",
        "| Model key | P | Group | Raw | Tier adjusted | Coverage adjusted | Evidence | Weight raw/adj | Benchmarks |",
        "|---|---|---|---:|---:|---:|---:|---:|---|",
    ]
    for row in p_rows[:120]:
        lines.append(
            f"| `{row['model_key']}` | `{row['p_code']}` {row['p_name']} | {row['group']} | {row['raw_score_10']} | {row['tier_adjusted_score_10']} | {row['coverage_adjusted_score_10']} | {row['evidence_count']} | {row['raw_weight_sum']}/{row['adjusted_weight_sum']} | {', '.join(row['benchmarks'])} |"
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
        "| Model key | Group | Raw | Tier adjusted | Coverage adjusted | P count | P codes |",
        "|---|---|---:|---:|---:|---:|---|",
    ]
    for row in group_rows:
        lines.append(
            f"| `{row['model_key']}` | {row['group']} | {row['raw_score_10']} | {row['tier_adjusted_score_10']} | {row['coverage_adjusted_score_10']} | {row['p_count_with_evidence']} | {', '.join(row['p_codes'])} |"
        )
    (OUT / "10_group_scores_raw_adjusted.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


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
4. For the final HTML, decide whether the headline radar should use `tier_adjusted_score_10` or the more conservative `coverage_adjusted_score_10`.
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
    write_open_questions()
    print(f"wrote artifacts to {OUT}")
    print(f"mapping rows: {len(MAPPINGS)}")
    print(f"eval summaries: {len(eval_rows)}")
    print(f"include candidates: {sum(1 for r in eval_rows if r['main_inclusion'] == 'include_candidate')}")
    print(f"otherbenchmark score rows: {len(other_rows)}")
    print(f"score candidates: {len(score_candidates)}")
    print(f"selected score rows: {len(selected_score_rows)}")
    print(f"p score rows: {len(p_rows)}")


if __name__ == "__main__":
    main()
