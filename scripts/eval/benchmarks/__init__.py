"""Benchmark adapters and their registry.

Add a new benchmark by creating ``eval/benchmarks/<name>.py`` with a
``BenchmarkAdapter`` subclass and registering it below.
"""

from __future__ import annotations

from ..base import BenchmarkAdapter
from .agieval import AGIEvalAdapter
from .ceval import CEvalAdapter
from .eduguard_bench import EduGuardAdversarialAdapter, EduGuardSATAAdapter
from .mathtutorbench import (
    MTBJudgeCalibration,
    MTBMistakeCorrection,
    MTBMistakeLocation,
    MTBPedagogy,
    MTBPedagogyHard,
    MTBProblemSolving,
    MTBScaffolding,
    MTBScaffoldingHard,
    MTBSocratic,
    MTBSolutionCorrectness,
)
from .mathvista import MathVistaAdapter
from .mmlu_pro import MMLUProAdapter
from .olympiadbench import OlympiadBenchAdapter


_ADAPTERS: list[type[BenchmarkAdapter]] = [
    MathVistaAdapter,
    MMLUProAdapter,
    AGIEvalAdapter,
    CEvalAdapter,
    OlympiadBenchAdapter,
    EduGuardSATAAdapter,
    EduGuardAdversarialAdapter,
    # MathTutorBench: judge calibration first, then the 9 tasks.
    MTBJudgeCalibration,
    MTBProblemSolving,
    MTBSocratic,
    MTBSolutionCorrectness,
    MTBMistakeLocation,
    MTBMistakeCorrection,
    MTBScaffolding,
    MTBPedagogy,
    MTBScaffoldingHard,
    MTBPedagogyHard,
]

_REGISTRY: dict[str, type[BenchmarkAdapter]] = {a.name: a for a in _ADAPTERS}


def get_adapter(name: str) -> BenchmarkAdapter:
    if name not in _REGISTRY:
        available = ", ".join(sorted(_REGISTRY)) or "(none)"
        raise SystemExit(f"Unknown benchmark '{name}'. Available: {available}")
    return _REGISTRY[name]()


def available_benchmarks() -> list[str]:
    return sorted(_REGISTRY)
