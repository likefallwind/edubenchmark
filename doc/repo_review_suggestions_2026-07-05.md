# 仓库整体评估与建议（2026-07-05）

> 目标读者：本仓库维护者。范围：对照「做全面、公正的 AI 教育 benchmark + LLM-as-judge 研究（rubric prompt → 自训对齐裁判模型）」这一目标，评估当前仓库状态并给出建议。结合了 2026-07 的网上调研（文末附来源）。

---

## 一、总体判断：已经做对的事

先说结论：这个仓库的**方法论底子在同类工作里是偏严格的**，以下几点值得保持、不要在后续迭代里丢掉：

1. **可追溯性**：每题带 `source_file` + `source_row_or_key`，manifest 用 `local_ready` / `coverage_gap` 等状态词诚实记录数据可得性，不把 proxy 当原生覆盖。这是"公正"的地基。
2. **裁判校准先行**：`mathtutorbench_judge_calibration` / `mrbench_judge` / `bea2025_judge` 三条线都是"先用人类金标校准裁判，再让裁判上岗"，而且被测/抽取/裁判三个模型解耦、win-rate 任务做了位置交换去偏。这个流程比大多数公开教育评测严格（很多论文直接拿 GPT-4 当裁判不做校准）。
3. **不跨 benchmark 平均、通用题只当门槛项**的解读守则，写进了 README guardrails。
4. **数据质量审计有实绩**：独立发现 EduGuard SATA 上游答案错位（1,333/2,635）并用官方 Results 多数投票重建、与上游修复版逐题一致——这说明"物化数据时做一致性校验"的习惯是有效的，建议把它固化为每个新 adapter 的接入清单项。
5. **原子能力体系在持续自我审计**（P01–P20 场景覆盖压力测试），并且明确标出了 🔴 真缺口而不是硬塞进现有维度。

下面的建议按主题分组，每组内按优先级排序。

---

## 二、LLM-as-Judge 研究路线（当前最值得投入的方向）

### 2.1 现状盘点（基于仓库内已有数据）

已完成的裁判校准结果汇总（全量跑）：

| 校准集 | n | 最佳裁判 | 关键数字 |
|---|---|---|---|
| mathtutorbench（482 专家偏好对 ×2 序） | 964 | MiniMax-M3 0.844 / glm-5.2 0.839 | agreement 0.81–0.84，各家差距很小 |
| mrbench_judge（8 维 ×13,240） | 13,240 | deepseek-v4-pro | agreement 0.719，macro-F1 0.524，**kappa 0.40** |
| bea2025_judge（4 维 ×9,904） | 9,904 | deepseek-v4-pro | exact acc 0.668，**kappa 0.404**，lenient acc 0.788 |

**核心事实：当前最好的通用大模型做教学维度裁判，与人类的 Cohen's kappa 只有 ≈0.40（moderate agreement），而 BEA 2025 官方 findings 里专门优化过的参赛系统最好也只到 3-class macro-F1 ≈0.58–0.72。** 这说明两点：(a) 现成模型 + 现成 rubric 的天花板不高，"裁判可靠性"本身就是要害问题，不是工程细节；(b) 你的校准数字和领域最好水平在同一量级，说明 harness 没有大的实现问题，剩下的提升要靠方法（rubric 设计、集成、微调）。

### 2.2 建议 J1：把三条校准线合并成一个正式的「教育裁判元评测集」（P0）

`scripts/build_judge_calibration_report.py` 已经在做合并展示，建议再往前一步，把它升级为**版本化的数据资产**而不只是报告：

- 统一 schema：`(context, response, dimension, human_label, source_benchmark, language)`，把 MRBench 13,240、BEA dev 9,904、MathTutorBench 偏好对 964 全部纳入，做去重（BEA 的 MRBench_V3 与 MRBench_V2 有血缘，需按 dialogue id 去重，避免元评测集内部泄漏）。
- 切出固定的 dev/test split 并写入 manifest。**这一步是后面"自训裁判"的前提**：训练用 dev，选模型/报告用 test，否则未来训出的裁判分数不可信。
- 这个元评测集本身就是可发表的贡献（教育域的 JudgeBench / RewardBench 类似物，目前没有公开对应物）。EduGuard 数据错位的发现也证明你们有能力做这类"评测的评测"。

