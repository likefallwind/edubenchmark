# Benchmark 语言与题型盘点（2026-10-21）

范围：当前进入 P01–P20 映射的 36 个 benchmark_id。未进映射的 k12bench、safe_child_llm、eduequity 和两个 judge_calibration 不计入。

## 统计口径

- **题量**：取该 benchmark 题量最大的已完成 run 的 `summary.json.total_items`。p07/p08 用的是固定题单（550 / 500 题），不是数据源全集。
- **语言**：调用各 adapter 的 `load_items` + `build_messages`，取发给模型的文本，按汉字占（汉字 + 英文单词）的比例判断：>0.5 记中文，<0.1 记英文，其余记混合（混合题占比 <1%，已并入多数语言）。p07/p08 用 run 的 `language` 桶；eduillustrate 不在本仓库 adapter 内，按其桶标签（中文题型/难度）记中文。
- **题型**：来自 adapter 的 `question_type` / `type` / `task` 桶；没有桶的按 adapter 判分代码归类。
- **判分方式**：按实际判分路径，与 R25 置信度规则同口径。LLM 只抽取答案、由规则比对金标的仍算规则判分。
- **分数区间**：`reports/atomic_ability_rebenchmark/13_mapping_validation_cells.jsonl` 中该 benchmark 主格子各模型的 0–10 最低至最高分。`*` 表示已知 prompt 泄露评分维度，分数虚高（见 `benchmark_baselines_2026-08-04.md`）。

统计脚本未入库（一次性分析），口径以本节为准。

## 总体

| 维度 | 结果 |
|---|---|
| 题量 | 95,655 题 |
| 语言（按题量） | 英文 75.6%，中文 24.4% |
| 语言（按 benchmark 数） | 纯英文 23 个，纯中文 8 个，中英双语 5 个 |
| 带图题 | 7.6%（olympiadbench、mathvista、k12vista、tutorbench、mmtutorbench） |
| 判分方式（按 benchmark 数） | 规则 21 个；LLM 裁判 14 个；BLEU 1 个 |
| 判分方式（按题量） | 规则 82.8%；LLM 裁判 16.3%；BLEU 1.4% |

### 题型（按题量）

| 题型 | 题量 | 占比 | 说明 |
|---|---:|---:|---|
| 打分/标注（模型当评卷人，对人类金标） | 34,674 | 36.2% | mrbench_judge、bea2025_judge、asap_2、sas_bench |
| 单选 | 22,300 | 23.3% | |
| 填空 / 短答案精确匹配 | 11,725 | 12.3% | 数值、表达式 |
| 开放生成 | 12,844 | 13.4% | 辅导回复、教学内容、对抗安全 |
| 多选 | 5,270 | 5.5% | eduguard_sata |
| 判断 / 分类 | 5,008 | 5.2% | 解答对错、错误步骤、学生状态四分类 |
| 简答（LLM 判对错） | 3,193 | 3.3% | k12vista 问答题、longtutor_evidence |
| 规则校验生成 | 541 | 0.6% | ifeval |
| 排序 | 100 | 0.1% | mooccube 学习顺序 |

### 按模型扮演的角色

| 角色 | benchmark 数 | 题量 | 中文占比 |
|---|---:|---:|---:|
| 考生（含教学法知识、安全知识选择题） | 9 | 36,686 | 36% |
| 通用（指令遵循） | 1 | 541 | 0% |
| 自建能力探针 | 4 | 1,900 | 43% |
| 老师判断学生作答 | 5 | 9,010 | 44% |
| 阅卷人 | 4 | 34,674 | 12% |
| 老师生成（辅导、讲解、教学内容） | 12 | 12,043 | 10% |
| 安全行为（对抗） | 1 | 801 | 0% |

## 逐 benchmark

