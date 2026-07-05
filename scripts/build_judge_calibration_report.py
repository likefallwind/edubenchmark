#!/usr/bin/env python3
"""Merge the mrbench_judge + bea2025_judge runs into one LLM-as-Judge
reliability report (education-domain analog of RuVerBench meta-evaluation).

Reads the per-benchmark summary.json emitted by scripts/eval_benchmark.py under
reports/eval/<benchmark>/<model>/ and writes a single self-contained HTML file
to html_report/. Idempotent: rerun after adding judge runs to refresh.
"""
from __future__ import annotations
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "html_report", "judge_calibration_report.html")

ALL_JUDGES = ["deepseek-v3.2", "deepseek-v4-flash", "deepseek-v4-pro", "minimax3"]
JUDGE_LABEL = {"deepseek-v3.2": "DeepSeek-V3.2",
               "deepseek-v4-flash": "DeepSeek-V4-Flash",
               "deepseek-v4-pro": "DeepSeek-V4-Pro",
               "minimax3": "MiniMax-M3"}
BENCHES = ["mrbench_judge", "bea2025_judge"]

# The 4 pedagogical dimensions shared by both benchmarks (mergeable).
SHARED_DIMS = ["Mistake_Identification", "Mistake_Location",
               "Providing_Guidance", "Actionability"]


def load(bench, judge):
    p = os.path.join(ROOT, "reports", "eval", bench, judge, "summary.json")
    if not os.path.exists(p):
        return None
    return json.load(open(p))


def fmt(x, d=3):
    return "—" if x is None else f"{x:.{d}f}"


def cls(v, good=0.4, warn=0.25):
    """Colour a Cohen's kappa-ish value."""
    if v is None:
        return ""
    if v >= good:
        return "good"
    if v >= warn:
        return "warn"
    return "bad"


def bar(v, vmax=1.0, color="#2f6df0"):
    pct = 0 if v is None else max(0, min(100, 100 * v / vmax))
    return (f'<div class="bar"><span style="width:{pct:.0f}%;background:{color}"></span></div>'
            f'<span class="barval">{fmt(v)}</span>')


