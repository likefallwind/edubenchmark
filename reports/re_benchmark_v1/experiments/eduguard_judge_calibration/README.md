# EduGuard-Bench P2 Judge 元评测 — 运行说明

**问题**：EduGuard-Bench 用 LLM-as-judge 判对抗安全回复是否有害 + 拒答质量。论文用 200 条人类 gold 选了 DeepSeek-V3，但那份 gold **未公开**。本实验自建一份 **Claude Opus 4.8 标注的 gold standard**，用它衡量任意 judge 模型（MiniMax-M3 / M2.7 / 未来其它）判得有多准，并与论文 DeepSeek-V3 同台对比。

> **金标来源声明**：`gold_annotations.jsonl` 由 **Claude Opus 4.8** 盲标（标注时不可见任何已有 judge 标签），遵循官方 EduGuard rubric。这是**模型标注的金标准**，非人类标注，使用与解读时请注明。

## 工具

一个脚本三步：`scripts/experiments/eduguard_judge_eval.py`（标准库 + pandas）。
需要本地数据集 `sources/datasets/eduguard_bench/`（官方 Results 提供 DeepSeek-V3 的 BoN=9 标签）。

### 1) sample — 构建固定评测样本（已完成，无需重跑）

```bash
python3 scripts/experiments/eduguard_judge_eval.py sample --size 120
```

分层抽样（harmful/harmless 均衡、五类攻击、拒答三档），写出 `sample.jsonl`（回复 + DeepSeek-V3 标签，仅用于分层与作为 DeepSeek-V3 judge 的预测）和 `gold_blind_worksheet.jsonl`（待标盲表）。`--size` 可调；默认保留已有样本为子集（断点续标/续判）。

### 2) judge — 让 judge 模型在固定样本上判（**需要 API**）

```bash
# 当前两个 judge；论文协议 BoN=9、不设 max_tokens
MINIMAX_API_KEY=... python3 scripts/experiments/eduguard_judge_eval.py judge \
    --judges MiniMax-M3 MiniMax-M2.7 --bon 9 --concurrency 2
```

- 官方两阶段 prompt + BoN 多数投票，逐票留痕到 `judgements.jsonl`。
- **断点续跑**：已判过的 (judge, item) 自动跳过；中途限速（MiniMax `2062`）直接重跑本命令即可补齐。
- 外层 `--concurrency 2`（内层每条已并发 `bon` 票，峰值≈concurrency×bon）。限速频繁就保持 2；很顺可升到 3–4。
- 120 条、双 judge、BoN=9 约需 **40–70 分钟**。建议后台跑：
  ```bash
  MINIMAX_API_KEY=... nohup python3 scripts/experiments/eduguard_judge_eval.py judge \
      --judges MiniMax-M3 MiniMax-M2.7 --bon 9 --concurrency 2 \
      > reports/re_benchmark_v1/experiments/eduguard_judge_agreement/judge_run.log 2>&1 &
  ```

### 3) score — 每个 judge vs Opus 金标（无需 API）

```bash
python3 scripts/experiments/eduguard_judge_eval.py score
```

打印每个 judge（DeepSeek-V3 用数据里的现成标签 + `judgements.jsonl` 里的每个模型）对 Opus 金标的 **harmfulness 准确率/Cohen κ** 与 **拒答质量准确率/κ**，写 `judge_vs_gold_summary.json`（含混淆矩阵 + 论文 Table 2 参照值）。

## 加一个新 judge 模型

```bash
# 例：测某个新模型当 judge
MINIMAX_API_KEY=... python3 scripts/experiments/eduguard_judge_eval.py judge --judges <新模型名> --bon 9
python3 scripts/experiments/eduguard_judge_eval.py score   # 它会自动出现在对比表里
```

> 注：当前 client 走 MiniMax OpenAI 兼容端点；接非 MiniMax 模型需在 `scripts/eval/minimax_client.py` 旁加对应 client，judge 逻辑（prompt/投票）不变。

## 产物

| 文件 | 内容 |
|---|---|
| `sample.jsonl` | 固定 120 条评测样本（回复 + DeepSeek-V3 标签） |
| `gold_annotations.jsonl` | **Opus 4.8 金标**（key, harm, quality, conf, note） |
| `gold_blind_worksheet.jsonl` | 盲标工作表（标注用，不含标签） |
| `judgements.jsonl` | 各 judge 的逐条裁决 + 逐票留痕 |
| `judge_vs_gold_summary.json` | 打分结果（κ / 准确率 / 混淆矩阵） |
| `REPORT.md` | 结果解读报告 |

## 当前状态（2026-06-13）

- 金标 120 条已由 Opus 4.8 标注完成（49 harmful / 71 harmless；拒答 18 standard / 29 educational / 1 flimsy）。
- DeepSeek-V3 已对全 120 条算分：harm κ **0.625**、refusal-quality κ **0.957**（n=48）。
- MiniMax-M3 / M2.7 目前只判过其中 30 条（pilot），需跑步骤 2 补满 90 条，再 score 即可在 120 条上同台对比。
