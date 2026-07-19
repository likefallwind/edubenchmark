# 逐 P 复核待落地裁决清单（2026-07-19 起）

工作方式：每个 P 逐格讨论 → 裁决当场记入本文件（精确到格子名与权重）→ 用户发话后一批落地（改 `data/mapping_measurement_model_v6.json` + 聚合脚本 + final 文档记 R2x + snapshot + 重跑管线 + diff 披露）。

已落地：R20（P01）、R21（P02，单独落地）、R22（P03–P07 + 缺测替代机制，本文件下方各节，落地于 2026-07-19，见 final 文档 R22 记录与快照 `_v6r21_snapshot_20260719`）。

## 已落地裁决（R22，2026-07-19 落地完毕）

### P03 多模态理解（2026-07-19 裁决）

1. **facet1 olympiadbench 格：改取多模态子集 + 降相关度，不删**（用户裁决）。
   - 取数从 `summary.accuracy` 改为 `by_bucket.modality.MM.accuracy`（M3 0.681 / dsv4-pro 0.658），subdimension 改名如 `multimodal-subset accuracy`。
   - 相关度 0.2 → **0.1**（建议值，落地前可否）。依据：盲测对照——deepseek-v4-pro 走 gateway 看不见图，MM 子集仍拿 0.658，只比明眼 M3 低 0.023，视觉信号在分数里极弱。
   - 附带：deepseek-v4-pro 该格建议作废（盲跑废分；作废后 dsv4 无 P03 分）——**待用户落地前确认**。
   - P04（0.25）/P05（0.55）的 olympiadbench 挂载不动。
2. **k12vista 按学科拆两格**（用户裁决同意）：math-g6/g9/g12（158/598，解题图）→ facet1 problem_images，相关度建议 **0.35**；理化生地（440/598，装置/地图/图表）→ facet2 subject_charts，维持 **0.55**。置信 0.8 两格沿用。实现注记：需确认 k12vista summary 的 by_bucket.subject 是否带分桶均分，否则从 scored.jsonl 重算。仅动 P03 的格；P04/P05 的 k12vista 整体挂载不动。
   - mathvista **维持整体挂 facet1 + 注记**：FQA(27%) 属 facet2 内容但 TQA/VQA(33%) 两 facet 都无家，硬拆制造新边界纠纷；单模型面拆了无收益，记 TODO。
3. **tutorbench 置信 1.0 → 0.8**（用户裁决）：代理性质（分数混教学回复质量方差）+ 模型面与主面板不重叠，1.0 不自洽。
4. 其余不动：mmtutorbench 0.3×0.9、视频/音频空 facet（coverage_gap）。

### P04 知识调用与掌握（2026-07-19 裁决完毕）

1. **mmlu_pro / ceval 置信度整体调高**（用户裁决；置信是 benchmark 级全局参数）：0.35 → **0.7**（建议值，落地前可否）。理由：精确匹配判分最硬，却被压到低于裁判天花板分的 edubench（0.8），倒挂；R20 废四档的同一逻辑。影响面：P04 学科知识（rel 0.6/0.6）与 P05 推理（rel 0.3/0.25）两处，方向一致可接受。agieval（0.4，同族）是否跟调，留到 P05 讨论时一起裁。
2. **mooccube_prereq 从 P04 摘除**（用户裁决："和这个事情关系不大"）。主家 P14 core（0.7）与 P05（0.1）不动。附带效果：P04 的机会校正量表混入问题就地消失。
3. edubench 两知识指标：**留，相关度不动**（0.35/0.3；用户裁决 2026-07-19）。生成式知识测量正当（与 facet2 win-rate 四格同逻辑）；裁判天花板作为已知测量弱点注记，不折进权重。
4. mathvista / olympiadbench / k12vista 三个解题格：**留，权重不动**（0.2/0.25/0.15；用户裁决 2026-07-19）。
5. **facet2 死格 bug 修复**（无争议项，落地时做）：聚合脚本补 pedagogy_benchmark 取数分支，从 by_bucket.category 拆 CDPK / SEND 两行喂 1,119 题完整跑分（11 模型）；0701 聚合卡格子退役（同一 benchmark 同协议的旧快照，避免同信号双算）。
6. facet2 mathtutorbench 四个 win-rate 格：**全留，权重不动**（用户裁决 2026-07-19）。理由：Pedagogy IF 是教学法知识的生成式测量（执行指定教学法，不知道方法就执行不出来），与 facet 描述"判别式与生成式测量并用"一致，同 facet1 edubench 生成侧知识证据的逻辑平行；scaffolding± 匹配稍弱但脚手架属教学法核心概念，0.15 低权合理。

