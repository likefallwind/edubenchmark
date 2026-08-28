# Atomic P Scores

P-score rows: 226
Covered P codes: P01, P02, P03, P04, P05, P06, P07, P08, P10, P11, P12, P13, P14, P15, P16, P17, P18, P19
Missing P codes: P09, P20
P rows reported as 未测过 (score_10 = null): 0
Capability-gap zero cells (score_10 = 0, counted): 36
Untested cells (not counted; see `09_atomic_p_untested_cells.jsonl`): 47

`score_10`: facet-weighted average with effective weight = relevance × confidence (R25 rule-derived weights). Coverage completeness is reported separately and is not folded back into the score.

## Missing-cell policy (R26, 2026-08-04)

The R22 rule -- fill a panel model's missing cell with the lowest score any tested
model got there -- is **removed**. A missing cell is now classified:

- `untested`: never run. No score, no denominator, reported as 未测过. A P whose
  cells are all untested gets `score_10: null`, **not** 0.
- `capability_gap`: the model lacks a capability the cell requires for *every* item
  (vision only so far; see `MODEL_CAPABILITIES` / `CELL_CAPABILITY_REQUIREMENTS`).
  That is a real capability gap rather than a scheduling gap, so it scores **0** and counts.

Cells where only *some* items need the capability (tutorbench, olympiadbench overall)
stay `untested`: a text-only model earns a genuine non-zero score there, so 0 would be
a measurement artifact rather than a capability difference.

## Sample Scores

