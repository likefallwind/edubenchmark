# Benchmark Todo

Record benchmark and measurement gaps discovered while using `edubenchassistant`.

Each entry should name the scenario, product reason, suggested data/eval design, related capabilities, and source report. Avoid duplicating an existing gap unless the new scenario changes the product requirement or evaluation design.

## 教育安全领域评测扫描 - 2026-05-20

- Gap: 中文本地化未成年人教育安全 benchmark 不足，尤其缺家校关系、校规、心理危机转介、学术诚信和本地政策语境。
  Product reason: 面向中文 K12 学生的 tutor、陪伴、作业反馈产品不能只依赖英文或通用 youth-safety benchmark 判定安全。
  Suggested data/eval: 构建中文多轮 red-team 集，按年龄段、风险类别、学校场景和转介动作标注；指标包括风险识别、拒答质量、转介质量、年龄适配和教育性替代建议。
  Related capabilities: D21, D24, D13; S7, S8
  Source report: reports/edubenchassistant/education-safety-benchmark-scan-evaluation.html

- Gap: 多轮长期使用中的情感依赖、边界侵犯、隐私披露和学生画像误用评测不足。
  Product reason: 学生安全风险常在连续互动中累积，单轮 ASR 或拒答测试会低估真实产品风险。
  Suggested data/eval: 设计多轮情景脚本、长期记忆/画像变体、延迟风险升级任务和人工审查 rubric；记录 unsafe turn rate、missed escalation rate、dependency reinforcement rate。
  Related capabilities: D21, D24, D15; S7, S8
  Source report: reports/edubenchassistant/education-safety-benchmark-scan-evaluation.html

- Gap: 产品级端到端安全事故率和人工介入效果缺少标准评测。
  Product reason: 公开 benchmark 多测模型回复，不能证明实际产品的 guardrail、教师复核、日志审计和危机升级链路有效。
  Suggested data/eval: 建立灰度发布安全监控集，统计风险命中率、误拒率、人工复核采纳率、升级响应时间、复发率和学生/教师反馈。
  Related capabilities: D24, D21; S7, S8
  Source report: reports/edubenchassistant/education-safety-benchmark-scan-evaluation.html

## RE_BENCHMARK_V1 research gaps - 2026-05-20

- Gap: TutorBench local download is incomplete and Pedagogy Benchmark is gated.
  Product reason: C2 tutoring and pedagogical-knowledge conclusions cannot rely only on EduBench proxies.
  Suggested data/eval: retry TutorBench parquet download; accept Pedagogy Benchmark HF terms; add rubric-based human review.
  Related capabilities: D12, D13, D14; S3.
  Source report: reports/re_benchmark_v1/RE_BENCHMARK_V1_RESEARCH_REPORT.md

- Gap: EdNet/ASSISTments are protocol datasets, not native LLM prompts.
  Product reason: personalization and knowledge tracing claims require KT metrics, not chat-model exact match.
  Suggested data/eval: download EdNet KT1 sample and define AUC/ACC/NLL protocol separately from LLM prompt runner.
  Related capabilities: D16, D17, D18; S5.
  Source report: reports/re_benchmark_v1/RE_BENCHMARK_V1_RESEARCH_REPORT.md

- Gap: Youth safety data for minors is incomplete locally.
  Product reason: education products serving minors need child/youth-specific safety checks beyond generic classroom safety.
  Suggested data/eval: acquire Safe-Child-LLM; monitor YouthSafe/YAIR, SproutBench, and CASTLE releases; build localized red-team set.
  Related capabilities: D21, D24; S7.
  Source report: reports/re_benchmark_v1/RE_BENCHMARK_V1_RESEARCH_REPORT.md

## Eval-framework adapter coverage - 2026-06-07

