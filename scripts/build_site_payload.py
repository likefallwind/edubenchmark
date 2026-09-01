#!/usr/bin/env python3
"""Build the AgenticEdu Continuum website payload (`agentic.json`).

This is a *reshaping* layer, not a second aggregation. Everything is derived
from `build_atomic_ability_explorer.build_payload()`, which already owns the
parsing of the v6 measurement model, the mapping doc (P definitions, boundary
rules) and the benchmark profile archive. Nothing is recomputed from the eval
tree here, and no constant is duplicated: model display names, the profile map,
group labels and the panel keys all come from the explorer module.

The website consumes a flatter, lookup-friendly shape than the explorer page:

    byJudge     dict "<judge_slug>" -> everything that carries a number
    scores      (inside byJudge) dict "<model_key>|<p_code>" -> score record
    groupScore  (inside byJudge) dict "<model_key>|<group>"  -> float
    tiers       the two presentation-layer tiers above the five groups; the
                membership is on `groups[].tier`, and no tier carries a score
    abilityRank (inside byJudge) dict "<p_code>" -> models ranked desc
    benchmarks  profile prose at the top level; the per-model leaderboard for
                each judge under `byJudge[j].benchmarks`, joined by id
    floor       (inside byJudge) the L1 (all-random) floor, per ability /
                benchmark / cell

A judged score is a reading taken with one instrument, so the site ships every
judge that has a complete enough view and lets the reader switch. The prose --
ability definitions, benchmark profiles, boundary rulings, the measurement model
-- is judge-invariant and stays at the top level rather than being copied per
judge: it would double the payload and imply the definitions move when the judge
does. What moves is only ever a number.

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
JUDGE_INDEX = ROOT / "reports" / "atomic_ability_rebenchmark" / "14_judge_views" / "index.json"

# 上站的判官。**不是**「所有判过分的判官」——deepseek-v3.2 缺 162 格、MiniMax-M2.7 缺
# 213 格，摆上去大半个页面是空的，读者只会当成 bug。够格的判据是覆盖度，写在
# 14_judge_views/index.json 里，由 edubenchmark 裁决，展示层不自己挑。
#
# 默认给 MiniMax-M3：它是 PRIMARY_JUDGE，历史数字跟它一致。它并不是覆盖最全的那个
# （212/212 是 deepseek-v4-flash），页面上要把这件事连同「M3 有 59 个自评格、
# v4-flash 有 0 个」一起说出来——留多判官的意义正是防模型给自己打高分。
SITE_JUDGES = ("MiniMax-M3", "deepseek-v4-flash")
DEFAULT_JUDGE = "MiniMax-M3"


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


def build_floor(judge: str) -> dict[str, Any]:
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
    # 判官换了，`L3:random` 那类格的地板也得换——它是把乱码交给真实判官打出来的分，
    # 是判官宽容度的读数，不是数据集属性。取不到就没有这一键（见下面 meta.undefined），
    # 页面写「没有随机地板」，绝不 fallback 成 0。
    cells, problems = floor.floor_cells(baselines, judge)
    if not cells:
        raise SystemExit(f"floor: no cells computed from {BASELINES}")
    evidence, p_rows, _groups, _untested, _incapable = floor.agg.score_atomic_p(cells)
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
    # The same floor under the text-only board. It has to be recomputed with the
    # same mask, not reused from `overall`: that one averages 18 abilities and
    # this one 16, so quoting `overall` next to a text-only score would put two
    # different denominators on the same bar.
    text_p_rows = [
        r for r in floor.agg.score_atomic_p(cells, skip_cell=floor.agg.requires_vision)[1]
        if r["model_key"] == floor.FLOOR_MODEL and r["score_10"] is not None
    ]
    return {
        "judge": judge,
        "p": per_p,
        "overallText": (
            round(statistics.fmean(r["score_10"] for r in text_p_rows), 4)
            if text_p_rows
            else None
        ),
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
            "judge": judge,
            # Benchmarks whose L1 is undefined or unbuildable: they carry no
            # floor entry, and the site has to render that as unknown rather
            # than as zero.
            "undefined": problems,
        },
    }


def build_site_payload(
    source: dict[str, Any], judge: str, weights: dict[tuple[str, str, str, str], dict[str, Any]]
) -> dict[str, Any]:
    """One judge's flat view. `weights` is shared across judges on purpose: 相关度 /
    置信 / 有效权重 是测量模型给的常数，不是读数。按单个判官的证据去取，那个判官没判
    过的格就会取到 None，同一张能力卡在两个判官下会显示不同的权重——权重并没有变。
    """
    panel = set(source["panel"])

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
    # 纯文本口径的群组分，键同形。别把它和 `groupScore` 放进同一张表比大小：
    # 同一个 group id 在两个口径下覆盖的 P 不一样（SRG 少了 P03/P04）。
    group_score_text = {f"{row['m']}|{row['g']}": row["s"] for row in source["group_scores_text"]}

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
            # 模态三态：true 实测有视觉 / false 实测没有 / null 从没探测过。
            # null 不是 false——网站要能说「未探测」，不能替源头下结论。
            "vision": m["vision"],
            # 纯文本口径的综合分（屏蔽由视觉定义的取分维度后重算）。和 `overall`
            # 不同底，两个数字永远不要相减或混排。
            "overallText": m["text_score"],
            "n_ability_text": m["text_p_count"],
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
        "groupScoreText": group_score_text,
        "abilityRank": ability_rank,
        "benchmarks": benchmarks,
        "panel": source["panel"],
        "floor": build_floor(judge),
    }


# 判官无关的块：定义、口径、散文。它们是测量模型，不是读数——换判官不该动一个字。
SHARED_KEYS = ("tiers", "groups", "abilities", "boundaries")
# 一个 benchmark 档案里判官无关的部分；`abilities` 与 `results` 是读数，进 byJudge。
BENCH_PROSE = ("id", "name", "one_liner", "family", "confidence", "rationale", "sections")
# meta 里判官无关的部分。其余（模型数、覆盖数、证据数……）每个判官各有一份。
META_SHARED = ("version", "date", "source_dir", "n_abilities_total", "n_benchmarks")


def judge_roster() -> list[dict[str, Any]]:
    """上站判官的名册 + 覆盖度，取自 edubenchmark 的判官视图索引。

    覆盖度和自评格数要一路带到页面上：读者得看见「这把尺子量到了多少」和「这把尺子
    有没有在给自己打分」，否则切换器就只是两组无从比较的数字。
    """
    index = json.loads(JUDGE_INDEX.read_text(encoding="utf-8"))
    by_judge = {v["judge"]: v for v in index["views"]}
    roster = []
    for judge in SITE_JUDGES:
        view = by_judge.get(judge)
        if view is None:
            raise SystemExit(f"judge {judge!r} 不在 {JUDGE_INDEX} 里——先跑一次聚合")
        roster.append(
            {
                "id": view["slug"],
                "judge": judge,
                "label": judge,
                "covered": view["covered"],
                "reachable": view["reachable"],
                "complete": view["complete"],
                "selfJudged": view["self_judged_cells"],
                "incapableBenchmarks": view["incapable_benchmarks"],
            }
        )
    return roster


def merge_judges(views: dict[str, dict[str, Any]], roster: list[dict[str, Any]]) -> dict[str, Any]:
    """把每个判官的扁平结构合成一份 payload：共享的提到顶层，带数字的留在 byJudge。"""
    first = views[roster[0]["id"]]
    for key in SHARED_KEYS:
        for slug, view in views.items():
            if view[key] != first[key]:
                # 定义/口径不该因判官而异。真不一样就是上游出了岔子，宁可炸也不要
                # 悄悄挑一个——页面会拿着 A 判官的定义去解释 B 判官的数字。
                raise SystemExit(f"判官无关的 {key!r} 在 {slug} 下与 {roster[0]['id']} 不一致")
    # 档案散文取全部判官的并集：deepseek-v4-flash 判不了 eduillustrate，它的视图里
    # 就没有那个 benchmark——但页面不能因此少一页。少了，另一个判官下存在的链接会 404，
    # 而真相是「这把尺子读不了它」，不是「没有这个测评集」。
    prose: dict[str, dict[str, Any]] = {}
    for view in views.values():
        for b in view["benchmarks"]:
            prose.setdefault(b["id"], {k: b[k] for k in BENCH_PROSE})
    order = [b["id"] for b in first["benchmarks"]]
    order += [bid for bid in sorted(prose) if bid not in order]

    payload: dict[str, Any] = {
        "meta": dict(
            {k: first["meta"][k] for k in META_SHARED},
            judges=roster,
            defaultJudge=next(r["id"] for r in roster if r["judge"] == DEFAULT_JUDGE),
        ),
        **{k: first[k] for k in SHARED_KEYS},
        # 顺序沿用主判官那份（按榜单行数降序），换判官不重排——切一下判官整页卡片
        # 跳一遍位置，读者会以为数据变了。
        "benchmarks": [prose[bid] for bid in order],
        "byJudge": {},
    }
    blind_by_slug = {r["id"]: set(r["incapableBenchmarks"]) for r in roster}
    for slug, view in views.items():
        have = {b["id"]: b for b in view["benchmarks"]}
        blind = blind_by_slug[slug]
        bench_rows = []
        for bid in order:
            b = have.get(bid)
            if b is not None:
                bench_rows.append({"id": bid, "abilities": b["abilities"], "results": b["results"]})
            else:
                # 空榜要说清是哪一种空：判官读不了图（blind）vs 这个测评集没人跑过。
                # 前者换个判官就有，后者换谁都没有。
                bench_rows.append(
                    {"id": bid, "abilities": [], "results": [], "blind": bid in blind}
                )
        payload["byJudge"][slug] = {
            "meta": {k: v for k, v in view["meta"].items() if k not in META_SHARED},
            "models": view["models"],
            "scores": view["scores"],
            "groupScore": view["groupScore"],
            "groupScoreText": view["groupScoreText"],
            "abilityRank": view["abilityRank"],
            "panel": view["panel"],
            "benchmarks": bench_rows,
            "floor": view["floor"],
        }
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out",
        type=Path,
        default=DEFAULT_OUT,
        help=f"where to write agentic.json (default: {DEFAULT_OUT})",
    )
    parser.add_argument(
        "--judge",
        default=None,
        help="只出这一个判官（调试用）。默认出 SITE_JUDGES 全部。",
    )
    args = parser.parse_args()

    explorer = load_explorer()
    roster = judge_roster()
    if args.judge:
        roster = [r for r in roster if r["judge"] == args.judge or r["id"] == args.judge]
        if not roster:
            raise SystemExit(f"--judge {args.judge!r} 不在 SITE_JUDGES {SITE_JUDGES} 里")

    sources = {r["id"]: explorer.build_payload(r["judge"]) for r in roster}
    # 权重跨判官共用：见 build_site_payload 的 docstring。取全部判官证据的并集，
    # 缺任何一个判官都不会让某一格的权重变成 None。
    weights = cell_weights([row for src in sources.values() for row in src["evidence"]])
    views = {
        r["id"]: build_site_payload(sources[r["id"]], r["judge"], weights) for r in roster
    }
    payload = merge_judges(views, roster)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    meta = payload["meta"]
    size_kb = args.out.stat().st_size / 1024
    print(f"wrote {args.out} ({size_kb:.0f} KB)")
    print(f"  {meta['version']} · {meta['date']} · {meta['n_benchmarks']} benchmarks "
          f"· 默认判官 {meta['defaultJudge']}")
    for entry in meta["judges"]:
        view = payload["byJudge"][entry["id"]]
        m = view["meta"]
        mark = "✅" if entry["complete"] else f"缺 {entry['reachable'] - entry['covered']}"
        print(
            f"  [{entry['id']}] {entry['judge']} · 覆盖 {entry['covered']}/{entry['reachable']} {mark}"
            f" · 自评格 {entry['selfJudged']}"
        )
        print(
            f"      {m['n_models']} models ({m['full_panel_size']} full panel) · "
            f"{m['n_abilities_covered']}/{meta['n_abilities_total']} abilities · "
            f"{m['n_evidence']} evidence rows"
        )
        if m.get("judge_incapable_p"):
            print(f"      判官判不了：{'、'.join(m['judge_incapable_p'])}")
        floor = view["floor"]
        print(
            f"      L1 floor: {len(floor['p'])} abilities · {floor['meta']['n_benchmarks']} "
            f"benchmarks · {floor['meta']['n_cells']} cells"
        )
        for problem in floor["meta"]["undefined"]:
            print(f"      ! floor: {problem}")


if __name__ == "__main__":
    main()
