# Benchmark 人类参照锚与可用门槛

> 由 `scripts/build_human_baseline_report.py` 生成，不要手改。
> 数据源：`data/benchmark_human_baselines_v1.json`、`reports/eval/`。
> 改结论要改 `scripts/build_human_baselines.py` 后重跑两个脚本。
> 地板那三层（随机 / 平凡策略 / 退化回复）在 `doc/benchmark_baselines_2026-08-04.md`，与本文互补。

## 这份文档回答两个问题，它们不是一个数

| | 问的是 | 怎么用 |
|---|---|---|
| **人类参照锚** | 人在这套题上能拿多少分 | 判断模型分是高是低的参照系 |
| **可用门槛** | 多少分算能上线 | 判断能不能交付的判定线 |

两者经常不重合，而且**大多数 benchmark 只有其中一边**——这是事实不是遗漏。
人类分低于门槛（人自己也不达标）和模型超过人类但没到门槛，都是真实存在的情形，
表里分两列各自留空，不互相填补。

分级沿用 `benchmark_human_baselines_v1.json` 的 A/B/C/D：A 同题同指标直接可比，
B 同 benchmark 但 split 或评分协议有差异，C 制度性代理或构造性上限，
D 只作语境（专用系统分、judge 可靠性）——D 永远不进人类分列。

## 表 A：人类参照锚

`人类` 与 `实跑区间` 都在 `指标` 那一列的字段的原始标度上；**同一行内可比，跨行不可比**。
`指标` 留空表示就是 headline，填了说明人类数只存在于另一个字段上（这时实跑区间也换算到那个字段）。

⚠ 带警告的行是**已知不可比**的对比，一句话读法位置直接放了阻断说明——
这些行的「模型 vs 人类」不要引用。

| benchmark | headline | 人类 | 级别 | 指标 | 实跑区间 | 一句话读法 |
|---|---|---|---|---|---|---|
| `agieval` | `accuracy` | 0.67 | B | — | 0.8112 – 0.9204 (7 模型) | ⚠ 总分口径不可比，看「逐任务对齐」那一节的加权值，不要看这一行。 |
| `bea2025_tutor` | `extra:pass_rate` | 0.5233 | B | — | 0.7133 – 0.9189 (9 模型) | ⚠ 同 mrbench_tutor：prompt 泄了评分维度，「模型超过人类专家」的读法不成立。 |
| `mathvista` | `accuracy` | 0.603 | A | — | 0.834 – 0.887 (3 模型) | 最好模型 0.887 已超过人类 |
| `mmtutorbench` | `extra:average_total_score_0_to_6` | 5.85 | B | — | 3.4447 – 4.7675 (5 模型) | ⚠ 跨 judge 不可比：人类 5.85 由论文的 GPT-o4-mini 打，我们的分由 MiniMax-M3 打，而且人类只评了 66 题子集。这条差距不能读成能力差。 |
| `mrbench_tutor` | `extra:pass_rate` | 0.605 | B | — | 0.68 – 0.9293 (8 模型) | ⚠ 不要读成「模型超过人类专家」：我们给被测模型的 prompt 逐条列出了 judge 的评分维度，人类教师没有这份清单。修掉泄题之前这一行的对比无效。 |
| `p08_abstention` | `extra:score_10` | 0.9316 | B | `extra:abstention_f1` | 0.8442 – 0.9306 (6 模型) | ⚠ 我们的 prompt 不提示存在不可答题，论文提示了，我们这边更难；差距是上界，不要读成「模型比人差这么多」。 |
| `asap_2` | `extra:overall.qwk` | — | — | — | 0.4091 – 0.6106 (12 模型) | 无人类数据（理由见「查过但确实没有」） |
| `bea2025_judge` | `extra:recommended_judge_score` | — | — | — | 0.3687 – 0.5488 (7 模型) | 无人类数据（理由见「查过但确实没有」） |
| `ceval` | `accuracy` | — | — | — | 0.8276 – 0.9547 (8 模型) | 无人类数据（理由见「查过但确实没有」） |
| `edubench` | `extra:overall.mean_overall_score` | — | — | — | 7.2624 – 8.719 (18 模型) | 无人类数据（理由见「查过但确实没有」） |
| `eduguard_adversarial` | `extra:overall.asr` | — | — | — | 0.0038 – 0.6241 (22 模型) ↓越低越好 | 无人类数据（理由见「查过但确实没有」） |
| `eduguard_sata` | `extra:overall.rfs` | — | — | — | 0.6934 – 0.7694 (8 模型) | 无人类数据（理由见「查过但确实没有」） |
| `ifeval` | `extra:prompt_strict_accuracy` | — | C | — | 0.8741 – 0.9298 (6 模型) | 无人类数据（理由见「查过但确实没有」） |
| `k12bench` | `accuracy` | — | — | — | 0.5001 – 0.5718 (3 模型) | 无人类数据（理由见「查过但确实没有」） |
| `k12vista` | `extra:official_score` | — | — | — | 0.5405 – 0.7398 (3 模型) | 无人类数据（理由见「查过但确实没有」） |
| `mmlu_pro` | `accuracy` | — | — | — | 0.791 – 0.8827 (7 模型) | 无人类数据（理由见「查过但确实没有」） |
| `mrbench_judge` | `extra:macro_over_dimensions.f1_macro` | — | — | — | 0.4109 – 0.5615 (8 模型) | 无人类数据（理由见「查过但确实没有」） |
| `olympiadbench` | `accuracy` | — | — | — | 0.716 – 0.7662 (4 模型) | 无人类数据（理由见「查过但确实没有」） |
| `pedagogy_benchmark` | `accuracy` | — | — | — | 0.6935 – 0.8901 (12 模型) | 无人类数据（理由见「查过但确实没有」） |
| `sas_bench` | `extra:overall.qwk` | — | — | — | 79.0429 – 86.7666 (9 模型) | 无人类数据（理由见「查过但确实没有」） |
| `tutorbench` | `extra:arr_w_x100` | — | — | — | 56.18 – 67.5 (4 模型) | 无人类数据（理由见「查过但确实没有」） |

