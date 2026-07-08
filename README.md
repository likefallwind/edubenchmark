# AI-教育 Benchmark 评测仓库

本仓库做两件事:

1. **跑评测** —— 一套可扩展的逐 benchmark 评测框架(`scripts/eval/`),针对 API 模型(默认 MiniMax-M3)在单个 benchmark 上打分:加载题目 → 调模型(支持文本+图像)→ LLM 抽取答案 → 判分 → 出 HTML 报告。这是当前最活跃的部分。
2. **建证据库与规格** —— AI-教育领域 benchmark / 指标 / 公开结果 / 数据可获得性的调研证据库,以及一版可追溯到题目出处的「原子能力-评价标准-题目」benchmark 规格(D01–D24 / S1–S8)。

> 默认语言:报告与内容用中文,脚本与代码用英文。贡献规范见 [`AGENTS.md`](./AGENTS.md),给 AI 助手的工作约定见 [`CLAUDE.md`](./CLAUDE.md)。

---

## 快速开始:评测一个 benchmark

### 1. 准备环境

凭证只从环境变量读取:

```bash
export MINIMAX_API_KEY=...                       # 必需
export MINIMAX_BASE_URL=https://api.minimaxi.com/v1   # 可选,默认即此
```

无第三方依赖,标准库即可跑(OlympiadBench 判分例外,见下)。

### 2. 一键评测(推荐)

```bash
# 跑全部 C1 主测 (mmlu_pro agieval olympiadbench)
./scripts/run_eval.sh

# 只跑指定的一个/多个
./scripts/run_eval.sh mmlu_pro
./scripts/run_eval.sh eduguard_sata eduguard_adversarial   # C5 EduGuard-Bench

# C4 MathTutorBench(教学过程评分/反馈质量),先一次性物化数据
python scripts/eval/data/fetch_eval_datasets.py --benchmark mathtutorbench
# 闭式任务(官方判分,无 judge);socratic 需 pip install sacrebleu
./scripts/run_eval.sh mathtutorbench_solution_correctness mathtutorbench_mistake_location mathtutorbench_mistake_correction
# 开放式教学反馈(LLM-as-judge 成对 win-rate,裁判=JUDGE_MODEL,默认 MiniMax-M3)
./scripts/run_eval.sh mathtutorbench_scaffolding mathtutorbench_pedagogy mathtutorbench_scaffolding_hard mathtutorbench_pedagogy_hard
# 裁判选择先行:被测模型即候选裁判,对论文专家偏好对的一致率越高越好,选最高者作生产裁判(MATHTUTORBENCH_JUDGE_MODEL)
MODEL=MiniMax-M3 ./scripts/run_eval.sh mathtutorbench_judge_calibration
MODEL=glm-5.1    ./scripts/run_eval.sh mathtutorbench_judge_calibration   # 对比另一候选裁判

# BEA 2025 shared task(4 维 tutor response 质量),先用 dev 人工标签校准 judge
python scripts/eval/data/fetch_eval_datasets.py --benchmark bea2025
LIMIT=20 MODEL=MiniMax-M3 ./scripts/run_eval.sh bea2025_judge
# 再用固定 judge 对被测模型生成的 tutor 回复打分;test 标签隐藏,本地不声称官方榜单等价
LIMIT=20 MODEL=doubao-seed-2.0-pro JUDGE_MODEL=MiniMax-M3 ./scripts/run_eval.sh bea2025_tutor

# MMTutorBench(多模态数学 tutoring),先一次性物化数据;第一版只建议小样本 smoke test
python scripts/eval/data/fetch_eval_datasets.py --benchmark mmtutorbench
LIMIT=5 MODEL=MiniMax-M3 JUDGE_MODEL=MiniMax-M3 ./scripts/run_eval.sh mmtutorbench
# 当前公开 JSONL 无逐题 human/expert gold;校准 adapter 只输出状态说明
LIMIT=20 MODEL=MiniMax-M3 ./scripts/run_eval.sh mmtutorbench_judge_calibration

# 小样本试跑 (LIMIT=0 或不设 = 全量)
LIMIT=200 ./scripts/run_eval.sh agieval

# 换被测 / judge 模型
MODEL=MiniMax-M3 JUDGE_MODEL=MiniMax-M3 ./scripts/run_eval.sh

# 后台长跑(脚本已设 PYTHONUNBUFFERED=1,日志实时写入)
CONCURRENCY=2 MODEL=MiniMax-M3 nohup ./scripts/run_eval.sh > eval.log 2>&1 &
tail -f eval.log
```

