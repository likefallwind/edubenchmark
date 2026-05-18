# AI 教育 Benchmark v1

生成日期：2026-05-18

这个文件是根目录入口，按 8 个一级尺度、D01-D24 原子能力、细粒度评价标准组织。每道评测题的完整题干、评分方式、题目来源文件和行/键位置在根目录 JSON 文件中：`ai_edu_benchmark_v1_questions.json`。

## 文件入口

| 文件 | 用途 |
| --- | --- |
| AI_EDU_BENCHMARK_V1.md | 根目录可读总览：尺度、原子能力、评价标准、覆盖状态。 |
| ai_edu_benchmark_v1_questions.json | 题目索引 JSON：每道题的题干、评分方式、source_file、source_row_or_key。 |
| AI_EDU_BENCHMARK_V1.html | 同内容 HTML，方便浏览。 |
| data/benchmark_v1_2026-05-18/items.jsonl | JSONL 明细：每行一道题/任务样本。 |
| data/benchmark_v1_2026-05-18/capability_criteria.jsonl | JSONL 明细：每行一个评价标准。 |
| data/benchmark_v1_2026-05-18/source_manifest.jsonl | JSONL 明细：每行一个来源/访问状态。 |

## 总览

| 项目 | 数量 |
| --- | --- |
| 一级尺度 | 8 |
| 原子能力 | 24 |
| 评价标准 | 84 |
| 评测题/任务样本 | 840 |
| 采样来源文件 | 29 |
| 含 proxy/gap 的评价标准 | 27 |

## 一级尺度

| 尺度 ID | 尺度名称 | 包含原子能力 |
| --- | --- | --- |
| S1 | 学科知识与解题正确性 | D01 通用学科知识与选择题答题；D02 中文本土知识与 K12 学科体系；D03 标准化考试与资格考试推理；D04 基础数学应用题；D08 代码生成与算法题解 |
| S2 | 复杂推理与过程正确性 | D05 高阶数学与竞赛推理 |
| S3 | 教学诊断与辅导策略 | D09 编程教育问答与代码诊断；D12 学生错误定位与纠错反馈；D13 苏格拉底式引导与脚手架；D14 教学法知识与教学设计 |
| S4 | 反馈、批改与评价 | D10 作文自动评分；D11 短答案和分步评分 |
| S5 | 个性化、学情与学习路径 | D15 学习规划、个性化与学情分析；D16 知识追踪与答题预测；D17 认知诊断与知识点掌握；D18 教育资源检索、推荐与学习路径 |
| S6 | 多模态教学理解与生成 | D06 几何视觉、图表和多模态数学；D07 科学实验、视频和长时序理解；D20 课堂视觉行为与参与度识别；D22 教学可视化生成；D23 交互式科学演示生成 |
| S7 | 教育安全、伦理与角色边界 | D21 教育安全、合规与角色扮演 |
| S8 | 真实教育效果与工作流价值 | D19 课堂话语和教师行为分析；D24 教育垂类系统端到端能力 |

## 原子能力与评价标准

### D01 通用学科知识与选择题答题

- 一级尺度：S1 学科知识与解题正确性
- 评测题数量：30
- JSON 查询方式：在 `ai_edu_benchmark_v1_questions.json` 中筛选 `dimension_id == "D01"`。

| 评价标准 ID | 评价标准 | 指标族 | 原生指标 | 推荐 Benchmark | 题目数 | 覆盖状态 |
| --- | --- | --- | --- | --- | --- | --- |
| D01-C01 | 总体正确率/平均分 | accuracy_or_exact_match | MMLU accuracy/average, CMMLU average, C-EVAL average, E-EVAL average | MMLU, CMMLU, C-EVAL, E-EVAL | 10 | sampled_10_local_items |
| D01-C02 | 学科切片正确率 | accuracy_or_exact_match | STEM/Humanities/Social Science/Other, subject-level score, C-Eval Hard | MMLU, CMMLU, C-EVAL, E-EVAL, GaokaoBench | 10 | sampled_10_local_items |
| D01-C03 | prompt 方式敏感性 | accuracy_or_exact_match | zero-shot, five-shot, CoT, few-shot CoT | CMMLU, C-EVAL, AGIEval, E-EVAL | 10 | sampled_10_local_items |

