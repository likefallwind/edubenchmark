# IFEval

**一句话**：541 条带可机器验证硬约束的指令（字数、格式、关键词、大小写等），官方规则代码判分——P01（指令与约束遵循）的第一个直接测量。

## 出处与背景

- Zhou et al. 2023, *Instruction-Following Evaluation for Large Language Models*（arXiv:2311.07911），google-research 官方实现，Apache-2.0。
- 接入动机（R13/R14）：edubench 裁判打的"指令遵循"分与知识指标在模型排名上信息重合（同源模型级 ρ≈0.96），且换裁判后不稳健——P01 的直接测量必须走规则判分。

## 数据

- `fetch_eval_datasets.py --benchmark ifeval` → `sources/datasets/ifeval/data/input_data.jsonl`（541 条）+ 官方 checker 四个模块 vendored 到 `sources/datasets/ifeval/instruction_following_eval/`。
- 判分依赖 nltk / langdetect / immutabledict / absl-py（miniconda python 已装；fetch 时自动下 nltk punkt）。

## 任务与判分

- 每条 prompt 带 `instruction_id_list` + `kwargs`（约 25 种指令类型）；无裁判、无抽取 LLM，直接对原始回复跑官方检查。
- headline = 官方 **prompt 级 strict accuracy**（一条 prompt 的全部指令在原始回复上全部满足）；`extra_metrics` 含 prompt-loose / instruction-strict / instruction-loose（loose 按官方 8 变体重试：去首行/尾行/去 `*`）。

## 在本仓库怎么用

```bash
/home/likefallwind/miniconda3/bin/python scripts/eval/data/fetch_eval_datasets.py --benchmark ifeval   # 一次性
MODEL=MiniMax-M3 ./scripts/run_eval.sh ifeval        # 全量 541 题，无 API 判分成本（只有答题成本）
```

## 局限与注意

- 通用指令、英文为主，不是教育语境——按 foundation_gate 挂 P01，作操作基座门槛证据，不宣称教育指令遵循。
- 部分指令（如"重复请求原文"）会让回复看起来像回显题面，是正常现象。

## 当前映射

- ifeval：P01 1.00，foundation_gate，weight 0.80；测量模型 P01/core 格子 weight 1.0（此前 P01 全是搭车格子）。
- 2026-07-12 冒烟（MiniMax-M3, LIMIT=5）：strict 5/5。全量跑分随批量启动。
