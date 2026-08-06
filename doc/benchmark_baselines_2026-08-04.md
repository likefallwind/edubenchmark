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
| **L3 退化回答** | 一段与题无关的回复交给真实 judge 打分 | judge 打分的生成类任务 |

**L1 几乎总是有定义的，只是它的形状随答案空间变。** 早先的表把 L1 一律理解成
「名叫 `uniform_random` 的那个策略」，对三分之一的 benchmark 是错的：
`p08_abstention` 的均匀抽样是 `coin_flip`（4.99，不是 0），成对比较任务的是随机 judge（0.5），
生成任务的则是乱码——也就是 L3 的 `random` 变体本身。现在每个 benchmark 在
`benchmark_baselines_v1.json` 里都带一个 `l1` 块写明它的 L1 是哪个数、怎么来的，
主表的 L1 列直接读它，三种来源分别标注：不带后缀=模拟，`(推导)`=闭式，`(乱码实测)`=经 judge 实测。

真正没有 L1 的只剩一个：`mmtutorbench_judge_calibration`——它没有公开人类金标，
adapter 本身不产出题目，没有可抽样的答案空间。表里记 `n/a`。

方法上没有手推公式，而是**用真实的 `adapter.score()` 和 `extra_summary()` 跑合成答案**，
这样 RFS 的部分分、macro-F1、QWK 都走的是和正式评测同一条代码路径。
闭式解只留作交叉验证。

**方法论验证**：用「MC 逐题 1/k + free-form 记 0」模拟 MathVista，得 0.1792，而官方论文公布的 Random chance 是 **0.179**——对得上。

## 主表

`L1` = 均匀随机；`L2` = 最强的平凡策略（括号内是策略名）；`L3` = 退化回复经真实 judge；
`人类` = 文献或数据集自带的人类参照（分级见下）；`实跑` = 已完成 run 的区间。
**同一行内所有数字都是该 benchmark headline 的原始标度**，跨行不可比。

空格的含义要分清（见文末「L1 的三种来源」）：

- **`n/a`** = 该层在这个 benchmark 上**没有定义**，不是没算。
- **`待跑`** = 需要 API 的实测还没跑到这一行（L1 列出现它，说明该 benchmark 的 L1 就是 L3 的乱码变体）。
- **`—`** = 该层不适用（judge 类任务没有 L2，规则判分类任务没有 L3）。
- **`⚠满分方向`** = 该 headline 越低越好，这个数落在满分那一头，**不是地板**。

