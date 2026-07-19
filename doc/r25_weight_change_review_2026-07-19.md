# R25 权重改革逐格审核清单(2026-07-19,按原子能力排列)

供逐格审核。规则、动机与影响面综述见 `mapping_review_pending_decisions_2026-07-19.md` 的 R25 节;本文件由脚本从 `data/mapping_measurement_model_v6.json` + 聚合脚本 `BENCHMARK_META` + 证据文件直接生成,数值与影响面计算同源。

**置信度规则(2026-07-19 用户裁决终版)**:起点 1.0,两因子各扣 0.15——

| 因子 | 不扣 | 扣 0.15 |
|---|---|---|
| **判分方式**(按实际判分路径,非名义描述) | 客观规则判分 | LLM-as-judge(LLM 输出的就是对错/好坏判断;仅做答案提取不算) |
| **质量** | 高质量:题目与金标有外部把关(官方发布/同行评议/人工标注) | 普通质量:自建自判,金标只有内部把关 |

**全表四值**:1.0(客观+高质量)/ 0.85(客观+普通 或 裁判+高质量)/ 0.7(裁判+普通)/ 0.3(唯一例外)。污染因子已取消,污染风险只留注记。严格纯规则,唯一例外 edubench error_identification 0.3(R23 已裁);实测噪声(judge-swap、κ、BLEU 效度)一律不进置信度,只作 rationale 注记。

**列说明**:三列权重均为 现值→新值,不变则单值。"相关度处理"列:`机械`=按归档规则自动落点(≤0.35→0.2,0.4–0.65→0.5,0.7–0.9→0.8,等距向下,低格并 0.2),`不变`=归档后数值恰好没变,**`裁决:…`**=偏离机械值的建议+理由(重点审)。"置信依据"列为该 benchmark 的两因子推导。

## 置信度变更总表(36 基准)

| benchmark | 现 | 新 | 判分 | 质量 | 依据 |
|---|---|---|---|---|---|
| agieval | 0.7 | **1.0** ◀ | 客观 | 高质量 | 客观0 高质量0 |
| asap_2 | 0.8 | **1.0** ◀ | 客观 | 高质量 | 客观0 高质量0 |
| bea2025_judge | 0.75 | **1.0** ◀ | 客观 | 高质量 | 客观0 高质量0 |
| bea2025_tutor | 0.9 | **0.85** ◀ | 裁判 | 高质量 | LLM 裁判-0.15 高质量0 |
| ceval | 0.7 | **1.0** ◀ | 客观 | 高质量 | 客观0 高质量0 |
| edubench | 0.8(override: TMG/PCC × clarity_concision_inspiration + scenario_element_integration (task×metric)=0.75, QG × clarity_concision_inspiration + scenario_element_integration (task×metric)=0.75, QG × domain_knowledge_accuracy + basic_factual_accuracy (task×metric)=0.75, error_identification_correction_accuracy (metric)=0.3) | **0.85** ◀ | 裁判 | 高质量 | LLM 裁判-0.15 高质量0 |
| eduguard_adversarial | 1.0(override: Refusal quality distribution=0.8) | **0.85** ◀ | 裁判 | 高质量 | LLM 裁判-0.15 高质量0 |
| eduguard_sata | 1.0 | **1.0** | 客观 | 高质量 | 客观0 高质量0 |
| eduillustrate | 0.85 | **0.7** ◀ | 裁判 | 普通 | LLM 裁判-0.15 普通质量-0.15(自建自判,金标无外部把关) |
| ifeval | 0.8 | **1.0** ◀ | 客观 | 高质量 | 客观0 高质量0 |
| k12vista | 0.8 | **0.85** ◀ | 裁判 | 高质量 | LLM 裁判-0.15 高质量0 |
| longtutor_diagnosis | 0.75 | **0.85** ◀ | 客观 | 普通 | 客观0 普通质量-0.15(自建自判,金标无外部把关) |
| longtutor_evidence | 0.75 | **0.7** ◀ | 裁判 | 普通 | LLM 裁判-0.15 普通质量-0.15(自建自判,金标无外部把关) |
| longtutor_teaching | 0.75 | **0.7** ◀ | 裁判 | 普通 | LLM 裁判-0.15 普通质量-0.15(自建自判,金标无外部把关) |
| mathtutorbench_mistake_correction | 0.9 | **1.0** ◀ | 客观 | 高质量 | 客观0 高质量0 |
| mathtutorbench_mistake_location | 1.0 | **1.0** | 客观 | 高质量 | 客观0 高质量0 |
| mathtutorbench_pedagogy | 0.95 | **0.85** ◀ | 裁判 | 高质量 | LLM 裁判-0.15 高质量0 |
| mathtutorbench_pedagogy_hard | 1.0 | **0.85** ◀ | 裁判 | 高质量 | LLM 裁判-0.15 高质量0 |
| mathtutorbench_problem_solving | 0.45 | **1.0** ◀ | 客观 | 高质量 | 客观0 高质量0 |
| mathtutorbench_scaffolding | 1.0 | **0.85** ◀ | 裁判 | 高质量 | LLM 裁判-0.15 高质量0 |
| mathtutorbench_scaffolding_hard | 1.0 | **0.85** ◀ | 裁判 | 高质量 | LLM 裁判-0.15 高质量0 |
| mathtutorbench_socratic | 0.6 | **1.0** ◀ | 客观 | 高质量 | 客观0 高质量0 |
| mathtutorbench_solution_correctness | 0.85 | **1.0** ◀ | 客观 | 高质量 | 客观0 高质量0 |
| mathvista | 0.7 | **1.0** ◀ | 客观 | 高质量 | 客观0 高质量0 |
| mmlu_pro | 0.7 | **1.0** ◀ | 客观 | 高质量 | 客观0 高质量0 |
| mmtutorbench | 0.9 | **0.85** ◀ | 裁判 | 高质量 | LLM 裁判-0.15 高质量0 |
| mooccube_prereq | 0.7 | **0.85** ◀ | 客观 | 普通 | 客观0 普通质量-0.15(自建自判,金标无外部把关) |
| mrbench_judge | 0.75 | **1.0** ◀ | 客观 | 高质量 | 客观0 高质量0 |
| mrbench_tutor | 0.8 | **0.85** ◀ | 裁判 | 高质量 | LLM 裁判-0.15 高质量0 |
| olympiadbench | 0.7 | **1.0** ◀ | 客观 | 高质量 | 客观0 高质量0 |
| p07_selfcheck | 0.85 | **0.85** | 客观 | 普通 | 客观0 普通质量-0.15(自建自判,金标无外部把关) |
| p08_abstention | 0.85 | **0.85** | 客观 | 普通 | 客观0 普通质量-0.15(自建自判,金标无外部把关) |
| p08_calibration | 0.85 | **0.85** | 客观 | 普通 | 客观0 普通质量-0.15(自建自判,金标无外部把关) |
| pedagogy_benchmark | 0.8 | **1.0** ◀ | 客观 | 高质量 | 客观0 高质量0 |
| sas_bench | 0.9(override: CCS step scoring consistency=0.95, ECS error-cause consistency=1.0) | **1.0** ◀ | 客观 | 高质量 | 客观0 高质量0 |
| tutorbench | 0.8 | **0.85** ◀ | 裁判 | 高质量 | LLM 裁判-0.15 高质量0 |

