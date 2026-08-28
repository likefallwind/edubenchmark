# mooccube_prereq — 评测产物说明

> 由 `scripts/build_eval_readmes.py` 生成（审计快照 `_audit/audit_2026-08-28.jsonl`）。**不要手改**：改脚本后重跑。
> 综述档案（这个 benchmark 是什么，给人读）：[`doc/benchmark_profiles/mooccube.md`](../../../doc/benchmark_profiles/mooccube.md)
> 本文件是给“要用这个分数的人”读的操作性病历：**分数能不能用、哪里坏了、要不要重跑**。

## 一、健康状况（坏消息在前）

全部 run 干净。

headline 口径：准确率（accuracy）。

| 模型 | headline | 审计判决 | 判分/抽取失败率 | 未判分率 | 说明 |
| --- | --- | --- | --- | --- | --- |
| `MiniMax-M2.7` | 0.6000 | clean | 0.0% | 0.0% | — |
| `Qwen-Qwen3.5-4B` | 0.2633 | clean | 0.0% | 0.0% | — |
| `Qwen-Qwen3.8-27B` | 0.5800 | clean | 0.0% | 0.0% | — |
| `deepseek-v4-pro` | 0.5267 | clean | 0.0% | 0.0% | — |
| `doubao-seed-2.0-pro` | 0.5800 | clean | 0.0% | 0.0% | — |
| `glm-5.2` | 0.5333 | clean | 0.0% | 0.0% | — |
| `minimax3` | 0.5767 | clean | 0.0% | 0.0% | — |

## 二、这个评测是什么

**一句话**：拿学堂在线知识图谱的 905 条专家先修边当金标，自建先修选择 + 学习顺序排序题——P19 的直接测量。

- **出处**：MOOCCube（自建题）。
- **数据**：自建。
- **任务与判分**：**100% 规则判分、零裁判**。
- **adapter**：`scripts/eval/benchmarks/mooccube_prereq.py`
- **局限**：只覆盖“知识结构”那一半路径规划；**目前没有任何跑完的产物**。

**怎么用**：

```bash
MODEL=<model> ./scripts/run_eval.sh mooccube_prereq
# 或：python scripts/eval_benchmark.py --benchmark mooccube_prereq --model <model> --limit 0
```

## 三、当前映射（M3 裁决相关）

| benchmark_weight | 能力（P:权重） |
| --- | --- |
| 0.85 | P15 学习路径规划（知识结构层） (0.8) |

---

审计脚本：`python scripts/audit_eval_artifacts.py --benchmark mooccube_prereq --verbose`（离线、幂等、有 unusable 时退出码非 0）。
