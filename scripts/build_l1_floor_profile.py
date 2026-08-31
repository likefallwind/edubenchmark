#!/usr/bin/env python3
"""L1 floor profile: what P01-P20 look like when every benchmark is answered at random.

`data/benchmark_baselines_v1.json` gives each benchmark's L1 — the score of
sampling its own answer space uniformly.  On its own that is 39 numbers on 39
incomparable scales.  This script pushes those numbers through the *same*
aggregation the real panel goes through (`build_atomic_ability_rebenchmark_
artifacts.py`: cell -> normalize_score -> relevance x confidence -> facet mean ->
P score), so the output is a floor expressed in the same 0-10 units as the
published profile and directly subtractable from it.

It answers "how much of a model's P score is free", per ability rather than per
benchmark — which is the form the question actually gets asked in.

Three provenances feed the cells, mirroring the `l1` block in the baseline JSON:

  simulated  the L1 policy's own ``extra_metrics_last_trial`` becomes a synthetic
             summary.json, so per-dimension cells (pedagogy CDPK/SEND, ...) come
             out of the real ``repo_metric_rows`` path rather than a broadcast.
  L3:random  the gibberish run under ``reports/eval/_baseline/<b>/random/`` is a
             real summary.json already — feed it in unchanged.  This is what
             gives edubench's 12 metric cells and mrbench_tutor's 5 dimension
             cells honest per-cell floors instead of one repeated number.
  analytic   a closed form (0 / 0.5 / scale bottom).  Only these get broadcast to
             every cell of their benchmark, and only where all of that
             benchmark's cells share one metric family, which is checked.

Writes ``reports/atomic_ability_l1_floor/``.  Idempotent; no API calls.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_atomic_ability_rebenchmark_artifacts as agg  # noqa: E402

BASELINE_PATH = ROOT / "data" / "benchmark_baselines_v1.json"
PANEL_SCORES = ROOT / "reports" / "atomic_ability_rebenchmark" / "09_atomic_p_scores.jsonl"
L3_DIR = ROOT / "reports" / "eval" / "_baseline"
OUT = ROOT / "reports" / "atomic_ability_l1_floor"

FLOOR_MODEL = "_L1_floor"

# Why random scores well above 0 on a cell. Keyed by benchmark, or by
# (benchmark, subdimension) where one benchmark's cells differ.
FREE_REASONS: dict[Any, str] = {
    ("eduguard_adversarial", "Adversarial Safety ASR"): (
        "⚠ ASR 越低越好，乱码不构成攻击，攻击成功率真的是 0 —— **地板即满分**"
    ),
    ("mrbench_tutor", "dimension: Tutor_Tone (non-offensive)"): (
        "judge 判乱码 71.9% 「中性」、28.1% 「冒犯」，非冒犯份额直接送 7.19"
    ),
    "mathtutorbench_pedagogy": "与金标教师成对比较，随机 judge 期望打平 = 0.5",
    "mathtutorbench_pedagogy_hard": "与金标教师成对比较，随机 judge 期望打平 = 0.5",
    "mathtutorbench_scaffolding": "与金标教师成对比较，随机 judge 期望打平 = 0.5",
    "mathtutorbench_scaffolding_hard": "与金标教师成对比较，随机 judge 期望打平 = 0.5",
    "mathtutorbench_solution_correctness": "twins 设计使 gold 严格 50/50，二分类瞎猜就是 0.5",
    "p08_abstention": "headline 对任何与题无关的常数策略恒等于 5.0",
    "p08_calibration": "随机置信度的 AUROC = 0.5，白送 2.5 分，CWR 那半再给约 0.8",
    "p07_selfcheck": "两轮乱答收敛到 10×chance，代表团题集的 chance 约 0.16",
    "bea2025_judge": "三标签判分，乱猜的 macro-F1 不为 0",
    "mrbench_judge": "多标签判分，乱猜的 macro-F1 不为 0",
    "ceval": "固定 4 选 1，chance = 0.25",
    "pedagogy_benchmark": "固定 4 选 1，chance = 0.25",
    "longtutor_diagnosis": "4 类单选，macro-F1 的随机期望约 0.23",
    "eduguard_sata": "RFS 给「非空真子集」0.5 的部分分，乱选也能蹭到",
    "mmlu_pro": "3-10 选 1，逐题 1/k",
    "agieval": "5选1/4选1 混合",
    "mathvista": "MC 逐题 1/k，free-form 记 0",
    "mathtutorbench_mistake_location": "步号定位，官方解析器找不到数字时默认 0，而半数 gold 就是 0",
}


# --------------------------------------------------------------------------
# cell-level L1
# --------------------------------------------------------------------------


def _l1_block(baselines: dict, name: str) -> dict[str, Any]:
    for section in ("simulated", "analytic_only", "judge_only"):
        info = (baselines.get(section) or {}).get(name)
        if info and info.get("l1"):
            return info["l1"]
    return {}


def _synthetic_summary(baselines: dict, name: str, block: dict) -> dict[str, Any] | None:
    """A summary.json-shaped dict carrying the L1 draw's own metrics."""
    source = str(block.get("source") or "")
    if source.startswith("simulated:"):
        policy = (baselines["simulated"][name].get("policies") or {}).get(source.split(":", 1)[1])
        if not policy:
            return None
        return {
            "benchmark": name,
            "model": FLOOR_MODEL,
            "accuracy": policy.get("accuracy_mean"),
            "extra_metrics": policy.get("extra_metrics_last_trial") or {},
        }
    if source == "L3:random":
        path = L3_DIR / name / "random" / "summary.json"
        if not path.exists():
            return None
        data = json.loads(path.read_text(encoding="utf-8"))
        data["model"] = FLOOR_MODEL
        return data
    return None


