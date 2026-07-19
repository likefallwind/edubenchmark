# Benchmark Portfolio Review

目的：先用两个直观指标判断当前 benchmark 是否还值得继续重点做。

## 两个主指标

1. **所有模型平均分**：对进入最终计算的 canonical score rows，在同一个 benchmark/subdimension 下跨模型取 `score_10` 平均。分数越高，说明当前模型整体越接近解决；分数越低，越有继续区分模型的价值。`NA` 表示该 mapping 目前没有进入最终计分的模型结果。
2. **原子能力有效相关性**：只由 mapping 决定，不看模型表现。公式（R20，无 tier 因子）：`100 × benchmark_weight × Σ(P_priority × ability_weight)`。

辅助列：`P 相关性` 是不乘 benchmark 置信权重的纯 P 能力相关性。

## 先看结论排序

| 建议 | Benchmark | Subdimension | 所有模型平均分 | 原子能力有效相关性 | P 相关性 | 模型数 | P 映射 |
|---|---|---|---:|---:|---:|---:|---|
| 值得继续做 | `eduguard_sata` EduGuard-Bench P1 | Teaching Harm / SATA RFS | 7.47 | 100.00 | 100.00 | 8 | P17 0.35, P18 0.30, P19 0.35 |
| 优先继续做 | `mathtutorbench_scaffolding_hard` MathTutorBench | Scaffolding hard | 2.92 | 89.00 | 89.00 | 7 | P05 0.15, P14 0.50, P16 0.35 |
| 优先继续做 | `mathtutorbench_scaffolding` MathTutorBench | Scaffolding | 3.23 | 89.00 | 89.00 | 7 | P05 0.15, P14 0.50, P16 0.35 |
| 优先继续做 | `sas_bench` SAS-Bench | ECS error-cause consistency | 5.58 | 84.00 | 84.00 | 8 | P05 0.20, P06 0.10, P10 0.70 |
| 值得继续做 | `mmtutorbench` MMTutorBench | multimodal tutor score | 6.67 | 78.75 | 87.50 | 2 | P03 0.30, P14 0.30, P16 0.40 |
| 值得继续做 | `eduguard_adversarial` EduGuard-Bench P2 | Adversarial Safety ASR | 6.92 | 78.00 | 78.00 | 7 | P17 0.30, P19 0.45 |
| 优先继续做 | `p08_calibration` P08 置信度校准 | calibration composite (CWR/AUROC) | 6.44 | 77.35 | 91.00 | 5 | P07 0.20, P08 0.80 |
| 优先继续做 | `tutorbench` TutorBench | Fair815 multimodal tutor quality | 5.48 | 71.00 | 88.75 | 6 | P03 0.25, P14 0.35, P16 0.40 |
| 优先继续做 | `p07_selfcheck` P07 两轮自查 | two-round self-check (fix/break rate) | 5.29 | 66.30 | 78.00 | 5 | P07 0.85, P08 0.15 |
| 值得继续做 | `eduguard_adversarial` EduGuard-Bench P2 | Refusal quality distribution | 6.71 | 63.60 | 79.50 | 7 | P17 0.15, P19 0.60 |
| 值得继续做 | `eduillustrate` EduIllustrate | 8-dim 0-5 visual explanation score | 6.93 | 59.71 | 70.25 | 4 | P04 0.45, P16 0.25 |
| 优先继续做 | `edubench` EduBench | personalized_adaptation_learning_support (metric) | 6.34 | 56.80 | 71.00 | 12 | P13 0.30, P14 0.40 |
| 重要但可降频 | `mathtutorbench_pedagogy_hard` MathTutorBench | Pedagogy IF hard | 7.92 | 85.00 | 85.00 | 7 | P05 0.25, P14 0.45, P16 0.30 |
| 重要但可降频 | `sas_bench` SAS-Bench | CCS step scoring consistency | 7.65 | 84.55 | 89.00 | 8 | P02 0.15, P10 0.25, P11 0.55 |
| 重要但可降频 | `mathtutorbench_mistake_location` MathTutorBench | Mistake Location | 7.75 | 82.25 | 82.25 | 5 | P02 0.15, P10 0.70 |
| 重要但可降频 | `mathtutorbench_pedagogy` MathTutorBench | Pedagogy IF | 8.25 | 80.75 | 85.00 | 7 | P05 0.25, P14 0.45, P16 0.30 |
| 重要但可降频 | `p08_abstention` P08 能力性弃答 | balanced abstention score | 8.90 | 68.64 | 80.75 | 5 | P08 0.85 |
| 重要但可降频 | `pedagogy_benchmark` Pedagogy Benchmark | SEND special education needs selection | 7.88 | 68.60 | 85.75 | 11 | P05 0.35, P13 0.25, P14 0.40 |
| 重要但可降频 | `pedagogy_benchmark` Pedagogy Benchmark | CDPK teaching knowledge selection | 8.50 | 65.40 | 81.75 | 11 | P05 0.45, P14 0.60 |
| 重要但可降频 | `mathtutorbench_solution_correctness` MathTutorBench | Solution Correctness | 8.68 | 64.39 | 75.75 | 5 | P07 0.25, P10 0.60 |
| 重要但可降频 | `mathtutorbench_mistake_correction` MathTutorBench | Mistake Correction | 9.02 | 58.72 | 65.25 | 5 | P06 0.20, P10 0.20, P16 0.35 |
| 重要但可降频 | `sas_bench` SAS-Bench | QWK holistic total score | 8.27 | 56.70 | 63.00 | 8 | P11 0.70 |
| 诊断保留 | `mooccube_prereq` MOOCCube 先修关系推理 | chance-corrected composite (先修选择 + 学习顺序排序) | 4.28 | 50.75 | 72.50 | 5 | P15 0.70 |
| 诊断保留 | `asap_2` ASAP 2.0 | essay holistic QWK | 5.45 | 46.80 | 58.50 | 7 | P11 0.65 |
| 不必重点看 | `mathvista` MathVista | task/question_type/answer_type accuracy | 8.41 | 45.32 | 64.75 | 1 | P03 0.35, P05 0.20, P06 0.45 |
| 诊断保留 | `mathtutorbench_socratic` MathTutorBench | Socratic Questioning | 2.73 | 42.75 | 71.25 | 4 | P14 0.40, P16 0.35 |
| 不必重点看 | `edubench` EduBench | TMG/PCC × clarity_concision_inspiration + scenario_element_integration (task×metric) | 8.19 | 39.19 | 52.25 | 12 | P16 0.55 |
| 不必重点看 | `longtutor_evidence` LongTutor 证据抽取 | Multi-session Reasoning accuracy | 6.71 | 38.62 | 51.50 | 4 | P02 0.70 |
| 不必重点看 | `longtutor_evidence` LongTutor 证据抽取 | Hallucination Check accuracy | 6.94 | 38.62 | 51.50 | 4 | P02 0.70 |
| 不必重点看 | `longtutor_evidence` LongTutor 证据抽取 | Information Extraction accuracy | 9.58 | 38.62 | 51.50 | 4 | P02 0.70 |
| 不必重点看 | `mmlu_pro` MMLU-Pro | overall/category accuracy | 8.60 | 36.75 | 52.50 | 5 | P05 0.60, P06 0.30 |
| 不必重点看 | `ifeval` IFEval | prompt-level strict accuracy | 9.06 | 36.00 | 45.00 | 5 | P01 1.00 |
| 不必重点看 | `olympiadbench` OlympiadBench | overall/subject/language/modality accuracy | 7.26 | 34.65 | 49.50 | 2 | P05 0.25, P06 0.55 |
| 不必重点看 | `ceval` C-EVAL | overall/category/subject accuracy | 9.11 | 34.48 | 49.25 | 5 | P05 0.60, P06 0.25 |
| 不必重点看 | `agieval` AGIEval | overall/task/language/question_type accuracy | 8.74 | 33.95 | 48.50 | 5 | P05 0.35, P06 0.45 |
| 诊断保留 | `longtutor_diagnosis` LongTutor 知识状态诊断 | four-category knowledge-state diagnosis macro-F1 | 2.65 | 31.88 | 42.50 | 4 | P10 0.10, P13 0.30 |
| 不必重点看 | `k12vista` K12Vista | science/geo subject-chart subset score | 6.77 | 30.80 | 38.50 | 2 | P03 0.55 |
| 诊断保留 | `bea2025_judge` BEA 2025 Judge | judge labels: mistake/guidance/actionability | 4.96 | 30.38 | 40.50 | 6 | P11 0.45 |
| 诊断保留 | `mrbench_judge` MRBench Judge | 8-dimension tutor response judging | 5.12 | 30.38 | 40.50 | 6 | P11 0.45 |
| 不必重点看 | `edubench` EduBench | higher_order_thinking_ability_development (metric) | 7.51 | 29.40 | 36.75 | 12 | P06 0.20, P16 0.25 |
| 不必重点看 | `edubench` EduBench | QG × clarity_concision_inspiration + scenario_element_integration (task×metric) | 8.16 | 27.00 | 36.00 | 12 | P12 0.40 |
| 诊断保留 | `edubench` EduBench | motivation_guidance_positive_feedback (metric) | 6.45 | 26.60 | 33.25 | 12 | P16 0.35 |
| 不必重点看 | `bea2025_tutor` BEA 2025 Tutor | dimension: Providing_Guidance | 9.63 | 25.65 | 28.50 | 3 | P14 0.30 |
| 不必重点看 | `mathtutorbench_problem_solving` MathTutorBench | Problem Solving | 9.70 | 24.98 | 55.50 | 4 | P05 0.30, P06 0.60 |
| 不必重点看 | `edubench` EduBench | clarity_concision_inspiration (metric) | 8.42 | 22.80 | 28.50 | 12 | P16 0.30 |
| 不必重点看 | `mrbench_tutor` MRBench Tutor | dimension: Providing_Guidance | 9.05 | 22.80 | 28.50 | 3 | P14 0.30 |
| 不必重点看 | `k12vista` K12Vista | official partial-credit score (per-blank 0/1 mean) | 6.97 | 22.20 | 27.75 | 2 | P05 0.15, P06 0.30 |
| 不必重点看 | `bea2025_tutor` BEA 2025 Tutor | dimension: Mistake_Identification | 8.32 | 21.38 | 23.75 | 3 | P10 0.25 |
| 诊断保留 | `longtutor_teaching` LongTutor 教学动作 | judge dims: strategy_alignment + history_utilization (1-5) | 5.66 | 21.37 | 28.50 | 4 | P14 0.30 |
| 不必重点看 | `edubench` EduBench | QG × domain_knowledge_accuracy + basic_factual_accuracy (task×metric) | 9.30 | 20.25 | 27.00 | 12 | P12 0.30 |
| 不必重点看 | `k12vista` K12Vista | math problem-figure subset score | 7.54 | 19.60 | 24.50 | 2 | P03 0.35 |
| 不必重点看 | `edubench` EduBench | scenario_element_integration (metric) | 7.68 | 19.00 | 23.75 | 12 | P14 0.25 |
| 不必重点看 | `mrbench_tutor` MRBench Tutor | dimension: Mistake_Identification | 9.02 | 19.00 | 23.75 | 3 | P10 0.25 |
| 不必重点看 | `edubench` EduBench | reasoning_process_rigor (metric) | 8.28 | 18.20 | 22.75 | 12 | P06 0.35 |
| 不必重点看 | `bea2025_tutor` BEA 2025 Tutor | dimension: Actionability | 9.31 | 17.10 | 19.00 | 3 | P16 0.20 |
| 不必重点看 | `edubench` EduBench | domain_knowledge_accuracy (metric) | 8.75 | 15.40 | 19.25 | 12 | P05 0.35 |
| 不必重点看 | `mrbench_tutor` MRBench Tutor | dimension: Actionability | 9.10 | 15.20 | 19.00 | 3 | P16 0.20 |
| 不必重点看 | `mrbench_tutor` MRBench Tutor | dimension: Tutor_Tone (encouraging share) | 9.35 | 15.20 | 19.00 | 3 | P16 0.20 |
| 不必重点看 | `edubench` EduBench | basic_factual_accuracy (metric) | 9.15 | 13.20 | 16.50 | 12 | P05 0.30 |
| 不必重点看 | `mrbench_tutor` MRBench Tutor | dimension: Tutor_Tone (non-offensive) | 10.00 | 7.20 | 9.00 | 3 | P17 0.10 |
| 不必重点看 | `edubench` EduBench | error_identification_correction_accuracy (metric) | 7.41 | 7.12 | 23.75 | 12 | P10 0.25 |
| 不必重点看 | `olympiadbench` OlympiadBench | multimodal-subset accuracy | 6.81 | 4.90 | 7.00 | 1 | P03 0.10 |

