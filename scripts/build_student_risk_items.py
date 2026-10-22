#!/usr/bin/env python3
"""Persona cards, authoring view and validation for the private set student_risk_v1.

The items are written directly by the assistant (Claude Code) following the
skill ``.claude/skills/building-private-test-sets/``; this script only does the
mechanical parts around that authoring:

  cards     Sample one persona card per item from the public specification in
            ``data/student_risk_v1/`` (deterministic seed).
  show      Print compact card summaries for one type (or all), as the brief the
            author writes from.
  export    Validate the authored items against their cards, then write
            items.jsonl, review_sheet.csv, the calibration subset and
            build_report.md.

Everything generated lives in ``private/student_risk_v1/`` (git-ignored: the
repository is public and the items must stay unpublished). Authored items go in
``private/student_risk_v1/authored/*.jsonl``, one JSON object per card:

  {"card_id": "SR-A1-001", "turns": ["..."], "signal_evidence": "...",
   "expected_handling": "..."}

Pair cards (age-sensitive types) also carry ``adult_turns``,
``adult_signal_evidence`` and ``adult_expected_handling``. A later line for the
same card overrides an earlier one, so revisions can simply be appended.

Cards carry the four-tier authoring severity the items were written to. Items
are labelled with the three judged risk levels (严重风险 / 轻微风险 / 无风险) via
``tier_to_risk_level`` in the taxonomy; an authored ``risk_level`` (or
``adult_risk_level``) overrides that mapping for a single item.

Usage:
  python scripts/build_student_risk_items.py cards
  python scripts/build_student_risk_items.py show --type A1
  python scripts/build_student_risk_items.py export
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SPEC_DIR = ROOT / "data" / "student_risk_v1"
OUT_DIR = ROOT / "private" / "student_risk_v1"
AUTHORED_DIR = OUT_DIR / "authored"

EXPLICITNESS = ["明说", "暗示", "淡化"]
# Words that would leak the card into the student's text.
META_LEAK = ["画像", "风险等级", "严重程度", "明显程度", "立即干预", "短期关注", "一般支持",
             "严重风险", "轻微风险",
             "作为一个AI", "作为AI"]


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


def weighted_choice(rng: random.Random, weights: dict[str, float]) -> str:
    keys = [k for k, w in weights.items() if w > 0]
    return rng.choices(keys, weights=[weights[k] for k in keys], k=1)[0]


def largest_remainder(total: int, weights: dict[str, int]) -> dict[str, int]:
    """Split ``total`` across keys proportionally to integer ``weights``."""
    s = sum(weights.values())
    if s == 0 or total == 0:
        return {k: 0 for k in weights}
    raw = {k: total * w / s for k, w in weights.items()}
    out = {k: math.floor(v) for k, v in raw.items()}
    for k in sorted(raw, key=lambda k: raw[k] - out[k], reverse=True)[: total - sum(out.values())]:
        out[k] += 1
    return out


def iter_types(taxonomy: dict[str, Any]):
    for cat in taxonomy["categories"]:
        for t in cat["types"]:
            yield cat, t


# ---------------------------------------------------------------- cards

def sample_persona(rng: random.Random, dims: dict[str, Any], grade: str) -> dict[str, str]:
    override = dims.get("grade_overrides", {}).get(grade, {})
    persona = {key: weighted_choice(rng, override.get(key, weights))
               for key, weights in dims["sampled_dimensions"].items() if key != "scenario"}
    # 留守 (parents away, child stays home) and 随迁 (child moves with parents) exclude each other.
    if persona["family"].startswith("留守") and persona["schooling"].startswith("随迁"):
        persona["schooling"] = "走读"
    return persona


def make_card(rng, dims, *, card_id, grade, scenario, mode, turn_mode, extra) -> dict[str, Any]:
    grade_label = dims["grades"][grade]["label"]
    return {
        "card_id": card_id,
        "grade": grade,
        "grade_label": grade_label,
        "minor": dims["grades"][grade]["minor"],
        "scenario": scenario,
        "system_prompt": dims["system_prompt_templates"][scenario].format(grade_label=grade_label),
        "expression_mode": mode,
        "turn_mode": turn_mode,
        "persona": sample_persona(rng, dims, grade),
        **extra,
    }


def build_cards(seed: int) -> list[dict[str, Any]]:
    taxonomy = load_json(SPEC_DIR / "taxonomy.json")
    dims = load_json(SPEC_DIR / "persona_dimensions.json")
    rng = random.Random(seed)
    scenario_w = dims["sampled_dimensions"]["scenario"]
    cards: list[dict[str, Any]] = []

    for cat, t in iter_types(taxonomy):
        quota = {s: n for s, n in t["severity_quota"].items() if n > 0}
        multi = largest_remainder(t.get("multi_turn", 0), quota)
        grades = list(t["grades"])
        rng.shuffle(grades)
        expl = EXPLICITNESS[:]
        rng.shuffle(expl)
        n = 0
        for sev, q in quota.items():
            for turn_mode, count in (("多轮", multi[sev]), ("单轮", q - multi[sev])):
                for _ in range(count):
                    n += 1
                    mode = ("多轮逐步显露" if turn_mode == "多轮"
                            else weighted_choice(rng, dims["expression_mode_weights"]))
                    cards.append(make_card(
                        rng, dims,
                        card_id=f"SR-{t['id']}-{n:03d}",
                        grade=grades[n % len(grades)],
                        scenario=weighted_choice(rng, scenario_w),
                        mode=mode,
                        turn_mode=turn_mode,
                        extra={
                            "kind": "pair" if t.get("age_sensitive") else "risk",
                            "category_id": cat["id"], "category": cat["name"],
                            "type_id": t["id"], "type_name": t["name"],
                            "severity": sev,
                            "explicitness": expl[n % 3],
                        },
                    ))

    grade_cycle = list(dims["grades"])
    for sub in taxonomy["controls"]["subtypes"]:
        for i in range(sub["count"]):
            cards.append(make_card(
                rng, dims,
                card_id=f"SR-{sub['id']}-{i + 1:03d}",
                grade=grade_cycle[i % len(grade_cycle)],
                scenario=weighted_choice(rng, scenario_w),
                mode=weighted_choice(rng, dims["control_expression_mode_weights"]),
                turn_mode="单轮",
                extra={
                    "kind": "control",
                    "category_id": "N", "category": "无风险对照",
                    "type_id": sub["id"], "type_name": sub["name"],
                    "severity": "无风险", "explicitness": "无风险",
                },
            ))
    return cards


def stage_cards(args) -> None:
    path = OUT_DIR / "cards.jsonl"
    if path.exists() and not args.force:
        print(f"cards exist: {path} (use --force to resample)")
        return
    cards = build_cards(args.seed)
    write_jsonl(path, cards)
    print(f"wrote {len(cards)} cards -> {path}")


def stage_show(args) -> None:
    cards = read_jsonl(OUT_DIR / "cards.jsonl")
    for c in cards:
        if args.type and c["type_id"] != args.type:
            continue
        p = c["persona"]
        print(f"{c['card_id']} | {c['severity']} | {c['explicitness']} | {c['turn_mode']} | {c['expression_mode']} | "
              f"{c['grade']} {p['gender']} | {p['family']}/{p['schooling']}/{p['region']} | "
              f"{p['academic']}/{p['social']}/{p['special_needs']} | {p['expression_style']} | {c['scenario']}"
              + (" | 年龄对照" if c["kind"] == "pair" else ""))


# ---------------------------------------------------------------- export

def text_of(turns: list[str]) -> str:
    return "\n".join(turns)


def ngrams(s: str, n: int = 3) -> set[str]:
    s = re.sub(r"\s+", "", s)
    return {s[i:i + n] for i in range(max(0, len(s) - n + 1))}


def problems_of(card: dict[str, Any], turns: list[str]) -> list[str]:
    problems = []
    want = 4 if card["turn_mode"] == "多轮" else 1
    if len(turns) != want:
        problems.append(f"消息条数应为 {want}，实为 {len(turns)}")
    joined = text_of(turns)
    problems += [f"出现设定泄露词「{w}」" for w in META_LEAK if w in joined]
    if want == 1 and not (15 <= len(joined) <= 400):
        problems.append(f"长度异常（{len(joined)} 字）")
    if want == 4 and any(not (8 <= len(t) <= 200) for t in turns):
        problems.append("多轮中有消息过短或过长")
    return problems


def load_authored() -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for path in sorted(AUTHORED_DIR.glob("*.jsonl")):
        for row in read_jsonl(path):
            out[row["card_id"]] = row
    return out


TIER_RE = re.compile(r"属于(立即干预|短期关注|一般支持|无风险)")


def build_items(cards: list[dict[str, Any]], authored: dict[str, dict[str, Any]], dims: dict[str, Any],
                taxonomy: dict[str, Any]):
    tier_map = taxonomy["tier_to_risk_level"]
    levels = set(taxonomy["risk_levels"])

    def labelled(level: str, evidence: str, problems: list[str]) -> tuple[str, list[str]]:
        # Notes were written against the authoring tier; restate them in the judged label.
        if level not in levels:
            problems = problems + [f"风险标签「{level}」不在 {sorted(levels)} 中"]
        return TIER_RE.sub(f"属于{level}", evidence), problems

    items, missing = [], []
    for card in cards:
        a = authored.get(card["card_id"])
        if not a:
            missing.append(card["card_id"])
            continue
        turns = [str(t).strip() for t in a.get("turns", []) if str(t).strip()]
        base = {
            "item_id": card["card_id"],
            "category_id": card["category_id"], "category": card["category"],
            "type_id": card["type_id"], "type_name": card["type_name"],
            "risk_level": a.get("risk_level") or tier_map[card["severity"]],
            "authoring_tier": card["severity"], "explicitness": card["explicitness"],
            "grade": card["grade"], "minor": card["minor"],
            "scenario": card["scenario"], "expression_mode": card["expression_mode"],
            "turn_mode": card["turn_mode"], "system_prompt": card["system_prompt"],
            "turns": turns, "persona": card["persona"],
            "signal_evidence": a.get("signal_evidence", ""),
            "expected_handling": a.get("expected_handling", ""),
            "author": a.get("author", "claude-code"),
            "problems": problems_of(card, turns),
            "pair_id": None, "review_status": "pending", "calibration": False,
        }
        base["signal_evidence"], base["problems"] = labelled(
            base["risk_level"], base["signal_evidence"], base["problems"])
        items.append(base)
        if card["kind"] == "pair":
            adult_turns = [str(t).strip() for t in a.get("adult_turns", []) if str(t).strip()]
            base["pair_id"] = card["card_id"]
            adult = dict(base)
            adult.update(
                item_id=card["card_id"] + "-adult",
                # Most adult versions carry no risk; a few (e.g. habitual smoking)
                # stay low-risk for adults too and set adult_risk_level.
                risk_level=a.get("adult_risk_level", "无风险"), authoring_tier="无风险",
                explicitness=a.get("adult_explicitness", "无风险"),
                grade="大学", minor=False,
                system_prompt=dims["system_prompt_templates"][card["scenario"]].format(
                    grade_label=dims["grades"]["大学"]["label"]),
                turns=adult_turns,
                signal_evidence=a.get("adult_signal_evidence", ""),
                expected_handling=a.get("adult_expected_handling", ""),
                problems=problems_of(card, adult_turns) or ([] if adult_turns else ["成年对照版本缺失"]),
            )
            adult["signal_evidence"], adult["problems"] = labelled(
                adult["risk_level"], adult["signal_evidence"], adult["problems"])
            items.append(adult)

    # Near-duplicates inside a type are flagged for rewriting, not dropped. Age
    # pairs are near-identical by design, so partners are not compared.
    seen: dict[str, list[tuple[str, str | None, set[str]]]] = defaultdict(list)
    for item in items:
        g = ngrams(text_of(item["turns"]))
        for other_id, other_pair, h in seen[item["type_id"]]:
            if item["pair_id"] and other_pair == item["pair_id"]:
                continue
            if len(g & h) / max(1, len(g | h)) > 0.5:
                item["problems"].append(f"与 {other_id} 近似")
                break
        seen[item["type_id"]].append((item["item_id"], item["pair_id"], g))
    return items, missing


CALIBRATION_PER_LEVEL = {"严重风险": 14, "轻微风险": 13, "无风险": 13}


def mark_calibration(items: list[dict[str, Any]], rng: random.Random) -> None:
    """Stratified subset for human scoring: 40 items over the risk levels, spread over categories."""
    for level, per_level in CALIBRATION_PER_LEVEL.items():
        by_cat: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for i in sorted(items, key=lambda i: i["item_id"]):
            if i["risk_level"] == level and not i["item_id"].endswith("-adult"):
                by_cat[i["category_id"]].append(i)
        for lst in by_cat.values():
            rng.shuffle(lst)
        picked = 0
        while picked < per_level and any(by_cat.values()):
            for cat in sorted(by_cat):
                if by_cat[cat] and picked < per_level:
                    by_cat[cat].pop()["calibration"] = True
                    picked += 1


def write_review_sheet(items: list[dict[str, Any]], path: Path) -> None:
    cols = ["item_id", "类型", "风险标签", "出题档位", "明显程度", "学段", "表达方式", "轮次", "系统提示", "学生消息",
            "信号说明", "期望应对", "画像", "自动检查", "校准子集",
            "风险标签是否合适（是 / 应为…）", "审核结论（保留/修改/删除）", "修改后消息", "审核备注"]
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(cols)
        for i in items:
            p = i["persona"]
            w.writerow([
                i["item_id"], f"{i['type_id']} {i['type_name']}", i["risk_level"], i["authoring_tier"],
                i["explicitness"], i["grade"],
                i["expression_mode"], i["turn_mode"], i["system_prompt"],
                "\n".join(f"【第{n + 1}条】{t}" for n, t in enumerate(i["turns"])),
                i["signal_evidence"], i["expected_handling"],
                "；".join(f"{k}:{v}" for k, v in p.items()),
                "；".join(i["problems"]), "是" if i["calibration"] else "", "", "", "", "",
            ])


def table(counter: Counter, title: str) -> str:
    return "\n".join([f"| {title} | 题数 |", "|---|---|", *[f"| {k} | {v} |" for k, v in sorted(counter.items())]])


def stage_export(args) -> None:
    dims = load_json(SPEC_DIR / "persona_dimensions.json")
    taxonomy = load_json(SPEC_DIR / "taxonomy.json")
    cards = read_jsonl(OUT_DIR / "cards.jsonl")
    items, missing = build_items(cards, load_authored(), dims, taxonomy)
    mark_calibration(items, random.Random(args.seed))
    write_jsonl(OUT_DIR / "items.jsonl", items)
    write_jsonl(OUT_DIR / "calibration_subset.jsonl", [i for i in items if i["calibration"]])
    write_review_sheet(items, OUT_DIR / "review_sheet.csv")
    flagged = [i for i in items if i["problems"]]
    report = [
        "# student_risk_v1 构建报告", "",
        f"导出时间：{utc_now()}。题目私有，不进仓库。", "",
        f"- 卡片 {len(cards)} 张，已出题 {len(cards) - len(missing)} 张，导出 {len(items)} 题"
        f"（风险题 {sum(i['risk_level'] != '无风险' for i in items)}，无风险 {sum(i['risk_level'] == '无风险' for i in items)}）。",
        f"- 未出题的卡：{len(missing)}" + (f"（{', '.join(missing[:20])}{' …' if len(missing) > 20 else ''}）" if missing else ""),
        f"- 自动检查有问题的题：{len(flagged)}。",
        f"- 校准子集：{sum(i['calibration'] for i in items)} 题。", "",
        "## 自动检查问题", "",
        *(["无。"] if not flagged else [f"- {i['item_id']}：{'；'.join(i['problems'])}" for i in flagged]), "",
        "## 分布", "",
        table(Counter(f"{i['type_id']} {i['type_name']}" for i in items), "类型"), "",
        table(Counter(i["risk_level"] for i in items), "风险标签"), "",
        table(Counter(i["authoring_tier"] for i in items), "出题档位"), "",
        table(Counter(i["explicitness"] for i in items), "明显程度"), "",
        table(Counter(i["grade"] for i in items), "学段"), "",
        table(Counter(i["expression_mode"] for i in items), "表达方式"), "",
        table(Counter(i["turn_mode"] for i in items), "轮次"), "",
    ]
    (OUT_DIR / "build_report.md").write_text("\n".join(report), encoding="utf-8")
    print(f"exported {len(items)} items; missing {len(missing)} cards; {len(flagged)} with problems")
    for i in flagged:
        print("PROBLEM", i["item_id"], "；".join(i["problems"]))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("stage", choices=["cards", "show", "export"])
    ap.add_argument("--seed", type=int, default=20261021)
    ap.add_argument("--type", default="", help="show: only this type id (e.g. A1, N2)")
    ap.add_argument("--force", action="store_true", help="cards: resample even if cards.jsonl exists")
    args = ap.parse_args()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    {"cards": stage_cards, "show": stage_show, "export": stage_export}[args.stage](args)


if __name__ == "__main__":
    main()
