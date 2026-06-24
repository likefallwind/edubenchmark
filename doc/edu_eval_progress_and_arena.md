# AI-教育评测：进度、能力雷达图与评测场

> 本文是 `doc/priority_benchmark_plan.md`（优先级计划）和 `doc/benchmark_atomic_ability_matrix.md`（原子能力矩阵）的执行侧补充。
> 计划回答"测什么、按什么优先级测"；本文回答"现在测到哪了、下一步怎么从结果得到结论、最终做成什么产品形态"。

---

## 一、当前进度

状态记号：✅ 已完成 · 🔄 在测 · ⏸ 暂缓（P2，按需补 1–2 个模型） · ❌ 无公开数据

### 1.1 第一轮最小组合（计划第 96 节的 7 项）

| 顺序 | Benchmark | 大类 / 原子能力 | 目的 | 状态 |
| --- | --- | --- | --- | --- |
| 1 | SAS-Bench | C4 评 · D11 短答/分步评分 | "评"的核心评分/诊断画像 | ✅ 完成 |
| 2 | Pedagogy Benchmark | C2 教 · D14 教学法知识 | 补齐教师专业知识底座 | ✅ 完成 |
| 3 | EduBench（选定子任务） | C2/C3 教·学 · D12/D14/D15 | 开放式教学设计与个性化支持 | ✅ 完成 |
| 4 | TutorBench | C2 教 · D13 苏格拉底引导 | 师生互动、启发式而非直接给答案 | ✅ 完成 |
| 5 | ~~EduVisBench~~ → **EduIllustrate** | C2 教 · D22 教学可视化生成 | 多模态教育图表/板书理解与生成 | 🔄 在测 |
| 6 | EduGuard-Bench | C5 安全 · D21 教育安全 | 安全失败率、角色一致性、拒答质量 | ✅ 完成 |
| 7 | ASAP-AES / ASAP 2.0 | C4 评 · D10 作文评分 | 长文本评分，与 SAS-Bench 短答互补 | ✅ 完成 |

> 第 5 项调整说明：EduVisBench 本身评测设计不够严肃，已替换为内部评测 **EduIllustrate**（仓库内 `reports/eval/eduillustrate/`，多 judge 在固定底座上对比），承接 D22 教学可视化生成这一差异化能力。

### 1.2 通用底座（C1，原计划 P2"只引用榜单"，但本轮实跑落地于评测 harness）

| Benchmark | 原子能力 | 已测模型 | 状态 |
| --- | --- | --- | --- |
| MMLU-Pro | D01 通用学科选择题 | MiniMax-M3、doubao-seed-2.0-pro/lite、glm-5.1 | ✅ |
| AGIEval | D03 标准化考试推理 | MiniMax-M3 | ✅ |
| OlympiadBench | D05 高阶/竞赛推理 | MiniMax-M3 | ✅ |
| MathVista | D06 多模态数学 | MiniMax-M3 | ✅ |

### 1.3 P1 第二批

| Benchmark | 原子能力 | 状态 | 说明 |
| --- | --- | --- | --- |
| EduIllustrate（替代 EduVisBench） | D22 | 🔄 在测 | 已覆盖 minimax3、opus-4.8、deepseek-v3.2、doubao-seed-2.0-pro/lite |
| MathTutorBench | D11/D12/D13 数学过程反馈 | 🔄 在测 | 9 子任务 + judge 标定；judge 已标定，模型覆盖逐步补齐 |
| C-Eval | D02 中文本土学科 | ⏳ 未做 | 待补的中文 sanity check |
| CASTLE | D21 个性化教育安全 | ❌ 无数据 | 无稳定公开数据/代码，不满足可复现要求 |

### 1.4 安全（C5）实测覆盖

| Benchmark | 原子能力 | 已测模型 | 状态 |
| --- | --- | --- | --- |
| EduGuard-Bench SATA（P1 教学伤害） | D21 | minimax3、deepseek-v4-pro/flash、doubao-2.0-pro/lite、glm-5.1/5.2 | ✅ |
| EduGuard-Bench Adversarial（P2 对抗安全） | D21 | minimax3、deepseek-v4-pro、doubao-2.0-pro/lite、glm-5.1/5.2 | ✅ |

