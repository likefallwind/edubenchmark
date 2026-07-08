# 教育裁判陪审团 vs 单裁判（judge_meta_eval_v1 · test split）

- 生成脚本：`scripts/build_judge_jury_report.py`（n_boot=1000, seed=20260706）
- 陪审团：deepseek-v4-pro / glm-5.2 / MiniMax-M3；多数投票 + dev-kappa 加权投票
- 所有区间为 cluster bootstrap 95% CI（重采样单元 = 对话/偏好对）；主判定 = 陪审团与最佳单裁判的 macro kappa 配对差值

## mrbench

test 集：3334 条判例 / 49 个对话簇；最佳单裁判（dev kappa）= **glm-5.2**

| 系统 | macro kappa | macro agreement | macro F1 | unparsed/弃权 |
|---|---|---|---|---|
| deepseek-v4-pro | 0.417 [0.378, 0.456] | 0.737 [0.717, 0.755] | 0.536 [0.508, 0.559] | 0.0 |
| glm-5.2 | 0.438 [0.398, 0.480] | 0.732 [0.711, 0.754] | 0.580 [0.548, 0.608] | 0.0 |
| MiniMax-M3 | 0.354 [0.319, 0.389] | 0.668 [0.645, 0.689] | 0.546 [0.521, 0.569] | 0.0 |
| jury_majority | 0.441 [0.401, 0.481] | 0.740 [0.718, 0.760] | 0.583 [0.552, 0.607] | 0.0 |
| jury_weighted | 0.437 [0.399, 0.478] | 0.741 [0.720, 0.762] | 0.560 [0.533, 0.594] | 0.0 |

- **jury_majority − glm-5.2**（macro kappa 配对差值）：0.003 [-0.016, 0.019] → **无显著差异**
- **jury_weighted − glm-5.2**（macro kappa 配对差值）：-0.001 [-0.022, 0.018] → **无显著差异**
- test 集三票分歧率：0.3089（per-dimension 见 summary.json）

## bea2025

test 集：2492 条判例 / 75 个对话簇；最佳单裁判（dev kappa）= **glm-5.2**

| 系统 | macro kappa | macro agreement | macro F1 | unparsed/弃权 |
|---|---|---|---|---|
| deepseek-v4-pro | 0.388 [0.341, 0.431] | 0.668 [0.639, 0.696] | 0.533 [0.503, 0.562] | 0.0 |
| glm-5.2 | 0.406 [0.362, 0.447] | 0.682 [0.656, 0.708] | 0.529 [0.503, 0.552] | 0.0 |
| MiniMax-M3 | 0.335 [0.292, 0.376] | 0.603 [0.574, 0.633] | 0.515 [0.485, 0.540] | 0.0 |
| jury_majority | 0.411 [0.365, 0.455] | 0.680 [0.653, 0.707] | 0.540 [0.511, 0.566] | 0.0 |
| jury_weighted | 0.408 [0.362, 0.453] | 0.679 [0.651, 0.705] | 0.540 [0.511, 0.566] | 0.0 |

- **jury_majority − glm-5.2**（macro kappa 配对差值）：0.005 [-0.014, 0.023] → **无显著差异**
- **jury_weighted − glm-5.2**（macro kappa 配对差值）：0.002 [-0.018, 0.020] → **无显著差异**
- test 集三票分歧率：0.3933（per-dimension 见 summary.json）

## mathtutorbench

test 集：240 条判例 / 120 个对话簇；最佳单裁判（dev kappa）= **MiniMax-M3**

| 系统 | macro kappa | macro agreement | macro F1 | unparsed/弃权 |
|---|---|---|---|---|
| deepseek-v4-pro | 0.608 [0.475, 0.733] | 0.804 [0.738, 0.867] | 0.804 [0.737, 0.867] | 0.0 |
| glm-5.2 | 0.692 [0.567, 0.800] | 0.846 [0.783, 0.900] | 0.846 [0.783, 0.900] | 0.0 |
| MiniMax-M3 | 0.675 [0.550, 0.792] | 0.838 [0.775, 0.896] | 0.838 [0.775, 0.896] | 0.0 |
| jury_majority | 0.667 [0.542, 0.783] | 0.833 [0.771, 0.892] | 0.833 [0.770, 0.891] | 0.0 |
| jury_weighted | 0.667 [0.542, 0.783] | 0.833 [0.771, 0.892] | 0.833 [0.770, 0.891] | 0.0 |

- **jury_majority − MiniMax-M3**（macro kappa 配对差值）：-0.008 [-0.083, 0.067] → **无显著差异**
- **jury_weighted − MiniMax-M3**（macro kappa 配对差值）：-0.008 [-0.083, 0.067] → **无显著差异**
- test 集三票分歧率：0.1375（per-dimension 见 summary.json）

## 长度偏置（WP5）

见 summary.json 每个来源的 `length_bias`：dimension_label 线为响应长度五分位的
agreement 与宽容度差 P(sys=Yes)−P(human=Yes)；pairwise 线为 P(选更长回复) 与人类专家的差值。
