# 映射效度检查报告（13 号）

生成脚本：`scripts/build_mapping_validation.py`（幂等）；测量模型：`data/mapping_measurement_model_v6.json`（adjudicated）。
规则见 `doc/mapping_validation_plan_2026-07-11.md` §2；ρ 一律与 n、90% CI 同格呈现，n<5 的配对只进低置信附录。

覆盖缺口（无任何 benchmark 映射，不参与本报告分析）：P09 工具使用与长程智能体执行、P20 学术诚信与作答真实性判定。

## Phase 0：天花板/方差受限名单

共 35 / 62 个有证据格子被标记 `variance_restricted`（mean≥8.5 或 n≥4 且 SD<0.5）。这些格子参与的配对**不进入裁决**；优先动作是上难度/换切分，不是改映射。

| Benchmark | Subdimension | n | mean | SD | 标记 |
|---|---|---:|---:|---:|---|
| `mrbench_tutor` | dimension: Tutor_Tone (non-offensive) | 7 | 10.0 | 0.0 | ceiling, low_variance |
| `bea2025_tutor` | dimension: Providing_Guidance | 7 | 9.716 | 0.169 | ceiling, low_variance |
| `mathtutorbench_problem_solving` | Problem Solving | 7 | 9.689 | 0.097 | ceiling, low_variance |
| `bea2025_tutor` | dimension: Actionability | 7 | 9.555 | 0.219 | ceiling, low_variance |
| `longtutor_evidence` | Information Extraction accuracy | 7 | 9.528 | 0.147 | ceiling, low_variance |
| `mrbench_tutor` | dimension: Actionability | 7 | 9.505 | 0.253 | ceiling, low_variance |
| `mrbench_tutor` | dimension: Mistake_Identification | 7 | 9.423 | 0.257 | ceiling, low_variance |
| `edubench` | QG × domain_knowledge_accuracy + basic_factual_accuracy (task×metric) | 14 | 9.309 | 0.382 | ceiling, low_variance |
| `mrbench_tutor` | dimension: Providing_Guidance | 7 | 9.224 | 0.228 | ceiling, low_variance |
| `edubench` | basic_factual_accuracy (metric) | 14 | 9.186 | 0.405 | ceiling, low_variance |
| `ifeval` | prompt-level strict accuracy | 7 | 9.125 | 0.232 | ceiling, low_variance |
| `mathtutorbench_mistake_correction` | Mistake Correction | 8 | 9.079 | 0.319 | ceiling, low_variance |
| `p08_abstention` | balanced abstention score | 7 | 8.991 | 0.244 | ceiling, low_variance |
| `ceval` | overall/category/subject accuracy | 9 | 8.974 | 0.455 | ceiling, low_variance |
| `bea2025_tutor` | dimension: Mistake_Identification | 7 | 8.864 | 0.272 | ceiling, low_variance |
| `edubench` | domain_knowledge_accuracy (metric) | 14 | 8.769 | 0.591 | ceiling |
| `agieval` | overall/task/language/question_type accuracy | 8 | 8.763 | 0.392 | ceiling, low_variance |
| `mathtutorbench_solution_correctness` | Solution Correctness | 8 | 8.732 | 0.138 | ceiling, low_variance |
| `mathvista` | task/question_type/answer_type accuracy | 4 | 8.557 | 0.238 | ceiling, low_variance |
| `mmlu_pro` | overall/category accuracy | 8 | 8.525 | 0.297 | ceiling, low_variance |
| `edubench` | clarity_concision_inspiration (metric) | 14 | 8.333 | 0.344 | low_variance |
| `mathtutorbench_pedagogy` | Pedagogy IF | 9 | 8.29 | 0.498 | low_variance |
| `sas_bench` | QWK holistic total score | 10 | 8.28 | 0.247 | low_variance |
| `edubench` | QG × clarity_concision_inspiration + scenario_element_integration (task×metric) | 14 | 8.251 | 0.36 | low_variance |
| `edubench` | scenario_element_integration (metric) | 14 | 7.827 | 0.395 | low_variance |
| `mathtutorbench_mistake_location` | Mistake Location | 8 | 7.711 | 0.147 | low_variance |
| `k12vista` | math problem-figure subset score | 4 | 7.698 | 0.255 | low_variance |
| `sas_bench` | CCS step scoring consistency | 10 | 7.632 | 0.268 | low_variance |
| `eduguard_sata` | Teaching Harm / SATA RFS | 10 | 7.488 | 0.228 | low_variance |
| `olympiadbench` | multimodal-subset accuracy | 4 | 7.06 | 0.48 | low_variance |
| `edubench` | motivation_guidance_positive_feedback (metric) | 14 | 6.55 | 0.295 | low_variance |
| `edubench` | personalized_adaptation_learning_support (metric) | 14 | 6.478 | 0.389 | low_variance |
| `tutorbench` | Fair815 multimodal tutor quality | 6 | 5.478 | 0.25 | low_variance |
| `p07_selfcheck` | two-round self-check (fix/break rate) | 7 | 5.196 | 0.244 | low_variance |
| `mathtutorbench_socratic` | Socratic Questioning | 7 | 2.799 | 0.366 | low_variance |

## 红旗配对（flagged：同 P 预期收敛却 ρ<0，n≥6）

每条 flagged 需人工裁决：改权重 / 拆 facet / 转裁判治理（计划 §2.6）。

| A | B | 共享 P（权重A/B） | n | ρ | 偏ρ(控综合分) | perm p | 90% CI | 评级 |
|---|---|---|---:|---:|---:|---:|---|---|
| `edubench` reasoning_process_rigor (metric) | `sas_bench` ECS error-cause consistency | P06(0.5/0.2) | 9 | -0.033 | -0.007 | 0.9467 | [-0.67, 0.714] | flagged |

## 观察带（watch：0≤ρ<0.2 且 n≥8）

| A | B | 共享 P（权重A/B） | n | ρ | 偏ρ(控综合分) | perm p | 90% CI | 评级 |
|---|---|---|---:|---:|---:|---:|---|---|
| `edubench` error_identification_correction_accuracy (metric) | `sas_bench` ECS error-cause consistency | P10(0.2/0.8) | 9 | 0.117 | 0.132 | 0.7751 | [-0.443, 0.726] | watch |
| `edubench` higher_order_thinking_ability_development (metric) | `sas_bench` ECS error-cause consistency | P06(0.2/0.2) | 9 | 0.05 | 0.149 | 0.9105 | [-0.625, 0.737] | watch |

## 已验证配对（validated：ρ≥0.5 且 CI 下界>0）

| A | B | 共享 P（权重A/B） | n | ρ | 偏ρ(控综合分) | perm p | 90% CI | 评级 |
|---|---|---|---:|---:|---:|---:|---|---|
| `mathtutorbench_pedagogy_hard` Pedagogy IF hard | `pedagogy_benchmark` SEND special education needs selection | P05(0.2/0.5), P14(0.5/0.5 异facet) | 7 | 0.991 | 0.993 | 0.0008 | [0.923, 1.0] | validated |
| `mathtutorbench_scaffolding_hard` Scaffolding hard | `pedagogy_benchmark` SEND special education needs selection | P05(0.2/0.5), P14(0.5/0.5 异facet) | 7 | 0.829 | 0.726 | 0.0302 | [0.412, 1.0] | validated |
| `mathtutorbench_pedagogy_hard` Pedagogy IF hard | `pedagogy_benchmark` CDPK teaching knowledge selection | P05(0.2/0.5), P14(0.5/0.8 异facet) | 7 | 0.75 | 0.409 | 0.0663 | [0.074, 1.0] | validated |

## 待定配对（provisional）

| A | B | 共享 P（权重A/B） | n | ρ | 偏ρ(控综合分) | perm p | 90% CI | 评级 |
|---|---|---|---:|---:|---:|---:|---|---|
| `mathtutorbench_scaffolding` Scaffolding | `pedagogy_benchmark` CDPK teaching knowledge selection | P05(0.2/0.5), P14(0.5/0.8 异facet) | 7 | 0.107 | -0.226 | 0.8397 | [-0.585, 0.765] | provisional |
| `longtutor_teaching` judge dims: strategy_alignment + history_utilization (1-5) | `mathtutorbench_scaffolding` Scaffolding | P14(0.2/0.5) | 7 | 0.143 | -0.028 | 0.7825 | [-0.808, 0.867] | provisional |
| `olympiadbench` overall/subject/language/modality accuracy | `sas_bench` ECS error-cause consistency | P05(0.2/0.2), P06(0.5/0.2 异facet) | 6 | 0.2 | 0.204 | 0.7139 | [-1.0, 0.939] | provisional |
| `edubench` error_identification_correction_accuracy (metric) | `longtutor_diagnosis` four-category knowledge-state diagnosis macro-F1 | P10(0.2/0.2) | 7 | 0.286 | 0.289 | 0.556 | [-0.63, 0.887] | provisional |
| `longtutor_teaching` judge dims: strategy_alignment + history_utilization (1-5) | `mathtutorbench_scaffolding_hard` Scaffolding hard | P14(0.2/0.5) | 7 | 0.429 | 0.265 | 0.3536 | [-0.434, 0.887] | provisional |
| `mathtutorbench_scaffolding_hard` Scaffolding hard | `pedagogy_benchmark` CDPK teaching knowledge selection | P05(0.2/0.5), P14(0.5/0.8 异facet) | 7 | 0.429 | -0.057 | 0.3536 | [-0.216, 0.944] | provisional |
| `edubench` higher_order_thinking_ability_development (metric) | `mathtutorbench_scaffolding_hard` Scaffolding hard | P16(0.2/0.2) | 9 | 0.433 | -0.11 | 0.2511 | [-0.27, 0.836] | provisional |
| `longtutor_diagnosis` four-category knowledge-state diagnosis macro-F1 | `sas_bench` ECS error-cause consistency | P10(0.2/0.8) | 7 | 0.464 | 0.676 | 0.3024 | [-0.261, 0.963] | provisional |
| `edubench` TMG/PCC × clarity_concision_inspiration + scenario_element_integration (task×metric) | `eduillustrate` 8-dim 0-5 visual explanation score | P16(0.5/0.2) | 5 | 0.5 | — | 0.45 | [-0.667, 1.0] | provisional |
| `edubench` higher_order_thinking_ability_development (metric) | `mathtutorbench_scaffolding` Scaffolding | P16(0.2/0.2) | 9 | 0.517 | 0.284 | 0.1615 | [-0.113, 0.93] | provisional |
| `longtutor_teaching` judge dims: strategy_alignment + history_utilization (1-5) | `mathtutorbench_pedagogy_hard` Pedagogy IF hard | P14(0.2/0.5) | 7 | 0.536 | 0.43 | 0.2357 | [-0.17, 1.0] | provisional |
| `bea2025_judge` judge labels: mistake/guidance/actionability | `mrbench_judge` 8-dimension tutor response judging | P11(0.5/0.5) | 9 | 0.55 | -0.059 | 0.1342 | [-0.148, 1.0] | provisional |
| `edubench` higher_order_thinking_ability_development (metric) | `mathtutorbench_pedagogy_hard` Pedagogy IF hard | P16(0.2/0.2) | 9 | 0.6 | 0.25 | 0.1001 | [-0.105, 0.982] | provisional |
| `mathtutorbench_scaffolding` Scaffolding | `pedagogy_benchmark` SEND special education needs selection | P05(0.2/0.5), P14(0.5/0.5 异facet) | 7 | 0.613 | 0.678 | 0.1579 | [0.0, 1.0] | provisional |

