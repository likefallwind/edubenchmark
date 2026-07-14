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
| 本方法（P1–P5 全开） | 及其去 P5（去诊断）消融；P6 未接入主循环，不参与消融 |

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
- 停机条件同 pilot：重诊断后候选全负 / 连续一轮无验收且无近失 → 该线收官。

### Round 1 结果（2026-07-08，三线全部验收，3/3）

| 线 | 胜者 | v1 → 新 kappa（评估片） | 配对差值 | dpfs_cal 参照 |
|---|---|---|---|---|
| mrbench/PG | **r1p2** | 0.322→**0.438** | **+0.116 [0.055, 0.174]** sig | 筛选即淘汰 |
| bea2025/PG | **r1p1** | 0.392→**0.484** | **+0.092 [0.028, 0.163]** sig | +0.031 ns |
| mrbench/Coherence | **r1p3** | 0.268→**0.318** | **+0.050 [0.006, 0.099]** sig | +0.034 ns |

- 验收编辑全部命中起点画像预测的 TSE→No 偏严格（mrbench = TSE 行为化判据
  "试图引导但误诊/有瑕疵→TSE 非 No"；bea = 定义改写 + 同判据；Coherence =
  "罐头衔接短语不回应学生具体输入→No"条款）。**与 M3 的验收方向相反 →
  缺陷是裁判特异的，方法迁移、条款不迁移（假设证实）。**
- **Coherence 被修动**推翻 pilot 的"标注噪声天花板"定性：M3 两轮 18 候选
  全灭是 M3 能力平台，非任务不可修。
- 校准手段在 glm 上继续陪跑（dpfs_cal 三线全 ns；remap 叠加恒等或为负）——
  "语义编辑 > 校准"在第二个裁判复现。
- glm 单轮收益（+0.116/+0.092/+0.050）远超 M3 全程唯一验收（+0.068），
  glm 对 rubric 语义的响应能力显著更强。
### Round 2 结果（2026-07-09）

| 线 | 结果 | 细节 |
|---|---|---|
| mrbench/Coherence | **r2p1 验收** | +0.082 [0.039, 0.123] sig，累计 0.268→**0.400**；条款="纠错/重读题目/换步骤建议是连贯教学回应，不判 No/TSE"；亚军 r2p2 也独立显著（+0.080） |
| mrbench/PG | 无验收 | 最好 r2p5 +0.035 [−0.016, 0.088] ns（边缘近失）；回归消融 r1p2 −0.086（仍在赚钱） |
| bea2025/PG | 无验收 → **收官** | 两幸存者全量转负（−0.005/−0.014），停机条件触发；终版 = stage1-r1-r1p1（0.484） |

- Coherence 与 M3 的对比进一步拉大：M3 该维度 18 候选全灭（平台 0.303），
  glm 两轮两验收累计 +0.132——"残余差距 = 标注噪声"的定性必须按裁判分别下。
- Round 3（Coherence 继续 + mrbench/PG 末轮打磨 r2p5 方向）2026-07-09 已启动
  （scratchpad `run_glm_round3.sh`）。bea 线若需要近失确认：r2 无近失，无需确认。

### Round 3 结果（2026-07-09）——两线无验收，进入收尾

- **mrbench/Coherence 收官**：唯一筛选过线的 r3p1 全量转负（−0.016）→ 终版
  **stage1-r2-r2p1（0.268→0.400，+0.132）**。收官时池一致率 0.817（v1 0.747）、
  重映射恒等、回归消融两条编辑均在赚钱（−0.097/−0.087）。
- **mrbench/PG**：最好 r3p3 +0.037 [−0.013, 0.085] ns——连续第二轮同区域边缘
  候选（r2 的 r2p5 +0.035）。按 pilot 先例走**独立确认**
  （`run_judge_rubric_confirm.py --confirm glm_mrbench_pg_r3p3`，须带
  `STAGE1_JUDGE_MODEL=glm-5.2`；确认集 = 重诊断池子样 600 条减反思见过的错例，
  incumbent r1p2 标签已缓存）。确认过线才收，否则定性选择噪声、
  线收官于 stage1-r1-r1p2（0.438）。
