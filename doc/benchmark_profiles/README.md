# Benchmark 档案（2026-07-11）

主计分体系里每个 benchmark 一份说明文档：它是什么、谁做的、数据从哪来、怎么判分、我们怎么用它、有什么局限、当前映射到哪些 P。目的是让映射裁决（M3）和对外解释时不用翻论文——所有"这个分数到底在测什么"的问题在这里有答案。

事实来源：官方论文/仓库、本仓库的调研库存（`doc/edubench.md`、`data/exhaustive_2026-05-13/`）、adapter 实现（`scripts/eval/benchmarks/`）、otherbenchmark 报告，以及 13 号映射效度检查的实测统计。**区分度数据以 2026-07-11 的 13 号检查为准**（n=共同模型数，均分/标准差按 0-10 归一分）。

配套文档：

- 缺口推荐：`doc/benchmark_gap_recommendations_2026-07-11.md`（无覆盖的 P 和子能力该引入什么）
- 构念核对：`doc/p_construct_review_2026-07-11.md`（每个格子挂得对不对）

## 档案索引

| 文件 | benchmark | 一句话 | 类型 |
|---|---|---|---|
| [mmlu_pro.md](mmlu_pro.md) | MMLU-Pro | 高难版 MMLU，10 选 1 学科知识 | 门槛 |
| [ceval.md](ceval.md) | C-Eval | 中文 52 学科考试选择题 | 门槛 |
| [agieval.md](agieval.md) | AGIEval | 高考/SAT/法考等标准化考试 | 门槛 |
| [olympiadbench.md](olympiadbench.md) | OlympiadBench | 奥赛级数学物理开放题 | 门槛 |
| [mathvista.md](mathvista.md) | MathVista | 图文数学推理 | 诊断 |
| [pedagogy_benchmark.md](pedagogy_benchmark.md) | Pedagogy Benchmark | 教师资格考试教学法选择题 | 教育核心 |
| [asap_2.md](asap_2.md) | ASAP 2.0 | 英文作文自动评分 | 教育核心 |
| [sas_bench.md](sas_bench.md) | SAS-Bench | 高考主观题分步评分+错因诊断 | 教育核心 |
| [edubench.md](edubench.md) | EduBench | 中文教育场景生成，9 场景 12 指标 | 教育核心 |
| [tutorbench.md](tutorbench.md) | TutorBench | 真实多模态辅导，rubric 判分 | 教育核心 |
| [mathtutorbench.md](mathtutorbench.md) | MathTutorBench | 数学辅导 7+2 任务全家桶 | 教育核心 |
| [bea2025.md](bea2025.md) | BEA 2025 共享任务 | tutor 回复 4 维教学质量 | 教育核心 |
| [mrbench.md](mrbench.md) | MRBench | tutor 回复 8 维人工标注 | 教育核心 |
| [mmtutorbench.md](mmtutorbench.md) | MMTutorBench | 视频关键帧数学辅导 | 诊断 |
| [eduguard_bench.md](eduguard_bench.md) | EduGuardBench | 教育安全：知识题+对抗攻击 | 教育核心 |
| [eduillustrate.md](eduillustrate.md) | EduIllustrate | 生成 Manim 可视化讲解 | 诊断 |
| [p08_selfbuilt.md](p08_selfbuilt.md) | P08 自建两件套 | 置信度校准 + 能力性弃答 | 诊断 |

## 档案模板

每份档案包含：**出处与背景**（发布方、时间、链接、要解决什么问题）/ **数据**（规模、语言、学段学科、获取状态）/ **任务与判分**（形式、官方指标、规则判分还是裁判判分、原生维度）/ **在本仓库怎么用**（adapter 或外部报告、运行要点）/ **局限与注意**（区分度实测、污染风险、裁判依赖）/ **当前映射**（挂载的 P 与核对结论）。
