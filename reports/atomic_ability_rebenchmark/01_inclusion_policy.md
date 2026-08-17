# Inclusion Policy

## Main scoring layer

Include a model-run only when all conditions hold:

1. It is a benchmark/model result, not a judge calibration, jury calibration, rubric prompt experiment, or backup copy.
2. It has a concrete model name and a non-zero `total_items`.
3. It has at least 100 total items, unless a human explicitly promotes the run after inspection.
4. It maps to at least one `P01-P20` ability through `02_benchmark_ability_mapping.jsonl`.
5. If multiple judge versions score the same model responses, keep only the selected primary judge in the main scoring layer and keep the others as context rows.

## Excluded by default

- Small samples and smoke tests: `total_items < 100`.
- Judge/rubric calibration: paths under `_judge_rubric`, `_judge_jury`, and benchmark ids containing `judge_calibration`.
- Backup directories such as `selfjudge_backup_*`.
- Protocol-only/data-resource rows without model scores.
- BEA/MRBench judge tasks: `bea2025_judge` and `mrbench_judge` are excluded in this pass. Tutor-generation tasks remain eligible.
- EduGuard P2 rows not judged by `deepseek-v3.2` are excluded from the repo scoring layer and preserved only as context.

## General-benchmark handling (R20)

MMLU-Pro, C-EVAL, AGIEval, OlympiadBench, and MathTutorBench problem-solving
style results map mostly to `P04` and `P05` (knowledge and reasoning), where
answering IS the construct. The former foundation-gate ×0.45 tier factor was
removed in R20: high answer accuracy still cannot dominate the education-side
abilities because general benchmarks are simply not mounted on education Ps.
Since R25 the guardrail is carried entirely by that structural constraint plus
per-cell relevance — confidence is rule-derived and no longer discounts a
benchmark for being general, so these exam-style benchmarks sit at 1.0
(objective scoring + externally vetted data).

EduIllustrate full-230 runs are included when `total_items >= 100`; 5-item
smoke/calibration runs remain excluded.
