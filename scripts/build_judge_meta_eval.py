#!/usr/bin/env python3
"""Build the judge meta-evaluation set ``data/judge_meta_eval_v1/``.

Merges the three human-gold judge-calibration lines into one versioned data
asset with a fixed dev/test split (plan: doc/judge_research_plan_2026-07-06.md
WP1). Sources are read-only; existing eval outputs are never touched.

- mrbench   (MRBench_V2.json)          dimension_label     8 dims x ~1,655 responses
- bea2025   (mrbench_v3_devset.json)   dimension_label     4 dims x ~2,476 responses
- mathtutorbench (pref_test.jsonl)     pairwise_preference 482 expert pairs x 2 orders

Two task_types keep their native label spaces — they are NOT merged. Native
adapter item_ids are preserved (``{source}::{native_id}``) so rows join
directly onto existing ``reports/eval/<benchmark>/<model>/scored.jsonl``.

Leakage control: BEA's dev set shares dialogues with MRBench_V2 (same
``conversation_id``). The split unit is the dialogue; a dialogue shared by
both sources is assigned once and lands in the same split for both.

Outputs (idempotent, deterministic for a fixed seed):

- items.jsonl      one row per judge decision, response text inline,
                   conversation context by reference (contexts.jsonl)
- contexts.jsonl   (source_benchmark, conversation_id) -> context, stored once
- manifest.json    version, seed, per source/split/dimension/label counts
- split_test_item_ids/{mrbench,bea2025,mathtutorbench}.txt
                   native adapter item_ids of the test split (for
                   ``eval_benchmark.py --item-list`` and offline filtering)
- split_dev_subsample_glm/{mrbench,bea2025}.txt
                   stratified dev subsample for estimating glm-5.2 voting
                   weights (WP3; weights must come from dev, never test)
- split_glm_run_item_ids/{mrbench,bea2025}.txt
                   test ∪ dev-subsample: the full set of items glm-5.2 runs,
                   used as the --item-list of the final combined --score-only
                   pass so its summary has stable sampling provenance

Usage:
    python scripts/build_judge_meta_eval.py               # build everything
    python scripts/build_judge_meta_eval.py --validate-only
"""

from __future__ import annotations

import argparse
import json
import random
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "data" / "judge_meta_eval_v1"

MRBENCH_PATH = ROOT / "sources" / "datasets" / "mrbench" / "MRBench_V2.json"
BEA_PATH = ROOT / "sources" / "datasets" / "bea2025" / "mrbench_v3_devset.json"
MTB_PATH = ROOT / "sources" / "datasets" / "mathtutorbench" / "data" / "pref_test.jsonl"

VERSION = "judge_meta_eval_v1"
SEED = 20260706
TEST_FRACTION = 0.25
# Stratified dev subsample sizes for glm-5.2 weight estimation (WP3).
GLM_DEV_SUBSAMPLE = {"mrbench": 1200, "bea2025": 800}

# Label vocabularies mirror the adapters (scripts/eval/benchmarks/{mrbench,bea2025}.py).
MRBENCH_DIMENSIONS: dict[str, tuple[str, ...]] = {
    "Mistake_Identification": ("Yes", "To some extent", "No"),
    "Mistake_Location": ("Yes", "To some extent", "No"),
    "Revealing_of_the_Answer": (
        "No",
        "Yes (and the answer is correct)",
        "Yes (but the answer is incorrect)",
    ),
    "Providing_Guidance": ("Yes", "To some extent", "No"),
    "Actionability": ("Yes", "To some extent", "No"),
    "Coherence": ("Yes", "To some extent", "No"),
    "Tutor_Tone": ("Encouraging", "Neutral", "Offensive"),
    "humanlikeness": ("Yes", "To some extent", "No"),
}
BEA_DIMENSIONS = ("Mistake_Identification", "Mistake_Location", "Providing_Guidance", "Actionability")
BEA_LABELS = ("Yes", "To some extent", "No")


def _sanitize_id(text: Any) -> str:
    """Mirror bea2025._sanitize_id so native item_ids match the adapter."""
    safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", str(text)).strip("_")
    return safe or "unknown"


