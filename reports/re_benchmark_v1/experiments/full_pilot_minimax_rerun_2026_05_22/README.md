# Full Pilot MiniMax Rerun - 2026-05-22

This experiment reran the full RE_BENCHMARK_V1 pilot set with MiniMax-M2.7.

## Run Configuration

- Runner: `scripts/run_re_benchmark_v1.py`
- Model: `MiniMax-M2.7`
- Selection: `all`
- Explicit limit: `999` to cover all 139 pilot items
- Concurrency: `2`
- Retry: `2` retries after empty/error responses
- Timeout: `180` seconds per request attempt
- `max_tokens`: omitted for all benchmark calls

The first invocation used the script default limit and therefore ran only 24 rows. The continuation run used `--minimax-limit 999` and filled the same `predictions.jsonl` to 139 rows.

## Outputs

- `prompts.jsonl`: exported prompts for all 139 pilot items
- `predictions.jsonl`: raw MiniMax responses for all 139 pilot items
- `run/scored_items.jsonl`: scoring and status rows
- `run/run_summary.json`: machine-readable summary
- `run/run_report.html`: browser-readable report

## Results

- Total pilot items: 139
- Predictions written: 139
- Empty/error responses: 3
- Auto-scored items: 29
- Auto-scored accuracy: 28/29 = 96.6%
- MCQ format compliance: 29/29
- Judge-required items: 100
- Protocol-required items: 10

Auto-scored breakdown:

| Category | Benchmark | Correct | Total |
| --- | --- | ---: | ---: |
| C1 | AGIEval | 18 | 19 |
| C1 | MMLU | 10 | 10 |

The only automatically scored miss was `REBV1-0036` from AGIEval. MiniMax returned `C`; the expected option was `A`.

## Remaining Empty/Error Rows

All remaining empty rows are from `statics2011` knowledge-tracing protocol items, not ordinary text QA prompts:

| Pilot item | Benchmark | Error | Attempts | Latency |
| --- | --- | --- | ---: | ---: |
| REBV1-0091 | statics2011 | The read operation timed out | 3 | 546.629s |
| REBV1-0093 | statics2011 | The read operation timed out | 3 | 546.706s |
| REBV1-0095 | statics2011 | The read operation timed out | 3 | 546.607s |

These should remain in the research report as protocol-required KT examples rather than being counted as text LLM benchmark failures.

## Interpretation

Removing `max_tokens` fixed the earlier MiniMax empty-final-text problem for normal text prompts and MCQ prompts. The tradeoff is runtime: long open-ended educational prompts can produce very long responses, and protocol-only KT prompts can still hit the wall-clock timeout.

For the next canonical run, protocol-only items should either be skipped by default or evaluated through a separate KT protocol runner, so MiniMax text QA accuracy is not mixed with non-LLM-native protocol tasks.
