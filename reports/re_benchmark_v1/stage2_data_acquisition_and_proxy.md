# Stage 2 数据补齐与替代策略

本阶段结论是：可以立刻使用的本地数据足以形成研究 pilot，但不足以宣称完整覆盖所有推荐 benchmark。v1 必须把 proxy 和 missing 标清楚。

## Acquisition 优先级

| benchmark | current status | next action | impact on v1 |
| --- | --- | --- | --- |
| Pedagogy Benchmark | manual_access_required | 接受 HF 条款后下载 | 影响 C2 教学法 MCQ；v1 暂用 EduBench proxy。 |
| TutorBench | download_incomplete | 重试 HF parquet 下载 | 影响 C2 tutoring 主测；v1 暂用 MathTutorBench/EduBench proxy。 |
| OlympiadBench | metadata_only | 下载官方 HF/Drive 数据 | 影响 C1 高难奥赛推理；v1 不伪装本地代码为数据。 |
| EdNet KT1 | metadata_only | 下载 bit.ly/Kaggle KT1 zip | 影响 C3 KT protocol 展示；不进入 LLM prompt。 |
| MMLU-Pro | external_download_needed | HF 数据较小，优先补齐 | 影响 C1 D01；v1 用 MMLU proxy。 |
| Safe-Child-LLM | external_download_needed | clone 官方 GitHub 并核验数据 | 影响 C5 儿童安全补充；v1 主测仍用 EduGuard。 |
| LiveCodeBench | external_download_needed | clone repo + sandbox | 影响 C1 代码执行；v1 用 MBPP/HumanEval/APPS proxy。 |

## Proxy 策略

| missing/target | v1 proxy | boundary |
| --- | --- | --- |
| MMLU-Pro | MMLU | D01 proxy only; do not label scores as MMLU-Pro. |
| OmniEduBench | E-EVAL / GaokaoBench / EduBench | Chinese education proxy with different task mix. |
| YouthSafe/YAIR | EduGuard-Bench + Safe-Child-LLM after acquisition | Youth-risk coverage remains incomplete. |
| ASAP-AES/SAS | EduEval Essay_Scoring + MathTutorBench | Essay/process feedback proxy, not Kaggle ASAP. |
| EdNet/ASSISTments | Protocol-only record | KT/CD cannot be merged into text LLM accuracy. |

## 暂缓项

- `YouthSafe/YAIR`：截至本次核验未找到可直接下载的 YAIR 数据文件；不进入 runnable pilot。

- `SproutBench`：按 release-pending 处理。

- `CASTLE`：发现论文线索，但未确认官方数据下载；按 release-pending 处理。

- `ASAP-AES/SAS`：需要 Kaggle 账号和条款，不能自动补齐。

- `Video-MME/DAiSEE`：多模态/视频成本高，后置。
