#!/usr/bin/env python3
"""Build the fixed evaluation sample for K12Vista (P04 多模态学科理解与推理).

The full benchmark is 33k items with base64-inlined images (501 MB JSONL) — far
beyond the per-model budget of this workstream. We therefore pin a **stratified
sample** once and every model runs that same list, exactly like the P08 item list.

Stratification is over ``type × subject × difficulty`` (the three axes the
official ``evalaute.py`` reports on), proportional to the population with a floor
of one item per non-empty cell, so no subject or question type drops out.

Outputs (idempotent, fixed seed):
  * ``data/k12vista/item_list_v1.txt``           — pinned hash_ids (committed)
  * ``data/k12vista/item_list_v1_manifest.json`` — provenance + stratum counts
  * ``sources/datasets/k12vista/K12_Vista/data/sample_v1.jsonl`` — sampled rows
    minus the base64 ``img`` field (gitignored)
  * ``sources/datasets/k12vista/images/<hash_id>.jpg`` — decoded images

Usage:
    python scripts/eval/data/build_k12vista_sample.py --size 300
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
SAMPLE_JSONL = SRC_DIR / "K12_Vista" / "data" / "sample_v1.jsonl"
OUT_DIR = ROOT / "data" / "k12vista"

SEED = 20260713


def stratum(rec: dict[str, Any]) -> tuple[str, str, str]:
    return (rec.get("type", ""), rec.get("subject", ""), rec.get("difficulty", ""))


def allocate(pop: dict[tuple[str, str, str], int], size: int) -> dict[tuple[str, str, str], int]:
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
    parser.add_argument("--size", type=int, default=300, help="sampled item count (default 300)")
    parser.add_argument("--full-jsonl", type=Path, default=FULL_JSONL)
    args = parser.parse_args()

    if not args.full_jsonl.exists():
        raise SystemExit(
            f"missing {args.full_jsonl}\n"
            "run: python scripts/eval/data/fetch_eval_datasets.py --benchmark k12vista"
        )

    # Pass 1: population per stratum (ids only — the base64 images stay on disk).
    by_stratum: dict[tuple[str, str, str], list[str]] = defaultdict(list)
    with args.full_jsonl.open(encoding="utf-8") as fh:
        for line in fh:
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            by_stratum[stratum(rec)].append(rec["hash_id"])
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
    SAMPLE_JSONL.parent.mkdir(parents=True, exist_ok=True)
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
    with SAMPLE_JSONL.open("w", encoding="utf-8") as fh:
        for rec in kept:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    (OUT_DIR / "item_list_v1.txt").write_text(
        "".join(f"{r['hash_id']}\n" for r in kept), encoding="utf-8"
    )
    manifest = {
        "version": "v1",
        "date": date.today().isoformat(),
        "source": "https://huggingface.co/datasets/lipku1999/K12-Vista (K12_Vista.jsonl)",
        "code": "https://github.com/lichongod/K12Vista",
        "population": sum(pop.values()),
        "size": len(kept),
        "seed": SEED,
        "stratification": "type × subject × difficulty, proportional with a floor of 1 per stratum",
        "counts": {
            "type": dict(sorted(Counter(r["type"] for r in kept).items())),
            "subject": dict(sorted(Counter(r["subject"] for r in kept).items())),
            "difficulty": dict(sorted(Counter(r["difficulty"] for r in kept).items())),
        },
        "images_dir": str(IMAGE_DIR.relative_to(ROOT)),
        "sample_jsonl": str(SAMPLE_JSONL.relative_to(ROOT)),
    }
    (OUT_DIR / "item_list_v1_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest["counts"], ensure_ascii=False, indent=2))
    print(f"wrote {OUT_DIR/'item_list_v1.txt'} and {SAMPLE_JSONL}")


if __name__ == "__main__":
    main()
