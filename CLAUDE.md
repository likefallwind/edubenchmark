# CLAUDE.md

This file is the concise entry point for Claude Code in this repository. The
tool-independent contributor rules in `AGENTS.md` are canonical. Read them
first. Do not duplicate or override them here.

## Start here

Use these documents in this order:

1. `README.md` — project purpose, normal commands, and current public entry
   points.
2. `AGENTS.md` — mandatory repository, testing, Git, and security rules.
3. `doc/repository_layout.md` — what belongs in each top-level directory.
4. `doc/current_architecture.md` — current evaluation and reporting data flow.
5. The relevant benchmark profile under `doc/benchmark_profiles/` or ability
   profile under `doc/ability_profiles/`.

The former long-form Claude notes are preserved at
`doc/old/CLAUDE_operational_notes_2026-08-31.md`. Consult them only for
historical incidents or old run interpretation; verify drift-prone details
against the current code and artifacts before acting.

## Current project model

This is a research and benchmark-specification workspace for AI-education
evaluation. It has four related layers:

- dated benchmark specifications and evidence bases;
- the per-benchmark evaluation harness under `scripts/eval/`;
- evaluation evidence under `reports/eval/`;
- the current P01-P20 atomic-ability measurement and reporting pipeline.

Historical D01-D24 / S1-S8 and RE_BENCHMARK_V1 assets remain valid versioned
artifacts, but they are not the current P01-P20 ability-profile schema. Do not
silently translate between these generations.

## Load-bearing rules

- Never hand-edit generated artifacts. Change their source data or generator,
  then rerun the documented pipeline.
- Never set a `max_tokens` ceiling for prediction, extraction, or judging unless
  a repository rule explicitly requires it. The sole pinned exception is the
  gateway requirement already encoded for `deepseek-v3.2`.
- Credentials come from environment variables only. Never write keys into code,
  commands committed to Git, reports, or logs.
- `reports/eval/**/summary.json` is the completion and aggregate source of truth.
  Predictions alone do not prove a completed or scored run.
- A judged run belongs at
  `reports/eval/<benchmark>/judge-<judge-slug>/<model-slug>/`. A rule-scored run
  has no judge segment and remains at
  `reports/eval/<benchmark>/<model-slug>/`.
- Directories beginning with `_` inside an evaluation tree are isolated support,
  smoke, migration, baseline, or degraded-variant artifacts. Do not treat them
  as ordinary model results unless the relevant workflow explicitly says so.
- The current atomic-ability source of truth is
  `data/mapping_measurement_model_v6.json`. Aggregation matches cells by exact
  `subdimension` text; renaming one side can silently drop evidence.
- Preserve dated and R-series snapshots. They make method changes auditable and
  scores across incompatible revisions distinguishable.
- Keep human gold, model-generated annotations, proxy data, unavailable data,
  and protocol-only items explicitly separated in manifests and reports.
- Do not infer longitudinal learning gain, student understanding, or deployment
  readiness from offline response-quality scores.

## Common task routes

### Run an evaluation

Prefer the repository wrapper:

```bash
LIMIT=5 MODEL=MiniMax-M3 ./scripts/run_eval.sh mmlu_pro
```

Use the lower-level entry point only for options the wrapper does not expose:

```bash
python scripts/eval_benchmark.py --benchmark mmlu_pro --limit 3 --dry-run
```

The adapter registry in `scripts/eval/benchmarks/__init__.py` is authoritative
for supported benchmark names. Provider routing in `scripts/eval/providers.py`
is authoritative for current model routes; do not rely on an old prose list.

### Add a benchmark

Use `.claude/skills/adding-eval-benchmark/SKILL.md`. It defines the research,
confirmation, smoke, full-run, mapping, and optional curated-set gates. The
general repository rules still apply.

### Rebuild the atomic-ability outputs

Run in this order:

```bash
python3 scripts/build_edubench_metric_summaries.py
python3 scripts/build_atomic_ability_rebenchmark_artifacts.py
python3 scripts/build_mapping_validation.py
python3 scripts/build_atomic_ability_html_report.py
python3 scripts/build_l1_floor_profile.py
```

Read `reports/atomic_ability_rebenchmark/README.md` and the current mapping
document before changing this pipeline. A mapping revision and a structural
code refactor should be separate changes.

### Validate a documentation-only change

At minimum, check the worktree, Markdown links, and stale path vocabulary. Do
not run API evaluations or regenerate reports for a documentation-only task.

### Validate code changes

Use the narrowest relevant checks first:

```bash
pytest -q tests
python scripts/build_benchmark_v1_2026_05_18.py --validate-only
```

Run `py_compile` only when useful and remember that this repository has
historically tracked bytecode in some environments; inspect the worktree after
validation.

## Documentation authority

- `README.md` describes the current user-facing project.
- `AGENTS.md` contains stable contributor rules.
- `doc/repository_layout.md` defines directory ownership.
- `doc/current_architecture.md` defines current data flow and path contracts.
- `data/mapping_measurement_model_v6.json` is the machine-readable mapping fact
  source.
- `doc/atomic_ability_mapping_v6_2026-07-19.md` is the current readable mapping
  snapshot; older files under `doc/old/` are history.
- Benchmark-specific truth belongs in `doc/benchmark_profiles/<name>.md` and the
  adapter implementation, not in an ever-growing paragraph here.

When two prose files disagree, verify the code and machine-readable artifact,
then repair the stale prose instead of adding another competing explanation.
