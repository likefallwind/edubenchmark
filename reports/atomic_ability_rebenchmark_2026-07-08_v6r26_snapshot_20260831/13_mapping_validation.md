# 映射效度检查报告（13 号）

生成脚本：`scripts/build_mapping_validation.py`（幂等）；测量模型：`data/mapping_measurement_model_v6.json`（adjudicated）。
规则见 `doc/mapping_validation_plan_2026-07-11.md` §2；ρ 一律与 n、90% CI 同格呈现，n<5 的配对只进低置信附录。

覆盖缺口（无任何 benchmark 映射，不参与本报告分析）：P09 工具使用与长程智能体执行、P20 学术诚信与作答真实性判定。

## Phase 0：天花板/方差受限名单

共 35 / 62 个有证据格子被标记 `variance_restricted`（mean≥8.5 或 n≥4 且 SD<0.5）。这些格子参与的配对**不进入裁决**；优先动作是上难度/换切分，不是改映射。

| Benchmark | Subdimension | n | mean | SD | 标记 |
|---|---|---:|---:|---:|---|
| `mrbench_tutor` | dimension: Tutor_Tone (non-offensive) | 5 | 10.0 | 0.0 | ceiling, low_variance |
| `mathtutorbench_problem_solving` | Problem Solving | 6 | 9.683 | 0.105 | ceiling, low_variance |
| `longtutor_evidence` | Information Extraction accuracy | 6 | 9.582 | 0.136 | ceiling, low_variance |
| `bea2025_tutor` | dimension: Providing_Guidance | 5 | 9.56 | 0.253 | ceiling, low_variance |
| `bea2025_tutor` | dimension: Actionability | 5 | 9.48 | 0.421 | ceiling, low_variance |
| `edubench` | QG × domain_knowledge_accuracy + basic_factual_accuracy (task×metric) | 13 | 9.23 | 0.472 | ceiling, low_variance |
| `mrbench_tutor` | dimension: Mistake_Identification | 5 | 9.215 | 0.378 | ceiling, low_variance |
| `mrbench_tutor` | dimension: Actionability | 5 | 9.17 | 0.605 | ceiling |
| `ifeval` | prompt-level strict accuracy | 6 | 9.071 | 0.201 | ceiling, low_variance |
| `edubench` | basic_factual_accuracy (metric) | 13 | 9.07 | 0.434 | ceiling, low_variance |
| `mrbench_tutor` | dimension: Providing_Guidance | 5 | 9.069 | 0.188 | ceiling, low_variance |
| `mathtutorbench_mistake_correction` | Mistake Correction | 7 | 9.043 | 0.327 | ceiling, low_variance |
| `p08_abstention` | balanced abstention score | 6 | 8.97 | 0.26 | ceiling, low_variance |
| `ceval` | overall/category/subject accuracy | 8 | 8.967 | 0.486 | ceiling, low_variance |
| `mrbench_tutor` | dimension: Tutor_Tone (encouraging share) | 5 | 8.929 | 1.31 | ceiling |
| `agieval` | overall/task/language/question_type accuracy | 7 | 8.742 | 0.418 | ceiling, low_variance |
| `mathtutorbench_solution_correctness` | Solution Correctness | 7 | 8.719 | 0.143 | ceiling, low_variance |
| `edubench` | domain_knowledge_accuracy (metric) | 13 | 8.661 | 0.687 | ceiling |
| `bea2025_tutor` | dimension: Mistake_Identification | 5 | 8.593 | 0.167 | ceiling, low_variance |
| `mathvista` | task/question_type/answer_type accuracy | 3 | 8.54 | 0.288 | ceiling |
| `mmlu_pro` | overall/category accuracy | 7 | 8.509 | 0.317 | ceiling, low_variance |
| `edubench` | clarity_concision_inspiration (metric) | 13 | 8.332 | 0.447 | low_variance |
| `sas_bench` | QWK holistic total score | 9 | 8.264 | 0.256 | low_variance |
| `mathtutorbench_pedagogy` | Pedagogy IF | 8 | 8.204 | 0.476 | low_variance |
| `edubench` | QG × clarity_concision_inspiration + scenario_element_integration (task×metric) | 13 | 8.128 | 0.416 | low_variance |
| `mathtutorbench_mistake_location` | Mistake Location | 7 | 7.688 | 0.143 | low_variance |
| `edubench` | scenario_element_integration (metric) | 13 | 7.658 | 0.395 | low_variance |
| `sas_bench` | CCS step scoring consistency | 9 | 7.606 | 0.271 | low_variance |
| `eduguard_sata` | Teaching Harm / SATA RFS | 9 | 7.483 | 0.241 | low_variance |
| `olympiadbench` | overall/subject/language/modality accuracy | 5 | 7.141 | 0.486 | low_variance |
| `edubench` | motivation_guidance_positive_feedback (metric) | 13 | 6.437 | 0.27 | low_variance |
| `edubench` | personalized_adaptation_learning_support (metric) | 13 | 6.358 | 0.343 | low_variance |
| `tutorbench` | Fair815 multimodal tutor quality | 6 | 5.478 | 0.25 | low_variance |
| `p07_selfcheck` | two-round self-check (fix/break rate) | 6 | 5.228 | 0.25 | low_variance |
| `mathtutorbench_socratic` | Socratic Questioning | 6 | 2.728 | 0.344 | low_variance |

## 红旗配对（flagged：同 P 预期收敛却 ρ<0，n≥6）

每条 flagged 需人工裁决：改权重 / 拆 facet / 转裁判治理（计划 §2.6）。

| A | B | 共享 P（权重A/B） | n | ρ | 偏ρ(控综合分) | perm p | 90% CI | 评级 |
|---|---|---|---:|---:|---:|---:|---|---|
| `edubench` error_identification_correction_accuracy (metric) | `sas_bench` ECS error-cause consistency | P10(0.2/0.8) | 8 | -0.238 | -0.225 | 0.5821 | [-0.842, 0.538] | flagged |
| `edubench` error_identification_correction_accuracy (metric) | `longtutor_diagnosis` four-category knowledge-state diagnosis macro-F1 | P10(0.2/0.2) | 6 | -0.2 | -0.157 | 0.7139 | [-1.0, 0.636] | flagged |
| `edubench` reasoning_process_rigor (metric) | `sas_bench` ECS error-cause consistency | P06(0.5/0.2) | 8 | -0.048 | -0.089 | 0.9349 | [-0.747, 0.722] | flagged |

## 观察带（watch：0≤ρ<0.2 且 n≥8）

| A | B | 共享 P（权重A/B） | n | ρ | 偏ρ(控综合分) | perm p | 90% CI | 评级 |
|---|---|---|---:|---:|---:|---:|---|---|
| `edubench` higher_order_thinking_ability_development (metric) | `sas_bench` ECS error-cause consistency | P06(0.2/0.2) | 8 | 0.167 | 0.119 | 0.7033 | [-0.544, 0.923] | watch |

## 已验证配对（validated：ρ≥0.5 且 CI 下界>0）

| A | B | 共享 P（权重A/B） | n | ρ | 偏ρ(控综合分) | perm p | 90% CI | 评级 |
|---|---|---|---:|---:|---:|---:|---|---|
| `mathtutorbench_pedagogy_hard` Pedagogy IF hard | `pedagogy_benchmark` SEND special education needs selection | P05(0.2/0.5), P14(0.5/0.5 异facet) | 6 | 1.0 | 1.0 | 0.0028 | [1.0, 1.0] | validated |
| `longtutor_diagnosis` four-category knowledge-state diagnosis macro-F1 | `sas_bench` ECS error-cause consistency | P10(0.2/0.8) | 6 | 0.771 | 0.825 | 0.1028 | [0.091, 1.0] | validated |
| `mathtutorbench_scaffolding` Scaffolding | `pedagogy_benchmark` SEND special education needs selection | P05(0.2/0.5), P14(0.5/0.5 异facet) | 6 | 0.771 | 0.908 | 0.1028 | [0.091, 1.0] | validated |
| `mathtutorbench_scaffolding_hard` Scaffolding hard | `pedagogy_benchmark` SEND special education needs selection | P05(0.2/0.5), P14(0.5/0.5 异facet) | 6 | 0.771 | 0.908 | 0.1028 | [0.091, 1.0] | validated |
| `edubench` higher_order_thinking_ability_development (metric) | `mathtutorbench_pedagogy_hard` Pedagogy IF hard | P16(0.2/0.2) | 8 | 0.69 | 0.61 | 0.0694 | [0.089, 1.0] | validated |

## 待定配对（provisional）

| A | B | 共享 P（权重A/B） | n | ρ | 偏ρ(控综合分) | perm p | 90% CI | 评级 |
|---|---|---|---:|---:|---:|---:|---|---|
| `longtutor_teaching` judge dims: strategy_alignment + history_utilization (1-5) | `mathtutorbench_scaffolding` Scaffolding | P14(0.2/0.5) | 6 | 0.143 | 0.306 | 0.8028 | [-0.939, 0.935] | provisional |
| `longtutor_teaching` judge dims: strategy_alignment + history_utilization (1-5) | `mathtutorbench_scaffolding_hard` Scaffolding hard | P14(0.2/0.5) | 6 | 0.143 | 0.306 | 0.8028 | [-1.0, 0.939] | provisional |
| `mathtutorbench_scaffolding` Scaffolding | `pedagogy_benchmark` CDPK teaching knowledge selection | P05(0.2/0.5), P14(0.5/0.8 异facet) | 6 | 0.257 | 0.217 | 0.6583 | [-0.6, 0.935] | provisional |
| `mathtutorbench_scaffolding_hard` Scaffolding hard | `pedagogy_benchmark` CDPK teaching knowledge selection | P05(0.2/0.5), P14(0.5/0.8 异facet) | 6 | 0.257 | 0.217 | 0.6583 | [-0.636, 0.939] | provisional |
| `longtutor_teaching` judge dims: strategy_alignment + history_utilization (1-5) | `mathtutorbench_pedagogy_hard` Pedagogy IF hard | P14(0.2/0.5) | 6 | 0.371 | 0.583 | 0.4972 | [-0.636, 1.0] | provisional |
| `bea2025_judge` judge labels: mistake/guidance/actionability | `mrbench_judge` 8-dimension tutor response judging | P11(0.5/0.5) | 8 | 0.429 | 0.03 | 0.2992 | [-0.367, 1.0] | provisional |
| `edubench` higher_order_thinking_ability_development (metric) | `mathtutorbench_scaffolding_hard` Scaffolding hard | P16(0.2/0.2) | 8 | 0.5 | 0.24 | 0.2162 | [-0.211, 0.923] | provisional |
| `edubench` higher_order_thinking_ability_development (metric) | `mathtutorbench_scaffolding` Scaffolding | P16(0.2/0.2) | 8 | 0.571 | 0.365 | 0.1511 | [-0.094, 0.926] | provisional |
| `mathtutorbench_pedagogy_hard` Pedagogy IF hard | `pedagogy_benchmark` CDPK teaching knowledge selection | P05(0.2/0.5), P14(0.5/0.8 异facet) | 6 | 0.714 | 0.531 | 0.1361 | [0.0, 1.0] | provisional |

