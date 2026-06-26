# AI 教育原子能力重估：从 Benchmark 证据反推的候选框架

日期：2026-06-25

> 更新说明：本文件保留为第一版候选框架。按 `doc/atomic_principle.md` 进一步收紧后的逐条审查和最终原子能力，见 `doc/atomic_ability_strict_principle_2026-06-25.md`。

本文只完成第一步：基于当前仓库已经整理的 benchmark、数据资源、优先级计划和部分实测进度，重新判断“哪些能力值得作为原子能力候选”。第二步，即基于已做实验结果和具体题目验证、拆分、合并这些能力，列在文末 TODO。

## 结论摘要

`doc/benchmark_atomic_ability_matrix.md` 里的 D01-D23 更适合作为“benchmark 覆盖索引”，不适合作为最终原子能力体系。主要问题是它把以下几类东西混在一起：

- 能力：例如错误定位、rubric 评分、脚手架引导。
- 场景：例如标准化考试、中文 K12、课堂视觉行为。
- 学科或地域标签：例如中文本土知识、K12 学科体系。
- 题型或输出形式：例如选择题、作文、短答案、交互式 HTML。
- 评测协议或产品层：例如知识追踪 protocol、教育垂类系统端到端能力。

更合理的做法是：

1. 用旧 D 码继续做证据索引，方便追踪 benchmark 来源。
2. 新增一层更接近机制的 A 码，作为“候选原子能力”。
3. 把语言、学科、学段、题型、模态、难度、风险等级作为标签，而不是原子能力本身。
4. 把真实学习效果、教师采纳、产品工作流作为验证层，不直接命名为原子能力。

## 依据与口径

本次重估参考了以下仓库内材料：

- 原子能力原则：`doc/atomic_principle.md`
- 旧矩阵：`doc/benchmark_atomic_ability_matrix.md`
- RE_BENCHMARK_V1 分类与主测计划：`doc/re_benchmark_v1.md`、`doc/priority_benchmark_plan.md`
- 当前执行进度：`doc/edu_eval_progress_and_arena.md`
- v1 题目与评价标准：`doc/AI_EDU_BENCHMARK_V1.md`、`data/benchmark_v1_2026-05-18/capability_criteria.jsonl`
- benchmark 目录与映射：`reports/2026-05-13/ai_edu_unified_benchmark_framework_2026-05-13.md`、`reports/2026-05-13/ai_edu_benchmark_catalog_2026-05-13.md`、`data/exhaustive_2026-05-13/benchmarks.jsonl`、`data/exhaustive_2026-05-13/dimension_mapping.jsonl`
- 数据可获取状态：`data/exhaustive_2026-05-13/dataset_acquisition_report.md`
- 已做实验与报告索引：`reports/re_benchmark_v1/RE_BENCHMARK_V1_RESEARCH_REPORT.md`、`reports/eval/*/*/summary.json`

结构化覆盖统计的关键事实：

- `data/exhaustive_2026-05-13/benchmarks.jsonl` 收录 78 个 benchmark/resource。
- `data/benchmark_v1_2026-05-18/capability_criteria.jsonl` 收录 24 个旧 D 码、84 条评价标准。
- 数据状态为：58 个有下载命令但未批量下载，19 个需要人工/元数据访问，1 个论文或发布待定。
- 当前实测已覆盖 MMLU-Pro、AGIEval、OlympiadBench、MathVista、EduGuard-Bench、MathTutorBench 若干子任务、EduIllustrate 等；但很多学习日志、课堂、资源推荐类仍主要是 protocol/resource，而不是统一 LLM leaderboard。

## 旧矩阵的主要问题

### 1. D01-D03 混合了知识、题型、地域和考试来源

`通用学科知识与选择题答题`、`中文本土知识与 K12 学科体系`、`标准化考试与资格考试推理` 都很重要，但它们不是同一层级的原子能力。

真正的底层能力更像：