## 表 B：可用门槛

`门槛` 落在 `指标` 那一列的字段上，**不一定是 headline**——判分类任务的可用性由一致性决定，
不由 macro-F1 决定，所以门槛压在 kappa 上。`达标` 数的是通过门槛的模型数 / 可比 run 总数。

| benchmark | 类型 | 指标 | 门槛 | 人类上限 | 实跑区间 | 达标 |
|---|---|---|---|---|---|---|
| `asap_2` | 行业标准 | `extra:overall.qwk` | 0.7 | — | 0.4091 – 0.6106 (12 模型) | **0/12** |
| `bea2025_judge` | 标注者一致性 | `extra:macro_over_dimensions.cohen_kappa` | 0.61 | 0.65 | 0.1448 – 0.4356 (7 模型) | **0/7** |
| `ceval` | 制度性代理 | `accuracy` | 0.6 | — | 0.8276 – 0.9547 (8 模型) | **8/8** |
| `mathtutorbench_judge_calibration` | 行业标准 | `accuracy` | 0.84 | — | 0.8102 – 0.8444 (7 模型) | **1/7** |
| `mathtutorbench_pedagogy` | 指标构造 | `extra:win_rate` | 0.5 | — | 0.7396 – 0.9052 (13 模型) | **13/13** |
| `mathtutorbench_pedagogy_hard` | 指标构造 | `extra:win_rate` | 0.5 | — | 0.6284 – 0.8853 (13 模型) | **13/13** |
| `mathtutorbench_scaffolding` | 指标构造 | `extra:win_rate` | 0.5 | — | 0.1426 – 0.6191 (13 模型) | **4/13** |
| `mathtutorbench_scaffolding_hard` | 指标构造 | `extra:win_rate` | 0.5 | — | 0.1239 – 0.5933 (13 模型) | **2/13** |
| `mrbench_judge` | 标注者一致性 | `extra:macro_over_dimensions.cohen_kappa` | 0.61 | 0.71 | 0.2653 – 0.412 (8 模型) | **0/8** |
| `p08_abstention` | 行业标准 | `extra:abstention_f1` | 0.9316 | — | 0.8442 – 0.9306 (6 模型) | **0/6** |
| `sas_bench` | 行业标准 | `extra:overall.qwk` | 70 | — | 79.0429 – 86.7666 (9 模型) | **9/9** |
| `edubench` | 无门槛 | `extra:overall.mean_overall_score` | — | — | 7.2624 – 8.719 (18 模型) | — |
| `eduguard_adversarial` | 无门槛 | `extra:overall.asr` | — | — | 0.0038 – 0.6241 (22 模型) ↓越低越好 | — |
| `ifeval` | 无门槛 | `extra:prompt_strict_accuracy` | — | — | 0.8741 – 0.9298 (6 模型) | — |
| `tutorbench` | 无门槛 | `extra:arr_w_x100` | — | — | 56.18 – 67.5 (4 模型) | — |

