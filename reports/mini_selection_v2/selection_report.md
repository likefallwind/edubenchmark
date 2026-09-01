# mini_v2 experimental selection report

> 状态：离线选题实验；尚未接入默认运行和正式 P01-P20 面板。

mini_v2 是代表性快速筛查集，不承诺复现全量绝对分。全量结果仍是校准依据。

- 抽样题：**4120**
- 固定全保题：**830**
- 日常总量：**4950**
- 目标 / 硬上限：**4500 / 5000**

## 抽样 Benchmark

| Benchmark | 运行 profile | 证据角色 | mini_v2 | 全量 | 比例 |
|---|---|---|---:|---:|---:|
| `mmlu_pro` | core | A | 80 | 12032 | 0.7% |
| `agieval` | core | A | 80 | 7272 | 1.1% |
| `olympiadbench` | core | A | 170 | 6728 | 2.5% |
| `asap_2` | core | A | 150 | 7421 | 2.0% |
| `sas_bench` | core | A | 250 | 4109 | 6.1% |
| `eduguard_sata` | core | A | 150 | 5270 | 2.8% |
| `edubench` | core | A | 150 | 3797 | 4.0% |
| `longtutor_evidence` | core | A | 100 | 3003 | 3.3% |
| `longtutor_diagnosis` | core | A | 100 | 1001 | 10.0% |
| `longtutor_teaching` | core | A | 100 | 1001 | 10.0% |
| `mathtutorbench_problem_solving` | core | A | 100 | 1319 | 7.6% |
| `mathtutorbench_solution_correctness` | core | A | 100 | 2004 | 5.0% |
| `mathtutorbench_mistake_location` | core | A | 100 | 2004 | 5.0% |
| `mathtutorbench_mistake_correction` | core | A | 100 | 1002 | 10.0% |
| `mathtutorbench_socratic` | core | A | 100 | 1319 | 7.6% |
| `mathtutorbench_pedagogy` | core | A | 100 | 1150 | 8.7% |
| `mathtutorbench_scaffolding` | core | A | 100 | 1150 | 8.7% |
| `ceval` | core | B | 150 | 1346 | 11.1% |
| `pedagogy_benchmark` | core | B | 200 | 1119 | 17.9% |
| `mathvista` | core | B | 100 | 1000 | 10.0% |
| `eduguard_adversarial` | core | B | 150 | 801 | 18.7% |
| `ifeval` | core | B | 100 | 541 | 18.5% |
| `mmtutorbench` | core | B | 100 | 770 | 13.0% |
| `k12vista` | core | B | 100 | 600 | 16.7% |
| `k12bench` | core | synthetic_expansion | 200 | 23640 | 0.8% |
| `tutorbench` | core | education_core | 200 | 1473 | 13.6% |
| `p07_selfcheck` | core | diagnostic | 100 | 550 | 18.2% |
| `p08_calibration` | core | diagnostic | 100 | 550 | 18.2% |
| `p08_abstention` | core | diagnostic | 100 | 500 | 20.0% |
| `mooccube_prereq` | core | diagnostic | 100 | 300 | 33.3% |
| `mathtutorbench_pedagogy_hard` | frontier | frontier | 75 | 327 | 22.9% |
| `mathtutorbench_scaffolding_hard` | frontier | frontier | 75 | 327 | 22.9% |
| `mrbench_tutor` | frontier | frontier | 60 | 200 | 30.0% |
| `bea2025_tutor` | frontier | frontier | 60 | 300 | 20.0% |
| `mrbench_judge` | judge | A | 60 | 13240 | 0.5% |
| `bea2025_judge` | judge | A | 60 | 9904 | 0.6% |

## 固定全保

| Benchmark | 角色 | 题数 | 模式 | 原因 |
|---|---|---:|---|---|
| `eduillustrate` | education_core | 230 | 全保 | already curated into 11 subject-grade cells; full generation/render chain |
| `eduequity` | safety_fairness | 400 | 全保 | 20 identity-axis x education-task cells are already small |
| `safe_child_llm` | safety_gate | 200 | 全保 | small safety gate; preserve age group and rare harm categories |

## 统一集合的运行 profiles

- **core**：`mmlu_pro`、`agieval`、`olympiadbench`、`asap_2`、`sas_bench`、`eduguard_sata`、`edubench`、`longtutor_evidence`、`longtutor_diagnosis`、`longtutor_teaching`、`mathtutorbench_problem_solving`、`mathtutorbench_solution_correctness`、`mathtutorbench_mistake_location`、`mathtutorbench_mistake_correction`、`mathtutorbench_socratic`、`mathtutorbench_pedagogy`、`mathtutorbench_scaffolding`、`ceval`、`pedagogy_benchmark`、`mathvista`、`eduguard_adversarial`、`ifeval`、`mmtutorbench`、`k12vista`、`k12bench`、`tutorbench`、`p07_selfcheck`、`p08_calibration`、`p08_abstention`、`mooccube_prereq`、`eduillustrate`、`eduequity`、`safe_child_llm`
- **frontier**：`mathtutorbench_pedagogy_hard`、`mathtutorbench_scaffolding_hard`、`mrbench_tutor`、`bea2025_tutor`
- **judge**：`mrbench_judge`、`bea2025_judge`

Judge calibration 是评测器质检工作流，不是被测模型 Benchmark，故不计入题量。

## 使用边界

- mini_v2 用于快速发现主要长短板和筛选需不需要跑全量。
- 不把 mini_v2 原始分与 full/mini_v1 无标注混排。
- QWK、Macro-F1、校准与分组安全指标会有更宽置信区间。
- 高风险发布、安全失败和小分差排名必须回到对应 Benchmark 全量。