def _read_json(path: Path) -> Any:
    if not path.exists():
        raise SystemExit(f"missing {path}; run scripts/eval/data/fetch_eval_datasets.py first")
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise SystemExit(f"missing {path}; run scripts/eval/data/fetch_eval_datasets.py first")
    rows = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


# ---------------------------------------------------------------------------
# Load the three sources into a common intermediate form
# ---------------------------------------------------------------------------


def load_mrbench() -> tuple[list[dict[str, Any]], dict[str, str]]:
    items: list[dict[str, Any]] = []
    contexts: dict[str, str] = {}
    for idx, entry in enumerate(_read_json(MRBENCH_PATH)):
        conv = entry.get("conversation_history") or ""
        cid = str(entry.get("conversation_id", idx))
        contexts[cid] = conv
        for model_name, payload in (entry.get("anno_llm_responses") or {}).items():
            response = str((payload or {}).get("response") or "")
            annotation = (payload or {}).get("annotation") or {}
            if not response.strip():
                continue
            for dim, labels in MRBENCH_DIMENSIONS.items():
                gold = annotation.get(dim)
                if gold not in labels:
                    continue
                items.append(
                    {
                        "native_item_id": f"c{idx}-{model_name}-{dim}",
                        "source_benchmark": "mrbench",
                        "task_type": "dimension_label",
                        "conversation_id": cid,
                        "dimension": dim,
                        "response": response,
                        "response_source_model": model_name,
                        "human_label": gold,
                        "language": "en",
                        "lineage": {"source_file": "sources/datasets/mrbench/MRBench_V2.json", "source_row_or_key": idx},
                    }
                )
    return items, contexts


def load_bea2025() -> tuple[list[dict[str, Any]], dict[str, str]]:
    items: list[dict[str, Any]] = []
    contexts: dict[str, str] = {}
    for idx, entry in enumerate(_read_json(BEA_PATH)):
        conv = str(entry.get("conversation_history") or entry.get("conversation history") or "").strip()
        cid = str(entry.get("conversation_id", idx))
        contexts[cid] = conv
        for tutor_id, payload in (entry.get("tutor_responses") or {}).items():
            response = str((payload or {}).get("response") or "").strip()
            annotation = (payload or {}).get("annotation") or {}
            if not response:
                continue
            for dim in BEA_DIMENSIONS:
                gold = annotation.get(dim)
                if gold not in BEA_LABELS:
                    continue
                items.append(
                    {
                        "native_item_id": f"c{idx}-{_sanitize_id(tutor_id)}-{dim}",
                        "source_benchmark": "bea2025",
                        "task_type": "dimension_label",
                        "conversation_id": cid,
                        "dimension": dim,
                        "response": response,
                        "response_source_model": str(tutor_id),
                        "human_label": gold,
                        "language": "en",
                        "lineage": {"source_file": "sources/datasets/bea2025/mrbench_v3_devset.json", "source_row_or_key": idx},
                    }
                )
    return items, contexts


def load_mathtutorbench() -> tuple[list[dict[str, Any]], dict[str, str]]:
    items: list[dict[str, Any]] = []
    contexts: dict[str, str] = {}
    for idx, ex in enumerate(_read_jsonl(MTB_PATH)):
        pos = str(ex.get("teacher_response_positive") or "")
        neg = str(ex.get("teacher_response_negative") or "")
        conv = ex.get("dialog_history") or []
        dialog = "\n".join(
            f"{'Student' if t.get('user') == 'Student' else 'Teacher'}: {t.get('text', '')}" for t in conv
        )
        pair_id = f"cal-{idx}"
        contexts[pair_id] = f"Problem: {ex.get('problem', '')}\n\nDialog so far:\n{dialog}"
        # #ab: A=positive, B=negative ; #ba: A=negative, B=positive (mirrors the adapter)
        for tag, resp_a, resp_b, positive_letter in (("ab", pos, neg, "A"), ("ba", neg, pos, "B")):
            items.append(
                {
                    "native_item_id": f"cal-{idx}#{tag}",
                    "source_benchmark": "mathtutorbench",
                    "task_type": "pairwise_preference",
                    "conversation_id": pair_id,
                    "dimension": None,
                    "response_a": resp_a,
                    "response_b": resp_b,
                    "response_source_model": "expert_pair",
                    "human_label": positive_letter,
                    "language": "en",
                    "lineage": {"source_file": "sources/datasets/mathtutorbench/data/pref_test.jsonl", "source_row_or_key": idx},
                }
            )
    return items, contexts