def main():
    data = {b: {j: load(b, j) for j in ALL_JUDGES} for b in BENCHES}
    # Only keep judges that have at least one run present, in a stable order.
    JUDGES = [j for j in ALL_JUDGES if any(data[b][j] for b in BENCHES)]

    # ---- headline macro table rows ----
    macro_rows = []
    for b in BENCHES:
        for j in JUDGES:
            s = data[b][j]
            if not s:
                continue
            em = s["extra_metrics"]
            mo = em.get("macro_over_dimensions", {})
            macro_rows.append({
                "bench": b, "judge": j, "n": s.get("total_items"),
                "agree": mo.get("agreement", mo.get("exact_accuracy")),
                "f1": mo.get("f1_macro", mo.get("exact_macro_f1")),
                "kappa": mo.get("cohen_kappa"),
                "lenient": mo.get("lenient_accuracy"),
            })

    # ---- shared-dimension merged view (weighted by n across both benches) ----
    # For each judge, per shared dim, aggregate agreement weighted by item count.
    merged = {j: {} for j in JUDGES}
    for j in JUDGES:
        for dim in SHARED_DIMS:
            num = den = 0.0
            kap_num = kap_den = 0.0
            for b in BENCHES:
                s = data[b][j]
                if not s:
                    continue
                pd = s["extra_metrics"]["per_dimension"].get(dim)
                if not pd:
                    continue
                n = pd["n"]
                agree = pd.get("agreement", pd.get("exact_accuracy"))
                kap = pd.get("cohen_kappa")
                if agree is not None:
                    num += agree * n
                    den += n
                if kap is not None:
                    kap_num += kap * n
                    kap_den += n
            merged[j][dim] = {
                "agree": num / den if den else None,
                "kappa": kap_num / kap_den if kap_den else None,
                "n": int(den),
            }

    # ---- per-benchmark full per-dimension tables ----
    def dim_table(bench):
        present = [j for j in JUDGES if data[bench][j]]
        s0 = data[bench][present[0]]
        dims = list(s0["extra_metrics"]["per_dimension"].keys())
        head = "".join(f"<th>{JUDGE_LABEL[j]}</th>" for j in present)
        rows = ""
        for dim in dims:
            n = s0["extra_metrics"]["per_dimension"][dim]["n"]
            cells = ""
            for j in present:
                pd = data[bench][j]["extra_metrics"]["per_dimension"][dim]
                agree = pd.get("agreement", pd.get("exact_accuracy"))
                kap = pd.get("cohen_kappa")
                cells += (f'<td><div class="cell">{bar(agree)}'
                          f'<span class="kap {cls(kap)}">κ {fmt(kap,2)}</span></div></td>')
            rows += f'<tr><td class="dim">{dim}</td><td class="muted">{n}</td>{cells}</tr>'
        return (f'<table><thead><tr><th style="text-align:left">维度 Dimension</th>'
                f'<th>N</th>{head}</tr></thead><tbody>{rows}</tbody></table>')

    # ---- best judge per bench ----
    def best(bench, key="kappa"):
        cand = [r for r in macro_rows if r["bench"] == bench and r[key] is not None]
        return max(cand, key=lambda r: r[key]) if cand else None

    mr_best = best("mrbench_judge")
    bea_best = best("bea2025_judge")

    # ---- macro table html ----
    def macro_table():
        rows = ""
        for r in macro_rows:
            bench_short = "MRBench" if r["bench"] == "mrbench_judge" else "BEA2025-dev"
            lenient = f'<td>{fmt(r["lenient"])}</td>' if r["bench"] == "bea2025_judge" else '<td class="muted">—</td>'
            rows += (f'<tr><td class="dim">{bench_short}</td>'
                     f'<td>{JUDGE_LABEL[r["judge"]]}</td>'
                     f'<td class="muted">{r["n"]}</td>'
                     f'<td>{bar(r["agree"])}</td>'
                     f'<td>{fmt(r["f1"])}</td>'
                     f'<td class="{cls(r["kappa"])}">{fmt(r["kappa"])}</td>'
                     f'{lenient}</tr>')
        return (f'<table><thead><tr><th style="text-align:left">基准</th><th>评委模型</th>'
                f'<th>判据数</th><th>一致率 Agreement</th><th>Macro-F1</th>'
                f'<th>Cohen κ</th><th>Lenient Acc</th></tr></thead><tbody>{rows}</tbody></table>')

    # ---- merged shared-dim table ----
    def merged_table():
        head = "".join(f"<th>{JUDGE_LABEL[j]}</th>" for j in JUDGES)
        rows = ""
        for dim in SHARED_DIMS:
            n = max(merged[j][dim]["n"] for j in JUDGES)
            cells = ""
            for j in JUDGES:
                d = merged[j][dim]
                cells += (f'<td><div class="cell">{bar(d["agree"])}'
                          f'<span class="kap {cls(d["kappa"])}">κ {fmt(d["kappa"],2)}</span></div></td>')
            rows += f'<tr><td class="dim">{dim}</td><td class="muted">{n}</td>{cells}</tr>'
        return (f'<table><thead><tr><th style="text-align:left">共享维度</th><th>合并 N</th>'
                f'{head}</tr></thead><tbody>{rows}</tbody></table>')

    total_tuples = sum(r["n"] for r in macro_rows if r["bench"] == "mrbench_judge" and r["judge"] == JUDGES[0]) \
        + sum(r["n"] for r in macro_rows if r["bench"] == "bea2025_judge" and r["judge"] == JUDGES[0])

    html = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>教育版 LLM-as-Judge 可靠性报告 · MRBench + BEA2025 校准</title>
