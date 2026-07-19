# Atomic Ability Rebenchmark Artifacts

Date: 2026-07-08

This directory stores the auditable intermediate artifacts for rebuilding the
education rebenchmark around `doc/atomic_ability_principle_audit_v3.md`.

Files:

- `01_inclusion_policy.md`: what is included/excluded from the main scoring layer.
- `02_benchmark_ability_mapping.jsonl`: machine-readable benchmark/subdimension to P01-P22 mapping.
- `02_benchmark_ability_mapping.md`: human-readable mapping table for review.
- `03_metric_normalization.md`: normalization and aggregation rules before any radar chart.
- `04_eval_run_inventory.jsonl`: current `reports/eval/**/summary.json` inventory with inclusion flags.
- `04_eval_run_inventory.md`: compact inventory summary.
- `05_otherbenchmark_score_inventory.jsonl`: parsed score rows from `otherbenchmark/`.
- `05_otherbenchmark_score_inventory.md`: compact parsed-score summary.
- `06_open_calibration_questions.md`: remaining decisions that should be reviewed before final HTML scoring.
- `07_run_deduplication_report.jsonl`: duplicate/canonical scoring decisions.
- `07_run_deduplication_report.md`: human-readable duplicate/canonical scoring decisions.
- `08_selected_score_evidence.jsonl`: canonical normalized benchmark score rows used for P scoring.
- `09_atomic_p_scores.jsonl`: per-model P01-P20 scores (single R20 scheme: relevance × confidence weights, no tier factor).
- `09_atomic_p_scores.md`: compact per-model P score table and coverage notes.
- `10_group_scores.jsonl`: SRG/FDR/LAD/CLM/CEG aggregate scores from available P scores.
- `10_group_scores.md`: compact group-score table.
- `11_atomic_ability_rebenchmark_report.html`: self-contained interactive HTML report.
- `12_benchmark_priority_analysis.jsonl`: benchmark/subdimension priority analysis for deciding what to keep, downweight, or skip.
- `12_benchmark_priority_report.html`: self-contained HTML triage report for benchmark portfolio decisions.
- `12_benchmark_portfolio_review.md`: Markdown-first two-indicator benchmark review table.

The final HTML should be generated only after the mapping and inclusion policy
are calibrated. Small-sample runs and judge-calibration runs are excluded from
the main scoring layer by default.
