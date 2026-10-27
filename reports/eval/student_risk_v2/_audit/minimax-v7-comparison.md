# MiniMax v7 vs Codex disagreement rerun

Scope: only model-item rows where the previous MiniMax judge differed from the Codex row-by-row review.
Judge: MiniMax-M3; prompt: v7; extraction/judge concurrency: 4.

| model | n | old rec agreement | v7 rec agreement | old intervention agreement | v7 intervention agreement | old joint agreement | v7 joint agreement | joint delta |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| MiniMax-M3.1-Flash-Preview | 176 | 0.2841 | 0.7955 | 0.3239 | 0.5568 | 0.0000 | 0.4773 | +0.4773 |
| deepseek-v4.1-flash | 172 | 0.1860 | 0.7616 | 0.2616 | 0.4651 | 0.0000 | 0.4302 | +0.4302 |
| doubao-seed-2.1-pro | 159 | 0.2075 | 0.7673 | 0.2704 | 0.4591 | 0.0000 | 0.4151 | +0.4151 |
| glm-5.3 | 166 | 0.2530 | 0.8193 | 0.3253 | 0.6084 | 0.0000 | 0.5482 | +0.5482 |
| glm-5.3-flash | 157 | 0.2484 | 0.8471 | 0.2866 | 0.5605 | 0.0000 | 0.5223 | +0.5223 |
| minimax3 | 162 | 0.2654 | 0.7840 | 0.2716 | 0.5062 | 0.0000 | 0.4506 | +0.4506 |

Remaining v7 disagreement rows, with reasons, are in `minimax-v7-comparison.json`; the CSV contains one row per rerun item.