### D02 中文本土知识与 K12 学科体系

- 一级尺度：S1 学科知识与解题正确性
- 评测题数量：30；含 proxy/gap
- JSON 查询方式：在 `ai_edu_benchmark_v1_questions.json` 中筛选 `dimension_id == "D02"`。

| 评价标准 ID | 评价标准 | 指标族 | 原生指标 | 推荐 Benchmark | 题目数 | 覆盖状态 |
| --- | --- | --- | --- | --- | --- | --- |
| D02-C01 | 中文 K12 学科正确率 | accuracy_or_exact_match | E-EVAL average, GaokaoBench objective overall, K12Vista direct overall | E-EVAL, GaokaoBench, K12Vista | 10 | sampled_10_local_items |
| D02-C02 | 中国本土知识正确率 | accuracy_or_exact_match | CMMLU China-specific, C-EVAL subject categories | CMMLU, C-EVAL | 10 | sampled_10_local_items |
| D02-C03 | 过程正确性 | accuracy_or_exact_match | K12Vista Step-by-Step overall, process correctness, hallucination/logical contradiction tags | K12Vista | 10 | sampled_10_proxy_items_coverage_gap |

### D03 标准化考试与资格考试推理

- 一级尺度：S1 学科知识与解题正确性
- 评测题数量：30
- JSON 查询方式：在 `ai_edu_benchmark_v1_questions.json` 中筛选 `dimension_id == "D03"`。

| 评价标准 ID | 评价标准 | 指标族 | 原生指标 | 推荐 Benchmark | 题目数 | 覆盖状态 |
| --- | --- | --- | --- | --- | --- | --- |
| D03-C01 | 考试题正确率 | accuracy_or_exact_match | AGIEval zero-shot/few-shot accuracy, GaokaoBench objective score | AGIEval, GaokaoBench, C-EVAL | 10 | sampled_10_local_items |
| D03-C02 | 主观题评分 | accuracy_or_exact_match | GaokaoBench subjective overall, subjective subject score | GaokaoBench | 10 | sampled_10_local_items |
| D03-C03 | 考试类型切片 | accuracy_or_exact_match | SAT, LSAT, Gaokao, Civil Service Exam, Law/Math/Reading subsets | AGIEval, C-EVAL | 10 | sampled_10_local_items |

### D04 基础数学应用题

- 一级尺度：S1 学科知识与解题正确性
- 评测题数量：30
- JSON 查询方式：在 `ai_edu_benchmark_v1_questions.json` 中筛选 `dimension_id == "D04"`。

| 评价标准 ID | 评价标准 | 指标族 | 原生指标 | 推荐 Benchmark | 题目数 | 覆盖状态 |
| --- | --- | --- | --- | --- | --- | --- |
| D04-C01 | 最终答案正确率 | accuracy_or_exact_match | GSM8K exact match, Math23K answer accuracy, Ape210K accuracy | GSM8K, Math23K, Ape210K | 10 | sampled_10_local_items |
| D04-C02 | 表达式/方程生成正确率 | accuracy_or_exact_match | equation accuracy, template accuracy, answer accuracy | Math23K, Ape210K | 10 | sampled_10_local_items |
| D04-C03 | 推理链设置效果 | accuracy_or_exact_match | CoT accuracy, verifier reranking result, self-consistency | GSM8K | 10 | sampled_10_local_items |

### D05 高阶数学与竞赛推理

- 一级尺度：S2 复杂推理与过程正确性
- 评测题数量：40；含 proxy/gap
- JSON 查询方式：在 `ai_edu_benchmark_v1_questions.json` 中筛选 `dimension_id == "D05"`。

