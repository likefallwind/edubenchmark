"""MOOCCube prerequisite reasoning adapter (P19a 学习路径规划 / 知识结构基础).

MOOCCube (Yu et al., ACL 2020) ships XuetangX's MOOC knowledge graph, including
905 expert-annotated prerequisite edges over 425 math / CS concepts. It is a
graph, not a question set, so the questions are *constructed* from the graph by
``scripts/eval/data/build_mooccube_item_list.py`` — deterministically, once —
and pinned in ``data/mooccube/item_list_v1.txt``.

Two task types, **both rule-scored — no LLM judge and no LLM answer extraction**
(P19's score must not inherit judge noise):

  * ``mcq``   — "学习 Y 之前必须先掌握下面哪一个？" 4 options, gold = a real
    ancestor of Y. Distractors are same-field on purpose, and up to two of them
    are *descendants* of Y — the same topic neighbourhood with the prerequisite
    direction flipped, so topical familiarity alone cannot answer it. Chance = 0.25.
  * ``order`` — 4-6 dependent concepts, shuffled; output a learning order that
    satisfies every prerequisite edge. Any topological order counts; partial
    credit = the fraction of satisfied constraints. The exact random-shuffle pass
    probability is enumerated per item at build time and capped at 5%.

Headline ``accuracy`` = overall item correctness (MCQ correct, ordering fully
consistent). ``extra_metrics.score_10`` is **chance-corrected** so a random
responder scores 0 rather than ~2.8:

    mcq_norm   = max(0, (mcq_acc   - 0.25)  / (1 - 0.25))
    order_norm = max(0, (order_acc - chance) / (1 - chance))   # chance ≈ 0.03
    score_10   = 10 * (0.5 * mcq_norm + 0.5 * order_norm)

Scope caveat (see doc/benchmark_profiles/mooccube.md): this measures the
*knowledge-structure* half of P19 — ordering a subject's concepts by dependency.
It says nothing about planning a path for a *particular learner's* current state,
which remains a coverage gap.
"""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any

from ..base import ROOT, BenchmarkAdapter
from ..minimax_client import MiniMaxClient

ITEMS_JSONL = ROOT / "sources" / "datasets" / "mooccube" / "items_v1.jsonl"
MANIFEST = ROOT / "data" / "mooccube" / "item_list_v1_manifest.json"

MCQ_CHANCE = 0.25
OPTION_KEYS = ("A", "B", "C", "D")
_SEP = re.compile(r"\s*(?:->|→|=>|⇒|>|＞|,|，|、)\s*")


def _load_rows() -> list[dict[str, Any]]:
    if not ITEMS_JSONL.is_file():
        raise SystemExit(
            f"missing {ITEMS_JSONL}\n"
            "run: python scripts/eval/data/fetch_eval_datasets.py --benchmark mooccube\n"
            " then: python scripts/eval/data/build_mooccube_item_list.py --size 300"
        )
    payload = ITEMS_JSONL.read_text(encoding="utf-8")
    if MANIFEST.is_file():
        expected = json.loads(MANIFEST.read_text(encoding="utf-8")).get("items_sha256")
        actual = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        if expected and expected != actual:
            raise SystemExit(
                f"{ITEMS_JSONL} does not match the pinned item list "
                f"(sha256 {actual[:12]} != manifest {expected[:12]}).\n"
                "Regenerate it with the committed builder: "
                "python scripts/eval/data/build_mooccube_item_list.py --size 300"
            )
    return [json.loads(line) for line in payload.splitlines() if line.strip()]


def _option_block(options: list[dict[str, Any]]) -> str:
    lines = []
    for opt in options:
        definition = opt.get("definition") or ""
        lines.append(f"{opt['key']}. {opt['name']}" + (f"——{definition}" if definition else ""))
    return "\n".join(lines)


def _mcq_prompt(row: dict[str, Any]) -> str:
    target = row["target_name"]
    definition = row.get("target_definition") or ""
    head = f"概念：{target}" + (f"\n定义：{definition}" if definition else "")
    return (
        "下面是某学科知识图谱中的一个概念。\n\n"
        f"{head}\n\n"
        f"问题：按照先修（prerequisite）关系，学习「{target}」之前，必须先掌握下面哪一个概念？\n"
        "注意：先修关系是有方向的——正确选项应当是「{0}」的前置基础，而不是要以「{0}」为基础才能学的后续概念。\n\n"
        f"{_option_block(row['options'])}\n\n"
        "可以简短思考，最后一行只写：答案：<字母>"
    ).format(target)


def _order_prompt(row: dict[str, Any]) -> str:
    names = [c["name"] for c in row["concepts"]]
    listing = "\n".join(
        f"- {c['name']}" + (f"：{c['definition']}" if c.get("definition") else "")
        for c in row["concepts"]
    )
    return (
        f"下面 {len(names)} 个概念之间存在先修（prerequisite）依赖关系，现在顺序是打乱的。\n\n"
        f"{listing}\n\n"
        "请把它们排成一个合理的学习顺序：一个概念的所有先修概念都必须排在它前面。"
        "满足全部依赖的顺序可能不止一种，给出其中任意一种即可。\n\n"
        "可以简短思考，最后一行只写（用 -> 分隔，只写概念名称，不要加序号）：\n"
        f"答案：<最先学的概念> -> <第二个> -> ... -> <最后学的概念>（共 {len(names)} 个）"
    )


