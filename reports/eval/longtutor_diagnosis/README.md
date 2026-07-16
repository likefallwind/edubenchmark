# longtutor_diagnosis — 评测产物说明

> 由 `scripts/build_eval_readmes.py` 生成（审计快照 `_audit/audit_2026-07-16.jsonl`）。**不要手改**：改脚本后重跑。
> 综述档案（这个 benchmark 是什么，给人读）：（暂无档案；本文件的“这个评测是什么”一节即是权威描述，事实来源是 adapter 源码与 AGENTS.md）
> 本文件是给“要用这个分数的人”读的操作性病历：**分数能不能用、哪里坏了、要不要重跑**。

## 一、健康状况（坏消息在前）

全部 run 干净。

headline 口径：准确率（accuracy）。

| 模型 | headline | 审计判决 | 判分/抽取失败率 | 未判分率 | 说明 |
| --- | --- | --- | --- | --- | --- |
| `glm-5.2` | 0.3497 | clean | 1.6% | 0.0% | 1.6% 的题命中失败标记：回复匹配到 0 个或多个诊断标签 |
| `deepseek-v4-pro` | 0.4366 | clean | 0.0% | 0.0% | — |
| `minimax3` | 0.4156 | clean | 0.0% | 0.0% | — |

## 二、这个评测是什么

**一句话**：LongTutor 任务二：根据长历史把当前错误归到四类知识状态。

- **出处**：LongTutor 上游发布（无 LICENSE，勿再分发数据）；见 AGENTS.md 的 LongTutor 段。
- **数据**：1,001 条，`prepare_longtutor.py` 重建历史特征后与人工金标 join。
- **任务与判分**：**纯本地字符串匹配**，无裁判；主指标 Macro-F1，accuracy 辅助。回复里匹配到 0 个或 >1 个标签记 `NO_LABEL`。
- **adapter**：`scripts/eval/benchmarks/longtutor.py`
- **局限**：离线长历史重放，不代表真实长期学习增益；三个 LongTutor 任务不许平均成一个分。

**怎么用**：

```bash
MODEL=<model> ./scripts/run_eval.sh longtutor_diagnosis
# 或：python scripts/eval_benchmark.py --benchmark longtutor_diagnosis --model <model> --limit 0
```

## 三、当前映射（M3 裁决相关）

| evidence_tier | benchmark_weight | 能力（P:权重） |
| --- | --- | --- |
| diagnostic | 0.75 | P11 错误诊断 (0.1)、P16 学习者画像建模 (0.3) |

---

审计脚本：`python scripts/audit_eval_artifacts.py --benchmark longtutor_diagnosis --verbose`（离线、幂等、有 unusable 时退出码非 0）。
