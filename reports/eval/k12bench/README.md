# k12bench — 评测产物说明

> 由 `scripts/build_eval_readmes.py` 生成（审计快照 `_audit/audit_2026-08-04.jsonl`）。**不要手改**：改脚本后重跑。
> 综述档案（这个 benchmark 是什么，给人读）：（暂无档案；本文件的“这个评测是什么”一节即是权威描述，事实来源是 adapter 源码与 AGENTS.md）
> 本文件是给“要用这个分数的人”读的操作性病历：**分数能不能用、哪里坏了、要不要重跑**。

## 一、健康状况（坏消息在前）

没有不可用的 run，但有 1 个带保留意见（caveat），引用时必须一并写出。

headline 口径：准确率（accuracy）。

| 模型 | headline | 审计判决 | 判分/抽取失败率 | 未判分率 | 说明 |
| --- | --- | --- | --- | --- | --- |
| `minimax3` | 0.5001 | caveat（可用，但必须带着下面的保留意见一起引用） | 0.0% | 0.0% | 产物数量对不上，最大缺口 2.7% |

## 二、这个评测是什么

（缺档案且缺条目，请补 `scripts/build_eval_readmes.py` 里的 `P` 字典。）

## 三、当前映射（M3 裁决相关）

`reports/atomic_ability_rebenchmark_2026-07-08/02_benchmark_ability_mapping.jsonl` 里没有这个 benchmark 的条目——它当前**不进能力雷达**。

---

审计脚本：`python scripts/audit_eval_artifacts.py --benchmark k12bench --verbose`（离线、幂等、有 unusable 时退出码非 0）。