# ---------------------------------------------------------------------------
# Split assignment (unit = dialogue / preference pair)
# ---------------------------------------------------------------------------


def assign_dialogue_splits(items: list[dict[str, Any]], rng: random.Random) -> dict[str, str]:
    """Assign each dimension-label dialogue to dev/test.

    Greedy proportional fill: dialogues are visited in a seeded random order;
    a dialogue goes to test while the majority of its items still fall under
    the per-source test quotas. A dialogue shared by mrbench and bea2025 is
    assigned exactly once, so it cannot straddle the split boundary.
    """
    per_dialogue: dict[str, Counter] = defaultdict(Counter)
    per_source_total: Counter = Counter()
    for it in items:
        per_dialogue[it["conversation_id"]][it["source_benchmark"]] += 1
        per_source_total[it["source_benchmark"]] += 1
    targets = {src: TEST_FRACTION * n for src, n in per_source_total.items()}

    dialogue_ids = sorted(per_dialogue)
    rng.shuffle(dialogue_ids)
    test_counts: Counter = Counter()
    splits: dict[str, str] = {}
    for cid in dialogue_ids:
        contributions = per_dialogue[cid]
        needed = sum(
            min(count, max(0.0, targets[src] - test_counts[src]))
            for src, count in contributions.items()
        )
        if needed > 0.5 * sum(contributions.values()):
            splits[cid] = "test"
            test_counts.update(contributions)
        else:
            splits[cid] = "dev"
    return splits


def assign_pair_splits(items: list[dict[str, Any]], rng: random.Random) -> dict[str, str]:
    pair_ids = sorted({it["conversation_id"] for it in items})
    rng.shuffle(pair_ids)
    n_test = round(TEST_FRACTION * len(pair_ids))
    test_ids = set(pair_ids[:n_test])
    return {pid: ("test" if pid in test_ids else "dev") for pid in pair_ids}


def stratified_dev_subsample(items: list[dict[str, Any]], size: int, rng: random.Random) -> list[str]:
    """Stratified (dimension x label) subsample of dev items for glm weight
    estimation. Returns native item_ids, sorted for determinism."""
    dev = [it for it in items if it["split"] == "dev"]
    buckets: dict[tuple[str, str], list[str]] = defaultdict(list)
    for it in dev:
        buckets[(str(it["dimension"]), it["human_label"])].append(it["native_item_id"])
    rate = size / len(dev)
    chosen: list[str] = []
    for key in sorted(buckets):
        ids = sorted(buckets[key])
        take = max(1, round(rate * len(ids)))
        chosen.extend(rng.sample(ids, min(take, len(ids))))
    return sorted(chosen)


# ---------------------------------------------------------------------------
# Build + validate
# ---------------------------------------------------------------------------


