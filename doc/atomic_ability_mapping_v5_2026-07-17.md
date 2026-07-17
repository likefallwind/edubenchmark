# 教育 AI 原子能力与 Benchmark 映射(v5 定稿,2026-07-17)

本文档是**当前状态的干净快照**:原子能力清单、每个能力的定义与 facet、映射到哪些 benchmark 的哪些维度、权重多少、测量成熟度如何,以及创新点和未完成事项。不含历史沿革与裁决过程——那些在 `doc/atomic_ability_mapping_final_2026-07-15.md`(裁决记录 R1–R19)和 `doc/benchmark_ability_mapping_v2_2026-07-15.md`(变化记录)里。

机器可读版(单一事实源):`data/mapping_measurement_model_v5.json`。本文档所有表格由该 JSON 逐格核对生成,如有出入以 JSON 为准。

约定:权重是 facet 内的相对重要度,不归一;格子写法为 `benchmark · 取分维度`。证据分四档:education_core(教学核心)/ diagnostic(诊断)/ foundation_gate(门槛)/ excluded_judge_task(暂不计分)。

分数聚合(逐层):①格子分 = benchmark 原始分按指标族归一到 0–10;②格子有效权重 = **映射表格子权重 × benchmark 置信权重**(后者按 benchmark 定于聚合脚本 `BENCHMARK_META`,表达该 benchmark 本身多可信,如 mmlu_pro 0.35 / sas_bench 0.9 / tutorbench 1.0);③facet 分 = 格子分按有效权重加权平均;④P 分 = 有证据 facet 的等权平均(空 facet 不计);⑤headline 用 tier_adjusted 口径:foundation_gate 档权重再 ×0.45,diagnostic 与 education_core 在 P 分中**不**降权(诊断档 ×0.75 只用于 12 号组合重要度分析,不进 P 分),excluded_judge_task 跳过。

## 划分规则(先读这个)

- **P 层**:原子能力靠组合覆盖场景(完备性/组合性,见 `doc/atomic_principle.md`)。子能力拆分成独立 P 需要理论/失败机制/教师标准/同源数据四类 benchmark 无关依据中至少两个;benchmark 的存在永远不构成拆分依据。
- **facet 层**(R19 成文):两条硬约束——**边界可判**(任何任务能无歧义归入唯一 facet,划分依据封闭可操作;"场景"这类开放轴不合格)与**不重复**(两个 facet 不能是同一构念换个说法)。现阶段**过于擦边的证据格宁缺勿滥**。
- **测不了 ≠ 不存在**:空白能力与空白 facet 保留在清单里显式标"暂未覆盖",清单不随测量可行性伸缩。

## 一、原子能力清单(20 项)

编号到 P23,其中 P04/P12/P13 是墓碑编号(已并入其他 P,保留不复用),在册 20 项。大类划分是展示层,不进测量模型。

### 模型基础能力(8 项)——不依赖教育场景就能定义,通用 benchmark 可测

| 子类 | P | 名称 | 一句话定义 | facet(子类别) | 测量成熟度 |
|---|---|---|---|---|---|
| 输入理解与遵循 | P01 | 指令与约束遵循 | 按显式指令和格式/行为约束产出 | 不分(core) | 直接测量(规则判分) |
| | P02 | 长上下文与证据定位 | 在长材料/长对话中定位并引用相关证据 | 不分(core) | 直接测量·区分度待验证(三模型面 0.787–0.807 挤在一起) |
| | P03 | 多模态理解 | 读懂教育场景中的非文本材料并据此推理 | 解题图像 / 学科图表 / 图文混排材料 / 视频音频【空白】 | 多源;学科图表与图文混排主格仅 1 模型面,参考值 |
| 知识与推理 | P05 | 知识调用与掌握 | 学科知识与教学专业知识的正确调用 | 学科知识调用 / 教学专业知识 | 多源·成熟(知识簇天花板,门槛性质) |
| | P06 | 推理与生成 | 解题推理与约束下的生成推理 | 解题推理 / 生成与归因推理 | 多源·成熟 |
| 输出可靠性 | P07 | 自我校验与修正 | 复查自己的输出,发现并修正错误 | 不分(core) | 直接测量(自建两轮自查) |
| | P08 | 置信度校准与弃答 | 自信程度与正确率一致;不会时主动弃答 | 置信度校准 / 能力性弃答 | 直接测量(两个自建测验一一对应) |
| 工具与长程执行 | P09 | 工具使用与长程智能体执行 | 调用工具、完成多步长程任务 | 工具调用与结果整合【空白】/ 长程计划与状态保持【空白】 | **空白,暂未覆盖** |

### 教育领域能力(12 项)——内核带教育专有的知识、构念或政策

