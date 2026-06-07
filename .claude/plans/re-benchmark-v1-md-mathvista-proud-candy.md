# 新增 3 个 C1 主测 benchmark 适配器（MMLU-Pro / AGIEval / OlympiadBench）

## Context

`re_benchmark_v1.md` 的 C1（学科认知与问题求解）推荐了 7 个主测 benchmark，目前只有
**MathVista**（D06）已接入 `scripts/eval/` 的 per-benchmark 评测框架。本次目标是再接入
用户点名的 **MMLU-Pro (D01)**、**AGIEval (D03)**、**OlympiadBench (D05)**，整体复用现有
框架（load → predict → extract → score → report），并通过
`python scripts/eval_benchmark.py --benchmark <name>` 调用。

**数据可得性现状（已核实）**——这是本次方案的关键约束：

| 目标 | 本地数据 | 来源 | 备注 |
| --- | --- | --- | --- |
| AGIEval | ✅ 已下载 `sources/datasets/agieval/data/v1_1/*.jsonl` | github ruixiangcui/AGIEval | 直接可用 |
| MMLU-Pro | ❌ 仅有普通 `mmlu`，无 mmlu-pro | HF `TIGER-AI-Lab/MMLU-Pro` | 需下载 |
| OlympiadBench | ❌ 只 clone 了仓库代码，无数据 | HF `Hothan/OlympiadBench` | 需下载（含图） |
| OmniEduBench | ❌ 无本地数据，且无公开下载 | 论文/项目页 manual_access_only | **本次跳过**，仅在文档登记缺失（用户决策） |

**用户已确认的决策**：
1. OmniEduBench：暂不开发，仅在文档标注“数据集缺失”。
2. OlympiadBench 判分：按官方要求，复用官方 `sympy`+LaTeX 判分器（已确认 sympy 1.14 / parse_latex 可用）。
3. OlympiadBench 范围：文本 + 多模态 OE（OE_TO + OE_MM），排除证明题（TP）。

环境已具备：`sympy 1.14`、`datasets 4.7`、`pandas 2.3`、`sympy.parsing.latex.parse_latex` 均可用。

## 框架接口（复用，不改动核心）

每个 benchmark = `scripts/eval/benchmarks/<name>.py` 里一个 `BenchmarkAdapter` 子类
（`scripts/eval/base.py`），实现 5 个方法：`load_items / build_messages / extract_answer /
score / buckets`，再在 `scripts/eval/benchmarks/__init__.py` 的 `_REGISTRY` 注册。
通用 runner（`scripts/eval/runner.py`）、报告（`report.py`）、客户端（`minimax_client.py`）、
入口（`scripts/eval_benchmark.py`）**均无需修改**——`available_benchmarks()` 自动发现注册项。
参考实现：`scripts/eval/benchmarks/mathvista.py`（含用 `exec`/动态加载官方文件的范式，
见其 `_load_demo_prompt`）。

Item 归一化结构见 `base.py` 顶部 docstring：`{item_id, text, image_paths, gold, meta}`。

## 改动清单

### 1. 数据获取（一次性，写入 `sources/datasets/`，gitignored）

新增脚本 `scripts/eval/data/fetch_eval_datasets.py`（或在 plan 验证后用文档化命令），
用 `datasets` 库把 parquet 物化成 stdlib 可读的 JSONL，使各 adapter 的 `load_items`
保持 stdlib-only（`json`）：

- **MMLU-Pro** → `sources/datasets/mmlu_pro/test.jsonl`
  ```python
  from datasets import load_dataset
  load_dataset("TIGER-AI-Lab/MMLU-Pro", split="test").to_json(
      "sources/datasets/mmlu_pro/test.jsonl", force_ascii=False)
  ```
  字段：`question, options(list≤10), answer(letter A–J), answer_index, category, question_id, src`。

- **OlympiadBench** → `sources/datasets/olympiadbench/data/<config>.jsonl` + 图片落盘到
  `sources/datasets/olympiadbench/images/`。遍历 4 个 OE 配置：
  `OE_TO_maths_en_COMP, OE_TO_maths_zh_CEE, OE_TO_maths_zh_COMP, OE_TO_physics_en_COMP`
  及对应 `OE_MM_*`（共 8 个 OE 配置，排除全部 `TP_*` 证明题）。脚本对每行：保存
  `images`（PIL list）为 `images/<id>_<k>.png`，把图片路径写回 jsonl 的 `image_paths` 字段，
  其余字段（`question, final_answer(list), is_multiple_answer, unit, answer_type, error,
  subject, language, subfield, context`）原样保留。
  > 实现时先 `load_dataset("Hothan/OlympiadBench", "OE_TO_maths_en_COMP", split="train")`
  > 打印一行确认字段名后再批量；HF 字段名以实际为准。