- **r3p3 独立确认（2026-07-09）：+0.016 [−0.035, 0.060] ns（n=532）**——
  选择片 +0.037 缩水过半且不显著 → 选择噪声（近失确认归零/缩水累计第 8 例），
  mrbench/PG 收官于 stage1-r1-r1p2。

### glm-5.2 实验最终结论（2026-07-09 收官，累计 ~22k glm 调用）

三线终版（评估片 kappa，全部显著验收、回归消融/确认俱在）：

| 线 | v1 → 终版 | 累计增益 | 验收轮次 |
|---|---|---|---|
| mrbench/Providing_Guidance | 0.322 → **0.438** | +0.116 | r1（r1p2） |
| bea2025/Providing_Guidance | 0.392 → **0.484** | +0.092 | r1（r1p1） |
| mrbench/Coherence | 0.268 → **0.400** | +0.132 | r1+r2（r1p3, r2p1） |

1. **方法完全迁移，条款完全不迁移**：glm 的验收编辑全修 TSE→No 偏严
   （M3 修的是 TSE→Yes 偏宽，方向相反）——rubric 进化必须按裁判跑，
   诊断驱动是方法有效的原因而非装饰。
2. **收益是 M3 的 3~5 倍**（4 条验收 vs 1 条；+0.34 总增益 vs +0.068）：
   更强的裁判对 rubric 语义的响应能力更强，"弱裁判省成本"在进化收益上是
   假节省。
3. **M3 pilot 的"标注噪声天花板"定性被修正**：Coherence（M3 18 候选全灭）
   在 glm 手里两轮验收 +0.132。残余差距的裁判能力成分比 pilot 估计的大；
   任务内在噪声的定量归因留给 Stage 3 / 消融。
4. 校准手段全程陪跑（dpfs_cal 三线 ns、remap 恒等）+ 平台出现在第 2~3 轮
   + 近失确认再次缩水（第 8 例）——pilot 的三层防过拟合结论在第二个裁判
   完整复现。
5. 收官时三线仍偏严（TSE→No 残余），但可修部分已被典型条款吃掉；
   进一步收益需换表示（Stage 3 前不再加轮次）。

**下一步待决（用户拍板）**：① 消融基线（§5）用 glm 跑（GEPA 原味/生成-K-选优/
手工 J2b，与本循环同预算对齐）；② Stage 3 test split 一次性终验（M3 r1p3 +
glm 三线终版一起上）；③ 生产裁判 M3→glm-5.2 切换（证据链现已包含进化后
rubric 的差距）。
- 完结后的待决项（用户拍板）：① 消融基线（§5：GEPA 原味、生成-K-选优、手工
  J2b）；② Stage 3 test split 一次性终验（M3 的 r1p3 + glm 的验收成果一起）；
  ③ 生产裁判 M3→glm-5.2 切换（证据已齐，见 judge_research_plan 附录 0）。

## 附录 3：Stage 2 消融基线（2026-07-10 收官，glm-5.2 判官）

三条主实验线上跑齐三个参照基线，**共享全方法的 infra**（`Renderer` 渲染 /
`run_candidate` 断点续跑 / `paired_eval` cluster-bootstrap 配对 CI），评估片、判官
（glm-5.2）、打分与主实验逐字节一致——**只有"候选如何提出/挑选"不同**。运行器
`scripts/run_judge_rubric_ablation.py`，产物在
`reports/eval/_judge_rubric/stage1_glm-5.2/<line>/ablation/`。

### 预算政策（与 §6 的偏差与理由）

