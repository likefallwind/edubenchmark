# Open Calibration Questions

Resolved in this pass:

- `foundation_gate` contributes to SRG/FDR through P-level scores at reduced effective weight.
- EduGuard P2 uses `deepseek-v3.2` judge as primary.
- BEA/MRBench judge tasks are excluded.
- EduIllustrate full-230 runs are included; 5-item runs are excluded.
- MiniMax-M3 canonical policy prefers included `minimax3/` or fuller-scored runs.

Remaining review points:

1. The v3 atomic list has `P01-P22`; there is no `P0`. If the request meant a specific ability, confirm whether it means `P01` or another P code.
2. Current evidence may still be sparse or absent for `P04`, `P08`, `P09`, `P15`, and `P19`. Confirm whether to leave them blank/low-coverage or add proxy mappings.
3. `P21/P22` are covered mainly by EduGuard safety evidence. Confirm whether that is sufficient, or whether to require student-risk-specific datasets.
4. For cross-model comparison, decide whether to add a strict `common-evidence` mode that only compares models on shared benchmark/subdimension coverage.
