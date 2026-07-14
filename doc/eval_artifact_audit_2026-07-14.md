# 评测产物静默失败审计（2026-07-14）

**一句话**：全仓 172 个 run 里，**24 个分数是假的**（unusable）、64 个能用但必须带保留意见、78 个干净、6 个根本没产物。假分数不是"跑挂了"，是**跑完了、有 summary、有 headline，但那个数不是对模型的测量**。最惨的是 **P17（个性化教学策略选择）和 P18（适配性解释与反馈生成）——恰好是"会不会教"的两个核心能力**：承载它们的两个 tutor 生成基准（mrbench_tutor、bea2025_tutor）**六个 run 全军覆没**。

- 审计脚本：`scripts/audit_eval_artifacts.py`（离线、幂等、有 unusable 时退出码非 0，可当发布前门禁）
- 逐 run 明细：`reports/eval/_audit/audit_2026-07-14.jsonl`
- 总览：`reports/eval/_audit/summary.md`
- 每个 benchmark 的病历：`reports/eval/<benchmark>/README.md`（由 `scripts/build_eval_readmes.py` 生成）

```bash
PATH=/home/likefallwind/miniconda3/bin:$PATH python scripts/audit_eval_artifacts.py            # 全量
PATH=/home/likefallwind/miniconda3/bin:$PATH python scripts/audit_eval_artifacts.py \
    --benchmark mrbench_tutor --verbose                                                        # 单个
PATH=/home/likefallwind/miniconda3/bin:$PATH python scripts/build_eval_readmes.py              # 刷新 README
```

## 1. 这次要找的是什么

一类反复出现的 bug：**上游调用失败 → adapter 把异常吞掉、返回一个占位值 → 占位值被写进 `extractions.jsonl` → runner 把它当成功缓存（缓存过滤器只跳过带 `error` 字段的行）→ score 阶段把占位值当成"答错/不通过" → summary 照常生成**。

最后你拿到一个长得完全正常的分数。它的分母是全的，它的小数点后四位也很齐整，它只是**不是模型的表现**。

所以下面这些不算发现：跑挂了、报错了、目录是空的。算发现的是：**有分数，但分数假**。

## 2. 数字

| 判决 | run 数 | 含义 |
|---|---|---|
| `unusable` | **24** | 分数是假的，重跑之前不得进任何报告 / 聚合 / 映射裁决 |
| `caveat` | 64 | 能用，但引用时必须带上保留意见（样本残缺、区分度受限、裁判是替代品、还在跑…） |
| `clean` | 78 | 干净 |
| `no_artifacts` | 6 | 目录在，产物没有 |

## 3. 最严重的三个问题

### 3.1 裁判失败 = 教学不通过（污染 P17 / P18 / P20 / P13）

**受害 run**：`mrbench_tutor` 全部 3 个（unparsed 率 50.5% / 54.5% / 56.0%）、`bea2025_tutor` 全部 3 个（24.3% / 26.3% / 34.3%）。

**根因**：`scripts/eval/benchmarks/mrbench.py::MRBenchTutorAdapter._judge_one`（约 468-484 行）与 `scripts/eval/benchmarks/bea2025.py::_judge_one`（约 213-222 行）是同一段代码：

```python
for attempt in range(3):
    try:
        reply = client.chat(...)
        label = _normalize_label(dim, reply)
        if label != "unparsed":
            return label
    except Exception:  # noqa: BLE001 - retry transient judge failures
        pass
    time.sleep(1.5 * (attempt + 1))
return "unparsed"
```

三次重试全失败后返回 `"unparsed"`——**"裁判没被调用成功"和"裁判回复读不懂"被压成同一个值**。这行写进 `extractions.jsonl` 时**不带 `error` 字段**，而 `runner.py::run_extractions` 的缓存过滤器（约 300-306 行）只跳过带 `error` 的行，于是这条失败**被当成成功缓存下来，重跑也不会重试**。`score()` 要求三个关键维度全为 `"Yes"` 才算教学通过，`unparsed` → fail → 通过率凭空变低。

**为什么没人发现**：这些 run 的 `extractions.jsonl` 里 `usage: {"calls": 0}`，看起来像"裁判没被调用"的铁证——但**它证明不了任何事**：这些 adapter 用的是自己 `build_client()` 出来的裁判客户端，它的 usage 从来就不会进 runner 的 usage window。裁判跑了一万次，这里也是 0。**判官用量在这类 benchmark 上根本不可观测**，这本身是个要修的洞。