- 概念和事实知识是否可靠；
- 能否理解题干并选出或生成答案；
- 能否处理考试题中的阅读、约束、推理和干扰项；
- 是否覆盖中文、本土课程、K12、资格考试等标签。

中文、K12、考试来源、选择题形式应当保留为覆盖标签，而不是都升格为原子能力。

### 2. D04-D07 把学科难度、推理机制和模态混在一起

基础数学、高阶数学、多模态数学、科学视频都应保留在 benchmark 组合中，但原子层应区分：

- 多步数量/符号推理；
- 证明或过程可靠性；
- 视觉 grounding；
- 时序/视频事件 grounding。

数学、物理、科学实验、图表、几何图等更适合作为学科/材料标签。

### 3. D10-D13 里已有较接近原子能力的核心结构

作文评分、短答案评分、错误定位、纠错反馈、苏格拉底式引导、脚手架，本身已经比 D01-D07 更接近教育核心能力。

但仍需要拆清楚：

- 评分一致性和反馈生成不是同一个能力；
- 发现学生错在哪里和给出下一步提示不是同一个能力；
- 苏格拉底式提问、脚手架支持、教学指令遵循可能高度相关，但需要用 MathTutorBench/TutorBench/Bridge 等实际结果验证是否应合并。

### 4. D14 明显可再分

`教学法知识与教学设计` 至少应拆成：

- 教学法/特殊教育等专业知识判断；
- 面向目标、学情和约束的教学设计与材料组织。

`doc/atomic_principle.md` 已经明确指出这是不应直接作为一个原子能力的例子。

### 5. D15-D18 横跨 LLM 生成任务和 EDM/LAK 预测任务

学习规划、个性化、学情分析、知识追踪、认知诊断、资源推荐、学习路径都重要，但其中有两种评测范式：

- LLM 原生生成/建议任务：学习计划、个性化解释、资源推荐理由。
- 传统或序列建模任务：KT AUC、答题预测、概念掌握估计、推荐排序。

这两类不应被强行合成一个能力分数。应保留多个候选能力，并在结果层标注评测范式。

### 6. D19-D20 是课堂过程证据，但当前成熟度不足

课堂话语、教师行为、课堂视觉行为、参与度识别很关键，尤其面向真实教学场景。但当前多是资源/protocol，统一榜单少，且音频、视频、文本同步理解和教学建议生成还没有稳定的同构评测。

因此它们应作为重要候选能力，但需要标注“证据成熟度中低”。

### 7. D21 应保留，但要拆成角色边界和风险控制

EduGuard-Bench 已经把教师角色一致性、教学伤害、安全攻击成功率、拒答质量拆得比较清楚。教育安全不是一个单点能力，至少包含：

- 教师/tutor 角色边界；
- 未成年人风险识别和升级；
- 对抗诱导下的稳健拒答；
- 年龄、学生状态和情境适配。

### 8. D24 不应作为原子能力

教育垂类系统端到端能力是产品/系统层验证，不是原子能力。它应该用来验证若干原子能力组合后是否在真实工作流中有效，包括 task completion、teacher adoption、learning gain、delayed retention 等。

## 新的候选原子能力 A 码

下面的 A 码是“第一步候选”，不是已经由实验严格验证的最终结构。证据成熟度含义：

- 高：多个 benchmark 或当前实测能支撑，且指标比较明确。
- 中：benchmark/resource 充足，但存在 judge、协议、模态或数据接入限制。
- 低：重要但主要依赖 protocol、代理样本或未来内部数据。

