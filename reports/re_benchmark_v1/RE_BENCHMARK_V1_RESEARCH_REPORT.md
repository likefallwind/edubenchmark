# RE_BENCHMARK_V1 研究报告

## Executive Summary

RE_BENCHMARK_V1 作为研究版方案成立：它把教育模型评测拆成 C1 学科解题、C2 教学辅导、C3 学情建模、C4 作答评价、C5 教育安全五类，并明确区分通用能力、教学行为、评分可靠性、学习日志 protocol 和安全边界。当前版本的价值是形成可讨论、可初跑、可说明缺口的能力画像；边界是不能声称全量、生产级、或跨模态统一总分。

MiniMax smoke test 只作为第一轮模型画像：自动题可算 exact match，开放教学/安全题只做 qualitative reading。C1/C4/C5 有较强本地可运行基础；C2 的 TutorBench/Pedagogy 仍受数据可得性限制；C3 主要是 protocol，不适合直接并入 LLM prompt 分数。

## Benchmark Coverage

研究 pilot 共 142 条记录。本地直接可用 benchmark 包括 AGIEval、MMLU proxy、MathVista metadata、EduBench、EduVisBench、MathTutorBench、EduEval Essay_Scoring、EduGuard-Bench。Proxy 项必须单独标注；EdNet、ASSISTments、DAiSEE 属 protocol 或外部数据任务。

## Model Findings

自动题仅报告自动评分子集，不跨 C1-C5 求平均。教学类开放题和安全类样例以成功/失败案例描述为主，避免把未校准的 LLM judge 当成金标准。

## Methodological Risks

- 数据污染：MMLU/AGIEval 等公开题可能进入训练语料。

- Proxy 失真：MMLU 不是 MMLU-Pro，EduEval Essay_Scoring 不是 ASAP。

- Judge 不稳定：TutorBench、MathTutorBench、EduBench、EduGuard 需要人审或双模型 judge。

- 本土化偏差：中文教育场景与国际 benchmark 分布不同。

- 模态不可合并：KT、视频、代码执行、多模态视觉与文本 LLM prompt 不能简单平均。

## Conclusion

v1 应输出能力画像而非排行榜总分。下一步优先补真实教学辅导数据、中文本地教育安全、作文/短答评分数据，以及 human rubric 或双模型 judge。视频、多模态、代码执行和全量 KT 在 v2 后置。
