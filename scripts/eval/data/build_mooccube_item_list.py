#!/usr/bin/env python3
"""Build the fixed item set for MOOCCube prerequisite reasoning (P19a).

MOOCCube ships a knowledge *graph*, not a question set, so the questions are
constructed here — deterministically, once — and every model then runs the same
pinned list via ``--item-list``, exactly like the P08 / K12Vista samples.

Gold
----
``relations/prerequisite-dependency.json``: 905 unique expert edges
``(prerequisite, dependent)`` over 425 math / CS concepts. (The similarly named
``additional_information/prerequisite_prediction.json`` is *not* gold — it is a
model-prediction dump on a different, unjoinable concept vocabulary; see
``doc/benchmark_profiles/mooccube.md``.)

The graph is **not** a DAG: 60 nodes sit on cycles. Both generators are written
to survive that (option validity is checked against the transitive closure; the
ordering task only samples induced subgraphs that are acyclic).

Two task types
--------------
1. ``mcq``  — "学习 Y 之前，下面哪个概念是必须先掌握的先修概念？" 4 options,
   exactly one of which is a real ancestor of Y in the graph. **Distractors are
   drawn to be hard on purpose**:
     * ``reverse``  — a *descendant* of Y (Y is its prerequisite, so the
       direction is flipped). In a topic-neighbourhood sense it is
       indistinguishable from the gold; only knowing the direction separates
       them. Guaranteed non-prerequisite (it is not in ``anc[Y]``).
     * ``sibling``  — a concept in the same field that co-occurs with Y in some
       course, and is neither an ancestor nor a descendant of Y.
   Random-choice baseline is 0.25 by construction (gold letter is uniform).

2. ``order`` — a connected acyclic induced subgraph of 4-6 concepts, presented
   shuffled; the model must output a learning order satisfying every
   prerequisite edge. Any topological order counts (uniqueness is not required).
   The **exact random baseline is enumerated per item** (n! ≤ 720) and only
   subgraphs with baseline ≤ ``--max-order-chance`` are kept, so a shuffling
   model cannot pass by luck.

Ceiling defence: both baselines are recorded in the manifest, and the adapter
reports chance-corrected components in ``score_10``.

Outputs (idempotent, fixed seed):
  * ``data/mooccube/item_list_v1.txt``           — pinned item ids (committed)
  * ``data/mooccube/item_list_v1_manifest.json`` — provenance, strata, baselines,
    and the sha256 of the generated items file (committed)
  * ``sources/datasets/mooccube/items_v1.jsonl`` — the generated questions
    (gitignored; regenerating this script reproduces it byte-for-byte, and the
    adapter verifies the sha256 against the manifest)

Usage:
    python scripts/eval/data/build_mooccube_item_list.py --size 300
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import random
import re
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "sources" / "datasets" / "mooccube" / "MOOCCube"
PREREQ_FILE = SRC / "relations" / "prerequisite-dependency.json"
CONCEPT_FILE = SRC / "entities" / "concept.json"
COURSE_CONCEPT_FILE = SRC / "relations" / "course-concept.json"
ITEMS_JSONL = ROOT / "sources" / "datasets" / "mooccube" / "items_v1.jsonl"
OUT_DIR = ROOT / "data" / "mooccube"

SEED = 20260713
OPTION_KEYS = ["A", "B", "C", "D"]
DEF_MAX_CHARS = 70


# --- graph ------------------------------------------------------------------


def load_graph() -> tuple[set[tuple[str, str]], dict[str, set[str]], dict[str, set[str]], list[str]]:
    if not PREREQ_FILE.is_file():
        raise SystemExit(
            f"missing {PREREQ_FILE}\n"
            "run: python scripts/eval/data/fetch_eval_datasets.py --benchmark mooccube"
        )
    edges: set[tuple[str, str]] = set()
    with PREREQ_FILE.open(encoding="utf-8") as fh:
        for line in fh:
            parts = line.rstrip("\n").split("\t")
            if len(parts) == 2 and parts[0] and parts[1]:
                edges.add((parts[0], parts[1]))
    succ: dict[str, set[str]] = defaultdict(set)
    pred: dict[str, set[str]] = defaultdict(set)
    for a, b in edges:
        succ[a].add(b)
        pred[b].add(a)
    nodes = sorted(set(succ) | set(pred))
    return edges, succ, pred, nodes


def transitive(adj: dict[str, set[str]], nodes: list[str]) -> dict[str, set[str]]:
    """Reachable set per node (cycle-safe; a node on a cycle reaches itself)."""
    out: dict[str, set[str]] = {}
    for n in nodes:
        seen: set[str] = set()
        stack = list(adj[n])
        while stack:
            x = stack.pop()
            if x in seen:
                continue
            seen.add(x)
            stack.extend(adj[x])
        out[n] = seen
    return out


def field_of(concept_id: str) -> str:
    return concept_id.rsplit("_", 1)[-1]


def load_concepts(nodes: list[str]) -> dict[str, dict[str, str]]:
    wanted = set(nodes)
    out: dict[str, dict[str, str]] = {}
    with CONCEPT_FILE.open(encoding="utf-8") as fh:
        for line in fh:
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if rec.get("id") in wanted:
                out[rec["id"]] = {
                    "name": rec.get("name", ""),
                    "definition": short_definition(rec.get("explanation", "")),
                }
    missing = wanted - set(out)
    if missing:
        raise SystemExit(f"{len(missing)} graph concepts missing from concept.json, e.g. {sorted(missing)[:3]}")
    return out


def short_definition(explanation: str) -> str:
    """The '定义：...' clause of a concept explanation, trimmed.

    Concepts whose explanation carries only a subject path ("学科：数学_代数几何学")
    and no 定义 clause get an empty string — the prompt then shows the bare name.
    Emitting the subject path instead would both read as garbage and hand the
    model a field hint the options are deliberately controlled for.
    """
    text = re.sub(r"\s+", " ", explanation or "").strip()
    m = re.search(r"定义[:：](.*?)(?:见载[:：]|$)", text)
    if not m:
        return ""
    body = re.sub(r"\s*见载[:：].*$", "", m.group(1)).strip()
    if len(body) > DEF_MAX_CHARS:
        body = body[:DEF_MAX_CHARS] + "…"
    return body


def load_course_concepts(nodes: list[str]) -> dict[str, set[str]]:
    wanted = set(nodes)
    out: dict[str, set[str]] = defaultdict(set)
    with COURSE_CONCEPT_FILE.open(encoding="utf-8") as fh:
        for line in fh:
            parts = line.rstrip("\n").split("\t")
            if len(parts) == 2 and parts[1] in wanted:
                out[parts[1]].add(parts[0])
    return out


def item_id(prefix: str, *parts: str) -> str:
    digest = hashlib.sha1("|".join(parts).encode("utf-8")).hexdigest()[:10]
    return f"mooccube-{prefix}-{digest}"


# --- task 1: prerequisite MCQ ------------------------------------------------


def build_mcq_pool(
    nodes: list[str],
    pred: dict[str, set[str]],
    anc: dict[str, set[str]],
    desc: dict[str, set[str]],
    concepts: dict[str, dict[str, str]],
    courses: dict[str, set[str]],
    rng: random.Random,
) -> list[dict[str, Any]]:
    pool: list[dict[str, Any]] = []
    for position, target in enumerate(nodes):
        field = field_of(target)
        # Every option — gold included — must sit in the target's own field, or
        # the field alone answers the question ("is 即时通信 a prerequisite of
        # 乘法?" needs no prerequisite knowledge). 35 of the 905 edges are
        # cross-field; those targets simply drop out.
        parents = sorted(n for n in pred[target] if field_of(n) == field)
        if not parents:
            continue
        # Guaranteed non-prerequisites: nothing on a path into `target`.
        forbidden = anc[target] | {target}
        reverse = sorted(n for n in desc[target] - forbidden if field_of(n) == field)
        siblings = sorted(
            n
            for n in nodes
            if n not in forbidden
            and n not in desc[target]
            and field_of(n) == field
            and (courses[n] & courses[target])
        )
        if len(reverse) + len(siblings) < 3:
            continue
        gold = rng.choice(parents)
        # Take up to 2 reverse distractors (the direction trap) and fill the rest
        # with same-course siblings; fall back to reverse if siblings run out.
        picked: list[tuple[str, str]] = []
        rev_take = rng.sample(reverse, min(2, len(reverse)))
        picked += [(c, "reverse") for c in rev_take]
        need = 3 - len(picked)
        sib_take = rng.sample(siblings, min(need, len(siblings)))
        picked += [(c, "sibling") for c in sib_take]
        if len(picked) < 3:
            extra = [c for c in reverse if c not in rev_take]
            picked += [(c, "reverse") for c in rng.sample(extra, 3 - len(picked))]
        # Rotate the gold slot instead of shuffling it, so a constant-letter
        # baseline ("always answer A") lands on exactly 1/4 and cannot beat chance.
        rng.shuffle(picked)
        options: list[tuple[str, str]] = list(picked)
        options.insert(position % len(OPTION_KEYS), (gold, "gold"))
        keys = {}
        opt_rows = []
        for key, (cid, role) in zip(OPTION_KEYS, options):
            keys[cid] = key
            opt_rows.append(
                {
                    "key": key,
                    "concept_id": cid,
                    "name": concepts[cid]["name"],
                    "definition": concepts[cid]["definition"],
                    "role": role,
                }
            )
        pool.append(
            {
                "item_id": item_id("mcq", target, *[o["concept_id"] for o in opt_rows]),
                "task": "mcq",
                "field": field_of(target),
                "target_id": target,
                "target_name": concepts[target]["name"],
                "target_definition": concepts[target]["definition"],
                "options": opt_rows,
                "gold_key": keys[gold],
                "gold_concept_id": gold,
                "n_reverse_distractors": sum(1 for o in opt_rows if o["role"] == "reverse"),
                "chance": 1.0 / len(OPTION_KEYS),
            }
        )
    return pool


# --- task 2: learning-order ordering -----------------------------------------


def is_acyclic(sub: set[str], edges: list[tuple[str, str]]) -> bool:
    adj: dict[str, set[str]] = defaultdict(set)
    for a, b in edges:
        adj[a].add(b)
    color: dict[str, int] = {}

    def visit(u: str) -> bool:
        color[u] = 1
        for v in adj[u]:
            if color.get(v) == 1:
                return False
            if color.get(v, 0) == 0 and not visit(v):
                return False
        color[u] = 2
        return True

    return all(visit(n) for n in sorted(sub) if color.get(n, 0) == 0)


def order_chance(nodes_: list[str], edges: list[tuple[str, str]]) -> float:
    """Exact probability a uniformly random permutation satisfies every edge."""
    good = 0
    total = 0
    for perm in itertools.permutations(nodes_):
        pos = {n: i for i, n in enumerate(perm)}
        total += 1
        if all(pos[a] < pos[b] for a, b in edges):
            good += 1
    return good / total


def build_order_pool(
    nodes: list[str],
    edges: set[tuple[str, str]],
    succ: dict[str, set[str]],
    pred: dict[str, set[str]],
    concepts: dict[str, dict[str, str]],
    rng: random.Random,
    want: int,
    max_chance: float,
    attempts: int = 20000,
) -> list[dict[str, Any]]:
    pool: dict[str, dict[str, Any]] = {}
    for _ in range(attempts):
        if len(pool) >= want * 3:  # oversample, the caller stratifies
            break
        size = rng.choice([4, 5, 5, 6])
        sub = {rng.choice(nodes)}
        while len(sub) < size:
            frontier = set()
            for n in sub:
                frontier |= succ[n] | pred[n]
            frontier -= sub
            if not frontier:
                break
            sub.add(rng.choice(sorted(frontier)))
        if len(sub) != size:
            continue
        sub_edges = sorted((a, b) for a, b in edges if a in sub and b in sub)
        if not is_acyclic(sub, sub_edges):
            continue
        members = sorted(sub)
        chance = order_chance(members, sub_edges)
        if chance > max_chance:
            continue
        iid = item_id("order", *members)
        if iid in pool:
            continue
        shown = members[:]
        rng.shuffle(shown)
        fields = Counter(field_of(n) for n in members)
        pool[iid] = {
            "item_id": iid,
            "task": "order",
            "field": fields.most_common(1)[0][0],
            "n_concepts": len(members),
            "concepts": [
                {
                    "concept_id": cid,
                    "name": concepts[cid]["name"],
                    "definition": concepts[cid]["definition"],
                }
                for cid in shown
            ],
            "edges": [[a, b] for a, b in sub_edges],
            "n_constraints": len(sub_edges),
            "chance": round(chance, 6),
        }
    return sorted(pool.values(), key=lambda r: r["item_id"])


# --- stratified selection -----------------------------------------------------


def stratified_take(pool: list[dict[str, Any]], key, size: int, rng: random.Random) -> list[dict[str, Any]]:
    """Proportional allocation over strata with a floor of 1, largest-remainder."""
    if size >= len(pool):
        return sorted(pool, key=lambda r: r["item_id"])
    groups: dict[Any, list[dict[str, Any]]] = defaultdict(list)
    for row in pool:
        groups[key(row)].append(row)
    strata = sorted(groups, key=str)
    total = sum(len(groups[s]) for s in strata)
    remaining = size - len(strata)
    if remaining < 0:
        raise SystemExit(f"size {size} below stratum count {len(strata)}")
    exact = {s: remaining * len(groups[s]) / total for s in strata}
    alloc = {s: 1 + int(exact[s]) for s in strata}
    leftover = size - sum(alloc.values())
    order = sorted(strata, key=lambda s: (exact[s] - int(exact[s]), len(groups[s])), reverse=True)
    for s in order[:leftover]:
        alloc[s] += 1
    for s in strata:
        alloc[s] = min(alloc[s], len(groups[s]))
    picked: list[dict[str, Any]] = []
    for s in strata:
        rows = sorted(groups[s], key=lambda r: r["item_id"])
        picked += rng.sample(rows, alloc[s])
    return sorted(picked, key=lambda r: r["item_id"])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--size", type=int, default=300, help="total item count (default 300)")
    parser.add_argument("--mcq-share", type=float, default=2 / 3, help="fraction of items that are MCQ")
    parser.add_argument(
        "--max-order-chance",
        type=float,
        default=0.05,
        help="drop ordering items a random shuffle would pass more often than this",
    )
    args = parser.parse_args()

    edges, succ, pred, nodes = load_graph()
    anc = transitive(pred, nodes)
    desc = transitive(succ, nodes)
    concepts = load_concepts(nodes)
    courses = load_course_concepts(nodes)
    on_cycle = [n for n in nodes if n in desc[n]]
    print(
        f"graph: {len(edges)} unique edges / {len(nodes)} concepts / "
        f"{len(on_cycle)} concepts on cycles (excluded from reverse distractors by the closure test)"
    )

    n_mcq = round(args.size * args.mcq_share)
    n_order = args.size - n_mcq

    rng = random.Random(SEED)
    mcq_pool = build_mcq_pool(nodes, pred, anc, desc, concepts, courses, rng)
    order_pool = build_order_pool(
        nodes, edges, succ, pred, concepts, rng, want=n_order, max_chance=args.max_order_chance
    )
    print(f"pools: mcq={len(mcq_pool)} order={len(order_pool)} (asking for {n_mcq}/{n_order})")
    if len(mcq_pool) < n_mcq or len(order_pool) < n_order:
        raise SystemExit("candidate pool too small; lower --size or raise --max-order-chance")

    # MCQ strata: field × does it carry the direction trap. Ordering strata:
    # field × subgraph size.
    mcq = stratified_take(
        mcq_pool, lambda r: (r["field"], "reverse" if r["n_reverse_distractors"] else "sibling_only"), n_mcq, rng
    )
    order = stratified_take(order_pool, lambda r: (r["field"], r["n_concepts"]), n_order, rng)
    items = mcq + order

    ITEMS_JSONL.parent.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in items)
    ITEMS_JSONL.write_text(payload, encoding="utf-8")
    (OUT_DIR / "item_list_v1.txt").write_text(
        "".join(f"{row['item_id']}\n" for row in items), encoding="utf-8"
    )

    mean_order_chance = sum(r["chance"] for r in order) / len(order) if order else None
    manifest = {
        "version": "v1",
        "date": date.today().isoformat(),
        "source": "http://lfs.aminer.cn/misc/moocdata/data/MOOCCube.zip",
        "citation": "Yu et al. 2020, MOOCCube (ACL 2020)",
        "gold_relation": "MOOCCube/relations/prerequisite-dependency.json (905 unique expert edges / 425 concepts)",
        "gold_direction": "left = prerequisite, right = dependent",
        "not_gold": (
            "additional_information/prerequisite_prediction.json — model-prediction dump on a "
            "different concept vocabulary (28/1605 positive overlap with the graph relation)"
        ),
        "seed": SEED,
        "size": len(items),
        "generator": "scripts/eval/data/build_mooccube_item_list.py",
        "items_jsonl": str(ITEMS_JSONL.relative_to(ROOT)),
        "items_sha256": hashlib.sha256(payload.encode("utf-8")).hexdigest(),
        "tasks": {
            "mcq": {
                "n": len(mcq),
                "question": "学习 Y 之前必须先掌握下面哪个概念（4 选 1）",
                "gold": "a real ancestor of Y in the prerequisite graph",
                "distractors": (
                    "reverse = a descendant of Y (direction trap, guaranteed non-prerequisite); "
                    "sibling = same field + shares a course with Y, neither ancestor nor descendant"
                ),
                "random_baseline": 0.25,
                "n_with_reverse_distractor": sum(1 for r in mcq if r["n_reverse_distractors"]),
                "gold_key_distribution": dict(sorted(Counter(r["gold_key"] for r in mcq).items())),
                "by_field": dict(sorted(Counter(r["field"] for r in mcq).items())),
            },
            "order": {
                "n": len(order),
                "question": "把 4-6 个有先修依赖的概念排成合理学习顺序",
                "scoring": "rule: every graph edge (a,b) must have a before b; partial credit = satisfied fraction",
                "random_baseline_mean": round(mean_order_chance, 4) if mean_order_chance is not None else None,
                "random_baseline_max": max((r["chance"] for r in order), default=None),
                "max_order_chance_filter": args.max_order_chance,
                "by_size": dict(sorted(Counter(r["n_concepts"] for r in order).items())),
                "by_field": dict(sorted(Counter(r["field"] for r in order).items())),
                "mean_constraints": round(sum(r["n_constraints"] for r in order) / len(order), 2) if order else None,
            },
        },
        "scoring": "100% rule-based; no LLM judge and no LLM answer extraction",
    }
    (OUT_DIR / "item_list_v1_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest["tasks"], ensure_ascii=False, indent=2))
    print(f"wrote {OUT_DIR/'item_list_v1.txt'} and {ITEMS_JSONL}")


if __name__ == "__main__":
    main()
