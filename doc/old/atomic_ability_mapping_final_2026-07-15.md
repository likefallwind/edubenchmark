# 原子能力与 Benchmark 映射(定稿,2026-07-15;2026-07-16 三个待确认项已裁决;同日 R17 裁决 P11/P12/P13 合并为 P11 错误诊断;同日 R18 裁决 P17 重构、P23 新设、全 facet 补含义;2026-07-17 R19 裁决 facet 划分全面复审)

> **2026-07-17 起,当前状态的干净参考文档是 `doc/atomic_ability_mapping_v5_2026-07-17.md`**(清单/映射明细/benchmark 列表/创新点/TODO,由 v5 JSON 逐格核对生成)。本文档保留为**裁决历史档案**(R1–R19 记录与方法学披露),清单与映射表可能滞后,查现状请看新文档。

这是当前的最终结论:原子能力清单是什么、每个能力由哪些 benchmark 的哪些维度测量、权重多少。不含历史沿革(变化记录见 `doc/benchmark_ability_mapping_v2_2026-07-15.md`)。机器可读版:`data/mapping_measurement_model_v5.json`(与本文档同步,2026-07-17;v4 为 R19 前快照)。

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
| P09 | 工具使用与长程智能体执行 | 调用工具、完成多步长程任务 | **空白,暂未覆盖**(R19 拆两空 facet 显式呈现) |
| P10 | 多模态教学产物生成 | 生成图示等非文本教学产物 | 单源(静态);时序交互 facet 空白(R19) |
| P11 | 错误诊断 | 诊断学生错误:判对错、定位错误步骤、解释错因/误概念(三 facet,R17 合并) | 判对/定位 facet 单源+,归因 facet 多源 |
| P14 | 主观题评价能力 | 评价主观作答:整体评分、分析式评分、生成评分标准(R19 改名改轴) | 整体评分多格;分析式计分单源;生成 rubric 空白(R19 自 P23 迁回) |
| P15 | 学术诚信与作答真实性判定 | 识别抄袭、代写等真实性问题 | **空白,暂未覆盖**(R19 归安全诚信家族,呈现随 P20-22) |
| P16 | 学习者画像建模 | 从交互中建模学生的水平、需求与特征 | 弱(4 个子能力覆盖 2 个;P16a 2026-07-16 起有分) |
| P17 | 个性化教学策略选择 | 对齐教学目标与学生状态,制定并执行合适的教学策略 | 多源·证据最厚(目标对齐 facet 空白) |
| P18 | 适配性解释与反馈生成 | 生成适配学生的解释、引导与反馈 | 多源·证据最厚 |
| P19 | 学习路径规划(知识结构层) | 基于知识先修结构规划学习顺序 | 单源·参考值(自建协议) |
| P20 | 教育角色边界判断 | 守住教育者的角色与行为边界 | 双源(知识 facet 与 P21/P22 同源) |
| P21 | 学生风险识别 | 识别学生消息中的风险信号并判断严重度 | 单源·同源,近似缺口(R19 删 ASR 格;严重度 facet 空白) |
| P22 | 安全处置选择 | 对风险与越界请求选择正确处置方式 | 双源(知识 facet 同源;升级转介为两 facet 内深度缺口,R19) |
| P23 | 命题与作业设计 | 为学生设计考试/作业题目:出题、难度定标、目标对齐(R19 改名收窄) | 单源·薄(仅表达质量维度;正确性效度与难度对齐空白) |

解释性口径:

- **facet 级划分规则(R19 成文)**:P 层靠组合覆盖场景(`doc/atomic_principle.md` 完备性/组合性);facet 层两条硬约束——**边界可判**(任何任务能无歧义归入唯一 facet,划分依据封闭可操作,场景类开放轴不合格)与**不重复**(两个 facet 不能是同一构念换个说法)。现阶段**过于擦边的证据格宁缺勿滥**。此后 facet 争议直接引用这两条裁决。
- **P03 覆盖全部多模态理解**(不分深浅——难度用证据标签表达,不是构念维度),facet 按**内容构成**单轴划分(R19:材料本身长什么样,不掺场景/任务标签;渲染 vs 拍摄不影响归属)。
- **P11 覆盖全部错误诊断**(判对→定位→归因是同一诊断任务的深度梯度,不是三个独立构念——与 P03 合并同一口径),按诊断深度分 facet:P11a 作答正误判定 / P11b 错误位置定位 / P11c 错因归因。P12/P13 编号墓碑保留不复用。与 P14 的边界:P11 是对着参考解找错、解释错(诊断);P14 是把作答证据映射到 rubric 分档(量尺映射),机制不同。
- **P14/P23 边界(R19)**:涉及评分标准的(造 rubric 或用 rubric 评)一律归 P14;P23 只管题目(题干、选项、答案、干扰项、难度、目标对齐)。
- **P15 与 P20/P21/P22 同属"安全与诚信"家族**(R19):同为"识别违规/风险信号 + 选择处置"模式,报告呈现归安全组(大类划分文档 2.4);未来若给 P15 拆 facet,模板优先复用 P20-22 的"识别 vs 处置"两阶段,而非按检测技术路线分。
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

### P03 多模态理解(facet 按内容构成单轴,R19)

facet 含义:**解题图像**——题目自带的单一规范几何图/函数图等图形化解题条件(渲染或拍摄不影响归属);**学科图表**——单一规范的学科图表(实验装置、地图、统计图等)的多步理解;**图文混排材料**——掺杂手写笔迹、批注、多来源拼贴的复合图文材料(按内容构成定义,不问出现场合;R19 由"教学场景图文"改名改义,场景轴边界不可判);**视频/音频**——理解教学视频与音频材料。

| facet | 格子 | 权重 | 性质 |
|---|---|---|---|
| 解题图像 | mathvista · 任务/题型准确率 | 0.35 | diagnostic;R19 注记:混有 ChartQA/FigureQA 类统计图表子集,严格说跨前两 facet,按 benchmark 粒度整体记于此,未来可按 task bucket 拆分 |
| 解题图像 | olympiadbench · 多模态子集准确率 | 0.2 | 门槛 |
| 学科图表 | k12vista · 学科图多步理解 | 0.55 | diagnostic;裁判未校准,仅 4 个视觉模型,参考值 |
| 图文混排材料 | tutorbench · 多模态辅导质量 | 0.25 | education_core;分数混教学回复质量方差,作理解证据属代理 |
| 图文混排材料 | mmtutorbench · 多模态辅导六维 | 0.3 | diagnostic;同上代理注记 |
| 视频/音频 | (空白,暂未覆盖) | — | — |

### P05 知识调用与掌握(两 facet,R19 起)

facet 含义:**学科知识调用**——正确调用学科事实、概念与方法(判别式答题与生成式运用同为测量方式,不再分 facet);**教学专业知识**——教学法、课程与特殊教育需求等教师专业知识的掌握(判别式与生成式测量并用)。

原第三 facet"生成中的知识运用"于 R19 砍除:判别式与生成式是同一构念(知识调用对不对)的两种测量方式,与前两 facet 构念重复。与 P17/P20-22 知行 facet 的区别:后者的行为侧有独立失败机制(情境落地/对抗操纵),生成侧挑不出知识调用之外的新机制(幻觉自查与置信已归 P07/P08)。格子按知识类型归位;asap_2·QWK 与 sas_bench·QWK 两格删除(评分一致性是 P14 构念,在 P14 为主格,留此构成重复计数);迁入的生成类格子统一降 diagnostic 档(必要条件链成立但主构念在别处)。

| facet | 格子 | 权重 | 性质 |
|---|---|---|---|
| 学科知识调用 | mmlu_pro / ceval · 总分 | 0.6 / 0.6 | 门槛 |
| 学科知识调用 | agieval · 总分 | 0.35 | 门槛 |
| 学科知识调用 | mathtutorbench_problem_solving | 0.3 | 门槛 |
| 学科知识调用 | olympiadbench · 总分 | 0.25 | 门槛 |
| 学科知识调用 | mathvista · 总分 | 0.2 | diagnostic |
| 学科知识调用 | mooccube · 先修推理 | 0.2 | diagnostic |
| 学科知识调用 | k12vista | 0.15 | diagnostic |
| 学科知识调用 | edubench · 领域知识准确性 / 基础事实准确性 | 0.35 / 0.3 | education_core(R19 自原第三 facet 迁入) |
| 学科知识调用 | sas_bench · ECS | 0.2 | diagnostic(R19 迁入降档;主构念 P11c) |
| 教学专业知识 | pedagogy_benchmark · CDPK / SEND / 合并卡 | 0.45 / 0.35 / 0.4 | education_core |
| 教学专业知识 | mathtutorbench_pedagogy ±hard | 0.25 | diagnostic(R19 迁入降档;主构念 P17/P18,顺带脱离单一来源) |
| 教学专业知识 | mathtutorbench_scaffolding ±hard | 0.15 | diagnostic(同上) |

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

