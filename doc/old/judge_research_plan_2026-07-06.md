# LLM-as-Judge 研究详细执行方案（2026-07-06）

> 来源：`doc/repo_review_suggestions_2026-07-05.md` 第二部分（J1–J6）+ 第三部分 3.1/3.2 相关项，经讨论后的落地方案。
>
> **已定决策**：
> - J4 陪审团做；J5 自训裁判暂缓（但所有前置为它预留）；
> - 陪审团成员 **{deepseek-v4-pro, glm-5.2, MiniMax-M3}**（三个不同家族）；
> - test split 按来源分层抽 ≈25%；
> - 原始数据与已有报告一律不动，新资产放新目录；
> - J2 不建 registry 框架，只做最小可归因（版本号 + hash）；
> - 生产默认裁判维持 MiniMax-M3 不变，换不换、换成什么由本研究结论决定。

---

## 0. 范围总览：做什么、不做什么

| 原建议 | 本方案 | 对应工作包 |
|---|---|---|
| J1 元评测集正式化 | **做**，双 task_type 子集设计，不强行统一标签空间 | WP1 |
| J2 prompt registry | **缩水为最小版**：adapter 内版本常量 + summary 记 hash | WP2 |
| J3 bias battery | **只做长度偏置**（零 API 事后分析）；自偏好靠 J4 稀释；风格/语言偏置缓 | WP5 |
| J4 异质陪审团 | **做**（本方案核心） | WP3 + WP4 |
| J6 不确定性路由 | **只做分歧落盘**（J4 副产物）；confidence 输出、人工队列缓 | WP4 内含 |
| 3.1 裁判/被测分离 | README 写规则；默认裁判不动 | WP5 内含 |
| 3.2 bootstrap CI + 配对检验 | **做**（jury 对比没有 CI 就没有结论），实现为公共 stats 模块 | WP0 |
| J2b rubric 消融 / J5 自训 / 风格语言偏置 / confidence 路由 | 暂缓，见附录 A 的预留接口 | — |

**执行顺序**：WP0 → WP1 → WP2 → WP3 → WP4 → WP5。WP0/1/2/5 零 API 成本，WP3 是唯一花钱步骤（全走 gateway 的 glm-5.2，约 9,800 次短输出调用），WP4 纯离线计算。

---

## 1. 已核实的事实基础（方案依据，均已在仓库验证）

1. **对话重叠**：BEA dev（300 对话）与 MRBench V2（200 对话）按 `conversation_id` 精确重叠 **182 个对话**。去重必须按对话分组，跨来源同对话必须进同一 split，否则元评测集内部泄漏。
2. **item_id 是位置式的**：mrbench_judge / bea2025_judge 的 item_id 形如 `c0-Gemini-Mistake_Identification`（`c{对话序号}-{回复模型}-{维度}`），mathtutorbench_judge_calibration 形如 `cal-0#ab`（`cal-{对对序号}#{ab|ba 顺序}`）。序号由源文件行序决定 → WP1 需先建 `conversation_id ↔ 序号` 映射，split 清单直接输出 **adapter 原生 item_id**，同时服务 `--item-list` 补跑和已有输出的离线过滤。
3. **陪审团数据现状**（per-item 输出 = `scored.jsonl` + `predictions.jsonl`，含 `reasoning` 字段即 judge rationale，已在落盘）：
   - mathtutorbench_judge_calibration（964）：**deepseek-v4-pro / glm-5.2 / MiniMax-M3 三家全量齐** → 陪审团纯离线；
   - mrbench_judge（13,240）/ bea2025_judge（9,904）：deepseek-v4-pro、MiniMax-M3（另有 v4-flash、v3.2）全量齐，**缺 glm-5.2 两格**；
   - `scored.jsonl` 已含 `pred_label` / `gold_label` / `dimension`（mathtutorbench 为 `pair_id` / `order` / `chose_positive`），离线合票所需字段齐全。
