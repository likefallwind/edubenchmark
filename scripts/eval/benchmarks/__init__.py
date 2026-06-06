"""Benchmark adapters and their registry.

Add a new benchmark by creating ``eval/benchmarks/<name>.py`` with a
``BenchmarkAdapter`` subclass and registering it below.
"""

from __future__ import annotations

from ..base import BenchmarkAdapter
from .mathvista import MathVistaAdapter


_REGISTRY: dict[str, type[BenchmarkAdapter]] = {
    MathVistaAdapter.name: MathVistaAdapter,
}


def get_adapter(name: str) -> BenchmarkAdapter:
    if name not in _REGISTRY:
        available = ", ".join(sorted(_REGISTRY)) or "(none)"
        raise SystemExit(f"Unknown benchmark '{name}'. Available: {available}")
    return _REGISTRY[name]()


def available_benchmarks() -> list[str]:
    return sorted(_REGISTRY)
