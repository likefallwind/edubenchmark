# mathtutorbench_scaffolding_hard — 评测产物说明

> 由 `scripts/build_eval_readmes.py` 生成（审计快照 `_audit/audit_2026-07-16.jsonl`）。**不要手改**：改脚本后重跑。
> 综述档案（这个 benchmark 是什么，给人读）：[`doc/benchmark_profiles/mathtutorbench.md`](../../../doc/benchmark_profiles/mathtutorbench.md)
> 本文件是给“要用这个分数的人”读的操作性病历：**分数能不能用、哪里坏了、要不要重跑**。

## 一、健康状况（坏消息在前）

没有不可用的 run，但有 2 个带保留意见（caveat），引用时必须一并写出。

headline 口径：胜率（对金标 tutor 回复）。

| 模型 | headline | 审计判决 | 判分/抽取失败率 | 未判分率 | 说明 |
| --- | --- | --- | --- | --- | --- |
| `doubao-seed-2.0-lite` | 0.1498 | caveat（可用，但必须带着下面的保留意见一起引用） | 8.6% | 0.0% | 8.6% 的题命中失败标记：两次成对投票都失败，win_score=None，被当成输；8.6% 的抽取/判分行带 error；summary.json 比产物旧：盘上的分数跟盘上的数据对不上 |
| `deepseek-v4-flash` | 0.1284 | caveat（可用，但必须带着下面的保留意见一起引用） | 5.5% | 0.0% | 5.5% 的题命中失败标记：两次成对投票都失败，win_score=None，被当成输；5.5% 的抽取/判分行带 error；summary.json 比产物旧：盘上的分数跟盘上的数据对不上 |
| `MiniMax-M2.7` | 0.1009 | clean | 0.0% | 0.0% | — |
| `deepseek-v4-pro` | 0.3578 | clean | 0.0% | 0.0% | — |
| `doubao-seed-2.0-pro` | 0.2783 | clean | 0.0% | 0.0% | — |
| `glm-5.2` | 0.4862 | clean | 0.0% | 0.0% | — |
| `minimax3` | 0.1896 | clean | 0.0% | 0.0% | — |

### 已定位的 bug（根因 + 修法）

**成对投票全失败 → win_score=None → 直接算输**

- 位置：`scripts/eval/benchmarks/mathtutorbench.py` → `_WinRateBase._vote_letter`（约 739-751 行）
- 根因：`except Exception: pass`，三次重试后 `return None`。两个顺序的票都是 None 时 `win_score = None`，`score()` 里 `correct = ws is not None and ws > 0.5` → **False**，即裁判挂掉等于生成回复输给金标。同样不带 `error`，同样被缓存。另外只有一票回来时，位置去偏（A/B 交换）失效，win_score 变成单票的 0/1，也没被标出来。
- 建议修法：1) 两票都失败时抛异常，让 runner 记 `error` 行；2) `score()` 遇 `win_score is None` 返回非 scored 状态而不是 correct=False；3) 单票的项在 `extra_summary` 里单列 `n_partial_vote`，胜率分母里要么剔除、要么显式标注。

> 本次审计**不改 adapter 代码**（那是下一步）。修完之后，受影响的 run 必须删掉 `extractions.jsonl` 里的坏行（或整个 extractions.jsonl）再重跑 —— 只跑 `--score-only` 没用，坏值已经被缓存进去了。

## 二、这个评测是什么

**一句话**：MathTutorBench：脚手架引导胜率，hard 变体。

- **出处**：MathTutorBench 官方仓库（LLM-as-judge 版胜率，替代论文的 GPU reward model）。
- **数据**：1,308 条。
- **任务与判分**：同 pedagogy。
- **adapter**：`scripts/eval/benchmarks/mathtutorbench.py`
- **局限**：同 pedagogy。

**怎么用**：

```bash
MODEL=<model> ./scripts/run_eval.sh mathtutorbench_scaffolding_hard
# 或：python scripts/eval_benchmark.py --benchmark mathtutorbench_scaffolding_hard --model <model> --limit 0
```

## 三、当前映射（M3 裁决相关）

| benchmark_weight | 能力（P:权重） |
| --- | --- |
| 1.0 | P04 知识调用与掌握 (0.15)、P13 个性化教学策略选择 (0.5)、P15 适配性解释与反馈生成 (0.35) |

---

审计脚本：`python scripts/audit_eval_artifacts.py --benchmark mathtutorbench_scaffolding_hard --verbose`（离线、幂等、有 unusable 时退出码非 0）。