4. **harness 无按清单跑的能力**：`eval_benchmark.py` 只有 `--limit/--offset`，需新增 `--item-list`。
5. **加权投票的权重约束**：权重必须在 dev split 上估计（test 上估计再在 test 上验证 = 泄漏）。deepseek-v4-pro / MiniMax-M3 的 dev 表现可从已有全量输出按 split 过滤得到，**glm-5.2 没有 dev 输出** → 需补一个小规模 dev 子样跑（见 WP3）。
6. 已知运行坑（来自项目记忆）：gateway 的 `API_GATEWAY` 在非交互 shell 里不自动加载，需显式传入；glm-5.2 默认 max_tokens 4096 上限（judge 输出是短标签，无影响）；MiniMax 配额共享——本方案 M3 的票全部复用已有输出，**零新增 M3 调用**。

---

## 2. WP0：公共统计模块 `scripts/eval/stats.py`（零 API）

所有后续报告的地基，纯 stdlib 实现：

- **cluster bootstrap**：以 `conversation_id` 为重采样单元（同一对话下的多个 item 高度相关，按 item 重采样会低估方差），默认 1,000 次重采样，percentile 法 95% CI。适用指标：agreement、macro-F1、Cohen's kappa。
- **配对差值 CI**：两套判决（如 jury vs 最佳单裁判）在同一 item 集上，对"差值"做同一重采样序列的 bootstrap CI；CI 含 0 即报告为"无显著差异"。
- **kappa 边界处理**：某标签在重采样中支持数为 0 时该次记 n/a，报告 n/a 率；不静默丢弃。
- 接口设计成通用函数（输入 `(item_id, cluster_id, correct/label 对)` 列表），供 WP4 的 jury 报告和未来 3.2 的全面改造复用；**本期不改动现有各 adapter 的 summary**，避免范围膨胀。

**验收**：单元式自测（构造已知分布的合成数据，CI 覆盖真值）+ `py_compile`。

## 3. WP1：元评测集 `data/judge_meta_eval_v1/`（零 API）

新建 `scripts/build_judge_meta_eval.py`（幂等，风格同现有 `build_*.py`，标准库 only）。

### 3.1 数据构成与 schema

三个来源，两种 task_type，**不合并标签空间**：

| 来源 | task_type | 规模 | 标签 |
|---|---|---|---|
| mrbench（MRBench_V2） | `dimension_label` | 13,240 = 1,655 (对话×回复模型) × 8 维 | 各维原生标签（Yes / To some extent / No；Tutor_Tone 三分类等） |
| bea2025（mrbench_v3_devset） | `dimension_label` | 9,904 = 2,476 回复 × 4 维 | 官方 4 维原生标签 |
| mathtutorbench（482 专家偏好对 × 2 序） | `pairwise_preference` | 964 | chosen ∈ {a, b} |

`items.jsonl` 每行：

```json
{
  "item_id": "mrbench::c0-Gemini-Mistake_Identification",   // "{source}::{adapter原生item_id}"，保证与已有输出可直接连接
  "source_benchmark": "mrbench",
  "task_type": "dimension_label",
  "conversation_id": "5440-1c7bf65e-...",                    // 去重/分组/cluster bootstrap 的单元
  "dimension": "Mistake_Identification",                     // pairwise 任务为 null
  "context": "...对话历史...",
  "response": "...被判的 tutor 回复...",                     // pairwise 为 response_a/response_b
  "response_source_model": "Gemini",                         // 该回复出自哪个模型/人类（Novice/Expert）
  "human_label": "Yes",
  "language": "en",
  "split": "dev",
  "lineage": {"source_file": "...", "source_row_or_key": "..."}
}
```

### 3.2 去重与切分算法