| benchmark | headline | 题数 | L1 随机 | L2 平凡策略 | L3 退化 | 人类 | 实跑区间 |
|---|---|---|---|---|---|---|---|
| `agieval` | `accuracy` | 7272 | 0.1737 | 0.2057 (single_letter_random) | — | 0.67 (B) | 0.8112 – 0.9204 (6 模型) |
| `asap_2` | `extra:overall.qwk` | 7421 | 0.008 | 0.0008 (prior_random) | — | — | 0.4726 – 0.6106 (11 模型) |
| `bea2025_judge` | `extra:recommended_judge_score` | 9904 | 0.2952 | 0.3345 (prior_random) | — | — | 0.3687 – 0.5488 (7 模型) |
| `bea2025_tutor` | `extra:pass_rate` | — | 0 (乱码实测) | — | 0 (echo) | 0.5233 (B) / 同 judge 0.1601 | 0.7133 – 0.8233 (4 模型) |
| `ceval` | `accuracy` | 1346 | 0.2515 | 0.2623 (majority_constant) | — | — | 0.8276 – 0.9547 (7 模型) |
| `edubench` | `extra:overall.mean_overall_score` | — | 1 (乱码实测) | — | 3.1104 (generic) | 无 | 7.4702 – 8.4796 (12 模型) |
| `eduguard_adversarial` | `extra:overall.asr` | — | 0 (乱码实测) ⚠满分方向 | — | 0 (random) | — | 0.0038 – 0.6241 (16 模型) ↓越低越好 |
| `eduguard_sata` | `extra:overall.rfs` | 5270 | 0.1002 | 0.2509 (single_letter_random) | — | — | 0.6934 – 0.7694 (7 模型) |
| `eduillustrate` | `extra:overall_mean_all_items` | — | 0 (推导) | — | 待跑 | 无 | — |
| `ifeval` | `extra:prompt_strict_accuracy` | 541 | 0.1183 | 0.0555 (generic_text) | — | — | 0.8741 – 0.9298 (5 模型) |
| `k12bench` | `accuracy` | 23640 | 0.0669 | 0.2066 (majority_constant) | — | — | 0.5001 – 0.5001 (1 模型) |
| `k12vista` | `extra:official_score` | — | 0 (乱码实测) | — | 0 (random) | — | 0.6548 – 0.7398 (2 模型) |
| `longtutor_diagnosis` | `extra:f1_macro` | 1001 | 0.2262 | 0.2483 (prior_random) | — | 无 | 0.1967 – 0.3158 (5 模型) |
| `longtutor_evidence` | `accuracy` | — | 0 (乱码实测) | — | 0 (random) | 无 | 0.7122 – 0.8069 (5 模型) |
| `longtutor_teaching` | `extra:judge_scores.average` | — | 1 (推导) | — | 待跑 | 无 | 3.038 – 4.234 (5 模型) |
| `mathtutorbench_judge_calibration` | `accuracy` | 964 | 0.4998 | 0.5 (always_a) | — | 无 | 0.8102 – 0.8444 (7 模型) |
| `mathtutorbench_mistake_correction` | `accuracy` | 1002 | 0 (推导) | 0.0141 (prior_random) | — | 无 | 0.8603 – 0.9421 (6 模型) |
| `mathtutorbench_mistake_location` | `extra:f1_micro` | 2004 | 0.0996 | 0.5 (always_zero) | — | 无 | 0.763 – 0.7919 (6 模型) |
| `mathtutorbench_pedagogy` | `extra:win_rate` | — | 0.5 (推导) | — | — | 无 | 0.7448 – 0.867 (7 模型) |
| `mathtutorbench_pedagogy_hard` | `extra:win_rate` | — | 0.5 (推导) | — | — | 无 | 0.6621 – 0.8639 (7 模型) |
| `mathtutorbench_problem_solving` | `accuracy` | 1319 | 0 (推导) | 0.0111 (prior_random) | — | 无 | 0.9545 – 0.9803 (5 模型) |
| `mathtutorbench_scaffolding` | `extra:win_rate` | — | 0.5 (推导) | — | — | 无 | 0.1426 – 0.5948 (7 模型) |
| `mathtutorbench_scaffolding_hard` | `extra:win_rate` | — | 0.5 (推导) | — | — | 无 | 0.13 – 0.5612 (7 模型) |
| `mathtutorbench_socratic` | `extra:avg_bleu` | — | 0 (推导) | — | — | 无 | 0.2131 – 0.2976 (5 模型) |
| `mathtutorbench_solution_correctness` | `extra:f1` | 2004 | 0.4996 | 0.6667 (always_yes) | — | 无 | 0.8567 – 0.8952 (6 模型) |
| `mathvista` | `accuracy` | 1000 | 0.1792 | 0.1991 (prior_random) | — | 0.603 (A) | 0.8409 – 0.887 (2 模型) |
| `mmlu_pro` | `accuracy` | 12032 | 0.1113 | 0.1166 (majority_constant) | — | — | 0.8273 – 0.8827 (6 模型) |
| `mmtutorbench` | `extra:average_total_score_0_to_6` | — | 0 (乱码实测) | — | 0.75 (generic) | 5.85 (B) | 3.4447 – 4.5584 (2 模型) |
| `mmtutorbench_judge_calibration` | `—` | — | n/a | — | 待跑 | 无 | — |
| `mooccube_prereq` | `extra:score_10` | 300 | 0.1029 | — | — | 无 | 3.789 – 4.76 (5 模型) |
| `mrbench_judge` | `extra:macro_over_dimensions.f1_macro` | 13240 | 0.2688 | 0.3337 (prior_random) | — | — | 0.4109 – 0.5615 (6 模型) |
| `mrbench_tutor` | `extra:pass_rate` | — | 0 (乱码实测) | — | 0 (echo) | 0.605 (B) / 同 judge 0.1637 | 0.68 – 0.83 (3 模型) |
| `olympiadbench` | `accuracy` | 6728 | 0 (推导) | 0.0033 (random_number) | — | — | 0.716 – 0.7662 (3 模型) |
| `p07_selfcheck` | `extra:score_10` | 550 | 1.8518 | 5 (never_change) | — | 无 | 5.019 – 5.572 (5 模型) |
| `p08_abstention` | `extra:score_10` | 5200 | 4.9906 | 5 (always_abstain) | — | 无 | 8.62 – 9.12 (5 模型) |
| `p08_calibration` | `extra:score_10` | 550 | 3.3248 | 5 (never_high_confidence) | — | 无 | 5.574 – 6.754 (5 模型) |
| `pedagogy_benchmark` | `accuracy` | 1119 | 0.2499 | 0.2931 (majority_constant) | — | — | 0.6935 – 0.8901 (11 模型) |
| `sas_bench` | `extra:overall.qwk` | — | 0 (推导) | 0 (constant_rating) | — | — | 79.0429 – 86.7666 (8 模型) |
| `tutorbench` | `extra:arr_w_x100` | — | 2.54 (乱码实测) | — | 2.54 (random) | — | 54.1 – 54.1 (1 模型) |

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

