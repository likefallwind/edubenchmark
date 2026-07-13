#!/usr/bin/env python3
"""Aggregate EduIllustrate (arXiv 2604.05005) generation + judge outputs into an
edubenchmark per-benchmark eval report.

EduIllustrate is a *generative multimodal* benchmark run from the upstream repo
(cloned at ``--source-repo``, default ``/home/likefallwind/code/EduIllustrate``),
NOT from edubenchmark's lean ``scripts/eval/`` adapter harness — its dependency
stack (manim + texlive) is too heavy to inline. This script only rolls the final
8-dimension judge scores back into the standard
``reports/eval/<benchmark>/<model-slug>/`` layout (summary.json / scored.jsonl /
report.html) so the result lands in the same place as every other eval.

Scoring recap (faithful to the paper): each rendered solution is judged on 8
dimensions (4 text + 4 visual) on a 0–5 Likert scale; the per-problem
``overall_score`` is the *geometric mean* of the 8. A problem that fails to
render (model emitted unrenderable Manim code) is a benchmark failure.

IMPORTANT: the judge here is a substitute provider (MiniMax-M3), NOT the paper's
Gemini 3.0 Pro — so these scores are for *internal comparison only*, not
leaderboard-comparable. This caveat is recorded in summary.json and the HTML.
"""
import argparse
import datetime as _dt
import glob
import html
import json
import math
import os

DIMS = [
    ("correctness_and_completeness", "解题步骤的正确性和完整性", "text"),
    ("logical_coherence", "讲解的逻辑连贯性", "text"),
    ("understandability_and_teaching_effect", "讲解的易懂性和教学效果", "text"),
    ("text_diagram_synergy", "图文协同的流畅性", "text"),
    ("diagram_match", "图示与题目的匹配度", "visual"),
    ("layout_and_visual_clarity", "排版和视觉呈现的清晰度", "visual"),
    ("element_layout_quality", "图片元素布局质量", "visual"),
    ("visual_consistency", "视觉一致性", "visual"),
]
DIM_KEYS = [d[0] for d in DIMS]
DIM_NAME = {d[0]: d[1] for d in DIMS}


def _mean(xs):
    xs = [x for x in xs if x is not None]
    return (sum(xs) / len(xs)) if xs else None


def _geomean(xs):
    xs = [x for x in xs if x is not None and x > 0]
    if not xs:
        return 0.0
    return math.exp(sum(math.log(x) for x in xs) / len(xs))


def load_problems(source_repo, eval_dir, data_path):
    meta = {}
    if os.path.exists(data_path):
        for i, p in enumerate(json.load(open(data_path, encoding="utf-8"))):
            meta[i] = p
    rows = []
    for f in sorted(glob.glob(os.path.join(source_repo, eval_dir, "evaluation_problem*.json"))):
        d = json.load(open(f, encoding="utf-8"))
        base = os.path.basename(f)
        pid = base.split("evaluation_", 1)[1].rsplit("_2026", 1)[0]
        idx = int(pid.split("_")[1])
        ev = d.get("evaluation", {})
        scores = {k: ev.get(k, {}).get("score") for k in DIM_KEYS}
        details = {k: d.get("dimension_details", {}).get(k, {}) for k in DIM_KEYS}
        m = meta.get(idx, {})
        rows.append({
            "item_id": pid,
            "index": idx,
            "hash_id": m.get("hash_id"),
            "subject": m.get("subject"),
            "difficulty": m.get("difficulty"),
            "type": m.get("type"),
            "knowledge_point": m.get("knowledge_point"),
            "scores": scores,
            "overall_score": ev.get("overall_score", {}).get("score"),
            "rendering_failed": bool(d.get("rendering_failed")),
            "justifications": {k: details[k].get("justification") for k in DIM_KEYS},
            "status": "judged",
        })
    return rows, meta


def add_failures(rows, meta, source_repo, gen_dir):
    """Append problems that have NO judged result (full render failure)."""
    judged = {r["index"] for r in rows}
    for idx, m in meta.items():
        if idx in judged:
            continue
        pid = f"problem_{idx}_{m.get('subject','').replace('-', '_')}" if m.get("subject") else f"problem_{idx}"
        # locate the actual dir name on disk
        cand = glob.glob(os.path.join(source_repo, gen_dir, f"problem_{idx}_*"))
        pid = os.path.basename(cand[0]) if cand else pid
        sol = cand and os.path.exists(os.path.join(cand[0], "doc", "solution.md"))
        rows.append({
            "item_id": pid,
            "index": idx,
            "hash_id": m.get("hash_id"),
            "subject": m.get("subject"),
            "difficulty": m.get("difficulty"),
            "type": m.get("type"),
            "knowledge_point": m.get("knowledge_point"),
            "scores": {k: None for k in DIM_KEYS},
            "overall_score": 0.0,            # render failure scores 0
            "rendering_failed": True,
            "justifications": {},
            "status": "solution_present_but_unjudged" if sol else "render_failure",
        })
    rows.sort(key=lambda r: r["index"])
    return rows


