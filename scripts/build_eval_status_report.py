#!/usr/bin/env python3
"""Rebuild the eval progress matrix at ``doc/eval_status_<date>.md``.

Scans ``reports/eval/<benchmark>/<model>/`` for ``summary.json`` /
``predictions.jsonl`` and reports ``scored (or judged) / total_items`` per
benchmark x model. Idempotent: rerun after any eval run finishes and it
regenerates the whole table from what's on disk, no hand edits.

The five "full-scale" core models (see doc/roadmap_to_convincing_eval_2026-07-12.md
line 24, "主测 5 个模型") get a dedicated gap section listing which benchmarks
they are missing or incomplete on.

Usage:
    python scripts/build_eval_status_report.py --date 2026-07-21
    python scripts/build_eval_status_report.py --date 2026-07-21 --prev doc/eval_status_2026-07-17.md --rename
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVAL_DIR = ROOT / "reports" / "eval"

SKIP_TOP_DIRS = {"_aggregate", "_audit", "_judge_jury", "_judge_rubric"}
DATE_DIR_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

# Canonicalize model directory names that refer to the same model under
# different spellings across benchmarks.
CANONICAL_MODEL = {
    "minimax3": "MiniMax-M3",
    "minimax-m3": "MiniMax-M3",
    "MiniMax-M3": "MiniMax-M3",
    "minimax-m2.7": "MiniMax-M2.7",
    "MiniMax-M2.7": "MiniMax-M2.7",
    "doubao-seed-2-0-pro-260215": "doubao-seed-2.0-pro",
    "doubao-seed-2.0-pro": "doubao-seed-2.0-pro",
}

# The five models this repo currently treats as the full-scale main panel.
CORE_5_MODELS = [
    "MiniMax-M3",
    "MiniMax-M2.7",
    "deepseek-v4-pro",
    "glm-5.2",
    "doubao-seed-2.0-pro",
]


def canon(name: str) -> str:
    return CANONICAL_MODEL.get(name, name)


def read_counts(summary_path: Path) -> tuple[int | None, int | None]:
    try:
        data = json.loads(summary_path.read_text())
    except Exception:
        return None, None
    scored = data.get("scored", data.get("judged"))
    total = data.get("total_items", data.get("total"))
    return scored, total


def scan() -> dict[str, dict[str, tuple[str, int | None, int | None]]]:
    """benchmark -> canonical_model -> (state, scored, total).

    state is one of "scored", "predictions_only". Legacy date-named run dirs
    (model identity ambiguous, predate per-model directories) are skipped.
    """
    matrix: dict[str, dict[str, tuple[str, int | None, int | None]]] = {}
    for bdir in sorted(EVAL_DIR.iterdir()):
        if not bdir.is_dir() or bdir.name in SKIP_TOP_DIRS:
            continue
        bench = bdir.name
        row: dict[str, tuple[str, int | None, int | None]] = {}
        for mdir in sorted(bdir.iterdir()):
            if not mdir.is_dir() or mdir.name.startswith("_"):
                continue
            if DATE_DIR_RE.match(mdir.name):
                continue
            summary = mdir / "summary.json"
            preds = mdir / "predictions.jsonl"
            if summary.exists():
                scored, total = read_counts(summary)
                if scored is None:
                    continue
                row[canon(mdir.name)] = ("scored", scored, total)
            elif preds.exists():
                row[canon(mdir.name)] = ("predictions_only", None, None)
        if bench == "edubench":
            # The colleague-imported deepseek-v3.2-judged run under
            # _judge-deepseek-v3.2/<model>/ is the only full-scale (3797-item)
            # edubench data on disk today; bare reports/eval/edubench/<model>/
            # dirs are small smoke tests. Merge it in as the primary count,
            # matching the convention the 2026-07-17 report used.
            judge_dir = bdir / "_judge-deepseek-v3.2"
            if judge_dir.is_dir():
                for mdir in sorted(judge_dir.iterdir()):
                    if not mdir.is_dir():
                        continue
                    summary = mdir / "summary.json"
                    if not summary.exists():
                        continue
                    scored, total = read_counts(summary)
                    if scored is None:
                        continue
                    key = canon(mdir.name)
                    existing = row.get(key)
                    if existing is None or (existing[2] or 0) < (total or 0):
                        row[key] = ("scored", scored, total)
        if row:
            matrix[bench] = row
    return matrix


def cell(entry: tuple[str, int | None, int | None] | None) -> str:
    if entry is None:
        return "-/-"
    state, scored, total = entry
    if state == "predictions_only":
        return "predictions only"
    return f"{scored}/{total}"


def build_main_table(matrix: dict[str, dict[str, tuple]], models: list[str]) -> str:
    header = "| 评测任务（纵轴） \\ 模型（横轴） | " + " | ".join(models) + " |"
    sep = "|---" * (len(models) + 1) + "|"
    lines = [header, sep]
    for bench in sorted(matrix):
        row = matrix[bench]
        cells = [cell(row.get(m)) for m in models]
        lines.append(f"|{bench}|" + "|".join(cells) + "|")
    return "\n".join(lines)


def build_gap_section(matrix: dict[str, dict[str, tuple]]) -> str:
    lines = []
    for bench in sorted(matrix):
        row = matrix[bench]
        missing = []
        incomplete = []
        for m in CORE_5_MODELS:
            entry = row.get(m)
            if entry is None:
                missing.append(m)
            elif entry[0] == "predictions_only":
                missing.append(f"{m}（仅 predictions，无 summary）")
            elif entry[2] and entry[1] != entry[2]:
                incomplete.append(f"{m}:{entry[1]}/{entry[2]}")
        if missing or incomplete:
            parts = []
            if missing:
                parts.append("缺: " + "、".join(missing))
            if incomplete:
                parts.append("不完整: " + "、".join(incomplete))
            lines.append(f"- **{bench}** — " + "；".join(parts))
    if not lines:
        return "（5 个核心模型在所有已发现的评测任务上都已跑满。）"
    return "\n".join(lines)


def all_models(matrix: dict[str, dict[str, tuple]]) -> list[str]:
    seen: set[str] = set()
    for row in matrix.values():
        seen.update(row.keys())
    ordered = [m for m in CORE_5_MODELS if m in seen]
    ordered += sorted(m for m in seen if m not in CORE_5_MODELS)
    return ordered


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--date", required=True, help="report date, e.g. 2026-07-21")
    args = parser.parse_args()

    matrix = scan()
    models = all_models(matrix)

    out_path = ROOT / "doc" / f"eval_status_{args.date}.md"
    body = f"""# 评测进度总览（截至 {args.date}）

