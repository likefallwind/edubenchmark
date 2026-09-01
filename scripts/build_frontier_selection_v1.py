#!/usr/bin/env python3
"""Build a <=5,000 item frontier challenge selection from existing full runs.

The frontier set is deliberately not population representative.  Within every
benchmark it retains three outcome classes from a frozen top-model panel:

* unanimous_failure: every panel model is below the task pass threshold;
* mixed_outcome: some panel models pass and some fail (ranking signal);
* unanimous_pass: every panel model passes (small coverage/anchor allowance).

The target mix is 35% / 60% / 5%, subject to available items and mandatory
coverage of every declared internal axis level.  No API calls are made.
"""

from __future__ import annotations

import hashlib
import json
import math
import statistics
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_mini_selection_v1 as v1  # noqa: E402
import build_mini_selection_v2 as v2  # noqa: E402

OUT_DIR = ROOT / "data" / "frontier_selection_v1"
REPORT_DIR = ROOT / "reports" / "frontier_selection_v1"
VERSION = "frontier_selection_v1_experimental"
SEED = 20260901
PANEL_SIZE = 5
MIN_PANEL_SIZE = 2
PASS_THRESHOLD = 0.5
FRONTIER_MODEL_KEYS = {
    "minimax-m3",
    "glm-5.2",
    "deepseek-v4-pro",
    "deepseek-v4-flash",
    "doubao-seed-2-0-pro",
    "qwen-qwen3-8-27b",
}
TARGET_SHARES = {
    "unanimous_failure": 0.35,
    "mixed_outcome": 0.60,
    "unanimous_pass": 0.05,
}
HARD_CEILING = 5000
RARE_LEVEL_MIN = 10


def _stable(item_id: str, benchmark: str, purpose: str) -> str:
    return hashlib.sha256(
        f"{SEED}|{purpose}|{benchmark}|{item_id}".encode("utf-8")
    ).hexdigest()


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _frontier_panel(
    bench: v1.Bench,
) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]], dict[str, dict[str, float]]]:
    """Return top full-run faces, representative rows, and per-face signals."""

    faces = v1.discover_faces(bench)
    representative: dict[str, dict[str, Any]] = {}
    face_signals: dict[str, dict[str, float]] = {}
    ranked = []
    for face in faces:
        signals: dict[str, float] = {}
        for row in v1.read_scored(face["dir"] / "scored.jsonl"):
            item_id = str(row["item_id"])
            representative.setdefault(item_id, row)
            value = bench.signal(row) if bench.signal else None
            if value is not None and math.isfinite(float(value)):
                signals[item_id] = min(1.0, max(0.0, float(value)))
        if not signals:
            continue
        mean = statistics.fmean(signals.values())
        face_signals[face["model_key"]] = signals
        ranked.append({**face, "mean_signal": mean, "scored_items": len(signals)})
    ranked.sort(key=lambda face: (-face["mean_signal"], face["model_key"]))
    eligible = [face for face in ranked if face["model_key"] in FRONTIER_MODEL_KEYS]
    if len(eligible) < MIN_PANEL_SIZE:
        raise RuntimeError(
            f"{bench.bid}: only {len(eligible)} complete faces from the fixed frontier cohort"
        )
    panel = eligible[:PANEL_SIZE]
    panel_signals = {face["model_key"]: face_signals[face["model_key"]] for face in panel}
    return panel, representative, panel_signals


