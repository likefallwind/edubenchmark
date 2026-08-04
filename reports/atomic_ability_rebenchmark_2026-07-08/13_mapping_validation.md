# 映射效度检查报告（13 号）

生成脚本：`scripts/build_mapping_validation.py`（幂等）；测量模型：`data/mapping_measurement_model_v6.json`（adjudicated）。
规则见 `doc/mapping_validation_plan_2026-07-11.md` §2；ρ 一律与 n、90% CI 同格呈现，n<5 的配对只进低置信附录。

覆盖缺口（无任何 benchmark 映射，不参与本报告分析）：P09 工具使用与长程智能体执行、P20 学术诚信与作答真实性判定。

## Phase 0：天花板/方差受限名单

共 38 / 62 个有证据格子被标记 `variance_restricted`（mean≥8.5 或 n≥4 且 SD<0.5）。这些格子参与的配对**不进入裁决**；优先动作是上难度/换切分，不是改映射。

| Benchmark | Subdimension | n | mean | SD | 标记 |
|---|---|---:|---:|---:|---|
| `mrbench_tutor` | dimension: Tutor_Tone (non-offensive) | 3 | 10.0 | 0.0 | ceiling |
| `mathtutorbench_problem_solving` | Problem Solving | 5 | 9.707 | 0.096 | ceiling, low_variance |
| `bea2025_tutor` | dimension: Providing_Guidance | 3 | 9.633 | 0.203 | ceiling |
| `longtutor_evidence` | Information Extraction accuracy | 5 | 9.582 | 0.152 | ceiling, low_variance |
| `mrbench_tutor` | dimension: Tutor_Tone (encouraging share) | 3 | 9.35 | 0.229 | ceiling |
| `bea2025_tutor` | dimension: Actionability | 3 | 9.311 | 0.391 | ceiling |
| `edubench` | QG × domain_knowledge_accuracy + basic_factual_accuracy (task×metric) | 12 | 9.297 | 0.424 | ceiling, low_variance |
| `edubench` | basic_factual_accuracy (metric) | 12 | 9.149 | 0.344 | ceiling, low_variance |
| `mrbench_tutor` | dimension: Actionability | 3 | 9.1 | 0.433 | ceiling |
| `ifeval` | prompt-level strict accuracy | 5 | 9.063 | 0.224 | ceiling, low_variance |
| `ceval` | overall/category/subject accuracy | 7 | 9.054 | 0.453 | ceiling, low_variance |
| `mrbench_tutor` | dimension: Providing_Guidance | 3 | 9.05 | 0.218 | ceiling |
| `mrbench_tutor` | dimension: Mistake_Identification | 3 | 9.017 | 0.333 | ceiling |
| `mathtutorbench_mistake_correction` | Mistake Correction | 5 | 9.016 | 0.33 | ceiling, low_variance |
| `p08_abstention` | balanced abstention score | 5 | 8.9 | 0.219 | ceiling, low_variance |
| `agieval` | overall/task/language/question_type accuracy | 6 | 8.815 | 0.406 | ceiling, low_variance |
| `edubench` | domain_knowledge_accuracy (metric) | 12 | 8.753 | 0.63 | ceiling |
| `mathtutorbench_solution_correctness` | Solution Correctness | 6 | 8.708 | 0.153 | ceiling, low_variance |
| `mathvista` | task/question_type/answer_type accuracy | 2 | 8.639 | 0.326 | ceiling |
| `mmlu_pro` | overall/category accuracy | 6 | 8.609 | 0.192 | ceiling, low_variance |
| `edubench` | clarity_concision_inspiration (metric) | 12 | 8.424 | 0.314 | low_variance |
| `sas_bench` | QWK holistic total score | 8 | 8.272 | 0.272 | low_variance |
| `mathtutorbench_pedagogy` | Pedagogy IF | 7 | 8.253 | 0.483 | low_variance |
| `edubench` | QG × clarity_concision_inspiration + scenario_element_integration (task×metric) | 12 | 8.162 | 0.414 | low_variance |
| `pedagogy_benchmark` | SEND special education needs selection | 11 | 7.884 | 0.496 | low_variance |
| `mathtutorbench_mistake_location` | Mistake Location | 6 | 7.728 | 0.106 | low_variance |
| `edubench` | scenario_element_integration (metric) | 12 | 7.685 | 0.4 | low_variance |
| `sas_bench` | CCS step scoring consistency | 8 | 7.648 | 0.258 | low_variance |
| `eduguard_sata` | Teaching Harm / SATA RFS | 8 | 7.473 | 0.255 | low_variance |
| `eduillustrate` | 8-dim 0-5 visual explanation score | 4 | 6.929 | 0.467 | low_variance |
| `longtutor_evidence` | Multi-session Reasoning accuracy | 5 | 6.752 | 0.445 | low_variance |
| `edubench` | motivation_guidance_positive_feedback (metric) | 12 | 6.454 | 0.275 | low_variance |
| `p08_calibration` | calibration composite (CWR/AUROC) | 5 | 6.439 | 0.492 | low_variance |
| `edubench` | personalized_adaptation_learning_support (metric) | 12 | 6.343 | 0.354 | low_variance |
| `tutorbench` | Fair815 multimodal tutor quality | 6 | 5.478 | 0.25 | low_variance |
| `p07_selfcheck` | two-round self-check (fix/break rate) | 5 | 5.288 | 0.226 | low_variance |
| `mooccube_prereq` | chance-corrected composite (先修选择 + 学习顺序排序) | 5 | 4.28 | 0.412 | low_variance |
| `mathtutorbench_socratic` | Socratic Questioning | 4 | 2.726 | 0.402 | low_variance |

## 红旗配对（flagged：同 P 预期收敛却 ρ<0，n≥6）

每条 flagged 需人工裁决：改权重 / 拆 facet / 转裁判治理（计划 §2.6）。

| A | B | 共享 P（权重A/B） | n | ρ | 偏ρ(控综合分) | perm p | 90% CI | 评级 |
|---|---|---|---:|---:|---:|---:|---|---|
| `edubench` reasoning_process_rigor (metric) | `sas_bench` ECS error-cause consistency | P06(0.5/0.2) | 7 | -0.357 | -0.363 | 0.4444 | [-1.0, 0.373] | flagged |
| `edubench` error_identification_correction_accuracy (metric) | `sas_bench` ECS error-cause consistency | P10(0.2/0.8) | 7 | -0.321 | -0.369 | 0.4976 | [-0.887, 0.585] | flagged |
| `edubench` higher_order_thinking_ability_development (metric) | `sas_bench` ECS error-cause consistency | P06(0.2/0.2) | 7 | -0.036 | 0.011 | 0.9635 | [-0.647, 0.808] | flagged |

## 观察带（watch：0≤ρ<0.2 且 n≥8）

（无）

## 已验证配对（validated：ρ≥0.5 且 CI 下界>0）

| A | B | 共享 P（权重A/B） | n | ρ | 偏ρ(控综合分) | perm p | 90% CI | 评级 |
|---|---|---|---:|---:|---:|---:|---|---|
| `longtutor_teaching` judge dims: strategy_alignment + history_utilization (1-5) | `mathtutorbench_pedagogy_hard` Pedagogy IF hard | P14(0.2/0.5) | 5 | 0.9 | 0.919 | 0.0833 | [0.25, 1.0] | validated |
| `longtutor_diagnosis` four-category knowledge-state diagnosis macro-F1 | `sas_bench` ECS error-cause consistency | P10(0.2/0.8) | 5 | 0.8 | 0.756 | 0.1333 | [0.111, 1.0] | validated |

