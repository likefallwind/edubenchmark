# p08_abstention — 评测产物说明

> 由 `scripts/build_eval_readmes.py` 生成（审计快照 `_audit/audit_2026-07-16.jsonl`）。**不要手改**：改脚本后重跑。
> 综述档案（这个 benchmark 是什么，给人读）：[`doc/benchmark_profiles/p08_selfbuilt.md`](../../../doc/benchmark_profiles/p08_selfbuilt.md)
> 本文件是给“要用这个分数的人”读的操作性病历：**分数能不能用、哪里坏了、要不要重跑**。

## 一、健康状况（坏消息在前）

全部 run 干净。

headline 口径：准确率（accuracy）。

| 模型 | headline | 审计判决 | 判分/抽取失败率 | 未判分率 | 说明 |
| --- | --- | --- | --- | --- | --- |
| `MiniMax-M2.7` | 0.8380 | clean | 0.0% | 0.0% | — |
| `deepseek-v4-pro` | 0.8920 | clean | 0.0% | 0.0% | — |
| `doubao-seed-2.0-pro` | 0.8860 | clean | 0.0% | 0.0% | — |
| `glm-5.2` | 0.8960 | clean | 0.0% | 0.0% | — |
| `minimax3` | 0.8520 | clean | 0.0% | 0.0% | — |

## 二、这个评测是什么

**一句话**：UMWP 不可答数学题 + 可答对照，测“不会的题敢不敢说不会”。

- **出处**：UMWP（Yuki-Asuuna/UMWP）。
- **数据**：500 题（250 不可答 + 250 可答）。
- **任务与判分**：**规则判分**：不可答题上弃答算对，可答题上答对算对。
- **adapter**：`scripts/eval/benchmarks/p08_abstention.py`
- **局限**：-

**怎么用**：

```bash
MODEL=<model> ./scripts/run_eval.sh p08_abstention
# 或：python scripts/eval_benchmark.py --benchmark p08_abstention --model <model> --limit 0
```

## 三、当前映射（M3 裁决相关）

| benchmark_weight | 能力（P:权重） |
| --- | --- |
| 0.85 | P08 置信度校准与弃答 (0.8) |

---

审计脚本：`python scripts/audit_eval_artifacts.py --benchmark p08_abstention --verbose`（离线、幂等、有 unusable 时退出码非 0）。
