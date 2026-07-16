# 映射效度检查报告（13 号）

生成脚本：`scripts/build_mapping_validation.py`（幂等）；测量模型：`data/mapping_measurement_model_v1.json`（reviewed）。
规则见 `doc/mapping_validation_plan_2026-07-11.md` §2；ρ 一律与 n、90% CI 同格呈现，n<5 的配对只进低置信附录。

覆盖缺口（无任何 benchmark 映射，不参与本报告分析）：P04 复杂多模态理解、P09 工具使用与长程智能体执行、P15 学术诚信与作答真实性判定、P19 学习路径规划。

## Phase 0：天花板/方差受限名单

共 19 / 34 个有证据格子被标记 `variance_restricted`（mean≥8.5 或 n≥4 且 SD<0.5）。这些格子参与的配对**不进入裁决**；优先动作是上难度/换切分，不是改映射。

| Benchmark | Subdimension | n | mean | SD | 标记 |
|---|---|---:|---:|---:|---|
| `mathtutorbench_problem_solving` | Problem Solving | 4 | 9.704 | 0.111 | ceiling, low_variance |
| `ceval` | overall/category/subject accuracy | 5 | 9.111 | 0.303 | ceiling, low_variance |
| `mathtutorbench_mistake_correction` | Mistake Correction | 5 | 9.016 | 0.33 | ceiling, low_variance |
| `edubench` | PCC pedagogical/personalized content creation | 11 | 8.803 | 0.567 | ceiling |
| `edubench` | PLS personalized learning support | 11 | 8.743 | 0.521 | ceiling |
| `ifeval` | prompt-level strict accuracy | 1 | 8.741 | — | ceiling |
| `agieval` | overall/task/language/question_type accuracy | 5 | 8.737 | 0.401 | ceiling, low_variance |
| `p08_abstention` | balanced abstention score | 1 | 8.72 | — | ceiling |
| `mathtutorbench_solution_correctness` | Solution Correctness | 5 | 8.683 | 0.157 | ceiling, low_variance |
| `mmlu_pro` | overall/category accuracy | 5 | 8.597 | 0.212 | ceiling, low_variance |
| `pedagogy_benchmark` | CDPK/SEND aggregate from 0701 card | 7 | 8.564 | 0.215 | ceiling, low_variance |
| `mathtutorbench_pedagogy` | Pedagogy IF | 7 | 8.319 | 0.499 | low_variance |
| `sas_bench` | QWK holistic total score | 6 | 8.244 | 0.304 | low_variance |
| `edubench` | IP idea provision / heuristic answer | 11 | 8.223 | 0.332 | low_variance |
| `mathtutorbench_mistake_location` | Mistake Location | 5 | 7.748 | 0.105 | low_variance |
| `sas_bench` | CCS step scoring consistency | 6 | 7.627 | 0.294 | low_variance |
| `eduguard_sata` | Teaching Harm / SATA RFS | 8 | 7.473 | 0.255 | low_variance |
| `tutorbench` | Fair815 multimodal tutor quality | 6 | 5.478 | 0.25 | low_variance |
| `mathtutorbench_socratic` | Socratic Questioning | 4 | 2.726 | 0.402 | low_variance |

## 红旗配对（flagged：同 P 预期收敛却 ρ<0，n≥6）

每条 flagged 需人工裁决：改权重 / 拆 facet / 降 tier / 转裁判治理（计划 §2.6）。

| A | B | 共享 P（权重A/B） | n | ρ | 偏ρ(控综合分) | perm p | 90% CI | 评级 |
|---|---|---|---:|---:|---:|---:|---|---|
| `edubench` QG question generation | `mathtutorbench_pedagogy_hard` Pedagogy IF hard | P05(0.3/0.25), P18(0.35/0.3 异facet) | 6 | -0.143 | -0.326 | 0.8028 | [-0.818, 0.806] | flagged |

## 观察带（watch：0≤ρ<0.2 且 n≥8）

（无）

## 已验证配对（validated：ρ≥0.5 且 CI 下界>0）

（无）

## 待定配对（provisional）

