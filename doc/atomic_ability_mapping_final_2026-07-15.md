# 原子能力与 Benchmark 映射(定稿,2026-07-15;2026-07-16 三个待确认项已裁决;同日 R17 裁决 P11/P12/P13 合并为 P11 错误诊断;同日 R18 裁决 P17 重构、P23 测评设计与出题新设、全 facet 补含义)

这是当前的最终结论:原子能力清单是什么、每个能力由哪些 benchmark 的哪些维度测量、权重多少。不含历史沿革(变化记录见 `doc/benchmark_ability_mapping_v2_2026-07-15.md`)。机器可读版:`data/mapping_measurement_model_v4.json`(与本文档同步,2026-07-16;v3 为 R18 前快照)。

约定:权重是 facet 内的相对重要度,不归一。格子写法为 `benchmark · 取分维度`。原三处 ※ 待确认项已于 2026-07-16 裁决完毕(文末有裁决记录),全表均为定稿。

## 原子能力清单(20 项)

| P | 名称 | 一句话定义 | 测量成熟度 |
|---|---|---|---|
| P01 | 指令与约束遵循 | 按显式指令和格式/行为约束产出 | 直接测量(规则判分) |
| P02 | 长上下文与证据定位 | 在长材料/长对话中定位并引用相关证据 | 直接测量·区分度待验证(2026-07-16 挂 longtutor_evidence) |
| P03 | 多模态理解 | 读懂教育场景中的图像/图表等非文本材料并据此推理 | 多源(学科图表 facet 为参考值) |
| P05 | 知识调用与掌握 | 学科知识与教学专业知识的正确调用 | 多源·成熟(知识簇天花板,门槛性质) |
| P06 | 推理与生成 | 解题推理与约束下的生成推理 | 多源·成熟 |
| P07 | 自我校验与修正 | 复查自己的输出,发现并修正错误 | 直接测量 |
| P08 | 置信度校准与弃答 | 自信程度与正确率一致;不会时主动弃答 | 直接测量(双任务) |
| P09 | 工具使用与长程智能体执行 | 调用工具、完成多步长程任务 | **空白,暂未覆盖** |
| P10 | 多模态教学产物生成 | 生成图示等非文本教学产物 | 单源 |
| P11 | 错误诊断 | 诊断学生错误:判对错、定位错误步骤、解释错因/误概念(三 facet,R17 合并) | 判对/定位 facet 单源+,归因 facet 多源 |
| P14 | 主观题 rubric 评分能力 | 依据评分标准评判主观作答与教学回复 | 学业评分多格;评判 facet 暂不计分(生成 rubric 已迁 P23) |
| P15 | 学术诚信与作答真实性判定 | 识别抄袭、代写等真实性问题 | **空白,暂未覆盖** |
| P16 | 学习者画像建模 | 从交互中建模学生的水平、需求与特征 | 弱(4 个子能力覆盖 2 个;P16a 2026-07-16 起有分) |
| P17 | 个性化教学策略选择 | 对齐教学目标与学生状态,制定并执行合适的教学策略 | 多源·证据最厚(目标对齐 facet 空白) |
| P18 | 适配性解释与反馈生成 | 生成适配学生的解释、引导与反馈 | 多源·证据最厚 |
| P19 | 学习路径规划(知识结构层) | 基于知识先修结构规划学习顺序 | 单源·参考值(自建协议) |
| P20 | 教育角色边界判断 | 守住教育者的角色与行为边界 | 双源(知识 facet 与 P21/P22 同源) |
| P21 | 学生风险识别 | 识别学生消息中的风险信号 | 双源(同上) |
| P22 | 安全处置选择 | 对风险与越界请求选择正确处置方式 | 双源(同上) |
| P23 | 测评设计与出题 | 设计有效的测评:出题、设计干扰项、生成评分标准 | 单源·薄(仅表达质量维度;测评效度空白,R18 新设) |

五条解释性口径:

- **P03 覆盖全部多模态理解**(不分深浅——难度用证据标签表达,不是构念维度),按材料类型分 facet。
- **P11 覆盖全部错误诊断**(判对→定位→归因是同一诊断任务的深度梯度,不是三个独立构念——与 P03 合并同一口径),按诊断深度分 facet:P11a 作答正误判定 / P11b 错误位置定位 / P11c 错因归因。P12/P13 编号墓碑保留不复用。与 P14 的边界:P11 是对着参考解找错、解释错(诊断);P14 是把作答证据映射到 rubric 分档(量尺映射),机制不同。
- **P19 只管知识结构层**。"针对某个学生当前状态的个性化路径规划"是 P16 × P19 的组合能力,不是 P19 的缺口。
- **教师协作不设独立 P**(R18):遵循教师设定的教学方案 = P01 × P17,该转交人类时转交 = P22 的一种处置方式,向教师报告学情 = P16 的输出侧,守住辅助者定位 = P20。残余机制("在教师主导的工作流中理解教师意图、不越俎代庖")目前只有人机协同教学(co-orchestration)一类理论依据,不满足拆分准入规则(至少两类 benchmark 无关依据);已记 `benchmark-todo.md`,若未来教师标准单列或出现专门评测再重审。
- **测不了 ≠ 不存在**:P09/P15 及各空白 facet 保留在清单里标"暂未覆盖",清单不随测量可行性伸缩。

