# MiniMax MCQ Prompt Fix Small Test

Date: 2026-05-20

## Goal

Check whether the revised multiple-choice prompt fixes the earlier issue where MiniMax explained its reasoning instead of returning a direct option.

The prompt now reconstructs MMLU/AGIEval options from source data and asks:

```text
Answer the following multiple-choice question.
Return only the option letter. Do not explain.
...
Answer:
```

## Sample

Six items were tested:

| benchmark | items |
| --- | --- |
| AGIEval | REBV1-0014, REBV1-0015, REBV1-0016 |
| MMLU | REBV1-0011, REBV1-0023, REBV1-0024 |

## Result

| run | prompt style | answer correct | format ok | empty responses | conclusion |
| --- | --- | --- | --- | --- | --- |
| `simple` | simple clear MCQ prompt | 4/6 | 4/6 | 1/6 | Best result. AGIEval returned clean letters; MMLU still had one empty response and one reasoning response. |
| `max_tokens_8` | simple prompt with very small output budget | 0/6 | 0/6 | 4/6 | Worse. Truncation and empty responses increased. |
| `over_strict_system` | over-strict prompt + system constraint | 1/6 | 0/6 | 3/6 | Worse. Extra strictness increased empty/truncated reasoning outputs. Do not use this direction. |

## Interpretation

The benchmark prompt construction issue is fixed: choices are present, labels are explicit, and the model is clearly asked to return the option letter.

The remaining issue is MiniMax behavior under this endpoint/model. On the simple prompt, it follows the requested MCQ format on 4/6 items. When it still returns reasoning or an empty response, that should be recorded as model/API behavior rather than hidden by prompt hacks.

Scoring now separates:

- `score`: whether the extracted answer matches the gold option.
- `format_ok`: whether the raw response is just an option letter.

This lets us report answer correctness and instruction-following separately.

## Files

- Simple-prompt run: `reports/re_benchmark_v1/experiments/mcq_prompt_fix/simple/`
- Max-token comparison: `reports/re_benchmark_v1/experiments/mcq_prompt_fix/max_tokens_8/`
- Over-strict comparison: `reports/re_benchmark_v1/experiments/mcq_prompt_fix/over_strict_system/`

Each run directory contains `predictions.jsonl` and `run/scored_items.jsonl`.
