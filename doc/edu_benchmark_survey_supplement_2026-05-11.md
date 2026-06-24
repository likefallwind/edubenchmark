# 教育 Benchmark 补充调研、权威性排序与原子能力覆盖分析

调研日期：2026-05-11  
原始报告：[edu_benchmark_survey.md](./edu_benchmark_survey.md)  
输入清单：[edubench.md](./edubench.md)  

## 口径说明

- 本文件是补充文件，不覆盖原报告。原报告中的论文结果、模型明细和“无统一榜单”判断仍作为基础事实使用。
- 本轮新增核验的线上来源优先使用 benchmark 官方仓库/项目页、模型官方报告或主流评测框架文档。第三方聚合榜单只用于判断“是否有社区热度/使用痕迹”，不作为权威最新分数的主证据。
- “权威性评分”是分析性评分，不是外部官方排名。评分综合：学术/任务设计质量 30、使用量与复现生态 25、教育场景贴合度 20、榜单维护与可比性 15、数据开放与泄漏控制 10。
- “使用量”用可见代理信号估计，包括 GitHub stars/forks、是否进入 OpenCompass/lm-eval 等评测框架、是否有官方/社区 leaderboard、是否被后续论文和模型卡频繁引用。无法统一抓取下载量的条目用“高/中/低”标注。
- 不同 benchmark 的分数、prompt、shot 数、模型版本和是否使用工具差异很大，本文件不跨 benchmark 直接做模型能力绝对比较。

## 一、旧模型结果的线上补充

### 1. 总体判断

老 benchmark 的更新结果大体分成三类：

| 类型 | 代表 benchmark | 更新后的结论 |
|---|---|---|
| 已明显饱和 | MMLU、GSM8K、HumanEval、MBPP | 前沿模型已接近或超过 90%，适合作为入门门槛，不适合作为教育能力排序主指标。 |
| 仍有区分度 | MATH、MATH-500、OlymMATH、OlympiadBench、MathVista、K12Vista、SciVideoBench、TutorBench、SAS-Bench | 高阶推理、多模态题、真实辅导与细粒度评分仍能拉开模型差距。 |
| 不应直接当 LLM 榜单 | Math23K、Ape210K、ASSISTments、EdNet、MOOCCube、FineWeb-Edu、课堂视频/转录资源、产品系统 | 更适合训练、任务构造或教育数据分析，需要另设任务协议后再比较模型。 |

### 2. 可补充进原报告的代表性新结果

