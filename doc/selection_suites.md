# Selection suites

This document defines the current relationship between the full benchmark
evidence, the representative mini suite, and the frontier challenge suite.  The
two selected suites are versioned measurement artifacts, not alternate names for
the full benchmark.

## Suite contracts

| Suite | Purpose | Current size | Selection principle | Score interpretation |
|---|---|---:|---|---|
| Full | Calibration authority and high-stakes reporting | Native benchmark sizes | No item filtering | Canonical benchmark result |
| `mini_v2` | Fast representative capability screen | 4,950 items / 39 benchmarks | Benchmark budgets plus internal subject/task/grade/type coverage | Screening profile; not a full-score proxy |
| `frontier_v1` | Challenge set for current and future frontier models | 4,919 items / 39 benchmarks | Unanimous failures, mixed model outcomes, and at most about 5% unanimous passes | Challenge and separation signal; not population representative |

Do not mix the three suites' raw scores in one unlabeled ranking.  A model can
score lower on `frontier_v1` simply because that suite intentionally concentrates
errors and disagreements.

## Shared coverage contract

Both selected suites cover all 39 current benchmark members:

- 36 benchmarks have deterministic item lists;
- EduIllustrate (230), EduEquity (400), and SafeChild (200) are fixed-full
  coverage anchors because their small internal structures are worth preserving;
- all 36 benchmarks in the current P01-P20 mapping are present;
- all 32 non-empty atomic-ability facets and all 104 measurement-cell source
  memberships are represented.

The atomic checks establish that a mapped evidence source is present.  They do
not establish that a selected score reproduces the full score, that every facet
has multiple independent sources, or that a structural measurement gap has been
filled.

## `mini_v2`: representative screening

`mini_v2` uses explicit per-benchmark item budgets rather than a single global
sampling percentage.  Commodity or very large banks such as MMLU-Pro and
K12Bench receive small caps, while distinctive education, tutoring, safety,
multimodal, calibration, and diagnosis tasks retain coverage.

Within each benchmark, deterministic stratification preserves the declared
subject, task, language, grade, modality, answer-type, or other consumed axes.
The resulting suite is suitable for routine screening and capability profiling,
but small-sample score drift and model-rank changes remain expected.  Full runs
are required for release decisions, safety failures, and small ranking gaps.

The `core`, `frontier`, and `judge` values in the manifest are execution profiles
inside one unified collection.  They control batching only; they do not change
suite membership.  Judge-calibration workflows are evaluator quality control,
not tested-model benchmarks, and are not counted as suite items.

## `frontier_v1`: errors and model separation

`frontier_v1` reuses the per-benchmark budget ceilings from `mini_v2`, but changes
the within-benchmark objective.  It classifies each item using a fixed repository
frontier-model cohort and a normalized pass threshold of 0.5:

- `unanimous_failure`: every available frontier-panel model is below threshold;
- `mixed_outcome`: at least one model is above and one below threshold;
- `unanimous_pass`: every model is above threshold.

The target mix is 35% unanimous failure, 60% mixed outcome, and at most about 5%
unanimous pass.  A benchmark budget is a ceiling, not a fill target: when error
and disagreement pools are exhausted, the builder leaves capacity unused rather
than padding with easy items.  The current sampled portion is 27.8% unanimous
failure, 67.3% mixed outcome, and 4.8% unanimous pass; the three fixed-full
coverage anchors are reported separately from these shares.

Unanimous failures track future capability boundaries but do not distinguish
current models.  Mixed-outcome items carry the main current-model ranking signal.
Long tails of tiny labels are pooled for coverage when a level has fewer than 10
eligible items, preventing dozens of rare topic names from forcing easy padding.

The eligible frontier cohort is frozen in the builder manifest.  Each benchmark
uses up to five available complete faces from that cohort.  SAS-Bench currently
has only two such faces, so its frontier item labels are explicitly low-confidence.
LLM-judged item labels are also conditional on the current judge and should be
rechecked across judges before external release.

## Files and regeneration

Machine-readable item lists and manifests:

```text
data/mini_selection_v2/
data/frontier_selection_v1/
```

Generated selection and validation reports:

```text
reports/mini_selection_v2/
reports/frontier_selection_v1/
```

Rebuild and validate without API calls:

```bash
python scripts/build_mini_selection_v2.py
python scripts/validate_mini_selection_v2.py

python scripts/build_frontier_selection_v1.py
python scripts/validate_frontier_selection_v1.py
```

The builders read existing full per-item evidence under `reports/eval/` and do
not modify it.  Edit the builder or this authored methodology document, then
regenerate manifests, item lists, and reports; do not hand-edit generated files.

## Versioning and release rules

- A frozen item list is part of the measurement definition.  Changing selected
  IDs, the frontier cohort, thresholds, quotas, or coverage policy requires a
  new suite version and a full regeneration of its validation artifacts.
- Record the suite version, manifest hash, tested model/provider, judge, and
  prompt/rubric version with every run.
- Validate a frontier revision on held-out or newly released models before
  claiming future-facing separation.
- Until a suite is wired into a canonical run profile, its manifest and item
  lists define selection membership; `reports/eval/**/summary.json` remains the
  completion truth for actual model runs.