### 2.3 建议 J2：rubric prompt 做成受控实验，而不是各 adapter 各写各的（P0）

目前每个 adapter 的 judge prompt 是独立硬编码的，rubric 研究没有统一的实验面。建议：

- 建一个 **judge prompt registry**（`scripts/eval/judge_prompts/`，带版本号），`summary.json` 里记录 `judge_prompt_version` + prompt hash。没有这个，后面任何 rubric 改进都无法归因。
- 在 J1 的元评测集上系统消融，文献里已知最有效的几个变量：
  1. **rubric 粒度**：整体打分 vs 每维单独判（你们已按维拆分，方向对）；rubric 里给**行为化锚点描述**（什么样的回复算 "Yes, but not precisely"）比抽象定义有效；
  2. **少样本人类锚点**：每档附 1–2 个人类标注过的真实例子（从 dev split 取），是提升 kappa 最便宜的手段；
  3. **判前先做**（"Do Before You Judge"/S2J 一路的发现）：让裁判先自己解题/写理想回复再对照评判，对数学类维度（Mistake_Identification / Mistake_Location）通常有明显提升——这两维恰好是你们 headline pass rate 的关键维；
  4. CoT 输出结构：先摘证据再给标签，降低 `unparsed` 率。
- 每次消融跑同一个固定 test split，产出 kappa + CI，进 `html_report/judge_calibration_report.html` 的时间序列。

### 2.4 建议 J3：补一套系统性的裁判偏置测试（P1）

已有 position_consistency（好），建议补齐成完整的 bias battery，在元评测集上一次性跑：

- **长度偏置**：把 agreement 按 response 长度分桶回归，教学场景裁判普遍偏爱更长的"看起来更耐心"的回复，而好的脚手架恰恰应该短——这是教育域特有的风险；
- **自偏好（self-preference）**：当前 MiniMax-M3 既当裁判又是被测模型（mrbench_tutor / bea2025_tutor / mmtutorbench 的默认 judge），这在对外报告里是硬伤，见 3.1；
- **风格/语气偏置**：同内容不同语气（鼓励式 vs 中性）的扰动对；
- **语言偏置**：EduGuard 是双语的，判中文回复和英文回复的 kappa 是否一致，直接关系"中文教育"这一主战场。

### 2.5 建议 J4：单裁判 → 异质陪审团（P1，性价比高）

eduguard_adversarial 已经在用 BoN=3（同一裁判自投票）。文献（PoLL、meta-judging 一线）比较一致的结论是：**多个不同家族的中等模型投票，通常比单个最强模型更接近人类、且天然稀释自偏好**。你们的基础设施已经支持多 provider，改造成本低：

- 在元评测集上对比：单 deepseek-v4-pro vs {deepseek-v4-flash, MiniMax-M3, glm-5.2} 多数投票 vs 加权投票（按各自校准 kappa 加权）；
- 分歧样本（3 票不一致）单独落盘——这既是"该送人工复核"的路由信号，也是未来训练数据里信息量最大的部分。

### 2.6 建议 J5：自训裁判模型的路线图（P1→P2）

自训是对的方向，但建议明确分两步走，先收数据、后训练：

1. **数据面（现在就能开始）**：
   - J1 元评测集 dev split ≈ 2 万条人类标注判例（英文为主）是 SFT 底料；
   - 每次 J4 陪审团运行的**多裁判输出 + 分歧标记 + rationale** 持续落盘，作为增广数据；
   - **最大的缺口是中文教学判例**。现有人类金标（MRBench/BEA/MathTutorBench）全是英文数学 tutoring；中文裁判训练数据基本要自建。建议先做一个小规模（300–500 条、双人标注、报 IAA）的中文教学反馈标注冲刺，既当中文校准集又当训练种子。这一条建议同步登记进 `benchmark-todo.md`。