1. 建全局对话表：MRBench 200 + BEA 300，按 `conversation_id` 合并 → **约 318 个唯一对话**（182 重叠）；mathtutorbench 的 482 对独立成组（无对话血缘）。
2. **切分单元 = 对话**（mathtutorbench 为偏好对）：一个对话的所有 item（跨来源、跨维度、跨回复模型）整体进同一 split；偏好对的 ab/ba 两序同 split。
3. dev/test ≈ 75/25，固定种子（写入 manifest），在对话约束下对（来源 × 维度 × 标签）分布做贪心平衡：以随机顺序逐对话分配，优先满足 test 侧各 (dimension, label) 桶的目标配额。
4. 重叠对话的 split 归属只判一次，两个来源共用。

### 3.3 输出

```
data/judge_meta_eval_v1/
├── items.jsonl
├── manifest.json            # 版本 judge_meta_eval_v1、种子、逐来源/split/维度/标签计数、
│                            # 去重说明（182 重叠对话数）、conversation_id↔序号映射的生成规则
├── split_test_item_ids/
│   ├── mrbench.txt          # adapter 原生 item_id，一行一个（供 --item-list / 离线过滤）
│   ├── bea2025.txt
│   └── mathtutorbench.txt
└── split_dev_subsample_glm/ # WP3 权重估计用的 dev 分层子样清单（见 5.2）
    ├── mrbench.txt
    └── bea2025.txt
```

预计 test split 规模：mrbench ≈ 3,300、bea2025 ≈ 2,500、mathtutorbench ≈ 240。

### 3.4 验收

- `--validate-only`：总数 = 24,108；无 `conversation_id` 跨 split；ab/ba 同 split；重叠 182 对话在两来源中 split 一致。
- dev/test 的各 (dimension, label) 分布差异打印在 manifest（分层是否成功一目了然）。
- 幂等：重跑两次输出 byte 级一致（种子固定、排序固定）。

## 4. WP2：judge prompt 可归因（零 API）

**不建 registry 目录**（共性只有"可归因"，prompt 内容本就该 per-benchmark 个性化）：

1. 涉及 LLM judge 的 adapter 各自声明 `JUDGE_PROMPT_VERSION = "v1"`：
   `mrbench.py`（judge + tutor 两条）、`bea2025.py`（同）、`mmtutorbench.py`、`eduguard.py`（adversarial 两阶段 → 记两个 hash：`harmfulness` / `refusal_tier`）、`mathtutorbench` 系（judge win-rate prompt）。
2. `summary.json` 新增 `judge_prompt_version` + `judge_prompt_sha256`（对 prompt 模板字符串取 sha256；多 prompt 的 adapter 记 `{名称: hash}` 字典）。
3. 历史 summary 不回填、不改动；本期不改任何 prompt 内容本身。

**验收**：`python -m py_compile scripts/eval/benchmarks/*.py` + 任选一个 benchmark `--dry-run`/小 limit 干跑核对 summary 新字段。

## 5. WP3：补齐 glm-5.2 判官数据（唯一花钱步骤）

### 5.1 harness 加 `--item-list <file>`

- 语义：`load_items` 之后按清单过滤（清单为 adapter 原生 item_id，一行一个）；与 `--limit/--offset` 互斥（同时给出时报错，避免歧义）。
- `summary.json` 记录 `item_list`（文件路径）+ `item_list_sha256` + `item_list_count`——顺带实现原建议 3.3"抽样协议固化"的记录半边。
- 预测/抽取的增量续跑逻辑（按 item_id skip）天然兼容，无需改动。

### 5.2 glm-5.2 补跑（gateway，判官输出为短标签）

| 跑什么 | 清单 | 规模 | 用途 |
|---|---|---|---|
| mrbench_judge × glm-5.2 | `split_test_item_ids/mrbench.txt` | ≈3,300 | test 上投票 |
| bea2025_judge × glm-5.2 | `split_test_item_ids/bea2025.txt` | ≈2,500 | test 上投票 |
| mrbench_judge × glm-5.2 | `split_dev_subsample_glm/mrbench.txt` | ≈1,200（dev 分层子样） | **加权投票的权重估计**（权重必须来自 dev，见事实 5） |
| bea2025_judge × glm-5.2 | `split_dev_subsample_glm/bea2025.txt` | ≈800（dev 分层子样） | 同上 |

