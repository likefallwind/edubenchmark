#!/usr/bin/env python3
"""Emit one README per benchmark under ``reports/eval/<benchmark>/README.md``.

The README sits next to the numbers, so whoever is about to quote a score reads
the medical chart first. It merges two things:

(a) what the benchmark is — condensed from ``doc/benchmark_profiles/<name>.md``
    (the human-readable survey, kept as-is and linked both ways) or, where no
    profile exists, written from the adapter source;
(b) what state the numbers are actually in — generated from the latest
    ``reports/eval/_audit/audit_*.jsonl``, bad news first.

Idempotent: rerun after every audit; it overwrites its own output and nothing
else. Never hand-edit the generated READMEs — edit this script.

Usage:
    python scripts/audit_eval_artifacts.py      # first, refresh the audit
    python scripts/build_eval_readmes.py
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
EVAL_ROOT = ROOT / "reports" / "eval"
AUDIT_DIR = EVAL_ROOT / "_audit"
MAPPING = ROOT / "reports" / "atomic_ability_rebenchmark_2026-07-08" / "02_benchmark_ability_mapping.jsonl"

# Anything below this line in an existing README is hand-written and survives
# regeneration untouched.
MARKER = "<!-- 以下为人工撰写内容，build_eval_readmes.py 不会覆盖 -->"

VERDICT_ZH = {
    "unusable": "**unusable**（分数是假的，必须重跑）",
    "caveat": "caveat（可用，但必须带着下面的保留意见一起引用）",
    "clean": "clean",
    "no_artifacts": "no_artifacts（目录在，产物没有）",
}

# --- (a) what each benchmark is -------------------------------------------
# ``profile`` links to doc/benchmark_profiles/<x>.md when one exists. The rest is
# condensed from that profile, the adapter source, and CLAUDE.md.
P: dict[str, dict[str, str]] = {
    "mmlu_pro": {
        "profile": "mmlu_pro",
        "one_liner": "MMLU 的高难升级版：10 选 1 学科知识题，测大学水平答题门槛。",
        "source": "TIGER-Lab/MMLU-Pro（公开镜像；TIGER-AI-Lab 那条路径是 gated）。",
        "data": "12,032 题，`fetch_eval_datasets.py --benchmark mmlu_pro`。",
        "scoring": "官方 `answer is (X)` 正则先抽，抽不到才退回抽取 LLM；精确匹配选项字母。规则为主，裁判只是兜底。",
        "adapter": "scripts/eval/benchmarks/mmlu_pro.py",
        "limits": "门槛题（foundation_gate），只证明会答题，不证明会教。",
    },
    "ceval": {
        "profile": "ceval",
        "one_liner": "中文 52 学科考试选择题，四个难度层。",
        "source": "ceval/ceval-exam。",
        "data": "val 分割 1,346 题（官方 test 不给答案）；每学科 5 条 dev 样例做 5-shot。",
        "scoring": "官方 5-shot answer-only 协议：**无抽取 LLM**，读回复首字母精确匹配，跟官方 `response[0] == answer` 一致。",
        "adapter": "scripts/eval/benchmarks/ceval.py",
        "limits": "门槛题；中文知识面，不测教学。",
    },
    "agieval": {
        "profile": "agieval",
        "one_liner": "人类标准化考试原题（高考/SAT/LSAT/法考），中英双语。",
        "source": "microsoft/AGIEval 仓库自带数据。",
        "data": "7,272 题（选择题 + 数学填空）。",
        "scoring": "选项字母按官方 `post_process.py` 解析，数学用官方 `math_equivalence.is_equiv`。规则判分，抽取 LLM 仅兜底。",
        "adapter": "scripts/eval/benchmarks/agieval.py",
        "limits": "门槛题。",
    },
    "olympiadbench": {
        "profile": "olympiadbench",
        "one_liner": "奥赛级数学/物理开放题，双语带图，门槛类里最难的一个。",
        "source": "Hothan/OlympiadBench（OE 配置，TP 证明题跳过）。",
        "data": "6,728 题；图片抽到 `olympiadbench/images/`。",
        "scoring": "prompt 与判分都移植官方仓库：`make_prompt` + sympy 符号判等 `AutoScoringJudge`。**需要 `antlr4-python3-runtime==4.11`**，跟 hydra-core 冲突。",
        "adapter": "scripts/eval/benchmarks/olympiadbench.py",
        "limits": "门槛题；符号判等偶有假阴。",
    },
    "mathvista": {
        "profile": "mathvista",
        "one_liner": "图文数学推理（图表/几何/函数图）。",
        "source": "MathVista 官方仓库。",
        "data": "1,000 题 testmini；图片需手动 `wget images.zip && unzip` 到 `sources/datasets/mathvista/data`。",
        "scoring": "移植官方 few-shot 抽取（`ext_ans.demo_prompt`）+ `normalize_extracted_answer` + 最近选项编辑距离。",
        "adapter": "scripts/eval/benchmarks/mathvista.py",
        "limits": "需要视觉模型（`MiniMax-M3`，不是 M2.7）。",
    },
    "ifeval": {
        "profile": "ifeval",
        "one_liner": "541 条带可机器验证硬约束的指令，官方规则代码判分——P01 的直接测量。",
        "source": "google-research IFEval（arXiv:2311.07911），官方 checker vendored。",
        "data": "`sources/datasets/ifeval/`，541 条；判分依赖 nltk/langdetect/immutabledict（在 miniconda python 里）。",
        "scoring": "**无裁判、无抽取 LLM**，直接对原始回复跑官方 checker。headline = prompt 级 strict accuracy。",
        "adapter": "scripts/eval/benchmarks/ifeval.py",
        "limits": "通用英文指令，不是教育语境。",
    },
    "eduguard_sata": {
        "profile": "eduguard_bench",
        "one_liner": "EduGuard P1 教学伤害全选题：知不知道什么算教学伤害。",
        "source": "github.com/YL1N/EduGuardBench。",
        "data": "2,635 条 × 中英双语 = 5,270。",
        "scoring": "**规则判分**，照官方 `run_p1_evaluation.py`：全选对 RFS=1，非空真子集 0.5，其余 0。无裁判。",
        "adapter": "scripts/eval/benchmarks/eduguard_bench.py",
        "limits": "测的是安全知识，不是安全行为。",
    },
    "eduguard_adversarial": {
        "profile": "eduguard_bench",
        "one_liner": "EduGuard P2 对抗安全：801 条越狱提示，测顶不顶得住诱导。",
        "source": "github.com/YL1N/EduGuardBench。",
        "data": "801 条。",
        "scoring": "两阶段 LLM-as-judge（移植 `run_p2_experiment.py`）：先判有害/无害，再判拒答质量；每阶段 BoN=3 多数票。裁判是 `--extractor-model`。报 ASR + 拒答质量分布。",
        "adapter": "scripts/eval/benchmarks/eduguard_bench.py",
        "limits": "裁判依赖强；裁判挂了会被算成“没拒答”，直接抬高 ASR（见健康状况）。",
    },
    "mrbench_judge": {
        "profile": "mrbench",
        "one_liner": "MRBench Step 1：被测模型**当裁判**，给 tutor 回复贴 8 维标签，跟人类金标比一致性。",
        "source": "kaushal0494/UnifyingAITutorEvaluation（NAACL 2025），`MRBench_V2.json`。",
        "data": "200 段对话 × 至多 9 个模型回复 × 维度 = 13,240 条。",
        "scoring": "被测模型自己出标签，本地跟人类金标比：每维 agreement + macro-F1 + Cohen's kappa。**没有第三方裁判**——unparsed 是被测模型的行为，不是管道故障。",
        "adapter": "scripts/eval/benchmarks/mrbench.py",
        "limits": "映射里是 `excluded_judge_task`（weight 0.0），只用来选裁判，不进能力雷达。",
    },
    "mrbench_tutor": {
        "profile": "mrbench",
        "one_liner": "MRBench Step 2：被测模型**生成** tutor 回复，固定裁判贴 8 维标签。",
        "source": "kaushal0494/UnifyingAITutorEvaluation（NAACL 2025），`MRBench_V2.json`。",
        "data": "200 段对话。",
        "scoring": "固定裁判 `MRBENCH_JUDGE_MODEL`（默认 MiniMax-M3，跟 `--extractor-model` 解耦）。headline = 教学通过率（Mistake_Identification / Providing_Guidance / Actionability 三个关键维度全 Yes）。",
        "adapter": "scripts/eval/benchmarks/mrbench.py",
        "limits": "通过率对裁判故障零容忍：任一关键维度 unparsed 就是 fail（见健康状况，这正是本次审计最严重的问题）。",
    },
    "bea2025_judge": {
        "profile": "bea2025",
        "one_liner": "BEA 2025 共享任务 Step 1：被测模型当裁判，给 dev 集 tutor 回复贴 4 维标签。",
        "source": "SIGEDU BEA 2025 官方任务 + `BEA_Shared_Task_2025_Datasets/mrbench_v3_devset.json`。",
        "data": "dev 集 9,904 条（(回复 × 维度) 一条）；test 标签官方隐藏。",
        "scoring": "跟人类标注比 exact / lenient accuracy + macro-F1 + kappa；`recommended_judge_score` = 4 维 exact macro-F1 均值。",
        "adapter": "scripts/eval/benchmarks/bea2025.py",
        "limits": "本地 dev 打分，**不等于官方榜**；映射里 weight 0.0。",
    },
    "bea2025_tutor": {
        "profile": "bea2025",
        "one_liner": "BEA 2025 Step 2：被测模型生成 tutor 回复，固定裁判贴 4 维标签。",
        "source": "SIGEDU BEA 2025 官方任务 + `BEA_Shared_Task_2025_Datasets/mrbench_v3_devset.json`。",
        "data": "dev 集 300 段对话。",
        "scoring": "固定裁判 `BEA2025_JUDGE_MODEL`/`JUDGE_MODEL`（默认 MiniMax-M3）。headline = 本地教学通过率（三个关键维度全 Yes）。",
        "adapter": "scripts/eval/benchmarks/bea2025.py",
        "limits": "不能宣称等价官方榜；跟 mrbench_tutor 同款裁判故障。",
    },
    "mathtutorbench_problem_solving": {
        "profile": "mathtutorbench",
        "one_liner": "MathTutorBench：会不会做题（GSM8K 风格，门槛项）。",
        "source": "MathTutorBench 官方仓库。", "data": "1,319 题。",
        "scoring": "数值精确匹配，抽取 LLM 仅兜底。",
        "adapter": "scripts/eval/benchmarks/mathtutorbench.py",
        "limits": "已接近天花板，区分不了模型。",
    },
    "mathtutorbench_solution_correctness": {
        "profile": "mathtutorbench",
        "one_liner": "MathTutorBench：判断学生解答对不对。",
        "source": "MathTutorBench 官方仓库。", "data": "1,002 条。",
        "scoring": "二分类精确匹配。",
        "adapter": "scripts/eval/benchmarks/mathtutorbench.py",
        "limits": "-",
    },
    "mathtutorbench_mistake_location": {
        "profile": "mathtutorbench",
        "one_liner": "MathTutorBench：定位学生错在哪一步。",
        "source": "MathTutorBench 官方仓库。", "data": "1,002 条。",
        "scoring": "分类精确匹配。",
        "adapter": "scripts/eval/benchmarks/mathtutorbench.py",
        "limits": "-",
    },
    "mathtutorbench_mistake_correction": {
        "profile": "mathtutorbench",
        "one_liner": "MathTutorBench：把学生的错解改对。",
        "source": "MathTutorBench 官方仓库。", "data": "1,002 条。",
        "scoring": "数值精确匹配。",
        "adapter": "scripts/eval/benchmarks/mathtutorbench.py",
        "limits": "-",
    },
    "mathtutorbench_socratic": {
        "profile": "mathtutorbench",
        "one_liner": "MathTutorBench：苏格拉底式提问（生成引导问题）。",
        "source": "MathTutorBench 官方仓库。", "data": "1,319 条。",
        "scoring": "官方指标 best-match SacreBLEU（0-1），规则判分。",
        "adapter": "scripts/eval/benchmarks/mathtutorbench.py",
        "limits": "BLEU 对措辞敏感，绝对值低是正常的，只做相对比较。",
    },
    "mathtutorbench_pedagogy": {
        "profile": "mathtutorbench",
        "one_liner": "MathTutorBench：教学质量胜率（对比金标 tutor 回复）。",
        "source": "MathTutorBench 官方仓库（LLM-as-judge 版胜率，替代论文的 GPU reward model）。", "data": "1,150 条。",
        "scoring": "LLM-as-judge 成对比较替代论文的 GPU reward model：A/B 两个顺序各投一票去位置偏差，win_score = 生成回复胜出比例。固定裁判 `MATHTUTORBENCH_JUDGE_MODEL`。",
        "adapter": "scripts/eval/benchmarks/mathtutorbench.py",
        "limits": "两票全失败 → win_score=None → **被当成输**（见健康状况）。",
    },
    "mathtutorbench_pedagogy_hard": {
        "profile": "mathtutorbench",
        "one_liner": "MathTutorBench：教学质量胜率，hard 变体。",
        "source": "MathTutorBench 官方仓库（LLM-as-judge 版胜率，替代论文的 GPU reward model）。", "data": "1,308 条。",
        "scoring": "同 pedagogy。",
        "adapter": "scripts/eval/benchmarks/mathtutorbench.py",
        "limits": "同 pedagogy。",
    },
    "mathtutorbench_scaffolding": {
        "profile": "mathtutorbench",
        "one_liner": "MathTutorBench：脚手架引导胜率——“会教”最核心的一项。",
        "source": "MathTutorBench 官方仓库（LLM-as-judge 版胜率，替代论文的 GPU reward model）。", "data": "1,150 条。",
        "scoring": "同 pedagogy（成对胜率）。",
        "adapter": "scripts/eval/benchmarks/mathtutorbench.py",
        "limits": "同 pedagogy；本次审计里裁判故障最集中的任务之一。",
    },
    "mathtutorbench_scaffolding_hard": {
        "profile": "mathtutorbench",
        "one_liner": "MathTutorBench：脚手架引导胜率，hard 变体。",
        "source": "MathTutorBench 官方仓库（LLM-as-judge 版胜率，替代论文的 GPU reward model）。", "data": "1,308 条。",
        "scoring": "同 pedagogy。",
        "adapter": "scripts/eval/benchmarks/mathtutorbench.py",
        "limits": "同 pedagogy。",
    },
    "mathtutorbench_judge_calibration": {
        "profile": "mathtutorbench",
        "one_liner": "MathTutorBench：裁判校准——被测模型在专家成对偏好上跟不跟得上人。",
        "source": "MathTutorBench 官方仓库。", "data": "成对样本，两个顺序各一条。",
        "scoring": "跟专家 positive 的一致率 + 位置一致性。被测模型即裁判。",
        "adapter": "scripts/eval/benchmarks/mathtutorbench.py",
        "limits": "选裁判用，不进能力雷达。",
    },
    "mmtutorbench": {
        "profile": "mmtutorbench",
        "one_liner": "视频关键帧数学辅导：看图 + 学生提问 → 结构化辅导回复。",
        "source": "Tangchiu/mmtutorbench，770 行 / 1,414 张关键帧。",
        "data": "`fetch_eval_datasets.py --benchmark mmtutorbench`。",
        "scoring": "固定 rubric 裁判 `MMTUTORBENCH_JUDGE_MODEL`（默认 MiniMax-M3）打 6 个二元维度，报 0-6 总分。",
        "adapter": "scripts/eval/benchmarks/mmtutorbench.py",
        "limits": "别默认跑全量 770；先 `LIMIT=5` 冒烟。",
    },
    "mmtutorbench_judge_calibration": {
        "profile": "mmtutorbench",
        "one_liner": "MMTutorBench 裁判校准——**只是个钩子**：公开 JSONL 没有逐题人工金标，所以它输出 status 而不是编分数。",
        "source": "Tangchiu/mmtutorbench。", "data": "无（没有人工金标）。",
        "scoring": "`extra_metrics.status = not_run`。",
        "adapter": "scripts/eval/benchmarks/mmtutorbench.py",
        "limits": "这是诚实的空钩子，不是故障。",
    },
    "eduillustrate": {
        "profile": "eduillustrate",
        "one_liner": "写 Manim 代码把解题过程画出来，渲染成功后裁判按 8 维（4 文本 + 4 视觉）打 0-5 分。",
        "source": "arXiv:2604.05005，本地生成器 `/home/likefallwind/code/EduIllustrate`。",
        "data": "benchmark.json 230 题（另有 5 题冒烟集）。",
        "scoring": "8 维 0-5 Likert，逐题几何平均，benchmark 级算术平均。**产物不走标准 harness**（没有 predictions/extractions，schema 自成一套）。",
        "adapter": "scripts/eval/build_eduillustrate_report.py",
        "limits": "裁判是替代 provider（MiniMax-M3 等），不是论文原用的 Gemini 3.0 Pro，**不可与论文榜比较**；渲染失败的题不送裁判、计 0，`overall_mean_judged_only` 有幸存者偏差，跨模型比较请用 `overall_mean_all_items`。",
    },
    "k12vista": {
        "profile": "k12vista",
        "one_liner": "3.3 万道中文 K12 图文学科题——P04（复杂多模态理解）的直接测量。",
        "source": "K12Vista。", "data": "尚未落地到本地产物。",
        "scoring": "裁判打分，`unparsed` 记 0。",
        "adapter": "scripts/eval/benchmarks/k12vista.py",
        "limits": "**一次都没跑过**，adapter 就绪、产物为空。",
    },
    "mooccube_prereq": {
        "profile": "mooccube",
        "one_liner": "拿学堂在线知识图谱的 905 条专家先修边当金标，自建先修选择 + 学习顺序排序题——P19 的直接测量。",
        "source": "MOOCCube（自建题）。", "data": "自建。",
        "scoring": "**100% 规则判分、零裁判**。",
        "adapter": "scripts/eval/benchmarks/mooccube_prereq.py",
        "limits": "只覆盖“知识结构”那一半路径规划；**目前没有任何跑完的产物**。",
    },
    "p07_selfcheck": {
        "profile": "p07_selfcheck",
        "one_liner": "先答题、再无提示地要求“重新检查”，分离“错改对”（真自查）与“对改错”（有害的自我怀疑）——P07 的直接测量。",
        "source": "自建，复用 P08 的题单代理（agieval/ceval/mmlu_pro/mtb_problem_solving）。",
        "data": "固定题单 `data/p08_calibration/item_list_v1.txt`，550 题。",
        "scoring": "第二轮在 `extract_answer` 里再调**被测模型本人**（`adapter.model_under_test`）。headline `score_10 = 10*[0.5*fix_rate + 0.5*(1-break_rate)]`，跟第一轮准确率解耦。",
        "adapter": "scripts/eval/benchmarks/p07_selfcheck.py",
        "limits": "第二轮撞限流会把整题从分母里剔掉（`n_round2_missing`），summary 照常出分——历史上就是这么翻的车。",
    },
    "p08_calibration": {
        "profile": "p08_selfbuilt",
        "one_liner": "答题时要求同时给 0-100 置信度，测“自信地教错”有多少——P08 的直接测量。",
        "source": "自建，题单 `data/p08_calibration/item_list_v1.txt`。", "data": "550 题。",
        "scoring": "delegate 判对错 + 解析置信度；报 ECE / CWR（高置信错答率）等。置信度解析不出来的题从校准指标里剔除并单独报 `confidence_unparsed_rate`（>10% 会自动打警告）。",
        "adapter": "scripts/eval/benchmarks/p08_calibration.py",
        "limits": "-",
    },
    "p08_abstention": {
        "profile": "p08_selfbuilt",
        "one_liner": "UMWP 不可答数学题 + 可答对照，测“不会的题敢不敢说不会”。",
        "source": "UMWP（Yuki-Asuuna/UMWP）。", "data": "500 题（250 不可答 + 250 可答）。",
        "scoring": "**规则判分**：不可答题上弃答算对，可答题上答对算对。",
        "adapter": "scripts/eval/benchmarks/p08_abstention.py",
        "limits": "-",
    },
    "edubench": {
        "profile": "edubench",
        "one_liner": "英文教育场景生成，12 维裁判打 0-10 分——当前证据体系里最大的分数来源。",
        "source": "同事完整跑批由 `scripts/import_edubench_results.py` 导入；原 prompt/item_id 现由 harness adapter 复用。",
        "data": "可比题单 3,797 题（IP 1253 / QG 1266 / TMG 578 / PLS 448 / PCC 252），现有 11 模型；不含 EC/QA/AG/ES。",
        "scoring": "固定 deepseek-v3.2 裁判按官方 12 维打连续分（0-10）；总体分是 12 维均值，场景分只平均官方动态分配给该任务的维度；不是准确率。",
        "adapter": "scripts/eval/benchmarks/edubench.py（原始外部结果仍由 scripts/import_edubench_results.py 导入）",
        "limits": "同事精确 judge prompt 未随产物交付，adapter 依据论文 12 维定义重建，故新旧结果不是逐字节协议复放。换裁判实验（`_judge_swap`）还显示：只有支持类簇（个性化/激励/高阶思维）对裁判稳健；**错误识别维度在这些任务上是裁判噪声，不可用于映射**。",
    },
    "longtutor_evidence": {
        "profile": None,
        "one_liner": "LongTutor 任务一：跨 7 天以上的学生历史里做单记录抽取 / 跨 session 推理 / 幻觉检查。",
        "source": "LongTutor 上游发布（无 LICENSE，勿再分发数据）；见 AGENTS.md 的 LongTutor 段。",
        "data": "`prepare_longtutor.py` 用上游 feature 代码重建 `history_features_lastq_scale.jsonl` 并校验 stable-key join；人工金标用 `human_an_updated.jsonl`（1,000 行），3,003 条问题。",
        "scoring": "先做归一化精确匹配，不中才叫裁判判语义等价（走 `--extractor-model` 客户端）。主指标：按 query 类型分的语义正确率。",
        "adapter": "scripts/eval/benchmarks/longtutor.py",
        "limits": "**离线长历史重放，不代表真实长期学习增益**；三个任务不许平均成一个分。",
    },
    "longtutor_diagnosis": {
        "profile": None,
        "one_liner": "LongTutor 任务二：根据长历史把当前错误归到四类知识状态。",
        "source": "LongTutor 上游发布（无 LICENSE，勿再分发数据）；见 AGENTS.md 的 LongTutor 段。",
        "data": "1,001 条，`prepare_longtutor.py` 重建历史特征后与人工金标 join。",
        "scoring": "**纯本地字符串匹配**，无裁判；主指标 Macro-F1，accuracy 辅助。回复里匹配到 0 个或 >1 个标签记 `NO_LABEL`。",
        "adapter": "scripts/eval/benchmarks/longtutor.py",
        "limits": "离线长历史重放，不代表真实长期学习增益；三个 LongTutor 任务不许平均成一个分。",
    },
    "longtutor_teaching": {
        "profile": None,
        "one_liner": "LongTutor 任务三：生成用到具体历史证据的自适应教学反馈，裁判按四维 1-5 分打分。",
        "source": "LongTutor 上游发布（无 LICENSE，勿再分发数据）；见 AGENTS.md 的 LongTutor 段。", "data": "1,001 条。",
        "scoring": "裁判（走 `--extractor-model` 客户端）返回 JSON，四维：history_utilization / strategy_alignment / coherence / appropriateness。",
        "adapter": "scripts/eval/benchmarks/longtutor.py",
        "limits": "**当前打分函数是坏的**（见健康状况），现有分数全 0，没有意义。",
    },
}

# --- known bugs, located to the function ----------------------------------
BUGS: dict[str, list[dict[str, str]]] = {
    "mrbench_tutor": [
        {
            "title": "裁判调用失败被当成“裁判说读不懂”，缓存下来，算成教学不通过",
            "where": "`scripts/eval/benchmarks/mrbench.py` → `MRBenchTutorAdapter._judge_one`（约 468-484 行）",
            "cause": (
                "`except Exception: pass` 把三次重试全部吞掉，最后 `return \"unparsed\"`——"
                "\"调用失败\" 和 \"裁判回了但归一不了\" 混成同一个值。这个 unparsed 写进 "
                "`extractions.jsonl`，行里**不带 `error` 字段**；而 `runner.py` 的 `run_extractions` "
                "缓存过滤器（约 300-306 行）只跳过带 `error` 的行，于是这条失败被当成**成功缓存**，"
                "重跑也不会重试。`score()` 要求三个关键维度全为 \"Yes\"，unparsed → fail → "
                "教学通过率凭空变低。"
            ),
            "fix": (
                "1) `_judge_one` 区分两种失败：调用异常返回/抛出 `judge_call_failed` sentinel，"
                "跟 `unparsed` 分开；2) `extract_answer` 只要有一个维度是 call_failed 就 `raise`，"
                "让 runner 写带 `error` 的行——这样既不缓存也能重试；3) `extra_summary` 把 unparsed "
                "从通过率分母里剔除并单独报 `n_unparsed`，别让它默默变成 fail。"
            ),
        }
    ],
    "bea2025_tutor": [
        {
            "title": "同款：裁判失败 → unparsed → 关键维度不通过",
            "where": "`scripts/eval/benchmarks/bea2025.py` → 模块级 `_judge_one`（约 213-222 行）",
            "cause": "跟 mrbench_tutor 一模一样的 `except Exception: pass` + `return \"unparsed\"`，同一条缓存路径。",
            "fix": "同 mrbench_tutor；两处最好抽成一个共用的 judge 调用工具函数，一次改完。",
        }
    ],
    "mathtutorbench_pedagogy": [
        {
            "title": "成对投票全失败 → win_score=None → 直接算输",
            "where": "`scripts/eval/benchmarks/mathtutorbench.py` → `_WinRateBase._vote_letter`（约 739-751 行）",
            "cause": (
                "`except Exception: pass`，三次重试后 `return None`。两个顺序的票都是 None 时 "
                "`win_score = None`，`score()` 里 `correct = ws is not None and ws > 0.5` → **False**，"
                "即裁判挂掉等于生成回复输给金标。同样不带 `error`，同样被缓存。"
                "另外只有一票回来时，位置去偏（A/B 交换）失效，win_score 变成单票的 0/1，也没被标出来。"
            ),
            "fix": (
                "1) 两票都失败时抛异常，让 runner 记 `error` 行；2) `score()` 遇 `win_score is None` "
                "返回非 scored 状态而不是 correct=False；3) 单票的项在 `extra_summary` 里单列 "
                "`n_partial_vote`，胜率分母里要么剔除、要么显式标注。"
            ),
        }
    ],
    "eduguard_adversarial": [
        {
            "title": "裁判异常行被打分成 judge_error，而 judge_error 计入“没拒答”，抬高 ASR",
            "where": "`scripts/eval/runner.py` → `run_scoring`（约 388-403 行）+ `eduguard_bench.py` → `score()`",
            "cause": (
                "EduGuard 的 `_vote` 是**会抛异常**的（好设计），runner 于是写下一行带 `error` 的 extraction。"
                "但 `run_scoring` 只判断 `ext is None`，带 `error` 的行照样进 `adapter.score(\"\")` → "
                "`final_label = judge_error` → `correct=False` → 在 ASR 口径里等于**攻击成功**。"
            ),
            "fix": "`run_scoring` 里加一条：`if ext.get(\"error\"): row[\"score_status\"] = \"extraction_error\"; continue`。这一条能同时救掉所有裁判类 benchmark。",
        }
    ],
    "longtutor_teaching": [
        {
            "title": "打分函数是死代码——四维分永远是 0",
            "where": "`scripts/eval/benchmarks/longtutor.py` → `_json_from_text`（约 84-96 行）",
            "cause": (
                "函数体只有 `match = re.search(...)` 和 `if not match: return None`；真正的 "
                "`try: return json.loads(match.group(0))` 掉到了**下一个函数 `_normalize_answer` 的 "
                "`return` 之后**，是永远执行不到的死代码。于是匹配成功时 `_json_from_text` 直接落到函数尾部、"
                "返回 `None` → `score()` 里 `parsed = {}` → 四维全部 clamp 成 0 → `correct=False`。"
                "裁判其实返回了合法 JSON（`extracted` 字段里看得到 ```json {...}```），分数却全 0。"
            ),
            "fix": "把 `try/json.loads/except json.JSONDecodeError` 挪回 `_json_from_text` 里；同时给 `extra_summary` 加一个 `n_unparsed_judgements`，全 0 这种事下次要能自己叫。",
        }
    ],
    "p07_selfcheck": [
        {
            "title": "第二轮撞限流 → r2_error 写进缓存 → 该题从指标分母里消失",
            "where": "`scripts/eval/benchmarks/p07_selfcheck.py` → `extract_answer`（约 112-131 行）",
            "cause": (
                "三次重试后把 `last_error` 塞进 `r2_error` 字段，`r2_response` 留空；extraction 行**不带 "
                "`error`**，于是被缓存。`score()` 把这题标 `r2_missing`，`extra_summary` 从 graded 里剔除，"
                "summary 照常算出 `score_10`——分母悄悄变小了。字段 `n_round2_missing` 里能看出来，但没人会去看。"
            ),
            "fix": "`extract_answer` 在 `r2_response` 为空时直接 `raise`，让 runner 记 error 行、下次重跑；`n_round2_missing > 0` 时在 summary 里写一条显式的 `warning` 字段。",
        }
    ],
}

QUOTA_NOTE = (
    "上游配额/限流打挂大批题目后，summary 仍在**幸存样本**上照常出分。"
    "这类 run 的分数没有“错”，但它测的是一个自选样本，不能跟全量 run 放在一张表里比。"
)


def load_audit() -> tuple[list[dict[str, Any]], str]:
    files = sorted(AUDIT_DIR.glob("audit_*.jsonl"))
    if not files:
        raise SystemExit("no audit file; run scripts/audit_eval_artifacts.py first")
    latest = files[-1]
    rows = [json.loads(line) for line in latest.read_text(encoding="utf-8").splitlines() if line.strip()]
    return rows, latest.stem.replace("audit_", "")


def load_mapping() -> dict[str, list[dict[str, Any]]]:
    out: dict[str, list[dict[str, Any]]] = {}
    if not MAPPING.exists():
        return out
    for line in MAPPING.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        out.setdefault(row["benchmark_id"], []).append(row)
    return out


# The audit JSONL is tooling output and stays in English; the READMEs are for
# readers, so the same structured fields are re-rendered in Chinese here.
FAIL_ZH: dict[str, str] = {
    "mrbench_tutor": "关键维度 unparsed，被当成教学不通过",
    "bea2025_tutor": "关键维度 unparsed，被当成教学不通过",
    "mathtutorbench_pedagogy": "两次成对投票都失败，win_score=None，被当成输",
    "mathtutorbench_pedagogy_hard": "两次成对投票都失败，win_score=None，被当成输",
    "mathtutorbench_scaffolding": "两次成对投票都失败，win_score=None，被当成输",
    "mathtutorbench_scaffolding_hard": "两次成对投票都失败，win_score=None，被当成输",
    "eduguard_adversarial": "judge_error，在 ASR 口径里等于攻击成功",
    "mmtutorbench": "rubric 解析不全，总分记 None",
    "longtutor_teaching": "裁判分解析恒为 0（打分函数是死代码）",
    "longtutor_diagnosis": "回复匹配到 0 个或多个诊断标签",
    "longtutor_evidence": "抽取为空，记为答错",
    "p07_selfcheck": "第二轮没回来，该题被踢出指标分母",
    "mrbench_judge": "被测模型自己给不出可解析标签（模型行为，非管道故障）",
    "bea2025_judge": "被测模型自己给不出可解析标签（模型行为，非管道故障）",
    "mathtutorbench_judge_calibration": "被测模型没给出 A/B 选择（模型行为）",
    "p08_calibration": "置信度没解析出来，该题被踢出校准指标",
    "eduillustrate": "渲染失败、没送裁判（headline 有幸存者偏差）",
}


# What the ``headline`` column actually is, per benchmark — an unlabelled 0.96
# next to "adversarial safety" reads as a disaster or a triumph depending on
# whether it is ASR or refusal rate, so say which.
HEADLINE_LABEL: dict[str, str] = {
    "eduguard_adversarial": "拒答率（accuracy，correct = 拒答成功）；**ASR = 1 − 该值**",
    "eduguard_sata": "RFS（全对 1 / 非空真子集 0.5 / 其余 0）",
    "mrbench_tutor": "教学通过率（三个关键维度全 Yes）",
    "bea2025_tutor": "本地教学通过率（三个关键维度全 Yes）",
    "bea2025_judge": "recommended_judge_score = 四维 exact macro-F1 均值",
    "mrbench_judge": "跟人类金标的整体一致率",
    "p07_selfcheck": "score_10 = 10×[0.5×fix_rate + 0.5×(1−break_rate)]（0-10）",
    "mmtutorbench": "六维 rubric 平均总分（0-6）",
    "longtutor_teaching": "四维裁判分均值（1-5）",
    "eduillustrate": "overall_mean_judged_only（0-5，**有幸存者偏差**）",
    "edubench": "12 维裁判总分均值（0-10）",
    "mathtutorbench_socratic": "best-match SacreBLEU（0-1）",
    "mathtutorbench_pedagogy": "胜率（对金标 tutor 回复）",
    "mathtutorbench_pedagogy_hard": "胜率（对金标 tutor 回复）",
    "mathtutorbench_scaffolding": "胜率（对金标 tutor 回复）",
    "mathtutorbench_scaffolding_hard": "胜率（对金标 tutor 回复）",
}


def zh_notes(rec: dict[str, Any]) -> str:
    """Re-render the audit's structured findings as Chinese notes."""
    notes: list[str] = []
    if rec.get("degenerate_headline"):
        notes.append("**headline 本身无效**（打分器坏了，不是模型的问题）")
    fail = float(rec.get("judge_fail_rate") or 0)
    if fail >= 0.005:
        notes.append(f"{fail:.1%} 的题命中失败标记：{FAIL_ZH.get(rec['benchmark'], '判分/抽取失败')}")
    ns = float(rec.get("not_scored_rate") or 0)
    if ns >= 0.02:
        notes.append(f"{ns:.1%} 的题没进判分（分数建立在 {rec.get('n_graded')}/{rec.get('n_expected')} 的残缺样本上）")
    pe = float(rec.get("pred_error_rate") or 0)
    if pe >= 0.02:
        notes.append(f"{pe:.1%} 的答题请求报错（上游限流/配额/参数错误）")
    ee = float(rec.get("ext_error_rate") or 0)
    if ee >= 0.02:
        notes.append(f"{ee:.1%} 的抽取/判分行带 error")
    gap = float(rec.get("worst_coverage_gap") or 0)
    if gap >= 0.02:
        notes.append(f"产物数量对不上，最大缺口 {gap:.1%}")
    if rec.get("stale_summary"):
        notes.append("summary.json 比产物旧：盘上的分数跟盘上的数据对不上")
    if rec.get("in_progress"):
        notes.append("一小时内还在写盘，疑似仍在跑，当前 summary 只是中间值")
    if rec.get("variance_restricted"):
        notes.append(
            f"variance_restricted（{'+'.join(rec.get('variance_flags') or [])}）："
            f"跨模型均值 {rec.get('cross_model_mean')} / 标准差 {rec.get('cross_model_sd')}"
        )
    if rec.get("n_expected") and int(rec["n_expected"]) < 20:
        notes.append(f"冒烟样本（n={rec['n_expected']}），只能验管道，不能当分数")
    if rec["verdict"] == "no_artifacts":
        notes.append("；".join(rec["findings"]) or "没有产物")
    return "；".join(notes) or "—"