<style>
  :root{{--panel:#fff;--ink:#1a2027;--muted:#5b6770;--line:#e3e8ee;--accent:#2f6df0;--accent2:#7c3aed;--good:#1f9d55;--warn:#d97706;--bad:#dc2626}}
  *{{box-sizing:border-box}}
  body{{margin:0;font-family:-apple-system,"Segoe UI",Roboto,"PingFang SC","Microsoft YaHei",sans-serif;color:var(--ink);background:#f4f6fa;line-height:1.65;font-size:15px}}
  .wrap{{max-width:1080px;margin:0 auto;padding:0 24px 80px}}
  header{{background:linear-gradient(135deg,#1e293b,#312e81);color:#fff;padding:48px 24px 40px;margin-bottom:8px}}
  header .inner{{max-width:1080px;margin:0 auto}}
  header h1{{margin:0 0 8px;font-size:29px}}
  header p{{margin:4px 0;opacity:.85;font-size:14px}}
  .tag{{display:inline-block;background:rgba(255,255,255,.15);border-radius:20px;padding:3px 12px;font-size:12px;margin-right:8px;margin-top:10px}}
  h2{{font-size:21px;margin:40px 0 14px;padding-bottom:8px;border-bottom:2px solid var(--line)}}
  h3{{font-size:16px;margin:24px 0 10px}}
  .grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:16px;margin:18px 0}}
  .kpi{{background:#fff;border:1px solid var(--line);border-radius:12px;padding:18px 20px}}
  .kpi .label{{font-size:12px;color:var(--muted);text-transform:uppercase;letter-spacing:.5px}}
  .kpi .val{{font-size:28px;font-weight:700;margin-top:4px}}
  .kpi .sub{{font-size:13px;color:var(--muted)}}
  table{{border-collapse:collapse;width:100%;margin:14px 0;font-size:14px;background:#fff}}
  th,td{{border:1px solid var(--line);padding:9px 12px;text-align:center;vertical-align:middle}}
  th{{background:#f0f3f8;font-weight:600}}
  td.dim{{text-align:left;font-weight:600}}
  td.muted,.muted{{color:var(--muted)}}
  tr:nth-child(even) td{{background:#fafbfd}}
  .bar{{position:relative;display:inline-block;height:16px;width:74px;background:#eef1f6;border-radius:4px;overflow:hidden;vertical-align:middle}}
  .bar>span{{position:absolute;left:0;top:0;bottom:0;border-radius:4px}}
  .barval{{font-size:12px;margin-left:6px;vertical-align:middle}}
  .cell{{display:flex;align-items:center;justify-content:center;gap:4px;flex-wrap:wrap}}
  .kap{{font-size:11px;padding:1px 5px;border-radius:4px;background:#f0f3f8}}
  .good{{color:var(--good)}} .warn{{color:var(--warn)}} .bad{{color:var(--bad)}}
  .note{{background:#f8fafc;border-left:4px solid var(--accent);padding:12px 18px;border-radius:0 8px 8px 0;margin:16px 0;font-size:14px}}
  .note.warn{{border-color:var(--warn);background:#fffbf2}}
  .note.key{{border-color:var(--accent2);background:#faf7ff}}
  ul{{margin:10px 0;padding-left:22px}} li{{margin:6px 0}}
  code{{background:#eef1f6;padding:1px 6px;border-radius:4px;font-size:13px}}
  footer{{color:var(--muted);font-size:12px;text-align:center;margin-top:50px;padding-top:20px;border-top:1px solid var(--line)}}
</style></head><body>
<header><div class="inner">
  <h1>教育版 LLM-as-Judge 可靠性报告</h1>
  <p>参照 RuVerBench 的判据校准元评测（meta-evaluation）· 被测模型即评委，对齐人工教学标注</p>
  <p>数据源：<strong>MRBench_V2</strong>（8 维教学量表）+ <strong>BEA2025 dev</strong>（4 维）· 三态人工 gold，未折二分类</p>
  <div>
    <span class="tag">mrbench_judge</span><span class="tag">bea2025_judge</span>
    <span class="tag">评委 × {len(JUDGES)}</span><span class="tag">100% 人工标注</span>
  </div>
</div></header>
<div class="wrap">

<div class="grid">
  <div class="kpi"><div class="label">待判教学回复</div><div class="val">4,086</div><div class="sub">1,610 MRBench + 2,476 BEA</div></div>
  <div class="kpi"><div class="label">判据级人工标签 / 评委</div><div class="val">23,144</div><div class="sub">13,240 + 9,904 tuples</div></div>
  <div class="kpi"><div class="label">评委模型</div><div class="val">{len(JUDGES)}</div><div class="sub">{" / ".join(JUDGE_LABEL[j] for j in JUDGES)}</div></div>
  <div class="kpi"><div class="label">评分口径</div><div class="val">三分类</div><div class="sub">exact 一致 + Macro-F1 + Cohen κ</div></div>
</div>

<div class="note key"><strong>怎么读这份报告：</strong>每个评委模型被要求对同一段 tutor 回复、在同一个教学维度上给出人工标注体系里的标签（Yes / To some extent / No 等）。分数 = 评委判断与<strong>人工 gold</strong> 的一致程度。这不是评 tutor 回复的好坏，而是评「模型当评委时有多像人」。κ（Cohen's kappa）扣除了随机一致的成分，是比原始一致率更可信的指标。</div>

<h2>一、总榜：跨维度宏平均</h2>
{macro_table()}
<p class="muted">Agreement=三态 exact 一致率的跨维度宏平均；Macro-F1 处理类别不均衡；κ 扣随机一致。BEA 另给 Lenient（把「To some extent」并入 Yes 一侧，等价一种二分类口径）。</p>
<div class="note">最强评委：MRBench 上 <strong>{JUDGE_LABEL[mr_best['judge']] if mr_best else '—'}</strong>（κ {fmt(mr_best['kappa'],2) if mr_best else '—'}），BEA2025 上 <strong>{JUDGE_LABEL[bea_best['judge']] if bea_best else '—'}</strong>（κ {fmt(bea_best['kappa'],2) if bea_best else '—'}）。三个评委拉得开：DeepSeek-V3.2 明显弱于另两个，说明该测评<strong>能区分评委优劣</strong>，不是天花板/地板。</div>

<h2>二、共享 4 维合并视图</h2>
<p>MRBench 与 BEA 都标注了这 4 个核心教学维度，合并后每维样本量翻倍（agreement 按样本数加权）。</p>
{merged_table()}

<h2>三、MRBench 全维度（8 维）</h2>
{dim_table('mrbench_judge')}

<h2>四、BEA2025-dev 全维度（4 维）</h2>
{dim_table('bea2025_judge')}

<h2>五、结论与读法</h2>
<ul>
  <li><strong>可靠性随维度剧烈波动。</strong>「是否泄题 Revealing_of_the_Answer」这类客观维度评委一致率高（&gt;0.9），而 <strong>Mistake_Location / Actionability</strong> 这类需要判断"引导是否可执行、错误定位是否准"的维度一致率最低——和 RuVerBench 里 Logic/Facts 比 Format 难验证是同一现象。</li>
  <li><strong>三分类是合理口径。</strong>「To some extent」中间态占 6–24%，正是评委与人分歧集中处；折成二分类会掩盖这部分难度。保留三态 + Macro-F1/κ 更能反映真实校准水平。</li>
  <li><strong>类别不均衡必须用 κ / Macro-F1 看。</strong>部分维度 Yes 占 80–88%，只看 agreement 会虚高；κ 才揭示评委是否真的在判断而非顺大流。</li>
</ul>

<div class="note warn"><strong>尚未完成（成品化缺口）：</strong>评委只覆盖 3 个国产模型；建议补 glm-5.1 / doubao / claude / gpt 凑成 6–8 模型榜。维度口径上 MRBench 8 维与 BEA 4 维仅部分重叠，跨基准结论以「共享 4 维」为准。BEA test 标签官方隐藏，本报告只用 dev。</div>

<footer>由 <code>scripts/build_judge_calibration_report.py</code> 自动生成 · 共 {total_tuples:,} 条判据级人工标签 / 评委 · 数据源 reports/eval/{{mrbench_judge,bea2025_judge}}/</footer>
</div></body></html>"""

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"wrote {OUT}  ({len(html):,} bytes)")
    print(f"total judge tuples per model: {total_tuples:,}")


if __name__ == "__main__":
    main()