| A | B | 共享 P（权重A/B） | n | ρ | 偏ρ(控综合分) | perm p | 90% CI | 评级 |
|---|---|---|---:|---:|---:|---:|---|---|
| `edubench` TMG teaching material generation | `sas_bench` ECS error-cause consistency | P05(0.35/0.2) | 5 | -0.2 | -0.212 | 0.7833 | [-1.0, 0.875] | provisional |
| `edubench` TMG teaching material generation | `mathtutorbench_pedagogy_hard` Pedagogy IF hard | P05(0.35/0.25), P18(0.4/0.3 异facet) | 6 | 0.029 | -0.262 | 1.0 | [-0.818, 1.0] | provisional |
| `edubench` QG question generation | `sas_bench` ECS error-cause consistency | P05(0.3/0.2) | 5 | 0.2 | 0.212 | 0.7833 | [-0.875, 1.0] | provisional |

## 因方差受限不裁决的配对

任一侧格子 variance_restricted；其 ρ 不作为构念证据。

| A | B | 共享 P（权重A/B） | n | ρ | 偏ρ(控综合分) | perm p | 90% CI | 评级 |
|---|---|---|---:|---:|---:|---:|---|---|
| `edubench` PCC pedagogical/personalized content creation | `mathtutorbench_scaffolding` Scaffolding | P17(0.3/0.5), P18(0.45/0.35 异facet) | 6 | -0.086 | -0.369 | 0.9194 | [-1.0, 0.939] | variance_restricted |
| `edubench` PCC pedagogical/personalized content creation | `mathtutorbench_scaffolding_hard` Scaffolding hard | P17(0.3/0.5), P18(0.45/0.35 异facet) | 6 | -0.086 | -0.369 | 0.9194 | [-1.0, 1.0] | variance_restricted |
| `edubench` PLS personalized learning support | `mathtutorbench_scaffolding` Scaffolding | P17(0.45/0.5), P18(0.25/0.35) | 6 | -0.086 | -0.369 | 0.9194 | [-1.0, 0.939] | variance_restricted |
| `edubench` PLS personalized learning support | `mathtutorbench_scaffolding_hard` Scaffolding hard | P17(0.45/0.5), P18(0.25/0.35) | 6 | -0.086 | -0.369 | 0.9194 | [-1.0, 0.939] | variance_restricted |
| `edubench` QG question generation | `mathtutorbench_pedagogy` Pedagogy IF | P05(0.3/0.25), P18(0.35/0.3 异facet) | 6 | -0.029 | -0.138 | 1.0 | [-0.636, 0.935] | variance_restricted |
| `edubench` IP idea provision / heuristic answer | `sas_bench` ECS error-cause consistency | P05(0.25/0.2) | 5 | 0.1 | 0.302 | 0.95 | [-1.0, 1.0] | variance_restricted |
| `edubench` PCC pedagogical/personalized content creation | `sas_bench` ECS error-cause consistency | P05(0.25/0.2) | 5 | 0.2 | 0.212 | 0.7833 | [-0.875, 1.0] | variance_restricted |
| `edubench` TMG teaching material generation | `mathtutorbench_pedagogy` Pedagogy IF | P05(0.35/0.25), P18(0.4/0.3 异facet) | 6 | 0.2 | 0.059 | 0.7139 | [-0.8, 1.0] | variance_restricted |
| `edubench` PCC pedagogical/personalized content creation | `mathtutorbench_pedagogy_hard` Pedagogy IF hard | P05(0.25/0.25), P17(0.3/0.45), P18(0.45/0.3 异facet) | 6 | 0.257 | 0.071 | 0.6583 | [-0.818, 1.0] | variance_restricted |
| `edubench` PLS personalized learning support | `mathtutorbench_pedagogy_hard` Pedagogy IF hard | P17(0.45/0.45), P18(0.25/0.3) | 6 | 0.257 | 0.071 | 0.6583 | [-0.818, 1.0] | variance_restricted |
| `edubench` IP idea provision / heuristic answer | `mathtutorbench_scaffolding` Scaffolding | P17(0.4/0.5), P18(0.35/0.35) | 6 | 0.314 | 0.427 | 0.5639 | [-0.6, 1.0] | variance_restricted |
| `edubench` IP idea provision / heuristic answer | `mathtutorbench_scaffolding_hard` Scaffolding hard | P17(0.4/0.5), P18(0.35/0.35) | 6 | 0.314 | 0.427 | 0.5639 | [-0.6, 1.0] | variance_restricted |
| `edubench` PCC pedagogical/personalized content creation | `mathtutorbench_pedagogy` Pedagogy IF | P05(0.25/0.25), P17(0.3/0.45), P18(0.45/0.3 异facet) | 6 | 0.429 | 0.356 | 0.4194 | [-0.5, 1.0] | variance_restricted |
| `edubench` PLS personalized learning support | `mathtutorbench_pedagogy` Pedagogy IF | P17(0.45/0.45), P18(0.25/0.3) | 6 | 0.429 | 0.356 | 0.4194 | [-0.636, 1.0] | variance_restricted |
| `edubench` IP idea provision / heuristic answer | `mathtutorbench_pedagogy_hard` Pedagogy IF hard | P05(0.25/0.25), P17(0.4/0.45), P18(0.35/0.3) | 6 | 0.486 | 0.616 | 0.3556 | [-0.5, 1.0] | variance_restricted |
| `edubench` IP idea provision / heuristic answer | `mathtutorbench_pedagogy` Pedagogy IF | P05(0.25/0.25), P17(0.4/0.45), P18(0.35/0.3) | 6 | 0.6 | 0.688 | 0.2417 | [-0.091, 1.0] | variance_restricted |
| `agieval` overall/task/language/question_type accuracy | `ceval` overall/category/subject accuracy | P05(0.35/0.6), P06(0.45/0.25) | 5 | 0.9 | 0.84 | 0.0833 | [0.25, 1.0] | variance_restricted |
| `ceval` overall/category/subject accuracy | `mmlu_pro` overall/category accuracy | P05(0.6/0.6), P06(0.25/0.3) | 5 | 0.9 | 0.84 | 0.0833 | [0.25, 1.0] | variance_restricted |
| `agieval` overall/task/language/question_type accuracy | `mmlu_pro` overall/category accuracy | P05(0.35/0.6), P06(0.45/0.3) | 5 | 1.0 | 1.0 | 0.0167 | [1.0, 1.0] | variance_restricted |