这三个的 **L1 和 L2 分得很开**，别把 5.0 当成随机分：

- `p07_selfcheck` — L1 均匀乱答 = **1.852**，L2 最优平凡策略 = **5.0**。两轮都均匀乱答：fix_rate 与 break_rate 同时趋近 chance 与 1−chance，score_10 收敛到 10×chance，远低于 never_change 的 5.0。
- `p08_calibration` — L1 均匀乱答 = **3.325**，L2 最优平凡策略 = **5.0**。答案与置信度都均匀随机：AUROC 回到 0.5，固定贡献 2.5 分；CWR@90 不是 1——均匀置信度把约一成题推过 90 分线，其中仍有 chance 比例答对，CWR 落在 0.84 左右，另一半再给约 0.8 分。合计 3.3，既不是 0 也不到 never_high_confidence 的 5.0。
- `p08_abstention` — L1 均匀乱答 = **4.991**，L2 最优平凡策略 = **5.0**。⚠ headline score_10 = 10×(弃答recall + 可答作答率)/2 —— 全弃答、全作答、抛硬币三种策略的期望值都恰好 5.0。这个指标对任何与题目无关的策略恒等于 5，必须单列说明。

换句话说，一个真去瞎猜的模型在 `p07_selfcheck` 上只有 1.85 分，而一个干脆不复查的模型白拿 5.0——
**这个指标奖励的是「别动」，不是「会查」**，实跑区间紧贴 5.0 正是这个原因。

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

- **`longtutor_teaching`**：judge 打 4 维 1-5 分，刻度下限 1（归一时按 (raw−1)/4 扣掉）。⚠ 不要用它的 accuracy：那只是「四个分数都成功解析且非 0」，实跑 0.999-1.000，1001 题里唯一那次失败是 judge 把 appropriateness 拼成了 appropriance
- **`eduguard_adversarial`**：⚠ 越狱攻击成功与否由内容决定，无 chance level；地板在另一头——全部拒答 = ASR 0 = 满分。乱码既非越狱成功也非合格拒答，落点只能实测

## ⚠ mrbench_tutor / bea2025_tutor 的 prompt 把评分表告诉了模型

这条是查「人类专家为什么分这么低」时挖出来的，属于 harness 缺陷，不是模型或 judge 的问题。

**我们给被测模型的 prompt，逐条罗列了 judge 要打的维度**：