def build_summary(rows, args):
    judged = [r for r in rows if r["status"] == "judged"]
    n_total = len(rows)
    n_judged = len(judged)
    n_fail = sum(1 for r in rows if r["status"] == "render_failure")

    per_dim_mean = {k: _mean([r["scores"][k] for r in judged]) for k in DIM_KEYS}
    overall_mean_judged = _mean([r["overall_score"] for r in judged])
    # all-items view: failures count as 0 (faithful to "failed render = failure")
    overall_mean_all = _mean([r["overall_score"] for r in rows])

    def bucket(field):
        out = {}
        for r in rows:
            key = r.get(field)
            if isinstance(key, list):
                key = ";".join(map(str, key))
            key = key or "unknown"
            b = out.setdefault(key, {"total": 0, "judged": 0, "overall_mean_all": []})
            b["total"] += 1
            if r["status"] == "judged":
                b["judged"] += 1
            b["overall_mean_all"].append(r["overall_score"])
        for k, b in out.items():
            b["overall_mean_all"] = round(_mean(b["overall_mean_all"]) or 0.0, 4)
        return out

    return {
        "benchmark": "eduillustrate",
        "benchmark_paper": "arXiv:2604.05005",
        "capability": "D06/D11 (multimodal STEM diagram generation + explanation)",
        "model": args.model,
        "judge_model": args.judge_model,
        "judge_is_substitute": True,
        "judge_note": (
            f"判官为替代 provider({args.judge_model}),非论文原用 Gemini 3.0 Pro;"
            "分数仅供内部对比,不可与论文 leaderboard 直接比较。"),
        "generation_concurrency": args.concurrency,
        "scoring": "8-dim 0-5 Likert, per-problem geometric mean; benchmark-level = arithmetic mean over problems",
        "total_items": n_total,
        "judged": n_judged,
        "render_failures": n_fail,
        "overall_mean_judged_only": round(overall_mean_judged or 0.0, 4),
        "overall_mean_all_items": round(overall_mean_all or 0.0, 4),
        "per_dimension_mean_judged": {k: (round(v, 4) if v is not None else None) for k, v in per_dim_mean.items()},
        "by_bucket": {
            "difficulty": bucket("difficulty"),
            "type": bucket("type"),
            "subject": bucket("subject"),
        },
        "run_notes": args.run_notes,
        "source_repo": args.source_repo,
        "generated_at": _dt.datetime.now().isoformat(timespec="seconds"),
    }


