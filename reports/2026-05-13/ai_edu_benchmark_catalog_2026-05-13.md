# AI-教育 Benchmark 信息目录

调研日期：2026-05-13  
目标文件：[todo.md](../../todo.md)  
关联框架：[ai_edu_unified_benchmark_framework_2026-05-13.md](./ai_edu_unified_benchmark_framework_2026-05-13.md)

## 说明

本文件聚焦“收集信息”，不是重新跑实验。它把当前仓库已整理的 78 个 AI-教育 benchmark / 数据资源统一到同一张目录表中，便于后续回答：

- 某个 AI 教育应用相似领域已有 benchmark 做过哪些评测。
- 这些 benchmark 测的问题是什么，落在哪些原子能力。
- 原生评测尺度/指标是什么。
- 是否已有公开模型结果，还是只是数据资源/任务协议。
- 数据入口和下载状态在哪里。

字段口径：

- “原子能力”沿用 [benchmark_metric_indicator_taxonomy_2026-05-12.md](../2026-05-12/benchmark_metric_indicator_taxonomy_2026-05-12.md) 的 D01-D24。
- “核心尺度”保留 benchmark 原生指标，不强行跨 benchmark 平均。
- “效果状态”区分“有公开模型结果”和“资源/任务协议；无统一榜单”。
- “数据状态”来自 [data/exhaustive_2026-05-13/dataset_acquisition_report.md](./data/exhaustive_2026-05-13/dataset_acquisition_report.md)，表示是否已有可执行下载入口；没有默认批量下载大数据集。

## 目录总表

