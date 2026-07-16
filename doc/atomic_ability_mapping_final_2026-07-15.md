# 原子能力与 Benchmark 映射(定稿,2026-07-15;2026-07-16 三个待确认项已裁决,全部定稿)

这是当前的最终结论:原子能力清单是什么、每个能力由哪些 benchmark 的哪些维度测量、权重多少。不含历史沿革(变化记录见 `doc/benchmark_ability_mapping_v2_2026-07-15.md`)。机器可读版:`data/mapping_measurement_model_v2.json`(与本文档同步,2026-07-16)。

约定:权重是 facet 内的相对重要度,不归一。格子写法为 `benchmark · 取分维度`。原三处 ※ 待确认项已于 2026-07-16 裁决完毕(文末有裁决记录),全表均为定稿。

## 原子能力清单(21 项)

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
| P11 | 作答正误判定 | 判断学生作答的对错 | 单源+ |
| P12 | 错误位置定位 | 指出错误发生在作答的哪一步 | 单源+ |
| P13 | 错因归因 | 解释错误背后的原因/误概念 | 多源 |
| P14 | 主观题 rubric 评分能力 | 依据(或构建)评分标准评判主观作答与教学回复 | 学业评分多格;评判/生成 facet 暂无分 |
| P15 | 学术诚信与作答真实性判定 | 识别抄袭、代写等真实性问题 | **空白,暂未覆盖** |
| P16 | 学习者画像建模 | 从交互中建模学生的水平、需求与特征 | 弱(4 个子能力覆盖 2 个;P16a 2026-07-16 起有分) |
| P17 | 个性化教学策略选择 | 针对学生选择并执行合适的教学策略 | 多源·证据最厚 |
| P18 | 适配性解释与反馈生成 | 生成适配学生的解释、引导与反馈 | 多源·证据最厚 |
| P19 | 学习路径规划(知识结构层) | 基于知识先修结构规划学习顺序 | 单源·参考值(自建协议) |
| P20 | 教育角色边界判断 | 守住教育者的角色与行为边界 | 双源(知识 facet 与 P21/P22 同源) |
| P21 | 学生风险识别 | 识别学生消息中的风险信号 | 双源(同上) |
| P22 | 安全处置选择 | 对风险与越界请求选择正确处置方式 | 双源(同上) |

三条解释性口径:

- **P03 覆盖全部多模态理解**(不分深浅——难度用证据标签表达,不是构念维度),按材料类型分 facet。
- **P19 只管知识结构层**。"针对某个学生当前状态的个性化路径规划"是 P16 × P19 的组合能力,不是 P19 的缺口。
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

| facet | 格子 | 权重 | 性质 |
|---|---|---|---|
| 解题图像 | mathvista · 任务/题型准确率 | 0.35 | diagnostic |
| 解题图像 | olympiadbench · 多模态子集准确率 | 0.2 | 门槛 |
| 学科图表 | k12vista · 学科图多步理解 | 0.55 | diagnostic;裁判未校准,仅 4 个视觉模型,参考值 |
| 教学场景图文 | tutorbench · 多模态辅导质量 | 0.25 | education_core |
| 教学场景图文 | mmtutorbench · 多模态辅导六维 | 0.3 | diagnostic |
| 视频/音频 | (空白,暂未覆盖) | — | — |

### P05 知识调用与掌握(三 facet)

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

### P11 作答正误判定

| 格子 | 权重 | 性质 |
|---|---|---|
| mathtutorbench_solution_correctness | 0.6 | education_core |
| mathtutorbench_mistake_location | 0.1 | education_core |
| bea2025_judge · 判卷一致性 | 0.25 | 暂不计分(judge 任务) |

### P12 错误位置定位

| 格子 | 权重 | 性质 |
|---|---|---|
| mathtutorbench_mistake_location | 0.7 | education_core |
| sas_bench · CCS | 0.25 | education_core |

(2026-07-16 裁决:longtutor_diagnosis 不挂 P12——语义核实后,任务输入里没有任何解题步骤可供定位,改挂 P16a 主 + P13 副,见对应小节。)

### P13 错因归因

