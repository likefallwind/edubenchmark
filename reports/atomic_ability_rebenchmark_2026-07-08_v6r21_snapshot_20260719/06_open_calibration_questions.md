# Open Calibration Questions

Resolved in this pass:

- R20: the four-level evidence-tier system is removed; scoring weight = relevance × confidence only.
- R20: P codes renumbered to the doc scheme `P01-P20` (no tombstones).
- EduGuard P2 uses `deepseek-v3.2` judge as primary.
- BEA/MRBench judge tasks are excluded (EXCLUDED_SCORING_BENCHMARKS + zero confidence weight + cell `excluded` marker).
- EduIllustrate full-230 runs are included; 5-item runs are excluded.
- MiniMax-M3 canonical policy prefers included `minimax3/` or fuller-scored runs.

Remaining review points:

1. `P08` (tool use / long-horizon) and `P20` (academic integrity) are declared domain gaps (report them honestly as uncovered); `P16`/`P14` are single-source reference values and `P12` covers 2 of 4 declared sub-abilities.
2. `P17-P19` are covered mainly by EduGuard safety evidence. Confirm whether that is sufficient, or whether to require student-risk-specific datasets.
3. For cross-model comparison, decide whether to add a strict `common-evidence` mode that only compares models on shared benchmark/subdimension coverage.
