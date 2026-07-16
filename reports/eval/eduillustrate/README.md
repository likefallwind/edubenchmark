# eduillustrate — 评测产物说明

> 由 `scripts/build_eval_readmes.py` 生成（审计快照 `_audit/audit_2026-07-16.jsonl`）。**不要手改**：改脚本后重跑。
> 综述档案（这个 benchmark 是什么，给人读）：[`doc/benchmark_profiles/eduillustrate.md`](../../../doc/benchmark_profiles/eduillustrate.md)
> 本文件是给“要用这个分数的人”读的操作性病历：**分数能不能用、哪里坏了、要不要重跑**。

## 一、健康状况（坏消息在前）

**这个 benchmark 下有 6 个 run 的分数不可用（unusable）。** 在重跑之前，不要把它们写进任何报告、聚合或映射裁决。

headline 口径：overall_mean_judged_only（0-5，**有幸存者偏差**）。

| 模型 | headline | 审计判决 | 判分/抽取失败率 | 未判分率 | 说明 |
| --- | --- | --- | --- | --- | --- |
| `doubao-seed-2.0-lite__gen-full230_judge-minimax3` | 3.3885 | **unusable**（分数是假的，必须重跑） | 21.7% | 21.7% | 21.7% 的题命中失败标记：渲染失败、没送裁判（headline 有幸存者偏差）；21.7% 的题没进判分（分数建立在 180/230 的残缺样本上） |
| `deepseek-v3.2` | 3.5301 | **unusable**（分数是假的，必须重跑） | 20.0% | 20.0% | 20.0% 的题命中失败标记：渲染失败、没送裁判（headline 有幸存者偏差）；20.0% 的题没进判分（分数建立在 4/5 的残缺样本上）；冒烟样本（n=5），只能验管道，不能当分数 |
| `doubao-seed-2.0-lite` | 3.6220 | **unusable**（分数是假的，必须重跑） | 20.0% | 20.0% | 20.0% 的题命中失败标记：渲染失败、没送裁判（headline 有幸存者偏差）；20.0% 的题没进判分（分数建立在 4/5 的残缺样本上）；冒烟样本（n=5），只能验管道，不能当分数 |
| `doubao-seed-2.0-pro` | 3.1258 | **unusable**（分数是假的，必须重跑） | 20.0% | 20.0% | 20.0% 的题命中失败标记：渲染失败、没送裁判（headline 有幸存者偏差）；20.0% 的题没进判分（分数建立在 4/5 的残缺样本上）；冒烟样本（n=5），只能验管道，不能当分数 |
| `minimax3` | 3.6649 | **unusable**（分数是假的，必须重跑） | 20.0% | 20.0% | 20.0% 的题命中失败标记：渲染失败、没送裁判（headline 有幸存者偏差）；20.0% 的题没进判分（分数建立在 4/5 的残缺样本上）；冒烟样本（n=5），只能验管道，不能当分数 |
| `opus-4.8` | 3.7144 | **unusable**（分数是假的，必须重跑） | 20.0% | 20.0% | 20.0% 的题命中失败标记：渲染失败、没送裁判（headline 有幸存者偏差）；20.0% 的题没进判分（分数建立在 4/5 的残缺样本上）；冒烟样本（n=5），只能验管道，不能当分数 |
| `doubao-seed-2.0-pro__gen-full230_judge-MiniMax-M3` | 3.7055 | caveat（可用，但必须带着下面的保留意见一起引用） | 10.4% | 10.4% | 10.4% 的题命中失败标记：渲染失败、没送裁判（headline 有幸存者偏差）；10.4% 的题没进判分（分数建立在 206/230 的残缺样本上） |
| `kimi-k2.7-code__gen-full230_judge-MiniMax-M3` | 3.5898 | caveat（可用，但必须带着下面的保留意见一起引用） | 0.4% | 0.4% | — |
| `MiniMax-M3__gen-full230_judge-MiniMax-M3` | 3.1748 | caveat（可用，但必须带着下面的保留意见一起引用） | 0.0% | 0.0% | — |

