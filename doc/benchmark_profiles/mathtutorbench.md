# MathTutorBench

**一句话**：数学辅导能力全家桶——7 个任务 + 2 个 hard 变体，从"会不会做题"一路测到"会不会搭脚手架引导学生"，是"会答题≠会教"命题的最直接载体。

## 出处与背景

- ETH Zurich LRE 组（Macina 等），2025；https://github.com/eth-lre/mathtutorbench
- 动机：基于学习科学理论把"辅导"拆成可分别测量的任务；原版配套一个专家级奖励模型（能区分专家/新手教师回复）判开放式任务。

## 数据

- 题源组合：GSM8K（解题类）、MathDial（对话辅导类）、eth-nlped/stepverify（学生解验证类）。英文。
- 本地可用，数据随评测直接拉取。

## 任务与判分（9 个 adapter + 1 个裁判校准）

| 任务 | 测什么 | 判分 |
|---|---|---|
| problem_solving | 解题正确率 | 规则（数值匹配） |
| solution_correctness | 判学生解对错 | 规则（移植官方 parse） |
| mistake_location | 定位第一处错误步骤 | 规则 |
| mistake_correction | 给出修正后的正确答案 | 规则（从回复提取答案） |
| socratic_questioning | 生成引导性提问 | SacreBLEU 对金标问题取最佳匹配 |
| scaffolding / scaffolding_hard | 生成下一步辅导回复 | 与参考回复比较的 win-rate |
| pedagogy / pedagogy_hard | 按教学法指令生成回复 | win-rate |

- 官方开放任务用 GPU 奖励模型判；本仓库用 **LLM 裁判 win-rate 替代**（`MATHTUTORBENCH_JUDGE_MODEL`，pairwise prompt 有版本号与 sha256 记录）——绝对分不可与论文对照，横向比较可用。
- `mathtutorbench_judge_calibration` 单独校准裁判与官方奖励模型的一致性。

## 局限与注意（13 号实测）

- **门槛化的任务**：problem_solving n=4 均分 9.70（严重受限）、solution_correctness n=5 均分 8.68 sd 0.16（受限）、mistake_correction n=5 均分 9.02（受限，pilot 里与门槛类 ρ≈1）、mistake_location n=5 sd 仅 0.10（受限）。
- **有区分度的任务**：scaffolding 均分 3.36 sd 1.83、scaffolding_hard 2.98/1.62（全体系区分度最好）、pedagogy_hard 8.00/0.71 尚可。
- **socratic_questioning 本地跑过分但没进映射**（构念核对 R11 要补挂）；BLEU 对短问句是弱指标，权重应保守。
- win-rate 类分数依赖裁判，且与参考回复风格相关。

## 当前映射

- 8 个任务各一行（见 `02_benchmark_ability_mapping.jsonl`）：解题类挂 P05/P06/P07/P11（R17 后判对/定位/归因是 P11a/b/c facet），辅导类挂 P17/P18；problem_solving 是 foundation_gate，其余 education_core。
- 构念核对：mistake_correction 在 P11c（原 P13）权重下调（R6）；scaffolding/pedagogy 归 strategy_enactment"对话辅导"侧（R4）；socratic 补挂（R11）。
