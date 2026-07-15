#!/usr/bin/env python3
"""Migrate silent judge-failure sentinels in extraction caches to explicit errors.

Historically the fixed-judge adapters (mrbench_tutor / bea2025_tutor /
mathtutorbench_*) swallowed judge/API failures and baked a sentinel value into
the extraction cache — an ``"unparsed"`` per-dimension label, or a ``null``
win_score. Those rows carried no ``error`` field, so the runner cached them as
successful and scored them as fake fails, and reruns skipped them.

The adapters no longer produce these sentinels (they raise instead), but the
already-written caches still hold them. This one-off, idempotent migration
rewrites each affected ``extractions.jsonl`` in place, converting every limbo
row into a proper error row (``extracted: ""`` + ``error: ...``). After this,
a normal resumable rerun (``run_eval.sh``) treats them as not-done and
re-judges them; anything that still fails stays an error, excluded from the
score, never a fake fail.

Usage:
    python scripts/eval/data/migrate_unparsed_to_error.py            # apply
    python scripts/eval/data/migrate_unparsed_to_error.py --dry-run  # report only
"""

from __future__ import annotations

import argparse
import glob
import json
import os
from typing import Any, Callable

REPORTS_ROOT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
    "reports",
    "eval",
)


def _labels_have_unparsed(payload: Any) -> bool:
    if not isinstance(payload, dict):
        return False
    return any(v == "unparsed" for k, v in payload.items() if k != "judge_model")


def _winscore_is_null(payload: Any) -> bool:
    return isinstance(payload, dict) and "win_score" in payload and payload.get("win_score") is None


# benchmark-dir-name -> (predicate on decoded extracted payload, reason)
# Only the fixed-judge adapters that baked silent sentinels are listed. The
# four mathtutorbench win-rate tasks (subclasses of _WinRateBase) use null
# win_score; the other mathtutorbench tasks are exact-match/reference-scored
# and error correctly through the standard extractor path, so they are excluded.
_UNPARSED_REASON = "judge produced 'unparsed' label(s) (likely failed/empty call)"
_NULLVOTE_REASON = "judge produced null win_score (likely failed/empty vote)"
TARGETS: list[tuple[str, Callable[[Any], bool], str]] = [
    ("mrbench_tutor", _labels_have_unparsed, _UNPARSED_REASON),
    ("bea2025_tutor", _labels_have_unparsed, _UNPARSED_REASON),
    ("mathtutorbench_scaffolding", _winscore_is_null, _NULLVOTE_REASON),
    ("mathtutorbench_pedagogy", _winscore_is_null, _NULLVOTE_REASON),
    ("mathtutorbench_scaffolding_hard", _winscore_is_null, _NULLVOTE_REASON),
    ("mathtutorbench_pedagogy_hard", _winscore_is_null, _NULLVOTE_REASON),
]


def _decode(extracted: Any) -> Any:
    if isinstance(extracted, str):
        try:
            return json.loads(extracted)
        except (json.JSONDecodeError, TypeError):
            return None
    return extracted


def migrate_file(path: str, predicate: Callable[[Any], bool], reason: str, dry_run: bool) -> int:
    out_rows: list[dict[str, Any]] = []
    changed = 0
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            if row.get("error"):
                out_rows.append(row)
                continue
            if predicate(_decode(row.get("extracted"))):
                new_row = {"item_id": row.get("item_id")}
                for keep in ("extractor_model", "extraction_cache_version"):
                    if keep in row:
                        new_row[keep] = row[keep]
                new_row["extracted"] = ""
                new_row["error"] = f"migrated: {reason}; re-judge required"
                out_rows.append(new_row)
                changed += 1
            else:
                out_rows.append(row)
    if changed and not dry_run:
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            for row in out_rows:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
        os.replace(tmp, path)
    return changed


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="report counts without rewriting files")
    args = ap.parse_args()

    grand = 0
    for bench, predicate, reason in TARGETS:
        for path in sorted(glob.glob(os.path.join(REPORTS_ROOT, bench, "*", "extractions.jsonl"))):
            changed = migrate_file(path, predicate, reason, args.dry_run)
            grand += changed
            if changed:
                rel = os.path.relpath(path, REPORTS_ROOT)
                verb = "would convert" if args.dry_run else "converted"
                print(f"  {verb} {changed:5d} limbo rows -> error  ({rel})")
    verb = "Would migrate" if args.dry_run else "Migrated"
    print(f"\n{verb} {grand} limbo rows to error rows across all targets.")


if __name__ == "__main__":
    main()