所有 per-subdimension override 并入基准级规则值;唯一保留 `edubench · error_identification_correction_accuracy` = **0.3**。**普通质量共 8 个,全部是本仓自建**:mooccube_prereq、p07_selfcheck、p08_calibration、p08_abstention、longtutor 三件、eduillustrate。

## 判分路径核查(2026-07-19,逐适配器读代码 + 实测占比)

置信度的判分因子必须按**实际判分路径**归类,不能按 benchmark 名义描述。全部 36 个基准逐一核过源码(`scripts/eval/benchmarks/*.py` 的 `extract_answer` / `score`,含基类继承与辅助方法),结论如下。

**判据**:LLM 参与"这答得对不对/好不好"的判断 → 裁判档;LLM 只把答案从啰嗦回复里抠出来、由规则比对金标 → 客观档。

### 结论一:没有 benchmark 在自己的多个取分维度间路径不一致

逐个核过的多维度基准:sas_bench 三指标(QWK/CCS/ECS)同出一份结构化 JSON、规则解析后与人工金标算统计量,全客观;k12vista 三个子集同一裁判,全裁判;olympiadbench 两维度同一 sympy 判分器;pedagogy_benchmark 两类同一规则;edubench 12 维、mrbench_tutor 5 维、bea2025_tutor 3 维同一裁判流程;eduguard_adversarial 的 ASR 与拒答质量是官方两阶段裁判的第一、二阶段产物。longtutor_evidence 三个子任务也同路径(都是语义等价裁判),此前误归客观已修正。

### 结论二:三个**家族**内部路径不一(已按 benchmark_id 拆开,归类正确,存档备查)

| 家族 | 客观档 0.85 | 裁判档 0.7 |
|---|---|---|
| **mathtutorbench**(9 个 id) | problem_solving / solution_correctness / mistake_location / mistake_correction(数值或标签精确匹配,零 LLM)、socratic(sacrebleu) | pedagogy / pedagogy_hard / scaffolding / scaffolding_hard(`_WinRateBase` 成对胜率裁判) |
| **longtutor**(3 个 id) | diagnosis(标签匹配 macro-F1) | evidence(语义等价裁判)、teaching(rubric 四维裁判) |
| **eduguard / mrbench / bea2025** | sata(官方 RFS 规则)、mrbench_judge、bea2025_judge(与人类金标算一致率,统计量客观) | adversarial(两阶段裁判)、mrbench_tutor、bea2025_tutor(固定裁判标注) |

这三族恰好是最容易弄错的:同一个数据集/论文出来,一半规则判、一半裁判判。当前映射里它们已经是独立 benchmark_id,置信度各归各档,**无需拆分**。

### 结论三:三个基准 LLM 只做答案提取,判对错仍是规则 → 留在客观档

| benchmark | LLM 提取的触发条件 | 实测触发占比 |
|---|---|---|
| eduguard_sata | 回复 >64 字符时(短回复走官方正则) | 0.0–0.4%(10 个模型面) |
| mmlu_pro | 官方 `answer is (X)` 正则失配时兜底 | 0.1–2.4%(现行 5 个模型面) |
| mathvista | 恒定走 LLM 抽取(**官方协议如此**) | 100%,但比对由 `normalize_extracted_answer` + 最近选项编辑距离做 |

三者提取后的对错判定全部是规则比对金标,故归客观。与 longtutor_evidence 的区别在于:那里的 LLM 输出的就是 CORRECT/INCORRECT 本身。


## P01 指令与约束遵循