## 逐能力映射明细

### P01 指令与约束遵循

| 格子 | 权重 | 性质 |
|---|---|---|
| ifeval · prompt 严格准确率 | 1.0 | 直接测量,规则判分无裁判 |
| agieval · 格式遵循 | 0.2 | 门槛 |
| ceval · 格式遵循 | 0.15 | 门槛 |
| mmlu_pro · 格式遵循 | 0.1 | 门槛 |
| p08_abstention · 弃答约束遵循 | 0.15 | diagnostic |

### P02 长上下文与证据定位(整体为代理证据)

| 格子 | 权重 | 性质 |
|---|---|---|
| longtutor_evidence · 长对话证据抽取 | 0.7 | 直接测量(2026-07-16 裁决定稿;三模型面 0.787/0.807/0.791 区分度待验证,报告按此表述) |
| asap_2 · 作文整体 QWK | 0.2 | 代理(搭车) |
| sas_bench · QWK / CCS | 0.15 / 0.2 | 代理(搭车) |
| mathtutorbench_solution_correctness / mistake_location | 0.15 / 0.2 | 代理(搭车) |

### P03 多模态理解(facet 按材料类型)

facet 含义:**解题图像**——读题目自带的几何图/函数图/图形化条件并据此解题;**学科图表**——读学科教学材料中的图表(实验装置、地图、统计图等)做多步理解;**教学场景图文**——辅导对话中理解学生发来的拍照/手写/截图等混合材料并作教学响应;**视频/音频**——理解教学视频与音频材料。

| facet | 格子 | 权重 | 性质 |
|---|---|---|---|
| 解题图像 | mathvista · 任务/题型准确率 | 0.35 | diagnostic |
| 解题图像 | olympiadbench · 多模态子集准确率 | 0.2 | 门槛 |
| 学科图表 | k12vista · 学科图多步理解 | 0.55 | diagnostic;裁判未校准,仅 4 个视觉模型,参考值 |
| 教学场景图文 | tutorbench · 多模态辅导质量 | 0.25 | education_core |
| 教学场景图文 | mmtutorbench · 多模态辅导六维 | 0.3 | diagnostic |
| 视频/音频 | (空白,暂未覆盖) | — | — |

### P05 知识调用与掌握(三 facet)

facet 含义:**学科知识调用**——答题时正确调用学科事实、概念与方法;**教学专业知识**——教学法、课程与特殊教育需求等教师专业知识的掌握;**生成中的知识运用**——生成解释、评分、教学内容时不出知识性错误。

| facet | 格子 | 权重 |
|---|---|---|
| 学科知识调用 | mmlu_pro / ceval · 总分 | 0.6 / 0.6 |
| 学科知识调用 | agieval · 总分 | 0.35 |
| 学科知识调用 | mathtutorbench_problem_solving | 0.3 |
| 学科知识调用 | olympiadbench · 总分 | 0.25 |
| 学科知识调用 | mathvista · 总分 | 0.2 |
| 学科知识调用 | mooccube · 先修推理 | 0.2 |
| 学科知识调用 | k12vista | 0.15 |
| 教学专业知识 | pedagogy_benchmark · CDPK / SEND / 合并卡 | 0.45 / 0.35 / 0.4 |
| 生成中的知识运用 | edubench · 领域知识准确性 | 0.35 |
| 生成中的知识运用 | edubench · 基础事实准确性 | 0.3 |
| 生成中的知识运用 | mathtutorbench_pedagogy ±hard | 0.25 |
| 生成中的知识运用 | sas_bench · ECS | 0.2 |
| 生成中的知识运用 | asap_2 · QWK / sas_bench · QWK | 0.15 / 0.15 |
| 生成中的知识运用 | mathtutorbench_scaffolding ±hard | 0.15 |

### P06 推理与生成(两 facet)

facet 含义:**解题推理**——面向标准答案的多步解题推理;**生成与归因推理**——生成教学内容、解释错因时的推理严谨性与思维引导深度。

| facet | 格子 | 权重 |
|---|---|---|
| 解题推理 | mathtutorbench_problem_solving | 0.6 |
| 解题推理 | olympiadbench · 总分 | 0.55 |
| 解题推理 | agieval / mathvista · 总分 | 0.45 / 0.45 |
| 解题推理 | mmlu_pro / ceval · 总分 | 0.3 / 0.25 |
| 解题推理 | k12vista | 0.3 |
| 解题推理 | mooccube · 先修推理 | 0.1 |
| 生成与归因推理 | edubench · 推理过程严谨性 | 0.35 |
| 生成与归因推理 | edubench · 高阶思维能力培养 | 0.2 |
| 生成与归因推理 | mathtutorbench_mistake_correction | 0.2 |
| 生成与归因推理 | sas_bench · ECS | 0.1 |

### P07 自我校验与修正

| 格子 | 权重 | 性质 |
|---|---|---|
| p07_selfcheck · 两轮自查(改对率/改错率合成) | 0.85 | 直接测量 |
| mathtutorbench_solution_correctness | 0.25 | 代理 |
| p08_calibration · 校准合成分 | 0.2 | 代理 |
| mathtutorbench_problem_solving | 0.1 | 代理 |

### P08 置信度校准与弃答(两 facet)