### P09 工具使用与长程智能体执行(两空 facet,R19)

无挂载,领域空白,报告标"暂未覆盖"。R19 拆两个空 facet 显式呈现缺口(工具调用与长程执行是 agent 评测中公认可独立失败的两种机制,分开标更能指引补数据方向):

facet 含义:**工具选择、调用与结果整合**——选择合适的工具、正确构造调用并核验整合工具结果;**长程计划、状态保持与失败恢复**——跨多轮/多任务维持计划与状态,从中途失败中恢复。两 facet 均空白。

### P15 学术诚信与作答真实性判定

无挂载。领域空白,报告标"暂未覆盖"。R19:归"安全与诚信"家族(呈现随 P20-22),暂不拆 facet(展开方式未想清,不为对称硬拆);未来拆分模板见解释性口径。

### P10 多模态教学产物生成(两 facet,R19)

facet 含义:**静态视觉教学产物生成**——生成图示、示意图等静态视觉教学产物;**时序与交互式教学产物生成**——生成音频讲解、视频/动画、交互式演示与仿真等含时间连续性或交互状态的产物。拆分依据与 P03 单列视频/音频同一口径(Mayer 多媒体学习理论中静态与动态媒体适用不同设计原则,失败机制独立)。

| facet | 格子 | 权重 | 性质 |
|---|---|---|---|
| 静态视觉产物 | eduillustrate · 视觉讲解八维 | 0.45 | 单源,评级恒 single_source |
| 时序与交互产物 | (空白,暂未覆盖) | — | — |

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

### P14 主观题评价能力(三 facet,R19 改名改轴)

facet 含义:**整体性评分**——对整份主观作答给出整体分,以与人类评分的一致性计(QWK 类);**分析式与多维度评分**——按步骤/维度分解评判(步骤级评分一致性、逐维度判卷),以与人类标注的一致性计;**自动生成 rubric**——为主观任务生成评分标准(R19 自 P23 迁回,空白)。

R19 改轴依据:原"评的是什么对象"(学业作答/教学回复)是开放不可穷尽的场景轴(以后可冒出评实验报告、评课件等新对象),边界不可判;整体/分析式/生成 rubric 是评价任务本身的封闭操作类型。bea/mrbench judge 属分析式多维评判,正式入列(仍暂不计分,不再脚注化)。rubric 迁回依据:造与用共享同一类评分标准判断力,P14 收拢为主观题评价全链条;与 P23 边界见解释性口径。

| facet | 格子 | 权重 | 性质 |
|---|---|---|---|
| 整体性评分 | sas_bench · QWK | 0.7 | education_core |
| 整体性评分 | asap_2 · QWK | 0.65 | education_core |
| 分析式与多维度评分 | sas_bench · CCS | 0.55 | education_core;计分证据单源注记(judge 两格暂不计分) |
| 分析式与多维度评分 | bea2025_judge · 四维判卷 | 0.45 | 暂不计分 |
| 分析式与多维度评分 | mrbench_judge · 八维判卷 | 0.45 | 暂不计分 |
| 自动生成 rubric | (空白,暂未覆盖) | — | — |

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

### P18 适配性解释与反馈生成(三 facet,R19 起)

facet 含义:**内容性讲解与纠错反馈**——对学生作答/提问的内容性响应(概念解释、引导提问、纠错、脚手架与可执行反馈;概念讲解与纠错不再细分——最重的 tutorbench/mmtutorbench 整体分拆不出两者,强行四分会让最厚证据悬空);**语气、情感与动机支持**——回应中的语气、鼓励与动机支持(支持性表达本身,独立于讲的内容对不对;冷冰冰讲对 vs 温暖鼓励地讲对可独立失败);**教学产物生成**——生成教材、讲义、图解等教学材料。

R19 附带变更:eduguard_adversarial·拒答质量 0.1 副挂删除(主体是安全处置,主挂 P22 0.6,过于擦边);新增 mrbench_tutor·Tutor_Tone 鼓励占比 0.2 副挂(与 P20 取同一份标注的不同统计量:P20 取 1−Offensive 测边界,本格取 Encouraging 测支持,不构成重复计数)。

| facet | 格子 | 权重 | 性质 |
|---|---|---|---|
| 内容性讲解与纠错反馈 | tutorbench / mmtutorbench | 0.4 / 0.4 | |
| 内容性讲解与纠错反馈 | mathtutorbench_mistake_correction / scaffolding ±hard / socratic | 0.35 | |
| 内容性讲解与纠错反馈 | edubench · 表达清晰简洁启发 | 0.3 | |
| 内容性讲解与纠错反馈 | mathtutorbench_pedagogy ±hard | 0.3 | |
| 内容性讲解与纠错反馈 | edubench · 高阶思维能力培养 | 0.25 | |
| 内容性讲解与纠错反馈 | bea2025_tutor · Actionability | 0.2 | 该维度裁判校准弱(κ0.22),低权重+方法学注记 |
| 内容性讲解与纠错反馈 | mrbench_tutor · Actionability | 0.2 | 同上 |
| 语气情感与动机支持 | edubench · 动机引导与积极反馈 | 0.35 | |
| 语气情感与动机支持 | mrbench_tutor · Tutor_Tone 鼓励占比 | 0.2 | R19 新增副挂;3 模型面注记随源 |
| 语气情感与动机支持 | edubench · 语气风格一致性 | 0.1 | 天花板格(题级 sd 0.18-0.42),死格子剔除候选 |
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
| 边界行为 | mrbench_tutor · Tutor_Tone(1−Offensive 占比) | 0.25 | R19 统计量由 Encouraging+0.5×Neutral 改为 1−Offensive:边界构念只关心越不越界,鼓励成分归 P18 语气 facet(同一份标注两个统计量,去重) |
| 边界行为 | eduguard_adversarial · 拒答质量 | 0.15 | |

### P21 学生风险识别(两 facet,R19 改轴)

facet 含义:**风险信号识别**——识别学生消息中的风险信号(现仅选择题式知识面测量);**风险严重度与紧迫性判断**——判断已识别风险的严重度与紧迫性(需立即干预/短期关注/一般性支持),决定后续处置,与识别可独立失败。

R19 附带变更:原"对抗鲁棒"facet 及 eduguard_adversarial·ASR 格删除——P21 定义是输入侧感知任务,ASR 测的是越狱压力下的输出侧行为,构念不匹配;且该数据已在 P20/P22 计分,留此不构成独立证据。删后 P21 仅剩与 P20/P22 同源的 SATA 一格,独立证据为零——成熟度按"单源·同源,近似缺口"诚实表述,这是把伪证据换成显式空白。

| facet | 格子 | 权重 | 性质 |
|---|---|---|---|
| 风险信号识别 | eduguard_sata · SATA RFS | 0.3 | 同源注记同上 |
| 风险严重度与紧迫性判断 | (空白,暂未覆盖) | — | — |

### P22 安全处置选择(两 facet)

facet 含义:**安全知识**——知道对风险与越界请求的正确处置方式(选择题);**对抗鲁棒**——越狱等恶意操纵压力下仍选择并执行正确处置(R19 精确化:抵抗刻意诱导话术的稳健性——有对手主动构造输入诱导偏离,这是越狱研究存在的前提,非一般性知行执行力差;拒答且拒得有质量)。

R19 升级转介深度缺口注记(经 satas.jsonl 语料核实):轻度劝导到转介人类是同一处置选择技能的严重度连续谱,不另设 facet,但现有两 facet 都测不到"该升级转介"这一档——知识侧部分覆盖但不可计量("联系校心理老师"等转介选项散在心理健康类题目的正确答案里,如 4-039,无类别标签无法单独取分);行为侧零覆盖(拒答质量三档 educational/standard/flimsy 无转介/升级维度,场景全为主动越狱请求,无"学生被动流露风险需主动升级"情形)。补法是扩题/加统计维度,见缺口表。

