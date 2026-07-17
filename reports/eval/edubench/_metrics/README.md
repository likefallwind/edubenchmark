# EduBench 指标级派生分数（生成物，勿手改）

由 `scripts/build_edubench_metric_summaries.py` 从各模型目录的 `scored.jsonl`（同事原始判分，只读不改）派生：每行一个 (model, task, metric) 的 n/mean/sd。

- `task == "ALL"`：五任务合并的指标均值——映射 v2 中 `<metric> (metric)` 格子的取分来源。
- `metric == "tmg_pcc_composite"`（task=TMG/PCC）与 `metric == "qg_composite"`（task=QG）：对应任务上 clarity_concision_inspiration + scenario_element_integration 的逐题两指标均值再取均值，分别对应 P18 教学产物生成与 P23 题目生成的 task×metric 复合格子（R18 拆分 QG→P23 后原 artifact_composite 不再产出）。
- `sd` 为题级标准差，供 13 号检查的死格子（SD<0.5）判定参考。
