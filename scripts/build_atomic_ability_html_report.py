#!/usr/bin/env python3
"""Build the standalone HTML report for the atomic-ability benchmark (mapping v5).

Reads the aggregation/validation artifacts and the adjudicated measurement model,
writes a self-contained Chinese HTML report to ``html_report/``.  Regenerate by
rerunning; never hand-edit the output.

Inputs:
- data/mapping_measurement_model_v6.json
- reports/atomic_ability_rebenchmark/09_atomic_p_scores.jsonl
- reports/atomic_ability_rebenchmark/13_mapping_validation_cells.jsonl
"""

from __future__ import annotations

import datetime
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "reports" / "atomic_ability_rebenchmark"
OUT_DIR = ROOT / "html_report"
OUT = OUT_DIR / "atomic_ability_benchmark_v6_report_2026-07-18.html"

RELEASE_MODELS = [
    ("minimax-m3", "MiniMax-M3"),
    ("minimax-m2.7", "MiniMax-M2.7"),
    ("deepseek-v4-pro", "DeepSeek-V4-Pro"),
    ("glm-5.2", "GLM-5.2"),
    ("doubao-seed-2-0-pro", "Doubao-Seed-2.0-Pro"),
    # 2026-08-17 加入：自建 vLLM 部署的 Qwen3.5-4B，20 项里测到 18 项，覆盖度与
    # 面板同级。它的 judge 判分格一律 MiniMax-M3——除 edubench 外与面板主流裁判
    # 一致，edubench 面板用的是论文口径的 deepseek-v3.2，那几格跨裁判不严格可比
    # （逐格裁判见 09_atomic_p_score_evidence.jsonl 的 judge_model 字段）。
    ("qwen-qwen3-5-4b", "Qwen3.5-4B"),
]

P_DEFINITIONS = {
    "P01": "按显式指令和格式/行为约束产出",
    "P02": "在长材料/长对话中定位并引用相关证据",
    "P03": "读懂教育场景中的图像/图表等非文本材料并据此推理",
    "P04": "产出图示等结构正确、可读、图文对应的非文本材料",
    "P05": "学科知识与教学专业知识的正确调用",
    "P06": "解题推理与约束下的生成推理",
    "P07": "复查自己的输出,发现并修正错误",
    "P08": "自信程度与正确率一致;不会时主动弃答",
    "P09": "调用工具、完成多步长程任务",
    "P10": "诊断学生错误:判对错、定位错误步骤、解释错因/误概念(三 facet)",
    "P11": "依据(或构建)评分标准评判主观作答与教学回复",
    "P12": "为学生设计考试/作业题目:出题、难度定标、目标对齐",
    "P13": "从交互中建模学生的水平、需求与特征",
    "P14": "针对学生选择并执行合适的教学策略",
    "P15": "基于知识先修结构规划学习顺序",
    "P16": "生成适配学生的解释、引导与反馈",
    "P17": "守住教育者的角色与行为边界",
    "P18": "识别学生消息中的风险信号",
    "P19": "对风险与越界请求选择正确处置方式",
    "P20": "识别抄袭、代写等真实性问题",
}

# 研究层数据 -> 用户版三档可信度的当前定档(与定稿文档口径一致)
P_CREDIBILITY = {
    "P01": ("可信", "直接测量,规则判分无裁判;R20 起单源(仅 ifeval)"),
    "P02": ("参考值", "直接测量但三模型区分度弱(0.79/0.81/0.79)"),
    "P03": ("参考值", "学科图表与图文混排主格仅 1 模型面;视频/音频 facet 空白;三个无视觉模型按 R26 记 0 分"),
    "P04": ("参考值", "单源(eduillustrate);教育域 benchmark 代理通用生成能力,下界估计;时序/交互 facet 空白;5 模型里 3 个未测过"),
    "P05": ("可信·门槛", "多源成熟,但知识簇天花板,门槛性质"),
    "P06": ("可信", "多源成熟"),
    "P07": ("可信", "直接测量(两轮自查)"),
    "P08": ("可信", "直接测量(双任务)"),
    "P09": ("暂未覆盖", "领域空白,诚实标注"),
    "P10": ("可信", "R17 合并(原编号 P11/P12/P13);判对/定位 facet 单源+,归因 facet 多源;edubench 错误识别指标带裁判噪声注记"),
    "P11": ("参考值", "R23 起 judge 格计分,分析式 facet 由单格变三格;生成 rubric facet 仍无分"),
    "P12": ("参考值", "单源,QG 格仅测表达质量,整 P 参考值"),
    "P13": ("参考值", "4 个子能力覆盖 2 个;P12a 金标有模板化风险"),
    "P14": ("可信", "证据最厚(10+ benchmark)"),
    "P15": ("参考值", "单源自建协议,3 模型面,机会校正后 3.8-4.5/10"),
    "P16": ("可信", "证据最厚"),
    "P17": ("参考值", "R23 起事实单源(EduGuard 两子任务);知识 facet 与 P18/P19 同源,不构成互证"),
    "P18": ("参考值", "同上"),
    "P19": ("参考值", "同上"),
    "P20": ("暂未覆盖", "领域空白,诚实标注"),
}

