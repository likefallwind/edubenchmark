#!/usr/bin/env python3
"""Build the AgenticEdu Continuum website payload (`agentic.json`).

This is a *reshaping* layer, not a second aggregation. Everything is derived
from `build_atomic_ability_explorer.build_payload()`, which already owns the
parsing of the v6 measurement model, the mapping doc (P definitions, boundary
rules) and the benchmark profile archive. Nothing is recomputed from the eval
tree here, and no constant is duplicated: model display names, the profile map,
group labels and the panel keys all come from the explorer module.

The website consumes a flatter, lookup-friendly shape than the explorer page:

    scores      dict "<model_key>|<p_code>" -> score record
    groupScore  dict "<model_key>|<group>"  -> float
    tiers       the two presentation-layer tiers above the five groups; the
                membership is on `groups[].tier`, and no tier carries a score
    abilityRank dict "<p_code>"             -> models ranked desc
    benchmarks  profile prose + the per-model leaderboard already joined in
    floor       the L1 (all-random) floor, per ability / benchmark / cell

The floor block is the one thing here that does not come from the explorer: it
is rebuilt by calling `build_l1_floor_profile` (same aggregation chain, no API
calls, ~40 ms) so it can never drift from `data/benchmark_baselines_v1.json`.

Usage:
    python scripts/build_site_payload.py [--out ../agenticeducontinnum/data/agentic.json]

The payload carries no `svgs` key - the four decorative SVGs are website
artwork and live in the website repo (`data/svgs.json`).
"""

from __future__ import annotations

import argparse
import collections
import importlib.util
import json
import statistics
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
EXPLORER = ROOT / "scripts" / "build_atomic_ability_explorer.py"
FLOOR = ROOT / "scripts" / "build_l1_floor_profile.py"
BASELINES = ROOT / "data" / "benchmark_baselines_v1.json"
DEFAULT_OUT = ROOT.parent / "agenticeducontinnum" / "data" / "agentic.json"


def load_script(path: Path, name: str):
    """Import a build script by path (their filenames are not importable)."""
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_explorer():
    return load_script(EXPLORER, "_explorer")


def cell_weights(evidence: list[dict[str, Any]]) -> dict[tuple[str, str, str, str], dict[str, Any]]:
    """Relevance / confidence / effective weight per (P, facet, benchmark, sub).

    All three are stamped onto every evidence row at aggregation time and are
    constant across models, so the first row for a cell is authoritative. The
    website must not re-derive `eff` as rel x conf: a handful of cells carry a
    per-subdimension confidence override that only the aggregator knows about.
    """
    out: dict[tuple[str, str, str, str], dict[str, Any]] = {}
    for row in evidence:
        out.setdefault(
            (row["p"], row["f"], row["b"], row["sd"]),
            {"rel": row["rel"], "conf": row["conf"], "eff": row["eff"]},
        )
    return out


def build_floor() -> dict[str, Any]:
    """The L1 floor — what a model that answers everything at random scores.

    Three levels, because the site quotes a score at three levels: per ability
    (the floor under a P score), per benchmark (the floor under a benchmark
    leaderboard) and per cell (the floor under one subdimension, which is where
    the number actually comes from). The benchmark figure is the same
    effective-weight-weighted mean of evidence rows the real leaderboard uses,
    so a floor and a model score on the same page are computed identically and
    can be read against each other.

    This is *not* a chance correction: nothing subtracts the floor from a
    published score. It ships alongside so a reader can see how much of a score
    was free.
    """
    floor = load_script(FLOOR, "_l1_floor")
    baselines = json.loads(BASELINES.read_text(encoding="utf-8"))
    cells, problems = floor.floor_cells(baselines)
    if not cells:
        raise SystemExit(f"floor: no cells computed from {BASELINES}")
    evidence, p_rows, _groups, _untested = floor.agg.score_atomic_p(cells)
    # score_atomic_p also emits R26 capability-gap rows for the real panel
    # models; only the synthetic floor model belongs here.
    evidence = [r for r in evidence if r["model_key"] == floor.FLOOR_MODEL]
    p_rows = [r for r in p_rows if r["model_key"] == floor.FLOOR_MODEL]

    by_bench: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    for row in evidence:
        by_bench[row["benchmark_id"]].append(row)

    per_p = {
        row["p_code"]: round(row["score_10"], 4)
        for row in p_rows
        if row["score_10"] is not None
    }
    return {
        "p": per_p,
        # Comparable to a model's `overall`, which is the same plain mean over
        # the same abilities - a full-panel model covers exactly these.
        "overall": round(statistics.fmean(per_p.values()), 4),
        "bench": {
            bench: round(
                sum(r["score_10"] * r["effective_weight"] for r in rows)
                / sum(r["effective_weight"] for r in rows),
                4,
            )
            for bench, rows in by_bench.items()
        },
        # `v` is the metric's own raw value (an accuracy, a share, a QWK), kept
        # because "chance = 0.25" explains a 2.5 far better than the 2.5 does.
        # `src` says how it was obtained: simulated:<policy> | L3:random | analytic.
        "cell": {
            f'{c["benchmark_id"]}|{c["subdimension"]}': {
                "s": round(c["score_10"], 4),
                "v": c["raw_value"],
                "src": c["l1_source"],
            }
            for c in cells
        },
        "meta": {
            "layer": "L1",
            "n_cells": len(cells),
            "n_benchmarks": len(by_bench),
            "source": "data/benchmark_baselines_v1.json",
            "report": "reports/atomic_ability_l1_floor/04_l1_floor_report.md",
            # Benchmarks whose L1 is undefined or unbuildable: they carry no
            # floor entry, and the site has to render that as unknown rather
            # than as zero.
            "undefined": problems,
        },
    }


