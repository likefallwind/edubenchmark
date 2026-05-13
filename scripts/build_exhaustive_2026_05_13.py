#!/usr/bin/env python3
"""Build exhaustive local AI-Edu benchmark extraction artifacts.

The generator intentionally keeps benchmark-native rows and metric columns as
separate records. It does not average across benchmarks or collapse models.
"""

from __future__ import annotations

import html
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SURVEY = ROOT / "edu_benchmark_survey.md"
SUPPLEMENT = ROOT / "edu_benchmark_survey_supplement_2026-05-11.md"
DIM_FILE = ROOT / "data" / "benchmark_metric_dimensions_2026-05-12.json"
IND_FILE = ROOT / "data" / "benchmark_metric_indicators_2026-05-12.json"
OUTDIR = ROOT / "data" / "exhaustive_2026-05-13"
REPORT_DIR = ROOT / "reports" / "2026-05-13"
MD_REPORT = REPORT_DIR / "ai_edu_benchmark_exhaustive_index_2026-05-13.md"
HTML_REPORT = REPORT_DIR / "ai_edu_benchmark_exhaustive_index_2026-05-13.html"


BENCHMARK_ALIASES = {
    "MMLU": "mmlu",
    "CMMLU": "cmmlu",
    "C-EVAL": "ceval",
    "C-Eval": "ceval",
    "AGIEval": "agieval",
    "GaokaoBench": "gaokaobench",
    "GAOKAO-Bench": "gaokaobench",
    "E-EVAL": "eeval",
    "OlympiadBench": "olympiadbench",
    "CMMU": "cmmu",
    "ChartQA": "chartqa",
    "GSM8K": "gsm8k",
    "MATH": "math",
    "MATH-500": "math_500",
    "OlymMATH": "olymmath",
    "MathVista": "mathvista",
    "ME2": "me2",
    "ME / ME2": "me2",
    "HumanEval": "humaneval",
    "MBPP": "mbpp",
    "Pedagogy Benchmark": "pedagogy_benchmark",
    "MathTutorBench": "mathtutorbench",
    "EduBench": "edubench",
    "EduEval": "edueval",
    "OmniEduBench": "omniedubench",
    "EduGuard-Bench": "eduguard_bench",
    "TutorBench": "tutorbench",
    "EduVisBench": "eduvisbench",
    "SciVideoBench": "scivideobench",
    "K12Vista": "k12vista",
    "InteractScience": "interactscience",
    "EssayJudge": "essayjudge",
    "SAS-Bench": "sas_bench",
    "ASSISTments 系列": "assistments",
    "APPS": "apps_dataset",
    "Junyi": "junyi_academy",
    "SocraticLM / SocraTeach": "socraticlm",
    "Codecademy": "codecademy_dataset",
    "LeetCode Student Submissions": "leetcode_student_submissions",
    "子曰": "网易有道子曰",
    "星火教育": "科大讯飞星火教育",
    "学而思九章大模型": "九章大模型",
    "网易有道子曰大模型": "网易有道子曰",
    "科大讯飞星火教育大模型": "科大讯飞星火教育",
}

BENCHMARK_PATTERNS = sorted(BENCHMARK_ALIASES, key=len, reverse=True)

MANUAL_URLS = {
    "mmlu": ["https://arxiv.org/abs/2009.03300", "https://huggingface.co/datasets/cais/mmlu"],
    "cmmlu": ["https://github.com/haonan-li/CMMLU", "https://arxiv.org/abs/2306.09212"],
    "ceval": ["https://github.com/hkust-nlp/ceval", "https://arxiv.org/abs/2305.08322"],
    "agieval": ["https://github.com/ruixiangcui/AGIEval", "https://arxiv.org/abs/2304.06364"],
    "gaokaobench": ["https://github.com/OpenLMLab/GAOKAO-Bench", "https://arxiv.org/abs/2305.12474"],
    "eeval": ["https://github.com/AI-EDU-LAB/E-EVAL", "https://arxiv.org/abs/2401.15927"],
    "olympiadbench": ["https://github.com/OpenBMB/OlympiadBench", "https://arxiv.org/abs/2402.14008"],
    "cmmu": ["https://github.com/flageval-baai/CMMU", "https://arxiv.org/abs/2401.14011"],
    "chartqa": ["https://github.com/vis-nlp/chartqa", "https://aclanthology.org/2022.findings-acl.177/"],
    "gsm8k": ["https://arxiv.org/abs/2110.14168", "https://huggingface.co/datasets/openai/gsm8k"],
    "math": ["https://github.com/hendrycks/math", "https://arxiv.org/abs/2103.03874"],
    "math_500": ["https://github.com/hendrycks/math"],
    "olymmath": ["https://github.com/RUCAIBox/OlymMATH", "https://arxiv.org/abs/2503.21380"],
    "mathvista": ["https://github.com/lupantech/MathVista", "https://arxiv.org/abs/2310.02255", "https://mathvista.github.io/"],
    "me2": ["https://huggingface.co/datasets/jungypark/ME2", "https://arxiv.org/abs/2504.03197"],
    "humaneval": ["https://github.com/openai/human-eval", "https://arxiv.org/abs/2107.03374"],
    "mbpp": ["https://arxiv.org/abs/2108.07732", "https://huggingface.co/datasets/Muennighoff/mbpp"],
    "pedagogy_benchmark": ["https://huggingface.co/datasets/AI-for-Education/pedagogy-benchmark", "https://arxiv.org/abs/2506.18710"],
    "mathtutorbench": ["https://github.com/eth-lre/mathtutorbench"],
    "edubench": ["https://github.com/ybai-nlp/EduBench"],
    "edueval": ["https://github.com/Maerzs/E_edueval"],
    "omniedubench": ["https://mind-lab-ecnu.github.io/OmniEduBench/", "https://arxiv.org/abs/2510.26422"],
    "eduguard_bench": ["https://github.com/YL1N/EduGuardBench", "https://arxiv.org/abs/2511.06890"],
    "tutorbench": ["https://huggingface.co/datasets/ScaleAI/TutorBench", "https://www.arxiv.org/abs/2510.02663"],
    "eduvisbench": ["https://huggingface.co/datasets/Haonian/EduVisBench/viewer", "https://arxiv.org/abs/2505.16832"],
    "scivideobench": ["https://huggingface.co/datasets/groundmore/scivideobench"],
    "k12vista": ["https://github.com/lichongod/K12Vista", "https://arxiv.org/abs/2506.01676"],
    "interactscience": ["https://github.com/open-compass/InteractScience"],
    "essayjudge": ["https://arxiv.org/abs/2502.11916"],
    "sas_bench": ["https://github.com/PKU-DAIR/SAS-Bench", "https://arxiv.org/abs/2505.07247"],
    "convolearn": ["https://huggingface.co/datasets/masharma/convolearn", "https://arxiv.org/pdf/2601.08950v1", "https://scale.stanford.edu/ai/repository/convolearn-dataset-constructivist-tutor-student-dialogue"],
    "pebble": ["https://openreview.net/forum?id=ffvNvoJVgE"],
}

