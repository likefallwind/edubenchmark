# 教育 AI 原子能力与 Benchmark 映射(v6 定稿,2026-07-19)

本文档是**当前状态的干净快照**:原子能力清单、每个能力的定义与 facet、映射到哪些 benchmark 的哪些维度、相关度与置信权重多少、测量成熟度如何,以及创新点和未完成事项。不含历史沿革与裁决过程——那些在 `doc/atomic_ability_mapping_final_2026-07-15.md`(裁决记录 R1–R24)里。

机器可读版(单一事实源):`data/mapping_measurement_model_v6.json`。本文档所有表格由该 JSON 与聚合脚本 `BENCHMARK_META` 逐格核对生成(2026-07-19,R24 后),分数区间取自 `reports/atomic_ability_rebenchmark_2026-07-08/09_atomic_p_score_evidence.jsonl`。如有出入以 JSON 为准。

> **⚠️ 编号已两度迁移。** 现行是 **R24 编号**。历史注记里的 P 号有两套旧方案:pre-R20(P01–P23 带墓碑,仍是 JSON 与本仓库各文档 **rationale 正文**里在用的方案,也是 `scripts/build_rebenchmark_conclusion_plan.py` 在用的方案)、R20(文档方案 P01–P20)。**两张对照表在 final 文档的 R20 与 R24 记录里**,R24 那张同时写在 JSON 的 `schema_notes.numbering_R24`。rationale 正文刻意从未机械替换——编号混在散文里,正则必误伤。**benchmark 名 `p07_selfcheck` / `p08_calibration` / `p08_abstention` 沿用 pre-R20 旧号起名,不要按名字推 P 号**(改名重构已列 TODO)。

## 划分规则(先读这个)

**P 级拆分准入**:子能力拆成独立 P,需要四类 benchmark 无关依据(理论框架 / 独立失败机制 / 教师专业标准条目 / 产品失败后果)中的至少两个。**benchmark 的存在永远不构成拆分依据**——"恰好有两个数据集"不等于"是两个构念"。

**facet 级拆分规则(R19)**:①**边界可判**——每个任务有且只有一个归属;开放的场景轴(如"教学交互场景")不合格,因为所有教育活动都能往里塞;②**构念不重复**——两个 facet 不能是同一件事测两遍(判别式 vs 生成式只是测量方式之差,不是两个 facet)。擦边的证据格宁缺勿滥。

**权重命名**(三个概念,前两个是存的,第三个是算出来的,别混):

- **相关度权重**:映射表"相关"列,即 JSON cell 的 `weight`——该 benchmark 指标与这个 facet 构念的贴合程度,按(格子 × facet)定,同一格挂不同 P 可以不同;
- **置信权重**:聚合脚本 `BENCHMARK_META.default_benchmark_weight`,即"置信"列——该 benchmark 本身多可信,按 benchmark 定,与 facet 无关,支持逐取分维度 override;
- **有效权重** = 相关度 × 置信(R20 起就这一个公式,四档证据分层已废除,无门槛因子)。

**聚合规则**:facet 内按有效权重加权平均 → P 分为各 facet 的**等权**平均(有证据的 facet 才进分母,空 facet 不算 0)。formative 声明因此真正落进分数。

**缺测替代(R22)**:发布面板某模型缺某格时,取该格已测面(≥3 个,`IMPUTE_MIN_FACES`)中的**最低分**顶替,标 `imputed`,HTML 报告打 ※。这是"没测不等于好"的保守处理,不是真实测量,读分时必须看替代占比(见第五部分)。

## 一、原子能力清单(20 项)

### 模型基础能力(9 项)——不依赖教育场景就能定义,通用 benchmark 可测

| 编号 | 能力 | 定义 |
|---|---|---|
| P01 | 指令与约束遵循 | 按显式指令和格式/行为约束产出 |
| P02 | 长上下文与证据定位 | 在长材料/长对话中定位并引用相关证据 |
| P03 | 多模态理解 | 读懂教育场景中的图像/图表等非文本材料并据此推理 |
| P04 | 多模态生成 | 产出图示等结构正确、可读、图文对应的非文本材料 |
| P05 | 知识调用与掌握 | 学科知识与教学专业知识的正确调用 |
| P06 | 推理与生成 | 解题推理与约束下的生成推理 |
| P07 | 自我校验与修正 | 复查自己的输出,发现并修正错误 |
| P08 | 置信度校准与弃答 | 自信程度与正确率一致;不会时主动弃答 |
| P09 | 工具使用与长程智能体执行 | 调用工具、完成多步长程任务 |

### 教育领域能力(11 项)——内核带教育专有的知识、构念或政策

| 编号 | 能力 | 定义 |
|---|---|---|
| P10 | 错误诊断 | 判对错、定位错误步骤、解释错因/误概念(三 facet 为诊断深度) |
| P11 | 主观题评价能力 | 依据(或构建)评分标准评判主观作答与教学回复 |
| P12 | 命题与作业设计 | 为学生设计考试/作业题目:出题、难度定标、目标对齐 |
| P13 | 学习者画像建模 | 从交互中建模学生的水平、需求与特征 |
| P14 | 个性化教学策略选择 | 对齐教学目标与学生状态,制定并执行合适的教学策略 |
| P15 | 学习路径规划(知识结构层) | 基于知识先修结构规划学习顺序 |
| P16 | 适配性解释与反馈生成 | 生成适配学生的解释、引导与反馈 |
| P17 | 教育角色边界判断 | 守住教育者的角色与行为边界 |
| P18 | 学生风险识别 | 识别学生消息中的风险信号 |
| P19 | 安全处置选择 | 对风险与越界请求选择正确处置方式 |
| P20 | 学术诚信与作答真实性判定 | 识别抄袭、代写等真实性问题 |

大类划分(展示层,不进测量模型)见 `doc/atomic_ability_category_grouping_2026-07-16.md`。

### 边界口径

- **P03 / P04**:一对读/写。P03 把图看懂,P04 把图产出来。P04 于 R23 由"多模态教学产物生成"改制而来并移入基础组——原定义与 P16 的产物 facet 是同一构念被按模态切开,导致 eduillustrate 双挂重复计分。
- **P10 / P11**:P10 是对着参考解找错、解释错(诊断);P11 是把作答证据映射到 rubric 分档(量尺映射),机制不同。
- **P11 / P12**:涉及评分标准(造或用)归 P11,P12 只管题目。
- **P14 / P16**:P14 评"选了什么教学策略",P16 评"把解释、反馈和支持表达得怎样"。
- **P13 / P10c**:P10c 错因归因是**从当前作答**解释这次错在哪;P13a 知识状态估计是**从交互历史**判断学生整体会什么不会什么。
- **P05 与 P06/P17**:P05 第三个 facet"生成中的知识运用"已于 R19 砍除——判别式答题与生成式运用是同一构念的两种测量方式;与 P17 的知/行两 facet 的区别在于后者的行为侧有独立失败机制(对抗操纵),生成侧挑不出知识调用之外的新机制。

