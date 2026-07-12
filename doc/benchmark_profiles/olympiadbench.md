# OlympiadBench

**一句话**：奥林匹克竞赛级数学/物理开放题（非选择题），双语带图，是当前门槛类里最难、离饱和最远的一个。

## 出处与背景

- OpenBMB / 清华，2024（ACL 2024）；https://github.com/OpenBMB/OlympiadBench
- 动机：常规考试题对强模型饱和，用奥赛题（IMO/IPhO 级别）保持区分度，且带完整推理过程标注。

## 数据

- 全集 8,476 题，数学+物理，中英双语，部分带图（多模态）。
- 本仓库只用 **OE（开放式作答）配置**，TP（证明题）配置跳过（无法自动判分）；图片抽取到 `olympiadbench/images/`。
- 获取：`fetch_eval_datasets.py --benchmark olympiadbench`（HF `Hothan/OlympiadBench`）。

## 任务与判分

- 开放式作答，答案是数值/表达式/区间。
- 判分移植官方 repo：`make_prompt` 构造提示，sympy 符号等价的 `AutoScoringJudge` 判对错——**需要 `antlr4-python3-runtime==4.11`**（与 hydra-core 的 4.9 依赖冲突，必要时独立 venv）。

## 在本仓库怎么用

- adapter `scripts/eval/benchmarks/olympiadbench.py`；多模态题需要视觉模型。

## 局限与注意

- **区分度（13 号实测）**：n=2，均分 7.26，标准差 0.14——没天花板问题，但共同模型太少，什么都推不出来。**补模型时优先补它**（门槛类里唯一有区分度潜力的）。
- 竞赛真题，污染风险存在但比普通考试题低（解题过程难背）。

## 当前映射

- P06 0.55 / P05 0.25 / P03 0.20；foundation_gate。
- 构念核对：P03 挂载属于"解题式图像理解"子方向（R5 拆分后归入该 facet）。