MATURITY = {}  # filled from measurement model rationale below


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def esc(text: object) -> str:
    return html.escape(str(text))


def build() -> str:
    mm = json.loads((ROOT / "data" / "mapping_measurement_model_v6.json").read_text(encoding="utf-8"))
    p_rows = load_jsonl(ART / "09_atomic_p_scores.jsonl")
    cells = load_jsonl(ART / "13_mapping_validation_cells.jsonl")

    abilities = {a["p_code"]: a for a in mm["abilities"] if a.get("model_type") != "tombstone"}
    # facet 中可计分(非 excluded)的 facet 数
    scorable_facets = {}
    for code, ability in abilities.items():
        n = 0
        for facet in ability.get("facets", []):
            if any(not c.get("excluded") for c in facet.get("cells", [])):
                n += 1
        scorable_facets[code] = n

    scores: dict[str, dict[str, dict]] = {}
    for row in p_rows:
        scores.setdefault(row["model_key"], {})[row["p_code"]] = row

    p_codes = sorted(abilities)

    # ---------- 矩阵 ----------
    matrix_rows = []
    for code in p_codes:
        ability = abilities[code]
        cells_html = []
        for key, _label in RELEASE_MODELS:
            row = scores.get(key, {}).get(code)
            if row is None or row["score_10"] is None:
                # R26：没有分数就是「未测过」，不再借别的模型的分数顶上。
                n_untested = (row or {}).get("untested_cell_count") or 0
                title = (
                    f"该模型这项能力的 {n_untested} 个取分格全部未测过，没有分数"
                    if n_untested
                    else "该模型没有这项能力的任何证据"
                )
                cells_html.append(f'<td class="cell none" title="{esc(title)}">未测过</td>')
                continue
            value = row["score_10"]
            width = max(0.0, min(100.0, value * 10))
            partial = row["facet_count_with_evidence"] < scorable_facets.get(code, 1)
            mark = ""
            title = f'{esc(row["p_name"])} · ' + " + ".join(
                f"{esc(k)} {v}" for k, v in row["facet_scores"].items()
            )
            if partial:
                mark = '<span class="partial" title="facet 面不齐,见脚注">◐</span>'
                title += f'（facet {row["facet_count_with_evidence"]}/{scorable_facets[code]}）'
            zero_share = row.get("capability_zero_weight_share") or 0.0
            if zero_share > 0:
                mark += '<span class="partial" title="含「能力不具备记 0 分」的格,见脚注">✕</span>'
                title += (
                    f'（{row.get("capability_zero_count", 0)} 个格因模型不具备所需能力'
                    f'（如视觉）计 0 分，占有效权重 {zero_share:.0%}）'
                )
            if row.get("untested_cell_count"):
                title += f'（另有 {row["untested_cell_count"]} 个格未测过，未计入分母）'
            cells_html.append(
                f'<td class="cell" title="{title}"><div class="val">{value:.2f}{mark}</div>'
                f'<div class="track"><div class="bar" style="width:{width:.0f}%"></div></div></td>'
            )
        tier, _ = P_CREDIBILITY.get(code, ("", ""))
        matrix_rows.append(
            f'<tr><th class="pcode">{code}</th><td class="pname">{esc(abilities[code]["p_name"])}'
            f'<span class="tier t-{"ok" if tier.startswith("可信") else "ref" if tier=="参考值" else "gap"}">{esc(tier)}</span></td>'
            + "".join(cells_html) + "</tr>"
        )

    # ---------- 能力清单 ----------
    ability_rows = []
    for code in p_codes:
        tier, note = P_CREDIBILITY.get(code, ("", ""))
        cls = "ok" if tier.startswith("可信") else "ref" if tier == "参考值" else "gap"
        ability_rows.append(
            f'<tr><th class="pcode">{code}</th><td>{esc(abilities[code]["p_name"])}</td>'
            f'<td class="def">{esc(P_DEFINITIONS.get(code, ""))}</td>'
            f'<td><span class="tier t-{cls}">{esc(tier)}</span></td><td class="def">{esc(note)}</td></tr>'
        )

    # ---------- 效度亮点 ----------
    scored_cells = [c for c in cells if c.get("n_models") and c.get("sd_score_10") is not None]
    top = sorted(scored_cells, key=lambda c: -c["sd_score_10"])[:6]
    flat = sorted((c for c in scored_cells if c.get("variance_restricted")), key=lambda c: c["sd_score_10"])[:6]

    def cell_li(c):
        return (
            f'<li><code>{esc(c["benchmark_id"])}</code> · {esc(c["subdimension"])}'
            f'<span class="mono">（n={c["n_models"]}，跨模型 SD={c["sd_score_10"]:.2f}）</span></li>'
        )

    top_html = "\n".join(cell_li(c) for c in top)
    flat_html = "\n".join(cell_li(c) for c in flat)

    n_cells = len([c for c in cells if not c.get("excluded")])
    n_restricted = sum(1 for c in scored_cells if c.get("variance_restricted"))

    generated = datetime.date.today().isoformat()

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>教育 AI 原子能力评测·映射 v6 报告（2026-07-18）</title>
<style>
:root {{
  color-scheme: light;
  --surface: #fcfcfb; --card: #ffffff; --ink: #0b0b0b; --ink-2: #52514e; --ink-3: #8a8880;
  --line: #e6e4de; --bar: #2a78d6; --track: #eceae4;
  --ok-bg: #e3f2e3; --ok-ink: #1c6b1c; --ref-bg: #fdf1d8; --ref-ink: #8a5f00; --gap-bg: #f1efe9; --gap-ink: #6d6b64;
}}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
    color-scheme: dark;
    --surface: #1a1a19; --card: #222220; --ink: #ffffff; --ink-2: #c3c2b7; --ink-3: #8a8880;
    --line: #3a3935; --bar: #3987e5; --track: #33322f;
    --ok-bg: #1d3a1d; --ok-ink: #8fd48f; --ref-bg: #40350f; --ref-ink: #e8c266; --gap-bg: #2e2d2a; --gap-ink: #a3a199;
  }}
}}
:root[data-theme="dark"] {{
  color-scheme: dark;
  --surface: #1a1a19; --card: #222220; --ink: #ffffff; --ink-2: #c3c2b7; --ink-3: #8a8880;
  --line: #3a3935; --bar: #3987e5; --track: #33322f;
  --ok-bg: #1d3a1d; --ok-ink: #8fd48f; --ref-bg: #40350f; --ref-ink: #e8c266; --gap-bg: #2e2d2a; --gap-ink: #a3a199;
}}
* {{ box-sizing: border-box; }}
body {{ margin: 0; background: var(--surface); color: var(--ink); font: 15px/1.7 -apple-system, "PingFang SC", "Microsoft YaHei", "Noto Sans CJK SC", sans-serif; }}
main {{ max-width: 1080px; margin: 0 auto; padding: 32px 20px 80px; }}
h1 {{ font-size: 26px; line-height: 1.35; margin: 8px 0 4px; }}
h2 {{ font-size: 19px; margin: 44px 0 10px; padding-top: 18px; border-top: 1px solid var(--line); }}
h3 {{ font-size: 16px; margin: 22px 0 8px; }}
p, li {{ color: var(--ink-2); }}
strong {{ color: var(--ink); }}
.sub {{ color: var(--ink-3); font-size: 13px; }}
.mono, code {{ font-family: ui-monospace, "SF Mono", Consolas, monospace; font-size: 0.88em; color: var(--ink-2); }}
code {{ background: var(--track); padding: 1px 5px; border-radius: 4px; }}
.tiles {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; margin: 20px 0; }}
.tile {{ background: var(--card); border: 1px solid var(--line); border-radius: 10px; padding: 14px 16px; }}
.tile .n {{ font-size: 26px; font-weight: 700; color: var(--ink); }}
.tile .l {{ font-size: 13px; color: var(--ink-3); margin-top: 2px; }}
.tablewrap {{ overflow-x: auto; border: 1px solid var(--line); border-radius: 10px; background: var(--card); }}
table {{ border-collapse: collapse; width: 100%; font-size: 13.5px; }}
th, td {{ padding: 7px 10px; text-align: left; border-bottom: 1px solid var(--line); vertical-align: top; }}
thead th {{ color: var(--ink-3); font-weight: 600; font-size: 12.5px; white-space: nowrap; position: sticky; top: 0; background: var(--card); }}
tbody tr:last-child th, tbody tr:last-child td {{ border-bottom: none; }}
.pcode {{ font-family: ui-monospace, Consolas, monospace; color: var(--ink-3); font-weight: 600; white-space: nowrap; }}
.pname {{ white-space: nowrap; font-weight: 600; color: var(--ink); }}
.cell {{ min-width: 108px; }}
.cell .val {{ font-variant-numeric: tabular-nums; font-weight: 600; color: var(--ink); }}
.cell.none {{ color: var(--ink-3); }}
.track {{ height: 5px; background: var(--track); border-radius: 3px; margin-top: 4px; }}
.bar {{ height: 100%; background: var(--bar); border-radius: 3px; }}
.partial {{ color: var(--ref-ink); margin-left: 4px; cursor: help; }}
.tier {{ display: inline-block; font-size: 11.5px; padding: 1px 8px; border-radius: 999px; margin-left: 8px; font-weight: 600; vertical-align: 1px; }}
.t-ok {{ background: var(--ok-bg); color: var(--ok-ink); }}
.t-ref {{ background: var(--ref-bg); color: var(--ref-ink); }}
.t-gap {{ background: var(--gap-bg); color: var(--gap-ink); }}
.def {{ color: var(--ink-2); }}
.note {{ background: var(--card); border: 1px solid var(--line); border-left: 3px solid var(--bar); border-radius: 8px; padding: 10px 14px; margin: 14px 0; font-size: 14px; }}
ul {{ padding-left: 22px; }}
footer {{ margin-top: 48px; color: var(--ink-3); font-size: 12.5px; border-top: 1px solid var(--line); padding-top: 14px; }}
ol li {{ margin: 4px 0; }}
</style>
</head>
<body>
<main>
<p class="sub">研究层预览 · 生成于 {generated} · 生成脚本 <span class="mono">scripts/build_atomic_ability_html_report.py</span></p>
<h1>教育 AI 原子能力评测：映射 v6 报告</h1>
<p>用 <strong>20 项原子能力（编号 P01–P20，R20 重编号后与文档口径一致）</strong>给大模型画教育能力画像。本报告基于映射 v6（最新 R25，2026-07-19：两个权重改为规则推导——相关度五档、置信度两因子；此前 R20 编号迁移与四档证据分层废除、R23 judge 任务恢复计分与多模态生成改制、R24 编号再迁）：每个能力由哪些评测的哪些维度测量、权重多少，全部带数据依据；分数按"facet 内加权、跨 facet 等权"聚合。这是研究层数据的预览——正式的双报告（研究版/用户版）在 M4 里程碑交付。</p>