§6 原定"与本方法同预算对齐 ≈8,000"。全方法**实测**每线 glm 花费为
8,731 / 5,643 / 8,566 次（`MEASURED_BUDGET`，各 `responses.jsonl` 行数之和）。
本轮取 **BUDGET=3,000 次/线**（≈全方法**第 1 轮**生产性搜索：6 候选筛选 + 3 存活
全量片 ≈3.3k，收益的大头正是在这轮拿到的）。降到 ~1/3 算力是因为 gateway 与用户
olympiadbench batch 共享，满预算需 ~3× 算力、ETA 数天。全预算对齐留作后续可选复现
（`--budget 0` 读 `MEASURED_BUDGET`）。此降预算**对基线有利**（搜索越多越可能撞上
显著或过拟合），故不削弱下述结论。

### 结果矩阵（Δκ vs v1，n≈600/线，95% cluster-bootstrap 配对 CI）

| 行 | 搜索策略 | mrbench/PG | bea/PG | mrbench/Coherence | 显著线 |
|---|---|---|---|---|---|
| v1 基线 | 现行 rubric | 0.322 | 0.392 | 0.268 | — |
| 0a 重映射地板※ | 后验标签重映射（零 API） | +0.050 ✓ | +0.041 ✓ | — | 基准级 |
| 0b DPFS+cal※ | 锚例校准 | +0.017 ns | — | — | 基准级 |
| **手工 J2b** | 人工 rubric，盲于诊断 | +0.032 ns | +0.010 ns | +0.034 ns | **0/3** |
| **生成-K-选优** | K=5 自由文本规则，raw κ 挑最优¹ | −0.001 ns | +0.005 ns | +0.029 ns | **0/3** |
| **GEPA 原味** | 反射式整段重写，val 贪心接受 | +0.054 ns | **−0.126 ✓劣化** | +0.048 ns | **0/3** |
| **全方法（P1–P6）** | 诊断驱动 + 显著性门控 | **+0.116 ✓** | **+0.092 ✓** | **+0.132 ✓** | **3/3** |

※ 0a/0b 系 Stage 0 的**基准级聚合**（8 维平均，见附录 0），与本轮**单维**粒度不同，
仅作方向参照。附录 0 已给出 mrbench/PG 的单维锚例免疫点 **0.383→0.400（+0.017 ns，
重映射同样无效）**——PG 是"语义缺口维度"，校准手段够不着，恰好预示手工/genk 在 PG
上也只能拿噪声级漂移。
¹ genk 用"在评估片上挑最高 κ"的**乐观上界**（正常应在 held-out 挑；此处故意放水），
最优候选仍全不显著。

### 三个基线各自的失败模式（互不相同，正是消融想要的）

1. **手工 J2b**：三线均正向小漂移（+0.010~+0.034），CI 全含零。人工把 rubric 写得
   规整（行为化标签锚点 + "判前先想理想教学动作"）但盲于诊断 → 噪声级提升。人工设计
   的上限不在文笔，在"知道往哪改"。
2. **生成-K-选优**：即便按乐观上界挑，最优也只 +0.03；mrbench/PG 甚至 −0.001
   （K 候选 κ 分布 min 0.216 / med 0.310 / max 0.321，全贴着或低于 v1）。加大搜索
   宽度救不了无方向搜索。
3. **GEPA 原味（最有说服力）**：三线冠军在 val 上 κ 分别 **0.542 / 0.594 / 0.690**，
   都比全方法漂亮——但落到 eval：**0.265 / 0.376 / 0.316**，其中 bea/PG **显著跌破
   v1（−0.126）**。经典过拟合：自由文本整段重写 + 无显著性门控 = 把 val 噪声当信号。
   这正是全方法坚持 cluster-bootstrap 配对 CI 验收门的直接理由——本消融把"防过拟合"
   从设计信念变成了实测证据（累计第 9 例 winner's curse 家族现象）。

### 结论