2. **训练面（数据齐后）**：
   - 起点用 SFT（label + rationale），7B–14B 开源底座即可——RM-R1/Think-J 一线的结果表明训练过的 7B–32B 生成式裁判在 RewardBench 类任务上能超过 70B+ 通用模型；教育域近期的 PEARL（arXiv 2605.29582，训 Socratic tutor 的教学奖励模型）和 MathTutorBench 官方的 1.5B pedagogical reward model 证明小模型在窄域够用；
   - 验收标准就用 J1 的 test split：**目标是超过 deepseek-v4-pro 的 kappa 0.40**，并在 J3 的 bias battery 上不差于它；
   - 自训裁判的另一个独立收益是**可复现性**：你们已经吃过一次亏（EduGuard 论文裁判 DeepSeek-V3 下线导致官方协议不可复现）。API 裁判会静默升级/下线，开源权重的自有裁判是长期公正性的唯一彻底解法。

### 2.7 建议 J6：裁判输出不确定性与人工路由（P2）

让裁判额外输出 confidence（或用陪审团分歧率代替），低置信样本进人工复核队列。这把"人工标注预算"从随机抽检变成主动学习式采样，同一预算下对裁判的改进快得多。

---

## 三、公正性工程（对外可信度的硬指标）

### 3.1 生产裁判与被测模型必须分离（P0，规则一句话就能定）

当前默认 `JUDGE_MODEL=MiniMax-M3`，而 MiniMax-M3 同时是被测模型之一。建议立一条硬规则写进 README：**任何对外报告的对比里，裁判不得是被测集合的成员；若无法避免，则用两个不同家族裁判各跑一遍并同时报告**。按 2.1 的校准结果，当前生产裁判换成 deepseek-v4-pro（两个校准集上 kappa 都最高）比 M3 更有依据——或直接上 J4 的陪审团。

### 3.2 报告统计量：点估计 → 置信区间（P0）

`summary.json` 目前只有点估计。教育任务样本量小（LIMIT=20 的 smoke、327 条的 `_hard` 任务），两个模型差 3–5 个点很可能不显著。建议：

- `report.py` 统一加 bootstrap 95% CI（对 accuracy/win-rate/kappa 都适用，纯 stdlib 可实现）；
- 模型间对比用**配对**检验（同题配对 bootstrap 或 McNemar），因为所有模型跑的是同一题集，配对检验灵敏得多；
- 报告规则：CI 重叠的对比一律表述为"无显著差异"。这是"公正 benchmark"最容易被同行挑刺、也最容易修的点。

### 3.3 抽样协议固化（P0）

`--limit/--offset` 式抽样在不同时间跑不同模型时可能拿到不同题集。建议对每个 benchmark 固化一份**带版本号的分层抽样清单**（item_id 列表 + 随机种子，签进 git），所有模型永远跑同一清单；全量跑的不受影响。同时在 summary 里记录 `item_list_version`。

### 3.4 污染（contamination）分级标注（P1）

C1 通用题（MMLU-Pro、C-Eval val、GSM8K、AGIEval）污染风险高且众所周知；`priority_benchmark_plan.md` 已经在用"引用榜单、不重跑"策略，方向对。建议再进一步：

- 在能力画像/汇总报告里给每个 benchmark 一个 **contamination risk 等级**（static-public / static-gated / live-refreshing），C-Eval val（答案公开）明确标注"仅 sanity check，分数上限无意义"；
- 廉价的污染探针：选项乱序重测 + 题干同义改写重测，掉分幅度大即可疑（对 gate 类 MCQ 一晚就能跑完）；
- 自建题目（840 题 v1 / pilot）一旦对外发布即视为进入污染窗口，建议保留一个**不发布的 held-out 子集**用于周期性对照。

### 3.5 生成任务的随机性（P2）

开放生成 + judge 的任务（scaffolding/pedagogy/tutor 类）单次采样方差不小。建议至少对 headline 指标做 2–3 seed 重复并报均值±区间；温度、seed 记入 summary。成本敏感的话只对"报告中要对外引用"的跑法做。

---

## 四、覆盖面：离"全面"还差什么

### 4.1 你们自己的压力测试已经指出的 🔴 真缺口（建议排优先级）

`atomic_ability_scenario_coverage_2026-06-29.md` 标出的四个不可还原残余，全世界目前都没有好 benchmark，这正是自建题目的差异化机会：

