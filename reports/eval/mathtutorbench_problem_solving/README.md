# mathtutorbench_problem_solving — 评测产物说明

> 由 `scripts/build_eval_readmes.py` 生成（审计快照 `_audit/audit_2026-07-16.jsonl`）。**不要手改**：改脚本后重跑。
> 综述档案（这个 benchmark 是什么，给人读）：[`doc/benchmark_profiles/mathtutorbench.md`](../../../doc/benchmark_profiles/mathtutorbench.md)
> 本文件是给“要用这个分数的人”读的操作性病历：**分数能不能用、哪里坏了、要不要重跑**。

## 一、健康状况（坏消息在前）

没有不可用的 run，但有 4 个带保留意见（caveat），引用时必须一并写出。

headline 口径：准确率（accuracy）。

| 模型 | headline | 审计判决 | 判分/抽取失败率 | 未判分率 | 说明 |
| --- | --- | --- | --- | --- | --- |
| `MiniMax-M2.7` | 0.9545 | caveat（可用，但必须带着下面的保留意见一起引用） | 0.0% | 0.0% | variance_restricted（ceiling+low_variance）：跨模型均值 0.9704 / 标准差 0.0096 |
| `deepseek-v4-flash` | 0.9742 | caveat（可用，但必须带着下面的保留意见一起引用） | 0.0% | 0.0% | variance_restricted（ceiling+low_variance）：跨模型均值 0.9704 / 标准差 0.0096 |
| `glm-5.2` | 0.9803 | caveat（可用，但必须带着下面的保留意见一起引用） | 0.0% | 0.0% | variance_restricted（ceiling+low_variance）：跨模型均值 0.9704 / 标准差 0.0096 |
| `minimax3` | 0.9727 | caveat（可用，但必须带着下面的保留意见一起引用） | 0.0% | 0.0% | variance_restricted（ceiling+low_variance）：跨模型均值 0.9704 / 标准差 0.0096 |

### 区分度

`variance_restricted`（ceiling+low_variance）：跨 4 个模型的 headline 均值 0.9704、标准差 0.0096。口径与 13 号映射效度检查一致：**区分度受限的格子不得驱动映射裁决**。

## 二、这个评测是什么

**一句话**：MathTutorBench：会不会做题（GSM8K 风格，门槛项）。

- **出处**：MathTutorBench 官方仓库。
- **数据**：1,319 题。
- **任务与判分**：数值精确匹配，抽取 LLM 仅兜底。
- **adapter**：`scripts/eval/benchmarks/mathtutorbench.py`
- **局限**：已接近天花板，区分不了模型。

**怎么用**：

```bash
MODEL=<model> ./scripts/run_eval.sh mathtutorbench_problem_solving
# 或：python scripts/eval_benchmark.py --benchmark mathtutorbench_problem_solving --model <model> --limit 0
```

## 三、当前映射（M3 裁决相关）

| benchmark_weight | 能力（P:权重） |
| --- | --- |
| 0.45 | P04 知识调用与掌握 (0.3)、P05 推理与生成 (0.6)、P06 自我校验与修正 (0.1) |

---

审计脚本：`python scripts/audit_eval_artifacts.py --benchmark mathtutorbench_problem_solving --verbose`（离线、幂等、有 unusable 时退出码非 0）。
