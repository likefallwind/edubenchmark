# Reports

本目录保存评测证据、生成报告和不可变的方法快照。它不只是按日期排列的调研报告目录。

## 主要目录

| 路径 | 内容 | 状态 |
|---|---|---|
| `eval/` | 各 benchmark 的预测、抽取、逐题判分、汇总和 HTML 报告 | 当前评测证据 |
| `atomic_ability_rebenchmark/` | 当前 P01-P20 能力画像聚合产物 | 当前生成产物 |
| `atomic_ability_l1_floor/` | 通过同一聚合管线计算的 L1 floor | 当前生成产物 |
| `atomic_ability_rebenchmark_*_snapshot_*` | R 系列或 mapping 版本变更前的完整快照 | 历史证据，只读保留 |
| `re_benchmark_v1/` | RE_BENCHMARK_V1 报告、试点和小实验 | 版本化工作流 |
| `mini_selection_v1/` | 精选题集选择和验证产物 | 版本化工作流 |
| `mini_selection_v2/` | 39 个 benchmark 的代表性快速筛查集选择与离线验证 | 当前实验工作流 |
| `frontier_selection_v1/` | 错题、模型分歧与未来能力边界组成的前沿挑战集 | 当前实验工作流 |
| `2026-05-12/`、`2026-05-13/` | 早期 benchmark 调研和证据库报告 | 历史报告 |
| `edubenchassistant/` | EduBench Assistant 生成的场景报告 | 按请求生成 |

## `reports/eval/` 路径规则

```text
# 规则判分
reports/eval/<benchmark>/<model-slug>/

# LLM 裁判判分
reports/eval/<benchmark>/judge-<judge-slug>/<model-slug>/

# smoke、baseline、迁移、降级输入等隔离产物
reports/eval/<benchmark>/_<variant>/...
```

一次标准运行通常包含 `predictions*.jsonl`、`extractions.jsonl`、
`scored.jsonl`、`summary.json` 和 `report.html`。其中 `summary.json` 是完成状态和
汇总指标的事实来源；预测文件、日志或正在运行的进程都不能单独证明评测已经完成。

## 编辑规则

- 标有生成器来源的文件不要手改，应修改源数据或脚本后重跑。
- 当前目录与历史 snapshot 不要混写；方法变化前按现有 R 系列规则保存快照。
- 不同裁判、输入变体、题单或不兼容生成参数不得复用同一结果目录。
- benchmark 目录下的 README 负责说明该 benchmark 的指标、判分和已知限制。

机器可读的规范和映射保存在 `../data/`；外部下载的数据集保存在
`../sources/datasets/`。顶层目录规则见 `../doc/repository_layout.md`。
full、mini_v2 和 frontier_v1 的用途、重建命令与分数边界见
`../doc/selection_suites.md`。
