# Otherbenchmark Score Inventory

Parsed score rows: 394

## By Score Role

| Role | Rows |
|---|---:|
| `legacy_context` | 157 |
| `scoring_candidate` | 237 |

`scoring_candidate` rows are eligible for the P-score layer. `legacy_context` rows are stored for audit only.

## By Benchmark

| Benchmark | Rows |
|---|---:|
| `asap_2` | 7 |
| `edubench` | 261 |
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
| `likert_0_to_10` | 195 |
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
| `edubench` | `legacy_context` | IP idea provision / heuristic answer | claude-sonnet-4-6 | `mean_0_to_10` | 8.502 | v1 任务级均分；映射 v2（R1）改按指标级取分后仅作上下文保留 |
| `edubench` | `legacy_context` | IP idea provision / heuristic answer | deepseek-v4-flash | `mean_0_to_10` | 8.156 | v1 任务级均分；映射 v2（R1）改按指标级取分后仅作上下文保留 |
| `edubench` | `legacy_context` | IP idea provision / heuristic answer | deepseek-v4-pro | `mean_0_to_10` | 8.202 | v1 任务级均分；映射 v2（R1）改按指标级取分后仅作上下文保留 |
| `edubench` | `legacy_context` | IP idea provision / heuristic answer | doubao-seed-2.0-lite | `mean_0_to_10` | 8.332 | v1 任务级均分；映射 v2（R1）改按指标级取分后仅作上下文保留 |
| `edubench` | `legacy_context` | IP idea provision / heuristic answer | doubao-seed-2.0-pro | `mean_0_to_10` | 8.665 | v1 任务级均分；映射 v2（R1）改按指标级取分后仅作上下文保留 |
| `edubench` | `legacy_context` | IP idea provision / heuristic answer | glm-5.1 | `mean_0_to_10` | 7.598 | v1 任务级均分；映射 v2（R1）改按指标级取分后仅作上下文保留 |
| `edubench` | `legacy_context` | IP idea provision / heuristic answer | kimi-k2.6 | `mean_0_to_10` | 7.983 | v1 任务级均分；映射 v2（R1）改按指标级取分后仅作上下文保留 |
| `edubench` | `legacy_context` | IP idea provision / heuristic answer | minimax-m2.7 | `mean_0_to_10` | 8.21 | v1 任务级均分；映射 v2（R1）改按指标级取分后仅作上下文保留 |
| `edubench` | `legacy_context` | IP idea provision / heuristic answer | minimax-m3 | `mean_0_to_10` | 8.62 | v1 任务级均分；映射 v2（R1）改按指标级取分后仅作上下文保留 |
| `edubench` | `legacy_context` | IP idea provision / heuristic answer | qwen3-14b | `mean_0_to_10` | 7.8 | v1 任务级均分；映射 v2（R1）改按指标级取分后仅作上下文保留 |
| `edubench` | `legacy_context` | IP idea provision / heuristic answer | qwen3.5-122b-a10b | `mean_0_to_10` | 8.388 | v1 任务级均分；映射 v2（R1）改按指标级取分后仅作上下文保留 |
| `edubench` | `legacy_context` | PCC pedagogical/personalized content creation | claude-sonnet-4-6 | `mean_0_to_10` | 9.177 | v1 任务级均分；映射 v2（R1）改按指标级取分后仅作上下文保留 |
| `edubench` | `legacy_context` | PCC pedagogical/personalized content creation | deepseek-v4-flash | `mean_0_to_10` | 9.467 | v1 任务级均分；映射 v2（R1）改按指标级取分后仅作上下文保留 |
| `edubench` | `legacy_context` | PCC pedagogical/personalized content creation | deepseek-v4-pro | `mean_0_to_10` | 8.428 | v1 任务级均分；映射 v2（R1）改按指标级取分后仅作上下文保留 |
| `edubench` | `legacy_context` | PCC pedagogical/personalized content creation | doubao-seed-2.0-lite | `mean_0_to_10` | 9.206 | v1 任务级均分；映射 v2（R1）改按指标级取分后仅作上下文保留 |
| `edubench` | `legacy_context` | PCC pedagogical/personalized content creation | doubao-seed-2.0-pro | `mean_0_to_10` | 9.535 | v1 任务级均分；映射 v2（R1）改按指标级取分后仅作上下文保留 |
| `edubench` | `legacy_context` | PCC pedagogical/personalized content creation | glm-5.1 | `mean_0_to_10` | 8.432 | v1 任务级均分；映射 v2（R1）改按指标级取分后仅作上下文保留 |
| `edubench` | `legacy_context` | PCC pedagogical/personalized content creation | kimi-k2.6 | `mean_0_to_10` | 8.854 | v1 任务级均分；映射 v2（R1）改按指标级取分后仅作上下文保留 |
| `edubench` | `legacy_context` | PCC pedagogical/personalized content creation | minimax-m2.7 | `mean_0_to_10` | 8.609 | v1 任务级均分；映射 v2（R1）改按指标级取分后仅作上下文保留 |
| `edubench` | `legacy_context` | PCC pedagogical/personalized content creation | minimax-m3 | `mean_0_to_10` | 9.131 | v1 任务级均分；映射 v2（R1）改按指标级取分后仅作上下文保留 |
| `edubench` | `legacy_context` | PCC pedagogical/personalized content creation | qwen3-14b | `mean_0_to_10` | 7.676 | v1 任务级均分；映射 v2（R1）改按指标级取分后仅作上下文保留 |
| `edubench` | `legacy_context` | PCC pedagogical/personalized content creation | qwen3.5-122b-a10b | `mean_0_to_10` | 8.319 | v1 任务级均分；映射 v2（R1）改按指标级取分后仅作上下文保留 |
| `edubench` | `legacy_context` | PLS personalized learning support | claude-sonnet-4-6 | `mean_0_to_10` | 9.081 | v1 任务级均分；映射 v2（R1）改按指标级取分后仅作上下文保留 |
| `edubench` | `legacy_context` | PLS personalized learning support | deepseek-v4-flash | `mean_0_to_10` | 9.194 | v1 任务级均分；映射 v2（R1）改按指标级取分后仅作上下文保留 |
| `edubench` | `legacy_context` | PLS personalized learning support | deepseek-v4-pro | `mean_0_to_10` | 8.591 | v1 任务级均分；映射 v2（R1）改按指标级取分后仅作上下文保留 |
| `edubench` | `legacy_context` | PLS personalized learning support | doubao-seed-2.0-lite | `mean_0_to_10` | 9.128 | v1 任务级均分；映射 v2（R1）改按指标级取分后仅作上下文保留 |
| `edubench` | `legacy_context` | PLS personalized learning support | doubao-seed-2.0-pro | `mean_0_to_10` | 9.437 | v1 任务级均分；映射 v2（R1）改按指标级取分后仅作上下文保留 |
| `edubench` | `legacy_context` | PLS personalized learning support | glm-5.1 | `mean_0_to_10` | 8.089 | v1 任务级均分；映射 v2（R1）改按指标级取分后仅作上下文保留 |
| `edubench` | `legacy_context` | PLS personalized learning support | kimi-k2.6 | `mean_0_to_10` | 8.899 | v1 任务级均分；映射 v2（R1）改按指标级取分后仅作上下文保留 |
| `edubench` | `legacy_context` | PLS personalized learning support | minimax-m2.7 | `mean_0_to_10` | 8.806 | v1 任务级均分；映射 v2（R1）改按指标级取分后仅作上下文保留 |
| `edubench` | `legacy_context` | PLS personalized learning support | minimax-m3 | `mean_0_to_10` | 8.905 | v1 任务级均分；映射 v2（R1）改按指标级取分后仅作上下文保留 |
| `edubench` | `legacy_context` | PLS personalized learning support | qwen3-14b | `mean_0_to_10` | 7.694 | v1 任务级均分；映射 v2（R1）改按指标级取分后仅作上下文保留 |
| `edubench` | `legacy_context` | PLS personalized learning support | qwen3.5-122b-a10b | `mean_0_to_10` | 8.348 | v1 任务级均分；映射 v2（R1）改按指标级取分后仅作上下文保留 |

Full parsed rows are in `05_otherbenchmark_score_inventory.jsonl`.
