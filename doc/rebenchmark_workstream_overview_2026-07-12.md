# Rebenchmark 效度工作线：来龙去脉与当前进度（2026-07-12）

这份文档是给"隔了几天回来看"的人写的总览：这条线在解决什么问题、每一步为什么做、发现了什么、现在到哪了、接下来需要你做什么。细节都在各自的专门文档里（文末有文档地图），这里只讲脉络。

## 一句话说清这条线

`reports/atomic_ability_rebenchmark_2026-07-08` 那份报告用 22 个原子能力（P01-P22）给模型画能力雷达图。你对它的客观性提出了怀疑。这条工作线做的事就一件：**把"每个 P 的分数为什么可信"变成可以检查的证据，查出来不可信的地方就修**。目标产物是映射表 v2（每个 benchmark 挂到哪个 P、权重多少，全部带数据依据）和一份带效度评级的报告。

## 起点：当时的三个怀疑（2026-07-11 定下计划）

1. **权重是拍的**。benchmark→P 的映射权重（比如 scaffolding 挂 P17 0.50）没有数据依据，改了也没人能说不对。
2. **分数挤在一起**。很多 benchmark 上所有模型都打 8.5+，排名基本是噪声，但雷达图照画。
3. **有些 P 看着有分，其实没测**。比如 P07"自我校验"，分数全是别的任务顺带算过来的（搭车），没有任何测验真的考过"自查"这个行为。

再加上 pilot 相关性分析的红旗：同一个 P 下的两个 benchmark，跨模型分数居然负相关（edubench × pedagogy_benchmark ρ=−0.90）——要么映射错了，要么分数本身不可靠。

## 做了什么、每一步为什么（时间顺序）

### 第一批：搭检查的架子（7-11）

| 做的事 | 为什么 |
|---|---|
| **预注册测量模型**（`data/mapping_measurement_model_v1.json`）：先声明每个 P 是"一个东西的多个指标"（reflective）还是"几块拼成的"（formative 含 facet） | 防止看完数据再编结构自圆其说。声明在先，数据只用来检验 |
| **13 号检查**（`scripts/build_mapping_validation.py`）：每个格子算区分度，每对同 P 的 benchmark 算跨模型相关，给评级 | 把"权重是拍的"变成"每个格子有 validated/flagged/受限 的标签" |
| **P08 自建两件套**（置信度校准 + 弃答） | P08 当时完全无覆盖，而"自信地教错"是教育产品最致命的失效模式，零标注就能测 |

首轮结果：**16/29 有证据的格子分数拉不开（天花板）**——这比映射错配更严重，是当前最大的问题；可裁决配对里 0 个 validated。

### 第二批：构念层面的核对（7-11，起因是你提的三个问题）

| 你提的问题 | 对应做的事 |
|---|---|
| "原子能力还是太粗，P 一样但实际差很远的 benchmark 被混在一起" | **逐 P 构念核对**（`doc/p_construct_review_2026-07-11.md`）：18 个有映射的 P，逐格子对照"P 的定义"和"benchmark 实际测的维度"，给出一致/搭车/不该挂的判断 → 修改建议 R1-R10 |
| "有些原子能力其实可以再拆，比如学习者画像" | **子能力细分**：P16 拆 4 个子能力（发现现有分数只测了其中 1 个）、P18 拆 4、P17 拆 2 |
| "拆分不能靠 benchmark，会被带偏" | **拆分准入规则**：四个 benchmark 无关的依据来源（理论/失败机制/人类教师标准/同源数据），至少两个支持才拆；benchmark 的存在永远不算依据。按这个规则回检，砍掉了我自己提的两个拆分（P17b 苏格拉底提问就是被 mathtutorbench 带偏的实例） |
| "每个 benchmark 调研不够深" | **17+2 份 benchmark 档案**（`doc/benchmark_profiles/`）+ **缺口推荐**（`doc/benchmark_gap_recommendations_2026-07-11.md`，每个缺口给候选数据和接入成本） |

### 第三批：edubench 原始数据到位后（7-12，就是这两天）

你从同事那里拿到了 edubench 完整跑分（11 模型 × 3,797 题，每题 12 个裁判指标的分数）。这批数据值钱的地方：**同一批回答、同一个裁判，指标之间的关系不受"不同 benchmark 方法不同"的干扰**——之前只能拿 11 个模型级的点算相关，现在每个模型有 3,797 个题级的点。