## 二、逐能力映射明细

分数区间为已测模型面的 score_10 跨度;"面"列为证据行数,括号内为替代值行数。

### P01 指令与约束遵循(单 facet,单源直接测量)

| facet | benchmark · 取分维度 | 相关 | 置信 | 有效 | 分数 | 面 |
|---|---|---|---|---|---|---|
| 核心 | ifeval · prompt-level strict accuracy | 1.0 | 0.8 | 0.80 | 8.74–9.30 | 5 |

R20 摘除全部搭车格:选择题的"格式遵循"实际取分是 accuracy(污染),弃答约束遵循无可分离的指令遵循信号。

### P02 长上下文与证据定位(单 facet,R21 三拆)

| facet | benchmark · 取分维度 | 相关 | 置信 | 有效 | 分数 | 面 |
|---|---|---|---|---|---|---|
| 核心 | longtutor_evidence · Information Extraction accuracy | 0.7 | 0.75 | 0.525 | 9.32–9.69 | 5(1) |
| | longtutor_evidence · Multi-session Reasoning accuracy | 0.7 | 0.75 | 0.525 | 5.96–7.01 | 5(1) |
| | longtutor_evidence · Hallucination Check accuracy | 0.7 | 0.75 | 0.525 | 6.08–7.52 | 5(1) |
| | mathtutorbench_mistake_location · Mistake Location | 0.15 | 1.0 | 0.15 | 7.65–7.92 | 6(1) |
| | sas_bench · CCS step scoring consistency | 0.15 | 0.95 | 0.143 | 7.25–8.03 | 8 |

R21:longtutor 按 `memory_type` 拆三格等权——单记录提取近天花板,跨 session 推理与幻觉检查才有区分度,合成一个总分会稀释掉后两者。同批摘除三个无可分离定位信号的搭车格(asap_2 QWK、sas_bench QWK、solution_correctness):整体打分里观测不到"定位过证据",那是评分一致性方差冒充 P02 证据。保留的两格定位行为为真但材料不长,相关度压到 0.15。

### P03 多模态理解(4 facet,按材料的内容构成)

| facet | benchmark · 取分维度 | 相关 | 置信 | 有效 | 分数 | 面 |
|---|---|---|---|---|---|---|
| 解题图像 | mathvista · task/question_type/answer_type accuracy | 0.35 | 0.7 | 0.245 | 8.41 | 1 |
| | k12vista · math problem-figure subset score | 0.35 | 0.8 | 0.28 | 7.34–7.74 | 2 |
| | olympiadbench · multimodal-subset accuracy | 0.1 | 0.7 | 0.07 | 6.81 | 1 |
| 学科图表 | k12vista · science/geo subject-chart subset score | 0.55 | 0.8 | 0.44 | 6.26–7.28 | 2 |
| 图文混排材料 | mmtutorbench · multimodal tutor score | 0.3 | 0.9 | 0.27 | 5.74–7.60 | 2 |
| | tutorbench · Fair815 multimodal tutor quality | 0.25 | 0.8 | 0.20 | 5.08–5.76 | 10(4) |
| 视频/音频 | —— 空白 —— | | | | | |

facet 轴统一为"内容构成"单轴(材料本身长什么样),不掺场景/任务标签——按场景定义边界不可判。渲染 vs 拍摄不影响归属(只是清晰度噪声)。

R22 两处修订:①olympiadbench 只进多模态子集且相关度压到 0.1——**盲测对照**发现看不见图的 deepseek-v4-pro 在该子集拿 0.658,几乎等于明眼的 M3 的 0.681,说明题干文本自带足够信息,多模态成分被污染;`BLIND_VISION_MODELS` 同时排除该模型的多模态格。②k12vista 按学科拆两格,数学图进解题图像、理化生地图表进学科图表。

### P04 多模态生成(2 facet,R23 改制并移入基础组)

| facet | benchmark · 取分维度 | 相关 | 置信 | 有效 | 分数 | 面 |
|---|---|---|---|---|---|---|
| 图示与示意图生成 | eduillustrate · 8-dim 0-5 visual explanation score | 0.45 | 0.85 | 0.383 | 6.35–7.41 | 7(3) |
| 时序与交互产物生成 | —— 空白 —— | | | | | |

eduillustrate 的 8 维 = 文本侧(正确性/逻辑/易懂/图文协同)+ 视觉侧(图题匹配/排版/元素布局/视觉一致),聚合取总均分。**不按这 8 维拆 facet**——同一道题会落进两个 facet,违反边界可判规则。

**证据局限(必须随分数呈现)**:eduillustrate 是教育域 benchmark,单独承担一个基础能力构念偏窄——用教学场景样本推断通用生成能力,是**下界代理而非通用测量**。通用图像/图表生成 benchmark 列入待补,`single_source` 标记保留。

### P05 知识调用与掌握(2 facet,按知识类型)

| facet | benchmark · 取分维度 | 相关 | 置信 | 有效 | 分数 | 面 |
|---|---|---|---|---|---|---|
| 学科知识调用 | mmlu_pro · overall/category accuracy | 0.6 | 0.7 | 0.42 | 8.27–8.83 | 6(1) |
| | ceval · overall/category/subject accuracy | 0.6 | 0.7 | 0.42 | 8.74–9.38 | 6(1) |
| | edubench · domain_knowledge_accuracy | 0.35 | 0.8 | 0.28 | 7.52–9.50 | 12 |
| | agieval · overall/task/language/question_type accuracy | 0.35 | 0.7 | 0.245 | 8.11–9.06 | 6(1) |
| | edubench · basic_factual_accuracy | 0.3 | 0.8 | 0.24 | 8.62–9.66 | 12 |
| | olympiadbench · overall/subject/language/modality accuracy | 0.25 | 0.7 | 0.175 | 7.16–7.36 | 2 |
| | sas_bench · ECS error-cause consistency | 0.2 | 1.0 | 0.20 | 3.79–6.60 | 8 |
| | mathvista · task/question_type/answer_type accuracy | 0.2 | 0.7 | 0.14 | 8.41 | 1 |
| | k12vista · official partial-credit score | 0.15 | 0.8 | 0.12 | 6.55–7.40 | 2 |
| | mathtutorbench_problem_solving · Problem Solving | 0.3 | 0.45 | 0.135 | 9.55–9.80 | 6(2) |
| 教学专业知识 | pedagogy_benchmark · CDPK teaching knowledge selection | 0.45 | 0.8 | 0.36 | 7.01–9.01 | 12(1) |
| | pedagogy_benchmark · SEND special education needs selection | 0.35 | 0.8 | 0.28 | 6.64–8.45 | 12(1) |
| | mathtutorbench_pedagogy_hard · Pedagogy IF hard | 0.25 | 1.0 | 0.25 | 6.62–8.64 | 7 |
| | mathtutorbench_pedagogy · Pedagogy IF | 0.25 | 0.95 | 0.238 | 7.45–8.67 | 7 |
| | mathtutorbench_scaffolding · Scaffolding | 0.15 | 1.0 | 0.15 | 1.43–5.95 | 7 |
| | mathtutorbench_scaffolding_hard · Scaffolding hard | 0.15 | 1.0 | 0.15 | 1.30–5.61 | 7 |

