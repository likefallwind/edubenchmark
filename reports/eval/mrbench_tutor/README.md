# mrbench_tutor — 评测产物说明

> 由 `scripts/build_eval_readmes.py` 生成（审计快照 `_audit/audit_2026-07-16.jsonl`）。**不要手改**：改脚本后重跑。
> 综述档案（这个 benchmark 是什么，给人读）：[`doc/benchmark_profiles/mrbench.md`](../../../doc/benchmark_profiles/mrbench.md)
> 本文件是给“要用这个分数的人”读的操作性病历：**分数能不能用、哪里坏了、要不要重跑**。

## 一、健康状况（坏消息在前）

全部 run 干净。

headline 口径：教学通过率（三个关键维度全 Yes）。

| 模型 | headline | 审计判决 | 判分/抽取失败率 | 未判分率 | 说明 |
| --- | --- | --- | --- | --- | --- |
| `MiniMax-M2.7` | 0.6800 | clean | 0.0% | 0.0% | — |
| `glm-5.2` | 0.7950 | clean | 0.0% | 0.0% | — |
| `minimax3` | 0.8300 | clean | 0.0% | 0.0% | — |

### 已定位的 bug（根因 + 修法）

**裁判调用失败被当成“裁判说读不懂”，缓存下来，算成教学不通过**

- 位置：`scripts/eval/benchmarks/mrbench.py` → `MRBenchTutorAdapter._judge_one`（约 468-484 行）
- 根因：`except Exception: pass` 把三次重试全部吞掉，最后 `return "unparsed"`——"调用失败" 和 "裁判回了但归一不了" 混成同一个值。这个 unparsed 写进 `extractions.jsonl`，行里**不带 `error` 字段**；而 `runner.py` 的 `run_extractions` 缓存过滤器（约 300-306 行）只跳过带 `error` 的行，于是这条失败被当成**成功缓存**，重跑也不会重试。`score()` 要求三个关键维度全为 "Yes"，unparsed → fail → 教学通过率凭空变低。
- 建议修法：1) `_judge_one` 区分两种失败：调用异常返回/抛出 `judge_call_failed` sentinel，跟 `unparsed` 分开；2) `extract_answer` 只要有一个维度是 call_failed 就 `raise`，让 runner 写带 `error` 的行——这样既不缓存也能重试；3) `extra_summary` 把 unparsed 从通过率分母里剔除并单独报 `n_unparsed`，别让它默默变成 fail。

> 本次审计**不改 adapter 代码**（那是下一步）。修完之后，受影响的 run 必须删掉 `extractions.jsonl` 里的坏行（或整个 extractions.jsonl）再重跑 —— 只跑 `--score-only` 没用，坏值已经被缓存进去了。

## 二、这个评测是什么

**一句话**：MRBench Step 2：被测模型**生成** tutor 回复，固定裁判贴 8 维标签。

- **出处**：kaushal0494/UnifyingAITutorEvaluation（NAACL 2025），`MRBench_V2.json`。
- **数据**：200 段对话。
- **任务与判分**：固定裁判 `MRBENCH_JUDGE_MODEL`（默认 MiniMax-M3，跟 `--extractor-model` 解耦）。headline = 教学通过率（Mistake_Identification / Providing_Guidance / Actionability 三个关键维度全 Yes）。
- **adapter**：`scripts/eval/benchmarks/mrbench.py`
- **局限**：通过率对裁判故障零容忍：任一关键维度 unparsed 就是 fail（见健康状况，这正是本次审计最严重的问题）。

**怎么用**：

```bash
MODEL=<model> ./scripts/run_eval.sh mrbench_tutor
# 或：python scripts/eval_benchmark.py --benchmark mrbench_tutor --model <model> --limit 0
```

## 三、当前映射（M3 裁决相关）

| benchmark_weight | 能力（P:权重） |
| --- | --- |
| 0.8 | P15 适配性解释与反馈生成 (0.2) |
| 0.8 | P09 错误诊断 (0.25) |
| 0.8 | P13 个性化教学策略选择 (0.3) |
| 0.8 | P15 适配性解释与反馈生成 (0.2) |
| 0.8 | P17 教育角色边界判断 (0.25) |

---

审计脚本：`python scripts/audit_eval_artifacts.py --benchmark mrbench_tutor --verbose`（离线、幂等、有 unusable 时退出码非 0）。