### 没过门槛的

**`asap_2`**（门槛 0.7 on `extra:overall.qwk`）—— 12/12 未达标：
- claude-sonnet-4-6: 0.6106
- qwen3.7-max: 0.6003
- doubao-seed-2.0-pro: 0.585
- glm-5.1: 0.5725
- kimi-k2.6: 0.5706
- MiniMax-M2.7: 0.5277
- deepseek-v4-pro: 0.5232
- deepseek-v4-flash: 0.5078
- MiniMax-M3: 0.49
- DeepSeek-R1-0528-Qwen3-8B: 0.4779
- gpt-5.4: 0.4726
- Qwen/Qwen3.5-4B: 0.4091

**`bea2025_judge`**（门槛 0.61 on `extra:macro_over_dimensions.cohen_kappa`）—— 7/7 未达标：
- glm-5.2: 0.4356
- doubao-seed-2.0-pro: 0.4081
- deepseek-v4-pro: 0.4037
- deepseek-v4-flash: 0.37
- MiniMax-M3: 0.3369
- MiniMax-M2.7: 0.3095
- deepseek-v3.2: 0.1448

**`mrbench_judge`**（门槛 0.61 on `extra:macro_over_dimensions.cohen_kappa`）—— 8/8 未达标：
- glm-5.2: 0.412
- doubao-seed-2.0-pro: 0.4058
- deepseek-v4-pro: 0.4003
- deepseek-v4-flash: 0.3831
- MiniMax-M2.7: 0.3712
- Qwen/Qwen3.5-4B: 0.3579
- MiniMax-M3: 0.3408
- deepseek-v3.2: 0.2653

**`p08_abstention`**（门槛 0.9316 on `extra:abstention_f1`）—— 6/6 未达标：
- Qwen/Qwen3.5-4B: 0.9306
- glm-5.2: 0.9072
- deepseek-v4-pro: 0.9027
- doubao-seed-2.0-pro: 0.8908
- MiniMax-M3: 0.8539
- MiniMax-M2.7: 0.8442

**`mathtutorbench_judge_calibration`**（门槛 0.84 on `accuracy`）—— 6/7 未达标：
- glm-5.2: 0.8392
- deepseek-v3.2: 0.8361
- doubao-seed-2.0-pro: 0.8268
- deepseek-v4-flash: 0.8257
- deepseek-v4-pro: 0.8174
- MiniMax-M2.7: 0.8102

**`mathtutorbench_scaffolding_hard`**（门槛 0.5 on `extra:win_rate`）—— 11/13 未达标：
- deepseek-v4-pro: 0.4419
- deepseek-v4-pro: 0.4128
- doubao-seed-2.0-pro: 0.37
- doubao-seed-2.0-pro: 0.3425
- MiniMax-M3: 0.2416
- MiniMax-M3: 0.2248
- Qwen/Qwen3.5-4B: 0.2187
- doubao-seed-2.0-lite: 0.204
- deepseek-v4-flash: 0.1667
- MiniMax-M2.7: 0.13
- MiniMax-M2.7: 0.1239

