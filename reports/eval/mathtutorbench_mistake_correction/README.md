# mathtutorbench_mistake_correction — 评测产物说明

> 由 `scripts/build_eval_readmes.py` 生成（审计快照 `_audit/audit_2026-08-04.jsonl`）。**不要手改**：改脚本后重跑。
> 综述档案（这个 benchmark 是什么，给人读）：[`doc/benchmark_profiles/mathtutorbench.md`](../../../doc/benchmark_profiles/mathtutorbench.md)
> 本文件是给“要用这个分数的人”读的操作性病历：**分数能不能用、哪里坏了、要不要重跑**。

## 一、健康状况（坏消息在前）

全部 run 干净。

headline 口径：准确率（accuracy）。

| 模型 | headline | 审计判决 | 判分/抽取失败率 | 未判分率 | 说明 |
| --- | --- | --- | --- | --- | --- |
| `glm-5.2` | 0.9371 | clean | 0.1% | 0.1% | — |
| `MiniMax-M2.7` | 0.8603 | clean | 0.0% | 0.0% | — |
| `deepseek-v4-flash` | 0.9172 | clean | 0.0% | 0.0% | — |
| `deepseek-v4-pro` | 0.9202 | clean | 0.0% | 0.0% | — |
| `minimax3` | 0.8733 | clean | 0.0% | 0.0% | — |

## 二、这个评测是什么

**一句话**：MathTutorBench：把学生的错解改对。

- **出处**：MathTutorBench 官方仓库。
- **数据**：1,002 条。
- **任务与判分**：数值精确匹配。
- **adapter**：`scripts/eval/benchmarks/mathtutorbench.py`
- **局限**：-

**怎么用**：

```bash
MODEL=<model> ./scripts/run_eval.sh mathtutorbench_mistake_correction
# 或：python scripts/eval_benchmark.py --benchmark mathtutorbench_mistake_correction --model <model> --limit 0
```

## 三、当前映射（M3 裁决相关）

| benchmark_weight | 能力（P:权重） |
| --- | --- |
| 1.0 | P06 推理与生成 (0.2)、P10 错误诊断 (0.2)、P16 适配性解释与反馈生成 (0.2) |

---

审计脚本：`python scripts/audit_eval_artifacts.py --benchmark mathtutorbench_mistake_correction --verbose`（离线、幂等、有 unusable 时退出码非 0）。
