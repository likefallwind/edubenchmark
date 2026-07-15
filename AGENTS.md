# Repository Guidelines

## Project Structure & Module Organization

This repository is a research and benchmark-specification workspace for AI education evaluation. Root Markdown/HTML files such as `AI_EDU_BENCHMARK_V1.md`, `re_benchmark_v1.md`, and `edu_benchmark_survey.md` are human-readable entry points. Machine-readable assets live under `data/`; RE_BENCHMARK_V1 assets live in `data/re_benchmark_v1/`. Generated reports belong in `reports/`, with RE reports in `reports/re_benchmark_v1/`. Small prompt/model experiments should go under `reports/re_benchmark_v1/experiments/<experiment_name>/`. Generation and runner code belongs in `scripts/`. Downloaded datasets belong in `sources/datasets/` and should not be committed.

## Build, Test, and Development Commands

Regenerate Benchmark v1:

```bash
python scripts/build_benchmark_v1_2026_05_18.py
```

Validate Benchmark v1 structure only:

```bash
python scripts/build_benchmark_v1_2026_05_18.py --validate-only
```

Regenerate RE_BENCHMARK_V1 research reports:

```bash
python scripts/generate_re_benchmark_v1_research.py
```

Export prompts and rescore existing predictions:

```bash
python scripts/run_re_benchmark_v1.py --export-prompts data/re_benchmark_v1/pilot_prompts.jsonl --predictions reports/re_benchmark_v1/minimax_predictions.jsonl
```

Run MiniMax only after setting `MINIMAX_API_KEY`; keep concurrency at 2:

```bash
python scripts/run_re_benchmark_v1.py --run-minimax-smoke --minimax-selection all --minimax-concurrency 2 --minimax-retries 2
```

## Coding Style & Naming Conventions

Use Python 3, four-space indentation, and standard-library-first implementations. Prefer JSONL for row-oriented benchmark data and Markdown/HTML for reports. Keep dated snapshot names such as `benchmark_v1_2026-05-18` or `*_2026_05_18.py`. Report proxy data, missing data, gated access, and protocol-only items explicitly. For MCQ prompts, reconstruct options from source data when possible and ask for an option letter; track answer correctness separately from format compliance.

**Model `max_tokens` policy — do not cap.** Never set a `max_tokens` ceiling for any model on any call (prediction, extraction, or LLM-as-judge) unless explicitly required. A cap starves reasoning models: `MiniMax-M3` spends the budget on hidden `reasoning_content` and returns empty `content`, which then surfaces as spurious "empty reply" / "unparsed" judge failures and silent fake-fail scores. In code, `extraction_max_tokens()` always returns `None` and `--max-tokens` defaults to `None`. The sole exception is `deepseek-v3.2` (pinned to `32768` via `_MODEL_PARAMS`), a hard gateway requirement, not a starvation cap.

## Testing Guidelines

There is no dedicated test suite yet. Use script-level validation and syntax checks:

```bash
python -m py_compile scripts/*.py
python scripts/build_benchmark_v1_2026_05_18.py --validate-only
```

For runner or prompt changes, run a small sample first and write outputs to `reports/re_benchmark_v1/experiments/<name>/`. Preserve raw `predictions.jsonl`, `run_summary.json`, and `scored_items.jsonl`.

## Commit & Pull Request Guidelines

Commit history uses short imperative summaries such as `Add ...`, `Update ...`, `Remove ...`, and `Refactor ...`. Keep commits scoped to one research artifact or script change. Pull requests should list changed reports/data, commands run, regenerated files, and known limitations such as proxy substitutions, judge-required tasks, or missing multimodal assets.

## Security & Configuration Tips

Use environment variables for credentials such as `MINIMAX_API_KEY`. Treat Kaggle, Hugging Face gated datasets, Google Drive links, and manual-access resources as external dependencies; document access state in manifests instead of embedding private files.
# LongTutor integration

LongTutor is integrated as an offline long-history benchmark, not as evidence of
real longitudinal learning gain. Its upstream repository and approximately 76 MB
of released data belong under `sources/datasets/longtutor/`, which is the shared
location for downloaded datasets and must remain uncommitted. The upstream release
currently has no `LICENSE` file, so do not redistribute its data without explicit
permission.

Acquire and prepare the data:

```bash
python scripts/eval/data/fetch_eval_datasets.py --benchmark longtutor
python scripts/eval/data/prepare_longtutor.py
```

The upstream release omits `history_features_lastq_scale.jsonl`; the preparation
script rebuilds it with the upstream feature code and verifies that its stable keys
join to the human gold. Keep human gold and automatically generated pipeline data
separate in reports.

Upstream generation clarification (received 2026-07-13): the released
`human_an_updated.jsonl` has 1,000 gold rows and `pipeline_an_scale.jsonl` has
2,437 generated rows, but both contain annotations only. Neither contains the
history/current-question input. The authors confirmed it must be regenerated from
`sequences_long.jsonl` and `questions.jsonl` with `compute_history_stats.py`, using
the XES3G5M concept-segmentation implementation commented out at the top of that
script; its active implementation is for MOOCRadar. The preparation script applies
that XES3G5M function, recovers the sampled intermediate trajectory prefixes from
the stable `_key`, and verifies the join. For the 1,000 human evaluation samples,
use `human_an_updated.jsonl` as gold, not `pipeline_an_scale.jsonl`. It must still
fail rather than fabricate inputs if the stable-key join is empty.

Run the three native task views with MiniMax-M3:

```bash
MODEL=MiniMax-M3 JUDGE_MODEL=MiniMax-M3 LIMIT=5 ./scripts/run_eval.sh \
  longtutor_evidence longtutor_diagnosis longtutor_teaching
```

Outputs follow the standard layout:

```text
reports/eval/longtutor_evidence/minimax3/
reports/eval/longtutor_diagnosis/minimax3/
reports/eval/longtutor_teaching/minimax3/
```

Do not average the three tasks into one score. Report Evidence semantic accuracy
by query type, Diagnosis Macro-F1 plus accuracy, and Teaching's four rubric scores.
Future work should add full/recent/relevant/shuffled/no-history ablations. A truly
longitudinal benchmark with persistent learner state, delayed post-tests, or a
student simulator is a separate protocol and may justify a separate repository.
