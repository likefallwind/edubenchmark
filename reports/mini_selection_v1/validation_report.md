# 精选题集 mini_v1 离线验证报告

随机种子 `20260719`；本报告全程零 API 调用，只读取 `reports/eval/` 的全量逐题结果。

## 一、自校准（重算逻辑是否可信）

先用全量题目重算每个消费格与每个 P 分，与已发布的 `09/10` 产物对账，对得上才说明重算逻辑正确。

- 逐格全量重算 vs 已发布 `08` 的最大差：**0.0071**（对上，阈值 0.01）。
- 复用聚合脚本 `score_atomic_p` 重算 P 分 vs 已发布 `09` 的最大差：**0.0**（对上）。
- 已对账的格×模型面共 **295** 个。
- 说明：P 分是直接复用聚合脚本的 score_atomic_p 跑在已发布 08 证据上重算的，不是复刻实现；逐格分数按实际差值分档，导入面能对上的照样算对上，对不上的单列并注明原因。

### 无法对账的格（单列，不混进通过项）

共比对 **309** 条（格 × 模型面）：**291** 条逐位对上（差 ≤ 0.01），**4** 条落在舍入/导入协议噪声内（差 ≤ 0.05），**14** 条对不上。

对不上的这些格，已发布分数不是本仓库判分器算出来的，逐题重算复现不了它们，属于既有产物的口径问题，
不是本次抽样引入的误差。它们的**精选 vs 全量漂移仍然有效**（两侧都用同一套重算），
只是**绝对分无法与已发布值对账**。

| benchmark | 格 | 模型面数 | 最大差 | 原因 |
|---|---|---:|---:|---|
| `sas_bench` | CCS step scoring consistency, ECS error-cause consistency | 14 | 2.2753 | imported face: published metric was computed externally by the colleague's scorer; this repo's port cannot reproduce it from the converted per-item data |

证据：sas_bench 唯一一个由本仓库原生跑出来的模型面（`glm-5.2`）三个格全部**逐位对上（差 0.0000）**；
导入面的 QWK 也只差 0.003–0.04（QWK 只依赖导入时忠实保留的总分标签）。
差异集中在 CCS/ECS，这两个指标依赖导入过程未能等价保留的步骤级错因标注，
因此是系统性偏移（CCS +0.55~0.67、ECS +1.39~2.28），不是随机噪声，也不是重算 bug。

## 二、总量

精选合计 **14217** 题 / 全量 **90903** 题 = **15.6%**（这 26 个可精选 benchmark）。

## 三、验收五项结果矩阵

标准 1/2/4 不变；标准 3 与 5 本轮改为相对判据（依据见下），**原始绝对值一并保留**，
两套判据并列呈现，避免改标准把矩阵改好看。

| 项 | 判据 | 总数 | 未通过 |
|---|---|---:|---:|
| 1 逐格绝对分漂移 | \|Δ\|≤0.3 | 45 | 7 |
| 2 逐 P 绝对分漂移 | \|Δ\|≤0.2 | 18 | 4 |
| 3a 逐格排名 τ（**新**：只算可区分的模型对） | τ≥0.9 | 39 | 1 |
| 3a' 逐格排名 τ（旧：全部模型对，留档） | τ≥0.9 | 38 | 14 |
| 3b 逐 P 排名 τ | τ≥0.9 | 18 | 6 |
| 4 留一法漂移 | \|Δ\|≤0.4 | 300 | 5 |
| 5 抽样效率（**新**：实测CI膨胀/理论膨胀） | ≤1.3 | 43 | 1 |
| 5' bootstrap CI 绝对半宽（旧，留档） | acc≤0.2 / stat≤0.5 | 45 | 27 |

**标准 3 为什么改**：旧判据在 n=9 时一次相邻换位就掉到 0.889，实际等于要求零换位；
而且会把分数统计上无法区分的模型换位也判为失败。新判据只统计**全量分差超过该格 CI 半宽**的模型对，
分差在噪声内的换位不计。

