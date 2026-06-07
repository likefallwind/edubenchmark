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


def _select_wrong(scored: list[dict[str, Any]], n: int) -> list[dict[str, Any]]:
    """Pick up to ``n`` incorrect rows, spread across tasks for variety."""
    wrong = [r for r in scored if r.get("score_status") == "scored" and not r.get("correct")]
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
    correct = sum(1 for r in counted if r.get("correct"))
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
                "correct": sum(1 for r in rows if r.get("correct")),
                "accuracy": (sum(1 for r in rows if r.get("correct")) / len(rows)) if rows else None,
            }
            for group, rows in sorted(groups.items())
        }

    return {
        "benchmark": benchmark,
        "model": model,
        "total_items": total,
        "scored": len(counted),
        "correct": correct,
        "accuracy": (correct / len(counted)) if counted else None,
        "status_counts": dict(status_counts),
        "by_bucket": by_bucket,
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
    bench_title = (getattr(adapter, "title", "") or summary["benchmark"]) if adapter else summary["benchmark"]
    homepage = getattr(adapter, "homepage", "") if adapter else ""
    description = getattr(adapter, "description", "") if adapter else ""

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
      <div class="kpi"><div class="v">{acc_text}</div><div class="k">正确率</div></div>
      <div class="kpi"><div class="v">{esc(summary['total_items'])}</div><div class="k">总题数</div></div>
      <div class="kpi"><div class="v">{esc(summary['scored'])}</div><div class="k">已判分</div></div>
      <div class="kpi"><div class="v">{esc(summary['correct'])}</div><div class="k">答对</div></div>
    </div>
  </header>
  {intro_html}
  {sample_html}
  {status_html}
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
            if line:
                rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