## 因方差受限不裁决的配对

任一侧格子 variance_restricted；其 ρ 不作为构念证据。

| A | B | 共享 P（权重A/B） | n | ρ | 偏ρ(控综合分) | perm p | 90% CI | 评级 |
|---|---|---|---:|---:|---:|---:|---|---|
| `edubench` error_identification_correction_accuracy (metric) | `mrbench_tutor` dimension: Mistake_Identification | P10(0.2/0.2) | 5 | -0.7 | -0.704 | 0.2333 | [-1.0, 0.667] | variance_restricted |
| `edubench` basic_factual_accuracy (metric) | `olympiadbench` overall/subject/language/modality accuracy | P05(0.2/0.2) | 5 | -0.6 | -0.794 | 0.35 | [-1.0, 1.0] | variance_restricted |
| `edubench` scenario_element_integration (metric) | `longtutor_teaching` judge dims: strategy_alignment + history_utilization (1-5) | P14(0.2/0.2) | 6 | -0.6 | -0.589 | 0.2417 | [-1.0, 0.091] | variance_restricted |
| `longtutor_evidence` Hallucination Check accuracy | `mathtutorbench_mistake_location` Mistake Location | P02(0.8/0.2) | 6 | -0.6 | -0.724 | 0.2417 | [-1.0, 0.394] | variance_restricted |
| `edubench` personalized_adaptation_learning_support (metric) | `longtutor_teaching` judge dims: strategy_alignment + history_utilization (1-5) | P14(0.5/0.2) | 6 | -0.543 | -0.539 | 0.2972 | [-1.0, 0.091] | variance_restricted |
| `edubench` personalized_adaptation_learning_support (metric) | `pedagogy_benchmark` SEND special education needs selection | P13(0.2/0.2), P14(0.5/0.5 异facet) | 9 | -0.527 | -0.36 | 0.1496 | [-0.893, 0.165] | variance_restricted |
| `bea2025_tutor` dimension: Providing_Guidance | `longtutor_teaching` judge dims: strategy_alignment + history_utilization (1-5) | P14(0.2/0.2) | 5 | -0.5 | -0.577 | 0.45 | [-1.0, 1.0] | variance_restricted |
| `bea2025_tutor` dimension: Mistake_Identification | `mathtutorbench_mistake_correction` Mistake Correction | P10(0.2/0.2) | 5 | -0.3 | -0.452 | 0.6833 | [-1.0, 1.0] | variance_restricted |
| `bea2025_tutor` dimension: Mistake_Identification | `mrbench_tutor` dimension: Mistake_Identification | P10(0.2/0.2) | 5 | -0.3 | -0.302 | 0.6833 | [-1.0, 1.0] | variance_restricted |
| `edubench` domain_knowledge_accuracy (metric) | `olympiadbench` overall/subject/language/modality accuracy | P05(0.2/0.2) | 5 | -0.3 | — | 0.6833 | [-1.0, 1.0] | variance_restricted |
| `mrbench_judge` 8-dimension tutor response judging | `sas_bench` CCS step scoring consistency | P11(0.5/0.5) | 6 | -0.257 | -0.784 | 0.6583 | [-1.0, 0.818] | variance_restricted |
| `edubench` basic_factual_accuracy (metric) | `sas_bench` ECS error-cause consistency | P05(0.2/0.2) | 8 | -0.238 | -0.281 | 0.5821 | [-0.927, 0.615] | variance_restricted |
| `edubench` personalized_adaptation_learning_support (metric) | `mrbench_tutor` dimension: Providing_Guidance | P14(0.5/0.2) | 5 | -0.2 | -0.612 | 0.7833 | [-1.0, 0.875] | variance_restricted |
| `edubench` scenario_element_integration (metric) | `mathtutorbench_socratic` Socratic Questioning | P14(0.2/0.5) | 6 | -0.2 | -0.575 | 0.7139 | [-0.939, 1.0] | variance_restricted |
| `mathtutorbench_mistake_correction` Mistake Correction | `sas_bench` ECS error-cause consistency | P06(0.2/0.2), P10(0.2/0.8) | 6 | -0.2 | -0.151 | 0.7139 | [-1.0, 0.636] | variance_restricted |
| `mmlu_pro` overall/category accuracy | `olympiadbench` overall/subject/language/modality accuracy | P05(0.5/0.2), P06(0.2/0.5) | 5 | -0.2 | 0.015 | 0.7833 | [-1.0, 0.875] | variance_restricted |
| `mathtutorbench_solution_correctness` Solution Correctness | `p07_selfcheck` two-round self-check (fix/break rate) | P07(0.2/0.8) | 6 | -0.143 | -0.384 | 0.8028 | [-0.92, 0.806] | variance_restricted |
| `edubench` domain_knowledge_accuracy (metric) | `sas_bench` ECS error-cause consistency | P05(0.2/0.2) | 8 | -0.119 | -0.19 | 0.793 | [-0.842, 0.772] | variance_restricted |
| `bea2025_tutor` dimension: Actionability | `mathtutorbench_mistake_correction` Mistake Correction | P16(0.2/0.2) | 5 | -0.1 | -0.367 | 0.95 | [-1.0, 1.0] | variance_restricted |
| `bea2025_tutor` dimension: Actionability | `mathtutorbench_scaffolding` Scaffolding | P16(0.2/0.2) | 5 | -0.1 | -0.89 | 0.95 | [-1.0, 1.0] | variance_restricted |
| `bea2025_tutor` dimension: Actionability | `mathtutorbench_scaffolding_hard` Scaffolding hard | P16(0.2/0.2) | 5 | -0.1 | -0.89 | 0.95 | [-1.0, 1.0] | variance_restricted |
| `bea2025_tutor` dimension: Actionability | `mathtutorbench_socratic` Socratic Questioning | P16(0.2/0.2) | 5 | -0.1 | -0.89 | 0.95 | [-1.0, 1.0] | variance_restricted |
| `bea2025_tutor` dimension: Providing_Guidance | `edubench` personalized_adaptation_learning_support (metric) | P14(0.2/0.5) | 5 | -0.1 | -0.236 | 0.95 | [-1.0, 1.0] | variance_restricted |
| `edubench` scenario_element_integration (metric) | `mrbench_tutor` dimension: Providing_Guidance | P14(0.2/0.2) | 5 | -0.1 | -0.764 | 0.95 | [-1.0, 1.0] | variance_restricted |
| `mathtutorbench_problem_solving` Problem Solving | `sas_bench` ECS error-cause consistency | P05(0.2/0.2), P06(0.5/0.2 异facet) | 5 | -0.1 | -0.034 | 0.95 | [-1.0, 1.0] | variance_restricted |
| `edubench` personalized_adaptation_learning_support (metric) | `mathtutorbench_socratic` Socratic Questioning | P14(0.5/0.5) | 6 | -0.086 | -0.281 | 0.9194 | [-1.0, 0.8] | variance_restricted |
| `edubench` error_identification_correction_accuracy (metric) | `mathtutorbench_mistake_correction` Mistake Correction | P10(0.2/0.2) | 7 | -0.071 | 0.109 | 0.9063 | [-0.808, 0.852] | variance_restricted |
| `edubench` clarity_concision_inspiration (metric) | `mathtutorbench_scaffolding_hard` Scaffolding hard | P16(0.2/0.2) | 8 | -0.048 | -0.679 | 0.9349 | [-0.823, 0.671] | variance_restricted |
| `edubench` personalized_adaptation_learning_support (metric) | `mathtutorbench_pedagogy_hard` Pedagogy IF hard | P14(0.5/0.5) | 8 | -0.048 | -0.069 | 0.9349 | [-0.644, 0.707] | variance_restricted |
| `mmlu_pro` overall/category accuracy | `sas_bench` ECS error-cause consistency | P05(0.5/0.2), P06(0.2/0.2 异facet) | 6 | -0.029 | 0.088 | 1.0 | [-0.92, 1.0] | variance_restricted |
| `edubench` personalized_adaptation_learning_support (metric) | `mathtutorbench_pedagogy` Pedagogy IF | P14(0.5/0.5) | 8 | -0.024 | -0.038 | 0.9768 | [-0.646, 0.605] | variance_restricted |
| `edubench` clarity_concision_inspiration (metric) | `mathtutorbench_scaffolding` Scaffolding | P16(0.2/0.2) | 8 | 0.0 | -0.637 | 1.0 | [-0.8, 0.747] | variance_restricted |
| `edubench` clarity_concision_inspiration (metric) | `mathtutorbench_pedagogy_hard` Pedagogy IF hard | P16(0.2/0.2) | 8 | 0.024 | -0.637 | 0.9768 | [-0.797, 0.747] | variance_restricted |
| `agieval` overall/task/language/question_type accuracy | `sas_bench` ECS error-cause consistency | P05(0.2/0.2), P06(0.5/0.2 异facet) | 6 | 0.029 | 0.164 | 1.0 | [-0.935, 0.636] | variance_restricted |
| `longtutor_evidence` Hallucination Check accuracy | `sas_bench` CCS step scoring consistency | P02(0.8/0.2) | 6 | 0.029 | 0.1 | 1.0 | [-1.0, 0.818] | variance_restricted |
| `edubench` clarity_concision_inspiration (metric) | `mathtutorbench_mistake_correction` Mistake Correction | P16(0.2/0.2) | 7 | 0.036 | -0.477 | 0.9635 | [-0.75, 0.765] | variance_restricted |
| `edubench` clarity_concision_inspiration (metric) | `mathtutorbench_pedagogy` Pedagogy IF | P16(0.2/0.2) | 8 | 0.048 | -0.477 | 0.9349 | [-0.8, 0.737] | variance_restricted |
| `agieval` overall/task/language/question_type accuracy | `edubench` basic_factual_accuracy (metric) | P05(0.2/0.2) | 7 | 0.071 | -0.471 | 0.9063 | [-0.667, 0.765] | variance_restricted |
| `ceval` overall/category/subject accuracy | `edubench` basic_factual_accuracy (metric) | P05(0.5/0.2) | 7 | 0.071 | -0.339 | 0.9063 | [-0.68, 0.778] | variance_restricted |
| `bea2025_tutor` dimension: Providing_Guidance | `mrbench_tutor` dimension: Providing_Guidance | P14(0.2/0.2) | 5 | 0.1 | -0.577 | 0.95 | [-1.0, 0.875] | variance_restricted |
| `edubench` motivation_guidance_positive_feedback (metric) | `mrbench_tutor` dimension: Tutor_Tone (encouraging share) | P16(0.5/0.2) | 5 | 0.1 | -0.275 | 0.95 | [-1.0, 1.0] | variance_restricted |
| `edubench` scenario_element_integration (metric) | `mathtutorbench_scaffolding_hard` Scaffolding hard | P14(0.2/0.5) | 8 | 0.119 | 0.013 | 0.793 | [-0.615, 0.899] | variance_restricted |
| `edubench` personalized_adaptation_learning_support (metric) | `mathtutorbench_scaffolding` Scaffolding | P14(0.5/0.5) | 8 | 0.167 | 0.177 | 0.7033 | [-0.659, 0.923] | variance_restricted |
| `edubench` scenario_element_integration (metric) | `mathtutorbench_scaffolding` Scaffolding | P14(0.2/0.5) | 8 | 0.19 | 0.09 | 0.6646 | [-0.589, 0.926] | variance_restricted |
| `bea2025_tutor` dimension: Mistake_Identification | `edubench` error_identification_correction_accuracy (metric) | P10(0.2/0.2) | 5 | 0.2 | 0.212 | 0.7833 | [-0.875, 1.0] | variance_restricted |
| `longtutor_diagnosis` four-category knowledge-state diagnosis macro-F1 | `mrbench_tutor` dimension: Mistake_Identification | P10(0.2/0.2) | 5 | 0.2 | 0.25 | 0.7833 | [-0.875, 1.0] | variance_restricted |
| `longtutor_teaching` judge dims: strategy_alignment + history_utilization (1-5) | `mathtutorbench_socratic` Socratic Questioning | P14(0.2/0.5) | 6 | 0.2 | 0.667 | 0.7139 | [-1.0, 0.939] | variance_restricted |
| `edubench` clarity_concision_inspiration (metric) | `mrbench_tutor` dimension: Actionability | P16(0.2/0.2) | 5 | 0.205 | -0.629 | 0.7667 | [-1.0, 1.0] | variance_restricted |
| `edubench` personalized_adaptation_learning_support (metric) | `mathtutorbench_scaffolding_hard` Scaffolding hard | P14(0.5/0.5) | 8 | 0.238 | 0.255 | 0.5821 | [-0.615, 0.925] | variance_restricted |
| `longtutor_diagnosis` four-category knowledge-state diagnosis macro-F1 | `mathtutorbench_mistake_correction` Mistake Correction | P10(0.2/0.2) | 6 | 0.257 | 0.187 | 0.6583 | [-0.6, 0.92] | variance_restricted |
| `longtutor_teaching` judge dims: strategy_alignment + history_utilization (1-5) | `mathtutorbench_pedagogy` Pedagogy IF | P14(0.2/0.5) | 6 | 0.257 | 0.66 | 0.6583 | [-0.818, 1.0] | variance_restricted |
| `edubench` basic_factual_accuracy (metric) | `mmlu_pro` overall/category accuracy | P05(0.2/0.5) | 7 | 0.286 | -0.094 | 0.556 | [-0.765, 0.882] | variance_restricted |
| `agieval` overall/task/language/question_type accuracy | `olympiadbench` overall/subject/language/modality accuracy | P05(0.2/0.2), P06(0.5/0.5) | 5 | 0.3 | 0.943 | 0.6833 | [-1.0, 1.0] | variance_restricted |
| `bea2025_tutor` dimension: Mistake_Identification | `longtutor_diagnosis` four-category knowledge-state diagnosis macro-F1 | P10(0.2/0.2) | 5 | 0.3 | 0.302 | 0.6833 | [-1.0, 1.0] | variance_restricted |
| `bea2025_tutor` dimension: Providing_Guidance | `edubench` scenario_element_integration (metric) | P14(0.2/0.2) | 5 | 0.3 | 0.126 | 0.6833 | [-1.0, 1.0] | variance_restricted |
| `bea2025_tutor` dimension: Providing_Guidance | `mathtutorbench_pedagogy` Pedagogy IF | P14(0.2/0.5) | 5 | 0.3 | -0.397 | 0.6833 | [-1.0, 1.0] | variance_restricted |
| `bea2025_tutor` dimension: Providing_Guidance | `mathtutorbench_pedagogy_hard` Pedagogy IF hard | P14(0.2/0.5) | 5 | 0.3 | -0.397 | 0.6833 | [-1.0, 1.0] | variance_restricted |
| `bea2025_tutor` dimension: Providing_Guidance | `mathtutorbench_scaffolding` Scaffolding | P14(0.2/0.5) | 5 | 0.3 | -0.397 | 0.6833 | [-0.875, 1.0] | variance_restricted |
| `bea2025_tutor` dimension: Providing_Guidance | `mathtutorbench_scaffolding_hard` Scaffolding hard | P14(0.2/0.5) | 5 | 0.3 | -0.397 | 0.6833 | [-0.875, 1.0] | variance_restricted |
| `bea2025_tutor` dimension: Providing_Guidance | `mathtutorbench_socratic` Socratic Questioning | P14(0.2/0.5) | 5 | 0.3 | -0.397 | 0.6833 | [-0.875, 1.0] | variance_restricted |
| `mrbench_tutor` dimension: Mistake_Identification | `sas_bench` ECS error-cause consistency | P10(0.2/0.8) | 5 | 0.3 | 0.302 | 0.6833 | [-0.875, 1.0] | variance_restricted |
| `olympiadbench` overall/subject/language/modality accuracy | `sas_bench` ECS error-cause consistency | P05(0.2/0.2), P06(0.5/0.2 异facet) | 5 | 0.3 | 0.231 | 0.6833 | [-1.0, 1.0] | variance_restricted |
| `ceval` overall/category/subject accuracy | `sas_bench` ECS error-cause consistency | P05(0.5/0.2), P06(0.2/0.2 异facet) | 6 | 0.314 | 0.471 | 0.5639 | [-0.636, 0.939] | variance_restricted |
| `p07_selfcheck` two-round self-check (fix/break rate) | `p08_calibration` calibration composite (CWR/AUROC) | P07(0.8/0.2), P08(0.2/0.8) | 6 | 0.314 | 0.234 | 0.5639 | [-0.6, 1.0] | variance_restricted |
| `longtutor_evidence` Information Extraction accuracy | `mathtutorbench_mistake_location` Mistake Location | P02(0.8/0.2) | 6 | 0.348 | 0.339 | 0.5111 | [-0.6, 1.0] | variance_restricted |
| `bea2025_tutor` dimension: Actionability | `mrbench_tutor` dimension: Actionability | P16(0.2/0.2) | 5 | 0.359 | 0.207 | 0.6333 | [-0.913, 1.0] | variance_restricted |
| `edubench` clarity_concision_inspiration (metric) | `mathtutorbench_socratic` Socratic Questioning | P16(0.2/0.2) | 6 | 0.371 | -0.752 | 0.4972 | [-0.636, 1.0] | variance_restricted |
| `edubench` scenario_element_integration (metric) | `mathtutorbench_pedagogy` Pedagogy IF | P14(0.2/0.5) | 8 | 0.381 | 0.318 | 0.3599 | [-0.415, 0.854] | variance_restricted |
| `bea2025_tutor` dimension: Actionability | `edubench` higher_order_thinking_ability_development (metric) | P16(0.2/0.2) | 5 | 0.4 | 0.313 | 0.5167 | [-0.667, 1.0] | variance_restricted |
| `bea2025_tutor` dimension: Actionability | `mathtutorbench_pedagogy` Pedagogy IF | P16(0.2/0.2) | 5 | 0.4 | 0.313 | 0.5167 | [-0.875, 1.0] | variance_restricted |
| `bea2025_tutor` dimension: Actionability | `mathtutorbench_pedagogy_hard` Pedagogy IF hard | P16(0.2/0.2) | 5 | 0.4 | 0.313 | 0.5167 | [-0.667, 1.0] | variance_restricted |
| `edubench` scenario_element_integration (metric) | `mathtutorbench_pedagogy_hard` Pedagogy IF hard | P14(0.2/0.5) | 8 | 0.405 | 0.34 | 0.3268 | [-0.392, 0.975] | variance_restricted |
| `ceval` overall/category/subject accuracy | `edubench` domain_knowledge_accuracy (metric) | P05(0.5/0.2) | 7 | 0.464 | -0.037 | 0.3024 | [-0.321, 1.0] | variance_restricted |
| `mathtutorbench_solution_correctness` Solution Correctness | `p08_calibration` calibration composite (CWR/AUROC) | P07(0.2/0.2) | 6 | 0.486 | 0.316 | 0.3556 | [-0.5, 1.0] | variance_restricted |
| `bea2025_tutor` dimension: Actionability | `edubench` clarity_concision_inspiration (metric) | P16(0.2/0.2) | 5 | 0.5 | 0.419 | 0.45 | [-0.667, 1.0] | variance_restricted |
| `bea2025_tutor` dimension: Mistake_Identification | `sas_bench` ECS error-cause consistency | P10(0.2/0.8) | 5 | 0.5 | 0.515 | 0.45 | [-1.0, 1.0] | variance_restricted |
| `edubench` reasoning_process_rigor (metric) | `mathtutorbench_mistake_correction` Mistake Correction | P06(0.5/0.2) | 7 | 0.536 | 0.234 | 0.2357 | [-0.261, 1.0] | variance_restricted |
| `agieval` overall/task/language/question_type accuracy | `edubench` domain_knowledge_accuracy (metric) | P05(0.2/0.2) | 7 | 0.571 | -0.007 | 0.2 | [-0.067, 1.0] | variance_restricted |
| `ceval` overall/category/subject accuracy | `mathtutorbench_problem_solving` Problem Solving | P05(0.5/0.2), P06(0.2/0.5) | 6 | 0.6 | -0.101 | 0.2417 | [0.0, 1.0] | variance_restricted |
| `ceval` overall/category/subject accuracy | `olympiadbench` overall/subject/language/modality accuracy | P05(0.5/0.2), P06(0.2/0.5) | 5 | 0.6 | 0.908 | 0.35 | [-1.0, 1.0] | variance_restricted |
| `edubench` basic_factual_accuracy (metric) | `mathtutorbench_problem_solving` Problem Solving | P05(0.2/0.2) | 6 | 0.6 | 0.565 | 0.2417 | [-0.2, 1.0] | variance_restricted |
| `longtutor_teaching` judge dims: strategy_alignment + history_utilization (1-5) | `mrbench_tutor` dimension: Providing_Guidance | P14(0.2/0.2) | 5 | 0.6 | 1.0 | 0.35 | [-1.0, 1.0] | variance_restricted |
| `mathtutorbench_pedagogy` Pedagogy IF | `pedagogy_benchmark` CDPK teaching knowledge selection | P05(0.2/0.5), P14(0.5/0.8 异facet) | 6 | 0.6 | 0.375 | 0.2417 | [-0.394, 1.0] | variance_restricted |
| `edubench` domain_knowledge_accuracy (metric) | `mmlu_pro` overall/category accuracy | P05(0.2/0.5) | 7 | 0.607 | 0.182 | 0.1667 | [-0.176, 1.0] | variance_restricted |
| `mathtutorbench_mistake_correction` Mistake Correction | `mrbench_tutor` dimension: Actionability | P16(0.2/0.2) | 5 | 0.616 | 0.269 | 0.3 | [-0.395, 1.0] | variance_restricted |
| `agieval` overall/task/language/question_type accuracy | `mathtutorbench_problem_solving` Problem Solving | P05(0.2/0.2), P06(0.5/0.5) | 6 | 0.657 | 0.167 | 0.175 | [0.0, 1.0] | variance_restricted |
| `mathtutorbench_mistake_location` Mistake Location | `sas_bench` CCS step scoring consistency | P02(0.2/0.2), P10(0.8/0.2) | 6 | 0.657 | 0.436 | 0.175 | [0.0, 1.0] | variance_restricted |
| `edubench` higher_order_thinking_ability_development (metric) | `mathtutorbench_pedagogy` Pedagogy IF | P16(0.2/0.2) | 8 | 0.667 | 0.676 | 0.0831 | [0.089, 1.0] | variance_restricted |
| `edubench` higher_order_thinking_ability_development (metric) | `mathtutorbench_mistake_correction` Mistake Correction | P06(0.2/0.2), P16(0.2/0.2) | 7 | 0.679 | 0.667 | 0.1095 | [-0.059, 1.0] | variance_restricted |
| `mathtutorbench_mistake_correction` Mistake Correction | `mrbench_tutor` dimension: Mistake_Identification | P10(0.2/0.2) | 5 | 0.7 | 0.875 | 0.2333 | [-0.25, 1.0] | variance_restricted |
| `longtutor_evidence` Multi-session Reasoning accuracy | `mathtutorbench_mistake_location` Mistake Location | P02(0.8/0.2) | 6 | 0.714 | 0.531 | 0.1361 | [0.0, 1.0] | variance_restricted |
| `mathtutorbench_scaffolding` Scaffolding | `mrbench_tutor` dimension: Actionability | P16(0.2/0.2) | 5 | 0.718 | -0.082 | 0.1667 | [0.0, 1.0] | variance_restricted |
| `mathtutorbench_scaffolding_hard` Scaffolding hard | `mrbench_tutor` dimension: Actionability | P16(0.2/0.2) | 5 | 0.718 | -0.082 | 0.1667 | [0.111, 1.0] | variance_restricted |
| `mathtutorbench_socratic` Socratic Questioning | `mrbench_tutor` dimension: Actionability | P16(0.2/0.2) | 5 | 0.718 | -0.082 | 0.1667 | [0.0, 1.0] | variance_restricted |
| `mathtutorbench_problem_solving` Problem Solving | `mmlu_pro` overall/category accuracy | P05(0.2/0.5), P06(0.5/0.2) | 6 | 0.771 | 0.42 | 0.1028 | [0.091, 1.0] | variance_restricted |
| `longtutor_evidence` Information Extraction accuracy | `sas_bench` CCS step scoring consistency | P02(0.8/0.2) | 6 | 0.812 | 0.916 | 0.0722 | [0.091, 1.0] | variance_restricted |
| `bea2025_judge` judge labels: mistake/guidance/actionability | `sas_bench` CCS step scoring consistency | P11(0.5/0.5) | 6 | 0.829 | 0.748 | 0.0583 | [0.091, 1.0] | variance_restricted |
| `agieval` overall/task/language/question_type accuracy | `mmlu_pro` overall/category accuracy | P05(0.2/0.5), P06(0.5/0.2) | 7 | 0.857 | 0.767 | 0.0238 | [0.412, 1.0] | variance_restricted |
| `ceval` overall/category/subject accuracy | `mmlu_pro` overall/category accuracy | P05(0.5/0.5), P06(0.2/0.2) | 7 | 0.857 | 0.793 | 0.0238 | [0.333, 1.0] | variance_restricted |
| `edubench` domain_knowledge_accuracy (metric) | `mathtutorbench_problem_solving` Problem Solving | P05(0.2/0.2) | 6 | 0.886 | 0.75 | 0.0333 | [0.5, 1.0] | variance_restricted |
| `edubench` higher_order_thinking_ability_development (metric) | `mathtutorbench_socratic` Socratic Questioning | P16(0.2/0.2) | 6 | 0.886 | 0.584 | 0.0333 | [0.5, 1.0] | variance_restricted |
| `longtutor_evidence` Multi-session Reasoning accuracy | `sas_bench` CCS step scoring consistency | P02(0.8/0.2) | 6 | 0.886 | 0.821 | 0.0333 | [0.5, 1.0] | variance_restricted |
| `mathtutorbench_pedagogy` Pedagogy IF | `mrbench_tutor` dimension: Providing_Guidance | P14(0.5/0.2) | 5 | 0.9 | 0.688 | 0.0833 | [0.25, 1.0] | variance_restricted |
| `mathtutorbench_pedagogy_hard` Pedagogy IF hard | `mrbench_tutor` dimension: Providing_Guidance | P14(0.5/0.2) | 5 | 0.9 | 0.688 | 0.0833 | [0.25, 1.0] | variance_restricted |
| `mathtutorbench_scaffolding` Scaffolding | `mrbench_tutor` dimension: Providing_Guidance | P14(0.5/0.2) | 5 | 0.9 | 0.688 | 0.0833 | [0.25, 1.0] | variance_restricted |
| `mathtutorbench_scaffolding_hard` Scaffolding hard | `mrbench_tutor` dimension: Providing_Guidance | P14(0.5/0.2) | 5 | 0.9 | 0.688 | 0.0833 | [0.25, 1.0] | variance_restricted |
| `mathtutorbench_socratic` Socratic Questioning | `mrbench_tutor` dimension: Providing_Guidance | P14(0.5/0.2) | 5 | 0.9 | 0.688 | 0.0833 | [0.25, 1.0] | variance_restricted |
| `agieval` overall/task/language/question_type accuracy | `ceval` overall/category/subject accuracy | P05(0.2/0.5), P06(0.5/0.2) | 7 | 0.929 | 0.903 | 0.0067 | [0.647, 1.0] | variance_restricted |
| `mathtutorbench_pedagogy` Pedagogy IF | `pedagogy_benchmark` SEND special education needs selection | P05(0.2/0.5), P14(0.5/0.5 异facet) | 6 | 0.943 | 0.91 | 0.0167 | [0.515, 1.0] | variance_restricted |
| `edubench` higher_order_thinking_ability_development (metric) | `mrbench_tutor` dimension: Actionability | P16(0.2/0.2) | 5 | 0.975 | 0.948 | 0.0333 | [0.791, 1.0] | variance_restricted |
| `mathtutorbench_pedagogy` Pedagogy IF | `mrbench_tutor` dimension: Actionability | P16(0.2/0.2) | 5 | 0.975 | 0.948 | 0.0333 | [0.791, 1.0] | variance_restricted |
| `mathtutorbench_pedagogy_hard` Pedagogy IF hard | `mrbench_tutor` dimension: Actionability | P16(0.2/0.2) | 5 | 0.975 | 0.948 | 0.0333 | [0.791, 1.0] | variance_restricted |