**标准 5 为什么改**：旧的绝对门槛已证实错配 —— 13 个格所需样本量超过 benchmark 全量本身
（longtutor_evidence 幻觉检查需 6,051 题、该格全量只有 1,001），即**跑全量也过不了**，
它衡量的是 benchmark 自身精度而非精选保真度。新判据同时 bootstrap 全量与精选，比较
`实测比值 / 理论比值`，理论值 `sqrt(N_full/N_mini)` 是纯随机抽样必然产生的膨胀；
接近 1.0 表示分层抽样与随机抽样一样有效，明显大于 1 才是真问题（阈值 1.3）。
全量与自身比恒等于 1.0，逻辑自洽。

留一法最差漂移：benchmark `mathtutorbench_pedagogy` · 格 `Pedagogy IF` · 留出模型 `deepseek-v4-pro` · Δ=0.637。

## 四、未通过明细

### 逐格 |Δ|>阈（7）

- `sas_bench` · ECS error-cause consistency · maxΔ=0.4459
- `longtutor_evidence` · Hallucination Check accuracy · maxΔ=0.3339
- `eduguard_adversarial` · Refusal quality distribution · maxΔ=0.448
- `pedagogy_benchmark` · SEND special education needs selection · maxΔ=0.303
- `mathtutorbench_scaffolding` · Scaffolding · maxΔ=0.559
- `longtutor_teaching` · judge dims: strategy_alignment + history_utilization (1-5) · maxΔ=0.3712
- `olympiadbench` · overall/subject/language/modality accuracy · maxΔ=0.3402

### 逐格 τ<0.9（1）

- `mmlu_pro` · overall/category accuracy · τ=0.8 (n=5)

### 逐 P |Δ|>阈（4）

- `P01` · maxΔ=0.2427
- `P12` · maxΔ=0.2011
- `P13` · maxΔ=0.2576
- `P18` · maxΔ=0.2

### 逐 P τ<0.9（6）

- `P03` · τ=0.8667 (n=10)
- `P04` · τ=0.7143 (n=7)
- `P06` · τ=0.8974 (n=13)
- `P12` · τ=0.8788 (n=12)
- `P17` · τ=0.8571 (n=8)
- `P18` · τ=0.691 (n=8)

### 留一法（5）

- `sas_bench` · ECS error-cause consistency · 留出 kimi-k2-6 · Δ=0.4459
- `mrbench_judge` · 8-dimension tutor response judging · 留出 minimax-m3 · Δ=0.443
- `mathtutorbench_pedagogy` · Pedagogy IF · 留出 deepseek-v4-pro · Δ=0.637
- `mathtutorbench_scaffolding` · Scaffolding · 留出 deepseek-v4-flash · Δ=-0.471
- `eduguard_adversarial` · Refusal quality distribution · 留出 glm-5.2 · Δ=-0.492

### bootstrap CI 抽样效率（3）

- `pedagogy_benchmark` · CDPK teaching knowledge selection · 效率=None (阈 1.3;精选半宽 None / 全量半宽 None = None，理论 1.2915)
- `edubench` · QG × clarity_concision_inspiration + scenario_element_integration (task×metric) · 效率=1.3363 (阈 1.3;精选半宽 0.1569 / 全量半宽 0.0407 = 3.8562，理论 2.8856)
- `pedagogy_benchmark` · SEND special education needs selection · 效率=None (阈 1.3;精选半宽 None / 全量半宽 None = None，理论 1.291)

## 五、已接受的漂移（用户裁决：不加题，带注记进面板）

这些格 |Δ| 超过 0.3，但残差在噪声量级内（maxΔ / CI 半宽约 0.4–1.1），
即漂移来自抽样方差而非系统偏差。用户已裁决**不加题**（加题会推高总占比，
且为了让指标好看而加题是被明确禁止的）。这些格将来进面板时必须带 mini_v1 漂移注记。

| benchmark | 格 | maxΔ | CI半宽 | Δ/CI |
|---|---|---:|---:|---:|
| `mathtutorbench_scaffolding` | Scaffolding | 0.559 | 0.6165 | 0.91 |
| `eduguard_adversarial` | Refusal quality distribution | 0.448 | 0.47 | 0.95 |
| `sas_bench` | ECS error-cause consistency | 0.4459 | 0.7402 | 0.6 |
| `longtutor_teaching` | judge dims: strategy_alignment + history_uti | 0.3712 | 0.425 | 0.87 |
| `olympiadbench` | overall/subject/language/modality accuracy | 0.3402 | 0.3292 | 1.03 |
| `longtutor_evidence` | Hallucination Check accuracy | 0.3339 | 0.8199 | 0.41 |
| `pedagogy_benchmark` | SEND special education needs selection | 0.303 | — | — |

