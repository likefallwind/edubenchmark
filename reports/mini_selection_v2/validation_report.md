# mini_v2 experimental validation

> 零 API 离线可行性审计。mini_v2 是代表性筛查集，不是 full-score proxy。

- 日常总量：**4950** / 5000
- 所有目标题数达到：**是**
- 所有声明的内部轴层级有覆盖：**是**
- 固定全保计数一致：**是**
- 正式映射 Benchmark 全部属于统一集合：**是**
- 非空原子能力 facet 覆盖：**32/32**
- measurement cell 来源 Benchmark 在集合中：**104/104**
- 可计算排名的格：**61**；τ<0.8：**31**

| Benchmark | 实际/目标 | 内部层级全覆盖 | 最大绝对漂移 | 最低 τ | 重复题号行 |
|---|---:|---|---:|---:|---:|
| `agieval` | 80/80 | 是 | 0.6858 | 0.6172 | 0 |
| `asap_2` | 150/150 | 是 | 0.1223 | 0.7975 | 0 |
| `bea2025_judge` | 60/60 | 是 | 0.957 | 0.3889 | 0 |
| `bea2025_tutor` | 60/60 | 是 | 0.734 | 0.3904 | 0 |
| `ceval` | 150/150 | 是 | 0.2914 | 0.8889 | 0 |
| `edubench` | 150/150 | 是 | 0.3014 | 0.626 | 0 |
| `eduguard_adversarial` | 150/150 | 是 | 0.745 | 1.0 | 0 |
| `eduguard_sata` | 150/150 | 是 | 0.367 | 0.5 | 0 |
| `ifeval` | 100/100 | 是 | 0.2078 | 0.7143 | 0 |
| `k12bench` | 200/200 | 是 | 0.1518 | 0.6667 | 630 |
| `k12vista` | 100/100 | 是 | 0.7187 | 0.6667 | 0 |
| `longtutor_diagnosis` | 100/100 | 是 | 1.3628 | 0.3333 | 1 |
| `longtutor_evidence` | 100/100 | 是 | 1.1855 | 0.4183 | 3 |
| `longtutor_teaching` | 100/100 | 是 | 0.2075 | 0.8095 | 1 |
| `mathtutorbench_mistake_correction` | 100/100 | 是 | 0.1325 | 0.9092 | 0 |
| `mathtutorbench_mistake_location` | 100/100 | 是 | 0.36 | 0.3706 | 0 |
| `mathtutorbench_pedagogy` | 100/100 | 是 | 0.666 | 0.4789 | 0 |
| `mathtutorbench_pedagogy_hard` | 75/75 | 是 | 0.684 | 0.6667 | 0 |
| `mathtutorbench_problem_solving` | 100/100 | 是 | 0.1971 | 0.801 | 0 |
| `mathtutorbench_scaffolding` | 100/100 | 是 | 3.5 | 0.5556 | 0 |
| `mathtutorbench_scaffolding_hard` | 75/75 | 是 | 1.042 | 0.7778 | 0 |
| `mathtutorbench_socratic` | 100/100 | 是 | 0.252 | 0.619 | 0 |
| `mathtutorbench_solution_correctness` | 100/100 | 是 | 0.664 | 0.0 | 0 |
| `mathvista` | 100/100 | 是 | 0.27 | 0.9129 | 0 |
| `mmlu_pro` | 80/80 | 是 | 0.4092 | 0.691 | 0 |
| `mmtutorbench` | 100/100 | 是 | 0.2088 | 1.0 | 0 |
| `mooccube_prereq` | 100/100 | 是 | 0.921 | 0.6831 | 0 |
| `mrbench_judge` | 60/60 | 是 | 2.212 | 0.3889 | 0 |
| `mrbench_tutor` | 60/60 | 是 | 1.183 | 0.0 | 0 |
| `olympiadbench` | 170/170 | 是 | 0.5164 | 0.8 | 0 |
| `p07_selfcheck` | 100/100 | 是 | 0.518 | 0.1429 | 0 |
| `p08_abstention` | 100/100 | 是 | 0.32 | 0.6156 | 0 |
| `p08_calibration` | 100/100 | 是 | 0.494 | 0.7143 | 0 |
| `pedagogy_benchmark` | 200/200 | 是 | 0.3042 | 0.6754 | 0 |
| `sas_bench` | 250/250 | 是 | 2.7941 | 0.4667 | 0 |
| `tutorbench` | 200/200 | 是 | 0.3452 | 1.0 | 0 |

## 使用边界

- mini_v2 is a representative screen, not a full-score proxy
- absolute score drift is diagnostic and is expected to exceed mini_v1 thresholds
- pedagogy_benchmark under 600 items requires a mini_v2-aware aggregation floor
- K12Bench has repeated native item ids; item-list selection operates on unique ids
- LLM-judged rankings remain conditional on the selected judge