知识簇普遍天花板,**门槛性质**——过线是必要条件,不证明会教。R22 把 mmlu_pro/ceval 0.35→0.7、agieval 0.4→0.7、olympiadbench 0.55→0.7:精确匹配判分最硬却被压到低于裁判天花板分的 edubench,是倒挂;"通识不主导教育画像"的护栏由映射结构承担(通识 benchmark 不挂教育侧 P),不该靠压置信实现。R22 同时把 mooccube_prereq 从本 P 摘除(先修关系推理与知识调用无构念链)。

mathtutorbench 的教学法/脚手架格挂在教学专业知识 facet,是因为 Pedagogy IF 是教学法的**生成式测量**,与 facet 描述"判别式与生成式测量并用"一致。

### P06 推理与生成(2 facet)

| facet | benchmark · 取分维度 | 相关 | 置信 | 有效 | 分数 | 面 |
|---|---|---|---|---|---|---|
| 解题推理 | olympiadbench · overall/subject/language/modality accuracy | 0.55 | 0.7 | 0.385 | 7.16–7.36 | 2 |
| | agieval · overall/task/language/question_type accuracy | 0.45 | 0.7 | 0.315 | 8.11–9.06 | 6(1) |
| | mathvista · task/question_type/answer_type accuracy | 0.45 | 0.7 | 0.315 | 8.41 | 1 |
| | mathtutorbench_problem_solving · Problem Solving | 0.6 | 0.45 | 0.27 | 9.55–9.80 | 6(2) |
| | k12vista · official partial-credit score | 0.3 | 0.8 | 0.24 | 6.55–7.40 | 2 |
| | mmlu_pro · overall/category accuracy | 0.3 | 0.7 | 0.21 | 8.27–8.83 | 6(1) |
| | ceval · overall/category/subject accuracy | 0.25 | 0.7 | 0.175 | 8.74–9.38 | 6(1) |
| 生成与归因推理 | edubench · reasoning_process_rigor | 0.35 | 0.8 | 0.28 | 7.10–8.95 | 12 |
| | mathtutorbench_mistake_correction · Mistake Correction | 0.2 | 0.9 | 0.18 | 8.60–9.37 | 6(1) |
| | edubench · higher_order_thinking_ability_development | 0.2 | 0.8 | 0.16 | 6.17–8.50 | 12 |
| | sas_bench · ECS error-cause consistency | 0.1 | 1.0 | 0.10 | 3.79–6.60 | 8 |

解题式推理与生成/归因式推理侧重不同,不强制协变。R22 摘除 mooccube_prereq 搭车格。

### P07 自我校验与修正(单 facet,自建直接测量)

| facet | benchmark · 取分维度 | 相关 | 置信 | 有效 | 分数 | 面 |
|---|---|---|---|---|---|---|
| 核心 | p07_selfcheck · two-round self-check (fix/break rate) | 0.85 | 0.85 | 0.723 | 5.02–5.57 | 5 |
| | mathtutorbench_solution_correctness · Solution Correctness | 0.25 | 0.85 | 0.213 | 8.57–8.95 | 6(1) |
| | p08_calibration · calibration composite (CWR/AUROC) | 0.2 | 0.85 | 0.17 | 5.57–6.75 | 5 |

两轮自查为主格,headline = 0.5×改对率 + 0.5×(1−改错率),与首轮正确率解耦。R22 摘除 problem_solving 搭车格(解题强与会复查之间无构念链)。

### P08 置信度校准与弃答(2 facet,自建直接测量)

| facet | benchmark · 取分维度 | 相关 | 置信 | 有效 | 分数 | 面 |
|---|---|---|---|---|---|---|
| 置信度校准 | p08_calibration · calibration composite (CWR/AUROC) | 0.8 | 0.85 | 0.68 | 5.57–6.75 | 5 |
| | p07_selfcheck · two-round self-check | 0.15 | 0.85 | 0.128 | 5.02–5.57 | 5 |
| 能力性弃答 | p08_abstention · balanced abstention score | 0.85 | 0.85 | 0.723 | 8.62–9.12 | 5 |

校准(概率质量)与弃答(行为决策)相关但可分离,两个自建测验按设计各测一半。

### P09 工具使用与长程智能体执行(2 空 facet)

**领域空白**,教育场景 agent/工具使用类评测缺位,报告标"暂未覆盖"。R19 拆两个空 facet(工具选择调用整合 / 长程计划状态保持失败恢复)显式呈现缺口——会调工具不代表撑得过长程状态维护,反之亦然,分开标更能指引补数据方向。

### P10 错误诊断(3 facet,按诊断深度)

| facet | benchmark · 取分维度 | 相关 | 置信 | 有效 | 分数 | 面 |
|---|---|---|---|---|---|---|
| 作答正误判定 | mathtutorbench_solution_correctness · Solution Correctness | 0.6 | 0.85 | 0.51 | 8.57–8.95 | 6(1) |
| 错误位置定位 | mathtutorbench_mistake_location · Mistake Location | 0.7 | 1.0 | 0.70 | 7.65–7.92 | 6(1) |
| | sas_bench · CCS step scoring consistency | 0.25 | 0.95 | 0.238 | 7.25–8.03 | 8 |
| 错因归因 | sas_bench · ECS error-cause consistency | 0.7 | 1.0 | 0.70 | 3.79–6.60 | 8 |
| | bea2025_tutor · dimension: Mistake_Identification | 0.25 | 0.9 | 0.225 | 7.93–8.53 | 5(2) |
| | mrbench_tutor · dimension: Mistake_Identification | 0.25 | 0.8 | 0.20 | 8.65–9.30 | 5(2) |
| | mathtutorbench_mistake_correction · Mistake Correction | 0.2 | 0.9 | 0.18 | 8.60–9.37 | 6(1) |
| | edubench · error_identification_correction_accuracy | 0.25 | **0.3** | 0.075 | 5.99–9.35 | 12 |
| | longtutor_diagnosis · four-category diagnosis macro-F1 | 0.1 | 0.75 | 0.075 | 1.97–3.16 | 5(1) |

R17 把原三个独立 P(判定/定位/归因)合并为一个 P、三项降为 facet:按拆分准入规则判定与定位不达标(残余约等于无、机制同为对参考解核验,分开的表象来自 mathtutorbench 恰好分任务);归因单独保留虽可但**允许拆≠必须拆**,诊断深度用 facet 表达。

