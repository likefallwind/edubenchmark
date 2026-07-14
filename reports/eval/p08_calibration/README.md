# p08_calibration — 评测产物说明

> 由 `scripts/build_eval_readmes.py` 生成（审计快照 `_audit/audit_2026-07-14.jsonl`）。**不要手改**：改脚本后重跑。
> 综述档案（这个 benchmark 是什么，给人读）：[`doc/benchmark_profiles/p08_selfbuilt.md`](../../../doc/benchmark_profiles/p08_selfbuilt.md)
> 本文件是给“要用这个分数的人”读的操作性病历：**分数能不能用、哪里坏了、要不要重跑**。

## 一、健康状况（坏消息在前）

全部 run 干净。

headline 口径：准确率（accuracy）。

| 模型 | headline | 审计判决 | 判分/抽取失败率 | 未判分率 | 说明 |
| --- | --- | --- | --- | --- | --- |
| `minimax3` | 0.5873 | clean | 0.9% | 0.0% | 0.9% 的题命中失败标记：置信度没解析出来，该题被踢出校准指标 |
| `MiniMax-M2.7` | 0.4909 | clean | 0.7% | 0.0% | 0.7% 的题命中失败标记：置信度没解析出来，该题被踢出校准指标 |
| `deepseek-v4-pro` | 0.6812 | clean | 0.0% | 0.2% | — |
| `doubao-seed-2.0-pro` | 0.6964 | clean | 0.0% | 0.0% | — |
| `glm-5.2` | 0.6673 | clean | 0.0% | 0.0% | — |

## 二、这个评测是什么

**一句话**：答题时要求同时给 0-100 置信度，测“自信地教错”有多少——P08 的直接测量。

- **出处**：自建，题单 `data/p08_calibration/item_list_v1.txt`。
- **数据**：550 题。
- **任务与判分**：delegate 判对错 + 解析置信度；报 ECE / CWR（高置信错答率）等。置信度解析不出来的题从校准指标里剔除并单独报 `confidence_unparsed_rate`（>10% 会自动打警告）。
- **adapter**：`scripts/eval/benchmarks/p08_calibration.py`
- **局限**：-

**怎么用**：

```bash
MODEL=<model> ./scripts/run_eval.sh p08_calibration
# 或：python scripts/eval_benchmark.py --benchmark p08_calibration --model <model> --limit 0
```

## 三、当前映射（M3 裁决相关）

| evidence_tier | benchmark_weight | 能力（P:权重） |
| --- | --- | --- |
| diagnostic | 0.85 | P08 置信度校准与弃答 (0.8)、P07 自我校验与修正 (0.2) |

---

审计脚本：`python scripts/audit_eval_artifacts.py --benchmark p08_calibration --verbose`（离线、幂等、有 unusable 时退出码非 0）。