facet 含义:**置信度校准**——表达的自信程度与实际正确率一致(不自信地教错);**能力性弃答**——面对不可答或超出能力的问题主动说不会。

| facet | 格子 | 权重 | 性质 |
|---|---|---|---|
| 置信度校准 | p08_calibration · CWR/AUROC 合成 | 0.8 | 直接测量 |
| 置信度校准 | p07_selfcheck | 0.15 | 相邻证据 |
| 能力性弃答 | p08_abstention · 平衡弃答分 | 0.85 | 直接测量 |

### P09 工具使用与长程智能体执行 / P15 学术诚信与作答真实性判定

无挂载。领域空白,报告标"暂未覆盖"。

### P10 多模态教学产物生成

| 格子 | 权重 |
|---|---|
| eduillustrate · 视觉讲解八维 | 0.45 |

### P11 错误诊断(三 facet,R17 合并)

facet 含义:**P11a 作答正误判定**——判断学生作答对不对;**P11b 错误位置定位**——指出错误发生在解答的哪一步;**P11c 错因归因**——解释为什么错(错因类别、误概念)。

| facet | 格子 | 权重 | 性质 |
|---|---|---|---|
| P11a 作答正误判定 | mathtutorbench_solution_correctness | 0.6 | education_core |
| P11b 错误位置定位 | mathtutorbench_mistake_location | 0.7 | education_core |
| P11b 错误位置定位 | sas_bench · CCS | 0.25 | education_core |
| P11c 错因归因 | sas_bench · ECS(与人类专家错因标签一致性) | 0.7 | 核心证据 |
| P11c 错因归因 | bea2025_tutor · Mistake_Identification | 0.25 | LLM 裁判单维度分 |
| P11c 错因归因 | mrbench_tutor · Mistake_Identification | 0.25 | 同上 |
| P11c 错因归因 | edubench · 错误识别与纠正 | 0.25 | 方法学局限注记:换裁判分歧大 |
| P11c 错因归因 | mathtutorbench_mistake_correction | 0.2 | 只测改对与否,部分相关 |
| P11c 错因归因 | longtutor_diagnosis · 四类知识状态诊断 macro-F1 | 0.1 | 副挂(2026-07-16 裁决:标签名义是错因类别,但归因证据源是交互历史特征而非作答内容,与 ECS 锚动用的能力不同,仅作相邻证据;主挂 P16a) |
| P11c 错因归因 | bea2025_judge / mrbench_judge | 0.3 / 0.25 | 暂不计分(judge 任务) |

两条随迁注记:①longtutor_diagnosis 不挂 P11b——语义核实后,任务输入里没有任何解题步骤可供定位(原"不挂 P12"裁决);②R17 附带删除原 P11 内两个同源重复格:mathtutorbench_mistake_location 0.1 搭车格(P11b 主格已持有)、bea2025_judge 0.25 暂不计分占位格(P11c 已持有同一占位),避免同 P 跨 facet 双计同一数据源。

### P14 主观题 rubric 评分能力(两 facet,R18 起)

facet 含义:**学业作答评分**——按评分标准给学生作文/简答打分,以与人类评分的一致性计;**教学回复评判**——作为裁判逐维度评判教学回复质量,以与人类标注的一致性计。原第三 facet"生成 rubric"已随 R18 迁入 P23(测评设计与出题)。

| facet | 格子 | 权重 | 性质 |
|---|---|---|---|
| 学业作答评分 | sas_bench · QWK / CCS | 0.7 / 0.55 | education_core |
| 学业作答评分 | asap_2 · QWK | 0.65 | education_core |
| 教学回复评判 | bea2025_judge · 四维判卷 | 0.45 | 暂不计分 |
| 教学回复评判 | mrbench_judge · 八维判卷 | 0.45 | 暂不计分 |

### P16 学习者画像建模(声明 4 个子能力,现覆盖 2 个)

facet 含义:**P16a 知识状态估计**——从作答历史判断学生会什么、不会什么;**P16b 误概念识别**——识别学生持有的具体误概念;**P16c 情感与参与识别**——识别学生情绪、动机与参与度信号;**P16d 支持需求判断**——判断学生需要哪类支持(含特殊教育需求)。

| facet(子能力) | 格子 | 权重 |
|---|---|---|
| P16a 知识状态估计 | longtutor_diagnosis · 四类知识状态诊断 macro-F1 | 0.3(参考值) |
| P16d 支持需求判断·画像知识 | pedagogy_benchmark · SEND / 合并卡 | 0.35 / 0.3 |
| P16d 支持需求判断·画像应用 | edubench · 个性化适应与学习支持 | 0.3 |
| P16b 误概念识别 / P16c 情感与参与识别 | (空白,暂未覆盖) | — |

P16a 挂载依据(2026-07-16 裁决):longtutor_diagnosis 的输入是 199 条历史作答记录(题面+知识点+时间+对错)+ 当前题面,四个标签(Recall Failure / Conceptual Gap / Procedural Error / Transfer Deficit)是认知层失败机制,归因证据源是交互历史——正对"从作答历史判断学生会什么、不会什么"这个此前零覆盖的子能力。方法学注记:①类别不平衡(Procedural 506/1000),多数类基线 accuracy 0.506 高于三模型的 0.35–0.44,headline 用 macro-F1;②金标为特征决策矩阵 + 人工修订,非独立盲标,权重保守、性质参考值;③仅 3 个模型面,不补跑。