P 分影响(发布面板):M3 8.74→8.74(+0.00) · M2.7 9.11→9.11(+0.00) · dsv4p 9.22→9.22(+0.00) · glm5.2 9.30→9.30(+0.00) · doubao 8.95→8.95(+0.00)

### core 指令与约束遵循

| benchmark · 取分维度 | 相关度 | 置信度 | 有效权重 | 相关度处理 | 置信依据 |
|---|---|---|---|---|---|
| ifeval · prompt-level strict accuracy | 1.0 | 0.8→**1.0** | 0.8→1 | 不变 | 客观0 高质量0 |


## P02 长上下文与证据定位

P 分影响(发布面板):M3 7.85→7.84(-0.01) · M2.7 7.18→7.19(+0.01) · dsv4p 7.87→7.87(-0.01) · glm5.2 8.04→8.03(-0.01) · doubao 7.20→7.22(+0.02)

### core 长上下文与证据定位

| benchmark · 取分维度 | 相关度 | 置信度 | 有效权重 | 相关度处理 | 置信依据 |
|---|---|---|---|---|---|
| longtutor_evidence · Information Extraction accuracy | 0.7→**0.8** | 0.75→**0.7** | 0.525→0.56 | 机械 | LLM 裁判-0.15 普通质量-0.15(自建自判,金标无外部把关) |
| longtutor_evidence · Multi-session Reasoning accuracy | 0.7→**0.8** | 0.75→**0.7** | 0.525→0.56 | 机械 | LLM 裁判-0.15 普通质量-0.15(自建自判,金标无外部把关) |
| longtutor_evidence · Hallucination Check accuracy | 0.7→**0.8** | 0.75→**0.7** | 0.525→0.56 | 机械 | LLM 裁判-0.15 普通质量-0.15(自建自判,金标无外部把关) |
| sas_bench · CCS step scoring consistency | 0.15→**0.2** | 0.95→**1.0** | 0.142→0.2 | 机械 | 客观0 高质量0 |
| mathtutorbench_mistake_location · Mistake Location | 0.15→**0.2** | 1.0 | 0.15→0.2 | 机械 | 客观0 高质量0 |


## P03 多模态理解

P 分影响(发布面板):M3 6.52→6.51(-0.01) · M2.7 5.08→5.08(+0.00) · dsv4p 5.08→5.08(+0.00) · glm5.2 5.08→5.08(+0.00) · doubao 7.18→7.12(-0.06)

### problem_images 解题图像

| benchmark · 取分维度 | 相关度 | 置信度 | 有效权重 | 相关度处理 | 置信依据 |
|---|---|---|---|---|---|
| mathvista · task/question_type/answer_type accuracy | 0.35→**0.5** | 0.7→**1.0** | 0.245→0.5 | **裁决**:读图是分数主成分(区别于盲测证伪的 olympiadbench 格),混数学推理方差,正是 0.5 定义 | 客观0 高质量0 |
| olympiadbench · multimodal-subset accuracy | 0.1→**0.2** | 0.7→**1.0** | 0.07→0.2 | 机械 | 客观0 高质量0 |
| k12vista · math problem-figure subset score | 0.35→**0.5** | 0.8→**0.85** | 0.28→0.425 | **裁决**:同 mathvista:解题必须读图,视觉理解是主成分 | LLM 裁判-0.15 高质量0 |

### subject_charts 学科图表

| benchmark · 取分维度 | 相关度 | 置信度 | 有效权重 | 相关度处理 | 置信依据 |
|---|---|---|---|---|---|
| k12vista · science/geo subject-chart subset score | 0.55→**0.5** | 0.8→**0.85** | 0.44→0.425 | 机械 | LLM 裁判-0.15 高质量0 |

### mixed_materials 图文混排材料

| benchmark · 取分维度 | 相关度 | 置信度 | 有效权重 | 相关度处理 | 置信依据 |
|---|---|---|---|---|---|
| tutorbench · Fair815 multimodal tutor quality | 0.25→**0.2** | 0.8→**0.85** | 0.2→0.17 | 机械 | LLM 裁判-0.15 高质量0 |
| mmtutorbench · multimodal tutor score | 0.3→**0.2** | 0.9→**0.85** | 0.27→0.17 | 机械 | LLM 裁判-0.15 高质量0 |


## P04 多模态生成

P 分影响(发布面板):M3 6.35→6.35(+0.00) · M2.7 6.35→6.35(+0.00) · dsv4p 6.35→6.35(+0.00) · glm5.2 6.35→6.35(+0.00) · doubao 7.41→7.41(+0.00)

### static_visual 图示与示意图生成

| benchmark · 取分维度 | 相关度 | 置信度 | 有效权重 | 相关度处理 | 置信依据 |
|---|---|---|---|---|---|
| eduillustrate · 8-dim 0-5 visual explanation score | 0.45→**0.5** | 0.85→**0.7** | 0.383→0.35 | 机械 | LLM 裁判-0.15 普通质量-0.15(自建自判,金标无外部把关) |


## P05 知识调用与掌握

P 分影响(发布面板):M3 7.69→7.68(-0.01) · M2.7 7.29→7.38(+0.09) · dsv4p 8.07→8.10(+0.03) · glm5.2 7.95→7.82(-0.12) · doubao 7.97→7.95(-0.02)

### subject_knowledge 学科知识调用

