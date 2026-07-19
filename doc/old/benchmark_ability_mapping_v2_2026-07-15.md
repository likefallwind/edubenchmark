# 原子能力 × Benchmark 映射 v2（2026-07-15）

M3 裁决(R1-R16,全部裁完)落地后的**最终映射关系**。裁决口径见 `doc/m3_adjudication_sheet_2026-07-14.md` 文末"裁决结果"表;本文档是它的展开——现在原子能力清单长什么样、每个 P 具体挂哪些 benchmark、权重多少。

标注约定:
- **【裁决】** = M3 裁决直接定下的数字/结构;
- **【草案】** = 裁决给了方向但具体权重由我起草,待首轮 v2 聚合跑出来后核对;
- **【待确认】** = 裁决单没覆盖的新挂载提案(longtutor 三任务)——**2026-07-16 已全部裁决**,结果:evidence→P02 挂(区分度待验证)、diagnosis→P16a 主 0.3 + P13 副 0.1(P12 排除)、teaching→P17 挂;详见定稿文档文末"裁决记录";
- 无标注 = 沿用 v1,裁决未触及。
- 权重是 facet 内的相对重要度(同 v1 约定,不归一)。

## 一、能力清单总览(裁决后 21 个 P)

P04 并入 P03,编号保留作墓碑不复用;其余编号不变,避免全库改引用。

| P | 名称(裁决后) | 变化 | 测量成熟度 | 主要证据来源 |
|---|---|---|---|---|
| P01 | 指令与约束遵循 | R13:直接测量只认 IFEval | **直接测量**(单源) | ifeval + 三个门槛卷 |
| P02 | 长上下文与证据定位 | R9:标纯代理;2026-07-16 挂 longtutor_evidence | **直接测量·区分度待验证** | longtutor_evidence + 搭车分 |
| P03 | **多模态理解**(原 P03+P04 合并) | R5:合并,facet 按材料类型;摘除 eduillustrate | 多源(学科图表 facet 为参考值) | mathvista、olympiadbench、k12vista、tutorbench、mmtutorbench |
| ~~P04~~ | (已并入 P03) | R5 | — | — |
| P05 | 知识调用与掌握 | R1:edubench 改指标级取分 | 多源·成熟(知识簇天花板,门槛性质) | mmlu_pro、ceval、agieval、pedagogy_benchmark、edubench 等 |
| P06 | 推理与生成 | R8:pedagogy_benchmark 移出;R1 | 多源·成熟 | olympiadbench、mathvista、agieval、edubench·推理严谨 等 |
| P07 | 自我校验与修正 | 已有直接测量(7-12 接入) | **直接测量**(单源) | p07_selfcheck |
| P08 | 置信度校准与弃答 | 已有直接测量(7-11 接入) | **直接测量**(双任务) | p08_calibration、p08_abstention |
| P09 | 工具使用与长程智能体执行 | — | **空白**(领域空白,报告诚实标注) | 无 |
| P10 | 多模态教学产物生成 | — | 单源 | eduillustrate |
| P11 | 作答正误判定 | — | 单源+ | mathtutorbench 两任务 |
| P12 | 错误位置定位 | 2026-07-16:longtutor_diagnosis 语义核实后**不挂**(输入无解题步骤) | 单源+ | mathtutorbench_mistake_location、sas_bench CCS |
| P13 | 错因归因 | R6 降权;R2 换单维度分;R1 加 edubench 指标 | 多源 | sas_bench ECS(核心)、bea/mrbench、edubench |
| P14 | **主观题 rubric 评分能力**(R3 重定义) | 三 facet,含空白"生成 rubric" | 学业作答多格,评判 facet 暂不计分 | asap_2、sas_bench、(bea/mrbench_judge) |
| P15 | 学术诚信与作答真实性判定 | — | **空白**(领域空白) | 无 |
| P16 | 学习者画像建模 | R12:4 子能力声明,现仅覆盖 1 个 | 弱(1/4 子能力有分) | pedagogy_benchmark SEND、edubench·个性化适应 |
| P17 | 个性化教学策略选择 | R4:执行 facet **不细分**;R2/R1/R11 | 多源·证据最厚 | mathtutorbench 5 任务、bea/mrbench_tutor、tutorbench、mmtutorbench、edubench |
| P18 | 适配性解释与反馈生成 | R2(Actionability 减半)、R7(拒答降权)、R1 | 多源·证据最厚 | 同上 + eduguard 拒答、eduillustrate |
| P19 | 学习路径规划(**定义澄清:知识结构层**) | R16:不拆 a/b;学习者状态路径=P16×P19 组合能力 | 单源·参考值(自建协议) | mooccube 先修推理 |
| P20 | 教育角色边界判断 | R10:与 P21/P22 知识 facet 同源,注明不互证 | 双源(有同源问题) | eduguard 两任务、mrbench_tutor·Tutor_Tone |
| P21 | 学生风险识别 | 同上 | 双源(同源问题) | eduguard 两任务 |
| P22 | 安全处置选择 | R7:拒答质量主挂这里 | 双源(同源问题) | eduguard 两任务 |