### P17 个性化教学策略选择(三 facet,R18 重构)

facet 含义:**教学目标对齐**——教学决策与课标/教学目标及学生当前状态保持一致,教的东西服务于既定目标;**教学策略制定**——面对具体学生情境选出或制定合适的教学策略(R18 由"教学策略知识"改名:facet 按构念命名,原名是测量层命名);**教学策略执行**——在真实辅导对话/生成中把策略落地做出来。

制定 facet 测量注记:现仅有情境化选择题一种测量方式("教师面对 X 情况,最佳做法是什么"),会选对选项与面对真学生制定出合适策略之间存在 knowing-doing gap,成熟度按陈述性代理表述。

| facet | 格子 | 权重 |
|---|---|---|
| 教学目标对齐 | (空白,暂未覆盖——现有格子无一测"教学行为是否服务于既定教学目标":longtutor_teaching 的 strategy_alignment 锚的是学生状态/历史,不是课标与目标) | — |
| 教学策略制定 | pedagogy_benchmark · CDPK / SEND / 合并卡 | 0.35 / 0.3 / 0.3 |
| 教学策略执行 | mathtutorbench_socratic · 提问式引导 | 0.65 |
| 教学策略执行 | mathtutorbench_scaffolding ±hard | 0.5 |
| 教学策略执行 | mathtutorbench_pedagogy ±hard | 0.45 |
| 教学策略执行 | edubench · 个性化适应与学习支持 | 0.4 |
| 教学策略执行 | tutorbench · 辅导质量 | 0.35 |
| 教学策略执行 | bea2025_tutor · Providing_Guidance | 0.3 |
| 教学策略执行 | mrbench_tutor · Providing_Guidance | 0.3 |
| 教学策略执行 | mmtutorbench · 六维合成 | 0.3 |
| 教学策略执行 | longtutor_teaching · strategy_alignment + history_utilization | 0.3(2026-07-16 裁决定稿,重算验证已完成:三模型 valid 1001,strategy_alignment 3.68–4.13 有区分度) |
| 教学策略执行 | edubench · 情景元素融合 | 0.25 |

### P18 适配性解释与反馈生成(两 facet)

facet 含义:**对话式反馈与引导**——对学生当下作答/提问的即时响应(解释、引导、鼓励、纠错反馈);**教学产物生成**——生成教材、讲义、图解等教学材料(出题已随 R18 拆出至 P23)。

| facet | 格子 | 权重 | 性质 |
|---|---|---|---|
| 对话式反馈与引导 | tutorbench / mmtutorbench | 0.4 / 0.4 | |
| 对话式反馈与引导 | edubench · 动机引导与积极反馈 | 0.35 | |
| 对话式反馈与引导 | mathtutorbench_mistake_correction / scaffolding ±hard / socratic | 0.35 | |
| 对话式反馈与引导 | edubench · 表达清晰简洁启发 | 0.3 | |
| 对话式反馈与引导 | mathtutorbench_pedagogy ±hard | 0.3 | |
| 对话式反馈与引导 | edubench · 高阶思维能力培养 | 0.25 | |
| 对话式反馈与引导 | bea2025_tutor · Actionability | 0.2 | 该维度裁判校准弱(κ0.22),低权重+方法学注记 |
| 对话式反馈与引导 | mrbench_tutor · Actionability | 0.2 | 同上 |
| 对话式反馈与引导 | edubench · 语气风格一致性 | 0.1 | |
| 对话式反馈与引导 | eduguard_adversarial · 拒答质量 | 0.1 | 主挂 P22 |
| 教学产物生成 | edubench · TMG/PCC 任务 ×(清晰启发/情景元素) | 0.4 | R18:QG 任务拆出迁 P23 |
| 教学产物生成 | eduillustrate · 视觉讲解八维 | 0.3 | |

### P19 学习路径规划(知识结构层)

| 格子 | 权重 | 性质 |
|---|---|---|
| mooccube · 先修关系推理 | 0.7 | 规则判分零裁判;自建协议、无公开基线,benchmark 权重 0.7,参考值 |

### P20 教育角色边界判断(两 facet)

facet 含义:**安全知识**——知道教育场景中哪些行为构成伤害/越界(选择题);**边界行为**——对抗压力下实际守住教育者的角色与行为边界。

| facet | 格子 | 权重 | 性质 |
|---|---|---|---|
| 安全知识 | eduguard_sata · SATA RFS | 0.35 | 与 P21/P22 同源,不构成互证 |
| 安全知识 | mrbench_judge | 0.3 | 暂不计分 |
| 边界行为 | eduguard_adversarial · ASR | 0.3 | |
| 边界行为 | mrbench_tutor · Tutor_Tone | 0.25 | |
| 边界行为 | eduguard_adversarial · 拒答质量 | 0.15 | |

### P21 学生风险识别(两 facet)

facet 含义:**安全知识**——识别学生消息中风险信号的知识面(选择题);**对抗鲁棒**——越狱/对抗话术下仍能识别风险。

