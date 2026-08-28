# ifeval — 评测产物说明

> 由 `scripts/build_eval_readmes.py` 生成（审计快照 `_audit/audit_2026-08-28.jsonl`）。**不要手改**：改脚本后重跑。
> 综述档案（这个 benchmark 是什么，给人读）：[`doc/benchmark_profiles/ifeval.md`](../../../doc/benchmark_profiles/ifeval.md)
> 本文件是给“要用这个分数的人”读的操作性病历：**分数能不能用、哪里坏了、要不要重跑**。

## 一、健康状况（坏消息在前）

全部 run 干净。

headline 口径：准确率（accuracy）。

| 模型 | headline | 审计判决 | 判分/抽取失败率 | 未判分率 | 说明 |
| --- | --- | --- | --- | --- | --- |
| `MiniMax-M2.7` | 0.9108 | clean | 0.0% | 0.5% | — |
| `Qwen-Qwen3.5-4B` | 0.9113 | clean | 0.0% | 0.0% | — |
| `Qwen-Qwen3.8-27B` | 0.9445 | clean | 0.0% | 0.0% | — |
| `deepseek-v4-pro` | 0.9222 | clean | 0.0% | 0.2% | — |
| `doubao-seed-2.0-pro` | 0.8946 | clean | 0.0% | 0.0% | — |
| `glm-5.2` | 0.9298 | clean | 0.0% | 0.0% | — |
| `minimax3` | 0.8741 | clean | 0.0% | 0.2% | — |

## 二、这个评测是什么

**一句话**：541 条带可机器验证硬约束的指令，官方规则代码判分——P01 的直接测量。

- **出处**：google-research IFEval（arXiv:2311.07911），官方 checker vendored。
- **数据**：`sources/datasets/ifeval/`，541 条；判分依赖 nltk/langdetect/immutabledict（在 miniconda python 里）。
- **任务与判分**：**无裁判、无抽取 LLM**，直接对原始回复跑官方 checker。headline = prompt 级 strict accuracy。
- **adapter**：`scripts/eval/benchmarks/ifeval.py`
- **局限**：通用英文指令，不是教育语境。

**怎么用**：

```bash
MODEL=<model> ./scripts/run_eval.sh ifeval
# 或：python scripts/eval_benchmark.py --benchmark ifeval --model <model> --limit 0
```

## 三、当前映射（M3 裁决相关）

| benchmark_weight | 能力（P:权重） |
| --- | --- |
| 1.0 | P01 指令与约束遵循 (1.0) |

---

审计脚本：`python scripts/audit_eval_artifacts.py --benchmark ifeval --verbose`（离线、幂等、有 unusable 时退出码非 0）。
