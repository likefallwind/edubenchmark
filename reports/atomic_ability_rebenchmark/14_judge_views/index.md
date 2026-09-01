# Judge Views

一个判官一套完整结果。评测场切判官时,读的是这里。

主产物(`09_*` / `10_*`)是 **MiniMax-M3** 的视图。

完整性的分母**按判官算**:判官读不了图就判不了 eduillustrate,那些格从它的分母里
扣掉(`judge_incapable`),不是待办。判据是取分行存在,不是目录存在——目录里的冒烟
跑分会被「样本<100」地板剔掉,只看目录会把它误判成已覆盖。

| 判官 | 覆盖 | 可达 | 状态 | 判不了的 benchmark | 自评格 |
|---|---:|---:|---|---|---:|
| `MiniMax-M3` (主) | 216 | 216 | ✅ 完整 | — | 47 |
| `deepseek-v4-flash` | 212 | 212 | ✅ 完整 | eduillustrate | 0 |
| `deepseek-v3.2` | 68 | 230 | 缺 162 | — | 0 |
| `MiniMax-M2.7` | 3 | 216 | 缺 213 | — | 0 |

**自评格**:判官就是被测模型本人。多判官的意义正是防「模型给自己打分打高」,
所以自评格必须标出来(证据行的 `self_judged`),但不能剔除——剔了该判官的视图就不完整。

## `deepseek-v3.2` 还缺 162 格

- bea2025_tutor · dimension: Actionability · deepseek-v4-pro
- bea2025_tutor · dimension: Actionability · doubao-seed-2-0-pro
- bea2025_tutor · dimension: Actionability · glm-5.2
- bea2025_tutor · dimension: Actionability · minimax-m2.7
- bea2025_tutor · dimension: Actionability · minimax-m3
- bea2025_tutor · dimension: Actionability · qwen-qwen3-5-4b
- bea2025_tutor · dimension: Actionability · qwen-qwen3-8-27b
- bea2025_tutor · dimension: Mistake_Identification · deepseek-v4-pro
- bea2025_tutor · dimension: Mistake_Identification · doubao-seed-2-0-pro
- bea2025_tutor · dimension: Mistake_Identification · glm-5.2
- bea2025_tutor · dimension: Mistake_Identification · minimax-m2.7
- bea2025_tutor · dimension: Mistake_Identification · minimax-m3
- bea2025_tutor · dimension: Mistake_Identification · qwen-qwen3-5-4b
- bea2025_tutor · dimension: Mistake_Identification · qwen-qwen3-8-27b
- bea2025_tutor · dimension: Providing_Guidance · deepseek-v4-pro
- bea2025_tutor · dimension: Providing_Guidance · doubao-seed-2-0-pro
- bea2025_tutor · dimension: Providing_Guidance · glm-5.2
- bea2025_tutor · dimension: Providing_Guidance · minimax-m2.7
- bea2025_tutor · dimension: Providing_Guidance · minimax-m3
- bea2025_tutor · dimension: Providing_Guidance · qwen-qwen3-5-4b
- bea2025_tutor · dimension: Providing_Guidance · qwen-qwen3-8-27b
- edubench · QG × clarity_concision_inspiration + scenario_element_integration (task×metric) · qwen-qwen3-5-4b
- edubench · QG × clarity_concision_inspiration + scenario_element_integration (task×metric) · qwen-qwen3-8-27b
- edubench · QG × domain_knowledge_accuracy + basic_factual_accuracy (task×metric) · qwen-qwen3-5-4b
- edubench · QG × domain_knowledge_accuracy + basic_factual_accuracy (task×metric) · qwen-qwen3-8-27b
- edubench · TMG/PCC × clarity_concision_inspiration + scenario_element_integration (task×metric) · qwen-qwen3-5-4b
- edubench · TMG/PCC × clarity_concision_inspiration + scenario_element_integration (task×metric) · qwen-qwen3-8-27b
- edubench · basic_factual_accuracy (metric) · qwen-qwen3-5-4b
- edubench · basic_factual_accuracy (metric) · qwen-qwen3-8-27b
- edubench · clarity_concision_inspiration (metric) · qwen-qwen3-5-4b
- edubench · clarity_concision_inspiration (metric) · qwen-qwen3-8-27b
- edubench · domain_knowledge_accuracy (metric) · qwen-qwen3-5-4b
- edubench · domain_knowledge_accuracy (metric) · qwen-qwen3-8-27b
- edubench · error_identification_correction_accuracy (metric) · qwen-qwen3-5-4b
- edubench · error_identification_correction_accuracy (metric) · qwen-qwen3-8-27b
- edubench · higher_order_thinking_ability_development (metric) · qwen-qwen3-5-4b
- edubench · higher_order_thinking_ability_development (metric) · qwen-qwen3-8-27b
- edubench · motivation_guidance_positive_feedback (metric) · qwen-qwen3-5-4b
- edubench · motivation_guidance_positive_feedback (metric) · qwen-qwen3-8-27b
- edubench · personalized_adaptation_learning_support (metric) · qwen-qwen3-5-4b