| 评价标准 ID | 评价标准 | 指标族 | 原生指标 | 推荐 Benchmark | 题目数 | 覆盖状态 |
| --- | --- | --- | --- | --- | --- | --- |
| D05-C01 | 最终答案正确率 | accuracy_or_exact_match | MATH accuracy, MATH-500 accuracy, OlymMATH accuracy, OlympiadBench accuracy | MATH, MATH-500, OlymMATH, OlympiadBench | 10 | sampled_10_local_items |
| D05-C02 | Hard 子集正确率 | accuracy_or_exact_match | OlymMATH-HARD, competition subset, Olympiad-level subset | OlymMATH, OlympiadBench | 10 | sampled_10_local_items |
| D05-C03 | 稳定性/多次采样收益 | programmatic_test | Pass@k, Cons@k, self-consistency | OlymMATH, MATH | 10 | sampled_10_local_items |
| D05-C04 | 证明/过程可评性 | accuracy_or_exact_match | theorem proving subset, process-level correctness | OlympiadBench, IMO-style benchmarks | 10 | sampled_10_proxy_items_coverage_gap |

### D06 几何视觉、图表和多模态数学

- 一级尺度：S6 多模态教学理解与生成
- 评测题数量：50；含 proxy/gap
- JSON 查询方式：在 `ai_edu_benchmark_v1_questions.json` 中筛选 `dimension_id == "D06"`。

| 评价标准 ID | 评价标准 | 指标族 | 原生指标 | 推荐 Benchmark | 题目数 | 覆盖状态 |
| --- | --- | --- | --- | --- | --- | --- |
| D06-C01 | 多模态数学总体正确率 | accuracy_or_exact_match | MathVista test/testmini accuracy, CMMU fill-in/choice accuracy, K12Vista direct overall | MathVista, CMMU, K12Vista | 10 | sampled_10_local_items |
| D06-C02 | 视觉上下文切片 | multimodal | MathVista visual context types, chart/table/geometry/figure QA | MathVista, ChartQA | 10 | sampled_10_local_items |
| D06-C03 | 数学推理类型切片 | accuracy_or_exact_match | algebraic, arithmetic, geometric, logical, numeric, scientific, statistical | MathVista | 10 | sampled_10_local_items |
| D06-C04 | 视觉关键点识别 | multimodal | ME2 Visual Keypoint Identification accuracy | ME2 | 10 | sampled_10_proxy_items_coverage_gap |
| D06-C05 | 基于关键点的讲解质量 | accuracy_or_exact_match | ME2 correctness, ME2 fidelity, ME2 referencing score | ME2 | 10 | sampled_10_proxy_items_coverage_gap |

### D07 科学实验、视频和长时序理解

- 一级尺度：S6 多模态教学理解与生成
- 评测题数量：40；含 proxy/gap
- JSON 查询方式：在 `ai_edu_benchmark_v1_questions.json` 中筛选 `dimension_id == "D07"`。

| 评价标准 ID | 评价标准 | 指标族 | 原生指标 | 推荐 Benchmark | 题目数 | 覆盖状态 |
| --- | --- | --- | --- | --- | --- | --- |
| D07-C01 | 科学视频总体正确率 | multimodal | SciVideoBench overall accuracy | SciVideoBench | 10 | sampled_10_proxy_items_coverage_gap |
| D07-C02 | 学科切片正确率 | accuracy_or_exact_match | Physics, Chemistry, Biology, Medicine | SciVideoBench | 10 | sampled_10_proxy_items_coverage_gap |
| D07-C03 | 推理类型切片 | accuracy_or_exact_match | Conceptual, Hypothetical, Quantitative | SciVideoBench | 10 | sampled_10_proxy_items_coverage_gap |
| D07-C04 | 视觉 grounding 依赖 | multimodal | vision-blind baseline, with-video vs no-video accuracy | SciVideoBench | 10 | sampled_10_proxy_items_coverage_gap |

### D08 代码生成与算法题解

- 一级尺度：S1 学科知识与解题正确性
- 评测题数量：30
- JSON 查询方式：在 `ai_edu_benchmark_v1_questions.json` 中筛选 `dimension_id == "D08"`。

