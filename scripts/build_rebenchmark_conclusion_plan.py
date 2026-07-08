#!/usr/bin/env python3
"""Build the 2026-07-06 rebenchmark conclusion and next-plan HTML report.

The report uses the current v3.2 P01-P22 atomic-capability definitions as the
ability spine. The five-dimension MiniMax-M3 profile is computed from current
``reports/eval/**/summary.json`` artifacts only; the 2026-07-01 cross-model
benchmark table is retained as reference evidence and is not used for the radar.
"""

from __future__ import annotations

import argparse
import html
import json
import math
import re
from collections import defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "tempt" / "rebenchmark-conclusion-plan-0706.html"
ATOMIC_DOC = ROOT / "doc" / "atomic_ability_principle_audit_v3.md"
MAIN_SOURCE = "tempt/rebenchmark-summary-0701.html"


DIMENSIONS: dict[str, dict[str, str]] = {
    "SRG": {
        "zh": "符号表征与情境锚定",
        "en": "Symbolic Representation & Grounding",
        "color": "#2563eb",
        "summary": "把指令、上下文、文本和多模态输入锚定成可推理的教育语境。",
    },
    "FDR": {
        "zh": "领域形式推理与可靠执行",
        "en": "Formal Domain Reasoning & Reliable Execution",
        "color": "#d97706",
        "summary": "调用知识、推理、校验、弃答和工具链完成可验证任务。",
    },
    "LAD": {
        "zh": "学习评价与错误诊断",
        "en": "Learning Assessment & Diagnostic Reasoning",
        "color": "#16a34a",
        "summary": "判断作答、定位错误、归因错因，并映射 rubric 或评分标准。",
    },
    "CLM": {
        "zh": "认知建模与教学规划",
        "en": "Cognitive Modeling & Instructional Planning",
        "color": "#7c3aed",
        "summary": "估计学习者状态，选择个性化干预，规划路径并生成适配反馈。",
    },
    "CEG": {
        "zh": "约束性教育生成",
        "en": "Constrained Educational Generation",
        "color": "#dc2626",
        "summary": "在角色边界、风险识别和安全处置约束下输出教育回复。",
    },
}

P_TO_DIMENSION: dict[str, str] = {
    **{f"P{i:02d}": "SRG" for i in range(1, 5)},
    **{f"P{i:02d}": "FDR" for i in range(5, 11)},
    **{f"P{i:02d}": "LAD" for i in range(11, 16)},
    **{f"P{i:02d}": "CLM" for i in range(16, 20)},
    **{f"P{i:02d}": "CEG" for i in range(20, 23)},
}


CAPABILITY_MAPPINGS: dict[str, dict[str, Any]] = {
    "Pedagogy Benchmark|Accuracy": {
        "primary_p_codes": ["P05", "P17"],
        "secondary_p_codes": ["P18"],
        "evidence_note": "教学法知识与教学策略选择；不是完整 tutor 过程评测。",
        "score_role": "main",
    },
    "ASAP 2.0|QWK": {
        "primary_p_codes": ["P14"],
        "secondary_p_codes": ["P11"],
        "evidence_note": "作文 trait/总分与人工评分一致性，主要支撑 rubric 映射评分。",
        "score_role": "main",
    },
    "EduBench|Mean": {
        "primary_p_codes": ["P01", "P05", "P06", "P17", "P18", "P19"],
        "secondary_p_codes": ["P10", "P16"],
        "evidence_note": "开放式教育任务生成均值；共享证据，不等于各 P 能力独立测量。",
        "score_role": "main",
    },
    "TutorBench|Fair815": {
        "primary_p_codes": ["P03", "P06", "P13", "P17", "P18"],
        "secondary_p_codes": ["P20"],
        "evidence_note": "多模态 tutoring 质量，覆盖感知、推理、错因与反馈策略。",
        "score_role": "main",
    },
    "SAS-Bench|QWK": {
        "primary_p_codes": ["P14"],
        "secondary_p_codes": ["P11"],
        "evidence_note": "短答案评分总分一致性，主要用于 rubric/分档映射。",
        "score_role": "main",
    },
    "SAS-Bench|CCS": {
        "primary_p_codes": ["P11", "P14"],
        "secondary_p_codes": ["P12"],
        "evidence_note": "分步/概念评分一致性，作为作答判定与 rubric 证据共享。",
        "score_role": "main",
    },
    "SAS-Bench|ECS": {
        "primary_p_codes": ["P13"],
        "secondary_p_codes": ["P12"],
        "evidence_note": "错误解释一致性，主要映射错因归因。",
        "score_role": "main",
    },
    "EduGuard-Bench|P1 RFS": {
        "primary_p_codes": ["P20", "P21", "P22"],
        "secondary_p_codes": ["P18"],
        "evidence_note": "教学伤害场景的角色边界、风险识别和教育性安全处置。",
        "score_role": "main",
    },
    "EduGuard-Bench|P2 ASR": {
        "primary_p_codes": ["P20", "P22"],
        "secondary_p_codes": ["P21"],
        "evidence_note": "对抗安全 attack success rate，归一化时使用 1-ASR。",
        "score_role": "main",
    },
    "mmlu_pro": {
        "primary_p_codes": ["P05", "P06"],
        "secondary_p_codes": ["P01"],
        "evidence_note": "学科知识与复杂选择题推理门槛项，不能证明教学能力。",
        "score_role": "display_only",
    },
    "ceval": {
        "primary_p_codes": ["P05"],
        "secondary_p_codes": ["P01", "P06"],
        "evidence_note": "中文考试与学科知识门槛项。",
        "score_role": "display_only",
    },
    "agieval": {
        "primary_p_codes": ["P05", "P06"],
        "secondary_p_codes": ["P01"],
        "evidence_note": "标准化考试与逻辑推理门槛项。",
        "score_role": "display_only",
    },
    "olympiadbench": {
        "primary_p_codes": ["P06"],
        "secondary_p_codes": ["P03", "P04", "P05"],
        "evidence_note": "奥赛数学/物理推理，含多模态题但不是教学反馈任务。",
        "score_role": "display_only",
    },
    "mathvista": {
        "primary_p_codes": ["P03", "P06"],
        "secondary_p_codes": ["P04"],
        "evidence_note": "多模态数学理解与解题，主要是 SRG/FDR 门槛。",
        "score_role": "display_only",
    },
    "mathtutorbench_problem_solving": {
        "primary_p_codes": ["P05", "P06"],
        "secondary_p_codes": ["P11"],
        "evidence_note": "求解正确性门槛，需与诊断/反馈任务分开解释。",
        "score_role": "display_only",
    },
    "mathtutorbench_solution_correctness": {
        "primary_p_codes": ["P11"],
        "secondary_p_codes": ["P07"],
        "evidence_note": "给定参考下判断学生解答是否正确。",
        "score_role": "display_only",
    },
    "mathtutorbench_mistake_location": {
        "primary_p_codes": ["P12"],
        "secondary_p_codes": ["P02", "P11"],
        "evidence_note": "定位学生步骤错误位置。",
        "score_role": "display_only",
    },
    "mathtutorbench_mistake_correction": {
        "primary_p_codes": ["P13", "P18"],
        "secondary_p_codes": ["P12"],
        "evidence_note": "纠错与反馈修正，兼有错因归因和适配反馈。",
        "score_role": "display_only",
    },
    "mathtutorbench_scaffolding": {
        "primary_p_codes": ["P17", "P18"],
        "secondary_p_codes": ["P13"],
        "evidence_note": "脚手架提示质量，LLM-as-judge 替代官方 reward model。",
        "score_role": "display_only",
    },
    "mathtutorbench_scaffolding_hard": {
        "primary_p_codes": ["P17", "P18"],
        "secondary_p_codes": ["P13"],
        "evidence_note": "困难脚手架提示质量，LLM-as-judge。",
        "score_role": "display_only",
    },
    "mathtutorbench_pedagogy": {
        "primary_p_codes": ["P17", "P18"],
        "secondary_p_codes": ["P05"],
        "evidence_note": "教学法选择与解释反馈质量，LLM-as-judge。",
        "score_role": "display_only",
    },
    "mathtutorbench_pedagogy_hard": {
        "primary_p_codes": ["P17", "P18"],
        "secondary_p_codes": ["P05"],
        "evidence_note": "困难教学法选择与反馈质量，LLM-as-judge。",
        "score_role": "display_only",
    },
    "mathtutorbench_socratic": {
        "primary_p_codes": ["P17", "P18"],
        "secondary_p_codes": ["P01"],
        "evidence_note": "苏格拉底式引导文本质量。",
        "score_role": "display_only",
    },
    "mathtutorbench_judge_calibration": {
        "primary_p_codes": ["P14"],
        "secondary_p_codes": ["P17", "P18"],
        "evidence_note": "候选 judge 与专家偏好一致率，属于裁判可靠性证据。",
        "score_role": "display_only",
    },
    "mmtutorbench": {
        "primary_p_codes": ["P03", "P04", "P13", "P18"],
        "secondary_p_codes": ["P05", "P06"],
        "evidence_note": "多模态 tutor 冒烟样本；样本量过小，只展示不计分。",
        "score_role": "display_only",
    },
    "mmtutorbench_judge_calibration": {
        "primary_p_codes": [],
        "secondary_p_codes": ["P14"],
        "evidence_note": "无公开逐项人类 gold，标记为 coverage_gap。",
        "score_role": "coverage_gap",
    },
    "eduguard_sata": {
        "primary_p_codes": ["P20", "P21", "P22"],
        "secondary_p_codes": ["P18"],
        "evidence_note": "教育安全 P1 SATA，使用 RFS/完美匹配等指标。",
        "score_role": "display_only",
    },
    "eduguard_adversarial": {
        "primary_p_codes": ["P20", "P22"],
        "secondary_p_codes": ["P21"],
        "evidence_note": "教育安全 P2 对抗测试，使用 1-ASR 解释。",
        "score_role": "display_only",
    },
    "mrbench_judge": {
        "primary_p_codes": ["P11", "P12", "P13", "P14", "P18"],
        "secondary_p_codes": ["P17"],
        "evidence_note": "tutor 回复质量维度的 judge-human agreement 与 kappa。",
        "score_role": "display_only",
    },
    "mrbench_tutor": {
        "primary_p_codes": ["P13", "P17", "P18"],
        "secondary_p_codes": ["P11", "P12"],
        "evidence_note": "tutor 回复生成/选择质量，不是主榜计分。",
        "score_role": "display_only",
    },
    "bea2025_judge": {
        "primary_p_codes": ["P12", "P13", "P14", "P18"],
        "secondary_p_codes": ["P11", "P17"],
        "evidence_note": "BEA dev-set judge 校准，含 exact/lenient/kappa。",
        "score_role": "display_only",
    },
    "bea2025_tutor": {
        "primary_p_codes": ["P13", "P17", "P18"],
        "secondary_p_codes": ["P12"],
        "evidence_note": "BEA tutor pass-rate 本地评测，官方 test labels hidden。",
        "score_role": "display_only",
    },
    "eduillustrate": {
        "primary_p_codes": ["P10"],
        "secondary_p_codes": ["P03", "P05", "P06", "P18"],
        "evidence_note": "多模态教学图解生成，当前多为替代 judge/小样本。",
        "score_role": "display_only",
    },
}


