# Selected Score Evidence

Canonical normalized score rows used for P scoring: 179

## By Source

| Source | Rows |
|---|---:|
| `otherbenchmark` | 93 |
| `repo_eval` | 86 |

## By Benchmark

| Benchmark | Rows |
|---|---:|
| `agieval` | 5 |
| `asap_2` | 7 |
| `bea2025_tutor` | 3 |
| `ceval` | 5 |
| `edubench` | 55 |
| `eduguard_adversarial` | 7 |
| `eduguard_sata` | 8 |
| `eduillustrate` | 3 |
| `mathtutorbench_mistake_correction` | 5 |
| `mathtutorbench_mistake_location` | 5 |
| `mathtutorbench_pedagogy` | 6 |
| `mathtutorbench_pedagogy_hard` | 6 |
| `mathtutorbench_problem_solving` | 4 |
| `mathtutorbench_scaffolding` | 7 |
| `mathtutorbench_scaffolding_hard` | 7 |
| `mathtutorbench_solution_correctness` | 5 |
| `mathvista` | 1 |
| `mmlu_pro` | 5 |
| `mrbench_tutor` | 2 |
| `olympiadbench` | 2 |
| `pedagogy_benchmark` | 7 |
| `sas_bench` | 18 |
| `tutorbench` | 6 |

## Sample Rows

