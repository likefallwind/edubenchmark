# EduBench 大模型教育能力评测实验报告 (更新版)

本报告基于 3797 个有效样本的评测数据，对 11 款参评大模型在教育场景中的综合表现进行了系统性梳理。报告分为三部分：**总体表现排名**、**按核心教育任务排名** 以及 **按评价指标维度排名**。

---

## 一、 总体表现排名 (Overall Performance)

基于所有任务和所有评价指标的综合平均分，各模型的整体表现排序如下：

| 排名 | 模型名称 | 综合得分 (Mean) | 梯队表现 |
| :--- | :--- | :--- | :--- |
| **1** | **minimax-m2.7** | **8.342** | 第一梯队 (领跑) |
| **2** | **qwen3.5-122b-a10b** | **8.249** | 第一梯队 |
| **3** | **doubao-seed-2.0-pro** | **8.228** | 第一梯队 |
| 4 | deepseek-v4-flash | 8.154 | 第二梯队 |
| 5 | claude-sonnet-4-6 | 8.112 | 第二梯队 |
| 6 | minimax-m3 | 8.069 | 第二梯队 |
| 7 | doubao-seed-2.0-lite | 8.037 | 第二梯队 |
| 8 | deepseek-v4-pro | 8.013 | 第三梯队 |
| 9 | kimi-k2.6 | 7.901 | 第三梯队 |
| 10 | glm-5.1 | 7.681 | 第三梯队 |
| 11 | qwen3-14b | 7.470 | 第三梯队 |

> **💡 总体洞察：**
> * `minimax-m2.7` 依然以 8.342 的得分稳居榜首。
> * 新加入的 `doubao-seed-2.0-pro` 表现强势，以 8.228 的高分空降第三名，成功跻身第一梯队。
> * 另一款新加入的国际旗舰模型 `claude-sonnet-4-6` 综合得分为 8.112，位列第五，展现出扎实的教育场景适应能力。

---

## 二、 按核心教育任务排名 (Task Breakdown)

以下是 11 款模型在 5 个核心教育任务（IP, PCC, PLS, QG, TMG）上的平均得分及排名。

### 1. 启发式解答 (IP - Idea Provision)
| 排名 | 模型 | 得分 |
| :--- | :--- | :--- |
| 1 | doubao-seed-2.0-pro | 8.665 |
| 2 | minimax-m3 | 8.620 |
| 3 | claude-sonnet-4-6 | 8.502 |
| 4 | qwen3.5-122b-a10b | 8.388 |
| 5 | doubao-seed-2.0-lite | 8.332 |
| 6 | minimax-m2.7 | 8.210 |
| 7 | deepseek-v4-pro | 8.202 |
| 8 | deepseek-v4-flash | 8.156 |
| 9 | kimi-k2.6 | 7.983 |
| 10 | qwen3-14b | 7.800 |
| 11 | glm-5.1 | 7.598 |

### 2. 个性化内容生成 (PCC - Personalized Content Creation)
| 排名 | 模型 | 得分 |
| :--- | :--- | :--- |
| 1 | doubao-seed-2.0-pro | 9.535 |
| 2 | deepseek-v4-flash | 9.467 |
| 3 | doubao-seed-2.0-lite | 9.206 |
| 4 | claude-sonnet-4-6 | 9.177 |
| 5 | minimax-m3 | 9.131 |
| 6 | kimi-k2.6 | 8.854 |
| 7 | minimax-m2.7 | 8.609 |
| 8 | glm-5.1 | 8.432 |
| 9 | deepseek-v4-pro | 8.428 |
| 10 | qwen3.5-122b-a10b | 8.319 |
| 11 | qwen3-14b | 7.676 |