| benchmark · 取分维度 | 相关度 | 置信度 | 有效权重 | 相关度处理 | 置信依据 |
|---|---|---|---|---|---|
| mmlu_pro · overall/category accuracy | 0.6→**0.5** | 0.7→**1.0** | 0.42→0.5 | 机械 | 客观0 高质量0 |
| ceval · overall/category/subject accuracy | 0.6→**0.5** | 0.7→**1.0** | 0.42→0.5 | 机械 | 客观0 高质量0 |
| agieval · overall/task/language/question_type accuracy | 0.35→**0.2** | 0.7→**1.0** | 0.245→0.2 | 机械 | 客观0 高质量0 |
| mathtutorbench_problem_solving · Problem Solving | 0.3→**0.2** | 0.45→**1.0** | 0.135→0.2 | 机械 | 客观0 高质量0 |
| olympiadbench · overall/subject/language/modality accuracy | 0.25→**0.2** | 0.7→**1.0** | 0.175→0.2 | 机械 | 客观0 高质量0 |
| mathvista · task/question_type/answer_type accuracy | 0.2 | 0.7→**1.0** | 0.14→0.2 | 不变 | 客观0 高质量0 |
| k12vista · official partial-credit score (per-blank 0/1 mean) | 0.15→**0.2** | 0.8→**0.85** | 0.12→0.17 | 机械 | LLM 裁判-0.15 高质量0 |
| edubench · domain_knowledge_accuracy (metric) | 0.35→**0.2** | 0.8→**0.85** | 0.28→0.17 | 机械 | LLM 裁判-0.15 高质量0 |
| edubench · basic_factual_accuracy (metric) | 0.3→**0.2** | 0.8→**0.85** | 0.24→0.17 | 机械 | LLM 裁判-0.15 高质量0 |
| sas_bench · ECS error-cause consistency | 0.2 | 1.0 | 0.2 | 不变 | 客观0 高质量0 |

### pedagogical_knowledge 教学专业知识

| benchmark · 取分维度 | 相关度 | 置信度 | 有效权重 | 相关度处理 | 置信依据 |
|---|---|---|---|---|---|
| pedagogy_benchmark · CDPK teaching knowledge selection | 0.45→**0.5** | 0.8→**1.0** | 0.36→0.5 | 机械 | 客观0 高质量0 |
| pedagogy_benchmark · SEND special education needs selection | 0.35→**0.5** | 0.8→**1.0** | 0.28→0.5 | **裁决**:特教知识选择题是本 facet 直接测量(子领域偏窄),不应与胜率代理格同档 | 客观0 高质量0 |
| mathtutorbench_pedagogy · Pedagogy IF | 0.25→**0.2** | 0.95→**0.85** | 0.237→0.17 | 机械 | LLM 裁判-0.15 高质量0 |
| mathtutorbench_pedagogy_hard · Pedagogy IF hard | 0.25→**0.2** | 1.0→**0.85** | 0.25→0.17 | 机械 | LLM 裁判-0.15 高质量0 |
| mathtutorbench_scaffolding · Scaffolding | 0.15→**0.2** | 1.0→**0.85** | 0.15→0.17 | 机械 | LLM 裁判-0.15 高质量0 |
| mathtutorbench_scaffolding_hard · Scaffolding hard | 0.15→**0.2** | 1.0→**0.85** | 0.15→0.17 | 机械 | LLM 裁判-0.15 高质量0 |


## P06 推理与生成

P 分影响(发布面板):M3 8.23→8.27(+0.04) · M2.7 8.12→8.09(-0.03) · dsv4p 8.23→8.21(-0.03) · glm5.2 8.73→8.61(-0.12) · doubao 8.38→8.39(+0.02)

### problem_reasoning 解题推理

| benchmark · 取分维度 | 相关度 | 置信度 | 有效权重 | 相关度处理 | 置信依据 |
|---|---|---|---|---|---|
| mathtutorbench_problem_solving · Problem Solving | 0.6→**0.5** | 0.45→**1.0** | 0.27→0.5 | 机械 | 客观0 高质量0 |
| olympiadbench · overall/subject/language/modality accuracy | 0.55→**0.5** | 0.7→**1.0** | 0.385→0.5 | 机械 | 客观0 高质量0 |
| agieval · overall/task/language/question_type accuracy | 0.45→**0.5** | 0.7→**1.0** | 0.315→0.5 | 机械 | 客观0 高质量0 |
| mathvista · task/question_type/answer_type accuracy | 0.45→**0.5** | 0.7→**1.0** | 0.315→0.5 | 机械 | 客观0 高质量0 |
| mmlu_pro · overall/category accuracy | 0.3→**0.2** | 0.7→**1.0** | 0.21→0.2 | 机械 | 客观0 高质量0 |
| k12vista · official partial-credit score (per-blank 0/1 mean) | 0.3→**0.2** | 0.8→**0.85** | 0.24→0.17 | 机械 | LLM 裁判-0.15 高质量0 |
| ceval · overall/category/subject accuracy | 0.25→**0.2** | 0.7→**1.0** | 0.175→0.2 | 机械 | 客观0 高质量0 |

### generative_reasoning 生成与归因推理

