#!/usr/bin/env python3
"""Build the fixed evaluation sample for K12Vista (P04 多模态学科理解与推理).

The full benchmark is 33k items with base64-inlined images (501 MB JSONL) — far
beyond the per-model budget of this workstream. We therefore pin a **stratified
sample** once and every model runs that same list, exactly like the P08 item list.

v2 (current): stratified over ``type × subject`` — the axes the official
``evalaute.py`` actually aggregates on (grade is encoded in ``subject``, e.g.
``math-g9``); 33 near-uniform strata, proportional allocation with a floor of 1.
``difficulty`` is deliberately NOT a stratification axis: the label ships with
the data but is undocumented in the paper, unused by the official eval, and so
skewed (71.7% 难 / only 4 易 in the population) that using it in v1 created 121
strata whose floor=1 pulled the sample ~15pp easier than the population.
Difficulty remains a reporting bucket only.

v1 (superseded, kept for provenance): 300 items over type × subject × difficulty.

Outputs (idempotent, fixed seed; <v> is the --version tag):
  * ``data/k12vista/item_list_<v>.txt``           — pinned hash_ids (committed)
  * ``data/k12vista/item_list_<v>_manifest.json`` — provenance + stratum counts
  * ``sources/datasets/k12vista/K12_Vista/data/sample_<v>.jsonl`` — sampled rows
    minus the base64 ``img`` field (gitignored)
  * ``sources/datasets/k12vista/images/<hash_id>.jpg`` — decoded images

Usage:
    python scripts/eval/data/build_k12vista_sample.py --size 600
"""

from __future__ import annotations

import argparse
import base64
import json
import random
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
SRC_DIR = ROOT / "sources" / "datasets" / "k12vista"
FULL_JSONL = SRC_DIR / "K12_Vista" / "data" / "K12_Vista.jsonl"
IMAGE_DIR = SRC_DIR / "images"
OUT_DIR = ROOT / "data" / "k12vista"

SEED = 20260713


def allocate(pop: dict[tuple[str, ...], int], size: int) -> dict[tuple[str, ...], int]:
    """Proportional allocation with a floor of 1 per non-empty stratum.

    Largest-remainder on the proportional part keeps the total exactly ``size``.
    """
    strata = sorted(pop)
    if size < len(strata):
        raise SystemExit(f"--size {size} is below the number of strata ({len(strata)}); raise it")
    total = sum(pop.values())
    remaining = size - len(strata)
    exact = {s: remaining * pop[s] / total for s in strata}
    alloc = {s: 1 + int(exact[s]) for s in strata}
    leftover = size - sum(alloc.values())
    for s in sorted(strata, key=lambda s: (exact[s] - int(exact[s]), pop[s]), reverse=True)[:leftover]:
        alloc[s] += 1
    # A stratum can never be asked for more items than it holds.
    for s in strata:
        alloc[s] = min(alloc[s], pop[s])
    return alloc


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--size", type=int, default=600, help="sampled item count (default 600)")
    parser.add_argument(
        "--axes",
        default="type,subject",
        help="comma-separated stratification fields (default type,subject — the official eval axes)",
    )
    parser.add_argument("--version", default="v2", help="output version tag (default v2)")
    parser.add_argument("--full-jsonl", type=Path, default=FULL_JSONL)
    args = parser.parse_args()
    axes = [a.strip() for a in args.axes.split(",") if a.strip()]
    sample_jsonl = SRC_DIR / "K12_Vista" / "data" / f"sample_{args.version}.jsonl"

    def stratum(rec: dict[str, Any]) -> tuple[str, ...]:
        return tuple(rec.get(a, "") for a in axes)

    if not args.full_jsonl.exists():
        raise SystemExit(
            f"missing {args.full_jsonl}\n"
            "run: python scripts/eval/data/fetch_eval_datasets.py --benchmark k12vista"
        )

    # Pass 1: population per stratum (ids only — the base64 images stay on disk).
    by_stratum: dict[tuple[str, ...], list[str]] = defaultdict(list)
    pop_marginals: dict[str, Counter] = {f: Counter() for f in ("type", "subject", "difficulty")}
    with args.full_jsonl.open(encoding="utf-8") as fh:
        for line in fh:
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            by_stratum[stratum(rec)].append(rec["hash_id"])
            for field, counter in pop_marginals.items():
                counter[rec.get(field, "")] += 1
    pop = {s: len(ids) for s, ids in by_stratum.items()}
    print(f"population: {sum(pop.values())} items across {len(pop)} strata")

    alloc = allocate(pop, args.size)
    rng = random.Random(SEED)
    keep: set[str] = set()
    for s in sorted(by_stratum):
        keep.update(rng.sample(sorted(by_stratum[s]), alloc[s]))
    print(f"sampled: {len(keep)} items")

    # Pass 2: materialize the sampled rows and decode their images.
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    sample_jsonl.parent.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    kept: list[dict[str, Any]] = []
    with args.full_jsonl.open(encoding="utf-8") as fh:
        for line in fh:
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if rec["hash_id"] not in keep:
                continue
            img = rec.pop("img", "")
            if img:
                (IMAGE_DIR / f"{rec['hash_id']}.jpg").write_bytes(base64.b64decode(img))
            kept.append(rec)

    kept.sort(key=lambda r: r["hash_id"])
    with sample_jsonl.open("w", encoding="utf-8") as fh:
        for rec in kept:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    (OUT_DIR / f"item_list_{args.version}.txt").write_text(
        "".join(f"{r['hash_id']}\n" for r in kept), encoding="utf-8"
    )
    manifest = {
        "version": args.version,
        "date": date.today().isoformat(),
        "source": "https://huggingface.co/datasets/lipku1999/K12-Vista (K12_Vista.jsonl)",
        "code": "https://github.com/lichongod/K12Vista",
        "population": sum(pop.values()),
        "size": len(kept),
        "seed": SEED,
        "stratification": f"{' × '.join(axes)}, proportional with a floor of 1 per stratum",
        "counts": {
            field: dict(sorted(Counter(r[field] for r in kept).items()))
            for field in ("type", "subject", "difficulty")
        },
        "population_counts": {
            field: dict(sorted(pop_marginals[field].items()))
            for field in ("type", "subject", "difficulty")
        },
        "images_dir": str(IMAGE_DIR.relative_to(ROOT)),
        "sample_jsonl": str(sample_jsonl.relative_to(ROOT)),
    }
    (OUT_DIR / f"item_list_{args.version}_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest["counts"], ensure_ascii=False, indent=2))
    print(f"wrote {OUT_DIR / f'item_list_{args.version}.txt'} and {sample_jsonl}")


if __name__ == "__main__":
    main()
