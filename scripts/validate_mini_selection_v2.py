#!/usr/bin/env python3
"""Offline feasibility audit for the experimental mini_v2 selection.

The audit asks whether the 5,000-item screening budget is mechanically viable:

* every requested item budget is met;
* every declared internal axis retains all levels;
* existing full-run model rankings are broadly preserved;
* score drift is exposed, not treated as a release gate (mini_v2 is not an
  absolute-score proxy).

No API calls are made and no reports/eval artifact is modified.
"""

from __future__ import annotations

import html
import json
import statistics
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_mini_selection_v1 as v1  # noqa: E402
import build_mini_selection_v2 as v2  # noqa: E402
import validate_mini_selection as legacy  # noqa: E402

MANIFEST_PATH = ROOT / "data" / "mini_selection_v2" / "selection_manifest.json"
MAPPING_PATH = ROOT / "data" / "mapping_measurement_model_v6.json"
OUT_DIR = ROOT / "reports" / "mini_selection_v2"
RANK_TAU_GUIDE = 0.80


def _mean_signal(bench: v1.Bench, rows: list[dict[str, Any]]) -> float | None:
    values = [bench.signal(row) for row in rows]
    values = [float(value) for value in values if value is not None]
    return 10.0 * statistics.fmean(values) if values else None


def _scores(bench: v1.Bench, rows: list[dict[str, Any]]) -> dict[str, float]:
    # Reuse the published adapter + mapping path whenever possible.  K12Bench is
    # not yet in the P01-P20 mapping, so its native per-instance Macro-F1 falls
    # back to the generic signal mean.
    try:
        mapped = legacy.recompute_from_rows(bench.bid, list(rows))
    except Exception:
        mapped = {}
    if mapped:
        return mapped
    value = _mean_signal(bench, rows)
    return {bench.cells[0]: value} if value is not None else {}


def _coverage(bench: v1.Bench, rows: list[dict[str, Any]], selected: set[str]) -> list[dict[str, Any]]:
    # Native item ids may repeat (currently K12Bench); coverage is defined over
    # selectable ids because --item-list cannot distinguish duplicate rows.
    representative: dict[str, dict[str, Any]] = {}
    for row in rows:
        representative.setdefault(str(row["item_id"]), row)
    out = []
    for index, (axis, kind) in enumerate(bench.axes):
        full_levels: dict[str, int] = {}
        mini_levels: dict[str, int] = {}
        for item_id, row in representative.items():
            key = bench.strata(row)
            level = str(key[index]) if index < len(key) else "?"
            full_levels[level] = full_levels.get(level, 0) + 1
            if item_id in selected:
                mini_levels[level] = mini_levels.get(level, 0) + 1
        missing = sorted(level for level in full_levels if mini_levels.get(level, 0) == 0)
        out.append(
            {
                "axis": axis,
                "kind": kind,
                "full_levels": len(full_levels),
                "selected_levels": len(mini_levels),
                "missing_levels": missing,
                "minimum_selected_per_level": min(mini_levels.values()) if mini_levels else 0,
            }
        )
    return out


def _fixed_checks() -> list[dict[str, Any]]:
    checks = []
    edu_path = ROOT.parent / "EduIllustrate" / "data" / "benchmark" / "benchmark.json"
    edu_count = len(json.loads(edu_path.read_text(encoding="utf-8"))) if edu_path.exists() else None
    checks.append({"benchmark": "eduillustrate", "expected": 230, "observed": edu_count})

    equity_path = ROOT / "data" / "eduequity" / "eduequity_pairs_zh.jsonl"
    equity_count = sum(1 for line in equity_path.open(encoding="utf-8") if line.strip()) if equity_path.exists() else None
    checks.append({"benchmark": "eduequity", "expected": 400, "observed": equity_count})

    safe_root = ROOT / "reports" / "eval" / "safe_child_llm" / "judge-minimax3" / "minimax3" / "scored.jsonl"
    safe_ids = (
        {str(row["item_id"]) for row in v1.read_scored(safe_root)} if safe_root.exists() else set()
    )
    checks.append({"benchmark": "safe_child_llm", "expected": 200, "observed": len(safe_ids) or None})
    for check in checks:
        check["pass"] = check["expected"] == check["observed"]
    return checks