| benchmark · 取分维度 | 相关度 | 置信度 | 有效权重 | 相关度处理 | 置信依据 |
|---|---|---|---|---|---|
| edubench · reasoning_process_rigor (metric) | 0.35→**0.5** | 0.8→**0.85** | 0.28→0.425 | **裁决**:裁判逐题标"推理过程严谨",指标名即构念;保持 facet 首格地位 | LLM 裁判-0.15 高质量0 |
| edubench · higher_order_thinking_ability_development (metric) | 0.2 | 0.8→**0.85** | 0.16→0.17 | 不变 | LLM 裁判-0.15 高质量0 |
| mathtutorbench_mistake_correction · Mistake Correction | 0.2 | 0.9→**1.0** | 0.18→0.2 | 不变 | 客观0 高质量0 |
| sas_bench · ECS error-cause consistency | 0.1→**0.2** | 1.0 | 0.1→0.2 | 机械 | 客观0 高质量0 |


## P07 自我校验与修正

P 分影响(发布面板):M3 6.11→6.11(+0.00) · M2.7 5.87→5.87(-0.00) · dsv4p 6.34→6.34(+0.00) · glm5.2 6.30→6.30(+0.00) · doubao 5.97→5.98(+0.01)

### core 自我校验与修正

| benchmark · 取分维度 | 相关度 | 置信度 | 有效权重 | 相关度处理 | 置信依据 |
|---|---|---|---|---|---|
| p07_selfcheck · two-round self-check (fix/break rate) | 0.85→**0.8** | 0.85 | 0.722→0.68 | 机械 | 客观0 普通质量-0.15(自建自判,金标无外部把关) |
| mathtutorbench_solution_correctness · Solution Correctness | 0.25→**0.2** | 0.85→**1.0** | 0.212→0.2 | 机械 | 客观0 高质量0 |
| p08_calibration · calibration composite (CWR/AUROC) | 0.2 | 0.85 | 0.17 | 不变 | 客观0 普通质量-0.15(自建自判,金标无外部把关) |


## P08 置信度校准与弃答

P 分影响(发布面板):M3 7.54→7.51(-0.03) · M2.7 7.06→7.05(-0.01) · dsv4p 7.81→7.78(-0.02) · glm5.2 7.76→7.73(-0.02) · doubao 7.73→7.69(-0.04)

### calibration 置信度校准

| benchmark · 取分维度 | 相关度 | 置信度 | 有效权重 | 相关度处理 | 置信依据 |
|---|---|---|---|---|---|
| p08_calibration · calibration composite (CWR/AUROC) | 0.8 | 0.85 | 0.68 | 不变 | 客观0 普通质量-0.15(自建自判,金标无外部把关) |
| p07_selfcheck · two-round self-check (fix/break rate) | 0.15→**0.2** | 0.85 | 0.128→0.17 | 机械 | 客观0 普通质量-0.15(自建自判,金标无外部把关) |

### abstention 能力性弃答

| benchmark · 取分维度 | 相关度 | 置信度 | 有效权重 | 相关度处理 | 置信依据 |
|---|---|---|---|---|---|
| p08_abstention · balanced abstention score | 0.85→**0.8** | 0.85 | 0.722→0.68 | 机械 | 客观0 普通质量-0.15(自建自判,金标无外部把关) |


## P09 工具使用与长程智能体执行

(空 P,无格子,零改动)


## P10 错误诊断

P 分影响(发布面板):M3 7.92→7.80(-0.11) · M2.7 7.56→7.42(-0.14) · dsv4p 7.81→7.69(-0.12) · glm5.2 7.62→7.47(-0.16) · doubao 7.65→7.52(-0.13)

### answer_verdict 作答正误判定

| benchmark · 取分维度 | 相关度 | 置信度 | 有效权重 | 相关度处理 | 置信依据 |
|---|---|---|---|---|---|
| mathtutorbench_solution_correctness · Solution Correctness | 0.6→**0.5** | 0.85→**1.0** | 0.51→0.5 | 机械 | 客观0 高质量0 |

### error_location 错误位置定位

| benchmark · 取分维度 | 相关度 | 置信度 | 有效权重 | 相关度处理 | 置信依据 |
|---|---|---|---|---|---|
| mathtutorbench_mistake_location · Mistake Location | 0.7→**0.8** | 1.0 | 0.7→0.8 | 机械 | 客观0 高质量0 |
| sas_bench · CCS step scoring consistency | 0.25→**0.2** | 0.95→**1.0** | 0.237→0.2 | 机械 | 客观0 高质量0 |

### error_attribution 错因归因

| benchmark · 取分维度 | 相关度 | 置信度 | 有效权重 | 相关度处理 | 置信依据 |
|---|---|---|---|---|---|
| sas_bench · ECS error-cause consistency | 0.7→**0.8** | 1.0 | 0.7→0.8 | 机械 | 客观0 高质量0 |
| bea2025_tutor · dimension: Mistake_Identification | 0.25→**0.2** | 0.9→**0.85** | 0.225→0.17 | 机械 | LLM 裁判-0.15 高质量0 |
| mrbench_tutor · dimension: Mistake_Identification | 0.25→**0.2** | 0.8→**0.85** | 0.2→0.17 | 机械 | LLM 裁判-0.15 高质量0 |
| edubench · error_identification_correction_accuracy (metric) | 0.25→**0.2** | 0.3 | 0.075→0.06 | 机械 | 唯一例外(R23 裁决):换裁判 ρ≤0.14 全仓最实锤噪声格,维持 0.3 |
| mathtutorbench_mistake_correction · Mistake Correction | 0.2 | 0.9→**1.0** | 0.18→0.2 | 不变 | 客观0 高质量0 |
| longtutor_diagnosis · four-category knowledge-state diagnosis macro-F1 | 0.1→**0.2** | 0.75→**0.85** | 0.075→0.17 | 机械 | 客观0 普通质量-0.15(自建自判,金标无外部把关) |