## 待定配对（provisional）

| A | B | 共享 P（权重A/B） | n | ρ | 偏ρ(控综合分) | perm p | 90% CI | 评级 |
|---|---|---|---:|---:|---:|---:|---|---|
| `edubench` error_identification_correction_accuracy (metric) | `longtutor_diagnosis` four-category knowledge-state diagnosis macro-F1 | P10(0.2/0.2) | 5 | -0.4 | -0.756 | 0.5167 | [-1.0, 0.875] | provisional |
| `longtutor_teaching` judge dims: strategy_alignment + history_utilization (1-5) | `mathtutorbench_scaffolding` Scaffolding | P14(0.2/0.5) | 5 | 0.3 | 0.327 | 0.6833 | [-1.0, 1.0] | provisional |
| `longtutor_teaching` judge dims: strategy_alignment + history_utilization (1-5) | `mathtutorbench_scaffolding_hard` Scaffolding hard | P14(0.2/0.5) | 5 | 0.3 | 0.327 | 0.6833 | [-1.0, 1.0] | provisional |
| `mathtutorbench_scaffolding` Scaffolding | `pedagogy_benchmark` CDPK teaching knowledge selection | P05(0.2/0.5), P14(0.5/0.8 异facet) | 5 | 0.3 | 0.314 | 0.6833 | [-0.667, 1.0] | provisional |
| `mathtutorbench_scaffolding_hard` Scaffolding hard | `pedagogy_benchmark` CDPK teaching knowledge selection | P05(0.2/0.5), P14(0.5/0.8 异facet) | 5 | 0.3 | 0.314 | 0.6833 | [-0.875, 1.0] | provisional |
| `bea2025_judge` judge labels: mistake/guidance/actionability | `mrbench_judge` 8-dimension tutor response judging | P11(0.5/0.5) | 6 | 0.429 | 0.316 | 0.4194 | [-0.5, 1.0] | provisional |
| `mathtutorbench_pedagogy_hard` Pedagogy IF hard | `pedagogy_benchmark` CDPK teaching knowledge selection | P05(0.2/0.5), P14(0.5/0.8 异facet) | 5 | 0.5 | 0.435 | 0.45 | [-0.667, 1.0] | provisional |
| `edubench` higher_order_thinking_ability_development (metric) | `mathtutorbench_pedagogy_hard` Pedagogy IF hard | P16(0.2/0.2) | 7 | 0.536 | 0.598 | 0.2357 | [-0.348, 1.0] | provisional |
| `edubench` higher_order_thinking_ability_development (metric) | `mathtutorbench_scaffolding` Scaffolding | P16(0.2/0.2) | 7 | 0.536 | 0.306 | 0.2357 | [-0.208, 1.0] | provisional |
| `edubench` higher_order_thinking_ability_development (metric) | `mathtutorbench_scaffolding_hard` Scaffolding hard | P16(0.2/0.2) | 7 | 0.536 | 0.306 | 0.2357 | [-0.321, 1.0] | provisional |

## 因方差受限不裁决的配对

任一侧格子 variance_restricted；其 ρ 不作为构念证据。