| 子类 | P | 名称 | 一句话定义 | facet(子类别) | 测量成熟度 |
|---|---|---|---|---|---|
| 学业评价与诊断 | P11 | 错误诊断 | 诊断学生错误:判对错、定位错误步骤、解释错因 | P11a 作答正误判定 / P11b 错误位置定位 / P11c 错因归因 | 判对/定位单源+;归因多源 |
| | P14 | 主观题评价能力 | 评价主观作答:整体评分、分析式评分、生成评分标准 | 整体性评分 / 分析式与多维度评分 / 自动生成 rubric【空白】 | 整体多源;分析式计分单源;rubric 生成空白 |
| | P23 | 命题与作业设计 | 为学生设计考试/作业题目:出题、难度定标、目标对齐 | 题目生成(正确性与质量)/ 难度与目标对齐【空白】 | 单源·薄(仅表达质量),整 P 参考值 |
| 学习者建模与教学规划 | P16 | 学习者画像建模 | 从交互中建模学生的水平、需求与特征 | P16a 知识状态估计 / P16b 误概念识别【空白】/ P16c 情感与参与识别【空白】/ P16d 支持需求判断 | 弱(4 个子能力覆盖 2 个;P16a 参考值) |
| | P17 | 个性化教学策略选择 | 对齐教学目标与学生状态,制定并执行合适的教学策略 | 教学目标对齐【空白】/ 教学策略制定 / 教学策略执行 | 执行 facet 多源·证据最厚;制定 facet 为陈述性代理 |
| | P19 | 学习路径规划(知识结构层) | 基于知识先修结构规划学习顺序 | 不分(core) | 单源·参考值(自建协议,3 模型面) |
| 教学生成与表达 | P18 | 适配性解释与反馈生成 | 生成适配学生的解释、引导与反馈 | 内容性讲解与纠错反馈 / 语气情感与动机支持 / 教学产物生成 | 内容 facet 多源·证据最厚;语气 facet 偏薄 |
| | P10 | 多模态教学产物生成 | 生成图示等非文本教学产物 | 静态视觉产物 / 时序与交互产物【空白】 | 单源(静态);时序交互空白 |
| 教育安全与诚信 | P20 | 教育角色边界判断 | 守住教育者的角色与行为边界 | 安全知识 / 边界行为 | 双源(知识 facet 与 P21/P22 同源) |
| | P21 | 学生风险识别 | 识别学生消息中的风险信号并判断严重度 | 风险信号识别 / 严重度与紧迫性判断【空白】 | 单源·同源,近似缺口 |
| | P22 | 安全处置选择 | 对风险与越界请求选择正确处置方式 | 安全知识 / 对抗鲁棒 | 双源;升级转介为两 facet 内深度缺口 |
| | P15 | 学术诚信与作答真实性判定 | 识别抄袭、代写等真实性问题 | 暂不拆 | **空白,暂未覆盖** |

### 边界口径

- **P03 按内容构成单轴分 facet**(材料本身长什么样,不掺场景/任务标签;渲染 vs 拍摄不影响归属)。难度不是构念维度,用证据标签表达。
- **P11 与 P14 的边界**:P11 是对着参考解找错、解释错(诊断);P14 是把作答证据映射到评分量尺(量尺映射),机制不同。
- **P14 与 P23 的边界**:涉及评分标准的(造 rubric 或用 rubric 评)一律归 P14;P23 只管题目(题干、选项、答案、干扰项、难度、目标对齐)。
- **P19 只管知识结构层**:"针对某个学生的个性化路径规划"是 P16 × P19 的组合能力,不是 P19 的缺口。
- **P15 与 P20–22 同属"识别信号 + 选择处置"家族**,报告呈现归安全组;未来若拆 facet,模板优先复用"识别 vs 处置"两阶段。
- **教师协作不设独立 P**:遵循教师方案 = P01 × P17,该转交人类 = P22 的一种处置,向教师报告学情 = P16 输出侧,守住辅助定位 = P20;残余机制不满足拆分准入。

## 二、逐能力映射明细

### P01 指令与约束遵循

定义:按显式指令和格式/行为约束产出。不分 facet:任务目标理解、格式约束、多约束优先级等可做诊断切片,但现阶段缺乏相互独立的测量,不拆。

| 格子 | 权重 | 档位/注记 |
|---|---|---|
| ifeval · prompt 严格准确率 | 1.0 | 门槛档;直接测量,规则判分无裁判 |
| agieval · 格式遵循 | 0.2 | 门槛 |
| ceval · 格式遵循 | 0.15 | 门槛 |
| mmlu_pro · 格式遵循 | 0.1 | 门槛 |
| p08_abstention · 弃答约束遵循 | 0.15 | diagnostic |

### P02 长上下文与证据定位

定义:在长材料/长对话中定位并引用相关证据。不分 facet:上下文长度、单/多文档是测试条件,不是构念维度。

| 格子 | 权重 | 档位/注记 |
|---|---|---|
| longtutor_evidence · 长对话证据抽取 | 0.7 | diagnostic;直接测量,但三模型面 0.787/0.807/0.791 区分度待验证 |
| asap_2 · 作文整体 QWK | 0.2 | 代理(搭车) |
| sas_bench · QWK / CCS | 0.15 / 0.2 | 代理(搭车) |
| mathtutorbench_solution_correctness / mistake_location | 0.15 / 0.2 | 代理(搭车) |

### P03 多模态理解(4 facet,按内容构成)

