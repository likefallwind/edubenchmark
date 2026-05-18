---
dataset_info:
  features:
  - name: subject
    dtype: string
  - name: data_source
    dtype: string
  - name: id
    dtype: int64
  - name: difficulty
    dtype: string
  - name: question
    dtype: string
  splits:
  - name: train
    num_bytes: 277160
    num_examples: 1154
  download_size: 102947
  dataset_size: 277160
configs:
- config_name: default
  data_files:
  - split: train
    path: data/train-*
---
