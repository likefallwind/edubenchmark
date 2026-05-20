#!/usr/bin/env python3
"""Build runnable RE_BENCHMARK_V1 assets.

This package turns re_benchmark_v1.md into a machine-readable registry,
source manifest, and a local-first pilot item set. It intentionally reuses the
existing 2026-05-18 item index so v1 can move toward execution without
resampling all upstream datasets.
"""

from __future__ import annotations

import html
import importlib.util
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SOURCE_MD = ROOT / "re_benchmark_v1.md"
ITEMS_IN = ROOT / "data" / "benchmark_v1_2026-05-18" / "items.jsonl"
ACQUISITION = ROOT / "data" / "exhaustive_2026-05-13" / "dataset_acquisition.jsonl"
OUT_DIR = ROOT / "data" / "re_benchmark_v1"
REPORT_DIR = ROOT / "reports" / "re_benchmark_v1"

REGISTRY_PATH = OUT_DIR / "benchmark_registry.jsonl"
SOURCE_MANIFEST_PATH = OUT_DIR / "source_manifest.jsonl"
PILOT_ITEMS_PATH = OUT_DIR / "pilot_items.jsonl"
PROMPTS_PATH = OUT_DIR / "pilot_prompts.jsonl"
README_PATH = OUT_DIR / "README.md"
REPORT_PATH = REPORT_DIR / "pilot_report.html"

TARGET_ITEMS_PER_CATEGORY = 60


CATEGORIES = [
    {
        "category_id": "C1",
        "name": "学科认知与问题求解",
        "short_name": "通用能力",
        "dimension_ids": ["D01", "D02", "D03", "D04", "D05", "D06", "D07", "D08"],
        "boundary": "偏会不会做题，不等同于会不会教。",
    },
    {
        "category_id": "C2",
        "name": "教学设计与学习辅导",
        "short_name": "教",
        "dimension_ids": ["D09", "D12", "D13", "D14", "D22", "D23"],
        "boundary": "关注教学行为；与 C4 的评分可靠性分开解释。",
    },
    {
        "category_id": "C3",
        "name": "学情建模与个性化",
        "short_name": "学",
        "dimension_ids": ["D15", "D16", "D17", "D18", "D20"],
        "boundary": "很多成熟评测是 EDM/LAK protocol，不一定是 LLM 原生 benchmark。",
    },
    {
        "category_id": "C4",
        "name": "作答评价与反馈",
        "short_name": "评",
        "dimension_ids": ["D10", "D11"],
        "boundary": "优先看评分一致性、rubric 和反馈可靠性。",
    },
    {
        "category_id": "C5",
        "name": "教育安全与伦理合规",
        "short_name": "安全",
        "dimension_ids": ["D21", "D24"],
        "boundary": "横切层；未成年人保护、角色边界和产品安全必须独立测。",
    },
]


