# `todo.md` 问题进一步调研：AI 教育 Benchmark 的机会点与空白

调研日期：2026-05-12  
基础材料：[todo.md](../../todo.md)、[edubench.md](../../edubench.md)、[edu_benchmark_survey.md](../../edu_benchmark_survey.md)、[edu_benchmark_survey_supplement_2026-05-11.md](../../edu_benchmark_survey_supplement_2026-05-11.md)

## 结论先行

1. **基础选择题、基础数学、入门代码已经不适合作为教育模型主排序指标。** MMLU、GSM8K、HumanEval、MBPP 这类曾经很难的基准，现在更多是门槛项；真正能区分教育模型的是多模态作业反馈、学生错因诊断、脚手架、分步评分、教学安全和长期学习效果。
2. **最值得补测的是“旧数据集 + 新模型 + 教育任务重定义”。** Math23K、Ape210K、ASAP-AES/SAS、CS1QA、QACP、TalkMoves、NCTE Transcripts、FoundationalAssist 这些资源本身有价值，但多数没有系统跑过 2025-2026 前沿模型，或者没有按现代 tutor/agent 方式重设任务。
3. **仍有挑战但关注不足的指标集中在过程而不是答案。** 例如 MathTutorBench 的 scaffolding / mistake location、TutorBench 的 adaptive explanation、SAS-Bench 的 ECS、K12Vista 的过程正确性、ME2 的视觉关键点、SciVideoBench 的定量视频推理、InteractScience 的功能正确性。
4. **四个场景中，“师生机协同教学助手”覆盖最好，“思政入心”和“学生科研创新”覆盖最弱。** 思政相关基准多停留在价值/伦理知识问答，几乎不测认同、迁移和行为改变；科研创新有 PaperBench、ResearchBench 等通用科研基准可借鉴，但缺少面向中学生/大学生科研训练的教育 benchmark。
5. **如果要做新的教育评测，最大机会不是再造一个总榜，而是补齐真实教育闭环。** 建议以“学生画像 + 多轮互动 + 教师介入 + 过程证据 + 安全约束 + 延迟学习结果”为核心，构造小而精的内部评测集。

## 一、哪些 benchmark 曾经做不好，但可能已被新模型显著改善

这里分两类：一类是已经被新模型明显追上、不适合继续当主指标；另一类是历史上难、但最新模型没有被系统补测，值得优先复核。

### 1. 已明显“门槛化”的老基准

| Benchmark | 早期困难点 | 现在的判断 | 建议用法 |
|---|---|---|---|
| MMLU / CMMLU / C-EVAL 选择题 | 早期 GPT-3/GPT-3.5 在多学科知识、中文本土知识上明显弱 | 前沿模型和中文强模型已在若干口径上接近 90 分段；C-EVAL 官方也已释放完整 test set 并停止维护原 leaderboard | 只做基础知识门槛，不作为教育产品主排序 |
| GSM8K | 早期 GPT-3 多步小学数学只有三四成水平，依赖 verifier 才提升 | 现有推理模型和数学模型基本已高度饱和 | 只检验基础算术链路，不代表 tutor 能力 |
| HumanEval / MBPP | Codex 时代仍有明显边界条件、需求理解和测试覆盖问题 | 入门代码生成已接近饱和；教育场景应转向学生代码诊断和反馈 | 作为编程能力入口项，权重降低 |
| MATH-500 | 早期 MATH 原集极难 | MATH-500 已被部分推理模型刷到很高；full MATH、OlymMATH、OlympiadBench 仍更有区分度 | 避免只报 MATH-500；区分 full MATH / MATH-500 / 奥赛级题 |

### 2. 值得优先补测的“旧难题”