### 2. `scripts/eval/benchmarks/mmlu_pro.py`（新增，纯文本 MCQ，D01）

- `load_items`：读 `test.jsonl`，`offset/limit` 切片；`gold = answer`（字母）；
  `meta` 存 `options, category`。
- `build_messages`：默认实现即可——`text` = 题干 + `A. ... B. ...`（按 options 顺序生成
  字母）+ “请逐步推理，并在最后一行输出 `The answer is (X)`。”（CoT，M3 为推理模型）。
- `extract_answer`：先用官方正则 `answer is \(?([A-J])\)?`（大小写无关、取最后一处匹配）快速
  路径；失败再 LLM 兜底抽取（复用 `client.chat(..., max_tokens=1024)`，prompt 要求只回字母，
  参照 mathvista 的 LLM 兜底）。
- `score`：`correct = (extracted_letter == gold)`；`normalized = extracted_letter`。
- `buckets`：`{"category": ...}`。

### 3. `scripts/eval/benchmarks/agieval.py`（新增，文本 MCQ + 数学填空，D03）

数据已在本地。复用官方逻辑，但**把所需的小函数内联**到 adapter（避免引入官方
`src/dataset_loader.py` 的 `tiktoken`/`pandas` 依赖）；数学等价判定**直接动态加载**
`sources/datasets/agieval/src/math_equivalence.py`（纯 stdlib，提供 `is_equiv`）。

- 任务集合（内联自 `dataset_loader.py`）：
  - MCQ：`english_qa_datasets` + `chinese_qa_datasets`（label 为字母；其中
    `multi_choice_datasets={jec-qa-kd, jec-qa-ca, gaokao-physics}` 的 label 为多字母集合）。
  - 数学填空：`math`（en）、`gaokao-mathcloze`（zh），`gold = answer`。
  - 默认主测集合建议覆盖全部 21 个 task（用 `--limit` 控量）；可在 adapter 顶部用常量列出。
- `load_items`：逐 task 读 `data/v1_1/<task>.jsonl`；`text` = 零样本 CoT 提示（内联
  `convert_zero_shot_CoT_stage1` 风格：题干+选项+“让我们逐步思考”，并要求结尾给出
  `答案是X` / `The answer is X`）；`meta` 存 `task, language, question_type(qa|cloze), options`。
- `extract_answer`：内联 `post_process.py` 的取字母逻辑（`answer is .*?([A-G])` /
  `答案是.*?([A-G])`，兜底 `find_first_capital_letter`）；数学题用内联 `parse_math_answer`
  抽 `\boxed{}`/末行。无需 LLM（省成本）。
- `score`：
  - MCQ 单选：`extracted_letter == gold`；多选（multi_choice）：把抽取与 gold 都规约为
    字母集合比较。
  - 数学：`is_equiv(extracted, gold)`（动态加载的 `math_equivalence`）。
- `buckets`：`{"task":..., "language":..., "question_type":...}`。

### 4. `scripts/eval/benchmarks/olympiadbench.py`（新增，OE 文本+多模态，D05）

- 复用官方判分器：动态加载 `sources/datasets/olympiadbench/eval/auto_scoring_judge.py`
  的 `AutoScoringJudge`（范式同 mathvista `_load_demo_prompt`，用 `exec`/`importlib`）；
  缓存一个实例。
- 复用官方 prompt：内联/移植 `inference/code/evaluators/evaluator.py` 的
  `get_answer_type_text` + `make_prompt` 逻辑（按 `is_chinese/is_math/is_multiple_answer/
  unit/answer_type` 生成提示，要求 `\boxed{}` 输出）。
- `load_items`：读步骤 1 生成的 `data/<config>.jsonl`；`image_paths` 来自落盘图片
  （MM 配置非空）；`gold = final_answer`（list）；`meta` 存
  `answer_type, is_multiple_answer, unit, error(precision), subject, language, is_mm, context`。
