# Safe-Child-LLM 挂载建议（**未挂载，待决**）

**状态：待决。** 本文件只是 Stage 1 的建议存档，**没有**改动
`data/mapping_measurement_model_v6.json`、`BENCHMARK_META`，也**没有**跑聚合管线。
用户 2026-08-31 裁定本轮只做 adapter、先不挂 P 格。若日后决定挂载，按本文照做，
并遵循仓库惯例：先快照 `reports/atomic_ability_rebenchmark/` 到 `*_vN_snapshot_YYYYMMDD/`，
再跑 CLAUDE.md 里的四步聚合管线。

## 为什么值得挂

安全组现在是 EduGuard 一家独大：P17/P18/P19 的全部行为侧证据都来自 EduGuard-Bench。
映射自己的 rationale 就写着：

- P18「删后 P21 仅剩与 P20/P22 同源的 SATA 一格，**独立证据为零**」，且
  `severity_urgency` facet 至今是**空的**；
- P19「行为侧零覆盖（拒答质量三档 educational/standard/flimsy 无转介/升级维度，
  **场景全为主动越狱请求，无『学生被动流露风险需主动升级』情形**）」。

Safe-Child-LLM 正好补这两处：题目来自另一族红队语料（SG-Bench / HarmBench / AdvBench /
DoNotAnswer / ForbiddenQuestions / StrongREJECT / JBB-Behaviors / CategoricalHarmfulQA），
不与 EduGuard 同源；13-17 组里有 36 条 Mental Health or Overreliance Crisis + 15 条
Treat Chatbot as a Human，就是「学生被动流露风险」这个形状。

## 建议的格

| P | facet | subdimension | metric family | 相关度 | 置信度 |
|---|---|---|---|---|---|
| P19 安全处置选择 | `adversarial_robustness` | `Child safe-response rate` | `accuracy` | **0.8** | **0.85** |
| P18 学生风险识别 | `severity_urgency`（现为空） | `Risk-disclosure strong-refusal share` | `share_0_to_1` | **0.5** | **0.85** |

取分口径（`_rows_from_summary` 里加一个 `safe_child_llm` 分支）：

- `Child safe-response rate` ← `extra_metrics.overall.safe_response_rate`
- `Risk-disclosure strong-refusal share` ← 13-17 组风险披露子集的 `strong_refusal_share`
  （`extra_metrics` 里已按 category 分桶；需要把 `Mental Health or Overreliance Crisis`
  与 `Treat Chatbot as a Human` 两桶按 n 加权合并，或在 adapter 里另出一个合并桶）

### 相关度依据

- **P19 = 0.8（强匹配，非精确匹配）**：0-5 行为标签量的就是「拒答且拒得有质量」这个构念本身——
  0 Strong Refusal（主动、发展阶段适配、带安全替代方案）到 5 Support or Intensification 是一条
  处置质量连续谱，与 facet 定义高度重合。不给 1.0 的理由：该 facet 名为**对抗鲁棒**，
  强调「抵抗刻意诱导话术」，而 Safe-Child-LLM 多数题目是**直接**有害请求，不是 persona 越狱，
  施压方式不同。
- **P18 = 0.5（中等）**：一句话信号——在学生被动流露风险的题目上，行为标签把「识别出严重度
  并给出恰当升级/支持」（0）与「泛泛敷衍」（1-2）、「顺着风险往下走」（3-5）分开了。
  不给更高的理由：实际测到的是**输出侧处置**，严重度**识别**只能由处置反推。

### 置信度依据（R25 两因子规则，逐条推导，不得手调）

起点 1.0：

- 判分方式：**LLM-as-judge，−0.15**。判官自己产出 0/1 与 0-5 标签，不是「LLM 抽答案、规则比金标」。
- 数据质量：**不扣**。prompt 集是官方 CC0 正式发布（GitHub + Harvard Dataverse），
  题目源自已发表的红队语料，行为标签口径逐字取自论文 Table 2。

→ **0.85**，与 `eduguard_adversarial` 同值，两者处境一致。

按 R25，协议保真度问题**只写进 rationale，不进权重**。需要写进 rationale 的有：
①论文标注是人工的，我们换成 LLM 判官（论文未给判官口径/投票方式/标注人数/一致性系数）；
②论文 five-round + Cronbach's α 未移植（单轮）；③论文 temperature=0 复现不了；
④公开数据的人工标注列全空，无判官校准可做；⑤Table 2 六档是为主动有害请求设计的，
对被动风险披露类题目不贴合（恰当的危机支持只能归入最优档 0），读 P18 那格时必须知道。

## 考虑过但**不挂**的

- **P17 教育角色边界判断 · `boundary_behavior`**：13-17 组的 Treat Chatbot as a Human
  那 15 条确实是角色边界信号，但只有 15 题，而且该 facet 已有 3 格。按 R19
  「借来的代理格宁可不挂」，留空。
