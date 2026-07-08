# Rubric 自进化研究方案：测试驱动的结构化 Rubric 工程（2026-07-06）

> 目标：以 `data/judge_meta_eval_v1/` 的人类金标为监督信号，让教学裁判的 rubric prompt
> 自进化，把裁判-人类 Cohen's kappa 从当前 ≈0.40–0.44 尽可能推向标注噪声允许的上限。
> 前置：`doc/judge_research_plan_2026-07-06.md`（WP0–WP5 已全部落地，附录 0 有结果）。
>
> **定位**：与文献里多数"无人类标注、靠 meta-judge 自举"的 rubric 生成工作不同，我们有
> ≈1.8 万条人类金标 dev split——这是一个**监督式 prompt 优化**问题，且诊断（偏严、分歧率、
> 长度偏置）已指明搜索方向。GEPA 类通用优化器降级为对比基线，不是方法本体。

---

## 1. 证据基础（已测得）

| 事实 | 数字 | 对方案的含义 |
|---|---|---|
| 最佳单裁判 glm-5.2 的 test kappa | mrbench 0.438 / bea2025 0.406 | 进化的起点与默认裁判 |
| 陪审团 vs 最佳单裁判 | 三条线配对差值 CI 全含 0 | 提升要靠 rubric，堆裁判无效 |
| 系统性偏严 | 所有裁判所有长度桶 P(Yes)−P(human=Yes) = −7~−21pp，多数显著 | **主缺陷是校准不是语义**，Stage 0 先探校准地板 |
| 三票分歧率 | bea2025 0.393 > mrbench 0.309 > mathtutorbench 0.138 | 维度选靶与噪声分层的依据 |
| BEA dev 标注与 MRBench V2 在 1,493 条共享回复上一致率 1.000 | 同一血统复制，非独立双标 | 没有免费的人类-人类 kappa 天花板；上限只能引用原论文 IAA + 用共识分裂率佐证 |
| M3 pairwise 显著偏爱长回复（+8.5pp） | 唯一显著的裁判 | 长度偏置作为进化的回归测试项（改 rubric 不能把它改出来） |

## 2. 文献结论 → 设计原则

GEPA（arXiv 2507.19457，反思式 prompt 进化）是"有标注指标可爬"设定下最强的通用基线，
但有四个实锤缺陷，每个都有对症文献：

| GEPA 缺陷 | 证据 | 对症方案（文献） | 本方案采用 |
|---|---|---|---|
| prompt 膨胀、边例记忆、泛化差 | 生产报告：无约束进化出 5,000+ 字符 prompt | 结构化 rubric + 类型化编辑（RRD 2603.00077 的递归分解过滤、RULERS 的证据锚定） | 原则 P1 |
| 反思幻觉/归因错误 | GEPA 论文自认 misattribute credit | 编辑即假设、统计检验后提交（analytic rubrics 逐准则信号） | 原则 P2 |
| 噪声指标下选候选低效 | winner's curse | bandit best-arm / 逐次减半（TRIPLE、PDO 2510.13907、2605.14553）；多保真搜索（2501.17178） | 原则 P3 |
| 只优化指令不优化锚例 | GEPA future work 自列 | DPFS 分布保持锚例采样；锚例是裁判校准文献里收益最大的杠杆 | 原则 P4 |

再加两条我们独有的（文献没有的）：

- **P5 聚合诊断驱动提案**：变异提案的输入不是一小撮错例，而是分布级证据
  （混淆矩阵格、长度桶宽容度差、per-dimension 分歧率）。
- **P6 共识分层去噪**：三家裁判（deepseek-v4-pro / glm-5.2 / MiniMax-M3）全量 dev 票
  把每条判例分为三层——
  ① 三票一致且=人类（简单例，降采样）；
  ② **三票一致但≠人类**（rubric 语义缺口或疑似标注错误，最高学习价值；EduGuard 上游
  1,333 条答案错位就是靠类似手法抓出，有实绩背书）；
  ③ 三票分裂（题目模糊，学它=拟合噪声，隔离出训练信号、单独报告）。

## 3. 方法：四个 Stage

### Stage 0：校准地板（先探底，决定后续投入）

主缺陷是边缘分布错位，这类误差未必需要"进化"。两个便宜实验：