- Gap: OmniEduBench (C1/C3, D02/D04/D15) 暂无公开可下载数据，无法接入 per-benchmark 评测框架。
  Product reason: OmniEduBench 是 C1“是否覆盖全学科”和 C3 中文个性化培养维度的关键中文主测，缺它则中文教育知识/培养维度只能靠 EduBench 等代理。
  Suggested data/eval: 关注 mind-lab-ecnu.github.io/OmniEduBench、arXiv 2510.26422、OpenReview IeJ9ABgf3k 的数据发布；数据可得后按 `scripts/eval/benchmarks/<name>.py` 范式新增 `omniedubench` adapter（客观题 EM、开放/论述题 LLM-judge）。
  Related capabilities: D02, D04, D15; C1, C3.
  Source: re_benchmark_v1.md C1/C3；data/exhaustive_2026-05-13/dataset_acquisition.jsonl (status=manual_access_or_metadata_only)

- Note: 已接入 per-benchmark 框架的 C1 主测 = MathVista(D06)、MMLU-Pro(D01)、AGIEval(D03)、OlympiadBench(D05)。
  OlympiadBench 判分依赖官方 sympy 符号判分器，需 `antlr4-python3-runtime==4.11`（与 hydra/omegaconf 的 4.9 pin 冲突，建议在独立 venv 运行）。

## EduGuard-Bench 接入与数据质量发现 - 2026-06-12

- Note: 已接入 per-benchmark 框架的 C5 主测 = eduguard_sata(D21, P1 教学伤害 SATA, 规则评分) + eduguard_adversarial(D21, P2 对抗安全, 两阶段 LLM-judge BoN=3)。
  论文 judge DeepSeek-V3(BoN=9) 已下线，当前 judge 暂用 MiniMax-M3(BoN=3，同官方公开代码默认)；judge 经 `--extractor-model` 可替换。

## MathTutorBench 接入（C4 过程评分/反馈质量深测）- 2026-06-20

- Note: 已接入 per-benchmark 框架的 C4 主测 = MathTutorBench 全 9 任务（D11/D12/D13），来自 eth-lre/mathtutorbench (EMNLP 2025, arXiv 2502.18940) 本地克隆。
  数据物化：`python scripts/eval/data/fetch_eval_datasets.py --benchmark mathtutorbench`（stepverify 1002 / pref_test 482 来自 HF，gsm8k_main·gsm8k_socratic 1319 来自本地 parquet；scaffolding/pedagogy 用克隆内 `datasets/mathdial_bridge*.json`）。
  - 闭式任务（无 judge，官方判分移植到 stdlib）：`mathtutorbench_problem_solving`(GSM8K 精确匹配, gate)、`_socratic`(SacreBLEU)、`_solution_correctness`(Yes/No acc+P/R/F1)、`_mistake_location`(步骤号 F1 micro/macro/weighted)、`_mistake_correction`(数值 acc)。
  - 开放式教学任务（LLM-as-judge 成对 win-rate，替代官方需 GPU 的 1.5B 偏好奖励模型 `eth-nlped/Qwen2.5-1.5B-pedagogical-rewardmodel`）：`_scaffolding`/`_pedagogy`(+`_hard`)。裁判用官方 reward-model 评分准则，位置交换去偏（两序）；裁判默认 MiniMax-M3，经 `MATHTUTORBENCH_JUDGE_MODEL` 可换。
- Note: 裁判选择本身作为一项评测先行 = `mathtutorbench_judge_calibration`，被测模型即候选裁判（`--model`），用论文开源偏好集 `dmacjam/pedagogical-rewardmodel-data` 的 test(482 对专家 positive/negative) 衡量与人类偏好一致率；每对以 #ab/#ba 两序出题以暴露位置偏置，extra_metrics 给 agreement 与 position_consistency。一致率最高者作 win-rate 任务生产裁判。
  冒烟（n 小）：MiniMax-M3 calibration agreement≈0.70 / position_consistency≈0.40；mistake_location acc≈0.90(f1_micro=acc)；scaffolding(judge=M3) win_rate≈0.20。全量校准与各候选裁判对比、全任务跑分待执行。