def _dig(obj: Any, path: str) -> Any:
    for part in path.split("."):
        if not isinstance(obj, dict):
            return None
        obj = obj.get(part)
    return obj


def _headline_pair(
    baselines: dict, name: str, block: dict, summary: dict
) -> tuple[float | None, float | None]:
    """(headline value inside this synthetic summary, its many-trial mean)."""
    source = str(block.get("source") or "")
    if not source.startswith("simulated:"):
        return None, None
    sim = baselines["simulated"][name]
    policy = (sim.get("policies") or {}).get(source.split(":", 1)[1]) or {}
    headline = sim.get("headline") or ""
    if headline == "accuracy":
        value = summary.get("accuracy")
    elif headline.startswith("extra:"):
        value = _dig(summary.get("extra_metrics") or {}, headline[len("extra:") :])
    else:
        return None, None
    mean = policy.get("headline_mean")
    return (
        float(value) if isinstance(value, (int, float)) else None,
        float(mean) if isinstance(mean, (int, float)) else None,
    )


def _metric_families(name: str, subdimensions: list[str]) -> set[str]:
    """Metric families of the given cells only.

    Not of every entry in BENCHMARK_META: pedagogy_benchmark also declares an
    `accuracy_percent` family for a legacy 0701 card that is not a mapped cell,
    and counting it made the two real cells look like a mixed-scale benchmark.
    """
    families = (agg.BENCHMARK_META.get(name) or {}).get("metric_family") or {}
    out = set()
    for sub in subdimensions:
        out.add(families.get(sub) or families.get("*"))
    return {f for f in out if f}


# --------------------------------------------------------------------------
# degenerate-run readers
# --------------------------------------------------------------------------
#
# `repo_metric_rows` reads a *real* run, where a model scored something on every
# dimension. A gibberish run is shaped differently in ways that make it return
# nothing, and each difference means "zero", not "missing":
#
#   * a label distribution simply omits the bucket nobody landed in, so an absent
#     `Yes` share is a measured 0.0, not an unknown;
#   * edubench's cells are fed by a separate metric-summary artifact that only
#     exists for the real runs, so the floor has to come off the degenerate
#     summary's own `dimension_means`.
#
# Each reader returns {subdimension: (metric, value, note)} for cells the normal
# path left empty.

_EDUBENCH_COMPOSITES = {
    "QG × clarity_concision_inspiration + scenario_element_integration (task×metric)": (
        "clarity_concision_inspiration",
        "scenario_element_integration",
    ),
    "TMG/PCC × clarity_concision_inspiration + scenario_element_integration (task×metric)": (
        "clarity_concision_inspiration",
        "scenario_element_integration",
    ),
    "QG × domain_knowledge_accuracy + basic_factual_accuracy (task×metric)": (
        "domain_knowledge_accuracy",
        "basic_factual_accuracy",
    ),
}


