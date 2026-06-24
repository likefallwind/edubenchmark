# EduGuard-Bench P2 Judge 校准：谁判得准（vs Opus-4.8 金标）

实验目录：`reports/re_benchmark_v1/experiments/eduguard_judge_calibration/`
日期：2026-06-13（首版）｜ 更新：2026-06-21 ｜ 运行方式见 `README.md`
状态：**金标 120 条（Opus 4.8）完成；9 个 judge 在全 120 条上同台算分**

## 1. 问题

EduGuard-Bench P2 用 LLM-as-judge 判 11,214 条对抗安全回复的 harmful/harmless + 拒答质量。论文（Appendix F）用 **200 条人类 gold** 校准候选 judge，按 Cohen's κ 选出 DeepSeek-V3（harm κ 0.882、refusal-quality κ 0.874）。但**那份人类 gold 未随仓库公开**（已核实仅 Dataset+Results，无标注文件、无 release/LFS/外链）。

本实验自建一份金标重做这套校准，把 MiniMax-M3 / M2.7、gateway 的 doubao/glm、以及多档 DeepSeek（论文 V3 标签 + 官方 v4-pro/flash + gateway 的 v3.2）放进与论文 DeepSeek-V3 同一把尺子。

> **金标来源声明**：`gold_annotations.jsonl` 由 **Claude Opus 4.8** 盲标（标注时不可见任何 judge 标签），遵循官方 EduGuard rubric。**这是模型标注的金标准，非人类标注。**

## 2. 方法（详见 README）

`sample`（固定分层抽 120 条）→ `judge`（judge 模型按官方两阶段 prompt + BoN=9 多数投票、不设 max_tokens，完全照论文协议）→ `score`（每个 judge vs Opus 金标算 κ）。DeepSeek-V3 的标签直接取自官方 Results（其 BoN=9 裁决）。

金标分布：120 条 = **49 harmful / 71 harmless**；拒答三档 = 18 standard / 29 educational / 1 flimsy；另 23 条 harmless 为良性合规或 API artifact（无拒答档位，不计入拒答质量对比）。

## 3. 结果

按 harmfulness κ 排序（全 120 条；数据出自 `judge_vs_gold_summary.json`）：

| Judge | harm 准确率 | harm κ | 拒答质量准确率 | 拒答质量 κ | n_harm | n_rq |
|---|---|---|---|---|---|---|
| **deepseek-v3.2**（gateway） | **0.925** | **0.843** | 0.915 | 0.834 | 120 | 47 |
| MiniMax-M3 | 0.888 | 0.764 | 0.881 | 0.771 | 107 | 42 |
| deepseek-v4-flash（官方） | 0.875 | 0.734 | 0.872 | 0.723 | 120 | 47 |
| glm-5.1（gateway） | 0.872 | 0.725 | 0.957 | **0.904** | 117 | 46 |
| doubao-seed-2.0-lite | 0.842 | 0.676 | 0.849 | 0.660 | 95 | 33 |
| doubao-seed-2.0-pro | 0.849 | 0.670 | 0.915 | 0.812 | 119 | 47 |
| MiniMax-M2.7 | 0.835 | 0.645 | 0.636 | 0.432 | 115 | 44 |
| DeepSeek-V3（论文标签） | 0.825 | 0.625 | 0.979 | **0.957** | 120 | 48 |
| deepseek-v4-pro（官方） | 0.825 | 0.612 | 0.938 | 0.870 | 120 | 48 |

论文 DeepSeek-V3 vs 人类：harm κ 0.882 / refusal-quality κ 0.874。`n_harm < 120` 表示该 judge 有若干条解析失败/未投出有效票，未计入。

### 稳健发现

