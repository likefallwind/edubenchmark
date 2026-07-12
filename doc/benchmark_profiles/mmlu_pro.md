# MMLU-Pro

**一句话**：MMLU 的高难升级版——选项从 4 个加到 10 个、题目偏推理，用来测大学水平的学科知识与答题能力。

## 出处与背景

- TIGER-Lab，2024（论文 *MMLU-Pro: A More Robust and Challenging Multi-Task Language Understanding Benchmark*）；https://huggingface.co/datasets/TIGER-Lab/MMLU-Pro
- 动机：原版 MMLU 被强模型刷到 88%+ 接近饱和，且对 prompt 敏感；MMLU-Pro 通过 10 选 1 + 提高推理占比来恢复区分度。

## 数据

- 约 12,000 题，14 个学科大类（数学、物理、化学、法律、工程、心理学等），英文。
- 获取：`TIGER-Lab/MMLU-Pro` 公开可下（注意 `TIGER-AI-Lab/` 路径是 gated 的，别用错）；`fetch_eval_datasets.py --benchmark mmlu_pro` 落到 `sources/datasets/`。

## 任务与判分

- 10 选 1 选择题，模型输出选项字母。
- 规则判分：官方 `answer is (X)` 正则提取，失败时走 LLM 提取兜底；精确匹配字母。无裁判依赖。

## 在本仓库怎么用

- adapter `scripts/eval/benchmarks/mmlu_pro.py`，`--benchmark mmlu_pro`。
- 按 category 出分桶。

## 局限与注意

- **区分度（13 号实测）**：n=5，均分 8.60，标准差 0.21 → ceiling + low_variance 双标记，当前模型集上排名基本无信息量。
- 训练数据污染风险高（公开考试题库类）。
- 纯英文，对中文教育场景是间接证据。

## 当前映射

- P05 知识调用 0.60 / P06 推理 0.30 / P01 指令遵循 0.10；evidence_tier = foundation_gate。
- 构念核对：P01 挂载属于搭车（R9）；§2.7 冗余规则下它是三个基础答题类里**保留的那一个**（agieval/ceval 转按需）。
