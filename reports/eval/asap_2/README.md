# ASAP 2.0 — imported evaluation artifacts

These runs were produced by another team and imported from `otherbenchmark/benchmark_raw_results_by_model_20260717/`. The source package is treated as immutable.

Primary metric: Quadratic weighted kappa (QWK) over the ASAP 2.0 test split; invalid/error rows are excluded from QWK and remain visible in status counts.

Each model directory contains `predictions.jsonl`, `scored.jsonl`, `summary.json`, and `report.html`. The normalized JSONL keeps raw model text and all scoring-relevant fields, but omits duplicated nested API response envelopes. `summary.json` records the original path and SHA-256 for traceability.

## 与本仓库 adapter 的口径关系（2026-07-18 补记）

本目录的结果由外部 `benchmark_runner.py` 产出。本仓库随后实现了 `scripts/eval/benchmarks/asap_2.py`，
默认口径 `ASAP_PROMPT_VARIANT=colleague` 即复刻该 runner，**新跑的模型可与本目录结果直接对比**。

已验证的一致性（用本仓库 adapter 重算本目录 `predictions.jsonl`，未调用任何 API）：

| 模型 | 已发布 QWK | 本仓库重算 | 差 |
|---|---|---|---|
| MiniMax-M3 | 0.490017498989 | 0.490017498989 | 0 |
| glm-5.1 | 0.572526333761 | 0.572526333761 | 1e-16 |

逐 prompt 亦全部吻合到浮点精度。题集为官方 test 划分，7,421 个 essay_id 与
`github.com/scrosseye/ASAP_2.0` 的 `ASAP_2_Final_github_test.csv` 逐一相同。

**口径要点：** 该 prompt 不向模型出示评分量规，且「有效分数区间」取自人工评分的观测 min/max
（跨 train+test 统计）。因此 Cowboy 一题被告知 1–5，而 Face on Mars 被告知 1–6——后者在 test 内
gold 最高仅 5 分，区间来自 train。这带有轻微标签分布泄露，是为对齐历史结果而保留的既有口径，
不代表它是更好的测量方式。若要更干净的测量，用 `ASAP_PROMPT_VARIANT=rubric`（出示官方量规、
固定 1–6），但**该变体与本目录结果不可比**。

**注意：** 用本仓库 harness 跑与本目录同名的模型会复用这里的 `predictions.jsonl` 作缓存，并覆盖
`scored.jsonl`/`summary.json`/`report.html`。复现既有模型请用 `eval_benchmark.py --out-dir <别处>`。