合计 ≈9,800 次调用；mathtutorbench 三家已全量，无需任何新跑。命令形如：

```bash
API_GATEWAY=... python scripts/eval_benchmark.py --benchmark mrbench_judge \
  --model glm-5.2 --item-list data/judge_meta_eval_v1/split_test_item_ids/mrbench.txt --limit 0
```

输出落在 `reports/eval/{mrbench_judge,bea2025_judge}/glm-5.2/`，与既有目录约定一致（dev 子样与 test 清单分两次跑、增量合并在同一目录，summary 里的 item_list 字段区分批次）。

**验收**：glm-5.2 两格的 scored.jsonl 覆盖对应清单全部 item_id；unparsed 率与其他裁判同量级（异常高说明 prompt/解析有问题，先修再算票）。

## 6. WP4：陪审团 vs 单裁判报告（纯离线）

新建 `scripts/build_judge_jury_report.py`（幂等），读三家裁判的 per-item 输出 + WP1 split，全部指标**只在 test split 上计算**，输出到 `reports/eval/_judge_jury/`。

### 6.1 投票规则（写死进报告，保证可复现）

- **多数投票（主结论）**：三票中占多数的标签；`unparsed` 视为弃权；三票全弃权 → jury unparsed；1:1:1 三分歧或弃权后平票 → 由 dev kappa 最高的裁判（当前为 deepseek-v4-pro）tie-break，tie-break 触发率单独报告。
- **加权投票（次结论）**：各裁判权重 = 其 **dev split** 上的 per-dimension kappa（glm-5.2 用 5.2 的 dev 子样估计；负 kappa 截断为 0）；标签得分 = Σ 投该标签裁判的权重。
- **pairwise（mathtutorbench）**：对每个偏好对的 ab/ba 两序分别合票，另报陪审团的 position consistency（两序结论一致率）——已有单裁判的这项指标，陪审团应不差于单裁判。

### 6.2 报告指标（全部带 WP0 的 cluster bootstrap 95% CI）

对每个单裁判和两种陪审团，在每个来源上：

- per-dimension + macro 的 agreement / macro-F1 / Cohen's kappa；
- **配对差值 CI**：jury − 最佳单裁判（同 item 配对 bootstrap），这是主判定；
- unparsed / 弃权 / tie-break 触发率。

**判定标准**（写死）：陪审团（任一投票方式）在 test split 上的 kappa 配对差值 CI 不含 0 且为正 → "陪审团显著优于最佳单裁判"；否则如实报告"无显著差异"或"更差"。**反向结论同样有效**——直接决定 3.1 的生产裁判是换 deepseek-v4-pro 还是上陪审团。

### 6.3 分歧落盘（J6 的免费部分，J5 的训练种子）

- `reports/eval/_judge_jury/disagreements.jsonl`：三票不完全一致的 item，每行含 `item_id`、`dimension`、`human_label`、三家的 `pred_label` + 原始 `response` + `reasoning`（rationale，predictions.jsonl 里已有，直接引用）；
- manifest 记录分歧率 per dimension——分歧率本身就是"该维度 rubric 模糊程度"的信号，供未来 J2b 消融选靶。

### 6.4 产出

```
reports/eval/_judge_jury/
├── summary.json          # 所有数字 + CI + 投票规则参数 + 依赖的输入文件 hash
├── jury_report.md / .html
└── disagreements.jsonl
```

## 7. WP5：长度偏置分析 + README 规则（零 API）

### 7.1 长度偏置（并入 jury 报告，单独一章）

教育场景特有风险：裁判偏爱"更长、看起来更耐心"的回复，而好的脚手架恰恰应该短。方法（纯事后分析，被判回复文本从源 JSON 经 item_id 连回）：