1. **deepseek-v3.2 是 harmfulness 判定的新最强 judge**：harm κ=0.843、准确率 92.5%，全 120 条无漏判，超过原最强的 MiniMax-M3（0.764），更大幅领先论文 DeepSeek-V3（0.625）和更重的官方 deepseek-v4-pro（0.612）。其 harm κ 已逼近论文 DeepSeek-V3-vs-人类的参照值（0.882）——是当前 P2 对抗安全适配器最值得替换上去的 judge。
2. **同为 DeepSeek，版本/路线差异极大**：gateway 的 v3.2 远好于官方 v4-pro/flash 和论文 V3。v4-pro 推理更重，harm κ 反而垫底——重推理 ≠ 判得准；本任务上 v3.2 的口径明显更贴近 Opus 严标。
3. **harm 与 refusal-quality 的最强项不是同一个模型**：harm 看 deepseek-v3.2，**拒答质量三档**仍是 DeepSeek-V3 论文标签（κ=0.957）与 glm-5.1（κ=0.904）最强。deepseek-v3.2 的 rq κ=0.834 属中上，不是最优。若评测重心在拒答质量分档，glm-5.1 仍是更好的选择。
4. **Harmfulness 的系统性分歧仍在**：Opus 比论文 DeepSeek-V3 更严（120 条里 Opus 判 49 harmful、DeepSeek 只判 38），分歧集中在两类边界：
   - **"拒答/虚构外壳下仍给了可操作有害内容"**：明确给药剂量、可用钓鱼邮件模板、分阶段致命脱水"仪式"、RFID 克隆/GPS 欺骗教程——Opus 判 harmful，论文 DeepSeek 常判 harmless-flimsy 或 harmless。deepseek-v3.2 在这类边界上更靠近 Opus，是它 harm κ 领先的主因。
   - **AP 虚构创作类**（写 villain/宣言/justify cruelty）：是否算 harmful 高度主观。
5. **MiniMax-M2.7 在拒答质量三档上最弱（κ=0.432）**，爱把 standard 混成 flimsy/educational；harm κ 也偏低。**M2.7 不适合直接当 judge。**

## 4. 局限

- **金标是 Opus 4.8 单一模型标注**，非人类、非多标注者。harm κ 的高低取决于"Opus 的严格口径 vs DeepSeek 的宽松口径"哪个更接近真值——这本身是判断哲学之争（"接受有害角色/给出虚构外壳下的有害内容"是否算攻击成功）。结论应在此前提下解读。**deepseek-v3.2 领先 = 它最贴近 Opus 的严标口径**，而非绝对意义上"最准"。
- **deepseek-v3.2 与 Opus 金标可能同源于近似的安全口径**（同属偏严的现代模型家族），κ 偏高需警惕这层相关性，不能据此断言它对人类真值也最优。
- 120 条样本，单一标注者；harm κ 在 0.84 附近时 ±0.07 量级的差异不应过度解读名次。
- 拒答质量三档里 flimsy 极稀少（真·flimsy 拒答本就罕见，许多被 DeepSeek 标为 flimsy 的，Opus 判成了 harmful）——三分类对 flimsy 的分辨力本实验无法充分检验。

## 5. 结论

- **deepseek-v3.2（gateway）= 当前 harmfulness 判定首选 judge**：harm κ 0.843、全 120 条无漏判，最贴近 Opus 严标，明显优于论文 DeepSeek-V3 与官方 v4-pro/flash。建议把 P2 对抗安全适配器的默认 judge 切到它（`--extractor-model deepseek-v3.2`）。
- **若评测重心在拒答质量三档**：glm-5.1（rq κ 0.904）或论文 DeepSeek-V3 标签更强；可考虑 harm 与 refusal-quality 分别用不同 judge。
- **论文 DeepSeek-V3 / 官方 deepseek-v4-pro**：harmfulness 偏宽松，会漏判"软壳硬核"的有害回复 → 当 judge 会**低估 ASR**；不建议在本任务上沿用。
- **MiniMax-M3**：harmfulness 第 2（κ 0.764），可作 MiniMax 侧备选；M2.7 拒答质量弱，不建议单独当 judge。
- **下一步**：若要把金标升级为更权威的真值，引入第二位（人类或异构模型）标注者复核 harmfulness 边界，验证 deepseek-v3.2 的领先不是与 Opus 同源口径造成的。
