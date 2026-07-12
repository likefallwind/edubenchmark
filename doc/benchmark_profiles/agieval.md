# AGIEval

**一句话**：拿人类标准化考试（高考、SAT、LSAT、法考、公务员考试）原题测模型，中英双语。

## 出处与背景

- 微软，2023（论文 *AGIEval: A Human-Centric Benchmark for Evaluating Foundation Models*）；https://github.com/ruixiangcui/AGIEval
- 动机：用"给人设计的考试"而非"给模型设计的题"来衡量模型的人类级认知任务表现。

## 数据

- 约 20 个任务子集：高考各科、SAT、LSAT、律师资格、公务员行测、数学竞赛填空等；中英双语混合。
- 获取：数据随官方 repo checkout 直接可用（不需要 HF 下载）。

## 任务与判分

- 两种题型：选择题（字母精确匹配，选项解析移植官方 `post_process.py`）+ 数学填空（等价判断动态加载官方 `math_equivalence.is_equiv`）。
- 规则判分为主，无裁判依赖。按任务/语言/题型出分桶。

## 在本仓库怎么用

- adapter `scripts/eval/benchmarks/agieval.py`；p08_calibration 复用其中部分题目做置信度测验。

## 局限与注意

- **区分度（13 号实测）**：n=5，均分 8.74，标准差 0.40 → ceiling + low_variance。
- 污染风险高（历年真题全网可查）。
- 混合题型使单一 accuracy 数字掩盖了子集差异。

## 当前映射

- P06 0.45 / P05 0.35 / P01 0.20；foundation_gate。
- 构念核对：P01 搭车（R9）。§2.7 冗余决策：对新模型**降为可选**（与 mmlu_pro/ceval 相互 ρ≥0.9）。
