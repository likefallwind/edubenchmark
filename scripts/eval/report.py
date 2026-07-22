"""Summary aggregation and HTML report for an evaluation run."""

from __future__ import annotations

import base64
import html
import json
import mimetypes
from collections import defaultdict
from pathlib import Path
from typing import Any


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def _paragraphs(text: str) -> str:
    """Render blank-line-separated text as <p> blocks (escaped)."""
    blocks = [b.strip() for b in str(text or "").split("\n\n") if b.strip()]
    return "".join(f"<p>{esc(b)}</p>" for b in blocks)


def _image_tag(path: Path, max_bytes: int = 1_500_000) -> str:
    """Inline a local image as a base64 data URI so the report is self-contained.

    Returns an empty string if the file is missing or too large to inline.
    """
    try:
        path = Path(path)
        if not path.is_file():
            return ""
        data = path.read_bytes()
        if len(data) > max_bytes:
            return f'<p class="muted">[图片过大未内联：{esc(path.name)}]</p>'
        mime = mimetypes.guess_type(str(path))[0] or "image/jpeg"
        uri = f"data:{mime};base64,{base64.b64encode(data).decode('ascii')}"
        return f'<img class="qimg" src="{uri}" alt="{esc(path.name)}">'
    except Exception:
        return ""


def _truncate(text: str, limit: int = 2000) -> tuple[str, bool]:
    text = str(text or "")
    if len(text) <= limit:
        return text, False
    return text[:limit], True


def _choices_html(choices: Any) -> str:
    if not isinstance(choices, (list, tuple)) or not choices:
        return ""
    letters = "ABCDEFGHIJ"
    rows = "".join(
        f"<li><strong>{letters[i] if i < len(letters) else i}.</strong> {esc(c)}</li>"
        for i, c in enumerate(choices)
    )
    return f"<ul class='choices'>{rows}</ul>"


def _render_item_card(
    item: dict[str, Any] | None,
    scored_row: dict[str, Any] | None,
    *,
    show_response: bool,
) -> str:
    """Render one question card: prompt + image + choices, optionally the
    model's response with extracted / gold for wrong-answer review."""
    if item is None and scored_row is None:
        return ""
    item = item or {}
    scored_row = scored_row or {}
    meta = item.get("meta") or {}
    item_id = scored_row.get("item_id") or item.get("item_id") or "?"
    buckets = scored_row.get("buckets") or {}
    tags = " ".join(f"<span class='tag'>{esc(k)}={esc(v)}</span>" for k, v in buckets.items())

    question = item.get("text") or meta.get("query") or "(题面缺失)"
    images = "".join(_image_tag(p) for p in (item.get("image_paths") or []))
    choices = _choices_html(meta.get("choices"))
    gold = scored_row.get("gold", item.get("gold"))

    parts = [
        f"<div class='card'><div class='card-head'><span class='pid'>#{esc(item_id)}</span>{tags}</div>",
        f"<div class='qtext'>{esc(question)}</div>",
        images,
        choices,
    ]
    if show_response:
        resp, clipped = _truncate(scored_row.get("response", ""))
        note = "<div class='muted'>（回答已截断）</div>" if clipped else ""
        parts.append(
            "<div class='ans-grid'>"
            f"<div class='ans wrong'><span class='lbl'>模型抽取答案</span>{esc(scored_row.get('extracted', ''))}</div>"
            f"<div class='ans'><span class='lbl'>归一化</span>{esc(scored_row.get('normalized', ''))}</div>"
            f"<div class='ans gold'><span class='lbl'>正确答案</span>{esc(gold)}</div>"
            "</div>"
            f"<details><summary>查看模型完整作答</summary><pre class='resp'>{esc(resp)}</pre>{note}</details>"
        )
    else:
        parts.append(f"<div class='ans gold inline'><span class='lbl'>参考答案</span>{esc(gold)}</div>")
    parts.append("</div>")
    return "".join(parts)


