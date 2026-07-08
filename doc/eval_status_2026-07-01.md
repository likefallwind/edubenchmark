# 评测进度总览（截至 2026-07-06）

说明：

- 纵轴是评测任务（基准），横轴是模型。
- `-/-` 表示该模型在该评测下尚无 `summary.json` 产出。
- `predictions only` 表示当前仅有 `predictions.jsonl`，未产出 `summary.json`。
- `-/X` 表示 `summary.json` 存在但 `scored` 缺失（多见于只做了部分统计摘要的基线）。

| 评测任务（纵轴） \ 模型（横轴） | deepseek-v3.2 | deepseek-v4-flash | deepseek-v4-pro | doubao-seed-2.0-pro | doubao-seed-2.0-lite | glm-5.1 | glm-5.2 | gpt-5.5 | kimi-k2.7-code | opus-4.8 | MiniMax-M2.7 | minimax3 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| agieval | -/- | 7270/7272 | 7272/7272 | -/- | -/- | -/- | 7219/7272 | -/- | -/- | -/- | 7266/7272 | 7268/7272 |
| bea2025_judge | 9904/9904 | 9904/9904 | 9904/9904 | -/- | -/- | -/- | -/- | -/- | -/- | -/- | -/- | 9896/9904 |
| bea2025_tutor | -/- | -/- | -/- | -/- | -/- | -/- | 300/300 | -/- | -/- | -/- | -/- | 300/300 |
| ceval | -/- | 1344/1346 | 1346/1346 | -/- | -/- | 5/5 | 1345/1346 | -/- | -/- | -/- | 1346/1346 | 1346/1346 |
| eduguard_adversarial | -/- | -/- | 801/801 | 801/801 | 801/801 | 772/801 | 801/801 | 797/801 | -/- | -/- | predictions only | 801/801 |
| eduguard_sata | -/- | 4/4 | 5266/5270 | 5270/5270 | 5270/5270 | 5268/5270 | 5270/5270 | 2148/2635 | -/- | -/- | -/- | 5270/5270 |
| eduillustrate | -/5 | -/- | -/- | -/5 | -/230 | -/- | -/- | -/- | -/230 | -/5 | -/- | -/230 |
| mathtutorbench_judge_calibration | 964/964 | 964/964 | 964/964 | -/- | -/- | -/- | 964/964 | -/- | -/- | -/- | 964/964 | 964/964 |
| mathtutorbench_mistake_correction | -/- | 1002/1002 | 1002/1002 | -/- | -/- | -/- | 1001/1002 | -/- | -/- | -/- | -/- | 1002/1002 |
| mathtutorbench_mistake_location | -/- | 2004/2004 | 2004/2004 | -/- | -/- | -/- | 2004/2004 | -/- | -/- | -/- | -/- | 2004/2004 |
| mathtutorbench_pedagogy | -/- | 1150/1150 | 1150/1150 | 1150/1150 | 1150/1150 | -/- | 1150/1150 | -/- | -/- | -/- | -/- | 1149/1150 |
| mathtutorbench_pedagogy_hard | -/- | 327/327 | 327/327 | 327/327 | 327/327 | -/- | 327/327 | -/- | -/- | -/- | -/- | 327/327 |
| mathtutorbench_problem_solving | -/- | 1319/1319 | -/- | -/- | -/- | -/- | 1319/1319 | -/- | -/- | -/- | -/- | 1319/1319 |
| mathtutorbench_scaffolding | -/- | 1150/1150 | 1150/1150 | 1150/1150 | 1150/1150 | -/- | 1150/1150 | -/- | -/- | -/- | -/- | 1150/1150 |
| mathtutorbench_scaffolding_hard | -/- | 327/327 | 327/327 | 327/327 | 327/327 | -/- | 327/327 | -/- | -/- | -/- | -/- | 327/327 |
| mathtutorbench_socratic | -/- | -/- | predictions only | -/- | -/- | -/- | predictions only | -/- | -/- | -/- | -/- | 3/3 |
| mathtutorbench_solution_correctness | -/- | 2004/2004 | 2004/2004 | -/- | -/- | -/- | 2004/2004 | -/- | -/- | -/- | -/- | 2004/2004 |
| mathvista | -/- | -/- | -/- | -/- | -/- | -/- | -/- | -/- | -/- | -/- | -/- | 993/1000 |
| mmlu_pro | -/- | 12021/12032 | 12024/12032 | 5/5 | 5/5 | 5/5 | 11875/12032 | 1/1 | -/- | -/- | 12022/12032 | 12032/12032 |
| mmtutorbench | -/- | -/- | -/- | -/- | -/- | -/- | -/- | -/- | -/- | -/- | -/- | 5/5 |
| mmtutorbench_judge_calibration | -/- | -/- | -/- | -/- | -/- | -/- | -/- | -/- | -/- | -/- | -/- | 0/0 |
| mrbench_judge | 13240/13240 | 13240/13240 | 13240/13240 | -/- | -/- | -/- | -/- | -/- | -/- | -/- | -/- | 13238/13240 |
| mrbench_tutor | -/- | -/- | -/- | -/- | -/- | -/- | 200/200 | -/- | -/- | -/- | -/- | 200/200 |
| olympiadbench | -/- | -/- | 2669/6728 | -/- | -/- | -/- | -/- | -/- | -/- | -/- | -/- | 6722/6728 |

## 2026-07-06 相对 2026-07-01 主要变化

- `agieval`：新增 `glm-5.2` 与 `MiniMax-M2.7` 的 `scored/total`（7219/7272 与 7266/7272）。
- `bea2025_judge`：新增 `deepseek-v4-pro` full（9904/9904）。
- `bea2025_tutor`：新增 `glm-5.2` 的 300/300。
- `ceval`：新增 `glm-5.2`（1345/1346）与 `MiniMax-M2.7` full（1346/1346）。
- `eduguard_adversarial`：`MiniMax-M2.7` 已有 predictions，仅有 `predictions.jsonl`，尚无 `summary.json`。
- `mathtutorbench_mistake_correction`：新增 `deepseek-v4-pro` full（1002/1002）、`glm-5.2`（1001/1002）。
- `mathtutorbench_mistake_location`：新增 `deepseek-v4-pro`、`glm-5.2` full（均 2004/2004）。
- `mathtutorbench_problem_solving`：新增 `glm-5.2` full（1319/1319）。
- `mathtutorbench_socratic`：`deepseek-v4-pro` 与 `glm-5.2` 暂为 `predictions only`。
- `mathtutorbench_solution_correctness`：新增 `deepseek-v4-pro` 与 `glm-5.2`（均 2004/2004）。
- `mmlu_pro`：`glm-5.2` 从 `predictions only` 完成到 11875/12032；`MiniMax-M2.7` 12022/12032。
- `mrbench_judge`：新增 `deepseek-v4-pro` full（13240/13240）。
- `mrbench_tutor`：新增 `glm-5.2` 200/200。
- `olympiadbench`：`deepseek-v4-pro` 从 `predictions only` 变为 2669/6728（非满量）。