## 区分效度（同 P 收敛配对 vs 不共享 P 的 baseline）

- 收敛配对（跨家族、非受限、n≥5）：4 对，mean ρ = -0.028，median = -0.057
- baseline（不共享任何 P）：5 对，mean ρ = -0.26，median = -0.2
- 差值 = 0.232，单侧 permutation p = 0.1911（配对之间共享格子、非独立；p 值仅供参考，结论以红旗/非红旗为主。）

若差值不显著为正，说明 P 划分对'哪些 benchmark 相关'没有预测力，映射层需整体重审。

## 家族方法方差（halo）

| 家族 | 家族内配对数 | 家族内 mean ρ | 跨家族配对数 | 跨家族 mean ρ | halo 分 | 家族内先聚合? |
|---|---:|---:|---:|---:|---:|---|
| `sas_bench` | 3 | 0.733 | 15 | -0.033 | 0.767 | 是 |
| `edubench` | 10 | 0.745 | 55 | -0.019 | 0.763 | 是 |
| `mathtutorbench` | 21 | 0.673 | 49 | 0.348 | 0.325 | 否 |
| `eduguard` | 1 | 0.071 | 18 | -0.021 | 0.092 | 否 |

halo 分 > 0.5 的家族：多子维度在 P 聚合前先合成一票（计划 §2.6）。

## P × 格子评级汇总

评级分布：flagged=2、provisional=2、variance_restricted=45、insufficient_evidence=50、single_source=1