def _failure_reason(row: dict[str, Any]) -> tuple[str, str]:
    """Map an unscored row to (category, explanation) for the report."""
    err = str(row.get("error") or "")
    low = err.lower()
    if "1026" in err or "sensitive" in low:
        return "输入审核拒绝", "平台内容审核判定输入敏感，拒绝处理——非模型能力问题"
    if "timed out" in low or "timeout" in low:
        return "请求超时", "模型推理时间超过超时上限，未在限定时间内返回"
    if row.get("empty_response"):
        return "空响应", "模型返回了空内容"
    if err:
        return "其他错误", err[:160]
    return "缺少预测", "该题没有生成预测（未运行或被跳过）"


def _unscored_section_html(scored: list[dict[str, Any]]) -> str:
    """Explain why scored < total: group no_prediction rows by failure reason."""
    unscored = [r for r in scored if r.get("score_status") != "scored"]
    if not unscored:
        return ""
    groups: dict[str, dict[str, Any]] = {}
    for row in unscored:
        cat, why = _failure_reason(row)
        g = groups.setdefault(cat, {"why": why, "ids": []})
        g["ids"].append(str(row.get("item_id")))
    rows = "".join(
        "<tr>"
        f"<td><strong>{esc(cat)}</strong></td>"
        f"<td>{esc(len(g['ids']))}</td>"
        f"<td>{esc(g['why'])}</td>"
        f"<td class='muted'>{esc(', '.join(g['ids']))}</td>"
        "</tr>"
        for cat, g in sorted(groups.items(), key=lambda kv: -len(kv[1]["ids"]))
    )
    return (
        f"<section><h2>未判分原因（{len(unscored)} 题）</h2>"
        "<p class='muted'>这些题目未取得有效作答，已从正确率分母中排除（不计为答错），多为平台审核或超时等基础设施限制。</p>"
        "<table><thead><tr><th>原因</th><th>数量</th><th>说明</th><th>题号</th></tr></thead>"
        f"<tbody>{rows}</tbody></table></section>"
    )


def _select_wrong(scored: list[dict[str, Any]], n: int) -> list[dict[str, Any]]:
    """Pick up to ``n`` incorrect rows, spread across tasks for variety."""
    wrong = [r for r in scored if r.get("score_status") == "scored" and r.get("correct") is False]
    by_task: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for r in wrong:
        by_task[str((r.get("buckets") or {}).get("task"))].append(r)
    picked: list[dict[str, Any]] = []
    queues = list(by_task.values())
    i = 0
    while len(picked) < n and any(queues):
        q = queues[i % len(queues)]
        if q:
            picked.append(q.pop(0))
        i += 1
        if i > 10000:
            break
    return picked[:n]


def build_summary(
    benchmark: str,
    model: str,
    scored: list[dict[str, Any]],
    bucket_keys: list[str],
) -> dict[str, Any]:
    total = len(scored)
    counted = [r for r in scored if r.get("score_status") == "scored"]
    accuracy_rows = [r for r in counted if isinstance(r.get("correct"), bool)]
    correct_count = sum(1 for r in accuracy_rows if r.get("correct"))
    correct: int | None = correct_count if accuracy_rows else None
    status_counts: dict[str, int] = defaultdict(int)
    for row in scored:
        status_counts[row.get("score_status", "unknown")] += 1

    by_bucket: dict[str, dict[str, dict[str, Any]]] = {}
    for key in bucket_keys:
        groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in counted:
            groups[str((row.get("buckets") or {}).get(key))].append(row)
        by_bucket[key] = {
            group: {
                "total": len(rows),
                "correct": (
                    sum(1 for r in rows if r.get("correct"))
                    if any(isinstance(r.get("correct"), bool) for r in rows)
                    else None
                ),
                "accuracy": (
                    sum(1 for r in rows if r.get("correct"))
                    / sum(1 for r in rows if isinstance(r.get("correct"), bool))
                    if any(isinstance(r.get("correct"), bool) for r in rows)
                    else None
                ),
            }
            for group, rows in sorted(groups.items())
        }

    return {
        "benchmark": benchmark,
        "model": model,
        "total_items": total,
        "scored": len(counted),
        "correct": correct,
        "accuracy": (correct_count / len(accuracy_rows)) if accuracy_rows else None,
        "status_counts": dict(status_counts),
        "by_bucket": by_bucket,
    }