def build() -> None:
    mr_items, mr_ctx = load_mrbench()
    bea_items, bea_ctx = load_bea2025()
    mtb_items, mtb_ctx = load_mathtutorbench()

    overlap = sorted(set(mr_ctx) & set(bea_ctx))

    rng = random.Random(SEED)
    dialogue_splits = assign_dialogue_splits(mr_items + bea_items, rng)
    pair_splits = assign_pair_splits(mtb_items, rng)

    all_items = []
    for it in mr_items + bea_items:
        it["split"] = dialogue_splits[it["conversation_id"]]
        all_items.append(it)
    for it in mtb_items:
        it["split"] = pair_splits[it["conversation_id"]]
        all_items.append(it)
    for it in all_items:
        it["item_id"] = f"{it['source_benchmark']}::{it['native_item_id']}"
    # Stable order: source, then native id.
    source_order = {"mrbench": 0, "bea2025": 1, "mathtutorbench": 2}
    all_items.sort(key=lambda it: (source_order[it["source_benchmark"]], it["native_item_id"]))

    glm_rng = random.Random(SEED + 1)
    glm_subsamples = {
        src: stratified_dev_subsample(
            [it for it in all_items if it["source_benchmark"] == src], size, glm_rng
        )
        for src, size in GLM_DEV_SUBSAMPLE.items()
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "split_test_item_ids").mkdir(exist_ok=True)
    (OUT_DIR / "split_dev_subsample_glm").mkdir(exist_ok=True)
    (OUT_DIR / "split_glm_run_item_ids").mkdir(exist_ok=True)

    field_order = [
        "item_id", "source_benchmark", "task_type", "native_item_id", "conversation_id",
        "dimension", "response", "response_a", "response_b", "response_source_model",
        "human_label", "language", "split", "lineage",
    ]
    with (OUT_DIR / "items.jsonl").open("w", encoding="utf-8") as fh:
        for it in all_items:
            row = {k: it[k] for k in field_order if k in it}
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")

    with (OUT_DIR / "contexts.jsonl").open("w", encoding="utf-8") as fh:
        for source, contexts in (("mrbench", mr_ctx), ("bea2025", bea_ctx), ("mathtutorbench", mtb_ctx)):
            for cid in sorted(contexts):
                fh.write(
                    json.dumps(
                        {"source_benchmark": source, "conversation_id": cid, "context": contexts[cid]},
                        ensure_ascii=False,
                    )
                    + "\n"
                )

    for src in ("mrbench", "bea2025", "mathtutorbench"):
        ids = [it["native_item_id"] for it in all_items if it["source_benchmark"] == src and it["split"] == "test"]
        (OUT_DIR / "split_test_item_ids" / f"{src}.txt").write_text("\n".join(ids) + "\n", encoding="utf-8")
    for src, ids in glm_subsamples.items():
        (OUT_DIR / "split_dev_subsample_glm" / f"{src}.txt").write_text("\n".join(ids) + "\n", encoding="utf-8")
        test_ids = [
            it["native_item_id"] for it in all_items if it["source_benchmark"] == src and it["split"] == "test"
        ]
        combined = sorted(set(test_ids) | set(ids))
        (OUT_DIR / "split_glm_run_item_ids" / f"{src}.txt").write_text("\n".join(combined) + "\n", encoding="utf-8")

    counts: dict[str, Any] = {}
    for src in ("mrbench", "bea2025", "mathtutorbench"):
        src_items = [it for it in all_items if it["source_benchmark"] == src]
        by_split = Counter(it["split"] for it in src_items)
        dim_label: dict[str, Any] = {}
        for split in ("dev", "test"):
            dist = Counter((str(it["dimension"]), it["human_label"]) for it in src_items if it["split"] == split)
            dim_label[split] = {f"{d}|{l}": c for (d, l), c in sorted(dist.items())}
        counts[src] = {
            "total": len(src_items),
            "dev": by_split.get("dev", 0),
            "test": by_split.get("test", 0),
            "dimension_label_distribution": dim_label,
        }

    manifest = {
        "version": VERSION,
        "seed": SEED,
        "test_fraction": TEST_FRACTION,
        "total_items": len(all_items),
        "split_unit": "conversation_id (dialogue) for dimension_label; pair for pairwise_preference",
        "native_id_rule": (
            "mrbench: c{row_idx}-{model}-{dim} over MRBench_V2.json row order; "
            "bea2025: c{row_idx}-{sanitized_tutor_id}-{dim} over mrbench_v3_devset.json row order; "
            "mathtutorbench: cal-{row_idx}#{ab|ba} over pref_test.jsonl row order. "
            "item_id = {source_benchmark}::{native_item_id} joins onto "
            "reports/eval/<benchmark>/<model>/scored.jsonl"
        ),
        "leakage_control": {
            "overlapping_dialogues_mrbench_bea2025": len(overlap),
            "rule": "a dialogue shared by both sources is assigned to one split for both",
        },
        "glm_dev_subsample": {
            src: {"size": len(ids), "purpose": "estimate glm-5.2 per-dimension dev kappa for weighted voting (WP3)"}
            for src, ids in glm_subsamples.items()
        },
        "counts": counts,
    }
    (OUT_DIR / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print(f"wrote {len(all_items)} items to {OUT_DIR / 'items.jsonl'}")
    for src, info in counts.items():
        print(f"  {src}: total={info['total']} dev={info['dev']} test={info['test']}")
    print(f"  overlapping dialogues (mrbench ∩ bea2025): {len(overlap)}")


def validate() -> None:
    items_path = OUT_DIR / "items.jsonl"
    if not items_path.exists():
        raise SystemExit(f"missing {items_path}; run without --validate-only first")
    items = _read_jsonl(items_path)
    manifest = _read_json(OUT_DIR / "manifest.json")

    errors: list[str] = []
    if len(items) != manifest.get("total_items"):
        errors.append(f"items.jsonl has {len(items)} rows, manifest says {manifest.get('total_items')}")

    # No dialogue may straddle the split boundary — including across sources
    # for the 182 dialogues shared by mrbench and bea2025.
    split_by_dialogue: dict[tuple[str, str], set[str]] = defaultdict(set)
    cross_source: dict[str, set[str]] = defaultdict(set)
    for it in items:
        split_by_dialogue[(it["source_benchmark"], it["conversation_id"])].add(it["split"])
        if it["source_benchmark"] in ("mrbench", "bea2025"):
            cross_source[it["conversation_id"]].add(it["split"])
    bad = [k for k, v in split_by_dialogue.items() if len(v) > 1]
    if bad:
        errors.append(f"{len(bad)} dialogues straddle dev/test within a source, e.g. {bad[:3]}")
    bad = [cid for cid, v in cross_source.items() if len(v) > 1]
    if bad:
        errors.append(f"{len(bad)} shared dialogues straddle dev/test across sources, e.g. {bad[:3]}")

    # Preference pairs keep both orders in the same split.
    by_pair: dict[str, set[str]] = defaultdict(set)
    for it in items:
        if it["task_type"] == "pairwise_preference":
            by_pair[it["conversation_id"]].add(it["split"])
    bad = [pid for pid, v in by_pair.items() if len(v) > 1]
    if bad:
        errors.append(f"{len(bad)} preference pairs straddle dev/test, e.g. {bad[:3]}")

    # Test id lists match items.jsonl.
    for src in ("mrbench", "bea2025", "mathtutorbench"):
        listed = set((OUT_DIR / "split_test_item_ids" / f"{src}.txt").read_text(encoding="utf-8").split())
        actual = {it["native_item_id"] for it in items if it["source_benchmark"] == src and it["split"] == "test"}
        if listed != actual:
            errors.append(f"split_test_item_ids/{src}.txt out of sync ({len(listed)} listed vs {len(actual)} actual)")

    # glm dev subsamples must be dev-only.
    dev_ids = {
        src: {it["native_item_id"] for it in items if it["source_benchmark"] == src and it["split"] == "dev"}
        for src in ("mrbench", "bea2025")
    }
    for src in ("mrbench", "bea2025"):
        listed = set((OUT_DIR / "split_dev_subsample_glm" / f"{src}.txt").read_text(encoding="utf-8").split())
        leaked = listed - dev_ids[src]
        if leaked:
            errors.append(f"split_dev_subsample_glm/{src}.txt contains {len(leaked)} non-dev ids")

    if errors:
        for err in errors:
            print(f"FAIL: {err}")
        raise SystemExit(1)
    per_source = Counter((it["source_benchmark"], it["split"]) for it in items)
    print(f"validate OK: {len(items)} items")
    for (src, split), n in sorted(per_source.items()):
        print(f"  {src}/{split}: {n}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--validate-only", action="store_true", help="check existing outputs, no rewrite")
    args = parser.parse_args()
    if args.validate_only:
        validate()
    else:
        build()
        validate()


if __name__ == "__main__":
    main()