### 3. 个性化学习支持 (PLS - Personalized Learning Support)
| 排名 | 模型 | 得分 |
| :--- | :--- | :--- |
| 1 | doubao-seed-2.0-pro | 9.437 |
| 2 | deepseek-v4-flash | 9.194 |
| 3 | doubao-seed-2.0-lite | 9.128 |
| 4 | claude-sonnet-4-6 | 9.081 |
| 5 | minimax-m3 | 8.905 |
| 6 | kimi-k2.6 | 8.899 |
| 7 | minimax-m2.7 | 8.806 |
| 8 | deepseek-v4-pro | 8.591 |
| 9 | qwen3.5-122b-a10b | 8.348 |
| 10 | glm-5.1 | 8.089 |
| 11 | qwen3-14b | 7.694 |

### 4. 题目生成 (QG - Question Generation)
| 排名 | 模型 | 得分 |
| :--- | :--- | :--- |
| 1 | minimax-m3 | 8.956 |
| 2 | deepseek-v4-flash | 8.912 |
| 3 | claude-sonnet-4-6 | 8.887 |
| 4 | doubao-seed-2.0-pro | 8.865 |
| 5 | doubao-seed-2.0-lite | 8.627 |
| 6 | qwen3.5-122b-a10b | 8.547 |
| 7 | kimi-k2.6 | 8.534 |
| 8 | minimax-m2.7 | 8.508 |
| 9 | glm-5.1 | 8.137 |
| 10 | deepseek-v4-pro | 7.925 |
| 11 | qwen3-14b | 7.324 |

### 5. 教学材料生成 (TMG - Teaching Material Generation)
| 排名 | 模型 | 得分 |
| :--- | :--- | :--- |
| 1 | deepseek-v4-flash | 9.231 |
| 2 | doubao-seed-2.0-pro | 9.197 |
| 3 | claude-sonnet-4-6 | 8.966 |
| 4 | doubao-seed-2.0-lite | 8.846 |
| 5 | kimi-k2.6 | 8.810 |
| 6 | minimax-m3 | 8.670 |
| 7 | minimax-m2.7 | 7.889 |
| 8 | deepseek-v4-pro | 7.581 |
| 9 | qwen3.5-122b-a10b | 7.563 |
| 10 | qwen3-14b | 7.014 |
| 11 | glm-5.1 | 6.178 |

> **💡 任务洞察：**
> * 新加入的 `doubao-seed-2.0-pro` 在 `IP` (启发式解答)、`PCC` (个性化内容生成) 和 `PLS` (个性化学习支持) 三大核心任务中强势登顶，展现了极具统治力的教育内容生成和路径规划能力。
> * `minimax-m3` 继续在 `QG` (题目生成) 任务中保持全场第一。
> * `deepseek-v4-flash` 在 `TMG` (教学材料生成) 中依然保持领先。

---

## 三、 按评价指标维度排名 (Metric Analysis)

### 1. 基础事实准确性 (Basic Factual Accuracy)
| 排名 | 模型 | 得分 |
| :--- | :--- | :--- |
| 1 | deepseek-v4-flash | 9.656 |
| 2 | minimax-m2.7 | 9.342 |
| 3 | claude-sonnet-4-6 | 9.290 |
| 4 | minimax-m3 | 9.277 |
| 5 | doubao-seed-2.0-pro | 9.251 |
| 6 | kimi-k2.6 | 9.226 |
| 7 | doubao-seed-2.0-lite | 9.133 |
| 8 | qwen3.5-122b-a10b | 8.953 |
| 9 | deepseek-v4-pro | 8.759 |
| 10 | qwen3-14b | 8.646 |
| 11 | glm-5.1 | 8.622 |

### 2. 领域知识准确性 (Domain Knowledge Accuracy)
| 排名 | 模型 | 得分 |
| :--- | :--- | :--- |
| 1 | deepseek-v4-flash | 9.358 |
| 2 | doubao-seed-2.0-pro | 9.351 |
| 3 | claude-sonnet-4-6 | 9.191 |
| 4 | minimax-m3 | 9.155 |
| 5 | doubao-seed-2.0-lite | 9.041 |
| 6 | kimi-k2.6 | 8.930 |
| 7 | minimax-m2.7 | 8.438 |
| 8 | qwen3.5-122b-a10b | 8.281 |
| 9 | deepseek-v4-pro | 8.224 |
| 10 | glm-5.1 | 8.043 |
| 11 | qwen3-14b | 7.524 |

