# 评测进度总览（截至 2026-06-27）

本文件汇总 `scripts/eval/` 逐基准评测框架（输出在 `reports/eval/<benchmark>/<model-slug>/`）目前的运行情况：做了哪些评测、各自跑了哪些模型、进度如何。

> 口径说明
> - **数据来源**：各 `summary.json`，指标取自其中的 `accuracy` / 专用 headline 字段。
> - **进度判定**：以 `scored`（已评分条目数）对照该基准的满量规模。`full` = 接近满量；`部分` = 明显少于满量但非冒烟；`冒烟` = 1–50 条的 smoke test；`失败/空` = scored=0 或目录为空。
> - **不可跨基准平均**：不同基准的 accuracy 不可直接比较或求平均，需先映射到 D01–D24 能力维度（见 README 解读护栏）。
> - 默认 answer-extraction 模型为 `MiniMax-M2.7`，除非另注。

---

## 一、模型清单

目前在评测中出现过的被测模型（candidate model）：

| 模型 | 提供方/通道 |
| --- | --- |
| MiniMax-M3 | MiniMax（视觉/推理，框架默认被测+常用判官） |
| MiniMax-M2.7 | MiniMax（默认抽取器，纯文本） |
| deepseek-v4-pro / deepseek-v4-flash | gateway（或 DeepSeek 官方 API） |
| deepseek-v3.2 | gateway（多作判官） |
| doubao-seed-2.0-pro / doubao-seed-2.0-lite | gateway |
| glm-5.1 / glm-5.2 | gateway |
| gpt-5.5 | gateway |
| opus-4.8 | 本助手（仅 eduillustrate 直评判官） |

---

## 二、各基准完成度速览

| 基准 | 能力维度 | 满量规模 | 已跑模型数 | 完成度 |
| --- | --- | --- | --- | --- |
| mmlu_pro | D01 | 12,032 | 5（仅 MiniMax-M3 满量） | 1 full + 4 冒烟 |
| agieval | D03 | ~7,272 | 1 | full（MiniMax-M3） |
| ceval | D01 | 1,346(val) | 2（仅 MiniMax-M3 满量） | 1 full + 1 冒烟 |
| olympiadbench | D05 | 6,728 | 1 | full（MiniMax-M3） |
| mathvista | D06 | 1,000 | 1 | full（MiniMax-M3） |
| eduguard_sata | D21 | 5,270 | 8 | 5 full + 1 部分 + 2 失败 |
| eduguard_adversarial | D21 | 801 | 7 | 全部 full（另有备用判官副本） |
| mathtutorbench_*（9 任务 + 判官标定） | D11–D13 等 | 各异 | 见下表 | 大部分 full |
| mrbench_judge | D11/D12/D13 | ~13,240 | 2 | 全部 full |
| mrbench_tutor | D11/D12/D13 | — | 1 | 冒烟 |
| bea2025_judge | D11/D12/D13 | ~9,904 | 2 | 1 full + 1 冒烟 |
| bea2025_tutor | D11/D12/D13 | — | 0 | 目录空（未跑） |
| mmtutorbench | 多模态数学辅导 | 770 | 1 | 冒烟 |
| mmtutorbench_judge_calibration | — | — | 1 | hook（无人工 gold，仅状态） |
| eduillustrate | D06/D11 | 230 | 见下表 | 2 个满量生成 + 多个判官对比冒烟 |

---

## 三、C1 知识/推理类（gate items）

| 基准 | 模型 | Accuracy | scored | 状态 |
| --- | --- | --- | --- | --- |
| mmlu_pro | MiniMax-M3 | 85.6% | 12,032 | full |
| mmlu_pro | glm-5.1 | (100%) | 5 | 冒烟 |
| mmlu_pro | doubao-seed-2.0-lite | (100%) | 5 | 冒烟 |
| mmlu_pro | doubao-seed-2.0-pro | (80%) | 5 | 冒烟 |
| mmlu_pro | gpt-5.5 | (100%) | 1 | 冒烟 |
| agieval | MiniMax-M3 | 85.6% | 7,268 | full |
| ceval | MiniMax-M3 | 88.3% | 1,346 | full（val 全集） |
| ceval | glm-5.1 | (100%) | 5 | 冒烟 |
| olympiadbench | MiniMax-M3 | 71.6% | 6,722 | full |
| mathvista | MiniMax-M3 | 84.1% | 993 | full |

