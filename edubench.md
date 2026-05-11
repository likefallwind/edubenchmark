# Edu Benchmark & Datasets

**模型、数据集、评测概览:**
* Large Language Models for Education: A Survey and Outlook
* https://github.com/GeminiLight/awesome-ai-llm4education
* Education Benchmark Share

---

## 一、解题能力评测Benchmark

### 1. 通用学科评测
* **MMLU**: 通用大模型评测基准,覆盖57个学科,包含STEM、人文社科、商科等全领域,难度从初中到大学专业级,其STEM子集是理科教育能力评测的核心基准: https://huggingface.co/datasets/cais/mmlu
* **CMMLU**: 中文版MMLU,覆盖67个主题,深度适配中文语境与文化背景,是中文大模型通识与学科知识评测的通用基准: https://github.com/haonan-li/CMMLU
* **C-EVAL**: 中文权威学科评测基准,覆盖52个学科,难度从初中到职业资格考试,是国内教育大模型基础能力评测的通用标准: https://github.com/hkust-nlp/ceval
* **AGIEval**: 覆盖中国高考、公务员考试、美国SAT、LSAT等权威考试,核心评测模型的人类级考试解题能力: https://github.com/ruixiangcui/AGIEval
* **GaokaoBench**: 2023年发布,覆盖中国高考全科(语文、数学、英语、文综、理综),包含3000+历年真题,配套标准答案与评分标准,是中文大模型高考级别解题能力的评测基准: https://github.com/OpenLMLab/GAOKAO-Bench
* **E-EVAL**: ACL 2024发布,覆盖中文K12全学段的评测基准,包含4351道选择题,覆盖小学、初中、高中全学科,评估模型对基础教育阶段知识的体系化掌握能力: https://github.com/AI-EDU-LAB/E-EVAL
* **Olympiad Bench**: 2024年发布,覆盖国际奥林匹克数学、物理、化学、生物竞赛真题,多语言、超难级别,核心评测大模型的顶尖科学推理与创造性解题能力: https://github.com/OpenBMB/OlympiadBench
* **CMMU**: IJCAI2024,中文多模态多题型理解与推理基准,覆盖图文结合的全学科题目,适配中文多模态教育大模型评测,覆盖小学、初中、高中学段,七门学科: https://github.com/flageval-baai/CMMU
* **ChartQA**: ACL 2022,教育场景图表问答基准,覆盖理科统计图、数据表、实验图等,核心评测模型对图表数据的理解与推理能力,适配物理、化学、生物等理科教育场景: https://github.com/vis-nlp/chartqa

### 2. 数学解题专项

| 名称 | 发布方/时间 | 特点 | 场景 | Link |
|---|---|---|---|---|
| GSM8K | OpenAI, 2021 | 8500道小学数学应用题,核心考察多步链式推理能力,是CoT技术验证的核心基准,全球大模型数学能力必测项 | 基础数学推理能力评测、思维链算法验证 | https://huggingface.co/datasets/openai/gsm8k |
| MATH | OpenAI, 2021 | 12500道高中数学竞赛题,分7大学科,配套完整解题步骤,难度分级明确,是中高阶数学能力评测的黄金基准 | 高阶数学推理、竞赛级解题能力评测 | https://github.com/hendrycks/math |
| Math23K | 中科院, 2017 | 23000道中文小学数学应用题,是中文场景数学解题模型训练与评测的核心基准 | 中文数学解题模型研发、小学数学推理能力评测 | https://github.com/SCNU203/Math23k |
| Ape210K | 腾讯, 2020 | 21万道中文数学题,覆盖小学到初中全学段,是目前规模最大的公开中文数学解题数据集 | 大规模中文数学大模型预训练、全学段解题能力评测 | https://github.com/Chenny0808/ape210k |
| NuminaMath | 2025 | 86万道数学竞赛题与完整CoT解决方案,覆盖AMC、AIME、IMO等赛事 | 竞赛级数学大模型微调、高阶创造性推理能力评测 | https://huggingface.co/collections/AI-MO/numinamath |
| IMO-ANSWER BENCH | 2025 | 面向国际数学奥林匹克(IMO)级别数学推理能力评测的高难度 benchmark | 评估大模型在非模板化、长链条、创造性数学解题任务上的表现。 | https://huggingface.co/datasets/Hwilner/imo-answerbench |
| OlymMATH | 2025 | 200道双语:中英完全平行,覆盖代数、几何、数论、组合数学四大竞赛核心模块 | 中高阶数学推理能力评测的基准 | https://github.com/RUCAIBox/OlymMATH |
| MathVista | 2023 | 包含图表、几何图形、数学公式、图文结合的数学题 | 评测多模态大模型的数学视觉理解与推理能力 | https://github.com/lupantech/MathVista?tab=readme-ov-file |
| BigMath-Verified | 2025 | 250k经过严格验证的高质量数学计算填空题 | 专为LLM数学推理强化学习设计,兼顾规模、质量、难度覆盖与可验证性 | https://huggingface.co/datasets/SynthLabsAI/Big-Math-RL-Verified |
| ME | 2025 | 覆盖几何题视觉关键点(辅助线)标注+分步解题讲解的高质量教育数据集 | 几何题辅助线等视觉关键点的教学级精细化标注,配套双粒度专家解题讲解 | https://huggingface.co/datasets/jungypark/ME2 |