## 二、edubench 取分方式(R1,跨多个 P 的横切变化)

edubench 不再以 5 个任务(IP/QG/TMG/PLS/PCC)的**任务均分**挂 P,改为按 **12 个原生裁判指标**逐维度取分(R14 否决后口径:12 维全部可用,不做裁判稳健性筛选;换裁判实验结论进报告方法学局限)。指标 → P 分配:

| edubench 指标 | 挂到 | 说明 |
|---|---|---|
| 基础事实准确性 | P05 | 知识簇,均分 9+,天花板 → 门槛性质【草案】 |
| 领域知识准确性 | P05 | 同上【草案】 |
| 推理过程严谨性 | P06 | 【草案】 |
| 错误识别与纠正 | P13 | R14 否决后入映射;**方法学局限注记**:换裁判 ρ≤0.14、三裁判均分 4.6/7.4/8.7【草案】 |
| 个性化适应与学习支持 | P16(画像应用)+ P17(策略执行) | 换裁判稳健(ρ 0.77-0.81)【草案】 |
| 动机引导与积极反馈 | P18 | 换裁判稳健(ρ 0.61-0.68)【草案】 |
| 表达清晰简洁启发 | P18 | 【草案】 |
| 高阶思维能力培养 | P18 + P06 | 换裁判稳健(ρ 0.63-0.73),视任务挂【草案】 |
| 情景元素融合 | P17 | 【草案】 |
| 语气风格一致性 | P18(小权重) | P20 曾是候选,构念对齐弱,不挂【草案】 |
| 指令遵循 | **不挂** | 【裁决 R13】模型排名级与知识指标 ρ≈0.96,无独立信息;P01 走 IFEval |
| 内容相关与范围控制 | **不挂** | 与知识/指令高相关簇(模型级 ρ 0.92-1.00),同理无独立信息【草案】 |

两条执行规则:①细挂到(任务 × 指标)格子层,**死格子不进映射**(题级 SD<0.5 的格子,如 PCC 上 4 个指标——裁判在该任务上不用这些指标区分回答);②数据源是同事的逐题原始判分(`reports/eval/edubench/`,裁判 deepseek-v3.2,尊重原论文设定)。

## 三、逐 P 明细

### P01 指令与约束遵循(reflective)

| 格子 | 权重 | tier | 变化 |
|---|---|---|---|
| ifeval · prompt 严格准确率 | 1.0 | 直接测量·规则判分 | 7-12 接入 |
| mmlu_pro / ceval / agieval · 格式遵循 | 0.1 / 0.15 / 0.2 | foundation_gate | 沿用 |
| p08_abstention · 弃答约束 | 0.15 | diagnostic | 沿用 |

edubench·指令遵循不挂【裁决 R13】。