| A | B | 共享 P（权重A/B） | n | ρ | 偏ρ(控综合分) | perm p | 90% CI | 评级 |
|---|---|---|---:|---:|---:|---:|---|---|
| `edubench` basic_factual_accuracy (metric) | `sas_bench` ECS error-cause consistency | P05(0.2/0.2) | 7 | -0.607 | -0.626 | 0.1667 | [-1.0, 0.176] | variance_restricted |
| `edubench` personalized_adaptation_learning_support (metric) | `longtutor_teaching` judge dims: strategy_alignment + history_utilization (1-5) | P14(0.5/0.2) | 5 | -0.6 | -0.612 | 0.35 | [-1.0, 0.25] | variance_restricted |
| `edubench` scenario_element_integration (metric) | `longtutor_teaching` judge dims: strategy_alignment + history_utilization (1-5) | P14(0.2/0.2) | 5 | -0.5 | -0.577 | 0.45 | [-1.0, 0.667] | variance_restricted |
| `ceval` overall/category/subject accuracy | `edubench` basic_factual_accuracy (metric) | P05(0.5/0.2) | 6 | -0.486 | -0.618 | 0.3556 | [-1.0, 0.5] | variance_restricted |
| `edubench` clarity_concision_inspiration (metric) | `mathtutorbench_pedagogy_hard` Pedagogy IF hard | P16(0.2/0.2) | 7 | -0.464 | -0.843 | 0.3024 | [-0.961, 0.208] | variance_restricted |
| `edubench` domain_knowledge_accuracy (metric) | `sas_bench` ECS error-cause consistency | P05(0.2/0.2) | 7 | -0.429 | -0.42 | 0.3536 | [-1.0, 0.412] | variance_restricted |
| `edubench` clarity_concision_inspiration (metric) | `mathtutorbench_pedagogy` Pedagogy IF | P16(0.2/0.2) | 7 | -0.393 | -0.674 | 0.3956 | [-0.882, 0.348] | variance_restricted |
| `edubench` personalized_adaptation_learning_support (metric) | `pedagogy_benchmark` SEND special education needs selection | P13(0.2/0.2), P14(0.5/0.5 异facet) | 8 | -0.347 | -0.303 | 0.4 | [-0.923, 0.584] | variance_restricted |
| `longtutor_evidence` Hallucination Check accuracy | `mathtutorbench_mistake_location` Mistake Location | P02(0.8/0.2) | 5 | -0.3 | -0.736 | 0.6833 | [-1.0, 1.0] | variance_restricted |
| `mmlu_pro` overall/category accuracy | `sas_bench` ECS error-cause consistency | P05(0.5/0.2), P06(0.2/0.2 异facet) | 5 | -0.3 | -0.126 | 0.6833 | [-1.0, 1.0] | variance_restricted |
| `agieval` overall/task/language/question_type accuracy | `edubench` basic_factual_accuracy (metric) | P05(0.2/0.2) | 6 | -0.257 | -0.537 | 0.6583 | [-0.935, 0.6] | variance_restricted |
| `agieval` overall/task/language/question_type accuracy | `sas_bench` ECS error-cause consistency | P05(0.2/0.2), P06(0.5/0.2 异facet) | 5 | -0.2 | 0.144 | 0.7833 | [-1.0, 0.875] | variance_restricted |
| `edubench` basic_factual_accuracy (metric) | `mmlu_pro` overall/category accuracy | P05(0.2/0.5) | 6 | -0.143 | -0.295 | 0.8028 | [-1.0, 0.636] | variance_restricted |
| `edubench` clarity_concision_inspiration (metric) | `mathtutorbench_scaffolding` Scaffolding | P16(0.2/0.2) | 7 | -0.107 | -0.598 | 0.8397 | [-0.961, 0.686] | variance_restricted |
| `edubench` clarity_concision_inspiration (metric) | `mathtutorbench_scaffolding_hard` Scaffolding hard | P16(0.2/0.2) | 7 | -0.107 | -0.598 | 0.8397 | [-0.961, 0.692] | variance_restricted |
| `edubench` scenario_element_integration (metric) | `mathtutorbench_pedagogy` Pedagogy IF | P14(0.2/0.5) | 7 | -0.107 | -0.084 | 0.8397 | [-0.961, 0.647] | variance_restricted |
| `edubench` error_identification_correction_accuracy (metric) | `mathtutorbench_mistake_correction` Mistake Correction | P10(0.2/0.2) | 5 | -0.1 | 0.105 | 0.95 | [-1.0, 1.0] | variance_restricted |
| `mathtutorbench_solution_correctness` Solution Correctness | `p07_selfcheck` two-round self-check (fix/break rate) | P07(0.2/0.8) | 5 | 0.0 | 0.649 | 1.0 | [-1.0, 1.0] | variance_restricted |
| `p07_selfcheck` two-round self-check (fix/break rate) | `p08_calibration` calibration composite (CWR/AUROC) | P07(0.8/0.2), P08(0.2/0.8) | 5 | 0.0 | 0.064 | 1.0 | [-0.875, 1.0] | variance_restricted |
| `edubench` personalized_adaptation_learning_support (metric) | `mathtutorbench_pedagogy` Pedagogy IF | P14(0.5/0.5) | 7 | 0.071 | 0.041 | 0.9063 | [-0.68, 0.698] | variance_restricted |
| `ceval` overall/category/subject accuracy | `sas_bench` ECS error-cause consistency | P05(0.5/0.2), P06(0.2/0.2 异facet) | 5 | 0.1 | 0.236 | 0.95 | [-1.0, 0.875] | variance_restricted |
| `edubench` scenario_element_integration (metric) | `mathtutorbench_pedagogy_hard` Pedagogy IF hard | P14(0.2/0.5) | 7 | 0.107 | 0.149 | 0.8397 | [-0.654, 0.962] | variance_restricted |
| `edubench` scenario_element_integration (metric) | `mathtutorbench_scaffolding` Scaffolding | P14(0.2/0.5) | 7 | 0.107 | 0.198 | 0.8397 | [-0.654, 0.963] | variance_restricted |
| `edubench` scenario_element_integration (metric) | `mathtutorbench_scaffolding_hard` Scaffolding hard | P14(0.2/0.5) | 7 | 0.107 | 0.198 | 0.8397 | [-0.68, 0.962] | variance_restricted |
| `ceval` overall/category/subject accuracy | `edubench` domain_knowledge_accuracy (metric) | P05(0.5/0.2) | 6 | 0.143 | -0.13 | 0.8028 | [-0.636, 1.0] | variance_restricted |
| `longtutor_evidence` Information Extraction accuracy | `mathtutorbench_mistake_location` Mistake Location | P02(0.8/0.2) | 5 | 0.2 | 0.263 | 0.7833 | [-0.875, 1.0] | variance_restricted |
| `edubench` personalized_adaptation_learning_support (metric) | `mathtutorbench_pedagogy_hard` Pedagogy IF hard | P14(0.5/0.5) | 7 | 0.214 | 0.178 | 0.6615 | [-0.647, 0.882] | variance_restricted |
| `edubench` clarity_concision_inspiration (metric) | `mathtutorbench_mistake_correction` Mistake Correction | P16(0.2/0.2) | 5 | 0.3 | 0.132 | 0.6833 | [-1.0, 1.0] | variance_restricted |
| `edubench` reasoning_process_rigor (metric) | `mathtutorbench_mistake_correction` Mistake Correction | P06(0.5/0.2) | 5 | 0.3 | — | 0.6833 | [-1.0, 1.0] | variance_restricted |
| `longtutor_evidence` Hallucination Check accuracy | `sas_bench` CCS step scoring consistency | P02(0.8/0.2) | 5 | 0.3 | 0.0 | 0.6833 | [-1.0, 1.0] | variance_restricted |
| `edubench` personalized_adaptation_learning_support (metric) | `mathtutorbench_scaffolding` Scaffolding | P14(0.5/0.5) | 7 | 0.357 | 0.315 | 0.4444 | [-0.608, 1.0] | variance_restricted |
| `edubench` personalized_adaptation_learning_support (metric) | `mathtutorbench_scaffolding_hard` Scaffolding hard | P14(0.5/0.5) | 7 | 0.357 | 0.315 | 0.4444 | [-0.593, 1.0] | variance_restricted |
| `edubench` domain_knowledge_accuracy (metric) | `mmlu_pro` overall/category accuracy | P05(0.2/0.5) | 6 | 0.371 | 0.122 | 0.4972 | [-0.742, 1.0] | variance_restricted |
| `agieval` overall/task/language/question_type accuracy | `mathtutorbench_problem_solving` Problem Solving | P05(0.2/0.2), P06(0.5/0.5) | 5 | 0.4 | -0.167 | 0.5167 | [-0.667, 1.0] | variance_restricted |
| `ceval` overall/category/subject accuracy | `mathtutorbench_problem_solving` Problem Solving | P05(0.5/0.2), P06(0.2/0.5) | 5 | 0.4 | -0.167 | 0.5167 | [-0.667, 1.0] | variance_restricted |
| `agieval` overall/task/language/question_type accuracy | `edubench` domain_knowledge_accuracy (metric) | P05(0.2/0.2) | 6 | 0.429 | -0.045 | 0.4194 | [-0.455, 1.0] | variance_restricted |
| `longtutor_evidence` Multi-session Reasoning accuracy | `mathtutorbench_mistake_location` Mistake Location | P02(0.8/0.2) | 5 | 0.5 | 0.435 | 0.45 | [-0.875, 1.0] | variance_restricted |
| `mathtutorbench_pedagogy` Pedagogy IF | `pedagogy_benchmark` CDPK teaching knowledge selection | P05(0.2/0.5), P14(0.5/0.8 异facet) | 5 | 0.5 | 0.435 | 0.45 | [-0.667, 1.0] | variance_restricted |
| `mathtutorbench_solution_correctness` Solution Correctness | `p08_calibration` calibration composite (CWR/AUROC) | P07(0.2/0.2) | 5 | 0.5 | 0.749 | 0.45 | [-0.667, 1.0] | variance_restricted |
| `edubench` basic_factual_accuracy (metric) | `mathtutorbench_problem_solving` Problem Solving | P05(0.2/0.2) | 5 | 0.6 | 0.919 | 0.35 | [-0.667, 1.0] | variance_restricted |
| `edubench` higher_order_thinking_ability_development (metric) | `mathtutorbench_mistake_correction` Mistake Correction | P06(0.2/0.2), P16(0.2/0.2) | 5 | 0.6 | 0.794 | 0.35 | [-1.0, 1.0] | variance_restricted |
| `edubench` higher_order_thinking_ability_development (metric) | `mathtutorbench_pedagogy` Pedagogy IF | P16(0.2/0.2) | 7 | 0.607 | 0.821 | 0.1667 | [-0.074, 1.0] | variance_restricted |
| `longtutor_evidence` Information Extraction accuracy | `sas_bench` CCS step scoring consistency | P02(0.8/0.2) | 5 | 0.7 | 0.87 | 0.2333 | [-0.25, 1.0] | variance_restricted |
| `longtutor_teaching` judge dims: strategy_alignment + history_utilization (1-5) | `mathtutorbench_pedagogy` Pedagogy IF | P14(0.2/0.5) | 5 | 0.7 | 0.875 | 0.2333 | [-0.25, 1.0] | variance_restricted |
| `mathtutorbench_mistake_location` Mistake Location | `sas_bench` CCS step scoring consistency | P02(0.2/0.2), P10(0.8/0.2) | 5 | 0.7 | 0.63 | 0.2333 | [-0.25, 1.0] | variance_restricted |
| `mathtutorbench_problem_solving` Problem Solving | `mmlu_pro` overall/category accuracy | P05(0.2/0.5), P06(0.5/0.2) | 5 | 0.7 | 0.459 | 0.2333 | [-0.25, 1.0] | variance_restricted |
| `ceval` overall/category/subject accuracy | `mmlu_pro` overall/category accuracy | P05(0.5/0.5), P06(0.2/0.2) | 6 | 0.771 | 0.753 | 0.1028 | [-0.032, 1.0] | variance_restricted |
| `agieval` overall/task/language/question_type accuracy | `mmlu_pro` overall/category accuracy | P05(0.2/0.5), P06(0.5/0.2) | 6 | 0.829 | 0.804 | 0.0583 | [0.091, 1.0] | variance_restricted |
| `edubench` domain_knowledge_accuracy (metric) | `mathtutorbench_problem_solving` Problem Solving | P05(0.2/0.2) | 5 | 0.9 | 0.84 | 0.0833 | [0.25, 1.0] | variance_restricted |
| `longtutor_evidence` Multi-session Reasoning accuracy | `sas_bench` CCS step scoring consistency | P02(0.8/0.2) | 5 | 0.9 | 0.908 | 0.0833 | [0.25, 1.0] | variance_restricted |
| `mathtutorbench_scaffolding` Scaffolding | `pedagogy_benchmark` SEND special education needs selection | P05(0.2/0.5), P14(0.5/0.5 异facet) | 5 | 0.9 | 0.982 | 0.0833 | [0.25, 1.0] | variance_restricted |
| `mathtutorbench_scaffolding_hard` Scaffolding hard | `pedagogy_benchmark` SEND special education needs selection | P05(0.2/0.5), P14(0.5/0.5 异facet) | 5 | 0.9 | 0.982 | 0.0833 | [0.25, 1.0] | variance_restricted |
| `agieval` overall/task/language/question_type accuracy | `ceval` overall/category/subject accuracy | P05(0.2/0.5), P06(0.5/0.2) | 6 | 0.943 | 0.99 | 0.0167 | [0.515, 1.0] | variance_restricted |
| `mathtutorbench_pedagogy` Pedagogy IF | `pedagogy_benchmark` SEND special education needs selection | P05(0.2/0.5), P14(0.5/0.5 异facet) | 5 | 1.0 | 1.0 | 0.0167 | [1.0, 1.0] | variance_restricted |
| `mathtutorbench_pedagogy_hard` Pedagogy IF hard | `pedagogy_benchmark` SEND special education needs selection | P05(0.2/0.5), P14(0.5/0.5 异facet) | 5 | 1.0 | 1.0 | 0.0167 | [1.0, 1.0] | variance_restricted |

