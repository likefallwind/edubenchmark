# Run Deduplication Report

Canonical scoring rules:

1. Keep only `score_role=scoring_candidate` rows for P scoring.
2. Prefer repo `summary.json` over derived HTML/Markdown report rows when the same benchmark/model/subdimension is duplicated.
3. For MiniMax-M3 conflicts, prefer included `minimax3/` paths and fuller-scored runs.
4. EduGuard P2 keeps only `deepseek-v3.2` judge rows in main scoring.

Duplicate score groups recorded: 64
MiniMax-M3 path-conflict rows recorded: 17

## Duplicate Score Rows

| Status | Benchmark | Model key | Source | Score | Path |
|---|---|---|---|---:|---|
| selected | `eduguard_adversarial` | `deepseek-v4-pro` | repo_eval | 3.7590 | `reports/eval/eduguard_adversarial/_judge-deepseek-v3.2/deepseek-v4-pro/summary.json` |
| rejected | `eduguard_adversarial` | `deepseek-v4-pro` | otherbenchmark | 3.7600 | `otherbenchmark/eduguard_overall_report.html` |
| selected | `eduguard_adversarial` | `doubao-seed-2-0-lite` | repo_eval | 4.8880 | `reports/eval/eduguard_adversarial/_judge-deepseek-v3.2/doubao-seed-2.0-lite/summary.json` |
| rejected | `eduguard_adversarial` | `doubao-seed-2-0-lite` | otherbenchmark | 4.8900 | `otherbenchmark/eduguard_overall_report.html` |
| selected | `eduguard_adversarial` | `doubao-seed-2-0-pro` | repo_eval | 3.9750 | `reports/eval/eduguard_adversarial/_judge-deepseek-v3.2/doubao-seed-2.0-pro/summary.json` |
| rejected | `eduguard_adversarial` | `doubao-seed-2-0-pro` | otherbenchmark | 3.9700 | `otherbenchmark/eduguard_overall_report.html` |
| selected | `eduguard_adversarial` | `glm-5.2` | repo_eval | 7.1540 | `reports/eval/eduguard_adversarial/_judge-deepseek-v3.2/glm-5.2/summary.json` |
| rejected | `eduguard_adversarial` | `glm-5.2` | otherbenchmark | 7.1500 | `otherbenchmark/eduguard_overall_report.html` |
| selected | `eduguard_adversarial` | `minimax-m3` | repo_eval | 9.1760 | `reports/eval/eduguard_adversarial/_judge-deepseek-v3.2/minimax3/summary.json` |
| rejected | `eduguard_adversarial` | `minimax-m3` | otherbenchmark | 9.1800 | `otherbenchmark/eduguard_overall_report.html` |
| selected | `eduguard_sata` | `deepseek-v4-pro` | repo_eval | 7.6120 | `reports/eval/eduguard_sata/deepseek-v4-pro/summary.json` |
| rejected | `eduguard_sata` | `deepseek-v4-pro` | otherbenchmark | 7.6120 | `otherbenchmark/eduguard_overall_report.html` |
| selected | `eduguard_sata` | `doubao-seed-2-0-lite` | repo_eval | 7.3000 | `reports/eval/eduguard_sata/doubao-seed-2.0-lite/summary.json` |
| rejected | `eduguard_sata` | `doubao-seed-2-0-lite` | otherbenchmark | 7.3000 | `otherbenchmark/eduguard_overall_report.html` |
| selected | `eduguard_sata` | `doubao-seed-2-0-pro` | repo_eval | 7.6180 | `reports/eval/eduguard_sata/doubao-seed-2.0-pro/summary.json` |
| rejected | `eduguard_sata` | `doubao-seed-2-0-pro` | otherbenchmark | 7.6180 | `otherbenchmark/eduguard_overall_report.html` |
| selected | `eduguard_sata` | `glm-5.1` | repo_eval | 7.6320 | `reports/eval/eduguard_sata/glm-5.1/summary.json` |
| rejected | `eduguard_sata` | `glm-5.1` | otherbenchmark | 7.6320 | `otherbenchmark/eduguard_overall_report.html` |
| selected | `eduguard_sata` | `glm-5.2` | repo_eval | 7.5950 | `reports/eval/eduguard_sata/glm-5.2/summary.json` |
| rejected | `eduguard_sata` | `glm-5.2` | otherbenchmark | 7.5950 | `otherbenchmark/eduguard_overall_report.html` |
| selected | `eduguard_sata` | `minimax-m3` | repo_eval | 7.6940 | `reports/eval/eduguard_sata/minimax3/summary.json` |
| rejected | `eduguard_sata` | `minimax-m3` | otherbenchmark | 7.6940 | `otherbenchmark/eduguard_overall_report.html` |
| selected | `mathvista` | `minimax-m3` | repo_eval | 8.4089 | `reports/eval/mathvista/minimax3/summary.json` |
| rejected | `mathvista` | `minimax-m3` | repo_eval | 8.4089 | `reports/eval/mathvista/2026-06-06/summary.json` |
| selected | `mmlu_pro` | `minimax-m3` | repo_eval | 8.5555 | `reports/eval/mmlu_pro/minimax3/summary.json` |
| rejected | `mmlu_pro` | `minimax-m3` | repo_eval | 8.1379 | `reports/eval/mmlu_pro/2026-06-07/summary.json` |
| selected | `olympiadbench` | `minimax-m3` | repo_eval | 7.1601 | `reports/eval/olympiadbench/minimax3/summary.json` |
| rejected | `olympiadbench` | `minimax-m3` | repo_eval | 8.9664 | `reports/eval/olympiadbench/2026-06-08/summary.json` |
| selected | `sas_bench` | `deepseek-v4-pro` | repo_eval | 7.6629 | `reports/eval/sas_bench/deepseek-v4-pro/summary.json` |
| rejected | `sas_bench` | `deepseek-v4-pro` | otherbenchmark | 7.6630 | `otherbenchmark/sas-bench-result0630.md` |
| selected | `sas_bench` | `glm-5.1` | repo_eval | 7.8142 | `reports/eval/sas_bench/glm-5.1/summary.json` |
| rejected | `sas_bench` | `glm-5.1` | otherbenchmark | 7.8140 | `otherbenchmark/sas-bench-result0630.md` |
| selected | `sas_bench` | `gpt-5.4` | repo_eval | 8.0261 | `reports/eval/sas_bench/gpt-5.4/summary.json` |
| rejected | `sas_bench` | `gpt-5.4` | otherbenchmark | 8.0260 | `otherbenchmark/sas-bench-result0630.md` |
| selected | `sas_bench` | `kimi-k2-6` | repo_eval | 7.3299 | `reports/eval/sas_bench/kimi-k2.6/summary.json` |
| rejected | `sas_bench` | `kimi-k2-6` | otherbenchmark | 7.3300 | `otherbenchmark/sas-bench-result0630.md` |
| selected | `sas_bench` | `minimax-m2.7` | repo_eval | 7.2457 | `reports/eval/sas_bench/minimax-m2.7/summary.json` |
| rejected | `sas_bench` | `minimax-m2.7` | otherbenchmark | 7.2460 | `otherbenchmark/sas-bench-result0630.md` |
| selected | `sas_bench` | `minimax-m3` | repo_eval | 7.6833 | `reports/eval/sas_bench/minimax-m3/summary.json` |
| rejected | `sas_bench` | `minimax-m3` | otherbenchmark | 7.6830 | `otherbenchmark/sas-bench-result0630.md` |
| selected | `sas_bench` | `deepseek-v4-pro` | repo_eval | 6.1694 | `reports/eval/sas_bench/deepseek-v4-pro/summary.json` |
| rejected | `sas_bench` | `deepseek-v4-pro` | otherbenchmark | 6.1690 | `otherbenchmark/sas-bench-result0630.md` |
| selected | `sas_bench` | `glm-5.1` | repo_eval | 6.2602 | `reports/eval/sas_bench/glm-5.1/summary.json` |
| rejected | `sas_bench` | `glm-5.1` | otherbenchmark | 6.2600 | `otherbenchmark/sas-bench-result0630.md` |
| selected | `sas_bench` | `gpt-5.4` | repo_eval | 5.5636 | `reports/eval/sas_bench/gpt-5.4/summary.json` |
| rejected | `sas_bench` | `gpt-5.4` | otherbenchmark | 5.5640 | `otherbenchmark/sas-bench-result0630.md` |
| selected | `sas_bench` | `kimi-k2-6` | repo_eval | 5.2204 | `reports/eval/sas_bench/kimi-k2.6/summary.json` |
| rejected | `sas_bench` | `kimi-k2-6` | otherbenchmark | 5.2200 | `otherbenchmark/sas-bench-result0630.md` |
| selected | `sas_bench` | `minimax-m2.7` | repo_eval | 5.1393 | `reports/eval/sas_bench/minimax-m2.7/summary.json` |
| rejected | `sas_bench` | `minimax-m2.7` | otherbenchmark | 5.1390 | `otherbenchmark/sas-bench-result0630.md` |
| selected | `sas_bench` | `minimax-m3` | repo_eval | 6.6022 | `reports/eval/sas_bench/minimax-m3/summary.json` |
| rejected | `sas_bench` | `minimax-m3` | otherbenchmark | 6.6020 | `otherbenchmark/sas-bench-result0630.md` |
| selected | `sas_bench` | `deepseek-v4-pro` | repo_eval | 8.1864 | `reports/eval/sas_bench/deepseek-v4-pro/summary.json` |
| rejected | `sas_bench` | `deepseek-v4-pro` | otherbenchmark | 8.1860 | `otherbenchmark/sas-bench-result0630.md` |
| selected | `sas_bench` | `glm-5.1` | repo_eval | 8.3563 | `reports/eval/sas_bench/glm-5.1/summary.json` |
| rejected | `sas_bench` | `glm-5.1` | otherbenchmark | 8.3560 | `otherbenchmark/sas-bench-result0630.md` |
| selected | `sas_bench` | `gpt-5.4` | repo_eval | 8.6767 | `reports/eval/sas_bench/gpt-5.4/summary.json` |
| rejected | `sas_bench` | `gpt-5.4` | otherbenchmark | 8.6770 | `otherbenchmark/sas-bench-result0630.md` |
| selected | `sas_bench` | `kimi-k2-6` | repo_eval | 7.9129 | `reports/eval/sas_bench/kimi-k2.6/summary.json` |
| rejected | `sas_bench` | `kimi-k2-6` | otherbenchmark | 7.9130 | `otherbenchmark/sas-bench-result0630.md` |
| selected | `sas_bench` | `minimax-m2.7` | repo_eval | 7.9043 | `reports/eval/sas_bench/minimax-m2.7/summary.json` |
| rejected | `sas_bench` | `minimax-m2.7` | otherbenchmark | 7.9040 | `otherbenchmark/sas-bench-result0630.md` |
| selected | `sas_bench` | `minimax-m3` | repo_eval | 8.4304 | `reports/eval/sas_bench/minimax-m3/summary.json` |
| rejected | `sas_bench` | `minimax-m3` | otherbenchmark | 8.4300 | `otherbenchmark/sas-bench-result0630.md` |