`run_eval.sh` 帮你处理了每个 benchmark 的特例(OlympiadBench 的判分专用 venv、EduGuard 的两阶段 LLM-as-judge、MathTutorBench 教学反馈的 win-rate 裁判注入等),日常优先用它。

### 3. 直接调底层入口(需要细控参数时)

```bash
python scripts/eval_benchmark.py --benchmark mmlu_pro --model MiniMax-M3 --concurrency 4 --limit 0
```

常用参数:

| 参数 | 默认 | 说明 |
|---|---|---|
| `--benchmark` | (必填) | `mathvista` / `mmlu_pro` / `agieval` / `olympiadbench` / `eduguard_sata` / `eduguard_adversarial` / `mathtutorbench_*` / `bea2025_judge` / `bea2025_tutor` / `mmtutorbench` / `mmtutorbench_judge_calibration`(见下表) |
| `--model` | `MiniMax-M3` | 被测模型(须用视觉模型 M3,M2.7 仅文本) |
| `--extractor-model` | `MiniMax-M2.7` | 答案抽取 / LLM-as-judge 模型 |
| `--limit` | `30` | 题量,`0`/负数 = 全量 |
| `--offset` | `0` | 起始偏移 |
| `--concurrency` | `4` | 预测并发 |
| `--timeout` | `300` | **流式下是"卡死间隔"超时**,见下 |
| `--retries` | `2` | 空响应重试次数 |
| `--max-tokens` | (不设) | 预测阶段建议不设,让推理模型自由生成 |
| `--skip-extract` | off | 只出预测,不抽取/判分 |
| `--score-only` | off | 复用已有预测,只做抽取+判分 |
| `--dry-run` | off | 打印构造好的消息(base64 图省略),不调 API |

各阶段**可断点续跑**:`predictions.jsonl` / `extractions.jsonl` 按 `item_id` 去重,已成功的重跑时跳过,报错/空响应的会重试。中途崩溃不丢已完成结果。

### 4. 输出位置

每个 benchmark 固定输出到 `reports/eval/<benchmark>/`:

- `predictions.jsonl` —— 模型原始回答(真实进度看这个,别看 `eval.log`)
- `extractions.jsonl` —— 抽取出的答案
- `scored.jsonl` —— 逐题判分
- `summary.json` —— 汇总(总数/正确数/准确率,按桶分组)
- `report.html` —— 可读报告

### 已支持的 benchmark

| 名称 | 能力 | 题型 / 判分 |
|---|---|---|
| `mmlu_pro` | D01 | 10 选 MCQ;官方 `answer is (X)` 正则 + LLM 兜底,比对选项字母 |
| `agieval` | D03 | 高考/法考 MCQ + 数学填空;选项字母解析 + 官方 `math_equivalence` 判等 |
| `olympiadbench` | D05 | 竞赛开放题(文本+多模态);移植官方 `make_prompt` 与 sympy 符号判分 `AutoScoringJudge` |
| `mathvista` | D06 | 视觉数学;移植官方 few-shot 抽取 + 最近选项编辑距离判分(需下载图片) |
| `eduguard_sata` | C5 | 教育安全多选(SATA);规则判分,中英双语 |
| `eduguard_adversarial` | C5 | 对抗安全;两阶段 LLM-as-judge(每阶段 BoN=3 投票) |
| `mathtutorbench_problem_solving` | gate | GSM8K 解题;`Final answer` 数字精确匹配(门槛项,非教学能力) |
| `mathtutorbench_socratic` | D13 | 苏格拉底式提问;移植官方 SacreBLEU(需 `pip install sacrebleu`) |
| `mathtutorbench_solution_correctness` | D12 | 学生解答对错(Yes/No);accuracy + P/R/F1 |
| `mathtutorbench_mistake_location` | D12 | 首个错误步骤号;步骤号 F1(micro/macro/weighted) |
| `mathtutorbench_mistake_correction` | D13 | 生成正确解;数值最终答案精确匹配 |
| `mathtutorbench_scaffolding` / `_hard` | D11/D13 | 脚手架回应;**LLM-as-judge 成对 win-rate**(对金标,位置交换去偏,替代官方 GPU 奖励模型) |
| `mathtutorbench_pedagogy` / `_hard` | D11/D13 | 教学法遵循;同上 LLM-as-judge win-rate |
| `mathtutorbench_judge_calibration` | — | 裁判选择(先行):被测模型即候选裁判,衡量与论文专家偏好对的一致率,选最高者作 win-rate 任务的生产裁判 |
| `bea2025_judge` | D11/D12/D13 | BEA 2025 dev:被测模型即候选裁判,对 4 个 shared-task 维度与 human labels 做 exact/lenient accuracy + macro-F1 + kappa |
| `bea2025_tutor` | D11/D12/D13 | 被测模型生成下一句 tutor 回复,固定 `BEA2025_JUDGE_MODEL`/`JUDGE_MODEL` 四维打标;headline 为本地 pedagogical pass rate,非官方榜单分 |
| `mmtutorbench` | D11/D13 | 多图数学 tutoring;previous images + current image + student query,固定 `MMTUTORBENCH_JUDGE_MODEL` 六维 0/1 rubric judge,总分 0-6 |
| `mmtutorbench_judge_calibration` | — | 校准钩子;当前公开 JSONL 未提供逐题 human/expert gold,只输出状态说明 |