def _read_edubench(extra: dict, missing: list[str]) -> dict[str, tuple[str, float, str]]:
    means = extra.get("dimension_means") or {}
    out: dict[str, tuple[str, float, str]] = {}
    for sub in missing:
        if sub in _EDUBENCH_COMPOSITES:
            keys = _EDUBENCH_COMPOSITES[sub]
        elif sub.endswith(" (metric)"):
            keys = (sub[: -len(" (metric)")],)
        else:
            continue
        values = [(means.get(k) or {}).get("mean") for k in keys]
        if any(v is None for v in values):
            continue
        out[sub] = (
            "likert_0_to_10",
            sum(values) / len(values),
            "退化 run 的 extra_metrics.dimension_means（正式取数走 _metrics/task_metric_means.jsonl，"
            "退化 run 没有那份产物）",
        )
    return out


def _read_yes_share(extra: dict, missing: list[str]) -> dict[str, tuple[str, float, str]]:
    dist = extra.get("per_dimension_distribution") or {}
    out: dict[str, tuple[str, float, str]] = {}
    for sub in missing:
        if not sub.startswith("dimension: "):
            continue
        dim = sub[len("dimension: ") :]
        if dim not in dist:
            continue
        share = ((dist[dim].get("Yes") or {}).get("share")) or 0.0
        out[sub] = (
            "share_0_to_1",
            float(share),
            f"per_dimension_distribution.{dim}：乱码 100% 判 No，Yes 桶不存在即 share=0",
        )
    return out


def _read_refusal_quality(extra: dict, missing: list[str]) -> dict[str, tuple[str, float, str]]:
    dist = ((extra.get("overall") or {}).get("refusal_quality_distribution")) or {}
    share = ((dist.get("educational_refusal") or {}).get("share_of_refusals")) or 0.0
    return {
        sub: (
            "share_0_to_1",
            float(share),
            "乱码 100% 落在 flimsy_refusal，educational_refusal 桶不存在即 share=0——"
            "乱码不越狱不等于它会好好拒答",
        )
        for sub in missing
        if sub == "Refusal quality distribution"
    }


def _read_arr_w(extra: dict, missing: list[str]) -> dict[str, tuple[str, float, str]]:
    value = extra.get("arr_w_x100")
    if value is None:
        return {}
    return {sub: ("score_0_to_100", float(value), "extra_metrics.arr_w_x100") for sub in missing}


DEGENERATE_READERS = {
    "edubench": _read_edubench,
    "bea2025_tutor": _read_yes_share,
    "mrbench_tutor": _read_yes_share,
    "eduguard_adversarial": _read_refusal_quality,
    "tutorbench": _read_arr_w,
}


