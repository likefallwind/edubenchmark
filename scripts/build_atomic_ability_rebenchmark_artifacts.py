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
    # P2 ASR tables for the two judges.
    for judge_marker, note in [
        ("(a) MiniMax-M3 judge", "MiniMax-M3 judge"),
        ("(b) deepseek-v3.2 judge", "deepseek-v3.2 judge"),
    ]:
        start = text.find(judge_marker)
        if start < 0:
            continue
        next_marker = text.find("<p class=\"small\"", start + 1)
        section_end = next_marker if next_marker > 0 else text.find("<p class=\"legend\">", start)
        block = text[start: section_end if section_end > 0 else len(text)]
        for tr in re.findall(r"<tr>(.*?)</tr>", block, flags=re.S):
            cells = [strip_tags(c) for c in re.findall(r"<td[^>]*>(.*?)</td>", tr, flags=re.S)]
            if len(cells) >= 2 and cells[0] and cells[0] != "模型":
                try:
                    value = float(cells[1].rstrip("%")) / 100.0
                except ValueError:
                    continue
                add_score(
                    rows,
                    source_path=path.relative_to(ROOT).as_posix(),
                    benchmark_id="eduguard_adversarial",
                    benchmark_name="EduGuard-Bench P2",
                    subdimension="Adversarial Safety ASR",
                    model=cells[0],
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
- `06_open_calibration_questions.md`: decisions that should be reviewed before final HTML scoring.

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
5. If multiple judge versions score the same model responses, keep them as separate evidence rows until a judge policy is chosen. Do not average judge variants silently.

## Excluded by default

- Small samples and smoke tests: `total_items < 100`.
- Judge/rubric calibration: paths under `_judge_rubric`, `_judge_jury`, and benchmark ids containing `judge_calibration`.
- Backup directories such as `selfjudge_backup_*`.
- Protocol-only/data-resource rows without model scores.

## Foundation gate handling

MMLU-Pro, C-EVAL, AGIEval, OlympiadBench problem-solving style results are not
ignored. They map mostly to `P05` and `P06`, with smaller `P01/P03` components.
However, they are tagged as `foundation_gate` and receive lower default weights
in the five-axis education radar because high answer accuracy does not prove
teaching, diagnosis, personalization, or safety capability.

If later analysis shows no P ability cleanly captures a foundation result, add a
separate report band named `LLM答题门槛能力`, but do not add it as a sixth radar
axis unless the atomic-ability spec is revised.
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
            "3. Within each model and P ability, compute a weighted average over evidence rows.",
            "4. Report coverage per P ability: number of contributing rows, total effective weight, and benchmark families.",
            "5. Aggregate P abilities to SRG/FDR/LAD/CLM/CEG only after P-level scores are available.",
            "6. Display foundation-gate scores separately or with lower weight; do not let answer-only benchmarks dominate education-specific axes.",
            "",
            "## Open scoring choices",
            "",
            "- Whether to use raw weighted average, coverage-aware shrinkage, or both side by side.",
            "- Whether `foundation_gate` evidence should contribute to the radar at 0.35-0.55 weight or only appear as a separate gate band.",
            "- Which EduGuard P2 judge variant should be primary for final scoring.",
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
    for row in rows:
        by_bench[row["benchmark_id"]] = by_bench.get(row["benchmark_id"], 0) + 1
        by_metric[row["metric"]] = by_metric.get(row["metric"], 0) + 1
    lines = [
        "# Otherbenchmark Score Inventory",
        "",
        f"Parsed score rows: {len(rows)}",
        "",
        "## By Benchmark",
        "",
        "| Benchmark | Rows |",
        "|---|---:|",
    ]
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
            "| Benchmark | Subdimension | Model | Metric | Raw value | Notes |",
            "|---|---|---|---|---:|---|",
        ]
    )
    for row in rows[:40]:
        lines.append(
            f"| `{row['benchmark_id']}` | {row['subdimension']} | {row['model']} | `{row['metric']}` | {row['raw_value']} | {row['notes']} |"
        )
    lines.append("")
    lines.append("Full parsed rows are in `05_otherbenchmark_score_inventory.jsonl`.")
    (OUT / "05_otherbenchmark_score_inventory.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_open_questions() -> None:
    text = """# Open Calibration Questions

1. Should `foundation_gate` results contribute to SRG/FDR radar axes at reduced weight, or appear only as a separate `LLM答题门槛能力` strip?
2. For EduGuard P2, should the final score use MiniMax-M3 judge, deepseek-v3.2 judge, or a conservative worst-case/average of both?
3. For duplicate MiniMax-M3 runs under dated directories and `minimax3/`, which path should be canonical when scored and displayed?
4. Should BEA/MRBench judge tasks score the model as an education evaluator (`P14/P13/P11`) or be separated from tutor-generation tasks?
5. Should EduIllustrate full-230 runs be included in the main radar now, or stay diagnostic until more models have full runs?
6. How should coverage be shown for P08, P09, P15, P19, P21/P22 when evidence is sparse or mostly safety-oriented?
7. Should final HTML include both raw P scores and shrinkage-adjusted P scores to avoid hiding low coverage?
"""
    (OUT / "06_open_calibration_questions.md").write_text(text, encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    eval_rows = inventory_eval_runs()
    other_rows = inventory_otherbenchmark_scores()
    write_readme()
    write_inclusion_policy()
    write_mapping_files()
    write_normalization()
    write_inventory(eval_rows)
    write_otherbenchmark_scores(other_rows)
    write_open_questions()
    print(f"wrote artifacts to {OUT}")
    print(f"mapping rows: {len(MAPPINGS)}")
    print(f"eval summaries: {len(eval_rows)}")
    print(f"include candidates: {sum(1 for r in eval_rows if r['main_inclusion'] == 'include_candidate')}")
    print(f"otherbenchmark score rows: {len(other_rows)}")


if __name__ == "__main__":
    main()