| 做的事 | 为什么 | 结论 |
|---|---|---|
| **逐题级指标分析**（`reports/eval/edubench/_analysis/`） | 验证之前模型级矩阵的结论靠不靠得住 | "答得准"和"教得好"题内零相关——**"会答题≠会教"最硬的证据**；但也发现"错误识别"指标区分度大得可疑 |
| **M2 换裁判实验**（`reports/eval/edubench/_judge_swap/`）：抽 250 条回答，换两个裁判重判 | 分数差异可能是"测的东西真不同"，也可能是"裁判乱打分"。不换裁判分不清这两者，之前所有 edubench 结论都悬着 | **按指标二分**：个性化/动机/高阶思维三个指标换裁判后依然一致（真测量）；"错误识别"三个裁判各判各的（纯裁判噪声，不能用）；知识类指标被打到天花板（只能当门槛） |
| **缺口前三项执行**：socratic 补挂（R11）、P07 两轮自查 adapter、IFEval adapter | 这三个是"零/低成本就能把'看着有分其实没测'变成'有直接测量'"的动作，之前已批准不必等其他里程碑 | 三个都接通冒烟了，等批量跑分出全量分数 |

## 如果只记五条结论

1. **天花板是最大的问题**：一半以上的格子分数拉不开，比映射错配严重。解法是补模型数（M2.5）和换更难的题，不是改权重。
2. **"会答题≠会教"从口号变成了证据**：同一批回答里，事实准确性与个性化/动机引导/高阶思维的相关约等于零。这是整个仓库核心命题目前最硬的一条支撑。
3. **LLM 裁判的分数要按指标甄别，不能整体信或整体不信**：edubench 12 个指标里只有支持簇 3 个跨裁判稳健；"错误识别"看着区分度最大，实际是裁判噪声——不做换裁判实验就会把噪声当成宝贝挂进映射。
4. **"有分"不等于"测过"**：P01/P02/P07 的分数全是搭车来的；P16 的分数只反映 4 个子能力中的 1 个。P01/P07 的直接测量这两天已经补上（IFEval、两轮自查），P02 还空着。
5. **映射 v2 的方向定了**：从"benchmark → P"改成"（任务 × 指标）→ 子能力 → P"两级。数据支持：按格子挂的区分度比按 benchmark 挂好一个量级（60 格里 52 格跨模型 SD≥0.3，对比 benchmark 级 16/29 受限）。

## 当前状态（里程碑）

| 里程碑 | 内容 | 状态 |
|---|---|---|
| M0/M1 | 测量模型声明 + 13 号检查跑通 | 已完成 7-11 |
| M1.5/M1.6 | 逐 P 构念核对 + 子能力细分 + 档案与缺口推荐 | 已完成 7-11 |
| M2 | 换裁判重判实验 | 已完成 7-12 |
| 缺口前三项 | socratic 补挂 / P07 自查 / IFEval | 已完成 7-12（等全量跑分） |
| 新四件全量首跑 | MiniMax-M3 × ifeval/p07_selfcheck/p08_calibration/p08_abstention | 已完成 7-12 晚（分数见下） |
| **M2.5** | 全量补到 5 个主力模型（10+ 模型走 200 题抽样档） | **剩 4 个模型等你启动** |
| **M3** | 人工裁决 R1-R14 → 映射表 v2 | **等你，约半天（关键路径，越早越好）** |
| M4 | 用 v2 重新聚合，v1/v2 对比 + 排名稳定性 + 双报告 | 在 M3 后 |
| 发布 | **7 月底**（决策记录 12 条；必做清单见 roadmap 文档文首） | 已定 7-12 |

## 需要你做的两件事

> **发布目标已定：7 月底**（决策记录第 12 条）。专家盲评、污染审计等加固项全部暂缓到发布后；发布必做清单和排期见 `doc/roadmap_to_convincing_eval_2026-07-12.md` 文首。清单里新增两个接入：P04 走 K12Vista、P19 走 MOOCCube 先修推理；P09/P15 是真领域空白，报告里诚实标"暂未覆盖"。关键路径是 **M3 裁决（下面第 1 件）→ 映射 v2 → M4 双报告**，裁决越早做后面越松。

**1. M3 裁决**：R1-R14 逐条过一遍（每条在构念核对文档第二节有完整理由，这里只列一句话）：

