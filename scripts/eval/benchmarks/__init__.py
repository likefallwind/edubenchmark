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
from .edubench import EduBenchAdapter
from .ifeval import IFEvalAdapter
from .k12vista import K12VistaAdapter
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
from .longtutor import LongTutorDiagnosisAdapter, LongTutorEvidenceAdapter, LongTutorTeachingAdapter
from .mmtutorbench import MMTutorBenchAdapter, MMTutorBenchJudgeCalibrationAdapter
from .mooccube_prereq import MOOCCubePrereqAdapter
from .mrbench import MRBenchJudgeAdapter, MRBenchTutorAdapter
from .olympiadbench import OlympiadBenchAdapter
from .p07_selfcheck import P07SelfCheckAdapter
from .p08_abstention import P08AbstentionAdapter
from .p08_calibration import P08CalibrationAdapter
from .sas_bench import SASBenchAdapter


_ADAPTERS: list[type[BenchmarkAdapter]] = [
    MathVistaAdapter,
    MMLUProAdapter,
    AGIEvalAdapter,
    CEvalAdapter,
    OlympiadBenchAdapter,
    # IFEval: verifiable instruction following, official rule scoring (P01).
    IFEvalAdapter,
    # K12Vista: Chinese K12 multimodal subject reasoning (P04).
    K12VistaAdapter,
    # MOOCCube: prerequisite reasoning + learning-order sorting, rule-scored (P19).
    MOOCCubePrereqAdapter,
    LongTutorEvidenceAdapter,
    LongTutorDiagnosisAdapter,
    LongTutorTeachingAdapter,
    EduGuardSATAAdapter,
    EduGuardAdversarialAdapter,
    # EduBench: comparable 3,797-prompt generation set + fixed 12-dimension judge.
    EduBenchAdapter,
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
    # P07 self-check: two-round intrinsic self-correction over the P08 delegates.
    P07SelfCheckAdapter,
    # SAS-Bench: model-as-grader, official QWK / CCS / ECS population metrics.
    SASBenchAdapter,
]

_REGISTRY: dict[str, type[BenchmarkAdapter]] = {a.name: a for a in _ADAPTERS}


def get_adapter(name: str) -> BenchmarkAdapter:
    if name not in _REGISTRY:
        available = ", ".join(sorted(_REGISTRY)) or "(none)"
        raise SystemExit(f"Unknown benchmark '{name}'. Available: {available}")
    return _REGISTRY[name]()


def available_benchmarks() -> list[str]:
    return sorted(_REGISTRY)