| Benchmark | 原报告里的偏旧点 | 本轮可补充的较新结果 | 解释 |
|---|---|---|---|
| MMLU | 原论文只到 GPT-3 系列；原报告主表仍以原论文为主。 | OpenAI GPT-4.1 报告中：GPT-4.1 为 90.2，GPT-4.1 mini 87.5，GPT-4o(2024-11-20) 85.7，o1(high) 91.8，o3-mini(high) 86.9，GPT-4.5 90.8。OpenAI open models 页还给出 gpt-oss-120b 90.0、gpt-oss-20b 85.3、o3 93.4、o4-mini 93.0。Meta Llama 3.1 405B-Instruct：MMLU 87.3，MMLU(CoT) 88.6。DeepSeek-R1 报告：MMLU 90.8；Qwen3-235B-A22B-Base：MMLU 87.81。 | MMLU 已经从“GPT-3 距专家很远”变成“前沿模型 90 左右、明显饱和”。教育选型时应转向 MMLU-Pro、GPQA、学科专项和教学任务。 |
| CMMLU | 原论文模型较旧，但原报告已摘到官方 README 更新榜。 | 官方 README 的开放模型榜显示：five-shot Lingzhi-72B-chat 90.26、Telechat2-35B 90.16、Spark 4.0 90.07、Qwen2-72B 89.65；zero-shot Spark 4.0 90.97、Telechat2-35B 90.49、Lingzhi-72B-chat 90.07。 | 中文通识题上，中文模型/中文优化模型已显著高于原论文 GPT-4 70.95；CMMLU 对中文文化和本土知识仍有价值。 |
| C-EVAL | 原始榜单只含 GPT-4、ChatGPT、Claude-v1.3 等。 | 官方 GitHub/官网说明：2025-07-27 已释放完整 test set，并停止维护原 leaderboard。DeepSeek-R1 模型报告自报 C-Eval 91.8。 | 现在 C-EVAL 更适合“自测/复现实验”，不再适合作为官方持续榜单。引用最新模型时必须标明是模型卡/自评还是第三方复现。 |
| AGIEval | 原论文和官方 v1.1 榜主要是 GPT-4/GPT-4o、ChatGPT、Llama 3。 | Meta Llama 3.1 405B 基座模型卡报告 AGIEval English 71.6；原报告已有 AGIEval-en few-shot GPT-4o 71.4、Llama 3 400B+ 69.9。 | AGIEval 仍可反映“标准化考试/资格考试”能力，但已不够覆盖真实教育对话与学习反馈。 |
| GaokaoBench | 原结果集中在 GPT-4-0314/0613、Gemini-Pro、ERNIE、GPT-3.5。 | OpenCompass 常见 benchmark 文档给出 GaokaoBench weighted average：GPT-4-0409 76.0、GPT-4-1106 74.8、Claude-3-Opus 74.2、Llama-3-70B-Instruct 67.8、Mixtral-8x22B 60.0。官方仓库另列 GAOKAO-Bench-Updates，用 2023 年及之后高考选择题补充原集。 | 主观题与理科仍比客观选择题更有区分度；若用于中文教育选型，建议结合更新题和人工评分。 |
| GSM8K | 原报告只列 GPT-3 33-55%。 | Meta Llama 3.1 405B-Instruct：GSM-8K 96.8；Qwen3-235B-A22B-Base：GSM8K 94.39；OpenCompass 文档中 Llama-3-70B-Instruct 90.2、Claude-3-Opus 87.7、Mixtral-8x22B 88.3。 | GSM8K 已高度饱和，只能说明基础多步算术能力达标。 |
| MATH | 原论文 GPT-3 175B few-shot 5.2。 | Llama 3.1 405B-Instruct：MATH(CoT) 73.8；Qwen3-235B-A22B-Base：MATH 71.84；DeepSeek-R1：MATH-500 97.3。 | full MATH 与 MATH-500 不是同一口径。总体趋势是高阶数学显著提升，但奥赛级、证明式、几何多模态仍难。 |
| HumanEval / MBPP | 原报告以 Codex 和早期 Google MBPP 模型为主。 | Llama 3.1 405B-Instruct：HumanEval 89.0、MBPP 88.6；OpenCompass 文档中 GPT-4-0409 HumanEval 82.3、MBPP 77.0；Qwen3-235B-A22B-Base：EvalPlus 77.60、MBPP 81.40。 | HumanEval/MBPP 作为代码入门题已趋饱和。编程教育更应看 CS1QA、QACP、学生代码诊断、隐藏测试和教学反馈。 |
| MathVista | 原报告已有 testmini 上 o1、Claude 3.5 Sonnet、GPT-4o 等结果。 | 官方项目页私有 test leaderboard 显示：InternVL2-Pro ALL 65.84、InternVL2-8B-MPO 65.65、InternVL-Chat-V1.2-Plus 60.18；testmini 与 test 口径不同。 | 多模态数学比纯文本数学更有区分度。testmini 适合开发，私有 test 更适合严肃比较。 |
| OlympiadBench | 原报告已包含 GPT-4o 补充。 | 官方仓库当前 full benchmark：GPT-4o 25.89、GPT-4V 17.97、Qwen-VL-Max 10.09；text-only：GPT-4o 39.72、GPT-4 29.93、Llama-3-70B-Instruct 20.27。 | 奥赛级双语多模态科学题仍远未饱和，尤其物理和图像题。 |
| OlymMATH | 新 benchmark，原报告已有 DeepSeek-R1、o3-mini、Gemini 2.5 Pro、Qwen3。 | 原报告中 Gemini 2.5 Pro 在英文 HARD 58.4、中文 HARD 55.4；o3-mini 约 31-33；DeepSeek-R1 约 16-20。 | 对现有数学 benchmark 饱和有修正作用。Hard 子集应优先纳入后续模型选型。 |
| Pedagogy Benchmark | 原报告已有 97 模型榜。 | 该榜已经覆盖 Gemini 2.5 Pro、o3、Claude 4、DeepSeek-R1 May 2025、GPT-4.5、Qwen3 等。CDPK/SEND 顶部在 85-89。 | 教育学知识类题表现已较高，但它是考试型教学法知识，不等于真实 tutor 对话质量。 |
| TutorBench | 原报告已有 GPT-5、Gemini 2.5 Pro、o3、Claude 4 等。 | 最高 Gemini 2.5 Pro overall 55.65、GPT-5 55.33、o3 Pro 54.62，GPT-4o 36.12。 | 真实辅导与多模态作业反馈仍很难，是比 GSM8K/MMLU 更有教育区分度的 benchmark。 |
| SAS-Bench | 原报告已覆盖 DeepSeek-R1/V3、Qwen3、GPT-4o-mini 等。 | 当前最值得保留的指标不是单一 QWK，而是 CCS/ECS：DeepSeek-R1 CCS 73.76、ECS 55.90；DeepSeek-V3 CCS 74.11、ECS 54.00。 | 总分一致性会高估模型，分步评分和错误原因一致性更能体现教育评分能力。 |

