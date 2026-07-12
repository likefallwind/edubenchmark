# P07 两轮自查（p07_selfcheck）

**一句话**：先答题、再在同一对话里无提示地要求"重新检查你的解答"，规则判分分离"错改对"（真自查）与"对改错"（有害的自我怀疑）——P07（自我校验与修正）的第一个直接测量。

## 出处与背景

- 本仓库自建（2026-07-12，缺口推荐文档优先级第 2 项）；协议是学术界 intrinsic self-correction 评测的标准做法（无外部反馈、不暗示对错）。
- 动机：构念核对（R9）发现 P07 此前全是搭车格子——分数看着有，实际没有任何测验直接考"自查"这个行为。

## 数据

- 零新增标注：复用 P08 的 delegate（ceval 0-shot / mmlu_pro / agieval / mtb_problem_solving）和**同一份**难度分层 item_list（`data/p08_calibration/item_list_v1.txt`，550 题），P07/P08 同题可比。

## 任务与判分

- 第一轮：delegate 原生出题（prediction 阶段）；第二轮：extract 阶段把原对话 + 模型自己的第一轮回答 + 固定复查指令再发给**被测模型本身**（harness 会把被测模型名写进 `adapter.model_under_test`；传给 extract 的 client 是抽取模型，不是被测模型）。
- 两轮答案都用 delegate 自己的抽取和判分。headline `score_10 = 10×[0.5×改对率 + 0.5×(1−改错率)]`，两项都以第一轮状态为条件，构造上与第一轮正确率解耦。`extra_metrics` 含 r1/r2 accuracy、net_gain、change_rate、逐来源分解。

## 在本仓库怎么用

```bash
MODEL=MiniMax-M3 ./scripts/run_eval.sh p07_selfcheck    # 默认走 item_list（550 题 × 2 轮）
```

## 为什么不能复用以前跑过的预测

以前各 benchmark 的全量预测只有"第一轮答案"，而 P07 测的是**第二轮行为**——模型看到自己的第一轮回答后改不改、改对还是改错。第二轮必须以第一轮的原始回复作为对话历史现场再调一次被测模型，这个交互在旧预测里不存在，也没法离线补造（换措辞、换上下文都算换协议）。所以旧全量分数只能省下"第一轮"这一半成本吗？也不能：为了保证两轮在同一套 prompt/参数/对话格式下发生，第一轮也要在本协议内重跑，否则改答率会混入格式差异。

## 局限与注意

- 每题两次被测模型调用（round 1 + round 2），成本约是普通跑分的 2 倍。
- "复查"指令措辞固定（中/英各一版）；换措辞就是换协议，对比时注意。
- 已知现象（文献一致）：多数模型 intrinsic self-correction 改对率低、部分模型改错率不低——低分是真实测量结果，不是 bug。

## 当前映射

- p07_selfcheck：P07 0.85 / P08 0.15，diagnostic，weight 0.85；测量模型 P07/core weight 0.85 + P08/calibration weight 0.15。
- 2026-07-12 冒烟（MiniMax-M3, 3 题）：1 题错改对、0 题对改错。全量跑分随批量启动。
