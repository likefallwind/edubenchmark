#!/usr/bin/env python3
"""Validate and export the hand-authored education_boundary_v1 item set."""
from __future__ import annotations
import argparse
import csv
import json
import random
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "data" / "education_boundary_v1"
OUT = ROOT / "private" / "education_boundary_v1"
AUTHORED = OUT / "authored"
CATEGORY_IDS = ["academic_integrity", "respect_nonhumiliation", "professional_authority", "teacher_student_relationship"]
RISK_MODES = ["direct_request", "authority_or_social_pressure", "emotional_pressure", "roleplay_or_progressive_escalation"]
ROLES = {"teacher", "tutor", "companion"}
AGES = {"primary", "middle", "high", "university"}
TURN_MODES = {"single": 1, "multi": 4}
META_LEAKS = ["boundary_degree", "guidance_degree", "越界程度", "正确引导", "评分", "裁判", "rubric", "expected_handling", "P17"]

def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))

def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    if not path.exists():
        return rows
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise SystemExit(f"{path}:{line_no}: invalid JSON: {exc}") from exc
    return rows

def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")

def norm(text: str) -> str:
    return re.sub(r"[\W_]+", "", text.lower(), flags=re.UNICODE)

def trigram_set(text: str) -> set[str]:
    text = norm(text)
    return {text[i:i + 3] for i in range(max(0, len(text) - 2))}

def problems(row: dict[str, Any]) -> list[str]:
    out = []
    required = ["item_id", "category_id", "category", "kind", "role", "age_band", "context", "pressure_mode", "turn_mode", "system_prompt", "turns", "expected_handling", "forbidden_behavior", "boundary_types", "referral_needed", "content_safety_overlap", "review_status", "author"]
    for key in required:
        if key not in row:
            out.append(f"缺字段:{key}")
    if row.get("category_id") not in CATEGORY_IDS:
        out.append("category_id 不在四类 P17")
    if row.get("kind") not in {"risk", "control"}:
        out.append("kind 必须为 risk/control")
    if row.get("role") not in ROLES:
        out.append("role 非法")
    if row.get("age_band") not in AGES:
        out.append("age_band 非法")
    if row.get("kind") == "risk" and row.get("pressure_mode") not in RISK_MODES:
        out.append("风险题 pressure_mode 非法")
    if row.get("kind") == "control" and row.get("pressure_mode") != "control":
        out.append("对照题 pressure_mode 必须为 control")
    if row.get("turn_mode") not in TURN_MODES:
        out.append("turn_mode 非法")
    turns = row.get("turns")
    if not isinstance(turns, list) or len(turns) != TURN_MODES.get(row.get("turn_mode"), -1):
        out.append("turns 条数与 turn_mode 不符")
    elif any(not isinstance(turn, str) or not turn.strip() for turn in turns):
        out.append("turns 含空消息")
    if row.get("turn_mode") == "single" and isinstance(turns, list) and not 12 <= len(turns[0]) <= 500:
        out.append("单轮长度异常")
    if row.get("turn_mode") == "multi" and isinstance(turns, list) and any(not 8 <= len(turn) <= 260 for turn in turns):
        out.append("多轮消息长度异常")
    joined = "\n".join(str(x) for x in (turns or []))
    for leak in META_LEAKS:
        if leak in joined:
            out.append(f"题面出现元数据泄露词:{leak}")
    if not row.get("expected_handling"):
        out.append("expected_handling 为空")
    if not row.get("forbidden_behavior"):
        out.append("forbidden_behavior 为空")
    if row.get("review_status") != "pending":
        out.append("review_status 应保持 pending")
    if row.get("author") != "claude-code":
        out.append("author 应为 claude-code")
    if row.get("kind") == "risk" and row.get("boundary_types") != [row.get("category_id")]:
        out.append("风险题 boundary_types 必须为本题主类")
    if row.get("kind") == "control" and row.get("boundary_types") != [row.get("category_id")]:
        out.append("对照题 boundary_types 必须为所在类别")
    if not isinstance(row.get("referral_needed"), bool):
        out.append("referral_needed 必须为 bool")
    if not isinstance(row.get("content_safety_overlap"), bool):
        out.append("content_safety_overlap 必须为 bool")
    if not isinstance(row.get("boundary_types"), list) or not row.get("boundary_types"):
        out.append("boundary_types 必须为非空列表")
    return out

def load_authored() -> list[dict[str, Any]]:
    rows = []
    for path in sorted(AUTHORED.glob("*.jsonl")):
        rows.extend(read_jsonl(path))
    return rows

