---
license: cc-by-nc-4.0

extra_gated_prompt: "You agree to our [Responsible Use Guidelines](https://www.etrialstestbed.org/mathnet57963-guidelines)."
    
extra_gated_fields:
  First and Last Name: text
  Affiliation(university, company, etc): text
  Country: country
  Why are you asking to use this dataset?: text
  How are you going to use this dataset?: text
  How will you store and secure this data?: text
  Do you have a university-affiliated email we could use to verify your request? If so, please enter it, if not, please explain why: text
  
  I agree to use this dataset for non-commercial use ONLY: checkbox
  While we think it's impossible for you to identify a student from these answers, you need to agree to not try to do so, and you also need to inform us if you find any PII in any of the images with the filenames: checkbox
  Check box - I agree that this data will be stored on secured institutional systems, will not be shared with unauthorized parties and will deleted or returned to ASSISTments when my research is complete: checkbox

configs:
  - config_name: Foundational ASSIST Dataset
    data_files: Data/Problems.csv
  - config_name: Interactions
    data_files: Data/Interactions.csv
  - config_name: Skills
    data_files: Data/Skills.csv
    
---

**Access requests will be faster if you have a university or research-affiliated email associated with your Hugging Face account**

**IMPORTANT UPDATE ON 3/19:** Due to an issue with git LFS 700k rows in interactions.csv were missing. Please redownload the dataset to use these rows.

# Overview of Foundational ASSIST
Foundational ASSIST is a dataset containing all natural text of problems and student answers as recorded by ASSISTments. The problems are from  from Illustrative Mathematics 6th - 8th grade math curriculum, a common core aligned curriculum popular in the United States. 

The data is in the "Data" folder. The code used to generate results in the original paper by Worden et al. is in the Code folder, and the results (in case you do not wish to reinference) are in the "Results" folder.

The dataset is comprised of three files: 
1. **Interactions**, which contains students attempts of problems, 
2. **Problems**, which includes information relevant to problems, and 
3. **Skills**, which links Problems to skills. 
The dataset was curated to include 5,000 unique students who have each completed between 211-421 problems in ASSISTments. The dataset includes 1.7 million instances of students solving problems, complete with the answer text, problem text, distractor text, and more.

# Interactions File
Interactions consists of 1,722,169 unique instances of students solving problems. The information provided includes a) problem_id, linking to Problems b) hint_count, the number of hints the student requested c) answer_text, the exact text of their first answer d) saw_answer, a boolean indicating whether the student requested to see the correct answer e) discrete_score, 0 the students score f) end_time, the time at which the student put in the correct answer to the problem g) user_xid, a unique identifier for each student.

Note that ASSISTments provides a discrete_score of 1 only if the student gets the problem correct on their first attempt, without requesting any support. If the student requests a hint, requests the answer, or has multiple tries they receive a 0. Accordingly, a student's answer can be the correct answer, but they can receive a 0 if the student requests a hint or sees the answer before entering the answer. This is shown in “table 7 cognitive accuracy when answers are incorrect” in our paper.

# Problems File
This file consists of information about 3,395 unique problems. The columns include 
1. Problem Set Id, which links problems that follow one another 
2. Problem Part, which indicates where in the Problem Set the problem occurs 
3. Problem Type, describing the type of problem 
4. Answer Type, describing the type of answer (see below table or more information) 
5. Problem Body, the problem text with HTML or markup illustrating exactly what the student saw (code to convert to natural language is available on the github) 
6. Fill-in Options 
7. Fill-in Answers 
8. Multiple Choice Options 
9. Multiple Choice Answers 
10. problem_id