def _item_statistics(
    representative: dict[str, dict[str, Any]],
    panel_signals: dict[str, dict[str, float]],
) -> dict[str, dict[str, Any]]:
    required_faces = max(1, min(3, len(panel_signals)))
    stats: dict[str, dict[str, Any]] = {}
    for item_id in representative:
        values = [signals[item_id] for signals in panel_signals.values() if item_id in signals]
        if len(values) < required_faces:
            continue
        passes = sum(value >= PASS_THRESHOLD for value in values)
        if passes == 0:
            outcome = "unanimous_failure"
        elif passes == len(values):
            outcome = "unanimous_pass"
        else:
            outcome = "mixed_outcome"
        pairwise_disagreement = (
            2.0 * passes * (len(values) - passes) / (len(values) * (len(values) - 1))
            if len(values) >= 2
            else 0.0
        )
        variance = statistics.pvariance(values) if len(values) >= 2 else 0.0
        mean = statistics.fmean(values)
        if outcome == "mixed_outcome":
            priority = 2.0 * pairwise_disagreement + variance + 0.2 * (1.0 - mean)
        elif outcome == "unanimous_failure":
            # Preserve both deep-unsolved and near-breakthrough items.  Variance
            # and max score favor items showing progress; error keeps deep
            # failures from disappearing when all signals are exactly zero.
            priority = 1.0 + variance + 0.4 * max(values) + 0.2 * (1.0 - mean)
        else:
            priority = variance + (1.0 - mean)
        stats[item_id] = {
            "outcome": outcome,
            "n_faces": len(values),
            "mean_signal": mean,
            "error_rate": 1.0 - mean,
            "variance": variance,
            "pairwise_disagreement": pairwise_disagreement,
            "priority": priority,
        }
    return stats


def _desired_counts(target: int) -> dict[str, int]:
    raw = {key: target * share for key, share in TARGET_SHARES.items()}
    counts = {key: int(math.floor(value)) for key, value in raw.items()}
    left = target - sum(counts.values())
    order = sorted(raw, key=lambda key: (-(raw[key] - counts[key]), key))
    for key in order[:left]:
        counts[key] += 1
    return counts


def _allocate_available(
    desired: dict[str, int], available: dict[str, int], target: int
) -> dict[str, int]:
    allocation = {key: min(desired[key], available.get(key, 0)) for key in desired}
    # A benchmark budget is a ceiling, not a fill requirement.  If the hard and
    # mixed pools run out, do not pad with easy items merely to hit the cap.
    preference = ["mixed_outcome", "unanimous_failure"]
    while sum(allocation.values()) < target:
        candidates = [key for key in preference if allocation[key] < available.get(key, 0)]
        if not candidates:
            break
        key = candidates[0]
        allocation[key] += 1
    return allocation


def _pick_diverse(
    bench: v1.Bench,
    item_ids: list[str],
    count: int,
    representative: dict[str, dict[str, Any]],
    stats: dict[str, dict[str, Any]],
) -> list[str]:
    if count >= len(item_ids):
        return sorted(item_ids)
    groups: dict[tuple, list[str]] = {}
    for item_id in item_ids:
        groups.setdefault(bench.strata(representative[item_id]), []).append(item_id)
    quotas = v1.largest_remainder({key: len(ids) for key, ids in groups.items()}, count)
    selected = []
    for key, ids in groups.items():
        ids.sort(key=lambda item_id: (-stats[item_id]["priority"], _stable(item_id, bench.bid, "rank")))
        selected.extend(ids[: quotas[key]])
    return sorted(selected)


