---
language:
- en
license: mit
task_categories:
- text-generation
pretty_name: ConvoLearn
size_categories:
- 1K<n<10K
tags:
- education
- tutoring
- dialogue
- conversational
- pedagogical
- constructivist-learning
---

# ConvoLearn

A dataset of tutor-student conversations demonstrating dialogic (knowledge-building) pedagogies.

## What's in here

2,134 dialogues between teachers and a simulated 7th-grade student discussing middle school Earth Science. Each conversation demonstrates one of six knowledge-building dimensions: cognitive engagement, formative assessment, accountability, cultural responsiveness, metacognition, or power dynamics.

The teachers were real educators (323 credentialed K-12 teachers, mean 10.9 years experience) recruited through Prolific. The student (Jamie) was simulated using Gemini-1.5-Pro with a consistent persona. Each dialogue has ~20 turns and was filtered for safety and basic quality. Effectiveness and completeness ratings are included as metadata across the full quality spectrum.

## Dataset Fields

- `kb_subdim`: Specific knowledge-building subdimension used (21 total)
- `kb_dim`: Broader knowledge-building dimension (6 total)
- `effectiveness_consensus`: Rating of how well the conversation demonstrates the dimension (1-5 scale)
- `completeness_consensus`: Rating of how complete the conversation is (1-3 scale)
- `cleaned_conversation`: Actual conversation text (cleaned)
- `earthscience_topic`: Earth Science concept discussed
- `num_exchanges`: Number of back-and-forth turns

## Quick stats

- Total conversations: 2,134
- Subject area: California Earth Science (middle school)
- Mean effectiveness: 3.36 / 5 (full spectrum retained)
- Knowledge-building dimension distribution:
  - Metacognition: 27.6%
  - Cognitive Engagement: 23.5%
  - Formative Assessment: 13.6%
  - Power Dynamics: 13.4%
  - Accountability: 12.9%
  - Cultural Responsiveness: 9.0%

## How to use this dataset

### Load the dataset
```python
from datasets import load_dataset

dataset = load_dataset("masharma/convolearn")

print(f"Total conversations: {len(dataset['train'])}")
print(dataset['train'][0])
```

### Filter by knowledge-building dimension
```python
# Get all metacognition conversations
metacognition_convos = dataset['train'].filter(
    lambda x: x['kb_dim'] == 'Metacognition'
)

# Get high-quality subset (effectiveness >= 3, completeness >= 2)
high_quality = dataset['train'].filter(
    lambda x: x['effectiveness_consensus'] >= 3 and x['completeness_consensus'] >= 2
)
```

### Analyze pedagogical patterns
```python
import pandas as pd

df = dataset['train'].to_pandas()

dimension_counts = df['kb_dim'].value_counts()
print(dimension_counts)

effectiveness_by_dim = df.groupby('kb_dim')['effectiveness_consensus'].mean()
print(effectiveness_by_dim)
```

## How it was made

We recruited ~500 U.S.-based certified teachers via Prolific. Each teacher was trained on two knowledge-building subdimensions and completed six conversations (three per subdimension) with a simulated 7th-grade student. After collection, dialogues were filtered for safety and quality issues (vagueness, repetition, technical errors). Effectiveness and completeness ratings were assigned via dual LLM annotation (GPT-4o + Claude Haiku), with disagreements resolved by Claude Sonnet 4.5. The full dataset spans the complete quality spectrum to support diverse uses including fine-tuning, contrastive learning, and effectiveness-weighted training.

## What it's useful for

Training or evaluating AI tutoring systems, especially if you care about pedagogical quality. The full quality spectrum makes it suitable for contrastive learning and DPO-style training in addition to standard fine-tuning. Also useful for studying how different teaching approaches play out in dialogue.

## Limitations

The student is simulated, not real. All conversations are in English, focused on a single subject (Earth Science), and reflect the US middle school curriculum. The pedagogical framework is constructivist, which may not align with all teaching philosophies. LLM-based annotation produces silver-standard labels; treat effectiveness and completeness scores as approximate rather than ground truth.

## Citation
```bibtex
@inproceedings{sharma2026convolearn,
  title={ConvoLearn: A Dataset for Fine-Tuning Dialogic AI Tutors},
  author={Sharma, Mayank and Pea, Roy and Subramonyam, Hari},
  booktitle={Under Review},
  year={2026}
}
```

## License

MIT

Questions? Open an issue or contact masharma@stanford.edu