**收益来自"诊断驱动 + 显著性门控"，不来自搜索宽度（genk）、文本自由度（GEPA）或
人工精雕（manual）。** 在与主实验逐字节一致的评估/判官/打分下，三个参照基线在 3 条线
共 9 格中零显著提升，GEPA 还制造了一次显著劣化；全方法 3/3 显著。§5 消融矩阵至此闭合
（P5/P6 的 2×2 去除消融未单跑，其必要性由 GEPA 的过拟合劣化与 pilot 的 winner's-curse
系列间接坐实）。下一步仍是待决项 ②/③（Stage 3 终验 / 生产裁判切换），需用户拍板。

## 附录 4：Stage 3 test-split 终验（2026-07-10，glm-5.2 判官）

封存的 test 人类金标**首次也是唯一一次**被触碰（协议 §4.1）。运行器
`scripts/run_judge_rubric_stage3.py`：在 test 片上跑 v1 与进化 rubric，各自 vs 人类
金标算 κ，配对 cluster-bootstrap CI。复用 stage1 全套渲染/判官/打分机器，只把评估集
换成 `split == test`。发车前硬断言 test 与 dev 的 eval/pool/对话簇零重叠（全过）；三条
进化 rubric 皆类型化编辑、无锚例 → 零泄漏。产物在 `stage1_glm-5.2/<line>/stage3/`。

### 结果：3 条线只有 1 条在 test 上复现

| 线 | 进化版本 | v1(test) | 进化(test) | test Δ vs v1 | 95% CI | 显著 | dev 曾经 | 复现 |
|---|---|---|---|---|---|---|---|---|
| mrbench/PG | r1p2 | 0.394 | **0.508** | **+0.115** | [+0.049, +0.185] | **是** | +0.116 ✓ | **✅** |
| mrbench/Coherence | r2p1 | 0.430 | 0.431 | +0.002 | [−0.080, +0.110] | 否 | +0.132 ✓ | ❌ |
| bea2025/PG | r1p1 | 0.477 | 0.465 | −0.012 | [−0.081, +0.056] | 否 | +0.092 ✓ | ❌ |
| **mrbench/PG（M3 pilot）** | r1p3 | 0.315 | **0.389** | **+0.074** | [+0.009, +0.137] | **是** | +0.068 ✓ | **✅** |

n=417（bea 623），n_boot=1000。前三行判官 glm-5.2；第四行判官 MiniMax-M3
（`STAGE1_JUDGE_MODEL=MiniMax-M3`，验 `stage1/mrbench__Providing_Guidance/rubric_current.json`）。

**M3 收尾**：M3 pilot 唯一验收编辑 r1p3 在 test 上也干净复现（dev +0.068 → test +0.074，
双显著）。**两个判官在 mrbench/PG 上各自进化出的编辑都过了 test 门**——该维度的"引导性
提问即算 Yes / TSE 偏严"病灶是任务级真缺陷，跨判官稳健可修。M3 pilot 因此**净成果非零**：
产出 1 条经 test 验证的真提升（虽仅 1 条 vs glm 的多条，仍坐实"更强判官进化产出率更高"，
但不等于弱判官进化毫无收益）。

### 为什么两条塌了：严格门控也拦不住的"dev 分布过拟合"

关键观察——**v1 在 test 上本就显著高于 dev**（mrbench/PG 0.322→0.394、Coherence
0.268→**0.430**、bea/PG 0.392→**0.477**）：test 片更干净（标注噪声小、簇更一致）。
进化编辑修的是 **dev 诊断里发现的特定 TSE→No 偏严模式**：

- **mrbench/PG**：该模式在 test 上依然存在 → 编辑修到真病灶 → +0.115 干净复现。**这是任务级真提升。**
- **Coherence / bea/PG**：dev 病灶在更干净的 test 上本就不明显（v1 已 0.43/0.48）→
  编辑修的是 dev 特有噪声 → test 上无物可修，归零甚至微负。