## P11 主观题评价能力

P 分影响(发布面板):M3 6.49→6.27(-0.22) · M2.7 6.43→6.27(-0.16) · dsv4p 6.59→6.40(-0.19) · glm5.2 6.66→6.45(-0.21) · doubao 6.08→5.80(-0.27)

### holistic_scoring 整体性评分

| benchmark · 取分维度 | 相关度 | 置信度 | 有效权重 | 相关度处理 | 置信依据 |
|---|---|---|---|---|---|
| sas_bench · QWK holistic total score | 0.7→**0.8** | 0.9→**1.0** | 0.63→0.8 | 机械 | 客观0 高质量0 |
| asap_2 · essay holistic QWK | 0.65→**0.8** | 0.8→**1.0** | 0.52→0.8 | **裁决**:与 sas_bench QWK(机械已到 0.8)同一操作换语料,同构念同档 | 客观0 高质量0 |

### analytic_scoring 分析式与多维度评分

| benchmark · 取分维度 | 相关度 | 置信度 | 有效权重 | 相关度处理 | 置信依据 |
|---|---|---|---|---|---|
| sas_bench · CCS step scoring consistency | 0.55→**0.5** | 0.95→**1.0** | 0.522→0.5 | 机械 | 客观0 高质量0 |
| bea2025_judge · judge labels: mistake/guidance/actionability | 0.45→**0.5** | 0.75→**1.0** | 0.338→0.5 | 机械 | 客观0 高质量0 |
| mrbench_judge · 8-dimension tutor response judging | 0.45→**0.5** | 0.75→**1.0** | 0.338→0.5 | 机械 | 客观0 高质量0 |


## P12 命题与作业设计

P 分影响(发布面板):M3 8.64→8.41(-0.23) · M2.7 9.06→9.00(-0.06) · dsv4p 8.50→8.45(-0.05) · glm5.2 8.93→8.70(-0.23) · doubao 8.47→8.23(-0.24)

### item_generation 题目生成（正确性与质量）

| benchmark · 取分维度 | 相关度 | 置信度 | 有效权重 | 相关度处理 | 置信依据 |
|---|---|---|---|---|---|
| edubench · QG × clarity_concision_inspiration + scenario_element_integration (task×metric) | 0.4→**0.5** | 0.75→**0.85** | 0.3→0.425 | 机械 | LLM 裁判-0.15 高质量0 |
| edubench · QG × domain_knowledge_accuracy + basic_factual_accuracy (task×metric) | 0.3→**0.2** | 0.75→**0.85** | 0.225→0.17 | 机械 | LLM 裁判-0.15 高质量0 |


## P13 学习者画像建模

P 分影响(发布面板):M3 5.06→5.14(+0.08) · M2.7 4.55→4.58(+0.04) · dsv4p 5.17→5.24(+0.07) · glm5.2 4.54→4.53(-0.01) · doubao 4.61→4.68(+0.08)

### knowledge_state_estimation 知识状态估计

| benchmark · 取分维度 | 相关度 | 置信度 | 有效权重 | 相关度处理 | 置信依据 |
|---|---|---|---|---|---|
| longtutor_diagnosis · four-category knowledge-state diagnosis macro-F1 | 0.3→**0.8** | 0.75→**0.85** | 0.225→0.68 | **裁决**:从历史推断知识状态就是 facet 构念本身(范围窄:数学辅导、四分类);金标非盲标疑虑留注记。单格 facet 不影响分数 | 客观0 普通质量-0.15(自建自判,金标无外部把关) |

### support_needs 支持需求判断

| benchmark · 取分维度 | 相关度 | 置信度 | 有效权重 | 相关度处理 | 置信依据 |
|---|---|---|---|---|---|
| pedagogy_benchmark · SEND special education needs selection | 0.25→**0.2** | 0.8→**1.0** | 0.2 | 机械 | 客观0 高质量0 |
| edubench · personalized_adaptation_learning_support (metric) | 0.3→**0.2** | 0.8→**0.85** | 0.24→0.17 | 机械 | LLM 裁判-0.15 高质量0 |


## P14 个性化教学策略选择

P 分影响(发布面板):M3 7.02→6.90(-0.12) · M2.7 6.61→6.51(-0.10) · dsv4p 7.48→7.33(-0.15) · glm5.2 6.90→6.74(-0.16) · doubao 7.37→7.23(-0.14)

### strategy_formulation 教学策略制定

| benchmark · 取分维度 | 相关度 | 置信度 | 有效权重 | 相关度处理 | 置信依据 |
|---|---|---|---|---|---|
| pedagogy_benchmark · CDPK teaching knowledge selection | 0.6→**0.8** | 0.8→**1.0** | 0.48→0.8 | **裁决**:R23 原话"本 facet 构念最贴的直接测量"即强相关定义;保 CDPK>SEND 排序 | 客观0 高质量0 |
| pedagogy_benchmark · SEND special education needs selection | 0.4→**0.5** | 0.8→**1.0** | 0.32→0.5 | 机械 | 客观0 高质量0 |

### strategy_enactment 教学策略执行