- Gap: 官方 1.5B 偏好奖励模型路径（GPU + transformers + HF 权重）未接入；本仓库以 LLM-as-judge 等价替代，二者直接对比留作后续。socratic 任务需 `sacrebleu`（可选依赖）。

- Data-quality finding（已由上游修复）: 初版（commit 67f4355, 2025-10-13）`Dataset/SATAs.xlsx` 的 Answer 列与题目行错位（该列按 `Results/SATAs/*.xlsx` 的行序排列，1,333/2,635 题答案落在错误题目上；直接使用会使 RFS 失真，冒烟样本上 0.79 → 0.39）。
  Resolution: 上游 commit 432e8da（2026-06-08 "Fix SATAs answer labels"）已修复；本仓库独立发现该问题并从 13 个官方 Results 文件按 ID 多数投票重建答案键（`fetch_eval_datasets.py --benchmark eduguard_bench`），重建键与上游修复版 2,635/2,635 逐题一致，且可复现论文各模型 RFS（DeepSeek-V3 0.728/论文0.73、Claude3.7 0.772/论文0.77）。多数投票逻辑保留作为对官方文件的一致性校验（当前输出 "0 misaligned corrected"）。
  Related capabilities: D21; C5.
  Source: sources/datasets/eduguard_bench/（需 git pull 至 432e8da 之后）；reports/eval/eduguard_sata/

## Rebenchmark conclusion capability gaps - 2026-07-06

- Gap: v3.2 主榜雷达对 P08、P09、P10、P15、P16、P22 仍是弱覆盖或单一证据覆盖。
  Product reason: 当前 0701 主 benchmark 足以展示 SRG/FDR/LAD/CLM/CEG 的能力画像，但不足以支撑置信弃答、工具长程执行、多模态教学产物、学术诚信、学习者画像和安全处置的稳健主榜结论。
  Suggested data/eval: 把 EduIllustrate/EduVisBench、学术诚信真伪集、学习历史画像集、工具使用长程任务和本地化教育安全处置集先作为 MiniMax-M3 展示证据，完成 judge 校准后升级为多模型主评测；每个 LLM-as-Judge 任务记录 judge 模型、prompt hash、校准集、kappa/CI、分歧率和人工复核策略。
  Related capabilities: P08, P09, P10, P15, P16, P22; SRG/FDR/LAD/CLM/CEG
  Source report: tempt/rebenchmark-conclusion-plan-0706.html

## Benchmark portfolio priority triage - 2026-07-08

- Gap: 当前优先继续做的 benchmark 集中在多模态 tutor、脚手架/教学干预、特殊教育需求、教育安全处置质量和分维度教学法评测；这些方向比基础答题门槛项更能区分教育核心能力。
  Product reason: 如果继续把分析精力放在 MMLU/C-EVAL/AGIEval 等门槛项，会高估“会答题”对真实教育产品的解释力，并低估 P16/P17/P18/P22 等教育残余能力缺口。
  Suggested data/eval: 优先补齐 MMTutorBench、MathTutorBench scaffolding/hard、EduGuard refusal-quality、Pedagogy CDPK/SEND 分项和 TutorBench/BEA tutor 的多模型主跑；基础考试类保留为低频 gate。
  Related capabilities: P03, P05, P16, P17, P18, P20, P22; SRG/FDR/CLM/CEG
  Source report: reports/atomic_ability_rebenchmark_2026-07-08/12_benchmark_priority_report.html

## Construct review gap sweep - 2026-07-11

- Gap: ~~P01/P07~~ P02 是隐性覆盖缺口——现有格子全是别的任务顺带的搭车成分。【更新 2026-07-12：P01 已接 IFEval（adapter `ifeval`，规则判分）、P07 已接两轮自查（adapter `p07_selfcheck`），两者已进映射与测量模型，等批量跑分；**只剩 P02** 长材料证据定位无直接测量。】
  Product reason: 这三项是操作基座，产品方看到分数会以为可用；实际结论没有证据支撑。
  Suggested data/eval: P02 教育长材料任务需自建（课堂实录/课程多章节定位），先声明缺口。
  Related capabilities: P02; SRG
  Source report: doc/p_construct_review_2026-07-11.md, doc/benchmark_gap_recommendations_2026-07-11.md