def fmt_headline(rec: dict[str, Any]) -> str:
    value = rec.get("headline")
    if isinstance(value, float):
        return f"{value:.4f}"
    if isinstance(value, int):
        return str(value)
    return "—"


def render(benchmark: str, runs: list[dict[str, Any]], mapping: dict[str, list[dict[str, Any]]], stamp: str) -> str:
    meta = P.get(benchmark, {})
    profile = meta.get("profile")
    profile_link = (
        f"[`doc/benchmark_profiles/{profile}.md`](../../../doc/benchmark_profiles/{profile}.md)"
        if profile
        else "（暂无档案；本文件的“这个评测是什么”一节即是权威描述，事实来源是 adapter 源码与 AGENTS.md）"
    )
    counts = {v: sum(1 for r in runs if r["verdict"] == v) for v in ("unusable", "caveat", "clean", "no_artifacts")}
    order = {"unusable": 0, "caveat": 1, "no_artifacts": 2, "clean": 3}
    ranked = sorted(runs, key=lambda r: (order[r["verdict"]], -float(r.get("judge_fail_rate") or 0), r["model"]))

    lines = [
        f"# {benchmark} — 评测产物说明",
        "",
        f"> 由 `scripts/build_eval_readmes.py` 生成（审计快照 `_audit/audit_{stamp}.jsonl`）。**不要手改**：改脚本后重跑。",
        f"> 综述档案（这个 benchmark 是什么，给人读）：{profile_link}",
        "> 本文件是给“要用这个分数的人”读的操作性病历：**分数能不能用、哪里坏了、要不要重跑**。",
        "",
        "## 一、健康状况（坏消息在前）",
        "",
    ]

    if counts["unusable"]:
        lines += [
            f"**这个 benchmark 下有 {counts['unusable']} 个 run 的分数不可用（unusable）。**"
            " 在重跑之前，不要把它们写进任何报告、聚合或映射裁决。",
            "",
        ]
    elif counts["caveat"]:
        lines += [f"没有不可用的 run，但有 {counts['caveat']} 个带保留意见（caveat），引用时必须一并写出。", ""]
    elif counts["no_artifacts"] and not counts["clean"]:
        lines += ["**这个 benchmark 一次都没跑出产物。**", ""]
    else:
        lines += ["全部 run 干净。", ""]

    lines += [
        f"headline 口径：{HEADLINE_LABEL.get(benchmark, '准确率（accuracy）')}。",
        "",
        "| 模型 | headline | 审计判决 | 判分/抽取失败率 | 未判分率 | 说明 |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for rec in ranked:
        lines.append(
            f"| `{rec['model']}` | {fmt_headline(rec)} | {VERDICT_ZH[rec['verdict']]} | "
            f"{float(rec.get('judge_fail_rate') or 0):.1%} | {float(rec.get('not_scored_rate') or 0):.1%} | "
            f"{zh_notes(rec).replace('|', '/')} |"
        )
    lines.append("")

    bugs = BUGS.get(benchmark) or []
    # Sibling benchmarks share the win-rate bug; point at the one write-up.
    if benchmark in ("mathtutorbench_pedagogy_hard", "mathtutorbench_scaffolding", "mathtutorbench_scaffolding_hard"):
        bugs = BUGS["mathtutorbench_pedagogy"]
    if bugs:
        lines += ["### 已定位的 bug（根因 + 修法）", ""]
        for bug in bugs:
            lines += [
                f"**{bug['title']}**",
                "",
                f"- 位置：{bug['where']}",
                f"- 根因：{bug['cause']}",
                f"- 建议修法：{bug['fix']}",
                "",
            ]
        lines += [
            "> 本次审计**不改 adapter 代码**（那是下一步）。修完之后，受影响的 run 必须删掉 "
            "`extractions.jsonl` 里的坏行（或整个 extractions.jsonl）再重跑 —— 只跑 `--score-only` "
            "没用，坏值已经被缓存进去了。",
            "",
        ]

    quota_runs = [r for r in runs if float(r.get("not_scored_rate") or 0) >= 0.02]
    if quota_runs:
        lines += [
            "### 样本残缺的 run",
            "",
            QUOTA_NOTE,
            "",
        ]
        for rec in quota_runs:
            lines.append(
                f"- `{rec['model']}`：只有 {rec.get('n_graded')} / {rec.get('n_expected')} 题进入判分"
                f"（未判分 {float(rec.get('not_scored_rate') or 0):.1%}）。"
            )
        lines.append("")

    if any(r.get("variance_restricted") for r in runs):
        rec = next(r for r in runs if r.get("variance_restricted"))
        lines += [
            "### 区分度",
            "",
            f"`variance_restricted`（{'+'.join(rec.get('variance_flags') or [])}）："
            f"跨 {len([r for r in runs if isinstance(r.get('headline'), (int, float))])} 个模型的 headline "
            f"均值 {rec.get('cross_model_mean')}、标准差 {rec.get('cross_model_sd')}。"
            "口径与 13 号映射效度检查一致：**区分度受限的格子不得驱动映射裁决**。",
            "",
        ]

    # --- section 2: what this benchmark is ---------------------------------
    lines += ["## 二、这个评测是什么", ""]
    if not meta:
        lines += ["（缺档案且缺条目，请补 `scripts/build_eval_readmes.py` 里的 `P` 字典。）", ""]
    else:
        lines += [
            f"**一句话**：{meta['one_liner']}",
            "",
            f"- **出处**：{meta['source']}",
            f"- **数据**：{meta['data']}",
            f"- **任务与判分**：{meta['scoring']}",
            f"- **adapter**：`{meta['adapter']}`",
            f"- **局限**：{meta['limits']}",
            "",
            "**怎么用**：",
            "",
            "```bash",
            f"MODEL=<model> ./scripts/run_eval.sh {benchmark}",
            f"# 或：python scripts/eval_benchmark.py --benchmark {benchmark} --model <model> --limit 0",
            "```",
            "",
        ]

    rows = mapping.get(benchmark) or []
    lines += ["## 三、当前映射（M3 裁决相关）", ""]
    if not rows:
        lines += [
            "`reports/atomic_ability_rebenchmark_2026-07-08/02_benchmark_ability_mapping.jsonl` 里没有这个 "
            "benchmark 的条目——它当前**不进能力雷达**。",
            "",
        ]
    else:
        lines += ["| evidence_tier | benchmark_weight | 能力（P:权重） |", "| --- | --- | --- |"]
        for row in rows:
            abilities = "、".join(f"{a['p_code']} {a['p_name']} ({a['weight']})" for a in row["abilities"])
            lines.append(f"| {row.get('evidence_tier')} | {row.get('default_benchmark_weight')} | {abilities} |")
        lines.append("")
        if counts["unusable"]:
            ps = sorted({a["p_code"] for row in rows for a in row["abilities"]})
            lines += [
                f"**这些 P 的证据因此受污染：{'、'.join(ps)}**。裁决前先看 "
                "[`doc/eval_artifact_audit_2026-07-14.md`](../../../doc/eval_artifact_audit_2026-07-14.md)。",
                "",
            ]

    lines += [
        "---",
        "",
        f"审计脚本：`python scripts/audit_eval_artifacts.py --benchmark {benchmark} --verbose`（离线、幂等、有 unusable 时退出码非 0）。",
    ]
    return "\n".join(lines) + "\n"


def preserved_tail(path: Path) -> str:
    """Everything a human wrote in this README, which we must not destroy.

    Some benchmarks already had a hand-written README (EduIllustrate's
    judged-only-vs-all-230 warning, LongTutor's judge-provenance notes). Those
    are worth more than anything generated here, so on the first pass they are
    migrated below the marker, and on every later pass they are read back and
    re-appended verbatim.
    """
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8")
    if MARKER in text:
        return text.split(MARKER, 1)[1]
    if text.lstrip().startswith("# ") and "scripts/build_eval_readmes.py` 生成" not in text:
        # A pre-existing hand-written README: demote its title and keep the body.
        return "\n\n" + text.strip() + "\n"
    return ""


def main() -> None:
    records, stamp = load_audit()
    mapping = load_mapping()
    by_bench: dict[str, list[dict[str, Any]]] = {}
    for rec in records:
        by_bench.setdefault(rec["benchmark"], []).append(rec)

    for benchmark, runs in sorted(by_bench.items()):
        out = EVAL_ROOT / benchmark / "README.md"
        out.parent.mkdir(parents=True, exist_ok=True)
        tail = preserved_tail(out).strip()
        body = render(benchmark, runs, mapping, stamp)
        if tail:
            body += f"\n{MARKER}\n\n{tail}\n"
        out.write_text(body, encoding="utf-8")
        print(f"wrote {out.relative_to(ROOT)} ({len(runs)} runs){' +手写段' if tail.strip() else ''}")


if __name__ == "__main__":
    main()
