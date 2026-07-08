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
| `likert_0_to_10` | higher_better | `score_10 = raw` |
| `likert_0_to_5` | higher_better | `score_10 = raw * 2` |
| `score_0_to_6` | higher_better | `score_10 = raw / 6 * 10` |
| `accuracy_or_f1` | higher_better | `prefer official f1/accuracy in extra_metrics when present; else accuracy * 10` |
| `win_rate_or_accuracy` | higher_better | `prefer win_rate/strict_win_rate when present; else accuracy * 10` |
| `share_0_to_1` | higher_better | `score_10 = share * 10` |

## Aggregation order

1. Normalize each benchmark subdimension score to 0-10.
2. Allocate that score to P abilities using `02_benchmark_ability_mapping.jsonl` weights.
3. Within each model and P ability, compute a weighted average over evidence rows.
4. Report coverage per P ability: number of contributing rows, total effective weight, and benchmark families.
5. Aggregate P abilities to SRG/FDR/LAD/CLM/CEG only after P-level scores are available.
6. Display foundation-gate scores separately or with lower weight; do not let answer-only benchmarks dominate education-specific axes.

## Open scoring choices

- Whether to use raw weighted average, coverage-aware shrinkage, or both side by side.
- Whether `foundation_gate` evidence should contribute to the radar at 0.35-0.55 weight or only appear as a separate gate band.
- Which EduGuard P2 judge variant should be primary for final scoring.
