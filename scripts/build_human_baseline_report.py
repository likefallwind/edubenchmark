#!/usr/bin/env python3
"""Assemble the human-anchor / usability-threshold report.

Sister report to `build_baseline_report.py`. That one answers "地板在哪" (random,
trivial strategy, degenerate reply). This one answers the two questions above the
floor, which are **not the same question** and get separate tables:

    人类参照锚   人在这套题上能拿多少分
    可用门槛     多少分算能上线，不管人在哪

Inputs:

    data/benchmark_human_baselines_v1.json   both tables + per-task human values
    reports/eval/<benchmark>/<model>/        observed model range
    reports/eval/_baseline/<b>/<variant>/    expert / novice replies re-scored
                                             through *our* judge

Writes `doc/benchmark_human_baselines_2026-08-15.md`. Idempotent.

Run-hygiene rules (coverage floor, date-dir and `_`-prefix skipping, descending
into `_judge-*`) are imported from `build_baseline_report` rather than
reimplemented, so the two reports can never disagree about which runs count.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_baseline_report import (  # noqa: E402
    COVERAGE_FLOOR,
    DATE_DIR,
    EVAL_DIR,
    LOWER_IS_BETTER,
    _headline_of,
    observed_range,
)

HUMAN_PATH = ROOT / "data" / "benchmark_human_baselines_v1.json"
OUT_PATH = ROOT / "doc" / "benchmark_human_baselines_2026-08-15.md"

KIND_LABEL = {
    "field_standard": "行业标准",
    "inter_annotator": "标注者一致性",
    "construct": "指标构造",
    "institutional": "制度性代理",
    "none": "无门槛",
}


# --------------------------------------------------------------------------
# reading our own runs
# --------------------------------------------------------------------------


def run_values(benchmark: str, metric: str) -> list[tuple[str, float]]:
    """Every comparable finished run's value on `metric`, best first.

    Same filtering as `observed_range`, but returns the per-model list — needed
    to say *how many* models clear a threshold, not just the range.
    """
    base = EVAL_DIR / benchmark
    if not base.is_dir():
        return []
    children = [c for c in base.iterdir() if c.is_dir()]
    for judge_dir in [c for c in children if c.name.startswith("_judge-")]:
        children += [c for c in judge_dir.iterdir() if c.is_dir()]

    runs: list[tuple[str, int, float]] = []
    for child in sorted(children, key=lambda p: p.name):
        if child.name.startswith("_") or DATE_DIR.match(child.name):
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
        value = _headline_of(summary, metric)
        if value is None:
            continue
        runs.append((str(summary.get("model") or child.name), int(summary.get("scored") or 0), value))
    if not runs:
        return []
    top = max(scored for _, scored, _ in runs)
    keep = [(m, v) for m, s, v in runs if s >= COVERAGE_FLOOR * top]
    return sorted(keep, key=lambda r: r[1], reverse=metric not in LOWER_IS_BETTER)


def task_buckets(benchmark: str) -> dict[str, dict[str, dict[str, Any]]]:
    """{model: {task: {total, accuracy}}} over comparable finished runs."""
    base = EVAL_DIR / benchmark
    if not base.is_dir():
        return {}
    out: dict[str, dict[str, dict[str, Any]]] = {}
    for child in sorted(base.iterdir(), key=lambda p: p.name):
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
        out[str(summary.get("model") or child.name)] = summary.get("by_bucket") or {}
    return out


# --------------------------------------------------------------------------
# per-task alignment
# --------------------------------------------------------------------------


def align_per_task(benchmark: str, spec: dict[str, Any]) -> dict[str, Any]:
    """Item-count-weighted human baseline over the tasks we actually ran.

    The paper's headline human number covers a different task mix than our run,
    so re-weighting by *our* item counts is the only comparable form. Tasks the
    paper has no human number for are dropped from both sides of the comparison,
    never zero-filled.
    """
    bucket_name = spec["bucket"]
    human = spec["values"]
    # Only AGIEval publishes a top-percentile row. Without it there is no "前 1%"
    # line to clear, and silently reusing the average as the ceiling would invent
    # a comparison the paper never made.
    has_top = all("top" in cell for cell in human.values())
    per_model: dict[str, Any] = {}
    per_task: dict[str, dict[str, Any]] = {}
    unknown_tasks: set[str] = set()

    for model, buckets in task_buckets(benchmark).items():
        tasks = (buckets or {}).get(bucket_name) or {}
        if not tasks:
            continue
        n_tot = h_avg = h_top = m_acc = 0.0
        for task, cell in tasks.items():
            if task not in human:
                if task not in spec.get("excluded", {}):
                    unknown_tasks.add(task)
                continue
            n = int(cell.get("total") or 0)
            acc = cell.get("accuracy")
            if not n or not isinstance(acc, (int, float)):
                continue
            n_tot += n
            h_avg += n * human[task]["avg"]
            h_top += n * human[task].get("top", 0.0)
            m_acc += n * float(acc)
            slot = per_task.setdefault(
                task, {"human_avg": human[task]["avg"], "human_top": human[task].get("top"), "models": {}}
            )
            slot["n"] = n
            slot["models"][model] = float(acc)
        if not n_tot:
            continue
        per_model[model] = {
            "n_items": int(n_tot),
            "human_avg_weighted": round(h_avg / n_tot, 4),
            "human_top_weighted": round(h_top / n_tot, 4) if has_top else None,
            "model_weighted": round(m_acc / n_tot, 4),
            "delta_vs_human_avg": round((m_acc - h_avg) / n_tot, 4),
            "beats_human_top": has_top and m_acc >= h_top,
        }
    return {
        "per_model": dict(sorted(per_model.items(), key=lambda kv: -kv[1]["model_weighted"])),
        "per_task": per_task,
        "unknown_tasks": sorted(unknown_tasks),
        "has_top": has_top,
    }


# --------------------------------------------------------------------------
# formatting
# --------------------------------------------------------------------------


def fmt(value: Any, digits: int = 4) -> str:
    if value is None:
        return "—"
    if isinstance(value, float):
        return f"{value:.{digits}f}".rstrip("0").rstrip(".")
    return str(value)


def fmt_range(rng: dict[str, Any]) -> str:
    if not rng or "min" not in rng:
        return "未跑"
    arrow = " ↓越低越好" if rng.get("lower_is_better") else ""
    return f"{fmt(rng['min'])} – {fmt(rng['max'])} ({rng['n_models']} 模型){arrow}"


def build(data: dict[str, Any]) -> str:
    lit = data["literature"]
    usability = data["usability_thresholds"]
    per_task_spec = data["per_task_human"]
    computed = (data.get("computed_from_local_data") or {}).get("results") or {}
    calib = (data.get("judge_calibration_vs_human_annotators") or {}).get("results") or {}
    self_built = data.get("no_external_human_reference") or {}

    out: list[str] = []
    w = out.append

    w("# Benchmark 人类参照锚与可用门槛")
    w("")
    w("> 由 `scripts/build_human_baseline_report.py` 生成，不要手改。")
    w("> 数据源：`data/benchmark_human_baselines_v1.json`、`reports/eval/`。")
    w("> 改结论要改 `scripts/build_human_baselines.py` 后重跑两个脚本。")
    w("> 地板那三层（随机 / 平凡策略 / 退化回复）在 `doc/benchmark_baselines_2026-08-04.md`，与本文互补。")
    w("")
    w("## 这份文档回答两个问题，它们不是一个数")
    w("")
    w("| | 问的是 | 怎么用 |")
    w("|---|---|---|")
    w("| **人类参照锚** | 人在这套题上能拿多少分 | 判断模型分是高是低的参照系 |")
    w("| **可用门槛** | 多少分算能上线 | 判断能不能交付的判定线 |")
    w("")
    w("两者经常不重合，而且**大多数 benchmark 只有其中一边**——这是事实不是遗漏。")
    w("人类分低于门槛（人自己也不达标）和模型超过人类但没到门槛，都是真实存在的情形，")
    w("表里分两列各自留空，不互相填补。")
    w("")
    w("分级沿用 `benchmark_human_baselines_v1.json` 的 A/B/C/D：A 同题同指标直接可比，")
    w("B 同 benchmark 但 split 或评分协议有差异，C 制度性代理或构造性上限，")
    w("D 只作语境（专用系统分、judge 可靠性）——D 永远不进人类分列。")
    w("")

    # ---------------- table A: human anchors ----------------
    w("## 表 A：人类参照锚")
    w("")
    w("`人类` 与 `实跑区间` 都在 `指标` 那一列的字段的原始标度上；**同一行内可比，跨行不可比**。")
    w("`指标` 留空表示就是 headline，填了说明人类数只存在于另一个字段上（这时实跑区间也换算到那个字段）。")
    w("")
    w("⚠ 带警告的行是**已知不可比**的对比，一句话读法位置直接放了阻断说明——")
    w("这些行的「模型 vs 人类」不要引用。")
    w("")
    w("| benchmark | headline | 人类 | 级别 | 指标 | 实跑区间 | 一句话读法 |")
    w("|---|---|---|---|---|---|---|")
    rows_a = []
    for name, entry in sorted(lit.items()):
        human = entry.get("human") or {}
        headline = entry.get("headline", "—")
        metric = human.get("metric") or headline
        rng = observed_range(name, metric)
        value = human.get("value")
        rows_a.append((name, headline, value, human.get("grade"), metric, headline, rng, human))
    # entries with a number first — those are the ones anyone actually reads
    rows_a.sort(key=lambda r: (r[2] is None, r[0]))
    for name, headline, value, grade, metric, hl, rng, human in rows_a:
        metric_cell = "—" if metric == hl else f"`{metric}`"
        if human.get("reading_blocked"):
            # An entry whose comparison is known-invalid must never print a
            # "model beats human" one-liner — that is exactly how a retracted
            # conclusion gets laundered back into a report.
            reading = human["reading_blocked"]
        elif value is None:
            reading = "无人类数据（理由见「查过但确实没有」）"
        elif rng and "min" in rng:
            best = rng["best"]
            if metric in LOWER_IS_BETTER:
                reading = "见备注"
            elif best >= value:
                reading = f"最好模型 {fmt(best)} 已超过人类"
            else:
                reading = f"最好模型 {fmt(best)} 仍低于人类"
        else:
            reading = "该指标尚无可比 run"
        w(
            f"| `{name}` | `{headline}` | {fmt(value)} | {grade or '—'} | {metric_cell} "
            f"| {fmt_range(rng)} | {reading} |"
        )
    w("")

    # ---------------- table B: usability ----------------
    w("## 表 B：可用门槛")
    w("")
    w("`门槛` 落在 `指标` 那一列的字段上，**不一定是 headline**——判分类任务的可用性由一致性决定，")
    w("不由 macro-F1 决定，所以门槛压在 kappa 上。`达标` 数的是通过门槛的模型数 / 可比 run 总数。")
    w("")
    w("| benchmark | 类型 | 指标 | 门槛 | 人类上限 | 实跑区间 | 达标 |")
    w("|---|---|---|---|---|---|---|")
    verdicts: dict[str, dict[str, Any]] = {}
    for name, entry in sorted(usability.items(), key=lambda kv: (kv[1].get("value") is None, kv[0])):
        metric = entry.get("metric") or (lit.get(name, {}).get("headline") or "—")
        value = entry.get("value")
        scale = float(entry.get("scale") or 1.0)
        runs = run_values(name, metric) if metric != "—" else []
        rng = observed_range(name, metric) if metric != "—" else {}
        if value is None:
            pass_cell = "—"
        elif not runs:
            pass_cell = "未跑"
        else:
            line = value * scale
            lower_better = metric in LOWER_IS_BETTER
            ok = [m for m, v in runs if (v <= line if lower_better else v >= line)]
            pass_cell = f"**{len(ok)}/{len(runs)}**"
            verdicts[name] = {"line": line, "passed": ok, "runs": runs, "metric": metric}
        ceiling = entry.get("human_ceiling")
        thr = "—" if value is None else fmt(value * scale)
        w(
            f"| `{name}` | {KIND_LABEL.get(entry.get('kind'), entry.get('kind'))} | `{metric}` "
            f"| {thr} | {fmt(ceiling)} | {fmt_range(rng)} | {pass_cell} |"
        )
    w("")

    # spell out the ones that fail, since that is the actionable half
    failing = [(n, v) for n, v in verdicts.items() if len(v["passed"]) < len(v["runs"])]
    if failing:
        w("### 没过门槛的")
        w("")
        for name, v in sorted(failing, key=lambda kv: len(kv[1]["passed"])):
            miss = [(m, val) for m, val in v["runs"] if m not in v["passed"]]
            w(f"**`{name}`**（门槛 {fmt(v['line'])} on `{v['metric']}`）—— {len(miss)}/{len(v['runs'])} 未达标：")
            for model, val in miss[:12]:
                w(f"- {model}: {fmt(val)}")
            if len(miss) > 12:
                w(f"- …… 另有 {len(miss) - 12} 个")
            w("")

    # ---------------- per-task ----------------
    w("## 逐任务对齐：把论文的人类分按我们的题数重算")
    w("")
    w("论文的人类总分覆盖的任务组合和我们跑的不一样，直接并列会误读。")
    w("下面按**我们自己的题数**给每个任务的人类分加权，论文没有人类分的任务从两边同时剔除，绝不补零。")
    w("")
    for name, spec in sorted(per_task_spec.items()):
        aligned = align_per_task(name, spec)
        if not aligned["per_model"]:
            continue
        w(f"### `{name}`")
        w("")
        w(f"人类来源：{spec['source']}；受试人群：{spec['population']}")
        w("")
        for task, why in (spec.get("excluded") or {}).items():
            w(f"- 剔除 `{task}`：{why}")
        if aligned["unknown_tasks"]:
            w(f"- ⚠ 有任务既不在人类表也不在剔除表里，join 漏了：{aligned['unknown_tasks']}")
        for caveat in spec.get("caveats") or []:
            w(f"- ⚠ {caveat}")
        w("")
        w("| 模型 | 对齐题数 | 人类均分(加权) | 人类前1%(加权) | 模型同题 | 差值 |")
        w("|---|---|---|---|---|---|")
        for model, cell in aligned["per_model"].items():
            mark = " ✅" if cell["beats_human_top"] else ""
            w(
                f"| {model} | {cell['n_items']} | {fmt(cell['human_avg_weighted'])} "
                f"| {fmt(cell['human_top_weighted'])} | {fmt(cell['model_weighted'])}{mark} "
                f"| {cell['delta_vs_human_avg']:+.4f} |"
            )
        w("")
        if aligned["has_top"]:
            w("✅ = 加权后已超过前 1% 考生线。")
        else:
            w("论文没给这个 benchmark 的前 1% 档，该列留空——不拿均分冒充上限。")
        w("")
        # Cross-check: the re-weighted average should land near the paper's own
        # published overall human number. A large drift means the per-task table
        # and the headline number are not describing the same thing.
        published = ((lit.get(name) or {}).get("human") or {}).get("value")
        sample = next(iter(aligned["per_model"].values()), None)
        if published is not None and sample is not None:
            drift = sample["human_avg_weighted"] - published
            w(
                f"> 交叉校验：按我们题数重算得 {fmt(sample['human_avg_weighted'])}，"
                f"论文自报总人类分 {fmt(published)}，差 {drift:+.4f}。"
            )
            w("> 差值来自题数分布与论文四舍五入，量级正常即说明逐任务表与总分是同一回事。")
            w("")
        # per-task detail: where models still lose to an ordinary human
        losers = []
        for task, cell in sorted(aligned["per_task"].items()):
            below = {m: v for m, v in cell["models"].items() if v < cell["human_avg"]}
            if below:
                losers.append((task, cell, below))
        if losers:
            w(f"**仍有模型低于普通人类的任务**（{len(losers)}/{len(aligned['per_task'])}）：")
            w("")
            w("| 任务 | 题数 | 人类均分 | 低于人类的模型 |")
            w("|---|---|---|---|")
            for task, cell, below in sorted(losers, key=lambda r: -len(r[2])):
                listed = ", ".join(f"{m} {fmt(v, 3)}" for m, v in sorted(below.items(), key=lambda kv: kv[1]))
                w(f"| `{task}` | {cell['n']} | {fmt(cell['human_avg'])} | {listed} |")
            w("")
        unjoined = spec.get("unjoined_reference")
        if unjoined:
            w(f"> 还没接上的细粒度：{unjoined['note']}")
            w(">")
            w("> " + "；".join(f"{k} {v}" for k, v in unjoined["by_skill"].items()))
            w("")

    # ---------------- same-pipeline human ----------------
    w("## 同管线复评：人类专家的回复过我们自己的 judge")
    w("")
    w("这是全套里最干净的一类人类锚——同题、同指标、同 judge，唯一的变量就是回复出自人还是模型。")
    w("目前只有两个 benchmark 的数据集自带人类教师回复，都已经跑过。")
    w("")
    if calib:
        w("| benchmark | 题数 | judge | 人类标注者判专家 | 我们的 judge 判同一批专家 | 差 |")
        w("|---|---|---|---|---|---|")
        for name, cell in sorted(calib.items()):
            hp, jp = cell.get("human_annotator_pass_rate"), cell.get("our_judge_pass_rate")
            gap = None if hp is None or jp is None else jp - hp
            w(
                f"| `{name}` | {cell.get('n_items')} | {cell.get('judge_model')} "
                f"| {fmt(hp)} | {fmt(jp)} | {fmt(gap)} |"
            )
        w("")
    # Quote the live model range rather than a hardcoded one — this paragraph is
    # the retraction notice, and a stale number in it undermines the point.
    model_span = []
    for name in sorted(calib):
        rng = observed_range(name, lit.get(name, {}).get("headline", "extra:pass_rate"))
        if rng and "min" in rng:
            model_span.append(f"`{name}` {fmt(rng['min'])}–{fmt(rng['max'])}")
    w("⚠ **这两个数现在还不能当人类基线用。** 同一批专家教师回复，人类标注者判下来通过率")
    w("0.52–0.61，我们的 judge 判下来只有 0.16" + ("，而模型拿到 " + "、".join(model_span) if model_span else "") + "。")
    w("原因是 harness 缺陷：我们给被测模型的 prompt 把 judge 要打的维度逐条列出来了，")
    w("模型照着清单写，人类教师没有这份清单（详见 `doc/benchmark_baselines_2026-08-04.md` 末节）。")
    w("**修掉泄题之前，任何「模型超过人类专家」的结论都不成立。**")
    w("")
    if computed:
        w("数据集自带标注（人类标注者口径，不经我们的 judge）：")
        w("")
        w("| benchmark | 角色 | n | pass_rate |")
        w("|---|---|---|---|")
        for name, tutors in sorted(computed.items()):
            for role, cell in tutors.items():
                w(f"| `{name}` | {role} | {cell['n']} | {fmt(cell['pass_rate'])} |")
        w("")

    # ---------------- honest blanks ----------------
    w("## 查过但确实没有")
    w("")
    w("这一节存在的意义是**别再查第二遍**。每条都写清查了哪篇、结论是什么。")
    w("")
    no_human = [(n, e) for n, e in sorted(lit.items()) if (e.get("human") or {}).get("value") is None]
    for name, entry in no_human:
        human = entry.get("human") or {}
        w(f"**`{name}`** — {human.get('source')}")
        w("")
        w(f"{human.get('note')}")
        w("")
        for anchor in entry.get("context_anchors") or []:
            w(f"- 语境锚（grade D，不是人类分）·{anchor['label']}：{fmt(anchor.get('value'))} — {anchor['note']}")
        w("")
    w("### 自建题集 / 无外部人类参照")
    w("")
    for name, why in sorted(self_built.items()):
        w(f"- **`{name}`** — {why}")
    w("")

    # ---------------- next steps ----------------
    w("## 还能补的（按成本从低到高）")
    w("")
    w("1. **mathtutorbench 新手教师锚**（零 API 额外数据，只花一次判分）——")
    w("   `pref_test.jsonl` 每条都带 `teacher_response_negative`，即新手教师原话。")
    w("   拿它当被测回复跑一遍，就能给 scaffolding / pedagogy 的 win_rate 补一个人类下锚。")
    w("   现在这四个任务只有 0.5 这个「与专家打平」的上锚，多数模型跌破它，")
    w("   但「跌破多少算差」没有参照——补上新手线就能说清是相当于新手还是不如新手。")
    w("2. **mathvista 技能维度 bucket**（不花 API）—— 给 adapter 加一个 skills bucket 后 `--score-only`")
    w("   重跑打分，就能接上论文的 7 类技能人类分（ALG 50.9 / LOG 40.7 等）。")
    w("3. **修 mrbench / bea2025 的 prompt 泄题**——这是解锁「同管线人类锚」这条路的前提，")
    w("   不修的话已经跑出来的 expert / novice 复评值都用不了。")
    w("4. **自建人类小样本**（要花钱，兜底方案，未启动）—— 只在精选题集上做。")
    w("   这是唯一能补 `ceval` / `mmlu_pro` / `olympiadbench` / `sas_bench` 这几格的办法，")
    w("   其余路线对它们全部无效。")
    w("")
    return "\n".join(out) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, default=OUT_PATH)
    args = ap.parse_args()

    data = json.loads(HUMAN_PATH.read_text(encoding="utf-8"))
    text = build(data)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}  ({len(text.splitlines())} 行)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