def _atomic_coverage(manifest: dict[str, Any]) -> dict[str, Any]:
    """Audit collection membership against every non-empty v6 measurement cell."""

    mapping = json.loads(MAPPING_PATH.read_text(encoding="utf-8"))
    collection = set(manifest["benchmarks"])
    collection.update(item["benchmark"] for item in manifest["fixed_full"])
    mapped_benchmarks: set[str] = set()
    abilities = []
    measurement_cells_total = 0
    measurement_cells_covered = 0
    nonempty_facets_total = 0
    nonempty_facets_covered = 0
    for ability in mapping["abilities"]:
        facets = []
        for facet in ability.get("facets", []):
            cells = facet.get("cells", [])
            if not cells:
                continue
            nonempty_facets_total += 1
            covered_cells = []
            missing_cells = []
            for cell in cells:
                benchmark = cell["benchmark_id"]
                mapped_benchmarks.add(benchmark)
                measurement_cells_total += 1
                record = {"benchmark": benchmark, "subdimension": cell["subdimension"]}
                if benchmark in collection:
                    measurement_cells_covered += 1
                    covered_cells.append(record)
                else:
                    missing_cells.append(record)
            facet_covered = bool(covered_cells) and not missing_cells
            if facet_covered:
                nonempty_facets_covered += 1
            facets.append(
                {
                    "facet": facet["facet_name"],
                    "covered": facet_covered,
                    "covered_cells": covered_cells,
                    "missing_cells": missing_cells,
                }
            )
        abilities.append(
            {
                "p_code": ability["p_code"],
                "p_name": ability["p_name"],
                "nonempty_facets": len(facets),
                "all_nonempty_facets_covered": all(facet["covered"] for facet in facets),
                "facets": facets,
            }
        )
    return {
        "mapping": MAPPING_PATH.relative_to(ROOT).as_posix(),
        "mapped_benchmarks_total": len(mapped_benchmarks),
        "mapped_benchmarks_covered": len(mapped_benchmarks & collection),
        "missing_mapped_benchmarks": sorted(mapped_benchmarks - collection),
        "measurement_cells_total": measurement_cells_total,
        "measurement_cells_covered": measurement_cells_covered,
        "nonempty_facets_total": nonempty_facets_total,
        "nonempty_facets_covered": nonempty_facets_covered,
        "abilities": abilities,
    }


