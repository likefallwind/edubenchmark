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

精选合计 **14381** 题 / 全量 **90903** 题 = **15.8%**（这 26 个可精选 benchmark）。

## 三、验收五项结果矩阵

| 项 | 判据 | 总数 | 未通过 |
|---|---|---:|---:|
| 1 逐格绝对分漂移 | \|Δ\|≤0.3 | 45 | 17 |
| 2 逐 P 绝对分漂移 | \|Δ\|≤0.2 | 18 | 9 |
| 3a 逐格排名 τ | τ≥0.9 | 36 | 20 |
| 3b 逐 P 排名 τ | τ≥0.9 | 18 | 7 |
| 4 留一法漂移 | \|Δ\|≤0.4 | 278 | 35 |
| 5 bootstrap 95%CI 半宽 | acc≤0.2 / stat≤0.5 | 43 | 27 |

留一法最差漂移：benchmark `sas_bench` · 格 `ECS error-cause consistency` · 留出模型 `minimax-m3` · Δ=-1.6214。

## 四、未通过明细

### 逐格 |Δ|>阈（17）

- `mrbench_judge` · 8-dimension tutor response judging · maxΔ=0.666
- `sas_bench` · CCS step scoring consistency · maxΔ=0.4464
- `sas_bench` · ECS error-cause consistency · maxΔ=1.6214
- `mathtutorbench_pedagogy` · Pedagogy IF · maxΔ=0.385
- `sas_bench` · QWK holistic total score · maxΔ=0.453
- `eduguard_adversarial` · Refusal quality distribution · maxΔ=0.448
- `mathtutorbench_scaffolding` · Scaffolding · maxΔ=1.135
- `edubench` · TMG/PCC × clarity_concision_inspiration + scenario_element_integration (task×metric) · maxΔ=0.403
- `longtutor_diagnosis` · four-category knowledge-state diagnosis macro-F1 · maxΔ=1.3144
- `edubench` · higher_order_thinking_ability_development (metric) · maxΔ=0.3703
- `longtutor_teaching` · judge dims: strategy_alignment + history_utilization (1-5) · maxΔ=0.3338
- `bea2025_judge` · judge labels: mistake/guidance/actionability · maxΔ=0.385
- `k12vista` · math problem-figure subset score · maxΔ=0.4534
- `edubench` · motivation_guidance_positive_feedback (metric) · maxΔ=0.4315
- `olympiadbench` · overall/subject/language/modality accuracy · maxΔ=0.3363
- `edubench` · personalized_adaptation_learning_support (metric) · maxΔ=0.7431
- `edubench` · scenario_element_integration (metric) · maxΔ=0.5091

### 逐格 τ<0.9（20）

- `mrbench_judge` · 8-dimension tutor response judging · τ=0.8667 (n=6)
- `sas_bench` · CCS step scoring consistency · τ=0.7143 (n=8)
- `sas_bench` · ECS error-cause consistency · τ=0.3571 (n=8)
- `longtutor_evidence` · Hallucination Check accuracy · τ=0.6667 (n=4)
- `longtutor_evidence` · Information Extraction accuracy · τ=0.3333 (n=4)
- `mathtutorbench_mistake_location` · Mistake Location · τ=0.8 (n=5)
- `longtutor_evidence` · Multi-session Reasoning accuracy · τ=0.6667 (n=4)
- `mathtutorbench_pedagogy` · Pedagogy IF · τ=0.7143 (n=7)
- `edubench` · QG × clarity_concision_inspiration + scenario_element_integration (task×metric) · τ=0.8788 (n=12)
- `sas_bench` · QWK holistic total score · τ=0.7857 (n=8)
- `mathtutorbench_solution_correctness` · Solution Correctness · τ=0.2 (n=5)
- `eduguard_sata` · Teaching Harm / SATA RFS · τ=0.4286 (n=7)
- `edubench` · error_identification_correction_accuracy (metric) · τ=0.8788 (n=12)
- `longtutor_teaching` · judge dims: strategy_alignment + history_utilization (1-5) · τ=0.6667 (n=4)
- `bea2025_judge` · judge labels: mistake/guidance/actionability · τ=0.8667 (n=6)
- `edubench` · motivation_guidance_positive_feedback (metric) · τ=0.7273 (n=12)
- `mmlu_pro` · overall/category accuracy · τ=0.8 (n=5)
- `edubench` · personalized_adaptation_learning_support (metric) · τ=0.7879 (n=12)
- `ifeval` · prompt-level strict accuracy · τ=0.8 (n=5)
- `edubench` · scenario_element_integration (metric) · τ=0.8703 (n=12)

