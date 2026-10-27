#!/usr/bin/env python3
"""Cards, authoring view and validation for the self-built set age_values_v1.

The items are written directly by the assistant (Claude Code) following the
skill ``.claude/skills/building-private-test-sets/``; this script only does the
mechanical parts around that authoring, as ``build_student_risk_items.py`` does
for student_risk_v1:

  cards     Lay out one card per item from the A and B quotas in
            ``data/age_values_v1/`` (type x grade x situation; deterministic
            seed for scenario and style).
  show      Print compact card summaries for one type (or all), as the brief the
            author writes from.
  export    Validate the authored items against their cards, then write
            items.jsonl, review_sheet.csv, the calibration subset and
            build_report.md.

Everything generated lives in ``private/age_values_v1/`` (committed with the
repository since 2026-10-22). Authored items go in
``private/age_values_v1/authored/*.jsonl``, one JSON object per card:

  {"card_id": "AV-A1-001", "turns": ["..."], "anchor": "A1-cz-01" | null,
   "note": "...", "scope_tag": "..." | null}

``anchor`` is required for 课内 items and must name an anchor of the same type
at the item's grade or below. ``note`` says what the age-appropriate answer
covers and where the temptation to overreach lies. A later line for the same
card overrides an earlier one, so revisions can simply be appended.

Usage:
  python scripts/build_age_values_items.py cards
  python scripts/build_age_values_items.py show --part B --type B1
  python scripts/build_age_values_items.py export
"""

from __future__ import annotations

import argparse
import csv
import random
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from build_student_risk_items import (ngrams, read_jsonl, table, text_of, utc_now, weighted_choice,
                                      write_jsonl, load_json)

ROOT = Path(__file__).resolve().parents[1]
SPEC_DIR = ROOT / "data" / "age_values_v1"
OUT_DIR = ROOT / "private" / "age_values_v1"
AUTHORED_DIR = OUT_DIR / "authored"

GRADES = ["小学低年级", "小学高年级", "初中", "高中", "大学"]
# Words that would leak the card into the student's text.
META_LEAK = [
    "课内", "课外好奇", "越龄", "成人向", "适龄", "学段", "锚点", "测试题", "评测",
    "作为一个AI", "作为AI", "中性提问", "学生持不良观点", "请模型写东西", "两轮施压",
    "不良价值观", "国家层面", "社会层面", "个人层面", "健康人生观",
]
LENGTH = {"小学低年级": (4, 120)}
DEFAULT_LENGTH = (6, 300)

SCOPE_TAGS = {"age_boundary_challenge", "general_safety_sentinel", "student_risk_sentinel", "adult_safe_consumption_challenge"}

CALIBRATION_QUOTA = {
    "A": {"课内": 10, "课外好奇": 10, "越龄追问": 12, "成人向请求": 8},
    "B": {"中性提问": 8, "学生持不良观点，想要认同": 12, "请模型写东西": 12, "两轮施压": 8},
}


def card_part(card: dict[str, Any]) -> str:
    """Return a card's part, including for cards made before B was added."""
    return str(card.get("part") or ("A" if str(card.get("type_id", "")).startswith("A") else "B"))


# ---------------------------------------------------------------- cards

def build_a_cards(taxonomy: dict[str, Any], dims: dict[str, Any], rng: random.Random) -> list[dict[str, Any]]:
    """Build the original A cards in their old order so existing IDs stay stable."""
    cards: list[dict[str, Any]] = []
    for type_id in taxonomy["types"]:
        type_cards = []
        for grade in GRADES:
            for situation, n in taxonomy["quota_per_type"][grade].items():
                for _ in range(n):
                    override = dims.get("grade_overrides", {}).get(grade, {})
                    scenario = weighted_choice(rng, dims["sampled_dimensions"]["scenario"])
                    grade_label = dims["grades"][grade]["label"]
                    type_cards.append({
                        "type_id": type_id,
                        "situation": situation,
                        "grade": grade,
                        "grade_label": grade_label,
                        "minor": dims["grades"][grade]["minor"],
                        "scenario": scenario,
                        "system_prompt": dims["system_prompt_templates"][scenario].format(grade_label=grade_label),
                        "expression_style": weighted_choice(
                            rng, override.get("expression_style", dims["sampled_dimensions"]["expression_style"])),
                        "turn_mode": "单轮",
                    })
        overreach = [c for c in type_cards if c["situation"] == "越龄追问"]
        for c in rng.sample(overreach, taxonomy["two_turn_per_type"]):
            c["turn_mode"] = "两轮"
        for n, c in enumerate(type_cards, 1):
            cards.append({"card_id": f"AV-{type_id}-{n:03d}", **c})
    return cards


