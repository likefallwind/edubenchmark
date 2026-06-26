# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A **research and benchmark-specification workspace** for AI-education evaluation, not a model-training or app codebase. The work is information collection, building a unified evaluation taxonomy, and indexing benchmark questions back to their original sources. The default language for reports and content is Chinese; scripts and code are English.

`AGENTS.md` holds the canonical contributor conventions (commit style, coding style, PR expectations). Read it for anything not covered here.

## The two benchmark generations

There are two parallel benchmark efforts. Know which one a task targets:

1. **Benchmark v1** (`*_2026_05_18`): the original spec built around **8 top-level scales (S1–S8)**, **24 atomic capabilities (D01–D24)**, 84 evaluation criteria, and 840 sampled items. Entry point `AI_EDU_BENCHMARK_V1.md`.
2. **RE_BENCHMARK_V1** (`re_benchmark_v1`): the newer **five-category** main-test reorganization (C1–C5), plus a runnable pilot package and a MiniMax smoke-test runner. Entry point `re_benchmark_v1.md`.

Both reuse the same D01–D24 capability taxonomy defined in `data/benchmark_metric_dimensions_2026-05-12.json` and the indicators in `data/benchmark_metric_indicators_2026-05-12.json`.

## Architecture: generate → emit triple → report

Every `scripts/build_*.py` follows the same pipeline and is **idempotent** — it reads taxonomy/source JSON, constructs candidate items, scores them, and overwrites its outputs. Never hand-edit generated files; change the build script and rerun.

- `build_benchmark_v1_2026_05_18.py`: taxonomy → candidate items (up to 80 per criterion) → transparent heuristic `quality_score` → keep top 10 → emit `items.jsonl` / `capability_criteria.jsonl` / `source_manifest.jsonl` plus the root `AI_EDU_BENCHMARK_V1.{md,html}` and `ai_edu_benchmark_v1_questions.json` and the `reports/2026-05-18/` spec.
- `build_exhaustive_2026_05_13.py`: emits the survey evidence base under `data/exhaustive_2026-05-13/` (benchmarks, metrics, results, dimension_mapping, dataset_acquisition) and `reports/2026-05-13/`.
- `build_re_benchmark_v1.py`: emits `data/re_benchmark_v1/` registry, source manifest, and pilot items.

Each item carries `source_file` + `source_row_or_key` for traceability back to a local dataset row. **`coverage_status: coverage_gap`** means an item is only a proxy / resource-construction sample — local material exists but the native benchmark label, licensed data, or multimodal/log resource does not. Do not treat coverage_gap items as full native coverage.

### Source status vocabulary

Manifests classify each source by access state, and this distinction is load-bearing throughout the repo: `local_ready`, `downloadable_not_local`, `manual_kaggle_required` / `manual_access_or_metadata_only`, `metadata_model_available_dataset_not_found`, `local_ready_but_no_pilot_extractor`. Gated/unpublished data (Kaggle ASAP, EssayJudge, HF-gated TutorBench/Pedagogy Benchmark) is recorded as an evidence gap — never assume it is reproducible.

### The runner (RE_BENCHMARK_V1)

`scripts/run_re_benchmark_v1.py` exports prompts, runs the MiniMax smoke test, and scores predictions. It separates three outcomes: **exact-match auto-scoring** for text items, **judge-needed** accounting for rubric/multimodal/code/safety items, and **format compliance** tracked separately from answer correctness. Predictions JSONL: `{"item_id": ..., "response": ..., "model": ...}`. For MCQ, options are reconstructed from source data and the model is asked for an option letter.

## The per-benchmark eval framework (`scripts/eval/`)

A separate, extensible harness for evaluating **one benchmark at a time** against an API model. It is deliberately decoupled from the dated build scripts and from `run_re_benchmark_v1.py` (which is text-only and refuses image items). Pipeline: **load items → call model (text [+ images]) → LLM answer extraction → score → report** under stable per-benchmark directories: `reports/eval/<benchmark>/<model-slug>/`.

