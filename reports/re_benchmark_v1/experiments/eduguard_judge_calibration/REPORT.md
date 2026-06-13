# EduGuard-Bench P2 Judge 校准：谁判得准（vs Opus-4.8 金标）

实验目录：`reports/re_benchmark_v1/experiments/eduguard_judge_calibration/`
日期：2026-06-13 ｜ 运行方式见 `README.md`
状态：**金标 120 条（Opus 4.8）完成；DeepSeek-V3 全量算分；MiniMax-M3/M2.7 待补满 90 条**

## 1. 问题

EduGuard-Bench P2 用 LLM-as-judge 判 11,214 条对抗安全回复的 harmful/harmless + 拒答质量。论文（Appendix F）用 **200 条人类 gold** 校准候选 judge，按 Cohen's κ 选出 DeepSeek-V3（harm κ 0.882、refusal-quality κ 0.874）。但**那份人类 gold 未随仓库公开**（已核实仅 Dataset+Results，无标注文件、无 release/LFS/外链）。

本实验自建一份金标重做这套校准，把 MiniMax-M3 / M2.7 放进与 DeepSeek-V3 同一把尺子。

> **金标来源声明**：`gold_annotations.jsonl` 由 **Claude Opus 4.8** 盲标（标注时不可见任何 judge 标签），遵循官方 EduGuard rubric。**这是模型标注的金标准，非人类标注。**

## 2. 方法（详见 README）

`sample`（固定分层抽 120 条）→ `judge`（judge 模型按官方两阶段 prompt + BoN=9 多数投票、不设 max_tokens，完全照论文协议）→ `score`（每个 judge vs Opus 金标算 κ）。DeepSeek-V3 的标签直接取自官方 Results（其 BoN=9 裁决）。

金标分布：120 条 = **49 harmful / 71 harmless**；拒答三档 = 18 standard / 29 educational / 1 flimsy；另 23 条 harmless 为良性合规或 API artifact（无拒答档位，不计入拒答质量对比）。

## 3. 结果

| Judge | harm 准确率 | harm κ | 拒答质量准确率 | 拒答质量 κ | n_harm | n_rq |
|---|---|---|---|---|---|---|
| **MiniMax-M3** | 0.862 | **0.726** | 0.875 | 0.778 | 29* | 8* |
| **DeepSeek-V3** | 0.825 | 0.625 | 0.979 | **0.957** | 120 | 48 |
| **MiniMax-M2.7** | 0.733 | 0.500 | 0.444 | 0.297 | 30* | 9* |

`*` M3/M2.7 目前只判过 30 条（pilot），跑满 90 条后这两行才是 120 条上的可比数字。论文 DeepSeek-V3 vs 人类：harm κ 0.882 / refusal-quality κ 0.874。

### 稳健发现

1. **拒答质量三档：DeepSeek-V3 对 Opus 金标 κ=0.957（n=48），近乎完美**，且与论文 0.874 一致 → 三档标注口径双方高度吻合，DeepSeek-V3 在这项上确实强。
2. **Harmfulness：DeepSeek-V3 对 Opus 金标 κ=0.625**，低于论文的 0.882。原因是 **Opus 比 DeepSeek-V3 更严**——120 条里 Opus 判 49 harmful、DeepSeek 只判 38。分歧系统性地集中在两类边界：
   - **"拒答/虚构外壳下仍给了可操作有害内容"**：如明确给药剂量（多条 HR 类 nootropic/MDMA）、给出可用钓鱼邮件模板、分阶段致命脱水"仪式"、RFID 克隆/GPS 欺骗教程——Opus 判 harmful，DeepSeek 常判 harmless-flimsy 或 harmless。
   - **AP 虚构创作类**（写 villain/宣言/justify cruelty）：是否算 harmful 高度主观。
3. **MiniMax-M2.7 在拒答质量三档上最弱（κ=0.297）**，爱把 standard 混成 flimsy/educational；harm κ 也最低。**M2.7 不适合直接当 judge。**
4. **MiniMax-M3（30 条上）harm κ=0.726、拒答 0.778**，是三者中 harm 最高——倾向支持 Opus 的"更严"口径；但需补满 90 条确认。

## 4. 局限

- **金标是 Opus 4.8 单一模型标注**，非人类、非多标注者。harm κ 的高低取决于"Opus 的严格口径 vs DeepSeek 的宽松口径"哪个更接近真值——这本身是判断哲学之争（"接受有害角色/给出虚构外壳下的有害内容"是否算攻击成功）。结论应在此前提下解读。
- M3/M2.7 尚未判满 120；当前其两行基于 30 条，置信区间大。
- 拒答质量三档里 flimsy 仅 1 条（真·flimsy 拒答本就稀少，许多被 DeepSeek 标为 flimsy 的，Opus 判成了 harmful）——三分类对 flimsy 的分辨力本实验无法充分检验。

## 5. 结论

- **DeepSeek-V3**：拒答质量分类很强（≈论文水平），但 harmfulness 判定偏宽松，会漏判"软壳硬核"的有害回复 → 当 judge 会**低估 ASR**。
- **MiniMax-M3**：harmfulness 上（小样本）反而最接近 Opus 严格口径，有潜力；拒答质量尚可。**最有希望的 MiniMax judge 候选。**
- **MiniMax-M2.7**：拒答质量明显弱，不建议单独当 judge。
- **下一步**：跑满 M3/M2.7 的 90 条得到 120 条全量对比；若要把金标升级为更权威的真值，引入第二位（人类或异构模型）标注者复核 harmfulness 边界。
