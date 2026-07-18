# longtutor_teaching — 评测产物说明

> 由 `scripts/build_eval_readmes.py` 生成（审计快照 `_audit/audit_2026-07-16.jsonl`）。**不要手改**：改脚本后重跑。
> 综述档案（这个 benchmark 是什么，给人读）：（暂无档案；本文件的“这个评测是什么”一节即是权威描述，事实来源是 adapter 源码与 AGENTS.md）
> 本文件是给“要用这个分数的人”读的操作性病历：**分数能不能用、哪里坏了、要不要重跑**。

## 一、健康状况（坏消息在前）

全部 run 干净。

headline 口径：四维裁判分均值（1-5）。

| 模型 | headline | 审计判决 | 判分/抽取失败率 | 未判分率 | 说明 |
| --- | --- | --- | --- | --- | --- |
| `glm-5.2` | 4.0310 | clean | 0.7% | 0.0% | 0.7% 的题命中失败标记：裁判分解析恒为 0（打分函数是死代码） |
| `deepseek-v4-pro` | 3.9540 | clean | 0.4% | 0.0% | — |
| `minimax3` | 4.1000 | clean | 0.4% | 0.0% | — |

### 已定位的 bug（根因 + 修法）

**打分函数是死代码——四维分永远是 0**

- 位置：`scripts/eval/benchmarks/longtutor.py` → `_json_from_text`（约 84-96 行）
- 根因：函数体只有 `match = re.search(...)` 和 `if not match: return None`；真正的 `try: return json.loads(match.group(0))` 掉到了**下一个函数 `_normalize_answer` 的 `return` 之后**，是永远执行不到的死代码。于是匹配成功时 `_json_from_text` 直接落到函数尾部、返回 `None` → `score()` 里 `parsed = {}` → 四维全部 clamp 成 0 → `correct=False`。裁判其实返回了合法 JSON（`extracted` 字段里看得到 ```json {...}```），分数却全 0。
- 建议修法：把 `try/json.loads/except json.JSONDecodeError` 挪回 `_json_from_text` 里；同时给 `extra_summary` 加一个 `n_unparsed_judgements`，全 0 这种事下次要能自己叫。

> 本次审计**不改 adapter 代码**（那是下一步）。修完之后，受影响的 run 必须删掉 `extractions.jsonl` 里的坏行（或整个 extractions.jsonl）再重跑 —— 只跑 `--score-only` 没用，坏值已经被缓存进去了。

## 二、这个评测是什么

**一句话**：LongTutor 任务三：生成用到具体历史证据的自适应教学反馈，裁判按四维 1-5 分打分。

- **出处**：LongTutor 上游发布（无 LICENSE，勿再分发数据）；见 AGENTS.md 的 LongTutor 段。
- **数据**：1,001 条。
- **任务与判分**：裁判（走 `--extractor-model` 客户端）返回 JSON，四维：history_utilization / strategy_alignment / coherence / appropriateness。
- **adapter**：`scripts/eval/benchmarks/longtutor.py`
- **局限**：**当前打分函数是坏的**（见健康状况），现有分数全 0，没有意义。

**怎么用**：

```bash
MODEL=<model> ./scripts/run_eval.sh longtutor_teaching
# 或：python scripts/eval_benchmark.py --benchmark longtutor_teaching --model <model> --limit 0
```

## 三、当前映射（M3 裁决相关）

| benchmark_weight | 能力（P:权重） |
| --- | --- |
| 0.75 | P13 个性化教学策略选择 (0.3) |

---

审计脚本：`python scripts/audit_eval_artifacts.py --benchmark longtutor_teaching --verbose`（离线、幂等、有 unusable 时退出码非 0）。

<!-- 以下为人工撰写内容，build_eval_readmes.py 不会覆盖 -->

# LongTutor 教学行动评测

本目录保存 LongTutor 开放式教学行动任务的评测产物。结果必须分别报告以下四个评分维度：

- 历史利用（History Utilization）
- 策略一致性（Strategy Alignment）
- 连贯性（Coherence）
- 适切性（Appropriateness）

不得将本任务与 LongTutor 的历史证据获取、知识状态诊断任务合并计算单一总分。

## 默认裁判模型

本仓库目前默认使用 `MiniMax-M3` 作为本任务的大模型裁判。该选择主要基于评测成本，
不代表 `MiniMax-M3` 是当前最好的裁判模型，也不代表它已经在 LongTutor 的人工四维评分上
完成校准。

LongTutor 的裁判调用不设置 `max_tokens`，避免推理模型在生成最终四维评分前耗尽输出额度。
裁判缓存同时记录裁判模型和提示词版本；未来更换裁判模型或评分提示词时，只重新执行裁判
与评分阶段，继续复用被测模型的 `predictions.jsonl`。

LongTutor 原论文使用 `Gemini-3-Flash` 作为裁判模型，并将温度设为 0.0。论文附录 I.1
报告了该裁判与两位专家在 100 条分层抽样教学回复上的一致性，但公开仓库没有提供复现该
校准实验所需的逐条专家评分。因此，使用 `MiniMax-M3` 得到的结果属于本仓库的评测口径，
不是对原论文裁判配置的严格复现。

使用当前默认配置运行小规模评测：

```bash
MODEL=MiniMax-M3 JUDGE_MODEL=MiniMax-M3 LIMIT=5 ./scripts/run_eval.sh \
  longtutor_teaching
```

每次报告必须保留裁判模型、提示词版本和提示词哈希。如果未来获得带人工四维评分的校准集，
应先比较候选裁判模型，再决定是否修改默认值。在此之前，不得将裁判分数描述为人工一致性，
也不得将它与 LongTutor 其他任务的指标合并平均。
