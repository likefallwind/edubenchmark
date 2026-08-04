#!/usr/bin/env python3
"""Validate a generated `agentic.json` against the rebenchmark artifacts.

`build_site_payload.py` reshapes; this script independently re-derives every
number straight from `reports/atomic_ability_rebenchmark_2026-07-08/*.jsonl`
and refuses anything that disagrees. It also checks the payload is internally
closed - no chart can reference a model, ability or benchmark that is not in
the file - so a stale or half-synced payload fails here rather than showing up
as a blank panel on the site.

Usage:
    python scripts/validate_site_payload.py path/to/agentic.json

Exits non-zero on the first failing check group; `scripts/sync-data.sh` in the
website repo gates the commit on it.
"""

from __future__ import annotations

import argparse
import collections
import importlib.util
import json
import statistics
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
REBENCH = ROOT / "reports" / "atomic_ability_rebenchmark_2026-07-08"
EXPLORER = ROOT / "scripts" / "build_atomic_ability_explorer.py"
TOL = 1e-6


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def load_explorer():
    spec = importlib.util.spec_from_file_location("_explorer", EXPLORER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Checker:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.checks = 0

    def eq(self, label: str, got: Any, want: Any) -> None:
        self.checks += 1
        if isinstance(got, float) and isinstance(want, float):
            if abs(got - want) <= TOL:
                return
        elif got == want:
            return
        self.errors.append(f"{label}: got {got!r}, expected {want!r}")

    def true(self, label: str, condition: bool) -> None:
        self.checks += 1
        if not condition:
            self.errors.append(label)


def validate(payload: dict[str, Any]) -> Checker:
    c = Checker()
    # R26 起该文件也收录「未测过」的 P 行（score_10=None）。它们没有分数，
    # 不进 payload，也不该进这里的任何比对——覆盖率必须按有分的行算。
    p_scores = [r for r in load_jsonl(REBENCH / "09_atomic_p_scores.jsonl") if r["score_10"] is not None]
    evidence = load_jsonl(REBENCH / "09_atomic_p_score_evidence.jsonl")
    group_scores = load_jsonl(REBENCH / "10_group_scores.jsonl")
    explorer = load_explorer()

    # --- scores round-trip to source jsonl --------------------------------
    c.eq("scores/count", len(payload["scores"]), len(p_scores))
    for row in p_scores:
        key = f"{row['model_key']}|{row['p_code']}"
        entry = payload["scores"].get(key)
        if entry is None:
            c.errors.append(f"scores/{key}: missing")
            continue
        c.eq(f"scores/{key}/s", entry["s"], round(row["score_10"], 4))
        c.eq(f"scores/{key}/nf", entry["nf"], row["facet_count_with_evidence"])
        c.eq(f"scores/{key}/zero", entry["zero"], row["capability_zero_count"])
        c.eq(f"scores/{key}/unt", entry["unt"], row["untested_cell_count"])

    c.eq("groupScore/count", len(payload["groupScore"]), len(group_scores))
    for row in group_scores:
        key = f"{row['model_key']}|{row['group']}"
        c.eq(f"groupScore/{key}", payload["groupScore"].get(key), round(row["score_10"], 4))

    # --- models: overall / n_ability / n_evidence -------------------------
    by_model = collections.defaultdict(list)
    for row in p_scores:
        by_model[row["model_key"]].append(round(row["score_10"], 4))
    ev_count = collections.Counter(row["model_key"] for row in evidence)
    c.eq("models/count", len(payload["models"]), len(by_model))
    for model in payload["models"]:
        key = model["key"]
        c.eq(f"models/{key}/overall", model["overall"], statistics.fmean(by_model[key]))
        c.eq(f"models/{key}/n_ability", model["n_ability"], len(by_model[key]))
        c.eq(f"models/{key}/n_evidence", model["n_evidence"], ev_count[key])
        c.eq(f"models/{key}/full", model["full"], key in set(payload["panel"]))
    c.eq("meta/n_evidence", payload["meta"]["n_evidence"], len(evidence))

    # --- panel ------------------------------------------------------------
    model_keys = {m["key"] for m in payload["models"]}
    for key in payload["panel"]:
        c.true(f"panel/{key}: not in models", key in model_keys)
    c.eq(
        "panel/size",
        sum(1 for m in payload["models"] if m["full"]),
        len(payload["panel"]),
    )

    # --- benchmarks: id set matches BENCHMARK_META, prose is present ------
    bench_ids = [b["id"] for b in payload["benchmarks"]]
    c.eq("benchmarks/unique-ids", len(set(bench_ids)), len(bench_ids))
    mapping_rows = load_jsonl(REBENCH / "02_benchmark_ability_mapping.jsonl")
    known = {row["benchmark_id"] for row in mapping_rows}
    c.true(
        f"benchmarks: ids outside the mapping table: {sorted(set(bench_ids) - known)}",
        set(bench_ids) <= known,
    )
    evidence_ids = {row["benchmark_id"] for row in evidence}
    c.eq("benchmarks/id-set", set(bench_ids), evidence_ids)
    for bench in payload["benchmarks"]:
        c.true(f"benchmarks/{bench['id']}: empty one_liner", bool(bench["one_liner"]))
        c.true(f"benchmarks/{bench['id']}: no sections", bool(bench["sections"]))
        c.true(f"benchmarks/{bench['id']}: no confidence", bench["confidence"] is not None)

    # --- benchmark leaderboards re-derived from evidence ------------------
    rows_by_bench = collections.defaultdict(lambda: collections.defaultdict(list))
    for row in evidence:
        if row.get("source_type") == "capability_gap_zero" or row.get("score_10") is None:
            continue
        rows_by_bench[row["benchmark_id"]][row["model_key"]].append(row)
    for bench in payload["benchmarks"]:
        groups = rows_by_bench[bench["id"]]
        c.eq(f"benchmarks/{bench['id']}/n_results", len(bench["results"]), len(groups))
        for result in bench["results"]:
            rows = groups.get(result["m"])
            if not rows:
                c.errors.append(f"benchmarks/{bench['id']}/{result['m']}: no evidence rows")
                continue
            want = sum(r["score_10"] * r["effective_weight"] for r in rows) / sum(
                r["effective_weight"] for r in rows
            )
            c.eq(f"benchmarks/{bench['id']}/{result['m']}/s", result["s"], want)
        ranks = [r["s"] for r in bench["results"]]
        c.true(f"benchmarks/{bench['id']}: results not sorted", ranks == sorted(ranks, reverse=True))

    # --- referential closure ---------------------------------------------
    bench_id_set = set(bench_ids)
    p_codes = {a["p_code"] for a in payload["abilities"]}
    group_ids = {g["id"] for g in payload["groups"]}
    # Cell weights are re-read straight from the evidence rows: the payload must
    # never invent a weight the aggregator did not stamp.
    ev_weights = {}
    for row in evidence:
        ev_weights.setdefault(
            (row["p_code"], row["facet_id"], row["benchmark_id"], row["subdimension"]),
            (row["ability_weight"], row["row_weight"], row["effective_weight"]),
        )
    for ability in payload["abilities"]:
        code = ability["p_code"]
        c.true(f"abilities/{code}: unknown group", ability["group"] in group_ids)
        c.true(f"abilities/{code}: empty definition", bool(ability["definition"]))
        c.true(f"abilities/{code}: empty one_liner", bool(ability["one_liner"]))
        c.true(f"abilities/{code}: no profile sections", bool(ability["sections"]))
        share_total = 0.0
        for facet in ability["facets"]:
            for cell in facet["cells"]:
                c.true(
                    f"abilities/{code}/{facet['id']}: unknown benchmark {cell['b']}",
                    cell["b"] in bench_id_set,
                )
                want = ev_weights.get((code, facet["id"], cell["b"], cell["sd"]))
                if want is None:
                    c.errors.append(
                        f"abilities/{code}/{facet['id']}/{cell['b']}·{cell['sd']}: no evidence row"
                    )
                    continue
                c.eq(f"abilities/{code}/{facet['id']}/{cell['b']}/rel", cell["rel"], want[0])
                c.eq(f"abilities/{code}/{facet['id']}/{cell['b']}/conf", cell["conf"], want[1])
                c.eq(f"abilities/{code}/{facet['id']}/{cell['b']}/eff", cell["eff"], want[2])
                share_total += cell["share"]
        # Nominal shares partition the P score, so they sum to 1 wherever there
        # is any evidence at all, and to 0 for the uncovered abilities.
        c.eq(f"abilities/{code}/share-sum", round(share_total, 9), 0.0 if code in payload["meta"]["uncovered_p"] else 1.0)
    for key in payload["scores"]:
        model_key, _, p_code = key.rpartition("|")
        c.true(f"scores/{key}: unknown model", model_key in model_keys)
        c.true(f"scores/{key}: unknown ability", p_code in p_codes)
    for key in payload["groupScore"]:
        model_key, _, group = key.rpartition("|")
        c.true(f"groupScore/{key}: unknown model", model_key in model_keys)
        c.true(f"groupScore/{key}: unknown group", group in group_ids)
    for bench in payload["benchmarks"]:
        for p_code in bench["abilities"]:
            c.true(f"benchmarks/{bench['id']}: unknown ability {p_code}", p_code in p_codes)
        for result in bench["results"]:
            c.true(f"benchmarks/{bench['id']}: unknown model {result['m']}", result["m"] in model_keys)

    # --- abilityRank agrees with scores -----------------------------------
    c.eq("abilityRank/keys", set(payload["abilityRank"]), p_codes)
    for p_code, ranked in payload["abilityRank"].items():
        want = {k.split("|")[0]: v["s"] for k, v in payload["scores"].items() if k.endswith("|" + p_code)}
        c.eq(f"abilityRank/{p_code}/count", len(ranked), len(want))
        for entry in ranked:
            c.eq(f"abilityRank/{p_code}/{entry['m']}", entry["s"], want.get(entry["m"]))
        order = [r["s"] for r in ranked]
        c.true(f"abilityRank/{p_code}: not sorted", order == sorted(order, reverse=True))
    for p_code in payload["meta"]["uncovered_p"]:
        c.eq(f"abilityRank/{p_code}: should be empty", len(payload["abilityRank"][p_code]), 0)

    # --- meta counts ------------------------------------------------------
    meta = payload["meta"]
    c.eq("meta/n_models", meta["n_models"], len(payload["models"]))
    c.eq("meta/n_benchmarks", meta["n_benchmarks"], len(payload["benchmarks"]))
    c.eq("meta/n_abilities_total", meta["n_abilities_total"], len(payload["abilities"]))
    covered = {k.split("|")[1] for k in payload["scores"]}
    c.eq("meta/n_abilities_covered", meta["n_abilities_covered"], len(covered))
    c.eq("meta/uncovered_p", set(meta["uncovered_p"]), p_codes - covered)
    c.true("boundaries: empty", bool(payload["boundaries"]))

    return c


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("payload", type=Path, help="path to agentic.json")
    args = parser.parse_args()

    if not args.payload.exists():
        print(f"payload not found: {args.payload}", file=sys.stderr)
        return 2

    checker = validate(json.loads(args.payload.read_text(encoding="utf-8")))
    if checker.errors:
        print(f"FAILED: {len(checker.errors)} of {checker.checks} checks", file=sys.stderr)
        for error in checker.errors[:40]:
            print(f"  - {error}", file=sys.stderr)
        if len(checker.errors) > 40:
            print(f"  ... and {len(checker.errors) - 40} more", file=sys.stderr)
        return 1
    print(f"OK: {checker.checks} checks passed on {args.payload}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
