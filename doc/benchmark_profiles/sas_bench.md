# SAS-Bench

**一句话**：高考主观题自动评分基准——不只给总分，还要分步踩分、诊断错因，和人类阅卷专家比三种一致性。

## 出处与背景

- PKU-DAIR，2025；https://github.com/PKU-DAIR/SAS-Bench
- 动机：作文评分（AES）只测整体分，真实阅卷要"过程分"和"错因"；SAS-Bench 用高考题把这三层都标注出来。

## 数据

- 高考 9 学科、1,030 道主观题、4,109 条真实学生作答；每条带人类总分、分步得分、错因标签。中文。
- 本地全量可用（同事跑分覆盖 4,109 条）。

## 任务与判分

- 三个原生指标，分别对应三种能力：
  - **QWK**：总分一致性（二次加权 Kappa）；
  - **CCS**：分步踩分一致性（结构化对齐每一步的给分）；
  - **ECS**：错因诊断一致性（错因判断与专家标签的 Spearman 趋势）。
- 12 个子任务（学科 × 题型）。

## 在本仓库怎么用

- 已接入通用评测基础设施，adapter 为 `scripts/eval/benchmarks/sas_bench.py`。先固定 revision 下载官方数据：

```bash
python scripts/eval/data/prepare_sas_bench.py
```

- 小样本先检查 prompt 与模型结构化输出；`max_tokens` 不设上限：

```bash
MODEL=MiniMax-M3 LIMIT=5 ./scripts/run_eval.sh sas_bench
```

- 全量运行使用 `LIMIT=0`。标准输出位于 `reports/eval/sas_bench/<model-slug>/`，包含 `predictions.jsonl`、`extractions.jsonl`、`scored.jsonl`、`summary.json` 和 `report.html`。`summary.json.extra_metrics` 给 QWK / CCS / ECS 的子任务值与宏平均；通用 `accuracy` 仅为严格结构完全匹配诊断值，不是 benchmark headline。
- 旧的 7 模型结果仍来自同事报告的规范化导入；新 adapter 使后续模型可由本仓库独立复跑。

## 局限与注意

- **区分度（13 号实测）**：QWK n=6 均分 8.24 sd 0.30（受限）、CCS n=6 均分 7.63 sd 0.29（受限）、**ECS n=6 均分 5.83 sd 0.60（不受限）**——三个指标里只有错因诊断拉得开分。
- **家族 halo 0.77**，触发"家族内先聚合成一票"规则。
- 报告自己的结论"会判分不等于会诊断"（GPT-5.4 QWK/CCS 最强但 ECS 不是第一）是 P11c 归因与 P14 评分分开映射的直接证据。
- 判分依赖 LLM 裁判链路，裁判是谁、prompt 什么版本要从同事处确认（与 edubench 一起进 M2 换裁判核对范围的候选）。

## 当前映射

- QWK：P14 0.70 主挂；CCS：P14 0.55 / P11b 0.25 / P02 0.20；ECS：P11c 0.70 主挂；education_core。（R17 后原 P12/P13 = P11b 定位 / P11c 归因 facet）
- 构念核对：ECS 是 P11c 归因唯一的直接测量；CCS 与 mistake_location 构成 P11b 定位的干净收敛对（等补模型验证）。
