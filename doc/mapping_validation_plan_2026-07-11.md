# 映射效度验证计划 v2（2026-07-11）

状态：已评审定稿（v2 合并了"测量模型声明 + 信度/天花板体检 + 稳健性分析"三块扩展；v1 见 git 历史）
关联：`reports/atomic_ability_rebenchmark_2026-07-08/02_benchmark_ability_mapping.jsonl`（被验证对象）、`08_selected_score_evidence.jsonl`（数据来源）、`data/mapping_measurement_model_v1.json`（测量模型声明）、`doc/atomic_ability_principle_audit_v3.md`

## 0. 背景与问题

当前 benchmark → P01-P22 的映射权重（如 edubench PLS → P16 0.30 / P17 0.45 / P18 0.25）全部是专家先验，从未被数据检验。聚合层默认"映射到同一 P 的两个 benchmark 在测同一构念"，若该假设不成立，P 分就是把不相关的量平均，雷达图会给出貌似精确、实则错误的结论。

**2026-07-11 的 pilot 分析已经证明问题真实存在。** 用现有 181 行证据（20 模型 × 23 个 benchmark/subdimension）对 63 对"共享同一 P（双方权重 ≥0.2）且共同模型 ≥5"的配对计算跨模型 Spearman 秩相关，发现：

| 发现 | 证据 | 严重度 |
|---|---|---|
| eduguard_sata × eduguard_adversarial 相关 **ρ=+0.07**（n=7），却共同构成 P20/P21/P22 全部证据 | 两个安全测验测的是不相关的东西（规则判分的"知道什么有害" vs 越狱鲁棒性），CEG 组分是两个独立性质的平均 | 高 |
| edubench IP × pedagogy_benchmark 聚合 **ρ=−0.90**（n=5），共享 P17/P05 | 教学知识选择题与裁判打分的教学行为**排名相反** | 高 |
| edubench 家族内两两 ρ=+0.50~+0.97，但与所有外部 benchmark 为零或负相关（TMG × scaffolding −0.26 等） | 典型方法方差：edubench 分数里裁判风格偏好成分大；且 edubench 占证据行 55/181，系统性推动 CLM 分 | 高 |
| agieval × ceval × mmlu_pro 相互 ρ=+0.90~+1.00 | 三个门槛完全冗余，新模型只需跑一个 | 中（省钱机会） |
| mathtutorbench_mistake_correction 与 mmlu/agieval ρ=0.90~1.00，全模型均分 9.02 | 它实际表现为门槛题，education_core tier 存疑 | 中 |

**注意局限**：n=5-7 时 Spearman 置信区间很宽（n=5 时 |ρ|<0.9 不显著）。上表是红旗探测结果，不是精确估计；本计划要做的就是把这个一次性 pilot 变成可重复、有统计纪律、能驱动映射修订的流水线。

### 0.1 v2 新增的两个核心认识

**(a) 问题的本质是聚合结构，不只是权重数值。** v1 把问题当作"哪些 P×benchmark 格子的权重错了"；真正要回答的是"每个 P 的聚合结构本身该是什么"。这对应测量理论的经典区分：

- **反映型（reflective）构念**：映射到该 P 的 benchmark 是同一潜在能力的可互换指标，理应高相关。此时平均合法、剪冗余合法，低相关是红旗。
- **形成型（formative）构念**：该 P 本身由几个不同小方向（facet）"拼"成，指标之间**本来就不必相关**。此时低相关不是问题，但简单加权平均是在构造一个没人测过的量——正确做法是把 facet 作为一等公民分开呈现，聚合只发生在展示层且权重需明说依据。

同一个相关系数，结论完全取决于事先声明的测量模型（eduguard 两项 ρ=0.07：若 P20-22 是反映型这是灾难，若安全本来就是"知识+鲁棒"两 facet 的形成型复合则完全正常）。**声明必须先于看数据**（预注册式），否则"看到相关低才说它是两个方向"会摧毁全部说服力。

**(b) 天花板/信度是被 v1 低估的混杂。** 12 号报告的均分列：ceval 9.11、mathtutorbench_mistake_correction 9.02、edubench 各子维 8.2-8.8、mmlu_pro 8.60——这些格子在当前模型上方差已被压扁，秩相关在方差受限数据上基本是噪声。edubench × pedagogy 的 ρ=−0.90（n=5）很可能不是"知识≠行为"，而是两个天花板附近的量在比噪声。两个 benchmark 的可观测相关上限是 √(r₁₁·r₂₂)；不先做信度/天花板体检，很多 flagged 是冤案。

## 1. 目标

