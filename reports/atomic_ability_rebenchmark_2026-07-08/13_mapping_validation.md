# 映射效度检查报告（13 号）

生成脚本：`scripts/build_mapping_validation.py`（幂等）；测量模型：`data/mapping_measurement_model_v5.json`（adjudicated）。
规则见 `doc/mapping_validation_plan_2026-07-11.md` §2；ρ 一律与 n、90% CI 同格呈现，n<5 的配对只进低置信附录。

覆盖缺口（无任何 benchmark 映射，不参与本报告分析）：P09 工具使用与长程智能体执行、P15 学术诚信与作答真实性判定。

## Phase 0：天花板/方差受限名单

共 34 / 54 个有证据格子被标记 `variance_restricted`（mean≥8.5 或 n≥4 且 SD<0.5）。这些格子参与的配对**不进入裁决**；优先动作是上难度/换切分，不是改映射。

| Benchmark | Subdimension | n | mean | SD | 标记 |
|---|---|---:|---:|---:|---|
| `mrbench_tutor` | dimension: Tutor_Tone (non-offensive) | 3 | 10.0 | 0.0 | ceiling |
| `mathtutorbench_problem_solving` | Problem Solving | 4 | 9.704 | 0.111 | ceiling, low_variance |
| `bea2025_tutor` | dimension: Providing_Guidance | 3 | 9.633 | 0.203 | ceiling |
| `mrbench_tutor` | dimension: Tutor_Tone (encouraging share) | 3 | 9.35 | 0.229 | ceiling |
| `bea2025_tutor` | dimension: Actionability | 3 | 9.311 | 0.391 | ceiling |
| `ceval` | overall/category/subject accuracy | 5 | 9.111 | 0.303 | ceiling, low_variance |
| `edubench` | basic_factual_accuracy (metric) | 11 | 9.105 | 0.324 | ceiling, low_variance |
| `mrbench_tutor` | dimension: Actionability | 3 | 9.1 | 0.433 | ceiling |
| `ifeval` | prompt-level strict accuracy | 5 | 9.063 | 0.224 | ceiling, low_variance |
| `mrbench_tutor` | dimension: Providing_Guidance | 3 | 9.05 | 0.218 | ceiling |
| `mrbench_tutor` | dimension: Mistake_Identification | 3 | 9.017 | 0.333 | ceiling |
| `mathtutorbench_mistake_correction` | Mistake Correction | 5 | 9.016 | 0.33 | ceiling, low_variance |
| `p08_abstention` | balanced abstention score | 5 | 8.9 | 0.219 | ceiling, low_variance |
| `agieval` | overall/task/language/question_type accuracy | 5 | 8.737 | 0.401 | ceiling, low_variance |
| `edubench` | domain_knowledge_accuracy (metric) | 11 | 8.685 | 0.613 | ceiling |
| `mathtutorbench_solution_correctness` | Solution Correctness | 5 | 8.683 | 0.157 | ceiling, low_variance |
| `mmlu_pro` | overall/category accuracy | 5 | 8.597 | 0.212 | ceiling, low_variance |
| `pedagogy_benchmark` | CDPK/SEND aggregate from 0701 card | 7 | 8.564 | 0.215 | ceiling, low_variance |
| `edubench` | tone_style_consistency (metric) | 11 | 8.477 | 0.184 | low_variance |
| `edubench` | clarity_concision_inspiration (metric) | 11 | 8.378 | 0.284 | low_variance |
| `mathtutorbench_pedagogy` | Pedagogy IF | 7 | 8.253 | 0.483 | low_variance |
| `sas_bench` | QWK holistic total score | 7 | 8.24 | 0.278 | low_variance |
| `edubench` | QG × clarity_concision_inspiration + scenario_element_integration (task×metric) | 11 | 8.155 | 0.434 | low_variance |
| `mathtutorbench_mistake_location` | Mistake Location | 5 | 7.748 | 0.105 | low_variance |
| `edubench` | scenario_element_integration (metric) | 11 | 7.684 | 0.42 | low_variance |
| `sas_bench` | CCS step scoring consistency | 7 | 7.623 | 0.269 | low_variance |
| `eduguard_sata` | Teaching Harm / SATA RFS | 8 | 7.473 | 0.255 | low_variance |
| `eduillustrate` | 8-dim 0-5 visual explanation score | 4 | 6.929 | 0.467 | low_variance |
| `p08_calibration` | calibration composite (CWR/AUROC) | 5 | 6.439 | 0.492 | low_variance |
| `edubench` | motivation_guidance_positive_feedback (metric) | 11 | 6.411 | 0.243 | low_variance |
| `edubench` | personalized_adaptation_learning_support (metric) | 11 | 6.294 | 0.326 | low_variance |
| `tutorbench` | Fair815 multimodal tutor quality | 6 | 5.478 | 0.25 | low_variance |
| `p07_selfcheck` | two-round self-check (fix/break rate) | 5 | 5.288 | 0.226 | low_variance |
| `mathtutorbench_socratic` | Socratic Questioning | 4 | 2.726 | 0.402 | low_variance |

## 红旗配对（flagged：同 P 预期收敛却 ρ<0，n≥6）

每条 flagged 需人工裁决：改权重 / 拆 facet / 降 tier / 转裁判治理（计划 §2.6）。

| A | B | 共享 P（权重A/B） | n | ρ | 偏ρ(控综合分) | perm p | 90% CI | 评级 |
|---|---|---|---:|---:|---:|---:|---|---|
| `edubench` error_identification_correction_accuracy (metric) | `sas_bench` ECS error-cause consistency | P11(0.25/0.7) | 6 | -0.486 | -0.497 | 0.3556 | [-1.0, 0.8] | flagged |

## 观察带（watch：0≤ρ<0.2 且 n≥8）

（无）

## 已验证配对（validated：ρ≥0.5 且 CI 下界>0）

（无）

## 待定配对（provisional）

