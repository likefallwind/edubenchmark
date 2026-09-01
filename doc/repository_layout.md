# Repository layout

This document defines the role of each top-level directory. It is the directory
placement rule for contributors and automation; `README.md` provides the shorter
user-facing map.

## Placement principles

Before adding a file, decide whether it is a source, a generated artifact, a
runtime artifact, or historical evidence. Do not place the same class of file in
multiple top-level directories merely because a particular script happens to
run from there.

- Source files are edited directly and reviewed.
- Generated artifacts are changed through their generator or source data.
- Runtime artifacts describe a process invocation and are not research results.
- Historical snapshots are immutable evidence of an earlier method or result.

## Top-level directories

| Path | Purpose | Editing and lifecycle rule |
|---|---|---|
| `data/` | Repository-owned machine-readable specifications, mappings, manifests, item lists, and compact prepared assets | Edit authoritative source files deliberately; regenerate derived files through their build script. |
| `doc/` | Human-authored methodology, profiles, plans, operations, and current architecture documentation | Prefer a stable topic name for current documents. Put superseded material in `doc/old/`. |
| `scripts/` | Build, evaluation, import, validation, analysis, and reporting code | Reusable evaluation framework code belongs in `scripts/eval/`; one-off research experiments belong in `scripts/experiments/`. |
| `reports/` | Evaluation evidence, generated research reports, ability profiles, and immutable result snapshots | Follow `reports/README.md`. Do not hand-edit files identified as generated. |
| `sources/` | External source material: downloaded datasets, papers, pages, screenshots, and extracted text | `sources/datasets/` is for external dataset copies and remains uncommitted unless an explicit repository decision says otherwise. |
| `tests/` | Automated regression and contract tests | Keep tests deterministic and offline by default. API smoke tests are operational runs, not unit tests. |
| `skills/` | Skills published or distributed as repository deliverables | Keep product-facing skill instructions here. Tool-specific maintenance skills belong under the corresponding hidden tool directory. |
| `html_report/` | Stable top-level HTML presentation artifacts produced by reporting pipelines | Treat as generated output. The separation from `reports/` is historical; do not create a third HTML output root. |
| `otherbenchmark/` | Imported or externally produced benchmark result bundles retained for comparison | Treat as external comparison evidence, not native `reports/eval/` runs. Document provenance inside each retained bundle. |
| `eval/` | Local run-control artifacts for evaluation launches, such as queue scripts, status tables, and process logs | Runtime workspace only. Do not treat it as the evaluation framework (`scripts/eval/`) or result tree (`reports/eval/`). |
| `logs/` | Longer-lived operational logs and completion markers for named bulk runs | Logs are process evidence, not scored benchmark evidence. A `summary.json` remains the result source of truth. |
| `tmp/` | Short-lived repository-local scratch files | Nothing here is authoritative. A workflow relying on a temporary file must copy the final evidence to its proper destination. |

## Hidden project directories

| Path | Purpose |
|---|---|
| `.githooks/` | Repository Git hooks. Enable them with `git config core.hooksPath .githooks`. |
| `.claude/` | Claude Code settings and repository-maintenance skills. These supplement, but do not override, `AGENTS.md`. |
| `.agents/` | Reserved workspace for agent tooling. It currently defines no repository rules. |
| `.codex/` | Reserved workspace for Codex-specific project configuration. It currently defines no repository rules. |
| `.learnings/` | Recorded operational mistakes and reusable lessons. Treat them as supporting history, not as a competing instruction hierarchy. |
| `.cache/`, `.pytest_cache/` | Local tool caches. They are not project documentation or research artifacts. |

## Documentation locations

- Root `README.md`: public overview and quick start.
- Root `AGENTS.md`: canonical contributor and agent rules.
- Root `CLAUDE.md`: concise Claude Code entry point.
- `doc/benchmark_profiles/`: current benchmark-specific descriptions.
- `doc/ability_profiles/`: current P01-P20 ability descriptions.
- `doc/old/`: superseded documents retained for history.
- `reports/**/README.md`: interpretation and provenance of a result family.

Do not add a second root-level overview for a new workstream. Extend the current
README or add a focused document under `doc/`, then link it from the appropriate
entry point.

## Evaluation path contract

The word `eval` appears in three intentional locations:

```text
scripts/eval/   evaluation framework implementation
reports/eval/   scored evidence and reports
reports/eval_suites/   mini_v2/frontier_v1 materialized result views
eval/           local launch and run-control artifacts
```

Within `reports/eval/`:

```text
# Rule-scored benchmark
reports/eval/<benchmark>/<model-slug>/

# LLM-judged benchmark
reports/eval/<benchmark>/judge-<judge-slug>/<model-slug>/

# Isolated support or noncanonical result
reports/eval/<benchmark>/_<variant>/...
```

The path identifies the measurement. Do not mix different judges, input
variants, item lists, or incompatible generation settings in one run directory.
Suite views mirror the rule/judge namespace below
`reports/eval_suites/<suite>/<benchmark>/`; compatible per-item evidence may be
reused across these roots only when its recorded identity hashes match.

## Naming

- Use lower-case snake case for benchmark IDs and Python modules.
- Preserve external model names in metadata; use the repository's canonical
  slug helper for paths.
- Keep intentional dated snapshots and R-series labels unchanged.
- Use descriptive topic names under `doc/`; use dates when the document is a
  point-in-time status or decision record.
- Prefix noncanonical evaluation subtrees with `_` so collectors can distinguish
  them from ordinary result dimensions.