| P | 类型 | facet | Benchmark | Subdimension | 权重 | 评级 |
|---|---|---|---|---|---:|---|
| P01 指令与约束遵循 | reflective | core | `agieval` | overall/task/language/question_type accuracy | 0.2 | **variance_restricted** |
| P01 指令与约束遵循 | reflective | core | `ifeval` | prompt-level strict accuracy | 1.0 | **variance_restricted** |
| P02 长上下文与证据定位 | reflective | core | `asap_2` | essay holistic QWK | 0.2 | **insufficient_evidence** |
| P02 长上下文与证据定位 | reflective | core | `mathtutorbench_mistake_location` | Mistake Location | 0.2 | **variance_restricted** |
| P02 长上下文与证据定位 | reflective | core | `sas_bench` | CCS step scoring consistency | 0.2 | **variance_restricted** |
| P03 常规多模态感知 | reflective | core | `eduillustrate` | 8-dim 0-5 visual explanation score | 0.25 | **insufficient_evidence** |
| P03 常规多模态感知 | reflective | core | `mathvista` | task/question_type/answer_type accuracy | 0.35 | **insufficient_evidence** |
| P03 常规多模态感知 | reflective | core | `mmtutorbench` | multimodal tutor score | 0.3 | **insufficient_evidence** |
| P03 常规多模态感知 | reflective | core | `olympiadbench` | overall/subject/language/modality accuracy | 0.2 | **insufficient_evidence** |
| P03 常规多模态感知 | reflective | core | `tutorbench` | Fair815 multimodal tutor quality | 0.25 | **variance_restricted** |
| P05 知识调用与掌握 | formative | applied_generation | `edubench` | QG question generation | 0.3 | **flagged** |
| P05 知识调用与掌握 | formative | applied_generation | `mathtutorbench_pedagogy_hard` | Pedagogy IF hard | 0.25 | **flagged** |
| P05 知识调用与掌握 | formative | subject_knowledge | `mathvista` | task/question_type/answer_type accuracy | 0.2 | **insufficient_evidence** |
| P05 知识调用与掌握 | formative | subject_knowledge | `olympiadbench` | overall/subject/language/modality accuracy | 0.25 | **insufficient_evidence** |
| P05 知识调用与掌握 | formative | pedagogical_knowledge | `pedagogy_benchmark` | CDPK teaching knowledge selection | 0.45 | **insufficient_evidence** |
| P05 知识调用与掌握 | formative | pedagogical_knowledge | `pedagogy_benchmark` | SEND special education needs selection | 0.35 | **insufficient_evidence** |
| P05 知识调用与掌握 | formative | applied_generation | `edubench` | TMG teaching material generation | 0.35 | **provisional** |
| P05 知识调用与掌握 | formative | applied_generation | `sas_bench` | ECS error-cause consistency | 0.2 | **provisional** |
| P05 知识调用与掌握 | formative | subject_knowledge | `agieval` | overall/task/language/question_type accuracy | 0.35 | **variance_restricted** |
| P05 知识调用与掌握 | formative | subject_knowledge | `ceval` | overall/category/subject accuracy | 0.6 | **variance_restricted** |
| P05 知识调用与掌握 | formative | applied_generation | `edubench` | IP idea provision / heuristic answer | 0.25 | **variance_restricted** |
| P05 知识调用与掌握 | formative | applied_generation | `edubench` | PCC pedagogical/personalized content creation | 0.25 | **variance_restricted** |
| P05 知识调用与掌握 | formative | applied_generation | `mathtutorbench_pedagogy` | Pedagogy IF | 0.25 | **variance_restricted** |
| P05 知识调用与掌握 | formative | subject_knowledge | `mathtutorbench_problem_solving` | Problem Solving | 0.3 | **variance_restricted** |
| P05 知识调用与掌握 | formative | subject_knowledge | `mmlu_pro` | overall/category accuracy | 0.6 | **variance_restricted** |
| P05 知识调用与掌握 | formative | pedagogical_knowledge | `pedagogy_benchmark` | CDPK/SEND aggregate from 0701 card | 0.4 | **variance_restricted** |
| P06 推理与生成 | formative | generative_reasoning | `edubench` | QG question generation | 0.35 | **insufficient_evidence** |
| P06 推理与生成 | formative | generative_reasoning | `edubench` | TMG teaching material generation | 0.25 | **insufficient_evidence** |
| P06 推理与生成 | formative | problem_reasoning | `mathvista` | task/question_type/answer_type accuracy | 0.45 | **insufficient_evidence** |
| P06 推理与生成 | formative | problem_reasoning | `olympiadbench` | overall/subject/language/modality accuracy | 0.55 | **insufficient_evidence** |
| P06 推理与生成 | formative | problem_reasoning | `pedagogy_benchmark` | CDPK teaching knowledge selection | 0.2 | **insufficient_evidence** |
| P06 推理与生成 | formative | problem_reasoning | `agieval` | overall/task/language/question_type accuracy | 0.45 | **variance_restricted** |
| P06 推理与生成 | formative | problem_reasoning | `ceval` | overall/category/subject accuracy | 0.25 | **variance_restricted** |
| P06 推理与生成 | formative | generative_reasoning | `mathtutorbench_mistake_correction` | Mistake Correction | 0.2 | **variance_restricted** |
| P06 推理与生成 | formative | problem_reasoning | `mathtutorbench_problem_solving` | Problem Solving | 0.6 | **variance_restricted** |
| P06 推理与生成 | formative | problem_reasoning | `mmlu_pro` | overall/category accuracy | 0.3 | **variance_restricted** |
| P07 自我校验与修正 | reflective | core | `p07_selfcheck` | two-round self-check (fix/break rate) | 0.85 | **insufficient_evidence** |
| P07 自我校验与修正 | reflective | core | `p08_calibration` | calibration composite (CWR/AUROC) | 0.2 | **insufficient_evidence** |
| P07 自我校验与修正 | reflective | core | `mathtutorbench_solution_correctness` | Solution Correctness | 0.25 | **variance_restricted** |
| P08 置信度校准与弃答 | formative | calibration | `p08_calibration` | calibration composite (CWR/AUROC) | 0.8 | **insufficient_evidence** |
| P08 置信度校准与弃答 | formative | abstention | `p08_abstention` | balanced abstention score | 0.85 | **variance_restricted** |
| P10 多模态教学产物生成 | reflective | core | `eduillustrate` | 8-dim 0-5 visual explanation score | 0.45 | **single_source** |
| P11 作答正误判定 | reflective | core | `bea2025_judge` | judge labels: mistake/guidance/actionability | 0.25 | **insufficient_evidence** |
| P11 作答正误判定 | reflective | core | `mathtutorbench_solution_correctness` | Solution Correctness | 0.6 | **variance_restricted** |
| P12 错误位置定位 | reflective | core | `mathtutorbench_mistake_location` | Mistake Location | 0.7 | **variance_restricted** |
| P12 错误位置定位 | reflective | core | `sas_bench` | CCS step scoring consistency | 0.25 | **variance_restricted** |
| P13 错因归因 | reflective | core | `bea2025_judge` | judge labels: mistake/guidance/actionability | 0.3 | **insufficient_evidence** |
| P13 错因归因 | reflective | core | `bea2025_tutor` | pedagogical pass rate | 0.25 | **insufficient_evidence** |
| P13 错因归因 | reflective | core | `mrbench_judge` | 8-dimension tutor response judging | 0.25 | **insufficient_evidence** |
| P13 错因归因 | reflective | core | `sas_bench` | ECS error-cause consistency | 0.7 | **insufficient_evidence** |
| P13 错因归因 | reflective | core | `mathtutorbench_mistake_correction` | Mistake Correction | 0.45 | **variance_restricted** |
| P14 Rubric 映射评分 | reflective | core | `asap_2` | essay holistic QWK | 0.65 | **insufficient_evidence** |
| P14 Rubric 映射评分 | reflective | core | `bea2025_judge` | judge labels: mistake/guidance/actionability | 0.45 | **insufficient_evidence** |
| P14 Rubric 映射评分 | reflective | core | `mrbench_judge` | 8-dimension tutor response judging | 0.45 | **insufficient_evidence** |
| P14 Rubric 映射评分 | reflective | core | `sas_bench` | CCS step scoring consistency | 0.55 | **variance_restricted** |
| P14 Rubric 映射评分 | reflective | core | `sas_bench` | QWK holistic total score | 0.7 | **variance_restricted** |
| P16 学习者画像建模 | formative | learner_knowledge | `pedagogy_benchmark` | SEND special education needs selection | 0.35 | **insufficient_evidence** |
| P16 学习者画像建模 | formative | learner_application | `edubench` | PLS personalized learning support | 0.3 | **variance_restricted** |
| P16 学习者画像建模 | formative | learner_knowledge | `pedagogy_benchmark` | CDPK/SEND aggregate from 0701 card | 0.3 | **variance_restricted** |
| P17 个性化教学策略选择 | formative | strategy_enactment | `bea2025_tutor` | pedagogical pass rate | 0.3 | **insufficient_evidence** |
| P17 个性化教学策略选择 | formative | strategy_enactment | `mathtutorbench_pedagogy_hard` | Pedagogy IF hard | 0.45 | **insufficient_evidence** |
| P17 个性化教学策略选择 | formative | strategy_enactment | `mathtutorbench_scaffolding` | Scaffolding | 0.5 | **insufficient_evidence** |
| P17 个性化教学策略选择 | formative | strategy_enactment | `mathtutorbench_scaffolding_hard` | Scaffolding hard | 0.5 | **insufficient_evidence** |
| P17 个性化教学策略选择 | formative | strategy_enactment | `mmtutorbench` | multimodal tutor score | 0.3 | **insufficient_evidence** |
| P17 个性化教学策略选择 | formative | strategy_enactment | `mrbench_tutor` | 8-dimension tutor pass rate | 0.3 | **insufficient_evidence** |
| P17 个性化教学策略选择 | formative | strategy_knowledge | `pedagogy_benchmark` | CDPK teaching knowledge selection | 0.35 | **insufficient_evidence** |
| P17 个性化教学策略选择 | formative | strategy_knowledge | `pedagogy_benchmark` | SEND special education needs selection | 0.3 | **insufficient_evidence** |
| P17 个性化教学策略选择 | formative | strategy_enactment | `edubench` | IP idea provision / heuristic answer | 0.4 | **variance_restricted** |
| P17 个性化教学策略选择 | formative | strategy_enactment | `edubench` | PCC pedagogical/personalized content creation | 0.3 | **variance_restricted** |
| P17 个性化教学策略选择 | formative | strategy_enactment | `edubench` | PLS personalized learning support | 0.45 | **variance_restricted** |
| P17 个性化教学策略选择 | formative | strategy_enactment | `mathtutorbench_pedagogy` | Pedagogy IF | 0.45 | **variance_restricted** |
| P17 个性化教学策略选择 | formative | strategy_enactment | `mathtutorbench_socratic` | Socratic Questioning | 0.65 | **variance_restricted** |
| P17 个性化教学策略选择 | formative | strategy_knowledge | `pedagogy_benchmark` | CDPK/SEND aggregate from 0701 card | 0.3 | **variance_restricted** |
| P17 个性化教学策略选择 | formative | strategy_enactment | `tutorbench` | Fair815 multimodal tutor quality | 0.35 | **variance_restricted** |
| P18 适配性解释与反馈生成 | formative | dialogic_feedback | `bea2025_tutor` | pedagogical pass rate | 0.45 | **insufficient_evidence** |
| P18 适配性解释与反馈生成 | formative | artifact_generation | `edubench` | QG question generation | 0.35 | **insufficient_evidence** |
| P18 适配性解释与反馈生成 | formative | artifact_generation | `edubench` | TMG teaching material generation | 0.4 | **insufficient_evidence** |
| P18 适配性解释与反馈生成 | formative | dialogic_feedback | `eduguard_adversarial` | Refusal quality distribution | 0.25 | **insufficient_evidence** |
| P18 适配性解释与反馈生成 | formative | artifact_generation | `eduillustrate` | 8-dim 0-5 visual explanation score | 0.3 | **insufficient_evidence** |
| P18 适配性解释与反馈生成 | formative | dialogic_feedback | `mathtutorbench_pedagogy_hard` | Pedagogy IF hard | 0.3 | **insufficient_evidence** |
| P18 适配性解释与反馈生成 | formative | dialogic_feedback | `mathtutorbench_scaffolding` | Scaffolding | 0.35 | **insufficient_evidence** |
| P18 适配性解释与反馈生成 | formative | dialogic_feedback | `mathtutorbench_scaffolding_hard` | Scaffolding hard | 0.35 | **insufficient_evidence** |
| P18 适配性解释与反馈生成 | formative | dialogic_feedback | `mmtutorbench` | multimodal tutor score | 0.4 | **insufficient_evidence** |
| P18 适配性解释与反馈生成 | formative | dialogic_feedback | `mrbench_tutor` | 8-dimension tutor pass rate | 0.45 | **insufficient_evidence** |
| P18 适配性解释与反馈生成 | formative | dialogic_feedback | `edubench` | IP idea provision / heuristic answer | 0.35 | **variance_restricted** |
| P18 适配性解释与反馈生成 | formative | artifact_generation | `edubench` | PCC pedagogical/personalized content creation | 0.45 | **variance_restricted** |
| P18 适配性解释与反馈生成 | formative | dialogic_feedback | `edubench` | PLS personalized learning support | 0.25 | **variance_restricted** |
| P18 适配性解释与反馈生成 | formative | dialogic_feedback | `mathtutorbench_mistake_correction` | Mistake Correction | 0.35 | **variance_restricted** |
| P18 适配性解释与反馈生成 | formative | dialogic_feedback | `mathtutorbench_pedagogy` | Pedagogy IF | 0.3 | **variance_restricted** |
| P18 适配性解释与反馈生成 | formative | dialogic_feedback | `mathtutorbench_socratic` | Socratic Questioning | 0.35 | **variance_restricted** |
| P18 适配性解释与反馈生成 | formative | dialogic_feedback | `tutorbench` | Fair815 multimodal tutor quality | 0.4 | **variance_restricted** |
| P20 教育角色边界判断 | formative | boundary_behavior | `eduguard_adversarial` | Adversarial Safety ASR | 0.3 | **insufficient_evidence** |
| P20 教育角色边界判断 | formative | safety_knowledge | `mrbench_judge` | 8-dimension tutor response judging | 0.3 | **insufficient_evidence** |
| P20 教育角色边界判断 | formative | boundary_behavior | `mrbench_tutor` | 8-dimension tutor pass rate | 0.25 | **insufficient_evidence** |
| P20 教育角色边界判断 | formative | safety_knowledge | `eduguard_sata` | Teaching Harm / SATA RFS | 0.35 | **variance_restricted** |
| P21 学生风险识别 | formative | adversarial_robustness | `eduguard_adversarial` | Adversarial Safety ASR | 0.25 | **insufficient_evidence** |
| P21 学生风险识别 | formative | safety_knowledge | `eduguard_sata` | Teaching Harm / SATA RFS | 0.3 | **variance_restricted** |
| P22 安全处置选择 | formative | adversarial_robustness | `eduguard_adversarial` | Adversarial Safety ASR | 0.45 | **insufficient_evidence** |
| P22 安全处置选择 | formative | adversarial_robustness | `eduguard_adversarial` | Refusal quality distribution | 0.6 | **insufficient_evidence** |
| P22 安全处置选择 | formative | safety_knowledge | `eduguard_sata` | Teaching Harm / SATA RFS | 0.35 | **variance_restricted** |

