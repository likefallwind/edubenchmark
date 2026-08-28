# Cross-model eval comparison

Per-benchmark, side-by-side. Accuracy is **not** comparable across benchmarks and is never averaged together.

## _judge_jury

| Model | Accuracy | Scored/Total | Extractor | Judge |
| --- | --- | --- | --- | --- |
| ? | n/a | None/None | — | — |

## agieval

| Model | Accuracy | Scored/Total | Extractor | Judge |
| --- | --- | --- | --- | --- |
| doubao-seed-2.0-pro | 92.0% | 7272/7272 | MiniMax-M2.7 | — |
| glm-5.2 | 90.6% | 7219/7272 | MiniMax-M2.7 | — |
| deepseek-v4-pro | 90.2% | 7272/7272 | MiniMax-M2.7 | — |
| deepseek-v4-flash | 89.4% | 7270/7272 | MiniMax-M2.7 | — |
| Qwen/Qwen3.8-27B | 89.1% | 7268/7272 | MiniMax-M2.7 | — |
| MiniMax-M3 | 85.6% | 7268/7272 | MiniMax-M2.7 | — |
| Qwen/Qwen3.5-4B | 83.0% | 7268/7272 | MiniMax-M2.7 | — |
| MiniMax-M2.7 | 81.1% | 7266/7272 | MiniMax-M2.7 | — |

## asap_2

| Model | Accuracy | Scored/Total | Extractor | Judge | adjacent_agreement | exact_agreement | mean_bias | mean_gold | mean_pred | n | qwk | scorable |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DeepSeek-R1-0528-Qwen3-8B | n/a | 7085/7421 | — | — | — | — | — | — | — | — | 0.478 | — |
| MiniMax-M2.7 | n/a | 7421/7421 | — | — | — | — | — | — | — | — | 0.528 | — |
| Qwen/Qwen3.5-4B | n/a | 7421/7421 | MiniMax-M2.7 | — | 0.883 | 0.388 | 0.277 | 2.920 | 3.197 | 7421 | 0.409 | 7421 |
| Qwen/Qwen3.8-27B | n/a | 7421/7421 | MiniMax-M2.7 | — | 0.945 | 0.476 | -0.120 | 2.920 | 2.800 | 7421 | 0.561 | 7421 |
| claude-sonnet-4-6 | n/a | 7421/7421 | — | — | — | — | — | — | — | — | 0.611 | — |
| deepseek-v4-flash | n/a | 7421/7421 | — | — | — | — | — | — | — | — | 0.508 | — |
| deepseek-v4-pro | n/a | 7421/7421 | — | — | — | — | — | — | — | — | 0.523 | — |
| doubao-seed-2.0-pro | n/a | 7421/7421 | MiniMax-M2.7 | — | 0.930 | 0.463 | -0.412 | 2.920 | 2.508 | 7421 | 0.585 | 7421 |
| glm-5.1 | n/a | 7421/7421 | — | — | — | — | — | — | — | — | 0.573 | — |
| glm-5.2 | n/a | 20/20 | MiniMax-M2.7 | — | 1.000 | 0.550 | -0.250 | 2.500 | 2.250 | 20 | 0.550 | 20 |
| gpt-5.4 | n/a | 7421/7421 | — | — | — | — | — | — | — | — | 0.473 | — |
| kimi-k2.6 | n/a | 7421/7421 | — | — | — | — | — | — | — | — | 0.571 | — |
| MiniMax-M3 | n/a | 7417/7421 | — | — | — | — | — | — | — | — | 0.490 | — |
| qwen3.7-max | n/a | 7421/7421 | — | — | — | — | — | — | — | — | 0.600 | — |

## bea2025_judge

| Model | Accuracy | Scored/Total | Extractor | Judge |
| --- | --- | --- | --- | --- |
| glm-5.2 | 68.8% | 9903/9904 | MiniMax-M2.7 | — |
| deepseek-v4-pro | 66.8% | 9904/9904 | MiniMax-M2.7 | — |
| doubao-seed-2.0-pro | 66.3% | 9904/9904 | MiniMax-M2.7 | — |
| Qwen/Qwen3.5-4B | 65.9% | 9904/9904 | MiniMax-M2.7 | — |
| deepseek-v4-flash | 64.6% | 9904/9904 | MiniMax-M2.7 | — |
| Qwen/Qwen3.8-27B | 60.8% | 9904/9904 | MiniMax-M2.7 | — |
| MiniMax-M2.7 | 60.3% | 9903/9904 | MiniMax-M2.7 | — |
| MiniMax-M3 | 59.3% | 9896/9904 | MiniMax-M2.7 | — |
| deepseek-v3.2 | 43.2% | 9904/9904 | MiniMax-M2.7 | — |

## bea2025_tutor

| Model | Accuracy | Scored/Total | Extractor | Judge |
| --- | --- | --- | --- | --- |
| glm-5.2 | 91.9% | 296/300 | MiniMax-M2.7 | deepseek-v4-flash |
| doubao-seed-2.0-pro | 91.6% | 296/300 | MiniMax-M2.7 | deepseek-v4-flash |
| MiniMax-M3 | 89.1% | 294/300 | MiniMax-M2.7 | deepseek-v4-flash |
| MiniMax-M2.7 | 85.7% | 300/300 | MiniMax-M2.7 | deepseek-v4-flash |
| doubao-seed-2.0-pro | 82.3% | 300/300 | MiniMax-M2.7 | MiniMax-M3 |
| MiniMax-M3 | 82.0% | 300/300 | MiniMax-M3 | MiniMax-M3 |
| glm-5.2 | 81.0% | 300/300 | MiniMax-M3 | MiniMax-M3 |
| Qwen/Qwen3.8-27B | 78.7% | 300/300 | MiniMax-M2.7 | MiniMax-M3 |
| Qwen/Qwen3.5-4B | 73.3% | 300/300 | MiniMax-M2.7 | MiniMax-M3 |
| MiniMax-M2.7 | 71.3% | 300/300 | MiniMax-M3 | MiniMax-M3 |

## ceval

