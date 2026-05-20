#!/usr/bin/env python3
"""Generate an HTML report for the MiniMax RE_BENCHMARK_V1 smoke run."""

from __future__ import annotations

import html
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "re_benchmark_v1"
REPORT_DIR = ROOT / "reports" / "re_benchmark_v1"
ITEMS_PATH = DATA_DIR / "pilot_items.jsonl"
PREDICTIONS_PATH = REPORT_DIR / "minimax_predictions.jsonl"
SCORES_PATH = REPORT_DIR / "minimax_auto_scores.jsonl"
PROMPTS_PATH = DATA_DIR / "pilot_prompts.jsonl"
OUT_PATH = REPORT_DIR / "minimax_smoke_report.html"
FULL_OUT_PATH = REPORT_DIR / "minimax_full_pilot_report.html"


CATEGORY_NAMES = {
    "C1": "学科认知与问题求解",
    "C2": "教学设计与学习辅导",
    "C3": "学情建模与个性化",
    "C4": "作答评价与反馈",
    "C5": "教育安全与伦理合规",
}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    with path.open(encoding="utf-8", errors="ignore") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def esc(value: Any) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def trunc(value: Any, limit: int = 360) -> str:
    text = " ".join(("" if value is None else str(value)).split())
    if len(text) <= limit:
        return text
    return text[: limit - 1] + "..."


def qualitative_label(prediction: dict[str, Any]) -> tuple[str, str]:
    response = str(prediction.get("response") or "").strip()
    if not response:
        return "空响应", "API 返回了空文本，不能用于能力判断。"
    category = prediction.get("category_id")
    benchmark = prediction.get("benchmark_id")
    if category == "C5":
        return "可人工复核", "给出拒答式安全回应；是否足够支持性需要按 EduGuard rubric 复核。"
    if category == "C4" and benchmark == "edueval":
        return "可人工复核", "给出作文分数和分维度理由；需与人工标签/评分尺度校准。"
    if category == "C2" and benchmark == "edueval":
        return "可人工复核", "给出结构化教学设计；需检查是否贴合题目、学段和教学资源约束。"
    return "可人工复核", "开放题暂不自动 judge，需要人工按 rubric 阅读。"


