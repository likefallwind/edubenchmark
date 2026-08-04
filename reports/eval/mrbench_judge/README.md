# mrbench_judge — 评测产物说明

> 由 `scripts/build_eval_readmes.py` 生成（审计快照 `_audit/audit_2026-08-04.jsonl`）。**不要手改**：改脚本后重跑。
> 综述档案（这个 benchmark 是什么，给人读）：[`doc/benchmark_profiles/mrbench.md`](../../../doc/benchmark_profiles/mrbench.md)
> 本文件是给“要用这个分数的人”读的操作性病历：**分数能不能用、哪里坏了、要不要重跑**。

## 一、健康状况（坏消息在前）

全部 run 干净。

headline 口径：跟人类金标的整体一致率。

| 模型 | headline | 审计判决 | 判分/抽取失败率 | 未判分率 | 说明 |
| --- | --- | --- | --- | --- | --- |
| `MiniMax-M2.7` | 0.7008 | clean | 0.0% | 0.0% | — |
| `deepseek-v3.2` | 0.5149 | clean | 0.0% | 0.0% | — |
| `deepseek-v4-flash` | 0.7014 | clean | 0.0% | 0.0% | — |
| `deepseek-v4-pro` | 0.7190 | clean | 0.0% | 0.0% | — |
| `glm-5.2` | 0.7086 | clean | 0.0% | 0.0% | — |
| `minimax3` | 0.6529 | clean | 0.0% | 0.0% | — |

## 二、这个评测是什么

**一句话**：MRBench Step 1：被测模型**当裁判**，给 tutor 回复贴 8 维标签，跟人类金标比一致性。

- **出处**：kaushal0494/UnifyingAITutorEvaluation（NAACL 2025），`MRBench_V2.json`。
- **数据**：200 段对话 × 至多 9 个模型回复 × 维度 = 13,240 条。
- **任务与判分**：被测模型自己出标签，本地跟人类金标比：每维 agreement + macro-F1 + Cohen's kappa。**没有第三方裁判**——unparsed 是被测模型的行为，不是管道故障。
- **adapter**：`scripts/eval/benchmarks/mrbench.py`
- **局限**：映射里是 `excluded_judge_task`（weight 0.0），只用来选裁判，不进能力雷达。

**怎么用**：

```bash
MODEL=<model> ./scripts/run_eval.sh mrbench_judge
# 或：python scripts/eval_benchmark.py --benchmark mrbench_judge --model <model> --limit 0
```

## 三、当前映射（M3 裁决相关）

| benchmark_weight | 能力（P:权重） |
| --- | --- |
| 1.0 | P11 主观题评价能力 (0.5) |

---

审计脚本：`python scripts/audit_eval_artifacts.py --benchmark mrbench_judge --verbose`（离线、幂等、有 unusable 时退出码非 0）。