### P02 长上下文与证据定位(reflective,R9 标纯代理)

| 格子 | 权重 | tier | 变化 |
|---|---|---|---|
| asap_2 · QWK | 0.2 | 代理(搭车) | 沿用,标 proxy_only |
| sas_bench · QWK / CCS | 0.15 / 0.2 | 代理(搭车) | 同上 |
| mathtutorbench solution_correctness / mistake_location | 0.15 / 0.2 | 代理(搭车) | 同上 |
| **longtutor_evidence · 长对话证据抽取** | **0.7** | **直接测量** | **【已裁决 2026-07-16】挂**——P02 从纯代理转单源直接测量;三模型面 0.787/0.807/0.791 区分度待验证,报告按"直接测量·区分度待验证"表述 |

### P03 多模态理解(R5 合并 P03+P04;facet 按材料类型)

| facet | 格子 | 权重 | 变化 |
|---|---|---|---|
| 解题图像 | mathvista | 0.35 | 沿用 |
| 解题图像 | olympiadbench | 0.2 | 沿用 |
| 学科图表 | **k12vista** | **0.55** | 【裁决 R15】新挂;tier diagnostic,报告标注"裁判未校准";仅 4 个视觉模型,成熟度参考值 |
| 教学场景图文 | tutorbench | 0.25 | 沿用 |
| 教学场景图文 | mmtutorbench | 0.3 | 沿用 |
| 视频/音频 | (空白标缺口) | — | 【裁决 R5】 |
| ~~eduillustrate~~ | — | — | 【裁决 R5】摘除(生成≠感知,已是 P10 主格) |

### P05 知识调用与掌握(formative,三 facet)

| facet | 格子 | 权重 | 变化 |
|---|---|---|---|
| 学科知识调用 | mmlu_pro 0.6 / ceval 0.6 / agieval 0.35 / olympiadbench 0.25 / mathvista 0.2 / mtb_problem_solving 0.3 | — | 沿用 |
| 学科知识调用 | **k12vista** | **0.15** | 【裁决 R15】 |
| 学科知识调用 | **mooccube** | **0.20** | 【裁决 R16】 |
| 教学专业知识 | pedagogy_benchmark CDPK 0.45 / SEND 0.35 / 合并卡 0.4 | — | 沿用 |
| 生成中的知识运用 | ~~edubench IP/PCC/QG/TMG 任务分~~ → **edubench·基础事实准确性 0.3 + edubench·领域知识准确性 0.35** | — | 【裁决 R1+草案权重】任务分退役,指标分顶上 |
| 生成中的知识运用 | asap_2 0.15 / sas QWK 0.15 / sas ECS 0.2 / mtb_pedagogy ×2 0.25 / mtb_scaffolding ×2 0.15 | — | 沿用 |

### P06 推理与生成(formative,两 facet)

| facet | 格子 | 权重 | 变化 |
|---|---|---|---|
| 解题推理 | mmlu_pro 0.3 / ceval 0.25 / agieval 0.45 / olympiadbench 0.55 / mathvista 0.45 / mtb_problem_solving 0.6 | — | 沿用 |
| 解题推理 | ~~pedagogy_benchmark 0.2~~ | — | 【裁决 R8】移出 |
| 解题推理 | **k12vista 0.30** / **mooccube 0.10** | — | 【裁决 R15/R16】 |
| 生成与归因推理 | ~~edubench QG 0.35 / TMG 0.25~~ → **edubench·推理过程严谨性 0.35 + edubench·高阶思维 0.2** | — | 【裁决 R1+草案权重】 |
| 生成与归因推理 | sas ECS 0.1 / mtb_mistake_correction 0.2 | — | 沿用 |

### P07 自我校验与修正 / P08 置信度校准与弃答

沿用 7-11/7-12 接入后的结构,不变:
- **P07**:p07_selfcheck 0.85(直接测量)+ mtb_problem_solving 0.1、mtb_solution_correctness 0.25、p08_calibration 0.2(搭车)。
- **P08**:校准 facet p08_calibration 0.8 + p07_selfcheck 0.15;弃答 facet p08_abstention 0.85。

