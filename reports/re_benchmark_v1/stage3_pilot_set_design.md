# Stage 3 研究版 Pilot Set 设计

研究 pilot 当前共 142 条，其中包含真实本地样本、proxy 样本、protocol-only 记录和 data-gap 记录。后两者不参与 LLM prompt 跑分。

## 按 C 类计数

| category | items |
| --- | --- |
| C1 | 49 |
| C2 | 32 |
| C3 | 21 |
| C4 | 20 |
| C5 | 20 |

## 按 runner 状态计数

| runner_status | items |
| --- | --- |
| auto_exact_match_candidate | 39 |
| needs_code_or_program_runner | 10 |
| needs_llm_or_human_judge | 70 |
| needs_multimodal_adapter | 20 |
| not_runnable_data_gap | 2 |
| protocol_only_not_llm_prompt | 1 |

## 按 benchmark 计数

| benchmark | items |
| --- | --- |
| agieval | 19 |
| ednet | 1 |
| edubench | 10 |
| edueval | 20 |
| eduguard_bench | 20 |
| eduvisbench | 10 |
| mathtutorbench | 20 |
| mathvista | 10 |
| mbpp | 10 |
| mmlu | 10 |
| pedagogy_benchmark | 1 |
| statics2011 | 10 |
| tutorbench | 1 |

## 字段口径

- `source_status` 来自研究 manifest，不把 README-only 或下载中断数据记为 ready。

- `is_proxy=true` 表示该样本服务于目标 benchmark/dimension 的替代测量，报告中不能混称。

- `is_protocol_only=true` 表示这是 KT/缺口/protocol 记录，不发送给 MiniMax。

- `requires_llm_judge=true` 的开放题在 v1 只归档回答并抽样人工阅读。
