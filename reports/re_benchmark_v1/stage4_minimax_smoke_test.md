# Stage 4 MiniMax Smoke Test

MiniMax full pilot 已运行：139 条预测；自动题 29 条，正确 28 条，accuracy=0.966；开放/需复核 100 条；protocol-only 10 条。

## 运行设置

- Endpoint: `https://api.minimaxi.com/anthropic/v1/messages`

- Model: `MiniMax-M2.7`

- 非流式；当前 runner 不向 MiniMax 发送 `max_tokens`，用 HTTP timeout + retry 控制长请求。

- 当前 canonical 预测文件中的空响应/timeout 为 3 条；这类行需要结合 benchmark 类型解释。

## 评分口径

- 自动题使用 option extraction + normalized exact match。

- 开放教学题、安全题不使用模型 judge；只归档回答并写 qualitative samples。

- MMLU/AGIEval 选择题 prompt 从原始数据重建选项，要求只返回选项字母；protocol-only 项不进入普通问答评分。

- 当前 canonical 结果来自 2026-05-22 full-pilot rerun：并发 2、retry 2、显式 `--minimax-limit 999`。

- 本轮把完整 `pilot_items.jsonl` 里的 139 条都发给 MiniMax；其中代码题、多模态题需要专用 runner 或 adapter；C3 protocol/proxy 题已按 protocol-only 口径单列，不能当作普通 LLM prompt 分数。

## By Category

| category | auto_scored | correct | judge_required | protocol_required | missing |
| --- | --- | --- | --- | --- | --- |
| C1 | 29 | 28 | 20 | 0 | 0 |
| C2 | 0 | 0 | 30 | 0 | 0 |
| C3 | 0 | 0 | 10 | 10 | 0 |
| C4 | 0 | 0 | 20 | 0 | 0 |
| C5 | 0 | 0 | 20 | 0 | 0 |

## Empty/Error Rows

当前剩余空响应均应结合 benchmark 类型解释；本轮为空的行来自 `statics2011` KT protocol，不进入普通文本问答准确率。

| pilot_item_id | benchmark | runner_status | error |
| --- | --- | --- | --- |
| REBV1-0091 | statics2011 | auto_exact_match_candidate | The read operation timed out |
| REBV1-0093 | statics2011 | auto_exact_match_candidate | The read operation timed out |
| REBV1-0095 | statics2011 | auto_exact_match_candidate | The read operation timed out |
