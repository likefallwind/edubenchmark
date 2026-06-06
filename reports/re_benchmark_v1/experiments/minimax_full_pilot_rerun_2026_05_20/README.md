# MiniMax Full Pilot Rerun - 2026-05-20

## Run Scope

This rerun used the current `data/re_benchmark_v1/pilot_items.jsonl` and the latest prompt-generation logic in `scripts/run_re_benchmark_v1.py`.

- Model: `MiniMax-M2.7`
- Endpoint: `https://api.minimaxi.com/anthropic/v1/messages`
- Items: 139 / 139
- Concurrency: 2
- Retries: 2
- Run window: 2026-05-20 20:13-20:38 Asia/Shanghai

## Output Files

- `prompts.jsonl`: exported prompts used for this run.
- `predictions.jsonl`: raw MiniMax responses.
- `run/scored_items.jsonl`: scoring rows.
- `run/run_summary.json`: machine-readable summary.
- `run/run_report.html`: generic runner report.
- `report.html`: human-readable run interpretation.

## Key Results

| metric | value |
| --- | --- |
| Predictions | 139 |
| API errors | 0 |
| Empty responses | 17 |
| Items needing retry | 28 |
| Auto-scored items | 29 |
| Auto-scored correct | 15 / 29 |
| Auto-scored accuracy | 0.517 |
| MCQ format-compliant responses | 14 / 29 |
| Judge-required items | 100 |
| Protocol-only items | 10 |

## Auto-Scored Breakdown

| benchmark | auto-scored | correct | format_ok |
| --- | ---: | ---: | ---: |
| AGIEval | 19 | 10 | 9 |
| MMLU | 10 | 5 | 5 |

## Interpretation

The run confirms that the latest pilot set and MiniMax runner are operational end to end. The C1 automatic subset now has explicit MCQ prompts and separates answer correctness from format compliance.

This is still a research smoke/full-pilot run, not a leaderboard. C2/C4/C5 outputs require human or LLM judge review, and C3 protocol-only records should not be merged into text-prompt accuracy. Empty responses remain a stability issue even with retries.

## Next Step

Use this run as the baseline for manual review. Start with:

1. Review incorrect auto-scored MCQs to separate knowledge errors, format errors, and empty responses.
2. Sample 10-20 judge-required C2/C4/C5 items for human rubric notes.
3. Decide whether to rerun only empty responses with a higher timeout or accept them as API/model instability evidence.
