#!/usr/bin/env python3
"""Build the experimental mini_v2 daily screening selection.

mini_v2 deliberately has a different contract from mini_v1:

* mini_v1 approximates full-set absolute scores and rankings.
* mini_v2 is a compact, representative screening suite with a 5,000-item hard
  ceiling.  Full runs remain the calibration authority.

The builder reuses mini_v1's deterministic, stratified selection machinery but
assigns benchmark-level *item budgets* by evidence role instead of applying a
common percentage to every source.  Commodity knowledge gates and large
synthetic/expanded banks therefore receive small caps, while distinctive
education tasks retain coverage across their internal buckets.

No API calls are made.  Existing mini_v1 files and reports/eval are read-only.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_mini_selection_v1 as v1  # noqa: E402

OUT_DIR = ROOT / "data" / "mini_selection_v2"
REPORT_DIR = ROOT / "reports" / "mini_selection_v2"
VERSION = "mini_v2_experimental"
SEED = 20260901
DAILY_TARGET = 4500
DAILY_HARD_CEILING = 5000

# mini_v2 accepts wider sampling uncertainty in exchange for a genuinely small
# daily suite.  A full run is required for high-stakes absolute-score claims.
v1.SEED = SEED
v1.MIN_TOTAL_ITEMS = 50
v1.RARE_GROUP_MIN = 10


def _clone(bench: v1.Bench) -> v1.Bench:
    """Copy a mini_v1 benchmark without its large-sample floors.

    The old ASAP/SAS floors were chosen to preserve full-score statistics.  That
    is not mini_v2's contract, so v2 records the resulting uncertainty instead
    of silently exceeding the global budget.
    """

    return v1.Bench(
        bench.bid,
        bench.tier,
        bench.rate,
        bench.signal,
        bench.strata,
        list(bench.cells),
        axes=bench.axes,
        panel_subdir=bench.panel_subdir,
    )


V1_BY_ID = {b.bid: b for b in v1.BENCHES}

# Explicit counts, not percentages.  Every formally mapped benchmark is a
# member of the unified collection; execution profiles only control batching.
TARGET_COUNTS = {
    "mmlu_pro": 80,
    "agieval": 80,
    "olympiadbench": 170,
    "asap_2": 150,
    "sas_bench": 250,
    "eduguard_sata": 150,
    "edubench": 150,
    "longtutor_evidence": 100,
    "longtutor_diagnosis": 100,
    "longtutor_teaching": 100,
    "mathtutorbench_problem_solving": 100,
    "mathtutorbench_solution_correctness": 100,
    "mathtutorbench_mistake_location": 100,
    "mathtutorbench_mistake_correction": 100,
    "mathtutorbench_socratic": 100,
    "mathtutorbench_pedagogy": 100,
    "mathtutorbench_scaffolding": 100,
    "ceval": 150,
    "pedagogy_benchmark": 200,
    "mathvista": 100,
    "eduguard_adversarial": 150,
    "ifeval": 100,
    "mmtutorbench": 100,
    "k12vista": 100,
    # Newly selectable / newly promoted tasks.
    "k12bench": 200,
    "tutorbench": 200,
    # Distinctive diagnostic tasks that mini_v1 used to run in full.
    "p07_selfcheck": 100,
    "p08_calibration": 100,
    "p08_abstention": 100,
    "mooccube_prereq": 100,
    # Every formally mapped benchmark belongs to the unified collection.  The
    # execution profile controls batching only; it does not change membership.
    "mathtutorbench_pedagogy_hard": 75,
    "mathtutorbench_scaffolding_hard": 75,
    "mrbench_tutor": 60,
    "bea2025_tutor": 60,
    "mrbench_judge": 60,
    "bea2025_judge": 60,
}


def _numeric(field: str, scale: float = 1.0) -> Callable[[dict[str, Any]], float | None]:
    def signal(row: dict[str, Any]) -> float | None:
        if row.get("score_status") != "scored":
            return None
        value = row.get(field)
        if isinstance(value, (int, float)):
            return float(value) / scale
        return None

    return signal


def _st_k12bench(row: dict[str, Any]) -> tuple[str, str, str]:
    buckets = row.get("buckets") or {}
    family = str(buckets.get("task_family", "?"))
    parts = str(row.get("item_id", "")).split("::")
    subtask = parts[1] if len(parts) >= 3 and parts[1].startswith("subtask") else family
    return family, subtask, str(buckets.get("subject", "?"))


def _st_tutorbench(row: dict[str, Any]) -> tuple[str, str, str]:
    buckets = row.get("buckets") or {}
    return (
        str(buckets.get("use_case", "?")),
        str(buckets.get("modality", "?")),
        str(buckets.get("subject", "?")),
    )


def _st_source_language(row: dict[str, Any]) -> tuple[str, str]:
    buckets = row.get("buckets") or {}
    return str(buckets.get("source_benchmark", "?")), str(buckets.get("language", "?"))


def _st_abstention(row: dict[str, Any]) -> tuple[str, str]:
    buckets = row.get("buckets") or {}
    return str(buckets.get("answerable", "?")), str(buckets.get("category", "?"))


def _st_mooccube(row: dict[str, Any]) -> tuple[str, str, str]:
    buckets = row.get("buckets") or {}
    return (
        str(buckets.get("task", "?")),
        str(buckets.get("field", "?")),
        str(buckets.get("variant", "?")),
    )


def _st_mrbench_tutor(row: dict[str, Any]) -> tuple[str, str]:
    buckets = row.get("buckets") or {}
    return str(buckets.get("data", "?")), str(buckets.get("topic", "?"))


EXTRA_BENCHES = {
    "k12bench": v1.Bench(
        "k12bench",
        "synthetic_expansion",
        0.01,
        _numeric("f1"),
        _st_k12bench,
        ["instance-level Macro-F1"],
        axes=(("task_family", v1.P), ("subtask", v1.P), ("subject", v1.P)),
    ),
    "tutorbench": v1.Bench(
        "tutorbench",
        "education_core",
        0.15,
        _numeric("normalized"),
        _st_tutorbench,
        ["official ARR_w / rubric-weighted tutor quality"],
        axes=(("use_case", v1.P), ("modality", v1.P), ("subject", v1.P)),
    ),
    "p07_selfcheck": v1.Bench(
        "p07_selfcheck",
        "diagnostic",
        0.2,
        v1.sig_correct,
        _st_source_language,
        ["two-round self-check (fix/break rate)"],
        axes=(("source_benchmark", v1.P), ("language", v1.P)),
    ),
    "p08_calibration": v1.Bench(
        "p08_calibration",
        "diagnostic",
        0.2,
        v1.sig_correct,
        _st_source_language,
        ["calibration composite (CWR/AUROC)"],
        axes=(("source_benchmark", v1.P), ("language", v1.P)),
    ),
    "p08_abstention": v1.Bench(
        "p08_abstention",
        "diagnostic",
        0.2,
        v1.sig_correct,
        _st_abstention,
        ["balanced abstention score"],
        axes=(("answerable", v1.P), ("category", v1.P)),
    ),
    "mooccube_prereq": v1.Bench(
        "mooccube_prereq",
        "diagnostic",
        0.33,
        v1.sig_correct,
        _st_mooccube,
        ["chance-corrected prerequisite composite"],
        axes=(("task", v1.P), ("field", v1.P), ("variant", v1.P)),
    ),
    "mathtutorbench_pedagogy_hard": v1.Bench(
        "mathtutorbench_pedagogy_hard",
        "frontier",
        0.2,
        v1.sig_win,
        v1.st_mtb_topic,
        ["Pedagogy IF hard"],
        axes=(("topic", v1.P),),
    ),
    "mathtutorbench_scaffolding_hard": v1.Bench(
        "mathtutorbench_scaffolding_hard",
        "frontier",
        0.2,
        v1.sig_win,
        v1.st_mtb_topic,
        ["Scaffolding hard"],
        axes=(("topic", v1.P),),
    ),
    "mrbench_tutor": v1.Bench(
        "mrbench_tutor",
        "frontier",
        0.3,
        v1.sig_correct,
        _st_mrbench_tutor,
        [
            "dimension: Mistake_Identification",
            "dimension: Providing_Guidance",
            "dimension: Actionability",
            "dimension: Tutor_Tone (encouraging share)",
            "dimension: Tutor_Tone (non-offensive)",
        ],
        axes=(("data", v1.P), ("topic", v1.P)),
    ),
    "bea2025_tutor": v1.Bench(
        "bea2025_tutor",
        "frontier",
        0.2,
        v1.sig_correct,
        v1.st_none,
        [
            "dimension: Mistake_Identification",
            "dimension: Providing_Guidance",
            "dimension: Actionability",
        ],
        axes=(("all", v1.P),),
    ),
}


def build_benches() -> list[v1.Bench]:
    benches = []
    for bid in TARGET_COUNTS:
        source = EXTRA_BENCHES.get(bid) or V1_BY_ID.get(bid)
        if source is None:
            raise KeyError(f"no mini_v2 benchmark definition for {bid}")
        benches.append(_clone(source))
    return benches


BENCHES = build_benches()

# Full-preserved tasks are already compact and structurally distinctive.  Their
# counts are included in the 5,000-item daily ceiling even though they do not use
# the generic --item-list runner.
FIXED_FULL = [
    {
        "benchmark": "eduillustrate",
        "count": 230,
        "role": "education_core",
        "reason": "already curated into 11 subject-grade cells; full generation/render chain",
        "runner": "../EduIllustrate/scripts/eval_eduillustrate.sh",
    },
    {
        "benchmark": "eduequity",
        "count": 400,
        "role": "safety_fairness",
        "reason": "20 identity-axis x education-task cells are already small",
        "runner": "scripts/run_eval.sh eduequity",
    },
    {
        "benchmark": "safe_child_llm",
        "count": 200,
        "role": "safety_gate",
        "reason": "small safety gate; preserve age group and rare harm categories",
        "runner": "scripts/run_eval.sh safe_child_llm",
    },
]

EXECUTION_PROFILE_OVERRIDES = {
    "mathtutorbench_pedagogy_hard": "frontier",
    "mathtutorbench_scaffolding_hard": "frontier",
    "mrbench_tutor": "frontier",
    "bea2025_tutor": "frontier",
    "mrbench_judge": "judge",
    "bea2025_judge": "judge",
}

AUXILIARY_WORKFLOWS = {
    "judge_calibration": ["mathtutorbench_judge_calibration", "mmtutorbench_judge_calibration"],
}


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _stable_order(benchmark: str, item_id: str) -> str:
    return hashlib.sha256(f"{SEED}|coverage|{benchmark}|{item_id}".encode("utf-8")).hexdigest()


def _ensure_axis_coverage(
    bench: v1.Bench,
    rows: list[dict[str, Any]],
    selected_ids: list[str],
    target: int,
) -> tuple[list[str], dict[str, Any], dict[str, dict[str, Any]]]:
    """Cover every declared axis level without increasing the item budget.

    mini_v1 could pool rare levels because it preserved population proportions.
    mini_v2 has a representation-first contract: every declared level receives
    at least one item.  Missing levels are added greedily, then redundant items
    are removed only when doing so leaves all axis levels represented.
    """

    representative: dict[str, dict[str, Any]] = {}
    for row in rows:
        representative.setdefault(str(row["item_id"]), row)
    selected = set(selected_ids)

    def pairs(item_id: str) -> set[tuple[int, str]]:
        key = bench.strata(representative[item_id])
        return {
            (index, str(key[index]) if index < len(key) else "?")
            for index, _axis in enumerate(bench.axes)
        }

    all_pairs = set().union(*(pairs(item_id) for item_id in representative)) if representative else set()
    covered = set().union(*(pairs(item_id) for item_id in selected)) if selected else set()
    missing = all_pairs - covered
    added: list[str] = []
    while missing:
        candidates = [item_id for item_id in representative if item_id not in selected]
        best = min(
            candidates,
            key=lambda item_id: (-len(pairs(item_id) & missing), _stable_order(bench.bid, item_id)),
        )
        if not (pairs(best) & missing):
            break
        selected.add(best)
        added.append(best)
        covered |= pairs(best)
        missing = all_pairs - covered

    removed: list[str] = []
    while len(selected) > target:
        counts: dict[tuple[int, str], int] = {}
        for item_id in selected:
            for pair in pairs(item_id):
                counts[pair] = counts.get(pair, 0) + 1
        removable = [
            item_id for item_id in selected
            if all(counts[pair] > 1 for pair in pairs(item_id))
        ]
        if not removable:
            raise RuntimeError(f"{bench.bid}: cannot preserve all axis levels within target={target}")
        # Prefer removing an item whose covered levels are already most abundant.
        drop = min(
            removable,
            key=lambda item_id: (
                -sum(counts[pair] for pair in pairs(item_id)),
                _stable_order(bench.bid, item_id),
            ),
        )
        selected.remove(drop)
        removed.append(drop)

    return (
        sorted(selected),
        {
            "added_for_axis_coverage": len(added),
            "removed_to_hold_budget": len(removed),
            "uncovered_axis_levels_after_repair": len(missing),
        },
        representative,
    )


def _write_report(manifest: dict[str, Any]) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    rows = []
    for bid, value in manifest["benchmarks"].items():
        rows.append(
            f"| `{bid}` | {value['execution_profile']} | {value['role']} | {value['selected_count']} | "
            f"{value['full_count']} | {value['selected_count'] / value['full_count']:.1%} |"
        )
    fixed_rows = [
        f"| `{x['benchmark']}` | {x['role']} | {x['count']} | 全保 | {x['reason']} |"
        for x in manifest["fixed_full"]
    ]
    totals = manifest["totals"]
    md = "\n".join(
        [
            "# mini_v2 experimental selection report",
            "",
            "> 状态：离线选题实验；尚未接入默认运行和正式 P01-P20 面板。",
            "",
            "mini_v2 是代表性快速筛查集，不承诺复现全量绝对分。全量结果仍是校准依据。",
            "",
            f"- 抽样题：**{totals['selected_items']}**",
            f"- 固定全保题：**{totals['fixed_full_items']}**",
            f"- 日常总量：**{totals['daily_total_items']}**",
            f"- 目标 / 硬上限：**{DAILY_TARGET} / {DAILY_HARD_CEILING}**",
            "",
            "## 抽样 Benchmark",
            "",
            "| Benchmark | 运行 profile | 证据角色 | mini_v2 | 全量 | 比例 |",
            "|---|---|---|---:|---:|---:|",
            *rows,
            "",
            "## 固定全保",
            "",
            "| Benchmark | 角色 | 题数 | 模式 | 原因 |",
            "|---|---|---:|---|---|",
            *fixed_rows,
            "",
            "## 统一集合的运行 profiles",
            "",
            *[
                f"- **{name}**：" + "、".join(f"`{x}`" for x in bids)
                for name, bids in manifest["execution_profiles"].items()
            ],
            "",
            "Judge calibration 是评测器质检工作流，不是被测模型 Benchmark，故不计入题量。",
            "",
            "## 使用边界",
            "",
            "- mini_v2 用于快速发现主要长短板和筛选需不需要跑全量。",
            "- 不把 mini_v2 原始分与 full/mini_v1 无标注混排。",
            "- QWK、Macro-F1、校准与分组安全指标会有更宽置信区间。",
            "- 高风险发布、安全失败和小分差排名必须回到对应 Benchmark 全量。",
            "",
        ]
    )
    (REPORT_DIR / "selection_report.md").write_text(md, encoding="utf-8")

    table_rows = "".join(
        "<tr>"
        f"<td>{bid}</td><td>{value['execution_profile']}</td><td>{value['role']}</td><td>{value['selected_count']}</td>"
        f"<td>{value['full_count']}</td><td>{value['selected_count'] / value['full_count']:.1%}</td>"
        "</tr>"
        for bid, value in manifest["benchmarks"].items()
    )
    fixed_html = "".join(
        f"<tr><td>{x['benchmark']}</td><td>{x['role']}</td><td>{x['count']}</td><td>{x['reason']}</td></tr>"
        for x in manifest["fixed_full"]
    )
    html = f"""<!doctype html><html lang=\"zh-CN\"><head><meta charset=\"utf-8\">