facet 定义:**解题图像**——题目自带的单一规范几何图/函数图等图形化解题条件(渲染或拍摄不影响归属);**学科图表**——单一规范的学科图表(实验装置、地图、统计图等)的多步理解;**图文混排材料**——掺杂手写笔迹、批注、多来源拼贴的复合图文材料,按内容构成定义、不问出现场合;**视频/音频**——教学视频与音频材料(空白)。

| facet | 格子 | 权重 | 档位/注记 |
|---|---|---|---|
| 解题图像 | mathvista · 任务/题型准确率 | 0.35 | diagnostic;混有统计图表子集,跨前两 facet,按 benchmark 粒度整体记于此 |
| 解题图像 | olympiadbench · 多模态子集准确率 | 0.2 | 门槛 |
| 学科图表 | k12vista · 学科图多步理解 | 0.55 | diagnostic;裁判未校准,1 模型面,参考值 |
| 图文混排材料 | tutorbench · 多模态辅导质量 | 0.25 | education_core;分数混教学质量方差,作理解证据属代理 |
| 图文混排材料 | mmtutorbench · 多模态辅导六维 | 0.3 | diagnostic;同上代理注记 |
| 视频/音频 | (空白,暂未覆盖) | — | — |

### P05 知识调用与掌握(2 facet,按知识类型)

facet 定义:**学科知识调用**——正确调用学科事实、概念与方法(判别式答题与生成式运用同为测量方式,不再分 facet);**教学专业知识**——教学法、课程与特殊教育需求等教师专业知识的掌握。

| facet | 格子 | 权重 | 档位/注记 |
|---|---|---|---|
| 学科知识调用 | mmlu_pro / ceval · 总分 | 0.6 / 0.6 | 门槛 |
| 学科知识调用 | agieval · 总分 | 0.35 | 门槛 |
| 学科知识调用 | mathtutorbench_problem_solving | 0.3 | 门槛 |
| 学科知识调用 | olympiadbench · 总分 | 0.25 | 门槛 |
| 学科知识调用 | mathvista · 总分 | 0.2 | diagnostic |
| 学科知识调用 | mooccube_prereq · 先修推理 | 0.2 | diagnostic;副挂 |
| 学科知识调用 | k12vista · 总分 | 0.15 | diagnostic;副挂 |
| 学科知识调用 | edubench · 领域知识准确性 / 基础事实准确性 | 0.35 / 0.3 | education_core;裁判打到天花板,门槛性质 |
| 学科知识调用 | sas_bench · ECS | 0.2 | diagnostic;相邻证据(主构念在 P11c) |
| 教学专业知识 | pedagogy_benchmark · CDPK / SEND / 合并卡 | 0.45 / 0.35 / 0.4 | education_core;CDPK/SEND 分列格现无独立数据源,实际计分只有合并卡 |
| 教学专业知识 | mathtutorbench_pedagogy ±hard | 0.25 | diagnostic;相邻证据(主构念在 P17/P18) |
| 教学专业知识 | mathtutorbench_scaffolding ±hard | 0.15 | diagnostic;同上 |

### P06 推理与生成(2 facet)

facet 定义:**解题推理**——面向标准答案的多步解题推理;**生成与归因推理**——生成教学内容、解释错因时的推理严谨性与思维引导深度。

| facet | 格子 | 权重 | 档位 |
|---|---|---|---|
| 解题推理 | mathtutorbench_problem_solving | 0.6 | 门槛 |
| 解题推理 | olympiadbench · 总分 | 0.55 | 门槛 |
| 解题推理 | agieval / mathvista · 总分 | 0.45 / 0.45 | 门槛 / diagnostic |
| 解题推理 | mmlu_pro / ceval · 总分 | 0.3 / 0.25 | 门槛 |
| 解题推理 | k12vista · 总分 | 0.3 | diagnostic |
| 解题推理 | mooccube_prereq · 先修推理 | 0.1 | diagnostic |
| 生成与归因推理 | edubench · 推理过程严谨性 | 0.35 | education_core |
| 生成与归因推理 | edubench · 高阶思维能力培养 | 0.2 | education_core;换裁判稳健(ρ 0.63–0.73) |
| 生成与归因推理 | mathtutorbench_mistake_correction | 0.2 | education_core |
| 生成与归因推理 | sas_bench · ECS | 0.1 | education_core |

### P07 自我校验与修正

定义:复查自己的输出,发现并修正错误。不分 facet:fix rate 与 break rate 是同一协议下的两个诊断指标,当前协议未把发现/定位/修复干净隔离,拆分会产生伪精细度。

| 格子 | 权重 | 档位/注记 |
|---|---|---|
| p07_selfcheck · 两轮自查(改对率/改错率合成) | 0.85 | diagnostic;直接测量,headline 与首轮正确率解耦 |
| mathtutorbench_solution_correctness | 0.25 | 代理 |
| p08_calibration · 校准合成分 | 0.2 | 代理 |
| mathtutorbench_problem_solving | 0.1 | 代理 |

### P08 置信度校准与弃答(2 facet)

facet 定义:**置信度校准**——表达的自信程度与实际正确率一致(不自信地教错);**能力性弃答**——面对不可答或超出能力的问题主动说不会。两个自建测验一一对应,是全映射最干净的 P。