## 按 benchmark 聚合

聚合口径：同一 benchmark 的多个 subdimension 先各自计算平均分和相关性，再在 benchmark 内做简单平均；只用于概览，具体判断仍看上面的 subdimension 明细。

| 建议 | Benchmark | Subdimension 数 | benchmark 平均分 | 平均原子相关性 | P 覆盖 |
|---|---|---:|---:|---:|---|
| 值得继续做 | `eduguard_sata` EduGuard-Bench P1 | 1 | 7.47 | 100.00 | P17, P18, P19 |
| 优先继续做 | `mathtutorbench_scaffolding_hard` MathTutorBench | 1 | 2.92 | 89.00 | P05, P14, P16 |
| 优先继续做 | `mathtutorbench_scaffolding` MathTutorBench | 1 | 3.23 | 89.00 | P05, P14, P16 |
| 值得继续做 | `mmtutorbench` MMTutorBench | 1 | 6.67 | 78.75 | P03, P14, P16 |
| 优先继续做 | `p08_calibration` P08 置信度校准 | 1 | 6.44 | 77.35 | P07, P08 |
| 优先继续做 | `tutorbench` TutorBench | 1 | 5.48 | 71.00 | P03, P14, P16 |
| 值得继续做 | `eduguard_adversarial` EduGuard-Bench P2 | 2 | 6.81 | 70.80 | P17, P19 |
| 优先继续做 | `p07_selfcheck` P07 两轮自查 | 1 | 5.29 | 66.30 | P07, P08 |
| 值得继续做 | `eduillustrate` EduIllustrate | 1 | 6.93 | 59.71 | P04, P16 |
| 重要但可降频 | `mathtutorbench_pedagogy_hard` MathTutorBench | 1 | 7.92 | 85.00 | P05, P14, P16 |
| 重要但可降频 | `mathtutorbench_mistake_location` MathTutorBench | 1 | 7.75 | 82.25 | P02, P10 |
| 重要但可降频 | `mathtutorbench_pedagogy` MathTutorBench | 1 | 8.25 | 80.75 | P05, P14, P16 |
| 重要但可降频 | `sas_bench` SAS-Bench | 3 | 7.17 | 75.08 | P02, P05, P06, P10, P11 |
| 重要但可降频 | `p08_abstention` P08 能力性弃答 | 1 | 8.90 | 68.64 | P08 |
| 重要但可降频 | `pedagogy_benchmark` Pedagogy Benchmark | 2 | 8.19 | 67.00 | P05, P13, P14 |
| 重要但可降频 | `mathtutorbench_solution_correctness` MathTutorBench | 1 | 8.68 | 64.39 | P07, P10 |
| 重要但可降频 | `mathtutorbench_mistake_correction` MathTutorBench | 1 | 9.02 | 58.72 | P06, P10, P16 |
| 诊断保留 | `mooccube_prereq` MOOCCube 先修关系推理 | 1 | 4.28 | 50.75 | P15 |
| 诊断保留 | `asap_2` ASAP 2.0 | 1 | 5.45 | 46.80 | P11 |
| 不必重点看 | `mathvista` MathVista | 1 | 8.41 | 45.32 | P03, P05, P06 |
| 诊断保留 | `mathtutorbench_socratic` MathTutorBench | 1 | 2.73 | 42.75 | P14, P16 |
| 不必重点看 | `longtutor_evidence` LongTutor 证据抽取 | 3 | 7.74 | 38.62 | P02 |
| 不必重点看 | `mmlu_pro` MMLU-Pro | 1 | 8.60 | 36.75 | P05, P06 |
| 不必重点看 | `ifeval` IFEval | 1 | 9.06 | 36.00 | P01 |
| 不必重点看 | `ceval` C-EVAL | 1 | 9.11 | 34.48 | P05, P06 |
| 不必重点看 | `agieval` AGIEval | 1 | 8.74 | 33.95 | P05, P06 |
| 诊断保留 | `longtutor_diagnosis` LongTutor 知识状态诊断 | 1 | 2.65 | 31.88 | P10, P13 |
| 诊断保留 | `bea2025_judge` BEA 2025 Judge | 1 | 4.96 | 30.38 | P11 |
| 诊断保留 | `mrbench_judge` MRBench Judge | 1 | 5.12 | 30.38 | P11 |
| 不必重点看 | `mathtutorbench_problem_solving` MathTutorBench | 1 | 9.70 | 24.98 | P05, P06 |
| 不必重点看 | `edubench` EduBench | 12 | 7.97 | 24.58 | P05, P06, P10, P12, P13, P14, P16 |
| 不必重点看 | `k12vista` K12Vista | 3 | 7.09 | 24.20 | P03, P05, P06 |
| 不必重点看 | `bea2025_tutor` BEA 2025 Tutor | 3 | 9.09 | 21.38 | P10, P14, P16 |
| 诊断保留 | `longtutor_teaching` LongTutor 教学动作 | 1 | 5.66 | 21.37 | P14 |
| 不必重点看 | `olympiadbench` OlympiadBench | 2 | 7.03 | 19.77 | P03, P05, P06 |
| 不必重点看 | `mrbench_tutor` MRBench Tutor | 5 | 9.30 | 15.88 | P10, P14, P16, P17 |

## 校准提示

- `所有模型平均分` 高但 `原子能力有效相关性` 低：通常不需要重点看，适合做门槛或背景参考。
- `所有模型平均分` 低且 `原子能力有效相关性` 高：优先继续做，因为它既重要又还没被解决好。
- `NA` 且相关性高：说明 mapping 认为它重要，但当前主计分层缺结果，应该优先补跑或确认数据源。
- foundation gate 不等于没用，只是不应主导教育能力判断；它更适合筛掉基础能力不足的模型。