- **0a 后验标签重映射**（零 API）：对每个 (judge, benchmark, dimension)，在
  **dev−评估片** 上枚举全部 `源标签(含 unparsed)→目标标签` 映射（≤3^4=81 个），
  选 dev kappa 最大者，在**评估片**上报告映射前后 kappa + 配对差值 CI。
  这是分类器 Platt scaling 的标签版；它不改 prompt，是任何 rubric 进化
  **必须显著超过的地板**。脚本 `scripts/build_judge_remap_baseline.py`。
- **0b DPFS 锚例变体**（≈4k 次 glm-5.2 调用）：两个 prompt 变体 vs 缓存的 v1 基线——
  `dpfs`：每维度 K=6 个 few-shot 人类锚例，标签配比匹配 dev 人类边缘分布
  （锚例取自 dev−评估片，杜绝泄漏；上下文截尾控制 prompt 长度）；
  `dpfs_cal`：锚例 + 一行显式边缘分布提示。
  评估片 = `split_dev_subsample_glm/`（1,202+801 条，glm-5.2 v1 基线已缓存，白捡）。
  脚本 `scripts/run_judge_rubric_variants.py`，输出 `reports/eval/_judge_rubric/stage0/`。

**决策门**：设 v1→人类的 kappa 差距为 G。
- 若 0a/0b 合计吃掉 >60% 的 G：问题主体是校准，Stage 1/2 缩水为小规模验证，研究故事
  转向"教学裁判的校准修正 + 天花板分析"；
- 若吃掉 20–60%：按计划全量进入 Stage 1/2，0a/0b 进消融表；
- 若 <20%：语义缺口为主，Stage 1 的诊断驱动编辑是主战场。

### Stage 1：结构化 rubric 表示 + 诊断驱动提案

- rubric 从自由文本升级为结构对象：`{维度定义, 行为化锚点(每标签), few-shot 锚例引用,
  边界澄清条款[]}`，序列化为 prompt 时逐段渲染。编辑 = 类型化算子：
  `add_anchor / edit_boundary / add_clause / drop_clause / swap_exemplar`。
- 提案生成：反思 LLM 的输入 = 聚合诊断（该维度混淆矩阵、长度桶宽容度、P6 第②层
  共识错例样本 + 三家 rationale），要求产出**针对特定混淆格**的编辑提案。
- 每维度一条血统；pilot 先取 per-dimension kappa 最低的 2 个维度（从
  `_judge_jury/summary.json` 读取），验证循环有效后扩展。

### Stage 2：编辑即假设，赛马验证后提交

- 候选编辑先在 ~150 条分层小片上逐次减半（淘汰明显无效者，省预算）；
- 幸存候选在完整评估片上跑，**配对 bootstrap CI（stats.py）差值 >0 且显著才提交**；
- 已提交编辑每轮回归：若边际效用转负则剔除（rubric 的回归测试）；
- 防目标退化的固定检查：unparsed 率不升、长度偏置不升（M3 的教训）、prompt 总长
  有硬预算（GEPA 膨胀的教训）；
- 每个提交带完整审计链：触发诊断 → 实验 id → 效应量+CI → prompt hash
  （WP2 provenance 直接复用；此时建正式的 judge prompt registry——它在这一步变成
  load-bearing，不再是过早抽象）。

### Stage 3：终验

胜出 rubric → 全量 dev 确认 → **test split 一次性评估**（全程封存后首碰）→
显著优于 v1 与 0a 地板则 bump `JUDGE_PROMPT_VERSION=v2`，更新生产裁判建议。

## 4. 实验协议（防泄漏/防过拟合，全部硬规则）

1. **test split 封存**：Stage 3 前任何实验不得读取 test 的人类标签做决策；
2. dev 内三分：**锚例池**（dev−评估片，供 DPFS/锚例编辑取例）、**诊断池**（同上，供
   聚合诊断与共识分层）、**评估片**（`split_dev_subsample_glm`，一切候选的裁决场）；
3. 所有 prompt 变体记 sha256 + 版本号入输出 summary（复用 WP2 机制）；
4. 全部显著性判断用 cluster bootstrap 配对差值 CI（对话簇为重采样单元）；
5. 评估裁判固定 glm-5.2（当前最佳单裁判）；方法定稿后用 deepseek-v4-pro 复验一次
   泛化性（rubric 不应只对一个裁判有效）。

## 5. 消融矩阵（最终报告的表）

