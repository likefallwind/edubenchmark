# AI-教育 Benchmark 调研仓库

本仓库用于整理 AI-教育领域 benchmark、评测尺度、公开效果、可获得数据集，以及一版可追溯的“原子能力-评价标准-题目出处”benchmark 规格。当前工作重点是信息收集、统一尺度建设和题目出处索引，不是重新跑模型实验。

## 目标

对应 `todo.md`，本仓库要形成一个可复用的 AI-教育 benchmark 证据库：

- 收集 AI-教育领域已有 benchmark / 数据资源。
- 记录每个 benchmark 测什么问题、使用什么原生指标、是否有公开模型结果。
- 下载或登记可获得的数据集，并区分自动下载、人工申请、论文待发布等状态。
- 基于已有原子尺度，形成统一的 AI-教育应用评测框架。
- 当给定一个新的 AI-教育应用时，可以快速判断相似领域已有评测、推荐重点指标和补充评测方式。

## 当前状态

截至 2026-05-18，仓库里有两层成果：

1. **调研证据库**：覆盖 AI-教育相关 benchmark / 数据资源、指标、公开结果、数据下载状态。
2. **Benchmark v1 规格**：把 8 个一级尺度、D01-D24 原子能力、84 个细粒度评价标准和 840 条本地题目/任务样本串起来。

调研证据库状态：

- 覆盖 78 个 benchmark / 数据资源。
- 抽取 165 个指标。
- 整理 1616 条公开模型/结果记录。
- 覆盖 24 个原子能力。
- 收敛为 8 个一级评测尺度。
- 已下载 GitHub / HuggingFace 可直接获取的大部分数据集。

Benchmark v1 状态：

- 8 个一级尺度。
- 24 个原子能力。
- 84 个评价标准。
- 840 条评测题/任务样本。
- 每条题都有 `source_file` 和 `source_row_or_key`，可追溯到本地数据源。
- 抽题逻辑不是固定取前 10 条，而是每个评价标准先取最多 80 条候选，再按 `quality_score` 选择前 10 条。
- 27 个评价标准标为 `coverage_gap` / proxy 样本，表示本地有可构造任务材料，但仍缺原生 benchmark 标签、授权数据、视频/图像资源或产品级日志。

仍未完全补齐的部分主要是访问权限问题：

- `ASAP-AES` 和 `ASAP-SAS` 需要 Kaggle 账号、API token 和竞赛条款确认。
- 19 个资源属于 `manual_access_or_metadata_only`，需要人工申请、页面确认或机构授权。
- `EssayJudge` 目前是论文/待发布状态，没有可批量下载的数据包。

## 从哪里开始

推荐阅读顺序：

1. [AI_EDU_BENCHMARK_V1.md](./AI_EDU_BENCHMARK_V1.md)：根目录主入口，查看 8 个一级尺度、D01-D24 原子能力和评价标准。
2. [ai_edu_benchmark_v1_questions.json](./ai_edu_benchmark_v1_questions.json)：题目索引 JSON，查每道题的来源文件和行/键位置。
3. [AI_EDU_BENCHMARK_V1.html](./AI_EDU_BENCHMARK_V1.html)：和主 Markdown 同内容，适合浏览。
4. [reports/2026-05-18/ai_edu_benchmark_v1_spec.md](./reports/2026-05-18/ai_edu_benchmark_v1_spec.md)：更完整的 v1 规格报告。
5. [reports/2026-05-13/ai_edu_unified_benchmark_framework_2026-05-13.md](./reports/2026-05-13/ai_edu_unified_benchmark_framework_2026-05-13.md)：统一尺度、场景映射和评分建议。
6. [reports/2026-05-13/ai_edu_benchmark_catalog_2026-05-13.md](./reports/2026-05-13/ai_edu_benchmark_catalog_2026-05-13.md)：benchmark 总目录。
7. [data/exhaustive_2026-05-13/dataset_acquisition_report.md](./data/exhaustive_2026-05-13/dataset_acquisition_report.md)：数据下载 manifest。

## 主要文件说明

