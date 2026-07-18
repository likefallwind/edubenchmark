# mathtutorbench_socratic — 评测产物说明

> 由 `scripts/build_eval_readmes.py` 生成（审计快照 `_audit/audit_2026-07-16.jsonl`）。**不要手改**：改脚本后重跑。
> 综述档案（这个 benchmark 是什么，给人读）：[`doc/benchmark_profiles/mathtutorbench.md`](../../../doc/benchmark_profiles/mathtutorbench.md)
> 本文件是给“要用这个分数的人”读的操作性病历：**分数能不能用、哪里坏了、要不要重跑**。

## 一、健康状况（坏消息在前）

全部 run 干净。

headline 口径：best-match SacreBLEU（0-1）。

| 模型 | headline | 审计判决 | 判分/抽取失败率 | 未判分率 | 说明 |
| --- | --- | --- | --- | --- | --- |
| `MiniMax-M2.7` | 0.2131 | clean | 0.0% | 0.0% | — |
| `deepseek-v4-pro` | 0.2838 | clean | 0.0% | 0.0% | — |
| `glm-5.2` | 0.2976 | clean | 0.0% | 0.0% | — |
| `minimax3` | 0.2960 | clean | 0.0% | 0.0% | — |

## 二、这个评测是什么

**一句话**：MathTutorBench：苏格拉底式提问（生成引导问题）。

- **出处**：MathTutorBench 官方仓库。
- **数据**：1,319 条。
- **任务与判分**：官方指标 best-match SacreBLEU（0-1），规则判分。
- **adapter**：`scripts/eval/benchmarks/mathtutorbench.py`
- **局限**：BLEU 对措辞敏感，绝对值低是正常的，只做相对比较。

**怎么用**：

```bash
MODEL=<model> ./scripts/run_eval.sh mathtutorbench_socratic
# 或：python scripts/eval_benchmark.py --benchmark mathtutorbench_socratic --model <model> --limit 0
```

## 三、当前映射（M3 裁决相关）

| benchmark_weight | 能力（P:权重） |
| --- | --- |
| 0.6 | P13 个性化教学策略选择 (0.65)、P15 适配性解释与反馈生成 (0.35) |

---

审计脚本：`python scripts/audit_eval_artifacts.py --benchmark mathtutorbench_socratic --verbose`（离线、幂等、有 unusable 时退出码非 0）。