def _parse_letter(response: str) -> str:
    text = response or ""
    matches = re.findall(r"答案\s*[:：]?\s*\(?\[?([A-Da-d])", text)
    if not matches:
        matches = re.findall(r"(?:answer|选项)\s*(?:is|为|是)?\s*[:：]?\s*\(?([A-Da-d])\b", text, re.IGNORECASE)
    if not matches:
        # last non-empty line that is (or starts with) a bare option letter
        for line in reversed([ln.strip() for ln in text.splitlines() if ln.strip()]):
            m = re.match(r"^\(?\[?\*{0,2}([A-Da-d])[\).\]、\s*]*$", line)
            if m:
                matches = [m.group(1)]
                break
    return matches[-1].upper() if matches else ""


def _parse_order(response: str, names: list[str]) -> list[str]:
    """Rule-based; returns a permutation of ``names`` or [] if unparseable."""
    text = response or ""
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    candidates: list[str] = []
    for line in reversed(lines):
        m = re.search(r"答案\s*[:：]\s*(.+)$", line)
        candidates.append(m.group(1) if m else line)
    wanted = set(names)
    for candidate in candidates:
        parts = [p.strip(" 　*`。.」「【】[]()（）") for p in _SEP.split(candidate) if p.strip()]
        parts = [re.sub(r"^\d+[\.、)]\s*", "", p) for p in parts]
        if len(parts) == len(names) and set(parts) == wanted:
            return parts
    # Fallback: a line that mentions every concept exactly once — order by first
    # occurrence. Skipped when one name is a substring of another (ambiguous).
    if any(a != b and a in b for a in names for b in names):
        return []
    for candidate in candidates:
        if all(candidate.count(n) == 1 for n in names):
            return sorted(names, key=candidate.index)
    return []


