# Atomic P Scores

P-score rows: 188
Covered P codes: P01, P02, P03, P04, P05, P06, P07, P09, P10, P11, P12, P13, P14, P15, P16, P17, P18, P19
Missing P codes: P08, P20

`score_10` (R20 single scheme): facet-weighted average with effective weight = relevance × confidence. Coverage completeness is reported separately and is not folded back into the score.

## Sample Scores

| Model key | P | Group | Score | Evidence | Weight sum | Benchmarks |
|---|---|---|---:|---:|---:|---|
| `claude-sonnet-4.6` | `P04` 知识调用与掌握 | FDR | 8.7625 | 4 | 1.16 | edubench, pedagogy_benchmark |
| `claude-sonnet-4.6` | `P05` 推理与生成 | FDR | 8.4166 | 2 | 0.44 | edubench |
| `claude-sonnet-4.6` | `P09` 错误诊断 | LAD | 6.074 | 1 | 0.2 | edubench |
| `claude-sonnet-4.6` | `P10` 主观题评价能力 | LAD | 6.106 | 1 | 0.52 | asap_2 |
| `claude-sonnet-4.6` | `P11` 命题与作业设计 | LAD | 8.043 | 1 | 0.3 | edubench |
| `claude-sonnet-4.6` | `P12` 学习者画像建模 | CLM | 7.1429 | 2 | 0.52 | edubench, pedagogy_benchmark |
| `claude-sonnet-4.6` | `P13` 个性化教学策略选择 | CLM | 7.5116 | 4 | 1.04 | edubench, pedagogy_benchmark |
| `claude-sonnet-4.6` | `P15` 适配性解释与反馈生成 | CLM | 7.9043 | 5 | 1.1 | edubench |
| `deepseek-r1-0528-qwen3-8b` | `P04` 知识调用与掌握 | FDR | 6.8453 | 2 | 0.64 | pedagogy_benchmark |
| `deepseek-r1-0528-qwen3-8b` | `P12` 学习者画像建模 | CLM | 6.6364 | 1 | 0.28 | pedagogy_benchmark |
| `deepseek-r1-0528-qwen3-8b` | `P13` 个性化教学策略选择 | CLM | 6.8364 | 2 | 0.52 | pedagogy_benchmark |
| `deepseek-v4-flash` | `P02` 长上下文与证据定位 | SRG | 7.74 | 1 | 0.15 | mathtutorbench_mistake_location |
| `deepseek-v4-flash` | `P04` 知识调用与掌握 | FDR | 7.8989 | 12 | 3.1675 | agieval, ceval, edubench, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_problem_solving, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard, mmlu_pro, pedagogy_benchmark |
| `deepseek-v4-flash` | `P05` 推理与生成 | FDR | 8.7747 | 7 | 1.59 | agieval, ceval, edubench, mathtutorbench_mistake_correction, mathtutorbench_problem_solving, mmlu_pro |
| `deepseek-v4-flash` | `P06` 自我校验与修正 | FDR | 8.567 | 1 | 0.2125 | mathtutorbench_solution_correctness |
| `deepseek-v4-flash` | `P09` 错误诊断 | LAD | 7.9888 | 4 | 1.59 | edubench, mathtutorbench_mistake_correction, mathtutorbench_mistake_location, mathtutorbench_solution_correctness |
| `deepseek-v4-flash` | `P10` 主观题评价能力 | LAD | 5.078 | 1 | 0.52 | asap_2 |
| `deepseek-v4-flash` | `P11` 命题与作业设计 | LAD | 8.09 | 1 | 0.3 | edubench |
| `deepseek-v4-flash` | `P12` 学习者画像建模 | CLM | 7.1113 | 2 | 0.52 | edubench, pedagogy_benchmark |
| `deepseek-v4-flash` | `P13` 个性化教学策略选择 | CLM | 6.601 | 8 | 2.9175 | edubench, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard, pedagogy_benchmark |
| `deepseek-v4-flash` | `P15` 适配性解释与反馈生成 | CLM | 7.1913 | 10 | 2.7 | edubench, mathtutorbench_mistake_correction, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard |
| `deepseek-v4-pro` | `P01` 指令与约束遵循 | SRG | 9.2222 | 1 | 0.8 | ifeval |
| `deepseek-v4-pro` | `P02` 长上下文与证据定位 | SRG | 7.8748 | 5 | 1.8675 | longtutor_evidence, mathtutorbench_mistake_location, sas_bench |
| `deepseek-v4-pro` | `P03` 多模态理解 | SRG | 5.079 | 1 | 0.2 | tutorbench |
| `deepseek-v4-pro` | `P04` 知识调用与掌握 | FDR | 8.0728 | 14 | 3.5425 | agieval, ceval, edubench, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_problem_solving, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard, mmlu_pro, olympiadbench, pedagogy_benchmark, sas_bench |
| `deepseek-v4-pro` | `P05` 推理与生成 | FDR | 8.2317 | 9 | 2.075 | agieval, ceval, edubench, mathtutorbench_mistake_correction, mathtutorbench_problem_solving, mmlu_pro, olympiadbench, sas_bench |
| `deepseek-v4-pro` | `P06` 自我校验与修正 | FDR | 6.3382 | 3 | 1.105 | mathtutorbench_solution_correctness, p07_selfcheck, p08_calibration |
| `deepseek-v4-pro` | `P07` 置信度校准与弃答 | FDR | 7.8082 | 3 | 1.53 | p07_selfcheck, p08_abstention, p08_calibration |
| `deepseek-v4-pro` | `P09` 错误诊断 | LAD | 7.8549 | 9 | 3.0275 | bea2025_tutor, edubench, longtutor_diagnosis, mathtutorbench_mistake_correction, mathtutorbench_mistake_location, mathtutorbench_solution_correctness, mrbench_tutor, sas_bench |
| `deepseek-v4-pro` | `P10` 主观题评价能力 | LAD | 7.2567 | 3 | 1.6725 | asap_2, sas_bench |
| `deepseek-v4-pro` | `P11` 命题与作业设计 | LAD | 8.3472 | 1 | 0.3 | edubench |
| `deepseek-v4-pro` | `P12` 学习者画像建模 | CLM | 5.2433 | 3 | 0.745 | edubench, longtutor_diagnosis, pedagogy_benchmark |
| `deepseek-v4-pro` | `P13` 个性化教学策略选择 | CLM | 7.3939 | 13 | 4.3225 | bea2025_tutor, edubench, longtutor_teaching, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard, mathtutorbench_socratic, mrbench_tutor, pedagogy_benchmark, tutorbench |
| `deepseek-v4-pro` | `P14` 学习路径规划（知识结构层） | CLM | 3.789 | 1 | 0.49 | mooccube_prereq |
| `deepseek-v4-pro` | `P15` 适配性解释与反馈生成 | CLM | 7.1701 | 16 | 3.985 | bea2025_tutor, edubench, eduillustrate, mathtutorbench_mistake_correction, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard, mathtutorbench_socratic, mrbench_tutor, tutorbench |
| `deepseek-v4-pro` | `P16` 多模态教学产物生成 | FDR | 6.3496 | 1 | 0.3825 | eduillustrate |
| `deepseek-v4-pro` | `P17` 教育角色边界判断 | CEG | 6.8189 | 4 | 0.955 | eduguard_adversarial, eduguard_sata, mrbench_tutor |
| `deepseek-v4-pro` | `P18` 学生风险识别 | CEG | 7.612 | 1 | 0.3 | eduguard_sata |
| `deepseek-v4-pro` | `P19` 安全处置选择 | CEG | 5.9689 | 3 | 1.22 | eduguard_adversarial, eduguard_sata |
| `doubao-seed-2-0-lite` | `P04` 知识调用与掌握 | FDR | 7.5584 | 6 | 1.3075 | edubench, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard |
| `doubao-seed-2-0-lite` | `P05` 推理与生成 | FDR | 8.2548 | 2 | 0.44 | edubench |
| `doubao-seed-2-0-lite` | `P09` 错误诊断 | LAD | 6.3803 | 1 | 0.2 | edubench |
| `doubao-seed-2-0-lite` | `P11` 命题与作业设计 | LAD | 8.1386 | 1 | 0.3 | edubench |
| `doubao-seed-2-0-lite` | `P12` 学习者画像建模 | CLM | 6.3047 | 1 | 0.24 | edubench |
| `doubao-seed-2-0-lite` | `P13` 个性化教学策略选择 | CLM | 5.476 | 6 | 2.3975 | edubench, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard |
| `doubao-seed-2-0-lite` | `P15` 适配性解释与反馈生成 | CLM | 6.7519 | 10 | 2.64 | edubench, eduillustrate, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard |
| `doubao-seed-2-0-lite` | `P16` 多模态教学产物生成 | FDR | 6.777 | 1 | 0.3825 | eduillustrate |
| `doubao-seed-2-0-lite` | `P17` 教育角色边界判断 | CEG | 6.3323 | 3 | 0.755 | eduguard_adversarial, eduguard_sata |
| `doubao-seed-2-0-lite` | `P18` 学生风险识别 | CEG | 7.3 | 1 | 0.3 | eduguard_sata |
| `doubao-seed-2-0-lite` | `P19` 安全处置选择 | CEG | 6.5377 | 3 | 1.22 | eduguard_adversarial, eduguard_sata |
| `doubao-seed-2-0-pro` | `P01` 指令与约束遵循 | SRG | 8.9464 | 1 | 0.8 | ifeval |
| `doubao-seed-2-0-pro` | `P02` 长上下文与证据定位 | SRG | 7.2006 | 5 | 1.8675 | longtutor_evidence, mathtutorbench_mistake_location, sas_bench |
| `doubao-seed-2-0-pro` | `P03` 多模态理解 | SRG | 7.1801 | 4 | 1.19 | k12vista, mmtutorbench, tutorbench |
| `doubao-seed-2-0-pro` | `P04` 知识调用与掌握 | FDR | 7.9708 | 14 | 3.4875 | agieval, ceval, edubench, k12vista, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_problem_solving, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard, mmlu_pro, pedagogy_benchmark, sas_bench |
| `doubao-seed-2-0-pro` | `P05` 推理与生成 | FDR | 8.3771 | 9 | 1.93 | agieval, ceval, edubench, k12vista, mathtutorbench_mistake_correction, mathtutorbench_problem_solving, mmlu_pro, sas_bench |
| `doubao-seed-2-0-pro` | `P06` 自我校验与修正 | FDR | 5.9682 | 3 | 1.105 | mathtutorbench_solution_correctness, p07_selfcheck, p08_calibration |
| `doubao-seed-2-0-pro` | `P07` 置信度校准与弃答 | FDR | 7.73 | 3 | 1.53 | p07_selfcheck, p08_abstention, p08_calibration |
| `doubao-seed-2-0-pro` | `P09` 错误诊断 | LAD | 7.6429 | 9 | 3.0275 | bea2025_tutor, edubench, longtutor_diagnosis, mathtutorbench_mistake_correction, mathtutorbench_mistake_location, mathtutorbench_solution_correctness, mrbench_tutor, sas_bench |
| `doubao-seed-2-0-pro` | `P10` 主观题评价能力 | LAD | 7.1199 | 3 | 1.6725 | asap_2, sas_bench |
| `doubao-seed-2-0-pro` | `P11` 命题与作业设计 | LAD | 7.7543 | 1 | 0.3 | edubench |
| `doubao-seed-2-0-pro` | `P12` 学习者画像建模 | CLM | 4.6828 | 3 | 0.745 | edubench, longtutor_diagnosis, pedagogy_benchmark |
| `doubao-seed-2-0-pro` | `P13` 个性化教学策略选择 | CLM | 7.2735 | 14 | 4.5925 | bea2025_tutor, edubench, longtutor_teaching, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard, mathtutorbench_socratic, mmtutorbench, mrbench_tutor, pedagogy_benchmark, tutorbench |
| `doubao-seed-2-0-pro` | `P14` 学习路径规划（知识结构层） | CLM | 4.486 | 1 | 0.49 | mooccube_prereq |
| `doubao-seed-2-0-pro` | `P15` 适配性解释与反馈生成 | CLM | 7.4515 | 17 | 4.345 | bea2025_tutor, edubench, eduillustrate, mathtutorbench_mistake_correction, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard, mathtutorbench_socratic, mmtutorbench, mrbench_tutor, tutorbench |
| `doubao-seed-2-0-pro` | `P16` 多模态教学产物生成 | FDR | 7.411 | 1 | 0.3825 | eduillustrate |
| `doubao-seed-2-0-pro` | `P17` 教育角色边界判断 | CEG | 6.9959 | 4 | 0.955 | eduguard_adversarial, eduguard_sata, mrbench_tutor |
| `doubao-seed-2-0-pro` | `P18` 学生风险识别 | CEG | 7.618 | 1 | 0.3 | eduguard_sata |
| `doubao-seed-2-0-pro` | `P19` 安全处置选择 | CEG | 6.3628 | 3 | 1.22 | eduguard_adversarial, eduguard_sata |
| `glm-5.1` | `P02` 长上下文与证据定位 | SRG | 7.8142 | 1 | 0.1425 | sas_bench |
| `glm-5.1` | `P04` 知识调用与掌握 | FDR | 8.2002 | 5 | 1.36 | edubench, pedagogy_benchmark, sas_bench |
| `glm-5.1` | `P05` 推理与生成 | FDR | 7.2726 | 3 | 0.54 | edubench, sas_bench |
| `glm-5.1` | `P09` 错误诊断 | LAD | 7.3016 | 3 | 1.1375 | edubench, sas_bench |
| `glm-5.1` | `P10` 主观题评价能力 | LAD | 7.4903 | 3 | 1.6725 | asap_2, sas_bench |
| `glm-5.1` | `P11` 命题与作业设计 | LAD | 8.1315 | 1 | 0.3 | edubench |
| `glm-5.1` | `P12` 学习者画像建模 | CLM | 7.3433 | 2 | 0.52 | edubench, pedagogy_benchmark |
| `glm-5.1` | `P13` 个性化教学策略选择 | CLM | 7.6765 | 4 | 1.04 | edubench, pedagogy_benchmark |
| `glm-5.1` | `P15` 适配性解释与反馈生成 | CLM | 7.161 | 5 | 1.1 | edubench |
| `glm-5.1` | `P17` 教育角色边界判断 | CEG | 8.3495 | 3 | 0.755 | eduguard_adversarial, eduguard_sata |
| `glm-5.1` | `P18` 学生风险识别 | CEG | 7.632 | 1 | 0.3 | eduguard_sata |
| `glm-5.1` | `P19` 安全处置选择 | CEG | 8.1594 | 3 | 1.22 | eduguard_adversarial, eduguard_sata |
| `glm-5.2` | `P01` 指令与约束遵循 | SRG | 9.2976 | 1 | 0.8 | ifeval |
| `glm-5.2` | `P02` 长上下文与证据定位 | SRG | 8.0373 | 5 | 1.8675 | longtutor_evidence, mathtutorbench_mistake_location, sas_bench |
| `glm-5.2` | `P03` 多模态理解 | SRG | 5.079 | 1 | 0.2 | tutorbench |
| `glm-5.2` | `P04` 知识调用与掌握 | FDR | 7.7418 | 13 | 3.3675 | agieval, ceval, edubench, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_problem_solving, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard, mmlu_pro, pedagogy_benchmark, sas_bench |
| `glm-5.2` | `P05` 推理与生成 | FDR | 8.1369 | 8 | 1.69 | agieval, ceval, edubench, mathtutorbench_mistake_correction, mathtutorbench_problem_solving, mmlu_pro, sas_bench |
| `glm-5.2` | `P06` 自我校验与修正 | FDR | 6.3022 | 3 | 1.105 | mathtutorbench_solution_correctness, p07_selfcheck, p08_calibration |
| `glm-5.2` | `P07` 置信度校准与弃答 | FDR | 7.7569 | 3 | 1.53 | p07_selfcheck, p08_abstention, p08_calibration |
| `glm-5.2` | `P09` 错误诊断 | LAD | 7.6075 | 9 | 3.0275 | bea2025_tutor, edubench, longtutor_diagnosis, mathtutorbench_mistake_correction, mathtutorbench_mistake_location, mathtutorbench_solution_correctness, mrbench_tutor, sas_bench |
| `glm-5.2` | `P10` 主观题评价能力 | LAD | 7.3031 | 3 | 1.6725 | asap_2, sas_bench |
| `glm-5.2` | `P11` 命题与作业设计 | LAD | 7.3499 | 1 | 0.3 | edubench |
| `glm-5.2` | `P12` 学习者画像建模 | CLM | 4.2239 | 3 | 0.745 | edubench, longtutor_diagnosis, pedagogy_benchmark |
| `glm-5.2` | `P13` 个性化教学策略选择 | CLM | 6.7382 | 13 | 4.3225 | bea2025_tutor, edubench, longtutor_teaching, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard, mathtutorbench_socratic, mrbench_tutor, pedagogy_benchmark, tutorbench |
| `glm-5.2` | `P14` 学习路径规划（知识结构层） | CLM | 3.911 | 1 | 0.49 | mooccube_prereq |
| `glm-5.2` | `P15` 适配性解释与反馈生成 | CLM | 7.0615 | 16 | 3.985 | bea2025_tutor, edubench, eduillustrate, mathtutorbench_mistake_correction, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard, mathtutorbench_socratic, mrbench_tutor, tutorbench |
| `glm-5.2` | `P16` 多模态教学产物生成 | FDR | 6.3496 | 1 | 0.3825 | eduillustrate |
| `glm-5.2` | `P17` 教育角色边界判断 | CEG | 7.6255 | 4 | 0.955 | eduguard_adversarial, eduguard_sata, mrbench_tutor |
| `glm-5.2` | `P18` 学生风险识别 | CEG | 7.595 | 1 | 0.3 | eduguard_sata |
| `glm-5.2` | `P19` 安全处置选择 | CEG | 6.7641 | 3 | 1.22 | eduguard_adversarial, eduguard_sata |
| `gpt-5.4` | `P02` 长上下文与证据定位 | SRG | 8.0261 | 1 | 0.1425 | sas_bench |
| `gpt-5.4` | `P04` 知识调用与掌握 | FDR | 6.9276 | 3 | 0.84 | pedagogy_benchmark, sas_bench |
| `gpt-5.4` | `P05` 推理与生成 | FDR | 5.5636 | 1 | 0.1 | sas_bench |
| `gpt-5.4` | `P09` 错误诊断 | LAD | 6.7949 | 2 | 0.9375 | sas_bench |
| `gpt-5.4` | `P10` 主观题评价能力 | LAD | 7.4582 | 3 | 1.6725 | asap_2, sas_bench |
| `gpt-5.4` | `P12` 学习者画像建模 | CLM | 7.9545 | 1 | 0.28 | pedagogy_benchmark |
| `gpt-5.4` | `P13` 个性化教学策略选择 | CLM | 8.2773 | 2 | 0.52 | pedagogy_benchmark |
| `gpt-5.5` | `P03` 多模态理解 | SRG | 5.757 | 1 | 0.2 | tutorbench |
| `gpt-5.5` | `P13` 个性化教学策略选择 | CLM | 5.757 | 1 | 0.28 | tutorbench |
| `gpt-5.5` | `P15` 适配性解释与反馈生成 | CLM | 5.757 | 1 | 0.32 | tutorbench |
| `gpt-5.5` | `P17` 教育角色边界判断 | CEG | 8.4564 | 3 | 0.755 | eduguard_adversarial, eduguard_sata |
| `gpt-5.5` | `P18` 学生风险识别 | CEG | 7.395 | 1 | 0.3 | eduguard_sata |
| `gpt-5.5` | `P19` 安全处置选择 | CEG | 8.265 | 3 | 1.22 | eduguard_adversarial, eduguard_sata |
| `kimi-k2-6` | `P02` 长上下文与证据定位 | SRG | 7.3299 | 1 | 0.1425 | sas_bench |
| `kimi-k2-6` | `P04` 知识调用与掌握 | FDR | 8.0639 | 5 | 1.36 | edubench, pedagogy_benchmark, sas_bench |
| `kimi-k2-6` | `P05` 推理与生成 | FDR | 7.3514 | 3 | 0.54 | edubench, sas_bench |
| `kimi-k2-6` | `P09` 错误诊断 | LAD | 6.3845 | 3 | 1.1375 | edubench, sas_bench |
| `kimi-k2-6` | `P10` 主观题评价能力 | LAD | 7.6214 | 2 | 1.1525 | sas_bench |
| `kimi-k2-6` | `P11` 命题与作业设计 | LAD | 8.205 | 1 | 0.3 | edubench |
| `kimi-k2-6` | `P12` 学习者画像建模 | CLM | 7.0136 | 2 | 0.52 | edubench, pedagogy_benchmark |
| `kimi-k2-6` | `P13` 个性化教学策略选择 | CLM | 7.3762 | 4 | 1.04 | edubench, pedagogy_benchmark |
| `kimi-k2-6` | `P15` 适配性解释与反馈生成 | CLM | 7.621 | 5 | 1.1 | edubench |

## Coverage Notes

- `P17`-`P19` are covered through EduGuard P1/P2 safety evidence.
- `P08` (tool use / long-horizon) and `P20` (academic integrity) are declared domain gaps; `P16`/`P14` are single-source and `P12` covers 2 of 4 declared sub-abilities; `P18` has zero independent evidence (shared-SATA single cell) and `P11` is expression-quality-only.
- The atomic list is `P01-P20` (R20 doc-scheme renumbering, no tombstones).

Full P rows are in `09_atomic_p_scores.jsonl`; allocated evidence rows are in `09_atomic_p_score_evidence.jsonl`.
