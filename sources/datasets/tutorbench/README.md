---
dataset_info:
  features:
  - name: TASK_ID
    dtype: string
  - name: BATCH
    dtype: string
  - name: SUBJECT
    dtype: string
  - name: PROMPT
    dtype: string
  - name: IMAGE_URL
    dtype: string
  - name: UC1_INITIAL_EXPLANATION
    dtype: string
  - name: FOLLOW_UP_PROMPT
    dtype: string
  - name: RUBRICS
    dtype: string
  - name: bloom_taxonomy
    dtype: string
  - name: Image
    dtype: image
  splits:
  - name: train
    num_bytes: 854610962.881
    num_examples: 1473
  download_size: 1118252762
  dataset_size: 854610962.881
configs:
- config_name: default
  data_files:
  - split: train
    path: data/train-*
---

TutorBench is a challenging benchmark to assess tutoring capabilities of LLMs. TutorBench consists of examples drawn from three common tutoring tasks: (i) generating adaptive explanations tailored to a student’s confusion, (ii) providing actionable feedback on a student’s work, and (iii) promoting active learning through effective hint generation.

Paper: [TutorBench: A Benchmark To Assess Tutoring Capabilities Of Large Language Models](https://www.arxiv.org/abs/2510.02663)