| facet | 格子 | 权重 | 档位 |
|---|---|---|---|
| 置信度校准 | p08_calibration · CWR/AUROC 合成 | 0.8 | diagnostic;直接测量 |
| 置信度校准 | p07_selfcheck | 0.15 | 相邻证据 |
| 能力性弃答 | p08_abstention · 平衡弃答分 | 0.85 | diagnostic;直接测量 |

### P09 工具使用与长程智能体执行(2 空 facet)

facet 定义:**工具选择、调用与结果整合**——选择合适的工具、正确构造调用并核验整合工具结果;**长程计划、状态保持与失败恢复**——跨多轮/多任务维持计划与状态,从中途失败中恢复。两种机制在 agent 评测中公认可独立失败,分开标出以指引补数据方向。两 facet 均无挂载,整 P 暂不可计分。

### P10 多模态教学产物生成(2 facet)

facet 定义:**静态视觉教学产物生成**——生成图示、示意图等静态视觉产物;**时序与交互式教学产物生成**——生成音频讲解、视频/动画、交互式演示与仿真等含时间连续性或交互状态的产物(空白)。

| facet | 格子 | 权重 | 档位/注记 |
|---|---|---|---|
| 静态视觉产物 | eduillustrate · 视觉讲解八维 | 0.45 | diagnostic;单源,评级恒 single_source |
| 时序与交互产物 | (空白,暂未覆盖) | — | — |

### P11 错误诊断(3 facet,按诊断深度)

facet 定义:**P11a 作答正误判定**——判断学生作答对不对;**P11b 错误位置定位**——指出错误发生在解答的哪一步;**P11c 错因归因**——解释为什么错(错因类别、误概念)。判对→定位→归因是同一诊断任务的深度梯度,不是三个独立构念。

| facet | 格子 | 权重 | 档位/注记 |
|---|---|---|---|
| P11a 作答正误判定 | mathtutorbench_solution_correctness | 0.6 | education_core |
| P11b 错误位置定位 | mathtutorbench_mistake_location | 0.7 | education_core |
| P11b 错误位置定位 | sas_bench · CCS | 0.25 | education_core |
| P11c 错因归因 | sas_bench · ECS(与人类专家错因标签一致性) | 0.7 | education_core;核心锚 |
| P11c 错因归因 | bea2025_tutor / mrbench_tutor · Mistake_Identification | 0.25 / 0.25 | education_core;LLM 裁判单维度分,3 模型面 |
| P11c 错因归因 | edubench · 错误识别与纠正 | 0.25 | education_core;方法学注记:换裁判分歧大(ρ≤0.14) |
| P11c 错因归因 | mathtutorbench_mistake_correction | 0.2 | education_core;只测改对与否,部分相关 |
| P11c 错因归因 | longtutor_diagnosis · 四类知识状态诊断 macro-F1 | 0.1 | diagnostic;副挂(主挂 P16a,归因证据源是交互历史而非作答内容) |
| P11c 错因归因 | bea2025_judge / mrbench_judge | 0.3 / 0.25 | 暂不计分(judge 任务) |

### P14 主观题评价能力(3 facet,按评价操作类型)

facet 定义:**整体性评分**——对整份主观作答给出整体分,以与人类评分的一致性计(QWK 类);**分析式与多维度评分**——按步骤/维度分解评判(步骤级评分一致性、逐维度判卷),以与人类标注的一致性计;**自动生成 rubric**——为主观任务生成评分标准(空白)。

| facet | 格子 | 权重 | 档位/注记 |
|---|---|---|---|
| 整体性评分 | sas_bench · QWK | 0.7 | education_core |
| 整体性评分 | asap_2 · QWK | 0.65 | education_core |
| 分析式与多维度评分 | sas_bench · CCS | 0.55 | education_core;该 facet 计分证据单源 |
| 分析式与多维度评分 | bea2025_judge · 四维判卷 | 0.45 | 暂不计分 |
| 分析式与多维度评分 | mrbench_judge · 八维判卷 | 0.45 | 暂不计分 |
| 自动生成 rubric | (空白,暂未覆盖) | — | — |

### P15 学术诚信与作答真实性判定

无挂载,领域空白,整 P 暂不可计分。暂不拆 facet(展开方式未定);归"安全与诚信"家族呈现。

### P16 学习者画像建模(4 子能力,覆盖 2)

facet 定义:**P16a 知识状态估计**——从作答历史判断学生会什么、不会什么;**P16b 误概念识别**——识别学生持有的具体误概念(空白);**P16c 情感与参与识别**——识别学生情绪、动机与参与度信号(空白);**P16d 支持需求判断**——判断学生需要哪类支持(含特殊教育需求)。

| facet | 格子 | 权重 | 档位/注记 |
|---|---|---|---|
| P16a 知识状态估计 | longtutor_diagnosis · 四类知识状态诊断 macro-F1 | 0.3 | diagnostic;参考值(类别不平衡,金标为决策矩阵+人工修订,3 模型面) |
| P16d 支持需求判断 | pedagogy_benchmark · SEND / 合并卡 | 0.35 / 0.3 | education_core(画像知识面) |
| P16d 支持需求判断 | edubench · 个性化适应与学习支持 | 0.3 | education_core(画像应用面);换裁判稳健 |
| P16b / P16c | (空白,暂未覆盖) | — | — |

