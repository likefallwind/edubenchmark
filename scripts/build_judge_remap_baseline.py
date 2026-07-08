#!/usr/bin/env python3
"""Stage 0a: post-hoc label-remapping floor for judge calibration.

Plan: doc/rubric_evolution_plan_2026-07-06.md. Diagnosis showed the judges'
main defect is marginal miscalibration (systematically stricter than human
annotators), which may not need any rubric evolution to fix. This script
measures how much of the judge-human kappa gap a pure output-side label
remapping closes — the *floor* any rubric-evolution method must beat.

Method, per (judge, benchmark, dimension):

1. learn on dev items OUTSIDE the evaluation slice: enumerate every mapping
   from observed source labels (canonical + ``unparsed``) to canonical labels
   and keep the one with the highest dev kappa (ties -> fewest changes vs
   identity);
2. evaluate on the frozen evaluation slice (``split_dev_subsample_glm``):
   report identity vs remapped kappa with a paired cluster-bootstrap CI.

The test split is never touched (protocol rule 1). mathtutorbench (pairwise
A/B) is excluded — remapping letters is meaningless there. Judges without
full dev coverage (glm-5.2 until its full run lands) are skipped with a note.

Offline only — no API calls. Output: reports/eval/_judge_rubric/stage0/remap/
"""

from __future__ import annotations

import argparse
import itertools
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from eval.stats import cluster_bootstrap_ci, cluster_bootstrap_diff_ci, kappa_stat

ROOT = Path(__file__).resolve().parents[1]
META_DIR = ROOT / "data" / "judge_meta_eval_v1"
OUT_DIR = ROOT / "reports" / "eval" / "_judge_rubric" / "stage0" / "remap"

JUDGES = {"deepseek-v4-pro": "deepseek-v4-pro", "glm-5.2": "glm-5.2", "MiniMax-M3": "minimax3"}
SOURCES = {"mrbench": "mrbench_judge", "bea2025": "bea2025_judge"}
N_BOOT = 1000


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def load_meta(source: str) -> list[dict[str, Any]]:
    return [r for r in _read_jsonl(META_DIR / "items.jsonl") if r["source_benchmark"] == source]


def load_preds(source: str, judge: str) -> dict[str, str]:
    path = ROOT / "reports" / "eval" / SOURCES[source] / JUDGES[judge] / "scored.jsonl"
    if not path.exists():
        return {}
    return {
        str(r["item_id"]): str(r["pred_label"])
        for r in _read_jsonl(path)
        if r.get("score_status") == "scored" and "pred_label" in r
    }


def best_mapping(pairs: list[tuple[str, str]], targets: list[str]) -> dict[str, str]:
    """Exhaustive search over source-label -> target-label mappings, maximizing
    kappa on the learning pool; ties prefer the mapping closest to identity."""
    sources = sorted({p for _, p in pairs})
    best: tuple[float, int, dict[str, str]] | None = None
    for combo in itertools.product(targets, repeat=len(sources)):
        mapping = dict(zip(sources, combo))
        mapped = [(g, mapping[p]) for g, p in pairs]
        kappa = kappa_stat(mapped)
        if kappa is None:
            continue
        changes = sum(1 for s in sources if mapping[s] != s)
        key = (kappa, -changes)
        if best is None or key > (best[0], best[1]):
            best = (kappa, -changes, mapping)
    return best[2] if best else {s: s for s in sources}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--n-boot", type=int, default=N_BOOT)
    args = parser.parse_args()

    summary: dict[str, Any] = {
        "stage": "0a post-hoc label remapping floor",
        "plan": "doc/rubric_evolution_plan_2026-07-06.md",
        "protocol": "learn on dev minus eval slice; evaluate on eval slice; test untouched",
        "n_boot": args.n_boot,
        "per_source": {},
    }

    for source in SOURCES:
        items = load_meta(source)
        eval_ids = set(
            (META_DIR / "split_dev_subsample_glm" / f"{source}.txt").read_text(encoding="utf-8").split()
        )
        by_id = {it["native_item_id"]: it for it in items}
        dims = sorted({str(it["dimension"]) for it in items})
        src_result: dict[str, Any] = {}

        for judge in JUDGES:
            preds = load_preds(source, judge)
            if not preds:
                src_result[judge] = {"skipped": "no outputs"}
                continue
            # Learning pool: dev, outside the eval slice, judge covered.
            learn = [
                it for it in items
                if it["split"] == "dev" and it["native_item_id"] not in eval_ids and it["native_item_id"] in preds
            ]
            eval_items = [
                it for it in items if it["native_item_id"] in eval_ids and it["native_item_id"] in preds
            ]
            if len(learn) < 500:
                src_result[judge] = {
                    "skipped": f"learning pool too small ({len(learn)} items) — full dev coverage not available yet"
                }
                continue

            mappings: dict[str, dict[str, str]] = {}
            for dim in dims:
                pairs = [
                    (it["human_label"], preds[it["native_item_id"]])
                    for it in learn if str(it["dimension"]) == dim
                ]
                targets = sorted({g for g, _ in pairs})
                mappings[dim] = best_mapping(pairs, targets)

            # Paired evaluation on the eval slice: identity vs remapped.
            rows = []
            for it in eval_items:
                dim = str(it["dimension"])
                raw = preds[it["native_item_id"]]
                rows.append(
                    (
                        it["conversation_id"],
                        {
                            "dim": dim,
                            "gold": it["human_label"],
                            "identity": raw,
                            "remapped": mappings[dim].get(raw, raw),
                        },
                    )
                )

            def macro_kappa(which: str):
                def stat(payloads):
                    by_dim = defaultdict(list)
                    for p in payloads:
                        by_dim[p["dim"]].append((p["gold"], p[which]))
                    vals = [v for v in (kappa_stat(ps) for ps in by_dim.values()) if v is not None]
                    return sum(vals) / len(vals) if vals else None
                return stat

            diff = cluster_bootstrap_diff_ci(rows, macro_kappa("remapped"), macro_kappa("identity"), n_boot=args.n_boot)
            per_dim = {}
            for dim in dims:
                dim_rows = [(c, p) for c, p in rows if p["dim"] == dim]
                per_dim[dim] = {
                    "mapping": {k: v for k, v in mappings[dim].items() if k != v} or "identity",
                    "kappa_identity": cluster_bootstrap_ci(
                        dim_rows, lambda ps: kappa_stat([(p["gold"], p["identity"]) for p in ps]), n_boot=0
                    )["point"],
                    "kappa_remapped": cluster_bootstrap_ci(
                        dim_rows, lambda ps: kappa_stat([(p["gold"], p["remapped"]) for p in ps]), n_boot=0
                    )["point"],
                }
            src_result[judge] = {
                "n_learn": len(learn),
                "n_eval": len(rows),
                "macro_kappa_identity": diff["point_b"],
                "macro_kappa_remapped": diff["point_a"],
                "paired_diff": diff,
                "per_dimension": per_dim,
            }
            print(
                f"{source} / {judge}: identity {diff['point_b']} -> remapped {diff['point_a']} "
                f"(diff {diff['point']} [{diff['ci_low']}, {diff['ci_high']}] sig={diff['significant']})"
            )
        summary["per_source"][source] = src_result

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"\nwrote {OUT_DIR / 'summary.json'}")


if __name__ == "__main__":
    main()
