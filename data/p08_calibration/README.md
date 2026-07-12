# P08/P07 共用题目清单（item_list_v1）

这个目录存的是自建测验的**固定题目清单**，不是题目本身——题目实体在 `sources/datasets/` 各题库里，这里只按 `<来源>::<原生题号>` 记录抽了哪些题。

## 谁在用

| 测验 | 用法 |
|---|---|
| `p08_calibration`（置信度校准） | 550 题原题 + 置信度诱导后缀 |
| `p07_selfcheck`（两轮自查） | 同一份 550 题，先答题再无提示复查 |

两个测验刻意共用同一份清单：P07 和 P08 的分数同题可比，且分析时可以用同题正确率做控制。

## 清单构成（v1，2026-07-11 生成）

- 共 550 题：ceval 200 / mmlu_pro 150 / agieval 100 / mtb_problem_solving 100（都是规则判分的 exact-match 题库）。
- **难度分层 30/50/20**（easy/mixed/hard）：难度用**历史模型集成**定义——当时已有全量跑分的模型里 0 个做错=easy、部分做错=mixed（信息量最高层）、全错=hard。绝不用被测模型自身的错题（否则对后来的模型不公平）。
- 固定随机种子，生成幂等。逐层明细在 `item_list_v1_layers.json`，统计在 `item_list_v1_manifest.json`。

## 重要纪律

1. **一轮跑分战役内不要重新生成清单**——所有模型必须跑同一套题才可比。要换题就升版本号（item_list_v2），旧分数标注清单版本。
2. 难度加权集上的绝对分数只用于**模型间相对比较**，不作自然分布下的绝对宣称（题目刻意偏难）。
3. 重新生成命令（只在开新版本时用）：`python scripts/eval/data/build_p08_item_list.py`

## 相关文档

- 设计动机与指标定义：`doc/p08_calibration_eval_plan_2026-07-11.md`
- 测验档案：`doc/benchmark_profiles/p08_selfbuilt.md`、`doc/benchmark_profiles/p07_selfcheck.md`
- adapter 实现：`scripts/eval/benchmarks/p08_calibration.py`、`p07_selfcheck.py`