### P17 个性化教学策略选择(3 facet)

facet 定义:**教学目标对齐**——教学决策与课标/教学目标及学生当前状态保持一致,教的东西服务于既定目标(空白:现有格子无一测此项,longtutor_teaching 的 strategy_alignment 锚的是学生状态/历史,不是课标目标);**教学策略制定**——面对具体学生情境选出或制定合适的教学策略(现仅情境化选择题测量,存在 knowing-doing gap,按陈述性代理表述);**教学策略执行**——在真实辅导对话/生成中把策略落地做出来。

| facet | 格子 | 权重 | 档位/注记 |
|---|---|---|---|
| 教学目标对齐 | (空白,暂未覆盖) | — | — |
| 教学策略制定 | pedagogy_benchmark · CDPK / SEND / 合并卡 | 0.35 / 0.3 / 0.3 | education_core |
| 教学策略执行 | mathtutorbench_socratic · 提问式引导 | 0.65 | education_core |
| 教学策略执行 | mathtutorbench_scaffolding ±hard | 0.5 | education_core |
| 教学策略执行 | mathtutorbench_pedagogy ±hard | 0.45 | education_core |
| 教学策略执行 | edubench · 个性化适应与学习支持 | 0.4 | education_core |
| 教学策略执行 | tutorbench · 辅导质量 | 0.35 | education_core |
| 教学策略执行 | bea2025_tutor / mrbench_tutor · Providing_Guidance | 0.3 / 0.3 | education_core;3 模型面 |
| 教学策略执行 | mmtutorbench · 六维合成 | 0.3 | diagnostic;1 模型面 |
| 教学策略执行 | longtutor_teaching · strategy_alignment + history_utilization | 0.3 | diagnostic;3 模型面 |
| 教学策略执行 | edubench · 情景元素融合 | 0.25 | education_core |

### P18 适配性解释与反馈生成(3 facet)

facet 定义:**内容性讲解与纠错反馈**——对学生作答/提问的内容性响应(概念解释、引导提问、纠错、脚手架与可执行反馈;讲解与纠错不再细分——最重的整体分证据拆不出两者);**语气、情感与动机支持**——回应中的语气、鼓励与动机支持(支持性表达本身,独立于讲的内容对不对);**教学产物生成**——生成教材、讲义、图解等教学材料。

| facet | 格子 | 权重 | 档位/注记 |
|---|---|---|---|
| 内容性讲解与纠错反馈 | tutorbench / mmtutorbench | 0.4 / 0.4 | education_core / diagnostic |
| 内容性讲解与纠错反馈 | mathtutorbench_mistake_correction / scaffolding ±hard / socratic | 0.35 | education_core |
| 内容性讲解与纠错反馈 | edubench · 表达清晰简洁启发 | 0.3 | education_core |
| 内容性讲解与纠错反馈 | mathtutorbench_pedagogy ±hard | 0.3 | education_core |
| 内容性讲解与纠错反馈 | edubench · 高阶思维能力培养 | 0.25 | education_core |
| 内容性讲解与纠错反馈 | bea2025_tutor / mrbench_tutor · Actionability | 0.2 / 0.2 | education_core;该维度裁判校准弱(κ0.22),低权重 |
| 语气情感与动机支持 | edubench · 动机引导与积极反馈 | 0.35 | education_core;换裁判稳健(ρ 0.61–0.68) |
| 语气情感与动机支持 | mrbench_tutor · Tutor_Tone 鼓励占比 | 0.2 | education_core;与 P20 取同一标注的不同统计量,3 模型面 |
| 语气情感与动机支持 | edubench · 语气风格一致性 | 0.1 | education_core;天花板格(题级 sd 0.18–0.42),死格子剔除候选 |
| 教学产物生成 | edubench · TMG/PCC ×(清晰启发/情景元素) | 0.4 | education_core |
| 教学产物生成 | eduillustrate · 视觉讲解八维 | 0.3 | diagnostic |

### P19 学习路径规划(知识结构层)

定义:基于知识先修结构规划学习顺序。学习者状态相关的路径规划 = P16 × P19 组合能力。

| 格子 | 权重 | 档位/注记 |
|---|---|---|
| mooccube_prereq · 先修关系推理(机会校正合成) | 0.7 | diagnostic;规则判分零裁判;自建协议、无公开基线,参考值;3 模型面(2026-07-17 首次有分,机会校正后 3.8–4.5/10) |

### P20 教育角色边界判断(2 facet)

facet 定义:**安全知识**——知道教育场景中哪些行为构成伤害/越界(选择题);**边界行为**——对抗压力下实际守住教育者的角色与行为边界。