<div class="tiles">
  <div class="tile"><div class="n">20 项</div><div class="l">原子能力（18 项可计分，P08/P20 领域空白）</div></div>
  <div class="tile"><div class="n">{n_cells} 个</div><div class="l">计分格子（benchmark × 取分维度），来自 30+ 评测变体</div></div>
  <div class="tile"><div class="n">4 个</div><div class="l">自建测验（校准 / 弃答 / 自查 / 先修推理），全部规则判分</div></div>
  <div class="tile"><div class="n">5 + 6</div><div class="l">发布模型全量面 + 扩展模型部分面（edubench 面 11 模型）</div></div>
</div>

<h2>一、怎么读这份报告</h2>
<ul>
  <li><strong>分数是 0–10 的加权合成</strong>：facet（子能力/证据面）内按有效权重加权平均，跨 facet 等权平均。有效权重 = 相关度 × 置信度，两者自 R25 起都由规则推导：<strong>相关度五档</strong>（1.0 完全一致 / 0.8 强相关 / 0.5 中等相关 / 0.2 弱相关 / 0 不挂格）；<strong>置信度两因子</strong>，起点 1.0 各扣 0.15——判分方式（客观规则判分不扣，LLM 当裁判扣）与数据质量（官方发布/同行评议/人工标注金标不扣，自建自判扣），落 1.0 / 0.85 / 0.7 三档。通识答题类证据的 ×0.45 降权口径已于 R20 废除，护栏改由"通识评测不挂教育侧能力"的结构约束承担。</li>
  <li><strong>每个 P 配一档可信度</strong>：<span class="tier t-ok">可信</span> 直接测量或多源互证；<span class="tier t-ref">参考值</span> 单源 / 区分度弱 / 覆盖不全，方向可用、数值别当真；<span class="tier t-gap">暂未覆盖</span> 诚实空白，不硬凑分。</li>
  <li><strong>◐ 表示该格子的 facet 面不齐</strong>（比如某模型只有一个 facet 有数据），横向对比时要小心；悬停可看 facet 明细。</li>
  <li><strong>测不了 ≠ 不存在</strong>：能力清单不随测量可行性伸缩，空白就标空白。</li>