### 逐 P |Δ|>阈（9）

- `P01` · maxΔ=0.2646
- `P06` · maxΔ=0.2513
- `P10` · maxΔ=0.3389
- `P11` · maxΔ=0.5165
- `P12` · maxΔ=0.2011
- `P13` · maxΔ=0.7549
- `P14` · maxΔ=0.3302
- `P16` · maxΔ=0.3065
- `P18` · maxΔ=0.209

### 逐 P τ<0.9（7）

- `P01` · τ=0.8 (n=5)
- `P02` · τ=0.8889 (n=9)
- `P03` · τ=0.8667 (n=10)
- `P04` · τ=0.7143 (n=7)
- `P12` · τ=0.8788 (n=12)
- `P17` · τ=0.8571 (n=8)
- `P18` · τ=0.5714 (n=8)

### 留一法（35）

- `sas_bench` · ECS error-cause consistency · 留出 deepseek-v4-pro · Δ=-0.6795
- `sas_bench` · ECS error-cause consistency · 留出 doubao-seed-2-0-pro · Δ=-1.173
- `sas_bench` · ECS error-cause consistency · 留出 glm-5.2 · Δ=-1.2294
- `sas_bench` · ECS error-cause consistency · 留出 minimax-m2.7 · Δ=-1.3463
- `sas_bench` · CCS step scoring consistency · 留出 minimax-m3 · Δ=-0.4464
- `sas_bench` · ECS error-cause consistency · 留出 minimax-m3 · Δ=-1.6214
- `sas_bench` · QWK holistic total score · 留出 minimax-m3 · Δ=-0.453
- `mrbench_judge` · 8-dimension tutor response judging · 留出 deepseek-v3-2 · Δ=0.411
- `mrbench_judge` · 8-dimension tutor response judging · 留出 minimax-m3 · Δ=0.435
- `edubench` · motivation_guidance_positive_feedback (metric) · 留出 claude-sonnet-4.6 · Δ=0.4634
- `edubench` · personalized_adaptation_learning_support (metric) · 留出 claude-sonnet-4.6 · Δ=0.7129
- `edubench` · scenario_element_integration (metric) · 留出 claude-sonnet-4.6 · Δ=0.491
- `edubench` · personalized_adaptation_learning_support (metric) · 留出 deepseek-v4-flash · Δ=0.5824
- `edubench` · scenario_element_integration (metric) · 留出 deepseek-v4-flash · Δ=0.4428
- `edubench` · personalized_adaptation_learning_support (metric) · 留出 doubao-seed-2-0-lite · Δ=0.6903
- `edubench` · scenario_element_integration (metric) · 留出 doubao-seed-2-0-lite · Δ=0.4368
- `edubench` · personalized_adaptation_learning_support (metric) · 留出 doubao-seed-2-0-pro · Δ=0.6853
- `edubench` · scenario_element_integration (metric) · 留出 doubao-seed-2-0-pro · Δ=0.4857
- `edubench` · TMG/PCC × clarity_concision_inspiration + scenario_element_integration (task×metric) · 留出 glm-5.1 · Δ=0.5205
- `edubench` · personalized_adaptation_learning_support (metric) · 留出 glm-5.1 · Δ=0.4922
- `edubench` · personalized_adaptation_learning_support (metric) · 留出 glm-5.2 · Δ=0.5199
- `edubench` · scenario_element_integration (metric) · 留出 glm-5.2 · Δ=0.4042
- `edubench` · personalized_adaptation_learning_support (metric) · 留出 kimi-k2-6 · Δ=0.6383
- `edubench` · personalized_adaptation_learning_support (metric) · 留出 minimax-m3 · Δ=0.6311
- `edubench` · personalized_adaptation_learning_support (metric) · 留出 qwen3-14b · Δ=0.4411
- `longtutor_diagnosis` · four-category knowledge-state diagnosis macro-F1 · 留出 deepseek-v4-pro · Δ=0.93
- `longtutor_diagnosis` · four-category knowledge-state diagnosis macro-F1 · 留出 glm-5.2 · Δ=1.1093
- `longtutor_diagnosis` · four-category knowledge-state diagnosis macro-F1 · 留出 minimax-m3 · Δ=1.1051
- `mathtutorbench_scaffolding` · Scaffolding · 留出 deepseek-v4-flash · Δ=-0.406
- `mathtutorbench_scaffolding` · Scaffolding · 留出 deepseek-v4-pro · Δ=0.873
- `mathtutorbench_scaffolding` · Scaffolding · 留出 doubao-seed-2-0-lite · Δ=0.459
- `mathtutorbench_scaffolding` · Scaffolding · 留出 doubao-seed-2-0-pro · Δ=0.779
- `mathtutorbench_scaffolding` · Scaffolding · 留出 minimax-m2.7 · Δ=1.344
- `mathtutorbench_scaffolding` · Scaffolding · 留出 minimax-m3 · Δ=1.246
- `eduguard_adversarial` · Refusal quality distribution · 留出 glm-5.2 · Δ=-0.484