| facet | 格子 | 权重 | 性质 |
|---|---|---|---|
| 安全知识 | eduguard_sata · SATA RFS | 0.3 | 同源注记同上 |
| 对抗鲁棒 | eduguard_adversarial · ASR | 0.25 | |

### P22 安全处置选择(两 facet)

facet 含义:**安全知识**——知道对风险与越界请求的正确处置方式(选择题);**对抗鲁棒**——越狱攻击下实际选择正确处置(拒答且拒得有质量)。

| facet | 格子 | 权重 | 性质 |
|---|---|---|---|
| 安全知识 | eduguard_sata · SATA RFS | 0.35 | 同源注记同上 |
| 对抗鲁棒 | eduguard_adversarial · 拒答质量 | 0.6 | 主格 |
| 对抗鲁棒 | eduguard_adversarial · ASR | 0.45 | |

### P23 测评设计与出题(两 facet,R18 新设)

facet 含义:**题目生成**——生成可用的测评题目(题干、选项、答案、干扰项);**生成 rubric**——为主观任务生成评分标准(自 P14 迁入)。

| facet | 格子 | 权重 | 性质 |
|---|---|---|---|
| 题目生成 | edubench · QG 任务 ×(清晰启发/情景元素) | 0.4 | 自 P18 拆出;两指标只测题目的表达质量,测评效度(答案唯一正确、难度定标、干扰项对应真实误概念、对齐考查目标)无任何格子——整 P 参考值 |
| 生成 rubric | (空白,暂未覆盖,自 P14 迁入) | — | — |

## 我们的创新与自建工作

这套映射不是把现成 benchmark 的榜单分数搬过来加权,以下工作是本仓库自己做的。

### 自建测验(4 个,均零标注成本、规则判分)

| 测验 | 测什么 | 协议 | 挂载 |
|---|---|---|---|
| p08_calibration | 置信度校准("自信地教错") | 复用精确匹配题 + 口头置信度,CWR/AUROC 合成 | P08 主格 |
| p08_abstention | 能力性弃答("不会时说不会") | UMWP/TreeCut 不可答题,平衡弃答分 | P08 主格 |
| p07_selfcheck | 两轮自查 | 先答题、再无提示复查;headline=0.5×改对率+0.5×(1−改错率),与首轮正确率解耦 | P07 主格 |
| mooccube_prereq | 知识结构层路径规划 | MOOCCube 905 条专家先修边当金标,自建 200 道先修选择 + 100 道排序,随机基线校正 | P19 首个测量 |

P01/P02/P07/P08 在此前的常规做法里全是"搭车分"(别的任务顺带算出来的),这四个测验加上 IFEval 接入和 longtutor 挂载,把其中三个 P 变成了直接测量。

### 接入并改造的公开 benchmark(17 个 adapter,30+ 个评测变体)

统一 eval harness(`scripts/eval/`,load → call → extract → score → report,断点续跑、逐 benchmark 稳定产物目录)下自行移植:mathtutorbench 家族 9 任务(**win-rate 判分用 LLM-as-judge 替换官方 GPU 奖励模型**,并做了裁判校准实验)、EduGuard 两阶段安全测验、MRBench / BEA2025 双模式(被测模型当裁判的校准模式 + 生成后固定裁判逐维度标注模式)、LongTutor 三任务(官方仓库只有 pipeline 脚本,移植成可复现 adapter)、MMTutorBench 多模态辅导、IFEval 官方 checker、K12Vista、MathVista/MMLU-Pro/AGIEval/OlympiadBench/C-Eval(判分逻辑逐个从官方 repo 移植,非自造)。EduBench 则是导入同事的全量原始判分(11 模型 × 3,797 题 × 12 指标)后做题级重分析。

### 方法学(相对"拿榜单分加权"的常规做法)

1. **预注册测量模型**:每个 P 先声明 reflective/formative 与 facet 结构(`data/mapping_measurement_model_v*.json`),声明先于数据,防止看完分数再编结构。
2. **映射效度检查**(13 号产物):每个格子算跨模型区分度、每对同 P 格子算跨模型相关,给 validated/flagged/受限评级——权重不再是拍的,错挂能被数据打回。
3. **换裁判实验**(M2):同一批回答换两个裁判重判,把 LLM 裁判指标二分为"真测量"(个性化/动机/高阶思维,ρ 0.6-0.8)与"裁判噪声"(错误识别,ρ≤0.14)——不做这一步会把噪声当宝贝挂进映射。
4. **题级证据**:"会答题≠会教"从口号变成数字——同一批回答内,事实准确性与个性化/动机引导的题内相关约等于零。
5. **(任务×指标)级取分 + 死格子剔除**:LLM 裁判 benchmark 不用任务均分,按原生指标逐格挂 P;题级 SD<0.5 的死格子不进映射。
6. **拆分准入规则**:子能力拆分需理论/失败机制/教师标准/同源数据四类 benchmark 无关依据中至少两个支持;benchmark 的存在永远不构成拆分依据(P17b 苏格拉底提问因此被砍,是反面教材)。
7. **facet 聚合**:facet 内按格子权重加权、跨 facet 等权,formative 声明真正落进分数(P16 不会被单一 facet 淹没)。
8. **证据分层**:education_core / diagnostic / foundation_gate(门槛,降权 0.45)/ excluded_judge_task 四档,通识题永远压不过教学核心证据。
9. **研究层/用户层分离**:加权与统计检验留研究层;用户版每 P 一个分数 + 三档白话可信度。
10. **裁判工程纪律**:裁判原文全部落盘(解析 bug 可零成本重算)、取消 unparsed 中间态(只有真 label 或可重判的 error)、全链路不设 max_tokens 上限(避免推理模型被饿死产生假失败)。