### 3. 代码能力专项
* **HumanEval**: 2021年OpenAI发布,代码生成能力权威评测基准,专门用于评估大模型根据自然语言描述生成功能正确的Python代码的能力: https://github.com/openai/human-eval
* **MBPP**: 2021年谷歌发布,面向入门级编程学习者的代码数据集,包含1000道入门级编程题,配套测试用例与标准答案: https://huggingface.co/datasets/Muennighoff/mbpp

---

## 二、教学能力评测Benchmark

| 名称 | 发布方/时间 | 评测维度 | 特点 | Link |
|---|---|---|---|---|
| Pedagogy Benchmark | 2025 | 跨领域教学法知识、特殊教育(SEND)教学能力、教学设计、学情评估能力 | 基于教师职业资格考试真题构建,覆盖97个大模型评测,核心验证模型的教育学专业能力 | https://huggingface.co/datasets/AI-for-Education/pedagogy-benchmark |
| MathTutorBench | EMNLP 2025 | 数学辅导专业度、学生认知理解、教学法适配性、开放式对话辅导能力 | 基于学习科学理论构建,配套专家级奖励模型,可精准区分专家与新手教师的教学回复 | https://github.com/eth-lre/mathtutorbench |
| EduBench | 2025 | 作业批改、学习规划、心理健康辅导、学情分析、知识点讲解等9大教育场景 | 包含4000+教育场景上下文,12维度评测体系 | https://github.com/ybai-nlp/EduBench |
| EduEval | 2025 | 知识准确性、教学引导能力、多轮对话辅导、安全合规、个性化适配、学情诊断能力 | 中文教育大模型评测基准,覆盖K12、高等教育、职业教育全学段 | https://github.com/Maerzs/E_edueval |
| OmniEduBench | 2025 | 知识理解维度、核心素养培养维度,覆盖11种考试题型、全学段全学科 | 同时评估知识掌握与素养培养的中文教育基准,包含24602道高质量问答对,贴合国内新课标要求 | https://mind-lab-ecnu.github.io/OmniEduBench/ |
| EduGuard-Bench | 2026 | 教学专业度+安全合规双维度 | 评估教育大模型作为“模拟教师”的专业可信度与对抗安全性的基准 | https://github.com/YL1N/EduGuardBench |
| TutorBench | 2025 | 自适应讲解,作业反馈与批改以及主动学习引导 | 1.47k 多模态数据集(文本+图片,含手写作业、图表、截图),覆盖6大 STEM 学科:生物、物理、化学、统计学、微积分、计算机科学。 | https://huggingface.co/datasets/ScaleAI/TutorBench |
| EduVisBench | 2025 | 逻辑序列,结构丰富度,语义对齐,讲解引导,交互参与度 | 教育可视化多模态评测基准,多模态输入+输出 | https://huggingface.co/datasets/Haonian/EduVisBench/viewer |
| SciVideoBench | 2025 | 科学事实理解,实验过程推理,长时序课堂理解,多模态对齐 | 聚焦科学教学视频,考验模型对长时程教学内容的理解与结构化能力 | https://huggingface.co/datasets/groundmore/scivideobench |
| K12Vista | 2025 | 知识掌握度,多模态理解,逻辑推理,过程正确性:步骤是否正确、是否跳步、是否幻觉、是否逻辑矛盾 | 构建了面向中文 K12教育的超大规模多模态评测基准,并首次系统性评测 MLLM 在K12场景的推理过程正确性 | https://github.com/lichongod/K12Vista |
| InteractScience | 2025 | 评测大模型生成交互式科学演示HTML 代码的能力,覆盖物理、化学、生物等理科教学场景 | 专门评估大模型生成带动态交互(滑块、按钮、下拉框等)的科学教学网页的能力 | https://github.com/open-compass/InteractScience |

