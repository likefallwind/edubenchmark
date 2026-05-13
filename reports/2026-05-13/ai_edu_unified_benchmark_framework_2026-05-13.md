# AI-教育统一 Benchmark 尺度与评测框架

调研日期：2026-05-13  
目标文件：[todo.md](../../todo.md)  
基础材料：[edu_benchmark_survey.md](../../edu_benchmark_survey.md)、[edu_benchmark_survey_supplement_2026-05-11.md](../../edu_benchmark_survey_supplement_2026-05-11.md)、[benchmark_metric_indicator_taxonomy_2026-05-12.md](../2026-05-12/benchmark_metric_indicator_taxonomy_2026-05-12.md)、[ai_edu_benchmark_exhaustive_index_2026-05-13.md](./ai_edu_benchmark_exhaustive_index_2026-05-13.md)、[ai_edu_benchmark_catalog_2026-05-13.md](./ai_edu_benchmark_catalog_2026-05-13.md)

## 一、结论

AI-教育 benchmark 不应该做成“所有分数平均”的单榜。更合理的是一个 **统一尺度 + 场景映射 + benchmark 证据库**：

1. **统一尺度**：把任意 AI 教育应用拆到 8 个一级尺度、24 个原子能力、若干原生指标。
2. **场景映射**：先判断应用属于 tutor、批改、备课、知识追踪、课堂分析、资源推荐、安全陪伴等哪类，再选择主评测和补充评测。
3. **证据分层**：把 benchmark 分成门槛项、主排序项、补充诊断项、资源构造项，不跨 benchmark 直接平均。
4. **结果解释**：同一个模型在 MMLU/GSM8K 高分，只能证明基础知识和基础数学过关，不能证明它会教学；教育核心能力主要体现在错因诊断、脚手架、个性化、分步评分、多模态 grounding、安全和真实学习效果。

## 二、统一 benchmark 尺度

### 1. 一级尺度

| 一级尺度 | 评测问题 | 典型指标形态 | 主 benchmark / 数据 |
|---|---|---|---|
| S1 学科知识与解题正确性 | 模型会不会做题、知识是否可靠 | Accuracy、Exact Match、subject score、hard subset score | MMLU、CMMLU、C-EVAL、E-EVAL、GaokaoBench、GSM8K、MATH、OlymMATH、OlympiadBench |
| S2 复杂推理与过程正确性 | 不只答案对，过程是否可靠 | process correctness、step correctness、CoT consistency、proof/process judge | K12Vista、GaokaoBench 主观题、OlympiadBench、ME2、SAS-Bench |
| S3 教学诊断与辅导策略 | 能否识别学生错因并给出合适下一步 | Mistake Location、Mistake Correction、Socratic Questioning、Scaffolding Win Rate、Pedagogy IF | MathTutorBench、TutorBench、MathDial、Bridge、SocraticLM、PEBBLE |
| S4 反馈、批改与评价 | 能否按 rubric 给分、解释扣分、提供可行动反馈 | QWK、CCS、ECS、trait-level agreement、rubric pass rate | ASAP-AES、ASAP-SAS、EssayJudge、SAS-Bench、TutorBench |
| S5 个性化、学情与学习路径 | 是否理解学生状态并适配资源/路径 | KT AUC/ACC、concept mastery、NDCG/MRR、profile alignment | ASSISTments、EdNet、Junyi、FoundationalAssist、PTADisc、MOOCCube |
| S6 多模态教学理解与生成 | 能否处理图、表、视频、手写、可视化和交互 | visual/math accuracy、keypoint accuracy、PFT、VQT、semantic alignment | MathVista、K12Vista、CMMU、ME2、SciVideoBench、EduVisBench、InteractScience |
| S7 教育安全、伦理与角色边界 | 能否安全地扮演教师/tutor，处理未成年人风险 | RFS、ASR、refusal quality、risk classification、age appropriateness | EduGuard-Bench、YouthSafe/YAIR、SproutBench、CASTLE 类学生安全评测 |
| S8 真实教育效果与工作流价值 | 学生是否真的学会，教师是否真的采纳 | learning gain、delayed retention、transfer、teacher adoption、edit distance、workflow success | 公开 benchmark 很弱，需内部实验、平台日志或 A/B |

### 2. 24 个原子能力归属