## 二、各维度 benchmark 权威性评分与排序

### 评分解释

| 分数段 | 含义 |
|---|---|
| 90-100 | 全球或领域内事实标准，使用量高、复现生态强，但可能已有饱和风险。 |
| 80-89 | 强推荐 benchmark，学术质量和使用量较高，适合纳入主评测集。 |
| 70-79 | 有明确场景价值，但可能缺少持续 leaderboard、规模偏小或口径不统一。 |
| 60-69 | 可作补充或任务构造资源，单独作为权威结论较弱。 |
| 60 以下 | 更像数据资源/产品入口/研究材料，不建议直接当 benchmark 排名依据。 |

### 1. 解题能力：通用学科与考试

| 排名 | Benchmark | 权威性 | 使用量/复现生态 | 主要理由 |
|---:|---|---:|---|---|
| 1 | MMLU | 92 | 极高 | 全球通用事实标准，几乎所有模型卡会报；缺点是前沿模型已饱和。 |
| 2 | C-EVAL | 88 | 高 | 中文多学科代表性强，GitHub 约 1.8k stars；但官方 leaderboard 已停止维护。 |
| 3 | CMMLU | 85 | 高 | 中文本土知识覆盖好，GitHub 约 814 stars，有官方 README 榜；数据污染和榜单维护需持续关注。 |
| 4 | AGIEval | 83 | 高 | 真实考试来源，GitHub 约 772 stars，适合人类考试型推理；教育对话覆盖弱。 |
| 5 | GaokaoBench | 79 | 中高 | 中文高考语境权威，GitHub 约 747 stars；主观题人工评分成本高，近年题需持续更新。 |
| 6 | E-EVAL | 78 | 中 | 中文 K12 学段贴合度高；国际使用量较低，题型主要是选择题。 |
| 7 | CMMU | 74 | 中 | 中文多模态学科题有场景价值；目前社区复现与模型覆盖不如 MMLU/C-EVAL。 |
| 8 | ChartQA | 72 | 高 | 图表问答经典，但不是教育专属；更适合作为图表理解原子能力。 |

### 2. 解题能力：数学专项

| 排名 | Benchmark | 权威性 | 使用量/复现生态 | 主要理由 |
|---:|---|---:|---|---|
| 1 | MATH | 93 | 极高 | 高阶数学事实标准，仍能区分模型；需区分 full MATH 与 MATH-500。 |
| 2 | GSM8K | 90 | 极高 | CoT 数学经典基准；但 95%+ 后已更像门槛。 |
| 3 | MathVista | 86 | 高 | 多模态数学权威度高，ICLR 2024 Oral；私有 test 设计较好。 |
| 4 | OlympiadBench | 84 | 中高 | 奥赛级双语多模态科学题，仍很难；GitHub stars 相对较少但任务价值高。 |
| 5 | OlymMATH | 82 | 中 | 针对数学 benchmark 饱和问题，Hard 子集有区分度；新基准还需更多引用沉淀。 |
| 6 | Math23K | 76 | 高 | 中文数学应用题经典训练/评测集；不适合直接评价现代 LLM tutor 能力。 |
| 7 | Ape210K | 72 | 中 | 大规模中文数学题资源；任务较偏答案/方程生成。 |
| 8 | ME2 | 71 | 中 | 几何关键点和讲解生成贴近教育，但较新、使用量待观察。 |
| 9 | NuminaMath | 69 | 高 | 数学训练语料影响大；作为 benchmark 容易有训练/测试边界问题。 |
| 10 | IMO-ANSWER BENCH | 66 | 低中 | 任务难度高，但模型榜单和复现生态较弱。 |
| 11 | BigMath-Verified | 64 | 中 | RL 数据价值高；不是直接模型 leaderboard。 |

### 3. 解题能力：代码与编程教育