| 评价标准 ID | 评价标准 | 指标族 | 原生指标 | 推荐 Benchmark | 题目数 | 覆盖状态 |
| --- | --- | --- | --- | --- | --- | --- |
| D08-C01 | 功能正确率 | programmatic_test | HumanEval pass@1, MBPP accuracy/pass@1, APPS test pass rate | HumanEval, MBPP, APPS | 10 | sampled_10_local_items |
| D08-C02 | 采样收益 | programmatic_test | pass@k, pass@10, pass@100 | HumanEval, APPS | 10 | sampled_10_local_items |
| D08-C03 | 题目难度切片 | accuracy_or_exact_match | introductory, interview, competition, difficulty tags | APPS, LeetCode-style datasets | 10 | sampled_10_local_items |

### D09 编程教育问答与代码诊断

- 一级尺度：S3 教学诊断与辅导策略
- 评测题数量：30
- JSON 查询方式：在 `ai_edu_benchmark_v1_questions.json` 中筛选 `dimension_id == "D09"`。

| 评价标准 ID | 评价标准 | 指标族 | 原生指标 | 推荐 Benchmark | 题目数 | 覆盖状态 |
| --- | --- | --- | --- | --- | --- | --- |
| D09-C01 | 学生问题类型识别 | accuracy_or_exact_match | CS1QA question type, intent/category classification | CS1QA, QACP | 10 | sampled_10_local_items |
| D09-C02 | 相关代码行定位 | accuracy_or_exact_match | CS1QA related code line annotation, bug localization | CS1QA, Codecademy Dataset | 10 | sampled_10_local_items |
| D09-C03 | 教学反馈质量 | tutoring_rubric | hint usefulness, concept explanation quality, non-spoiler feedback | CS1QA, QACP, self-built required | 10 | sampled_10_local_items |

### D10 作文自动评分

- 一级尺度：S4 反馈、批改与评价
- 评测题数量：30；含 proxy/gap
- JSON 查询方式：在 `ai_edu_benchmark_v1_questions.json` 中筛选 `dimension_id == "D10"`。

| 评价标准 ID | 评价标准 | 指标族 | 原生指标 | 推荐 Benchmark | 题目数 | 覆盖状态 |
| --- | --- | --- | --- | --- | --- | --- |
| D10-C01 | 总分一致性 | rubric_or_agreement | QWK, holistic score agreement | ASAP-AES, EssayJudge, ELLIPSE | 10 | sampled_10_local_items |
| D10-C02 | 多维 trait 一致性 | rubric_or_agreement | vocabulary, sentence, argument clarity, coherence, syntax trait QWK | EssayJudge, ELLIPSE | 10 | sampled_10_proxy_items_coverage_gap |
| D10-C03 | 跨 prompt 泛化和公平性 | rubric_or_agreement | cross-prompt QWK, length bias, group fairness slice | ASAP-AES, ELLIPSE, self-built required | 10 | sampled_10_proxy_items_coverage_gap |

### D11 短答案和分步评分

- 一级尺度：S4 反馈、批改与评价
- 评测题数量：40；含 proxy/gap
- JSON 查询方式：在 `ai_edu_benchmark_v1_questions.json` 中筛选 `dimension_id == "D11"`。

| 评价标准 ID | 评价标准 | 指标族 | 原生指标 | 推荐 Benchmark | 题目数 | 覆盖状态 |
| --- | --- | --- | --- | --- | --- | --- |
| D11-C01 | 总体评分一致性 | rubric_or_agreement | QWK, overall score agreement | ASAP-SAS, SAS-Bench | 10 | sampled_10_local_items |
| D11-C02 | 分步评分一致性 | rubric_or_agreement | CCS: Comprehensive Consistency Score | SAS-Bench | 10 | sampled_10_proxy_items_coverage_gap |
| D11-C03 | 错误原因一致性 | rubric_or_agreement | ECS: Errors Consistency Score | SAS-Bench | 10 | sampled_10_proxy_items_coverage_gap |
| D11-C04 | 局部分析指标 | rubric_or_agreement | F1 score, subject/question-type slice | SAS-Bench | 10 | sampled_10_proxy_items_coverage_gap |