def build_summary() -> dict[str, Any]:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    bench_by_id = {bench.bid: bench for bench in v2.BENCHES}
    results = []
    for bid, meta in manifest["benchmarks"].items():
        bench = bench_by_id[bid]
        selected = {
            line.strip()
            for line in (ROOT / meta["item_list"]).read_text(encoding="utf-8").splitlines()
            if line.strip()
        }
        faces = v1.discover_faces(bench)
        per_model: dict[str, dict[str, dict[str, float]]] = {}
        coverage_rows = None
        for face in faces:
            rows = v1.read_scored(face["dir"] / "scored.jsonl")
            if coverage_rows is None:
                coverage_rows = rows
            subset = [row for row in rows if str(row["item_id"]) in selected]
            full_scores = _scores(bench, rows)
            mini_scores = _scores(bench, subset)
            common = sorted(set(full_scores) & set(mini_scores))
            per_model[face["model_key"]] = {
                cell: {"full": full_scores[cell], "mini": mini_scores[cell]}
                for cell in common
            }

        cells = sorted({cell for model in per_model.values() for cell in model})
        cell_results = []
        for cell in cells:
            pairs = [
                (model, values[cell]["full"], values[cell]["mini"])
                for model, values in per_model.items()
                if cell in values
            ]
            full = [row[1] for row in pairs]
            mini = [row[2] for row in pairs]
            tau = legacy.kendall_tau(full, mini)
            deltas = [abs(a - b) for a, b in zip(full, mini)]
            cell_results.append(
                {
                    "cell": cell,
                    "n_models": len(pairs),
                    "max_abs_delta": round(max(deltas), 4) if deltas else None,
                    "mean_abs_delta": round(statistics.fmean(deltas), 4) if deltas else None,
                    "tau": round(tau, 4) if tau is not None else None,
                    "rank_guide_pass": tau is None or tau >= RANK_TAU_GUIDE,
                }
            )
        coverage = _coverage(bench, coverage_rows or [], selected)
        results.append(
            {
                "benchmark": bid,
                "target": meta["target_count"],
                "selected": len(selected),
                "target_met": len(selected) == meta["target_count"],
                "full_rows": meta["full_count"],
                "unique_item_ids": meta["unique_item_ids"],
                "duplicate_item_id_rows": meta["duplicate_item_id_rows"],
                "coverage": coverage,
                "coverage_complete": all(not axis["missing_levels"] for axis in coverage),
                "cells": cell_results,
            }
        )

    fixed_checks = _fixed_checks()
    atomic_coverage = _atomic_coverage(manifest)
    all_cells = [cell for result in results for cell in result["cells"]]
    return {
        "version": manifest["version"],
        "generated_by": "scripts/validate_mini_selection_v2.py",
        "contract": manifest["contract"],
        "totals": manifest["totals"],
        "rank_tau_guide": RANK_TAU_GUIDE,
        "checks": {
            "hard_ceiling": manifest["totals"]["within_hard_ceiling"],
            "all_targets_met": all(result["target_met"] for result in results),
            "all_declared_axis_levels_covered": all(result["coverage_complete"] for result in results),
            "fixed_full_counts_match": all(check["pass"] for check in fixed_checks),
            "all_mapped_benchmarks_in_collection": not atomic_coverage["missing_mapped_benchmarks"],
            "all_nonempty_atomic_facets_covered": (
                atomic_coverage["nonempty_facets_covered"]
                == atomic_coverage["nonempty_facets_total"]
            ),
            "all_measurement_cells_covered": (
                atomic_coverage["measurement_cells_covered"]
                == atomic_coverage["measurement_cells_total"]
            ),
            "rank_cells_total": len([cell for cell in all_cells if cell["tau"] is not None]),
            "rank_cells_below_guide": len(
                [cell for cell in all_cells if cell["tau"] is not None and not cell["rank_guide_pass"]]
            ),
        },
        "fixed_full_checks": fixed_checks,
        "atomic_coverage": atomic_coverage,
        "benchmarks": results,
        "limitations": [
            "mini_v2 is a representative screen, not a full-score proxy",
            "absolute score drift is diagnostic and is expected to exceed mini_v1 thresholds",
            "pedagogy_benchmark under 600 items requires a mini_v2-aware aggregation floor",
            "K12Bench has repeated native item ids; item-list selection operates on unique ids",
            "LLM-judged rankings remain conditional on the selected judge",
        ],
    }