class MOOCCubePrereqAdapter(BenchmarkAdapter):
    name = "mooccube_prereq"
    title = "MOOCCube 先修关系推理（P19 学习路径规划的知识结构基础，规则判分）"
    homepage = "http://moocdata.cn/data/MOOCCube"
    description = (
        "MOOCCube（Yu et al., ACL 2020，学堂在线）知识图谱里 905 条专家标注的先修边（425 个数学/"
        "计算机概念）当金标，构造两类题、100% 规则判分——无裁判、无抽取模型。\n\n"
        "① 先修选择（200 题）：给概念 Y，问学它之前必须先掌握哪一个。干扰项一律同领域，其中最多两个是 Y 的"
        "**后继**概念（方向反转陷阱：Y 才是它们的先修）——只靠“听起来相关”选不对，必须懂方向。随机基线 0.25。\n\n"
        "② 学习顺序排序（100 题）：4-6 个有依赖的概念打乱，要求排出满足全部先修约束的顺序（任意合法拓扑序均算对，"
        "部分分 = 满足的约束比例）。每题随机打乱的通过概率在出题时精确枚举，只保留 ≤5% 的题。\n\n"
        "headline accuracy = 两类题的整体正确率；extra_metrics.score_10 做了**随机基线校正**"
        "（随机作答得 0 分）。注意：这测的是学科知识结构层面的路径，不是针对某个学生当前状态的个性化路径规划。"
    )

    def load_items(self, limit: int | None = None, offset: int = 0) -> list[dict[str, Any]]:
        rows = _load_rows()
        mcq = [r for r in rows if r["task"] == "mcq"]
        order = [r for r in rows if r["task"] == "order"]
        # Interleave 2 MCQ : 1 ordering so any --limit prefix stays balanced
        # across the two task types (smoke tests exercise both).
        ordered: list[dict[str, Any]] = []
        i = j = 0
        while i < len(mcq) or j < len(order):
            for _ in range(2):
                if i < len(mcq):
                    ordered.append(mcq[i])
                    i += 1
            if j < len(order):
                ordered.append(order[j])
                j += 1

        items: list[dict[str, Any]] = []
        for row in ordered:
            if row["task"] == "mcq":
                text = _mcq_prompt(row)
                gold: Any = row["gold_key"]
            else:
                text = _order_prompt(row)
                gold = row["edges"]
            items.append(
                {
                    "item_id": row["item_id"],
                    "text": text,
                    "image_paths": [],
                    "gold": gold,
                    "meta": row,
                }
            )
        end = offset + limit if limit is not None else None
        return items[offset:end]

    def extract_answer(self, item: dict[str, Any], response: str, client: MiniMaxClient, model: str) -> str:
        """Pure regex. No LLM call — P19 must not inherit extraction-model noise."""
        row = item["meta"]
        if row["task"] == "mcq":
            return _parse_letter(response)
        names = [c["name"] for c in row["concepts"]]
        return " -> ".join(_parse_order(response, names))

    def score(self, extracted: str, item: dict[str, Any]) -> dict[str, Any]:
        row = item["meta"]
        if row["task"] == "mcq":
            answer = (extracted or "").strip().upper()
            unparsed = answer not in OPTION_KEYS
            return {
                "correct": (not unparsed) and answer == row["gold_key"],
                "normalized": answer,
                "gold": row["gold_key"],
                "task": "mcq",
                "unparsed": unparsed,
                "chance": MCQ_CHANCE,
                "n_constraints": 1,
                "n_satisfied": 0,
            }

        names = [c["name"] for c in row["concepts"]]
        sequence = [p for p in (extracted or "").split(" -> ") if p]
        unparsed = len(sequence) != len(names) or set(sequence) != set(names)
        edges = [(a, b) for a, b in row["edges"]]
        by_id = {c["concept_id"]: c["name"] for c in row["concepts"]}
        satisfied = 0
        if not unparsed:
            pos = {n: i for i, n in enumerate(sequence)}
            satisfied = sum(1 for a, b in edges if pos[by_id[a]] < pos[by_id[b]])
        return {
            "correct": (not unparsed) and satisfied == len(edges),
            "normalized": " -> ".join(sequence),
            "gold": "; ".join(f"{by_id[a]} 先于 {by_id[b]}" for a, b in edges),
            "task": "order",
            "unparsed": unparsed,
            "chance": row["chance"],
            "n_constraints": len(edges),
            "n_satisfied": satisfied,
        }

    def buckets(self, item: dict[str, Any]) -> dict[str, str]:
        # Every item must expose the same bucket keys — the report takes its
        # column set from the first item only.
        row = item["meta"]
        if row["task"] == "mcq":
            variant = "mcq_with_reverse_trap" if row["n_reverse_distractors"] else "mcq_sibling_only"
        else:
            variant = f"order_n{row['n_concepts']}"
        return {"task": row["task"], "field": row["field"], "variant": variant}

    def extra_summary(self, scored: list[dict[str, Any]]) -> dict[str, Any]:
        rows = [r for r in scored if r.get("score_status") == "scored"]
        if not rows:
            return {}
        mcq = [r for r in rows if r.get("task") == "mcq"]
        order = [r for r in rows if r.get("task") == "order"]

        def acc(subset: list[dict[str, Any]]) -> float | None:
            return round(sum(1 for r in subset if r.get("correct")) / len(subset), 4) if subset else None

        def unparsed_rate(subset: list[dict[str, Any]]) -> float | None:
            return round(sum(1 for r in subset if r.get("unparsed")) / len(subset), 4) if subset else None

        out: dict[str, Any] = {
            "n_scored": len(rows),
            "n_mcq": len(mcq),
            "n_order": len(order),
            "mcq_accuracy": acc(mcq),
            "order_exact_accuracy": acc(order),
            "unparsed_rate": unparsed_rate(rows),
            "mcq_unparsed_rate": unparsed_rate(mcq),
            "order_unparsed_rate": unparsed_rate(order),
            "scoring": "rule-based (option-letter regex + topological constraint check); no judge, no extraction LLM",
        }
        if mcq:
            variant = lambda r: (r.get("buckets") or {}).get("variant")  # noqa: E731
            out["mcq_accuracy_with_reverse_trap"] = acc(
                [r for r in mcq if variant(r) == "mcq_with_reverse_trap"]
            )
            out["mcq_accuracy_sibling_only"] = acc(
                [r for r in mcq if variant(r) == "mcq_sibling_only"]
            )
        if order:
            total = sum(r.get("n_constraints", 0) for r in order)
            out["order_constraint_satisfaction"] = (
                round(sum(r.get("n_satisfied", 0) for r in order) / total, 4) if total else None
            )
            out["order_random_baseline"] = round(
                sum(r.get("chance", 0.0) for r in order) / len(order), 4
            )

        # Chance-corrected headline: a random responder scores 0.
        mcq_acc = out["mcq_accuracy"]
        order_acc = out["order_exact_accuracy"]
        parts: list[float] = []
        weights: list[float] = []
        if mcq_acc is not None:
            out["mcq_chance_corrected"] = round(max(0.0, (mcq_acc - MCQ_CHANCE) / (1 - MCQ_CHANCE)), 4)
            parts.append(out["mcq_chance_corrected"])
            weights.append(0.5)
        if order_acc is not None:
            base = out.get("order_random_baseline") or 0.0
            out["order_chance_corrected"] = round(max(0.0, (order_acc - base) / (1 - base)), 4)
            parts.append(out["order_chance_corrected"])
            weights.append(0.5)
        if parts:
            total_w = sum(weights)
            composite = sum(p * w for p, w in zip(parts, weights)) / total_w
            out["headline_metric"] = (
                "score_10 = 10 × (0.5×mcq_chance_corrected + 0.5×order_chance_corrected); "
                "each component = max(0, (acc − chance) / (1 − chance))"
            )
            out["score_10"] = round(10 * composite, 3)
        return out