def _ensure_axis_coverage(
    bench: v1.Bench,
    representative: dict[str, dict[str, Any]],
    selected_ids: list[str],
    target_cap: int,
    stats: dict[str, dict[str, Any]],
) -> tuple[list[str], dict[str, Any]]:
    """Cover common axis levels and one pooled rare-level bucket per axis.

    Frontier selection must not add dozens of unanimously passed items solely
    because a source exposes a long tail of tiny labels (for example ~95 math
    tutor topics).  Levels with fewer than ``RARE_LEVEL_MIN`` items are pooled
    into one explicit ``__rare__`` coverage bucket.
    """

    frequencies: list[dict[str, int]] = []
    for index, _axis in enumerate(bench.axes):
        counts: dict[str, int] = {}
        for row in representative.values():
            key = bench.strata(row)
            level = str(key[index]) if index < len(key) else "?"
            counts[level] = counts.get(level, 0) + 1
        frequencies.append(counts)

    def pairs(item_id: str) -> set[tuple[int, str]]:
        key = bench.strata(representative[item_id])
        out = set()
        for index, _axis in enumerate(bench.axes):
            level = str(key[index]) if index < len(key) else "?"
            token = level if frequencies[index].get(level, 0) >= RARE_LEVEL_MIN else "__rare__"
            out.add((index, token))
        return out

    selected = set(selected_ids)
    all_pairs = set().union(*(pairs(item_id) for item_id in representative)) if representative else set()
    covered = set().union(*(pairs(item_id) for item_id in selected)) if selected else set()
    added = []
    while all_pairs - covered:
        missing = all_pairs - covered
        candidates = [item_id for item_id in representative if item_id not in selected]
        best = min(
            candidates,
            key=lambda item_id: (
                -len(pairs(item_id) & missing),
                -stats[item_id]["priority"],
                _stable(item_id, bench.bid, "coverage"),
            ),
        )
        selected.add(best)
        added.append(best)
        covered |= pairs(best)

    removed = []
    while len(selected) > target_cap:
        counts: dict[tuple[int, str], int] = {}
        for item_id in selected:
            for pair in pairs(item_id):
                counts[pair] = counts.get(pair, 0) + 1
        removable = [
            item_id for item_id in selected if all(counts[pair] > 1 for pair in pairs(item_id))
        ]
        if not removable:
            raise RuntimeError(f"{bench.bid}: axis coverage cannot fit cap={target_cap}")
        drop = min(
            removable,
            key=lambda item_id: (stats[item_id]["priority"], _stable(item_id, bench.bid, "drop")),
        )
        selected.remove(drop)
        removed.append(drop)

    rare_counts = {
        axis: sum(1 for count in frequencies[index].values() if count < RARE_LEVEL_MIN)
        for index, (axis, _kind) in enumerate(bench.axes)
    }
    return sorted(selected), {
        "rare_level_min": RARE_LEVEL_MIN,
        "rare_levels_pooled_by_axis": rare_counts,
        "added_for_axis_coverage": len(added),
        "removed_to_hold_cap": len(removed),
        "uncovered_axis_buckets": len(all_pairs - covered),
    }


def _summarize_outcomes(item_ids: list[str], stats: dict[str, dict[str, Any]]) -> dict[str, Any]:
    counts = {key: 0 for key in TARGET_SHARES}
    for item_id in item_ids:
        counts[stats[item_id]["outcome"]] += 1
    total = len(item_ids)
    return {
        "counts": counts,
        "shares": {key: round(count / total, 4) if total else 0.0 for key, count in counts.items()},
        "mean_error_rate": round(
            statistics.fmean(stats[item_id]["error_rate"] for item_id in item_ids), 4
        ) if item_ids else None,
        "mean_pairwise_disagreement": round(
            statistics.fmean(stats[item_id]["pairwise_disagreement"] for item_id in item_ids), 4
        ) if item_ids else None,
    }


def _write_report(manifest: dict[str, Any]) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    rows = []
    for bid, meta in manifest["benchmarks"].items():
        outcomes = meta["selected_outcomes"]["counts"]
        rows.append(
            f"| `{bid}` | {meta['selected_count']} | {outcomes['unanimous_failure']} | "
            f"{outcomes['mixed_outcome']} | {outcomes['unanimous_pass']} | "
            f"{meta['selected_outcomes']['mean_error_rate']} | "
            f"{meta['selected_outcomes']['mean_pairwise_disagreement']} |"
        )
    totals = manifest["totals"]
    md = "\n".join(
        [
            "# Frontier selection v1 experimental report",
            "",
            "> 状态：零 API 离线选题实验；用于前沿模型挑战，不代表题库总体分布。",
            "",
            f"- 抽样题：**{totals['selected_items']}**",
            f"- 固定全保覆盖题：**{totals['fixed_full_items']}**",
            f"- 总量：**{totals['total_items']}** / {HARD_CEILING}",
            f"- Benchmark：**{totals['collection_benchmarks']}**",
            f"- 目标构成：全员失败 {TARGET_SHARES['unanimous_failure']:.0%} / 有对有错 {TARGET_SHARES['mixed_outcome']:.0%} / 全员通过最多约 {TARGET_SHARES['unanimous_pass']:.0%}",
            f"- 实际抽样构成：全员失败 {totals['selected_outcome_shares']['unanimous_failure']:.1%} / 有对有错 {totals['selected_outcome_shares']['mixed_outcome']:.1%} / 全员通过 {totals['selected_outcome_shares']['unanimous_pass']:.1%}",
            "",
            "## 逐 Benchmark",
            "",
            "| Benchmark | 题数 | 全员失败 | 有对有错 | 全员通过 | 平均错误率 | 平均两两分歧 |",
            "|---|---:|---:|---:|---:|---:|---:|",
            *rows,
            "",
            "## 固定全保覆盖项",
            "",
            *[
                f"- `{item['benchmark']}`：{item['count']} 题；保持完整安全/公平/生成结构，未按错题率裁切。"
                for item in manifest["fixed_full"]
            ],
            "",
            "## 解释边界",
            "",
            "- 全员失败题是未来能力边界，保留但不承担当前模型主排序。",
            "- 有对有错题承担主要区分度；全员通过题只作少量覆盖锚点。",
            "- 模型面板来自固定的仓库前沿 cohort；每个 Benchmark 在其中取全量表现最好的至多 5 个完整结果面。",
            "- LLM-judged 题的难度和区分度依赖当前裁判；发布前应做跨 Judge 稳定性检查。",
            "- 本集合分数不可与 full 或 mini_v2 原始分无标注混排。",
            "",
        ]
    )
    (REPORT_DIR / "selection_report.md").write_text(md, encoding="utf-8")

    body = "".join(
        "<tr>"
        f"<td>{bid}</td><td>{meta['selected_count']}</td>"
        f"<td>{meta['selected_outcomes']['counts']['unanimous_failure']}</td>"
        f"<td>{meta['selected_outcomes']['counts']['mixed_outcome']}</td>"
        f"<td>{meta['selected_outcomes']['counts']['unanimous_pass']}</td>"
        f"<td>{meta['selected_outcomes']['mean_error_rate']}</td>"
        f"<td>{meta['selected_outcomes']['mean_pairwise_disagreement']}</td></tr>"
        for bid, meta in manifest["benchmarks"].items()
    )
    html = f"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>Frontier selection v1</title>
