# Selected Score Evidence

Canonical normalized score rows used for P scoring: 820

## By Source

| Source | Rows |
|---|---:|
| `otherbenchmark` | 330 |
| `repo_eval` | 490 |

## By Benchmark

| Benchmark | Rows |
|---|---:|
| `agieval` | 8 |
| `asap_2` | 7 |
| `bea2025_judge` | 9 |
| `bea2025_tutor` | 42 |
| `ceval` | 9 |
| `edubench` | 312 |
| `eduguard_adversarial` | 19 |
| `eduguard_sata` | 10 |
| `eduillustrate` | 6 |
| `ifeval` | 7 |
| `k12vista` | 27 |
| `longtutor_diagnosis` | 7 |
| `longtutor_evidence` | 42 |
| `longtutor_teaching` | 14 |
| `mathtutorbench_mistake_correction` | 8 |
| `mathtutorbench_mistake_location` | 8 |
| `mathtutorbench_pedagogy` | 16 |
| `mathtutorbench_pedagogy_hard` | 16 |
| `mathtutorbench_problem_solving` | 7 |
| `mathtutorbench_scaffolding` | 16 |
| `mathtutorbench_scaffolding_hard` | 16 |
| `mathtutorbench_socratic` | 7 |
| `mathtutorbench_solution_correctness` | 8 |
| `mathvista` | 4 |
| `mmlu_pro` | 8 |
| `mmtutorbench` | 8 |
| `mooccube_prereq` | 7 |
| `mrbench_judge` | 9 |
| `mrbench_tutor` | 70 |
| `olympiadbench` | 10 |
| `p07_selfcheck` | 7 |
| `p08_abstention` | 7 |
| `p08_calibration` | 7 |
| `pedagogy_benchmark` | 26 |
| `sas_bench` | 30 |
| `tutorbench` | 6 |

## Sample Rows

