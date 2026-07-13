# K12Vista

**一句话**：3.3 万道中文 K12 图文学科题（数理化生地 × 小初高，选择/填空/问答），必须先读懂学科图再多步推理——P04（复杂多模态理解）的第一个直接测量，也是中文多模态的补位。

## 出处与背景

- Li et al. 2025, *K12Vista*（arXiv:2506.01676），官方仓库 github.com/lichongod/K12Vista，数据 `lipku1999/K12-Vista`（公开，无 gate）。
- 接入动机：P04 在测量模型 v1 里是四个完全空白的 P 之一（`model_type: undeclared`，零格子）。缺口推荐文档（2026-07-11）把 K12Vista 列为首选，理由是中文、公开有标签、静态图文、接入成本与 mathvista 同级。

## 数据

- `fetch_eval_datasets.py --benchmark k12vista` → 克隆官方仓库（要 `K12_Vista/code/prompt.py`）+ 下 `K12_Vista.jsonl`（33,660 行 / 501 MB）。
- **图是 base64 内嵌在 `img` 字段的**，没有单独的图片包——省了配图这一步。
- `build_k12vista_sample.py --size 300` 生成**固定题单** `data/k12vista/item_list_v1.txt`：按 `题型 × 学科 × 难度` 分层（121 个层，按人口比例分配、每层至少 1 题），解码出图片到 `sources/datasets/k12vista/images/`，并写一份去掉 base64 的瘦身 jsonl。所有模型跑同一份题。
- 抽样构成：选择题 104 / 填空题 97 / 问答题 99；11 个学科-学段各 23-31 题；难度 难 164 / 较难 72 / 中 38 / 较易 25 / 易 1（**79% 是难或较难**——这是人口本身的分布，不是我们挑的）。

## 任务与判分

- **提示词照搬官方** `prompt.py::infer_prompt['directly_infer_prompt'][题型]`（三种题型三套）。官方 runner 会把题干里的 `<image>` 占位符删掉、把图放在文本**前面**（`models/vllminfer.py`），我们一致。
- **判分照搬官方** `eval_prompt['directly_eval_prompt'][题型]`：裁判逐空提取参考答案与学生答案，输出 `<evaluation>[[参考],[学生],[0/1 列表]]</evaluation>`，**题分 = 各空得分均值**（多空题部分给分，见 `models/K12_PEM_judgemodel.py`）。
- 表头 `accuracy` = 严格全对率（所有空都对）；官方口径的部分给分均值在 `extra_metrics.official_score`，`score_10` = 10× 它，供能力聚合用。按题型/学科/学段/难度分桶。

## 在本仓库怎么用

```bash
/home/likefallwind/miniconda3/bin/python scripts/eval/data/fetch_eval_datasets.py --benchmark k12vista   # 一次性
/home/likefallwind/miniconda3/bin/python scripts/eval/data/build_k12vista_sample.py --size 300           # 一次性，固定题单
MODEL=MiniMax-M3 ./scripts/run_eval.sh k12vista        # 被测模型必须是视觉模型
MODEL=doubao-seed-2.0-pro K12VISTA_JUDGE_MODEL=MiniMax-M3 ./scripts/run_eval.sh k12vista
```

## 局限与注意

- **裁判不是官方那一个**。官方判分用 GPU 部署的 Qwen2.5-VL-72B 或微调的 K12-PEM，本地起不来；这里换成 API 裁判（`K12VISTA_JUDGE_MODEL`，默认 `MiniMax-M3`）。rubric 原文一字未改，但**裁判模型本身没有拿人工金标校准过**，报告里必须直说，不能声称与官方榜单可比。
- 裁判只看文本（题干、标准答案、解析、学生作答），不看图——官方也是这样，所以裁判不需要视觉能力。
- **模型面天然受限：主测 5 个模型里只有 2 个能看图**。2026-07-13 用真实题图逐个探测的结果——能看图：`MiniMax-M3`、`doubao-seed-2.0-pro`、`doubao-seed-2.0-lite`、`kimi-k2.6`；不能看图：`MiniMax-M2.7`（纯文本）、`glm-5.2`（网关 400）、`deepseek-v4-pro`。
- **`deepseek-v4-pro` 是个陷阱**：收到图片不报错、返回 200，然后回一句"你没有上传图片"照样作答。跑之前不探测的话，会静默产出一堆瞎猜的分数而判分链路毫无警告。**文本模型在 K12Vista 上必须标"不适用"，绝不能记 0 分**——那是测量假象不是能力差距。
- 建议模型面：`MiniMax-M3` + `doubao-seed-2.0-pro`（主测 5 中的两个）+ `doubao-seed-2.0-lite` + `kimi-k2.6`（补充档），凑够 4 个模型，13 号检查的跨模型相关才有最低样本量（≥3）。
- 只跑 300 题抽样，不跑全量 33k：预算约束，且分层已覆盖全部 121 个层。抽样误差要在报告里带上（bootstrap CI）。

## 当前映射

- 提案：k12vista → **P04 0.55 / P06 0.30 / P05 0.15**，diagnostic，weight 0.80。理由：图文接地的深理解是主成分，解题推理与学科知识各占一部分。
- **权重未定，已登记为 R15 进 M3 裁决**（争点：是 P04 还是 P03、裁判未校准要不要降 evidence_tier、要不要补 P03 小权重）。测量模型 v1 是预注册文件，P04 的格子留给 v2 声明，此次不动 v1。