| A | B | 共享 P（权重A/B） | n | ρ | 偏ρ(控综合分) | perm p | 90% CI | 评级 |
|---|---|---|---:|---:|---:|---:|---|---|
| `edubench` higher_order_thinking_ability_development (metric) | `mathtutorbench_scaffolding` Scaffolding | P18(0.25/0.35) | 6 | 0.371 | 0.486 | 0.4972 | [-0.636, 1.0] | provisional |
| `edubench` higher_order_thinking_ability_development (metric) | `mathtutorbench_scaffolding_hard` Scaffolding hard | P18(0.25/0.35) | 6 | 0.371 | 0.486 | 0.4972 | [-0.636, 1.0] | provisional |
| `edubench` higher_order_thinking_ability_development (metric) | `mathtutorbench_pedagogy_hard` Pedagogy IF hard | P18(0.25/0.3) | 6 | 0.486 | 0.723 | 0.3556 | [-0.818, 1.0] | provisional |

## 因方差受限不裁决的配对

任一侧格子 variance_restricted；其 ρ 不作为构念证据。

| A | B | 共享 P（权重A/B） | n | ρ | 偏ρ(控综合分) | perm p | 90% CI | 评级 |
|---|---|---|---:|---:|---:|---:|---|---|
| `edubench` personalized_adaptation_learning_support (metric) | `pedagogy_benchmark` CDPK/SEND aggregate from 0701 card | P16(0.3/0.3), P17(0.4/0.3 异facet) | 5 | -0.9 | -0.995 | 0.0833 | [-1.0, -0.25] | variance_restricted |
| `edubench` clarity_concision_inspiration (metric) | `mathtutorbench_pedagogy_hard` Pedagogy IF hard | P18(0.3/0.3) | 6 | -0.771 | -0.42 | 0.1028 | [-1.0, -0.091] | variance_restricted |
| `edubench` clarity_concision_inspiration (metric) | `mathtutorbench_scaffolding` Scaffolding | P18(0.3/0.35) | 6 | -0.771 | -0.772 | 0.1028 | [-1.0, -0.091] | variance_restricted |
| `edubench` clarity_concision_inspiration (metric) | `mathtutorbench_scaffolding_hard` Scaffolding hard | P18(0.3/0.35) | 6 | -0.771 | -0.772 | 0.1028 | [-1.0, -0.091] | variance_restricted |
| `edubench` clarity_concision_inspiration (metric) | `mathtutorbench_pedagogy` Pedagogy IF | P18(0.3/0.3) | 6 | -0.714 | 0.062 | 0.1361 | [-1.0, 0.091] | variance_restricted |
| `edubench` basic_factual_accuracy (metric) | `sas_bench` ECS error-cause consistency | P05(0.3/0.2) | 6 | -0.371 | -0.382 | 0.4972 | [-1.0, 0.636] | variance_restricted |
| `edubench` domain_knowledge_accuracy (metric) | `sas_bench` ECS error-cause consistency | P05(0.35/0.2) | 6 | -0.086 | -0.058 | 0.9194 | [-0.939, 0.92] | variance_restricted |
| `edubench` personalized_adaptation_learning_support (metric) | `mathtutorbench_pedagogy` Pedagogy IF | P17(0.4/0.45) | 6 | -0.086 | -0.311 | 0.9194 | [-0.92, 0.92] | variance_restricted |
| `edubench` scenario_element_integration (metric) | `mathtutorbench_pedagogy` Pedagogy IF | P17(0.25/0.45) | 6 | -0.086 | -0.311 | 0.9194 | [-0.92, 0.92] | variance_restricted |
| `edubench` personalized_adaptation_learning_support (metric) | `mathtutorbench_scaffolding` Scaffolding | P17(0.4/0.5) | 6 | -0.029 | -0.144 | 1.0 | [-0.818, 1.0] | variance_restricted |
| `edubench` personalized_adaptation_learning_support (metric) | `mathtutorbench_scaffolding_hard` Scaffolding hard | P17(0.4/0.5) | 6 | -0.029 | -0.144 | 1.0 | [-0.818, 1.0] | variance_restricted |
| `edubench` scenario_element_integration (metric) | `mathtutorbench_scaffolding` Scaffolding | P17(0.25/0.5) | 6 | -0.029 | -0.144 | 1.0 | [-0.935, 1.0] | variance_restricted |
| `edubench` scenario_element_integration (metric) | `mathtutorbench_scaffolding_hard` Scaffolding hard | P17(0.25/0.5) | 6 | -0.029 | -0.144 | 1.0 | [-0.818, 1.0] | variance_restricted |
| `p07_selfcheck` two-round self-check (fix/break rate) | `p08_calibration` calibration composite (CWR/AUROC) | P07(0.85/0.2) | 5 | 0.0 | -0.075 | 1.0 | [-0.875, 1.0] | variance_restricted |
| `edubench` personalized_adaptation_learning_support (metric) | `mathtutorbench_pedagogy_hard` Pedagogy IF hard | P17(0.4/0.45) | 6 | 0.029 | -0.106 | 1.0 | [-0.806, 1.0] | variance_restricted |
| `edubench` scenario_element_integration (metric) | `mathtutorbench_pedagogy_hard` Pedagogy IF hard | P17(0.25/0.45) | 6 | 0.029 | -0.106 | 1.0 | [-0.806, 1.0] | variance_restricted |
| `edubench` higher_order_thinking_ability_development (metric) | `mathtutorbench_pedagogy` Pedagogy IF | P18(0.25/0.3) | 6 | 0.543 | 0.888 | 0.2972 | [-0.548, 1.0] | variance_restricted |
| `agieval` overall/task/language/question_type accuracy | `ceval` overall/category/subject accuracy | P05(0.35/0.6), P06(0.45/0.25) | 5 | 0.9 | 0.98 | 0.0833 | [0.25, 1.0] | variance_restricted |
| `ceval` overall/category/subject accuracy | `mmlu_pro` overall/category accuracy | P05(0.6/0.6), P06(0.25/0.3) | 5 | 0.9 | 0.98 | 0.0833 | [0.25, 1.0] | variance_restricted |
| `agieval` overall/task/language/question_type accuracy | `mmlu_pro` overall/category accuracy | P05(0.35/0.6), P06(0.45/0.3) | 5 | 1.0 | 1.0 | 0.0167 | [1.0, 1.0] | variance_restricted |