def render_html(summary, rows):
    def esc(x):
        return html.escape(str(x)) if x is not None else ""

    def score_cell(v):
        if v is None:
            return '<td class="na">—</td>'
        c = "good" if v >= 4 else ("mid" if v >= 3 else "bad")
        return f'<td class="{c}">{v:.2f}</td>'

    dim_head = "".join(f"<th>{esc(DIM_NAME[k])}</th>" for k in DIM_KEYS)
    body_rows = []
    for r in rows:
        cells = "".join(score_cell(r["scores"].get(k)) for k in DIM_KEYS)
        ov = r["overall_score"]
        ovc = "good" if (ov and ov >= 4) else ("mid" if (ov and ov >= 3) else "bad")
        status = {"judged": "已评分",
                  "render_failure": "渲染失败",
                  "solution_present_but_unjudged": "有解未评"}.get(r["status"], r["status"])
        body_rows.append(
            f"<tr><td>{esc(r['item_id'])}</td><td>{esc(r['difficulty'])}</td>"
            f"<td>{esc(r['type'])}</td>{cells}"
            f'<td class="{ovc}"><b>{ov:.3f}</b></td><td>{esc(status)}</td></tr>')

    pdm = summary["per_dimension_mean_judged"]
    dim_means = "".join(
        f"<tr><td>{esc(DIM_NAME[k])}</td><td>{esc(t)}</td>"
        f"<td>{('%.3f' % pdm[k]) if pdm[k] is not None else '—'}</td></tr>"
        for k, t in [(d[0], d[2]) for d in DIMS])

    return f"""<!doctype html><html lang="zh"><head><meta charset="utf-8">
<title>EduIllustrate × {esc(summary['model'])} — 评测报告</title>
<style>
body{{font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;margin:2rem auto;max-width:1100px;color:#1a1a1a;line-height:1.5}}
h1{{font-size:1.5rem}} h2{{font-size:1.15rem;margin-top:1.8rem;border-bottom:2px solid #eee;padding-bottom:.3rem}}
table{{border-collapse:collapse;width:100%;margin:.6rem 0;font-size:.9rem}}
th,td{{border:1px solid #ddd;padding:.35rem .5rem;text-align:center}}
th{{background:#f6f8fa}} td:first-child,th:first-child{{text-align:left}}
.good{{background:#e6f4ea;color:#137333}} .mid{{background:#fef7e0;color:#a36a00}} .bad{{background:#fce8e6;color:#c5221f}}
.na{{color:#aaa}}
.kpi{{display:inline-block;border:1px solid #ddd;border-radius:8px;padding:.6rem 1rem;margin:.3rem .5rem .3rem 0;min-width:8rem}}
.kpi b{{display:block;font-size:1.6rem}}
.warn{{background:#fff4e5;border:1px solid #ffcc80;border-radius:8px;padding:.7rem 1rem;margin:1rem 0}}
small{{color:#666}}
</style></head><body>
<h1>EduIllustrate（arXiv:2604.05005）评测报告</h1>
<p><b>生成模型</b>：{esc(summary['model'])} ｜ <b>判官</b>：{esc(summary['judge_model'])}（替代，非原论文 Gemini 3.0 Pro）｜
<b>生成并发</b>：{esc(summary['generation_concurrency'])} ｜ 生成时间：{esc(summary['generated_at'])}</p>
<div class="warn">⚠️ <b>分数仅供内部对比</b>：{esc(summary['judge_note'])}</div>

<h2>总览</h2>
<div>
<span class="kpi">题目数<b>{summary['total_items']}</b></span>
<span class="kpi">已评分<b>{summary['judged']}</b></span>
<span class="kpi">渲染失败<b>{summary['render_failures']}</b></span>
<span class="kpi">综合分（已评）<b>{summary['overall_mean_judged_only']:.3f}</b><small>仅成功渲染题</small></span>
<span class="kpi">综合分（全部）<b>{summary['overall_mean_all_items']:.3f}</b><small>失败计 0</small></span>
</div>
<p><small>综合分 = 每题 8 维几何均值，再对题目取算术平均。0–5 分制。</small></p>

<h2>各维度均分（仅成功渲染题）</h2>
<table><tr><th>维度</th><th>类别</th><th>均分</th></tr>{dim_means}</table>

<h2>逐题明细</h2>
<table><tr><th>题目</th><th>难度</th><th>题型</th>{dim_head}<th>综合</th><th>状态</th></tr>
{''.join(body_rows)}</table>
<p><small>列顺序：文本维度（正确性 / 逻辑 / 易懂 / 图文协同）→ 视觉维度（图题匹配 / 排版 / 元素布局 / 视觉一致）。</small></p>

<h2>运行说明</h2>
<ul>{''.join(f'<li>{esc(n)}</li>' for n in summary['run_notes'])}</ul>
<p><small>数据来源：{esc(summary['source_repo'])}（上游 EduIllustrate 仓库，单独运行；本报告仅回收最终分数）。</small></p>
</body></html>"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-repo", default="/home/likefallwind/code/EduIllustrate")
    ap.add_argument("--eval-dir", default="output/smoke_c3_eval")
    ap.add_argument("--gen-dir", default="output/smoke_c3")
    ap.add_argument("--data-path", default="/home/likefallwind/code/EduIllustrate/data/benchmark/smoke5.json")
    ap.add_argument("--model", default="MiniMax-M3")
    ap.add_argument("--judge-model", default="MiniMax-M3")
    ap.add_argument("--concurrency", default="unspecified")
    ap.add_argument("--run-note", action="append", dest="run_notes", default=None,
                    help="本次运行的注记,可重复传;不传则留空。")
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "..", "..",
                                                  "reports", "eval", "eduillustrate", "minimax3"))
    args = ap.parse_args()
    args.run_notes = args.run_notes or []

    rows, meta = load_problems(args.source_repo, args.eval_dir, args.data_path)
    rows = add_failures(rows, meta, args.source_repo, args.gen_dir)
    summary = build_summary(rows, args)

    out = os.path.abspath(args.out)
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    with open(os.path.join(out, "scored.jsonl"), "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with open(os.path.join(out, "report.html"), "w", encoding="utf-8") as f:
        f.write(render_html(summary, rows))
    print(f"wrote summary.json / scored.jsonl / report.html -> {out}")
    print(f"  total={summary['total_items']} judged={summary['judged']} "
          f"fail={summary['render_failures']} "
          f"overall(judged)={summary['overall_mean_judged_only']} "
          f"overall(all)={summary['overall_mean_all_items']}")


if __name__ == "__main__":
    main()