- `build_messages`：默认实现即可（text + images）；text = `make_prompt + (context+) question`。
- `extract_answer`：正则取最后一个 `\boxed{...}` 内容（兜底取 “final answer is” 之后/原文），
  无需 LLM。
- `score`：`precision = float(meta.error)`（缺省 `1e-8`）；`gold = ",".join(final_answer)`；
  `correct = judge.judge(gold, extracted, precision)`，`try/except` 包裹（sympy 解析可能抛错→
  判 False）。
- `buckets`：`{"subject":..., "language":..., "modality": "MM"|"TO", "answer_type":...}`。

### 5. 注册与文档

- `scripts/eval/benchmarks/__init__.py`：import 三个新 Adapter，加入 `_REGISTRY`。
- `benchmark-todo.md`：新增一条 OmniEduBench **数据缺失（manual_access_only，无公开下载）**
  的待办登记。
- `re_benchmark_v1.md`：在 C1 表的 OmniEduBench 行附近加一句脚注，标注“当前无公开可得数据，
  评测框架暂未接入”。
- `CLAUDE.md` 的 per-benchmark eval framework 段落：补充新接入的 3 个 benchmark 及其数据获取
  方式（与 MathVista 同列）。

## 复用要点（避免重复造轮子）

- 不改 `runner.py / report.py / minimax_client.py / eval_benchmark.py`（自动发现注册）。
- MathVista 的 LLM 兜底抽取、`max_tokens=1024` 给推理模型留头寸的范式直接照搬
  （`scripts/eval/benchmarks/mathvista.py:105-113`）。
- OlympiadBench 判分、AGIEval 数学等价**直接动态加载官方文件**，零重写、与官方分数可比。
- `scripts/eval/scoring.py` 的 `safe_equal` 可用于 MMLU-Pro / AGIEval 选择题比较。

## 验证

1. 语法：`python -m py_compile scripts/eval/benchmarks/*.py scripts/eval_benchmark.py`
2. 注册可见：`python scripts/eval_benchmark.py --benchmark agieval --help` 不报 Unknown；
   `available_benchmarks()` 含 `agieval, mmlu_pro, olympiadbench, mathvista`。
3. Dry-run（不调 API，校验 load + prompt 构造）：
   ```bash
   python scripts/eval_benchmark.py --benchmark agieval --limit 3 --dry-run
   python scripts/eval_benchmark.py --benchmark mmlu_pro --limit 3 --dry-run
   python scripts/eval_benchmark.py --benchmark olympiadbench --limit 3 --dry-run   # 需先跑数据获取
   ```
4. 小样本真跑（需 `MINIMAX_API_KEY`，文本模型也可，但多模态 OE 用 `MiniMax-M3`）：
   ```bash
   MINIMAX_API_KEY=... python scripts/eval_benchmark.py --benchmark mmlu_pro --limit 20 --concurrency 2
   MINIMAX_API_KEY=... python scripts/eval_benchmark.py --benchmark agieval --limit 20 --concurrency 2
   MINIMAX_API_KEY=... python scripts/eval_benchmark.py --benchmark olympiadbench --limit 20 --model MiniMax-M3 --concurrency 2
   ```
   产出 `reports/eval/<benchmark>/<date>/{predictions,extractions,scored}.jsonl + summary.json + report.html`。
5. 判分器自检：对 `olympiadbench/eval/scoring_examples.json` 跑一遍 `AutoScoringJudge`，
   确认与官方期望一致（动态加载无回归）。

## 调用方式（交付给用户）

```bash
# 0) 一次性获取数据（agieval 已有，可跳过）
python scripts/eval/data/fetch_eval_datasets.py --benchmark mmlu_pro
python scripts/eval/data/fetch_eval_datasets.py --benchmark olympiadbench

# 1) 评测（与 MathVista 完全一致的入口）
MINIMAX_API_KEY=... python scripts/eval_benchmark.py --benchmark mmlu_pro     --limit 50 --concurrency 2
MINIMAX_API_KEY=... python scripts/eval_benchmark.py --benchmark agieval      --limit 50 --concurrency 2
MINIMAX_API_KEY=... python scripts/eval_benchmark.py --benchmark olympiadbench --limit 50 --model MiniMax-M3 --concurrency 2
```
常用开关：`--dry-run`（不调 API 看 prompt）、`--score-only`（复用预测重判）、
`--skip-extract`（只出预测）、`--limit 0`（全量）。