| prompt 里的指令 | judge 的评分维度 |
|---|---|
| identify and locate any mistake the student made | Mistake_Identification + Mistake_Location |
| give a helpful hint or explanation | Providing_Guidance |
| make the next step clear | **Actionability** |
| Do NOT reveal the final answer outright | Revealing_of_the_Answer |
| encouraging | Tutor_Tone |
| natural | Humanlikeness |

bea2025_tutor 的四条指令同样 1:1 对上它的四个维度。MRBench 版还额外把
**参考解法（Reference solution）**放进了 prompt。

也就是说：**模型被明确告知了评分标准，还拿到了答案**。
数据集里的人类专家教师和那 8 个 2024 年 LLM，写回复时两样都没有。

### 后果

这解释了下面这组数为什么会长这样——不需要引入「judge 有偏见」之类的假设：

（专家同尺复评正在重跑，数字待补；`reports/eval/_baseline/*/expert/` 完成后重跑本脚本。）

典型分歧长这样（MRBench，学生上一轮已自己纠正了错误）：

> **专家教师的回复**：So 12 devided by 4 =. .?
>
> 人类标注 `Mistake_Identification` = **Yes**（错误学生已自纠，教师正确识别并推进下一步）
> 我们的 judge = **No**（这句话里找不到任何指出错误的表述）

### 对照：judge 对所有 tutor 都比人类标注者严

顺带排除掉「judge 专门针对人类」这个可能。`mrbench_judge` 的既有 run 里，
同一个模型已经把全部 9 个 tutor 的回复对着人类金标判过一遍（免费的大样本）：

| tutor | 词数中位 | 人类判 pass | judge 判 pass | 差 |
|---|---|---|---|---|
| `Novice` ←人类 | 5 | 0 | 0.0182 | +0.018 |
| `Expert` ←人类 | 16 | 0.605 | 0.175 | -0.430 |
| `Phi3` | 20 | 0.06 | 0.04 | -0.020 |
| `Mistral` | 24 | 0.515 | 0.18 | -0.335 |
| `Gemini` | 24 | 0.5 | 0.095 | -0.405 |
| `Sonnet` | 26 | 0.54 | 0.09 | -0.450 |
| `Llama318B` | 36 | 0.2412 | 0.0704 | -0.171 |
| `GPT4` | 36 | 0.42 | 0.28 | -0.140 |
| `Llama31405B` | 43 | 0.635 | 0.305 | -0.330 |

- judge 对**每一个** tutor 都比人类标注者严，Sonnet 的 −0.450 比人类专家的 −0.430 还狠。
- 回复长度与该落差的相关只有 **r = -0.26**，n=9，不显著。
- 这 9 个 tutor 的回复**都不是用我们的 prompt 生成的**，所以它们全部落在 0.02–0.31，
  而吃了我们 prompt 的模型落在 0.68–0.83 —— 与上面的泄题解释一致。

> 口径说明：mrbench_judge 用 v1 rubric，mrbench_tutor 用 v2；绝对值不可互换，方向与排序可比

### 结论与待办

1. **`pass_rate` 不能当「辅导能力」的绝对值用，更不能拿来和人类教师比。**
   模型手里有评分表和答案，人类专家两样都没有。主表里那个人类值已标为 B 级，
   同尺复评下的 0.10–0.15 也同样不能单独拿出来说事——**两个数都不构成对比**。
2. **模型之间横向比仍然有效**：所有被测模型吃的是同一个 prompt。
3. **映射要留意。** `mrbench_tutor` 的逐维 Yes 占比挂在 P13/P15/P17 上，
   这几个 P 的绝对值含有「照着指令写」的成分。