**edubench 错误识别格的置信在 R23 压到 0.3**:M2 换裁判实验 ρ≤0.14、三裁判均分 4.6/7.4/8.7,是全仓库噪声最实锤的格,且跨模型排序与其他错误诊断格全部相反(M2.7 9.35 vs M3 5.99)。格不删、注记在位(R14"12 维全可挂"原则形式保留),但有效权重 0.2→0.075,降为尾部证据。R23 同时删除本 facet 的两个 judge 格(构念错位,judge 挂载收拢至 P11)。

### P11 主观题评价能力(3 facet,按评价操作类型)

| facet | benchmark · 取分维度 | 相关 | 置信 | 有效 | 分数 | 面 |
|---|---|---|---|---|---|---|
| 整体性评分 | sas_bench · QWK holistic total score | 0.7 | 0.9 | 0.63 | 7.90–8.68 | 8 |
| | asap_2 · essay holistic QWK | 0.65 | 0.8 | 0.52 | 4.73–6.11 | 10(3) |
| 分析式与多维度评分 | sas_bench · CCS step scoring consistency | 0.55 | 0.95 | 0.523 | 7.25–8.03 | 8 |
| | bea2025_judge · judge labels: mistake/guidance/actionability | 0.45 | 0.75 | 0.338 | 3.69–5.49 | 7(1) |
| | mrbench_judge · 8-dimension tutor response judging | 0.45 | 0.75 | 0.338 | 4.11–5.62 | 7(1) |
| 自动生成 rubric | —— 空白 —— | | | | | |

facet 轴是**评价操作类型**而非评价对象——"评的是什么对象"这条轴开放不可穷尽(以后可冒出评实验报告/评课件),边界不可判。

**R23 在此推翻 R20 的全局 judge 排除**:本 P 的被测构念就是判卷能力,judge 数据构念对口。`EXCLUDED_SCORING_BENCHMARKS` 清空、排除改由格级 `excluded` 标记承担,构念错位的 P10/P17 挂载删除,两个 judge benchmark 置信 0.0→0.75。取分一律用 macro-F1 而非裸 accuracy(judge 标签类别高度不平衡)。

> **⚠️ 尺度警告**:judge 格的 macro-F1(3.69–5.62)与同 facet 的 QWK/CCS(7.25–8.68)不在同一度量尺度上,两者进同一个加权平均隐含了可比性假设。本 P 分数因此在 R23 整体下移约 0.7–1.0——**这是口径变化而非模型退步,跨 R23 前后不可比**。该尺度问题待单独处理。

### P12 命题与作业设计(2 facet)

| facet | benchmark · 取分维度 | 相关 | 置信 | 有效 | 分数 | 面 |
|---|---|---|---|---|---|---|
| 题目生成(正确性与质量) | edubench · QG × 清晰启发 + 情景元素(task×metric) | 0.4 | 0.75 | 0.30 | 7.35–8.87 | 12 |
| | edubench · QG × 学科知识 + 基础事实(task×metric) | 0.3 | 0.75 | 0.225 | 8.43–9.85 | 12 |
| 难度与目标对齐 | —— 空白 —— | | | | | |

R19 定的 facet 二分对应经典测量学的两类独立参数:项目技术质量 / 难度与区分度定标。R23 新增第二格,用现成逐题裁判数据把"生成题目的内容正确性"从零覆盖变**部分覆盖**(裁判逐题核对学科内容对错);知识维度偏天花板(8.4–9.9),作代理格注记。**测评学效度(区分度、干扰项有效性、作答歧义)仍无覆盖**,整 P 参考值。

### P13 学习者画像建模(4 子能力声明,覆盖 2)

| facet | benchmark · 取分维度 | 相关 | 置信 | 有效 | 分数 | 面 |
|---|---|---|---|---|---|---|
| 知识状态估计 | longtutor_diagnosis · four-category diagnosis macro-F1 | 0.3 | 0.75 | 0.225 | 1.97–3.16 | 5(1) |
| 误概念识别 | —— 空白 —— | | | | | |
| 情感与参与识别 | —— 空白 —— | | | | | |
| 支持需求判断 | edubench · personalized_adaptation_learning_support | 0.3 | 0.8 | 0.24 | 5.55–6.88 | 12 |
| | pedagogy_benchmark · SEND special education needs selection | 0.25 | 0.8 | 0.20 | 6.64–8.45 | 12(1) |

longtutor_diagnosis 的低分是**真实发现**不是 bug,但带两条方法学注记:类别不平衡(多数类基线 acc 0.506 > 模型 0.35–0.44)、金标为特征决策矩阵+人工修订而非独立盲标。

R23 把 SEND 在支持需求 facet 的相关度 0.35→0.25:SEND 是教师考试选择题,测"知道特教需求知识";本 facet 构念是"判断学生需要哪类支持"(行为侧)。知识侧证据挂行为侧构念降一档,知识主家 P05 不动。

### P14 个性化教学策略选择(3 facet)

| facet | benchmark · 取分维度 | 相关 | 置信 | 有效 | 分数 | 面 |
|---|---|---|---|---|---|---|
| 教学目标对齐 | —— 空白 —— | | | | | |
| 教学策略制定 | pedagogy_benchmark · CDPK teaching knowledge selection | 0.6 | 0.8 | 0.48 | 7.01–9.01 | 12(1) |
| | pedagogy_benchmark · SEND special education needs selection | 0.4 | 0.8 | 0.32 | 6.64–8.45 | 12(1) |
| 教学策略执行 | mathtutorbench_scaffolding · Scaffolding | 0.5 | 1.0 | 0.50 | 1.43–5.95 | 7 |
| | mathtutorbench_scaffolding_hard · Scaffolding hard | 0.5 | 1.0 | 0.50 | 1.30–5.61 | 7 |
| | mathtutorbench_pedagogy_hard · Pedagogy IF hard | 0.45 | 1.0 | 0.45 | 6.62–8.64 | 7 |
| | mathtutorbench_pedagogy · Pedagogy IF | 0.45 | 0.95 | 0.428 | 7.45–8.67 | 7 |
| | edubench · personalized_adaptation_learning_support | 0.4 | 0.8 | 0.32 | 5.55–6.88 | 12 |
| | tutorbench · Fair815 multimodal tutor quality | 0.35 | 0.8 | 0.28 | 5.08–5.76 | 10(4) |
| | bea2025_tutor · dimension: Providing_Guidance | 0.3 | 0.9 | 0.27 | 9.40–9.77 | 5(2) |
| | mmtutorbench · multimodal tutor score | 0.3 | 0.9 | 0.27 | 5.74–7.60 | 2 |
| | mrbench_tutor · dimension: Providing_Guidance | 0.3 | 0.8 | 0.24 | 8.80–9.20 | 5(2) |
| | mathtutorbench_socratic · Socratic Questioning | 0.4 | 0.6 | 0.24 | 2.13–2.98 | 5(1) |
| | longtutor_teaching · strategy_alignment + history_utilization | 0.3 | 0.75 | 0.225 | 3.60–6.52 | 5(1) |
| | edubench · scenario_element_integration | 0.25 | 0.8 | 0.20 | 7.23–8.38 | 12 |