## MiniMax-M3 Path Conflicts

| Status | Benchmark | Metric | Value | Scored/Total | Inclusion | Path |
|---|---|---|---:|---:|---|---|
| not_selected | `agieval` | `accuracy` | None | 0/7272 | include_candidate | `reports/eval/agieval/2026-06-08/summary.json` |
| selected | `agieval` | `accuracy` | 0.8560814529444138 | 7268/7272 | include_candidate | `reports/eval/agieval/minimax3/summary.json` |
| selected | `eduguard_adversarial` | `asr` | 0.0824 | 801/801 | include_candidate | `reports/eval/eduguard_adversarial/_judge-deepseek-v3.2/minimax3/summary.json` |
| not_selected | `eduguard_adversarial` | `asr` | 0.035 | 801/801 | exclude_from_main | `reports/eval/eduguard_adversarial/minimax3/summary.json` |
| selected | `eduillustrate` | `overall_mean_judged_only` | 3.1748 | 230/230 | include_candidate | `reports/eval/eduillustrate/MiniMax-M3__gen-full230_judge-MiniMax-M3/summary.json` |
| not_selected | `eduillustrate` | `overall_mean_judged_only` | 3.5301 | 4/5 | exclude_from_main | `reports/eval/eduillustrate/deepseek-v3.2/summary.json` |
| not_selected | `eduillustrate` | `overall_mean_judged_only` | 3.622 | 4/5 | exclude_from_main | `reports/eval/eduillustrate/doubao-seed-2.0-lite/summary.json` |
| not_selected | `eduillustrate` | `overall_mean_judged_only` | 3.1258 | 4/5 | exclude_from_main | `reports/eval/eduillustrate/doubao-seed-2.0-pro/summary.json` |
| not_selected | `eduillustrate` | `overall_mean_judged_only` | 3.6649 | 4/5 | exclude_from_main | `reports/eval/eduillustrate/minimax3/summary.json` |
| not_selected | `eduillustrate` | `overall_mean_judged_only` | 3.7144 | 4/5 | exclude_from_main | `reports/eval/eduillustrate/opus-4.8/summary.json` |
| not_selected | `mathvista` | `accuracy` | 0.8408862034239678 | 993/1000 | include_candidate | `reports/eval/mathvista/2026-06-06/summary.json` |
| selected | `mathvista` | `accuracy` | 0.8408862034239678 | 993/1000 | include_candidate | `reports/eval/mathvista/minimax3/summary.json` |
| not_selected | `mmlu_pro` | `accuracy` | 0.8137863443319177 | 3061/12032 | include_candidate | `reports/eval/mmlu_pro/2026-06-07/summary.json` |
| selected | `mmlu_pro` | `accuracy` | 0.8555518617021277 | 12032/12032 | include_candidate | `reports/eval/mmlu_pro/minimax3/summary.json` |
| not_selected | `olympiadbench` | `accuracy` | 0.896640826873385 | 387/6728 | include_candidate | `reports/eval/olympiadbench/2026-06-08/summary.json` |
| selected | `olympiadbench` | `accuracy` | 0.7160071407319251 | 6722/6728 | include_candidate | `reports/eval/olympiadbench/minimax3/summary.json` |
| not_selected | `olympiadbench` | `accuracy` | 0.4523809523809524 | 42/6728 | exclude_from_main | `reports/eval/olympiadbench/summary.json` |

Full records are in `07_run_deduplication_report.jsonl`.