## 低置信附录（3 ≤ n < 5，仅呈现不评级）

| A | B | 共享 P | n | ρ |
|---|---|---|---:|---:|
| `edubench` IP idea provision / heuristic answer | `mathtutorbench_mistake_correction` Mistake Correction | P18(0.35/0.35) | 4 | -0.6 |
| `asap_2` essay holistic QWK | `mathtutorbench_mistake_location` Mistake Location | P02(0.2/0.2) | 3 | -0.5 |
| `asap_2` essay holistic QWK | `sas_bench` CCS step scoring consistency | P02(0.2/0.2), P14(0.65/0.55) | 4 | -0.4 |
| `asap_2` essay holistic QWK | `sas_bench` QWK holistic total score | P14(0.65/0.7) | 4 | -0.4 |
| `edubench` QG question generation | `mathtutorbench_mistake_correction` Mistake Correction | P06(0.35/0.2), P18(0.35/0.35 异facet) | 4 | -0.4 |
| `edubench` PLS personalized learning support | `mathtutorbench_mistake_correction` Mistake Correction | P18(0.25/0.35) | 4 | -0.2 |
| `edubench` TMG teaching material generation | `mathtutorbench_mistake_correction` Mistake Correction | P06(0.25/0.2), P18(0.4/0.35 异facet) | 4 | -0.2 |
| `bea2025_tutor` pedagogical pass rate | `mathtutorbench_mistake_correction` Mistake Correction | P13(0.25/0.45), P18(0.45/0.35) | 3 | 0.5 |
| `bea2025_tutor` pedagogical pass rate | `mathtutorbench_pedagogy` Pedagogy IF | P17(0.3/0.45), P18(0.45/0.3) | 3 | 0.5 |
| `bea2025_tutor` pedagogical pass rate | `mathtutorbench_pedagogy_hard` Pedagogy IF hard | P17(0.3/0.45), P18(0.45/0.3) | 3 | 0.5 |
| `bea2025_tutor` pedagogical pass rate | `mathtutorbench_scaffolding` Scaffolding | P17(0.3/0.5), P18(0.45/0.35) | 3 | 0.5 |
| `bea2025_tutor` pedagogical pass rate | `mathtutorbench_scaffolding_hard` Scaffolding hard | P17(0.3/0.5), P18(0.45/0.35) | 3 | 0.5 |
| `bea2025_tutor` pedagogical pass rate | `mathtutorbench_socratic` Socratic Questioning | P17(0.3/0.65), P18(0.45/0.35) | 3 | 0.5 |
| `edubench` IP idea provision / heuristic answer | `mathtutorbench_socratic` Socratic Questioning | P17(0.4/0.65), P18(0.35/0.35) | 3 | 0.5 |
| `edubench` PCC pedagogical/personalized content creation | `mathtutorbench_socratic` Socratic Questioning | P17(0.3/0.65), P18(0.45/0.35 异facet) | 3 | 0.5 |
| `edubench` PLS personalized learning support | `mathtutorbench_socratic` Socratic Questioning | P17(0.45/0.65), P18(0.25/0.35) | 3 | 0.5 |
| `mathtutorbench_mistake_correction` Mistake Correction | `mrbench_tutor` 8-dimension tutor pass rate | P18(0.35/0.45) | 3 | 0.5 |
| `mathtutorbench_mistake_correction` Mistake Correction | `sas_bench` ECS error-cause consistency | P13(0.45/0.7) | 3 | 0.5 |
| `mathtutorbench_mistake_location` Mistake Location | `sas_bench` CCS step scoring consistency | P02(0.2/0.2), P12(0.7/0.25) | 3 | 0.5 |
| `mathtutorbench_pedagogy` Pedagogy IF | `mrbench_tutor` 8-dimension tutor pass rate | P17(0.45/0.3), P18(0.3/0.45) | 3 | 0.5 |
| `mathtutorbench_pedagogy` Pedagogy IF | `sas_bench` ECS error-cause consistency | P05(0.25/0.2) | 3 | 0.5 |
| `mathtutorbench_pedagogy_hard` Pedagogy IF hard | `mrbench_tutor` 8-dimension tutor pass rate | P17(0.45/0.3), P18(0.3/0.45) | 3 | 0.5 |
| `mathtutorbench_pedagogy_hard` Pedagogy IF hard | `sas_bench` ECS error-cause consistency | P05(0.25/0.2) | 3 | 0.5 |
| `mathtutorbench_scaffolding` Scaffolding | `mrbench_tutor` 8-dimension tutor pass rate | P17(0.5/0.3), P18(0.35/0.45) | 3 | 0.5 |
| `mathtutorbench_scaffolding_hard` Scaffolding hard | `mrbench_tutor` 8-dimension tutor pass rate | P17(0.5/0.3), P18(0.35/0.45) | 3 | 0.5 |
| `mathtutorbench_socratic` Socratic Questioning | `mrbench_tutor` 8-dimension tutor pass rate | P17(0.65/0.3), P18(0.35/0.45) | 3 | 0.5 |
| `agieval` overall/task/language/question_type accuracy | `mathtutorbench_problem_solving` Problem Solving | P05(0.35/0.3), P06(0.45/0.6) | 4 | 1.0 |
| `bea2025_tutor` pedagogical pass rate | `mrbench_tutor` 8-dimension tutor pass rate | P17(0.3/0.3), P18(0.45/0.45) | 3 | 1.0 |
| `ceval` overall/category/subject accuracy | `mathtutorbench_problem_solving` Problem Solving | P05(0.6/0.3), P06(0.25/0.6) | 4 | 1.0 |
| `mathtutorbench_problem_solving` Problem Solving | `mmlu_pro` overall/category accuracy | P05(0.3/0.6), P06(0.6/0.3) | 4 | 1.0 |

