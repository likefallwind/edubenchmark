# EduBench 换裁判实验（M2，2026-07-12）

样本：250 条 response（5 任务 × 每任务 50，横跨 11 个被测模型），原裁判 deepseek-v3.2，新裁判 deepseek-v4-pro, doubao-seed-2.0-pro。
rubric 按论文官方 12 指标定义重建（同事原始判分 prompt 未随数据提供），所以对比原裁判的一致性是"裁判+prompt 同时更换"的联合稳健性，读数会偏严。

## original vs deepseek-v4-pro（n=250）

- response 级总分 Spearman：**0.449**
- 模型排名级 Spearman（11 模型）：**0.228**

| 指标 | response 级 ρ | QWK | 均分 A | 均分 B |
|---|---|---|---|---|
| instruction_following | 0.222 | 0.362 | 9.01 | 9.76 |
| tone_style_consistency | 0.033 | 0.0 | 8.54 | 9.8 |
| content_relevance_scope_control | 0.149 | 0.118 | 9.05 | 9.94 |
| scenario_element_integration | 0.206 | 0.071 | 8.01 | 9.8 |
| basic_factual_accuracy | 0.231 | 0.154 | 9.01 | 9.88 |
| domain_knowledge_accuracy | 0.151 | 0.062 | 8.64 | 9.94 |
| reasoning_process_rigor | 0.262 | 0.096 | 8.14 | 9.64 |
| error_identification_correction_accuracy | 0.029 | 0.001 | 7.4 | 8.68 |
| clarity_concision_inspiration | 0.255 | 0.197 | 8.53 | 9.5 |
| motivation_guidance_positive_feedback | 0.611 | 0.411 | 6.84 | 7.72 |
| personalized_adaptation_learning_support | 0.772 | 0.679 | 7.19 | 7.51 |
| higher_order_thinking_ability_development | 0.625 | 0.557 | 8.01 | 8.87 |

## original vs doubao-seed-2.0-pro（n=250）

- response 级总分 Spearman：**0.426**
- 模型排名级 Spearman（11 模型）：**0.364**

| 指标 | response 级 ρ | QWK | 均分 A | 均分 B |
|---|---|---|---|---|
| instruction_following | 0.306 | 0.483 | 9.01 | 9.84 |
| tone_style_consistency | 0.137 | 0.013 | 8.54 | 9.96 |
| content_relevance_scope_control | 0.249 | 0.071 | 9.05 | 9.97 |
| scenario_element_integration | 0.106 | 0.036 | 8.01 | 9.84 |
| basic_factual_accuracy | 0.202 | 0.055 | 9.01 | 9.98 |
| domain_knowledge_accuracy | 0.261 | 0.067 | 8.64 | 9.95 |
| reasoning_process_rigor | 0.329 | 0.161 | 8.14 | 9.34 |
| error_identification_correction_accuracy | -0.032 | -0.032 | 7.4 | 4.58 |
| clarity_concision_inspiration | 0.316 | 0.165 | 8.53 | 9.54 |
| motivation_guidance_positive_feedback | 0.684 | 0.439 | 6.84 | 6.97 |
| personalized_adaptation_learning_support | 0.784 | 0.639 | 7.19 | 6.6 |
| higher_order_thinking_ability_development | 0.71 | 0.541 | 8.01 | 8.8 |

## deepseek-v4-pro vs doubao-seed-2.0-pro（n=250）

- response 级总分 Spearman：**0.683**
- 模型排名级 Spearman（11 模型）：**0.743**

| 指标 | response 级 ρ | QWK | 均分 A | 均分 B |
|---|---|---|---|---|
| instruction_following | 0.503 | 0.573 | 9.76 | 9.84 |
| tone_style_consistency | 0.122 | 0.164 | 9.8 | 9.96 |
| content_relevance_scope_control | 0.325 | 0.428 | 9.94 | 9.97 |
| scenario_element_integration | 0.268 | 0.34 | 9.8 | 9.84 |
| basic_factual_accuracy | 0.42 | 0.352 | 9.88 | 9.98 |
| domain_knowledge_accuracy | 0.334 | 0.384 | 9.94 | 9.95 |
| reasoning_process_rigor | 0.312 | 0.337 | 9.64 | 9.34 |
| error_identification_correction_accuracy | 0.137 | 0.067 | 8.68 | 4.58 |
| clarity_concision_inspiration | 0.496 | 0.547 | 9.5 | 9.54 |
| motivation_guidance_positive_feedback | 0.668 | 0.62 | 7.72 | 6.97 |
| personalized_adaptation_learning_support | 0.806 | 0.725 | 7.51 | 6.6 |
| higher_order_thinking_ability_development | 0.727 | 0.847 | 8.87 | 8.8 |
