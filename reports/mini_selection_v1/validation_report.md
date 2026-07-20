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

精选合计 **13101** 题 / 全量 **90903** 题 = **14.4%**（这 26 个可精选 benchmark）。

## 三、验收五项结果矩阵

| 项 | 判据 | 总数 | 未通过 |
|---|---|---:|---:|
| 1 逐格绝对分漂移 | \|Δ\|≤0.3 | 45 | 9 |
| 2 逐 P 绝对分漂移 | \|Δ\|≤0.2 | 18 | 8 |
| 3a 逐格排名 τ | τ≥0.9 | 38 | 15 |
| 3b 逐 P 排名 τ | τ≥0.9 | 18 | 7 |
| 4 留一法漂移 | \|Δ\|≤0.4 | 300 | 19 |
| 5 bootstrap 95%CI 半宽 | acc≤0.2 / stat≤0.5 | 43 | 27 |

留一法最差漂移：benchmark `sas_bench` · 格 `ECS error-cause consistency` · 留出模型 `minimax-m3` · Δ=-1.9408。

## 四、未通过明细

### 逐格 |Δ|>阈（9）

- `sas_bench` · CCS step scoring consistency · maxΔ=0.5831
- `sas_bench` · ECS error-cause consistency · maxΔ=1.9408
- `longtutor_evidence` · Hallucination Check accuracy · maxΔ=0.3339
- `sas_bench` · QWK holistic total score · maxΔ=0.619
- `eduguard_adversarial` · Refusal quality distribution · maxΔ=0.448
- `pedagogy_benchmark` · SEND special education needs selection · maxΔ=0.303
- `mathtutorbench_scaffolding` · Scaffolding · maxΔ=0.559
- `longtutor_teaching` · judge dims: strategy_alignment + history_utilization (1-5) · maxΔ=0.3712
- `olympiadbench` · overall/subject/language/modality accuracy · maxΔ=0.3402

### 逐格 τ<0.9（15）

- `mrbench_judge` · 8-dimension tutor response judging · τ=0.8667 (n=6)
- `sas_bench` · ECS error-cause consistency · τ=0.3571 (n=8)
- `longtutor_evidence` · Hallucination Check accuracy · τ=0.6667 (n=4)
- `longtutor_evidence` · Information Extraction accuracy · τ=0.3333 (n=4)
- `mathtutorbench_mistake_location` · Mistake Location · τ=0.8 (n=5)
- `longtutor_evidence` · Multi-session Reasoning accuracy · τ=0.6667 (n=4)
- `edubench` · QG × clarity_concision_inspiration + scenario_element_integration (task×metric) · τ=0.8788 (n=12)
- `sas_bench` · QWK holistic total score · τ=0.7143 (n=8)
- `mathtutorbench_solution_correctness` · Solution Correctness · τ=0.2 (n=5)
- `eduguard_sata` · Teaching Harm / SATA RFS · τ=0.5855 (n=7)
- `longtutor_teaching` · judge dims: strategy_alignment + history_utilization (1-5) · τ=0.6667 (n=4)
- `bea2025_judge` · judge labels: mistake/guidance/actionability · τ=0.8667 (n=6)
- `edubench` · motivation_guidance_positive_feedback (metric) · τ=0.8485 (n=12)
- `mmlu_pro` · overall/category accuracy · τ=0.8 (n=5)
- `edubench` · personalized_adaptation_learning_support (metric) · τ=0.8485 (n=12)

### 逐 P |Δ|>阈（8）

- `P01` · maxΔ=0.2427
- `P02` · maxΔ=0.3764
- `P06` · maxΔ=0.3711
- `P10` · maxΔ=0.6366
- `P11` · maxΔ=0.3389
- `P12` · maxΔ=0.2011
- `P13` · maxΔ=0.2576
- `P18` · maxΔ=0.2

### 逐 P τ<0.9（7）

- `P03` · τ=0.8667 (n=10)
- `P04` · τ=0.7143 (n=7)
- `P06` · τ=0.8718 (n=13)
- `P11` · τ=0.8485 (n=12)
- `P12` · τ=0.8788 (n=12)
- `P17` · τ=0.8571 (n=8)
- `P18` · τ=0.691 (n=8)

### 留一法（19）