def _sum_usage(rows: "dict[str, dict[str, Any]] | list[dict[str, Any]]") -> dict[str, int]:
    """Sum per-row ``usage`` dicts into one totals block.

    Accepts the by-item dicts the runner threads around (or a list of rows).
    ``items_with_usage`` counts rows whose usage reported any tokens, so a result
    with calls>0 but items_with_usage==0 flags a provider that omitted usage.
    """
    iterable = rows.values() if isinstance(rows, dict) else rows
    totals = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0, "calls": 0, "items_with_usage": 0}
    for row in iterable:
        usage = row.get("usage")
        if not isinstance(usage, dict):
            continue
        for field in ("prompt_tokens", "completion_tokens", "total_tokens", "calls"):
            value = usage.get(field)
            if isinstance(value, (int, float)):
                totals[field] += int(value)
        if any(isinstance(usage.get(f), (int, float)) and usage.get(f) for f in ("prompt_tokens", "completion_tokens", "total_tokens")):
            totals["items_with_usage"] += 1
    return totals


def aggregate_token_usage(
    predictions: "dict[str, dict[str, Any]]",
    extractions: "dict[str, dict[str, Any]]",
) -> dict[str, Any]:
    """Aggregate prediction vs. extraction token usage for ``summary.json``."""
    prediction = _sum_usage(predictions)
    extraction = _sum_usage(extractions)
    return {
        "prediction": prediction,
        "extraction": extraction,
        "total_tokens": prediction["total_tokens"] + extraction["total_tokens"],
    }


_REPORT_CSS = """
  body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans SC", sans-serif; margin: 0; background: #f4f6fb; color: #182033; line-height: 1.6; }
  main { max-width: 980px; margin: 0 auto; padding: 32px 22px 60px; }
  header, section { background: white; border: 1px solid #dbe2ef; border-radius: 10px; padding: 22px 24px; margin-bottom: 18px; }
  h1 { margin: 0 0 6px; font-size: 26px; }
  h2 { margin: 2px 0 14px; font-size: 19px; border-left: 4px solid #4361ee; padding-left: 10px; }
  a { color: #3a56d4; }
  p { margin: 0 0 10px; }
  .muted { color: #6b7588; font-size: 13px; }
  section.warn { background: #fff8e6; border-color: #f0d9a0; }
  section.warn h2 { border-left-color: #d98324; }
  .kpis { display: flex; flex-wrap: wrap; gap: 12px; margin-top: 12px; }
  .kpi { flex: 1 1 130px; background: #f5f8ff; border: 1px solid #dde6fb; border-radius: 8px; padding: 12px 14px; }
  .kpi .v { font-size: 24px; font-weight: 700; color: #1b2a6b; }
  .kpi .k { font-size: 12px; color: #6b7588; text-transform: uppercase; letter-spacing: .04em; }
  table { width: 100%; border-collapse: collapse; }
  th, td { padding: 9px 10px; border-bottom: 1px solid #e4e9f4; text-align: left; }
  th { background: #f7f9fd; font-size: 13px; }
  .bar { background: #eaeefb; border-radius: 4px; height: 8px; overflow: hidden; min-width: 90px; }
  .bar > i { display: block; height: 100%; background: #4361ee; }
  .card { border: 1px solid #e1e7f4; border-radius: 8px; padding: 16px 18px; margin-bottom: 16px; background: #fcfdff; }
  .card-head { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; margin-bottom: 8px; }
  .pid { font-weight: 700; color: #1b2a6b; }
  .tag { font-size: 12px; background: #eef2fc; color: #455; border-radius: 999px; padding: 2px 10px; }
  .qtext { white-space: pre-wrap; margin-bottom: 10px; }
  .qimg { max-width: 100%; max-height: 320px; border: 1px solid #e1e7f4; border-radius: 6px; margin: 6px 0; }
  .choices { margin: 6px 0; padding-left: 18px; }
  .ans-grid { display: flex; flex-wrap: wrap; gap: 10px; margin: 10px 0; }
  .ans { background: #f5f8ff; border: 1px solid #dde6fb; border-radius: 6px; padding: 8px 12px; font-weight: 600; }
  .ans.inline { display: inline-block; margin-top: 6px; }
  .ans.wrong { background: #fdeeee; border-color: #f3c9c9; color: #b3261e; }
  .ans.gold { background: #eafaf0; border-color: #c2ebd2; color: #166c3b; }
  .ans .lbl { display: block; font-size: 11px; font-weight: 500; color: #6b7588; text-transform: uppercase; letter-spacing: .04em; }
  details { margin-top: 8px; }
  summary { cursor: pointer; color: #3a56d4; font-size: 14px; }
  pre.resp { white-space: pre-wrap; word-break: break-word; background: #0f1730; color: #e6ebff; padding: 14px; border-radius: 6px; max-height: 360px; overflow: auto; font-size: 13px; }
"""


