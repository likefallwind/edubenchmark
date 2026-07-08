#!/usr/bin/env python3
"""Jury vs single-judge comparison on the judge meta-eval test split (WP4/WP5).

Offline only — reads existing per-item judge outputs plus the frozen split in
``data/judge_meta_eval_v1/`` and writes ``reports/eval/_judge_jury/``. No API
calls. Plan: doc/judge_research_plan_2026-07-06.md sections 6-7.

Jury = {deepseek-v4-pro, glm-5.2, MiniMax-M3} (three model families). Voting
rules (fixed for reproducibility):

- majority vote: most common valid label; ``unparsed``/``no_choice`` counts as
  abstention; full abstention -> unparsed; ties broken by the judge with the
  highest mean dev-split kappa (tie-break rate reported).
- weighted vote: per-judge weight = its per-dimension **dev-split** kappa
  (glm-5.2 estimated on the stratified dev subsample; negatives clipped to 0);
  test-split weights would leak the evaluation set.

All headline numbers are computed on the **test split only**, with cluster
bootstrap 95% CIs (cluster = dialogue / preference pair; scripts/eval/stats.py).
The primary verdict is the paired difference in macro Cohen's kappa between
each jury variant and the best single judge (best = highest mean dev kappa).

Also emitted:

- disagreements.jsonl — items where the three judges' valid labels differ
  (with raw judge responses + reasoning): the human-review queue seed (J6) and
  the highest-information future training data (J5).
- length-bias section (WP5): agreement and leniency gap
  P(judge says Yes) - P(human says Yes) by response-length quintile, plus the
  pairwise P(chooses the longer response) gap vs expert humans.

Usage:
    python scripts/build_judge_jury_report.py            # full report
    python scripts/build_judge_jury_report.py --n-boot 200   # quicker CIs
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Callable

from eval.stats import (
    DEFAULT_SEED,
    agreement_stat,
    cluster_bootstrap_ci,
    cluster_bootstrap_diff_ci,
    kappa_stat,
    macro_f1_stat,
)

ROOT = Path(__file__).resolve().parents[1]
META_DIR = ROOT / "data" / "judge_meta_eval_v1"
OUT_DIR = ROOT / "reports" / "eval" / "_judge_jury"

# judge display name -> reports/eval/<benchmark>/<dir> slug
JUDGES: dict[str, str] = {
    "deepseek-v4-pro": "deepseek-v4-pro",
    "glm-5.2": "glm-5.2",
    "MiniMax-M3": "minimax3",
}

# meta-eval source -> eval-harness benchmark directory
SOURCES: dict[str, str] = {
    "mrbench": "mrbench_judge",
    "bea2025": "bea2025_judge",
    "mathtutorbench": "mathtutorbench_judge_calibration",
}

ABSTAIN_LABELS = {"unparsed", "no_choice", ""}
# Dimensions using the Yes / To some extent / No scale (leniency analysis).
YES_SCALE_EXCLUDED = {"Revealing_of_the_Answer", "Tutor_Tone"}


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _round(x: float | None) -> float | None:
    return None if x is None else round(x, 4)


# ---------------------------------------------------------------------------
# Load inputs
# ---------------------------------------------------------------------------


def load_meta_items() -> dict[str, list[dict[str, Any]]]:
    by_source: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in _read_jsonl(META_DIR / "items.jsonl"):
        by_source[row["source_benchmark"]].append(row)
    return by_source


def load_judge_outputs(source: str) -> tuple[dict[str, dict[str, str]], dict[str, dict[str, dict[str, Any]]], dict[str, str]]:
    """Return (labels, raw, input_hashes).

    labels[judge][native_item_id] = predicted label (or A/B letter)
    raw[judge][native_item_id]    = {"response": ..., "reasoning": ...}
    """
    bench_dir = ROOT / "reports" / "eval" / SOURCES[source]
    labels: dict[str, dict[str, str]] = {}
    raw: dict[str, dict[str, dict[str, Any]]] = {}
    hashes: dict[str, str] = {}
    for judge, slug in JUDGES.items():
        scored_path = bench_dir / slug / "scored.jsonl"
        if not scored_path.exists():
            print(f"  !! missing {scored_path} — {judge} excluded for {source}")
            continue
        per_item: dict[str, str] = {}
        for row in _read_jsonl(scored_path):
            if row.get("score_status") != "scored":
                continue
            if "pred_label" in row:
                per_item[str(row["item_id"])] = str(row["pred_label"])
            else:  # pairwise: normalized is the chosen letter or no_choice
                per_item[str(row["item_id"])] = str(row.get("normalized") or "no_choice")
        labels[judge] = per_item
        hashes[f"{SOURCES[source]}/{slug}/scored.jsonl"] = _sha256_file(scored_path)
        raw_map: dict[str, dict[str, Any]] = {}
        pred_path = bench_dir / slug / "predictions.jsonl"
        if pred_path.exists():
            for row in _read_jsonl(pred_path):
                entry = {"response": row.get("response")}
                if row.get("reasoning"):
                    entry["reasoning"] = row["reasoning"]
                raw_map[str(row["item_id"])] = entry
        raw[judge] = raw_map
    return labels, raw, hashes


# ---------------------------------------------------------------------------
# Dev weights + voting
# ---------------------------------------------------------------------------


def dev_weights(items: list[dict[str, Any]], labels: dict[str, dict[str, str]]) -> dict[str, dict[str, float]]:
    """Per-judge per-dimension Cohen's kappa on dev items the judge covered.

    glm-5.2 only covers the stratified dev subsample — that is by design (the
    weight estimate must come from dev, never test). Negative kappas clip to 0
    at voting time; raw values are reported.
    """
    weights: dict[str, dict[str, float]] = {}
    for judge, per_item in labels.items():
        pairs_by_dim: dict[str, list[tuple[str, str]]] = defaultdict(list)
        for it in items:
            if it["split"] != "dev":
                continue
            pred = per_item.get(it["native_item_id"])
            if pred is None:
                continue
            dim = str(it["dimension"] or "pairwise")
            pairs_by_dim[dim].append((it["human_label"], pred))
        weights[judge] = {}
        for dim, pairs in pairs_by_dim.items():
            kappa = kappa_stat(pairs)
            weights[judge][dim] = 0.0 if kappa is None else kappa
    return weights


def judge_ranking(weights: dict[str, dict[str, float]]) -> list[str]:
    """Judges ordered by mean dev kappa (tie-break priority)."""
    means = {
        judge: (sum(dims.values()) / len(dims)) if dims else float("-inf")
        for judge, dims in weights.items()
    }
    return sorted(means, key=lambda j: -means[j])


def vote(
    votes: dict[str, str],
    dim: str,
    weights: dict[str, dict[str, float]],
    ranking: list[str],
) -> tuple[str, bool, str, bool]:
    """Return (majority_label, majority_tiebroken, weighted_label, weighted_tiebroken)."""
    valid = {j: lab for j, lab in votes.items() if lab not in ABSTAIN_LABELS}
    if not valid:
        return "unparsed", False, "unparsed", False

    def tie_break(candidates: set[str]) -> str:
        for judge in ranking:
            lab = valid.get(judge)
            if lab in candidates:
                return lab
        return sorted(candidates)[0]

    counts = Counter(valid.values())
    top = max(counts.values())
    leaders = {lab for lab, c in counts.items() if c == top}
    if len(leaders) == 1:
        majority, m_tb = next(iter(leaders)), False
    else:
        majority, m_tb = tie_break(leaders), True

    scores: dict[str, float] = defaultdict(float)
    for judge, lab in valid.items():
        scores[lab] += max(0.0, weights.get(judge, {}).get(dim, 0.0))
    top_w = max(scores.values())
    leaders_w = {lab for lab, s in scores.items() if abs(s - top_w) < 1e-12}
    if top_w <= 0:  # all weights clipped to zero -> fall back to majority
        return majority, m_tb, majority, m_tb
    if len(leaders_w) == 1:
        weighted, w_tb = next(iter(leaders_w)), False
    else:
        weighted, w_tb = tie_break(leaders_w), True
    return majority, m_tb, weighted, w_tb


# ---------------------------------------------------------------------------
# Metrics over payload rows
# ---------------------------------------------------------------------------
# payload = {"gold", "dim", "labels": {system: label}, "n_words", "native_item_id"}


def _pairs_for(payloads: list[dict[str, Any]], system: str, dim: str | None = None) -> list[tuple[str, str]]:
    return [
        (p["gold"], p["labels"][system])
        for p in payloads
        if dim is None or p["dim"] == dim
    ]


def macro_stat(system: str, base: Callable[[list[tuple[str, str]]], float | None]) -> Callable:
    """Macro over dimensions: apply ``base`` per dimension, average valid values."""

    def stat(payloads: list[dict[str, Any]]) -> float | None:
        by_dim: dict[str, list[tuple[str, str]]] = defaultdict(list)
        for p in payloads:
            by_dim[p["dim"]].append((p["gold"], p["labels"][system]))
        values = [v for v in (base(pairs) for pairs in by_dim.values()) if v is not None]
        return sum(values) / len(values) if values else None

    return stat


def system_metrics(
    rows: list[tuple[Any, dict[str, Any]]],
    system: str,
    dims: list[str],
    n_boot: int,
) -> dict[str, Any]:
    payloads = [p for _, p in rows]
    out: dict[str, Any] = {
        "macro": {
            "agreement": cluster_bootstrap_ci(rows, macro_stat(system, agreement_stat), n_boot=n_boot),
            "f1_macro": cluster_bootstrap_ci(rows, macro_stat(system, macro_f1_stat), n_boot=n_boot),
            "cohen_kappa": cluster_bootstrap_ci(rows, macro_stat(system, kappa_stat), n_boot=n_boot),
        },
    }
    per_dim: dict[str, Any] = {}
    for dim in dims:
        dim_rows = [(c, p) for c, p in rows if p["dim"] == dim]
        pairs = _pairs_for([p for _, p in dim_rows], system)
        per_dim[dim] = {
            "n": len(pairs),
            "agreement": _round(agreement_stat(pairs)),
            "f1_macro": _round(macro_f1_stat(pairs)),
            "cohen_kappa": cluster_bootstrap_ci(dim_rows, lambda ps, s=system: kappa_stat(_pairs_for(ps, s)), n_boot=n_boot),
        }
    out["per_dimension"] = per_dim
    abstain = sum(1 for p in payloads if p["labels"][system] in ABSTAIN_LABELS)
    out["unparsed_rate"] = _round(abstain / len(payloads)) if payloads else None
    return out


# ---------------------------------------------------------------------------
# Length bias (WP5)
# ---------------------------------------------------------------------------


def length_buckets(payloads: list[dict[str, Any]], n_buckets: int = 5) -> list[int]:
    """Quintile thresholds over unique responses (not per-item, to avoid the
    8x-per-dimension duplication skewing the cut points)."""
    unique_lengths = sorted({(p["response_key"]): p["n_words"] for p in payloads}.values())
    if not unique_lengths:
        return []
    return [
        unique_lengths[min(len(unique_lengths) - 1, (i * len(unique_lengths)) // n_buckets)]
        for i in range(1, n_buckets)
    ]


def bucket_of(n_words: int, thresholds: list[int]) -> int:
    for i, t in enumerate(thresholds):
        if n_words < t:
            return i
    return len(thresholds)


def length_bias_dimension_label(
    rows: list[tuple[Any, dict[str, Any]]],
    systems: list[str],
    n_boot: int,
) -> dict[str, Any]:
    """Per length-quintile: agreement, and leniency gap P(sys=Yes)-P(human=Yes)
    over the Yes/To-some-extent/No dimensions."""
    payloads = [p for _, p in rows]
    thresholds = length_buckets(payloads)
    result: dict[str, Any] = {
        "bucket_thresholds_words": thresholds,
        "note": (
            "leniency_gap = P(system label == 'Yes') - P(human label == 'Yes') per response-length "
            "quintile, over Yes/To some extent/No dimensions only; positive in high buckets = the "
            "system rewards longer responses more than humans do"
        ),
        "buckets": {},
    }
    yes_rows = [(c, p) for c, p in rows if p["dim"] not in YES_SCALE_EXCLUDED]
    for b in range(len(thresholds) + 1):
        b_rows = [(c, p) for c, p in rows if bucket_of(p["n_words"], thresholds) == b]
        b_yes = [(c, p) for c, p in yes_rows if bucket_of(p["n_words"], thresholds) == b]
        cell: dict[str, Any] = {
            "n_items": len(b_rows),
            "human_yes_rate": _round(
                sum(1 for _, p in b_yes if p["gold"] == "Yes") / len(b_yes)
            )
            if b_yes
            else None,
        }
        for system in systems:
            pairs = _pairs_for([p for _, p in b_rows], system)
            gap_ci = cluster_bootstrap_ci(
                b_yes,
                lambda ps, s=system: (
                    (sum(1 for p in ps if p["labels"][s] == "Yes") - sum(1 for p in ps if p["gold"] == "Yes"))
                    / len(ps)
                )
                if ps
                else None,
                n_boot=n_boot,
            )
            cell[system] = {
                "agreement": _round(agreement_stat(pairs)),
                "leniency_gap": gap_ci,
            }
        result["buckets"][f"q{b + 1}"] = cell
    return result


def length_bias_pairwise(
    rows: list[tuple[Any, dict[str, Any]]],
    systems: list[str],
    n_boot: int,
) -> dict[str, Any]:
    """P(chooses the longer response): systems vs the expert human gold.

    payload extras: len_a, len_b. Decisions where both responses have equal
    length are skipped.
    """

    def longer_rate(system: str) -> Callable:
        def stat(payloads: list[dict[str, Any]]) -> float | None:
            chose_longer = total = 0
            for p in payloads:
                if p["len_a"] == p["len_b"]:
                    continue
                lab = p["gold"] if system == "human" else p["labels"][system]
                if lab not in ("A", "B"):
                    continue
                total += 1
                longer = "A" if p["len_a"] > p["len_b"] else "B"
                chose_longer += lab == longer
            return chose_longer / total if total else None

        return stat

    result: dict[str, Any] = {
        "note": "P(chose the longer of the two responses); compare each system against the expert human rate",
        "human": cluster_bootstrap_ci(rows, longer_rate("human"), n_boot=n_boot),
    }
    for system in systems:
        result[system] = {
            "p_choose_longer": cluster_bootstrap_ci(rows, longer_rate(system), n_boot=n_boot),
            "gap_vs_human": cluster_bootstrap_diff_ci(
                rows, longer_rate(system), longer_rate("human"), n_boot=n_boot
            ),
        }
    return result


# ---------------------------------------------------------------------------
# Per-source pipeline
# ---------------------------------------------------------------------------


def process_source(
    source: str,
    items: list[dict[str, Any]],
    n_boot: int,
) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, str]]:
    print(f"== {source}")
    labels, raw, hashes = load_judge_outputs(source)
    judges = sorted(labels, key=lambda j: list(JUDGES).index(j))
    if len(judges) < 2:
        return {"skipped": f"only {len(judges)} judges with outputs"}, [], hashes

    weights = dev_weights(items, labels)
    ranking = judge_ranking(weights)
    best_single = ranking[0]

    # Build test payloads where every judge voted.
    test_items = [it for it in items if it["split"] == "test"]
    rows: list[tuple[Any, dict[str, Any]]] = []
    tie_break_counts = {"majority": 0, "weighted": 0}
    missing_any = 0
    for it in test_items:
        nid = it["native_item_id"]
        votes = {}
        for judge in judges:
            lab = labels[judge].get(nid)
            if lab is None:
                break
            votes[judge] = lab
        else:
            dim = str(it["dimension"] or "pairwise")
            majority, m_tb, weighted, w_tb = vote(votes, dim, weights, ranking)
            tie_break_counts["majority"] += m_tb
            tie_break_counts["weighted"] += w_tb
            if it["task_type"] == "pairwise_preference":
                len_a = len(str(it.get("response_a") or "").split())
                len_b = len(str(it.get("response_b") or "").split())
                n_words = max(len_a, len_b)
                response_key = nid
                extra = {"len_a": len_a, "len_b": len_b}
            else:
                n_words = len(str(it.get("response") or "").split())
                response_key = f"{it['conversation_id']}::{it['response_source_model']}"
                extra = {}
            payload = {
                "native_item_id": nid,
                "gold": it["human_label"],
                "dim": dim,
                "n_words": n_words,
                "response_key": response_key,
                "labels": {**votes, "jury_majority": majority, "jury_weighted": weighted},
                **extra,
            }
            rows.append((it["conversation_id"], payload))
            continue
        missing_any += 1
    print(f"  test items with all {len(judges)} judges: {len(rows)}/{len(test_items)} (missing {missing_any})")

    dims = sorted({p["dim"] for _, p in rows})
    systems = judges + ["jury_majority", "jury_weighted"]

    metrics = {system: system_metrics(rows, system, dims, n_boot) for system in systems}
    for jury in ("jury_majority", "jury_weighted"):
        metrics[jury]["tie_break_rate"] = _round(
            tie_break_counts[jury.split("_")[1]] / len(rows)
        ) if rows else None

    paired: dict[str, Any] = {"best_single_judge": best_single, "criterion": "highest mean dev-split kappa"}
    for jury in ("jury_majority", "jury_weighted"):
        paired[f"{jury}_minus_best"] = cluster_bootstrap_diff_ci(
            rows,
            macro_stat(jury, kappa_stat),
            macro_stat(best_single, kappa_stat),
            n_boot=n_boot,
        )

    # Disagreements (all splits where every judge voted) — J6 seed / J5 data.
    disagreements: list[dict[str, Any]] = []
    disagree_test = Counter()
    dim_totals = Counter()
    for it in items:
        nid = it["native_item_id"]
        votes = {j: labels[j].get(nid) for j in judges}
        if any(v is None for v in votes.values()):
            continue
        valid = {j: v for j, v in votes.items() if v not in ABSTAIN_LABELS}
        dim = str(it["dimension"] or "pairwise")
        if it["split"] == "test":
            dim_totals[dim] += 1
        if len(set(valid.values())) <= 1 and len(valid) == len(votes):
            continue
        if it["split"] == "test":
            disagree_test[dim] += 1
        disagreements.append(
            {
                "item_id": it["item_id"],
                "source_benchmark": source,
                "split": it["split"],
                "dimension": it["dimension"],
                "human_label": it["human_label"],
                "votes": votes,
                "judge_raw": {j: raw.get(j, {}).get(nid) for j in judges},
            }
        )

    result = {
        "n_test_items": len(rows),
        "n_test_clusters": len({c for c, _ in rows}),
        "judges": judges,
        "dev_weights_kappa": {j: {d: _round(k) for d, k in sorted(weights[j].items())} for j in judges},
        "tie_break_ranking": ranking,
        "systems": metrics,
        "paired_diff_macro_kappa": paired,
        "disagreement_rate_test": {
            "overall": _round(sum(disagree_test.values()) / sum(dim_totals.values())) if dim_totals else None,
            "per_dimension": {
                d: _round(disagree_test[d] / dim_totals[d]) for d in sorted(dim_totals) if dim_totals[d]
            },
        },
    }
    if source == "mathtutorbench":
        result["length_bias"] = length_bias_pairwise(rows, systems, n_boot)
    else:
        result["length_bias"] = length_bias_dimension_label(rows, systems, n_boot)
    return result, disagreements, hashes


# ---------------------------------------------------------------------------
# Report rendering
# ---------------------------------------------------------------------------


def _fmt_ci(cell: dict[str, Any] | None) -> str:
    if not cell or cell.get("point") is None:
        return "n/a"
    return f"{cell['point']:.3f} [{cell['ci_low']:.3f}, {cell['ci_high']:.3f}]"


def render_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# 教育裁判陪审团 vs 单裁判（judge_meta_eval_v1 · test split）",
        "",
        f"- 生成脚本：`scripts/build_judge_jury_report.py`（n_boot={summary['n_boot']}, seed={summary['seed']}）",
        "- 陪审团：deepseek-v4-pro / glm-5.2 / MiniMax-M3；多数投票 + dev-kappa 加权投票",
        "- 所有区间为 cluster bootstrap 95% CI（重采样单元 = 对话/偏好对）；主判定 = 陪审团与最佳单裁判的 macro kappa 配对差值",
        "",
    ]
    for source, res in summary["per_source"].items():
        lines.append(f"## {source}")
        lines.append("")
        if "skipped" in res:
            lines.append(f"跳过：{res['skipped']}")
            lines.append("")
            continue
        lines.append(
            f"test 集：{res['n_test_items']} 条判例 / {res['n_test_clusters']} 个对话簇；"
            f"最佳单裁判（dev kappa）= **{res['paired_diff_macro_kappa']['best_single_judge']}**"
        )
        lines.append("")
        lines.append("| 系统 | macro kappa | macro agreement | macro F1 | unparsed/弃权 |")
        lines.append("|---|---|---|---|---|")
        for system, m in res["systems"].items():
            lines.append(
                f"| {system} | {_fmt_ci(m['macro']['cohen_kappa'])} | {_fmt_ci(m['macro']['agreement'])} "
                f"| {_fmt_ci(m['macro']['f1_macro'])} | {m.get('unparsed_rate')} |"
            )
        lines.append("")
        paired = res["paired_diff_macro_kappa"]
        for jury in ("jury_majority", "jury_weighted"):
            d = paired[f"{jury}_minus_best"]
            verdict = (
                "显著更优" if d.get("significant") and (d.get("point") or 0) > 0
                else "显著更差" if d.get("significant")
                else "无显著差异"
            )
            lines.append(
                f"- **{jury} − {paired['best_single_judge']}**（macro kappa 配对差值）："
                f"{_fmt_ci(d)} → **{verdict}**"
            )
        dr = res["disagreement_rate_test"]
        lines.append(f"- test 集三票分歧率：{dr['overall']}（per-dimension 见 summary.json）")
        lines.append("")
    lines.append("## 长度偏置（WP5）")
    lines.append("")
    lines.append("见 summary.json 每个来源的 `length_bias`：dimension_label 线为响应长度五分位的")
    lines.append("agreement 与宽容度差 P(sys=Yes)−P(human=Yes)；pairwise 线为 P(选更长回复) 与人类专家的差值。")
    lines.append("")
    return "\n".join(lines)


def render_html(markdown: str) -> str:
    # Minimal renderer: tables + headings + list items, monospace-safe.
    import html as _html

    out = [
        "<!DOCTYPE html><html><head><meta charset='utf-8'><title>Judge jury report</title>",
        "<style>body{font-family:system-ui,sans-serif;max-width:1080px;margin:2rem auto;padding:0 1rem;}"
        "table{border-collapse:collapse;margin:1rem 0;}td,th{border:1px solid #ccc;padding:4px 10px;font-size:14px;}"
        "th{background:#f5f5f5;}</style></head><body>",
    ]
    in_table = False
    for line in markdown.splitlines():
        stripped = line.strip()
        if stripped.startswith("|"):
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            if all(set(c) <= {"-", ":", " "} and c for c in cells):
                continue
            if not in_table:
                out.append("<table>")
                in_table = True
                out.append("<tr>" + "".join(f"<th>{_html.escape(c)}</th>" for c in cells) + "</tr>")
            else:
                out.append("<tr>" + "".join(f"<td>{_html.escape(c)}</td>" for c in cells) + "</tr>")
            continue
        if in_table:
            out.append("</table>")
            in_table = False
        if stripped.startswith("# "):
            out.append(f"<h1>{_html.escape(stripped[2:])}</h1>")
        elif stripped.startswith("## "):
            out.append(f"<h2>{_html.escape(stripped[3:])}</h2>")
        elif stripped.startswith("- "):
            out.append(f"<li>{_html.escape(stripped[2:]).replace('**', '')}</li>")
        elif stripped:
            out.append(f"<p>{_html.escape(stripped)}</p>")
    if in_table:
        out.append("</table>")
    out.append("</body></html>")
    return "\n".join(out)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--n-boot", type=int, default=1000, help="bootstrap resamples (default 1000)")
    args = parser.parse_args()

    by_source = load_meta_items()
    all_hashes: dict[str, str] = {"judge_meta_eval_v1/items.jsonl": _sha256_file(META_DIR / "items.jsonl")}
    per_source: dict[str, Any] = {}
    all_disagreements: list[dict[str, Any]] = []
    for source in SOURCES:
        result, disagreements, hashes = process_source(source, by_source.get(source, []), args.n_boot)
        per_source[source] = result
        all_disagreements.extend(disagreements)
        all_hashes.update(hashes)

    summary = {
        "report": "judge jury vs single judge on judge_meta_eval_v1 test split",
        "plan": "doc/judge_research_plan_2026-07-06.md (WP4/WP5)",
        "jury": list(JUDGES),
        "n_boot": args.n_boot,
        "seed": DEFAULT_SEED,
        "voting_rules": {
            "majority": "most common valid label; unparsed/no_choice abstain; tie -> highest mean dev-kappa judge",
            "weighted": "label score = sum of per-dimension dev-split kappa (clipped at 0) of judges voting it",
        },
        "input_hashes": all_hashes,
        "per_source": per_source,
        "n_disagreements": len(all_disagreements),
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with (OUT_DIR / "disagreements.jsonl").open("w", encoding="utf-8") as fh:
        for row in all_disagreements:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    markdown = render_markdown(summary)
    (OUT_DIR / "jury_report.md").write_text(markdown, encoding="utf-8")
    (OUT_DIR / "jury_report.html").write_text(render_html(markdown), encoding="utf-8")
    print(f"\nwrote {OUT_DIR}/summary.json, jury_report.md/.html, disagreements.jsonl ({len(all_disagreements)} rows)")


if __name__ == "__main__":
    main()