> MathTutorBench(eth-lre/mathtutorbench)首次使用前先物化数据:`python scripts/eval/data/fetch_eval_datasets.py --benchmark mathtutorbench`(stepverify/pref_test 取自 HF,gsm8k 取自本地 parquet;scaffolding/pedagogy 用克隆内 `datasets/mathdial_bridge*.json`)。win-rate 裁判经 `MATHTUTORBENCH_JUDGE_MODEL`(默认 `MiniMax-M3`)固定、与被测/抽取模型解耦。

> BEA 2025(shared task Pedagogical Ability Assessment of AI-powered Tutors)首次使用前先物化数据:`python scripts/eval/data/fetch_eval_datasets.py --benchmark bea2025`。当前 manifest 记录 dev set 为 300 个 dialogue / 2,476 个带人工标注 tutor response;test set 为 191 个 dialogue / 1,547 个 response,但无本地标签/身份,只能导出预测或走官方/CodaBench 评测。常规流程是先 `LIMIT=20 MODEL=<candidate-judge> ./scripts/run_eval.sh bea2025_judge` 选裁判,再 `LIMIT=10/20 MODEL=<tested-model> JUDGE_MODEL=<chosen-judge> ./scripts/run_eval.sh bea2025_tutor` 小样本 smoke。

> MMTutorBench(Tangchiu/mmtutorbench)首次使用前先物化数据:`python scripts/eval/data/fetch_eval_datasets.py --benchmark mmtutorbench`(770 条 JSONL + 1414 张 keyframe 图片 + `data_manifest.json`)。常规接入先跑 `LIMIT=5` smoke test;全量 770 条成本较高,不要默认启动。rubric judge 经 `MMTUTORBENCH_JUDGE_MODEL`(默认 `MiniMax-M3`)固定。

新增一个 benchmark:在 `scripts/eval/benchmarks/<name>.py` 写一个 `BenchmarkAdapter` 子类(实现 `load_items` / `build_messages` / `extract_answer` / `score` / `buckets`),并在 `scripts/eval/benchmarks/__init__.py` 注册。

### 流式与超时(重要)

`scripts/eval/minimax_client.py` 是一个 **OpenAI 兼容客户端,默认走流式**(`stream=True`),按 SSE 逐 token 读取。这带来一个关键语义:

> `--timeout` 限制的是**两个数据块之间的最大间隔(卡死检测)**,不是总生成时长。

推理模型(M3、DeepSeek-R1 等)边想边吐 `reasoning_content`,连接一直有数据流动,所以它想多久都不会超时,只有连接**真卡死**才会被掐断。客户端只累加 `delta.content`(可见答案),忽略 `reasoning_content`(思维链)。

> ⚠️ 历史坑:早期为非流式请求,`timeout=300` 实际变成"总生成必须在 300s 内完成",导致 M3 难题大面积 `The read operation timed out` 且每条还白白重试 3 次(~900s)。改流式后此问题消除。

### 支持的模型 / provider

`--model`(以及 `--extractor-model` / `JUDGE_MODEL`)按**模型名前缀**自动路由到对应后端,无需改代码——provider 注册表在 `scripts/eval/providers.py`。当前支持:

| provider | 模型名 | 所需环境变量 | 端点 |
|---|---|---|---|
| **minimax** | `MiniMax-M3`(视觉,默认被测)、`MiniMax-M2.7`(纯文本,默认抽取/judge) | `MINIMAX_API_KEY` | `https://api.minimaxi.com/v1`(可经 `MINIMAX_BASE_URL` 覆盖) |
| **gateway** | `doubao-seed-2.0-pro`、`doubao-seed-2.0-lite`、`glm-5.1`(及任意 `doubao*` / `glm*`) | `API_GATEWAY` | 本地中转 `http://127.0.0.1:8111/v1`(可经 `API_GATEWAY_BASE_URL` 覆盖) |
| **deepseek** | `deepseek-v4-pro`、`deepseek-v4-flash`(官方只有这两档,无 `deepseek-v4-lite`) | `DEEPSEEK_API` | `https://api.deepseek.com`(可经 `DEEPSEEK_BASE_URL` 覆盖) |

