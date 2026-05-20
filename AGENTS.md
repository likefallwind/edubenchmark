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