### 3. 指令遵循 (Instruction Following)
| 排名 | 模型 | 得分 |
| :--- | :--- | :--- |
| 1 | deepseek-v4-flash | 9.589 |
| 2 | doubao-seed-2.0-pro | 9.474 |
| 3 | claude-sonnet-4-6 | 9.447 |
| 4 | minimax-m3 | 9.442 |
| 5 | minimax-m2.7 | 9.363 |
| 6 | doubao-seed-2.0-lite | 9.325 |
| 7 | kimi-k2.6 | 9.284 |
| 8 | qwen3.5-122b-a10b | 9.106 |
| 9 | deepseek-v4-pro | 8.596 |
| 10 | qwen3-14b | 8.333 |
| 11 | glm-5.1 | 7.084 |

### 4. 错误识别与纠正准确性 (Error Identification Correction Accuracy)
| 排名 | 模型 | 得分 |
| :--- | :--- | :--- |
| 1 | minimax-m2.7 | 9.350 |
| 2 | qwen3.5-122b-a10b | 9.265 |
| 3 | deepseek-v4-pro | 8.961 |
| 4 | glm-5.1 | 8.640 |
| 5 | qwen3-14b | 8.459 |
| 6 | doubao-seed-2.0-lite | 6.380 |
| 7 | doubao-seed-2.0-pro | 6.319 |
| 8 | deepseek-v4-flash | 6.298 |
| 9 | kimi-k2.6 | 6.204 |
| 10 | claude-sonnet-4-6 | 6.074 |
| 11 | minimax-m3 | 5.988 |

### 5. 场景元素整合 (Scenario Element Integration)
| 排名 | 模型 | 得分 |
| :--- | :--- | :--- |
| 1 | minimax-m2.7 | 8.378 |
| 2 | qwen3.5-122b-a10b | 8.378 |
| 3 | deepseek-v4-pro | 8.169 |
| 4 | glm-5.1 | 7.671 |
| 5 | doubao-seed-2.0-pro | 7.554 |
| 6 | doubao-seed-2.0-lite | 7.532 |
| 7 | deepseek-v4-flash | 7.464 |
| 8 | claude-sonnet-4-6 | 7.395 |
| 9 | minimax-m3 | 7.375 |
| 10 | kimi-k2.6 | 7.374 |
| 11 | qwen3-14b | 7.234 |

### 6. 内容相关性与范围控制 (Content Relevance Scope Control)
| 排名 | 模型 | 得分 |
| :--- | :--- | :--- |
| 1 | deepseek-v4-flash | 9.628 |
| 2 | doubao-seed-2.0-pro | 9.469 |
| 3 | claude-sonnet-4-6 | 9.391 |
| 4 | minimax-m3 | 9.367 |
| 5 | doubao-seed-2.0-lite | 9.316 |
| 6 | kimi-k2.6 | 9.284 |
| 7 | minimax-m2.7 | 9.139 |
| 8 | qwen3.5-122b-a10b | 8.983 |
| 9 | deepseek-v4-pro | 8.856 |
| 10 | glm-5.1 | 8.597 |
| 11 | qwen3-14b | 8.496 |

### 7. 表达清晰度与启发性 (Clarity, Concision, Inspiration)
| 排名 | 模型 | 得分 |
| :--- | :--- | :--- |
| 1 | deepseek-v4-flash | 8.691 |
| 2 | minimax-m2.7 | 8.622 |
| 3 | claude-sonnet-4-6 | 8.594 |
| 4 | minimax-m3 | 8.560 |
| 5 | doubao-seed-2.0-pro | 8.506 |
| 6 | doubao-seed-2.0-lite | 8.449 |
| 7 | kimi-k2.6 | 8.414 |
| 8 | qwen3.5-122b-a10b | 8.377 |
| 9 | deepseek-v4-pro | 8.196 |
| 10 | qwen3-14b | 7.924 |
| 11 | glm-5.1 | 7.825 |