### 样本残缺的 run

上游配额/限流打挂大批题目后，summary 仍在**幸存样本**上照常出分。这类 run 的分数没有“错”，但它测的是一个自选样本，不能跟全量 run 放在一张表里比。

- `deepseek-v3.2`：只有 4 / 5 题进入判分（未判分 20.0%）。
- `doubao-seed-2.0-lite`：只有 4 / 5 题进入判分（未判分 20.0%）。
- `doubao-seed-2.0-lite__gen-full230_judge-minimax3`：只有 180 / 230 题进入判分（未判分 21.7%）。
- `doubao-seed-2.0-pro`：只有 4 / 5 题进入判分（未判分 20.0%）。
- `doubao-seed-2.0-pro__gen-full230_judge-MiniMax-M3`：只有 206 / 230 题进入判分（未判分 10.4%）。
- `minimax3`：只有 4 / 5 题进入判分（未判分 20.0%）。
- `opus-4.8`：只有 4 / 5 题进入判分（未判分 20.0%）。

## 二、这个评测是什么

**一句话**：写 Manim 代码把解题过程画出来，渲染成功后裁判按 8 维（4 文本 + 4 视觉）打 0-5 分。

- **出处**：arXiv:2604.05005，本地生成器 `/home/likefallwind/code/EduIllustrate`。
- **数据**：benchmark.json 230 题（另有 5 题冒烟集）。
- **任务与判分**：8 维 0-5 Likert，逐题几何平均，benchmark 级算术平均。**产物不走标准 harness**（没有 predictions/extractions，schema 自成一套）。
- **adapter**：`scripts/eval/build_eduillustrate_report.py`
- **局限**：裁判是替代 provider（MiniMax-M3 等），不是论文原用的 Gemini 3.0 Pro，**不可与论文榜比较**；渲染失败的题不送裁判、计 0，`overall_mean_judged_only` 有幸存者偏差，跨模型比较请用 `overall_mean_all_items`。

**怎么用**：

```bash
MODEL=<model> ./scripts/run_eval.sh eduillustrate
# 或：python scripts/eval_benchmark.py --benchmark eduillustrate --model <model> --limit 0
```

## 三、当前映射（M3 裁决相关）

| evidence_tier | benchmark_weight | 能力（P:权重） |
| --- | --- | --- |
| diagnostic | 0.85 | P10 多模态教学产物生成 (0.45)、P18 适配性解释与反馈生成 (0.3) |

**这些 P 的证据因此受污染：P10、P18**。裁决前先看 [`doc/eval_artifact_audit_2026-07-14.md`](../../../doc/eval_artifact_audit_2026-07-14.md)。

---

审计脚本：`python scripts/audit_eval_artifacts.py --benchmark eduillustrate --verbose`（离线、幂等、有 unusable 时退出码非 0）。

<!-- 以下为人工撰写内容，build_eval_readmes.py 不会覆盖 -->

# EduIllustrate 评测结果索引

生成侧仓库：`/home/likefallwind/code/EduIllustrate`（本目录只存评测产物，生成产物留在该仓库的 `output/`）。
题库：`data/benchmark/benchmark.json`（230 题）。评分：8 维 0-5 Likert，单题取几何均值，benchmark 级取算术均值。

> 判官均为替代 provider（MiniMax-M3），非论文原用的 Gemini 3.0 Pro。分数仅供内部横向对比，**不可与论文 leaderboard 直接比较**。

## 全量 230 题（判官 MiniMax-M3）

**排序以 `all-230` 为准**，它是唯一可跨模型比较的口径。

| 模型 | 判卷 | 渲染失败 | judged-only | **all-230** |
|---|---|---|---|---|
| kimi-k2.7-code | 229 | 1 | 3.590 | **3.574** |
| doubao-seed-2.0-pro | 206 | 24 | 3.705 | **3.319** |
| MiniMax-M3 | 230 | 0 | 3.175 | **3.175** |
| doubao-seed-2.0-lite | 180 | 50 | 3.389 | **2.652** |

