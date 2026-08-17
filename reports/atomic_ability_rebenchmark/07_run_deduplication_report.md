# Run Deduplication Report

Canonical scoring rules:

1. Keep only `score_role=scoring_candidate` rows for P scoring.
2. Prefer repo `summary.json` over derived HTML/Markdown report rows when the same benchmark/model/subdimension is duplicated.
3. For MiniMax-M3 conflicts, prefer included `minimax3/` paths and fuller-scored runs.
4. EduGuard P2 keeps only `deepseek-v3.2` judge rows in main scoring.

Duplicate score groups recorded: 181
MiniMax-M3 path-conflict rows recorded: 42

## Duplicate Score Rows

| Status | Benchmark | Model key | Source | Score | Path |
|---|---|---|---|---:|---|
| selected | `bea2025_tutor` | `doubao-seed-2-0-pro` | repo_eval | 9.7670 | `reports/eval/bea2025_tutor/doubao-seed-2.0-pro/summary.json` |
| rejected | `bea2025_tutor` | `doubao-seed-2-0-pro` | repo_eval | 10.0000 | `reports/eval/bea2025_tutor/_judge-deepseek-v4-flash/doubao-seed-2.0-pro/summary.json` |
| selected | `bea2025_tutor` | `glm-5.2` | repo_eval | 9.6000 | `reports/eval/bea2025_tutor/glm-5.2/summary.json` |
| rejected | `bea2025_tutor` | `glm-5.2` | repo_eval | 9.8990 | `reports/eval/bea2025_tutor/_judge-deepseek-v4-flash/glm-5.2/summary.json` |
| selected | `bea2025_tutor` | `minimax-m2.7` | repo_eval | 9.8000 | `reports/eval/bea2025_tutor/_judge-deepseek-v4-flash/MiniMax-M2.7/summary.json` |
| rejected | `bea2025_tutor` | `minimax-m2.7` | repo_eval | 8.8670 | `reports/eval/bea2025_tutor/MiniMax-M2.7/summary.json` |
| selected | `bea2025_tutor` | `minimax-m3` | repo_eval | 9.4670 | `reports/eval/bea2025_tutor/minimax3/summary.json` |
| rejected | `bea2025_tutor` | `minimax-m3` | repo_eval | 9.8640 | `reports/eval/bea2025_tutor/_judge-deepseek-v4-flash/minimax3/summary.json` |
| selected | `bea2025_tutor` | `doubao-seed-2-0-pro` | repo_eval | 8.7330 | `reports/eval/bea2025_tutor/doubao-seed-2.0-pro/summary.json` |
| rejected | `bea2025_tutor` | `doubao-seed-2-0-pro` | repo_eval | 9.1890 | `reports/eval/bea2025_tutor/_judge-deepseek-v4-flash/doubao-seed-2.0-pro/summary.json` |
| selected | `bea2025_tutor` | `glm-5.2` | repo_eval | 8.5000 | `reports/eval/bea2025_tutor/glm-5.2/summary.json` |
| rejected | `bea2025_tutor` | `glm-5.2` | repo_eval | 9.2570 | `reports/eval/bea2025_tutor/_judge-deepseek-v4-flash/glm-5.2/summary.json` |
| selected | `bea2025_tutor` | `minimax-m2.7` | repo_eval | 8.8000 | `reports/eval/bea2025_tutor/_judge-deepseek-v4-flash/MiniMax-M2.7/summary.json` |
| rejected | `bea2025_tutor` | `minimax-m2.7` | repo_eval | 7.9330 | `reports/eval/bea2025_tutor/MiniMax-M2.7/summary.json` |
| selected | `bea2025_tutor` | `minimax-m3` | repo_eval | 8.5330 | `reports/eval/bea2025_tutor/minimax3/summary.json` |
| rejected | `bea2025_tutor` | `minimax-m3` | repo_eval | 8.9460 | `reports/eval/bea2025_tutor/_judge-deepseek-v4-flash/minimax3/summary.json` |
| selected | `bea2025_tutor` | `doubao-seed-2-0-pro` | repo_eval | 9.5670 | `reports/eval/bea2025_tutor/doubao-seed-2.0-pro/summary.json` |
| rejected | `bea2025_tutor` | `doubao-seed-2-0-pro` | repo_eval | 9.9320 | `reports/eval/bea2025_tutor/_judge-deepseek-v4-flash/doubao-seed-2.0-pro/summary.json` |
| selected | `bea2025_tutor` | `glm-5.2` | repo_eval | 9.7330 | `reports/eval/bea2025_tutor/glm-5.2/summary.json` |
| rejected | `bea2025_tutor` | `glm-5.2` | repo_eval | 9.9320 | `reports/eval/bea2025_tutor/_judge-deepseek-v4-flash/glm-5.2/summary.json` |
| selected | `bea2025_tutor` | `minimax-m2.7` | repo_eval | 9.6000 | `reports/eval/bea2025_tutor/_judge-deepseek-v4-flash/MiniMax-M2.7/summary.json` |
| rejected | `bea2025_tutor` | `minimax-m2.7` | repo_eval | 9.4000 | `reports/eval/bea2025_tutor/MiniMax-M2.7/summary.json` |
| selected | `bea2025_tutor` | `minimax-m3` | repo_eval | 9.7670 | `reports/eval/bea2025_tutor/minimax3/summary.json` |
| rejected | `bea2025_tutor` | `minimax-m3` | repo_eval | 9.8980 | `reports/eval/bea2025_tutor/_judge-deepseek-v4-flash/minimax3/summary.json` |
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
| selected | `k12vista` | `minimax-m3` | repo_eval | 7.4059 | `reports/eval/k12vista/_sample-v3/minimax3/summary.json` |
| rejected | `k12vista` | `minimax-m3` | repo_eval | 7.3359 | `reports/eval/k12vista/minimax3/summary.json` |
| selected | `k12vista` | `minimax-m3` | repo_eval | 6.6730 | `reports/eval/k12vista/_sample-v3/minimax3/summary.json` |
| rejected | `k12vista` | `minimax-m3` | repo_eval | 6.5480 | `reports/eval/k12vista/minimax3/summary.json` |
| selected | `k12vista` | `minimax-m3` | repo_eval | 6.4061 | `reports/eval/k12vista/_sample-v3/minimax3/summary.json` |
| rejected | `k12vista` | `minimax-m3` | repo_eval | 6.2649 | `reports/eval/k12vista/minimax3/summary.json` |
| selected | `mathtutorbench_pedagogy` | `deepseek-v4-pro` | repo_eval | 8.3960 | `reports/eval/mathtutorbench_pedagogy/deepseek-v4-pro/summary.json` |
| rejected | `mathtutorbench_pedagogy` | `deepseek-v4-pro` | repo_eval | 8.6870 | `reports/eval/mathtutorbench_pedagogy/_judge-deepseek-v4-flash/deepseek-v4-pro/summary.json` |
| selected | `mathtutorbench_pedagogy` | `doubao-seed-2-0-pro` | repo_eval | 8.6700 | `reports/eval/mathtutorbench_pedagogy/doubao-seed-2.0-pro/summary.json` |
| rejected | `mathtutorbench_pedagogy` | `doubao-seed-2-0-pro` | repo_eval | 9.0520 | `reports/eval/mathtutorbench_pedagogy/_judge-deepseek-v4-flash/doubao-seed-2.0-pro/summary.json` |
| selected | `mathtutorbench_pedagogy` | `glm-5.2` | repo_eval | 8.5830 | `reports/eval/mathtutorbench_pedagogy/glm-5.2/summary.json` |
| rejected | `mathtutorbench_pedagogy` | `glm-5.2` | repo_eval | 8.8780 | `reports/eval/mathtutorbench_pedagogy/_judge-deepseek-v4-flash/glm-5.2/summary.json` |
| selected | `mathtutorbench_pedagogy` | `minimax-m2.7` | repo_eval | 7.9130 | `reports/eval/mathtutorbench_pedagogy/_judge-deepseek-v4-flash/MiniMax-M2.7/summary.json` |
| rejected | `mathtutorbench_pedagogy` | `minimax-m2.7` | repo_eval | 7.4480 | `reports/eval/mathtutorbench_pedagogy/MiniMax-M2.7/summary.json` |
| selected | `mathtutorbench_pedagogy` | `minimax-m3` | repo_eval | 8.3170 | `reports/eval/mathtutorbench_pedagogy/minimax3/summary.json` |
| rejected | `mathtutorbench_pedagogy` | `minimax-m3` | repo_eval | 8.4740 | `reports/eval/mathtutorbench_pedagogy/_judge-deepseek-v4-flash/minimax3/summary.json` |
| selected | `mathtutorbench_pedagogy_hard` | `deepseek-v4-pro` | repo_eval | 8.5320 | `reports/eval/mathtutorbench_pedagogy_hard/deepseek-v4-pro/summary.json` |
| rejected | `mathtutorbench_pedagogy_hard` | `deepseek-v4-pro` | repo_eval | 8.5630 | `reports/eval/mathtutorbench_pedagogy_hard/_judge-deepseek-v4-flash/deepseek-v4-pro/summary.json` |
| selected | `mathtutorbench_pedagogy_hard` | `doubao-seed-2-0-pro` | repo_eval | 8.6390 | `reports/eval/mathtutorbench_pedagogy_hard/doubao-seed-2.0-pro/summary.json` |
| rejected | `mathtutorbench_pedagogy_hard` | `doubao-seed-2-0-pro` | repo_eval | 8.8530 | `reports/eval/mathtutorbench_pedagogy_hard/_judge-deepseek-v4-flash/doubao-seed-2.0-pro/summary.json` |
| selected | `mathtutorbench_pedagogy_hard` | `glm-5.2` | repo_eval | 8.3490 | `reports/eval/mathtutorbench_pedagogy_hard/glm-5.2/summary.json` |
| rejected | `mathtutorbench_pedagogy_hard` | `glm-5.2` | repo_eval | 8.5780 | `reports/eval/mathtutorbench_pedagogy_hard/_judge-deepseek-v4-flash/glm-5.2/summary.json` |
| selected | `mathtutorbench_pedagogy_hard` | `minimax-m2.7` | repo_eval | 6.8810 | `reports/eval/mathtutorbench_pedagogy_hard/_judge-deepseek-v4-flash/MiniMax-M2.7/summary.json` |
| rejected | `mathtutorbench_pedagogy_hard` | `minimax-m2.7` | repo_eval | 6.6210 | `reports/eval/mathtutorbench_pedagogy_hard/MiniMax-M2.7/summary.json` |
| selected | `mathtutorbench_pedagogy_hard` | `minimax-m3` | repo_eval | 7.8750 | `reports/eval/mathtutorbench_pedagogy_hard/minimax3/summary.json` |
| rejected | `mathtutorbench_pedagogy_hard` | `minimax-m3` | repo_eval | 7.9050 | `reports/eval/mathtutorbench_pedagogy_hard/_judge-deepseek-v4-flash/minimax3/summary.json` |
| selected | `mathtutorbench_scaffolding` | `deepseek-v4-pro` | repo_eval | 5.0040 | `reports/eval/mathtutorbench_scaffolding/deepseek-v4-pro/summary.json` |
| rejected | `mathtutorbench_scaffolding` | `deepseek-v4-pro` | repo_eval | 5.2650 | `reports/eval/mathtutorbench_scaffolding/_judge-deepseek-v4-flash/deepseek-v4-pro/summary.json` |
| selected | `mathtutorbench_scaffolding` | `doubao-seed-2-0-pro` | repo_eval | 3.4960 | `reports/eval/mathtutorbench_scaffolding/doubao-seed-2.0-pro/summary.json` |
| rejected | `mathtutorbench_scaffolding` | `doubao-seed-2-0-pro` | repo_eval | 3.5350 | `reports/eval/mathtutorbench_scaffolding/_judge-deepseek-v4-flash/doubao-seed-2.0-pro/summary.json` |
| selected | `mathtutorbench_scaffolding` | `glm-5.2` | repo_eval | 5.9480 | `reports/eval/mathtutorbench_scaffolding/glm-5.2/summary.json` |
| rejected | `mathtutorbench_scaffolding` | `glm-5.2` | repo_eval | 6.1910 | `reports/eval/mathtutorbench_scaffolding/_judge-deepseek-v4-flash/glm-5.2/summary.json` |
| selected | `mathtutorbench_scaffolding` | `minimax-m2.7` | repo_eval | 1.4780 | `reports/eval/mathtutorbench_scaffolding/_judge-deepseek-v4-flash/MiniMax-M2.7/summary.json` |
| rejected | `mathtutorbench_scaffolding` | `minimax-m2.7` | repo_eval | 1.4260 | `reports/eval/mathtutorbench_scaffolding/MiniMax-M2.7/summary.json` |