说明：

- 纵轴是评测任务（benchmark），横轴是模型（按 `reports/eval/` 现存目录动态发现，不再固定 12 模型口径；同一模型的不同目录拼写已归一，如 `minimax3`/`minimax-m3` → `MiniMax-M3`）。
- `-/-` 表示该模型在该评测下尚无 `summary.json`，也无 `predictions.jsonl` 产出（含内容为空的占位目录）。
- `predictions only` 表示仅有 `predictions.jsonl`，无 `summary.json`。
- `x/y` 表示 `summary.json` 中 `scored`（或 `judged`）与 `total_items`（或 `total`）比对。
- 统计口径：按本仓库内 `reports/eval/*/*/summary.json`（或 `predictions.jsonl`）可见产物直接统计；跳过 `_` 前缀的裁判/分析/归档子目录（如 `_judge-*`、`_stale`、`_analysis`）以及早期无模型名的日期目录（`2026-06-0x/`，模型身份不明）。
- 前 5 列是当前的核心全量模型面（见 `doc/roadmap_to_convincing_eval_2026-07-12.md` "主测 5 个模型"）：MiniMax-M3、MiniMax-M2.7、deepseek-v4-pro、glm-5.2、doubao-seed-2.0-pro。
- `edubench` 行是例外：`reports/eval/edubench/<model>/` 下目前只有零星 smoke 测试（如 glm-5.2 的 5/5），真正的全量 3797 题数据在 `_judge-deepseek-v3.2/<model>/`（colleague 导入、裁判为 deepseek-v3.2），本表按历史口径把它合并进对应模型列展示。

## 主表

{build_main_table(matrix, models)}

## 5 个核心全量模型的缺口

{build_gap_section(matrix)}
"""
    out_path.write_text(body)
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