### D12 学生错误定位与纠错反馈

- 一级尺度：S3 教学诊断与辅导策略
- 评测题数量：40
- JSON 查询方式：在 `ai_edu_benchmark_v1_questions.json` 中筛选 `dimension_id == "D12"`。

| 评价标准 ID | 评价标准 | 指标族 | 原生指标 | 推荐 Benchmark | 题目数 | 覆盖状态 |
| --- | --- | --- | --- | --- | --- | --- |
| D12-C01 | 错误位置定位 | tutoring_rubric | MathTutorBench Mistake Location | MathTutorBench, Bridge | 10 | sampled_10_local_items |
| D12-C02 | 纠错准确性 | tutoring_rubric | MathTutorBench Mistake Correction | MathTutorBench, SAS-Bench | 10 | sampled_10_local_items |
| D12-C03 | 学生答案正确性判断 | tutoring_rubric | MathTutorBench Solution Correctness | MathTutorBench | 10 | sampled_10_local_items |
| D12-C04 | 错因解释质量 | tutoring_rubric | error cause, misconception diagnosis, expert tutor decision | Bridge, SAS-Bench, MathDial | 10 | sampled_10_local_items |

### D13 苏格拉底式引导与脚手架

- 一级尺度：S3 教学诊断与辅导策略
- 评测题数量：40
- JSON 查询方式：在 `ai_edu_benchmark_v1_questions.json` 中筛选 `dimension_id == "D13"`。

| 评价标准 ID | 评价标准 | 指标族 | 原生指标 | 推荐 Benchmark | 题目数 | 覆盖状态 |
| --- | --- | --- | --- | --- | --- | --- |
| D13-C01 | 苏格拉底式提问 | tutoring_rubric | MathTutorBench Socratic Questioning | MathTutorBench, MathDial | 10 | sampled_10_local_items |
| D13-C02 | 脚手架胜率 | tutoring_rubric | Scaffolding Win Rate, Scaffolding (Hard) | MathTutorBench | 10 | sampled_10_local_items |
| D13-C03 | 教学指令遵循 | accuracy_or_exact_match | Pedagogy IF Win Rate, Pedagogy IF (Hard) | MathTutorBench | 10 | sampled_10_local_items |
| D13-C04 | 下一步教学决策 | tutoring_rubric | expert tutor decision alignment, hint generation quality | Bridge, TutorBench, SocraticLM | 10 | sampled_10_local_items |

### D14 教学法知识与教学设计

- 一级尺度：S3 教学诊断与辅导策略
- 评测题数量：30
- JSON 查询方式：在 `ai_edu_benchmark_v1_questions.json` 中筛选 `dimension_id == "D14"`。

| 评价标准 ID | 评价标准 | 指标族 | 原生指标 | 推荐 Benchmark | 题目数 | 覆盖状态 |
| --- | --- | --- | --- | --- | --- | --- |
| D14-C01 | 教学法知识正确率 | accuracy_or_exact_match | CDPK, pedagogical knowledge score | Pedagogy Benchmark | 10 | sampled_10_local_items |
| D14-C02 | 特殊教育能力 | accuracy_or_exact_match | SEND | Pedagogy Benchmark | 10 | sampled_10_local_items |
| D14-C03 | 教学设计质量 | accuracy_or_exact_match | lesson planning, instructional design, rubric-based education score | EduBench, EduEval, OmniEduBench | 10 | sampled_10_local_items |

### D15 学习规划、个性化与学情分析

- 一级尺度：S5 个性化、学情与学习路径
- 评测题数量：30；含 proxy/gap
- JSON 查询方式：在 `ai_edu_benchmark_v1_questions.json` 中筛选 `dimension_id == "D15"`。

