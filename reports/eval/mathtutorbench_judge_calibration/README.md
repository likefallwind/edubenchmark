# mathtutorbench_judge_calibration — 评测产物说明

> 由 `scripts/build_eval_readmes.py` 生成（审计快照 `_audit/audit_2026-08-28.jsonl`）。**不要手改**：改脚本后重跑。
> 综述档案（这个 benchmark 是什么，给人读）：[`doc/benchmark_profiles/mathtutorbench.md`](../../../doc/benchmark_profiles/mathtutorbench.md)
> 本文件是给“要用这个分数的人”读的操作性病历：**分数能不能用、哪里坏了、要不要重跑**。

## 一、健康状况（坏消息在前）

没有不可用的 run，但有 9 个带保留意见（caveat），引用时必须一并写出。

headline 口径：准确率（accuracy）。

| 模型 | headline | 审计判决 | 判分/抽取失败率 | 未判分率 | 说明 |
| --- | --- | --- | --- | --- | --- |
| `MiniMax-M2.7` | 0.8102 | caveat（可用，但必须带着下面的保留意见一起引用） | 0.0% | 0.0% | variance_restricted（low_variance）：跨模型均值 0.8284 / 标准差 0.0111 |
| `Qwen-Qwen3.5-4B` | 0.8174 | caveat（可用，但必须带着下面的保留意见一起引用） | 0.0% | 0.0% | variance_restricted（low_variance）：跨模型均值 0.8284 / 标准差 0.0111 |
| `Qwen-Qwen3.8-27B` | 0.8382 | caveat（可用，但必须带着下面的保留意见一起引用） | 0.0% | 0.0% | variance_restricted（low_variance）：跨模型均值 0.8284 / 标准差 0.0111 |
| `deepseek-v3.2` | 0.8361 | caveat（可用，但必须带着下面的保留意见一起引用） | 0.0% | 0.0% | variance_restricted（low_variance）：跨模型均值 0.8284 / 标准差 0.0111 |
| `deepseek-v4-flash` | 0.8257 | caveat（可用，但必须带着下面的保留意见一起引用） | 0.0% | 0.0% | variance_restricted（low_variance）：跨模型均值 0.8284 / 标准差 0.0111 |
| `deepseek-v4-pro` | 0.8174 | caveat（可用，但必须带着下面的保留意见一起引用） | 0.0% | 0.0% | variance_restricted（low_variance）：跨模型均值 0.8284 / 标准差 0.0111 |
| `doubao-seed-2.0-pro` | 0.8268 | caveat（可用，但必须带着下面的保留意见一起引用） | 0.0% | 0.0% | variance_restricted（low_variance）：跨模型均值 0.8284 / 标准差 0.0111 |
| `glm-5.2` | 0.8392 | caveat（可用，但必须带着下面的保留意见一起引用） | 0.0% | 0.0% | variance_restricted（low_variance）：跨模型均值 0.8284 / 标准差 0.0111 |
| `minimax3` | 0.8444 | caveat（可用，但必须带着下面的保留意见一起引用） | 0.0% | 0.0% | variance_restricted（low_variance）：跨模型均值 0.8284 / 标准差 0.0111 |

### 区分度

`variance_restricted`（low_variance）：跨 9 个模型的 headline 均值 0.8284、标准差 0.0111。口径与 13 号映射效度检查一致：**区分度受限的格子不得驱动映射裁决**。

## 二、这个评测是什么

**一句话**：MathTutorBench：裁判校准——被测模型在专家成对偏好上跟不跟得上人。

- **出处**：MathTutorBench 官方仓库。
- **数据**：成对样本，两个顺序各一条。
- **任务与判分**：跟专家 positive 的一致率 + 位置一致性。被测模型即裁判。
- **adapter**：`scripts/eval/benchmarks/mathtutorbench.py`
- **局限**：选裁判用，不进能力雷达。

**怎么用**：

```bash
MODEL=<model> ./scripts/run_eval.sh mathtutorbench_judge_calibration
# 或：python scripts/eval_benchmark.py --benchmark mathtutorbench_judge_calibration --model <model> --limit 0
```

## 三、当前映射（M3 裁决相关）

`reports/atomic_ability_rebenchmark/02_benchmark_ability_mapping.jsonl` 里没有这个 benchmark 的条目——它当前**不进能力雷达**。

---

审计脚本：`python scripts/audit_eval_artifacts.py --benchmark mathtutorbench_judge_calibration --verbose`（离线、幂等、有 unusable 时退出码非 0）。
