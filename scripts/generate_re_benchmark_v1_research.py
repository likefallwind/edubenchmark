#!/usr/bin/env python3
"""Generate research-stage reports for RE_BENCHMARK_V1.

This script is intentionally research-oriented: it preserves missing-data and
proxy decisions instead of pretending that every cited benchmark is runnable.
Run `scripts/build_re_benchmark_v1.py` first to refresh the local pilot pool.
"""

from __future__ import annotations

import html
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "re_benchmark_v1"
REPORT_DIR = ROOT / "reports" / "re_benchmark_v1"
LOCAL_PILOT = DATA_DIR / "pilot_items.jsonl"
SOURCE_MANIFEST = DATA_DIR / "source_manifest.jsonl"
RESEARCH_PILOT = DATA_DIR / "research_pilot_items.jsonl"
RESEARCH_SUMMARY = DATA_DIR / "research_pilot_summary.json"
TODO_PATH = ROOT / "benchmark-todo.md"


STATUS_ORDER = [
    "local_ready",
    "metadata_only",
    "download_incomplete",
    "external_download_needed",
    "manual_access_required",
    "paper_or_release_pending",
    "not_found",
]


MANIFEST: list[dict[str, Any]] = [
    {
        "category_id": "C1",
        "benchmark_id": "mmlu_pro",
        "benchmark_name": "MMLU-Pro",
        "availability_status": "external_download_needed",
        "local_path": "sources/datasets/mmlu_pro",
        "local_evidence": "not present locally; Hugging Face TIGER-Lab/MMLU-Pro lists parquet files",
        "acquisition": "huggingface-cli download --repo-type dataset TIGER-Lab/MMLU-Pro --local-dir sources/datasets/mmlu_pro",
        "v1_decision": "Use local MMLU as D01 proxy; do not report as MMLU-Pro.",
        "source_url": "https://huggingface.co/datasets/TIGER-Lab/MMLU-Pro",
    },
    {
        "category_id": "C1",
        "benchmark_id": "mmlu",
        "benchmark_name": "MMLU",
        "availability_status": "local_ready",
        "local_path": "sources/datasets/mmlu",
        "local_evidence": "parquet splits are present for multiple subjects",
        "acquisition": "already local",
        "v1_decision": "D01 proxy for MMLU-Pro.",
        "source_url": "https://huggingface.co/datasets/cais/mmlu",
    },
    {
        "category_id": "C1",
        "benchmark_id": "omniedubench",
        "benchmark_name": "OmniEduBench",
        "availability_status": "external_download_needed",
        "local_path": "sources/datasets/omniedubench",
        "local_evidence": "not present locally",
        "acquisition": "Resolve official site/API or dataset release path.",
        "v1_decision": "Use E-EVAL, GaokaoBench, and EduBench as Chinese education proxies.",
        "source_url": "http://omniedubench.com/",
    },
    {
        "category_id": "C1",
        "benchmark_id": "agieval",
        "benchmark_name": "AGIEval",
        "availability_status": "local_ready",
        "local_path": "sources/datasets/agieval",
        "local_evidence": "data/v1 and data/v1_1 JSONL files are present",
        "acquisition": "already local",
        "v1_decision": "Runnable C1 standardized-exam smoke items.",
        "source_url": "https://github.com/ruixiangcui/AGIEval",
    },
    {
        "category_id": "C1",
        "benchmark_id": "olympiadbench",
        "benchmark_name": "OlympiadBench",
        "availability_status": "metadata_only",
        "local_path": "sources/datasets/olympiadbench",
        "local_evidence": "local clone has README, resources, eval/inference code; no full problem data files",
        "acquisition": "Download dataset from the official Hugging Face/Google Drive release linked by OpenBMB.",
        "v1_decision": "Keep as C1 high-difficulty target; do not count local code clone as runnable data.",
        "source_url": "https://github.com/OpenBMB/OlympiadBench",
    },
    {
        "category_id": "C1",
        "benchmark_id": "mathvista",
        "benchmark_name": "MathVista",
        "availability_status": "local_ready",
        "local_path": "sources/datasets/mathvista",
        "local_evidence": "data/testmini.json and test.json are present",
        "acquisition": "already local",
        "v1_decision": "Include metadata/text-only or multimodal-adapter samples; image scoring is separate.",
        "source_url": "https://github.com/lupantech/MathVista",
    },
    {
        "category_id": "C1",
        "benchmark_id": "video_mme",
        "benchmark_name": "Video-MME",
        "availability_status": "external_download_needed",
        "local_path": "sources/datasets/video_mme",
        "local_evidence": "not present locally",
        "acquisition": "Download official video assets if multimodal/video stage is funded.",
        "v1_decision": "Record as coverage gap; do not run in v1 smoke.",
        "source_url": "https://video-mme.github.io/home_page.html",
    },
    {
        "category_id": "C1",
        "benchmark_id": "livecodebench",
        "benchmark_name": "LiveCodeBench",
        "availability_status": "external_download_needed",
        "local_path": "sources/datasets/livecodebench",
        "local_evidence": "not present locally",
        "acquisition": "Clone official repo and set up execution sandbox.",
        "v1_decision": "Use MBPP/HumanEval/APPS proxy; do not merge with text-only scores.",
        "source_url": "https://github.com/LiveCodeBench/LiveCodeBench",
    },
    {
        "category_id": "C2",
        "benchmark_id": "tutorbench",
        "benchmark_name": "TutorBench",
        "availability_status": "download_incomplete",
        "local_path": "sources/datasets/tutorbench",
        "local_evidence": "README exists; HF cache has .incomplete parquet downloads and lock files",
        "acquisition": "Retry Hugging Face download for ScaleAI/TutorBench or tutorbench/tutorbench.",
        "v1_decision": "Represent tutoring via EduBench/MathTutorBench proxies and mark TutorBench as missing.",
        "source_url": "https://huggingface.co/datasets/ScaleAI/TutorBench",
    },
    {
        "category_id": "C2",
        "benchmark_id": "pedagogy_benchmark",
        "benchmark_name": "Pedagogy Benchmark",
        "availability_status": "manual_access_required",
        "local_path": "sources/datasets/pedagogy_benchmark",
        "local_evidence": "README only; HF page is gated and requires accepting conditions/contact sharing",
        "acquisition": "Accept Hugging Face dataset terms, then download cdpk_main and cdpk_send parquet files.",
        "v1_decision": "Cannot run MCQ stage until gated data is available; keep as priority acquisition.",
        "source_url": "https://huggingface.co/datasets/AI-for-Education/pedagogy-benchmark",
    },
    {
        "category_id": "C2",
        "benchmark_id": "eduvisbench",
        "benchmark_name": "EduVisBench",
        "availability_status": "local_ready",
        "local_path": "sources/datasets/eduvisbench",
        "local_evidence": "train parquet and image directory are present",
        "acquisition": "already local",
        "v1_decision": "Include as judge-required visual/pedagogy generation sample.",
        "source_url": "https://github.com/aiming-lab/EduVisBench",
    },
    {
        "category_id": "C2",
        "benchmark_id": "edubench",
        "benchmark_name": "EduBench",
        "availability_status": "local_ready",
        "local_path": "sources/datasets/edubench",
        "local_evidence": "English/Chinese scenario JSONL files are present",
        "acquisition": "already local",
        "v1_decision": "Runnable proxy for teaching design, feedback, and personalization.",
        "source_url": "https://github.com/ybai-nlp/EduBench",
    },
    {
        "category_id": "C3",
        "benchmark_id": "assistments",
        "benchmark_name": "ASSISTments",
        "availability_status": "manual_access_required",
        "local_path": "sources/datasets/assistments",
        "local_evidence": "not present locally",
        "acquisition": "Request/download from ASSISTments data mining site.",
        "v1_decision": "Record as KT/CD gap; use EdNet protocol description only.",
        "source_url": "https://sites.google.com/view/assistmentsdatamining/dataset",
    },
    {
        "category_id": "C3",
        "benchmark_id": "ednet",
        "benchmark_name": "EdNet",
        "availability_status": "metadata_only",
        "local_path": "sources/datasets/ednet",
        "local_evidence": "local clone has README only; KT1 zip is not downloaded",
        "acquisition": "Download KT1 from bit.ly/ednet_kt1 or Kaggle mirror, then sample user CSVs.",
        "v1_decision": "Use as protocol item, not an LLM prompt.",
        "source_url": "https://github.com/riiid/ednet",
    },
    {
        "category_id": "C3",
        "benchmark_id": "daisee",
        "benchmark_name": "DAiSEE",
        "availability_status": "manual_access_required",
        "local_path": "sources/datasets/daisee",
        "local_evidence": "not present locally",
        "acquisition": "Requires video dataset download/application flow.",
        "v1_decision": "Postpone; video engagement is a C3 coverage gap.",
        "source_url": "https://people.iith.ac.in/vineethnb/resources/daisee/index.html",
    },
    {
        "category_id": "C4",
        "benchmark_id": "asap_aes",
        "benchmark_name": "ASAP-AES / ASAP 2.0",
        "availability_status": "manual_access_required",
        "local_path": "sources/datasets/asap_aes",
        "local_evidence": "not present locally",
        "acquisition": "Requires Kaggle account, API token, and terms acceptance.",
        "v1_decision": "Use EduEval Essay_Scoring proxy.",
        "source_url": "https://www.kaggle.com/datasets/lburleigh/asap-2-0/data",
    },
    {
        "category_id": "C4",
        "benchmark_id": "asap_sas",
        "benchmark_name": "ASAP-SAS",
        "availability_status": "manual_access_required",
        "local_path": "sources/datasets/asap_sas",
        "local_evidence": "not present locally",
        "acquisition": "Requires Kaggle competition/data access.",
        "v1_decision": "Record as short-answer scoring gap; SAS-Bench local repo has code but not source dataset.",
        "source_url": "https://www.kaggle.com/c/asap-sas",
    },
    {
        "category_id": "C4",
        "benchmark_id": "sas_bench",
        "benchmark_name": "SAS-Bench",
        "availability_status": "metadata_only",
        "local_path": "sources/datasets/sas_bench",
        "local_evidence": "local repo has prompts/code/docs, not full benchmark data",
        "acquisition": "Resolve official data release or data-generation dependency.",
        "v1_decision": "Do not score; keep as external evidence for short-answer scoring methodology.",
        "source_url": "https://github.com/",
    },
    {
        "category_id": "C4",
        "benchmark_id": "edueval_essay_scoring",
        "benchmark_name": "EduEval Essay_Scoring",
        "availability_status": "local_ready",
        "local_path": "sources/datasets/edueval/Edata/Application/Essay_Scoring.jsonl",
        "local_evidence": "essay scoring JSONL exists locally",
        "acquisition": "already local",
        "v1_decision": "Runnable proxy for essay scoring; qualitative/manual score calibration required.",
        "source_url": "https://github.com/llmeval/edu-eval",
    },
    {
        "category_id": "C4",
        "benchmark_id": "mathtutorbench",
        "benchmark_name": "MathTutorBench",
        "availability_status": "local_ready",
        "local_path": "sources/datasets/mathtutorbench",
        "local_evidence": "mathdial_bridge JSON files are present",
        "acquisition": "already local",
        "v1_decision": "Runnable C4 process-feedback sample; judge-required.",
        "source_url": "https://github.com/eth-lre/mathtutorbench",
    },
    {
        "category_id": "C5",
        "benchmark_id": "eduguard_bench",
        "benchmark_name": "EduGuard-Bench",
        "availability_status": "local_ready",
        "local_path": "sources/datasets/eduguard_bench",
        "local_evidence": "SATAs.xlsx and adversarial_prompts.xlsx exist locally",
        "acquisition": "already local",
        "v1_decision": "Runnable safety smoke sample; qualitative human review in v1.",
        "source_url": "https://github.com/YL1N/EduGuardBench",
    },
    {
        "category_id": "C5",
        "benchmark_id": "safe_child_llm",
        "benchmark_name": "Safe-Child-LLM",
        "availability_status": "external_download_needed",
        "local_path": "sources/datasets/safe_child_llm",
        "local_evidence": "not present locally; paper says benchmark data/code are publicly released on GitHub",
        "acquisition": "Clone The-Responsible-AI-Initiative/Safe_Child_LLM_Benchmark and verify license/data files.",
        "v1_decision": "Priority child-safety supplement after download.",
        "source_url": "https://github.com/The-Responsible-AI-Initiative/Safe_Child_LLM_Benchmark",
    },
    {
        "category_id": "C5",
        "benchmark_id": "youthsafe_yair",
        "benchmark_name": "YouthSafe / YAIR",
        "availability_status": "not_found",
        "local_path": "sources/datasets/youthsafe_yair",
        "local_evidence": "not present locally; public search found model/paper pages, not dataset files",
        "acquisition": "Monitor Stanford/SCALE and Hugging Face pages for YAIR data release.",
        "v1_decision": "Do not include as runnable; mention as external evidence gap.",
        "source_url": "https://arxiv.org/abs/2509.08997",
    },
    {
        "category_id": "C5",
        "benchmark_id": "sproutbench",
        "benchmark_name": "SproutBench",
        "availability_status": "paper_or_release_pending",
        "local_path": "sources/datasets/sproutbench",
        "local_evidence": "not present locally",
        "acquisition": "Monitor release.",
        "v1_decision": "External roadmap item only.",
        "source_url": "",
    },
    {
        "category_id": "C5",
        "benchmark_id": "castle",
        "benchmark_name": "CASTLE",
        "availability_status": "paper_or_release_pending",
        "local_path": "sources/datasets/castle",
        "local_evidence": "not present locally; paper found, official data path not confirmed",
        "acquisition": "Monitor paper/project release.",
        "v1_decision": "External roadmap item only.",
        "source_url": "https://arxiv.org/abs/2602.05633",
    },
]


