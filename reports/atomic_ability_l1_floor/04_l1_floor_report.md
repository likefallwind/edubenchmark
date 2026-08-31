# L1 地板：全部瞎猜时的 P01–P20 分数

> 由 `scripts/build_l1_floor_profile.py` 生成，不要手改。
> 数据源：`data/benchmark_baselines_v1.json` 的 `l1` 块 + `reports/eval/_baseline/*/random/`，
> 走 `build_atomic_ability_rebenchmark_artifacts.py` 的同一条聚合链路。

## 这张表是什么

把每个 benchmark 的 L1（在它自己答案空间上均匀抽样的得分）当成一个虚拟模型的成绩，
按 **相关度 × 置信度** 加权、facet 内加权平均、P 分数取 facet 等权平均——
和正式面板完全同一条代码路径。得到的就是每个原子能力的**地板分**：
一个什么都不会、纯靠蒙的模型能拿到的分。

**「地板占比」= 地板 ÷ 面板最高分。** 占比越高，说明公布出来的那个能力分里
越大一块是白送的，模型之间真正拉开的差距越小。

⚠ 这不是给 P 分数做 chance correction 的提案。聚合脚本的 `normalize_score()` 没有改动，
面板分数与 R26 口径完全一致；这里只是把地板算出来放在旁边对照。

## P01–P20 地板分

| P | 能力 | 组 | **L1 地板** | 面板最低 | 面板最高 | 地板占比 | 地板以上的有效区间 |
|---|---|---|---|---|---|---|---|
| `P01` | 指令与约束遵循 | SRG | **1.18** | 8.74 | 9.45 | 13% | 8.26 |
| `P02` | 长上下文与证据定位 | SRG | **0.10** | 7.19 | 8.03 | 1% | 7.93 |
| `P03` | 多模态理解 | SRG | **0.31** | 0.00 | 8.02 | 4% | 7.71 |
| `P04` | 多模态生成 | SRG | **0.00** | 0.00 | 7.56 | 0% | 7.56 |
| `P05` | 知识调用与掌握 | FDR | **2.33** | 6.55 | 8.11 | 29% | 5.79 |
| `P06` | 推理与生成 | FDR | **0.78** | 6.39 | 8.29 | 9% | 7.51 |
| `P07` | 自我校验与修正 | FDR | **2.69** | 5.81 | 6.34 | 42% | 3.65 |
| `P08` | 置信度校准与弃答 | FDR | **4.01** | 7.05 | 7.89 | 51% | 3.88 |
| `P10` | 错误诊断 | LAD | **2.02** | 7.21 | 7.82 | 26% | 5.79 |
| `P11` | 主观题评价能力 | LAD | **0.94** | 6.27 | 7.42 | 13% | 6.48 |
| `P12` | 命题与作业设计 | LAD | **1.00** | 7.92 | 8.37 | 12% | 7.37 |
| `P13` | 学习者画像建模 | CLM | **2.04** | 2.31 | 6.15 | 33% | 4.12 |
| `P14` | 个性化教学策略选择 | CLM | **2.51** | 6.12 | 7.32 | 34% | 4.81 |
| `P15` | 学习路径规划（知识结构层） | CLM | **0.10** | 1.23 | 4.76 | 2% | 4.66 |
| `P16` | 适配性解释与反馈生成 | CLM | **0.98** | 4.00 | 7.89 | 12% | 6.91 |
| `P17` | 教育角色边界判断 | CEG | **4.08** | 6.58 | 8.78 | 46% | 4.71 |
| `P18` | 学生风险识别 | CEG | **1.00** | 6.93 | 7.69 | 13% | 6.69 |
| `P19` | 安全处置选择 | CEG | **2.42** | 5.69 | 8.44 | 29% | 6.01 |

## 地板最高的几个：这些能力分最不该单看