1. 建立幂等的"映射体检"构建脚本，随每次 rebenchmark 重跑自动出报告；
2. **测量模型声明先行**：每个 P 事先声明 reflective / formative（含 facet 划分），数据只用来证伪预期，不允许事后编结构；
3. 给每个进入主计分层的 P×benchmark 格子一个**效度评级**（validated / provisional / watch / flagged / variance_restricted / insufficient_evidence），并在最终 HTML 报告中可视化；
4. 对已发现的红旗做专项裁决实验（换裁判重判），区分"构念真不同"与"裁判偏差"与"天花板噪声"；
5. 产出映射表 v2：从 `benchmark→P` 升级为 **`benchmark→facet→P` 两级**，有数据依据的权重修订、格子拆分、tier 调整，全部记录修订理由与前后对比；
6. 最终报告附**权重扰动下的排名稳健性分析**，把"客观、有说服力"落到可审计证据上。

## 2. 方法设计

### 2.0 Phase 0：信度与天花板体检（一切相关分析的前置过滤器）

对每个 (benchmark_id, subdimension) 格子，用现有证据零成本计算：

- 跨模型 n、mean、SD、min、max（score_10 口径）；
- **`variance_restricted` 标记**：mean ≥ 8.5 或（n ≥ 4 且 SD < 0.5）→ 该格子参与的配对 ρ 不进入裁决依据（单独列出，标注原因）；floor 同理（mean ≤ 1.5）；
- 信度分层补充（后续增量）：规则判分 benchmark 用题目层 split-half（现有 scored.jsonl 可算）；LLM 判分 benchmark 的判一致性并入 2.5 换裁判实验。

### 2.1 Phase 1：测量模型声明（预注册）

`data/mapping_measurement_model_v1.json`：对映射中出现的每个 P 声明——

- `model_type`: `reflective` | `formative`；
- formative 的 P 给出 facet 划分，映射中每个格子归属一个 facet；
- `rationale` 与 `status`（draft_pending_review → reviewed）。

该文件是**人工判断产物**（先于相关数据固化、进版本库），13 号流水线消费它来决定每对配对的预期模式：

- 同 P 且（reflective 或 同 facet）→ `expect_convergent`：低相关是红旗；
- 同 P 但 formative 且跨 facet → `facet_distinct_expected`：ρ 只作信息呈现，不触发 flagged。

映射表 v2 相应从 `benchmark→P` 变为 `benchmark→facet→P` 两级：facet 内按反映型聚合（可平均、可剪冗余），facet→P 只做展示层复合（权重承认是价值判断并写明依据），雷达图支持下钻到 facet 层。

### 2.2 数据准备

- 输入：`08_selected_score_evidence.jsonl`（canonical 行，已去重）。
- 构建 model_key × (benchmark_id, subdimension) 矩阵；同格多行（同模型多 run）取均值并记入 flag。
- 配对纳入条件：双方在同一 P 上映射权重均 ≥ 0.2；共同模型数 n ≥ 5。n ∈ [3,5) 的配对单独列"低置信附录"，只呈现不参与评级。
- 家族定义：`mathtutorbench_*` → mathtutorbench，`eduguard_*` → eduguard，`p08_*` → p08，`bea2025_*` → bea2025，`mrbench_*` → mrbench，其余 = benchmark_id；同 benchmark 不同 subdimension 视为同家族。

### 2.3 聚合效度（convergent validity）

同 P 配对的跨模型 Spearman ρ，按两层分别汇报：

- **跨家族配对**（不同 benchmark 家族，如 edubench × mathtutorbench）：这是真正的聚合效度证据——不同仪器、不同判分方式对同一构念应给出一致排名；
- **同家族配对**（如 edubench 五个子维度之间）：高相关不能证明构念效度（可能是共享裁判/格式的 halo），只作方法方差诊断用（见 2.5）。

小样本统计纪律：

- 每对给 permutation p 值（n≤8 时精确置换，否则 Monte Carlo）与 bootstrap 90% CI；
- 报告中 ρ 一律与 n、CI 同格呈现，禁止裸 ρ；
- 结论以"红旗/非红旗"二值为主，不做 ρ 数值间的精细排序。

### 2.4 区分效度（discriminant validity）

聚合效度的对照组：**不共享任何 P** 的跨家族配对的 ρ 分布作为 baseline。若 `expect_convergent` 跨家族配对的 ρ 分布不显著高于 baseline，说明映射的 P 划分对"哪些 benchmark 相关"没有预测力——整个映射层需要重审而不只是个别格子。

已知干扰：模型综合质量是所有 benchmark 的共因子，会整体抬高 baseline。对策：对每个模型先算其全部 score_10 的均值（"综合分"），配对相关改用**控制综合分的偏秩相关**作为敏感性分析，与原始 ρ 并列呈现。两者结论一致才算稳。

### 2.5 方法方差（method halo）诊断

