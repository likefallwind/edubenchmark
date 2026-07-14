# mmtutorbench_judge_calibration — 评测产物说明

> 由 `scripts/build_eval_readmes.py` 生成（审计快照 `_audit/audit_2026-07-14.jsonl`）。**不要手改**：改脚本后重跑。
> 综述档案（这个 benchmark 是什么，给人读）：[`doc/benchmark_profiles/mmtutorbench.md`](../../../doc/benchmark_profiles/mmtutorbench.md)
> 本文件是给“要用这个分数的人”读的操作性病历：**分数能不能用、哪里坏了、要不要重跑**。

## 一、健康状况（坏消息在前）

**这个 benchmark 一次都没跑出产物。**

headline 口径：准确率（accuracy）。

| 模型 | headline | 审计判决 | 判分/抽取失败率 | 未判分率 | 说明 |
| --- | --- | --- | --- | --- | --- |
| `minimax3` | — | no_artifacts（目录在，产物没有） | 0.0% | 0.0% | adapter declares status=not_run: no public per-item human/expert gold scores found in MMTutorBench JSONL — honest hook, no score to trust or distrust |

## 二、这个评测是什么

**一句话**：MMTutorBench 裁判校准——**只是个钩子**：公开 JSONL 没有逐题人工金标，所以它输出 status 而不是编分数。

- **出处**：Tangchiu/mmtutorbench。
- **数据**：无（没有人工金标）。
- **任务与判分**：`extra_metrics.status = not_run`。
- **adapter**：`scripts/eval/benchmarks/mmtutorbench.py`
- **局限**：这是诚实的空钩子，不是故障。

**怎么用**：

```bash
MODEL=<model> ./scripts/run_eval.sh mmtutorbench_judge_calibration
# 或：python scripts/eval_benchmark.py --benchmark mmtutorbench_judge_calibration --model <model> --limit 0
```

## 三、当前映射（M3 裁决相关）

`reports/atomic_ability_rebenchmark_2026-07-08/02_benchmark_ability_mapping.jsonl` 里没有这个 benchmark 的条目——它当前**不进能力雷达**。

---

审计脚本：`python scripts/audit_eval_artifacts.py --benchmark mmtutorbench_judge_calibration --verbose`（离线、幂等、有 unusable 时退出码非 0）。