| Benchmark | Model key | Metric | Raw | Score 0-10 | Source |
|---|---|---|---:|---:|---|
| `asap_2` | `claude-sonnet-4.6` | `qwk_0_to_100` | 61.06 | 6.1060 | `otherbenchmark/rebenchmark-summary-0701.html` |
| `edubench` | `claude-sonnet-4.6` | `likert_0_to_10` | 8.043 | 8.0430 | `reports/eval/edubench/_metrics/task_metric_means.jsonl` |
| `edubench` | `claude-sonnet-4.6` | `likert_0_to_10` | 9.5727 | 9.5727 | `reports/eval/edubench/_metrics/task_metric_means.jsonl` |
| `edubench` | `claude-sonnet-4.6` | `likert_0_to_10` | 8.5054 | 8.5054 | `reports/eval/edubench/_metrics/task_metric_means.jsonl` |
| `edubench` | `claude-sonnet-4.6` | `likert_0_to_10` | 9.2902 | 9.2902 | `reports/eval/edubench/_metrics/task_metric_means.jsonl` |
| `edubench` | `claude-sonnet-4.6` | `likert_0_to_10` | 8.5939 | 8.5939 | `reports/eval/edubench/_metrics/task_metric_means.jsonl` |
| `edubench` | `claude-sonnet-4.6` | `likert_0_to_10` | 9.1909 | 9.1909 | `reports/eval/edubench/_metrics/task_metric_means.jsonl` |
| `edubench` | `claude-sonnet-4.6` | `likert_0_to_10` | 6.074 | 6.0740 | `reports/eval/edubench/_metrics/task_metric_means.jsonl` |
| `edubench` | `claude-sonnet-4.6` | `likert_0_to_10` | 7.9773 | 7.9773 | `reports/eval/edubench/_metrics/task_metric_means.jsonl` |
| `edubench` | `claude-sonnet-4.6` | `likert_0_to_10` | 6.424 | 6.4240 | `reports/eval/edubench/_metrics/task_metric_means.jsonl` |
| `edubench` | `claude-sonnet-4.6` | `likert_0_to_10` | 6.3551 | 6.3551 | `reports/eval/edubench/_metrics/task_metric_means.jsonl` |
| `edubench` | `claude-sonnet-4.6` | `likert_0_to_10` | 8.6676 | 8.6676 | `reports/eval/edubench/_metrics/task_metric_means.jsonl` |
| `edubench` | `claude-sonnet-4.6` | `likert_0_to_10` | 7.3948 | 7.3948 | `reports/eval/edubench/_metrics/task_metric_means.jsonl` |
| `pedagogy_benchmark` | `claude-sonnet-4.6` | `accuracy` | 0.8654060066740823 | 8.6541 | `reports/eval/pedagogy_benchmark/claude-sonnet-4-6/summary.json` |
| `pedagogy_benchmark` | `claude-sonnet-4.6` | `accuracy` | 0.7818181818181819 | 7.8182 | `reports/eval/pedagogy_benchmark/claude-sonnet-4-6/summary.json` |
| `pedagogy_benchmark` | `deepseek-r1-0528-qwen3-8b` | `accuracy` | 0.7007786429365962 | 7.0078 | `reports/eval/pedagogy_benchmark/DeepSeek-R1-0528-Qwen3-8B/summary.json` |
| `pedagogy_benchmark` | `deepseek-r1-0528-qwen3-8b` | `accuracy` | 0.6636363636363637 | 6.6364 | `reports/eval/pedagogy_benchmark/DeepSeek-R1-0528-Qwen3-8B/summary.json` |
| `bea2025_judge` | `deepseek-v3-2` | `accuracy` | 0.3687 | 3.6870 | `reports/eval/bea2025_judge/deepseek-v3.2/summary.json` |
| `mrbench_judge` | `deepseek-v3-2` | `accuracy` | 0.4109 | 4.1090 | `reports/eval/mrbench_judge/deepseek-v3.2/summary.json` |
| `agieval` | `deepseek-v4-flash` | `accuracy` | 0.8936726272352132 | 8.9367 | `reports/eval/agieval/deepseek-v4-flash/summary.json` |
| `asap_2` | `deepseek-v4-flash` | `qwk_0_to_100` | 50.78 | 5.0780 | `otherbenchmark/rebenchmark-summary-0701.html` |
| `bea2025_judge` | `deepseek-v4-flash` | `accuracy` | 0.5139 | 5.1390 | `reports/eval/bea2025_judge/deepseek-v4-flash/summary.json` |
| `ceval` | `deepseek-v4-flash` | `accuracy` | 0.921875 | 9.2188 | `reports/eval/ceval/deepseek-v4-flash/summary.json` |
| `edubench` | `deepseek-v4-flash` | `likert_0_to_10` | 8.09 | 8.0900 | `reports/eval/edubench/_metrics/task_metric_means.jsonl` |
| `edubench` | `deepseek-v4-flash` | `likert_0_to_10` | 9.8045 | 9.8045 | `reports/eval/edubench/_metrics/task_metric_means.jsonl` |
| `edubench` | `deepseek-v4-flash` | `likert_0_to_10` | 8.8452 | 8.8452 | `reports/eval/edubench/_metrics/task_metric_means.jsonl` |
| `edubench` | `deepseek-v4-flash` | `likert_0_to_10` | 9.6558 | 9.6558 | `reports/eval/edubench/_metrics/task_metric_means.jsonl` |
| `edubench` | `deepseek-v4-flash` | `likert_0_to_10` | 8.6913 | 8.6913 | `reports/eval/edubench/_metrics/task_metric_means.jsonl` |
| `edubench` | `deepseek-v4-flash` | `likert_0_to_10` | 9.3584 | 9.3584 | `reports/eval/edubench/_metrics/task_metric_means.jsonl` |
| `edubench` | `deepseek-v4-flash` | `likert_0_to_10` | 6.2981 | 6.2981 | `reports/eval/edubench/_metrics/task_metric_means.jsonl` |
| `edubench` | `deepseek-v4-flash` | `likert_0_to_10` | 7.7664 | 7.7664 | `reports/eval/edubench/_metrics/task_metric_means.jsonl` |
| `edubench` | `deepseek-v4-flash` | `likert_0_to_10` | 6.3566 | 6.3566 | `reports/eval/edubench/_metrics/task_metric_means.jsonl` |
| `edubench` | `deepseek-v4-flash` | `likert_0_to_10` | 6.2865 | 6.2865 | `reports/eval/edubench/_metrics/task_metric_means.jsonl` |
| `edubench` | `deepseek-v4-flash` | `likert_0_to_10` | 8.2934 | 8.2934 | `reports/eval/edubench/_metrics/task_metric_means.jsonl` |
| `edubench` | `deepseek-v4-flash` | `likert_0_to_10` | 7.4643 | 7.4643 | `reports/eval/edubench/_metrics/task_metric_means.jsonl` |
| `mathtutorbench_mistake_correction` | `deepseek-v4-flash` | `accuracy` | 0.9171656686626747 | 9.1717 | `reports/eval/mathtutorbench_mistake_correction/deepseek-v4-flash/summary.json` |
| `mathtutorbench_mistake_location` | `deepseek-v4-flash` | `accuracy_or_f1` | 0.774 | 7.7400 | `reports/eval/mathtutorbench_mistake_location/deepseek-v4-flash/summary.json` |
| `mathtutorbench_pedagogy` | `deepseek-v4-flash` | `win_rate_or_accuracy` | 0.7712 | 7.7120 | `reports/eval/mathtutorbench_pedagogy/judge-minimax3/deepseek-v4-flash/summary.json` |
| `mathtutorbench_pedagogy_hard` | `deepseek-v4-flash` | `win_rate_or_accuracy` | 0.7365 | 7.3650 | `reports/eval/mathtutorbench_pedagogy_hard/judge-minimax3/deepseek-v4-flash/summary.json` |
| `mathtutorbench_problem_solving` | `deepseek-v4-flash` | `accuracy` | 0.9742228961334344 | 9.7422 | `reports/eval/mathtutorbench_problem_solving/deepseek-v4-flash/summary.json` |
| `mathtutorbench_scaffolding` | `deepseek-v4-flash` | `win_rate_or_accuracy` | 0.15 | 1.5000 | `reports/eval/mathtutorbench_scaffolding/judge-minimax3/deepseek-v4-flash/summary.json` |
| `mathtutorbench_scaffolding_hard` | `deepseek-v4-flash` | `win_rate_or_accuracy` | 0.1667 | 1.6670 | `reports/eval/mathtutorbench_scaffolding_hard/judge-minimax3/deepseek-v4-flash/summary.json` |
| `mathtutorbench_solution_correctness` | `deepseek-v4-flash` | `accuracy_or_f1` | 0.8567 | 8.5670 | `reports/eval/mathtutorbench_solution_correctness/deepseek-v4-flash/summary.json` |
| `mmlu_pro` | `deepseek-v4-flash` | `accuracy` | 0.8590799434323267 | 8.5908 | `reports/eval/mmlu_pro/deepseek-v4-flash/summary.json` |
| `mrbench_judge` | `deepseek-v4-flash` | `accuracy` | 0.5134 | 5.1340 | `reports/eval/mrbench_judge/deepseek-v4-flash/summary.json` |
| `pedagogy_benchmark` | `deepseek-v4-flash` | `accuracy` | 0.8754171301446051 | 8.7542 | `reports/eval/pedagogy_benchmark/deepseek-v4-flash/summary.json` |
| `pedagogy_benchmark` | `deepseek-v4-flash` | `accuracy` | 0.7818181818181819 | 7.8182 | `reports/eval/pedagogy_benchmark/deepseek-v4-flash/summary.json` |
| `agieval` | `deepseek-v4-pro` | `accuracy` | 0.9019526952695269 | 9.0195 | `reports/eval/agieval/deepseek-v4-pro/summary.json` |
| `asap_2` | `deepseek-v4-pro` | `qwk_0_to_100` | 52.32 | 5.2320 | `otherbenchmark/rebenchmark-summary-0701.html` |
| `bea2025_judge` | `deepseek-v4-pro` | `accuracy` | 0.5374 | 5.3740 | `reports/eval/bea2025_judge/deepseek-v4-pro/summary.json` |
| `bea2025_tutor` | `deepseek-v4-pro` | `share_0_to_1` | 0.9633 | 9.6330 | `reports/eval/bea2025_tutor/judge-deepseek-v4-flash/deepseek-v4-pro/summary.json` |
| `bea2025_tutor` | `deepseek-v4-pro` | `share_0_to_1` | 0.9233 | 9.2330 | `reports/eval/bea2025_tutor/judge-minimax3/deepseek-v4-pro/summary.json` |
| `bea2025_tutor` | `deepseek-v4-pro` | `share_0_to_1` | 0.9467 | 9.4670 | `reports/eval/bea2025_tutor/judge-deepseek-v4-flash/deepseek-v4-pro/summary.json` |
| `bea2025_tutor` | `deepseek-v4-pro` | `share_0_to_1` | 0.9067 | 9.0670 | `reports/eval/bea2025_tutor/judge-minimax3/deepseek-v4-pro/summary.json` |
| `bea2025_tutor` | `deepseek-v4-pro` | `share_0_to_1` | 0.9933 | 9.9330 | `reports/eval/bea2025_tutor/judge-deepseek-v4-flash/deepseek-v4-pro/summary.json` |
| `bea2025_tutor` | `deepseek-v4-pro` | `share_0_to_1` | 0.9767 | 9.7670 | `reports/eval/bea2025_tutor/judge-minimax3/deepseek-v4-pro/summary.json` |
| `ceval` | `deepseek-v4-pro` | `accuracy` | 0.9383358098068351 | 9.3834 | `reports/eval/ceval/deepseek-v4-pro/summary.json` |
| `edubench` | `deepseek-v4-pro` | `likert_0_to_10` | 7.7855 | 7.7855 | `reports/eval/edubench/_metrics/task_metric_means.jsonl` |
| `edubench` | `deepseek-v4-pro` | `likert_0_to_10` | 8.3472 | 8.3472 | `reports/eval/edubench/_metrics/task_metric_means.jsonl` |
| `edubench` | `deepseek-v4-pro` | `likert_0_to_10` | 8.6398 | 8.6398 | `reports/eval/edubench/_metrics/task_metric_means.jsonl` |
| `edubench` | `deepseek-v4-pro` | `likert_0_to_10` | 8.6793 | 8.6793 | `reports/eval/edubench/_metrics/task_metric_means.jsonl` |
| `edubench` | `deepseek-v4-pro` | `likert_0_to_10` | 8.7062 | 8.7062 | `reports/eval/edubench/_metrics/task_metric_means.jsonl` |
| `edubench` | `deepseek-v4-pro` | `likert_0_to_10` | 9.7449 | 9.7449 | `reports/eval/edubench/_metrics/task_metric_means.jsonl` |
| `edubench` | `deepseek-v4-pro` | `likert_0_to_10` | 8.081 | 8.0810 | `reports/eval/edubench/_metrics/task_metric_means.jsonl` |
| `edubench` | `deepseek-v4-pro` | `likert_0_to_10` | 7.8699 | 7.8699 | `reports/eval/edubench/_metrics/task_metric_means.jsonl` |
| `edubench` | `deepseek-v4-pro` | `likert_0_to_10` | 8.5098 | 8.5098 | `reports/eval/edubench/_metrics/task_metric_means.jsonl` |
| `edubench` | `deepseek-v4-pro` | `likert_0_to_10` | 9.0222 | 9.0222 | `reports/eval/edubench/_metrics/task_metric_means.jsonl` |
| `edubench` | `deepseek-v4-pro` | `likert_0_to_10` | 8.7588 | 8.7588 | `reports/eval/edubench/_metrics/task_metric_means.jsonl` |
| `edubench` | `deepseek-v4-pro` | `likert_0_to_10` | 9.7472 | 9.7472 | `reports/eval/edubench/_metrics/task_metric_means.jsonl` |
| `edubench` | `deepseek-v4-pro` | `likert_0_to_10` | 7.8095 | 7.8095 | `reports/eval/edubench/_metrics/task_metric_means.jsonl` |
| `edubench` | `deepseek-v4-pro` | `likert_0_to_10` | 8.1962 | 8.1962 | `reports/eval/edubench/_metrics/task_metric_means.jsonl` |
| `edubench` | `deepseek-v4-pro` | `likert_0_to_10` | 8.482 | 8.4820 | `reports/eval/edubench/_metrics/task_metric_means.jsonl` |
| `edubench` | `deepseek-v4-pro` | `likert_0_to_10` | 8.4238 | 8.4238 | `reports/eval/edubench/_metrics/task_metric_means.jsonl` |
| `edubench` | `deepseek-v4-pro` | `likert_0_to_10` | 8.2236 | 8.2236 | `reports/eval/edubench/_metrics/task_metric_means.jsonl` |
| `edubench` | `deepseek-v4-pro` | `likert_0_to_10` | 9.4554 | 9.4554 | `reports/eval/edubench/_metrics/task_metric_means.jsonl` |
| `edubench` | `deepseek-v4-pro` | `likert_0_to_10` | 6.8675 | 6.8675 | `reports/eval/edubench/_metrics/task_metric_means.jsonl` |
| `edubench` | `deepseek-v4-pro` | `likert_0_to_10` | 8.9613 | 8.9613 | `reports/eval/edubench/_metrics/task_metric_means.jsonl` |
| `edubench` | `deepseek-v4-pro` | `likert_0_to_10` | 7.8541 | 7.8541 | `reports/eval/edubench/_metrics/task_metric_means.jsonl` |
| `edubench` | `deepseek-v4-pro` | `likert_0_to_10` | 7.1696 | 7.1696 | `reports/eval/edubench/_metrics/task_metric_means.jsonl` |
| `edubench` | `deepseek-v4-pro` | `likert_0_to_10` | 7.0345 | 7.0345 | `reports/eval/edubench/_metrics/task_metric_means.jsonl` |

Full selected rows are in `08_selected_score_evidence.jsonl`.