| facet | 格子 | 权重 | 档位/注记 |
|---|---|---|---|
| 安全知识 | eduguard_sata · SATA RFS | 0.35 | education_core;与 P21/P22 同源,不构成互证 |
| 安全知识 | mrbench_judge | 0.3 | 暂不计分 |
| 边界行为 | eduguard_adversarial · ASR | 0.3 | education_core |
| 边界行为 | mrbench_tutor · Tutor_Tone(1−Offensive 占比) | 0.25 | education_core;边界构念只取越界信号,鼓励成分归 P18 |
| 边界行为 | eduguard_adversarial · 拒答质量 | 0.15 | diagnostic;主挂 P22 |

### P21 学生风险识别(2 facet)

facet 定义:**风险信号识别**——识别学生消息中的风险信号(现仅选择题式知识面测量);**风险严重度与紧迫性判断**——判断已识别风险需立即干预、短期关注还是一般性支持(空白;决定后续处置,与识别可独立失败)。

成熟度注记:唯一格子与 P20/P22 同源,P21 独立证据为零——"单源·同源,近似缺口"。

| facet | 格子 | 权重 | 档位/注记 |
|---|---|---|---|
| 风险信号识别 | eduguard_sata · SATA RFS | 0.3 | education_core;同源注记同上 |
| 严重度与紧迫性判断 | (空白,暂未覆盖) | — | — |

### P22 安全处置选择(2 facet)

facet 定义:**安全知识**——知道对风险与越界请求的正确处置方式(选择题);**对抗鲁棒**——越狱等恶意操纵压力下仍选择并执行正确处置(抵抗刻意诱导话术的稳健性,非一般执行力;拒答且拒得有质量)。

深度缺口注记:轻度劝导到转介人类是同一处置技能的严重度连续谱,不另设 facet,但现有两 facet 都测不到"该升级转介"这一档——知识侧部分覆盖但不可计量(转介选项散在 SATA 心理健康类题的正确答案里,无类别标签),行为侧零覆盖(拒答质量三档无转介维度,场景全为主动越狱)。

| facet | 格子 | 权重 | 档位/注记 |
|---|---|---|---|
| 安全知识 | eduguard_sata · SATA RFS | 0.35 | education_core;同源注记同上 |
| 对抗鲁棒 | eduguard_adversarial · 拒答质量 | 0.6 | diagnostic;主格 |
| 对抗鲁棒 | eduguard_adversarial · ASR | 0.45 | education_core |

### P23 命题与作业设计(2 facet)

facet 定义:**题目生成(正确性与质量)**——生成题干、选项、答案、干扰项本身的正确性与质量(答案唯一、无歧义、干扰项有效);**难度与目标对齐**——难度定标、区分度控制、与课标/考查目标对齐(空白)。二分对应测量学中项目技术质量与难度定标两类独立参数。

| facet | 格子 | 权重 | 档位/注记 |
|---|---|---|---|
| 题目生成(正确性与质量) | edubench · QG ×(清晰启发/情景元素) | 0.4 | education_core;两指标只测表达质量,正确性效度无格子——薄覆盖,整 P 参考值 |
| 难度与目标对齐 | (空白,暂未覆盖) | — | — |

## 三、Benchmark 列表

发布口径 5 个模型:MiniMax-M3 / MiniMax-M2.7 / deepseek-v4-pro / glm-5.2 / doubao-seed-2.0-pro。

| benchmark | 是什么 | 判分方式 | 喂给哪些 P | 现状/模型面 |
|---|---|---|---|---|
| ifeval | 541 条可验证指令 | 规则判分 | P01 | 齐 |
| mmlu_pro / ceval / agieval | 通识/学科选择题卷 | 精确匹配 | P01(门槛)、P05、P06 | 齐 |
| olympiadbench | 奥赛开放题(含多模态) | 符号等价判分 | P03、P05、P06 | 仅 2 个视觉模型 |
| mathvista | 数学图像理解 | 官方抽取+匹配 | P03、P05、P06 | 仅 1 个视觉模型 |
| k12vista | K12 学科图多步理解(600 题) | LLM 裁判(未校准) | P03、P05、P06 | 1 模型面(doubao 产物 summary 缺 totals 被排除) |
| mooccube_prereq | 课程先修关系推理(自建协议,300 题) | 规则判分 | P19、P05、P06 | 3 模型面(缺 M2.7 / doubao) |
| p07_selfcheck | 两轮自查(自建) | 规则判分 | P07、P08 | 齐 |
| p08_calibration / p08_abstention | 置信度校准 / 弃答(自建) | 规则判分 | P08、P07、P01 | 齐 |
| asap_2 | 学生作文评分 | QWK 对人类分 | P14、P02 | 齐 |
| sas_bench | 简答题评分(QWK/CCS/ECS 三指标) | 对人类标注一致性 | P14、P11(b/c)、P02、P05(仅 ECS)、P06 | 齐 |
| pedagogy_benchmark | 教学专业知识选择题(CDPK/SEND) | 精确匹配 | P05、P16d、P17 | CDPK/SEND 分列格无独立数据源,现只有合并卡计分 |
| edubench | 5 任务生成 × 12 裁判指标(指标级取分) | LLM 裁判(deepseek-v3.2,原论文设定) | P05、P06、P11c、P16d、P17、P18、P23(QG) | 11 模型,但面是 glm-5.1 而非发布口径的 glm-5.2 |
| mathtutorbench 家族(9 任务) | 数学辅导对话(解题/判对/定位/纠错/脚手架/教学法/苏格拉底) | 精确匹配 + LLM 裁判胜率 | P02、P05、P06、P07、P11(a/b/c)、P17、P18 | problem_solving / socratic 4 模型面,其余基本齐 |
| tutorbench | 多模态辅导质量 | LLM 裁判 | P03、P17、P18 | — |
| mmtutorbench | 多模态数学辅导(六维 rubric,770 题) | LLM 裁判 | P03、P17、P18 | 1 模型面 |
| bea2025_tutor / mrbench_tutor | 生成辅导回复,固定裁判逐维度标注 | LLM 裁判单维度分 | P11c、P17、P18(含 Tutor_Tone 鼓励占比)、P20(1−Offensive) | 3 模型面(已裁决不补跑) |
| bea2025_judge / mrbench_judge | 被测模型当裁判,对人类金标 | 一致性/F1 | P11c、P14、P20 | 均暂不计分 |
| eduguard_sata | 教学伤害多选(SATA,2,635 题) | 规则判分(RFS) | P20、P21、P22(三 P 同源) | 齐 |
| eduguard_adversarial | 对抗越狱 + 拒答质量(801 题) | 两阶段 LLM 裁判 | P20、P22 | 齐 |
| eduillustrate | 生成教学图示质量 | LLM 裁判八维 | P10、P18 | 4 模型面 |
| longtutor 三任务 | 长对话辅导(证据/诊断/教学) | 语义裁判 / 规则 F1 / LLM 裁判四维 | P02(evidence)、P16a 主 + P11c 副(diagnosis)、P17(teaching) | 3 模型面(已裁决不补跑) |