### P05 推理与生成（2026-07-19 裁决中）

1. **mooccube_prereq 从 P05 摘除**（用户裁决，采纳建议）：构念沾边（排序推理）但有效权重仅 0.07、机会校正量表与 facet 不同族、拖低覆盖模型。摘后 mooccube 仅剩主家 P14 core（0.7）。
2. **agieval 置信 0.4 → 0.7**（用户裁决，采纳建议）：与 mmlu/ceval 同族（考试 MCQ、精确匹配、官方解析），跟随同一档。影响面：P04 学科知识（rel 0.35）+ P05 解题推理（rel 0.45）。
3. **olympiadbench 置信 0.55 → 0.7**（用户裁决 2026-07-19）：全 facet 唯一未饱和（7.2–7.4，余格 8.3–9.8 天花板）、真正承担区分度的解题证据，不应压最低档；污染风险低于 mmlu。影响面：P04（rel 0.25）+ P05（rel 0.55）+ P03 facet1（rel 待落地改 0.1、取数改 MM 子集）。
4. sas_bench ECS 的 glm-5.2 异常（3.79）：**排查完毕，非 bug，分数保留**。QWK/CCS 正常，无解析失败；异常来自真实行为——glm-5.2 从不贴"步骤正确"（物理/地理均 0 次，glm-5.1 为 180/85 次）、物理题几乎不用金标第一高频错因"忽略特殊情况或近似假设"（3 vs 122）、滥用"回答不完整"。ECS 测的就是错因分布与人类的一致性，如实反映。注记：任务级 ECS 只有 5–7 个错因可排，Spearman 噪声大，负值≈零相关放大，任务级数字勿过度解读。
5. facet2（生成与归因推理）其余格子：无异议，维持。

### P05 裁决完毕（2026-07-19）

### P06 自我校验与修正（2026-07-19 裁决中）

1. **mathtutorbench_problem_solving 从 P06 摘除**（用户裁决）："解题强"与"会复查自己"无构念链，有效权重 0.045 天花板尾巴。主家 P04（0.3）/P05（0.6）不动。
2. **benchmark 改名（全局重构，暂记不动手）**：p07_selfcheck / p08_calibration（及同族 p08_abstention）沿用旧 P 编号起名，R20 编号迁移后名不符实（自查现在是 P06、校准弃答是 P07）。用户裁决：去掉 pXX 前缀改中性名（如 selfcheck / calibration / abstention），免得再改编号又失联。涉及：adapter 注册名、reports/eval/ 目录名、映射 JSON benchmark_id、聚合脚本、item_list 路径、历史文档引用——动静大，**单独找时机做，不并入本批映射落地**。
3. deepseek-v4-flash 的 P06 虚高（8.77，无直接测量）：由下面第 4 条的全局机制解决；flash 的 p07_selfcheck 长期仍应补跑（个案治疗）。
4. **缺测处理机制（全局聚合算法改动，用户裁决 2026-07-19）**：
   - 缺格**取该格已测模型中的最低分临时替代**（min-imputation，保守下界），并**显著标注**"未测·替代值"（逐格 `imputed` 标记 + P 级替代权重占比，09 产物与 HTML 同步）；
   - 边界（建议默认，用户可否）：格子已测模型 **≥3 面才参与替代**（1–2 面的 min 无意义甚至虚高，如 mathvista 单面 8.41），不足者对未测模型保持缺失、只计入未测标注；替代仅对**发布面板模型**做，顺路导入的外围模型（tutorbench 的 Qwen3.5 系等）不铺替代行；
   - 长期以补齐测试为正解，替代是过渡；
   - 这是算法改动，落地时在 R22 单独披露替代前后全 P 分数 diff。
   - 注：此机制取代此前讨论过的"覆盖率门槛不发布"方案（弃用）。

### P07 置信度校准与弃答（2026-07-19 零改动过审）

全部自建直接测量、三格同一 5 模型面、facet 边界可判不重复；p07_selfcheck 副挂 0.15 构念链成立保留；弃答 facet 单源+偏高（8.6–9.1）记区分度观察注记。

