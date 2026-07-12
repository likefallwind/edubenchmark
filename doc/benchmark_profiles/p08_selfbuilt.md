# P08 自建两件套（p08_calibration / p08_abstention）

**一句话**：为 P08（置信度校准与弃答）专门设计的两个自建测验——一个测"自信地教错有多少"，一个测"不会的题敢不敢说不会"。教育产品里这是"模型会不会一本正经误导学生"的直接代理。

## 出处与背景

- 本仓库自建，设计文档 `doc/p08_calibration_eval_plan_2026-07-11.md`（v1 零标注方案）。
- 动机：P08 此前完全无覆盖；方案刻意选择零人工标注路线——复用已有 exact-match benchmark 的对错信号。

## 数据

- **p08_calibration**：550 题，从 ceval / mmlu_pro / agieval / mtb_problem_solving 分层抽样（`data/p08_calibration/item_list_v1.txt`，抽样器 `build_p08_item_list.py`），答题时要求附带 verbalized confidence（ceval 走 0-shot 以容纳置信度后缀）。
- **p08_abstention**：UMWP（不可答数学应用题——删掉必要条件后的题）等公开集，`fetch_eval_datasets.py --benchmark umwp`。

## 任务与判分

- calibration：规则判对错 + 解析自报置信度 → **CWR**（自信错误率）、ECE、AUROC；headline = 0.5×(1−CWR)+0.5×AUROC，归一到 `composite_0_to_10`。
- abstention：规则判分（识别不可答并声明），无裁判；balanced abstention score。

## 局限与注意

- 目前只有 MiniMax-M3 可用分（待批量跑），13 号检查里尚无配对可算。
- verbalized confidence 是模型"嘴上说的"置信度，与内部概率可能脱节——这本身是测量的一部分，但解释时别当真概率。
- 题源复用门槛 benchmark → 与门槛分数天然相关，分析 P08 时要用偏相关控制总分（13 号脚本已支持）。

## 当前映射

- p08_calibration：P08 0.80 / P07 0.20；p08_abstention：P08 0.85 / P01 0.15；diagnostic。
- 构念核对：P08 是设计上最干净的 formative P（两 facet 各有专属测验）；它同时是 P07/P01 的搭车来源之一（R9 备注）。