## 区分效度（同 P 收敛配对 vs 不共享 P 的 baseline）

- 收敛配对（跨家族、非受限、n≥5）：15 对，mean ρ = 0.288，median = 0.3
- baseline（不共享任何 P）：68 对，mean ρ = 0.104，median = 0.068
- 差值 = 0.184，单侧 permutation p = 0.0848（配对之间共享格子、非独立；p 值仅供参考，结论以红旗/非红旗为主。）

若差值不显著为正，说明 P 划分对'哪些 benchmark 相关'没有预测力，映射层需整体重审。

## 家族方法方差（halo）

| 家族 | 家族内配对数 | 家族内 mean ρ | 跨家族配对数 | 跨家族 mean ρ | halo 分 | 家族内先聚合? |
|---|---:|---:|---:|---:|---:|---|
| `pedagogy_benchmark` | 1 | 0.77 | 52 | 0.21 | 0.56 | 是 |
| `eduguard` | 3 | 0.357 | 74 | -0.086 | 0.443 | 否 |
| `edubench` | 66 | 0.349 | 384 | 0.018 | 0.33 | 否 |
| `p08` | 1 | 0.6 | 66 | 0.315 | 0.285 | 否 |
| `mathtutorbench` | 27 | 0.548 | 238 | 0.272 | 0.276 | 否 |
| `sas_bench` | 3 | 0.413 | 108 | 0.155 | 0.258 | 否 |
| `longtutor_evidence` | 3 | 0.533 | 96 | 0.3 | 0.233 | 否 |

halo 分 > 0.5 的家族：多子维度在 P 聚合前先合成一票（计划 §2.6）。

## P × 格子评级汇总

评级分布：validated=4、flagged=4、provisional=12、variance_restricted=59、insufficient_evidence=19、single_source=6