## 因方差受限不裁决的配对

任一侧格子 variance_restricted；其 ρ 不作为构念证据。

| A | B | 共享 P（权重A/B） | n | ρ | 偏ρ(控综合分) | perm p | 90% CI | 评级 |
|---|---|---|---:|---:|---:|---:|---|---|
| `mathtutorbench_problem_solving` Problem Solving | `olympiadbench` overall/subject/language/modality accuracy | P05(0.2/0.2), P06(0.5/0.5) | 5 | -0.462 | -0.668 | 0.4333 | [-1.0, 1.0] | variance_restricted |
| `edubench` domain_knowledge_accuracy (metric) | `olympiadbench` overall/subject/language/modality accuracy | P05(0.2/0.2) | 6 | -0.429 | -0.544 | 0.4194 | [-1.0, 0.6] | variance_restricted |
| `longtutor_evidence` Hallucination Check accuracy | `mathtutorbench_mistake_location` Mistake Location | P02(0.8/0.2) | 7 | -0.429 | -0.731 | 0.3536 | [-1.0, 0.593] | variance_restricted |
| `edubench` clarity_concision_inspiration (metric) | `mrbench_tutor` dimension: Actionability | P16(0.2/0.2) | 7 | -0.357 | -0.73 | 0.4444 | [-1.0, 0.412] | variance_restricted |
| `mathtutorbench_mistake_correction` Mistake Correction | `sas_bench` ECS error-cause consistency | P06(0.2/0.2), P10(0.2/0.8) | 7 | -0.286 | -0.194 | 0.556 | [-0.887, 0.412] | variance_restricted |
| `edubench` basic_factual_accuracy (metric) | `sas_bench` ECS error-cause consistency | P05(0.2/0.2) | 9 | -0.283 | -0.255 | 0.4567 | [-0.846, 0.538] | variance_restricted |
| `edubench` basic_factual_accuracy (metric) | `olympiadbench` overall/subject/language/modality accuracy | P05(0.2/0.2) | 6 | -0.257 | -0.417 | 0.6583 | [-1.0, 0.818] | variance_restricted |
| `mathtutorbench_problem_solving` Problem Solving | `sas_bench` ECS error-cause consistency | P05(0.2/0.2), P06(0.5/0.2 异facet) | 6 | -0.232 | -0.03 | 0.6722 | [-0.949, 0.866] | variance_restricted |
| `edubench` personalized_adaptation_learning_support (metric) | `mrbench_tutor` dimension: Providing_Guidance | P14(0.5/0.2) | 7 | -0.179 | -0.531 | 0.7131 | [-0.887, 0.667] | variance_restricted |
| `mathtutorbench_solution_correctness` Solution Correctness | `p07_selfcheck` two-round self-check (fix/break rate) | P07(0.2/0.8) | 7 | -0.179 | -0.572 | 0.7131 | [-0.765, 0.68] | variance_restricted |
| `mmlu_pro` overall/category accuracy | `olympiadbench` overall/subject/language/modality accuracy | P05(0.5/0.2), P06(0.2/0.5) | 6 | -0.143 | -0.157 | 0.8028 | [-1.0, 0.636] | variance_restricted |
| `edubench` scenario_element_integration (metric) | `mathtutorbench_socratic` Socratic Questioning | P14(0.2/0.5) | 7 | -0.107 | -0.469 | 0.8397 | [-0.846, 1.0] | variance_restricted |
| `edubench` scenario_element_integration (metric) | `longtutor_teaching` judge dims: strategy_alignment + history_utilization (1-5) | P14(0.2/0.2) | 7 | -0.071 | -0.104 | 0.9063 | [-0.765, 0.704] | variance_restricted |
| `mmlu_pro` overall/category accuracy | `sas_bench` ECS error-cause consistency | P05(0.5/0.2), P06(0.2/0.2 异facet) | 7 | -0.036 | 0.193 | 0.9635 | [-0.846, 0.957] | variance_restricted |
| `edubench` clarity_concision_inspiration (metric) | `mathtutorbench_scaffolding_hard` Scaffolding hard | P16(0.2/0.2) | 9 | -0.033 | -0.455 | 0.95 | [-0.717, 0.67] | variance_restricted |
| `agieval` overall/task/language/question_type accuracy | `sas_bench` ECS error-cause consistency | P05(0.2/0.2), P06(0.5/0.2 异facet) | 7 | 0.0 | 0.224 | 1.0 | [-0.765, 0.667] | variance_restricted |
| `bea2025_tutor` dimension: Mistake_Identification | `edubench` error_identification_correction_accuracy (metric) | P10(0.2/0.2) | 7 | 0.0 | -0.01 | 1.0 | [-0.765, 0.882] | variance_restricted |
| `edubench` domain_knowledge_accuracy (metric) | `sas_bench` ECS error-cause consistency | P05(0.2/0.2) | 9 | 0.0 | 0.056 | 1.0 | [-0.651, 0.812] | variance_restricted |
| `edubench` error_identification_correction_accuracy (metric) | `mathtutorbench_mistake_correction` Mistake Correction | P10(0.2/0.2) | 8 | 0.0 | -0.212 | 1.0 | [-0.744, 0.62] | variance_restricted |
| `p07_selfcheck` two-round self-check (fix/break rate) | `p08_calibration` calibration composite (CWR/AUROC) | P07(0.8/0.2), P08(0.2/0.8) | 7 | 0.0 | -0.239 | 1.0 | [-0.852, 0.889] | variance_restricted |
| `bea2025_tutor` dimension: Providing_Guidance | `edubench` personalized_adaptation_learning_support (metric) | P14(0.2/0.5) | 7 | 0.036 | -0.413 | 0.9508 | [-0.765, 0.963] | variance_restricted |
| `edubench` personalized_adaptation_learning_support (metric) | `pedagogy_benchmark` SEND special education needs selection | P13(0.2/0.2), P14(0.5/0.5 异facet) | 10 | 0.043 | 0.077 | 0.9113 | [-0.538, 0.686] | variance_restricted |
| `agieval` overall/task/language/question_type accuracy | `edubench` basic_factual_accuracy (metric) | P05(0.2/0.2) | 8 | 0.071 | -0.239 | 0.882 | [-0.726, 0.797] | variance_restricted |
| `ceval` overall/category/subject accuracy | `edubench` basic_factual_accuracy (metric) | P05(0.5/0.2) | 8 | 0.071 | -0.188 | 0.882 | [-0.778, 0.923] | variance_restricted |
| `edubench` clarity_concision_inspiration (metric) | `mathtutorbench_socratic` Socratic Questioning | P16(0.2/0.2) | 7 | 0.071 | -0.974 | 0.9063 | [-0.731, 1.0] | variance_restricted |
| `longtutor_evidence` Hallucination Check accuracy | `sas_bench` CCS step scoring consistency | P02(0.8/0.2) | 7 | 0.071 | 0.022 | 0.9063 | [-0.882, 0.961] | variance_restricted |
| `edubench` clarity_concision_inspiration (metric) | `mathtutorbench_scaffolding` Scaffolding | P16(0.2/0.2) | 9 | 0.083 | -0.113 | 0.842 | [-0.67, 0.739] | variance_restricted |
| `edubench` scenario_element_integration (metric) | `mathtutorbench_pedagogy` Pedagogy IF | P14(0.2/0.5) | 9 | 0.083 | -0.195 | 0.8478 | [-0.579, 0.712] | variance_restricted |
| `bea2025_tutor` dimension: Providing_Guidance | `longtutor_teaching` judge dims: strategy_alignment + history_utilization (1-5) | P14(0.2/0.2) | 7 | 0.09 | -0.103 | 0.8595 | [-0.647, 0.765] | variance_restricted |
| `edubench` scenario_element_integration (metric) | `mathtutorbench_scaffolding` Scaffolding | P14(0.2/0.5) | 9 | 0.1 | -0.103 | 0.8055 | [-0.635, 0.945] | variance_restricted |
| `edubench` clarity_concision_inspiration (metric) | `mathtutorbench_pedagogy_hard` Pedagogy IF hard | P16(0.2/0.2) | 9 | 0.117 | -0.192 | 0.7769 | [-0.59, 0.722] | variance_restricted |
| `agieval` overall/task/language/question_type accuracy | `olympiadbench` overall/subject/language/modality accuracy | P05(0.2/0.2), P06(0.5/0.5) | 6 | 0.143 | 0.2 | 0.8028 | [-0.806, 0.92] | variance_restricted |
| `bea2025_tutor` dimension: Mistake_Identification | `sas_bench` ECS error-cause consistency | P10(0.2/0.8) | 7 | 0.143 | 0.179 | 0.7825 | [-0.585, 1.0] | variance_restricted |
| `edubench` clarity_concision_inspiration (metric) | `mathtutorbench_mistake_correction` Mistake Correction | P16(0.2/0.2) | 8 | 0.143 | -0.105 | 0.752 | [-0.585, 0.728] | variance_restricted |
| `edubench` error_identification_correction_accuracy (metric) | `mrbench_tutor` dimension: Mistake_Identification | P10(0.2/0.2) | 7 | 0.143 | 0.124 | 0.7825 | [-0.654, 1.0] | variance_restricted |
| `longtutor_teaching` judge dims: strategy_alignment + history_utilization (1-5) | `mrbench_tutor` dimension: Providing_Guidance | P14(0.2/0.2) | 7 | 0.143 | 0.032 | 0.7825 | [-0.615, 0.887] | variance_restricted |
| `edubench` personalized_adaptation_learning_support (metric) | `mathtutorbench_scaffolding` Scaffolding | P14(0.5/0.5) | 9 | 0.167 | -0.258 | 0.6683 | [-0.509, 0.655] | variance_restricted |
| `mathtutorbench_pedagogy` Pedagogy IF | `mrbench_tutor` dimension: Providing_Guidance | P14(0.5/0.2) | 7 | 0.179 | -0.1 | 0.7131 | [-0.647, 1.0] | variance_restricted |
| `edubench` personalized_adaptation_learning_support (metric) | `mathtutorbench_pedagogy` Pedagogy IF | P14(0.5/0.5) | 9 | 0.2 | -0.36 | 0.6208 | [-0.409, 0.714] | variance_restricted |
| `mathtutorbench_pedagogy_hard` Pedagogy IF hard | `mrbench_tutor` dimension: Providing_Guidance | P14(0.5/0.2) | 7 | 0.214 | 0.025 | 0.6615 | [-0.647, 1.0] | variance_restricted |
| `mrbench_judge` 8-dimension tutor response judging | `sas_bench` CCS step scoring consistency | P11(0.5/0.5) | 7 | 0.214 | -0.331 | 0.6615 | [-0.778, 0.961] | variance_restricted |
| `ceval` overall/category/subject accuracy | `sas_bench` ECS error-cause consistency | P05(0.5/0.2), P06(0.2/0.2 异facet) | 7 | 0.25 | 0.49 | 0.5948 | [-0.519, 0.882] | variance_restricted |
| `edubench` personalized_adaptation_learning_support (metric) | `longtutor_teaching` judge dims: strategy_alignment + history_utilization (1-5) | P14(0.5/0.2) | 7 | 0.25 | 0.029 | 0.5948 | [-0.765, 0.887] | variance_restricted |
| `edubench` scenario_element_integration (metric) | `mrbench_tutor` dimension: Providing_Guidance | P14(0.2/0.2) | 7 | 0.25 | 0.24 | 0.5948 | [-0.585, 0.957] | variance_restricted |
| `mathtutorbench_scaffolding` Scaffolding | `mrbench_tutor` dimension: Actionability | P16(0.2/0.2) | 7 | 0.25 | 0.023 | 0.5948 | [-0.698, 1.0] | variance_restricted |
| `bea2025_tutor` dimension: Providing_Guidance | `edubench` scenario_element_integration (metric) | P14(0.2/0.2) | 7 | 0.252 | 0.25 | 0.5905 | [-0.75, 0.963] | variance_restricted |
| `edubench` clarity_concision_inspiration (metric) | `mathtutorbench_pedagogy` Pedagogy IF | P16(0.2/0.2) | 9 | 0.267 | 0.069 | 0.5032 | [-0.459, 0.828] | variance_restricted |
| `edubench` personalized_adaptation_learning_support (metric) | `mathtutorbench_pedagogy_hard` Pedagogy IF hard | P14(0.5/0.5) | 9 | 0.283 | -0.344 | 0.4645 | [-0.282, 0.704] | variance_restricted |
| `longtutor_diagnosis` four-category knowledge-state diagnosis macro-F1 | `mathtutorbench_mistake_correction` Mistake Correction | P10(0.2/0.2) | 7 | 0.286 | -0.118 | 0.556 | [-0.556, 0.882] | variance_restricted |
| `mrbench_tutor` dimension: Mistake_Identification | `sas_bench` ECS error-cause consistency | P10(0.2/0.8) | 7 | 0.286 | 0.445 | 0.556 | [-0.412, 0.961] | variance_restricted |
| `edubench` scenario_element_integration (metric) | `mathtutorbench_pedagogy_hard` Pedagogy IF hard | P14(0.2/0.5) | 9 | 0.3 | 0.065 | 0.4454 | [-0.386, 0.846] | variance_restricted |
| `edubench` basic_factual_accuracy (metric) | `mmlu_pro` overall/category accuracy | P05(0.2/0.5) | 8 | 0.31 | 0.05 | 0.4618 | [-0.659, 0.865] | variance_restricted |
| `ceval` overall/category/subject accuracy | `olympiadbench` overall/subject/language/modality accuracy | P05(0.5/0.2), P06(0.2/0.5) | 6 | 0.314 | 0.35 | 0.5639 | [-0.636, 1.0] | variance_restricted |
| `edubench` scenario_element_integration (metric) | `mathtutorbench_scaffolding_hard` Scaffolding hard | P14(0.2/0.5) | 9 | 0.317 | 0.076 | 0.4038 | [-0.446, 1.0] | variance_restricted |
| `mathtutorbench_socratic` Socratic Questioning | `mrbench_tutor` dimension: Providing_Guidance | P14(0.5/0.2) | 7 | 0.321 | 0.065 | 0.4976 | [-0.444, 0.957] | variance_restricted |
| `bea2025_tutor` dimension: Actionability | `mrbench_tutor` dimension: Actionability | P16(0.2/0.2) | 7 | 0.393 | -0.036 | 0.3956 | [-0.593, 0.867] | variance_restricted |
| `edubench` higher_order_thinking_ability_development (metric) | `mrbench_tutor` dimension: Actionability | P16(0.2/0.2) | 7 | 0.393 | -0.036 | 0.3956 | [-0.593, 0.852] | variance_restricted |
| `bea2025_tutor` dimension: Providing_Guidance | `mathtutorbench_socratic` Socratic Questioning | P14(0.2/0.5) | 7 | 0.396 | -0.171 | 0.381 | [-0.705, 0.832] | variance_restricted |
| `edubench` reasoning_process_rigor (metric) | `mathtutorbench_mistake_correction` Mistake Correction | P06(0.5/0.2) | 8 | 0.405 | -0.098 | 0.3268 | [-0.425, 0.975] | variance_restricted |
| `edubench` personalized_adaptation_learning_support (metric) | `mathtutorbench_scaffolding_hard` Scaffolding hard | P14(0.5/0.5) | 9 | 0.417 | -0.143 | 0.273 | [-0.231, 0.826] | variance_restricted |
| `longtutor_teaching` judge dims: strategy_alignment + history_utilization (1-5) | `mathtutorbench_pedagogy` Pedagogy IF | P14(0.2/0.5) | 7 | 0.464 | 0.318 | 0.3024 | [-0.208, 1.0] | variance_restricted |
| `bea2025_tutor` dimension: Mistake_Identification | `longtutor_diagnosis` four-category knowledge-state diagnosis macro-F1 | P10(0.2/0.2) | 7 | 0.5 | 0.5 | 0.2667 | [-0.185, 0.923] | variance_restricted |
| `edubench` domain_knowledge_accuracy (metric) | `mmlu_pro` overall/category accuracy | P05(0.2/0.5) | 8 | 0.5 | 0.262 | 0.2162 | [-0.263, 1.0] | variance_restricted |
| `mathtutorbench_scaffolding` Scaffolding | `mrbench_tutor` dimension: Providing_Guidance | P14(0.5/0.2) | 7 | 0.5 | 0.418 | 0.2667 | [-0.208, 0.961] | variance_restricted |
| `bea2025_tutor` dimension: Providing_Guidance | `mathtutorbench_pedagogy` Pedagogy IF | P14(0.2/0.5) | 7 | 0.523 | 0.273 | 0.2349 | [-0.412, 1.0] | variance_restricted |
| `ceval` overall/category/subject accuracy | `edubench` domain_knowledge_accuracy (metric) | P05(0.5/0.2) | 8 | 0.524 | 0.355 | 0.1966 | [-0.16, 0.926] | variance_restricted |
| `bea2025_tutor` dimension: Actionability | `edubench` clarity_concision_inspiration (metric) | P16(0.2/0.2) | 7 | 0.536 | 0.356 | 0.2357 | [-0.321, 1.0] | variance_restricted |
| `mathtutorbench_mistake_correction` Mistake Correction | `mrbench_tutor` dimension: Actionability | P16(0.2/0.2) | 7 | 0.536 | 0.295 | 0.2357 | [-0.167, 1.0] | variance_restricted |
| `mathtutorbench_pedagogy` Pedagogy IF | `mrbench_tutor` dimension: Actionability | P16(0.2/0.2) | 7 | 0.536 | 0.281 | 0.2357 | [-0.208, 0.887] | variance_restricted |
| `mathtutorbench_scaffolding_hard` Scaffolding hard | `mrbench_tutor` dimension: Actionability | P16(0.2/0.2) | 7 | 0.536 | 0.295 | 0.2357 | [-0.333, 1.0] | variance_restricted |
| `mathtutorbench_solution_correctness` Solution Correctness | `p08_calibration` calibration composite (CWR/AUROC) | P07(0.2/0.2) | 7 | 0.536 | 0.055 | 0.2357 | [-0.176, 0.887] | variance_restricted |
| `agieval` overall/task/language/question_type accuracy | `edubench` domain_knowledge_accuracy (metric) | P05(0.2/0.2) | 8 | 0.571 | 0.406 | 0.1511 | [-0.013, 0.923] | variance_restricted |
| `bea2025_tutor` dimension: Actionability | `mathtutorbench_scaffolding` Scaffolding | P16(0.2/0.2) | 7 | 0.571 | 0.376 | 0.2 | [-0.059, 0.962] | variance_restricted |
| `edubench` motivation_guidance_positive_feedback (metric) | `mrbench_tutor` dimension: Tutor_Tone (encouraging share) | P16(0.5/0.2) | 7 | 0.571 | 0.536 | 0.2 | [-0.094, 1.0] | variance_restricted |
| `bea2025_tutor` dimension: Providing_Guidance | `mathtutorbench_pedagogy_hard` Pedagogy IF hard | P14(0.2/0.5) | 7 | 0.577 | 0.405 | 0.1857 | [-0.21, 1.0] | variance_restricted |
| `ceval` overall/category/subject accuracy | `mathtutorbench_problem_solving` Problem Solving | P05(0.5/0.2), P06(0.2/0.5) | 7 | 0.595 | 0.168 | 0.1698 | [-0.063, 1.0] | variance_restricted |
| `longtutor_teaching` judge dims: strategy_alignment + history_utilization (1-5) | `mathtutorbench_socratic` Socratic Questioning | P14(0.2/0.5) | 7 | 0.607 | 0.795 | 0.1667 | [-0.148, 1.0] | variance_restricted |
| `mathtutorbench_scaffolding_hard` Scaffolding hard | `mrbench_tutor` dimension: Providing_Guidance | P14(0.5/0.2) | 7 | 0.607 | 0.57 | 0.1667 | [-0.038, 1.0] | variance_restricted |
| `agieval` overall/task/language/question_type accuracy | `mathtutorbench_problem_solving` Problem Solving | P05(0.2/0.2), P06(0.5/0.5) | 7 | 0.631 | 0.278 | 0.1413 | [-0.059, 1.0] | variance_restricted |
| `edubench` basic_factual_accuracy (metric) | `mathtutorbench_problem_solving` Problem Solving | P05(0.2/0.2) | 7 | 0.631 | 0.512 | 0.1413 | [-0.066, 1.0] | variance_restricted |
| `bea2025_tutor` dimension: Actionability | `mathtutorbench_scaffolding_hard` Scaffolding hard | P16(0.2/0.2) | 7 | 0.643 | 0.141 | 0.1389 | [-0.125, 0.923] | variance_restricted |
| `bea2025_tutor` dimension: Mistake_Identification | `mathtutorbench_mistake_correction` Mistake Correction | P10(0.2/0.2) | 7 | 0.643 | 0.781 | 0.1389 | [-0.067, 1.0] | variance_restricted |
| `edubench` higher_order_thinking_ability_development (metric) | `mathtutorbench_mistake_correction` Mistake Correction | P06(0.2/0.2), P16(0.2/0.2) | 8 | 0.643 | 0.184 | 0.0962 | [-0.063, 1.0] | variance_restricted |
| `mathtutorbench_pedagogy_hard` Pedagogy IF hard | `mrbench_tutor` dimension: Actionability | P16(0.2/0.2) | 7 | 0.643 | 0.493 | 0.1389 | [-0.087, 0.923] | variance_restricted |
| `bea2025_tutor` dimension: Providing_Guidance | `mathtutorbench_scaffolding` Scaffolding | P14(0.2/0.5) | 7 | 0.667 | 0.57 | 0.1159 | [0.059, 0.961] | variance_restricted |
| `mathtutorbench_socratic` Socratic Questioning | `mrbench_tutor` dimension: Actionability | P16(0.2/0.2) | 7 | 0.679 | 0.667 | 0.1095 | [-0.125, 1.0] | variance_restricted |
| `mathtutorbench_problem_solving` Problem Solving | `mmlu_pro` overall/category accuracy | P05(0.2/0.5), P06(0.5/0.2) | 7 | 0.685 | 0.181 | 0.1 | [-0.067, 0.963] | variance_restricted |
| `bea2025_tutor` dimension: Actionability | `mathtutorbench_mistake_correction` Mistake Correction | P16(0.2/0.2) | 7 | 0.714 | 0.32 | 0.0881 | [0.059, 1.0] | variance_restricted |
| `bea2025_tutor` dimension: Actionability | `mathtutorbench_socratic` Socratic Questioning | P16(0.2/0.2) | 7 | 0.714 | -0.229 | 0.0881 | [-0.043, 1.0] | variance_restricted |
| `edubench` higher_order_thinking_ability_development (metric) | `mathtutorbench_socratic` Socratic Questioning | P16(0.2/0.2) | 7 | 0.714 | -0.229 | 0.0881 | [0.059, 1.0] | variance_restricted |
| `edubench` personalized_adaptation_learning_support (metric) | `mathtutorbench_socratic` Socratic Questioning | P14(0.5/0.5) | 7 | 0.714 | 0.413 | 0.0881 | [-0.067, 0.923] | variance_restricted |
| `longtutor_diagnosis` four-category knowledge-state diagnosis macro-F1 | `mrbench_tutor` dimension: Mistake_Identification | P10(0.2/0.2) | 7 | 0.714 | 0.629 | 0.0881 | [0.094, 1.0] | variance_restricted |
| `longtutor_evidence` Information Extraction accuracy | `mathtutorbench_mistake_location` Mistake Location | P02(0.8/0.2) | 7 | 0.714 | 0.26 | 0.0881 | [0.059, 1.0] | variance_restricted |
| `longtutor_evidence` Multi-session Reasoning accuracy | `mathtutorbench_mistake_location` Mistake Location | P02(0.8/0.2) | 7 | 0.714 | 0.15 | 0.0881 | [0.0, 1.0] | variance_restricted |
| `mathtutorbench_mistake_correction` Mistake Correction | `mrbench_tutor` dimension: Mistake_Identification | P10(0.2/0.2) | 7 | 0.714 | 0.617 | 0.0881 | [0.0, 1.0] | variance_restricted |
| `bea2025_tutor` dimension: Providing_Guidance | `mathtutorbench_scaffolding_hard` Scaffolding hard | P14(0.2/0.5) | 7 | 0.721 | 0.61 | 0.0794 | [0.162, 0.944] | variance_restricted |
| `edubench` domain_knowledge_accuracy (metric) | `mathtutorbench_problem_solving` Problem Solving | P05(0.2/0.2) | 7 | 0.721 | 0.575 | 0.077 | [-0.059, 1.0] | variance_restricted |
| `edubench` higher_order_thinking_ability_development (metric) | `mathtutorbench_pedagogy` Pedagogy IF | P16(0.2/0.2) | 9 | 0.733 | 0.549 | 0.032 | [0.217, 1.0] | variance_restricted |
| `bea2025_tutor` dimension: Actionability | `mathtutorbench_pedagogy_hard` Pedagogy IF hard | P16(0.2/0.2) | 7 | 0.75 | 0.554 | 0.0663 | [0.0, 1.0] | variance_restricted |
| `mathtutorbench_mistake_location` Mistake Location | `sas_bench` CCS step scoring consistency | P02(0.2/0.2), P10(0.8/0.2) | 7 | 0.75 | 0.355 | 0.0663 | [0.094, 1.0] | variance_restricted |
| `mathtutorbench_pedagogy` Pedagogy IF | `pedagogy_benchmark` CDPK teaching knowledge selection | P05(0.2/0.5), P14(0.5/0.8 异facet) | 7 | 0.75 | 0.409 | 0.0663 | [0.094, 1.0] | variance_restricted |
| `bea2025_tutor` dimension: Providing_Guidance | `mrbench_tutor` dimension: Providing_Guidance | P14(0.2/0.2) | 7 | 0.793 | 0.769 | 0.0397 | [0.321, 1.0] | variance_restricted |
| `longtutor_evidence` Multi-session Reasoning accuracy | `sas_bench` CCS step scoring consistency | P02(0.8/0.2) | 7 | 0.821 | 0.343 | 0.0341 | [0.407, 1.0] | variance_restricted |
| `bea2025_judge` judge labels: mistake/guidance/actionability | `sas_bench` CCS step scoring consistency | P11(0.5/0.5) | 7 | 0.857 | 0.521 | 0.0238 | [0.412, 1.0] | variance_restricted |
| `bea2025_tutor` dimension: Actionability | `mathtutorbench_pedagogy` Pedagogy IF | P16(0.2/0.2) | 7 | 0.857 | 0.639 | 0.0238 | [0.333, 1.0] | variance_restricted |
| `agieval` overall/task/language/question_type accuracy | `mmlu_pro` overall/category accuracy | P05(0.2/0.5), P06(0.5/0.2) | 8 | 0.881 | 0.775 | 0.0072 | [0.595, 1.0] | variance_restricted |
| `ceval` overall/category/subject accuracy | `mmlu_pro` overall/category accuracy | P05(0.5/0.5), P06(0.2/0.2) | 8 | 0.881 | 0.831 | 0.0072 | [0.556, 1.0] | variance_restricted |
| `bea2025_tutor` dimension: Mistake_Identification | `mrbench_tutor` dimension: Mistake_Identification | P10(0.2/0.2) | 7 | 0.893 | 0.943 | 0.0123 | [0.434, 1.0] | variance_restricted |
| `longtutor_evidence` Information Extraction accuracy | `sas_bench` CCS step scoring consistency | P02(0.8/0.2) | 7 | 0.929 | 0.78 | 0.0067 | [0.585, 1.0] | variance_restricted |
| `agieval` overall/task/language/question_type accuracy | `ceval` overall/category/subject accuracy | P05(0.2/0.5), P06(0.5/0.2) | 8 | 0.952 | 0.928 | 0.0011 | [0.73, 1.0] | variance_restricted |
| `mathtutorbench_pedagogy` Pedagogy IF | `pedagogy_benchmark` SEND special education needs selection | P05(0.2/0.5), P14(0.5/0.5 异facet) | 7 | 0.991 | 0.993 | 0.0008 | [0.923, 1.0] | variance_restricted |
| `bea2025_tutor` dimension: Actionability | `edubench` higher_order_thinking_ability_development (metric) | P16(0.2/0.2) | 7 | 1.0 | 1.0 | 0.0004 | [1.0, 1.0] | variance_restricted |