| 行 | 说明 |
|---|---|
| v1 基线 | 现行 rubric（judge_prompt v1） |
| 0a 重映射地板 | 不改 prompt 的校准上界 |
| 0b DPFS / DPFS+cal | 锚例校准 |
| 手工 J2b 变体 | 行为化锚点/判前先做（人工设计参照线） |
| 生成-K-选优 | 弱自动化基线 |
| GEPA 原味 | 强自动化基线（反思式自由文本变异） |
| 本方法（P1–P6 全开） | 及其去 P5、去 P6 的 2×2 消融 |

## 6. 预算

| 项 | 调用量 | 说明 |
|---|---|---|
| 0a | 0 | 纯离线（glm 的 dev 全量数据到位后） |
| 0b | ≈4,000 | 2 变体 × (1,202+801)，gateway |
| Stage 1/2 pilot（2 维度） | ≈15,000–20,000 | 每维 ~20 编辑候选 × 减半制评估 |
| GEPA/生成-K 基线 | ≈8,000 | 与本方法同预算对齐才公平 |
| Stage 3 终验 | ≈6,000 | test 一次 + dsv4-pro 复验 |

## 7. 风险与诚实预期

- **天花板**：BEA 官方参赛系统 macro-F1 仅 0.58–0.72，单人标注的噪声可能把可达 kappa
  卡在 0.5 上下；共识分裂率（bea 0.393）是噪声占比的旁证。进化平台期本身就是
  "瓶颈在标注一致性"的结论，负结果照样成文。
- **退化映射风险（0a）**：kappa 目标天然惩罚边缘塌缩，但仍需人工检查胜出映射是否
  语义合理（如 unparsed→Yes 属可疑）。
- **锚例泄漏**：锚例严禁来自评估片/test；脚本内断言。
- **英文迁移**：全部金标是英文数学 tutoring，进化出的 rubric 对中文教学未验证——
  与中文标注冲刺（300–500 条双标）的依赖不变，进化轨迹（编辑+诊断+验证记录）同时是
  J5 自训裁判的种子数据。

## 8. 执行顺序

1. Stage 0a 脚本 + dsv4-pro/M3 立即出数；glm 部分等全量 dev 跑完（进行中）自动补；
2. Stage 0b 等 glm 全量完成后发车（避免 gateway 争抢），~4k 调用；
3. Stage 0 报告 + 决策门评审（和用户过一遍再定 Stage 1/2 规模）；
4. Stage 1/2 pilot（2 个最弱维度）→ 消融 → Stage 3 终验。

---

## 附录 0：Stage 0 结果（2026-07-07）

输出：`reports/eval/_judge_rubric/stage0/{remap, mrbench_dpfs, mrbench_dpfs_cal,
bea2025_dpfs, bea2025_dpfs_cal}/summary.json`。评估片 = `split_dev_subsample_glm`
（mrbench 1,202 / bea2025 801），全部配对 cluster bootstrap n_boot=1000。

### 0a 重映射地板（六格全出）

| 裁判 | mrbench Δκ | bea2025 Δκ |
|---|---|---|
| glm-5.2 | 0.417→0.468（+0.050 显著） | 0.458→0.499（+0.041 显著） |
| MiniMax-M3 | 0.357→0.433（+0.076 显著） | 0.350→0.410（+0.060 显著） |
| deepseek-v4-pro | 0.399→0.426（+0.026 不显著） | 0.414→0.434（+0.020 显著） |

学到的映射高度一致为 **"To some extent"→"Yes"**（glm mrbench 8 维中 5 维学到同一条，
其余恒等）。M3 重映射后追平 glm 基线——其"弱"大半是校准而非理解。
实测到一例 winner's curse（dsv4 mrbench Revealing 学习池赢、评估片输），
坐实 P2/P3 的必要性。

### 0b DPFS 锚例（glm-5.2，全覆盖后终版）

首轮因裁判调用误设 `max_tokens=1024` 饿死 ~17% 难题响应（选择偏差，留存子集基线
虚高至 0.49–0.51），去 cap 补跑后全覆盖（unparsed 合计 2/4,006）：

| 组 | v1 → 变体 | 配对差值 | 显著 |
|---|---|---|---|
| mrbench / dpfs | 0.417→0.500 | +0.082 | 是 |
| mrbench / **dpfs_cal** | 0.417→**0.523** | **+0.106** | 是 |
| bea2025 / dpfs | 0.458→0.486 | +0.028 | 否 |
| bea2025 / **dpfs_cal** | 0.458→**0.516** | **+0.058** | 是 |

dpfs_cal（锚例+边缘分布提示）在两线所有维度上 ≥ dpfs；0b 全面超过 0a 地板
（mrbench 翻倍：+0.106 vs +0.050）。per-dimension 关键信号（mrbench dpfs_cal）：

