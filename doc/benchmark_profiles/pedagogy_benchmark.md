# Pedagogy Benchmark

**一句话**：用教师资格/职业考试真题测模型的**教学法专业知识**——不是学科知识，而是"怎么教"的知识。

## 出处与背景

- AI for Education（aiforeducation.io），2025（论文 *Benchmarking the Pedagogical Knowledge of Large Language Models*）；https://huggingface.co/datasets/AI-for-Education/pedagogy-benchmark
- 动机：模型的学科能力评得很多，教育学专业知识（学习理论、课堂管理、评估方法、特殊教育）几乎没人评。官方 leaderboard 覆盖 97 个模型。

## 数据

- 两个子集：**CDPK**（跨领域教学法知识，约 900 题选择题）和 **SEND**（特殊教育需求，约 300 题）。题目来自教师资格认证考试。
- **获取状态：HF gated**（要申请），本地没有原始数据——这是它和其他教育核心 benchmark 的关键区别。

## 任务与判分

- 选择题，accuracy，规则判分。
- 原生维度：CDPK 按教学主题分类；SEND 单列。

## 在本仓库怎么用

- **无 adapter**，分数来自同事跑分的外部报告（`otherbenchmark/`，0701 聚合卡片 + `ASAP+Peda.png`）。仓库里它是 `source_scope: otherbenchmark`。
- 映射里有三行：CDPK / SEND / 0701 聚合卡片（后者只在没有细分分数时用，去重逻辑保证不重复计分）。

## 局限与注意

- **区分度（13 号实测）**：n=7，均分 8.56，标准差 0.21 → ceiling + low_variance。**pilot 里 ρ=−0.90 红旗（与 edubench）双方都在受限名单里，该证据不可靠**——权重修订已按计划推迟。
- 无原始数据在手：没法复算、没法抽题检查污染、没法进 p08 复用。凡是基于它的结论都依赖同事报告的口径。
- "知道怎么教"≠"实际会教"——它是 P17 里唯一的知识侧证据，正因如此才拆了 strategy_knowledge facet。

## 当前映射

- CDPK：P05 0.45 / P17 0.35 / P06 0.20；SEND：P05 0.35 / P16 0.35 / P17 0.30；education_core。
- 构念核对：P06 problem_reasoning 挂载建议移出（R8）；P16/P17 的知识侧 facet 由它独家供分。