1. **多模态教学产出**（D5/D6：生成图示/分步图解/示范音频）——EduVisBench 只覆盖一小角；这是自建 benchmark 最值得投入的一个，因为主流模型的多模态生成正在快速商用化，评测需求即将爆发；
2. **群体协作/课堂管理**（C7/C9）——可先从 MCD 类课堂对话语料构造判别式任务起步；
3. **学生作答真实性检测**（E5：AI 代写/抄袭信号）——教育产品刚需，且与 D21 安全正交。

### 4.2 中文教育主测的替代路径（P1）

OmniEduBench 长期无数据，不必再等。2026 上半年出现了几个可评估的中文替代：**EduEval**（11K 题、24 任务、按认知层级组织，arXiv 2512.00290）、**K12Vista**（33K 中文 K12 多模态题）、**K12-KGraph/K12-Bench**（23.6K 题、课标知识图对齐，arXiv 2605.09635，含先修关系推理等非记忆任务，区分度好：Gemini-3-Flash 仅 57%）。建议按 re_benchmark_v1 的筛选标准过一遍这三个，选 1–2 个接入 adapter，填上 C1/C3 中文缺口，并更新 `benchmark-todo.md` 里的 OmniEduBench 条目。

### 4.3 多轮教学是最大的结构性盲区（P1，方法上要立项）

现有 tutor 类 adapter 全部是"给定对话历史 → 生成下一句"。真实教学能力（引导不泄题、随学生状态调整、长程一致性）只能在**多轮**里显形，你们的 benchmark-todo 里安全线已经指出了同样的问题（单轮 ASR 低估风险）。建议立一个 pilot：**LLM 学生模拟器 + 被测 tutor 跑完整 5–10 轮对话 → 裁判对整条轨迹按维度打分**。学生模拟器本身要先做行为校准（犯错率、追问率对齐真实学生分布），可从 MathDial/MRBench 的真实学生话轮里取分布。这个方向和 J5 的自训裁判是互相喂的：轨迹级判例正是裁判训练里最稀缺的数据。

### 4.4 明确宣布"不测什么"（P2，一段话的事）

真实学习效果（learning gain）、教师采纳、KT/CD 协议类任务（EdNet/ASSISTments，需要训传统模型）目前都不在 LLM harness 射程内。建议在 README 里加一节 "Out of scope / 需要产品遥测或专项协议"，把边界说清楚——对外主张"全面"时，明示边界比默不作声更可信。

---

## 五、汇总与呈现（从"一堆 summary.json"到"能力画像"）

### 5.1 自动化能力画像聚合器（P1）

guardrail 说了"先映射到 D01–D24 再画像"，但目前没有自动聚合器（`reports/eval/_aggregate` 尚未承担此职责，`eval_status_*.md` 只跟踪完成度）。建议写 `scripts/build_capability_profile.py`（幂等，风格同现有 build 脚本）：

- 读所有 `reports/eval/*/*/summary.json` → 按 adapter 注册的 D 维映射 → 每模型输出能力画像（雷达/表格 HTML）；
- 每个格子必须带：n、CI（3.2）、裁判及其校准 kappa（若是 judge 任务）、污染等级（3.4）、item_list_version（3.3）；
- **设计上不提供跨 benchmark 平均分**，让 guardrail 变成代码强制而不是文档约定。

### 5.2 裁判可靠性传导到结论置信度（P2）

judge 任务的模型分数上限受裁判 kappa 制约（kappa 0.4 的裁判判出的 5 个点差距基本是噪声）。画像里对 judge 类格子建议加一档"结论置信度"标记（rule-scored > 高kappa judge > 低kappa judge），读者一眼能看出哪些结论敢用。

---

## 六、工程与仓库卫生（小项）

- `eval/*.log` 若已被 git 跟踪建议移入 gitignore（日志与 `reports/eval` 的 JSONL 重复且体积会涨）。
- token/成本核算目前只有 mmtutorbench 记录 usage，建议 runner 层统一记录每次运行的 token 用量进 summary——做"哪些 benchmark 值得花钱重测"的决策（priority plan 的核心问题 3）需要真实成本数。
- judge 输出全文（rationale）建议全部落盘保留（部分 adapter 已做），这是 J5 训练数据和事后审计的原料，删了就没了。
- `doc/eval_status_*.md` 手工维护成本在涨，5.1 的聚合器可以顺手把这张表自动生成。