| A 码 | 候选原子能力 | 核心判据 | 主要 benchmark 证据 | 旧 D 码来源 | 成熟度 |
| --- | --- | --- | --- | --- | --- |
| A01 | 学科知识与概念判别 | 能否在给定学科语境中识别事实、概念、定义、规则和关系 | MMLU-Pro/MMLU、C-EVAL、CMMLU、E-EVAL、GaokaoBench、OmniEduBench | D01、D02、D03 | 高 |
| A02 | 多步数量与符号推理 | 能否把文本题转为计算、方程、符号变换或多步推导，并得到可核验答案 | GSM8K、MATH、MATH-500、OlymMATH、OlympiadBench、Math23K、Ape210K | D04、D05 | 高 |
| A03 | 过程可靠性与证明/步骤一致性 | 不只最终答案对，步骤是否无跳步、无幻觉、可被评分规则或过程 judge 检查 | K12Vista、OlympiadBench、SAS-Bench、MathTutorBench、ME2 | D02、D05、D06、D11、D12 | 中 |
| A04 | 可执行产物构建 | 生成代码、交互程序或可运行教学演示时，功能是否通过测试 | HumanEval、MBPP、APPS、LiveCodeBench、InteractScience | D08、D23 | 高/中 |
| A05 | 图表、几何和视觉 grounding | 能否从图像、图表、几何图、手写或视觉关键点中提取与题目相关的证据 | MathVista、ChartQA、CMMU、K12Vista、ME2、EduVisBench/EduIllustrate | D06、D22 | 高/中 |
| A06 | 时序和多模态事件 grounding | 能否理解视频、实验过程、课堂事件及音视频文本对齐 | SciVideoBench、Video-MME、ARIC、TIMSS Video Study、LectureBank | D07、D20、D19 | 中/低 |
| A07 | 学生作答状态判定 | 能否判断学生答案、步骤或代码当前是否正确、完整、可接受 | MathTutorBench Solution Correctness、SAS-Bench、CS1QA、ASAP-SAS | D09、D11、D12 | 高/中 |
| A08 | 错误定位与错因诊断 | 能否指出第一处关键错误、相关代码行、错误类型或潜在 misconception | MathTutorBench Mistake Location/Correction、SAS-Bench ECS、Bridge、CS1QA、ME2 | D09、D11、D12、D17 | 高 |
| A09 | 可行动纠错反馈 | 能否给出针对学生当前错误的解释、提示和修改建议，而不是只给标准答案 | TutorBench、MathTutorBench、MathDial、Bridge、SAS-Bench、QACP | D09、D12、D13 | 高/中 |
| A10 | 脚手架与下一步教学决策 | 能否选择合适的下一步问题、提示强度和引导策略，控制不过早泄题 | TutorBench、MathTutorBench、MathDial、Bridge、ConvoLearn、SocraticLM、PEBBLE | D13、D12 | 高/中 |
| A11 | 教学法与特殊教育知识判断 | 能否回答教学法、课堂策略、特殊教育需求等教师专业知识问题 | Pedagogy Benchmark、EduEval、OmniEduBench | D14 | 高 |
| A12 | 教学设计与材料组织 | 能否围绕目标、学情、活动、评价和约束组织教案、练习、讲解材料 | EduBench、EduEval、OmniEduBench、Pedagogy Benchmark | D14、D15、D18 | 高/中 |
| A13 | 教学表征与可视化设计 | 能否把抽象知识转化为图示、板书、动画、交互或结构化视觉表达，并保持语义对齐 | EduIllustrate、EduVisBench、VisualEDU、ME2、InteractScience | D22、D23、D06 | 中 |
| A14 | Rubric 评分校准 | 能否按人工 rubric 或评分标准稳定给分，并与人工评分保持一致 | ASAP-AES、ASAP-SAS、EssayJudge、SAS-Bench | D10、D11 | 高/中 |
| A15 | 学习历史状态预测 | 能否根据学生历史作答/行为序列预测下一题表现或学习风险 | ASSISTments、EdNet、KDD Cup 2010、Junyi、STATICS2011 | D16 | 中/低 |
| A16 | 知识点掌握与概念映射 | 能否估计学生掌握的知识点、薄弱概念、题目-KC 标签或先修结构 | ASSISTments、FoundationalAssist、PTADisc、Junyi、数字教育应用算法智能诊断公共数据集 | D17 | 中/低 |
| A17 | 个性化适配、资源推荐与学习路径 | 能否依据学生画像、目标、历史和约束推荐资源、规划路径并解释选择 | EduBench、EduEval、MOOCCube、EdNet、SIGHT、TutorialBank、FineWeb-Edu | D15、D18 | 中/低 |
| A18 | 课堂话语、参与和行为理解 | 能否从课堂文本、对话、视频或多模态信号识别教学话语、学生参与和课堂事件 | TalkMoves、NCTE Transcripts、ConvoLearn、EduDial、IntrEx、SCB-Dataset、ARIC | D19、D20 | 中/低 |
| A19 | 教育安全、角色边界与风险处置 | 能否维持教师/tutor 角色，识别未成年人风险，抵抗对抗诱导，并给出合适拒答或转介 | EduGuard-Bench、YouthSafe/YAIR、CASTLE、EduBench/EduEval 安全子任务 | D21 | 高/中 |