ABILITY_CODE_OVERRIDES: dict[str, dict[str, list[str]]] = {
    "Pedagogy Benchmark|Accuracy": {
        "score_p_codes": ["P05", "P06", "P17"],
        "covered_p_codes": ["P05", "P06", "P16", "P17", "P18"],
    },
    "ASAP 2.0|QWK": {
        "score_p_codes": ["P14"],
        "covered_p_codes": ["P02", "P05", "P06", "P11", "P14"],
    },
    "EduBench|Mean": {
        "score_p_codes": ["P17", "P18", "P19"],
        "covered_p_codes": ["P01", "P05", "P06", "P10", "P11", "P12", "P13", "P16", "P17", "P18", "P19"],
    },
    "TutorBench|Fair815": {
        "score_p_codes": ["P03", "P06", "P13", "P17", "P18"],
        "covered_p_codes": ["P01", "P03", "P04", "P05", "P06", "P11", "P12", "P13", "P17", "P18", "P20"],
    },
    "SAS-Bench|QWK": {
        "score_p_codes": ["P14"],
        "covered_p_codes": ["P11", "P14"],
    },
    "SAS-Bench|CCS": {
        "score_p_codes": ["P11", "P14"],
        "covered_p_codes": ["P11", "P12", "P14"],
    },
    "SAS-Bench|ECS": {
        "score_p_codes": ["P13"],
        "covered_p_codes": ["P12", "P13"],
    },
    "EduGuard-Bench|P1 RFS": {
        "score_p_codes": ["P20", "P21", "P22"],
        "covered_p_codes": ["P18", "P20", "P21", "P22"],
    },
    "EduGuard-Bench|P2 ASR": {
        "score_p_codes": ["P20", "P22"],
        "covered_p_codes": ["P20", "P21", "P22"],
    },
    "mmlu_pro": {
        "score_p_codes": ["P05", "P06"],
        "covered_p_codes": ["P01", "P05", "P06"],
    },
    "ceval": {
        "score_p_codes": ["P05"],
        "covered_p_codes": ["P01", "P05", "P06"],
    },
    "agieval": {
        "score_p_codes": ["P05", "P06"],
        "covered_p_codes": ["P01", "P05", "P06"],
    },
    "olympiadbench": {
        "score_p_codes": ["P06"],
        "covered_p_codes": ["P03", "P04", "P05", "P06"],
    },
    "mathvista": {
        "score_p_codes": ["P03", "P04", "P06"],
        "covered_p_codes": ["P03", "P04", "P06"],
    },
    "mathtutorbench_problem_solving": {
        "score_p_codes": ["P05", "P06"],
        "covered_p_codes": ["P05", "P06"],
    },
    "mathtutorbench_solution_correctness": {
        "score_p_codes": ["P11"],
        "covered_p_codes": ["P07", "P11"],
    },
    "mathtutorbench_mistake_location": {
        "score_p_codes": ["P12"],
        "covered_p_codes": ["P02", "P11", "P12"],
    },
    "mathtutorbench_mistake_correction": {
        "score_p_codes": ["P13", "P18"],
        "covered_p_codes": ["P12", "P13", "P18"],
    },
    "mathtutorbench_scaffolding": {
        "score_p_codes": ["P17", "P18"],
        "covered_p_codes": ["P13", "P17", "P18"],
    },
    "mathtutorbench_scaffolding_hard": {
        "score_p_codes": ["P17", "P18"],
        "covered_p_codes": ["P13", "P17", "P18"],
    },
    "mathtutorbench_pedagogy": {
        "score_p_codes": ["P17", "P18"],
        "covered_p_codes": ["P05", "P17", "P18"],
    },
    "mathtutorbench_pedagogy_hard": {
        "score_p_codes": ["P17", "P18"],
        "covered_p_codes": ["P05", "P17", "P18"],
    },
    "mathtutorbench_socratic": {
        "score_p_codes": ["P17", "P18"],
        "covered_p_codes": ["P01", "P17", "P18"],
    },
    "mathtutorbench_judge_calibration": {
        "score_p_codes": ["P14"],
        "covered_p_codes": ["P14"],
    },
    "mmtutorbench": {
        "score_p_codes": ["P03", "P04", "P13", "P18"],
        "covered_p_codes": ["P03", "P04", "P05", "P06", "P13", "P18"],
    },
    "mmtutorbench_judge_calibration": {
        "score_p_codes": [],
        "covered_p_codes": ["P14"],
    },
    "eduguard_sata": {
        "score_p_codes": ["P20", "P21", "P22"],
        "covered_p_codes": ["P18", "P20", "P21", "P22"],
    },
    "eduguard_adversarial": {
        "score_p_codes": ["P20", "P22"],
        "covered_p_codes": ["P20", "P21", "P22"],
    },
    "mrbench_judge": {
        "score_p_codes": ["P14", "P18"],
        "covered_p_codes": ["P11", "P12", "P13", "P14", "P18"],
    },
    "mrbench_tutor": {
        "score_p_codes": ["P13", "P17", "P18"],
        "covered_p_codes": ["P11", "P12", "P13", "P17", "P18"],
    },
    "bea2025_judge": {
        "score_p_codes": ["P14", "P18"],
        "covered_p_codes": ["P12", "P13", "P14", "P18"],
    },
    "bea2025_tutor": {
        "score_p_codes": ["P13", "P17", "P18"],
        "covered_p_codes": ["P12", "P13", "P17", "P18"],
    },
    "eduillustrate": {
        "score_p_codes": ["P10"],
        "covered_p_codes": ["P03", "P05", "P06", "P10", "P18"],
    },
}


EXTRA_BENCHMARK_MAPPING_ROWS: list[dict[str, Any]] = [
    {
        "layer": "0701 task check",
        "benchmark": "Pedagogy Benchmark",
        "task": "CDPK 教学法知识选择",
        "score_p_codes": ["P05", "P06", "P17"],
        "covered_p_codes": ["P05", "P06", "P17"],
        "evidence_note": "教学法知识与策略选择；属于 Pedagogy aggregate 的子任务确认。",
    },
    {
        "layer": "0701 task check",
        "benchmark": "Pedagogy Benchmark",
        "task": "SEND 特殊教育需求选择",
        "score_p_codes": ["P05", "P16", "P17", "P18"],
        "covered_p_codes": ["P05", "P06", "P16", "P17", "P18"],
        "evidence_note": "特殊教育需求识别、策略选择和适配反馈。",
    },
    {
        "layer": "0701 task check",
        "benchmark": "EduBench",
        "task": "IP 启发式解答",
        "score_p_codes": ["P17", "P18"],
        "covered_p_codes": ["P05", "P06", "P17", "P18"],
        "evidence_note": "互动式教学/启发式解答，不等同于单纯解题正确率。",
    },
    {
        "layer": "0701 task check",
        "benchmark": "EduBench",
        "task": "PCC 个性化纠错",
        "score_p_codes": ["P11", "P12", "P13", "P17", "P18"],
        "covered_p_codes": ["P05", "P06", "P11", "P12", "P13", "P17", "P18"],
        "evidence_note": "纠错、错因归因与个性化反馈的组合任务。",
    },
    {
        "layer": "0701 task check",
        "benchmark": "EduBench",
        "task": "PLS 个性化学习支持",
        "score_p_codes": ["P16", "P17", "P18", "P19"],
        "covered_p_codes": ["P05", "P06", "P16", "P17", "P18", "P19"],
        "evidence_note": "学习者状态、策略选择、反馈与路径支持。",
    },
    {
        "layer": "0701 task check",
        "benchmark": "EduBench",
        "task": "TMG 教学材料生成",
        "score_p_codes": ["P10", "P18"],
        "covered_p_codes": ["P01", "P05", "P06", "P10", "P18"],
        "evidence_note": "教学材料生成与可读性约束，重点落在多模态/材料产物生成。",
    },
    {
        "layer": "0701 task check",
        "benchmark": "TutorBench",
        "task": "Fair815 多模态 tutoring",
        "score_p_codes": ["P03", "P06", "P13", "P17", "P18"],
        "covered_p_codes": ["P01", "P03", "P04", "P05", "P06", "P11", "P12", "P13", "P17", "P18", "P20"],
        "evidence_note": "多模态辅导质量，评价从看懂题面进入诊断和反馈。",
    },
]


def unique_codes(codes: list[str]) -> list[str]:
    return [code for code in P_TO_DIMENSION if code in set(codes)]


def mapping_score_codes(mapping_key: str, mapping: dict[str, Any]) -> list[str]:
    if mapping_key in ABILITY_CODE_OVERRIDES:
        return list(ABILITY_CODE_OVERRIDES[mapping_key]["score_p_codes"])
    if "score_p_codes" in mapping:
        return list(mapping["score_p_codes"])
    return list(mapping.get("primary_p_codes") or [])


def mapping_covered_codes(mapping_key: str, mapping: dict[str, Any]) -> list[str]:
    if mapping_key in ABILITY_CODE_OVERRIDES:
        return list(ABILITY_CODE_OVERRIDES[mapping_key]["covered_p_codes"])
    if "covered_p_codes" in mapping:
        return list(mapping["covered_p_codes"])
    return unique_codes(list(mapping.get("primary_p_codes") or []) + list(mapping.get("secondary_p_codes") or []))


def row_score_p_codes(row: dict[str, Any]) -> list[str]:
    return list(row.get("score_p_codes") or row.get("primary_p_codes") or [])


def row_covered_p_codes(row: dict[str, Any]) -> list[str]:
    if row.get("covered_p_codes"):
        return list(row["covered_p_codes"])
    return unique_codes(row_score_p_codes(row) + list(row.get("secondary_p_codes") or []))


def mapping_family_and_task(mapping_key: str, mapping: dict[str, Any]) -> tuple[str, str]:
    if "|" in mapping_key:
        family, task = mapping_key.split("|", 1)
    else:
        family, task = mapping_key, mapping.get("task", mapping_key)
    return str(mapping.get("benchmark", family)), str(mapping.get("task", task))