## 附录:Benchmark 索引(每个测验一行)

| benchmark | 是什么 | 判分方式 | 喂给哪些 P |
|---|---|---|---|
| ifeval | 541 条可验证指令 | 规则判分 | P01 |
| mmlu_pro / ceval / agieval | 通识/学科选择题卷 | 精确匹配 | P01(门槛)、P05、P06 |
| olympiadbench | 奥赛开放题(含多模态) | 符号等价判分 | P03、P05、P06 |
| mathvista | 数学图像理解 | 官方抽取+匹配 | P03、P05、P06 |
| k12vista | K12 学科图多步理解 | LLM 裁判(未校准) | P03、P05、P06 |
| mooccube | 课程先修关系推理(自建协议) | 规则判分 | P19、P05、P06 |
| p07_selfcheck | 两轮自查 | 规则判分 | P07、P08 |
| p08_calibration / p08_abstention | 置信度校准 / 弃答 | 规则判分 | P08、P07、P01 |
| asap_2 | 学生作文评分 | QWK 对人类分 | P14、P02、P05 |
| sas_bench | 简答题评分(QWK/CCS/ECS 三指标) | 对人类标注一致性 | P14、P11(b 定位/c 归因)、P02、P05、P06 |
| pedagogy_benchmark | 教学专业知识选择题(CDPK/SEND) | 精确匹配 | P05、P16、P17 |
| edubench | 5 任务生成 × 12 裁判指标(取指标级分) | LLM 裁判(deepseek-v3.2,原论文设定) | P05、P06、P11c、P16、P17、P18、P23(QG) |
| mathtutorbench 家族(9 任务) | 数学辅导对话(解题/判对/定位/纠错/脚手架/教学法/苏格拉底) | 精确匹配 + LLM 裁判胜率 | P02、P05、P06、P07、P11(a/b/c)、P17、P18 |
| tutorbench | 多模态辅导质量 | LLM 裁判 | P03、P17、P18 |
| mmtutorbench | 多模态数学辅导(六维 rubric) | LLM 裁判 | P03、P17、P18 |
| bea2025_tutor / mrbench_tutor | 生成辅导回复,固定裁判逐维度标注 | LLM 裁判单维度分 | P11c、P17、P18、P20(mrbench) |
| bea2025_judge / mrbench_judge | 被测模型当裁判,对人类金标 | 一致性/F1 | P11c、P14、P20(均暂不计分) |
| eduguard_sata | 教学伤害多选(SATA) | 规则判分(RFS) | P20、P21、P22(同源) |
| eduguard_adversarial | 对抗越狱 + 拒答质量 | 两阶段 LLM 裁判 | P20、P21、P22、P18 |
| eduillustrate | 生成教学图示质量 | LLM 裁判八维 | P10、P18 |
| longtutor 三任务 | 长对话辅导(证据/诊断/教学) | 语义裁判 / 规则 F1 / LLM 裁判四维 | P02(evidence)、P16a 主 + P11c 副(diagnosis)、P17(teaching)——2026-07-16 裁决定稿 |

## 裁决记录(2026-07-16,原三处待确认项全部落定)

1. **longtutor_evidence → P02(0.7),挂**。P02 由纯代理转直接测量;三模型面 accuracy 0.787/0.807/0.791 挤得很紧,成熟度按"直接测量·区分度待验证"表述,等 13 号检查配对结果。
2. **longtutor_diagnosis → P16a 主挂(0.3,参考值)+ P13 副挂(0.1),不挂 P12**。语义核实:输入无解题步骤(P12 排除);四标签是认知层失败机制、归因证据源是交互历史特征而非作答内容,构念正主是 P16a"知识状态估计"(此前零覆盖);与 sas_bench ECS 动用的能力不同,P13 仅作相邻证据副挂。附带方法学注记(类别不平衡、金标决策矩阵模板化风险)见 P16 小节。
3. **longtutor_teaching → P17 执行 facet(0.3),挂**。前置条件(4 维全 0 bug 修复后重算验证)已满足:三个模型 valid_judgements 均 1001,strategy_alignment 3.68–4.13 有区分度。取 strategy_alignment + history_utilization 两维,coherence/appropriateness 不入分。

同日决定:**longtutor 三任务与 mrbench_tutor / bea2025_tutor 的模型面缺口不补跑**(longtutor 缺 MiniMax-M2.7、doubao-seed-2.0-pro;mrbench/bea 缺 deepseek-v4-pro、doubao-seed-2.0-pro 的生成),v2 聚合与 13 号检查按 3 模型面注记。

机器可读落盘:`data/mapping_measurement_model_v2.json`(2026-07-16,含全部 R1-R16 裁决 + 本页三项)。

## 裁决记录 R17(2026-07-16,P11/P12/P13 合并)

**原 P11 作答正误判定 / P12 错误位置定位 / P13 错因归因合并为 P11「错误诊断」**,原三项降为 facet(P11a/P11b/P11c),P12/P13 编号墓碑保留不复用,清单 21→19。