## 第一阶段能力重要性排序

这里的“重要”不是说可以直接上线，而是说当前 benchmark 体系反复把它作为模型差异来源或教育产品底线。

### P0：教育 re-benchmark 的核心能力

这些能力直接支撑“会不会教、会不会评、是否安全”，应作为当前教育模型评价的主轴：

- A07 学生作答状态判定
- A08 错误定位与错因诊断
- A09 可行动纠错反馈
- A10 脚手架与下一步教学决策
- A11 教学法与特殊教育知识判断
- A12 教学设计与材料组织
- A14 Rubric 评分校准
- A19 教育安全、角色边界与风险处置

对应当前 P0/P1 实测与计划：SAS-Bench、ASAP-AES、Pedagogy Benchmark、EduBench、TutorBench、MathTutorBench、EduGuard-Bench。

### P1：差异化教育能力和多模态能力

这些能力能明显区分教育场景，但成本、judge 或数据接入更复杂：

- A03 过程可靠性与证明/步骤一致性
- A05 图表、几何和视觉 grounding
- A06 时序和多模态事件 grounding
- A13 教学表征与可视化设计
- A17 个性化适配、资源推荐与学习路径
- A18 课堂话语、参与和行为理解

对应 benchmark：MathVista、ME2、K12Vista、SciVideoBench、EduIllustrate/EduVisBench、InteractScience、MOOCCube、TalkMoves、ARIC。

### P2：底座和背景能力

这些能力是门槛项或背景项，很重要，但不应证明“会教学”：

- A01 学科知识与概念判别
- A02 多步数量与符号推理
- A04 可执行产物构建

对应 benchmark：MMLU-Pro、C-EVAL、AGIEval、OlympiadBench、MathVista、HumanEval/LiveCodeBench。它们适合筛掉基础能力不足的模型，或作为能力雷达图的底座轴，不适合替代教育核心能力。

### 专项 protocol：重要但不要强行并入 LLM 总榜

- A15 学习历史状态预测
- A16 知识点掌握与概念映射

它们在教育数据挖掘和学习分析中非常成熟，但与通用 LLM API 评测不是同构问题。应在 EDM/LAK 专项里评估，或作为产品系统的学习状态模块评价。

## 旧 D 码到新 A 码的对应关系

