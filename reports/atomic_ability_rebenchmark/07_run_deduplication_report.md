# Run Deduplication Report

Canonical scoring rules:

1. Keep only `score_role=scoring_candidate` rows for P scoring.
2. Prefer repo `summary.json` over derived HTML/Markdown report rows when the same benchmark/model/subdimension is duplicated.
3. For MiniMax-M3 conflicts, prefer included `minimax3/` paths and fuller-scored runs.
4. EduGuard P2 keeps only `deepseek-v3.2` judge rows in main scoring.

Duplicate score groups recorded: 63
MiniMax-M3 path-conflict rows recorded: 50

## Duplicate Score Rows

| Status | Benchmark | Model key | Source | Score | Path |
|---|---|---|---|---:|---|
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
| selected | `k12vista` | `minimax-m3` | repo_eval | 7.4059 | `reports/eval/k12vista/_sample-v3/judge-minimax3/minimax3/summary.json` |
| rejected | `k12vista` | `minimax-m3` | repo_eval | 7.3359 | `reports/eval/k12vista/judge-minimax3/minimax3/summary.json` |
| selected | `k12vista` | `minimax-m3` | repo_eval | 6.6730 | `reports/eval/k12vista/_sample-v3/judge-minimax3/minimax3/summary.json` |
| rejected | `k12vista` | `minimax-m3` | repo_eval | 6.5480 | `reports/eval/k12vista/judge-minimax3/minimax3/summary.json` |
| selected | `k12vista` | `minimax-m3` | repo_eval | 6.4061 | `reports/eval/k12vista/_sample-v3/judge-minimax3/minimax3/summary.json` |
| rejected | `k12vista` | `minimax-m3` | repo_eval | 6.2649 | `reports/eval/k12vista/judge-minimax3/minimax3/summary.json` |
| selected | `mathvista` | `minimax-m3` | repo_eval | 8.4089 | `reports/eval/mathvista/minimax3/summary.json` |
| rejected | `mathvista` | `minimax-m3` | repo_eval | 8.4089 | `reports/eval/mathvista/2026-06-06/summary.json` |
| selected | `mmlu_pro` | `minimax-m3` | repo_eval | 8.5555 | `reports/eval/mmlu_pro/minimax3/summary.json` |
| rejected | `mmlu_pro` | `minimax-m3` | repo_eval | 8.1379 | `reports/eval/mmlu_pro/2026-06-07/summary.json` |
| selected | `olympiadbench` | `glm-5.2` | repo_eval | 6.3518 | `reports/eval/olympiadbench/_noimage/glm-5.2/summary.json` |
| rejected | `olympiadbench` | `glm-5.2` | repo_eval | 8.4063 | `reports/eval/olympiadbench/glm-5.2/summary.json` |
| rejected | `olympiadbench` | `glm-5.2` | repo_eval | 6.5333 | `reports/eval/olympiadbench/_noimage/glm-5.2/_sample300_snapshot_20260722/summary.json` |
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
| not_selected | `bea2025_tutor` | `pass_rate` | 0.8912 | 294/300 | include_candidate | `reports/eval/bea2025_tutor/judge-deepseek-v4-flash/minimax3/summary.json` |
| selected | `bea2025_tutor` | `pass_rate` | 0.82 | 300/300 | include_candidate | `reports/eval/bea2025_tutor/judge-minimax3/minimax3/summary.json` |
| selected | `edubench` | `accuracy` | None | 3797/3797 | include_candidate | `reports/eval/edubench/judge-deepseek-v3.2/minimax-m3/summary.json` |
| not_selected | `edubench` | `accuracy` | None | 3796/3797 | include_candidate | `reports/eval/edubench/judge-deepseek-v4-flash/minimax-m3/summary.json` |
| not_selected | `edubench` | `accuracy` | None | 3784/3797 | include_candidate | `reports/eval/edubench/judge-minimax3/minimax-m3/summary.json` |
| not_selected | `eduequity` | `accuracy` | None | 397/400 | include_candidate | `reports/eval/eduequity/judge-deepseek-v4-flash/minimax3/summary.json` |
| selected | `eduequity` | `accuracy` | None | 400/400 | include_candidate | `reports/eval/eduequity/judge-minimax3/minimax3/summary.json` |
| selected | `eduguard_adversarial` | `asr` | 0.0824 | 801/801 | include_candidate | `reports/eval/eduguard_adversarial/judge-deepseek-v3.2/minimax3/summary.json` |
| not_selected | `eduguard_adversarial` | `asr` | 0.0492 | 793/801 | exclude_from_main | `reports/eval/eduguard_adversarial/judge-deepseek-v4-flash/minimax3/summary.json` |
| not_selected | `eduguard_adversarial` | `asr` | 0.035 | 801/801 | exclude_from_main | `reports/eval/eduguard_adversarial/judge-minimax3/minimax3/summary.json` |
| not_selected | `eduillustrate` | `overall_mean_all_items` | 2.9715 | 5/5 | exclude_from_main | `reports/eval/eduillustrate/_smoke/judge-claude-opus-4-8/minimax3/summary.json` |
| not_selected | `eduillustrate` | `overall_mean_all_items` | 2.8241 | 5/5 | exclude_from_main | `reports/eval/eduillustrate/_smoke/judge-deepseek-v3.2/minimax3/summary.json` |
| not_selected | `eduillustrate` | `overall_mean_all_items` | 2.8976 | 5/5 | exclude_from_main | `reports/eval/eduillustrate/_smoke/judge-doubao-seed-2.0-lite/minimax3/summary.json` |
| not_selected | `eduillustrate` | `overall_mean_all_items` | 2.5007 | 5/5 | exclude_from_main | `reports/eval/eduillustrate/_smoke/judge-doubao-seed-2.0-pro/minimax3/summary.json` |
| not_selected | `eduillustrate` | `overall_mean_all_items` | 2.9319 | 5/5 | exclude_from_main | `reports/eval/eduillustrate/_smoke/judge-minimax3/minimax3/summary.json` |
| selected | `eduillustrate` | `overall_mean_all_items` | 3.1748 | 230/230 | include_candidate | `reports/eval/eduillustrate/judge-minimax3/minimax3/summary.json` |
| selected | `k12vista` | `accuracy` | 0.48123436196830693 | 1199/1200 | include_candidate | `reports/eval/k12vista/_sample-v3/judge-minimax3/minimax3/summary.json` |
| not_selected | `k12vista` | `accuracy` | 0.46153846153846156 | 598/600 | include_candidate | `reports/eval/k12vista/judge-deepseek-v4-flash/minimax3/summary.json` |
| not_selected | `k12vista` | `accuracy` | 0.46488294314381273 | 598/600 | include_candidate | `reports/eval/k12vista/judge-minimax3/minimax3/summary.json` |
| not_selected | `longtutor_evidence` | `accuracy` | 0.7978687978687978 | 3003/3003 | include_candidate | `reports/eval/longtutor_evidence/judge-deepseek-v4-flash/minimax3/summary.json` |
| selected | `longtutor_evidence` | `accuracy` | 0.7872127872127872 | 3003/3003 | include_candidate | `reports/eval/longtutor_evidence/judge-minimax3/minimax3/summary.json` |
| not_selected | `longtutor_teaching` | `accuracy` | 1.0 | 1001/1001 | include_candidate | `reports/eval/longtutor_teaching/judge-deepseek-v4-flash/minimax3/summary.json` |
| selected | `longtutor_teaching` | `accuracy` | 0.999000999000999 | 1001/1001 | include_candidate | `reports/eval/longtutor_teaching/judge-minimax3/minimax3/summary.json` |
| not_selected | `mathtutorbench_pedagogy` | `accuracy` | 0.8139130434782609 | 1150/1150 | include_candidate | `reports/eval/mathtutorbench_pedagogy/judge-deepseek-v4-flash/minimax3/summary.json` |
| selected | `mathtutorbench_pedagogy` | `accuracy` | 0.7930434782608695 | 1150/1150 | include_candidate | `reports/eval/mathtutorbench_pedagogy/judge-minimax3/minimax3/summary.json` |
| not_selected | `mathtutorbench_pedagogy_hard` | `accuracy` | 0.746177370030581 | 327/327 | include_candidate | `reports/eval/mathtutorbench_pedagogy_hard/judge-deepseek-v4-flash/minimax3/summary.json` |
| selected | `mathtutorbench_pedagogy_hard` | `accuracy` | 0.7339449541284404 | 327/327 | include_candidate | `reports/eval/mathtutorbench_pedagogy_hard/judge-minimax3/minimax3/summary.json` |
| not_selected | `mathtutorbench_scaffolding` | `accuracy` | 0.23043478260869565 | 1150/1150 | include_candidate | `reports/eval/mathtutorbench_scaffolding/judge-deepseek-v4-flash/minimax3/summary.json` |
| selected | `mathtutorbench_scaffolding` | `accuracy` | 0.22956521739130434 | 1150/1150 | include_candidate | `reports/eval/mathtutorbench_scaffolding/judge-minimax3/minimax3/summary.json` |
| not_selected | `mathtutorbench_scaffolding_hard` | `accuracy` | 0.1712538226299694 | 327/327 | include_candidate | `reports/eval/mathtutorbench_scaffolding_hard/judge-deepseek-v4-flash/minimax3/summary.json` |
| selected | `mathtutorbench_scaffolding_hard` | `accuracy` | 0.18960244648318042 | 327/327 | include_candidate | `reports/eval/mathtutorbench_scaffolding_hard/judge-minimax3/minimax3/summary.json` |
| not_selected | `mathvista` | `accuracy` | 0.8408862034239678 | 993/1000 | include_candidate | `reports/eval/mathvista/2026-06-06/summary.json` |
| selected | `mathvista` | `accuracy` | 0.8408862034239678 | 993/1000 | include_candidate | `reports/eval/mathvista/minimax3/summary.json` |
| not_selected | `mmlu_pro` | `accuracy` | 0.8137863443319177 | 3061/12032 | include_candidate | `reports/eval/mmlu_pro/2026-06-07/summary.json` |
| selected | `mmlu_pro` | `accuracy` | 0.8555518617021277 | 12032/12032 | include_candidate | `reports/eval/mmlu_pro/minimax3/summary.json` |
| not_selected | `mmtutorbench` | `accuracy` | 0.09492847854356307 | 769/770 | include_candidate | `reports/eval/mmtutorbench/judge-deepseek-v4-flash/minimax3/summary.json` |
| selected | `mmtutorbench` | `accuracy` | 0.033810143042912875 | 769/770 | include_candidate | `reports/eval/mmtutorbench/judge-minimax3/minimax3/summary.json` |
| not_selected | `mrbench_tutor` | `pass_rate` | 0.9045 | 199/200 | include_candidate | `reports/eval/mrbench_tutor/judge-deepseek-v4-flash/minimax3/summary.json` |
| selected | `mrbench_tutor` | `pass_rate` | 0.83 | 200/200 | include_candidate | `reports/eval/mrbench_tutor/judge-minimax3/minimax3/summary.json` |
| not_selected | `olympiadbench` | `accuracy` | 0.896640826873385 | 387/6728 | include_candidate | `reports/eval/olympiadbench/2026-06-08/summary.json` |
| not_selected | `olympiadbench` | `unknown` | None | 0/0 | exclude_from_main | `reports/eval/olympiadbench/_mini_v1/MiniMax-M3/summary.json` |
| not_selected | `olympiadbench` | `unknown` | None | 0/0 | exclude_from_main | `reports/eval/olympiadbench/_noimage/MiniMax-M3_uncapped_full_2026-07-23/summary.json` |
| not_selected | `olympiadbench` | `accuracy` | None | 0/6 | exclude_from_main | `reports/eval/olympiadbench/_noimage/_minimax_verbosity_probe/summary.json` |
| not_selected | `olympiadbench` | `accuracy` | 0.4523809523809524 | 42/6728 | exclude_from_main | `reports/eval/olympiadbench/_stale/minimax3_partial-20260616/summary.json` |
| selected | `olympiadbench` | `accuracy` | 0.7160071407319251 | 6722/6728 | include_candidate | `reports/eval/olympiadbench/minimax3/summary.json` |
| selected | `tutorbench` | `accuracy` | None | 1440/1473 | include_candidate | `reports/eval/tutorbench/judge-deepseek-v4-flash/minimax3/summary.json` |
| not_selected | `tutorbench` | `accuracy` | None | 1440/1473 | include_candidate | `reports/eval/tutorbench/judge-minimax3/_m3_fullset_20260723/summary.json` |
| not_selected | `tutorbench` | `accuracy` | None | 6/6 | exclude_from_main | `reports/eval/tutorbench/judge-minimax3/minimax3/summary.json` |

Full records are in `07_run_deduplication_report.jsonl`.