| Model key | P | Group | Score | Evidence | 0-score cells | Untested cells | Weight sum | Benchmarks |
|---|---|---|---:|---:|---:|---:|---:|---|
| `claude-sonnet-4.6` | `P05` 知识调用与掌握 | FDR | 8.7383 | 4 | 0 | 0 | 1.34 | edubench, pedagogy_benchmark |
| `claude-sonnet-4.6` | `P06` 推理与生成 | FDR | 8.4704 | 2 | 0 | 0 | 0.595 | edubench |
| `claude-sonnet-4.6` | `P10` 错误诊断 | LAD | 6.074 | 1 | 0 | 0 | 0.06 | edubench |
| `claude-sonnet-4.6` | `P11` 主观题评价能力 | LAD | 6.106 | 1 | 0 | 0 | 0.8 | asap_2 |
| `claude-sonnet-4.6` | `P12` 命题与作业设计 | LAD | 8.4801 | 2 | 0 | 0 | 0.595 | edubench |
| `claude-sonnet-4.6` | `P13` 学习者画像建模 | CLM | 7.146 | 2 | 0 | 0 | 0.37 | edubench, pedagogy_benchmark |
| `claude-sonnet-4.6` | `P14` 个性化教学策略选择 | CLM | 7.4924 | 4 | 0 | 0 | 1.895 | edubench, pedagogy_benchmark |
| `claude-sonnet-4.6` | `P16` 适配性解释与反馈生成 | CLM | 7.7383 | 4 | 0 | 0 | 1.19 | edubench |
| `deepseek-r1-0528-qwen3-8b` | `P05` 知识调用与掌握 | FDR | 6.8221 | 2 | 0 | 0 | 1.0 | pedagogy_benchmark |
| `deepseek-r1-0528-qwen3-8b` | `P13` 学习者画像建模 | CLM | 6.6364 | 1 | 0 | 0 | 0.2 | pedagogy_benchmark |
| `deepseek-r1-0528-qwen3-8b` | `P14` 个性化教学策略选择 | CLM | 6.8649 | 2 | 0 | 0 | 1.3 | pedagogy_benchmark |
| `deepseek-v3-2` | `P11` 主观题评价能力 | LAD | 3.898 | 2 | 0 | 0 | 1.0 | bea2025_judge, mrbench_judge |
| `deepseek-v4-flash` | `P02` 长上下文与证据定位 | SRG | 7.74 | 1 | 0 | 0 | 0.2 | mathtutorbench_mistake_location |
| `deepseek-v4-flash` | `P05` 知识调用与掌握 | FDR | 7.9504 | 12 | 0 | 0 | 3.42 | agieval, ceval, edubench, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_problem_solving, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard, mmlu_pro, pedagogy_benchmark |
| `deepseek-v4-flash` | `P06` 推理与生成 | FDR | 8.8085 | 7 | 0 | 0 | 2.195 | agieval, ceval, edubench, mathtutorbench_mistake_correction, mathtutorbench_problem_solving, mmlu_pro |
| `deepseek-v4-flash` | `P07` 自我校验与修正 | FDR | 8.567 | 1 | 0 | 0 | 0.2 | mathtutorbench_solution_correctness |
| `deepseek-v4-flash` | `P10` 错误诊断 | LAD | 8.2718 | 4 | 0 | 0 | 1.56 | edubench, mathtutorbench_mistake_correction, mathtutorbench_mistake_location, mathtutorbench_solution_correctness |
| `deepseek-v4-flash` | `P11` 主观题评价能力 | LAD | 5.1073 | 3 | 0 | 0 | 1.8 | asap_2, bea2025_judge, mrbench_judge |
| `deepseek-v4-flash` | `P12` 命题与作业设计 | LAD | 8.5799 | 2 | 0 | 0 | 0.595 | edubench |
| `deepseek-v4-flash` | `P13` 学习者画像建模 | CLM | 7.1144 | 2 | 0 | 0 | 0.37 | edubench, pedagogy_benchmark |
| `deepseek-v4-flash` | `P14` 个性化教学策略选择 | CLM | 6.7449 | 8 | 0 | 0 | 3.595 | edubench, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard, pedagogy_benchmark |
| `deepseek-v4-flash` | `P16` 适配性解释与反馈生成 | CLM | 7.1803 | 9 | 0 | 0 | 2.07 | edubench, mathtutorbench_mistake_correction, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard |
| `deepseek-v4-pro` | `P01` 指令与约束遵循 | SRG | 9.2222 | 1 | 0 | 0 | 1.0 | ifeval |
| `deepseek-v4-pro` | `P02` 长上下文与证据定位 | SRG | 7.8656 | 5 | 0 | 0 | 2.08 | longtutor_evidence, mathtutorbench_mistake_location, sas_bench |
| `deepseek-v4-pro` | `P03` 多模态理解 | SRG | 0.0 | 4 | 4 | 2 | 1.52 | k12vista, mathvista, mmtutorbench |
| `deepseek-v4-pro` | `P04` 多模态生成 | SRG | 0.0 | 1 | 1 | 0 | 0.35 | eduillustrate |
| `deepseek-v4-pro` | `P05` 知识调用与掌握 | FDR | 7.3713 | 15 | 2 | 1 | 3.99 | agieval, ceval, edubench, k12vista, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard, mathvista, mmlu_pro, olympiadbench, pedagogy_benchmark, sas_bench |
| `deepseek-v4-pro` | `P06` 推理与生成 | FDR | 6.6945 | 10 | 2 | 1 | 3.065 | agieval, ceval, edubench, k12vista, mathtutorbench_mistake_correction, mathvista, mmlu_pro, olympiadbench, sas_bench |
| `deepseek-v4-pro` | `P07` 自我校验与修正 | FDR | 6.342 | 3 | 0 | 0 | 1.05 | mathtutorbench_solution_correctness, p07_selfcheck, p08_calibration |
| `deepseek-v4-pro` | `P08` 置信度校准与弃答 | FDR | 7.7836 | 3 | 0 | 0 | 1.53 | p07_selfcheck, p08_abstention, p08_calibration |
| `deepseek-v4-pro` | `P10` 错误诊断 | LAD | 7.552 | 7 | 0 | 2 | 2.73 | edubench, longtutor_diagnosis, mathtutorbench_mistake_correction, mathtutorbench_mistake_location, mathtutorbench_solution_correctness, sas_bench |
| `deepseek-v4-pro` | `P11` 主观题评价能力 | LAD | 6.4007 | 5 | 0 | 0 | 3.1 | asap_2, bea2025_judge, mrbench_judge, sas_bench |
| `deepseek-v4-pro` | `P12` 命题与作业设计 | LAD | 8.4498 | 2 | 0 | 0 | 0.595 | edubench |
| `deepseek-v4-pro` | `P13` 学习者画像建模 | CLM | 5.245 | 3 | 0 | 0 | 1.05 | edubench, longtutor_diagnosis, pedagogy_benchmark |
| `deepseek-v4-pro` | `P14` 个性化教学策略选择 | CLM | 7.0386 | 11 | 1 | 3 | 4.405 | edubench, longtutor_teaching, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard, mathtutorbench_socratic, mmtutorbench, pedagogy_benchmark |
| `deepseek-v4-pro` | `P15` 学习路径规划（知识结构层） | CLM | 3.789 | 1 | 0 | 0 | 0.68 | mooccube_prereq |
| `deepseek-v4-pro` | `P16` 适配性解释与反馈生成 | CLM | 5.8231 | 12 | 2 | 4 | 2.835 | edubench, eduillustrate, mathtutorbench_mistake_correction, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard, mathtutorbench_socratic, mmtutorbench |
| `deepseek-v4-pro` | `P17` 教育角色边界判断 | CEG | 5.8532 | 3 | 0 | 1 | 0.795 | eduguard_adversarial, eduguard_sata |
| `deepseek-v4-pro` | `P18` 学生风险识别 | CEG | 7.612 | 1 | 0 | 0 | 0.2 | eduguard_sata |
| `deepseek-v4-pro` | `P19` 安全处置选择 | CEG | 6.0467 | 3 | 0 | 0 | 1.305 | eduguard_adversarial, eduguard_sata |
| `doubao-seed-2-0-lite` | `P04` 多模态生成 | SRG | 5.3038 | 1 | 0 | 0 | 0.35 | eduillustrate |
| `doubao-seed-2-0-lite` | `P05` 知识调用与掌握 | FDR | 7.202 | 6 | 0 | 0 | 1.02 | edubench, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard |
| `doubao-seed-2-0-lite` | `P06` 推理与生成 | FDR | 8.3156 | 2 | 0 | 0 | 0.595 | edubench |
| `doubao-seed-2-0-lite` | `P10` 错误诊断 | LAD | 6.3803 | 1 | 0 | 0 | 0.06 | edubench |
| `doubao-seed-2-0-lite` | `P12` 命题与作业设计 | LAD | 8.4848 | 2 | 0 | 0 | 0.595 | edubench |
| `doubao-seed-2-0-lite` | `P13` 学习者画像建模 | CLM | 6.3047 | 1 | 0 | 0 | 0.17 | edubench |
| `doubao-seed-2-0-lite` | `P14` 个性化教学策略选择 | CLM | 5.664 | 6 | 0 | 0 | 2.295 | edubench, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard |
| `doubao-seed-2-0-lite` | `P16` 适配性解释与反馈生成 | CLM | 6.7266 | 9 | 0 | 0 | 2.01 | edubench, eduillustrate, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard |
| `doubao-seed-2-0-lite` | `P17` 教育角色边界判断 | CEG | 6.3566 | 3 | 0 | 0 | 0.795 | eduguard_adversarial, eduguard_sata |
| `doubao-seed-2-0-lite` | `P18` 学生风险识别 | CEG | 7.3 | 1 | 0 | 0 | 0.2 | eduguard_sata |
| `doubao-seed-2-0-lite` | `P19` 安全处置选择 | CEG | 6.6595 | 3 | 0 | 0 | 1.305 | eduguard_adversarial, eduguard_sata |
| `doubao-seed-2-0-pro` | `P01` 指令与约束遵循 | SRG | 8.9464 | 1 | 0 | 0 | 1.0 | ifeval |
| `doubao-seed-2-0-pro` | `P02` 长上下文与证据定位 | SRG | 7.9358 | 5 | 0 | 0 | 2.08 | longtutor_evidence, mathtutorbench_mistake_location, sas_bench |
| `doubao-seed-2-0-pro` | `P03` 多模态理解 | SRG | 7.6821 | 5 | 0 | 1 | 1.72 | k12vista, mathvista, mmtutorbench, olympiadbench |
| `doubao-seed-2-0-pro` | `P04` 多模态生成 | SRG | 6.6376 | 1 | 0 | 0 | 0.35 | eduillustrate |
| `doubao-seed-2-0-pro` | `P05` 知识调用与掌握 | FDR | 8.1093 | 16 | 0 | 0 | 4.19 | agieval, ceval, edubench, k12vista, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_problem_solving, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard, mathvista, mmlu_pro, olympiadbench, pedagogy_benchmark, sas_bench |
| `doubao-seed-2-0-pro` | `P06` 推理与生成 | FDR | 8.5831 | 11 | 0 | 0 | 3.565 | agieval, ceval, edubench, k12vista, mathtutorbench_mistake_correction, mathtutorbench_problem_solving, mathvista, mmlu_pro, olympiadbench, sas_bench |
| `doubao-seed-2-0-pro` | `P07` 自我校验与修正 | FDR | 6.026 | 3 | 0 | 0 | 1.05 | mathtutorbench_solution_correctness, p07_selfcheck, p08_calibration |
| `doubao-seed-2-0-pro` | `P08` 置信度校准与弃答 | FDR | 7.6935 | 3 | 0 | 0 | 1.53 | p07_selfcheck, p08_abstention, p08_calibration |
| `doubao-seed-2-0-pro` | `P10` 错误诊断 | LAD | 7.7212 | 9 | 0 | 0 | 3.07 | bea2025_tutor, edubench, longtutor_diagnosis, mathtutorbench_mistake_correction, mathtutorbench_mistake_location, mathtutorbench_solution_correctness, mrbench_tutor, sas_bench |
| `doubao-seed-2-0-pro` | `P11` 主观题评价能力 | LAD | 7.179 | 4 | 0 | 1 | 2.3 | bea2025_judge, mrbench_judge, sas_bench |
| `doubao-seed-2-0-pro` | `P12` 命题与作业设计 | LAD | 8.2344 | 2 | 0 | 0 | 0.595 | edubench |
| `doubao-seed-2-0-pro` | `P13` 学习者画像建模 | CLM | 4.8701 | 3 | 0 | 0 | 1.05 | edubench, longtutor_diagnosis, pedagogy_benchmark |
| `doubao-seed-2-0-pro` | `P14` 个性化教学策略选择 | CLM | 7.3963 | 13 | 0 | 1 | 4.745 | bea2025_tutor, edubench, longtutor_teaching, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard, mathtutorbench_socratic, mmtutorbench, mrbench_tutor, pedagogy_benchmark |
| `doubao-seed-2-0-pro` | `P15` 学习路径规划（知识结构层） | CLM | 4.486 | 1 | 0 | 0 | 0.68 | mooccube_prereq |
| `doubao-seed-2-0-pro` | `P16` 适配性解释与反馈生成 | CLM | 7.6659 | 15 | 0 | 1 | 3.345 | bea2025_tutor, edubench, eduillustrate, mathtutorbench_mistake_correction, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard, mathtutorbench_socratic, mmtutorbench, mrbench_tutor |
| `doubao-seed-2-0-pro` | `P17` 教育角色边界判断 | CEG | 6.7266 | 4 | 0 | 0 | 0.965 | eduguard_adversarial, eduguard_sata, mrbench_tutor |
| `doubao-seed-2-0-pro` | `P18` 学生风险识别 | CEG | 7.618 | 1 | 0 | 0 | 0.2 | eduguard_sata |
| `doubao-seed-2-0-pro` | `P19` 安全处置选择 | CEG | 6.5183 | 3 | 0 | 0 | 1.305 | eduguard_adversarial, eduguard_sata |
| `glm-5.1` | `P02` 长上下文与证据定位 | SRG | 7.8142 | 1 | 0 | 0 | 0.2 | sas_bench |
| `glm-5.1` | `P05` 知识调用与掌握 | FDR | 8.0983 | 5 | 0 | 0 | 1.54 | edubench, pedagogy_benchmark, sas_bench |
| `glm-5.1` | `P06` 推理与生成 | FDR | 7.2276 | 3 | 0 | 0 | 0.795 | edubench, sas_bench |
| `glm-5.1` | `P10` 错误诊断 | LAD | 7.1202 | 3 | 0 | 0 | 1.06 | edubench, sas_bench |
| `glm-5.1` | `P11` 主观题评价能力 | LAD | 7.4274 | 3 | 0 | 0 | 2.1 | asap_2, sas_bench |
| `glm-5.1` | `P12` 命题与作业设计 | LAD | 8.3655 | 2 | 0 | 0 | 0.595 | edubench |
| `glm-5.1` | `P13` 学习者画像建模 | CLM | 7.3481 | 2 | 0 | 0 | 0.37 | edubench, pedagogy_benchmark |
| `glm-5.1` | `P14` 个性化教学策略选择 | CLM | 7.6159 | 4 | 0 | 0 | 1.895 | edubench, pedagogy_benchmark |
| `glm-5.1` | `P16` 适配性解释与反馈生成 | CLM | 7.0109 | 4 | 0 | 0 | 1.19 | edubench |
| `glm-5.1` | `P17` 教育角色边界判断 | CEG | 8.327 | 3 | 0 | 0 | 0.795 | eduguard_adversarial, eduguard_sata |
| `glm-5.1` | `P18` 学生风险识别 | CEG | 7.632 | 1 | 0 | 0 | 0.2 | eduguard_sata |
| `glm-5.1` | `P19` 安全处置选择 | CEG | 8.0466 | 3 | 0 | 0 | 1.305 | eduguard_adversarial, eduguard_sata |
| `glm-5.2` | `P01` 指令与约束遵循 | SRG | 9.2976 | 1 | 0 | 0 | 1.0 | ifeval |
| `glm-5.2` | `P02` 长上下文与证据定位 | SRG | 8.0299 | 5 | 0 | 0 | 2.08 | longtutor_evidence, mathtutorbench_mistake_location, sas_bench |
| `glm-5.2` | `P03` 多模态理解 | SRG | 0.0 | 4 | 4 | 2 | 1.52 | k12vista, mathvista, mmtutorbench |
| `glm-5.2` | `P04` 多模态生成 | SRG | 0.0 | 1 | 1 | 0 | 0.35 | eduillustrate |
| `glm-5.2` | `P05` 知识调用与掌握 | FDR | 7.1776 | 14 | 2 | 2 | 3.19 | agieval, ceval, edubench, k12vista, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_problem_solving, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard, mathvista, mmlu_pro, olympiadbench, sas_bench |
| `glm-5.2` | `P06` 推理与生成 | FDR | 7.0995 | 11 | 2 | 0 | 3.565 | agieval, ceval, edubench, k12vista, mathtutorbench_mistake_correction, mathtutorbench_problem_solving, mathvista, mmlu_pro, olympiadbench, sas_bench |
| `glm-5.2` | `P07` 自我校验与修正 | FDR | 6.3047 | 3 | 0 | 0 | 1.05 | mathtutorbench_solution_correctness, p07_selfcheck, p08_calibration |
| `glm-5.2` | `P08` 置信度校准与弃答 | FDR | 7.7336 | 3 | 0 | 0 | 1.53 | p07_selfcheck, p08_abstention, p08_calibration |
| `glm-5.2` | `P10` 错误诊断 | LAD | 7.4658 | 9 | 0 | 0 | 3.07 | bea2025_tutor, edubench, longtutor_diagnosis, mathtutorbench_mistake_correction, mathtutorbench_mistake_location, mathtutorbench_solution_correctness, mrbench_tutor, sas_bench |
| `glm-5.2` | `P11` 主观题评价能力 | LAD | 7.3949 | 4 | 0 | 1 | 2.3 | bea2025_judge, mrbench_judge, sas_bench |
| `glm-5.2` | `P12` 命题与作业设计 | LAD | 8.6966 | 2 | 0 | 0 | 0.595 | edubench |
| `glm-5.2` | `P13` 学习者画像建模 | CLM | 4.5977 | 2 | 0 | 1 | 0.85 | edubench, longtutor_diagnosis |
| `glm-5.2` | `P14` 个性化教学策略选择 | CLM | 6.3631 | 11 | 1 | 3 | 3.445 | bea2025_tutor, edubench, longtutor_teaching, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard, mathtutorbench_socratic, mmtutorbench, mrbench_tutor |
| `glm-5.2` | `P15` 学习路径规划（知识结构层） | CLM | 3.911 | 1 | 0 | 0 | 0.68 | mooccube_prereq |
| `glm-5.2` | `P16` 适配性解释与反馈生成 | CLM | 6.791 | 15 | 2 | 1 | 3.345 | bea2025_tutor, edubench, eduillustrate, mathtutorbench_mistake_correction, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard, mathtutorbench_socratic, mmtutorbench, mrbench_tutor |
| `glm-5.2` | `P17` 教育角色边界判断 | CEG | 7.4097 | 4 | 0 | 0 | 0.965 | eduguard_adversarial, eduguard_sata, mrbench_tutor |
| `glm-5.2` | `P18` 学生风险识别 | CEG | 7.595 | 1 | 0 | 0 | 0.2 | eduguard_sata |
| `glm-5.2` | `P19` 安全处置选择 | CEG | 6.5963 | 3 | 0 | 0 | 1.305 | eduguard_adversarial, eduguard_sata |
| `gpt-5.4` | `P02` 长上下文与证据定位 | SRG | 8.0261 | 1 | 0 | 0 | 0.2 | sas_bench |
| `gpt-5.4` | `P05` 知识调用与掌握 | FDR | 6.9089 | 3 | 0 | 0 | 1.2 | pedagogy_benchmark, sas_bench |
| `gpt-5.4` | `P06` 推理与生成 | FDR | 5.5636 | 1 | 0 | 0 | 0.2 | sas_bench |
| `gpt-5.4` | `P10` 错误诊断 | LAD | 6.7949 | 2 | 0 | 0 | 1.0 | sas_bench |
| `gpt-5.4` | `P11` 主观题评价能力 | LAD | 7.3637 | 3 | 0 | 0 | 2.1 | asap_2, sas_bench |
| `gpt-5.4` | `P13` 学习者画像建模 | CLM | 7.9545 | 1 | 0 | 0 | 0.2 | pedagogy_benchmark |
| `gpt-5.4` | `P14` 个性化教学策略选择 | CLM | 8.3234 | 2 | 0 | 0 | 1.3 | pedagogy_benchmark |
| `gpt-5.5` | `P03` 多模态理解 | SRG | 5.757 | 1 | 0 | 0 | 0.17 | tutorbench |
| `gpt-5.5` | `P14` 个性化教学策略选择 | CLM | 5.757 | 1 | 0 | 0 | 0.17 | tutorbench |
| `gpt-5.5` | `P16` 适配性解释与反馈生成 | CLM | 5.757 | 1 | 0 | 0 | 0.425 | tutorbench |
| `gpt-5.5` | `P17` 教育角色边界判断 | CEG | 8.4338 | 3 | 0 | 0 | 0.795 | eduguard_adversarial, eduguard_sata |
| `gpt-5.5` | `P18` 学生风险识别 | CEG | 7.395 | 1 | 0 | 0 | 0.2 | eduguard_sata |
| `gpt-5.5` | `P19` 安全处置选择 | CEG | 8.1514 | 3 | 0 | 0 | 1.305 | eduguard_adversarial, eduguard_sata |
| `kimi-k2-6` | `P02` 长上下文与证据定位 | SRG | 7.3299 | 1 | 0 | 0 | 0.2 | sas_bench |
| `kimi-k2-6` | `P05` 知识调用与掌握 | FDR | 7.867 | 5 | 0 | 0 | 1.54 | edubench, pedagogy_benchmark, sas_bench |
| `kimi-k2-6` | `P06` 推理与生成 | FDR | 7.2262 | 3 | 0 | 0 | 0.795 | edubench, sas_bench |
| `kimi-k2-6` | `P10` 错误诊断 | LAD | 6.3095 | 3 | 0 | 0 | 1.06 | edubench, sas_bench |
| `kimi-k2-6` | `P11` 主观题评价能力 | LAD | 7.6214 | 2 | 0 | 0 | 1.3 | sas_bench |
| `kimi-k2-6` | `P12` 命题与作业设计 | LAD | 8.5477 | 2 | 0 | 0 | 0.595 | edubench |
| `kimi-k2-6` | `P13` 学习者画像建模 | CLM | 7.0168 | 2 | 0 | 0 | 0.37 | edubench, pedagogy_benchmark |
| `kimi-k2-6` | `P14` 个性化教学策略选择 | CLM | 7.3447 | 4 | 0 | 0 | 1.895 | edubench, pedagogy_benchmark |

## Coverage Notes

- `P17`-`P19` are covered through EduGuard P1/P2 safety evidence.
- `P08` (tool use / long-horizon) and `P20` (academic integrity) are declared domain gaps; `P16`/`P14` are single-source and `P12` covers 2 of 4 declared sub-abilities; `P18` has zero independent evidence (shared-SATA single cell) and `P11` is expression-quality-only.
- The atomic list is `P01-P20` (R20 doc-scheme renumbering, no tombstones).

Full P rows are in `09_atomic_p_scores.jsonl`; allocated evidence rows are in `09_atomic_p_score_evidence.jsonl`.
