# No-MaxTokens Final Check - 2026-05-22

## Scope

This final check reran the two remaining empty rows after removing `max_tokens` from all MiniMax benchmark test calls.

| item | benchmark | result |
| --- | --- | --- |
| `REBV1-0132` | EduGuard-Bench | Recovered non-empty response: `A, B` |
| `REBV1-0090` | STATICS2011 | Still failed with read timeout |

## Result

`REBV1-0132` is now runnable with the no-`max_tokens` runner. The earlier empty response was caused by output-budget exhaustion during `thinking`.

`REBV1-0090` remains unsuitable as a normal MiniMax prompt. It is a knowledge-tracing protocol row, not a direct answerable item. Raw API diagnostics showed that MiniMax can generate a long protocol report for it, but runner-level calls can still hit read timeout. It should remain `protocol_required` and should not be counted as a text-prompt failure.

## Merged Full-Pilot Result

After merging the recovered `REBV1-0132` response:

| metric | value |
| --- | ---: |
| Total predictions | 139 |
| Empty responses | 1 |
| Auto-scored correct | 22 / 29 |
| MCQ format OK | 22 / 29 |
| Judge-required | 100 |
| Protocol-required | 10 |

The only remaining empty row is `REBV1-0090`, which is protocol-only.

## Files

- `items.jsonl`: the two checked items.
- `predictions.jsonl`: final-check predictions.
- `run/scored_items.jsonl`: final-check scoring.
- `merged_full_predictions.jsonl`: 139-row merged prediction file.
- `merged_run/scored_items.jsonl`: merged full-pilot scoring.
- `merged_run/run_summary.json`: merged full-pilot summary.