| 编号 | 一句话 | 状态 |
|---|---|---|
| R1 | edubench 从"5 任务均分挂 P"改为"按原生指标挂 P"（经 R13/R14 收窄后：只挂个性化→P17c、动机→P18c、高阶思维→P18/P06 三个稳健指标） | 待裁决 |
| R2 | bea2025_tutor/mrbench_tutor 用逐维度分替换复合 pass rate | 待裁决 |
| R3 | P14 拆"学业作答评分/教学回复评判"两 facet | 待裁决 |
| R4 | P17 策略执行 facet 拆"对话辅导/内容个性化" | 待裁决 |
| R5 | P03 拆"解题图像/教学场景图文"，取消 eduillustrate 的 P03 挂载 | 待裁决 |
| R6 | mistake_correction 的 P13 权重 0.45 → 约 0.2 | 待裁决 |
| R7 | QG 类降权/移 P06；eduguard 拒答质量改挂 P22 为主 | 待裁决 |
| R8 | pedagogy_benchmark 移出 P06 | 待裁决 |
| R9 | P01/P02/P07 标 proxy_only | P01/P07 已补直接测量，仅剩 P02 |
| R10 | SATA 先做类别标注才能拆 CEG 三 P 的独立证据 | 待做（LLM 粗标 + 抽检） |
| R11 | socratic 补挂 P17 | **已执行 7-12** |
| R12 | 测量模型 v2 按"子能力声明"重写 | 随 M3 一起 |
| R13 | edubench"指令遵循"指标不作 P01 直接测量（P01 走 IFEval） | 已定论（数据支持） |
| R14 | edubench"错误识别"指标不入映射（裁判噪声）；R1 收窄为支持簇三指标 | 已定论（M2 实验支持） |

**2. 启动批量跑分（M2.5）**：规模上限按你定的预算——**全量最多 5 个模型**（MiniMax-M3 / MiniMax-M2.7 / deepseek-v4-pro / glm-5.2 / doubao-seed-2.0-pro，按与现有分数的重叠度选），10+ 模型的扩展以后走 200 题固定抽样档。MiniMax-M3 已跑完（2026-07-12）：

| 测验 | 题数 | headline | 备注 |
|---|---|---|---|
| ifeval | 541 | prompt 严格准确率 0.874 | 规则判分，无裁判 |
| p07_selfcheck | 550×2 轮（520 题两轮齐） | score_10 5.27（改对率 0.098 / 改错率 0.044） | 与文献一致：改对率低是真实测量；30 题第二轮撞配额待扫尾 |
| p08_calibration | 550 | score_10 6.56（AUROC 0.638、90 分自信下错误率 0.33） | |
| p08_abstention | 500 | score_10 8.72（弃答召回 0.748、几乎不误弃） | |

剩 4 个模型的启动命令（注意 PATH 前缀要放在 nohup 里面，否则 ifeval 会因缺 absl/nltk 崩掉——7-12 已踩过一次）：

```bash
nohup bash -c 'for M in deepseek-v4-pro glm-5.2 doubao-seed-2.0-pro MiniMax-M2.7; do PATH=/home/likefallwind/miniconda3/bin:$PATH MODEL=$M CONCURRENCY=4 ./scripts/run_eval.sh ifeval p08_abstention p08_calibration p07_selfcheck; done' > eval/batch_4models.log 2>&1 &
```

跑完后重跑 `python scripts/build_atomic_ability_rebenchmark_artifacts.py && python scripts/build_mapping_validation.py` 让 P01/P07/P08 上图、13 号出配对。

## 文档地图（哪个文档管什么）

