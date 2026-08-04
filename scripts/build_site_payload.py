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
    abilityRank dict "<p_code>"             -> models ranked desc
    benchmarks  profile prose + the per-model leaderboard already joined in

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
DEFAULT_OUT = ROOT.parent / "agenticeducontinnum" / "data" / "agentic.json"


def load_explorer():
    """Import the explorer module by path (its filename is not importable)."""
    spec = importlib.util.spec_from_file_location("_explorer", EXPLORER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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
    scores = {
        f"{row['m']}|{row['p']}": {
            "s": row["s"],
            "facets": row["facets"],
            "n": row["n"],
            "zero": row["zero"],
            "zerow": row["zerow"],
            "unt": row["unt"],
            "nf": row["nf"],
            "b": row["b"],
        }
        for row in source["scores"]
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
        "groups": source["groups"],
        "abilities": abilities,
        "boundaries": source["boundaries"],
        "models": models,
        "scores": scores,
        "groupScore": group_score,
        "abilityRank": ability_rank,
        "benchmarks": benchmarks,
        "panel": source["panel"],
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


if __name__ == "__main__":
    main()