## 区分效度（同 P 收敛配对 vs 不共享 P 的 baseline）

- 收敛配对（跨家族、非受限、n≥5）：4 对，mean ρ = 0.185，median = 0.371
- baseline（不共享任何 P）：25 对，mean ρ = -0.209，median = -0.2
- 差值 = 0.395，单侧 permutation p = 0.0237（配对之间共享格子、非独立；p 值仅供参考，结论以红旗/非红旗为主。）

若差值不显著为正，说明 P 划分对'哪些 benchmark 相关'没有预测力，映射层需整体重审。

## 家族方法方差（halo）

| 家族 | 家族内配对数 | 家族内 mean ρ | 跨家族配对数 | 跨家族 mean ρ | halo 分 | 家族内先聚合? |
|---|---:|---:|---:|---:|---:|---|
| `sas_bench` | 3 | 0.714 | 39 | -0.218 | 0.932 | 是 |
| `eduguard` | 3 | 0.357 | 55 | -0.186 | 0.543 | 是 |
| `edubench` | 66 | 0.291 | 144 | -0.24 | 0.531 | 是 |
| `mathtutorbench` | 21 | 0.658 | 97 | 0.15 | 0.508 | 是 |
| `p08` | 1 | 0.6 | 14 | 0.586 | 0.014 | 否 |

halo 分 > 0.5 的家族：多子维度在 P 聚合前先合成一票（计划 §2.6）。

## P × 格子评级汇总

评级分布：flagged=2、provisional=4、variance_restricted=55、insufficient_evidence=39、single_source=2