依据(全部 benchmark 无关):

1. **P11/P12 拆分不满足拆分准入规则**(理论/失败机制/教师标准/同源数据四类依据至少两个):v3 审计自认两者残余约等于无、机制同为对参考解核验;分成两个 P 的表象来自 mathtutorbench 恰好分成两个任务,而 benchmark 的存在不构成拆分依据。
2. **P13 单独保留虽通过准入检验**(教师 noticing 的 perceive/interpret 之分、误概念知识残余、sas_bench CCS/ECS 独立标注),但允许拆≠必须拆;合入后与 P03/P04 合并同一口径——诊断深度用 facet 表达,不是独立构念。
3. **测量上互补**:原 P11/P12 均为薄证据单源+,合并后整 P 多源,formative facet 机制现成。

附带变更:原 P11 内删除两个同源重复格(mathtutorbench_mistake_location 0.1 搭车格、bea2025_judge 0.25 暂不计分占位格),均已由 P11b/P11c 持有,避免同 P 跨 facet 双计。其余格子、权重、evidence_tier 原样迁移,含 longtutor_diagnosis 副挂 0.1 与 edubench 指标的方法学注记。

**方法学披露**:本裁决发生在见数之后(v2 聚合分数已产出)。修订仅以上述构念层依据支撑,不引用任何分数模式;v2 聚合产物快照保存在 `reports/atomic_ability_rebenchmark_2026-07-08_v2_snapshot_20260716/`,可做 v2/v3 对比。

机器可读落盘:`data/mapping_measurement_model_v3.json`(2026-07-16,R1-R17 全部裁决;v2 为 R17 前快照,保留不删)。

## 裁决记录 R18(2026-07-16,P17 重构 + P23 新设 + facet 含义补全 + 教师协作口径)

五项议题(用户 2026-07-16 提出)一次裁决:

1. **P17 增设"教学目标对齐"facet(空白,暂未覆盖)**。P17 原定义只锚"学生状态"一个对齐目标,漏了"课标/教学目标"。依据(benchmark 无关,两类):①理论——constructive alignment 是教学设计经典框架;②教师标准——新课标评价体系与教师资格标准中"教学目标设计与达成"为独立条目。语义核实:现有全部格子无一测目标对齐(longtutor_teaching 的 strategy_alignment 锚的是学生状态/历史)。P 定义同步改为"对齐教学目标与学生状态,制定并执行合适的教学策略"。
2. **P17"教学策略知识"facet 改名"教学策略制定"**。facet 按构念命名,不按测量方式命名;pedagogy_benchmark 的题目实质是情境化决策题("教师面对 X,最佳做法"),更贴"制定"。格子与权重不动,附 knowing-doing gap 测量注记。P17 结构由两 facet 变三 facet:目标对齐(空白)→ 策略制定 → 策略执行。
3. **全部 facet 补一句含义定义**,写进各 P 小节表前,并同步进 v4 JSON 的 `facet_description` 字段。此后 facet 边界争议引用定义裁决,不再现场论证。
4. **P23"测评设计与出题"新设**(P04/P12/P13 为墓碑,新 P 顺延编号;清单 19→20)。此前出题仅以 edubench QG 一格折叠在 P18"教学产物生成"里,清单上不可见,且所取指标(清晰启发/情景元素)只测表达质量,测评效度零覆盖。拆分依据(benchmark 无关,三类):①理论——测评素养(assessment literacy)在教师能力框架中独立于教学实施;②失败机制——擅长讲解的模型可能出出答案有歧义、干扰项无效的题,两能力可独立失败;③教师标准——"命题与作业设计"为独立条目。附带迁移:edubench QG 格子自 P18 拆出(P18 该格子改为 TMG/PCC);P14"生成 rubric"空 facet 迁入(P14 收窄为纯评分,与 P23 边界:P14 是用 rubric 评,P23 是造题与造 rubric)。
5. **"与人类教师协作"不进清单**。拆开看多数成分现有 P 已覆盖(见"五条解释性口径"新增条目);残余机制仅一类理论依据(human-AI co-orchestration),不满足拆分准入。记 `benchmark-todo.md`,触发条件(教师标准单列/专门评测出现)满足时重审。

**方法学披露**:同 R17,本裁决发生在见数之后(v2/v3 聚合分数已产出);修订仅以上述构念层依据支撑,不引用任何分数模式。P17 制定/执行两 facet 的格子与权重原样保留;P23 的 QG 格子沿用原 P18 格子权重 0.4,无任何格子权重因本裁决变动。

机器可读落盘:`data/mapping_measurement_model_v4.json`(2026-07-16,R1-R18 全部裁决;v3 为 R18 前快照,保留不删)。

## 评测覆盖与数据缺口(截至 2026-07-16)

映射关系已定稿,但"每个格子都有可信分数"还欠下面这些。分四类:没跑的、面太窄的、构念层缺依据的、流程性的。

### 1. 还没跑出分数的 benchmark(挂载已定,格子空转)

