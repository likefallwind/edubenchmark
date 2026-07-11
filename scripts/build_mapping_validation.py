#!/usr/bin/env python3
"""Mapping-validity health check for the atomic-ability rebenchmark (report #13).

Implements doc/mapping_validation_plan_2026-07-11.md (v2):

- Phase 0 cell audit: per (benchmark, subdimension) cell, cross-model n /
  mean / SD and ``variance_restricted`` (ceiling/floor) flags. Correlations on
  variance-restricted cells never drive adjudication.
- Pre-registered measurement model: ``data/mapping_measurement_model_v1.json``
  declares each P reflective or formative (with facets). Pairs sharing a P are
  only *expected* to converge when the P is reflective or both cells sit in
  the same facet; formative cross-facet pairs are reported as
  ``facet_distinct_expected`` and never flagged.
- Convergent validity: cross-model Spearman rho per pair with permutation p
  (exact for n<=8, Monte Carlo above), bootstrap 90% CI, and a partial rank
  correlation controlling each model's overall mean score (sensitivity check).
- Discriminant validity: rho distribution of cross-family pairs sharing *no*
  P as the baseline that convergent pairs must beat.
- Method halo: per benchmark family, mean within-family rho minus mean
  cross-family rho.
- Ratings per plan section 2.6: validated / flagged / watch / provisional /
  variance_restricted, rolled up to P x cell grid ratings.

Outputs (idempotent, into the rebenchmark directory):
  13_mapping_validation_cells.jsonl
  13_mapping_validation_pairs.jsonl
  13_mapping_validation.md
  13_mapping_validation.html

Pure standard library. ``--validate-only`` checks input structure and pair
counts without rewriting outputs.
"""

from __future__ import annotations

import argparse
import html
import itertools
import json
import math
import random
import statistics
from collections import defaultdict
from pathlib import Path

DEFAULT_REBENCH_DIR = Path("reports/atomic_ability_rebenchmark_2026-07-08")
DEFAULT_MEASUREMENT_MODEL = Path("data/mapping_measurement_model_v1.json")

EVIDENCE_NAME = "08_selected_score_evidence.jsonl"
MAPPING_NAME = "02_benchmark_ability_mapping.jsonl"

OUT_CELLS = "13_mapping_validation_cells.jsonl"
OUT_PAIRS = "13_mapping_validation_pairs.jsonl"
OUT_MD = "13_mapping_validation.md"
OUT_HTML = "13_mapping_validation.html"

WEIGHT_MIN = 0.2

FAMILY_PREFIXES = ("mathtutorbench", "eduguard", "p08", "bea2025", "mrbench")

RATING_ORDER = [
    "validated",
    "flagged",
    "watch",
    "provisional",
    "variance_restricted",
    "insufficient_evidence",
    "single_source",
]


# ---------------------------------------------------------------------------
# Small stats helpers (stdlib only)
# ---------------------------------------------------------------------------


def rankdata(values):
    """Average ranks (1-based) with tie handling."""
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        avg = (i + j) / 2 + 1
        for k in range(i, j + 1):
            ranks[order[k]] = avg
        i = j + 1
    return ranks


def pearson(x, y):
    n = len(x)
    mx = sum(x) / n
    my = sum(y) / n
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    sxx = sum((a - mx) ** 2 for a in x)
    syy = sum((b - my) ** 2 for b in y)
    if sxx <= 0 or syy <= 0:
        return None
    return sxy / math.sqrt(sxx * syy)


def spearman(x, y):
    return pearson(rankdata(x), rankdata(y))


def permutation_pvalue(x, y, rng, n_mc=10000, exact_max_n=8):
    """Two-sided permutation p for Spearman rho.

    Uses the centered rank cross-product as the test statistic (monotone in
    rho for fixed marginal ranks), exact enumeration when n! is affordable.
    """
    rx = rankdata(x)
    ry = rankdata(y)
    n = len(rx)
    mx = sum(rx) / n
    my = sum(ry) / n
    cx = [a - mx for a in rx]
    cy = [b - my for b in ry]
    observed = abs(sum(a * b for a, b in zip(cx, cy)))
    if all(v == 0 for v in cx) or all(v == 0 for v in cy):
        return None, None
    if n <= exact_max_n:
        count = 0
        total = 0
        for perm in itertools.permutations(cy):
            total += 1
            stat = abs(sum(a * b for a, b in zip(cx, perm)))
            if stat >= observed - 1e-12:
                count += 1
        return count / total, "exact"
    count = 0
    cy_list = list(cy)
    for _ in range(n_mc):
        rng.shuffle(cy_list)
        stat = abs(sum(a * b for a, b in zip(cx, cy_list)))
        if stat >= observed - 1e-12:
            count += 1
    return (count + 1) / (n_mc + 1), "monte_carlo"


def bootstrap_ci(x, y, rng, n_boot=2000, alpha=0.10):
    """Percentile bootstrap CI for Spearman rho; degenerate replicates dropped."""
    n = len(x)
    reps = []
    na = 0
    for _ in range(n_boot):
        idx = [rng.randrange(n) for _ in range(n)]
        bx = [x[i] for i in idx]
        by = [y[i] for i in idx]
        r = spearman(bx, by)
        if r is None:
            na += 1
        else:
            reps.append(r)
    if len(reps) < n_boot * 0.5:
        return None, None, na / n_boot
    reps.sort()
    lo = reps[int(len(reps) * (alpha / 2))]
    hi = reps[min(len(reps) - 1, int(len(reps) * (1 - alpha / 2)))]
    return lo, hi, na / n_boot


