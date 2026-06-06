"""Summary aggregation and HTML report for an evaluation run."""

from __future__ import annotations

import html
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


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


def write_report(path: Path, summary: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    acc = summary["accuracy"]
    acc_text = "n/a" if acc is None else f"{acc:.3f}"
    status_rows = "".join(
        f"<tr><td>{esc(k)}</td><td>{esc(v)}</td></tr>" for k, v in sorted(summary["status_counts"].items())
    )
    bucket_sections = []
    for key, groups in summary["by_bucket"].items():
        rows = "".join(
            "<tr>"
            f"<td>{esc(group)}</td>"
            f"<td>{esc(stat['total'])}</td>"
            f"<td>{esc(stat['correct'])}</td>"
            f"<td>{'n/a' if stat['accuracy'] is None else f'{stat['accuracy']:.3f}'}</td>"
            "</tr>"
            for group, stat in groups.items()
        )
        bucket_sections.append(
            f"<section><h2>By {esc(key)}</h2>"
            "<table><thead><tr><th>Group</th><th>Total</th><th>Correct</th><th>Accuracy</th></tr></thead>"
            f"<tbody>{rows}</tbody></table></section>"
        )
    html_text = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Eval Report · {esc(summary['benchmark'])}</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans SC", sans-serif; margin: 0; background: #f4f6fb; color: #182033; }}
    main {{ max-width: 980px; margin: 0 auto; padding: 32px 22px 50px; }}
    header, section {{ background: white; border: 1px solid #dbe2ef; border-radius: 8px; padding: 22px; margin-bottom: 16px; }}
    h1 {{ margin: 0 0 8px; }}
    table {{ width: 100%; border-collapse: collapse; }}
    th, td {{ padding: 9px 10px; border-bottom: 1px solid #dbe2ef; text-align: left; }}
    th {{ background: #f7f9fd; }}
  </style>
</head>
<body>
<main>
  <header>
    <h1>Eval Report · {esc(summary['benchmark'])}</h1>
    <p>Model: <strong>{esc(summary['model'])}</strong>. Items: <strong>{esc(summary['total_items'])}</strong>. Scored: <strong>{esc(summary['scored'])}</strong>. Accuracy: <strong>{acc_text}</strong>.</p>
  </header>
  <section>
    <h2>Status</h2>
    <table><thead><tr><th>Status</th><th>Count</th></tr></thead><tbody>{status_rows}</tbody></table>
  </section>
  {''.join(bucket_sections)}
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
