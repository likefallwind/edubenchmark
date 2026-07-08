# Inclusion Policy

## Main scoring layer

Include a model-run only when all conditions hold:

1. It is a benchmark/model result, not a judge calibration, jury calibration, rubric prompt experiment, or backup copy.
2. It has a concrete model name and a non-zero `total_items`.
3. It has at least 100 total items, unless a human explicitly promotes the run after inspection.
4. It maps to at least one `P01-P22` ability through `02_benchmark_ability_mapping.jsonl`.
5. If multiple judge versions score the same model responses, keep them as separate evidence rows until a judge policy is chosen. Do not average judge variants silently.

## Excluded by default

- Small samples and smoke tests: `total_items < 100`.
- Judge/rubric calibration: paths under `_judge_rubric`, `_judge_jury`, and benchmark ids containing `judge_calibration`.
- Backup directories such as `selfjudge_backup_*`.
- Protocol-only/data-resource rows without model scores.

## Foundation gate handling

MMLU-Pro, C-EVAL, AGIEval, OlympiadBench problem-solving style results are not
ignored. They map mostly to `P05` and `P06`, with smaller `P01/P03` components.
However, they are tagged as `foundation_gate` and receive lower default weights
in the five-axis education radar because high answer accuracy does not prove
teaching, diagnosis, personalization, or safety capability.

If later analysis shows no P ability cleanly captures a foundation result, add a
separate report band named `LLM答题门槛能力`, but do not add it as a sixth radar
axis unless the atomic-ability spec is revised.
