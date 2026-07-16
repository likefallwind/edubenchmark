# 教学裁判研究线 · 交接文档（2026-07-16）

给接手这条研究线的下一个 agent。目标：让你不用翻聊天记录就能接着往下推。

---

## 一句话说清这是什么

这条研究线做的是「LLM-as-Judge 教学裁判」的自进化 rubric：让一个大模型当教学对话的评分裁判，用**结构化 rubric + 受限编辑算子 + 诊断驱动提案 + 两段制统计显著性门 + 失败账本**这套自进化循环，在**零新增人工标注**的前提下把裁判和人类标注的一致性（Cohen's kappa）往上推，并用 test 切片做终验。整条线为一篇论文服务。

**当前状态：13 个实验全部跑完，报告写完，且已经提交（commit `d6e720c`）。工作树是干净的——现在树里那 29 个 dirty 文件是另一条线（`atomic_ability_rebenchmark`）的产物，跟裁判研究无关，别动。**

---

## 先读这三份（按顺序）

1. **`doc/judge_research_full_report_2026-07-11.md`**（977 行，权威全程报告）
   - 最前面有「执行摘要：如果只读十行」——十行看完全部结论。
   - §1 是 13 个实验总览表。
   - §10 是**产物索引**：每个实验对应的脚本 + 输出目录，是最权威的文件地图，比本交接文档更细。
2. **`doc/rubric_evolution_plan_2026-07-06.md`**（方法设计 + 原始数据）
   - 附录 0–8 逐个实验记原始结果。附录 7 = 近失确认+下游排名，附录 8 = 去诊断消融+迁移矩阵（最近两批）。
3. **记忆 `judge-meta-eval-jury.md`**（`~/.claude/.../memory/`）——数据资产、脚本布局、prompt provenance、统计口径的速查。

---

## 13 个实验 → 脚本 → 输出目录 → 结论

输出目录统一在 `reports/eval/_judge_rubric/` 下。权威版见报告 §10；这里给快速索引。

| # | 实验 | 脚本 | 状态目录 | 一句话结论 |
|---|------|------|----------|-----------|
| 1 | 元评测集（给裁判出考卷）| judge_meta_eval 数据 | — | 造出可复用的裁判考卷 |
| 2 | 多裁判投票 | — | — | 陪审团投票没用 |
| 3 | Stage 0 校准地板 | `run_judge_calibration.sh` | `stage0/` | 先把便宜的校准收益拿干净 |
| 4 | rubric 自进化 + M3 pilot（核心方法）| `run_judge_rubric_stage1.py` | `stage1/` | 方法成立，M3 3 轮 ~25k 调用 |
| 5 | glm-5.2 主实验 | `run_judge_stage1.py`（`STAGE1_*`）| `stage1_glm-5.2/` | 换裁判仍灵，r1 3/3 验收 |
| 6/§6.1 | 纯 M3 自举对照 | `run_judge_stage1_m3_self.sh` | `stage1_minimax3_self/` | 严格同规格对称对比 |
| 7/§6.2 | dsv4 自举复验 | `run_judge_stage1_dsv4_self.sh` | `stage1_deepseek-v4-pro/` | 裁判样本从 2 增到 3 |
| 8/§6.3 | 近失候选独立确认 | `run_judge_rubric_confirm.py` | 各臂状态目录内 | 六次复验零成立，两次显著变差 |
| 9/§7 | 消融基线 | `run_judge_rubric_ablation.py` | `stage1_minimax3_full/` 等 | 见 §7.1 归因修正 |
| 10/§7.1 | 去诊断单成分消融（P5）| `run_judge_stage1_nodiag.sh` → `run_judge_rubric_stage1.py --no-diagnosis` | `stage1_glm-5.2_nodiag/` | 去诊断仍 2/3 验收，推翻「收益来自诊断」的粗归因 |
| 11/§8.1 | 下游排名影响 | `run_judge_downstream_ranking.py` | `downstream_ranking/` | v1 vs v2 排名基本不变（修掉 max_tokens 坑后）|
| 12/§8 | test 终验 | `run_judge_rubric_stage3.py` | `stage1_glm-5.2/`（test 切片）| dev 3 条显著只 1 条在 test 复现 |
| 13/§8.2 | 跨裁判迁移矩阵 | `run_judge_rubric_transfer.py` → `run_judge_transfer.sh` | `transfer_matrix/` | 诊断 rubric 可跨裁判迁移，去诊断的不迁移；最弱裁判写出最好 rubric |

