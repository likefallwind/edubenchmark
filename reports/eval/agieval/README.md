# agieval — 评测产物说明

> 由 `scripts/build_eval_readmes.py` 生成（审计快照 `_audit/audit_2026-07-14.jsonl`）。**不要手改**：改脚本后重跑。
> 综述档案（这个 benchmark 是什么，给人读）：[`doc/benchmark_profiles/agieval.md`](../../../doc/benchmark_profiles/agieval.md)
> 本文件是给“要用这个分数的人”读的操作性病历：**分数能不能用、哪里坏了、要不要重跑**。

## 一、健康状况（坏消息在前）

**这个 benchmark 下有 1 个 run 的分数不可用（unusable）。** 在重跑之前，不要把它们写进任何报告、聚合或映射裁决。

headline 口径：准确率（accuracy）。

| 模型 | headline | 审计判决 | 判分/抽取失败率 | 未判分率 | 说明 |
| --- | --- | --- | --- | --- | --- |
| `2026-06-08` | — | **unusable**（分数是假的，必须重跑） | 0.0% | 100.0% | 100.0% 的题没进判分（分数建立在 0/7272 的残缺样本上）；100.0% 的答题请求报错（上游限流/配额/参数错误） |
| `MiniMax-M2.7` | 0.8112 | caveat（可用，但必须带着下面的保留意见一起引用） | 0.0% | 0.1% | 产物数量对不上，最大缺口 18.2%；summary.json 比产物旧：盘上的分数跟盘上的数据对不上 |
| `glm-5.2` | 0.9055 | clean | 0.0% | 0.7% | — |
| `deepseek-v4-pro` | 0.9020 | clean | 0.0% | 0.0% | — |
| `deepseek-v4-flash` | 0.8937 | clean | 0.0% | 0.0% | — |
| `minimax3` | 0.8561 | clean | 0.0% | 0.1% | — |

### 样本残缺的 run

上游配额/限流打挂大批题目后，summary 仍在**幸存样本**上照常出分。这类 run 的分数没有“错”，但它测的是一个自选样本，不能跟全量 run 放在一张表里比。

- `2026-06-08`：只有 0 / 7272 题进入判分（未判分 100.0%）。

## 二、这个评测是什么

**一句话**：人类标准化考试原题（高考/SAT/LSAT/法考），中英双语。

- **出处**：microsoft/AGIEval 仓库自带数据。
- **数据**：7,272 题（选择题 + 数学填空）。
- **任务与判分**：选项字母按官方 `post_process.py` 解析，数学用官方 `math_equivalence.is_equiv`。规则判分，抽取 LLM 仅兜底。
- **adapter**：`scripts/eval/benchmarks/agieval.py`
- **局限**：门槛题。

**怎么用**：

```bash
MODEL=<model> ./scripts/run_eval.sh agieval
# 或：python scripts/eval_benchmark.py --benchmark agieval --model <model> --limit 0
```

## 三、当前映射（M3 裁决相关）

| evidence_tier | benchmark_weight | 能力（P:权重） |
| --- | --- | --- |
| foundation_gate | 0.4 | P06 推理与生成 (0.45)、P05 知识调用与掌握 (0.35)、P01 指令与约束遵循 (0.2) |

**这些 P 的证据因此受污染：P01、P05、P06**。裁决前先看 [`doc/eval_artifact_audit_2026-07-14.md`](../../../doc/eval_artifact_audit_2026-07-14.md)。

---

审计脚本：`python scripts/audit_eval_artifacts.py --benchmark agieval --verbose`（离线、幂等、有 unusable 时退出码非 0）。