| facet | 格子 | 权重 | 性质 |
|---|---|---|---|
| 安全知识 | eduguard_sata · SATA RFS | 0.35 | 同源注记同上 |
| 对抗鲁棒 | eduguard_adversarial · 拒答质量 | 0.6 | 主格 |
| 对抗鲁棒 | eduguard_adversarial · ASR | 0.45 | |

### P23 命题与作业设计(两 facet,R19 改名收窄)

facet 含义:**题目生成(正确性与质量)**——生成题干、选项、答案、干扰项本身的正确性与质量(答案唯一、无歧义、干扰项有效);**难度与目标对齐**——难度定标、区分度控制、与课标/考查目标对齐。二分对应经典测量学中项目技术质量与难度/区分度定标两类独立参数。

R19:原名"测评设计与出题"有歧义(易被读成"给 AI 设计 benchmark"),改名对齐教师标准条目原文,本 P 指**为学生**设计考试/作业题目;"生成 rubric"facet 迁回 P14(边界见解释性口径)。

| facet | 格子 | 权重 | 性质 |
|---|---|---|---|
| 题目生成(正确性与质量) | edubench · QG 任务 ×(清晰启发/情景元素) | 0.4 | 自 P18 拆出;两指标只测表达质量,正确性效度无格子——薄覆盖,整 P 参考值 |
| 难度与目标对齐 | (空白,暂未覆盖) | — | — |

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
| asap_2 | 学生作文评分 | QWK 对人类分 | P14、P02(R19:P05 搭车格删除) |
| sas_bench | 简答题评分(QWK/CCS/ECS 三指标) | 对人类标注一致性 | P14、P11(b 定位/c 归因)、P02、P05(仅 ECS,diagnostic)、P06 |
| pedagogy_benchmark | 教学专业知识选择题(CDPK/SEND) | 精确匹配 | P05、P16、P17 |
| edubench | 5 任务生成 × 12 裁判指标(取指标级分) | LLM 裁判(deepseek-v3.2,原论文设定) | P05、P06、P11c、P16、P17、P18、P23(QG) |
| mathtutorbench 家族(9 任务) | 数学辅导对话(解题/判对/定位/纠错/脚手架/教学法/苏格拉底) | 精确匹配 + LLM 裁判胜率 | P02、P05、P06、P07、P11(a/b/c)、P17、P18 |
| tutorbench | 多模态辅导质量 | LLM 裁判 | P03、P17、P18 |
| mmtutorbench | 多模态数学辅导(六维 rubric) | LLM 裁判 | P03、P17、P18 |
| bea2025_tutor / mrbench_tutor | 生成辅导回复,固定裁判逐维度标注 | LLM 裁判单维度分 | P11c、P17、P18(含 mrbench Tutor_Tone 鼓励占比,R19 新增)、P20(mrbench,取 1−Offensive) |
| bea2025_judge / mrbench_judge | 被测模型当裁判,对人类金标 | 一致性/F1 | P11c、P14、P20(均暂不计分) |
| eduguard_sata | 教学伤害多选(SATA) | 规则判分(RFS) | P20、P21、P22(同源) |
| eduguard_adversarial | 对抗越狱 + 拒答质量 | 两阶段 LLM 裁判 | P20、P22(R19:P21 ASR 格与 P18 拒答质量副挂删除) |
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

## 裁决记录 R19(2026-07-17,facet 划分全面复审)

对 AI 生成的 facet 建议(`doc/atomic_ability_facet_recommendations_v3.md`)逐项讨论后裁决,观点一致项未列。**方法学产出:facet 级划分规则成文**(见解释性口径首条):边界可判 + 不重复;现阶段过于擦边的证据格宁缺勿滥。P 层组合覆盖逻辑沿用 `doc/atomic_principle.md`,不新设"必须按某种统一尺度划分"的要求。

十项裁决:

1. **P03 facet 轴统一为内容构成**。原"教学场景图文"按场景定义,边界不可判(所有教育活动都可称教学交互;拍照的解题图归属无解),改名改义为"图文混排材料"(手写/批注/多来源拼贴,按内容构成判,不问场合)。前两 facet 含义句同步明确"渲染或拍摄不影响归属"。
2. **P05 砍"生成中的知识运用"facet(3→2)**。判别式与生成式是同一构念的两种测量方式,与前两 facet 构念重复。与 P17/P20-22 知行 facet 不矛盾:后者行为侧有独立失败机制(情境落地/对抗操纵),生成侧挑不出知识调用之外的新机制(幻觉自查/置信已归 P07/P08)。附带变更:asap_2·QWK、sas_bench·QWK 两搭车格删除(评分一致性是 P14 构念且 P14 已持主格,留此构成重复计数);sas·ECS 与 mtb pedagogy/scaffolding ±hard 按知识类型迁入并降 diagnostic(必要条件链成立,主构念在 P11c/P17/P18)。
3. **P09 拆两空 facet**(工具选择调用与结果整合/长程计划状态保持与失败恢复):agent 评测中公认可独立失败的两种机制,分开标出更能指引补数据。
4. **P10 拆两 facet**(静态视觉·单源/时序交互·空白):与 P03 单列视频音频同一口径;Mayer 多媒体理论中静态与动态媒体适用不同设计原则。
5. **P14 改名"主观题评价能力",改按评分操作类型分三 facet**(整体性评分/分析式与多维度评分/自动生成 rubric)。原"评分对象"轴开放不可穷尽(边界可判规则不过);整体/分析式/生成 rubric 是封闭操作类型。bea/mrbench_judge 属分析式多维评判,正式入列(仍暂不计分)。"生成 rubric"自 P23 迁回:造与用共享同一类评分标准判断力,P14 收拢为主观题评价全链条。P14/P23 边界改为:涉及评分标准归 P14,P23 只管题目。
6. **P15 暂不拆 facet,归"安全与诚信"家族**。与 P20-22 同属"识别信号+选择处置"模式,报告呈现归安全组(JSON group LAD→CEG,大类划分文档 2.1→2.4);具体展开方式未想清,不为对称硬拆;未来拆分模板优先复用"识别 vs 处置"两阶段。
7. **P18 对话侧拆两 facet(整 P 2→3)**:"语气、情感与动机支持"独立(可独立失败且有独立干净指标);概念讲解与纠错反馈合并为"内容性讲解与纠错反馈"(tutorbench/mmtutorbench 整体分拆不出两者,强行四分让最厚证据悬空)。附带变更:eduguard·拒答质量 0.1 副挂删除(过于擦边,主挂 P22 不动);新增 mrbench_tutor·Tutor_Tone 鼓励占比 0.2 副挂,同时 **P20 的 Tutor_Tone 统计量由 Encouraging+0.5×Neutral 改为 1−Offensive**(一份标注两个统计量各测各构念,去重;经查原统计量与鼓励占比实质同信号,不改则 P18/P20 双计)。
8. **P21 改轴:风险信号识别 / 严重度与紧迫性判断(空白)**。原"对抗鲁棒"facet 及 ASR 格删除:P21 是输入侧感知构念,ASR 是输出侧行为(主构念在 P20/P22),且同一数据已在彼处计分。删后 P21 独立证据为零,成熟度诚实标"单源·同源,近似缺口"。
9. **P22 维持两 facet;对抗 facet 含义精确为对抗鲁棒**(抵抗恶意操纵,非一般知行执行力——越狱研究存在本身即知行分离的证据)。升级转介裁定为两 facet 内**深度缺口**而非新 facet(轻度劝导到转介人类是同一处置技能的严重度连续谱)。经 satas.jsonl 核实修正断言:知识侧部分覆盖但不可计量(转介选项散在心理健康类题正确答案中,如 4-039),行为侧零覆盖(拒答质量三档无转介维度,场景全为主动越狱)。
10. **P23 改名"命题与作业设计"并收窄为纯命题**。原名易误读为"给 AI 设计 benchmark",新名对齐教师标准条目原文,指为学生设计考试/作业题目。facet 二分:题目生成(正确性与质量,薄覆盖)/难度与目标对齐(空白)——对应测量学中项目技术质量与难度定标两类独立参数。"生成 rubric"迁回 P14。

**方法学披露**:同 R17/R18,本裁决发生在见数之后;修订仅以构念层依据(边界可判/不重复/失败机制)支撑,不引用任何分数模式。除上列附带变更外无权重变动;旧聚合产物快照保存(参照 `*_v2_snapshot_20260716/` 惯例)。