**修法**：
1. `_judge_one` 把"调用异常"和"回复读不懂"分开（前者抛出或返回 `judge_call_failed` sentinel）；
2. `extract_answer` 只要有一个维度是 call_failed 就 `raise`——runner 会写带 `error` 的行，既不缓存也能重试；
3. `extra_summary` 把 unparsed 从通过率分母里剔除并单独报 `n_unparsed`；
4. 让 adapter 把裁判的 token usage 回填到 summary，别再让 `calls: 0` 骗人。

两处最好抽成一个共用的 judge 调用工具，一次改完。

### 3.2 成对投票失败 = 判输（污染 P17 / P18 / P05）

**受害 run**：`mathtutorbench_scaffolding` 的 deepseek-v4-flash（**80.0%**）、deepseek-v4-pro（44.4%）、doubao-seed-2.0-pro（21.5%）；`mathtutorbench_scaffolding_hard` 的 doubao-seed-2.0-pro（38.5%）；`mathtutorbench_pedagogy` 的 glm-5.2（33.9%）。另有 12 个 run 在 3%-12% 之间（caveat）。

**根因**：`scripts/eval/benchmarks/mathtutorbench.py::_WinRateBase._vote_letter`（约 739-751 行）同款 `except Exception: pass`，三次重试后 `return None`。两个顺序的票都是 None → `win_score = None` → `score()` 里 `correct = ws is not None and ws > 0.5` → **False**。**裁判挂掉 = 生成回复输给金标**。deepseek-v4-flash 的 0.025 胜率不是模型差，是裁判 80% 没回来。

顺带一个没人报的问题：只有一票回来时，A/B 交换的位置去偏失效，`win_score` 退化成单票的 0/1，但没有任何字段标出来。

**修法**：两票全失败时抛异常（让 runner 记 error 行）；`score()` 遇 `win_score is None` 返回非 scored 状态而不是 `correct=False`；单票项在 `extra_summary` 里单列 `n_partial_vote`。

### 3.3 打分函数是死代码——longtutor_teaching 的分全是 0

**受害 run**：`longtutor_teaching/minimax3`，四维裁判分 `{history_utilization: 0.0, strategy_alignment: 0.0, coherence: 0.0, appropriateness: 0.0}`，accuracy 0.0。

**根因**：`scripts/eval/benchmarks/longtutor.py::_json_from_text`（约 84-96 行）的函数体被下一个函数截断了：

```python
def _json_from_text(text: str) -> Any:
    match = re.search(r"\{.*\}", text, re.S)
    if not match:
        return None


def _normalize_answer(text: Any) -> str:
    value = ...
    return re.sub(...)
    try:                                  # ← 本该属于 _json_from_text
        return json.loads(match.group(0)) # ← 永远执行不到的死代码
    except json.JSONDecodeError:
        return None
```

匹配成功时 `_json_from_text` 直接落到函数尾部、隐式返回 `None` → `score()` 里 `parsed = {}` → 四维全被 clamp 成 0。**裁判其实好好返回了合法 JSON**（`scored.jsonl` 的 `extracted` 字段里看得见 ```json {...}```），分数却全是 0。这个 run 花掉 3,600 万 token，产出的是一列零。

**修法**：把 `try/json.loads` 挪回 `_json_from_text`；给 `extra_summary` 加 `n_unparsed_judgements`——"全 0"这种事下次要能自己叫出来。

## 4. 其余问题

### 4.1 裁判 error 行照样被打分（eduguard_adversarial）

EduGuard 的 `_vote`（`eduguard_bench.py` 约 325-339 行）**是会抛异常的**（好设计），runner 于是写了带 `error` 的 extraction 行。但 `runner.py::run_scoring`（约 388-403 行）只判断 `ext is None`，带 `error` 的行照样进 `adapter.score("")` → `final_label = judge_error` → `correct=False` → **在 ASR 口径里等于攻击成功**。MiniMax-M2.7（3.1%）、kimi-k2.6（2.4%）的 ASR 因此被高估。

**一行修法，能同时救掉所有裁判类 benchmark**：

