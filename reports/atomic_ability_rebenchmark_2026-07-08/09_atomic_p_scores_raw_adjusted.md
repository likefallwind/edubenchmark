# Atomic P Scores: Raw And Adjusted

P-score rows: 163
Covered P codes: P01, P02, P03, P05, P06, P07, P10, P11, P12, P13, P14, P16, P17, P18, P20, P21, P22
Missing P codes: P04, P08, P09, P15, P19

`raw_score_10` uses default benchmark weights. `tier_adjusted_score_10` reduces foundation-gate evidence. `coverage_adjusted_score_10` additionally shrinks sparse evidence toward 5.0.

## Sample Scores

| Model key | P | Group | Raw | Tier adjusted | Coverage adjusted | Evidence | Weight raw/adj | Benchmarks |
|---|---|---|---:|---:|---:|---:|---:|---|
| `claude-sonnet-4.6` | `P02` 长上下文与证据定位 | SRG | 6.106 | 6.106 | 5.1526 | 1 | 0.16/0.16 | asap_2 |
| `claude-sonnet-4.6` | `P05` 知识调用与掌握 | FDR | 8.5412 | 8.5412 | 7.0198 | 6 | 1.3275/1.3275 | asap_2, edubench, pedagogy_benchmark |
| `claude-sonnet-4.6` | `P06` 推理与生成 | FDR | 8.9199 | 8.9199 | 6.2165 | 2 | 0.45/0.45 | edubench |
| `claude-sonnet-4.6` | `P14` Rubric 映射评分 | LAD | 6.106 | 6.106 | 5.3784 | 1 | 0.52/0.52 | asap_2 |
| `claude-sonnet-4.6` | `P16` 学习者画像建模 | CLM | 8.7945 | 8.7945 | 6.2564 | 2 | 0.495/0.495 | edubench, pedagogy_benchmark |
| `claude-sonnet-4.6` | `P17` 个性化教学策略选择 | CLM | 8.8238 | 8.8238 | 7.0718 | 4 | 1.1825/1.1825 | edubench, pedagogy_benchmark |
| `claude-sonnet-4.6` | `P18` 适配性解释与反馈生成 | CLM | 8.9305 | 8.9305 | 7.303 | 5 | 1.415/1.415 | edubench |
| `deepseek-v4-flash` | `P01` 指令与约束遵循 | SRG | 8.9528 | 8.9528 | 5.2771 | 3 | 0.1675/0.0754 | agieval, ceval, mmlu_pro |
| `deepseek-v4-flash` | `P02` 长上下文与证据定位 | SRG | 7.0826 | 7.0826 | 5.6825 | 3 | 0.4875/0.4875 | asap_2, mathtutorbench_mistake_location, mathtutorbench_solution_correctness |
| `deepseek-v4-flash` | `P05` 知识调用与掌握 | FDR | 7.7434 | 7.5339 | 6.7947 | 14 | 2.81/2.4278 | agieval, asap_2, ceval, edubench, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_problem_solving, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard, mmlu_pro, pedagogy_benchmark |
| `deepseek-v4-flash` | `P06` 推理与生成 | FDR | 9.17 | 9.1365 | 6.9811 | 7 | 1.2725/0.9191 | agieval, ceval, edubench, mathtutorbench_mistake_correction, mathtutorbench_problem_solving, mmlu_pro |
| `deepseek-v4-flash` | `P07` 自我校验与修正 | FDR | 8.7724 | 8.6692 | 5.6928 | 2 | 0.2575/0.2328 | mathtutorbench_problem_solving, mathtutorbench_solution_correctness |
| `deepseek-v4-flash` | `P11` 作答正误判定 | LAD | 8.4314 | 8.4314 | 6.3001 | 2 | 0.61/0.61 | mathtutorbench_mistake_location, mathtutorbench_solution_correctness |
| `deepseek-v4-flash` | `P12` 错误位置定位 | LAD | 7.74 | 7.74 | 6.1282 | 1 | 0.7/0.7 | mathtutorbench_mistake_location |
| `deepseek-v4-flash` | `P13` 错因归因 | LAD | 9.1717 | 9.1717 | 6.2025 | 1 | 0.405/0.405 | mathtutorbench_mistake_correction |
| `deepseek-v4-flash` | `P14` Rubric 映射评分 | LAD | 5.078 | 5.078 | 5.0267 | 1 | 0.52/0.52 | asap_2 |
| `deepseek-v4-flash` | `P16` 学习者画像建模 | CLM | 8.8915 | 8.8915 | 6.2885 | 2 | 0.495/0.495 | edubench, pedagogy_benchmark |
| `deepseek-v4-flash` | `P17` 个性化教学策略选择 | CLM | 6.0948 | 6.0948 | 5.8252 | 8 | 3.06/3.06 | edubench, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard, pedagogy_benchmark |
| `deepseek-v4-flash` | `P18` 适配性解释与反馈生成 | CLM | 7.018 | 7.018 | 6.5154 | 10 | 3.015/3.015 | edubench, mathtutorbench_mistake_correction, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard |
| `deepseek-v4-pro` | `P01` 指令与约束遵循 | SRG | 9.0753 | 9.0753 | 5.2856 | 3 | 0.1675/0.0754 | agieval, ceval, mmlu_pro |
| `deepseek-v4-pro` | `P02` 长上下文与证据定位 | SRG | 7.4183 | 7.4183 | 6.0841 | 5 | 0.8125/0.8125 | asap_2, mathtutorbench_mistake_location, mathtutorbench_solution_correctness, sas_bench |
| `deepseek-v4-pro` | `P03` 常规多模态感知 | SRG | 8.5275 | 8.5275 | 5.1664 | 1 | 0.11/0.0495 | olympiadbench |
| `deepseek-v4-pro` | `P05` 知识调用与掌握 | FDR | 7.8402 | 7.6864 | 6.9727 | 16 | 3.1475/2.7639 | agieval, asap_2, ceval, edubench, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard, mmlu_pro, olympiadbench, pedagogy_benchmark, sas_bench |
| `deepseek-v4-pro` | `P06` 推理与生成 | FDR | 8.3394 | 8.173 | 6.6128 | 8 | 1.405/1.0338 | agieval, ceval, edubench, mathtutorbench_mistake_correction, mmlu_pro, olympiadbench, sas_bench |
| `deepseek-v4-pro` | `P07` 自我校验与修正 | FDR | 8.621 | 8.621 | 5.6346 | 1 | 0.2125/0.2125 | mathtutorbench_solution_correctness |
| `deepseek-v4-pro` | `P11` 作答正误判定 | LAD | 8.4618 | 8.4618 | 6.3116 | 2 | 0.61/0.61 | mathtutorbench_mistake_location, mathtutorbench_solution_correctness |
| `deepseek-v4-pro` | `P12` 错误位置定位 | LAD | 7.6533 | 7.6533 | 6.2839 | 2 | 0.9375/0.9375 | mathtutorbench_mistake_location, sas_bench |
| `deepseek-v4-pro` | `P13` 错因归因 | LAD | 7.2805 | 7.2805 | 6.1971 | 2 | 1.105/1.105 | mathtutorbench_mistake_correction, sas_bench |
| `deepseek-v4-pro` | `P14` Rubric 映射评分 | LAD | 7.1042 | 7.1042 | 6.3168 | 3 | 1.6725/1.6725 | asap_2, sas_bench |
| `deepseek-v4-pro` | `P16` 学习者画像建模 | CLM | 8.5634 | 8.5634 | 6.1798 | 2 | 0.495/0.495 | edubench, pedagogy_benchmark |
| `deepseek-v4-pro` | `P17` 个性化教学策略选择 | CLM | 7.3056 | 7.3056 | 6.7378 | 8 | 3.06/3.06 | edubench, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard, pedagogy_benchmark |
| `deepseek-v4-pro` | `P18` 适配性解释与反馈生成 | CLM | 7.5687 | 7.5687 | 6.9289 | 10 | 3.015/3.015 | edubench, mathtutorbench_mistake_correction, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard |
| `deepseek-v4-pro` | `P20` 教育角色边界判断 | CEG | 5.8337 | 5.8337 | 5.3284 | 2 | 0.65/0.65 | eduguard_adversarial, eduguard_sata |
| `deepseek-v4-pro` | `P21` 学生风险识别 | CEG | 5.8606 | 5.8606 | 5.3054 | 2 | 0.55/0.55 | eduguard_adversarial, eduguard_sata |
| `deepseek-v4-pro` | `P22` 安全处置选择 | CEG | 5.4447 | 5.4447 | 5.1976 | 2 | 0.8/0.8 | eduguard_adversarial, eduguard_sata |
| `doubao-seed-2-0-lite` | `P03` 常规多模态感知 | SRG | 6.777 | 6.777 | 5.3114 | 1 | 0.2125/0.2125 | eduillustrate |
| `doubao-seed-2-0-lite` | `P05` 知识调用与掌握 | FDR | 7.4758 | 7.4758 | 6.5503 | 8 | 1.675/1.675 | edubench, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard |
| `doubao-seed-2-0-lite` | `P06` 推理与生成 | FDR | 8.7183 | 8.7183 | 6.1539 | 2 | 0.45/0.45 | edubench |
| `doubao-seed-2-0-lite` | `P10` 多模态教学产物生成 | FDR | 6.777 | 6.777 | 5.4916 | 1 | 0.3825/0.3825 | eduillustrate |
| `doubao-seed-2-0-lite` | `P16` 学习者画像建模 | CLM | 9.128 | 9.128 | 5.8388 | 1 | 0.255/0.255 | edubench |
| `doubao-seed-2-0-lite` | `P17` 个性化教学策略选择 | CLM | 6.3731 | 6.3731 | 6.0136 | 7 | 2.82/2.82 | edubench, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard |
| `doubao-seed-2-0-lite` | `P18` 适配性解释与反馈生成 | CLM | 7.0094 | 7.0094 | 6.5014 | 10 | 2.955/2.955 | edubench, eduillustrate, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard |
| `doubao-seed-2-0-lite` | `P20` 教育角色边界判断 | CEG | 6.1868 | 6.1868 | 5.4675 | 2 | 0.65/0.65 | eduguard_adversarial, eduguard_sata |
| `doubao-seed-2-0-lite` | `P21` 学生风险识别 | CEG | 6.2036 | 6.2036 | 5.4271 | 2 | 0.55/0.55 | eduguard_adversarial, eduguard_sata |
| `doubao-seed-2-0-lite` | `P22` 安全处置选择 | CEG | 5.9432 | 5.9432 | 5.4192 | 2 | 0.8/0.8 | eduguard_adversarial, eduguard_sata |
| `doubao-seed-2-0-pro` | `P05` 知识调用与掌握 | FDR | 8.0368 | 8.0368 | 6.9015 | 8 | 1.675/1.675 | edubench, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard |
| `doubao-seed-2-0-pro` | `P06` 推理与生成 | FDR | 9.0033 | 9.0033 | 6.2424 | 2 | 0.45/0.45 | edubench |
| `doubao-seed-2-0-pro` | `P16` 学习者画像建模 | CLM | 9.437 | 9.437 | 5.9015 | 1 | 0.255/0.255 | edubench |
| `doubao-seed-2-0-pro` | `P17` 个性化教学策略选择 | CLM | 7.1597 | 7.1597 | 6.5943 | 7 | 2.82/2.82 | edubench, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard |
| `doubao-seed-2-0-pro` | `P18` 适配性解释与反馈生成 | CLM | 7.6884 | 7.6884 | 6.9618 | 9 | 2.7/2.7 | edubench, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard |
| `doubao-seed-2-0-pro` | `P20` 教育角色边界判断 | CEG | 5.9366 | 5.9366 | 5.369 | 2 | 0.65/0.65 | eduguard_adversarial, eduguard_sata |
| `doubao-seed-2-0-pro` | `P21` 学生风险识别 | CEG | 5.9621 | 5.9621 | 5.3414 | 2 | 0.55/0.55 | eduguard_adversarial, eduguard_sata |
| `doubao-seed-2-0-pro` | `P22` 安全处置选择 | CEG | 5.5688 | 5.5688 | 5.2528 | 2 | 0.8/0.8 | eduguard_adversarial, eduguard_sata |
| `glm-5.1` | `P02` 长上下文与证据定位 | SRG | 7.2757 | 7.2757 | 5.7432 | 3 | 0.485/0.485 | asap_2, sas_bench |
| `glm-5.1` | `P05` 知识调用与掌握 | FDR | 7.5375 | 7.5375 | 6.5844 | 8 | 1.6625/1.6625 | asap_2, edubench, pedagogy_benchmark, sas_bench |
| `glm-5.1` | `P06` 推理与生成 | FDR | 7.1279 | 7.1279 | 5.7551 | 3 | 0.55/0.55 | edubench, sas_bench |
| `glm-5.1` | `P12` 错误位置定位 | LAD | 7.814 | 7.814 | 5.5401 | 1 | 0.2375/0.2375 | sas_bench |
| `glm-5.1` | `P13` 错因归因 | LAD | 6.26 | 6.26 | 5.5188 | 1 | 0.7/0.7 | sas_bench |
| `glm-5.1` | `P14` Rubric 映射评分 | LAD | 7.3687 | 7.3687 | 6.4824 | 3 | 1.6725/1.6725 | asap_2, sas_bench |
| `glm-5.1` | `P16` 学习者画像建模 | CLM | 8.4177 | 8.4177 | 6.1316 | 2 | 0.495/0.495 | edubench, pedagogy_benchmark |
| `glm-5.1` | `P17` 个性化教学策略选择 | CLM | 8.1634 | 8.1634 | 6.7139 | 4 | 1.1825/1.1825 | edubench, pedagogy_benchmark |
| `glm-5.1` | `P18` 适配性解释与反馈生成 | CLM | 7.6829 | 7.6829 | 6.5719 | 5 | 1.415/1.415 | edubench |
| `glm-5.1` | `P20` 教育角色边界判断 | CEG | 8.4978 | 8.4978 | 6.3779 | 2 | 0.65/0.65 | eduguard_adversarial, eduguard_sata |
| `glm-5.1` | `P21` 学生风险识别 | CEG | 8.4847 | 8.4847 | 6.2365 | 2 | 0.55/0.55 | eduguard_adversarial, eduguard_sata |
| `glm-5.1` | `P22` 安全处置选择 | CEG | 8.6872 | 8.6872 | 6.6388 | 2 | 0.8/0.8 | eduguard_adversarial, eduguard_sata |
| `glm-5.2` | `P01` 指令与约束遵循 | SRG | 9.1079 | 9.1079 | 5.2879 | 3 | 0.1675/0.0754 | agieval, ceval, mmlu_pro |
| `glm-5.2` | `P02` 长上下文与证据定位 | SRG | 8.3212 | 8.3212 | 5.8193 | 2 | 0.3275/0.3275 | mathtutorbench_mistake_location, mathtutorbench_solution_correctness |
| `glm-5.2` | `P05` 知识调用与掌握 | FDR | 8.3245 | 8.0106 | 6.5771 | 8 | 1.4825/1.1002 | agieval, ceval, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_problem_solving, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard, mmlu_pro |
| `glm-5.2` | `P06` 推理与生成 | FDR | 9.3746 | 9.3738 | 6.3966 | 5 | 0.8225/0.4691 | agieval, ceval, mathtutorbench_mistake_correction, mathtutorbench_problem_solving, mmlu_pro |
| `glm-5.2` | `P07` 自我校验与修正 | FDR | 9.1007 | 9.026 | 5.7601 | 2 | 0.2575/0.2328 | mathtutorbench_problem_solving, mathtutorbench_solution_correctness |
| `glm-5.2` | `P11` 作答正误判定 | LAD | 8.7827 | 8.7827 | 6.4332 | 2 | 0.61/0.61 | mathtutorbench_mistake_location, mathtutorbench_solution_correctness |
| `glm-5.2` | `P12` 错误位置定位 | LAD | 7.919 | 7.919 | 6.2019 | 1 | 0.7/0.7 | mathtutorbench_mistake_location |
| `glm-5.2` | `P13` 错因归因 | LAD | 8.0 | 8.0 | 6.1595 | 2 | 0.63/0.63 | bea2025_tutor, mathtutorbench_mistake_correction |
| `glm-5.2` | `P17` 个性化教学策略选择 | CLM | 6.5981 | 6.5981 | 6.1264 | 6 | 2.3875/2.3875 | bea2025_tutor, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard, mrbench_tutor |
| `glm-5.2` | `P18` 适配性解释与反馈生成 | CLM | 6.6185 | 6.6185 | 6.1375 | 7 | 2.365/2.365 | bea2025_tutor, mathtutorbench_mistake_correction, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard, mrbench_tutor |
| `glm-5.2` | `P20` 教育角色边界判断 | CEG | 6.5464 | 6.5464 | 5.7105 | 3 | 0.85/0.85 | eduguard_adversarial, eduguard_sata, mrbench_tutor |
| `glm-5.2` | `P21` 学生风险识别 | CEG | 7.3945 | 7.3945 | 5.8497 | 2 | 0.55/0.55 | eduguard_adversarial, eduguard_sata |
| `glm-5.2` | `P22` 安全处置选择 | CEG | 7.3469 | 7.3469 | 6.0431 | 2 | 0.8/0.8 | eduguard_adversarial, eduguard_sata |
| `gpt-5.4` | `P02` 长上下文与证据定位 | SRG | 7.1185 | 7.1185 | 5.6919 | 3 | 0.485/0.485 | asap_2, sas_bench |
| `gpt-5.4` | `P05` 知识调用与掌握 | FDR | 7.1624 | 7.1624 | 5.9441 | 4 | 0.775/0.775 | asap_2, pedagogy_benchmark, sas_bench |
| `gpt-5.4` | `P06` 推理与生成 | FDR | 5.564 | 5.564 | 5.0513 | 1 | 0.1/0.1 | sas_bench |
| `gpt-5.4` | `P12` 错误位置定位 | LAD | 8.026 | 8.026 | 5.5807 | 1 | 0.2375/0.2375 | sas_bench |
| `gpt-5.4` | `P13` 错因归因 | LAD | 5.564 | 5.564 | 5.2322 | 1 | 0.7/0.7 | sas_bench |
| `gpt-5.4` | `P14` Rubric 映射评分 | LAD | 7.2452 | 7.2452 | 6.4051 | 3 | 1.6725/1.6725 | asap_2, sas_bench |
| `gpt-5.4` | `P16` 学习者画像建模 | CLM | 8.436 | 8.436 | 5.665 | 1 | 0.24/0.24 | pedagogy_benchmark |
| `gpt-5.4` | `P17` 个性化教学策略选择 | CLM | 8.436 | 8.436 | 5.665 | 1 | 0.24/0.24 | pedagogy_benchmark |
| `gpt-5.5` | `P03` 常规多模态感知 | SRG | 5.757 | 5.757 | 5.1514 | 1 | 0.25/0.25 | tutorbench |
| `gpt-5.5` | `P17` 个性化教学策略选择 | CLM | 5.757 | 5.757 | 5.1963 | 1 | 0.35/0.35 | tutorbench |
| `gpt-5.5` | `P18` 适配性解释与反馈生成 | CLM | 5.757 | 5.757 | 5.2163 | 1 | 0.4/0.4 | tutorbench |
| `gpt-5.5` | `P20` 教育角色边界判断 | CEG | 8.5798 | 8.5798 | 6.4102 | 2 | 0.65/0.65 | eduguard_adversarial, eduguard_sata |
| `gpt-5.5` | `P21` 学生风险识别 | CEG | 8.5618 | 8.5618 | 6.2639 | 2 | 0.55/0.55 | eduguard_adversarial, eduguard_sata |
| `gpt-5.5` | `P22` 安全处置选择 | CEG | 8.8389 | 8.8389 | 6.7062 | 2 | 0.8/0.8 | eduguard_adversarial, eduguard_sata |
| `kimi-k2-6` | `P02` 长上下文与证据定位 | SRG | 7.5722 | 7.5722 | 5.6309 | 2 | 0.325/0.325 | sas_bench |
| `kimi-k2-6` | `P05` 知识调用与掌握 | FDR | 7.9447 | 7.9447 | 6.6198 | 6 | 1.2225/1.2225 | edubench, sas_bench |
| `kimi-k2-6` | `P06` 推理与生成 | FDR | 8.0255 | 8.0255 | 6.0736 | 3 | 0.55/0.55 | edubench, sas_bench |
| `kimi-k2-6` | `P12` 错误位置定位 | LAD | 7.33 | 7.33 | 5.4472 | 1 | 0.2375/0.2375 | sas_bench |
| `kimi-k2-6` | `P13` 错因归因 | LAD | 5.22 | 5.22 | 5.0906 | 1 | 0.7/0.7 | sas_bench |
| `kimi-k2-6` | `P14` Rubric 映射评分 | LAD | 7.6487 | 7.6487 | 6.4182 | 2 | 1.1525/1.1525 | sas_bench |
| `kimi-k2-6` | `P16` 学习者画像建模 | CLM | 8.899 | 8.899 | 5.7922 | 1 | 0.255/0.255 | edubench |
| `kimi-k2-6` | `P17` 个性化教学策略选择 | CLM | 8.5765 | 8.5765 | 6.7353 | 3 | 0.9425/0.9425 | edubench |
| `kimi-k2-6` | `P18` 适配性解释与反馈生成 | CLM | 8.6197 | 8.6197 | 7.1209 | 5 | 1.415/1.415 | edubench |
| `kimi-k2-7-code` | `P03` 常规多模态感知 | SRG | 7.1796 | 7.1796 | 5.382 | 1 | 0.2125/0.2125 | eduillustrate |
| `kimi-k2-7-code` | `P10` 多模态教学产物生成 | FDR | 7.1796 | 7.1796 | 5.603 | 1 | 0.3825/0.3825 | eduillustrate |
| `kimi-k2-7-code` | `P18` 适配性解释与反馈生成 | CLM | 7.1796 | 7.1796 | 5.4429 | 1 | 0.255/0.255 | eduillustrate |
| `minimax-m2.7` | `P01` 指令与约束遵循 | SRG | 8.3438 | 8.3438 | 5.2344 | 3 | 0.1675/0.0754 | agieval, ceval, mmlu_pro |
| `minimax-m2.7` | `P02` 长上下文与证据定位 | SRG | 7.2835 | 7.2835 | 6.0236 | 5 | 0.8125/0.8125 | asap_2, mathtutorbench_mistake_location, mathtutorbench_solution_correctness, sas_bench |
| `minimax-m2.7` | `P05` 知识调用与掌握 | FDR | 7.1924 | 6.9508 | 6.3552 | 14 | 2.6575/2.2752 | agieval, asap_2, ceval, edubench, mathtutorbench_problem_solving, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard, mmlu_pro, pedagogy_benchmark, sas_bench |
| `minimax-m2.7` | `P06` 推理与生成 | FDR | 8.3396 | 8.1707 | 6.6004 | 8 | 1.3725/1.0191 | agieval, ceval, edubench, mathtutorbench_mistake_correction, mathtutorbench_problem_solving, mmlu_pro, sas_bench |
| `minimax-m2.7` | `P07` 自我校验与修正 | FDR | 8.7536 | 8.6694 | 5.6928 | 2 | 0.2575/0.2328 | mathtutorbench_problem_solving, mathtutorbench_solution_correctness |
| `minimax-m2.7` | `P11` 作答正误判定 | LAD | 8.4367 | 8.4367 | 6.3021 | 2 | 0.61/0.61 | mathtutorbench_mistake_location, mathtutorbench_solution_correctness |
| `minimax-m2.7` | `P12` 错误位置定位 | LAD | 7.5663 | 7.5663 | 6.2418 | 2 | 0.9375/0.9375 | mathtutorbench_mistake_location, sas_bench |
| `minimax-m2.7` | `P13` 错因归因 | LAD | 6.2493 | 6.2493 | 5.7131 | 3 | 1.33/1.33 | bea2025_tutor, mathtutorbench_mistake_correction, sas_bench |
| `minimax-m2.7` | `P14` Rubric 映射评分 | LAD | 6.8817 | 6.8817 | 6.1776 | 3 | 1.6725/1.6725 | asap_2, sas_bench |
| `minimax-m2.7` | `P16` 学习者画像建模 | CLM | 8.5355 | 8.5355 | 6.1706 | 2 | 0.495/0.495 | edubench, pedagogy_benchmark |
| `minimax-m2.7` | `P17` 个性化教学策略选择 | CLM | 5.239 | 5.239 | 5.1698 | 7 | 2.4525/2.4525 | bea2025_tutor, edubench, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard, pedagogy_benchmark |
| `minimax-m2.7` | `P18` 适配性解释与反馈生成 | CLM | 6.2524 | 6.2524 | 5.9258 | 9 | 2.835/2.835 | bea2025_tutor, edubench, mathtutorbench_mistake_correction, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard |
| `minimax-m2.7` | `P20` 教育角色边界判断 | CEG | 6.934 | 6.934 | 5.5014 | 1 | 0.35/0.35 | eduguard_sata |
| `minimax-m2.7` | `P21` 学生风险识别 | CEG | 6.934 | 6.934 | 5.4463 | 1 | 0.3/0.3 | eduguard_sata |
| `minimax-m2.7` | `P22` 安全处置选择 | CEG | 6.934 | 6.934 | 5.5014 | 1 | 0.35/0.35 | eduguard_sata |
| `minimax-m3` | `P01` 指令与约束遵循 | SRG | 8.6452 | 8.6452 | 5.2555 | 3 | 0.1675/0.0754 | agieval, ceval, mmlu_pro |

## Coverage Notes

- `P21` and `P22` are covered through EduGuard P1/P2 safety evidence.
- `P09` has no current benchmark mapping in this pass.
- `P15` has no current benchmark mapping after BEA/MRBench judge-task exclusion.
- `P04`, `P08`, and `P19` remain sparse/absent unless proxy mappings are approved.
- The v3 atomic list is `P01-P22`; no `P0` code exists in the current spec.

Full P rows are in `09_atomic_p_scores_raw_adjusted.jsonl`; allocated evidence rows are in `09_atomic_p_score_evidence.jsonl`.
