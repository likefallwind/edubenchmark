# 精选题集(mini_v1)方案定稿(2026-07-19)

对应 todo.md 第 1 条:"筛选出一个精选题集;以后默认做精选题集,需要再做全量"。本文档是与用户讨论后的定稿方案,实现前的唯一依据。

## 一、定位与目标(已裁决)

- **定位:日常主力,全量留作校准。** 新模型日常评测跑精选集,结果进 P01–P20 面板并标注 `mini_v1`;每隔几个模型抽一个跑全量,核对精选分与全量分的漂移。精选集**不替代**全量——全量是校准手段,留一法暴露不了的面板过拟合靠它兜底。
- **保真目标:绝对分 + 排名都保。** 精选分与全量分要近似可比,历史全量结果不作废。因此抽样用难度匹配,不做激进的区分度优选(那只保排名、绝对分会系统性偏移)。
- **C 档小 benchmark 不动。** p07/p08 三自建、mooccube、mrbench_tutor、bea2025_tutor、eduillustrate、mathtutorbench 两个 hard 变体、各 judge_calibration 原样保留——合计不到全量 4%,且多为单源主格,题量再小统计量撑不住。

## 二、现状基线

全量一个模型 ≈ **95,151 题**预测调用 + judge 类的数万次裁判调用。前 10 个大头占 76%:mrbench_judge 13,240、mmlu_pro 12,032、bea2025_judge 9,904、asap_2 7,421、agieval 7,272、olympiadbench 6,728、eduguard_sata 5,270、sas_bench 4,109、edubench 3,797、longtutor_evidence 3,003。

三个现成条件:

1. **多模型逐题结果在库**:多数 benchmark 有 4–12 个模型的全量 `scored.jsonl`,可算逐题难度(跨模型均分)与区分度(题分-总分相关)。
2. **验证免费**:选题后不跑 API,用已有逐题结果重算精选集分数,与全量逐格对比,迭代到达标。
3. **`--item-list` 已在 harness**(与 `--limit` 互斥,sha256 自动写入 summary),p08 的 pinned item list 是先例。

## 三、方法

### 精选单位:取分格(cell),不是 benchmark 整体

映射消费的是 (benchmark × subdimension) 格子(longtutor_evidence 按 memory_type 三拆、k12vista 按学科两拆、olympiadbench 只有多模态子集进 P03、edubench 按 task×metric 取分)。**每个被消费的格子在精选集里必须保有足够题量**,否则聚合静默变噪。选题脚本须从 `data/mapping_measurement_model_v6.json` + 聚合脚本的 bucket 定义读出"哪些格子被消费",不得手抄。

### 抽样:分层 × 难度匹配

- 分层轴 = 聚合消费的 bucket × 难度五分箱(难度 = 跨模型逐题均分),层内按比例随机抽(固定 seed)。
- 区分度仅作层内**温和优先级**(模型间分歧大的题优先),不作硬筛。
- 多模型面不足的(k12vista 1 个、mathvista/mmtutorbench 2 个)退化为纯内容分层。
- ceval 5-shot dev 范例、pedagogy_benchmark 的 `is_exemplar` 行天然不在候选池。

### 统计量类型决定每格最小 n

accuracy 类可砍狠;QWK / macro-F1 / κ / RFS 是总体统计量,抽样方差大——用现有逐题数据 bootstrap 出每格统计量的抽样分布,定最小 n。已知硬约束:

- **asap_2**:QWK 按 prompt 分组,每 prompt ≥ ~150 篇;按人类分数分布 + source 条件(资料可得/受限)分层,保住分数谱两端。
- **bea2025_judge / mrbench_judge**:macro-F1 对类别不平衡敏感,按 (dimension × gold label) 分层,8 维/4 维全保。
- **sas_bench**:QWK/CCS/ECS 三个统计量共用题面,取三者最严的 n;按题型/学科分层。
- **eduguard_sata**:RFS 三档,按语言 × 类别分层。
- **eduguard_adversarial**:ASR 是全库区分度最好的格,按攻击类别分层,砍前用 9 个已有模型面重点验证 ASR 漂移。
- **longtutor_evidence**:按 memory_type 三层(单记录提取近天花板,可多砍;跨 session 推理与幻觉检查是区分度所在,少砍)。
- **edubench**:按 task 五层;12 指标共用题面,判分是逐题 12 维裁判,砍题即同比例省裁判。
- **olympiadbench**:多模态子集是 P03 消费格,单独设层保量。

