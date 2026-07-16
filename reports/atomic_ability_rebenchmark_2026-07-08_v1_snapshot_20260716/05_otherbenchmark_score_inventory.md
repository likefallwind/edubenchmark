# Otherbenchmark Score Inventory

Parsed score rows: 199

## By Score Role

| Role | Rows |
|---|---:|
| `legacy_context` | 95 |
| `scoring_candidate` | 104 |

`scoring_candidate` rows are eligible for the P-score layer. `legacy_context` rows are stored for audit only.

## By Benchmark

| Benchmark | Rows |
|---|---:|
| `asap_2` | 7 |
| `edubench` | 66 |
| `eduguard_adversarial` | 24 |
| `eduguard_sata` | 13 |
| `legacy_radar_0701` | 40 |
| `pedagogy_benchmark` | 7 |
| `sas_bench` | 36 |
| `tutorbench` | 6 |

## By Metric

| Metric | Rows |
|---|---:|
| `accuracy_percent` | 7 |
| `asr_0_to_1_lower_better` | 24 |
| `legacy_axis_0_to_100` | 40 |
| `mean_0_to_10` | 66 |
| `qwk_0_to_100` | 19 |
| `rfs_0_to_1` | 6 |
| `score_0_to_100` | 37 |

## Sample Rows

