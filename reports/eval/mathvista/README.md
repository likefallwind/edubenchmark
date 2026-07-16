# mathvista — 评测产物说明

> 由 `scripts/build_eval_readmes.py` 生成（审计快照 `_audit/audit_2026-07-16.jsonl`）。**不要手改**：改脚本后重跑。
> 综述档案（这个 benchmark 是什么，给人读）：[`doc/benchmark_profiles/mathvista.md`](../../../doc/benchmark_profiles/mathvista.md)
> 本文件是给“要用这个分数的人”读的操作性病历：**分数能不能用、哪里坏了、要不要重跑**。

## 一、健康状况（坏消息在前）

全部 run 干净。

headline 口径：准确率（accuracy）。

| 模型 | headline | 审计判决 | 判分/抽取失败率 | 未判分率 | 说明 |
| --- | --- | --- | --- | --- | --- |
| `2026-06-06` | 0.8409 | clean | 0.1% | 0.7% | — |
| `minimax3` | 0.8409 | clean | 0.1% | 0.7% | — |

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

| evidence_tier | benchmark_weight | 能力（P:权重） |
| --- | --- | --- |
| diagnostic | 0.7 | P03 多模态理解 (0.35)、P05 知识调用与掌握 (0.2)、P06 推理与生成 (0.45) |

---

审计脚本：`python scripts/audit_eval_artifacts.py --benchmark mathvista --verbose`（离线、幂等、有 unusable 时退出码非 0）。