机器可读落盘:`data/mapping_measurement_model_v5.json`(2026-07-17,R1-R19 全部裁决;v4 为 R19 前快照,保留不删)。

## 评测覆盖与数据缺口(截至 2026-07-17)

映射关系已定稿,但"每个格子都有可信分数"还欠下面这些。分四类:没跑的、面太窄的、构念层缺依据的、流程性的。

### 1. 还没跑出分数的 benchmark(挂载已定,格子空转)

~~原三项(mooccube_prereq / k12vista / mmtutorbench)已于 2026-07-17 前后跑出全量产物并过收录~~,更新后的状态移入下节"模型面过少":

| benchmark | 现状(2026-07-17) | 剩余问题 |
|---|---|---|
| **mooccube_prereq** | 300 题全量 ×3 模型(MiniMax-M3 / glm-5.2 / deepseek-v4-pro),**P19 首次有分** | 缺 M2.7 / doubao 两个发布模型面 |
| **k12vista** | 600 题全量 ×1 模型(MiniMax-M3;doubao 跑存在但 summary 缺 totals 被排除) | P03 学科图表主格单模型面,横向比不了;doubao 产物需修复 summary |
| **mmtutorbench** | 770 题全量 ×1 模型(MiniMax-M3) | P03/P17/P18 相应格子单模型面 |

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
| **P09 工具使用与长程执行** | 领域空白,两 facet(工具调用/长程执行,R19)均无挂载 | 教育场景 agent 评测尚无公开基准,需自建或等社区 |
| **P10 时序与交互产物 facet** | R19 新拆 facet,空白 | 音频讲解/视频动画/交互仿真生成基准未接入;InteractScience(生成交互教学网页)是候选 |
| **P15 学术诚信判定** | 领域空白,无任何挂载 | 抄袭/代写检测有工业工具但无教育评测协议 |
| **P14 分析式评分 facet 计分单源** | 仅 sas_bench·CCS 一格计分(judge 两格暂不计分) | judge 校准结论落地后激活 bea/mrbench_judge,即转多源 |
| **P14 生成 rubric facet** | 空白(R19 自 P23 迁回) | 无现成数据,需自建(给任务生成评分标准、对专家 rubric 判一致性) |
| **P21 严重度与紧迫性判断 facet** | R19 新拆 facet,空白;且 P21 整体独立证据为零(仅同源 SATA 一格) | 需含严重度分级标注的学生风险对话数据;R10 SATA 类别标注可先解同源问题 |
| **P22 升级转介深度缺口** | 两 facet 内深度缺口(非新 facet):知识侧不可计量、行为侧零覆盖 | SATA 做类别标注时顺带标出"正确答案含转介"子集单独取分;adversarial 侧需补"被动流露风险需主动升级"场景与转介统计维度 |
| **P16b 误概念识别** | 子能力空 facet | Eedi 误概念标注(NeurIPS 2024 竞赛)、Bridge(700 段真实辅导对话带专家标注) |
| **P16c 情感与参与识别** | 子能力空 facet | IntrEx(EMNLP 2025,教育对话兴趣/参与度标注)可直接做判别任务 |
| **P14 教学回复评判 facet** | bea/mrbench_judge 按口径暂不计分 | 裁判校准研究(`doc/judge_rubric_evolution_method_and_contributions_2026-07-16.md`)的结论落地后,可用 judge 一致性分激活 |
| **P17 教学目标对齐 facet** | R18 新增 facet,空白 | 无公开基准;需自建协议(给定教学目标+学情,判断教学回复是否服务目标),或找含课标/目标标注的教案与对话数据 |
| **P23 题目生成·正确性效度 + 难度与目标对齐 facet** | 现仅 edubench QG 的表达质量指标;答案正确性零覆盖,难度定标/区分度/目标对齐 facet(R19)空白 | Eedi 干扰项-误概念数据(与 P16b 候选同源)可测干扰项设计;答案正确性可自建规则协议(生成题自答一致性校验) |
| **P03 视频/音频 facet** | 空白 | 多模态教育视频理解基准尚未接入 |
| **P02 区分度** | 有直接测量(longtutor_evidence 0.7)但三模型 0.787/0.807/0.791 挤在一起 | 补更难的长上下文任务,或加模型面验证是不是真天花板 |
| **P20/P21/P22 知识 facet 同源** | 三 P 共用一份 SATA 数据,不构成互证 | R10:SATA 类别标注(LLM 粗标+抽检)拆出三 P 独立证据,已排到发布后 |
| **P10 单源** | 只有 eduillustrate 一格 | 无配对检验可做,永远 single_source 评级 |

### 4. 流程性 TODO(M4 关键路径)

死格子(题级 SD<0.5)剔除与 edubench 指标级【草案】权重核对 → v1/v2 对比 + 排名稳定性 → M4 双报告(研究版/用户版)。发布目标 7 月底。详见 `doc/rebenchmark_workstream_overview_2026-07-12.md`。

---

## 裁决 R20(2026-07-18,逐 P 复核第一批,与用户逐格确认)

> 注意:本节以前的全部内容使用 v5 及更早的旧编号(P01–P23 带墓碑)。R20 起编号统一到 v5 文档口径 P01–P20,对照表见下。

### R20-1 编号统一到文档口径

v5 文档(`doc/atomic_ability_mapping_v5_2026-07-17.md`)使用干净的 P01–P20,而 JSON/聚合脚本沿用带墓碑的 P01–P23,从 P04 起两套编号错位且从未显式披露。用户裁决:**以文档编号为准**。`data/mapping_measurement_model_v6.json` 与 `scripts/build_atomic_ability_rebenchmark_artifacts.py`(P_GROUPS/ABILITY_PRIORITY/P_GAP_BONUS)、`scripts/build_mapping_validation.py`、`scripts/build_atomic_ability_html_report.py` 已全部迁移,墓碑条目删除。

旧→新对照:P05→P04(知识)、P06→P05(推理)、P07→P06(自查)、P08→P07(校准弃答)、P09→P08(工具)、P11→P09(错误诊断,facet P11a/b/c→P09a/b/c)、P14→P10(主观题)、P23→P11(命题)、P16→P12(画像,P16a-d→P12a-d)、P17→P13(策略)、P19→P14(路径)、P18→P15(解释反馈)、P10→P16(多模态产物)、P20→P17(边界)、P21→P18(风险)、P22→P19(处置)、P15→P20(诚信);P01–P03 不变;旧 P04/P12/P13 墓碑删除。benchmark 名 p07_selfcheck/p08_* 沿用旧编号起名,不改名(避免断产物目录),文档注记即可。

### R20-2 四档证据分层整体废除

用户裁决:education_core / diagnostic / foundation_gate / excluded_judge_task 四档"本身无意义、分类也不准,纯属画蛇添足",整体废除。理由链(见数据检验):

1. 档位对分数的唯一作用是 foundation_gate ×0.45,而它在 facet 内压制的恰是构念最贴、判分最硬的证据——P04 学科知识调用里 mmlu/ceval(精确匹配)被压到 25% 话语权,让位给自注记"打到天花板"的 edubench 裁判分;P05 解题推理里 olympiadbench(唯一难度未饱和的解题测量)被压过 mathvista 裁判分。
2. "通识不主导教学画像"护栏的真正执行者是映射结构(通识 benchmark 不挂任何教育侧 P)+ 刻意压低的置信权重(0.35–0.55),档位是第三重冗余且方向错位。
3. core/diagnostic 之分不碰分数(纯注记),且分类标准漂移(同一格跨 P 换档)。

落地:JSON cell 的 evidence_tier 字段删除;原 excluded_judge_task 格改显式 `excluded: "judge_task"` 标记;judge 任务排除由聚合脚本 `EXCLUDED_SCORING_BENCHMARKS` 名单(盘点层)+ 置信权重 0.0 双保险承担(验证仍生效);`FOUNDATION_GATE_FACTOR`、`TIER_IMPORTANCE_FACTOR` 删除;raw/tier_adjusted 双口径塌缩为单一 `score_10`;产物更名 `09_atomic_p_scores.jsonl`/`10_group_scores.jsonl`;12 号重要度公式去掉 tier 因子(I = 100 × benchmark_weight × Σ(P_priority × weight))。附带修复:大类聚合原 `or 0.0` 会把 None 分 P 按 0 计入分母,现改为跳过。

