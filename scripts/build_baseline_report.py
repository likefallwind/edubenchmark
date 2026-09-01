#!/usr/bin/env python3
"""Assemble the baseline reference report.

Joins the three baseline layers with what the models actually scored, so every
number in `reports/eval/` can finally be read against a floor and (where one
exists) a ceiling:

    data/benchmark_baselines_v1.json         L1 random + L2 trivial strategy
    reports/eval/_baseline/<b>/<variant>/    L3 degenerate reply + human reference
    data/benchmark_human_baselines_v1.json   human performance from the literature
    reports/eval/<benchmark>/<model>/        observed model range

Writes `doc/benchmark_baselines_2026-08-04.md`. Idempotent — rerun after any
baseline run and it picks the new numbers up.

Observed-range hygiene (from the audit of reports/eval): smoke runs with a
handful of items sit in the same directories as full runs and often show
accuracy 1.0; date-named directories are snapshots, not models; several full
runs are truncated. So a run counts only if it is finished and scored at least
90% of the item count of the largest run for that benchmark.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from eval.judge_dirs import is_judge_dir  # noqa: E402

EVAL_DIR = ROOT / "reports" / "eval"
BASELINE_DIR = EVAL_DIR / "_baseline"
RANDOM_PATH = ROOT / "data" / "benchmark_baselines_v1.json"
HUMAN_PATH = ROOT / "data" / "benchmark_human_baselines_v1.json"
OUT_PATH = ROOT / "doc" / "benchmark_baselines_2026-08-04.md"

DATE_DIR = re.compile(r"^\d{4}-\d{2}-\d{2}$")
COVERAGE_FLOOR = 0.9

# Metrics where a smaller number is the better score, so "best run" flips.
LOWER_IS_BETTER = {"extra:overall.asr"}

# A pipeline smoke run leaves a real summary.json behind. Below this many items
# the number is noise and must not be quoted as a floor or a human anchor.
MIN_L3_N = 20


def _dig(obj: Any, path: str) -> Any:
    for part in path.split("."):
        if not isinstance(obj, dict) or part not in obj:
            return None
        obj = obj[part]
    return obj


def _headline_of(summary: dict, headline: str) -> float | None:
    if headline == "accuracy":
        value = summary.get("accuracy")
    elif headline.startswith("extra:"):
        value = _dig(summary.get("extra_metrics") or {}, headline.split(":", 1)[1])
    else:
        # judge-only benchmarks carry no headline path in the baselines file
        return None
    return float(value) if isinstance(value, (int, float)) else None


def observed_range(benchmark: str, headline: str) -> dict[str, Any]:
    """Min/max headline across the *comparable* finished runs of a benchmark."""
    base = EVAL_DIR / benchmark
    if not base.is_dir():
        return {}
    runs: list[tuple[str, int, float]] = []
    excluded: list[str] = []
    # EduBench's real results live one level down under judge-deepseek-v3.2/,
    # not directly under the benchmark dir, so descend into judge-* too.
    children = [c for c in base.iterdir() if c.is_dir()]
    for judge_dir in [c for c in children if is_judge_dir(c.name)]:
        children += [c for c in judge_dir.iterdir() if c.is_dir()]
    for child in sorted(children, key=lambda p: p.name):
        if not child.is_dir() or child.name.startswith("_") or DATE_DIR.match(child.name):
            continue
        path = child / "summary.json"
        if not path.exists():
            continue
        try:
            summary = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        if summary.get("run_status") == "running":
            excluded.append(f"{child.name}(未跑完)")
            continue
        value = _headline_of(summary, headline)
        scored = int(summary.get("scored") or 0)
        if value is None:
            continue
        runs.append((str(summary.get("model") or child.name), scored, value))
    if not runs:
        return {"excluded": excluded}
    top = max(scored for _, scored, _ in runs)
    keep = [(m, s, v) for m, s, v in runs if s >= COVERAGE_FLOOR * top]
    excluded += [f"{m}({s}/{top} 题)" for m, s, _ in runs if s < COVERAGE_FLOOR * top]
    if not keep:
        return {"excluded": excluded}
    worst, best = min(keep, key=lambda r: r[2]), max(keep, key=lambda r: r[2])
    if headline in LOWER_IS_BETTER:
        worst, best = best, worst
    return {
        "n_models": len(keep),
        "n_items": top,
        "lower_is_better": headline in LOWER_IS_BETTER,
        # "min"/"max" stay numeric extremes; worst/best carry the quality reading.
        "min": min(keep, key=lambda r: r[2])[2],
        "max": max(keep, key=lambda r: r[2])[2],
        "worst": worst[2],
        "worst_model": worst[0],
        "best": best[2],
        "best_model": best[0],
        "min_model": min(keep, key=lambda r: r[2])[0],
        "max_model": max(keep, key=lambda r: r[2])[0],
        "excluded": excluded,
    }


def _runs_below(benchmark: str, headline: str, floor: float) -> list[tuple[str, float]]:
    """Comparable finished runs scoring at or under the floor, worst first."""
    base = EVAL_DIR / benchmark
    if not base.is_dir() or headline in LOWER_IS_BETTER:
        return []
    rng = observed_range(benchmark, headline)
    if rng.get("n_items") is None:
        return []
    out: list[tuple[str, float]] = []
    for child in sorted(base.iterdir()):
        if not child.is_dir() or child.name.startswith("_") or DATE_DIR.match(child.name):
            continue
        path = child / "summary.json"
        if not path.exists():
            continue
        try:
            summary = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        if summary.get("run_status") == "running":
            continue
        if int(summary.get("scored") or 0) < COVERAGE_FLOOR * rng["n_items"]:
            continue
        value = _headline_of(summary, headline)
        if value is not None and value < floor:
            out.append((str(summary.get("model") or child.name), value))
    return sorted(out, key=lambda r: r[1])


def l3_results() -> dict[str, dict[str, Any]]:
    """Degenerate / human-reference runs produced by run_reference_baseline.py."""
    out: dict[str, dict[str, Any]] = {}
    if not BASELINE_DIR.is_dir():
        return out
    for bench_dir in sorted(BASELINE_DIR.iterdir()):
        if not bench_dir.is_dir():
            continue
        # 2026-08-31 起基线也按判官分命名空间（`judge-<slug>/<variant>/`）——地板是
        # 判官的读数，不带判官的路径下第二个判官只能覆盖第一个。旧的两级布局仍然读得
        # 出来，未迁移的 checkout 不至于突然一个基线都找不到。
        var_dirs = []
        for child in sorted(bench_dir.iterdir()):
            if not child.is_dir() or child.name.startswith("_"):
                continue
            if is_judge_dir(child.name):
                var_dirs += [v for v in sorted(child.iterdir()) if v.is_dir() and not v.name.startswith("_")]
            else:
                var_dirs.append(child)
        for var_dir in var_dirs:
            # `_stale_*` holds runs superseded by a judge/config fix; they are
            # kept on disk for comparison but must never enter the tables.
            if not var_dir.is_dir() or var_dir.name.startswith("_"):
                continue
            summary_path = var_dir / "summary.json"
            meta_path = var_dir / "baseline_meta.json"
            if not summary_path.exists():
                continue
            try:
                summary = json.loads(summary_path.read_text(encoding="utf-8"))
                meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
            except (json.JSONDecodeError, OSError):
                continue
            if summary.get("run_status") == "running":
                continue
            out.setdefault(bench_dir.name, {})[var_dir.name] = {
                "scored": summary.get("scored"),
                "underpowered": int(summary.get("scored") or 0) < MIN_L3_N,
                "accuracy": summary.get("accuracy"),
                "judge_model": summary.get("judge_model")
                or (summary.get("extra_metrics") or {}).get("judge_model"),
                "extra_metrics": summary.get("extra_metrics") or {},
                "layer": meta.get("layer"),
            }
    return out


def _l1_cell(block: dict[str, Any], variants: dict[str, Any], headline: str) -> str:
    """The L1 cell, resolved from the baseline JSON's per-benchmark `l1` block.

    Three provenances read differently and the cell says which: a simulated
    draw prints bare, a closed form is marked 推导, and a generation task's
    uniform draw is the measured L3 `random` gibberish. `n/a` is reserved for
    "uniform sampling is undefined here", never for "not computed yet".
    """
    if not block:
        return "—"
    if not block.get("defined", True):
        return "n/a"
    source = str(block.get("source") or "")
    value, suffix = block.get("value"), ""
    if source == "L3:random":
        run = (variants or {}).get("random")
        if not run or run.get("underpowered"):
            return "待跑"
        value = _headline_of(
            {"accuracy": run["accuracy"], "extra_metrics": run["extra_metrics"]}, headline
        )
        suffix = " (乱码实测)"
    elif source == "analytic":
        suffix = " (推导)"
    if value is None:
        return "待跑" if source == "L3:random" else "n/a"
    cell = _fmt(value) + suffix
    if block.get("direction") == "lower_is_better" or block.get("caveat"):
        cell += f" ⚠{block.get('caveat') or '满分方向'}"
    return cell


def _fmt(value: Any, digits: int = 4) -> str:
    if value is None:
        return "—"
    if isinstance(value, float):
        text = f"{value:.{digits}f}"
        # Only trim a fractional tail — rstrip("0") on "20" would yield "2".
        return text.rstrip("0").rstrip(".") if "." in text else text
    return str(value)


def build(random_data: dict, human_data: dict, l3: dict) -> str:
    lines: list[str] = []
    add = lines.append

    add("# Benchmark 基准锚点：随机基线 / 平凡策略 / 人类表现")
    add("")
    add("> 由 `scripts/build_baseline_report.py` 生成，不要手改。")
    add("> 数据源：`data/benchmark_baselines_v1.json`、`data/benchmark_human_baselines_v1.json`、")
    add("> `reports/eval/_baseline/`。改结论要改上游脚本后重跑。")
    add("")
    add("## 为什么不是一个数")
    add("")
    add("最初的问题是「纯随机瞎猜能得多少分」。真去逐个 benchmark 推导之后，结论是：")
    add("**对一半以上的 benchmark，均匀随机根本不是地板。** 所以分三层：")
    add("")
    add("| 层 | 含义 | 什么时候它才是真地板 |")
    add("|---|---|---|")
    add("| **L1 均匀随机** | 在题目自身答案空间上均匀抽样 | 选项数固定、类别均衡的选择题 |")
    add("| **L2 平凡策略** | 与题目内容无关的最优常数策略（按先验猜 / 全选多数类 / 从不改答案 / 全部弃答） | 类别不平衡的分类题、复合指标、量表打分 |")
    add("| **L3 退化回答** | 一段与题无关的回复交给真实 judge 打分 | judge 打分的生成类任务 |")
    add("")
    add("**L1 几乎总是有定义的，只是它的形状随答案空间变。** 早先的表把 L1 一律理解成")
    add("「名叫 `uniform_random` 的那个策略」，对三分之一的 benchmark 是错的：")
    add("`p08_abstention` 的均匀抽样是 `coin_flip`（4.99，不是 0），成对比较任务的是随机 judge（0.5），")
    add("生成任务的则是乱码——也就是 L3 的 `random` 变体本身。现在每个 benchmark 在")
    add("`benchmark_baselines_v1.json` 里都带一个 `l1` 块写明它的 L1 是哪个数、怎么来的，")
    add("主表的 L1 列直接读它，三种来源分别标注：不带后缀=模拟，`(推导)`=闭式，`(乱码实测)`=经 judge 实测。")
    add("")
    add("真正没有 L1 的只剩一个：`mmtutorbench_judge_calibration`——它没有公开人类金标，")
    add("adapter 本身不产出题目，没有可抽样的答案空间。表里记 `n/a`。")
    add("")
    add("方法上没有手推公式，而是**用真实的 `adapter.score()` 和 `extra_summary()` 跑合成答案**，")
    add("这样 RFS 的部分分、macro-F1、QWK 都走的是和正式评测同一条代码路径。")
    add("闭式解只留作交叉验证。")
    add("")
    add("**方法论验证**：用「MC 逐题 1/k + free-form 记 0」模拟 MathVista，得 "
        f"{_fmt((random_data['simulated'].get('mathvista', {}).get('policies', {}).get('uniform_random', {}) or {}).get('headline_mean'))}"
        "，而官方论文公布的 Random chance 是 **0.179**——对得上。")
    add("")

    # ---- main table -------------------------------------------------------
    add("## 主表")
    add("")
    add("`L1` = 均匀随机；`L2` = 最强的平凡策略（括号内是策略名）；`L3` = 退化回复经真实 judge；")
    add("`人类` = 文献或数据集自带的人类参照（分级见下）；`实跑` = 已完成 run 的区间。")
    add("**同一行内所有数字都是该 benchmark headline 的原始标度**，跨行不可比。")
    add("")
    add("空格的含义要分清（见文末「L1 的三种来源」）：")
    add("")
    add("- **`n/a`** = 该层在这个 benchmark 上**没有定义**，不是没算。")
    add("- **`待跑`** = 需要 API 的实测还没跑到这一行（L1 列出现它，说明该 benchmark 的 L1 就是 L3 的乱码变体）。")
    add("- **`—`** = 该层不适用（judge 类任务没有 L2，规则判分类任务没有 L3）。")
    add("- **`⚠满分方向`** = 该 headline 越低越好，这个数落在满分那一头，**不是地板**。")
    add("")
    add("| benchmark | headline | 题数 | L1 随机 | L2 平凡策略 | L3 退化 | 人类 | 实跑区间 |")
    add("|---|---|---|---|---|---|---|---|")

    all_names = sorted(
        set(random_data.get("simulated", {}))
        | set(random_data.get("analytic_only", {}))
        | set(random_data.get("judge_only", {}))
    )
    lit = human_data.get("literature", {})

    for name in all_names:
        sim = (random_data.get("simulated") or {}).get(name)
        ana = (random_data.get("analytic_only") or {}).get(name)
        jud = (random_data.get("judge_only") or {}).get(name)
        headline = (sim or ana or jud or {}).get("headline") or "—"
        n_items = _fmt((sim or {}).get("n_items"))

        variants = l3.get(name) or {}
        # Which number is L1 comes from the data's own `l1` block, never from
        # whether a policy happens to be named uniform_random — that guess was
        # wrong for a third of the set (p08_abstention's uniform draw is
        # coin_flip; a generation task's is the L3 `random` gibberish).
        block = (sim or {}).get("l1") or (ana or {}).get("l1") or (jud or {}).get("l1") or {}
        l1 = _l1_cell(block, variants, headline)
        l1_policy = block.get("source", "").split(":", 1)[-1] if block.get("source", "").startswith("simulated") else None

        # L2 candidates: every simulated policy that is not the L1 draw, plus
        # any closed-form floor. p07/p08_calibration carry both at once.
        l2 = "—"
        candidates: dict[str, float] = {}
        for key, entry in ((sim or {}).get("policies") or {}).items():
            if key != l1_policy and entry.get("headline_mean") is not None:
                candidates[key] = entry["headline_mean"]
        for key, info in ((ana or {}).get("floors") or {}).items():
            # Skip the floor that *is* this benchmark's L1, and any floor that
            # scores a different statistic than the headline.
            if key == block.get("floor_key") or info.get("metric"):
                continue
            if info.get("value") is not None:
                candidates[key] = info["value"]
        if candidates:
            best = max(candidates, key=lambda k: candidates[k])
            l2 = f"{_fmt(candidates[best])} ({best})"

        l3cell = "待跑" if name in (random_data.get("judge_only") or {}) else "—"
        degenerate = {
            v: _headline_of(
                {"accuracy": d["accuracy"], "extra_metrics": d["extra_metrics"]}, headline
            )
            for v, d in variants.items()
            if d.get("layer") == "L3_degenerate" and not d.get("underpowered")
        }
        degenerate = {k: v for k, v in degenerate.items() if v is not None}
        if degenerate:
            best = max(degenerate, key=lambda k: degenerate[k])
            l3cell = f"{_fmt(degenerate[best])} ({best})"

        entry = lit.get(name) or {}
        human = entry.get("human") or {}
        if human.get("value") is not None:
            hcell = f"{_fmt(human['value'])} ({human.get('grade')})"
        elif name in (human_data.get("no_external_human_reference") or {}):
            hcell = "无"
        else:
            hcell = "—"
        ref = {
            v: _headline_of(
                {"accuracy": d["accuracy"], "extra_metrics": d["extra_metrics"]}, headline
            )
            for v, d in variants.items()
            if d.get("layer") == "L3_reference" and not d.get("underpowered")
        }
        if ref.get("expert") is not None:
            hcell += f" / 同 judge {_fmt(ref['expert'])}"

        rng = observed_range(name, headline) if headline != "—" else {}
        if rng.get("min") is None:
            obs = "—"
        else:
            arrow = " ↓越低越好" if rng.get("lower_is_better") else ""
            obs = f"{_fmt(rng['min'])} – {_fmt(rng['max'])} ({rng['n_models']} 模型){arrow}"
        add(f"| `{name}` | `{headline}` | {n_items} | {l1} | {l2} | {l3cell} | {hcell} | {obs} |")

    add("")

    # ---- interpretation warnings -----------------------------------------
    add("## 解读警告（读分数前先看这一节）")
    add("")
    add("### 1. 三个指标的地板是 5.0/10，不是 0")
    add("")
    for name in ("p07_selfcheck", "p08_calibration"):
        ana = (random_data.get("analytic_only") or {}).get(name) or {}
        for policy, info in (ana.get("floors") or {}).items():
            if info.get("value") is not None:
                add(f"- **`{name}`** — {policy} = **{_fmt(info['value'])}**：{info['derivation']}")
    p08 = ((random_data.get("simulated") or {}).get("p08_abstention") or {}).get("policies") or {}
    if p08:
        vals = ", ".join(f"{k}={_fmt(v.get('headline_mean'))}" for k, v in p08.items())
        add(f"- **`p08_abstention`** — 实测三种与题目无关的策略：{vals}。")
        add("  这个 headline 对任何常数策略都恒等于 5.0，超过 5 才说明真的在区分可答/不可答。")
    add("")
    add("对照实跑值（同为 `score_10`）：")
    for name in ("p07_selfcheck", "p08_calibration", "p08_abstention"):
        src = (random_data.get("simulated") or {}).get(name) or (
            random_data.get("analytic_only") or {}
        ).get(name) or {}
        rng = observed_range(name, src.get("headline", "extra:score_10"))
        if rng.get("min") is None:
            continue
        gap = rng["min"] - 5.0
        verdict = (
            f"最低的 {rng['min_model']} 只比平凡策略高 {_fmt(gap, 3)} 分"
            if gap >= 0
            else f"最低的 {rng['min_model']} **低于**平凡策略 {_fmt(-gap, 3)} 分"
        )
        add(f"- `{name}`：{_fmt(rng['min'], 3)} – {_fmt(rng['max'], 3)}（{rng['n_models']} 模型）——{verdict}。")
    add("")
    add("**p07_selfcheck 尤其值得停下来看**：它衡量的是「自我复查能不能改对而不改坏」，")
    add("而全部模型都挤在 5.0 这条「从不改答案」的线附近。这不是分数低，是这个指标目前几乎没测出东西。")
    add("")
    add("这三个的 **L1 和 L2 分得很开**，别把 5.0 当成随机分：")
    add("")
    for name in ("p07_selfcheck", "p08_calibration", "p08_abstention"):
        sim = (random_data.get("simulated") or {}).get(name) or {}
        block = sim.get("l1") or {}
        if block.get("value") is None:
            continue
        add(f"- `{name}` — L1 均匀乱答 = **{_fmt(block['value'], 3)}**，L2 最优平凡策略 = **5.0**。{sim.get('note', '')}")
    add("")
    add("换句话说，一个真去瞎猜的模型在 `p07_selfcheck` 上只有 1.85 分，而一个干脆不复查的模型白拿 5.0——")
    add("**这个指标奖励的是「别动」，不是「会查」**，实跑区间紧贴 5.0 正是这个原因。")
    add("")

    add("### 2. 类别不平衡的判分任务：多数类基线远高于随机")
    add("")
    for name in ("mrbench_judge", "bea2025_judge"):
        sim = (random_data.get("simulated") or {}).get(name)
        if not sim:
            continue
        pol = sim.get("policies") or {}
        add(f"- **`{name}`**（headline `{sim['headline']}`）：")
        for pname, entry in pol.items():
            add(
                f"  - {pname}: headline={_fmt(entry.get('headline_mean'))}, "
                f"accuracy={_fmt(entry.get('accuracy_mean'))}"
            )
    add("")
    add("注意 accuracy 与 headline 的分裂：全选多数类的 **accuracy 能到 0.63–0.72**，")
    add("但 macro-F1 只有 0.26–0.28。仓库把 headline 定成 macro-F1 是对的，")
    add("**任何时候都不要用这两个 benchmark 的 accuracy 做横向比较**。")
    add("")

    add("### 3. 地板吃掉了报告分数的多少")
    add("")
    add("「地板占比」= 平凡策略分 ÷ 最好成绩。占比越高，说明公布出来的那个数里")
    add("越大一块是白送的，模型之间真正拉开的差距越小。")
    add("")
    add("| benchmark | 最强平凡策略 | 地板 | 实跑最低 | 实跑最高 | 地板占比 | 地板以上的有效区间 |")
    add("|---|---|---|---|---|---|---|")
    rows: list[tuple] = []
    # Simulated floors and closed-form floors are the same kind of claim, so the
    # "how much of the score is free" table must cover both — otherwise the
    # pairwise-comparison tasks, whose 0.5 floor is the most consequential one in
    # the whole set, silently drop out.
    # p07_selfcheck / p08_calibration have a simulated L1 *and* a closed-form L2,
    # so accumulate per benchmark rather than appending twice — two rows for one
    # benchmark, disagreeing on the floor, is exactly what this table must not do.
    merged: dict[str, tuple[str, dict[str, float]]] = {}
    for name, sim in (random_data.get("simulated") or {}).items():
        pol = sim.get("policies") or {}
        vals = {k: v.get("headline_mean") for k, v in pol.items() if v.get("headline_mean") is not None}
        if vals:
            merged[name] = (sim["headline"], vals)
    for name, ana in (random_data.get("analytic_only") or {}).items():
        vals = {
            k: v["value"]
            for k, v in (ana.get("floors") or {}).items()
            if v.get("value") is not None and not v.get("metric")
        }
        if vals:
            headline, prev = merged.get(name, (ana["headline"], {}))
            merged[name] = (headline, {**prev, **vals})
    floor_sources: list[tuple[str, str, dict[str, float]]] = [
        (name, headline, vals) for name, (headline, vals) in merged.items()
    ]

    for name, headline, vals in floor_sources:
        best = max(vals, key=lambda k: vals[k])
        rng = observed_range(name, headline)
        if rng.get("max") is None or rng["max"] <= 0:
            continue
        share = vals[best] / rng["max"]
        if share >= 0.25:
            rows.append((name, best, vals[best], rng["min"], rng["max"], share))
    for name, policy, floor, lo, hi, share in sorted(rows, key=lambda r: -r[5]):
        add(
            f"| `{name}` | `{policy}` | {_fmt(floor)} | {_fmt(lo)} | {_fmt(hi)} | "
            f"**{share:.0%}** | {_fmt(hi - floor)} |"
        )
    add("")
    add("### 3b. 跌破地板的：这些分数说明模型在该任务上没有可用信号")
    add("")
    any_below = False
    for name, headline, vals in sorted(floor_sources):
        best = max(vals, key=lambda k: vals[k])
        floor = vals[best]
        runs = _runs_below(name, headline, floor)
        if not runs:
            continue
        any_below = True
        rng = observed_range(name, headline)
        add(
            f"**`{name}`**（地板 {_fmt(floor)}，策略 `{best}`）—— "
            f"{len(runs)}/{rng.get('n_models', '?')} 个模型跌破："
        )
        for model, value in runs:
            add(f"- {model}: {_fmt(value)}")
        add("")
    if not any_below:
        add("（暂无）")
        add("")
    add("`mathtutorbench_scaffolding` 这一条尤其要读懂：它的 headline 是**与金标教师回应的成对胜率**，")
    add("0.5 就是「与专家教师打平」。跌破 0.5 不是「分数偏低」，而是**在搭脚手架这件事上确实不如人类教师**。")
    add("对照 `mathtutorbench_pedagogy`（同样的比法、同样的 0.5 锚）七个模型全部在 0.66–0.87：")
    add("**这两个任务的结论方向是相反的**，而只看原始分会以为都是「有的高有的低」。")
    add("")

    add("### 4. 地板在另一头 / 指标本身无区分度")
    add("")
    for name, info in (random_data.get("judge_only") or {}).items():
        if "⚠" in info.get("reason", ""):
            add(f"- **`{name}`**：{info['reason']}")
    add("")

    # ---- judge validity ---------------------------------------------------
    calib_block = human_data.get("judge_calibration_vs_human_annotators") or {}
    calib = calib_block.get("results") or {}
    ctrl = calib_block.get("cross_tutor_control")
    # The prompt-leak finding is a static property of the adapter, so it is
    # reported unconditionally — unlike the paired numbers, which are suppressed
    # while a baseline run is mid-flight.
    if True:
        add("## ⚠ mrbench_tutor / bea2025_tutor 的 prompt 把评分表告诉了模型")
        add("")
        add("这条是查「人类专家为什么分这么低」时挖出来的，属于 harness 缺陷，不是模型或 judge 的问题。")
        add("")
        add("**我们给被测模型的 prompt，逐条罗列了 judge 要打的维度**：")
        add("")
        add("| prompt 里的指令 | judge 的评分维度 |")
        add("|---|---|")
        add("| identify and locate any mistake the student made | Mistake_Identification + Mistake_Location |")
        add("| give a helpful hint or explanation | Providing_Guidance |")
        add("| make the next step clear | **Actionability** |")
        add("| Do NOT reveal the final answer outright | Revealing_of_the_Answer |")
        add("| encouraging | Tutor_Tone |")
        add("| natural | Humanlikeness |")
        add("")
        add("bea2025_tutor 的四条指令同样 1:1 对上它的四个维度。MRBench 版还额外把")
        add("**参考解法（Reference solution）**放进了 prompt。")
        add("")
        add("也就是说：**模型被明确告知了评分标准，还拿到了答案**。")
        add("数据集里的人类专家教师和那 8 个 2024 年 LLM，写回复时两样都没有。")
        add("")
        add("### 后果")
        add("")
        add("这解释了下面这组数为什么会长这样——不需要引入「judge 有偏见」之类的假设：")
        add("")
        if calib:
            add("| benchmark | 题数 | 人类标注者判专家 | 我们的 judge 判**同一批**专家 | 同一 judge 判模型 |")
            add("|---|---|---|---|---|")
            for name, info in sorted(calib.items()):
                rng = observed_range(name, "extra:pass_rate")
                model_cell = (
                    f"{_fmt(rng['min'])} – {_fmt(rng['max'])}" if rng.get("min") is not None else "—"
                )
                add(
                    f"| `{name}` | {info['n_items']} | **{_fmt(info['human_annotator_pass_rate'])}** | "
                    f"**{_fmt(info['our_judge_pass_rate'])}** | {model_cell} |"
                )
            add("")
            add("人类标注者认为专家教师和模型在同一档；我们的 judge 认为专家教师远不如模型。")
            add("差距集中在 prompt 明确点名的那几维：")
            add("")
            add("| benchmark | 维度 | 人类标注 | 我们的 judge | 落差 |")
            add("|---|---|---|---|---|")
            for name, info in sorted(calib.items()):
                for dim, pair in info["per_key_dimension_yes_share"].items():
                    h, j = pair["human_annotator"], pair["our_judge"]
                    gap = (h - j) if (h is not None and j is not None) else None
                    mark = " ⚠" if gap is not None and gap >= 0.4 else ""
                    add(f"| `{name}` | {dim} | {_fmt(h)} | {_fmt(j)} | −{_fmt(gap)}{mark} |")
        else:
            add("（专家同尺复评正在重跑，数字待补；`reports/eval/_baseline/*/expert/` 完成后重跑本脚本。）")
        add("")
        add("典型分歧长这样（MRBench，学生上一轮已自己纠正了错误）：")
        add("")
        add("> **专家教师的回复**：So 12 devided by 4 =. .?")
        add(">")
        add("> 人类标注 `Mistake_Identification` = **Yes**（错误学生已自纠，教师正确识别并推进下一步）")
        add("> 我们的 judge = **No**（这句话里找不到任何指出错误的表述）")
        add("")

        if ctrl:
            add("### 对照：judge 对所有 tutor 都比人类标注者严")
            add("")
            add("顺带排除掉「judge 专门针对人类」这个可能。`mrbench_judge` 的既有 run 里，")
            add("同一个模型已经把全部 9 个 tutor 的回复对着人类金标判过一遍（免费的大样本）：")
            add("")
            add("| tutor | 词数中位 | 人类判 pass | judge 判 pass | 差 |")
            add("|---|---|---|---|---|")
            for tutor, info in (ctrl.get("per_tutor") or {}).items():
                mark = " ←人类" if tutor in ("Expert", "Novice") else ""
                add(
                    f"| `{tutor}`{mark} | {_fmt(info['median_words'], 0)} | "
                    f"{_fmt(info['human_annotator_pass_rate'])} | {_fmt(info['judge_pass_rate'])} | "
                    f"{info['gap']:+.3f} |"
                )
            add("")
            add("- judge 对**每一个** tutor 都比人类标注者严，Sonnet 的 −0.450 比人类专家的 −0.430 还狠。")
            add(f"- 回复长度与该落差的相关只有 **r = {ctrl.get('length_vs_gap_pearson_r')}**，n=9，不显著。")
            add("- 这 9 个 tutor 的回复**都不是用我们的 prompt 生成的**，所以它们全部落在 0.02–0.31，")
            add("  而吃了我们 prompt 的模型落在 0.68–0.83 —— 与上面的泄题解释一致。")
            add("")
            add(f"> 口径说明：{ctrl.get('prompt_caveat')}")
            add("")

        add("### 结论与待办")
        add("")
        add("1. **`pass_rate` 不能当「辅导能力」的绝对值用，更不能拿来和人类教师比。**")
        add("   模型手里有评分表和答案，人类专家两样都没有。主表里那个人类值已标为 B 级，")
        add("   同尺复评下的 0.10–0.15 也同样不能单独拿出来说事——**两个数都不构成对比**。")
        add("2. **模型之间横向比仍然有效**：所有被测模型吃的是同一个 prompt。")
        add("3. **映射要留意。** `mrbench_tutor` 的逐维 Yes 占比挂在 P13/P15/P17 上，")
        add("   这几个 P 的绝对值含有「照着指令写」的成分。")
        add("")
        add("**决定性实验（未做）**：用一个不罗列评分维度、不给参考解法的中性 prompt，")
        add("让同一个现代模型重跑一遍。若 pass_rate 显著回落到人类专家那一档，")
        add("就确认是 prompt 泄题；若基本不变，则说明确实是能力差距。")
        add("在这个实验出结果前，不要去改 judge 或 rubric——问题大概率不在那边。")
        add("")

    # ---- human section ----------------------------------------------------
    add("## 人类表现：能查到的很少，查不到的如实留空")
    add("")
    cov = human_data.get("coverage") or {}
    add(
        f"{cov.get('with_human_value', 0)}/{cov.get('literature_entries', 0)} 个 benchmark 有可用的人类数值，"
        f"另有 {cov.get('no_external_reference', 0)} 个属自建或无外部人类参照。分级分布：{cov.get('by_grade')}。"
    )
    add("")
    add("| 分级 | 含义 |")
    add("|---|---|")
    for grade, meaning in (human_data.get("schema_notes", {}).get("grades") or {}).items():
        add(f"| **{grade}** | {meaning} |")
    add("")
    add("### 有数的")
    add("")
    add("| benchmark | 人类值 | 分级 | 来源 | 关键限制 |")
    add("|---|---|---|---|---|")
    for name, entry in sorted(lit.items()):
        human = entry.get("human") or {}
        if human.get("value") is None:
            continue
        add(
            f"| `{name}` | {_fmt(human['value'])} | {human.get('grade')} | "
            f"{human.get('source', '')} | {human.get('note', '').replace(chr(10), ' ')} |"
        )
    add("")
    add("### 查过但没有的（附证据，不必重查）")
    add("")
    add("| benchmark | 查了什么 | 结论 |")
    add("|---|---|---|")
    for name, entry in sorted(lit.items()):
        human = entry.get("human") or {}
        if human.get("value") is not None:
            continue
        add(f"| `{name}` | {human.get('source', '')} | {entry.get('evidence', '')} |")
    add("")

    # ---- L3 detail --------------------------------------------------------
    if l3:
        add("## L3 实跑明细：退化回复与人类参照，同一个 judge")
        add("")
        add("`refusal` = 「我不确定」；`echo` = 复述原话；`generic` = 与题无关但语气漂亮的通用教学话术；")
        add("`expert` / `novice` = 数据集自带的人类教师回复，用**我们的 judge** 复评。")
        add("")
        add("| benchmark | 变体 | 层 | 题数 | headline | judge |")
        add("|---|---|---|---|---|---|")
        for bench in sorted(l3):
            sim = (random_data.get("simulated") or {}).get(bench) or {}
            ana = (random_data.get("analytic_only") or {}).get(bench) or {}
            jud_e = (random_data.get("judge_only") or {}).get(bench) or {}
            lit_e = lit.get(bench) or {}
            headline = (
                sim.get("headline")
                or ana.get("headline")
                or jud_e.get("headline")
                or lit_e.get("headline")
                or "accuracy"
            )
            for variant, data in sorted(l3[bench].items()):
                value = _headline_of(
                    {"accuracy": data["accuracy"], "extra_metrics": data["extra_metrics"]}, headline
                )
                n_cell = f"{data.get('scored')}"
                if data.get("underpowered"):
                    n_cell += f" ⚠<{MIN_L3_N}，样本过小，仅表示管线跑通"
                add(
                    f"| `{bench}` | {variant} | {data.get('layer', '')} | {n_cell} | "
                    f"{_fmt(value)} | {data.get('judge_model')} |"
                )
        add("")
        add("**读法**：`generic` 这一行最关键。它完全没有解题内容，只有教学腔。")
        add("它拿到的分就是该 judge 奖励「形式」而非「实质」的部分，必须从模型分里扣掉再看差距。")
        add("")

    add("## L1 的三种来源")
    add("")
    add("「均匀随机能得多少分」对每个 benchmark 都成立，只是**均匀抽样抽的是什么**不一样，")
    add("所以这个数有三种来法。主表的 L1 列按来源标注，下面逐类列全。")
    add("")

    def _by_source(kind: str) -> list[tuple[str, dict, dict]]:
        rows = []
        for section in ("simulated", "analytic_only", "judge_only"):
            for nm, info in (random_data.get(section) or {}).items():
                block = info.get("l1") or {}
                if block.get("source") == kind and block.get("defined", True):
                    rows.append((nm, block, info))
        return sorted(rows)

    add("### A. 模拟——答案空间可以枚举，直接抽")
    add("")
    add("选项、标签、步号、评分档位这些都能列举，于是用真实的 `adapter.score()` 跑合成答案。")
    add("注意抽的不总是「选项字母」：")
    add("")
    for nm, block, info in [r for r in _by_source("simulated:coin_flip") + _by_source("simulated:random_text")]:
        add(f"- `{nm}` — L1 = **{_fmt(block.get('value'))}**（策略 `{block['source'].split(':')[1]}`）。{info.get('note', '')}")
    add("")
    add("其余模拟类的 L1 就是 `uniform_random` 策略本身，数值见主表。")
    add("")

    add("### B. 推导——均匀抽样的期望可以证明，模拟只会添噪声")
    add("")
    for nm, block, _ in _by_source("analytic"):
        add(f"- `{nm}` — L1 = **{_fmt(block.get('value'))}**：{block.get('derivation', '')}")
    add("")
    add("这一类里 `mathtutorbench` 的四个成对比较任务最容易读错：**0.5 既是随机地板也是人类锚**，")
    add("含义是「与专家教师打平」，低于 0.5 才说明比金标教师差。")
    add("")

    add("### C. 实测——生成任务的均匀抽样就是乱码，只能喂给真实 judge")
    add("")
    add("模型要写一段话，不存在「选项」可以抽，但答案空间仍然是 token 序列，")
    add("在它上面均匀抽样就是乱码。所以这类的 L1 = L3 的 **`random`** 变体，是同一个数。")
    add("")
    add("两个例外不必实测，标 `(推导)`：`eduillustrate` 交付的是 Manim 代码，乱码编译不过，")
    add("八个维度全 0；`longtutor_teaching` 的 headline 是解析成功率，乱码同样拿 1.0。")
    add("")
    add("两点要注意：")
    add("")
    add("1. **不是所有都归零。** 打分量表自带下限，乱码也拿得到。EduBench 是 1-10 量表，")
    add("   下限就是 **1.0**；拿模型的 8.0 直接当「比 0 高 8 分」会把差距高估整整一分。")
    add("2. **有一个理论上可以为负。** TutorBench 的 rubric 含 −5 权重项，所以刻度下限无法先验给出。")
    add("   实测乱码是 **+2.54**——judge 并没有触发那些扣分项，乱码只是拿不到分，不是被扣分。")
    add("")
    add("| benchmark | L1（乱码实测） | 刻度下限 | 说明 |")
    add("|---|---|---|---|")
    for name, info in sorted((random_data.get("judge_only") or {}).items()):
        block = info.get("l1") or {}
        if not block.get("defined", True):
            continue  # listed under D instead
        floor = info.get("scale_floor")
        headline = info.get("headline") or "—"
        # The column header already says 乱码实测; repeating it in every cell
        # just makes the table wider.
        measured = _l1_cell(block, l3.get(name) or {}, headline).replace(" (乱码实测)", "")
        add(
            f"| `{name}` | {measured} | {_fmt(floor) if floor is not None else '需实测'} "
            f"| {info.get('reason', '')} |"
        )
    add("")

    add("### D. 唯一真的没有 L1 的")
    add("")
    for section in ("simulated", "analytic_only", "judge_only"):
        for nm, info in sorted((random_data.get(section) or {}).items()):
            block = info.get("l1") or {}
            if not block.get("defined", True):
                add(f"- `{nm}` — {block.get('derivation', '')}")
    add("")

    add("### E. 反过来的两个")
    add("")
    add("- `mooccube_prereq` — 唯一自带 chance correction 的 benchmark，")
    add("  随机作答的 `score_10` 已经被扣到接近 0，不存在比它更高的平凡策略，所以 L2 空着。")
    add("- `ifeval` — **L1 高于 L2**：乱码（0.118）比一段像样的散文（0.056）更能满足")
    add("  「全小写 / 不许出现逗号 / 字数下限」这类纯形式约束。这里最强的与题无关策略就是乱码本身。")
    add("")

    add("## 未覆盖 / 待办")
    add("")
    skipped = random_data.get("skipped") or {}
    if skipped:
        for name, reason in skipped.items():
            add(f"- `{name}`：{reason}")
    # Spell out which benchmark is missing which variant: "L3 只跑了部分" gave no
    # way to tell a missing L1 (the `random` variant) from a missing extra angle.
    degenerate_variants = ("random", "refusal", "echo", "generic")
    no_l1, partial = [], []
    for name, info in sorted((random_data.get("judge_only") or {}).items()):
        block = info.get("l1") or {}
        if not block.get("defined", True):
            continue
        have = {v for v in degenerate_variants if v in (l3.get(name) or {})}
        # Only a benchmark whose L1 *is* the gibberish run is missing an L1 when
        # that run is absent; the two with a derived L1 just lack the extra L3
        # angles, which is a much smaller gap.
        if "random" not in have and block.get("source") == "L3:random":
            no_l1.append(name)
        missing = [v for v in degenerate_variants if v not in have]
        if have and missing:
            partial.append((name, missing))
    if no_l1:
        add(f"- **这些 benchmark 连 L1 都还没有**（它们的 L1 就是 L3 的 `random` 变体）："
            f"{'、'.join('`' + n + '`' for n in no_l1)}。跑 "
            "`scripts/run_reference_baseline.py --benchmark <名> --variant random` 即可补上。")
    for name, missing in partial:
        add(f"- `{name}` 的退化四件套只跑了 {4 - len(missing)}/4，缺 "
            f"{'、'.join('`' + m + '`' for m in missing)}。")
    add("- L3 的每个变体默认只跑 40 题（`--limit`），是量级参考而非精确值。")
    add("- 本报告**不改**聚合脚本的归一化。给 P01–P20 做 chance correction 会让分数与 R25 不可比，")
    add("  那是独立决策；`benchmark_baselines_v1.json` 的字段已为此留好接口。")
    add("")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, default=OUT_PATH)
    args = ap.parse_args()

    random_data = json.loads(RANDOM_PATH.read_text(encoding="utf-8"))
    human_data = json.loads(HUMAN_PATH.read_text(encoding="utf-8"))
    text = build(random_data, human_data, l3_results())
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out} ({len(text.splitlines())} lines)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