| benchmark | 现状 | 影响 | 补法 |
|---|---|---|---|
| **mooccube_prereq** | adapter 已接入,0 个模型跑出产物 | **P19 整个能力无分**(20 P 里唯一"有挂载没分数"的) | `MODEL=<m> ./scripts/run_eval.sh mooccube_prereq`,300 题纯规则判分零裁判,5 个发布模型很便宜,优先做 |
| **k12vista** | adapter 已接入,0 个模型跑出产物 | P03 学科图表 facet(权重 0.55 的主格)无分 | 只能跑视觉模型(注意 deepseek-v4-pro 收图不报错但看不见);需 LLM 裁判 |
| **mmtutorbench** | 只有 LIMIT=5 的冒烟跑,被收录规则(<100 题)排除 | P03 教学场景图文 / P17 / P18 各一格空转 | 至少一档 ≥100 题的正式跑(770 题全量或抽样档) |

### 2. 模型面过少的 benchmark(有分,但配对检验和横向对比受限)

发布口径 5 个模型(MiniMax-M3 / M2.7 / deepseek-v4-pro / glm-5.2 / doubao-seed-2.0-pro)。当前各 benchmark 模型面:

| 面宽 | benchmark | 备注 |
|---|---|---|
| **1-2 个** | mathvista(1)、olympiadbench(2) | 多模态答题类只有视觉模型跑过;P03 解题图像 facet 横向比不了 |
| **3 个** | longtutor 三任务、bea2025_tutor、mrbench_tutor | **2026-07-16 已裁决不补跑**,按 3 模型面注记;若未来要用这些格子做排名再回头补(longtutor 缺 M2.7/doubao;bea/mrbench 缺 deepseek-v4-pro/doubao 的**生成**) |
| **4 个** | eduillustrate、mathtutorbench_problem_solving、mathtutorbench_socratic | 补 1-2 个模型即可齐面 |
| 模型错位 | edubench 面是 **glm-5.1** 而非发布口径的 glm-5.2 | glm-5.2 的 P16/P17/P18 里 edubench 格子全缺,P16 尤其失真(只剩 P16a 一个 facet,不可横比);同事数据不可重跑,选择:接受错位注记,或自跑 glm-5.2 的 edubench 面 |
| 数据源缺 | pedagogy_benchmark 的 CDPK / SEND 两个**分列**格子无独立数据源 | 现只有 0701 卡的合并分在计分;P05 教学知识、P16d、P17 制定 facet 的分辨率因此损失 |
| 裁判 error 未清 | deepseek-v4-flash、doubao-seed-2.0-lite 在 mathtutorbench win-rate 上还有几十到几百行 error | 非发布模型不挡路;想扩展模型面时先断点续判再采信 |

### 3. 缺失评测依据的原子能力(构念层缺口)

| 能力 | 缺什么 | 候选路线(详见 `doc/benchmark_gap_recommendations_2026-07-11.md`) |
|---|---|---|
| **P09 工具使用与长程执行** | 领域空白,无任何挂载 | 教育场景 agent 评测尚无公开基准,需自建或等社区 |
| **P15 学术诚信判定** | 领域空白,无任何挂载 | 抄袭/代写检测有工业工具但无教育评测协议 |
| **P16b 误概念识别** | 子能力空 facet | Eedi 误概念标注(NeurIPS 2024 竞赛)、Bridge(700 段真实辅导对话带专家标注) |
| **P16c 情感与参与识别** | 子能力空 facet | IntrEx(EMNLP 2025,教育对话兴趣/参与度标注)可直接做判别任务 |
| **P14 教学回复评判 facet** | bea/mrbench_judge 按口径暂不计分 | 裁判校准研究(`doc/judge_rubric_evolution_method_and_contributions_2026-07-16.md`)的结论落地后,可用 judge 一致性分激活 |
| **P17 教学目标对齐 facet** | R18 新增 facet,空白 | 无公开基准;需自建协议(给定教学目标+学情,判断教学回复是否服务目标),或找含课标/目标标注的教案与对话数据 |
| **P23 题目生成·效度维度** | 现仅 edubench QG 的表达质量指标,答案正确性/难度定标/干扰项质量零覆盖 | Eedi 干扰项-误概念数据(与 P16b 候选同源)可测干扰项设计;答案正确性可自建规则协议(生成题自答一致性校验) |
| **P23 生成 rubric facet** | 空白(R18 自 P14 迁入) | 无现成数据,需自建(给任务生成评分标准、对专家 rubric 判一致性) |
| **P03 视频/音频 facet** | 空白 | 多模态教育视频理解基准尚未接入 |
| **P02 区分度** | 有直接测量(longtutor_evidence 0.7)但三模型 0.787/0.807/0.791 挤在一起 | 补更难的长上下文任务,或加模型面验证是不是真天花板 |
| **P20/P21/P22 知识 facet 同源** | 三 P 共用一份 SATA 数据,不构成互证 | R10:SATA 类别标注(LLM 粗标+抽检)拆出三 P 独立证据,已排到发布后 |
| **P10 单源** | 只有 eduillustrate 一格 | 无配对检验可做,永远 single_source 评级 |

### 4. 流程性 TODO(M4 关键路径)

死格子(题级 SD<0.5)剔除与 edubench 指标级【草案】权重核对 → v1/v2 对比 + 排名稳定性 → M4 双报告(研究版/用户版)。发布目标 7 月底。详见 `doc/rebenchmark_workstream_overview_2026-07-12.md`。
