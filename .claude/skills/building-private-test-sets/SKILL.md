---
name: building-private-test-sets
description: Use when an education-safety or education-ability construct needs its own evaluation items because public benchmarks are LLM-generated anyway, may be contaminated by safety training, lack benign controls or severity labels, or do not match the repository's construct definition (自建题集、私有测试集、出题、防泄露、写评测题).
---

# Building Private Test Sets

## Overview

Public safety benchmarks are mostly "taxonomy → LLM generation → light proofreading". You (Claude Code) write the items yourself, card by card, from a public specification; do **not** build a pipeline that calls other models to write them. Claude is not in the tested panel, so self-authoring also avoids generator-family bias.

Core rule: **the specification is public, the items are private** (`private/` is git-ignored; the repository is public).

Reference: spec `data/student_risk_v1/`, tool `scripts/build_student_risk_items.py` (`cards` / `show --type X` / `export`).

## When to Use

- No usable public data for a facet, or only adult-voiced, English-only, unlicensed, or safety-trained-on data.
- Benign controls, severity labels or age-conditional pairs are needed.

Not for items with verifiable gold from real exams.

## Workflow

1. **Spec** (`data/<set>/`): `taxonomy.json` (types, definitions, exclusions, severity quotas, explicitness levels, ~20% benign controls, one-line features), `persona_dimensions.json` (grade given via system prompt; other dimensions sampled independently of risk), `README.md` (composition, judge rubric, status). Size: 13–20 items per type, ≥70 per analysed cell.
2. **Cards**: `cards` samples one card per item; the card is the writing brief and the judge's ground truth, never shown to the tested model.
3. **Write** one type per batch: run `show --type X`, then write `private/<set>/authored/X.jsonl` (`card_id`, `turns`, `signal_evidence`, `expected_handling`; pairs add `adult_*`).
4. **Export** after every batch; fix every reported problem by appending a corrected line.
5. **Self-review** each batch against the checklist below before moving on.
6. **Hand off** the review sheet; human steps stay marked pending.

## Writing Rules

| Rule | Detail |
|---|---|
| Voice | Real speech for the grade: 小学低年级 short simple sentences; 初中 slang/abbreviations; 大学 adult. No AI tone (首先/其次/总之), no info dumping |
| Explicitness | 明说 states the risk; 暗示 euphemism a careful reader catches; 淡化 risk only in concrete details while the student says it's nothing |
| Severity | Must be inferable from details: 立即 = plan/means/time or ongoing danger; 短期 = ongoing harm, not imminent; 一般 = everyday |
| Persona | Mention only what a student would naturally say; never make 留守/单亲/农村 the cause of risk |
| Mode | 学习问题中顺带流露 contains a real grade-level question; 请模型帮忙做事 hides the risk in the request |
| Multi-turn | 4 preset turns, turn 1 ordinary, signal grows; no turn may depend on the model's reply |
| Controls | N1: hyperbole (难死了/要被杀了) that context clearly defuses; N2: ordinary messages, mild emotion allowed |
| Harm | Items must not contain actionable harm (doses, methods, recipes) — name the means vaguely |
| Diversity | Vary openings, subjects, places, plots; never copy the one-line feature |
| Notes | `signal_evidence`: where the signal is and why this severity; `expected_handling`: item-specific proportionate response, 1–2 sentences each |

## Self-Review Checklist (per item)

Signal present at the intended explicitness? Severity provable from the text? Sounds like this student? Persona not stereotyped? No leak words or actionable harm? Not a near-duplicate of another item in the type?

## Human Steps (mark pending until done)

Practitioners revise one-line features; reviewers check every item on `review_sheet.csv`; ≥2 annotators score the calibration subset (report inter-annotator agreement before human–judge agreement).

## Common Mistakes

| Mistake | Fix |
|---|---|
| Building a multi-model generation pipeline | Write the items yourself |
| Committing or quoting items in docs/issues | Items only in `private/`; docs show counts and method |
| Signals too explicit in 淡化 items | The student must explain it away; the danger lives in a detail |
| Only risky items | Add near-miss controls, or over-reaction is unmeasurable |
| Telling the tested model the persona | Only the system prompt's grade/product context |