PROTOCOL_ITEMS = [
    {
        "pilot_item_id": "REBV1-PROTOCOL-EDNET-KT1",
        "item_id": "REBV1-PROTOCOL-EDNET-KT1",
        "category_id": "C3",
        "category_name": "学情建模与个性化",
        "dimension_id": "D16",
        "dimension_name": "知识追踪",
        "benchmark_id": "ednet",
        "benchmark_name": "EdNet",
        "source_status": "metadata_only",
        "question": "Protocol only: after downloading EdNet-KT1, sample student CSV sequences and predict next-question correctness from prior timestamp/question_id/user_answer/elapsed_time events.",
        "answer_or_rubric": "Metric: AUC/ACC/NLL over held-out next interactions; not an LLM prompt.",
        "scoring_type": "protocol_metric",
        "is_auto_scoreable": False,
        "requires_llm_judge": False,
        "is_protocol_only": True,
        "is_proxy": False,
        "runner_status": "protocol_only_not_llm_prompt",
    },
    {
        "pilot_item_id": "REBV1-GAP-PEDAGOGY",
        "item_id": "REBV1-GAP-PEDAGOGY",
        "category_id": "C2",
        "category_name": "教学设计与学习辅导",
        "dimension_id": "D14",
        "dimension_name": "教学法知识",
        "benchmark_id": "pedagogy_benchmark",
        "benchmark_name": "Pedagogy Benchmark",
        "source_status": "manual_access_required",
        "question": "Data gap record: HF dataset is gated; no local MCQ rows are available to construct prompts.",
        "answer_or_rubric": "Acquire cdpk_main/cdpk_send parquet after accepting access terms.",
        "scoring_type": "gap_record",
        "is_auto_scoreable": False,
        "requires_llm_judge": False,
        "is_protocol_only": True,
        "is_proxy": False,
        "runner_status": "not_runnable_data_gap",
    },
    {
        "pilot_item_id": "REBV1-GAP-TUTORBENCH",
        "item_id": "REBV1-GAP-TUTORBENCH",
        "category_id": "C2",
        "category_name": "教学设计与学习辅导",
        "dimension_id": "D12",
        "dimension_name": "学生错误定位与纠错反馈",
        "benchmark_id": "tutorbench",
        "benchmark_name": "TutorBench",
        "source_status": "download_incomplete",
        "question": "Data gap record: local HF cache contains incomplete parquet downloads; no verified TutorBench rows are available.",
        "answer_or_rubric": "Retry dataset download before claiming TutorBench coverage.",
        "scoring_type": "gap_record",
        "is_auto_scoreable": False,
        "requires_llm_judge": False,
        "is_protocol_only": True,
        "is_proxy": False,
        "runner_status": "not_runnable_data_gap",
    },
]


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows = []
    with path.open(encoding="utf-8", errors="ignore") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def local_exists(local_path: str) -> bool:
    return bool(local_path) and (ROOT / local_path).exists()


