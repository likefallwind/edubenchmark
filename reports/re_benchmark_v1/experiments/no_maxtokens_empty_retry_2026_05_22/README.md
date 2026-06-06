# No-MaxTokens Empty Retry - 2026-05-22

## Scope

This experiment reran the 10 still-empty items after removing `max_tokens` from MiniMax calls in `scripts/run_re_benchmark_v1.py`. A follow-up raw API diagnostic showed the same issue can affect benchmark-embedded instruction items, so the runner now omits `max_tokens` for all MiniMax benchmark test calls.

The change was motivated by MiniMax documentation and raw API diagnostics: MiniMax-M2.7 may spend the whole `max_tokens` budget on `thinking` blocks before emitting a final `text` block. Omitting `max_tokens` lets the endpoint reach `end_turn` and return final text.

## Retry Result

| metric | value |
| --- | ---: |
| Rerun items | 10 |
| Non-empty responses recovered | 8 |
| Still empty | 2 |
| API-error rows | 1 |
| Auto-scored retry items | 7 |
| Correct among retry auto items | 6 / 7 |
| Format OK among retry auto items | 7 / 7 |

Remaining empty rows:

| item | benchmark | note |
| --- | --- | --- |
| `REBV1-0090` | STATICS2011 | protocol-only item; retry ended with error/empty |
| `REBV1-0132` | EduGuard-Bench | judge-required safety/role-play item; still empty |

## Merged Full-Pilot Result

`merged_full_predictions.jsonl` starts from the previous merged 139-row file and replaces original empty rows when this retry produced a non-empty response.

| metric | after previous retry | after no-maxTokens merge |
| --- | ---: | ---: |
| Total predictions | 139 | 139 |
| Empty responses | 10 | 2 |
| Newly replaced rows | 0 | 8 |
| Auto-scored correct | 16 / 29 | 22 / 29 |
| MCQ format OK | 15 / 29 | 22 / 29 |

## Interpretation

Removing `max_tokens` materially improves MiniMax behavior. Most prior empty MCQ responses were not true service failures; they were responses where the generation budget was exhausted by `thinking` before final `text`.

For future MiniMax runs:

- Do not send `max_tokens` for benchmark test calls.
- Rely on request timeout and retry controls for runaway calls.
- Continue to report `score` and `format_ok` separately.

## Files

- `empty_items.jsonl`: the 10 selected still-empty items.
- `prompts.jsonl`: prompts used in this retry.
- `predictions.jsonl`: retry-only predictions.
- `run/scored_items.jsonl`: retry-only scores.
- `merged_full_predictions.jsonl`: full 139-row merged prediction file.
- `merged_run/scored_items.jsonl`: merged full-pilot scores.
- `merged_run/run_summary.json`: merged full-pilot summary.
