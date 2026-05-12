# Learnings

## [LRN-20260512-001] correction

**Logged**: 2026-05-12T14:22:04+08:00  
**Priority**: high  
**Status**: pending  
**Area**: evaluation

### Summary
For high-quality education benchmark pilots, "expert review" must mean human expert review; AI-generated expert scores are not valid Go/No-Go evidence.

### Details
The user corrected that if a benchmark requires expert evaluation, relying on AI for that evaluation is not acceptable. Automation can anonymize outputs, validate CSV structure, check completeness, and summarize returned scores, but it must not substitute for human subject-matter or education experts.

### Suggested Action
Make human-only expert review explicit in protocols, handoff materials, decision templates, and status/audit docs. Keep actual benchmark status `NOT_READY` until human R1/R2 scores are returned.

### Metadata
- Source: user_feedback
- Related Files: pilot_evaluation_protocol_v0.1.md, review_templates/expert_review_guide_v0.1.md, pilot_runs/expert_review_handoff.md
- Tags: evaluation, benchmark, human-review

