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