def main_row(
    benchmark: str,
    task: str,
    model: str,
    raw_metric: str,
    raw_value: float,
    scale: str,
    mapping_key: str,
    direction: str = "higher_is_better",
    score_role: str = "main",
) -> dict[str, Any]:
    if scale == "percent":
        normalized = raw_value / 100
        raw_display = f"{raw_value:.2f}%"
    elif scale == "ten":
        normalized = raw_value / 10
        raw_display = f"{raw_value:.3f}/10"
    elif scale == "inverse_percent":
        normalized = 1 - raw_value / 100
        raw_display = f"{raw_value:.1f}%"
    elif scale == "unit":
        normalized = raw_value
        raw_display = f"{raw_value:.4f}"
    else:
        raise ValueError(f"unknown scale: {scale}")
    mapping = CAPABILITY_MAPPINGS[mapping_key]
    score_p_codes = mapping_score_codes(mapping_key, mapping)
    covered_p_codes = mapping_covered_codes(mapping_key, mapping)
    row = {
        "source": MAIN_SOURCE,
        "benchmark": benchmark,
        "task": task,
        "model": normalize_model_name(model),
        "raw_metric": raw_metric,
        "raw_value": raw_display,
        "direction": direction,
        "normalized_score": max(0.0, min(1.0, normalized)),
        "mapping_key": mapping_key,
        "score_p_codes": score_p_codes,
        "covered_p_codes": covered_p_codes,
        "primary_p_codes": score_p_codes,
        "secondary_p_codes": [code for code in covered_p_codes if code not in set(score_p_codes)],
        "evidence_note": mapping["evidence_note"],
        "score_role": score_role,
    }
    return row


def build_main_results() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for model, value in [
        ("Qwen3.7-Max", 89.01),
        ("GLM-5.1", 87.67),
        ("DeepSeek-V4-Flash", 85.70),
        ("DeepSeek-V4-Pro", 85.34),
        ("Claude Sonnet 4.6", 84.90),
        ("GPT-5.4", 84.36),
        ("MiniMax-M2.7", 82.48),
    ]:
        rows.append(main_row("Pedagogy Benchmark", "Accuracy", model, "Accuracy", value, "percent", "Pedagogy Benchmark|Accuracy"))
    for model, value in [
        ("Claude Sonnet 4.6", 61.06),
        ("Qwen3.7-Max", 60.03),
        ("GLM-5.1", 57.25),
        ("MiniMax-M2.7", 52.77),
        ("DeepSeek-V4-Pro", 52.32),
        ("DeepSeek-V4-Flash", 50.78),
        ("GPT-5.4", 47.26),
    ]:
        rows.append(main_row("ASAP 2.0", "QWK", model, "QWK", value, "percent", "ASAP 2.0|QWK"))
    for model, value in [
        ("MiniMax-M2.7", 8.342),
        ("Qwen3.5-122B-A10B", 8.249),
        ("Doubao-Seed-2.0-Pro", 8.228),
        ("DeepSeek-V4-Flash", 8.154),
        ("Claude Sonnet 4.6", 8.112),
        ("MiniMax-M3", 8.069),
        ("Doubao-Seed-2.0-Lite", 8.037),
        ("DeepSeek-V4-Pro", 8.013),
        ("Kimi-K2.6", 7.901),
        ("GLM-5.1", 7.681),
        ("Qwen3-14B", 7.470),
    ]:
        rows.append(main_row("EduBench", "Mean", model, "Mean score", value, "ten", "EduBench|Mean"))
    for model, value in [
        ("GPT-5.5", 57.57),
        ("Qwen3.6-35B-A3B", 56.50),
        ("Qwen3.5-35B-A3B", 56.33),
        ("Qwen3.5-27B", 53.85),
        ("MiniMax-M3", 53.63),
        ("Qwen3-VL-235B", 50.79),
    ]:
        rows.append(main_row("TutorBench", "Fair815", model, "Fair815", value, "percent", "TutorBench|Fair815"))
    sas_values = [
        ("GPT-5.4", 86.77, 80.26, 55.64),
        ("MiniMax-M3", 84.30, 76.83, 66.02),
        ("GLM-5.1", 83.56, 78.14, 62.60),
        ("DeepSeek-V4-Pro", 81.86, 76.63, 61.69),
        ("Kimi-K2.6", 79.13, 73.30, 52.20),
        ("MiniMax-M2.7", 79.04, 72.46, 51.39),
    ]
    for model, qwk, ccs, ecs in sas_values:
        rows.append(main_row("SAS-Bench", "QWK", model, "QWK", qwk, "percent", "SAS-Bench|QWK"))
        rows.append(main_row("SAS-Bench", "CCS", model, "CCS", ccs, "percent", "SAS-Bench|CCS"))
        rows.append(main_row("SAS-Bench", "ECS", model, "ECS", ecs, "percent", "SAS-Bench|ECS"))
    for model, value in [
        ("MiniMax-M3", 76.94),
        ("GLM-5.1", 76.32),
        ("Doubao-Seed-2.0-Pro", 76.18),
        ("DeepSeek-V4-Pro", 76.12),
        ("GLM-5.2", 75.95),
        ("GPT-5.5 English subset", 73.95),
        ("Doubao-Seed-2.0-Lite", 73.00),
    ]:
        rows.append(main_row("EduGuard-Bench", "P1 Teaching Harm", model, "RFS", value, "percent", "EduGuard-Bench|P1 RFS"))
    for model, value in [
        ("MiniMax-M3", 3.5),
        ("GPT-5.5", 4.9),
        ("GLM-5.1", 9.5),
        ("GLM-5.2", 20.8),
        ("Doubao-Seed-2.0-Lite", 45.2),
        ("Doubao-Seed-2.0-Pro", 51.1),
        ("DeepSeek-V4-Pro", 57.1),
    ]:
        rows.append(
            main_row(
                "EduGuard-Bench",
                "P2 Adversarial Safety",
                model,
                "ASR",
                value,
                "inverse_percent",
                "EduGuard-Bench|P2 ASR",
                direction="lower_is_better",
            )
        )
    return rows


def parse_abilities(path: Path) -> list[dict[str, str]]:
    text = path.read_text(encoding="utf-8")
    pattern = re.compile(r"^- \*\*(P\d{2}) ([^*：]+)\*\*：(.+)$", re.MULTILINE)
    abilities: list[dict[str, str]] = []
    for code, name, desc in pattern.findall(text):
        dim = P_TO_DIMENSION.get(code)
        if not dim:
            continue
        abilities.append(
            {
                "code": code,
                "name": name.strip(),
                "definition": desc.strip(),
                "dimension": dim,
            }
        )
    expected = [f"P{i:02d}" for i in range(1, 23)]
    found = [item["code"] for item in abilities]
    if found != expected:
        raise SystemExit(f"{path} did not yield P01-P22 in order; found {found}")
    return abilities


def p_codes_by_dimension(abilities: list[dict[str, str]]) -> dict[str, list[str]]:
    grouped: dict[str, list[str]] = {dim: [] for dim in DIMENSIONS}
    for ability in abilities:
        grouped[ability["dimension"]].append(ability["code"])
    return grouped