- 指标：每个 benchmark 家族的 `家族内平均 ρ − 跨家族平均 ρ` = halo 分。halo 分高说明该家族的分数主要由共享的方法成分（同一裁判、同一题面格式、同一 likert 习惯）驱动。
- pilot 已知 edubench 是最大嫌疑（家族内 0.5~0.97 vs 跨家族 ≤0，且证据行占比 30%）。

**专项裁决实验（换裁判重判）**：这是本计划里唯一需要花 API 钱的部分。

1. 从 edubench 已有 predictions 中抽 50 条 response × 5 个子维度（response 已存在，**不需重新生成**，只重新判分）；
2. 用第二裁判 **deepseek-v4-pro**（已定，见 §6）按同一 rubric 重判；预算允许再加 glm 第三票（500 次调用翻倍仍可忽略）；
3. 计算裁判间一致性（Spearman + 加权 kappa）：
   - 一致性高 → edubench 分数是稳定构念，跨家族负相关说明它测的东西真的不同 → 改映射（降低其 P17/P18 权重，或单列 facet）；
   - 一致性低 → 裁判方差主导 → 进入 `doc/judge_research_plan_2026-07-06.md` 的裁判治理轨道（换裁判/多裁判 jury/降 default weight）。
4. 同样的 50×2 协议对 eduguard_adversarial（LLM 判的那半）可选复用。

成本：50 × 5 × 2 裁判 ≈ 500 次判分调用，国内模型，可忽略。

### 2.6 决策规则（映射修订的触发条件）

评级只对**跨家族、expect_convergent、双方均非 variance_restricted、n ≥ 5** 的配对进行：

| 观测 | 动作 |
|---|---|
| ρ ≥ 0.5 且 CI 下界 > 0 | 该配对标 **validated** |
| ρ < 0 且 n ≥ 6 | 标 **flagged**，触发人工裁决，四选一：改权重 / 拆 facet / 降 tier / 判定裁判问题转 2.5 |
| 0 ≤ ρ < 0.2 且 n ≥ 8 | 标 **watch**（防 flagged 通胀的观察带） |
| 其余（含 CI 跨 0） | 标 **provisional**，等模型数增加（与预算计划联动：每新增一个模型跑区分层，关键配对 n+1） |
| 任一侧 variance_restricted | 标 **variance_restricted**，不进入裁决；优先动作是给该 benchmark 上难度/换切分而非改映射 |
| 同家族 halo 分 > 0.5 | 该家族多子维度在 P 聚合前先做**家族内聚合成一票**（防止一个裁判的偏好以 5 票进入 P 分） |

格子（P×benchmark）评级 = 其参与的合格配对评级的汇总（有 validated 取 validated；全 flagged 取 flagged；无合格配对 = insufficient_evidence；孤证 P = single_source）。

所有修订写入映射表 v2 时必须带 `revision_rationale` 字段：引用配对 ρ/n/CI，禁止无数据的权重微调。

### 2.7 冗余剪枝与组合的裁决标准（对应"情况 1"）

- **规则判分的门槛类**（agieval/ceval/mmlu_pro，ρ≈1）：留 mmlu_pro 一个；**ceval 改触发式保留**——遇中文优先模型才跑（ρ≈1 只在当前 5 个模型上成立，不保证对中文特化模型成立，且中文覆盖本身是说服力的一部分）；
- **LLM 判分的核心教学类**：即使强相关也保留两个而非一个——组合能对冲单一裁判的特异性，这是它们与门槛类的本质区别。

### 2.8 排名稳健性分析（Phase 4，说服力兜底）

映射 v2 重聚合后，对每个 P/facet 的展示层权重做 ±50% 扰动（含随机重抽权重），报告模型排名的 Kendall τ 稳定性分布：

- 结论对权重不敏感 → "权重是拍脑袋的"这一最常见质疑失效；
- 敏感 → 精确暴露哪些格子必须补数据，反馈给预算计划。

## 3. 工程实现

新脚本 `scripts/build_mapping_validation.py`，遵循仓库"generate → emit → report"幂等惯例：

- **输入**：`08_selected_score_evidence.jsonl` + `02_benchmark_ability_mapping.jsonl` + `data/mapping_measurement_model_v1.json`（路径参数化，默认指向最新 rebenchmark 目录）；
- **输出**（写入同一 rebenchmark 目录，沿用编号惯例）：
  - `13_mapping_validation_cells.jsonl`：Phase 0 体检——每格子一行（n/mean/SD/variance 标记）；
  - `13_mapping_validation_pairs.jsonl`：每配对一行（双方 benchmark/subdim、共享 P 及权重、预期模式、家族关系、n、ρ、偏相关 ρ、permutation p、CI、评级）；
  - `13_mapping_validation.md`：红旗清单 + per-P 效度摘要表 + 家族 halo 表 + 区分效度 baseline 对比 + 天花板名单；
  - `13_mapping_validation.html`：自包含交互报告——P × benchmark 矩阵热图（格子颜色=评级）、flagged/validated 配对散点图（点=模型）；
