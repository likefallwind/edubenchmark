# Atomic P Scores: Raw And Adjusted

P-score rows: 164
Covered P codes: P01, P02, P03, P05, P06, P07, P08, P10, P11, P12, P13, P14, P16, P17, P18, P20, P21, P22
Missing P codes: P04, P09, P15, P19

`raw_score_10` uses default benchmark weights. `tier_adjusted_score_10` reduces foundation-gate evidence. Coverage completeness is reported separately and is not folded back into the score.

## Sample Scores

| Model key | P | Group | Raw | Tier adjusted | Evidence | Weight raw/adj | Benchmarks |
|---|---|---|---:|---:|---:|---:|---|
| `claude-sonnet-4.6` | `P02` 长上下文与证据定位 | SRG | 6.106 | 6.106 | 1 | 0.16/0.16 | asap_2 |
| `claude-sonnet-4.6` | `P05` 知识调用与掌握 | FDR | 8.5412 | 8.5412 | 6 | 1.3275/1.3275 | asap_2, edubench, pedagogy_benchmark |
| `claude-sonnet-4.6` | `P06` 推理与生成 | FDR | 8.9199 | 8.9199 | 2 | 0.45/0.45 | edubench |
| `claude-sonnet-4.6` | `P14` Rubric 映射评分 | LAD | 6.106 | 6.106 | 1 | 0.52/0.52 | asap_2 |
| `claude-sonnet-4.6` | `P16` 学习者画像建模 | CLM | 8.7945 | 8.7945 | 2 | 0.495/0.495 | edubench, pedagogy_benchmark |
| `claude-sonnet-4.6` | `P17` 个性化教学策略选择 | CLM | 8.8238 | 8.8238 | 4 | 1.1825/1.1825 | edubench, pedagogy_benchmark |
| `claude-sonnet-4.6` | `P18` 适配性解释与反馈生成 | CLM | 8.9305 | 8.9305 | 5 | 1.415/1.415 | edubench |
| `deepseek-v4-flash` | `P01` 指令与约束遵循 | SRG | 8.9528 | 8.9528 | 3 | 0.1675/0.0754 | agieval, ceval, mmlu_pro |
| `deepseek-v4-flash` | `P02` 长上下文与证据定位 | SRG | 7.0826 | 7.0826 | 3 | 0.4875/0.4875 | asap_2, mathtutorbench_mistake_location, mathtutorbench_solution_correctness |
| `deepseek-v4-flash` | `P05` 知识调用与掌握 | FDR | 7.7434 | 7.5339 | 14 | 2.81/2.4278 | agieval, asap_2, ceval, edubench, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_problem_solving, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard, mmlu_pro, pedagogy_benchmark |
| `deepseek-v4-flash` | `P06` 推理与生成 | FDR | 9.17 | 9.1365 | 7 | 1.2725/0.9191 | agieval, ceval, edubench, mathtutorbench_mistake_correction, mathtutorbench_problem_solving, mmlu_pro |
| `deepseek-v4-flash` | `P07` 自我校验与修正 | FDR | 8.7724 | 8.6692 | 2 | 0.2575/0.2328 | mathtutorbench_problem_solving, mathtutorbench_solution_correctness |
| `deepseek-v4-flash` | `P11` 作答正误判定 | LAD | 8.4314 | 8.4314 | 2 | 0.61/0.61 | mathtutorbench_mistake_location, mathtutorbench_solution_correctness |
| `deepseek-v4-flash` | `P12` 错误位置定位 | LAD | 7.74 | 7.74 | 1 | 0.7/0.7 | mathtutorbench_mistake_location |
| `deepseek-v4-flash` | `P13` 错因归因 | LAD | 9.1717 | 9.1717 | 1 | 0.405/0.405 | mathtutorbench_mistake_correction |
| `deepseek-v4-flash` | `P14` Rubric 映射评分 | LAD | 5.078 | 5.078 | 1 | 0.52/0.52 | asap_2 |
| `deepseek-v4-flash` | `P16` 学习者画像建模 | CLM | 8.8915 | 8.8915 | 2 | 0.495/0.495 | edubench, pedagogy_benchmark |
| `deepseek-v4-flash` | `P17` 个性化教学策略选择 | CLM | 6.0948 | 6.0948 | 8 | 3.06/3.06 | edubench, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard, pedagogy_benchmark |
| `deepseek-v4-flash` | `P18` 适配性解释与反馈生成 | CLM | 7.018 | 7.018 | 10 | 3.015/3.015 | edubench, mathtutorbench_mistake_correction, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard |
| `deepseek-v4-pro` | `P01` 指令与约束遵循 | SRG | 9.0753 | 9.0753 | 3 | 0.1675/0.0754 | agieval, ceval, mmlu_pro |
| `deepseek-v4-pro` | `P02` 长上下文与证据定位 | SRG | 7.4183 | 7.4183 | 5 | 0.8125/0.8125 | asap_2, mathtutorbench_mistake_location, mathtutorbench_solution_correctness, sas_bench |
| `deepseek-v4-pro` | `P03` 常规多模态感知 | SRG | 7.3613 | 7.3613 | 1 | 0.11/0.0495 | olympiadbench |
| `deepseek-v4-pro` | `P05` 知识调用与掌握 | FDR | 7.7893 | 7.6603 | 16 | 3.1475/2.7639 | agieval, asap_2, ceval, edubench, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard, mmlu_pro, olympiadbench, pedagogy_benchmark, sas_bench |
| `deepseek-v4-pro` | `P06` 推理与生成 | FDR | 8.0883 | 8.0194 | 8 | 1.405/1.0338 | agieval, ceval, edubench, mathtutorbench_mistake_correction, mmlu_pro, olympiadbench, sas_bench |
| `deepseek-v4-pro` | `P07` 自我校验与修正 | FDR | 8.621 | 8.621 | 1 | 0.2125/0.2125 | mathtutorbench_solution_correctness |
| `deepseek-v4-pro` | `P11` 作答正误判定 | LAD | 8.4618 | 8.4618 | 2 | 0.61/0.61 | mathtutorbench_mistake_location, mathtutorbench_solution_correctness |
| `deepseek-v4-pro` | `P12` 错误位置定位 | LAD | 7.6533 | 7.6533 | 2 | 0.9375/0.9375 | mathtutorbench_mistake_location, sas_bench |
| `deepseek-v4-pro` | `P13` 错因归因 | LAD | 7.2805 | 7.2805 | 2 | 1.105/1.105 | mathtutorbench_mistake_correction, sas_bench |
| `deepseek-v4-pro` | `P14` Rubric 映射评分 | LAD | 7.1042 | 7.1042 | 3 | 1.6725/1.6725 | asap_2, sas_bench |
| `deepseek-v4-pro` | `P16` 学习者画像建模 | CLM | 8.5634 | 8.5634 | 2 | 0.495/0.495 | edubench, pedagogy_benchmark |
| `deepseek-v4-pro` | `P17` 个性化教学策略选择 | CLM | 6.8006 | 6.8006 | 9 | 3.45/3.45 | edubench, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard, mathtutorbench_socratic, pedagogy_benchmark |
| `deepseek-v4-pro` | `P18` 适配性解释与反馈生成 | CLM | 7.2606 | 7.2606 | 11 | 3.225/3.225 | edubench, mathtutorbench_mistake_correction, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard, mathtutorbench_socratic |
| `deepseek-v4-pro` | `P20` 教育角色边界判断 | CEG | 5.8337 | 5.8337 | 2 | 0.65/0.65 | eduguard_adversarial, eduguard_sata |
| `deepseek-v4-pro` | `P21` 学生风险识别 | CEG | 5.8606 | 5.8606 | 2 | 0.55/0.55 | eduguard_adversarial, eduguard_sata |
| `deepseek-v4-pro` | `P22` 安全处置选择 | CEG | 5.4447 | 5.4447 | 2 | 0.8/0.8 | eduguard_adversarial, eduguard_sata |
| `doubao-seed-2-0-lite` | `P03` 常规多模态感知 | SRG | 6.777 | 6.777 | 1 | 0.2125/0.2125 | eduillustrate |
| `doubao-seed-2-0-lite` | `P05` 知识调用与掌握 | FDR | 7.4758 | 7.4758 | 8 | 1.675/1.675 | edubench, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard |
| `doubao-seed-2-0-lite` | `P06` 推理与生成 | FDR | 8.7183 | 8.7183 | 2 | 0.45/0.45 | edubench |
| `doubao-seed-2-0-lite` | `P10` 多模态教学产物生成 | FDR | 6.777 | 6.777 | 1 | 0.3825/0.3825 | eduillustrate |
| `doubao-seed-2-0-lite` | `P16` 学习者画像建模 | CLM | 9.128 | 9.128 | 1 | 0.255/0.255 | edubench |
| `doubao-seed-2-0-lite` | `P17` 个性化教学策略选择 | CLM | 6.3731 | 6.3731 | 7 | 2.82/2.82 | edubench, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard |
| `doubao-seed-2-0-lite` | `P18` 适配性解释与反馈生成 | CLM | 7.0094 | 7.0094 | 10 | 2.955/2.955 | edubench, eduillustrate, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard |
| `doubao-seed-2-0-lite` | `P20` 教育角色边界判断 | CEG | 6.1868 | 6.1868 | 2 | 0.65/0.65 | eduguard_adversarial, eduguard_sata |
| `doubao-seed-2-0-lite` | `P21` 学生风险识别 | CEG | 6.2036 | 6.2036 | 2 | 0.55/0.55 | eduguard_adversarial, eduguard_sata |
| `doubao-seed-2-0-lite` | `P22` 安全处置选择 | CEG | 5.9432 | 5.9432 | 2 | 0.8/0.8 | eduguard_adversarial, eduguard_sata |
| `doubao-seed-2-0-pro` | `P05` 知识调用与掌握 | FDR | 8.0368 | 8.0368 | 8 | 1.675/1.675 | edubench, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard |
| `doubao-seed-2-0-pro` | `P06` 推理与生成 | FDR | 9.0033 | 9.0033 | 2 | 0.45/0.45 | edubench |
| `doubao-seed-2-0-pro` | `P16` 学习者画像建模 | CLM | 9.437 | 9.437 | 1 | 0.255/0.255 | edubench |
| `doubao-seed-2-0-pro` | `P17` 个性化教学策略选择 | CLM | 7.1597 | 7.1597 | 7 | 2.82/2.82 | edubench, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard |
| `doubao-seed-2-0-pro` | `P18` 适配性解释与反馈生成 | CLM | 7.6884 | 7.6884 | 9 | 2.7/2.7 | edubench, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard |
| `doubao-seed-2-0-pro` | `P20` 教育角色边界判断 | CEG | 5.9366 | 5.9366 | 2 | 0.65/0.65 | eduguard_adversarial, eduguard_sata |
| `doubao-seed-2-0-pro` | `P21` 学生风险识别 | CEG | 5.9621 | 5.9621 | 2 | 0.55/0.55 | eduguard_adversarial, eduguard_sata |
| `doubao-seed-2-0-pro` | `P22` 安全处置选择 | CEG | 5.5688 | 5.5688 | 2 | 0.8/0.8 | eduguard_adversarial, eduguard_sata |
| `glm-5.1` | `P02` 长上下文与证据定位 | SRG | 7.2757 | 7.2757 | 3 | 0.485/0.485 | asap_2, sas_bench |
| `glm-5.1` | `P05` 知识调用与掌握 | FDR | 7.5375 | 7.5375 | 8 | 1.6625/1.6625 | asap_2, edubench, pedagogy_benchmark, sas_bench |
| `glm-5.1` | `P06` 推理与生成 | FDR | 7.1279 | 7.1279 | 3 | 0.55/0.55 | edubench, sas_bench |
| `glm-5.1` | `P12` 错误位置定位 | LAD | 7.814 | 7.814 | 1 | 0.2375/0.2375 | sas_bench |
| `glm-5.1` | `P13` 错因归因 | LAD | 6.26 | 6.26 | 1 | 0.7/0.7 | sas_bench |
| `glm-5.1` | `P14` Rubric 映射评分 | LAD | 7.3687 | 7.3687 | 3 | 1.6725/1.6725 | asap_2, sas_bench |
| `glm-5.1` | `P16` 学习者画像建模 | CLM | 8.4177 | 8.4177 | 2 | 0.495/0.495 | edubench, pedagogy_benchmark |
| `glm-5.1` | `P17` 个性化教学策略选择 | CLM | 8.1634 | 8.1634 | 4 | 1.1825/1.1825 | edubench, pedagogy_benchmark |
| `glm-5.1` | `P18` 适配性解释与反馈生成 | CLM | 7.6829 | 7.6829 | 5 | 1.415/1.415 | edubench |
| `glm-5.1` | `P20` 教育角色边界判断 | CEG | 8.4978 | 8.4978 | 2 | 0.65/0.65 | eduguard_adversarial, eduguard_sata |
| `glm-5.1` | `P21` 学生风险识别 | CEG | 8.4847 | 8.4847 | 2 | 0.55/0.55 | eduguard_adversarial, eduguard_sata |
| `glm-5.1` | `P22` 安全处置选择 | CEG | 8.6872 | 8.6872 | 2 | 0.8/0.8 | eduguard_adversarial, eduguard_sata |
| `glm-5.2` | `P01` 指令与约束遵循 | SRG | 9.1079 | 9.1079 | 3 | 0.1675/0.0754 | agieval, ceval, mmlu_pro |
| `glm-5.2` | `P02` 长上下文与证据定位 | SRG | 8.3212 | 8.3212 | 2 | 0.3275/0.3275 | mathtutorbench_mistake_location, mathtutorbench_solution_correctness |
| `glm-5.2` | `P05` 知识调用与掌握 | FDR | 8.3245 | 8.0106 | 8 | 1.4825/1.1002 | agieval, ceval, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_problem_solving, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard, mmlu_pro |
| `glm-5.2` | `P06` 推理与生成 | FDR | 9.3746 | 9.3738 | 5 | 0.8225/0.4691 | agieval, ceval, mathtutorbench_mistake_correction, mathtutorbench_problem_solving, mmlu_pro |
| `glm-5.2` | `P07` 自我校验与修正 | FDR | 9.1007 | 9.026 | 2 | 0.2575/0.2328 | mathtutorbench_problem_solving, mathtutorbench_solution_correctness |
| `glm-5.2` | `P11` 作答正误判定 | LAD | 8.7827 | 8.7827 | 2 | 0.61/0.61 | mathtutorbench_mistake_location, mathtutorbench_solution_correctness |
| `glm-5.2` | `P12` 错误位置定位 | LAD | 7.919 | 7.919 | 1 | 0.7/0.7 | mathtutorbench_mistake_location |
| `glm-5.2` | `P13` 错因归因 | LAD | 8.0 | 8.0 | 2 | 0.63/0.63 | bea2025_tutor, mathtutorbench_mistake_correction |
| `glm-5.2` | `P17` 个性化教学策略选择 | CLM | 6.0895 | 6.0895 | 7 | 2.7775/2.7775 | bea2025_tutor, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard, mathtutorbench_socratic, mrbench_tutor |
| `glm-5.2` | `P18` 适配性解释与反馈生成 | CLM | 6.3214 | 6.3214 | 8 | 2.575/2.575 | bea2025_tutor, mathtutorbench_mistake_correction, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard, mathtutorbench_socratic, mrbench_tutor |
| `glm-5.2` | `P20` 教育角色边界判断 | CEG | 6.5464 | 6.5464 | 3 | 0.85/0.85 | eduguard_adversarial, eduguard_sata, mrbench_tutor |
| `glm-5.2` | `P21` 学生风险识别 | CEG | 7.3945 | 7.3945 | 2 | 0.55/0.55 | eduguard_adversarial, eduguard_sata |
| `glm-5.2` | `P22` 安全处置选择 | CEG | 7.3469 | 7.3469 | 2 | 0.8/0.8 | eduguard_adversarial, eduguard_sata |
| `gpt-5.4` | `P02` 长上下文与证据定位 | SRG | 7.1185 | 7.1185 | 3 | 0.485/0.485 | asap_2, sas_bench |
| `gpt-5.4` | `P05` 知识调用与掌握 | FDR | 7.1624 | 7.1624 | 4 | 0.775/0.775 | asap_2, pedagogy_benchmark, sas_bench |
| `gpt-5.4` | `P06` 推理与生成 | FDR | 5.564 | 5.564 | 1 | 0.1/0.1 | sas_bench |
| `gpt-5.4` | `P12` 错误位置定位 | LAD | 8.026 | 8.026 | 1 | 0.2375/0.2375 | sas_bench |
| `gpt-5.4` | `P13` 错因归因 | LAD | 5.564 | 5.564 | 1 | 0.7/0.7 | sas_bench |
| `gpt-5.4` | `P14` Rubric 映射评分 | LAD | 7.2452 | 7.2452 | 3 | 1.6725/1.6725 | asap_2, sas_bench |
| `gpt-5.4` | `P16` 学习者画像建模 | CLM | 8.436 | 8.436 | 1 | 0.24/0.24 | pedagogy_benchmark |
| `gpt-5.4` | `P17` 个性化教学策略选择 | CLM | 8.436 | 8.436 | 1 | 0.24/0.24 | pedagogy_benchmark |
| `gpt-5.5` | `P03` 常规多模态感知 | SRG | 5.757 | 5.757 | 1 | 0.25/0.25 | tutorbench |
| `gpt-5.5` | `P17` 个性化教学策略选择 | CLM | 5.757 | 5.757 | 1 | 0.35/0.35 | tutorbench |
| `gpt-5.5` | `P18` 适配性解释与反馈生成 | CLM | 5.757 | 5.757 | 1 | 0.4/0.4 | tutorbench |
| `gpt-5.5` | `P20` 教育角色边界判断 | CEG | 8.5798 | 8.5798 | 2 | 0.65/0.65 | eduguard_adversarial, eduguard_sata |
| `gpt-5.5` | `P21` 学生风险识别 | CEG | 8.5618 | 8.5618 | 2 | 0.55/0.55 | eduguard_adversarial, eduguard_sata |
| `gpt-5.5` | `P22` 安全处置选择 | CEG | 8.8389 | 8.8389 | 2 | 0.8/0.8 | eduguard_adversarial, eduguard_sata |
| `kimi-k2-6` | `P02` 长上下文与证据定位 | SRG | 7.5722 | 7.5722 | 2 | 0.325/0.325 | sas_bench |
| `kimi-k2-6` | `P05` 知识调用与掌握 | FDR | 7.9447 | 7.9447 | 6 | 1.2225/1.2225 | edubench, sas_bench |
| `kimi-k2-6` | `P06` 推理与生成 | FDR | 8.0255 | 8.0255 | 3 | 0.55/0.55 | edubench, sas_bench |
| `kimi-k2-6` | `P12` 错误位置定位 | LAD | 7.33 | 7.33 | 1 | 0.2375/0.2375 | sas_bench |
| `kimi-k2-6` | `P13` 错因归因 | LAD | 5.22 | 5.22 | 1 | 0.7/0.7 | sas_bench |
| `kimi-k2-6` | `P14` Rubric 映射评分 | LAD | 7.6487 | 7.6487 | 2 | 1.1525/1.1525 | sas_bench |
| `kimi-k2-6` | `P16` 学习者画像建模 | CLM | 8.899 | 8.899 | 1 | 0.255/0.255 | edubench |
| `kimi-k2-6` | `P17` 个性化教学策略选择 | CLM | 8.5765 | 8.5765 | 3 | 0.9425/0.9425 | edubench |
| `kimi-k2-6` | `P18` 适配性解释与反馈生成 | CLM | 8.6197 | 8.6197 | 5 | 1.415/1.415 | edubench |
| `kimi-k2-7-code` | `P03` 常规多模态感知 | SRG | 7.1796 | 7.1796 | 1 | 0.2125/0.2125 | eduillustrate |
| `kimi-k2-7-code` | `P10` 多模态教学产物生成 | FDR | 7.1796 | 7.1796 | 1 | 0.3825/0.3825 | eduillustrate |
| `kimi-k2-7-code` | `P18` 适配性解释与反馈生成 | CLM | 7.1796 | 7.1796 | 1 | 0.255/0.255 | eduillustrate |
| `minimax-m2.7` | `P01` 指令与约束遵循 | SRG | 8.3438 | 8.3438 | 3 | 0.1675/0.0754 | agieval, ceval, mmlu_pro |
| `minimax-m2.7` | `P02` 长上下文与证据定位 | SRG | 7.2835 | 7.2835 | 5 | 0.8125/0.8125 | asap_2, mathtutorbench_mistake_location, mathtutorbench_solution_correctness, sas_bench |
| `minimax-m2.7` | `P05` 知识调用与掌握 | FDR | 7.184 | 6.984 | 16 | 3.145/2.7628 | agieval, asap_2, ceval, edubench, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_problem_solving, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard, mmlu_pro, pedagogy_benchmark, sas_bench |
| `minimax-m2.7` | `P06` 推理与生成 | FDR | 8.3396 | 8.1707 | 8 | 1.3725/1.0191 | agieval, ceval, edubench, mathtutorbench_mistake_correction, mathtutorbench_problem_solving, mmlu_pro, sas_bench |
| `minimax-m2.7` | `P07` 自我校验与修正 | FDR | 8.7536 | 8.6694 | 2 | 0.2575/0.2328 | mathtutorbench_problem_solving, mathtutorbench_solution_correctness |
| `minimax-m2.7` | `P11` 作答正误判定 | LAD | 8.4367 | 8.4367 | 2 | 0.61/0.61 | mathtutorbench_mistake_location, mathtutorbench_solution_correctness |
| `minimax-m2.7` | `P12` 错误位置定位 | LAD | 7.5663 | 7.5663 | 2 | 0.9375/0.9375 | mathtutorbench_mistake_location, sas_bench |
| `minimax-m2.7` | `P13` 错因归因 | LAD | 6.2493 | 6.2493 | 3 | 1.33/1.33 | bea2025_tutor, mathtutorbench_mistake_correction, sas_bench |
| `minimax-m2.7` | `P14` Rubric 映射评分 | LAD | 6.8817 | 6.8817 | 3 | 1.6725/1.6725 | asap_2, sas_bench |
| `minimax-m2.7` | `P16` 学习者画像建模 | CLM | 8.5355 | 8.5355 | 2 | 0.495/0.495 | edubench, pedagogy_benchmark |
| `minimax-m2.7` | `P17` 个性化教学策略选择 | CLM | 5.2212 | 5.2212 | 11 | 3.96/3.96 | bea2025_tutor, edubench, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard, mathtutorbench_socratic, mrbench_tutor, pedagogy_benchmark |
| `minimax-m2.7` | `P18` 适配性解释与反馈生成 | CLM | 5.8764 | 5.8764 | 13 | 3.99/3.99 | bea2025_tutor, edubench, mathtutorbench_mistake_correction, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard, mathtutorbench_socratic, mrbench_tutor |
| `minimax-m2.7` | `P20` 教育角色边界判断 | CEG | 5.5216 | 5.5216 | 2 | 0.55/0.55 | eduguard_sata, mrbench_tutor |
| `minimax-m2.7` | `P21` 学生风险识别 | CEG | 6.934 | 6.934 | 1 | 0.3/0.3 | eduguard_sata |
| `minimax-m2.7` | `P22` 安全处置选择 | CEG | 6.934 | 6.934 | 1 | 0.35/0.35 | eduguard_sata |
| `minimax-m3` | `P01` 指令与约束遵循 | SRG | 8.7237 | 8.7232 | 5 | 1.095/0.5629 | agieval, ceval, ifeval, mmlu_pro, p08_abstention |

## Coverage Notes

- `P21` and `P22` are covered through EduGuard P1/P2 safety evidence.
- `P09` has no current benchmark mapping in this pass.
- `P15` has no current benchmark mapping after BEA/MRBench judge-task exclusion.
- `P04`, `P08`, and `P19` remain sparse/absent unless proxy mappings are approved.
- The v3 atomic list is `P01-P22`; no `P0` code exists in the current spec.

Full P rows are in `09_atomic_p_scores_raw_adjusted.jsonl`; allocated evidence rows are in `09_atomic_p_score_evidence.jsonl`.