## 四、我们的创新与自建工作

这套映射不是把现成 benchmark 的榜单分数搬过来加权,以下工作是本仓库自己做的。

### 自建测验(4 个,均零标注成本、规则判分)

| 测验 | 测什么 | 协议 | 挂载 |
|---|---|---|---|
| p08_calibration | 置信度校准("自信地教错") | 复用精确匹配题 + 口头置信度,CWR/AUROC 合成 | P08 主格 |
| p08_abstention | 能力性弃答("不会时说不会") | UMWP/TreeCut 不可答题,平衡弃答分 | P08 主格 |
| p07_selfcheck | 两轮自查 | 先答题、再无提示复查;headline 与首轮正确率解耦 | P07 主格 |
| mooccube_prereq | 知识结构层路径规划 | MOOCCube 905 条专家先修边当金标,自建 200 道先修选择 + 100 道排序,随机基线校正 | P19 首个测量 |

P01/P02/P07/P08 在常规做法里全是"搭车分",这四个测验加上 IFEval 接入和 longtutor 挂载,把其中三个 P 变成了直接测量。

### 接入并改造的公开 benchmark(17 个 adapter,30+ 个评测变体)

统一 eval harness(`scripts/eval/`,load → call → extract → score → report,断点续跑、逐 benchmark 稳定产物目录)下自行移植:mathtutorbench 家族 9 任务(**win-rate 判分用 LLM-as-judge 替换官方 GPU 奖励模型**,并做裁判校准实验)、EduGuard 两阶段安全测验、MRBench / BEA2025 双模式(被测模型当裁判的校准模式 + 生成后固定裁判逐维度标注模式)、LongTutor 三任务(官方仓库只有 pipeline 脚本,移植成可复现 adapter)、MMTutorBench 多模态辅导、IFEval 官方 checker、K12Vista、MathVista/MMLU-Pro/AGIEval/OlympiadBench/C-Eval(判分逻辑逐个从官方 repo 移植)。EduBench 则是导入同事的全量原始判分(11 模型 × 3,797 题 × 12 指标)后做题级重分析。

### 方法学(相对"拿榜单分加权"的常规做法)

1. **预注册测量模型**:每个 P 先声明 reflective/formative 与 facet 结构(`data/mapping_measurement_model_v*.json`),声明先于数据,防止看完分数再编结构;见数后的构念修订必须带裁决记录与方法学披露。
2. **facet 级划分规则成文**:边界可判 + 构念不重复;过于擦边的证据格宁缺勿滥(与 P 级拆分准入规则并列,facet 争议直接引用规则裁决)。
3. **映射效度检查**(13 号产物):每个格子算跨模型区分度、每对同 P 格子算跨模型相关,给 validated/flagged/受限评级——权重不再是拍的,错挂能被数据打回。
4. **换裁判实验**(M2):同一批回答换两个裁判重判,把 LLM 裁判指标二分为"真测量"(个性化/动机/高阶思维,ρ 0.6–0.8)与"裁判噪声"(错误识别,ρ≤0.14)。
5. **题级证据**:"会答题≠会教"从口号变成数字——同一批回答内,事实准确性与个性化/动机引导的题内相关约等于零。
6. **(任务×指标)级取分 + 死格子剔除**:LLM 裁判 benchmark 不用任务均分,按原生指标逐格挂 P;题级 SD<0.5 的死格子不进映射。
7. **一份标注多个统计量**:同一裁判标注按构念取不同统计量分挂不同 P(如 Tutor_Tone:P20 取 1−Offensive 测边界,P18 取鼓励占比测支持),不重复计数。
8. **拆分准入规则**:子能力拆成独立 P 需四类 benchmark 无关依据取二;benchmark 的存在永远不构成拆分依据。
9. **facet 聚合**:facet 内按格子权重加权、跨 facet 等权,formative 声明真正落进分数。
10. **证据分层**:education_core / diagnostic / foundation_gate(降权 0.45)/ excluded_judge_task 四档,通识题永远压不过教学核心证据。
11. **研究层/用户层分离**:加权与统计检验留研究层;用户版每 P 一个分数 + 三档白话可信度。
12. **裁判工程纪律**:裁判原文全部落盘、取消 unparsed 中间态、全链路不设 max_tokens 上限(避免推理模型被饿死产生假失败)。

