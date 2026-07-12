# MMTutorBench

**一句话**：视频关键帧数学辅导基准——模型看教学视频的关键帧序列 + 学生提问，生成结构化辅导回复，裁判按 6 个二元维度打分。

## 出处与背景

- HF `Tangchiu/mmtutorbench`，2025。
- 动机：真实辅导常发生在"学生看着题/看着讲解卡住了"的多模态语境，考察模型能否基于视觉上下文做辅导（而非只看文字）。

## 数据

- 770 条 JSONL 样本、1,414 张关键帧图片。英文。
- 获取：`fetch_eval_datasets.py --benchmark mmtutorbench`（JSONL + 关键帧 + `data_manifest.json`）。

## 任务与判分

- 输入：历史关键帧 + 当前帧 + 学生提问；要求回复分三段：Insight Discovery / Operation Formulation / Operation Execution。
- 固定 rubric 裁判（`MMTUTORBENCH_JUDGE_MODEL`，默认 MiniMax-M3）按 6 个二元维度判分：insight_identification、operation_prescription、operation_execution、solution_scope_control、brevity、coherence；报告 0-6 总分 + 论文等权分。
- **mmtutorbench_judge_calibration 只是占位**：公开数据没有逐条人类金标，无法做裁判校准（输出状态而非编造校准）。

## 在本仓库怎么用

- 首次冒烟：`LIMIT=5 MODEL=MiniMax-M3 JUDGE_MODEL=MiniMax-M3 ./scripts/run_eval.sh mmtutorbench`；不要默认跑全量 770。

## 局限与注意

- **区分度（13 号实测）**：n=1（默认小样本、单模型），当前不进主图（映射备注"小样本默认排除"）。
- 无人类金标 → 裁判分数完全没有外部锚点，只能做模型间相对比较。
- 三段式格式要求让分数混入格式遵循成分。

## 当前映射

- P18 0.40 / P03 0.30 / P17 0.30；diagnostic。
- 构念核对：P03 归"教学场景图文理解"（R5）；P17 归"对话辅导"侧（R4）。