Problem Set example: PSB6N4 consists of three problems. The first is problem_id 151389 (as it has ‘Problem Part’ = 1, the second is problem_id 151533, and the third/last is 151647.


<table>
  <tr>
   <td>Answer Type
   </td>
   <td>Description
   </td>
   <td>Fill-in Options
   </td>
   <td>Fill-in Answers
   </td>
   <td>Multiple Choice Options
   </td>
   <td>Multiple Choice Answers
   </td>
  </tr>
  <tr>
   <td>Numeric
   </td>
   <td>The student must type in the correct number
   </td>
   <td>The correct answer. If there are multiple correct answers they are separated by a “,”.
   </td>
   <td>The correct answer. If there are multiple correct answers they are separated by a “,”.
   </td>
   <td>n/a
   </td>
   <td>n/a
   </td>
  </tr>
  <tr>
   <td>Drop Down
   </td>
   <td>The student must select the correct option from a drop-down menu. These are similar to multiple choice
   </td>
   <td>All the drop down options, separated by “&lt;/p>,”
   </td>
   <td>The correct dropdown option.
   </td>
   <td>n/a
   </td>
   <td>n/a
   </td>
  </tr>
  <tr>
   <td>Algebraic Expression
   </td>
   <td>The student must type in the correct, short, algebraic expression, or a similar equivalent expression. E.g. if the answer is a^2+b^2 then b^2+a^2 would also be correct.
   </td>
   <td>The correct answer. If there are multiple correct answers they are separated by a “,”.
   </td>
   <td>The correct answer. If there are multiple correct answers they are separated by a “,”.
   </td>
   <td>n/a
   </td>
   <td>n/a
   </td>
  </tr>
  <tr>
   <td>Ordering
   </td>
   <td>The student must order some values in some order. Note the initial order of how these are presented to students is randomized.
   </td>
   <td>The correct order of objects, separated by “,”. 
   </td>
   <td>The correct order of objects, separated by “,”.
   </td>
   <td>n/a
   </td>
   <td>n/a
   </td>
  </tr>
  <tr>
   <td>Exact Match
   </td>
   <td>The student must type in exactly the correct answer. This could be a number, expression, point, list, etc.
   </td>
   <td>The correct answer. If there are multiple correct answers they are separated by a “,”. Note that some answers, e.g. lists, require the whole text (1,2,3) and there is only a single answer.
   </td>
   <td>The correct answer. If there are multiple correct answers they are separated by a “,”. Note that some answers, e.g. lists, require the whole text (1,2,3) and there is only a single answer.
   </td>
   <td>n/a
   </td>
   <td>n/a
   </td>
  </tr>
  <tr>
   <td>Exact Fraction
   </td>
   <td>The student must type in exactly the correct fraction.
   </td>
   <td>The correct answer. If there are multiple correct answers they are separated by a “,”.
   </td>
   <td>The correct answer. If there are multiple correct answers they are separated by a “,”.
   </td>
   <td>n/a
   </td>
   <td>n/a
   </td>
  </tr>
  <tr>
   <td>Numeric Expression
   </td>
   <td>The student must type in a numeric expression. Note that simplification occurs, e.g. if the answer is 11^3, 1331 is also considered correct.
   </td>
   <td>The correct answer. If there are multiple correct answers they are separated by a “,”.
   </td>
   <td>The correct answer. If there are multiple correct answers they are separated by a “,”.
   </td>
   <td>n/a
   </td>
   <td>n/a
   </td>
  </tr>
  <tr>
   <td>Multiple Choice
   </td>
   <td>The student must select the correct option.
   </td>
   <td>n/a
   </td>
   <td>n/a
   </td>
   <td>A list of options, separated by ‘||’.
   </td>
   <td>The correct option.
   </td>
  </tr>
  <tr>
   <td>Check all that apply
   </td>
   <td>The student must select all correct option(s).
   </td>
   <td>n/a
   </td>
   <td>n/a
   </td>
   <td>A list of options, separated by ‘||’.
   </td>
   <td>The correct option(s), separated by ‘||’.
   </td>
  </tr>
</table>

# Skills File
The skills file consists of 
1) problem_id, linking to problems in the Problems file 
2) skill_id, a unique identifier per skill 
3) node_code, which identifies the ASSISTments Skill tag Illustrative Math code for the skill and 
4) node_name, a description of the skill. In total there are 224 unique skills.

# Data Source
All data across each file are from [ASSISTments](https://new.assistments.org/), where students complete in-class work as well as homework and receive support and feedback from the platform. This work was done in conjunction with [Dr. Heffernan’s lab at WPI](https://www.neilheffernan.net/home). To ensure student privacy, our team attempted to remove all Personal Identifiable Information (PII). However, it is possible students could type PII into fill-in problems, which we aimed to detect and remove, but short of a manual review of 1.7 million interaction logs becomes infeasible. Accordingly, we ask that if people using this dataset come across PII to please contact us at [etrials@assistments.org](etrials@assistments.org) so it can be removed.

# License and Sharing Agreement
This dataset is licensed under CC-BY-NC-4.0. We require that this dataset is used for research and educational purposes following this 
[Responsible Use Guidelines](https://www.etrialstestbed.org/mathnet57963-guidelines).

# Citation

If you use the **FoundationalASSIST** dataset in your research, please cite the following paper:

> Worden, E., Heffernan, C., Heffernan, N., & Sonkar, S. (2026). FoundationalASSIST: An Educational Dataset for Foundational Knowledge Tracing and Pedagogical Grounding of LLMs. *arXiv preprint arXiv:2602.00070*.

### BibTeX

```bibtex
@article{worden2026foundationalassist,
  title={FoundationalASSIST: An Educational Dataset for Foundational Knowledge Tracing and Pedagogical Grounding of LLMs},
  author={Worden, Eamon and Heffernan, Cristina and Heffernan, Neil and Sonkar, Shashank},
  journal={arXiv preprint arXiv:2602.00070},
  year={2026}
}
```

### FAQs
Q: Where is the code that cleans the problem text?
A: This repository, in Code/clean_utils.py or cleantext.py, both are similar.

Q: How does discrete_score work?
A: Discrete score is 1 if the student solved the problem on their first try without requesting a hint (hint_count) or an explanation/seeing the answer (saw_answer).
Note this is recorded by ASSISTments. There are 433 rows where discrete_score = 1 despite saw_answer = True or hint_count > 0. In these instances, the student correctly solved the problem then requested hints/explanation/the answer anyways.

Q: Does the dataset track multiple attempts? (E.g. the student first incorrectly said 3, then incorrectly answered 6, then correctly answered 9)
A: No. We recognize it may be valuable to have this data. However, currently, answer_text (in Interactions.csv) is the first answer (right or wrong) the student submitted for the problem. Second/future attempts are not included in this dataset, but stay tuned.

Q: I ran <b>python gptoss120bvllmmcq.py --batch-size 10 --num-students 500 --bin-size 10 --min-history 50 --data-dir ../Data --num-gpus 4</b>(or a similar) line and got a different number of predictions. Why?
A: Between running the code and publishing the data we slighlty modified our PII filter. As such, this line: 
selected_users = np.random.choice(all_users, size=min(num_students, len(all_users)), replace=False)
Had a slightly different order which screwed everything up. If you'd like to run code using the exact same users, please modify your code to get the unique user_ids from Results/inference_data_kt_results.zip, and make selected_users be those unique user_ids.