| 排名 | Benchmark / 数据集 | 权威性 | 使用量/复现生态 | 主要理由 |
|---:|---|---:|---|---|
| 1 | HumanEval | 89 | 极高 | 代码生成经典事实标准；前沿模型已接近饱和，存在污染风险。 |
| 2 | MBPP | 83 | 高 | 入门编程题更贴近教学；也已趋于饱和。 |
| 3 | APPS | 78 | 高 | 更接近竞赛编程和隐藏测试，难度高；教育反馈维度不足。 |
| 4 | CS1QA | 73 | 中 | 真实 CS1 学生问答，适合编程教育 QA；无统一 LLM 榜单。 |
| 5 | QACP | 65 | 低中 | 中文 Python 教育 QA 有场景价值；公开模型评测不足。 |
| 6 | Codecademy / LeetCode Student Submissions | 62 | 中 | 适合学习行为和代码诊断研究；题目泄漏和平台偏差明显。 |

### 4. 教学能力与教育多模态

| 排名 | Benchmark | 权威性 | 使用量/复现生态 | 主要理由 |
|---:|---|---:|---|---|
| 1 | MathTutorBench | 88 | 中高 | 明确区分“会做题”和“会辅导”，有错误定位、纠错、脚手架等教育核心维度。 |
| 2 | Pedagogy Benchmark | 85 | 中高 | 模型覆盖多，教育学/SEND 维度清晰；但偏教师考试知识。 |
| 3 | TutorBench | 84 | 中高 | 多模态作业反馈和主动学习引导，前沿模型仍低于 56%，区分度好。 |
| 4 | EduBench | 79 | 中 | 覆盖教育场景广；部分指标依赖模型评委，需人评校准。 |
| 5 | EduEval | 78 | 中 | 中文教育生成/知识评测有价值；few-shot 口径和 GPT 评测偏差需注意。 |
| 6 | OmniEduBench | 77 | 中 | 中文新课标知识/培养双维度有特色；较新，外部复现少。 |
| 7 | K12Vista | 75 | 中 | 中文 K12 多模态题和过程正确性重要；模型覆盖不错但较新。 |
| 8 | SciVideoBench | 73 | 中 | 科学视频理解覆盖稀缺能力；任务和榜单仍在早期。 |
| 9 | EduVisBench | 72 | 中 | 教学可视化生成是关键但新兴；评分协议需更多验证。 |
| 10 | EduGuard-Bench | 70 | 中 | 教学专业度+安全双维度有价值；论文中个别 ASR 表述需谨慎核对。 |
| 11 | InteractScience | 69 | 中 | 交互式科学演示生成贴近应用；还需更多模型和人工验证。 |

### 5. 知识追踪、认知诊断与学习路径

| 排名 | 数据集/Benchmark | 权威性 | 使用量/复现生态 | 主要理由 |
|---:|---|---:|---|---|
| 1 | ASSISTments 系列 | 92 | 极高 | KT/CD 经典事实标准，使用时间长、论文多；旧版本题干文本不足。 |
| 2 | KDD Cup 2010 | 88 | 高 | 学生建模经典竞赛数据；强平台日志偏置。 |
| 3 | EdNet | 85 | 高 | 交互规模极大，适合序列 KT；缺少开放式教学语境。 |
| 4 | Junyi Academy | 82 | 高 | 中文/繁中 K12 数学平台数据价值高；受平台策略影响。 |
| 5 | PTADisc | 79 | 中 | 编程课程大规模认知诊断/KT 数据，跨课迁移价值高。 |
| 6 | FoundationalAssist | 76 | 中 | 保留题目文本和实际作答，适合 foundation model；较新。 |
| 7 | MOOCCube | 75 | 高 | MOOC 资源/推荐/知识图谱经典；不是 LLM 教学能力榜。 |
| 8 | Adaptive Geography Practice | 69 | 中 | 自适应练习场景清晰但领域窄。 |
| 9 | STATICS2011 | 64 | 中 | 小规模经典验证集；不适合大模型评测。 |
| 10 | Synthetic | 58 | 中 | 用于机制验证，不代表真实学习行为。 |

### 6. 自动评分

| 排名 | Benchmark | 权威性 | 使用量/复现生态 | 主要理由 |
|---:|---|---:|---|---|
| 1 | ASAP-AES | 92 | 极高 | 作文自动评分经典事实标准；跨 prompt、公平性和长度偏差仍是风险。 |
| 2 | ASAP-SAS | 88 | 高 | 短答案评分经典数据；细粒度解释不足。 |
| 3 | SAS-Bench | 83 | 中 | 中文高考短答案、分步评分和错误诊断贴近教育；较新。 |
| 4 | EssayJudge | 79 | 中 | 多模态作文评分有新意；开源复现和引用还需沉淀。 |
| 5 | ELLIPSE Corpus | 73 | 中 | 二语写作多维标注有价值；不是统一模型榜单。 |

