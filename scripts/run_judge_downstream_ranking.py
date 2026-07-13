#!/usr/bin/env python3
"""Downstream-ranking experiment (judge research report §9.4 #4).

Question: after the production judge-rubric upgrade v1→v2 (mrbench
Providing_Guidance only, Stage-3 test-validated), do the RANKINGS of tested
models on mrbench_tutor change — i.e. does a better-calibrated judge change
evaluation conclusions, or only absolute numbers?

Design (cheap by construction): v1 and v2 judge prompts differ ONLY in the
Providing_Guidance dimension, and the tutor headline (pedagogical pass rate)
needs only the three key dimensions. So per cached generation we make 4 judge
calls — Mistake_Identification / Actionability (shared by both versions) +
Providing_Guidance under v1 AND under v2 — instead of 2×8.

Inputs: cached generations reports/eval/mrbench_tutor/<model>/predictions.jsonl
(the tested models are NOT re-run). Judge is fixed (DOWNSTREAM_JUDGE_MODEL or
MRBENCH_JUDGE_MODEL, default glm-5.2 — the production judge), decoupled from
the tested models.

Outputs under reports/eval/_judge_rubric/downstream_ranking/:
- responses.jsonl   one row per (tested_model, item, dimension, version):
                    raw judge reply + normalized label (resumable cache)
- summary.json      per-model v1/v2 pass rates + paired cluster-bootstrap CI
                    of the per-item pass diff, PG label flip matrix, rankings
                    under v1 vs v2, and ranking-stability bootstrap

Usage:
    python3 run_judge_downstream_ranking.py --concurrency 6
    python3 run_judge_downstream_ranking.py --models minimax3,glm-5.2 --limit 20
"""

from __future__ import annotations

import argparse
import json
import os
import random
import threading
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from eval.base import prompt_sha256
from eval.benchmarks.mrbench import (
    MRBenchTutorAdapter,
    _evolved_judge_prompt,
    _judge_prompt,
    _normalize_label,
)
from eval.providers import build_client
from eval.stats import cluster_bootstrap_diff_ci

ROOT = Path(__file__).resolve().parents[1]
TUTOR_RUNS = ROOT / "reports" / "eval" / "mrbench_tutor"
OUT_DIR = ROOT / "reports" / "eval" / "_judge_rubric" / "downstream_ranking"

JUDGE_MODEL = (
    os.environ.get("DOWNSTREAM_JUDGE_MODEL")
    or os.environ.get("MRBENCH_JUDGE_MODEL")
    or "glm-5.2"
)
KEY_DIMENSIONS = ["Mistake_Identification", "Providing_Guidance", "Actionability"]
# (dimension, prompt_version) pairs actually judged. MI/Actionability are
# byte-identical between v1 and v2 (asserted in main), so they are judged once
# and shared; only Providing_Guidance is judged under both versions.
JUDGE_TASKS = [
    ("Mistake_Identification", "shared"),
    ("Actionability", "shared"),
    ("Providing_Guidance", "v1"),
    ("Providing_Guidance", "v2"),
]


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _prompt_for(dim: str, version: str, conv: str, response: str) -> str:
    if version == "v2":
        return _evolved_judge_prompt(dim, conv, response)
    return _judge_prompt(dim, conv, response)


def judge_call(client: Any, dim: str, version: str, conv: str, response: str) -> tuple[str, str]:
    prompt = _prompt_for(dim, version, conv, response)
    last = ""
    for attempt in range(3):
        try:
            # No max_tokens cap: glm's inline CoT spends the budget before the
            # label, and a cap returns empty content that scores as a fail —
            # which hit the longer v2 rubric prompt hardest (70 vs 17 empties)
            # and faked a v2 pass-rate drop. Stage 1's judge is uncapped too.
            reply = client.chat([{"role": "user", "content": prompt}], model=JUDGE_MODEL)
            last = reply or ""
            label = _normalize_label(dim, last)
            if label != "unparsed":
                return label, last
        except Exception as exc:  # noqa: BLE001 - transient judge failures
            last = f"<error: {exc}>"
        time.sleep(1.5 * (attempt + 1))
    return "unparsed", last