## 区分效度（同 P 收敛配对 vs 不共享 P 的 baseline）

- 收敛配对（跨家族、非受限、n≥5）：20 对，mean ρ = 0.426，median = 0.449
- baseline（不共享任何 P）：160 对，mean ρ = 0.236，median = 0.286
- 差值 = 0.189，单侧 permutation p = 0.0161（配对之间共享格子、非独立；p 值仅供参考，结论以红旗/非红旗为主。）

若差值不显著为正，说明 P 划分对'哪些 benchmark 相关'没有预测力，映射层需整体重审。

## 家族方法方差（halo）

| 家族 | 家族内配对数 | 家族内 mean ρ | 跨家族配对数 | 跨家族 mean ρ | halo 分 | 家族内先聚合? |
|---|---:|---:|---:|---:|---:|---|
| `pedagogy_benchmark` | 1 | 0.854 | 98 | 0.411 | 0.443 | 否 |
| `eduguard` | 3 | 0.357 | 88 | 0.002 | 0.355 | 否 |
| `edubench` | 66 | 0.428 | 504 | 0.129 | 0.298 | 否 |
| `mathtutorbench` | 36 | 0.575 | 381 | 0.35 | 0.225 | 否 |
| `sas_bench` | 3 | 0.329 | 147 | 0.239 | 0.091 | 否 |
| `p08` | 1 | 0.27 | 96 | 0.21 | 0.06 | 否 |
| `bea2025` | 6 | 0.431 | 184 | 0.381 | 0.049 | 否 |
| `longtutor_evidence` | 3 | 0.333 | 141 | 0.31 | 0.023 | 否 |
| `mrbench` | 10 | 0.147 | 225 | 0.272 | -0.126 | 否 |

