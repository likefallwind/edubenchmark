# Benchmark 逐项档案（2026-10-21）

`index.html` 是 P01–P20 映射内 36 个 benchmark 的逐项档案表：让模型做什么、测哪些能力、语言与题量、题型、判分与裁判、区分度、参照线和已知问题。按模型扮演的角色分组，可按语言、判分方式、区分度筛选。

**这是手工整理的分析快照，不是生成产物**，没有生成脚本，也不会随管线重跑更新。数据变化后如需刷新，从下列来源重新核对，另存一份带新日期的目录，不要原地覆盖。

## 数据来源

| 列 | 来源 |
|---|---|
| 测哪些能力 | `data/mapping_measurement_model_v6.json`（数字是 R25 相关度档位） |
| 语言 | 各 adapter `load_items` + `build_messages` 实际发给模型的题面，按汉字比例判断；p07/p08 取 run 的 `language` 桶 |
| 题量 | 各 benchmark 题量最大的已完成 run 的 `summary.json.total_items` |
| 题型 | adapter 的 `question_type` / `type` / `task` 桶，没有桶的按判分代码归类 |
| 判分与裁判 | adapter 判分路径；裁判模型取自 `reports/atomic_ability_rebenchmark/08_selected_score_evidence.jsonl` |
| 区分度 | `reports/atomic_ability_rebenchmark/13_mapping_validation_cells.jsonl` 主格子的 0–10 分布 |
| 参照线 | `data/benchmark_baselines_v1.json`（地板）、`data/benchmark_human_baselines_v1.json`（人类分与可用门槛） |
| 已知问题 | `doc/benchmark_profiles/`、`doc/benchmark_baselines_2026-08-04.md`、`doc/benchmark_human_baselines_2026-08-15.md` 及映射复核记录 |

## 区分度分档

高：模型间标准差 ≥ 0.8；中：0.4–0.8；低：标准差 < 0.4，或均分 ≥ 8.5（撞天花板）。每个 benchmark 只有 4–14 个模型有分，只作粗分。

语言与题型的汇总统计见 `doc/benchmark_language_format_inventory_2026-10-21.md`。