## 六、逐格漂移与排名（新旧判据并列）

| benchmark | 格 | 模型数 | maxΔ | τ新(可区分对) | 可区分对数 | τ旧(全部对) | CI半宽精选 | CI半宽全量 | 抽样效率 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `mathtutorbench_scaffolding` | Scaffolding | 7 | 0.559 | 1.0 | 19/21 | 1.0 | 0.6165 | 0.248 | 0.8978 |
| `eduguard_adversarial` | Refusal quality distribution | 7 | 0.448 | 1.0 | 20/21 | 1.0 | 0.47 | 0.259 | 1.147 |
| `sas_bench` | ECS error-cause consistency | 8 | 0.4459 | 1.0 | 11/28 | 0.7143 | 0.7402 | 0.712 | 0.6505 |
| `longtutor_teaching` | judge dims: strategy_alignment + history | 4 | 0.3712 | 1.0 | 5/6 | 0.6667 | 0.425 | 0.165 | 0.9971 |
| `olympiadbench` | overall/subject/language/modality accura | 2 | 0.3402 | 1.0 | 1/1 | — | 0.3292 | 0.1078 | 1.0579 |
| `longtutor_evidence` | Hallucination Check accuracy | 4 | 0.3339 | 1.0 | 5/6 | 0.6667 | 0.8199 | 0.2893 | 0.9813 |
| `pedagogy_benchmark` | SEND special education needs selection | 11 | 0.303 | — | 0/55 | 0.9162 | — | — | — |
| `longtutor_evidence` | Multi-session Reasoning accuracy | 4 | 0.277 | 1.0 | 3/6 | 0.6667 | 0.7972 | 0.2482 | 1.112 |
| `longtutor_evidence` | Information Extraction accuracy | 4 | 0.2736 | 1.0 | 3/6 | 0.3333 | 0.3444 | 0.1023 | 1.1657 |
| `edubench` | QG × domain_knowledge_accuracy + basic_f | 12 | 0.265 | 1.0 | 63/66 | 0.9394 | 0.1319 | 0.0357 | 1.2792 |
| `mathtutorbench_pedagogy` | Pedagogy IF | 7 | 0.263 | 1.0 | 16/21 | 0.9048 | 0.5665 | 0.1955 | 1.0465 |
| `mathtutorbench_solution_correctness` | Solution Correctness | 5 | 0.259 | 1.0 | 4/10 | 0.2 | 0.516 | 0.1685 | 1.0598 |
| `ifeval` | prompt-level strict accuracy | 5 | 0.2427 | 1.0 | 4/10 | 0.9487 | 0.4672 | 0.2879 | 1.0252 |
| `eduguard_sata` | Teaching Harm / SATA RFS | 7 | 0.2 | 1.0 | 11/21 | 0.5855 | 0.2575 | 0.1015 | 0.8785 |
| `edubench` | TMG/PCC × clarity_concision_inspiration  | 12 | 0.1966 | 1.0 | 60/66 | 0.9394 | 0.1876 | 0.0758 | 0.8572 |
| `longtutor_diagnosis` | four-category knowledge-state diagnosis  | 4 | 0.1962 | 1.0 | 5/6 | 1.0 | 0.5568 | 0.2808 | 0.7701 |
| `ceval` | overall/category/subject accuracy | 5 | 0.1757 | 1.0 | 6/10 | 0.9487 | 0.3253 | 0.1783 | 1.1533 |
| `edubench` | QG × clarity_concision_inspiration + sce | 12 | 0.1756 | 0.9365 | 63/66 | 0.8788 | 0.1569 | 0.0407 | 1.3363 |
| `bea2025_judge` | judge labels: mistake/guidance/actionabi | 6 | 0.175 | 1.0 | 14/15 | 0.8667 | 0.2825 | 0.0885 | 1.1055 |
| `mrbench_judge` | 8-dimension tutor response judging | 6 | 0.172 | 1.0 | 11/15 | 0.8667 | 0.3135 | 0.219 | 0.4959 |
| `eduguard_adversarial` | Adversarial Safety ASR | 7 | 0.172 | 1.0 | 21/21 | 1.0 | 0.2815 | 0.206 | 0.8637 |
| `mathtutorbench_mistake_correction` | Mistake Correction | 5 | 0.1706 | 1.0 | 6/10 | 0.9487 | 0.5667 | 0.2046 | 1.0717 |
| `olympiadbench` | multimodal-subset accuracy | 2 | 0.1447 | 1.0 | 1/1 | — | 0.4433 | 0.1621 | 0.9478 |
| `edubench` | domain_knowledge_accuracy (metric) | 12 | 0.1398 | 0.9692 | 65/66 | 0.9394 | 0.0768 | 0.0258 | 1.0306 |
| `pedagogy_benchmark` | CDPK teaching knowledge selection | 11 | 0.1348 | — | 0/55 | 1.0 | — | — | — |
| `agieval` | overall/task/language/question_type accu | 5 | 0.1278 | 1.0 | 9/10 | 1.0 | 0.252 | 0.0817 | 1.0687 |
| `sas_bench` | QWK holistic total score | 8 | 0.118 | 1.0 | 20/28 | 1.0 | 0.2353 | 0.1896 | 0.7766 |
| `edubench` | error_identification_correction_accuracy | 12 | 0.1177 | 1.0 | 65/66 | 0.9697 | 0.1349 | 0.0423 | 1.1057 |
| `mmlu_pro` | overall/category accuracy | 5 | 0.1149 | 0.7778 | 9/10 | 0.8 | 0.1766 | 0.0661 | 0.9259 |
| `mmtutorbench` | multimodal tutor score | 2 | 0.1137 | 1.0 | 1/1 | — | 0.2788 | 0.1525 | 1.156 |
| `edubench` | personalized_adaptation_learning_support | 12 | 0.0998 | 0.9667 | 60/66 | 0.8485 | 0.1711 | 0.0625 | 0.9477 |
| `edubench` | scenario_element_integration (metric) | 12 | 0.0982 | 1.0 | 60/66 | 0.9313 | 0.1316 | 0.0498 | 0.9161 |
| `edubench` | motivation_guidance_positive_feedback (m | 12 | 0.0917 | 0.9661 | 59/66 | 0.8485 | 0.1327 | 0.04 | 1.1485 |
| `edubench` | reasoning_process_rigor (metric) | 12 | 0.0908 | 0.9688 | 64/66 | 0.9313 | 0.0932 | 0.0316 | 1.022 |
| `mathtutorbench_socratic` | Socratic Questioning | 4 | 0.089 | 1.0 | 5/6 | 1.0 | 0.282 | 0.084 | 1.1619 |
| `sas_bench` | CCS step scoring consistency | 8 | 0.0862 | 1.0 | 21/28 | 0.9286 | 0.2653 | 0.2433 | 0.6823 |
| `edubench` | higher_order_thinking_ability_developmen | 12 | 0.0749 | 1.0 | 63/66 | 0.9697 | 0.1305 | 0.0408 | 1.1077 |
| `mathtutorbench_mistake_location` | Mistake Location | 5 | 0.073 | 1.0 | 3/10 | 0.8 | 0.542 | 0.177 | 1.0597 |
| `mathtutorbench_problem_solving` | Problem Solving | 4 | 0.0705 | 1.0 | 3/6 | 1.0 | 0.3165 | 0.0872 | 1.2562 |
| `edubench` | clarity_concision_inspiration (metric) | 12 | 0.0667 | 0.9697 | 66/66 | 0.9697 | 0.0658 | 0.0203 | 1.1243 |
| `edubench` | basic_factual_accuracy (metric) | 12 | 0.0514 | 0.9077 | 65/66 | 0.9091 | 0.0735 | 0.0199 | 1.2804 |
| `k12vista` | science/geo subject-chart subset score | 1 | 0.0475 | — | 0/0 | — | 0.5602 | 0.3358 | 1.0539 |
| `k12vista` | official partial-credit score (per-blank | 1 | 0.043 | — | 0/0 | — | 0.5 | 0.319 | 0.9913 |
| `mathvista` | task/question_type/answer_type accuracy | 1 | 0.0294 | — | 0/0 | — | 0.3542 | 0.2156 | 1.039 |
| `k12vista` | math problem-figure subset score | 1 | 0.0278 | — | 0/0 | — | 0.9668 | 0.6705 | 0.9149 |