这是 cluster-bootstrap 配对 CI 门控**也拦不住**的过拟合层级：dev 上的 κ 提升真实、可
复现（配对 CI 全过），但它是"对 dev 标注分布"的真提升，非"对任务"的真提升。**只有独立
test 终验能区分这两者**——本阶段兑现了这道门存在的全部意义（消融的 GEPA 是"选择噪声当
信号"，本阶段是更隐蔽的"dev 分布特异性被当作能力"，二者互补）。

### 生产切换（2026-07-10 已落地，用户拍板）

两个动作均已写入代码：

- **③a 换判官模型 M3→glm-5.2**（✅ 已做）：`mrbench.py` + `bea2025.py` 的
  `DEFAULT_JUDGE_MODEL` 改 glm-5.2。证据来自 judge_research 附录 0（glm 为这两条
  dimension-label 线的最佳单裁判），**与 rubric 结果无关，独立成立**。
  **范围仅这两条**：mathtutorbench（pairwise，glm 最佳无证据；但 M3 有实测长度偏置，
  留作后续换判据）、mmtutorbench（多模态判官，未进 meta-eval）、eduguard（安全判官，
  同）**一律不动**——盲切无证据支撑。`MRBENCH_JUDGE_MODEL`/`BEA2025_JUDGE_MODEL` 仍可覆盖。
- **③b 换 rubric v2**（✅ 已做，仅 mrbench/PG）：`mrbench.py` 新增 `_evolved_judge_prompt`，
  把 r1p2 的 `To some extent` 标签准则注入**仅 tutor 固定生产判官**（`_judge_one`），
  经断言**与 test 上验证的 stage1 Renderer 渲染 byte 完全一致**（上生产的 == 验证过的）；
  `PRODUCTION_JUDGE_PROMPT_VERSION="v2"`，provenance 记 `evolved_dimensions=["Providing_Guidance"]`。
  **`mrbench_judge` 校准基准保持 v1**（它测被测模型的判官能力，prompt 不能漂）；其余 7 维 == v1。
  **Coherence 与 bea/PG 保留 v1**（dev 增益系过拟合，未过 test，不上生产）。

方法论层面这是**正结果**：自进化能产出任务级真提升（**mrbench/PG 被两个判官各自独立
进化 + dev/test 双验**，是最稳健的赢家），但 glm 三线 test 存活率 1/3——需要 test 终验做
最后闸门，dev 显著性不足以直接上生产。负结果照样成文，且强化了"每条线独立 test 验收、
不整批上"的工程纪律。跨判官看：唯一双判官都过 test 的维度是 mrbench/PG（引导性提问算 Yes /
TSE 偏严病灶），是全流程最可靠的一处真实能力缺口。

## 附录 5：纯 M3 自举对照实验（judge=reflector=MiniMax-M3，2026-07-12 收官）

**动机**：附录 2 的"glm 4 验收 vs M3 1 验收"存在两个混淆——pilot 前两轮协议较轻
（静态 v1 诊断 + 157 筛选片）、且 pilot 的提案由 glm-5.2 代写（混合配置），而 glm
主实验是"自己进化自己"。本实验补 **judge=reflector=MiniMax-M3** 的完整 Stage 2 规格
（--big-screen 250 + --rediagnose，切片与 glm 逐字节相同），与 glm 自进化完全对称。

**基建**：`STAGE1_REFLECT_MODEL`（反思模型 env 覆盖）+ `STAGE1_OUT_SLUG`（状态目录
隔离，本实验 `stage1_minimax3_self/`；另备 `stage1_minimax3_full/` = glm 反思版对照
arm，因配额与"对称性更优"改道，脚本 `run_judge_stage1_m3_full.sh` 保留未跑完）。
v1 标签复用 minimax3 缓存全量跑（零开销）。启动脚本 `scripts/run_judge_stage1_m3_self.sh
[round]`，日志自写 `stage1_minimax3_self/round<N>_run.log`。2 轮 ≈17k M3 调用。

