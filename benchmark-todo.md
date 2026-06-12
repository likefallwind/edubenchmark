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

- Data-quality finding: 官方 `Dataset/SATAs.xlsx` 的 Answer 列与题目行错位（该列按 `Results/SATAs/*.xlsx` 的行序排列，约 1,333/2,635 题答案落在错误题目上）。
  Product reason: 直接使用官方数据文件评测会使 RFS/Accuracy 大幅失真（冒烟样本上 RFS 0.79 → 0.39）。
  Mitigation: `scripts/eval/data/fetch_eval_datasets.py --benchmark eduguard_bench` 已改为从 13 个官方 Results 文件按 ID 多数投票重建答案键（该键可复现论文 DeepSeek-V3 RFS≈0.73）；可考虑向上游仓库报 issue。
  Related capabilities: D21; C5.
  Source: sources/datasets/eduguard_bench/；reports/eval/eduguard_sata/