> 注：括号内的小样本 accuracy 仅来自 ≤5 条冒烟，不具统计意义。MMLU-Pro 除 MiniMax-M3 外其余模型仅做了流程冒烟。

---

## 四、D21 安全类（EduGuard-Bench）

### eduguard_sata（Select-All-That-Apply，规则评分，满量 5,270）

| 模型 | RFS/Accuracy | scored | 状态 |
| --- | --- | --- | --- |
| deepseek-v4-pro | 70.4% | 5,266 | full |
| doubao-seed-2.0-pro | 70.1% | 5,270 | full |
| doubao-seed-2.0-lite | 69.2% | 5,270 | full |
| gpt-5.5 | 68.9% | 2,148 | 部分 |
| glm-5.2 | 65.4% | 5,270 | full |
| deepseek-v4-flash | — | 4 | 冒烟 |
| glm-5.1 | null | 0 | 失败/空 |
| MiniMax-M3 | null | 0 | 失败/空 |

### eduguard_adversarial（越狱对抗，两段式 LLM-as-judge，满量 801）

数值为「安全得分」（越高越安全）。默认判官 MiniMax-M2.7；另有一套用 deepseek-v3.2 作判官的副本（`_judge-deepseek-v3.2/`）。

| 模型 | 安全分(默认判官) | 安全分(deepseek 判官) | scored | 状态 |
| --- | --- | --- | --- | --- |
| MiniMax-M3 | 96.5% | 91.8% | 801 | full |
| gpt-5.5 | 95.1%(判官 M3) | 99.6% | 797 | full |
| glm-5.1 | 90.0% | 95.1% | 772 | full |
| glm-5.2 | 79.2% | 71.5% | 801 | full |
| doubao-seed-2.0-lite | 54.6% | 48.8% | 801 | full |
| doubao-seed-2.0-pro | 48.6% | 39.7% | 801 | full |
| deepseek-v4-pro | 42.8% | 37.5% | 801 | full |

> 判官切换会明显改变排名/绝对值（如 doubao、deepseek 系列），结论需注明判官。另有 doubao 自评判官备份（`selfjudge_backup_*`）。

---

## 五、D11–D13 教学/辅导类

### mathtutorbench（多任务）

| 任务 | 满量 | 已跑模型（accuracy/win-rate） |
| --- | --- | --- |
| judge_calibration | 964 | glm-5.2 83.9% · deepseek-v3.2 83.6% · deepseek-v4-flash 82.6% · deepseek-v4-pro 81.7% · MiniMax-M2.7 81.0% · MiniMax-M3 84.4%（均 full） |
| pedagogy | 1,150 | deepseek-v4-pro 77.2% · doubao-pro 77.1% · doubao-lite 75.2% · deepseek-v4-flash 71.0% · glm-5.2 55.4%（均 full） |
| pedagogy_hard | 327 | deepseek-v4-pro 77.1% · doubao-pro 76.5% · glm-5.2 74.3% · doubao-lite 67.3% · deepseek-v4-flash 63.3%（均 full） |
| scaffolding | 1,150 | glm-5.2 51.0% · deepseek-v4-pro 28.4% · doubao-pro 25.9% · doubao-lite 20.3% · deepseek-v4-flash 2.5%；MiniMax-M3 仅冒烟(5) |
| scaffolding_hard | 327 | glm-5.2 46.2% · deepseek-v4-pro 33.6% · doubao-pro 21.4% · doubao-lite 15.0% · deepseek-v4-flash 12.8%（均 full） |
| mistake_location | 2,004 | MiniMax-M3 77.5%（full） |
| mistake_correction | 1,002 | MiniMax-M3 87.3%（full） |
| solution_correctness | 2,004 | MiniMax-M3 87.7%（full） |
| socratic | — | MiniMax-M3 冒烟(3) |

