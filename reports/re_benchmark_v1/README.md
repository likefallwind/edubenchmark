# RE_BENCHMARK_V1 Reports

This folder contains the research reports and model-run artifacts for RE_BENCHMARK_V1.

## Primary Reading Order

1. `2026-05-20_worklog.md` - what was done today and what to do next.
2. `RE_BENCHMARK_V1_RESEARCH_REPORT.md` - overall research conclusion.
3. `stage1_data_status.md` - dataset availability and manifest status.
4. `stage2_data_acquisition_and_proxy.md` - missing data and proxy decisions.
5. `stage3_pilot_set_design.md` - pilot-set design and field meanings.
6. `stage4_minimax_smoke_test.md` - MiniMax run scope and scoring caveats.
7. `v2_roadmap.md` - recommended next version priorities.

## MiniMax Outputs

- `minimax_predictions.jsonl`: full-pilot raw predictions.
- `minimax_auto_scores.jsonl`: score rows for the full pilot.
- `minimax_full_pilot_report.html`: browser-friendly full-pilot report.
- `minimax_qualitative_samples.md`: examples for manual review.

## Experiments

Small, non-canonical experiments belong under `experiments/`.

Current experiment:

- `experiments/mcq_prompt_fix/`: tests whether MCQ prompts now elicit option-letter responses.
- `experiments/minimax_full_pilot_rerun_2026_05_20/`: full 139-item MiniMax rerun with the current pilot set and prompt logic.
- `experiments/empty_response_retry_2026_05_22/`: reruns empty responses from the full pilot and provides a merged 139-row prediction file.
- `experiments/no_maxtokens_empty_retry_2026_05_22/`: reruns remaining empty items after removing `max_tokens` from MiniMax benchmark test calls.
- `experiments/no_maxtokens_final_check_2026_05_22/`: final check of the last two empty rows; only the protocol-only STATICS item remains empty.
- `experiments/full_pilot_minimax_rerun_2026_05_22/`: full 139-item MiniMax-M2.7 rerun with no `max_tokens`, concurrency 2, and explicit `--minimax-limit 999`; auto-scored result is 28/29, with 3 remaining empty protocol-only STATICS rows.

Keep experimental files out of the root report directory unless they are final research deliverables.