## 区分效度（同 P 收敛配对 vs 不共享 P 的 baseline）

- 收敛配对（跨家族、非受限、n≥5）：18 对，mean ρ = 0.393，median = 0.4
- baseline（不共享任何 P）：135 对，mean ρ = 0.205，median = 0.2
- 差值 = 0.188，单侧 permutation p = 0.0389（配对之间共享格子、非独立；p 值仅供参考，结论以红旗/非红旗为主。）

若差值不显著为正，说明 P 划分对'哪些 benchmark 相关'没有预测力，映射层需整体重审。

## 家族方法方差（halo）

| 家族 | 家族内配对数 | 家族内 mean ρ | 跨家族配对数 | 跨家族 mean ρ | halo 分 | 家族内先聚合? |
|---|---:|---:|---:|---:|---:|---|
| `pedagogy_benchmark` | 1 | 0.823 | 82 | 0.377 | 0.446 | 否 |
| `eduguard` | 3 | 0.357 | 87 | 0.048 | 0.309 | 否 |
| `edubench` | 66 | 0.398 | 492 | 0.138 | 0.26 | 否 |
| `mathtutorbench` | 36 | 0.58 | 376 | 0.331 | 0.249 | 否 |
| `sas_bench` | 3 | 0.439 | 147 | 0.237 | 0.202 | 否 |
| `mrbench` | 10 | 0.391 | 213 | 0.283 | 0.108 | 否 |
| `p08` | 1 | 0.2 | 96 | 0.193 | 0.007 | 否 |
| `longtutor_evidence` | 3 | 0.233 | 141 | 0.235 | -0.002 | 否 |
| `bea2025` | 6 | 0.183 | 175 | 0.246 | -0.063 | 否 |

