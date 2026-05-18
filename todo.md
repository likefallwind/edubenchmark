## 更挑战性的目标：

## AutoEDU Benchmark: 可执行方案

### 一、短期执行计划（1周内可完成）

目标：建立初步可运行的 AutoEDU 核心评测体系（Core EDU Eval），确保已有 benchmark 入库、分类、初步校准和模型初测。

#### 1. Benchmark 收集与入库(done)

* 收集现有教育 AI benchmark（EduBench、TutorBench、K-12EduBench、作文批改等）。
* 统一格式化数据：题目、能力维度、任务类型、学段、学科、评分方式、rubric、许可证、语言。
* 建立 benchmark registry，记录 metadata 和状态标记（core、diagnostic、experimental、retired）。

#### 2. 初步能力分类与题型划分(done)

* 使用 LLM 对 benchmark 项目进行能力维度映射（数学、语言、批改、教学设计、学生支持等）。
* 人类专家抽样校验 LLM 分类准确性，保证分类可靠性。

#### 3. Benchmark 和题目质量校准

* 按照教育有效性、评分可靠性、复现性、难度、区分度、冗余度、污染风险对 benchmark 和题目打分。
* 删除或标记明显不靠谱的题目。

#### 4. 核心评测（Core EDU Eval）搭建

* 从高质量题目中挑选 anchor items，覆盖关键教育能力维度。
* 选定参考模型集合（通用强模型、开源模型、教育微调模型）进行初测，记录 item 的难度、饱和度和区分度。

#### 5. 测试系统搭建与初步报告

* 实现基础评测流程：模型输入题目 → 评测 → 输出能力分布。
* 生成初步能力画像，保证短期内可以运行 end-to-end 流程。

### 二、长期执行计划（1个月内可完成）

目标：扩展 AutoEDU 为完整动态 adaptive benchmark 系统，支持 human-in-the-loop、动态题目更新与权重管理。

#### 1. Adaptive Evaluation Engine 开发

* 根据模型表现动态抽题，弱模型多测基础题，强模型抽高难度题。
* 实现题目采样权重调整机制：当题目饱和且区分度低时，降低采样权重；保留回归测试。
* 与 IRT / CAT 模型结合，实现 item-level 动态选择。

#### 2. Human-in-the-Loop Challenge 流程

* 搭建教师/学生/教育专家提交 challenge task 的入口。
* 将 challenge task 标注能力维度、难度和教育情境。
* 将 human challenge task 融入 adaptive evaluation，发现模型弱点。

#### 3. 新 Benchmark 动态接入与发现机制

* 建立流程：新 benchmark → 分类 → reference model 测试 → difficulty/discrimination/saturation → anchor calibration → Core / Live / Diagnostic 分配。
* 引入新 benchmark 发现机制：持续监控教育领域新数据、教材更新、教师/学生提交的 challenge task，自动识别潜在新 benchmark 并纳入评测流程。
* 确保历史模型可比性与新 benchmark 融合。

#### 4. 题目生命周期管理

* 定期检查所有题目状态（Active、Saturating、Saturated、Retired、Challenge、Anchor）。
* 自动调整采样、权重和 retirement。

#### 5. Dashboard 与报告系统

* 可视化能力画像、题目饱和度、benchmark 覆盖度、模型能力分布。
* 输出 Core Score、Adaptive Score、Diagnostic Profile。
* 支持版本化管理（Core-v1.0、Live-2026Q2 等）。

#### 6. 系统验证与优化

* 运行 reference models 对全量题目，评估 adaptive 流程精度与效率。
* 通过 human-in-the-loop 测试 challenge task，验证弱点发现能力。
* 调整参数、anchor items、权重策略，确保能力估计稳定。

#### 7. 文档与流程标准化

* 完成 AutoEDU 文档规范：benchmark registry schema、item calibration 流程、adaptive evaluation algorithm、human challenge process、dynamic update rules。
* 确保系统可复制、可扩展，支撑后续新 benchmark、模型、能力维度扩展。