| 评价标准 ID | 评价标准 | 指标族 | 原生指标 | 推荐 Benchmark | 题目数 | 覆盖状态 |
| --- | --- | --- | --- | --- | --- | --- |
| D15-C01 | 学习规划质量 | accuracy_or_exact_match | learning planning, study plan rubric score | EduBench, EduEval | 10 | sampled_10_local_items |
| D15-C02 | 个性化适配 | accuracy_or_exact_match | personalization, student profile alignment | EduBench, CASTLE, self-built required | 10 | sampled_10_local_items |
| D15-C03 | 学情预测/推荐效果 | prediction_or_ranking | KT AUC, ACC, next response prediction, recommendation ranking | ASSISTments, EdNet, Junyi, MOOCCube | 10 | sampled_10_proxy_items_coverage_gap |

### D16 知识追踪与答题预测

- 一级尺度：S5 个性化、学情与学习路径
- 评测题数量：30
- JSON 查询方式：在 `ai_edu_benchmark_v1_questions.json` 中筛选 `dimension_id == "D16"`。

| 评价标准 ID | 评价标准 | 指标族 | 原生指标 | 推荐 Benchmark | 题目数 | 覆盖状态 |
| --- | --- | --- | --- | --- | --- | --- |
| D16-C01 | 下一题答对概率预测 | prediction_or_ranking | AUC, ACC, RMSE | ASSISTments, KDD Cup 2010, EdNet, Junyi, STATICS2011 | 10 | sampled_10_local_items |
| D16-C02 | 长序列建模能力 | prediction_or_ranking | sequence-level AUC, long interaction split | EdNet, KDD Cup 2010 | 10 | sampled_10_local_items |
| D16-C03 | 跨数据/跨知识点泛化 | prediction_or_ranking | cross-dataset split, concept split, student split | ASSISTments, Junyi, FoundationalAssist | 10 | sampled_10_local_items |

### D17 认知诊断与知识点掌握

- 一级尺度：S5 个性化、学情与学习路径
- 评测题数量：30；含 proxy/gap
- JSON 查询方式：在 `ai_edu_benchmark_v1_questions.json` 中筛选 `dimension_id == "D17"`。

| 评价标准 ID | 评价标准 | 指标族 | 原生指标 | 推荐 Benchmark | 题目数 | 覆盖状态 |
| --- | --- | --- | --- | --- | --- | --- |
| D17-C01 | 知识点掌握估计 | accuracy_or_exact_match | concept mastery, knowledge component mastery | ASSISTments, PTADisc, Junyi | 10 | sampled_10_proxy_items_coverage_gap |
| D17-C02 | 诊断解释质量 | accuracy_or_exact_match | diagnostic explanation, misconception explanation | FoundationalAssist, self-built required | 10 | sampled_10_proxy_items_coverage_gap |
| D17-C03 | 概念标签预测/映射 | accuracy_or_exact_match | concept label prediction, KC tagging | PTADisc, ASSISTments | 10 | sampled_10_proxy_items_coverage_gap |

### D18 教育资源检索、推荐与学习路径

- 一级尺度：S5 个性化、学情与学习路径
- 评测题数量：30；含 proxy/gap
- JSON 查询方式：在 `ai_edu_benchmark_v1_questions.json` 中筛选 `dimension_id == "D18"`。

| 评价标准 ID | 评价标准 | 指标族 | 原生指标 | 推荐 Benchmark | 题目数 | 覆盖状态 |
| --- | --- | --- | --- | --- | --- | --- |
| D18-C01 | 资源检索相关性 | prediction_or_ranking | Recall@k, MRR, NDCG, retrieval relevance | MOOCCube, TutorialBank, LectureBank | 10 | sampled_10_proxy_items_coverage_gap |
| D18-C02 | 学习路径连贯性 | accuracy_or_exact_match | prerequisite consistency, path coherence, concept graph alignment | MOOCCube, SIGHT, self-built required | 10 | sampled_10_proxy_items_coverage_gap |
| D18-C03 | 教育语料质量 | accuracy_or_exact_match | educational quality score, filter score | FineWeb-Edu, Chinese FineWeb Edu | 10 | sampled_10_proxy_items_coverage_gap |

### D19 课堂话语和教师行为分析

- 一级尺度：S8 真实教育效果与工作流价值
- 评测题数量：30
- JSON 查询方式：在 `ai_edu_benchmark_v1_questions.json` 中筛选 `dimension_id == "D19"`。

