# bea2025_tutor — 评测产物说明

> 由 `scripts/build_eval_readmes.py` 生成（审计快照 `_audit/audit_2026-07-16.jsonl`）。**不要手改**：改脚本后重跑。
> 综述档案（这个 benchmark 是什么，给人读）：[`doc/benchmark_profiles/bea2025.md`](../../../doc/benchmark_profiles/bea2025.md)
> 本文件是给“要用这个分数的人”读的操作性病历：**分数能不能用、哪里坏了、要不要重跑**。

## 一、健康状况（坏消息在前）

全部 run 干净。

headline 口径：本地教学通过率（三个关键维度全 Yes）。

| 模型 | headline | 审计判决 | 判分/抽取失败率 | 未判分率 | 说明 |
| --- | --- | --- | --- | --- | --- |
| `MiniMax-M2.7` | 0.7133 | clean | 0.0% | 0.0% | — |
| `glm-5.2` | 0.8100 | clean | 0.0% | 0.0% | — |
| `minimax3` | 0.8200 | clean | 0.0% | 0.0% | — |

### 已定位的 bug（根因 + 修法）

**同款：裁判失败 → unparsed → 关键维度不通过**

- 位置：`scripts/eval/benchmarks/bea2025.py` → 模块级 `_judge_one`（约 213-222 行）
- 根因：跟 mrbench_tutor 一模一样的 `except Exception: pass` + `return "unparsed"`，同一条缓存路径。
- 建议修法：同 mrbench_tutor；两处最好抽成一个共用的 judge 调用工具函数，一次改完。

> 本次审计**不改 adapter 代码**（那是下一步）。修完之后，受影响的 run 必须删掉 `extractions.jsonl` 里的坏行（或整个 extractions.jsonl）再重跑 —— 只跑 `--score-only` 没用，坏值已经被缓存进去了。

## 二、这个评测是什么

**一句话**：BEA 2025 Step 2：被测模型生成 tutor 回复，固定裁判贴 4 维标签。

- **出处**：SIGEDU BEA 2025 官方任务 + `BEA_Shared_Task_2025_Datasets/mrbench_v3_devset.json`。
- **数据**：dev 集 300 段对话。
- **任务与判分**：固定裁判 `BEA2025_JUDGE_MODEL`/`JUDGE_MODEL`（默认 MiniMax-M3）。headline = 本地教学通过率（三个关键维度全 Yes）。
- **adapter**：`scripts/eval/benchmarks/bea2025.py`
- **局限**：不能宣称等价官方榜；跟 mrbench_tutor 同款裁判故障。

**怎么用**：

```bash
MODEL=<model> ./scripts/run_eval.sh bea2025_tutor
# 或：python scripts/eval_benchmark.py --benchmark bea2025_tutor --model <model> --limit 0
```

## 三、当前映射（M3 裁决相关）

| benchmark_weight | 能力（P:权重） |
| --- | --- |
| 0.85 | P16 适配性解释与反馈生成 (0.2) |
| 0.85 | P10 错误诊断 (0.2) |
| 0.85 | P14 个性化教学策略选择 (0.2) |

---

审计脚本：`python scripts/audit_eval_artifacts.py --benchmark bea2025_tutor --verbose`（离线、幂等、有 unusable 时退出码非 0）。