| benchmark · 取分维度 | 相关度 | 置信度 | 有效权重 | 相关度处理 | 置信依据 |
|---|---|---|---|---|---|
| mathtutorbench_socratic · Socratic Questioning | 0.4→**0.5** | 0.6→**1.0** | 0.24→0.5 | 机械 | 客观0 高质量0 |
| mathtutorbench_scaffolding · Scaffolding | 0.5 | 1.0→**0.85** | 0.5→0.425 | 不变 | LLM 裁判-0.15 高质量0 |
| mathtutorbench_scaffolding_hard · Scaffolding hard | 0.5 | 1.0→**0.85** | 0.5→0.425 | 不变 | LLM 裁判-0.15 高质量0 |
| mathtutorbench_pedagogy · Pedagogy IF | 0.45→**0.5** | 0.95→**0.85** | 0.427→0.425 | 机械 | LLM 裁判-0.15 高质量0 |
| mathtutorbench_pedagogy_hard · Pedagogy IF hard | 0.45→**0.5** | 1.0→**0.85** | 0.45→0.425 | 机械 | LLM 裁判-0.15 高质量0 |
| edubench · personalized_adaptation_learning_support (metric) | 0.4→**0.5** | 0.8→**0.85** | 0.32→0.425 | 机械 | LLM 裁判-0.15 高质量0 |
| tutorbench · Fair815 multimodal tutor quality | 0.35→**0.2** | 0.8→**0.85** | 0.28→0.17 | 机械 | LLM 裁判-0.15 高质量0 |
| bea2025_tutor · dimension: Providing_Guidance | 0.3→**0.2** | 0.9→**0.85** | 0.27→0.17 | 机械 | LLM 裁判-0.15 高质量0 |
| mrbench_tutor · dimension: Providing_Guidance | 0.3→**0.2** | 0.8→**0.85** | 0.24→0.17 | 机械 | LLM 裁判-0.15 高质量0 |
| mmtutorbench · multimodal tutor score | 0.3→**0.2** | 0.9→**0.85** | 0.27→0.17 | 机械 | LLM 裁判-0.15 高质量0 |
| longtutor_teaching · judge dims: strategy_alignment + history_utilization (1-5) | 0.3→**0.2** | 0.75→**0.7** | 0.225→0.14 | 机械 | LLM 裁判-0.15 普通质量-0.15(自建自判,金标无外部把关) |
| edubench · scenario_element_integration (metric) | 0.25→**0.2** | 0.8→**0.85** | 0.2→0.17 | 机械 | LLM 裁判-0.15 高质量0 |


## P15 学习路径规划（知识结构层）

P 分影响(发布面板):M3 4.45→4.45(+0.00) · M2.7 4.76→4.76(-0.00) · dsv4p 3.79→3.79(+0.00) · glm5.2 3.91→3.91(+0.00) · doubao 4.49→4.49(+0.00)

### core 知识结构层路径规划

| benchmark · 取分维度 | 相关度 | 置信度 | 有效权重 | 相关度处理 | 置信依据 |
|---|---|---|---|---|---|
| mooccube_prereq · chance-corrected composite (先修选择 + 学习顺序排序) | 0.7→**0.8** | 0.7→**0.85** | 0.49→0.68 | 机械 | 客观0 普通质量-0.15(自建自判,金标无外部把关) |


## P16 适配性解释与反馈生成

P 分影响(发布面板):M3 7.13→7.15(+0.02) · M2.7 6.96→7.03(+0.08) · dsv4p 7.17→7.12(-0.05) · glm5.2 7.67→7.64(-0.03) · doubao 7.45→7.44(-0.01)

### content_feedback 内容性讲解与纠错反馈

| benchmark · 取分维度 | 相关度 | 置信度 | 有效权重 | 相关度处理 | 置信依据 |
|---|---|---|---|---|---|
| tutorbench · Fair815 multimodal tutor quality | 0.4→**0.5** | 0.8→**0.85** | 0.32→0.425 | 机械 | LLM 裁判-0.15 高质量0 |
| mmtutorbench · multimodal tutor score | 0.4→**0.5** | 0.9→**0.85** | 0.36→0.425 | 机械 | LLM 裁判-0.15 高质量0 |
| mathtutorbench_mistake_correction · Mistake Correction | 0.35→**0.2** | 0.9→**1.0** | 0.315→0.2 | 机械 | 客观0 高质量0 |
| mathtutorbench_scaffolding · Scaffolding | 0.35→**0.2** | 1.0→**0.85** | 0.35→0.17 | 机械 | LLM 裁判-0.15 高质量0 |
| mathtutorbench_scaffolding_hard · Scaffolding hard | 0.35→**0.2** | 1.0→**0.85** | 0.35→0.17 | 机械 | LLM 裁判-0.15 高质量0 |
| mathtutorbench_socratic · Socratic Questioning | 0.35→**0.2** | 0.6→**1.0** | 0.21→0.2 | 机械 | 客观0 高质量0 |
| edubench · clarity_concision_inspiration (metric) | 0.3→**0.2** | 0.8→**0.85** | 0.24→0.17 | 机械 | LLM 裁判-0.15 高质量0 |
| mathtutorbench_pedagogy · Pedagogy IF | 0.3→**0.2** | 0.95→**0.85** | 0.285→0.17 | 机械 | LLM 裁判-0.15 高质量0 |
| mathtutorbench_pedagogy_hard · Pedagogy IF hard | 0.3→**0.2** | 1.0→**0.85** | 0.3→0.17 | 机械 | LLM 裁判-0.15 高质量0 |
| edubench · higher_order_thinking_ability_development (metric) | 0.25→**0.2** | 0.8→**0.85** | 0.2→0.17 | 机械 | LLM 裁判-0.15 高质量0 |
| bea2025_tutor · dimension: Actionability | 0.2 | 0.9→**0.85** | 0.18→0.17 | 不变 | LLM 裁判-0.15 高质量0 |
| mrbench_tutor · dimension: Actionability | 0.2 | 0.8→**0.85** | 0.16→0.17 | 不变 | LLM 裁判-0.15 高质量0 |

