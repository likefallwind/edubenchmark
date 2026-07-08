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
- `06_open_calibration_questions.md`: decisions that should be reviewed before final HTML scoring.

The final HTML should be generated only after the mapping and inclusion policy
are calibrated. Small-sample runs and judge-calibration runs are excluded from
the main scoring layer by default.