### 留一法防面板过拟合

难度/区分度信号来自现有面板模型。选题时轮流留出一个模型不参与难度估计,在被留出模型上验证漂移。这是本方案唯一实质方法学风险,留一法量化它,定期全量校准兜底。

## 四、分档与预算

| 档 | benchmark | 抽样率 | 备注 |
|---|---|---|---|
| A 狠砍 | mmlu_pro、agieval、olympiadbench、asap_2、sas_bench、eduguard_sata、bea2025_judge、mrbench_judge、edubench、longtutor 三任务、mathtutorbench 非 hard 各任务 | 10–15% | 题量大、难度信号足 |
| B 温和 | ceval(配额按 category 层,52 科目太细)、pedagogy_benchmark、mathvista、eduguard_adversarial、ifeval、mmtutorbench、k12vista | 30–50% | 中等题量或统计量脆弱 |
| C 不动 | p07/p08 三自建、mooccube、mrbench_tutor、bea2025_tutor、eduillustrate、mathtutorbench_*_hard、各 judge_calibration | 100% | 已小,多为单源主格 |

预算:A 12% + B 40% + C 100% ≈ **~1.3 万题 / 模型,约全量 14%**,judge 调用同比例下降。抽样率是初值,验证不达标的格子加题,天花板格子(如 longtutor 单记录提取)可再压。

## 五、验收标准(标准 3、5 已于 2026-07-20 修订)

用全部已有模型面离线重算:

1. 每个消费格 |Δscore_10(精选 − 全量)| ≤ 0.3;
2. 每个 P 分 |Δ| ≤ 0.2;
3. **模型排名 Kendall τ ≥ 0.9,仅统计可分辨模型对**——全量分差超过该格噪声尺度(CI 半宽)的模型对才计入;分差在噪声内、或完全并列的模型对换位不计失败;
4. 留一法:被留出模型上同样满足 1–3(允许个别格放宽到 0.4,须注记);
5. **抽样效率 = (精选 CI 半宽 / 全量 CI 半宽) ÷ √(N_全量/N_精选) ≤ 1.3**——即分层抽样的精度损失不显著劣于纯随机抽样。

### 为什么改标准 3 和 5

原标准是**绝对门槛**,但精选集的本质是**相对全量的近似**,判据也必须是相对的。

- **原标准 5(CI 半宽 ≤2pp)测错了对象**。CI 半宽只由样本量与指标方差决定,公式里根本没有"全量分数"这一项,因此它测的是 *benchmark 自身的固有精度*,不是精选集的保真度。实证:27 个失败格中 **13 个所需样本量超过该 benchmark 全量本身**(longtutor_evidence 幻觉检查需 6,051 题,全量只有 1,001;ifeval 需 1,178,全量 541)——**这些格跑全量也过不了**。一条全量都过不了的标准,显然不是在验收精选集。改后的效率判据全量自比恒为 1.0,逻辑自洽。
- **原标准 3(τ≥0.9)门槛过死且惩罚了不存在的差别**。n=9 时一次相邻换位即掉到 0.889,实际要求零换位;更实质的是,分数统计上无法区分的两个模型(如 7.42 vs 7.45)换位并非失真。改后格级失败由 14 降至 1,说明原失败绝大多数是无害换位。
- **防自欺**:两条修订后的判据与原始绝对值(`cell_tau_raw_legacy`、`ci_abs_legacy`)**并列输出**,原始数字始终可查,避免"改标准让矩阵好看"。

### 抽样调整纪律(2026-07-20 确立)

**禁止对着验证结果调抽样。** 当前面板仅 5–12 个模型,追着失败格加题即是拟合这批模型——正是留一法要防的毛病。

判别标准:**一项抽样调整必须能给出一个不看验证结果也成立的理由。**

- 合格示例(sas_bench):"该指标是 12 个子任务先算再等权平均,故每子任务需足够题量"——由指标定义推出,不依赖任何验证数字。
- 不合格示例:"某格 Δ 超标 → 给它加题"——理由完全来自本次结果。