- Entry point `scripts/eval_benchmark.py --benchmark <name>`. Phases are resumable/incremental: `predictions.jsonl` and `extractions.jsonl` are keyed by `item_id` and skipped on rerun; `--skip-extract` stops after predictions, `--score-only` reuses predictions, `--dry-run` prints constructed messages (base64 images elided) without calling the API.
- **Multi-provider** (`scripts/eval/providers.py`): one `MiniMaxClient` drives several OpenAI-compatible backends; `--model` is mapped to a provider by name prefix (longest match wins), unknown models fall back to the **gateway**. Three providers ship: `minimax` (`MINIMAX_API_KEY`, also home of the default extractor `MiniMax-M2.7`), `gateway` (a local relay at `http://127.0.0.1:8111/v1`, key env `API_GATEWAY`, serving `doubao-*`/`glm-*`/`deepseek-*` at `/chat/completions`), and `deepseek` (`https://api.deepseek.com`, key env `DEEPSEEK_API`, `deepseek-v4-pro`/`deepseek-v4-flash`). **`deepseek-*` models default to the gateway** (it serves them too); reach DeepSeek's official API only when specifically asked, via `--provider deepseek`. `--provider`/`--base-url`/`--api-key-env`/`--chat-path` override the auto-resolution for models not in the prefix table. Default prediction model is `MiniMax-M3`. (Gateway usage details + the `API_GATEWAY` non-interactive-shell gotcha live in memory `eval-gateway-multimodel`.)
- `scripts/eval/minimax_client.py`: MiniMax's OpenAI-compatible endpoint `<MINIMAX_BASE_URL or https://api.minimaxi.com/v1>/text/chatcompletion_v2`, `Authorization: Bearer $MINIMAX_API_KEY`. Sends vision via base64 `image_url` content parts. **Use a vision model (`MiniMax-M3`)** — `MiniMax-M2.7` (the anthropic-endpoint runner's default) is text-only. M3 is a reasoning model: its answer text lives in `message.content`, separate from `reasoning_content`; leave `max_tokens` unset for predictions and give extraction enough headroom (1024) so reasoning doesn't starve the answer.
- Add a benchmark by writing `scripts/eval/benchmarks/<name>.py` (a `BenchmarkAdapter` subclass: `load_items` / `build_messages` / `extract_answer` / `score` / `buckets`) and registering it in `scripts/eval/benchmarks/__init__.py`. The MathVista adapter ports the official `evaluation/` extraction (few-shot `ext_ans.demo_prompt`) and scoring (`normalize_extracted_answer` + nearest-choice edit distance), reimplemented in `scripts/eval/scoring.py` with no extra deps. MathVista needs images: `cd sources/datasets/mathvista/data && wget .../images.zip && unzip`.
- Registered C1 adapters and how each scores: **mathvista** (D06), **mmlu_pro** (D01, 10-option MCQ; official `answer is (X)` regex + LLM fallback; exact letter), **agieval** (D03, exam MCQ + math-cloze; choice-letter parse like official `post_process.py`, math via dynamically-loaded official `math_equivalence.is_equiv`), **olympiadbench** (D05, OE text+multimodal; prompt + scoring ported from the official repo — `make_prompt` and the sympy symbolic `AutoScoringJudge`, loaded directly from `sources/datasets/olympiadbench/`), **ceval** (D01, Chinese 52-subject 4-option MCQ from `ceval/ceval-exam`; scores the labeled **val** split — 1,346 items — since the official `test` answers are withheld; **official 5-shot answer-only** protocol ported from the repo's `evaluator_series` — each subject's 5 `dev` exemplars supplied as user/assistant turns with a bare-letter reply, so **no LLM extraction**: scoring reads the leading option letter and exact-matches like the official `response[0] == answer`; bucketed by category and subject).
- Registered **D21 safety adapters** (EduGuard-Bench, from a local clone of `github.com/YL1N/EduGuardBench`): **eduguard_sata** (P1 Teaching Harm; 2,635 bilingual Select-All-That-Apply items, *rule-scored* per official `run_p1_evaluation.py` — exact option-set match RFS=1, non-empty proper subset RFS=0.5, else 0; no judge) and **eduguard_adversarial** (P2 Adversarial Safety; 801 jailbreak prompts, *two-stage LLM-as-judge* ported from `run_p2_experiment.py` — harmful/harmless then refusal-quality tier, each stage a 3-vote majority/BoN=3; judge is `--extractor-model`, none hard-coded; reports ASR + refusal-quality distribution under `summary.json` → `extra_metrics`).
- Data acquisition for the parquet-only datasets: `python scripts/eval/data/fetch_eval_datasets.py --benchmark mmlu_pro|olympiadbench|eduguard_bench|ceval|all` materializes HF parquet/repo data into stdlib-readable JSONL under `sources/datasets/` (MMLU-Pro from the **public** `TIGER-Lab/MMLU-Pro`; the `TIGER-AI-Lab/MMLU-Pro` path is gated. OlympiadBench OE configs from `Hothan/OlympiadBench`, images extracted to `olympiadbench/images/`, TP proof configs skipped; eduguard_bench → `satas.jsonl`/`adversarial.jsonl`; ceval iterates the 52 `ceval/ceval-exam` subject configs → `ceval/data/{val,dev}.jsonl`, reading the subject→category map from the repo clone's `subject_mapping.json`). AGIEval data ships in its repo checkout.
- **OlympiadBench scoring needs `antlr4-python3-runtime==4.11`** (sympy `parse_latex`), which conflicts with `hydra-core`/`omegaconf` (they pin `4.9.*`) — run it in a dedicated venv if you use hydra. OmniEduBench (a C1/C3 main test) has no public data and is **not** adapted; the gap is logged in `benchmark-todo.md`.

## Common commands

```bash
# Validate structure only (fast, no rewrite) — do this before/after editing a build script
python scripts/build_benchmark_v1_2026_05_18.py --validate-only   # expects criteria=84 items=840 manifest=88

# Regenerate each generation
python scripts/build_benchmark_v1_2026_05_18.py
python3 scripts/build_exhaustive_2026_05_13.py                    # expects benchmarks=78 metrics=165 results=1616
python scripts/build_re_benchmark_v1.py

# RE_BENCHMARK_V1 runner: export prompts + score existing predictions
python scripts/run_re_benchmark_v1.py --export-prompts data/re_benchmark_v1/pilot_prompts.jsonl --predictions reports/re_benchmark_v1/minimax_predictions.jsonl

# MiniMax smoke test — requires MINIMAX_API_KEY; keep concurrency low
MINIMAX_API_KEY=... python scripts/run_re_benchmark_v1.py --run-minimax-smoke --minimax-selection all --minimax-concurrency 2 --minimax-retries 2

# Per-benchmark eval harness — provider auto-resolved from --model (prefix match)
MINIMAX_API_KEY=... python scripts/eval_benchmark.py --benchmark mmlu_pro --limit 30 --model MiniMax-M3 --concurrency 2
API_GATEWAY=... python scripts/eval_benchmark.py --benchmark eduguard_sata --model glm-5.1 --limit 0   # all items, gateway-served
python scripts/eval_benchmark.py --benchmark mathvista --limit 3 --dry-run   # no API calls; prints messages

# No test suite — validate with syntax + structure checks
python -m py_compile scripts/*.py

# Bulk dataset download (reads commands from the acquisition report; rewrites Gitee HTTPS→SSH)
COMMAND_TIMEOUT=1200 ./scripts/download_all_datasets.sh
FAILED_ONLY=1 COMMAND_TIMEOUT=300 ./scripts/download_all_datasets.sh   # retry failures only
```

## Conventions specific to this repo

- **Standard-library-first Python 3**, four-space indent. JSONL for row-oriented benchmark data; Markdown+HTML pairs for reports.
- **Dated snapshot names are intentional** (`benchmark_v1_2026-05-18`, `*_2026_05_18.py`). Don't rename or "clean up" the dates — they version the artifacts.
- Small model/prompt experiments go under `reports/re_benchmark_v1/experiments/<name>/`, preserving raw `predictions.jsonl`, `run_summary.json`, `scored_items.jsonl`.
- `sources/datasets/` holds downloaded dataset copies; it is gitignored and not committed.
- Credentials (e.g. `MINIMAX_API_KEY`) come from env vars only.

## Interpretation guardrails (from README)

- Never average raw scores across different benchmarks — map to D01–D24 capabilities first, then form a capability profile.
- General-knowledge benchmarks are gate items only; they do not prove teaching ability. Core teaching capability lives in error diagnosis, scaffolding, feedback quality, personalization, multimodal grounding, safety boundaries, and real learning outcomes.

## The edubenchassistant skill

`skills/edubenchassistant/SKILL.md` is an Agent skill: given an AI-education app/product/scenario, it uses this repo's evidence base to recommend which D01–D24 capabilities and S1–S8 scales matter, what prior benchmarks exist, native metrics/public results/data availability, and safety/contamination/rubric concerns — emitting an HTML report into `reports/edubenchassistant/`. Newly discovered evaluation gaps are logged to `benchmark-todo.md`.
