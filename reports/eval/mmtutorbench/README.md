# mmtutorbench — 评测产物说明

> 由 `scripts/build_eval_readmes.py` 生成（审计快照 `_audit/audit_2026-08-28.jsonl`）。**不要手改**：改脚本后重跑。
> 综述档案（这个 benchmark 是什么，给人读）：[`doc/benchmark_profiles/mmtutorbench.md`](../../../doc/benchmark_profiles/mmtutorbench.md)
> 本文件是给“要用这个分数的人”读的操作性病历：**分数能不能用、哪里坏了、要不要重跑**。

## 一、健康状况（坏消息在前）

没有不可用的 run，但有 1 个带保留意见（caveat），引用时必须一并写出。

headline 口径：六维 rubric 平均总分（0-6）。

| 模型 | headline | 审计判决 | 判分/抽取失败率 | 未判分率 | 说明 |
| --- | --- | --- | --- | --- | --- |
| `Qwen-Qwen3.5-4B` | 3.6609 | caveat（可用，但必须带着下面的保留意见一起引用） | 2.7% | 0.0% | 2.7% 的题命中失败标记：rubric 解析不全，总分记 None |
| `Qwen-Qwen3.8-27B` | 4.1170 | clean | 0.1% | 0.0% | — |
| `doubao-seed-2.0-pro` | 4.7675 | clean | 0.0% | 0.0% | — |
| `doubao-seed-2.0-pro` | 4.5584 | clean | 0.0% | 0.0% | — |
| `minimax3` | 3.5033 | clean | 0.0% | 0.1% | — |
| `minimax3` | 3.4447 | clean | 0.0% | 0.1% | — |

## 二、这个评测是什么

**一句话**：视频关键帧数学辅导：看图 + 学生提问 → 结构化辅导回复。

- **出处**：Tangchiu/mmtutorbench，770 行 / 1,414 张关键帧。
- **数据**：`fetch_eval_datasets.py --benchmark mmtutorbench`。
- **任务与判分**：固定 rubric 裁判 `MMTUTORBENCH_JUDGE_MODEL`（默认 MiniMax-M3）打 6 个二元维度，报 0-6 总分。
- **adapter**：`scripts/eval/benchmarks/mmtutorbench.py`
- **局限**：别默认跑全量 770；先 `LIMIT=5` 冒烟。

**怎么用**：

```bash
MODEL=<model> ./scripts/run_eval.sh mmtutorbench
# 或：python scripts/eval_benchmark.py --benchmark mmtutorbench --model <model> --limit 0
```

## 三、当前映射（M3 裁决相关）

| benchmark_weight | 能力（P:权重） |
| --- | --- |
| 0.85 | P03 多模态理解 (0.2)、P14 个性化教学策略选择 (0.2)、P16 适配性解释与反馈生成 (0.5) |

---

审计脚本：`python scripts/audit_eval_artifacts.py --benchmark mmtutorbench --verbose`（离线、幂等、有 unusable 时退出码非 0）。