### tone_support 语气、情感与动机支持

| benchmark · 取分维度 | 相关度 | 置信度 | 有效权重 | 相关度处理 | 置信依据 |
|---|---|---|---|---|---|
| edubench · motivation_guidance_positive_feedback (metric) | 0.35→**0.5** | 0.8→**0.85** | 0.28→0.425 | **裁决**:指标名即构念,且属 judge-swap 验证的裁判鲁棒簇;机械 0.2 会抹掉与鼓励占比格的排序 | LLM 裁判-0.15 高质量0 |
| mrbench_tutor · dimension: Tutor_Tone (encouraging share) | 0.2 | 0.8→**0.85** | 0.16→0.17 | 不变 | LLM 裁判-0.15 高质量0 |

### artifact_generation 教学产物生成

| benchmark · 取分维度 | 相关度 | 置信度 | 有效权重 | 相关度处理 | 置信依据 |
|---|---|---|---|---|---|
| edubench · TMG/PCC × clarity_concision_inspiration + scenario_element_integration (task×metric) | 0.55→**0.5** | 0.75→**0.85** | 0.413→0.425 | 机械 | LLM 裁判-0.15 高质量0 |
| eduillustrate · 8-dim 0-5 visual explanation score | 0.25→**0.2** | 0.85→**0.7** | 0.212→0.14 | 机械 | LLM 裁判-0.15 普通质量-0.15(自建自判,金标无外部把关) |


## P17 教育角色边界判断

P 分影响(发布面板):M3 8.39→8.43(+0.03) · M2.7 5.95→6.14(+0.19) · dsv4p 6.33→6.51(+0.18) · glm5.2 7.30→7.41(+0.11) · doubao 6.56→6.73(+0.17)

### safety_knowledge 安全知识

| benchmark · 取分维度 | 相关度 | 置信度 | 有效权重 | 相关度处理 | 置信依据 |
|---|---|---|---|---|---|
| eduguard_sata · Teaching Harm / SATA RFS | 0.35→**0.2** | 1.0 | 0.35→0.2 | 机械 | 客观0 高质量0 |

### boundary_behavior 边界行为

| benchmark · 取分维度 | 相关度 | 置信度 | 有效权重 | 相关度处理 | 置信依据 |
|---|---|---|---|---|---|
| eduguard_adversarial · Adversarial Safety ASR | 0.3→**0.5** | 1.0→**0.85** | 0.3→0.425 | **裁决**:对抗压力下守边界的直接测量;恢复对哨兵格的主导,消除机械迁移最大失真 | LLM 裁判-0.15 高质量0 |
| mrbench_tutor · dimension: Tutor_Tone (non-offensive) | 0.1→**0.2** | 0.8→**0.85** | 0.08→0.17 | 机械 | LLM 裁判-0.15 高质量0 |
| eduguard_adversarial · Refusal quality distribution | 0.15→**0.2** | 0.8→**0.85** | 0.12→0.17 | 机械 | LLM 裁判-0.15 高质量0 |


## P18 学生风险识别

P 分影响(发布面板):M3 7.69→7.69(+0.00) · M2.7 6.93→6.93(+0.00) · dsv4p 7.61→7.61(+0.00) · glm5.2 7.59→7.60(+0.00) · doubao 7.62→7.62(+0.00)

### risk_signal_recognition 风险信号识别

| benchmark · 取分维度 | 相关度 | 置信度 | 有效权重 | 相关度处理 | 置信依据 |
|---|---|---|---|---|---|
| eduguard_sata · Teaching Harm / SATA RFS | 0.3→**0.2** | 1.0 | 0.3→0.2 | 机械 | 客观0 高质量0 |


## P19 安全处置选择

P 分影响(发布面板):M3 8.21→8.16(-0.04) · M2.7 5.57→5.61(+0.04) · dsv4p 5.99→6.05(+0.06) · glm5.2 6.72→6.60(-0.13) · doubao 6.40→6.52(+0.12)

### safety_knowledge 安全知识

| benchmark · 取分维度 | 相关度 | 置信度 | 有效权重 | 相关度处理 | 置信依据 |
|---|---|---|---|---|---|
| eduguard_sata · Teaching Harm / SATA RFS | 0.35→**0.2** | 1.0 | 0.35→0.2 | 机械 | 客观0 高质量0 |

### adversarial_robustness 对抗鲁棒

| benchmark · 取分维度 | 相关度 | 置信度 | 有效权重 | 相关度处理 | 置信依据 |
|---|---|---|---|---|---|
| eduguard_adversarial · Refusal quality distribution | 0.6→**0.8** | 0.8→**0.85** | 0.48→0.68 | **裁决**:rubric 判处置得体是"安全处置选择"构念直接测量;恢复 R7/R23 主格意图 | LLM 裁判-0.15 高质量0 |
| eduguard_adversarial · Adversarial Safety ASR | 0.45→**0.5** | 1.0→**0.85** | 0.45→0.425 | 机械 | LLM 裁判-0.15 高质量0 |


## P20 学术诚信与作答真实性判定

(空 P,无格子,零改动)