> MiniMax-M3 只在 location/correction/solution_correctness 跑了满量；scaffolding/socratic 仍是冒烟。gateway 系模型（deepseek/doubao/glm）覆盖了 pedagogy/scaffolding/judge_calibration 全集，但缺 location/correction/socratic。

### MRBench（NAACL 2025）

| 任务 | 模型 | 指标 | scored | 状态 |
| --- | --- | --- | --- | --- |
| mrbench_judge（判官标定，被测模型即判官） | MiniMax-M3 | 65.3% 一致率 | 13,238 | full |
| mrbench_judge | deepseek-v3.2 | 51.5% 一致率 | 13,240 | full |
| mrbench_tutor（生成+固定判官） | MiniMax-M3 | — | 4 | 冒烟 |

### BEA 2025 shared task

| 任务 | 模型 | 指标 | scored | 状态 |
| --- | --- | --- | --- | --- |
| bea2025_judge（被测=判官） | deepseek-v3.2 | exact 43.2% / rec_judge 0.369 | 9,904 | full |
| bea2025_judge | MiniMax-M3 | exact 45.0% / rec_judge 0.323 | 20 | 冒烟 |
| bea2025_tutor | — | — | 0 | 目录空，未运行 |

> 仅用 dev 做本地评分；test 标签本地隐藏，不可声称与官方 BEA leaderboard 等价。

---

## 六、多模态教学/插图类

### mmtutorbench（多模态数学辅导，满量 770）

| 任务 | 模型 | 状态 |
| --- | --- | --- |
| mmtutorbench | MiniMax-M3（judge=MiniMax-M3） | 冒烟(5)，尚未满量 |
| mmtutorbench_judge_calibration | MiniMax-M3 | hook only：公开 JSONL 无人工 gold，仅输出状态 |

### eduillustrate（STEM 图示生成+讲解，arXiv:2604.05005，满量 230）

8 维 0–5 Likert，逐题几何平均，基准级算术平均。判官为替代 provider，非论文原用 Gemini 3.0 Pro，分数仅供内部对比。

| 生成模型 | 判官 | 规模 | overall mean | 状态 |
| --- | --- | --- | --- | --- |
| MiniMax-M3 | MiniMax-M3 | 230 | 3.175 | 满量生成 |
| doubao-seed-2.0-lite | MiniMax-M3 | 230 | 2.652 | 满量生成 |
| MiniMax-M3 | opus-4.8（本助手直评） | 5 | 2.972 | 判官对比冒烟 |
| MiniMax-M3 | MiniMax-M3 | 5 | 2.932 | 判官对比冒烟 |
| MiniMax-M3 | doubao-seed-2.0-lite | 5 | 2.898 | 判官对比冒烟 |
| MiniMax-M3 | deepseek-v3.2 | 5 | 2.824 | 判官对比冒烟 |
| MiniMax-M3 | doubao-seed-2.0-pro | 5 | 2.501 | 判官对比冒烟 |

> eduillustrate 上多数小样本是「固定生成、换判官」的判官一致性对比；只有 MiniMax-M3 与 doubao-lite 两个生成模型跑了 230 满量。

---

## 七、缺口与待办（建议）

- **被测模型覆盖不均**：知识类（mmlu_pro/agieval/ceval/olympiadbench/mathvista）几乎只有 MiniMax-M3 满量，其余模型仅冒烟；如要横向对比需补跑 gateway 系模型满量。
- **失败需重跑**：`eduguard_sata` 的 glm-5.1、MiniMax-M3 为 scored=0；`gpt-5.5` 仅 2,148/5,270（部分）。
- **冒烟待扩量**：mrbench_tutor、bea2025_judge(MiniMax-M3)、mmtutorbench、mathtutorbench 的 scaffolding/socratic(MiniMax-M3)。
- **未启动**：bea2025_tutor 目录为空。
- **判官口径**：eduguard_adversarial、eduillustrate、mrbench/bea 系判官切换显著影响结论，报告中务必标注判官身份；判官标定（mathtutorbench/mrbench_judge）本身是「模型即判官」实验，勿与被测能力混淆。
- `reports/eval/_aggregate/index.md` 已过期（2026-06-16，仅含早期小样本），建议重生成。