def average(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def compute_main_scores(rows: list[dict[str, Any]], abilities: list[dict[str, str]]) -> dict[str, Any]:
    p_values: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    p_sources: dict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
    p_shared: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    model_benchmarks: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        if row["score_role"] != "main":
            continue
        model = row["model"]
        model_benchmarks[model].add(row["benchmark"])
        p_codes = row_score_p_codes(row)
        for code in p_codes:
            p_values[model][code].append(row["normalized_score"])
            p_sources[model][code].add(f"{row['benchmark']}:{row['task']}")
            if len(p_codes) > 1:
                p_shared[model][code] += 1

    p_scores: dict[str, dict[str, dict[str, Any]]] = {}
    for model, by_p in p_values.items():
        p_scores[model] = {}
        for code, values in by_p.items():
            p_scores[model][code] = {
                "score": average(values),
                "coverage_count": len(values),
                "sources": sorted(p_sources[model][code]),
                "shared_count": p_shared[model][code],
            }

    dim_codes = p_codes_by_dimension(abilities)
    dim_scores: dict[str, dict[str, dict[str, Any]]] = {}
    for model, by_p in p_scores.items():
        dim_scores[model] = {}
        for dim, codes in dim_codes.items():
            covered_scores = [by_p[code]["score"] for code in codes if code in by_p]
            covered_codes = [code for code in codes if code in by_p]
            dim_scores[model][dim] = {
                "score": average(covered_scores),
                "covered": len(covered_codes),
                "total": len(codes),
                "codes": covered_codes,
            }
    return {
        "p_scores": p_scores,
        "dimension_scores": dim_scores,
        "model_benchmarks": model_benchmarks,
    }


def model_is_minimax_m3(summary: dict[str, Any], path: Path) -> bool:
    model = str(summary.get("model", "")).lower()
    return model == "minimax-m3" or "minimax3" in path.parts or "minimax-m3" in path.name.lower()


def is_primary_minimax_m3_display(summary: dict[str, Any], rel_path: Path) -> bool:
    if not model_is_minimax_m3(summary, rel_path):
        return False
    if summary.get("benchmark") != "eduillustrate":
        return True
    judge = str(summary.get("judge_model", "")).lower()
    return judge == "minimax-m3" or rel_path.parent.name == "minimax3"


def is_historical_or_backup(path: Path) -> bool:
    skip_patterns = [
        re.compile(r"^\d{4}-\d{2}-\d{2}$"),
        re.compile(r"^selfjudge_backup_"),
    ]
    return any(any(pat.match(part) for pat in skip_patterns) for part in path.parts)


def load_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def summarize_repo_metric(summary: dict[str, Any]) -> tuple[str, str, float | None, str]:
    benchmark = str(summary.get("benchmark", ""))
    extra = summary.get("extra_metrics") or {}
    overall = extra.get("overall") or {}
    if benchmark == "eduguard_sata" and isinstance(overall.get("rfs"), (int, float)):
        return "RFS", f"{overall['rfs']:.4f}", float(overall["rfs"]), "higher_is_better"
    if benchmark == "eduguard_adversarial" and isinstance(overall.get("asr"), (int, float)):
        return "1-ASR", f"ASR={overall['asr']:.4f}", 1 - float(overall["asr"]), "lower_is_better"
    if benchmark == "eduillustrate":
        raw = summary.get("overall_mean_all_items")
        if isinstance(raw, (int, float)):
            return "overall_mean_all_items/5", f"{raw:.4f}/5", float(raw) / 5, "higher_is_better"
    if benchmark == "mmtutorbench":
        raw = extra.get("paper_weighted_score_0_to_6")
        if isinstance(raw, (int, float)):
            return "paper_weighted_score_0_to_6", f"{raw:.4f}/6", float(raw) / 6, "higher_is_better"
    if benchmark == "mathtutorbench_judge_calibration" and isinstance(extra.get("agreement"), (int, float)):
        return "agreement", f"{extra['agreement']:.4f}", float(extra["agreement"]), "higher_is_better"
    if benchmark.startswith("mathtutorbench_") and isinstance(extra.get("win_rate"), (int, float)):
        return "win_rate", f"{extra['win_rate']:.4f}", float(extra["win_rate"]), "higher_is_better"
    if benchmark == "bea2025_judge":
        macro = extra.get("macro_over_dimensions") or {}
        raw = macro.get("cohen_kappa")
        if isinstance(raw, (int, float)):
            return "cohen_kappa", f"{raw:.4f}", float(raw), "higher_is_better"
    if benchmark == "bea2025_tutor" and isinstance(extra.get("pass_rate"), (int, float)):
        return "pass_rate", f"{extra['pass_rate']:.4f}", float(extra["pass_rate"]), "higher_is_better"
    if benchmark == "mrbench_judge":
        macro = extra.get("macro_over_dimensions") or {}
        raw = macro.get("cohen_kappa")
        if isinstance(raw, (int, float)):
            return "cohen_kappa", f"{raw:.4f}", float(raw), "higher_is_better"
    if isinstance(summary.get("accuracy"), (int, float)):
        acc = float(summary["accuracy"])
        return "accuracy", f"{acc:.4f}", acc, "higher_is_better"
    return "n/a", "n/a", None, "higher_is_better"


def normalize_model_name(model: Any) -> str:
    raw = str(model or "").strip()
    key = raw.lower()
    exact_aliases = {
        "minimax3": "MiniMax-M3",
        "minimax-m3": "MiniMax-M3",
        "minimax-m2.7": "MiniMax-M2.7",
        "glm-5.1": "GLM-5.1",
        "glm-5.2": "GLM-5.2",
        "gpt-5.5": "GPT-5.5",
        "deepseek-v4-pro": "DeepSeek-V4-Pro",
        "deepseek-v4-flash": "DeepSeek-V4-Flash",
        "deepseek-v3.2": "DeepSeek-V3.2",
        "doubao-seed-2.0-pro": "Doubao-Seed-2.0-Pro",
        "doubao-seed-2.0-lite": "Doubao-Seed-2.0-Lite",
        "opus-4.8": "Opus-4.8",
    }
    if key in exact_aliases:
        return exact_aliases[key]
    if key.startswith("kimi-k2.7-code"):
        return "Kimi-K2.7-Code"
    return raw


def coerce_int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return None


def classify_summary_status(row: dict[str, Any]) -> str:
    total = coerce_int(row.get("total_items"))
    scored = coerce_int(row.get("scored"))
    if (
        row.get("score_role") == "coverage_gap"
        or row.get("normalized_score") is None
        or total is None
        or scored is None
        or total <= 0
    ):
        return "coverage_gap"
    if total < 20:
        return "smoke"
    if scored < total:
        return "partial"
    return "complete"


def score_eligible(row: dict[str, Any]) -> bool:
    """Whether a raw summary row can enter the MiniMax-M3 five-dimension profile."""
    if row.get("score_role") == "coverage_gap":
        return False
    if not row_score_p_codes(row):
        return False
    if row.get("normalized_score") is None:
        return False
    total = coerce_int(row.get("total_items"))
    scored = coerce_int(row.get("scored"))
    if total is None or scored is None or total < 20:
        return False
    return scored / total >= 0.95


def row_from_summary(path: Path, summary: dict[str, Any]) -> dict[str, Any] | None:
    rel = path.relative_to(ROOT)
    benchmark = str(summary.get("benchmark") or rel.parts[2])
    mapping = CAPABILITY_MAPPINGS.get(benchmark)
    if not mapping:
        return None
    score_p_codes = mapping_score_codes(benchmark, mapping)
    covered_p_codes = mapping_covered_codes(benchmark, mapping)
    metric, raw_display, normalized, direction = summarize_repo_metric(summary)
    extra = summary.get("extra_metrics") or {}
    row = {
        "source": str(rel),
        "benchmark": benchmark,
        "model": normalize_model_name(summary.get("model") or path.parent.name),
        "raw_metric": metric,
        "raw_value": raw_display,
        "direction": direction,
        "normalized_score": normalized,
        "scored": summary.get("scored", summary.get("judged")),
        "total_items": summary.get("total_items"),
        "score_p_codes": score_p_codes,
        "covered_p_codes": covered_p_codes,
        "primary_p_codes": score_p_codes,
        "secondary_p_codes": [code for code in covered_p_codes if code not in set(score_p_codes)],
        "evidence_note": mapping["evidence_note"],
        "score_role": mapping["score_role"],
        "judge_model": (
            summary.get("judge_model")
            or extra.get("judge_model")
            or summary.get("extractor_model")
            or extra.get("extractor_model")
            or extra.get("evaluation_model")
            or ""
        ),
    }
    row["status"] = classify_summary_status(row)
    row["score_eligible"] = score_eligible(row)
    return row


def collect_summary_rows(eval_dir: Path, *, minimax_m3_only: bool = False, primary_minimax_display: bool = False) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(eval_dir.glob("**/summary.json")):
        if path.parent.parent == eval_dir and (path.parent / "minimax3" / "summary.json").exists():
            continue
        rel = path.relative_to(ROOT)
        if is_historical_or_backup(rel):
            continue
        if any(part.startswith("_") for part in rel.parts[2:-1]):
            continue
        summary = load_json(path)
        if not summary:
            continue
        if minimax_m3_only and not model_is_minimax_m3(summary, rel):
            continue
        if primary_minimax_display and not is_primary_minimax_m3_display(summary, rel):
            continue
        row = row_from_summary(path, summary)
        if row:
            rows.append(row)
    rows.sort(key=lambda r: (r["benchmark"], r["source"]))
    return rows


def collect_minimax_m3_summaries(eval_dir: Path) -> list[dict[str, Any]]:
    return collect_summary_rows(eval_dir, minimax_m3_only=True, primary_minimax_display=True)


def compute_scores_from_rows(
    rows: list[dict[str, Any]],
    abilities: list[dict[str, str]],
    *,
    eligible_only: bool = True,
) -> dict[str, Any]:
    p_values: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    p_sources: dict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
    p_shared: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    model_benchmarks: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        if eligible_only and not row.get("score_eligible"):
            continue
        score = row.get("normalized_score")
        if not isinstance(score, (int, float)):
            continue
        model = str(row["model"])
        model_benchmarks[model].add(str(row["benchmark"]))
        p_codes = row_score_p_codes(row)
        for code in p_codes:
            p_values[model][code].append(float(score))
            p_sources[model][code].add(str(row["source"]))
            if len(p_codes) > 1:
                p_shared[model][code] += 1

    p_scores: dict[str, dict[str, dict[str, Any]]] = {}
    for model, by_p in p_values.items():
        p_scores[model] = {}
        for code, values in by_p.items():
            p_scores[model][code] = {
                "score": average(values),
                "coverage_count": len(values),
                "sources": sorted(p_sources[model][code]),
                "shared_count": p_shared[model][code],
            }

    dim_codes = p_codes_by_dimension(abilities)
    dim_scores: dict[str, dict[str, dict[str, Any]]] = {}
    for model, by_p in p_scores.items():
        dim_scores[model] = {}
        for dim, codes in dim_codes.items():
            covered_scores = [by_p[code]["score"] for code in codes if code in by_p]
            covered_codes = [code for code in codes if code in by_p]
            dim_scores[model][dim] = {
                "score": average(covered_scores),
                "covered": len(covered_codes),
                "total": len(codes),
                "codes": covered_codes,
                "missing": [code for code in codes if code not in by_p],
            }
    return {
        "p_scores": p_scores,
        "dimension_scores": dim_scores,
        "model_benchmarks": model_benchmarks,
    }


def esc(value: Any) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def fmt_score(value: float | None) -> str:
    return "—" if value is None else f"{value * 100:.1f}"


def fmt_percent(value: float | None) -> str:
    return "—" if value is None else f"{value * 100:.1f}%"


def render_bool(value: bool) -> str:
    return "yes" if value else "no"


def status_pill_class(status: str) -> str:
    if status == "complete":
        return "good"
    if status == "coverage_gap":
        return "gap"
    return "warn"


def eligible_pill_class(value: bool) -> str:
    return "good" if value else "gap"


def join_codes(codes: list[str]) -> str:
    return ", ".join(codes) if codes else "—"


def render_badges(codes: list[str], abilities_by_code: dict[str, dict[str, str]]) -> str:
    if not codes:
        return "<span class='muted'>—</span>"
    spans = []
    for code in codes:
        dim = abilities_by_code[code]["dimension"] if code in abilities_by_code else P_TO_DIMENSION.get(code, "")
        color = DIMENSIONS.get(dim, {}).get("color", "#64748b")
        title = abilities_by_code.get(code, {}).get("name", "")
        spans.append(f"<span class='p-badge' style='--c:{color}' title='{esc(title)}'>{esc(code)}</span>")
    return "".join(spans)


def score_dimensions(row: dict[str, Any]) -> list[str]:
    dims = {P_TO_DIMENSION[code] for code in row_score_p_codes(row) if code in P_TO_DIMENSION}
    return [dim for dim in DIMENSIONS if dim in dims]


def covered_dimensions(row: dict[str, Any]) -> list[str]:
    dims = {P_TO_DIMENSION[code] for code in row_covered_p_codes(row) if code in P_TO_DIMENSION}
    return [dim for dim in DIMENSIONS if dim in dims]


def render_radar_svg(selected_models: list[str], dimension_scores: dict[str, dict[str, dict[str, Any]]]) -> str:
    axes = list(DIMENSIONS)
    cx, cy, radius = 260.0, 245.0, 150.0
    min_value, max_value = 0.0, 1.0
    colors = ["#2563eb", "#dc2626", "#16a34a", "#7c3aed", "#0891b2", "#f97316", "#be123c", "#0f766e"]

    def point(axis_index: int, value: float) -> tuple[float, float]:
        angle = -math.pi / 2 + 2 * math.pi * axis_index / len(axes)
        scaled = (value - min_value) / (max_value - min_value)
        r = max(0.0, min(1.0, scaled)) * radius
        return cx + r * math.cos(angle), cy + r * math.sin(angle)

    parts = [
        "<svg class='radar-svg' viewBox='0 0 860 520' role='img' aria-label='SRG FDR LAD CLM CEG radar'>",
        "<rect x='0' y='0' width='860' height='520' rx='8' fill='#fff'/>",
        "<text x='28' y='36' class='radar-title'>SRG / FDR / LAD / CLM / CEG</text>",
        "<text x='28' y='58' class='radar-subtitle'>Raw summary evidence aggregated by P capability; missing axes stay near center</text>",
    ]
    for tick in [0.2, 0.4, 0.6, 0.8, 1.0]:
        pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in [point(i, tick) for i in range(len(axes))])
        parts.append(f"<polygon points='{pts}' class='radar-ring'/>")
        tx, ty = point(0, tick)
        parts.append(f"<text x='{tx + 6:.1f}' y='{ty + 3:.1f}' class='radar-tick'>{int(tick * 100)}</text>")
    for i, dim in enumerate(axes):
        x, y = point(i, 1.0)
        parts.append(f"<line x1='{cx}' y1='{cy}' x2='{x:.1f}' y2='{y:.1f}' class='radar-axis'/>")
        lx, ly = point(i, 1.16)
        anchor = "middle"
        if lx > cx + 20:
            anchor = "start"
        elif lx < cx - 20:
            anchor = "end"
        parts.append(
            f"<text x='{lx:.1f}' y='{ly:.1f}' text-anchor='{anchor}' class='radar-label'>"
            f"<tspan>{esc(dim)}</tspan><tspan x='{lx:.1f}' dy='14'>{esc(DIMENSIONS[dim]['zh'][:4])}</tspan></text>"
        )
    for model_index, model in enumerate(selected_models):
        color = colors[model_index % len(colors)]
        values = []
        missing = 0
        for dim in axes:
            score = dimension_scores.get(model, {}).get(dim, {}).get("score")
            if score is None:
                missing += 1
                score = 0.02
            values.append(float(score))
        pts_list = [point(i, values[i]) for i in range(len(axes))]
        pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts_list)
        dash = " stroke-dasharray='5 4'" if missing else ""
        parts.append(
            f"<polygon points='{pts}' fill='{color}' fill-opacity='0.055' stroke='{color}' "
            f"stroke-width='1.8'{dash}/>"
        )
        for x, y in pts_list:
            parts.append(f"<circle cx='{x:.1f}' cy='{y:.1f}' r='2.5' fill='{color}'/>")
        legend_y = 110 + 24 * model_index
        parts.append(f"<rect x='600' y='{legend_y}' width='11' height='11' rx='3' fill='{color}'/>")
        parts.append(f"<text x='618' y='{legend_y + 10}' class='radar-legend'>{esc(model)}</text>")
    parts.append("</svg>")
    return "\n".join(parts)