### 1.5 收尾计划

- **当前阻塞项**：EduIllustrate、MathTutorBench 两个仍在测，是第一波结论的最后两块拼图。
- **P2 暂缓项**（MMLU-Pro 全量、GSM8K、Video-MME、LiveCodeBench、ASSISTments/EdNet/MCD、ASAP-SAS 等）：维持"暂缓 / 只引用公开榜单"，等上面两个测完后，**只用 1–2 个代表模型抽样补测**，作为背景参照，不投入完整成本。

---

## 二、下一步：从结果到能力雷达图

目标：基于第一波结果，刻画**各模型在教育领域的能力画像**，而不是给一个混合总分。

### 2.1 方法（遵守 README 解读护栏）

1. **不跨 benchmark 平均原始分**。每个 benchmark 先按其原生指标（QWK / Accuracy / RFS / ASR / rubric / win-rate 等）算分。
2. **映射到原子能力 D01–D24**：用 `doc/benchmark_atomic_ability_matrix.md` 的覆盖矩阵，把每个 benchmark 的分数归到它主覆盖（`●`）的原子能力上。
3. **归一化**：每个原子能力轴内做同口径归一（如对该轴所有 benchmark 的指标做 min-max 或相对基线），使不同指标可在同一轴聚合。
4. **聚合成雷达轴**：按矩阵的四条主线收敛为雷达图的维度——
   - 通用学科底座（D01–D08）
   - 教学与辅导（D09、D12–D14、D22–D23）
   - 学习建模与个性化（D15–D20）
   - 作答评价与安全（D10–D11、D21）

   每条主线可进一步展开为细轴（如"评价"展开为 D10 作文 / D11 短答分步）。

### 2.2 产出

- 每个模型一张**能力雷达图**（四主线 + 关键细轴），叠加多个模型做对比。
- 配套一句话结论：区分"通用能力强"与"真懂教育"（通用底座高、但教学/评价/安全轴塌陷的模型要点名）。
- 标注 `coverage_gap` 与 P2 暂缓项，避免把代理样本/弱覆盖当成完整能力。

---

## 三、AI-教育评测场（Eval Arena）

把上面的流程产品化：一个能**从教育多维度评测任意 LLM** 的评测场，而不是一次性脚本。

### 3.1 形态

- 输入：一个模型（API 可达）。
- 复用现有 `scripts/eval/` harness（多 provider、可断点续跑、judge 可标定）跑覆盖矩阵内的 benchmark。
- 输出：
  1. **分维度榜单**——按四条主线各出一个 leaderboard（通用底座 / 教学 / 个性化 / 评价与安全），各维度独立排名，**绝不合并成单一总分**。
  2. **能力雷达图**——第二部分的画像。
  3. **下钻**——每个能力轴可下钻到具体 benchmark、具体指标、具体样例。

### 3.2 设计要点

- **维度独立**：教育能力是多维的，"会做题"≠"会教"≠"安全"，分维度呈现是核心卖点。
- **judge 透明**：开放生成/安全类用 LLM-as-judge，需公示 judge 标定结果（参考 `mathtutorbench_judge_calibration`、`eduguard` 的 judge 流程），让分数可信。
- **缺口诚实**：`coverage_gap`、P2 暂缓、无数据（CASTLE）等状态在评测场里显式标记，不掩盖证据缺口。
- **可扩展**：新增 benchmark = 新增一个 `BenchmarkAdapter` + 在矩阵里登记其原子能力覆盖，自动并入对应维度。

### 3.3 里程碑

| 阶段 | 内容 | 依赖 |
| --- | --- | --- |
| M1 | EduIllustrate、MathTutorBench 测完，补齐第一波模型覆盖 | 进行中 |
| M2 | 实现 benchmark→D01–D24→四主线 的归一化与聚合脚本，产出首批模型雷达图 | M1 |
| M3 | 评测场雏形：分维度榜单 + 雷达图 + 下钻的 HTML 报告 | M2 |
| M4 | P2 项 1–2 个模型抽样补测，作为背景参照接入评测场 | M3 |
