生成日期：2026-06-22。本文基于当前本地结果文件生成。注意：本文没有假设所有模型都完整跑满 815 个样本；缺失、skipped 和 judge 失败都在表格中单独列出。

## 评测设置

- 评测集合：`organized_eval_sets_20260616/tested_by_both_samples.json`
- 总样本数：815
- Judge 模型：`claude-sonnet-4-6`
- Judge 输出目录：`vlm_eval_results/fair815_claude_judge/`
- 汇总命令：`bash summarize_fair815_judges.sh`

三个指标含义：

- **Simple Pass**：不加权 rubric 通过率。所有 rubric 条目同等计数。
- **Weighted Positive**：加权 rubric 分数。critical rubric 权重更高，not_critical 权重较低。
- **Weighted Shifted**：考虑 negative rubric 下界后的加权归一化分数。本文主要用这个指标做模型排序。

当前分母口径：所有模型都按 815 个 fair samples 的全部 rubrics 作为分母。skipped、empty、missing answer 没有从分母中移除，而是基本按未通过处理。因此缺失较多的模型分数偏保守。

## 主要结果

| 排名 | 模型 | Simple Pass | Weighted Positive | Weighted Shifted | Generation 覆盖 | Judge 覆盖 / Skips |
|---:|---|---:|---:|---:|---:|---:|
| 1 | GPT-5.5 | 61.88% | 55.98% | 57.57% | 815/815 | 813 judged, 2 failed judge |
| 2 | Qwen3.6-35B-A3B | 60.90% | 54.88% | 56.50% | 801/815 | 799 judged, 16 skipped |
| 3 | Qwen3.5-35B-A3B | 61.04% | 54.70% | 56.33% | 797/815 | 797 judged, 18 skipped |
| 4 | Qwen3.5-27B | 59.61% | 52.12% | 53.85% | 807/815 | 803 judged, 12 skipped |
| 5 | MiniMax-M3 | 59.11% | 51.90% | 53.63% | 811/815 | 764 judged, 51 skipped |
| 6 | Qwen3-VL-235B | 56.51% | 48.95% | 50.79% | 815/815 | 815 judged, 0 skipped |

## 费用估算

费用根据本地结果文件中的 `usage` 字段统计，并使用 apihy 页面上提供的模型单价估算。单位为美元。这里把被测模型 generation 成本和 Claude judge 成本分开列出。

| 模型 | Generation input | Generation output | Judge input | Judge output | Generation cost | Judge cost | Total cost |
|---|---:|---:|---:|---:|---:|---:|---:|
| GPT-5.5 | 1,163,659 | 1,071,300 | 1,817,442 | 733,539 | $34.16 | $6.75 | **$40.91** |
| Qwen3-VL-235B | 804,172 | 1,584,860 | 1,828,961 | 762,510 | $4.83 | $6.94 | **$11.77** |
| Qwen3.5-27B | 797,343 | 1,295,017 | 1,942,030 | 754,815 | $0.98 | $7.03 | **$8.01** |
| Qwen3.5-35B-A3B | 772,415 | 2,934,890 | 1,819,345 | 749,380 | $1.40 | $6.85 | **$8.24** |
| Qwen3.6-35B-A3B | 780,874 | 2,706,907 | 1,753,565 | 753,756 | $4.45 | $6.79 | **$11.25** |

总费用估算：约 **$80.17**。

其中：

- 被测模型 generation 总成本：约 **$45.82**
- Claude judge 总成本：约 **$34.36**

价格口径：

| 模型 | 输入价格 / 1M tokens | 补全价格 / 1M tokens |
|---|---:|---:|
| GPT-5.5 | $4.5000 | $27.0000 |
| Qwen3-VL-235B | $0.2900 | $2.9000 |
| Qwen3.5-27B | $0.0900 | $0.7000 |
| Qwen3.5-35B-A3B | $0.0600 | $0.4600 |
| Qwen3.6-35B-A3B | $0.2600 | $1.5700 |
| Claude Sonnet 4.6 judge | $1.2300 | $6.1500 |

注意：这些费用按本地记录到 `usage` 的成功请求估算。少量 HTTP 400 图片下载超时请求如果网关也收费，可能会有很小额外成本；目前没有把这类失败请求额外计入。

## 结果解读