- **dimension_label 线**：按被判 response 长度（空白分词数）在元评测集上取五分位桶，每桶每裁判算：
  1. 与人类的 agreement（裁判在长回复上是否更不可靠）；
  2. **宽容度差** P(judge=Yes | 桶) − P(human=Yes | 桶)（裁判是否系统性给长回复更高标签）——这是长度偏置的直接证据，比 agreement 更灵敏；
  3. 对多数投票陪审团做同样两条（陪审团是否稀释了长度偏置）。
- **pairwise 线（mathtutorbench）**：P(裁判选更长回复) vs P(人类专家选更长回复)，差值带 CI。
- 结果进 jury_report 的"长度偏置"章节，每格带 WP0 的 bootstrap CI。
- **自偏好说明**：MRBench/BEA 的被判回复出自 GPT-4/Gemini/Llama/人类等固定集合，陪审团三家都不在其中，故自偏好在金标数据上不可直接测——这正是"用异质陪审团稀释自偏好"作为工程解的原因，报告里如实写明这一局限。

### 7.2 README guardrails 增加一条（3.1）

> 对外报告的模型对比中，裁判不得是被测集合的成员；无法避免时，用两个不同家族的裁判各跑一遍并同时报告两套数字。

默认生产裁判（`MRBENCH_JUDGE_MODEL` 等）**维持 MiniMax-M3 不变**，待 WP4 结论出来再议替换。

---

## 8. 执行顺序、成本与验收总表

| # | 工作包 | 新增/改动文件 | API 成本 | 验收 |
|---|---|---|---|---|
| 1 | WP0 stats 模块 | `scripts/eval/stats.py` | 零 | 合成数据自测 CI 覆盖真值 |
| 2 | WP1 元评测集 | `scripts/build_judge_meta_eval.py` → `data/judge_meta_eval_v1/` | 零 | validate-only 通过；无对话跨 split；幂等 byte 一致 |
| 3 | WP2 prompt 可归因 | 5 处 adapter + summary 字段 | 零 | py_compile + 干跑核对字段 |
| 4 | WP3 glm-5.2 补跑 | `eval_benchmark.py` 加 `--item-list`；跑 4 个清单 | ≈9,800 次短输出调用（gateway） | 清单全覆盖；unparsed 率正常 |
| 5 | WP4 jury 报告 | `scripts/build_judge_jury_report.py` → `reports/eval/_judge_jury/` | 零 | 判定标准出数（含反向结论）；分歧文件落盘 |
| 6 | WP5 长度偏置 + README | jury 报告加章节；README 一条规则 | 零 | 五分位×裁判矩阵带 CI |

**风险与坑**（运行前自查）：`API_GATEWAY` 非交互 shell 不自动加载需显式传；M3 票全部复用已有输出（零新增 M3 调用，不碰 MiniMax 配额）；glm-5.2 max_tokens 4096 上限对短标签输出无影响；kappa 在零支持标签下记 n/a 并报告 n/a 率；BEA 只用 dev（官方 test 标签隐藏），本方案的 dev/test 均为 dev 内自切。

---

## 附录 0：执行结果（2026-07-06，全部 WP 已落地）

产出：`scripts/eval/stats.py`、`scripts/build_judge_meta_eval.py` → `data/judge_meta_eval_v1/`
（24,108 条，test 3,336/2,492/240）、`--item-list`、5 个 adapter 的 prompt provenance、
glm-5.2 两格补跑（7,831 次调用，unparsed=0）、`scripts/build_judge_jury_report.py` →
`reports/eval/_judge_jury/`（n_boot=1000）。

**主判定：陪审团不显著优于最佳单裁判**（三条线的 macro kappa 配对差值 CI 全部含 0；
mrbench +0.003 [-0.016, 0.019]，bea2025 +0.005 [-0.014, 0.023]，mathtutorbench −0.008）。
按 3.1 的行动项：**生产裁判换单裁判即可，不必上陪审团**。

