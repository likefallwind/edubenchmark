# C-Eval

**一句话**：中文学科考试选择题基准，52 个学科、从初中到职业资格四个难度层，测中文语境下的学科知识。

## 出处与背景

- 上海交大 / 清华 / 港科大等，2023（NeurIPS 2023 Datasets & Benchmarks）；https://github.com/hkust-nlp/ceval
- 动机：给中文大模型一个覆盖国内考试体系的知识基准，弥补 MMLU 英文中心的问题。

## 数据

- 13,948 题选择题（4 选 1），52 学科 × 4 难度（初中/高中/大学/职业资格）。
- **官方 test 集答案不公开**（要提交官网评分）；本仓库评的是带标签的 **val 集 1,346 题**。
- 获取：`fetch_eval_datasets.py --benchmark ceval` 遍历 52 个 subject config，学科→大类映射读官方 repo 的 `subject_mapping.json`。

## 任务与判分

- 官方协议是 **5-shot answer-only**：每学科 5 道 dev 题作为多轮示例、回复裸字母；本仓库 adapter 照搬（无 LLM 提取，读首字母精确匹配，同官方 `response[0] == answer`）。
- 按大类和学科出分桶。

## 在本仓库怎么用

- adapter `scripts/eval/benchmarks/ceval.py`；注意 p08_calibration 里复用 ceval 时改走 0-shot（要给置信度后缀留空间）。

## 局限与注意

- **区分度（13 号实测）**：n=5，均分 9.11，标准差 0.30 → ceiling + low_variance，是全体系里天花板最严重的格子之一。
- 污染风险极高：题目来自公开考试题库，且发布已两年多。
- val 只有 1,346 题，学科级分数样本很小。

## 当前映射

- P05 0.60 / P06 0.25 / P01 0.15；foundation_gate。
- 构念核对：P01 搭车（R9）。§2.7 冗余决策：**转为按需跑**——只在评测中文优先模型时启用（与 mmlu_pro ρ≈1 只在现有模型上成立，中文特化模型未必）。
