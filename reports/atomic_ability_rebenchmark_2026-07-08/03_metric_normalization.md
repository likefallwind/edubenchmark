# Metric Normalization And Aggregation

All benchmark-native metrics are first normalized to a 0-10 scale.

| Metric family | Direction | Rule |
|---|---|---|
| `accuracy_percent` | higher_better | `score_10 = percent / 10` |
| `accuracy` | higher_better | `score_10 = accuracy * 10` |
| `pass_rate` | higher_better | `score_10 = pass_rate * 10` |
| `rfs_0_to_1` | higher_better | `score_10 = rfs * 10` |
| `asr_0_to_1_lower_better` | lower_better | `score_10 = (1 - asr) * 10` |
| `score_0_to_100` | higher_better | `score_10 = raw / 10` |
| `qwk_0_to_100` | higher_better | `score_10 = qwk / 10` |
| `mean_0_to_10` | higher_better | `score_10 = raw` |
| `likert_0_to_10` | higher_better | `score_10 = raw` |
| `likert_0_to_5` | higher_better | `score_10 = raw * 2` |
| `score_0_to_6` | higher_better | `score_10 = raw / 6 * 10` |
| `accuracy_or_f1` | higher_better | `prefer official f1/accuracy in extra_metrics when present; else accuracy * 10` |
| `win_rate_or_accuracy` | higher_better | `prefer win_rate/strict_win_rate when present; else accuracy * 10` |
| `share_0_to_1` | higher_better | `score_10 = share * 10` |
| `legacy_axis_0_to_100` | higher_better | `score_10 = raw / 10; context only, not used for P scoring` |

## Aggregation order

1. Normalize each benchmark subdimension score to 0-10.
2. Allocate that score to P abilities using `02_benchmark_ability_mapping.jsonl` weights.
3. `raw_score_10`: weighted average over evidence rows using default benchmark weights.
4. `tier_adjusted_score_10`: same weighted average after multiplying `foundation_gate` evidence by 0.45.
5. `coverage_adjusted_score_10`: shrink tier-adjusted evidence toward a neutral prior of 5.0 with K=1.0, so sparse P abilities are visible.
6. Report coverage per P ability: number of contributing rows, total effective weight, and benchmark families.
7. Aggregate P abilities to SRG/FDR/LAD/CLM/CEG only after P-level scores are available.

## Resolved scoring choices in this pass

- `foundation_gate` contributes to SRG/FDR through P scores at reduced effective weight.
- EduGuard P2 uses `deepseek-v3.2` judge as the primary scoring judge.
- BEA/MRBench judge tasks are excluded; BEA/MRBench tutor tasks remain eligible.
- EduIllustrate full-230 runs are eligible; small 5-item runs are excluded.
