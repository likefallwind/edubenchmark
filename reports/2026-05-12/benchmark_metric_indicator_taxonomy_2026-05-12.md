# AI-Edu Benchmark 原子能力下的评测指标拆解

调研日期：2026-05-12  
结构化数据：[data/benchmark_metric_indicators_2026-05-12.json](./data/benchmark_metric_indicators_2026-05-12.json)  
维度数据：[data/benchmark_metric_dimensions_2026-05-12.json](./data/benchmark_metric_dimensions_2026-05-12.json)

## 读法

- 本文件补齐“24 个原子能力下面究竟用什么指标评测”的信息。
- “原始指标名”尽量保留 benchmark 官方或论文中的指标名称；“归一化指标”是为了后续把不同 benchmark 聚合到统一大 benchmark。
- 很多教育数据集没有统一 LLM leaderboard，因此对应指标写成“应如何测”，并标注需要自建或二次定义任务。

## 指标总表

| ID | 原子能力 | 归一化指标 | Benchmark 原始指标 / 子维度 | 评分方式 |
|---|---|---|---|---|
| D01 | 通用学科知识与选择题答题 | 总体正确率/平均分 | MMLU accuracy、CMMLU average、C-EVAL average、E-EVAL average | 选择题 exact match 后按题目或学科平均 |
| D01 | 通用学科知识与选择题答题 | 学科切片正确率 | STEM/Humanities/Social Science/Other、subject-level score、C-Eval Hard | 按学科、难度、hard subset 聚合准确率 |
| D01 | 通用学科知识与选择题答题 | prompt 方式敏感性 | zero-shot、five-shot、CoT、few-shot CoT | 同一题集比较不同提示设置下的准确率变化 |
| D02 | 中文本土知识与 K12 学科体系 | 中文 K12 学科正确率 | E-EVAL average、GaokaoBench objective overall、K12Vista direct overall | 按学段和学科切片统计正确率 |
| D02 | 中文本土知识与 K12 学科体系 | 中国本土知识正确率 | CMMLU China-specific、C-EVAL subject categories | 对中国历史、政治、法律、文化等题目计算正确率 |
| D02 | 中文本土知识与 K12 学科体系 | 过程正确性 | K12Vista Step-by-Step overall、process correctness、hallucination/logical contradiction tags | 检查步骤是否跳步、幻觉、逻辑矛盾或图文误解 |
| D03 | 标准化考试与资格考试推理 | 考试题正确率 | AGIEval zero-shot/few-shot accuracy、GaokaoBench objective score | 客观题 exact match 或多选匹配 |
| D03 | 标准化考试与资格考试推理 | 主观题评分 | GaokaoBench subjective overall、subjective subject score | 按标准答案和评分细则人工或模型辅助评分 |
| D03 | 标准化考试与资格考试推理 | 考试类型切片 | SAT、LSAT、Gaokao、Civil Service Exam、Law/Math/Reading subsets | 按考试来源或题型统计准确率 |
| D04 | 基础数学应用题 | 最终答案正确率 | GSM8K exact match、Math23K answer accuracy、Ape210K accuracy | 抽取最终数值/表达式，与标准答案 exact match 或数值等价 |
| D04 | 基础数学应用题 | 表达式/方程生成正确率 | equation accuracy、template accuracy、answer accuracy | 比较生成方程、模板或计算结果是否等价 |
| D04 | 基础数学应用题 | 推理链设置效果 | CoT accuracy、verifier reranking、self-consistency | 比较直接作答、CoT、多采样、verifier 的答案正确率 |
| D05 | 高阶数学与竞赛推理 | 最终答案正确率 | MATH accuracy、MATH-500 accuracy、OlymMATH accuracy、OlympiadBench accuracy | 抽取 boxed answer，进行 exact match、数值容差或符号等价判断 |
| D05 | 高阶数学与竞赛推理 | Hard 子集正确率 | OlymMATH-HARD、competition subset、Olympiad-level subset | 按高难子集单独统计准确率 |
| D05 | 高阶数学与竞赛推理 | 稳定性/多次采样收益 | Pass@k、Cons@k、self-consistency | 多次采样后统计至少一次答对或一致答案答对的比例 |
| D05 | 高阶数学与竞赛推理 | 证明/过程可评性 | theorem proving subset、process-level correctness | 证明题用人工、形式化 checker 或 LLM judge |
| D06 | 几何视觉、图表和多模态数学 | 多模态数学总体正确率 | MathVista test/testmini accuracy、CMMU fill-in/choice accuracy、K12Vista direct overall | 对图文题最终答案做 exact match、选项匹配或模型裁判 |
| D06 | 几何视觉、图表和多模态数学 | 视觉上下文切片 | MathVista visual context types、chart/table/geometry/figure QA | 按图表、几何图、函数图、科学论文图等视觉类型统计准确率 |
| D06 | 几何视觉、图表和多模态数学 | 数学推理类型切片 | algebraic、arithmetic、geometric、logical、numeric、scientific、statistical | 按推理类型统计准确率 |
| D06 | 几何视觉、图表和多模态数学 | 视觉关键点识别 | ME2 Visual Keypoint Identification accuracy | 判断模型是否识别辅助线、点、角、标记等视觉元素 |
| D06 | 几何视觉、图表和多模态数学 | 基于关键点的讲解质量 | ME2 correctness、fidelity、referencing score | 评价讲解是否正确、忠实于图像、明确引用视觉关键点 |
| D07 | 科学实验、视频和长时序理解 | 科学视频总体正确率 | SciVideoBench overall accuracy | 对科学视频多选题计算正确率 |
| D07 | 科学实验、视频和长时序理解 | 学科切片正确率 | Physics、Chemistry、Biology、Medicine | 按科学学科统计准确率 |
| D07 | 科学实验、视频和长时序理解 | 推理类型切片 | Conceptual、Hypothetical、Quantitative | 按概念理解、假设推理、定量计算统计准确率 |
| D07 | 科学实验、视频和长时序理解 | 视觉 grounding 依赖 | vision-blind baseline、with-video vs no-video accuracy | 比较有视频输入和无视频输入时的表现差距 |
| D08 | 代码生成与算法题解 | 功能正确率 | HumanEval pass@1、MBPP accuracy/pass@1、APPS test pass rate | 运行单元测试或隐藏测试，统计通过率 |
| D08 | 代码生成与算法题解 | 采样收益 | pass@k、pass@10、pass@100 | 多次采样中至少一个候选通过测试的概率估计 |
| D08 | 代码生成与算法题解 | 题目难度切片 | introductory、interview、competition、difficulty tags | 按难度或题源统计测试通过率 |
| D09 | 编程教育问答与代码诊断 | 学生问题类型识别 | CS1QA question type、intent/category classification | 分类学生问题属于概念、语法、运行错误、调试等类型 |
| D09 | 编程教育问答与代码诊断 | 相关代码行定位 | CS1QA related code line annotation、bug localization | 判断模型能否定位与问题相关的代码行或错误位置 |
| D09 | 编程教育问答与代码诊断 | 教学反馈质量 | hint usefulness、concept explanation quality、non-spoiler feedback | 评价提示是否可操作、解释概念且不过早泄露完整答案 |
| D10 | 作文自动评分 | 总分一致性 | QWK、holistic score agreement | 模型评分与人工评分之间计算 Quadratic Weighted Kappa |
| D10 | 作文自动评分 | 多维 trait 一致性 | vocabulary、sentence、argument clarity、coherence、syntax trait QWK | 按词汇、句法、篇章、论证等维度分别计算 QWK |
| D10 | 作文自动评分 | 跨 prompt 泛化和公平性 | cross-prompt QWK、length bias、group fairness slice | 跨题目、群体、文本长度切片比较评分一致性和偏差 |
| D11 | 短答案和分步评分 | 总体评分一致性 | QWK、overall score agreement | 模型总分与人工总分之间计算 QWK |
| D11 | 短答案和分步评分 | 分步评分一致性 | CCS: Comprehensive Consistency Score | 评估 overall score 与 step-wise scores 的一致性 |
| D11 | 短答案和分步评分 | 错误原因一致性 | ECS: Errors Consistency Score | 比较模型和人工标注的错误类型频率分布一致性 |
| D11 | 短答案和分步评分 | 局部分析指标 | F1 score、subject/question-type slice | 对特定错误类型、学科、题型计算 F1 或切片分数 |
| D12 | 学生错误定位与纠错反馈 | 错误位置定位 | MathTutorBench Mistake Location | 判断模型能否指出学生解答中的第一处错误或关键错误位置 |
| D12 | 学生错误定位与纠错反馈 | 纠错准确性 | MathTutorBench Mistake Correction | 判断模型能否给出正确纠正，而不是只给最终答案 |
| D12 | 学生错误定位与纠错反馈 | 学生答案正确性判断 | MathTutorBench Solution Correctness | 二分类判断学生答案或步骤是否正确 |
| D12 | 学生错误定位与纠错反馈 | 错因解释质量 | error cause、misconception diagnosis、expert tutor decision | 评价模型解释学生为什么错、下一步应如何引导 |
| D13 | 苏格拉底式引导与脚手架 | 苏格拉底式提问 | MathTutorBench Socratic Questioning | 评价回复是否通过问题引导学生思考，而非直接给答案 |
| D13 | 苏格拉底式引导与脚手架 | 脚手架胜率 | Scaffolding Win Rate、Scaffolding (Hard) | 成对比较模型回复在分层提示、逐步支持上的优劣 |
| D13 | 苏格拉底式引导与脚手架 | 教学指令遵循 | Pedagogy IF Win Rate、Pedagogy IF (Hard) | 评价模型是否遵循特定教学策略或教学法指令 |
| D13 | 苏格拉底式引导与脚手架 | 下一步教学决策 | expert tutor decision alignment、hint generation quality | 比较模型下一步提示/追问是否符合专家 tutor 决策 |
| D14 | 教学法知识与教学设计 | 教学法知识正确率 | CDPK、pedagogical knowledge score | 基于教师职业知识或教学法题目计算正确率 |
| D14 | 教学法知识与教学设计 | 特殊教育能力 | SEND | 评估特殊教育需求相关教学知识和策略 |
| D14 | 教学法知识与教学设计 | 教学设计质量 | lesson planning、instructional design、rubric-based education score | 按教学目标、活动设计、评价方式、适配性等 rubric 评分 |
| D15 | 学习规划、个性化与学情分析 | 学习规划质量 | learning planning、study plan rubric score | 评价目标拆解、时间安排、资源推荐和可执行性 |
| D15 | 学习规划、个性化与学情分析 | 个性化适配 | personalization、student profile alignment | 评价回复是否适配学生年级、基础、错误历史、兴趣和情绪 |
| D15 | 学习规划、个性化与学情分析 | 学情预测/推荐效果 | KT AUC、ACC、next response prediction、recommendation ranking | 预测学生下次答题正确性或推荐资源，用 AUC/ACC/NDCG 等评估 |
| D16 | 知识追踪与答题预测 | 下一题答对概率预测 | AUC、ACC、RMSE | 用历史作答序列预测下一次作答是否正确 |
| D16 | 知识追踪与答题预测 | 长序列建模能力 | sequence-level AUC、long interaction split | 在长学习日志上统计预测指标 |
| D16 | 知识追踪与答题预测 | 跨数据/跨知识点泛化 | cross-dataset split、concept split、student split | 按学生、题目、知识点或时间切分后比较 AUC/ACC |
| D17 | 认知诊断与知识点掌握 | 知识点掌握估计 | concept mastery、knowledge component mastery | 估计学生对知识概念的掌握概率或等级 |
| D17 | 认知诊断与知识点掌握 | 诊断解释质量 | diagnostic explanation、misconception explanation | 评价模型给出的薄弱知识点解释是否和作答证据一致 |
| D17 | 认知诊断与知识点掌握 | 概念标签预测/映射 | concept label prediction、KC tagging | 预测题目或学生错误对应的知识点标签 |
| D18 | 教育资源检索、推荐与学习路径 | 资源检索相关性 | Recall@k、MRR、NDCG、retrieval relevance | 根据查询或知识点检索课程、视频、教程，计算排序指标 |
| D18 | 教育资源检索、推荐与学习路径 | 学习路径连贯性 | prerequisite consistency、path coherence、concept graph alignment | 评价推荐序列是否符合先修关系和学习目标 |
| D18 | 教育资源检索、推荐与学习路径 | 教育语料质量 | educational quality score、filter score | 对网页/文本资源的教育密度、清晰度、可靠性评分 |
| D19 | 课堂话语和教师行为分析 | 课堂话语动作分类 | Talk Moves labels、instructional moves classification | 把教师话语标注为追问、复述、促推理、连接学生想法等类别 |
| D19 | 课堂话语和教师行为分析 | 课堂反馈建议质量 | teacher feedback usefulness、actionability、pedagogical alignment | 评价基于课堂片段给教师的建议是否可执行、对齐教学目标 |
| D19 | 课堂话语和教师行为分析 | 跨课堂泛化 | cross-teacher、cross-school、cross-country split | 按教师、学校、国家或课程切分后评估分类或建议质量 |
| D20 | 课堂视觉行为与参与度识别 | 学生行为识别 | behavior classification accuracy、action recognition | 识别听讲、举手、互动、走神等课堂行为 |
| D20 | 课堂视觉行为与参与度识别 | 参与度/兴趣度预测 | engagement score、interest level、participation label | 根据对话、视频或行为预测学生参与度 |
| D20 | 课堂视觉行为与参与度识别 | 多模态同步理解 | audio-video-text alignment、classroom event grounding | 联合图像、音频、文本定位课堂事件和参与变化 |
| D21 | 教育安全、合规与角色扮演 | 角色扮演专业度 | RFS、role-following score | 评价模型作为教师/tutor 是否遵循教育角色和专业边界 |
| D21 | 教育安全、合规与角色扮演 | 攻击成功率/安全失败率 | ASR | 统计对抗诱导下模型产生不安全或不专业回复的比例，越低越好 |
| D21 | 教育安全、合规与角色扮演 | 青少年风险识别与转介 | youth risk category、safeguard success、crisis escalation quality | 评估 grooming、自伤、边界侵犯、情感依赖等风险识别和升级建议 |
| D21 | 教育安全、合规与角色扮演 | 学生个体差异安全 | student-specific safety、empathy、developmental appropriateness | 按年龄、认知水平、心理状态评价回复是否安全适配 |
| D22 | 教学可视化生成 | 逻辑序列 | logic sequence | 评价可视化步骤是否符合解题或概念讲解顺序 |
| D22 | 教学可视化生成 | 结构丰富度 | structural richness | 评价图形、布局、层次、交互元素是否支持学习 |
| D22 | 教学可视化生成 | 语义对齐 | semantic alignment | 评价视觉元素是否准确表达题目和讲解内容 |
| D22 | 教学可视化生成 | 讲解引导 | explanation guidance | 评价可视化是否引导学生理解关键步骤，而非只做装饰 |
| D22 | 教学可视化生成 | 交互参与度 | interaction engagement | 评价互动控件、动态变化、探索路径是否有教育价值 |
| D23 | 交互式科学演示生成 | 程序功能测试通过率 | PFT Overall、PFT Average、PFT Perfect | 用 Playwright/unit tests 检查交互功能是否按题目要求工作 |
| D23 | 交互式科学演示生成 | 动作成功率 | VQT Action | 执行指定交互动作后，检查期望视觉状态是否出现 |
| D23 | 交互式科学演示生成 | 视觉相似度 | VQT CLIP | 比较生成快照和参考快照的 CLIP 相似度 |
| D23 | 交互式科学演示生成 | 语义正确性 | VQT VLM-judge | 用多模态模型判断视觉结果是否符合科学演示规格 |
| D24 | 教育垂类系统端到端能力 | 外部 benchmark 能力 | MathTutorBench scores、EduBench scores、TutorBench scores | 把系统或底座模型放到公开 benchmark 上复测 |
| D24 | 教育垂类系统端到端能力 | 工作流完成度 | task completion、workflow success、teacher adoption | 评估备课、讲题、批改、学情分析等产品工作流是否完整完成 |
| D24 | 教育垂类系统端到端能力 | 真实学习效果 | learning gain、delayed retention、transfer、A/B outcome | 通过前后测、延迟测、迁移题或平台 A/B 指标评估学生是否真正学会 |
| D24 | 教育垂类系统端到端能力 | 教师采纳与修改量 | teacher acceptance rate、edit distance、override rate | 统计教师是否采纳 AI 建议、修改多少、拒绝原因 |