## LongTutor 长历史个性化辅导 - 2026-07-13

- Note: 已按作者说明使用 `compute_history_stats.py` 顶部被注释的 XES3G5M concept-segmentation 逻辑，从 `sequences_long.jsonl` 和 `questions.jsonl` 重建 `history_features_lastq_scale.jsonl`；1,000 条输入与 `human_an_updated.jsonl` 的 1,000 条人工 gold 按稳定 `_key` 全量对齐。人工评测必须使用 `human_an_updated.jsonl`，不能误用自动生成的 `pipeline_an_scale.jsonl`。
- Note: 已接入 `longtutor_evidence`、`longtutor_diagnosis`、`longtutor_teaching` 和 `run_eval.sh`。MiniMax-M3 smoke（每任务 2 条）已完成；Evidence 语义 judge 与 Teaching 四维 judge 需要通过 `extraction_max_tokens()` 为推理模型保留足够输出 token。
- Gap: 尚未完成 MiniMax-M3 对 1,000 条人工样本的三任务全量评测，也未对 Evidence Semantic Accuracy judge 和 Teaching 四维 judge 做人工抽样校准。
  Product reason: 小样本 smoke 只能证明数据、模型调用、解析、评分和报告链路可运行，不能形成长历史证据获取、状态诊断和个性化教学能力结论。
  Suggested data/eval: 先扩大到分层样本，按 Information Extraction / Multi-session Reasoning / Hallucination Check 与四类 diagnosis 检查；人工复核 judge 一致性后再运行全量 1,000 条，并分别报告 Evidence accuracy、Diagnosis Macro-F1/accuracy、Teaching 四维分，不计算跨任务总平均。
  Related capabilities: D12, D13, D15, D16, D17; S3, S5
  Source: ACL 2026 LongTutor; `sources/datasets/longtutor/`; `reports/eval/longtutor_*/minimax3/`

- Gap: P16 学习者画像的分数只反映"支持需求判断"一个子能力；知识状态估计、误概念识别、参与度识别三个子能力无任何覆盖。~~P17 的苏格拉底式引导有本地分数（mathtutorbench_socratic）但未进映射~~【已完成 2026-07-12：socratic 全量判分 4 模型并补挂 P17/P18】。
  Product reason: 个性化教学产品的核心是画像，当前 P16 分数会严重高估画像能力覆盖面。
  Suggested data/eval: FoundationalASSIST 构造"读作答历史预测下一题"任务（P16a）；Eedi 误概念映射（P16b）；IntrEx 参与度判别（P16c）；socratic 补挂映射（P17a 的提问式干预测量来源，零成本）。
  Related capabilities: P16, P17, P19; CLM
  Source report: doc/p_construct_review_2026-07-11.md 第三节

- Gap: P19 学习路径规划只覆盖了"知识结构"一半——个性化路径（按学习者当前状态定制）仍是缺口。【更新 2026-07-13：**P19a 先修关系推理已接入** MOOCCube（adapter `mooccube_prereq`，905 条专家先修边当金标，200 道先修选择 + 100 道学习顺序排序，100% 规则判分零裁判；固定题单 `data/mooccube/item_list_v1.txt`；已进 MAPPINGS，权重待 R16 裁决）。P19 从"零覆盖"变成"部分覆盖"，**不得在报告里宣称 P19 已完整覆盖**。】
  Product reason: 先修图谱测的是"课程设计者视角的静态知识依赖"，产品里真正要的是"这个学生现在该学什么"——两者不是一回事，混为一谈会高估个性化路径能力。
  Suggested data/eval: P19b 下一步练习推荐——用知识追踪日志（FoundationalASSIST / Junyi / PTADisc，与 P16a 共用数据）：读学生作答历史 → 推荐下一题 → 用该生实际表现验证；P19c 整体规划生成无现成数据，需 rubric + 裁判，成本高，缓。v2 测量模型建议把 P19 拆成 P19a（有测量）/ P19b（缺口）两个 facet。
  Related capabilities: P19, P16; CLM
  Source: doc/benchmark_profiles/mooccube.md; doc/benchmark_gap_recommendations_2026-07-11.md 第 P19 节

