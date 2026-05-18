---
language:
- en
license: cc-by-4.0
tags:
- dialog
- tutoring
- math
- gsm8k
- conversation
- education
task_categories:
- text-generation
pretty_name: MathDial
size_categories:
- 1K<n<10K
---
# Mathdial dataset
https://arxiv.org/abs/2305.14536

MathDial: A Dialogue Tutoring Dataset with Rich Pedagogical Properties Grounded in Math Reasoning Problems.

MathDial is grounded in math word problems as well as student confusions which provide a challenging testbed for creating faithful and equitable dialogue tutoring models able to reason over complex information. Current models achieve high accuracy in solving such problems but they fail in the task of teaching.

## Data Structure
- `qid` - unique identifier of the problem
- `scenario` - order of the problem in the data collection, out of the 5 scenarios in a session
- `question` - math problem text
- `ground_truth` - correct answer to the problem
- `student_incorrect_solution` - student incorrect solution to the problem caused by some confusion
- `student_profile` - student profile based on general math problem solving student misconceptions
- `teacher_described_confusion` - teacher annotated student confusion in free text
- `self-correctness` - teacher annotated whether student solved the problem correctly by the end of the conversation
    - options: `Yes`, `Yes, but I had to reveal the answer`, `No`
- `self-typical-confusion` - teacher annotated whether student exhibited a typical 7th grade confusion, Likert scale 1 (unlikely) to 5 (very likely)
- `self-typical-interactions` - teacher annotated whether student exhibited typical 7th grade interactions, Likert scale 1 (unlikely) to 5 (very likely)
- `conversation` - conversation in a string format with `|EOM|` delimiter between Teacher and Student personas  `Persona: (dialog_act) text` e.g. `Teacher: (focus) What is the difference?|EOM|Student: I mean ...|EOM|Teacher:`


---
license: cc-by-4.0
---