**`mathtutorbench_scaffolding`**（门槛 0.5 on `extra:win_rate`）—— 9/13 未达标：
- doubao-seed-2.0-pro: 0.3535
- doubao-seed-2.0-pro: 0.3496
- MiniMax-M3: 0.2783
- MiniMax-M3: 0.2713
- doubao-seed-2.0-lite: 0.2537
- Qwen/Qwen3.5-4B: 0.2422
- deepseek-v4-flash: 0.15
- MiniMax-M2.7: 0.1478
- MiniMax-M2.7: 0.1426

## 逐任务对齐：把论文的人类分按我们的题数重算

论文的人类总分覆盖的任务组合和我们跑的不一样，直接并列会误读。
下面按**我们自己的题数**给每个任务的人类分加权，论文没有人类分的任务从两边同时剔除，绝不补零。

### `agieval`

人类来源：AGIEval, arXiv:2304.06364, Table 2/3；受试人群：真实考生分数分布折算：avg = 50 百分位，top = 前 1%

- 剔除 `math`：MATH 子集不是真人考试，论文无人类分；加权时必须排除（约 1,000 题）。
- ⚠ 同一场考试的三个 LSAT 子任务共用一个人类分（56/91），SAT 三个子任务共用 66/94——这是考试级折算，不是子任务级实测。
- ⚠ sat-en-without-passage 是「不给原文」的消融设定，人类那 0.66 是给原文考出来的，这一格模型吃亏，差值不要当能力差读。

| 模型 | 对齐题数 | 人类均分(加权) | 人类前1%(加权) | 模型同题 | 差值 |
|---|---|---|---|---|---|
| doubao-seed-2.0-pro | 6272 | 0.6996 | 0.9067 | 0.9193 ✅ | +0.2197 |
| glm-5.2 | 6230 | 0.6992 | 0.9066 | 0.9032 | +0.2040 |
| deepseek-v4-pro | 6272 | 0.6996 | 0.9067 | 0.8983 | +0.1987 |
| deepseek-v4-flash | 6271 | 0.6996 | 0.9067 | 0.8889 | +0.1893 |
| MiniMax-M3 | 6268 | 0.6995 | 0.9067 | 0.8464 | +0.1468 |
| Qwen/Qwen3.5-4B | 6272 | 0.6996 | 0.9067 | 0.8166 | +0.1171 |
| MiniMax-M2.7 | 6267 | 0.6995 | 0.9067 | 0.7972 | +0.0977 |

✅ = 加权后已超过前 1% 考生线。

> 交叉校验：按我们题数重算得 0.6996，论文自报总人类分 0.67，差 +0.0296。
> 差值来自题数分布与论文四舍五入，量级正常即说明逐任务表与总分是同一回事。

**仍有模型低于普通人类的任务**（6/20）：

| 任务 | 题数 | 人类均分 | 低于人类的模型 |
|---|---|---|---|
| `gaokao-mathcloze` | 118 | 0.73 | MiniMax-M2.7 0.305, Qwen/Qwen3.5-4B 0.314, deepseek-v4-flash 0.322, deepseek-v4-pro 0.322, doubao-seed-2.0-pro 0.322, glm-5.2 0.322, MiniMax-M3 0.322 |
| `logiqa-en` | 650 | 0.86 | MiniMax-M2.7 0.743, Qwen/Qwen3.5-4B 0.777, MiniMax-M3 0.823, deepseek-v4-flash 0.825, deepseek-v4-pro 0.856 |
| `logiqa-zh` | 650 | 0.88 | MiniMax-M2.7 0.826, Qwen/Qwen3.5-4B 0.84, MiniMax-M3 0.871, deepseek-v4-flash 0.873 |
| `sat-en-without-passage` | 206 | 0.66 | deepseek-v4-pro 0.485, Qwen/Qwen3.5-4B 0.553, MiniMax-M2.7 0.568, MiniMax-M3 0.587 |
| `jec-qa-kd` | 477 | 0.71 | MiniMax-M2.7 0.589, Qwen/Qwen3.5-4B 0.643, MiniMax-M3 0.677 |
| `jec-qa-ca` | 533 | 0.58 | MiniMax-M2.7 0.542, Qwen/Qwen3.5-4B 0.548 |

