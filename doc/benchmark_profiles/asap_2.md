# ASAP 2.0

**一句话**：英文学生作文自动评分——给模型一篇作文，让它按 rubric 打整体分，和人类评分员比一致性。

## 出处与背景

- Kaggle "Learning Agency Lab – Automated Essay Scoring 2.0" 竞赛（2024），是 2012 年 Hewlett 基金会 ASAP-AES 的续作；https://www.kaggle.com/competitions/learning-agency-lab-automated-essay-scoring-2
- 动机：ASAP 2012 老化且泄露严重，2.0 换了新的学生作文集（约 24,000 篇，6-12 年级议论文），整体分 1-6。

## 数据

- 约 24k 篇真实学生作文，英文，holistic 1-6 分。
- **获取状态：Kaggle manual required（gated）**——本地无原始数据，仓库口径里记为证据缺口。

## 任务与判分

- 模型读作文 + rubric，输出整体分；指标 **QWK**（二次加权 Kappa，对"差得远的错"惩罚更重）。
- 无官方"模型 leaderboard"——它本来是训练竞赛，拿来测 LLM zero-shot 评分是社区用法。

## 在本仓库怎么用

- **无 adapter**，分数来自同事跑分（`otherbenchmark/`，`ASAP+Peda.png`），QWK 归一到 0-10。

## 局限与注意

- **区分度（13 号实测）**：n=7，均分 5.45，标准差 0.51 → **没有天花板问题**，是教育核心类里区分度最好的格子之一。
- LLM zero-shot QWK 天然偏低（人类评分员间 QWK 约 0.7-0.8），分数解释要对照人类基线。
- 只有整体分没有 trait 分，测不了细粒度评分能力（ELLIPSE/EssayJudge 才有多维，见缺口推荐）。

## 当前映射

- P14 rubric 评分 0.65 / P02 证据定位 0.20 / P05 0.15；education_core。
- 构念核对：P02 挂载属于搭车（R9）；P14 拆分后归"学业作答评分"facet（R3）。