**决定性实验（未做）**：用一个不罗列评分维度、不给参考解法的中性 prompt，
让同一个现代模型重跑一遍。若 pass_rate 显著回落到人类专家那一档，
就确认是 prompt 泄题；若基本不变，则说明确实是能力差距。
在这个实验出结果前，不要去改 judge 或 rubric——问题大概率不在那边。

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
| `bea2025_tutor` | expert | L3_reference | 281 | 0.1601 | MiniMax-M3 |
| `bea2025_tutor` | generic | L3_degenerate | 40 | 0 | MiniMax-M3 |
| `bea2025_tutor` | novice | L3_reference | 76 | 0.0263 | MiniMax-M3 |
| `bea2025_tutor` | random | L3_degenerate | 37 | 0 | MiniMax-M3 |
| `bea2025_tutor` | refusal | L3_degenerate | 37 | 0 | MiniMax-M3 |
| `edubench` | echo | L3_degenerate | 40 | 1.2396 | deepseek-v3.2 |
| `edubench` | generic | L3_degenerate | 40 | 3.1104 | deepseek-v3.2 |
| `edubench` | random | L3_degenerate | 40 | 1 | deepseek-v3.2 |
| `edubench` | refusal | L3_degenerate | 40 | 1.5042 | deepseek-v3.2 |
| `eduguard_adversarial` | random | L3_degenerate | 40 | 0 | MiniMax-M3 |
| `k12vista` | random | L3_degenerate | 40 | 0 | MiniMax-M3 |
| `longtutor_evidence` | random | L3_degenerate | 38 | 0 | MiniMax-M3 |
| `mmtutorbench` | echo | L3_degenerate | 40 | 0.05 | MiniMax-M3 |
| `mmtutorbench` | generic | L3_degenerate | 40 | 0.75 | MiniMax-M3 |
| `mmtutorbench` | random | L3_degenerate | 40 | 0 | MiniMax-M3 |
| `mmtutorbench` | refusal | L3_degenerate | 40 | 0.2083 | MiniMax-M3 |
| `mrbench_tutor` | echo | L3_degenerate | 37 | 0 | MiniMax-M3 |
| `mrbench_tutor` | expert | L3_reference | 171 | 0.1637 | MiniMax-M3 |
| `mrbench_tutor` | generic | L3_degenerate | 40 | 0 | MiniMax-M3 |
| `mrbench_tutor` | gpt4 | L3_reference | 185 | 0.1946 | MiniMax-M3 |
| `mrbench_tutor` | llama31405b | L3_reference | 182 | 0.2747 | MiniMax-M3 |
| `mrbench_tutor` | novice | L3_reference | 51 | 0 | MiniMax-M3 |
| `mrbench_tutor` | random | L3_degenerate | 32 | 0 | MiniMax-M3 |
| `mrbench_tutor` | refusal | L3_degenerate | 40 | 0 | MiniMax-M3 |
| `mrbench_tutor` | sonnet | L3_reference | 180 | 0.1389 | MiniMax-M3 |
| `tutorbench` | random | L3_degenerate | 40 | 2.54 | MiniMax-M3 |

**读法**：`generic` 这一行最关键。它完全没有解题内容，只有教学腔。
它拿到的分就是该 judge 奖励「形式」而非「实质」的部分，必须从模型分里扣掉再看差距。

## L1 的三种来源

「均匀随机能得多少分」对每个 benchmark 都成立，只是**均匀抽样抽的是什么**不一样，
所以这个数有三种来法。主表的 L1 列按来源标注，下面逐类列全。

### A. 模拟——答案空间可以枚举，直接抽

选项、标签、步号、评分档位这些都能列举，于是用真实的 `adapter.score()` 跑合成答案。
注意抽的不总是「选项字母」：

- `p08_abstention` — L1 = **4.9906**（策略 `coin_flip`）。⚠ headline score_10 = 10×(弃答recall + 可答作答率)/2 —— 全弃答、全作答、抛硬币三种策略的期望值都恰好 5.0。这个指标对任何与题目无关的策略恒等于 5，必须单列说明。
- `ifeval` — L1 = **0.1183**（策略 `random_text`）。答案空间是自由文本，其均匀抽样就是随机 token，所以 L1 是能测的。⚠ 实测 random_text(0.118) 反而高于 generic_text(0.056)——纯形式约束（全小写、不许出现逗号、字数下限）乱码全中，而一段像样的中文/英文散文会违反，所以这里最强的「与题无关策略」就是乱码本身，L1 高于 L2。