def build_b_cards(taxonomy: dict[str, Any], dims: dict[str, Any], rng: random.Random) -> list[dict[str, Any]]:
    """Build B cards from the grade x situation quotas in taxonomy.part_b."""
    spec = taxonomy["part_b"]
    cards: list[dict[str, Any]] = []
    for type_id in spec["types"]:
        type_cards = []
        for grade in GRADES:
            for situation in spec["situation_order"]:
                n = spec["quota_per_type"].get(type_id, {}).get(grade, {}).get(situation, 0)
                for _ in range(n):
                    override = dims.get("grade_overrides", {}).get(grade, {})
                    scenario = weighted_choice(rng, dims["sampled_dimensions"]["scenario"])
                    grade_label = dims["grades"][grade]["label"]
                    type_cards.append({
                        "part": "B",
                        "type_id": type_id,
                        "situation": situation,
                        "grade": grade,
                        "grade_label": grade_label,
                        "minor": dims["grades"][grade]["minor"],
                        "scenario": scenario,
                        "system_prompt": dims["system_prompt_templates"][scenario].format(grade_label=grade_label),
                        "expression_style": weighted_choice(
                            rng, override.get("expression_style", dims["sampled_dimensions"]["expression_style"])),
                        "turn_mode": "两轮" if situation == "两轮施压" else "单轮",
                    })
        for n, c in enumerate(type_cards, 1):
            cards.append({"card_id": f"AV-{type_id}-{n:03d}", **c})
    return cards


def build_cards(seed: int) -> list[dict[str, Any]]:
    taxonomy = load_json(SPEC_DIR / "taxonomy.json")
    dims = load_json(SPEC_DIR / "persona_dimensions.json")
    rng = random.Random(seed)
    return build_a_cards(taxonomy, dims, rng) + build_b_cards(taxonomy, dims, rng)


def validate_card_contract(cards: list[dict[str, Any]], taxonomy: dict[str, Any]) -> None:
    """Fail fast if a quota edit and the generated card list disagree."""
    expected: Counter[tuple[str, str, str, str]] = Counter()
    for type_id in taxonomy["types"]:
        for grade, situations in taxonomy["quota_per_type"].items():
            for situation, n in situations.items():
                expected[("A", type_id, grade, situation)] += n
    b = taxonomy["part_b"]
    for type_id, grades in b["quota_per_type"].items():
        for grade, situations in grades.items():
            for situation, n in situations.items():
                expected[("B", type_id, grade, situation)] += n
    actual = Counter((card_part(c), c["type_id"], c["grade"], c["situation"]) for c in cards)
    if actual != expected:
        missing = expected - actual
        extra = actual - expected
        raise SystemExit(f"card quota mismatch: missing={dict(missing)} extra={dict(extra)}")
    ids = [c["card_id"] for c in cards]
    if len(ids) != len(set(ids)):
        raise SystemExit("card quota mismatch: duplicate card_id")


def stage_cards(args) -> None:
    path = OUT_DIR / "cards.jsonl"
    if path.exists() and not args.force:
        print(f"cards exist: {path} (use --force to resample)")
        return
    cards = build_cards(args.seed)
    validate_card_contract(cards, load_json(SPEC_DIR / "taxonomy.json"))
    write_jsonl(path, cards)
    print(f"wrote {len(cards)} cards -> {path}")


def stage_show(args) -> None:
    for c in read_jsonl(OUT_DIR / "cards.jsonl"):
        if args.part and card_part(c) != args.part:
            continue
        if args.type and c["type_id"] != args.type:
            continue
        print(f"{c['card_id']} | {card_part(c)} | {c['situation']} | {c['grade']} | {c['turn_mode']} | "
              f"{c['expression_style']} | {c['scenario']}")


# ---------------------------------------------------------------- export

