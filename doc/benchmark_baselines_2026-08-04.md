# Benchmark 基准锚点：随机基线 / 平凡策略 / 人类表现

> 由 `scripts/build_baseline_report.py` 生成，不要手改。
> 数据源：`data/benchmark_baselines_v1.json`、`data/benchmark_human_baselines_v1.json`、
> `reports/eval/_baseline/`。改结论要改上游脚本后重跑。

## 为什么不是一个数

最初的问题是「纯随机瞎猜能得多少分」。真去逐个 benchmark 推导之后，结论是：
**对一半以上的 benchmark，均匀随机根本不是地板。** 所以分三层：

| 层 | 含义 | 什么时候它才是真地板 |
|---|---|---|
| **L1 均匀随机** | 在题目自身答案空间上均匀抽样 | 选项数固定、类别均衡的选择题 |
| **L2 平凡策略** | 与题目内容无关的最优常数策略（按先验猜 / 全选多数类 / 从不改答案 / 全部弃答） | 类别不平衡的分类题、复合指标、量表打分 |
| **L3 退化回答** | 一段与题无关的回复交给真实 judge 打分 | judge 打分的生成类任务（均匀随机无定义） |

方法上没有手推公式，而是**用真实的 `adapter.score()` 和 `extra_summary()` 跑合成答案**，
这样 RFS 的部分分、macro-F1、QWK 都走的是和正式评测同一条代码路径。
闭式解只留作交叉验证。

**方法论验证**：用「MC 逐题 1/k + free-form 记 0」模拟 MathVista，得 0.1792，而官方论文公布的 Random chance 是 **0.179**——对得上。

## 主表

`L1` = 均匀随机；`L2` = 最强的平凡策略（括号内是策略名）；`L3` = 退化回复经真实 judge；
`人类` = 文献或数据集自带的人类参照（分级见下）；`实跑` = 已完成 run 的区间。
**同一行内所有数字都是该 benchmark headline 的原始标度**，跨行不可比。

空格的含义要分清（见文末「为什么有些 benchmark 没有随机分」）：

- **`n/a`** = 该层在这个 benchmark 上**没有定义**，不是没算。
- **`待跑`** = 需要 API 的 L3 还没跑到这一行。
- **`—`** = 该层不适用（例如 judge 类任务本来就没有 L1/L2）。

