"""Single read/write entry point for per-run `predictions.jsonl`.

Large benchmarks produce prediction files that exceed GitHub's 100 MB
per-file hard limit. To keep the files in git (colleagues clone them) and
still push, oversized predictions are transparently split into plain-text
shards:

    predictions.jsonl          <- shard 1 (also the base name; always <= limit)
    predictions.part2.jsonl    <- shard 2
    predictions.part3.jsonl    <- ...

Every reader goes through `read_predictions()` and every whole-file writer
through `write_predictions()`, so the on-disk format (sharding today, gzip
tomorrow) lives in exactly one place. The runner's hot loop appends row by row
via `append_prediction()` for crash-safety, which rolls to the next shard as
soon as one would exceed the limit; `write_predictions()` then re-packs
authoritatively at the end of the run.

Keeping every shard under the limit *during* the run is deliberate: a run that
is interrupted, killed, or simply committed while still in flight never gets to
the end-of-run re-pack, and an oversized file left behind blocks `git push`.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Iterable

try:  # imported as `eval.predictions_io`
    from .report import append_jsonl, read_jsonl
except ImportError:  # run as a standalone script from inside scripts/eval/
    from report import append_jsonl, read_jsonl  # type: ignore

# 90 MiB, a 10 MB margin under GitHub's 100 MB per-file hard limit.
_SHARD_LIMIT = 90 * 1024 * 1024
_SUFFIX = ".jsonl"


def _base_path(path_or_dir: Path | str) -> Path:
    """Normalize a run dir or a base path to the shard-1 (`predictions.jsonl`) path."""
    p = Path(path_or_dir)
    if p.suffix == _SUFFIX:
        return p
    return p / "predictions.jsonl"


def _shard_path(base: Path, n: int) -> Path:
    if n == 1:
        return base
    stem = base.name[: -len(_SUFFIX)]
    return base.with_name(f"{stem}.part{n}{_SUFFIX}")


def _numbered_shards(base: Path) -> list[tuple[int, Path]]:
    """Return `(shard_number, path)` for existing shards, ascending (part10 after part9)."""
    stem = base.name[: -len(_SUFFIX)]
    found: list[tuple[int, Path]] = []
    if base.exists():
        found.append((1, base))
    part_re = re.compile(rf"^{re.escape(stem)}\.part(\d+){re.escape(_SUFFIX)}$")
    parent = base.parent
    if parent.exists():
        for f in parent.glob(f"{stem}.part*{_SUFFIX}"):
            m = part_re.match(f.name)
            if m:
                found.append((int(m.group(1)), f))
    found.sort(key=lambda t: t[0])
    return found


def _existing_shards(base: Path) -> list[Path]:
    """Return existing shard files in ascending numeric order (part10 after part9)."""
    return [f for _, f in _numbered_shards(base)]


def read_predictions(path_or_dir: Path | str) -> list[dict[str, Any]]:
    """Read a (possibly sharded) predictions file. Accepts a run dir or base path."""
    base = _base_path(path_or_dir)
    rows: list[dict[str, Any]] = []
    for shard in _existing_shards(base):
        rows.extend(read_jsonl(shard))
    return rows


def predictions_exist(path_or_dir: Path | str) -> bool:
    """True if any non-empty prediction shard exists (base or a part)."""
    return any(s.stat().st_size > 0 for s in _existing_shards(_base_path(path_or_dir)))


def write_predictions(path_or_dir: Path | str, rows: Iterable[dict[str, Any]]) -> list[Path]:
    """Authoritative whole-file write: drop stale shards, then write `rows` split
    across as many shards as needed to keep each under the size limit. Returns the
    shard paths written."""
    base = _base_path(path_or_dir)
    base.parent.mkdir(parents=True, exist_ok=True)
    for stale in _existing_shards(base):
        stale.unlink()

    written: list[Path] = []
    shard_idx = 1
    path = _shard_path(base, shard_idx)
    fh = path.open("w", encoding="utf-8")
    written.append(path)
    size = 0
    try:
        for row in rows:
            line = json.dumps(row, ensure_ascii=False) + "\n"
            nbytes = len(line.encode("utf-8"))
            # Roll to a new shard before writing a line that would overflow the
            # current one (but never leave a shard empty — a single >limit line
            # still goes alone, which never happens for real predictions).
            if size > 0 and size + nbytes > _SHARD_LIMIT:
                fh.close()
                shard_idx += 1
                path = _shard_path(base, shard_idx)
                fh = path.open("w", encoding="utf-8")
                written.append(path)
                size = 0
            fh.write(line)
            size += nbytes
    finally:
        fh.close()
    return written


def append_prediction(path_or_dir: Path | str, row: dict[str, Any]) -> None:
    """Crash-safe incremental append to the tail of a (possibly sharded) run.

    Appends to the highest-numbered existing shard (or the base if none exist)
    so the row lands at the true end of the read sequence. This preserves the
    single-file invariant that reruns rely on: a freshly re-run item is read
    *after* any stale errored copy left in an earlier shard, so last-wins keeps
    the good row.

    The tail shard is rolled to the next number before it would exceed the size
    limit, so *every* shard is under the limit at every point in the run, not
    just after `write_predictions` re-packs at the end. Without that, a run
    killed or interrupted part-way (or committed while still running) leaves an
    oversized file behind that git cannot push. Rolling keeps the read order
    intact because the new shard is the highest-numbered one and is therefore
    read last.
    """
    base = _base_path(path_or_dir)
    shards = _numbered_shards(base)
    number, target = shards[-1] if shards else (1, base)
    nbytes = len(json.dumps(row, ensure_ascii=False).encode("utf-8")) + 1
    size = target.stat().st_size if target.exists() else 0
    if size > 0 and size + nbytes > _SHARD_LIMIT:
        target = _shard_path(base, number + 1)
    append_jsonl(target, row)


def _pack(path: Path | str) -> list[Path]:
    """Read an existing (possibly single-file) predictions path and rewrite it as
    size-limited shards. Idempotent; used to pack pre-existing oversized files."""
    base = _base_path(path)
    rows = read_predictions(base)
    return write_predictions(base, rows)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("usage: python scripts/eval/predictions_io.py <predictions.jsonl|run_dir> ...")
        raise SystemExit(2)
    for arg in sys.argv[1:]:
        shards = _pack(arg)
        total = sum(s.stat().st_size for s in shards)
        print(f"{arg} -> {len(shards)} shard(s), {total / 1024 / 1024:.1f} MiB total")
        for s in shards:
            print(f"    {s}  ({s.stat().st_size / 1024 / 1024:.1f} MiB)")
