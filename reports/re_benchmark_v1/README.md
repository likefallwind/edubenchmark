# RE_BENCHMARK_V1 Reports — 索引

本目录存放 RE_BENCHMARK_V1 的研究报告与模型运行产物。**先看本索引再找文件**。

约定：叙述性文档放根目录；零散的小实验放 `experiments/<name>/`；同名标准产物
（`predictions.jsonl` / `run_summary.json` / `scored_items.jsonl`）是各 run 的固定输出名。

## 1. 阅读顺序（研究文档）

1. `2026-05-20_worklog.md` — 当日进展与待办。
2. `RE_BENCHMARK_V1_RESEARCH_REPORT.md`（`.html` 为浏览器版）— 总研究结论。
3. `stage1_data_status.md` — 数据可得性与 manifest 状态。
4. `stage2_data_acquisition_and_proxy.md` — 缺失数据与代理方案决策。
5. `stage3_pilot_set_design.md` — pilot 集设计与字段含义。
6. `stage4_minimax_smoke_test.md` — MiniMax 运行范围与评分注意事项。
7. `v2_roadmap.md` — 下一版优先级建议。
8. `2026-05-20_research_status_and_next_steps.html` — 状态快照（浏览器版）。

## 2. MiniMax 全量 pilot 产物（canonical run）

- `minimax_predictions.jsonl` — full-pilot 原始预测。
- `minimax_auto_scores.jsonl` — full-pilot 自动评分行。
- `minimax_full_pilot_report.html` — 浏览器版 full-pilot 报告。
- `minimax_qualitative_samples.md` — 人工抽查样例。

## 3. 早期/中间运行产物（smoke / 早期 pilot，多已被第 2 节或 experiments/ 取代）

- `minimax_smoke_report.html` — 最早的 smoke-test 报告。
- `pilot_report.html` / `run_report.html` — 早期 run 报告。
- `run_summary.json` / `scored_items.jsonl` — 早期 run 的汇总与评分行。

> 这些是历史产物、被若干文档按标准名引用，故保留在根目录；查"当前结论"请用第 1、2 节。

## 4. 实验（`experiments/`）

小型、非 canonical 的实验放这里；最终交付物才进根目录。

- `experiments/eduguard_judge_calibration/` — **C5 judge 校准**：以 Opus-4.8 金标衡量
  MiniMax-M3 / M2.7 / DeepSeek-V3 当 judge 判得准不准（见其 `README.md` 跑法、`REPORT.md` 结论）。
- `experiments/mcq_prompt_fix/` — 测 MCQ prompt 是否能引出选项字母作答。
- `experiments/minimax_full_pilot_rerun_2026_05_20/` — 139 题全量 MiniMax 重跑。
- `experiments/empty_response_retry_2026_05_22/` — 重跑 full-pilot 的空响应，给出合并 139 行预测。
- `experiments/no_maxtokens_empty_retry_2026_05_22/` — 去掉 `max_tokens` 后重跑剩余空响应。
- `experiments/no_maxtokens_final_check_2026_05_22/` — 最后两条空行的终检。
- `experiments/full_pilot_minimax_rerun_2026_05_22/` — 无 `max_tokens`、并发 2 的 139 题 M2.7 重跑。