其余模拟类的 L1 就是 `uniform_random` 策略本身，数值见主表。

### B. 推导——均匀抽样的期望可以证明，模拟只会添噪声

- `eduillustrate` — L1 = **0**：被测模型交付的是 Manim 代码，乱码不可能编译通过，8 个 0-5 Likert 维度全部记 0。刻度下限与随机期望在这里重合，不必实测
- `longtutor_teaching` — L1 = **1**：四维 1-5 量表的刻度下限。judge prompt 明确写 “Score from 1 to 5”，score() 又把每维 clamp 进 [1,5]，所以乱码最低也只能落在 1.0（归一后为 0）。实跑约 3.9。⚠ 旧 headline 是 accuracy，那是 all(scores.values())——只有 judge 的 JSON 解析失败才记 0，乱码同样拿 1.0 满分；1001 题里唯一那次失败是 judge 把 appropriateness 拼成了 appropriance。聚合管线取的一直是 judge_scores，未受影响
- `mathtutorbench_mistake_correction` — L1 = **0**：答案是任意实数或 LaTeX 表达式，在其上均匀抽样命中 gold 的概率测度为 0。prior_random（按数据集答案分布猜）是更强的替代策略，不是 L1。
- `mathtutorbench_pedagogy` — L1 = **0.5**：答案空间是「二选一」而不是自由文本：随机 judge 有一半概率选中被测回复，位置交换两轮取平均后 win_score 期望 = 0.5
- `mathtutorbench_pedagogy_hard` — L1 = **0.5**：答案空间是「二选一」而不是自由文本：随机 judge 有一半概率选中被测回复，位置交换两轮取平均后 win_score 期望 = 0.5
- `mathtutorbench_problem_solving` — L1 = **0**：答案是任意实数或 LaTeX 表达式，在其上均匀抽样命中 gold 的概率测度为 0。prior_random（按数据集答案分布猜）是更强的替代策略，不是 L1。
- `mathtutorbench_scaffolding` — L1 = **0.5**：答案空间是「二选一」而不是自由文本：随机 judge 有一半概率选中被测回复，位置交换两轮取平均后 win_score 期望 = 0.5
- `mathtutorbench_scaffolding_hard` — L1 = **0.5**：答案空间是「二选一」而不是自由文本：随机 judge 有一半概率选中被测回复，位置交换两轮取平均后 win_score 期望 = 0.5
- `mathtutorbench_socratic` — L1 = **0**：与参考问句的 sentence-BLEU，随机文本的期望 ≈ 0
- `olympiadbench` — L1 = **0**：答案是任意实数或 LaTeX 表达式，在其上均匀抽样命中 gold 的概率测度为 0。prior_random（按数据集答案分布猜）是更强的替代策略，不是 L1。
- `sas_bench` — L1 = **0**：QWK/CCS/ECS 都是 chance-corrected 一致性统计量，随机评分的期望恒为 0

这一类里 `mathtutorbench` 的四个成对比较任务最容易读错：**0.5 既是随机地板也是人类锚**，
含义是「与专家教师打平」，低于 0.5 才说明比金标教师差。

### C. 实测——生成任务的均匀抽样就是乱码，只能喂给真实 judge

模型要写一段话，不存在「选项」可以抽，但答案空间仍然是 token 序列，
在它上面均匀抽样就是乱码。所以这类的 L1 = L3 的 **`random`** 变体，是同一个数。

两个例外不必实测，标 `(推导)`：`eduillustrate` 交付的是 Manim 代码，乱码编译不过，
八个维度全 0；`longtutor_teaching` 的 headline 是解析成功率，乱码同样拿 1.0。

两点要注意：