---

## 三、知识追踪领域

| Dataset | 发布方/时间 | 特点 | Link |
|---|---|---|---|
| ASSISTments系列 | 2009-2010、2012-2013、2015、2017多个数据集子集 | 覆盖K12数学学科,包含题目知识点标签、学生作答对错、作答时长等核心特征,配套完整基线模型与评测指标 | https://sites.google.com/site/assistmentsdata/datasets |
| KDD Cup 2010 | KDD竞赛组委会,2010 | 代数答题数据集,包含百万级学生交互记录,分为Bridge to Algebra、Algebra I两个子集,是大规模KT模型评测的经典基准 | https://pslcdatashop.web.cmu.edu/KDDCup/downloads.jsp |
| EdNet | 韩国,2020 | Santa 智能学习平台的数据,131M+交互记录,来自784,309 名学生,包含超1亿条学生学习行为记录,覆盖答题、视频观看、点击、时长等多维度特征,分为KT1-KT4四个梯度子集 | https://github.com/riiid/ednet |
| Junyi Academy | 台湾均一教育平台,2018 | 中文K12数学KT数据集,247k学生,包含百万级交互记录,配套完整的知识点层级体系,是中文场景KT研究的核心基准 | https://pslcdatashop.web.cmu.edu/DatasetInfo?datasetId=1198 |
| FoundationalAssist | 2026 | 包含5000名学生、170万次交互,保留题目文本、学生实际作答内容、错误选项细节,对齐K12课标 | https://huggingface.co/datasets/ASSISTments/FoundationalASSIST/viewer |
| 数字教育应用算法智能诊断公共数据集 | 教育部/北京师范大学, 2025 | 教育算法公共数据集,覆盖教学诊断、学情预警、认知发展等场景 | https://www.nda.gov.cn/sjj/ywpd/szkjyjcss/0915/20250915162252254699971_pc.html |
| PTADisc | 2023 | 包含74门课程, 1,530,100名学生, 4,054个知识概念, 225,615个问题/练习题, 超过680,000,000条学生回答记录 | https://github.com/wahr0411/PTADisc |
| STATICS2011 | 2011 | 333个学生,1224个题目数,来源CMU的OLI (Open Learning Initiative)在线学习系统 | https://github.com/chrispiech/DeepKnowledgeTracing/tree/master/data/synthetic |
| Synthetic | 2015 | 合成模拟数据集,用于测试模型在已知结构的理想环境下的表现,4k个虚拟学生,50个问题构建的模拟生成的学生答题行为数据 | https://pslcdatashop.web.cmu.edu/DatasetInfo?datasetId=507 |
| Adaptive Geography Practice |  | 大规模高质量的真实在线学习日志,90k名地理学习者在自适应练习系统中的行为 | https://www.fi.muni.cz/adaptivelearning/?a=data |

---

