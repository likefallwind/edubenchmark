# TutorBench

**一句话**：Scale AI 的真实多模态辅导基准——学生上传手写作业/图表/截图提问，模型当家教，按人写的逐条 rubric 判回复质量。

## 出处与背景

- Scale AI，2025；https://huggingface.co/datasets/ScaleAI/TutorBench
- 动机：辅导能力评测要贴近真实使用（多模态输入 + 自适应讲解 + 作业反馈 + 主动引导三类任务），rubric 由人工逐题编写。

## 数据

- 约 1,470 条样本，文本+图片（手写作业、图表、截图），6 大 STEM 学科（生物/物理/化学/统计/微积分/计算机）。英文。
- **获取状态：HF gated**（CLAUDE.md 记录在案），本地无原始数据。

## 任务与判分

- 模型生成辅导回复，LLM 裁判逐条判 rubric 通过与否。三个指标：Simple Pass（不加权）、Weighted Positive（critical 条目权重更高）、**Weighted Shifted**（考虑负面 rubric 下界，主排序指标）。
- 本地口径：**Fair815**——815 个公平样本子集，所有模型同分母；缺失/跳过按未通过算（保守）。

## 在本仓库怎么用

- **无 adapter**，分数来自同事报告 `otherbenchmark/tutorbench_0630.MD`（vlm_eval 链路）。

## 局限与注意

- **区分度（13 号实测）**：n=6，均分 5.48，标准差 0.25 → low_variance 受限。均分不高但模型间拉不开。
- 报告自己的 case study 发现：**它强烈奖励"完整、显式、分步骤"的回答风格**——回答简短的模型（如 Qwen3-VL-235B）失分主要因为不够显式，而非看不懂图。也就是说分数里混着可观的"回答风格"方差。
- rubric 判分依赖裁判 LLM；缺失样本处理口径影响绝对分。

## 当前映射

- P18 0.40 / P17 0.35 / P03 0.25；education_core。
- 构念核对：P03 挂载归"教学场景图文理解"子方向（R5）；P17 归 strategy_enactment 的"对话辅导"侧（R4）。