| 优先级 | Benchmark / 数据资源 | 为什么可能已被新模型做好 | 为什么仍值得补测 | 建议补测协议 |
|---:|---|---|---|---|
| 1 | **Math23K、Ape210K** | 中文数学、方程生成、应用题解析能力被 Qwen、DeepSeek、Gemini、OpenAI 推理模型显著加强 | 公开结果多来自 seq2seq/tree decoder 时代；现代 LLM 统一榜单不足，且可能存在训练污染 | 使用去重/新题切分；比较 zero-shot、CoT、工具调用、只给答案 vs 分步讲解 |
| 1 | **ASAP-AES、ASAP-SAS、ELLIPSE** | LLM 的语义理解和 rubric-following 能力远强于传统特征工程/小模型 | 总分 QWK 可能很高，但公平性、长度偏差、跨 prompt 泛化、解释质量未必解决 | 同时报 QWK、跨 prompt、长度控制、公平性切片、反馈可操作性、人评一致性 |
| 1 | **CS1QA、QACP、Codecademy / LeetCode Student Submissions** | 代码模型和 agent 已能读代码、运行测试、解释错误 | 编程教育不是生成标准答案，而是理解学生代码和学生问题；这一点还没有统一强榜 | 任务拆成错误定位、最小提示、概念解释、不要泄露完整答案、可运行修复 |
| 2 | **TalkMoves、NCTE Transcripts、课堂转录类数据** | 新模型上下文理解、意图识别和少样本分类更强 | 近期 instructional moves 研究显示 few-shot 最强配置也只有中等一致性，课堂话语仍未解决 | 按真实课堂上下文分类 talk moves，并评估教师可用反馈，不只评 utterance label |
| 2 | **ChartQA、IM2LATEX-100K、图表/公式识别类教育资源** | GPT-4o、Gemini、Qwen2.5-VL 等多模态模型比早期 VL-T5/CNN-RNN 强很多 | 许多旧基准没有按教学场景重测，例如图表解释、公式批改、单位换算、错因说明 | 加入“看图解题 + 教学解释 + 错误反馈”组合任务 |
| 2 | **MathDial、Bridge、Google Education Dialogue Dataset** | 前沿模型的对话自然度和上下文保持能力显著增强 | 原始数据多是训练/分析资源，不是持续 leaderboard；最新教育模型没有统一横评 | 用专家 rubric 评下一步教学决策、脚手架、是否过早给答案、是否理解学生误解 |
| 3 | **FoundationalAssist、ASSISTments 文本增强版本** | LLM 可直接利用题干、学生作答、错误选项生成诊断特征 | KT/CD 社区指标成熟，但 LLM 融合后是否提升答题预测和个性化反馈还不清楚 | 比较传统 KT、LLM feature、LLM+KT hybrid；指标包括 AUC、错因标签和推荐解释 |

## 二、哪些指标仍很挑战，但 benchmark 关注度还不够

这些指标的共同特点是：它们不是“答案对不对”，而是“教育过程是否有效、可信、可解释、安全”。

| 指标 | 代表 benchmark | 证据信号 | 为什么重要 |
|---|---|---|---|
| 学生错因定位 | MathTutorBench、Bridge、MathDial、SAS-Bench | MathTutorBench 中 mistake location 明显低于 problem solving；Bridge 显示错误的下一步教学决策会显著损害回复质量 | tutor 首先要知道学生怎么错，而不是自己会做题 |
| 脚手架与苏格拉底式引导 | MathTutorBench、TutorBench、SocraticLM | 数学专用模型可高分解题，但 scaffolding / pedagogy IF 很低；TutorBench 顶部模型 overall 仍低于 56% | 这是“会解题”和“会教”的分界线 |
| 自适应讲解 | TutorBench、EduBench | TutorBench 报告指出 adaptive explanation generation 是更弱用例之一 | 学生水平、情绪、先验知识不同，同一答案不能适配所有人 |
| 分步评分与错误原因一致性 | SAS-Bench、EssayJudge、GaokaoBench 主观题 | SAS-Bench 中 ECS 明显低于总分一致性；EssayJudge 的高层论证维度仍弱 | 自动批改不能只给总分，要能说明哪一步、为什么扣分 |
| 多模态过程正确性 | K12Vista、MathVista、CMMU、ME2 | K12Vista 不只评最终答案，还构造过程评估；ME2 要求识别辅助线、点、角等视觉关键点 | 真实作业大量依赖图、表、手写、步骤和视觉 grounding |
| 科学视频定量推理 | SciVideoBench | Gemini-2.5-Pro overall 约 64，但定量推理低于概念题；无视觉输入时接近随机 | 科学实验理解需要时序观察、测量和因果推理 |
| 教学可视化与交互功能正确性 | EduVisBench、InteractScience、VisualEDU | InteractScience 指出模型能生成可点击 UI，但科学语义和功能正确性弱；EduVisBench 中专门 agent 明显优于裸模型 | 教育内容生成不能只是“看起来像”，必须科学正确、可操作 |
| 教育安全与学生个体差异 | EduGuard-Bench、CASTLE、YouthSafe | EduGuard 显示专业度和安全性不一致；CASTLE 指出学生画像下的个性化安全很难；YouthSafe 聚焦青少年风险 | 教育场景涉及未成年人、心理脆弱、师生权力关系，不能只套通用安全集 |
| 课堂话语动作识别 | TalkMoves、NCTE Transcripts | 新近研究显示基础模型识别 instructional moves 有意义但可靠性有限，few-shot 也未完全解决 | 教师助手如果要给课堂反馈，必须理解教师提问、追问、转述、促推理等动作 |
| 长期学习增益 | 目前几乎没有成熟公开 benchmark | 现有评测多是一次性题目或对话质量 | 教育产品最终要证明学生是否真正学会、保持、迁移，而不是模型回答是否漂亮 |