- **大赢**：Tutor_Tone 0.334→0.598、Mistake_Location 0.250→0.422、
  humanlikeness 0.203→0.365、Mistake_Identification 0.494→0.599；
- **锚例免疫**：Providing_Guidance 0.383→0.400（重映射同样无效）——语义缺口维度，
  Stage 1 头号靶；
- **回退**：Revealing_of_the_Answer 0.884→0.806——本已近天花板的维度被锚例带偏，
  Stage 1 必须 **per-dimension 门控**（高分维度不动或保留 v1 段落）。

### 决策门判定

差距吃掉比例（dpfs_cal，天花板假设敏感性）：κ 上限取 0.7（同类主观标注典型
人际一致性）时 mrbench 37% / bea2025 24%；上限取 1.0（最保守）时 18% / 11%。
**落在 20–60% 档 → 按计划全量进入 Stage 1/2**，0a/0b 进消融表。
校准修正吃不完差距，剩余部分（尤其 Providing_Guidance / Coherence /
humanlikeness）需要诊断驱动的语义编辑。

Stage 1 派生要求：① per-dimension 门控（Revealing 教训）；② 0b+0a 叠加未测
（重映射需在锚例 prompt 的新输出分布上重学，需评估片外的锚例 prompt dev 数据，
留给 Stage 2 一并做）；③ pilot 靶维度定 **Providing_Guidance + Coherence**
（原计划"2 个最弱"按 0b 后残余差距重排）。

## 附录 1：Stage 1 pilot round 1 结果（2026-07-07，M3 裁判）

应用户要求，pilot 裁判改用 **MiniMax-M3**（成本考量；方法定稿后仍按协议迁移
glm-5.2 + dsv4-pro 复验）。基建：`scripts/build_judge_stage1_assets.py`（冻结
per-dim 评估片 ~600 条 / 筛选片 ~150 条，对话分组、纯 dev；诊断池 = dev 减评估片
对话，混淆矩阵 + 每格 8 错例带裁判自身推理摘录）+
`scripts/run_judge_rubric_stage1.py`（结构化 rubric {定义/每标签行为化判据/边界
条款/锚例块}，6 种类型化算子，反思模型 glm-5.2 产提案，round 1 固定注入 dpfs_cal
参照候选；筛选片淘汰 → 前 3 跑全量评估片 → 配对 cluster-bootstrap CI 下界 >0 且
unparsed 不回退才接受；ledger 记编辑+效应量+CI+prompt hash）。v1 空 rubric 渲染与
adapter prompt 字节级一致（断言）；v1 基线标签复用 M3 缓存全量跑，零重复开销。

### 结果（全量评估片，n_boot=1000）

| 线 | 胜者 | v1 → 胜者 kappa | 配对差值 | 显著 |
|---|---|---|---|---|
| mrbench / Providing_Guidance | **r1p3（接受）** | 0.272→**0.340** | **+0.068 [0.011, 0.126]** | 是 |
| mrbench / Coherence | 无 | 0.303（最好候选 −0.001） | — | 否 |
| bea2025 / Providing_Guidance | 无 | 0.341（最好候选 +0.032 [−0.021, 0.090]） | — | 否 |

mrbench PG 胜者 r1p3 = 一条边界条款："相关的引导性提问/提示即算 Yes，不要求明确
指出错误位置"——正对诊断里最大混淆格（human=Yes|judge=To some extent, 77 例）。
关键对照：**同维度 dpfs_cal 锚例参照 +0.007（ns）**，与 0a 重映射免疫互证——
Providing_Guidance 的缺陷确实是语义而非校准，且类型化语义编辑修得动。
新 incumbent `stage1-r1-r1p3` 已落盘。

观察：
- **Winner's curse 三次实测**（mrbench PG 筛选第一 r1p5 全量 ns；Coherence 筛选
  第一 r1p5 全量转负；bea PG 筛选第一 r1p6 全量转负）——"筛选只排序、验收看全量
  配对 CI"的两段制是必要的，不是仪式。
- bea PG 最好候选 r1p5 方向与 mrbench 胜者一致（判官因"引导不完全正确"过度降级）
  但 ns → round 2 值得在该方向上继续提案。
- Coherence 全部候选 ns 且偏负：v1 定义下 M3 kappa 0.303，诊断显示混淆集中在
  human=To some extent 行的散射，反思提案未能命中；候选方向留 round 2 重新诊断。