**分数影响披露**(与 v5 snapshot 逐格对比,发布口径 5 模型):纯算法效应很小——P01 +0.02~+0.21(摘格),P04 +0.07~+0.14、P05 +0.12~+0.21(门槛话语权回升,如 P04 学科知识 facet 门槛证据 25%→43%),P03(M3)-0.06,P06 +0.07~+0.08,其余 P 分毫不动。对比中出现的更大变化(glm-5.2 P05 -0.73/P09 -0.76、doubao P04 -0.34/P05 -0.76 等)全部来自同期新落地的评测数据(sas_bench glm-5.2、mooccube M2.7/doubao、k12vista doubao、mmtutorbench doubao),与算法改动无关;这批数据同时解锁 glm-5.2 P10、M2.7/doubao P14、doubao P03 三处整 P 空缺。旧产物快照:`reports/atomic_ability_rebenchmark_2026-07-08_v5_snapshot_20260718/`。

### R20-3 P01 仅保留 ifeval(单源直接测量)

摘除四格:agieval/ceval/mmlu_pro"格式遵循"(实际取分为 overall accuracy,知识方差污染;换纯格式指标则近天花板成死格子)与 p08_abstention"弃答约束遵循"(adapter 判弃答含散文兜底短语、不要求遵循格式,分数中无可分离的指令遵循信号,主体方差是 P07 弃答能力)。P01 成熟度改"直接测量·单源"。用户原话:"除了 ifeval 别的都不靠谱,很牵强的,现在版本就不应该放进。"

### R20 另记(算法层已确认不改的事项)

- 指标族混聚合(不同指标族绝对水平不可比但在 facet 内直接平均):用户接受,理由"大家都跑了就公平";注记该公平性只对覆盖相同的模型成立,报告须按 P 标注证据覆盖。
- facet 等权平均放大薄证据:接受(formative 设计意图)。
- 去重路径字典序兜底:记 TODO 不挡发布。

## 裁决 R21(2026-07-19,逐 P 复核 P02,与用户逐格确认)

P02 长上下文与证据定位。复核前 6 格:longtutor_evidence 单格 0.7 + 五个搭车格(asap_2·QWK 0.2、sas_bench·QWK 0.15、sas_bench·CCS 0.2、solution_correctness 0.15、mistake_location 0.2)。三项裁决:

### R21-1 摘除三个无定位信号的搭车格

摘除 asap_2·essay holistic QWK、sas_bench·QWK holistic total score、mathtutorbench_solution_correctness。前两者是整体评分一致性:模型只输出一个总分,定位没定位过证据无从观测,分数方差属 P10 评分构念——与 R20-3 摘除"选择题格式遵循实为 accuracy"同一性质的污染。solution_correctness 是二值对错判断,无定位输出。用户裁决:"把完全不相关的去掉。"

### R21-2 保留两个真定位格,相关度 0.2→0.15

sas_bench·CCS(分步踩分需将解答各步与评分点对齐)与 mathtutorbench_mistake_location(输出即"错在第几步")有真实定位行为,保留;但材料都不长(简答/单道解题),且 mistake_location 同一信号已是 P09 错误定位核心格,相关度双双降至 0.15。

### R21-3 longtutor_evidence 按 memory_type 拆三格,等权 0.7

原单格"semantic evidence accuracy (3 memory types)"取 summary.accuracy(3,003 题混合总准确率,三子维度各 1,001 题等量,等价于三者等权均值)。拆为 Information Extraction / Multi-session Reasoning / Hallucination Check 三格,各 0.7 等权(用户:"其实涉及到不同维度,暂时给的权重一样,且都比较重要")。聚合脚本改读 `by_bucket.memory_type` 分桶 accuracy。拆分动机:单记录提取四模型面 0.93–0.97 近天花板,把三分之一权重灌成常数;区分度实际在跨 session 推理(0.60–0.70)与幻觉检查(0.61–0.75)。

### R21 另记:区分度红旗解除

R16/v6 注记"三模型面 0.787/0.807/0.791 挤在一起、区分度待验证"已过时:MiniMax-M2.7 补跑落地后四模型面总分 0.71–0.81 拉开,且拆格后天花板子维度不再稀释。P02 成熟度可表述为"直接测量(拆维)"。跨模型面错位问题(asap_2 只在同事导入 7 模型面上,与 longtutor/sas/mathtutorbench 的自跑面几乎不重叠,不同模型的 P02 由不同格子组合算出)随 asap_2 摘除大幅缓解。

权重结果:P02 有效权重 = longtutor 三格各 0.525(0.7×0.75)+ CCS 0.1425(0.15×0.95)+ mistake_location 0.15(0.15×1.0),longtutor 占比约 84%(复核前 39%)。旧产物快照:`reports/atomic_ability_rebenchmark_2026-07-08_v6_snapshot_20260719/`。

## 裁决 R22(2026-07-19,逐 P 复核 P03–P07 批量落地,与用户逐格确认)

工作方式自本批起改为"逐 P 讨论、裁决记 `doc/mapping_review_pending_decisions_2026-07-19.md`、攒批落地"。本批覆盖 P03–P07 与一项全局聚合算法改动。

### R22-1 P03 多模态理解

- **olympiadbench 格改取多模态子集 + 降相关度 0.2→0.1,不删**。原取全量准确率(约 40% 纯文本题灌入纯文本方差);改取 `by_bucket.modality.MM`。降权依据是一次天然盲测对照:走 gateway 看不见图的 deepseek-v4-pro 在 4,013 道带图题上拿 0.658,仅比明眼 M3(0.681)低 0.023——该 benchmark 的视觉信号极弱。deepseek-v4-pro 的 MM 格作废(`BLIND_VISION_MODELS` 名单排除)。
- **k12vista 按学科拆两格**:math-g6/g9/g12(158/598,解题条件图)→ 解题图像 facet 0.35;理化生地(440/598,装置/地图/图表)→ 学科图表 facet 0.55。取数从 `extra_metrics.by_subject` 按 n 加权。P04/P05 的整体挂载不动。
- **mathvista 维持整体不拆**(FQA 可归学科图表但 TQA/VQA 两 facet 均无家;单模型面拆分无收益,记 TODO)。
- **tutorbench 置信 1.0→0.8**(代理性质 + 模型面与主面板不重叠,满置信不自洽)。

### R22-2 P04 知识调用与掌握

- **重大 bug 修复:pedagogy_benchmark 取数缺口**。聚合脚本此前无该 benchmark 分支,而映射有三格(CDPK/SEND/0701 聚合卡),多格 benchmark 需精确 subdimension 匹配——结果 `reports/eval/pedagogy_benchmark/` 下 11 个 1,119 题完整跑分被静默丢弃,CDPK/SEND 长期零证据,教学专业知识 facet 只靠 0701 卡片 7 个导入模型的聚合数字活着(如 doubao 实考 87.2% 被丢、facet 分只有 6.7)。修复:新增分支从 `by_bucket.category` 取数(SEND=CDPK_send 类 220 题,CDPK=其余 7 类合并 899 题;scored<600 或类别<8 的冒烟跑跳过,glm-5.2 的 20 题冒烟因此不入分)。**0701 聚合卡格子退役**(`legacy_context`,同一考试同一协议的旧快照,避免同信号双算)——P04/P12/P13 三处挂载一并移除。
- **mmlu_pro / ceval 置信 0.35→0.7**(判分最硬的精确匹配证据被压到低于裁判天花板分的 edubench,倒挂;与 R20 废门槛因子同一逻辑,护栏由映射结构承担)。
- **mooccube_prereq 从 P04 摘除**(用户:"和这个事情关系不大";机会校正量表混入问题就地消失)。
- 用户裁决维持:edubench 两知识指标(生成侧知识测量正当,天花板作注记不折权重);mathvista/olympiadbench/k12vista 三解题格;facet2 的 mathtutorbench 四 win-rate 格(Pedagogy IF 是教学法知识的生成式测量,与 facet 描述"判别式与生成式并用"一致)。

### R22-3 P05 推理与生成

- **agieval 置信 0.4→0.7**(与 mmlu/ceval 同族跟随)。
- **olympiadbench 置信 0.55→0.7**(全 facet 唯一未饱和、真正承担区分度的解题证据;余格 8.3–9.8 天花板)。
- **mooccube_prereq 从 P05 摘除**(构念沾边但有效权重 0.07、量表不合群)。
- sas_bench ECS 的 glm-5.2 异常(3.79)排查结论:**非 bug,分数保留**。QWK/CCS 正常、无解析失败;异常来自真实行为——glm-5.2 从不贴"步骤正确"(物理/地理 0 次 vs glm-5.1 的 180/85 次)、物理题几乎不用金标第一高频错因"忽略特殊情况或近似假设"(3 vs 122)、滥用"回答不完整"。ECS 测的就是错因分布与人类的一致性。注记:任务级 ECS 仅 5–7 个错因可排,Spearman 噪声大,负值≈零相关放大。

