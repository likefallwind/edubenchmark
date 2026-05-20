# Stage 1 数据状态核验

核验日期：2026-05-20。状态口径采用研究 manifest 枚举：`local_ready`、`metadata_only`、`download_incomplete`、`external_download_needed`、`manual_access_required`、`paper_or_release_pending`、`not_found`。

## 总体状态

| status | count |
| --- | --- |
| local_ready | 8 |
| metadata_only | 3 |
| download_incomplete | 1 |
| external_download_needed | 5 |
| manual_access_required | 5 |
| paper_or_release_pending | 2 |
| not_found | 1 |

## C1-C5 可用性总表

| category | local_ready | metadata_only | download_incomplete | external_download_needed | manual_access_required | paper_or_release_pending | not_found |
| --- | --- | --- | --- | --- | --- | --- | --- |
| C1 | 3 | 1 | 0 | 4 | 0 | 0 | 0 |
| C2 | 2 | 0 | 1 | 0 | 1 | 0 | 0 |
| C3 | 0 | 1 | 0 | 0 | 2 | 0 | 0 |
| C4 | 2 | 1 | 0 | 0 | 2 | 0 | 0 |
| C5 | 1 | 0 | 0 | 1 | 0 | 2 | 1 |

## Benchmark 明细

| C | benchmark | status | local evidence | v1 decision |
| --- | --- | --- | --- | --- |
| C1 | MMLU-Pro | external_download_needed | not present locally; Hugging Face TIGER-Lab/MMLU-Pro lists parquet files | Use local MMLU as D01 proxy; do not report as MMLU-Pro. |
| C1 | MMLU | local_ready | parquet splits are present for multiple subjects | D01 proxy for MMLU-Pro. |
| C1 | OmniEduBench | external_download_needed | not present locally | Use E-EVAL, GaokaoBench, and EduBench as Chinese education proxies. |
| C1 | AGIEval | local_ready | data/v1 and data/v1_1 JSONL files are present | Runnable C1 standardized-exam smoke items. |
| C1 | OlympiadBench | metadata_only | local clone has README, resources, eval/inference code; no full problem data files | Keep as C1 high-difficulty target; do not count local code clone as runnable data. |
| C1 | MathVista | local_ready | data/testmini.json and test.json are present | Include metadata/text-only or multimodal-adapter samples; image scoring is separate. |
| C1 | Video-MME | external_download_needed | not present locally | Record as coverage gap; do not run in v1 smoke. |
| C1 | LiveCodeBench | external_download_needed | not present locally | Use MBPP/HumanEval/APPS proxy; do not merge with text-only scores. |
| C2 | TutorBench | download_incomplete | README exists; HF cache has .incomplete parquet downloads and lock files | Represent tutoring via EduBench/MathTutorBench proxies and mark TutorBench as missing. |
| C2 | Pedagogy Benchmark | manual_access_required | README only; HF page is gated and requires accepting conditions/contact sharing | Cannot run MCQ stage until gated data is available; keep as priority acquisition. |
| C2 | EduVisBench | local_ready | train parquet and image directory are present | Include as judge-required visual/pedagogy generation sample. |
| C2 | EduBench | local_ready | English/Chinese scenario JSONL files are present | Runnable proxy for teaching design, feedback, and personalization. |
| C3 | ASSISTments | manual_access_required | not present locally | Record as KT/CD gap; use EdNet protocol description only. |
| C3 | EdNet | metadata_only | local clone has README only; KT1 zip is not downloaded | Use as protocol item, not an LLM prompt. |
| C3 | DAiSEE | manual_access_required | not present locally | Postpone; video engagement is a C3 coverage gap. |
| C4 | ASAP-AES / ASAP 2.0 | manual_access_required | not present locally | Use EduEval Essay_Scoring proxy. |
| C4 | ASAP-SAS | manual_access_required | not present locally | Record as short-answer scoring gap; SAS-Bench local repo has code but not source dataset. |
| C4 | SAS-Bench | metadata_only | local repo has prompts/code/docs, not full benchmark data | Do not score; keep as external evidence for short-answer scoring methodology. |
| C4 | EduEval Essay_Scoring | local_ready | essay scoring JSONL exists locally | Runnable proxy for essay scoring; qualitative/manual score calibration required. |
| C4 | MathTutorBench | local_ready | mathdial_bridge JSON files are present | Runnable C4 process-feedback sample; judge-required. |
| C5 | EduGuard-Bench | local_ready | SATAs.xlsx and adversarial_prompts.xlsx exist locally | Runnable safety smoke sample; qualitative human review in v1. |
| C5 | Safe-Child-LLM | external_download_needed | not present locally; paper says benchmark data/code are publicly released on GitHub | Priority child-safety supplement after download. |
| C5 | YouthSafe / YAIR | not_found | not present locally; public search found model/paper pages, not dataset files | Do not include as runnable; mention as external evidence gap. |
| C5 | SproutBench | paper_or_release_pending | not present locally | External roadmap item only. |
| C5 | CASTLE | paper_or_release_pending | not present locally; paper found, official data path not confirmed | External roadmap item only. |

## 修正结论

- `OlympiadBench` 本地只有代码、README、资源图和 eval/inference 脚本，不能算数据 ready。

- `TutorBench` 本地 Hugging Face 缓存存在 `.incomplete` parquet，属于下载中断。

- `Pedagogy Benchmark` 本地只有 README；线上 HF 数据集是 gated，需要先接受条件。

- `EdNet` 本地只有 README/git clone；KT1 数据包未下载，只能做 protocol 说明。