## 待落地裁决（R23 批次）

### P08 工具使用与长程智能体执行（2026-07-19 零改动过审）

领域空白：两个空 facet（工具调用/长程执行，R19 拆分显式呈现缺口）、零格子零证据，维持"暂未覆盖"声明。

### P09 错误诊断（2026-07-19 裁决完毕）

1. **edubench · error_identification_correction_accuracy 置信 override 0.8→0.3**（用户裁决选 C 折中；机制参照 QG/TMG 的 0.75 override 先例，加 `benchmark_weight_overrides` 条目）。依据：M2 换裁判实验 ρ≤0.14、三裁判均分 4.6/7.4/8.7，全仓库噪声最实锤的格；跨模型排序与其他错误诊断格全部拧着（M2.7 9.35 vs M3 5.99）。R14"12 维全可挂"原则形式保留（格不删、注记在位），噪声实质失去话语权（有效权重 0.2→0.075，降为尾部证据）。
2. 其余格子零改动：facet a/b 干净；facet c 的 ECS 锚 + bea/mrbench MI + mistake_correction + longtutor_diagnosis 副挂结构维持。

### P10 主观题评价能力（2026-07-19 零改动过审）

三 facet（整体性/分析式/生成 rubric 空白）结构与格子全部维持；asap_2/sas QWK 在此为主家构念对口。附带：**asap_2 补跑 minimax-m3 / glm-5.2 / doubao 记入遗留补测清单**（当前三者拿替代值 4.73，补跑后自动覆盖；harness colleague 变体与导入面可比；注意 CLAUDE.md 的导入目录覆写陷阱，用 `--out-dir` 或补跑后核对）。

### P12 学习者画像建模（2026-07-19 裁决完毕）

1. **pedagogy_benchmark · SEND 在 P12d 相关度 0.35→0.25**（用户裁决选 B）：SEND 是教师考试选择题，测"知道特教需求知识"；P12d 构念是"判断学生需要哪类支持"——知识侧证据挂行为侧构念，降一档并注记知识代理。知识主家 P04 不动。
2. 其余零改动：P12a longtutor_diagnosis 0.3（方法学注记扎实，低分是真实发现）；P12b/c 空白声明；P12d edubench personalized_adaptation 0.3。
3. 附注：R22 补丁（canonical_model 归一 doubao-seed-2-0-pro-260215）后 SEND 格 13 个真实面。

### P11 命题与作业设计（2026-07-19 裁决：采纳 B）

1. **新增格**：item_generation facet 加 `edubench · QG × domain_knowledge + basic_factual (task×metric)` 复合，rel **0.3**、置信沿用 QG override **0.75**——用现成裁判数据把"生成题目的内容正确性"从零覆盖变部分覆盖（裁判逐题核对学科内容对错；知识维度偏天花板 7.8–9.9，注记保留）。实现：`build_edubench_metric_summaries.py` COMPOSITES 加 `qg_correctness_composite`（QG 任务上 domain_knowledge_accuracy + basic_factual_accuracy 均值）→ 聚合脚本 metric 行 + 映射格。facet 描述"正确性效度无格子"降级为"部分覆盖（表达+内容正确性；测评学效度仍无）"。
2. 现有 QG 表达复合格维持 0.4×0.75；难度对齐空 facet 维持。

### P13 个性化教学策略选择（2026-07-19 裁决完毕）

1. **facet2 相关度上调**（用户裁决："给低了"）：CDPK 0.35→**0.6**、SEND 0.3→**0.4**。声明层归位（CDPK 是本 facet 构念最贴的直接测量，不该低于 facet3 的 BLEU 格）；facet 内只有两格，分数仅受比例影响，实际不变。
2. **mathtutorbench_socratic 相关度 0.65→0.4**（用户裁决）：BLEU 对参考问句判分，方差里"引导质量"与"措辞相似"不可分（置信 0.6 已折价，但 0.65 rel 仍居 facet 前三）；降后由语义鲁棒的胜率格主导执行 facet。
3. 其余零改动：facet1 空白声明维持；facet3 另 11 格（MathTutorBench 4 胜率格、EduBench 2、TutorBench、MRBench/BEA Providing_Guidance、MMTutorBench、LongTutor teaching）维持；bea/mrbench 近天花板与 TutorBench 替代依赖作注记。

## 讨论中 / 未裁决

- P14 学习路径规划（下一个）