| 旧 D 码 | 建议处理 | 对应新 A 码 |
| --- | --- | --- |
| D01 通用学科知识与选择题答题 | 拆分；选择题为题型标签 | A01 |
| D02 中文本土知识与 K12 学科体系 | 拆分；中文/K12/本土为标签 | A01、A03、A05 |
| D03 标准化考试与资格考试推理 | 降级为考试来源/任务标签 | A01、A02、A03 |
| D04 基础数学应用题 | 保留为数学标签下的推理证据 | A02 |
| D05 高阶数学与竞赛推理 | 拆出多步推理和过程可靠性 | A02、A03 |
| D06 几何视觉、图表和多模态数学 | 拆出视觉 grounding 和过程解释 | A05、A03、A13 |
| D07 科学实验、视频和长时序理解 | 保留为时序/视频 grounding 候选 | A06 |
| D08 代码生成与算法题解 | 保留为可执行产物构建 | A04 |
| D09 编程教育问答与代码诊断 | 拆出代码/问题诊断和反馈 | A07、A08、A09 |
| D10 作文自动评分 | 题材标签，核心是 rubric 评分 | A14 |
| D11 短答案和分步评分 | 拆出评分校准、状态判定、错误归因 | A14、A07、A08 |
| D12 学生错误定位与纠错反馈 | 拆成诊断和反馈 | A07、A08、A09 |
| D13 苏格拉底式引导与脚手架 | 保留为教学策略/下一步决策 | A10 |
| D14 教学法知识与教学设计 | 必须拆分 | A11、A12 |
| D15 学习规划、个性化与学情分析 | 拆成个性化生成、KT、诊断 | A17、A15、A16 |
| D16 知识追踪与答题预测 | 保留为专项预测能力 | A15 |
| D17 认知诊断与知识点掌握 | 保留为知识点诊断能力 | A16 |
| D18 教育资源检索、推荐与学习路径 | 并入个性化路径/资源推荐 | A17 |
| D19 课堂话语和教师行为分析 | 并入课堂过程理解 | A18 |
| D20 课堂视觉行为与参与度识别 | 并入课堂过程理解或 A06 的多模态分支，待实验拆分 | A18、A06 |
| D21 教育安全、合规与角色扮演 | 保留但内部继续拆分指标 | A19 |
| D22 教学可视化生成 | 降为教学表征/可视化设计 | A13、A05 |
| D23 交互式科学演示生成 | 交互式输出是任务形式，核心为可执行产物和教学表征 | A04、A13 |
| D24 教育垂类系统端到端能力 | 不作为原子能力，移入验证层 | 组合验证层 |

## 建议的标签体系

这些字段应和 A 码同时记录，但不应再命名为原子能力：

| 标签类型 | 示例 |
| --- | --- |
| 学科 | 数学、物理、化学、生物、语文、英语、历史、编程 |
| 学段 | 小学、初中、高中、高教、职业教育、教师教育 |
| 语言/地域 | 中文、英文、双语、中国本土课程、国际考试 |
| 题型 | 选择题、填空、短答、作文、代码、开放生成、对话、多轮 |
| 模态 | 文本、图像、图表、几何图、手写、视频、音频、交互网页 |
| 难度 | 基础、常规、高阶、竞赛、hard subset |
| 评测器 | exact match、程序测试、rubric、人审、LLM judge、pairwise judge |
| 产品风险 | 低风险练习、高风险评分、未成年人安全、心理危机、教师审核 |

## 先不要做的事

- 不要把 A01-A19 直接平均成一个总分。
- 不要用 MMLU/GSM8K/AGIEval 高分证明模型具备教学能力。
- 不要把只有一个 benchmark 支撑的能力当作已验证原子能力。
- 不要把资源数据集直接当模型 leaderboard。
- 不要把 D24 这类端到端系统表现降维成单个原子能力。

## 第二阶段 TODO：用实验和具体题目验证新 A 码

### 1. 建立 item 级标注表

新增一个结构化文件，例如：

```text
data/atomic_ability_v2/item_labels.jsonl
```

每条记录至少包含：

- `item_id`
- `source_file`
- `benchmark_id`
- `old_dimension_id`
- `primary_atomic_ability`
- `secondary_atomic_abilities`
- `tags.subject`
- `tags.grade_band`
- `tags.language`
- `tags.modality`
- `tags.item_format`
- `tags.scoring_method`
- `label_confidence`
- `notes`

第一批应覆盖：