| P | 类型 | facet | Benchmark | Subdimension | 权重 | 评级 |
|---|---|---|---|---|---:|---|
| P01 指令与约束遵循 | reflective | core | `ifeval` | prompt-level strict accuracy | 1.0 | **variance_restricted** |
| P02 长上下文与证据定位 | reflective | core | `longtutor_evidence` | Hallucination Check accuracy | 0.8 | **insufficient_evidence** |
| P02 长上下文与证据定位 | reflective | core | `longtutor_evidence` | Information Extraction accuracy | 0.8 | **variance_restricted** |
| P02 长上下文与证据定位 | reflective | core | `longtutor_evidence` | Multi-session Reasoning accuracy | 0.8 | **variance_restricted** |
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
| P05 知识调用与掌握 | formative | subject_knowledge | `olympiadbench` | overall/subject/language/modality accuracy | 0.2 | **insufficient_evidence** |
| P05 知识调用与掌握 | formative | subject_knowledge | `sas_bench` | ECS error-cause consistency | 0.2 | **insufficient_evidence** |
| P05 知识调用与掌握 | formative | pedagogical_knowledge | `mathtutorbench_pedagogy_hard` | Pedagogy IF hard | 0.2 | **provisional** |
| P05 知识调用与掌握 | formative | pedagogical_knowledge | `mathtutorbench_scaffolding` | Scaffolding | 0.2 | **provisional** |
| P05 知识调用与掌握 | formative | pedagogical_knowledge | `mathtutorbench_scaffolding_hard` | Scaffolding hard | 0.2 | **provisional** |
| P05 知识调用与掌握 | formative | pedagogical_knowledge | `pedagogy_benchmark` | CDPK teaching knowledge selection | 0.5 | **provisional** |
| P05 知识调用与掌握 | formative | subject_knowledge | `agieval` | overall/task/language/question_type accuracy | 0.2 | **variance_restricted** |
| P05 知识调用与掌握 | formative | subject_knowledge | `ceval` | overall/category/subject accuracy | 0.5 | **variance_restricted** |
| P05 知识调用与掌握 | formative | subject_knowledge | `edubench` | basic_factual_accuracy (metric) | 0.2 | **variance_restricted** |
| P05 知识调用与掌握 | formative | subject_knowledge | `edubench` | domain_knowledge_accuracy (metric) | 0.2 | **variance_restricted** |
| P05 知识调用与掌握 | formative | pedagogical_knowledge | `mathtutorbench_pedagogy` | Pedagogy IF | 0.2 | **variance_restricted** |
| P05 知识调用与掌握 | formative | subject_knowledge | `mathtutorbench_problem_solving` | Problem Solving | 0.2 | **variance_restricted** |
| P05 知识调用与掌握 | formative | subject_knowledge | `mathvista` | task/question_type/answer_type accuracy | 0.2 | **variance_restricted** |
| P05 知识调用与掌握 | formative | subject_knowledge | `mmlu_pro` | overall/category accuracy | 0.5 | **variance_restricted** |
| P05 知识调用与掌握 | formative | pedagogical_knowledge | `pedagogy_benchmark` | SEND special education needs selection | 0.5 | **variance_restricted** |
| P06 推理与生成 | formative | generative_reasoning | `edubench` | higher_order_thinking_ability_development (metric) | 0.2 | **flagged** |
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
| P07 自我校验与修正 | reflective | core | `mathtutorbench_solution_correctness` | Solution Correctness | 0.2 | **variance_restricted** |
| P07 自我校验与修正 | reflective | core | `p07_selfcheck` | two-round self-check (fix/break rate) | 0.8 | **variance_restricted** |
| P07 自我校验与修正 | reflective | core | `p08_calibration` | calibration composite (CWR/AUROC) | 0.2 | **variance_restricted** |
| P08 置信度校准与弃答 | formative | calibration | `p07_selfcheck` | two-round self-check (fix/break rate) | 0.2 | **variance_restricted** |
| P08 置信度校准与弃答 | formative | abstention | `p08_abstention` | balanced abstention score | 0.8 | **variance_restricted** |
| P08 置信度校准与弃答 | formative | calibration | `p08_calibration` | calibration composite (CWR/AUROC) | 0.8 | **variance_restricted** |
| P10 错误诊断 | formative | error_attribution | `edubench` | error_identification_correction_accuracy (metric) | 0.2 | **flagged** |
| P10 错误诊断 | formative | error_attribution | `bea2025_tutor` | dimension: Mistake_Identification | 0.2 | **insufficient_evidence** |
| P10 错误诊断 | formative | error_attribution | `longtutor_diagnosis` | four-category knowledge-state diagnosis macro-F1 | 0.2 | **validated** |
| P10 错误诊断 | formative | error_attribution | `sas_bench` | ECS error-cause consistency | 0.8 | **validated** |
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
| P13 学习者画像建模 | formative | support_needs | `edubench` | personalized_adaptation_learning_support (metric) | 0.2 | **variance_restricted** |
| P13 学习者画像建模 | formative | support_needs | `pedagogy_benchmark` | SEND special education needs selection | 0.2 | **variance_restricted** |
| P14 个性化教学策略选择 | formative | strategy_enactment | `mmtutorbench` | multimodal tutor score | 0.2 | **insufficient_evidence** |
| P14 个性化教学策略选择 | formative | strategy_formulation | `pedagogy_benchmark` | CDPK teaching knowledge selection | 0.8 | **insufficient_evidence** |
| P14 个性化教学策略选择 | formative | strategy_enactment | `mathtutorbench_scaffolding` | Scaffolding | 0.5 | **provisional** |
| P14 个性化教学策略选择 | formative | strategy_enactment | `mathtutorbench_scaffolding_hard` | Scaffolding hard | 0.5 | **provisional** |
| P14 个性化教学策略选择 | formative | strategy_enactment | `longtutor_teaching` | judge dims: strategy_alignment + history_utilization (1-5) | 0.2 | **validated** |
| P14 个性化教学策略选择 | formative | strategy_enactment | `mathtutorbench_pedagogy_hard` | Pedagogy IF hard | 0.5 | **validated** |
| P14 个性化教学策略选择 | formative | strategy_enactment | `bea2025_tutor` | dimension: Providing_Guidance | 0.2 | **variance_restricted** |
| P14 个性化教学策略选择 | formative | strategy_enactment | `edubench` | personalized_adaptation_learning_support (metric) | 0.5 | **variance_restricted** |
| P14 个性化教学策略选择 | formative | strategy_enactment | `edubench` | scenario_element_integration (metric) | 0.2 | **variance_restricted** |
| P14 个性化教学策略选择 | formative | strategy_enactment | `mathtutorbench_pedagogy` | Pedagogy IF | 0.5 | **variance_restricted** |
| P14 个性化教学策略选择 | formative | strategy_enactment | `mathtutorbench_socratic` | Socratic Questioning | 0.5 | **variance_restricted** |
| P14 个性化教学策略选择 | formative | strategy_enactment | `mrbench_tutor` | dimension: Providing_Guidance | 0.2 | **variance_restricted** |
| P14 个性化教学策略选择 | formative | strategy_formulation | `pedagogy_benchmark` | SEND special education needs selection | 0.5 | **variance_restricted** |
| P14 个性化教学策略选择 | formative | strategy_enactment | `tutorbench` | Fair815 multimodal tutor quality | 0.2 | **variance_restricted** |
| P15 学习路径规划（知识结构层） | reflective | core | `mooccube_prereq` | chance-corrected composite (先修选择 + 学习顺序排序) | 0.8 | **single_source** |
| P16 适配性解释与反馈生成 | formative | artifact_generation | `edubench` | TMG/PCC × clarity_concision_inspiration + scenario_element_integration (task×metric) | 0.5 | **insufficient_evidence** |
| P16 适配性解释与反馈生成 | formative | content_feedback | `mmtutorbench` | multimodal tutor score | 0.5 | **insufficient_evidence** |
| P16 适配性解释与反馈生成 | formative | content_feedback | `edubench` | higher_order_thinking_ability_development (metric) | 0.2 | **provisional** |
| P16 适配性解释与反馈生成 | formative | content_feedback | `mathtutorbench_pedagogy_hard` | Pedagogy IF hard | 0.2 | **provisional** |
| P16 适配性解释与反馈生成 | formative | content_feedback | `mathtutorbench_scaffolding` | Scaffolding | 0.2 | **provisional** |
| P16 适配性解释与反馈生成 | formative | content_feedback | `mathtutorbench_scaffolding_hard` | Scaffolding hard | 0.2 | **provisional** |
| P16 适配性解释与反馈生成 | formative | content_feedback | `bea2025_tutor` | dimension: Actionability | 0.2 | **variance_restricted** |
| P16 适配性解释与反馈生成 | formative | content_feedback | `edubench` | clarity_concision_inspiration (metric) | 0.2 | **variance_restricted** |
| P16 适配性解释与反馈生成 | formative | tone_support | `edubench` | motivation_guidance_positive_feedback (metric) | 0.5 | **variance_restricted** |
| P16 适配性解释与反馈生成 | formative | artifact_generation | `eduillustrate` | 8-dim 0-5 visual explanation score | 0.2 | **variance_restricted** |
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
| `bea2025_tutor` dimension: Mistake_Identification | `edubench` error_identification_correction_accuracy (metric) | P10(0.2/0.2) | 3 | -1.0 |
| `bea2025_tutor` dimension: Providing_Guidance | `edubench` scenario_element_integration (metric) | P14(0.2/0.2) | 3 | -1.0 |
| `edubench` error_identification_correction_accuracy (metric) | `mrbench_tutor` dimension: Mistake_Identification | P10(0.2/0.2) | 3 | -1.0 |
| `edubench` motivation_guidance_positive_feedback (metric) | `mrbench_tutor` dimension: Tutor_Tone (encouraging share) | P16(0.5/0.2) | 3 | -1.0 |
| `mathtutorbench_problem_solving` Problem Solving | `olympiadbench` overall/subject/language/modality accuracy | P05(0.2/0.2), P06(0.5/0.5) | 3 | -1.0 |
| `edubench` basic_factual_accuracy (metric) | `olympiadbench` overall/subject/language/modality accuracy | P05(0.2/0.2) | 4 | -0.8 |
| `edubench` scenario_element_integration (metric) | `mathtutorbench_socratic` Socratic Questioning | P14(0.2/0.5) | 4 | -0.8 |
| `bea2025_tutor` dimension: Providing_Guidance | `edubench` personalized_adaptation_learning_support (metric) | P14(0.2/0.5) | 3 | -0.5 |
| `edubench` scenario_element_integration (metric) | `mrbench_tutor` dimension: Providing_Guidance | P14(0.2/0.2) | 3 | -0.5 |
| `asap_2` essay holistic QWK | `sas_bench` QWK holistic total score | P11(0.8/0.8) | 4 | -0.4 |
| `edubench` domain_knowledge_accuracy (metric) | `olympiadbench` overall/subject/language/modality accuracy | P05(0.2/0.2) | 4 | -0.4 |
| `mathtutorbench_mistake_correction` Mistake Correction | `sas_bench` ECS error-cause consistency | P06(0.2/0.2), P10(0.2/0.8) | 4 | -0.4 |
| `mmlu_pro` overall/category accuracy | `olympiadbench` overall/subject/language/modality accuracy | P05(0.5/0.2), P06(0.2/0.5) | 4 | -0.4 |
| `mrbench_judge` 8-dimension tutor response judging | `sas_bench` CCS step scoring consistency | P11(0.5/0.5) | 4 | -0.4 |
| `mathtutorbench_problem_solving` Problem Solving | `sas_bench` ECS error-cause consistency | P05(0.2/0.2), P06(0.5/0.2 异facet) | 4 | -0.2 |
| `edubench` clarity_concision_inspiration (metric) | `mrbench_tutor` dimension: Actionability | P16(0.2/0.2) | 3 | 0.0 |
| `edubench` personalized_adaptation_learning_support (metric) | `mathtutorbench_socratic` Socratic Questioning | P14(0.5/0.5) | 4 | 0.2 |
| `longtutor_teaching` judge dims: strategy_alignment + history_utilization (1-5) | `mathtutorbench_socratic` Socratic Questioning | P14(0.2/0.5) | 4 | 0.2 |
| `olympiadbench` overall/subject/language/modality accuracy | `sas_bench` ECS error-cause consistency | P05(0.2/0.2), P06(0.5/0.2 异facet) | 4 | 0.2 |
| `agieval` overall/task/language/question_type accuracy | `olympiadbench` overall/subject/language/modality accuracy | P05(0.2/0.2), P06(0.5/0.5) | 4 | 0.4 |
| `edubench` clarity_concision_inspiration (metric) | `mathtutorbench_socratic` Socratic Questioning | P16(0.2/0.2) | 4 | 0.4 |
| `longtutor_diagnosis` four-category knowledge-state diagnosis macro-F1 | `mathtutorbench_mistake_correction` Mistake Correction | P10(0.2/0.2) | 4 | 0.4 |
| `bea2025_tutor` dimension: Actionability | `edubench` clarity_concision_inspiration (metric) | P16(0.2/0.2) | 3 | 0.5 |
| `bea2025_tutor` dimension: Mistake_Identification | `mathtutorbench_mistake_correction` Mistake Correction | P10(0.2/0.2) | 3 | 0.5 |
| `bea2025_tutor` dimension: Mistake_Identification | `sas_bench` ECS error-cause consistency | P10(0.2/0.8) | 3 | 0.5 |
| `bea2025_tutor` dimension: Providing_Guidance | `mathtutorbench_pedagogy` Pedagogy IF | P14(0.2/0.5) | 3 | 0.5 |
| `bea2025_tutor` dimension: Providing_Guidance | `mathtutorbench_pedagogy_hard` Pedagogy IF hard | P14(0.2/0.5) | 3 | 0.5 |
| `bea2025_tutor` dimension: Providing_Guidance | `mathtutorbench_scaffolding` Scaffolding | P14(0.2/0.5) | 3 | 0.5 |
| `bea2025_tutor` dimension: Providing_Guidance | `mathtutorbench_scaffolding_hard` Scaffolding hard | P14(0.2/0.5) | 3 | 0.5 |
| `bea2025_tutor` dimension: Providing_Guidance | `mathtutorbench_socratic` Socratic Questioning | P14(0.2/0.5) | 3 | 0.5 |
| `bea2025_tutor` dimension: Providing_Guidance | `mrbench_tutor` dimension: Providing_Guidance | P14(0.2/0.2) | 3 | 0.5 |
| `edubench` personalized_adaptation_learning_support (metric) | `mrbench_tutor` dimension: Providing_Guidance | P14(0.5/0.2) | 3 | 0.5 |
| `longtutor_teaching` judge dims: strategy_alignment + history_utilization (1-5) | `mrbench_tutor` dimension: Providing_Guidance | P14(0.2/0.2) | 3 | 0.5 |
| `mathtutorbench_mistake_correction` Mistake Correction | `mrbench_tutor` dimension: Mistake_Identification | P10(0.2/0.2) | 3 | 0.5 |
| `mrbench_tutor` dimension: Mistake_Identification | `sas_bench` ECS error-cause consistency | P10(0.2/0.8) | 3 | 0.5 |
| `bea2025_judge` judge labels: mistake/guidance/actionability | `sas_bench` CCS step scoring consistency | P11(0.5/0.5) | 4 | 0.8 |
| `ceval` overall/category/subject accuracy | `olympiadbench` overall/subject/language/modality accuracy | P05(0.5/0.2), P06(0.2/0.5) | 4 | 0.8 |
| `bea2025_tutor` dimension: Actionability | `mrbench_tutor` dimension: Actionability | P16(0.2/0.2) | 3 | 0.866 |
| `edubench` higher_order_thinking_ability_development (metric) | `mrbench_tutor` dimension: Actionability | P16(0.2/0.2) | 3 | 0.866 |
| `mathtutorbench_mistake_correction` Mistake Correction | `mrbench_tutor` dimension: Actionability | P16(0.2/0.2) | 3 | 0.866 |
| `mathtutorbench_pedagogy` Pedagogy IF | `mrbench_tutor` dimension: Actionability | P16(0.2/0.2) | 3 | 0.866 |
| `mathtutorbench_pedagogy_hard` Pedagogy IF hard | `mrbench_tutor` dimension: Actionability | P16(0.2/0.2) | 3 | 0.866 |
| `mathtutorbench_scaffolding` Scaffolding | `mrbench_tutor` dimension: Actionability | P16(0.2/0.2) | 3 | 0.866 |
| `mathtutorbench_scaffolding_hard` Scaffolding hard | `mrbench_tutor` dimension: Actionability | P16(0.2/0.2) | 3 | 0.866 |
| `mathtutorbench_socratic` Socratic Questioning | `mrbench_tutor` dimension: Actionability | P16(0.2/0.2) | 3 | 0.866 |
| `bea2025_tutor` dimension: Actionability | `edubench` higher_order_thinking_ability_development (metric) | P16(0.2/0.2) | 3 | 1.0 |
| `bea2025_tutor` dimension: Actionability | `mathtutorbench_mistake_correction` Mistake Correction | P16(0.2/0.2) | 3 | 1.0 |
| `bea2025_tutor` dimension: Actionability | `mathtutorbench_pedagogy` Pedagogy IF | P16(0.2/0.2) | 3 | 1.0 |
| `bea2025_tutor` dimension: Actionability | `mathtutorbench_pedagogy_hard` Pedagogy IF hard | P16(0.2/0.2) | 3 | 1.0 |
| `bea2025_tutor` dimension: Actionability | `mathtutorbench_scaffolding` Scaffolding | P16(0.2/0.2) | 3 | 1.0 |
| `bea2025_tutor` dimension: Actionability | `mathtutorbench_scaffolding_hard` Scaffolding hard | P16(0.2/0.2) | 3 | 1.0 |
| `bea2025_tutor` dimension: Actionability | `mathtutorbench_socratic` Socratic Questioning | P16(0.2/0.2) | 3 | 1.0 |
| `bea2025_tutor` dimension: Mistake_Identification | `longtutor_diagnosis` four-category knowledge-state diagnosis macro-F1 | P10(0.2/0.2) | 3 | 1.0 |
| `bea2025_tutor` dimension: Mistake_Identification | `mrbench_tutor` dimension: Mistake_Identification | P10(0.2/0.2) | 3 | 1.0 |
| `bea2025_tutor` dimension: Providing_Guidance | `longtutor_teaching` judge dims: strategy_alignment + history_utilization (1-5) | P14(0.2/0.2) | 3 | 1.0 |
| `edubench` TMG/PCC × clarity_concision_inspiration + scenario_element_integration (task×metric) | `eduillustrate` 8-dim 0-5 visual explanation score | P16(0.5/0.2) | 3 | 1.0 |
| `edubench` higher_order_thinking_ability_development (metric) | `mathtutorbench_socratic` Socratic Questioning | P16(0.2/0.2) | 4 | 1.0 |
| `longtutor_diagnosis` four-category knowledge-state diagnosis macro-F1 | `mrbench_tutor` dimension: Mistake_Identification | P10(0.2/0.2) | 3 | 1.0 |
| `mathtutorbench_pedagogy` Pedagogy IF | `mrbench_tutor` dimension: Providing_Guidance | P14(0.5/0.2) | 3 | 1.0 |
| `mathtutorbench_pedagogy_hard` Pedagogy IF hard | `mrbench_tutor` dimension: Providing_Guidance | P14(0.5/0.2) | 3 | 1.0 |
| `mathtutorbench_scaffolding` Scaffolding | `mrbench_tutor` dimension: Providing_Guidance | P14(0.5/0.2) | 3 | 1.0 |
| `mathtutorbench_scaffolding_hard` Scaffolding hard | `mrbench_tutor` dimension: Providing_Guidance | P14(0.5/0.2) | 3 | 1.0 |
| `mathtutorbench_socratic` Socratic Questioning | `mrbench_tutor` dimension: Providing_Guidance | P14(0.5/0.2) | 3 | 1.0 |