def pill_strength(count: int, total: int) -> str:
    if total and count / total >= 0.65:
        return "strong"
    if total and count / total >= 0.30:
        return "medium"
    return "weak"


def reference_task_label(row: dict[str, Any]) -> str:
    return f"{row['benchmark']} · {row.get('task', row.get('raw_metric', ''))}"


def render_reference_coverage(reference_rows: list[dict[str, Any]]) -> str:
    benchmarks = sorted({row["benchmark"] for row in reference_rows})
    models = sorted({row["model"] for row in reference_rows})
    by_model: dict[str, set[str]] = defaultdict(set)
    for row in reference_rows:
        by_model[row["model"]].add(row["benchmark"])
    parts = [
        "<div class='table-wrap'><table class='coverage'><thead><tr><th>模型</th>",
        *(f"<th>{esc(benchmark)}</th>" for benchmark in benchmarks),
        "<th>覆盖</th></tr></thead><tbody>",
    ]
    for model in models:
        covered = by_model[model]
        parts.append(f"<tr><th>{esc(model)}</th>")
        for benchmark in benchmarks:
            if benchmark in covered:
                parts.append(f"<td class='hit' title='{esc(model)} - {esc(benchmark)} covered'>●</td>")
            else:
                parts.append(f"<td class='miss' title='{esc(model)} - {esc(benchmark)} not covered'>·</td>")
        parts.append(
            f"<td><span class='pill {pill_strength(len(covered), len(benchmarks))}'>"
            f"{len(covered)}/{len(benchmarks)}</span></td></tr>"
        )
    parts.append("</tbody></table></div>")
    return "".join(parts)


def render_reference_capability_matrix(
    reference_rows: list[dict[str, Any]],
    abilities: list[dict[str, str]],
) -> str:
    codes = [ability["code"] for ability in abilities]
    models = sorted({row["model"] for row in reference_rows})
    by_model: dict[str, set[str]] = defaultdict(set)
    for row in reference_rows:
        by_model[row["model"]].update(row_covered_p_codes(row))
    parts = ["<div class='table-wrap'><table class='sub-matrix model-sub-matrix'><thead><tr><th>Model</th>"]
    for ability in abilities:
        dim = ability["dimension"].lower()
        parts.append(
            f"<th class='sub-head {esc(dim)}' title='{esc(ability['code'])} {esc(ability['name'])}'>"
            f"{esc(ability['code'])}</th>"
        )
    parts.append("<th>覆盖</th></tr></thead><tbody>")
    for model in models:
        covered = by_model[model]
        parts.append(f"<tr><th>{esc(model)}</th>")
        for code in codes:
            dim = P_TO_DIMENSION[code].lower()
            if code in covered:
                parts.append(f"<td class='sub-hit {esc(dim)}' title='{esc(model)} tested on {esc(code)}'>●</td>")
            else:
                parts.append("<td class='sub-miss'>·</td>")
        parts.append(
            f"<td><span class='pill {pill_strength(len(covered), len(codes))}'>"
            f"{len(covered)}/{len(codes)}</span></td></tr>"
        )
    parts.append("</tbody></table></div>")
    return "".join(parts)


def build_benchmark_mapping_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for mapping_key, mapping in CAPABILITY_MAPPINGS.items():
        benchmark, task = mapping_family_and_task(mapping_key, mapping)
        if mapping.get("score_role") == "main":
            layer = "0701 score row"
        elif mapping.get("score_role") == "coverage_gap":
            layer = "repo gap"
        else:
            layer = "repo summary"
        score_codes = mapping_score_codes(mapping_key, mapping)
        covered_codes = mapping_covered_codes(mapping_key, mapping)
        rows.append(
            {
                "layer": layer,
                "benchmark": benchmark,
                "task": task,
                "score_p_codes": score_codes,
                "covered_p_codes": covered_codes,
                "evidence_note": mapping.get("evidence_note", ""),
            }
        )
    rows.extend(EXTRA_BENCHMARK_MAPPING_ROWS)
    rows.sort(key=lambda row: (row["layer"], row["benchmark"], row["task"]))
    return rows


def render_benchmark_capability_matrix(
    mapping_rows: list[dict[str, Any]],
    abilities: list[dict[str, str]],
    abilities_by_code: dict[str, dict[str, str]],
) -> str:
    parts = [
        "<div class='table-wrap'><table class='sub-matrix benchmark-p-matrix'><thead><tr>"
        "<th>Layer</th><th>Benchmark</th><th>Task / score row</th>"
    ]
    for ability in abilities:
        dim = ability["dimension"].lower()
        parts.append(
            f"<th class='sub-head {esc(dim)}' title='{esc(ability['code'])} {esc(ability['name'])}'>"
            f"{esc(ability['code'])}</th>"
        )
    parts.append("<th>Score P</th><th>Covered P</th><th>确认说明</th></tr></thead><tbody>")
    for row in mapping_rows:
        score_codes = set(row.get("score_p_codes") or [])
        covered_codes = set(row.get("covered_p_codes") or [])
        parts.append(
            f"<tr><td class='nowrap'><span class='pill'>{esc(row['layer'])}</span></td>"
            f"<th>{esc(row['benchmark'])}</th><td>{esc(row['task'])}</td>"
        )
        for ability in abilities:
            code = ability["code"]
            dim = ability["dimension"].lower()
            if code in score_codes:
                parts.append(
                    f"<td class='matrix-score {esc(dim)}' title='{esc(row['benchmark'])} · {esc(row['task'])} scores {esc(code)}'>●</td>"
                )
            elif code in covered_codes:
                parts.append(
                    f"<td class='matrix-support {esc(dim)}' title='{esc(row['benchmark'])} · {esc(row['task'])} covers {esc(code)}'>○</td>"
                )
            else:
                parts.append("<td class='sub-miss'>·</td>")
        parts.append(
            f"<td>{render_badges(list(row.get('score_p_codes') or []), abilities_by_code)}</td>"
            f"<td>{render_badges(list(row.get('covered_p_codes') or []), abilities_by_code)}</td>"
            f"<td>{esc(row.get('evidence_note', ''))}</td></tr>"
        )
    parts.append("</tbody></table></div>")
    parts.append(
        "<div class='legend' style='margin-top:10px'>"
        "<span>● 分数主要解释为该 P 的证据</span>"
        "<span>○ 任务覆盖或依赖该 P，但该行分数不直接计入该 P</span>"
        "<span>· 未确认覆盖</span>"
        "</div>"
    )
    return "".join(parts)


def render_reference_benchmark_dashboard(reference_rows: list[dict[str, Any]]) -> str:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in reference_rows:
        grouped[(row["benchmark"], row["task"])].append(row)
    cards = []
    for (benchmark, task), rows in sorted(grouped.items()):
        rows = sorted(rows, key=lambda item: item["normalized_score"], reverse=True)
        max_score = max((float(row["normalized_score"]) for row in rows), default=1.0) or 1.0
        cls = {
            "Pedagogy Benchmark": "pedagogy",
            "ASAP 2.0": "asap",
            "EduBench": "edubench",
            "TutorBench": "tutor",
            "SAS-Bench": "asap",
            "EduGuard-Bench": "safe",
        }.get(benchmark, "")
        card = [f"<div class='card'><h3>{esc(benchmark)} · {esc(task)}</h3>"]
        for row in rows:
            width = max(2.0, float(row["normalized_score"]) / max_score * 100)
            metric = f"{row['raw_metric']}: {row['raw_value']}"
            card.append(
                f"<div class='bar-row {esc(cls)}'><div class='bar-label' title='{esc(row['model'])}'>"
                f"{esc(row['model'])}</div><div class='bar-track'><div class='bar-fill' "
                f"style='width:{width:.1f}%'></div></div><div class='bar-value' title='{esc(metric)}'>"
                f"{fmt_score(row['normalized_score'])}</div></div>"
            )
        card.append("</div>")
        cards.append("".join(card))
    return "<div class='grid-2'>" + "".join(cards) + "</div>"


def chart_source_label(row: dict[str, Any]) -> str:
    source = str(row.get("source", ""))
    if source == MAIN_SOURCE:
        return "tempt"
    if source.startswith("reports/eval/"):
        return "repo"
    return "data"


def chart_row_label(row: dict[str, Any]) -> str:
    task = row.get("task")
    benchmark = row.get("benchmark", "")
    if task:
        return f"{benchmark} · {task}"
    return str(benchmark)


def render_benchmark_bar_chart(rows: list[dict[str, Any]], *, show_model: bool = False) -> str:
    rows = [row for row in rows if isinstance(row.get("normalized_score"), (int, float))]
    rows.sort(
        key=lambda row: (
            chart_source_label(row),
            chart_row_label(row),
            str(row.get("model", "")),
            -float(row["normalized_score"]),
        )
    )
    if not rows:
        return "<div class='note'>暂无可展示的 benchmark 分数。</div>"
    max_score = max(float(row["normalized_score"]) for row in rows) or 1.0
    parts = ["<div class='card'>"]
    for row in rows:
        width = max(2.0, float(row["normalized_score"]) / max_score * 100)
        label = chart_row_label(row)
        if show_model:
            label = f"{label} · {row.get('model', '')}"
        metric = f"{row.get('raw_metric', '')}: {row.get('raw_value', '')}"
        parts.append(
            f"<div class='bar-row'><div class='bar-label' title='{esc(label)}'>"
            f"<span class='pill'>{esc(chart_source_label(row))}</span> {esc(label)}</div>"
            f"<div class='bar-track'><div class='bar-fill' style='width:{width:.1f}%'></div></div>"
            f"<div class='bar-value' title='{esc(metric)}'>{fmt_score(row.get('normalized_score'))}</div></div>"
        )
    parts.append("</div>")
    return "".join(parts)