前缀无法匹配的模型名默认落到 gateway。注意 gateway 也单独暴露了一个同名 `deepseek-v4-pro`,与官方直连不同;要走 gateway 那份需 `--provider gateway` 显式指定。

> 被测模型与抽取/judge 模型用**独立 client**,可分属不同 provider(如被测走 deepseek、judge 留在 minimax),所以跨 provider 评测时对应的多个 key 都要设。

```bash
# 例:被测 deepseek-v4-pro(DeepSeek 官方),抽取/judge 仍用 MiniMax
DEEPSEEK_API=<key> MINIMAX_API_KEY=<key> \
python scripts/eval_benchmark.py --benchmark mmlu_pro --model deepseek-v4-pro --limit 50
```

**接任意其它 OpenAI 兼容服务(未注册的)**:用逃生口环境变量,不用动代码——
`MINIMAX_BASE_URL` + `MINIMAX_CHAT_PATH`(默认 `/text/chatcompletion_v2`,标准 OpenAI 服务设为 `/chat/completions`)指向目标端点即可;或新增一个 provider 时在 `providers.py` 注册一条。

### benchmark 专项说明

- **OlympiadBench 判分**需要 `antlr4-python3-runtime==4.11`(sympy `parse_latex`),与 `hydra-core`/`omegaconf` 冲突。`run_eval.sh` 已用 `uv` 临时环境隔离判分阶段;手动跑见脚本里的两段命令。
- **MathVista 需要图片**:`cd sources/datasets/mathvista/data && wget .../images.zip && unzip`。
- **拉取 parquet/JSON/JSONL 数据集**:`python scripts/eval/data/fetch_eval_datasets.py --benchmark mmlu_pro|olympiadbench|mathtutorbench|bea2025|mmtutorbench|all`(MMLU-Pro 用**公开**的 `TIGER-Lab/MMLU-Pro`;OlympiadBench 取 OE 配置,图片解到 `olympiadbench/images/`;MathTutorBench 物化 stepverify/pref_test(HF)+ gsm8k(本地 parquet);BEA 2025 下载 dev/test JSON 并写 hidden-test-label manifest;MMTutorBench 下载 JSONL+keyframes 并写 manifest)。AGIEval 数据随其仓库 checkout。
- **MathTutorBench 教学反馈**:`mathtutorbench_scaffolding`/`_pedagogy`(+`_hard`)用 LLM-as-judge 成对 win-rate 替代官方需 GPU 的 1.5B 偏好奖励模型,裁判经 `MATHTUTORBENCH_JUDGE_MODEL`(默认 `MiniMax-M3`)固定;`mathtutorbench_judge_calibration` 先用论文专家偏好集选裁判。`run_eval.sh` 已封装 win-rate 任务的 judge 注入,`socratic` 需 `pip install sacrebleu`。
- **限流自愈**:连续 `RATE_LIMIT_THRESHOLD`(默认 10)个 429/限流错误即判定被限流,自动 sleep `RATE_LIMIT_SLEEP` 秒(默认 1800)后重排被限样本(每条最多 `RATE_LIMIT_MAX_RETRIES` 次,默认 3)。

---

## 评测框架架构(`scripts/eval/`)

故意与下面的「带日期快照的 build 脚本」和 `run_re_benchmark_v1.py`(纯文本、拒图)解耦。

```text
scripts/
├── eval_benchmark.py        # 入口:解析参数,调 runner
├── run_eval.sh              # 一键评测封装(处理各 benchmark 特例)
└── eval/
    ├── runner.py            # 通用循环:predict → extract → score → report,断点续跑 + 限流守卫
    ├── minimax_client.py    # OpenAI 兼容流式客户端(文本+base64 图像)
    ├── base.py              # BenchmarkAdapter 抽象基类
    ├── scoring.py           # 复用的判分工具(无额外依赖)
    ├── report.py            # JSONL 读写 + summary + HTML 报告
    ├── benchmarks/          # 每个 benchmark 一个 adapter
    └── data/                # 数据拉取脚本(fetch_eval_datasets.py)
```

---

## 三套产物 / 重新生成

