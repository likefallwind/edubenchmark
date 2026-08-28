# mathvista — 评测产物说明

> 由 `scripts/build_eval_readmes.py` 生成（审计快照 `_audit/audit_2026-08-28.jsonl`）。**不要手改**：改脚本后重跑。
> 综述档案（这个 benchmark 是什么，给人读）：[`doc/benchmark_profiles/mathvista.md`](../../../doc/benchmark_profiles/mathvista.md)
> 本文件是给“要用这个分数的人”读的操作性病历：**分数能不能用、哪里坏了、要不要重跑**。

## 一、健康状况（坏消息在前）

没有不可用的 run，但有 5 个带保留意见（caveat），引用时必须一并写出。

headline 口径：准确率（accuracy）。

| 模型 | headline | 审计判决 | 判分/抽取失败率 | 未判分率 | 说明 |
| --- | --- | --- | --- | --- | --- |
| `2026-06-06` | 0.8409 | caveat（可用，但必须带着下面的保留意见一起引用） | 1.1% | 0.7% | 1.1% 的题命中失败标记：判分/抽取失败；variance_restricted（low_variance）：跨模型均值 0.8528 / 标准差 0.0194 |
| `minimax3` | 0.8409 | caveat（可用，但必须带着下面的保留意见一起引用） | 1.1% | 0.7% | 1.1% 的题命中失败标记：判分/抽取失败；variance_restricted（low_variance）：跨模型均值 0.8528 / 标准差 0.0194 |
| `Qwen-Qwen3.8-27B` | 0.8610 | caveat（可用，但必须带着下面的保留意见一起引用） | 0.7% | 0.0% | 0.7% 的题命中失败标记：判分/抽取失败；variance_restricted（low_variance）：跨模型均值 0.8528 / 标准差 0.0194 |
| `Qwen-Qwen3.5-4B` | 0.8340 | caveat（可用，但必须带着下面的保留意见一起引用） | 0.5% | 0.0% | 0.5% 的题命中失败标记：判分/抽取失败；variance_restricted（low_variance）：跨模型均值 0.8528 / 标准差 0.0194 |
| `doubao-seed-2.0-pro` | 0.8870 | caveat（可用，但必须带着下面的保留意见一起引用） | 0.5% | 0.0% | 0.5% 的题命中失败标记：判分/抽取失败；variance_restricted（low_variance）：跨模型均值 0.8528 / 标准差 0.0194 |

### 区分度

`variance_restricted`（low_variance）：跨 5 个模型的 headline 均值 0.8528、标准差 0.0194。口径与 13 号映射效度检查一致：**区分度受限的格子不得驱动映射裁决**。

## 二、这个评测是什么

**一句话**：图文数学推理（图表/几何/函数图）。

- **出处**：MathVista 官方仓库。
- **数据**：1,000 题 testmini；图片需手动 `wget images.zip && unzip` 到 `sources/datasets/mathvista/data`。
- **任务与判分**：移植官方 few-shot 抽取（`ext_ans.demo_prompt`）+ `normalize_extracted_answer` + 最近选项编辑距离。
- **adapter**：`scripts/eval/benchmarks/mathvista.py`
- **局限**：需要视觉模型（`MiniMax-M3`，不是 M2.7）。

**怎么用**：

```bash
MODEL=<model> ./scripts/run_eval.sh mathvista
# 或：python scripts/eval_benchmark.py --benchmark mathvista --model <model> --limit 0
```

## 三、当前映射（M3 裁决相关）

| benchmark_weight | 能力（P:权重） |
| --- | --- |
| 1.0 | P03 多模态理解 (0.5)、P05 知识调用与掌握 (0.2)、P06 推理与生成 (0.5) |

---

审计脚本：`python scripts/audit_eval_artifacts.py --benchmark mathvista --verbose`（离线、幂等、有 unusable 时退出码非 0）。