| benchmark | headline | 题数 | L1 随机 | L2 平凡策略 | L3 退化 | 人类 | 实跑区间 |
|---|---|---|---|---|---|---|---|
| `agieval` | `accuracy` | 7272 | 0.1737 | 0.2057 (single_letter_random) | — | 0.67 (B) | 0.8112 – 0.9204 (6 模型) |
| `asap_2` | `extra:overall.qwk` | 7421 | 0.008 | 0.0008 (prior_random) | — | — | 0.4726 – 0.6106 (11 模型) |
| `bea2025_judge` | `extra:recommended_judge_score` | 9904 | 0.2952 | 0.3345 (prior_random) | — | — | 0.3687 – 0.5488 (6 模型) |
| `bea2025_tutor` | `extra:pass_rate` | — | 0 (刻度下限) | — | 0 (echo) | 0.5233 (B) / 同 judge 0.15 | 0.7133 – 0.82 (3 模型) |
| `ceval` | `accuracy` | 1346 | 0.2515 | 0.2623 (majority_constant) | — | — | 0.8276 – 0.9547 (7 模型) |
| `edubench` | `extra:overall.mean_overall_score` | — | 1 (刻度下限) | — | 3.1104 (generic) | 无 | 7.4702 – 8.4796 (12 模型) |
| `eduguard_adversarial` | `extra:overall.asr` | — | — | — | 0 (random) | — | 0.0038 – 0.6241 (16 模型) ↓越低越好 |
| `eduguard_sata` | `extra:overall.rfs` | 5270 | 0.1002 | 0.2509 (single_letter_random) | — | — | 0.6934 – 0.7694 (7 模型) |
| `eduillustrate` | `extra:overall_mean_all_items` | — | 0 (刻度下限) | — | 待跑 | 无 | — |
| `ifeval` | `extra:prompt_strict_accuracy` | 541 | n/a | 0.0555 (generic_text) | — | — | 0.8741 – 0.9298 (5 模型) |
| `k12bench` | `accuracy` | 23640 | 0.0669 | 0.2066 (majority_constant) | — | — | 0.5001 – 0.5001 (1 模型) |
| `k12vista` | `extra:official_score` | — | 0 (刻度下限) | — | 0 (_stale_judge-MiniMax-M2.7_random) | — | 0.6548 – 0.7398 (2 模型) |
| `longtutor_diagnosis` | `extra:f1_macro` | 1001 | 0.2262 | 0.2483 (prior_random) | — | 无 | 0.1967 – 0.3158 (5 模型) |
| `longtutor_evidence` | `accuracy` | — | 0 (刻度下限) | — | 0 (random) | 无 | 0.7122 – 0.8069 (5 模型) |
| `longtutor_teaching` | `accuracy` | — | — | — | 待跑 | 无 | 0.999 – 1 (5 模型) |
| `mathtutorbench_judge_calibration` | `accuracy` | 964 | 0.4998 | 0.5 (always_a) | — | 无 | 0.8102 – 0.8444 (6 模型) |
| `mathtutorbench_mistake_correction` | `accuracy` | 1002 | n/a | 0.0141 (prior_random) | — | 无 | 0.8603 – 0.9371 (5 模型) |
| `mathtutorbench_mistake_location` | `extra:f1_micro` | 2004 | 0.0996 | 0.5 (always_zero) | — | 无 | 0.763 – 0.7919 (6 模型) |
| `mathtutorbench_pedagogy` | `extra:win_rate` | — | — | 0.5 (random_judge) | — | 无 | 0.7448 – 0.867 (7 模型) |
| `mathtutorbench_pedagogy_hard` | `extra:win_rate` | — | — | 0.5 (random_judge) | — | 无 | 0.6621 – 0.8639 (7 模型) |
| `mathtutorbench_problem_solving` | `accuracy` | 1319 | n/a | 0.0111 (prior_random) | — | 无 | 0.9545 – 0.9803 (5 模型) |
| `mathtutorbench_scaffolding` | `extra:win_rate` | — | — | 0.5 (random_judge) | — | 无 | 0.1426 – 0.5948 (7 模型) |
| `mathtutorbench_scaffolding_hard` | `extra:win_rate` | — | — | 0.5 (random_judge) | — | 无 | 0.13 – 0.5612 (7 模型) |
| `mathtutorbench_socratic` | `extra:avg_bleu` | — | — | 0 (random_text) | — | 无 | 0.2131 – 0.2976 (4 模型) |
| `mathtutorbench_solution_correctness` | `extra:f1` | 2004 | 0.4996 | 0.6667 (always_yes) | — | 无 | 0.8567 – 0.8952 (6 模型) |
| `mathvista` | `accuracy` | 1000 | 0.1792 | 0.1991 (prior_random) | — | 0.603 (A) | 0.8409 – 0.887 (2 模型) |
| `mmlu_pro` | `accuracy` | 12032 | 0.1113 | 0.1166 (majority_constant) | — | — | 0.8273 – 0.8827 (6 模型) |
| `mmtutorbench` | `extra:average_total_score_0_to_6` | — | 0 (刻度下限) | — | 0.75 (generic) | 5.85 (B) | 3.4447 – 4.5584 (2 模型) |
| `mmtutorbench_judge_calibration` | `—` | — | — | — | 待跑 | 无 | — |
| `mooccube_prereq` | `extra:score_10` | 300 | 0.1029 | — | — | 无 | 3.789 – 4.76 (5 模型) |
| `mrbench_judge` | `extra:macro_over_dimensions.f1_macro` | 13240 | 0.2688 | 0.3337 (prior_random) | — | — | 0.4109 – 0.5615 (6 模型) |
| `mrbench_tutor` | `extra:pass_rate` | — | 0 (刻度下限) | — | 0 (echo) | 0.605 (B) / 同 judge 0.1 | 0.68 – 0.83 (3 模型) |
| `olympiadbench` | `accuracy` | 6728 | n/a | 0.0033 (random_number) | — | — | 0.716 – 0.7662 (3 模型) |
| `p07_selfcheck` | `extra:score_10` | — | — | 5 (never_change) | — | 无 | 5.019 – 5.572 (5 模型) |
| `p08_abstention` | `extra:score_10` | 5200 | n/a | 5 (always_abstain) | — | 无 | 8.62 – 9.12 (5 模型) |
| `p08_calibration` | `extra:score_10` | — | — | 5 (never_high_confidence) | — | 无 | 5.574 – 6.754 (5 模型) |
| `pedagogy_benchmark` | `accuracy` | 1119 | 0.2499 | 0.2931 (majority_constant) | — | — | 0.6935 – 0.8901 (11 模型) |
| `sas_bench` | `extra:overall.qwk` | — | — | 0 (random_or_constant_rating) | — | — | 79.0429 – 86.7666 (8 模型) |
| `tutorbench` | `extra:arr_w_x100` | — | — | — | 2.54 (random) | — | 54.1 – 54.1 (1 模型) |

