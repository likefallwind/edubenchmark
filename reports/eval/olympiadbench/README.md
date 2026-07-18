# olympiadbench — 评测产物说明

> 由 `scripts/build_eval_readmes.py` 生成（审计快照 `_audit/audit_2026-07-16.jsonl`）。**不要手改**：改脚本后重跑。
> 综述档案（这个 benchmark 是什么，给人读）：[`doc/benchmark_profiles/olympiadbench.md`](../../../doc/benchmark_profiles/olympiadbench.md)
> 本文件是给“要用这个分数的人”读的操作性病历：**分数能不能用、哪里坏了、要不要重跑**。

## 一、健康状况（坏消息在前）

**这个 benchmark 下有 2 个 run 的分数不可用（unusable）。** 在重跑之前，不要把它们写进任何报告、聚合或映射裁决。

headline 口径：准确率（accuracy）。

| 模型 | headline | 审计判决 | 判分/抽取失败率 | 未判分率 | 说明 |
| --- | --- | --- | --- | --- | --- |
| `2026-06-08` | 0.8966 | **unusable**（分数是假的，必须重跑） | 0.0% | 94.2% | 94.2% 的题没进判分（分数建立在 387/6728 的残缺样本上）；94.2% 的答题请求报错（上游限流/配额/参数错误）；产物数量对不上，最大缺口 94.2% |
| `deepseek-v4-pro` | 0.7361 | **unusable**（分数是假的，必须重跑） | 0.0% | 0.6% | 60.3% 的答题请求报错（上游限流/配额/参数错误）；summary.json 比产物旧：盘上的分数跟盘上的数据对不上 |
| `minimax3` | 0.7160 | clean | 0.0% | 0.1% | — |

### 样本残缺的 run

上游配额/限流打挂大批题目后，summary 仍在**幸存样本**上照常出分。这类 run 的分数没有“错”，但它测的是一个自选样本，不能跟全量 run 放在一张表里比。

- `2026-06-08`：只有 387 / 6728 题进入判分（未判分 94.2%）。

## 二、这个评测是什么

**一句话**：奥赛级数学/物理开放题，双语带图，门槛类里最难的一个。

- **出处**：Hothan/OlympiadBench（OE 配置，TP 证明题跳过）。
- **数据**：6,728 题；图片抽到 `olympiadbench/images/`。
- **任务与判分**：prompt 与判分都移植官方仓库：`make_prompt` + sympy 符号判等 `AutoScoringJudge`。**需要 `antlr4-python3-runtime==4.11`**，跟 hydra-core 冲突。
- **adapter**：`scripts/eval/benchmarks/olympiadbench.py`
- **局限**：门槛题；符号判等偶有假阴。

**怎么用**：

```bash
MODEL=<model> ./scripts/run_eval.sh olympiadbench
# 或：python scripts/eval_benchmark.py --benchmark olympiadbench --model <model> --limit 0
```

## 三、当前映射（M3 裁决相关）

| benchmark_weight | 能力（P:权重） |
| --- | --- |
| 0.55 | P03 多模态理解 (0.2)、P04 知识调用与掌握 (0.25)、P05 推理与生成 (0.55) |

**这些 P 的证据因此受污染：P03、P04、P05**。裁决前先看 [`doc/eval_artifact_audit_2026-07-14.md`](../../../doc/eval_artifact_audit_2026-07-14.md)。

---

审计脚本：`python scripts/audit_eval_artifacts.py --benchmark olympiadbench --verbose`（离线、幂等、有 unusable 时退出码非 0）。