</ul>

<h2>二、核心发现</h2>
<ol>
  <li><strong>"会答题 ≠ 会教"是数字，不是口号。</strong>同一模型内，答题类能力（P05 推理、P09a 判对错 facet）普遍比教学核心能力（P13 策略执行、P12 画像、P06 自查）高出 1.5–3 分；P09 错误诊断内部同样呈深度梯度——判对（8.6–9.0）＞定位（7.6–7.9）＞归因（6.9–8.2）。题级证据更硬：同一批回答里，事实准确性与个性化/动机引导的题内相关约等于零。</li>
  <li><strong>教学短板集中在"看见学生"</strong>：P12 学习者画像（知识状态估计 macro-F1 仅 0.23–0.32，全体模型跑不过多数类基线的 accuracy）和 P06 自我校验（改对率约 0.10）是全场最低的两块。</li>
  <li><strong>安全能力模型间差异大</strong>：P17–P19 上 MiniMax-M3（8.2–8.5）与 DeepSeek-V4-Pro（5.7–6.0）拉开近 3 分——但注意三 P 的知识 facet 同源，不构成三份独立证据。</li>
  <li><strong>天花板依然是最大威胁</strong>：{n_restricted}/{len(scored_cells)} 个有分格子跨模型方差受限（分数挤在一起），知识类与语气类指标尤甚——这些格子只能当门槛，不能用来排名。</li>