| P | 类型 | facet | Benchmark | Subdimension | 权重 | 评级 |
|---|---|---|---|---|---:|---|
| P01 指令与约束遵循 | reflective | core | `agieval` | overall/task/language/question_type accuracy | 0.2 | **variance_restricted** |
| P01 指令与约束遵循 | reflective | core | `ifeval` | prompt-level strict accuracy | 1.0 | **variance_restricted** |
| P02 长上下文与证据定位 | reflective | core | `asap_2` | essay holistic QWK | 0.2 | **insufficient_evidence** |
| P02 长上下文与证据定位 | reflective | core | `longtutor_evidence` | semantic evidence accuracy (3 memory types) | 0.7 | **insufficient_evidence** |
| P02 长上下文与证据定位 | reflective | core | `mathtutorbench_mistake_location` | Mistake Location | 0.2 | **variance_restricted** |
| P02 长上下文与证据定位 | reflective | core | `sas_bench` | CCS step scoring consistency | 0.2 | **variance_restricted** |
| P03 多模态理解 | formative | subject_charts | `k12vista` | official partial-credit score (per-blank 0/1 mean) | 0.55 | **insufficient_evidence** |
| P03 多模态理解 | formative | problem_images | `mathvista` | task/question_type/answer_type accuracy | 0.35 | **insufficient_evidence** |
| P03 多模态理解 | formative | mixed_materials | `mmtutorbench` | multimodal tutor score | 0.3 | **insufficient_evidence** |
| P03 多模态理解 | formative | problem_images | `olympiadbench` | overall/subject/language/modality accuracy | 0.2 | **insufficient_evidence** |
| P03 多模态理解 | formative | mixed_materials | `tutorbench` | Fair815 multimodal tutor quality | 0.25 | **variance_restricted** |
| P05 知识调用与掌握 | formative | pedagogical_knowledge | `mathtutorbench_pedagogy_hard` | Pedagogy IF hard | 0.25 | **insufficient_evidence** |
| P05 知识调用与掌握 | formative | subject_knowledge | `mathvista` | task/question_type/answer_type accuracy | 0.2 | **insufficient_evidence** |
| P05 知识调用与掌握 | formative | subject_knowledge | `mooccube_prereq` | chance-corrected composite (先修选择 + 学习顺序排序) | 0.2 | **insufficient_evidence** |
| P05 知识调用与掌握 | formative | subject_knowledge | `olympiadbench` | overall/subject/language/modality accuracy | 0.25 | **insufficient_evidence** |
| P05 知识调用与掌握 | formative | pedagogical_knowledge | `pedagogy_benchmark` | CDPK teaching knowledge selection | 0.45 | **insufficient_evidence** |
| P05 知识调用与掌握 | formative | pedagogical_knowledge | `pedagogy_benchmark` | SEND special education needs selection | 0.35 | **insufficient_evidence** |
| P05 知识调用与掌握 | formative | subject_knowledge | `sas_bench` | ECS error-cause consistency | 0.2 | **insufficient_evidence** |
| P05 知识调用与掌握 | formative | subject_knowledge | `agieval` | overall/task/language/question_type accuracy | 0.35 | **variance_restricted** |
| P05 知识调用与掌握 | formative | subject_knowledge | `ceval` | overall/category/subject accuracy | 0.6 | **variance_restricted** |
| P05 知识调用与掌握 | formative | subject_knowledge | `edubench` | basic_factual_accuracy (metric) | 0.3 | **variance_restricted** |
| P05 知识调用与掌握 | formative | subject_knowledge | `edubench` | domain_knowledge_accuracy (metric) | 0.35 | **variance_restricted** |
| P05 知识调用与掌握 | formative | pedagogical_knowledge | `mathtutorbench_pedagogy` | Pedagogy IF | 0.25 | **variance_restricted** |
| P05 知识调用与掌握 | formative | subject_knowledge | `mathtutorbench_problem_solving` | Problem Solving | 0.3 | **variance_restricted** |
| P05 知识调用与掌握 | formative | subject_knowledge | `mmlu_pro` | overall/category accuracy | 0.6 | **variance_restricted** |
| P05 知识调用与掌握 | formative | pedagogical_knowledge | `pedagogy_benchmark` | CDPK/SEND aggregate from 0701 card | 0.4 | **variance_restricted** |
| P06 推理与生成 | formative | generative_reasoning | `edubench` | higher_order_thinking_ability_development (metric) | 0.2 | **insufficient_evidence** |
| P06 推理与生成 | formative | generative_reasoning | `edubench` | reasoning_process_rigor (metric) | 0.35 | **insufficient_evidence** |
| P06 推理与生成 | formative | problem_reasoning | `k12vista` | official partial-credit score (per-blank 0/1 mean) | 0.3 | **insufficient_evidence** |
| P06 推理与生成 | formative | problem_reasoning | `mathvista` | task/question_type/answer_type accuracy | 0.45 | **insufficient_evidence** |
| P06 推理与生成 | formative | problem_reasoning | `olympiadbench` | overall/subject/language/modality accuracy | 0.55 | **insufficient_evidence** |
| P06 推理与生成 | formative | problem_reasoning | `agieval` | overall/task/language/question_type accuracy | 0.45 | **variance_restricted** |
| P06 推理与生成 | formative | problem_reasoning | `ceval` | overall/category/subject accuracy | 0.25 | **variance_restricted** |
| P06 推理与生成 | formative | generative_reasoning | `mathtutorbench_mistake_correction` | Mistake Correction | 0.2 | **variance_restricted** |
| P06 推理与生成 | formative | problem_reasoning | `mathtutorbench_problem_solving` | Problem Solving | 0.6 | **variance_restricted** |
| P06 推理与生成 | formative | problem_reasoning | `mmlu_pro` | overall/category accuracy | 0.3 | **variance_restricted** |
| P07 自我校验与修正 | reflective | core | `mathtutorbench_solution_correctness` | Solution Correctness | 0.25 | **variance_restricted** |
| P07 自我校验与修正 | reflective | core | `p07_selfcheck` | two-round self-check (fix/break rate) | 0.85 | **variance_restricted** |
| P07 自我校验与修正 | reflective | core | `p08_calibration` | calibration composite (CWR/AUROC) | 0.2 | **variance_restricted** |
| P08 置信度校准与弃答 | formative | abstention | `p08_abstention` | balanced abstention score | 0.85 | **variance_restricted** |
| P08 置信度校准与弃答 | formative | calibration | `p08_calibration` | calibration composite (CWR/AUROC) | 0.8 | **variance_restricted** |
| P10 多模态教学产物生成 | formative | static_visual | `eduillustrate` | 8-dim 0-5 visual explanation score | 0.45 | **single_source** |
| P11 错误诊断 | formative | error_attribution | `edubench` | error_identification_correction_accuracy (metric) | 0.25 | **flagged** |
| P11 错误诊断 | formative | error_attribution | `sas_bench` | ECS error-cause consistency | 0.7 | **flagged** |
| P11 错误诊断 | formative | error_attribution | `bea2025_judge` | judge labels: mistake/guidance/actionability | 0.3 | **insufficient_evidence** |
| P11 错误诊断 | formative | error_attribution | `bea2025_tutor` | dimension: Mistake_Identification | 0.25 | **insufficient_evidence** |
| P11 错误诊断 | formative | error_attribution | `mrbench_judge` | 8-dimension tutor response judging | 0.25 | **insufficient_evidence** |
| P11 错误诊断 | formative | error_attribution | `mathtutorbench_mistake_correction` | Mistake Correction | 0.2 | **variance_restricted** |
| P11 错误诊断 | formative | error_location | `mathtutorbench_mistake_location` | Mistake Location | 0.7 | **variance_restricted** |
| P11 错误诊断 | formative | answer_verdict | `mathtutorbench_solution_correctness` | Solution Correctness | 0.6 | **variance_restricted** |
| P11 错误诊断 | formative | error_attribution | `mrbench_tutor` | dimension: Mistake_Identification | 0.25 | **variance_restricted** |
| P11 错误诊断 | formative | error_location | `sas_bench` | CCS step scoring consistency | 0.25 | **variance_restricted** |
| P14 主观题评价能力 | formative | holistic_scoring | `asap_2` | essay holistic QWK | 0.65 | **insufficient_evidence** |
| P14 主观题评价能力 | formative | analytic_scoring | `bea2025_judge` | judge labels: mistake/guidance/actionability | 0.45 | **insufficient_evidence** |
| P14 主观题评价能力 | formative | analytic_scoring | `mrbench_judge` | 8-dimension tutor response judging | 0.45 | **insufficient_evidence** |
| P14 主观题评价能力 | formative | analytic_scoring | `sas_bench` | CCS step scoring consistency | 0.55 | **variance_restricted** |
| P14 主观题评价能力 | formative | holistic_scoring | `sas_bench` | QWK holistic total score | 0.7 | **variance_restricted** |
| P16 学习者画像建模 | formative | knowledge_state_estimation | `longtutor_diagnosis` | four-category knowledge-state diagnosis macro-F1 | 0.3 | **insufficient_evidence** |
| P16 学习者画像建模 | formative | support_needs | `pedagogy_benchmark` | SEND special education needs selection | 0.35 | **insufficient_evidence** |
| P16 学习者画像建模 | formative | support_needs | `edubench` | personalized_adaptation_learning_support (metric) | 0.3 | **variance_restricted** |
| P16 学习者画像建模 | formative | support_needs | `pedagogy_benchmark` | CDPK/SEND aggregate from 0701 card | 0.3 | **variance_restricted** |
| P17 个性化教学策略选择 | formative | strategy_enactment | `longtutor_teaching` | judge dims: strategy_alignment + history_utilization (1-5) | 0.3 | **insufficient_evidence** |
| P17 个性化教学策略选择 | formative | strategy_enactment | `mathtutorbench_pedagogy_hard` | Pedagogy IF hard | 0.45 | **insufficient_evidence** |
| P17 个性化教学策略选择 | formative | strategy_enactment | `mathtutorbench_scaffolding` | Scaffolding | 0.5 | **insufficient_evidence** |
| P17 个性化教学策略选择 | formative | strategy_enactment | `mathtutorbench_scaffolding_hard` | Scaffolding hard | 0.5 | **insufficient_evidence** |
| P17 个性化教学策略选择 | formative | strategy_enactment | `mmtutorbench` | multimodal tutor score | 0.3 | **insufficient_evidence** |
| P17 个性化教学策略选择 | formative | strategy_formulation | `pedagogy_benchmark` | CDPK teaching knowledge selection | 0.35 | **insufficient_evidence** |
| P17 个性化教学策略选择 | formative | strategy_formulation | `pedagogy_benchmark` | SEND special education needs selection | 0.3 | **insufficient_evidence** |
| P17 个性化教学策略选择 | formative | strategy_enactment | `bea2025_tutor` | dimension: Providing_Guidance | 0.3 | **variance_restricted** |
| P17 个性化教学策略选择 | formative | strategy_enactment | `edubench` | personalized_adaptation_learning_support (metric) | 0.4 | **variance_restricted** |
| P17 个性化教学策略选择 | formative | strategy_enactment | `edubench` | scenario_element_integration (metric) | 0.25 | **variance_restricted** |
| P17 个性化教学策略选择 | formative | strategy_enactment | `mathtutorbench_pedagogy` | Pedagogy IF | 0.45 | **variance_restricted** |
| P17 个性化教学策略选择 | formative | strategy_enactment | `mathtutorbench_socratic` | Socratic Questioning | 0.65 | **variance_restricted** |
| P17 个性化教学策略选择 | formative | strategy_enactment | `mrbench_tutor` | dimension: Providing_Guidance | 0.3 | **variance_restricted** |
| P17 个性化教学策略选择 | formative | strategy_formulation | `pedagogy_benchmark` | CDPK/SEND aggregate from 0701 card | 0.3 | **variance_restricted** |
| P17 个性化教学策略选择 | formative | strategy_enactment | `tutorbench` | Fair815 multimodal tutor quality | 0.35 | **variance_restricted** |
| P18 适配性解释与反馈生成 | formative | artifact_generation | `edubench` | TMG/PCC × clarity_concision_inspiration + scenario_element_integration (task×metric) | 0.4 | **insufficient_evidence** |
| P18 适配性解释与反馈生成 | formative | content_feedback | `mmtutorbench` | multimodal tutor score | 0.4 | **insufficient_evidence** |
| P18 适配性解释与反馈生成 | formative | content_feedback | `edubench` | higher_order_thinking_ability_development (metric) | 0.25 | **provisional** |
| P18 适配性解释与反馈生成 | formative | content_feedback | `mathtutorbench_pedagogy_hard` | Pedagogy IF hard | 0.3 | **provisional** |
| P18 适配性解释与反馈生成 | formative | content_feedback | `mathtutorbench_scaffolding` | Scaffolding | 0.35 | **provisional** |
| P18 适配性解释与反馈生成 | formative | content_feedback | `mathtutorbench_scaffolding_hard` | Scaffolding hard | 0.35 | **provisional** |
| P18 适配性解释与反馈生成 | formative | content_feedback | `bea2025_tutor` | dimension: Actionability | 0.2 | **variance_restricted** |
| P18 适配性解释与反馈生成 | formative | content_feedback | `edubench` | clarity_concision_inspiration (metric) | 0.3 | **variance_restricted** |
| P18 适配性解释与反馈生成 | formative | tone_support | `edubench` | motivation_guidance_positive_feedback (metric) | 0.35 | **variance_restricted** |
| P18 适配性解释与反馈生成 | formative | artifact_generation | `eduillustrate` | 8-dim 0-5 visual explanation score | 0.3 | **variance_restricted** |
| P18 适配性解释与反馈生成 | formative | content_feedback | `mathtutorbench_mistake_correction` | Mistake Correction | 0.35 | **variance_restricted** |
| P18 适配性解释与反馈生成 | formative | content_feedback | `mathtutorbench_pedagogy` | Pedagogy IF | 0.3 | **variance_restricted** |
| P18 适配性解释与反馈生成 | formative | content_feedback | `mathtutorbench_socratic` | Socratic Questioning | 0.35 | **variance_restricted** |
| P18 适配性解释与反馈生成 | formative | content_feedback | `mrbench_tutor` | dimension: Actionability | 0.2 | **variance_restricted** |
| P18 适配性解释与反馈生成 | formative | tone_support | `mrbench_tutor` | dimension: Tutor_Tone (encouraging share) | 0.2 | **variance_restricted** |
| P18 适配性解释与反馈生成 | formative | content_feedback | `tutorbench` | Fair815 multimodal tutor quality | 0.4 | **variance_restricted** |
| P19 学习路径规划（知识结构层） | reflective | core | `mooccube_prereq` | chance-corrected composite (先修选择 + 学习顺序排序) | 0.7 | **single_source** |
| P20 教育角色边界判断 | formative | boundary_behavior | `eduguard_adversarial` | Adversarial Safety ASR | 0.3 | **insufficient_evidence** |
| P20 教育角色边界判断 | formative | safety_knowledge | `mrbench_judge` | 8-dimension tutor response judging | 0.3 | **insufficient_evidence** |
| P20 教育角色边界判断 | formative | safety_knowledge | `eduguard_sata` | Teaching Harm / SATA RFS | 0.35 | **variance_restricted** |
| P20 教育角色边界判断 | formative | boundary_behavior | `mrbench_tutor` | dimension: Tutor_Tone (non-offensive) | 0.25 | **variance_restricted** |
| P21 学生风险识别 | formative | risk_signal_recognition | `eduguard_sata` | Teaching Harm / SATA RFS | 0.3 | **variance_restricted** |
| P22 安全处置选择 | formative | adversarial_robustness | `eduguard_adversarial` | Adversarial Safety ASR | 0.45 | **insufficient_evidence** |
| P22 安全处置选择 | formative | adversarial_robustness | `eduguard_adversarial` | Refusal quality distribution | 0.6 | **insufficient_evidence** |
| P22 安全处置选择 | formative | safety_knowledge | `eduguard_sata` | Teaching Harm / SATA RFS | 0.35 | **variance_restricted** |
| P23 命题与作业设计 | formative | item_generation | `edubench` | QG × clarity_concision_inspiration + scenario_element_integration (task×metric) | 0.4 | **variance_restricted** |

