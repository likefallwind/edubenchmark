# Cross-model eval comparison

Per-benchmark, side-by-side. Accuracy is **not** comparable across benchmarks and is never averaged together.

## agieval

| Model | Accuracy | Scored/Total | Extractor |
| --- | --- | --- | --- |
| MiniMax-M3 | 85.6% | 7266/7272 | MiniMax-M2.7 |

## eduguard_adversarial

| Model | Accuracy | Scored/Total | Extractor | asr | attack_success | n_judged |
| --- | --- | --- | --- | --- | --- | --- |
| MiniMax-M3 | 100.0% | 30/30 | MiniMax-M3 | 0.000 | 0 | 30 |

## eduguard_sata

| Model | Accuracy | Scored/Total | Extractor | accuracy_perfect_match | inclusion_rate | n | omission_rate | rfs |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| MiniMax-M3 | 76.0% | 50/50 | MiniMax-M2.7 | 0.760 | 0.180 | 50 | 0.060 | 0.790 |

## mathvista

| Model | Accuracy | Scored/Total | Extractor |
| --- | --- | --- | --- |
| MiniMax-M3 | 84.1% | 993/1000 | MiniMax-M2.7 |

## mmlu_pro

| Model | Accuracy | Scored/Total | Extractor |
| --- | --- | --- | --- |
| doubao-seed-2.0-lite | 100.0% | 5/5 | MiniMax-M2.7 |
| glm-5.1 | 100.0% | 5/5 | MiniMax-M2.7 |
| MiniMax-M3 | 85.6% | 12026/12032 | MiniMax-M2.7 |
| doubao-seed-2.0-pro | 80.0% | 5/5 | MiniMax-M2.7 |

## olympiadbench

| Model | Accuracy | Scored/Total | Extractor |
| --- | --- | --- | --- |
| MiniMax-M3 | 75.7% | 3923/6728 | MiniMax-M2.7 |