### `mathvista`

人类来源：MathVista (ICLR 2024), arXiv:2310.02255, Table 2；受试人群：AMT 标注员，高中及以上学历，20 分钟做 5 题

- ⚠ 限时协议：几何题人类只有 48.4%，是没时间算，不是算不出。模型在这一格 98% 不代表几何能力超人。

| 模型 | 对齐题数 | 人类均分(加权) | 人类前1%(加权) | 模型同题 | 差值 |
|---|---|---|---|---|---|
| doubao-seed-2.0-pro | 1000 | 0.597 | — | 0.887 | +0.2900 |
| MiniMax-M3 | 993 | 0.5971 | — | 0.8409 | +0.2438 |
| Qwen/Qwen3.5-4B | 1000 | 0.597 | — | 0.834 | +0.2370 |

论文没给这个 benchmark 的前 1% 档，该列留空——不拿均分冒充上限。

> 交叉校验：按我们题数重算得 0.597，论文自报总人类分 0.603，差 -0.0060。
> 差值来自题数分布与论文四舍五入，量级正常即说明逐任务表与总分是同一回事。

> 还没接上的细粒度：论文还给了 7 类数学技能的人类分，但我们的 mathvista adapter 没建 skill bucket，现在 join 不上。要用得给 adapter 加一个 skills bucket 再 --score-only 重跑打分（不花 API 额度）。
>
> ALG 代数 0.509；ARI 算术 0.592；GEO 几何 0.514；LOG 逻辑 0.407；NUM 数值常识 0.538；SCI 科学 0.649；STA 统计 0.639

## 同管线复评：人类专家的回复过我们自己的 judge

这是全套里最干净的一类人类锚——同题、同指标、同 judge，唯一的变量就是回复出自人还是模型。
目前只有两个 benchmark 的数据集自带人类教师回复，都已经跑过。

| benchmark | 题数 | judge | 人类标注者判专家 | 我们的 judge 判同一批专家 | 差 |
|---|---|---|---|---|---|
| `bea2025_tutor` | 300 | MiniMax-M3 | 0.5233 | 0.1601 | -0.3632 |
| `mrbench_tutor` | 200 | MiniMax-M3 | 0.605 | 0.1637 | -0.4413 |

⚠ **这两个数现在还不能当人类基线用。** 同一批专家教师回复，人类标注者判下来通过率
0.52–0.61，我们的 judge 判下来只有 0.16，而模型拿到 `bea2025_tutor` 0.7133–0.9189、`mrbench_tutor` 0.68–0.9293。
原因是 harness 缺陷：我们给被测模型的 prompt 把 judge 要打的维度逐条列出来了，
模型照着清单写，人类教师没有这份清单（详见 `doc/benchmark_baselines_2026-08-04.md` 末节）。
**修掉泄题之前，任何「模型超过人类专家」的结论都不成立。**

数据集自带标注（人类标注者口径，不经我们的 judge）：

| benchmark | 角色 | n | pass_rate |
|---|---|---|---|
| `bea2025_tutor` | Expert | 300 | 0.5233 |
| `bea2025_tutor` | Novice | 76 | 0.0132 |
| `mrbench_tutor` | Expert | 200 | 0.605 |
| `mrbench_tutor` | Novice | 55 | 0 |

## 查过但确实没有

这一节存在的意义是**别再查第二遍**。每条都写清查了哪篇、结论是什么。

**`asap_2`** — ASAP 2.0 corpus paper (Crossley et al., Assessing Writing, 2025)

已核：语料由两组评分员打分，但 (1) 公开发布的 CSV 只保留合议后的单一 score 列，本地算不出人类互评 QWK；(2) 语料论文在 ScienceDirect 付费墙后（HTTP 403），拿不到数字。在拿到论文前如实留空。