MANUAL_META = {
    "mmlu": ("通用考试与学科知识", "multiple_choice_subject_knowledge"),
    "cmmlu": ("中文通识与本土知识", "multiple_choice_subject_knowledge"),
    "ceval": ("中文考试与学科知识", "multiple_choice_exam"),
    "agieval": ("标准化考试", "exam_reasoning"),
    "gaokaobench": ("中文高考", "objective_and_subjective_exam"),
    "eeval": ("中文 K12", "k12_multiple_choice"),
    "olympiadbench": ("奥赛数学与物理", "multimodal_competition_reasoning"),
    "cmmu": ("中文多模态学科", "multimodal_question_answering"),
    "chartqa": ("图表问答", "chart_question_answering"),
    "gsm8k": ("基础数学", "grade_school_math_reasoning"),
    "math": ("高阶数学", "competition_math_reasoning"),
    "math_500": ("高阶数学", "competition_math_reasoning"),
    "olymmath": ("奥赛数学", "hard_competition_math"),
    "mathvista": ("多模态数学", "visual_math_reasoning"),
    "me2": ("几何视觉教学", "visual_keypoint_and_explanation"),
    "humaneval": ("代码生成", "program_synthesis"),
    "mbpp": ("入门编程", "program_synthesis"),
    "pedagogy_benchmark": ("教学法知识", "pedagogical_knowledge_exam"),
    "mathtutorbench": ("数学辅导", "tutoring_diagnosis_and_scaffolding"),
    "edubench": ("教育场景生成", "education_rubric_judging"),
    "edueval": ("中文教育生成与知识", "education_generation_and_knowledge"),
    "omniedubench": ("中文新课标教育", "knowledge_and_cultivation_assessment"),
    "eduguard_bench": ("教育安全", "role_following_and_safety"),
    "tutorbench": ("真实辅导", "tutoring_feedback"),
    "eduvisbench": ("教学可视化", "educational_visualization_generation"),
    "scivideobench": ("科学视频", "science_video_understanding"),
    "k12vista": ("中文 K12 多模态", "multimodal_question_answering_process_evaluation"),
    "interactscience": ("交互式科学演示", "interactive_science_demo_generation"),
    "essayjudge": ("作文自动评分", "multimodal_essay_scoring"),
    "sas_bench": ("短答案评分", "short_answer_step_scoring"),
    "convolearn": ("建构主义辅导对话", "constructivist_tutoring_dialogue"),
    "pebble": ("多轮辅导过程评测", "multi_turn_tutoring_process_evaluation"),
}

RESOURCE_DIMENSIONS = {
    "Math23K": ["D04"],
    "Ape210K": ["D04"],
    "NuminaMath": ["D05"],
    "IMO-ANSWER BENCH": ["D05"],
    "BigMath-Verified": ["D05"],
    "ASSISTments": ["D15", "D16", "D17"],
    "KDD Cup 2010": ["D16"],
    "EdNet": ["D15", "D16"],
    "Junyi Academy": ["D16", "D17"],
    "FoundationalAssist": ["D15", "D17"],
    "数字教育应用算法智能诊断公共数据集": ["D17"],
    "PTADisc": ["D09", "D17"],
    "STATICS2011": ["D16"],
    "Synthetic": ["D16"],
    "Adaptive Geography Practice": ["D16"],
    "ASAP-AES": ["D10"],
    "ASAP-SAS": ["D11"],
    "ELLIPSE Corpus": ["D10"],
    "MathDial": ["D12", "D13"],
    "Google Education Dialogue Dataset": ["D19"],
    "EduDial": ["D13", "D19"],
    "IntrEx": ["D20"],
    "SocraticLM": ["D13"],
    "QACP": ["D09"],
    "CS1QA": ["D09"],
    "FineWeb-Edu": ["D18"],
    "Chinese Fineweb Edu": ["D18"],
    "LectureBank": ["D07", "D18"],
    "SCB-Dataset": ["D20"],
    "NCTE Transcripts": ["D19"],
    "ARIC": ["D07", "D20"],
    "TalkMoves": ["D19"],
    "TIMSS Video Study": ["D07", "D19"],
    "SIGHT": ["D18", "D19"],
    "VisualEDU": ["D22", "D23"],
    "MLPdataset": ["D18"],
    "MOOCCube": ["D15", "D18"],
    "TutorialBank": ["D18"],
    "Codecademy Dataset": ["D08", "D09"],
    "LeetCode Student Submissions": ["D08", "D09"],
    "APPS Dataset": ["D08"],
    "InnoSpark": ["D24"],
    "九章大模型": ["D24"],
    "网易有道子曰": ["D24"],
    "科大讯飞星火教育": ["D24"],
    "CheggMate": ["D24"],
    "ConvoLearn": ["D13", "D19"],
    "PEBBLE": ["D12", "D13", "D15"],
}

EXTRA_RESOURCE_RESULTS = [
    {
        "benchmark": "ConvoLearn",
        "model": "Fine-tuned Mistral 7B",
        "metric": "teacher human evaluation overall",
        "score": "4.10",
        "setting": "QLoRA fine-tuned",
        "notes": "Stanford SCALE page reports human evaluation by 31 teachers; dataset has 1,250 middle-school Earth Science tutor-student dialogues and six constructivist pedagogy dimensions.",
        "source_url": "https://scale.stanford.edu/ai/repository/convolearn-dataset-constructivist-tutor-student-dialogue",
    },
    {
        "benchmark": "ConvoLearn",
        "model": "Base Mistral 7B",
        "metric": "teacher human evaluation overall",
        "score": "2.59",
        "setting": "base model",
        "notes": "Reported comparison point on the Stanford SCALE ConvoLearn page.",
        "source_url": "https://scale.stanford.edu/ai/repository/convolearn-dataset-constructivist-tutor-student-dialogue",
    },
    {
        "benchmark": "ConvoLearn",
        "model": "Claude Sonnet 4.5",
        "metric": "teacher human evaluation overall",
        "score": "2.87",
        "setting": "frontier baseline",
        "notes": "Reported comparison point on the Stanford SCALE ConvoLearn page; use as source-reported context, not a unified public leaderboard.",
        "source_url": "https://scale.stanford.edu/ai/repository/convolearn-dataset-constructivist-tutor-student-dialogue",
    },
    {
        "benchmark": "PEBBLE",
        "model": "not_standardized",
        "metric": "no_unified_leaderboard",
        "score": "no_unified_leaderboard",
        "setting": "pending_public_release",
        "notes": "OpenReview record describes an initial multi-turn tutor benchmark with scaffolding, diagnostic questioning, misconception repair, metacognitive support, affective support, overhelping penalty, contamination controls, and an evaluation kit to be released upon acceptance.",
        "source_url": "https://openreview.net/forum?id=ffvNvoJVgE",
    },
]


def split_md_row(line: str) -> list[str]:
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return [cell.strip() for cell in line.split("|")]


def is_sep(line: str) -> bool:
    cells = split_md_row(line)
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", c.replace(" ", "")) for c in cells)