| 文件 / 目录 | 作用 |
|---|---|
| `AI_EDU_BENCHMARK_V1.md` | 根目录可读总览。按 S1-S8、D01-D24、评价标准组织，是当前最推荐打开的入口。 |
| `AI_EDU_BENCHMARK_V1.html` | 根目录 HTML 版总览，方便浏览表格。 |
| `ai_edu_benchmark_v1_questions.json` | 题目索引 JSON。每条题含 `item_id`、`dimension_id`、`criterion_id`、`question`、`answer_or_rubric`、`scoring_method`、`source_file`、`source_row_or_key`、`quality_score`。 |
| `data/benchmark_v1_2026-05-18/items.jsonl` | v1 题目明细，每行一道题或一个任务构造样本。适合程序读取。 |
| `data/benchmark_v1_2026-05-18/capability_criteria.jsonl` | v1 评价标准明细，每行一个标准，包含原子能力、指标族、推荐 benchmark、覆盖状态和抽样规则。 |
| `data/benchmark_v1_2026-05-18/source_manifest.jsonl` | v1 来源 manifest，说明每个来源文件是否本地存在、访问状态、抽样说明、抽到的 row/key。 |
| `reports/2026-05-18/ai_edu_benchmark_v1_spec.md` | v1 完整规格报告，内容比根目录总览更细。 |
| `reports/2026-05-18/ai_edu_benchmark_v1_spec.html` | v1 完整规格 HTML 报告。 |
| `scripts/build_benchmark_v1_2026_05_18.py` | 生成 v1 三件套和明细 JSONL 的脚本。核心逻辑是“读取 taxonomy -> 构造候选题 -> 质量排序 -> 取前 10 -> 输出 Markdown/HTML/JSON”。 |
| `data/exhaustive_2026-05-13/` | 2026-05-13 的调研证据库：benchmark、指标、公开结果、能力映射和数据获取状态。 |
| `reports/2026-05-13/` | 2026-05-13 的调研报告、统一框架、benchmark catalog。 |
| `data/benchmark_metric_dimensions_2026-05-12.json` | D01-D24 原子能力定义、相关 benchmark 和覆盖说明。 |
| `data/benchmark_metric_indicators_2026-05-12.json` | 每个原子能力下的细粒度评价指标，是 v1 评价标准的主要来源。 |
| `sources/datasets/` | 本地下载的数据集副本。已在 `.gitignore` 中，通常不提交到 git。 |
| `skills/edubenchassistant/SKILL.md` | 面向 Agent 的 EduBench Assistant skill。 |

## 目录结构

```text
.
├── data/
│   ├── benchmark_metric_dimensions_2026-05-12.json
│   ├── benchmark_metric_indicators_2026-05-12.json
│   ├── model_dimension_performance_2026-05-12.json
│   ├── benchmark_v1_2026-05-18/
│   │   ├── items.jsonl
│   │   ├── capability_criteria.jsonl
│   │   └── source_manifest.jsonl
│   └── exhaustive_2026-05-13/
│       ├── benchmarks.jsonl
│       ├── metrics.jsonl
│       ├── results.jsonl
│       ├── dimension_mapping.jsonl
│       ├── dataset_acquisition.jsonl
│       ├── dataset_acquisition_report.md
│       └── download_summary.csv
├── reports/
│   ├── 2026-05-12/
│   ├── 2026-05-13/
│   └── 2026-05-18/
├── scripts/
│   ├── build_exhaustive_2026_05_13.py
│   ├── build_benchmark_v1_2026_05_18.py
│   └── download_all_datasets.sh
├── skills/
│   └── edubenchassistant/
│       └── SKILL.md
├── sources/
│   └── datasets/
├── AI_EDU_BENCHMARK_V1.md
├── AI_EDU_BENCHMARK_V1.html
├── ai_edu_benchmark_v1_questions.json
└── todo.md
```

说明：

- `reports/` 放人可读调研报告和结论。
- `data/` 放机器可读抽取结果、下载 manifest 和日志。
- `scripts/` 放生成脚本和下载脚本。
- `skills/edubenchassistant/` 放面向 Agent 的 EduBench Assistant skill。
- `sources/` 放真实下载的数据集，已在 `.gitignore` 中，不提交到 git。

## EduBench Assistant Skill

本仓库包含一个 Agent skill：[skills/edubenchassistant/SKILL.md](./skills/edubenchassistant/SKILL.md)。

它用于在用户描述一个 AI-教育应用、产品想法或具体教学场景时，基于本仓库资料生成评测建议，并最终输出 HTML 报告。典型输出包括：

- 应重点关注哪些 D01-D24 原子能力。
- 对应哪些 S1-S8 一级尺度。
- 过去已有 benchmark 做过哪些相似评测。
- 原生指标、公开模型结果和数据集可用状态。
- 需要额外关注的安全、污染、rubric、学习效果、教师监督等问题。

本地开发安装方式：

