#!/usr/bin/env python3
"""Offline audit for frontier_selection_v1.  Makes no API calls."""

from __future__ import annotations

import hashlib
import html
import json
import statistics
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_frontier_selection_v1 as frontier  # noqa: E402
import validate_mini_selection_v2 as mini_validator  # noqa: E402

MANIFEST_PATH = ROOT / "data" / "frontier_selection_v1" / "selection_manifest.json"
OUT_DIR = ROOT / "reports" / "frontier_selection_v1"


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def build_summary() -> dict[str, Any]:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    outcomes = Counter()
    results = []
    all_available_classes_represented = True
    hashes_match = True
    counts_match = True
    caps_respected = True
    axes_covered = True
    disagreement_uplifts = []
    error_uplifts = []
    low_confidence_panels = []
    for bid, meta in manifest["benchmarks"].items():
        text = (ROOT / meta["item_list"]).read_text(encoding="utf-8")
        ids = [line for line in text.splitlines() if line]
        hashes_match &= _sha(text) == meta["item_list_sha256"]
        counts_match &= len(ids) == meta["selected_count"] == len(set(ids))
        caps_respected &= meta["selected_count"] <= meta["target_count"]
        axes_covered &= meta["coverage_repair"]["uncovered_axis_buckets"] == 0
        selected_counts = meta["selected_outcomes"]["counts"]
        full_counts = meta["full_outcomes"]["counts"]
        outcomes.update(selected_counts)
        for outcome in ("unanimous_failure", "mixed_outcome"):
            if full_counts[outcome] > 0 and selected_counts[outcome] == 0:
                all_available_classes_represented = False
        full_disagreement = meta["full_outcomes"]["mean_pairwise_disagreement"]
        selected_disagreement = meta["selected_outcomes"]["mean_pairwise_disagreement"]
        full_error = meta["full_outcomes"]["mean_error_rate"]
        selected_error = meta["selected_outcomes"]["mean_error_rate"]
        disagreement_uplifts.append(selected_disagreement - full_disagreement)
        error_uplifts.append(selected_error - full_error)
        results.append(
            {
                "benchmark": bid,
                "selected": meta["selected_count"],
                "cap": meta["target_count"],
                "panel_models": len(meta["frontier_panel"]),
                "outcomes": selected_counts,
                "easy_share": meta["selected_outcomes"]["shares"]["unanimous_pass"],
                "mean_error_rate": selected_error,
                "disagreement_uplift": round(selected_disagreement - full_disagreement, 4),
                "error_uplift": round(selected_error - full_error, 4),
                "mini_v2_overlap_share": meta["mini_v2_overlap_share"],
                "axis_buckets_covered": meta["coverage_repair"]["uncovered_axis_buckets"] == 0,
            }
        )
        if len(meta["frontier_panel"]) < 3:
            low_confidence_panels.append(bid)

    selected_total = sum(outcomes.values())
    outcome_shares = {
        key: round(outcomes[key] / selected_total, 4) if selected_total else 0.0
        for key in frontier.TARGET_SHARES
    }
    atomic = mini_validator._atomic_coverage(manifest)
    mapped_ok = not atomic["missing_mapped_benchmarks"]
    facet_ok = atomic["nonempty_facets_covered"] == atomic["nonempty_facets_total"]
    cells_ok = atomic["measurement_cells_covered"] == atomic["measurement_cells_total"]
    checks = {
        "hard_ceiling": manifest["totals"]["within_hard_ceiling"],
        "all_item_counts_match": counts_match,
        "all_item_list_hashes_match": hashes_match,
        "all_benchmark_caps_respected": caps_respected,
        "all_pooled_axis_buckets_covered": axes_covered,
        "all_available_failure_and_mixed_classes_represented": all_available_classes_represented,
        "sampled_unanimous_pass_share_at_most_target": (
            outcome_shares["unanimous_pass"] <= frontier.TARGET_SHARES["unanimous_pass"]
        ),
        "all_mapped_benchmarks_in_collection": mapped_ok,
        "all_nonempty_atomic_facets_covered": facet_ok,
        "all_measurement_cell_sources_present": cells_ok,
        "all_frontier_panels_meet_minimum_size": all(
            row["panel_models"] >= frontier.MIN_PANEL_SIZE for row in results
        ),
    }
    return {
        "version": manifest["version"],
        "generated_by": "scripts/validate_frontier_selection_v1.py",
        "totals": manifest["totals"],
        "selected_outcome_counts": dict(outcomes),
        "selected_outcome_shares": outcome_shares,
        "checks": checks,
        "atomic_coverage": {
            key: atomic[key]
            for key in (
                "mapped_benchmarks_total",
                "mapped_benchmarks_covered",
                "missing_mapped_benchmarks",
                "nonempty_facets_total",
                "nonempty_facets_covered",
                "measurement_cells_total",
                "measurement_cells_covered",
            )
        },
        "portfolio_diagnostics": {
            "benchmarks_with_disagreement_uplift": sum(value >= 0 for value in disagreement_uplifts),
            "benchmarks_total": len(disagreement_uplifts),
            "mean_disagreement_uplift": round(statistics.fmean(disagreement_uplifts), 4),
            "benchmarks_with_error_rate_uplift": sum(value >= 0 for value in error_uplifts),
            "mean_error_rate_uplift": round(statistics.fmean(error_uplifts), 4),
            "low_confidence_panels_below_3_models": low_confidence_panels,
        },
        "benchmarks": results,
        "limitations": [
            "the eligible frontier cohort is fixed, but the available complete model faces can differ by benchmark",
            "unanimous failure is a future-facing challenge signal, not current-model discrimination",
            "fixed full EduIllustrate, EduEquity, and SafeChild items are coverage anchors and are not hardness-filtered",
            "LLM-judged item difficulty remains conditional on the current judge",
            "selection validity should be rechecked on held-out or newly released frontier models",
            "SAS-Bench currently has only two complete faces in the fixed frontier cohort, so its item labels are low-confidence",
        ],
    }