- Gap: P21 风险识别六类风险（自伤/霸凌/成人内容/违法/心理危机/依赖诱导）被 SATA 一个无类别标签的分数覆盖；教育场景心理危机对话安全是否有专门 benchmark 未调研。
  Product reason: 学生心理危机处置是安全合规的重点审查项，需要类别级证据。
  Suggested data/eval: 先对 SATA 2,635 题做 LLM 类别粗标+抽检（同时解锁 P20/21/22 独立证据）；调研心理健康对话安全 benchmark。
  Related capabilities: P20, P21, P22; CEG
  Source report: doc/p_construct_review_2026-07-11.md, doc/benchmark_gap_recommendations_2026-07-11.md

## R18 裁决随记(P17 重构 / P23 新设 / 教师协作) - 2026-07-16

- Gap: "与人类教师协作"裁决不进原子清单——多数成分现有 P 已覆盖(遵循教师方案 = P01×P17,该转交人类 = P22 的一种处置,向教师报告学情 = P16 输出侧,守住辅助定位 = P20);残余机制"教师主导工作流中理解教师意图、不越俎代庖"仅有人机协同教学(co-orchestration)一类理论依据,不满足拆分准入规则(至少两类 benchmark 无关依据)。
  Product reason: 教师侧 copilot(备课、批改、学情分析)是主流落地场景;若将来教师标准把人机协作单列,或出现专门评测,需重审是否设独立 P。
  Suggested data/eval: 关注 teacher-AI co-orchestration 方向评测;场景层报告用现有 P 组合出分,不在原子层虚报覆盖。
  Related capabilities: P01, P16, P17, P20, P22; CLM/CEG
  Source: doc/atomic_ability_mapping_final_2026-07-15.md 裁决记录 R18

- Gap: P17 新增"教学目标对齐"facet 空白——没有任何格子测"教学行为是否服务于课标/教学目标"(longtutor_teaching 的 strategy_alignment 锚的是学生状态/历史,不是目标)。
  Product reason: 课堂/校内产品必须对齐课标,只测"对学生个性化"会漏掉"教偏了方向"这类失败。
  Suggested data/eval: 自建协议——给定教学目标+学情,判断教学回复是否服务目标;或寻找含课标/目标标注的教案与教学对话数据。
  Related capabilities: P17; CLM
  Source: doc/atomic_ability_mapping_final_2026-07-15.md 裁决记录 R18

- Gap: P23 测评设计与出题(R18 新设)——现仅 edubench QG 的表达质量指标(清晰启发/情景元素),测评效度(答案唯一正确、难度定标、干扰项对应真实误概念、对齐考查目标)零覆盖;生成 rubric facet(自 P14 迁入)仍空白。
  Product reason: 出题/组卷是教师侧高频功能;表达流畅但效度差的题(答案歧义、干扰项无效)对产品是隐性风险,当前分数完全测不出来。
  Suggested data/eval: Eedi 干扰项-误概念数据(与 P16b 候选同源)测干扰项设计;答案正确性可自建规则协议(生成题自答一致性校验);rubric 生成需自建对专家 rubric 的一致性协议。
  Related capabilities: P23, P14, P16; LAD
  Source: doc/atomic_ability_mapping_final_2026-07-15.md 裁决记录 R18

## R19 裁决随记(facet 划分全面复审) - 2026-07-17