## 四、自动评分领域
* **ASAP-AES**: 2012年,英文作文批改基准,包含8个不同年级、不同主题的作文集,配套专家多维度评分: https://www.kaggle.com/c/asap-aes/data
* **ASAP-SAS**: 2012年,短答案主观题批改基准,覆盖科学、历史等学科的简答题,配套专家评分与要点标注: https://www.kaggle.com/c/asap-sas/data
* **ELLIPSE Corpus**: 2024年,9,000+英语学习者作文,多维度(连贯、句法、词汇)评分: https://www.kaggle.com/datasets/mpware/ellipse-corpus
* **EssayJudge**: ACL2025,多模态细粒度AES基准,专门评测 MLLM在词汇-句子-篇章三级写作能力: https://arxiv.org/pdf/2502.11916
* **SAS-Bench**: 2025年,高考9学科、1,030题、4,109条,分步评分+错误诊断: https://github.com/PKU-DAIR/SAS-Bench

---

## 五、教育问答领域
* **MathDial**: 2022,数学辅导对话数据集,核心聚焦苏格拉底式引导对话,而非直接给答案,包含学生错误概念识别、导师分步引导的完整对话轨迹: https://huggingface.co/datasets/eth-nlped/mathdial
* **Google Education Dialogue Dataset**: Google 2024,由Gemini Ultra 模拟生成(非真实师生对话)47,234 条完整师生对话(40,000训练+7,234测试): https://github.com/google-research-datasets/Education-Dialogue-Dataset
* **EduDial**: 2025,基于教学大纲与策略,教师-学生智能体交互模拟生成34,250个多轮对话会话,K-12 数学(345个核心知识点、173个章节): https://github.com/Mind-Lab-ECNU/EduDial/tree/main
* **IntrEx**: EMNLP 2025,面向教育对话的学生兴趣度/参与度大规模标注数据集,专门建模辅导对话中学生的学习参与度、内容兴趣度: https://huggingface.co/collections/XingweiT/intrex
* **Bridge**: NAACL 2024,数学错题辅导的多轮对话+专家决策标注数据集,700条真实师生数学辅导对话,每条对话聚焦:学生犯错→新手 tutor 回复专家 tutor修正回复+专家决策标注: https://github.com/rosewang2008/bridge#dataset
* **SocraticLM**: NeurIPS 2024,35k多轮师生教学对话数据集+22k单轮师生教学对话数据集: https://github.com/Ljyustc/SocraticLM#socrateach-dataset
* **QACP**: 2024,中文编程知识问答数据集:10,960个高质量问题;一个专家初标,一个专家复核: https://github.com/NTAIX/Chinese-Python-QA-Dataset
* **CS1QA**: 2022,9,237个问答对的编程教育问答数据集,附带学生代码、问题类型标注和与问题相关的代码行: https://github.com/cyoon47/CS1QA/tree/main/data

---

