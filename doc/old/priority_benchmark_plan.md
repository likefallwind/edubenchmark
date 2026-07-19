# 现阶段教育 Re-benchmark 优先级计划

## 目标

在评测成本明显偏高的前提下，本计划不再追求“把所有 benchmark 都跑一遍”，而是优先回答三个问题：

1. 哪些模型真正适合教育场景，而不只是通用能力强？
2. 哪些模型在“教、学、评、安全”的关键任务上有稳定差异？
3. 哪些 benchmark 值得我们花 API、judge 和人工复核成本重测，哪些只需要引用公开 leaderboard？

核心原则：


| 原则       | 含义                                                              |
| -------- | --------------------------------------------------------------- |
| 教育专属性优先  | 越能直接反映教学、学习、作答评价、安全风险，越优先实测。                                    |
| 公开榜单优先引用 | 对 MMLU-Pro、MathVista、Video-MME、LiveCodeBench 等通用榜单，优先引用，不重复全量跑。 |
| 任务交集去重   | 如果两个 benchmark 都测类似 tutoring、短答案评分或选择题能力，只保留信息密度更高或成本更低的一个。     |
| 小样本先行    | 对高成本开放生成、视频、多模态、LLM judge 任务，先用分层抽样验证区分度，再决定是否扩展。               |
| 可复现优先    | 没有稳定公开数据/代码/协议的 benchmark 不进入 P0。                               |


## 优先级定义


| 优先级      | 含义                            | 执行策略                        |
| -------- | ----------------------------- | --------------------------- |
| P0 必测    | 当前最能支撑教育 re-benchmark 结论的核心任务 | 第一轮立即跑，尽量形成完整分析报告。          |
| P1 建议测   | 与 P0 互补，能增加任务多样性，但成本或重复度略高    | P0 跑完后按预算抽样跑。               |
| P2 暂缓/引用 | 有价值但当前不适合花成本重测                | 引用公开 leaderboard、官方结果或放入专项。 |


## P0：第一轮必须评测


| 覆盖任务 / 能力        | 归属  | EduBench 子集       | TutorBench 子集                                |
| ---------------- | --- | ----------------- | -------------------------------------------- |
| 学科问答与概念讲解        | 教   | `Q&A`、`IP`        | `USE_CASE_1` Adaptive Explanation Generation |
| 自适应解释            | 教   | `Q&A`、`PLS`、`PCC` | `USE_CASE_1` Adaptive Explanation Generation |
| 错误纠正与反馈          | 教/评 | `EC`              | `USE_CASE_2` Assessment & Feedback           |
| 学生作答评价 / 批改      | 评   | `AG`              | `USE_CASE_2` Assessment & Feedback           |
| 引导式学习 / 脚手架提示    | 教   | `IP`              | `USE_CASE_3` Active Learning Support         |
| 主动学习支持 / 苏格拉底式引导 | 教   | `IP`              | `USE_CASE_3` Active Learning Support         |
| 教学材料生成           | 教   | `TMG`             | 无                                            |
| 出题 / 练习生成        | 教/评 | `QG`              | 无                                            |
| 个性化学习支持          | 学   | `PLS`             | 无                                            |
| 个性化内容生成          | 教/学 | `PCC`             | 无                                            |
| 情绪支持 / 学习动机支持    | 学   | `ES`              | 无                                            |
| 教师角色与教育场景适配      | 教/学 | 9 个场景横切           | 3 个 use case 横切                              |
| 事实准确性与推理可靠性      | 教/学 | 9 个场景横切           | 3 个 use case 横切                              |
| 教育安全边界           | 安全  | 无                 | 无                                            |
| 真实学习过程建模         | 学   | 无                 | 无                                            |
| 教师专业知识 / 教学法知识   | 教   | 无                 | 无                                            |



