# MathVista

**一句话**：图文结合的数学推理基准（图表、几何图、函数图像），测多模态模型"看图做数学"的能力。

## 出处与背景

- Lu Pan 等（UCLA / 微软），2023，ICLR 2024；https://github.com/lupantech/MathVista
- 动机：数学推理评测此前几乎全是纯文本，MathVista 把 28 个既有多模态数据集 + 3 个新建子集统一成一个视觉数学基准。

## 数据

- 6,141 题；常用 testmini 1,000 题（带答案）；英文。
- 图片需单独下载：`cd sources/datasets/mathvista/data && wget .../images.zip && unzip`。

## 任务与判分

- 混合题型（选择/数值/文本），按 task / question_type / answer_type 分桶。
- 判分移植官方 `evaluation/`：few-shot 提取提示（`ext_ans.demo_prompt`）+ `normalize_extracted_answer` + 最近选项编辑距离，重实现在 `scripts/eval/scoring.py`，无额外依赖。

## 在本仓库怎么用

- adapter `scripts/eval/benchmarks/mathvista.py`；必须用视觉模型（MiniMax-M3 可以，M2.7 纯文本不行）；`--dry-run` 会省略 base64 图片打印消息。

## 局限与注意

- **区分度（13 号实测）**：n=1——只有一个模型跑过，完全没法做配对分析。补模型清单里要带上它。
- 题源来自公开数据集拼装，部分子集污染风险高。
- 感知与推理混在一个 accuracy 里，拆不开（构念核对里归"解题式图像理解"）。

## 当前映射

- P06 0.45 / P03 0.35 / P05 0.20；diagnostic。
- 构念核对：P03 的最接近直接测量，R5 拆分后归"解题图像理解"facet。
