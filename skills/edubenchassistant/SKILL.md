---
name: edubenchassistant
description: Use when a user describes an AI-education application, classroom/tutoring/grading scenario, or asks to run an evaluation on a benchmark (跑评测/评测某个 benchmark), evaluate model results, or produce an evaluation/assessment report (评估报告) — covering benchmark, metric, atomic-capability, dataset guidance AND running the eval framework + reporting its results
---

# EduBench Assistant

## Overview

This skill operates in two modes. Pick the one the request needs:

- **Advisory mode** — the user describes an AI-education product/scenario and wants an evaluation & product-readiness plan. Use the local evidence base to map to atomic capabilities, prior benchmarks, public model evidence, native metrics, dataset availability, gaps, and product implications. Deliver an HTML report and record benchmark gaps. (Sections: *Required Sources* through *Quick Benchmark Hints*.)
- **Evaluation mode** — the user wants to actually run a benchmark through the framework against a model and/or assess the results. Launch the run as a detached background job and produce a rich HTML evaluation report. (Sections: *Running an evaluation* and *Building the evaluation report*.)

A request can use both: run the eval, then interpret the results with the advisory evidence base.

## Required Sources

When working inside `/home/likefallwind/code/edubenchmark`, read these first:

- `reports/2026-05-13/ai_edu_unified_benchmark_framework_2026-05-13.md`
- `reports/2026-05-13/ai_edu_benchmark_catalog_2026-05-13.md`
- `data/exhaustive_2026-05-13/dataset_acquisition_report.md`

Use JSONL files in `data/exhaustive_2026-05-13/` when precise filtering is needed:

- `benchmarks.jsonl`
- `metrics.jsonl`
- `results.jsonl`
- `dimension_mapping.jsonl`
- `dataset_acquisition.jsonl`

Do not invent benchmark coverage. If a scenario is weakly covered, say so and propose internal evaluation needs.

## Scenario Mapping

Map the user scenario to one or more of these evaluation scales:

| Scale | Focus |
|---|---|
| S1 | Subject knowledge and answer correctness |
| S2 | Complex reasoning and process correctness |
| S3 | Teaching diagnosis and tutoring strategy |
| S4 | Feedback, grading, and rubric-based evaluation |
| S5 | Personalization, learner modeling, and learning path |
| S6 | Multimodal educational understanding and generation |
| S7 | Education safety, ethics, and role boundaries |
| S8 | Real learning effect and workflow value |

Then map to D01-D24 atomic capabilities from the unified framework. Prefer 3-8 primary capabilities; separate secondary capabilities.

## Output Requirements

Always produce or update an HTML file unless the user explicitly asks for another format. Use a clear filename such as:

```text
reports/edubenchassistant/<scenario-slug>-evaluation.html
```

The HTML must include:

- Scenario interpretation: what the application does, who uses it, input/output, and risk level.
- Primary atomic capabilities: D-codes, names, why they matter.
- Existing benchmark evidence: benchmark names, what they test, native metrics, and whether public model results exist.
- Dataset status: local path or access status from the acquisition manifest.
- Current model readiness: what public benchmark results imply about what current models can likely do, and the limits of that inference.
- Recommended evaluation plan: gate checks, primary ranking checks, diagnostic checks, and internal checks.
- Product recommendations: what can be used directly now, what can be used only with guardrails or teacher review, and what requires product development, new data, or new benchmark design before release.
- Extra attention points: safety, leakage/contamination, rubric reliability, multimodal grounding, teacher oversight, learning-effect gaps.
- Coverage judgment: enough public benchmark coverage, partial coverage, or needs custom benchmark.

Keep the HTML self-contained with inline CSS. Use tables for benchmark mapping and a concise summary section at the top.

## Product Readiness Guidance

Include a product-facing recommendation table with these categories:

| Category | Meaning |
|---|---|
| Ready to use | Existing benchmarks and model results are strong enough for low-risk product use, with normal monitoring. |
| Use with guardrails | Public evidence is useful but incomplete; require constraints such as teacher review, confidence thresholds, refusal rules, audit logs, or limited rollout. |
| Needs development | The product needs new workflow logic, UI controls, human review protocols, retrieval/data integration, calibration, or monitoring before it can be reliable. |
| Needs new benchmark/data | Public coverage is weak; define internal datasets, rubrics, red-team sets, pilots, or learning-effect studies. |

