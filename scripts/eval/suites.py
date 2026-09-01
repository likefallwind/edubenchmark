"""Selection-suite paths and manifests shared by runners and materializers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .base import ROOT
from .judge_dirs import judge_dir_name


SUITES = ("full", "mini_v2", "frontier_v1")
SELECTION_SUITES = SUITES[1:]
SUITE_DATA_DIRS = {
    "mini_v2": ROOT / "data" / "mini_selection_v2",
    "frontier_v1": ROOT / "data" / "frontier_selection_v1",
}
SUITE_RESULT_ROOT = ROOT / "reports" / "eval_suites"


def load_manifest(suite: str) -> dict[str, Any]:
    if suite not in SELECTION_SUITES:
        raise ValueError(f"selection suite required, got {suite!r}")
    return json.loads((SUITE_DATA_DIRS[suite] / "selection_manifest.json").read_text(encoding="utf-8"))


def suite_benchmark(suite: str, benchmark: str) -> dict[str, Any] | None:
    return load_manifest(suite).get("benchmarks", {}).get(benchmark)


def fixed_full_entry(suite: str, benchmark: str) -> dict[str, Any] | None:
    for row in load_manifest(suite).get("fixed_full", []):
        if row.get("benchmark") == benchmark:
            return row
    return None


def suite_item_list(suite: str, benchmark: str) -> Path | None:
    row = suite_benchmark(suite, benchmark)
    return ROOT / row["item_list"] if row else None


def run_dir(
    suite: str,
    benchmark: str,
    model_slug: str,
    judge_model: str | None,
    variant: str | None = None,
) -> Path:
    if suite == "full":
        base = ROOT / "reports" / "eval" / benchmark
    else:
        base = SUITE_RESULT_ROOT / suite / benchmark
    if variant:
        base = base / f"_{variant}"
    if judge_model:
        base = base / judge_dir_name(judge_model)
    return base / model_slug


def federated_run_dirs(
    benchmark: str, model_slug: str, variant: str | None = None
) -> list[Path]:
    """Return existing Full/selection run dirs for this benchmark and model.

    Judge namespaces are deliberately all considered for predictions: a model
    answer is judge-independent. Extraction identity checks decide whether a
    judged/extracted row is reusable.
    """
    bases = [ROOT / "reports" / "eval" / benchmark]
    bases.extend(SUITE_RESULT_ROOT / suite / benchmark for suite in SELECTION_SUITES)
    found: list[Path] = []
    for base in bases:
        if variant:
            base = base / f"_{variant}"
        direct = base / model_slug
        if direct.is_dir():
            found.append(direct)
        if base.is_dir():
            found.extend(sorted(p / model_slug for p in base.glob("judge-*") if (p / model_slug).is_dir()))
    return list(dict.fromkeys(path.resolve() for path in found))