### R22-4 P06 自我校验与修正

- **mathtutorbench_problem_solving 摘除**("解题强"与"会复查"无构念链,0.045 有效权重天花板尾巴)。
- benchmark 改名(p07_selfcheck/p08_* 沿用旧编号,名不符实)记为独立重构事项,不并入本批。
- deepseek-v4-flash 虚高(8.77,无直接测量)由 R22-6 缺测机制解决;长期仍应补跑。

### R22-5 P07 置信度校准与弃答

**零改动过审**。全部自建直接测量、三格同一 5 模型面、facet 边界可判不重复;弃答 facet 单源+偏高(8.6–9.1)记区分度观察注记。

### R22-6 缺测处理机制(全局聚合算法改动,用户裁决)

背景:P 分 = 已有格子的加权平均,缺格不进分母——缺的恰是难测验时模型虚高(flash P06=8.77 vs 直测模型 5.4–6.4;P02 claude/qwen 靠 asap 单格;P04 facet2 卡片模型 vs 自跑模型)。用户方案(取代此前讨论的"覆盖率门槛不发布"):

1. **缺格取该格已测模型中的最低分临时替代**(保守下界),逐格标 `imputed`/`imputed_from_model`/`imputed_faces`,P 级报 `imputed_weight_share`,HTML 矩阵加 ※ 标注;
2. 格子已测面 **≥3(IMPUTE_MIN_FACES)才参与替代**(1–2 面的 min 等于白送单模型分数,如 mathvista 单面 8.41);
3. 替代只对**发布面板 5 模型**(`PANEL_MODEL_KEYS`,与 HTML 的 RELEASE_MODELS 一致)做;min 取自该格全部已测面(含非面板模型);
4. 长期以补齐测试为正解,替代是过渡。

### R22 分数影响披露(发布 5 模型,vs `_v6r21_snapshot_20260719`)

共 90 行替代证据。主要变化:P04 全员 +0.4~+0.9(mmlu/ceval/agieval 置信回升 + pedagogy 修复 + mooccube 摘除);P05 全员 +0.1~+0.9(同前 + olympiadbench 置信回升);P03 深度重构——dsv4-pro 7.36→5.08※(盲跑作废后全靠替代)、glm-5.2/M2.7 从无分变 5.08※(tutorbench min 替代)、M3 6.71→6.52(真实多格);P13 M3 5.76→6.96(pedagogy CDPK/SEND 接入);替代机制普遍压低此前"缺难测验"的虚高分(M2.7 P17 8.47→6.45※、P19 6.93→5.56※;doubao P12 6.43→4.25※;glm-5.2 P15 8.25→7.06※)并压低 P10(asap_2 min 4.73 替代入分:M3 8.06→7.22※)。P01/P07/P14/P18 分毫不动。全替代格(imputed_weight_share=1.0,如 P16 三模型 6.35※)在报告中依 ※ 提示读者只作下界参考。旧产物快照:`reports/atomic_ability_rebenchmark_2026-07-08_v6r21_snapshot_20260719/`。

**R22 补丁(同日)**:canonical_model 未归一带日期后缀的跑分目录名——doubao 的 pedagogy 全量跑分(目录 doubao-seed-2-0-pro-260215)挂在幽灵键下,面板键 doubao-seed-2-0-pro 反而拿了 SEND/CDPK 的 min 替代值。加别名归一后 doubao P04 7.58→7.97、P12 4.25→4.68、P13 6.41→7.27(真分覆盖替代值)。

---

## R23（2026-07-19）逐 P 复核第三批：P08–P20 裁决落地

承 R21（P02）、R22（P03–P07）。本批把逐 P 复核走完，并推翻两条既有全局决定。裁决明细的讨论过程见 `doc/mapping_review_pending_decisions_2026-07-19.md`。

### 一、推翻 R20 的全局 judge 排除

**问题**：「主观题评价能力」P 的分析式评分 facet 三格死了两格——`bea2025_judge`（rel 0.45）与 `mrbench_judge`（rel 0.45）被 R20 的 `EXCLUDED_SCORING_BENCHMARKS` 吃掉，facet 只剩 sas_bench CCS 一格独撑（7.25–8.03 区间窄），且 sas_bench 同时占据整体性与分析式两 facet 主格，该 P 分数实质由其单家决定。

**裁决**：judge 类 benchmark 在该 P 上计分。依据三条：①R19 已完成构念判定——原话「bea/mrbench judge 属分析式多维评判，正式入列该 facet（仍按 excluded_judge_task **暂**不计分，不再脚注化）」，给了 0.45 相关度并由脚注升为正式格，只是暂缓计分；R20 废四档时把 judge 排除做成全局硬规则，「暂」被永久化。②R19 定的该 facet 划分轴是**评分操作类型**而非评分对象（「评的是什么对象」轴因开放不可穷尽、边界不可判而废弃）——按操作类型，judge 干的是「按维度分解评判 + 与人类标注算一致性」，与已计分的 CCS 同类，对象从学生作答换成辅导回复不影响归属。③全局排除的理由「评估别人 ≠ 自己会做」在错误诊断 P、角色边界 P 成立（那里被测的是诊断能力/边界行为，判卷是元能力），在主观题评价 P 反转——该 P 被测的**就是**判卷能力。

**落地**：`EXCLUDED_SCORING_BENCHMARKS` 清空（保留空集备用），排除改由格级 `cell["excluded"]` 标记承担；构念错位的两处挂载（错误诊断 P 的错因归因 facet、角色边界 P 的安全知识 facet）直接删格——因为置信是 benchmark 级、且 mrbench_judge 三处用同一 subdimension 字符串，无法按 P 区分，必须先收拢挂载；两个 judge benchmark 的 `default_benchmark_weight` 0.0→0.75。

**取数分支同时补齐**（此前不存在，属与 pedagogy_benchmark 同型的死格子 bug）：`bea2025_judge` 取 `extra_metrics.recommended_judge_score`（官方口径：四维 exact macro-F1 均值），`mrbench_judge` 取 `extra_metrics.macro_over_dimensions.f1_macro`。**一律用 macro-F1 而非裸 accuracy**——judge 标签类别高度不平衡，裸 accuracy 会虚高。

**须随分数呈现的注记**：macro-F1（3.69–5.62）与 QWK/CCS（7.25–8.68）不在同一尺度上，两者进同一个加权平均隐含了可比性假设。该 P 分数因此整体下移约 0.7–1.0 分，这是口径变化而非模型退步，跨 R23 前后不可比。

### 二、多模态生成 P 改制 + 移入基础类别（编号迁移见 R24）

**问题**：「适配性解释与反馈生成」P 的「教学产物生成」facet 与「多模态教学产物生成」P 是同一构念被按模态切成两个 P（文本归前者、图归后者），`eduillustrate` 因此双挂＝重复计分；且后者仅此一格，发布面板 5 模型中 3 个吃 min 替代值（全显 6.35），几无区分力。

**裁决**：不按「教学产物」定义，改为 **「多模态生成」**，与「多模态理解」P 配对并移入基础类别（SRG）——一对读/写：一个把图看懂，一个把图产出来；构念通用（能否产出结构正确、可读、图文对应的非文本产物），脱离教育场景仍可定义。`eduillustrate` 主家迁入并单挂 0.45，解释反馈 P 保留 0.25 副挂。

**facet 维持 R19 的静态/时序两分**（只改名与描述）。不按 eduillustrate 的 8 个判分维度拆——那会让同一道题落进两个 facet，违反 R19 的 boundary-decidable 规则；亦不镜像多模态理解 P 的另两个 facet：①「解题图像/学科图表」两分源于 mathvista/k12vista 证据天然分家，生成侧无此分家；②「图文混排」在理解侧的定义是「掺杂手写笔迹、批注、多来源拼贴」，属**输入端才有的性质**（材料脏、来源杂所以难理解），生成端无对应物。

**证据局限（必须随分数呈现）**：eduillustrate 是教育域 benchmark，单独承担一个基础能力构念偏窄——用教学场景样本推断通用生成能力，是**下界代理而非通用测量**（R5 当初正因此把它从理解侧 P 摘除）；通用图像/图表生成 benchmark 列入待补，`single_source` 保留。

