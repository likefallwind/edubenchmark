# pedagogy_benchmark — 评测产物说明

> 由 `scripts/build_eval_readmes.py` 生成（审计快照 `_audit/audit_2026-08-04.jsonl`）。**不要手改**：改脚本后重跑。
> 综述档案（这个 benchmark 是什么，给人读）：（暂无档案；本文件的“这个评测是什么”一节即是权威描述，事实来源是 adapter 源码与 AGENTS.md）
> 本文件是给“要用这个分数的人”读的操作性病历：**分数能不能用、哪里坏了、要不要重跑**。

## 一、健康状况（坏消息在前）

没有不可用的 run，但有 1 个带保留意见（caveat），引用时必须一并写出。

headline 口径：准确率（accuracy）。

| 模型 | headline | 审计判决 | 判分/抽取失败率 | 未判分率 | 说明 |
| --- | --- | --- | --- | --- | --- |
| `kimi-k2.6` | 0.8302 | caveat（可用，但必须带着下面的保留意见一起引用） | 0.0% | 0.0% | — |
| `gpt-4o` | — | no_artifacts（目录在，产物没有） | 0.0% | 0.0% | no summary.json and no scored.jsonl — nothing was produced |
| `DeepSeek-R1-0528-Qwen3-8B` | 0.6935 | clean | 0.0% | 0.0% | — |
| `MiniMax-M2.7` | 0.8248 | clean | 0.0% | 0.0% | — |
| `claude-sonnet-4-6` | 0.8490 | clean | 0.0% | 0.0% | — |
| `deepseek-v4-flash` | 0.8570 | clean | 0.0% | 0.0% | — |
| `deepseek-v4-pro` | 0.8534 | clean | 0.0% | 0.0% | — |
| `doubao-seed-2-0-pro-260215` | 0.8722 | clean | 0.0% | 0.0% | — |
| `glm-5.1` | 0.8767 | clean | 0.0% | 0.0% | — |
| `glm-5.2` | 1.0000 | clean | 0.0% | 0.0% | — |
| `gpt-5.4` | 0.8436 | clean | 0.0% | 0.0% | — |
| `minimax3` | 0.8231 | clean | 0.0% | 0.0% | — |
| `qwen3.7-max` | 0.8901 | clean | 0.0% | 0.0% | — |

## 二、这个评测是什么

（缺档案且缺条目，请补 `scripts/build_eval_readmes.py` 里的 `P` 字典。）

## 三、当前映射（M3 裁决相关）

| benchmark_weight | 能力（P:权重） |
| --- | --- |
| 1.0 | P05 知识调用与掌握 (0.5)、P14 个性化教学策略选择 (0.8) |
| 1.0 | P05 知识调用与掌握 (0.5)、P13 学习者画像建模 (0.2)、P14 个性化教学策略选择 (0.5) |

---

审计脚本：`python scripts/audit_eval_artifacts.py --benchmark pedagogy_benchmark --verbose`（离线、幂等、有 unusable 时退出码非 0）。

<!-- 以下为人工撰写内容，build_eval_readmes.py 不会覆盖 -->

# Pedagogy Benchmark — imported evaluation artifacts

These runs were produced by another team and imported from `otherbenchmark/benchmark_raw_results_by_model_20260717/`. The source package is treated as immutable.

Primary metric: Accuracy over 1,119 multiple-choice items.

Each model directory contains `predictions.jsonl`, `scored.jsonl`, `summary.json`, and `report.html`. The normalized JSONL keeps raw model text and all scoring-relevant fields, but omits duplicated nested API response envelopes. `summary.json` records the original path and SHA-256 for traceability.

## 与本仓库 adapter 的口径关系（2026-07-18 补记）

本目录的结果由外部 `benchmark_runner.py` 产出。本仓库随后实现了
`scripts/eval/benchmarks/pedagogy_benchmark.py`，默认口径 `PROMPT_VARIANT=colleague` 即复刻该
runner 的提示词与答案解析，并沿用其 `<task>:<category_key>:<index>` 题号，**新跑的模型可与本目录
结果直接对比**。已验证：本仓库枚举出的 1,119 道题，题号集合与每题标准答案均与本目录逐一相同。

**1,119 而非 1,143 的原因：** 官方每个 question 配置声明 `example_rows: [0,1,2]`，HF 发布版把上游
dev 与 test 合并为按类目分块的单一文件，故 8 个类目各自的前 3 题是提示词示例、不计分
（1143 − 8×3 = 1119）。本目录的 1,119 正是官方计分集。

**口径要点：** 该 runner 的提示词是官方原文的宽松改写（漏掉 `Only answer the real question.`、
结尾两条指令合并成一行、`(with answers)` 括号丢失），答案解析取「最后一个 A–G」而非官方 REPAT
锚定正则，且**对所有模型统一用 3-shot**——官方代码本会把推理模型路由到零样本分支。
若要严格官方口径，用 `PROMPT_VARIANT=auto|fewshot|zeroshot`，但**这些变体与本目录结果不可比**。

**注意：** 用本仓库 harness 跑与本目录同名的模型会覆盖这里的结果，复现既有模型请用
`eval_benchmark.py --out-dir <别处>`。