## 低置信附录（3 ≤ n < 5，仅呈现不评级）

| A | B | 共享 P | n | ρ |
|---|---|---|---:|---:|
| `ceval` overall/category/subject accuracy | `mooccube_prereq` chance-corrected composite (先修选择 + 学习顺序排序) | P05(0.6/0.2) | 3 | -1.0 |
| `edubench` personalized_adaptation_learning_support (metric) | `mathtutorbench_socratic` Socratic Questioning | P17(0.4/0.65) | 3 | -1.0 |
| `edubench` scenario_element_integration (metric) | `mathtutorbench_socratic` Socratic Questioning | P17(0.25/0.65) | 3 | -1.0 |
| `longtutor_teaching` judge dims: strategy_alignment + history_utilization (1-5) | `mathtutorbench_socratic` Socratic Questioning | P17(0.3/0.65) | 3 | -1.0 |
| `agieval` overall/task/language/question_type accuracy | `mooccube_prereq` chance-corrected composite (先修选择 + 学习顺序排序) | P05(0.35/0.2) | 3 | -0.5 |
| `asap_2` essay holistic QWK | `mathtutorbench_mistake_location` Mistake Location | P02(0.2/0.2) | 3 | -0.5 |
| `edubench` clarity_concision_inspiration (metric) | `mathtutorbench_socratic` Socratic Questioning | P18(0.3/0.35) | 3 | -0.5 |
| `longtutor_teaching` judge dims: strategy_alignment + history_utilization (1-5) | `mathtutorbench_pedagogy` Pedagogy IF | P17(0.3/0.45) | 3 | -0.5 |
| `longtutor_teaching` judge dims: strategy_alignment + history_utilization (1-5) | `mathtutorbench_scaffolding` Scaffolding | P17(0.3/0.5) | 3 | -0.5 |
| `longtutor_teaching` judge dims: strategy_alignment + history_utilization (1-5) | `mathtutorbench_scaffolding_hard` Scaffolding hard | P17(0.3/0.5) | 3 | -0.5 |
| `mmlu_pro` overall/category accuracy | `mooccube_prereq` chance-corrected composite (先修选择 + 学习顺序排序) | P05(0.6/0.2) | 3 | -0.5 |
| `agieval` overall/task/language/question_type accuracy | `edubench` basic_factual_accuracy (metric) | P05(0.35/0.3) | 4 | -0.4 |
| `asap_2` essay holistic QWK | `sas_bench` CCS step scoring consistency | P02(0.2/0.2), P14(0.65/0.55 异facet) | 4 | -0.4 |
| `asap_2` essay holistic QWK | `sas_bench` QWK holistic total score | P14(0.65/0.7) | 4 | -0.4 |
| `ceval` overall/category/subject accuracy | `edubench` basic_factual_accuracy (metric) | P05(0.6/0.3) | 4 | -0.4 |
| `edubench` basic_factual_accuracy (metric) | `mmlu_pro` overall/category accuracy | P05(0.3/0.6) | 4 | -0.4 |
| `edubench` clarity_concision_inspiration (metric) | `mathtutorbench_mistake_correction` Mistake Correction | P18(0.3/0.35) | 4 | -0.4 |
| `edubench` reasoning_process_rigor (metric) | `mathtutorbench_mistake_correction` Mistake Correction | P06(0.35/0.2) | 4 | -0.4 |
| `agieval` overall/task/language/question_type accuracy | `edubench` domain_knowledge_accuracy (metric) | P05(0.35/0.35) | 4 | -0.2 |
| `ceval` overall/category/subject accuracy | `edubench` domain_knowledge_accuracy (metric) | P05(0.6/0.35) | 4 | -0.2 |
| `edubench` domain_knowledge_accuracy (metric) | `mmlu_pro` overall/category accuracy | P05(0.35/0.6) | 4 | -0.2 |
| `edubench` error_identification_correction_accuracy (metric) | `mathtutorbench_mistake_correction` Mistake Correction | P11(0.25/0.2) | 4 | -0.2 |
| `edubench` higher_order_thinking_ability_development (metric) | `mathtutorbench_mistake_correction` Mistake Correction | P06(0.2/0.2), P18(0.25/0.35) | 4 | 0.2 |
| `mathtutorbench_solution_correctness` Solution Correctness | `p07_selfcheck` two-round self-check (fix/break rate) | P07(0.25/0.85) | 4 | 0.4 |
| `mathtutorbench_solution_correctness` Solution Correctness | `p08_calibration` calibration composite (CWR/AUROC) | P07(0.25/0.2) | 4 | 0.4 |
| `agieval` overall/task/language/question_type accuracy | `sas_bench` ECS error-cause consistency | P05(0.35/0.2) | 3 | 0.5 |
| `bea2025_tutor` dimension: Mistake_Identification | `mathtutorbench_mistake_correction` Mistake Correction | P11(0.25/0.2) | 3 | 0.5 |
| `bea2025_tutor` dimension: Providing_Guidance | `mathtutorbench_pedagogy` Pedagogy IF | P17(0.3/0.45) | 3 | 0.5 |
| `bea2025_tutor` dimension: Providing_Guidance | `mathtutorbench_pedagogy_hard` Pedagogy IF hard | P17(0.3/0.45) | 3 | 0.5 |
| `bea2025_tutor` dimension: Providing_Guidance | `mathtutorbench_scaffolding` Scaffolding | P17(0.3/0.5) | 3 | 0.5 |
| `bea2025_tutor` dimension: Providing_Guidance | `mathtutorbench_scaffolding_hard` Scaffolding hard | P17(0.3/0.5) | 3 | 0.5 |
| `bea2025_tutor` dimension: Providing_Guidance | `mathtutorbench_socratic` Socratic Questioning | P17(0.3/0.65) | 3 | 0.5 |
| `bea2025_tutor` dimension: Providing_Guidance | `mrbench_tutor` dimension: Providing_Guidance | P17(0.3/0.3) | 3 | 0.5 |
| `ceval` overall/category/subject accuracy | `sas_bench` ECS error-cause consistency | P05(0.6/0.2) | 3 | 0.5 |
| `edubench` basic_factual_accuracy (metric) | `mathtutorbench_problem_solving` Problem Solving | P05(0.3/0.3) | 3 | 0.5 |
| `longtutor_evidence` semantic evidence accuracy (3 memory types) | `mathtutorbench_mistake_location` Mistake Location | P02(0.7/0.2) | 3 | 0.5 |
| `longtutor_teaching` judge dims: strategy_alignment + history_utilization (1-5) | `mathtutorbench_pedagogy_hard` Pedagogy IF hard | P17(0.3/0.45) | 3 | 0.5 |
| `mathtutorbench_mistake_correction` Mistake Correction | `mrbench_tutor` dimension: Mistake_Identification | P11(0.2/0.25) | 3 | 0.5 |
| `mathtutorbench_mistake_correction` Mistake Correction | `sas_bench` ECS error-cause consistency | P11(0.2/0.7) | 3 | 0.5 |
| `mathtutorbench_mistake_location` Mistake Location | `sas_bench` CCS step scoring consistency | P02(0.2/0.2), P11(0.7/0.25) | 3 | 0.5 |
| `mathtutorbench_pedagogy` Pedagogy IF | `pedagogy_benchmark` CDPK/SEND aggregate from 0701 card | P05(0.25/0.4), P17(0.45/0.3 异facet) | 3 | 0.5 |
| `mathtutorbench_pedagogy_hard` Pedagogy IF hard | `pedagogy_benchmark` CDPK/SEND aggregate from 0701 card | P05(0.25/0.4), P17(0.45/0.3 异facet) | 3 | 0.5 |
| `mmlu_pro` overall/category accuracy | `sas_bench` ECS error-cause consistency | P05(0.6/0.2) | 3 | 0.5 |
| `agieval` overall/task/language/question_type accuracy | `ifeval` prompt-level strict accuracy | P01(0.2/1.0) | 4 | 0.8 |
| `bea2025_tutor` dimension: Actionability | `mrbench_tutor` dimension: Actionability | P18(0.2/0.2) | 3 | 0.866 |
| `mathtutorbench_mistake_correction` Mistake Correction | `mrbench_tutor` dimension: Actionability | P18(0.35/0.2) | 3 | 0.866 |
| `mathtutorbench_pedagogy` Pedagogy IF | `mrbench_tutor` dimension: Actionability | P18(0.3/0.2) | 3 | 0.866 |
| `mathtutorbench_pedagogy_hard` Pedagogy IF hard | `mrbench_tutor` dimension: Actionability | P18(0.3/0.2) | 3 | 0.866 |
| `mathtutorbench_scaffolding` Scaffolding | `mrbench_tutor` dimension: Actionability | P18(0.35/0.2) | 3 | 0.866 |
| `mathtutorbench_scaffolding_hard` Scaffolding hard | `mrbench_tutor` dimension: Actionability | P18(0.35/0.2) | 3 | 0.866 |
| `mathtutorbench_socratic` Socratic Questioning | `mrbench_tutor` dimension: Actionability | P18(0.35/0.2) | 3 | 0.866 |
| `agieval` overall/task/language/question_type accuracy | `mathtutorbench_problem_solving` Problem Solving | P05(0.35/0.3), P06(0.45/0.6) | 4 | 1.0 |
| `bea2025_tutor` dimension: Actionability | `mathtutorbench_mistake_correction` Mistake Correction | P18(0.2/0.35) | 3 | 1.0 |
| `bea2025_tutor` dimension: Actionability | `mathtutorbench_pedagogy` Pedagogy IF | P18(0.2/0.3) | 3 | 1.0 |
| `bea2025_tutor` dimension: Actionability | `mathtutorbench_pedagogy_hard` Pedagogy IF hard | P18(0.2/0.3) | 3 | 1.0 |
| `bea2025_tutor` dimension: Actionability | `mathtutorbench_scaffolding` Scaffolding | P18(0.2/0.35) | 3 | 1.0 |
| `bea2025_tutor` dimension: Actionability | `mathtutorbench_scaffolding_hard` Scaffolding hard | P18(0.2/0.35) | 3 | 1.0 |
| `bea2025_tutor` dimension: Actionability | `mathtutorbench_socratic` Socratic Questioning | P18(0.2/0.35) | 3 | 1.0 |
| `bea2025_tutor` dimension: Mistake_Identification | `mrbench_tutor` dimension: Mistake_Identification | P11(0.25/0.25) | 3 | 1.0 |
| `ceval` overall/category/subject accuracy | `mathtutorbench_problem_solving` Problem Solving | P05(0.6/0.3), P06(0.25/0.6) | 4 | 1.0 |
| `edubench` TMG/PCC × clarity_concision_inspiration + scenario_element_integration (task×metric) | `eduillustrate` 8-dim 0-5 visual explanation score | P18(0.4/0.3) | 3 | 1.0 |
| `edubench` domain_knowledge_accuracy (metric) | `mathtutorbench_problem_solving` Problem Solving | P05(0.35/0.3) | 3 | 1.0 |
| `edubench` higher_order_thinking_ability_development (metric) | `mathtutorbench_socratic` Socratic Questioning | P18(0.25/0.35) | 3 | 1.0 |
| `mathtutorbench_pedagogy` Pedagogy IF | `mrbench_tutor` dimension: Providing_Guidance | P17(0.45/0.3) | 3 | 1.0 |
| `mathtutorbench_pedagogy_hard` Pedagogy IF hard | `mrbench_tutor` dimension: Providing_Guidance | P17(0.45/0.3) | 3 | 1.0 |
| `mathtutorbench_problem_solving` Problem Solving | `mmlu_pro` overall/category accuracy | P05(0.3/0.6), P06(0.6/0.3) | 4 | 1.0 |
| `mathtutorbench_scaffolding` Scaffolding | `mrbench_tutor` dimension: Providing_Guidance | P17(0.5/0.3) | 3 | 1.0 |
| `mathtutorbench_scaffolding_hard` Scaffolding hard | `mrbench_tutor` dimension: Providing_Guidance | P17(0.5/0.3) | 3 | 1.0 |
| `mathtutorbench_socratic` Socratic Questioning | `mrbench_tutor` dimension: Providing_Guidance | P17(0.65/0.3) | 3 | 1.0 |