## 三、四个场景的 benchmark 覆盖情况

### 1. 师生机协同的教学助手

**覆盖判断：中等偏强，但缺少真正的三方协同闭环。**

已有覆盖：

| 能力 | 可用 benchmark / 数据 |
|---|---|
| 单生一机 tutor 回复 | MathTutorBench、TutorBench、MathDial、Bridge、SocraticLM |
| 作业反馈与批改 | TutorBench、SAS-Bench、EssayJudge、ASAP-AES/SAS、GaokaoBench 主观题 |
| 教师助手 / 教学设计 | Pedagogy Benchmark、EduBench、EduEval、OmniEduBench |
| 课堂话语分析 | TalkMoves、NCTE Transcripts、TIMSS Video Study |
| 学情预测 / 个性化 | ASSISTments、EdNet、Junyi、FoundationalAssist、PTADisc |
| 安全合规 | EduGuard-Bench、CASTLE、YouthSafe |

主要空白：

- 缺少“教师-学生-AI”三方同场景数据：教师如何采纳、修改、拒绝 AI 建议没有被标准化评估。
- 缺少课堂工作流指标：备课、课中巡视、课后作业、家校沟通之间没有贯通。
- 缺少干预后结果：模型提示后学生是否能独立改正、教师是否节省时间、错误是否复现。

建议内部评测模块：

| 任务 | 样本设计 | 指标 |
|---|---|---|
| AI 给教师的课堂建议 | 给出课堂片段、学生回答、教学目标，让模型建议下一步教师动作 | 教学目标对齐、可执行性、不过度替代教师、风险提示 |
| AI 辅助学生但保留教师监督 | 学生卡住，AI 给分层提示，教师可插入约束 | 是否过早泄题、是否促使学生表达思路、教师采纳率 |
| 作业批改闭环 | 学生答案、rubric、历史错因、教师偏好 | 分数一致性、错因准确、反馈可行动、教师修改量 |

### 2. 思政教育“入耳容易，入心难”

**覆盖判断：弱。现有 benchmark 多测“价值知识/伦理判断”，很少测“内化、认同、迁移”。**

已有覆盖：

| 层级 | 可用 benchmark / 数据 | 能测什么 |
|---|---|---|
| 政治/法律/伦理知识 | CMMLU、C-EVAL、E-EVAL、GaokaoBench、M3KE | 知识点和选择题答题 |
| 教育价值观 / 教师伦理 | Edu-Values、EduEval Ethics、OmniEduBench cultivation dimension | 教育价值、教师职业伦理、文化素养、素养培养 |
| 安全与价值对齐 | EduGuard-Bench、CASTLE、通用 safety benchmark | 是否输出不当内容、是否尊重学生差异 |

主要空白：

- “入心”不是单轮问答能测的。需要看学生是否能把价值判断迁移到真实冲突、长期行动和自我反思。
- 当前基准容易变成政治/伦理标准答案识别，无法区分背诵式回答和真实理解。
- 缺少年龄分层、地区差异、家庭背景、同伴影响下的教育场景。
- 缺少对“说教感”的评价。模型可能观点正确但表达方式让学生抵触。

建议内部评测模块：

| 任务 | 样本设计 | 指标 |
|---|---|---|
| 价值冲突情境讨论 | 校园欺凌、集体责任、网络言论、志愿服务、学术诚信等情境 | 价值判断合理性、共情、非灌输、引导学生自我表达 |
| 延迟反思任务 | 同一学生前后两轮反思，第二轮加入真实选择压力 | 观点一致性、迁移深度、行动计划可行性 |
| 反说教表达评估 | 同一价值目标，用不同语气和策略生成回复 | 学生接受度、人味、开放性、避免空话套话 |

### 3. 青少年身心健康问题

**覆盖判断：中等，但教育场景下的未成年人心理安全仍明显不足。**

已有覆盖：