生成参数统一为 topic=4 / scene=4、max_retries=3；评测统一为 max_workers=4、retry_limit=2。

### ⚠️ 不要用 judged-only 排名

`overall_mean_judged_only` 只统计成功出稿的题，**有幸存者偏差**：渲染失败的题不是随机掉的，而是模型画不出来的那批难题，把它们排除后剩下的样本自然偏容易。失败率越高的模型，这个分被抬得越狠。

最典型的是 **doubao-seed-2.0-pro：judged-only 3.705 是全场最高，但它失败了 24 题**，按 230 分母折算只有 3.319，实际落后 kimi-k2.7-code。谁要是照 judged-only 排名，会得出完全相反的结论。

跨模型比较一律用 `overall_mean_all_items`（失败题计 0）。

### 各 run 的目录

- [`kimi-k2.7-code__gen-full230_judge-MiniMax-M3/`](kimi-k2.7-code__gen-full230_judge-MiniMax-M3/)
- [`doubao-seed-2.0-pro__gen-full230_judge-MiniMax-M3/`](doubao-seed-2.0-pro__gen-full230_judge-MiniMax-M3/) — 另见 [coverage_note.md](doubao-seed-2.0-pro__gen-full230_judge-MiniMax-M3/coverage_note.md)（24 题失败清单与根因）
- [`MiniMax-M3__gen-full230_judge-MiniMax-M3/`](MiniMax-M3__gen-full230_judge-MiniMax-M3/)
- [`doubao-seed-2.0-lite__gen-full230_judge-minimax3/`](doubao-seed-2.0-lite__gen-full230_judge-minimax3/)

每个目录含 `summary.json`（分维度 + 按难度/题型/科目分桶）、`scored.jsonl`（逐题）、`report.html`（可读表格）、以及各题的 `evaluation_problem*.json`。

## 分维度观察（judged，全量 run）

| 维度 | MiniMax-M3 | kimi-k2.7 | doubao-pro | doubao-lite |
|---|---|---|---|---|
| correctness_and_completeness | 3.239 | 4.135 | **4.204** | 4.017 |
| logical_coherence | 3.530 | 4.288 | **4.413** | 4.078 |
| understandability_and_teaching_effect | 2.713 | 3.205 | **3.316** | 3.156 |
| text_diagram_synergy | 3.350 | **3.497** | 3.496 | 3.171 |
| diagram_match | **3.006** | 2.990 | 2.962 | 2.794 |
| layout_and_visual_clarity | 3.522 | 4.031 | **4.316** | 3.972 |
| element_layout_quality | **3.595** | 3.486 | 3.509 | 3.171 |
| visual_consistency | 4.002 | 3.889 | **4.280** | 4.148 |

**`diagram_match` 是全 benchmark 的共同短板**——四个模型都卡在 2.79~3.01，且是多数模型八维里的最低项。"图到底对不对得上题目要求"是当前最难的一环，跟模型选型关系不大。

## 旧的部分跑（勿与全量混淆）

以下目录是早期 4-5 题的 smoke / 判官对比实验，**分母不是 230**，不要拿来跟上表比：
`minimax3/`、`doubao-seed-2.0-pro/`、`doubao-seed-2.0-lite/`、`deepseek-v3.2/`、`opus-4.8/`（这几个的 `model` 字段多为 MiniMax-M3，变的是判官）。

## 怎么再跑一个模型

在 EduIllustrate 仓库：

```bash
bash scripts/run_doubao_pro.sh          # 生成(照着改 --model 和 output_dir)
GEN_CONCURRENCY="topic=4 / scene=4" \
  bash scripts/eval_eduillustrate.sh output/<生成目录> <模型标签> MiniMax-M3
```

评测脚本会自动把报告写进本目录，并把生成/评测参数记进 `summary.json` 的 `run_notes`。