- Gap: P09 拆两空 facet 后缺口更具体——"工具选择、调用与结果整合"与"长程计划、状态保持与失败恢复"均无任何挂载。
  Product reason: 教育 agent(自动批改流水线、跨会话学习管家)两种失败机制独立:会调工具不代表撑得过长程状态维护,反之亦然。
  Suggested data/eval: 工具侧可从"调用计算器/画图/检索课程库完成辅导"自建小规模任务起步;长程侧关注跨会话教育 agent 评测,通用 GAIA/tau-bench 类只能当门槛证据。
  Related capabilities: P09; FDR
  Source: doc/atomic_ability_mapping_final_2026-07-15.md 裁决记录 R19

- Gap: P10 新拆"时序与交互式教学产物生成"facet 空白——音频讲解、视频/动画、交互式演示与仿真生成无任何评测。
  Product reason: 语言学习、实验演示、数字课程的核心产物形态;静态图示(eduillustrate)分数替代不了。
  Suggested data/eval: InteractScience(生成带交互控件的科学教学网页)是最近候选;教学视频/动画生成基准待社区。
  Related capabilities: P10; FDR
  Source: doc/atomic_ability_mapping_final_2026-07-15.md 裁决记录 R19

- Gap: P14(R19 改名"主观题评价能力")分析式评分 facet 计分单源(仅 sas_bench·CCS;bea/mrbench_judge 暂不计分)+ 生成 rubric facet 空白(自 P23 迁回)。
  Product reason: 分析式/步骤级评分是过程性评价的基础;rubric 生成决定主观任务能否被一致透明地评分。
  Suggested data/eval: judge 校准研究结论落地后激活 bea/mrbench_judge 一致性分即转多源;rubric 生成需自建对专家 rubric 的一致性协议。
  Related capabilities: P14; LAD
  Source: doc/atomic_ability_mapping_final_2026-07-15.md 裁决记录 R19

- Gap: P21 改轴后独立证据为零——"风险信号识别"仅剩与 P20/P22 同源的 SATA 一格(原 ASR 格构念不匹配已删),"风险严重度与紧迫性判断"facet 空白。
  Product reason: 严重度分级(立即干预/短期关注/一般支持)直接决定处置路径,是安全系统的门槛环节;"看见风险"和"判断多紧急"可独立失败。
  Suggested data/eval: 需含严重度分级标注的学生风险对话数据;R10 的 SATA 类别标注可先解三 P 同源问题。
  Related capabilities: P21, P20, P22; CEG
  Source: doc/atomic_ability_mapping_final_2026-07-15.md 裁决记录 R19

- Gap: P22 升级转介深度缺口(两 facet 内,非新 facet)——知识侧部分覆盖但不可计量(转介选项散在 SATA 心理健康类题正确答案里,无类别标签),行为侧零覆盖(拒答质量三档无转介维度,场景全为主动越狱,无"被动流露风险需主动升级"情形)。
  Product reason: 高风险场景"优雅拒答但没做转介"按现有评分拿满分,真正救命的动作测不到。
  Suggested data/eval: SATA 类别标注(R10)时顺带标"正确答案含转介"子集单独取分;adversarial 侧扩"高严重度需升级"场景并给拒答质量加转介统计维度。
  Related capabilities: P22, P21; CEG
  Source: doc/atomic_ability_mapping_final_2026-07-15.md 裁决记录 R19

- Gap: P23(R19 改名"命题与作业设计")新拆"难度与目标对齐"facet 空白——难度定标、区分度、对齐课标/考查目标无任何格子;题目正确性效度也仍零覆盖(现有 QG 格只测表达质量)。
  Product reason: 组卷产品的核心是难度和考查目标匹配,不是题目写得通顺。
  Suggested data/eval: Eedi 干扰项-误概念数据测干扰项设计;难度定标可用真实作答通过率校验自建;目标对齐需含课标标注的题库。
  Related capabilities: P23; LAD
  Source: doc/atomic_ability_mapping_final_2026-07-15.md 裁决记录 R19
