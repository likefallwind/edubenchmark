#!/usr/bin/env python3
"""Materialize HuggingFace parquet datasets into stdlib-readable JSONL (+ images).

The per-benchmark eval adapters under ``scripts/eval/benchmarks/`` read plain
JSONL with the standard library only. The heavy ``pandas``/``pyarrow`` dependency
is isolated to this one-time acquisition step.

Outputs (under ``sources/datasets/``, gitignored):
  - MMLU-Pro:      ``mmlu_pro/test.jsonl``                  (TIGER-Lab/MMLU-Pro)
  - OlympiadBench: ``olympiadbench/data/<OE_config>.jsonl`` + ``olympiadbench/images/*``
                   (Hothan/OlympiadBench, OE open-ended configs only; TP proofs skipped)

Usage:
    python scripts/eval/data/fetch_eval_datasets.py --benchmark mmlu_pro
    python scripts/eval/data/fetch_eval_datasets.py --benchmark olympiadbench
    python scripts/eval/data/fetch_eval_datasets.py --benchmark all
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
HF = "https://huggingface.co/datasets"

MMLU_PRO_URL = f"{HF}/TIGER-Lab/MMLU-Pro/resolve/main/data/test-00000-of-00001.parquet"

OLYMPIAD_REPO = f"{HF}/Hothan/OlympiadBench/resolve/main/OlympiadBench"
# Open-ended configs only (OE_*). Theorem-proving (TP_*) needs human/LLM grading
# and is intentionally excluded from the auto-scored adapter.
OLYMPIAD_OE_CONFIGS = [
    "OE_MM_maths_en_COMP", "OE_MM_maths_zh_CEE", "OE_MM_maths_zh_COMP",
    "OE_MM_physics_en_COMP", "OE_MM_physics_zh_CEE",
    "OE_TO_maths_en_COMP", "OE_TO_maths_zh_CEE", "OE_TO_maths_zh_COMP",
    "OE_TO_physics_en_COMP", "OE_TO_physics_zh_CEE",
]


def _jsonable(value: Any) -> Any:
    """Convert numpy arrays / scalars from pandas into JSON-native types."""
    if value is None:
        return None
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    if hasattr(value, "tolist"):  # numpy array / scalar
        return _jsonable(value.tolist())
    if isinstance(value, float) and pd.isna(value):
        return None
    return value


def fetch_mmlu_pro() -> Path:
    out_dir = ROOT / "sources" / "datasets" / "mmlu_pro"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "test.jsonl"
    print(f"reading {MMLU_PRO_URL}")
    df = pd.read_parquet(MMLU_PRO_URL)
    keep = ["question_id", "question", "options", "answer", "answer_index", "category", "src"]
    with out_path.open("w", encoding="utf-8") as fh:
        for _, row in df.iterrows():
            rec = {k: _jsonable(row[k]) for k in keep}
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"wrote {len(df)} rows -> {out_path}")
    return out_path


def fetch_olympiadbench() -> Path:
    base = ROOT / "sources" / "datasets" / "olympiadbench"
    data_dir = base / "data"
    img_dir = base / "images"
    data_dir.mkdir(parents=True, exist_ok=True)
    img_dir.mkdir(parents=True, exist_ok=True)

    image_cols = [f"image_{i}" for i in range(1, 10)]
    scalar_cols = [
        "id", "question", "final_answer", "context", "modality", "difficulty",
        "is_multiple_answer", "unit", "answer_type", "error", "question_type",
        "subfield", "subject", "language",
    ]

    total = 0
    for config in OLYMPIAD_OE_CONFIGS:
        url = f"{OLYMPIAD_REPO}/{config}/{config}.parquet"
        print(f"reading {url}")
        df = pd.read_parquet(url)
        out_path = data_dir / f"{config}.jsonl"
        with out_path.open("w", encoding="utf-8") as fh:
            for _, row in df.iterrows():
                rec = {col: _jsonable(row[col]) for col in scalar_cols if col in df.columns}
                rec["config"] = config
                image_paths: list[str] = []
                for col in image_cols:
                    cell = row[col] if col in df.columns else None
                    if isinstance(cell, dict) and cell.get("bytes"):
                        orig = cell.get("path") or f"{col}.jpg"
                        ext = Path(str(orig)).suffix or ".jpg"
                        fname = f"{config}_{rec['id']}_{col}{ext}"
                        (img_dir / fname).write_bytes(cell["bytes"])
                        image_paths.append(f"images/{fname}")
                rec["image_paths"] = image_paths
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
        total += len(df)
        print(f"  wrote {len(df)} rows -> {out_path}")
    print(f"OlympiadBench: {total} OE rows across {len(OLYMPIAD_OE_CONFIGS)} configs")
    return data_dir


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--benchmark", required=True, choices=["mmlu_pro", "olympiadbench", "all"])
    args = parser.parse_args()
    if args.benchmark in ("mmlu_pro", "all"):
        fetch_mmlu_pro()
    if args.benchmark in ("olympiadbench", "all"):
        fetch_olympiadbench()


if __name__ == "__main__":
    main()
