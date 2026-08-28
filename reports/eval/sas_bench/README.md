# sas_bench — 评测产物说明

> 由 `scripts/build_eval_readmes.py` 生成（审计快照 `_audit/audit_2026-08-28.jsonl`）。**不要手改**：改脚本后重跑。
> 综述档案（这个 benchmark 是什么，给人读）：（暂无档案；本文件的“这个评测是什么”一节即是权威描述，事实来源是 adapter 源码与 AGENTS.md）
> 本文件是给“要用这个分数的人”读的操作性病历：**分数能不能用、哪里坏了、要不要重跑**。

## 一、健康状况（坏消息在前）

全部 run 干净。

headline 口径：准确率（accuracy）。

| 模型 | headline | 审计判决 | 判分/抽取失败率 | 未判分率 | 说明 |
| --- | --- | --- | --- | --- | --- |
| `Qwen-Qwen3.5-4B` | 0.0893 | clean | 0.0% | 0.2% | — |
| `Qwen-Qwen3.8-27B` | 0.1039 | clean | 0.0% | 0.0% | — |
| `deepseek-v4-pro` | — | clean | 0.0% | 0.0% | — |
| `doubao-seed-2.0-pro` | — | clean | 0.0% | 0.0% | — |
| `glm-5.1` | — | clean | 0.0% | 0.0% | — |
| `glm-5.2` | 0.1167 | clean | 0.0% | 0.3% | — |
| `gpt-5.4` | — | clean | 0.0% | 0.0% | — |
| `kimi-k2.6` | — | clean | 0.0% | 0.0% | — |
| `minimax-m2.7` | — | clean | 0.0% | 0.0% | — |
| `minimax-m3` | — | clean | 0.0% | 0.0% | — |

## 二、这个评测是什么

（缺档案且缺条目，请补 `scripts/build_eval_readmes.py` 里的 `P` 字典。）

## 三、当前映射（M3 裁决相关）

| benchmark_weight | 能力（P:权重） |
| --- | --- |
| 1.0 | P02 长上下文与证据定位 (0.2)、P10 错误诊断 (0.2)、P11 主观题评价能力 (0.5) |
| 1.0 | P05 知识调用与掌握 (0.2)、P06 推理与生成 (0.2)、P10 错误诊断 (0.8) |
| 1.0 | P11 主观题评价能力 (0.8) |

---

审计脚本：`python scripts/audit_eval_artifacts.py --benchmark sas_bench --verbose`（离线、幂等、有 unusable 时退出码非 0）。
