# bea2025_judge — 评测产物说明

> 由 `scripts/build_eval_readmes.py` 生成（审计快照 `_audit/audit_2026-07-14.jsonl`）。**不要手改**：改脚本后重跑。
> 综述档案（这个 benchmark 是什么，给人读）：[`doc/benchmark_profiles/bea2025.md`](../../../doc/benchmark_profiles/bea2025.md)
> 本文件是给“要用这个分数的人”读的操作性病历：**分数能不能用、哪里坏了、要不要重跑**。

## 一、健康状况（坏消息在前）

全部 run 干净。

headline 口径：recommended_judge_score = 四维 exact macro-F1 均值。

| 模型 | headline | 审计判决 | 判分/抽取失败率 | 未判分率 | 说明 |
| --- | --- | --- | --- | --- | --- |
| `MiniMax-M2.7` | 0.4960 | clean | 0.0% | 0.0% | — |
| `deepseek-v3.2` | 0.3687 | clean | 0.0% | 0.0% | — |
| `deepseek-v4-flash` | 0.5139 | clean | 0.0% | 0.0% | — |
| `deepseek-v4-pro` | 0.5374 | clean | 0.0% | 0.0% | — |
| `glm-5.2` | 0.5488 | clean | 0.0% | 0.0% | — |
| `minimax3` | 0.5122 | clean | 0.0% | 0.1% | — |

## 二、这个评测是什么

**一句话**：BEA 2025 共享任务 Step 1：被测模型当裁判，给 dev 集 tutor 回复贴 4 维标签。

- **出处**：SIGEDU BEA 2025 官方任务 + `BEA_Shared_Task_2025_Datasets/mrbench_v3_devset.json`。
- **数据**：dev 集 9,904 条（(回复 × 维度) 一条）；test 标签官方隐藏。
- **任务与判分**：跟人类标注比 exact / lenient accuracy + macro-F1 + kappa；`recommended_judge_score` = 4 维 exact macro-F1 均值。
- **adapter**：`scripts/eval/benchmarks/bea2025.py`
- **局限**：本地 dev 打分，**不等于官方榜**；映射里 weight 0.0。

**怎么用**：

```bash
MODEL=<model> ./scripts/run_eval.sh bea2025_judge
# 或：python scripts/eval_benchmark.py --benchmark bea2025_judge --model <model> --limit 0
```

## 三、当前映射（M3 裁决相关）

| evidence_tier | benchmark_weight | 能力（P:权重） |
| --- | --- | --- |
| excluded_judge_task | 0.0 | P14 Rubric 映射评分 (0.45)、P13 错因归因 (0.3)、P11 作答正误判定 (0.25) |

---

审计脚本：`python scripts/audit_eval_artifacts.py --benchmark bea2025_judge --verbose`（离线、幂等、有 unusable 时退出码非 0）。