**结果**（评估片配对 cluster-bootstrap CI，n_boot=1000）：

| 线 | round 1 | round 2 | 终局 |
|---|---|---|---|
| mrbench/PG | **r1p3 验收** 0.272→0.365（+0.094 [0.026, 0.164]，add_clause 放宽 TSE→No 过严） | 重诊断后候选全负；回归消融 r1p3 −0.043 仍在赚钱；remap 叠加恒等 | r1p3 局部最优，收官 |
| mrbench/Coherence | 最好 +0.032 ns | 最好 r2p3 +0.058 [−0.011, 0.132] ns | 近失 r2p3 独立确认（n=558）**−0.059 [−0.145, 0.036]**，方向翻负 → 选择噪声，收官 |
| bea2025/PG | 最好 +0.015 ns（筛选头名 r1p6 +0.075 全量现形） | 最好 +0.007 ns | 两轮无验收无近失，收官 |

r1p3 验收后重诊断池一致率 0.597→0.665。勘误（07-12 复核）：Coherence r2p3 按 glm 判例应算边缘近失，已登记独立确认；PG/bea 无近失。

**结论**：① 同规格对称对比落定——glm 自进化 round 1 即 3/3 验收 vs 纯 M3 1/3，
"强裁判进化收益大"排除协议混淆；② M3 瓶颈在判分不在写提案——同线 M3 自写提案
+0.094 > pilot glm 代写 +0.068（且两次验收的编辑针对不同混淆格）；③ winner's curse
再添 2 例（累计 11 例家族），两段制照拦。**证据边界**：test 已在 Stage 3 开封用掉，
本实验验收 rubric 仅有 dev 证据。报告见 judge_research_full_report §6.1。

## 附录 6：deepseek-v4-pro 自举复验（judge=reflector=deepseek-v4-pro，2026-07-12）

**动机**：协议预留的第三裁判复验（裁判 n=2→3），与 glm 主实验、纯 M3 自举
逐项对称：同三条线、250 题大筛选片、每轮自适应重诊断、相同冻结评估切片、
相同 CI 下界验收门，唯一变量是裁判本身。

**基建**：`scripts/run_judge_stage1_dsv4_self.sh [round] [lines]`
（`STAGE1_JUDGE_MODEL=STAGE1_REFLECT_MODEL=deepseek-v4-pro`，走 gateway；
第二参数选线 all/mrbench_pg/mrbench_coh/bea_pg，round 3 起只跑未收官线）。
状态目录 `reports/eval/_judge_rubric/stage1_deepseek-v4-pro/`，日志
`roundN_run.log` 同目录。前两轮约 15k 次调用。

**结果**（评估片配对 cluster-bootstrap CI，n_boot=1000）：

| 线 | round 1 | round 2 | 终局 |
|---|---|---|---|
| mrbench/PG | 唯一幸存者 r1p4 +0.028 ns，空手 | **r2p2 验收** 0.319→0.406（**+0.087 [0.034, 0.140]**，add_clause："带事实错误但仍在往具体步骤引导 → TSE 而非 No"） | round 3（新 incumbent 重诊断）三决赛候选全量全部翻负（r3p6 −0.018 / r3p3 −0.022 / r3p2 −0.046，筛选分却全为正 → winner's curse 第 13 例），无验收无近失，**收官于 stage1-r2-r2p2** |
| mrbench/Coherence | 筛选头名 r1p4 筛 +0.040 → 全量 −0.026 翻负（winner's curse 第 12 例）；最好 +0.036 ns | 重诊断后 r2p5 +0.042 [−0.006] / r2p6 +0.042 [−0.013] 均 ns | 两个近失独立确认（n=556）**双双显著变差**：−0.105 [−0.186, −0.027] / −0.097 [−0.169, −0.025] → 收官 |
| bea2025/PG | 唯一幸存者是校准参照 dpfs_cal +0.029 ns | 最好 +0.031 ns | 两轮无验收无近失，收官 |