> 注：表里「实验号」与报告 §1 总览表一致；报告章节号（§6.3 等）见上表右侧标注。

---

## 三个最硬的结论（论文卖点）

1. **归因修正**：承重墙是**受限编辑算子（P1）+ 两段制统计门（P2/P3）**，不是诊断。去诊断消融仍 2/3 验收证明了这点（§7.1）。
2. **诊断买的是「可迁移性」不是「效应量」**：迁移矩阵里诊断驱动的 rubric 6 个跨裁判格子全正、4 个显著；去诊断 rubric 一迁移就 −0.004/−0.046（§8.2）。
3. **test 是硬门槛**：统计门只能挡住选择噪声（13 例 winner's curse + 6 例近失确认全灭），挡不住「dev 分布特异性」——只有 test 终验能。glm 三条 dev 显著线两条在 test 塌了（§8）。

---

## 操作红线（务必遵守）

- **凭据**：只用 `eval "$(grep -E '^export (API_GATEWAY|MINIMAX_API_KEY)=' ~/.bashrc)"` 取。别硬编码、别 echo 出来。
- **绝不广谱 pkill**：用户的 `run_eval.sh` 常驻后台跑批量评测，杀进程只能按**核实过的具体 PID**，误杀会打断无关评测。（记忆 `never-broad-pkill-eval-runs`）
- **并发 ≤ 6**：MiniMax / glm / gateway 都是。
- **test 切片只能开一次，已经烧掉了**（glm Stage 3 用过）。M3-self、dsv4、no-diagnosis 三套 rubric **永远只是 dev 证据**，不许拿去 test 复验，也不许在选择切片上回测近失候选。
- **max_tokens 绝不设上限**（除 `deepseek-v3.2` 那个 gateway 硬要求）。推理模型（glm 内联 CoT / M3 隐藏 reasoning）被 cap 会把预算烧在思考上、返回空 content → unparsed → 假 fail。这个坑在本线咬过两次（0b 锚点、下游排名）。记忆 `eval-no-max-tokens-cap-policy`。
- **不要提交**，除非用户明确要求。裁判线目前已提交、干净；别顺手把无关的 29 个 dirty 文件卷进来。
- 中间运行日志一律写 `reports/eval/_judge_rubric/`；脚本放仓库 `scripts/`。

---

## 关键机制备忘（改代码前先懂）

- **近失协议**：候选点估计为正且 CI 下界 ≥ −0.016 才叫近失，必须在**选择从没碰过的数据**上独立确认，**不许**在选择切片上回测。
- **两种确认模式**（`run_judge_rubric_confirm.py`）：`rediag_subsample`（在 ~560 题重诊断子样本上确认，与 eval 切片不交）vs `pool_remainder`（池减子样本，只对 bea2025 这种 1248 大池可行；mrbench 637 池会退化到 <30 题，功效不足——这个坑修过）。
- **去诊断开关**：`run_judge_rubric_stage1.py --no-diagnosis` 保留受限编辑/筛选/eval 切片/统计门/账本，只砍混淆矩阵+错例。与 `--rediagnose` 互斥。
- **迁移矩阵**：4 rubric × 3 裁判，483 题（诊断池子样本减 126 个 reflection 见过的错例），每格对比该裁判自己缓存的 v1；对角线复用各臂 `pool_<version>` 缓存。断言与 eval 切片零重叠。
- **P6（共识分层）设计了但从未接入主循环**——报告里明确不计入方法，别在文档里给它记功。

---

## 可能的下一步（如果用户要继续推）

报告 §9.4 的原「待补实验」四项已全部做完并划掉。若还要往前，方向候选：
- 把迁移矩阵扩到更多任务/维度（目前只覆到 mrbench/PG 这一格的存在性证明）。
- 更大裁判池（>3）验证「最弱裁判写最好 rubric」是不是稳定规律。
- 论文写作：故事线在 §9.1，贡献点→证据对照在 §9.2，limitations 在 §9.3，都可直接用。

如果用户是要**继续跑实验**，先确认清楚具体补哪个格子/哪个裁判，再动手——别自作主张烧 test，也别在选择切片上回测。