## 解读警告（读分数前先看这一节）

### 1. 三个指标的地板是 5.0/10，不是 0

- **`p07_selfcheck`** — never_change = **5**：score_10 = 10×[0.5×fix_rate + 0.5×(1−break_rate)]；一个从不修改答案的模型 fix_rate=0、break_rate=0 → 10×0.5 = 5.0
- **`p08_calibration`** — never_high_confidence = **5**：score_10 = 10×[0.5×(1−CWR@90) + 0.5×AUROC]；从不给出 ≥90 的置信度时 CWR 未定义而退化为 10×AUROC，随机置信度 AUROC=0.5 → 5.0
- **`p08_abstention`** — 实测三种与题目无关的策略：always_abstain=5, always_answer=5, coin_flip=4.9906。
  这个 headline 对任何常数策略都恒等于 5.0，超过 5 才说明真的在区分可答/不可答。

对照实跑值（同为 `score_10`）：
- `p07_selfcheck`：5.019 – 5.572（5 模型）——最低的 doubao-seed-2.0-pro 只比平凡策略高 0.019 分。
- `p08_calibration`：5.574 – 6.754（5 模型）——最低的 MiniMax-M2.7 只比平凡策略高 0.574 分。
- `p08_abstention`：8.62 – 9.12（5 模型）——最低的 MiniMax-M2.7 只比平凡策略高 3.62 分。

**p07_selfcheck 尤其值得停下来看**：它衡量的是「自我复查能不能改对而不改坏」，
而全部模型都挤在 5.0 这条「从不改答案」的线附近。这不是分数低，是这个指标目前几乎没测出东西。

### 2. 类别不平衡的判分任务：多数类基线远高于随机

- **`mrbench_judge`**（headline `extra:macro_over_dimensions.f1_macro`）：
  - uniform_random: headline=0.2688, accuracy=0.3353
  - prior_random: headline=0.3337, accuracy=0.5973
  - majority_constant: headline=0.2783, accuracy=0.7246
- **`bea2025_judge`**（headline `extra:recommended_judge_score`）：
  - uniform_random: headline=0.2952, accuracy=0.3322
  - prior_random: headline=0.3345, accuracy=0.4843
  - majority_constant: headline=0.2551, accuracy=0.6252

注意 accuracy 与 headline 的分裂：全选多数类的 **accuracy 能到 0.63–0.72**，
但 macro-F1 只有 0.26–0.28。仓库把 headline 定成 macro-F1 是对的，
**任何时候都不要用这两个 benchmark 的 accuracy 做横向比较**。

### 3. 地板吃掉了报告分数的多少

「地板占比」= 平凡策略分 ÷ 最好成绩。占比越高，说明公布出来的那个数里
越大一块是白送的，模型之间真正拉开的差距越小。

| benchmark | 最强平凡策略 | 地板 | 实跑最低 | 实跑最高 | 地板占比 | 地板以上的有效区间 |
|---|---|---|---|---|---|---|
| `p07_selfcheck` | `never_change` | 5 | 5.019 | 5.572 | **90%** | 0.572 |
| `mathtutorbench_scaffolding_hard` | `random_judge` | 0.5 | 0.13 | 0.5612 | **89%** | 0.0612 |
| `mathtutorbench_scaffolding` | `random_judge` | 0.5 | 0.1426 | 0.5948 | **84%** | 0.0948 |
| `longtutor_diagnosis` | `prior_random` | 0.2483 | 0.1967 | 0.3158 | **79%** | 0.0675 |
| `mathtutorbench_solution_correctness` | `always_yes` | 0.6667 | 0.8567 | 0.8952 | **74%** | 0.2285 |
| `p08_calibration` | `never_high_confidence` | 5 | 5.574 | 6.754 | **74%** | 1.754 |
| `mathtutorbench_mistake_location` | `always_zero` | 0.5 | 0.763 | 0.7919 | **63%** | 0.2919 |
| `bea2025_judge` | `prior_random` | 0.3345 | 0.3687 | 0.5488 | **61%** | 0.2143 |
| `mrbench_judge` | `prior_random` | 0.3337 | 0.4109 | 0.5615 | **59%** | 0.2278 |
| `mathtutorbench_judge_calibration` | `always_a` | 0.5 | 0.8102 | 0.8444 | **59%** | 0.3444 |
| `mathtutorbench_pedagogy_hard` | `random_judge` | 0.5 | 0.6621 | 0.8639 | **58%** | 0.3639 |
| `mathtutorbench_pedagogy` | `random_judge` | 0.5 | 0.7448 | 0.867 | **58%** | 0.367 |
| `p08_abstention` | `always_abstain` | 5 | 8.62 | 9.12 | **55%** | 4.12 |
| `k12bench` | `majority_constant` | 0.2066 | 0.5001 | 0.5001 | **41%** | 0.2935 |
| `pedagogy_benchmark` | `majority_constant` | 0.2931 | 0.6935 | 0.8901 | **33%** | 0.597 |
| `eduguard_sata` | `single_letter_random` | 0.2509 | 0.6934 | 0.7694 | **33%** | 0.5185 |
| `ceval` | `majority_constant` | 0.2623 | 0.8276 | 0.9547 | **27%** | 0.6924 |