def validate(rows: list[dict[str, Any]]) -> tuple[list[str], dict[str, Any]]:
    errors = []
    seen = set()
    all_text = {}
    for idx, row in enumerate(rows):
        item_id = row.get("item_id", f"row-{idx + 1}")
        errors.extend(f"{item_id}: {err}" for err in problems(row))
        if item_id in seen:
            errors.append(f"{item_id}: duplicate item_id")
        seen.add(item_id)
        turns = row.get("turns") if isinstance(row.get("turns"), list) else []
        all_text[item_id] = trigram_set("\n".join(turns))
    ids = sorted(all_text)
    for i, left in enumerate(ids):
        for right in ids[i + 1:]:
            if all_text[left] and all_text[left] == all_text[right]:
                errors.append(f"{left}/{right}: exact duplicate turns")
    counts = Counter((row.get("category_id"), row.get("kind")) for row in rows)
    modes = Counter((row.get("category_id"), row.get("pressure_mode")) for row in rows if row.get("kind") == "risk")
    multis = Counter(row.get("category_id") for row in rows if row.get("kind") == "risk" and row.get("turn_mode") == "multi")
    for cat in CATEGORY_IDS:
        if counts[(cat, "risk")] != 60:
            errors.append(f"{cat}: risk count {counts[(cat, 'risk')]} != 60")
        if counts[(cat, "control")] != 20:
            errors.append(f"{cat}: control count {counts[(cat, 'control')]} != 20")
        for mode in RISK_MODES:
            if modes[(cat, mode)] != 15:
                errors.append(f"{cat}: {mode} count {modes[(cat, mode)]} != 15")
        if multis[cat] < 20:
            errors.append(f"{cat}: multi risk count {multis[cat]} < 20")
    summary = {
        "total": len(rows),
        "risk": sum(row.get("kind") == "risk" for row in rows),
        "control": sum(row.get("kind") == "control" for row in rows),
        "by_category_kind": {f"{cat}:{kind}": counts[(cat, kind)] for cat in CATEGORY_IDS for kind in ("risk", "control")},
        "by_pressure_mode": dict(Counter(row.get("pressure_mode") for row in rows if row.get("kind") == "risk")),
        "multi_risk_by_category": dict(multis),
        "problem_count": len(errors),
    }
    return errors, summary

def export(rows: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    rows = sorted(rows, key=lambda row: row["item_id"])
    cards = []
    for row in rows:
        card = dict(row)
        card["turns"] = None
        cards.append(card)
    write_jsonl(OUT / "cards.jsonl", cards)
    write_jsonl(OUT / "items.jsonl", rows)
    fields = ["item_id", "category_id", "kind", "role", "age_band", "context", "pressure_mode", "turn_mode", "system_prompt", "turns", "expected_handling", "forbidden_behavior", "review_status", "human_boundary_degree", "human_guidance_degree", "review_decision", "review_notes"]
    with (OUT / "review_sheet.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({**{field: row.get(field, "") for field in fields}, "turns": json.dumps(row.get("turns", []), ensure_ascii=False)})
    rng = random.Random(20261025)
    calibration = []
    for cat in CATEGORY_IDS:
        cat_rows = [row for row in rows if row["category_id"] == cat]
        calibration.extend(rng.sample([row for row in cat_rows if row["kind"] == "risk"], 6))
        calibration.extend(rng.sample([row for row in cat_rows if row["kind"] == "control"], 4))
    write_jsonl(OUT / "calibration_subset.jsonl", sorted(calibration, key=lambda row: row["item_id"]))
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "pending_human_review",
        "summary": summary,
        "rubric": read_json(SPEC / "taxonomy.json")["primary_rubric"],
        "notes": ["自动检查通过不等于题目效度成立。", "review_status 保持 pending，等待实践者逐题审查。", "calibration_subset.jsonl 含每类 6 风险 + 4 对照，共 40 题。"],
    }
    (OUT / "build_report.md").write_text("# education_boundary_v1 build report\n\n" + json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["validate-only", "export"])
    args = parser.parse_args()
    rows = load_authored()
    errors, summary = validate(rows)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if errors:
        print(f"\n{len(errors)} validation errors:")
        print("\n".join(errors[:200]))
        if len(errors) > 200:
            print(f"... {len(errors) - 200} more")
        return 1
    if args.command == "export":
        export(rows, summary)
        print(f"exported {len(rows)} items to {OUT}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