| 格子 | 权重 | 性质 |
|---|---|---|
| sas_bench · ECS(与人类专家错因标签一致性) | 0.7 | 核心证据 |
| bea2025_tutor · Mistake_Identification | 0.25 | LLM 裁判单维度分 |
| mrbench_tutor · Mistake_Identification | 0.25 | 同上 |
| edubench · 错误识别与纠正 | 0.25 | 方法学局限注记:换裁判分歧大 |
| mathtutorbench_mistake_correction | 0.2 | 只测改对与否,部分相关 |
| longtutor_diagnosis · 四类知识状态诊断 macro-F1 | 0.1 | 副挂(2026-07-16 裁决:标签名义是错因类别,但归因证据源是交互历史特征而非作答内容,与 ECS 锚动用的能力不同,仅作相邻证据;主挂 P16a) |
| bea2025_judge / mrbench_judge | 0.3 / 0.25 | 暂不计分(judge 任务) |

### P14 主观题 rubric 评分能力(三 facet)

| facet | 格子 | 权重 | 性质 |
|---|---|---|---|
| 学业作答评分 | sas_bench · QWK / CCS | 0.7 / 0.55 | education_core |
| 学业作答评分 | asap_2 · QWK | 0.65 | education_core |
| 教学回复评判 | bea2025_judge · 四维判卷 | 0.45 | 暂不计分 |
| 教学回复评判 | mrbench_judge · 八维判卷 | 0.45 | 暂不计分 |
| 生成 rubric | (空白,暂未覆盖) | — | — |

### P16 学习者画像建模(声明 4 个子能力,现覆盖 2 个)

| facet(子能力) | 格子 | 权重 |
|---|---|---|
| P16a 知识状态估计 | longtutor_diagnosis · 四类知识状态诊断 macro-F1 | 0.3(参考值) |
| P16d 支持需求判断·画像知识 | pedagogy_benchmark · SEND / 合并卡 | 0.35 / 0.3 |
| P16d 支持需求判断·画像应用 | edubench · 个性化适应与学习支持 | 0.3 |
| P16b 误概念识别 / P16c 情感与参与识别 | (空白,暂未覆盖) | — |

P16a 挂载依据(2026-07-16 裁决):longtutor_diagnosis 的输入是 199 条历史作答记录(题面+知识点+时间+对错)+ 当前题面,四个标签(Recall Failure / Conceptual Gap / Procedural Error / Transfer Deficit)是认知层失败机制,归因证据源是交互历史——正对"从作答历史判断学生会什么、不会什么"这个此前零覆盖的子能力。方法学注记:①类别不平衡(Procedural 506/1000),多数类基线 accuracy 0.506 高于三模型的 0.35–0.44,headline 用 macro-F1;②金标为特征决策矩阵 + 人工修订,非独立盲标,权重保守、性质参考值;③仅 3 个模型面,不补跑。

### P17 个性化教学策略选择(两 facet)

| facet | 格子 | 权重 |
|---|---|---|
| 教学策略知识 | pedagogy_benchmark · CDPK / SEND / 合并卡 | 0.35 / 0.3 / 0.3 |
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
| 教学产物生成 | edubench · QG/TMG/PCC 任务 ×(清晰启发/情景元素) | 0.4 | |
| 教学产物生成 | eduillustrate · 视觉讲解八维 | 0.3 | |

### P19 学习路径规划(知识结构层)

| 格子 | 权重 | 性质 |
|---|---|---|
| mooccube · 先修关系推理 | 0.7 | 规则判分零裁判;自建协议、无公开基线,benchmark 权重 0.7,参考值 |

### P20 教育角色边界判断(两 facet)

| facet | 格子 | 权重 | 性质 |
|---|---|---|---|
| 安全知识 | eduguard_sata · SATA RFS | 0.35 | 与 P21/P22 同源,不构成互证 |
| 安全知识 | mrbench_judge | 0.3 | 暂不计分 |
| 边界行为 | eduguard_adversarial · ASR | 0.3 | |
| 边界行为 | mrbench_tutor · Tutor_Tone | 0.25 | |
| 边界行为 | eduguard_adversarial · 拒答质量 | 0.15 | |

### P21 学生风险识别(两 facet)

