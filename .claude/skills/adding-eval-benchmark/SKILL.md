---
name: adding-eval-benchmark
description: Use when the user gives a benchmark's paper or GitHub/HuggingFace URL and wants it added to the eval harness (新增 benchmark / 加评测 / integrate a benchmark), asks whether a benchmark is already covered or worth adding, or wants a new dataset wired into scripts/eval + the P01–P20 mapping.
---

# Adding a New Eval Benchmark

## Overview

Turn a benchmark (paper / GitHub / HF URL) into a runnable adapter in `scripts/eval/`, and — if the user wants — into the P01–P20 atomic-ability panel. **The work is five stages separated by user-confirmation gates. Never skip a gate; never jump ahead of a "no".** Stages 2+ only start after the user approves the recommendation from Stage 1.

Read `AGENTS.md`, `doc/repository_layout.md`, and `doc/current_architecture.md` before touching code. `CLAUDE.md` is the concise Claude Code entry point. This skill orchestrates that infrastructure; it does not replace it.

```
Stage 1  RESEARCH & RECOMMEND  ──gate──▶  Stage 2  IMPLEMENT + SMOKE TEST
   │  already added?  → tell user, STOP                 │ (default model MiniMax-M3)
   │  data unusable?  → log gap, STOP                    ▼
   └─ addable → recommend P-abilities + weights   gate ▶ Stage 3  FULL EVAL (1–3 models) + mount
                & CONFIRM → write doc/tochange/          │ (confirm smoke looks good first)
                (do NOT edit the final mapping yet)      ▼
                                               gate ▶ Stage 4  CURATED SET (ask; optional)
                                                        ▼
                                               gate ▶ Stage 5  RUN EVAL on curated set (ask; optional)
```

## Stage 1 — Research & recommend (always do this first)

1. **Is it already added?** Grep `scripts/eval/benchmarks/`, the registry in `scripts/eval/benchmarks/__init__.py`, `scripts/eval/data/fetch_eval_datasets.py`, and `CLAUDE.md`. Match on the dataset, not just the name (e.g. a Kaggle mirror of an existing corpus). If present → say so and **STOP**.
2. **Can the data actually be used?** Classify with the repo's source-status vocabulary (`local_ready` … `manual_kaggle_required` … `metadata_model_available_dataset_not_found`). Gated/unpublished data (Kaggle-required, HF-gated without terms, license-restricted, "data available on request") = an evidence gap. If unusable → record it in `benchmark-todo.md` and **STOP**. Do not pretend a gated set is reproducible.
3. **Is it worth adding?** State in one or two sentences what capability gap it fills versus current coverage, and whether it duplicates an existing cell. Recommend against adding a near-duplicate.
4. **Recommend the mount and CONFIRM.** Propose the concrete `(P-ability · facet · subdimension)` cells, each with two weights, then ask the user to confirm before any code:
   - **Relevance** (cell `weight`): `1.0` exact construct match · `0.8` strong · `0.5` moderate · `0.2` weak (must state the one-sentence signal) · not mounted at all otherwise.
   - **Confidence** (`default_benchmark_weight`): start `1.0`; **−0.15 if the actual scoring path is LLM-as-judge** (an LLM that only extracts an answer a rule then compares stays objective); **−0.15 if data/gold is self-built & self-judged** (external release / peer review / human annotation deducts nothing). Yields `1.0 / 0.85 / 0.7`. Never hand-pick the number — derive it and say why.
5. **On confirmation, stage the recommendation — do NOT edit the final mapping yet.** Write the confirmed cells + both weights + one-line rationale each to **`doc/tochange/<benchmark>.md`** (create the folder if missing). **Do not** touch `data/mapping_measurement_model_v6.json`, the final mapping docs, or `BENCHMARK_META`, and do not rerun the aggregation pipeline at this stage. The actual mount happens in Stage 3, after full runs exist. This keeps the final atomic-ability documents clean until there is real score evidence to mount.

## Stage 2 — Implement + smoke test (after confirmation)

Use the miniconda python for all fetch/eval commands (pandas/datasets live there — see memory `eval-python-interpreter`).