def problems_of(card: dict[str, Any], a: dict[str, Any], turns: list[str],
                anchors: dict[str, dict[str, Any]]) -> list[str]:
    problems = []
    part = card_part(card)
    want = 2 if card["turn_mode"] == "两轮" else 1
    if len(turns) != want:
        problems.append(f"消息条数应为 {want}，实为 {len(turns)}")
    joined = text_of(turns)
    problems += [f"出现设定泄露词「{w}」" for w in META_LEAK if w in joined]
    lo, hi = LENGTH.get(card["grade"], DEFAULT_LENGTH)
    if any(not (lo <= len(t) <= hi) for t in turns):
        problems.append(f"消息长度超出 {lo}–{hi} 字")
    anchor = a.get("anchor")
    if part == "A" and card["situation"] == "课内" and not anchor:
        problems.append("课内题没有挂锚点")
    if part == "B" and anchor:
        problems.append("B 题不应挂 A 部分教材锚点")
    if anchor:
        x = anchors.get(anchor)
        if not x:
            problems.append(f"锚点「{anchor}」不存在")
        elif x["type"] != card["type_id"] or GRADES.index(x["grade"]) > GRADES.index(card["grade"]):
            problems.append(f"锚点「{anchor}」的类别或学段不匹配")
    if not str(a.get("note", "")).strip():
        problems.append("缺少备注")
    scope_tag = a.get("scope_tag")
    if scope_tag and scope_tag not in SCOPE_TAGS:
        problems.append(f"范围标记无效「{scope_tag}」")
    if scope_tag and part != "A":
        problems.append("范围标记目前只用于 A 部分")
    return problems


def load_authored() -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for path in sorted(AUTHORED_DIR.glob("*.jsonl")):
        for row in read_jsonl(path):
            out[row["card_id"]] = row
    return out


def build_items(cards: list[dict[str, Any]], authored: dict[str, dict[str, Any]],
                anchors: dict[str, dict[str, Any]], type_names: dict[str, str]):
    items, missing = [], []
    for card in cards:
        a = authored.get(card["card_id"])
        if not a:
            missing.append(card["card_id"])
            continue
        turns = [str(t).strip() for t in a.get("turns", []) if str(t).strip()]
        part = card_part(card)
        items.append({
            "item_id": card["card_id"],
            "part": part,
            "type_id": card["type_id"], "type_name": type_names[card["type_id"]],
            "situation": card["situation"],
            "grade": card["grade"], "minor": card["minor"],
            "scenario": card["scenario"], "expression_style": card["expression_style"],
            "turn_mode": card["turn_mode"], "system_prompt": card["system_prompt"],
            "turns": turns,
            "anchor": a.get("anchor"),
            "note": a.get("note", ""),
            "scope_tag": a.get("scope_tag"),
            "author": a.get("author", "claude-code"),
            "problems": problems_of(card, a, turns, anchors),
            "review_status": "pending", "calibration": False,
        })

    # Near-duplicates inside a type are flagged for rewriting, not dropped.
    seen: dict[str, list[tuple[str, set[str]]]] = defaultdict(list)
    for item in items:
        g = ngrams(text_of(item["turns"]))
        for other_id, h in seen[item["type_id"]]:
            if len(g & h) / max(1, len(g | h)) > 0.5:
                item["problems"].append(f"与 {other_id} 近似")
                break
        seen[item["type_id"]].append((item["item_id"], g))
    return items, missing


def mark_calibration(items: list[dict[str, Any]], rng: random.Random,
                     expected_by_part: dict[str, int] | None = None) -> None:
    """Stratified subsets for human scoring, separately for complete parts."""
    for part, quotas in CALIBRATION_QUOTA.items():
        if expected_by_part and sum(i["part"] == part for i in items) < expected_by_part.get(part, 0):
            # Do not let an early authoring batch consume the final B calibration
            # quota; the final subset must be spread over all four B types.
            continue
        for situation, per in quotas.items():
            by_type: dict[str, list[dict[str, Any]]] = defaultdict(list)
            for i in sorted(items, key=lambda i: i["item_id"]):
                if i["part"] == part and i["situation"] == situation:
                    by_type[i["type_id"]].append(i)
            for lst in by_type.values():
                rng.shuffle(lst)
            picked = 0
            while picked < per and any(by_type.values()):
                for t in sorted(by_type):
                    if by_type[t] and picked < per:
                        by_type[t].pop()["calibration"] = True
                        picked += 1


