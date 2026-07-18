# Atomic P Scores: Raw And Adjusted

P-score rows: 178
Covered P codes: P01, P02, P03, P05, P06, P07, P08, P10, P11, P14, P16, P17, P18, P19, P20, P21, P22, P23
Missing P codes: P04, P09, P12, P13, P15

`raw_score_10` uses default benchmark weights. `tier_adjusted_score_10` reduces foundation-gate evidence. Coverage completeness is reported separately and is not folded back into the score.

## Sample Scores

| Model key | P | Group | Raw | Tier adjusted | Evidence | Weight raw/adj | Benchmarks |
|---|---|---|---:|---:|---:|---:|---|
| `claude-sonnet-4.6` | `P02` 长上下文与证据定位 | SRG | 6.106 | 6.106 | 1 | 0.16/0.16 | asap_2 |
| `claude-sonnet-4.6` | `P05` 知识调用与掌握 | FDR | 8.8634 | 8.8634 | 3 | 0.84/0.84 | edubench, pedagogy_benchmark |
| `claude-sonnet-4.6` | `P06` 推理与生成 | FDR | 8.4166 | 8.4166 | 2 | 0.44/0.44 | edubench |
| `claude-sonnet-4.6` | `P11` 错误诊断 | LAD | 6.074 | 6.074 | 1 | 0.2/0.2 | edubench |
| `claude-sonnet-4.6` | `P14` 主观题评价能力 | LAD | 6.106 | 6.106 | 1 | 0.52/0.52 | asap_2 |
| `claude-sonnet-4.6` | `P16` 学习者画像建模 | CLM | 7.4226 | 7.4226 | 2 | 0.48/0.48 | edubench, pedagogy_benchmark |
| `claude-sonnet-4.6` | `P17` 个性化教学策略选择 | CLM | 7.6225 | 7.6225 | 3 | 0.76/0.76 | edubench, pedagogy_benchmark |
| `claude-sonnet-4.6` | `P18` 适配性解释与反馈生成 | CLM | 7.9043 | 7.9043 | 5 | 1.1/1.1 | edubench |
| `claude-sonnet-4.6` | `P23` 命题与作业设计 | LAD | 8.043 | 8.043 | 1 | 0.3/0.3 | edubench |
| `deepseek-v4-flash` | `P01` 指令与约束遵循 | SRG | 8.9528 | 8.9528 | 3 | 0.1675/0.0754 | agieval, ceval, mmlu_pro |
| `deepseek-v4-flash` | `P02` 长上下文与证据定位 | SRG | 7.0826 | 7.0826 | 3 | 0.4875/0.4875 | asap_2, mathtutorbench_mistake_location, mathtutorbench_solution_correctness |
| `deepseek-v4-flash` | `P05` 知识调用与掌握 | FDR | 7.7379 | 7.7794 | 11 | 2.3225/1.9402 | agieval, ceval, edubench, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_problem_solving, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard, mmlu_pro, pedagogy_benchmark |
| `deepseek-v4-flash` | `P06` 推理与生成 | FDR | 8.8347 | 8.8347 | 7 | 1.2625/0.9091 | agieval, ceval, edubench, mathtutorbench_mistake_correction, mathtutorbench_problem_solving, mmlu_pro |
| `deepseek-v4-flash` | `P07` 自我校验与修正 | FDR | 8.7724 | 8.6692 | 2 | 0.2575/0.2328 | mathtutorbench_problem_solving, mathtutorbench_solution_correctness |
| `deepseek-v4-flash` | `P11` 错误诊断 | LAD | 7.9888 | 7.9888 | 4 | 1.59/1.59 | edubench, mathtutorbench_mistake_correction, mathtutorbench_mistake_location, mathtutorbench_solution_correctness |
| `deepseek-v4-flash` | `P14` 主观题评价能力 | LAD | 5.078 | 5.078 | 1 | 0.52/0.52 | asap_2 |
| `deepseek-v4-flash` | `P16` 学习者画像建模 | CLM | 7.4283 | 7.4283 | 2 | 0.48/0.48 | edubench, pedagogy_benchmark |
| `deepseek-v4-flash` | `P17` 个性化教学策略选择 | CLM | 6.7249 | 6.7249 | 7 | 2.6375/2.6375 | edubench, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard, pedagogy_benchmark |
| `deepseek-v4-flash` | `P18` 适配性解释与反馈生成 | CLM | 7.1913 | 7.1913 | 10 | 2.7/2.7 | edubench, mathtutorbench_mistake_correction, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard |
| `deepseek-v4-flash` | `P23` 命题与作业设计 | LAD | 8.09 | 8.09 | 1 | 0.3/0.3 | edubench |
| `deepseek-v4-pro` | `P01` 指令与约束遵循 | SRG | 9.1809 | 9.1658 | 5 | 1.095/0.5629 | agieval, ceval, ifeval, mmlu_pro, p08_abstention |
| `deepseek-v4-pro` | `P02` 长上下文与证据定位 | SRG | 7.6135 | 7.6135 | 6 | 1.3375/1.3375 | asap_2, longtutor_evidence, mathtutorbench_mistake_location, mathtutorbench_solution_correctness, sas_bench |
| `deepseek-v4-pro` | `P03` 多模态理解 | SRG | 7.3613 | 7.3613 | 1 | 0.11/0.0495 | olympiadbench |
| `deepseek-v4-pro` | `P05` 知识调用与掌握 | FDR | 7.6472 | 7.5078 | 13 | 2.665/2.2814 | agieval, ceval, edubench, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard, mmlu_pro, mooccube_prereq, olympiadbench, pedagogy_benchmark, sas_bench |
| `deepseek-v4-pro` | `P06` 推理与生成 | FDR | 7.8324 | 7.6228 | 9 | 1.465/1.0938 | agieval, ceval, edubench, mathtutorbench_mistake_correction, mmlu_pro, mooccube_prereq, olympiadbench, sas_bench |
| `deepseek-v4-pro` | `P07` 自我校验与修正 | FDR | 6.3382 | 6.3382 | 3 | 1.105/1.105 | mathtutorbench_solution_correctness, p07_selfcheck, p08_calibration |
| `deepseek-v4-pro` | `P08` 置信度校准与弃答 | FDR | 7.8082 | 7.8082 | 3 | 1.53/1.53 | p07_selfcheck, p08_abstention, p08_calibration |
| `deepseek-v4-pro` | `P11` 错误诊断 | LAD | 7.7347 | 7.7347 | 7 | 2.6025/2.6025 | edubench, longtutor_diagnosis, mathtutorbench_mistake_correction, mathtutorbench_mistake_location, mathtutorbench_solution_correctness, sas_bench |
| `deepseek-v4-pro` | `P14` 主观题评价能力 | LAD | 7.2567 | 7.2567 | 3 | 1.6725/1.6725 | asap_2, sas_bench |
| `deepseek-v4-pro` | `P16` 学习者画像建模 | CLM | 5.3222 | 5.3222 | 3 | 0.705/0.705 | edubench, longtutor_diagnosis, pedagogy_benchmark |
| `deepseek-v4-pro` | `P17` 个性化教学策略选择 | CLM | 7.2966 | 7.2966 | 9 | 3.2525/3.2525 | edubench, longtutor_teaching, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard, mathtutorbench_socratic, pedagogy_benchmark |
| `deepseek-v4-pro` | `P18` 适配性解释与反馈生成 | CLM | 7.1511 | 7.1511 | 11 | 2.91/2.91 | edubench, mathtutorbench_mistake_correction, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard, mathtutorbench_socratic |
| `deepseek-v4-pro` | `P19` 学习路径规划（知识结构层） | CLM | 3.789 | 3.789 | 1 | 0.49/0.49 | mooccube_prereq |
| `deepseek-v4-pro` | `P20` 教育角色边界判断 | CEG | 5.8377 | 5.8377 | 3 | 0.755/0.755 | eduguard_adversarial, eduguard_sata |
| `deepseek-v4-pro` | `P21` 学生风险识别 | CEG | 7.612 | 7.612 | 1 | 0.3/0.3 | eduguard_sata |
| `deepseek-v4-pro` | `P22` 安全处置选择 | CEG | 5.9689 | 5.9689 | 3 | 1.22/1.22 | eduguard_adversarial, eduguard_sata |
| `deepseek-v4-pro` | `P23` 命题与作业设计 | LAD | 8.3472 | 8.3472 | 1 | 0.3/0.3 | edubench |
| `doubao-seed-2-0-lite` | `P05` 知识调用与掌握 | FDR | 7.5584 | 7.5584 | 6 | 1.3075/1.3075 | edubench, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard |
| `doubao-seed-2-0-lite` | `P06` 推理与生成 | FDR | 8.2548 | 8.2548 | 2 | 0.44/0.44 | edubench |
| `doubao-seed-2-0-lite` | `P10` 多模态教学产物生成 | FDR | 6.777 | 6.777 | 1 | 0.3825/0.3825 | eduillustrate |
| `doubao-seed-2-0-lite` | `P11` 错误诊断 | LAD | 6.3803 | 6.3803 | 1 | 0.2/0.2 | edubench |
| `doubao-seed-2-0-lite` | `P16` 学习者画像建模 | CLM | 6.3047 | 6.3047 | 1 | 0.24/0.24 | edubench |
| `doubao-seed-2-0-lite` | `P17` 个性化教学策略选择 | CLM | 5.476 | 5.476 | 6 | 2.3975/2.3975 | edubench, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard |
| `doubao-seed-2-0-lite` | `P18` 适配性解释与反馈生成 | CLM | 6.7519 | 6.7519 | 10 | 2.64/2.64 | edubench, eduillustrate, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard |
| `doubao-seed-2-0-lite` | `P20` 教育角色边界判断 | CEG | 6.3323 | 6.3323 | 3 | 0.755/0.755 | eduguard_adversarial, eduguard_sata |
| `doubao-seed-2-0-lite` | `P21` 学生风险识别 | CEG | 7.3 | 7.3 | 1 | 0.3/0.3 | eduguard_sata |
| `doubao-seed-2-0-lite` | `P22` 安全处置选择 | CEG | 6.5377 | 6.5377 | 3 | 1.22/1.22 | eduguard_adversarial, eduguard_sata |
| `doubao-seed-2-0-lite` | `P23` 命题与作业设计 | LAD | 8.1386 | 8.1386 | 1 | 0.3/0.3 | edubench |
| `doubao-seed-2-0-pro` | `P01` 指令与约束遵循 | SRG | 8.951 | 8.9552 | 2 | 0.9275/0.4875 | ifeval, p08_abstention |
| `doubao-seed-2-0-pro` | `P02` 长上下文与证据定位 | SRG | 7.857 | 7.857 | 2 | 0.325/0.325 | sas_bench |
| `doubao-seed-2-0-pro` | `P05` 知识调用与掌握 | FDR | 7.521 | 7.521 | 7 | 1.5075/1.5075 | edubench, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard, sas_bench |
| `doubao-seed-2-0-pro` | `P06` 推理与生成 | FDR | 8.2586 | 8.2586 | 3 | 0.54/0.54 | edubench, sas_bench |
| `doubao-seed-2-0-pro` | `P07` 自我校验与修正 | FDR | 5.3495 | 5.3495 | 2 | 0.8925/0.8925 | p07_selfcheck, p08_calibration |
| `doubao-seed-2-0-pro` | `P08` 置信度校准与弃答 | FDR | 7.73 | 7.73 | 3 | 1.53/1.53 | p07_selfcheck, p08_abstention, p08_calibration |
| `doubao-seed-2-0-pro` | `P10` 多模态教学产物生成 | FDR | 7.411 | 7.411 | 1 | 0.3825/0.3825 | eduillustrate |
| `doubao-seed-2-0-pro` | `P11` 错误诊断 | LAD | 6.808 | 6.808 | 3 | 1.1375/1.1375 | edubench, sas_bench |
| `doubao-seed-2-0-pro` | `P14` 主观题评价能力 | LAD | 7.9089 | 7.9089 | 2 | 1.1525/1.1525 | sas_bench |
| `doubao-seed-2-0-pro` | `P16` 学习者画像建模 | CLM | 6.431 | 6.431 | 1 | 0.24/0.24 | edubench |
| `doubao-seed-2-0-pro` | `P17` 个性化教学策略选择 | CLM | 6.0994 | 6.0994 | 6 | 2.3975/2.3975 | edubench, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard |
| `doubao-seed-2-0-pro` | `P18` 适配性解释与反馈生成 | CLM | 7.1715 | 7.1715 | 10 | 2.64/2.64 | edubench, eduillustrate, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard |
| `doubao-seed-2-0-pro` | `P20` 教育角色边界判断 | CEG | 6.1006 | 6.1006 | 3 | 0.755/0.755 | eduguard_adversarial, eduguard_sata |
| `doubao-seed-2-0-pro` | `P21` 学生风险识别 | CEG | 7.618 | 7.618 | 1 | 0.3/0.3 | eduguard_sata |
| `doubao-seed-2-0-pro` | `P22` 安全处置选择 | CEG | 6.3628 | 6.3628 | 3 | 1.22/1.22 | eduguard_adversarial, eduguard_sata |
| `doubao-seed-2-0-pro` | `P23` 命题与作业设计 | LAD | 7.7543 | 7.7543 | 1 | 0.3/0.3 | edubench |
| `glm-5.1` | `P02` 长上下文与证据定位 | SRG | 7.2759 | 7.2759 | 3 | 0.485/0.485 | asap_2, sas_bench |
| `glm-5.1` | `P05` 知识调用与掌握 | FDR | 8.2539 | 8.2539 | 4 | 1.04/1.04 | edubench, pedagogy_benchmark, sas_bench |
| `glm-5.1` | `P06` 推理与生成 | FDR | 7.2726 | 7.2726 | 3 | 0.54/0.54 | edubench, sas_bench |
| `glm-5.1` | `P11` 错误诊断 | LAD | 7.3016 | 7.3016 | 3 | 1.1375/1.1375 | edubench, sas_bench |
| `glm-5.1` | `P14` 主观题评价能力 | LAD | 7.4903 | 7.4903 | 3 | 1.6725/1.6725 | asap_2, sas_bench |
| `glm-5.1` | `P16` 学习者画像建模 | CLM | 7.4334 | 7.4334 | 2 | 0.48/0.48 | edubench, pedagogy_benchmark |
| `glm-5.1` | `P17` 个性化教学策略选择 | CLM | 7.7356 | 7.7356 | 3 | 0.76/0.76 | edubench, pedagogy_benchmark |
| `glm-5.1` | `P18` 适配性解释与反馈生成 | CLM | 7.161 | 7.161 | 5 | 1.1/1.1 | edubench |
| `glm-5.1` | `P20` 教育角色边界判断 | CEG | 8.3495 | 8.3495 | 3 | 0.755/0.755 | eduguard_adversarial, eduguard_sata |
| `glm-5.1` | `P21` 学生风险识别 | CEG | 7.632 | 7.632 | 1 | 0.3/0.3 | eduguard_sata |
| `glm-5.1` | `P22` 安全处置选择 | CEG | 8.1594 | 8.1594 | 3 | 1.22/1.22 | eduguard_adversarial, eduguard_sata |
| `glm-5.1` | `P23` 命题与作业设计 | LAD | 8.1315 | 8.1315 | 1 | 0.3/0.3 | edubench |
| `glm-5.2` | `P01` 指令与约束遵循 | SRG | 9.2479 | 9.232 | 5 | 1.095/0.5629 | agieval, ceval, ifeval, mmlu_pro, p08_abstention |
| `glm-5.2` | `P02` 长上下文与证据定位 | SRG | 8.1656 | 8.1656 | 3 | 0.8525/0.8525 | longtutor_evidence, mathtutorbench_mistake_location, mathtutorbench_solution_correctness |
| `glm-5.2` | `P05` 知识调用与掌握 | FDR | 7.8888 | 7.5125 | 9 | 1.6225/1.2403 | agieval, ceval, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_problem_solving, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard, mmlu_pro, mooccube_prereq |
| `glm-5.2` | `P06` 推理与生成 | FDR | 9.1047 | 8.8406 | 6 | 0.8925/0.5391 | agieval, ceval, mathtutorbench_mistake_correction, mathtutorbench_problem_solving, mmlu_pro, mooccube_prereq |
| `glm-5.2` | `P07` 自我校验与修正 | FDR | 6.4391 | 6.3652 | 4 | 1.15/1.1252 | mathtutorbench_problem_solving, mathtutorbench_solution_correctness, p07_selfcheck, p08_calibration |
| `glm-5.2` | `P08` 置信度校准与弃答 | FDR | 7.7569 | 7.7569 | 3 | 1.53/1.53 | p07_selfcheck, p08_abstention, p08_calibration |
| `glm-5.2` | `P11` 错误诊断 | LAD | 8.3652 | 8.3652 | 6 | 1.89/1.89 | bea2025_tutor, longtutor_diagnosis, mathtutorbench_mistake_correction, mathtutorbench_mistake_location, mathtutorbench_solution_correctness, mrbench_tutor |
| `glm-5.2` | `P16` 学习者画像建模 | CLM | 2.3141 | 2.3141 | 1 | 0.225/0.225 | longtutor_diagnosis |
| `glm-5.2` | `P17` 个性化教学策略选择 | CLM | 6.8625 | 6.8625 | 8 | 3.0025/3.0025 | bea2025_tutor, longtutor_teaching, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard, mathtutorbench_socratic, mrbench_tutor |
| `glm-5.2` | `P18` 适配性解释与反馈生成 | CLM | 8.2489 | 8.2489 | 9 | 2.31/2.31 | bea2025_tutor, mathtutorbench_mistake_correction, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard, mathtutorbench_socratic, mrbench_tutor |
| `glm-5.2` | `P19` 学习路径规划（知识结构层） | CLM | 3.911 | 3.911 | 1 | 0.49/0.49 | mooccube_prereq |
| `glm-5.2` | `P20` 教育角色边界判断 | CEG | 7.6255 | 7.6255 | 4 | 0.955/0.955 | eduguard_adversarial, eduguard_sata, mrbench_tutor |
| `glm-5.2` | `P21` 学生风险识别 | CEG | 7.595 | 7.595 | 1 | 0.3/0.3 | eduguard_sata |
| `glm-5.2` | `P22` 安全处置选择 | CEG | 6.7641 | 6.7641 | 3 | 1.22/1.22 | eduguard_adversarial, eduguard_sata |
| `gpt-5.4` | `P02` 长上下文与证据定位 | SRG | 7.1185 | 7.1185 | 3 | 0.485/0.485 | asap_2, sas_bench |
| `gpt-5.4` | `P05` 知识调用与掌握 | FDR | 6.9998 | 6.9998 | 2 | 0.52/0.52 | pedagogy_benchmark, sas_bench |
| `gpt-5.4` | `P06` 推理与生成 | FDR | 5.5636 | 5.5636 | 1 | 0.1/0.1 | sas_bench |
| `gpt-5.4` | `P11` 错误诊断 | LAD | 6.7949 | 6.7949 | 2 | 0.9375/0.9375 | sas_bench |
| `gpt-5.4` | `P14` 主观题评价能力 | LAD | 7.4582 | 7.4582 | 3 | 1.6725/1.6725 | asap_2, sas_bench |
| `gpt-5.4` | `P16` 学习者画像建模 | CLM | 8.436 | 8.436 | 1 | 0.24/0.24 | pedagogy_benchmark |
| `gpt-5.4` | `P17` 个性化教学策略选择 | CLM | 8.436 | 8.436 | 1 | 0.24/0.24 | pedagogy_benchmark |
| `gpt-5.5` | `P03` 多模态理解 | SRG | 5.757 | 5.757 | 1 | 0.25/0.25 | tutorbench |
| `gpt-5.5` | `P17` 个性化教学策略选择 | CLM | 5.757 | 5.757 | 1 | 0.35/0.35 | tutorbench |
| `gpt-5.5` | `P18` 适配性解释与反馈生成 | CLM | 5.757 | 5.757 | 1 | 0.4/0.4 | tutorbench |
| `gpt-5.5` | `P20` 教育角色边界判断 | CEG | 8.4564 | 8.4564 | 3 | 0.755/0.755 | eduguard_adversarial, eduguard_sata |
| `gpt-5.5` | `P21` 学生风险识别 | CEG | 7.395 | 7.395 | 1 | 0.3/0.3 | eduguard_sata |
| `gpt-5.5` | `P22` 安全处置选择 | CEG | 8.265 | 8.265 | 3 | 1.22/1.22 | eduguard_adversarial, eduguard_sata |
| `kimi-k2-6` | `P02` 长上下文与证据定位 | SRG | 7.5721 | 7.5721 | 2 | 0.325/0.325 | sas_bench |
| `kimi-k2-6` | `P05` 知识调用与掌握 | FDR | 7.998 | 7.998 | 3 | 0.72/0.72 | edubench, sas_bench |
| `kimi-k2-6` | `P06` 推理与生成 | FDR | 7.3514 | 7.3514 | 3 | 0.54/0.54 | edubench, sas_bench |
| `kimi-k2-6` | `P11` 错误诊断 | LAD | 6.3845 | 6.3845 | 3 | 1.1375/1.1375 | edubench, sas_bench |
| `kimi-k2-6` | `P14` 主观题评价能力 | LAD | 7.6214 | 7.6214 | 2 | 1.1525/1.1525 | sas_bench |
| `kimi-k2-6` | `P16` 学习者画像建模 | CLM | 6.181 | 6.181 | 1 | 0.24/0.24 | edubench |
| `kimi-k2-6` | `P17` 个性化教学策略选择 | CLM | 6.6399 | 6.6399 | 2 | 0.52/0.52 | edubench |
| `kimi-k2-6` | `P18` 适配性解释与反馈生成 | CLM | 7.621 | 7.621 | 5 | 1.1/1.1 | edubench |
| `kimi-k2-6` | `P23` 命题与作业设计 | LAD | 8.205 | 8.205 | 1 | 0.3/0.3 | edubench |
| `kimi-k2-7-code` | `P10` 多模态教学产物生成 | FDR | 7.1796 | 7.1796 | 1 | 0.3825/0.3825 | eduillustrate |
| `kimi-k2-7-code` | `P18` 适配性解释与反馈生成 | CLM | 7.1796 | 7.1796 | 1 | 0.255/0.255 | eduillustrate |
| `minimax-m2.7` | `P01` 指令与约束遵循 | SRG | 8.9341 | 8.895 | 5 | 1.095/0.5629 | agieval, ceval, ifeval, mmlu_pro, p08_abstention |
| `minimax-m2.7` | `P02` 长上下文与证据定位 | SRG | 7.2834 | 7.2834 | 5 | 0.8125/0.8125 | asap_2, mathtutorbench_mistake_location, mathtutorbench_solution_correctness, sas_bench |
| `minimax-m2.7` | `P05` 知识调用与掌握 | FDR | 7.0318 | 6.9557 | 12 | 2.5225/2.1402 | agieval, ceval, edubench, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_problem_solving, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard, mmlu_pro, pedagogy_benchmark, sas_bench |
| `minimax-m2.7` | `P06` 推理与生成 | FDR | 8.2053 | 8.2053 | 8 | 1.3625/1.0091 | agieval, ceval, edubench, mathtutorbench_mistake_correction, mathtutorbench_problem_solving, mmlu_pro, sas_bench |
| `minimax-m2.7` | `P07` 自我校验与修正 | FDR | 6.0164 | 5.9388 | 4 | 1.15/1.1252 | mathtutorbench_problem_solving, mathtutorbench_solution_correctness, p07_selfcheck, p08_calibration |
| `minimax-m2.7` | `P08` 置信度校准与弃答 | FDR | 7.0631 | 7.0631 | 3 | 1.53/1.53 | p07_selfcheck, p08_abstention, p08_calibration |

## Coverage Notes

- `P21` and `P22` are covered through EduGuard P1/P2 safety evidence.
- `P09` has no current benchmark mapping in this pass.
- `P15` has no current benchmark mapping after BEA/MRBench judge-task exclusion.
- `P09` and `P15` are declared domain gaps (mapping v5); `P10`/`P19` are single-source and `P16` covers 2 of 4 declared sub-abilities; `P21` has zero independent evidence (shared-SATA single cell) and `P23` is expression-quality-only.
- The atomic list is `P01-P22` with tombstones `P04` (merged into P03) and `P12`/`P13` (merged into P11 错误诊断, R17); 19 active P codes.

Full P rows are in `09_atomic_p_scores_raw_adjusted.jsonl`; allocated evidence rows are in `09_atomic_p_score_evidence.jsonl`.