def _bucket_section_html(key: str, groups: dict[str, dict[str, Any]]) -> str:
    rows = []
    for group, stat in groups.items():
        acc = stat["accuracy"]
        pct = 0 if acc is None else round(acc * 100)
        acc_text = "n/a" if acc is None else f"{acc:.3f}"
        rows.append(
            "<tr>"
            f"<td>{esc(group)}</td><td>{esc(stat['total'])}</td><td>{esc(stat['correct'])}</td>"
            f"<td>{acc_text}</td>"
            f"<td><div class='bar'><i style='width:{pct}%'></i></div></td>"
            "</tr>"
        )
    return (
        f"<h3 style='margin:16px 0 6px;font-size:15px'>按 {esc(key)} 分组</h3>"
        "<table><thead><tr><th>分组</th><th>题数</th><th>正确</th><th>正确率</th><th></th></tr></thead>"
        f"<tbody>{''.join(rows)}</tbody></table>"
    )


def write_report(
    path: Path,
    summary: dict[str, Any],
    scored: list[dict[str, Any]] | None = None,
    items_by_id: dict[str, dict[str, Any]] | None = None,
    adapter: Any = None,
    *,
    num_samples: int = 2,
    num_wrong: int = 6,
) -> None:
    """Write a self-contained HTML eval report.

    Backward compatible: with only ``summary`` it still emits the overview +
    bucket tables. Pass ``scored`` + ``items_by_id`` + ``adapter`` to also get
    the benchmark intro, sample questions, and a wrong-answer gallery.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    scored = scored or []
    items_by_id = items_by_id or {}

    acc = summary["accuracy"]
    acc_text = "n/a" if acc is None else f"{acc * 100:.1f}%"
    primary_text = acc_text
    primary_label = "正确率"
    fourth_text: Any = summary["correct"]
    fourth_label = "答对"
    # Continuous rubric benchmarks deliberately have no binary accuracy.  When
    # they expose the established overall/scenario fields, surface those as the
    # report KPIs instead of leading with four variations of "n/a".
    overall = (summary.get("extra_metrics") or {}).get("overall") or {}
    if acc is None and isinstance(overall.get("mean_overall_score"), (int, float)):
        primary_text = f"{float(overall['mean_overall_score']):.3f}"
        primary_label = "总体平均分"
        if isinstance(overall.get("mean_scenario_score"), (int, float)):
            fourth_text = f"{float(overall['mean_scenario_score']):.3f}"
            fourth_label = "场景平均分"
    bench_title = (getattr(adapter, "title", "") or summary["benchmark"]) if adapter else summary["benchmark"]
    homepage = getattr(adapter, "homepage", "") if adapter else ""
    description = getattr(adapter, "description", "") if adapter else ""

    # --- degraded-input warning (--no-images) ---
    variant_html = ""
    if summary.get("input_variant") == "no_images":
        note = summary.get("input_variant_note") or "图片已 withheld，仅发送文本。"
        variant_html = (
            "<section class='warn'><h2>⚠ 文本降级变体（--no-images）</h2>"
            f"<p>{esc(note)}</p>"
            "<p class='muted'>本页所有分数仅供该模型自身的文本可解子集参考，"
            "不得并入主结果、不得与其它模型横向比较。</p></section>"
        )

    # --- benchmark intro ---
    intro_html = ""
    if description or homepage:
        link = f"<p class='muted'>主页：<a href='{esc(homepage)}'>{esc(homepage)}</a></p>" if homepage else ""
        intro_html = f"<section><h2>基准介绍</h2>{_paragraphs(description)}{link}</section>"

    # --- sample questions ---
    sample_html = ""
    if items_by_id and num_samples > 0:
        ordered_ids = [r["item_id"] for r in scored] or list(items_by_id)
        cards = []
        for iid in ordered_ids:
            item = items_by_id.get(str(iid))
            if not item:
                continue
            srow = next((r for r in scored if str(r.get("item_id")) == str(iid)), {"item_id": iid})
            cards.append(_render_item_card(item, srow, show_response=False))
            if len(cards) >= num_samples:
                break
        if cards:
            sample_html = f"<section><h2>题目示例</h2>{''.join(cards)}</section>"

    # --- benchmark-specific extra metrics (e.g. RFS, ASR) ---
    extra_html = ""
    if summary.get("extra_metrics"):
        extra_json = json.dumps(summary["extra_metrics"], ensure_ascii=False, indent=2)
        extra_html = (
            "<section><h2>专项指标</h2>"
            "<p class='muted'>该基准在正确率之外的官方指标（同 summary.json 的 extra_metrics）。</p>"
            f"<pre class='resp'>{esc(extra_json)}</pre></section>"
        )

    # --- status table ---
    status_rows = "".join(
        f"<tr><td>{esc(k)}</td><td>{esc(v)}</td></tr>" for k, v in sorted(summary["status_counts"].items())
    )
    status_html = (
        "<section><h2>作答情况</h2>"
        "<table><thead><tr><th>状态</th><th>数量</th></tr></thead>"
        f"<tbody>{status_rows}</tbody></table>"
        + "".join(_bucket_section_html(k, g) for k, g in summary["by_bucket"].items())
        + "</section>"
    )

    # --- unscored reasons (explains scored < total) ---
    unscored_html = _unscored_section_html(scored)

    # --- wrong-answer gallery ---
    wrong_html = ""
    if scored and num_wrong > 0:
        picked = _select_wrong(scored, num_wrong)
        if picked:
            cards = [
                _render_item_card(items_by_id.get(str(r.get("item_id"))), r, show_response=True)
                for r in picked
            ]
            wrong_html = (
                f"<section><h2>错题分析（{len(picked)} 例）</h2>"
                "<p class='muted'>已尽量覆盖不同任务类型；展开可查看模型完整推理过程。</p>"
                f"{''.join(cards)}</section>"
            )

    html_text = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>评测报告 · {esc(summary['benchmark'])}</title>
  <style>{_REPORT_CSS}</style>
</head>
<body>
<main>
  <header>
    <h1>评测报告 · {esc(bench_title)}</h1>
    <p class="muted">基准 {esc(summary['benchmark'])} · 模型 <strong>{esc(summary['model'])}</strong></p>
    <div class="kpis">
      <div class="kpi"><div class="v">{esc(primary_text)}</div><div class="k">{esc(primary_label)}</div></div>
      <div class="kpi"><div class="v">{esc(summary['total_items'])}</div><div class="k">总题数</div></div>
      <div class="kpi"><div class="v">{esc(summary['scored'])}</div><div class="k">已判分</div></div>
      <div class="kpi"><div class="v">{esc(fourth_text)}</div><div class="k">{esc(fourth_label)}</div></div>
    </div>
  </header>
  {variant_html}
  {intro_html}
  {sample_html}
  {extra_html}
  {status_html}
  {unscored_html}
  {wrong_html}
</main>
</body>
</html>
"""
    path.write_text(html_text, encoding="utf-8")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows = []
    with path.open(encoding="utf-8", errors="ignore") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                # Partial line left by an interrupted append; the item will rerun.
                continue
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(row, ensure_ascii=False) + "\n"
    with path.open("a+b") as fh:
        # Terminate a truncated trailing line left by an interrupted append so
        # it can't swallow this row (reads honor seek; writes still go to EOF).
        fh.seek(0, 2)
        if fh.tell() > 0:
            fh.seek(fh.tell() - 1)
            if fh.read(1) != b"\n":
                line = "\n" + line
        fh.write(line.encode("utf-8"))