### 3b. 跌破地板的：这些分数说明模型在该任务上没有可用信号

**`longtutor_diagnosis`**（地板 0.2483，策略 `prior_random`）—— 3/5 个模型跌破：
- MiniMax-M2.7: 0.1967
- glm-5.2: 0.2314
- doubao-seed-2.0-pro: 0.2338

**`mathtutorbench_scaffolding`**（地板 0.5，策略 `random_judge`）—— 5/7 个模型跌破：
- MiniMax-M2.7: 0.1426
- deepseek-v4-flash: 0.15
- doubao-seed-2.0-lite: 0.2537
- MiniMax-M3: 0.2713
- doubao-seed-2.0-pro: 0.3496

**`mathtutorbench_scaffolding_hard`**（地板 0.5，策略 `random_judge`）—— 6/7 个模型跌破：
- MiniMax-M2.7: 0.13
- deepseek-v4-flash: 0.1667
- doubao-seed-2.0-lite: 0.204
- MiniMax-M3: 0.2248
- doubao-seed-2.0-pro: 0.3425
- deepseek-v4-pro: 0.4128

`mathtutorbench_scaffolding` 这一条尤其要读懂：它的 headline 是**与金标教师回应的成对胜率**，
0.5 就是「与专家教师打平」。跌破 0.5 不是「分数偏低」，而是**在搭脚手架这件事上确实不如人类教师**。
对照 `mathtutorbench_pedagogy`（同样的比法、同样的 0.5 锚）七个模型全部在 0.66–0.87：
**这两个任务的结论方向是相反的**，而只看原始分会以为都是「有的高有的低」。

### 4. 地板在另一头 / 指标本身无区分度

- **`longtutor_teaching`**：judge 打 4 维 1-5 分（刻度下限 1，归一时按 (raw−1)/4 已扣掉）。⚠ 其 accuracy 只是「四个分数都成功解析且非 0」，实跑 0.999-1.000，是解析成功率不是能力分，不可用于比较模型
- **`eduguard_adversarial`**：⚠ 越狱攻击成功与否由内容决定，无 chance level；地板在另一头——全部拒答 = ASR 0 = 满分。乱码既非越狱成功也非合格拒答，落点只能实测

## ⚠ 最重要的发现：judge 把人类专家教师排在所有模型之下

这是本轮基线工作的副产品，但比任何一条地板都重要。

MRBench 和 BEA 2025 的数据集里自带**真人专家教师**的回复。把这批回复原样喂给
我们评测模型时用的那个 judge，得到的分数应该和人类标注者给同一批回复的分数接近——
否则两把尺子就不是一回事。结果差得很远：

| benchmark | 题数 | 人类标注者判专家 | 我们的 judge 判**同一批**专家 | 同一 judge 判模型 |
|---|---|---|---|---|
| `bea2025_tutor` | 40 | **0.525** | **0.15** | 0.7133 – 0.82 |
| `mrbench_tutor` | 40 | **0.65** | **0.1** | 0.68 – 0.83 |

**人类标注者认为专家教师和模型在同一水平线上（0.53–0.65 vs 0.68–0.83）；
我们的 judge 认为专家教师（0.10–0.15）远不如模型（0.68–0.83）。**

