---
dataset_info:
  features:
  - name: id
    dtype: string
  - name: chapter_title
    dtype: string
  - name: section_title
    dtype: string
  - name: answer_type
    dtype: string
  - name: problem_text
    dtype: string
  - name: solution_text
    dtype: string
  - name: answer_text
    dtype: string
  - name: question_type
    dtype: string
  - name: question_answer_type
    dtype: string
  - name: visual_key_points
    list:
    - name: description
      dtype: string
    - name: element
      dtype: string
  - name: problem_image
    dtype: image
  - name: summary_solution_text
    dtype: string
  - name: visual_identification_answer
    dtype: string
  - name: visual_identification_option
    dtype: string
  splits:
  - name: train
    num_bytes: 54588039
    num_examples: 1000
  download_size: 52475831
  dataset_size: 54588039
configs:
- config_name: default
  data_files:
  - split: train
    path: data/train-*
---
