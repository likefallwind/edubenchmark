# mmtutorbench — 评测产物说明

> 由 `scripts/build_eval_readmes.py` 生成（审计快照 `_audit/audit_2026-07-16.jsonl`）。**不要手改**：改脚本后重跑。
> 综述档案（这个 benchmark 是什么，给人读）：[`doc/benchmark_profiles/mmtutorbench.md`](../../../doc/benchmark_profiles/mmtutorbench.md)
> 本文件是给“要用这个分数的人”读的操作性病历：**分数能不能用、哪里坏了、要不要重跑**。

## 一、健康状况（坏消息在前）

**这个 benchmark 下有 1 个 run 的分数不可用（unusable）。** 在重跑之前，不要把它们写进任何报告、聚合或映射裁决。

headline 口径：六维 rubric 平均总分（0-6）。

| 模型 | headline | 审计判决 | 判分/抽取失败率 | 未判分率 | 说明 |
| --- | --- | --- | --- | --- | --- |
| `minimax3` | 4.0000 | **unusable**（分数是假的，必须重跑） | 0.0% | 0.0% | 产物数量对不上，最大缺口 14000.0%；summary.json 比产物旧：盘上的分数跟盘上的数据对不上；一小时内还在写盘，疑似仍在跑，当前 summary 只是中间值；冒烟样本（n=5），只能验管道，不能当分数 |

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

**这些 P 的证据因此受污染：P03、P14、P16**。裁决前先看 [`doc/eval_artifact_audit_2026-07-14.md`](../../../doc/eval_artifact_audit_2026-07-14.md)。

---

审计脚本：`python scripts/audit_eval_artifacts.py --benchmark mmtutorbench --verbose`（离线、幂等、有 unusable 时退出码非 0）。