| 评价标准 ID | 评价标准 | 指标族 | 原生指标 | 推荐 Benchmark | 题目数 | 覆盖状态 |
| --- | --- | --- | --- | --- | --- | --- |
| D19-C01 | 课堂话语动作分类 | accuracy_or_exact_match | Talk Moves labels, instructional moves classification | TalkMoves, NCTE Transcripts | 10 | sampled_10_local_items |
| D19-C02 | 课堂反馈建议质量 | tutoring_rubric | teacher feedback usefulness, actionability, pedagogical alignment | NCTE Transcripts, TIMSS Video Study, self-built required | 10 | sampled_10_local_items |
| D19-C03 | 跨课堂泛化 | accuracy_or_exact_match | cross-teacher, cross-school, cross-country split | TIMSS Video Study, TalkMoves | 10 | sampled_10_local_items |

### D20 课堂视觉行为与参与度识别

- 一级尺度：S6 多模态教学理解与生成
- 评测题数量：30；含 proxy/gap
- JSON 查询方式：在 `ai_edu_benchmark_v1_questions.json` 中筛选 `dimension_id == "D20"`。

| 评价标准 ID | 评价标准 | 指标族 | 原生指标 | 推荐 Benchmark | 题目数 | 覆盖状态 |
| --- | --- | --- | --- | --- | --- | --- |
| D20-C01 | 学生行为识别 | accuracy_or_exact_match | behavior classification accuracy, action recognition | SCB-Dataset, ARIC | 10 | sampled_10_proxy_items_coverage_gap |
| D20-C02 | 参与度/兴趣度预测 | accuracy_or_exact_match | engagement score, interest level, participation label | IntrEx, ARIC | 10 | sampled_10_proxy_items_coverage_gap |
| D20-C03 | 多模态同步理解 | multimodal | audio-video-text alignment, classroom event grounding | ARIC, classroom video resources | 10 | sampled_10_proxy_items_coverage_gap |

### D21 教育安全、合规与角色扮演

- 一级尺度：S7 教育安全、伦理与角色边界
- 评测题数量：40
- JSON 查询方式：在 `ai_edu_benchmark_v1_questions.json` 中筛选 `dimension_id == "D21"`。

| 评价标准 ID | 评价标准 | 指标族 | 原生指标 | 推荐 Benchmark | 题目数 | 覆盖状态 |
| --- | --- | --- | --- | --- | --- | --- |
| D21-C01 | 角色扮演专业度 | safety | RFS, role-following score | EduGuard-Bench | 10 | sampled_10_local_items |
| D21-C02 | 攻击成功率/安全失败率 | safety | ASR | EduGuard-Bench, YouthSafe | 10 | sampled_10_local_items |
| D21-C03 | 青少年风险识别与转介 | accuracy_or_exact_match | youth risk category, safeguard success, crisis escalation quality | YouthSafe, CASTLE, self-built required | 10 | sampled_10_local_items |
| D21-C04 | 学生个体差异安全 | safety | student-specific safety, empathy, developmental appropriateness | CASTLE | 10 | sampled_10_local_items |

### D22 教学可视化生成

- 一级尺度：S6 多模态教学理解与生成
- 评测题数量：50
- JSON 查询方式：在 `ai_edu_benchmark_v1_questions.json` 中筛选 `dimension_id == "D22"`。

| 评价标准 ID | 评价标准 | 指标族 | 原生指标 | 推荐 Benchmark | 题目数 | 覆盖状态 |
| --- | --- | --- | --- | --- | --- | --- |
| D22-C01 | 逻辑序列 | accuracy_or_exact_match | logic sequence | EduVisBench, VisualEDU | 10 | sampled_10_local_items |
| D22-C02 | 结构丰富度 | accuracy_or_exact_match | structural richness | EduVisBench | 10 | sampled_10_local_items |
| D22-C03 | 语义对齐 | accuracy_or_exact_match | semantic alignment | EduVisBench, ME2 | 10 | sampled_10_local_items |
| D22-C04 | 讲解引导 | accuracy_or_exact_match | explanation guidance | EduVisBench, VisualEDU | 10 | sampled_10_local_items |
| D22-C05 | 交互参与度 | accuracy_or_exact_match | interaction engagement | EduVisBench, InteractScience | 10 | sampled_10_local_items |