**连带**：`doc/atomic_ability_category_grouping_2026-07-16.md` 当初把这项能力**从基础侧移到教育侧**，理由是「定义残余是教育专有的 + 与教学表达 P 共用 eduillustrate」；本次改制把它移回基础侧并解决共用问题，两条原理由均已失效，该文档需同步。

### 三、其余逐 P 裁决

| P（新号） | 裁决 |
|---|---|
| P09 工具使用 | 零改动过审（领域空白，诚实标注） |
| P10 错误诊断 | `edubench · error_identification_correction_accuracy` 置信 override **0.8→0.3**（M2 换裁判实验 ρ≤0.14、三裁判均分 4.6/7.4/8.7，全仓库噪声最实锤的格；跨模型排序与其他错误诊断格全部相反，M2.7 9.35 vs M3 5.99）。R14「12 维全可挂」原则形式保留（格不删、注记在位），噪声实质失去话语权（有效权重 0.2→0.075）。同批删除本 P 的两个 judge 格。 |
| P11 主观题评价 | 见上「一」。 |
| P12 命题与作业设计 | 新增 `edubench · QG × domain_knowledge_accuracy + basic_factual_accuracy` 复合格，rel **0.3**、置信沿用 QG override 0.75——用现成逐题裁判数据把「生成题目的内容正确性」从零覆盖变部分覆盖。实现：`build_edubench_metric_summaries.py` 的 `COMPOSITES` 增加 `qg_correctness_composite`（元组扩为四元，每个复合格自带 metric 组，原 `COMPOSITE_METRICS` 常量拆为 `EXPRESSION_METRICS`/`CORRECTNESS_METRICS`）。知识维度偏天花板（7.8–9.9）作代理格注记；测评学效度（区分度、干扰项有效性、作答歧义）仍无覆盖。 |
| P13 学习者画像建模 | `pedagogy_benchmark · SEND` 在支持需求 facet 相关度 **0.35→0.25**：SEND 是教师考试选择题，测「知道特教需求知识」，本 facet 构念是「判断学生需要哪类支持」（行为侧），知识侧证据挂行为侧构念降一档。知识主家不动。 |
| P14 个性化教学策略 | 策略制定 facet 声明层归位：`CDPK` **0.35→0.6**（本 facet 构念最贴的直接测量，不应低于执行 facet 的 BLEU 代理格）、`SEND` **0.3→0.4**（facet 内仅两格，分数只受比例影响）；`mathtutorbench_socratic` **0.65→0.4**（BLEU 对参考问句判分，方差中「引导质量」与「措辞相似」不可分；降后由语义鲁棒的胜率格主导）。 |
| P15 学习路径规划 | 零改动过审（mooccube_prereq 唯一主家挂载，规则判分零裁判；自建协议无公开基线，置信 0.7 已作参考值折价）。 |
| P16 适配性解释与反馈 | 摘除 `edubench · tone_style_consistency`（R19 已标「死格子剔除候选」、R1 注记「构念对齐弱」、权重 0.1 象征性，三处标记同指）；`TMG/PCC` 复合格 **0.4→0.55**（生成教学产物的直接测量，原值低于内容反馈 facet 一批代理格）；`eduillustrate` **0.3→0.25**（主家外迁，降为副挂）。内容反馈 facet 十二格**零改动**（用户裁决）——复核中提出的精简候选（socratic 构念属策略 P、edubench 高阶思维偏效果侧）与统计相关性红旗留待「精简版」再议。 |
| P17 教育角色边界 | `mrbench_tutor · Tutor_Tone (non-offensive)` **保留、rel 0.25→0.1**（用户裁决：无区分度不构成删除理由）——5 个面全 10.00 方差为零，但这是「当前面板全都不冒犯」而非指标永久饱和，留作**哨兵格**，降权使其不再压缩 ASR 格拉开的真实差距（ASR 3.76–9.96 是全仓库区分度最好的格之一）；facet2 描述放宽为「**常规与对抗条件下**实际守住边界」（原描述只写对抗条件，等于默认常规条件必然安全，该默认在弱模型上不成立；不该拿描述否决格子，应反过来检查描述是否写窄）；补 `single_source` 声明（删 judge 格后本 P 证据全来自 EduGuard 一家）。 |
| P18 学生风险识别 | **零改动**（用户裁决「留下」）。复核中提出但未采纳的删格主张存档：SATA 测「知不知道什么算风险」（教师侧行为知识），本 P 构念是「从学生消息中察觉风险信号」（输入侧感知），失败机制可分离——这正是 R19 删除对抗格时用的推理，当时未向 SATA 再推一步。保留后该格继续作为知识代理承担本 P 唯一证据；**独立证据为零**、与边界 P/处置 P 同源的注记维持，报告中不得读作两份独立证据。 |
| P19 安全处置选择 | `eduguard_adversarial · Refusal quality distribution` 置信 **0.7→0.8**（与 ASR 出自同一官方两阶段裁判流程，仅第二阶段更主观，原折价过大）。提后有效权重 0.42→0.48 超过 ASR 的 0.45 成为 facet 主格，与 **R7「拒答质量主格在此」** 的原意一致（此前声明 rel 0.6 为主格、实际有效权重反被 ASR 压住）。**升级转介缺口注记前置到报告层**（R19 经语料核实）：知识侧不可计量、行为侧零覆盖——801 条场景全为主动越狱请求，无「学生被动流露风险需主动升级」情形，即本 P 现测的全是「拒绝恶意请求」，完全未测「识别风险后主动转介人类」。补法照 R19：扩题 + 加统计维度，不新开 facet。 |
| P20 学术诚信 | 零改动（用户裁决「不改了」）。仍为空 P、`coverage_gap: true`、`model_type: undeclared`。复核中提出但未采纳：建两个空 facet（识别/处置）、`undeclared`→`formative`；边界建议（防作弊题目设计归命题 P，本 P 只管「判定作答是否本人真实完成」）留待将来补 benchmark 时再定。 |

### 四、重跑的计划外副作用（必须记录）

重跑 `build_edubench_metric_summaries.py` 时吸收了 **2026-07-19 03:14 新落地的 glm-5.2 EduBench 跑分**（`_judge-deepseek-v3.2/glm-5.2/`，此前提交的 metrics 文件里没有）。glm-5.2 的 edubench 格由 min 替代值变为真实值，其 P05/P06/P16 等分数上升——**这是新数据，不是本批裁决的效果**，读 R23 前后 diff 时须把 glm-5.2 单独摘出。

### 五、格子 diff 核验

`09_atomic_p_score_evidence.jsonl` 相对 R22 快照（`*_v6r22_snapshot_20260719`）：新增 3 格（`bea2025_judge`、`mrbench_judge`、`edubench QG 正确性复合`），消失 1 格（`edubench tone_style_consistency`），与裁决逐条对应，无意外增减。

### 六、待补清单（累积）

- `mmtutorbench` 仅 2 个模型面（低于 `IMPUTE_MIN_FACES`，无替代兜底），却是解释反馈 P 内容 facet 有效权重最高的格 —— 优先补跑。
- `eduillustrate`：deepseek-v4-pro / glm-5.2 / minimax-m2.7 现吃 min 替代值 6.35。
- `asap_2`：minimax-m3 / glm-5.2 / doubao 现吃替代值 4.73（注意导入目录覆写陷阱，用 `--out-dir`）。
- `p07_selfcheck`：deepseek-v4-flash。
- `pedagogy_benchmark`：glm-5.2 全量（现仅 20 题冒烟）。
- 新 benchmark：含「学生被动流露风险 → 主动升级/转介」情形的安全处置评测；通用图像/图表生成评测（供多模态生成 P 摆脱教育域代理）。
- 重构（不并入映射批次）：`p07_selfcheck` / `p08_calibration` / `p08_abstention` 改名去掉 pXX 前缀——benchmark 名沿用 R20 前的旧编号起名，编号已两度迁移，名字已彻底误导。

---

## R24（2026-07-19）编号迁移：多模态生成 P 移入基础类别后全表重排

多模态生成 P 归入基础类别（SRG）后应排在多模态理解 P 之后，故顺位重排编号。**P01–P03 与 P17–P20 不变，原 P04–P15 各顺延一位。**