**意外发现：glm-5.2 取代 deepseek-v4-pro 成为最佳单裁判**（此前 review doc 2.1 的结论基于
glm-5.2 未跑这两个校准集）：test split 上 mrbench kappa 0.438 vs dsv4-pro 0.417，bea2025
0.406 vs 0.388（差值未做显著性检验，但两条线方向一致且 glm dev kappa 也最高）。
MiniMax-M3 在两条 dimension_label 线上都明显垫底（0.354 / 0.335）——**当前生产默认裁判
恰好是最弱的候选**，建议切换默认 judge 至 glm-5.2 或 deepseek-v4-pro（留待用户拍板）。

**长度偏置（7.1）**：dimension_label 线上所有裁判在所有长度桶都比人类更严
（P(judge=Yes)−P(human=Yes) 全为负且大多显著），并非"偏爱长回复"，而是系统性偏严；
M3 最严（−0.16~−0.21），这解释了它 kappa 垫底。pairwise 线上 **M3 显著偏爱更长回复**
（P(选更长)=0.585 vs 人类 0.500，gap +0.085 [0.017, 0.154] 显著）——教育场景"裁判偏爱看似
更耐心的长回复"的风险在 M3 上实测成立，dsv4-pro/glm-5.2/陪审团无显著偏好。

**分歧数据（J6a/J5 种子）**：`disagreements.jsonl` 2,892 条（含三家 raw response+reasoning）；
test 集三票分歧率 mrbench 0.309 / bea2025 0.393 / mathtutorbench 0.138——bea 维度的 rubric
模糊度最高，是 J2b 消融的首选靶。

**2026-07-07 终版复核（glm-5.2 全量 dev 落地后）**：glm-5.2 补齐全量
（mrbench 13,240 全量 kappa 0.412、bea2025 9,904 全量 kappa 0.436，unparsed 均为 0），
加权投票权重改用全量 dev 估计后重跑 n_boot=1000——**主判定不变**：
jury_majority−best mrbench +0.003 [-0.016, 0.019]、bea2025 +0.005 [-0.014, 0.023]、
mathtutorbench −0.008，加权投票同样全含 0。陪审团结论就此定案；
后续提升路径全部转入 `doc/rubric_evolution_plan_2026-07-06.md`（Stage 0 已在执行，
0a 重映射地板六格全显著/边缘显著，映射高度一致为 "To some extent"→"Yes"）。
disagreements.jsonl 更新至 8,544 条（全量口径）。

## 附录 A：暂缓项及本方案为其预留的接口

| 暂缓项 | 预留 |
|---|---|
| J2b rubric 消融（人类锚点少样本、判前先做、CoT 结构、行为化锚点） | WP2 的版本号/hash 使任何 prompt 改动可归因；WP1 的固定 test split 是消融的统一实验面；WP4 的 per-dimension 分歧率指出先消融哪个维度 |
| J5 自训裁判 | WP1 dev split ≈1.8 万条人类判例是 SFT 底料；WP4 的 disagreements.jsonl（含三家 rationale）是最高信息量训练数据；验收标准 = WP1 test split 上超过最佳单裁判 kappa。**最大缺口仍是中文判例**（现有金标全英文数学 tutoring），300–500 条双人标注冲刺已登记 `benchmark-todo.md` 的入口在原 review doc 2.6 |
| J6 confidence 路由 | disagreements.jsonl 即"低置信队列"的雏形；等有人工复核流程再接 |
| 风格/语气偏置 | 需构造同内容不同语气的扰动对，属于造数据任务，与中文标注冲刺可合并规划 |
| 语言偏置 | 依赖中文人类金标（同上缺口） |
| 生产裁判切换（3.1 后半） | 由 WP4 判定标准的结论直接给出行动项 |
