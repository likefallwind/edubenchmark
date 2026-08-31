# Atomic P Scores — 纯文本口径 (text-only board)

跟 `09_atomic_p_scores.jsonl` 走的是**同一条**聚合链路（同样的 relevance ×
confidence 权重、facet 等权、benchmark 加权），唯一差别是：由视觉定义的取分维度
整格不参与——既不产出证据行，也不记 0、不记未测，而是根本不进这一轮的分母。

这样做是为了让纯文本模型和多模态模型能放在同一把尺子上比。**不要**改成「记 0」：
那等于断言多模态模型不具备视觉（假的），而且死重会随着多模态 benchmark 增多而
单调增长，跨轮次的分数就不再可比。

被屏蔽的取分维度：8 个

| benchmark | subdimension |
|---|---|
| `eduillustrate` | 8-dim 0-5 visual explanation score |
| `k12vista` | math problem-figure subset score |
| `k12vista` | official partial-credit score (per-blank 0/1 mean) |
| `k12vista` | science/geo subject-chart subset score |
| `mathvista` | task/question_type/answer_type accuracy |
| `mmtutorbench` | multimodal tutor score |
| `olympiadbench` | multimodal-subset accuracy |
| `tutorbench` | Fair815 multimodal tutor quality |

判据是 `requires_vision()`，读的是 `CELL_CAPABILITY_REQUIREMENTS`——跟
`missing_cell_verdict()` 同一张表但**不同的问题**：那个问「这个模型能不能作答」
（只有 REQUIRE_ALL 才记 0 分），这个问「这一格测的东西离了视觉还成不成立」
（两种严格度都算）。加新的多模态 benchmark 时只需在那张表登记一笔，两边同时生效。

P-score rows: 168
Covered P codes: P01, P02, P05, P06, P07, P08, P10, P11, P12, P13, P14, P15, P16, P17, P18, P19
Capability-gap zero cells: 0 （应为 0：视觉格已整格移除，没有能力门槛可言）

## 面板模型综合分（该口径下已测 P 的平均）

| model | 综合分 | 已测能力项 |
|---|---:|---:|
| `qwen-qwen3-8-27b` | 7.4634 | 16 |
| `minimax-m3` | 7.4289 | 16 |
| `doubao-seed-2-0-pro` | 7.1622 | 15 |
| `glm-5.2` | 7.0221 | 15 |
| `deepseek-v4-pro` | 6.9932 | 15 |
| `minimax-m2.7` | 6.9038 | 15 |
| `qwen-qwen3-5-4b` | 6.8141 | 16 |