- 语境锚（grade D，不是人类分）·AES 领域的人类互评 QWK 常规区间（grade D）：— — 跨数据集约 0.61-0.97；领域内把机器-人类 QWK ≥ 0.70 视为可接受门槛。我们实跑 0.473-0.611，整体低于该门槛——这是有意义的定性结论，但 0.61-0.97 这个区间不是 ASAP 2.0 的数，不能当人类基线用。

**`bea2025_judge`** — Findings of the BEA 2025 Shared Task, arXiv:2507.10579

共享任务的金标即人类标注本身，论文未单独报「人类复现金标」的 macro-F1。

- 语境锚（grade D，不是人类分）·标注者间 Fleiss kappa（人类判分的一致性上限）：0.65 — dev 集 200 段对话由 4 名标注者标，平均 Fleiss kappa 0.65（substantial）；另有 83 条回复由 6 名组织者复标，Fleiss kappa 0.64。这是本 benchmark 上唯一的人类侧硬数字，对应我们的 extra_metrics.macro_over_dimensions.cohen_kappa。
- 语境锚（grade D，不是人类分）·最佳参赛系统 macro-F1（专用系统锚，grade D，非人类）：— — 四个赛道 exact macro-F1 最好成绩：Mistake Identification 0.7181(BJTU)、Actionability 0.7085(bea-jh)、Mistake Location 0.5983(BLCU-ICALL)、Providing Guidance 0.5834(MSA)；lenient 口径为 0.9185 / 0.8659 / 0.8404 / 0.7860。50+ 支队伍参赛。我们最好的 recommended_judge_score 是 0.549（glm-5.2），在专用微调系统的区间下沿。
- 语境锚（grade D，不是人类分）·人类教师回复在 tutor identification 赛道的可辨识度：— — 专家教师 79.1%、新手教师 66.5%——这是「认得出是人写的」，不是教学质量分。

**`ceval`** — C-Eval (NeurIPS 2023 D&B), arXiv:2305.08322

已核：论文未报人类表现，只报模型分（当时仅 GPT-4 超过 60%）。


**`edubench`** — EduBench (arXiv:2505.16160), github.com/ybai-nlp/EduBench

无人类作答分：评分完全靠 LLM judge 打 12 维 1-10 分，论文与仓库都没有让人类写回答再评的实验。量表下限是 1，地板靠退化回复实测。

- 语境锚（grade D，不是人类分）·judge 相对人类标注的系统性通胀（grade D，但读分时必须挂上）：— — 论文的人类评测只有 198 条样本（中英各 99）、且只有 1 名标注者（作者自己说 due to cost constraints ... may limit the reliability）。与 judge 的 Kendall's W：DeepSeek-V3 / R1 / QwQ-Plus 均为 0.63，GPT-4o 只有 0.56。论文明确指出模型 judge 在指标级与场景级都比人类高约 1 分。我们实跑区间 7.47-8.48，按这个修正，人类观感大致在 6.5-7.5。

**`eduguard_adversarial`** — EduGuardBench, arXiv:2511.06890

越狱抵抗力没有「人类基线」这个概念；地板在另一头——全部拒答即 ASR 0。

- 语境锚（grade D，不是人类分）·judge 与人类标注的校准（grade D）：— — 论文选 DeepSeek-V3 当 judge，与人类一致性 Cohen's kappa 0.882（有害性二分类）与 0.874（拒答质量三分类）。我们默认 judge 是 MiniMax-M3，未做同等校准。

**`eduguard_sata`** — EduGuardBench, arXiv:2511.06890

已核：SATA 金标由外部专家团设计，论文未让人类作答，无人类 RFS。


**`ifeval`** — IFEval, Google Research

构造性上限：指令都是可程序化验证的（字数、格式、禁用词等），认真执行的人类接近 1.0。这是设计推论而非实测，标为 grade C，不要当实测人类分用。

- 语境锚（grade D，不是人类分）·内容无关的通用文本地板：— — 见 benchmark_baselines_v1.json：generic_text 策略 prompt-strict 约 0.056。

**`k12bench`** — K12-KGraph, arXiv:2605.09635

已核：题目由课程知识图谱自动派生，论文未做人类作答实验。