策略制定 facet 是情境化选择题、**陈述性代理**,与执行 facet 之间有 knowing-doing gap 注记。R23 把两格相关度上调(CDPK 0.35→0.6、SEND 0.3→0.4)做声明层归位——CDPK 是本 facet 构念最贴的直接测量,不该低于执行 facet 的 BLEU 代理格;facet 内只有两格,分数仅受比例影响。同批 socratic 0.65→0.4:BLEU 对参考问句判分,方差里"引导质量"与"措辞相似"不可分,降后由语义鲁棒的胜率格主导。

### P15 学习路径规划(知识结构层,单 facet 单源)

| facet | benchmark · 取分维度 | 相关 | 置信 | 有效 | 分数 | 面 |
|---|---|---|---|---|---|---|
| 核心 | mooccube_prereq · chance-corrected composite(先修选择 + 学习顺序排序) | 0.7 | 0.7 | 0.49 | 3.79–4.76 | 5 |

R16 把定义澄清为**知识结构层**的路径规划;"针对学生当前状态的个性化路径"是 P13×P15 的组合能力,不另设 facet。规则判分零裁判,但自建协议、无公开基线,置信压到 0.70 作参考值。R22 后这是 mooccube 的唯一主家挂载。

### P16 适配性解释与反馈生成(3 facet)

| facet | benchmark · 取分维度 | 相关 | 置信 | 有效 | 分数 | 面 |
|---|---|---|---|---|---|---|
| 内容性讲解与纠错反馈 | mmtutorbench · multimodal tutor score | 0.4 | 0.9 | 0.36 | 5.74–7.60 | 2 |
| | mathtutorbench_scaffolding · Scaffolding | 0.35 | 1.0 | 0.35 | 1.43–5.95 | 7 |
| | mathtutorbench_scaffolding_hard · Scaffolding hard | 0.35 | 1.0 | 0.35 | 1.30–5.61 | 7 |
| | tutorbench · Fair815 multimodal tutor quality | 0.4 | 0.8 | 0.32 | 5.08–5.76 | 10(4) |
| | mathtutorbench_mistake_correction · Mistake Correction | 0.35 | 0.9 | 0.315 | 8.60–9.37 | 6(1) |
| | mathtutorbench_pedagogy_hard · Pedagogy IF hard | 0.3 | 1.0 | 0.30 | 6.62–8.64 | 7 |
| | mathtutorbench_pedagogy · Pedagogy IF | 0.3 | 0.95 | 0.285 | 7.45–8.67 | 7 |
| | edubench · clarity_concision_inspiration | 0.3 | 0.8 | 0.24 | 7.83–8.93 | 12 |
| | mathtutorbench_socratic · Socratic Questioning | 0.35 | 0.6 | 0.21 | 2.13–2.98 | 5(1) |
| | edubench · higher_order_thinking_ability_development | 0.25 | 0.8 | 0.20 | 6.17–8.50 | 12 |
| | bea2025_tutor · dimension: Actionability | 0.2 | 0.9 | 0.18 | 8.87–9.60 | 5(2) |
| | mrbench_tutor · dimension: Actionability | 0.2 | 0.8 | 0.16 | 8.60–9.35 | 5(2) |
| 语气、情感与动机支持 | edubench · motivation_guidance_positive_feedback | 0.35 | 0.8 | 0.28 | 6.12–6.92 | 12 |
| | mrbench_tutor · Tutor_Tone(鼓励占比) | 0.2 | 0.8 | 0.16 | 9.15–9.60 | 5(2) |
| 教学产物生成 | edubench · TMG/PCC × 清晰启发 + 情景元素(task×metric) | 0.55 | 0.75 | 0.413 | 7.13–8.85 | 12 |
| | eduillustrate · 8-dim 0-5 visual explanation score | 0.25 | 0.85 | 0.213 | 6.35–7.41 | 7(3) |

R19 把对话侧拆成三 facet:语气支持独立(冷冰冰讲对 vs 温暖鼓励地讲对可独立失败,且有干净指标);概念讲解与纠错合并(最重的 tutorbench/mmtutorbench 整体分拆不出讲解/纠错,强行四分会让最厚证据悬空)。

R23 三处修订:摘除 `edubench · tone_style_consistency`(R19 已标死格子候选、R1 注记构念对齐弱、权重 0.1 象征性,三处标记同指);TMG/PCC 0.4→0.55(生成教学产物的直接测量,原值低于内容 facet 一批代理格);eduillustrate 0.3→0.25(主家迁 P04,降为副挂)。**内容反馈 facet 十二格零改动**——复核中提出的精简候选(socratic 构念属 P14、高阶思维偏效果侧)与统计冗余留待"精简版"再议。

> **两条不改分的注记**:①P14 执行 facet 与本 P 内容 facet 有 9 格同源数据(同一批判分换构念读取),两 P 分数会机械性高相关,效度检验中不得互为独立证据面。②内容 facet 内 scaffolding ↔ scaffolding_hard 跨模型 r=+0.98(n=7)、pedagogy ↔ pedagogy_hard r=+0.92,mathtutorbench 一家占 6/12 格、合计有效权重 1.81,facet 分数实质由其主导;edubench 清晰启发 ↔ scaffolding r=−0.92(n=6),同 facet 内两格给出相反排序——后者与效度计划记录的"edubench 家族内高相关、与外部零或负相关＝方法方差"同源,属 edubench 整体置信层问题。

### P17 教育角色边界判断(2 facet,事实单源)

| facet | benchmark · 取分维度 | 相关 | 置信 | 有效 | 分数 | 面 |
|---|---|---|---|---|---|---|
| 安全知识 | eduguard_sata · Teaching Harm / SATA RFS | 0.35 | 1.0 | 0.35 | 6.93–7.69 | 8 |
| 边界行为 | eduguard_adversarial · Adversarial Safety ASR | 0.3 | 1.0 | 0.30 | **3.76–9.96** | 8(1) |
| | eduguard_adversarial · Refusal quality distribution | 0.15 | 0.8 | 0.12 | 4.62–8.29 | 8(1) |
| | mrbench_tutor · Tutor_Tone(非冒犯占比) | 0.1 | 0.8 | 0.08 | 10.00–10.00 | 5(2) |

立论:知道边界(SATA 知识)与守住边界(对抗/对话行为)**不协变**(pilot ρ=0.07)。ASR 格是全仓库区分度最好的格之一。