def main() -> None:
    items = {row["pilot_item_id"]: row for row in read_jsonl(ITEMS_PATH)}
    predictions = read_jsonl(PREDICTIONS_PATH)
    scores = {row["pilot_item_id"]: row for row in read_jsonl(SCORES_PATH)}
    prompts = {row["pilot_item_id"]: row for row in read_jsonl(PROMPTS_PATH)}

    tested = []
    for prediction in predictions:
        item = items.get(prediction["pilot_item_id"], {})
        score = scores.get(prediction["pilot_item_id"], {})
        prompt = prompts.get(prediction["pilot_item_id"], {})
        tested.append({"prediction": prediction, "item": item, "score": score, "prompt": prompt})

    auto = [row for row in tested if row["score"].get("score_status") == "auto_scored"]
    judge = [row for row in tested if row["score"].get("score_status") == "judge_required"]
    protocol = [row for row in tested if row["score"].get("score_status") == "protocol_required"]
    correct = sum(1 for row in auto if row["score"].get("score") == 1.0)
    empty = sum(1 for row in tested if not str(row["prediction"].get("response") or "").strip())
    prompt_style_counts = Counter(row.get("prompt_style", "unknown") for row in prompts.values())

    by_category: dict[str, Counter[str]] = defaultdict(Counter)
    by_benchmark: dict[str, Counter[str]] = defaultdict(Counter)
    for row in tested:
        pred = row["prediction"]
        score = row["score"]
        category = pred.get("category_id", "unknown")
        benchmark = pred.get("benchmark_id", "unknown")
        status = score.get("score_status", "unscored")
        by_category[category][status] += 1
        by_benchmark[benchmark][status] += 1
        if score.get("score") == 1.0:
            by_category[category]["correct"] += 1
            by_benchmark[benchmark]["correct"] += 1
        if not str(pred.get("response") or "").strip():
            by_category[category]["empty_response"] += 1
            by_benchmark[benchmark]["empty_response"] += 1

    category_rows = []
    for category, counts in sorted(by_category.items()):
        tested_count = counts["auto_scored"] + counts["judge_required"] + counts["protocol_required"]
        category_rows.append(
            "<tr>"
            f"<td><strong>{esc(category)}</strong><br><span>{esc(CATEGORY_NAMES.get(category, ''))}</span></td>"
            f"<td>{tested_count}</td>"
            f"<td>{counts['auto_scored']}</td>"
            f"<td>{counts['correct']}</td>"
            f"<td>{counts['judge_required']}</td>"
            f"<td>{counts['protocol_required']}</td>"
            f"<td>{counts['empty_response']}</td>"
            "</tr>"
        )

    benchmark_rows = []
    for benchmark, counts in sorted(by_benchmark.items()):
        tested_count = counts["auto_scored"] + counts["judge_required"] + counts["protocol_required"]
        benchmark_rows.append(
            "<tr>"
            f"<td>{esc(benchmark)}</td>"
            f"<td>{tested_count}</td>"
            f"<td>{counts['auto_scored']}</td>"
            f"<td>{counts['correct']}</td>"
            f"<td>{counts['judge_required']}</td>"
            f"<td>{counts['protocol_required']}</td>"
            f"<td>{counts['empty_response']}</td>"
            "</tr>"
        )

    prompt_rows = []
    for style, count in sorted(prompt_style_counts.items()):
        prompt_rows.append(
            "<tr>"
            f"<td>{esc(style)}</td>"
            f"<td>{count}</td>"
            "</tr>"
        )

    auto_rows = []
    for row in auto:
        item = row["item"]
        pred = row["prediction"]
        score = row["score"]
        verdict = "正确" if score.get("score") == 1.0 else "错误"
        gold = item.get("answer_or_rubric")
        if score.get("correct_label"):
            gold = f"{score.get('correct_label')} ({score.get('correct_text')})"
        auto_rows.append(
            "<tr>"
            f"<td>{esc(pred.get('pilot_item_id'))}</td>"
            f"<td>{esc(pred.get('benchmark_id'))}</td>"
            f"<td>{esc(item.get('dimension_id'))}<br><span>{esc(item.get('dimension_name'))}</span></td>"
            f"<td>{esc(trunc(item.get('question'), 520))}</td>"
            f"<td>{esc(gold)}</td>"
            f"<td>{esc(trunc(pred.get('response'), 360))}</td>"
            f"<td>{esc(score.get('extracted_answer') or pred.get('extracted_answer'))}</td>"
            f"<td><span class='pill {'ok' if verdict == '正确' else 'bad'}'>{verdict}</span></td>"
            "</tr>"
        )

    judge_rows = []
    for row in judge:
        item = row["item"]
        pred = row["prediction"]
        label, note = qualitative_label(pred)
        judge_rows.append(
            "<tr>"
            f"<td>{esc(pred.get('pilot_item_id'))}</td>"
            f"<td>{esc(pred.get('category_id'))} / {esc(pred.get('benchmark_id'))}</td>"
            f"<td>{esc(item.get('dimension_id'))}<br><span>{esc(item.get('dimension_name'))}</span></td>"
            f"<td>{esc(trunc(item.get('question'), 520))}</td>"
            f"<td>{esc(trunc(pred.get('response'), 620))}</td>"
            f"<td><span class='pill neutral'>{esc(label)}</span><br>{esc(note)}</td>"
            "</tr>"
        )

    accuracy = correct / len(auto) if auto else None
    accuracy_text = "n/a" if accuracy is None else f"{accuracy:.3f}"
    is_full_pilot = len(predictions) >= len(items)
    report_name = "MiniMax RE_BENCHMARK_V1 Full Pilot Report" if is_full_pilot else "MiniMax RE_BENCHMARK_V1 Smoke Report"
    run_label = "full pilot run" if is_full_pilot else "smoke run"
    auto_summary_parts = []
    for benchmark in sorted(by_benchmark):
        counts = by_benchmark[benchmark]
        if counts["auto_scored"]:
            auto_summary_parts.append(f"{benchmark}: {counts['correct']}/{counts['auto_scored']}")
    auto_summary = "；".join(auto_summary_parts) if auto_summary_parts else "无自动评分题"
    open_summary_parts = []
    for benchmark in sorted(by_benchmark):
        counts = by_benchmark[benchmark]
        if counts["judge_required"]:
            open_summary_parts.append(f"{benchmark}: {counts['judge_required']} 条")
    open_summary = "；".join(open_summary_parts) if open_summary_parts else "无开放题"
    protocol_summary_parts = []
    for benchmark in sorted(by_benchmark):
        counts = by_benchmark[benchmark]
        if counts["protocol_required"]:
            protocol_summary_parts.append(f"{benchmark}: {counts['protocol_required']} 条")
    protocol_summary = "；".join(protocol_summary_parts) if protocol_summary_parts else "无 protocol-only 题"
    html_text = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(report_name)}</title>
  <style>
    :root {{
      --ink: #172033;
      --muted: #647086;
      --line: #dbe2ef;
      --panel: #ffffff;
      --bg: #f5f7fb;
      --good: #166534;
      --bad: #991b1b;
      --warn: #92400e;
      --blue: #1d4ed8;
    }}
    body {{ margin: 0; background: var(--bg); color: var(--ink); font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans SC", Arial, sans-serif; }}
    main {{ max-width: 1180px; margin: 0 auto; padding: 32px 22px 56px; }}
    header, section {{ background: var(--panel); border: 1px solid var(--line); border-radius: 8px; padding: 22px; margin-bottom: 16px; }}
    h1 {{ margin: 0 0 8px; font-size: 30px; }}
    h2 {{ margin: 0 0 14px; font-size: 21px; }}
    p {{ line-height: 1.62; }}
    .muted, span {{ color: var(--muted); }}
    .grid {{ display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 12px; }}
    .tile {{ background: #f8fafc; border: 1px solid var(--line); border-radius: 8px; padding: 14px; min-height: 72px; }}
    .tile b {{ display: block; font-size: 26px; margin-bottom: 4px; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
    th, td {{ padding: 10px 9px; border-bottom: 1px solid var(--line); text-align: left; vertical-align: top; }}
    th {{ background: #f8fafc; font-weight: 650; }}
    code {{ background: #eef2f8; padding: 2px 5px; border-radius: 4px; }}
    .pill {{ display: inline-block; border-radius: 999px; padding: 3px 8px; font-size: 12px; font-weight: 650; }}
    .pill.ok {{ color: var(--good); background: #dcfce7; }}
    .pill.bad {{ color: var(--bad); background: #fee2e2; }}
    .pill.neutral {{ color: var(--blue); background: #dbeafe; margin-bottom: 5px; }}
    .callout {{ border-left: 4px solid var(--warn); background: #fffbeb; padding: 12px 14px; border-radius: 6px; }}
    .scroll {{ overflow-x: auto; }}
  </style>
</head>
<body>
<main>
  <header>
    <h1>{esc(report_name)}</h1>
    <p class="muted">模型：<code>MiniMax-M2.7</code>。数据来源：<code>reports/re_benchmark_v1/minimax_predictions.jsonl</code>、<code>minimax_auto_scores.jsonl</code> 和 <code>data/re_benchmark_v1/pilot_prompts.jsonl</code>。生成口径：2026-05-20。</p>
    <p>这是一轮研究版 {esc(run_label)}，不是完整榜单。实际向 MiniMax 发送了 {len(predictions)} 道 pilot item，其中 {len(auto)} 道可自动评分，{len(judge)} 道需要人工或 LLM judge 复核，{len(protocol)} 道是 protocol-only 项。</p>
  </header>

  <section>
    <h2>总体结论</h2>
    <div class="grid">
      <div class="tile"><b>{len(predictions)}</b><span>已测试题目</span></div>
      <div class="tile"><b>{len(auto)}</b><span>自动评分题</span></div>
      <div class="tile"><b>{correct}/{len(auto)}</b><span>自动题正确</span></div>
      <div class="tile"><b>{accuracy_text}</b><span>自动题 accuracy</span></div>
      <div class="tile"><b>{len(protocol)}</b><span>protocol-only</span></div>
    </div>
    <p class="callout">结论边界：自动题样本只有 {len(auto)} 道，不能代表完整 C1 能力；开放教学、作文评分和安全题没有自动 judge，本报告只做人工阅读摘要。另有 {empty} 条返回为空，提示本轮 API/timeout 或 endpoint 行为还不稳定。注意：历史 MiniMax 预测可能来自修复前统一 wrapper prompt；正式复跑应使用当前 <code>pilot_prompts.jsonl</code> 的 prompt 口径。</p>
  </section>

  <section>
    <h2>Prompt 口径</h2>
    <p>当前 prompt 已按题型分流：MMLU/AGIEval 选择题从原始数据重建选项并要求只返回选项字母；EduGuard 使用题目内嵌安全指令；KT/protocol 项不再当作普通问答；多模态项在 text-only 运行中明确返回图像输入缺失。</p>
    <div class="scroll">
      <table><thead><tr><th>Prompt style</th><th>Items</th></tr></thead><tbody>{''.join(prompt_rows)}</tbody></table>
    </div>
  </section>

  <section>
    <h2>按类别统计</h2>
    <div class="scroll">
      <table><thead><tr><th>类别</th><th>已测</th><th>自动评分</th><th>正确</th><th>需复核</th><th>Protocol</th><th>空响应</th></tr></thead><tbody>{''.join(category_rows)}</tbody></table>
    </div>
  </section>

  <section>
    <h2>按 Benchmark 统计</h2>
    <div class="scroll">
      <table><thead><tr><th>Benchmark</th><th>已测</th><th>自动评分</th><th>正确</th><th>需复核</th><th>Protocol</th><th>空响应</th></tr></thead><tbody>{''.join(benchmark_rows)}</tbody></table>
    </div>
  </section>

  <section>
    <h2>自动题逐题结果</h2>
    <div class="scroll">
      <table>
        <thead><tr><th>Item</th><th>Benchmark</th><th>维度</th><th>题目</th><th>标准答案</th><th>MiniMax 回答</th><th>抽取答案</th><th>结果</th></tr></thead>
        <tbody>{''.join(auto_rows)}</tbody>
      </table>
    </div>
  </section>

  <section>
    <h2>开放题与安全题样例</h2>
    <p class="muted">这些题没有自动判分。这里记录“是否有可复核输出”和初步阅读备注。</p>
    <div class="scroll">
      <table>
        <thead><tr><th>Item</th><th>类别 / Benchmark</th><th>维度</th><th>题目</th><th>MiniMax 回答摘要</th><th>人工阅读备注</th></tr></thead>
        <tbody>{''.join(judge_rows)}</tbody>
      </table>
    </div>
  </section>

  <section>
    <h2>效果判断</h2>
    <p>本轮最明确的信号来自 C1 自动题：{esc(auto_summary)}，合计 {correct}/{len(auto)}，accuracy={esc(accuracy_text)}。</p>
    <p>C2/C4/C5 的开放题覆盖：{esc(open_summary)}。Protocol-only 覆盖：{esc(protocol_summary)}。有些题能生成结构化教学设计、作文评分理由、数学纠错反馈或安全拒答；但本轮仍有 {empty} 条空响应或截断式输出，需要在下一轮加入重试、响应完整性检查和人工 rubric。</p>
    <p>因此，当前结论应写成“MiniMax API 链路已打通，并发上限 2 的 {esc(run_label)} 已完成；自动题表现 {correct}/{len(auto)}；开放题、代码题、多模态题和安全题需要人工或专用 runner 复核；protocol-only 项不进入普通 LLM prompt 跑分；本轮不足以发布模型榜单”。</p>
  </section>
</main>
</body>
</html>
"""
    OUT_PATH.write_text(html_text, encoding="utf-8")
    if is_full_pilot:
        FULL_OUT_PATH.write_text(html_text, encoding="utf-8")
    print(OUT_PATH.relative_to(ROOT))
    if is_full_pilot:
        print(FULL_OUT_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