所有 `scripts/build_*.py` 都是**幂等**的:读 taxonomy/源 JSON → 构造题 → 打分 → 覆盖输出。**不要手改生成文件,改脚本再重跑。**

| 产物 | 入口 / 重新生成 | 校验 |
|---|---|---|
| **Benchmark v1**(`*_2026_05_18`):8 尺度 / 24 能力 / 84 标准 / 840 题 | `python scripts/build_benchmark_v1_2026_05_18.py` | `--validate-only` → `criteria=84 items=840 manifest=88` |
| **调研证据库**(`exhaustive_2026-05-13`) | `python3 scripts/build_exhaustive_2026_05_13.py` | `benchmarks=78 metrics=165 results=1616` |
| **RE_BENCHMARK_V1**(五大类 C1–C5 + 试点包) | `python scripts/build_re_benchmark_v1.py` | 见 `re_benchmark_v1.md` |

阅读入口:

- [`AI_EDU_BENCHMARK_V1.md`](./AI_EDU_BENCHMARK_V1.md) —— v1 主入口(S1–S8 / D01–D24 / 评价标准)
- [`ai_edu_benchmark_v1_questions.json`](./ai_edu_benchmark_v1_questions.json) —— 题目索引,每题带 `source_file` + `source_row_or_key`
- [`re_benchmark_v1.md`](./re_benchmark_v1.md) —— 五大类主测组合口径
- [`reports/2026-05-13/`](./reports/2026-05-13/) —— 统一框架、benchmark catalog、调研报告
- [`data/benchmark_metric_dimensions_2026-05-12.json`](./data/benchmark_metric_dimensions_2026-05-12.json) / [`indicators`](./data/benchmark_metric_indicators_2026-05-12.json) —— D01–D24 能力与指标定义(两套 build 脚本共用)

### 数据状态词汇(贯穿全仓库,有承重作用)

manifest 用这些词区分每个源的可获得性:`local_ready`、`downloadable_not_local`、`manual_kaggle_required` / `manual_access_or_metadata_only`、`metadata_model_available_dataset_not_found`、`local_ready_but_no_pilot_extractor`。门控/未发布数据(Kaggle ASAP、EssayJudge、HF-gated TutorBench/Pedagogy)一律记为证据缺口,**不假设可复现**。题目上的 `coverage_status: coverage_gap` 表示该条只是 proxy / 资源构造样本,不能当作原生 benchmark 已完全覆盖。

---

## 数据下载

```bash
# 批量(从 dataset_acquisition_report.md 读命令,Gitee HTTPS 自动改写为 SSH)
COMMAND_TIMEOUT=1200 ./scripts/download_all_datasets.sh

# 只重试失败项
FAILED_ONLY=1 COMMAND_TIMEOUT=300 ./scripts/download_all_datasets.sh
```

结果写入 `data/exhaustive_2026-05-13/download_summary.csv` 和 `dataset_download.log`。下载的数据集副本放 `sources/datasets/`,已 gitignore,不提交。

---

## EduBench Assistant Skill

[`skills/edubenchassistant/SKILL.md`](./skills/edubenchassistant/SKILL.md) 是一个面向 Agent 的 skill:给定一个 AI-教育应用/产品/场景,它基于本仓库证据库推荐应关注的 D01–D24 能力与 S1–S8 尺度、相似的已有 benchmark、原生指标/公开结果/数据可用性、以及安全/污染/rubric 关注点,最终输出 HTML 报告到 `reports/edubenchassistant/`。新发现的评测缺口记入 `benchmark-todo.md`。

```bash
# 本地安装
install -D skills/edubenchassistant/SKILL.md ~/.agents/skills/edubenchassistant/SKILL.md

# 或通过 Skills CLI(仓库已发布到 GitHub 时)
npx skills add likefallwind/edubenchmark@edubenchassistant -g -y
```

---

## 解读须知(guardrails)

- **不要把不同 benchmark 的原始分数直接平均**;先映射到 D01–D24 能力,再形成能力画像。
- 通用知识类 benchmark 只是**门槛项**,不能证明教学能力。教育核心能力在于错因诊断、脚手架、反馈质量、个性化、多模态 grounding、安全边界和真实学习效果。
- **裁判与被测分离**:对外报告的模型对比中,LLM 裁判不得是被测集合的成员;无法避免时,用两个不同家族的裁判各跑一遍并同时报告两套数字。裁判的选择依据是人类金标校准(`data/judge_meta_eval_v1/` + `reports/eval/_judge_jury/`),不是名气。
- 公开 benchmark 对长期学习效果、教师采纳、师生机协同和中文本地教育安全的覆盖仍不足。
