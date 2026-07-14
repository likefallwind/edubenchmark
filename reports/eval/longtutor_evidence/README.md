# longtutor_evidence — 评测产物说明

> 由 `scripts/build_eval_readmes.py` 生成（审计快照 `_audit/audit_2026-07-14.jsonl`）。**不要手改**：改脚本后重跑。
> 综述档案（这个 benchmark 是什么，给人读）：（暂无档案；本文件的“这个评测是什么”一节即是权威描述，事实来源是 adapter 源码与 AGENTS.md）
> 本文件是给“要用这个分数的人”读的操作性病历：**分数能不能用、哪里坏了、要不要重跑**。

## 一、健康状况（坏消息在前）

**这个 benchmark 下有 2 个 run 的分数不可用（unusable）。** 在重跑之前，不要把它们写进任何报告、聚合或映射裁决。

headline 口径：准确率（accuracy）。

| 模型 | headline | 审计判决 | 判分/抽取失败率 | 未判分率 | 说明 |
| --- | --- | --- | --- | --- | --- |
| `deepseek-v4-pro` | — | **unusable**（分数是假的，必须重跑） | 0.0% | 100.0% | 100.0% 的题没进判分（分数建立在 0/3003 的残缺样本上）；一小时内还在写盘，疑似仍在跑，当前 summary 只是中间值 |
| `glm-5.2` | — | **unusable**（分数是假的，必须重跑） | 0.0% | 100.0% | 100.0% 的题没进判分（分数建立在 0/3003 的残缺样本上）；产物数量对不上，最大缺口 64.1% |
| `minimax3` | 0.7872 | clean | 0.0% | 0.0% | — |

### 样本残缺的 run

上游配额/限流打挂大批题目后，summary 仍在**幸存样本**上照常出分。这类 run 的分数没有“错”，但它测的是一个自选样本，不能跟全量 run 放在一张表里比。

- `deepseek-v4-pro`：只有 0 / 3003 题进入判分（未判分 100.0%）。
- `glm-5.2`：只有 0 / 3003 题进入判分（未判分 100.0%）。

## 二、这个评测是什么

**一句话**：LongTutor 任务一：跨 7 天以上的学生历史里做单记录抽取 / 跨 session 推理 / 幻觉检查。

- **出处**：LongTutor 上游发布（无 LICENSE，勿再分发数据）；见 AGENTS.md 的 LongTutor 段。
- **数据**：`prepare_longtutor.py` 用上游 feature 代码重建 `history_features_lastq_scale.jsonl` 并校验 stable-key join；人工金标用 `human_an_updated.jsonl`（1,000 行），3,003 条问题。
- **任务与判分**：先做归一化精确匹配，不中才叫裁判判语义等价（走 `--extractor-model` 客户端）。主指标：按 query 类型分的语义正确率。
- **adapter**：`scripts/eval/benchmarks/longtutor.py`
- **局限**：**离线长历史重放，不代表真实长期学习增益**；三个任务不许平均成一个分。

**怎么用**：

```bash
MODEL=<model> ./scripts/run_eval.sh longtutor_evidence
# 或：python scripts/eval_benchmark.py --benchmark longtutor_evidence --model <model> --limit 0
```

## 三、当前映射（M3 裁决相关）

`reports/atomic_ability_rebenchmark_2026-07-08/02_benchmark_ability_mapping.jsonl` 里没有这个 benchmark 的条目——它当前**不进能力雷达**。

---

审计脚本：`python scripts/audit_eval_artifacts.py --benchmark longtutor_evidence --verbose`（离线、幂等、有 unusable 时退出码非 0）。

<!-- 以下为人工撰写内容，build_eval_readmes.py 不会覆盖 -->

# LongTutor 历史证据获取评测

本目录保存 LongTutor 历史证据获取任务的评测产物。任务包含单记录信息提取、跨记录推理和
幻觉检查三个维度，主指标为语义正确率。

判分先在本地执行归一化精确匹配；候选答案与人工参考答案一致时不调用大模型。只有精确匹配
失败时，才调用语义裁判判断答案是否保持相同核心含义。语义裁判只接收问题、参考答案和候选
答案，不重复输入完整学习历史。

语义裁判调用不设置 `max_tokens`，避免推理模型在输出最终判断前耗尽额度。裁判缓存记录裁判
模型和提示词版本；更换裁判模型或提示词时，只重新执行裁判与评分阶段，不重新生成被测模型
答案。

本任务不得与 LongTutor 的知识状态诊断、教学行动任务合并计算单一总分。