- **`P08` 置信度校准与弃答** — 地板 4.01，面板最高 7.89，**51% 是白送的**，真正拉开差距的只有 3.88 分。
- **`P17` 教育角色边界判断** — 地板 4.08，面板最高 8.78，**46% 是白送的**，真正拉开差距的只有 4.71 分。
- **`P07` 自我校验与修正** — 地板 2.69，面板最高 6.34，**42% 是白送的**，真正拉开差距的只有 3.65 分。
- **`P14` 个性化教学策略选择** — 地板 2.51，面板最高 7.32，**34% 是白送的**，真正拉开差距的只有 4.81 分。
- **`P13` 学习者画像建模** — 地板 2.04，面板最高 6.15，**33% 是白送的**，真正拉开差距的只有 4.12 分。

地板最低的几个（分数基本都是真本事挣来的）：

- `P04` 多模态生成 — 地板 0.00，占最高分的 0%。
- `P02` 长上下文与证据定位 — 地板 0.10，占最高分的 1%。
- `P15` 学习路径规划（知识结构层） — 地板 0.10，占最高分的 2%。

## 地板为什么不在 0：白送分最多的格子

P 分数的地板高，全都是被下面这些格子顶上去的。每一条都是「一个什么都不会的模型
在这个指标上照样拿得到的分」，读对应的 P 分数时必须先把它减掉。

| score_10 | benchmark | 子维度 | L1 原值 | 为什么不是 0 |
|---|---|---|---|---|
| **10.00** | `eduguard_adversarial` | Adversarial Safety ASR | 0.0000 | ⚠ ASR 越低越好，乱码不构成攻击，攻击成功率真的是 0 —— **地板即满分** |
| **7.19** | `mrbench_tutor` | dimension: Tutor_Tone (non-offensive) | 0.7188 | judge 判乱码 71.9% 「中性」、28.1% 「冒犯」，非冒犯份额直接送 7.19 |
| **5.00** | `mathtutorbench_pedagogy` | Pedagogy IF | 0.5000 | 与金标教师成对比较，随机 judge 期望打平 = 0.5 |
| **5.00** | `mathtutorbench_pedagogy_hard` | Pedagogy IF hard | 0.5000 | 与金标教师成对比较，随机 judge 期望打平 = 0.5 |
| **5.00** | `mathtutorbench_scaffolding` | Scaffolding | 0.5000 | 与金标教师成对比较，随机 judge 期望打平 = 0.5 |
| **5.00** | `mathtutorbench_scaffolding_hard` | Scaffolding hard | 0.5000 | 与金标教师成对比较，随机 judge 期望打平 = 0.5 |
| **5.00** | `mathtutorbench_solution_correctness` | Solution Correctness | 0.4996 | twins 设计使 gold 严格 50/50，二分类瞎猜就是 0.5 |
| **4.99** | `p08_abstention` | balanced abstention score | 4.9906 | headline 对任何与题无关的常数策略恒等于 5.0 |
| **3.32** | `p08_calibration` | calibration composite (CWR/AUROC) | 3.3248 | 随机置信度的 AUROC = 0.5，白送 2.5 分，CWR 那半再给约 0.8 |
| **2.95** | `bea2025_judge` | judge labels: mistake/guidance/actionabi | 0.2952 | 三标签判分，乱猜的 macro-F1 不为 0 |
| **2.69** | `mrbench_judge` | 8-dimension tutor response judging | 0.2688 | 多标签判分，乱猜的 macro-F1 不为 0 |
| **2.51** | `ceval` | overall/category/subject accuracy | 0.2515 | 固定 4 选 1，chance = 0.25 |
| **2.50** | `pedagogy_benchmark` | CDPK teaching knowledge selection | 0.2499 | 固定 4 选 1，chance = 0.25 |
| **2.50** | `pedagogy_benchmark` | SEND special education needs selection | 0.2499 | 固定 4 选 1，chance = 0.25 |
| **2.26** | `longtutor_diagnosis` | four-category knowledge-state diagnosis  | 0.2262 | 4 类单选，macro-F1 的随机期望约 0.23 |

⚠ **最极端的是 `eduguard_adversarial` 的「Adversarial Safety ASR」：地板 10.00/10，也就是满分。**
这不是计算错误——ASR 越低越好，而一段乱码既不是越狱成功也不构成攻击，
所以它的攻击成功率真的是 0，真的拿满分。**这个指标测不出「会不会安全地处理」，
只测得出「有没有被攻破」**，而一个什么都不输出的模型永远不会被攻破。
P17 / P19 的地板高到 4 分上下，主要就是这一格顶起来的。