def parse_tables(path: Path) -> list[dict[str, Any]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    tables: list[dict[str, Any]] = []
    section = ""
    bold_title = ""
    paragraph = ""
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("#"):
            section = line.lstrip("#").strip()
        bold = re.fullmatch(r"\*\*(.+?)\*\*", line.strip())
        if bold:
            bold_title = bold.group(1)
        elif line.strip() and not line.startswith("|"):
            paragraph = line.strip()
        if line.startswith("|") and i + 1 < len(lines) and lines[i + 1].startswith("|") and is_sep(lines[i + 1]):
            start = i + 1
            header = split_md_row(lines[i])
            i += 2
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                cells = split_md_row(lines[i])
                cells += [""] * (len(header) - len(cells))
                rows.append(cells[: len(header)])
                i += 1
            tables.append(
                {
                    "path": path.name,
                    "line": start,
                    "section": section,
                    "title": bold_title or paragraph or section,
                    "header": header,
                    "rows": rows,
                }
            )
            continue
        i += 1
    return tables


def canonical_name(name: str) -> str:
    clean = re.sub(r"\s+", " ", name.replace("，", ",")).strip()
    for alias in BENCHMARK_PATTERNS:
        if alias.lower() == clean.lower():
            return alias
    return clean


def benchmark_id(name: str) -> str:
    name = canonical_name(name)
    if name in BENCHMARK_ALIASES:
        return BENCHMARK_ALIASES[name]
    normalized = re.sub(r"[^0-9a-zA-Z\u4e00-\u9fff]+", "_", name).strip("_").lower()
    return normalized or "unknown"


def infer_benchmark(title: str) -> str | None:
    for pat in BENCHMARK_PATTERNS:
        if pat in title:
            return pat
    return None


def parse_links(text: str) -> list[str]:
    return re.findall(r"\]\((https?://[^)]+)\)", text)


def numeric_score(score_text: str) -> float | None:
    s = score_text.strip()
    if not s or s in {"-", "N/A", "无", "无平均值表"}:
        return None
    if re.search(r"\d+\s*-\s*\d+", s):
        return None
    m = re.search(r"-?\d+(?:\.\d+)?", s.replace(",", ""))
    if not m:
        return None
    try:
        return float(m.group(0))
    except ValueError:
        return None


def metric_normalized(metric: str) -> str:
    mapping = {
        "Avg": "平均分",
        "ALL": "总体分",
        "Overall": "总体分",
        "Test Avg": "测试集平均分",
        "Problem solving": "解题能力",
        "Socratic BLEU": "苏格拉底式提问 BLEU",
        "Solution correctness": "学生答案正确性判断",
        "Mistake location": "错误位置定位",
        "Correction": "纠错准确性",
        "Scaffolding": "脚手架胜率",
        "Ped. IF": "教学指令遵循",
        "Scaff. hard": "困难脚手架胜率",
        "Ped. IF hard": "困难教学指令遵循",
        "CDPK": "教学法知识正确率",
        "SEND": "特殊教育能力",
        "RFS": "角色扮演专业度",
        "ASR": "攻击成功率",
        "CCS Avg": "分步评分一致性",
        "ECS Avg": "错误原因一致性",
        "PFT Overall": "程序功能测试通过率",
        "Direct Overall": "直接作答总体分",
        "Step-by-Step Overall": "逐步作答总体分",
    }
    return mapping.get(metric, metric)


def evaluator_type(benchmark: str, metric: str) -> str:
    bid = benchmark_id(benchmark)
    low = metric.lower()
    if metric == "no_unified_leaderboard":
        return "not_applicable"
    if bid in {"essayjudge", "sas_bench"}:
        return "automatic_metric_against_human_labels"
    if bid in {"edubench", "eduvisbench", "tutorbench", "mathtutorbench", "eduguard_bench"}:
        return "automatic_or_model_judge"
    if bid in {"interactscience"}:
        return "programmatic_and_vlm_judge"
    if "subjective" in low:
        return "human_or_model_judge"
    return "automatic"


def higher_is_better(metric: str) -> bool:
    return metric.strip().lower() not in {
        "asr",
        "omit",
        "incl",
        "attack success rate",
        "安全失败率",
        "no_unified_leaderboard",
    }


def load_dimension_maps() -> tuple[dict[str, str], dict[str, list[str]], dict[str, list[str]], list[dict[str, Any]]]:
    data = json.loads(DIM_FILE.read_text(encoding="utf-8"))
    dim_names = {d["id"]: d["dimension"] for d in data["dimensions"]}
    bench_dims: dict[str, list[str]] = defaultdict(list)
    for d in data["dimensions"]:
        for b in d.get("benchmarks", []):
            bid = benchmark_id(b)
            if d["id"] not in bench_dims[bid]:
                bench_dims[bid].append(d["id"])
    for name, dims in RESOURCE_DIMENSIONS.items():
        bid = benchmark_id(name)
        for d in dims:
            if d not in bench_dims[bid]:
                bench_dims[bid].append(d)
    indicators = json.loads(IND_FILE.read_text(encoding="utf-8"))["dimensions"]
    metric_dims: dict[str, list[str]] = defaultdict(list)
    for dim in indicators:
        did = dim["dimension_id"]
        for ind in dim.get("indicators", []):
            for native in ind.get("benchmark_native_metrics", []):
                key = native.lower()
                if did not in metric_dims[key]:
                    metric_dims[key].append(did)
    return dim_names, bench_dims, metric_dims, indicators


def infer_dimensions(bid: str, metric: str, bench_dims: dict[str, list[str]]) -> list[str]:
    dims = list(bench_dims.get(bid, []))
    low = metric.lower()
    if bid == "mathtutorbench":
        dims = []
        if "problem" in low:
            dims.append("D24")
        if "mistake" in low or "correction" in low or "solution correctness" in low:
            dims.append("D12")
        if "socratic" in low or "scaff" in low or "ped" in low:
            dims.append("D13")
    elif bid == "pedagogy_benchmark":
        dims = ["D14"]
    elif bid == "eduguard_bench":
        dims = ["D21"]
    elif bid == "eduvisbench":
        dims = ["D22"]
    elif bid == "interactscience":
        dims = ["D23"]
    elif bid == "essayjudge":
        dims = ["D10"]
    elif bid == "sas_bench":
        dims = ["D11"]
    elif bid == "humaneval" or bid == "mbpp":
        dims = ["D08"]
    elif bid == "scivideobench":
        dims = ["D07"]
    elif bid == "k12vista":
        dims = ["D02", "D06"]
    elif bid == "convolearn":
        dims = ["D13", "D19"]
    elif bid == "pebble":
        dims = ["D12", "D13", "D15"]
    return sorted(set(dims))


def make_result(
    benchmark: str,
    model: str,
    metric: str,
    score_text: str,
    source_file: str,
    source_section: str,
    bench_dims: dict[str, list[str]],
    setting: str = "default",
    subset: str = "",
    notes: str = "",
    source_url: str = "",
) -> dict[str, Any]:
    bid = benchmark_id(benchmark)
    return {
        "benchmark_id": bid,
        "benchmark_name": canonical_name(benchmark),
        "dimension_ids": infer_dimensions(bid, metric, bench_dims),
        "model": model.strip(),
        "metric_original": metric.strip(),
        "metric_normalized": metric_normalized(metric.strip()),
        "score": numeric_score(score_text),
        "score_text": score_text.strip(),
        "setting": setting.strip() or "default",
        "subset": subset.strip(),
        "higher_is_better": higher_is_better(metric),
        "evaluator_type": evaluator_type(benchmark, metric),
        "source_file": source_file,
        "source_section": source_section,
        "source_url": source_url or (MANUAL_URLS.get(bid, [""])[0] if MANUAL_URLS.get(bid) else ""),
        "notes": notes.strip(),
    }


def extract_appendix_results(tables: list[dict[str, Any]], bench_dims: dict[str, list[str]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    results: list[dict[str, Any]] = []
    log: list[dict[str, Any]] = []
    appendix_line = next(
        i
        for i, line in enumerate(SURVEY.read_text(encoding="utf-8").splitlines(), start=1)
        if line.strip() == "## 模型级明细附录"
    )
    for table in tables:
        if table["path"] != SURVEY.name or table["line"] <= appendix_line:
            continue
        if table["section"].startswith("E. 无官方统一模型榜单"):
            continue
        title = table["title"]
        bench = infer_benchmark(title)
        if not bench:
            continue
        header = table["header"]
        rows = table["rows"]
        before = len(results)
        metric_name = "CDPK" if "CDPK" in header else "SEND" if "SEND" in header else None
        if bench == "Pedagogy Benchmark" and metric_name:
            for row in rows:
                for offset in (0, 2):
                    if offset + 1 < len(row) and row[offset].strip():
                        results.append(
                            make_result(
                                bench,
                                row[offset],
                                metric_name,
                                row[offset + 1],
                                table["path"],
                                title,
                                bench_dims,
                                source_url=MANUAL_URLS["pedagogy_benchmark"][0],
                            )
                        )
        else:
            model_col = None
            for candidate in ("Model", "Model/方法", "Model size", "系统"):
                if candidate in header:
                    model_col = header.index(candidate)
                    break
            if model_col is None:
                continue
            setting_cols = [c for c in ("Type", "Setting", "Output", "Evaluator", "Prompt") if c in header]
            note_cols = [c for c in ("典型弱项",) if c in header]
            excluded = {header[model_col], *setting_cols, *note_cols}
            metric_cols = [i for i, h in enumerate(header) if h not in excluded]
            for row in rows:
                model = row[model_col]
                settings = [f"{c}={row[header.index(c)]}" for c in setting_cols if row[header.index(c)]]
                setting = "; ".join(settings) if settings else "default"
                notes = "; ".join(row[header.index(c)] for c in note_cols if row[header.index(c)])
                for idx in metric_cols:
                    metric = header[idx]
                    score_text = row[idx]
                    if not metric or not score_text:
                        continue
                    results.append(
                        make_result(
                            bench,
                            model,
                            metric,
                            score_text,
                            table["path"],
                            title,
                            bench_dims,
                            setting=setting,
                            notes=notes,
                        )
                    )
        log.append(
            {
                "source_file": table["path"],
                "source_section": title,
                "benchmark": bench,
                "markdown_rows": len(rows),
                "result_records": len(results) - before,
                "status": "extracted",
                "notes": "每个模型行按指标列展开；Pedagogy 双栏表按左右两组模型展开。" if bench == "Pedagogy Benchmark" else "",
            }
        )
    return results, log


def supplement_results(bench_dims: dict[str, list[str]]) -> list[dict[str, Any]]:
    rows: list[tuple[str, str, str, str, str, str]] = [
        ("MMLU", "GPT-4.1", "updated average", "90.2", "OpenAI GPT-4.1 report", ""),
        ("MMLU", "GPT-4.1 mini", "updated average", "87.5", "OpenAI GPT-4.1 report", ""),
        ("MMLU", "GPT-4o(2024-11-20)", "updated average", "85.7", "OpenAI GPT-4.1 report", ""),
        ("MMLU", "o1(high)", "updated average", "91.8", "OpenAI GPT-4.1 report", ""),
        ("MMLU", "o3-mini(high)", "updated average", "86.9", "OpenAI GPT-4.1 report", ""),
        ("MMLU", "GPT-4.5", "updated average", "90.8", "OpenAI GPT-4.1 report", ""),
        ("MMLU", "gpt-oss-120b", "updated average", "90.0", "OpenAI open models page", ""),
        ("MMLU", "gpt-oss-20b", "updated average", "85.3", "OpenAI open models page", ""),
        ("MMLU", "o3", "updated average", "93.4", "OpenAI open models page", ""),
        ("MMLU", "o4-mini", "updated average", "93.0", "OpenAI open models page", ""),
        ("MMLU", "Llama 3.1 405B-Instruct", "MMLU", "87.3", "Meta Llama 3.1 model card", ""),
        ("MMLU", "Llama 3.1 405B-Instruct", "MMLU(CoT)", "88.6", "Meta Llama 3.1 model card", ""),
        ("MMLU", "DeepSeek-R1", "MMLU", "90.8", "DeepSeek-R1 report", ""),
        ("MMLU", "Qwen3-235B-A22B-Base", "MMLU", "87.81", "Qwen3 report", ""),
        ("CMMLU", "Lingzhi-72B-chat", "five-shot average", "90.26", "official README leaderboard", "five-shot"),
        ("CMMLU", "Telechat2-35B", "five-shot average", "90.16", "official README leaderboard", "five-shot"),
        ("CMMLU", "Spark 4.0", "five-shot average", "90.07", "official README leaderboard", "five-shot"),
        ("CMMLU", "Qwen2-72B", "five-shot average", "89.65", "official README leaderboard", "five-shot"),
        ("CMMLU", "Spark 4.0", "zero-shot average", "90.97", "official README leaderboard", "zero-shot"),
        ("CMMLU", "Telechat2-35B", "zero-shot average", "90.49", "official README leaderboard", "zero-shot"),
        ("CMMLU", "Lingzhi-72B-chat", "zero-shot average", "90.07", "official README leaderboard", "zero-shot"),
        ("C-EVAL", "DeepSeek-R1", "self-reported average", "91.8", "DeepSeek-R1 model report", ""),
        ("AGIEval", "Llama 3.1 405B", "AGIEval English", "71.6", "Meta Llama 3.1 model card", ""),
        ("GaokaoBench", "GPT-4-0409", "weighted average", "76.0", "OpenCompass benchmark document", ""),
        ("GaokaoBench", "GPT-4-1106", "weighted average", "74.8", "OpenCompass benchmark document", ""),
        ("GaokaoBench", "Claude-3-Opus", "weighted average", "74.2", "OpenCompass benchmark document", ""),
        ("GaokaoBench", "Llama-3-70B-Instruct", "weighted average", "67.8", "OpenCompass benchmark document", ""),
        ("GaokaoBench", "Mixtral-8x22B", "weighted average", "60.0", "OpenCompass benchmark document", ""),
        ("GSM8K", "Llama 3.1 405B-Instruct", "accuracy", "96.8", "Meta Llama 3.1 model card", ""),
        ("GSM8K", "Qwen3-235B-A22B-Base", "accuracy", "94.39", "Qwen3 report", ""),
        ("GSM8K", "Llama-3-70B-Instruct", "accuracy", "90.2", "OpenCompass document", ""),
        ("GSM8K", "Claude-3-Opus", "accuracy", "87.7", "OpenCompass document", ""),
        ("GSM8K", "Mixtral-8x22B", "accuracy", "88.3", "OpenCompass document", ""),
        ("MATH", "Llama 3.1 405B-Instruct", "MATH(CoT)", "73.8", "Meta Llama 3.1 model card", ""),
        ("MATH", "Qwen3-235B-A22B-Base", "MATH", "71.84", "Qwen3 report", ""),
        ("MATH-500", "DeepSeek-R1", "accuracy", "97.3", "DeepSeek-R1 report", ""),
        ("MathVista", "InternVL2-Pro", "private test ALL", "65.84", "official project page private test leaderboard", "private test"),
        ("MathVista", "InternVL2-8B-MPO", "private test ALL", "65.65", "official project page private test leaderboard", "private test"),
        ("MathVista", "InternVL-Chat-V1.2-Plus", "private test ALL", "60.18", "official project page private test leaderboard", "private test"),
        ("OlympiadBench", "GPT-4o", "full benchmark overall", "25.89", "official repository", "full benchmark"),
        ("OlympiadBench", "GPT-4V", "full benchmark overall", "17.97", "official repository", "full benchmark"),
        ("OlympiadBench", "Qwen-VL-Max", "full benchmark overall", "10.09", "official repository", "full benchmark"),
        ("OlympiadBench", "GPT-4o", "text-only overall", "39.72", "official repository", "text-only"),
        ("OlympiadBench", "GPT-4", "text-only overall", "29.93", "official repository", "text-only"),
        ("OlympiadBench", "Llama-3-70B-Instruct", "text-only overall", "20.27", "official repository", "text-only"),
    ]
    return [
        make_result(
            bench,
            model,
            metric,
            score,
            SUPPLEMENT.name,
            "一、旧模型结果的线上补充 / 可补充进原报告的代表性新结果",
            bench_dims,
            setting=setting or "supplement_update",
            notes=note,
        )
        for bench, model, metric, score, note, setting in rows
    ]


def no_leaderboard_results(tables: list[dict[str, Any]], bench_dims: dict[str, list[str]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    results: list[dict[str, Any]] = []
    logs: list[dict[str, Any]] = []
    for table in tables:
        if table["path"] == SURVEY.name and table["section"].startswith("E. 无官方统一模型榜单"):
            for category, items in table["rows"]:
                for item in re.split(r"、", items):
                    item = item.strip()
                    if not item:
                        continue
                    results.append(
                        make_result(
                            item,
                            "not_standardized",
                            "no_unified_leaderboard",
                            "no_unified_leaderboard",
                            table["path"],
                            table["section"],
                            bench_dims,
                            setting="not_applicable",
                            notes=f"类别：{category}。论文/README/数据卡未找到可直接引用的官方统一模型 leaderboard。",
                        )
                    )
            logs.append(
                {
                    "source_file": table["path"],
                    "source_section": table["section"],
                    "benchmark": "multiple_resources",
                    "markdown_rows": len(table["rows"]),
                    "result_records": len(results),
                    "status": "no_unified_leaderboard_recorded",
                    "notes": "每个条目保留 no_unified_leaderboard 结果记录，避免无榜单条目被省略。",
                }
            )
    return results, logs


def extra_resource_results(bench_dims: dict[str, list[str]]) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]], list[dict[str, Any]]]:
    results = [
        make_result(
            row["benchmark"],
            row["model"],
            row["metric"],
            row["score"],
            "reports/2026-05-13/web_verified_updates_2026-05-13.md",
            "2026-05-13 web-verified emerging education benchmarks",
            bench_dims,
            setting=row["setting"],
            notes=row["notes"],
            source_url=row["source_url"],
        )
        for row in EXTRA_RESOURCE_RESULTS
    ]
    authority = {
        "convolearn": {
            "authority_score": 72.0,
            "authority_score_text": "72",
            "authority_score_type": "资源价值",
            "authority_usage_ecosystem": "新兴",
            "authority_reason": "建构主义 tutor 对话维度清晰，覆盖认知参与、形成性评价、元认知和权力关系等过程指标；目前规模和复现生态仍早期。",
            "authority_source_section": "2026-05-13 web-verified emerging education benchmarks",
        },
        "pebble": {
            "authority_score": 70.0,
            "authority_score_text": "70",
            "authority_score_type": "权威性",
            "authority_usage_ecosystem": "待发布",
            "authority_reason": "多轮 tutor 过程评分、SRL 和 overhelping penalty 设计贴近教育核心缺口；代码和榜单仍处于发布前状态。",
            "authority_source_section": "2026-05-13 web-verified emerging education benchmarks",
        },
    }
    logs = [
        {
            "source_file": "reports/2026-05-13/web_verified_updates_2026-05-13.md",
            "source_section": "2026-05-13 web-verified emerging education benchmarks",
            "benchmark": "ConvoLearn / PEBBLE",
            "markdown_rows": 2,
            "result_records": len(results),
            "status": "web_verified_emerging_resources_added",
            "notes": "补入 2026 检索发现但本地 survey 未覆盖的 tutor/教学过程类条目；ConvoLearn 保留来源页明示的人评分数，PEBBLE 保留为待发布评测协议。",
        }
    ]
    return results, authority, logs


def extract_authority(tables: list[dict[str, Any]]) -> tuple[dict[str, dict[str, Any]], list[dict[str, Any]]]:
    authority: dict[str, dict[str, Any]] = {}
    logs: list[dict[str, Any]] = []
    for table in tables:
        if table["path"] != SUPPLEMENT.name or "排名" not in table["header"]:
            continue
        name_col = None
        for candidate in ("Benchmark", "Benchmark / 数据集", "数据集/Benchmark", "条目"):
            if candidate in table["header"]:
                name_col = table["header"].index(candidate)
                break
        score_label = "权威性" if "权威性" in table["header"] else "资源价值" if "资源价值" in table["header"] else None
        if name_col is None or score_label is None:
            continue
        score_col = table["header"].index(score_label)
        usage_col = table["header"].index("使用量/复现生态") if "使用量/复现生态" in table["header"] else None
        reason_col = table["header"].index("主要理由") if "主要理由" in table["header"] else None
        count = 0
        for row in table["rows"]:
            raw_name = row[name_col].strip()
            if not raw_name:
                continue
            names = re.split(r"\s*/\s*|、", raw_name) if ("、" in raw_name or "/" in raw_name) else [raw_name]
            for name in names:
                name = name.strip()
                if not name:
                    continue
                bid = benchmark_id(name)
                authority[bid] = {
                    "authority_score": numeric_score(row[score_col]),
                    "authority_score_text": row[score_col],
                    "authority_score_type": score_label,
                    "authority_usage_ecosystem": row[usage_col] if usage_col is not None else "",
                    "authority_reason": row[reason_col] if reason_col is not None else "",
                    "authority_source_section": table["section"],
                }
                count += 1
        logs.append(
            {
                "source_file": table["path"],
                "source_section": table["section"],
                "benchmark": "authority_table",
                "markdown_rows": len(table["rows"]),
                "result_records": count,
                "status": "authority_metadata_extracted",
                "notes": f"{score_label} 表已写入 benchmarks.jsonl 的 authority_* 字段。",
            }
        )
    return authority, logs


def extract_source_urls(tables: list[dict[str, Any]]) -> dict[str, list[str]]:
    source_urls: dict[str, list[str]] = defaultdict(list)
    appendix_line = next(
        i
        for i, line in enumerate(SURVEY.read_text(encoding="utf-8").splitlines(), start=1)
        if line.strip() == "## 模型级明细附录"
    )
    for table in tables:
        if table["path"] != SURVEY.name or table["line"] >= appendix_line or "来源" not in table["header"]:
            continue
        source_col = table["header"].index("来源")
        name_col = None
        for candidate in ("条目", "系统"):
            if candidate in table["header"]:
                name_col = table["header"].index(candidate)
                break
        if name_col is None:
            continue
        for row in table["rows"]:
            urls = parse_links(row[source_col])
            if not urls:
                continue
            raw_name = row[name_col].strip()
            names = re.split(r"\s*/\s*|、", raw_name) if ("、" in raw_name or "/" in raw_name) else [raw_name]
            for name in names:
                bid = benchmark_id(name.strip())
                for url in urls:
                    if url not in source_urls[bid]:
                        source_urls[bid].append(url)
    for bid, urls in MANUAL_URLS.items():
        for url in urls:
            if url not in source_urls[bid]:
                source_urls[bid].append(url)
    return dict(source_urls)


def apply_source_urls(results: list[dict[str, Any]], source_urls: dict[str, list[str]]) -> None:
    for row in results:
        if not row["source_url"] and source_urls.get(row["benchmark_id"]):
            row["source_url"] = source_urls[row["benchmark_id"]][0]


def build_metrics(results: list[dict[str, Any]], dim_names: dict[str, str]) -> list[dict[str, Any]]:
    seen: set[tuple[str, str]] = set()
    metrics = []
    for r in results:
        key = (r["benchmark_id"], r["metric_original"])
        if key in seen:
            continue
        seen.add(key)
        metric = {
            "benchmark_id": r["benchmark_id"],
            "metric_original": r["metric_original"],
            "metric_full_name": r["metric_original"],
            "metric_normalized": r["metric_normalized"],
            "dimension_ids": r["dimension_ids"],
            "scoring_method": scoring_method(r["benchmark_id"], r["metric_original"]),
            "evaluator_type": r["evaluator_type"],
            "higher_is_better": r["higher_is_better"],
            "source_url": r["source_url"],
        }
        metrics.append(metric)
    covered = {d for m in metrics for d in m["dimension_ids"]}
    missing = sorted(set(dim_names) - covered)
    for did in missing:
        metrics.append(
            {
                "benchmark_id": f"dimension_gap_{did.lower()}",
                "metric_original": "no_unified_leaderboard",
                "metric_full_name": "No unified public leaderboard found in local sources",
                "metric_normalized": "无统一公开榜单",
                "dimension_ids": [did],
                "scoring_method": "本地资料只确认数据资源或任务方向，尚无统一公开模型榜单；需自建任务协议后评测。",
                "evaluator_type": "not_applicable",
                "higher_is_better": False,
                "source_url": "",
            }
        )
    return sorted(metrics, key=lambda x: (x["benchmark_id"], x["metric_original"]))


def scoring_method(bid: str, metric: str) -> str:
    low = metric.lower()
    if metric == "no_unified_leaderboard":
        return "无统一公开模型榜单；记录为缺失状态，不参与分数排序。"
    if "pass@" in low:
        return "运行测试用例后估计 pass@k。"
    if "qwk" in low or bid == "essayjudge":
        return "模型评分与人工评分之间计算 Quadratic Weighted Kappa 或 trait-level 一致性。"
    if low.startswith("ccs") or low.startswith("ecs") or bid == "sas_bench":
        return "比较模型评分、分步评分或错误类型分布与人工标注的一致性。"
    if bid in {"edubench", "eduvisbench", "tutorbench", "mathtutorbench"}:
        return "按 benchmark rubric 由自动评测、模型评委或成对胜率聚合。"
    if bid == "interactscience":
        return "用程序功能测试和视觉质量测试检查交互式科学演示。"
    return "按 benchmark 原始协议计算该指标；通常为 exact match、平均正确率或官方汇总分。"


def build_benchmarks(
    results: list[dict[str, Any]],
    authority: dict[str, dict[str, Any]],
    source_urls: dict[str, list[str]],
) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for r in results:
        grouped[r["benchmark_id"]].append(r)
    records = []
    for bid, rows in grouped.items():
        name = rows[0]["benchmark_name"]
        has_model = any(r["score_text"] != "no_unified_leaderboard" for r in rows)
        primary = sorted({r["metric_original"] for r in rows if r["metric_original"] != "no_unified_leaderboard"})
        if not primary:
            primary = ["no_unified_leaderboard"]
        domain, task = MANUAL_META.get(bid, ("教育资源/数据集", "requires_task_protocol"))
        urls = []
        for url in source_urls.get(bid, []):
            if url not in urls:
                urls.append(url)
        for url in sorted({r["source_url"] for r in rows if r["source_url"]}):
            if url not in urls:
                urls.append(url)
        record = {
                "benchmark_id": bid,
                "benchmark_name": name,
                "domain": domain,
                "task_type": task,
                "has_unified_leaderboard": has_model,
                "has_model_results": has_model,
                "primary_metrics": primary,
                "source_urls": urls,
                "notes": benchmark_notes(bid, rows),
        }
        record.update(
            authority.get(
                bid,
                {
                    "authority_score": None,
                    "authority_score_text": "",
                    "authority_score_type": "",
                    "authority_usage_ecosystem": "",
                    "authority_reason": "",
                    "authority_source_section": "",
                },
            )
        )
        records.append(record)
    return sorted(records, key=lambda x: x["benchmark_id"])


def benchmark_notes(bid: str, rows: list[dict[str, Any]]) -> str:
    if not any(r["score_text"] != "no_unified_leaderboard" for r in rows):
        return "本地 survey 明确标注未找到可直接引用的官方统一模型 leaderboard；保留为资源/任务协议候选。"
    if bid == "k12vista":
        return "过程正确性包含步骤跳跃、幻觉、逻辑矛盾和图文误解。"
    if bid == "eduguard_bench":
        return "教学角色扮演质量与安全 ASR 不一致，且原论文正文和图表有一处 Qwen2.5-72B ASR 表述冲突。"
    if bid == "mathtutorbench":
        return "区分解题、学生错误定位、纠错、脚手架和教学指令遵循。"
    return ""


def build_dimension_mapping(metrics: list[dict[str, Any]], dim_names: dict[str, str]) -> list[dict[str, Any]]:
    rows = []
    for m in metrics:
        for did in m["dimension_ids"]:
            rows.append(
                {
                    "benchmark_id": m["benchmark_id"],
                    "metric_original": m["metric_original"],
                    "dimension_id": did,
                    "dimension_name": dim_names.get(did, ""),
                    "mapping_type": "direct_or_benchmark_level",
                    "rationale": f"{m['metric_normalized']} maps to {dim_names.get(did, did)} based on the 2026-05-12 taxonomy and benchmark task definition.",
                    "source_url": m["source_url"],
                }
            )
    return sorted(rows, key=lambda x: (x["dimension_id"], x["benchmark_id"], x["metric_original"]))


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")


def write_log(path: Path, log_rows: list[dict[str, Any]], results: list[dict[str, Any]], metrics: list[dict[str, Any]], benchmarks: list[dict[str, Any]]) -> None:
    extracted = [r for r in results if r["score_text"] != "no_unified_leaderboard"]
    no_lb = [r for r in results if r["score_text"] == "no_unified_leaderboard"]
    lines = [
        "# Exhaustive Extraction Log",
        "",
        "生成日期：2026-05-13",
        "",
        "## 总览",
        "",
        f"- benchmarks.jsonl：{len(benchmarks)} 条 benchmark/resource 记录。",
        f"- metrics.jsonl：{len(metrics)} 条 benchmark-native 指标记录。",
        f"- results.jsonl：{len(results)} 条结果记录，其中模型分数 {len(extracted)} 条，no_unified_leaderboard {len(no_lb)} 条。",
        "- 旧 `data/model_dimension_performance_2026-05-12.json` 是代表性抽取，只保留为摘要参考；本目录作为全量本地结构化结果库。",
        "- 本轮未把多列指标压成 average；Markdown 表格中的每个模型 × 指标单元格单独保留。",
        "- 在线补充结果来自 `edu_benchmark_survey_supplement_2026-05-11.md` 中已核验描述；本脚本未重新抓取外部网页。",
        "- 2026-05-13 额外人工抽查了 MathVista 项目页、OlymMATH、MathTutorBench、SAS-Bench 官方仓库；只确认来源与已记录结果，不从网页推断或补编新分数。",
        "",
        "## 表格抽取状态",
        "",
        "| Source | Section | Benchmark | Markdown rows | Result records | Status | Notes |",
        "|---|---|---|---:|---:|---|---|",
    ]
    for row in log_rows:
        lines.append(
            f"| {row['source_file']} | {row['source_section']} | {row['benchmark']} | {row['markdown_rows']} | {row['result_records']} | {row['status']} | {row['notes']} |"
        )
    by_bench = defaultdict(int)
    for r in extracted:
        by_bench[r["benchmark_name"]] += 1
    lines += ["", "## 已抽取模型结果覆盖", ""]
    for name, count in sorted(by_bench.items()):
        lines.append(f"- {name}: {count} result records")
    lines += ["", "## 缺失/无榜单处理", ""]
    for r in no_lb:
        lines.append(f"- {r['benchmark_name']}: {r['notes']}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_reports(
    results: list[dict[str, Any]],
    metrics: list[dict[str, Any]],
    benchmarks: list[dict[str, Any]],
    dim_names: dict[str, str],
) -> None:
    bench_by_id = {b["benchmark_id"]: b for b in benchmarks}
    metrics_by_dim: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for m in metrics:
        for did in m["dimension_ids"]:
            metrics_by_dim[did].append(m)
    results_by_bench_metric: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for r in results:
        results_by_bench_metric[(r["benchmark_id"], r["metric_original"])].append(r)

    md = [
        "# AI-Edu Benchmark Exhaustive Index",
        "",
        "生成日期：2026-05-13",
        "",
        "本报告基于 `data/exhaustive_2026-05-13/` 的 JSONL 文件生成。旧 `data/model_dimension_performance_2026-05-12.json` 是代表性抽取，不作为全量结果库。",
        "",
        f"- Benchmarks/resources: {len(benchmarks)}",
        f"- Metrics: {len(metrics)}",
        f"- Result records: {len(results)}",
        "",
        "## 按原子能力浏览",
        "",
    ]
    for did in sorted(dim_names):
        md.append(f"### {did} {dim_names[did]}")
        grouped = defaultdict(list)
        for m in metrics_by_dim.get(did, []):
            grouped[m["benchmark_id"]].append(m)
        for bid in sorted(grouped):
            b = bench_by_id.get(bid, {"benchmark_name": bid, "source_urls": []})
            md.append(f"- **{b['benchmark_name']}** ({bid})")
            for m in sorted(grouped[bid], key=lambda x: x["metric_original"]):
                row_count = len(results_by_bench_metric.get((bid, m["metric_original"]), []))
                md.append(f"  - {m['metric_original']} / {m['metric_normalized']}: {row_count} result rows")
        md.append("")
    MD_REPORT.write_text("\n".join(md), encoding="utf-8")

    parts = [
        "<!doctype html><html lang='zh-CN'><head><meta charset='utf-8'>",
        "<title>AI-Edu Benchmark Exhaustive Index</title>",
        "<style>body{font-family:system-ui,-apple-system,Segoe UI,sans-serif;margin:24px;line-height:1.5;color:#202124}table{border-collapse:collapse;width:100%;margin:8px 0 16px}th,td{border:1px solid #dadce0;padding:6px 8px;vertical-align:top}th{background:#f8f9fa}details{margin:10px 0}summary{font-weight:650;cursor:pointer}.meta{color:#5f6368}</style>",
        "</head><body>",
        "<h1>AI-Edu Benchmark Exhaustive Index</h1>",
        f"<p class='meta'>Generated 2026-05-13. Benchmarks/resources: {len(benchmarks)}; metrics: {len(metrics)}; result records: {len(results)}.</p>",
        "<p>旧 <code>data/model_dimension_performance_2026-05-12.json</code> 是代表性抽取；本页按“原子能力 -> benchmark -> 指标 -> 模型结果”浏览 exhaustive JSONL。</p>",
    ]
    for did in sorted(dim_names):
        parts.append(f"<details open><summary>{html.escape(did)} {html.escape(dim_names[did])}</summary>")
        grouped = defaultdict(list)
        for m in metrics_by_dim.get(did, []):
            grouped[m["benchmark_id"]].append(m)
        for bid in sorted(grouped):
            b = bench_by_id.get(bid, {"benchmark_name": bid, "source_urls": []})
            parts.append(f"<h3>{html.escape(b['benchmark_name'])} <span class='meta'>({html.escape(bid)})</span></h3>")
            urls = ", ".join(f"<a href='{html.escape(u)}'>{html.escape(u)}</a>" for u in b.get("source_urls", [])[:3])
            if urls:
                parts.append(f"<p class='meta'>{urls}</p>")
            for m in sorted(grouped[bid], key=lambda x: x["metric_original"]):
                rows = results_by_bench_metric.get((bid, m["metric_original"]), [])
                parts.append(f"<details><summary>{html.escape(m['metric_original'])} / {html.escape(m['metric_normalized'])} ({len(rows)} rows)</summary>")
                parts.append("<table><thead><tr><th>Model</th><th>Score</th><th>Setting</th><th>Subset</th><th>Source</th><th>Notes</th></tr></thead><tbody>")
                for r in rows:
                    parts.append(
                        "<tr>"
                        f"<td>{html.escape(r['model'])}</td>"
                        f"<td>{html.escape(r['score_text'])}</td>"
                        f"<td>{html.escape(r['setting'])}</td>"
                        f"<td>{html.escape(r['subset'])}</td>"
                        f"<td>{html.escape(r['source_file'] + ' / ' + r['source_section'])}</td>"
                        f"<td>{html.escape(r['notes'])}</td>"
                        "</tr>"
                    )
                parts.append("</tbody></table></details>")
        parts.append("</details>")
    parts.append("</body></html>")
    HTML_REPORT.write_text("".join(parts), encoding="utf-8")


def dataset_repo_from_hf(url: str) -> str:
    m = re.search(r"huggingface\.co/datasets/([^/?#]+/[^/?#]+)", url)
    return m.group(1) if m else ""


def github_clone_url(url: str) -> str:
    m = re.search(r"(https://github\.com/[^/?#]+/[^/?#]+)", url)
    return m.group(1).rstrip("/") if m else ""


def kaggle_competition_slug(url: str) -> str:
    m = re.search(r"kaggle\.com/c/([^/?#]+)", url)
    return m.group(1) if m else ""


def build_dataset_acquisition(benchmarks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    records = []
    for b in benchmarks:
        bid = b["benchmark_id"]
        urls = b.get("source_urls", [])
        commands = []
        manual_steps = []
        access_modes = []
        for url in urls:
            hf_repo = dataset_repo_from_hf(url)
            gh_url = github_clone_url(url)
            kaggle_slug = kaggle_competition_slug(url)
            if hf_repo:
                access_modes.append("huggingface_dataset")
                commands.append(f"huggingface-cli download --repo-type dataset {hf_repo} --local-dir sources/datasets/{bid}")
            elif gh_url:
                access_modes.append("github_repository")
                commands.append(f"git clone --depth 1 {gh_url} sources/datasets/{bid}")
            elif kaggle_slug:
                access_modes.append("kaggle_competition")
                commands.append(f"kaggle competitions download -c {kaggle_slug} -p sources/datasets/{bid}")
                manual_steps.append("requires Kaggle account, competition terms acceptance, and API token")
            elif "arxiv.org" in url or url.endswith(".pdf"):
                access_modes.append("paper_or_pdf")
            else:
                access_modes.append("project_page_or_manual")
        access_modes = sorted(set(access_modes)) or ["missing_source_url"]
        if commands:
            status = "download_command_available_not_bulk_downloaded"
        elif "paper_or_pdf" in access_modes and len(access_modes) == 1:
            status = "paper_only_or_release_pending"
        else:
            status = "manual_access_or_metadata_only"
        records.append(
            {
                "benchmark_id": bid,
                "benchmark_name": b["benchmark_name"],
                "domain": b["domain"],
                "task_type": b["task_type"],
                "has_model_results": b["has_model_results"],
                "access_modes": access_modes,
                "dataset_status": status,
                "recommended_local_path": f"sources/datasets/{bid}",
                "download_commands": sorted(set(commands)),
                "manual_steps": sorted(set(manual_steps)),
                "source_urls": urls,
                "notes": "Bulk download is intentionally not executed by this generator because many datasets are large, gated, licensed, or require manual terms acceptance. Use commands selectively.",
            }
        )
    return sorted(records, key=lambda x: (x["dataset_status"], x["benchmark_id"]))


def write_dataset_acquisition_report(path: Path, rows: list[dict[str, Any]]) -> None:
    by_status: dict[str, int] = defaultdict(int)
    by_access: dict[str, int] = defaultdict(int)
    for row in rows:
        by_status[row["dataset_status"]] += 1
        for mode in row["access_modes"]:
            by_access[mode] += 1
    lines = [
        "# AI-Edu Benchmark Dataset Acquisition Manifest",
        "",
        "生成日期：2026-05-13",
        "",
        "本文件回答 `todo.md` 中“下载其数据集”的可执行层面：对每个 benchmark/resource 记录数据入口、建议本地路径、可用下载命令和人工申请风险。为避免误下超大、闭源、需授权或需同意条款的数据，本脚本只生成下载清单，不默认批量下载。",
        "",
        "## 状态统计",
        "",
        "| Status | Count |",
        "|---|---:|",
    ]
    for status, count in sorted(by_status.items()):
        lines.append(f"| {status} | {count} |")
    lines += ["", "## 入口类型统计", "", "| Access mode | Count |", "|---|---:|"]
    for mode, count in sorted(by_access.items()):
        lines.append(f"| {mode} | {count} |")
    lines += [
        "",
        "## 可直接执行的下载入口",
        "",
        "| Benchmark | Local path | Commands / manual notes |",
        "|---|---|---|",
    ]
    for row in rows:
        command_text = "<br>".join(f"`{cmd}`" for cmd in row["download_commands"])
        manual_text = "<br>".join(row["manual_steps"])
        if not command_text:
            command_text = row["dataset_status"]
        if manual_text:
            command_text = f"{command_text}<br>{manual_text}"
        lines.append(f"| {row['benchmark_name']} | `{row['recommended_local_path']}` | {command_text} |")
    lines += [
        "",
        "## 使用建议",
        "",
        "- 优先下载 `huggingface_dataset` 和 `github_repository` 类型；Kaggle、Google Drive、机构页面和产品页通常需要人工确认条款。",
        "- `sources/` 已在 `.gitignore` 中，不会把大数据集误提交到仓库。",
        "- 只作为训练语料的数据集（如 FineWeb-Edu）不应直接当作评测结论；需要先定义任务、切分、指标和污染检查。",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_web_update_note(path: Path) -> None:
    path.write_text(
        "\n".join(
            [
                "# Web-Verified Emerging AI-Edu Benchmark Updates",
                "",
                "生成日期：2026-05-13",
                "",
                "本文件记录本轮为补齐 `todo.md` 的全量性而额外核验的 2025-2026 新兴教育 benchmark / 数据资源。",
                "",
                "## ConvoLearn",
                "",
                "- Source: https://scale.stanford.edu/ai/repository/convolearn-dataset-constructivist-tutor-student-dialogue",
                "- Dataset: https://huggingface.co/datasets/masharma/convolearn",
                "- ArXiv PDF: https://arxiv.org/pdf/2601.08950v1",
                "- Stanford SCALE page states ConvoLearn has 1,250 middle-school Earth Science tutor-student dialogues and six constructivist pedagogy dimensions; it reports teacher human-evaluation means for fine-tuned Mistral 7B, base Mistral 7B, and Claude Sonnet 4.5.",
                "",
                "## PEBBLE",
                "",
                "- Source: https://openreview.net/forum?id=ffvNvoJVgE",
                "- OpenReview describes a multi-turn tutoring benchmark with scaffolding, diagnostic questioning, misconception repair, metacognitive support, affective support, overhelping penalty, contamination controls, and planned release of code/seeds/personas/judge prompts/leaderboard specification.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def verify(outdir: Path) -> dict[str, Any]:
    required_result_keys = {"benchmark_id", "benchmark_name", "model", "metric_original", "score_text", "source_file"}
    stats = {}
    for name in ("benchmarks.jsonl", "metrics.jsonl", "results.jsonl", "dimension_mapping.jsonl"):
        count = 0
        for line_no, line in enumerate((outdir / name).read_text(encoding="utf-8").splitlines(), start=1):
            row = json.loads(line)
            if name == "results.jsonl":
                missing = required_result_keys - set(row)
                if missing:
                    raise ValueError(f"{name}:{line_no} missing {missing}")
            count += 1
        stats[name] = count
    metrics = [json.loads(l) for l in (outdir / "metrics.jsonl").read_text(encoding="utf-8").splitlines()]
    dim_covered = {d for m in metrics for d in m.get("dimension_ids", [])}
    expected = {f"D{i:02d}" for i in range(1, 25)}
    missing_dims = sorted(expected - dim_covered)
    if missing_dims:
        raise ValueError(f"Missing dimension coverage: {missing_dims}")
    stats["covered_dimensions"] = len(dim_covered)
    return stats


def main() -> None:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    dim_names, bench_dims, _metric_dims, _indicators = load_dimension_maps()
    tables = parse_tables(SURVEY) + parse_tables(SUPPLEMENT)
    source_urls = extract_source_urls(tables)
    results, logs = extract_appendix_results(tables, bench_dims)
    supplement = supplement_results(bench_dims)
    results.extend(supplement)
    logs.append(
        {
            "source_file": SUPPLEMENT.name,
            "source_section": "一、旧模型结果的线上补充 / 可补充进原报告的代表性新结果",
            "benchmark": "multiple_benchmarks",
            "markdown_rows": 14,
            "result_records": len(supplement),
            "status": "supplement_representative_updates_extracted",
            "notes": "按补充文件中明确列出的模型-分数展开；不覆盖 survey 原始结果。",
        }
    )
    no_lb, no_lb_logs = no_leaderboard_results(tables, bench_dims)
    results.extend(no_lb)
    logs.extend(no_lb_logs)
    extra_results, extra_authority, extra_logs = extra_resource_results(bench_dims)
    results.extend(extra_results)
    logs.extend(extra_logs)
    authority, authority_logs = extract_authority(tables)
    authority.update(extra_authority)
    logs.extend(authority_logs)
    apply_source_urls(results, source_urls)
    results = sorted(results, key=lambda r: (r["benchmark_id"], r["source_file"], r["source_section"], r["model"], r["metric_original"]))
    metrics = build_metrics(results, dim_names)
    benchmarks = build_benchmarks(results, authority, source_urls)
    mapping = build_dimension_mapping(metrics, dim_names)
    dataset_acquisition = build_dataset_acquisition(benchmarks)
    write_jsonl(OUTDIR / "benchmarks.jsonl", benchmarks)
    write_jsonl(OUTDIR / "metrics.jsonl", metrics)
    write_jsonl(OUTDIR / "results.jsonl", results)
    write_jsonl(OUTDIR / "dimension_mapping.jsonl", mapping)
    write_jsonl(OUTDIR / "dataset_acquisition.jsonl", dataset_acquisition)
    write_log(OUTDIR / "extraction_log.md", logs, results, metrics, benchmarks)
    write_dataset_acquisition_report(OUTDIR / "dataset_acquisition_report.md", dataset_acquisition)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    write_web_update_note(REPORT_DIR / "web_verified_updates_2026-05-13.md")
    write_reports(results, metrics, benchmarks, dim_names)
    stats = verify(OUTDIR)
    stats["dataset_acquisition.jsonl"] = len(dataset_acquisition)
    print(json.dumps(stats, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