## 形成型跨 facet 配对（facet_distinct_expected，信息呈现，不触发红旗）

| A | B | 共享 P | n | ρ |
|---|---|---|---:|---:|
| `edubench` basic_factual_accuracy (metric) | `mathtutorbench_pedagogy_hard` Pedagogy IF hard | P05(0.3/0.25 异facet) | 6 | -0.771 |
| `edubench` basic_factual_accuracy (metric) | `mathtutorbench_pedagogy` Pedagogy IF | P05(0.3/0.25 异facet) | 6 | -0.714 |
| `edubench` basic_factual_accuracy (metric) | `pedagogy_benchmark` CDPK/SEND aggregate from 0701 card | P05(0.3/0.4 异facet) | 5 | -0.4 |
| `edubench` motivation_guidance_positive_feedback (metric) | `mathtutorbench_pedagogy` Pedagogy IF | P18(0.35/0.3 异facet) | 6 | -0.371 |
| `edubench` error_identification_correction_accuracy (metric) | `sas_bench` CCS step scoring consistency | P11(0.25/0.25 异facet) | 6 | -0.314 |
| `edubench` domain_knowledge_accuracy (metric) | `pedagogy_benchmark` CDPK/SEND aggregate from 0701 card | P05(0.35/0.4 异facet) | 5 | -0.3 |
| `edubench` scenario_element_integration (metric) | `pedagogy_benchmark` CDPK/SEND aggregate from 0701 card | P17(0.25/0.3 异facet) | 5 | -0.3 |
| `edubench` TMG/PCC × clarity_concision_inspiration + scenario_element_integration (task×metric) | `mathtutorbench_scaffolding` Scaffolding | P18(0.4/0.35 异facet) | 6 | -0.257 |
| `edubench` TMG/PCC × clarity_concision_inspiration + scenario_element_integration (task×metric) | `mathtutorbench_scaffolding_hard` Scaffolding hard | P18(0.4/0.35 异facet) | 6 | -0.257 |
| `edubench` motivation_guidance_positive_feedback (metric) | `mathtutorbench_pedagogy_hard` Pedagogy IF hard | P18(0.35/0.3 异facet) | 6 | -0.143 |
| `edubench` domain_knowledge_accuracy (metric) | `mathtutorbench_pedagogy_hard` Pedagogy IF hard | P05(0.35/0.25 异facet) | 6 | -0.029 |
| `edubench` motivation_guidance_positive_feedback (metric) | `mathtutorbench_scaffolding` Scaffolding | P18(0.35/0.35 异facet) | 6 | -0.029 |
| `edubench` motivation_guidance_positive_feedback (metric) | `mathtutorbench_scaffolding_hard` Scaffolding hard | P18(0.35/0.35 异facet) | 6 | -0.029 |
| `edubench` TMG/PCC × clarity_concision_inspiration + scenario_element_integration (task×metric) | `mathtutorbench_pedagogy_hard` Pedagogy IF hard | P18(0.4/0.3 异facet) | 6 | 0.029 |
| `edubench` domain_knowledge_accuracy (metric) | `mathtutorbench_pedagogy` Pedagogy IF | P05(0.35/0.25 异facet) | 6 | 0.086 |
| `edubench` TMG/PCC × clarity_concision_inspiration + scenario_element_integration (task×metric) | `mathtutorbench_pedagogy` Pedagogy IF | P18(0.4/0.3 异facet) | 6 | 0.2 |
| `agieval` overall/task/language/question_type accuracy | `mathtutorbench_pedagogy_hard` Pedagogy IF hard | P05(0.35/0.25 异facet) | 5 | 0.8 |
| `ceval` overall/category/subject accuracy | `mathtutorbench_pedagogy` Pedagogy IF | P05(0.6/0.25 异facet) | 5 | 0.8 |
| `mathtutorbench_pedagogy_hard` Pedagogy IF hard | `mmlu_pro` overall/category accuracy | P05(0.25/0.6 异facet) | 5 | 0.8 |
| `agieval` overall/task/language/question_type accuracy | `mathtutorbench_pedagogy` Pedagogy IF | P05(0.35/0.25 异facet) | 5 | 0.9 |
| `ceval` overall/category/subject accuracy | `mathtutorbench_mistake_correction` Mistake Correction | P06(0.25/0.2 异facet) | 5 | 0.9 |
| `ceval` overall/category/subject accuracy | `mathtutorbench_pedagogy_hard` Pedagogy IF hard | P05(0.6/0.25 异facet) | 5 | 0.9 |
| `mathtutorbench_pedagogy` Pedagogy IF | `mmlu_pro` overall/category accuracy | P05(0.25/0.6 异facet) | 5 | 0.9 |
| `agieval` overall/task/language/question_type accuracy | `mathtutorbench_mistake_correction` Mistake Correction | P06(0.45/0.2 异facet) | 5 | 1.0 |
| `mathtutorbench_mistake_correction` Mistake Correction | `mmlu_pro` overall/category accuracy | P06(0.2/0.3 异facet) | 5 | 1.0 |

## 局限

- n=5-8 的置信区间很宽，评级以红旗探测为目的，不是效应量精确估计；补模型数（M2.5）是第一优先级。
- 偏相关控制的'综合分'由同一批证据构造，存在轻度内生性；仅作敏感性检查。
- 配对之间共享格子、非独立，区分效度的 permutation p 只作参考。