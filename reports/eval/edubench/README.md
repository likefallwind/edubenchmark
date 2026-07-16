# edubench — 评测产物说明

> 由 `scripts/build_eval_readmes.py` 生成（审计快照 `_audit/audit_2026-07-16.jsonl`）。**不要手改**：改脚本后重跑。
> 综述档案（这个 benchmark 是什么，给人读）：[`doc/benchmark_profiles/edubench.md`](../../../doc/benchmark_profiles/edubench.md)
> 本文件是给“要用这个分数的人”读的操作性病历：**分数能不能用、哪里坏了、要不要重跑**。

## 一、健康状况（坏消息在前）

没有不可用的 run，但有 1 个带保留意见（caveat），引用时必须一并写出。

headline 口径：12 维裁判总分均值（0-10）。

| 模型 | headline | 审计判决 | 判分/抽取失败率 | 未判分率 | 说明 |
| --- | --- | --- | --- | --- | --- |
| `glm-5.1` | 7.6813 | caveat（可用，但必须带着下面的保留意见一起引用） | 0.0% | 0.0% | — |
| `claude-sonnet-4-6` | 8.1121 | clean | 0.0% | 0.0% | — |
| `deepseek-v4-flash` | 8.1542 | clean | 0.0% | 0.0% | — |
| `deepseek-v4-pro` | 8.0134 | clean | 0.0% | 0.0% | — |
| `doubao-seed-2.0-lite` | 8.0371 | clean | 0.0% | 0.0% | — |
| `doubao-seed-2.0-pro` | 8.2276 | clean | 0.0% | 0.0% | — |
| `kimi-k2.6` | 7.9014 | clean | 0.0% | 0.0% | — |
| `minimax-m2.7` | 8.3424 | clean | 0.0% | 0.0% | — |
| `minimax-m3` | 8.0687 | clean | 0.0% | 0.0% | — |
| `qwen3-14b` | 7.4702 | clean | 0.0% | 0.0% | — |
| `qwen3.5-122b-a10b` | 8.2492 | clean | 0.0% | 0.0% | — |

## 二、这个评测是什么

**一句话**：中文教育场景生成，12 维裁判打 0-10 分——当前证据体系里最大的分数来源。

- **出处**：同事的完整跑批，`scripts/import_edubench_results.py` 导入；**源目录不可变**。
- **数据**：11 个模型 × 3,797 题，逐题 12 维裁判分（裁判 deepseek-v3.2）；只有 IP/QG/TMG/PLS/PCC 五个任务，没有 EC/QA/AG/ES。
- **任务与判分**：连续分（0-10），不是准确率。
- **adapter**：`scripts/import_edubench_results.py（非 harness adapter）`
- **局限**：换裁判实验（`_judge_swap`）显示：只有支持类簇（个性化/激励/高阶思维）对裁判稳健；**错误识别维度在这些任务上是裁判噪声，不可用于映射**。

**怎么用**：

```bash
MODEL=<model> ./scripts/run_eval.sh edubench
# 或：python scripts/eval_benchmark.py --benchmark edubench --model <model> --limit 0
```

## 三、当前映射（M3 裁决相关）

| evidence_tier | benchmark_weight | 能力（P:权重） |
| --- | --- | --- |
| education_core | 0.75 | P18 适配性解释与反馈生成 (0.4) |
| education_core | 0.8 | P05 知识调用与掌握 (0.3) |
| education_core | 0.8 | P18 适配性解释与反馈生成 (0.3) |
| education_core | 0.8 | P05 知识调用与掌握 (0.35) |
| education_core | 0.8 | P11 错误诊断 (0.25) |
| education_core | 0.8 | P06 推理与生成 (0.2)、P18 适配性解释与反馈生成 (0.25) |
| education_core | 0.8 | P18 适配性解释与反馈生成 (0.35) |
| education_core | 0.8 | P16 学习者画像建模 (0.3)、P17 个性化教学策略选择 (0.4) |
| education_core | 0.8 | P06 推理与生成 (0.35) |
| education_core | 0.8 | P17 个性化教学策略选择 (0.25) |
| education_core | 0.8 | P18 适配性解释与反馈生成 (0.1) |

---

审计脚本：`python scripts/audit_eval_artifacts.py --benchmark edubench --verbose`（离线、幂等、有 unusable 时退出码非 0）。
