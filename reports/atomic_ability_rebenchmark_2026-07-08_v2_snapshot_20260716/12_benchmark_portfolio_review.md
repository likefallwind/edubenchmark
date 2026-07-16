# Benchmark Portfolio Review

目的：先用两个直观指标判断当前 benchmark 是否还值得继续重点做。

## 两个主指标

1. **所有模型平均分**：对进入最终计算的 canonical score rows，在同一个 benchmark/subdimension 下跨模型取 `score_10` 平均。分数越高，说明当前模型整体越接近解决；分数越低，越有继续区分模型的价值。`NA` 表示该 mapping 目前没有进入最终计分的模型结果。
2. **原子能力有效相关性**：只由 mapping 决定，不看模型表现。公式：`100 × benchmark_weight × tier_factor × Σ(P_priority × ability_weight)`。其中 `tier_factor`: education_core=1.00, diagnostic=0.75, foundation_gate=0.45, excluded_judge_task=0.08。

辅助列：`P 相关性` 是不乘 benchmark/tier 的纯 P 能力相关性；`tier` 表示证据直接性。基础答题类通常会因为 `foundation_gate` 被降权。

## 先看结论排序

| 建议 | Benchmark | Subdimension | 所有模型平均分 | 原子能力有效相关性 | P 相关性 | tier | 模型数 | P 映射 |
|---|---|---|---:|---:|---:|---|---:|---|
| 值得继续做 | `eduguard_adversarial` EduGuard-Bench P2 | Adversarial Safety ASR | 6.92 | 100.00 | 100.00 | education_core | 7 | P20 0.30, P21 0.25, P22 0.45 |
| 值得继续做 | `eduguard_sata` EduGuard-Bench P1 | Teaching Harm / SATA RFS | 7.47 | 100.00 | 100.00 | education_core | 8 | P20 0.35, P21 0.30, P22 0.35 |
| 优先继续做 | `mathtutorbench_scaffolding_hard` MathTutorBench | Scaffolding hard | 2.92 | 89.00 | 89.00 | education_core | 7 | P05 0.15, P17 0.50, P18 0.35 |
| 优先继续做 | `mathtutorbench_scaffolding` MathTutorBench | Scaffolding | 3.23 | 89.00 | 89.00 | education_core | 7 | P05 0.15, P17 0.50, P18 0.35 |
| 优先继续做 | `tutorbench` TutorBench | Fair815 multimodal tutor quality | 5.48 | 88.75 | 88.75 | education_core | 6 | P03 0.25, P17 0.35, P18 0.40 |
| 优先继续做 | `sas_bench` SAS-Bench | ECS error-cause consistency | 5.83 | 84.00 | 84.00 | education_core | 6 | P05 0.20, P06 0.10, P13 0.70 |
| 优先继续做 | `asap_2` ASAP 2.0 | essay holistic QWK | 5.45 | 68.60 | 85.75 | education_core | 7 | P02 0.20, P05 0.15, P14 0.65 |
| 高相关但缺跑分 | `pedagogy_benchmark` Pedagogy Benchmark | SEND special education needs selection | NA | 68.20 | 85.25 | education_core | 0 | P05 0.35, P16 0.35, P17 0.30 |
| 高相关但缺跑分 | `mmtutorbench` MMTutorBench | multimodal tutor score | NA | 59.06 | 87.50 | diagnostic | 0 | P03 0.30, P17 0.30, P18 0.40 |
| 优先继续做 | `p08_calibration` P08 置信度校准 | calibration composite (CWR/AUROC) | 6.44 | 58.01 | 91.00 | diagnostic | 5 | P07 0.20, P08 0.80 |
| 优先继续做 | `mathtutorbench_socratic` MathTutorBench | Socratic Questioning | 2.73 | 57.00 | 95.00 | education_core | 4 | P17 0.65, P18 0.35 |
| 优先继续做 | `edubench` EduBench | personalized_adaptation_learning_support (metric) | 6.29 | 56.80 | 71.00 | education_core | 11 | P16 0.30, P17 0.40 |
| 高相关但缺跑分 | `mooccube_prereq` MOOCCube 先修关系推理 | chance-corrected composite (先修选择 + 学习顺序排序) | NA | 47.25 | 90.00 | diagnostic | 0 | P05 0.20, P06 0.10, P19 0.70 |
| 高相关但缺跑分 | `pedagogy_benchmark` Pedagogy Benchmark | CDPK teaching knowledge selection | NA | 46.40 | 58.00 | education_core | 0 | P05 0.45, P17 0.35 |
| 重要但可降频 | `mathtutorbench_mistake_location` MathTutorBench | Mistake Location | 7.75 | 90.50 | 90.50 | education_core | 5 | P02 0.20, P11 0.10, P12 0.70 |
| 重要但可降频 | `sas_bench` SAS-Bench | CCS step scoring consistency | 7.63 | 86.45 | 91.00 | education_core | 6 | P02 0.20, P12 0.25, P14 0.55 |
| 重要但可降频 | `mathtutorbench_pedagogy_hard` MathTutorBench | Pedagogy IF hard | 7.92 | 85.00 | 85.00 | education_core | 7 | P05 0.25, P17 0.45, P18 0.30 |
| 重要但可降频 | `mathtutorbench_pedagogy` MathTutorBench | Pedagogy IF | 8.25 | 80.75 | 85.00 | education_core | 7 | P05 0.25, P17 0.45, P18 0.30 |
| 重要但可降频 | `sas_bench` SAS-Bench | QWK holistic total score | 8.24 | 78.30 | 87.00 | education_core | 6 | P02 0.15, P05 0.15, P14 0.70 |
| 重要但可降频 | `mathtutorbench_solution_correctness` MathTutorBench | Solution Correctness | 8.68 | 72.67 | 85.50 | education_core | 5 | P02 0.15, P07 0.25, P11 0.60 |
| 重要但可降频 | `pedagogy_benchmark` Pedagogy Benchmark | CDPK/SEND aggregate from 0701 card | 8.56 | 66.80 | 83.50 | education_core | 7 | P05 0.40, P16 0.30, P17 0.30 |
| 重要但可降频 | `mathtutorbench_mistake_correction` MathTutorBench | Mistake Correction | 9.02 | 58.72 | 65.25 | education_core | 5 | P06 0.20, P13 0.20, P18 0.35 |
| 重要但可降频 | `p08_abstention` P08 能力性弃答 | balanced abstention score | 8.90 | 55.78 | 87.50 | diagnostic | 5 | P01 0.15, P08 0.85 |
| 诊断保留 | `p07_selfcheck` P07 两轮自查 | two-round self-check (fix/break rate) | 5.29 | 49.72 | 78.00 | diagnostic | 5 | P07 0.85, P08 0.15 |
| 不必重点看 | `eduillustrate` EduIllustrate | 8-dim 0-5 visual explanation score | 6.93 | 47.81 | 75.00 | diagnostic | 4 | P10 0.45, P18 0.30 |
| 不必重点看 | `eduguard_adversarial` EduGuard-Bench P2 | Refusal quality distribution | 6.71 | 46.72 | 89.00 | diagnostic | 7 | P18 0.10, P20 0.15, P22 0.60 |
| 暂不判断 | `k12vista` K12Vista | official partial-credit score (per-blank 0/1 mean) | NA | 39.75 | 66.25 | diagnostic | 0 | P03 0.55, P05 0.15, P06 0.30 |
| 不必重点看 | `mathvista` MathVista | task/question_type/answer_type accuracy | 8.41 | 33.99 | 64.75 | diagnostic | 1 | P03 0.35, P05 0.20, P06 0.45 |
| 不必重点看 | `edubench` EduBench | higher_order_thinking_ability_development (metric) | 7.44 | 29.40 | 36.75 | education_core | 11 | P06 0.20, P18 0.25 |
| 不必重点看 | `longtutor_evidence` LongTutor 证据抽取 | semantic evidence accuracy (3 memory types) | 7.95 | 28.97 | 51.50 | diagnostic | 3 | P02 0.70 |
| 不必重点看 | `edubench` EduBench | QG/TMG/PCC × clarity_concision_inspiration + scenario_element_integration (task×metric) | 8.15 | 28.50 | 38.00 | education_core | 11 | P18 0.40 |
| 诊断保留 | `edubench` EduBench | motivation_guidance_positive_feedback (metric) | 6.41 | 26.60 | 33.25 | education_core | 11 | P18 0.35 |
| 不必重点看 | `bea2025_tutor` BEA 2025 Tutor | dimension: Providing_Guidance | 9.63 | 25.65 | 28.50 | education_core | 3 | P17 0.30 |
| 诊断保留 | `longtutor_diagnosis` LongTutor 知识状态诊断 | four-category knowledge-state diagnosis macro-F1 | 2.87 | 23.91 | 42.50 | diagnostic | 3 | P13 0.10, P16 0.30 |
| 不必重点看 | `edubench` EduBench | clarity_concision_inspiration (metric) | 8.38 | 22.80 | 28.50 | education_core | 11 | P18 0.30 |
| 不必重点看 | `mrbench_tutor` MRBench Tutor | dimension: Providing_Guidance | 9.05 | 22.80 | 28.50 | education_core | 3 | P17 0.30 |
| 不必重点看 | `bea2025_tutor` BEA 2025 Tutor | dimension: Mistake_Identification | 8.32 | 21.38 | 23.75 | education_core | 3 | P13 0.25 |
| 不必重点看 | `edubench` EduBench | error_identification_correction_accuracy (metric) | 7.45 | 19.00 | 23.75 | education_core | 11 | P13 0.25 |
| 不必重点看 | `edubench` EduBench | scenario_element_integration (metric) | 7.68 | 19.00 | 23.75 | education_core | 11 | P17 0.25 |
| 不必重点看 | `mrbench_tutor` MRBench Tutor | dimension: Mistake_Identification | 9.02 | 19.00 | 23.75 | education_core | 3 | P13 0.25 |
| 不必重点看 | `edubench` EduBench | reasoning_process_rigor (metric) | 8.22 | 18.20 | 22.75 | education_core | 11 | P06 0.35 |
| 不必重点看 | `mrbench_tutor` MRBench Tutor | dimension: Tutor_Tone | 9.68 | 18.00 | 22.50 | education_core | 3 | P20 0.25 |
| 不必重点看 | `bea2025_tutor` BEA 2025 Tutor | dimension: Actionability | 9.31 | 17.10 | 19.00 | education_core | 3 | P18 0.20 |
| 低频门槛 | `ifeval` IFEval | prompt-level strict accuracy | 9.06 | 16.20 | 45.00 | foundation_gate | 5 | P01 1.00 |
| 不必重点看 | `longtutor_teaching` LongTutor 教学动作 | judge dims: strategy_alignment + history_utilization (1-5) | 6.67 | 16.03 | 28.50 | diagnostic | 3 | P17 0.30 |
| 门槛保留 | `olympiadbench` OlympiadBench | overall/subject/language/modality accuracy | 7.26 | 15.72 | 63.50 | foundation_gate | 2 | P03 0.20, P05 0.25, P06 0.55 |
| 不必重点看 | `edubench` EduBench | domain_knowledge_accuracy (metric) | 8.69 | 15.40 | 19.25 | education_core | 11 | P05 0.35 |
| 不必重点看 | `mrbench_tutor` MRBench Tutor | dimension: Actionability | 9.10 | 15.20 | 19.00 | education_core | 3 | P18 0.20 |
| 不必重点看 | `edubench` EduBench | basic_factual_accuracy (metric) | 9.10 | 13.20 | 16.50 | education_core | 11 | P05 0.30 |
| 低频门槛 | `mathtutorbench_problem_solving` MathTutorBench | Problem Solving | 9.70 | 12.76 | 63.00 | foundation_gate | 4 | P05 0.30, P06 0.60, P07 0.10 |
| 低频门槛 | `agieval` AGIEval | overall/task/language/question_type accuracy | 8.74 | 10.35 | 57.50 | foundation_gate | 5 | P01 0.20, P05 0.35, P06 0.45 |
| 低频门槛 | `mmlu_pro` MMLU-Pro | overall/category accuracy | 8.60 | 8.98 | 57.00 | foundation_gate | 5 | P01 0.10, P05 0.60, P06 0.30 |
| 低频门槛 | `ceval` C-EVAL | overall/category/subject accuracy | 9.11 | 8.82 | 56.00 | foundation_gate | 5 | P01 0.15, P05 0.60, P06 0.25 |
| 不必重点看 | `edubench` EduBench | tone_style_consistency (metric) | 8.48 | 7.60 | 9.50 | education_core | 11 | P18 0.10 |
| 先排除 | `bea2025_judge` BEA 2025 Judge | judge labels: mistake/guidance/actionability | NA | 0.00 | 90.25 | excluded_judge_task | 0 | P11 0.25, P13 0.30, P14 0.45 |
| 先排除 | `mrbench_judge` MRBench Judge | 8-dimension tutor response judging | NA | 0.00 | 91.25 | excluded_judge_task | 0 | P13 0.25, P14 0.45, P20 0.30 |

