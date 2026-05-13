---
name: edubenchassistant
description: Use when a user describes an AI-education application, product idea, classroom scenario, tutoring workflow, grading tool, learning analytics task, or education safety case and needs benchmark, metric, atomic capability, dataset, or evaluation guidance
---

# EduBench Assistant

## Overview

Use the local EduBenchmark evidence base to turn an AI-education application scenario into an evaluation plan. The answer must identify relevant atomic capabilities, prior benchmarks, native metrics, dataset availability, and extra risks, then present the result as an HTML report.

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
- Recommended evaluation plan: gate checks, primary ranking checks, diagnostic checks, and internal checks.
- Extra attention points: safety, leakage/contamination, rubric reliability, multimodal grounding, teacher oversight, learning-effect gaps.
- Coverage judgment: enough public benchmark coverage, partial coverage, or needs custom benchmark.

Keep the HTML self-contained with inline CSS. Use tables for benchmark mapping and a concise summary section at the top.

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
6. Write the HTML report.
7. Summarize the output path and the main coverage judgment to the user.

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
