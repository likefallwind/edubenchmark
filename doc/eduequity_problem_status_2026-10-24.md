# EduEquity 问题现状

日期：2026-10-24  
范围：`data/eduequity/`、EduBench 来源数据、生成与判分脚本、现有 full-run 结果。

## 一、当前判断

EduEquity 的反事实成对设计是清楚的：同一个教育任务只改变学习者身份陈述，再比较模型是否给予不同的教学服务。这个结构适合作为身份敏感性压力测试。

但目前它还不能作为经过验证的公平 benchmark，也不适合用于稳定的模型公平排名、上线门槛或合规证明。主要原因是：

- 上游题目本身主要由 GPT-4o 自由生成，质量验证很弱；
- EduEquity 选取 100 个 seed 和注入身份的原始构建脚本没有随仓库保存；
- QG、TMG、PLS、PCC 是开放生成任务，没有统一 gold 或严格的内容质量 rubric；
- 评分完全依赖单个 LLM judge，没有充分的人类校准和重复性证据；
- 现有结果显示有粗粒度模型差异，但没有证明每道题都有稳定区分度；
- 至少两个模型的生成覆盖不完整，部分缺失回答仍可能以 Hard Fail 进入总分。

## 二、数据和评测结构

当前数据包括：

- 100 个身份中立 seed；
- 5 类 EduBench 任务：IP、QG、TMG、PLS、PCC；
- 每类 20 个 seed；
- 4 个身份轴：gender、ethnicity、urban/rural、socioeconomic background；
- 400 个 A/B pair，800 个 prompt。

每个 pair 的两侧在学科、学段、任务文本、学习目标、困难和资源条件上保持一致，只改变身份陈述。gender、urban/rural 和 SES 的 A/B 方向各为 50/50。A/B 文本归一化检查未发现额外的任务差异。

但是 400 个 pair 不是 400 个独立教育任务。同一个 seed 会被复制到四个身份轴，因此统计分析应按 `seed_id` 聚类，不能把所有 pair 当成独立样本。

此外，400/400 个 pair 的预期标签都是 `no_substantive_difference`。当前没有预先注入的“降低标准、拒绝服务、刻板化建议或资源差异”等阳性控制，所以无法评估 judge 的敏感度、召回率和真阳性识别能力。

## 三、题目来源和生成 provenance

EduEquity 的 seed 来自 DirectionAI/EduBench。仓库记录的上游来源 commit 是 `f19004a5c68c27cd9d354401654345072fb712c6`；EduEquity pair 中记录的 source revision 是 `4e24dc659a17535460d57839ab5ec02c0a4ed6d0`，二者并不相同。

EduBench 的来源代码显示了大致的 AI 生成方式：

- IP：给定学科、学段和题型，让 GPT-4o 自由生成题目和思路；
- QG：让 GPT-4o 自由生成知识点、题目、思路和答案；
- TMG：让 GPT-4o 自由生成知识点和教学素材；
- PLS：让 GPT-4o 自由生成学生画像和个性化学习内容；
- PCC：让 GPT-4o 自由生成学生画像、学习路径和个性化建议。

这些脚本普遍使用 `gpt-4o`、temperature 0.7 和 `max_tokens=2048`，主要做 JSON、字段存在和非空检查，没有系统检查事实正确性、答案唯一性、题型匹配、难度或教育适切性。

当前仓库没有保存：

- EduEquity 选取 100 个 seed 的构建脚本；
- 当时的筛选标准和随机种子；
- 少数民族身份的具体抽样过程；
- 原始 API 请求、完整运行日志和人工筛选记录。

因此可以复核当前 JSONL，但不能从仓库完整重建这 100 个 seed 是如何选出的。EduEquity 当前的生成脚本只负责读取固定 prompt 并生成被测模型回答，不负责生成题目本身。

## 四、题目质量问题

### 4.1 IP：有具体题干，但仍有明显内容效度问题

IP 是当前最接近“固定题目”的任务，但快速人工初筛已经发现多个需要修复或剔除的 seed：

- IP_005 标为英语，选项却全部是中文句子；
- IP_010 自由落体 3 秒没有说明重力加速度；
- IP_013 将细胞壁、细胞膜和细胞器混在“细胞内主要结构”中，边界不清；
- IP_014 把“作者如何表达态度”写成了“该学生如何表达态度”；
- IP_015 “最有可能涉及氧化还原”存在争议空间；
- IP_004 的“每组苹果树和橙子树数量相同”表述不够精确。

IP 题目整体偏基础，部分题目存在天花板，难度跨度和高阶任务覆盖不足。

### 4.2 QG：源元数据和生成结果存在错配

QG 的任务是开放式出题，而不是回答固定题目。当前 20 个 QG seed 中：

- 2 个源记录的题型元数据与生成题型不一致；
- 4 个知识点字段与 prompt 标签不完全一致；
- 没有严格的固定输出 schema；
- 没有独立核验答案唯一性和干扰项质量。

因此 QG 的公平分会混入命题能力、知识点对齐、答案正确性、题型遵从和格式风格。

### 4.3 TMG：题型字段没有实际作用

