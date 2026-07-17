#!/usr/bin/env python3
"""Download the pinned SAS-Bench release into sources/datasets/sas_bench.

The upstream code checkout may already exist at that path.  This script only
materializes the Hugging Face data files under its ``datasets/`` child and
writes a reproducibility manifest.  Downloaded benchmark data stays uncommitted.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TARGET = ROOT / "sources" / "datasets" / "sas_bench"
DATA_DIR = TARGET / "datasets"
REPOSITORY = "aleversn/SAS-Bench"
REVISION = "89e572cff503f4beee01f0a6f6a78ccde0a32bdb"
BASE_URL = f"https://huggingface.co/datasets/{REPOSITORY}/resolve/{REVISION}/datasets"
FILES = [
    "0_Physics_ShortAns.jsonl",
    "1_History_ShortAns.jsonl",
    "2_Physics_Choice.jsonl",
    "3_Geography_ShortAns.jsonl",
    "4_Biology_gapfilling.jsonl",
    "5_Chinese_gapfilling.jsonl",
    "6_Chinese_ShortAns.jsonl",
    "7_Math_ShortAns.jsonl",
    "8_Political_ShortAns.jsonl",
    "9_English_gapfilling.jsonl",
    "10_Math_gapfilling.jsonl",
    "11_Chemistry_gapfilling.jsonl",
    "ID_DICT.json",
    "dataset_info.json",
    "error_type.jsonl",
]


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _jsonl_rows(path: Path) -> int | None:
    if path.suffix != ".jsonl" or path.name == "error_type.jsonl":
        return None
    with path.open("rb") as handle:
        return sum(1 for line in handle if line.strip())


def main() -> None:
    TARGET.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="sas_bench_", dir=TARGET) as tmp:
        staging = Path(tmp)
        for name in FILES:
            destination = staging / name
            url = f"{BASE_URL}/{name}?download=true"
            print(f"download {name}", flush=True)
            with urllib.request.urlopen(url, timeout=120) as response, destination.open("wb") as output:
                shutil.copyfileobj(response, output)
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        for name in FILES:
            (staging / name).replace(DATA_DIR / name)

    entries = []
    for name in FILES:
        path = DATA_DIR / name
        entries.append(
            {
                "path": f"datasets/{name}",
                "bytes": path.stat().st_size,
                "sha256": _sha256(path),
                "rows": _jsonl_rows(path),
            }
        )
    total_rows = sum(entry["rows"] or 0 for entry in entries)
    if total_rows != 4109:
        raise RuntimeError(f"expected 4109 SAS-Bench responses, found {total_rows}")
    manifest = {
        "benchmark": "sas_bench",
        "source": f"https://huggingface.co/datasets/{REPOSITORY}",
        "revision": REVISION,
        "prepared_at": datetime.now(timezone.utc).isoformat(),
        "license": "Apache-2.0; upstream dataset card additionally limits data use to research",
        "total_response_rows": total_rows,
        "files": entries,
    }
    (TARGET / "data_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"prepared {total_rows} rows in {DATA_DIR}")


if __name__ == "__main__":
    main()