### P09 / P15(空白)

无任何挂载。真领域空白,报告标"暂未覆盖"(发布必做清单已确认此口径)。

### P10 多模态教学产物生成

eduillustrate 0.45 主格,沿用。(它从 P03 摘除后,这里是唯一挂载。)

### P11 作答正误判定

mtb_solution_correctness 0.6 / mtb_mistake_location 0.1 / bea2025_judge 0.25(excluded,暂不计分)。沿用。

### P12 错误位置定位

| 格子 | 权重 | 变化 |
|---|---|---|
| mathtutorbench_mistake_location | 0.7 | 沿用 |
| sas_bench · CCS | 0.25 | 沿用 |
| ~~longtutor_diagnosis~~ | — | **【已裁决 2026-07-16】不挂 P12**——语义核实:输入是历史作答记录+当前题面,无任何解题步骤可定位;四标签是认知层失败机制,改挂 **P16a 主(0.3,参考值)+ P13 副(0.1)**,依据与方法学注记见定稿文档 P16 小节 |

### P13 错因归因

| 格子 | 权重 | 变化 |
|---|---|---|
| sas_bench · ECS | 0.7 | 沿用,核心证据【裁决 R6 确认】 |
| mathtutorbench_mistake_correction | ~~0.45~~ → **0.20** | 【裁决 R6】只看改没改对,不考错因;天花板格 |
| bea2025_tutor · **Mistake_Identification 单维度分** | 0.25 | 【裁决 R2】原复合 pass rate 0.25 换成干净维度分 |
| **mrbench_tutor · Mistake_Identification 单维度分** | **0.25** | 【裁决 R2+草案】v1 此格不存在(pass rate 只挂了 P17/P18/P20),补齐 |
| **edubench · 错误识别与纠正** | **0.25** | 【裁决 R1/R14+草案】入映射;报告方法学局限注明换裁判分歧数字 |
| bea2025_judge / mrbench_judge | 0.3 / 0.25 | excluded 暂不计分,沿用(未来归 P14 教学回复评判 facet,见 R3) |

### P14 主观题 rubric 评分能力(R3 重定义,三 facet)

| facet | 格子 | 权重 | 变化 |
|---|---|---|---|
| 学业作答评分 | asap_2 · QWK | 0.65 | 沿用 |
| 学业作答评分 | sas_bench · QWK / CCS | 0.7 / 0.55 | 沿用 |
| 教学回复评判 | bea2025_judge / mrbench_judge | 0.45 / 0.45 | 沿用 excluded(judge 任务暂不进模型分;启用时不与学业评分混,这正是拆 facet 的意义) |
| 生成 rubric | (空白标缺口) | — | 【裁决 R3】无现有测量,声明缺口 |

### P16 学习者画像建模(R12:按 4 子能力声明,现仅覆盖"画像应用"1 个)

| facet | 格子 | 权重 | 变化 |
|---|---|---|---|
| 画像知识 | pedagogy_benchmark SEND 0.35 / 合并卡 0.3 | — | 沿用 |
| 画像应用 | ~~edubench PLS 任务分 0.3~~ → **edubench·个性化适应与学习支持(PLS 任务)0.3** | — | 【裁决 R1】指标级取分,构念更对题 |
| (另 3 个子能力) | 空白标缺口 | — | 【裁决 R12】7-11 细分声明保留 |

### P17 个性化教学策略选择(formative;执行 facet 不细分【裁决 R4】)

