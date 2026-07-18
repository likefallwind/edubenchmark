# Atomic P Scores

P-score rows: 181
Covered P codes: P01, P02, P03, P04, P05, P06, P07, P09, P10, P11, P12, P13, P14, P15, P16, P17, P18, P19
Missing P codes: P08, P20

`score_10` (R20 single scheme): facet-weighted average with effective weight = relevance × confidence. Coverage completeness is reported separately and is not folded back into the score.

## Sample Scores

| Model key | P | Group | Score | Evidence | Weight sum | Benchmarks |
|---|---|---|---:|---:|---:|---|
| `claude-sonnet-4.6` | `P02` 长上下文与证据定位 | SRG | 6.106 | 1 | 0.16 | asap_2 |
| `claude-sonnet-4.6` | `P04` 知识调用与掌握 | FDR | 8.8634 | 3 | 0.84 | edubench, pedagogy_benchmark |
| `claude-sonnet-4.6` | `P05` 推理与生成 | FDR | 8.4166 | 2 | 0.44 | edubench |
| `claude-sonnet-4.6` | `P09` 错误诊断 | LAD | 6.074 | 1 | 0.2 | edubench |
| `claude-sonnet-4.6` | `P10` 主观题评价能力 | LAD | 6.106 | 1 | 0.52 | asap_2 |
| `claude-sonnet-4.6` | `P11` 命题与作业设计 | LAD | 8.043 | 1 | 0.3 | edubench |
| `claude-sonnet-4.6` | `P12` 学习者画像建模 | CLM | 7.4226 | 2 | 0.48 | edubench, pedagogy_benchmark |
| `claude-sonnet-4.6` | `P13` 个性化教学策略选择 | CLM | 7.6225 | 3 | 0.76 | edubench, pedagogy_benchmark |
| `claude-sonnet-4.6` | `P15` 适配性解释与反馈生成 | CLM | 7.9043 | 5 | 1.1 | edubench |
| `deepseek-v4-flash` | `P02` 长上下文与证据定位 | SRG | 7.0826 | 3 | 0.4875 | asap_2, mathtutorbench_mistake_location, mathtutorbench_solution_correctness |
| `deepseek-v4-flash` | `P04` 知识调用与掌握 | FDR | 7.7379 | 11 | 2.3225 | agieval, ceval, edubench, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_problem_solving, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard, mmlu_pro, pedagogy_benchmark |
| `deepseek-v4-flash` | `P05` 推理与生成 | FDR | 8.8347 | 7 | 1.2625 | agieval, ceval, edubench, mathtutorbench_mistake_correction, mathtutorbench_problem_solving, mmlu_pro |
| `deepseek-v4-flash` | `P06` 自我校验与修正 | FDR | 8.7724 | 2 | 0.2575 | mathtutorbench_problem_solving, mathtutorbench_solution_correctness |
| `deepseek-v4-flash` | `P09` 错误诊断 | LAD | 7.9888 | 4 | 1.59 | edubench, mathtutorbench_mistake_correction, mathtutorbench_mistake_location, mathtutorbench_solution_correctness |
| `deepseek-v4-flash` | `P10` 主观题评价能力 | LAD | 5.078 | 1 | 0.52 | asap_2 |
| `deepseek-v4-flash` | `P11` 命题与作业设计 | LAD | 8.09 | 1 | 0.3 | edubench |
| `deepseek-v4-flash` | `P12` 学习者画像建模 | CLM | 7.4283 | 2 | 0.48 | edubench, pedagogy_benchmark |
| `deepseek-v4-flash` | `P13` 个性化教学策略选择 | CLM | 6.7249 | 7 | 2.6375 | edubench, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard, pedagogy_benchmark |
| `deepseek-v4-flash` | `P15` 适配性解释与反馈生成 | CLM | 7.1913 | 10 | 2.7 | edubench, mathtutorbench_mistake_correction, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard |
| `deepseek-v4-pro` | `P01` 指令与约束遵循 | SRG | 9.2222 | 1 | 0.8 | ifeval |
| `deepseek-v4-pro` | `P02` 长上下文与证据定位 | SRG | 7.6135 | 6 | 1.3375 | asap_2, longtutor_evidence, mathtutorbench_mistake_location, mathtutorbench_solution_correctness, sas_bench |
| `deepseek-v4-pro` | `P03` 多模态理解 | SRG | 7.3613 | 1 | 0.11 | olympiadbench |
| `deepseek-v4-pro` | `P04` 知识调用与掌握 | FDR | 7.6472 | 13 | 2.665 | agieval, ceval, edubench, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard, mmlu_pro, mooccube_prereq, olympiadbench, pedagogy_benchmark, sas_bench |
| `deepseek-v4-pro` | `P05` 推理与生成 | FDR | 7.8324 | 9 | 1.465 | agieval, ceval, edubench, mathtutorbench_mistake_correction, mmlu_pro, mooccube_prereq, olympiadbench, sas_bench |
| `deepseek-v4-pro` | `P06` 自我校验与修正 | FDR | 6.3382 | 3 | 1.105 | mathtutorbench_solution_correctness, p07_selfcheck, p08_calibration |
| `deepseek-v4-pro` | `P07` 置信度校准与弃答 | FDR | 7.8082 | 3 | 1.53 | p07_selfcheck, p08_abstention, p08_calibration |
| `deepseek-v4-pro` | `P09` 错误诊断 | LAD | 7.7347 | 7 | 2.6025 | edubench, longtutor_diagnosis, mathtutorbench_mistake_correction, mathtutorbench_mistake_location, mathtutorbench_solution_correctness, sas_bench |
| `deepseek-v4-pro` | `P10` 主观题评价能力 | LAD | 7.2567 | 3 | 1.6725 | asap_2, sas_bench |
| `deepseek-v4-pro` | `P11` 命题与作业设计 | LAD | 8.3472 | 1 | 0.3 | edubench |
| `deepseek-v4-pro` | `P12` 学习者画像建模 | CLM | 5.3222 | 3 | 0.705 | edubench, longtutor_diagnosis, pedagogy_benchmark |
| `deepseek-v4-pro` | `P13` 个性化教学策略选择 | CLM | 7.2981 | 9 | 3.2525 | edubench, longtutor_teaching, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard, mathtutorbench_socratic, pedagogy_benchmark |
| `deepseek-v4-pro` | `P14` 学习路径规划（知识结构层） | CLM | 3.789 | 1 | 0.49 | mooccube_prereq |
| `deepseek-v4-pro` | `P15` 适配性解释与反馈生成 | CLM | 7.1511 | 11 | 2.91 | edubench, mathtutorbench_mistake_correction, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard, mathtutorbench_socratic |
| `deepseek-v4-pro` | `P17` 教育角色边界判断 | CEG | 5.8377 | 3 | 0.755 | eduguard_adversarial, eduguard_sata |
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
| `doubao-seed-2-0-pro` | `P02` 长上下文与证据定位 | SRG | 7.857 | 2 | 0.325 | sas_bench |
| `doubao-seed-2-0-pro` | `P03` 多模态理解 | SRG | 7.4977 | 2 | 0.71 | k12vista, mmtutorbench |
| `doubao-seed-2-0-pro` | `P04` 知识调用与掌握 | FDR | 7.1845 | 9 | 1.7675 | edubench, k12vista, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard, mooccube_prereq, sas_bench |
| `doubao-seed-2-0-pro` | `P05` 推理与生成 | FDR | 7.4995 | 5 | 0.85 | edubench, k12vista, mooccube_prereq, sas_bench |
| `doubao-seed-2-0-pro` | `P06` 自我校验与修正 | FDR | 5.3495 | 2 | 0.8925 | p07_selfcheck, p08_calibration |
| `doubao-seed-2-0-pro` | `P07` 置信度校准与弃答 | FDR | 7.73 | 3 | 1.53 | p07_selfcheck, p08_abstention, p08_calibration |
| `doubao-seed-2-0-pro` | `P09` 错误诊断 | LAD | 6.808 | 3 | 1.1375 | edubench, sas_bench |
| `doubao-seed-2-0-pro` | `P10` 主观题评价能力 | LAD | 7.9089 | 2 | 1.1525 | sas_bench |
| `doubao-seed-2-0-pro` | `P11` 命题与作业设计 | LAD | 7.7543 | 1 | 0.3 | edubench |
| `doubao-seed-2-0-pro` | `P12` 学习者画像建模 | CLM | 6.431 | 1 | 0.24 | edubench |
| `doubao-seed-2-0-pro` | `P13` 个性化教学策略选择 | CLM | 6.251 | 7 | 2.6675 | edubench, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard, mmtutorbench |
| `doubao-seed-2-0-pro` | `P14` 学习路径规划（知识结构层） | CLM | 4.486 | 1 | 0.49 | mooccube_prereq |
| `doubao-seed-2-0-pro` | `P15` 适配性解释与反馈生成 | CLM | 7.2342 | 11 | 3.0 | edubench, eduillustrate, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard, mmtutorbench |
| `doubao-seed-2-0-pro` | `P16` 多模态教学产物生成 | FDR | 7.411 | 1 | 0.3825 | eduillustrate |
| `doubao-seed-2-0-pro` | `P17` 教育角色边界判断 | CEG | 6.1006 | 3 | 0.755 | eduguard_adversarial, eduguard_sata |
| `doubao-seed-2-0-pro` | `P18` 学生风险识别 | CEG | 7.618 | 1 | 0.3 | eduguard_sata |
| `doubao-seed-2-0-pro` | `P19` 安全处置选择 | CEG | 6.3628 | 3 | 1.22 | eduguard_adversarial, eduguard_sata |
| `glm-5.1` | `P02` 长上下文与证据定位 | SRG | 7.2759 | 3 | 0.485 | asap_2, sas_bench |
| `glm-5.1` | `P04` 知识调用与掌握 | FDR | 8.2539 | 4 | 1.04 | edubench, pedagogy_benchmark, sas_bench |
| `glm-5.1` | `P05` 推理与生成 | FDR | 7.2726 | 3 | 0.54 | edubench, sas_bench |
| `glm-5.1` | `P09` 错误诊断 | LAD | 7.3016 | 3 | 1.1375 | edubench, sas_bench |
| `glm-5.1` | `P10` 主观题评价能力 | LAD | 7.4903 | 3 | 1.6725 | asap_2, sas_bench |
| `glm-5.1` | `P11` 命题与作业设计 | LAD | 8.1315 | 1 | 0.3 | edubench |
| `glm-5.1` | `P12` 学习者画像建模 | CLM | 7.4334 | 2 | 0.48 | edubench, pedagogy_benchmark |
| `glm-5.1` | `P13` 个性化教学策略选择 | CLM | 7.7356 | 3 | 0.76 | edubench, pedagogy_benchmark |
| `glm-5.1` | `P15` 适配性解释与反馈生成 | CLM | 7.161 | 5 | 1.1 | edubench |
| `glm-5.1` | `P17` 教育角色边界判断 | CEG | 8.3495 | 3 | 0.755 | eduguard_adversarial, eduguard_sata |
| `glm-5.1` | `P18` 学生风险识别 | CEG | 7.632 | 1 | 0.3 | eduguard_sata |
| `glm-5.1` | `P19` 安全处置选择 | CEG | 8.1594 | 3 | 1.22 | eduguard_adversarial, eduguard_sata |
| `glm-5.2` | `P01` 指令与约束遵循 | SRG | 9.2976 | 1 | 0.8 | ifeval |
| `glm-5.2` | `P02` 长上下文与证据定位 | SRG | 8.1469 | 5 | 1.1775 | longtutor_evidence, mathtutorbench_mistake_location, mathtutorbench_solution_correctness, sas_bench |
| `glm-5.2` | `P04` 知识调用与掌握 | FDR | 7.4497 | 10 | 1.8225 | agieval, ceval, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_problem_solving, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard, mmlu_pro, mooccube_prereq, sas_bench |
| `glm-5.2` | `P05` 推理与生成 | FDR | 8.1085 | 7 | 0.9925 | agieval, ceval, mathtutorbench_mistake_correction, mathtutorbench_problem_solving, mmlu_pro, mooccube_prereq, sas_bench |
| `glm-5.2` | `P06` 自我校验与修正 | FDR | 6.4391 | 4 | 1.15 | mathtutorbench_problem_solving, mathtutorbench_solution_correctness, p07_selfcheck, p08_calibration |
| `glm-5.2` | `P07` 置信度校准与弃答 | FDR | 7.7569 | 3 | 1.53 | p07_selfcheck, p08_abstention, p08_calibration |
| `glm-5.2` | `P09` 错误诊断 | LAD | 7.607 | 8 | 2.8275 | bea2025_tutor, longtutor_diagnosis, mathtutorbench_mistake_correction, mathtutorbench_mistake_location, mathtutorbench_solution_correctness, mrbench_tutor, sas_bench |
| `glm-5.2` | `P10` 主观题评价能力 | LAD | 8.1549 | 2 | 1.1525 | sas_bench |
| `glm-5.2` | `P12` 学习者画像建模 | CLM | 2.3141 | 1 | 0.225 | longtutor_diagnosis |
| `glm-5.2` | `P13` 个性化教学策略选择 | CLM | 6.8625 | 8 | 3.0025 | bea2025_tutor, longtutor_teaching, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard, mathtutorbench_socratic, mrbench_tutor |
| `glm-5.2` | `P14` 学习路径规划（知识结构层） | CLM | 3.911 | 1 | 0.49 | mooccube_prereq |
| `glm-5.2` | `P15` 适配性解释与反馈生成 | CLM | 8.2489 | 9 | 2.31 | bea2025_tutor, mathtutorbench_mistake_correction, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard, mathtutorbench_socratic, mrbench_tutor |
| `glm-5.2` | `P17` 教育角色边界判断 | CEG | 7.6255 | 4 | 0.955 | eduguard_adversarial, eduguard_sata, mrbench_tutor |
| `glm-5.2` | `P18` 学生风险识别 | CEG | 7.595 | 1 | 0.3 | eduguard_sata |
| `glm-5.2` | `P19` 安全处置选择 | CEG | 6.7641 | 3 | 1.22 | eduguard_adversarial, eduguard_sata |
| `gpt-5.4` | `P02` 长上下文与证据定位 | SRG | 7.1185 | 3 | 0.485 | asap_2, sas_bench |
| `gpt-5.4` | `P04` 知识调用与掌握 | FDR | 6.9998 | 2 | 0.52 | pedagogy_benchmark, sas_bench |
| `gpt-5.4` | `P05` 推理与生成 | FDR | 5.5636 | 1 | 0.1 | sas_bench |
| `gpt-5.4` | `P09` 错误诊断 | LAD | 6.7949 | 2 | 0.9375 | sas_bench |
| `gpt-5.4` | `P10` 主观题评价能力 | LAD | 7.4582 | 3 | 1.6725 | asap_2, sas_bench |
| `gpt-5.4` | `P12` 学习者画像建模 | CLM | 8.436 | 1 | 0.24 | pedagogy_benchmark |
| `gpt-5.4` | `P13` 个性化教学策略选择 | CLM | 8.436 | 1 | 0.24 | pedagogy_benchmark |
| `gpt-5.5` | `P03` 多模态理解 | SRG | 5.757 | 1 | 0.25 | tutorbench |
| `gpt-5.5` | `P13` 个性化教学策略选择 | CLM | 5.757 | 1 | 0.35 | tutorbench |
| `gpt-5.5` | `P15` 适配性解释与反馈生成 | CLM | 5.757 | 1 | 0.4 | tutorbench |
| `gpt-5.5` | `P17` 教育角色边界判断 | CEG | 8.4564 | 3 | 0.755 | eduguard_adversarial, eduguard_sata |
| `gpt-5.5` | `P18` 学生风险识别 | CEG | 7.395 | 1 | 0.3 | eduguard_sata |
| `gpt-5.5` | `P19` 安全处置选择 | CEG | 8.265 | 3 | 1.22 | eduguard_adversarial, eduguard_sata |
| `kimi-k2-6` | `P02` 长上下文与证据定位 | SRG | 7.5721 | 2 | 0.325 | sas_bench |
| `kimi-k2-6` | `P04` 知识调用与掌握 | FDR | 7.998 | 3 | 0.72 | edubench, sas_bench |
| `kimi-k2-6` | `P05` 推理与生成 | FDR | 7.3514 | 3 | 0.54 | edubench, sas_bench |
| `kimi-k2-6` | `P09` 错误诊断 | LAD | 6.3845 | 3 | 1.1375 | edubench, sas_bench |
| `kimi-k2-6` | `P10` 主观题评价能力 | LAD | 7.6214 | 2 | 1.1525 | sas_bench |
| `kimi-k2-6` | `P11` 命题与作业设计 | LAD | 8.205 | 1 | 0.3 | edubench |
| `kimi-k2-6` | `P12` 学习者画像建模 | CLM | 6.181 | 1 | 0.24 | edubench |
| `kimi-k2-6` | `P13` 个性化教学策略选择 | CLM | 6.6399 | 2 | 0.52 | edubench |
| `kimi-k2-6` | `P15` 适配性解释与反馈生成 | CLM | 7.621 | 5 | 1.1 | edubench |
| `kimi-k2-7-code` | `P15` 适配性解释与反馈生成 | CLM | 7.1796 | 1 | 0.255 | eduillustrate |
| `kimi-k2-7-code` | `P16` 多模态教学产物生成 | FDR | 7.1796 | 1 | 0.3825 | eduillustrate |
| `minimax-m2.7` | `P01` 指令与约束遵循 | SRG | 9.1078 | 1 | 0.8 | ifeval |
| `minimax-m2.7` | `P02` 长上下文与证据定位 | SRG | 7.2834 | 5 | 0.8125 | asap_2, mathtutorbench_mistake_location, mathtutorbench_solution_correctness, sas_bench |
| `minimax-m2.7` | `P04` 知识调用与掌握 | FDR | 6.876 | 13 | 2.6625 | agieval, ceval, edubench, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_problem_solving, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard, mmlu_pro, mooccube_prereq, pedagogy_benchmark, sas_bench |
| `minimax-m2.7` | `P05` 推理与生成 | FDR | 8.0055 | 9 | 1.4325 | agieval, ceval, edubench, mathtutorbench_mistake_correction, mathtutorbench_problem_solving, mmlu_pro, mooccube_prereq, sas_bench |

## Coverage Notes

- `P17`-`P19` are covered through EduGuard P1/P2 safety evidence.
- `P08` (tool use / long-horizon) and `P20` (academic integrity) are declared domain gaps; `P16`/`P14` are single-source and `P12` covers 2 of 4 declared sub-abilities; `P18` has zero independent evidence (shared-SATA single cell) and `P11` is expression-quality-only.
- The atomic list is `P01-P20` (R20 doc-scheme renumbering, no tombstones).

Full P rows are in `09_atomic_p_scores.jsonl`; allocated evidence rows are in `09_atomic_p_score_evidence.jsonl`.