</ol>

<h2>三、模型 × 能力分数矩阵（发布 5 模型，0–10）</h2>
<div class="tablewrap">
<table>
<thead><tr><th>P</th><th>能力 / 可信度</th>{"".join(f"<th>{esc(label)}</th>" for _, label in RELEASE_MODELS)}</tr></thead>
<tbody>
{chr(10).join(matrix_rows)}
</tbody>
</table>
</div>
<p class="sub">◐ = facet 面不齐（悬停单元格看 facet 明细与缺口）；✕ = 该能力含「能力不具备记 0 分」的格——模型跑不了那套题不是因为没排上队，而是缺必需能力（当前只有视觉一项），悬停看占多少有效权重；<b>未测过</b> = 该模型这项能力的取分格一个都没跑过，<b>不给分、也不折算成 0</b>。GLM-5.2 的 P12 只有"知识状态估计"一个 facet（edubench 面跑的是 GLM-5.1），横向不可比。</p>
<div class="note"><b>缺测口径（R26，2026-08-04）</b>：此前缺格会取"该格已测模型的最低分"顶替，那既不是这个模型的成绩、也不是诚实的空白——MiniMax-M2.7 / GLM-5.2 / DeepSeek-V4-Pro 的 P03 多模态理解因此拿到过 5.08 分，而这三个模型连图都收不进去。现在缺格分两类：<b>能力不具备</b>（整套题都要该能力才能作答，模型没有）记 <b>0 分</b>并按常规权重规则传导到它挂载的每一个能力；<b>未测过</b>（没跑过，或只有部分题需要该能力、文本模型仍能拿到真实分数）<b>不计分也不进分母</b>，逐格清单见 <span class="mono">09_atomic_p_untested_cells.jsonl</span>。</div>

<h2>四、能力清单与可信度</h2>
<div class="tablewrap">
<table>
<thead><tr><th>P</th><th>名称</th><th>一句话定义</th><th>可信度</th><th>依据</th></tr></thead>
<tbody>
{chr(10).join(ability_rows)}
</tbody>
</table>
</div>

<h2>五、效度检查摘要（13 号检查，映射 v5 口径）</h2>
<p>每个格子算跨模型区分度、每对同 P 格子算跨模型相关。区分度最好与最差的格子：</p>
<h3>拉得开（适合排名）</h3>
<ul>{top_html}</ul>
<h3>挤在一起（方差受限，只能当门槛）</h3>
<ul>{flat_html}</ul>
<div class="note">LLM 裁判的分数按指标甄别，不整体信/不整体疑：换裁判实验显示 edubench 的个性化/动机/高阶思维三指标跨裁判稳健（ρ 0.6–0.8），而"错误识别"指标是裁判噪声（ρ≤0.14）——后者虽入映射但带方法学局限注记、低权重。</div>