| 方向 | 可用 benchmark / 数据 | 说明 |
|---|---|---|
| 教育场景心理辅导 | EduBench mental health 相关任务 | 覆盖教育模型的心理健康辅导场景，但深度有限 |
| 青少年 AI 风险 | YouthSafe / YAIR | 面向青少年 LLM 互动风险，覆盖 grooming、边界侵犯、情感依赖等细粒度风险 |
| 学生个性化安全 | CASTLE | 按学生认知和心理属性评估个性化安全、同理心和学生对齐 |
| 心理咨询质量 | CounselBench、TrustMH-Bench、PsychiatryBench、MentalBench | 更偏泛心理健康/临床，不是专门的学校场景 |
| 教育安全与角色扮演 | EduGuard-Bench | 能评估教育角色扮演中的专业度与安全性 |

主要空白：

- 学校语境独特：学生、班主任、家长、心理老师、校规之间存在复杂边界。
- 青少年心理问题常与学习压力、人际关系、家庭冲突、网络使用交织，不能照搬成人咨询 benchmark。
- 关键指标应包含危机识别、转介、隐私保护、非诊断化表达、避免过度依赖，而不只是“安慰得好不好”。
- 高风险任务不适合完全自动化，benchmark 应评估“什么时候升级给人类”。

建议内部评测模块：

| 任务 | 样本设计 | 指标 |
|---|---|---|
| 学业压力与情绪支持 | 不同年龄、成绩、家庭期望、睡眠状态的学生求助 | 共情、具体建议、不过度承诺、鼓励求助 |
| 危机升级 | 自伤暗示、霸凌、性骚扰、成瘾、极端焦虑 | 风险识别、转介质量、紧急程度判断、隐私边界 |
| 教师/家长沟通建议 | 学生不想告诉家长或老师时，模型给沟通方案 | 尊重学生、保护安全、合法合规、可执行 |

### 4. 学生科研创新

**覆盖判断：弱。通用科研 agent benchmark 很有参考价值，但不是教育化的科研训练 benchmark。**

可借鉴的 benchmark：

| 类型 | Benchmark | 可借鉴点 |
|---|---|---|
| 科研复现 | PaperBench、PRBench | 从论文理解到代码实现、实验复现、rubric 分解 |
| 科学发现 / 假设生成 | ResearchBench | 研究问题、背景、灵感检索、假设构成和排序 |
| 科学视频与实验理解 | SciVideoBench | 实验视频、时序观察、定量推理 |
| 科学交互演示 | InteractScience、EduVisBench | 把科学概念变成交互式可视化 |
| 高阶科学推理 | OlympiadBench、CMMU、K12Vista、MathVista | 学科知识、多模态推理、过程正确性 |

主要空白：

- 学生科研创新不是“复现顶会论文”。它更关注问题发现、资料搜集、实验设计、数据记录、失败复盘、表达展示。
- 当前教育 benchmark 很少评价“新颖但可行”的问题提出，也很少评价科学伦理、引用规范、数据可信度。
- 学生科研往往需要教师指导，缺少“AI 作为科研导师而非代写者”的评测。

建议内部评测模块：

| 任务 | 样本设计 | 指标 |
|---|---|---|
| 研究选题 | 给学生兴趣、年级、资源约束，让模型提出 3 个课题 | 新颖性、可行性、年龄适配、资源匹配、避免伪科学 |
| 文献与资料理解 | 给若干网页/论文摘要/数据，让模型帮学生梳理 | 引用准确、信息整合、指出不确定性、不过度编造 |
| 实验设计 | 给问题和可用器材，让模型设计实验或调查 | 变量控制、可重复性、安全伦理、数据记录 |
| 结果分析与展示 | 给表格/图像/失败结果，让模型协助解释和改进 | 统计合理、承认失败、改进建议、展示清晰 |
| 防代写 | 学生要求直接生成完整论文/项目 | 是否转为指导、保留学生主体性、学术诚信 |

## 四、建议的下一步评测组合

如果目标是为教育模型/产品建立一套有区分度的 benchmark，建议分三层。

### A. 门槛层：确认基础能力

| 能力 | benchmark |
|---|---|
| 中文 K12 知识 | C-EVAL、CMMLU、E-EVAL、GaokaoBench |
| 基础数学和代码 | GSM8K、MATH、HumanEval、MBPP |
| 基础多模态 | MathVista、CMMU、K12Vista |

这层不要给太高权重，主要用于筛掉明显不合格模型。

