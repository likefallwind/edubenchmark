"""Where a judged run's results live, and how to recognise that layout.

Every run scored by an LLM judge is stored under a directory that names the
judge::

    reports/eval/<benchmark>/judge-<judge-slug>/<model-slug>/

This is unconditional: the default judge gets a directory too.  The earlier
scheme wrote the default judge's runs to a bare ``<benchmark>/<model>/`` and
only named alternate judges (as ``_judge-<slug>/``), which meant a path could
not be read without knowing which judge was the default *at the time the run
was made* — untenable once several judges are in rotation.

Rule-scored benchmarks have no judge and keep the two-level
``<benchmark>/<model>/`` shape; ``judge-none`` would be noise.

The leading underscore was dropped deliberately.  In this repo ``_`` prefixes
mean "not a model result — skip me", and every collector honours that; a judge
namespace is the opposite, it holds ordinary results that must stay visible.
``is_judge_dir`` still recognises the legacy ``_judge-`` spelling so a stray
old directory is never mistaken for a model.
"""

from __future__ import annotations

from pathlib import Path

from .providers import model_slug

PREFIX = "judge-"
LEGACY_PREFIX = "_judge-"


def judge_dir_name(judge_model: str) -> str:
    """Directory name for a judge, e.g. ``judge-minimax3``."""
    return f"{PREFIX}{model_slug(judge_model)}"


def is_judge_dir(name: str) -> bool:
    """True for a judge namespace directory, current or legacy spelling."""
    return name.startswith(PREFIX) or name.startswith(LEGACY_PREFIX)


def judge_of_dir(name: str) -> str | None:
    """The judge slug a namespace directory names, or None if it is not one."""
    if name.startswith(PREFIX):
        return name[len(PREFIX):]
    if name.startswith(LEGACY_PREFIX):
        return name[len(LEGACY_PREFIX):]
    return None


def find_judge_dir(benchmark_dir: Path, judge_model: str) -> Path:
    """The directory holding ``judge_model``'s runs for one benchmark.

    Returns the current-spelling path; if only a legacy ``_judge-`` directory is
    present on disk, returns that instead, so a not-yet-migrated checkout keeps
    reading results rather than silently finding none.
    """
    current = benchmark_dir / judge_dir_name(judge_model)
    if current.is_dir():
        return current
    legacy = benchmark_dir / f"{LEGACY_PREFIX}{model_slug(judge_model)}"
    if legacy.is_dir():
        return legacy
    return current


def iter_run_dirs(benchmark_dir: Path):
    """Every run directory under one benchmark: bare model dirs plus the
    contents of each judge namespace.  Variant trees (``_noimage``, ``_smoke``,
    ``_stale``, ...) keep their leading underscore and are NOT descended into —
    callers that want them must ask for them explicitly, exactly as before."""
    if not benchmark_dir.is_dir():
        return
    for child in sorted(benchmark_dir.iterdir()):
        if not child.is_dir():
            continue
        if is_judge_dir(child.name):
            for run in sorted(child.iterdir()):
                if run.is_dir():
                    yield run
        elif not child.name.startswith("_"):
            yield child