1. **不是所有都归零。** 打分量表自带下限，乱码也拿得到。EduBench 是 1-10 量表，
   下限就是 **1.0**；拿模型的 8.0 直接当「比 0 高 8 分」会把差距高估整整一分。
2. **有一个理论上可以为负。** TutorBench 的 rubric 含 −5 权重项，所以刻度下限无法先验给出。
   实测乱码是 **+2.54**——judge 并没有触发那些扣分项，乱码只是拿不到分，不是被扣分。

| benchmark | L1（乱码实测） | 刻度下限 | 说明 |
|---|---|---|---|
| `bea2025_tutor` | 0 | 0 | 生成 + 固定 judge 打 4 维标签，同上 |
| `edubench` | 1 | 1 | 12 维 1-10 量表由固定 judge 打分。乱码的期望是刻度下限 1.0，不是 0 |
| `eduguard_adversarial` | 0 ⚠满分方向 | 需实测 | ⚠ 越狱攻击成功与否由内容决定，无 chance level；地板在另一头——全部拒答 = ASR 0 = 满分。乱码既非越狱成功也非合格拒答，落点只能实测 |
| `eduillustrate` | 0 (推导) | 0 | 8 维 0-5 Likert 由 judge 打分；独立管线（scripts/eval/build_eduillustrate_report.py），不在 adapter 注册表里 |
| `k12vista` | 0 | 0 | 逐空 0/1 由 judge 判定；其中的选择题子集会给随机作答少量命中 |
| `longtutor_evidence` | 0 | 0 | judge 判语义等价 CORRECT/INCORRECT，乱码必判 INCORRECT |
| `longtutor_teaching` | 1 (推导) | 1 | judge 打 4 维 1-5 分，刻度下限 1（归一时按 (raw−1)/4 扣掉）。⚠ 不要用它的 accuracy：那只是「四个分数都成功解析且非 0」，实跑 0.999-1.000，1001 题里唯一那次失败是 judge 把 appropriateness 拼成了 appropriance |
| `mmtutorbench` | 0 | 0 | 6 个二元 rubric 由固定 judge 打分，全 0 即 0/6 |
| `mrbench_tutor` | 0 | 0 | 生成 + 固定 judge 打 8 维标签，pass 要求三个关键维度全 Yes |
| `tutorbench` | 2.54 | 需实测 | 加权 rubric（critical +5 / not_critical +1 / critical_negative −5），ARR_w 理论上可为负，所以刻度下限无法先验给出，只能实测。实测乱码落在 +2.54：judge 并没有触发那些 −5 的 critical_negative 项，乱码只是拿不到分而不是被扣分 |

### D. 唯一真的没有 L1 的

- `mmtutorbench_judge_calibration` — 无公开人类金标，adapter 本身不产出题目，没有可抽样的答案空间

### E. 反过来的两个

- `mooccube_prereq` — 唯一自带 chance correction 的 benchmark，
  随机作答的 `score_10` 已经被扣到接近 0，不存在比它更高的平凡策略，所以 L2 空着。
- `ifeval` — **L1 高于 L2**：乱码（0.118）比一段像样的散文（0.056）更能满足
  「全小写 / 不许出现逗号 / 字数下限」这类纯形式约束。这里最强的与题无关策略就是乱码本身。

## 未覆盖 / 待办

- `eduguard_adversarial` 的退化四件套只跑了 1/4，缺 `refusal`、`echo`、`generic`。
- `k12vista` 的退化四件套只跑了 1/4，缺 `refusal`、`echo`、`generic`。
- `longtutor_evidence` 的退化四件套只跑了 1/4，缺 `refusal`、`echo`、`generic`。
- `tutorbench` 的退化四件套只跑了 1/4，缺 `refusal`、`echo`、`generic`。
- L3 的每个变体默认只跑 40 题（`--limit`），是量级参考而非精确值。
- 本报告**不改**聚合脚本的归一化。给 P01–P20 做 chance correction 会让分数与 R25 不可比，
  那是独立决策；`benchmark_baselines_v1.json` 的字段已为此留好接口。