### bootstrap CI（27）

- `sas_bench` · CCS step scoring consistency · 半宽=0.5437 (阈 0.5)
- `sas_bench` · ECS error-cause consistency · 半宽=0.9497 (阈 0.5)
- `longtutor_evidence` · Hallucination Check accuracy · 半宽=0.8334 (阈 0.2)
- `longtutor_evidence` · Information Extraction accuracy · 半宽=0.3724 (阈 0.2)
- `mathtutorbench_mistake_correction` · Mistake Correction · 半宽=0.5417 (阈 0.2)
- `mathtutorbench_mistake_location` · Mistake Location · 半宽=0.542 (阈 0.2)
- `longtutor_evidence` · Multi-session Reasoning accuracy · 半宽=0.894 (阈 0.2)
- `mathtutorbench_pedagogy` · Pedagogy IF · 半宽=0.4295 (阈 0.2)
- `mathtutorbench_problem_solving` · Problem Solving · 半宽=0.3165 (阈 0.2)
- `sas_bench` · QWK holistic total score · 半宽=0.5656 (阈 0.5)
- `eduguard_adversarial` · Refusal quality distribution · 半宽=0.415 (阈 0.2)
- `mathtutorbench_scaffolding` · Scaffolding · 半宽=0.539 (阈 0.2)
- `mathtutorbench_socratic` · Socratic Questioning · 半宽=0.273 (阈 0.2)
- `mathtutorbench_solution_correctness` · Solution Correctness · 半宽=0.516 (阈 0.2)
- `eduguard_sata` · Teaching Harm / SATA RFS · 半宽=0.3105 (阈 0.2)
- `longtutor_diagnosis` · four-category knowledge-state diagnosis macro-F1 · 半宽=0.6189 (阈 0.5)
- `longtutor_teaching` · judge dims: strategy_alignment + history_utilization (1-5) · 半宽=0.2488 (阈 0.2)
- `k12vista` · math problem-figure subset score · 半宽=0.9202 (阈 0.2)
- `mmtutorbench` · multimodal tutor score · 半宽=0.2345 (阈 0.2)
- `olympiadbench` · multimodal-subset accuracy · 半宽=0.4433 (阈 0.2)
- `k12vista` · official partial-credit score (per-blank 0/1 mean) · 半宽=0.4685 (阈 0.2)
- `ceval` · overall/category/subject accuracy · 半宽=0.3154 (阈 0.2)
- `olympiadbench` · overall/subject/language/modality accuracy · 半宽=0.3009 (阈 0.2)
- `agieval` · overall/task/language/question_type accuracy · 半宽=0.2152 (阈 0.2)
- `ifeval` · prompt-level strict accuracy · 半宽=0.4358 (阈 0.2)
- `k12vista` · science/geo subject-chart subset score · 半宽=0.5602 (阈 0.2)
- `mathvista` · task/question_type/answer_type accuracy · 半宽=0.3472 (阈 0.2)

## 五、逐格漂移（前若干）