| 文档 | 管什么 | 什么时候看 |
|---|---|---|
| 本文档 | 来龙去脉总览 | 回来接续工作时 |
| `doc/atomic_ability_mapping_final_2026-07-15.md` | **映射定稿**：21 个 P 的最终清单 + 逐 P 挂载明细 + benchmark 索引（无历史沿革,拿来即用） | 查"某个 P 现在挂什么"时,以此为准 |
| `doc/benchmark_ability_mapping_v2_2026-07-15.md` | 映射 v2 **变化记录**：v1→v2 每格改了什么、依据哪条裁决 | 审查"为什么这样改"时 |
| `doc/roadmap_to_convincing_eval_2026-07-12.md` | 五问体检：离"真正有说服力"还差什么 + 性价比排序（专家盲评是分水岭） | 规划 M4 之后的方向时 |
| `doc/mapping_validation_plan_2026-07-11.md` | 效度验证的完整方法设计 + 里程碑 + 决策记录（1-11 条） | 想核对"为什么这么设计" |
| `doc/p_construct_review_2026-07-11.md` | 逐 P 核对表 + R1-R14 完整理由 + 拆分准入规则 + 三例数据依据 | M3 裁决时逐条对着看 |
| `doc/benchmark_gap_recommendations_2026-07-11.md` | 每个缺口的候选 benchmark 和接入成本，优先级表（含执行状态） | 决定下一个接什么数据 |
| `doc/benchmark_profiles/` | 每个 benchmark 一份档案（是什么、怎么判分、局限、当前映射） | 对某个 benchmark 有疑问时 |
| `doc/p08_calibration_eval_plan_2026-07-11.md` | P08 两件套的设计 | P08 分数解读时 |
| `reports/atomic_ability_rebenchmark_2026-07-08/13_mapping_validation.{md,html}` | 13 号检查的最新运行结果（格子评级） | 每次加了新跑分后重跑再看 |
| `reports/eval/edubench/_analysis/` 与 `_judge_swap/` | edubench 逐题分析和换裁判实验的数字 | 查 R13/R14 的原始证据 |

## 四个约定

这条线的每一步遵守四条纪律（前两条 7-11 定，后两条 7-12 你补充定下，完整表述见计划文档决策记录 10/11 条）：

1. **修改映射必须带数据依据**（配对 ρ/n/置信区间写进 revision_rationale）。
2. **结构声明先于数据**（测量模型、拆分规则都先写定再看数）。
3. **构念层与测量层分离**：P01-P22 清单不因"现在测不了"而修改——测不了是覆盖缺口，标出来当未来方向；只有 P 本身定义不合理才动它。之前"收敛成 7-9 个簇"的想法按此撤回，改为逐 P 测量成熟度分级（成熟/单源/代理/空白）。
4. **研究层与用户层分离**：加权和统计检验全部留在研究层不降级；用户版报告每个 P 只给一个分数 + 三档白话可信度（已验证/参考值/暂未覆盖）+ 产品语言解释。M4 交付两份报告而不是一份。


> **2026-07-14：M3 裁决单已就绪** —— `doc/m3_adjudication_sheet_2026-07-14.md`。A 组 5 条（原则已覆盖，默认执行）+ B 组 11 条（需逐条点头：R1-R8、R10 的权重与挂载，R15 K12Vista、R16 MOOCCube 的新权重）。裁完才能出映射 v2 → 双报告，是发布关键路径。

## 2026-07-15：裁判静默失败的根因修复 + 数据重判（回来先看这一节）

**背景**：7-14 的 `doc/eval_artifact_audit_2026-07-14.md` 审计发现 mrbench_tutor / bea2025_tutor / 4 个 mathtutorbench win-rate（scaffolding/pedagogy/±hard）的裁判缓存里，约一半的行是 "empty/unparsed" 却被当成"打了分的失败"混进分母——**这些正是 R2（bea/mrbench 逐维度分）依赖的数据**。7-15 把根因查清并修掉了：

**根因（不是配额限流，是 max_tokens 把 M3 饿死）**：`is_reasoning_model('MiniMax-M3')` 误返 False（它只认 `reasoning_effort` 参数，而 M3 不吃），于是判裁调用被 `extraction_max_tokens(model, 512)` 卡在 512 token；M3 是推理模型，512 token 全被 `reasoning_content` 吃光，`content` 返空 → 记成失败。判据：真配额限流时 client 会抛 `base_resp` 错误码，而这里是"空回复无错误码"。详见 memory `eval-no-max-tokens-cap-policy`。

**已修**：
1. **max_tokens 政策：所有模型默认不设上限**（`extraction_max_tokens` 恒返 `None`，`--max-tokens` 默认 None）。唯一例外 `deepseek-v3.2→32768`（网关硬性要求）。已写进 `CLAUDE.md` / `AGENTS.md`。
2. **裁判原文全部落盘**：mrbench_tutor / bea2025_tutor / mathtutorbench win-rate 三个适配器改为 `extract_answer` 存裁判**原文**、解析挪到 `score()`（与 longtutor 一致）——解析 bug 可 `--score-only` 白嫖重算,不再丢内容。
3. **取消 "unparsed" 中间态**：裁判结果只有两种——救回真 label，或 error（排除出分母、可重判），绝不再有"当假不及格"的第三态。已把历史 3789 行 limbo 迁移成 error（`scripts/eval/data/migrate_unparsed_to_error.py`）。
4. longtutor_teaching 的 4 维全 0 bug（`_json_from_text` 死代码）已修并重算，summary 现为真分。

