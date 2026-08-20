#!/usr/bin/env python3
"""Validate a generated `agentic.json` against the rebenchmark artifacts.

`build_site_payload.py` reshapes; this script independently re-derives every
number straight from `reports/atomic_ability_rebenchmark/*.jsonl`
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
REBENCH = ROOT / "reports" / "atomic_ability_rebenchmark"
FLOOR_DIR = ROOT / "reports" / "atomic_ability_l1_floor"
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
        # The cell lists are what the site names on screen, so they must match
        # the counts they sit next to and the source's own untested inventory.
        c.eq(f"scores/{key}/zc", len(entry["zc"]), row["capability_zero_count"])
        c.eq(f"scores/{key}/uc", len(entry["uc"]), row["untested_cell_count"])
        c.eq(
            f"scores/{key}/uc/cells",
            sorted({f'{cell["b"]} · {cell["sd"]}' for cell in entry["uc"]}),
            sorted(row["untested_cells"]),
        )

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

    # --- the text-only board ----------------------------------------------
    # Re-derived from its own artifact, exactly like the main board is: the
    # payload must not be the only place these numbers exist.
    text_p = [
        r for r in load_jsonl(REBENCH / "09_atomic_p_scores_text_only.jsonl")
        if r["score_10"] is not None
    ]
    text_by_model = collections.defaultdict(list)
    for row in text_p:
        text_by_model[row["model_key"]].append(round(row["score_10"], 4))
    for model in payload["models"]:
        key = model["key"]
        got = text_by_model.get(key, [])
        c.eq(
            f"models/{key}/overallText",
            model["overallText"],
            statistics.fmean(got) if got else None,
        )
        c.eq(f"models/{key}/n_ability_text", model["n_ability_text"], len(got))
        # Three states. `None` means never probed and must survive as null — a
        # payload that turned it into False would be claiming the model has no
        # vision, which is a different (and unevidenced) statement.
        c.true(
            f"models/{key}/vision: not tri-state ({model['vision']!r})",
            model["vision"] in (True, False, None),
        )
        c.eq(
            f"models/{key}/vision",
            model["vision"],
            explorer.agg.MODEL_CAPABILITIES.get(key, {}).get("vision"),
        )
    # The whole point of this board is one yardstick, so every panel model has
    # to be scored over the *same* abilities. If a future panel member is short
    # a non-visual ability this fires, and it should: the board would be
    # comparing models over different denominators without saying so.
    panel_text_sets = {
        m["key"]: frozenset(r["p_code"] for r in text_p if r["model_key"] == m["key"])
        for m in payload["models"] if m["full"]
    }
    c.eq(
        "models: panel models scored over different abilities on the text board "
        f"({ {k: len(v) for k, v in panel_text_sets.items()} })",
        len(set(panel_text_sets.values())),
        1,
    )
    text_groups = load_jsonl(REBENCH / "10_group_scores_text_only.jsonl")
    c.eq("groupScoreText/count", len(payload["groupScoreText"]), len(text_groups))
    for row in text_groups:
        gkey = f"{row['model_key']}|{row['group']}"
        c.eq(f"groupScoreText/{gkey}", payload["groupScoreText"].get(gkey), round(row["score_10"], 4))
    masked = {(cell["b"], cell["sd"]) for cell in payload["meta"]["text_only"]["masked_cells"]}
    c.eq("meta/text_only/masked_cells", masked, set(explorer.agg.masked_cells()))
    c.true("meta/text_only/masked_cells: empty", bool(masked))
    c.eq(
        "meta/text_only/n_abilities",
        payload["meta"]["text_only"]["n_abilities"],
        len({r["p_code"] for r in text_p}),
    )
    # A masked cell must leave no trace in the text-only evidence: if one shows
    # up there the mask was applied after aggregation, not before, and the
    # scores are the wrong ones.
    text_ev = load_jsonl(REBENCH / "09_atomic_p_score_evidence_text_only.jsonl")
    leaked = {(r["benchmark_id"], r["subdimension"]) for r in text_ev} & masked
    c.eq(f"text-only evidence: masked cells leaked through {sorted(leaked)}", leaked, set())
    # And no capability-gap zeros can survive there: the cells that could gate
    # on vision are gone, so nothing is left to be gated on.
    c.eq(
        "text-only evidence: capability-gap zeros should not exist",
        sum(1 for r in text_ev if r.get("source_type") == "capability_gap_zero"),
        0,
    )

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

    # --- the tier layer above the groups ---------------------------------
    # Presentation-only: it carries no score, so there is nothing here to
    # re-derive from the artifacts - what has to hold is that it is a clean
    # partition of the groups and that the two orderings agree, because the
    # site renders tiers in `tiers` order and fills each from `groups` order.
    tiers = payload["tiers"]
    c.true("tiers: empty", bool(tiers))
    tier_ids = [t["id"] for t in tiers]
    c.eq("tiers: duplicate id", len(set(tier_ids)), len(tier_ids))
    for tier in tiers:
        c.true(f"tiers/{tier['id']}: empty id or label", bool(tier["id"]) and bool(tier["label"]))
    blocks: list[str] = []
    for group in payload["groups"]:
        tier = group.get("tier")
        c.true(f"groups/{group['id']}: unknown tier {tier!r}", tier in set(tier_ids))
        if not blocks or blocks[-1] != tier:
            blocks.append(tier)
    # Collapsing the group list to its runs of `tier` must reproduce `tiers`
    # exactly: that catches an interleaved group (a run repeating), a tier with
    # no groups, and a tier order that disagrees with the group order - each of
    # which would put a group under the wrong heading on the site. Every group
    # carries exactly one `tier`, so coverage and disjointness come for free.
    c.eq("groups: tier blocks do not match tiers", blocks, tier_ids)
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

    # --- L1 floor re-derived from the floor artifacts ---------------------
    # `build_site_payload` recomputes the floor from the baseline JSON; this
    # side reads the committed `reports/atomic_ability_l1_floor/*.jsonl`
    # instead, so the two only agree when the report has been regenerated
    # against the same baselines. A mismatch here means: rerun
    # `scripts/build_l1_floor_profile.py`.
    floor = payload.get("floor")
    c.true("floor: missing from payload", isinstance(floor, dict))
    if isinstance(floor, dict):
        floor_cells = load_jsonl(FLOOR_DIR / "01_l1_floor_cells.jsonl")
        floor_evidence = load_jsonl(FLOOR_DIR / "02_l1_floor_evidence.jsonl")
        floor_p = load_jsonl(FLOOR_DIR / "03_l1_floor_p_scores.jsonl")

        c.eq("floor/p/count", len(floor["p"]), len([r for r in floor_p if r["score_10"] is not None]))
        for row in floor_p:
            if row["score_10"] is None:
                continue
            c.eq(f"floor/p/{row['p_code']}", floor["p"].get(row["p_code"]), round(row["score_10"], 4))

        c.eq(
            "floor/overall",
            floor["overall"],
            round(
                statistics.fmean(
                    round(r["score_10"], 4) for r in floor_p if r["score_10"] is not None
                ),
                4,
            ),
        )

        c.eq("floor/cell/count", len(floor["cell"]), len(floor_cells))
        for row in floor_cells:
            key = f"{row['benchmark_id']}|{row['subdimension']}"
            entry = floor["cell"].get(key)
            if entry is None:
                c.errors.append(f"floor/cell/{key}: missing")
                continue
            c.eq(f"floor/cell/{key}/s", entry["s"], round(row["score_10"], 4))
            c.eq(f"floor/cell/{key}/v", entry["v"], row["raw_value"])
            c.eq(f"floor/cell/{key}/src", entry["src"], row["l1_source"])

        # Benchmark floors use the same weighted mean as the real leaderboards -
        # the two numbers sit on the same bar on screen, so they must be built
        # the same way.
        floor_by_bench = collections.defaultdict(list)
        for row in floor_evidence:
            floor_by_bench[row["benchmark_id"]].append(row)
        c.eq("floor/bench/count", len(floor["bench"]), len(floor_by_bench))
        for bench, rows in floor_by_bench.items():
            want = sum(r["score_10"] * r["effective_weight"] for r in rows) / sum(
                r["effective_weight"] for r in rows
            )
            c.eq(f"floor/bench/{bench}", floor["bench"].get(bench), round(want, 4))

        # Referential closure: a floor may be missing (an undefined L1), but it
        # must never name an ability, benchmark or cell the site does not have.
        site_cells = {
            (cell["b"], cell["sd"])
            for ability in payload["abilities"]
            for facet in ability["facets"]
            for cell in facet["cells"]
        }
        for p_code in floor["p"]:
            c.true(f"floor/p/{p_code}: unknown ability", p_code in p_codes)
        for bench in floor["bench"]:
            c.true(f"floor/bench/{bench}: unknown benchmark", bench in bench_id_set)
        for key in floor["cell"]:
            bench, _, sub = key.partition("|")
            c.true(f"floor/cell/{key}: not a scored cell", (bench, sub) in site_cells)
        c.eq("floor/meta/n_cells", floor["meta"]["n_cells"], len(floor["cell"]))
        c.eq("floor/meta/n_benchmarks", floor["meta"]["n_benchmarks"], len(floor["bench"]))

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