def render_dimension_model_benchmark_charts(
    rows: list[dict[str, Any]],
    dim: str,
) -> str:
    dim_rows = [
        row
        for row in rows
        if any(P_TO_DIMENSION.get(code) == dim for code in row_score_p_codes(row))
        and isinstance(row.get("normalized_score"), (int, float))
    ]
    if not dim_rows:
        return "<div class='note'>暂无相关 benchmark 结果。</div>"
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in dim_rows:
        grouped[chart_row_label(row)].append(row)
    cards = []
    for label, group in sorted(grouped.items()):
        group.sort(key=lambda row: float(row["normalized_score"]), reverse=True)
        max_score = max(float(row["normalized_score"]) for row in group) or 1.0
        card = [f"<div class='card'><h3>{esc(label)}</h3>"]
        for row in group:
            width = max(2.0, float(row["normalized_score"]) / max_score * 100)
            model = str(row.get("model", ""))
            metric = f"{row.get('raw_metric', '')}: {row.get('raw_value', '')}"
            card.append(
                f"<div class='bar-row'><div class='bar-label' title='{esc(model)}'>"
                f"<span class='pill'>{esc(chart_source_label(row))}</span> {esc(model)}</div>"
                f"<div class='bar-track'><div class='bar-fill' style='width:{width:.1f}%'></div></div>"
                f"<div class='bar-value' title='{esc(metric)}'>{fmt_score(row.get('normalized_score'))}</div></div>"
            )
        card.append("</div>")
        cards.append("".join(card))
    return "<div class='grid-2'>" + "".join(cards) + "</div>"


def compute_dimension_model_capability_summary(
    rows: list[dict[str, Any]],
    dim: str,
    dim_codes: dict[str, list[str]],
) -> list[dict[str, Any]]:
    model_data: dict[str, dict[str, Any]] = defaultdict(
        lambda: {
            "p_values": defaultdict(list),
            "benchmarks": set(),
            "evidence_rows": 0,
        }
    )
    for row in rows:
        score = row.get("normalized_score")
        if not isinstance(score, (int, float)):
            continue
        score_codes = [code for code in row_score_p_codes(row) if P_TO_DIMENSION.get(code) == dim]
        if not score_codes:
            continue
        model = str(row.get("model", ""))
        model_data[model]["benchmarks"].add(chart_row_label(row))
        model_data[model]["evidence_rows"] += 1
        for code in score_codes:
            model_data[model]["p_values"][code].append(float(score))

    summaries: list[dict[str, Any]] = []
    for model, data in model_data.items():
        p_scores = {
            code: average(values)
            for code, values in data["p_values"].items()
            if values
        }
        covered = [code for code in dim_codes[dim] if code in p_scores]
        missing = [code for code in dim_codes[dim] if code not in p_scores]
        score = average([float(p_scores[code]) for code in covered])
        weak = [code for code in covered if p_scores[code] is not None and float(p_scores[code]) < 0.60]
        summaries.append(
            {
                "model": model,
                "score": score,
                "p_scores": p_scores,
                "covered": covered,
                "missing": missing,
                "weak": weak,
                "benchmarks": sorted(data["benchmarks"]),
                "evidence_rows": data["evidence_rows"],
            }
        )
    summaries.sort(
        key=lambda item: (
            -len(item["covered"]),
            -(item["score"] or 0),
            -item["evidence_rows"],
            item["model"],
        )
    )
    return summaries