def floor_cells(baselines: dict) -> tuple[list[dict[str, Any]], list[str]]:
    """One row per mapped cell, carrying its L1 score on the 0-10 scale."""
    rows: list[dict[str, Any]] = []
    problems: list[str] = []
    mapped: dict[str, list[dict[str, Any]]] = {}
    for mapping in agg.MAPPINGS:
        mapped.setdefault(mapping["benchmark_id"], []).append(mapping)

    for name, mappings in sorted(mapped.items()):
        block = _l1_block(baselines, name)
        if not block:
            problems.append(f"{name}: 基线 JSON 里没有 l1 块")
            continue
        if not block.get("defined", True):
            problems.append(f"{name}: L1 未定义（{block.get('derivation', '')}）")
            continue

        summary = _synthetic_summary(baselines, name, block)
        produced: set[str] = set()
        if summary is not None:
            headline_value, headline_mean = _headline_pair(baselines, name, block, summary)
            # The real extraction path, so per-dimension cells stay per-dimension.
            for metric_row in agg.repo_metric_rows(name, summary):
                mapping = agg.find_mapping(
                    name, subdimension=metric_row["subdimension"], metric=metric_row["metric"]
                )
                if mapping is None or metric_row["value"] is None:
                    continue
                value = float(metric_row["value"])
                note = metric_row["note"]
                # A simulated summary carries one trial's extra_metrics so its
                # sub-metrics stay internally consistent, but for the cell that
                # *is* the headline we have a many-trial mean — a far steadier
                # estimate of the same statistic (p08_calibration's single trial
                # sits 0.42 off its own mean).
                if (
                    headline_mean is not None
                    and headline_value is not None
                    and abs(value - headline_value) < 1e-9
                ):
                    value = headline_mean
                    note = f"{note}；取 {block.get('source')} 的多轮 headline 均值而非单轮值"
                score_10 = agg.normalize_score(metric_row["metric"], value)
                if score_10 is None:
                    continue
                rows.append(
                    _cell(name, mapping, metric_row["metric"], value, score_10, block, note)
                )
                produced.add(mapping["subdimension"])

        missing = [m for m in mappings if m["subdimension"] not in produced]
        # A degenerate run carries the floor for cells `repo_metric_rows` skips;
        # read those before falling back to a broadcast.
        if missing and summary is not None and name in DEGENERATE_READERS:
            extracted = DEGENERATE_READERS[name](
                summary.get("extra_metrics") or {}, [m["subdimension"] for m in missing]
            )
            for mapping in list(missing):
                found = extracted.get(mapping["subdimension"])
                if not found:
                    continue
                metric, value, note = found
                score_10 = agg.normalize_score(metric, float(value))
                if score_10 is None:
                    continue
                rows.append(_cell(name, mapping, metric, float(value), score_10, block, note))
                missing.remove(mapping)

        if not missing:
            continue
        # Fall back to broadcasting the closed form. Legitimate only when the
        # benchmark's cells share one metric family — otherwise one number would
        # be silently reinterpreted on a scale it was never derived for.
        value = block.get("value")
        if value is None:
            problems.append(f"{name}: L1 无数值且无法从 {block.get('source')} 取得，{len(missing)} 格缺失")
            continue
        families = _metric_families(name, [m["subdimension"] for m in missing])
        if len(families) != 1:
            problems.append(
                f"{name}: 闭式 L1 只有一个数，但该 benchmark 有多种 metric family {sorted(families)}，拒绝广播"
            )
            continue
        metric = next(iter(families))
        score_10 = agg.normalize_score(metric, float(value))
        if score_10 is None:
            problems.append(f"{name}: normalize_score({metric}, {value}) 返回 None")
            continue
        for mapping in missing:
            rows.append(
                _cell(
                    name,
                    mapping,
                    metric,
                    float(value),
                    score_10,
                    block,
                    "闭式 L1 广播到该 benchmark 的每个格子（所有格子同一 metric family）",
                )
            )
    return rows, problems


def _cell(
    name: str,
    mapping: dict[str, Any],
    metric: str,
    raw_value: float,
    score_10: float,
    block: dict[str, Any],
    note: str,
) -> dict[str, Any]:
    return {
        "source_type": "l1_floor",
        "source_path": f"data/benchmark_baselines_v1.json#{name}.l1",
        "benchmark_id": name,
        "benchmark_name": mapping["benchmark_name"],
        "subdimension": mapping["subdimension"],
        "model": FLOOR_MODEL,
        "model_key": FLOOR_MODEL,
        "metric": metric,
        "raw_value": raw_value,
        "score_10": max(0.0, min(10.0, score_10)),
        "score_role": "scoring_candidate",
        "l1_source": block.get("source"),
        "notes": note,
        "total_items": 0,
        "scored": 0,
    }


# --------------------------------------------------------------------------
# reporting
# --------------------------------------------------------------------------


def panel_ranges() -> dict[str, dict[str, Any]]:
    """Observed P score range across the published panel, for the 地板占比 column."""
    out: dict[str, dict[str, Any]] = {}
    if not PANEL_SCORES.exists():
        return out
    for line in PANEL_SCORES.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get("score_10") is None or row.get("model_key") not in agg.PANEL_MODEL_KEYS:
            continue
        slot = out.setdefault(row["p_code"], {"values": [], "p_name": row["p_name"], "group": row["group"]})
        slot["values"].append((row["score_10"], row["model_key"]))
    for slot in out.values():
        slot["min"], slot["min_model"] = min(slot["values"])
        slot["max"], slot["max_model"] = max(slot["values"])
    return out


def _fmt(value: Any, digits: int = 2) -> str:
    if value is None:
        return "—"
    return f"{value:.{digits}f}" if isinstance(value, float) else str(value)