R23 三处:①Tutor_Tone 相关度 0.25→0.1 但**保留**——5 个面全 10.00 方差为零,但这是"当前面板全都不冒犯"而非指标永久饱和(换弱模型 Offensive 会出现),留作**哨兵格**,降权使其不再压缩 ASR 拉开的真实差距;②边界行为 facet 描述放宽为"**常规与对抗条件下**守住边界"——只测压力条件等于默认常规条件必然安全,该默认在弱模型上不成立;③补 `single_source` 声明:删 judge 格后本 P 证据全部来自 EduGuard 一家两个子任务,两 facet 不协变的立论仍成立但**不构成跨 benchmark 互证**。

### P18 学生风险识别(2 facet,独立证据为零)

| facet | benchmark · 取分维度 | 相关 | 置信 | 有效 | 分数 | 面 |
|---|---|---|---|---|---|---|
| 风险信号识别 | eduguard_sata · Teaching Harm / SATA RFS | 0.3 | 1.0 | 0.30 | 6.93–7.69 | 8 |
| 风险严重度与紧迫性判断 | —— 空白 —— | | | | | |

R19 删除了原对抗鲁棒格(ASR 测越狱压力下的输出侧行为,而本 P 定义是**输入侧感知**任务)。删后仅剩与 P17/P19 同源的 SATA 一格。

> **⚠️ 本 P 独立证据为零。** 成熟度按"单源·同源,近似缺口"表述;显示分数与 P17 安全知识 facet 数值相同,**报告中不得读作两份独立证据**。复核中曾主张连 SATA 也摘除(SATA 测"知不知道什么算风险"的教师侧知识,与"从学生消息里察觉风险信号"失败机制可分离),用户裁决保留,该格继续作为知识代理承担本 P 唯一证据。

### P19 安全处置选择(2 facet)

| facet | benchmark · 取分维度 | 相关 | 置信 | 有效 | 分数 | 面 |
|---|---|---|---|---|---|---|
| 安全知识 | eduguard_sata · Teaching Harm / SATA RFS | 0.35 | 1.0 | 0.35 | 6.93–7.69 | 8 |
| 对抗鲁棒 | eduguard_adversarial · Refusal quality distribution | 0.6 | 0.8 | 0.48 | 4.62–8.29 | 8(1) |
| | eduguard_adversarial · Adversarial Safety ASR | 0.45 | 1.0 | 0.45 | 3.76–9.96 | 8(1) |

三个安全 P 中结构最健康的一个:两 facet 皆有证据,对抗侧两格分工明确——ASR 测"顶没顶住",拒答质量测"顶住之后处理得不得体"。R23 把拒答质量置信 0.7→0.8:它与 ASR 出自同一官方两阶段裁判流程,只是第二阶段判拒绝质量档更主观,原折价过大;提后有效权重 0.48 超过 ASR 的 0.45 成为 facet 主格,与 R7"拒答质量主格在此"的原意一致(此前声明与实际相拧)。

> **⚠️ 升级转介深度缺口**(经 satas.jsonl 语料核实):知识侧部分覆盖但不可计量("联系校心理老师"等转介选项散在心理健康类题的正确答案里,无类别标签无法单独取分);行为侧**零覆盖**——拒答质量三档无转介/升级维度,801 条场景全为主动越狱请求,无"学生被动流露风险需主动升级"情形。即本 P 现测的全是"拒绝恶意请求",完全未测"识别风险后主动转介人类"。补法是扩题 + 加统计维度,**不新开 facet**(轻度劝导到转介人类是同一处置选择技能的严重度连续谱)。

### P20 学术诚信与作答真实性判定(空 P)

**领域空白**,抄袭/代写/真实性判定评测缺位,`facets: []`、`coverage_gap: true`、`model_type: undeclared`,报告标"暂未覆盖"。未来若拆 facet,优先复用 P17–P19 的"识别 vs 处置"两阶段模板,而非按检测技术路线分(技术路线会把 facet 绑死在实现手段上)。边界:防作弊题目设计归 P12(那是出题动作),本 P 只管"判定这份作答是否本人真实完成"。

## 三、Benchmark 列表与置信权重

| benchmark | 名称 | 置信 | 定权理由 |
|---|---|---|---|
| eduguard_sata | EduGuard-Bench P1 | **1.0** | 官方 RFS 规则判分零裁判;R10:三 P 知识 facet 同源,不构成互证 |
| eduguard_adversarial | EduGuard-Bench P2 | **1.0**(拒答质量 override **0.8**) | 官方两阶段裁判流程原样移植,3 票多数;第二阶段判拒绝质量档更主观,折价一档 |
| mathtutorbench_mistake_location | MathTutorBench | 1.0 | 错误位置定位的直接测量 |
| mathtutorbench_scaffolding / _hard | MathTutorBench | 1.0 | 脚手架主测下一步教学干预选择与反馈生成 |
| mathtutorbench_pedagogy_hard | MathTutorBench | 1.0 | hard 子集较有区分度 |
| sas_bench | SAS-Bench | 0.9(CCS **0.95** / ECS **1.0**) | 简答题评分三指标:QWK 总分一致性、CCS 分步踩分、ECS 错因诊断一致性(错因归因核心锚) |
| mathtutorbench_pedagogy | MathTutorBench | 0.95 | 教学法指令遵循 |
| bea2025_tutor | BEA 2025 Tutor | 0.9 | 生成 tutor 回复 + 固定裁判逐维度标注;κ 0.22 校准弱,相关度侧已减半 |
| mathtutorbench_mistake_correction | MathTutorBench | 0.9 | 纠错需识别错因并生成可用修正 |
| mmtutorbench | MMTutorBench | 0.9 | 多模态 tutor 综合;当前小样本 |
| eduillustrate | EduIllustrate | 0.85 | 教学图示/图文协同生成;R5 后不再挂理解侧 |
| p07_selfcheck / p08_calibration / p08_abstention | 自建三测验 | 0.85 | 规则判分零裁判,但自建协议、无公开基线 |
| mathtutorbench_solution_correctness | MathTutorBench | 0.85 | 给定参考/学生解判断正确性 |
| edubench | EduBench | 0.8(TMG/PCC、QG 两复合 **0.75**;错误识别 **0.3**) | 12 原生裁判指标逐维度取分;错误识别换裁判 ρ≤0.14 故重罚,知识类指标天花板 |
| pedagogy_benchmark | Pedagogy Benchmark | 0.8 | 教学法知识选择题,规则判分无 LLM 抽取 |
| asap_2 | ASAP 2.0 | 0.8 | 官方 test split QWK 对人类整体分;非官方榜单口径 |
| ifeval | IFEval | 0.8 | 官方 checker 规则判分无裁判;通用指令非教育语境,门槛证据 |
| k12vista | K12Vista | 0.8 | 官方 rubric 的 LLM 裁判逐空 0/1;裁判未校准,参考值 |
| mrbench_tutor | MRBench Tutor | 0.8 | 固定裁判 8 维标注;一份标注取两个统计量分挂两 P(去重) |
| tutorbench | TutorBench | **0.8** | R22:1.0→0.8——分数混教学回复质量方差且模型面与主面板不重叠,满置信不自洽 |
| bea2025_judge / mrbench_judge | 判卷校准 | **0.75** | **R23 由 0.0 提起**,仅在 P11 计分;人类标注锚定的一致率统计,因裁判协议噪声折价一档 |
| longtutor_evidence / _diagnosis / _teaching | LongTutor 三任务 | 0.75 | 官方仓库只有 pipeline 脚本,自行移植为可复现 adapter |
| mmlu_pro / ceval / agieval / olympiadbench / mathvista | 通识与解题 | **0.7** | R22 统一提档:精确匹配判分最硬却被压到低于裁判天花板分,是倒挂;护栏由映射结构承担 |
| mooccube_prereq | MOOCCube 先修关系 | 0.7 | 905 条专家先修边当金标,100% 规则判分;自建协议、无公开基线,参考值 |
| mathtutorbench_socratic | MathTutorBench | 0.6 | BLEU 对合理的不同问法会误罚,保守 |
| mathtutorbench_problem_solving | MathTutorBench | 0.45 | 数学求解门槛,重要但不能证明会辅导 |