halo 分 > 0.5 的家族：多子维度在 P 聚合前先合成一票（计划 §2.6）。

## P × 格子评级汇总

评级分布：validated=8、flagged=3、watch=1、provisional=9、variance_restricted=55、insufficient_evidence=22、single_source=6

| P | 类型 | facet | Benchmark | Subdimension | 权重 | 评级 |
|---|---|---|---|---|---:|---|
| P01 指令与约束遵循 | reflective | core | `ifeval` | prompt-level strict accuracy | 1.0 | **variance_restricted** |
| P02 长上下文与证据定位 | reflective | core | `longtutor_evidence` | Hallucination Check accuracy | 0.8 | **insufficient_evidence** |
| P02 长上下文与证据定位 | reflective | core | `longtutor_evidence` | Multi-session Reasoning accuracy | 0.8 | **insufficient_evidence** |
| P02 长上下文与证据定位 | reflective | core | `longtutor_evidence` | Information Extraction accuracy | 0.8 | **variance_restricted** |
| P02 长上下文与证据定位 | reflective | core | `mathtutorbench_mistake_location` | Mistake Location | 0.2 | **variance_restricted** |
| P02 长上下文与证据定位 | reflective | core | `sas_bench` | CCS step scoring consistency | 0.2 | **variance_restricted** |
| P03 多模态理解 | formative | problem_images | `k12vista` | math problem-figure subset score | 0.5 | **insufficient_evidence** |
| P03 多模态理解 | formative | subject_charts | `k12vista` | science/geo subject-chart subset score | 0.5 | **insufficient_evidence** |
| P03 多模态理解 | formative | mixed_materials | `mmtutorbench` | multimodal tutor score | 0.2 | **insufficient_evidence** |
| P03 多模态理解 | formative | problem_images | `olympiadbench` | multimodal-subset accuracy | 0.2 | **insufficient_evidence** |
| P03 多模态理解 | formative | problem_images | `mathvista` | task/question_type/answer_type accuracy | 0.5 | **variance_restricted** |
| P03 多模态理解 | formative | mixed_materials | `tutorbench` | Fair815 multimodal tutor quality | 0.2 | **variance_restricted** |
| P04 多模态生成 | formative | static_visual | `eduillustrate` | 8-dim 0-5 visual explanation score | 0.5 | **single_source** |
| P05 知识调用与掌握 | formative | subject_knowledge | `k12vista` | official partial-credit score (per-blank 0/1 mean) | 0.2 | **insufficient_evidence** |
| P05 知识调用与掌握 | formative | subject_knowledge | `sas_bench` | ECS error-cause consistency | 0.2 | **insufficient_evidence** |
| P05 知识调用与掌握 | formative | pedagogical_knowledge | `pedagogy_benchmark` | CDPK teaching knowledge selection | 0.5 | **provisional** |
| P05 知识调用与掌握 | formative | pedagogical_knowledge | `mathtutorbench_pedagogy_hard` | Pedagogy IF hard | 0.2 | **validated** |
| P05 知识调用与掌握 | formative | pedagogical_knowledge | `mathtutorbench_scaffolding` | Scaffolding | 0.2 | **validated** |
| P05 知识调用与掌握 | formative | pedagogical_knowledge | `mathtutorbench_scaffolding_hard` | Scaffolding hard | 0.2 | **validated** |
| P05 知识调用与掌握 | formative | pedagogical_knowledge | `pedagogy_benchmark` | SEND special education needs selection | 0.5 | **validated** |
| P05 知识调用与掌握 | formative | subject_knowledge | `agieval` | overall/task/language/question_type accuracy | 0.2 | **variance_restricted** |
| P05 知识调用与掌握 | formative | subject_knowledge | `ceval` | overall/category/subject accuracy | 0.5 | **variance_restricted** |
| P05 知识调用与掌握 | formative | subject_knowledge | `edubench` | basic_factual_accuracy (metric) | 0.2 | **variance_restricted** |
| P05 知识调用与掌握 | formative | subject_knowledge | `edubench` | domain_knowledge_accuracy (metric) | 0.2 | **variance_restricted** |
| P05 知识调用与掌握 | formative | pedagogical_knowledge | `mathtutorbench_pedagogy` | Pedagogy IF | 0.2 | **variance_restricted** |
| P05 知识调用与掌握 | formative | subject_knowledge | `mathtutorbench_problem_solving` | Problem Solving | 0.2 | **variance_restricted** |
| P05 知识调用与掌握 | formative | subject_knowledge | `mathvista` | task/question_type/answer_type accuracy | 0.2 | **variance_restricted** |
| P05 知识调用与掌握 | formative | subject_knowledge | `mmlu_pro` | overall/category accuracy | 0.5 | **variance_restricted** |
| P05 知识调用与掌握 | formative | subject_knowledge | `olympiadbench` | overall/subject/language/modality accuracy | 0.2 | **variance_restricted** |
| P06 推理与生成 | formative | generative_reasoning | `edubench` | reasoning_process_rigor (metric) | 0.5 | **flagged** |
| P06 推理与生成 | formative | generative_reasoning | `sas_bench` | ECS error-cause consistency | 0.2 | **flagged** |
| P06 推理与生成 | formative | problem_reasoning | `k12vista` | official partial-credit score (per-blank 0/1 mean) | 0.2 | **insufficient_evidence** |
| P06 推理与生成 | formative | problem_reasoning | `agieval` | overall/task/language/question_type accuracy | 0.5 | **variance_restricted** |
| P06 推理与生成 | formative | problem_reasoning | `ceval` | overall/category/subject accuracy | 0.2 | **variance_restricted** |
| P06 推理与生成 | formative | generative_reasoning | `mathtutorbench_mistake_correction` | Mistake Correction | 0.2 | **variance_restricted** |
| P06 推理与生成 | formative | problem_reasoning | `mathtutorbench_problem_solving` | Problem Solving | 0.5 | **variance_restricted** |
| P06 推理与生成 | formative | problem_reasoning | `mathvista` | task/question_type/answer_type accuracy | 0.5 | **variance_restricted** |
| P06 推理与生成 | formative | problem_reasoning | `mmlu_pro` | overall/category accuracy | 0.2 | **variance_restricted** |
| P06 推理与生成 | formative | problem_reasoning | `olympiadbench` | overall/subject/language/modality accuracy | 0.5 | **variance_restricted** |
| P06 推理与生成 | formative | generative_reasoning | `edubench` | higher_order_thinking_ability_development (metric) | 0.2 | **watch** |
| P07 自我校验与修正 | reflective | core | `p08_calibration` | calibration composite (CWR/AUROC) | 0.2 | **insufficient_evidence** |
| P07 自我校验与修正 | reflective | core | `mathtutorbench_solution_correctness` | Solution Correctness | 0.2 | **variance_restricted** |
| P07 自我校验与修正 | reflective | core | `p07_selfcheck` | two-round self-check (fix/break rate) | 0.8 | **variance_restricted** |
| P08 置信度校准与弃答 | formative | calibration | `p08_calibration` | calibration composite (CWR/AUROC) | 0.8 | **insufficient_evidence** |
| P08 置信度校准与弃答 | formative | calibration | `p07_selfcheck` | two-round self-check (fix/break rate) | 0.2 | **variance_restricted** |
| P08 置信度校准与弃答 | formative | abstention | `p08_abstention` | balanced abstention score | 0.8 | **variance_restricted** |
| P10 错误诊断 | formative | error_attribution | `edubench` | error_identification_correction_accuracy (metric) | 0.2 | **flagged** |
| P10 错误诊断 | formative | error_attribution | `longtutor_diagnosis` | four-category knowledge-state diagnosis macro-F1 | 0.2 | **validated** |
| P10 错误诊断 | formative | error_attribution | `sas_bench` | ECS error-cause consistency | 0.8 | **validated** |
| P10 错误诊断 | formative | error_attribution | `bea2025_tutor` | dimension: Mistake_Identification | 0.2 | **variance_restricted** |
| P10 错误诊断 | formative | error_attribution | `mathtutorbench_mistake_correction` | Mistake Correction | 0.2 | **variance_restricted** |
| P10 错误诊断 | formative | error_location | `mathtutorbench_mistake_location` | Mistake Location | 0.8 | **variance_restricted** |
| P10 错误诊断 | formative | answer_verdict | `mathtutorbench_solution_correctness` | Solution Correctness | 0.5 | **variance_restricted** |
| P10 错误诊断 | formative | error_attribution | `mrbench_tutor` | dimension: Mistake_Identification | 0.2 | **variance_restricted** |
| P10 错误诊断 | formative | error_location | `sas_bench` | CCS step scoring consistency | 0.2 | **variance_restricted** |
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
| P16 适配性解释与反馈生成 | formative | artifact_generation | `edubench` | TMG/PCC × clarity_concision_inspiration + scenario_element_integration (task×metric) | 0.5 | **insufficient_evidence** |
| P16 适配性解释与反馈生成 | formative | artifact_generation | `eduillustrate` | 8-dim 0-5 visual explanation score | 0.2 | **insufficient_evidence** |
| P16 适配性解释与反馈生成 | formative | content_feedback | `mmtutorbench` | multimodal tutor score | 0.5 | **insufficient_evidence** |
| P16 适配性解释与反馈生成 | formative | content_feedback | `mathtutorbench_scaffolding` | Scaffolding | 0.2 | **provisional** |
| P16 适配性解释与反馈生成 | formative | content_feedback | `mathtutorbench_scaffolding_hard` | Scaffolding hard | 0.2 | **provisional** |
| P16 适配性解释与反馈生成 | formative | content_feedback | `edubench` | higher_order_thinking_ability_development (metric) | 0.2 | **validated** |
| P16 适配性解释与反馈生成 | formative | content_feedback | `mathtutorbench_pedagogy_hard` | Pedagogy IF hard | 0.2 | **validated** |
| P16 适配性解释与反馈生成 | formative | content_feedback | `bea2025_tutor` | dimension: Actionability | 0.2 | **variance_restricted** |
| P16 适配性解释与反馈生成 | formative | content_feedback | `edubench` | clarity_concision_inspiration (metric) | 0.2 | **variance_restricted** |
| P16 适配性解释与反馈生成 | formative | tone_support | `edubench` | motivation_guidance_positive_feedback (metric) | 0.5 | **variance_restricted** |
| P16 适配性解释与反馈生成 | formative | content_feedback | `mathtutorbench_mistake_correction` | Mistake Correction | 0.2 | **variance_restricted** |
| P16 适配性解释与反馈生成 | formative | content_feedback | `mathtutorbench_pedagogy` | Pedagogy IF | 0.2 | **variance_restricted** |
| P16 适配性解释与反馈生成 | formative | content_feedback | `mathtutorbench_socratic` | Socratic Questioning | 0.2 | **variance_restricted** |
| P16 适配性解释与反馈生成 | formative | content_feedback | `mrbench_tutor` | dimension: Actionability | 0.2 | **variance_restricted** |
| P16 适配性解释与反馈生成 | formative | tone_support | `mrbench_tutor` | dimension: Tutor_Tone (encouraging share) | 0.2 | **variance_restricted** |
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
| `mathtutorbench_problem_solving` Problem Solving | `olympiadbench` overall/subject/language/modality accuracy | P05(0.2/0.2), P06(0.5/0.5) | 4 | -0.8 |
| `bea2025_tutor` dimension: Providing_Guidance | `mmtutorbench` multimodal tutor score | P14(0.2/0.2) | 3 | -0.5 |
| `edubench` clarity_concision_inspiration (metric) | `mmtutorbench` multimodal tutor score | P16(0.2/0.5) | 3 | -0.5 |
| `asap_2` essay holistic QWK | `sas_bench` QWK holistic total score | P11(0.8/0.8) | 4 | -0.4 |
| `eduguard_adversarial` Adversarial Safety ASR | `mrbench_tutor` dimension: Tutor_Tone (non-offensive) | P17(0.5/0.2) | 3 | — |
| `eduguard_adversarial` Refusal quality distribution | `mrbench_tutor` dimension: Tutor_Tone (non-offensive) | P17(0.2/0.2) | 3 | — |
| `bea2025_tutor` dimension: Actionability | `mmtutorbench` multimodal tutor score | P16(0.2/0.5) | 3 | 0.5 |
| `edubench` basic_factual_accuracy (metric) | `k12vista` official partial-credit score (per-blank 0/1 mean) | P05(0.2/0.2) | 3 | 0.5 |
| `edubench` basic_factual_accuracy (metric) | `mathvista` task/question_type/answer_type accuracy | P05(0.2/0.2) | 3 | 0.5 |
| `edubench` higher_order_thinking_ability_development (metric) | `mmtutorbench` multimodal tutor score | P16(0.2/0.5) | 3 | 0.5 |
| `edubench` personalized_adaptation_learning_support (metric) | `mmtutorbench` multimodal tutor score | P14(0.5/0.2) | 3 | 0.5 |
| `edubench` scenario_element_integration (metric) | `mmtutorbench` multimodal tutor score | P14(0.2/0.2) | 3 | 0.5 |
| `k12vista` official partial-credit score (per-blank 0/1 mean) | `mathtutorbench_problem_solving` Problem Solving | P05(0.2/0.2), P06(0.2/0.5) | 3 | 0.5 |
| `k12vista` official partial-credit score (per-blank 0/1 mean) | `olympiadbench` overall/subject/language/modality accuracy | P05(0.2/0.2), P06(0.2/0.5) | 3 | 0.5 |
| `k12vista` official partial-credit score (per-blank 0/1 mean) | `sas_bench` ECS error-cause consistency | P05(0.2/0.2), P06(0.2/0.2 异facet) | 3 | 0.5 |
| `mathtutorbench_pedagogy` Pedagogy IF | `mmtutorbench` multimodal tutor score | P14(0.5/0.2), P16(0.2/0.5) | 3 | 0.5 |
| `mathtutorbench_pedagogy_hard` Pedagogy IF hard | `mmtutorbench` multimodal tutor score | P14(0.5/0.2), P16(0.2/0.5) | 3 | 0.5 |
| `mathtutorbench_problem_solving` Problem Solving | `mathvista` task/question_type/answer_type accuracy | P05(0.2/0.2), P06(0.5/0.5) | 3 | 0.5 |
| `mathtutorbench_scaffolding` Scaffolding | `mmtutorbench` multimodal tutor score | P14(0.5/0.2), P16(0.2/0.5) | 3 | 0.5 |
| `mathtutorbench_scaffolding_hard` Scaffolding hard | `mmtutorbench` multimodal tutor score | P14(0.5/0.2), P16(0.2/0.5) | 3 | 0.5 |
| `mathtutorbench_socratic` Socratic Questioning | `mmtutorbench` multimodal tutor score | P14(0.5/0.2), P16(0.2/0.5) | 3 | 0.5 |
| `mathvista` task/question_type/answer_type accuracy | `olympiadbench` overall/subject/language/modality accuracy | P05(0.2/0.2), P06(0.5/0.5) | 3 | 0.5 |
| `mathvista` task/question_type/answer_type accuracy | `sas_bench` ECS error-cause consistency | P05(0.2/0.2), P06(0.5/0.2 异facet) | 3 | 0.5 |
| `mmtutorbench` multimodal tutor score | `mrbench_tutor` dimension: Actionability | P16(0.5/0.2) | 3 | 0.5 |
| `mmtutorbench` multimodal tutor score | `mrbench_tutor` dimension: Providing_Guidance | P14(0.2/0.2) | 3 | 0.5 |
| `edubench` TMG/PCC × clarity_concision_inspiration + scenario_element_integration (task×metric) | `eduillustrate` 8-dim 0-5 visual explanation score | P16(0.5/0.2) | 4 | 0.8 |
| `agieval` overall/task/language/question_type accuracy | `k12vista` official partial-credit score (per-blank 0/1 mean) | P05(0.2/0.2), P06(0.5/0.2) | 3 | 1.0 |
| `agieval` overall/task/language/question_type accuracy | `mathvista` task/question_type/answer_type accuracy | P05(0.2/0.2), P06(0.5/0.5) | 3 | 1.0 |
| `ceval` overall/category/subject accuracy | `k12vista` official partial-credit score (per-blank 0/1 mean) | P05(0.5/0.2), P06(0.2/0.2) | 3 | 1.0 |
| `ceval` overall/category/subject accuracy | `mathvista` task/question_type/answer_type accuracy | P05(0.5/0.2), P06(0.2/0.5) | 3 | 1.0 |
| `edubench` domain_knowledge_accuracy (metric) | `k12vista` official partial-credit score (per-blank 0/1 mean) | P05(0.2/0.2) | 3 | 1.0 |
| `edubench` domain_knowledge_accuracy (metric) | `mathvista` task/question_type/answer_type accuracy | P05(0.2/0.2) | 3 | 1.0 |
| `k12vista` math problem-figure subset score | `mathvista` task/question_type/answer_type accuracy | P03(0.5/0.5) | 3 | 1.0 |
| `k12vista` math problem-figure subset score | `olympiadbench` multimodal-subset accuracy | P03(0.5/0.2) | 3 | 1.0 |
| `k12vista` official partial-credit score (per-blank 0/1 mean) | `mathvista` task/question_type/answer_type accuracy | P05(0.2/0.2), P06(0.2/0.5) | 3 | 1.0 |
| `k12vista` official partial-credit score (per-blank 0/1 mean) | `mmlu_pro` overall/category accuracy | P05(0.2/0.5), P06(0.2/0.2) | 3 | 1.0 |
| `longtutor_teaching` judge dims: strategy_alignment + history_utilization (1-5) | `mmtutorbench` multimodal tutor score | P14(0.2/0.2) | 3 | 1.0 |
| `mathtutorbench_mistake_correction` Mistake Correction | `mmtutorbench` multimodal tutor score | P16(0.2/0.5) | 3 | 1.0 |
| `mathvista` task/question_type/answer_type accuracy | `mmlu_pro` overall/category accuracy | P05(0.2/0.5), P06(0.5/0.2) | 3 | 1.0 |
| `mathvista` task/question_type/answer_type accuracy | `olympiadbench` multimodal-subset accuracy | P03(0.5/0.2) | 3 | 1.0 |