崩在哪一维，逐维看得很清楚：

| benchmark | 维度 | 人类标注 | 我们的 judge | 落差 |
|---|---|---|---|---|
| `bea2025_tutor` | Mistake_Identification | 0.875 | 0.475 | −0.4 ⚠ |
| `bea2025_tutor` | Providing_Guidance | 0.65 | 0.575 | −0.075 |
| `bea2025_tutor` | Actionability | 0.7 | 0.425 | −0.275 |
| `mrbench_tutor` | Mistake_Identification | 0.775 | 0.55 | −0.225 |
| `mrbench_tutor` | Providing_Guidance | 0.725 | 0.375 | −0.35 |
| `mrbench_tutor` | Actionability | 0.85 | 0.3 | −0.55 ⚠ |

`Actionability` 塌得最狠（MRBench 0.85 → 0.30）。看一条真实的专家回复就明白了：

> Not quite, remember, Jam has three boxes full of pencils and 2 loose pencils
> which give a total of 26 pencils.

真人教师说话短、依赖上下文，不会把「你下一步该做什么」显式写出来；
人类标注者懂教学语境，判 Yes。LLM judge 找不到显式的行动指令，判 No。
而模型的回复通常长、结构化、把每个 rubric 关键词都写全——正好投 judge 所好。

### 这意味着什么

`mrbench_tutor` / `bea2025_tutor` 的 `pass_rate`，在我们当前的 judge 下，
**相当程度上测的是「写得像不像 LLM 式辅导」，而不是教学质量**。
三点后果：

1. **不要拿这两个 benchmark 的分数说「模型的辅导能力接近/超过人类教师」。**
   本报告主表里那个 0.605 的人类值是人类标注者给的，与模型分不同尺，已标为 B 级。
2. **映射受影响。** `mrbench_tutor` 的逐维 Yes 占比挂在 P13/P15/P17 上，
   这部分分数带着同样的风格偏好。
3. **这是可修的。** 要么换 judge 并用这批专家回复做校准（专家应当落在模型区间内），
   要么改 rubric 让 Actionability 不再奖励显式措辞。修之前，先别把这两个分数当教学质量看。

## 人类表现：能查到的很少，查不到的如实留空

5/19 个 benchmark 有可用的人类数值，另有 20 个属自建或无外部人类参照。分级分布：{'A': 1, 'B': 4, 'null': 14}。

| 分级 | 含义 |
|---|---|
| **A** | 同 benchmark、同 split、同指标，直接可比 |
| **B** | 同 benchmark 但 split / 子集 / 评分协议有差异，需换算或只能定性对照 |
| **C** | 制度性代理（考试及格线、人群均分）或构造性上限，非题级实测 |
| **D** | 仅作语境（SOTA 系统分、judge 可靠性、其他 benchmark），绝不当人类基线，只进 context_anchors |

### 有数的

| benchmark | 人类值 | 分级 | 来源 | 关键限制 |
|---|---|---|---|---|
| `agieval` | 0.67 | B | AGIEval (NAACL 2024 Findings), arXiv:2304.06364；仓库 data/exhaustive_2026-05-13/results.jsonl 已收录 | 论文只对 LSAT / SAT / Gaokao 这些真人考试子集给出人类分，而我们跑的 7,272 题还包含 MATH(1,000) 等无人类分的任务，所以 0.670 不能直接和我们的总 accuracy 并列，只能逐 task 对齐后使用。 |
| `bea2025_tutor` | 0.5233 | B | 本地 mrbench_v3_devset.json 自带的 Expert 教师回复 + 人类标注 | 由本地数据集自带的 Expert / Novice 人类教师回复 + 人类标注金标算出，用的是 adapter 自己的标签归一与 KEY_DIMENSIONS 判定，因此与我们的 pass_rate 同口径同题集。唯一的口径差：这里的标签来自人类标注者，我们模型的标签来自 LLM judge。跑 scripts/run_reference_baseline.py --variant expert 用同一个 judge 复评后才严格可比。 |
| `mathvista` | 0.603 | A | MathVista (ICLR 2024), arXiv:2310.02255；官方 repo lupantech/MathVista 榜单 | 论文的人类评测就在 testmini 1,000 题上做，与我们的评测集完全一致。 |
| `mmtutorbench` | 5.85 | B | MMTutorBench (ACL 2026), arXiv:2510.23477 | 两处不可比：(1) 人类只在 66 题子集上评，我们跑 770 行；(2) 人类回复由论文的 GPT-o4-mini rubric judge 打分，我们的固定 judge 是 MiniMax-M3。judge 不同会整体平移分数，跨 judge 直接比会误判。 |
| `mrbench_tutor` | 0.605 | B | 本地 MRBench_V2.json 自带的 Expert 教师回复 + 人类标注 | 由本地数据集自带的 Expert / Novice 人类教师回复 + 人类标注金标算出，用的是 adapter 自己的标签归一与 KEY_DIMENSIONS 判定，因此与我们的 pass_rate 同口径同题集。唯一的口径差：这里的标签来自人类标注者，我们模型的标签来自 LLM judge。跑 scripts/run_reference_baseline.py --variant expert 用同一个 judge 复评后才严格可比。 |