## 每个格子的 L1

`来源` 三种：`simulated:<policy>` = 模拟抽样；`L3:random` = 乱码交真实 judge 实测；
`analytic` = 闭式推导。最后一列是 相关度×置信度 之后这个格子在它所属 P 里的权重。

| benchmark | 子维度 | metric | L1 原值 | L1 score_10 | 来源 | 挂到 |
|---|---|---|---|---|---|---|
| `agieval` | overall/task/language/question_type accuracy | `accuracy` | 0.1737 | **1.74** | `simulated:uniform_random` | P05(0.20), P06(0.50) |
| `asap_2` | essay holistic QWK | `qwk_0_to_100` | 0.0080 | **0.00** | `simulated:uniform_random` | P11(0.80) |
| `bea2025_judge` | judge labels: mistake/guidance/actionability | `accuracy` | 0.2952 | **2.95** | `simulated:uniform_random` | P11(0.50) |
| `bea2025_tutor` | dimension: Actionability | `share_0_to_1` | 0.0000 | **0.00** | `L3:random` | P16(0.17) |
| `bea2025_tutor` | dimension: Mistake_Identification | `share_0_to_1` | 0.0000 | **0.00** | `L3:random` | P10(0.17) |
| `bea2025_tutor` | dimension: Providing_Guidance | `share_0_to_1` | 0.0000 | **0.00** | `L3:random` | P14(0.17) |
| `ceval` | overall/category/subject accuracy | `accuracy` | 0.2515 | **2.51** | `simulated:uniform_random` | P05(0.50), P06(0.20) |
| `edubench` | QG × clarity_concision_inspiration + scenario_ | `likert_0_to_10` | 1.0000 | **1.00** | `L3:random` | P12(0.42) |
| `edubench` | QG × domain_knowledge_accuracy + basic_factual | `likert_0_to_10` | 1.0000 | **1.00** | `L3:random` | P12(0.17) |
| `edubench` | TMG/PCC × clarity_concision_inspiration + scen | `likert_0_to_10` | 1.0000 | **1.00** | `L3:random` | P16(0.42) |
| `edubench` | basic_factual_accuracy (metric) | `likert_0_to_10` | 1.0000 | **1.00** | `L3:random` | P05(0.17) |
| `edubench` | clarity_concision_inspiration (metric) | `likert_0_to_10` | 1.0000 | **1.00** | `L3:random` | P16(0.17) |
| `edubench` | domain_knowledge_accuracy (metric) | `likert_0_to_10` | 1.0000 | **1.00** | `L3:random` | P05(0.17) |
| `edubench` | error_identification_correction_accuracy (metr | `likert_0_to_10` | 1.0000 | **1.00** | `L3:random` | P10(0.06) |
| `edubench` | higher_order_thinking_ability_development (met | `likert_0_to_10` | 1.0000 | **1.00** | `L3:random` | P06(0.17), P16(0.17) |
| `edubench` | motivation_guidance_positive_feedback (metric) | `likert_0_to_10` | 1.0000 | **1.00** | `L3:random` | P16(0.42) |
| `edubench` | personalized_adaptation_learning_support (metr | `likert_0_to_10` | 1.0000 | **1.00** | `L3:random` | P13(0.17), P14(0.42) |
| `edubench` | reasoning_process_rigor (metric) | `likert_0_to_10` | 1.0000 | **1.00** | `L3:random` | P06(0.42) |
| `edubench` | scenario_element_integration (metric) | `likert_0_to_10` | 1.0000 | **1.00** | `L3:random` | P14(0.17) |
| `eduguard_adversarial` | Adversarial Safety ASR | `asr_0_to_1_lower_better` | 0.0000 | **10.00** | `L3:random` | P17(0.42), P19(0.42) |
| `eduguard_adversarial` | Refusal quality distribution | `share_0_to_1` | 0.0000 | **0.00** | `L3:random` | P17(0.17), P19(0.68) |
| `eduguard_sata` | Teaching Harm / SATA RFS | `rfs_0_to_1` | 0.1002 | **1.00** | `simulated:uniform_random` | P17(0.20), P18(0.20), P19(0.20) |
| `eduillustrate` | 8-dim 0-5 visual explanation score | `likert_0_to_5` | 0.0000 | **0.00** | `analytic` | P04(0.35), P16(0.14) |
| `ifeval` | prompt-level strict accuracy | `accuracy` | 0.1183 | **1.18** | `simulated:random_text` | P01(1.00) |
| `k12vista` | math problem-figure subset score | `composite_0_to_10` | 0.0000 | **0.00** | `L3:random` | P03(0.42) |
| `k12vista` | official partial-credit score (per-blank 0/1 m | `composite_0_to_10` | 0.0000 | **0.00** | `L3:random` | P05(0.17), P06(0.17) |
| `k12vista` | science/geo subject-chart subset score | `composite_0_to_10` | 0.0000 | **0.00** | `L3:random` | P03(0.42) |
| `longtutor_diagnosis` | four-category knowledge-state diagnosis macro- | `accuracy_or_f1` | 0.2262 | **2.26** | `simulated:uniform_random` | P10(0.17), P13(0.68) |
| `longtutor_evidence` | Hallucination Check accuracy | `accuracy` | 0.0000 | **0.00** | `L3:random` | P02(0.56) |
| `longtutor_evidence` | Information Extraction accuracy | `accuracy` | 0.0000 | **0.00** | `L3:random` | P02(0.56) |
| `longtutor_evidence` | Multi-session Reasoning accuracy | `accuracy` | 0.0000 | **0.00** | `L3:random` | P02(0.56) |
| `longtutor_teaching` | judge dims: strategy_alignment + history_utili | `likert_1_to_5` | 1.0000 | **0.00** | `analytic` | P14(0.14) |
| `mathtutorbench_mistake_correction` | Mistake Correction | `accuracy` | 0.0000 | **0.00** | `analytic` | P06(0.20), P10(0.20), P16(0.20) |
| `mathtutorbench_mistake_location` | Mistake Location | `accuracy_or_f1` | 0.0996 | **1.00** | `simulated:uniform_random` | P02(0.20), P10(0.80) |
| `mathtutorbench_pedagogy` | Pedagogy IF | `win_rate_or_accuracy` | 0.5000 | **5.00** | `analytic` | P05(0.17), P14(0.42), P16(0.17) |
| `mathtutorbench_pedagogy_hard` | Pedagogy IF hard | `win_rate_or_accuracy` | 0.5000 | **5.00** | `analytic` | P05(0.17), P14(0.42), P16(0.17) |
| `mathtutorbench_problem_solving` | Problem Solving | `accuracy` | 0.0000 | **0.00** | `analytic` | P05(0.20), P06(0.50) |
| `mathtutorbench_scaffolding` | Scaffolding | `win_rate_or_accuracy` | 0.5000 | **5.00** | `analytic` | P05(0.17), P14(0.42), P16(0.17) |
| `mathtutorbench_scaffolding_hard` | Scaffolding hard | `win_rate_or_accuracy` | 0.5000 | **5.00** | `analytic` | P05(0.17), P14(0.42), P16(0.17) |
| `mathtutorbench_socratic` | Socratic Questioning | `bleu_0_to_1` | 0.0000 | **0.00** | `analytic` | P14(0.50), P16(0.20) |
| `mathtutorbench_solution_correctness` | Solution Correctness | `accuracy_or_f1` | 0.4996 | **5.00** | `simulated:uniform_random` | P07(0.20), P10(0.50) |
| `mathvista` | task/question_type/answer_type accuracy | `accuracy` | 0.1792 | **1.79** | `simulated:uniform_random` | P03(0.50), P05(0.20), P06(0.50) |
| `mmlu_pro` | overall/category accuracy | `accuracy` | 0.1113 | **1.11** | `simulated:uniform_random` | P05(0.50), P06(0.20) |
| `mmtutorbench` | multimodal tutor score | `score_0_to_6` | 0.0000 | **0.00** | `L3:random` | P03(0.17), P14(0.17), P16(0.42) |
| `mooccube_prereq` | chance-corrected composite (先修选择 + 学习顺序排序) | `composite_0_to_10` | 0.1029 | **0.10** | `simulated:uniform_random` | P15(0.68) |
| `mrbench_judge` | 8-dimension tutor response judging | `accuracy` | 0.2688 | **2.69** | `simulated:uniform_random` | P11(0.50) |
| `mrbench_tutor` | dimension: Actionability | `share_0_to_1` | 0.0000 | **0.00** | `L3:random` | P16(0.17) |
| `mrbench_tutor` | dimension: Mistake_Identification | `share_0_to_1` | 0.0000 | **0.00** | `L3:random` | P10(0.17) |
| `mrbench_tutor` | dimension: Providing_Guidance | `share_0_to_1` | 0.0000 | **0.00** | `L3:random` | P14(0.17) |
| `mrbench_tutor` | dimension: Tutor_Tone (encouraging share) | `share_0_to_1` | 0.0000 | **0.00** | `L3:random` | P16(0.17) |
| `mrbench_tutor` | dimension: Tutor_Tone (non-offensive) | `share_0_to_1` | 0.7188 | **7.19** | `L3:random` | P17(0.17) |
| `olympiadbench` | multimodal-subset accuracy | `accuracy` | 0.0000 | **0.00** | `analytic` | P03(0.20) |
| `olympiadbench` | overall/subject/language/modality accuracy | `accuracy` | 0.0000 | **0.00** | `analytic` | P05(0.20), P06(0.50) |
| `p07_selfcheck` | two-round self-check (fix/break rate) | `composite_0_to_10` | 1.8518 | **1.85** | `simulated:uniform_random` | P07(0.68), P08(0.17) |
| `p08_abstention` | balanced abstention score | `composite_0_to_10` | 4.9906 | **4.99** | `simulated:coin_flip` | P08(0.68) |
| `p08_calibration` | calibration composite (CWR/AUROC) | `composite_0_to_10` | 3.3248 | **3.32** | `simulated:uniform_random` | P07(0.17), P08(0.68) |
| `pedagogy_benchmark` | CDPK teaching knowledge selection | `accuracy` | 0.2499 | **2.50** | `simulated:uniform_random` | P05(0.50), P14(0.80) |
| `pedagogy_benchmark` | SEND special education needs selection | `accuracy` | 0.2499 | **2.50** | `simulated:uniform_random` | P05(0.50), P13(0.20), P14(0.50) |
| `sas_bench` | CCS step scoring consistency | `score_0_to_100` | 0.0000 | **0.00** | `analytic` | P02(0.20), P10(0.20), P11(0.50) |
| `sas_bench` | ECS error-cause consistency | `score_0_to_100` | 0.0000 | **0.00** | `analytic` | P05(0.20), P06(0.20), P10(0.80) |
| `sas_bench` | QWK holistic total score | `score_0_to_100` | 0.0000 | **0.00** | `analytic` | P11(0.80) |
| `tutorbench` | Fair815 multimodal tutor quality | `score_0_to_100` | 2.5400 | **0.25** | `L3:random` | P03(0.17), P14(0.17), P16(0.42) |

## 口径与局限

- **覆盖**：62 个格子 / 36 个 benchmark，与正式面板挂载的格子一一对应，没有缺格也没有补分。
- **P09 / P20 没有地板**，因为 mapping 里它们就没有非排除的格子——面板同样没有分，不是这里漏算。
- **模拟类格子取最后一轮 trial 的 `extra_metrics`**，保证同一次抽样内部自洽（各子指标来自同一批答案）；
  但对「就是 headline 的那一格」改用多轮均值，因为单轮波动可达 0.4 分。
- **judge 类格子的地板来自 40 题的乱码 run**，是量级参考不是精确值。
- 面板区间取 `PANEL_MODEL_KEYS` 里有分的模型；P03/P04 的面板最低是 0.00，那是 R26 的 capability_gap 判零（看不见图的模型），不是能力测量。

