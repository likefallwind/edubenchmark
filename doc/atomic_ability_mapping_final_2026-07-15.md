# 原子能力与 Benchmark 映射(定稿,2026-07-15)

这是当前的最终结论:原子能力清单是什么、每个能力由哪些 benchmark 的哪些维度测量、权重多少。不含历史沿革(变化记录见 `doc/benchmark_ability_mapping_v2_2026-07-15.md`)。

约定:权重是 facet 内的相对重要度,不归一。格子写法为 `benchmark · 取分维度`。带 ※ 的格子尚待确认(文末列出),其余均为定稿。

## 原子能力清单(21 项)

| P | 名称 | 一句话定义 | 测量成熟度 |
|---|---|---|---|
| P01 | 指令与约束遵循 | 按显式指令和格式/行为约束产出 | 直接测量(规则判分) |
| P02 | 长上下文与证据定位 | 在长材料/长对话中定位并引用相关证据 | 代理(※待 longtutor 转直接) |
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
| P16 | 学习者画像建模 | 从交互中建模学生的水平、需求与特征 | 弱(4 个子能力仅覆盖 1 个) |
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
| ※ longtutor_evidence · 长对话证据抽取 | 0.7 | 直接测量候选 |
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
| ※ longtutor_diagnosis · 长对话错误诊断 F1 | 0.3 | 规则判分 |
| sas_bench · CCS | 0.25 | education_core |

### P13 错因归因

| 格子 | 权重 | 性质 |
|---|---|---|
| sas_bench · ECS(与人类专家错因标签一致性) | 0.7 | 核心证据 |
| bea2025_tutor · Mistake_Identification | 0.25 | LLM 裁判单维度分 |
| mrbench_tutor · Mistake_Identification | 0.25 | 同上 |
| edubench · 错误识别与纠正 | 0.25 | 方法学局限注记:换裁判分歧大 |
| mathtutorbench_mistake_correction | 0.2 | 只测改对与否,部分相关 |
| bea2025_judge / mrbench_judge | 0.3 / 0.25 | 暂不计分(judge 任务) |

### P14 主观题 rubric 评分能力(三 facet)

| facet | 格子 | 权重 | 性质 |
|---|---|---|---|
| 学业作答评分 | sas_bench · QWK / CCS | 0.7 / 0.55 | education_core |
| 学业作答评分 | asap_2 · QWK | 0.65 | education_core |
| 教学回复评判 | bea2025_judge · 四维判卷 | 0.45 | 暂不计分 |
| 教学回复评判 | mrbench_judge · 八维判卷 | 0.45 | 暂不计分 |
| 生成 rubric | (空白,暂未覆盖) | — | — |

### P16 学习者画像建模(声明 4 个子能力,现覆盖 1 个)

| facet | 格子 | 权重 |
|---|---|---|
| 画像知识 | pedagogy_benchmark · SEND / 合并卡 | 0.35 / 0.3 |
| 画像应用 | edubench · 个性化适应与学习支持(PLS 任务) | 0.3 |
| (其余 3 个子能力) | (空白,暂未覆盖) | — |

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
| 教学策略执行 | ※ longtutor_teaching · strategy_alignment + history_utilization | 0.3 |
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
| longtutor 三任务 ※ | 长对话辅导(证据/诊断/教学) | F1 / LLM 裁判 | ※P02、※P12、※P17(待确认) |

## 待确认项(仅此三处,其余均为定稿)

1. ※ longtutor_evidence → P02(0.7):挂上后 P02 由纯代理转直接测量;
2. ※ longtutor_diagnosis → P12(0.3):若语义核实更偏"归因"则改挂 P13;
3. ※ longtutor_teaching → P17 执行 facet(0.3):等分数重算验证后挂。