### 查过但没有的（附证据，不必重查）

| benchmark | 查了什么 | 结论 |
|---|---|---|
| `asap_2` | ASAP 2.0 corpus paper (Crossley et al., Assessing Writing, 2025) | 已查 GitHub README 与语料论文页：README 未给一致性数字，论文 403。 |
| `bea2025_judge` | Findings of the BEA 2025 Shared Task, arXiv:2507.10579 | 已查 Findings 论文：给出各赛道最佳系统分与参赛规模，未给人类基线。 |
| `ceval` | C-Eval (NeurIPS 2023 D&B), arXiv:2305.08322 | 已查论文与 NeurIPS 版：无 human 行。 |
| `eduguard_adversarial` | EduGuardBench, arXiv:2511.06890 | 已查论文：给出 judge 校准 kappa，无人类 ASR。 |
| `eduguard_sata` | EduGuardBench, arXiv:2511.06890 | 已查论文：只有 judge 与人类的校准 kappa，无人类作答分。 |
| `ifeval` | IFEval, Google Research | 论文无人类实验；此处只记构造性上限。 |
| `k12bench` | K12-KGraph, arXiv:2605.09635 | 已查论文与项目页：无 human baseline。 |
| `k12vista` | K12Vista, arXiv:2506.01676 | 已查论文摘要与项目页：无 human 作答分。 |
| `mmlu_pro` | MMLU-Pro (NeurIPS 2024 D&B) | 已查论文：无 human 行；MMLU 的 89.8% 出自 arXiv:2009.03300，属另一 benchmark。 |
| `mrbench_judge` | Unifying AI Tutor Evaluation / MRBench, arXiv:2412.09416 | 论文正文给出总体 kappa 0.71 与试点 Fleiss 0.65，未按维度拆分。 |
| `olympiadbench` | OlympiadBench (ACL 2024), arXiv:2402.14008 | 已查 arXiv:2402.14008 摘要与正文：无人类基线，仅有定性表述。 |
| `pedagogy_benchmark` | Benchmarking the Pedagogical Knowledge of LLMs, arXiv:2506.18710 | 已查论文：给出人群均分约 50%，同时明确声明 question-level human results are not available。 |
| `sas_bench` | SAS-Bench, arXiv:2505.07247 | 已查 arXiv:2505.07247 全文：明确无 inter-annotator agreement 数字。 |
| `tutorbench` | TutorBench (Scale AI), arXiv:2510.02663 | 已查论文：只有 judge-人类一致性与模型分，无人类作答分。 |

## L3 实跑明细：退化回复与人类参照，同一个 judge

`refusal` = 「我不确定」；`echo` = 复述原话；`generic` = 与题无关但语气漂亮的通用教学话术；
`expert` / `novice` = 数据集自带的人类教师回复，用**我们的 judge** 复评。

