# Stage 4 MiniMax Smoke Test

MiniMax full pilot 已运行：139 条预测；自动题 29 条，正确 16 条，accuracy=0.552；开放/需复核 100 条；protocol-only 10 条。

## 运行设置

- Endpoint: `https://api.minimaxi.com/anthropic/v1/messages`

- Model: `MiniMax-M2.7`

- 非流式；MCQ/短答 256 tokens，开放教学/安全题 1024 tokens，长推理/代码保留 2048 token 预算。

## 评分口径

- 自动题使用 option extraction + normalized exact match。

- 开放教学题、安全题不使用模型 judge；只归档回答并写 qualitative samples。

- MMLU/AGIEval 选择题 prompt 从原始数据重建选项，要求只返回选项字母；protocol-only 项不进入普通问答评分。

- 注意：当前报告重算的是已有 MiniMax 预测；这些历史预测可能来自修复前的统一 wrapper prompt。严格模型结论需要用当前 `pilot_prompts.jsonl` 重新发起 MiniMax run。

- 本轮把完整 `pilot_items.jsonl` 里的 139 条都发给 MiniMax；其中代码题、多模态题需要专用 runner 或 adapter；C3 protocol/proxy 题已按 protocol-only 口径单列，不能当作普通 LLM prompt 分数。

## By Category

| category | auto_scored | correct | judge_required | protocol_required | missing |
| --- | --- | --- | --- | --- | --- |
| C1 | 29 | 16 | 20 | 0 | 0 |
| C2 | 0 | 0 | 30 | 0 | 0 |
| C3 | 0 | 0 | 10 | 10 | 0 |
| C4 | 0 | 0 | 20 | 0 | 0 |
| C5 | 0 | 0 | 20 | 0 | 0 |