## 四、我们的创新与自建工作

这套映射不是把现成 benchmark 的榜单分数搬过来加权,以下工作是本仓库自己做的。

### 自建测验(4 个,均零标注成本、规则判分)

| 测验 | 测什么 | 协议 | 挂载 |
|---|---|---|---|
| p08_calibration | 置信度校准("自信地教错") | 复用精确匹配题 + 口头置信度,CWR/AUROC 合成 | P08 主格 |
| p08_abstention | 能力性弃答("不会时说不会") | UMWP/TreeCut 不可答题,平衡弃答分 | P08 主格 |
| p07_selfcheck | 两轮自查 | 先答题、再无提示复查;headline 与首轮正确率解耦 | P07 主格 |
| mooccube_prereq | 知识结构层路径规划 | MOOCCube 905 条专家先修边当金标,自建 200 道先修选择 + 100 道排序,随机基线校正 | P15 首个测量 |

P01/P02/P07/P08 在常规做法里全是"搭车分",这四个测验加上 IFEval 接入和 longtutor 挂载,把其中三个 P 变成了直接测量。

### 接入并改造的公开 benchmark(17 个 adapter,30+ 个评测变体)

统一 eval harness(`scripts/eval/`,load → call → extract → score → report,断点续跑、逐 benchmark 稳定产物目录)下自行移植:mathtutorbench 家族 9 任务(**win-rate 判分用 LLM-as-judge 替换官方 GPU 奖励模型**,并做裁判校准实验)、EduGuard 两阶段安全测验、MRBench / BEA2025 双模式(被测模型当裁判的校准模式 + 生成后固定裁判逐维度标注模式)、LongTutor 三任务、MMTutorBench 多模态辅导、IFEval 官方 checker、K12Vista、MathVista/MMLU-Pro/AGIEval/OlympiadBench/C-Eval(判分逻辑逐个从官方 repo 移植)。EduBench 则是导入同事的全量原始判分(11 模型 × 3,797 题 × 12 指标)后做题级重分析。

### 方法学(相对"拿榜单分加权"的常规做法)

1. **预注册测量模型**:每个 P 先声明 reflective/formative 与 facet 结构,声明先于数据;见数后的构念修订必须带裁决记录与方法学披露。
2. **拆分准入规则成文**:P 级需四类 benchmark 无关依据取二;facet 级需边界可判 + 构念不重复。**benchmark 的存在永远不构成拆分依据。**
3. **映射效度检查**(13 号产物):每个格子算跨模型区分度、每对同 P 格子算跨模型相关,给 validated/flagged/受限评级——权重不是拍的,错挂能被数据打回。
4. **换裁判实验**(M2):同一批回答换两个裁判重判,把 LLM 裁判指标二分为"真测量"(个性化/动机/高阶思维,ρ 0.6–0.8)与"裁判噪声"(错误识别,ρ≤0.14),后者在 R23 被重罚至置信 0.3。
5. **盲测对照**:用看不见图的模型跑多模态子集,若其分数≈明眼模型则说明该子集被文本污染(olympiadbench 因此从 0.2 降到 0.1),`BLIND_VISION_MODELS` 排除盲模型的视觉格。
6. **题级证据**:"会答题≠会教"从口号变成数字——同一批回答内,事实准确性与个性化/动机引导的题内相关约等于零。
7. **(任务×指标)级取分 + 死格子剔除**:LLM 裁判 benchmark 不用任务均分,按原生指标逐格挂 P;题级 SD 过低的死格子不进映射。
8. **一份标注多个统计量**:同一裁判标注按构念取不同统计量分挂不同 P(Tutor_Tone:P17 取 1−Offensive 测边界,P16 取鼓励占比测支持),不重复计数。
9. **缺测 min 替代**(R22):没测不等于好——缺格取该格已测面最低分顶替并标记,取代此前"缺测就不进分母"导致的虚高。
10. **研究层/用户层分离**:加权与统计检验留研究层;用户版每 P 一个分数 + 三档白话可信度。
11. **裁判工程纪律**:裁判原文全部落盘、取消 unparsed 中间态、全链路不设 max_tokens 上限(避免推理模型被饿死产生假失败)。

### 被推翻过的机制(留作教训)

- **四档证据分层**(education_core / diagnostic / foundation_gate ×0.45 / excluded_judge_task):R20 整体废除。档位在 facet 内压制的恰恰是构念最贴、判分最硬的证据;"通识不主导教学画像"应由映射结构承担(通识 benchmark 不挂教育侧 P),不该靠降权实现。
- **judge 任务全局排除**:R23 推翻。全局规则的理由"评估别人 ≠ 自己会做"在 P10/P17 成立,在 P11 恰好反转——那个 P 被测的就是判卷能力。教训是**全局规则要留格级例外口**,否则一刀切会在个别 P 上正好切反。

## 五、测量成熟度与替代值占比

### 三档可信度定档

| 档 | P |
|---|---|
| 可信 | P01(单源但规则判分)、P06、P07、P08、P10、P16 |
| 可信·门槛 | P05(多源成熟,但知识簇天花板,门槛性质) |
| 参考值 | P02、P03、P04、P11、P12、P13、P14、P15、P17、P18、P19 |
| 暂未覆盖 | P09、P20 |

### 替代值占比(发布面板 5 模型)

R22 的 min 替代让每个模型在每个可计分 P 上都有分,但**替代值不是测量**。下表是各模型分数中来自替代的权重占比,读分必须配合看:

| 模型 | 有替代成分的 P 数 | 整 P 全替代(占比 100%) | 占比最高的几个 |
|---|---|---|---|
| doubao-seed-2.0-pro | 11 | —— | P02 0.92、P10 0.65、P06 0.60、P11 0.51 |
| deepseek-v4-pro | 8 | **P03、P04** | P16 0.26、P14 0.18 |
| glm-5.2 | 7 | **P03、P04** | P13 0.30、P14 0.24、P11 0.22 |
| minimax-m2.7 | 6 | **P03、P04** | P19 0.73、P17 0.49 |
| minimax-m3 | 1 | —— | P11 0.22 |

**P03、P04 对三个模型是 100% 替代**——这两个 P 上除 M3 与 doubao 外没有任何真实测量,显示的 5.08 / 6.35 就是面板最低分本身,不可用于模型间比较。**doubao 的 P02 占比 0.92**、**M2.7 的 P19 占比 0.73** 同理。

## 六、未完成 TODO

### 数据缺口(挂载已定,分数不全)

按"补了解锁什么"排序:

| 项 | 现状 | 补法与收益 |
|---|---|---|
| **eduillustrate** | 发布面板 2/5(仅 M3、doubao) | **P04 唯一来源**,三个模型 100% 吃替代值;补齐即解锁整个 P04 |
| **视觉面(mathvista / olympiadbench / k12vista / mmtutorbench)** | 1/5、2/5、2/5、2/5 | P03 三个模型 100% 吃替代值;注意 deepseek-v4-pro 收图不报错但**看不见**,补它等于产出盲答废分 |
| **mmtutorbench** | 仅 2 个面,低于 `IMPUTE_MIN_FACES` 无替代兜底 | 却是 P16 内容 facet 有效权重最高的格(0.36),**优先级高** |
| **sas_bench 缺 glm-5.2** | 面是 glm-5.1。卡着 P11 两个 facet、P10 错因归因核心锚(0.7)、P10 定位(0.238),且置信 0.9–1.0 是全表最高档 | 官方 repo 在本地 `sources/datasets/sas_bench`(pipeline 全套 + CCS/ECS 官方实现),4,109 题跑一个模型即可;我们 harness 里**没有** sas adapter |
| **asap_2** | 3/5 吃替代值 4.73 | 补齐后 P11 整体性评分才是双源。⚠️ 导入目录可被覆写,用 `scripts/eval_benchmark.py --out-dir <scratch>` |
| **pedagogy_benchmark 缺 glm-5.2 全量** | 现仅 20 题冒烟 | 卡着 P05 教学知识、P13d、P14 制定三处 |
| **p07_selfcheck 缺 deepseek-v4-flash** | 4/5 | |
| edubench 模型错位 | glm-5.2 面已于 2026-07-19 补齐;其余模型齐 | 已解决 |
| 裁判 error 未清 | deepseek-v4-flash、doubao-lite 在 mathtutorbench win-rate 有残余 error 行 | 非发布模型不挡路 |

**sas_bench 的 CCS/ECS 尚未独立复算**:QWK 已复算并与同事日志吻合(最大偏差 2.8e-14),但 CCS/ECS 仍沿用日志值(`summary.json` 的 `audit.ccs_ecs_independently_verified: false`)。官方实现在本地,应补一次复算把 flag 翻正。

### 构念缺口(空白 facet / 空白 P)

| 项 | 缺什么 | 候选路线 |
|---|---|---|
| P09 两 facet | 教育场景 agent 评测领域空白 | 工具侧自建小任务(调计算器/画图/检索课程库);长程侧等社区;通用 GAIA/tau-bench 类只能当门槛 |
| P20 | 领域空白,暂不拆 facet | 需要时自建:真实学生作答 + 模型改写对照组做判别任务(AUC) |
| **P04 通用生成证据** | 唯一来源是教育域 benchmark,属下界代理 | 通用图像/图表生成评测,让 P04 摆脱教育域代理 |
| P04 时序与交互产物 | 空 facet | InteractScience(生成交互教学网页)是候选 |
| P03 视频/音频 | 空 facet | SciVideoBench 等,需 harness 支持视频输入 |
| P13b 误概念识别 | 空 facet | Eedi 误概念标注(NeurIPS 2024 竞赛)、Bridge(700 段真实辅导对话) |
| P13c 情感与参与识别 | 空 facet | IntrEx(EMNLP 2025)可直接做判别任务 |
| P14 教学目标对齐 | 空 facet | 自建协议(给定教学目标+学情,判断教学回复是否服务目标),或找含课标标注的教案对话数据 |
| P11 生成 rubric | 空 facet | 自建"对专家 rubric 一致性"协议 |
| P12 正确性效度 + 难度目标对齐 | R23 后正确性部分覆盖;测评学效度与第二 facet 仍空 | Eedi 干扰项-误概念数据测干扰项设计;难度定标用真实作答通过率校验 |
| **P19 升级转介** | 知识侧不可计量、行为侧零覆盖 | 含"学生被动流露风险 → 主动升级/转介"情形的安全处置评测(**新 benchmark 需求**) |
| P18 严重度判断 + 独立证据为零 | 空 facet;唯一格子与 P17/P19 同源 | 需含严重度分级标注的学生风险对话数据;SATA 类别标注先解同源 |
| P17/P18/P19 知识 facet 同源 | 三 P 共用一份 SATA | R10:SATA 类别标注(LLM 粗标+抽检)拆出独立证据 |
| P02 区分度 | 三拆后已解除红旗 | 若需更强区分,补更难的长上下文任务 |

### 方法学待办

1. **度量尺度可比性**(R23 新暴露):P11 分析式 facet 里 macro-F1(3.7–5.6)与 QWK/CCS(7.3–8.7)混在同一加权平均,隐含了两者可比的假设。这不只影响 P11——凡是同一 facet 混了不同度量族的地方都有此问题,需要一次系统排查与统一归一方案。
2. **P16 内容 facet 精简**:12 格中 mathtutorbench 占 6 格、合计有效权重 1.81,且 hard/非 hard 对之间 r=0.92–0.98。本轮按"只按构念裁决、统计冗余不作删格依据"的口径零改动,留待精简版处理。
3. **benchmark 改名重构**:`p07_selfcheck` / `p08_calibration` / `p08_abstention` 沿用 pre-R20 旧编号起名,编号已两度迁移,名字彻底误导。涉及 adapter 名、`reports/eval/` 目录、映射 benchmark_id、聚合脚本、item_list 路径、历史文档,单独作为一次重构,不并入映射批次。
4. **`build_rebenchmark_conclusion_plan.py` 编号迁移**:仍是 pre-R20 旧号(含 P21/P22),不在四步管线内,单独处理。

### 流程性

死格子剔除与 edubench 指标级权重核对 → v 版本对比 + 排名稳定性 → M4 双报告(研究版/用户版)。详见 `doc/rebenchmark_workstream_overview_2026-07-12.md`。