| facet | 格子 | 权重 | 变化 |
|---|---|---|---|
| 教学策略知识 | pedagogy_benchmark CDPK 0.35 / SEND 0.3 / 合并卡 0.3 | — | 沿用 |
| 教学策略执行 | mtb_scaffolding ×2 | 0.5 | 沿用 |
| 教学策略执行 | mtb_pedagogy ×2 | 0.45 | 沿用 |
| 教学策略执行 | mathtutorbench_socratic | 0.65 | 【裁决 R11,7-12 已执行】 |
| 教学策略执行 | tutorbench 0.35 / mmtutorbench 0.3 | — | 沿用 |
| 教学策略执行 | bea2025_tutor · **Providing_Guidance 单维度分** | 0.3 | 【裁决 R2】替换复合 pass rate |
| 教学策略执行 | mrbench_tutor · **Providing_Guidance 单维度分** | 0.3 | 【裁决 R2】同上 |
| 教学策略执行 | ~~edubench IP 0.4 / PCC 0.3 / PLS 0.45~~ → **edubench·个性化适应 0.4 + edubench·情景元素融合 0.25** | — | 【裁决 R1+草案权重】 |
| 教学策略执行 | **longtutor_teaching · strategy_alignment + history_utilization** | **0.3** | **【已裁决 2026-07-16】挂**——重算验证完成(三模型 valid 1001,strategy_alignment 3.68–4.13 有区分度) |

### P18 适配性解释与反馈生成(formative,两 facet)

| facet | 格子 | 权重 | 变化 |
|---|---|---|---|
| 对话式反馈与引导 | mtb_mistake_correction 0.35 / mtb_pedagogy ×2 0.3 / mtb_scaffolding ×2 0.35 / socratic 0.35 / tutorbench 0.4 / mmtutorbench 0.4 | — | 沿用 |
| 对话式反馈与引导 | bea2025_tutor · **Actionability 单维度分** | ~~0.45~~ → **0.20** | 【裁决 R2】换单维度分,且**权重减半**(该维度裁判校准 κ 仅 0.22,vs 识错 0.38;校准数字进方法学局限) |
| 对话式反馈与引导 | mrbench_tutor · **Actionability 单维度分** | ~~0.45~~ → **0.20** | 【裁决 R2】同上 |
| 对话式反馈与引导 | eduguard_adversarial · 拒答质量 | ~~0.25~~ → **0.10** | 【裁决 R7】主体是安全处置,主挂 P22 |
| 对话式反馈与引导 | ~~edubench IP 0.35 / PLS 0.25~~ → **edubench·动机引导 0.35 + edubench·清晰启发 0.3 + edubench·高阶思维 0.25 + edubench·语气一致 0.1** | — | 【裁决 R1+草案权重】 |
| 教学产物生成 | **edubench·(QG/TMG/PCC 任务 × 清晰启发/情景元素指标)0.4** | — | 【裁决 R1+草案】替换原 PCC 0.45 / QG 0.35 / TMG 0.4 任务分;R7 裁决"QG 不动",故 QG 任务份额不降、不移 P06 |
| 教学产物生成 | eduillustrate | 0.3 | 沿用 |

### P19 学习路径规划(R16:定义澄清为**知识结构层**的路径规划)

| 格子 | 权重 | 变化 |
|---|---|---|
| **mooccube · 先修关系推理** | **0.70** | 【裁决 R16】首个测量;bw 0.70(自建协议、无公开基线);规则判分零裁判 |

定义注记【裁决 R16】:"针对学生当前状态的个性化路径规划"是 **P16 × P19 的组合能力**,不是 P19 的缺口;报告按此表述,不设 P19b。成熟度:参考值(单源、自建协议)。

### P20 / P21 / P22(安全三 P;R10:知识 facet 同源注记)

