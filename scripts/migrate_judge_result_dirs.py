#!/usr/bin/env python3
"""One-off migration: make the judge visible in every judged run's directory path.

Old layout (conditional — the canonical judge was invisible)::

    reports/eval/<benchmark>/<model>/                 # judged by MiniMax-M3, unlabelled
    reports/eval/<benchmark>/_judge-<judge>/<model>/  # any other judge

New layout (unconditional, no leading underscore so ordinary collectors see it)::

    reports/eval/<benchmark>/judge-<judge>/<model>/

Rule-scored benchmarks keep the two-level ``<benchmark>/<model>/`` shape: they
have no judge, and inventing a ``judge-none`` level would be noise.

The migration is a pure **path insertion / component rename** — the leaf
directory name (the model slug) is never rewritten, so nothing that keys on the
model slug can drift.  The judge of each run is read from its own artifacts
(``summary.json`` top level, then ``extra_metrics``, then per-item
``extractions.jsonl``), never guessed from the directory name; a run whose judge
cannot be established is reported and left alone.

Usage::

    python3 scripts/migrate_judge_result_dirs.py                 # dry run + manifest
    python3 scripts/migrate_judge_result_dirs.py --apply         # git mv
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

# The judge directory must be named exactly the way the writers will name it,
# aliases included (``model_slug("MiniMax-M3") == "minimax3"``) — a second
# slugging scheme here would silently split one judge across two directories.
from eval.providers import model_slug  # noqa: E402
EVAL_DIR = ROOT / "reports" / "eval"
MANIFEST = EVAL_DIR / "_migration" / "judge_dir_migration_2026-08-28.json"

# Trees that are not per-model benchmark results and must not be touched.
SKIP_BENCHMARKS = {
    "_audit",
    "_aggregate",
    "_baseline",
    "_migration",
    # External pipeline: it names its own dirs ``<model>__gen-fullN_judge-<judge>``
    # and is mid-run for Qwen3.8-27B; renaming would break its resume.
    "eduillustrate",
}

# Sub-trees inside a benchmark that are meta-experiments or parked archives.
SKIP_SEGMENTS = {
    "_judge_rubric",
    "_judge_jury",
    "_judge_swap",
    "_analysis",
    "_metrics",
    "_stale",  # parked archive, already invisible everywhere
}

# Variant markers (``_noimage``, ``_smoke``, ``_sample-v3``, ...) stay ABOVE the
# judge level, matching how eval_benchmark.py composes ``_noimage`` today. Any
# leading-underscore segment that is not the old judge namespace counts as one.
def _is_variant(segment: str) -> bool:
    return segment.startswith("_") and not segment.startswith("_judge-")


def judge_of(run_dir: Path) -> tuple[str | None, str]:
    """(judge model, how it was established) for one run directory."""
    summary = run_dir / "summary.json"
    if not summary.exists():
        return None, "no summary.json"
    try:
        data = json.loads(summary.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None, "summary.json is not valid JSON"

    judge = data.get("judge_model")
    if judge:
        return str(judge), "summary.judge_model"

    extra = data.get("extra_metrics")
    if isinstance(extra, dict) and extra.get("judge_model"):
        return str(extra["judge_model"]), "summary.extra_metrics.judge_model"

    # Per-item records are the authoritative fallback for pre-field runs.
    extractions = run_dir / "extractions.jsonl"
    if extractions.exists():
        with extractions.open(encoding="utf-8") as fh:
            for i, line in enumerate(fh):
                if i > 200:
                    break
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                for candidate in (row, row.get("extracted")):
                    if isinstance(candidate, str):
                        try:
                            candidate = json.loads(candidate)
                        except json.JSONDecodeError:
                            continue
                    if isinstance(candidate, dict) and candidate.get("judge_model"):
                        return str(candidate["judge_model"]), "extractions.jsonl"

    # Self-judging era (2026-06-16 and earlier): the judge was whatever the
    # extractor slot held, which for these backups is the model under test.
    if "selfjudge" in run_dir.name and data.get("extractor_model"):
        return str(data["extractor_model"]), "selfjudge backup: extractor_model"

    return None, "unresolved"


def plan() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    moves: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []

    for summary in sorted(EVAL_DIR.glob("*/**/summary.json")):
        run_dir = summary.parent
        rel = run_dir.relative_to(EVAL_DIR)
        benchmark = rel.parts[0]
        middle = rel.parts[1:]

        if benchmark in SKIP_BENCHMARKS or benchmark.startswith("_"):
            continue
        if any(part in SKIP_SEGMENTS for part in middle):
            skipped.append({"path": str(rel), "reason": "meta-experiment or archive"})
            continue
        if not middle:
            skipped.append({"path": str(rel), "reason": "benchmark home summary, no model dir"})
            continue

        judge, source = judge_of(run_dir)
        if not judge:
            # Rule-scored runs legitimately have no judge; only report the ones
            # that sit under a judge namespace (those should have had one).
            if any(p.startswith(("_judge-", "judge-")) for p in middle):
                skipped.append({"path": str(rel), "reason": f"judge unresolved ({source})"})
            continue

        judge_dir = f"judge-{model_slug(judge)}"
        # 最后一段永远是跑分目录本身（``_m3_fullset_20260723`` 这种带下划线的历史
        # 命名也算），只有它前面的下划线段才是变体层。把末段当变体会算出「把目录
        # 搬进它自己」。
        head, leaf = middle[:-1], middle[-1]
        variants = [p for p in head if _is_variant(p)]
        # Everything that is neither a variant marker nor the old judge namespace
        # is preserved verbatim (model slug, and any nested backup dir).
        tail = [p for p in head if not _is_variant(p) and not p.startswith(("_judge-", "judge-"))] + [leaf]
        new_rel = Path(benchmark, *variants, judge_dir, *tail)

        if new_rel == rel:
            continue
        moves.append(
            {
                "old": str(rel),
                "new": str(new_rel),
                "judge": judge,
                "judge_source": source,
                "model": _model_of(summary),
            }
        )
    return moves, skipped


def _model_of(summary: Path) -> str:
    try:
        return str(json.loads(summary.read_text(encoding="utf-8")).get("model", "?"))
    except json.JSONDecodeError:
        return "?"


def check(moves: list[dict[str, Any]]) -> list[str]:
    """Pre-flight safety checks; returns a list of blocking problems."""
    problems: list[str] = []
    seen: dict[str, str] = {}
    for m in moves:
        if m["new"] in seen:
            problems.append(f"collision: {m['old']} and {seen[m['new']]} both map to {m['new']}")
        seen[m["new"]] = m["old"]
        dest = EVAL_DIR / m["new"]
        if dest.exists():
            problems.append(f"destination already exists: {m['new']}")
        src = EVAL_DIR / m["old"]
        if not src.is_dir():
            problems.append(f"source missing: {m['old']}")
        if Path(m["old"]) in Path(m["new"]).parents:
            problems.append(f"destination is inside its own source: {m['old']} -> {m['new']}")
    # A move whose destination is inside another move's source (or vice versa)
    # would be order-dependent; the insertion-only scheme should never produce one.
    for m in moves:
        for other in moves:
            if m is other:
                continue
            if Path(m["new"]) == Path(other["old"]) or Path(other["old"]) in Path(m["new"]).parents:
                problems.append(f"nested move: {m['old']} -> {m['new']} collides with source {other['old']}")
    return problems


def apply(moves: list[dict[str, Any]]) -> None:
    # Deepest-first so a nested run dir moves before its parent disappears.
    for m in sorted(moves, key=lambda x: len(Path(x["old"]).parts), reverse=True):
        src = EVAL_DIR / m["old"]
        dest = EVAL_DIR / m["new"]
        dest.parent.mkdir(parents=True, exist_ok=True)
        # git mv keeps history for committed results; a never-committed run
        # (eduequity's judge output, for one) has no index entry, so fall back
        # to a plain rename rather than failing the whole migration.
        tracked = subprocess.run(
            ["git", "ls-files", "--error-unmatch", str(src.relative_to(ROOT))],
            cwd=ROOT, capture_output=True,
        ).returncode == 0
        if tracked:
            subprocess.run(["git", "mv", str(src), str(dest)], cwd=ROOT, check=True)
        else:
            src.rename(dest)
        print(f"moved {'git' if tracked else 'fs '} {m['old']} -> {m['new']}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="perform the git mv (default: dry run)")
    args = parser.parse_args()

    moves, skipped = plan()
    problems = check(moves)

    by_bench: dict[str, int] = {}
    for m in moves:
        by_bench[Path(m["old"]).parts[0]] = by_bench.get(Path(m["old"]).parts[0], 0) + 1
    print(f"planned moves: {len(moves)}")
    for b, n in sorted(by_bench.items()):
        print(f"  {b:34s} {n:3d}")
    print(f"\nskipped: {len(skipped)}")
    for s in skipped:
        print(f"  {s['path']:60s} {s['reason']}")
    if problems:
        print(f"\nBLOCKING PROBLEMS ({len(problems)}):")
        for p in problems:
            print(f"  {p}")

    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(
        json.dumps({"moves": moves, "skipped": skipped, "problems": problems}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"\nmanifest: {MANIFEST.relative_to(ROOT)}")

    if args.apply:
        if problems:
            raise SystemExit("refusing to apply with blocking problems")
        apply(moves)


if __name__ == "__main__":
    main()