def build_site_payload(source: dict[str, Any]) -> dict[str, Any]:
    panel = set(source["panel"])
    weights = cell_weights(source["evidence"])

    # --- abilities: keep only what the site renders -----------------------
    # Each cell carries its own weight breakdown plus `share`, the fraction of
    # the P score it accounts for *when a model has every cell measured*: facets
    # are averaged equally, cells within a facet by effective weight. A model
    # missing cells shifts the real split, which is why the page labels this the
    # nominal share rather than that model's actual one.
    abilities = []
    for a in source["abilities"]:
        scored_facets = [f for f in a["facets"] if f["cells"]]
        facet_share = 1 / len(scored_facets) if scored_facets else 0.0
        facets = []
        for f in a["facets"]:
            cells = []
            eff_total = sum(
                weights.get((a["p_code"], f["facet_id"], c["benchmark_id"], c["subdimension"]), {}).get("eff") or 0.0
                for c in f["cells"]
            )
            for c in f["cells"]:
                w = weights.get(
                    (a["p_code"], f["facet_id"], c["benchmark_id"], c["subdimension"]), {}
                )
                eff = w.get("eff")
                cells.append(
                    {
                        "b": c["benchmark_id"],
                        "sd": c["subdimension"],
                        "w": c["weight"],
                        "rel": w.get("rel", c["weight"]),
                        "conf": w.get("conf"),
                        "eff": eff,
                        "share": (eff / eff_total * facet_share) if eff and eff_total else 0.0,
                    }
                )
            facets.append(
                {
                    "id": f["facet_id"],
                    "name": f["facet_name"],
                    "desc": f["facet_description"],
                    "share": facet_share if f["cells"] else 0.0,
                    "cells": cells,
                }
            )
        abilities.append(
            {
                "p_code": a["p_code"],
                "p_name": a["p_name"],
                "group": a["group"],
                "definition": a["definition"],
                "one_liner": a["profile"]["one_liner"],
                "sections": [
                    {"heading": s["heading"], "bullets": s["bullets"]}
                    for s in a["profile"]["sections"]
                ],
                "facets": facets,
            }
        )

    # --- scores / groupScore / abilityRank --------------------------------
    # R26 gives a missing cell one of two verdicts, and the site has to name the
    # cell to explain either one, so both are listed per (model, P) rather than
    # only counted: `zc` = capability-gap zeros (scored 0, counted, `cap` says
    # which capability the model lacks), `uc` = untested (no score, no
    # denominator). The counts `zero` / `unt` stay as the cheap read. Each entry
    # carries its facet id, because the same cell can be mounted on two facets of
    # one P and the site marks cells inside their facet.
    zero_cells: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    for row in source["evidence"]:
        if row["zero"]:
            zero_cells[f"{row['m']}|{row['p']}"].append(
                {"f": row["f"], "b": row["b"], "sd": row["sd"], "cap": row["cap"]}
            )
    untested_cells: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    for row in source["untested"]:
        untested_cells[f"{row['m']}|{row['p']}"].append(
            {"f": row["f"], "b": row["b"], "sd": row["sd"]}
        )

    scores = {}
    for row in source["scores"]:
        key = f"{row['m']}|{row['p']}"
        scores[key] = {
            "s": row["s"],
            "facets": row["facets"],
            "n": row["n"],
            "zero": row["zero"],
            "zerow": row["zerow"],
            "zc": sorted(zero_cells.get(key, []), key=lambda c: (c["b"], c["sd"], c["f"])),
            "unt": row["unt"],
            "uc": sorted(untested_cells.get(key, []), key=lambda c: (c["b"], c["sd"], c["f"])),
            "nf": row["nf"],
            "b": row["b"],
        }
    group_score = {f"{row['m']}|{row['g']}": row["s"] for row in source["group_scores"]}

    # Every P gets a key, including the two with no benchmark yet - the site
    # reads `abilityRank[p_code]` unguarded to show the "N models" count.
    ability_rank: dict[str, list[dict[str, Any]]] = {a["p_code"]: [] for a in abilities}
    for row in source["scores"]:
        ability_rank[row["p"]].append(
            {"m": row["m"], "s": row["s"], "zero": row["zero"], "full": row["m"] in panel}
        )
    for rows in ability_rank.values():
        rows.sort(key=lambda r: (-r["s"], r["m"]))

    # --- models: overall is the plain mean of that model's P scores -------
    by_model: dict[str, list[float]] = collections.defaultdict(list)
    for row in source["scores"]:
        by_model[row["m"]].append(row["s"])
    models = [
        {
            "key": m["key"],
            "display": m["display"],
            "full": m["full_panel"],
            "overall": statistics.fmean(by_model[m["key"]]),
            "n_ability": m["p_count"],
            "n_evidence": m["evidence_count"],
        }
        for m in source["models"]
    ]
    models.sort(key=lambda m: (-m["overall"], m["key"]))

    # --- benchmarks: profile prose + per-model leaderboard ----------------
    # A benchmark's headline number is the effective-weight-weighted mean of
    # its evidence rows - the same weights the P scores use, so the benchmark
    # page and the ability page cannot disagree about which model did better.
    # Capability-gap zeros are excluded from a benchmark's leaderboard: the model
    # never produced an answer there, so the 0 is a statement about the model's
    # capability, not a measurement made on this benchmark. It still counts in the
    # P scores, where the capability gap is exactly what is being reported.
    rows_by_bench: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    for row in source["evidence"]:
        if row["zero"] or row["s"] is None:
            continue
        rows_by_bench[row["b"]].append(row)

    benchmarks = []
    for bench in source["benchmarks"]:
        rows = rows_by_bench.get(bench["id"], [])
        by_key: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
        for row in rows:
            by_key[row["m"]].append(row)
        results = [
            {
                "m": key,
                "s": sum(r["s"] * r["eff"] for r in group) / sum(r["eff"] for r in group),
                "full": key in panel,
            }
            for key, group in by_key.items()
        ]
        results.sort(key=lambda r: (-r["s"], r["m"]))
        benchmarks.append(
            {
                "id": bench["id"],
                # The profile's own H1 wins: the mapping table names all nine
                # MathTutorBench sub-tasks "MathTutorBench", which would give
                # nine identically titled pages.
                "name": bench["profile"].get("title") or bench["name"],
                "one_liner": bench["profile"]["one_liner"],
                "family": bench["metric_family"],
                "confidence": bench["confidence"],
                "rationale": bench["rationale"],
                "sections": [
                    {"heading": s["heading"], "bullets": s["bullets"]}
                    for s in bench["profile"]["sections"]
                ],
                "abilities": sorted({r["p"] for r in rows}),
                "results": results,
            }
        )
    benchmarks.sort(key=lambda b: (-len(b["results"]), b["id"]))

    return {
        "meta": source["meta"],
        "tiers": source["tiers"],
        "groups": source["groups"],
        "abilities": abilities,
        "boundaries": source["boundaries"],
        "models": models,
        "scores": scores,
        "groupScore": group_score,
        "abilityRank": ability_rank,
        "benchmarks": benchmarks,
        "panel": source["panel"],
        "floor": build_floor(),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out",
        type=Path,
        default=DEFAULT_OUT,
        help=f"where to write agentic.json (default: {DEFAULT_OUT})",
    )
    args = parser.parse_args()

    payload = build_site_payload(load_explorer().build_payload())
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    meta = payload["meta"]
    size_kb = args.out.stat().st_size / 1024
    print(f"wrote {args.out} ({size_kb:.0f} KB)")
    print(
        f"  {meta['version']} · {meta['date']} · {meta['n_models']} models "
        f"({meta['full_panel_size']} full panel) · {meta['n_abilities_covered']}"
        f"/{meta['n_abilities_total']} abilities · {meta['n_benchmarks']} benchmarks "
        f"· {meta['n_evidence']} evidence rows"
    )
    floor = payload["floor"]
    print(
        f"  L1 floor: {len(floor['p'])} abilities · {floor['meta']['n_benchmarks']} benchmarks "
        f"· {floor['meta']['n_cells']} cells"
    )
    for problem in floor["meta"]["undefined"]:
        print(f"  ! floor: {problem}")


if __name__ == "__main__":
    main()
