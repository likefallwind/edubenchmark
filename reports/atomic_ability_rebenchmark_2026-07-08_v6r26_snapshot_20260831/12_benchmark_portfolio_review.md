# Benchmark Portfolio Review

目的：先用两个直观指标判断当前 benchmark 是否还值得继续重点做。

## 两个主指标

1. **所有模型平均分**：对进入最终计算的 canonical score rows，在同一个 benchmark/subdimension 下跨模型取 `score_10` 平均。分数越高，说明当前模型整体越接近解决；分数越低，越有继续区分模型的价值。`NA` 表示该 mapping 目前没有进入最终计分的模型结果。
2. **原子能力有效相关性**：只由 mapping 决定，不看模型表现。公式（R20，无 tier 因子）：`100 × benchmark_weight × Σ(P_priority × ability_weight)`。

辅助列：`P 相关性` 是不乘 benchmark 置信权重的纯 P 能力相关性。

## 先看结论排序

| 建议 | Benchmark | Subdimension | 所有模型平均分 | 原子能力有效相关性 | P 相关性 | 模型数 | P 映射 |
|---|---|---|---:|---:|---:|---:|---|
| 优先继续做 | `sas_bench` SAS-Bench | ECS error-cause consistency | 5.28 | 100.00 | 100.00 | 10 | P05 0.20, P06 0.20, P10 0.80 |
| 值得继续做 | `eduguard_adversarial` EduGuard-Bench P2 | Refusal quality distribution | 6.71 | 85.00 | 100.00 | 7 | P17 0.20, P19 0.80 |
| 值得继续做 | `eduguard_adversarial` EduGuard-Bench P2 | Adversarial Safety ASR | 6.92 | 85.00 | 100.00 | 7 | P17 0.50, P19 0.50 |
| 优先继续做 | `longtutor_diagnosis` LongTutor 知识状态诊断 | four-category knowledge-state diagnosis macro-F1 | 2.74 | 82.45 | 97.00 | 7 | P10 0.20, P13 0.80 |
| 优先继续做 | `p08_calibration` P08 置信度校准 | calibration composite (CWR/AUROC) | 6.45 | 77.35 | 91.00 | 7 | P07 0.20, P08 0.80 |
| 优先继续做 | `asap_2` ASAP 2.0 | essay holistic QWK | 5.45 | 72.00 | 72.00 | 7 | P11 0.80 |
| 优先继续做 | `mooccube_prereq` MOOCCube 先修关系推理 | chance-corrected composite (先修选择 + 学习顺序排序) | 3.87 | 69.70 | 82.00 | 7 | P15 0.80 |
| 优先继续做 | `tutorbench` TutorBench | Fair815 multimodal tutor quality | 5.48 | 68.42 | 80.50 | 6 | P03 0.20, P14 0.20, P16 0.50 |
| 值得继续做 | `mmtutorbench` MMTutorBench | multimodal tutor score | 6.58 | 68.42 | 80.50 | 4 | P03 0.20, P14 0.20, P16 0.50 |
| 优先继续做 | `p07_selfcheck` P07 两轮自查 | two-round self-check (fix/break rate) | 5.20 | 67.15 | 79.00 | 7 | P07 0.80, P08 0.20 |
| 优先继续做 | `mathtutorbench_socratic` MathTutorBench | Socratic Questioning | 2.80 | 66.50 | 66.50 | 7 | P14 0.50, P16 0.20 |
| 优先继续做 | `mathtutorbench_scaffolding_hard` MathTutorBench | Scaffolding hard | 2.80 | 65.88 | 77.50 | 9 | P05 0.20, P14 0.50, P16 0.20 |
| 优先继续做 | `mathtutorbench_scaffolding` MathTutorBench | Scaffolding | 3.05 | 65.88 | 77.50 | 9 | P05 0.20, P14 0.50, P16 0.20 |
| 值得继续做 | `eduguard_sata` EduGuard-Bench P1 | Teaching Harm / SATA RFS | 7.49 | 63.00 | 63.00 | 10 | P17 0.20, P18 0.20, P19 0.20 |
| 优先继续做 | `edubench` EduBench | personalized_adaptation_learning_support (metric) | 6.40 | 60.78 | 71.50 | 14 | P13 0.20, P14 0.50 |
| 重要但可降频 | `pedagogy_benchmark` Pedagogy Benchmark | CDPK teaching knowledge selection | 8.45 | 103.50 | 103.50 | 13 | P05 0.50, P14 0.80 |
| 重要但可降频 | `pedagogy_benchmark` Pedagogy Benchmark | SEND special education needs selection | 7.83 | 99.00 | 99.00 | 13 | P05 0.50, P13 0.20, P14 0.50 |
| 重要但可降频 | `mathtutorbench_mistake_location` MathTutorBench | Mistake Location | 7.71 | 95.00 | 95.00 | 8 | P02 0.20, P10 0.80 |
| 重要但可降频 | `sas_bench` SAS-Bench | CCS step scoring consistency | 7.63 | 83.00 | 83.00 | 10 | P02 0.20, P10 0.20, P11 0.50 |
| 重要但可降频 | `mathvista` MathVista | task/question_type/answer_type accuracy | 8.56 | 78.50 | 78.50 | 4 | P03 0.50, P05 0.20, P06 0.50 |
| 重要但可降频 | `sas_bench` SAS-Bench | QWK holistic total score | 8.28 | 72.00 | 72.00 | 10 | P11 0.80 |
| 重要但可降频 | `mathtutorbench_pedagogy_hard` MathTutorBench | Pedagogy IF hard | 7.76 | 65.88 | 77.50 | 9 | P05 0.20, P14 0.50, P16 0.20 |
| 重要但可降频 | `mathtutorbench_pedagogy` MathTutorBench | Pedagogy IF | 8.17 | 65.88 | 77.50 | 9 | P05 0.20, P14 0.50, P16 0.20 |
| 重要但可降频 | `p08_abstention` P08 能力性弃答 | balanced abstention score | 8.99 | 64.60 | 76.00 | 7 | P08 0.80 |
| 重要但可降频 | `mathtutorbench_solution_correctness` MathTutorBench | Solution Correctness | 8.73 | 62.50 | 62.50 | 8 | P07 0.20, P10 0.50 |
| 不必重点看 | `mathtutorbench_mistake_correction` MathTutorBench | Mistake Correction | 9.08 | 51.00 | 51.00 | 8 | P06 0.20, P10 0.20, P16 0.20 |
| 诊断保留 | `eduillustrate` EduIllustrate | 8-dim 0-5 visual explanation score | 5.30 | 49.00 | 70.00 | 5 | P04 0.50, P16 0.20 |
| 诊断保留 | `bea2025_judge` BEA 2025 Judge | judge labels: mistake/guidance/actionability | 5.06 | 45.00 | 45.00 | 9 | P11 0.50 |
| 诊断保留 | `mrbench_judge` MRBench Judge | 8-dimension tutor response judging | 5.24 | 45.00 | 45.00 | 9 | P11 0.50 |
| 不必重点看 | `ifeval` IFEval | prompt-level strict accuracy | 9.12 | 45.00 | 45.00 | 7 | P01 1.00 |
| 不必重点看 | `olympiadbench` OlympiadBench | overall/subject/language/modality accuracy | 7.25 | 43.50 | 43.50 | 6 | P05 0.20, P06 0.50 |
| 不必重点看 | `agieval` AGIEval | overall/task/language/question_type accuracy | 8.76 | 43.50 | 43.50 | 8 | P05 0.20, P06 0.50 |
| 不必重点看 | `mathtutorbench_problem_solving` MathTutorBench | Problem Solving | 9.69 | 43.50 | 43.50 | 7 | P05 0.20, P06 0.50 |
| 不必重点看 | `longtutor_evidence` LongTutor 证据抽取 | Multi-session Reasoning accuracy | 6.65 | 40.60 | 58.00 | 7 | P02 0.80 |
| 不必重点看 | `longtutor_evidence` LongTutor 证据抽取 | Hallucination Check accuracy | 7.31 | 40.60 | 58.00 | 7 | P02 0.80 |
| 不必重点看 | `longtutor_evidence` LongTutor 证据抽取 | Information Extraction accuracy | 9.59 | 40.60 | 58.00 | 7 | P02 0.80 |
| 不必重点看 | `mmlu_pro` MMLU-Pro | overall/category accuracy | 8.52 | 40.50 | 40.50 | 8 | P05 0.50, P06 0.20 |
| 不必重点看 | `ceval` C-EVAL | overall/category/subject accuracy | 8.97 | 40.50 | 40.50 | 9 | P05 0.50, P06 0.20 |
| 诊断保留 | `edubench` EduBench | motivation_guidance_positive_feedback (metric) | 6.45 | 40.38 | 47.50 | 14 | P16 0.50 |
| 不必重点看 | `edubench` EduBench | TMG/PCC × clarity_concision_inspiration + scenario_element_integration (task×metric) | 8.12 | 40.38 | 47.50 | 14 | P16 0.50 |
| 不必重点看 | `edubench` EduBench | QG × clarity_concision_inspiration + scenario_element_integration (task×metric) | 8.11 | 38.25 | 45.00 | 14 | P12 0.50 |
| 诊断保留 | `k12vista` K12Vista | science/geo subject-chart subset score | 6.33 | 29.75 | 35.00 | 4 | P03 0.50 |
| 不必重点看 | `k12vista` K12Vista | math problem-figure subset score | 7.49 | 29.75 | 35.00 | 4 | P03 0.50 |
| 不必重点看 | `edubench` EduBench | reasoning_process_rigor (metric) | 8.18 | 27.62 | 32.50 | 14 | P06 0.50 |
| 不必重点看 | `edubench` EduBench | higher_order_thinking_ability_development (metric) | 7.41 | 27.20 | 32.00 | 14 | P06 0.20, P16 0.20 |
| 不必重点看 | `k12vista` K12Vista | official partial-credit score (per-blank 0/1 mean) | 6.64 | 20.40 | 24.00 | 4 | P05 0.20, P06 0.20 |
| 不必重点看 | `edubench` EduBench | scenario_element_integration (metric) | 7.66 | 16.15 | 19.00 | 14 | P14 0.20 |
| 不必重点看 | `edubench` EduBench | clarity_concision_inspiration (metric) | 8.29 | 16.15 | 19.00 | 14 | P16 0.20 |
| 不必重点看 | `bea2025_tutor` BEA 2025 Tutor | dimension: Mistake_Identification | 8.45 | 16.15 | 19.00 | 6 | P10 0.20 |
| 不必重点看 | `mrbench_tutor` MRBench Tutor | dimension: Tutor_Tone (encouraging share) | 9.02 | 16.15 | 19.00 | 6 | P16 0.20 |
| 不必重点看 | `mrbench_tutor` MRBench Tutor | dimension: Providing_Guidance | 9.04 | 16.15 | 19.00 | 6 | P14 0.20 |
| 不必重点看 | `mrbench_tutor` MRBench Tutor | dimension: Mistake_Identification | 9.20 | 16.15 | 19.00 | 6 | P10 0.20 |
| 不必重点看 | `mrbench_tutor` MRBench Tutor | dimension: Actionability | 9.22 | 16.15 | 19.00 | 6 | P16 0.20 |
| 不必重点看 | `bea2025_tutor` BEA 2025 Tutor | dimension: Actionability | 9.29 | 16.15 | 19.00 | 6 | P16 0.20 |
| 不必重点看 | `bea2025_tutor` BEA 2025 Tutor | dimension: Providing_Guidance | 9.56 | 16.15 | 19.00 | 6 | P14 0.20 |
| 不必重点看 | `edubench` EduBench | QG × domain_knowledge_accuracy + basic_factual_accuracy (task×metric) | 9.19 | 15.30 | 18.00 | 14 | P12 0.20 |
| 不必重点看 | `mrbench_tutor` MRBench Tutor | dimension: Tutor_Tone (non-offensive) | 10.00 | 15.30 | 18.00 | 6 | P17 0.20 |
| 不必重点看 | `olympiadbench` OlympiadBench | multimodal-subset accuracy | 7.06 | 14.00 | 14.00 | 4 | P03 0.20 |
| 诊断保留 | `longtutor_teaching` LongTutor 教学动作 | judge dims: strategy_alignment + history_utilization (1-5) | 6.32 | 13.30 | 19.00 | 7 | P14 0.20 |
| 不必重点看 | `edubench` EduBench | domain_knowledge_accuracy (metric) | 8.63 | 9.35 | 11.00 | 14 | P05 0.20 |
| 不必重点看 | `edubench` EduBench | basic_factual_accuracy (metric) | 9.07 | 9.35 | 11.00 | 14 | P05 0.20 |
| 不必重点看 | `edubench` EduBench | error_identification_correction_accuracy (metric) | 7.31 | 5.70 | 19.00 | 14 | P10 0.20 |