| Model | Accuracy | Scored/Total | Extractor | Judge |
| --- | --- | --- | --- | --- |
| glm-5.1 | 100.0% | 5/5 | MiniMax-M2.7 | — |
| doubao-seed-2.0-pro | 95.5% | 1346/1346 | MiniMax-M2.7 | — |
| deepseek-v4-pro | 93.8% | 1346/1346 | MiniMax-M2.7 | — |
| glm-5.2 | 93.8% | 1345/1346 | MiniMax-M2.7 | — |
| deepseek-v4-flash | 92.2% | 1344/1346 | MiniMax-M2.7 | — |
| Qwen/Qwen3.8-27B | 90.3% | 1345/1346 | MiniMax-M2.7 | — |
| MiniMax-M3 | 88.3% | 1346/1346 | MiniMax-M2.7 | — |
| MiniMax-M2.7 | 87.4% | 1346/1346 | MiniMax-M2.7 | — |
| Qwen/Qwen3.5-4B | 83.6% | 1346/1346 | MiniMax-M2.7 | — |
| Qwen/Qwen3-8B | 82.8% | 1346/1346 | MiniMax-M2.7 | — |

## edubench

| Model | Accuracy | Scored/Total | Extractor | Judge | mean_overall_score | mean_scenario_score |
| --- | --- | --- | --- | --- | --- | --- |
| Qwen/Qwen3.5-4B | n/a | 0/3797 | deepseek-v3.2 | deepseek-v3.2 | — | — |
| claude-sonnet-4-6 | n/a | 3797/3797 | — | deepseek-v3.2 | 8.112 | 8.814 |
| deepseek-v4-flash | n/a | 3797/3797 | — | deepseek-v3.2 | 8.154 | 8.781 |
| deepseek-v4-pro | n/a | 3797/3797 | — | deepseek-v3.2 | 8.013 | 8.076 |
| doubao-seed-2.0-lite | n/a | 3797/3797 | — | deepseek-v3.2 | 8.037 | 8.661 |
| doubao-seed-2.0-pro | n/a | 3797/3797 | — | deepseek-v3.2 | 8.228 | 8.962 |
| glm-5.1 | n/a | 3797/3797 | — | deepseek-v3.2 | 7.681 | 7.675 |
| glm-5.2 | n/a | 3795/3797 | deepseek-v3.2 | deepseek-v3.2 | 8.480 | 9.099 |
| kimi-k2.6 | n/a | 3797/3797 | — | deepseek-v3.2 | 7.901 | 8.458 |
| minimax-m2.7 | n/a | 3797/3797 | — | deepseek-v3.2 | 8.342 | 8.357 |
| minimax-m3 | n/a | 3797/3797 | — | deepseek-v3.2 | 8.069 | 8.807 |
| qwen3-14b | n/a | 3797/3797 | — | deepseek-v3.2 | 7.470 | 7.501 |
| qwen3.5-122b-a10b | n/a | 3797/3797 | — | deepseek-v3.2 | 8.249 | 8.306 |
| deepseek-v4-pro | n/a | 3722/3797 | MiniMax-M2.7 | deepseek-v4-flash | 8.487 | 8.814 |
| doubao-seed-2.0-pro | n/a | 3717/3797 | MiniMax-M2.7 | deepseek-v4-flash | 8.676 | 9.038 |
| glm-5.2 | n/a | 3797/3797 | MiniMax-M2.7 | deepseek-v4-flash | 8.577 | 8.863 |
| minimax-m2.7 | n/a | 3797/3797 | MiniMax-M2.7 | deepseek-v4-flash | 8.570 | 8.807 |
| minimax-m3 | n/a | 3796/3797 | MiniMax-M2.7 | deepseek-v4-flash | 8.719 | 9.021 |
| Qwen/Qwen3.5-4B | n/a | 3795/3797 | MiniMax-M3 | MiniMax-M3 | 7.262 | 7.373 |
| Qwen/Qwen3.8-27B | n/a | 3794/3797 | MiniMax-M3 | MiniMax-M3 | 7.732 | 7.840 |
| glm-5.2 | n/a | 5/5 | MiniMax-M3 | MiniMax-M3 | 8.067 | 8.600 |

## eduequity

| Model | Accuracy | Scored/Total | Extractor | Judge | both_invalid_rate | dim_development_opportunity_parity | dim_instructional_standard_parity | dim_respect_and_non_stereotyping | dim_support_quality_parity | eduequity_score | hard_fail_rate | judge_error_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| MiniMax-M2.7 | n/a | 400/400 | — | MiniMax-M3 | 0.000 | 6.950 | 7.325 | 8.045 | 7.048 | 7.101 | 0.055 | 0.000 |
| deepseek-v4-pro | n/a | 400/400 | — | MiniMax-M3 | 0.000 | 7.490 | 7.810 | 8.357 | 7.580 | 7.643 | 0.037 | 0.000 |
| doubao-seed-2.0-lite | n/a | 397/400 | — | MiniMax-M3 | 0.000 | 7.489 | 7.806 | 8.224 | 7.788 | 7.651 | 0.040 | 0.007 |
| doubao-seed-2.1-turbo | n/a | 399/400 | — | MiniMax-M3 | 0.000 | 7.266 | 7.624 | 7.724 | 7.576 | 7.351 | 0.043 | 0.003 |
| glm-5.2 | n/a | 400/400 | — | MiniMax-M3 | 0.000 | 7.072 | 7.555 | 7.765 | 7.412 | 7.204 | 0.055 | 0.000 |
| MiniMax-M3 | n/a | 400/400 | — | MiniMax-M3 | 0.000 | 6.933 | 7.370 | 7.705 | 7.340 | 7.111 | 0.052 | 0.000 |

## eduguard_adversarial

