# Teaching-judge rubric robustness audit

> Offline reanalysis only. No new human labels and no model calls are used by this audit.

## 1. Multiplicity-corrected accepted candidates

| Arm | Line | Round | Candidate | Delta kappa | p | Holm within round | Holm across arm |
|---|---|---:|---|---:|---:|---:|---:|
| glm_full | mrbench/Providing_Guidance | 1 | r1p2 | +0.1159 | 0.0002 | 0.0006 | 0.0038 |
| glm_full | mrbench/Coherence | 1 | r1p3 | +0.0496 | 0.0232 | 0.0696 | 0.3479 |
| glm_full | mrbench/Coherence | 2 | r2p1 | +0.0823 | 0.0002 | 0.0004 | 0.0038 |
| glm_full | bea2025/Providing_Guidance | 1 | r1p1 | +0.0923 | 0.0062 | 0.0186 | 0.1054 |
| glm_nodiag | mrbench/Providing_Guidance | 1 | r1p2 | +0.0827 | 0.0002 | 0.0004 | 0.0012 |
| glm_nodiag | mrbench/Coherence | 1 | r1p6 | +0.0606 | 0.0108 | 0.0324 | 0.0540 |
| m3_self | mrbench/Providing_Guidance | 1 | r1p3 | +0.0938 | 0.0032 | 0.0096 | 0.0576 |
| dsv4_self | mrbench/Providing_Guidance | 2 | r2p2 | +0.0871 | 0.0006 | 0.0018 | 0.0090 |

## 2. Sealed-test multiplicity sensitivity

| Judge | Line | Delta kappa | p | Holm across four | Survives |
|---|---|---:|---:|---:|---:|
| glm-5.2 | mrbench/Providing_Guidance | +0.1147 | 0.0010 | 0.0040 | yes |
| glm-5.2 | mrbench/Coherence | +0.0018 | 0.5029 | 1.0000 | no |
| glm-5.2 | bea2025/Providing_Guidance | -0.0124 | 0.6483 | 1.0000 | no |
| minimax3 | mrbench/Providing_Guidance | +0.0740 | 0.0084 | 0.0252 | yes |

## 3. Conversation-level stability

| Line | Overall delta | Positive repeated folds | Fold p10 to p90 | Leave-one-conversation-out range |
|---|---:|---:|---:|---:|
| mrbench/Providing_Guidance | +0.1159 | 0.977 | +0.0382 to +0.1864 | +0.1068 to +0.1251 |
| mrbench/Coherence | +0.1318 | 0.986 | +0.0579 to +0.2011 | +0.1246 to +0.1417 |
| bea2025/Providing_Guidance | +0.0923 | 0.901 | +0.0014 to +0.1754 | +0.0818 to +0.1017 |

## 4. Factorial-style evidence boundary

The repository contains a broad four-family ablation plus a strict P5 removal. It is not a complete factorial isolation of constrained editing and significance gating; the missing cells are recorded in `summary.json` rather than inferred away.

## 5. Proposal-seed replication

- `full`: 1 runs; acceptance rate 1.0; median accepted effect 0.1159.
- `no_diagnosis`: 1 runs; acceptance rate 1.0; median accepted effect 0.0827.

## Interpretation rule

- Holm-corrected results support family-wise claims.
- BH-corrected results support explicitly labeled exploratory claims.
- Repeated-fold results are stability diagnostics, not new independent test evidence.
- The sealed test remains untouched by selection; its four pre-existing lines are only re-scored offline.