## 五、未完成 TODO

### 数据缺口(挂载已定,分数不全)

| 项 | 现状 | 补法 |
|---|---|---|
| mooccube_prereq 模型面 | 3/5(缺 M2.7、doubao) | 300 题规则判分零裁判,跑起来便宜,优先补 |
| k12vista 模型面 | 1/5;doubao 产物 summary 缺 totals 被收录规则排除 | 修复 doubao summary;补视觉模型(注意 deepseek-v4-pro 收图不报错但看不见) |
| mmtutorbench 模型面 | 1/5(770 题全量仅 MiniMax-M3) | 补跑,需 LLM 裁判 |
| mathvista / olympiadbench 面窄 | 1 / 2 个视觉模型 | P03 解题图像 facet 横向比不了,补视觉模型 |
| longtutor 三任务、bea2025_tutor、mrbench_tutor | 3 模型面,**已裁决不补跑** | 若未来要用这些格子做排名再回头补 |
| edubench 模型错位 | 面是 glm-5.1 而非发布口径 glm-5.2 | 接受错位注记,或自跑 glm-5.2 的 edubench 面 |
| pedagogy_benchmark CDPK/SEND 分列 | 两个分列格无独立数据源,只有合并卡计分 | 找/跑分列数据,恢复 P05 教学知识、P16d、P17 制定的分辨率 |
| 裁判 error 未清 | deepseek-v4-flash、doubao-lite 在 mathtutorbench win-rate 有残余 error 行 | 非发布模型不挡路;扩面时先断点续判 |

### 构念缺口(空白 facet / 空白 P)

| 项 | 缺什么 | 候选路线 |
|---|---|---|
| P09 两 facet | 教育场景 agent 评测领域空白 | 工具侧自建小任务(调计算器/画图/检索课程库);长程侧等社区;通用 GAIA/tau-bench 类只能当门槛 |
| P15 | 领域空白,暂不拆 facet | 需要时自建:真实学生作答 + 模型改写对照组做判别任务(AUC) |
| P16b 误概念识别 | 空 facet | Eedi 误概念标注(NeurIPS 2024 竞赛)、Bridge(700 段真实辅导对话) |
| P16c 情感与参与识别 | 空 facet | IntrEx(EMNLP 2025)可直接做判别任务 |
| P17 教学目标对齐 | 空 facet | 自建协议(给定教学目标+学情,判断教学回复是否服务目标),或找含课标标注的教案对话数据 |
| P14 分析式评分单源 + 生成 rubric 空白 | CCS 一格计分;rubric 无数据 | judge 校准结论落地后激活 bea/mrbench_judge 即转多源;rubric 需自建对专家 rubric 一致性协议 |
| P21 严重度判断 + 独立证据为零 | 空 facet;唯一格子与 P20/P22 同源 | 需含严重度分级标注的学生风险对话数据;R10 SATA 类别标注先解同源 |
| P22 升级转介深度缺口 | 知识侧不可计量、行为侧零覆盖 | SATA 类别标注时标出"正确答案含转介"子集单独取分;adversarial 扩"被动流露风险需主动升级"场景 |
| P23 正确性效度 + 难度目标对齐 | QG 格只测表达质量;第二 facet 空白 | Eedi 干扰项-误概念数据测干扰项设计;答案正确性自建"生成题自答一致性"规则协议;难度定标用真实作答通过率校验 |
| P03 视频/音频 | 空 facet | 多模态教育视频理解基准未接入(候选 SciVideoBench,需 harness 支持视频输入) |
| P10 时序与交互产物 | 空 facet | InteractScience(生成交互教学网页)是候选 |
| P02 区分度 | 直接测量但三模型分数挤在一起 | 补更难的长上下文任务,或加模型面验证是否真天花板 |
| P20/P21/P22 知识 facet 同源 | 三 P 共用一份 SATA | R10:SATA 类别标注(LLM 粗标+抽检)拆出独立证据,排发布后 |

### 流程性(M4 关键路径)

死格子(题级 SD<0.5)剔除与 edubench 指标级【草案】权重核对 → v 版本对比 + 排名稳定性 → M4 双报告(研究版/用户版)。发布目标 7 月底。详见 `doc/rebenchmark_workstream_overview_2026-07-12.md`。