## 六、其他教育资源
* **FineWeb-Edu**: Hugging Face 官方团队于2024年6月发布的高质量教育专属预训练语料: https://huggingface.co/datasets/HuggingFaceFW/fineweb-edu
* **Chinese Fineweb Edu**: OpenCSG于2024年8月正式发布的高质量中文教育预训练语料: https://huggingface.co/datasets/opencsg/chinese-fineweb-edu
* **IM2LATEX-100K**: 公式识别核心数据集,包含10万张印刷/手写数学公式图片与对应LaTeX代码,是教育场景公式识别、公式批改模型研发的基准: https://arxiv.org/abs/1609.04938
* **LectureBank**: 大学课程多模态数据集,包含课程视频、音频、PPT、板书、字幕,覆盖多学科,适配课程内容理解、知识点提取、自动字幕生成等场景: https://github.com/Yale-LILY/LectureBank
* **SCB-Dataset**: 智慧教室课堂行为视频数据集,包含学生听课、举手、互动、走神等行为标注: https://github.com/Whiffe/SCB-dataset
* **NCTE Transcripts**: 2022,约1,660节小学数学课(4-5年级)的完整文本实录: https://github.com/ddemszky/classroom-transcript-analysis
* **ARIC 真实课堂监控行为数据集** (电子科技大学,2024): 多视角4K真实课堂监控,含图像、音频、文本三模态,标注师生全场景行为,官方地址: https://ivipclab.github.io/publication_ARIC/ARIC/
* **TalkMoves**: 包含567篇由人工注释的K-12 数学课堂教学转录文本,涵盖完整课程或课程片段: https://github.com/SumnerLab/TalkMoves/tree/main/data
* **TIMSS Video Study**: 超过1,000节八年级数学和科学课堂的录像以及转录文本,涵盖7个国家: https://www.timssvideo.com/transcripts
* **SIGHT**: 收录了MIT数学公开课的288个讲座转录文本和15,784条学生评论: https://github.com/rosewang2008/sight/tree/main/data
* **VisualEDU**: 面向数学教育的端到端解题可视化讲解生成系统+配套标注数据集,基于大模型与 Manim 动画引擎,实现数学题的分步解题、动画代码生成、视频渲染全流程自动化: https://github.com/Uchihalchigo/VisualEDU
* **MLPdataset**: 9031 张大学课程幻灯片、180+小时真人教授讲解视频、10位大学讲师的完整系列课程: https://github.com/mlpdataset
* **MOOCCube**: 【ACL 2020】 http://moocdata.cn/data/MOOCCube,包含706门来自“学堂在线”的真实课程,38,181个教学视频,包含114,563个概念,并构建了概念图谱(包含先后修、上下位等关系,包含199,199名用户的选课记录和详细视频观看行为(如观看次数、倍速、拖拽位置等)。
* **TutorialBank**: 【ACL 2018】 https://github.com/Yale-LILY/TutorialBank,包含20,243个资源,均带有有效的URL、元数据(Meta-data)和经过良好标注的主题(Topics)
* **Codecademy Dataset**: 包含编程学习者的代码提交、学习轨迹、错误记录,覆盖Python、Java、JavaScript等主流语言,适配编程学习路径规划、个性化辅导: https://github.com/Codecademy/datasets
* **LeetCode Student Submissions**: 覆盖 LeetCode 全量题目,包含题目描述、难度分级、测试用例、用户提交代码、运行结果(AC/WA/TLE/RE等)、错误类型、执行时间/内存性能评分: https://huggingface.co/datasets/newfacade/LeetCodeDataset
* **APPS Dataset**: 包含5000道算法编程题、23万条用户提交记录、错误类型标注、测试用例: https://github.com/hendrycks/apps

---

## 七、教育大模型系统
* **InnoSpark**: 华东师范大学联合上海创智学院研发的教育垂类大模型,适配K12到高等教育全场景,核心具备智能备课、AI一对一家教、学情分析、跨学科教学设计能力: https://github.com/sii-research/coclp.git 、 https://huggingface.co/collections/sii-research/innospark-687c9533a8ca0fb33ef57e5a 、 https://beta.aiecnu.cn
* **学而思九章大模型**: 好未来学而思自研的数学专属教育垂类大模型,覆盖3-18岁全学段数学教学,核心具备分步讲题、引导式解题、错题诊断、奥数辅导能力,配套完整的中小学数学知识图谱: https://www.mathgpt.com/
* **网易有道子曰大模型**: 网易有道自研的全学科教育垂类大模型,覆盖K12全学科、语言学习、职业教育,核心优势包括多模态讲题、作文批改、口语陪练、智能教案生成,深度适配国内新课标体系: https://aicenter.youdao.com/#/home
* **科大讯飞星火教育大模型**: 科大讯飞基于星火大模型打造的教育专属版本,覆盖学情诊断、智慧备课、分层作业生成、口语测评、AI实验模拟,深度适配国内中小学智慧课堂场景: https://xinghuo.xfyun.cn/education
* **CheggMate**: 教育平台 Chegg联合 OpenAI 打造的教育大模型系统,覆盖中学到大学全学段,核心具备作业分步讲解、考试备考辅导、知识点精讲、错题诊断能力,依托平台海量题库与教学资源: https://www.chegg.com/cheggmate
* **Google LearnLM**: Google DeepMind 专为教育场景研发的大模型系列,聚焦K12 数学与科学教学,可根据学生认知水平调整教学节奏,落地于Google Classroom 教育生态: https://cloud.google.com/solutions/learnlm