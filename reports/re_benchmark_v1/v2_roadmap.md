# RE_BENCHMARK_V1 v2 Roadmap

1. 补齐 Pedagogy Benchmark gated 数据、TutorBench parquet、MMLU-Pro、OlympiadBench full data、EdNet KT1 sample。

2. 建立 C2/C4/C5 的 human rubric：教学反馈、评分理由、安全边界分别标注。

3. 建立双模型 judge + 人工抽查协议，报告 judge agreement，不直接信单一 judge。

4. 分离四条 runner：text MCQ/short answer、open-ended judge、program execution、KT/video/multimodal protocol。

5. 加入中文本地教育安全与未成年人保护红队集，避免只依赖英文 youth-safety 外部证据。

6. 只在各类内部报告分数，不发布跨 C1-C5 的单一平均分。
