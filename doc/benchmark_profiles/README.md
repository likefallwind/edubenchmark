# Benchmark 档案

主计分体系里**每个 benchmark_id 一份档案**：它是什么、谁做的、数据从哪来、怎么判分、我们怎么用它、有什么局限。目的是让映射裁决和对外解释时不用翻论文——所有"这个分数到底在测什么"的问题在这里有答案。

事实来源：官方论文/仓库、本仓库的调研库存（`doc/edubench.md`、`data/exhaustive_2026-05-13/`）、adapter 实现（`scripts/eval/benchmarks/`）、otherbenchmark 报告，以及 13 号映射效度检查的实测统计。**区分度数据以 2026-07-11 的 13 号检查为准**（n=共同模型数，均分/标准差按 0-10 归一分）。

## 一个 id 一份档案

档案文件名必须等于 benchmark_id（唯一例外 `mooccube_prereq` → `mooccube.md`，走 `PROFILE_MAP`）。

这条规则是改出来的。此前 17 个子评测 id 折叠到 5 份家族档案上，结果是：点进 `mathtutorbench_socratic` 看到的是整个家族的九行任务表，其中八行与这个格子无关；而家族档案「当前映射」一节说的 P 列表，与该 id 实际挂载的 P 对不上。现在每个 id 自带档案，开头点明它是家族里的哪一个、与兄弟子评测什么关系。

下面五份是**家族背景文档**，保留供阅读，构建脚本不再读取：`mathtutorbench.md`、`eduguard_bench.md`、`mrbench.md`、`bea2025.md`、`p08_selfbuilt.md`。

## 档案索引

### 门槛与通识

| 文件 | 一句话 |
|---|---|
| [mmlu_pro.md](mmlu_pro.md) | 高难版 MMLU，10 选 1 学科知识 |
| [ceval.md](ceval.md) | 中文 52 学科考试选择题 |
| [agieval.md](agieval.md) | 高考/SAT/法考等标准化考试原题 |
| [olympiadbench.md](olympiadbench.md) | 奥赛级数学物理开放题 |
| [ifeval.md](ifeval.md) | 可验证指令遵循，规则判分 |

### 多模态

| 文件 | 一句话 |
|---|---|
| [mathvista.md](mathvista.md) | 图文数学推理 |
| [k12vista.md](k12vista.md) | 中文 K12 图文学科题 |
| [mmtutorbench.md](mmtutorbench.md) | 视频关键帧数学辅导 |
| [eduillustrate.md](eduillustrate.md) | 生成 Manim 可视化讲解 |

### 教育核心（单 id）

| 文件 | 一句话 |
|---|---|
| [edubench.md](edubench.md) | 中文教育场景生成，9 场景 12 指标 |
| [pedagogy_benchmark.md](pedagogy_benchmark.md) | 教师资格考试教学法选择题 |
| [tutorbench.md](tutorbench.md) | 真实多模态辅导，rubric 判分 |
| [asap_2.md](asap_2.md) | 英文作文自动评分 |
| [sas_bench.md](sas_bench.md) | 高考主观题分步评分 + 错因诊断 |
| [mooccube.md](mooccube.md) | 先修关系推理（id `mooccube_prereq`） |
| [p07_selfcheck.md](p07_selfcheck.md) | 无提示两轮自查，改对率 vs 改错率 |

### MathTutorBench 九个子任务

家族背景见 [mathtutorbench.md](mathtutorbench.md)。四个规则判分的硬任务 + 一个 BLEU 判分 + 四个胜率判分的开放任务。

| 文件 | 一句话 |
|---|---|
| [mathtutorbench_problem_solving.md](mathtutorbench_problem_solving.md) | 纯解题，门槛用 |
| [mathtutorbench_solution_correctness.md](mathtutorbench_solution_correctness.md) | 判学生解对错 |
| [mathtutorbench_mistake_location.md](mathtutorbench_mistake_location.md) | 定位首处错误步骤 |
| [mathtutorbench_mistake_correction.md](mathtutorbench_mistake_correction.md) | 给出改对的解答 |
| [mathtutorbench_socratic.md](mathtutorbench_socratic.md) | 引导性提问，BLEU 判分 |
| [mathtutorbench_scaffolding.md](mathtutorbench_scaffolding.md) | 搭脚手架，区分度最好的格子之一 |
| [mathtutorbench_scaffolding_hard.md](mathtutorbench_scaffolding_hard.md) | 脚手架 hard，与常规版 r=0.98 |
| [mathtutorbench_pedagogy.md](mathtutorbench_pedagogy.md) | 按给定教学法生成回复 |
| [mathtutorbench_pedagogy_hard.md](mathtutorbench_pedagogy_hard.md) | 教学法 hard，与常规版 r=0.92 |

### 成对子评测

| 文件 | 一句话 |
|---|---|
| [eduguard_sata.md](eduguard_sata.md) | 教学伤害知识全选题（家族见 [eduguard_bench.md](eduguard_bench.md)） |
| [eduguard_adversarial.md](eduguard_adversarial.md) | 801 条越狱提示，区分度最大的格子 |
| [bea2025_tutor.md](bea2025_tutor.md) | 生成 tutor 回复，4 维标注（家族见 [bea2025.md](bea2025.md)） |
| [bea2025_judge.md](bea2025_judge.md) | 当裁判贴标签，与人类金标比 |
| [mrbench_tutor.md](mrbench_tutor.md) | 生成 tutor 回复，8 维标注（家族见 [mrbench.md](mrbench.md)） |
| [mrbench_judge.md](mrbench_judge.md) | 当裁判贴 8 维标签 |
| [p08_calibration.md](p08_calibration.md) | 自报置信度 vs 实际正确率（家族见 [p08_selfbuilt.md](p08_selfbuilt.md)） |
| [p08_abstention.md](p08_abstention.md) | 不可答题的弃答表现 |

### LongTutor 三个子评测

| 文件 | 一句话 |
|---|---|
| [longtutor_evidence.md](longtutor_evidence.md) | 长材料证据定位，按记忆类型三分 |
| [longtutor_diagnosis.md](longtutor_diagnosis.md) | 从长历史诊断学生知识状态 |
| [longtutor_teaching.md](longtutor_teaching.md) | 长历史下的教学动作选择 |

## 档案模板

**单 id 的 benchmark**：出处与背景 / 数据 / 任务与判分 / 在本仓库怎么用 / 局限与注意。

**子评测**：这是哪个子评测（家族、兄弟子评测、为什么分开计分）/ 出处与背景 / 任务与判分 / 局限与注意。

## 写作约定

- **不写权重数字、不写映射清单。** `当前映射` 小节会被解析器丢弃，网站上的权重表由 `data/mapping_measurement_model_v6.json` 生成。老档案里残留的 `当前映射` 一节用的还是旧 P 编号，不要照抄。
- H1 标题就是网站上的页面标题，子评测请写成 `家族 · 子任务名`。
- `**一句话**：…` 紧跟 H1，是卡片和页面导语。
- 每行一条 bullet，自成一句；表格和代码块会被解析器丢弃。

配套文档：缺口推荐 `doc/benchmark_gap_recommendations_2026-07-11.md`、构念核对 `doc/p_construct_review_2026-07-11.md`。