## 按 benchmark 聚合

聚合口径：同一 benchmark 的多个 subdimension 先各自计算平均分和相关性，再在 benchmark 内做简单平均；只用于概览，具体判断仍看上面的 subdimension 明细。

| 建议 | Benchmark | Subdimension 数 | benchmark 平均分 | 平均原子相关性 | P 覆盖 |
|---|---|---:|---:|---:|---|
| 值得继续做 | `eduguard_adversarial` EduGuard-Bench P2 | 2 | 6.81 | 85.00 | P17, P19 |
| 优先继续做 | `longtutor_diagnosis` LongTutor 知识状态诊断 | 1 | 2.74 | 82.45 | P10, P13 |
| 优先继续做 | `p08_calibration` P08 置信度校准 | 1 | 6.45 | 77.35 | P07, P08 |
| 优先继续做 | `asap_2` ASAP 2.0 | 1 | 5.45 | 72.00 | P11 |
| 优先继续做 | `mooccube_prereq` MOOCCube 先修关系推理 | 1 | 3.87 | 69.70 | P15 |
| 优先继续做 | `tutorbench` TutorBench | 1 | 5.48 | 68.42 | P03, P14, P16 |
| 值得继续做 | `mmtutorbench` MMTutorBench | 1 | 6.58 | 68.42 | P03, P14, P16 |
| 优先继续做 | `p07_selfcheck` P07 两轮自查 | 1 | 5.20 | 67.15 | P07, P08 |
| 优先继续做 | `mathtutorbench_socratic` MathTutorBench | 1 | 2.80 | 66.50 | P14, P16 |
| 优先继续做 | `mathtutorbench_scaffolding_hard` MathTutorBench | 1 | 2.80 | 65.88 | P05, P14, P16 |
| 优先继续做 | `mathtutorbench_scaffolding` MathTutorBench | 1 | 3.05 | 65.88 | P05, P14, P16 |
| 值得继续做 | `eduguard_sata` EduGuard-Bench P1 | 1 | 7.49 | 63.00 | P17, P18, P19 |
| 重要但可降频 | `pedagogy_benchmark` Pedagogy Benchmark | 2 | 8.14 | 101.25 | P05, P13, P14 |
| 重要但可降频 | `mathtutorbench_mistake_location` MathTutorBench | 1 | 7.71 | 95.00 | P02, P10 |
| 重要但可降频 | `sas_bench` SAS-Bench | 3 | 7.06 | 85.00 | P02, P05, P06, P10, P11 |
| 重要但可降频 | `mathvista` MathVista | 1 | 8.56 | 78.50 | P03, P05, P06 |
| 重要但可降频 | `mathtutorbench_pedagogy_hard` MathTutorBench | 1 | 7.76 | 65.88 | P05, P14, P16 |
| 重要但可降频 | `mathtutorbench_pedagogy` MathTutorBench | 1 | 8.17 | 65.88 | P05, P14, P16 |
| 重要但可降频 | `p08_abstention` P08 能力性弃答 | 1 | 8.99 | 64.60 | P08 |
| 重要但可降频 | `mathtutorbench_solution_correctness` MathTutorBench | 1 | 8.73 | 62.50 | P07, P10 |
| 不必重点看 | `mathtutorbench_mistake_correction` MathTutorBench | 1 | 9.08 | 51.00 | P06, P10, P16 |
| 诊断保留 | `eduillustrate` EduIllustrate | 1 | 5.30 | 49.00 | P04, P16 |
| 诊断保留 | `bea2025_judge` BEA 2025 Judge | 1 | 5.06 | 45.00 | P11 |
| 诊断保留 | `mrbench_judge` MRBench Judge | 1 | 5.24 | 45.00 | P11 |
| 不必重点看 | `ifeval` IFEval | 1 | 9.12 | 45.00 | P01 |
| 不必重点看 | `agieval` AGIEval | 1 | 8.76 | 43.50 | P05, P06 |
| 不必重点看 | `mathtutorbench_problem_solving` MathTutorBench | 1 | 9.69 | 43.50 | P05, P06 |
| 不必重点看 | `longtutor_evidence` LongTutor 证据抽取 | 3 | 7.85 | 40.60 | P02 |
| 不必重点看 | `mmlu_pro` MMLU-Pro | 1 | 8.52 | 40.50 | P05, P06 |
| 不必重点看 | `ceval` C-EVAL | 1 | 8.97 | 40.50 | P05, P06 |
| 不必重点看 | `olympiadbench` OlympiadBench | 2 | 7.16 | 28.75 | P03, P05, P06 |
| 不必重点看 | `k12vista` K12Vista | 3 | 6.82 | 26.63 | P03, P05, P06 |
| 不必重点看 | `edubench` EduBench | 12 | 7.90 | 25.55 | P05, P06, P10, P12, P13, P14, P16 |
| 不必重点看 | `bea2025_tutor` BEA 2025 Tutor | 3 | 9.10 | 16.15 | P10, P14, P16 |
| 不必重点看 | `mrbench_tutor` MRBench Tutor | 5 | 9.30 | 15.98 | P10, P14, P16, P17 |
| 诊断保留 | `longtutor_teaching` LongTutor 教学动作 | 1 | 6.32 | 13.30 | P14 |

## 校准提示

- `所有模型平均分` 高但 `原子能力有效相关性` 低：通常不需要重点看，适合做门槛或背景参考。
- `所有模型平均分` 低且 `原子能力有效相关性` 高：优先继续做，因为它既重要又还没被解决好。
- `NA` 且相关性高：说明 mapping 认为它重要，但当前主计分层缺结果，应该优先补跑或确认数据源。
- foundation gate 不等于没用，只是不应主导教育能力判断；它更适合筛掉基础能力不足的模型。