## `MiniMax-M2.7` 还缺 213 格

- bea2025_tutor · dimension: Actionability · deepseek-v4-pro
- bea2025_tutor · dimension: Actionability · doubao-seed-2-0-pro
- bea2025_tutor · dimension: Actionability · glm-5.2
- bea2025_tutor · dimension: Actionability · minimax-m2.7
- bea2025_tutor · dimension: Actionability · minimax-m3
- bea2025_tutor · dimension: Actionability · qwen-qwen3-5-4b
- bea2025_tutor · dimension: Actionability · qwen-qwen3-8-27b
- bea2025_tutor · dimension: Mistake_Identification · deepseek-v4-pro
- bea2025_tutor · dimension: Mistake_Identification · doubao-seed-2-0-pro
- bea2025_tutor · dimension: Mistake_Identification · glm-5.2
- bea2025_tutor · dimension: Mistake_Identification · minimax-m2.7
- bea2025_tutor · dimension: Mistake_Identification · minimax-m3
- bea2025_tutor · dimension: Mistake_Identification · qwen-qwen3-5-4b
- bea2025_tutor · dimension: Mistake_Identification · qwen-qwen3-8-27b
- bea2025_tutor · dimension: Providing_Guidance · deepseek-v4-pro
- bea2025_tutor · dimension: Providing_Guidance · doubao-seed-2-0-pro
- bea2025_tutor · dimension: Providing_Guidance · glm-5.2
- bea2025_tutor · dimension: Providing_Guidance · minimax-m2.7
- bea2025_tutor · dimension: Providing_Guidance · minimax-m3
- bea2025_tutor · dimension: Providing_Guidance · qwen-qwen3-5-4b
- bea2025_tutor · dimension: Providing_Guidance · qwen-qwen3-8-27b
- edubench · QG × clarity_concision_inspiration + scenario_element_integration (task×metric) · deepseek-v4-pro
- edubench · QG × clarity_concision_inspiration + scenario_element_integration (task×metric) · doubao-seed-2-0-pro
- edubench · QG × clarity_concision_inspiration + scenario_element_integration (task×metric) · glm-5.2
- edubench · QG × clarity_concision_inspiration + scenario_element_integration (task×metric) · minimax-m2.7
- edubench · QG × clarity_concision_inspiration + scenario_element_integration (task×metric) · minimax-m3
- edubench · QG × clarity_concision_inspiration + scenario_element_integration (task×metric) · qwen-qwen3-5-4b
- edubench · QG × clarity_concision_inspiration + scenario_element_integration (task×metric) · qwen-qwen3-8-27b
- edubench · QG × domain_knowledge_accuracy + basic_factual_accuracy (task×metric) · deepseek-v4-pro
- edubench · QG × domain_knowledge_accuracy + basic_factual_accuracy (task×metric) · doubao-seed-2-0-pro
- edubench · QG × domain_knowledge_accuracy + basic_factual_accuracy (task×metric) · glm-5.2
- edubench · QG × domain_knowledge_accuracy + basic_factual_accuracy (task×metric) · minimax-m2.7
- edubench · QG × domain_knowledge_accuracy + basic_factual_accuracy (task×metric) · minimax-m3
- edubench · QG × domain_knowledge_accuracy + basic_factual_accuracy (task×metric) · qwen-qwen3-5-4b
- edubench · QG × domain_knowledge_accuracy + basic_factual_accuracy (task×metric) · qwen-qwen3-8-27b
- edubench · TMG/PCC × clarity_concision_inspiration + scenario_element_integration (task×metric) · deepseek-v4-pro
- edubench · TMG/PCC × clarity_concision_inspiration + scenario_element_integration (task×metric) · doubao-seed-2-0-pro
- edubench · TMG/PCC × clarity_concision_inspiration + scenario_element_integration (task×metric) · glm-5.2
- edubench · TMG/PCC × clarity_concision_inspiration + scenario_element_integration (task×metric) · minimax-m2.7
- edubench · TMG/PCC × clarity_concision_inspiration + scenario_element_integration (task×metric) · minimax-m3