## 形成型跨 facet 配对（facet_distinct_expected，信息呈现，不触发红旗）

| A | B | 共享 P | n | ρ |
|---|---|---|---:|---:|
| `edubench` IP idea provision / heuristic answer | `pedagogy_benchmark` CDPK/SEND aggregate from 0701 card | P05(0.25/0.4 异facet), P17(0.4/0.3 异facet) | 5 | -0.9 |
| `edubench` PLS personalized learning support | `pedagogy_benchmark` CDPK/SEND aggregate from 0701 card | P16(0.3/0.3 异facet), P17(0.45/0.3 异facet) | 5 | -0.3 |
| `edubench` TMG teaching material generation | `pedagogy_benchmark` CDPK/SEND aggregate from 0701 card | P05(0.35/0.4 异facet) | 5 | -0.3 |
| `edubench` TMG teaching material generation | `mathtutorbench_scaffolding` Scaffolding | P18(0.4/0.35 异facet) | 6 | -0.257 |
| `edubench` TMG teaching material generation | `mathtutorbench_scaffolding_hard` Scaffolding hard | P18(0.4/0.35 异facet) | 6 | -0.257 |
| `edubench` QG question generation | `mathtutorbench_scaffolding` Scaffolding | P18(0.35/0.35 异facet) | 6 | -0.143 |
| `edubench` QG question generation | `mathtutorbench_scaffolding_hard` Scaffolding hard | P18(0.35/0.35 异facet) | 6 | -0.143 |
| `edubench` PCC pedagogical/personalized content creation | `pedagogy_benchmark` CDPK/SEND aggregate from 0701 card | P05(0.25/0.4 异facet), P17(0.3/0.3 异facet) | 5 | -0.1 |
| `edubench` QG question generation | `pedagogy_benchmark` CDPK/SEND aggregate from 0701 card | P05(0.3/0.4 异facet) | 5 | -0.1 |
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