## 按 benchmark 聚合

聚合口径：同一 benchmark 的多个 subdimension 先各自计算平均分和相关性，再在 benchmark 内做简单平均；只用于概览，具体判断仍看上面的 subdimension 明细。

| 建议 | Benchmark | Subdimension 数 | benchmark 平均分 | 平均原子相关性 | tier | P 覆盖 |
|---|---|---:|---:|---:|---|---|
| 值得继续做 | `eduguard_sata` EduGuard-Bench P1 | 1 | 7.47 | 100.00 | education_core | P20, P21, P22 |
| 优先继续做 | `mathtutorbench_scaffolding_hard` MathTutorBench | 1 | 2.92 | 89.00 | education_core | P05, P17, P18 |
| 优先继续做 | `mathtutorbench_scaffolding` MathTutorBench | 1 | 3.23 | 89.00 | education_core | P05, P17, P18 |
| 优先继续做 | `tutorbench` TutorBench | 1 | 5.48 | 88.75 | education_core | P03, P17, P18 |
| 优先继续做 | `asap_2` ASAP 2.0 | 1 | 5.45 | 68.60 | education_core | P02, P05, P14 |
| 高相关但缺跑分 | `pedagogy_benchmark` Pedagogy Benchmark | 3 | 8.56 | 60.47 | education_core | P05, P16, P17 |
| 高相关但缺跑分 | `mmtutorbench` MMTutorBench | 1 | NA | 59.06 | diagnostic | P03, P17, P18 |
| 优先继续做 | `p08_calibration` P08 置信度校准 | 1 | 6.44 | 58.01 | diagnostic | P07, P08 |
| 优先继续做 | `mathtutorbench_socratic` MathTutorBench | 1 | 2.73 | 57.00 | education_core | P17, P18 |
| 高相关但缺跑分 | `mooccube_prereq` MOOCCube 先修关系推理 | 1 | NA | 47.25 | diagnostic | P05, P06, P19 |
| 重要但可降频 | `mathtutorbench_mistake_location` MathTutorBench | 1 | 7.75 | 90.50 | education_core | P02, P11, P12 |
| 重要但可降频 | `mathtutorbench_pedagogy_hard` MathTutorBench | 1 | 7.92 | 85.00 | education_core | P05, P17, P18 |
| 重要但可降频 | `sas_bench` SAS-Bench | 3 | 7.23 | 82.92 | education_core | P02, P05, P06, P12, P13, P14 |
| 重要但可降频 | `mathtutorbench_pedagogy` MathTutorBench | 1 | 8.25 | 80.75 | education_core | P05, P17, P18 |
| 不必重点看 | `eduguard_adversarial` EduGuard-Bench P2 | 2 | 6.81 | 73.36 | diagnostic, education_core | P18, P20, P21, P22 |
| 重要但可降频 | `mathtutorbench_solution_correctness` MathTutorBench | 1 | 8.68 | 72.67 | education_core | P02, P07, P11 |
| 重要但可降频 | `mathtutorbench_mistake_correction` MathTutorBench | 1 | 9.02 | 58.72 | education_core | P06, P13, P18 |
| 重要但可降频 | `p08_abstention` P08 能力性弃答 | 1 | 8.90 | 55.78 | diagnostic | P01, P08 |
| 诊断保留 | `p07_selfcheck` P07 两轮自查 | 1 | 5.29 | 49.72 | diagnostic | P07, P08 |
| 不必重点看 | `eduillustrate` EduIllustrate | 1 | 6.93 | 47.81 | diagnostic | P10, P18 |
| 暂不判断 | `k12vista` K12Vista | 1 | NA | 39.75 | diagnostic | P03, P05, P06 |
| 不必重点看 | `mathvista` MathVista | 1 | 8.41 | 33.99 | diagnostic | P03, P05, P06 |
| 不必重点看 | `longtutor_evidence` LongTutor 证据抽取 | 1 | 7.95 | 28.97 | diagnostic | P02 |
| 诊断保留 | `longtutor_diagnosis` LongTutor 知识状态诊断 | 1 | 2.87 | 23.91 | diagnostic | P13, P16 |
| 不必重点看 | `edubench` EduBench | 11 | 7.84 | 23.32 | education_core | P05, P06, P13, P16, P17, P18 |
| 不必重点看 | `bea2025_tutor` BEA 2025 Tutor | 3 | 9.09 | 21.38 | education_core | P13, P17, P18 |
| 不必重点看 | `mrbench_tutor` MRBench Tutor | 4 | 9.21 | 18.75 | education_core | P13, P17, P18, P20 |
| 低频门槛 | `ifeval` IFEval | 1 | 9.06 | 16.20 | foundation_gate | P01 |
| 不必重点看 | `longtutor_teaching` LongTutor 教学动作 | 1 | 6.67 | 16.03 | diagnostic | P17 |
| 门槛保留 | `olympiadbench` OlympiadBench | 1 | 7.26 | 15.72 | foundation_gate | P03, P05, P06 |
| 低频门槛 | `mathtutorbench_problem_solving` MathTutorBench | 1 | 9.70 | 12.76 | foundation_gate | P05, P06, P07 |
| 低频门槛 | `agieval` AGIEval | 1 | 8.74 | 10.35 | foundation_gate | P01, P05, P06 |
| 低频门槛 | `mmlu_pro` MMLU-Pro | 1 | 8.60 | 8.98 | foundation_gate | P01, P05, P06 |
| 低频门槛 | `ceval` C-EVAL | 1 | 9.11 | 8.82 | foundation_gate | P01, P05, P06 |
| 先排除 | `bea2025_judge` BEA 2025 Judge | 1 | NA | 0.00 | excluded_judge_task | P11, P13, P14 |
| 先排除 | `mrbench_judge` MRBench Judge | 1 | NA | 0.00 | excluded_judge_task | P13, P14, P20 |

## 校准提示

- `所有模型平均分` 高但 `原子能力有效相关性` 低：通常不需要重点看，适合做门槛或背景参考。
- `所有模型平均分` 低且 `原子能力有效相关性` 高：优先继续做，因为它既重要又还没被解决好。
- `NA` 且相关性高：说明 mapping 认为它重要，但当前主计分层缺结果，应该优先补跑或确认数据源。
- foundation gate 不等于没用，只是不应主导教育能力判断；它更适合筛掉基础能力不足的模型。
