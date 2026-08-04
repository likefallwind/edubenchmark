# edubench — 评测产物说明

> 由 `scripts/build_eval_readmes.py` 生成（审计快照 `_audit/audit_2026-08-04.jsonl`）。**不要手改**：改脚本后重跑。
> 综述档案（这个 benchmark 是什么，给人读）：[`doc/benchmark_profiles/edubench.md`](../../../doc/benchmark_profiles/edubench.md)
> 本文件是给“要用这个分数的人”读的操作性病历：**分数能不能用、哪里坏了、要不要重跑**。

## 一、健康状况（坏消息在前）

没有不可用的 run，但有 1 个带保留意见（caveat），引用时必须一并写出。

headline 口径：12 维裁判总分均值（0-10）。

| 模型 | headline | 审计判决 | 判分/抽取失败率 | 未判分率 | 说明 |
| --- | --- | --- | --- | --- | --- |
| `glm-5.2` | 8.0667 | caveat（可用，但必须带着下面的保留意见一起引用） | 0.0% | 0.0% | 冒烟样本（n=5），只能验管道，不能当分数 |
| `minimax3` | — | no_artifacts（目录在，产物没有） | 0.0% | 0.0% | no summary.json and no scored.jsonl — nothing was produced |

## 二、这个评测是什么

**一句话**：英文教育场景生成，12 维裁判打 0-10 分——当前证据体系里最大的分数来源。

- **出处**：同事完整跑批由 `scripts/import_edubench_results.py` 导入；原 prompt/item_id 现由 harness adapter 复用。
- **数据**：可比题单 3,797 题（IP 1253 / QG 1266 / TMG 578 / PLS 448 / PCC 252），现有 11 模型；不含 EC/QA/AG/ES。
- **任务与判分**：默认 MiniMax-M3 裁判按官方 12 维打连续分（0-10）；同事历史跑批使用 deepseek-v3.2，隔离在 `_judge-deepseek-v3.2/`。总体分是 12 维均值，场景分只平均官方动态分配给该任务的维度；不是准确率。
- **adapter**：`scripts/eval/benchmarks/edubench.py（原始外部结果仍由 scripts/import_edubench_results.py 导入）`
- **局限**：同事精确 judge prompt 未随产物交付，adapter 依据论文 12 维定义重建，故新旧结果不是逐字节协议复放。换裁判实验（`_judge_swap`）还显示：只有支持类簇（个性化/激励/高阶思维）对裁判稳健；**错误识别维度在这些任务上是裁判噪声，不可用于映射**。

**怎么用**：

```bash
MODEL=<model> ./scripts/run_eval.sh edubench
# 或：python scripts/eval_benchmark.py --benchmark edubench --model <model> --limit 0
```

## 三、当前映射（M3 裁决相关）

| benchmark_weight | 能力（P:权重） |
| --- | --- |
| 0.85 | P12 命题与作业设计 (0.5) |
| 0.85 | P12 命题与作业设计 (0.2) |
| 0.85 | P16 适配性解释与反馈生成 (0.5) |
| 0.85 | P05 知识调用与掌握 (0.2) |
| 0.85 | P16 适配性解释与反馈生成 (0.2) |
| 0.85 | P05 知识调用与掌握 (0.2) |
| 0.3 | P10 错误诊断 (0.2) |
| 0.85 | P06 推理与生成 (0.2)、P16 适配性解释与反馈生成 (0.2) |
| 0.85 | P16 适配性解释与反馈生成 (0.5) |
| 0.85 | P13 学习者画像建模 (0.2)、P14 个性化教学策略选择 (0.5) |
| 0.85 | P06 推理与生成 (0.5) |
| 0.85 | P14 个性化教学策略选择 (0.2) |

---

审计脚本：`python scripts/audit_eval_artifacts.py --benchmark edubench --verbose`（离线、幂等、有 unusable 时退出码非 0）。