---

## 七、建议的执行顺序（一页版）

| 优先级 | 事项 | 章节 | 为什么先做 |
|---|---|---|---|
| P0 | 裁判/被测分离规则 + 生产裁判换 deepseek-v4-pro 或陪审团 | 3.1 | 一句话规则，堵住对外报告最大的硬伤 |
| P0 | summary 加 bootstrap CI + 配对检验 | 3.2 | 所有后续结论的地基，stdlib 可实现 |
| P0 | 元评测集正式化（统一 schema + dev/test split） | 2.2 | 裁判研究和自训的前提，数据都已在库 |
| P0 | judge prompt registry + 版本入 summary | 2.3 | 不做则 rubric 实验无法归因 |
| P1 | rubric 消融（人类锚点少样本、判前先做） | 2.3 | 提升 kappa 最便宜的路径 |
| P1 | 异质陪审团 vs 单裁判对比 + 分歧落盘 | 2.5/2.4 | 基建现成，稀释自偏好，攒训练数据 |
| P1 | 中文教学判例标注冲刺（300–500 条，双标注报 IAA） | 2.6 | 中文裁判的数据缺口只能自己填 |
| P1 | 中文 K12 新 benchmark 评估接入（EduEval/K12-Bench/K12Vista 选 1–2） | 4.2 | 替代长期缺位的 OmniEduBench |
| P1 | 能力画像聚合器 | 5.1 | 把 guardrail 变成代码 |
| P1 | 多轮教学 pilot（学生模拟器 + 轨迹级裁判） | 4.3 | 最大结构性盲区，且反哺裁判训练数据 |
| P2 | bias battery / 污染探针 / 自训裁判 SFT / 不确定性路由 | 2.4/3.4/2.6/2.7 | 依赖上面的数据与基建就绪 |

---

## 附：本次调研主要来源

- BEA 2025 shared task findings（裁判任务人类上限参照，best macro-F1 0.58–0.72）：[arXiv 2507.10579](https://arxiv.org/abs/2507.10579)、[SIGEDU task page](https://sig-edu.org/sharedtask/2025)
- LLM-as-judge 综述与方法：[Awesome-LLM-as-a-judge](https://github.com/llm-as-a-judge/Awesome-LLM-as-a-judge)、[From Holistic Evaluation to Structured Criteria (arXiv 2606.08625)](https://arxiv.org/pdf/2606.08625)、[Do Before You Judge (arXiv 2509.19880)](https://arxiv.org/pdf/2509.19880)、[Think-J (arXiv 2505.14268)](https://arxiv.org/pdf/2505.14268)、[S2J (arXiv 2509.22099)](https://arxiv.org/pdf/2509.22099)、[Meta-Judging survey (arXiv 2601.17312)](https://arxiv.org/pdf/2601.17312)、[RubricBench (arXiv 2603.01562)](https://arxiv.org/pdf/2603.01562)
- 教育域裁判/奖励模型训练：[PEARL: Training Socratic Tutors with Pedagogically Aligned RL (arXiv 2605.29582)](https://arxiv.org/pdf/2605.29582)、[Towards Pedagogically Aligned LLM Tutors for Math Mistake Remediation (arXiv 2606.21502)](https://arxiv.org/pdf/2606.21502)
- 污染检测与评测统计：[Benchmark Data Contamination survey (arXiv 2406.04244)](https://arxiv.org/html/2406.04244v1)、[Quantifying the Effect of Test Set Contamination on Generative Evaluations (arXiv 2601.04301)](https://arxiv.org/pdf/2601.04301)、[Contamination-Resistant Benchmarks (arXiv 2605.19999)](https://arxiv.org/pdf/2605.19999)
- 中文 K-12 新 benchmark：[K12-KGraph / K12-Bench (arXiv 2605.09635)](https://arxiv.org/html/2605.09635)、[EduEval (arXiv 2512.00290)](https://arxiv.org/html/2512.00290)、[K12Vista (arXiv 2506.01676)](https://arxiv.org/html/2506.01676v1)、[E-EVAL (arXiv 2401.15927)](https://arxiv.org/abs/2401.15927)