| Benchmark / 资源 | 领域 | 原子能力 | 核心尺度 / 指标 | 效果状态 | 数据状态 | 数据/项目入口 |
|---|---|---|---|---|---|---|
| Adaptive Geography Practice | 教育资源/数据集 | D16 | no_unified_leaderboard | 资源/任务协议；无统一榜单 | manual_access_or_metadata_only | https://www.fi.muni.cz/adaptivelearning/?a=data |
| AGIEval | 标准化考试 | D01、D03 | AGIEval English、Few-shot、Few-shot CoT、Zero-shot、Zero-shot CoT | 有公开模型结果 | download_command_available_not_bulk_downloaded | https://github.com/ruixiangcui/AGIEval |
| Ape210K | 教育资源/数据集 | D04 | no_unified_leaderboard | 资源/任务协议；无统一榜单 | download_command_available_not_bulk_downloaded | https://github.com/Chenny0808/ape210k |
| APPS Dataset | 教育资源/数据集 | D08 | no_unified_leaderboard | 资源/任务协议；无统一榜单 | download_command_available_not_bulk_downloaded | https://github.com/hendrycks/apps |
| ARIC | 教育资源/数据集 | D07、D20 | no_unified_leaderboard | 资源/任务协议；无统一榜单 | manual_access_or_metadata_only | https://ivipclab.github.io/publication_ARIC/ARIC/ |
| ASAP-AES | 教育资源/数据集 | D10 | no_unified_leaderboard | 资源/任务协议；无统一榜单 | download_command_available_not_bulk_downloaded | https://www.kaggle.com/c/asap-aes/data |
| ASAP-SAS | 教育资源/数据集 | D11 | no_unified_leaderboard | 资源/任务协议；无统一榜单 | download_command_available_not_bulk_downloaded | https://www.kaggle.com/c/asap-sas/data |
| ASSISTments | 教育资源/数据集 | D15、D16、D17 | no_unified_leaderboard | 资源/任务协议；无统一榜单 | manual_access_or_metadata_only | https://sites.google.com/site/assistmentsdata/datasets |
| BigMath-Verified | 教育资源/数据集 | D05 | no_unified_leaderboard | 资源/任务协议；无统一榜单 | download_command_available_not_bulk_downloaded | https://huggingface.co/datasets/SynthLabsAI/Big-Math-RL-Verified |
| C-EVAL | 中文考试与学科知识 | D01、D02、D03 | CoT Avg、Five-shot Avg、Hard CoT、Hard Five、Hard Zero、Zero Avg、self-reported average | 有公开模型结果 | download_command_available_not_bulk_downloaded | https://github.com/hkust-nlp/ceval |
| ChartQA | 图表问答 | D06 | ChartQA-H、ChartQA-M、Overall | 有公开模型结果 | download_command_available_not_bulk_downloaded | https://github.com/vis-nlp/chartqa |
| CheggMate | 教育资源/数据集 | D24 | no_unified_leaderboard | 资源/任务协议；无统一榜单 | manual_access_or_metadata_only | https://www.chegg.com/cheggmate |
| Chinese Fineweb Edu | 教育资源/数据集 | D18 | no_unified_leaderboard | 资源/任务协议；无统一榜单 | download_command_available_not_bulk_downloaded | https://huggingface.co/datasets/opencsg/chinese-fineweb-edu |
| CMMLU | 中文通识与本土知识 | D01、D02 | Avg、China-specific、Humanities、Other、STEM、Social Sci.、five-shot average、zero-shot average | 有公开模型结果 | download_command_available_not_bulk_downloaded | https://github.com/haonan-li/CMMLU |
| CMMU | 中文多模态学科 | D06、D07 | Test Avg | 有公开模型结果 | download_command_available_not_bulk_downloaded | https://github.com/flageval-baai/CMMU |
| Codecademy Dataset | 教育资源/数据集 | D08、D09 | no_unified_leaderboard | 资源/任务协议；无统一榜单 | download_command_available_not_bulk_downloaded | https://github.com/Codecademy/datasets |
| ConvoLearn | 建构主义辅导对话 | D13、D19 | teacher human evaluation overall | 有公开模型结果 | download_command_available_not_bulk_downloaded | https://huggingface.co/datasets/masharma/convolearn |
| CS1QA | 教育资源/数据集 | D09 | no_unified_leaderboard | 资源/任务协议；无统一榜单 | download_command_available_not_bulk_downloaded | https://github.com/cyoon47/CS1QA/tree/main/data |
| EdNet | 教育资源/数据集 | D15、D16 | no_unified_leaderboard | 资源/任务协议；无统一榜单 | download_command_available_not_bulk_downloaded | https://github.com/riiid/ednet |
| EduBench | 教育场景生成 | D14、D15、D21 | Avg | 有公开模型结果 | download_command_available_not_bulk_downloaded | https://github.com/ybai-nlp/EduBench |
| EduDial | 教育资源/数据集 | D13、D19 | no_unified_leaderboard | 资源/任务协议；无统一榜单 | download_command_available_not_bulk_downloaded | https://github.com/Mind-Lab-ECNU/EduDial/tree/main |
| EduEval | 中文教育生成与知识 | D14、D15、D21 | Few-shot Avg、Zero-shot Avg | 有公开模型结果 | download_command_available_not_bulk_downloaded | https://github.com/Maerzs/E_edueval |
| EduGuard-Bench | 教育安全 | D21 | ASR、Acc、Incl、Omit、RFS | 有公开模型结果 | download_command_available_not_bulk_downloaded | https://github.com/YL1N/EduGuardBench |
| EduVisBench | 教学可视化 | D22 | Avg、Explan. Guidance、Interaction、Logical Seq.、Semantic Align.、Struct. Rich. | 有公开模型结果 | download_command_available_not_bulk_downloaded | https://huggingface.co/datasets/Haonian/EduVisBench/viewer |
| E-EVAL | 中文 K12 | D01、D02 | Five-shot AO、Five-shot CoT、Zero-shot | 有公开模型结果 | download_command_available_not_bulk_downloaded | https://github.com/AI-EDU-LAB/E-EVAL |
| ELLIPSE Corpus | 教育资源/数据集 | D10 | no_unified_leaderboard | 资源/任务协议；无统一榜单 | manual_access_or_metadata_only | https://www.kaggle.com/datasets/mpware/ellipse-corpus |
| EssayJudge | 作文自动评分 | D10 | AC、CH、EL、GA、LR、OE、OC、QWK、SV、WC | 有公开模型结果 | paper_only_or_release_pending | https://arxiv.org/abs/2502.11916 |
| FineWeb-Edu | 教育资源/数据集 | D18 | no_unified_leaderboard | 资源/任务协议；无统一榜单 | download_command_available_not_bulk_downloaded | https://huggingface.co/datasets/HuggingFaceFW/fineweb-edu |
| FoundationalAssist | 教育资源/数据集 | D15、D17 | no_unified_leaderboard | 资源/任务协议；无统一榜单 | download_command_available_not_bulk_downloaded | https://huggingface.co/datasets/ASSISTments/FoundationalASSIST/viewer |
| GaokaoBench | 中文高考 | D01、D02、D03 | Objective Overall、Subjective Overall、weighted average | 有公开模型结果 | download_command_available_not_bulk_downloaded | https://github.com/OpenLMLab/GAOKAO-Bench |
| Google Education Dialogue Dataset | 教育资源/数据集 | D19 | no_unified_leaderboard | 资源/任务协议；无统一榜单 | download_command_available_not_bulk_downloaded | https://github.com/google-research-datasets/Education-Dialogue-Dataset |
| GSM8K | 基础数学 | D04 | accuracy、代表结果 | 有公开模型结果 | download_command_available_not_bulk_downloaded | https://arxiv.org/abs/2110.14168 |
| HumanEval | 代码生成 | D08 | pass@1、pass@10、pass@100 | 有公开模型结果 | download_command_available_not_bulk_downloaded | https://github.com/openai/human-eval |
| IMO-ANSWER BENCH | 教育资源/数据集 | D05 | no_unified_leaderboard | 资源/任务协议；无统一榜单 | download_command_available_not_bulk_downloaded | https://huggingface.co/datasets/Hwilner/imo-answerbench |
| InnoSpark | 教育资源/数据集 | D24 | no_unified_leaderboard | 资源/任务协议；无统一榜单 | download_command_available_not_bulk_downloaded | https://github.com/sii-research/coclp.git |
| InteractScience | 交互式科学演示 | D23 | PFT Overall | 有公开模型结果 | download_command_available_not_bulk_downloaded | https://github.com/open-compass/InteractScience |
| IntrEx | 教育资源/数据集 | D20 | no_unified_leaderboard | 资源/任务协议；无统一榜单 | manual_access_or_metadata_only | https://huggingface.co/collections/XingweiT/intrex |
| Junyi Academy | 教育资源/数据集 | D16、D17 | no_unified_leaderboard | 资源/任务协议；无统一榜单 | manual_access_or_metadata_only | https://pslcdatashop.web.cmu.edu/DatasetInfo?datasetId=1198 |
| K12Vista | 中文 K12 多模态 | D02、D06 | Direct Overall、Step-by-Step Overall | 有公开模型结果 | download_command_available_not_bulk_downloaded | https://github.com/lichongod/K12Vista |
| KDD Cup 2010 | 教育资源/数据集 | D16 | no_unified_leaderboard | 资源/任务协议；无统一榜单 | manual_access_or_metadata_only | https://pslcdatashop.web.cmu.edu/KDDCup/downloads.jsp |
| LectureBank | 教育资源/数据集 | D07、D18 | no_unified_leaderboard | 资源/任务协议；无统一榜单 | download_command_available_not_bulk_downloaded | https://github.com/Yale-LILY/LectureBank |
| LeetCode Student Submissions | 教育资源/数据集 | D08、D09 | no_unified_leaderboard | 资源/任务协议；无统一榜单 | download_command_available_not_bulk_downloaded | https://huggingface.co/datasets/newfacade/LeetCodeDataset |
| MATH | 高阶数学 | D05 | Algebra、Avg、Count/Prob、Geometry、Intermed. Alg.、MATH、MATH(CoT)、Num. Theory、Prealg.、Precalc. | 有公开模型结果 | download_command_available_not_bulk_downloaded | https://github.com/hendrycks/math |
| Math23K | 教育资源/数据集 | D04 | no_unified_leaderboard | 资源/任务协议；无统一榜单 | download_command_available_not_bulk_downloaded | https://github.com/SCNU203/Math23k |
| MATH-500 | 高阶数学 | D05 | accuracy | 有公开模型结果 | download_command_available_not_bulk_downloaded | https://github.com/hendrycks/math |
| MathDial | 教育资源/数据集 | D12、D13 | no_unified_leaderboard | 资源/任务协议；无统一榜单 | download_command_available_not_bulk_downloaded | https://huggingface.co/datasets/eth-nlped/mathdial |
| MathTutorBench | 数学辅导 | D12、D13、D24 | Correction、Mistake location、Ped. IF、Ped. IF hard、Problem solving、Scaff. hard、Scaffolding、Socratic BLEU、Solution correctness | 有公开模型结果 | download_command_available_not_bulk_downloaded | https://github.com/eth-lre/mathtutorbench |
| MathVista | 多模态数学 | D06、D22 | ALL、private test ALL | 有公开模型结果 | download_command_available_not_bulk_downloaded | https://github.com/lupantech/MathVista |
| MBPP | 入门编程 | D08 | Problems solved、Samples solving task | 有公开模型结果 | download_command_available_not_bulk_downloaded | https://arxiv.org/abs/2108.07732 |
| ME2 | 几何视觉教学 | D06、D12、D22 | Explanation correctness、Fidelity、Reference、Visual Keypoint Overall | 有公开模型结果 | download_command_available_not_bulk_downloaded | https://huggingface.co/datasets/jungypark/ME2 |
| MLPdataset | 教育资源/数据集 | D18 | no_unified_leaderboard | 资源/任务协议；无统一榜单 | manual_access_or_metadata_only | https://github.com/mlpdataset |
| MMLU | 通用考试与学科知识 | D01、D03 | Avg、Humanities、MMLU、MMLU(CoT)、Other、STEM、Social Science、updated average | 有公开模型结果 | download_command_available_not_bulk_downloaded | https://arxiv.org/abs/2009.03300 |
| MOOCCube | 教育资源/数据集 | D15、D18 | no_unified_leaderboard | 资源/任务协议；无统一榜单 | manual_access_or_metadata_only | http://moocdata.cn/data/MOOCCube |
| NCTE Transcripts | 教育资源/数据集 | D19 | no_unified_leaderboard | 资源/任务协议；无统一榜单 | download_command_available_not_bulk_downloaded | https://github.com/ddemszky/classroom-transcript-analysis |
| NuminaMath | 教育资源/数据集 | D05 | no_unified_leaderboard | 资源/任务协议；无统一榜单 | manual_access_or_metadata_only | https://huggingface.co/collections/AI-MO/numinamath |
| OlymMATH | 奥赛数学 | D05 | Chinese HARD C@64、Chinese HARD P@1、English HARD C@64、English HARD P@1 | 有公开模型结果 | download_command_available_not_bulk_downloaded | https://github.com/RUCAIBox/OlymMATH |
| OlympiadBench | 奥赛数学与物理 | D05、D06 | Maths Avg、Overall、Physics Avg、full benchmark overall、text-only overall | 有公开模型结果 | download_command_available_not_bulk_downloaded | https://github.com/OpenBMB/OlympiadBench |
| OmniEduBench | 中文新课标教育 | D02、D03、D14 | Cultivation Avg、Knowledge Avg | 有公开模型结果 | manual_access_or_metadata_only | https://mind-lab-ecnu.github.io/OmniEduBench/ |
| PEBBLE | 多轮辅导过程评测 | D12、D13、D15 | no_unified_leaderboard | 资源/任务协议；无统一榜单 | manual_access_or_metadata_only | https://openreview.net/forum?id=ffvNvoJVgE |
| Pedagogy Benchmark | 教学法知识 | D14 | CDPK、SEND | 有公开模型结果 | download_command_available_not_bulk_downloaded | https://huggingface.co/datasets/AI-for-Education/pedagogy-benchmark |
| PTADisc | 教育资源/数据集 | D09、D17 | no_unified_leaderboard | 资源/任务协议；无统一榜单 | download_command_available_not_bulk_downloaded | https://github.com/wahr0411/PTADisc |
| QACP | 教育资源/数据集 | D09 | no_unified_leaderboard | 资源/任务协议；无统一榜单 | download_command_available_not_bulk_downloaded | https://github.com/NTAIX/Chinese-Python-QA-Dataset |
| SAS-Bench | 短答案评分 | D11 | CCS Avg、ECS Avg | 有公开模型结果 | download_command_available_not_bulk_downloaded | https://github.com/PKU-DAIR/SAS-Bench |
| SCB-Dataset | 教育资源/数据集 | D20 | no_unified_leaderboard | 资源/任务协议；无统一榜单 | download_command_available_not_bulk_downloaded | https://github.com/Whiffe/SCB-dataset |
| SciVideoBench | 科学视频 | D07 | Overall | 有公开模型结果 | download_command_available_not_bulk_downloaded | https://huggingface.co/datasets/groundmore/scivideobench |
| SIGHT | 教育资源/数据集 | D18、D19 | no_unified_leaderboard | 资源/任务协议；无统一榜单 | download_command_available_not_bulk_downloaded | https://github.com/rosewang2008/sight/tree/main/data |
| SocraticLM | 教育资源/数据集 | D13 | no_unified_leaderboard | 资源/任务协议；无统一榜单 | download_command_available_not_bulk_downloaded | https://github.com/Ljyustc/SocraticLM#socrateach-dataset |
| STATICS2011 | 教育资源/数据集 | D16 | no_unified_leaderboard | 资源/任务协议；无统一榜单 | download_command_available_not_bulk_downloaded | https://github.com/chrispiech/DeepKnowledgeTracing/tree/master/data/synthetic |
| Synthetic | 教育资源/数据集 | D16 | no_unified_leaderboard | 资源/任务协议；无统一榜单 | manual_access_or_metadata_only | https://pslcdatashop.web.cmu.edu/DatasetInfo?datasetId=507 |
| TalkMoves | 教育资源/数据集 | D19 | no_unified_leaderboard | 资源/任务协议；无统一榜单 | download_command_available_not_bulk_downloaded | https://github.com/SumnerLab/TalkMoves/tree/main/data |
| TIMSS Video Study | 教育资源/数据集 | D07、D19 | no_unified_leaderboard | 资源/任务协议；无统一榜单 | manual_access_or_metadata_only | https://www.timssvideo.com/transcripts |
| TutorBench | 真实辅导 | D13 | Multimodal、Overall、Text-only | 有公开模型结果 | download_command_available_not_bulk_downloaded | https://huggingface.co/datasets/ScaleAI/TutorBench |
| TutorialBank | 教育资源/数据集 | D18 | no_unified_leaderboard | 资源/任务协议；无统一榜单 | download_command_available_not_bulk_downloaded | https://github.com/Yale-LILY/TutorialBank |
| VisualEDU | 教育资源/数据集 | D22、D23 | no_unified_leaderboard | 资源/任务协议；无统一榜单 | download_command_available_not_bulk_downloaded | https://github.com/UchihaIchigo/VisualEDU |
| 九章大模型 | 教育资源/数据集 | D24 | no_unified_leaderboard | 资源/任务协议；无统一榜单 | manual_access_or_metadata_only | https://www.mathgpt.com/ |
| 数字教育应用算法智能诊断公共数据集 | 教育资源/数据集 | D17 | no_unified_leaderboard | 资源/任务协议；无统一榜单 | manual_access_or_metadata_only | https://www.nda.gov.cn/sjj/ywpd/szkjyjcss/0915/20250915162252254699971_pc.html |
| 科大讯飞星火教育 | 教育资源/数据集 | D24 | no_unified_leaderboard | 资源/任务协议；无统一榜单 | manual_access_or_metadata_only | https://xinghuo.xfyun.cn/education |
| 网易有道子曰 | 教育资源/数据集 | D24 | no_unified_leaderboard | 资源/任务协议；无统一榜单 | manual_access_or_metadata_only | https://aicenter.youdao.com/#/home |

## 如何使用这张表

1. 先在 [ai_edu_unified_benchmark_framework_2026-05-13.md](./ai_edu_unified_benchmark_framework_2026-05-13.md) 中定位应用场景。
2. 再回到本目录表，找到对应原子能力下有哪些 benchmark/资源。
3. 若“效果状态”为“有公开模型结果”，可用于已有模型表现对照。
4. 若“效果状态”为“资源/任务协议；无统一榜单”，它更适合构造评测任务，不应直接拿来比较模型。
5. 若“数据状态”为 `manual_access_or_metadata_only`，通常需要人工申请、同意条款或从项目页二次确认；不要默认批量下载。
