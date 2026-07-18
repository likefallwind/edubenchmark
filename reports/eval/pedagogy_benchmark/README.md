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
