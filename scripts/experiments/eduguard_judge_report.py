"""Render report.html for the EduGuard-Bench P2 judge calibration experiment.

Reads ``judge_vs_gold_summary.json`` (written by ``eduguard_judge_eval.py score``)
and regenerates ``report.html`` in the same directory. Idempotent: rerun after
scoring a new judge to refresh the table. No external deps.

    python scripts/experiments/eduguard_judge_report.py
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "reports" / "re_benchmark_v1" / "experiments" / "eduguard_judge_calibration"
SUMMARY_PATH = OUT_DIR / "judge_vs_gold_summary.json"
REPORT_PATH = OUT_DIR / "report.html"


def _pct(x: float | None) -> str:
    return "n/a" if x is None else f"{x * 100:.2f}%"


def _kappa(x: float | None) -> str:
    return "n/a" if x is None else f"{x:.4f}"


def render(summary: dict) -> str:
    dist = summary["gold_distribution"]
    harm = dist["harm"]
    tiers = dist["refusal_tiers"]
    total = sum(harm.values())

    paper_rows = "\n".join(
        f"<tr><td>{m}</td><td>{v['harm']:.4f}</td><td>{v['refusal_quality']:.4f}</td></tr>"
        for m, v in summary["paper_reference_kappa_vs_human"].items()
    )

    tier_lines = "\n".join(f"        <div>{k}: {v}</div>" for k, v in tiers.items())

    # judges sorted by harm κ desc (None last) — same order the score CLI prints.
    judges = summary["judges"]
    ordered = sorted(
        judges.items(),
        key=lambda kv: (kv[1].get("harm_kappa") is None, -(kv[1].get("harm_kappa") or -9)),
    )
    judge_rows = "\n".join(
        f"""      <tr>
        <td>{name}</td>
        <td>{_pct(r['harm_accuracy'])}</td>
        <td>{_kappa(r['harm_kappa'])}</td>
        <td>{r['n_harm']}</td>
        <td>{_pct(r['refusal_quality_accuracy'])}</td>
        <td>{_kappa(r['refusal_quality_kappa'])}</td>
        <td>{r['n_refusal_quality']}</td>
      </tr>"""
        for name, r in ordered
    )

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>EduGuard-Bench P2 Judge 校准报告</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f6f7fb; color: #1f2937; margin: 0; padding: 0; }}
    .container {{ max-width: 1100px; margin: 0 auto; padding: 28px 18px 40px; }}
    h1 {{ margin: 0 0 10px; color: #111827; }}
    .meta {{ color: #6b7280; margin-bottom: 18px; font-size: 13px; }}
    .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin: 18px 0 20px; }}
    .card {{ background: #fff; border: 1px solid #e5e7eb; border-radius: 10px; padding: 14px 16px; }}
    .card h3 {{ margin: 0 0 8px; font-size: 15px; }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 8px; background: #fff; }}
    th, td {{ border: 1px solid #e5e7eb; padding: 8px 10px; text-align: left; font-size: 13px; }}
    th {{ background: #f3f4f6; }}
    .footer {{ color: #6b7280; font-size: 12px; margin-top: 22px; }}
    .updated {{ margin-top: 6px; color: #374151; font-weight: 600; }}
    pre {{ background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 8px; padding: 10px; overflow: auto; }}
  </style>
</head>
<body>
  <div class="container">
    <h1>EduGuard-Bench P2 Judge 校准报告（vs Claude Opus 4.8 金标）</h1>
    <div class="meta">
      实验目录：<code>reports/re_benchmark_v1/experiments/eduguard_judge_calibration/</code>  ｜
      样本规模：{total}（harmful {harm.get('harmful', 0)} / harmless {harm.get('harmless', 0)}）
    </div>

    <div class="grid">
      <div class="card">
        <h3>金标拒答分布</h3>
{tier_lines}
      </div>
      <div class="card">
        <h3>论文参考（人类标注对比）</h3>
        <table>
          <thead><tr><th>模型</th><th>harm κ</th><th>refusal-quality κ</th></tr></thead>
          <tbody>
            {paper_rows}
          </tbody>
        </table>
      </div>
    </div>

    <div class="card" style="margin-bottom: 20px;">
      <h3>评测结果（按 harm κ 排序）</h3>
      <table>
        <thead>
          <tr>
            <th>judge 模型</th>
            <th>harm 准确率</th>
            <th>harm κ</th>
            <th>n_harm</th>
            <th>拒答质量准确率</th>
            <th>拒答质量 κ</th>
            <th>n_refusal_quality</th>
          </tr>
        </thead>
        <tbody>
{judge_rows}
        </tbody>
      </table>
    </div>

    <div class="card">
      <h3>输出文件</h3>
      <div>judge_vs_gold_summary.json：{SUMMARY_PATH}</div>
      <div>judgements.jsonl：{OUT_DIR / 'judgements.jsonl'}</div>
    </div>

    <div class="footer">
      <div>更新时间（本地）：{now}</div>
      <div class="updated">已根据最新 `judge_vs_gold_summary.json` 重生成</div>
    </div>
  </div>
</body>
</html>
"""


def main() -> None:
    summary = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
    REPORT_PATH.write_text(render(summary), encoding="utf-8")
    print(f"wrote {REPORT_PATH} ({len(summary['judges'])} judges)")


if __name__ == "__main__":
    main()
