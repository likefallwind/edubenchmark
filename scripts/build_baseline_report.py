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

ROOT = Path(__file__).resolve().parents[1]
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
    # EduBench's real results live one level down under _judge-deepseek-v3.2/,
    # not directly under the benchmark dir, so descend into _judge-* too.
    children = [c for c in base.iterdir() if c.is_dir()]
    for judge_dir in [c for c in children if c.name.startswith("_judge-")]:
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
        for var_dir in sorted(bench_dir.iterdir()):
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


def _fmt(value: Any, digits: int = 4) -> str:
    if value is None:
        return "—"
    if isinstance(value, float):
        return f"{value:.{digits}f}".rstrip("0").rstrip(".")
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
    add("| **L3 退化回答** | 一段与题无关的回复交给真实 judge 打分 | judge 打分的生成类任务（均匀随机无定义） |")
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
    add("空格的含义要分清（见文末「为什么有些 benchmark 没有随机分」）：")
    add("")
    add("- **`n/a`** = 该层在这个 benchmark 上**没有定义**，不是没算。")
    add("- **`待跑`** = 需要 API 的 L3 还没跑到这一行。")
    add("- **`—`** = 该层不适用（例如 judge 类任务本来就没有 L1/L2）。")
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

        l1 = l2 = "—"
        # A judge-scored generation task still has a knowable floor: the bottom
        # of the rating scale. Surface it in the L1 column rather than leaving
        # the cell blank — "random gibberish scores 1.0, not 0" is exactly the
        # number a reader needs before subtracting a floor from a model score.
        if jud and jud.get("scale_floor") is not None:
            l1 = f"{_fmt(jud['scale_floor'])} (刻度下限)"
        if sim:
            policies = sim.get("policies") or {}
            uniform = policies.get("uniform_random") or {}
            # No uniform_random policy means uniform sampling is undefined for
            # this answer space (open-ended numeric/symbolic, rule checker,
            # composite metric) — not that the computation was skipped.
            l1 = _fmt(uniform.get("headline_mean")) if uniform else "n/a"
            others = {
                k: v.get("headline_mean")
                for k, v in policies.items()
                if k != "uniform_random" and v.get("headline_mean") is not None
            }
            if others:
                best = max(others, key=lambda k: others[k])
                l2 = f"{_fmt(others[best])} ({best})"
        elif ana:
            floors = ana.get("floors") or {}
            named = {k: v.get("value") for k, v in floors.items() if v.get("value") is not None}
            if named:
                best = max(named, key=lambda k: named[k])
                l2 = f"{_fmt(named[best])} ({best})"

        l3cell = "待跑" if name in (random_data.get("judge_only") or {}) else "—"
        variants = l3.get(name) or {}
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
    floor_sources: list[tuple[str, str, dict[str, float]]] = []
    for name, sim in (random_data.get("simulated") or {}).items():
        pol = sim.get("policies") or {}
        vals = {k: v.get("headline_mean") for k, v in pol.items() if v.get("headline_mean") is not None}
        if vals:
            floor_sources.append((name, sim["headline"], vals))
    for name, ana in (random_data.get("analytic_only") or {}).items():
        vals = {
            k: v["value"] for k, v in (ana.get("floors") or {}).items() if v.get("value") is not None
        }
        if vals:
            floor_sources.append((name, ana["headline"], vals))

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
    calib = (human_data.get("judge_calibration_vs_human_annotators") or {}).get("results") or {}
    if calib:
        add("## ⚠ 最重要的发现：judge 把人类专家教师排在所有模型之下")
        add("")
        add("这是本轮基线工作的副产品，但比任何一条地板都重要。")
        add("")
        add("MRBench 和 BEA 2025 的数据集里自带**真人专家教师**的回复。把这批回复原样喂给")
        add("我们评测模型时用的那个 judge，得到的分数应该和人类标注者给同一批回复的分数接近——")
        add("否则两把尺子就不是一回事。结果差得很远：")
        add("")
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
        add("**人类标注者认为专家教师和模型在同一水平线上（0.53–0.65 vs 0.68–0.83）；")
        add("我们的 judge 认为专家教师（0.10–0.15）远不如模型（0.68–0.83）。**")
        add("")
        add("崩在哪一维，逐维看得很清楚：")
        add("")
        add("| benchmark | 维度 | 人类标注 | 我们的 judge | 落差 |")
        add("|---|---|---|---|---|")
        for name, info in sorted(calib.items()):
            for dim, pair in info["per_key_dimension_yes_share"].items():
                h, j = pair["human_annotator"], pair["our_judge"]
                gap = (h - j) if (h is not None and j is not None) else None
                mark = " ⚠" if gap is not None and gap >= 0.4 else ""
                add(f"| `{name}` | {dim} | {_fmt(h)} | {_fmt(j)} | −{_fmt(gap)}{mark} |")
        add("")
        add("`Actionability` 塌得最狠（MRBench 0.85 → 0.30）。看一条真实的专家回复就明白了：")
        add("")
        add("> Not quite, remember, Jam has three boxes full of pencils and 2 loose pencils")
        add("> which give a total of 26 pencils.")
        add("")
        add("真人教师说话短、依赖上下文，不会把「你下一步该做什么」显式写出来；")
        add("人类标注者懂教学语境，判 Yes。LLM judge 找不到显式的行动指令，判 No。")
        add("而模型的回复通常长、结构化、把每个 rubric 关键词都写全——正好投 judge 所好。")
        add("")
        add("### 这意味着什么")
        add("")
        add("`mrbench_tutor` / `bea2025_tutor` 的 `pass_rate`，在我们当前的 judge 下，")
        add("**相当程度上测的是「写得像不像 LLM 式辅导」，而不是教学质量**。")
        add("三点后果：")
        add("")
        add("1. **不要拿这两个 benchmark 的分数说「模型的辅导能力接近/超过人类教师」。**")
        add("   本报告主表里那个 0.605 的人类值是人类标注者给的，与模型分不同尺，已标为 B 级。")
        add("2. **映射受影响。** `mrbench_tutor` 的逐维 Yes 占比挂在 P13/P15/P17 上，")
        add("   这部分分数带着同样的风格偏好。")
        add("3. **这是可修的。** 要么换 judge 并用这批专家回复做校准（专家应当落在模型区间内），")
        add("   要么改 rubric 让 Actionability 不再奖励显式措辞。修之前，先别把这两个分数当教学质量看。")
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
            lit_e = lit.get(bench) or {}
            headline = sim.get("headline") or ana.get("headline") or lit_e.get("headline") or "accuracy"
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

    add("## 为什么有些 benchmark 没有随机分")
    add("")
    add("主表里的空格几乎都不是「没算」，而是**均匀随机在那种题型上没有定义**。四类：")
    add("")
    add("### A. judge 打分的生成题——随机的对应物是乱码，得实测")
    add("")
    add("模型要写一段话，不存在「选项」可以抽。但**期望仍然是有的**：生成任务的答案空间就是")
    add("token 序列，在它上面均匀抽样就是乱码。所以「瞎填能得几分」= 把乱码喂给真实 judge 看它给几分，")
    add("对应 L3 的 **`random`** 变体。")
    add("")
    add("两点要注意：")
    add("")
    add("1. **不是所有都归零。** 打分量表自带下限，乱码也拿得到。EduBench 是 1-10 量表，")
    add("   下限就是 **1.0**；拿模型的 8.0 直接当「比 0 高 8 分」会把差距高估整整一分。")
    add("   下表的「刻度下限」列就是这个数。")
    add("2. **有一个可能是负的。** TutorBench 的 rubric 含 −5 权重项，乱码的期望**低于 0**。")
    add("")
    add("| benchmark | 刻度下限 | 说明 |")
    add("|---|---|---|")
    for name, info in sorted((random_data.get("judge_only") or {}).items()):
        floor = info.get("scale_floor")
        add(f"| `{name}` | {_fmt(floor) if floor is not None else '需实测'} | {info.get('reason', '')} |")
    add("")
    add("### B. 地板是代数推出来的，模拟没有意义")
    add("")
    for name, info in sorted((random_data.get("analytic_only") or {}).items()):
        floors = info.get("floors") or {}
        first = next((v for v in floors.values() if v.get("value") is not None), None)
        derivation = (first or {}).get("derivation", "")
        add(f"- `{name}` — {derivation}")
    add("")
    add("### C. 答案空间是开放的，「均匀」无从定义")
    add("")
    add("填任意实数或 LaTeX 表达式的题，在实数上均匀抽样的命中概率测度为 0。")
    add("这类改用更严的替代策略——按数据集真实答案分布猜（`prior_random`），")
    add("即「瞎猜的上界」；规则校验类则用一段与题无关的通用文本。")
    add("")
    for name, sim in sorted((random_data.get("simulated") or {}).items()):
        policies = sim.get("policies") or {}
        if "uniform_random" in policies:
            continue
        used = ", ".join(
            f"`{k}`={_fmt(v.get('headline_mean'))}" for k, v in policies.items()
        )
        add(f"- `{name}` — 替代策略：{used}")
        add(f"  - {sim.get('note', '')}")
    add("")
    add("### D. 反过来的一个")
    add("")
    add("- `mooccube_prereq` — 唯一自带 chance correction 的 benchmark，")
    add("  随机作答的 `score_10` 已经被扣到接近 0，不存在比它更高的平凡策略，所以 L2 空着。")
    add("")

    add("## 未覆盖 / 待办")
    add("")
    skipped = random_data.get("skipped") or {}
    if skipped:
        for name, reason in skipped.items():
            add(f"- `{name}`：{reason}")
    add("- L3 只跑了部分 benchmark。其余 judge 打分的生成类任务见 "
        "`data/benchmark_baselines_v1.json` → `judge_only`，用 "
        "`scripts/run_reference_baseline.py` 逐个补。")
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