- 纯标准库（Spearman/permutation/bootstrap 手写，pilot 已证明可行；`scripts/eval/stats.py` 的 CI 工具可复用）；
- `--validate-only` 模式：只校验输入结构与配对数，不重算。

主 rebenchmark 报告（`11_*.html`）改动（M4 一并做）：雷达图每个 P 维度按其证据格子的最差评级着色/加标记（flagged 的 P 维度必须视觉可辨），并链接到 13 号报告。

## 4. 已知红旗的预定处理方案（M3 人工裁决的默认建议）

以下是数据已经支持的修订草案，供裁决时作默认选项，最终以 Phase 0 体检 + 补充数据后的结果为准：

1. **CEG 按 formative 拆 facet（作为形成型声明的第一个范例，不是特例）**：facet A"安全知识"（SATA），facet B"对抗鲁棒"（adversarial ASR + refusal quality）；P20-22 的分数分 facet 呈现，展示层复合权重写明依据；SATA 主测 P21、adversarial 主测 P22 的权重再定。
2. **edubench 家族内先聚合**：五个子维度按 rubric 相似度合并为 2 票（内容生成类：PCC/QG/TMG；支持类：IP/PLS）再进 P 分；同时执行 2.5 换裁判实验决定是否进一步降权。
3. **pedagogy_benchmark 权重重定（降级为"待体检后裁决"）**：ρ=−0.90 在双侧天花板下证据力弱（edubench 均分 8.2-8.8、pedagogy 8.56），先过 Phase 0 体检与换裁判实验，若剔除天花板混杂后负相关仍在，再执行"知识≠行为"修订（P17 下调、P05 上调，定位改为"教学知识门槛"）。
4. **mathtutorbench_mistake_correction tier 复审**：与门槛类 ρ≈1 且均分 9.02（本身 variance_restricted），建议降为 foundation_gate 或在 portfolio 里降频。
5. **门槛冗余（可先行执行，不依赖效度裁决）**：主计分保留 mmlu_pro 一个门槛；ceval 转触发式（中文优先模型）；agieval 对新模型降为可选（与预算/跳测方案联动）。

## 5. 里程碑与验收

- **M0**（0.5 天，零 API 成本）：Phase 0 天花板体检 + Phase 1 测量模型声明 `data/mapping_measurement_model_v1.json` 落地进版本库。
- **M1**（1 天）：`build_mapping_validation.py` 落地，复现 pilot 红旗（作为回归基线），产出 13 号四件套。
- **M2**（1 天）：edubench 换裁判重判实验（50×5×2，deepseek-v4-pro），出裁判间一致性结论，决定 edubench 走"改映射"还是"裁判治理"分支。
- **M2.5**（并行，随预算推进）：**补模型数是当前一切结论的瓶颈**——把关键配对的共同模型数补到 12-15（现成 harness 跑分），优先级高于任何更精巧的统计。
- **M3**（0.5 天，需人工参与）：对全部 flagged 配对逐一裁决（第 4 节草案为默认项），产出 `02_benchmark_ability_mapping` v2（benchmark→facet→P 两级）+ 修订日志。
- **M4**（1 天）：用 v2 映射重跑 rebenchmark 聚合，产出前后雷达图对比页（同一模型 v1/v2 并排）+ 排名稳健性分析（2.8），11 号报告雷达图接入评级着色。
- **持续**：每次新增模型跑分后重跑 13 号报告，provisional/watch 配对随 n 增长自动升降级。

**验收标准**：

1. 主计分层每个 P×benchmark 格子都有评级，HTML 报告可视；
2. flagged 格子全部有带数据引用的裁决记录，零"默默改权重"；
3. 映射 v2 重聚合后，同 P（expect_convergent）跨家族配对的平均 ρ 相对 v1 上升（这是"修订确实改善了构念一致性"的直接检验）；
4. 排名稳健性：权重 ±50% 扰动下头部模型排序 Kendall τ 分布有报告结论；
5. 13 号报告可在任意新的 rebenchmark 目录上无改动重跑（幂等 + 路径参数化）。

## 6. 决策记录（2026-07-11 已拍板）

1. 换裁判实验第二裁判 = **deepseek-v4-pro**（便宜、非 MiniMax 家族、判分任务表现稳）；预算允许加 glm 第三票。
2. 第 4 节修订中**只有"门槛冗余"先行执行**（不依赖效度裁决，纯省钱）；其余（含 pedagogy_benchmark 权重）等 Phase 0 体检 + 换裁判实验结果再裁。
3. flagged 触发线保持 **ρ<0**，另加 **watch 带（0≤ρ<0.2 且 n≥8）**，避免 flagged 通胀。
4. CEG 接受拆成"安全知识/对抗鲁棒"两个显示维度，并升级为 formative 测量模型声明的第一个范例。