| benchmark | 变体 | 层 | 题数 | headline | judge |
|---|---|---|---|---|---|
| `bea2025_tutor` | echo | L3_degenerate | 40 | 0 | MiniMax-M3 |
| `bea2025_tutor` | expert | L3_reference | 40 | 0.15 | MiniMax-M3 |
| `bea2025_tutor` | generic | L3_degenerate | 40 | 0 | MiniMax-M3 |
| `bea2025_tutor` | novice | L3_reference | 12 ⚠<20，样本过小，仅表示管线跑通 | 0.0833 | MiniMax-M3 |
| `bea2025_tutor` | random | L3_degenerate | 37 | 0 | MiniMax-M3 |
| `bea2025_tutor` | refusal | L3_degenerate | 37 | 0 | MiniMax-M3 |
| `edubench` | echo | L3_degenerate | 40 | — | deepseek-v3.2 |
| `edubench` | generic | L3_degenerate | 40 | — | deepseek-v3.2 |
| `edubench` | random | L3_degenerate | 40 | — | deepseek-v3.2 |
| `edubench` | refusal | L3_degenerate | 40 | — | deepseek-v3.2 |
| `eduguard_adversarial` | random | L3_degenerate | 40 | 0 | MiniMax-M3 |
| `k12vista` | _stale_judge-MiniMax-M2.7_random | L3_degenerate | 38 | 0 | MiniMax-M2.7 |
| `k12vista` | random | L3_degenerate | 40 | 0 | MiniMax-M3 |
| `longtutor_evidence` | random | L3_degenerate | 38 | 0 | MiniMax-M3 |
| `mmtutorbench` | echo | L3_degenerate | 40 | 0.05 | MiniMax-M3 |
| `mmtutorbench` | generic | L3_degenerate | 40 | 0.75 | MiniMax-M3 |
| `mmtutorbench` | random | L3_degenerate | 40 | 0 | MiniMax-M3 |
| `mmtutorbench` | refusal | L3_degenerate | 40 | 0.2083 | MiniMax-M3 |
| `mrbench_tutor` | echo | L3_degenerate | 37 | 0 | MiniMax-M3 |
| `mrbench_tutor` | expert | L3_reference | 40 | 0.1 | MiniMax-M3 |
| `mrbench_tutor` | generic | L3_degenerate | 40 | 0 | MiniMax-M3 |
| `mrbench_tutor` | novice | L3_reference | 11 ⚠<20，样本过小，仅表示管线跑通 | 0 | MiniMax-M3 |
| `mrbench_tutor` | random | L3_degenerate | 32 | 0 | MiniMax-M3 |
| `mrbench_tutor` | refusal | L3_degenerate | 40 | 0 | MiniMax-M3 |
| `tutorbench` | random | L3_degenerate | 40 | 2.54 | MiniMax-M3 |

**读法**：`generic` 这一行最关键。它完全没有解题内容，只有教学腔。
它拿到的分就是该 judge 奖励「形式」而非「实质」的部分，必须从模型分里扣掉再看差距。

## 为什么有些 benchmark 没有随机分

主表里的空格几乎都不是「没算」，而是**均匀随机在那种题型上没有定义**。四类：

### A. judge 打分的生成题——随机的对应物是乱码，得实测

模型要写一段话，不存在「选项」可以抽。但**期望仍然是有的**：生成任务的答案空间就是
token 序列，在它上面均匀抽样就是乱码。所以「瞎填能得几分」= 把乱码喂给真实 judge 看它给几分，
对应 L3 的 **`random`** 变体。

两点要注意：

1. **不是所有都归零。** 打分量表自带下限，乱码也拿得到。EduBench 是 1-10 量表，
   下限就是 **1.0**；拿模型的 8.0 直接当「比 0 高 8 分」会把差距高估整整一分。
   下表的「刻度下限」列就是这个数。
2. **有一个可能是负的。** TutorBench 的 rubric 含 −5 权重项，乱码的期望**低于 0**。

| benchmark | 刻度下限 | 说明 |
|---|---|---|
| `bea2025_tutor` | 0 | 生成 + 固定 judge 打 4 维标签，同上 |
| `edubench` | 1 | 12 维 1-10 量表由固定 judge 打分。乱码的期望是刻度下限 1.0，不是 0 |
| `eduguard_adversarial` | 需实测 | ⚠ 越狱攻击成功与否由内容决定，无 chance level；地板在另一头——全部拒答 = ASR 0 = 满分。乱码既非越狱成功也非合格拒答，落点只能实测 |
| `eduillustrate` | 0 | 8 维 0-5 Likert 由 judge 打分；独立管线（scripts/eval/build_eduillustrate_report.py），不在 adapter 注册表里 |
| `k12vista` | 0 | 逐空 0/1 由 judge 判定；其中的选择题子集会给随机作答少量命中 |
| `longtutor_evidence` | 0 | judge 判语义等价 CORRECT/INCORRECT，乱码必判 INCORRECT |
| `longtutor_teaching` | 需实测 | judge 打 4 维 1-5 分（刻度下限 1，归一时按 (raw−1)/4 已扣掉）。⚠ 其 accuracy 只是「四个分数都成功解析且非 0」，实跑 0.999-1.000，是解析成功率不是能力分，不可用于比较模型 |
| `mmtutorbench` | 0 | 6 个二元 rubric 由固定 judge 打分，全 0 即 0/6 |
| `mmtutorbench_judge_calibration` | 需实测 | 无公开人类金标，adapter 本身不产出题目 |
| `mrbench_tutor` | 0 | 生成 + 固定 judge 打 8 维标签，pass 要求三个关键维度全 Yes |
| `tutorbench` | 需实测 | 加权 rubric（critical +5 / not_critical +1 / critical_negative −5），ARR_w 可为负，故乱码的期望**低于** 0，只能实测 |

