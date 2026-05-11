# 教育 Benchmark 与数据集调研报告

调研日期：2026-05-11  
输入清单：[edubench.md](./edubench.md)

资料缓存：本轮下载的论文 PDF、README/页面文本和抽取文本统一放在 `sources/` 下，且 `sources/` 已加入 `.gitignore`。主要目录包括 `sources/papers/`、`sources/text/`、`sources/pages/`、`sources/screenshots/`。报告正文只保留可读结论和模型结果，原始中间材料可在本仓库本地复核。

## 读法与口径

- 本报告沿用 `edubench.md` 的七大类结构。每个条目尽量回答三件事：评测过哪些模型或系统、代表性结果、暴露出的能力短板。
- 很多条目本质是训练/研究数据集或产品系统，不是带统一 leaderboard 的 benchmark。对这类条目，本报告明确标注“无统一模型榜单”，避免把数据资源误写成模型评测结果。
- 分数均来自论文、官方 README、数据卡或项目页；不同论文的 prompt、shot 数、评测脚本和时间不同，不建议跨基准直接横向相减。

## 核心结论

1. **解题类能力已经高度分层。** 通用考试类基准中 GPT-4/4o、Gemini、Qwen、DeepSeek 等前沿模型明显领先，但数学、物理、多模态题、开放式主观题仍是主要短板。中文 K12 场景中，Qwen、ERNIE、Spark 等中文模型在若干基准上可超过 GPT-4/ChatGPT。
2. **“会解题”不等于“会教学”。** MathTutorBench 显示，数学专用模型可以有较高 problem solving 分数，却在脚手架、苏格拉底式提问、纠错反馈上很弱。EduGuard-Bench 也显示教学角色扮演质量与安全性并不自动同步提升。
3. **多模态教育任务仍明显困难。** CMMU、OlympiadBench、MathVista、ME2、K12Vista、SciVideoBench、EduVisBench、InteractScience 都指向同一问题：模型经常能给出文字推理，却难以稳定理解图像、定位关键视觉元素、生成可解释的可视化或交互演示。
4. **自动评分类任务的真实难点在细粒度一致性。** ASAP-AES/ASAP-SAS 是经典数据集；EssayJudge 与 SAS-Bench 更进一步要求细粒度维度、分步评分和错误原因解释。SAS-Bench 中 DeepSeek-V3/DeepSeek-R1 代表性较强，但科学题、分步一致性和错误原因预测仍难。
5. **知识追踪与教育资源类条目多数不是 LLM 榜单。** ASSISTments、KDD Cup、EdNet、MOOCCube、课堂视频/转录等更适合评测 KT/CD/推荐/课堂分析模型；不能直接用来判断大模型“教育能力”，除非另设任务和评分协议。
6. **教育大模型系统公开可比性弱。** InnoSpark、九章、子曰、星火教育、CheggMate 等更多是产品或垂类模型入口，公开页面通常缺少统一 benchmark 分数。Google LearnLM 在 MathTutorBench 中有可引用结果，且表现接近或超过 GPT-4o 的若干教学维度。

## 一、解题能力评测 Benchmark

### 1. 通用学科评测

