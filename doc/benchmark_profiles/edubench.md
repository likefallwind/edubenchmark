# EduBench

**一句话**：中文教育场景生成基准——给模型真实教育任务（讲题、出题、编材料、个性化支持），LLM 裁判按 12 个指标维度打 0-10 分。占当前证据行的 55/181，是体系里最大的分数来源。

## 出处与背景

- Bai 等（ybai-nlp/EduBench），2025；https://github.com/ybai-nlp/EduBench
- 动机：把教育大模型评测从选择题拉到真实生成任务，覆盖 9 大教育场景（作业批改、学习规划、心理健康辅导、学情分析、知识点讲解等）、4,000+ 场景上下文。

## 数据

- 官方发布覆盖 4,000+ 教育场景上下文；论文的人类/模型一致性实验使用 198 条中英 sampled data。
- 本仓库可比题单为 **3,797 条英文有效样本 × 11 个既有模型**，prompt、item_id 与 responses 已规范化到 `reports/eval/edubench/_judge-deepseek-v3.2/<model>/`。

## 任务与判分

- 本仓库用到 5 个任务：**IP** 启发式解答 / **PCC** 个性化内容生成 / **PLS** 个性化学习支持 / **QG** 题目生成 / **TMG** 教学材料生成。
- LLM 裁判打分，0-10。**原生维度是 12 个评价指标**：基础事实准确性、领域知识准确性、指令遵循、错误识别与纠正、场景元素整合、内容相关性与范围控制、表达清晰启发性、推理严密性、语气风格一致性、高阶思维培养、动机引导正向反馈、个性化适应学习支持。**本地报告（`otherbenchmark/edubench-0625.md`）第三节有 12 指标的逐模型分数。**

## 在本仓库怎么用

- 原始数据已到位（2026-07-12）：`reports/eval/edubench/_judge-deepseek-v3.2/<model>/`，11 模型 × 3,797 题（IP 1253 / QG 1266 / TMG 578 / PLS 448 / PCC 252，**只有这 5 个生成/支持类任务，没有 EC/QA/AG/ES**），逐题 12 指标分，裁判 deepseek-v3.2。导入脚本 `scripts/import_edubench_results.py`（源目录只读）。
- 原生 harness adapter：`scripts/eval/benchmarks/edubench.py`；复用同一 3,797 条 prompt/item_id，默认 MiniMax-M3 固定裁判，输出标准 `predictions.jsonl` / `extractions.jsonl` / `scored.jsonl` / `summary.json` / `report.html`。非 MiniMax-M3 裁判统一隔离到 `_judge-<judge>/<model>/`。
- 同事的精确 judge prompt 没有随原始产物交付，官方仓库也未提供可直接执行的完整裁判代码；adapter 的 prompt 依据论文 12 维定义和官方动态指标分配重建。题单与裁判身份可比，但不能宣称是旧协议的逐字节复放。
- 逐题级分析：`scripts/analyze_edubench_item_level.py` → `reports/eval/edubench/_analysis/`；换裁判实验：`scripts/run_edubench_judge_swap.py` → `reports/eval/edubench/_judge_swap/`。

## 局限与注意

- **区分度（13 号实测，n=11）**：IP 8.22/0.33（受限）、PCC 8.80/0.57（受限）、PLS 8.74/0.52（受限）、QG 8.47/0.50（临界）、TMG 8.18/1.00（不受限）——LLM 裁判打分整体偏高压缩。
- **家族 halo 0.76**（家族内 ρ 0.5-0.97、对外接近零），触发"家族内先聚合"。
- **M2 换裁判实验结论（2026-07-12，250 条 × deepseek-v4-pro + doubao-seed-2.0-pro）**：指标分三类——支持簇（个性化适应 ρ 0.77-0.81、高阶思维 0.63-0.73、动机引导 0.61-0.68）跨裁判稳健是真测量；**错误识别指标是裁判噪声**（三裁判两两 ρ≤0.14、均分 4.6/7.4/8.7 各判各的），不入映射；知识/格式簇被新裁判打到天花板（9.8-10.0）只作门槛参考。对原裁判总分 response 级 ρ=0.43-0.45（含 prompt 差异）。
- 题级两簇结构：基础事实与动机/个性化/高阶思维题级 ρ≈0——同一批回答里"答得准"和"教得好"是独立方向（"会答题≠会教"最硬同源证据）。

## 当前映射与升级方向

- 5 任务分别挂 P17/P18 为主（IP/PLS）、P18/P05/P06（PCC/QG/TMG）、P16（PLS 0.30）；education_core。
- **R1（按 R14 收窄）**：按指标挂 P 限定在裁判稳健的三个指标——个性化适应→P17c、动机引导→P18c、高阶思维→P18/P06；~~错误识别→P11c~~（R14 否决：裁判噪声）；指令遵循不作 P01 直接测量（R13，走 IFEval）；知识指标只作门槛。任务×指标格子区分度：60 格里 52 格跨模型 SD≥0.3，比整 benchmark 级好一个量级。