## 形成型跨 facet 配对（facet_distinct_expected，信息呈现，不触发红旗）

| A | B | 共享 P | n | ρ |
|---|---|---|---:|---:|
| `edubench` personalized_adaptation_learning_support (metric) | `longtutor_diagnosis` four-category knowledge-state diagnosis macro-F1 | P13(0.2/0.8 异facet) | 6 | -0.6 |
| `mathtutorbench_mistake_location` Mistake Location | `mrbench_tutor` dimension: Mistake_Identification | P10(0.8/0.2 异facet) | 5 | -0.6 |
| `bea2025_tutor` dimension: Mistake_Identification | `mathtutorbench_solution_correctness` Solution Correctness | P10(0.2/0.5 异facet) | 5 | -0.5 |
| `mathtutorbench_solution_correctness` Solution Correctness | `sas_bench` ECS error-cause consistency | P10(0.5/0.8 异facet) | 6 | -0.486 |
| `bea2025_tutor` dimension: Mistake_Identification | `sas_bench` CCS step scoring consistency | P10(0.2/0.2 异facet) | 5 | -0.4 |
| `edubench` personalized_adaptation_learning_support (metric) | `pedagogy_benchmark` CDPK teaching knowledge selection | P14(0.5/0.8 异facet) | 9 | -0.4 |
| `mrbench_judge` 8-dimension tutor response judging | `sas_bench` QWK holistic total score | P11(0.5/0.8 异facet) | 6 | -0.257 |
| `mathtutorbench_scaffolding` Scaffolding | `olympiadbench` overall/subject/language/modality accuracy | P05(0.2/0.2 异facet) | 5 | -0.2 |
| `mathtutorbench_scaffolding_hard` Scaffolding hard | `olympiadbench` overall/subject/language/modality accuracy | P05(0.2/0.2 异facet) | 5 | -0.2 |
| `edubench` basic_factual_accuracy (metric) | `mathtutorbench_scaffolding_hard` Scaffolding hard | P05(0.2/0.2 异facet) | 8 | -0.19 |
| `edubench` error_identification_correction_accuracy (metric) | `mathtutorbench_mistake_location` Mistake Location | P10(0.2/0.8 异facet) | 7 | -0.179 |
| `edubench` basic_factual_accuracy (metric) | `pedagogy_benchmark` SEND special education needs selection | P05(0.2/0.5 异facet) | 9 | -0.151 |
| `edubench` basic_factual_accuracy (metric) | `mathtutorbench_scaffolding` Scaffolding | P05(0.2/0.2 异facet) | 8 | -0.143 |
| `longtutor_diagnosis` four-category knowledge-state diagnosis macro-F1 | `mathtutorbench_solution_correctness` Solution Correctness | P10(0.2/0.5 异facet) | 6 | -0.143 |
| `edubench` error_identification_correction_accuracy (metric) | `sas_bench` CCS step scoring consistency | P10(0.2/0.2 异facet) | 8 | -0.119 |
| `mathtutorbench_scaffolding` Scaffolding | `sas_bench` ECS error-cause consistency | P05(0.2/0.2 异facet) | 6 | -0.086 |
| `mathtutorbench_scaffolding_hard` Scaffolding hard | `sas_bench` ECS error-cause consistency | P05(0.2/0.2 异facet) | 6 | -0.086 |
| `p07_selfcheck` two-round self-check (fix/break rate) | `p08_abstention` balanced abstention score | P08(0.2/0.8 异facet) | 6 | -0.086 |
| `edubench` basic_factual_accuracy (metric) | `mathtutorbench_pedagogy` Pedagogy IF | P05(0.2/0.2 异facet) | 8 | -0.048 |
| `edubench` basic_factual_accuracy (metric) | `mathtutorbench_pedagogy_hard` Pedagogy IF hard | P05(0.2/0.2 异facet) | 8 | -0.048 |
| `edubench` error_identification_correction_accuracy (metric) | `mathtutorbench_solution_correctness` Solution Correctness | P10(0.2/0.5 异facet) | 7 | -0.036 |
| `mathtutorbench_mistake_location` Mistake Location | `sas_bench` ECS error-cause consistency | P10(0.8/0.8 异facet) | 6 | -0.029 |
| `edubench` clarity_concision_inspiration (metric) | `mrbench_tutor` dimension: Tutor_Tone (encouraging share) | P16(0.2/0.2 异facet) | 5 | 0.0 |
| `edubench` TMG/PCC × clarity_concision_inspiration + scenario_element_integration (task×metric) | `mathtutorbench_scaffolding_hard` Scaffolding hard | P16(0.5/0.2 异facet) | 8 | 0.048 |
| `mathtutorbench_pedagogy` Pedagogy IF | `sas_bench` ECS error-cause consistency | P05(0.2/0.2 异facet) | 6 | 0.086 |
| `bea2025_tutor` dimension: Mistake_Identification | `mathtutorbench_mistake_location` Mistake Location | P10(0.2/0.8 异facet) | 5 | 0.1 |
| `edubench` basic_factual_accuracy (metric) | `pedagogy_benchmark` CDPK teaching knowledge selection | P05(0.2/0.5 异facet) | 9 | 0.1 |
| `edubench` higher_order_thinking_ability_development (metric) | `olympiadbench` overall/subject/language/modality accuracy | P06(0.2/0.5 异facet) | 5 | 0.1 |
| `edubench` reasoning_process_rigor (metric) | `olympiadbench` overall/subject/language/modality accuracy | P06(0.5/0.5 异facet) | 5 | 0.1 |
| `mrbench_tutor` dimension: Mistake_Identification | `sas_bench` CCS step scoring consistency | P10(0.2/0.2 异facet) | 5 | 0.1 |
| `edubench` TMG/PCC × clarity_concision_inspiration + scenario_element_integration (task×metric) | `mathtutorbench_scaffolding` Scaffolding | P16(0.5/0.2 异facet) | 8 | 0.143 |
| `edubench` motivation_guidance_positive_feedback (metric) | `mathtutorbench_pedagogy` Pedagogy IF | P16(0.5/0.2 异facet) | 8 | 0.143 |
| `edubench` domain_knowledge_accuracy (metric) | `pedagogy_benchmark` SEND special education needs selection | P05(0.2/0.5 异facet) | 9 | 0.167 |
| `mathtutorbench_mistake_correction` Mistake Correction | `mrbench_tutor` dimension: Tutor_Tone (encouraging share) | P16(0.2/0.2 异facet) | 5 | 0.2 |
| `mathtutorbench_scaffolding` Scaffolding | `mrbench_tutor` dimension: Tutor_Tone (encouraging share) | P16(0.2/0.2 异facet) | 5 | 0.2 |
| `mathtutorbench_scaffolding_hard` Scaffolding hard | `mrbench_tutor` dimension: Tutor_Tone (encouraging share) | P16(0.2/0.2 异facet) | 5 | 0.2 |
| `mathtutorbench_socratic` Socratic Questioning | `mrbench_tutor` dimension: Tutor_Tone (encouraging share) | P16(0.2/0.2 异facet) | 5 | 0.2 |
| `edubench` domain_knowledge_accuracy (metric) | `mathtutorbench_scaffolding_hard` Scaffolding hard | P05(0.2/0.2 异facet) | 8 | 0.238 |
| `edubench` motivation_guidance_positive_feedback (metric) | `mathtutorbench_socratic` Socratic Questioning | P16(0.5/0.2 异facet) | 6 | 0.257 |
| `longtutor_diagnosis` four-category knowledge-state diagnosis macro-F1 | `mathtutorbench_mistake_location` Mistake Location | P10(0.2/0.8 异facet) | 6 | 0.257 |
| `edubench` motivation_guidance_positive_feedback (metric) | `mathtutorbench_mistake_correction` Mistake Correction | P16(0.5/0.2 异facet) | 7 | 0.286 |
| `bea2025_tutor` dimension: Actionability | `edubench` TMG/PCC × clarity_concision_inspiration + scenario_element_integration (task×metric) | P16(0.2/0.5 异facet) | 5 | 0.3 |
| `longtutor_teaching` judge dims: strategy_alignment + history_utilization (1-5) | `pedagogy_benchmark` CDPK teaching knowledge selection | P14(0.2/0.8 异facet) | 5 | 0.3 |
| `mathtutorbench_pedagogy` Pedagogy IF | `olympiadbench` overall/subject/language/modality accuracy | P05(0.2/0.2 异facet) | 5 | 0.3 |
| `mathtutorbench_problem_solving` Problem Solving | `pedagogy_benchmark` CDPK teaching knowledge selection | P05(0.2/0.5 异facet) | 5 | 0.3 |
| `edubench` domain_knowledge_accuracy (metric) | `mathtutorbench_scaffolding` Scaffolding | P05(0.2/0.2 异facet) | 8 | 0.31 |
| `edubench` motivation_guidance_positive_feedback (metric) | `mathtutorbench_pedagogy_hard` Pedagogy IF hard | P16(0.5/0.2 异facet) | 8 | 0.31 |
| `mathtutorbench_pedagogy_hard` Pedagogy IF hard | `sas_bench` ECS error-cause consistency | P05(0.2/0.2 异facet) | 6 | 0.314 |
| `edubench` TMG/PCC × clarity_concision_inspiration + scenario_element_integration (task×metric) | `mathtutorbench_pedagogy_hard` Pedagogy IF hard | P16(0.5/0.2 异facet) | 8 | 0.333 |
| `edubench` motivation_guidance_positive_feedback (metric) | `mathtutorbench_scaffolding` Scaffolding | P16(0.5/0.2 异facet) | 8 | 0.333 |
| `edubench` TMG/PCC × clarity_concision_inspiration + scenario_element_integration (task×metric) | `mathtutorbench_pedagogy` Pedagogy IF | P16(0.5/0.2 异facet) | 8 | 0.357 |
| `edubench` motivation_guidance_positive_feedback (metric) | `mathtutorbench_scaffolding_hard` Scaffolding hard | P16(0.5/0.2 异facet) | 8 | 0.357 |
| `edubench` motivation_guidance_positive_feedback (metric) | `mrbench_tutor` dimension: Actionability | P16(0.5/0.2 异facet) | 5 | 0.359 |
| `edubench` domain_knowledge_accuracy (metric) | `pedagogy_benchmark` CDPK teaching knowledge selection | P05(0.2/0.5 异facet) | 9 | 0.367 |
| `edubench` domain_knowledge_accuracy (metric) | `mathtutorbench_pedagogy` Pedagogy IF | P05(0.2/0.2 异facet) | 8 | 0.381 |
| `edubench` domain_knowledge_accuracy (metric) | `mathtutorbench_pedagogy_hard` Pedagogy IF hard | P05(0.2/0.2 异facet) | 8 | 0.381 |
| `edubench` TMG/PCC × clarity_concision_inspiration + scenario_element_integration (task×metric) | `mathtutorbench_mistake_correction` Mistake Correction | P16(0.5/0.2 异facet) | 7 | 0.393 |
| `edubench` TMG/PCC × clarity_concision_inspiration + scenario_element_integration (task×metric) | `mrbench_tutor` dimension: Tutor_Tone (encouraging share) | P16(0.5/0.2 异facet) | 5 | 0.4 |
| `longtutor_teaching` judge dims: strategy_alignment + history_utilization (1-5) | `pedagogy_benchmark` SEND special education needs selection | P14(0.2/0.5 异facet) | 5 | 0.4 |
| `mathtutorbench_mistake_correction` Mistake Correction | `olympiadbench` overall/subject/language/modality accuracy | P06(0.2/0.5 异facet) | 5 | 0.4 |
| `mathtutorbench_solution_correctness` Solution Correctness | `mrbench_tutor` dimension: Mistake_Identification | P10(0.5/0.2 异facet) | 5 | 0.4 |
| `edubench` scenario_element_integration (metric) | `pedagogy_benchmark` SEND special education needs selection | P14(0.2/0.5 异facet) | 9 | 0.427 |
| `mathtutorbench_mistake_correction` Mistake Correction | `sas_bench` CCS step scoring consistency | P10(0.2/0.2 异facet) | 6 | 0.429 |
| `edubench` scenario_element_integration (metric) | `pedagogy_benchmark` CDPK teaching knowledge selection | P14(0.2/0.8 异facet) | 9 | 0.45 |
| `pedagogy_benchmark` CDPK teaching knowledge selection | `sas_bench` ECS error-cause consistency | P05(0.5/0.2 异facet) | 8 | 0.476 |
| `bea2025_tutor` dimension: Actionability | `mrbench_tutor` dimension: Tutor_Tone (encouraging share) | P16(0.2/0.2 异facet) | 5 | 0.5 |
| `mathtutorbench_problem_solving` Problem Solving | `pedagogy_benchmark` SEND special education needs selection | P05(0.2/0.5 异facet) | 5 | 0.5 |
| `mathtutorbench_socratic` Socratic Questioning | `pedagogy_benchmark` CDPK teaching knowledge selection | P14(0.5/0.8 异facet) | 5 | 0.5 |
| `edubench` reasoning_process_rigor (metric) | `mmlu_pro` overall/category accuracy | P06(0.5/0.2 异facet) | 7 | 0.536 |
| `edubench` higher_order_thinking_ability_development (metric) | `mathtutorbench_problem_solving` Problem Solving | P06(0.2/0.5 异facet) | 6 | 0.543 |
| `edubench` reasoning_process_rigor (metric) | `mathtutorbench_problem_solving` Problem Solving | P06(0.5/0.5 异facet) | 6 | 0.543 |
| `longtutor_diagnosis` four-category knowledge-state diagnosis macro-F1 | `sas_bench` CCS step scoring consistency | P10(0.2/0.2 异facet) | 6 | 0.543 |
| `mathtutorbench_solution_correctness` Solution Correctness | `sas_bench` CCS step scoring consistency | P10(0.5/0.2 异facet) | 6 | 0.543 |
| `bea2025_judge` judge labels: mistake/guidance/actionability | `sas_bench` QWK holistic total score | P11(0.5/0.8 异facet) | 6 | 0.6 |
| `mathtutorbench_pedagogy_hard` Pedagogy IF hard | `olympiadbench` overall/subject/language/modality accuracy | P05(0.2/0.2 异facet) | 5 | 0.6 |
| `ceval` overall/category/subject accuracy | `edubench` reasoning_process_rigor (metric) | P06(0.2/0.5 异facet) | 7 | 0.607 |
| `agieval` overall/task/language/question_type accuracy | `edubench` reasoning_process_rigor (metric) | P06(0.5/0.5 异facet) | 7 | 0.679 |
| `ceval` overall/category/subject accuracy | `mathtutorbench_scaffolding` Scaffolding | P05(0.5/0.2 异facet) | 7 | 0.679 |
| `ceval` overall/category/subject accuracy | `mathtutorbench_scaffolding_hard` Scaffolding hard | P05(0.5/0.2 异facet) | 7 | 0.679 |
| `edubench` higher_order_thinking_ability_development (metric) | `mmlu_pro` overall/category accuracy | P06(0.2/0.2 异facet) | 7 | 0.679 |
| `bea2025_tutor` dimension: Actionability | `edubench` motivation_guidance_positive_feedback (metric) | P16(0.2/0.5 异facet) | 5 | 0.7 |
| `edubench` higher_order_thinking_ability_development (metric) | `mrbench_tutor` dimension: Tutor_Tone (encouraging share) | P16(0.2/0.2 异facet) | 5 | 0.7 |
| `longtutor_diagnosis` four-category knowledge-state diagnosis macro-F1 | `pedagogy_benchmark` SEND special education needs selection | P13(0.8/0.2 异facet) | 5 | 0.7 |
| `mathtutorbench_pedagogy` Pedagogy IF | `mrbench_tutor` dimension: Tutor_Tone (encouraging share) | P16(0.2/0.2 异facet) | 5 | 0.7 |
| `mathtutorbench_pedagogy_hard` Pedagogy IF hard | `mrbench_tutor` dimension: Tutor_Tone (encouraging share) | P16(0.2/0.2 异facet) | 5 | 0.7 |
| `ceval` overall/category/subject accuracy | `edubench` higher_order_thinking_ability_development (metric) | P06(0.2/0.2 异facet) | 7 | 0.75 |
| `agieval` overall/task/language/question_type accuracy | `pedagogy_benchmark` CDPK teaching knowledge selection | P05(0.2/0.5 异facet) | 6 | 0.771 |
| `mmlu_pro` overall/category accuracy | `pedagogy_benchmark` CDPK teaching knowledge selection | P05(0.5/0.5 异facet) | 6 | 0.771 |
| `agieval` overall/task/language/question_type accuracy | `mathtutorbench_scaffolding` Scaffolding | P05(0.2/0.2 异facet) | 7 | 0.786 |
| `agieval` overall/task/language/question_type accuracy | `mathtutorbench_scaffolding_hard` Scaffolding hard | P05(0.2/0.2 异facet) | 7 | 0.786 |
| `mathtutorbench_mistake_correction` Mistake Correction | `mmlu_pro` overall/category accuracy | P06(0.2/0.2 异facet) | 7 | 0.786 |
| `mathtutorbench_pedagogy` Pedagogy IF | `mmlu_pro` overall/category accuracy | P05(0.2/0.5 异facet) | 7 | 0.786 |
| `mathtutorbench_socratic` Socratic Questioning | `pedagogy_benchmark` SEND special education needs selection | P14(0.5/0.5 异facet) | 5 | 0.8 |
| `agieval` overall/task/language/question_type accuracy | `edubench` higher_order_thinking_ability_development (metric) | P06(0.5/0.2 异facet) | 7 | 0.821 |
| `agieval` overall/task/language/question_type accuracy | `mathtutorbench_pedagogy` Pedagogy IF | P05(0.2/0.2 异facet) | 7 | 0.821 |
| `edubench` TMG/PCC × clarity_concision_inspiration + scenario_element_integration (task×metric) | `mrbench_tutor` dimension: Actionability | P16(0.5/0.2 异facet) | 5 | 0.821 |
| `mathtutorbench_pedagogy_hard` Pedagogy IF hard | `mmlu_pro` overall/category accuracy | P05(0.2/0.5 异facet) | 7 | 0.821 |
| `mathtutorbench_scaffolding` Scaffolding | `mmlu_pro` overall/category accuracy | P05(0.2/0.5 异facet) | 7 | 0.821 |
| `mathtutorbench_scaffolding_hard` Scaffolding hard | `mmlu_pro` overall/category accuracy | P05(0.2/0.5 异facet) | 7 | 0.821 |
| `edubench` TMG/PCC × clarity_concision_inspiration + scenario_element_integration (task×metric) | `mathtutorbench_socratic` Socratic Questioning | P16(0.5/0.2 异facet) | 6 | 0.829 |
| `pedagogy_benchmark` SEND special education needs selection | `sas_bench` ECS error-cause consistency | P05(0.5/0.2 异facet) | 8 | 0.833 |
| `ceval` overall/category/subject accuracy | `mathtutorbench_mistake_correction` Mistake Correction | P06(0.2/0.2 异facet) | 7 | 0.857 |
| `ceval` overall/category/subject accuracy | `mathtutorbench_pedagogy` Pedagogy IF | P05(0.5/0.2 异facet) | 7 | 0.857 |
| `agieval` overall/task/language/question_type accuracy | `pedagogy_benchmark` SEND special education needs selection | P05(0.2/0.5 异facet) | 6 | 0.886 |
| `ceval` overall/category/subject accuracy | `pedagogy_benchmark` CDPK teaching knowledge selection | P05(0.5/0.5 异facet) | 6 | 0.886 |
| `mmlu_pro` overall/category accuracy | `pedagogy_benchmark` SEND special education needs selection | P05(0.5/0.5 异facet) | 6 | 0.886 |
| `agieval` overall/task/language/question_type accuracy | `mathtutorbench_pedagogy_hard` Pedagogy IF hard | P05(0.2/0.2 异facet) | 7 | 0.893 |
| `ceval` overall/category/subject accuracy | `pedagogy_benchmark` SEND special education needs selection | P05(0.5/0.5 异facet) | 6 | 0.943 |
| `agieval` overall/task/language/question_type accuracy | `mathtutorbench_mistake_correction` Mistake Correction | P06(0.5/0.2 异facet) | 7 | 0.964 |
| `ceval` overall/category/subject accuracy | `mathtutorbench_pedagogy_hard` Pedagogy IF hard | P05(0.5/0.2 异facet) | 7 | 0.964 |

## 局限

- n=5-8 的置信区间很宽，评级以红旗探测为目的，不是效应量精确估计；补模型数（M2.5）是第一优先级。
- 偏相关控制的'综合分'由同一批证据构造，存在轻度内生性；仅作敏感性检查。
- 配对之间共享格子、非独立，区分效度的 permutation p 只作参考。