- 语境锚（grade D，不是人类分）·论文报告的模型区间：— — Gemini-3-Flash 57% exact match，最强开源 Gemma-4-31B-IT 46%。我们实跑 minimax3 0.500，落在这个区间内，可作为接入正确性的旁证。

**`k12vista`** — K12Vista, arXiv:2506.01676

已核：论文重点在 K12-PEM 过程评估模型与人工标注的 K12-PEBench，未给人类答题基线。


**`mmlu_pro`** — MMLU-Pro (NeurIPS 2024 D&B)

已核：论文未报人类表现。常被引用的 89.8% 是原版 MMLU 论文对众包标注员的估计值，既是另一个 benchmark（4 选 1，题目也不同），本身也不可靠，不外推。


**`mrbench_judge`** — Unifying AI Tutor Evaluation / MRBench, arXiv:2412.09416

论文未给「人类当 judge 复现金标」的 macro-F1，只给一致性统计量。

- 语境锚（grade D，不是人类分）·标注者间 Cohen's kappa（人类判分的一致性上限，对应 macro_over_dimensions.cohen_kappa）：0.71 — 论文报总体 kappa 0.71（substantial），试点阶段 Fleiss kappa 0.65。我们最好的模型 kappa 约 0.41（glm-5.2），离人类互评一致性还有明显距离——这是这个 benchmark 上最有意义的人类锚。

**`olympiadbench`** — OlympiadBench (ACL 2024), arXiv:2402.14008

已核：论文全文未给人类表现分。摘要里的 expert-level annotations 指的是标注过程，不是人类作答基线。网上流传的「人类专家 >90%」没有论文出处，不采用。

- 语境锚（grade D，不是人类分）·论文最强模型 GPT-4V：0.1797 — 对照我们实跑的 0.716-0.766：两年模型进步 + 我们只跑 OE 子集（跳过 TP 证明题），协议差异巨大，不要拿论文数当难度参照。

**`pedagogy_benchmark`** — Benchmarking the Pedagogical Knowledge of LLMs, arXiv:2506.18710

论文原话：Question-level human results are not available for these exams。他们那个 ~50% 是把每道题赋以其来源试卷的平均正确率再取平均得到的，所以题级估计其实存在——但这个字段没随数据发布，本地 questions.jsonl 只有 year / category / education_level。2026-08-15 决定：不去找作者要，按没有处理。

- 语境锚（grade D，不是人类分）·智利教师专业发展考试人群均分（制度性代理，grade C）：0.5 — 2017-2021 共 25,000+ 名受训教师的平均预期得分，非本题集实测。论文自己也提醒 this is only an estimate, and any interpretation should be made with caution。

**`sas_bench`** — SAS-Bench, arXiv:2505.07247

已核：论文未报标注者间一致性，也没有人类-人类 QWK。18 位学科专家分两组标注 + 分歧讨论重标，但无量化一致性统计。

- 语境锚（grade D，不是人类分）·论文最强模型：— — Deepseek-V3 平均 CCS 74.11%，Deepseek-R1 平均 ECS 55.90%。

**`tutorbench`** — TutorBench (Scale AI), arXiv:2510.02663

论文未报人类专家在 ARR_w 上的得分。本来还有一条路：论文说每条样本都配了专家写的 golden tutoring response，把它过我们自己的 judge 就能得到同管线人类分——但公开发布的 sources/datasets/tutorbench/tutorbench.jsonl 只有 rubrics，没有那条参考回复（字段只有 prompt / initial_explanation / follow_up_prompt / rubrics / image 等）。这条路在本地走不通。

- 语境锚（grade D，不是人类分）·judge 可靠性（grade D）：— — LLM judge 与人类一致率 0.78，人类互评一致率 0.75；judge 对多数投票的 F1 0.82，最强单个人类专家 0.91。另：论文最强模型 Gemini 2.5 Pro ARR_w 55.65%，无前沿模型超过 56%。注意我们的 judge 是 MiniMax-M3、论文用 Claude Sonnet 4 且只评 Fair815 子集，不可直接对标。