**正在跑（可能已跑完）**：对发布 5 模型（MiniMax-M3/M2.7、deepseek-v4-pro、glm-5.2、doubao-seed-2.0-pro）的 25 个 `(benchmark×模型)` 对、约 2533 行 error 断点续判（裁判固定 MiniMax-M3，只补 error 行，predictions 不动）。已验证首对 `mathtutorbench_scaffolding_hard/MiniMax-M2.7` 327/327、0 error。
- **怎么确认跑完**：对这 6 个 benchmark 的发布模型目录，按 item_id 去重后数 `extractions.jsonl` 里带 `error` 的行（`grep -c` 会因追加重复虚高，必须去重）；全为 0 即完成。
- **没跑完怎么续**：`JUDGE_MODEL=MiniMax-M3 CONCURRENCY=4 MODEL=<模型> ./scripts/run_eval.sh <benchmark>`，逐对重跑即可（幂等续判）。

**对计划的影响**：重判跑完前，**不要采信当前 mrbench/bea/mathtutorbench 的分数**；跑完后这些是可信的逐维度数据，R2 才有干净输入。待办：①代码改动 commit（数据等重判完单独提）②重判跑完核对 error 归零 → `--score-only` 出分 ③恢复 M3 裁决（R1-R16）→ 映射 v2 → M4 双报告。

## 2026-07-15（下午）：M3 裁决全部完成，关键路径解锁

**M3 裁决 R1-R16 全部裁完**，最终口径见 `doc/m3_adjudication_sheet_2026-07-14.md` 文末"裁决结果"一节（多条与原提案不同，以那张表为准）。要点：

- **构念层三个大动作**：P03+P04 合并为「多模态理解」（P 清单 22→21，facet 按材料类型分）；P14 重定义为「主观题 rubric 评分能力」（三 facet，含空白的"生成 rubric"）；P19 定义澄清为知识结构层路径规划（学习者状态路径 = P16×P19 组合能力，不设 P19b）。
- **P17 策略执行不细分**（两版拆分方案议后均放弃）。
- **取分方式**：R2 执行（bea/mrbench 逐维度分，Actionability→P18 权重减半）；R1 按 12 维全用口径执行。
- **权重修正**：R6（mistake_correction P13 0.45→0.20）、R7 部分（仅拒答质量 P18 0.25→0.10，QG 不动）、R8（pedagogy_benchmark 移出 P06）执行。
- **新挂载**：R15 K12Vista（学科图表 facet 0.55）、R16 MOOCCube（P19 0.70）按裁决进 v2；longtutor 三任务挂载在 v2 草案中标"待确认"。

**里程碑状态更正**：M2.5 的 4 个补跑模型（ifeval/p07_selfcheck/p08_calibration/p08_abstention × M2.7/deepseek-v4-pro/glm-5.2/doubao-seed-2.0-pro）**已跑完**（上文"剩 4 个模型等你启动"已过时；M3 的结果在 `minimax3` 目录）。M3 裁决**已完成**。

**当前进行中/待办**（按依赖顺序）：
1. 裁判 error 行断点续判仍在跑（26 对进行到第 2 对，MiniMax 配额限流中会自动重试）。跑完前 mrbench/bea/mathtutorbench 分数继续不采信。
2. 重判完成后：核对 error 归零 → `--score-only` 出分；补 longtutor_teaching glm-5.2/minimax3 各缺的 1 条裁判缓存并重算 summary（当前两者仍是全 0 旧账，deepseek-v4-pro 已是真分）。
3. mrbench_tutor / bea2025_tutor 缺 deepseek-v4-pro、doubao-seed-2.0-pro 两个模型的**生成**（不只是重判）——R2 逐维度数据目前只有 3 个模型面，是否补跑待定。
4. 按裁决结果产出 `mapping_measurement_model_v2.json` + 映射 v2 → 重跑聚合 + 13 号检查 → v1/v2 对比 → M4 双报告。