| benchmark | 格 | 模型数 | maxΔ | τ | CI半宽 |
|---|---|---:|---:|---:|---:|
| `sas_bench` | ECS error-cause consistency | 8 | 1.6214 | 0.3571 | 0.9497 |
| `longtutor_diagnosis` | four-category knowledge-state diagnosis macro- | 4 | 1.3144 | 1.0 | 0.6189 |
| `mathtutorbench_scaffolding` | Scaffolding | 7 | 1.135 | 0.9048 | 0.539 |
| `edubench` | personalized_adaptation_learning_support (metr | 12 | 0.7431 | 0.7879 | 0.1636 |
| `mrbench_judge` | 8-dimension tutor response judging | 6 | 0.666 | 0.8667 | 0.3255 |
| `edubench` | scenario_element_integration (metric) | 12 | 0.5091 | 0.8703 | 0.1196 |
| `k12vista` | math problem-figure subset score | 1 | 0.4534 | — | 0.9202 |
| `sas_bench` | QWK holistic total score | 8 | 0.453 | 0.7857 | 0.5656 |
| `eduguard_adversarial` | Refusal quality distribution | 7 | 0.448 | 1.0 | 0.415 |
| `sas_bench` | CCS step scoring consistency | 8 | 0.4464 | 0.7143 | 0.5437 |
| `edubench` | motivation_guidance_positive_feedback (metric) | 12 | 0.4315 | 0.7273 | 0.1055 |
| `edubench` | TMG/PCC × clarity_concision_inspiration + scen | 12 | 0.403 | 0.9091 | 0.1313 |
| `mathtutorbench_pedagogy` | Pedagogy IF | 7 | 0.385 | 0.7143 | 0.4295 |
| `bea2025_judge` | judge labels: mistake/guidance/actionability | 6 | 0.385 | 0.8667 | 0.2755 |
| `edubench` | higher_order_thinking_ability_development (met | 12 | 0.3703 | 0.9091 | 0.113 |
| `olympiadbench` | overall/subject/language/modality accuracy | 2 | 0.3363 | — | 0.3009 |
| `longtutor_teaching` | judge dims: strategy_alignment + history_utili | 4 | 0.3338 | 0.6667 | 0.2488 |
| `longtutor_evidence` | Hallucination Check accuracy | 4 | 0.2856 | 0.6667 | 0.8334 |
| `longtutor_evidence` | Multi-session Reasoning accuracy | 4 | 0.277 | 0.6667 | 0.894 |
| `longtutor_evidence` | Information Extraction accuracy | 4 | 0.2736 | 0.3333 | 0.3724 |
| `edubench` | QG × domain_knowledge_accuracy + basic_factual | 12 | 0.265 | 0.9394 | 0.1384 |
| `ifeval` | prompt-level strict accuracy | 5 | 0.2646 | 0.8 | 0.4358 |
| `mathtutorbench_solution_correctness` | Solution Correctness | 5 | 0.259 | 0.2 | 0.516 |
| `eduguard_sata` | Teaching Harm / SATA RFS | 7 | 0.209 | 0.4286 | 0.3105 |
| `edubench` | domain_knowledge_accuracy (metric) | 12 | 0.1997 | 0.9394 | 0.0631 |
| `edubench` | error_identification_correction_accuracy (metr | 12 | 0.1961 | 0.8788 | 0.1271 |
| `edubench` | clarity_concision_inspiration (metric) | 12 | 0.1951 | 0.9091 | 0.0556 |
| `edubench` | reasoning_process_rigor (metric) | 12 | 0.193 | 0.9394 | 0.0814 |
| `edubench` | QG × clarity_concision_inspiration + scenario_ | 12 | 0.1756 | 0.8788 | 0.148 |
| `ceval` | overall/category/subject accuracy | 5 | 0.173 | 0.9487 | 0.3154 |
| `eduguard_adversarial` | Adversarial Safety ASR | 7 | 0.159 | 1.0 | 0.296 |
| `olympiadbench` | multimodal-subset accuracy | 2 | 0.1447 | — | 0.4433 |
| `agieval` | overall/task/language/question_type accuracy | 5 | 0.1389 | 1.0 | 0.2152 |
| `edubench` | basic_factual_accuracy (metric) | 12 | 0.138 | 0.9394 | 0.0532 |
| `k12vista` | official partial-credit score (per-blank 0/1 m | 1 | 0.126 | — | 0.4685 |
| `mathtutorbench_mistake_correction` | Mistake Correction | 5 | 0.1206 | 0.9487 | 0.5417 |
| `mmlu_pro` | overall/category accuracy | 5 | 0.1088 | 0.8 | 0.1938 |
| `mathtutorbench_socratic` | Socratic Questioning | 4 | 0.097 | 1.0 | 0.273 |
| `mmtutorbench` | multimodal tutor score | 2 | 0.0822 | — | 0.2345 |
| `mathtutorbench_mistake_location` | Mistake Location | 5 | 0.073 | 0.8 | 0.542 |
| `mathtutorbench_problem_solving` | Problem Solving | 4 | 0.0705 | 1.0 | 0.3165 |
| `k12vista` | science/geo subject-chart subset score | 1 | 0.0475 | — | 0.5602 |
| `mathvista` | task/question_type/answer_type accuracy | 1 | 0.0187 | — | 0.3472 |
| `pedagogy_benchmark` | CDPK teaching knowledge selection | 0 | 0.0 | — | — |
| `pedagogy_benchmark` | SEND special education needs selection | 0 | 0.0 | — | — |

