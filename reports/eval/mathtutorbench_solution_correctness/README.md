# mathtutorbench_solution_correctness — 评测产物说明

> 由 `scripts/build_eval_readmes.py` 生成（审计快照 `_audit/audit_2026-07-16.jsonl`）。**不要手改**：改脚本后重跑。
> 综述档案（这个 benchmark 是什么，给人读）：[`doc/benchmark_profiles/mathtutorbench.md`](../../../doc/benchmark_profiles/mathtutorbench.md)
> 本文件是给“要用这个分数的人”读的操作性病历：**分数能不能用、哪里坏了、要不要重跑**。

## 一、健康状况（坏消息在前）

没有不可用的 run，但有 5 个带保留意见（caveat），引用时必须一并写出。

headline 口径：准确率（accuracy）。

| 模型 | headline | 审计判决 | 判分/抽取失败率 | 未判分率 | 说明 |
| --- | --- | --- | --- | --- | --- |
| `minimax3` | 0.8772 | caveat（可用，但必须带着下面的保留意见一起引用） | 0.1% | 0.0% | variance_restricted（low_variance）：跨模型均值 0.873 / 标准差 0.0142 |
| `MiniMax-M2.7` | 0.8663 | caveat（可用，但必须带着下面的保留意见一起引用） | 0.0% | 0.0% | variance_restricted（low_variance）：跨模型均值 0.873 / 标准差 0.0142 |
| `deepseek-v4-flash` | 0.8588 | caveat（可用，但必须带着下面的保留意见一起引用） | 0.0% | 0.0% | variance_restricted（low_variance）：跨模型均值 0.873 / 标准差 0.0142 |
| `deepseek-v4-pro` | 0.8638 | caveat（可用，但必须带着下面的保留意见一起引用） | 0.0% | 0.0% | variance_restricted（low_variance）：跨模型均值 0.873 / 标准差 0.0142 |
| `glm-5.2` | 0.8987 | caveat（可用，但必须带着下面的保留意见一起引用） | 0.0% | 0.0% | variance_restricted（low_variance）：跨模型均值 0.873 / 标准差 0.0142 |

### 区分度

`variance_restricted`（low_variance）：跨 5 个模型的 headline 均值 0.873、标准差 0.0142。口径与 13 号映射效度检查一致：**区分度受限的格子不得驱动映射裁决**。

## 二、这个评测是什么

**一句话**：MathTutorBench：判断学生解答对不对。

- **出处**：MathTutorBench 官方仓库。
- **数据**：1,002 条。
- **任务与判分**：二分类精确匹配。
- **adapter**：`scripts/eval/benchmarks/mathtutorbench.py`
- **局限**：-

**怎么用**：

```bash
MODEL=<model> ./scripts/run_eval.sh mathtutorbench_solution_correctness
# 或：python scripts/eval_benchmark.py --benchmark mathtutorbench_solution_correctness --model <model> --limit 0
```

## 三、当前映射（M3 裁决相关）

| evidence_tier | benchmark_weight | 能力（P:权重） |
| --- | --- | --- |
| education_core | 0.85 | P02 长上下文与证据定位 (0.15)、P07 自我校验与修正 (0.25)、P11 错误诊断 (0.6) |

---

审计脚本：`python scripts/audit_eval_artifacts.py --benchmark mathtutorbench_solution_correctness --verbose`（离线、幂等、有 unusable 时退出码非 0）。