清单满足抽样原则(严格比例分配、难度五分箱分层、分层轴按指标定义分类)即可定稿。残留失败格**照实注记,不修**。

### 逐 P 可用性标签(取代单一通过/失败)

验收产出不是一个总通过率,而是每个 P 一个标签,说明该 P 的 mini 分能用来做什么:

| 标签 | 含义 |
|---|---|
| 可用于排名 | 绝对分与名次都保真,日常直接读 |
| 仅可用于绝对分 | 分数可信,但可分辨对里有翻转,名次需谨慎 |
| 需跑全量 | 证据太薄,精选不足以支撑结论 |
| 本就不可排名 | 全量也排不出(替代值主导或证据同源),与精选无关 |

这样可避免"某 P 不可信但被总体通过率掩盖"。

## 六、产物、存放与隔离(全部增量,不碰现有内容)

**隔离原则:mini 管线在验证通过并明确裁决接入之前,对现有数据与四步管线零改动。** 具体布局:

| 产物 | 位置 | 性质 |
|---|---|---|
| 题目清单 + 选题 manifest | `data/mini_selection_v1/` | 新目录,纯增量 |
| 离线验证报告 | `reports/mini_selection_v1/` | 新目录;验证只**读** `reports/eval/` 的全量 `scored.jsonl`,不写 |
| mini 实际跑分结果 | `reports/eval_mini_v1/<benchmark>/<model>/` | **独立结果树**,与 `reports/eval/` 平行 |
| mini 聚合面板(将来接入后) | `reports/atomic_ability_rebenchmark_mini_v1/` | 独立输出目录,不与主面板混写 |

**为什么 mini 结果必须另起结果树**:harness 默认写 `reports/eval/<benchmark>/<model>/`,且把已有 `predictions.jsonl` 当断点缓存——同名模型跑 mini 会复用全量预测、并把 `scored.jsonl`/`summary.json` 覆写成子集口径(即 asap_2/pedagogy 导入目录 hazard 的一般化)。放平行树后模型名永不冲突,现有全量结果物理上不可能被 mini 运行触碰。

步骤:

1. `scripts/build_mini_selection_v1.py`(幂等):读全量 `scored.jsonl`(只读)→ 题×模型矩阵 → 分层抽样 → `data/mini_selection_v1/<benchmark>_items_v1.txt` + `selection_manifest.json`(seed、分层配额、每格题数、参与估计的模型面)。
2. `scripts/validate_mini_selection.py` → `reports/mini_selection_v1/`:逐格 Δ、逐 P Δ、排名 τ、留一法、bootstrap CI,HTML+MD 报告。**到这一步为止不发生任何 API 调用、不写任何既有目录。**
3. 跑法:`scripts/eval_benchmark.py --benchmark X --item-list data/mini_selection_v1/X_items_v1.txt --out-dir reports/eval_mini_v1/X/<model>`;`run_eval.sh` 加 `MINI=1` 开关,自动拼这个 out-dir(注意现有 `OUT_DIR` 变量是被忽略的,MINI 路径要真正传 `--out-dir`)。
4. 聚合侧**暂不动**:四步管线继续只读 `reports/eval/`,主面板与 HTML 报告不感知 mini。等验证达标、用户裁决接入后,再让聚合脚本显式加开关读 `reports/eval_mini_v1/`,mini 面打标(类似 imputed 的 ※),输出到独立目录——那是单独一个批次,不并入本期。
5. **清单纪律**:`mini_v1` 清单一经定稿不可改;重选=换量表,须升 `mini_v2` 并整套重新验证,老清单保留。

## 七、风险注记

- **面板过拟合**:难度估计基于 ≤12 个模型,对风格迥异的新模型(如纯推理模型)漂移可能超预期——靠留一法预警 + 定期全量校准兜底,不假装选题是模型无关的。
- **总体统计量方差**:QWK/macro-F1 格即使达标,单模型单格的抽样噪声也比全量大,读 mini 面板的格间小差异要更保守。
- **judge 链噪声不变**:精选不改变裁判协议,R23 判定的裁判噪声格(如 edubench 错误识别 0.3)在 mini 里同样存在,权重体系原样沿用。
- **分数可比性声明**:mini_v1 分数默认与全量近似可比(验收标准 1–2 保证),但对外呈现时仍应标注测量方式,不与全量分混排在同一列无标注。