## MiniMax-M3 Path Conflicts

| Status | Benchmark | Metric | Value | Scored/Total | Inclusion | Path |
|---|---|---|---:|---:|---|---|
| not_selected | `agieval` | `accuracy` | None | 0/7272 | include_candidate | `reports/eval/agieval/2026-06-08/summary.json` |
| selected | `agieval` | `accuracy` | 0.8560814529444138 | 7268/7272 | include_candidate | `reports/eval/agieval/minimax3/summary.json` |
| not_selected | `bea2025_tutor` | `pass_rate` | 0.8912 | 294/300 | include_candidate | `reports/eval/bea2025_tutor/_judge-deepseek-v4-flash/minimax3/summary.json` |
| selected | `bea2025_tutor` | `pass_rate` | 0.82 | 300/300 | include_candidate | `reports/eval/bea2025_tutor/minimax3/summary.json` |
| selected | `edubench` | `accuracy` | None | 3797/3797 | include_candidate | `reports/eval/edubench/_judge-deepseek-v3.2/minimax-m3/summary.json` |
| not_selected | `edubench` | `accuracy` | None | 3796/3797 | include_candidate | `reports/eval/edubench/_judge-deepseek-v4-flash/minimax-m3/summary.json` |
| selected | `eduguard_adversarial` | `asr` | 0.0824 | 801/801 | include_candidate | `reports/eval/eduguard_adversarial/_judge-deepseek-v3.2/minimax3/summary.json` |
| not_selected | `eduguard_adversarial` | `asr` | 0.0492 | 793/801 | exclude_from_main | `reports/eval/eduguard_adversarial/_judge-deepseek-v4-flash/minimax3/summary.json` |
| not_selected | `eduguard_adversarial` | `asr` | 0.035 | 801/801 | exclude_from_main | `reports/eval/eduguard_adversarial/minimax3/summary.json` |
| selected | `eduillustrate` | `overall_mean_all_items` | 3.1748 | 230/230 | include_candidate | `reports/eval/eduillustrate/MiniMax-M3__gen-full230_judge-MiniMax-M3/summary.json` |
| not_selected | `eduillustrate` | `overall_mean_all_items` | 2.8241 | 5/5 | exclude_from_main | `reports/eval/eduillustrate/deepseek-v3.2/summary.json` |
| not_selected | `eduillustrate` | `overall_mean_all_items` | 2.8976 | 5/5 | exclude_from_main | `reports/eval/eduillustrate/doubao-seed-2.0-lite/summary.json` |
| not_selected | `eduillustrate` | `overall_mean_all_items` | 2.5007 | 5/5 | exclude_from_main | `reports/eval/eduillustrate/doubao-seed-2.0-pro/summary.json` |
| not_selected | `eduillustrate` | `overall_mean_all_items` | 2.9319 | 5/5 | exclude_from_main | `reports/eval/eduillustrate/minimax3/summary.json` |
| not_selected | `eduillustrate` | `overall_mean_all_items` | 2.9715 | 5/5 | exclude_from_main | `reports/eval/eduillustrate/opus-4.8/summary.json` |
| selected | `k12vista` | `accuracy` | 0.48123436196830693 | 1199/1200 | include_candidate | `reports/eval/k12vista/_sample-v3/minimax3/summary.json` |
| not_selected | `k12vista` | `accuracy` | 0.46488294314381273 | 598/600 | include_candidate | `reports/eval/k12vista/minimax3/summary.json` |
| not_selected | `mathtutorbench_pedagogy` | `accuracy` | 0.8139130434782609 | 1150/1150 | include_candidate | `reports/eval/mathtutorbench_pedagogy/_judge-deepseek-v4-flash/minimax3/summary.json` |
| selected | `mathtutorbench_pedagogy` | `accuracy` | 0.7930434782608695 | 1150/1150 | include_candidate | `reports/eval/mathtutorbench_pedagogy/minimax3/summary.json` |
| not_selected | `mathtutorbench_pedagogy_hard` | `accuracy` | 0.746177370030581 | 327/327 | include_candidate | `reports/eval/mathtutorbench_pedagogy_hard/_judge-deepseek-v4-flash/minimax3/summary.json` |
| selected | `mathtutorbench_pedagogy_hard` | `accuracy` | 0.7339449541284404 | 327/327 | include_candidate | `reports/eval/mathtutorbench_pedagogy_hard/minimax3/summary.json` |
| not_selected | `mathtutorbench_scaffolding` | `accuracy` | 0.23043478260869565 | 1150/1150 | include_candidate | `reports/eval/mathtutorbench_scaffolding/_judge-deepseek-v4-flash/minimax3/summary.json` |
| selected | `mathtutorbench_scaffolding` | `accuracy` | 0.22956521739130434 | 1150/1150 | include_candidate | `reports/eval/mathtutorbench_scaffolding/minimax3/summary.json` |
| not_selected | `mathtutorbench_scaffolding_hard` | `accuracy` | 0.1712538226299694 | 327/327 | include_candidate | `reports/eval/mathtutorbench_scaffolding_hard/_judge-deepseek-v4-flash/minimax3/summary.json` |
| selected | `mathtutorbench_scaffolding_hard` | `accuracy` | 0.18960244648318042 | 327/327 | include_candidate | `reports/eval/mathtutorbench_scaffolding_hard/minimax3/summary.json` |
| not_selected | `mathvista` | `accuracy` | 0.8408862034239678 | 993/1000 | include_candidate | `reports/eval/mathvista/2026-06-06/summary.json` |
| selected | `mathvista` | `accuracy` | 0.8408862034239678 | 993/1000 | include_candidate | `reports/eval/mathvista/minimax3/summary.json` |
| not_selected | `mmlu_pro` | `accuracy` | 0.8137863443319177 | 3061/12032 | include_candidate | `reports/eval/mmlu_pro/2026-06-07/summary.json` |
| selected | `mmlu_pro` | `accuracy` | 0.8555518617021277 | 12032/12032 | include_candidate | `reports/eval/mmlu_pro/minimax3/summary.json` |
| not_selected | `mmtutorbench` | `accuracy` | 0.09492847854356307 | 769/770 | include_candidate | `reports/eval/mmtutorbench/_judge-deepseek-v4-flash/minimax3/summary.json` |
| selected | `mmtutorbench` | `accuracy` | 0.033810143042912875 | 769/770 | include_candidate | `reports/eval/mmtutorbench/minimax3/summary.json` |
| not_selected | `mrbench_tutor` | `pass_rate` | 0.9045 | 199/200 | include_candidate | `reports/eval/mrbench_tutor/_judge-deepseek-v4-flash/minimax3/summary.json` |
| selected | `mrbench_tutor` | `pass_rate` | 0.83 | 200/200 | include_candidate | `reports/eval/mrbench_tutor/minimax3/summary.json` |
| not_selected | `olympiadbench` | `accuracy` | 0.896640826873385 | 387/6728 | include_candidate | `reports/eval/olympiadbench/2026-06-08/summary.json` |
| not_selected | `olympiadbench` | `unknown` | None | 0/0 | exclude_from_main | `reports/eval/olympiadbench/_mini_v1/MiniMax-M3/summary.json` |
| not_selected | `olympiadbench` | `unknown` | None | 0/0 | exclude_from_main | `reports/eval/olympiadbench/_noimage/MiniMax-M3_uncapped_full_2026-07-23/summary.json` |
| not_selected | `olympiadbench` | `accuracy` | None | 0/6 | exclude_from_main | `reports/eval/olympiadbench/_noimage/_minimax_verbosity_probe/summary.json` |
| selected | `olympiadbench` | `accuracy` | 0.7160071407319251 | 6722/6728 | include_candidate | `reports/eval/olympiadbench/minimax3/summary.json` |
| not_selected | `olympiadbench` | `accuracy` | 0.4523809523809524 | 42/6728 | exclude_from_main | `reports/eval/olympiadbench/summary.json` |
| selected | `tutorbench` | `accuracy` | None | 1440/1473 | include_candidate | `reports/eval/tutorbench/_judge-deepseek-v4-flash/minimax3/summary.json` |
| not_selected | `tutorbench` | `accuracy` | None | 1440/1473 | include_candidate | `reports/eval/tutorbench/_m3_fullset_20260723/summary.json` |
| not_selected | `tutorbench` | `accuracy` | None | 6/6 | exclude_from_main | `reports/eval/tutorbench/minimax3/summary.json` |

Full records are in `07_run_deduplication_report.jsonl`.