| 一级尺度 | 原子能力 |
|---|---|
| S1 学科知识与解题正确性 | D01 通用学科知识、D02 中文 K12、D03 标准化考试、D04 基础数学、D05 高阶数学、D08 代码生成 |
| S2 复杂推理与过程正确性 | D02 过程正确性、D03 主观题、D05 证明/竞赛推理、D06 多模态数学过程、D07 科学视频推理 |
| S3 教学诊断与辅导策略 | D09 编程教育问答、D12 学生错误定位、D13 苏格拉底式引导、D14 教学法知识 |
| S4 反馈、批改与评价 | D10 作文评分、D11 短答案和分步评分、D12 纠错反馈 |
| S5 个性化、学情与学习路径 | D15 学习规划、D16 知识追踪、D17 认知诊断、D18 资源推荐 |
| S6 多模态教学理解与生成 | D06 多模态数学、D07 科学视频、D20 课堂视觉行为、D22 教学可视化、D23 交互科学演示 |
| S7 教育安全、伦理与角色边界 | D21 教育安全、D24 教育垂类系统边界与端到端风险 |
| S8 真实教育效果与工作流价值 | D15 学习规划、D18 学习路径、D19 课堂话语、D24 端到端系统能力 |

## 三、benchmark 证据分层

### 1. 门槛项

门槛项用于筛掉基础能力不足的模型，不适合做教育应用主排序。

| 能力 | Benchmark | 原因 |
|---|---|---|
| 通用知识 | MMLU、CMMLU、C-EVAL | 使用广、可比性强，但前沿模型已接近饱和 |
| 基础数学 | GSM8K、Math23K、Ape210K | 可检验基本数学链路，但不能代表 tutor 能力 |
| 入门代码 | HumanEval、MBPP | 适合筛基础编程能力，编程教育应转向学生代码诊断 |
| 基础多模态 | ChartQA、CMMU、MathVista testmini | 可测图表/图文理解，但不等于教学解释质量 |

### 2. 主排序项

主排序项更贴近 AI 教育核心价值，应该在综合评测中给更高权重。

| 教育能力 | 主 benchmark | 为什么重要 |
|---|---|---|
| 数学 tutor | MathTutorBench、TutorBench、MathDial、Bridge、OlymMATH | 区分“会做题”和“会教”，能看错因定位、脚手架、引导式提问 |
| 多模态作业反馈 | TutorBench、K12Vista、MathVista、ME2 | 真实作业常有图、表、步骤、手写和图文 grounding |
| 分步评分与批改解释 | SAS-Bench、EssayJudge、ASAP-AES、ASAP-SAS | 总分一致性不足以说明批改有效，必须看步骤和错因 |
| 教师助手与教学设计 | Pedagogy Benchmark、EduBench、EduEval、OmniEduBench | 覆盖教学法知识、备课、学习规划、教育任务生成 |
| 教育安全 | EduGuard-Bench、YouthSafe/YAIR、SproutBench | 未成年人场景必须单独测角色边界、风险识别和拒答质量 |
| 交互式教学内容 | EduVisBench、InteractScience、VisualEDU | 教育内容生成必须科学正确、可交互、可运行，而不是只看起来像 |

### 3. 补充诊断项

这些 benchmark/数据集不一定有统一 LLM 榜单，但很适合定位问题。

| 方向 | 数据 / benchmark | 用法 |
|---|---|---|
| 知识追踪 | ASSISTments、KDD Cup 2010、EdNet、Junyi、STATICS2011 | 测 AUC/ACC/RMSE，判断是否能预测学习状态 |
| 认知诊断 | PTADisc、FoundationalAssist、数字教育应用算法智能诊断公共数据集 | 测知识点掌握、概念标签、错因解释 |
| 课堂话语 | TalkMoves、NCTE Transcripts、TIMSS Video Study、SIGHT | 测教师话语动作、课堂反馈建议、跨教师泛化 |
| 课程资源 | MOOCCube、LectureBank、TutorialBank、FineWeb-Edu | 构造资源检索、推荐、课程理解任务 |
| 编程教育 | CS1QA、QACP、Codecademy、LeetCode Student Submissions | 测学生问题理解、代码错误定位、非泄题式提示 |

### 4. 资源构造项

FineWeb-Edu、Chinese FineWeb Edu、MOOCCube、LectureBank、ARIC、TIMSS Video Study、产品系统入口等，更多是训练语料、任务材料或产品对象，不应直接作为“模型好坏”的结论来源。使用时必须先定义任务、标注协议、切分方式、指标和污染检查。

## 四、统一评分建议

### 1. 不跨 benchmark 直接平均

不同 benchmark 的题型、prompt、shot 数、模型版本、评测器和分数尺度差异很大。统一总分应该先按“原子能力”归一，而不是把原始分数直接平均。

推荐流程：