| facet | 格子 | 权重 | 性质 |
|---|---|---|---|
| 安全知识 | eduguard_sata · SATA RFS | 0.3 | 同源注记同上 |
| 对抗鲁棒 | eduguard_adversarial · ASR | 0.25 | |

### P22 安全处置选择(两 facet)

| facet | 格子 | 权重 | 性质 |
|---|---|---|---|
| 安全知识 | eduguard_sata · SATA RFS | 0.35 | 同源注记同上 |
| 对抗鲁棒 | eduguard_adversarial · 拒答质量 | 0.6 | 主格 |
| 对抗鲁棒 | eduguard_adversarial · ASR | 0.45 | |

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
| sas_bench | 简答题评分(QWK/CCS/ECS 三指标) | 对人类标注一致性 | P14、P13、P12、P02、P05、P06 |
| pedagogy_benchmark | 教学专业知识选择题(CDPK/SEND) | 精确匹配 | P05、P16、P17 |
| edubench | 5 任务生成 × 12 裁判指标(取指标级分) | LLM 裁判(deepseek-v3.2,原论文设定) | P05、P06、P13、P16、P17、P18 |
| mathtutorbench 家族(9 任务) | 数学辅导对话(解题/判对/定位/纠错/脚手架/教学法/苏格拉底) | 精确匹配 + LLM 裁判胜率 | P02、P05、P06、P07、P11、P12、P13、P17、P18 |
| tutorbench | 多模态辅导质量 | LLM 裁判 | P03、P17、P18 |
| mmtutorbench | 多模态数学辅导(六维 rubric) | LLM 裁判 | P03、P17、P18 |
| bea2025_tutor / mrbench_tutor | 生成辅导回复,固定裁判逐维度标注 | LLM 裁判单维度分 | P13、P17、P18、P20(mrbench) |
| bea2025_judge / mrbench_judge | 被测模型当裁判,对人类金标 | 一致性/F1 | P11、P13、P14、P20(均暂不计分) |
| eduguard_sata | 教学伤害多选(SATA) | 规则判分(RFS) | P20、P21、P22(同源) |
| eduguard_adversarial | 对抗越狱 + 拒答质量 | 两阶段 LLM 裁判 | P20、P21、P22、P18 |
| eduillustrate | 生成教学图示质量 | LLM 裁判八维 | P10、P18 |
| longtutor 三任务 | 长对话辅导(证据/诊断/教学) | 语义裁判 / 规则 F1 / LLM 裁判四维 | P02(evidence)、P16a 主 + P13 副(diagnosis)、P17(teaching)——2026-07-16 裁决定稿 |

## 裁决记录(2026-07-16,原三处待确认项全部落定)

1. **longtutor_evidence → P02(0.7),挂**。P02 由纯代理转直接测量;三模型面 accuracy 0.787/0.807/0.791 挤得很紧,成熟度按"直接测量·区分度待验证"表述,等 13 号检查配对结果。
2. **longtutor_diagnosis → P16a 主挂(0.3,参考值)+ P13 副挂(0.1),不挂 P12**。语义核实:输入无解题步骤(P12 排除);四标签是认知层失败机制、归因证据源是交互历史特征而非作答内容,构念正主是 P16a"知识状态估计"(此前零覆盖);与 sas_bench ECS 动用的能力不同,P13 仅作相邻证据副挂。附带方法学注记(类别不平衡、金标决策矩阵模板化风险)见 P16 小节。
3. **longtutor_teaching → P17 执行 facet(0.3),挂**。前置条件(4 维全 0 bug 修复后重算验证)已满足:三个模型 valid_judgements 均 1001,strategy_alignment 3.68–4.13 有区分度。取 strategy_alignment + history_utilization 两维,coherence/appropriateness 不入分。

同日决定:**longtutor 三任务与 mrbench_tutor / bea2025_tutor 的模型面缺口不补跑**(longtutor 缺 MiniMax-M2.7、doubao-seed-2.0-pro;mrbench/bea 缺 deepseek-v4-pro、doubao-seed-2.0-pro 的生成),v2 聚合与 13 号检查按 3 模型面注记。

机器可读落盘:`data/mapping_measurement_model_v2.json`(2026-07-16,含全部 R1-R16 裁决 + 本页三项)。
