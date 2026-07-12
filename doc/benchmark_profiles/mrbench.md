# MRBench

**一句话**：AI tutor 回复的 8 维人工标注基准（NAACL 2025 *Unifying AI Tutor Evaluation*）——200 段学生犯错对话 × 至多 9 个模型的 tutor 回复，每条人工标 8 个教学维度。

## 出处与背景

- Maurya、Kochmar 等（MBZUAI），NAACL 2025；repo `kaushal0494/UnifyingAITutorEvaluation`，数据 `MRBench/MRBench_V2.json`。
- 动机：把 tutor 回复质量的评价维度统一成一个分类学（后来直接衍生出 BEA 2025 共享任务）。

## 数据

- 200 段对话（源自 MathDial + Bridge，真实学生数学错误），每段配至多 9 个 tutor 模型的回复，人工标注 8 维。英文。
- 获取：`fetch_eval_datasets.py --benchmark mrbench`（urllib 直下）。

## 任务与判分

- 8 个原生维度：Mistake Identification / Mistake Location / Revealing of the Answer（No / Yes-correct / Yes-incorrect）/ Providing Guidance / Actionability / Coherence / Tutor Tone（鼓励/中性/冒犯）/ Humanlikeness。
- 两个 adapter：
  - **mrbench_judge**：被测模型当裁判逐维贴标签，与人类金标算一致率 + macro-F1 + kappa（测"这个模型做裁判有多像人"）；
  - **mrbench_tutor**：被测模型生成下一句 tutor 回复，固定裁判（`MRBENCH_JUDGE_MODEL`，默认 MiniMax-M3）标 8 维；headline = 关键三维（MI/PG/Actionability）全 Yes 的 pass rate，全部维度分布在 `extra_metrics`。

## 局限与注意

- **区分度（13 号实测）**：mrbench_tutor n=3，均分 3.73，sd 0.65——分数拉得开但模型太少。
- 只有 200 段对话，样本量小，维度级估计噪声大。
- tutor 侧结果依赖固定裁判的标注质量；judge 侧 excluded 不计分。
- pass rate 复合问题同 BEA（构念核对 R2：Mistake_Identification→P13、Guidance/Actionability→P17/P18、Revealing_Answer/Tutor_Tone→P20，单维分现成）。

## 当前映射

- mrbench_tutor：P18 0.45 / P17 0.30 / P20 0.25，education_core；mrbench_judge：P14/P13/P20，excluded_judge_task。
- 构念核对：R2、R3；P20 的"不泄题/语气"证据应指向单维度而非整体 pass rate。
