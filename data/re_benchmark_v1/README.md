# RE_BENCHMARK_V1 runnable package

Generated from `re_benchmark_v1.md` and local `data/benchmark_v1_2026-05-18/items.jsonl`.

## Files

- `benchmark_registry.jsonl`: curated C1-C5 benchmark registry.
- `source_manifest.jsonl`: local/download/manual status for each benchmark.
- `pilot_items.jsonl`: local-first smoke test items.
- `pilot_prompts.jsonl`: prompt export for model calls.

## Registry status

- `downloadable_not_local`: 1
- `local_ready`: 10
- `manual_access_or_metadata_only`: 2
- `manual_kaggle_required`: 2
- `metadata_model_available_dataset_not_found`: 1
- `needs_acquisition_entry`: 4

## Pilot item counts

- `C1` 学科认知与问题求解: 49
- `C2` 教学设计与学习辅导: 30
- `C3` 学情建模与个性化: 20
- `C4` 作答评价与反馈: 20
- `C5` 教育安全与伦理合规: 20

## Next extraction work

Some benchmarks are local-ready in `source_manifest.jsonl` but currently have
`local_ready_but_no_pilot_extractor`. Those need benchmark-specific item
extractors before they can contribute to `pilot_items.jsonl`.

## Run

```bash
python scripts/build_re_benchmark_v1.py
python scripts/run_re_benchmark_v1.py --export-prompts data/re_benchmark_v1/pilot_prompts.jsonl
```