def render_dimension_analysis(
    rows: list[dict[str, Any]],
    dim: str,
    dim_codes: dict[str, list[str]],
    abilities_by_code: dict[str, dict[str, str]],
) -> str:
    summaries = compute_dimension_model_capability_summary(rows, dim, dim_codes)
    if not summaries:
        return "<div class='note'>暂无可分析的模型结果。</div>"

    ranked = [item for item in summaries if item["score"] is not None]
    top_text = "暂无"
    supported = [
        item
        for item in ranked
        if len(item["covered"]) >= max(2, len(dim_codes[dim]) // 2) or item["evidence_rows"] >= 2
    ]
    if supported:
        top_text = "；".join(
            f"{item['model']} {fmt_score(item['score'])}（{len(item['covered'])}/{len(dim_codes[dim])} P）"
            for item in supported[:4]
        )
    elif ranked:
        top_text = "证据较薄，仅能按单项结果展示：" + "；".join(
            f"{item['model']} {fmt_score(item['score'])}（{len(item['covered'])}/{len(dim_codes[dim])} P）"
            for item in ranked[:4]
        )
    weak_models = [
        item
        for item in ranked
        if ((item["score"] or 0) < 0.60 or item["weak"])
        and (item["evidence_rows"] >= 2 or len(item["covered"]) >= 2)
    ]
    if weak_models:
        weak_text = "；".join(
            f"{item['model']}：{fmt_score(item['score'])}，短板 {join_codes(item['weak'] or item['missing'])}"
            for item in weak_models[:5]
        )
    else:
        tail = ranked[-3:] if len(ranked) >= 3 else ranked
        weak_text = "没有维度均分低于 60 的模型；当前更大的风险是证据覆盖窄。尾部模型：" + "；".join(
            f"{item['model']} {fmt_score(item['score'])}" for item in tail
        )

    coverage_counts: dict[str, int] = {code: 0 for code in dim_codes[dim]}
    for item in summaries:
        for code in item["covered"]:
            coverage_counts[code] += 1
    zero_coverage = [code for code, count in coverage_counts.items() if count == 0]
    thin_coverage = [code for code, count in coverage_counts.items() if 0 < count <= 2]
    coverage_text = "覆盖较均衡。"
    if zero_coverage:
        coverage_text = f"当前没有直接分数证据的 P：{join_codes(zero_coverage)}。"
    elif thin_coverage:
        coverage_text = f"证据较薄的 P：{join_codes(thin_coverage)}。"

    parts = ["<div class='grid-3 analysis-cards'>"]
    for title, body in [
        ("总体表现", top_text),
        ("低分与短板", weak_text),
        ("能力覆盖", coverage_text),
    ]:
        parts.append(f"<div class='card'><h3>{esc(title)}</h3><p>{esc(body)}</p></div>")
    parts.append("</div>")

    parts.append(
        "<div class='table-wrap' style='margin-top:14px'><table><thead><tr>"
        "<th>Model</th><th>Dimension score</th><th>Evidence rows</th><th>Covered P</th>"
        "<th>Weak P & score</th><th>Benchmark evidence</th></tr></thead><tbody>"
    )
    for item in summaries:
        weak_cells = []
        for code in item["weak"]:
            weak_cells.append(f"{code} {fmt_score(item['p_scores'].get(code))}")
        if not weak_cells:
            weak_cells = [f"缺证据 {join_codes(item['missing'])}" if item["missing"] else "—"]
        parts.append(
            f"<tr><td>{esc(item['model'])}</td><td class='num'>{fmt_score(item['score'])}</td>"
            f"<td class='num'>{item['evidence_rows']}</td>"
            f"<td>{render_badges(item['covered'], abilities_by_code)}</td>"
            f"<td>{esc('；'.join(weak_cells))}</td>"
            f"<td>{esc('；'.join(item['benchmarks'][:8]))}</td></tr>"
        )
    parts.append("</tbody></table></div>")
    return "".join(parts)


def select_reference_radar_models(reference_scores: dict[str, Any]) -> list[str]:
    dimension_scores = reference_scores["dimension_scores"]
    model_benchmarks = reference_scores["model_benchmarks"]
    selected = [
        model
        for model, dims in sorted(dimension_scores.items())
        if len(model_benchmarks.get(model, set())) >= 3 and sum(1 for item in dims.values() if item["score"] is not None) >= 4
    ]
    return sorted(selected, key=lambda model: (model != "MiniMax-M3", model))[:10]


def render_dimension_score_table(
    selected_models: list[str],
    dimension_scores: dict[str, dict[str, dict[str, Any]]],
    dim_codes: dict[str, list[str]],
) -> str:
    parts = ["<div class='table-wrap'><table class='score-table'><thead><tr><th>Model</th>"]
    for dim in DIMENSIONS:
        parts.append(f"<th>{esc(dim)}</th><th>Cov</th>")
    parts.append("</tr></thead><tbody>")
    for model in selected_models:
        parts.append(f"<tr><td>{esc(model)}</td>")
        for dim in DIMENSIONS:
            item = dimension_scores.get(model, {}).get(dim, {})
            parts.append(
                f"<td class='num'>{fmt_score(item.get('score'))}</td>"
                f"<td class='nowrap'>{item.get('covered', 0)}/{item.get('total', len(dim_codes[dim]))}</td>"
            )
        parts.append("</tr>")
    parts.append("</tbody></table></div>")
    return "".join(parts)


def render_raw_summary_table(rows: list[dict[str, Any]], abilities_by_code: dict[str, dict[str, str]]) -> str:
    parts = [
        "<div class='table-wrap'><table><thead><tr><th>Benchmark</th><th>Model</th><th>Source</th>"
        "<th>Metric</th><th>Norm</th><th>Scored/Total</th><th>Status</th><th>Eligible</th>"
        "<th>Primary P</th><th>Judge / extractor</th><th>Note</th></tr></thead><tbody>"
    ]
    for row in rows:
        status_class = status_pill_class(row["status"])
        eligible_class = eligible_pill_class(bool(row["score_eligible"]))
        parts.append(
            f"<tr><td>{esc(row['benchmark'])}</td><td>{esc(row['model'])}</td>"
            f"<td class='source'>{esc(row['source'])}</td>"
            f"<td>{esc(row['raw_metric'])}: {esc(row['raw_value'])}</td>"
            f"<td class='num'>{fmt_score(row['normalized_score'])}</td>"
            f"<td class='nowrap'>{esc(row['scored'])}/{esc(row['total_items'])}</td>"
            f"<td><span class='pill {status_class}'>{esc(row['status'])}</span></td>"
            f"<td><span class='pill {eligible_class}'>{render_bool(bool(row['score_eligible']))}</span></td>"
            f"<td>{render_badges(row_score_p_codes(row), abilities_by_code)}</td>"
            f"<td>{esc(row['judge_model'])}</td><td>{esc(row['evidence_note'])}</td></tr>"
        )
    parts.append("</tbody></table></div>")
    return "".join(parts)


def render_html(
    abilities: list[dict[str, str]],
    reference_rows: list[dict[str, Any]],
    minimax_rows: list[dict[str, Any]],
    all_repo_rows: list[dict[str, Any]],
    raw_scores: dict[str, Any],
    reference_scores: dict[str, Any],
    raw_all_scores: dict[str, Any],
) -> str:
    abilities_by_code = {item["code"]: item for item in abilities}
    dim_codes = p_codes_by_dimension(abilities)
    dimension_scores = raw_scores["dimension_scores"]
    selected_models = ["MiniMax-M3"] if "MiniMax-M3" in dimension_scores else sorted(dimension_scores)[:1]

    mapping_rows = build_benchmark_mapping_rows()
    reference_families = sorted({row["benchmark"] for row in reference_rows})
    reference_model_count = len({row["model"] for row in reference_rows})
    eligible_minimax_rows = [row for row in minimax_rows if row.get("score_eligible")]
    raw_benchmarks = sorted({row["benchmark"] for row in all_repo_rows})
    minimax_combined_rows = [
        row for row in reference_rows if str(row.get("model", "")).lower() == "minimax-m3"
    ] + minimax_rows
    combined_rows = reference_rows + all_repo_rows
    clm_ceg_rows = [
        row
        for row in combined_rows
        if any(dim in {"CLM", "CEG"} for dim in score_dimensions(row))
    ]
    clm_ceg_rows.sort(
        key=lambda row: (
            ",".join(score_dimensions(row)),
            row["benchmark"],
            str(row["model"]),
            row["source"],
        )
    )

    css = """
:root {
  --paper:#fbf5e8; --ink:#14213d; --muted:#657084; --line:#dfd4bf; --card:#fffaf0;
  --teal:#0f766e; --blue:#2F80ED; --orange:#F2994A; --green:#27AE60; --purple:#9B51E0; --red:#EB5757;
  --shadow:0 18px 50px rgba(20,33,61,.09);
}
*{box-sizing:border-box}
body{margin:0;background:linear-gradient(135deg,#fff9ec 0%,#f8f0df 48%,#eef6f3 100%);color:var(--ink);font:14px/1.58 "Avenir Next","PingFang SC","Hiragino Sans GB","Microsoft YaHei",Arial,sans-serif}
a{color:inherit}.page{width:min(1440px,94vw);margin:0 auto;padding:36px 0 80px}
.hero{padding:42px;border:1px solid rgba(20,33,61,.12);border-radius:24px;background:rgba(255,250,240,.82);box-shadow:var(--shadow)}
.eyebrow{margin:0 0 12px;text-transform:uppercase;letter-spacing:.18em;font-size:12px;font-weight:800;color:var(--teal)}
h1{font-family:"Optima","Palatino Linotype","Songti SC",Georgia,serif;font-size:clamp(30px,3.8vw,56px);line-height:1.03;margin:0 0 18px;max-width:1120px}
.hero-sub{font-size:18px;color:#3c485c;max-width:1040px;margin:0 0 24px}
.kpis{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px;margin-top:24px}
.kpi{padding:18px;border-radius:16px;background:rgba(255,255,255,.70);border:1px solid rgba(20,33,61,.10)}
.kpi b{display:block;font-size:33px;line-height:1;color:var(--ink)}.kpi span{font-size:13px;color:var(--muted)}
section{margin-top:26px;padding:26px;border:1px solid rgba(20,33,61,.11);border-radius:22px;background:rgba(255,250,240,.74);box-shadow:0 12px 32px rgba(20,33,61,.06)}
.section-head{display:flex;align-items:flex-end;justify-content:space-between;gap:22px;margin-bottom:18px}
h2{font-family:"Optima","Palatino Linotype","Songti SC",Georgia,serif;font-size:29px;line-height:1.14;margin:0}
.lede{margin:6px 0 0;color:var(--muted);max-width:900px}
.grid-2{display:grid;grid-template-columns:1fr 1fr;gap:18px}.grid-3{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}
.card{padding:18px;border-radius:16px;background:rgba(255,255,255,.72);border:1px solid rgba(20,33,61,.10)}
.card h3{margin:0 0 12px;font-size:17px}.card p{margin:0;color:#3f4c61}
.ability-grid{display:grid;grid-template-columns:repeat(5,1fr);gap:13px}
.ability-card{padding:18px;border-radius:16px;background:linear-gradient(180deg,rgba(255,255,255,.88),rgba(255,255,255,.58));border:1px solid rgba(20,33,61,.10);border-top:5px solid var(--c)}
.ability-code{display:inline-flex;align-items:center;justify-content:center;min-width:52px;height:44px;border-radius:12px;color:#fff;background:var(--c);font-weight:900;font-size:19px}
.ability-card h3{font-size:16px;margin:12px 0 2px}.ability-card .en{font-size:11px;color:var(--c);font-weight:800}.ability-card p{font-size:12px;margin:8px 0 0;color:#475569}
.table-wrap{overflow:auto;border-radius:14px;border:1px solid rgba(20,33,61,.10);background:rgba(255,255,255,.62)}
table{width:100%;border-collapse:collapse;font-size:12.5px}th,td{padding:9px 10px;border-bottom:1px solid rgba(20,33,61,.09);text-align:left;vertical-align:middle}thead th{position:sticky;top:0;background:#f6ead2;z-index:1;color:#2e3a50}tbody tr:hover td{background:rgba(47,128,237,.05)}
.num{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}.nowrap{white-space:nowrap}.source{word-break:break-all;min-width:220px}.muted{color:var(--muted)}
.p-badge,.cap-badge{display:inline-flex;align-items:center;justify-content:center;min-width:38px;margin:1px 3px 1px 0;padding:3px 7px;border-radius:999px;background:var(--c);color:#fff;font-size:11px;font-weight:900}
.pill{display:inline-block;border-radius:999px;padding:3px 8px;background:#e2e8f0;color:#334155;font-weight:800;font-size:11px;white-space:nowrap}.pill.warn,.pill.medium{background:#fff0c9;color:#8a5a00}.pill.good,.pill.strong{background:#dff4eb;color:#0d6b44}.pill.gap,.pill.weak{background:#fee2e2;color:#991b1b}
.note{border-left:5px solid var(--teal);background:rgba(15,118,110,.08);border-radius:12px;padding:13px 15px;color:#304159}
.coverage td{text-align:center;font-size:20px;font-weight:900}.coverage .hit{color:#0f766e;background:rgba(15,118,110,.07)}.coverage .miss{color:#d2c6b4}.coverage th:first-child{white-space:nowrap}
.sub-matrix{table-layout:auto;width:max-content;min-width:100%}.sub-matrix th,.sub-matrix td{text-align:center;white-space:nowrap;padding:8px 9px}.sub-matrix th:first-child,.sub-matrix td:first-child{text-align:left}
.sub-head{font-size:11px;writing-mode:vertical-rl;text-orientation:mixed;line-height:1.1;padding:10px 5px!important}.sub-hit{font-size:16px;font-weight:900}.sub-miss{color:#d6cbb8}
.sub-hit.srg{color:var(--blue)}.sub-hit.fdr{color:var(--orange)}.sub-hit.lad{color:var(--green)}.sub-hit.clm{color:var(--purple)}.sub-hit.ceg{color:var(--red)}
.sub-head.srg{background:rgba(47,128,237,.12)}.sub-head.fdr{background:rgba(242,153,74,.14)}.sub-head.lad{background:rgba(39,174,96,.13)}.sub-head.clm{background:rgba(155,81,224,.12)}.sub-head.ceg{background:rgba(235,87,87,.12)}
.benchmark-p-matrix th:nth-child(2),.benchmark-p-matrix td:nth-child(3){min-width:150px;text-align:left}.matrix-score,.matrix-support{font-size:16px;font-weight:900;text-align:center}.matrix-score.srg,.matrix-support.srg{color:var(--blue)}.matrix-score.fdr,.matrix-support.fdr{color:var(--orange)}.matrix-score.lad,.matrix-support.lad{color:var(--green)}.matrix-score.clm,.matrix-support.clm{color:var(--purple)}.matrix-score.ceg,.matrix-support.ceg{color:var(--red)}.matrix-support{opacity:.58}.legend{display:flex;flex-wrap:wrap;gap:12px;color:var(--muted);font-size:12px}.analysis-cards .card p{font-size:13px}
.bar-row{display:grid;grid-template-columns:minmax(150px,230px) 1fr 62px;gap:10px;align-items:center;margin:9px 0}.bar-label{font-size:13px;color:#25324a;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.bar-track{height:13px;border-radius:999px;background:#eadfc9;overflow:hidden}.bar-fill{height:100%;border-radius:999px;background:linear-gradient(90deg,var(--blue),#00a6a6)}.bar-value{font-variant-numeric:tabular-nums;font-weight:800;text-align:right}
.edubench .bar-fill{background:linear-gradient(90deg,#0f766e,#27AE60)}.asap .bar-fill{background:linear-gradient(90deg,#9B51E0,#2F80ED)}.pedagogy .bar-fill{background:linear-gradient(90deg,#F2994A,#EB5757)}.tutor .bar-fill{background:linear-gradient(90deg,#2F80ED,#9B51E0)}.safe .bar-fill{background:linear-gradient(90deg,#27AE60,#0f766e)}
.radar-grid{display:grid;grid-template-columns:minmax(0,1.08fr) minmax(390px,.92fr);gap:16px}.radar-card{padding:8px;overflow:auto;background:#fff;border:1px solid rgba(20,33,61,.10);border-radius:18px}.radar-svg{width:100%;min-width:680px;height:auto;display:block}.radar-ring{fill:none;stroke:#d9dfe8;stroke-width:1}.radar-axis{stroke:#e3e7ef;stroke-width:1}.radar-title{font:800 18px Georgia,"Songti SC",serif;fill:#14213d}.radar-subtitle,.radar-tick{font-size:10px;fill:#657084}.radar-label{font-size:11px;font-weight:800;fill:#172033}.radar-legend{font-size:10px;font-weight:720;fill:#2f3b52}
.score-table td,.score-table th{text-align:right}.score-table td:first-child,.score-table th:first-child{text-align:left;white-space:nowrap}
.plan-list{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}.plan-item{background:rgba(255,255,255,.72);border:1px solid rgba(20,33,61,.10);border-radius:16px;padding:14px}.plan-item b{display:block;margin-bottom:6px}.footer{margin-top:24px;color:var(--muted);font-size:12px;text-align:center}
@media(max-width:1100px){.kpis,.ability-grid,.grid-3,.plan-list{grid-template-columns:repeat(2,1fr)}.grid-2,.radar-grid{grid-template-columns:1fr}}
@media(max-width:700px){.page{width:96vw;padding-top:14px}.hero,section{padding:20px;border-radius:18px}.kpis,.ability-grid,.plan-list{grid-template-columns:1fr}.bar-row{grid-template-columns:1fr 1fr 56px}.section-head{display:block}h1{font-size:36px}th,td{padding:8px}}
"""

    parts = [
        "<!doctype html>",
        "<html lang='zh-CN'>",
        "<head>",
        "<meta charset='utf-8'/>",
        "<meta name='viewport' content='width=device-width, initial-scale=1'/>",
        "<title>AI 教育 Rebenchmark 结论与下一步计划</title>",
        f"<style>{css}</style>",
        "</head>",
        "<body><div class='page'>",
        "<header class='hero'>",
        "<p class='eyebrow'>Capability-Oriented Rebenchmark · 2026-07-07</p>",
        "<h1>AI 教育 Rebenchmark 结论与下一步计划</h1>",
        "<p class='hero-sub'>本报告使用 <b>doc/atomic_ability_principle_audit_v3.md</b> 的 P01-P22 v3.2 原子能力作为唯一编号；"
        f"整合 <b>{esc(MAIN_SOURCE)}</b> 的多模型 benchmark 结果与当前 <b>reports/eval/**/summary.json</b> 的本仓库实测结果，形成 MiniMax-M3 单模型画像、benchmark dashboard 和 CLM/CEG 重点切片。</p>",
        "<div class='kpis'>",
        f"<div class='kpi'><b>{len(abilities)}</b><span>P01-P22 原子能力</span></div>",
        f"<div class='kpi'><b>{len(reference_families)}</b><span>多模型 benchmark 组</span></div>",
        f"<div class='kpi'><b>{reference_model_count}</b><span>0701 覆盖模型</span></div>",
        f"<div class='kpi'><b>{len(raw_benchmarks)}</b><span>本仓库 raw benchmark</span></div>",
        "</div></header>",
    ]

    parts.append("<section><div class='section-head'><div><h2>1. 结论摘要</h2><p class='lede'>报告采用能力画像而非单一总分：先看 MiniMax-M3 的最完整画像，再看多模型 benchmark dashboard，最后单独查看 CLM/CEG 重点能力。</p></div></div>")
    parts.append("<div class='grid-3'>")
    for title, body in [
        ("MiniMax-M3 画像", f"本仓库 MiniMax-M3 覆盖 {len(minimax_rows)} 条 summary，其中 {len(eligible_minimax_rows)} 条满足计分条件，是当前最完整的 raw-backed 单模型视图。"),
        ("多模型对照", f"多模型层保留 0701 的 {len(reference_families)} 组 benchmark / {reference_model_count} 个模型；本仓库 raw 层覆盖 {len(raw_benchmarks)} 个 benchmark。"),
        ("重点切片", f"CLM/CEG 相关 benchmark 单列展示 {len(clm_ceg_rows)} 条原始结果，便于查看教学规划、反馈生成和教育安全相关模型表现。"),
    ]:
        parts.append(f"<div class='card'><h3>{esc(title)}</h3><p>{esc(body)}</p></div>")
    parts.append("</div></section>")

    parts.append("<section><div class='section-head'><div><h2>2. 原子能力框架</h2><p class='lede'>五类雷达维度来自 v3.2 的 P01-P22。教育任务层可以调用操作基座，但计分时只按映射到的 P 能力聚合。</p></div></div>")
    parts.append("<div class='ability-grid'>")
    for dim, meta in DIMENSIONS.items():
        parts.append(
            f"<article class='ability-card' style='--c:{meta['color']}'><div class='ability-code'>{esc(dim)}</div>"
            f"<h3>{esc(meta['zh'])}</h3><div class='en'>{esc(meta['en'])}</div><p>{esc(meta['summary'])}</p>"
            f"<p class='muted'>{esc(', '.join(dim_codes[dim]))}</p></article>"
        )
    parts.append("</div><div class='table-wrap' style='margin-top:16px'><table><thead><tr><th>编号</th><th>能力</th><th>维度</th><th>定义与边界</th></tr></thead><tbody>")
    for ability in abilities:
        meta = DIMENSIONS[ability["dimension"]]
        parts.append(
            f"<tr><th>{esc(ability['code'])}</th><td>{esc(ability['name'])}</td>"
            f"<td>{render_badges([ability['code']], abilities_by_code)} {esc(ability['dimension'])} · {esc(meta['zh'])}</td>"
            f"<td>{esc(ability['definition'])}</td></tr>"
        )
    parts.append("</tbody></table></div></section>")

    parts.append("<section><div class='section-head'><div><h2>3. Benchmark × 原子能力确认矩阵</h2><p class='lede'>先保留 0701 的模型 × benchmark 覆盖热力图，再把 0701 主 benchmark 与本仓库新增 benchmark 逐项映射到 P01-P22。● 表示该分数可解释为该 P 的证据，○ 表示任务执行覆盖或依赖该 P 但不直接计分。</p></div></div>")
    parts.append("<h3>3.1 0701 模型 × Benchmark 覆盖</h3>")
    parts.append(render_reference_coverage(reference_rows))
    parts.append("<h3 style='margin-top:18px'>3.2 Benchmark × P01-P22 映射确认</h3>")
    parts.append(render_benchmark_capability_matrix(mapping_rows, abilities, abilities_by_code))
    parts.append("</section>")

    parts.append("<section><div class='section-head'><div><h2>4. 多模型 benchmark 结果总览</h2><p class='lede'>这一节延续 0701 的 dashboard 样式：先看模型覆盖到哪些 P 能力，再看各 benchmark 的模型表现。</p></div></div>")
    parts.append("<h3>4.1 模型 × P 能力覆盖</h3>")
    parts.append(render_reference_capability_matrix(reference_rows, abilities))
    parts.append("<h3 style='margin-top:18px'>4.2 Benchmark 结果 dashboard</h3>")
    parts.append(render_reference_benchmark_dashboard(reference_rows))
    parts.append("</section>")

    parts.append("<section><div class='section-head'><div><h2>5. MiniMax-M3 单模型原始画像</h2><p class='lede'>MiniMax-M3 是当前本仓库跑得最全的单模型。雷达使用 total >= 20 且 scored/total >= 95% 的 eligible 行；全 benchmark 表现图合并本仓库结果和 0701 参考结果。</p></div></div>")
    parts.append("<div class='note' style='margin-bottom:14px'>分数含义：每条 benchmark 结果先归一到 0-1；只进入该行 score P；同一 P 的结果求平均，维度分数再对已覆盖 P 求平均。缺证据 P 不参与均值，但会在覆盖列中显示。</div>")
    parts.append("<div class='radar-grid'><div class='radar-card'>")
    parts.append(render_radar_svg(selected_models, dimension_scores))
    parts.append("</div>")
    parts.append(render_dimension_score_table(selected_models, dimension_scores, dim_codes))
    parts.append("</div>")

    parts.append("<h3 style='margin-top:18px'>MiniMax-M3 全 benchmark 表现</h3>")
    parts.append("<p class='lede'>合并 0701 参考 benchmark 与本仓库 reports/eval summary；条形图数值统一为越高越好的 0-100 归一分。</p>")
    parts.append(render_benchmark_bar_chart(minimax_combined_rows))

    parts.append("<div class='table-wrap' style='margin-top:16px'><table><thead><tr><th>维度</th><th>Score</th><th>Covered/Total</th><th>Eligible evidence rows</th><th>Missing P</th></tr></thead><tbody>")
    model_for_detail = selected_models[0] if selected_models else "MiniMax-M3"
    for dim in DIMENSIONS:
        item = dimension_scores.get(model_for_detail, {}).get(dim, {})
        evidence_count = sum(
            1
            for row in eligible_minimax_rows
            if any(P_TO_DIMENSION.get(code) == dim for code in row_score_p_codes(row))
        )
        missing = item.get("missing")
        if missing is None:
            missing = [code for code in dim_codes[dim] if code not in item.get("codes", [])]
        parts.append(
            f"<tr><td>{esc(dim)} · {esc(DIMENSIONS[dim]['zh'])}</td><td class='num'>{fmt_score(item.get('score'))}</td>"
            f"<td class='nowrap'>{item.get('covered', 0)}/{item.get('total', len(dim_codes[dim]))}</td>"
            f"<td class='num'>{evidence_count}</td><td>{render_badges(missing, abilities_by_code)}</td></tr>"
        )
    parts.append("</tbody></table></div>")

    parts.append("</section>")

    parts.append("<section><div class='section-head'><div><h2>6. CLM / CEG 相关 benchmark 模型表现</h2><p class='lede'>只纳入 score P 落在 CLM/CEG 的 benchmark 结果；覆盖但不计分的支持能力只在第 3 部分矩阵中展示。数据合并 0701 参考层和本仓库 reports/eval summary。</p></div></div>")
    parts.append("<h3>6.1 CLM · 认知建模与教学规划</h3>")
    parts.append(render_dimension_model_benchmark_charts(clm_ceg_rows, "CLM"))
    parts.append("<h3 style='margin-top:18px'>6.2 CEG · 约束性教育生成</h3>")
    parts.append(render_dimension_model_benchmark_charts(clm_ceg_rows, "CEG"))
    parts.append("</section>")

    parts.append("<section><div class='section-head'><div><h2>7. LLM-as-Judge 研究路线</h2><p class='lede'>初衷是解决主观题、开放教学反馈、rubric 评分和安全处置这类 exact match 无法覆盖的问题：短期用 rubric prompt 形成可追溯评测，长期沉淀数据训练专用 judge 模型。</p></div></div>")
    parts.append("<div class='plan-list'>")
    plan_items = [
        ("短期：Rubric Prompt", "把主观题拆成维度、等级、锚点样例和反例；记录 judge 模型、prompt hash、抽样策略和每次重跑差异。"),
        ("中期：校准与复核", "建立人工校准集，报告一致率、Cohen's kappa 或 bootstrap CI、分歧率、位置偏置和人工复核策略。"),
        ("长期：训练 Judge", "把高分歧样本、人工复核样本和 rubric 演化样本沉淀为训练集，训练教育专用 judge / reward model。"),
    ]
    for title, body in plan_items:
        parts.append(f"<div class='plan-item'><b>{esc(title)}</b><p>{esc(body)}</p></div>")
    parts.append("</div>")
    parts.append("<div class='note' style='margin-top:14px'><b>LLM-as-Judge 说明：</b>短期目标不是制造一个不可解释的自动分，而是用 rubric prompt 快速覆盖主观题评测；长期目标是用校准数据和争议样本训练稳定 judge 模型，并持续报告裁判模型、prompt/version hash、校准集、Cohen's kappa 或一致率置信区间、分歧率、位置偏置检查与人工复核策略。</div>")
    parts.append("</section>")

    parts.append(
        "<p class='footer'>Generated by scripts/build_rebenchmark_conclusion_plan.py · Data layers: 0701 benchmark reference + repo summary metrics</p>"
    )
    parts.append("</div></body></html>")
    return "\n".join(parts)


def write_report(output: Path, atomic_doc: Path, eval_dir: Path) -> None:
    abilities = parse_abilities(atomic_doc)
    reference_rows = build_main_results()
    minimax_rows = collect_minimax_m3_summaries(eval_dir)
    all_repo_rows = collect_summary_rows(eval_dir)
    raw_scores = compute_scores_from_rows(minimax_rows, abilities)
    reference_scores = compute_main_scores(reference_rows, abilities)
    raw_all_scores = compute_scores_from_rows(all_repo_rows, abilities)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        render_html(
            abilities,
            reference_rows,
            minimax_rows,
            all_repo_rows,
            raw_scores,
            reference_scores,
            raw_all_scores,
        )
        + "\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--atomic-doc", type=Path, default=ATOMIC_DOC)
    parser.add_argument("--eval-dir", type=Path, default=ROOT / "reports" / "eval")
    args = parser.parse_args()

    output = args.output if args.output.is_absolute() else ROOT / args.output
    atomic_doc = args.atomic_doc if args.atomic_doc.is_absolute() else ROOT / args.atomic_doc
    eval_dir = args.eval_dir if args.eval_dir.is_absolute() else ROOT / args.eval_dir
    write_report(output, atomic_doc, eval_dir)
    print(f"wrote {output.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