halo 分 > 0.5 的家族：多子维度在 P 聚合前先合成一票（计划 §2.6）。

## P × 格子评级汇总

评级分布：validated=4、flagged=2、watch=3、provisional=16、variance_restricted=54、insufficient_evidence=19、single_source=6

| P | 类型 | facet | Benchmark | Subdimension | 权重 | 评级 |
|---|---|---|---|---|---:|---|
| P01 指令与约束遵循 | reflective | core | `ifeval` | prompt-level strict accuracy | 1.0 | **variance_restricted** |
| P02 长上下文与证据定位 | reflective | core | `longtutor_evidence` | Hallucination Check accuracy | 0.8 | **insufficient_evidence** |
| P02 长上下文与证据定位 | reflective | core | `longtutor_evidence` | Multi-session Reasoning accuracy | 0.8 | **insufficient_evidence** |
| P02 长上下文与证据定位 | reflective | core | `longtutor_evidence` | Information Extraction accuracy | 0.8 | **variance_restricted** |
| P02 长上下文与证据定位 | reflective | core | `mathtutorbench_mistake_location` | Mistake Location | 0.2 | **variance_restricted** |
| P02 长上下文与证据定位 | reflective | core | `sas_bench` | CCS step scoring consistency | 0.2 | **variance_restricted** |
| P03 多模态理解 | formative | subject_charts | `k12vista` | science/geo subject-chart subset score | 0.5 | **insufficient_evidence** |
| P03 多模态理解 | formative | mixed_materials | `mmtutorbench` | multimodal tutor score | 0.2 | **insufficient_evidence** |
| P03 多模态理解 | formative | problem_images | `k12vista` | math problem-figure subset score | 0.5 | **variance_restricted** |
| P03 多模态理解 | formative | problem_images | `mathvista` | task/question_type/answer_type accuracy | 0.5 | **variance_restricted** |
| P03 多模态理解 | formative | problem_images | `olympiadbench` | multimodal-subset accuracy | 0.2 | **variance_restricted** |
| P03 多模态理解 | formative | mixed_materials | `tutorbench` | Fair815 multimodal tutor quality | 0.2 | **variance_restricted** |
| P04 多模态生成 | formative | static_visual | `eduillustrate` | 8-dim 0-5 visual explanation score | 0.5 | **single_source** |
| P05 知识调用与掌握 | formative | subject_knowledge | `k12vista` | official partial-credit score (per-blank 0/1 mean) | 0.2 | **insufficient_evidence** |
| P05 知识调用与掌握 | formative | pedagogical_knowledge | `mathtutorbench_scaffolding` | Scaffolding | 0.2 | **provisional** |
| P05 知识调用与掌握 | formative | subject_knowledge | `olympiadbench` | overall/subject/language/modality accuracy | 0.2 | **provisional** |
| P05 知识调用与掌握 | formative | subject_knowledge | `sas_bench` | ECS error-cause consistency | 0.2 | **provisional** |
| P05 知识调用与掌握 | formative | pedagogical_knowledge | `mathtutorbench_pedagogy_hard` | Pedagogy IF hard | 0.2 | **validated** |
| P05 知识调用与掌握 | formative | pedagogical_knowledge | `mathtutorbench_scaffolding_hard` | Scaffolding hard | 0.2 | **validated** |
| P05 知识调用与掌握 | formative | pedagogical_knowledge | `pedagogy_benchmark` | CDPK teaching knowledge selection | 0.5 | **validated** |
| P05 知识调用与掌握 | formative | pedagogical_knowledge | `pedagogy_benchmark` | SEND special education needs selection | 0.5 | **validated** |
| P05 知识调用与掌握 | formative | subject_knowledge | `agieval` | overall/task/language/question_type accuracy | 0.2 | **variance_restricted** |
| P05 知识调用与掌握 | formative | subject_knowledge | `ceval` | overall/category/subject accuracy | 0.5 | **variance_restricted** |
| P05 知识调用与掌握 | formative | subject_knowledge | `edubench` | basic_factual_accuracy (metric) | 0.2 | **variance_restricted** |
| P05 知识调用与掌握 | formative | subject_knowledge | `edubench` | domain_knowledge_accuracy (metric) | 0.2 | **variance_restricted** |
| P05 知识调用与掌握 | formative | pedagogical_knowledge | `mathtutorbench_pedagogy` | Pedagogy IF | 0.2 | **variance_restricted** |
| P05 知识调用与掌握 | formative | subject_knowledge | `mathtutorbench_problem_solving` | Problem Solving | 0.2 | **variance_restricted** |
| P05 知识调用与掌握 | formative | subject_knowledge | `mathvista` | task/question_type/answer_type accuracy | 0.2 | **variance_restricted** |
| P05 知识调用与掌握 | formative | subject_knowledge | `mmlu_pro` | overall/category accuracy | 0.5 | **variance_restricted** |
| P06 推理与生成 | formative | generative_reasoning | `edubench` | reasoning_process_rigor (metric) | 0.5 | **flagged** |
| P06 推理与生成 | formative | generative_reasoning | `sas_bench` | ECS error-cause consistency | 0.2 | **flagged** |
| P06 推理与生成 | formative | problem_reasoning | `k12vista` | official partial-credit score (per-blank 0/1 mean) | 0.2 | **insufficient_evidence** |
| P06 推理与生成 | formative | problem_reasoning | `olympiadbench` | overall/subject/language/modality accuracy | 0.5 | **insufficient_evidence** |
| P06 推理与生成 | formative | problem_reasoning | `agieval` | overall/task/language/question_type accuracy | 0.5 | **variance_restricted** |
| P06 推理与生成 | formative | problem_reasoning | `ceval` | overall/category/subject accuracy | 0.2 | **variance_restricted** |
| P06 推理与生成 | formative | generative_reasoning | `mathtutorbench_mistake_correction` | Mistake Correction | 0.2 | **variance_restricted** |
| P06 推理与生成 | formative | problem_reasoning | `mathtutorbench_problem_solving` | Problem Solving | 0.5 | **variance_restricted** |
| P06 推理与生成 | formative | problem_reasoning | `mathvista` | task/question_type/answer_type accuracy | 0.5 | **variance_restricted** |
| P06 推理与生成 | formative | problem_reasoning | `mmlu_pro` | overall/category accuracy | 0.2 | **variance_restricted** |
| P06 推理与生成 | formative | generative_reasoning | `edubench` | higher_order_thinking_ability_development (metric) | 0.2 | **watch** |
| P07 自我校验与修正 | reflective | core | `p08_calibration` | calibration composite (CWR/AUROC) | 0.2 | **insufficient_evidence** |
| P07 自我校验与修正 | reflective | core | `mathtutorbench_solution_correctness` | Solution Correctness | 0.2 | **variance_restricted** |
| P07 自我校验与修正 | reflective | core | `p07_selfcheck` | two-round self-check (fix/break rate) | 0.8 | **variance_restricted** |
| P08 置信度校准与弃答 | formative | calibration | `p08_calibration` | calibration composite (CWR/AUROC) | 0.8 | **insufficient_evidence** |
| P08 置信度校准与弃答 | formative | calibration | `p07_selfcheck` | two-round self-check (fix/break rate) | 0.2 | **variance_restricted** |
| P08 置信度校准与弃答 | formative | abstention | `p08_abstention` | balanced abstention score | 0.8 | **variance_restricted** |
| P10 错误诊断 | formative | error_attribution | `longtutor_diagnosis` | four-category knowledge-state diagnosis macro-F1 | 0.2 | **provisional** |
| P10 错误诊断 | formative | error_attribution | `bea2025_tutor` | dimension: Mistake_Identification | 0.2 | **variance_restricted** |
| P10 错误诊断 | formative | error_attribution | `mathtutorbench_mistake_correction` | Mistake Correction | 0.2 | **variance_restricted** |
| P10 错误诊断 | formative | error_location | `mathtutorbench_mistake_location` | Mistake Location | 0.8 | **variance_restricted** |
| P10 错误诊断 | formative | answer_verdict | `mathtutorbench_solution_correctness` | Solution Correctness | 0.5 | **variance_restricted** |
| P10 错误诊断 | formative | error_attribution | `mrbench_tutor` | dimension: Mistake_Identification | 0.2 | **variance_restricted** |
| P10 错误诊断 | formative | error_location | `sas_bench` | CCS step scoring consistency | 0.2 | **variance_restricted** |
| P10 错误诊断 | formative | error_attribution | `edubench` | error_identification_correction_accuracy (metric) | 0.2 | **watch** |
| P10 错误诊断 | formative | error_attribution | `sas_bench` | ECS error-cause consistency | 0.8 | **watch** |
| P11 主观题评价能力 | formative | holistic_scoring | `asap_2` | essay holistic QWK | 0.8 | **insufficient_evidence** |
| P11 主观题评价能力 | formative | analytic_scoring | `bea2025_judge` | judge labels: mistake/guidance/actionability | 0.5 | **provisional** |
| P11 主观题评价能力 | formative | analytic_scoring | `mrbench_judge` | 8-dimension tutor response judging | 0.5 | **provisional** |
| P11 主观题评价能力 | formative | analytic_scoring | `sas_bench` | CCS step scoring consistency | 0.5 | **variance_restricted** |
| P11 主观题评价能力 | formative | holistic_scoring | `sas_bench` | QWK holistic total score | 0.8 | **variance_restricted** |
| P12 命题与作业设计 | formative | item_generation | `edubench` | QG × clarity_concision_inspiration + scenario_element_integration (task×metric) | 0.5 | **variance_restricted** |
| P12 命题与作业设计 | formative | item_generation | `edubench` | QG × domain_knowledge_accuracy + basic_factual_accuracy (task×metric) | 0.2 | **variance_restricted** |
| P13 学习者画像建模 | formative | knowledge_state_estimation | `longtutor_diagnosis` | four-category knowledge-state diagnosis macro-F1 | 0.8 | **insufficient_evidence** |
| P13 学习者画像建模 | formative | support_needs | `pedagogy_benchmark` | SEND special education needs selection | 0.2 | **insufficient_evidence** |
| P13 学习者画像建模 | formative | support_needs | `edubench` | personalized_adaptation_learning_support (metric) | 0.2 | **variance_restricted** |
| P14 个性化教学策略选择 | formative | strategy_enactment | `mmtutorbench` | multimodal tutor score | 0.2 | **insufficient_evidence** |
| P14 个性化教学策略选择 | formative | strategy_formulation | `pedagogy_benchmark` | CDPK teaching knowledge selection | 0.8 | **insufficient_evidence** |
| P14 个性化教学策略选择 | formative | strategy_formulation | `pedagogy_benchmark` | SEND special education needs selection | 0.5 | **insufficient_evidence** |
| P14 个性化教学策略选择 | formative | strategy_enactment | `longtutor_teaching` | judge dims: strategy_alignment + history_utilization (1-5) | 0.2 | **provisional** |
| P14 个性化教学策略选择 | formative | strategy_enactment | `mathtutorbench_pedagogy_hard` | Pedagogy IF hard | 0.5 | **provisional** |
| P14 个性化教学策略选择 | formative | strategy_enactment | `mathtutorbench_scaffolding` | Scaffolding | 0.5 | **provisional** |
| P14 个性化教学策略选择 | formative | strategy_enactment | `mathtutorbench_scaffolding_hard` | Scaffolding hard | 0.5 | **provisional** |
| P14 个性化教学策略选择 | formative | strategy_enactment | `bea2025_tutor` | dimension: Providing_Guidance | 0.2 | **variance_restricted** |
| P14 个性化教学策略选择 | formative | strategy_enactment | `edubench` | personalized_adaptation_learning_support (metric) | 0.5 | **variance_restricted** |
| P14 个性化教学策略选择 | formative | strategy_enactment | `edubench` | scenario_element_integration (metric) | 0.2 | **variance_restricted** |
| P14 个性化教学策略选择 | formative | strategy_enactment | `mathtutorbench_pedagogy` | Pedagogy IF | 0.5 | **variance_restricted** |
| P14 个性化教学策略选择 | formative | strategy_enactment | `mathtutorbench_socratic` | Socratic Questioning | 0.5 | **variance_restricted** |
| P14 个性化教学策略选择 | formative | strategy_enactment | `mrbench_tutor` | dimension: Providing_Guidance | 0.2 | **variance_restricted** |
| P14 个性化教学策略选择 | formative | strategy_enactment | `tutorbench` | Fair815 multimodal tutor quality | 0.2 | **variance_restricted** |
| P15 学习路径规划（知识结构层） | reflective | core | `mooccube_prereq` | chance-corrected composite (先修选择 + 学习顺序排序) | 0.8 | **single_source** |
| P16 适配性解释与反馈生成 | formative | content_feedback | `mmtutorbench` | multimodal tutor score | 0.5 | **insufficient_evidence** |
| P16 适配性解释与反馈生成 | formative | tone_support | `mrbench_tutor` | dimension: Tutor_Tone (encouraging share) | 0.2 | **insufficient_evidence** |
| P16 适配性解释与反馈生成 | formative | artifact_generation | `edubench` | TMG/PCC × clarity_concision_inspiration + scenario_element_integration (task×metric) | 0.5 | **provisional** |
| P16 适配性解释与反馈生成 | formative | content_feedback | `edubench` | higher_order_thinking_ability_development (metric) | 0.2 | **provisional** |
| P16 适配性解释与反馈生成 | formative | artifact_generation | `eduillustrate` | 8-dim 0-5 visual explanation score | 0.2 | **provisional** |
| P16 适配性解释与反馈生成 | formative | content_feedback | `mathtutorbench_pedagogy_hard` | Pedagogy IF hard | 0.2 | **provisional** |
| P16 适配性解释与反馈生成 | formative | content_feedback | `mathtutorbench_scaffolding` | Scaffolding | 0.2 | **provisional** |
| P16 适配性解释与反馈生成 | formative | content_feedback | `mathtutorbench_scaffolding_hard` | Scaffolding hard | 0.2 | **provisional** |
| P16 适配性解释与反馈生成 | formative | content_feedback | `bea2025_tutor` | dimension: Actionability | 0.2 | **variance_restricted** |
| P16 适配性解释与反馈生成 | formative | content_feedback | `edubench` | clarity_concision_inspiration (metric) | 0.2 | **variance_restricted** |
| P16 适配性解释与反馈生成 | formative | tone_support | `edubench` | motivation_guidance_positive_feedback (metric) | 0.5 | **variance_restricted** |
| P16 适配性解释与反馈生成 | formative | content_feedback | `mathtutorbench_mistake_correction` | Mistake Correction | 0.2 | **variance_restricted** |
| P16 适配性解释与反馈生成 | formative | content_feedback | `mathtutorbench_pedagogy` | Pedagogy IF | 0.2 | **variance_restricted** |
| P16 适配性解释与反馈生成 | formative | content_feedback | `mathtutorbench_socratic` | Socratic Questioning | 0.2 | **variance_restricted** |
| P16 适配性解释与反馈生成 | formative | content_feedback | `mrbench_tutor` | dimension: Actionability | 0.2 | **variance_restricted** |
| P16 适配性解释与反馈生成 | formative | content_feedback | `tutorbench` | Fair815 multimodal tutor quality | 0.5 | **variance_restricted** |
| P17 教育角色边界判断 | formative | boundary_behavior | `eduguard_adversarial` | Adversarial Safety ASR | 0.5 | **single_source** |
| P17 教育角色边界判断 | formative | boundary_behavior | `eduguard_adversarial` | Refusal quality distribution | 0.2 | **single_source** |
| P17 教育角色边界判断 | formative | safety_knowledge | `eduguard_sata` | Teaching Harm / SATA RFS | 0.2 | **single_source** |
| P17 教育角色边界判断 | formative | boundary_behavior | `mrbench_tutor` | dimension: Tutor_Tone (non-offensive) | 0.2 | **single_source** |
| P18 学生风险识别 | formative | risk_signal_recognition | `eduguard_sata` | Teaching Harm / SATA RFS | 0.2 | **variance_restricted** |
| P19 安全处置选择 | formative | adversarial_robustness | `eduguard_adversarial` | Adversarial Safety ASR | 0.5 | **insufficient_evidence** |
| P19 安全处置选择 | formative | adversarial_robustness | `eduguard_adversarial` | Refusal quality distribution | 0.8 | **insufficient_evidence** |
| P19 安全处置选择 | formative | safety_knowledge | `eduguard_sata` | Teaching Harm / SATA RFS | 0.2 | **variance_restricted** |

