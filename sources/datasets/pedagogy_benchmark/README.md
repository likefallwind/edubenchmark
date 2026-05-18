---
license: mit
configs:
- config_name: cdpk_main
  data_files:
  - split: train
    path: cdpk_main/train-*
- config_name: cdpk_send
  data_files:
  - split: train
    path: cdpk_send/train-*
dataset_info:
- config_name: cdpk_main
  features:
  - name: question_id
    dtype: int64
  - name: question
    dtype: string
  - name: answer_a
    dtype: string
  - name: answer_b
    dtype: string
  - name: answer_c
    dtype: string
  - name: answer_d
    dtype: string
  - name: answer_e
    dtype: float64
  - name: answer_f
    dtype: float64
  - name: answer_g
    dtype: float64
  - name: correct_answer
    dtype: string
  - name: category
    dtype: string
  - name: pedagogical_subdomain
    dtype: string
  - name: age_group
    dtype: string
  - name: year
    dtype: int64
  - name: secondary_category
    dtype: string
  splits:
  - name: train
    num_bytes: 855590
    num_examples: 920
  download_size: 441017
  dataset_size: 855590
- config_name: cdpk_send
  features:
  - name: question_id
    dtype: int64
  - name: question
    dtype: string
  - name: answer_a
    dtype: string
  - name: answer_b
    dtype: string
  - name: answer_c
    dtype: string
  - name: answer_d
    dtype: string
  - name: answer_e
    dtype: float64
  - name: answer_f
    dtype: float64
  - name: answer_g
    dtype: float64
  - name: correct_answer
    dtype: string
  - name: category
    dtype: string
  - name: pedagogical_subdomain
    dtype: string
  - name: age_group
    dtype: string
  - name: year
    dtype: int64
  - name: secondary_category
    dtype: string
  splits:
  - name: train
    num_bytes: 266282
    num_examples: 223
  download_size: 140499
  dataset_size: 266282
---

# Dataset Card for The Pedagogy Benchmark

## Dataset Description

* **Repository:** [GitHub](https://github.com/Ai-for-Education/pedagogy-benchmark)
* **Paper:** [arXiv](https://arxiv.org/abs/2506.18710)
* **CDPK Leaderboard:** [CDPK](https://rebrand.ly/pedagogy)
* **SEND Leaderboard:** [SEND](https://rebrand.ly/sendpedagogy)

### Dataset Summary

This dataset provides the questions for the pedgagoy benchmarks described in [Benchmarking the Pedagogical Knowledge of Large Language Models](https://arxiv.org/abs/2506.18710).
These are questions from teacher training exams, which are designed to evaluate large language models on their Cross-Domain Pedagogical Knowledge (CDPK) and Special Education Needs and Disability (SEND) pedagogical knowledge. 
Existing benchmarks have largely focused on content knowledge, leaving a significant gap in assessing a model's understanding of teaching methods and practices.

The benchmarks are constructed from a curated set of multiple-choice questions sourced from the professional development exams for teachers provided by the Chilean Ministry of Education. These questions cover a range of pedagogical subdomains, including teaching strategies, assessment methods, student understanding, education theories, and classroom management.

The dataset is divided into two main configurations:
* **CDPK (Cross-Domain Pedagogical Knowledge):** Comprises 920 multiple-choice questions that evaluate a broad range of general pedagogical knowledge.
* **SEND (Special Educational Needs and Disability):** A more specialized benchmark consisting of 223 questions focused on pedagogy related to special educational needs and disabilities.

We request that you *do not reveal examples from this dataset online*, to reduce the risk of leakage into foundation model training corpora. 

### Supported Tasks and Leaderboards

The primary supported task is **multiple-choice question answering**. The dataset is designed to benchmark the pedagogical knowledge of Large Language Models.

You can explore results on the interactive online leaderboards, which are frequently updated with new models. 
A leaderboard is available for the [CDPK Benchmark](https://rebrand.ly/pedagogy) and a separate one is dedicated to the [SEND Benchmark](https://rebrand.ly/sendpedagogy).

### Languages

The source questions were originally in Spanish and have been translated into English for this dataset. See the [preprint](https://arxiv.org/abs/2506.18710) for more details. 

## Dataset Structure

### Data Instances

Each data point consists of a question, four possible answers, the correct answer's index, and metadata about the question's category, educational level, and pedagogical subdomain.

**Example:**
```
{
  "question": "According to Bowlby's theory, which of the following statements corresponds to a characteristic of attachment?",
  "answer_a": "It is a process that lasts until the early years of life",
  "answer_b": "It is a bond that must be stable and continuous to ensure proper development",
  "answer_c": "It is a bond that determines all affective relationships in life and development",
  "answer_d": "It is the first relationship of the newborn with its mother and cannot be replaced by another person"
  ],
  "answer": "B",
  "category": "General",
  "age_group": "Secondary",
  "pedagogical_subdomain": "Education theories"
}
```


### Data Fields

- `question`: The text of the multiple-choice question.
- `answer_a`, `answer_b`, ... : The answer responses. 
- `correct_answer`: The letter corresponding to the correct answer (e.g. "B")
- `category`: The subject category of the question (e.g., 'Science', 'Literacy', 'Maths', 'SEND').
- `education_level`: The educational level the question pertains to (e.g., 'Pre-primary', 'Primary', 'Secondary').
- `pedagogical_subdomain`: The pedagogical subdomain of the question (e.g., 'Teaching strategies', 'Assessment').
- `year`: The year of the exam from which the question was taken. 

Note that SEND questions all have `category` as "SEND", have have the additional column:
- `secondary_category`: The subject category of the SEND question

### Citation Information

If you find this useful in your research, please consider citing the paper:

```
 @misc{lelievre2025pedagogybenchmark,
      title={Benchmarking the Pedagogical Knowledge of Large Language Models}, 
      author={Maxime Lelièvre and Amy Waldock and Meng Liu and Natalia Valdés Aspillaga and Alasdair Mackintosh and María José Ogando Portela and Jared Lee and Paul Atherton and Robin A. A. Ince and Oliver G. B. Garrod},
      year={2025},
      eprint={2506.18710},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2506.18710}, 
}
```