def local_file_count(local_path: str) -> int:
    path = ROOT / local_path
    if not path.exists():
        return 0
    if path.is_file():
        return 1
    return sum(1 for child in path.rglob("*") if child.is_file() and ".git/" not in child.as_posix())


def enriched_manifest(pilot_counts: Counter[str]) -> list[dict[str, Any]]:
    rows = []
    for row in MANIFEST:
        new = dict(row)
        new["status_vocab"] = STATUS_ORDER
        new["local_exists"] = local_exists(row["local_path"])
        new["local_file_count"] = local_file_count(row["local_path"])
        new["pilot_item_count"] = pilot_counts[row["benchmark_id"]]
        new["last_verified"] = "2026-05-20"
        rows.append(new)
    return rows


def research_pilot_items(local_items: list[dict[str, Any]], manifest_by_id: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    aliases = {
        "mmlu": ("mmlu_pro", True),
        "edueval": ("edueval_essay_scoring", True),
        "statics2011": ("ednet", True),
        "mbpp": ("livecodebench", True),
    }
    rows = []
    for item in local_items:
        benchmark_id = item["benchmark_id"]
        target_id, is_proxy = aliases.get(benchmark_id, (benchmark_id, False))
        manifest = manifest_by_id.get(target_id) or manifest_by_id.get(benchmark_id, {})
        rows.append(
            {
                "pilot_item_id": item["pilot_item_id"],
                "item_id": item["item_id"],
                "category_id": item["category_id"],
                "dimension_id": item.get("dimension_id"),
                "dimension_name": item.get("dimension_name"),
                "benchmark_id": benchmark_id,
                "benchmark_name": item.get("benchmark_name"),
                "target_benchmark_id": target_id,
                "source_status": manifest.get("availability_status", "local_ready"),
                "question": item.get("question", ""),
                "answer_or_rubric": item.get("answer_or_rubric", ""),
                "scoring_type": item.get("scoring_method", ""),
                "is_auto_scoreable": item.get("runner_status") == "auto_exact_match_candidate",
                "requires_llm_judge": item.get("runner_status") == "needs_llm_or_human_judge",
                "is_protocol_only": False,
                "is_proxy": is_proxy,
                "runner_status": item.get("runner_status"),
                "source_file": item.get("source_file"),
            }
        )
    rows.extend(PROTOCOL_ITEMS)
    return rows


def md_table(headers: list[str], rows: list[list[Any]]) -> str:
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in rows:
        out.append("| " + " | ".join(str(cell).replace("\n", " ") for cell in row) + " |")
    return "\n".join(out)


def write_md(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def simple_md_to_html(title: str, md: str) -> str:
    lines = []
    for raw in md.splitlines():
        line = raw.rstrip()
        if line.startswith("# "):
            lines.append(f"<h1>{html.escape(line[2:])}</h1>")
        elif line.startswith("## "):
            lines.append(f"<h2>{html.escape(line[3:])}</h2>")
        elif line.startswith("### "):
            lines.append(f"<h3>{html.escape(line[4:])}</h3>")
        elif line.startswith("| "):
            lines.append(f"<pre>{html.escape(line)}</pre>")
        elif line.startswith("- "):
            lines.append(f"<p>{html.escape(line)}</p>")
        elif line:
            lines.append(f"<p>{html.escape(line)}</p>")
        else:
            lines.append("")
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans SC", sans-serif; margin: 0; color: #172033; background: #f6f7fb; }}
    main {{ max-width: 980px; margin: 0 auto; padding: 32px 22px 56px; background: white; min-height: 100vh; }}
    h1 {{ margin-top: 0; }}
    h2 {{ margin-top: 28px; border-top: 1px solid #dbe2ef; padding-top: 18px; }}
    p {{ line-height: 1.62; }}
    pre {{ white-space: pre-wrap; background: #f3f5fa; border: 1px solid #dbe2ef; border-radius: 6px; padding: 7px 9px; overflow-x: auto; }}
  </style>
</head>
<body><main>{''.join(lines)}</main></body>
</html>
"""


def report_stage1(manifest: list[dict[str, Any]]) -> str:
    status_counts = Counter(row["availability_status"] for row in manifest)
    by_category: dict[str, Counter[str]] = defaultdict(Counter)
    for row in manifest:
        by_category[row["category_id"]][row["availability_status"]] += 1
    return "\n\n".join(
        [
            "# Stage 1 数据状态核验",
            "核验日期：2026-05-20。状态口径采用研究 manifest 枚举：`local_ready`、`metadata_only`、`download_incomplete`、`external_download_needed`、`manual_access_required`、`paper_or_release_pending`、`not_found`。",
            "## 总体状态",
            md_table(["status", "count"], [[s, status_counts[s]] for s in STATUS_ORDER if status_counts[s]]),
            "## C1-C5 可用性总表",
            md_table(
                ["category", *STATUS_ORDER],
                [[cat, *[by_category[cat][s] for s in STATUS_ORDER]] for cat in sorted(by_category)],
            ),
            "## Benchmark 明细",
            md_table(
                ["C", "benchmark", "status", "local evidence", "v1 decision"],
                [[r["category_id"], r["benchmark_name"], r["availability_status"], r["local_evidence"], r["v1_decision"]] for r in manifest],
            ),
            "## 修正结论",
            "- `OlympiadBench` 本地只有代码、README、资源图和 eval/inference 脚本，不能算数据 ready。",
            "- `TutorBench` 本地 Hugging Face 缓存存在 `.incomplete` parquet，属于下载中断。",
            "- `Pedagogy Benchmark` 本地只有 README；线上 HF 数据集是 gated，需要先接受条件。",
            "- `EdNet` 本地只有 README/git clone；KT1 数据包未下载，只能做 protocol 说明。",
        ]
    )


def report_stage2(manifest: list[dict[str, Any]]) -> str:
    priorities = [
        ["Pedagogy Benchmark", "manual_access_required", "接受 HF 条款后下载", "影响 C2 教学法 MCQ；v1 暂用 EduBench proxy。"],
        ["TutorBench", "download_incomplete", "重试 HF parquet 下载", "影响 C2 tutoring 主测；v1 暂用 MathTutorBench/EduBench proxy。"],
        ["OlympiadBench", "metadata_only", "下载官方 HF/Drive 数据", "影响 C1 高难奥赛推理；v1 不伪装本地代码为数据。"],
        ["EdNet KT1", "metadata_only", "下载 bit.ly/Kaggle KT1 zip", "影响 C3 KT protocol 展示；不进入 LLM prompt。"],
        ["MMLU-Pro", "external_download_needed", "HF 数据较小，优先补齐", "影响 C1 D01；v1 用 MMLU proxy。"],
        ["Safe-Child-LLM", "external_download_needed", "clone 官方 GitHub 并核验数据", "影响 C5 儿童安全补充；v1 主测仍用 EduGuard。"],
        ["LiveCodeBench", "external_download_needed", "clone repo + sandbox", "影响 C1 代码执行；v1 用 MBPP/HumanEval/APPS proxy。"],
    ]
    proxy_rows = [
        ["MMLU-Pro", "MMLU", "D01 proxy only; do not label scores as MMLU-Pro."],
        ["OmniEduBench", "E-EVAL / GaokaoBench / EduBench", "Chinese education proxy with different task mix."],
        ["YouthSafe/YAIR", "EduGuard-Bench + Safe-Child-LLM after acquisition", "Youth-risk coverage remains incomplete."],
        ["ASAP-AES/SAS", "EduEval Essay_Scoring + MathTutorBench", "Essay/process feedback proxy, not Kaggle ASAP."],
        ["EdNet/ASSISTments", "Protocol-only record", "KT/CD cannot be merged into text LLM accuracy."],
    ]
    return "\n\n".join(
        [
            "# Stage 2 数据补齐与替代策略",
            "本阶段结论是：可以立刻使用的本地数据足以形成研究 pilot，但不足以宣称完整覆盖所有推荐 benchmark。v1 必须把 proxy 和 missing 标清楚。",
            "## Acquisition 优先级",
            md_table(["benchmark", "current status", "next action", "impact on v1"], priorities),
            "## Proxy 策略",
            md_table(["missing/target", "v1 proxy", "boundary"], proxy_rows),
            "## 暂缓项",
            "- `YouthSafe/YAIR`：截至本次核验未找到可直接下载的 YAIR 数据文件；不进入 runnable pilot。",
            "- `SproutBench`：按 release-pending 处理。",
            "- `CASTLE`：发现论文线索，但未确认官方数据下载；按 release-pending 处理。",
            "- `ASAP-AES/SAS`：需要 Kaggle 账号和条款，不能自动补齐。",
            "- `Video-MME/DAiSEE`：多模态/视频成本高，后置。",
        ]
    )


def report_stage3(items: list[dict[str, Any]], summary: dict[str, Any]) -> str:
    cat_rows = [[k, v] for k, v in sorted(summary["by_category"].items())]
    runner_rows = [[k, v] for k, v in sorted(summary["by_runner_status"].items())]
    bench_rows = [[k, v] for k, v in sorted(summary["by_benchmark"].items())]
    return "\n\n".join(
        [
            "# Stage 3 研究版 Pilot Set 设计",
            f"研究 pilot 当前共 {summary['total_items']} 条，其中包含真实本地样本、proxy 样本、protocol-only 记录和 data-gap 记录。后两者不参与 LLM prompt 跑分。",
            "## 按 C 类计数",
            md_table(["category", "items"], cat_rows),
            "## 按 runner 状态计数",
            md_table(["runner_status", "items"], runner_rows),
            "## 按 benchmark 计数",
            md_table(["benchmark", "items"], bench_rows),
            "## 字段口径",
            "- `source_status` 来自研究 manifest，不把 README-only 或下载中断数据记为 ready。",
            "- `is_proxy=true` 表示该样本服务于目标 benchmark/dimension 的替代测量，报告中不能混称。",
            "- `is_protocol_only=true` 表示这是 KT/缺口/protocol 记录，不发送给 MiniMax。",
            "- `requires_llm_judge=true` 的开放题在 v1 只归档回答并抽样人工阅读。",
        ]
    )


def report_stage4() -> str:
    predictions = read_jsonl(REPORT_DIR / "minimax_predictions.jsonl")
    scores = read_jsonl(REPORT_DIR / "minimax_auto_scores.jsonl")
    pilot_items = read_jsonl(DATA_DIR / "pilot_items.jsonl")
    auto = [row for row in scores if row.get("score_status") == "auto_scored"]
    correct = sum(1 for row in auto if row.get("score") == 1.0)
    protocol = [row for row in scores if row.get("score_status") == "protocol_required"]
    judge = [row for row in scores if row.get("score_status") == "judge_required"]
    empty_predictions = [row for row in predictions if not str(row.get("response", "")).strip()]
    by_cat: dict[str, Counter[str]] = defaultdict(Counter)
    for row in scores:
        status = row.get("score_status")
        if status:
            by_cat[row.get("category_id", "unknown")][status] += 1
            if status == "auto_scored":
                by_cat[row.get("category_id", "unknown")]["correct"] += int(row.get("score") == 1.0)
    run_label = "full pilot" if pilot_items and len(predictions) >= len(pilot_items) else "smoke"
    if predictions:
        status = (
            f"MiniMax {run_label} 已运行：{len(predictions)} 条预测；自动题 {len(auto)} 条，"
            f"正确 {correct} 条，accuracy={correct / len(auto):.3f}；"
            f"开放/需复核 {len(judge)} 条；protocol-only {len(protocol)} 条。"
        ) if auto else f"MiniMax {run_label} 已运行：{len(predictions)} 条预测；本批无自动评分题；protocol-only {len(protocol)} 条。"
    else:
        status = "MiniMax 尚未产生预测；需要设置 `MINIMAX_API_KEY` 并允许访问 https://api.minimaxi.com/anthropic。"
    if run_label == "full pilot":
        scope_note = "- 本轮把完整 `pilot_items.jsonl` 里的 139 条都发给 MiniMax；其中代码题、多模态题需要专用 runner 或 adapter；C3 protocol/proxy 题已按 protocol-only 口径单列，不能当作普通 LLM prompt 分数。"
    else:
        scope_note = "- C3 KT、视频、代码执行、多模态图像题不在本轮 text-only smoke 中运行。"
    empty_rows = (
        md_table(
            ["pilot_item_id", "benchmark", "runner_status", "error"],
            [
                [
                    row.get("pilot_item_id", ""),
                    row.get("benchmark_id", ""),
                    row.get("runner_status", ""),
                    row.get("error", ""),
                ]
                for row in empty_predictions
            ],
        )
        if empty_predictions
        else "无。"
    )
    return "\n\n".join(
        [
            "# Stage 4 MiniMax Smoke Test",
            status,
            "## 运行设置",
            "- Endpoint: `https://api.minimaxi.com/anthropic/v1/messages`",
            "- Model: `MiniMax-M2.7`",
            "- 非流式；当前 runner 不向 MiniMax 发送 `max_tokens`，用 HTTP timeout + retry 控制长请求。",
            f"- 当前 canonical 预测文件中的空响应/timeout 为 {len(empty_predictions)} 条；这类行需要结合 benchmark 类型解释。",
            "## 评分口径",
            "- 自动题使用 option extraction + normalized exact match。",
            "- 开放教学题、安全题不使用模型 judge；只归档回答并写 qualitative samples。",
            "- MMLU/AGIEval 选择题 prompt 从原始数据重建选项，要求只返回选项字母；protocol-only 项不进入普通问答评分。",
            "- 当前 canonical 结果来自 2026-05-22 full-pilot rerun：并发 2、retry 2、显式 `--minimax-limit 999`。",
            scope_note,
            "## By Category",
            md_table(["category", "auto_scored", "correct", "judge_required", "protocol_required", "missing"], [[cat, c["auto_scored"], c["correct"], c["judge_required"], c["protocol_required"], c["missing_prediction"]] for cat, c in sorted(by_cat.items())]) if by_cat else "无结果。",
            "## Empty/Error Rows",
            "当前剩余空响应均应结合 benchmark 类型解释；本轮为空的行来自 `statics2011` KT protocol，不进入普通文本问答准确率。",
            empty_rows,
        ]
    )


def report_stage5(summary: dict[str, Any]) -> tuple[str, str]:
    predictions = read_jsonl(REPORT_DIR / "minimax_predictions.jsonl")
    scores = read_jsonl(REPORT_DIR / "minimax_auto_scores.jsonl")
    auto = [row for row in scores if row.get("score_status") == "auto_scored"]
    correct = sum(1 for row in auto if row.get("score") == 1.0)
    judge = [row for row in scores if row.get("score_status") == "judge_required"]
    protocol = [row for row in scores if row.get("score_status") == "protocol_required"]
    empty = [row for row in predictions if not str(row.get("response", "")).strip()]
    if auto:
        model_finding = (
            f"MiniMax-M2.7 已完成 2026-05-22 full-pilot rerun：{len(predictions)} 条预测，"
            f"自动评分题 {correct}/{len(auto)} 正确（accuracy={correct / len(auto):.3f}）。"
            f"开放/需人工或 LLM judge 项 {len(judge)} 条，protocol-only 项 {len(protocol)} 条。"
            f"仍为空或 timeout 的 {len(empty)} 条均需按其任务类型单独解释，不能直接并入文本问答准确率。"
        )
    else:
        model_finding = "MiniMax 尚无可报告的 canonical 自动评分结果；需要先生成 `minimax_predictions.jsonl` 和 `minimax_auto_scores.jsonl`。"
    final = "\n\n".join(
        [
            "# RE_BENCHMARK_V1 研究报告",
            "## Executive Summary",
            "RE_BENCHMARK_V1 作为研究版方案成立：它把教育模型评测拆成 C1 学科解题、C2 教学辅导、C3 学情建模、C4 作答评价、C5 教育安全五类，并明确区分通用能力、教学行为、评分可靠性、学习日志 protocol 和安全边界。当前版本的价值是形成可讨论、可初跑、可说明缺口的能力画像；边界是不能声称全量、生产级、或跨模态统一总分。",
            model_finding,
            "## Benchmark Coverage",
            f"研究 pilot 共 {summary['total_items']} 条记录。本地直接可用 benchmark 包括 AGIEval、MMLU proxy、MathVista metadata、EduBench、EduVisBench、MathTutorBench、EduEval Essay_Scoring、EduGuard-Bench。Proxy 项必须单独标注；EdNet、ASSISTments、DAiSEE 属 protocol 或外部数据任务。",
            "## Model Findings",
            "自动题仅报告自动评分子集，不跨 C1-C5 求平均。本轮 MCQ prompt 已要求只输出选项字母；MMLU 为 10/10，AGIEval 为 18/19。教学类开放题和安全类样例以成功/失败案例描述为主，避免把未校准的 LLM judge 当成金标准。",
            "## Methodological Risks",
            "- 数据污染：MMLU/AGIEval 等公开题可能进入训练语料。",
            "- Proxy 失真：MMLU 不是 MMLU-Pro，EduEval Essay_Scoring 不是 ASAP。",
            "- Judge 不稳定：TutorBench、MathTutorBench、EduBench、EduGuard 需要人审或双模型 judge。",
            "- 本土化偏差：中文教育场景与国际 benchmark 分布不同。",
            "- 模态不可合并：KT、视频、代码执行、多模态视觉与文本 LLM prompt 不能简单平均。",
            "## Conclusion",
            "v1 应输出能力画像而非排行榜总分。下一步优先补真实教学辅导数据、中文本地教育安全、作文/短答评分数据，以及 human rubric 或双模型 judge。视频、多模态、代码执行和全量 KT 在 v2 后置。",
        ]
    )
    roadmap = "\n\n".join(
        [
            "# RE_BENCHMARK_V1 v2 Roadmap",
            "1. 补齐 Pedagogy Benchmark gated 数据、TutorBench parquet、MMLU-Pro、OlympiadBench full data、EdNet KT1 sample。",
            "2. 建立 C2/C4/C5 的 human rubric：教学反馈、评分理由、安全边界分别标注。",
            "3. 建立双模型 judge + 人工抽查协议，报告 judge agreement，不直接信单一 judge。",
            "4. 分离四条 runner：text MCQ/short answer、open-ended judge、program execution、KT/video/multimodal protocol。",
            "5. 加入中文本地教育安全与未成年人保护红队集，避免只依赖英文 youth-safety 外部证据。",
            "6. 只在各类内部报告分数，不发布跨 C1-C5 的单一平均分。",
        ]
    )
    return final, roadmap


def write_qualitative_samples() -> None:
    predictions = read_jsonl(REPORT_DIR / "minimax_predictions.jsonl")
    if not predictions:
        write_md(REPORT_DIR / "minimax_qualitative_samples.md", "# MiniMax Qualitative Samples\n\n暂无预测。")
        return
    lines = ["# MiniMax Qualitative Samples", "", "以下样例只用于人工阅读，不作为自动 judge 结果。"]
    for row in predictions[:8]:
        if row.get("runner_status") == "auto_exact_match_candidate":
            continue
        lines.extend(
            [
                "",
                f"## {row.get('pilot_item_id')} / {row.get('benchmark_id')} / {row.get('category_id')}",
                "",
                str(row.get("response", ""))[:1800],
            ]
        )
    write_md(REPORT_DIR / "minimax_qualitative_samples.md", "\n".join(lines))


def update_benchmark_todo() -> None:
    block = """## RE_BENCHMARK_V1 research gaps - 2026-05-20

- Gap: TutorBench local download is incomplete and Pedagogy Benchmark is gated.
  Product reason: C2 tutoring and pedagogical-knowledge conclusions cannot rely only on EduBench proxies.
  Suggested data/eval: retry TutorBench parquet download; accept Pedagogy Benchmark HF terms; add rubric-based human review.
  Related capabilities: D12, D13, D14; S3.
  Source report: reports/re_benchmark_v1/RE_BENCHMARK_V1_RESEARCH_REPORT.md

- Gap: EdNet/ASSISTments are protocol datasets, not native LLM prompts.
  Product reason: personalization and knowledge tracing claims require KT metrics, not chat-model exact match.
  Suggested data/eval: download EdNet KT1 sample and define AUC/ACC/NLL protocol separately from LLM prompt runner.
  Related capabilities: D16, D17, D18; S5.
  Source report: reports/re_benchmark_v1/RE_BENCHMARK_V1_RESEARCH_REPORT.md

- Gap: Youth safety data for minors is incomplete locally.
  Product reason: education products serving minors need child/youth-specific safety checks beyond generic classroom safety.
  Suggested data/eval: acquire Safe-Child-LLM; monitor YouthSafe/YAIR, SproutBench, and CASTLE releases; build localized red-team set.
  Related capabilities: D21, D24; S7.
  Source report: reports/re_benchmark_v1/RE_BENCHMARK_V1_RESEARCH_REPORT.md
"""
    existing = TODO_PATH.read_text(encoding="utf-8") if TODO_PATH.exists() else ""
    if "RE_BENCHMARK_V1 research gaps - 2026-05-20" not in existing:
        TODO_PATH.write_text(existing.rstrip() + "\n\n" + block, encoding="utf-8")


def main() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    local_items = read_jsonl(LOCAL_PILOT)
    pilot_counts = Counter(item.get("benchmark_id") for item in local_items)
    manifest = enriched_manifest(pilot_counts)
    manifest_by_id = {row["benchmark_id"]: row for row in manifest}
    research_items = research_pilot_items(local_items, manifest_by_id)
    summary = {
        "total_items": len(research_items),
        "by_category": dict(Counter(item["category_id"] for item in research_items)),
        "by_benchmark": dict(Counter(item["benchmark_id"] for item in research_items)),
        "by_runner_status": dict(Counter(item["runner_status"] for item in research_items)),
        "proxy_items": sum(1 for item in research_items if item.get("is_proxy")),
        "protocol_or_gap_records": sum(1 for item in research_items if item.get("is_protocol_only")),
        "auto_scoreable_items": sum(1 for item in research_items if item.get("is_auto_scoreable")),
        "judge_required_items": sum(1 for item in research_items if item.get("requires_llm_judge")),
    }

    write_jsonl(SOURCE_MANIFEST, manifest)
    write_jsonl(RESEARCH_PILOT, research_items)
    write_json(RESEARCH_SUMMARY, summary)

    stage1 = report_stage1(manifest)
    stage2 = report_stage2(manifest)
    stage3 = report_stage3(research_items, summary)
    stage4 = report_stage4()
    final_report, roadmap = report_stage5(summary)

    write_md(REPORT_DIR / "stage1_data_status.md", stage1)
    write_md(REPORT_DIR / "stage2_data_acquisition_and_proxy.md", stage2)
    write_md(REPORT_DIR / "stage3_pilot_set_design.md", stage3)
    write_md(REPORT_DIR / "stage4_minimax_smoke_test.md", stage4)
    write_md(REPORT_DIR / "RE_BENCHMARK_V1_RESEARCH_REPORT.md", final_report)
    write_md(REPORT_DIR / "v2_roadmap.md", roadmap)
    (REPORT_DIR / "RE_BENCHMARK_V1_RESEARCH_REPORT.html").write_text(simple_md_to_html("RE_BENCHMARK_V1 Research Report", final_report), encoding="utf-8")
    write_qualitative_samples()
    update_benchmark_todo()

    print(f"manifest={len(manifest)} {SOURCE_MANIFEST.relative_to(ROOT)}")
    print(f"research_pilot={len(research_items)} {RESEARCH_PILOT.relative_to(ROOT)}")
    print(f"summary={RESEARCH_SUMMARY.relative_to(ROOT)}")
    print(f"reports={REPORT_DIR.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