## 低置信附录（3 ≤ n < 5，仅呈现不评级）

| A | B | 共享 P | n | ρ |
|---|---|---|---:|---:|
| `asap_2` essay holistic QWK | `sas_bench` QWK holistic total score | P11(0.8/0.8) | 4 | -0.4 |
| `bea2025_tutor` dimension: Providing_Guidance | `mmtutorbench` multimodal tutor score | P14(0.2/0.2) | 4 | -0.4 |
| `mmtutorbench` multimodal tutor score | `mrbench_tutor` dimension: Providing_Guidance | P14(0.2/0.2) | 4 | -0.4 |
| `edubench` personalized_adaptation_learning_support (metric) | `mmtutorbench` multimodal tutor score | P14(0.5/0.2) | 4 | 0.0 |
| `eduguard_adversarial` Adversarial Safety ASR | `mrbench_tutor` dimension: Tutor_Tone (non-offensive) | P17(0.5/0.2) | 4 | — |
| `eduguard_adversarial` Refusal quality distribution | `mrbench_tutor` dimension: Tutor_Tone (non-offensive) | P17(0.2/0.2) | 4 | — |
| `mathtutorbench_scaffolding` Scaffolding | `mmtutorbench` multimodal tutor score | P14(0.5/0.2), P16(0.2/0.5) | 4 | 0.2 |
| `k12vista` official partial-credit score (per-blank 0/1 mean) | `mathtutorbench_problem_solving` Problem Solving | P05(0.2/0.2), P06(0.2/0.5) | 4 | 0.316 |
| `mathtutorbench_problem_solving` Problem Solving | `mathvista` task/question_type/answer_type accuracy | P05(0.2/0.2), P06(0.5/0.5) | 4 | 0.316 |
| `bea2025_tutor` dimension: Actionability | `mmtutorbench` multimodal tutor score | P16(0.2/0.5) | 4 | 0.4 |
| `edubench` basic_factual_accuracy (metric) | `k12vista` official partial-credit score (per-blank 0/1 mean) | P05(0.2/0.2) | 4 | 0.4 |
| `edubench` basic_factual_accuracy (metric) | `mathvista` task/question_type/answer_type accuracy | P05(0.2/0.2) | 4 | 0.4 |
| `edubench` clarity_concision_inspiration (metric) | `mmtutorbench` multimodal tutor score | P16(0.2/0.5) | 4 | 0.4 |
| `edubench` higher_order_thinking_ability_development (metric) | `mmtutorbench` multimodal tutor score | P16(0.2/0.5) | 4 | 0.4 |
| `k12vista` official partial-credit score (per-blank 0/1 mean) | `sas_bench` ECS error-cause consistency | P05(0.2/0.2), P06(0.2/0.2 异facet) | 4 | 0.4 |
| `mathvista` task/question_type/answer_type accuracy | `sas_bench` ECS error-cause consistency | P05(0.2/0.2), P06(0.5/0.2 异facet) | 4 | 0.4 |
| `edubench` scenario_element_integration (metric) | `mmtutorbench` multimodal tutor score | P14(0.2/0.2) | 4 | 0.6 |
| `k12vista` math problem-figure subset score | `olympiadbench` multimodal-subset accuracy | P03(0.5/0.2) | 4 | 0.6 |
| `k12vista` official partial-credit score (per-blank 0/1 mean) | `olympiadbench` overall/subject/language/modality accuracy | P05(0.2/0.2), P06(0.2/0.5) | 4 | 0.6 |
| `mathtutorbench_socratic` Socratic Questioning | `mmtutorbench` multimodal tutor score | P14(0.5/0.2), P16(0.2/0.5) | 4 | 0.6 |
| `mathvista` task/question_type/answer_type accuracy | `olympiadbench` overall/subject/language/modality accuracy | P05(0.2/0.2), P06(0.5/0.5) | 4 | 0.6 |
| `mmtutorbench` multimodal tutor score | `mrbench_tutor` dimension: Actionability | P16(0.5/0.2) | 4 | 0.6 |
| `edubench` domain_knowledge_accuracy (metric) | `k12vista` official partial-credit score (per-blank 0/1 mean) | P05(0.2/0.2) | 4 | 0.8 |
| `edubench` domain_knowledge_accuracy (metric) | `mathvista` task/question_type/answer_type accuracy | P05(0.2/0.2) | 4 | 0.8 |
| `k12vista` math problem-figure subset score | `mathvista` task/question_type/answer_type accuracy | P03(0.5/0.5) | 4 | 0.8 |
| `longtutor_teaching` judge dims: strategy_alignment + history_utilization (1-5) | `mmtutorbench` multimodal tutor score | P14(0.2/0.2) | 4 | 0.8 |
| `mathtutorbench_pedagogy` Pedagogy IF | `mmtutorbench` multimodal tutor score | P14(0.5/0.2), P16(0.2/0.5) | 4 | 0.8 |
| `mathtutorbench_pedagogy_hard` Pedagogy IF hard | `mmtutorbench` multimodal tutor score | P14(0.5/0.2), P16(0.2/0.5) | 4 | 0.8 |
| `mathtutorbench_scaffolding_hard` Scaffolding hard | `mmtutorbench` multimodal tutor score | P14(0.5/0.2), P16(0.2/0.5) | 4 | 0.8 |
| `mathvista` task/question_type/answer_type accuracy | `olympiadbench` multimodal-subset accuracy | P03(0.5/0.2) | 4 | 0.8 |
| `agieval` overall/task/language/question_type accuracy | `k12vista` official partial-credit score (per-blank 0/1 mean) | P05(0.2/0.2), P06(0.5/0.2) | 4 | 1.0 |
| `agieval` overall/task/language/question_type accuracy | `mathvista` task/question_type/answer_type accuracy | P05(0.2/0.2), P06(0.5/0.5) | 4 | 1.0 |
| `ceval` overall/category/subject accuracy | `k12vista` official partial-credit score (per-blank 0/1 mean) | P05(0.5/0.2), P06(0.2/0.2) | 4 | 1.0 |
| `ceval` overall/category/subject accuracy | `mathvista` task/question_type/answer_type accuracy | P05(0.5/0.2), P06(0.2/0.5) | 4 | 1.0 |
| `k12vista` official partial-credit score (per-blank 0/1 mean) | `mathvista` task/question_type/answer_type accuracy | P05(0.2/0.2), P06(0.2/0.5) | 4 | 1.0 |
| `k12vista` official partial-credit score (per-blank 0/1 mean) | `mmlu_pro` overall/category accuracy | P05(0.2/0.5), P06(0.2/0.2) | 4 | 1.0 |
| `mathtutorbench_mistake_correction` Mistake Correction | `mmtutorbench` multimodal tutor score | P16(0.2/0.5) | 4 | 1.0 |
| `mathvista` task/question_type/answer_type accuracy | `mmlu_pro` overall/category accuracy | P05(0.2/0.5), P06(0.5/0.2) | 4 | 1.0 |