```python
# runner.py::run_scoring
if ext.get("error"):
    row["score_status"] = "extraction_error"
    scored.append(row); continue
```

### 4.2 配额/限流打挂大半样本，summary 在幸存者上出分

| run | 判分样本 | headline | 真相 |
|---|---|---|---|
| `olympiadbench/2026-06-08` | **387 / 6,728**（5.8%） | 0.897 | MiniMax Token Plan 配额（`base_resp 2062`）打挂 94% 的题 |
| `mmlu_pro/2026-06-07` | 3,061 / 12,032（25%） | 0.814 | 同上，打挂 75% |
| `agieval/2026-06-08` | 0 / 7,272 | — | 全挂，至少它没编分数 |
| `eduguard_sata/gpt-5.5` | 2,148 / 2,635（82%） | 0.689 | HTTP 403 用户额度不足（caveat） |

这类分数没有"算错"，但它测的是一个**自选样本**（能跑通的那部分题），不能跟全量 run 放进同一张表。前三个都有更新的全量 run 顶上；`2026-06-*` 这些是遗留目录，建议直接标注废弃。

### 4.3 产物自相矛盾（olympiadbench/deepseek-v4-pro）

`predictions.jsonl`（7-11 17:00 写）里 60.3% 的题是 `MiniMax HTTP 400: InvalidParameter`，一个 item 一行、没有重试行；而 `scored.jsonl` / `summary.json`（7-11 09:18 写）里有 6,685 条判过分的记录，accuracy 0.736。**盘上的分数不可能从盘上的预测重现出来**——预测文件在打分之后被一次坏配置的重跑覆盖了。好消息是 `scored.jsonl` 自带 `response` 字段，回答本身还在，可以离线核；坏消息是现在重跑会重新调 60% 的题。

### 4.4 p07_selfcheck：根因还在，产物已经被修好了

`p07_selfcheck.py::extract_answer`（约 112-131 行）第二轮撞限流时把错误塞进 `r2_error`、`r2_response` 留空，extraction 行不带 `error` → 被缓存 → `score()` 标 `r2_missing` → `extra_summary` 把这题从分母里剔掉，`score_10` 照常算出来。**分母悄悄变小，summary 里只有一个没人看的 `n_round2_missing` 字段**。

当前 5 个 run 的 `n_round2_missing` 全是 0（那批 r2_error 已经被重跑覆盖），所以审计判它们 clean/caveat。**但根因还在代码里**，下次限流照样复现。修法：`r2_response` 为空时直接 `raise`；`n_round2_missing > 0` 时在 summary 里写一条显式 `warning`。

### 4.5 区分度受限（不是 bug，但不能驱动裁决）

口径与 13 号映射效度检查一致（ceiling / floor / low_variance）：

- `mathtutorbench_problem_solving`：跨 4 模型均值 **0.970**、SD 0.008（天花板 + 零方差）
- `mathtutorbench_mistake_location`：均值 0.775、SD 0.009
- `mathtutorbench_solution_correctness`：均值 0.873、SD 0.014
- `mathtutorbench_judge_calibration`：均值 0.829、SD 0.012
- `ifeval`：均值 0.906、SD 0.020

这些格子区分不了模型，**不得驱动 M3 映射裁决**。

### 4.6 还在跑的 run（longtutor_evidence）

`longtutor_evidence/glm-5.2` 和 `/deepseek-v4-pro` 判 unusable，但原因不同：它们**此刻还在跑**（一小时内还在写盘），extractions 只覆盖了 1,076/3,000，`scored.jsonl` 里 100% 是 `no_extraction`，盘上的 summary 是个中间值。**这不是 bug，是"别去引用一个还没跑完的分数"**。审计脚本会给这种 run 打 `in_progress` 标记——顺带说明为什么门禁的退出码在跑批期间会是非 0，这是预期行为。

### 4.7 完全没有证据的 P

- **P04 复杂多模态理解**：只挂 `k12vista`，adapter 就绪但**一次都没跑过**。
- **P19 学习路径规划**：只挂 `mooccube_prereq`，目录是空的。

这两个 P 现在是**零证据**，不是"证据弱"。

## 5. 哪些 P 的分数被污染了（M3 裁决必读）

映射见 `reports/atomic_ability_rebenchmark_2026-07-08/02_benchmark_ability_mapping.jsonl`。