| Model | Accuracy | Scored/Total | Extractor | Judge | asr | attack_success | n_judged |
| --- | --- | --- | --- | --- | --- | --- | --- |
| gpt-5.5 | 99.6% | 797/801 | MiniMax-M2.7 | deepseek-v3.2 | 0.004 | 3 | 797 |
| MiniMax-M2.7 | 97.1% | 794/801 | MiniMax-M2.7 | deepseek-v4-flash | 0.029 | 23 | 794 |
| MiniMax-M3 | 96.5% | 801/801 | MiniMax-M2.7 | MiniMax-M3 | 0.035 | 28 | 801 |
| gpt-5.5 | 95.1% | 797/801 | MiniMax-M3 | MiniMax-M3 | 0.049 | 39 | 797 |
| MiniMax-M3 | 95.1% | 793/801 | MiniMax-M2.7 | deepseek-v4-flash | 0.049 | 39 | 793 |
| glm-5.1 | 95.1% | 772/801 | MiniMax-M2.7 | deepseek-v3.2 | 0.049 | 38 | 772 |
| MiniMax-M2.7 | 94.3% | 801/801 | MiniMax-M2.7 | MiniMax-M3 | 0.027 | 21 | 776 |
| MiniMax-M3 | 91.8% | 801/801 | MiniMax-M2.7 | deepseek-v3.2 | 0.082 | 66 | 801 |
| glm-5.1 | 90.0% | 772/801 | MiniMax-M2.7 | MiniMax-M3 | 0.095 | 73 | 768 |
| Qwen/Qwen3.5-4B | 89.6% | 800/801 | MiniMax-M2.7 | MiniMax-M3 | 0.104 | 83 | 800 |
| Qwen/Qwen3.8-27B | 85.0% | 801/801 | MiniMax-M2.7 | MiniMax-M3 | 0.150 | 120 | 801 |
| kimi-k2.6 | 83.6% | 801/801 | MiniMax-M2.7 | MiniMax-M3 | 0.143 | 112 | 782 |
| glm-5.2 | 79.6% | 798/801 | MiniMax-M2.7 | deepseek-v4-flash | 0.204 | 163 | 798 |
| glm-5.2 | 79.2% | 801/801 | MiniMax-M2.7 | MiniMax-M3 | 0.207 | 166 | 800 |
| glm-5.2 | 71.5% | 801/801 | MiniMax-M2.7 | deepseek-v3.2 | 0.285 | 228 | 801 |
| doubao-seed-2.0-lite | 54.6% | 801/801 | MiniMax-M2.7 | MiniMax-M3 | 0.452 | 361 | 798 |
| doubao-seed-2.0-pro | 52.3% | 801/801 | MiniMax-M2.7 | deepseek-v4-flash | 0.477 | 382 | 801 |
| doubao-seed-2.0-lite | 48.8% | 801/801 | MiniMax-M2.7 | deepseek-v3.2 | 0.511 | 409 | 800 |
| doubao-seed-2.0-pro | 48.6% | 801/801 | MiniMax-M2.7 | MiniMax-M3 | 0.511 | 407 | 796 |
| deepseek-v4-pro | 42.8% | 801/801 | MiniMax-M2.7 | MiniMax-M3 | 0.571 | 456 | 799 |
| deepseek-v4-pro | 41.8% | 801/801 | MiniMax-M2.7 | deepseek-v4-flash | 0.582 | 466 | 801 |
| doubao-seed-2.0-pro | 39.7% | 801/801 | MiniMax-M2.7 | deepseek-v3.2 | 0.603 | 482 | 800 |
| deepseek-v4-pro | 37.5% | 801/801 | MiniMax-M2.7 | deepseek-v3.2 | 0.624 | 498 | 798 |

## eduguard_sata

| Model | Accuracy | Scored/Total | Extractor | Judge | accuracy_perfect_match | inclusion_rate | n | omission_rate | rfs |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| MiniMax-M3 | 72.5% | 5270/5270 | MiniMax-M2.7 | — | 0.725 | 0.184 | 5270 | 0.091 | 0.769 |
| deepseek-v4-pro | 70.4% | 5266/5270 | MiniMax-M2.7 | — | 0.704 | 0.181 | 5266 | 0.115 | 0.761 |
| doubao-seed-2.0-pro | 70.1% | 5270/5270 | MiniMax-M2.7 | — | 0.701 | 0.175 | 5270 | 0.125 | 0.762 |
| Qwen/Qwen3.8-27B | 69.3% | 5267/5270 | MiniMax-M2.7 | — | 0.693 | 0.186 | 5267 | 0.121 | 0.753 |
| doubao-seed-2.0-lite | 69.2% | 5270/5270 | MiniMax-M2.7 | — | 0.692 | 0.230 | 5270 | 0.077 | 0.730 |
| gpt-5.5 | 68.9% | 2148/2635 | MiniMax-M2.7 | — | 0.690 | 0.210 | 2148 | 0.101 | 0.740 |
| Qwen/Qwen3.5-4B | 67.9% | 5270/5270 | MiniMax-M2.7 | — | 0.679 | 0.163 | 5270 | 0.158 | 0.757 |
| glm-5.1 | 66.0% | 5268/5270 | MiniMax-M2.7 | — | 0.660 | 0.132 | 5268 | 0.208 | 0.763 |
| MiniMax-M2.7 | 65.6% | 5269/5270 | MiniMax-M2.7 | — | 0.656 | 0.268 | 5269 | 0.076 | 0.693 |
| glm-5.2 | 65.4% | 5270/5270 | MiniMax-M2.7 | — | 0.653 | 0.134 | 5270 | 0.213 | 0.759 |
| deepseek-v4-flash | 50.0% | 4/4 | MiniMax-M2.7 | — | 0.500 | 0.250 | 4 | 0.250 | 0.625 |

## eduillustrate

| Model | Accuracy | Scored/Total | Extractor | Judge |
| --- | --- | --- | --- | --- |
| MiniMax-M3 | n/a | None/5 | — | MiniMax-M3 |

## ifeval

| Model | Accuracy | Scored/Total | Extractor | Judge |
| --- | --- | --- | --- | --- |
| Qwen/Qwen3.8-27B | 94.5% | 541/541 | MiniMax-M2.7 | — |
| glm-5.2 | 93.0% | 541/541 | MiniMax-M2.7 | — |
| deepseek-v4-pro | 92.2% | 540/541 | MiniMax-M2.7 | — |
| Qwen/Qwen3.5-4B | 91.1% | 541/541 | MiniMax-M2.7 | — |
| MiniMax-M2.7 | 91.1% | 538/541 | MiniMax-M2.7 | — |
| doubao-seed-2.0-pro | 89.5% | 541/541 | MiniMax-M2.7 | — |
| MiniMax-M3 | 87.4% | 540/541 | MiniMax-M2.7 | — |

## k12bench

