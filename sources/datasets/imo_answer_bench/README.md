---
license: cc-by-4.0
language:
  - en
tags:
  - mathematical reasoning
  - imo
  - problem solving
---

# IMO-AnswerBench

## Dataset Description

**IMO-AnswerBench** is a benchmark dataset for evaluating the mathematical reasoning capabilities of large language models. It consists of 400 challenging short-answer problems from the International Mathematical Olympiad (IMO) and other sources.

This dataset is part of the **IMO-Bench** suite, released by Google DeepMind in conjunction with their 2025 IMO gold medal achievement.

### Supported Tasks and Leaderboards

The primary task for this dataset is **mathematical problem solving**, where a model is given a problem and must produce a short, verifiable answer.

### Languages

The dataset is in English.

## Dataset Structure

### Data Instances

A typical data instance consists of a problem statement, a short answer, and metadata about the problem.

```json
{
  "Problem ID": "imo-bench-algebra-001",
  "Problem": "For a given positive integer $N$, Henry writes the quotient of $ab$ divided by $N+1$ on the board for each integer pair $(a,b)$ where $1\\le a,b\\le N$. Find all $N$ such that the sum of the $N^2$ numbers Henry wrote on the board is $\\frac{N^3-N^2+2}{4}$.",
  "Short Answer": "3",
  "Category": "Algebra",
  "Subcategory": "Operation",
  "Source": "IMO Shortlist 2021"
}
```

### Data Fields

- `Problem ID`: A unique identifier for the problem.
- `Problem`: The problem statement in LaTeX format.
- `Short Answer`: The correct short answer to the problem.
- `Category`: The mathematical category of the problem (Algebra, Combinatorics, Geometry, Number Theory).
- `Subcategory`: A more specific subcategory.
- `Source`: The source of the problem (e.g., IMO Shortlist, national Olympiads).

### Data Splits

The dataset is not split into train/validation/test sets. It is intended for zero-shot or few-shot evaluation.

## Dataset Creation

### Curation Rationale

The problems were curated to cover a wide range of mathematical topics and difficulty levels, with a focus on problems that require deep reasoning and problem-solving skills.

### Source Data

The problems were sourced from the International Mathematical Olympiad (IMO), IMO Shortlists, and various national Olympiads.

### Annotations

The short answers were verified by a panel of IMO medalists and mathematicians.

## Considerations for Using the Data

### Social Impact of Dataset

This dataset can be used to advance the state of the art in mathematical reasoning, which has applications in science, engineering, and education.

### Discussion of Biases

The dataset is focused on competitive mathematics problems, which may not be representative of all types of mathematical reasoning.

### Other Known Limitations

The dataset is in English and uses LaTeX for mathematical notation.

## Paper

This dataset is associated with the paper: [Towards Robust Mathematical Reasoning](https://huggingface.co/papers/2511.01846)

## Additional Information

### Dataset Curators

The dataset was curated by the Google DeepMind Superhuman Reasoning team.

### Licensing Information

The dataset is licensed under the Creative Commons Attribution 4.0 International License (CC-BY-4.0).

### Citation Information

```
@inproceedings{luong-etal-2025-towards,
    title = "Towards Robust Mathematical Reasoning",
    author  = {Thang Luong and Dawsen Hwang and Hoang H. Nguyen and Golnaz Ghiasi and Yuri Chervonyi and Insuk Seo and Junsu Kim and Garrett Bingham and Jonathan Lee and Swaroop Mishra and Alex Zhai and Clara Huiyi Hu and Henryk Michalewski and Jimin Kim and Jeonghyun Ahn and Junhwi Bae and Xingyou Song and Trieu H. Trinh and Quoc V. Le and Junehyuk Jung},
    booktitle = "Proceedings of the 2025 Conference on Empirical Methods in Natural Language Processing",
    year = "2025",
    url = "https://aclanthology.org/2025.emnlp-main.1794/",
}
```
