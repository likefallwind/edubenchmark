"""Generic, per-benchmark evaluation framework (v1).

A thin, standard-library-first harness that evaluates one benchmark at a time
against an API model (MiniMax to start). The pipeline is:

    load items -> build request (text [+ images]) -> call model
    -> (optional) LLM answer extraction -> score -> report

Each benchmark plugs in a `BenchmarkAdapter` under `eval.benchmarks`.
"""
