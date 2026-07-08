# Benchmark To Atomic Ability Mapping

Each row maps one benchmark subdimension to 1-3 P abilities. Weights sum to 1 within the row.

| Benchmark | Subdimension | Tier | Metric | Default weight | P weights | Rationale |
|---|---|---|---|---:|---|---|
| MMLU-Pro (`mmlu_pro`) | overall/category accuracy | foundation_gate | accuracy | 0.35 | P05 0.60, P06 0.30, P01 0.10 | 基础学科知识与选择题答题能力，主要验证 LLM 答题门槛，不应主导教育能力雷达图。 |
| C-EVAL (`ceval`) | overall/category/subject accuracy | foundation_gate | accuracy | 0.35 | P05 0.60, P06 0.25, P01 0.15 | 中文考试与学科知识，属于基础答题门槛；对应知识调用、推理和选项约束遵循。 |
| AGIEval (`agieval`) | overall/task/language/question_type accuracy | foundation_gate | accuracy | 0.40 | P06 0.45, P05 0.35, P01 0.20 | 标准化考试推理与答题，仍是 LLM 答题能力门槛；更偏 P06。 |
| OlympiadBench (`olympiadbench`) | overall/subject/language/modality accuracy | foundation_gate | accuracy | 0.55 | P06 0.55, P05 0.25, P03 0.20 | 高难学科推理和多模态竞赛题，答题能力未完全饱和；仍作为门槛/诊断而非教育核心。 |
| MathVista (`mathvista`) | task/question_type/answer_type accuracy | diagnostic | accuracy | 0.70 | P03 0.35, P06 0.45, P05 0.20 | 静态图文数学题，主要测常规多模态感知、数学推理和知识调用。 |
| Pedagogy Benchmark (`pedagogy_benchmark`) | CDPK teaching knowledge selection | education_core | accuracy | 0.80 | P05 0.45, P17 0.35, P06 0.20 | 教学法知识选择题，既有教育知识，也有教学策略选择和形式推理。 |
| Pedagogy Benchmark (`pedagogy_benchmark`) | SEND special education needs selection | education_core | accuracy | 0.80 | P05 0.35, P16 0.35, P17 0.30 | 特殊教育需求判断更依赖学习者画像和干预策略选择。 |
| ASAP 2.0 (`asap_2`) | essay holistic QWK | education_core | qwk_0_to_100 | 0.80 | P14 0.65, P02 0.20, P05 0.15 | 作文评分一致性主要是 rubric 映射评分，同时需要定位文本证据与写作知识。 |
| SAS-Bench (`sas_bench`) | QWK holistic total score | education_core | score_0_to_100 | 0.90 | P14 0.70, P02 0.15, P05 0.15 | 总分评分一致性主测 rubric 映射评分。 |
| SAS-Bench (`sas_bench`) | CCS step scoring consistency | education_core | score_0_to_100 | 0.95 | P14 0.55, P12 0.25, P02 0.20 | 分步踩分同时涉及 rubric 映射、错误位置/步骤定位和证据定位。 |
| SAS-Bench (`sas_bench`) | ECS error-cause consistency | education_core | score_0_to_100 | 1.00 | P13 0.70, P05 0.20, P06 0.10 | 错因诊断准确度主测错因归因。 |
| EduBench (`edubench`) | IP idea provision / heuristic answer | education_core | likert_0_to_10 | 0.80 | P17 0.40, P18 0.35, P05 0.25 | 启发式解答主要是教学策略选择与适配性解释。 |
| EduBench (`edubench`) | PCC pedagogical/personalized content creation | education_core | likert_0_to_10 | 0.80 | P18 0.45, P17 0.30, P05 0.25 | 教育内容生成以反馈解释和策略适配为主，当前多为纯文本，不直接等同 P10。 |
| EduBench (`edubench`) | PLS personalized learning support | education_core | likert_0_to_10 | 0.85 | P16 0.30, P17 0.45, P18 0.25 | 个性化学习支持以学习者画像、干预策略和适配反馈为主。 |
| EduBench (`edubench`) | QG question generation | education_core | likert_0_to_10 | 0.75 | P18 0.35, P06 0.35, P05 0.30 | 题目生成是教育约束下的推理生成和适配解释，不是非文本多模态产物。 |
| EduBench (`edubench`) | TMG teaching material generation | education_core | likert_0_to_10 | 0.75 | P18 0.40, P05 0.35, P06 0.25 | 教学材料生成主要看教育解释、领域知识和生成推理；若包含图示再另映射 P10。 |
| TutorBench (`tutorbench`) | Fair815 multimodal tutor quality | education_core | score_0_to_100 | 1.00 | P18 0.40, P17 0.35, P03 0.25 | 真实多模态 tutor 质量综合考察反馈生成、策略选择和图文感知。 |
| MathTutorBench (`mathtutorbench_problem_solving`) | Problem Solving | foundation_gate | accuracy | 0.45 | P06 0.60, P05 0.30, P07 0.10 | 数学求解门槛，重要但不能证明会辅导。 |
| MathTutorBench (`mathtutorbench_solution_correctness`) | Solution Correctness | education_core | accuracy_or_f1 | 0.85 | P11 0.60, P07 0.25, P02 0.15 | 给定参考/学生解判断正确性，主测作答正误判定。 |
| MathTutorBench (`mathtutorbench_mistake_location`) | Mistake Location | education_core | accuracy_or_f1 | 1.00 | P12 0.70, P02 0.20, P11 0.10 | 错误位置定位是 P12 的直接测量。 |
| MathTutorBench (`mathtutorbench_mistake_correction`) | Mistake Correction | education_core | accuracy | 0.90 | P13 0.45, P18 0.35, P06 0.20 | 纠错需要识别错因并生成可用修正/反馈。 |
| MathTutorBench (`mathtutorbench_pedagogy`) | Pedagogy IF | education_core | win_rate_or_accuracy | 0.95 | P17 0.45, P18 0.30, P05 0.25 | 教学法指令遵循主测策略选择和适配反馈。 |
| MathTutorBench (`mathtutorbench_pedagogy_hard`) | Pedagogy IF hard | education_core | win_rate_or_accuracy | 1.00 | P17 0.45, P18 0.30, P05 0.25 | hard 子集较有区分度，权重略高。 |
| MathTutorBench (`mathtutorbench_scaffolding`) | Scaffolding | education_core | win_rate_or_accuracy | 1.00 | P17 0.50, P18 0.35, P05 0.15 | 脚手架主测下一步教学干预选择与反馈生成。 |
| MathTutorBench (`mathtutorbench_scaffolding_hard`) | Scaffolding hard | education_core | win_rate_or_accuracy | 1.00 | P17 0.50, P18 0.35, P05 0.15 | hard 子集仍主测教学干预与反馈。 |
| BEA 2025 Judge (`bea2025_judge`) | judge labels: mistake/guidance/actionability | education_core | accuracy | 0.80 | P14 0.45, P13 0.30, P11 0.25 | 作为教育评判者，主要看 rubric/标签映射、错因判断和正误判断。 |
| BEA 2025 Tutor (`bea2025_tutor`) | pedagogical pass rate | education_core | pass_rate | 0.90 | P18 0.45, P17 0.30, P13 0.25 | 生成 tutor 回复，强调可行动指导、反馈生成和错因识别。 |
| MRBench Judge (`mrbench_judge`) | 8-dimension tutor response judging | education_core | accuracy | 0.75 | P14 0.45, P13 0.25, P20 0.30 | 多维 tutor 回复评判含评分映射、错因/定位和泄题/角色边界。 |
| MRBench Tutor (`mrbench_tutor`) | 8-dimension tutor pass rate | education_core | pass_rate | 0.80 | P18 0.45, P17 0.30, P20 0.25 | tutor 回复生成同时考查指导、反馈和不泄题/角色边界。 |
| EduGuard-Bench P1 (`eduguard_sata`) | Teaching Harm / SATA RFS | education_core | rfs_0_to_1 | 1.00 | P20 0.35, P21 0.30, P22 0.35 | 教学伤害全选题同时测试角色边界、风险识别和处置选择。 |
| EduGuard-Bench P2 (`eduguard_adversarial`) | Adversarial Safety ASR | education_core | asr_0_to_1_lower_better | 1.00 | P22 0.45, P20 0.30, P21 0.25 | 对抗安全主要测安全处置，同时需要识别风险和维持教育角色边界。 |
| EduGuard-Bench P2 (`eduguard_adversarial`) | Refusal quality distribution | diagnostic | share_0_to_1 | 0.70 | P22 0.60, P18 0.25, P20 0.15 | 教育型拒答是处置选择和教育性重定向质量。 |
| EduIllustrate (`eduillustrate`) | 8-dim 0-5 visual explanation score | diagnostic | likert_0_to_5 | 0.85 | P10 0.45, P03 0.25, P18 0.30 | 教学图示/图文协同生成直接测多模态教学产物生成。 |
| MMTutorBench (`mmtutorbench`) | multimodal tutor score | diagnostic | score_0_to_6 | 0.90 | P03 0.30, P18 0.40, P17 0.30 | 多模态 tutor 综合测图文感知、反馈生成和策略选择；当前小样本默认排除主图。 |
