# 2026-05-13 AI-教育 Benchmark 调研状态

本目录收纳 2026-05-13 这一轮围绕 `todo.md` 产生的结论性报告。原始结构化抽取和下载日志仍在 `../../data/exhaustive_2026-05-13/`，真实数据集仍在 `../../sources/datasets/`，且 `sources/` 已由 `.gitignore` 忽略。

## 是否足够

当前材料已经足够支撑第一版统一 AI-教育 benchmark 框架：

- 已形成 78 个 benchmark / 数据资源的目录、领域、原子能力、原生指标、公开结果状态和数据入口。
- 已抽取 165 个指标、1616 条模型/结果记录，能回答“相似领域有哪些评测、测什么尺度、有哪些已有效果”。
- 已把评测体系收敛到 8 个一级尺度、24 个原子能力，并给出场景到 benchmark 的映射方式。
- 已把可直接下载的数据入口整理成 manifest，并把 GitHub / HuggingFace 可获得的数据基本落到本地。

不应视为已经完全结束的部分：

- Kaggle 的 ASAP-AES、ASAP-SAS 还缺少本机 Kaggle 授权和竞赛条款确认，暂未下载。
- 19 个 `manual_access_or_metadata_only` 资源需要人工申请、同意条款、机构页面确认或产品侧访问，不能自动批量下载。
- EssayJudge 目前是论文/待发布状态，没有可批量下载的数据包。
- 长期学习效果、教师-学生-AI 三方协同、中文本地教育安全、端到端产品评测仍是公开 benchmark 的明显空白，需要后续自建或平台日志补充。

## 关键文件

- `ai_edu_benchmark_catalog_2026-05-13.md`：统一目录表，适合查某个 benchmark 测什么、有什么指标、数据入口在哪里。
- `ai_edu_unified_benchmark_framework_2026-05-13.md`：最终统一尺度和场景映射框架。
- `ai_edu_benchmark_exhaustive_index_2026-05-13.md`：按 D01-D24 原子能力展开的全量索引。
- `web_verified_updates_2026-05-13.md`：当日补充核验的新兴资源。
- `../../data/exhaustive_2026-05-13/dataset_acquisition_report.md`：数据下载 manifest。
- `../../data/exhaustive_2026-05-13/download_summary.csv`：实际下载尝试记录。
- `../../scripts/download_all_datasets.sh`：批量下载脚本；已支持 Gitee HTTPS URL 自动改写为 SSH。

## 数据落地状态

- 可直接下载入口：58 个。
- 本地已落地目录：56 个，位于 `../../sources/datasets/`。
- 剩余直接下载阻塞：ASAP-AES、ASAP-SAS，原因是 Kaggle 账号/API token/竞赛条款。
- 人工访问或元数据-only：19 个。
- 论文或待发布：1 个。

下一步若要补齐数据下载，只需要先完成 Kaggle 授权，然后运行：

```bash
FAILED_ONLY=1 COMMAND_TIMEOUT=300 ./scripts/download_all_datasets.sh
```

## 目录整理约定

- `reports/YYYY-MM-DD/`：放结论性报告和人可读索引。
- `data/exhaustive_YYYY-MM-DD/`：放 JSONL、下载 manifest、日志、summary 等机器可读/过程文件。
- `sources/datasets/`：放真实下载的数据集，不提交到 git。
- `scripts/`：放生成和下载脚本。