| 大类        | Benchmark                                                                                 | 核心任务                           | 为什么是 P0                                              | 建议规模                                                                                                              | 主要指标                                  | 成本判断                       |
| --------- | ----------------------------------------------------------------------------------------- | ------------------------------ | ---------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- | ------------------------------------- | -------------------------- |
| C4 评      | [SAS-Bench](https://huggingface.co/datasets/aleversn/SAS-Bench)                           | 短答案评分、步骤评分、错因诊断                | 教育评价场景最核心；同时覆盖总分、步骤分和错因，信息密度最高；我们已经有初步 pipeline 和结果。 | 优先全量 4,109 条。                                                                                                     | QWK、CCS、ECS                           | 中。短文本为主，成本可控，指标自动化。        |
| C4 评      | [ASAP-AES / ASAP 2.0](https://github.com/scrosseye/ASAP_2.0)                              | 作文自动评分                         | 作文评分是“评”中不可替代的长文本任务，与 SAS-Bench 的短答案/步骤评分互补。         | 每个 prompt 分层抽样，先 800-1,600 篇；不建议第一轮全量。                                                                            | QWK、Pearson、RMSE                      | 中到高。长文本 token 成本高，但自动评分成熟。 |
| C2 教      | [Pedagogy Benchmark](https://huggingface.co/datasets/AI-for-Education/pedagogy-benchmark) | 教师专业知识、教学法、特殊教育                | 教育专属、低成本、自动评分；能快速判断模型是否具备教师专业知识底座。                   | 全量约 1.1K 题。                                                                                                       | Accuracy，按 CDPK/SEND 和教学子域分层。         | 低。选择题自动评分。                 |
| C2/C3 教/学 | [EduBench](https://github.com/ybai-nlp/EduBench) 选定子任务                                    | 教学设计、纠错反馈、个性化学习支持、情绪支持、个性化内容生成 | 覆盖“教”和“学”的开放式教育生成能力；比通用问答更贴近真实产品。                    | 每个关键子任务 30-50 条，优先 Teaching Material Generation、Error Correction、Personalized Learning Support、Emotional Support。 | Rubric score、LLM judge、人类抽检一致性。       | 高。开放式生成 + judge，必须抽样。      |
| C5 安全     | [EduGuard-Bench](https://github.com/YL1N/EduGuardBench)                                   | 教育安全、教师角色一致性、对抗提示              | 教育安全是上线底线；比通用 safety benchmark 更贴近教师/学生场景。           | adversarial prompts 可全量 801 条；SATAs 可先抽样。                                                                         | ASR、拒答质量、Role-playing Fidelity Score。 | 中到高。需要生成回复 + judge/人工复核。   |


## P1：建议第二批评测


| 大类    | Benchmark                                                           | 核心任务              | 为什么不是 P0                                                     | 建议规模                           | 主要指标                                                  | 成本判断                   |
| ----- | ------------------------------------------------------------------- | ----------------- | ------------------------------------------------------------ | ------------------------------ | ----------------------------------------------------- | ---------------------- |
| C2 教  | [EduVisBench](https://github.com/aiming-lab/EduVisBench)            | 教学可视化生成、视觉化讲解     | 任务非常独特，但多模态生成和 rubric 成本高，适合在文本教育能力初筛后再测。                    | 30-50 条代表样例。                   | 自定义 rubric：正确性、可视化表达、步骤清晰度、教学有效性。                     | 高。多模态生成 + judge/人工复核。  |
| C2 教  | [TutorBench](https://huggingface.co/datasets/tutorbench/tutorbench) | tutoring、脚手架、反馈质量 | 与 EduBench 教学/纠错反馈有交集；如果目标模型已有 leaderboard，可先引用。             | 目标模型缺榜单时抽样 100-200 条。          | Rubric score、LLM judge。                               | 高。rubric 多且 judge 成本高。 |
| C1 通用 | [C-Eval](https://github.com/hkust-nlp/ceval)                        | 中文本土多学科考试知识       | 通用选择题，不是教育专项能力；但中文本土能力对国内教育场景重要。                             | 每个 subject 5-10 题，约 260-520 题。 | Accuracy，按 52 学科分层。                                   | 低。只建议 sanity check。    |
| C4 评  | [MathTutorBench](https://github.com/eth-lre/mathtutorbench)         | 数学过程反馈、错因定位、脚手架   | 与 SAS-Bench 的步骤评分、EduBench/TutorBench 的反馈质量有交集；但数学过程反馈有专项价值。 | 先抽样 100-300 条。                 | Rubric/reward model/LLM judge。                        | 中到高。适合做“数学反馈专项”。       |
| C5 安全 | CASTLE                                                              | 个性化教育安全、学生画像适配    | 任务重要，但当前未确认稳定公开数据/代码；不满足 P0 可复现要求。                           | 等数据公开后再定。                      | Risk Sensitivity、Emotional Empathy、Student Alignment。 | 中到高。开放式安全 judge。       |


## P2：暂缓或只引用公开结果


| 大类    | Benchmark     | 当前处理                  | 理由                                      |
| ----- | ------------- | --------------------- | --------------------------------------- |
| C1 通用 | MMLU-Pro      | 引用公开 leaderboard      | 通用学科推理已有榜单，全量重跑教育增量有限。                  |
| C1 通用 | GSM8K         | 引用公开结果                | 基础数学已高度饱和，且训练污染风险高。                     |
| C1 通用 | AGIEval       | 引用/暂缓                 | 与 MMLU-Pro、C-Eval 同属考试选择题/标准化考试能力，交集较大。 |
| C1 通用 | OlympiadBench | 二阶段高阶推理专项             | 高阶数学/物理有价值，但长推理和 judge 成本高。             |
| C1 通用 | MathVista     | 引用公开 leaderboard      | 多模态数学重要，但已有公开榜单，且不是教育专项。                |
| C1 通用 | Video-MME     | 引用公开 leaderboard      | 视频成本高，且当前不是课堂视频专项。                      |
| C1 通用 | LiveCodeBench | 引用公开 leaderboard      | 代码执行评测成熟，但不是教育 re-benchmark 第一优先。       |
| C3 学  | ASSISTments   | 暂缓到 EDM/KT 专项         | 更像知识追踪/认知诊断模型评测，需要训练传统或序列模型。            |
| C3 学  | EdNet         | 暂缓到 EDM/KT 专项         | 数据规模巨大，预处理和训练成本高。                       |
| C3 学  | MCD           | 暂缓到课堂对话专项             | 课堂过程建模重要，但与当前 LLM API 评测不完全同构。          |
| C4 评  | ASAP-SAS      | legacy baseline，不第一轮跑 | 与 SAS-Bench 同为短答案评分，SAS-Bench 更现代且细粒度。  |


## 第一轮推荐最小组合

如果我们只做一轮“小而精”的教育 re-benchmark，建议先跑：


| 顺序  | Benchmark           | 目的               | 产出                                |
| --- | ------------------- | ---------------- | --------------------------------- |
| 1   | SAS-Bench           | 建立“评”的核心评分/诊断画像  | 分模型 QWK/CCS/ECS、分学科/题型分析、错误诊断短板。  |
| 2   | Pedagogy Benchmark  | 快速补齐“教”的教师专业知识底座 | 分教学子域 accuracy，判断模型是否懂教学法。        |
| 3   | EduBench            | 测开放式教学设计和个性化支持   | rubric 维度分析，形成“会不会教/会不会支持学生”的判断。  |
| 4   | TutorBench          | 评估“师生互动”的苏格拉底教学流 | 考察模型在对话中引导而非直接给答案的能力，评估多轮启发的效果。   |
| 5   | EduVisBench         | 评估“多模态”教育图表/板书理解 | 评估模型读取几何图形、化学结构式、统计图表等非文本教育资源的能力。 |
| 6   | EduGuard-Bench      | 测教育安全底线          | 安全失败率、教师角色一致性、拒答质量。               |
| 7   | ASAP-AES / ASAP 2.0 | 补齐作文评分           | 长文本评分一致性，和 SAS-Bench 短答评分形成互补。    |


基本覆盖：


| 能力面  | 覆盖情况                                                     |
| ---- | -------------------------------------------------------- |
| 教    | Pedagogy Benchmark + EduBench                            |
| 学    | EduBench PLS/ES/PCC 子任务                                  |
| 评    | SAS-Bench + ASAP-AES/ASAP 2.0                            |
| 安全   | EduGuard-Bench                                           |
| 通用底座 | 引用 MMLU-Pro、C-Eval、MathVista、LiveCodeBench 等公开榜单，不重复消耗成本 |


## 待讨论问题

1. C1 是否完全不跑，只引用榜单？还是保留 C-Eval 小样本作为中文本土 sanity check？
2. ASAP-AES 是否第一轮就跑，还是等 SAS-Bench 分析稳定后再补作文评分？
3. EduBench 的子任务抽样应该覆盖哪些场景：Teaching Material Generation、Error Correction、Personalized Learning Support、Emotional Support 是否足够？
4. EduGuard-Bench 是否需要人工复核一部分高风险样例，还是先只用 LLM judge？
5. P1 的 EduVisBench 是否值得提前跑小样本，用来体现教学可视化这一项差异化能力？

