# Frontier selection v1 experimental report

> 状态：零 API 离线选题实验；用于前沿模型挑战，不代表题库总体分布。

- 抽样题：**4089**
- 固定全保覆盖题：**830**
- 总量：**4919** / 5000
- Benchmark：**39**
- 目标构成：全员失败 35% / 有对有错 60% / 全员通过最多约 5%
- 实际抽样构成：全员失败 27.8% / 有对有错 67.3% / 全员通过 4.8%

## 逐 Benchmark

| Benchmark | 题数 | 全员失败 | 有对有错 | 全员通过 | 平均错误率 | 平均两两分歧 |
|---|---:|---:|---:|---:|---:|---:|
| `mmlu_pro` | 80 | 28 | 48 | 4 | 0.7033 | 0.37 |
| `agieval` | 80 | 28 | 52 | 0 | 0.7244 | 0.3946 |
| `olympiadbench` | 170 | 59 | 102 | 9 | 0.6655 | 0.3929 |
| `asap_2` | 150 | 5 | 138 | 7 | 0.4485 | 0.4427 |
| `sas_bench` | 250 | 88 | 150 | 12 | 0.652 | 0.6 |
| `eduguard_sata` | 150 | 53 | 90 | 7 | 0.7213 | 0.36 |
| `edubench` | 150 | 0 | 143 | 7 | 0.3177 | 0.3907 |
| `longtutor_evidence` | 100 | 35 | 60 | 5 | 0.71 | 0.36 |
| `longtutor_diagnosis` | 100 | 35 | 60 | 5 | 0.71 | 0.36 |
| `longtutor_teaching` | 100 | 19 | 76 | 5 | 0.5466 | 0.4567 |
| `mathtutorbench_problem_solving` | 69 | 16 | 48 | 5 | 0.4899 | 0.3246 |
| `mathtutorbench_solution_correctness` | 100 | 35 | 60 | 5 | 0.684 | 0.36 |
| `mathtutorbench_mistake_location` | 100 | 35 | 60 | 5 | 0.684 | 0.36 |
| `mathtutorbench_mistake_correction` | 100 | 28 | 67 | 5 | 0.6235 | 0.357 |
| `mathtutorbench_socratic` | 100 | 35 | 60 | 5 | 0.6211 | 0.36 |
| `mathtutorbench_pedagogy` | 100 | 11 | 84 | 5 | 0.528 | 0.466 |
| `mathtutorbench_scaffolding` | 100 | 35 | 60 | 5 | 0.722 | 0.358 |
| `ceval` | 150 | 36 | 107 | 7 | 0.5506 | 0.3562 |
| `pedagogy_benchmark` | 200 | 53 | 137 | 10 | 0.623 | 0.383 |
| `mathvista` | 100 | 35 | 60 | 5 | 0.6733 | 0.4 |
| `eduguard_adversarial` | 150 | 36 | 107 | 7 | 0.5967 | 0.4756 |
| `ifeval` | 100 | 6 | 89 | 5 | 0.396 | 0.446 |
| `mmtutorbench` | 100 | 35 | 60 | 5 | 0.6233 | 0.4 |
| `k12vista` | 100 | 35 | 60 | 5 | 0.601 | 0.4 |
| `k12bench` | 200 | 70 | 120 | 10 | 0.7209 | 0.4 |
| `tutorbench` | 200 | 70 | 120 | 10 | 0.5586 | 0.4 |
| `p07_selfcheck` | 100 | 35 | 60 | 5 | 0.6747 | 0.362 |
| `p08_calibration` | 100 | 35 | 60 | 5 | 0.653 | 0.3587 |
| `p08_abstention` | 100 | 22 | 73 | 5 | 0.554 | 0.352 |
| `mooccube_prereq` | 100 | 35 | 60 | 5 | 0.718 | 0.31 |
| `mathtutorbench_pedagogy_hard` | 75 | 4 | 67 | 4 | 0.5347 | 0.4427 |
| `mathtutorbench_scaffolding_hard` | 75 | 26 | 45 | 4 | 0.6987 | 0.352 |
| `mrbench_tutor` | 60 | 5 | 52 | 3 | 0.43 | 0.49 |
| `bea2025_tutor` | 60 | 12 | 45 | 3 | 0.56 | 0.45 |
| `mrbench_judge` | 60 | 21 | 38 | 1 | 0.73 | 0.38 |
| `bea2025_judge` | 60 | 21 | 36 | 3 | 0.71 | 0.36 |

## 固定全保覆盖项

- `eduillustrate`：230 题；保持完整安全/公平/生成结构，未按错题率裁切。
- `eduequity`：400 题；保持完整安全/公平/生成结构，未按错题率裁切。
- `safe_child_llm`：200 题；保持完整安全/公平/生成结构，未按错题率裁切。

## 解释边界

- 全员失败题是未来能力边界，保留但不承担当前模型主排序。
- 有对有错题承担主要区分度；全员通过题只作少量覆盖锚点。
- 模型面板来自固定的仓库前沿 cohort；每个 Benchmark 在其中取全量表现最好的至多 5 个完整结果面。
- LLM-judged 题的难度和区分度依赖当前裁判；发布前应做跨 Judge 稳定性检查。
- 本集合分数不可与 full 或 mini_v2 原始分无标注混排。