### B. 地板是代数推出来的，模拟没有意义

- `mathtutorbench_pedagogy` — 与金标教师回应成对比较，位置交换两轮取平均。随机选择时 win_score 期望 = 0.5（(0,1) 与 (1,0) 各 1/4，平局 0.5 占 1/2）
- `mathtutorbench_pedagogy_hard` — 与金标教师回应成对比较，位置交换两轮取平均。随机选择时 win_score 期望 = 0.5（(0,1) 与 (1,0) 各 1/4，平局 0.5 占 1/2）
- `mathtutorbench_scaffolding` — 与金标教师回应成对比较，位置交换两轮取平均。随机选择时 win_score 期望 = 0.5（(0,1) 与 (1,0) 各 1/4，平局 0.5 占 1/2）
- `mathtutorbench_scaffolding_hard` — 与金标教师回应成对比较，位置交换两轮取平均。随机选择时 win_score 期望 = 0.5（(0,1) 与 (1,0) 各 1/4，平局 0.5 占 1/2）
- `mathtutorbench_socratic` — 与参考问句的 sentence-BLEU，随机文本期望 ≈ 0
- `p07_selfcheck` — score_10 = 10×[0.5×fix_rate + 0.5×(1−break_rate)]；一个从不修改答案的模型 fix_rate=0、break_rate=0 → 10×0.5 = 5.0
- `p08_calibration` — score_10 = 10×[0.5×(1−CWR@90) + 0.5×AUROC]；从不给出 ≥90 的置信度时 CWR 未定义而退化为 10×AUROC，随机置信度 AUROC=0.5 → 5.0
- `sas_bench` — QWK/CCS/ECS 都是 chance-corrected 一致性统计量，随机与常数评分的期望都是 0

### C. 答案空间是开放的，「均匀」无从定义

填任意实数或 LaTeX 表达式的题，在实数上均匀抽样的命中概率测度为 0。
这类改用更严的替代策略——按数据集真实答案分布猜（`prior_random`），
即「瞎猜的上界」；规则校验类则用一段与题无关的通用文本。

- `ifeval` — 替代策略：`generic_text`=0.0555, `empty`=0
  - 规则校验器，无随机可言；用一段与题无关的通用文本量出「形式合格但内容无关」的地板。
- `mathtutorbench_mistake_correction` — 替代策略：`prior_random`=0.0141
  - 开放数值答案，随机 ≈ 0；prior_random 是「按答案先验瞎猜」的上界。
- `mathtutorbench_problem_solving` — 替代策略：`prior_random`=0.0111
  - 开放数值答案，随机 ≈ 0；prior_random 是「按答案先验瞎猜」的上界。
- `olympiadbench` — 替代策略：`random_number`=0.0033
  - 开放数值/符号答案，随机 ≈ 0。sympy 判定很慢，只在 300 题样本上做经验确认。
- `p08_abstention` — 替代策略：`always_abstain`=5, `always_answer`=5, `coin_flip`=4.9906
  - ⚠ headline score_10 = 10×(弃答recall + 可答作答率)/2 —— 全弃答、全作答、抛硬币三种策略的期望值都恰好 5.0。这个指标对任何与题目无关的策略恒等于 5，必须单列说明。

### D. 反过来的一个

- `mooccube_prereq` — 唯一自带 chance correction 的 benchmark，
  随机作答的 `score_10` 已经被扣到接近 0，不存在比它更高的平凡策略，所以 L2 空着。

## 未覆盖 / 待办

- L3 只跑了部分 benchmark。其余 judge 打分的生成类任务见 `data/benchmark_baselines_v1.json` → `judge_only`，用 `scripts/run_reference_baseline.py` 逐个补。
- 本报告**不改**聚合脚本的归一化。给 P01–P20 做 chance correction 会让分数与 R25 不可比，
  那是独立决策；`benchmark_baselines_v1.json` 的字段已为此留好接口。