**结论**：① 三裁判梯度成形——glm 一轮 3/3（累计 +0.34）、M3 一轮 1/3（+0.094）、
dsv4 两轮 1/3（+0.087），方法普适、节奏随裁判变化，零假验收；② 失败台账（P4）
第一次单独救活一条线——round 1 三线空手，round 2 反思吃着 round 1 失败台账
换打法直接命中显著验收，"一轮定生死"的协议会错判 dsv4 为"修不动"；③ dsv4 与
glm 在 mrbench/PG 同一混淆格（人类 TSE、裁判 No，过严）独立收敛到几乎同一句
处方，把该线"任务级 rubric 缺口"的证据加厚到第三个裁判（dsv4 份 dev-only）。
**证据边界**：test 已封，验收 rubric 仅 dev 证据。round 3 已跑完（2026-07-12 22:18，winner=none），mrbench/PG 走完"验收 → 重诊断收官轮"完整闭环；剩余未了项只有 Coherence 的两个近失独立确认。
报告见 judge_research_full_report §6.2。

## 附录 7：近失独立确认总账 + 下游排名（2026-07-13 收官）

**近失确认 6 战 6 败**（`scripts/run_judge_rubric_confirm.py`，确认集与选择切片零重叠、
剔除反思见过的错例、incumbent 标签走缓存）：

| 确认 key | 选择片 | 确认集 | n |
|---|---|---|---|
| `mrbench_pg_r2p3`（pilot/M3） | +0.055 [−0.001, 0.110] | −0.002 [−0.059, 0.059] ns | 559 |
| `bea2025_pg_r3p5`（pilot/M3） | +0.059 [−0.010, 0.129] | −0.001 [−0.044, 0.047] ns | 625 |
| `glm_mrbench_pg_r3p3` | +0.037 [−0.013, 0.085] | +0.016 [−0.035, 0.060] ns | 532 |
| `m3self_mrbench_coh_r2p3` | +0.058 [−0.011, 0.132] | **−0.059** [−0.145, 0.036] ns | 558 |
| `dsv4_mrbench_coh_r2p5` | +0.042 [−0.006, 0.096] | **−0.105 [−0.186, −0.027] 显著变差** | 556 |
| `dsv4_mrbench_coh_r2p6` | +0.042 [−0.013, 0.096] | **−0.097 [−0.169, −0.025] 显著变差** | 556 |

**基建修正**：v1-incumbent 的线原本配成 `conf_source: pool_remainder`，但 mrbench 池只有
637 题、重诊断子样本占 605 题，剩余 <30 题（CI ±0.2，无判别力）。改为 `rediag_subsample`
（v1 标签取缓存全量跑，零额外 incumbent 调用），n≈556 起。**确认集功效先算再跑**。

**下游排名**（`scripts/run_judge_downstream_ranking.py`，判官 glm-5.2，3 被测模型 ×200 题
×4 调用 = 2,400）：排名 v1/v2 完全一致（glm-5.2 > minimax3 > MiniMax-M2.7），
通过率 v2 下移（0.950→0.935 ns / 0.925→0.895 sig / 0.885→0.840 sig），
模型极差 0.065→0.095、排名自助稳定性 0.847→0.914。翻转以 Yes→TSE（19）与 No→TSE（13）
为主，正是 v2 那条编辑的作用。**坑**：首跑判官调用带 `max_tokens=1024`，glm 内联 CoT
吃光预算 → 空 content → unparsed 按 fail 计分（v2 中招 70 次 vs v1 17 次），伪造出
"v2 暴跌 6~10pp"；去掉上限重跑后 unparsed 归零。报告见 full_report §6.3 / §8.1。
