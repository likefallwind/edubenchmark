# Selected Score Evidence

Canonical normalized score rows used for P scoring: 531

## By Source

| Source | Rows |
|---|---:|
| `otherbenchmark` | 181 |
| `repo_eval` | 350 |

## By Benchmark

| Benchmark | Rows |
|---|---:|
| `agieval` | 8 |
| `asap_2` | 7 |
| `bea2025_judge` | 9 |
| `bea2025_tutor` | 18 |
| `ceval` | 9 |
| `edubench` | 168 |
| `eduguard_adversarial` | 14 |
| `eduguard_sata` | 10 |
| `eduillustrate` | 5 |
| `ifeval` | 7 |
| `k12vista` | 12 |
| `longtutor_diagnosis` | 7 |
| `longtutor_evidence` | 21 |
| `longtutor_teaching` | 7 |
| `mathtutorbench_mistake_correction` | 8 |
| `mathtutorbench_mistake_location` | 8 |
| `mathtutorbench_pedagogy` | 9 |
| `mathtutorbench_pedagogy_hard` | 9 |
| `mathtutorbench_problem_solving` | 7 |
| `mathtutorbench_scaffolding` | 9 |
| `mathtutorbench_scaffolding_hard` | 9 |
| `mathtutorbench_socratic` | 7 |
| `mathtutorbench_solution_correctness` | 8 |
| `mathvista` | 4 |
| `mmlu_pro` | 8 |
| `mmtutorbench` | 4 |
| `mooccube_prereq` | 7 |
| `mrbench_judge` | 9 |
| `mrbench_tutor` | 30 |
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
| `ceval` | `deepseek-v4-pro` | `accuracy` | 0.9383358098068351 | 9.3834 | `reports/eval/ceval/deepseek-v4-pro/summary.json` |
| `edubench` | `deepseek-v4-pro` | `likert_0_to_10` | 8.3472 | 8.3472 | `reports/eval/edubench/_metrics/task_metric_means.jsonl` |
| `edubench` | `deepseek-v4-pro` | `likert_0_to_10` | 8.7062 | 8.7062 | `reports/eval/edubench/_metrics/task_metric_means.jsonl` |
| `edubench` | `deepseek-v4-pro` | `likert_0_to_10` | 7.8699 | 7.8699 | `reports/eval/edubench/_metrics/task_metric_means.jsonl` |
| `edubench` | `deepseek-v4-pro` | `likert_0_to_10` | 8.7588 | 8.7588 | `reports/eval/edubench/_metrics/task_metric_means.jsonl` |
| `edubench` | `deepseek-v4-pro` | `likert_0_to_10` | 8.1962 | 8.1962 | `reports/eval/edubench/_metrics/task_metric_means.jsonl` |
| `edubench` | `deepseek-v4-pro` | `likert_0_to_10` | 8.2236 | 8.2236 | `reports/eval/edubench/_metrics/task_metric_means.jsonl` |
| `edubench` | `deepseek-v4-pro` | `likert_0_to_10` | 8.9613 | 8.9613 | `reports/eval/edubench/_metrics/task_metric_means.jsonl` |
| `edubench` | `deepseek-v4-pro` | `likert_0_to_10` | 7.0345 | 7.0345 | `reports/eval/edubench/_metrics/task_metric_means.jsonl` |
| `edubench` | `deepseek-v4-pro` | `likert_0_to_10` | 6.4398 | 6.4398 | `reports/eval/edubench/_metrics/task_metric_means.jsonl` |
| `edubench` | `deepseek-v4-pro` | `likert_0_to_10` | 6.4385 | 6.4385 | `reports/eval/edubench/_metrics/task_metric_means.jsonl` |
| `edubench` | `deepseek-v4-pro` | `likert_0_to_10` | 7.9357 | 7.9357 | `reports/eval/edubench/_metrics/task_metric_means.jsonl` |
| `edubench` | `deepseek-v4-pro` | `likert_0_to_10` | 8.1691 | 8.1691 | `reports/eval/edubench/_metrics/task_metric_means.jsonl` |
| `eduguard_adversarial` | `deepseek-v4-pro` | `asr_0_to_1_lower_better` | 0.6241 | 3.7590 | `reports/eval/eduguard_adversarial/judge-deepseek-v3.2/deepseek-v4-pro/summary.json` |
| `eduguard_adversarial` | `deepseek-v4-pro` | `share_0_to_1` | 0.4933 | 4.9330 | `reports/eval/eduguard_adversarial/judge-deepseek-v3.2/deepseek-v4-pro/summary.json` |
| `eduguard_sata` | `deepseek-v4-pro` | `rfs_0_to_1` | 0.7612 | 7.6120 | `reports/eval/eduguard_sata/deepseek-v4-pro/summary.json` |
| `ifeval` | `deepseek-v4-pro` | `accuracy` | 0.9222222222222223 | 9.2222 | `reports/eval/ifeval/deepseek-v4-pro/summary.json` |
| `longtutor_diagnosis` | `deepseek-v4-pro` | `accuracy_or_f1` | 0.3158242873546295 | 3.1582 | `reports/eval/longtutor_diagnosis/deepseek-v4-pro/summary.json` |
| `longtutor_evidence` | `deepseek-v4-pro` | `accuracy` | 0.7082917082917083 | 7.0829 | `reports/eval/longtutor_evidence/judge-minimax3/deepseek-v4-pro/summary.json` |
| `longtutor_evidence` | `deepseek-v4-pro` | `accuracy` | 0.9690309690309691 | 9.6903 | `reports/eval/longtutor_evidence/judge-minimax3/deepseek-v4-pro/summary.json` |
| `longtutor_evidence` | `deepseek-v4-pro` | `accuracy` | 0.6973026973026973 | 6.9730 | `reports/eval/longtutor_evidence/judge-minimax3/deepseek-v4-pro/summary.json` |
| `longtutor_teaching` | `deepseek-v4-pro` | `likert_1_to_5` | 3.6079999999999997 | 6.5200 | `reports/eval/longtutor_teaching/judge-minimax3/deepseek-v4-pro/summary.json` |
| `mathtutorbench_mistake_correction` | `deepseek-v4-pro` | `accuracy` | 0.9201596806387226 | 9.2016 | `reports/eval/mathtutorbench_mistake_correction/deepseek-v4-pro/summary.json` |
| `mathtutorbench_mistake_location` | `deepseek-v4-pro` | `accuracy_or_f1` | 0.765 | 7.6500 | `reports/eval/mathtutorbench_mistake_location/deepseek-v4-pro/summary.json` |
| `mathtutorbench_pedagogy` | `deepseek-v4-pro` | `win_rate_or_accuracy` | 0.8396 | 8.3960 | `reports/eval/mathtutorbench_pedagogy/judge-minimax3/deepseek-v4-pro/summary.json` |
| `mathtutorbench_pedagogy_hard` | `deepseek-v4-pro` | `win_rate_or_accuracy` | 0.8532 | 8.5320 | `reports/eval/mathtutorbench_pedagogy_hard/judge-minimax3/deepseek-v4-pro/summary.json` |
| `mathtutorbench_scaffolding` | `deepseek-v4-pro` | `win_rate_or_accuracy` | 0.5004 | 5.0040 | `reports/eval/mathtutorbench_scaffolding/judge-minimax3/deepseek-v4-pro/summary.json` |
| `mathtutorbench_scaffolding_hard` | `deepseek-v4-pro` | `win_rate_or_accuracy` | 0.4128 | 4.1280 | `reports/eval/mathtutorbench_scaffolding_hard/judge-minimax3/deepseek-v4-pro/summary.json` |
| `mathtutorbench_socratic` | `deepseek-v4-pro` | `bleu_0_to_1` | 0.2838 | 2.8380 | `reports/eval/mathtutorbench_socratic/deepseek-v4-pro/summary.json` |
| `mathtutorbench_solution_correctness` | `deepseek-v4-pro` | `accuracy_or_f1` | 0.8621 | 8.6210 | `reports/eval/mathtutorbench_solution_correctness/deepseek-v4-pro/summary.json` |

Full selected rows are in `08_selected_score_evidence.jsonl`.