| Model | Accuracy | Scored/Total | Extractor | Judge | exact_match | macro_f1 | n | precision | recall |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Qwen/Qwen3.8-27B | 57.3% | 23640/23640 | MiniMax-M2.7 | — | 0.573 | 0.757 | 23640 | 0.727 | 0.848 |
| doubao-seed-2.0-pro | 57.2% | 23640/23640 | MiniMax-M2.7 | — | 0.572 | 0.760 | 23640 | 0.729 | 0.851 |
| Qwen/Qwen3.5-4B | 52.5% | 23640/23640 | MiniMax-M2.7 | — | 0.525 | 0.717 | 23640 | 0.685 | 0.816 |
| MiniMax-M3 | 50.0% | 23639/23640 | MiniMax-M2.7 | — | 0.500 | 0.712 | 23639 | 0.671 | 0.830 |

## k12vista

| Model | Accuracy | Scored/Total | Extractor | Judge |
| --- | --- | --- | --- | --- |
| doubao-seed-2.0-pro | 55.5% | 600/600 | MiniMax-M2.7 | MiniMax-M2.7 |
| Qwen/Qwen3.8-27B | 54.2% | 600/600 | MiniMax-M2.7 | MiniMax-M3 |
| MiniMax-M3 | 46.5% | 598/600 | MiniMax-M2.7 | MiniMax-M3 |
| Qwen/Qwen3.5-4B | 39.3% | 600/600 | MiniMax-M2.7 | MiniMax-M3 |

## longtutor_diagnosis

| Model | Accuracy | Scored/Total | Extractor | Judge |
| --- | --- | --- | --- | --- |
| Qwen/Qwen3.8-27B | 46.1% | 1000/1001 | MiniMax-M3 | — |
| deepseek-v4-pro | 43.7% | 1001/1001 | MiniMax-M3 | — |
| MiniMax-M3 | 41.6% | 1001/1001 | MiniMax-M3 | — |
| doubao-seed-2.0-pro | 37.7% | 1001/1001 | MiniMax-M3 | — |
| glm-5.2 | 35.0% | 1001/1001 | MiniMax-M3 | — |
| Qwen/Qwen3.5-4B | 29.3% | 1001/1001 | MiniMax-M3 | — |
| MiniMax-M2.7 | 27.9% | 1001/1001 | MiniMax-M3 | — |

## longtutor_evidence

| Model | Accuracy | Scored/Total | Extractor | Judge |
| --- | --- | --- | --- | --- |
| glm-5.2 | 80.7% | 3003/3003 | MiniMax-M3 | MiniMax-M3 |
| Qwen/Qwen3.8-27B | 80.3% | 3001/3003 | MiniMax-M3 | MiniMax-M3 |
| doubao-seed-2.0-pro | 80.1% | 3003/3003 | MiniMax-M3 | MiniMax-M3 |
| Qwen/Qwen3.5-4B | 79.3% | 3003/3003 | MiniMax-M3 | MiniMax-M3 |
| deepseek-v4-pro | 79.2% | 3003/3003 | MiniMax-M3 | MiniMax-M3 |
| MiniMax-M3 | 78.7% | 3003/3003 | MiniMax-M3 | MiniMax-M3 |
| MiniMax-M2.7 | 71.2% | 3002/3003 | MiniMax-M3 | MiniMax-M3 |

## longtutor_teaching

| Model | Accuracy | Scored/Total | Extractor | Judge |
| --- | --- | --- | --- | --- |
| MiniMax-M2.7 | 100.0% | 1001/1001 | MiniMax-M3 | MiniMax-M3 |
| Qwen/Qwen3.8-27B | 100.0% | 1001/1001 | MiniMax-M3 | MiniMax-M3 |
| deepseek-v4-pro | 100.0% | 1001/1001 | MiniMax-M3 | MiniMax-M3 |
| glm-5.2 | 100.0% | 1001/1001 | MiniMax-M3 | MiniMax-M3 |
| doubao-seed-2.0-pro | 99.9% | 1001/1001 | MiniMax-M3 | MiniMax-M3 |
| MiniMax-M3 | 99.9% | 1001/1001 | MiniMax-M3 | MiniMax-M3 |
| Qwen/Qwen3.5-4B | 99.4% | 1001/1001 | MiniMax-M3 | MiniMax-M3 |

## mathtutorbench_judge_calibration

| Model | Accuracy | Scored/Total | Extractor | Judge |
| --- | --- | --- | --- | --- |
| MiniMax-M3 | 84.4% | 964/964 | MiniMax-M2.7 | — |
| glm-5.2 | 83.9% | 964/964 | MiniMax-M2.7 | — |
| Qwen/Qwen3.8-27B | 83.8% | 964/964 | MiniMax-M2.7 | — |
| deepseek-v3.2 | 83.6% | 964/964 | MiniMax-M2.7 | — |
| doubao-seed-2.0-pro | 82.7% | 964/964 | MiniMax-M2.7 | — |
| deepseek-v4-flash | 82.6% | 964/964 | MiniMax-M2.7 | — |
| Qwen/Qwen3.5-4B | 81.7% | 964/964 | MiniMax-M2.7 | — |
| deepseek-v4-pro | 81.7% | 964/964 | MiniMax-M2.7 | — |
| MiniMax-M2.7 | 81.0% | 964/964 | MiniMax-M2.7 | — |

## mathtutorbench_mistake_correction

| Model | Accuracy | Scored/Total | Extractor | Judge |
| --- | --- | --- | --- | --- |
| doubao-seed-2.0-pro | 94.2% | 1002/1002 | MiniMax-M2.7 | — |
| glm-5.2 | 93.7% | 1001/1002 | MiniMax-M2.7 | — |
| Qwen/Qwen3.8-27B | 93.3% | 1002/1002 | MiniMax-M2.7 | — |
| deepseek-v4-pro | 92.0% | 1002/1002 | MiniMax-M2.7 | — |
| deepseek-v4-flash | 91.7% | 1002/1002 | MiniMax-M2.7 | — |
| Qwen/Qwen3.5-4B | 88.0% | 1002/1002 | MiniMax-M2.7 | — |
| MiniMax-M3 | 87.3% | 1002/1002 | MiniMax-M2.7 | — |
| MiniMax-M2.7 | 86.0% | 1002/1002 | MiniMax-M2.7 | — |

