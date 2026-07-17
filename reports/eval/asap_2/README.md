# ASAP 2.0 — imported evaluation artifacts

These runs were produced by another team and imported from `otherbenchmark/benchmark_raw_results_by_model_20260717/`. The source package is treated as immutable.

Primary metric: Quadratic weighted kappa (QWK) over the ASAP 2.0 test split; invalid/error rows are excluded from QWK and remain visible in status counts.

Each model directory contains `predictions.jsonl`, `scored.jsonl`, `summary.json`, and `report.html`. The normalized JSONL keeps raw model text and all scoring-relevant fields, but omits duplicated nested API response envelopes. `summary.json` records the original path and SHA-256 for traceability.