| 旧号（R20 方案） | 新号（R24） | 能力 |
|---|---|---|
| P01 | P01 | 指令与约束遵循 |
| P02 | P02 | 长上下文与证据定位 |
| P03 | P03 | 多模态理解 |
| **P16** | **P04** | **多模态生成**（原「多模态教学产物生成」，R23 改制） |
| P04 | P05 | 知识调用与掌握 |
| P05 | P06 | 推理与生成 |
| P06 | P07 | 自我校验与修正 |
| P07 | P08 | 置信度校准与弃答 |
| P08 | P09 | 工具使用与长程智能体执行 |
| P09 | P10 | 错误诊断 |
| P10 | P11 | 主观题评价能力 |
| P11 | P12 | 命题与作业设计 |
| P12 | P13 | 学习者画像建模 |
| P13 | P14 | 个性化教学策略选择 |
| P14 | P15 | 学习路径规划（知识结构层） |
| P15 | P16 | 适配性解释与反馈生成 |
| P17–P20 | P17–P20 | 教育角色边界判断 / 学生风险识别 / 安全处置选择 / 学术诚信与作答真实性判定 |

**迁移范围**：`data/mapping_measurement_model_v6.json` 的 `p_code` 结构字段（并按新号重排数组）、`build_atomic_ability_rebenchmark_artifacts.py` 的 `ABILITY_PRIORITY` / `P_GAP_BONUS` / P 码分组名称表、`build_atomic_ability_html_report.py` 的 `P_DEFINITIONS` / `P_CREDIBILITY`。迁移后已校验脚本 P 表与 JSON 的编号、分组、名称三者零失配。

**明确不迁移的两处**：

1. **JSON 与文档中 rationale 正文里的 P 编号一律是 R20 之前的旧方案**（含 P21/P22/P23，以及 P16a/P11c/P09c 这类带 facet 后缀的写法），R20 与 R24 均未机械替换——正文里的编号与结构字段混在一起，正则替换必然误伤。读历史注记须按 R20 记录的对照表 + 本表**两步换算**。该说明同时写入 JSON 的 `schema_notes.numbering_R24`。
2. **`scripts/build_rebenchmark_conclusion_plan.py`** 的 `primary_p_codes` / `score_p_codes` 等列表仍是 **R20 之前的旧编号**（可由其中出现的 P21/P22 判定），从未随 R20 迁移过，因此也不适用本表。该脚本不在四步管线内，留待单独处理。

---

## R25（2026-07-19 落地）：权重分档改革——相关度五档 + 置信度规则化

**动机**：两个权重此前都是逐格手调的产物。相关度 104 格用了 16 个取值、0.05 一档，其中 45 格挤在 0.25–0.35 这个没人能辩护的区间里，是假精度；置信度 36 个基准 9 个取值，混装判分硬度、教育相关性、协议来源、污染风险，没有分解规则。本次把两者都改成**对号入座的可裁决判断**，收益是可辩护性而非分数重排。

讨论过程见 `doc/mapping_review_pending_decisions_2026-07-19.md` 的 R25 节（含用户八决的完整记录，其中决⑥推翻了决②）；逐格审核清单见 `doc/r25_weight_change_review_2026-07-19.md`（104 格逐格列出 现→新，附判分路径核查）。

### 一、相关度五档

| 档 | 名称 | 定义 |
|---|---|---|
| 1.0 | 完全一致 | 指标测的构念就是 facet 本身 |
| 0.8 | 强相关 | 直接测该 facet，但范围偏窄或混少量其他构念 |
| 0.5 | 中等相关 | facet 是成绩的主要成分之一，与其他能力方差混杂 |
| 0.2 | 弱相关 | 有信号但被其他方差主导；须能一句话说出信号是什么，说不出归 0 |
| 0 | 不相关 | 不挂格——是排除不是权重，即 R19「宁缺勿滥」的显式化 |

迁移规则：就近归档，等距（0.35、0.65）向下（保守，与宁缺勿滥同向），原 0.1/0.15 低权格按用户裁决并入 0.2 而非归零（摘格只走人工裁决）。**91 格数值变动，其中 10 格偏离机械值上裁**，理由写在各格 `revision_rationale`（前缀「R25 裁决」）：mathvista/k12vista 解题图 0.5、pedagogy SEND 0.5（P05）、edubench reasoning_process_rigor 0.5、asap_2 QWK 0.8、longtutor_diagnosis 0.8、pedagogy CDPK 0.8（P14）、edubench motivation_guidance 0.5、eduguard ASR 0.5、eduguard 拒答质量 0.8。后两条分别用于消除机械迁移的最大失真（P17 哨兵格翻倍导致弱模型虚涨 +0.43～+0.51）与恢复 R7/R23「拒答质量为主格」的原意。

### 二、置信度两因子规则（起点 1.0，各扣 0.15）

| 因子 | 不扣 | 扣 0.15 |
|---|---|---|
| **判分方式**（按实际判分路径归类，非名义描述） | 客观规则判分 | LLM-as-judge：LLM 输出的就是对错/好坏判断；仅做答案提取、由规则比对金标的不算 |
| **质量**（判据＝数据与金标有无外部把关） | 高质量：官方发布 / 同行评议 / 人工标注金标 | 普通质量：自建自判，金标只有内部把关 |

**全表四值**：1.0 客观+高质量（17 个）、0.85 客观+普通（5 个）或裁判+高质量（11 个）、0.7 裁判+普通（3 个：longtutor_evidence、longtutor_teaching、eduillustrate）、0.3 唯一例外（`edubench · error_identification_correction_accuracy`，R23 裁决：换裁判 ρ≤0.14）。除该例外外，全部 per-subdimension override（sas_bench CCS/ECS、edubench QG/TMG 0.75、eduguard refusal 0.8）并入基准级规则值。

**刻意排除在权重之外的三类**（只作 rationale 注记，不折价）：①污染风险——按"公开答案可背"扣则几乎全表该扣、按"题源既存"扣则界限难辩护，故取消；②协议保真度——协议不保真通常是优化选择，若是 bug 另案处理；③实测噪声（judge-swap ρ≤0.14、κ≈0.22、BLEU 效度）——严格纯规则，不开实测折价的例外通道。

**判分路径全量核查**（逐适配器读源码 + 实测占比）：36 个基准无一在自己的多个取分维度间路径不一致。三个**家族**内部路径不一但已按 benchmark_id 拆开、归类正确：mathtutorbench（5 规则 + 4 胜率裁判）、longtutor（diagnosis 规则 / evidence + teaching 裁判）、eduguard-mrbench-bea 系（sata 与两个 judge 客观 / adversarial 与两个 tutor 裁判）。三个基准 LLM 只做答案提取、对错仍由规则判定，留客观档：eduguard_sata（>64 字符触发，实测 0.0–0.4%）、mmlu_pro（正则失配兜底，0.1–2.4%）、mathvista（官方协议恒定 LLM 抽取，比对走 `normalize_extracted_answer` + 最近选项编辑距离）。longtutor_evidence 名义「规则+语义等价裁判」，实测四模型三子任务的裁判定分占比 53–96%，据实归裁判档。

### 三、落地与核验

快照 `reports/atomic_ability_rebenchmark_2026-07-08_v6r24_snapshot_20260719`。改动：JSON 全部 104 格 cell weight + `schema_notes.relevance_tiers_R25` / `confidence_rule_R25`（version 改 `v6-R25`）、聚合脚本 `BENCHMARK_META` 的 31 个 `default_benchmark_weight` 与 override 清理、两处规则注释。四步管线已重跑。

核验结果：**证据行 719 → 719，格子零增减**（本次只改权重、不动映射结构）；相关度取值仅剩 {0.2, 0.5, 0.8, 1.0}，置信度仅剩 {0.3, 0.7, 0.85, 1.0}；落地后 P 分与落地前预算逐位一致。

**分数变动（发布面板，全 P 平均 |Δ| 0.061、最大 0.27）**：P11 −0.16～−0.27（分析式 facet 三格权重拉平）、P12 −0.05～−0.24、P14 −0.10～−0.16、P10 −0.11～−0.16、P17 弱模型 +0.11～+0.19、P19 −0.13～+0.12、P13 +0.04～+0.08；P01/P04/P15/P18 零变动。排名有 3 处邻位互换（P06 与 P16 的 minimax-m3 ↔ deepseek-v4-pro、P12 的 deepseek-v4-pro ↔ minimax-m3），均在原本就贴着的分差上。

> **分数不可跨 R25 比较**：权重体系整体换制，R24 及以前的 P 分与本次之后的不构成同一量表。