| Benchmark | Role | Subdimension | Model | Metric | Raw value | Notes |
|---|---|---|---|---|---:|---|
| `asap_2` | `scoring_candidate` | essay holistic QWK | Claude Sonnet 4.6 | `qwk_0_to_100` | 61.06 | parsed from 0701 summary card |
| `asap_2` | `scoring_candidate` | essay holistic QWK | DeepSeek-V4-Flash | `qwk_0_to_100` | 50.78 | parsed from 0701 summary card |
| `asap_2` | `scoring_candidate` | essay holistic QWK | DeepSeek-V4-Pro | `qwk_0_to_100` | 52.32 | parsed from 0701 summary card |
| `asap_2` | `scoring_candidate` | essay holistic QWK | GLM-5.1 | `qwk_0_to_100` | 57.25 | parsed from 0701 summary card |
| `asap_2` | `scoring_candidate` | essay holistic QWK | GPT-5.4 | `qwk_0_to_100` | 47.26 | parsed from 0701 summary card |
| `asap_2` | `scoring_candidate` | essay holistic QWK | MiniMax-M2.7 | `qwk_0_to_100` | 52.77 | parsed from 0701 summary card |
| `asap_2` | `scoring_candidate` | essay holistic QWK | Qwen3.7-Max | `qwk_0_to_100` | 60.03 | parsed from 0701 summary card |
| `edubench` | `scoring_candidate` | IP idea provision / heuristic answer | claude-sonnet-4-6 | `mean_0_to_10` | 8.502 |  |
| `edubench` | `scoring_candidate` | IP idea provision / heuristic answer | deepseek-v4-flash | `mean_0_to_10` | 8.156 |  |
| `edubench` | `scoring_candidate` | IP idea provision / heuristic answer | deepseek-v4-pro | `mean_0_to_10` | 8.202 |  |
| `edubench` | `scoring_candidate` | IP idea provision / heuristic answer | doubao-seed-2.0-lite | `mean_0_to_10` | 8.332 |  |
| `edubench` | `scoring_candidate` | IP idea provision / heuristic answer | doubao-seed-2.0-pro | `mean_0_to_10` | 8.665 |  |
| `edubench` | `scoring_candidate` | IP idea provision / heuristic answer | glm-5.1 | `mean_0_to_10` | 7.598 |  |
| `edubench` | `scoring_candidate` | IP idea provision / heuristic answer | kimi-k2.6 | `mean_0_to_10` | 7.983 |  |
| `edubench` | `scoring_candidate` | IP idea provision / heuristic answer | minimax-m2.7 | `mean_0_to_10` | 8.21 |  |
| `edubench` | `scoring_candidate` | IP idea provision / heuristic answer | minimax-m3 | `mean_0_to_10` | 8.62 |  |
| `edubench` | `scoring_candidate` | IP idea provision / heuristic answer | qwen3-14b | `mean_0_to_10` | 7.8 |  |
| `edubench` | `scoring_candidate` | IP idea provision / heuristic answer | qwen3.5-122b-a10b | `mean_0_to_10` | 8.388 |  |
| `edubench` | `scoring_candidate` | PCC pedagogical/personalized content creation | claude-sonnet-4-6 | `mean_0_to_10` | 9.177 |  |
| `edubench` | `scoring_candidate` | PCC pedagogical/personalized content creation | deepseek-v4-flash | `mean_0_to_10` | 9.467 |  |
| `edubench` | `scoring_candidate` | PCC pedagogical/personalized content creation | deepseek-v4-pro | `mean_0_to_10` | 8.428 |  |
| `edubench` | `scoring_candidate` | PCC pedagogical/personalized content creation | doubao-seed-2.0-lite | `mean_0_to_10` | 9.206 |  |
| `edubench` | `scoring_candidate` | PCC pedagogical/personalized content creation | doubao-seed-2.0-pro | `mean_0_to_10` | 9.535 |  |
| `edubench` | `scoring_candidate` | PCC pedagogical/personalized content creation | glm-5.1 | `mean_0_to_10` | 8.432 |  |
| `edubench` | `scoring_candidate` | PCC pedagogical/personalized content creation | kimi-k2.6 | `mean_0_to_10` | 8.854 |  |
| `edubench` | `scoring_candidate` | PCC pedagogical/personalized content creation | minimax-m2.7 | `mean_0_to_10` | 8.609 |  |
| `edubench` | `scoring_candidate` | PCC pedagogical/personalized content creation | minimax-m3 | `mean_0_to_10` | 9.131 |  |
| `edubench` | `scoring_candidate` | PCC pedagogical/personalized content creation | qwen3-14b | `mean_0_to_10` | 7.676 |  |
| `edubench` | `scoring_candidate` | PCC pedagogical/personalized content creation | qwen3.5-122b-a10b | `mean_0_to_10` | 8.319 |  |
| `edubench` | `scoring_candidate` | PLS personalized learning support | claude-sonnet-4-6 | `mean_0_to_10` | 9.081 |  |
| `edubench` | `scoring_candidate` | PLS personalized learning support | deepseek-v4-flash | `mean_0_to_10` | 9.194 |  |
| `edubench` | `scoring_candidate` | PLS personalized learning support | deepseek-v4-pro | `mean_0_to_10` | 8.591 |  |
| `edubench` | `scoring_candidate` | PLS personalized learning support | doubao-seed-2.0-lite | `mean_0_to_10` | 9.128 |  |
| `edubench` | `scoring_candidate` | PLS personalized learning support | doubao-seed-2.0-pro | `mean_0_to_10` | 9.437 |  |
| `edubench` | `scoring_candidate` | PLS personalized learning support | glm-5.1 | `mean_0_to_10` | 8.089 |  |
| `edubench` | `scoring_candidate` | PLS personalized learning support | kimi-k2.6 | `mean_0_to_10` | 8.899 |  |
| `edubench` | `scoring_candidate` | PLS personalized learning support | minimax-m2.7 | `mean_0_to_10` | 8.806 |  |
| `edubench` | `scoring_candidate` | PLS personalized learning support | minimax-m3 | `mean_0_to_10` | 8.905 |  |
| `edubench` | `scoring_candidate` | PLS personalized learning support | qwen3-14b | `mean_0_to_10` | 7.694 |  |
| `edubench` | `scoring_candidate` | PLS personalized learning support | qwen3.5-122b-a10b | `mean_0_to_10` | 8.348 |  |

Full parsed rows are in `05_otherbenchmark_score_inventory.jsonl`.
