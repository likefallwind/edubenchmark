# Open Calibration Questions

Resolved in this pass:

- `foundation_gate` contributes to SRG/FDR through P-level scores at reduced effective weight.
- EduGuard P2 uses `deepseek-v3.2` judge as primary.
- BEA/MRBench judge tasks are excluded.
- EduIllustrate full-230 runs are included; 5-item runs are excluded.
- MiniMax-M3 canonical policy prefers included `minimax3/` or fuller-scored runs.

Remaining review points:

1. The atomic list spans `P01-P22` with tombstones `P04` (into P03) and `P12`/`P13` (into P11, R17); there is no `P0`. If the request meant a specific ability, confirm whether it means `P01` or another P code.
2. `P09` and `P15` are declared domain gaps under mapping v3 (report them honestly as uncovered); `P10`/`P19` are single-source reference values and `P16` covers 2 of 4 declared sub-abilities.
3. `P21/P22` are covered mainly by EduGuard safety evidence. Confirm whether that is sufficient, or whether to require student-risk-specific datasets.
4. For cross-model comparison, decide whether to add a strict `common-evidence` mode that only compares models on shared benchmark/subdimension coverage.