def pass_label(labels: dict[str, str], pg_version: str) -> bool:
    pg = labels.get(("Providing_Guidance", pg_version))
    return (
        labels.get(("Mistake_Identification", "shared")) == "Yes"
        and labels.get(("Actionability", "shared")) == "Yes"
        and pg == "Yes"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--models", default=None,
                        help="comma-separated tested-model dirs under mrbench_tutor/ (default: all with predictions.jsonl)")
    parser.add_argument("--limit", type=int, default=0, help="cap items per model (smoke tests only)")
    parser.add_argument("--concurrency", type=int, default=6)
    parser.add_argument("--n-boot", type=int, default=1000)
    args = parser.parse_args()

    # v1/v2 must differ ONLY in Providing_Guidance for the shared-dim shortcut.
    for dim in ("Mistake_Identification", "Actionability"):
        assert _judge_prompt(dim, "{c}", "{r}") == _evolved_judge_prompt(dim, "{c}", "{r}"), dim
    assert _judge_prompt("Providing_Guidance", "{c}", "{r}") != _evolved_judge_prompt("Providing_Guidance", "{c}", "{r}")

    if args.models:
        models = [m.strip() for m in args.models.split(",") if m.strip()]
    else:
        models = sorted(d.name for d in TUTOR_RUNS.iterdir() if (d / "predictions.jsonl").exists())
    conv_by_id = {
        it["item_id"]: it["meta"]["conversation_history"]
        for it in MRBenchTutorAdapter().load_items()
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    resp_path = OUT_DIR / "responses.jsonl"
    done: dict[tuple[str, str, str, str], dict[str, Any]] = {}
    if resp_path.exists():
        for r in _read_jsonl(resp_path):
            done[(r["tested_model"], r["item_id"], r["dimension"], r["version"])] = r

    todo: list[tuple[str, str, str, str, str, str]] = []
    items_by_model: dict[str, list[str]] = {}
    for model in models:
        preds = _read_jsonl(TUTOR_RUNS / model / "predictions.jsonl")
        if args.limit:
            preds = preds[: args.limit]
        ids = []
        for p in preds:
            iid = str(p["item_id"])
            conv = conv_by_id.get(iid)
            if conv is None:
                continue
            ids.append(iid)
            for dim, version in JUDGE_TASKS:
                if (model, iid, dim, version) not in done:
                    todo.append((model, iid, dim, version, conv, str(p.get("response") or "")))
        items_by_model[model] = ids

    print(f"judge={JUDGE_MODEL} models={models} cached={len(done)} todo={len(todo)}")
    if todo:
        client = build_client(JUDGE_MODEL)
        lock = threading.Lock()
        counter = [0]

        def run_one(task: tuple[str, str, str, str, str, str]) -> None:
            model, iid, dim, version, conv, response = task
            label, raw = judge_call(client, dim, version, conv, response)
            row = {
                "tested_model": model, "item_id": iid, "dimension": dim,
                "version": version, "label": label,
                "raw_tail": raw[-400:],
            }
            with lock:
                with resp_path.open("a", encoding="utf-8") as fh:
                    fh.write(json.dumps(row, ensure_ascii=False) + "\n")
                done[(model, iid, dim, version)] = row
                counter[0] += 1
                if counter[0] % 50 == 0:
                    print(f"  {counter[0]}/{len(todo)} last={model}/{iid}/{dim}/{version} label={label}")

        with ThreadPoolExecutor(max_workers=args.concurrency) as pool:
            list(pool.map(run_one, todo))

    # ---- analysis ----
    per_model: dict[str, dict[str, Any]] = {}
    pass_rows_by_model: dict[str, list[dict[str, Any]]] = {}
    for model in models:
        rows = []
        flips: Counter = Counter()
        pg_dist = {"v1": Counter(), "v2": Counter()}
        unparsed = 0
        for iid in items_by_model[model]:
            labels = {
                (dim, version): done[(model, iid, dim, version)]["label"]
                for dim, version in JUDGE_TASKS
                if (model, iid, dim, version) in done
            }
            if len(labels) < len(JUDGE_TASKS):
                continue
            unparsed += sum(1 for v in labels.values() if v == "unparsed")
            v1p, v2p = pass_label(labels, "v1"), pass_label(labels, "v2")
            pg1, pg2 = labels[("Providing_Guidance", "v1")], labels[("Providing_Guidance", "v2")]
            pg_dist["v1"][pg1] += 1
            pg_dist["v2"][pg2] += 1
            if pg1 != pg2:
                flips[f"{pg1} -> {pg2}"] += 1
            rows.append({"cluster": iid, "v1": 1.0 if v1p else 0.0, "v2": 1.0 if v2p else 0.0})
        pass_rows_by_model[model] = rows
        n = len(rows)
        diff = cluster_bootstrap_diff_ci(
            [(r["cluster"], (r["v1"], r["v2"])) for r in rows],
            stat_a=lambda ps: sum(p[1] for p in ps) / len(ps) if ps else None,
            stat_b=lambda ps: sum(p[0] for p in ps) / len(ps) if ps else None,
            n_boot=args.n_boot,
        ) if n else None
        per_model[model] = {
            "n": n,
            "pass_rate_v1": round(sum(r["v1"] for r in rows) / n, 4) if n else None,
            "pass_rate_v2": round(sum(r["v2"] for r in rows) / n, 4) if n else None,
            "pass_diff_v2_minus_v1_ci": diff,
            "pg_label_dist": {v: dict(sorted(c.items())) for v, c in pg_dist.items()},
            "pg_flip_matrix": dict(sorted(flips.items())),
            "unparsed_labels": unparsed,
        }

    def ranking(version: str) -> list[str]:
        return sorted(
            models,
            key=lambda m: -(per_model[m][f"pass_rate_{version}"] or 0.0),
        )

    # ranking-stability bootstrap: resample dialogues jointly across models
    rng = random.Random(20260712)
    common = sorted(set.intersection(*(set(items_by_model[m]) for m in models))) if models else []
    by_key = {
        (m, r["cluster"]): r for m in models for r in pass_rows_by_model[m]
    }
    same_rank = {"v1": 0, "v2": 0}
    rank_v1, rank_v2 = ranking("v1"), ranking("v2")
    n_rank_boot = min(args.n_boot, 1000)
    for _ in range(n_rank_boot):
        sample = [common[rng.randrange(len(common))] for _ in common]
        for version, base in (("v1", rank_v1), ("v2", rank_v2)):
            rates = {
                m: sum(by_key[(m, iid)][version] for iid in sample if (m, iid) in by_key) for m in models
            }
            if sorted(models, key=lambda m: -rates[m]) == base:
                same_rank[version] += 1

    summary = {
        "experiment": "downstream ranking v1 vs v2 judge rubric (report §9.4 #4)",
        "judge_model": JUDGE_MODEL,
        "judge_prompt_sha256": {
            "v1_pg": prompt_sha256(_judge_prompt("Providing_Guidance", "{c}", "{r}")),
            "v2_pg": prompt_sha256(_evolved_judge_prompt("Providing_Guidance", "{c}", "{r}")),
        },
        "tested_models": models,
        "per_model": per_model,
        "ranking_v1": rank_v1,
        "ranking_v2": rank_v2,
        "ranking_changed": rank_v1 != rank_v2,
        "ranking_bootstrap_stability": {
            v: round(same_rank[v] / n_rank_boot, 4) for v in ("v1", "v2")
        },
        "n_boot": args.n_boot,
    }
    (OUT_DIR / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({k: summary[k] for k in ("ranking_v1", "ranking_v2", "ranking_changed")}, ensure_ascii=False))
    for m in models:
        pm = per_model[m]
        print(f"{m}: v1={pm['pass_rate_v1']} v2={pm['pass_rate_v2']} flips={sum(pm['pg_flip_matrix'].values())}")
    print(f"wrote {OUT_DIR / 'summary.json'}")


if __name__ == "__main__":
    main()