| Benchmark | Model key | Metric | Raw | Score 0-10 | Source |
|---|---|---|---:|---:|---|
| `asap_2` | `claude-sonnet-4.6` | `qwk_0_to_100` | 61.06 | 6.1060 | `otherbenchmark/rebenchmark-summary-0701.html` |
| `edubench` | `claude-sonnet-4.6` | `mean_0_to_10` | 8.502 | 8.5020 | `otherbenchmark/edubench-0625.md` |
| `edubench` | `claude-sonnet-4.6` | `mean_0_to_10` | 9.177 | 9.1770 | `otherbenchmark/edubench-0625.md` |
| `edubench` | `claude-sonnet-4.6` | `mean_0_to_10` | 9.081 | 9.0810 | `otherbenchmark/edubench-0625.md` |
| `edubench` | `claude-sonnet-4.6` | `mean_0_to_10` | 8.887 | 8.8870 | `otherbenchmark/edubench-0625.md` |
| `edubench` | `claude-sonnet-4.6` | `mean_0_to_10` | 8.966 | 8.9660 | `otherbenchmark/edubench-0625.md` |
| `pedagogy_benchmark` | `claude-sonnet-4.6` | `accuracy_percent` | 84.9 | 8.4900 | `otherbenchmark/rebenchmark-summary-0701.html` |
| `agieval` | `deepseek-v4-flash` | `accuracy` | 0.8936726272352132 | 8.9367 | `reports/eval/agieval/deepseek-v4-flash/summary.json` |
| `asap_2` | `deepseek-v4-flash` | `qwk_0_to_100` | 50.78 | 5.0780 | `otherbenchmark/rebenchmark-summary-0701.html` |
| `ceval` | `deepseek-v4-flash` | `accuracy` | 0.921875 | 9.2188 | `reports/eval/ceval/deepseek-v4-flash/summary.json` |
| `edubench` | `deepseek-v4-flash` | `mean_0_to_10` | 8.156 | 8.1560 | `otherbenchmark/edubench-0625.md` |
| `edubench` | `deepseek-v4-flash` | `mean_0_to_10` | 9.467 | 9.4670 | `otherbenchmark/edubench-0625.md` |
| `edubench` | `deepseek-v4-flash` | `mean_0_to_10` | 9.194 | 9.1940 | `otherbenchmark/edubench-0625.md` |
| `edubench` | `deepseek-v4-flash` | `mean_0_to_10` | 8.912 | 8.9120 | `otherbenchmark/edubench-0625.md` |
| `edubench` | `deepseek-v4-flash` | `mean_0_to_10` | 9.231 | 9.2310 | `otherbenchmark/edubench-0625.md` |
| `mathtutorbench_mistake_correction` | `deepseek-v4-flash` | `accuracy` | 0.9171656686626747 | 9.1717 | `reports/eval/mathtutorbench_mistake_correction/deepseek-v4-flash/summary.json` |
| `mathtutorbench_mistake_location` | `deepseek-v4-flash` | `accuracy_or_f1` | 0.774 | 7.7400 | `reports/eval/mathtutorbench_mistake_location/deepseek-v4-flash/summary.json` |
| `mathtutorbench_pedagogy` | `deepseek-v4-flash` | `win_rate_or_accuracy` | 0.7712 | 7.7120 | `reports/eval/mathtutorbench_pedagogy/deepseek-v4-flash/summary.json` |
| `mathtutorbench_pedagogy_hard` | `deepseek-v4-flash` | `win_rate_or_accuracy` | 0.7365 | 7.3650 | `reports/eval/mathtutorbench_pedagogy_hard/deepseek-v4-flash/summary.json` |
| `mathtutorbench_problem_solving` | `deepseek-v4-flash` | `accuracy` | 0.9742228961334344 | 9.7422 | `reports/eval/mathtutorbench_problem_solving/deepseek-v4-flash/summary.json` |
| `mathtutorbench_scaffolding` | `deepseek-v4-flash` | `win_rate_or_accuracy` | 0.15 | 1.5000 | `reports/eval/mathtutorbench_scaffolding/deepseek-v4-flash/summary.json` |
| `mathtutorbench_scaffolding_hard` | `deepseek-v4-flash` | `win_rate_or_accuracy` | 0.1667 | 1.6670 | `reports/eval/mathtutorbench_scaffolding_hard/deepseek-v4-flash/summary.json` |
| `mathtutorbench_solution_correctness` | `deepseek-v4-flash` | `accuracy_or_f1` | 0.8567 | 8.5670 | `reports/eval/mathtutorbench_solution_correctness/deepseek-v4-flash/summary.json` |
| `mmlu_pro` | `deepseek-v4-flash` | `accuracy` | 0.8590799434323267 | 8.5908 | `reports/eval/mmlu_pro/deepseek-v4-flash/summary.json` |
| `pedagogy_benchmark` | `deepseek-v4-flash` | `accuracy_percent` | 85.7 | 8.5700 | `otherbenchmark/rebenchmark-summary-0701.html` |
| `agieval` | `deepseek-v4-pro` | `accuracy` | 0.9019526952695269 | 9.0195 | `reports/eval/agieval/deepseek-v4-pro/summary.json` |
| `asap_2` | `deepseek-v4-pro` | `qwk_0_to_100` | 52.32 | 5.2320 | `otherbenchmark/rebenchmark-summary-0701.html` |
| `ceval` | `deepseek-v4-pro` | `accuracy` | 0.9383358098068351 | 9.3834 | `reports/eval/ceval/deepseek-v4-pro/summary.json` |
| `edubench` | `deepseek-v4-pro` | `mean_0_to_10` | 8.202 | 8.2020 | `otherbenchmark/edubench-0625.md` |
| `edubench` | `deepseek-v4-pro` | `mean_0_to_10` | 8.428 | 8.4280 | `otherbenchmark/edubench-0625.md` |
| `edubench` | `deepseek-v4-pro` | `mean_0_to_10` | 8.591 | 8.5910 | `otherbenchmark/edubench-0625.md` |
| `edubench` | `deepseek-v4-pro` | `mean_0_to_10` | 7.925 | 7.9250 | `otherbenchmark/edubench-0625.md` |
| `edubench` | `deepseek-v4-pro` | `mean_0_to_10` | 7.581 | 7.5810 | `otherbenchmark/edubench-0625.md` |
| `eduguard_adversarial` | `deepseek-v4-pro` | `asr_0_to_1_lower_better` | 0.6241 | 3.7590 | `reports/eval/eduguard_adversarial/_judge-deepseek-v3.2/deepseek-v4-pro/summary.json` |
| `eduguard_sata` | `deepseek-v4-pro` | `rfs_0_to_1` | 0.7612 | 7.6120 | `reports/eval/eduguard_sata/deepseek-v4-pro/summary.json` |
| `mathtutorbench_mistake_correction` | `deepseek-v4-pro` | `accuracy` | 0.9201596806387226 | 9.2016 | `reports/eval/mathtutorbench_mistake_correction/deepseek-v4-pro/summary.json` |
| `mathtutorbench_mistake_location` | `deepseek-v4-pro` | `accuracy_or_f1` | 0.765 | 7.6500 | `reports/eval/mathtutorbench_mistake_location/deepseek-v4-pro/summary.json` |
| `mathtutorbench_pedagogy` | `deepseek-v4-pro` | `win_rate_or_accuracy` | 0.8522 | 8.5220 | `reports/eval/mathtutorbench_pedagogy/deepseek-v4-pro/summary.json` |
| `mathtutorbench_pedagogy_hard` | `deepseek-v4-pro` | `win_rate_or_accuracy` | 0.8659 | 8.6590 | `reports/eval/mathtutorbench_pedagogy_hard/deepseek-v4-pro/summary.json` |
| `mathtutorbench_scaffolding` | `deepseek-v4-pro` | `win_rate_or_accuracy` | 0.5547 | 5.5470 | `reports/eval/mathtutorbench_scaffolding/deepseek-v4-pro/summary.json` |
| `mathtutorbench_scaffolding_hard` | `deepseek-v4-pro` | `win_rate_or_accuracy` | 0.4121 | 4.1210 | `reports/eval/mathtutorbench_scaffolding_hard/deepseek-v4-pro/summary.json` |
| `mathtutorbench_solution_correctness` | `deepseek-v4-pro` | `accuracy_or_f1` | 0.8621 | 8.6210 | `reports/eval/mathtutorbench_solution_correctness/deepseek-v4-pro/summary.json` |
| `mmlu_pro` | `deepseek-v4-pro` | `accuracy` | 0.8740851630073186 | 8.7409 | `reports/eval/mmlu_pro/deepseek-v4-pro/summary.json` |
| `olympiadbench` | `deepseek-v4-pro` | `accuracy` | 0.8527538403896591 | 8.5275 | `reports/eval/olympiadbench/deepseek-v4-pro/summary.json` |
| `pedagogy_benchmark` | `deepseek-v4-pro` | `accuracy_percent` | 85.34 | 8.5340 | `otherbenchmark/rebenchmark-summary-0701.html` |
| `sas_bench` | `deepseek-v4-pro` | `score_0_to_100` | 76.63 | 7.6630 | `otherbenchmark/sas-bench-result0630.md` |
| `sas_bench` | `deepseek-v4-pro` | `score_0_to_100` | 61.69 | 6.1690 | `otherbenchmark/sas-bench-result0630.md` |
| `sas_bench` | `deepseek-v4-pro` | `qwk_0_to_100` | 81.86 | 8.1860 | `otherbenchmark/sas-bench-result0630.md` |
| `edubench` | `doubao-seed-2-0-lite` | `mean_0_to_10` | 8.332 | 8.3320 | `otherbenchmark/edubench-0625.md` |
| `edubench` | `doubao-seed-2-0-lite` | `mean_0_to_10` | 9.206 | 9.2060 | `otherbenchmark/edubench-0625.md` |
| `edubench` | `doubao-seed-2-0-lite` | `mean_0_to_10` | 9.128 | 9.1280 | `otherbenchmark/edubench-0625.md` |
| `edubench` | `doubao-seed-2-0-lite` | `mean_0_to_10` | 8.627 | 8.6270 | `otherbenchmark/edubench-0625.md` |
| `edubench` | `doubao-seed-2-0-lite` | `mean_0_to_10` | 8.846 | 8.8460 | `otherbenchmark/edubench-0625.md` |
| `eduguard_adversarial` | `doubao-seed-2-0-lite` | `asr_0_to_1_lower_better` | 0.5112 | 4.8880 | `reports/eval/eduguard_adversarial/_judge-deepseek-v3.2/doubao-seed-2.0-lite/summary.json` |
| `eduguard_sata` | `doubao-seed-2-0-lite` | `rfs_0_to_1` | 0.73 | 7.3000 | `reports/eval/eduguard_sata/doubao-seed-2.0-lite/summary.json` |
| `eduillustrate` | `doubao-seed-2-0-lite` | `likert_0_to_5` | 3.3885 | 6.7770 | `reports/eval/eduillustrate/doubao-seed-2.0-lite__gen-full230_judge-minimax3/summary.json` |
| `mathtutorbench_pedagogy` | `doubao-seed-2-0-lite` | `win_rate_or_accuracy` | 0.8646 | 8.6460 | `reports/eval/mathtutorbench_pedagogy/doubao-seed-2.0-lite/summary.json` |
| `mathtutorbench_pedagogy_hard` | `doubao-seed-2-0-lite` | `win_rate_or_accuracy` | 0.8045 | 8.0450 | `reports/eval/mathtutorbench_pedagogy_hard/doubao-seed-2.0-lite/summary.json` |
| `mathtutorbench_scaffolding` | `doubao-seed-2-0-lite` | `win_rate_or_accuracy` | 0.2537 | 2.5370 | `reports/eval/mathtutorbench_scaffolding/doubao-seed-2.0-lite/summary.json` |
| `mathtutorbench_scaffolding_hard` | `doubao-seed-2-0-lite` | `win_rate_or_accuracy` | 0.204 | 2.0400 | `reports/eval/mathtutorbench_scaffolding_hard/doubao-seed-2.0-lite/summary.json` |
| `edubench` | `doubao-seed-2-0-pro` | `mean_0_to_10` | 8.665 | 8.6650 | `otherbenchmark/edubench-0625.md` |
| `edubench` | `doubao-seed-2-0-pro` | `mean_0_to_10` | 9.535 | 9.5350 | `otherbenchmark/edubench-0625.md` |
| `edubench` | `doubao-seed-2-0-pro` | `mean_0_to_10` | 9.437 | 9.4370 | `otherbenchmark/edubench-0625.md` |
| `edubench` | `doubao-seed-2-0-pro` | `mean_0_to_10` | 8.865 | 8.8650 | `otherbenchmark/edubench-0625.md` |
| `edubench` | `doubao-seed-2-0-pro` | `mean_0_to_10` | 9.197 | 9.1970 | `otherbenchmark/edubench-0625.md` |
| `eduguard_adversarial` | `doubao-seed-2-0-pro` | `asr_0_to_1_lower_better` | 0.6025 | 3.9750 | `reports/eval/eduguard_adversarial/_judge-deepseek-v3.2/doubao-seed-2.0-pro/summary.json` |
| `eduguard_sata` | `doubao-seed-2-0-pro` | `rfs_0_to_1` | 0.7618 | 7.6180 | `reports/eval/eduguard_sata/doubao-seed-2.0-pro/summary.json` |
| `mathtutorbench_pedagogy` | `doubao-seed-2-0-pro` | `win_rate_or_accuracy` | 0.8767 | 8.7670 | `reports/eval/mathtutorbench_pedagogy/doubao-seed-2.0-pro/summary.json` |
| `mathtutorbench_pedagogy_hard` | `doubao-seed-2-0-pro` | `win_rate_or_accuracy` | 0.8688 | 8.6880 | `reports/eval/mathtutorbench_pedagogy_hard/doubao-seed-2.0-pro/summary.json` |
| `mathtutorbench_scaffolding` | `doubao-seed-2-0-pro` | `win_rate_or_accuracy` | 0.3843 | 3.8430 | `reports/eval/mathtutorbench_scaffolding/doubao-seed-2.0-pro/summary.json` |
| `mathtutorbench_scaffolding_hard` | `doubao-seed-2-0-pro` | `win_rate_or_accuracy` | 0.3881 | 3.8810 | `reports/eval/mathtutorbench_scaffolding_hard/doubao-seed-2.0-pro/summary.json` |
| `asap_2` | `glm-5.1` | `qwk_0_to_100` | 57.25 | 5.7250 | `otherbenchmark/rebenchmark-summary-0701.html` |
| `edubench` | `glm-5.1` | `mean_0_to_10` | 7.598 | 7.5980 | `otherbenchmark/edubench-0625.md` |
| `edubench` | `glm-5.1` | `mean_0_to_10` | 8.432 | 8.4320 | `otherbenchmark/edubench-0625.md` |
| `edubench` | `glm-5.1` | `mean_0_to_10` | 8.089 | 8.0890 | `otherbenchmark/edubench-0625.md` |
| `edubench` | `glm-5.1` | `mean_0_to_10` | 8.137 | 8.1370 | `otherbenchmark/edubench-0625.md` |
| `edubench` | `glm-5.1` | `mean_0_to_10` | 6.178 | 6.1780 | `otherbenchmark/edubench-0625.md` |
| `eduguard_adversarial` | `glm-5.1` | `asr_0_to_1_lower_better` | 0.0492 | 9.5080 | `reports/eval/eduguard_adversarial/_judge-deepseek-v3.2/glm-5.1/summary.json` |
| `eduguard_sata` | `glm-5.1` | `rfs_0_to_1` | 0.7632 | 7.6320 | `reports/eval/eduguard_sata/glm-5.1/summary.json` |
| `pedagogy_benchmark` | `glm-5.1` | `accuracy_percent` | 87.67 | 8.7670 | `otherbenchmark/rebenchmark-summary-0701.html` |

Full selected rows are in `08_selected_score_evidence.jsonl`.
