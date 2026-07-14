# k12vista — 评测产物说明

> 由 `scripts/build_eval_readmes.py` 生成（审计快照 `_audit/audit_2026-07-14.jsonl`）。**不要手改**：改脚本后重跑。
> 综述档案（这个 benchmark 是什么，给人读）：[`doc/benchmark_profiles/k12vista.md`](../../../doc/benchmark_profiles/k12vista.md)
> 本文件是给“要用这个分数的人”读的操作性病历：**分数能不能用、哪里坏了、要不要重跑**。

## 一、健康状况（坏消息在前）

**这个 benchmark 一次都没跑出产物。**

headline 口径：准确率（accuracy）。

| 模型 | headline | 审计判决 | 判分/抽取失败率 | 未判分率 | 说明 |
| --- | --- | --- | --- | --- | --- |
| `(no runs)` | — | no_artifacts（目录在，产物没有） | 0.0% | 0.0% | no summary.json and no scored.jsonl — nothing was produced |

## 二、这个评测是什么

**一句话**：3.3 万道中文 K12 图文学科题——P04（复杂多模态理解）的直接测量。

- **出处**：K12Vista。
- **数据**：尚未落地到本地产物。
- **任务与判分**：裁判打分，`unparsed` 记 0。
- **adapter**：`scripts/eval/benchmarks/k12vista.py`
- **局限**：**一次都没跑过**，adapter 就绪、产物为空。

**怎么用**：

```bash
MODEL=<model> ./scripts/run_eval.sh k12vista
# 或：python scripts/eval_benchmark.py --benchmark k12vista --model <model> --limit 0
```

## 三、当前映射（M3 裁决相关）

| evidence_tier | benchmark_weight | 能力（P:权重） |
| --- | --- | --- |
| diagnostic | 0.8 | P04 复杂多模态理解 (0.55)、P06 推理与生成 (0.3)、P05 知识调用与掌握 (0.15) |

---

审计脚本：`python scripts/audit_eval_artifacts.py --benchmark k12vista --verbose`（离线、幂等、有 unusable 时退出码非 0）。
