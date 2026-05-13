# AI-Edu Benchmark Dataset Acquisition Manifest

生成日期：2026-05-13

本文件回答 `todo.md` 中“下载其数据集”的可执行层面：对每个 benchmark/resource 记录数据入口、建议本地路径、可用下载命令和人工申请风险。为避免误下超大、闭源、需授权或需同意条款的数据，本脚本只生成下载清单，不默认批量下载。

## 状态统计

| Status | Count |
|---|---:|
| download_command_available_not_bulk_downloaded | 58 |
| manual_access_or_metadata_only | 19 |
| paper_only_or_release_pending | 1 |

## 入口类型统计

| Access mode | Count |
|---|---:|
| github_repository | 40 |
| huggingface_dataset | 16 |
| kaggle_competition | 2 |
| paper_or_pdf | 27 |
| project_page_or_manual | 24 |

## 可直接执行的下载入口

| Benchmark | Local path | Commands / manual notes |
|---|---|---|
| AGIEval | `sources/datasets/agieval` | `git clone --depth 1 https://github.com/ruixiangcui/AGIEval sources/datasets/agieval` |
| Ape210K | `sources/datasets/ape210k` | `git clone --depth 1 https://github.com/Chenny0808/ape210k sources/datasets/ape210k` |
| APPS Dataset | `sources/datasets/apps_dataset` | `git clone --depth 1 https://github.com/hendrycks/apps sources/datasets/apps_dataset` |
| ASAP-AES | `sources/datasets/asap_aes` | `kaggle competitions download -c asap-aes -p sources/datasets/asap_aes`<br>requires Kaggle account, competition terms acceptance, and API token |
| ASAP-SAS | `sources/datasets/asap_sas` | `kaggle competitions download -c asap-sas -p sources/datasets/asap_sas`<br>requires Kaggle account, competition terms acceptance, and API token |
| BigMath-Verified | `sources/datasets/bigmath_verified` | `huggingface-cli download --repo-type dataset SynthLabsAI/Big-Math-RL-Verified --local-dir sources/datasets/bigmath_verified` |
| C-EVAL | `sources/datasets/ceval` | `git clone --depth 1 https://github.com/hkust-nlp/ceval sources/datasets/ceval` |
| ChartQA | `sources/datasets/chartqa` | `git clone --depth 1 https://github.com/vis-nlp/chartqa sources/datasets/chartqa` |
| Chinese Fineweb Edu | `sources/datasets/chinese_fineweb_edu` | `huggingface-cli download --repo-type dataset opencsg/chinese-fineweb-edu --local-dir sources/datasets/chinese_fineweb_edu` |
| CMMLU | `sources/datasets/cmmlu` | `git clone --depth 1 https://github.com/haonan-li/CMMLU sources/datasets/cmmlu` |
| CMMU | `sources/datasets/cmmu` | `git clone --depth 1 https://github.com/flageval-baai/CMMU sources/datasets/cmmu` |
| Codecademy Dataset | `sources/datasets/codecademy_dataset` | `git clone --depth 1 https://github.com/Codecademy/datasets sources/datasets/codecademy_dataset` |
| ConvoLearn | `sources/datasets/convolearn` | `huggingface-cli download --repo-type dataset masharma/convolearn --local-dir sources/datasets/convolearn` |
| CS1QA | `sources/datasets/cs1qa` | `git clone --depth 1 https://github.com/cyoon47/CS1QA sources/datasets/cs1qa` |
| EdNet | `sources/datasets/ednet` | `git clone --depth 1 https://github.com/riiid/ednet sources/datasets/ednet` |
| EduBench | `sources/datasets/edubench` | `git clone --depth 1 https://github.com/ybai-nlp/EduBench sources/datasets/edubench` |
| EduDial | `sources/datasets/edudial` | `git clone --depth 1 https://github.com/Mind-Lab-ECNU/EduDial sources/datasets/edudial` |
| EduEval | `sources/datasets/edueval` | `git clone --depth 1 https://github.com/Maerzs/E_edueval sources/datasets/edueval` |
| EduGuard-Bench | `sources/datasets/eduguard_bench` | `git clone --depth 1 https://github.com/YL1N/EduGuardBench sources/datasets/eduguard_bench` |
| EduVisBench | `sources/datasets/eduvisbench` | `huggingface-cli download --repo-type dataset Haonian/EduVisBench --local-dir sources/datasets/eduvisbench` |
| E-EVAL | `sources/datasets/eeval` | `git clone --depth 1 https://github.com/AI-EDU-LAB/E-EVAL sources/datasets/eeval` |
| FineWeb-Edu | `sources/datasets/fineweb_edu` | `huggingface-cli download --repo-type dataset HuggingFaceFW/fineweb-edu --local-dir sources/datasets/fineweb_edu` |
| FoundationalAssist | `sources/datasets/foundationalassist` | `huggingface-cli download --repo-type dataset ASSISTments/FoundationalASSIST --local-dir sources/datasets/foundationalassist` |
| GaokaoBench | `sources/datasets/gaokaobench` | `git clone --depth 1 https://github.com/OpenLMLab/GAOKAO-Bench sources/datasets/gaokaobench` |
| Google Education Dialogue Dataset | `sources/datasets/google_education_dialogue_dataset` | `git clone --depth 1 https://github.com/google-research-datasets/Education-Dialogue-Dataset sources/datasets/google_education_dialogue_dataset` |
| GSM8K | `sources/datasets/gsm8k` | `huggingface-cli download --repo-type dataset openai/gsm8k --local-dir sources/datasets/gsm8k` |
| HumanEval | `sources/datasets/humaneval` | `git clone --depth 1 https://github.com/openai/human-eval sources/datasets/humaneval` |
| IMO-ANSWER BENCH | `sources/datasets/imo_answer_bench` | `huggingface-cli download --repo-type dataset Hwilner/imo-answerbench --local-dir sources/datasets/imo_answer_bench` |
| InnoSpark | `sources/datasets/innospark` | `git clone --depth 1 https://github.com/sii-research/coclp.git sources/datasets/innospark` |
| InteractScience | `sources/datasets/interactscience` | `git clone --depth 1 https://github.com/open-compass/InteractScience sources/datasets/interactscience` |
| K12Vista | `sources/datasets/k12vista` | `git clone --depth 1 https://github.com/lichongod/K12Vista sources/datasets/k12vista` |
| LectureBank | `sources/datasets/lecturebank` | `git clone --depth 1 https://github.com/Yale-LILY/LectureBank sources/datasets/lecturebank` |
| LeetCode Student Submissions | `sources/datasets/leetcode_student_submissions` | `huggingface-cli download --repo-type dataset newfacade/LeetCodeDataset --local-dir sources/datasets/leetcode_student_submissions` |
| MATH | `sources/datasets/math` | `git clone --depth 1 https://github.com/hendrycks/math sources/datasets/math` |
| Math23K | `sources/datasets/math23k` | `git clone --depth 1 https://github.com/SCNU203/Math23k sources/datasets/math23k` |
| MATH-500 | `sources/datasets/math_500` | `git clone --depth 1 https://github.com/hendrycks/math sources/datasets/math_500` |
| MathDial | `sources/datasets/mathdial` | `huggingface-cli download --repo-type dataset eth-nlped/mathdial --local-dir sources/datasets/mathdial` |
| MathTutorBench | `sources/datasets/mathtutorbench` | `git clone --depth 1 https://github.com/eth-lre/mathtutorbench sources/datasets/mathtutorbench` |
| MathVista | `sources/datasets/mathvista` | `git clone --depth 1 https://github.com/lupantech/MathVista sources/datasets/mathvista` |
| MBPP | `sources/datasets/mbpp` | `huggingface-cli download --repo-type dataset Muennighoff/mbpp --local-dir sources/datasets/mbpp` |
| ME2 | `sources/datasets/me2` | `huggingface-cli download --repo-type dataset jungypark/ME2 --local-dir sources/datasets/me2` |
| MMLU | `sources/datasets/mmlu` | `huggingface-cli download --repo-type dataset cais/mmlu --local-dir sources/datasets/mmlu` |
| NCTE Transcripts | `sources/datasets/ncte_transcripts` | `git clone --depth 1 https://github.com/ddemszky/classroom-transcript-analysis sources/datasets/ncte_transcripts` |
| OlymMATH | `sources/datasets/olymmath` | `git clone --depth 1 https://github.com/RUCAIBox/OlymMATH sources/datasets/olymmath` |
| OlympiadBench | `sources/datasets/olympiadbench` | `git clone --depth 1 https://github.com/OpenBMB/OlympiadBench sources/datasets/olympiadbench` |
| Pedagogy Benchmark | `sources/datasets/pedagogy_benchmark` | `huggingface-cli download --repo-type dataset AI-for-Education/pedagogy-benchmark --local-dir sources/datasets/pedagogy_benchmark` |
| PTADisc | `sources/datasets/ptadisc` | `git clone --depth 1 https://github.com/wahr0411/PTADisc sources/datasets/ptadisc` |
| QACP | `sources/datasets/qacp` | `git clone --depth 1 https://github.com/NTAIX/Chinese-Python-QA-Dataset sources/datasets/qacp` |
| SAS-Bench | `sources/datasets/sas_bench` | `git clone --depth 1 https://github.com/PKU-DAIR/SAS-Bench sources/datasets/sas_bench` |
| SCB-Dataset | `sources/datasets/scb_dataset` | `git clone --depth 1 https://github.com/Whiffe/SCB-dataset sources/datasets/scb_dataset` |
| SciVideoBench | `sources/datasets/scivideobench` | `huggingface-cli download --repo-type dataset groundmore/scivideobench --local-dir sources/datasets/scivideobench` |
| SIGHT | `sources/datasets/sight` | `git clone --depth 1 https://github.com/rosewang2008/sight sources/datasets/sight` |
| SocraticLM | `sources/datasets/socraticlm` | `git clone --depth 1 https://github.com/Ljyustc/SocraticLM sources/datasets/socraticlm` |
| STATICS2011 | `sources/datasets/statics2011` | `git clone --depth 1 https://github.com/chrispiech/DeepKnowledgeTracing sources/datasets/statics2011` |
| TalkMoves | `sources/datasets/talkmoves` | `git clone --depth 1 https://github.com/SumnerLab/TalkMoves sources/datasets/talkmoves` |
| TutorBench | `sources/datasets/tutorbench` | `huggingface-cli download --repo-type dataset ScaleAI/TutorBench --local-dir sources/datasets/tutorbench` |
| TutorialBank | `sources/datasets/tutorialbank` | `git clone --depth 1 https://github.com/Yale-LILY/TutorialBank sources/datasets/tutorialbank` |
| VisualEDU | `sources/datasets/visualedu` | `git clone --depth 1 https://github.com/UchihaIchigo/VisualEDU sources/datasets/visualedu` |
| Adaptive Geography Practice | `sources/datasets/adaptive_geography_practice` | manual_access_or_metadata_only |
| ARIC | `sources/datasets/aric` | manual_access_or_metadata_only |
| ASSISTments | `sources/datasets/assistments` | manual_access_or_metadata_only |
| CheggMate | `sources/datasets/cheggmate` | manual_access_or_metadata_only |
| ELLIPSE Corpus | `sources/datasets/ellipse_corpus` | manual_access_or_metadata_only |
| IntrEx | `sources/datasets/intrex` | manual_access_or_metadata_only |
| Junyi Academy | `sources/datasets/junyi_academy` | manual_access_or_metadata_only |
| KDD Cup 2010 | `sources/datasets/kdd_cup_2010` | manual_access_or_metadata_only |
| MLPdataset | `sources/datasets/mlpdataset` | manual_access_or_metadata_only |
| MOOCCube | `sources/datasets/mooccube` | manual_access_or_metadata_only |
| NuminaMath | `sources/datasets/numinamath` | manual_access_or_metadata_only |
| OmniEduBench | `sources/datasets/omniedubench` | manual_access_or_metadata_only |
| PEBBLE | `sources/datasets/pebble` | manual_access_or_metadata_only |
| Synthetic | `sources/datasets/synthetic` | manual_access_or_metadata_only |
| TIMSS Video Study | `sources/datasets/timss_video_study` | manual_access_or_metadata_only |
| 九章大模型 | `sources/datasets/九章大模型` | manual_access_or_metadata_only |
| 数字教育应用算法智能诊断公共数据集 | `sources/datasets/数字教育应用算法智能诊断公共数据集` | manual_access_or_metadata_only |
| 科大讯飞星火教育 | `sources/datasets/科大讯飞星火教育` | manual_access_or_metadata_only |
| 网易有道子曰 | `sources/datasets/网易有道子曰` | manual_access_or_metadata_only |
| EssayJudge | `sources/datasets/essayjudge` | paper_only_or_release_pending |

## 使用建议

- 优先下载 `huggingface_dataset` 和 `github_repository` 类型；Kaggle、Google Drive、机构页面和产品页通常需要人工确认条款。
- `sources/` 已在 `.gitignore` 中，不会把大数据集误提交到仓库。
- 只作为训练语料的数据集（如 FineWeb-Edu）不应直接当作评测结论；需要先定义任务、切分、指标和污染检查。
