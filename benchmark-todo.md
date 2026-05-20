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