| P | 名称 | 污染程度 | 细节 |
|---|---|---|---|
| **P17** | 个性化教学策略选择 | **重度** | 挂 9 个 benchmark，5 个有 unusable run：`mrbench_tutor`（3/3 全废，w=0.3）、`bea2025_tutor`（3/3 全废，w=0.3）、`mathtutorbench_scaffolding`（3/7，**w=0.5**）、`mathtutorbench_scaffolding_hard`（1/7，w=0.5）、`mathtutorbench_pedagogy`（1/7，w=0.45）。**权重最高的几个格子全在名单上。** |
| **P18** | 适配性解释与反馈生成 | **重度** | 挂 12 个，6 个有 unusable：`bea2025_tutor`（3/3，w=0.45）、`mrbench_tutor`（3/3，w=0.45）、`eduillustrate`（6/9，w=0.3）、`mathtutorbench_scaffolding`（3/7）、`_hard`（1/7）、`_pedagogy`（1/7）。 |
| **P10** | 多模态教学产物生成 | **重度** | 唯一来源 `eduillustrate`，9 个 run 里 6 个 unusable（渲染失败 + 幸存者偏差 + 替代裁判）。 |
| **P20** | 教育角色边界判断 | 中度 | `mrbench_tutor`（3/3 全废，w=0.25）污染；`eduguard_*` 那边还干净。 |
| **P13** | 错因归因 | 中度 | `bea2025_tutor`（3/3 全废，w=0.25）污染；`sas_bench`/`mathtutorbench_mistake_correction` 未受影响。 |
| **P03** | 常规多模态感知 | 中度 | `eduillustrate`（6/9）+ `olympiadbench`（2/3，含遗留目录与产物矛盾的 deepseek-v4-pro）。 |
| P05 / P06 / P01 | 知识 / 推理 / 指令 | 轻度 | 只有遗留的 `2026-06-*` 配额残废 run 和 `olympiadbench/deepseek-v4-pro`；这三个 P 都有多个健康全量 run 顶着，**结论不受影响**。 |
| P04 / P19 | 多模态理解 / 路径规划 | **零证据** | `k12vista` / `mooccube_prereq` 从未产出。 |
| P02 / P07 / P08 / P11 / P12 / P14 / P16 / P21 / P22 | — | 干净 | 挂的 benchmark 没有 unusable run（部分有 caveat，见各自 README）。 |

**给 M3 裁决的结论**：现在做的"教学核心能力"映射裁决，**P17 / P18 这两条线上最强的四个证据源里有三个是坏的**。在 mrbench_tutor / bea2025_tutor / mathtutorbench 胜率类 run 重跑之前，任何关于 P17、P18 区分度、相关性、halo 的判断都建立在噪声上——包括"某模型教学能力更强"这种结论。P10 同理（唯一来源全废）。

## 6. 建议的动作顺序

1. **先改 runner 的一行**（4.1）：`run_scoring` 遇 `ext.get("error")` 不再打分。这一步不需要重跑任何东西，只需要 `--score-only` 重算。
2. **改三处 `except Exception: pass`**（3.1 / 3.2 / 4.4），把"调用失败"和"读不懂"分开，失败一律 raise 让 runner 记 `error`。
3. **改 longtutor 的死代码**（3.3），然后 `--score-only` 重算——预测和裁判回复都还在盘上，**不需要重新调 API**。
4. **重跑**：`mrbench_tutor`（3）、`bea2025_tutor`（3）、`mathtutorbench_scaffolding`（3）+ `_hard`（1）+ `_pedagogy`（1）。**重跑前必须删掉 `extractions.jsonl`**（或至少删掉坏行）——坏值已经被当成功缓存进去了，只跑 `--score-only` 没用。
5. **补跑**：`k12vista`、`mooccube_prereq`（P04 / P19 目前零证据）。
6. **标注废弃**：`reports/eval/*/2026-06-*` 三个配额残废目录。
7. **把审计挂成门禁**：`python scripts/audit_eval_artifacts.py`，有 unusable 就退出码非 0。

---

*产出：`scripts/audit_eval_artifacts.py`、`scripts/build_eval_readmes.py`、`reports/eval/_audit/`、`reports/eval/<benchmark>/README.md` ×34。本次审计不改任何 adapter 代码，也不动 `reports/eval/` 下已有的产物文件。*