TMG 的 prompt 核心是“根据知识点生成教学素材”，虽然保留了单选题、多选题、简答题等元数据，但这些题型并不真正决定输出内容。它更像知识点到教案的开放生成任务。

### 4.4 PLS/PCC：画像格式和构念不稳定

PLS 和 PCC 的学生画像由上游模型自由生成，存在以下问题：

- 自然语言、Python dict 字符串和不同字段集合混用；
- PLS 的题型为 NA；
- PCC 有部分 NA，且部分画像缺少姓名、年级、目标或能力字段；
- 不同画像的信息量和具体程度差异很大；
- prompt 中存在“学生画像：学生的画像”等重复文本。

这使得身份差异很难与画像信息量、字段缺失和任务开放性分开。

## 五、身份覆盖边界

- ethnicity 轴的 100 对覆盖约 55 个少数民族名称；大多数民族只有 1–2 个 pair，且都是与汉族配对。它不能支持具体民族或“少数民族整体”的公平估计，更适合称为汉族与多个少数民族名称的刻板化敏感性测试。
- gender 只有男/女二元，没有非二元、跨性别或性别表达变体。
- urban/rural 和 SES prompt 明确写入“所需资源均可获得”。这有助于隔离身份刻板印象，但不代表真实的资源不平等场景。
- 没有残障、方言/语言、移民/地域、年龄交叉身份或多重身份组合。

## 六、现有结果和区分度

在同一个 MiniMax-M3 judge 下，现有 target 模型的总体 EduEquity Score 约为 6.52–7.92。按任务汇总的平均分约为：

| 任务 | 平均分 |
|---|---:|
| IP | 8.64 |
| QG | 7.61 |
| TMG | 6.37 |
| PLS | 7.34 |
| PCC | 7.07 |

这说明它能产生粗粒度的模型和任务差异，但不能直接说明题目质量或公平测量已经可靠。

按 pair score 对模型总体分数做 leave-one-out 相关，MiniMax-M3 judge 下平均相关约为 0.25，中位数约为 0.25；约 22% 的 pair 相关超过 0.5，约 21% 为负相关。每道题只有约 11 个模型观测，逐题相关仍然不稳定。

IP 存在明显天花板：约 57% 的 IP pair 得分不低于 9，且有两个 IP pair 在 11 个 target 模型上都得到至少 9 分。当前只能说有部分题能区分模型，不能说 400 个 pair 都有稳定区分度。

## 七、裁判和运行问题

同一个 target 模型分别使用 MiniMax-M3 和 deepseek-v4-flash judge 时：

- pair 分数的平均绝对差约为 1.46–1.80/10；
- 分数相关约为 0.51–0.65；
- 逐题完全相同的比例约为 4%–7%。

这说明 judge 选择会明显改变绝对分数和部分模型排序。当前没有充分的人类金标、独立裁判交叉校准或重复判断协议。

离线 artifact audit 显示 28 个运行目录中有 2 个 caveat：

- `Qwen-Qwen3.5-4B` 生成 795/800 条；
- `glm-5.3-flash` 生成 799/800 条。

部分单侧无效 pair 仍可能被 judge 判为 Hard Fail 并进入总分，因此这些结果不能直接用于正式横向排名。

另外，`reports/eval/eduequity/README.md` 使用了“headline=accuracy”的旧表述，与实际 0–10 parity score 不一致。实际分数应查看对应 `summary.json` 的 `extra_metrics.overall.eduequity_score`，同时检查生成覆盖率。

## 八、当前可以和不可以说什么

### 可以说

- EduEquity 可以作为身份条件反事实压力测试；
- 某些模型、任务或身份轴上出现了可观察的输出差异；
- TMG、QG 等开放任务比 IP 更容易暴露服务不对称；
- 现有输出中 lower-SES、rural、female 有时更容易被 judge 判为不利，但这只是模型输出与 judge 的联合诊断。

### 不能说

- 不能说当前分数是真实、稳定的群体公平值；
- 不能说 400 个题都有良好心理测量区分度；
- 不能把民族轴结果泛化为少数民族整体结论；
- 不能把模型排名当成经过校准的公平排名；
- 不能用它作为上线门槛、合规证明或真实教育公平效果证据。

## 九、主要证据路径

- `data/eduequity/eduequity_pairs_zh.jsonl`
- `data/eduequity/eduequity_prompts_flat_zh.jsonl`
- `doc/eduequity_run_and_evaluation_guide_2026-08-26.md`
- `scripts/run_eduequity_generation.py`
- `scripts/run_eduequity_judge.py`
- `sources/datasets/edubench/data_manifest.json`
- `sources/datasets/edubench/code/generation/IP.py`
- `sources/datasets/edubench/code/generation/QG.py`
- `sources/datasets/edubench/code/generation/TMG.py`
- `sources/datasets/edubench/code/generation/PLS.py`
- `sources/datasets/edubench/code/generation/PCC.py`
- `reports/eval/eduequity/judge-minimax3/*/summary.json`
- `reports/eval/eduequity/judge-deepseek-v4-flash/*/summary.json`
- `reports/eval/_audit/audit_2026-10-24.jsonl`
