# Current repository architecture

This document describes the current data flow. It is intentionally shorter than
benchmark profiles and historical decision records.

## Four layers

### 1. Specifications and evidence

Versioned benchmark specifications, mappings, manifests, and fixed item lists
live under `data/`. Human-readable research and methodology live under `doc/`.
External datasets and source material live under `sources/`.

The historical D01-D24 / S1-S8 benchmark and RE_BENCHMARK_V1 remain preserved.
The current cross-benchmark capability profile uses P01-P20, whose
machine-readable source of truth is `data/mapping_measurement_model_v6.json`.

### 2. Per-benchmark evaluation

The normal entry point is `scripts/run_eval.sh`, which dispatches to
`scripts/eval_benchmark.py` and the framework under `scripts/eval/`.

```text
adapter.load_items
       ↓
adapter.build_messages
       ↓
prediction provider
       ↓
answer extraction or LLM judge
       ↓
adapter.score and extra_summary
       ↓
JSONL evidence + summary.json + report.html
```

Benchmark adapters are registered in
`scripts/eval/benchmarks/__init__.py`. That registry, rather than a prose list,
is authoritative for the currently supported benchmark IDs.

### 3. Evaluation evidence

Rule-scored results use:

```text
reports/eval/<benchmark>/<model-slug>/
```

LLM-judged results make the judge a first-class path dimension:

```text
reports/eval/<benchmark>/judge-<judge-slug>/<model-slug>/
```

A normal run may contain:

- `predictions.jsonl` and rolled `predictions.partN.jsonl` shards;
- `extractions.jsonl`;
- `scored.jsonl`;
- `summary.json`;
- `report.html`.

`summary.json` is the aggregate and completion source of truth. A prediction
file, log, process, or directory name alone does not establish completion.

### 4. Atomic-ability reporting

The current reporting pipeline joins eligible evaluation summaries to the
P01-P20 measurement model, normalizes benchmark metrics, selects compatible run
evidence, aggregates cells and facets, and emits Markdown, JSONL, and HTML
artifacts.

Run the pipeline in the documented order:

```bash
python3 scripts/build_edubench_metric_summaries.py
python3 scripts/build_atomic_ability_rebenchmark_artifacts.py
python3 scripts/build_mapping_validation.py
python3 scripts/build_atomic_ability_html_report.py
python3 scripts/build_l1_floor_profile.py
```

The current outputs live in `reports/atomic_ability_rebenchmark/` and
`reports/atomic_ability_l1_floor/`; historical R-series directories are
immutable comparison snapshots.

## Identity dimensions that must remain separate

An evaluation result is not identified by model name alone. Depending on the
benchmark, its meaning can also depend on:

- benchmark and subtask;
- tested model and provider;
- judge model;
- prompt or rubric version;
- standard versus no-image input;
- fixed item list or full set;
- generation parameters;
- mapping revision used for downstream aggregation.

The repository records these dimensions in paths, `summary.json`, prompt hashes,
and manifests. Never collapse two incompatible identities into one directory or
one score.

## Generated versus authored content

Generators should be idempotent and overwrite their declared outputs. Generated
files are changed through their source or generator, while authored methodology
and decision records are edited directly.

When unsure which side a file is on, check its header, sibling README, generator
references, and Git history before editing it.

## Historical boundaries

The following coexist deliberately:

- D01-D24 / S1-S8: original benchmark specification generation;
- RE_BENCHMARK_V1 C1-C5: later runnable pilot organization;
- per-benchmark evaluation harness: independent benchmark execution;
- P01-P20: current cross-benchmark ability profile.

They are related, but they are not interchangeable schemas. Reports must name
which generation or revision they use.