### 7. 教育问答与师生对话

| 排名 | Benchmark / 数据集 | 权威性 | 使用量/复现生态 | 主要理由 |
|---:|---|---:|---|---|
| 1 | MathDial | 83 | 中高 | 学生错误、困惑和苏格拉底式引导贴近 tutor 任务。 |
| 2 | Bridge | 79 | 中 | 真实数学错题辅导对话和专家决策稀缺；规模小。 |
| 3 | SocraticLM / SocraTeach | 74 | 中 | 苏格拉底式教学数据规模较大；跨模型榜单不足。 |
| 4 | CS1QA | 72 | 中 | 编程教育 QA 真实度高；数据申请和任务口径限制使用量。 |
| 5 | Google Education Dialogue Dataset | 70 | 中 | 合成多轮对话规模大，有偏好元数据；真实课堂外推风险。 |
| 6 | QACP | 65 | 低中 | 中文编程 QA 价值明确；公开评测生态弱。 |
| 7 | EduDial | 63 | 低中 | 清单价值高，但公开入口/代码状态限制复核。 |
| 8 | IntrEx | 61 | 低中 | 学生 engagement 重要但榜单和任务定义不充分。 |

### 8. 课堂、课程资源与产品系统

这些条目更像资源库或产品入口，不建议直接按“benchmark 权威性”比较。若必须排序，应理解为“作为评测构造资源的价值”。

| 排名 | 条目 | 资源价值 | 使用量/复现生态 | 主要理由 |
|---:|---|---:|---|---|
| 1 | MOOCCube | 82 | 高 | 课程、概念图谱、用户行为完整，适合推荐和学习路径。 |
| 2 | FineWeb-Edu | 80 | 高 | 教育预训练语料影响大；不是评测集。 |
| 3 | TalkMoves | 76 | 中 | 教师话语动作识别清晰，课堂分析价值高。 |
| 4 | NCTE Transcripts | 75 | 中 | 小学数学课堂转录稀缺，适合话语分析。 |
| 5 | LectureBank | 73 | 中 | 课程多模态资源丰富，任务定义分散。 |
| 6 | TIMSS Video Study | 72 | 中 | 跨文化课堂视频/转录有价值，年代和语言差异大。 |
| 7 | ARIC | 71 | 中 | 真实课堂多模态行为数据，隐私和复现门槛高。 |
| 8 | SIGHT | 69 | 中 | 讲座转录+评论适合课程理解和反馈建模。 |
| 9 | VisualEDU | 66 | 低中 | 系统/数据价值明确，但不是通用榜单。 |
| 10 | InnoSpark、九章、子曰、星火教育、CheggMate、LearnLM | 25-55 | 不一 | 多数是产品/垂类系统入口。只有 LearnLM 在 MathTutorBench 中有可引用公开分数。 |

## 三、AI+教育原子能力覆盖统计

### 1. 原子能力矩阵