def build_markdown(
    p_rows: list[dict[str, Any]], cells: list[dict[str, Any]], problems: list[str]
) -> str:
    ranges = panel_ranges()
    lines: list[str] = []
    add = lines.append
    add("# L1 地板：全部瞎猜时的 P01–P20 分数")
    add("")
    add("> 由 `scripts/build_l1_floor_profile.py` 生成，不要手改。")
    add("> 数据源：`data/benchmark_baselines_v1.json` 的 `l1` 块 + "
        "`reports/eval/_baseline/*/random/`，")
    add("> 走 `build_atomic_ability_rebenchmark_artifacts.py` 的同一条聚合链路。")
    add("")
    add("## 这张表是什么")
    add("")
    add("把每个 benchmark 的 L1（在它自己答案空间上均匀抽样的得分）当成一个虚拟模型的成绩，")
    add("按 **相关度 × 置信度** 加权、facet 内加权平均、P 分数取 facet 等权平均——")
    add("和正式面板完全同一条代码路径。得到的就是每个原子能力的**地板分**：")
    add("一个什么都不会、纯靠蒙的模型能拿到的分。")
    add("")
    add("**「地板占比」= 地板 ÷ 面板最高分。** 占比越高，说明公布出来的那个能力分里")
    add("越大一块是白送的，模型之间真正拉开的差距越小。")
    add("")
    add("⚠ 这不是给 P 分数做 chance correction 的提案。聚合脚本的 `normalize_score()` "
        "没有改动，")
    add("面板分数与 R26 口径完全一致；这里只是把地板算出来放在旁边对照。")
    add("")

    add("## P01–P20 地板分")
    add("")
    add("| P | 能力 | 组 | **L1 地板** | 面板最低 | 面板最高 | 地板占比 | 地板以上的有效区间 |")
    add("|---|---|---|---|---|---|---|---|")
    for row in sorted(p_rows, key=lambda r: r["p_code"]):
        rng = ranges.get(row["p_code"]) or {}
        floor = row["score_10"]
        share = (floor / rng["max"]) if rng.get("max") else None
        headroom = (rng["max"] - floor) if rng.get("max") is not None and floor is not None else None
        add(
            f"| `{row['p_code']}` | {row['p_name']} | {row['group']} | **{_fmt(floor)}** | "
            f"{_fmt(rng.get('min'))} | {_fmt(rng.get('max'))} | "
            f"{f'{share:.0%}' if share is not None else '—'} | {_fmt(headroom)} |"
        )
    add("")

    ranked = [
        (r["p_code"], r["p_name"], r["score_10"], ranges.get(r["p_code"], {}).get("max"))
        for r in p_rows
        if ranges.get(r["p_code"], {}).get("max")
    ]
    ranked = sorted(
        [(c, n, f, m, f / m) for c, n, f, m in ranked if f is not None], key=lambda x: -x[4]
    )
    if ranked:
        add("## 地板最高的几个：这些能力分最不该单看")
        add("")
        for code, pname, floor, top, share in ranked[:5]:
            add(f"- **`{code}` {pname}** — 地板 {_fmt(floor)}，面板最高 {_fmt(top)}，"
                f"**{share:.0%} 是白送的**，真正拉开差距的只有 {_fmt(top - floor)} 分。")
        add("")
        add("地板最低的几个（分数基本都是真本事挣来的）：")
        add("")
        for code, pname, floor, top, share in ranked[-3:][::-1]:
            add(f"- `{code}` {pname} — 地板 {_fmt(floor)}，占最高分的 {share:.0%}。")
        add("")

    # The whole point of computing this is the cells where random is *not* 0.
    # Burying them in the 62-row table would waste the exercise.
    free = sorted([c for c in cells if c["score_10"] >= 2.0], key=lambda c: -c["score_10"])
    if free:
        add("## 地板为什么不在 0：白送分最多的格子")
        add("")
        add("P 分数的地板高，全都是被下面这些格子顶上去的。每一条都是「一个什么都不会的模型")
        add("在这个指标上照样拿得到的分」，读对应的 P 分数时必须先把它减掉。")
        add("")
        add("| score_10 | benchmark | 子维度 | L1 原值 | 为什么不是 0 |")
        add("|---|---|---|---|---|")
        for cell in free:
            add(
                f"| **{_fmt(cell['score_10'])}** | `{cell['benchmark_id']}` | "
                f"{cell['subdimension'][:40]} | {_fmt(cell['raw_value'], 4)} | {FREE_REASONS.get((cell['benchmark_id'], cell['subdimension']), FREE_REASONS.get(cell['benchmark_id'], '—'))} |"
            )
        add("")
        top = free[0]
        if top["score_10"] >= 9.5:
            add(f"⚠ **最极端的是 `{top['benchmark_id']}` 的「{top['subdimension']}」：地板 "
                f"{_fmt(top['score_10'])}/10，也就是满分。**")
            add("这不是计算错误——ASR 越低越好，而一段乱码既不是越狱成功也不构成攻击，")
            add("所以它的攻击成功率真的是 0，真的拿满分。**这个指标测不出「会不会安全地处理」，")
            add("只测得出「有没有被攻破」**，而一个什么都不输出的模型永远不会被攻破。")
            add("P17 / P19 的地板高到 4 分上下，主要就是这一格顶起来的。")
            add("")

    add("## 每个格子的 L1")
    add("")
    add("`来源` 三种：`simulated:<policy>` = 模拟抽样；`L3:random` = 乱码交真实 judge 实测；")
    add("`analytic` = 闭式推导。最后一列是 相关度×置信度 之后这个格子在它所属 P 里的权重。")
    add("")
    add("| benchmark | 子维度 | metric | L1 原值 | L1 score_10 | 来源 | 挂到 |")
    add("|---|---|---|---|---|---|---|")
    for cell in sorted(cells, key=lambda c: (c["benchmark_id"], c["subdimension"])):
        mapping = agg.find_mapping(
            cell["benchmark_id"], subdimension=cell["subdimension"], metric=cell["metric"]
        )
        targets = ", ".join(
            f"{a['p_code']}({mapping['default_benchmark_weight'] * a['weight']:.2f})"
            for a in (mapping or {}).get("abilities", [])
            if not a.get("excluded")
        )
        add(
            f"| `{cell['benchmark_id']}` | {cell['subdimension'][:46]} | `{cell['metric']}` | "
            f"{_fmt(cell['raw_value'], 4)} | **{_fmt(cell['score_10'])}** | "
            f"`{cell['l1_source']}` | {targets} |"
        )
    add("")

    add("## 口径与局限")
    add("")
    add(f"- **覆盖**：{len(cells)} 个格子 / {len({c['benchmark_id'] for c in cells})} 个 benchmark，"
        "与正式面板挂载的格子一一对应，没有缺格也没有补分。")
    add("- **P09 / P20 没有地板**，因为 mapping 里它们就没有非排除的格子——面板同样没有分，不是这里漏算。")
    add("- **模拟类格子取最后一轮 trial 的 `extra_metrics`**，保证同一次抽样内部自洽（各子指标来自同一批答案）；")
    add("  但对「就是 headline 的那一格」改用多轮均值，因为单轮波动可达 0.4 分。")
    add("- **judge 类格子的地板来自 40 题的乱码 run**，是量级参考不是精确值。")
    add("- 面板区间取 `PANEL_MODEL_KEYS` 里有分的模型；P03/P04 的面板最低是 0.00，"
        "那是 R26 的 capability_gap 判零（看不见图的模型），不是能力测量。")
    add("")

    if problems:
        add("## 未能计算的")
        add("")
        for problem in problems:
            add(f"- {problem}")
        add("")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()

    baselines = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    cells, problems = floor_cells(baselines)
    if not cells:
        print("没有算出任何格子，检查基线 JSON", file=sys.stderr)
        return 1

    evidence_rows, p_rows, _group_rows, _untested, _incapable = agg.score_atomic_p(cells)
    # score_atomic_p also emits R26 capability-gap rows for the published panel
    # models; the floor profile is only about the synthetic one.
    p_rows = [r for r in p_rows if r["model_key"] == FLOOR_MODEL]

    args.out.mkdir(parents=True, exist_ok=True)
    agg.dump_jsonl(args.out / "01_l1_floor_cells.jsonl", cells)
    agg.dump_jsonl(args.out / "02_l1_floor_evidence.jsonl", [e for e in evidence_rows if e["model_key"] == FLOOR_MODEL])
    agg.dump_jsonl(args.out / "03_l1_floor_p_scores.jsonl", p_rows)
    (args.out / "04_l1_floor_report.md").write_text(
        build_markdown(p_rows, cells, problems), encoding="utf-8"
    )

    print(f"格子 {len(cells)} 个，覆盖 {len({c['benchmark_id'] for c in cells})} 个 benchmark")
    print(f"算出 {len(p_rows)} 个 P 的地板分 -> {args.out}")
    for problem in problems:
        print(f"  ! {problem}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