### 自建题集 / 无外部人类参照

- **`eduillustrate`** — 仓库自建题集 + 自建 judge rubric，无外部人类参照。
- **`longtutor_diagnosis`** — 仓库自建，无外部人类参照。
- **`longtutor_evidence`** — 仓库自建，无外部人类参照。
- **`longtutor_teaching`** — 仓库自建，无外部人类参照；且其 accuracy 实为解析成功率（实跑 0.999-1.000），无区分度。
- **`mathtutorbench_judge_calibration`** — 官方 A/B 偏好对（teacher_response_positive = 专家改写，negative = 新手原话），金标即人类偏好，无「人类得分」概念。可比的是专用系统锚：论文自己微调的 Qwen2.5-1.5B 奖励模型区分专家/新手的准确率是 0.84，我们实跑 0.810-0.844，已经同水平。
- **`mathtutorbench_mistake_correction`** — 同上。
- **`mathtutorbench_mistake_location`** — 标注金标即人类判断，论文未报人类复现分。
- **`mathtutorbench_pedagogy`** — 与金标教师回应成对比较，win_rate 0.5 即「与专家教师打平」——该基准的专家锚天然是 0.5。还差一个下锚：data/pref_test.jsonl 每条都带 teacher_response_negative（新手教师原话），拿它当被测回复跑一遍就能得到「新手教师 win_rate」，让跌破 0.5 的模型有「相当于新手 / 不如新手」的落点。未跑。
- **`mathtutorbench_pedagogy_hard`** — 同上，专家锚 = win_rate 0.5，新手锚未跑。
- **`mathtutorbench_problem_solving`** — GSM8K 派生，官方无人类基线（GSM8K 原论文的人类基线针对完整数据集，非此子集）。
- **`mathtutorbench_scaffolding`** — 同上，专家锚 = win_rate 0.5，新手锚未跑（这个任务 7 个模型有 5 个跌破 0.5，最需要下锚）。
- **`mathtutorbench_scaffolding_hard`** — 同上，专家锚 = win_rate 0.5，新手锚未跑（6/7 跌破）。
- **`mathtutorbench_socratic`** — BLEU 对参考问句，人类改述同样拿不到高 BLEU，该指标无人类上限意义。
- **`mathtutorbench_solution_correctness`** — 同上。
- **`mmtutorbench_judge_calibration`** — 公开 JSONL 无 per-item 人类金标，adapter 本身不产出题目。
- **`mooccube_prereq`** — 仓库自建（基于 MOOCCube 图谱派生），无外部人类参照；已内建 chance correction。
- **`p07_selfcheck`** — 仓库自建复合指标，无人类对照概念；平凡策略地板 5.0/10。
- **`p08_calibration`** — 仓库自建复合指标，无人类对照概念；平凡策略地板 5.0/10。

## 还能补的（按成本从低到高）

1. **mathtutorbench 新手教师锚**（零 API 额外数据，只花一次判分）——
   `pref_test.jsonl` 每条都带 `teacher_response_negative`，即新手教师原话。
   拿它当被测回复跑一遍，就能给 scaffolding / pedagogy 的 win_rate 补一个人类下锚。
   现在这四个任务只有 0.5 这个「与专家打平」的上锚，多数模型跌破它，
   但「跌破多少算差」没有参照——补上新手线就能说清是相当于新手还是不如新手。
2. **mathvista 技能维度 bucket**（不花 API）—— 给 adapter 加一个 skills bucket 后 `--score-only`
   重跑打分，就能接上论文的 7 类技能人类分（ALG 50.9 / LOG 40.7 等）。
3. **修 mrbench / bea2025 的 prompt 泄题**——这是解锁「同管线人类锚」这条路的前提，
   不修的话已经跑出来的 expert / novice 复评值都用不了。
4. **自建人类小样本**（要花钱，兜底方案，未启动）—— 只在精选题集上做。
   这是唯一能补 `ceval` / `mmlu_pro` / `olympiadbench` / `sas_bench` 这几格的办法，
   其余路线对它们全部无效。