| 原子能力 | 覆盖 benchmark / 数据集 | 覆盖数 | 代表表现 | 差距判断 |
|---|---|---:|---|---|
| 通用学科知识与选择题答题 | MMLU、CMMLU、C-EVAL、E-EVAL、AGIEval、GaokaoBench | 6 | MMLU 前沿模型 90 左右；CMMLU/C-EVAL 中文强模型也到 90 左右；GaokaoBench 客观题约 70-76。 | 覆盖充分，但选择题已部分饱和；主观题和理科推理仍难。 |
| 中文本土知识与 K12 学科体系 | CMMLU、C-EVAL、E-EVAL、GaokaoBench、OmniEduBench、K12Vista | 6 | CMMLU/Spark 4.0 zero-shot 90.97；E-EVAL Qwen-72B 约 88.8；K12Vista direct 最好约 55。 | 文本选择题强，多模态/过程题弱。 |
| 标准化考试与资格考试推理 | AGIEval、GaokaoBench、C-EVAL、MMLU、OmniEduBench | 5 | AGIEval-en GPT-4o/Llama 3.1 405B 约 71；GaokaoBench 新 OpenCompass 结果约 76。 | 客观题可用，主观题、法律/物理/数学更难。 |
| 基础数学应用题 | GSM8K、Math23K、Ape210K、E-EVAL 数学子集 | 4 | GSM8K Llama 3.1 405B 96.8，Qwen3-235B 94.39。 | 基本饱和，不应作为数学教育核心排序指标。 |
| 高阶数学与竞赛推理 | MATH、MATH-500、OlymMATH、OlympiadBench、IMO-ANSWER BENCH、NuminaMath | 6 | Llama 3.1 405B full MATH 73.8；DeepSeek-R1 MATH-500 97.3；OlymMATH-HARD Gemini 2.5 Pro 约 55-58；OlympiadBench full GPT-4o 25.89。 | 覆盖较充分，难度差异大；奥赛和证明式推理仍有明显空间。 |
| 几何视觉、图表和多模态数学 | MathVista、CMMU、K12Vista、ME2、ChartQA、OlympiadBench | 6 | MathVista test 最高约 65.8；K12Vista 最好约 55；ME2 视觉关键点 Gemini 2.0 Flash 0.576。 | 仍是强区分能力；视觉定位和过程 grounding 是短板。 |
| 科学实验、视频和长时序理解 | SciVideoBench、K12Vista、CMMU、LectureBank、TIMSS Video Study、ARIC | 6 | SciVideoBench Gemini-2.5-Pro overall 64.30，GPT-4o 24.90。 | 覆盖开始增加，但视频/实验定量推理仍弱。 |
| 代码生成与算法题解 | HumanEval、MBPP、APPS、LeetCode Student Submissions、CodeForce/LiveCodeBench 类模型报告 | 5 | HumanEval Llama 3.1 405B 89.0，MBPP 88.6；更真实 coding benchmark 分化更明显。 | 入门题饱和；教育反馈、调试和学习者代码理解覆盖不足。 |
| 编程教育问答与代码诊断 | CS1QA、QACP、Codecademy Dataset、PTADisc、LeetCode Student Submissions | 5 | 多数无统一 LLM 榜单；CS1QA 真实学生问题价值高。 | 覆盖数据多但 benchmark 少，是明显空白。 |
| 作文自动评分 | ASAP-AES、ELLIPSE、EssayJudge | 3 | EssayJudge 中 GPT-4o 词汇/句子多维 QWK 较高，但 Argument Clarity 仅 0.30，低于人类 0.72。 | 总体评分可做，论证/篇章级反馈不足。 |
| 短答案和分步评分 | ASAP-SAS、SAS-Bench、GaokaoBench 主观题 | 3 | SAS-Bench DeepSeek-R1 CCS 73.76、ECS 55.90；GaokaoBench 主观总体 GPT-4 约 51。 | 细粒度一致性显著难于总分一致性。 |
| 学生错误定位与纠错反馈 | MathTutorBench、Bridge、MathDial、SAS-Bench、ME2 | 5 | MathTutorBench LearnLM mistake location 0.57、correction 0.74；GPT-4o correction 0.84。 | 错误定位仍弱，直接纠错强于诊断学生思路。 |
| 苏格拉底式引导与脚手架 | MathTutorBench、MathDial、SocraticLM、Bridge、TutorBench | 5 | MathTutorBench 中 Qwen2.5-Math-7B 解题 0.88，但 scaffolding win 0.06、pedagogy IF win 0.07。 | “会解题不会教”现象最明显；真实 tutor 核心短板。 |
| 教学法知识与教学设计 | Pedagogy Benchmark、EduBench、EduEval、OmniEduBench | 4 | Pedagogy Benchmark 顶部 CDPK/SEND 约 85-89；EduBench 平均可到 9/10 左右。 | 考试型教学知识较强，真实课堂转化未充分验证。 |
| 学习规划、个性化与学情分析 | EduBench、EduEval、ASSISTments、EdNet、FoundationalAssist、MOOCCube | 6 | EduBench 覆盖学习规划/学情分析；KT 数据集多用 AUC/ACC 而非 LLM 生成质量。 | 数据覆盖高，但 LLM 与传统 KT/CD 评价口径未统一。 |
| 知识追踪与答题预测 | ASSISTments、KDD Cup 2010、EdNet、Junyi、STATICS2011、Synthetic、Adaptive Geography Practice | 7 | 传统 KT 模型有成熟 AUC/ACC 生态；旧数据缺题干和开放回答。 | 非 LLM 体系成熟，LLM 融合评测不足。 |
| 认知诊断与知识点掌握 | ASSISTments、PTADisc、Junyi、FoundationalAssist、数字教育应用算法智能诊断公共数据集 | 5 | PTADisc 覆盖 4,054 概念和大规模 PTA 作答；FoundationalAssist 保留文本和错误选项。 | 很适合教育算法，缺少开放统一 LLM leaderboard。 |
| 教育资源检索、推荐与学习路径 | MOOCCube、TutorialBank、FineWeb-Edu、Chinese FineWeb Edu、SIGHT、LectureBank | 6 | MOOCCube/TutorialBank 资源丰富；FineWeb-Edu 是训练语料。 | 资源侧覆盖足，模型效果评价分散。 |
| 课堂话语和教师行为分析 | TalkMoves、NCTE Transcripts、TIMSS Video Study、SIGHT、Google Education Dialogue Dataset | 5 | TalkMoves/NCTE 提供真实课堂话语标注；Google 数据规模大但合成。 | 真实课堂标注稀缺，跨文化/跨教师泛化难。 |
| 课堂视觉行为与参与度识别 | SCB-Dataset、ARIC、IntrEx、课堂视频资源 | 4 | SCB/ARIC 适合行为识别；IntrEx 关注 engagement。 | 视觉行为和对话 engagement 尚未和学习效果打通。 |
| 教育安全、合规与角色扮演 | EduGuard-Bench、EduBench、EduEval、产品系统安全评测 | 3 | EduGuard-Bench 中 Claude-3.7 RFS 0.77、ASR 27.0；DeepSeek-V3 RFS 0.73 但 ASR 81.6。 | 教学能力与安全性不一致，需单独测。 |
| 教学可视化生成 | EduVisBench、VisualEDU、ME2、InteractScience、MathVista | 5 | EduVisAgent 81.6；v0 58.2；GPT-4o Webpage 38.1；InteractScience 最佳 PFT 约 41。 | 视觉/交互生成仍弱，专门流程明显优于通用模型裸生成。 |
| 交互式科学演示生成 | InteractScience、EduVisBench、VisualEDU | 3 | InteractScience Claude-Sonnet-4 PFT 41.47、GPT-5 39.47、GPT-4o 28.27。 | 覆盖少但应用价值高，功能完整性是瓶颈。 |
| 教育垂类系统端到端能力 | LearnLM、InnoSpark、九章、子曰、星火教育、CheggMate + 外部 benchmark | 6 | LearnLM 在 MathTutorBench 有公开结果；其他产品系统多无可复现统一分数。 | 产品能力强依赖闭源题库/工作流，外部可比性最弱。 |