BENCHMARKS = [
    {
        "category_id": "C1",
        "benchmark_id": "mmlu_pro",
        "benchmark_name": "MMLU-Pro",
        "role": "main",
        "dimensions": ["D01"],
        "status_hint": "downloadable_not_local",
        "source_urls": ["https://github.com/TIGER-AI-Lab/MMLU-Pro"],
        "pilot_action": "Use local MMLU as temporary proxy until MMLU-Pro is acquired.",
    },
    {
        "category_id": "C1",
        "benchmark_id": "omniedubench",
        "benchmark_name": "OmniEduBench",
        "role": "main",
        "dimensions": ["D02", "D04", "D15"],
        "status_hint": "manual_access_or_metadata_only",
        "source_urls": ["http://omniedubench.com/"],
        "pilot_action": "Use local E-EVAL/GaokaoBench/EduBench proxy items until data is available.",
    },
    {
        "category_id": "C1",
        "benchmark_id": "agieval",
        "benchmark_name": "AGIEval",
        "role": "main",
        "dimensions": ["D03"],
        "status_hint": "local_ready",
        "source_urls": ["https://github.com/ruixiangcui/AGIEval"],
    },
    {
        "category_id": "C1",
        "benchmark_id": "olympiadbench",
        "benchmark_name": "OlympiadBench",
        "role": "main",
        "dimensions": ["D05"],
        "status_hint": "local_ready",
        "source_urls": ["https://github.com/OpenBMB/OlympiadBench"],
    },
    {
        "category_id": "C1",
        "benchmark_id": "mathvista",
        "benchmark_name": "MathVista",
        "role": "main",
        "dimensions": ["D06"],
        "status_hint": "local_ready",
        "source_urls": ["https://github.com/lupantech/MathVista"],
    },
    {
        "category_id": "C1",
        "benchmark_id": "video_mme",
        "benchmark_name": "Video-MME",
        "role": "main",
        "dimensions": ["D07"],
        "status_hint": "needs_acquisition_entry",
        "source_urls": ["https://video-mme.github.io/home_page.html"],
        "pilot_action": "Use local SciVideoBench or LectureBank proxy while video pipeline is not ready.",
    },
    {
        "category_id": "C1",
        "benchmark_id": "livecodebench",
        "benchmark_name": "LiveCodeBench",
        "role": "main",
        "dimensions": ["D08"],
        "status_hint": "needs_acquisition_entry",
        "source_urls": ["https://github.com/LiveCodeBench/LiveCodeBench"],
        "pilot_action": "Use local HumanEval/MBPP/APPS proxy until sandbox runner is ready.",
    },
    {
        "category_id": "C2",
        "benchmark_id": "tutorbench",
        "benchmark_name": "TutorBench",
        "role": "main",
        "dimensions": ["D09", "D12", "D13"],
        "status_hint": "local_ready",
        "source_urls": ["https://huggingface.co/datasets/ScaleAI/TutorBench"],
    },
    {
        "category_id": "C2",
        "benchmark_id": "pedagogy_benchmark",
        "benchmark_name": "Pedagogy Benchmark",
        "role": "main",
        "dimensions": ["D14"],
        "status_hint": "local_ready",
        "source_urls": ["https://huggingface.co/datasets/AI-for-Education/pedagogy-benchmark"],
    },
    {
        "category_id": "C2",
        "benchmark_id": "eduvisbench",
        "benchmark_name": "EduVisBench",
        "role": "main",
        "dimensions": ["D22"],
        "status_hint": "local_ready",
        "source_urls": ["https://github.com/aiming-lab/EduVisBench"],
    },
    {
        "category_id": "C2",
        "benchmark_id": "edubench",
        "benchmark_name": "EduBench",
        "role": "main",
        "dimensions": ["D14", "D23"],
        "status_hint": "local_ready",
        "source_urls": ["https://github.com/ybai-nlp/EduBench"],
    },
    {
        "category_id": "C3",
        "benchmark_id": "assistments",
        "benchmark_name": "ASSISTments",
        "role": "main",
        "dimensions": ["D16", "D17"],
        "status_hint": "manual_access_or_metadata_only",
        "source_urls": ["https://sites.google.com/view/assistmentsdatamining/dataset"],
        "pilot_action": "Use local EdNet/STATICS2011 proxy until ASSISTments access is resolved.",
    },
    {
        "category_id": "C3",
        "benchmark_id": "ednet",
        "benchmark_name": "EdNet",
        "role": "main",
        "dimensions": ["D16", "D18"],
        "status_hint": "local_ready",
        "source_urls": ["https://github.com/riiid/ednet"],
    },
    {
        "category_id": "C3",
        "benchmark_id": "daisee",
        "benchmark_name": "DAiSEE",
        "role": "main",
        "dimensions": ["D20"],
        "status_hint": "needs_acquisition_entry",
        "source_urls": ["https://people.iith.ac.in/vineethnb/resources/daisee/index.html"],
        "pilot_action": "Keep D20 as a coverage gap until video-classification assets are acquired.",
    },
    {
        "category_id": "C4",
        "benchmark_id": "asap_aes",
        "benchmark_name": "ASAP-AES / ASAP 2.0",
        "role": "main",
        "dimensions": ["D10"],
        "status_hint": "manual_kaggle_required",
        "source_urls": ["https://www.kaggle.com/datasets/lburleigh/asap-2-0/data"],
        "pilot_action": "Use local EduEval essay scoring proxy until Kaggle access is configured.",
    },
    {
        "category_id": "C4",
        "benchmark_id": "asap_sas",
        "benchmark_name": "ASAP-SAS",
        "role": "main",
        "dimensions": ["D11"],
        "status_hint": "manual_kaggle_required",
        "source_urls": ["https://www.kaggle.com/c/asap-sas"],
        "pilot_action": "Use local SAS-Bench/Gaokao subjective proxy until Kaggle access is configured.",
    },
    {
        "category_id": "C4",
        "benchmark_id": "mathtutorbench",
        "benchmark_name": "MathTutorBench",
        "role": "main",
        "dimensions": ["D11", "D12"],
        "status_hint": "local_ready",
        "source_urls": ["https://github.com/eth-lre/mathtutorbench"],
    },
    {
        "category_id": "C5",
        "benchmark_id": "eduguard_bench",
        "benchmark_name": "EduGuard-Bench",
        "role": "main",
        "dimensions": ["D21"],
        "status_hint": "local_ready",
        "source_urls": ["https://github.com/YL1N/EduGuardBench"],
    },
    {
        "category_id": "C5",
        "benchmark_id": "youthsafe",
        "benchmark_name": "YouthSafe / YAIR",
        "role": "observe",
        "dimensions": ["D21"],
        "status_hint": "metadata_model_available_dataset_not_found",
        "source_urls": [
            "https://arxiv.org/abs/2509.08997",
            "https://huggingface.co/YouthSafe/YouthSafe-Teen-GAI-Risk",
        ],
        "pilot_action": "Do not include in runnable v1 until YAIR data is found or released.",
    },
    {
        "category_id": "C5",
        "benchmark_id": "safe_child_llm",
        "benchmark_name": "Safe-Child-LLM",
        "role": "supplement",
        "dimensions": ["D21"],
        "status_hint": "needs_acquisition_entry",
        "source_urls": ["https://github.com/The-Responsible-AI-Initiative/Safe_Child_LLM_Benchmark"],
        "pilot_action": "Add as the first child-safety supplement after data/license verification.",
    },
]


