# Exhaustive Extraction Log

生成日期：2026-05-13

## 总览

- benchmarks.jsonl：78 条 benchmark/resource 记录。
- metrics.jsonl：165 条 benchmark-native 指标记录。
- results.jsonl：1616 条结果记录，其中模型分数 1569 条，no_unified_leaderboard 47 条。
- 旧 `data/model_dimension_performance_2026-05-12.json` 是代表性抽取，只保留为摘要参考；本目录作为全量本地结构化结果库。
- 本轮未把多列指标压成 average；Markdown 表格中的每个模型 × 指标单元格单独保留。
- 在线补充结果来自 `edu_benchmark_survey_supplement_2026-05-11.md` 中已核验描述；本脚本未重新抓取外部网页。
- 2026-05-13 额外人工抽查了 MathVista 项目页、OlymMATH、MathTutorBench、SAS-Bench 官方仓库；只确认来源与已记录结果，不从网页推断或补编新分数。

## 表格抽取状态

| Source | Section | Benchmark | Markdown rows | Result records | Status | Notes |
|---|---|---|---:|---:|---|---|
| edu_benchmark_survey.md | MMLU 原论文结果 | MMLU | 9 | 45 | extracted |  |
| edu_benchmark_survey.md | CMMLU 五样本结果 | CMMLU | 21 | 126 | extracted |  |
| edu_benchmark_survey.md | C-EVAL 全量与 Hard 子集 | C-EVAL | 11 | 66 | extracted |  |
| edu_benchmark_survey.md | AGIEval 平均结果 | AGIEval | 6 | 24 | extracted |  |
| edu_benchmark_survey.md | GaokaoBench 总体结果 | GaokaoBench | 12 | 24 | extracted |  |
| edu_benchmark_survey.md | E-EVAL Prompt 设置对比 | E-EVAL | 15 | 45 | extracted |  |
| edu_benchmark_survey.md | OlympiadBench 关键结果 | OlympiadBench | 9 | 27 | extracted |  |
| edu_benchmark_survey.md | CMMU 测试集平均分 | CMMU | 10 | 10 | extracted |  |
| edu_benchmark_survey.md | ChartQA 结果 | ChartQA | 9 | 27 | extracted |  |
| edu_benchmark_survey.md | GSM8K 原论文读数 | GSM8K | 3 | 3 | extracted |  |
| edu_benchmark_survey.md | MATH 原论文结果 | MATH | 7 | 56 | extracted |  |
| edu_benchmark_survey.md | OlymMATH HARD 代表结果 | OlymMATH | 4 | 16 | extracted |  |
| edu_benchmark_survey.md | MathVista testmini 官方榜单 ALL 分数 | MathVista | 62 | 62 | extracted |  |
| edu_benchmark_survey.md | ME2 视觉关键点与讲解生成 | ME2 | 10 | 40 | extracted |  |
| edu_benchmark_survey.md | HumanEval 原论文结果 | HumanEval | 14 | 42 | extracted |  |
| edu_benchmark_survey.md | MBPP 原论文结果 | MBPP | 6 | 12 | extracted |  |
| edu_benchmark_survey.md | Pedagogy Benchmark 完整 CDPK 榜单 | Pedagogy Benchmark | 49 | 97 | extracted | 每个模型行按指标列展开；Pedagogy 双栏表按左右两组模型展开。 |
| edu_benchmark_survey.md | Pedagogy Benchmark 完整 SEND 榜单 | Pedagogy Benchmark | 48 | 95 | extracted | 每个模型行按指标列展开；Pedagogy 双栏表按左右两组模型展开。 |
| edu_benchmark_survey.md | MathTutorBench 全表 | MathTutorBench | 8 | 72 | extracted |  |
| edu_benchmark_survey.md | EduBench 人工与模型评测 | EduBench | 16 | 16 | extracted |  |
| edu_benchmark_survey.md | EduEval 汇总均分 | EduEval | 14 | 28 | extracted |  |
| edu_benchmark_survey.md | OmniEduBench 主表 | OmniEduBench | 11 | 22 | extracted |  |
| edu_benchmark_survey.md | EduGuard-Bench 代表结果 | EduGuard-Bench | 14 | 70 | extracted |  |
| edu_benchmark_survey.md | TutorBench 全表 | TutorBench | 15 | 45 | extracted |  |
| edu_benchmark_survey.md | EduVisBench 全表 | EduVisBench | 17 | 102 | extracted |  |
| edu_benchmark_survey.md | SciVideoBench 全模型 Overall | SciVideoBench | 59 | 59 | extracted |  |
| edu_benchmark_survey.md | K12Vista Direct 与 Step-by-Step Overall | K12Vista | 26 | 52 | extracted |  |
| edu_benchmark_survey.md | InteractScience PFT Overall | InteractScience | 16 | 16 | extracted |  |
| edu_benchmark_survey.md | EssayJudge QWK 全表 | EssayJudge | 19 | 190 | extracted |  |
| edu_benchmark_survey.md | SAS-Bench CCS/ECS 平均 | SAS-Bench | 16 | 32 | extracted |  |
| edu_benchmark_survey_supplement_2026-05-11.md | 一、旧模型结果的线上补充 / 可补充进原报告的代表性新结果 | multiple_benchmarks | 14 | 45 | supplement_representative_updates_extracted | 按补充文件中明确列出的模型-分数展开；不覆盖 survey 原始结果。 |
| edu_benchmark_survey.md | E. 无官方统一模型榜单的条目 | multiple_resources | 6 | 46 | no_unified_leaderboard_recorded | 每个条目保留 no_unified_leaderboard 结果记录，避免无榜单条目被省略。 |
| reports/2026-05-13/web_verified_updates_2026-05-13.md | 2026-05-13 web-verified emerging education benchmarks | ConvoLearn / PEBBLE | 2 | 4 | web_verified_emerging_resources_added | 补入 2026 检索发现但本地 survey 未覆盖的 tutor/教学过程类条目；ConvoLearn 保留来源页明示的人评分数，PEBBLE 保留为待发布评测协议。 |
| edu_benchmark_survey_supplement_2026-05-11.md | 1. 解题能力：通用学科与考试 | authority_table | 8 | 8 | authority_metadata_extracted | 权威性 表已写入 benchmarks.jsonl 的 authority_* 字段。 |
| edu_benchmark_survey_supplement_2026-05-11.md | 2. 解题能力：数学专项 | authority_table | 11 | 11 | authority_metadata_extracted | 权威性 表已写入 benchmarks.jsonl 的 authority_* 字段。 |
| edu_benchmark_survey_supplement_2026-05-11.md | 3. 解题能力：代码与编程教育 | authority_table | 6 | 7 | authority_metadata_extracted | 权威性 表已写入 benchmarks.jsonl 的 authority_* 字段。 |
| edu_benchmark_survey_supplement_2026-05-11.md | 4. 教学能力与教育多模态 | authority_table | 11 | 11 | authority_metadata_extracted | 权威性 表已写入 benchmarks.jsonl 的 authority_* 字段。 |
| edu_benchmark_survey_supplement_2026-05-11.md | 5. 知识追踪、认知诊断与学习路径 | authority_table | 10 | 10 | authority_metadata_extracted | 权威性 表已写入 benchmarks.jsonl 的 authority_* 字段。 |
| edu_benchmark_survey_supplement_2026-05-11.md | 6. 自动评分 | authority_table | 5 | 5 | authority_metadata_extracted | 权威性 表已写入 benchmarks.jsonl 的 authority_* 字段。 |
| edu_benchmark_survey_supplement_2026-05-11.md | 7. 教育问答与师生对话 | authority_table | 8 | 9 | authority_metadata_extracted | 权威性 表已写入 benchmarks.jsonl 的 authority_* 字段。 |
| edu_benchmark_survey_supplement_2026-05-11.md | 8. 课堂、课程资源与产品系统 | authority_table | 10 | 15 | authority_metadata_extracted | 资源价值 表已写入 benchmarks.jsonl 的 authority_* 字段。 |

