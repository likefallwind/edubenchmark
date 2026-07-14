# p07_selfcheck — 评测产物说明

> 由 `scripts/build_eval_readmes.py` 生成（审计快照 `_audit/audit_2026-07-14.jsonl`）。**不要手改**：改脚本后重跑。
> 综述档案（这个 benchmark 是什么，给人读）：[`doc/benchmark_profiles/p07_selfcheck.md`](../../../doc/benchmark_profiles/p07_selfcheck.md)
> 本文件是给“要用这个分数的人”读的操作性病历：**分数能不能用、哪里坏了、要不要重跑**。

## 一、健康状况（坏消息在前）

全部 run 干净。

headline 口径：score_10 = 10×[0.5×fix_rate + 0.5×(1−break_rate)]（0-10）。

| 模型 | headline | 审计判决 | 判分/抽取失败率 | 未判分率 | 说明 |
| --- | --- | --- | --- | --- | --- |
| `MiniMax-M2.7` | 5.1450 | clean | 0.0% | 0.0% | — |
| `deepseek-v4-pro` | 5.5720 | clean | 0.0% | 0.7% | — |
| `doubao-seed-2.0-pro` | 5.0190 | clean | 0.0% | 0.0% | — |
| `glm-5.2` | 5.4600 | clean | 0.0% | 0.0% | — |
| `minimax3` | 5.2460 | clean | 0.0% | 0.0% | — |

### 已定位的 bug（根因 + 修法）

**第二轮撞限流 → r2_error 写进缓存 → 该题从指标分母里消失**

- 位置：`scripts/eval/benchmarks/p07_selfcheck.py` → `extract_answer`（约 112-131 行）
- 根因：三次重试后把 `last_error` 塞进 `r2_error` 字段，`r2_response` 留空；extraction 行**不带 `error`**，于是被缓存。`score()` 把这题标 `r2_missing`，`extra_summary` 从 graded 里剔除，summary 照常算出 `score_10`——分母悄悄变小了。字段 `n_round2_missing` 里能看出来，但没人会去看。
- 建议修法：`extract_answer` 在 `r2_response` 为空时直接 `raise`，让 runner 记 error 行、下次重跑；`n_round2_missing > 0` 时在 summary 里写一条显式的 `warning` 字段。

> 本次审计**不改 adapter 代码**（那是下一步）。修完之后，受影响的 run 必须删掉 `extractions.jsonl` 里的坏行（或整个 extractions.jsonl）再重跑 —— 只跑 `--score-only` 没用，坏值已经被缓存进去了。

## 二、这个评测是什么

**一句话**：先答题、再无提示地要求“重新检查”，分离“错改对”（真自查）与“对改错”（有害的自我怀疑）——P07 的直接测量。

- **出处**：自建，复用 P08 的题单代理（agieval/ceval/mmlu_pro/mtb_problem_solving）。
- **数据**：固定题单 `data/p08_calibration/item_list_v1.txt`，550 题。
- **任务与判分**：第二轮在 `extract_answer` 里再调**被测模型本人**（`adapter.model_under_test`）。headline `score_10 = 10*[0.5*fix_rate + 0.5*(1-break_rate)]`，跟第一轮准确率解耦。
- **adapter**：`scripts/eval/benchmarks/p07_selfcheck.py`
- **局限**：第二轮撞限流会把整题从分母里剔掉（`n_round2_missing`），summary 照常出分——历史上就是这么翻的车。

**怎么用**：

```bash
MODEL=<model> ./scripts/run_eval.sh p07_selfcheck
# 或：python scripts/eval_benchmark.py --benchmark p07_selfcheck --model <model> --limit 0
```

## 三、当前映射（M3 裁决相关）

| evidence_tier | benchmark_weight | 能力（P:权重） |
| --- | --- | --- |
| diagnostic | 0.85 | P07 自我校验与修正 (0.85)、P08 置信度校准与弃答 (0.15) |

---

审计脚本：`python scripts/audit_eval_artifacts.py --benchmark p07_selfcheck --verbose`（离线、幂等、有 unusable 时退出码非 0）。