### D23 交互式科学演示生成

- 一级尺度：S6 多模态教学理解与生成
- 评测题数量：40
- JSON 查询方式：在 `ai_edu_benchmark_v1_questions.json` 中筛选 `dimension_id == "D23"`。

| 评价标准 ID | 评价标准 | 指标族 | 原生指标 | 推荐 Benchmark | 题目数 | 覆盖状态 |
| --- | --- | --- | --- | --- | --- | --- |
| D23-C01 | 程序功能测试通过率 | programmatic_test | PFT Overall, PFT Average, PFT Perfect | InteractScience | 10 | sampled_10_local_items |
| D23-C02 | 动作成功率 | accuracy_or_exact_match | VQT Action | InteractScience | 10 | sampled_10_local_items |
| D23-C03 | 视觉相似度 | multimodal | VQT CLIP | InteractScience | 10 | sampled_10_local_items |
| D23-C04 | 语义正确性 | accuracy_or_exact_match | VQT VLM-judge | InteractScience | 10 | sampled_10_local_items |

### D24 教育垂类系统端到端能力

- 一级尺度：S8 真实教育效果与工作流价值
- 评测题数量：40；含 proxy/gap
- JSON 查询方式：在 `ai_edu_benchmark_v1_questions.json` 中筛选 `dimension_id == "D24"`。

| 评价标准 ID | 评价标准 | 指标族 | 原生指标 | 推荐 Benchmark | 题目数 | 覆盖状态 |
| --- | --- | --- | --- | --- | --- | --- |
| D24-C01 | 外部 benchmark 能力 | tutoring_rubric | MathTutorBench scores, EduBench scores, TutorBench scores | LearnLM, InnoSpark, 九章, 子曰, 星火教育, CheggMate | 10 | sampled_10_proxy_items_coverage_gap |
| D24-C02 | 工作流完成度 | accuracy_or_exact_match | task completion, workflow success, teacher adoption | self-built required | 10 | sampled_10_proxy_items_coverage_gap |
| D24-C03 | 真实学习效果 | accuracy_or_exact_match | learning gain, delayed retention, transfer, A/B outcome | self-built required | 10 | sampled_10_proxy_items_coverage_gap |
| D24-C04 | 教师采纳与修改量 | accuracy_or_exact_match | teacher acceptance rate, edit distance, override rate | self-built required | 10 | sampled_10_proxy_items_coverage_gap |

## 题目 JSON 结构

`ai_edu_benchmark_v1_questions.json` 是一个 JSON object，核心字段如下：

| 字段 | 说明 |
| --- | --- |
| metadata | 生成日期、题目数、评价标准数、关联文件路径。 |
| questions | 题目数组。每个元素对应一条评测题或资源构造任务。 |
| questions[].item_id | 题目唯一 ID。 |
| questions[].dimension_id / criterion_id | 对应原子能力和评价标准。 |
| questions[].question | 题干或任务构造说明。 |
| questions[].source_file | 本地来源文件路径。 |
| questions[].source_row_or_key | 来源文件中的行号、key、ID 或构造键。 |
| questions[].item_record_file / item_record_line | 该题在 JSONL 明细中的位置。 |
| questions[].answer_or_rubric / scoring_method | 标准答案、评分规则或 rubric。 |

## 覆盖说明

覆盖状态为 `sampled_10_local_items` 的标准有 10 条直接本地样本。覆盖状态包含 `coverage_gap` 的标准虽然也保留了 10 条本地 proxy/resource-construction 样本，但还缺少对应原生 benchmark 的完整标签、视频/图像资源、授权数据或产品级日志，下一版需要补齐。

完整可读报告也保留在：`reports/2026-05-18/ai_edu_benchmark_v1_spec.md` 和 `reports/2026-05-18/ai_edu_benchmark_v1_spec.html`。
