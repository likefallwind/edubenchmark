"""Benchmark adapters and their registry.

Add a new benchmark by creating ``eval/benchmarks/<name>.py`` with a
``BenchmarkAdapter`` subclass and registering it below.
"""

from __future__ import annotations

from ..base import BenchmarkAdapter
from .agieval import AGIEvalAdapter
from .bea2025 import BEA2025JudgeAdapter, BEA2025TutorAdapter
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
from .mmtutorbench import MMTutorBenchAdapter, MMTutorBenchJudgeCalibrationAdapter
from .mrbench import MRBenchJudgeAdapter, MRBenchTutorAdapter
from .olympiadbench import OlympiadBenchAdapter
from .p08_abstention import P08AbstentionAdapter
from .p08_calibration import P08CalibrationAdapter


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
    # MRBench: Step 1 judge calibration, then Step 2 generation + judge scoring.
    MRBenchJudgeAdapter,
    MRBenchTutorAdapter,
    # BEA 2025: four shared-task dimensions, dev labels local / test labels hidden.
    BEA2025JudgeAdapter,
    BEA2025TutorAdapter,
    # MMTutorBench: multimodal tutoring generation + fixed rubric judge.
    MMTutorBenchAdapter,
    MMTutorBenchJudgeCalibrationAdapter,
    # P08 calibration: composite over exact-match delegates + verbalized confidence.
    P08CalibrationAdapter,
    # P08 abstention: UMWP unanswerable vs answerable, rule-scored (no judge).
    P08AbstentionAdapter,
]

_REGISTRY: dict[str, type[BenchmarkAdapter]] = {a.name: a for a in _ADAPTERS}


def get_adapter(name: str) -> BenchmarkAdapter:
    if name not in _REGISTRY:
        available = ", ".join(sorted(_REGISTRY)) or "(none)"
        raise SystemExit(f"Unknown benchmark '{name}'. Available: {available}")
    return _REGISTRY[name]()


def available_benchmarks() -> list[str]:
    return sorted(_REGISTRY)