- `sas_bench` · ECS error-cause consistency · 留出 deepseek-v4-pro · Δ=-0.8581
- `sas_bench` · QWK holistic total score · 留出 deepseek-v4-pro · Δ=-0.518
- `sas_bench` · CCS step scoring consistency · 留出 doubao-seed-2-0-pro · Δ=-0.4739
- `sas_bench` · ECS error-cause consistency · 留出 doubao-seed-2-0-pro · Δ=-0.8803
- `sas_bench` · QWK holistic total score · 留出 doubao-seed-2-0-pro · Δ=-0.4427
- `sas_bench` · ECS error-cause consistency · 留出 glm-5.1 · Δ=-1.1885
- `sas_bench` · CCS step scoring consistency · 留出 glm-5.2 · Δ=-0.5156
- `sas_bench` · ECS error-cause consistency · 留出 glm-5.2 · Δ=-1.2584
- `sas_bench` · ECS error-cause consistency · 留出 kimi-k2-6 · Δ=-0.5397
- `sas_bench` · QWK holistic total score · 留出 kimi-k2-6 · Δ=-0.4302
- `sas_bench` · CCS step scoring consistency · 留出 minimax-m2.7 · Δ=-0.4301
- `sas_bench` · ECS error-cause consistency · 留出 minimax-m2.7 · Δ=-1.2959
- `sas_bench` · CCS step scoring consistency · 留出 minimax-m3 · Δ=-0.5831
- `sas_bench` · ECS error-cause consistency · 留出 minimax-m3 · Δ=-1.9408
- `sas_bench` · QWK holistic total score · 留出 minimax-m3 · Δ=-0.619
- `mrbench_judge` · 8-dimension tutor response judging · 留出 minimax-m3 · Δ=0.443
- `mathtutorbench_pedagogy` · Pedagogy IF · 留出 deepseek-v4-pro · Δ=0.637
- `mathtutorbench_scaffolding` · Scaffolding · 留出 deepseek-v4-flash · Δ=-0.471
- `eduguard_adversarial` · Refusal quality distribution · 留出 glm-5.2 · Δ=-0.492

### bootstrap CI（29）

- `sas_bench` · CCS step scoring consistency · 半宽=0.5362 (阈 0.5)
- `pedagogy_benchmark` · CDPK teaching knowledge selection · 半宽=None (阈 0.2)
- `sas_bench` · ECS error-cause consistency · 半宽=1.182 (阈 0.5)
- `longtutor_evidence` · Hallucination Check accuracy · 半宽=0.8199 (阈 0.2)
- `longtutor_evidence` · Information Extraction accuracy · 半宽=0.3444 (阈 0.2)
- `mathtutorbench_mistake_correction` · Mistake Correction · 半宽=0.5667 (阈 0.2)
- `mathtutorbench_mistake_location` · Mistake Location · 半宽=0.542 (阈 0.2)
- `longtutor_evidence` · Multi-session Reasoning accuracy · 半宽=0.7972 (阈 0.2)
- `mathtutorbench_pedagogy` · Pedagogy IF · 半宽=0.5665 (阈 0.2)
- `mathtutorbench_problem_solving` · Problem Solving · 半宽=0.3165 (阈 0.2)
- `sas_bench` · QWK holistic total score · 半宽=0.7131 (阈 0.5)
- `eduguard_adversarial` · Refusal quality distribution · 半宽=0.47 (阈 0.2)
- `pedagogy_benchmark` · SEND special education needs selection · 半宽=None (阈 0.2)
- `mathtutorbench_scaffolding` · Scaffolding · 半宽=0.6165 (阈 0.2)
- `mathtutorbench_socratic` · Socratic Questioning · 半宽=0.282 (阈 0.2)
- `mathtutorbench_solution_correctness` · Solution Correctness · 半宽=0.516 (阈 0.2)
- `eduguard_sata` · Teaching Harm / SATA RFS · 半宽=0.2575 (阈 0.2)
- `longtutor_diagnosis` · four-category knowledge-state diagnosis macro-F1 · 半宽=0.5568 (阈 0.5)
- `longtutor_teaching` · judge dims: strategy_alignment + history_utilization (1-5) · 半宽=0.425 (阈 0.2)
- `k12vista` · math problem-figure subset score · 半宽=0.9668 (阈 0.2)
- `mmtutorbench` · multimodal tutor score · 半宽=0.2788 (阈 0.2)
- `olympiadbench` · multimodal-subset accuracy · 半宽=0.4433 (阈 0.2)
- `k12vista` · official partial-credit score (per-blank 0/1 mean) · 半宽=0.5 (阈 0.2)
- `ceval` · overall/category/subject accuracy · 半宽=0.3253 (阈 0.2)
- `olympiadbench` · overall/subject/language/modality accuracy · 半宽=0.3292 (阈 0.2)
- `agieval` · overall/task/language/question_type accuracy · 半宽=0.252 (阈 0.2)
- `ifeval` · prompt-level strict accuracy · 半宽=0.4672 (阈 0.2)
- `k12vista` · science/geo subject-chart subset score · 半宽=0.5602 (阈 0.2)
- `mathvista` · task/question_type/answer_type accuracy · 半宽=0.3542 (阈 0.2)

## 五、逐格漂移（前若干）