## 关键发现

1. **答案正确率类指标最成熟，但最容易饱和。** MMLU、GSM8K、HumanEval、基础 K12 选择题都属于这一类，应作为门槛项。
2. **教育核心指标主要是过程指标。** Mistake Location、Scaffolding Win Rate、Pedagogy IF、CCS、ECS、process correctness、visual keypoint identification 比普通 accuracy 更能区分 tutor 能力。
3. **多模态教学指标正在变细。** MathVista 按推理类型和视觉上下文切片，ME2 进一步把“视觉关键点识别”和“基于关键点的讲解”拆开，InteractScience 直接测交互代码能不能运行和视觉结果对不对。
4. **知识追踪和认知诊断指标成熟但和 LLM 断层。** AUC/ACC/RMSE 是成熟指标，但它们评价预测，不评价解释、引导和反馈质量。
5. **长期学习效果仍缺公开指标。** learning gain、delayed retention、transfer、teacher adoption 目前更适合作为自建 benchmark 或真实产品实验指标。

## 指标来源补充

- MathTutorBench 官方榜单指标：Problem Solving、Socratic Questioning、Solution Correctness、Mistake Location、Mistake Correction、Scaffolding Win Rate、Pedagogy IF Win Rate、Scaffolding (Hard)、Pedagogy IF (Hard)。
- TutorBench 指标框架：Adaptive Explanation Generation、Assessment & Feedback、Active Learning Support，并用样本级 rubric criteria 计算 pass rate/overall。
- SAS-Bench 指标：QWK、CCS、ECS、F1 和学科/题型切片。
- MathVista 指标：overall accuracy、test/testmini、数学推理类型切片、视觉上下文切片、任务类型切片。
- SciVideoBench 指标：overall accuracy、学科切片 Physics/Chemistry/Biology/Medicine、推理类型 Conceptual/Hypothetical/Quantitative、vision-blind baseline。
- ME2 指标：Visual Keypoint Identification accuracy；Keypoint-based Explanation Generation 的 correctness、fidelity、referencing。
- InteractScience 指标：PFT Overall/Average/Perfect、VQT Action、VQT CLIP、VQT VLM-judge。
