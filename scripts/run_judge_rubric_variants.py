#!/usr/bin/env python3
"""Stage 0b: DPFS few-shot anchor variants for the judge rubric prompt.

Plan: doc/rubric_evolution_plan_2026-07-06.md. Two prompt variants against the
cached v1 baseline (glm-5.2 already ran rubric v1 on the evaluation slice):

- ``dpfs``      per-dimension K=6 human-labeled anchor examples whose label
                proportions mirror the human marginal distribution
                (distribution-preserving few-shot sampling);
- ``dpfs_cal``  dpfs + one explicit calibration line stating the human label
                distribution and warning against over-using the middle label
                (targets the measured Yes/To-some-extent boundary defect).

Protocol guards (plan section 4): anchors come from dev OUTSIDE the evaluation
slice (asserted); the evaluation slice is ``split_dev_subsample_glm``; the
test split is never read. Outputs land under
``reports/eval/_judge_rubric/stage0/<benchmark>_<variant>/`` with prompt
template + anchor hashes for provenance. Resumable: responses are appended to
``responses.jsonl`` keyed by item_id and skipped on rerun.

Usage (needs API_GATEWAY):
    python scripts/run_judge_rubric_variants.py --benchmark mrbench --variant dpfs
    python scripts/run_judge_rubric_variants.py --benchmark bea2025 --variant dpfs_cal --concurrency 6
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import time
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from eval.base import prompt_sha256
from eval.benchmarks import bea2025 as bea_mod
from eval.benchmarks import mrbench as mr_mod
from eval.providers import build_client
from eval.stats import cluster_bootstrap_ci, cluster_bootstrap_diff_ci, kappa_stat

ROOT = Path(__file__).resolve().parents[1]
META_DIR = ROOT / "data" / "judge_meta_eval_v1"
OUT_BASE = ROOT / "reports" / "eval" / "_judge_rubric" / "stage0"

SEED = 20260706
K_ANCHORS = 6
CONTEXT_TAIL_CHARS = 400
JUDGE_MODEL = "glm-5.2"
BASELINE_DIRS = {"mrbench": "mrbench_judge", "bea2025": "bea2025_judge"}
VARIANT_VERSION = {"dpfs": "v1+dpfs6", "dpfs_cal": "v1+dpfs6+cal"}


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    if not path.exists():
        return rows
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def adapter_bits(benchmark: str):
    """(dimensions dict, judge_prompt fn, normalize fn) mirroring the adapter."""
    if benchmark == "mrbench":
        return mr_mod.DIMENSIONS, mr_mod._judge_prompt, mr_mod._normalize_label
    if benchmark == "bea2025":
        dims = {d: {**cfg, "labels": bea_mod.LABELS} for d, cfg in bea_mod.DIMENSIONS.items()}
        return dims, bea_mod._judge_prompt, lambda dim, text: bea_mod._normalize_label(text)
    raise SystemExit(f"unsupported benchmark {benchmark}")


def load_items(benchmark: str) -> tuple[list[dict[str, Any]], dict[str, str]]:
    items = [r for r in _read_jsonl(META_DIR / "items.jsonl") if r["source_benchmark"] == benchmark]
    contexts = {
        r["conversation_id"]: r["context"]
        for r in _read_jsonl(META_DIR / "contexts.jsonl")
        if r["source_benchmark"] == benchmark
    }
    return items, contexts


def select_anchors(
    items: list[dict[str, Any]], eval_ids: set[str], dims: dict[str, Any], rng: random.Random
) -> dict[str, list[dict[str, Any]]]:
    """DPFS: per dimension, K anchors from the dev anchor pool whose label
    counts follow the human marginals (largest-remainder allocation)."""
    pool = [it for it in items if it["split"] == "dev" and it["native_item_id"] not in eval_ids]
    anchors: dict[str, list[dict[str, Any]]] = {}
    for dim in dims:
        dim_pool = [it for it in pool if str(it["dimension"]) == dim]
        by_label: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for it in dim_pool:
            by_label[it["human_label"]].append(it)
        total = len(dim_pool)
        # Largest-remainder allocation of K over labels.
        quotas = {lab: K_ANCHORS * len(rows) / total for lab, rows in by_label.items()}
        counts = {lab: int(q) for lab, q in quotas.items()}
        for lab in sorted(quotas, key=lambda l: -(quotas[l] - counts[l])):
            if sum(counts.values()) >= K_ANCHORS:
                break
            counts[lab] += 1
        chosen: list[dict[str, Any]] = []
        for lab in sorted(counts):
            rows = sorted(by_label[lab], key=lambda it: it["native_item_id"])
            # Prefer compact responses so the prompt stays bounded.
            compact = [it for it in rows if 8 <= len(str(it["response"]).split()) <= 80] or rows
            chosen.extend(rng.sample(compact, min(counts[lab], len(compact))))
        rng.shuffle(chosen)  # avoid label-ordered anchors
        anchors[dim] = chosen
        for a in chosen:
            assert a["native_item_id"] not in eval_ids, "anchor leaked from evaluation slice"
            assert a["split"] == "dev", "anchor leaked from test split"
    return anchors


def human_marginals(items: list[dict[str, Any]], eval_ids: set[str], dim: str) -> dict[str, float]:
    pool = [
        it for it in items
        if it["split"] == "dev" and it["native_item_id"] not in eval_ids and str(it["dimension"]) == dim
    ]
    dist = Counter(it["human_label"] for it in pool)
    return {lab: n / len(pool) for lab, n in sorted(dist.items())}


def anchor_block(
    dim_cfg: dict[str, Any], anchors: list[dict[str, Any]], contexts: dict[str, str],
    marginals: dict[str, float] | None,
) -> str:
    parts = [
        "Before judging, calibrate yourself with real examples labeled by expert human annotators "
        f"on this dimension ({dim_cfg['title']}):",
        "",
    ]
    for i, a in enumerate(anchors, 1):
        tail = str(contexts.get(a["conversation_id"], ""))[-CONTEXT_TAIL_CHARS:]
        parts += [
            f"Example {i}:",
            f"Conversation (final part): ...{tail}",
            f"Tutor reply: {a['response']}",
            f"Expert label: {a['human_label']}",
            "",
        ]
    if marginals is not None:
        dist = ", ".join(f"{lab}: {p:.0%}" for lab, p in marginals.items())
        parts += [
            f"Calibration note: across many cases, expert annotators' labels on this dimension are "
            f"distributed approximately as {dist}. Match this calibration. In particular, do not "
            f"choose a middle/partial label where an expert annotator would simply answer the "
            f"positive label.",
            "",
        ]
    return "\n".join(parts)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--benchmark", required=True, choices=sorted(BASELINE_DIRS))
    parser.add_argument("--variant", required=True, choices=sorted(VARIANT_VERSION))
    parser.add_argument("--concurrency", type=int, default=6)
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--n-boot", type=int, default=1000)
    parser.add_argument("--score-only", action="store_true", help="reuse existing responses; score only")
    args = parser.parse_args()

    dims, judge_prompt, normalize = adapter_bits(args.benchmark)
    items, contexts = load_items(args.benchmark)
    eval_ids = set(
        (META_DIR / "split_dev_subsample_glm" / f"{args.benchmark}.txt").read_text(encoding="utf-8").split()
    )
    eval_items = [it for it in items if it["native_item_id"] in eval_ids]
    rng = random.Random(SEED)
    anchors = select_anchors(items, eval_ids, dims, rng)
    with_cal = args.variant == "dpfs_cal"
    marginals = {dim: human_marginals(items, eval_ids, dim) for dim in dims} if with_cal else {}

    out_dir = OUT_BASE / f"{args.benchmark}_{args.variant}"
    out_dir.mkdir(parents=True, exist_ok=True)
    resp_path = out_dir / "responses.jsonl"

    def build_prompt(it: dict[str, Any]) -> str:
        dim = str(it["dimension"])
        block = anchor_block(dims[dim], anchors[dim], contexts, marginals.get(dim))
        base = judge_prompt(dim, contexts.get(it["conversation_id"], ""), it["response"])
        return f"{block}\nNow judge the following case.\n\n{base}"

    template_hash = prompt_sha256(
        *(
            anchor_block(dims[d], anchors[d], contexts, marginals.get(d))
            + "\n"
            + judge_prompt(d, "{conversation_history}", "{response}")
            for d in dims
        )
    )

    done = {r["item_id"] for r in _read_jsonl(resp_path) if str(r.get("response") or "").strip()}
    pending = [it for it in eval_items if it["native_item_id"] not in done]
    print(f"{args.benchmark}/{args.variant}: eval={len(eval_items)} cached={len(done)} to_run={len(pending)}")

    if pending and not args.score_only:
        client = build_client(JUDGE_MODEL)

        def call(it: dict[str, Any]) -> dict[str, Any]:
            prompt = build_prompt(it)
            started = time.time()
            error = None
            text = ""
            for attempt in range(args.retries):
                try:
                    # No max_tokens cap: glm-5.2 spends budget on thinking before
                    # the answer; a 1024 cap starved ~17% of items into empty
                    # content (the v1 baseline run is uncapped, same as here).
                    text = client.chat(
                        [{"role": "user", "content": prompt}],
                        model=JUDGE_MODEL,
                    )
                    error = None
                    if text.strip():
                        break
                except Exception as exc:  # noqa: BLE001
                    error = str(exc)
                time.sleep(1.5 * (attempt + 1))
            row = {
                "item_id": it["native_item_id"],
                "response": text,
                "latency_seconds": round(time.time() - started, 2),
            }
            if error:
                row["error"] = error
            return row

        completed = 0
        with ThreadPoolExecutor(max_workers=args.concurrency) as pool, resp_path.open("a", encoding="utf-8") as fh:
            for row in pool.map(call, pending):
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")
                fh.flush()
                completed += 1
                if completed % 100 == 0 or row.get("error"):
                    print(f"  {completed}/{len(pending)} last={row['item_id']} err={row.get('error')}")

    # ---- score: variant vs cached v1 baseline, paired on the same items ----
    responses = {r["item_id"]: r for r in _read_jsonl(resp_path) if str(r.get("response") or "").strip()}
    baseline_path = ROOT / "reports" / "eval" / BASELINE_DIRS[args.benchmark] / JUDGE_MODEL / "scored.jsonl"
    baseline = {
        str(r["item_id"]): str(r["pred_label"])
        for r in _read_jsonl(baseline_path)
        if r.get("score_status") == "scored" and "pred_label" in r
    }
    rows = []
    unparsed = 0
    for it in eval_items:
        nid = it["native_item_id"]
        if nid not in responses or nid not in baseline:
            continue
        dim = str(it["dimension"])
        label = normalize(dim, responses[nid]["response"])
        unparsed += label == "unparsed"
        rows.append(
            (it["conversation_id"], {"dim": dim, "gold": it["human_label"], "variant": label, "baseline": baseline[nid]})
        )

    def macro_kappa(which: str):
        def stat(payloads):
            by_dim = defaultdict(list)
            for p in payloads:
                by_dim[p["dim"]].append((p["gold"], p[which]))
            vals = [v for v in (kappa_stat(ps) for ps in by_dim.values()) if v is not None]
            return sum(vals) / len(vals) if vals else None
        return stat

    diff = cluster_bootstrap_diff_ci(rows, macro_kappa("variant"), macro_kappa("baseline"), n_boot=args.n_boot)
    per_dim = {}
    for dim in dims:
        dim_rows = [(c, p) for c, p in rows if p["dim"] == dim]
        per_dim[dim] = {
            "n": len(dim_rows),
            "kappa_baseline": cluster_bootstrap_ci(
                dim_rows, lambda ps: kappa_stat([(p["gold"], p["baseline"]) for p in ps]), n_boot=0
            )["point"],
            "kappa_variant": cluster_bootstrap_ci(
                dim_rows, lambda ps: kappa_stat([(p["gold"], p["variant"]) for p in ps]), n_boot=0
            )["point"],
            "anchor_labels": Counter(a["human_label"] for a in anchors[dim]),
        }

    summary = {
        "stage": "0b DPFS anchor variants",
        "plan": "doc/rubric_evolution_plan_2026-07-06.md",
        "benchmark": args.benchmark,
        "variant": args.variant,
        "judge_model": JUDGE_MODEL,
        "judge_prompt_version": VARIANT_VERSION[args.variant],
        "judge_prompt_sha256": template_hash,
        "k_anchors": K_ANCHORS,
        "seed": SEED,
        "n_eval": len(rows),
        "unparsed": unparsed,
        "macro_kappa_baseline": diff["point_b"],
        "macro_kappa_variant": diff["point_a"],
        "paired_diff": diff,
        "per_dimension": per_dim,
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2, default=dict) + "\n", encoding="utf-8")
    print(
        f"\n{args.benchmark}/{args.variant}: baseline {diff['point_b']} -> variant {diff['point_a']} "
        f"(diff {diff['point']} [{diff['ci_low']}, {diff['ci_high']}] sig={diff['significant']}), "
        f"unparsed={unparsed}/{len(rows)}"
    )
    print(f"wrote {out_dir / 'summary.json'}")


if __name__ == "__main__":
    main()