<h2>六、我们的创新与自建工作</h2>
<h3>自建了 4 个测验（零标注成本、规则判分）</h3>
<ul>
  <li><strong>置信度校准</strong>（p08_calibration）：测"自信地教错"——教育产品最致命的失效模式；</li>
  <li><strong>能力性弃答</strong>（p08_abstention）：不会时能不能说"不会"；</li>
  <li><strong>两轮自查</strong>（p07_selfcheck）：无提示复查，改对率/改错率与首轮正确率解耦；</li>
  <li><strong>先修关系推理</strong>（mooccube_prereq）：905 条专家先修边做金标的自建协议（评测已接入，分数待跑）。</li>
</ul>
<p>这四个 + IFEval 接入 + LongTutor 挂载，把 P01/P06/P07 从"搭车分"变成了直接测量。</p>
<h3>方法学（相对"拿榜单分加权"）</h3>
<ol>
  <li>预注册测量模型：先声明每个 P 的结构（reflective/formative + facet），再看数据；</li>
  <li>映射效度检查：每个格子有区分度评级，每对同 P 格子有跨模型相关——权重不是拍的，错挂会被数据打回；</li>
  <li>换裁判实验：把 LLM 裁判指标二分为真测量与裁判噪声；</li>
  <li>(任务×指标)级取分：裁判类评测不用任务均分，按原生指标逐格挂载，死格子（题级 SD&lt;0.5）剔除；</li>
  <li>拆分准入规则：子能力拆分需 benchmark 无关的依据（理论/失败机制/教师标准/同源数据）至少两条支持；</li>
  <li>证据分层与门槛降权：通识答题证据永远压不过教学核心证据；</li>
  <li>裁判工程纪律：裁判原文落盘、无 unparsed 中间态、全链路不设 max_tokens 上限。</li>
</ol>
<h3>接入改造的公开评测（17 个 adapter、30+ 变体）</h3>
<p>统一评测框架下移植：MathTutorBench 9 任务（win-rate 判分用 LLM 裁判替换官方 GPU 奖励模型）、EduGuard 两阶段安全、MRBench/BEA2025 双模式、LongTutor 三任务、MMTutorBench、IFEval 官方 checker、K12Vista、MathVista/MMLU-Pro/AGIEval/OlympiadBench/C-Eval（判分逻辑逐个从官方仓库移植）；EduBench 导入同事全量原始判分（11 模型 × 3,797 题 × 12 指标）后做题级重分析。</p>

<h2>七、缺口与限制（诚实声明）</h2>
<ul>
  <li><strong>领域空白</strong>：P08 工具使用与长程执行、P20 学术诚信判定——教育评测领域没有可用基准，报告不硬凑。</li>
  <li><strong>参考值</strong>：P14（mooccube_prereq，3 模型面）与 P03 学科图表 facet（K12Vista，1 模型面）面窄。</li>
  <li><strong>面不齐</strong>：LongTutor / MRBench / BEA 类格子只有 3 个模型面（已决定不补跑，按注记处理）；edubench 面是 GLM-5.1 而非 5.2。</li>
  <li><strong>子能力覆盖</strong>：P12 声明 4 个子能力只测到 2 个；P10 三 facet 只有学业评分有分。</li>
  <li><strong>同源</strong>：P17/P18/P19 的知识 facet 来自同一份 SATA 数据，三个分数不构成互证。</li>
  <li><strong>方差受限</strong>：约六成有分格子分数挤在一起，排名意义有限——补更难的题比调权重更要紧。</li>
</ul>

<footer>
数据源：<span class="mono">reports/atomic_ability_rebenchmark/</span>（09 分数、10 证据、13 效度）·
映射定稿 <span class="mono">doc/atomic_ability_mapping_final_2026-07-15.md</span> ·
测量模型 <span class="mono">data/mapping_measurement_model_v6.json</span>。
分数为研究层原始口径，用户版报告（每 P 一分 + 三档可信度 + 产品语言）随 M4 交付。
</footer>
</main>
</body>
</html>
"""


def main() -> None:
    OUT_DIR.mkdir(exist_ok=True)
    OUT.write_text(build(), encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
