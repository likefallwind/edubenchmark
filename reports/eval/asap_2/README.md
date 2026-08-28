# asap_2 — 评测产物说明

> 由 `scripts/build_eval_readmes.py` 生成（审计快照 `_audit/audit_2026-08-28.jsonl`）。**不要手改**：改脚本后重跑。
> 综述档案（这个 benchmark 是什么，给人读）：（暂无档案；本文件的“这个评测是什么”一节即是权威描述，事实来源是 adapter 源码与 AGENTS.md）
> 本文件是给“要用这个分数的人”读的操作性病历：**分数能不能用、哪里坏了、要不要重跑**。

## 一、健康状况（坏消息在前）

没有不可用的 run，但有 1 个带保留意见（caveat），引用时必须一并写出。

headline 口径：准确率（accuracy）。

| 模型 | headline | 审计判决 | 判分/抽取失败率 | 未判分率 | 说明 |
| --- | --- | --- | --- | --- | --- |
| `DeepSeek-R1-0528-Qwen3-8B` | — | caveat（可用，但必须带着下面的保留意见一起引用） | 0.0% | 4.5% | 4.5% 的题没进判分（分数建立在 7085/7421 的残缺样本上）；4.5% 的答题请求报错（上游限流/配额/参数错误） |
| `MiniMax-M2.7` | — | clean | 0.0% | 0.0% | — |
| `Qwen-Qwen3.5-4B` | — | clean | 0.0% | 0.0% | — |
| `Qwen-Qwen3.8-27B` | — | clean | 0.0% | 0.0% | — |
| `claude-sonnet-4-6` | — | clean | 0.0% | 0.0% | — |
| `deepseek-v4-flash` | — | clean | 0.0% | 0.0% | — |
| `deepseek-v4-pro` | — | clean | 0.0% | 0.0% | — |
| `doubao-seed-2.0-pro` | — | clean | 0.0% | 0.0% | — |
| `glm-5.1` | — | clean | 0.0% | 0.0% | — |
| `glm-5.2` | — | clean | 0.0% | 0.0% | — |
| `gpt-5.4` | — | clean | 0.0% | 0.0% | — |
| `kimi-k2.6` | — | clean | 0.0% | 0.0% | — |
| `minimax3` | — | clean | 0.0% | 0.1% | — |
| `qwen3.7-max` | — | clean | 0.0% | 0.0% | — |

### 样本残缺的 run

上游配额/限流打挂大批题目后，summary 仍在**幸存样本**上照常出分。这类 run 的分数没有“错”，但它测的是一个自选样本，不能跟全量 run 放在一张表里比。

- `DeepSeek-R1-0528-Qwen3-8B`：只有 7085 / 7421 题进入判分（未判分 4.5%）。

## 二、这个评测是什么

（缺档案且缺条目，请补 `scripts/build_eval_readmes.py` 里的 `P` 字典。）

## 三、当前映射（M3 裁决相关）

| benchmark_weight | 能力（P:权重） |
| --- | --- |
| 1.0 | P11 主观题评价能力 (0.8) |

---

审计脚本：`python scripts/audit_eval_artifacts.py --benchmark asap_2 --verbose`（离线、幂等、有 unusable 时退出码非 0）。

<!-- 以下为人工撰写内容，build_eval_readmes.py 不会覆盖 -->

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