| 条目 | 评测模型与代表性结果 | 特殊发现 / 模型短板 | 来源 |
|---|---|---|---|
| MMLU | 原论文评测 Random、RoBERTa、ALBERT、GPT-2、UnifiedQA、GPT-3 系列。代表性平均分：Random 25.0，RoBERTa 27.9，GPT-2 32.4，UnifiedQA 48.9，GPT-3 XL 43.9。 | 当时所有模型距离专家水平很远；STEM、计算和程序性知识明显弱于陈述性知识；GPT-3 校准不稳。 | [arXiv:2009.03300](https://arxiv.org/abs/2009.03300), [HF](https://huggingface.co/datasets/cais/mmlu) |
| CMMLU | 原论文评测 GPT-4、ChatGPT、LLaMA/LLaMA2、BLOOMZ、Falcon、Baichuan 等；五-shot 中 GPT-4 平均约 70.95，ChatGPT 55.51，LLaMA2-70B 53.21。官方 README 的更新榜单中 Spark 4.0、Telechat2-35B、Lingzhi-72B、Qwen 系列已达到 85-91 左右。 | 中文本土知识、STEM、否定题和复杂选项对模型更难；CoT 并非总是提升，部分模型反而下降。 | [GitHub](https://github.com/haonan-li/CMMLU), [arXiv:2306.09212](https://arxiv.org/abs/2306.09212) |
| C-EVAL | 零样本平均：GPT-4 66.4，ChatGPT 51.0，Claude-v1.3 50.5，GLM-130B 44.0，ChatGLM-6B 38.9；五样本平均：GPT-4 68.7，ChatGPT 54.4，Claude-v1.3 54.2。 | C-Eval Hard 中 GPT-4 约 53-55，ChatGPT 约 37-41；复杂数学、物理、化学仍显著拉低表现。部分指令模型五-shot 不如 zero-shot。 | [GitHub](https://github.com/hkust-nlp/ceval), [arXiv:2305.08322](https://arxiv.org/abs/2305.08322) |
| AGIEval | 官方 v1.1 榜单：AGIEval-en few-shot 中 GPT-4o 71.4，Llama 3 400B+ 69.9，Llama 3 70B 63.0，GPT-3.5-Turbo 52.7；AGIEval-zh few-shot 中 GPT-4o 71.9，GPT-3.5-Turbo 49.5。 | 以高考、公考、SAT、LSAT 等人类考试衡量“考试型推理”；GPT-4o 与 GPT-3.5 差距大，中文子集对 GPT-3.5 更难。 | [GitHub](https://github.com/ruixiangcui/AGIEval), [arXiv:2304.06364](https://arxiv.org/abs/2304.06364) |
| GaokaoBench | 客观题总体：GPT-4-0314 72.2%，GPT-4-0613 71.6%，Gemini-Pro 57.9%，ERNIE-Bot 56.6%，GPT-3.5 53.2%。主观题总体：GPT-4-0314 51.9%，ERNIE-Bot 48.4%，GPT-3.5 35.8%。 | 折算高考总分时 GPT-4 领先，但所有模型文科强于理科；英语、生物相对好，数学、物理、化学和语文主观题弱。 | [GitHub](https://github.com/OpenLMLab/GAOKAO-Bench), [arXiv:2305.12474](https://arxiv.org/abs/2305.12474) |
| E-EVAL | 中文 K12：Qwen-72B 平均 88.8，ERNIE-Bot 4.0 平均 85.5，Yi-34B-chat 76.8，GPT-4 70.6，GPT-3.5 54.6，Qwen-7B 59.9。 | 中文 K12 中中文模型显著强于 GPT-4/ChatGPT；文科好于理科，复杂数学薄弱；few-shot 和 CoT 对部分强模型反而降低平均分。 | [GitHub](https://github.com/AI-EDU-LAB/E-EVAL), [arXiv:2401.15927](https://arxiv.org/abs/2401.15927) |
| OlympiadBench | 完整多模态榜单：GPT-4o 平均 25.89，GPT-4V 17.97，Qwen-VL-Max 10.09，Claude3-Opus 7.65，Gemini-Pro-Vision 4.22。文本子集：GPT-4o 39.72，GPT-4 29.93，DeepSeekMath-7B-RL 17.02。 | 奥赛级双语、多模态数学和物理极难；图片题、物理题、非英语题更难；闭源模型有优势但绝对分仍低。 | [GitHub](https://github.com/OpenBMB/OlympiadBench), [arXiv:2402.14008](https://arxiv.org/abs/2402.14008) |
| CMMU | GPT-4 评测填空题时，测试集平均：GPT-4V 30.91，Qwen-VL-Plus 27.73，Gemini-Pro 22.50，Intern-XComposer 18.42，Qwen-VL-Chat 12.14，LLaVA-1.5-13B 11.96。 | 中文多模态、多题型学科题对 MLLM 很难；填空/多选低于单选；数学、物理弱于政治、历史；高中题难于小学题。 | [GitHub](https://github.com/flageval-baai/CMMU), [arXiv:2401.14011](https://arxiv.org/abs/2401.14011) |
| ChartQA | 原论文评测 TaPas、VisionTaPas、T5、VL-T5；ChartQA 上 TaPas 41.28，VisionTaPas 45.52，VL-T5 41.56；用 PlotQA 预训练后 VL-T5 可到 51.84。 | 人写问题 ChartQA-H 明显更难；图表问答的瓶颈是视觉定位、表格/数值抽取、算术和多引用推理，不只是语言理解。 | [GitHub](https://github.com/vis-nlp/chartqa), [ACL Anthology](https://aclanthology.org/2022.findings-acl.177/) |

### 2. 数学解题专项

| 条目 | 评测模型与代表性结果 | 特殊发现 / 模型短板 | 来源 |
|---|---|---|---|
| GSM8K | OpenAI 原论文评测 GPT-3 系列生成器与 verifier；175B fine-tuned 约 33-34%，175B generator + verifier 在多样本重排下约 55%。 | 仅靠规模提升不足；算术错误、多步链式推理和中间步骤一致性是主要问题；verifier、采样重排和计算工具可显著帮助。 | [arXiv:2110.14168](https://arxiv.org/abs/2110.14168), [HF](https://huggingface.co/datasets/openai/gsm8k) |
| MATH | 原论文评测 GPT-2、GPT-3；GPT-2 1.5B 平均 6.9，GPT-3 13B few-shot 3.0，GPT-3 13B fine-tuned 5.6，GPT-3 175B few-shot 5.2；普通人约 40%，IMO 金牌水平约 90%。 | 竞赛级高中数学对早期 LLM 几乎不可解；难度等级越高接近 0；写出步骤的训练有帮助，但生成步骤本身并不保证正确。 | [GitHub](https://github.com/hendrycks/math), [arXiv:2103.03874](https://arxiv.org/abs/2103.03874) |
| Math23K | 主要是中文小学数学应用题数据集；官方仓库提供数据划分，不提供统一 LLM leaderboard。常被 seq2seq、tree decoder、graph solver、LLM 数学微调论文使用。 | 更适合训练/评测中文数学应用题求解器；问题在于答案模式较模板化，跨数据集泛化和真实教学反馈能力不能由该集单独证明。 | [GitHub](https://github.com/SCNU203/Math23k) |
| Ape210K | 官方仓库给出 210,488 道题、56,532 模板，train/valid/test 为 200,288/5,000/5,000；其 feature-rich copy-augmented seq2seq baseline 约 70% accuracy。 | 规模和模板数大，覆盖小学到初中；仍主要评测方程/答案生成，无法直接评估教学式解释或开放式推理。 | [GitHub](https://github.com/Chenny0808/ape210k) |
| NuminaMath | Hugging Face collection 主要是高阶数学训练语料/CoT 解题集合，不是单独的模型榜单。相关 NuminaMath 模型常用于奥赛、AIME、MATH 等下游评测。 | 更适合做数学模型微调和蒸馏；作为“benchmark”时需要另选测试集，否则存在训练集和评测集边界不清的问题。 | [HF Collection](https://huggingface.co/collections/AI-MO/numinamath) |
| IMO-ANSWER BENCH | 数据卡描述为 400 道 IMO/短名单/国家奥赛短答案题；数据卡本身不提供模型排行榜。 | 任务强调可验证短答案和非模板化奥赛推理；真正难点是从长证明搜索到稳定答案，而不是选择题模式识别。 | [HF Dataset](https://huggingface.co/datasets/Hwilner/imo-answerbench) |
| OlymMATH | 评测 DeepSeek-R1、o3-mini、Gemini 2.5 Pro、Qwen3、QwQ 等 28 个模型。英文 HARD 上 DeepSeek-R1 约 19.5%，o3-mini 31.2%，Gemini 2.5 Pro 58.4%；中文 HARD 上 DeepSeek-R1 15.9%，o3-mini 32.9%，Gemini 55.4%。 | 现有数学 benchmark 已有饱和趋势，OlymMATH-HARD 对前沿模型仍有区分度；Pass@64 远高于 Cons@64，说明模型会“偶尔猜对”但推理不稳定。 | [GitHub](https://github.com/RUCAIBox/OlymMATH), [arXiv:2503.21380](https://arxiv.org/abs/2503.21380) |
| MathVista | 官方榜单 testmini：OpenAI o1 73.9，Claude 3.5 Sonnet 67.7，GPT-4o 63.8，Gemini 1.5 Pro 63.9，GPT-4V 49.9；原论文中 GPT-4V 仍低于人类约 10.4 个点。 | 图形、图表、几何和数学文本混合；视觉感知、细粒度图形理解和组合推理是短板。最新模型已可超过原人类均值，但复杂视觉推理仍不稳。 | [GitHub](https://github.com/lupantech/MathVista), [arXiv:2310.02255](https://arxiv.org/abs/2310.02255) |
| BigMath-Verified | 主要是 RL 数学训练/验证数据集，含 250K+ 高质量可验证数学题；使用 Llama-3.1-8B 与 405B 等模型做难度和过滤估计。 | 不是公开 leaderboard。价值在于为 RL 提供可自动验证的数学题；多选、证明、开放式题被过滤，说明数据构造会影响模型学到的推理形态。 | [HF Dataset](https://huggingface.co/datasets/SynthLabsAI/Big-Math-RL-Verified), [arXiv:2502.17387](https://arxiv.org/abs/2502.17387) |
| ME / ME2 | 评测 Molmo、LLaVA-1.6、Qwen2-VL、Qwen2.5-VL、Math-PUMA、URSA、Math-LLaVA、GPT-4o、Gemini 2.0 Flash 等。视觉关键点识别中 Gemini 2.0 Flash overall 0.576，GPT-4o 0.472，Qwen2.5-VL-72B 0.536；讲解生成中 Gemini/GPT-4o 领先。 | 几何教学不只是算对，还要识别辅助线、关键点和图形关系。开源模型和数学专用模型在视觉关键点、忠实解释上明显不足。 | [HF Dataset](https://huggingface.co/datasets/jungypark/ME2), [arXiv:2504.03197](https://arxiv.org/abs/2504.03197) |

### 3. 代码能力专项

| 条目 | 评测模型与代表性结果 | 特殊发现 / 模型短板 | 来源 |
|---|---|---|---|
| HumanEval | Codex 论文评测 GPT-3、GPT-J、GPT-Neo、TabNine、Codex。Codex-12B pass@1 28.81，pass@10 46.81，pass@100 72.31；Codex-S pass@1 37.7，pass@100 77.5；GPT-3 在该设置下接近 0。 | 代码微调是关键；pass@k 强依赖采样；模型常在作用域、边界条件、测试覆盖和安全性上失败。 | [GitHub](https://github.com/openai/human-eval), [arXiv:2107.03374](https://arxiv.org/abs/2107.03374) |
| MBPP | 原论文评测大规模程序合成模型；137B few-shot 约 59%，fine-tuning 可提升约 10 个点；MathQA-Python fine-tuned 最大模型约 83.8。 | 入门级编程题更贴近教学；测试用例可引导模型，但运行时错误、需求理解偏差和边界条件仍常见。 | [arXiv:2108.07732](https://arxiv.org/abs/2108.07732), [HF](https://huggingface.co/datasets/Muennighoff/mbpp) |

## 二、教学能力评测 Benchmark

| 条目 | 评测模型与代表性结果 | 特殊发现 / 模型短板 | 来源 |
|---|---|---|---|
| Pedagogy Benchmark | 评测 97 个 LLM；CDPK 从 Llama-3.2-1B 的约 28% 到 Gemini 2.5 Pro 的约 89%，SEND 从约 29% 到 Gemini 2.5 Pro 的约 86%；DeepSeek-R1 等 reasoning 模型靠前。 | 教师职业知识和特殊教育能力并不等同于通用问答能力；reasoning 模型整体更好，但不同学科/教学场景差异明显。 | [HF](https://huggingface.co/datasets/AI-for-Education/pedagogy-benchmark), [arXiv:2506.18710](https://arxiv.org/abs/2506.18710) |
| MathTutorBench | 代表性结果：LearnLM-1.5-Pro problem solving 0.94、mistake location 0.57、correction 0.74；GPT-4o problem solving 0.90、correction 0.84；Qwen2.5-Math-7B problem solving 0.88，但 scaffolding win 0.06、pedagogy IF win 0.07。 | 数学专用模型会做题但不一定会辅导；苏格拉底式提问、个性化脚手架和定位学生错误是主要短板。 | [GitHub](https://github.com/eth-lre/mathtutorbench) |
| EduBench | 评测 DeepSeek-R1、GPT-4o、Qwen-Max、Qwen2.5-14B/7B 等。GPT-4o evaluator 下 DeepSeek-R1 平均约 9.06，Qwen-Max 约 8.99，Qwen2.5-14B/7B 约 8.87；蒸馏版 Qwen2.5-7B 可超过未蒸馏 7B 并接近更大模型。 | 教育场景维度包括作业批改、学习规划、心理健康、讲解等；高阶思维、情感互动和个性化更难。知识蒸馏对教育任务收益明显。 | [GitHub](https://github.com/ybai-nlp/EduBench) |
| EduEval | 中文教育基准：Spark-X1 官方汇总约 81.1，Qwen-plus 77.7，Qwen-72B 75.0，GPT-4o 71.0，Qwen-14B 68.1，Qwen-7B 60.8；few-shot 中多模型下降。 | 记忆类任务高于应用/创造类；few-shot 不一定有利，尤其开放生成和 GPT 评测下可能引入偏差。 | [GitHub](https://github.com/Maerzs/E_edueval) |
| OmniEduBench | 评测 11 个模型：GPT-4o、Gemini-2.5 Pro、Claude-4 Sonnet、Qwen3、QwQ、Seed-OSS、DeepSeek-V3.1、MuduoLLM 等。知识维度 Gemini-2.5 Pro 62.76 最高，QwQ 53.87 次高；培养维度 QwQ 70.27 最高，Claude-4 Sonnet 70.03，Gemini-2.5 Pro 69.14。 | 中文教育中“知识”与“育人/培养”分离评测。GPT-4o 在知识维度仅 24.17，显示对中文考试式教育题鲁棒性弱；HARD 子集即使最强模型也低于 50%。 | [Project](https://mind-lab-ecnu.github.io/OmniEduBench/), [arXiv:2510.26422](https://arxiv.org/abs/2510.26422), [OpenReview](https://openreview.net/forum?id=IeJ9ABgf3k) |
| EduGuard-Bench | 评测 14 个模型；RFS 中 Claude-3.7 0.77、DeepSeek-V3 0.73、GPT-4o 0.69、Qwen2.5-72B 0.56。图 6 的 ASR 排序中 Claude-3.7 27.0 最低，DeepSeek-V3 81.6 最高；论文正文另有一句称 Qwen2.5-72B 为 17.2，和图表数值 56.2 不一致。 | reasoning 模型角色扮演更好，但安全不一定更好；主要失败模式是“教学无能”而非单纯拒答；存在中等规模模型更脆弱的 scaling paradox。 | [GitHub](https://github.com/YL1N/EduGuardBench), [arXiv:2511.06890](https://arxiv.org/abs/2511.06890) |
| TutorBench | 论文表 1 评测 Gemini 2.5 Pro、GPT-5、o3、Claude Opus/Sonnet、Llama 4 Maverick、GPT-4o 等；Gemini 2.5 Pro overall 55.65，GPT-5 55.33，GPT-4o 36.12。 | 重点是辅导能力而不是单题答案；多模态作业反馈普遍低于文本场景，所有前沿模型 overall 仍低于 56%。 | [HF](https://huggingface.co/datasets/ScaleAI/TutorBench), [arXiv:2510.02663](https://www.arxiv.org/abs/2510.02663) |
| EduVisBench | 评测 Flux.1-dev、SD3.5、SDXL、Deepseek-VL2、GLM-4V、MiniCPM-V、Mistral-Small、Phi、Qwen2.5-VL-72B、GPT-4o、Claude 3.7 Sonnet、Gemini 2.0 Flash、v0、EduVisAgent。平均分：v0 58.2，Claude 3.7 Sonnet Webpage 54.6，Gemini 2.0 Flash 43.6，GPT-4o Webpage 38.1；EduVisAgent 81.6，相对 v0 提升 40.2%。 | 现有模型常能写文字解法，却不能把推理拆成符合认知过程的可视化。网页形式通常优于 SVG；专门的多智能体教学可视化流程明显更强。 | [HF](https://huggingface.co/datasets/Haonian/EduVisBench/viewer), [arXiv:2505.16832](https://arxiv.org/abs/2505.16832), [OpenReview](https://openreview.net/forum?id=FVCpV04ZRe) |
| SciVideoBench | 榜单：Gemini-2.5-Pro overall 64.30，Gemini-2.5-Flash 46.40，Gemini-1.5-Pro 27.50，Gemini-2.0-Flash 25.70，GPT-4o 24.90。Gemini-2.5-Pro 的 Quantitative 50.61，低于 Conceptual 69.73 和 Hypothetical 67.79。 | 长时序科学视频理解、实验过程推理、字幕/图像/音频对齐难；定量推理是明显短板。 | [HF](https://huggingface.co/datasets/groundmore/scivideobench) |
| K12Vista | 33K 中文 K12 多模态题；论文表 7 评测 Gemini2-thinking、Qwen2.5-VL、QVQ、InternVL2.5、GPT-4o、LLaVA-OneVision 等 26 个 MLLM。Direct overall：Gemini2-thinking 55.47、Qwen2.5-VL-32B 55.42、GPT-4o 35.02。 | Step-by-Step overall 通常低于 Direct，仅 Gemini2-thinking 从 55.47 升至 57.36；过程正确性暴露步骤跳跃、幻觉、逻辑矛盾和图文误解。 | [GitHub](https://github.com/lichongod/K12Vista), [arXiv:2506.01676](https://arxiv.org/abs/2506.01676) |
| InteractScience | 评测 GPT-5、GPT-4.1、GPT-4o、Gemini-2.5-Pro、Claude Sonnet/Opus、Qwen3、Qwen2.5-VL 等生成交互式 HTML。PFT overall：Claude-Sonnet-4 41.47，GPT-5 39.47，Claude-Opus-4 40.27，GPT-4o 28.27；开源 Qwen3-235B-A22B 33.33，Qwen2.5-VL-72B 23.73。 | 生成科学交互演示仍很难，最佳功能正确性也只有四成左右；动作/视觉可较好，真正的功能完整性和 perfect rate 低。 | [GitHub](https://github.com/open-compass/InteractScience) |

## 三、知识追踪领域

| 条目 | 评测模型与代表性结果 | 特殊发现 / 模型短板 | 来源 |
|---|---|---|---|
| ASSISTments 系列 | 经典 KT 数据集，常用于 BKT、DKT、DKVMN、SAKT、AKT、SAINT、NCD 等模型，以 AUC/ACC/RMSE 比较；官方数据页本身不是统一 LLM leaderboard。 | 不同年份字段差异大；知识点标签、缺失值、切分方式会显著影响结果。旧版本缺少题干文本，限制了大模型直接利用。 | [Official](https://sites.google.com/site/assistmentsdata/datasets) |
| KDD Cup 2010 | 竞赛围绕 Algebra I 与 Bridge to Algebra 学生交互日志；传统参赛系统多用特征工程、IRT/BKT、矩阵分解、逻辑回归和集成模型。 | 是大规模学生建模经典基准，但结果依赖竞赛特征和平台日志；不能直接说明教学对话能力。 | [PSLC DataShop](https://pslcdatashop.web.cmu.edu/KDDCup/downloads.jsp) |
| EdNet | 131M+ 交互、784K+ 学生；常用于 DKT、SAKT、AKT、SAINT、Transformer KT 等序列模型。官方仓库主要发布数据，不给单一权威榜单。 | 极大规模带来长序列建模优势；行为维度从答题扩展到学习活动，但缺少完整教学语境和开放答案解释。 | [GitHub](https://github.com/riiid/ednet) |
| Junyi Academy | 台湾均一教育平台 K12 数学数据；常用于 BKT、DKT、IRT、知识点图谱/层级模型。 | 中文/繁中数学平台数据价值高，但练习推荐和重复作答会带来强平台策略偏置。 | [PSLC DataShop](https://pslcdatashop.web.cmu.edu/DatasetInfo?datasetId=1198) |
| FoundationalAssist | 约 5,000 学生、170 万交互，保留题目文本、学生实际作答和错误选项；数据卡未提供模型榜单。 | 相比旧 KT 数据更适合 foundation model 做文本级诊断；但仍需要统一任务定义和隐私/课程切分规范。 | [HF](https://huggingface.co/datasets/ASSISTments/FoundationalASSIST/viewer) |
| 数字教育应用算法智能诊断公共数据集 | 公共教育算法数据集入口，覆盖教学诊断、学情预警、认知发展等；官方页面不提供统一模型榜单。 | 适合构建国产教育算法评测，但需要明确公开任务、指标、训练/测试切分后才可比较模型。 | [NDA](https://www.nda.gov.cn/sjj/ywpd/szkjyjcss/0915/20250915162252254699971_pc.html) |
| PTADisc | 面向 PTA 编程/课程学习的超大规模数据，覆盖 74 门课程、4054 概念、225K 问题、6.8 亿作答记录；常用于认知诊断、KT、课程分析。 | 数据规模极大，可检验概念诊断与程序学习行为；难点是跨课、跨题型迁移和概念标签质量。 | [GitHub](https://github.com/wahr0411/PTADisc) |
| STATICS2011 | CMU OLI 统计课程数据，常作为 DKT 仓库中的经典真实数据集；用于 BKT/DKT 等 KT 模型对比。 | 学生数和题量相对小，适合方法验证但不适合评估大模型教育能力。 | [DKT Data](https://github.com/chrispiech/DeepKnowledgeTracing/tree/master/data/synthetic) |
| Synthetic | 约 4K 虚拟学生、50 个问题的合成数据，用于验证 KT 模型在已知生成结构下的行为。 | 优点是结构可控，缺点是与真实学习行为差距大；模型在合成数据好不代表真实课堂有效。 | [PSLC DataShop](https://pslcdatashop.web.cmu.edu/DatasetInfo?datasetId=507) |
| Adaptive Geography Practice | 大规模地理自适应练习日志，约 90K 学习者；常用于自适应练习、知识状态估计和推荐算法。 | 领域是地理知识，不是通用 K12；评测重点偏学习路径与答题预测，不是开放式教学能力。 | [Official](https://www.fi.muni.cz/adaptivelearning/?a=data) |

## 四、自动评分领域

| 条目 | 评测模型与代表性结果 | 特殊发现 / 模型短板 | 来源 |
|---|---|---|---|
| ASAP-AES | Kaggle 经典英文作文评分竞赛数据，评价指标主要是 QWK；后续常见模型包括 EASE、LSTM/CNN、BERT/DeBERTa、LLM-as-a-rater 等。官方数据页不是 LLM 论文榜单。 | 作文评分容易受长度、提示主题、年级和写作模板影响；跨 prompt 泛化与公平性是长期问题。 | [Kaggle](https://www.kaggle.com/c/asap-aes/data) |
| ASAP-SAS | Kaggle 短答案评分数据，覆盖科学、历史等；传统评测模型包括特征工程、SVM/回归、神经匹配、BERT/LLM 评分。官方数据页不是统一 LLM 榜单。 | 短答案比作文更依赖参考答案、关键词和领域知识；同义表达、部分正确、遗漏步骤容易误判。 | [Kaggle](https://www.kaggle.com/c/asap-sas/data) |
| ELLIPSE Corpus | 9,000+ 英语学习者作文，含多维写作能力标注；Kaggle 数据页本身不提供统一模型 leaderboard。 | 更适合评估二语写作诊断和多维反馈；难点在于词汇、句法、篇章连贯等维度并不完全独立。 | [Kaggle](https://www.kaggle.com/datasets/mpware/ellipse-corpus) |
| EssayJudge | 评测 Yi-VL、Qwen2-VL、DeepSeek-VL、Qwen-Max、Step-1V、Gemini-1.5、Claude-3.5、GPT-4o-mini、GPT-4o 等；指标为 QWK。GPT-4o 总体最强，闭源 MLLM 普遍强于开源。 | 图像/手写/版面信息能提升多维作文评分；Argument Clarity 等高层维度仍难，开源模型倾向保守或低分。 | [arXiv:2502.11916](https://arxiv.org/abs/2502.11916) |
| SAS-Bench | 评测 16 个 LLM，包括 DeepSeek-R1/V3、QwQ-32B、Qwen3-32B/8B、Qwen2.5、LLaMA3、Mixtral、GLM4、GPT-4o-mini 等；CCS 中 DeepSeek-V3 平均最好，QWK 中 DeepSeek-R1 最好，ECS 中 DeepSeek-R1 平均最高。 | 分步评分一致性比总体分更难；科学题显著困难；few-shot 通常有帮助，但可能提升总分一致性同时误导步骤一致性；缺少评分细则会普遍降分。 | [GitHub](https://github.com/PKU-DAIR/SAS-Bench), [arXiv:2505.07247](https://arxiv.org/abs/2505.07247) |

## 五、教育问答领域

| 条目 | 评测模型与代表性结果 | 特殊发现 / 模型短板 | 来源 |
|---|---|---|---|
| MathDial | 数据卡强调当前模型会做数学题但不会教；包含学生错误解、学生画像、教师标注困惑、自我纠正等。数据卡未给统一模型榜单。 | 关键任务是围绕学生误解进行苏格拉底式引导，而不是直接给答案。 | [HF](https://huggingface.co/datasets/eth-nlped/mathdial), [arXiv:2305.14536](https://arxiv.org/abs/2305.14536) |
| Google Education Dialogue Dataset | 由 Gemini Ultra 生成 40,000 训练 + 7,234 测试多轮师生对话；用于 Multi-turn RL from Preference Human Feedback 实验。 | 是合成对话资源，不是直接的模型排行榜；优势是规模和偏好元数据，风险是合成分布与真实课堂差距。 | [GitHub](https://github.com/google-research-datasets/Education-Dialogue-Dataset), [arXiv:2405.14655](https://arxiv.org/abs/2405.14655) |
| EduDial | 官方 README 当前仅显示 “code come soon”；清单描述其为 K12 数学教学大纲与策略驱动的 34,250 多轮对话。 | 目前公开入口不足以支持模型结果结论；可作为后续教学对话仿真数据关注。 | [GitHub](https://github.com/Mind-Lab-ECNU/EduDial/tree/main) |
| IntrEx | Hugging Face collection 入口定位为学生兴趣度/参与度教育对话标注数据；公开入口未提供可抓取的统一榜单。 | 价值在于建模学生 engagement；需要与对话质量、学习增益和长期留存结合评估。 | [HF Collection](https://huggingface.co/collections/XingweiT/intrex) |
| Bridge | 700 条真实数学错题辅导对话，带专家 tutor 决策标注；论文报告 GPT-4 回复加入专家决策后偏好率提升 76%，随机决策会使质量下降 97%。 | 教学回复质量高度依赖“下一步教学决策”；大模型语言能力强，但若决策错误，回复会明显变差。 | [GitHub](https://github.com/rosewang2008/bridge#dataset) |
| SocraticLM | SocraTeach 含 35K 多轮、22K 单轮教学对话；实现基于 Qwen2.5-Math-7B-Instruct 的增强训练/评测流程。 | 目标是苏格拉底式教学而非答案生成；公开 README 更偏数据和训练脚本，未提供完整跨模型榜单。 | [GitHub](https://github.com/Ljyustc/SocraticLM#socrateach-dataset) |
| QACP | 中文 Python 问答数据集，清单给出 10,960 个高质量问题；官方入口没有可用统一模型榜单。 | 适合评测编程教育问答、概念解释和代码错误定位；需要另行定义检索式 QA、生成式 QA 或 tutor 任务。 | [GitHub](https://github.com/NTAIX/Chinese-Python-QA-Dataset) |
| CS1QA | NAACL 2022 编程入门课程代码问答数据，包含 9,237 个 QA 对、学生代码、问题类型和相关代码行；仓库提示未标注大规模原始数据需邮件申请。 | 更接近真实 CS1 学生求助；挑战是把自然语言问题、代码上下文和错误行联合理解。 | [GitHub](https://github.com/cyoon47/CS1QA/tree/main/data) |

## 六、其他教育资源

| 条目 | 类型与可用评测对象 | 特殊发现 / 模型短板 | 来源 |
|---|---|---|---|
| FineWeb-Edu | 高质量教育预训练语料，不是 benchmark；用于训练/筛选教育文本和训练语言模型。 | 价值在于语料质量和教育密度；不能单独证明模型教学能力。 | [HF](https://huggingface.co/datasets/HuggingFaceFW/fineweb-edu) |
| Chinese Fineweb Edu | 中文教育预训练语料，不是 benchmark。 | 适合中文教育模型预训练/继续预训练；仍需下游 benchmark 验证。 | [HF](https://huggingface.co/datasets/opencsg/chinese-fineweb-edu) |
| IM2LATEX-100K | 公式图片到 LaTeX 的 OCR/序列生成数据集；常用于 CNN-RNN/Transformer 公式识别模型。 | 教育场景的公式识别基础能力，短板通常在复杂排版、手写噪声和符号细节。 | [arXiv:1609.04938](https://arxiv.org/abs/1609.04938) |
| LectureBank | 大学课程视频、音频、PPT、板书、字幕等资源；可评测课程理解、字幕、摘要、知识点抽取。 | 多模态课程资源丰富，但任务定义分散，缺少统一大模型榜单。 | [GitHub](https://github.com/Yale-LILY/LectureBank) |
| SCB-Dataset | 智慧教室学生行为视频数据；可评测行为识别、课堂参与度检测。 | 不是语言模型 benchmark；挑战在真实教室遮挡、多学生动作和标注一致性。 | [GitHub](https://github.com/Whiffe/SCB-dataset) |
| NCTE Transcripts | 约 1,660 节小学数学课转录文本；可用于课堂话语、教师提问、反馈策略分析。 | 适合 NLP 课堂分析，不直接评估解题能力；跨教师/学校迁移是难点。 | [GitHub](https://github.com/ddemszky/classroom-transcript-analysis) |
| ARIC | 多视角 4K 真实课堂监控，含图像、音频、文本三模态和师生行为标注。 | 对多模态课堂行为识别有价值；隐私、视角、遮挡和音视频同步是主要挑战。 | [Project](https://ivipclab.github.io/publication_ARIC/ARIC/) |
| TalkMoves | 567 篇人工注释 K12 数学课堂转录，标注 talk moves。 | 适合评测教师话语动作识别；大模型容易混淆相近教学意图。 | [GitHub](https://github.com/SumnerLab/TalkMoves/tree/main/data) |
| TIMSS Video Study | 1,000+ 八年级数学/科学课堂视频与转录，覆盖 7 个国家。 | 适合跨文化课堂分析；视频年代、课程制度和语言差异会影响泛化。 | [Official](https://www.timssvideo.com/transcripts) |
| SIGHT | MIT 数学公开课 288 个讲座转录和 15,784 条学生评论。 | 可用于讲座理解、学生反馈建模、知识点抽取；不是模型排行榜。 | [GitHub](https://github.com/rosewang2008/sight/tree/main/data) |
| VisualEDU | 数学解题可视化讲解生成系统与数据，基于 LLM 和 Manim。 | 与 EduVisBench 类似，真正难点是让动画严格对应解题步骤，而非生成装饰性图形。 | [GitHub](https://github.com/Uchihalchigo/VisualEDU) |
| MLPdataset | 大学课程幻灯片、180+ 小时讲解视频、讲师课程数据。 | 适合课程视频理解、幻灯片-讲解对齐、讲座摘要；无统一榜单。 | [GitHub](https://github.com/mlpdataset) |
| MOOCCube | ACL 2020 MOOC 数据，含课程、视频、概念图谱、用户选课和观看行为。 | 适合课程推荐、概念图谱、学习路径建模；模型评测常在推荐/KT 指标上，不等同于 LLM 教学能力。 | [Official](http://moocdata.cn/data/MOOCCube) |
| TutorialBank | ACL 2018 教程资源库，20,243 个资源及 URL、元数据、主题标注。 | 适合教育资源检索、分类和推荐；网页失效和主题层级噪声是主要问题。 | [GitHub](https://github.com/Yale-LILY/TutorialBank) |
| Codecademy Dataset | 编程学习者代码提交、学习轨迹和错误记录。 | 适合编程学习分析和个性化反馈；公开数据规模/字段与真实平台闭源数据相比有限。 | [GitHub](https://github.com/Codecademy/datasets) |
| LeetCode Student Submissions | LeetCode 题目、提交代码、运行结果、性能信息数据集。 | 适合代码生成/纠错/学习者行为分析；要注意题目泄漏和刷题数据与课堂编程的差异。 | [HF](https://huggingface.co/datasets/newfacade/LeetCodeDataset) |
| APPS Dataset | 5,000 道算法编程题、测试用例和大量提交；常用于评测程序合成模型，如 GPT/Code 模型、Codex、CodeGen 等。 | 比 HumanEval 更长、更接近竞赛编程；长程算法设计、输入输出格式和隐藏测试是主要失败点。 | [GitHub](https://github.com/hendrycks/apps) |

## 七、教育大模型系统

| 系统 | 公开评测与结果 | 特殊发现 / 模型短板 | 来源 |
|---|---|---|---|
| InnoSpark | 公开入口包含模型/项目集合与教育应用站点；未见统一公开 benchmark 表。 | 更适合作为教育垂类系统候选，被 E-EVAL、EduEval、OmniEduBench 等外部基准系统评估。 | [GitHub](https://github.com/sii-research/coclp.git), [HF Collection](https://huggingface.co/collections/sii-research/innospark-687c9533a8ca0fb33ef57e5a), [Site](https://beta.aiecnu.cn) |
| 学而思九章大模型 | 公开页面定位数学教育垂类模型；未见可复现公开 benchmark 表。 | 应用重点是分步讲题、引导式解题、错题诊断；需要在 MathTutorBench、OlymMATH、ME2 等外部基准验证。 | [Official](https://www.mathgpt.com/) |
| 网易有道子曰大模型 | 公开页面定位全学科教育大模型；未见统一公开 benchmark 表。 | 产品能力覆盖讲题、作文批改、口语陪练、教案生成；跨任务评测需用 EduEval、EssayJudge、ASAP、口语测评集等组合。 | [Official](https://aicenter.youdao.com/#/home) |
| 科大讯飞星火教育大模型 | 公开页面定位星火教育版，覆盖学情诊断、备课、分层作业、口语测评、AI 实验。 | 需要区分底座通用能力、教育内容安全、课堂工作流集成；公开页面不等于可复现评测。 | [Official](https://xinghuo.xfyun.cn/education) |
| CheggMate | Chegg 与 OpenAI 合作的学习辅导系统；公开产品页不提供统一模型 benchmark。 | 依赖 Chegg 题库和平台资源，优势可能在资源检索和流程体验；外部不可复现性强。 | [Official](https://www.chegg.com/cheggmate) |
| Google LearnLM | 在 MathTutorBench 中 LearnLM-1.5-Pro problem solving 0.94、solution correctness 0.75、mistake location 0.57、correction 0.74，整体教学维度强于多数通用模型。 | LearnLM 是少数在公开教学能力 benchmark 中可引用的教育模型；仍需检验中文、本地课程、长期学习增益和安全性。 | [Google Cloud](https://cloud.google.com/solutions/learnlm), [MathTutorBench](https://github.com/eth-lre/mathtutorbench) |

## 模型级明细附录

本附录按“有官方模型评测结果的 benchmark”优先列出逐模型结果。若条目是数据集、预训练语料、产品页或资源库，且论文/README 没有统一 leaderboard，则明确写成“无官方统一榜单”。分数不跨 benchmark 直接比较。

### A. 通用考试与学科知识

**MMLU 原论文结果**

| Model | Humanities | Social Science | STEM | Other | Avg |
|---|---:|---:|---:|---:|---:|
| Random | 25.0 | 25.0 | 25.0 | 25.0 | 25.0 |
| RoBERTa | 27.9 | 28.8 | 27.0 | 27.7 | 27.9 |
| ALBERT | 27.2 | 25.7 | 27.7 | 27.9 | 27.1 |
| GPT-2 | 32.8 | 33.3 | 30.2 | 33.1 | 32.4 |
| UnifiedQA | 45.6 | 56.6 | 40.2 | 54.6 | 48.9 |
| GPT-3 Small few-shot | 24.4 | 30.9 | 26.0 | 24.1 | 25.9 |
| GPT-3 Medium few-shot | 26.1 | 21.6 | 25.6 | 25.5 | 24.9 |
| GPT-3 Large few-shot | 27.1 | 25.6 | 24.3 | 26.5 | 26.0 |
| GPT-3 X-Large few-shot | 40.8 | 50.4 | 36.7 | 48.8 | 43.9 |

主要失败维度：STEM 和计算型题低于社科/其他类；程序性知识和校准能力弱；所有模型距专家水平很远。

**CMMLU 五样本结果**

| Model | Type | STEM | Humanities | Social Sci. | Other | China-specific | Avg |
|---|---|---:|---:|---:|---:|---:|---:|
| GPT-4 | Chat | 65.23 | 72.11 | 72.06 | 74.79 | 66.12 | 70.95 |
| ChatGPT | Chat | 47.81 | 55.68 | 56.50 | 62.66 | 50.69 | 55.51 |
| LLaMA2-70B | Base | 44.11 | 57.05 | 55.63 | 56.65 | 48.01 | 53.21 |
| Falcon-40B | Base | 33.33 | 43.46 | 44.28 | 44.75 | 39.46 | 41.45 |
| LLaMA-65B | Base | 34.47 | 40.24 | 41.55 | 42.88 | 37.00 | 39.80 |
| LLaMA2-13B | Base | 33.04 | 39.73 | 38.45 | 42.54 | 35.67 | 38.24 |
| BLOOMZ-7B | Chat | 30.56 | 39.10 | 38.59 | 40.32 | 37.15 | 37.04 |
| LLaMA-30B | Base | 29.69 | 33.68 | 34.08 | 37.40 | 30.68 | 33.63 |
| LLaMA2-7B | Base | 30.03 | 34.76 | 33.72 | 33.62 | 30.12 | 32.96 |
| ZHLLaMA-13B | Chat | 27.12 | 33.18 | 34.87 | 35.10 | 32.97 | 32.63 |
| BXLLaMA-13B | Chat | 27.50 | 32.47 | 32.33 | 35.77 | 31.64 | 31.90 |
| LLaMA-13B | Base | 29.21 | 30.96 | 31.74 | 33.07 | 30.86 | 31.24 |
| Baichuan2-13B | Base | 48.36 | 67.44 | 66.40 | 65.94 | 63.48 | 61.92 |
| Baichuan-13B | Base | 42.38 | 61.61 | 60.44 | 59.26 | 56.62 | 55.82 |
| InternLM-20B | Chat | 42.70 | 60.51 | 58.00 | 57.62 | 54.72 | 54.52 |
| Xverse-13B | Chat | 41.65 | 55.72 | 57.47 | 57.32 | 52.32 | 53.08 |
| InternLM-7B | Base | 41.71 | 54.43 | 56.42 | 55.38 | 53.11 | 52.07 |
| ChatGLM2-6B | Chat | 42.65 | 50.88 | 51.22 | 50.72 | 48.66 | 48.87 |
| BatGPT-15B | Chat | 41.68 | 50.14 | 50.78 | 48.68 | 46.93 | 47.88 |
| Baichuan-7B | Base | 35.25 | 48.07 | 47.88 | 46.61 | 44.14 | 44.43 |
| ChatGLM-6B | Chat | 32.35 | 39.22 | 39.65 | 38.62 | 37.70 | 37.48 |

主要失败维度：STEM 仍最弱；中国本土知识会拉开通用英文模型与中文模型差距；CoT 在 CMMLU 中不是稳定增益。

**C-EVAL 全量与 Hard 子集**

| Model | Zero Avg | Five-shot Avg | CoT Avg | Hard Zero | Hard Five | Hard CoT |
|---|---:|---:|---:|---:|---:|---:|
| GPT-4 | 66.4 | 68.7 | 68.3 | 53.3 | 54.9 | 56.8 |
| ChatGPT | 51.0 | 54.4 | 50.0 | 36.7 | 41.4 | 35.0 |
| Claude-v1.3 | 50.5 | 54.2 | 54.2 | 37.6 | 39.0 | 39.2 |
| Claude-instant-v1.0 | 40.6 | 45.9 | 44.5 | 32.1 | 35.5 | 33.4 |
| Bloomz-mt | 44.3 | 39.0 | - | 30.8 | 30.4 | - |
| GLM-130B | 44.0 | 40.3 | 28.8 | 30.7 | 30.3 | 22.6 |
| LLaMA-65B | 34.7 | 38.8 | 30.3 | 29.8 | 31.7 | 21.4 |
| ChatGLM-6B | 38.9 | 34.5 | 34.5 | 29.2 | 23.1 | 26.1 |
| MOSS | 33.1 | 31.1 | 31.2 | 28.4 | 24.0 | 21.6 |
| Chinese-LLaMA-13B | 29.6 | 33.3 | 25.4 | 27.5 | 27.3 | 15.4 |
| Chinese-Alpaca-13B | 30.9 | 26.7 | - | 24.4 | 27.1 | - |

主要失败维度：Hard 子集对所有模型都明显更难；多模型 five-shot 下降，说明示例会引入格式/分布干扰；CoT 对中文考试题并非默认有效。

**AGIEval 平均结果**

| Model | Zero-shot | Zero-shot CoT | Few-shot | Few-shot CoT |
|---|---:|---:|---:|---:|
| Human avg | 67.0 | - | - | - |
| Human top | 91.0 | - | - | - |
| text-davinci-003 | 38.1 | 37.4 | 41.2 | 40.4 |
| ChatGPT | 42.9 | 43.2 | 44.4 | 45.0 |
| GPT-4 | 56.4 | 58.4 | 59.2 | 61.3 |
| Vicuna-13B | 无平均值表；任务分数极低，例如 MATH 6.8/6.6、GK-Math-Cloze 2.5/1.7 | - | - | - |

主要失败维度：标准化考试里的数学、物理、法律推理和无材料阅读题拉低表现；GPT-4 距人类 top 仍有大差距。

**GaokaoBench 总体结果**

| Model | Objective Overall | Subjective Overall | 典型弱项 |
|---|---:|---:|---|
| LLaMA-7B | 21.1 | - | 物理 0.0，中文/英语低 |
| Vicuna-7B | 21.0 | - | 语文 12.0，物理 7.0 |
| Baichuan2-7B-Base | 27.2 | - | 物理 0.0 |
| Baichuan2-7B-Chat | 40.5 | - | 数学、物理、化学 |
| Baichuan2-13B-Chat | 43.9 | - | 数学、物理 |
| ChatGLM-6B | 30.8 | - | 英语、物理、生物 |
| ChatGLM2-6B | 42.7 | - | 数学、物理 |
| GPT-4-0613 | 71.6 | 50.8 | 主观数学 24.6/27.5，化学 28.5 |
| GPT-4-0314 | 72.2 | 51.9 | 主观数学 24.1/27.9 |
| GPT-3.5-turbo-0301 | 53.2 | 35.8 | 主观数学 15.2/15.9，物理 16.9 |
| ERNIE-Bot-0615 | 56.6 | 48.4 | 主观数学 17.0/25.6 |
| ERNIE-Bot-turbo-0725 | 45.6 | 39.2 | 主观数学 14.6/15.6 |

主要失败维度：主观理科题尤其数学、物理、化学明显困难；英语和生物相对容易；国内中文模型在部分文科/生物题上接近或超过 GPT 系列。

**E-EVAL Prompt 设置对比**

| Model | Zero-shot | Five-shot AO | Five-shot CoT |
|---|---:|---:|---:|
| Qwen-72B-Chat | 89.0 | 88.7 | 88.8 |
| Ernie-Bot 4.0 | 86.7 | 85.2 | 84.6 |
| Yi-34B-Chat | 72.5 | 81.4 | 76.6 |
| Ernie-Bot | 76.1 | 75.7 | 75.7 |
| GPT-4 | 70.5 | 73.8 | 67.4 |
| Yi-6B-Chat | 68.8 | 71.2 | 66.5 |
| Qwen-7B-Chat | 58.7 | 60.4 | 60.4 |
| Baichuan2-13B-Chat | 56.1 | 60.9 | 56.1 |
| ChatGLM3-6B | 59.8 | 59.2 | 53.7 |
| Baichuan2-7B-Chat | 55.2 | 56.2 | 52.9 |
| ChatGPT | 54.5 | 56.9 | 52.3 |
| Chinese-Alpaca-2-13B | 44.8 | 46.2 | 38.7 |
| Educhat-sft-002-13B | 33.2 | 39.4 | 36.1 |
| Chinese-LLaMA-2-13B | 35.7 | 38.9 | 33.2 |
| Educhat-sft-002-13B-Baichuan | 54.0 | 14.4 | 38.1 |

主要失败维度：中文 K12 里中文模型显著占优；few-shot/CoT 对强模型并不稳定，可能因提示格式和解释冗余导致下降。

**OlympiadBench 关键结果**

| Model | Setting | Maths Avg | Physics Avg | Overall |
|---|---|---:|---:|---:|
| LLaVA-NeXT-34B | full multimodal | 4.30 | 2.08 | 3.65 |
| Yi-VL-34B | full multimodal | 4.23 | 1.46 | 3.42 |
| Gemini-Pro-Vision | full multimodal | 5.14 | 2.45 | 4.22 |
| Qwen-VL-Max | full multimodal | 12.65 | 5.09 | 10.09 |
| GPT-4V | full multimodal | 21.70 | 10.74 | 17.97 |
| DeepSeekMath-7B-RL | text-only | 18.09 | 9.97 | 17.02 |
| Qwen-VL-Max | text-only | 19.70 | 8.83 | 18.27 |
| GPT-4V | text-only | 31.01 | 16.24 | 29.07 |
| GPT-4 | text-only | 32.00 | 16.24 | 29.93 |

主要失败维度：奥赛物理比数学更低；图像输入并不自动提升，很多模型“看图”后反而受扰；中文复杂证明题尤其难。

**CMMU 测试集平均分**

| Model | Test Avg |
|---|---:|
| InstructBLIP-13B | 0.48 |
| CogVLM-7B | 4.90 |
| ShareGPT4V-7B | 7.63 |
| mPLUG-Owl2-7B | 8.58 |
| LLaVA-1.5-13B | 11.96 |
| Qwen-VL-Chat-7B | 12.14 |
| Intern-XComposer-7B | 18.42 |
| Gemini-Pro | 22.50 |
| Qwen-VL-Plus | 27.73 |
| GPT-4V | 30.91 |

主要失败维度：填空题和多选题远难于单选；高中题难于小学题；数学、物理、图表题容易出现视觉定位和选项理解错误。

**ChartQA 结果**

| Model | ChartQA-H | ChartQA-M | Overall |
|---|---:|---:|---:|
| TaPas | 28.72 | 53.84 | 41.28 |
| VisionTaPas | 29.60 | 61.44 | 45.52 |
| VisionTaPas dagger | 24.84 | 61.60 | 43.72 |
| T5 | 25.12 | 56.96 | 41.04 |
| VL-T5 | 26.24 | 56.88 | 41.56 |
| VisionTaPas star | 25.12 | 38.80 | 31.96 |
| VL-T5 star | 22.08 | 19.84 | 20.96 |
| VisionTaPas Pretrained | 32.56 | 61.60 | 47.08 |
| VL-T5 Pretrained | 40.08 | 63.60 | 51.84 |

主要失败维度：人工问题 ChartQA-H 比机器生成问题难很多；多图元引用、数值抽取和算术组合是瓶颈。

### B. 数学、视觉数学与代码

**GSM8K 原论文读数**

| Model/方法 | 代表结果 |
|---|---|
| GPT-3 175B fine-tuned | 约 33-34% |
| GPT-3 175B generator + verifier 多样本重排 | 约 55% |
| 小模型 generator + verifier | verifier 有效，但不如大 generator |

主要失败维度：多步算术和中间状态一致性；verifier 可以显著提升，但不能根治错误推理。

**MATH 原论文结果**

| Model | Prealg. | Algebra | Num. Theory | Count/Prob | Geometry | Intermed. Alg. | Precalc. | Avg |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| GPT-2 0.1B | 5.2 | 5.1 | 5.0 | 2.8 | 5.7 | 6.5 | 7.3 | 5.4 |
| GPT-2 0.3B | 6.7 | 6.6 | 5.5 | 3.8 | 6.9 | 6.0 | 7.1 | 6.2 |
| GPT-2 0.7B | 6.9 | 6.1 | 5.5 | 5.1 | 8.2 | 5.8 | 7.7 | 6.4 |
| GPT-2 1.5B | 8.3 | 6.2 | 4.8 | 5.4 | 8.7 | 6.1 | 8.8 | 6.9 |
| GPT-3 13B few-shot | 4.1 | 2.4 | 3.3 | 4.5 | 1.0 | 3.2 | 2.0 | 3.0 |
| GPT-3 13B fine-tuned | 6.8 | 5.3 | 5.5 | 4.1 | 7.1 | 4.7 | 5.8 | 5.6 |
| GPT-3 175B few-shot | 7.7 | 6.0 | 4.4 | 4.7 | 3.1 | 4.4 | 4.0 | 5.2 |

主要失败维度：竞赛级题几乎全面困难；模型规模本身不足，过程监督和工具使用才是后来数学能力提升的关键。

**OlymMATH HARD 代表结果**

| Model | English HARD P@1 | English HARD C@64 | Chinese HARD P@1 | Chinese HARD C@64 |
|---|---:|---:|---:|---:|
| DeepSeek-R1 | 19.5 | 25.0 | 15.9 | 17.0 |
| OpenAI o3-mini | 31.2 | 39.0 | 32.9 | 42.0 |
| Gemini 2.5 Pro | 58.4 | 67.0 | 55.4 | 63.0 |
| Qwen3-235B-A22B | 36.5 | 41.0 | 28.1 | 34.0 |

主要失败维度：Pass@64 与 Cons@64 差距很大，说明模型存在“偶尔解出但不能稳定一致”的问题；中英平行题仍有语言差异。

**MathVista testmini 官方榜单 ALL 分数**

| Model | ALL |
|---|---:|
| OpenAI o1 | 73.9 |
| Grok-2 | 69.0 |
| Grok-2 mini | 68.1 |
| Claude 3.5 Sonnet | 67.7 |
| LLaVA-OneVision | 67.5 |
| InternVL2-Pro | 66.8 |
| TextGrad GPT-4o | 66.1 |
| Gemini 1.5 Pro May | 63.9 |
| GPT-4o | 63.8 |
| Human | 60.3 |
| InternVL-Chat-V1.2-Plus | 59.9 |
| Gemini 1.5 Flash | 58.4 |
| GPT-4T | 58.1 |
| Pixtral 12B | 58.0 |
| InternLM-XComposer2-VL-7B | 57.6 |
| Gemini 1.0 Ultra | 53.0 |
| Grok-1.5V | 52.8 |
| Gemini 1.5 Pro Feb | 52.1 |
| Claude 3 Opus | 50.5 |
| GPT-4V Playground | 49.9 |
| Claude 3 Sonnet | 47.9 |
| InternVL-Chat-V1.2 | 47.7 |
| Math-LLaVA-13B | 46.6 |
| LLaVA-NeXT-34B | 46.5 |
| Claude 3 Haiku | 46.4 |
| Gemini 1.0 Pro | 45.2 |
| Phi-3-Vision | 44.5 |
| Phi-3.5-Vision | 43.9 |
| Qwen-VL-Plus | 43.3 |
| Mini-Gemini-HD | 43.3 |
| SPHINX-MoE | 42.3 |
| Mini-Gemini Mixtral | 41.8 |
| MM1-7B-MoE | 40.9 |
| MiniCPM-V-2 | 40.6 |
| MM1-30B | 39.4 |
| SPHINX-Plus | 36.8 |
| SPHINX V2 | 36.7 |
| MM1-7B | 35.9 |
| SPHINX-Intern2 | 35.5 |
| OmniLMM-12B | 34.9 |
| Multimodal Bard | 34.8 |
| LLaVA-NeXT-Vicuna-7B | 34.6 |
| PoT GPT-4 | 33.9 |
| CoT Claude | 33.2 |
| CoT GPT-4 | 33.2 |
| CoT ChatGPT | 33.2 |
| MM1-3B-MoE | 32.6 |
| MM1-3B | 32.0 |
| Gemini Nano2 | 30.6 |
| LLaVA-1.5-13B | 27.6 |
| SPHINX V1 | 27.5 |
| Gemini Nano1 | 27.3 |
| PoT ChatGPT | 26.8 |
| SPHINX-Tiny | 26.4 |
| LLaVA LLaMA-2-13B | 26.1 |
| InstructBLIP | 25.3 |
| LLaVAR | 25.2 |
| LLaMA-Adapter-V2 | 23.9 |
| miniGPT4 | 23.1 |
| mPLUG-Owl | 22.2 |
| IDEFICS | 19.8 |
| Random | 17.9 |

主要失败维度：逻辑图形、数值题、视觉问答混合题最难；早期 CoT/PoT 在多模态设置中不稳。

**ME2 视觉关键点与讲解生成**

| Model | Visual Keypoint Overall | Explanation correctness | Fidelity | Reference |
|---|---:|---:|---:|---:|
| Gemini 2.0 Flash | 0.576 | 3.849 | 3.489 | 4.103 |
| GPT-4o | 0.472 | 3.784 | 3.153 | 3.892 |
| Qwen2.5-VL-72B | 0.536 | 3.397 | 3.048 | 3.533 |
| Qwen2.5-VL-7B | 0.403 | 3.005 | 2.375 | 3.132 |
| Qwen2-VL | 0.296 | - | - | - |
| Molmo 7B | 0.267 | - | - | - |
| LLaVA-1.6 7B | 0.265 | - | - | - |
| Math-PUMA 7B | 0.200 | - | - | - |
| URSA 8B | 0.029 | - | - | - |
| Math-LLaVA 13B | 0.217 | - | - | - |

主要失败维度：几何辅助线、关键点、图形关系 grounding；数学专用模型不等于几何视觉教学能力强。

**HumanEval 原论文结果**

| Model | pass@1 | pass@10 | pass@100 |
|---|---:|---:|---:|
| GPT-Neo 125M | 0.75 | 1.88 | 2.97 |
| GPT-Neo 1.3B | 4.79 | 7.47 | 16.30 |
| GPT-Neo 2.7B | 6.41 | 11.27 | 21.37 |
| GPT-J 6B | 11.62 | 15.74 | 27.74 |
| TabNine | 2.58 | 4.35 | 7.59 |
| Codex-12M | 2.00 | 3.62 | 8.58 |
| Codex-25M | 3.21 | 7.10 | 12.89 |
| Codex-42M | 5.06 | 8.80 | 15.55 |
| Codex-85M | 8.22 | 12.81 | 22.40 |
| Codex-300M | 13.17 | 20.37 | 36.27 |
| Codex-679M | 16.22 | 25.70 | 40.95 |
| Codex-2.5B | 21.36 | 35.42 | 59.50 |
| Codex-12B | 28.81 | 46.81 | 72.31 |
| Codex-S | 37.7 | - | 77.5 |

主要失败维度：自然语言需求理解、边界条件、隐藏测试、运行时错误和安全问题。

**MBPP 原论文结果**

| Model size | Prompt | Problems solved | Samples solving task |
|---|---|---:|---:|
| 8B | original | 35% | 4.46% |
| 8B | edited | 45% | 7.36% |
| 68B | original | 48% | 8.02% |
| 68B | edited | 61% | 12.95% |
| 137B | original | 63% | 20.78% |
| 137B | edited | 79% | 31.85% |

主要失败维度：初学者编程题仍受 prompt 清晰度影响；模型易忽视边界条件和测试断言。

### C. 教学能力与教育多模态

**Pedagogy Benchmark 完整 CDPK 榜单**

| Model | CDPK | Model | CDPK |
|---|---:|---|---:|
| Gemini-2.5 Pro | 88.77 | Gemini-1.5 Pro | 73.86 |
| o3 | 87.88 | Qwen-3 8B | 73.53 |
| Claude Opus 4 Thinking low | 87.43 | Claude-3.5 Sonnet June | 73.08 |
| Claude Sonnet 4 Thinking low | 86.76 | Grok Beta | 72.86 |
| Deepseek R1 May 2025 | 86.65 | Gemma-3 27B | 72.64 |
| o1 | 86.43 | o1-Mini | 72.64 |
| Claude Opus 4 | 86.32 | Phi-4 | 72.19 |
| Gemini-2.5 Flash | 85.54 | Gemini-1.5 Flash | 72.19 |
| Claude-3.7 Sonnet Thinking medium | 85.43 | Doubao-1.5 Lite | 72.08 |
| GPT-4.5 Preview | 85.21 | Yi Lightning | 71.75 |
| Claude Sonnet 4 | 84.76 | Yi-Large | 71.52 |
| Qwen-3 32B | 82.42 | Gemma-2 27B | 71.19 |
| GPT-4.1 | 82.31 | Sonar | 70.75 |
| o4-Mini | 81.98 | Mistral Small 3 | 70.41 |
| Grok-3 | 81.76 | Nova Lite | 69.97 |
| Llama-4 Maverick | 81.65 | Jamba 1.6 Large | 69.86 |
| Doubao-1.5 Pro | 80.76 | GPT-4o Mini | 69.19 |
| Grok-3 Mini | 80.65 | Jamba 1.5 Large | 69.08 |
| Qwen-3 235B 22B active | 80.65 | Hunyuan Large | 68.19 |
| Grok-2 | 80.20 | Gemma-3 12B | 67.63 |
| Mistral Medium 3 | 79.98 | Qwen-2.5 7B | 66.74 |
| Gemini-2.0 Flash | 79.87 | Mixtral-8x22B | 65.85 |
| Qwen-3 30B 3B active | 79.76 | Hunyuan Large Long Context | 65.41 |
| o3-Mini | 79.42 | Gemma-3n E4B | 63.96 |
| Llama-3.1 405B | 78.75 | GPT-4.1 Nano | 63.52 |
| Qwen-3 14B | 78.53 | Claude-3.5 Haiku | 63.29 |
| Deepseek V3 | 78.31 | Nova Micro | 63.18 |
| GPT-4o | 78.31 | LFM-7B | 61.85 |
| Command A | 77.86 | Command-R+ August | 61.51 |
| Gemini-2.0 Flash-Lite | 77.64 | Jamba Instruct | 61.18 |
| LearnLM 1.5 Pro | 77.31 | Jamba 1.6 Mini | 61.07 |
| Deepseek V3 0324 | 77.09 | Jamba 1.5 Mini | 60.96 |
| Claude-3 Opus | 76.97 | Mixtral-8x7B | 59.84 |
| Qwen-2.5 32B | 76.86 | Gemini-1.5 Flash 8B | 59.18 |
| Claude-3.5 Sonnet October | 76.75 | Llama-3.1 8B | 59.07 |
| Claude-3.7 Sonnet | 76.75 | Llama-3.2 11B | 59.07 |
| Llama-3.2 90B | 76.31 | LFM-3B | 57.06 |
| Gemini-2.5 Flash-Lite Preview | 76.20 | Claude-3 Haiku | 56.95 |
| Mistral Small 3.1 24B | 75.86 | Mistral Nemo | 56.95 |
| Qwen-2.5 14B | 75.64 | Ministral 8B | 56.40 |
| Qwen-2.5 72B | 75.42 | Phi-3.5 Mini | 56.06 |
| Nova Pro | 75.31 | Phi-4 Multimodal | 53.17 |
| Mistral Large November | 75.31 | Ministral 3B | 52.39 |
| Llama-3.3 70B | 75.19 | Gemma-3 4B | 52.39 |
| GPT-4.1 Mini | 75.08 | GPT-3.5 Turbo | 52.28 |
| Llama-3.1 70B | 74.97 | Phi-3.5 Vision | 51.06 |
| Llama-4 Scout | 74.53 | Command R7B | 46.05 |
| GPT-4 Turbo | 74.30 | Llama-3.2 1B | 28.03 |
| GPT-4 | 74.08 |  |  |

**Pedagogy Benchmark 完整 SEND 榜单**

| Model | SEND | Model | SEND |
|---|---:|---|---:|
| Gemini-2.5 Pro | 85.91 | Llama-3.3 70B | 69.55 |
| Claude Opus 4 Thinking low | 83.64 | Mistral Small 3.1 24B | 69.55 |
| o3 | 82.27 | GPT-4 | 69.09 |
| Claude Sonnet 4 Thinking low | 80.91 | Claude-3 Opus | 68.64 |
| Claude Opus 4 | 80.91 | Mistral Small 3 | 68.64 |
| Claude Sonnet 4 | 80.00 | Nova Lite | 68.64 |
| o1-Medium | 79.55 | o1-Mini | 68.64 |
| GPT-4.1 | 79.55 | Doubao-1.5 Lite | 68.64 |
| Claude-3.7 Sonnet Thinking medium | 79.09 | Gemini-1.5 Flash | 68.18 |
| Gemini-2.5 Flash | 78.64 | Llama-4 Scout | 67.73 |
| Deepseek R1 May 2025 | 78.64 | Jamba 1.5 Large | 67.73 |
| o4-Mini | 78.64 | Hunyuan Large Long Context | 67.73 |
| GPT-4.5 Preview | 78.18 | Claude-3.5 Haiku | 67.27 |
| Grok-2 | 77.27 | Grok Beta | 67.27 |
| Mistral Medium 3 | 77.27 | Command-R+ August | 66.36 |
| Grok-3 Mini | 75.91 | Jamba 1.6 Large | 66.36 |
| Gemini-2.0 Flash | 75.91 | Claude-3.5 Sonnet October | 66.36 |
| Llama-4 Maverick | 75.45 | Claude-3.5 Sonnet June | 66.36 |
| Qwen-3 32B | 75.45 | Gemma-3 12B | 65.91 |
| Qwen-3 30B 3B active | 75.45 | Yi-Large | 65.91 |
| Qwen-3 235B 22B active | 75.45 | Mixtral-8x7B | 65.00 |
| GPT-4.1 Mini | 75.00 | Llama-3.2 11B | 65.00 |
| Deepseek V3 | 74.09 | Sonar | 65.00 |
| Gemini-2.5 Flash-Lite Preview | 73.64 | Llama-3.1 8B | 64.55 |
| Gemma-3 27B | 73.64 | GPT-4.1 Nano | 64.55 |
| GPT-4o | 73.64 | Yi Lightning | 64.09 |
| Deepseek V3 0324 | 73.18 | Phi-3.5 Vision | 63.64 |
| Gemma-2 27B | 73.18 | Mixtral-8x22B | 62.73 |
| Doubao-1.5 Pro | 73.18 | Gemma-3n E4B | 62.73 |
| o3-Mini | 72.73 | Mistral Nemo | 62.27 |
| Llama-3.1 405B | 72.27 | Qwen-2.5 7B | 61.82 |
| Grok-3 | 72.27 | Phi-3.5 Mini | 61.36 |
| Gemini-1.5 Pro | 72.27 | Jamba 1.6 Mini | 60.91 |
| Command A | 71.82 | Nova Micro | 60.91 |
| Gemini-2.0 Flash-Lite | 71.82 | LFM-3B | 60.00 |
| Mistral Large November | 71.36 | Ministral 8B | 60.00 |
| LearnLM 1.5 Pro | 71.36 | Ministral 3B | 59.55 |
| Nova Pro | 71.36 | LFM-7B | 58.64 |
| GPT-4o Mini | 71.36 | Jamba Instruct | 58.18 |
| Qwen-2.5 72B | 70.91 | Phi-4 Multimodal | 58.18 |
| Claude-3.7 Sonnet | 70.45 | Gemini-1.5 Flash 8B | 57.73 |
| Llama-3.2 90B | 70.45 | Jamba 1.5 Mini | 57.27 |
| Qwen-3 14B | 70.45 | Claude-3 Haiku | 56.36 |
| Hunyuan Large | 70.00 | Gemma-3 4B | 55.45 |
| Llama-3.1 70B | 70.00 | Command R7B | 53.18 |
| GPT-4 Turbo | 70.00 | GPT-3.5 Turbo | 52.73 |
| Qwen-3 8B | 69.55 | Llama-3.2 1B | 28.64 |
| Phi-4 | 69.55 |  |  |

主要失败维度：SEND 专业知识、课堂管理、评估策略；CDPK 与 SEND 相关很高，但弱模型常出现反向偏科。

**MathTutorBench 全表**

| Model | Problem solving | Socratic BLEU | Solution correctness | Mistake location | Correction | Scaffolding | Ped. IF | Scaff. hard | Ped. IF hard |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| LLaMA3.2-3B-Instruct | 0.60 | 0.29 | 0.67 | 0.41 | 0.13 | 0.64 | 0.63 | 0.45 | 0.40 |
| LLaMA3.1-8B | 0.70 | 0.29 | 0.63 | 0.29 | 0.09 | 0.61 | 0.67 | 0.46 | 0.49 |
| LLaMA3.1-70B | 0.91 | 0.29 | 0.71 | 0.56 | 0.19 | 0.63 | 0.70 | 0.49 | 0.49 |
| GPT-4o | 0.90 | 0.48 | 0.67 | 0.37 | 0.84 | 0.50 | 0.82 | 0.46 | 0.70 |
| LearnLM-1.5-Pro | 0.94 | 0.32 | 0.75 | 0.57 | 0.74 | 0.64 | 0.68 | 0.66 | 0.67 |
| Llemma-7B-ScienceTutor | 0.62 | 0.29 | 0.66 | 0.29 | 0.16 | 0.37 | 0.48 | 0.38 | 0.42 |
| Qwen2.5-7B-SocraticLM | 0.73 | 0.32 | 0.05 | 0.39 | 0.23 | 0.39 | 0.39 | 0.28 | 0.28 |
| Qwen2.5-Math-7B-Instruct | 0.88 | 0.35 | 0.43 | 0.47 | 0.49 | 0.06 | 0.07 | 0.05 | 0.05 |

主要失败维度：解题、纠错、脚手架三者存在张力；数学强模型可能最不适合作为 tutor 回复模型。

**EduBench 人工与模型评测**

| Evaluator | Model | Avg |
|---|---|---:|
| DeepSeek V3 | DeepSeek R1 | 8.93 |
| DeepSeek V3 | DeepSeek V3 | 8.66 |
| DeepSeek V3 | Qwen Max | 8.66 |
| DeepSeek V3 | Qwen2.5-14B-Instruct | 8.46 |
| DeepSeek V3 | Qwen2.5-7B-Instruct | 8.44 |
| GPT-4o | DeepSeek R1 | 8.98 |
| GPT-4o | DeepSeek V3 | 8.93 |
| GPT-4o | Qwen Max | 8.90 |
| GPT-4o | Qwen2.5-14B-Instruct | 8.77 |
| GPT-4o | Qwen2.5-7B-Instruct | 8.77 |
| Human | DeepSeek R1 | 8.74 |
| Human | DeepSeek V3 | 7.89 |
| Human | Qwen Max | 8.02 |
| Human | Qwen2.5-14B-Instruct | 7.56 |
| Human | Qwen2.5-7B-Instruct | 7.46 |
| DeepSeek V3 | Distillation Qwen2.5-7B | 8.75 |

主要失败维度：模型评委普遍比人类打分高；Qwen2.5-7B 在 Error Identification & Correction Precision 和 Reasoning Process Rigor 上弱；DeepSeek V3 与人类一致性相对更好，GPT-4o 一致性最低。

**EduEval 汇总均分**

| Model | Zero-shot Avg | Few-shot Avg |
|---|---:|---:|
| Spark-X1 | 81.1 | 77.4 |
| Qwen-plus | 77.7 | 75.8 |
| Qwen-72B | 75.0 | 72.1 |
| DeepseekR1-32B | 74.8 | - |
| GPT-4o | 71.0 | 67.3 |
| Yi-34B | 69.8 | - |
| Qwen-14B-Chat | 68.1 | 65.2 |
| GLM4-9B-Chat | 67.6 | - |
| Qwen-7B | 60.8 | 53.7 |
| Yi-6B | 57.9 | - |
| EduChat-sft-002-13B | 53.8 | - |
| LLaMA3-8B | 50.3 | - |
| BaiChuan-13B | 48.7 | - |
| LLaMA2-Chinese-13B | 39.3 | - |

主要失败维度：记忆/理解好于应用/推理/创造；few-shot 经常下降，说明教育生成类任务不能简单套通用考试提示。

**OmniEduBench 主表**

| Model | Knowledge Avg | Cultivation Avg |
|---|---:|---:|
| Qwen3 8B | 43.86 | 68.62 |
| Qwen3 14B | 35.62 | 63.60 |
| MuduoLLM 14B | 33.68 | 63.96 |
| QwQ 32B | 53.87 | 70.27 |
| Seed-OSS 36B | 49.53 | 67.18 |
| Qwen2.5 72B | 22.76 | 65.34 |
| Qwen3 235B | 40.82 | 63.74 |
| DeepSeek-V3.1 | 36.05 | 68.55 |
| GPT-4o | 24.17 | 59.57 |
| Claude-4 Sonnet | 40.35 | 70.03 |
| Gemini-2.5 Pro | 62.76 | 69.14 |

主要失败维度：知识维度远比培养维度更拉开差距；GPT-4o 和 Qwen2.5-72B 在中文知识题上很低；HARD 子集所有模型显著下降。

**EduGuard-Bench 代表结果**

| Model | Type | RFS | Acc | Omit | Incl | ASR |
|---|---|---:|---:|---:|---:|---:|
| Claude-3.7 | reasoning | 0.77 | 71.84 | 10.78 | 17.38 | 27.0 |
| Qwen3-235B-R | reasoning | 0.69 | 63.98 | 9.22 | 26.80 | 70.0 |
| Deepseek-R1 | reasoning | 0.75 | 70.09 | 9.87 | 20.04 | 59.4 |
| R1-Distill-70B | reasoning | 0.73 | 69.51 | 7.95 | 22.54 | 63.2 |
| Qwen3-32B-R | reasoning | 0.75 | 71.16 | 7.29 | 21.55 | 75.2 |
| GLM-Z1-9B | reasoning | 0.69 | 64.06 | 9.63 | 26.31 | 79.0 |
| Qwen3-8B-R | reasoning | 0.69 | 60.76 | 16.05 | 23.19 | 60.4 |
| GPT-4o | non-reasoning | 0.69 | 67.96 | 2.96 | 29.08 | 42.8 |
| Deepseek-V3 | non-reasoning | 0.73 | 71.46 | 2.58 | 25.96 | 81.6 |
| Qwen3-235B-NR | non-reasoning | 0.67 | 64.58 | 4.29 | 31.13 | 63.8 |
| Qwen2.5-72B | non-reasoning | 0.56 | 52.68 | 6.79 | 40.53 | 56.2 |
| Qwen3-32B-NR | non-reasoning | 0.72 | 70.21 | 3.04 | 26.75 | 68.4 |
| Qwen3-8B-NR | non-reasoning | 0.61 | 50.68 | 19.99 | 29.33 | 62.7 |
| Educhat-r1 | non-reasoning | 0.71 | 66.12 | 9.83 | 24.05 | 70.0 |

主要失败维度：安全和教学能力不一致；reasoning 提升角色扮演，但不必然提升对抗安全；Deepseek-V3 的 ASR 最高，图 6 排序中 Claude-3.7 最安全。注意：论文正文一句话称 Qwen2.5-72B 为 17.2% 最安全，但同页图 6 和 Response Type Distribution 都显示 Qwen2.5-72B ASR 为 56.2%，本表按图表数值记录。

**TutorBench 全表**

| Model | Text-only | Multimodal | Overall |
|---|---:|---:|---:|
| Gemini 2.5 Pro | 57.05 | 54.53 | 55.65 |
| GPT-5 | 57.03 | 53.97 | 55.33 |
| o3 Pro | 56.07 | 53.45 | 54.62 |
| o3 Medium Effort | 54.11 | 51.68 | 52.76 |
| o3 High Effort | 52.91 | 51.43 | 52.09 |
| Claude Opus 4.1 Thinking | 51.65 | 50.08 | 50.78 |
| Claude Opus 4 Thinking | 50.40 | 49.14 | 49.71 |
| Claude Opus 4.1 | 49.51 | 45.72 | 47.40 |
| Claude 3.7 Sonnet Thinking | 45.67 | 47.07 | 46.45 |
| Claude Opus 4 | 47.79 | 43.59 | 45.46 |
| Llama 4 Maverick | 39.54 | 40.73 | 40.20 |
| GPT-4o | 39.10 | 33.74 | 36.12 |
| gpt-oss-120b | 56.01 | N/A | N/A |
| gpt-oss-20b | 49.01 | N/A | N/A |
| DeepSeek-R1 | 48.38 | N/A | N/A |

主要失败维度：所有前沿模型总体低于 56%；多模态作业反馈比纯文本更低；GPT-4o 在该基准明显落后于最新 reasoning 模型。

**EduVisBench 全表**

| Model | Output | Logical Seq. | Struct. Rich. | Semantic Align. | Explan. Guidance | Interaction | Avg |
|---|---|---:|---:|---:|---:|---:|---:|
| Flux.1-dev | Image | 13.8 | 13.4 | 13.2 | 11.7 | 8.5 | 13.8 |
| SD3.5 | Image | 17.3 | 20.3 | 18.8 | 16.8 | 13.0 | 18.4 |
| SDXL | Image | 17.3 | 23.3 | 25.5 | 18.9 | 15.4 | 21.8 |
| Deepseek VL2 | Webpage | 20.3 | 17.1 | 15.7 | 17.9 | 17.0 | 17.5 |
| GLM-4V-9B | Webpage | 22.3 | 21.1 | 19.4 | 24.5 | 21.5 | 21.9 |
| MiniCPM-V-2.6 | Webpage | 24.1 | 17.3 | 15.5 | 19.1 | 17.4 | 19.3 |
| Mistral-Small-3.1 | Webpage | 29.1 | 31.6 | 32.2 | 32.3 | 33.5 | 30.2 |
| Phi-3.5 | Webpage | 25.3 | 20.7 | 19.1 | 21.2 | 19.5 | 21.8 |
| Phi-4 | Webpage | 26.1 | 25.1 | 22.9 | 27.8 | 25.5 | 26.4 |
| Qwen2.5-VL-72B | Webpage | 24.3 | 18.1 | 15.8 | 19.7 | 17.1 | 20.0 |
| Claude 3.7 Sonnet | SVG | 61.2 | 26.7 | 23.6 | 18.5 | 16.9 | 42.0 |
| Claude 3.7 Sonnet | Webpage | 56.2 | 57.5 | 55.6 | 44.8 | 42.6 | 54.6 |
| GPT-4o | Webpage | 47.6 | 39.3 | 37.9 | 25.7 | 24.2 | 38.1 |
| GPT-4o | SVG | 36.1 | 19.7 | 19.5 | 13.0 | 12.8 | 26.3 |
| Gemini 2.0 Flash | Webpage | 46.9 | 9.5 | 15.7 | 31.7 | 26.5 | 43.6 |
| v0 | Webpage | 63.0 | 37.6 | 47.2 | 53.3 | 58.5 | 58.2 |
| EduVisAgent | Webpage | - | - | - | - | - | 81.6 |

主要失败维度：扩散模型只能生成图像，教学逻辑和交互低；SVG 输出通常比网页弱；v0 结构和交互较强，但仍缺少面向解题步骤的教学组织。

**SciVideoBench 全模型 Overall**

| Model | Setting | Overall |
|---|---|---:|
| Random | baseline | 10.00 |
| Human graduate students | human | 17.40 |
| GPT-4o | vision-blind | 15.80 |
| Qwen2.5 0.5B | vision-blind | 12.40 |
| Qwen2.5 1.5B | vision-blind | 13.40 |
| Qwen2.5 3B | vision-blind | 16.40 |
| Qwen2.5 7B | vision-blind | 16.70 |
| Qwen2.5 32B | vision-blind | 17.10 |
| Qwen2.5 72B | vision-blind | 18.90 |
| Gemini-2.5-Pro | proprietary | 64.30 |
| Gemini-2.5-Flash | proprietary | 46.40 |
| Gemini-1.5-Pro | proprietary | 27.50 |
| Gemini-2.0-Flash | proprietary | 25.70 |
| GPT-4o | proprietary | 24.90 |
| Gemini-1.5-Pro | proprietary CoT | 48.60 |
| Gemini-2.0-Flash | proprietary CoT | 39.70 |
| GPT-4o | proprietary CoT | 35.00 |
| InternVL-3-78B | open CoT | 37.90 |
| InternVL-3-14B | open CoT | 34.20 |
| InternVL-3-14B-Instruct | open CoT | 31.50 |
| InternVL-3-8B | open CoT | 25.50 |
| InternVL2-Llama3-76B | open CoT | 24.90 |
| InternVL-3-9B-Instruct | open CoT | 24.00 |
| InternVL-3-2B | open CoT | 22.20 |
| Qwen2.5-VL-32B-Instruct | open CoT | 20.80 |
| LLaVA-OneVision-7B | open CoT | 19.90 |
| Qwen2.5-VL-3B-Instruct | open CoT | 18.10 |
| InternVL-3-1B | open CoT | 14.00 |
| LLaVA-OneVision-0.5B | open CoT | 10.40 |
| InternVL-3-2B-Instruct | open 0.5-4B | 24.00 |
| InternVL-3-2B | open 0.5-4B | 22.90 |
| InternVL2-4B | open 0.5-4B | 21.30 |
| InternVL-3-1B-Instruct | open 0.5-4B | 18.90 |
| InternVL-3-1B | open 0.5-4B | 18.50 |
| Qwen2.5-VL-3B-Instruct | open 0.5-4B | 16.10 |
| InternVL2-1B | open 0.5-4B | 14.40 |
| InternVL2-2B | open 0.5-4B | 13.10 |
| LLaVA-OneVision-0.5B | open 0.5-4B | 12.10 |
| InternVL-3-14B | open 7-14B | 35.70 |
| InternVL-3-14B-Instruct | open 7-14B | 35.70 |
| InternVL-3-8B | open 7-14B | 30.50 |
| InternVL-3-8B-Instruct | open 7-14B | 29.40 |
| InternVL-3-9B-Instruct | open 7-14B | 29.20 |
| InternVL-3-9B | open 7-14B | 27.20 |
| InternVideo2.5-Chat-8B | open 7-14B | 25.30 |
| InternVL2-8B | open 7-14B | 19.40 |
| LLaVA-OneVision-7B | open 7-14B | 18.80 |
| Qwen2.5-VL-7B-Instruct | open 7-14B | 16.40 |
| LongVA | open 7-14B | 14.30 |
| InternVL-3-38B | open 26-40B | 38.30 |
| InternVL-3-38B-Instruct | open 26-40B | 37.30 |
| InternVL2-40B | open 26-40B | 23.80 |
| Qwen2.5-VL-32B-Instruct | open 26-40B | 21.50 |
| LLaVA-NeXT-Video-32B | open 26-40B | 21.10 |
| InternVL2-26B | open 26-40B | 19.50 |
| InternVL-3-78B-Instruct | open >70B | 38.80 |
| InternVL-3-78B | open >70B | 38.50 |
| InternVL2-Llama3-76B | open >70B | 26.30 |
| Qwen2.5-VL-72B-Instruct | open >70B | 20.30 |

主要失败维度：Quantitative Reasoning 最难，Gemini-2.5-Pro 也只有 50.61；视觉盲基线接近随机，说明视频输入不可替代；CoT 对闭源模型提升明显，但对很多开源模型会降低 overall。

**K12Vista Direct 与 Step-by-Step Overall**

| Model | Direct Overall | Step-by-Step Overall |
|---|---:|---:|
| Gemini2-thinking | 55.47 | 57.36 |
| Qwen2.5-VL-32B | 55.42 | 53.35 |
| Qwen2.5-VL-72B | 51.39 | 49.93 |
| Gemini2-flash | 51.08 | 47.34 |
| QVQ-72B-preview | 49.54 | 46.31 |
| InternVL2.5-MPO-78B | 45.43 | 42.82 |
| InternVL2.5-MPO-38B | 40.85 | 38.54 |
| InternVL2.5-78B | 40.41 | 38.53 |
| GPT-4o | 35.02 | 35.00 |
| InternVL2.5-38B | 36.45 | 33.40 |
| InternVL2.5-MPO-26B | 33.58 | 29.92 |
| Qwen2.5-VL-7B | 39.82 | 27.16 |
| LLaVA-OneVision-72B | 31.57 | 27.11 |
| Qwen2-VL-72B | 34.48 | 25.71 |
| InternVL2.5-MPO-8B | 29.94 | 26.93 |
| InternVL2.5-MPO-4B | 29.33 | 25.09 |
| InternVL2.5-26B | 30.60 | 24.66 |
| InternVL2.5-8B | 27.31 | 22.69 |
| InternVL2-76B | 28.95 | 20.85 |
| InternVL2.5-4B | 27.18 | 20.70 |
| MiniCPM-o-2.6 | 26.91 | 19.09 |
| Qwen2.5-VL-3B | 31.99 | 16.45 |
| InternVL2-40B | 28.18 | 13.90 |
| InternVL2-8B | 25.73 | 12.97 |
| Qwen2-VL-7B | 25.70 | 12.58 |
| LLaVA-OneVision-7B | 23.94 | 11.92 |

主要失败维度：step-by-step evaluation 通常更低，只对 reasoning-enhanced 模型有帮助；GPT-4o 在中文 K12 多模态题上并不靠前；低参数模型过程正确性断崖式下降。

**InteractScience PFT Overall**

| Model | PFT Overall |
|---|---:|
| Claude-Sonnet-4-20250514 | 41.47 |
| GPT-5 | 39.47 |
| Claude-Opus-4 | 40.27 |
| GPT-4.1 | 37.07 |
| Gemini-2.5-Pro | 35.33 |
| Claude-3.5-Sonnet | 33.33 |
| GPT-4o | 28.27 |
| Qwen3-235B-A22B | 33.33 |
| Qwen3-32B | 27.20 |
| Qwen3-14B | 24.13 |
| Qwen3-8B | 20.00 |
| Qwen3-4B | 14.67 |
| Qwen3-1.7B | 6.53 |
| Qwen2.5-Coder-32B | 27.20 |
| Qwen2.5-VL-72B | 23.73 |
| Qwen2.5-VL-7B | 7.47 |

主要失败维度：动作和视觉可达分较高，但真正的功能完整性低；最佳 PFT overall 只有约 41%，说明交互式科学演示还远未解决。

### D. 自动评分

**EssayJudge QWK 全表**

| Model | LA | LD | CH | GA | GD | PA | AC | JP | OS | EL |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Yi-VL-6B | 0.07 | 0.05 | 0.08 | 0.09 | 0.05 | 0.09 | 0.05 | 0.13 | 0.05 | 0.07 |
| Qwen2-VL-7B | 0.20 | 0.26 | 0.13 | 0.21 | 0.16 | 0.12 | 0.17 | 0.10 | 0.14 | 0.15 |
| DeepSeek-VL-7B | 0.09 | 0.12 | 0.12 | 0.13 | 0.35 | 0.06 | 0.18 | 0.21 | 0.08 | 0.09 |
| LLaVA-NEXT-8B | 0.02 | 0.04 | 0.03 | 0.11 | 0.10 | 0.02 | 0.12 | 0.15 | 0.02 | 0.10 |
| InternVL2-8B | 0.28 | 0.27 | 0.34 | 0.36 | 0.31 | 0.33 | 0.25 | 0.29 | 0.31 | 0.29 |
| InternVL2.5-8B | 0.14 | 0.29 | 0.29 | 0.29 | 0.31 | 0.26 | 0.15 | 0.21 | 0.25 | 0.22 |
| MiniCPM-V2.6-8B | 0.18 | 0.07 | 0.08 | 0.16 | 0.09 | 0.04 | 0.12 | 0.35 | 0.06 | 0.24 |
| MiniCPM-LLaMA3-V2.5-8B | 0.37 | 0.27 | 0.36 | 0.29 | 0.34 | 0.29 | 0.09 | 0.18 | 0.21 | 0.09 |
| Ovis1.6-Gemma2-9B | 0.15 | 0.11 | 0.13 | 0.39 | 0.27 | 0.36 | 0.11 | 0.13 | 0.14 | 0.21 |
| LLaMA-3.2-Vision-11B | 0.20 | 0.16 | 0.17 | 0.14 | 0.11 | 0.12 | 0.09 | 0.17 | 0.17 | 0.16 |
| Qwen-Max | 0.57 | 0.51 | 0.52 | 0.56 | 0.48 | 0.40 | 0.34 | 0.54 | 0.45 | 0.41 |
| Step-1V | 0.52 | 0.40 | 0.49 | 0.50 | 0.46 | 0.37 | 0.26 | 0.39 | 0.31 | 0.25 |
| Gemini-1.5-Pro | 0.52 | 0.46 | 0.57 | 0.56 | 0.51 | 0.35 | 0.29 | 0.46 | 0.54 | 0.28 |
| Gemini-1.5-Flash | 0.46 | 0.40 | 0.48 | 0.53 | 0.41 | 0.33 | 0.33 | 0.42 | 0.47 | 0.28 |
| Claude-3.5-Haiku | 0.59 | 0.54 | 0.53 | 0.50 | 0.57 | 0.40 | 0.35 | 0.39 | 0.48 | 0.33 |
| Claude-3.5-Sonnet | 0.66 | 0.60 | 0.58 | 0.66 | 0.60 | 0.57 | 0.33 | 0.46 | 0.39 | 0.35 |
| GPT-4o-mini | 0.64 | 0.56 | 0.54 | 0.58 | 0.54 | 0.45 | 0.33 | 0.57 | 0.45 | 0.46 |
| GPT-4o | 0.89 | 0.89 | 0.87 | 0.85 | 0.61 | 0.65 | 0.30 | 0.80 | 0.79 | 0.70 |
| Human | 0.91 | 0.91 | 0.89 | 0.93 | 0.56 | 0.86 | 0.72 | 0.86 | 0.88 | 0.77 |

主要失败维度：Argument Clarity (AC) 对 GPT-4o 也只有 0.30，显著低于人类 0.72；闭源模型词汇级强，论证/篇章级仍弱；去掉图像后 GPT-4o 在全部 10 个维度下降。

**SAS-Bench CCS/ECS 平均**

| Model | CCS Avg | ECS Avg |
|---|---:|---:|
| Deepseek-R1 | 73.76 | 55.90 |
| QwQ-32B | 64.51 | 45.90 |
| TinyR1-32B-Preview | 65.17 | 44.82 |
| Qwen3-32B | 67.20 | 39.12 |
| Qwen3-8B | 58.43 | 29.25 |
| MiMo-7B-RL | 46.03 | 30.00 |
| Deepseek-Prover-V2-7B | 21.55 | -8.44 |
| DeepSeek-R1-Distill-7B | 40.44 | -14.34 |
| Deepseek-V3 | 74.11 | 54.00 |
| GPT-4o-mini-20240718 | 58.56 | 50.53 |
| Llama3.3-70B-Instruct | 62.73 | 36.26 |
| Mixtral 8x7B-Instruct | 35.49 | 29.30 |
| Qwen2.5-32B-Instruct | 62.56 | 40.76 |
| Qwen2.5-14B-Instruct | 64.44 | 43.02 |
| GLM4-9B-Chat | 46.85 | 38.43 |
| Llama3-8B-Instruct | 36.08 | 14.14 |

主要失败维度：CCS 低于 QWK，说明只看总分会高估模型；ECS 对错误原因分布更敏感，低模型可出现负相关；英语填空和科学题最不稳定。

### E. 无官方统一模型榜单的条目

下列条目本轮按论文/README/数据卡确认后，未找到可直接引用的官方统一模型 leaderboard。它们仍然重要，但应被视为数据资源、训练语料、产品入口或需另设协议的任务集合：

| 类别 | 条目 |
|---|---|
| 数学数据资源 | Math23K、Ape210K、NuminaMath、IMO-ANSWER BENCH、BigMath-Verified |
| 知识追踪/认知诊断 | ASSISTments、KDD Cup 2010、EdNet、Junyi Academy、FoundationalAssist、数字教育应用算法智能诊断公共数据集、PTADisc、STATICS2011、Synthetic、Adaptive Geography Practice |
| 自动评分经典数据 | ASAP-AES、ASAP-SAS、ELLIPSE Corpus |
| 教育问答数据 | MathDial、Google Education Dialogue Dataset、EduDial、IntrEx、SocraticLM、QACP、CS1QA |
| 教育资源 | FineWeb-Edu、Chinese Fineweb Edu、LectureBank、SCB-Dataset、NCTE Transcripts、ARIC、TalkMoves、TIMSS Video Study、SIGHT、VisualEDU、MLPdataset、MOOCCube、TutorialBank、Codecademy Dataset、LeetCode Student Submissions、APPS Dataset |
| 教育系统/产品 | InnoSpark、九章大模型、网易有道子曰、科大讯飞星火教育、CheggMate |

对这些条目，后续要比较模型时应先定义任务和指标。例如 Math23K/Ape210K 可做答案准确率，ASSISTments/EdNet 可做 AUC/ACC 的 KT 预测，MathDial/Bridge/SocraticLM 可做 tutor 决策和对话质量，FineWeb-Edu/Chinese FineWeb Edu 只能作为训练语料，不能单独作为评测结论。

## 覆盖性审计

已覆盖 `edubench.md` 中全部 7 个大类：

- 解题能力评测 Benchmark：通用学科 9 项、数学专项 10 项、代码专项 2 项。
- 教学能力评测 Benchmark：11 项。
- 知识追踪领域：10 项。
- 自动评分领域：5 项。
- 教育问答领域：8 项。
- 其他教育资源：18 项。
- 教育大模型系统：6 项。

需后续深挖的条目：

- **EduDial、IntrEx、QACP**：公开入口未提供完整模型榜单，建议后续下载论文或数据后补充。
- **K12Vista**：已从论文 PDF 文本中补充 Direct/Step-by-Step overall；若需要学科、年级、题型全维度表，建议再把 PDF 表格截图或表格 OCR 独立成 CSV。
- **国内产品系统**：多数公开页面是产品介绍，缺少可复现评测协议；建议统一放入 E-EVAL、EduEval、OmniEduBench、MathTutorBench、EssayJudge/SAS-Bench 等外部基准做二次评测。