<title>mini_v2 experimental selection</title><style>
body{{font-family:-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif;max-width:1080px;margin:32px auto;padding:0 20px;line-height:1.55;color:#202124}}
h1,h2{{color:#17324d}}.cards{{display:flex;gap:12px;flex-wrap:wrap}}.card{{background:#eef5fb;border-radius:8px;padding:12px 18px}}
table{{border-collapse:collapse;width:100%;font-size:14px}}th,td{{border:1px solid #d8dee4;padding:7px;text-align:left}}th{{background:#f6f8fa}}
.warn{{background:#fff7e6;border-left:4px solid #e69b00;padding:10px 14px}}
</style></head><body><h1>mini_v2 experimental selection</h1>
<p class=\"warn\">离线选题实验，尚未接入默认运行与正式能力面板。mini_v2 是代表性筛查集，不承诺复现全量绝对分。</p>
<div class=\"cards\"><div class=\"card\">抽样题<br><b>{totals['selected_items']}</b></div>
<div class=\"card\">固定全保<br><b>{totals['fixed_full_items']}</b></div>
<div class=\"card\">日常总量<br><b>{totals['daily_total_items']}</b> / {DAILY_HARD_CEILING}</div></div>
<h2>抽样 Benchmark</h2><table><tr><th>Benchmark</th><th>运行 profile</th><th>证据角色</th><th>mini_v2</th><th>全量</th><th>比例</th></tr>{table_rows}</table>
<h2>固定全保</h2><table><tr><th>Benchmark</th><th>角色</th><th>题数</th><th>原因</th></tr>{fixed_html}</table>
<h2>使用边界</h2><ul><li>快速筛查与能力覆盖，不替代 full。</li><li>高风险、安全失败、小分差排名必须回到全量。</li><li>core、frontier、judge 都属于同一精选集；profile 只控制分批执行。</li></ul>
</body></html>"""
    (REPORT_DIR / "selection_report.html").write_text(html, encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest: dict[str, Any] = {
        "version": VERSION,
        "seed": SEED,
        "generated_by": "scripts/build_mini_selection_v2.py",
        "contract": "representative daily screening; full set remains calibration authority",
        "budget": {"target": DAILY_TARGET, "hard_ceiling": DAILY_HARD_CEILING},
        "benchmarks": {},
        "fixed_full": FIXED_FULL,
        "execution_profiles": {"core": [], "frontier": [], "judge": []},
        "auxiliary_workflows": AUXILIARY_WORKFLOWS,
    }

    selected_total = 0
    for bench in BENCHES:
        faces = v1.discover_faces(bench)
        if not faces:
            print(f"[skip] {bench.bid}: no full scored panel face")
            continue
        full_rows = v1.read_scored(faces[0]["dir"] / "scored.jsonl")
        unique_item_ids = len({str(row["item_id"]) for row in full_rows})
        target = min(TARGET_COUNTS[bench.bid], unique_item_ids)
        # select_benchmark allocates against unique item ids.  Most benchmarks
        # have one row per id; K12Bench currently has repeated native ids, so
        # using the raw line count would silently undershoot the requested cap.
        result = v1.select_benchmark(bench, rate_override=target / unique_item_ids)
        if result is None:
            continue
        ids, coverage_repair, representative = _ensure_axis_coverage(
            bench,
            full_rows,
            result.pop("selected_ids"),
            target,
        )
        selected_set = set(ids)
        result["selected_count"] = len(ids)
        result["composition"] = v1.composition_report(
            bench, representative, sorted(representative), selected_set
        )
        result["max_abs_shift_pp_proportional_axes"] = round(
            max(
                [
                    value["max_abs_shift_pp"]
                    for value in result["composition"].values()
                    if value["kind"] == "proportional"
                ],
                default=0.0,
            ),
            3,
        )
        result["cell_selected_counts"] = v1.per_cell_counts(bench, representative, selected_set)
        text = "\n".join(ids) + "\n"
        path = OUT_DIR / f"{bench.bid}_items_v2.txt"
        path.write_text(text, encoding="utf-8")
        result.update(
            {
                "role": bench.tier,
                "execution_profile": EXECUTION_PROFILE_OVERRIDES.get(bench.bid, "core"),
                "target_count": TARGET_COUNTS[bench.bid],
                "unique_item_ids": unique_item_ids,
                "duplicate_item_id_rows": len(full_rows) - unique_item_ids,
                "coverage_repair": coverage_repair,
                "item_list": path.relative_to(ROOT).as_posix(),
                "item_list_sha256": _sha(text),
            }
        )
        manifest["benchmarks"][bench.bid] = result
        manifest["execution_profiles"][result["execution_profile"]].append(bench.bid)
        selected_total += result["selected_count"]
        print(f"{bench.bid:36s} {result['selected_count']:4d}/{result['full_count']:5d}")

    manifest["execution_profiles"]["core"].extend(x["benchmark"] for x in FIXED_FULL)
    fixed_total = sum(x["count"] for x in FIXED_FULL)
    daily_total = selected_total + fixed_total
    manifest["totals"] = {
        "selected_benchmarks": len(manifest["benchmarks"]),
        "fixed_full_benchmarks": len(FIXED_FULL),
        "collection_benchmarks": len(manifest["benchmarks"]) + len(FIXED_FULL),
        "selected_items": selected_total,
        "fixed_full_items": fixed_total,
        "daily_total_items": daily_total,
        "within_target": daily_total <= DAILY_TARGET,
        "within_hard_ceiling": daily_total <= DAILY_HARD_CEILING,
    }
    if daily_total > DAILY_HARD_CEILING:
        raise SystemExit(f"mini_v2 budget {daily_total} exceeds hard ceiling {DAILY_HARD_CEILING}")

    manifest_path = OUT_DIR / "selection_manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    _write_report(manifest)
    print(f"TOTAL selected={selected_total} fixed={fixed_total} daily={daily_total}")
    print(f"manifest -> {manifest_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