GPT-5.5 仍然是当前 Weighted Shifted 指标下的第一名，但它和 Qwen3.6-35B-A3B 的差距很小：约 1.07 个百分点。

这次比较中最反直觉的现象是：Qwen3.5-35B-A3B 和 Qwen3.6-35B-A3B 都明显超过了 Qwen3-VL-235B。这个结果不是因为只在成功样本上算分造成的；当前分母仍然是 815 个样本的全部 rubrics，缺失样本会被惩罚。因此新 Qwen 模型的分数反而是偏保守的。

从 case study 看，Qwen3-VL-235B 的主要失分原因往往不是完全看不懂图，而是回答过短、不够显式，或者没有逐条覆盖 tutoring rubric。TutorBench 这个评测强烈奖励完整、显式、分步骤的教学式回答；Qwen3.5/3.6 系列可能更贴合这种 rubric 风格。

MiniMax-M3 已经并入当前表格。MiniMax 的原始输出中大量包含 `<think>...</think>`。为保持和其它模型的口径一致，当前 MiniMax judge 使用的是 `final` 模式：保留原始 generation 文件不变，但 judge 时去掉 `<think>...</think>` 后只评最终回答。由于部分样本去掉 thinking 后没有有效 final answer，因此 MiniMax 有 51 个 skipped；这些 skipped 没有从 815 分母中移除。

## 缺失与 skipped 情况

| 模型 | 非空答案 | 缺失答案 | 已 judge | Skipped | 其他 judge 失败 |
|---|---:|---:|---:|---:|---:|
| GPT-5.5 | 815 | 0 | 813 | 0 | 2 |
| Qwen3-VL-235B | 815 | 0 | 815 | 0 | 0 |
| Qwen3.5-27B | 807 | 8 | 803 | 12 | 0 |
| Qwen3.5-35B-A3B | 797 | 18 | 797 | 18 | 0 |
| Qwen3.6-35B-A3B | 801 | 14 | 799 | 16 | 0 |
| MiniMax-M3 | 811 | 4 | 764 | 51 | 0 |

主要 generation 失败原因：

```text
InvalidParameter: Download multimodal file timed out
```

这说明网关或模型后端下载远程图片 URL 超时。失败样本的本地图片存在，其中不少是较大的 PNG。已经加入本地图片补跑路径：`USE_LOCAL_IMAGES=1 bash rerun_fair815_skipped.sh`，但当前报告按照现有结果生成，没有继续补跑。

## 定性 Case Study

10 个可视化 case study 页面：

- `Case-Study/index.html`

一个反差特别明显的单题详细页面：

- `analysis_case_683e451098da731381469199_model_comparison.html`

这些页面包含题目图片、模型回答、总分、critical 分数、judge summary 和逐条 rubric 判断。

## 关键结论

1. 按 Weighted Shifted 排名：GPT-5.5 > Qwen3.6-35B-A3B > Qwen3.5-35B-A3B > Qwen3.5-27B > MiniMax-M3 > Qwen3-VL-235B。
2. Qwen3.6-35B-A3B 在当前 fair815 上非常接近 GPT-5.5，而且是在存在 skipped penalty 的情况下取得的。
3. Qwen3.5-35B-A3B 的性价比非常突出：总费用约 $8.24，分数接近 GPT-5.5 的 $40.91 成本结果。
4. Qwen3-VL-235B 在这个 benchmark setting 下表现不如预期，主要问题可能是 tutoring response 不够完整，而不一定是视觉理解完全失败。
5. 当前报告可以用于初步比较；如果后续需要严格公平，可以用本地 base64 图片补齐剩余 missing generations 后重新 summarize。


MiniMax-M3 的主要 generation / judge 文件：

- `vlm_eval_results/fair815_MiniMax-M3_official_prompt_no_rubrics.jsonl`
- `vlm_eval_results/fair815_claude_judge/minimax_m3_final_claude_sonnet46_judge.jsonl`

## 复现命令

汇总当前 judge 文件：

```bash
bash summarize_fair815_judges.sh
```

未来如果要用本地图片补跑缺失样本：

```bash
USE_LOCAL_IMAGES=1 API_KEY=sk-... bash rerun_fair815_skipped.sh
```

补跑后重新汇总：

```bash
bash summarize_fair815_judges.sh
```