## 形成型跨 facet 配对（facet_distinct_expected，信息呈现，不触发红旗）

| A | B | 共享 P | n | ρ |
|---|---|---|---:|---:|
| `edubench` basic_factual_accuracy (metric) | `pedagogy_benchmark` SEND special education needs selection | P05(0.2/0.5 异facet) | 8 | -0.647 |
| `edubench` personalized_adaptation_learning_support (metric) | `longtutor_diagnosis` four-category knowledge-state diagnosis macro-F1 | P13(0.2/0.8 异facet) | 5 | -0.6 |
| `edubench` basic_factual_accuracy (metric) | `mathtutorbench_pedagogy_hard` Pedagogy IF hard | P05(0.2/0.2 异facet) | 7 | -0.571 |
| `edubench` basic_factual_accuracy (metric) | `mathtutorbench_pedagogy` Pedagogy IF | P05(0.2/0.2 异facet) | 7 | -0.5 |
| `edubench` error_identification_correction_accuracy (metric) | `mathtutorbench_mistake_location` Mistake Location | P10(0.2/0.8 异facet) | 6 | -0.314 |
| `longtutor_diagnosis` four-category knowledge-state diagnosis macro-F1 | `mathtutorbench_mistake_location` Mistake Location | P10(0.2/0.8 异facet) | 5 | -0.3 |
| `mathtutorbench_mistake_location` Mistake Location | `sas_bench` ECS error-cause consistency | P10(0.8/0.8 异facet) | 5 | -0.3 |
| `mathtutorbench_scaffolding` Scaffolding | `sas_bench` ECS error-cause consistency | P05(0.2/0.2 异facet) | 5 | -0.3 |
| `mathtutorbench_scaffolding_hard` Scaffolding hard | `sas_bench` ECS error-cause consistency | P05(0.2/0.2 异facet) | 5 | -0.3 |
| `mathtutorbench_solution_correctness` Solution Correctness | `sas_bench` ECS error-cause consistency | P10(0.5/0.8 异facet) | 5 | -0.3 |
| `edubench` basic_factual_accuracy (metric) | `mathtutorbench_scaffolding` Scaffolding | P05(0.2/0.2 异facet) | 7 | -0.286 |
| `edubench` basic_factual_accuracy (metric) | `mathtutorbench_scaffolding_hard` Scaffolding hard | P05(0.2/0.2 异facet) | 7 | -0.286 |
| `edubench` basic_factual_accuracy (metric) | `pedagogy_benchmark` CDPK teaching knowledge selection | P05(0.2/0.5 异facet) | 8 | -0.286 |
| `mathtutorbench_pedagogy` Pedagogy IF | `sas_bench` ECS error-cause consistency | P05(0.2/0.2 异facet) | 5 | -0.2 |
| `edubench` domain_knowledge_accuracy (metric) | `pedagogy_benchmark` SEND special education needs selection | P05(0.2/0.5 异facet) | 8 | -0.192 |
| `edubench` personalized_adaptation_learning_support (metric) | `pedagogy_benchmark` CDPK teaching knowledge selection | P14(0.5/0.8 异facet) | 8 | -0.19 |
| `edubench` error_identification_correction_accuracy (metric) | `sas_bench` CCS step scoring consistency | P10(0.2/0.2 异facet) | 7 | -0.179 |
| `edubench` motivation_guidance_positive_feedback (metric) | `mathtutorbench_pedagogy` Pedagogy IF | P16(0.5/0.2 异facet) | 7 | -0.179 |
| `edubench` error_identification_correction_accuracy (metric) | `mathtutorbench_solution_correctness` Solution Correctness | P10(0.2/0.5 异facet) | 6 | -0.086 |
| `edubench` TMG/PCC × clarity_concision_inspiration + scenario_element_integration (task×metric) | `mathtutorbench_pedagogy_hard` Pedagogy IF hard | P16(0.5/0.2 异facet) | 7 | 0.0 |
| `longtutor_diagnosis` four-category knowledge-state diagnosis macro-F1 | `mathtutorbench_solution_correctness` Solution Correctness | P10(0.2/0.5 异facet) | 5 | 0.0 |
| `edubench` TMG/PCC × clarity_concision_inspiration + scenario_element_integration (task×metric) | `mathtutorbench_scaffolding` Scaffolding | P16(0.5/0.2 异facet) | 7 | 0.036 |
| `edubench` TMG/PCC × clarity_concision_inspiration + scenario_element_integration (task×metric) | `mathtutorbench_scaffolding_hard` Scaffolding hard | P16(0.5/0.2 异facet) | 7 | 0.036 |
| `edubench` domain_knowledge_accuracy (metric) | `mathtutorbench_pedagogy_hard` Pedagogy IF hard | P05(0.2/0.2 异facet) | 7 | 0.071 |
| `edubench` domain_knowledge_accuracy (metric) | `pedagogy_benchmark` CDPK teaching knowledge selection | P05(0.2/0.5 异facet) | 8 | 0.095 |
| `mathtutorbench_pedagogy_hard` Pedagogy IF hard | `sas_bench` ECS error-cause consistency | P05(0.2/0.2 异facet) | 5 | 0.1 |
| `edubench` motivation_guidance_positive_feedback (metric) | `mathtutorbench_pedagogy_hard` Pedagogy IF hard | P16(0.5/0.2 异facet) | 7 | 0.107 |
| `edubench` scenario_element_integration (metric) | `pedagogy_benchmark` SEND special education needs selection | P14(0.2/0.5 异facet) | 8 | 0.18 |
| `edubench` TMG/PCC × clarity_concision_inspiration + scenario_element_integration (task×metric) | `mathtutorbench_mistake_correction` Mistake Correction | P16(0.5/0.2 异facet) | 5 | 0.2 |
| `edubench` TMG/PCC × clarity_concision_inspiration + scenario_element_integration (task×metric) | `mathtutorbench_pedagogy` Pedagogy IF | P16(0.5/0.2 异facet) | 7 | 0.214 |
| `edubench` domain_knowledge_accuracy (metric) | `mathtutorbench_pedagogy` Pedagogy IF | P05(0.2/0.2 异facet) | 7 | 0.214 |
| `edubench` scenario_element_integration (metric) | `pedagogy_benchmark` CDPK teaching knowledge selection | P14(0.2/0.8 异facet) | 8 | 0.214 |
| `pedagogy_benchmark` CDPK teaching knowledge selection | `sas_bench` ECS error-cause consistency | P05(0.5/0.2 异facet) | 7 | 0.214 |
| `edubench` domain_knowledge_accuracy (metric) | `mathtutorbench_scaffolding` Scaffolding | P05(0.2/0.2 异facet) | 7 | 0.25 |
| `edubench` domain_knowledge_accuracy (metric) | `mathtutorbench_scaffolding_hard` Scaffolding hard | P05(0.2/0.2 异facet) | 7 | 0.25 |
| `edubench` reasoning_process_rigor (metric) | `mmlu_pro` overall/category accuracy | P06(0.5/0.2 异facet) | 6 | 0.257 |
| `edubench` higher_order_thinking_ability_development (metric) | `mathtutorbench_problem_solving` Problem Solving | P06(0.2/0.5 异facet) | 5 | 0.3 |
| `edubench` reasoning_process_rigor (metric) | `mathtutorbench_problem_solving` Problem Solving | P06(0.5/0.5 异facet) | 5 | 0.3 |
| `longtutor_diagnosis` four-category knowledge-state diagnosis macro-F1 | `sas_bench` CCS step scoring consistency | P10(0.2/0.2 异facet) | 5 | 0.3 |
| `edubench` motivation_guidance_positive_feedback (metric) | `mathtutorbench_scaffolding` Scaffolding | P16(0.5/0.2 异facet) | 7 | 0.357 |
| `edubench` motivation_guidance_positive_feedback (metric) | `mathtutorbench_scaffolding_hard` Scaffolding hard | P16(0.5/0.2 异facet) | 7 | 0.357 |
| `ceval` overall/category/subject accuracy | `edubench` reasoning_process_rigor (metric) | P06(0.2/0.5 异facet) | 6 | 0.371 |
| `edubench` motivation_guidance_positive_feedback (metric) | `mathtutorbench_mistake_correction` Mistake Correction | P16(0.5/0.2 异facet) | 5 | 0.4 |
| `edubench` higher_order_thinking_ability_development (metric) | `mmlu_pro` overall/category accuracy | P06(0.2/0.2 异facet) | 6 | 0.486 |
| `agieval` overall/task/language/question_type accuracy | `edubench` reasoning_process_rigor (metric) | P06(0.5/0.5 异facet) | 6 | 0.6 |
| `ceval` overall/category/subject accuracy | `edubench` higher_order_thinking_ability_development (metric) | P06(0.2/0.2 异facet) | 6 | 0.6 |
| `mmlu_pro` overall/category accuracy | `pedagogy_benchmark` CDPK teaching knowledge selection | P05(0.5/0.5 异facet) | 5 | 0.6 |
| `p07_selfcheck` two-round self-check (fix/break rate) | `p08_abstention` balanced abstention score | P08(0.2/0.8 异facet) | 5 | 0.6 |
| `mathtutorbench_solution_correctness` Solution Correctness | `sas_bench` CCS step scoring consistency | P10(0.5/0.2 异facet) | 5 | 0.7 |
| `ceval` overall/category/subject accuracy | `mathtutorbench_scaffolding` Scaffolding | P05(0.5/0.2 异facet) | 6 | 0.714 |
| `ceval` overall/category/subject accuracy | `mathtutorbench_scaffolding_hard` Scaffolding hard | P05(0.5/0.2 异facet) | 6 | 0.714 |
| `mathtutorbench_pedagogy_hard` Pedagogy IF hard | `mmlu_pro` overall/category accuracy | P05(0.2/0.5 异facet) | 6 | 0.714 |
| `pedagogy_benchmark` SEND special education needs selection | `sas_bench` ECS error-cause consistency | P05(0.5/0.2 异facet) | 7 | 0.75 |
| `agieval` overall/task/language/question_type accuracy | `edubench` higher_order_thinking_ability_development (metric) | P06(0.5/0.2 异facet) | 6 | 0.771 |
| `agieval` overall/task/language/question_type accuracy | `mathtutorbench_scaffolding` Scaffolding | P05(0.2/0.2 异facet) | 6 | 0.771 |
| `agieval` overall/task/language/question_type accuracy | `mathtutorbench_scaffolding_hard` Scaffolding hard | P05(0.2/0.2 异facet) | 6 | 0.771 |
| `mathtutorbench_pedagogy` Pedagogy IF | `mmlu_pro` overall/category accuracy | P05(0.2/0.5 异facet) | 6 | 0.771 |
| `agieval` overall/task/language/question_type accuracy | `pedagogy_benchmark` CDPK teaching knowledge selection | P05(0.2/0.5 异facet) | 5 | 0.8 |
| `ceval` overall/category/subject accuracy | `pedagogy_benchmark` CDPK teaching knowledge selection | P05(0.5/0.5 异facet) | 5 | 0.8 |
| `mmlu_pro` overall/category accuracy | `pedagogy_benchmark` SEND special education needs selection | P05(0.5/0.5 异facet) | 5 | 0.8 |
| `agieval` overall/task/language/question_type accuracy | `mathtutorbench_pedagogy_hard` Pedagogy IF hard | P05(0.2/0.2 异facet) | 6 | 0.886 |
| `ceval` overall/category/subject accuracy | `mathtutorbench_pedagogy` Pedagogy IF | P05(0.5/0.2 异facet) | 6 | 0.886 |
| `agieval` overall/task/language/question_type accuracy | `pedagogy_benchmark` SEND special education needs selection | P05(0.2/0.5 异facet) | 5 | 0.9 |
| `ceval` overall/category/subject accuracy | `mathtutorbench_mistake_correction` Mistake Correction | P06(0.2/0.2 异facet) | 5 | 0.9 |
| `ceval` overall/category/subject accuracy | `pedagogy_benchmark` SEND special education needs selection | P05(0.5/0.5 异facet) | 5 | 0.9 |
| `agieval` overall/task/language/question_type accuracy | `mathtutorbench_pedagogy` Pedagogy IF | P05(0.2/0.2 异facet) | 6 | 0.943 |
| `ceval` overall/category/subject accuracy | `mathtutorbench_pedagogy_hard` Pedagogy IF hard | P05(0.5/0.2 异facet) | 6 | 0.943 |
| `mathtutorbench_scaffolding` Scaffolding | `mmlu_pro` overall/category accuracy | P05(0.2/0.5 异facet) | 6 | 0.943 |
| `mathtutorbench_scaffolding_hard` Scaffolding hard | `mmlu_pro` overall/category accuracy | P05(0.2/0.5 异facet) | 6 | 0.943 |
| `agieval` overall/task/language/question_type accuracy | `mathtutorbench_mistake_correction` Mistake Correction | P06(0.5/0.2 异facet) | 5 | 1.0 |
| `mathtutorbench_mistake_correction` Mistake Correction | `mmlu_pro` overall/category accuracy | P06(0.2/0.2 异facet) | 5 | 1.0 |

## 局限

- n=5-8 的置信区间很宽，评级以红旗探测为目的，不是效应量精确估计；补模型数（M2.5）是第一优先级。
- 偏相关控制的'综合分'由同一批证据构造，存在轻度内生性；仅作敏感性检查。
- 配对之间共享格子、非独立，区分效度的 permutation p 只作参考。