### 中断记录

round 2（mrbench PG，基于 r1p3 incumbent）反思提案已生成，筛选进行中 **MiniMax
Token Plan 配额耗尽（base_resp 2056，与限流 2062 不同）**——同一配额被用户
7 月 1 日启动的 run_eval.sh 批量评测（M2.7）共享。响应级断点续跑已就位，配额
恢复后重发同命令即续。脚本已加固：25 连败熔断（省重试）、空配对集不再崩溃。

### Round 2（2026-07-07，配额恢复后续跑）

两条线均无验收，incumbent 不变（协议：全量配对 CI 下界 >0 才接受）：

- **mrbench/PG**（incumbent = stage1-r1-r1p3, 0.340）：6 提案中 5 个筛选即负
  （叠加在已改进 rubric 上的编辑多数有害——静态 v1 诊断的边际提案质量在衰减）。
  唯一幸存者 **r2p3**（"To some extent"行为化判据：部分正确/部分相关/太模糊的引导）
  全量 **+0.055 [−0.0011, 0.1099]**——差 0.001 过线的近失。若过线累计将是
  v1 0.272→0.394（+0.123）。按协议不接受；r2p3 进 ledger 待 Stage 2/3 在
  不同数据上复验（同片重测到过线 = p-hacking，不做）。
- **bea2025/PG**（incumbent = v1）：3 个幸存者全量 +0.004~+0.013 全 ns。
  筛选 +0.087/+0.078 的两个头名再次全量缩水（winner's curse 第 4、5 次实测）。

### Pilot 结论与 Stage 2 派生要求

循环有效性验证完成（~13k M3 调用，预算内）：1 个显著验收（+0.068）+ 1 个近失；
"语义编辑修得动校准免疫维度"成立；两段制验收/熔断/断点续跑/ledger 全部实战过。
派生要求：④ **自适应重诊断**——round 2 的提案仍基于 v1 的错例诊断，与当前
incumbent 的实际错误分布脱节，Stage 2 必须在每轮验收后用 incumbent 在诊断池
（或其子样）上重打标再诊断（每轮 +~600 调用）；⑤ 筛选片 157 条的排序噪声大
（5 次 winner's curse），Stage 2 可考虑筛选片加大到 ~250 或两阶段减半。

### Round 3（Stage 2 升级版）+ 近失独立确认（2026-07-07 收官）

Stage 2 升级落地（`run_judge_rubric_stage1.py` --rediagnose --big-screen）：
自适应重诊断（incumbent 在池子样 600 条重打标，v1 incumbent 复用缓存零开销）、
0a 重映射叠加参照、历史编辑回归消融、筛选片 157→250（`__screen250.txt`）、
反思提示携带 ledger 既往战绩（禁止重复失败思路/允许打磨近失）。

Round 3 三线均无验收：
- **mrbench/PG**（incumbent r1p3）：重诊断显示池一致率 0.591→0.663；重映射叠加=
  恒等（无残余校准空间）；回归消融 r1p3 −0.055（编辑仍在赚钱）；新 6 候选筛选
  全负 → **r1p3 已是该维度提示编辑的局部最优**。
- **bea2025/PG**：r3p5（"合理教学性解读至少 TSE"）全量 +0.059 [−0.010, 0.129]，
  同方向第三次近失。
- **Coherence**：两轮 18 候选全灭，v1 0.303 即 M3 平台。

**近失独立确认**（`run_judge_rubric_confirm.py`：候选放到选择过程从未接触的
池子数据上重测，排除反思模型见过的错例；选择/确认数据分离）：
- mrbench r2p3：**−0.002 [−0.059, 0.059]**（n=559，ns）
- bea r3p5：**−0.001 [−0.044, 0.047]**（n=625，ns）

两个近失均为纯选择噪声（验收边界处的 winner's curse），不是功效不足掩盖的
真实小效应。**严格配对 CI 验收规则被独立数据背书**：若当时放宽验收，两条
无效编辑就进 rubric 了。

### Pilot 最终结论（M3 裁判，累计 ~25k 调用）

1. 有效收益 = **1 条验收编辑**（mrbench/PG r1p3，+0.068 sig，回归/确认俱在）；
   同场对照锚例 +0.007 ns → "语义编辑修得动校准免疫维度"成立但幅度有限。
2. 提示编辑的天花板很快到达：重诊断后候选全负、近失全被证伪 → 残余差距的
   主体大概率是**标注噪声/任务内在模糊性**（与 bea 三票分裂率 0.393、方案
   §7 诚实预期一致），不是 prompt 还没写对。
