# ceval — 评测产物说明

> 由 `scripts/build_eval_readmes.py` 生成（审计快照 `_audit/audit_2026-07-14.jsonl`）。**不要手改**：改脚本后重跑。
> 综述档案（这个 benchmark 是什么，给人读）：[`doc/benchmark_profiles/ceval.md`](../../../doc/benchmark_profiles/ceval.md)
> 本文件是给“要用这个分数的人”读的操作性病历：**分数能不能用、哪里坏了、要不要重跑**。

## 一、健康状况（坏消息在前）

没有不可用的 run，但有 1 个带保留意见（caveat），引用时必须一并写出。

headline 口径：准确率（accuracy）。

| 模型 | headline | 审计判决 | 判分/抽取失败率 | 未判分率 | 说明 |
| --- | --- | --- | --- | --- | --- |
| `glm-5.1` | 1.0000 | caveat（可用，但必须带着下面的保留意见一起引用） | 0.0% | 0.0% | 冒烟样本（n=5），只能验管道，不能当分数 |
| `MiniMax-M2.7` | 0.8744 | clean | 0.0% | 0.0% | — |
| `deepseek-v4-flash` | 0.9219 | clean | 0.0% | 0.1% | — |
| `deepseek-v4-pro` | 0.9383 | clean | 0.0% | 0.0% | — |
| `glm-5.2` | 0.9375 | clean | 0.0% | 0.1% | — |
| `minimax3` | 0.8834 | clean | 0.0% | 0.0% | — |

## 二、这个评测是什么

**一句话**：中文 52 学科考试选择题，四个难度层。

- **出处**：ceval/ceval-exam。
- **数据**：val 分割 1,346 题（官方 test 不给答案）；每学科 5 条 dev 样例做 5-shot。
- **任务与判分**：官方 5-shot answer-only 协议：**无抽取 LLM**，读回复首字母精确匹配，跟官方 `response[0] == answer` 一致。
- **adapter**：`scripts/eval/benchmarks/ceval.py`
- **局限**：门槛题；中文知识面，不测教学。

**怎么用**：

```bash
MODEL=<model> ./scripts/run_eval.sh ceval
# 或：python scripts/eval_benchmark.py --benchmark ceval --model <model> --limit 0
```

## 三、当前映射（M3 裁决相关）

| evidence_tier | benchmark_weight | 能力（P:权重） |
| --- | --- | --- |
| foundation_gate | 0.35 | P05 知识调用与掌握 (0.6)、P06 推理与生成 (0.25)、P01 指令与约束遵循 (0.15) |

---

审计脚本：`python scripts/audit_eval_artifacts.py --benchmark ceval --verbose`（离线、幂等、有 unusable 时退出码非 0）。