### 2. 覆盖数量统计

按原子能力归并后，本轮共拆出 24 个 AI+教育能力点。覆盖情况如下：

| 覆盖等级 | 能力数量 | 能力 |
|---|---:|---|
| 高覆盖，且有公开模型分数 | 10 | 通用学科、中文 K12、标准化考试、基础数学、高阶数学、多模态数学、代码生成、自动评分、短答案评分、教学可视化/交互生成 |
| 中覆盖，有数据或新榜但复现仍不足 | 9 | 科学视频、学生错误定位、苏格拉底式引导、教学法知识、学习规划、认知诊断、教育资源推荐、课堂话语、教育安全 |
| 数据多但缺 LLM 统一榜单 | 4 | 编程教育问答、知识追踪、课堂视觉行为、教育垂类系统端到端能力 |
| 明显薄弱 | 1 | 长期学习增益/真实 A-B 实验效果。原清单里几乎没有能直接评估“学生学会了多少”的公开 benchmark。 |

按领域看：

| 领域 | 覆盖 benchmark / 数据集数量 | 表现概况 |
|---|---:|---|
| 解题/考试 | 20+ | 覆盖最充分；选择题和基础数学已饱和，高考主观题、奥赛、多模态题仍难。 |
| 教学/辅导 | 10+ | 近两年增长最快；真实 tutor、脚手架、错误定位和作业反馈仍远低于单题解题。 |
| 知识追踪/诊断 | 10+ | 传统教育数据丰富；与 LLM 生成式教育能力之间缺统一桥接 benchmark。 |
| 自动评分 | 5 | 作文/短答案都有经典数据；细粒度步骤一致性、错误原因和公平性仍弱。 |
| 教育问答/对话 | 8 | 数据不少，但真实对话少、榜单少，教学决策比语言表面质量更关键。 |
| 课堂/课程资源 | 15+ | 资源丰富但任务分散；更适合构造下游评测，而不是直接排名模型。 |
| 教育产品系统 | 6 | 可用入口多，可复现公开分数少；除 LearnLM 外，大多需要外部 benchmark 二次测。 |

### 3. 表现差异结论