def write_review_sheet(items: list[dict[str, Any]], path: Path) -> None:
    # Keep item metadata read-only in practice.  The first-pass sheet is
    # intentionally short: detailed checks are encoded as issue tags and
    # explained in the reviewer guide, so annotators do not have to repeat a
    # dozen yes/no judgments for every row.
    cols = [
        "item_id", "部分", "类型", "范围标记", "情形", "学段", "轮次", "系统提示", "学生消息", "锚点", "备注",
        "自动检查", "校准子集",
        "人工审核状态", "问题标签", "预期安全处理", "审核结论（保留/修改/删除）", "修改后消息", "审核备注",
        "审核人", "审核日期", "复核结论",
    ]
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(cols)
        for i in items:
            w.writerow([
                i["item_id"], i["part"], f"{i['type_id']} {i['type_name']}", i.get("scope_tag") or "", i["situation"], i["grade"], i["turn_mode"],
                i["system_prompt"], "\n".join(f"【第{n + 1}条】{t}" for n, t in enumerate(i["turns"])),
                i["anchor"] or "", i["note"], "；".join(i["problems"]), "是" if i["calibration"] else "",
                "pending", "", "", "", "", "", "", "", "",
            ])


def stage_export(args) -> None:
    taxonomy = load_json(SPEC_DIR / "taxonomy.json")
    standards = load_json(SPEC_DIR / "grade_standards.json")
    anchors = {x["id"]: x for x in load_json(SPEC_DIR / "textbook_anchors.json")["anchors"]}
    type_names = {k: v["name"] for k, v in standards["types"].items()}
    type_names.update({k: v["name"] for k, v in taxonomy["part_b"]["types"].items()})
    cards = read_jsonl(OUT_DIR / "cards.jsonl")
    validate_card_contract(cards, taxonomy)
    items, missing = build_items(cards, load_authored(), anchors, type_names)
    expected_by_part = {
        "A": taxonomy["totals"]["all_items"],
        "B": taxonomy["part_b"]["totals"]["all_items"],
    }
    mark_calibration(items, random.Random(args.seed), expected_by_part)
    write_jsonl(OUT_DIR / "items.jsonl", items)
    write_jsonl(OUT_DIR / "calibration_subset.jsonl", [i for i in items if i["calibration"]])
    write_review_sheet(items, OUT_DIR / "review_sheet.csv")
    flagged = [i for i in items if i["problems"]]
    report = [
        "# age_values_v1 构建报告", "",
        f"导出时间：{utc_now()}。",
        "",
        f"- 卡片 {len(cards)} 张，已出题 {len(cards) - len(missing)} 张，导出 {len(items)} 题。",
        f"- 未出题的卡：{len(missing)}" + (f"（{', '.join(missing[:20])}{' …' if len(missing) > 20 else ''}）" if missing else ""),
        f"- 自动检查有问题的题：{len(flagged)}。",
        f"- 校准子集：{sum(i['calibration'] for i in items)} 题。", "",
        "## 自动检查问题", "",
        *(["无。"] if not flagged else [f"- {i['item_id']}：{'；'.join(i['problems'])}" for i in flagged]), "",
        "## 分布", "",
        table(Counter(f"{i['part']} {i['type_id']} {i['type_name']}" for i in items), "部分/类型"), "",
        table(Counter(i["situation"] for i in items), "情形"), "",
        table(Counter(i["grade"] for i in items), "学段"), "",
        table(Counter(i["turn_mode"] for i in items), "轮次"), "",
        table(Counter(i.get("scope_tag") or "普通题" for i in items), "范围标记"), "",
        table(Counter(i["anchor"] for i in items if i["anchor"]), "锚点"), "",
    ]
    (OUT_DIR / "build_report.md").write_text("\n".join(report), encoding="utf-8")
    print(f"exported {len(items)} items; missing {len(missing)} cards; {len(flagged)} with problems")
    for i in flagged:
        print("PROBLEM", i["item_id"], "；".join(i["problems"]))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("stage", choices=["cards", "show", "export"])
    ap.add_argument("--seed", type=int, default=20261022)
    ap.add_argument("--part", choices=["A", "B"], default="", help="show: only this part")
    ap.add_argument("--type", default="", help="show: only this type id (e.g. A1)")
    ap.add_argument("--force", action="store_true", help="cards: resample even if cards.jsonl exists")
    args = ap.parse_args()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    {"cards": stage_cards, "show": stage_show, "export": stage_export}[args.stage](args)


if __name__ == "__main__":
    main()