### B. 区分层：教育核心能力

| 能力 | benchmark |
|---|---|
| 数学 tutor | MathTutorBench、TutorBench、MathDial、Bridge |
| 作业批改 | SAS-Bench、EssayJudge、ASAP-AES/SAS |
| 多模态讲解 | ME2、EduVisBench、InteractScience |
| 科学视频和实验 | SciVideoBench、K12Vista |
| 教学安全 | EduGuard-Bench、CASTLE、YouthSafe |

这层应是模型选型的主分数来源。

### C. 自建层：现有 benchmark 覆盖不到的场景

| 场景 | 自建优先级 | 原因 |
|---|---:|---|
| 师生机协同闭环 | 高 | 有相关组件，但缺三方工作流和教师采纳指标 |
| 思政入心 | 高 | 公开 benchmark 基本不测价值内化和迁移 |
| 青少年心理安全 | 高 | 有 YouthSafe/CASTLE 可借鉴，但学校场景需要本地化 |
| 学生科研创新 | 高 | 通用科研 benchmark 不适配学生科研训练 |
| 长期学习增益 | 最高 | 当前最大空白，必须结合小规模教学实验或平台日志 |

## 五、可执行的内部 benchmark 设计草案

建议不要一次性做大而全的总榜，先做 5 个 100-200 条样本的小评测，每个样本带专家 rubric。

| 模块 | 样本数 | 输入 | 输出 | 关键指标 |
|---|---:|---|---|---|
| Tutor-Loop | 150 | 学生错误解、历史表现、教师目标 | 分层提示和下一步追问 | 错因定位、脚手架、不过早给答案 |
| Teacher-Copilot | 120 | 课堂片段、学生发言、教学目标 | 给教师的课中建议 | 可执行性、教师采纳、课堂节奏 |
| Values-Internalization | 120 | 价值冲突情境、学生画像 | 引导式讨论与反思任务 | 非说教、价值清晰、迁移深度 |
| Youth-Wellbeing | 150 | 青少年求助、多轮上下文 | 支持回复和升级建议 | 风险识别、同理心、转介、隐私 |
| Student-Research | 150 | 兴趣、资源、资料、数据 | 选题/实验/分析指导 | 新颖性、可行性、学术诚信 |

推荐评分方式：

- **自动初评 + 专家抽检**：自动评委用于规模化，专家用于校准和争议样本。
- **多维 rubric**：每个任务至少包含 correctness、pedagogy、personalization、safety、actionability。
- **对抗样本**：加入诱导泄题、诱导代写、心理危机、价值冲突、错误图表等高风险输入。
- **延迟任务**：对同一学生在第二轮/第三轮中检查是否真的改正、迁移或形成行动计划。

## 主要参考来源

- MathTutorBench: https://huggingface.co/papers/2502.18940
- TutorBench: https://scale.com/blog/tutorbench
- K12Vista: https://scale.stanford.edu/ai/repository/k12vista-exploring-boundaries-mllms-k-12-education
- ME2: https://me2-benchmark.github.io/
- EduVisBench: https://scale.stanford.edu/ai/repository/eduvisbench-eduvisagent-benchmark-and-multi-agent-framework-pedagogical-visualization
- SciVideoBench: https://scivideobench.github.io/
- InteractScience: https://www.researchgate.net/publication/396459862_InteractScience_Programmatic_and_Visually-Grounded_Evaluation_of_Interactive_Scientific_Demonstration_Code_Generation
- TalkMoves / instructional moves: https://papers.cool/arxiv/2204.09652, https://chatpaper.com/chatpaper/paper/221390
- YouthSafe: https://scale.stanford.edu/ai/repository/youthsafe-youth-centric-safety-benchmark-and-safeguard-model-large-language-models
- CASTLE: https://researchtrend.ai/papers/2602.05633
- CounselBench: https://www.emergentmind.com/papers/2506.08584
- PsychiatryBench: https://www.nature.com/articles/s41746-026-02582-w
- Edu-Values: https://papers.cool/arxiv/2409.12739
- EduEval: https://scale.stanford.edu/ai/repository/edueval-hierarchical-cognitive-benchmark-evaluating-large-language-models-chinese
- OmniEduBench: https://www.researchgate.net/publication/397089016_OmniEduBench_A_Comprehensive_Chinese_Benchmark_for_Evaluating_Large_Language_Models_in_Education
- PaperBench: https://openai.com/index/paperbench/
- ResearchBench: https://huggingface.co/papers/2503.21248