def write_reports(summary: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "validation_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    checks = summary["checks"]
    rows = []
    for result in summary["benchmarks"]:
        worst_delta = max(
            [cell["max_abs_delta"] for cell in result["cells"] if cell["max_abs_delta"] is not None],
            default=None,
        )
        worst_tau = min([cell["tau"] for cell in result["cells"] if cell["tau"] is not None], default=None)
        rows.append(
            f"| `{result['benchmark']}` | {result['selected']}/{result['target']} | "
            f"{'是' if result['coverage_complete'] else '否'} | "
            f"{worst_delta if worst_delta is not None else '—'} | {worst_tau if worst_tau is not None else '—'} | "
            f"{result['duplicate_item_id_rows']} |"
        )
    md = "\n".join(
        [
            "# mini_v2 experimental validation",
            "",
            "> 零 API 离线可行性审计。mini_v2 是代表性筛查集，不是 full-score proxy。",
            "",
            f"- 日常总量：**{summary['totals']['daily_total_items']}** / 5000",
            f"- 所有目标题数达到：**{'是' if checks['all_targets_met'] else '否'}**",
            f"- 所有声明的内部轴层级有覆盖：**{'是' if checks['all_declared_axis_levels_covered'] else '否'}**",
            f"- 固定全保计数一致：**{'是' if checks['fixed_full_counts_match'] else '否'}**",
            f"- 正式映射 Benchmark 全部属于统一集合：**{'是' if checks['all_mapped_benchmarks_in_collection'] else '否'}**",
            f"- 非空原子能力 facet 覆盖：**{summary['atomic_coverage']['nonempty_facets_covered']}/{summary['atomic_coverage']['nonempty_facets_total']}**",
            f"- measurement cell 来源 Benchmark 在集合中：**{summary['atomic_coverage']['measurement_cells_covered']}/{summary['atomic_coverage']['measurement_cells_total']}**",
            f"- 可计算排名的格：**{checks['rank_cells_total']}**；τ<{RANK_TAU_GUIDE}：**{checks['rank_cells_below_guide']}**",
            "",
            "| Benchmark | 实际/目标 | 内部层级全覆盖 | 最大绝对漂移 | 最低 τ | 重复题号行 |",
            "|---|---:|---|---:|---:|---:|",
            *rows,
            "",
            "## 使用边界",
            "",
            *[f"- {item}" for item in summary["limitations"]],
            "",
        ]
    )
    (OUT_DIR / "validation_report.md").write_text(md, encoding="utf-8")

    body_rows = "".join(
        "<tr>"
        f"<td>{html.escape(result['benchmark'])}</td><td>{result['selected']}/{result['target']}</td>"
        f"<td>{'是' if result['coverage_complete'] else '否'}</td>"
        f"<td>{max([cell['max_abs_delta'] for cell in result['cells'] if cell['max_abs_delta'] is not None], default='—')}</td>"
        f"<td>{min([cell['tau'] for cell in result['cells'] if cell['tau'] is not None], default='—')}</td>"
        f"<td>{result['duplicate_item_id_rows']}</td></tr>"
        for result in summary["benchmarks"]
    )
    report_html = f"""<!doctype html><html lang=\"zh-CN\"><head><meta charset=\"utf-8\"><title>mini_v2 validation</title>
<style>body{{font-family:-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif;max-width:1080px;margin:32px auto;padding:0 20px;color:#202124}}
table{{border-collapse:collapse;width:100%;font-size:14px}}th,td{{border:1px solid #d8dee4;padding:7px;text-align:left}}th{{background:#f6f8fa}}
.cards{{display:flex;gap:12px;flex-wrap:wrap}}.card{{background:#eef5fb;border-radius:8px;padding:12px 18px}}.warn{{background:#fff7e6;padding:12px;border-left:4px solid #e69b00}}</style></head>
<body><h1>mini_v2 experimental validation</h1><p class=\"warn\">代表性筛查集，不承诺复现 full 绝对分。</p>
<div class=\"cards\"><div class=\"card\">日常总量<br><b>{summary['totals']['daily_total_items']}</b> / 5000</div>
<div class=\"card\">内部层级全覆盖<br><b>{'是' if checks['all_declared_axis_levels_covered'] else '否'}</b></div>
<div class=\"card\">原子 facet 覆盖<br><b>{summary['atomic_coverage']['nonempty_facets_covered']}/{summary['atomic_coverage']['nonempty_facets_total']}</b></div>
<div class=\"card\">τ&lt;{RANK_TAU_GUIDE}<br><b>{checks['rank_cells_below_guide']}/{checks['rank_cells_total']}</b></div></div>
<h2>逐 Benchmark</h2><table><tr><th>Benchmark</th><th>实际/目标</th><th>层级全覆盖</th><th>最大漂移</th><th>最低 τ</th><th>重复题号行</th></tr>{body_rows}</table>
<h2>限制</h2><ul>{''.join(f'<li>{html.escape(item)}</li>' for item in summary['limitations'])}</ul></body></html>"""
    (OUT_DIR / "validation_report.html").write_text(report_html, encoding="utf-8")


def main() -> None:
    summary = build_summary()
    write_reports(summary)
    print(json.dumps({"totals": summary["totals"], "checks": summary["checks"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