CATEGORY_BY_DIMENSION = {
    dimension_id: category["category_id"]
    for category in CATEGORIES
    for dimension_id in category["dimension_ids"]
}

PILOT_READY_BENCHMARK_IDS = {
    "mmlu",
    "agieval",
    "olympiadbench",
    "mathvista",
    "tutorbench",
    "pedagogy_benchmark",
    "eduvisbench",
    "edubench",
    "edueval",
    "ednet",
    "statics2011",
    "sas_bench",
    "mathtutorbench",
    "eduguard_bench",
    "humaneval",
    "mbpp",
    "apps_dataset",
    "scivideobench",
}


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


def acquisition_by_id() -> dict[str, dict[str, Any]]:
    return {row["benchmark_id"]: row for row in read_jsonl(ACQUISITION)}


def local_path_status(benchmark_id: str, acquisition: dict[str, dict[str, Any]]) -> tuple[str, str | None]:
    row = acquisition.get(benchmark_id, {})
    local_path = row.get("recommended_local_path")
    if local_path and (ROOT / local_path).exists():
        return "local_ready", local_path
    if local_path:
        return row.get("dataset_status", "not_local"), local_path
    return "not_in_acquisition_manifest", None


def build_registry(acquisition: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    category_names = {c["category_id"]: c["name"] for c in CATEGORIES}
    rows = []
    for benchmark in BENCHMARKS:
        local_status, local_path = local_path_status(benchmark["benchmark_id"], acquisition)
        if benchmark["status_hint"] in {"needs_acquisition_entry", "metadata_model_available_dataset_not_found"}:
            effective_status = benchmark["status_hint"]
        elif local_status == "local_ready":
            effective_status = "local_ready"
        else:
            effective_status = benchmark["status_hint"]
        rows.append(
            {
                **benchmark,
                "category_name": category_names[benchmark["category_id"]],
                "effective_status": effective_status,
                "local_path": local_path,
                "in_acquisition_manifest": benchmark["benchmark_id"] in acquisition,
            }
        )
    return rows


def build_source_manifest(
    registry: list[dict[str, Any]],
    acquisition: dict[str, dict[str, Any]],
    pilot_counts: Counter[str] | None = None,
) -> list[dict[str, Any]]:
    pilot_counts = pilot_counts or Counter()
    rows = []
    for benchmark in registry:
        acq = acquisition.get(benchmark["benchmark_id"], {})
        pilot_item_count = pilot_counts[benchmark["benchmark_id"]]
        if benchmark["effective_status"] == "local_ready" and pilot_item_count == 0:
            extraction_status = "local_ready_but_no_pilot_extractor"
        elif pilot_item_count > 0:
            extraction_status = "included_in_pilot"
        else:
            extraction_status = "not_in_runnable_pilot"
        rows.append(
            {
                "benchmark_id": benchmark["benchmark_id"],
                "benchmark_name": benchmark["benchmark_name"],
                "category_id": benchmark["category_id"],
                "role": benchmark["role"],
                "effective_status": benchmark["effective_status"],
                "extraction_status": extraction_status,
                "pilot_item_count": pilot_item_count,
                "local_path": benchmark.get("local_path"),
                "local_exists": bool(benchmark.get("local_path") and (ROOT / benchmark["local_path"]).exists()),
                "download_commands": acq.get("download_commands", []),
                "manual_steps": acq.get("manual_steps", []),
                "source_urls": benchmark.get("source_urls") or acq.get("source_urls", []),
                "pilot_action": benchmark.get("pilot_action", "Eligible for runnable pilot if item extraction exists."),
            }
        )
    return rows


def category_for_item(item: dict[str, Any]) -> str | None:
    benchmark_id = item.get("benchmark_id")
    dimension_id = item.get("dimension_id")
    if benchmark_id == "mathtutorbench" and dimension_id == "D12":
        # In re_benchmark_v1, MathTutorBench is also the C4 process feedback deep test.
        return "C4"
    return CATEGORY_BY_DIMENSION.get(dimension_id)


def build_pilot_items(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
    seen_source_keys: set[tuple[str, str, str, str]] = set()
    for item in items:
        category_id = category_for_item(item)
        if not category_id:
            continue
        benchmark_id = item.get("benchmark_id")
        source_file = item.get("source_file", "")
        if benchmark_id not in PILOT_READY_BENCHMARK_IDS:
            continue
        if source_file and not (ROOT / source_file).exists():
            continue
        key = (
            category_id,
            str(benchmark_id),
            str(source_file),
            str(item.get("source_row_or_key", "")),
        )
        if key in seen_source_keys:
            continue
        seen_source_keys.add(key)
        enriched = dict(item)
        enriched["category_id"] = category_id
        enriched["category_name"] = next(c["name"] for c in CATEGORIES if c["category_id"] == category_id)
        enriched["pilot_split"] = "smoke"
        enriched["runner_status"] = infer_runner_status(enriched)
        buckets[category_id].append(enriched)

    selected: list[dict[str, Any]] = []
    for category in CATEGORIES:
        category_id = category["category_id"]
        candidates = sorted(
            buckets.get(category_id, []),
            key=lambda row: (
                -float(row.get("quality_score", 0) or 0),
                row.get("dimension_id", ""),
                row.get("benchmark_id", ""),
                row.get("item_id", ""),
            ),
        )
        selected.extend(stratified_take(candidates, TARGET_ITEMS_PER_CATEGORY))

    for idx, item in enumerate(selected, 1):
        item["pilot_item_id"] = f"REBV1-{idx:04d}"
    return selected


def infer_runner_status(item: dict[str, Any]) -> str:
    evaluator_type = str(item.get("evaluator_type", "")).lower()
    scoring = str(item.get("scoring_method", "")).lower()
    modalities = set(item.get("input_modalities") or [])
    if "video" in modalities:
        return "needs_video_adapter"
    if "image" in modalities or "image_optional" in modalities:
        return "needs_multimodal_adapter"
    if "program" in scoring or "pass@" in scoring:
        return "needs_code_or_program_runner"
    if "judge" in evaluator_type or "human" in evaluator_type or "rubric" in scoring:
        return "needs_llm_or_human_judge"
    return "auto_exact_match_candidate"


def stratified_take(candidates: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    if len(candidates) <= limit:
        return candidates
    by_dimension: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for candidate in candidates:
        by_dimension[candidate.get("dimension_id", "unknown")].append(candidate)
    selected = []
    dimensions = sorted(by_dimension)
    while len(selected) < limit and any(by_dimension.values()):
        for dimension in dimensions:
            if by_dimension[dimension]:
                selected.append(by_dimension[dimension].pop(0))
                if len(selected) >= limit:
                    break
    return selected


def build_prompts(pilot_items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    runner_path = ROOT / "scripts" / "run_re_benchmark_v1.py"
    spec = importlib.util.spec_from_file_location("run_re_benchmark_v1", runner_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load prompt builder from {runner_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.build_prompt_rows(pilot_items)


def write_readme(registry: list[dict[str, Any]], pilot_items: list[dict[str, Any]]) -> None:
    status_counts = Counter(row["effective_status"] for row in registry)
    category_counts = Counter(item["category_id"] for item in pilot_items)
    lines = [
        "# RE_BENCHMARK_V1 runnable package",
        "",
        "Generated from `re_benchmark_v1.md` and local `data/benchmark_v1_2026-05-18/items.jsonl`.",
        "",
        "## Files",
        "",
        "- `benchmark_registry.jsonl`: curated C1-C5 benchmark registry.",
        "- `source_manifest.jsonl`: local/download/manual status for each benchmark.",
        "- `pilot_items.jsonl`: local-first smoke test items.",
        "- `pilot_prompts.jsonl`: prompt export for model calls.",
        "",
        "## Registry status",
        "",
    ]
    for status, count in sorted(status_counts.items()):
        lines.append(f"- `{status}`: {count}")
    lines.extend(["", "## Pilot item counts", ""])
    for category in CATEGORIES:
        lines.append(f"- `{category['category_id']}` {category['name']}: {category_counts[category['category_id']]}")
    lines.extend(
        [
            "",
            "## Next extraction work",
            "",
            "Some benchmarks are local-ready in `source_manifest.jsonl` but currently have",
            "`local_ready_but_no_pilot_extractor`. Those need benchmark-specific item",
            "extractors before they can contribute to `pilot_items.jsonl`.",
            "",
            "## Run",
            "",
            "```bash",
            "python scripts/build_re_benchmark_v1.py",
            "python scripts/run_re_benchmark_v1.py --export-prompts data/re_benchmark_v1/pilot_prompts.jsonl",
            "```",
            "",
        ]
    )
    README_PATH.write_text("\n".join(lines), encoding="utf-8")


def write_report(registry: list[dict[str, Any]], manifest: list[dict[str, Any]], pilot_items: list[dict[str, Any]]) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    status_counts = Counter(row["effective_status"] for row in registry)
    category_counts = Counter(item["category_id"] for item in pilot_items)
    runner_counts = Counter(item["runner_status"] for item in pilot_items)
    rows = []
    for row in manifest:
        rows.append(
            "<tr>"
            f"<td>{esc(row['category_id'])}</td>"
            f"<td>{esc(row['benchmark_name'])}</td>"
            f"<td>{esc(row['role'])}</td>"
            f"<td><span class='status'>{esc(row['effective_status'])}</span></td>"
            f"<td><span class='status'>{esc(row['extraction_status'])}</span></td>"
            f"<td>{row['pilot_item_count']}</td>"
            f"<td>{esc(row.get('local_path') or '')}</td>"
            f"<td>{esc(row.get('pilot_action') or '')}</td>"
            "</tr>"
        )
    html_text = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>RE_BENCHMARK_V1 Pilot Package</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans SC", sans-serif; margin: 0; background: #f3f6fb; color: #182033; }}
    main {{ max-width: 1180px; margin: 0 auto; padding: 32px 22px 52px; }}
    header, section {{ background: white; border: 1px solid #dbe2ef; border-radius: 8px; padding: 22px; margin-bottom: 16px; }}
    h1 {{ margin: 0 0 8px; font-size: 30px; }}
    h2 {{ margin: 0 0 12px; font-size: 22px; }}
    .grid {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; }}
    .tile {{ background: #f7f9fd; border: 1px solid #dbe2ef; border-radius: 8px; padding: 14px; }}
    .tile b {{ display: block; font-size: 24px; }}
    table {{ width: 100%; border-collapse: collapse; }}
    th, td {{ padding: 9px 10px; border-bottom: 1px solid #dbe2ef; text-align: left; vertical-align: top; }}
    th {{ background: #f7f9fd; }}
    .status {{ font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 12px; }}
    code {{ background: #eef2f8; padding: 2px 4px; border-radius: 4px; }}
  </style>
</head>
<body>
<main>
  <header>
    <h1>RE_BENCHMARK_V1 Pilot Package</h1>
    <p>本报告把 <code>re_benchmark_v1.md</code> 落成 registry、source manifest、pilot items 和 prompt export。Pilot 只使用本地可追溯样本；缺失数据保持为 manifest 状态，不伪造样本。</p>
  </header>
  <section>
    <h2>Summary</h2>
    <div class="grid">
      <div class="tile"><b>{len(registry)}</b><span>registry benchmarks</span></div>
      <div class="tile"><b>{len(pilot_items)}</b><span>pilot items</span></div>
      <div class="tile"><b>{sum(1 for r in registry if r['effective_status'] == 'local_ready')}</b><span>local-ready benchmarks</span></div>
      <div class="tile"><b>{len(status_counts)}</b><span>status types</span></div>
    </div>
  </section>
  <section>
    <h2>Pilot Items By Category</h2>
    <ul>{''.join(f"<li><code>{esc(c['category_id'])}</code> {esc(c['name'])}: {category_counts[c['category_id']]}</li>" for c in CATEGORIES)}</ul>
  </section>
  <section>
    <h2>Runner Status</h2>
    <ul>{''.join(f"<li><code>{esc(k)}</code>: {v}</li>" for k, v in sorted(runner_counts.items()))}</ul>
  </section>
  <section>
    <h2>Source Manifest</h2>
    <table>
      <thead><tr><th>C</th><th>Benchmark</th><th>Role</th><th>Status</th><th>Extraction</th><th>Pilot items</th><th>Local path</th><th>Pilot action</th></tr></thead>
      <tbody>{''.join(rows)}</tbody>
    </table>
  </section>
</main>
</body>
</html>
"""
    REPORT_PATH.write_text(html_text, encoding="utf-8")


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def main() -> None:
    if not SOURCE_MD.exists():
        raise SystemExit("re_benchmark_v1.md not found")
    if not ITEMS_IN.exists():
        raise SystemExit("data/benchmark_v1_2026-05-18/items.jsonl not found")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    acquisition = acquisition_by_id()
    registry = build_registry(acquisition)
    source_items = read_jsonl(ITEMS_IN)
    pilot_items = build_pilot_items(source_items)
    pilot_counts = Counter(item["benchmark_id"] for item in pilot_items)
    manifest = build_source_manifest(registry, acquisition, pilot_counts)
    prompts = build_prompts(pilot_items)

    write_jsonl(REGISTRY_PATH, registry)
    write_jsonl(SOURCE_MANIFEST_PATH, manifest)
    write_jsonl(PILOT_ITEMS_PATH, pilot_items)
    write_jsonl(PROMPTS_PATH, prompts)
    write_readme(registry, pilot_items)
    write_report(registry, manifest, pilot_items)

    print(f"registry={len(registry)} {REGISTRY_PATH.relative_to(ROOT)}")
    print(f"manifest={len(manifest)} {SOURCE_MANIFEST_PATH.relative_to(ROOT)}")
    print(f"pilot_items={len(pilot_items)} {PILOT_ITEMS_PATH.relative_to(ROOT)}")
    print(f"prompts={len(prompts)} {PROMPTS_PATH.relative_to(ROOT)}")
    print(f"report={REPORT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