1. **Fetcher**: add a `--benchmark <name>` branch to `scripts/eval/data/fetch_eval_datasets.py` writing stdlib-readable JSONL (+ images) under `sources/datasets/<name>/` (gitignored). Materialize once.
2. **Adapter**: write `scripts/eval/benchmarks/<name>.py` — a `BenchmarkAdapter` subclass (see `base.py`). Copy the closest existing adapter as a template: MCQ → `ceval.py`/`mmlu_pro.py`; open-ended + LLM-judge → `mmtutorbench.py`/`mrbench.py`; population metric (QWK/κ) → `asap_2.py`. Implement `load_items` / `extract_answer` / `score` / `buckets`; override `build_messages` only if the default (text + images) is wrong. Set `title`/`homepage`/`description`. Port the **official** prompt + scoring where one exists; reimplement in `scripts/eval/scoring.py` (stdlib-only). Emit stable `item_id`s.
3. **Judge decoupling** (only if scoring is LLM-as-judge): a fixed judge via its own env var + `resolved_judge_model()`, decoupled from `--extractor-model`; add `judge_prompt_provenance()`. **Never set `max_tokens`** (starves reasoning models — memory `eval-no-max-tokens-cap-policy`).
4. **Register** in `scripts/eval/benchmarks/__init__.py`, and add a `run_eval.sh` case only if it needs judge/item-list/special wiring.
5. **Smoke test** with MiniMax-M3, small limit: first `--dry-run`, then real:
   ```
   python scripts/eval_benchmark.py --benchmark <name> --limit 3 --model MiniMax-M3 --dry-run
   LIMIT=5 MODEL=MiniMax-M3 ./scripts/run_eval.sh <name>
   ```
   Confirm `predictions.jsonl` / `extractions.jsonl` / `scored.jsonl` / `summary.json` / `report.html` look sane. Rule-scored runs use `reports/eval/<name>/minimax3/`; judged runs use `reports/eval/<name>/judge-<judge-slug>/minimax3/`. Run `python -m py_compile scripts/eval/benchmarks/<name>.py`.

## Stage 3 — Full eval (1–3 models) + mount (after smoke; confirm first)

**Gate: after the smoke test, show the user the smoke results and confirm they look good before running anything at scale.** Do not proceed on assumption.

1. **Run 1–3 models full** into the standard tree (no `--limit`, or `--limit 0`): `reports/eval/<name>/<model-slug>/` for rule-scored tasks, or `reports/eval/<name>/judge-<judge-slug>/<model-slug>/` for judged tasks. MiniMax-M3 first; add 1–2 more faces if the user wants them (this also gives the curated set its ≥3-face difficulty signal later). Verify provider and vision constraints against `scripts/eval/providers.py` and the relevant benchmark profile.
2. **Mount into the panel** (only if the user wants it on the P01–P20 radar): now apply the staged **`doc/tochange/<benchmark>.md`** recommendation into `data/mapping_measurement_model_v6.json` + a `BENCHMARK_META` entry, snapshot `reports/atomic_ability_rebenchmark/` to `*_vN_snapshot_YYYYMMDD/`, then rerun the 4-step aggregation pipeline (CLAUDE.md). Cells match by **exact `subdimension` string** — a rename silently drops the cell. Once applied, you may clear/mark the `doc/tochange/<benchmark>.md` entry as done.

## Stage 4 — Curated (精选) set (ask the user; optional)

Only if the user confirms, and only after the full runs of Stage 3 exist. Follow `doc/mini_selection_plan_2026-07-19.md`: sample at the **cell** level, stratified × difficulty-matched, fixed seed, to `data/mini_selection_v1/<name>_items_v1.txt` + manifest; offline-validate against acceptance standards (per-cell |Δ|≤0.3, per-P |Δ|≤0.2, ranking τ≥0.9 on distinguishable pairs, leave-one-out, sampling efficiency ≤1.3).

**Face-count caveat:** difficulty/discrimination signals require ≥3 model faces of full `scored.jsonl`. Stage 3's 1–3 full runs may not reach that. Until they do, either **content-stratify only** (the degraded path used for low-face-count sets) or **defer the mini set** and tell the user why. Tier by budget (A 10–15% hard-cut / B 30–50% / C 100% untouched) per the plan. **Discipline: never tune sampling against validation results** — every adjustment must have a reason that holds without looking at the numbers.

## Stage 5 — Run eval on the curated set (ask the user; optional)

Only if the user confirms. Run the mini set into the isolated parallel tree — never `reports/eval/`:
```
MINI=1 MODEL=MiniMax-M3 ./scripts/run_eval.sh <name>   # → reports/eval_mini_v1/<name>/minimax3/
```

## Common mistakes

| Mistake | Fix |
|---|---|
| Coding before the Stage 1 confirmation | Recommend abilities + weights, get "yes", then code. |
| Editing the final mapping in Stage 1 | Stage the recommendation in `doc/tochange/<benchmark>.md`; mount only in Stage 3 after full runs. |
| Running full eval before confirming smoke | Show smoke results, get "yes", then run 1–3 full models. |
| Building the curated set before full runs | Curated set is Stage 4 — it needs Stage 3's full `scored.jsonl` faces. |
| Treating gated/Kaggle-required data as usable | It's an evidence gap → `benchmark-todo.md`, STOP. |
| Hand-tuning the confidence weight | Derive from the two-factor rule (scoring method + data quality). |
| Capping `max_tokens` | Never — it starves reasoning models and fakes "empty reply" failures. |
| Judge = extractor model | Decouple the judge via its own env var + `resolved_judge_model()`. |
| Building a mini set with no multi-model faces | Content-stratify only, or defer; don't fake difficulty signals. |
| Running mini into `reports/eval/` | Use `MINI=1` → `reports/eval_mini_v1/`; it clobbers full results otherwise. |
| Renaming a cell after mounting | Aggregation matches exact `subdimension`; a rename silently drops the cell. |
| Skipping an optional stage the user *did* want | Stages 4 and 5 are gated by asking, not by assuming "no". |