1. **基础知识和基础数学已经不能代表教育能力。** MMLU、GSM8K、HumanEval 顶部模型已接近饱和，用它们筛掉弱模型可以，但用来排序教育产品会误导。
2. **真实教学能力的短板集中在诊断、脚手架和反馈。** MathTutorBench、TutorBench、Bridge、MathDial 都显示，模型能解题不等于能判断学生错因并给出合适下一步。
3. **多模态教育题比文本题更有区分度。** MathVista、K12Vista、ME2、SciVideoBench、EduVisBench、InteractScience 的最高分明显低于通用选择题，且错误更接近真实教学场景。
4. **自动评分要看细粒度，不只看总分。** EssayJudge 和 SAS-Bench 都说明，总体分数一致性可能还可以，但论证清晰度、分步一致性和错误原因解释明显更难。
5. **知识追踪和资源推荐是“数据强、LLM 榜单弱”。** ASSISTments、EdNet、MOOCCube 等非常权威，但它们评价的是学生状态预测/推荐/行为建模，不是直接评价大模型讲课质量。
6. **长期学习增益是最大空白。** 现有公开 benchmark 很少直接测学生使用模型后是否真正学得更好、迁移更强、保持更久。若要评估教育产品，最终仍需小规模教学实验或平台 A/B 指标。

## 四、推荐评测组合

如果目标是评估“AI 教育模型/产品”，不建议只跑一个综合榜。可以按用途组合：

| 目标 | 推荐主 benchmark | 推荐补充 |
|---|---|---|
| 中文 K12 解题底座 | C-EVAL、CMMLU、E-EVAL、GaokaoBench | K12Vista、CMMU、OlympiadBench |
| 数学 tutor | MATH、OlymMATH、MathVista、MathTutorBench | ME2、MathDial、Bridge |
| 多模态作业反馈 | TutorBench、K12Vista、MathVista、EssayJudge | ME2、CMMU |
| 自动批改 | ASAP-AES、ASAP-SAS、SAS-Bench、EssayJudge | GaokaoBench 主观题 |
| 教学法/教师助手 | Pedagogy Benchmark、EduBench、EduEval、OmniEduBench | TutorBench、EduGuard-Bench |
| 知识追踪/个性化学习 | ASSISTments、EdNet、Junyi、FoundationalAssist | MOOCCube、PTADisc |
| 课堂/课程理解 | SciVideoBench、LectureBank、TalkMoves、NCTE Transcripts | ARIC、TIMSS Video Study、SIGHT |
| 交互式教学内容生成 | EduVisBench、InteractScience | VisualEDU、MathVista |

## 五、后续建议

- 建一个小型内部评测集，把本报告的 24 个原子能力映射到产品场景。例如“错因诊断”“分层提示”“讲解改写”“题目推荐”“作文批改解释”“课堂话语识别”各取 30-100 条高质量样本。
- 对公开 benchmark 采用分层权重，而不是平均分：基础选择题权重低，多模态、主观题、错误诊断、脚手架和安全权重高。
- 对 C-EVAL、CMMLU、MMLU、GSM8K、HumanEval 这类高使用量但可能饱和/泄漏的 benchmark，只做门槛项；真正排序依赖 OlymMATH、MathVista、TutorBench、MathTutorBench、SAS-Bench、EduGuard-Bench 等更贴近教育困难点的任务。
- 产品系统评测必须补“真实使用指标”：学生留存、题目完成率、提示后改正率、错因复现率、教师采纳率、作业批改一致性、敏感场景拒答/转介质量。

## 主要新增来源

- CMMLU official GitHub leaderboard: https://github.com/haonan-li/CMMLU
- C-EVAL official GitHub and website: https://github.com/hkust-nlp/ceval, https://cevalbenchmark.com/
- AGIEval official GitHub: https://github.com/ruixiangcui/AGIEval
- GAOKAO-Bench official GitHub: https://github.com/OpenLMLab/GAOKAO-Bench
- MathVista official project page and GitHub: https://mathvista.github.io/, https://github.com/lupantech/MathVista
- OlympiadBench official GitHub: https://github.com/OpenBMB/OlympiadBench
- OpenCompass common benchmark documentation: https://opencompass.readthedocs.io/en/latest/user_guides/corebench.html
- OpenAI GPT-4.1 / GPT-5 / open models benchmark pages: https://openai.com/index/gpt-4-1/, https://openai.com/index/introducing-gpt-5-for-developers/, https://openai.com/open-models
- Meta Llama 3.1 405B model card: https://huggingface.co/meta-llama/Llama-3.1-405B
- Qwen3 GitHub, blog, and technical report: https://github.com/QwenLM/Qwen3, https://qwenlm.github.io/blog/qwen3/, https://arxiv.org/abs/2505.09388
- DeepSeek-R1 official release and repository: https://api-docs.deepseek.com/news/news250120, https://github.com/deepseek-ai/DeepSeek-R1