| P | facet | 格子 | 权重 | 变化 |
|---|---|---|---|---|
| P20 | 安全知识 | eduguard_sata | 0.35 | 沿用;【裁决 R10】报告注明三 P 此 facet 同源、不构成互证;类别标注 todo 发布后做 |
| P20 | 安全知识 | mrbench_judge | 0.3 | excluded 沿用 |
| P20 | 边界行为 | mrbench_tutor · **Tutor_Tone 单维度分** | 0.25 | 【裁决 R2 延伸+草案】原 pass rate 格换成语气维度(Encouraging/Neutral/Offensive),构念对齐"角色边界" |
| P20 | 边界行为 | eduguard_adversarial ASR 0.3 / 拒答质量 0.15 | — | 沿用 |
| P21 | 安全知识 | eduguard_sata | 0.3 | 沿用+同源注记 |
| P21 | 对抗鲁棒 | eduguard_adversarial ASR | 0.25 | 沿用 |
| P22 | 安全知识 | eduguard_sata | 0.35 | 沿用+同源注记 |
| P22 | 对抗鲁棒 | eduguard_adversarial ASR 0.45 / **拒答质量 0.6** | — | 沿用(拒答质量主格在此,R7 只动了它在 P18 的副挂) |

## 四、遗留与执行清单

1. ~~三个【待确认】格子~~ **已裁决(2026-07-16)**:evidence→P02 挂(区分度待验证)、diagnosis→P16a 主 0.3 + P13 副 0.1(P12 排除)、teaching→P17 挂。已进 `data/mapping_measurement_model_v2.json`。
2. **【草案】权重**(主要是 edubench 指标级格子)在 v2 首轮聚合 + 13 号检查跑完后核对:凡是死格子(题级 SD<0.5)剔除,凡是与同 facet 内其他格子跨模型负相关的红旗格子回到裁决。
3. mrbench 的 **Revealing_of_the_Answer**(不泄答案)维度现在没挂任何 P——它是脚手架质量的负向信号,备选挂 P17 执行 facet,暂不动,记录在案。
4. ~~数据依赖~~ **已解除(2026-07-16 核对)**:裁判 error 断点续判跑完,6 个裁判依赖 benchmark × 发布 5 模型去重后 error 全 0,mrbench/bea/mathtutorbench 分数解禁;longtutor_teaching 三模型均为全量真分(valid 1001)。**补跑决定(2026-07-16):不补**——mrbench_tutor/bea2025_tutor 缺 deepseek-v4-pro、doubao-seed-2.0-pro 生成,longtutor 缺 MiniMax-M2.7、doubao-seed-2.0-pro,均维持 3 模型面并在配对检验与报告中注记。
5. ~~产出 mapping_measurement_model_v2.json~~ **已落盘(2026-07-16)** → 剩:聚合脚本 MAPPINGS 切 v2(含 edubench 指标级取分与 bea/mrbench 单维度分的取数改造)→ 重跑聚合 + 13 号检查 → v1/v2 对比(21 P 口径,P03 合并与 P04 墓碑在对比中说明)→ M4 双报告。

## 五、v3 增量(2026-07-16,裁决 R17:P11/P12/P13 合并)

- **原 P11 作答正误判定 / P12 错误位置定位 / P13 错因归因合并为 P11「错误诊断」**,三项降为 facet(P11a 判定 / P11b 定位 / P11c 归因),P12/P13 墓碑保留,清单 21→19。依据全部 benchmark 无关(P11/P12 拆分不满足准入规则;P13 可拆但不必拆,口径与 P03/P04 合并一致);详细论证与方法学披露(见数后修订)见 `doc/atomic_ability_mapping_final_2026-07-15.md` 裁决记录 R17。
- **格子迁移**:原 P12 两格→P11b、原 P13 八格→P11c,权重/evidence_tier/注记原样;原 P11 内删除两个同源重复格(mathtutorbench_mistake_location 0.1、bea2025_judge 0.25 占位),121→119 格。
- **落盘与重跑**:`data/mapping_measurement_model_v3.json`(v2 保留为 R17 前快照);聚合与 13 号检查已切 v3 重跑,v2 口径产物快照在 `reports/atomic_ability_rebenchmark_2026-07-08_v2_snapshot_20260716/`;HTML 报告改出 `html_report/atomic_ability_benchmark_v3_report_2026-07-16.html`(v2 版保留)。