def partial_spearman(x, y, z):
    """Rank partial correlation of x,y controlling z."""
    rxy = spearman(x, y)
    rxz = spearman(x, z)
    ryz = spearman(y, z)
    if rxy is None or rxz is None or ryz is None:
        return None
    den = (1 - rxz**2) * (1 - ryz**2)
    if den <= 1e-12:
        return None
    return (rxy - rxz * ryz) / math.sqrt(den)


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------


def family_of(benchmark_id):
    for prefix in FAMILY_PREFIXES:
        if benchmark_id == prefix or benchmark_id.startswith(prefix + "_"):
            return prefix
    return benchmark_id


def load_jsonl(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def load_evidence_matrix(path):
    """model_key x (benchmark_id, subdimension) -> mean score_10."""
    raw = defaultdict(list)
    for row in load_jsonl(path):
        if row.get("dedupe_status") not in (None, "selected"):
            continue
        score = row.get("score_10")
        model = row.get("model_key")
        if score is None or not model:
            continue
        cell = (row["benchmark_id"], row.get("subdimension") or "")
        raw[(cell, model)].append(float(score))
    matrix = defaultdict(dict)
    multi_run = []
    for (cell, model), scores in raw.items():
        if len(scores) > 1:
            multi_run.append({"cell": list(cell), "model_key": model, "runs": len(scores)})
        matrix[cell][model] = sum(scores) / len(scores)
    return matrix, multi_run


def load_mapping(path):
    """(benchmark_id, subdimension) -> {p_code: weight}, plus row metadata."""
    weights = {}
    meta = {}
    for row in load_jsonl(path):
        cell = (row["benchmark_id"], row.get("subdimension") or "")
        weights[cell] = {a["p_code"]: a["weight"] for a in row["abilities"]}
        meta[cell] = {
            "benchmark_name": row.get("benchmark_name"),
            "evidence_tier": row.get("evidence_tier"),
        }
    return weights, meta


def load_measurement_model(path):
    with open(path, encoding="utf-8") as f:
        doc = json.load(f)
    model_type = {}
    p_name = {}
    facet_of = {}
    single_source = set()
    for p in doc["abilities"]:
        code = p["p_code"]
        model_type[code] = p["model_type"]
        p_name[code] = p["p_name"]
        if p.get("single_source"):
            single_source.add(code)
        for facet in p["facets"]:
            for cell in facet["cells"]:
                key = (code, cell["benchmark_id"], cell["subdimension"])
                facet_of[key] = facet["facet_id"]
    return {
        "doc": doc,
        "model_type": model_type,
        "p_name": p_name,
        "facet_of": facet_of,
        "single_source": single_source,
    }


# ---------------------------------------------------------------------------
# Phase 0: cell audit
# ---------------------------------------------------------------------------


def audit_cells(matrix, mapping_weights, mapping_meta, args):
    cells = []
    for cell in sorted(set(mapping_weights) | set(matrix)):
        scores = list(matrix.get(cell, {}).values())
        n = len(scores)
        mean = sum(scores) / n if n else None
        sd = statistics.stdev(scores) if n >= 2 else None
        flags = []
        if cell not in mapping_weights:
            flags.append("not_in_mapping")
        if n and mean is not None:
            if mean >= args.ceiling_mean:
                flags.append("ceiling")
            if mean <= args.floor_mean:
                flags.append("floor")
            if n >= 4 and sd is not None and sd < args.min_sd:
                flags.append("low_variance")
        variance_restricted = any(f in flags for f in ("ceiling", "floor", "low_variance"))
        cells.append({
            "benchmark_id": cell[0],
            "subdimension": cell[1],
            "family": family_of(cell[0]),
            "evidence_tier": (mapping_meta.get(cell) or {}).get("evidence_tier"),
            "n_models": n,
            "mean_score_10": round(mean, 3) if mean is not None else None,
            "sd_score_10": round(sd, 3) if sd is not None else None,
            "min_score_10": round(min(scores), 3) if n else None,
            "max_score_10": round(max(scores), 3) if n else None,
            "flags": flags,
            "variance_restricted": variance_restricted,
            "p_weights": mapping_weights.get(cell, {}),
        })
    return cells


# ---------------------------------------------------------------------------
# Pair analysis
# ---------------------------------------------------------------------------


def classify_pair(cell_a, cell_b, mapping_weights, mm):
    """Shared-P structure and expected pattern for one unordered cell pair."""
    wa = mapping_weights.get(cell_a, {})
    wb = mapping_weights.get(cell_b, {})
    shared = []
    for p_code in sorted(set(wa) & set(wb)):
        if wa[p_code] < WEIGHT_MIN or wb[p_code] < WEIGHT_MIN:
            continue
        fa = mm["facet_of"].get((p_code, cell_a[0], cell_a[1]))
        fb = mm["facet_of"].get((p_code, cell_b[0], cell_b[1]))
        if mm["model_type"].get(p_code) == "reflective" or (fa and fa == fb):
            pattern = "expect_convergent"
        else:
            pattern = "facet_distinct_expected"
        shared.append({
            "p_code": p_code,
            "p_name": mm["p_name"].get(p_code),
            "weight_a": wa[p_code],
            "weight_b": wb[p_code],
            "facet_a": fa,
            "facet_b": fb,
            "pattern": pattern,
        })
    any_shared_at_all = bool(set(wa) & set(wb))
    same_family = family_of(cell_a[0]) == family_of(cell_b[0])
    if same_family:
        pair_class = "same_family"
    elif any(s["pattern"] == "expect_convergent" for s in shared):
        pair_class = "convergent"
    elif shared:
        pair_class = "facet_distinct"
    elif not any_shared_at_all:
        pair_class = "baseline_no_shared_p"
    else:
        pair_class = "weak_shared"
    return shared, pair_class


def rate_pair(pair, args):
    """Plan section 2.6 rating; only convergent cross-family pairs are rated."""
    if pair["pair_class"] != "convergent":
        return None
    if pair["n_common_models"] < args.min_n:
        return "insufficient_evidence"
    if pair["variance_restricted_a"] or pair["variance_restricted_b"]:
        return "variance_restricted"
    rho = pair["spearman_rho"]
    if rho is None:
        return "insufficient_evidence"
    if rho >= 0.5 and pair["ci_low"] is not None and pair["ci_low"] > 0:
        return "validated"
    if rho < 0 and pair["n_common_models"] >= args.flag_min_n:
        return "flagged"
    if 0 <= rho < 0.2 and pair["n_common_models"] >= args.watch_min_n:
        return "watch"
    return "provisional"


def analyze_pairs(matrix, mapping_weights, cell_audit, mm, args):
    rng = random.Random(args.seed)
    restricted = {
        (c["benchmark_id"], c["subdimension"]): c["variance_restricted"]
        for c in cell_audit
    }
    composite = defaultdict(list)
    for cell, per_model in matrix.items():
        for model, score in per_model.items():
            composite[model].append(score)
    composite = {m: sum(v) / len(v) for m, v in composite.items()}

    evidence_cells = sorted(c for c in matrix if c in mapping_weights)
    pairs = []
    for cell_a, cell_b in itertools.combinations(evidence_cells, 2):
        common = sorted(set(matrix[cell_a]) & set(matrix[cell_b]))
        if len(common) < args.appendix_min_n:
            continue
        shared, pair_class = classify_pair(cell_a, cell_b, mapping_weights, mm)
        x = [matrix[cell_a][m] for m in common]
        y = [matrix[cell_b][m] for m in common]
        z = [composite[m] for m in common]
        rho = spearman(x, y)
        p_value = p_method = ci_low = ci_high = boot_na = prho = None
        if rho is not None:
            p_value, p_method = permutation_pvalue(x, y, rng, n_mc=args.n_perm)
            ci_low, ci_high, boot_na = bootstrap_ci(x, y, rng, n_boot=args.n_boot)
            prho = partial_spearman(x, y, z)
        pair = {
            "benchmark_a": cell_a[0],
            "subdimension_a": cell_a[1],
            "benchmark_b": cell_b[0],
            "subdimension_b": cell_b[1],
            "family_a": family_of(cell_a[0]),
            "family_b": family_of(cell_b[0]),
            "pair_class": pair_class,
            "shared_ps": shared,
            "n_common_models": len(common),
            "common_models": common,
            "spearman_rho": round(rho, 3) if rho is not None else None,
            "partial_rho_vs_composite": round(prho, 3) if prho is not None else None,
            "permutation_p": round(p_value, 4) if p_value is not None else None,
            "permutation_method": p_method,
            "ci90_low": round(ci_low, 3) if ci_low is not None else None,
            "ci90_high": round(ci_high, 3) if ci_high is not None else None,
            "bootstrap_na_rate": round(boot_na, 3) if boot_na is not None else None,
            "variance_restricted_a": restricted.get(cell_a, False),
            "variance_restricted_b": restricted.get(cell_b, False),
        }
        pair["ci_low"] = ci_low
        pair["rating"] = rate_pair(pair, args)
        pair["low_confidence_appendix"] = pair["n_common_models"] < args.min_n
        del pair["ci_low"]
        pairs.append(pair)
    return pairs


# ---------------------------------------------------------------------------
# Roll-ups
# ---------------------------------------------------------------------------


def family_halo(pairs, args):
    within = defaultdict(list)
    across = defaultdict(list)
    for p in pairs:
        if p["spearman_rho"] is None or p["n_common_models"] < args.min_n:
            continue
        if p["family_a"] == p["family_b"]:
            within[p["family_a"]].append(p["spearman_rho"])
        else:
            across[p["family_a"]].append(p["spearman_rho"])
            across[p["family_b"]].append(p["spearman_rho"])
    rows = []
    for family in sorted(set(within) | set(across)):
        w = within.get(family, [])
        a = across.get(family, [])
        if not w:
            continue
        mean_w = sum(w) / len(w)
        mean_a = sum(a) / len(a) if a else None
        halo = mean_w - mean_a if mean_a is not None else None
        rows.append({
            "family": family,
            "n_within_pairs": len(w),
            "mean_within_rho": round(mean_w, 3),
            "n_cross_pairs": len(a),
            "mean_cross_rho": round(mean_a, 3) if mean_a is not None else None,
            "halo_score": round(halo, 3) if halo is not None else None,
            "aggregate_family_first": bool(halo is not None and halo > 0.5),
        })
    return rows


def discriminant_summary(pairs, args, rng):
    def eligible(p, klass):
        return (
            p["pair_class"] == klass
            and p["spearman_rho"] is not None
            and p["n_common_models"] >= args.min_n
            and not p["variance_restricted_a"]
            and not p["variance_restricted_b"]
        )

    conv = [p["spearman_rho"] for p in pairs if eligible(p, "convergent")]
    base = [p["spearman_rho"] for p in pairs if eligible(p, "baseline_no_shared_p")]
    result = {
        "n_convergent_pairs": len(conv),
        "n_baseline_pairs": len(base),
        "convergent_mean_rho": round(sum(conv) / len(conv), 3) if conv else None,
        "convergent_median_rho": round(statistics.median(conv), 3) if conv else None,
        "baseline_mean_rho": round(sum(base) / len(base), 3) if base else None,
        "baseline_median_rho": round(statistics.median(base), 3) if base else None,
        "mean_diff": None,
        "permutation_p_one_sided": None,
        "caveat": "配对之间共享格子、非独立；p 值仅供参考，结论以红旗/非红旗为主。",
    }
    if conv and base:
        diff = sum(conv) / len(conv) - sum(base) / len(base)
        result["mean_diff"] = round(diff, 3)
        pool = conv + base
        n_conv = len(conv)
        count = 0
        n_iter = 10000
        for _ in range(n_iter):
            rng.shuffle(pool)
            d = sum(pool[:n_conv]) / n_conv - sum(pool[n_conv:]) / (len(pool) - n_conv)
            if d >= diff - 1e-12:
                count += 1
        result["permutation_p_one_sided"] = round((count + 1) / (n_iter + 1), 4)
    return result


def grid_ratings(pairs, cell_audit, mapping_weights, mm, args):
    """Rating per (P, cell) grid cell for cells mapped at weight >= 0.2."""
    restricted = {
        (c["benchmark_id"], c["subdimension"]): c["variance_restricted"]
        for c in cell_audit
    }
    has_evidence = {
        (c["benchmark_id"], c["subdimension"]): c["n_models"] > 0
        for c in cell_audit
    }
    by_p_cell = defaultdict(list)
    for pair in pairs:
        if pair["pair_class"] != "convergent" or pair["rating"] is None:
            continue
        for s in pair["shared_ps"]:
            if s["pattern"] != "expect_convergent":
                continue
            for bench, subdim in (
                (pair["benchmark_a"], pair["subdimension_a"]),
                (pair["benchmark_b"], pair["subdimension_b"]),
            ):
                by_p_cell[(s["p_code"], bench, subdim)].append(pair["rating"])
    grid = []
    for cell, weights in sorted(mapping_weights.items()):
        for p_code, weight in sorted(weights.items()):
            if weight < WEIGHT_MIN:
                continue
            key = (p_code, cell[0], cell[1])
            ratings = by_p_cell.get(key, [])
            if p_code in mm["single_source"]:
                rating = "single_source"
            elif restricted.get(cell):
                rating = "variance_restricted"
            elif "validated" in ratings:
                rating = "validated"
            elif "flagged" in ratings:
                rating = "flagged"
            elif "watch" in ratings:
                rating = "watch"
            elif "provisional" in ratings:
                rating = "provisional"
            elif not has_evidence.get(cell):
                rating = "insufficient_evidence"
            else:
                rating = "insufficient_evidence"
            grid.append({
                "p_code": p_code,
                "p_name": mm["p_name"].get(p_code),
                "model_type": mm["model_type"].get(p_code),
                "facet": mm["facet_of"].get(key),
                "benchmark_id": cell[0],
                "subdimension": cell[1],
                "weight": weight,
                "rating": rating,
                "n_rated_pairs": len(ratings),
            })
    return grid


# ---------------------------------------------------------------------------
# Reports
# ---------------------------------------------------------------------------


def fmt(v):
    return "—" if v is None else v


def pair_label(p, side):
    return f"`{p['benchmark_' + side]}` {p['subdimension_' + side]}"


def pair_shared_str(p):
    return ", ".join(
        f"{s['p_code']}({s['weight_a']}/{s['weight_b']}{'' if s['pattern'] == 'expect_convergent' else ' 异facet'})"
        for s in p["shared_ps"]
    )


def write_md(path, cells, pairs, grid, halo, disc, mm, args):
    lines = []
    add = lines.append
    add("# 映射效度体检报告（13 号）")
    add("")
    add(f"生成脚本：`scripts/build_mapping_validation.py`（幂等）；测量模型：`{args.measurement_model}`（{mm['doc'].get('status')}）。")
    add("规则见 `doc/mapping_validation_plan_2026-07-11.md` §2；ρ 一律与 n、90% CI 同格呈现，n<5 的配对只进低置信附录。")
    add("")

    restricted = [c for c in cells if c["variance_restricted"]]
    add("## Phase 0：天花板/方差受限名单")
    add("")
    add(f"共 {len(restricted)} / {len([c for c in cells if c['n_models']])} 个有证据格子被标记 `variance_restricted`（mean≥{args.ceiling_mean} 或 n≥4 且 SD<{args.min_sd}）。这些格子参与的配对**不进入裁决**；优先动作是上难度/换切分，不是改映射。")
    add("")
    add("| Benchmark | Subdimension | n | mean | SD | 标记 |")
    add("|---|---|---:|---:|---:|---|")
    for c in sorted(restricted, key=lambda c: -(c["mean_score_10"] or 0)):
        add(f"| `{c['benchmark_id']}` | {c['subdimension']} | {c['n_models']} | {fmt(c['mean_score_10'])} | {fmt(c['sd_score_10'])} | {', '.join(c['flags'])} |")
    add("")

    def pair_table(title, rows, note=""):
        add(f"## {title}")
        add("")
        if note:
            add(note)
            add("")
        if not rows:
            add("（无）")
            add("")
            return
        add("| A | B | 共享 P（权重A/B） | n | ρ | 偏ρ(控综合分) | perm p | 90% CI | 评级 |")
        add("|---|---|---|---:|---:|---:|---:|---|---|")
        for p in rows:
            ci = f"[{fmt(p['ci90_low'])}, {fmt(p['ci90_high'])}]"
            add(
                f"| {pair_label(p, 'a')} | {pair_label(p, 'b')} | {pair_shared_str(p)} | "
                f"{p['n_common_models']} | {fmt(p['spearman_rho'])} | {fmt(p['partial_rho_vs_composite'])} | "
                f"{fmt(p['permutation_p'])} | {ci} | {p['rating'] or '—'} |"
            )
        add("")

    rated = [p for p in pairs if p["pair_class"] == "convergent" and not p["low_confidence_appendix"]]
    flagged = [p for p in rated if p["rating"] == "flagged"]
    watch = [p for p in rated if p["rating"] == "watch"]
    validated = [p for p in rated if p["rating"] == "validated"]
    provisional = [p for p in rated if p["rating"] == "provisional"]
    var_pairs = [p for p in rated if p["rating"] == "variance_restricted"]

    pair_table("红旗配对（flagged：同 P 预期收敛却 ρ<0，n≥6）", sorted(flagged, key=lambda p: p["spearman_rho"] or 0),
               "每条 flagged 需人工裁决：改权重 / 拆 facet / 降 tier / 转裁判治理（计划 §2.6）。")
    pair_table("观察带（watch：0≤ρ<0.2 且 n≥8）", watch)
    pair_table("已验证配对（validated：ρ≥0.5 且 CI 下界>0）", sorted(validated, key=lambda p: -(p["spearman_rho"] or 0)))
    pair_table("待定配对（provisional）", sorted(provisional, key=lambda p: p["spearman_rho"] or 0))
    pair_table("因方差受限不裁决的配对", sorted(var_pairs, key=lambda p: p["spearman_rho"] or 0),
               "任一侧格子 variance_restricted；其 ρ 不作为构念证据。")

    add("## 区分效度（同 P 收敛配对 vs 不共享 P 的 baseline）")
    add("")
    add(f"- 收敛配对（跨家族、非受限、n≥{args.min_n}）：{disc['n_convergent_pairs']} 对，mean ρ = {fmt(disc['convergent_mean_rho'])}，median = {fmt(disc['convergent_median_rho'])}")
    add(f"- baseline（不共享任何 P）：{disc['n_baseline_pairs']} 对，mean ρ = {fmt(disc['baseline_mean_rho'])}，median = {fmt(disc['baseline_median_rho'])}")
    add(f"- 差值 = {fmt(disc['mean_diff'])}，单侧 permutation p = {fmt(disc['permutation_p_one_sided'])}（{disc['caveat']}）")
    add("")
    add("若差值不显著为正，说明 P 划分对'哪些 benchmark 相关'没有预测力，映射层需整体重审。")
    add("")

    add("## 家族方法方差（halo）")
    add("")
    add("| 家族 | 家族内配对数 | 家族内 mean ρ | 跨家族配对数 | 跨家族 mean ρ | halo 分 | 家族内先聚合? |")
    add("|---|---:|---:|---:|---:|---:|---|")
    for h in sorted(halo, key=lambda h: -(h["halo_score"] if h["halo_score"] is not None else -9)):
        add(f"| `{h['family']}` | {h['n_within_pairs']} | {h['mean_within_rho']} | {h['n_cross_pairs']} | {fmt(h['mean_cross_rho'])} | {fmt(h['halo_score'])} | {'是' if h['aggregate_family_first'] else '否'} |")
    add("")
    add("halo 分 > 0.5 的家族：多子维度在 P 聚合前先合成一票（计划 §2.6）。")
    add("")

    add("## P × 格子评级汇总")
    add("")
    counts = defaultdict(int)
    for g in grid:
        counts[g["rating"]] += 1
    add("评级分布：" + "、".join(f"{r}={counts[r]}" for r in RATING_ORDER if counts[r]))
    add("")
    add("| P | 类型 | facet | Benchmark | Subdimension | 权重 | 评级 |")
    add("|---|---|---|---|---|---:|---|")
    for g in sorted(grid, key=lambda g: (g["p_code"], g["rating"], g["benchmark_id"])):
        add(f"| {g['p_code']} {g['p_name']} | {g['model_type']} | {fmt(g['facet'])} | `{g['benchmark_id']}` | {g['subdimension']} | {g['weight']} | **{g['rating']}** |")
    add("")

    appendix = [p for p in pairs if p["pair_class"] == "convergent" and p["low_confidence_appendix"]]
    add("## 低置信附录（3 ≤ n < 5，仅呈现不评级）")
    add("")
    if appendix:
        add("| A | B | 共享 P | n | ρ |")
        add("|---|---|---|---:|---:|")
        for p in sorted(appendix, key=lambda p: p["spearman_rho"] or 0):
            add(f"| {pair_label(p, 'a')} | {pair_label(p, 'b')} | {pair_shared_str(p)} | {p['n_common_models']} | {fmt(p['spearman_rho'])} |")
    else:
        add("（无）")
    add("")

    distinct = [p for p in pairs if p["pair_class"] == "facet_distinct" and p["spearman_rho"] is not None and not p["low_confidence_appendix"]]
    add("## 形成型跨 facet 配对（facet_distinct_expected，信息呈现，不触发红旗）")
    add("")
    if distinct:
        add("| A | B | 共享 P | n | ρ |")
        add("|---|---|---|---:|---:|")
        for p in sorted(distinct, key=lambda p: p["spearman_rho"] or 0):
            add(f"| {pair_label(p, 'a')} | {pair_label(p, 'b')} | {pair_shared_str(p)} | {p['n_common_models']} | {fmt(p['spearman_rho'])} |")
    else:
        add("（无）")
    add("")
    add("## 局限")
    add("")
    add("- n=5-8 的置信区间很宽，评级以红旗探测为目的，不是效应量精确估计；补模型数（M2.5）是第一优先级。")
    add("- 偏相关控制的'综合分'由同一批证据构造，存在轻度内生性；仅作敏感性检查。")
    add("- 配对之间共享格子、非独立，区分效度的 permutation p 只作参考。")
    path.write_text("\n".join(lines), encoding="utf-8")


RATING_COLORS = {
    "validated": "#1a7f37",
    "flagged": "#c1121f",
    "watch": "#e6a700",
    "provisional": "#7a7a7a",
    "variance_restricted": "#9457c9",
    "insufficient_evidence": "#c4c4c4",
    "single_source": "#4a76c9",
}


def scatter_svg(pair, matrix):
    cell_a = (pair["benchmark_a"], pair["subdimension_a"])
    cell_b = (pair["benchmark_b"], pair["subdimension_b"])
    pts = [(matrix[cell_a][m], matrix[cell_b][m], m) for m in pair["common_models"]]
    w, h, pad = 260, 220, 34
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    x0, x1 = min(xs), max(xs)
    y0, y1 = min(ys), max(ys)
    xr = (x1 - x0) or 1.0
    yr = (y1 - y0) or 1.0
    sx = lambda v: pad + (v - x0) / xr * (w - 2 * pad)
    sy = lambda v: h - pad - (v - y0) / yr * (h - 2 * pad)
    dots = "".join(
        f'<circle cx="{sx(x):.1f}" cy="{sy(y):.1f}" r="4" fill="#2563eb" opacity="0.8"><title>{html.escape(m)}: ({x:.2f}, {y:.2f})</title></circle>'
        for x, y, m in pts
    )
    color = RATING_COLORS.get(pair["rating"] or "provisional", "#7a7a7a")
    title = f"{pair['benchmark_a']} × {pair['benchmark_b']}  ρ={pair['spearman_rho']} n={pair['n_common_models']}"
    return (
        f'<div class="scatter"><div class="scatter-title" style="border-left:4px solid {color}">{html.escape(title)}</div>'
        f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
        f'<rect x="{pad}" y="{pad}" width="{w - 2 * pad}" height="{h - 2 * pad}" fill="none" stroke="#ccc"/>'
        f'{dots}'
        f'<text x="{w / 2}" y="{h - 6}" font-size="10" text-anchor="middle" fill="#555">{html.escape(pair["benchmark_a"])}</text>'
        f'<text x="10" y="{h / 2}" font-size="10" text-anchor="middle" fill="#555" transform="rotate(-90 10 {h / 2})">{html.escape(pair["benchmark_b"])}</text>'
        f"</svg></div>"
    )


def write_html(path, cells, pairs, grid, halo, disc, matrix, mm, args):
    p_codes = sorted({g["p_code"] for g in grid})
    grid_lookup = {}
    for g in grid:
        grid_lookup[(g["p_code"], g["benchmark_id"], g["subdimension"])] = g
    cell_rows = sorted(
        {(g["benchmark_id"], g["subdimension"]) for g in grid},
        key=lambda c: (family_of(c[0]), c[0], c[1]),
    )
    heat = ['<table class="heat"><thead><tr><th>Benchmark / Subdimension</th>']
    heat += [f"<th>{p}</th>" for p in p_codes]
    heat.append("</tr></thead><tbody>")
    for bench, subdim in cell_rows:
        heat.append(f'<tr><td class="rowhead">{html.escape(bench)}<br><span class="sub">{html.escape(subdim)}</span></td>')
        for p in p_codes:
            g = grid_lookup.get((p, bench, subdim))
            if g is None:
                heat.append("<td></td>")
            else:
                color = RATING_COLORS[g["rating"]]
                facet = f" · {g['facet']}" if g["facet"] and g["facet"] != "core" else ""
                heat.append(
                    f'<td class="cell" style="background:{color}" title="{p} w={g["weight"]}{html.escape(facet)} — {g["rating"]}"></td>'
                )
        heat.append("</tr>")
    heat.append("</tbody></table>")

    legend = "".join(
        f'<span class="lg"><span class="sw" style="background:{c}"></span>{r}</span>'
        for r, c in RATING_COLORS.items()
    )

    rated = [p for p in pairs if p["pair_class"] == "convergent" and not p["low_confidence_appendix"]]
    show = [p for p in rated if p["rating"] in ("flagged", "validated", "watch")]
    scatters = "".join(scatter_svg(p, matrix) for p in sorted(show, key=lambda p: p["spearman_rho"] or 0))

    pair_rows = []
    for p in sorted(rated, key=lambda p: (p["rating"] or "", p["spearman_rho"] or 0)):
        ci = f"[{fmt(p['ci90_low'])}, {fmt(p['ci90_high'])}]"
        pair_rows.append(
            f"<tr><td>{html.escape(p['benchmark_a'])}<br><span class='sub'>{html.escape(p['subdimension_a'])}</span></td>"
            f"<td>{html.escape(p['benchmark_b'])}<br><span class='sub'>{html.escape(p['subdimension_b'])}</span></td>"
            f"<td>{html.escape(pair_shared_str(p))}</td><td>{p['n_common_models']}</td>"
            f"<td>{fmt(p['spearman_rho'])}</td><td>{fmt(p['partial_rho_vs_composite'])}</td>"
            f"<td>{fmt(p['permutation_p'])}</td><td>{ci}</td>"
            f"<td><span class='badge' style='background:{RATING_COLORS.get(p['rating'], '#999')}'>{p['rating']}</span></td></tr>"
        )

    halo_rows = "".join(
        f"<tr><td>{h['family']}</td><td>{h['n_within_pairs']}</td><td>{h['mean_within_rho']}</td>"
        f"<td>{h['n_cross_pairs']}</td><td>{fmt(h['mean_cross_rho'])}</td><td>{fmt(h['halo_score'])}</td>"
        f"<td>{'是' if h['aggregate_family_first'] else '否'}</td></tr>"
        for h in sorted(halo, key=lambda h: -(h["halo_score"] if h["halo_score"] is not None else -9))
    )

    restricted = [c for c in cells if c["variance_restricted"]]
    restricted_rows = "".join(
        f"<tr><td>{html.escape(c['benchmark_id'])}</td><td>{html.escape(c['subdimension'])}</td>"
        f"<td>{c['n_models']}</td><td>{fmt(c['mean_score_10'])}</td><td>{fmt(c['sd_score_10'])}</td>"
        f"<td>{', '.join(c['flags'])}</td></tr>"
        for c in sorted(restricted, key=lambda c: -(c["mean_score_10"] or 0))
    )

    doc = f"""<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="utf-8">
<title>映射效度体检报告（13 号）</title>
<style>
body {{ font-family: -apple-system, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif; margin: 24px auto; max-width: 1200px; color: #222; line-height: 1.5; }}
h1 {{ font-size: 22px; }} h2 {{ font-size: 17px; margin-top: 28px; border-bottom: 1px solid #ddd; padding-bottom: 4px; }}
table {{ border-collapse: collapse; font-size: 12.5px; margin: 10px 0; }}
th, td {{ border: 1px solid #ddd; padding: 4px 8px; text-align: left; vertical-align: top; }}
th {{ background: #f5f5f5; }}
.sub {{ color: #777; font-size: 11px; }}
.heat td.cell {{ width: 26px; height: 22px; padding: 0; }}
.heat td.rowhead {{ font-size: 11.5px; }}
.lg {{ margin-right: 14px; font-size: 12px; }}
.sw {{ display: inline-block; width: 12px; height: 12px; margin-right: 4px; vertical-align: -1px; }}
.badge {{ color: #fff; padding: 1px 6px; border-radius: 3px; font-size: 11px; }}
.scatters {{ display: flex; flex-wrap: wrap; gap: 12px; }}
.scatter {{ border: 1px solid #e3e3e3; padding: 6px; }}
.scatter-title {{ font-size: 11px; padding-left: 6px; margin-bottom: 4px; max-width: 250px; }}
.note {{ background: #f8f6ee; border-left: 4px solid #e6a700; padding: 8px 12px; font-size: 13px; }}
</style>
</head>
<body>
<h1>映射效度体检报告（13 号）</h1>
<p>输入：<code>{EVIDENCE_NAME}</code> + <code>{MAPPING_NAME}</code> + <code>{html.escape(str(args.measurement_model))}</code>（预注册测量模型，status={html.escape(str(mm['doc'].get('status')))}）。
规则见 <code>doc/mapping_validation_plan_2026-07-11.md</code> §2.6。明细数据：<code>{OUT_PAIRS}</code> / <code>{OUT_CELLS}</code>；文字版：<code>{OUT_MD}</code>。</p>
<div class="note">评级只针对「跨家族 + 预期收敛 + 双方非方差受限 + n≥{args.min_n}」的配对；形成型 P 的跨 facet 配对按声明预期不收敛，不触发红旗。n=5-8 时 CI 很宽，本报告是红旗探测器，不是效应量估计。</div>

<h2>P × 格子评级热图（格子颜色 = 评级；悬停看权重/facet）</h2>
<p>{legend}</p>
{"".join(heat)}

<h2>关键配对散点（flagged / watch / validated；点 = 模型，悬停看模型名）</h2>
<div class="scatters">{scatters}</div>

<h2>全部被评级配对</h2>
<table><thead><tr><th>A</th><th>B</th><th>共享 P（权重A/B）</th><th>n</th><th>ρ</th><th>偏ρ</th><th>perm p</th><th>90% CI</th><th>评级</th></tr></thead>
<tbody>{"".join(pair_rows)}</tbody></table>

<h2>区分效度</h2>
<p>同 P 收敛配对 mean ρ = <b>{fmt(disc['convergent_mean_rho'])}</b>（{disc['n_convergent_pairs']} 对） vs 不共享 P 的 baseline mean ρ = <b>{fmt(disc['baseline_mean_rho'])}</b>（{disc['n_baseline_pairs']} 对），差值 {fmt(disc['mean_diff'])}，单侧 permutation p = {fmt(disc['permutation_p_one_sided'])}。<span class="sub">{html.escape(disc['caveat'])}</span></p>

<h2>家族方法方差（halo）</h2>
<table><thead><tr><th>家族</th><th>家族内对数</th><th>家族内 mean ρ</th><th>跨家族对数</th><th>跨家族 mean ρ</th><th>halo 分</th><th>家族内先聚合?</th></tr></thead>
<tbody>{halo_rows}</tbody></table>

<h2>Phase 0：方差受限格子（不进入裁决）</h2>
<table><thead><tr><th>Benchmark</th><th>Subdimension</th><th>n</th><th>mean</th><th>SD</th><th>标记</th></tr></thead>
<tbody>{restricted_rows}</tbody></table>
</body>
</html>
"""
    path.write_text(doc, encoding="utf-8")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def build_parser():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--rebenchmark-dir", type=Path, default=DEFAULT_REBENCH_DIR)
    ap.add_argument("--measurement-model", type=Path, default=DEFAULT_MEASUREMENT_MODEL)
    ap.add_argument("--min-n", type=int, default=5, help="最小共同模型数（评级门槛）")
    ap.add_argument("--appendix-min-n", type=int, default=3, help="低置信附录门槛")
    ap.add_argument("--flag-min-n", type=int, default=6)
    ap.add_argument("--watch-min-n", type=int, default=8)
    ap.add_argument("--ceiling-mean", type=float, default=8.5)
    ap.add_argument("--floor-mean", type=float, default=1.5)
    ap.add_argument("--min-sd", type=float, default=0.5)
    ap.add_argument("--n-boot", type=int, default=2000)
    ap.add_argument("--n-perm", type=int, default=10000)
    ap.add_argument("--seed", type=int, default=20260711)
    ap.add_argument("--validate-only", action="store_true")
    return ap


def main():
    args = build_parser().parse_args()
    rdir = args.rebenchmark_dir
    matrix, multi_run = load_evidence_matrix(rdir / EVIDENCE_NAME)
    mapping_weights, mapping_meta = load_mapping(rdir / MAPPING_NAME)
    mm = load_measurement_model(args.measurement_model)

    evidence_only = sorted(set(matrix) - set(mapping_weights))
    mapping_only = sorted(set(mapping_weights) - set(matrix))
    uncovered = [
        (p_code, cell)
        for cell, weights in mapping_weights.items()
        for p_code in weights
        if (p_code, cell[0], cell[1]) not in mm["facet_of"]
    ]

    n_models = len({m for per in matrix.values() for m in per})
    pilot_style_pairs = 0
    for a, b in itertools.combinations(sorted(c for c in matrix if c in mapping_weights), 2):
        common = set(matrix[a]) & set(matrix[b])
        if len(common) < args.min_n:
            continue
        wa, wb = mapping_weights[a], mapping_weights[b]
        if any(wa.get(p, 0) >= WEIGHT_MIN and wb.get(p, 0) >= WEIGHT_MIN for p in wa):
            pilot_style_pairs += 1

    print(f"evidence cells={len(matrix)} models={n_models} mapping rows={len(mapping_weights)}")
    print(f"measurement model: abilities={len(mm['model_type'])} facet assignments={len(mm['facet_of'])}")
    print(f"shared-P(>= {WEIGHT_MIN}) pairs with n>={args.min_n} (pilot definition): {pilot_style_pairs}")
    if multi_run:
        print(f"multi-run cells averaged: {len(multi_run)}")
    if evidence_only:
        print(f"WARN evidence cells not in mapping: {evidence_only}")
    if mapping_only:
        print(f"NOTE mapping cells without evidence: {[c[0] for c in mapping_only]}")
    if uncovered:
        raise SystemExit(f"measurement model missing facet assignment for: {uncovered[:5]} ...")
    if args.validate_only:
        print("validate-only OK")
        return

    cell_audit = audit_cells(matrix, mapping_weights, mapping_meta, args)
    pairs = analyze_pairs(matrix, mapping_weights, cell_audit, mm, args)
    halo = family_halo(pairs, args)
    disc = discriminant_summary(pairs, args, random.Random(args.seed + 1))
    grid = grid_ratings(pairs, cell_audit, mapping_weights, mm, args)

    with open(rdir / OUT_CELLS, "w", encoding="utf-8") as f:
        for c in cell_audit:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    with open(rdir / OUT_PAIRS, "w", encoding="utf-8") as f:
        for p in pairs:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")
    write_md(rdir / OUT_MD, cell_audit, pairs, grid, halo, disc, mm, args)
    write_html(rdir / OUT_HTML, cell_audit, pairs, grid, halo, disc, matrix, mm, args)

    rated = [p for p in pairs if p["pair_class"] == "convergent" and not p["low_confidence_appendix"]]
    summary = defaultdict(int)
    for p in rated:
        summary[p["rating"]] += 1
    print(f"pairs computed={len(pairs)} convergent rated={len(rated)} -> " + ", ".join(f"{k}={v}" for k, v in sorted(summary.items())))
    print(f"variance_restricted cells={sum(1 for c in cell_audit if c['variance_restricted'])}")
    print(f"wrote {rdir / OUT_CELLS}, {rdir / OUT_PAIRS}, {rdir / OUT_MD}, {rdir / OUT_HTML}")


if __name__ == "__main__":
    main()