- `data/benchmark_v1_2026-05-18/items.jsonl`
- `data/re_benchmark_v1/pilot_items.jsonl`
- `reports/re_benchmark_v1/scored_items.jsonl`
- `reports/eval/*/*/summary.json` 能追溯到 item 的 benchmark 输出

### 2. 用已跑结果做“可辨识性”检查

目标：验证 A 码之间是否真的区分模型画像。

最小分析：

- 构造 `model x item` 或 `model x metric` 矩阵。
- 按 A 码聚合每个模型的表现。
- 检查 A 码之间的相关性。
- 如果两个 A 码在多个模型和多个 benchmark 上高度同涨同跌，考虑合并。
- 如果一个 A 码内部出现稳定分裂，考虑拆分。

优先验证的拆分：

- A11 教学法知识 vs A12 教学设计。
- A08 错误定位/错因诊断 vs A09 纠错反馈。
- A10 苏格拉底式提问 vs 脚手架胜率 vs 教学指令遵循。
- A05 视觉 grounding vs A13 教学可视化设计。
- A14 作文评分 vs 短答案/分步评分。
- A19 角色一致性 vs 对抗安全 vs 青少年风险转介。
- A15 知识追踪 vs A16 认知诊断。

### 3. 对具体题目做边界审查

每个候选 A 码抽 30-50 道题，人工检查：

- 这道题主要测的到底是什么？
- 是否混入了无关能力，例如语言阅读、格式遵循、背景知识、judge 偏好？
- 如果去掉图像、rubric、学生历史、教学指令，能力要求是否改变？
- 同一道题是否应有多个能力标签？主标签是什么？

输出建议：

```text
reports/atomic_ability_v2/item_audit_2026-xx-xx.md
```

### 4. 做最小干预实验

用少量题目验证能力是否可被定向干预：

- 给 A05 题目提供视觉关键点，看是否只提升视觉 grounding 相关任务。
- 给 A14 题目提供更明确 rubric，看是否提升评分一致性但不必然提升教学反馈。
- 给 A10 题目固定“不要直接给答案”的教学策略，看是否提升脚手架而不改变解题正确率。
- 给 A17 题目提供学生画像和历史，看是否提升个性化路径，而不只是生成更长建议。
- 给 A19 题目加入年龄/危机线索，看模型是否改变风险识别和转介策略。

### 5. 固定 judge 和人工校准流程

开放式任务不能只看单一 LLM judge。需要：

- 为 A09/A10/A12/A13/A14/A19 各保留 gold 或人工抽检集。
- 固定 judge 模型、judge prompt、BoN/投票规则。
- 记录 self-judge 风险。
- 输出 judge 与人工一致性。
- 对安全任务保留高风险样例人工复核。

### 6. 重生成覆盖矩阵，但只作为证据矩阵

第二阶段验证后再新增：

```text
doc/benchmark_atomic_ability_v2_matrix.md
```

新矩阵应以 A01-A19 为行，benchmark 为列，并额外列出：

- 主测/交叉/只作标签；
- 是否有公开模型结果；
- 是否已有本地实测；
- 是否需要 judge；
- 是否有 coverage_gap；
- 数据访问状态。

### 7. 更新能力雷达图聚合逻辑

`doc/edu_eval_progress_and_arena.md` 目前仍按旧 D01-D24 聚合。后续应改为：

- 底座：A01-A05
- 教学：A07-A13
- 评价：A14
- 学习建模与个性化：A15-A17
- 课堂过程：A18
- 安全：A19

聚合时只在同一 A 码内归一，不跨 A 码直接平均。最终仍输出能力画像，而不是单榜总分。

## 当前建议

短期内不要直接替换旧矩阵。建议把旧矩阵定位为“D 码覆盖矩阵”，把本文的 A 码作为下一版 item 标注和实验分析的候选原子能力。等第二阶段完成可辨识性、题目审查和 judge 校准后，再决定哪些 A 码合并、拆分或降级为标签。
