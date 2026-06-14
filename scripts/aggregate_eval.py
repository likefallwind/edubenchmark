#!/usr/bin/env python3
"""Aggregate per-benchmark eval summaries into one cross-model comparison.

Reads ``reports/eval/<benchmark>/summary.json`` (the home / MiniMax baseline) and
every ``reports/eval/<benchmark>/<model>/summary.json`` subdir produced by the
non-default models, then emits a side-by-side report at
``reports/eval/_aggregate/index.{md,html}``.

Guardrail (per README): results are shown **per benchmark** only. Accuracy is
never averaged across benchmarks — each benchmark measures a different thing.

Usage:
    python scripts/aggregate_eval.py
    python scripts/aggregate_eval.py --eval-dir reports/eval --out-dir reports/eval/_aggregate
"""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
AGGREGATE_DIRNAME = "_aggregate"


def _load_summary(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _model_slug(model: str) -> str:
    # Mirror eval.providers.model_slug without importing (keeps this script
    # runnable standalone). Keep letters/digits/dot/dash/underscore.
    import re

    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", (model or "").strip())
    return slug.strip("-") or "model"


def collect(eval_dir: Path) -> dict[str, list[dict[str, Any]]]:
    """Return {benchmark: [summary, ...]} across the home dir and model subdirs."""
    results: dict[str, list[dict[str, Any]]] = {}
    for bench_dir in sorted(p for p in eval_dir.iterdir() if p.is_dir()):
        if bench_dir.name == AGGREGATE_DIRNAME:
            continue
        summaries: list[dict[str, Any]] = []
        # Home model (top-level summary.json).
        home = _load_summary(bench_dir / "summary.json")
        if home:
            summaries.append(home)
        # Per-model subdirs: accept only dirs whose name is the model's slug,
        # which filters out dated snapshot subdirs (e.g. 2026-06-08/).
        for sub in sorted(p for p in bench_dir.iterdir() if p.is_dir()):
            sub_summary = _load_summary(sub / "summary.json")
            if not sub_summary:
                continue
            if _model_slug(sub_summary.get("model", "")) == sub.name:
                summaries.append(sub_summary)
        if summaries:
            results[bench_dir.name] = summaries
    return results


def _overall_metrics(summary: dict[str, Any]) -> dict[str, Any]:
    """Scalar metrics from extra_metrics['overall'] (rfs, asr, ...), if present."""
    extra = summary.get("extra_metrics") or {}
    overall = extra.get("overall") or {}
    return {k: v for k, v in overall.items() if isinstance(v, (int, float))}


def _fmt_acc(value: Any) -> str:
    return "n/a" if value is None else f"{value * 100:.1f}%"


def _rows(summaries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for s in summaries:
        row = {
            "model": s.get("model", "?"),
            "accuracy": s.get("accuracy"),
            "scored": s.get("scored"),
            "total": s.get("total_items"),
            "extractor_model": s.get("extractor_model", ""),
            "extra": _overall_metrics(s),
        }
        rows.append(row)
    # Best accuracy first (None sorts last).
    rows.sort(key=lambda r: (r["accuracy"] is None, -(r["accuracy"] or 0)))
    return rows


def render_markdown(results: dict[str, list[dict[str, Any]]]) -> str:
    lines = ["# Cross-model eval comparison", ""]
    lines.append(
        "Per-benchmark, side-by-side. Accuracy is **not** comparable across "
        "benchmarks and is never averaged together."
    )
    lines.append("")
    for bench in sorted(results):
        rows = _rows(results[bench])
        extra_keys = sorted({k for r in rows for k in r["extra"]})
        lines.append(f"## {bench}")
        lines.append("")
        header = ["Model", "Accuracy", "Scored/Total", "Extractor"] + extra_keys
        lines.append("| " + " | ".join(header) + " |")
        lines.append("| " + " | ".join(["---"] * len(header)) + " |")
        for r in rows:
            cells = [
                r["model"],
                _fmt_acc(r["accuracy"]),
                f"{r['scored']}/{r['total']}",
                r["extractor_model"] or "—",
            ]
            for k in extra_keys:
                v = r["extra"].get(k)
                cells.append("—" if v is None else (f"{v:.3f}" if isinstance(v, float) else str(v)))
            lines.append("| " + " | ".join(cells) + " |")
        lines.append("")
    return "\n".join(lines)


def render_html(results: dict[str, list[dict[str, Any]]]) -> str:
    def esc(x: Any) -> str:
        return html.escape(str(x))

    parts = [
        "<!doctype html><html lang='zh'><head><meta charset='utf-8'>",
        "<title>Cross-model eval comparison</title>",
        "<style>",
        "body{font:14px/1.5 -apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;"
        "margin:2rem auto;max-width:1000px;color:#222;padding:0 1rem}",
        "h1{margin-bottom:.2rem}h2{margin-top:2rem;border-bottom:2px solid #eee;padding-bottom:.3rem}",
        ".note{color:#666}",
        "table{border-collapse:collapse;width:100%;margin:.5rem 0 1.5rem}",
        "th,td{border:1px solid #ddd;padding:.4rem .6rem;text-align:left}",
        "th{background:#f7f7f7}tr:nth-child(even) td{background:#fafafa}",
        "td.num{text-align:right;font-variant-numeric:tabular-nums}",
        ".best td{font-weight:600}",
        "</style></head><body>",
        "<h1>Cross-model eval comparison</h1>",
        "<p class='note'>Per-benchmark, side-by-side. Accuracy is not comparable across "
        "benchmarks and is never averaged together.</p>",
    ]
    for bench in sorted(results):
        rows = _rows(results[bench])
        extra_keys = sorted({k for r in rows for k in r["extra"]})
        parts.append(f"<h2>{esc(bench)}</h2><table>")
        header = ["Model", "Accuracy", "Scored/Total", "Extractor"] + extra_keys
        parts.append("<tr>" + "".join(f"<th>{esc(h)}</th>" for h in header) + "</tr>")
        for i, r in enumerate(rows):
            cls = " class='best'" if i == 0 and r["accuracy"] is not None else ""
            cells = [
                f"<td>{esc(r['model'])}</td>",
                f"<td class='num'>{esc(_fmt_acc(r['accuracy']))}</td>",
                f"<td class='num'>{esc(r['scored'])}/{esc(r['total'])}</td>",
                f"<td>{esc(r['extractor_model'] or '—')}</td>",
            ]
            for k in extra_keys:
                v = r["extra"].get(k)
                txt = "—" if v is None else (f"{v:.3f}" if isinstance(v, float) else str(v))
                cells.append(f"<td class='num'>{esc(txt)}</td>")
            parts.append(f"<tr{cls}>" + "".join(cells) + "</tr>")
        parts.append("</table>")
    parts.append("</body></html>")
    return "".join(parts)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--eval-dir", type=Path, default=ROOT / "reports" / "eval")
    parser.add_argument("--out-dir", type=Path, default=None, help="default: <eval-dir>/_aggregate")
    args = parser.parse_args()

    eval_dir = args.eval_dir
    out_dir = args.out_dir or (eval_dir / AGGREGATE_DIRNAME)
    out_dir.mkdir(parents=True, exist_ok=True)

    results = collect(eval_dir)
    if not results:
        print(f"no summaries found under {eval_dir}")
        return

    (out_dir / "index.md").write_text(render_markdown(results) + "\n", encoding="utf-8")
    (out_dir / "index.html").write_text(render_html(results) + "\n", encoding="utf-8")

    n_models = sum(len(v) for v in results.values())
    print(f"aggregated {len(results)} benchmarks, {n_models} model-runs -> {out_dir / 'index.html'}")
    for bench in sorted(results):
        models = ", ".join(s.get("model", "?") for s in results[bench])
        print(f"  {bench}: {models}")


if __name__ == "__main__":
    main()
