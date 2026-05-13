# AI-教育 Benchmark 调研仓库

本仓库用于整理 AI-教育领域 benchmark、评测尺度、公开效果和可获得数据集。当前工作重点是信息收集与统一尺度建设，不是重新跑模型实验。

## 目标

对应 `todo.md`，本仓库要形成一个可复用的 AI-教育 benchmark 证据库：

- 收集 AI-教育领域已有 benchmark / 数据资源。
- 记录每个 benchmark 测什么问题、使用什么原生指标、是否有公开模型结果。
- 下载或登记可获得的数据集，并区分自动下载、人工申请、论文待发布等状态。
- 基于已有原子尺度，形成统一的 AI-教育应用评测框架。
- 当给定一个新的 AI-教育应用时，可以快速判断相似领域已有评测、推荐重点指标和补充评测方式。

## 当前状态

截至 2026-05-13，第一版统一框架已经可以使用：

- 覆盖 78 个 benchmark / 数据资源。
- 抽取 165 个指标。
- 整理 1616 条公开模型/结果记录。
- 覆盖 24 个原子能力。
- 收敛为 8 个一级评测尺度。
- 已下载 GitHub / HuggingFace 可直接获取的大部分数据集。

仍未完全补齐的部分主要是访问权限问题：

- `ASAP-AES` 和 `ASAP-SAS` 需要 Kaggle 账号、API token 和竞赛条款确认。
- 19 个资源属于 `manual_access_or_metadata_only`，需要人工申请、页面确认或机构授权。
- `EssayJudge` 目前是论文/待发布状态，没有可批量下载的数据包。

## 从哪里开始

推荐阅读顺序：

1. [todo.md](./todo.md)：项目目标。
2. [reports/2026-05-13/README.md](./reports/2026-05-13/README.md)：当前调研状态和是否足够的判断。
3. [reports/2026-05-13/ai_edu_unified_benchmark_framework_2026-05-13.md](./reports/2026-05-13/ai_edu_unified_benchmark_framework_2026-05-13.md)：统一尺度、场景映射和评分建议。
4. [reports/2026-05-13/ai_edu_benchmark_catalog_2026-05-13.md](./reports/2026-05-13/ai_edu_benchmark_catalog_2026-05-13.md)：benchmark 总目录。
5. [data/exhaustive_2026-05-13/dataset_acquisition_report.md](./data/exhaustive_2026-05-13/dataset_acquisition_report.md)：数据下载 manifest。

## 目录结构

```text
.
├── data/
│   ├── benchmark_metric_dimensions_2026-05-12.json
│   ├── benchmark_metric_indicators_2026-05-12.json
│   ├── model_dimension_performance_2026-05-12.json
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
│   └── 2026-05-13/
├── scripts/
│   ├── build_exhaustive_2026_05_13.py
│   └── download_all_datasets.sh
├── sources/
│   └── datasets/
└── todo.md
```

说明：

- `reports/` 放人可读调研报告和结论。
- `data/` 放机器可读抽取结果、下载 manifest 和日志。
- `scripts/` 放生成脚本和下载脚本。
- `sources/` 放真实下载的数据集，已在 `.gitignore` 中，不提交到 git。

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

## 重新生成抽取结果

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