def write_reports(summary: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "validation_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    checks = summary["checks"]
    rows = [
        f"| `{row['benchmark']}` | {row['selected']}/{row['cap']} | "
        f"{row['outcomes']['unanimous_failure']} | {row['outcomes']['mixed_outcome']} | "
        f"{row['outcomes']['unanimous_pass']} | {row['disagreement_uplift']} | "
        f"{row['error_uplift']} | {row['mini_v2_overlap_share']:.1%} |"
        for row in summary["benchmarks"]
    ]
    diag = summary["portfolio_diagnostics"]
    atomic = summary["atomic_coverage"]
    md = "\n".join(
        [
            "# Frontier selection v1 validation",
            "",
            "> 零 API 离线审计。通过题比例只针对 36 个难度抽样 Benchmark；3 个固定全保项另列。",
            "",
            f"- 总量：**{summary['totals']['total_items']}** / {frontier.HARD_CEILING}",
            f"- 抽样构成：全员失败 **{summary['selected_outcome_shares']['unanimous_failure']:.1%}**；有对有错 **{summary['selected_outcome_shares']['mixed_outcome']:.1%}**；全员通过 **{summary['selected_outcome_shares']['unanimous_pass']:.1%}**",
            f"- 正式映射 Benchmark：**{atomic['mapped_benchmarks_covered']}/{atomic['mapped_benchmarks_total']}**",
            f"- 非空原子能力 facet：**{atomic['nonempty_facets_covered']}/{atomic['nonempty_facets_total']}**",
            f"- measurement cell 来源：**{atomic['measurement_cells_covered']}/{atomic['measurement_cells_total']}**",
            f"- 区分度相对全量提升的 Benchmark：**{diag['benchmarks_with_disagreement_uplift']}/{diag['benchmarks_total']}**",
            f"- 少于 3 个前沿模型面的低置信 Benchmark：**{', '.join(diag['low_confidence_panels_below_3_models']) or '无'}**",
            "",
            "## 硬检查",
            "",
            *[f"- {key}：**{'通过' if value else '失败'}**" for key, value in checks.items()],
            "",
            "## 逐 Benchmark",
            "",
            "| Benchmark | 实际/上限 | 全员失败 | 有对有错 | 全员通过 | 区分度增量 | 错误率增量 | 与 mini_v2 重合 |",
            "|---|---:|---:|---:|---:|---:|---:|---:|",
            *rows,
            "",
            "## 限制",
            "",
            *[f"- {item}" for item in summary["limitations"]],
            "",
        ]
    )
    (OUT_DIR / "validation_report.md").write_text(md, encoding="utf-8")

    body = "".join(
        "<tr>"
        f"<td>{html.escape(row['benchmark'])}</td><td>{row['selected']}/{row['cap']}</td>"
        f"<td>{row['outcomes']['unanimous_failure']}</td><td>{row['outcomes']['mixed_outcome']}</td>"
        f"<td>{row['outcomes']['unanimous_pass']}</td><td>{row['disagreement_uplift']}</td>"
        f"<td>{row['error_uplift']}</td><td>{row['mini_v2_overlap_share']:.1%}</td></tr>"
        for row in summary["benchmarks"]
    )
    report_html = f"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>Frontier selection v1 validation</title>
<style>body{{font-family:-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif;max-width:1100px;margin:32px auto;padding:0 20px;color:#202124}}table{{border-collapse:collapse;width:100%;font-size:13px}}th,td{{border:1px solid #d8dee4;padding:7px;text-align:left}}th{{background:#f6f8fa}}.cards{{display:flex;gap:12px;flex-wrap:wrap}}.card{{background:#eef5fb;border-radius:8px;padding:12px 18px}}.warn{{background:#fff7e6;border-left:4px solid #e69b00;padding:10px 14px}}</style></head>
<body><h1>Frontier selection v1 validation</h1><p class="warn">前沿挑战集，不是总体代表性分布。</p><div class="cards"><div class="card">总量<br><b>{summary['totals']['total_items']}</b></div><div class="card">全员失败<br><b>{summary['selected_outcome_shares']['unanimous_failure']:.1%}</b></div><div class="card">有对有错<br><b>{summary['selected_outcome_shares']['mixed_outcome']:.1%}</b></div><div class="card">全员通过<br><b>{summary['selected_outcome_shares']['unanimous_pass']:.1%}</b></div></div>
<h2>逐 Benchmark</h2><table><tr><th>Benchmark</th><th>实际/上限</th><th>全员失败</th><th>有对有错</th><th>全员通过</th><th>区分度增量</th><th>错误率增量</th><th>mini 重合</th></tr>{body}</table></body></html>"""
    (OUT_DIR / "validation_report.html").write_text(report_html, encoding="utf-8")


def main() -> None:
    summary = build_summary()
    write_reports(summary)
    print(json.dumps({
        "totals": summary["totals"],
        "selected_outcome_shares": summary["selected_outcome_shares"],
        "checks": summary["checks"],
        "portfolio_diagnostics": summary["portfolio_diagnostics"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