## 已抽取模型结果覆盖

- AGIEval: 25 result records
- C-EVAL: 67 result records
- CMMLU: 133 result records
- CMMU: 10 result records
- ChartQA: 27 result records
- ConvoLearn: 3 result records
- E-EVAL: 45 result records
- EduBench: 16 result records
- EduEval: 28 result records
- EduGuard-Bench: 70 result records
- EduVisBench: 102 result records
- EssayJudge: 190 result records
- GSM8K: 8 result records
- GaokaoBench: 29 result records
- HumanEval: 42 result records
- InteractScience: 16 result records
- K12Vista: 52 result records
- MATH: 58 result records
- MATH-500: 1 result records
- MBPP: 12 result records
- ME2: 40 result records
- MMLU: 59 result records
- MathTutorBench: 72 result records
- MathVista: 65 result records
- OlymMATH: 16 result records
- OlympiadBench: 33 result records
- OmniEduBench: 22 result records
- Pedagogy Benchmark: 192 result records
- SAS-Bench: 32 result records
- SciVideoBench: 59 result records
- TutorBench: 45 result records

## 缺失/无榜单处理

- Adaptive Geography Practice: 类别：知识追踪/认知诊断。论文/README/数据卡未找到可直接引用的官方统一模型 leaderboard。
- Ape210K: 类别：数学数据资源。论文/README/数据卡未找到可直接引用的官方统一模型 leaderboard。
- APPS Dataset: 类别：教育资源。论文/README/数据卡未找到可直接引用的官方统一模型 leaderboard。
- ARIC: 类别：教育资源。论文/README/数据卡未找到可直接引用的官方统一模型 leaderboard。
- ASAP-AES: 类别：自动评分经典数据。论文/README/数据卡未找到可直接引用的官方统一模型 leaderboard。
- ASAP-SAS: 类别：自动评分经典数据。论文/README/数据卡未找到可直接引用的官方统一模型 leaderboard。
- ASSISTments: 类别：知识追踪/认知诊断。论文/README/数据卡未找到可直接引用的官方统一模型 leaderboard。
- BigMath-Verified: 类别：数学数据资源。论文/README/数据卡未找到可直接引用的官方统一模型 leaderboard。
- CheggMate: 类别：教育系统/产品。论文/README/数据卡未找到可直接引用的官方统一模型 leaderboard。
- Chinese Fineweb Edu: 类别：教育资源。论文/README/数据卡未找到可直接引用的官方统一模型 leaderboard。
- Codecademy Dataset: 类别：教育资源。论文/README/数据卡未找到可直接引用的官方统一模型 leaderboard。
- CS1QA: 类别：教育问答数据。论文/README/数据卡未找到可直接引用的官方统一模型 leaderboard。
- EdNet: 类别：知识追踪/认知诊断。论文/README/数据卡未找到可直接引用的官方统一模型 leaderboard。
- EduDial: 类别：教育问答数据。论文/README/数据卡未找到可直接引用的官方统一模型 leaderboard。
- ELLIPSE Corpus: 类别：自动评分经典数据。论文/README/数据卡未找到可直接引用的官方统一模型 leaderboard。
- FineWeb-Edu: 类别：教育资源。论文/README/数据卡未找到可直接引用的官方统一模型 leaderboard。
- FoundationalAssist: 类别：知识追踪/认知诊断。论文/README/数据卡未找到可直接引用的官方统一模型 leaderboard。
- Google Education Dialogue Dataset: 类别：教育问答数据。论文/README/数据卡未找到可直接引用的官方统一模型 leaderboard。
- IMO-ANSWER BENCH: 类别：数学数据资源。论文/README/数据卡未找到可直接引用的官方统一模型 leaderboard。
- InnoSpark: 类别：教育系统/产品。论文/README/数据卡未找到可直接引用的官方统一模型 leaderboard。
- IntrEx: 类别：教育问答数据。论文/README/数据卡未找到可直接引用的官方统一模型 leaderboard。
- Junyi Academy: 类别：知识追踪/认知诊断。论文/README/数据卡未找到可直接引用的官方统一模型 leaderboard。
- KDD Cup 2010: 类别：知识追踪/认知诊断。论文/README/数据卡未找到可直接引用的官方统一模型 leaderboard。
- LectureBank: 类别：教育资源。论文/README/数据卡未找到可直接引用的官方统一模型 leaderboard。
- LeetCode Student Submissions: 类别：教育资源。论文/README/数据卡未找到可直接引用的官方统一模型 leaderboard。
- Math23K: 类别：数学数据资源。论文/README/数据卡未找到可直接引用的官方统一模型 leaderboard。
- MathDial: 类别：教育问答数据。论文/README/数据卡未找到可直接引用的官方统一模型 leaderboard。
- MLPdataset: 类别：教育资源。论文/README/数据卡未找到可直接引用的官方统一模型 leaderboard。
- MOOCCube: 类别：教育资源。论文/README/数据卡未找到可直接引用的官方统一模型 leaderboard。
- NCTE Transcripts: 类别：教育资源。论文/README/数据卡未找到可直接引用的官方统一模型 leaderboard。
- NuminaMath: 类别：数学数据资源。论文/README/数据卡未找到可直接引用的官方统一模型 leaderboard。
- PEBBLE: OpenReview record describes an initial multi-turn tutor benchmark with scaffolding, diagnostic questioning, misconception repair, metacognitive support, affective support, overhelping penalty, contamination controls, and an evaluation kit to be released upon acceptance.
- PTADisc: 类别：知识追踪/认知诊断。论文/README/数据卡未找到可直接引用的官方统一模型 leaderboard。
- QACP: 类别：教育问答数据。论文/README/数据卡未找到可直接引用的官方统一模型 leaderboard。
- SCB-Dataset: 类别：教育资源。论文/README/数据卡未找到可直接引用的官方统一模型 leaderboard。
- SIGHT: 类别：教育资源。论文/README/数据卡未找到可直接引用的官方统一模型 leaderboard。
- SocraticLM: 类别：教育问答数据。论文/README/数据卡未找到可直接引用的官方统一模型 leaderboard。
- STATICS2011: 类别：知识追踪/认知诊断。论文/README/数据卡未找到可直接引用的官方统一模型 leaderboard。
- Synthetic: 类别：知识追踪/认知诊断。论文/README/数据卡未找到可直接引用的官方统一模型 leaderboard。
- TalkMoves: 类别：教育资源。论文/README/数据卡未找到可直接引用的官方统一模型 leaderboard。
- TIMSS Video Study: 类别：教育资源。论文/README/数据卡未找到可直接引用的官方统一模型 leaderboard。
- TutorialBank: 类别：教育资源。论文/README/数据卡未找到可直接引用的官方统一模型 leaderboard。
- VisualEDU: 类别：教育资源。论文/README/数据卡未找到可直接引用的官方统一模型 leaderboard。
- 九章大模型: 类别：教育系统/产品。论文/README/数据卡未找到可直接引用的官方统一模型 leaderboard。
- 数字教育应用算法智能诊断公共数据集: 类别：知识追踪/认知诊断。论文/README/数据卡未找到可直接引用的官方统一模型 leaderboard。
- 科大讯飞星火教育: 类别：教育系统/产品。论文/README/数据卡未找到可直接引用的官方统一模型 leaderboard。
- 网易有道子曰: 类别：教育系统/产品。论文/README/数据卡未找到可直接引用的官方统一模型 leaderboard。