## mathtutorbench_mistake_location

| Model | Accuracy | Scored/Total | Extractor | Judge |
| --- | --- | --- | --- | --- |
| glm-5.2 | 79.2% | 2004/2004 | MiniMax-M2.7 | — |
| Qwen/Qwen3.8-27B | 78.7% | 2004/2004 | MiniMax-M2.7 | — |
| MiniMax-M3 | 77.5% | 2004/2004 | MiniMax-M2.7 | — |
| deepseek-v4-flash | 77.4% | 2004/2004 | MiniMax-M2.7 | — |
| MiniMax-M2.7 | 76.7% | 2004/2004 | MiniMax-M2.7 | — |
| deepseek-v4-pro | 76.5% | 2004/2004 | MiniMax-M2.7 | — |
| doubao-seed-2.0-pro | 76.3% | 2004/2004 | MiniMax-M2.7 | — |
| Qwen/Qwen3.5-4B | 74.5% | 2004/2004 | MiniMax-M2.7 | — |

## mathtutorbench_pedagogy

| Model | Accuracy | Scored/Total | Extractor | Judge |
| --- | --- | --- | --- | --- |
| doubao-seed-2.0-pro | 86.6% | 1150/1150 | MiniMax-M2.7 | deepseek-v4-flash |
| glm-5.2 | 85.3% | 1150/1150 | MiniMax-M2.7 | deepseek-v4-flash |
| deepseek-v4-pro | 83.0% | 1150/1150 | MiniMax-M2.7 | deepseek-v4-flash |
| doubao-seed-2.0-pro | 82.5% | 1150/1150 | MiniMax-M2.7 | MiniMax-M3 |
| MiniMax-M3 | 81.4% | 1150/1150 | MiniMax-M2.7 | deepseek-v4-flash |
| glm-5.2 | 81.4% | 1150/1150 | MiniMax-M2.7 | MiniMax-M3 |
| deepseek-v4-pro | 79.8% | 1150/1150 | MiniMax-M2.7 | MiniMax-M3 |
| MiniMax-M3 | 79.3% | 1150/1150 | MiniMax-M2.7 | MiniMax-M3 |
| Qwen/Qwen3.8-27B | 78.3% | 1150/1150 | MiniMax-M2.7 | MiniMax-M3 |
| doubao-seed-2.0-lite | 75.2% | 1150/1150 | MiniMax-M2.7 | MiniMax-M3 |
| MiniMax-M2.7 | 73.6% | 1150/1150 | MiniMax-M2.7 | deepseek-v4-flash |
| deepseek-v4-flash | 71.0% | 1150/1150 | MiniMax-M2.7 | MiniMax-M3 |
| MiniMax-M2.7 | 69.0% | 1150/1150 | MiniMax-M2.7 | MiniMax-M3 |
| Qwen/Qwen3.5-4B | 64.9% | 1150/1150 | MiniMax-M2.7 | MiniMax-M3 |

## mathtutorbench_pedagogy_hard

| Model | Accuracy | Scored/Total | Extractor | Judge |
| --- | --- | --- | --- | --- |
| doubao-seed-2.0-pro | 83.2% | 327/327 | MiniMax-M2.7 | deepseek-v4-flash |
| doubao-seed-2.0-pro | 82.3% | 327/327 | MiniMax-M2.7 | MiniMax-M3 |
| deepseek-v4-pro | 81.0% | 327/327 | MiniMax-M2.7 | deepseek-v4-flash |
| deepseek-v4-pro | 81.0% | 327/327 | MiniMax-M2.7 | MiniMax-M3 |
| glm-5.2 | 80.7% | 327/327 | MiniMax-M2.7 | deepseek-v4-flash |
| glm-5.2 | 77.7% | 327/327 | MiniMax-M2.7 | MiniMax-M3 |
| MiniMax-M3 | 74.6% | 327/327 | MiniMax-M2.7 | deepseek-v4-flash |
| MiniMax-M3 | 73.4% | 327/327 | MiniMax-M2.7 | MiniMax-M3 |
| Qwen/Qwen3.8-27B | 73.1% | 327/327 | MiniMax-M2.7 | MiniMax-M3 |
| doubao-seed-2.0-lite | 67.3% | 327/327 | MiniMax-M2.7 | MiniMax-M3 |
| deepseek-v4-flash | 63.3% | 327/327 | MiniMax-M2.7 | MiniMax-M3 |
| MiniMax-M2.7 | 61.5% | 327/327 | MiniMax-M2.7 | deepseek-v4-flash |
| MiniMax-M2.7 | 59.0% | 327/327 | MiniMax-M2.7 | MiniMax-M3 |
| Qwen/Qwen3.5-4B | 52.9% | 327/327 | MiniMax-M2.7 | MiniMax-M3 |

## mathtutorbench_problem_solving

| Model | Accuracy | Scored/Total | Extractor | Judge |
| --- | --- | --- | --- | --- |
| glm-5.2 | 98.0% | 1319/1319 | MiniMax-M2.7 | — |
| deepseek-v4-flash | 97.4% | 1319/1319 | MiniMax-M2.7 | — |
| Qwen/Qwen3.8-27B | 97.3% | 1319/1319 | MiniMax-M2.7 | — |
| MiniMax-M3 | 97.3% | 1319/1319 | MiniMax-M2.7 | — |
| doubao-seed-2.0-pro | 97.2% | 1319/1319 | MiniMax-M2.7 | — |
| Qwen/Qwen3.5-4B | 95.6% | 1319/1319 | MiniMax-M2.7 | — |
| MiniMax-M2.7 | 95.5% | 1319/1319 | MiniMax-M2.7 | — |

## mathtutorbench_scaffolding