<style>body{{font-family:-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif;max-width:1100px;margin:32px auto;padding:0 20px;color:#202124}}table{{border-collapse:collapse;width:100%;font-size:13px}}th,td{{border:1px solid #d8dee4;padding:7px;text-align:left}}th{{background:#f6f8fa}}.cards{{display:flex;gap:12px;flex-wrap:wrap}}.card{{background:#eef5fb;border-radius:8px;padding:12px 18px}}.warn{{background:#fff7e6;border-left:4px solid #e69b00;padding:10px 14px}}</style></head>
<body><h1>Frontier selection v1</h1><p class="warn">前沿挑战集，不代表总体题目分布；全员失败题用于追踪未来突破。</p>
<div class="cards"><div class="card">总题数<br><b>{totals['total_items']}</b> / {HARD_CEILING}</div><div class="card">Benchmark<br><b>{totals['collection_benchmarks']}</b></div><div class="card">抽样题<br><b>{totals['selected_items']}</b></div></div>
<h2>逐 Benchmark</h2><table><tr><th>Benchmark</th><th>题数</th><th>全员失败</th><th>有对有错</th><th>全员通过</th><th>平均错误率</th><th>两两分歧</th></tr>{body}</table>
<h2>边界</h2><ul><li>有对有错题用于当前模型排序。</li><li>全员失败题用于未来能力追踪。</li><li>固定全保项未按错题率裁切。</li><li>LLM Judge 结果需要跨裁判复核。</li></ul></body></html>"""
    (REPORT_DIR / "selection_report.html").write_text(html, encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest: dict[str, Any] = {
        "version": VERSION,
        "seed": SEED,
        "generated_by": "scripts/build_frontier_selection_v1.py",
        "contract": "frontier challenge: retain unanimous failures and high-disagreement errors",
        "panel_rule": {
            "eligible_model_keys": sorted(FRONTIER_MODEL_KEYS),
            "selection": f"top {PANEL_SIZE} available complete faces from the fixed frontier cohort by full-run mean signal",
            "minimum_panel_size": MIN_PANEL_SIZE,
            "pass_threshold": PASS_THRESHOLD,
        },
        "target_outcome_shares": TARGET_SHARES,
        "benchmarks": {},
        "fixed_full": v2.FIXED_FULL,
    }
    selected_total = 0
    for bench in v2.BENCHES:
        panel, representative, panel_signals = _frontier_panel(bench)
        if not panel:
            raise RuntimeError(f"{bench.bid}: no full scored model face")
        stats = _item_statistics(representative, panel_signals)
        if not stats:
            raise RuntimeError(f"{bench.bid}: no items shared by the frontier panel")
        target = min(v2.TARGET_COUNTS[bench.bid], len(stats))
        pools = {
            outcome: sorted(item_id for item_id, value in stats.items() if value["outcome"] == outcome)
            for outcome in TARGET_SHARES
        }
        desired = _desired_counts(target)
        allocation = _allocate_available(
            desired, {outcome: len(ids) for outcome, ids in pools.items()}, target
        )
        selected = []
        for outcome, count in allocation.items():
            selected.extend(_pick_diverse(bench, pools[outcome], count, representative, stats))
        selected = sorted(set(selected))
        representative = {item_id: row for item_id, row in representative.items() if item_id in stats}
        selected, coverage_repair = _ensure_axis_coverage(
            bench, representative, selected, target, stats
        )
        text = "\n".join(selected) + "\n"
        item_path = OUT_DIR / f"{bench.bid}_frontier_items_v1.txt"
        item_path.write_text(text, encoding="utf-8")
        mini_path = ROOT / "data" / "mini_selection_v2" / f"{bench.bid}_items_v2.txt"
        mini_ids = set(mini_path.read_text(encoding="utf-8").splitlines()) if mini_path.exists() else set()
        panel_rows = [
            {
                "model": face["model_key"],
                "full_mean_signal": round(face["mean_signal"], 4),
                "scored_items": face["scored_items"],
            }
            for face in panel
        ]
        meta = {
            "target_count": v2.TARGET_COUNTS[bench.bid],
            "selected_count": len(selected),
            "full_unique_items": len(stats),
            "frontier_panel": panel_rows,
            "desired_outcome_counts": desired,
            "allocated_outcome_counts_before_coverage_repair": allocation,
            "full_outcomes": _summarize_outcomes(sorted(stats), stats),
            "selected_outcomes": _summarize_outcomes(selected, stats),
            "coverage_repair": coverage_repair,
            "axes": [{"axis": axis, "kind": kind} for axis, kind in bench.axes],
            "composition": v1.composition_report(bench, representative, sorted(representative), set(selected)),
            "mini_v2_overlap_count": len(set(selected) & mini_ids),
            "mini_v2_overlap_share": round(len(set(selected) & mini_ids) / len(selected), 4),
            "item_list": item_path.relative_to(ROOT).as_posix(),
            "item_list_sha256": _sha(text),
        }
        manifest["benchmarks"][bench.bid] = meta
        selected_total += len(selected)
        outcomes = meta["selected_outcomes"]["counts"]
        print(
            f"{bench.bid:36s} {len(selected):4d}  fail={outcomes['unanimous_failure']:4d} "
            f"mixed={outcomes['mixed_outcome']:4d} pass={outcomes['unanimous_pass']:3d}"
        )

    selected_outcomes = {key: 0 for key in TARGET_SHARES}
    for meta in manifest["benchmarks"].values():
        for key, count in meta["selected_outcomes"]["counts"].items():
            selected_outcomes[key] += count
    selected_outcome_shares = {
        key: round(count / selected_total, 4) if selected_total else 0.0
        for key, count in selected_outcomes.items()
    }
    fixed_total = sum(item["count"] for item in v2.FIXED_FULL)
    total = selected_total + fixed_total
    manifest["totals"] = {
        "selected_benchmarks": len(manifest["benchmarks"]),
        "fixed_full_benchmarks": len(v2.FIXED_FULL),
        "collection_benchmarks": len(manifest["benchmarks"]) + len(v2.FIXED_FULL),
        "selected_items": selected_total,
        "fixed_full_items": fixed_total,
        "total_items": total,
        "within_hard_ceiling": total <= HARD_CEILING,
        "selected_outcome_counts": selected_outcomes,
        "selected_outcome_shares": selected_outcome_shares,
    }
    if total > HARD_CEILING:
        raise SystemExit(f"frontier budget {total} exceeds hard ceiling {HARD_CEILING}")
    path = OUT_DIR / "selection_manifest.json"
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _write_report(manifest)
    print(f"TOTAL selected={selected_total} fixed={fixed_total} total={total}")
    print(f"manifest -> {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