| benchmark | 题量 | 语言 | 带图 | 题型 | 判分 | 角色 | 分数区间 |
|---|---:|---|---:|---|---|---|---|
| mmlu_pro | 12,032 | 英 | 0 | 单选（10 选 1） | 规则 | 考生 | 7.9–8.8 |
| ceval | 1,346 | 中 | 0 | 单选 | 规则 | 考生 | 8.3–9.6 |
| agieval | 7,272 | 中 47% / 英 53% | 0 | 单选 6,154 + 填空 1,118 | 规则 | 考生 | 8.1–9.2 |
| olympiadbench | 6,728 | 中 77% / 英 23% | 4,055 | 填空（数值/表达式/区间等） | 规则 | 考生 | 6.4–7.8 |
| mathvista | 1,000 | 英 | 1,000 | 单选 540 + 填空 460 | 规则 | 考生 | 8.3–8.9 |
| k12vista | 600 | 中 | 600 | 单选 209 + 填空 198 + 问答 193 | LLM 按官方 rubric 逐空判 0/1 | 考生 | 6.0–7.6 |
| mathtutorbench_problem_solving | 1,319 | 英 | 0 | 填空（GSM8K 数值） | 规则 | 考生 | 9.5–9.8 |
| pedagogy_benchmark | 1,119 | 英 | 0 | 单选（教学法知识） | 规则 | 考生（教学法） | 6.6–9.0 |
| eduguard_sata | 5,270 | 中 50% / 英 50% | 0 | 多选（哪些构成教学伤害） | 规则 | 考生（安全知识） | 6.9–7.7 |
| ifeval | 541 | 英 | 0 | 带硬约束的生成 | 规则（官方 checker） | 通用 | 8.7–9.5 |
| p07_selfcheck | 550 | 中 47% / 英 53% | 0 | 复用单选 + 填空，两轮作答 | 规则 | 探针 | 4.9–5.6 |
| p08_calibration | 550 | 中 47% / 英 53% | 0 | 复用单选 + 填空，附报置信度 | 规则 | 探针 | 5.6–7.1 |
| p08_abstention | 500 | 英 | 0 | 填空或弃答（UMWP） | 规则 | 探针 | 8.6–9.3 |
| mooccube_prereq | 300 | 中 | 0 | 单选 200 + 排序 100 | 规则 | 探针 | 1.2–4.8 |
| mathtutorbench_solution_correctness | 2,004 | 英 | 0 | 判断学生解答对错 | 规则 | 老师判断 | 8.6–9.0 |
| mathtutorbench_mistake_location | 2,004 | 英 | 0 | 指出第一处错误步骤 | 规则 | 老师判断 | 7.5–7.9 |
| mathtutorbench_mistake_correction | 1,002 | 英 | 0 | 改正后给出最终答案 | 规则 | 老师判断 | 8.6–9.4 |
| longtutor_diagnosis | 1,000 | 中 | 0 | 学生知识状态四分类 | 规则（macro-F1） | 老师判断 | 1.5–4.8 |
| longtutor_evidence | 3,000 | 中 | 0 | 从长历史中提取/推理/查幻觉，简答 | LLM 语义等价判对错 | 老师判断 | 6.4–9.6 |
| sas_bench | 4,109 | 中 | 0 | 给学生简答/填空题分步打分 + 错因标注 | 规则（QWK/CCS/ECS） | 阅卷人 | 3.8–8.7 |
| asap_2 | 7,421 | 英 | 0 | 作文整体打分 1–6 | 规则（QWK） | 阅卷人 | 4.7–6.1 |
| mrbench_judge | 13,240 | 英 | 0 | 给辅导回复贴 8 维标签 | 规则（对人类标注） | 阅卷人 | 4.1–5.9 |
| bea2025_judge | 9,904 | 英 | 0 | 给辅导回复贴 4 维标签 | 规则（对人类标注） | 阅卷人 | 3.7–5.5 |
| mathtutorbench_socratic | 1,319 | 英 | 0 | 生成引导性提问 | BLEU 对教师金标 | 老师生成 | 2.1–3.2 |
| mathtutorbench_scaffolding | 1,150 | 英 | 0 | 生成下一句辅导回复 | LLM 成对比较（对金标教师） | 老师生成 | 1.5–6.1 |
| mathtutorbench_scaffolding_hard | 327 | 英 | 0 | 同上，加难 | LLM 成对比较 | 老师生成 | 1.3–5.8 |
| mathtutorbench_pedagogy | 1,150 | 英 | 0 | 按指定教学法生成回复 | LLM 成对比较 | 老师生成 | 7.6–8.9 |
| mathtutorbench_pedagogy_hard | 327 | 英 | 0 | 同上，加难 | LLM 成对比较 | 老师生成 | 6.4–8.8 |
| mrbench_tutor | 200 | 英 | 0 | 生成辅导回复 | LLM 8 维 rubric | 老师生成 | 8.9–9.9* |
| bea2025_tutor | 300 | 英 | 0 | 生成辅导回复 | LLM 4 维 rubric | 老师生成 | 8.4–9.9* |
| tutorbench | 1,473 | 英 | 811 | 回答学生上传的作业/截图提问 | LLM 逐条 rubric | 老师生成 | 5.1–5.8 |
| mmtutorbench | 770 | 英 | 770 | 看教学视频关键帧后辅导 | LLM 6 维 rubric | 老师生成 | 5.8–7.8 |
| longtutor_teaching | 1,000 | 中 | 0 | 基于长历史给出下一步教学反馈 | LLM 4 维 rubric | 老师生成 | 3.7–8.2 |
| edubench | 3,797 | 英 | 0 | 出题、讲题、编材料、个性化支持等 5 类任务 | LLM 12 维 rubric | 老师生成 | 5.6–9.8 |
| eduillustrate | 230 | 中 | 0（输出为动画） | 写 Manim 代码画出解题过程 | 渲染 + LLM 8 维 rubric | 老师生成 | 1.0–7.6 |
| eduguard_adversarial | 801 | 英 | 0 | 越狱诱导下的回应 | LLM 安全裁判 | 安全行为 | 3.8–10.0 |

## 主要发现

1. **英文为主，越接近真实教学行为，中文越少。** 按题量中文只占 24%。考生类有 36% 中文，主要来自 olympiadbench、ceval、agieval。"老师生成"这一组 12 个 benchmark 里只有 longtutor_teaching 和 eduillustrate 是中文，按题量仅 10%。对话式辅导（MathTutorBench、MRBench、BEA、TutorBench、MMTutorBench）全部是英文。edubench 原始数据有中文，但本仓库可比集的 3,797 题全部是英文。
2. **约八成题量是规则判分。** 但按 benchmark 个数，14 个依赖 LLM 裁判，基本就是全部的"老师生成"组。客观、可复现的判分和最核心的教学行为几乎不重叠。
3. **题量最大的是"打分/标注"类。** mrbench_judge、bea2025_judge、asap_2 三个加起来占总题量三分之一以上，题量规模不代表它们在能力画像中的分量。
4. **封闭题型普遍分高、拉不开差距，开放生成和"针对具体学生判断"的题差距大。** 分数区间列与此前"知道 vs 做到"的判断一致；mrbench_tutor / bea2025_tutor 的高分是 prompt 泄露评分维度造成的，不属于真实饱和。