1. 每个 benchmark 内部保留原始分数。
2. 同一原子能力内，把指标转成等级：强、合格、弱、缺失。
3. 对饱和 benchmark 降权，对高区分度 benchmark 升权。
4. 对有风险的自动评测附上人工复核或置信等级。
5. 最终输出“能力画像”，不是只输出一个总分。

### 2. 100 分制的默认权重

这个权重用于“通用 AI 教育应用”初筛，具体产品应按场景调整。

| 模块 | 权重 | 说明 |
|---|---:|---|
| 基础知识与正确性 | 15 | 门槛项，高于阈值后不再过度奖励 |
| 教学诊断与脚手架 | 20 | 教育应用的核心差异点 |
| 反馈与批改解释 | 15 | 作业、作文、短答案、代码反馈都需要 |
| 复杂推理与多模态 grounding | 15 | 数学、科学、图表、视频、手写场景关键 |
| 个性化与学情建模 | 10 | 学习路径、推荐、学情预测 |
| 教育安全与角色边界 | 15 | 未成年人、教师角色、心理风险必须单列 |
| 端到端工作流与真实效果 | 10 | 教师采纳、学生改正、学习增益，公开 benchmark 不足时用内部评测补 |

### 3. 阈值建议

| 层级 | 判断规则 |
|---|---|
| 不合格 | 基础知识/安全任一核心项明显失败；或答题正确但频繁泄题、越界、误导学生 |
| 可用原型 | 门槛项合格，但教学诊断、脚手架、个性化或多模态存在明显短板 |
| 可控上线 | 主任务 benchmark 合格，安全项合格，有人工复核/教师介入机制 |
| 强教育能力 | 不仅会做题，还能稳定诊断错因、分层提示、按学生状态调整、解释评分、处理多模态材料 |
| 真实有效 | 有延迟学习、迁移、留存、教师采纳或 A/B 证据支持 |

## 五、应用到任意 AI 教育产品的映射方法

### 1. 先问 6 个问题

| 问题 | 决定什么 |
|---|---|
| 面向谁？学生、教师、家长、学校管理者？ | 年龄、安全、工作流和输出口径 |
| 做什么任务？答题、辅导、批改、备课、推荐、课堂分析、心理支持？ | 选主 benchmark |
| 输入是什么？文本、图像、作业照片、视频、代码、学习日志、多轮对话？ | 选多模态/KT/对话类指标 |
| 输出是什么？答案、提示、反馈、分数、教案、资源路径、风险建议？ | 选 rubric 和自动指标 |
| 是否影响真实学生？ | 是否需要安全、人工复核、学习效果指标 |
| 是否可复现？ | 是否能使用公开 benchmark，还是必须自建内部集 |

### 2. 场景到 benchmark 的映射

| 应用场景 | 主评测 | 补充评测 | 必测指标 |
|---|---|---|---|
| 数学解题助手 | MATH、OlymMATH、OlympiadBench、MathVista | GSM8K、GaokaoBench、ME2 | 最终答案、hard subset、过程正确性、视觉关键点 |
| 数学 tutor | MathTutorBench、TutorBench、MathDial、Bridge | MATH、OlymMATH、K12Vista、PEBBLE | 错因定位、脚手架、苏格拉底式提问、不过早给答案 |
| 中文 K12 学科助手 | C-EVAL、CMMLU、E-EVAL、GaokaoBench | OmniEduBench、K12Vista、EduEval | 学科正确率、中文本土知识、主观题评分、过程正确性 |
| 作文/短答案批改 | ASAP-AES、ASAP-SAS、EssayJudge、SAS-Bench | GaokaoBench 主观题、EduBench | QWK、trait QWK、CCS、ECS、反馈可行动性 |
| 编程教育助手 | CS1QA、QACP、Codecademy、LeetCode Student Submissions | HumanEval、MBPP、APPS | 错误定位、代码行关联、概念解释、非泄题提示 |
| 教师备课/教案助手 | Pedagogy Benchmark、EduBench、EduEval、OmniEduBench | MOOCCube、LectureBank、TutorBench | 教学目标对齐、活动设计、评价设计、资源质量 |
| 个性化学习路径 | ASSISTments、EdNet、Junyi、FoundationalAssist、MOOCCube | EduBench、PTADisc | KT AUC/ACC、知识点掌握、推荐 NDCG、路径连贯性 |
| 多模态作业反馈 | TutorBench、K12Vista、MathVista、ME2 | CMMU、ChartQA、EssayJudge | 图文 grounding、步骤反馈、视觉关键点、rubric pass rate |
| 课堂分析助手 | TalkMoves、NCTE Transcripts、TIMSS Video Study、ARIC | SIGHT、LectureBank、EduBench | 话语动作分类、行为识别、教师建议可执行性 |
| 交互式教学内容生成 | InteractScience、EduVisBench、VisualEDU | MathVista、ME2 | 程序功能通过率、语义对齐、交互参与度、科学正确性 |
| 青少年安全/陪伴 | YouthSafe/YAIR、SproutBench、EduGuard-Bench | CASTLE、EduBench 心理健康类任务 | 风险识别、转介质量、年龄适配、拒答质量、边界感 |
| 教育垂类大模型系统 | 按具体功能拆分以上所有场景 | LearnLM/产品公开结果只作参考 | 端到端任务完成、教师采纳、学生改正率、安全事故率 |