Tie every product recommendation back to benchmark evidence or an explicit evidence gap. Do not say a product capability is ready just because a model performs well on a general knowledge, math, or coding benchmark.

## Benchmark Todo Recording

After producing the report, append benchmark gaps to `benchmark-todo.md` unless the user explicitly says not to modify files. Create the file if it does not exist.

Use this compact format:

```markdown
## <scenario name> - <YYYY-MM-DD>

- Gap: <missing measurement scale or benchmark need>
  Product reason: <why this blocks or limits the application>
  Suggested data/eval: <dataset, rubric, red-team set, pilot, or metric>
  Related capabilities: <D-codes and scales>
  Source report: <reports/edubenchassistant/...html>
```

Only record genuine missing benchmarks or measurement scales. Do not duplicate an existing item unless the new scenario adds a materially different product reason or evaluation design.

## Workflow

1. Parse the scenario. If essential details are missing, make conservative assumptions and state them in the HTML.
2. Read the required sources. Use `rg` first to find relevant benchmark names, D-codes, and scenario terms.
3. Select primary and secondary atomic capabilities.
4. Select benchmarks in tiers:
   - Gate: basic knowledge/correctness/safety requirements.
   - Primary: closest match to the application value.
   - Diagnostic: useful for failure analysis.
   - Internal: required when public benchmark coverage is weak.
5. Check data status in `dataset_acquisition_report.md` or `dataset_acquisition.jsonl`.
6. Infer product readiness from the benchmark evidence, current model results, dataset status, and explicit gaps.
7. Write the HTML report.
8. Append missing benchmark/data needs to `benchmark-todo.md`.
9. Summarize the output path, main coverage judgment, product-readiness judgment, and any new benchmark-todo entries to the user.

## Running an evaluation (framework mode)

The per-benchmark eval harness lives in `scripts/eval/`; the entry point is `scripts/eval_benchmark.py --benchmark <name>`. Run available benchmarks with `python scripts/eval_benchmark.py --benchmark x --limit 1 --dry-run` to list names, or read `scripts/eval/benchmarks/__init__.py`. Pipeline: load items → call model (text [+ images]) → LLM answer extraction → score → write `reports/eval/<benchmark>/<date>/`.

Before launching, confirm with the user: **which benchmark, which model, and the sample size** (`--limit 0` = full set). Vision benchmarks (e.g. mathvista) need a vision model — use `--model MiniMax-M3`, not the text-only `MiniMax-M2.7`. Requires `MINIMAX_API_KEY` in the environment. MathVista also needs images unzipped under `sources/datasets/mathvista/data/` (see CLAUDE.md).

**Default to a detached background run** — full benchmarks take a long time, so the job must survive the terminal closing. Use `nohup` + `&` and record the PID and log path:

```bash
DATE=$(date +%F)
mkdir -p reports/eval/<name>
MINIMAX_API_KEY=$MINIMAX_API_KEY nohup python scripts/eval_benchmark.py \
  --benchmark <name> --limit 0 --model MiniMax-M3 --concurrency 4 \
  > reports/eval/<name>/run_${DATE}.log 2>&1 &
echo $! > reports/eval/<name>/run.pid
```

- The run is **resumable/incremental**: `predictions.jsonl` and `extractions.jsonl` are keyed by `item_id`; rerunning the same command retries only failed/empty/missing items. A dropped connection or a closed terminal never loses completed work.
- Monitor with `tail -n 30 reports/eval/<name>/run_*.log` (do not block on `tail -f`); check liveness with `kill -0 $(cat reports/eval/<name>/run.pid)`. Tell the user the log path and PID so they can check progress themselves.
- Keep concurrency modest (2–4). For a quick smoke test first, use `--limit 30` foreground before committing to the full run.
- When the run finishes, the framework writes `summary.json`, `scored.jsonl`, and a rich `report.html` automatically.

## Building the evaluation report

Each run auto-generates `reports/eval/<benchmark>/<date>/report.html` via `scripts/eval/report.py`. To rebuild/enrich a finished run **without re-calling the API** (e.g. an old run, or to show more wrong examples), use the standalone regenerator:

```bash
python scripts/build_eval_report.py --benchmark <name> \
  --run-dir reports/eval/<name>/<date> --num-samples 2 --num-wrong 8
```

The report is self-contained (inline CSS, base64-inlined images for displayed questions) and includes:

- **KPI header**: overall accuracy, total items, scored count, correct count.
- **基准介绍**: a short intro to the benchmark and its homepage, taken from the adapter's `title`/`homepage`/`description`.
- **题目示例**: one or two real questions rendered with their image(s), choices, and reference answer.
- **作答情况**: status breakdown plus per-bucket accuracy tables with bars (e.g. by question_type / answer_type / task).
- **错题分析**: several incorrect items spread across task types, each showing the question, image, model's extracted vs. gold answer, and the full model reasoning (collapsible).

After generating the HTML, **add a short narrative interpretation** for the user (in chat or appended): which D01–D24 capabilities the accuracy profile speaks to, the failure patterns visible in the wrong examples (not just the number), and any product-readiness or safety implication — reuse the advisory evidence base for this. Never reduce the result to a single accuracy number; report the capability/bucket profile.

When you add a new benchmark adapter, set its `title`, `homepage`, and `description` class attributes so the report's intro section renders — otherwise it falls back to the bare benchmark name.

## Quick Benchmark Hints

| Scenario | Primary capabilities | Benchmarks to consider |
|---|---|---|
| Math solving assistant | D04, D05, D06, D02 | GSM8K, MATH, MATH-500, OlymMATH, OlympiadBench, MathVista, GaokaoBench |
| Math tutor | D12, D13, D05, D06, D21 | MathTutorBench, TutorBench, MathDial, Bridge, K12Vista, PEBBLE |
| Essay or short-answer grading | D10, D11, D12, D21 | ASAP-AES, ASAP-SAS, EssayJudge, SAS-Bench, GaokaoBench subjective tasks |
| Programming education assistant | D08, D09, D12, D13 | CS1QA, QACP, Codecademy, LeetCode Student Submissions, HumanEval, MBPP, APPS |
| Teacher lesson planning | D14, D15, D18, D21 | Pedagogy Benchmark, EduBench, EduEval, OmniEduBench, MOOCCube, LectureBank |
| Personalized learning path | D15, D16, D17, D18 | ASSISTments, EdNet, Junyi, FoundationalAssist, PTADisc, MOOCCube |
| Multimodal homework feedback | D06, D12, D22, D21 | TutorBench, K12Vista, MathVista, ME2, CMMU, ChartQA |
| Classroom analysis | D19, D20, D07, D21 | TalkMoves, NCTE Transcripts, TIMSS Video Study, ARIC, SIGHT |
| Interactive teaching content | D22, D23, D06, D21 | EduVisBench, InteractScience, VisualEDU, MathVista, ME2 |
| Youth safety or companion | D21, D24, D13 | EduGuard-Bench, YouthSafe/YAIR, SproutBench, CASTLE, internal localized safety set |

## Common Mistakes

- Do not treat MMLU, C-EVAL, GSM8K, or HumanEval as proof of teaching ability. They are gate checks.
- Do not average raw benchmark scores across tasks. Report a capability profile.
- Do not ignore dataset access status. Kaggle/manual/pending resources are not equivalent to local reproducible data.
- Do not hide coverage gaps. Public benchmarks are weak for long-term learning gain, teacher adoption, and localized youth safety.
- Do not generate only prose when the user asks for application guidance. The deliverable is an HTML evaluation report.
- Do not stop at an evaluation plan. The user also needs product-side implications: direct-use areas, guarded-use areas, engineering/product work, and new measurement needs.
- Do not forget `benchmark-todo.md`. Future benchmark requirements should be preserved outside the one-off HTML report.
- Do not run a full evaluation in the foreground. Long runs must be detached (`nohup ... &`) with the log path and PID surfaced, so a closed terminal does not kill the job.
- Do not use a text-only model for a multimodal benchmark. MathVista needs `MiniMax-M3`; `MiniMax-M2.7` will fail on image items.
- Do not block the session on `tail -f` to watch a background run. Poll the log with a bounded `tail -n`, and let the user check progress via the path/PID you reported.
- Do not deliver an eval report as just an accuracy number. Include the bucket profile and a narrative reading of the wrong examples.