| Model | Accuracy | Scored/Total | Extractor | Judge |
| --- | --- | --- | --- | --- |
| glm-5.2 | 54.9% | 1150/1150 | MiniMax-M2.7 | deepseek-v4-flash |
| glm-5.2 | 53.1% | 1150/1150 | MiniMax-M2.7 | MiniMax-M3 |
| deepseek-v4-pro | 46.9% | 1150/1150 | MiniMax-M2.7 | deepseek-v4-flash |
| deepseek-v4-pro | 43.4% | 1150/1150 | MiniMax-M2.7 | MiniMax-M3 |
| doubao-seed-2.0-pro | 29.1% | 1150/1150 | MiniMax-M2.7 | MiniMax-M3 |
| doubao-seed-2.0-pro | 28.8% | 1150/1150 | MiniMax-M2.7 | deepseek-v4-flash |
| MiniMax-M3 | 23.0% | 1150/1150 | MiniMax-M2.7 | deepseek-v4-flash |
| MiniMax-M3 | 23.0% | 1150/1150 | MiniMax-M2.7 | MiniMax-M3 |
| doubao-seed-2.0-lite | 20.3% | 1150/1150 | MiniMax-M2.7 | MiniMax-M3 |
| Qwen/Qwen3.8-27B | 19.4% | 1150/1150 | MiniMax-M2.7 | MiniMax-M3 |
| Qwen/Qwen3.5-4B | 17.5% | 1150/1150 | MiniMax-M2.7 | MiniMax-M3 |
| MiniMax-M2.7 | 12.0% | 1150/1150 | MiniMax-M2.7 | MiniMax-M3 |
| MiniMax-M2.7 | 11.3% | 1150/1150 | MiniMax-M2.7 | deepseek-v4-flash |
| deepseek-v4-flash | 2.5% | 1150/1150 | MiniMax-M2.7 | MiniMax-M3 |

## mathtutorbench_scaffolding_hard

| Model | Accuracy | Scored/Total | Extractor | Judge |
| --- | --- | --- | --- | --- |
| glm-5.2 | 50.8% | 327/327 | MiniMax-M2.7 | deepseek-v4-flash |
| glm-5.2 | 48.6% | 327/327 | MiniMax-M2.7 | MiniMax-M3 |
| deepseek-v4-pro | 37.3% | 327/327 | MiniMax-M2.7 | deepseek-v4-flash |
| deepseek-v4-pro | 35.8% | 327/327 | MiniMax-M2.7 | MiniMax-M3 |
| doubao-seed-2.0-pro | 31.5% | 327/327 | MiniMax-M2.7 | deepseek-v4-flash |
| doubao-seed-2.0-pro | 27.8% | 327/327 | MiniMax-M2.7 | MiniMax-M3 |
| Qwen/Qwen3.8-27B | 20.2% | 327/327 | MiniMax-M2.7 | MiniMax-M3 |
| MiniMax-M3 | 19.0% | 327/327 | MiniMax-M2.7 | MiniMax-M3 |
| MiniMax-M3 | 17.1% | 327/327 | MiniMax-M2.7 | deepseek-v4-flash |
| doubao-seed-2.0-lite | 15.0% | 327/327 | MiniMax-M2.7 | MiniMax-M3 |
| Qwen/Qwen3.5-4B | 14.4% | 327/327 | MiniMax-M2.7 | MiniMax-M3 |
| deepseek-v4-flash | 12.8% | 327/327 | MiniMax-M2.7 | MiniMax-M3 |
| MiniMax-M2.7 | 10.1% | 327/327 | MiniMax-M2.7 | MiniMax-M3 |
| MiniMax-M2.7 | 9.8% | 327/327 | MiniMax-M2.7 | deepseek-v4-flash |

## mathtutorbench_socratic

| Model | Accuracy | Scored/Total | Extractor | Judge |
| --- | --- | --- | --- | --- |
| Qwen/Qwen3.8-27B | 15.9% | 1319/1319 | MiniMax-M2.7 | — |
| MiniMax-M3 | 13.5% | 1319/1319 | MiniMax-M2.7 | — |
| doubao-seed-2.0-pro | 12.8% | 1319/1319 | MiniMax-M2.7 | — |
| deepseek-v4-pro | 12.0% | 1319/1319 | MiniMax-M2.7 | — |
| glm-5.2 | 11.6% | 1319/1319 | MiniMax-M2.7 | — |
| Qwen/Qwen3.5-4B | 8.0% | 1319/1319 | MiniMax-M2.7 | — |
| MiniMax-M2.7 | 4.5% | 1319/1319 | MiniMax-M2.7 | — |

## mathtutorbench_solution_correctness

| Model | Accuracy | Scored/Total | Extractor | Judge |
| --- | --- | --- | --- | --- |
| glm-5.2 | 89.9% | 2004/2004 | MiniMax-M2.7 | — |
| Qwen/Qwen3.8-27B | 88.8% | 2004/2004 | MiniMax-M2.7 | — |
| Qwen/Qwen3.5-4B | 88.5% | 2004/2004 | MiniMax-M2.7 | — |
| doubao-seed-2.0-pro | 88.5% | 2004/2004 | MiniMax-M2.7 | — |
| MiniMax-M3 | 87.7% | 2004/2004 | MiniMax-M2.7 | — |
| MiniMax-M2.7 | 86.6% | 2004/2004 | MiniMax-M2.7 | — |
| deepseek-v4-pro | 86.4% | 2004/2004 | MiniMax-M2.7 | — |
| deepseek-v4-flash | 85.9% | 2004/2004 | MiniMax-M2.7 | — |

## mathvista

| Model | Accuracy | Scored/Total | Extractor | Judge |
| --- | --- | --- | --- | --- |
| doubao-seed-2.0-pro | 88.7% | 1000/1000 | MiniMax-M2.7 | — |
| Qwen/Qwen3.8-27B | 86.1% | 1000/1000 | MiniMax-M2.7 | — |
| MiniMax-M3 | 84.1% | 993/1000 | MiniMax-M2.7 | — |
| Qwen/Qwen3.5-4B | 83.4% | 1000/1000 | MiniMax-M2.7 | — |

## mmlu_pro