## 六、已收集 benchmark 信息的覆盖判断

### 1. 覆盖较充分

- 通用学科与考试：MMLU、CMMLU、C-EVAL、E-EVAL、AGIEval、GaokaoBench。
- 数学与多模态数学：GSM8K、MATH、MATH-500、OlymMATH、OlympiadBench、MathVista、ME2、K12Vista。
- 教学/辅导：MathTutorBench、TutorBench、MathDial、Bridge、SocraticLM、Pedagogy Benchmark、EduBench、EduEval、OmniEduBench。
- 自动评分：ASAP-AES、ASAP-SAS、EssayJudge、SAS-Bench。
- 知识追踪/诊断：ASSISTments、KDD Cup 2010、EdNet、Junyi、FoundationalAssist、PTADisc。

### 2. 覆盖中等但需要继续收集

- 青少年安全和心理健康：YouthSafe/YAIR、SproutBench、CASTLE、EduGuard-Bench、通用心理健康 benchmark。
- 课堂多模态行为：ARIC、SCB-Dataset、TIMSS Video Study、IntrEx。
- 学生科研创新：可借鉴 PaperBench、ResearchBench、SciVideoBench、InteractScience，但缺少教育化科研训练 benchmark。
- 思政/价值内化：现有多为知识/伦理问答，缺少内化、迁移和延迟反思。

### 3. 最大空白

1. **长期学习效果**：公开 benchmark 很少测 learning gain、delayed retention、transfer。
2. **教师-学生-AI 三方协同**：缺少教师采纳、修改、拒绝 AI 建议的标准数据。
3. **学生真实错因演化**：多数 benchmark 是单轮回答，少有多轮诊断和后续改正。
4. **中文本地教育安全**：未成年人、家校关系、校规、心理危机、思政表达都需要本地化。
5. **产品级端到端评测**：大多数教育垂类系统公开页面没有可复现 benchmark 分数。

## 七、后续信息收集优先级

| 优先级 | 需要补的信息 | 为什么 |
|---:|---|---|
| 1 | 每个 benchmark 的题目类型、样本量、数据入口、license、是否有 leaderboard、是否有模型结果 | 这是统一 benchmark 目录的基础字段 |
| 1 | 每个指标的评分器类型：自动、人工、模型裁判、程序测试、pairwise、人机混合 | 直接决定结果可信度 |
| 1 | 每个 benchmark 的饱和度：是否还能区分前沿模型 | 决定权重 |
| 2 | 新兴安全 benchmark：YouthSafe/YAIR、SproutBench、CASTLE | 未成年人安全是教育应用上线门槛 |
| 2 | 多轮 tutor benchmark：PEBBLE、ConvoLearn、MathTutorBench 后续榜单 | 补齐“怎么教”而非“会不会做题” |
| 2 | 课堂和教师工作流数据 | 补齐教师助手和师生机协同 |
| 3 | 学习效果实证/A-B 数据 | 公开资料少，但这是最终教育价值 |

## 八、主要新增外部来源

- MathTutorBench ACL Anthology: https://aclanthology.org/2025.emnlp-main.11/
- MathTutorBench project/GitHub: https://eth-lre.github.io/mathtutorbench/ , https://github.com/eth-lre/mathtutorbench
- TutorBench Scale Labs page: https://labs.scale.com/papers/tutorbench
- PEBBLE OpenReview: https://openreview.net/forum?id=ffvNvoJVgE
- YouthSafe / YAIR: https://scale.stanford.edu/ai/repository/youthsafe-youth-centric-safety-benchmark-and-safeguard-model-large-language-models
- SproutBench: https://scale.stanford.edu/ai/repository/sproutbench-benchmark-safe-and-ethical-large-language-models-youth
- K12Vista: https://scale.stanford.edu/ai/repository/k12vista-exploring-boundaries-mllms-k-12-education
- EduGuardBench: https://scale.stanford.edu/ai/repository/eduguardbench-holistic-benchmark-evaluating-pedagogical-fidelity-and-adversarial