## 形成型跨 facet 配对（facet_distinct_expected，信息呈现，不触发红旗）

| A | B | 共享 P | n | ρ |
|---|---|---|---:|---:|
| `mathtutorbench_scaffolding` Scaffolding | `olympiadbench` overall/subject/language/modality accuracy | P05(0.2/0.2 异facet) | 6 | -0.543 |
| `mathtutorbench_solution_correctness` Solution Correctness | `sas_bench` ECS error-cause consistency | P10(0.5/0.8 异facet) | 7 | -0.536 |
| `p07_selfcheck` two-round self-check (fix/break rate) | `p08_abstention` balanced abstention score | P08(0.2/0.8 异facet) | 7 | -0.36 |
| `bea2025_tutor` dimension: Mistake_Identification | `mathtutorbench_mistake_location` Mistake Location | P10(0.2/0.8 异facet) | 7 | -0.357 |
| `mathtutorbench_scaffolding` Scaffolding | `mrbench_tutor` dimension: Tutor_Tone (encouraging share) | P16(0.2/0.2 异facet) | 7 | -0.25 |
| `mathtutorbench_scaffolding_hard` Scaffolding hard | `mrbench_tutor` dimension: Tutor_Tone (encouraging share) | P16(0.2/0.2 异facet) | 7 | -0.25 |
| `edubench` motivation_guidance_positive_feedback (metric) | `mathtutorbench_mistake_correction` Mistake Correction | P16(0.5/0.2 异facet) | 8 | -0.214 |
| `edubench` motivation_guidance_positive_feedback (metric) | `mrbench_tutor` dimension: Actionability | P16(0.5/0.2 异facet) | 7 | -0.214 |
| `mathtutorbench_mistake_location` Mistake Location | `sas_bench` ECS error-cause consistency | P10(0.8/0.8 异facet) | 7 | -0.214 |
| `edubench` personalized_adaptation_learning_support (metric) | `pedagogy_benchmark` CDPK teaching knowledge selection | P14(0.5/0.8 异facet) | 10 | -0.212 |
| `edubench` reasoning_process_rigor (metric) | `olympiadbench` overall/subject/language/modality accuracy | P06(0.5/0.5 异facet) | 6 | -0.2 |
| `mathtutorbench_scaffolding_hard` Scaffolding hard | `olympiadbench` overall/subject/language/modality accuracy | P05(0.2/0.2 异facet) | 6 | -0.143 |
| `mathtutorbench_scaffolding_hard` Scaffolding hard | `sas_bench` ECS error-cause consistency | P05(0.2/0.2 异facet) | 7 | -0.107 |
| `edubench` basic_factual_accuracy (metric) | `mathtutorbench_scaffolding` Scaffolding | P05(0.2/0.2 异facet) | 9 | -0.1 |
| `edubench` higher_order_thinking_ability_development (metric) | `olympiadbench` overall/subject/language/modality accuracy | P06(0.2/0.5 异facet) | 6 | -0.086 |
| `mrbench_tutor` dimension: Providing_Guidance | `pedagogy_benchmark` CDPK teaching knowledge selection | P14(0.2/0.8 异facet) | 6 | -0.086 |
| `edubench` basic_factual_accuracy (metric) | `pedagogy_benchmark` SEND special education needs selection | P05(0.2/0.5 异facet) | 10 | -0.085 |
| `edubench` scenario_element_integration (metric) | `pedagogy_benchmark` CDPK teaching knowledge selection | P14(0.2/0.8 异facet) | 10 | -0.079 |
| `mrbench_judge` 8-dimension tutor response judging | `sas_bench` QWK holistic total score | P11(0.5/0.8 异facet) | 7 | -0.071 |
| `edubench` motivation_guidance_positive_feedback (metric) | `mathtutorbench_pedagogy` Pedagogy IF | P16(0.5/0.2 异facet) | 9 | 0.0 |
| `eduillustrate` 8-dim 0-5 visual explanation score | `mathtutorbench_scaffolding` Scaffolding | P16(0.2/0.2 异facet) | 5 | 0.0 |
| `mathtutorbench_mistake_location` Mistake Location | `mrbench_tutor` dimension: Mistake_Identification | P10(0.8/0.2 异facet) | 7 | 0.0 |
| `mathtutorbench_scaffolding` Scaffolding | `sas_bench` ECS error-cause consistency | P05(0.2/0.2 异facet) | 7 | 0.0 |
| `edubench` basic_factual_accuracy (metric) | `mathtutorbench_pedagogy` Pedagogy IF | P05(0.2/0.2 异facet) | 9 | 0.017 |
| `edubench` basic_factual_accuracy (metric) | `pedagogy_benchmark` CDPK teaching knowledge selection | P05(0.2/0.5 异facet) | 10 | 0.03 |
| `edubench` basic_factual_accuracy (metric) | `mathtutorbench_pedagogy_hard` Pedagogy IF hard | P05(0.2/0.2 异facet) | 9 | 0.033 |
| `longtutor_diagnosis` four-category knowledge-state diagnosis macro-F1 | `mathtutorbench_solution_correctness` Solution Correctness | P10(0.2/0.5 异facet) | 7 | 0.036 |
| `edubench` domain_knowledge_accuracy (metric) | `pedagogy_benchmark` SEND special education needs selection | P05(0.2/0.5 异facet) | 10 | 0.037 |
| `edubench` error_identification_correction_accuracy (metric) | `mathtutorbench_solution_correctness` Solution Correctness | P10(0.2/0.5 异facet) | 8 | 0.048 |
| `edubench` TMG/PCC × clarity_concision_inspiration + scenario_element_integration (task×metric) | `mathtutorbench_scaffolding_hard` Scaffolding hard | P16(0.5/0.2 异facet) | 9 | 0.05 |
| `edubench` basic_factual_accuracy (metric) | `mathtutorbench_scaffolding_hard` Scaffolding hard | P05(0.2/0.2 异facet) | 9 | 0.05 |
| `mrbench_tutor` dimension: Providing_Guidance | `pedagogy_benchmark` SEND special education needs selection | P14(0.2/0.5 异facet) | 6 | 0.058 |
| `edubench` TMG/PCC × clarity_concision_inspiration + scenario_element_integration (task×metric) | `mathtutorbench_scaffolding` Scaffolding | P16(0.5/0.2 异facet) | 9 | 0.067 |
| `edubench` motivation_guidance_positive_feedback (metric) | `mathtutorbench_scaffolding` Scaffolding | P16(0.5/0.2 异facet) | 9 | 0.067 |
| `mathtutorbench_mistake_correction` Mistake Correction | `mrbench_tutor` dimension: Tutor_Tone (encouraging share) | P16(0.2/0.2 异facet) | 7 | 0.071 |
| `mathtutorbench_pedagogy` Pedagogy IF | `sas_bench` ECS error-cause consistency | P05(0.2/0.2 异facet) | 7 | 0.071 |
| `edubench` motivation_guidance_positive_feedback (metric) | `mathtutorbench_pedagogy_hard` Pedagogy IF hard | P16(0.5/0.2 异facet) | 9 | 0.083 |
| `edubench` motivation_guidance_positive_feedback (metric) | `mathtutorbench_socratic` Socratic Questioning | P16(0.5/0.2 异facet) | 7 | 0.107 |
| `edubench` error_identification_correction_accuracy (metric) | `mathtutorbench_mistake_location` Mistake Location | P10(0.2/0.8 异facet) | 8 | 0.143 |
| `mathtutorbench_pedagogy` Pedagogy IF | `olympiadbench` overall/subject/language/modality accuracy | P05(0.2/0.2 异facet) | 6 | 0.143 |
| `mathtutorbench_pedagogy_hard` Pedagogy IF hard | `mrbench_tutor` dimension: Tutor_Tone (encouraging share) | P16(0.2/0.2 异facet) | 7 | 0.143 |
| `edubench` domain_knowledge_accuracy (metric) | `mathtutorbench_scaffolding_hard` Scaffolding hard | P05(0.2/0.2 异facet) | 9 | 0.167 |
| `edubench` error_identification_correction_accuracy (metric) | `sas_bench` CCS step scoring consistency | P10(0.2/0.2 异facet) | 9 | 0.167 |
| `edubench` domain_knowledge_accuracy (metric) | `pedagogy_benchmark` CDPK teaching knowledge selection | P05(0.2/0.5 异facet) | 10 | 0.176 |
| `edubench` scenario_element_integration (metric) | `pedagogy_benchmark` SEND special education needs selection | P14(0.2/0.5 异facet) | 10 | 0.177 |
| `mathtutorbench_socratic` Socratic Questioning | `mrbench_tutor` dimension: Tutor_Tone (encouraging share) | P16(0.2/0.2 异facet) | 7 | 0.179 |
| `edubench` reasoning_process_rigor (metric) | `mathtutorbench_problem_solving` Problem Solving | P06(0.5/0.5 异facet) | 7 | 0.18 |
| `edubench` motivation_guidance_positive_feedback (metric) | `mathtutorbench_scaffolding_hard` Scaffolding hard | P16(0.5/0.2 异facet) | 9 | 0.183 |
| `bea2025_tutor` dimension: Mistake_Identification | `sas_bench` CCS step scoring consistency | P10(0.2/0.2 异facet) | 7 | 0.214 |
| `mathtutorbench_pedagogy` Pedagogy IF | `mrbench_tutor` dimension: Tutor_Tone (encouraging share) | P16(0.2/0.2 异facet) | 7 | 0.214 |
| `bea2025_tutor` dimension: Mistake_Identification | `mathtutorbench_solution_correctness` Solution Correctness | P10(0.2/0.5 异facet) | 7 | 0.25 |
| `mathtutorbench_pedagogy_hard` Pedagogy IF hard | `sas_bench` ECS error-cause consistency | P05(0.2/0.2 异facet) | 7 | 0.25 |
| `mathtutorbench_problem_solving` Problem Solving | `pedagogy_benchmark` CDPK teaching knowledge selection | P05(0.2/0.5 异facet) | 6 | 0.29 |
| `bea2025_tutor` dimension: Providing_Guidance | `pedagogy_benchmark` CDPK teaching knowledge selection | P14(0.2/0.8 异facet) | 6 | 0.314 |
| `mathtutorbench_mistake_correction` Mistake Correction | `olympiadbench` overall/subject/language/modality accuracy | P06(0.2/0.5 异facet) | 6 | 0.314 |
| `mathtutorbench_pedagogy_hard` Pedagogy IF hard | `olympiadbench` overall/subject/language/modality accuracy | P05(0.2/0.2 异facet) | 6 | 0.314 |
| `edubench` domain_knowledge_accuracy (metric) | `mathtutorbench_pedagogy_hard` Pedagogy IF hard | P05(0.2/0.2 异facet) | 9 | 0.317 |
| `bea2025_tutor` dimension: Actionability | `edubench` motivation_guidance_positive_feedback (metric) | P16(0.2/0.5 异facet) | 7 | 0.321 |
| `edubench` TMG/PCC × clarity_concision_inspiration + scenario_element_integration (task×metric) | `mrbench_tutor` dimension: Actionability | P16(0.5/0.2 异facet) | 7 | 0.321 |
| `mathtutorbench_solution_correctness` Solution Correctness | `mrbench_tutor` dimension: Mistake_Identification | P10(0.5/0.2 异facet) | 7 | 0.321 |
| `edubench` domain_knowledge_accuracy (metric) | `mathtutorbench_scaffolding` Scaffolding | P05(0.2/0.2 异facet) | 9 | 0.333 |
| `pedagogy_benchmark` CDPK teaching knowledge selection | `sas_bench` ECS error-cause consistency | P05(0.5/0.2 异facet) | 9 | 0.333 |
| `edubench` TMG/PCC × clarity_concision_inspiration + scenario_element_integration (task×metric) | `mathtutorbench_pedagogy_hard` Pedagogy IF hard | P16(0.5/0.2 异facet) | 9 | 0.367 |
| `edubench` clarity_concision_inspiration (metric) | `mrbench_tutor` dimension: Tutor_Tone (encouraging share) | P16(0.2/0.2 异facet) | 7 | 0.393 |
| `longtutor_diagnosis` four-category knowledge-state diagnosis macro-F1 | `mathtutorbench_mistake_location` Mistake Location | P10(0.2/0.8 异facet) | 7 | 0.393 |
| `edubench` clarity_concision_inspiration (metric) | `eduillustrate` 8-dim 0-5 visual explanation score | P16(0.2/0.2 异facet) | 5 | 0.4 |
| `edubench` higher_order_thinking_ability_development (metric) | `eduillustrate` 8-dim 0-5 visual explanation score | P16(0.2/0.2 异facet) | 5 | 0.4 |
| `mathtutorbench_problem_solving` Problem Solving | `pedagogy_benchmark` SEND special education needs selection | P05(0.2/0.5 异facet) | 6 | 0.406 |
| `edubench` personalized_adaptation_learning_support (metric) | `longtutor_diagnosis` four-category knowledge-state diagnosis macro-F1 | P13(0.2/0.8 异facet) | 7 | 0.464 |
| `mathtutorbench_mistake_correction` Mistake Correction | `sas_bench` CCS step scoring consistency | P10(0.2/0.2 异facet) | 7 | 0.464 |
| `mrbench_tutor` dimension: Mistake_Identification | `sas_bench` CCS step scoring consistency | P10(0.2/0.2 异facet) | 7 | 0.464 |
| `edubench` domain_knowledge_accuracy (metric) | `mathtutorbench_pedagogy` Pedagogy IF | P05(0.2/0.2 异facet) | 9 | 0.5 |
| `eduillustrate` 8-dim 0-5 visual explanation score | `mathtutorbench_pedagogy` Pedagogy IF | P16(0.2/0.2 异facet) | 5 | 0.5 |
| `agieval` overall/task/language/question_type accuracy | `edubench` reasoning_process_rigor (metric) | P06(0.5/0.5 异facet) | 8 | 0.524 |
| `edubench` TMG/PCC × clarity_concision_inspiration + scenario_element_integration (task×metric) | `mathtutorbench_mistake_correction` Mistake Correction | P16(0.5/0.2 异facet) | 8 | 0.524 |
| `edubench` reasoning_process_rigor (metric) | `mmlu_pro` overall/category accuracy | P06(0.5/0.2 异facet) | 8 | 0.524 |
| `edubench` TMG/PCC × clarity_concision_inspiration + scenario_element_integration (task×metric) | `mathtutorbench_pedagogy` Pedagogy IF | P16(0.5/0.2 异facet) | 9 | 0.533 |
| `mathtutorbench_solution_correctness` Solution Correctness | `sas_bench` CCS step scoring consistency | P10(0.5/0.2 异facet) | 7 | 0.536 |
| `edubench` higher_order_thinking_ability_development (metric) | `mathtutorbench_problem_solving` Problem Solving | P06(0.2/0.5 异facet) | 7 | 0.541 |
| `ceval` overall/category/subject accuracy | `edubench` reasoning_process_rigor (metric) | P06(0.2/0.5 异facet) | 8 | 0.548 |
| `bea2025_tutor` dimension: Providing_Guidance | `pedagogy_benchmark` SEND special education needs selection | P14(0.2/0.5 异facet) | 6 | 0.551 |
| `bea2025_tutor` dimension: Actionability | `mrbench_tutor` dimension: Tutor_Tone (encouraging share) | P16(0.2/0.2 异facet) | 7 | 0.571 |
| `edubench` higher_order_thinking_ability_development (metric) | `mrbench_tutor` dimension: Tutor_Tone (encouraging share) | P16(0.2/0.2 异facet) | 7 | 0.571 |
| `edubench` motivation_guidance_positive_feedback (metric) | `eduillustrate` 8-dim 0-5 visual explanation score | P16(0.5/0.2 异facet) | 5 | 0.6 |
| `ceval` overall/category/subject accuracy | `mathtutorbench_scaffolding` Scaffolding | P05(0.5/0.2 异facet) | 8 | 0.619 |
| `edubench` higher_order_thinking_ability_development (metric) | `mmlu_pro` overall/category accuracy | P06(0.2/0.2 异facet) | 8 | 0.619 |
| `pedagogy_benchmark` SEND special education needs selection | `sas_bench` ECS error-cause consistency | P05(0.5/0.2 异facet) | 9 | 0.628 |
| `longtutor_diagnosis` four-category knowledge-state diagnosis macro-F1 | `pedagogy_benchmark` SEND special education needs selection | P13(0.8/0.2 异facet) | 6 | 0.638 |
| `bea2025_judge` judge labels: mistake/guidance/actionability | `sas_bench` QWK holistic total score | P11(0.5/0.8 异facet) | 7 | 0.643 |
| `edubench` TMG/PCC × clarity_concision_inspiration + scenario_element_integration (task×metric) | `mrbench_tutor` dimension: Tutor_Tone (encouraging share) | P16(0.5/0.2 异facet) | 7 | 0.643 |
| `mathtutorbench_socratic` Socratic Questioning | `pedagogy_benchmark` CDPK teaching knowledge selection | P14(0.5/0.8 异facet) | 6 | 0.657 |
| `ceval` overall/category/subject accuracy | `edubench` higher_order_thinking_ability_development (metric) | P06(0.2/0.2 异facet) | 8 | 0.69 |
| `agieval` overall/task/language/question_type accuracy | `mathtutorbench_scaffolding` Scaffolding | P05(0.2/0.2 异facet) | 8 | 0.714 |
| `ceval` overall/category/subject accuracy | `mathtutorbench_scaffolding_hard` Scaffolding hard | P05(0.5/0.2 异facet) | 8 | 0.714 |
| `longtutor_diagnosis` four-category knowledge-state diagnosis macro-F1 | `sas_bench` CCS step scoring consistency | P10(0.2/0.2 异facet) | 7 | 0.714 |
| `longtutor_teaching` judge dims: strategy_alignment + history_utilization (1-5) | `pedagogy_benchmark` CDPK teaching knowledge selection | P14(0.2/0.8 异facet) | 6 | 0.714 |
| `olympiadbench` overall/subject/language/modality accuracy | `pedagogy_benchmark` SEND special education needs selection | P05(0.2/0.5 异facet) | 5 | 0.718 |
| `longtutor_teaching` judge dims: strategy_alignment + history_utilization (1-5) | `pedagogy_benchmark` SEND special education needs selection | P14(0.2/0.5 异facet) | 6 | 0.725 |
| `mathtutorbench_scaffolding` Scaffolding | `mmlu_pro` overall/category accuracy | P05(0.2/0.5 异facet) | 8 | 0.738 |
| `agieval` overall/task/language/question_type accuracy | `pedagogy_benchmark` CDPK teaching knowledge selection | P05(0.2/0.5 异facet) | 7 | 0.75 |
| `edubench` TMG/PCC × clarity_concision_inspiration + scenario_element_integration (task×metric) | `mathtutorbench_socratic` Socratic Questioning | P16(0.5/0.2 异facet) | 7 | 0.75 |
| `mmlu_pro` overall/category accuracy | `pedagogy_benchmark` CDPK teaching knowledge selection | P05(0.5/0.5 异facet) | 7 | 0.75 |
| `mathtutorbench_socratic` Socratic Questioning | `pedagogy_benchmark` SEND special education needs selection | P14(0.5/0.5 异facet) | 6 | 0.754 |
| `agieval` overall/task/language/question_type accuracy | `edubench` higher_order_thinking_ability_development (metric) | P06(0.5/0.2 异facet) | 8 | 0.762 |
| `agieval` overall/task/language/question_type accuracy | `mathtutorbench_scaffolding_hard` Scaffolding hard | P05(0.2/0.2 异facet) | 8 | 0.786 |
| `eduillustrate` 8-dim 0-5 visual explanation score | `mathtutorbench_pedagogy_hard` Pedagogy IF hard | P16(0.2/0.2 异facet) | 5 | 0.8 |
| `eduillustrate` 8-dim 0-5 visual explanation score | `mathtutorbench_scaffolding_hard` Scaffolding hard | P16(0.2/0.2 异facet) | 5 | 0.8 |
| `olympiadbench` overall/subject/language/modality accuracy | `pedagogy_benchmark` CDPK teaching knowledge selection | P05(0.2/0.5 异facet) | 5 | 0.8 |
| `ceval` overall/category/subject accuracy | `mathtutorbench_mistake_correction` Mistake Correction | P06(0.2/0.2 异facet) | 8 | 0.81 |
| `mathtutorbench_mistake_correction` Mistake Correction | `mmlu_pro` overall/category accuracy | P06(0.2/0.2 异facet) | 8 | 0.81 |
| `ceval` overall/category/subject accuracy | `pedagogy_benchmark` CDPK teaching knowledge selection | P05(0.5/0.5 异facet) | 7 | 0.821 |
| `agieval` overall/task/language/question_type accuracy | `pedagogy_benchmark` SEND special education needs selection | P05(0.2/0.5 异facet) | 7 | 0.829 |
| `ceval` overall/category/subject accuracy | `pedagogy_benchmark` SEND special education needs selection | P05(0.5/0.5 异facet) | 7 | 0.865 |
| `agieval` overall/task/language/question_type accuracy | `mathtutorbench_pedagogy_hard` Pedagogy IF hard | P05(0.2/0.2 异facet) | 8 | 0.881 |
| `mathtutorbench_pedagogy_hard` Pedagogy IF hard | `mmlu_pro` overall/category accuracy | P05(0.2/0.5 异facet) | 8 | 0.881 |
| `mathtutorbench_scaffolding_hard` Scaffolding hard | `mmlu_pro` overall/category accuracy | P05(0.2/0.5 异facet) | 8 | 0.881 |
| `mmlu_pro` overall/category accuracy | `pedagogy_benchmark` SEND special education needs selection | P05(0.5/0.5 异facet) | 7 | 0.901 |
| `agieval` overall/task/language/question_type accuracy | `mathtutorbench_mistake_correction` Mistake Correction | P06(0.5/0.2 异facet) | 8 | 0.905 |
| `agieval` overall/task/language/question_type accuracy | `mathtutorbench_pedagogy` Pedagogy IF | P05(0.2/0.2 异facet) | 8 | 0.905 |
| `ceval` overall/category/subject accuracy | `mathtutorbench_pedagogy` Pedagogy IF | P05(0.5/0.2 异facet) | 8 | 0.905 |
| `mathtutorbench_pedagogy` Pedagogy IF | `mmlu_pro` overall/category accuracy | P05(0.2/0.5 异facet) | 8 | 0.905 |
| `bea2025_tutor` dimension: Actionability | `edubench` TMG/PCC × clarity_concision_inspiration + scenario_element_integration (task×metric) | P16(0.2/0.5 异facet) | 7 | 0.929 |
| `ceval` overall/category/subject accuracy | `mathtutorbench_pedagogy_hard` Pedagogy IF hard | P05(0.5/0.2 异facet) | 8 | 0.929 |

## 局限

- n=5-8 的置信区间很宽，评级以红旗探测为目的，不是效应量精确估计；补模型数（M2.5）是第一优先级。
- 偏相关控制的'综合分'由同一批证据构造，存在轻度内生性；仅作敏感性检查。
- 配对之间共享格子、非独立，区分效度的 permutation p 只作参考。