| Model | Accuracy | Scored/Total | Extractor | Judge |
| --- | --- | --- | --- | --- |
| doubao-seed-2.0-lite | 100.0% | 5/5 | MiniMax-M2.7 | — |
| glm-5.1 | 100.0% | 5/5 | MiniMax-M2.7 | — |
| gpt-5.5 | 100.0% | 1/1 | gpt-5.5 | — |
| glm-5.2 | 88.3% | 11875/12032 | MiniMax-M2.7 | — |
| deepseek-v4-pro | 87.4% | 12024/12032 | MiniMax-M2.7 | — |
| doubao-seed-2.0-pro | 86.7% | 12032/12032 | MiniMax-M2.7 | — |
| Qwen/Qwen3.8-27B | 86.3% | 11712/12032 | MiniMax-M2.7 | — |
| deepseek-v4-flash | 85.9% | 12021/12032 | MiniMax-M2.7 | — |
| MiniMax-M3 | 85.6% | 12032/12032 | MiniMax-M2.7 | — |
| MiniMax-M2.7 | 82.7% | 12022/12032 | MiniMax-M2.7 | — |
| Qwen/Qwen3.5-4B | 79.1% | 12031/12032 | MiniMax-M2.7 | — |
| Qwen/Qwen3-8B | 76.7% | 30/30 | MiniMax-M2.7 | — |

## mmtutorbench

| Model | Accuracy | Scored/Total | Extractor | Judge |
| --- | --- | --- | --- | --- |
| doubao-seed-2.0-pro | 52.9% | 770/770 | MiniMax-M2.7 | deepseek-v4-flash |
| doubao-seed-2.0-pro | 36.6% | 770/770 | MiniMax-M2.7 | MiniMax-M3 |
| Qwen/Qwen3.5-4B | 13.1% | 770/770 | MiniMax-M2.7 | MiniMax-M3 |
| MiniMax-M3 | 9.5% | 769/770 | MiniMax-M2.7 | deepseek-v4-flash |
| Qwen/Qwen3.8-27B | 8.3% | 770/770 | MiniMax-M2.7 | MiniMax-M3 |
| MiniMax-M3 | 3.4% | 769/770 | MiniMax-M2.7 | MiniMax-M3 |

## mmtutorbench_judge_calibration

| Model | Accuracy | Scored/Total | Extractor | Judge |
| --- | --- | --- | --- | --- |
| MiniMax-M3 | n/a | 0/0 | MiniMax-M2.7 | — |

## mooccube_prereq

| Model | Accuracy | Scored/Total | Extractor | Judge |
| --- | --- | --- | --- | --- |
| MiniMax-M2.7 | 60.0% | 300/300 | MiniMax-M2.7 | — |
| Qwen/Qwen3.8-27B | 58.0% | 300/300 | MiniMax-M2.7 | — |
| doubao-seed-2.0-pro | 58.0% | 300/300 | MiniMax-M2.7 | — |
| MiniMax-M3 | 57.7% | 300/300 | MiniMax-M2.7 | — |
| glm-5.2 | 53.3% | 300/300 | MiniMax-M2.7 | — |
| deepseek-v4-pro | 52.7% | 300/300 | MiniMax-M2.7 | — |
| Qwen/Qwen3.5-4B | 26.3% | 300/300 | MiniMax-M2.7 | — |

## mrbench_judge

| Model | Accuracy | Scored/Total | Extractor | Judge |
| --- | --- | --- | --- | --- |
| deepseek-v4-pro | 71.9% | 13240/13240 | MiniMax-M2.7 | — |
| glm-5.2 | 70.9% | 13240/13240 | MiniMax-M2.7 | — |
| doubao-seed-2.0-pro | 70.7% | 13240/13240 | MiniMax-M2.7 | — |
| deepseek-v4-flash | 70.1% | 13240/13240 | MiniMax-M2.7 | — |
| MiniMax-M2.7 | 70.1% | 13240/13240 | MiniMax-M2.7 | — |
| Qwen/Qwen3.5-4B | 67.9% | 13240/13240 | MiniMax-M2.7 | — |
| Qwen/Qwen3.8-27B | 67.6% | 13240/13240 | MiniMax-M2.7 | — |
| MiniMax-M3 | 65.3% | 13238/13240 | MiniMax-M2.7 | — |
| deepseek-v3.2 | 51.5% | 13240/13240 | deepseek-v3.2 | — |

## mrbench_tutor

| Model | Accuracy | Scored/Total | Extractor | Judge |
| --- | --- | --- | --- | --- |
| glm-5.2 | 92.9% | 184/200 | MiniMax-M2.7 | deepseek-v4-flash |
| MiniMax-M3 | 90.5% | 199/200 | MiniMax-M2.7 | deepseek-v4-flash |
| doubao-seed-2.0-pro | 89.8% | 186/200 | MiniMax-M2.7 | deepseek-v4-flash |
| MiniMax-M2.7 | 84.8% | 184/200 | MiniMax-M2.7 | deepseek-v4-flash |
| MiniMax-M3 | 83.0% | 200/200 | MiniMax-M2.7 | MiniMax-M3 |
| Qwen/Qwen3.8-27B | 79.5% | 200/200 | MiniMax-M2.7 | MiniMax-M3 |
| glm-5.2 | 79.5% | 200/200 | MiniMax-M2.7 | MiniMax-M3 |
| Qwen/Qwen3.5-4B | 74.5% | 200/200 | MiniMax-M2.7 | MiniMax-M3 |
| doubao-seed-2.0-pro | 73.4% | 177/200 | MiniMax-M2.7 | MiniMax-M3 |
| MiniMax-M2.7 | 68.0% | 200/200 | MiniMax-M2.7 | MiniMax-M3 |

## olympiadbench

| Model | Accuracy | Scored/Total | Extractor | Judge |
| --- | --- | --- | --- | --- |
| glm-5.2 | 84.1% | 2673/6728 | MiniMax-M2.7 | — |
| Qwen/Qwen3.8-27B | 78.1% | 6449/6728 | MiniMax-M2.7 | — |
| doubao-seed-2.0-pro | 76.6% | 6728/6728 | MiniMax-M2.7 | — |
| deepseek-v4-pro | 73.6% | 6685/6728 | MiniMax-M2.7 | — |
| Qwen/Qwen3.5-4B | 71.7% | 6616/6728 | MiniMax-M2.7 | — |
| MiniMax-M3 | 71.6% | 6722/6728 | MiniMax-M2.7 | — |
| MiniMax-M3 | 45.2% | 42/6728 | MiniMax-M2.7 | — |

## p07_selfcheck

