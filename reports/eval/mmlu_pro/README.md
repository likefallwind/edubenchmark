# mmlu_pro — 评测产物说明

> 由 `scripts/build_eval_readmes.py` 生成（审计快照 `_audit/audit_2026-07-16.jsonl`）。**不要手改**：改脚本后重跑。
> 综述档案（这个 benchmark 是什么，给人读）：[`doc/benchmark_profiles/mmlu_pro.md`](../../../doc/benchmark_profiles/mmlu_pro.md)
> 本文件是给“要用这个分数的人”读的操作性病历：**分数能不能用、哪里坏了、要不要重跑**。

## 一、健康状况（坏消息在前）

**这个 benchmark 下有 1 个 run 的分数不可用（unusable）。** 在重跑之前，不要把它们写进任何报告、聚合或映射裁决。

headline 口径：准确率（accuracy）。

| 模型 | headline | 审计判决 | 判分/抽取失败率 | 未判分率 | 说明 |
| --- | --- | --- | --- | --- | --- |
| `2026-06-07` | 0.8138 | **unusable**（分数是假的，必须重跑） | 0.0% | 74.6% | 74.6% 的题没进判分（分数建立在 3061/12032 的残缺样本上）；74.6% 的答题请求报错（上游限流/配额/参数错误）；产物数量对不上，最大缺口 74.6% |
| `doubao-seed-2.0-lite` | 1.0000 | caveat（可用，但必须带着下面的保留意见一起引用） | 0.0% | 0.0% | 冒烟样本（n=5），只能验管道，不能当分数 |
| `doubao-seed-2.0-pro` | 0.8000 | caveat（可用，但必须带着下面的保留意见一起引用） | 0.0% | 0.0% | 冒烟样本（n=5），只能验管道，不能当分数 |
| `glm-5.1` | 1.0000 | caveat（可用，但必须带着下面的保留意见一起引用） | 0.0% | 0.0% | 冒烟样本（n=5），只能验管道，不能当分数 |
| `gpt-5.5` | 1.0000 | caveat（可用，但必须带着下面的保留意见一起引用） | 0.0% | 0.0% | 冒烟样本（n=1），只能验管道，不能当分数 |
| `glm-5.2` | 0.8827 | clean | 0.1% | 1.3% | — |
| `deepseek-v4-pro` | 0.8741 | clean | 0.0% | 0.1% | — |
| `MiniMax-M2.7` | 0.8273 | clean | 0.0% | 0.1% | — |
| `deepseek-v4-flash` | 0.8591 | clean | 0.0% | 0.1% | — |
| `minimax3` | 0.8556 | clean | 0.0% | 0.0% | — |

### 样本残缺的 run

上游配额/限流打挂大批题目后，summary 仍在**幸存样本**上照常出分。这类 run 的分数没有“错”，但它测的是一个自选样本，不能跟全量 run 放在一张表里比。

- `2026-06-07`：只有 3061 / 12032 题进入判分（未判分 74.6%）。

## 二、这个评测是什么

**一句话**：MMLU 的高难升级版：10 选 1 学科知识题，测大学水平答题门槛。

- **出处**：TIGER-Lab/MMLU-Pro（公开镜像；TIGER-AI-Lab 那条路径是 gated）。
- **数据**：12,032 题，`fetch_eval_datasets.py --benchmark mmlu_pro`。
- **任务与判分**：官方 `answer is (X)` 正则先抽，抽不到才退回抽取 LLM；精确匹配选项字母。规则为主，裁判只是兜底。
- **adapter**：`scripts/eval/benchmarks/mmlu_pro.py`
- **局限**：门槛题（foundation_gate），只证明会答题，不证明会教。

**怎么用**：

```bash
MODEL=<model> ./scripts/run_eval.sh mmlu_pro
# 或：python scripts/eval_benchmark.py --benchmark mmlu_pro --model <model> --limit 0
```

## 三、当前映射（M3 裁决相关）

| evidence_tier | benchmark_weight | 能力（P:权重） |
| --- | --- | --- |
| foundation_gate | 0.35 | P01 指令与约束遵循 (0.1)、P05 知识调用与掌握 (0.6)、P06 推理与生成 (0.3) |

**这些 P 的证据因此受污染：P01、P05、P06**。裁决前先看 [`doc/eval_artifact_audit_2026-07-14.md`](../../../doc/eval_artifact_audit_2026-07-14.md)。

---

审计脚本：`python scripts/audit_eval_artifacts.py --benchmark mmlu_pro --verbose`（离线、幂等、有 unusable 时退出码非 0）。
