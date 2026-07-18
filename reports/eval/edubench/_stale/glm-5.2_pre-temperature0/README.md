# glm-5.2 EduBench — 作废的半截 run(2026-07-18 之前的配置)

**这不是一次有效评测,不要用于任何对比,也不要被下游流水线读取。**
保留在这里只是作为"改配置会改变生成"的证据。

## 它是什么

2026-07-18 16:02 起跑、中途死掉的一次 glm-5.2 EduBench run,原位置在
`reports/eval/edubench/_judge-deepseek-v3.2/glm-5.2/`。

- `predictions.jsonl` — 2997 行(满额 3797),只有预测,判分那步从未开始
- `summary.json` — 状态卡在 `run_status: running`,进程已不存在

## 为什么作废

它生成于 EduBench adapter 对齐同事协议**之前**的配置,与现在的 run 至少差三处:

1. 没有 `temperature=0`(走服务端默认,GLM 系约 0.75)
2. 没有 predict 侧 system prompt `You are a helpful educational assistant.`
3. judge prompt 是旧的简版(无分档锚点),维度表也是 official 而非 colleague 那套

实测确认过:同 5 道题用新配置重跑,与这里的旧结果**没有一条相同**,
逐字符相似度只有 0.10–0.57,其中一条从 380 字变成 1080 字。

## 有效的 run 在哪

`reports/eval/edubench/_judge-deepseek-v3.2/glm-5.2/`(重跑后),
与同事导入的 11 个模型并排,题单、judge prompt、判分口径均已逐字节对齐。
