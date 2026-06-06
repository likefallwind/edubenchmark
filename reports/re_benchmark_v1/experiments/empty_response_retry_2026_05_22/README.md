# Empty Response Retry - 2026-05-22

## Scope

This experiment reran the 17 empty-response items from the MiniMax full pilot rerun on 2026-05-20.

- Model: `MiniMax-M2.7`
- Items rerun: 17
- Concurrency: 2
- Timeout: 180 seconds
- Retries: 3
- Source run: `reports/re_benchmark_v1/experiments/minimax_full_pilot_rerun_2026_05_20/`

## Retry Result

| metric | value |
| --- | --- |
| Rerun items | 17 |
| Non-empty responses recovered | 7 |
| Still empty after retry | 10 |
| API errors | 0 |
| Auto-scored retry items | 8 |
| Correct among retry auto items | 1 / 8 |
| Format OK among retry auto items | 1 / 8 |

Still-empty items by benchmark:

| benchmark | empty count |
| --- | ---: |
| AGIEval | 6 |
| MMLU | 1 |
| STATICS2011 | 2 |
| EduGuard-Bench | 1 |

## Merged Full-Pilot Result

`merged_full_predictions.jsonl` starts from the 2026-05-20 full pilot predictions and replaces the original empty rows when this retry produced a non-empty response.

| metric | before retry | after merge |
| --- | ---: | ---: |
| Total predictions | 139 | 139 |
| Empty responses | 17 | 10 |
| Replaced rows | 0 | 7 |
| Auto-scored correct | 15 / 29 | 16 / 29 |
| MCQ format OK | 14 / 29 | 15 / 29 |

## Interpretation

The retry helped but did not eliminate empty responses. The remaining empty rows are concentrated in AGIEval, one MMLU item, two protocol-only STATICS2011 records, and one EduGuard item. Because the second pass used longer timeout and more retries, the remaining empties should be treated as MiniMax endpoint/model instability for this research run unless there is a reason to spend more API time.

## Files

- `empty_items.jsonl`: the 17 items selected for retry.
- `prompts.jsonl`: prompts used for the retry run.
- `predictions.jsonl`: retry-only MiniMax predictions.
- `run/scored_items.jsonl`: retry-only scoring.
- `merged_full_predictions.jsonl`: full 139-row prediction file with recovered responses merged in.
- `merged_run/scored_items.jsonl`: scoring for the merged 139-row file.
- `merged_run/run_summary.json`: merged full-pilot summary.