```bash
install -D skills/edubenchassistant/SKILL.md ~/.agents/skills/edubenchassistant/SKILL.md
```

如果把本仓库发布到 GitHub，并保持 `skills/edubenchassistant/SKILL.md` 结构，可以用 Skills CLI 安装：

```bash
npx skills add <owner>/<repo>@edubenchassistant -g -y
```

示例：

```bash
npx skills add likefallwind/edubenchmark@edubenchassistant -g -y
```

常用 Skills CLI 命令：

```bash
npx skills find education benchmark
npx skills check
npx skills update
```

## 数据下载

批量下载脚本：

```bash
COMMAND_TIMEOUT=1200 ./scripts/download_all_datasets.sh
```

只重试失败项：

```bash
FAILED_ONLY=1 COMMAND_TIMEOUT=300 ./scripts/download_all_datasets.sh
```

脚本会从 `data/exhaustive_2026-05-13/dataset_acquisition_report.md` 读取下载命令，并把结果写入：

- `data/exhaustive_2026-05-13/download_summary.csv`
- `data/exhaustive_2026-05-13/dataset_download.log`

如果下载源是 Gitee HTTPS URL，脚本会自动改写为 SSH 形式，适配已有 Gitee SSH 权限。

## 重新生成 Benchmark v1

运行：

```bash
python scripts/build_benchmark_v1_2026_05_18.py
```

该脚本会更新：

- `AI_EDU_BENCHMARK_V1.md`
- `AI_EDU_BENCHMARK_V1.html`
- `ai_edu_benchmark_v1_questions.json`
- `data/benchmark_v1_2026-05-18/items.jsonl`
- `data/benchmark_v1_2026-05-18/capability_criteria.jsonl`
- `data/benchmark_v1_2026-05-18/source_manifest.jsonl`
- `reports/2026-05-18/ai_edu_benchmark_v1_spec.md`
- `reports/2026-05-18/ai_edu_benchmark_v1_spec.html`

只做结构校验：

```bash
python scripts/build_benchmark_v1_2026_05_18.py --validate-only
```

当前验证结果：

```text
criteria=84
items=840
manifest=88
```

抽题逻辑：

- 每个评价标准先构造最多 80 条本地候选题。
- 用透明启发式打 `quality_score`：题干长度、答案/rubric 完整度、评分方式、evaluator、题源是否存在、benchmark 是否匹配、是否有程序测试/多模态/安全/rubric 信号。
- 每个评价标准最终保留前 10 条。
- `coverage_status` 包含 `coverage_gap` 的标准表示当前只是 proxy/resource-construction 样本，不能当作原生 benchmark 已完全覆盖。

## 重新生成 2026-05-13 调研抽取结果

运行：

```bash
python3 scripts/build_exhaustive_2026_05_13.py
```

该脚本会更新：

- `data/exhaustive_2026-05-13/*.jsonl`
- `data/exhaustive_2026-05-13/dataset_acquisition_report.md`
- `reports/2026-05-13/ai_edu_benchmark_exhaustive_index_2026-05-13.md`
- `reports/2026-05-13/ai_edu_benchmark_exhaustive_index_2026-05-13.html`
- `reports/2026-05-13/web_verified_updates_2026-05-13.md`

当前验证结果为：

```text
benchmarks.jsonl: 78
metrics.jsonl: 165
results.jsonl: 1616
dimension_mapping.jsonl: 256
covered_dimensions: 24
dataset_acquisition.jsonl: 78
```

## 使用方式

评估一个新的 AI-教育应用时，建议按以下流程：

1. 在统一框架中定位应用场景，例如数学 tutor、作文批改、编程教育、教师备课、个性化学习路径或教育安全。
2. 根据场景映射找到主 benchmark 和补充 benchmark。
3. 回到 benchmark catalog 查看对应原子能力、原生指标、公开效果和数据状态。
4. 对可直接下载的数据使用 `sources/datasets/` 中的本地副本。
5. 对人工授权或未发布数据，只记录为证据缺口，不假设已经可复现。

## 注意事项

- 不要把不同 benchmark 的原始分数直接平均；应先映射到原子能力，再形成能力画像。
- 通用知识类 benchmark 只能作为门槛项，不能证明模型具备教学能力。
- 教育核心能力更依赖错因诊断、脚手架、反馈质量、个性化、多模态 grounding、安全边界和真实学习效果。
- 公开 benchmark 对长期学习效果、教师采纳、师生机协同和中文本地教育安全覆盖仍不足。
