# Frontier selection v1 validation

> 零 API 离线审计。通过题比例只针对 36 个难度抽样 Benchmark；3 个固定全保项另列。

- 总量：**4919** / 5000
- 抽样构成：全员失败 **27.8%**；有对有错 **67.3%**；全员通过 **4.8%**
- 正式映射 Benchmark：**36/36**
- 非空原子能力 facet：**32/32**
- measurement cell 来源：**104/104**
- 区分度相对全量提升的 Benchmark：**35/36**
- 少于 3 个前沿模型面的低置信 Benchmark：**sas_bench**

## 硬检查

- hard_ceiling：**通过**
- all_item_counts_match：**通过**
- all_item_list_hashes_match：**通过**
- all_benchmark_caps_respected：**通过**
- all_pooled_axis_buckets_covered：**通过**
- all_available_failure_and_mixed_classes_represented：**通过**
- sampled_unanimous_pass_share_at_most_target：**通过**
- all_mapped_benchmarks_in_collection：**通过**
- all_nonempty_atomic_facets_covered：**通过**
- all_measurement_cell_sources_present：**通过**
- all_frontier_panels_meet_minimum_size：**通过**

## 逐 Benchmark

| Benchmark | 实际/上限 | 全员失败 | 有对有错 | 全员通过 | 区分度增量 | 错误率增量 | 与 mini_v2 重合 |
|---|---:|---:|---:|---:|---:|---:|---:|
| `agieval` | 80/80 | 28 | 52 | 0 | 0.3365 | 0.6265 | 0.0% |
| `asap_2` | 150/150 | 5 | 138 | 7 | 0.4329 | 0.3183 | 2.0% |
| `bea2025_judge` | 60/60 | 21 | 36 | 3 | 0.158 | 0.3646 | 0.0% |
| `bea2025_tutor` | 60/60 | 12 | 45 | 3 | 0.2487 | 0.3733 | 21.7% |
| `ceval` | 150/150 | 36 | 107 | 7 | 0.3008 | 0.4814 | 10.7% |
| `edubench` | 150/150 | 0 | 143 | 7 | 0.3738 | 0.1366 | 4.7% |
| `eduguard_adversarial` | 150/150 | 36 | 107 | 7 | 0.0703 | 0.1991 | 16.0% |
| `eduguard_sata` | 150/150 | 53 | 90 | 7 | 0.2837 | 0.4821 | 4.7% |
| `ifeval` | 100/100 | 6 | 89 | 5 | 0.3362 | 0.3091 | 22.0% |
| `k12bench` | 200/200 | 70 | 120 | 10 | 0.2794 | 0.4741 | 1.5% |
| `k12vista` | 100/100 | 35 | 60 | 5 | 0.294 | 0.0522 | 19.0% |
| `longtutor_diagnosis` | 100/100 | 35 | 60 | 5 | 0.1246 | 0.118 | 5.0% |
| `longtutor_evidence` | 100/100 | 35 | 60 | 5 | 0.2722 | 0.5079 | 7.0% |
| `longtutor_teaching` | 100/100 | 19 | 76 | 5 | 0.2487 | 0.2283 | 12.0% |
| `mathtutorbench_mistake_correction` | 100/100 | 28 | 67 | 5 | 0.3054 | 0.5533 | 12.0% |
| `mathtutorbench_mistake_location` | 100/100 | 35 | 60 | 5 | 0.2809 | 0.4626 | 4.0% |
| `mathtutorbench_pedagogy` | 100/100 | 11 | 84 | 5 | 0.333 | 0.3743 | 20.0% |
| `mathtutorbench_pedagogy_hard` | 75/75 | 4 | 67 | 4 | 0.3057 | 0.3647 | 29.3% |
| `mathtutorbench_problem_solving` | 69/100 | 16 | 48 | 5 | 0.3076 | 0.4643 | 7.2% |
| `mathtutorbench_scaffolding` | 100/100 | 35 | 60 | 5 | 0.0217 | 0.1138 | 5.0% |
| `mathtutorbench_scaffolding_hard` | 75/75 | 26 | 45 | 4 | -0.004 | 0.0589 | 26.7% |
| `mathtutorbench_socratic` | 100/100 | 35 | 60 | 5 | 0.2473 | -0.0796 | 5.0% |
| `mathtutorbench_solution_correctness` | 100/100 | 35 | 60 | 5 | 0.2887 | 0.5665 | 5.0% |
| `mathvista` | 100/100 | 35 | 60 | 5 | 0.2892 | 0.5384 | 11.0% |
| `mmlu_pro` | 80/80 | 28 | 48 | 4 | 0.2932 | 0.5704 | 0.0% |
| `mmtutorbench` | 100/100 | 35 | 60 | 5 | 0.2698 | 0.2967 | 11.0% |
| `mooccube_prereq` | 100/100 | 35 | 60 | 5 | 0.168 | 0.2773 | 29.0% |
| `mrbench_judge` | 60/60 | 21 | 38 | 1 | 0.2172 | 0.4323 | 1.7% |
| `mrbench_tutor` | 60/60 | 5 | 52 | 3 | 0.253 | 0.2365 | 36.7% |
| `olympiadbench` | 170/170 | 59 | 102 | 9 | 0.2525 | 0.4162 | 4.7% |
| `p07_selfcheck` | 100/100 | 35 | 60 | 5 | 0.1625 | 0.337 | 19.0% |
| `p08_abstention` | 100/100 | 22 | 73 | 5 | 0.272 | 0.4384 | 21.0% |
| `p08_calibration` | 100/100 | 35 | 60 | 5 | 0.1886 | 0.312 | 16.0% |
| `pedagogy_benchmark` | 200/200 | 53 | 137 | 10 | 0.2602 | 0.4773 | 17.0% |
| `sas_bench` | 250/250 | 88 | 150 | 12 | 0.5597 | -0.2375 | 6.4% |
| `tutorbench` | 200/200 | 70 | 120 | 10 | 0.1419 | 0.2206 | 14.0% |

## 限制

- the eligible frontier cohort is fixed, but the available complete model faces can differ by benchmark
- unanimous failure is a future-facing challenge signal, not current-model discrimination
- fixed full EduIllustrate, EduEquity, and SafeChild items are coverage anchors and are not hardness-filtered
- LLM-judged item difficulty remains conditional on the current judge
- selection validity should be rechecked on held-out or newly released frontier models
- SAS-Bench currently has only two complete faces in the fixed frontier cohort, so its item labels are low-confidence