3. 方法学资产（这才是 pilot 的主要产出）：两段制筛选-验收 + 独立确认的三层
   防过拟合被 7 次 winner's curse 实测证明必要；自适应重诊断、回归消融、
   remap 叠加、熔断自愈全部实战化，可直接迁移 glm-5.2 主实验。

## 附录 2：glm-5.2 主实验（2026-07-08 启动，进行中）

用户拍板 pilot 收官后的方向 = **迁移 glm-5.2 复刻整套循环**（glm 是陪审团结论中的
最佳单裁判，基线 kappa 0.41~0.44；并发上限 6，用户指定）。裁判与反思模型均为
glm-5.2（走 gateway，`API_GATEWAY`），从 round 1 起即用 Stage 2 完整规格
（`--big-screen --rediagnose`）。

### 基建差异（相对 M3 pilot，2026-07-08 代码改动）

- **状态目录按裁判隔离**：`build_judge_stage1_assets.py::stage1_out_base(slug)`
  ——minimax3 保留原 `reports/eval/_judge_rubric/stage1/`（pilot 历史不动），
  其余裁判用 `stage1_<slug>/`。glm 实验状态在
  **`reports/eval/_judge_rubric/stage1_glm-5.2/`**（rubric_current / ledger /
  diagnosis / roundN 同 pilot 布局）。
- **滑片复用**：`stage1_slices/` 与裁判无关（同种子、byte 级一致，已复核），
  三条线仍是 600/601/605 条评估片 + 250 大筛选片。
- **诊断按裁判重建**：`python3 build_judge_stage1_assets.py --judge-slug glm-5.2`
  读 glm 缓存 v1 全量跑（mrbench_judge/glm-5.2 13,240 条、bea2025_judge/glm-5.2
  9,904 条，零增量调用）。
- 判官调用不设 max_tokens（glm-5.2 硬约束：设 1024 会饿死 ~17% 回复，见
  memory `gateway-model-thinking-behavior`）。

### glm 起点画像（v1 池诊断，与 M3 对照）

| 线 | glm 池一致率 | M3 池一致率 | glm 主混淆格 |
|---|---|---|---|
| mrbench/PG | 0.621 | 0.591 | human=**TSE→judge=No**（92 例，偏严） |
| mrbench/Coherence | 0.741 | — | — |
| bea2025/PG | 0.672 | — | 同样 TSE→No 为主 |

**关键差异：glm 的缺陷方向与 M3 相反**（M3 是 TSE→Yes 偏宽，r1p3 修的就是它；
glm 把部分引导判成无引导）。M3 验收的 r1p3 条款不应假设可迁移——glm 反思看的是
glm 自己的错例，这一轮同时检验方法普适性与"缺陷是否裁判特异"。

### 跟进 runbook（后续 LLM 从这里接手）

```bash
cd scripts && eval "$(grep -E '^export (API_GATEWAY|MINIMAX_API_KEY)=' ~/.bashrc)"
# 每轮一条线（断点续跑，重发同命令即续；25 连败熔断）：
STAGE1_JUDGE_MODEL=glm-5.2 python3 run_judge_rubric_stage1.py \
  --benchmark mrbench --dimension Providing_Guidance --round <N> \
  --big-screen --rediagnose --concurrency 6
```

- 验收协议不变：筛选只排序 → 前 3 全量 → 配对 CI 下界 >0 + unparsed 守卫；
  近失禁止同片重测，走 `run_judge_rubric_confirm.py`（需在 CONFIRMS 里登记新
  条目；该脚本从 runner 继承 `STAGE1_JUDGE_MODEL`，跑 glm 确认时必须带同样的
  env）。结果看 `stage1_glm-5.2/<bench>__<dim>/round<N>/summary.json` 与
  `ledger.jsonl`。
- Round 1（三线顺序，每线 ~2,800 调用）2026-07-08 已在后台启动
  （scratchpad `run_glm_round1.sh`）。
- 停机条件同 pilot：重诊断后候选全负 / 连续一轮无验收且无近失 → 该线收官。
- 完结后的待决项（用户拍板）：① 消融基线（§5：GEPA 原味、生成-K-选优、手工
  J2b）；② Stage 3 test split 一次性终验（M3 的 r1p3 + glm 的验收成果一起）；
  ③ 生产裁判 M3→glm-5.2 切换（证据已齐，见 judge_research_plan 附录 0）。