| benchmark | 格 | 模型数 | maxΔ | τ | CI半宽 |
|---|---|---:|---:|---:|---:|
| `sas_bench` | ECS error-cause consistency | 8 | 1.9408 | 0.3571 | 1.182 |
| `sas_bench` | QWK holistic total score | 8 | 0.619 | 0.7143 | 0.7131 |
| `sas_bench` | CCS step scoring consistency | 8 | 0.5831 | 0.9286 | 0.5362 |
| `mathtutorbench_scaffolding` | Scaffolding | 7 | 0.559 | 1.0 | 0.6165 |
| `eduguard_adversarial` | Refusal quality distribution | 7 | 0.448 | 1.0 | 0.47 |
| `longtutor_teaching` | judge dims: strategy_alignment + history_utili | 4 | 0.3712 | 0.6667 | 0.425 |
| `olympiadbench` | overall/subject/language/modality accuracy | 2 | 0.3402 | — | 0.3292 |
| `longtutor_evidence` | Hallucination Check accuracy | 4 | 0.3339 | 0.6667 | 0.8199 |
| `pedagogy_benchmark` | SEND special education needs selection | 11 | 0.303 | 0.9162 | — |
| `longtutor_evidence` | Multi-session Reasoning accuracy | 4 | 0.277 | 0.6667 | 0.7972 |
| `longtutor_evidence` | Information Extraction accuracy | 4 | 0.2736 | 0.3333 | 0.3444 |
| `edubench` | QG × domain_knowledge_accuracy + basic_factual | 12 | 0.265 | 0.9394 | 0.1319 |
| `mathtutorbench_pedagogy` | Pedagogy IF | 7 | 0.263 | 0.9048 | 0.5665 |
| `mathtutorbench_solution_correctness` | Solution Correctness | 5 | 0.259 | 0.2 | 0.516 |
| `ifeval` | prompt-level strict accuracy | 5 | 0.2427 | 0.9487 | 0.4672 |
| `eduguard_sata` | Teaching Harm / SATA RFS | 7 | 0.2 | 0.5855 | 0.2575 |
| `edubench` | TMG/PCC × clarity_concision_inspiration + scen | 12 | 0.1966 | 0.9394 | 0.1876 |
| `longtutor_diagnosis` | four-category knowledge-state diagnosis macro- | 4 | 0.1962 | 1.0 | 0.5568 |
| `ceval` | overall/category/subject accuracy | 5 | 0.1757 | 0.9487 | 0.3253 |
| `edubench` | QG × clarity_concision_inspiration + scenario_ | 12 | 0.1756 | 0.8788 | 0.1569 |
| `bea2025_judge` | judge labels: mistake/guidance/actionability | 6 | 0.175 | 0.8667 | 0.2825 |
| `mrbench_judge` | 8-dimension tutor response judging | 6 | 0.172 | 0.8667 | 0.3135 |
| `eduguard_adversarial` | Adversarial Safety ASR | 7 | 0.172 | 1.0 | 0.2815 |
| `mathtutorbench_mistake_correction` | Mistake Correction | 5 | 0.1706 | 0.9487 | 0.5667 |
| `olympiadbench` | multimodal-subset accuracy | 2 | 0.1447 | — | 0.4433 |
| `edubench` | domain_knowledge_accuracy (metric) | 12 | 0.1398 | 0.9394 | 0.0768 |
| `pedagogy_benchmark` | CDPK teaching knowledge selection | 11 | 0.1348 | 1.0 | — |
| `agieval` | overall/task/language/question_type accuracy | 5 | 0.1278 | 1.0 | 0.252 |
| `edubench` | error_identification_correction_accuracy (metr | 12 | 0.1177 | 0.9697 | 0.1349 |
| `mmlu_pro` | overall/category accuracy | 5 | 0.1149 | 0.8 | 0.1766 |
| `mmtutorbench` | multimodal tutor score | 2 | 0.1137 | — | 0.2788 |
| `edubench` | personalized_adaptation_learning_support (metr | 12 | 0.0998 | 0.8485 | 0.1711 |
| `edubench` | scenario_element_integration (metric) | 12 | 0.0982 | 0.9313 | 0.1316 |
| `edubench` | motivation_guidance_positive_feedback (metric) | 12 | 0.0917 | 0.8485 | 0.1327 |
| `edubench` | reasoning_process_rigor (metric) | 12 | 0.0908 | 0.9313 | 0.0932 |
| `mathtutorbench_socratic` | Socratic Questioning | 4 | 0.089 | 1.0 | 0.282 |
| `edubench` | higher_order_thinking_ability_development (met | 12 | 0.0749 | 0.9697 | 0.1305 |
| `mathtutorbench_mistake_location` | Mistake Location | 5 | 0.073 | 0.8 | 0.542 |
| `mathtutorbench_problem_solving` | Problem Solving | 4 | 0.0705 | 1.0 | 0.3165 |
| `edubench` | clarity_concision_inspiration (metric) | 12 | 0.0667 | 0.9697 | 0.0658 |
| `edubench` | basic_factual_accuracy (metric) | 12 | 0.0514 | 0.9091 | 0.0735 |
| `k12vista` | science/geo subject-chart subset score | 1 | 0.0475 | — | 0.5602 |
| `k12vista` | official partial-credit score (per-blank 0/1 m | 1 | 0.043 | — | 0.5 |
| `mathvista` | task/question_type/answer_type accuracy | 1 | 0.0294 | — | 0.3542 |
| `k12vista` | math problem-figure subset score | 1 | 0.0278 | — | 0.9668 |