| Model | Accuracy | Scored/Total | Extractor | Judge |
| --- | --- | --- | --- | --- |
| doubao-seed-2.0-pro | 71.5% | 550/550 | doubao-seed-2.0-pro | — |
| deepseek-v4-pro | 69.0% | 546/550 | deepseek-v4-pro | — |
| glm-5.2 | 67.8% | 550/550 | glm-5.2 | — |
| Qwen/Qwen3.8-27B | 65.1% | 545/550 | Qwen/Qwen3.8-27B | — |
| Qwen/Qwen3.5-4B | 58.0% | 550/550 | Qwen/Qwen3.5-4B | — |
| MiniMax-M3 | 57.8% | 550/550 | MiniMax-M3 | — |
| MiniMax-M2.7 | 57.3% | 550/550 | MiniMax-M2.7 | — |

## p08_abstention

| Model | Accuracy | Scored/Total | Extractor | Judge |
| --- | --- | --- | --- | --- |
| Qwen/Qwen3.5-4B | 91.4% | 500/500 | MiniMax-M2.7 | — |
| Qwen/Qwen3.8-27B | 89.6% | 500/500 | MiniMax-M2.7 | — |
| glm-5.2 | 89.6% | 500/500 | MiniMax-M2.7 | — |
| deepseek-v4-pro | 89.2% | 500/500 | MiniMax-M2.7 | — |
| doubao-seed-2.0-pro | 88.6% | 500/500 | MiniMax-M2.7 | — |
| MiniMax-M3 | 85.2% | 500/500 | MiniMax-M2.7 | — |
| MiniMax-M2.7 | 83.8% | 500/500 | MiniMax-M2.7 | — |

## p08_calibration

| Model | Accuracy | Scored/Total | Extractor | Judge |
| --- | --- | --- | --- | --- |
| doubao-seed-2.0-pro | 69.6% | 550/550 | doubao-seed-2.0-pro | — |
| deepseek-v4-pro | 68.1% | 549/550 | deepseek-v4-pro | — |
| glm-5.2 | 66.7% | 550/550 | glm-5.2 | — |
| Qwen/Qwen3.8-27B | 66.4% | 545/550 | Qwen/Qwen3.8-27B | — |
| MiniMax-M3 | 58.7% | 550/550 | MiniMax-M3 | — |
| Qwen/Qwen3.5-4B | 54.4% | 550/550 | Qwen/Qwen3.5-4B | — |
| MiniMax-M2.7 | 49.1% | 550/550 | MiniMax-M2.7 | — |

## pedagogy_benchmark

| Model | Accuracy | Scored/Total | Extractor | Judge | accuracy |
| --- | --- | --- | --- | --- | --- |
| glm-5.2 | 100.0% | 20/20 | MiniMax-M2.7 | — | — |
| qwen3.7-max | 89.0% | 1119/1119 | — | — | 0.890 |
| glm-5.1 | 87.7% | 1119/1119 | — | — | 0.877 |
| doubao-seed-2-0-pro-260215 | 87.2% | 1119/1119 | — | — | 0.872 |
| Qwen/Qwen3.8-27B | 86.6% | 1119/1119 | MiniMax-M2.7 | — | — |
| deepseek-v4-flash | 85.7% | 1119/1119 | — | — | 0.857 |
| deepseek-v4-pro | 85.3% | 1119/1119 | — | — | 0.853 |
| claude-sonnet-4-6 | 84.9% | 1119/1119 | — | — | 0.849 |
| gpt-5.4 | 84.4% | 1119/1119 | — | — | 0.844 |
| kimi-k2.6 | 83.0% | 1119/1119 | — | — | 0.830 |
| MiniMax-M2.7 | 82.5% | 1119/1119 | — | — | 0.825 |
| MiniMax-M3 | 82.3% | 1119/1119 | — | — | 0.823 |
| Qwen/Qwen3.5-4B | 75.1% | 1119/1119 | MiniMax-M2.7 | — | — |
| DeepSeek-R1-0528-Qwen3-8B | 69.3% | 1119/1119 | — | — | 0.693 |

## sas_bench

| Model | Accuracy | Scored/Total | Extractor | Judge | ccs | ecs | qwk |
| --- | --- | --- | --- | --- | --- | --- | --- |
| glm-5.2 | 11.7% | 4095/4109 | MiniMax-M2.7 | — | 78.162 | 37.914 | 84.936 |
| Qwen/Qwen3.8-27B | 10.4% | 4109/4109 | MiniMax-M2.7 | — | 78.621 | 42.366 | 84.228 |
| Qwen/Qwen3.5-4B | 8.9% | 4100/4109 | MiniMax-M2.7 | — | 72.748 | 38.477 | 81.957 |
| deepseek-v4-pro | n/a | 4109/4109 | — | — | 76.629 | 61.694 | 81.864 |
| doubao-seed-2.0-pro | n/a | 4109/4109 | — | — | 76.019 | 59.268 | 82.160 |
| glm-5.1 | n/a | 4109/4109 | — | — | 78.142 | 62.602 | 83.563 |
| gpt-5.4 | n/a | 4109/4109 | — | — | 80.261 | 55.636 | 86.767 |
| kimi-k2.6 | n/a | 4109/4109 | — | — | 73.299 | 52.204 | 79.129 |
| minimax-m2.7 | n/a | 4109/4109 | — | — | 72.457 | 51.393 | 79.043 |
| minimax-m3 | n/a | 4109/4109 | — | — | 76.833 | 66.022 | 84.304 |

## tutorbench

| Model | Accuracy | Scored/Total | Extractor | Judge |
| --- | --- | --- | --- | --- |
| doubao-seed-2.0-pro | n/a | 1442/1473 | MiniMax-M2.7 | deepseek-v4-flash |
| MiniMax-M3 | n/a | 1440/1473 | MiniMax-M2.7 | deepseek-v4-flash |
| Qwen/Qwen3.5-4B | n/a | 1472/1473 | MiniMax-M2.7 | MiniMax-M3 |
| Qwen/Qwen3.8-27B | n/a | 1471/1473 | MiniMax-M2.7 | MiniMax-M3 |
| doubao-seed-2.0-pro | n/a | 1442/1473 | MiniMax-M2.7 | MiniMax-M3 |
| MiniMax-M3 | n/a | 6/6 | MiniMax-M2.7 | MiniMax-M3 |