### 8. 推理过程严密性 (Reasoning Process Rigor)
| 排名 | 模型 | 得分 |
| :--- | :--- | :--- |
| 1 | doubao-seed-2.0-pro | 8.953 |
| 2 | minimax-m3 | 8.701 |
| 3 | claude-sonnet-4-6 | 8.668 |
| 4 | doubao-seed-2.0-lite | 8.539 |
| 5 | deepseek-v4-flash | 8.293 |
| 6 | minimax-m2.7 | 8.200 |
| 7 | qwen3.5-122b-a10b | 8.159 |
| 8 | kimi-k2.6 | 8.138 |
| 9 | deepseek-v4-pro | 7.936 |
| 10 | glm-5.1 | 7.736 |
| 11 | qwen3-14b | 7.100 |

### 9. 语气与风格一致性 (Tone Style Consistency)
| 排名 | 模型 | 得分 |
| :--- | :--- | :--- |
| 1 | qwen3.5-122b-a10b | 8.725 |
| 2 | minimax-m2.7 | 8.724 |
| 3 | doubao-seed-2.0-pro | 8.565 |
| 4 | deepseek-v4-pro | 8.552 |
| 5 | claude-sonnet-4-6 | 8.538 |
| 6 | minimax-m3 | 8.504 |
| 7 | deepseek-v4-flash | 8.463 |
| 8 | doubao-seed-2.0-lite | 8.427 |
| 9 | kimi-k2.6 | 8.352 |
| 10 | glm-5.1 | 8.320 |
| 11 | qwen3-14b | 8.081 |

### 10. 高阶思维能力培养 (Higher Order Thinking Ability Development)
| 排名 | 模型 | 得分 |
| :--- | :--- | :--- |
| 1 | doubao-seed-2.0-pro | 8.496 |
| 2 | minimax-m3 | 8.013 |
| 3 | claude-sonnet-4-6 | 7.978 |
| 4 | deepseek-v4-flash | 7.766 |
| 5 | doubao-seed-2.0-lite | 7.754 |
| 6 | kimi-k2.6 | 7.304 |
| 7 | qwen3.5-122b-a10b | 7.289 |
| 8 | glm-5.1 | 7.094 |
| 9 | deepseek-v4-pro | 7.033 |
| 10 | minimax-m2.7 | 6.888 |
| 11 | qwen3-14b | 6.174 |

### 11. 动机引导与正向反馈 (Motivation Guidance Positive Feedback)
| 排名 | 模型 | 得分 |
| :--- | :--- | :--- |
| 1 | minimax-m2.7 | 6.923 |
| 2 | qwen3.5-122b-a10b | 6.758 |
| 3 | glm-5.1 | 6.444 |
| 4 | deepseek-v4-pro | 6.440 |
| 5 | claude-sonnet-4-6 | 6.424 |
| 6 | doubao-seed-2.0-pro | 6.363 |
| 7 | deepseek-v4-flash | 6.357 |
| 8 | minimax-m3 | 6.318 |
| 9 | doubao-seed-2.0-lite | 6.243 |
| 10 | kimi-k2.6 | 6.125 |
| 11 | qwen3-14b | 6.125 |

### 12. 个性化适应与学习支持 (Personalized Adaptation Learning Support)
| 排名 | 模型 | 得分 |
| :--- | :--- | :--- |
| 1 | minimax-m2.7 | 6.743 |
| 2 | qwen3.5-122b-a10b | 6.717 |
| 3 | deepseek-v4-pro | 6.439 |
| 4 | doubao-seed-2.0-pro | 6.431 |
| 5 | claude-sonnet-4-6 | 6.355 |
| 6 | doubao-seed-2.0-lite | 6.305 |
| 7 | deepseek-v4-flash | 6.287 |
| 8 | kimi-k2.6 | 6.181 |
| 9 | minimax-m3 | 6.126 |
| 10 | glm-5.1 | 6.100 |
| 11 | qwen3-14b | 5.547 |

---
*生成日期：2026-06-25*