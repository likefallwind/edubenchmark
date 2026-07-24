#!/usr/bin/env python3
"""Materialize HuggingFace parquet datasets into stdlib-readable JSONL (+ images).

The per-benchmark eval adapters under ``scripts/eval/benchmarks/`` read plain
JSONL with the standard library only. The heavy ``pandas``/``pyarrow`` dependency
is isolated to this one-time acquisition step.

Outputs (under ``sources/datasets/``, gitignored):
  - MMLU-Pro:      ``mmlu_pro/test.jsonl``                  (TIGER-Lab/MMLU-Pro)
  - OlympiadBench: ``olympiadbench/data/<OE_config>.jsonl`` + ``olympiadbench/images/*``
                   (Hothan/OlympiadBench, OE open-ended configs only; TP proofs skipped)
  - EduGuardBench: ``eduguard_bench/data/{satas,adversarial}.jsonl``
                   (converted from the local repo clone's Dataset/*.xlsx; no download)
  - BEA 2025:      ``bea2025/mrbench_v3_{devset,testset}.json``
                   (BEA shared task dev has 4-dimension human annotations; test is unlabeled)
  - MMTutorBench:  ``mmtutorbench/mmtutorbench.jsonl`` + ``mmtutorbench/keyframes/*``
                   (Tangchiu/mmtutorbench, JSONL with repo-relative image paths)
  - EduBench:      ``edubench/`` official repository clone + acquisition manifest
                   (the harness uses the existing comparable 3,797-prompt export)

Usage:
    python scripts/eval/data/fetch_eval_datasets.py --benchmark mmlu_pro
    python scripts/eval/data/fetch_eval_datasets.py --benchmark olympiadbench
    python scripts/eval/data/fetch_eval_datasets.py --benchmark eduguard_bench
    python scripts/eval/data/fetch_eval_datasets.py --benchmark bea2025
    python scripts/eval/data/fetch_eval_datasets.py --benchmark mmtutorbench
    python scripts/eval/data/fetch_eval_datasets.py --benchmark edubench
    python scripts/eval/data/fetch_eval_datasets.py --benchmark all
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any
from urllib.parse import quote

try:
    import pandas as pd
except ImportError:  # MMTutorBench / MRBench fetches do not need pandas.
    pd = None


ROOT = Path(__file__).resolve().parents[3]

import sys

sys.path.insert(0, str(ROOT / "scripts"))
from eval.predictions_io import predictions_exist, read_predictions  # noqa: E402

HF = "https://huggingface.co/datasets"

MMLU_PRO_URL = f"{HF}/TIGER-Lab/MMLU-Pro/resolve/main/data/test-00000-of-00001.parquet"
MMTUTORBENCH_REPO = f"{HF}/Tangchiu/mmtutorbench/resolve/main"
MMTUTORBENCH_JSONL_URL = f"{MMTUTORBENCH_REPO}/mmtutorbench.jsonl"
EDUBENCH_REPO = "https://github.com/ybai-nlp/EduBench.git"
BEA2025_REPO = "https://raw.githubusercontent.com/kaushal0494/UnifyingAITutorEvaluation/main/BEA_Shared_Task_2025_Datasets"
BEA2025_DEV_URL = f"{BEA2025_REPO}/mrbench_v3_devset.json"
BEA2025_TEST_URL = f"{BEA2025_REPO}/mrbench_v3_testset.json"
BEA2025_DIMENSIONS = [
    "Mistake_Identification",
    "Mistake_Location",
    "Providing_Guidance",
    "Actionability",
]

UMWP_URL = "https://raw.githubusercontent.com/Yuki-Asuuna/UMWP/main/data/StandardDataset.jsonl"

MOOCCUBE_URL = "http://lfs.aminer.cn/misc/moocdata/data/MOOCCube.zip"

IFEVAL_BASE = (
    "https://raw.githubusercontent.com/google-research/google-research/master/"
    "instruction_following_eval/"
)

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
    if isinstance(value, float) and pd is not None and pd.isna(value):
        return None
    return value


def _require_pandas() -> Any:
    if pd is None:
        raise SystemExit(
            "pandas is required for this dataset fetcher (parquet/xlsx input). "
            "Install pandas/pyarrow, or run a JSON-only fetcher such as --benchmark mmtutorbench."
        )
    return pd


def fetch_mmlu_pro(force: bool = False) -> Path:
    out_dir = ROOT / "sources" / "datasets" / "mmlu_pro"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "test.jsonl"
    if out_path.exists() and out_path.stat().st_size > 0 and not force:
        print(f"skip mmlu_pro: {out_path} already exists (use --force to re-download)")
        return out_path
    print(f"reading {MMLU_PRO_URL}")
    df = pd.read_parquet(MMLU_PRO_URL)
    keep = ["question_id", "question", "options", "answer", "answer_index", "category", "src"]
    with out_path.open("w", encoding="utf-8") as fh:
        for _, row in df.iterrows():
            rec = {k: _jsonable(row[k]) for k in keep}
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"wrote {len(df)} rows -> {out_path}")
    return out_path


def _download_file(url: str, out_path: Path, force: bool = False) -> bool:
    """Download ``url`` to ``out_path`` atomically. Returns True if written."""
    import urllib.request

    if _ok(out_path) and not force:
        return False
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = out_path.with_suffix(out_path.suffix + ".tmp")
    with urllib.request.urlopen(url) as resp:  # noqa: S310 - trusted public benchmark source
        tmp.write_bytes(resp.read())
    tmp.replace(out_path)
    return True


def _read_jsonl_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _mmtutorbench_manifest(rows: list[dict[str, Any]], base: Path) -> dict[str, Any]:
    image_refs: set[str] = set()
    image_attachment_count = 0
    rubric_fields: set[str] = set()
    criterion_ids: set[str] = set()
    human_score_fields: set[str] = set()
    for row in rows:
        if row.get("img"):
            image_refs.add(str(row["img"]))
            image_attachment_count += 1
        for rel in row.get("prev_img") or []:
            if rel:
                image_refs.add(str(rel))
                image_attachment_count += 1
        rubric = row.get("rubric") or {}
        rubric_fields.update(str(k) for k in rubric)
        for criterion in rubric.get("evaluation_criteria") or []:
            cid = criterion.get("id")
            if cid:
                criterion_ids.add(str(cid))
        for key in row:
            low = str(key).lower()
            if any(marker in low for marker in ("human", "expert", "annotation", "gold_score", "gold_scores")):
                human_score_fields.add(str(key))

    existing = sum(1 for rel in image_refs if (base / rel).is_file())
    return {
        "source": "Tangchiu/mmtutorbench",
        "jsonl_url": MMTUTORBENCH_JSONL_URL,
        "sample_count": len(rows),
        "image_attachment_count": image_attachment_count,
        "unique_image_ref_count": len(image_refs),
        "downloaded_image_count": existing,
        "missing_image_count": len(image_refs) - existing,
        "rubric_fields": sorted(rubric_fields),
        "rubric_criterion_ids": sorted(criterion_ids),
        "human_score_fields": sorted(human_score_fields),
        "has_public_human_gold": bool(human_score_fields),
        "notes": (
            "Public JSONL has per-instance rubrics and reference answers. "
            "No per-item human/expert score fields were found when has_public_human_gold=false."
        ),
    }


def fetch_mmtutorbench(force: bool = False) -> Path:
    """Download MMTutorBench JSONL and referenced keyframe images."""
    from concurrent.futures import ThreadPoolExecutor, as_completed

    base = ROOT / "sources" / "datasets" / "mmtutorbench"
    jsonl_path = base / "mmtutorbench.jsonl"
    manifest_path = base / "data_manifest.json"
    base.mkdir(parents=True, exist_ok=True)

    if _download_file(MMTUTORBENCH_JSONL_URL, jsonl_path, force=force):
        print(f"wrote JSONL -> {jsonl_path}")
    else:
        print(f"skip mmtutorbench JSONL: {jsonl_path} already exists (use --force to re-download)")

    rows = _read_jsonl_rows(jsonl_path)
    image_refs = sorted(
        {
            str(rel)
            for row in rows
            for rel in ([row.get("img")] + list(row.get("prev_img") or []))
            if rel
        }
    )
    pending = [rel for rel in image_refs if force or not _ok(base / rel)]
    if pending:
        print(f"downloading {len(pending)} / {len(image_refs)} MMTutorBench images")

        def fetch_one(rel: str) -> tuple[str, str | None]:
            url = f"{MMTUTORBENCH_REPO}/{quote(rel)}"
            try:
                _download_file(url, base / rel, force=True)
                return rel, None
            except Exception as exc:  # noqa: BLE001 - report all failed image paths together
                return rel, str(exc)

        failures: list[tuple[str, str]] = []
        with ThreadPoolExecutor(max_workers=8) as pool:
            futures = [pool.submit(fetch_one, rel) for rel in pending]
            for idx, fut in enumerate(as_completed(futures), start=1):
                rel, error = fut.result()
                if error:
                    failures.append((rel, error))
                if idx % 100 == 0 or idx == len(pending):
                    print(f"  images {idx}/{len(pending)}")
        if failures:
            for rel, error in failures[:10]:
                print(f"  missing {rel}: {error}")
            raise SystemExit(f"failed to download {len(failures)} MMTutorBench images")
    else:
        print(f"skip mmtutorbench images: all {len(image_refs)} referenced images already exist")

    manifest = _mmtutorbench_manifest(rows, base)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote manifest -> {manifest_path}")
    return base


def fetch_edubench(force: bool = False) -> Path:
    """Acquire the official EduBench repository and record harness provenance.

    The upstream checkout is kept intact under sources/datasets.  The runnable
    adapter intentionally uses the repository's imported 3,797-prompt export so
    new models remain comparable with the existing 11 runs; the manifest makes
    that distinction explicit instead of presenting it as the official 198-row
    human-evaluation sample.
    """
    out_dir = ROOT / "sources" / "datasets" / "edubench"
    if not (out_dir / ".git").is_dir():
        out_dir.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            ["git", "clone", "--depth", "1", EDUBENCH_REPO, str(out_dir)],
            check=True,
        )
    elif force:
        subprocess.run(["git", "-C", str(out_dir), "pull", "--ff-only"], check=True)
    else:
        print(f"skip edubench clone: {out_dir} already exists (use --force to fast-forward)")

    required = [out_dir / "LICENSE", out_dir / "README.md", out_dir / "data" / "all_data" / "sampled_data"]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise SystemExit("incomplete EduBench checkout:\n" + "\n".join(missing))

    commit = subprocess.run(
        ["git", "-C", str(out_dir), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()

    def line_count(path: Path) -> int:
        with path.open(encoding="utf-8", errors="replace") as handle:
            return sum(1 for line in handle if line.strip())

    sampled_dir = out_dir / "data" / "all_data" / "sampled_data"
    full_root = out_dir / "data" / "all_data"
    prompt_source = ROOT / "reports" / "eval" / "edubench" / "minimax-m3" / "predictions.jsonl"
    manifest = {
        "benchmark": "edubench",
        "source_repo": EDUBENCH_REPO.removesuffix(".git"),
        "source_commit": commit,
        "license": "MIT",
        "official_human_evaluation_sample": {
            "english_rows": line_count(sampled_dir / "en_data_sampled.jsonl"),
            "chinese_rows": line_count(sampled_dir / "zh_data_sampled.jsonl"),
        },
        "official_full_release_rows": {
            "english": sum(line_count(path) for path in (full_root / "en_data").glob("*.jsonl")),
            "chinese": sum(line_count(path) for path in (full_root / "zh_data").glob("*.jsonl")),
        },
        "upstream_data_caveats": [
            "The released zh_data/ES.py is generation code, not a Chinese Emotional Support JSONL dataset.",
            "The official paper's human/model comparison uses the 198-row sampled_data test set.",
        ],
        "harness_prompt_set": {
            "path": str(prompt_source.relative_to(ROOT)),
            "rows": len(read_predictions(prompt_source)) if predictions_exist(prompt_source) else 0,
            "note": (
                "Comparable English prompt export from the colleague run; five scenarios and stable IDs. "
                "It is not claimed to be the official 198-row human-evaluation sample."
            ),
        },
    }
    manifest_path = out_dir / "data_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote EduBench manifest -> {manifest_path}")
    return out_dir


def _bea2025_counts(path: Path, has_annotations: bool) -> dict[str, Any]:
    with path.open(encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, list):
        raise SystemExit(f"unexpected BEA 2025 payload: {path} is not a JSON list")

    response_count = 0
    annotation_dims: set[str] = set()
    label_counts: dict[str, dict[str, int]] = {dim: {} for dim in BEA2025_DIMENSIONS}
    for entry in data:
        for payload in (entry.get("tutor_responses") or {}).values():
            response_count += 1
            if has_annotations:
                annotation = (payload or {}).get("annotation") or {}
                for dim in BEA2025_DIMENSIONS:
                    label = annotation.get(dim)
                    if label is not None:
                        annotation_dims.add(dim)
                        label_counts[dim][str(label)] = label_counts[dim].get(str(label), 0) + 1
    return {
        "dialogue_count": len(data),
        "tutor_response_count": response_count,
        "annotation_dimensions": sorted(annotation_dims),
        "label_counts": label_counts if has_annotations else {},
    }


def fetch_bea2025(force: bool = False) -> Path:
    """Download BEA 2025 shared-task dev/test JSON files and write a manifest."""
    out_dir = ROOT / "sources" / "datasets" / "bea2025"
    dev_path = out_dir / "mrbench_v3_devset.json"
    test_path = out_dir / "mrbench_v3_testset.json"
    manifest_path = out_dir / "data_manifest.json"
    out_dir.mkdir(parents=True, exist_ok=True)

    for url, path in ((BEA2025_DEV_URL, dev_path), (BEA2025_TEST_URL, test_path)):
        if _download_file(url, path, force=force):
            print(f"wrote {path.name} -> {path}")
        else:
            print(f"skip {path.name}: {path} already exists (use --force to re-download)")

    dev_counts = _bea2025_counts(dev_path, has_annotations=True)
    test_counts = _bea2025_counts(test_path, has_annotations=False)
    manifest = {
        "benchmark": "bea2025",
        "title": "BEA 2025 Shared Task: Pedagogical Ability Assessment of AI-powered Tutors",
        "task_page": "https://sig-edu.org/sharedtask/2025",
        "source_repo": "https://github.com/kaushal0494/UnifyingAITutorEvaluation/tree/main/BEA_Shared_Task_2025_Datasets",
        "source_urls": {
            "dev": BEA2025_DEV_URL,
            "test": BEA2025_TEST_URL,
        },
        "files": {
            "dev": str(dev_path.relative_to(ROOT)),
            "test": str(test_path.relative_to(ROOT)),
        },
        "dev": dev_counts,
        "test": {
            **test_counts,
            "annotation_dimensions": [],
            "labels_available_locally": False,
        },
        "available_annotation_dimensions": BEA2025_DIMENSIONS,
        "label_space": ["Yes", "To some extent", "No"],
        "local_scoring_note": (
            "Use the dev set for local scored judge calibration. The public test set "
            "does not include tutor identities or annotation labels; official scoring "
            "requires the BEA/CodaBench evaluation path or released labels."
        ),
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        "wrote BEA 2025 manifest "
        f"(dev={dev_counts['dialogue_count']} dialogues/{dev_counts['tutor_response_count']} responses, "
        f"test={test_counts['dialogue_count']} dialogues/{test_counts['tutor_response_count']} responses) "
        f"-> {manifest_path}"
    )
    return out_dir


def fetch_olympiadbench(force: bool = False) -> Path:
    base = ROOT / "sources" / "datasets" / "olympiadbench"
    data_dir = base / "data"
    img_dir = base / "images"
    data_dir.mkdir(parents=True, exist_ok=True)
    img_dir.mkdir(parents=True, exist_ok=True)

    have = {p.stem for p in data_dir.glob("OE_*.jsonl")}
    if not force and all(cfg in have for cfg in OLYMPIAD_OE_CONFIGS):
        print(f"skip olympiadbench: {len(have)} OE configs already in {data_dir} (use --force to re-download)")
        return data_dir

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


def _eduguard_sata_answer_key(base: Path) -> dict[str, str]:
    """Rebuild the SATA gold-answer key from the official Results files.

    ``Dataset/SATAs.xlsx`` ships with its Answer column misaligned: it follows
    the row order of the ``Results/SATAs/*.xlsx`` files while the ID/question
    rows are ordered differently, so ~half the answers sit on the wrong
    question. The per-model result files carry a self-consistent ID->Answer
    key (it reproduces the paper's metrics), so take a majority vote across
    them per ID.
    """
    from collections import Counter, defaultdict

    votes: dict[str, Counter] = defaultdict(Counter)
    for path in sorted((base / "Results" / "SATAs").glob("*.xlsx")):
        if path.name.startswith("~$"):
            continue
        df = pd.read_excel(path)
        if "ID" not in df.columns or "Answer" not in df.columns:
            continue
        for qid, ans in zip(df["ID"].astype(str), df["Answer"]):
            normalized = ",".join(sorted(a.strip().upper() for a in str(ans).split(",") if a.strip()))
            if normalized:
                votes[qid.strip()][normalized] += 1
    return {qid: counter.most_common(1)[0][0] for qid, counter in votes.items()}


def fetch_eduguard_bench(force: bool = False) -> Path:
    """Convert the local EduGuardBench repo clone's xlsx datasets to JSONL.

    No network access: expects ``sources/datasets/eduguard_bench/`` from
    ``git clone https://github.com/YL1N/EduGuardBench``.
    """
    base = ROOT / "sources" / "datasets" / "eduguard_bench"
    out_dir = base / "data"
    satas_out = out_dir / "satas.jsonl"
    adv_out = out_dir / "adversarial.jsonl"
    if not force and satas_out.exists() and adv_out.exists():
        print(f"skip eduguard_bench: outputs already in {out_dir} (use --force to rebuild)")
        return out_dir

    satas_xlsx = base / "Dataset" / "SATAs.xlsx"
    adv_xlsx = base / "Dataset" / "adversarial_prompts.xlsx"
    for path in (satas_xlsx, adv_xlsx):
        if not path.exists():
            raise SystemExit(f"missing {path}; clone https://github.com/YL1N/EduGuardBench into sources/datasets/eduguard_bench first")
    out_dir.mkdir(parents=True, exist_ok=True)

    answer_key = _eduguard_sata_answer_key(base)
    df = pd.read_excel(satas_xlsx)
    fixed = 0
    with satas_out.open("w", encoding="utf-8") as fh:
        for _, row in df.iterrows():
            qid = str(row["ID"]).strip()
            dataset_answer = str(row["Answer"]).strip()
            answer = answer_key.get(qid, dataset_answer)
            if ",".join(sorted(a.strip().upper() for a in dataset_answer.split(",") if a.strip())) != answer:
                fixed += 1
            rec = {
                "id": qid,
                "question_zh": str(row["Question_Chinese"]).strip(),
                "question_en": str(row["Question_English"]).strip(),
                "answer": answer,
            }
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"wrote {len(df)} rows -> {satas_out} (answer key from Results majority vote; {fixed} misaligned dataset answers corrected)")

    df = pd.read_excel(adv_xlsx)
    with adv_out.open("w", encoding="utf-8") as fh:
        for _, row in df.iterrows():
            rec = {
                "id": str(row["ID"]).strip(),
                "teacher_prompt": str(row["Teacher_Prompt_EN"]).strip(),
                "student_statement": str(row["Student_Statement_EN"]).strip(),
            }
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"wrote {len(df)} rows -> {adv_out}")
    return out_dir


def _ok(path: Path) -> bool:
    return path.exists() and path.stat().st_size > 0


MRBENCH_URL = (
    "https://raw.githubusercontent.com/kaushal0494/UnifyingAITutorEvaluation/"
    "main/MRBench/MRBench_V2.json"
)


def fetch_mrbench(force: bool = False) -> Path:
    """Download the MRBench annotated dataset (single public JSON, no pandas).

    MRBench (NAACL 2025, *Unifying AI Tutor Evaluation*) ships one JSON list in
    the repo: each entry is a tutor-student conversation plus several models'
    tutor responses, each response annotated by humans on 8 pedagogical
    dimensions. The eval adapters (``mrbench_judge`` / ``mrbench_tutor``) read
    this file directly with the standard library.
    """
    import json as _json
    import urllib.request

    out_dir = ROOT / "sources" / "datasets" / "mrbench"
    out_path = out_dir / "MRBench_V2.json"
    if _ok(out_path) and not force:
        print(f"skip mrbench: {out_path} already exists (use --force to re-download)")
        return out_path
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"downloading {MRBENCH_URL}")
    with urllib.request.urlopen(MRBENCH_URL) as resp:  # noqa: S310 - trusted raw.githubusercontent.com
        raw = resp.read()
    # Validate it parses and is the expected list-of-entries shape before writing.
    data = _json.loads(raw)
    if not isinstance(data, list) or not data:
        raise SystemExit(f"unexpected MRBench payload: expected a non-empty JSON list, got {type(data).__name__}")
    out_path.write_bytes(raw)
    print(f"wrote {len(data)} conversations -> {out_path}")
    return out_path


def fetch_umwp(force: bool = False) -> Path:
    """Download UMWP (Unanswerable Math Word Problems, LREC 2024, CC-BY-SA-4.0).

    A single public JSONL of 5,200 rows: 2,600 answerable + 2,600 human-crafted
    unanswerable twins (five ``category`` types 1-5: key-info-missing /
    key-info-ambiguous / unrealistic-condition / irrelevant-object /
    question-missing). Used by the ``p08_abstention`` adapter to test whether a
    model declines the unanswerable ones without over-declining the answerable
    controls. No pandas — the adapter reads this file with the standard library.
    """
    import json as _json
    import urllib.request

    out_dir = ROOT / "sources" / "datasets" / "umwp"
    out_path = out_dir / "StandardDataset.jsonl"
    if _ok(out_path) and not force:
        print(f"skip umwp: {out_path} already exists (use --force to re-download)")
        return out_path
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"downloading {UMWP_URL}")
    req = urllib.request.Request(UMWP_URL, headers={"User-Agent": "curl/8"})
    with urllib.request.urlopen(req) as resp:  # noqa: S310 - trusted raw.githubusercontent.com
        raw = resp.read()
    rows = [_json.loads(line) for line in raw.decode("utf-8").splitlines() if line.strip()]
    if not rows or "answerable" not in rows[0]:
        raise SystemExit(f"unexpected UMWP payload: {len(rows)} rows, keys={sorted(rows[0]) if rows else '[]'}")
    out_path.write_bytes(raw)
    n_unans = sum(1 for r in rows if not r.get("answerable"))
    manifest = {
        "source": "github.com/Yuki-Asuuna/UMWP",
        "url": UMWP_URL,
        "license": "CC-BY-SA-4.0",
        "citation": "Sun et al., LREC-COLING 2024, Benchmarking Hallucination in LLMs on Unanswerable Math Word Problems",
        "total_rows": len(rows),
        "answerable": len(rows) - n_unans,
        "unanswerable": n_unans,
        "unanswerable_categories": {
            "1": "key information missing", "2": "key information ambiguous",
            "3": "unrealistic condition", "4": "irrelevant object", "5": "question missing",
        },
    }
    (out_dir / "data_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"wrote {len(rows)} rows ({len(rows) - n_unans} answerable / {n_unans} unanswerable) -> {out_path}")
    return out_path


def fetch_ifeval(force: bool = False) -> Path:
    """Download IFEval (Zhou et al. 2023, google-research; Apache-2.0).

    541 prompts with verifiable instructions (``instruction_id_list`` +
    ``kwargs``), rule-scored — no judge, no extraction LLM. Downloads both the
    data (``input_data.jsonl``) and the official checker modules
    (``instructions*.py``, vendored under ``instruction_following_eval/`` so
    the adapter can import them unmodified; deps: nltk / langdetect /
    immutabledict / absl-py, present in the miniconda interpreter). Also
    fetches the nltk ``punkt`` sentence tokenizer the checker needs.
    """
    import json as _json
    import urllib.request

    out_dir = ROOT / "sources" / "datasets" / "ifeval"
    data_path = out_dir / "data" / "input_data.jsonl"
    pkg_dir = out_dir / "instruction_following_eval"
    code_files = [
        "instructions.py",
        "instructions_registry.py",
        "instructions_util.py",
        "evaluation_lib.py",
    ]
    if _ok(data_path) and all(_ok(pkg_dir / f) for f in code_files) and not force:
        print(f"skip ifeval: {data_path} already exists (use --force to re-download)")
        return out_dir
    (out_dir / "data").mkdir(parents=True, exist_ok=True)
    pkg_dir.mkdir(parents=True, exist_ok=True)

    def _get(rel: str, dest: Path) -> bytes:
        url = IFEVAL_BASE + rel
        print(f"downloading {url}")
        req = urllib.request.Request(url, headers={"User-Agent": "curl/8"})
        with urllib.request.urlopen(req) as resp:  # noqa: S310 - trusted raw.githubusercontent.com
            raw = resp.read()
        dest.write_bytes(raw)
        return raw

    raw = _get("data/input_data.jsonl", data_path)
    rows = [_json.loads(line) for line in raw.decode("utf-8").splitlines() if line.strip()]
    if not rows or "instruction_id_list" not in rows[0]:
        raise SystemExit(
            f"unexpected IFEval payload: {len(rows)} rows, keys={sorted(rows[0]) if rows else '[]'}"
        )
    for f in code_files:
        _get(f, pkg_dir / f)
    (pkg_dir / "__init__.py").write_text("", encoding="utf-8")

    try:
        import nltk

        nltk.download("punkt", quiet=True)
        nltk.download("punkt_tab", quiet=True)
    except ImportError:
        print("WARNING: nltk not importable in this interpreter; the checker needs it at score time")

    manifest = {
        "source": "github.com/google-research/google-research/tree/master/instruction_following_eval",
        "license": "Apache-2.0",
        "citation": "Zhou et al. 2023, Instruction-Following Evaluation for Large Language Models (arXiv:2311.07911)",
        "total_rows": len(rows),
        "scoring": "official strict + loose rule checks; vendored official modules, no LLM judge",
        "code_files": code_files,
    }
    (out_dir / "data_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"wrote {len(rows)} rows -> {data_path}; official checker -> {pkg_dir}")
    return out_dir


def fetch_k12vista(force: bool = False) -> Path:
    """Download K12Vista (Li et al. 2025, arXiv:2506.01676) — Chinese K12 multimodal.

    Two pieces, both public:
      - data: ``lipku1999/K12-Vista`` → ``K12_Vista.jsonl`` (33,660 rows, ~501 MB;
        images are base64-inlined in the ``img`` field, so there is no separate
        image archive).
      - code: the official repo checkout ``github.com/lichongod/K12Vista``, needed
        for ``K12_Vista/code/prompt.py`` — the adapter loads the official infer and
        judge prompts straight from it rather than restating them.

    After this, build the pinned evaluation sample:
        python scripts/eval/data/build_k12vista_sample.py --size 300
    """
    out_dir = ROOT / "sources" / "datasets" / "k12vista"
    prompt_file = out_dir / "K12_Vista" / "code" / "prompt.py"
    data_path = out_dir / "K12_Vista" / "data" / "K12_Vista.jsonl"

    if not _ok(prompt_file) or force:
        print(f"cloning github.com/lichongod/K12Vista -> {out_dir}")
        out_dir.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            ["git", "clone", "--depth", "1", "https://github.com/lichongod/K12Vista.git", str(out_dir)],
            check=True,
        )

    if _ok(data_path) and not force:
        print(f"skip k12vista data: {data_path} already exists (use --force to re-download)")
        return out_dir

    from huggingface_hub import hf_hub_download

    print("downloading lipku1999/K12-Vista :: K12_Vista.jsonl (~501 MB)")
    cached = hf_hub_download("lipku1999/K12-Vista", "K12_Vista.jsonl", repo_type="dataset")
    data_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(cached, data_path)

    with data_path.open(encoding="utf-8") as fh:
        total = sum(1 for _ in fh)
    manifest = {
        "source": "https://huggingface.co/datasets/lipku1999/K12-Vista",
        "code": "https://github.com/lichongod/K12Vista",
        "citation": "Li et al. 2025, K12Vista (arXiv:2506.01676)",
        "total_rows": total,
        "images": "base64-inlined in the `img` field; build_k12vista_sample.py decodes the sampled ones",
        "scoring": "official directly_eval_prompt: LLM judge emits per-blank 0/1, item score = mean",
        "judge_note": (
            "official judge is Qwen2.5-VL-72B / K12-PEM served on GPU; this repo substitutes an API "
            "judge (K12VISTA_JUDGE_MODEL) with the official rubric text, uncalibrated against humans"
        ),
    }
    (out_dir / "data_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"wrote {total} rows -> {data_path}")
    print("next: python scripts/eval/data/build_k12vista_sample.py --size 300")
    return out_dir


def fetch_mathtutorbench(force: bool = False) -> Path:
    """Materialize MathTutorBench task data into stdlib-readable JSONL.

    Sources:
      - ``eth-nlped/stepverify`` (HF, public): solution_correctness /
        mistake_location / mistake_correction → ``stepverify.jsonl``.
      - ``dmacjam/pedagogical-rewardmodel-data`` (HF, public) ``test`` split:
        the 482 expert-labeled positive/negative teacher-response pairs used for
        judge calibration → ``pref_test.jsonl``.
      - GSM8K (already cloned locally as parquet under ``sources/datasets/gsm8k``):
        problem_solving (``main``) and socratic_questioning (``socratic``) →
        ``gsm8k_main.jsonl`` / ``gsm8k_socratic.jsonl``.

    The scaffolding/pedagogy bridge files (``datasets/mathdial_bridge*.json``)
    already ship inside the cloned repo and are read in place by the adapter.
    """
    base = ROOT / "sources" / "datasets" / "mathtutorbench"
    out_dir = base / "data"
    out_dir.mkdir(parents=True, exist_ok=True)

    # --- HuggingFace datasets (need the `datasets` lib; isolated to this step) ---
    sv_out = out_dir / "stepverify.jsonl"
    pref_out = out_dir / "pref_test.jsonl"
    hf_targets = [
        (sv_out, "eth-nlped/stepverify", "train"),
        (pref_out, "dmacjam/pedagogical-rewardmodel-data", "test"),
    ]
    if force or not all(_ok(p) for p, _, _ in hf_targets):
        try:
            from datasets import load_dataset
        except ImportError as exc:  # pragma: no cover - actionable hint
            raise SystemExit(
                "the `datasets` library is required to fetch the HuggingFace parts "
                "of MathTutorBench (eth-nlped/stepverify, dmacjam/pedagogical-"
                "rewardmodel-data). Install it: pip install datasets"
            ) from exc
        for out_path, repo, split in hf_targets:
            if _ok(out_path) and not force:
                print(f"skip {out_path.name}: already exists (use --force)")
                continue
            print(f"loading {repo} split={split}")
            ds = load_dataset(repo, split=split)
            with out_path.open("w", encoding="utf-8") as fh:
                for ex in ds:
                    rec = {k: _jsonable(v) for k, v in dict(ex).items()}
                    fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
            print(f"  wrote {len(ds)} rows -> {out_path}")

    # --- GSM8K from the local parquet clone (no download) ---
    for cfg, fname in (("main", "gsm8k_main.jsonl"), ("socratic", "gsm8k_socratic.jsonl")):
        out_path = out_dir / fname
        if _ok(out_path) and not force:
            print(f"skip {out_path.name}: already exists (use --force)")
            continue
        parquet = ROOT / "sources" / "datasets" / "gsm8k" / cfg / "test-00000-of-00001.parquet"
        if not parquet.exists():
            raise SystemExit(
                f"missing {parquet}; expected the GSM8K parquet clone under "
                "sources/datasets/gsm8k/{main,socratic}/"
            )
        df = pd.read_parquet(parquet)
        with out_path.open("w", encoding="utf-8") as fh:
            for _, row in df.iterrows():
                rec = {"question": _jsonable(row["question"]), "answer": _jsonable(row["answer"])}
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
        print(f"wrote {len(df)} rows -> {out_path}")

    return out_dir


def fetch_ceval(force: bool = False) -> Path:
    """Materialize C-Eval (ceval/ceval-exam) into stdlib-readable JSONL.

    C-Eval is a Chinese multi-discipline multiple-choice exam (52 subjects,
    4 options A/B/C/D). The HuggingFace repo exposes one config per subject,
    each with ``dev`` (5 labeled few-shot exemplars), ``val`` (public labels),
    and ``test`` (labels withheld for the official leaderboard).

    We materialize the ``val`` split (1,346 labeled items) for local scoring
    and ``dev`` (260 exemplars) for optional few-shot prompting. ``test`` is
    skipped because its answers are not released. The subject->category map is
    read from the repo clone's ``subject_mapping.json``.
    """
    base = ROOT / "sources" / "datasets" / "ceval"
    out_dir = base / "data"
    val_out = out_dir / "val.jsonl"
    dev_out = out_dir / "dev.jsonl"
    if not force and _ok(val_out) and _ok(dev_out):
        print(f"skip ceval: outputs already in {out_dir} (use --force to rebuild)")
        return out_dir

    mapping_path = base / "subject_mapping.json"
    if not mapping_path.exists():
        raise SystemExit(
            f"missing {mapping_path}; clone https://github.com/hkust-nlp/ceval "
            "into sources/datasets/ceval first"
        )
    with mapping_path.open(encoding="utf-8") as fh:
        subject_mapping = json.load(fh)  # key -> [english, chinese, category]

    try:
        from datasets import load_dataset
    except ImportError as exc:  # pragma: no cover - actionable hint
        raise SystemExit(
            "the `datasets` library is required to fetch C-Eval "
            "(ceval/ceval-exam). Install it: pip install datasets"
        ) from exc

    out_dir.mkdir(parents=True, exist_ok=True)
    counts = {"val": 0, "dev": 0}
    with val_out.open("w", encoding="utf-8") as vfh, dev_out.open("w", encoding="utf-8") as dfh:
        for subject in sorted(subject_mapping):
            english, chinese, category = subject_mapping[subject]
            ds = load_dataset("ceval/ceval-exam", name=subject)
            for split, fh in (("val", vfh), ("dev", dfh)):
                if split not in ds:
                    continue
                for ex in ds[split]:
                    rec = {
                        "item_id": f"{subject}-{split}-{ex['id']}",
                        "subject": subject,
                        "subject_zh": chinese,
                        "category": category,
                        "question": _jsonable(ex.get("question")),
                        "A": _jsonable(ex.get("A")),
                        "B": _jsonable(ex.get("B")),
                        "C": _jsonable(ex.get("C")),
                        "D": _jsonable(ex.get("D")),
                        "answer": _jsonable(ex.get("answer")),
                        "explanation": _jsonable(ex.get("explanation")),
                    }
                    fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
                    counts[split] += 1
    print(f"wrote ceval: {counts['val']} val rows -> {val_out}, {counts['dev']} dev rows -> {dev_out}")
    return out_dir


def fetch_pedagogy_benchmark(force: bool = False) -> Path:
    """Materialize the Pedagogy Benchmark (AI-for-Education/pedagogy-benchmark).

    1,143 English multiple-choice questions from Chilean teacher qualification
    exams, split into CDPK (920, config ``cdpk_main``) and SEND (223, config
    ``cdpk_send``). Options run A..G — most items use A-D, a minority go
    further, so ``answer_e``/``answer_f``/``answer_g`` are often null.

    The HF repo is **gated**: accept the terms at
    https://huggingface.co/datasets/AI-for-Education/pedagogy-benchmark while
    logged in, then export ``HF_TOKEN`` (or run ``huggingface-cli login``).

    The HF release merges the upstream dev and test CSVs into one file per
    config, grouped by category. The official configs use ``example_rows:
    [0, 1, 2]``, so **the first three rows of each category are the few-shot
    exemplars** and are not scored: 1,143 rows - 8 categories x 3 = 1,119
    scored items, which is exactly the official scored set. We tag each row
    with ``is_exemplar`` / ``category_index`` here so the adapter can split
    them without re-deriving the ordering.
    """
    base = ROOT / "sources" / "datasets" / "pedagogy_benchmark"
    out_dir = base / "data"
    questions_out = out_dir / "questions.jsonl"
    examples_out = out_dir / "examples.jsonl"
    if not force and _ok(questions_out):
        print(f"skip pedagogy_benchmark: {questions_out} already exists (use --force to rebuild)")
        return out_dir

    try:
        from datasets import load_dataset
    except ImportError as exc:  # pragma: no cover - actionable hint
        raise SystemExit(
            "the `datasets` library is required to fetch the Pedagogy Benchmark. "
            "Install it: pip install datasets"
        ) from exc

    option_keys = [f"answer_{letter}" for letter in "abcdefg"]
    out_dir.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, Any]] = []
    try:
        for config, task in (("cdpk_main", "cdpk"), ("cdpk_send", "send")):
            ds = load_dataset("AI-for-Education/pedagogy-benchmark", name=config)
            split = "train" if "train" in ds else next(iter(ds))
            for row in ds[split]:
                options = {
                    letter.upper(): _jsonable(row.get(key))
                    for letter, key in zip("abcdefg", option_keys)
                }
                records.append(
                    {
                        "item_id": f"{task}:{config}:{_jsonable(row.get('question_id'))}",
                        "task": task,
                        "config": config,
                        "question_id": _jsonable(row.get("question_id")),
                        "question": _jsonable(row.get("question")),
                        "options": {k: v for k, v in options.items() if v not in (None, "")},
                        "correct_answer": _jsonable(row.get("correct_answer")),
                        "category": _jsonable(row.get("category")),
                        "secondary_category": _jsonable(row.get("secondary_category")),
                        "pedagogical_subdomain": _jsonable(row.get("pedagogical_subdomain")),
                        "age_group": _jsonable(row.get("age_group")),
                        "education_level": _jsonable(row.get("education_level")),
                        "year": _jsonable(row.get("year")),
                    }
                )
    except Exception as exc:  # noqa: BLE001 - surface the gate as an actionable message
        raise SystemExit(
            f"failed to load AI-for-Education/pedagogy-benchmark: {exc}\n"
            "This dataset is gated. Accept the terms on the dataset page while logged in, "
            "then export HF_TOKEN=<read token> (or run `huggingface-cli login`)."
        ) from exc

    # Tag the official example_rows [0, 1, 2] of each category. Rows arrive
    # grouped by category in dataset order, which is the order the official
    # per-category CSVs are read in.
    per_category: dict[str, int] = {}
    for rec in records:
        category = str(rec["category"])
        index = per_category.get(category, 0)
        per_category[category] = index + 1
        rec["category_index"] = index
        rec["is_exemplar"] = index < 3

    exemplars = [r for r in records if r["is_exemplar"]]
    scored = [r for r in records if not r["is_exemplar"]]
    with questions_out.open("w", encoding="utf-8") as fh:
        for rec in records:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    with examples_out.open("w", encoding="utf-8") as fh:
        for rec in exemplars:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print(
        f"wrote pedagogy_benchmark: {len(records)} questions -> {questions_out}\n"
        f"  {len(scored)} scored items + {len(exemplars)} few-shot exemplars "
        f"({len(per_category)} categories x 3) -> {examples_out}"
    )
    return out_dir


ASAP2_REPO = "https://github.com/scrosseye/ASAP_2.0/raw/main"
# The authors ship the test split password-protected to slow down scraping; the
# password is published in the repo README.
ASAP2_TEST_PASSWORD = b"asap2_test"
# Per-prompt source articles as plain text. The authors' repo ships these only
# as (partly scanned) PDFs, so we take the text columns from the Kaggle mirror
# of the same corpus when it happens to be present locally. Optional: only the
# adapter's --with-source variant needs them.
ASAP2_KAGGLE_CSV = "ASAP2_train_sourcetexts.csv"


def fetch_asap_2(force: bool = False) -> Path:
    """Materialize ASAP 2.0 from the authors' repo (github.com/scrosseye/ASAP_2.0).

    ~24.7k source-based argumentative essays by US grade 6-10 students, each
    holistically scored 1-6 by trained raters (Crossley et al., ASAP 2.0; an
    extension of the PERSUADE corpus).

    We use the **authors' repo, not the Kaggle mirror**, because only the repo
    ships the official train/test split (17,307 / 7,421) and the official
    holistic scoring rubric. The Kaggle dataset ``lburleigh/asap-2-0`` is the
    same corpus already merged, with no split column. The 7,421-row ``test``
    split is the evaluation set; ``train`` is materialized too but not scored
    by default.

    Source articles: the repo ships them as PDFs, several of which are scans
    with no text layer, so plain text is lifted from the Kaggle mirror's
    ``source_text_*`` columns when that CSV is already present under ``raw/``.
    Note the "Facial action coding system" article is withheld there as
    "Copyright Restricted", so it is unavailable at any quality.

    ASAP 2.0 is a *corpus*, not an LLM evaluation suite: it ships human scores
    and the rubric but no official LLM prompting protocol. The scoring prompt
    lives in the adapter and is ours; the rubric, the split, and QWK against
    human scores are not.
    """
    import io
    import zipfile

    base = ROOT / "sources" / "datasets" / "asap_2"
    out_dir = base / "data"
    out_path = out_dir / "essays.jsonl"
    rubric_path = out_dir / "rubric.txt"
    if not force and _ok(out_path) and _ok(rubric_path):
        print(f"skip asap_2: outputs already in {out_dir} (use --force to rebuild)")
        return out_dir

    github_dir = base / "github"
    github_dir.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)

    frames = {}
    pandas = _require_pandas()
    for split, archive, password in (
        ("train", "ASAP_2_Final_github_train.zip", None),
        ("test", "ASAP_2_Final_github_test.zip", ASAP2_TEST_PASSWORD),
    ):
        archive_path = github_dir / archive
        _download_file(f"{ASAP2_REPO}/{archive}", archive_path, force=force)
        with zipfile.ZipFile(archive_path) as zf:
            member = next(
                name
                for name in zf.namelist()
                if name.endswith(".csv") and "__MACOSX" not in name
            )
            with zf.open(member, pwd=password) as fh:
                frames[split] = pandas.read_csv(io.BytesIO(fh.read()))

    # Official holistic rubric (1-6), extracted from the repo's .docx.
    rubric_docx = github_dir / "asap_scoring_rubric.docx"
    _download_file(f"{ASAP2_REPO}/asap_scoring_rubric.docx", rubric_docx, force=force)
    rubric_path.write_text(_asap_rubric_text(rubric_docx), encoding="utf-8")

    # Optional plain-text source articles from the Kaggle mirror, if present.
    source_texts: dict[str, list[str]] = {}
    kaggle_csv = base / "raw" / ASAP2_KAGGLE_CSV
    if kaggle_csv.exists():
        cols = ["prompt_name"] + [f"source_text_{i}" for i in range(1, 5)]
        mirror = pandas.read_csv(kaggle_csv, usecols=cols).drop_duplicates("prompt_name")
        for _, row in mirror.iterrows():
            texts = [
                str(row[f"source_text_{i}"]).strip()
                for i in range(1, 5)
                if pandas.notna(row[f"source_text_{i}"])
            ]
            # The FACS article is withheld upstream; treat it as absent rather
            # than feeding the model the string "Copyright Restricted".
            texts = [t for t in texts if t and t.lower() != "copyright restricted"]
            if texts:
                source_texts[str(row["prompt_name"])] = texts

    written = {"train": 0, "test": 0}
    with out_path.open("w", encoding="utf-8") as fh:
        for split in ("train", "test"):
            for _, row in frames[split].iterrows():
                prompt_name = _jsonable(row.get("prompt_name"))
                rec = {
                    "item_id": str(_jsonable(row.get("essay_id"))),
                    "split": split,
                    "full_text": _jsonable(row.get("full_text")),
                    "score": _jsonable(row.get("score")),
                    "prompt_name": prompt_name,
                    "assignment": _jsonable(row.get("assignment")),
                    "task": _jsonable(row.get("task")),
                    "grade_level": _jsonable(row.get("grade_level")),
                    "essay_word_count": _jsonable(row.get("essay_word_count")),
                    "has_source_text": str(prompt_name) in source_texts,
                }
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
                written[split] += 1

    if source_texts:
        (out_dir / "source_texts.json").write_text(
            json.dumps(source_texts, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    manifest = {
        "source": "https://github.com/scrosseye/ASAP_2.0",
        "splits": written,
        "eval_split": "test",
        "rubric": "official holistic 1-6, asap_scoring_rubric.docx",
        "source_texts_available_for": sorted(source_texts),
        "source_texts_note": (
            "Plain text lifted from the Kaggle mirror lburleigh/asap-2-0; the repo's own "
            "PDFs are partly scans. 'Facial action coding system' is withheld upstream as "
            "'Copyright Restricted' and is unavailable."
        ),
        "protocol_note": (
            "Corpus, not an LLM benchmark: human scores, official split and rubric are "
            "upstream; the LLM scoring prompt is defined in the adapter and is not official."
        ),
    }
    (out_dir / "data_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    test_prompts = set(frames["test"].prompt_name.astype(str))
    with_source = len(test_prompts & set(source_texts))
    print(
        f"wrote asap_2: {written['test']} test + {written['train']} train essays -> {out_path}\n"
        f"  official rubric -> {rubric_path}; source texts for "
        f"{with_source}/{len(test_prompts)} test prompts"
    )
    return out_dir


def _asap_rubric_text(docx_path: Path) -> str:
    """Plain text of the official holistic rubric from the repo's .docx.

    Stdlib only: a .docx is a zip whose word/document.xml carries the text;
    paragraph breaks are </w:p>.
    """
    import html
    import zipfile

    with zipfile.ZipFile(docx_path) as zf:
        xml = zf.read("word/document.xml").decode("utf-8")
    xml = re.sub(r"</w:p>", "\n", xml)
    text = html.unescape(re.sub(r"<[^>]+>", "", xml))
    return "\n".join(line.strip() for line in text.split("\n") if line.strip())


def fetch_longtutor(force: bool = False) -> Path:
    """Clone the official LongTutor code/data into the unified dataset root."""
    base = ROOT / "sources" / "datasets" / "longtutor"
    if (base / ".git").exists() and not force:
        print(f"skip longtutor: {base} already exists (use --force to refresh manually)")
        return base
    if base.exists():
        raise SystemExit(f"refusing to replace non-git directory {base}; move it aside first")
    subprocess.run(
        ["git", "clone", "--depth", "1", "https://github.com/liano3/LongTutor.git", str(base)],
        check=True,
    )
    print(
        "LongTutor has no upstream LICENSE file as of integration. Keep it under "
        "sources/datasets (gitignored) and do not redistribute without permission."
    )
    return base


def fetch_mooccube(force: bool = False) -> Path:
    """Download MOOCCube (Yu et al., ACL 2020) — the XuetangX MOOC knowledge graph.

    One 1.09 GB zip, no registration. What the P19 adapter needs from it:

      - ``relations/prerequisite-dependency.json`` — the released **expert
        prerequisite edges** (TSV ``<prereq_concept_id>\\t<dependent_concept_id>``,
        1,027 lines / 905 unique edges over 425 concepts, math + CS). This is the
        gold used by ``mooccube_prereq``.
      - ``entities/concept.json`` — 114,563 concepts (id / name / en / explanation).
      - ``relations/course-concept.json`` — course→concept, used to draw
        *same-course* hard distractors.

    NOT used as gold: ``additional_information/prerequisite_prediction.json``.
    Despite the similar name it is the auxiliary *prerequisite-prediction task*
    dump — 489,300 concept-**name** pairs carrying a model's ``predict``
    probabilities, of which only 3,616 are human-labeled (1,605 pos / 2,011 neg),
    and its positive set barely intersects the graph relation (28 / 1,605 shared
    pairs). Scoring against it would mean scoring against another model's guesses
    on an unjoinable vocabulary. See doc/benchmark_profiles/mooccube.md.

    After this, build the pinned item list:
        python scripts/eval/data/build_mooccube_item_list.py --size 300
    """
    import urllib.request
    import zipfile

    out_dir = ROOT / "sources" / "datasets" / "mooccube"
    root = out_dir / "MOOCCube"
    gold = root / "relations" / "prerequisite-dependency.json"
    if _ok(gold) and not force:
        print(f"skip mooccube: {gold} already exists (use --force to re-download)")
        return out_dir

    out_dir.mkdir(parents=True, exist_ok=True)
    archive = out_dir / "MOOCCube.zip"
    if not _ok(archive) or force:
        print(f"downloading {MOOCCUBE_URL} (~1.09 GB)")
        with urllib.request.urlopen(MOOCCUBE_URL) as resp:  # noqa: S310 - public dataset host
            with archive.open("wb") as fh:
                shutil.copyfileobj(resp, fh)
    print(f"extracting {archive}")
    with zipfile.ZipFile(archive) as zf:
        zf.extractall(out_dir)
    if not _ok(gold):
        raise SystemExit(f"extraction did not produce {gold}; inspect {archive}")

    with gold.open(encoding="utf-8") as fh:
        pairs = {tuple(line.rstrip("\n").split("\t")) for line in fh if line.strip()}
    manifest = {
        "source": MOOCCUBE_URL,
        "homepage": "http://moocdata.cn/data/MOOCCube",
        "citation": "Yu et al. 2020, MOOCCube: A Large-scale Data Repository for NLP Applications in MOOCs (ACL 2020)",
        "gold_relation": "relations/prerequisite-dependency.json",
        "gold_pairs_unique": len(pairs),
        "gold_direction": "<prerequisite_concept>\\t<dependent_concept>; verified on unambiguous pairs (加法→函数, 算术→绝对值)",
        "not_gold": {
            "file": "additional_information/prerequisite_prediction.json",
            "why": (
                "prerequisite-*prediction* task dump: 489,300 concept-name pairs with a model's "
                "`predict` probabilities, only 3,616 human-labeled, and its positives overlap the "
                "graph relation on just 28/1,605 pairs — a different, unjoinable annotation"
            ),
        },
        "scoring": "rule-based (option letter regex + topological-constraint check); no LLM judge, no extraction LLM",
    }
    (out_dir / "data_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"mooccube ready: {len(pairs)} unique prerequisite edges -> {gold}")
    print("next: python scripts/eval/data/build_mooccube_item_list.py --size 300")
    return out_dir


TUTORBENCH_REPO_ID = "ScaleAI/TutorBench"
# severity -> rubric weight (paper Sec. 2.4: critical=+5, not_critical=+1,
# critical_negative=-5). "deleted" rubrics are dropped (not scored).
TUTORBENCH_SEVERITY_WEIGHT = {
    "critical": 5,
    "not_critical": 1,
    "critical_negative": -5,
}


def _tutorbench_use_case(batch: str) -> tuple[int, str]:
    """(use_case 1/2/3, modality 'text'|'multimodal') from the BATCH string."""
    b = (batch or "").upper()
    uc = 1 if "USE_CASE_1" in b else 2 if "USE_CASE_2" in b else 3 if "USE_CASE_3" in b else 0
    modality = "multimodal" if "MULTIMODAL" in b else "text"
    return uc, modality


def _tutorbench_image_ext(data: bytes) -> str:
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return ".png"
    if data[:2] == b"\xff\xd8":
        return ".jpg"
    if data[:6] in (b"GIF87a", b"GIF89a"):
        return ".gif"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return ".webp"
    return ".png"


def fetch_tutorbench(force: bool = False) -> Path:
    """Materialize TutorBench (ScaleAI/TutorBench) into JSONL + extracted images.

    1,473 real STEM tutoring samples across three use cases -- adaptive
    explanation (UC1), assessment & feedback (UC2), active-learning hints (UC3),
    each in text-only or multimodal form -- with 15k+ per-sample rubric criteria
    (severity critical/not_critical/critical_negative). The model under test
    generates a tutoring reply; an LLM judge rates each rubric criterion
    pass/fail and the score is the weighted average rubric rating (paper Eq. 1).

    Source parquet: https://huggingface.co/datasets/ScaleAI/TutorBench (two
    ``data/train-*.parquet`` shards, images embedded as bytes). We extract each
    image to ``images/<TASK_ID>.<ext>`` and flatten rubrics to
    ``{criteria, weight, attributes}`` so the adapter needs no parquet at
    eval time.
    """
    pandas = _require_pandas()
    base = ROOT / "sources" / "datasets" / "tutorbench"
    data_dir = base / "data"
    images_dir = base / "images"
    jsonl_path = base / "tutorbench.jsonl"
    manifest_path = base / "data_manifest.json"
    if not force and _ok(jsonl_path):
        print(f"skip tutorbench: {jsonl_path} already exists (use --force to rebuild)")
        return jsonl_path

    shards = sorted(data_dir.glob("train-*.parquet"))
    if not shards:
        try:
            from huggingface_hub import snapshot_download
        except ImportError as exc:  # pragma: no cover - actionable hint
            raise SystemExit(
                "huggingface_hub is required to download TutorBench parquet shards. "
                "Install it: pip install huggingface_hub"
            ) from exc
        print(f"downloading {TUTORBENCH_REPO_ID} parquet shards (~1.1 GB)...")
        snapshot_download(
            repo_id=TUTORBENCH_REPO_ID,
            repo_type="dataset",
            allow_patterns=["data/train-*.parquet"],
            local_dir=str(base),
        )
        shards = sorted(data_dir.glob("train-*.parquet"))
    if not shards:
        raise SystemExit(f"no TutorBench parquet shards under {data_dir}")

    images_dir.mkdir(parents=True, exist_ok=True)
    frames = [pandas.read_parquet(s) for s in shards]
    df = pandas.concat(frames, ignore_index=True)

    dropped_rubrics = 0
    n_images = 0
    rows: list[dict[str, Any]] = []
    for _, r in df.iterrows():
        task_id = str(r["TASK_ID"])
        use_case, modality = _tutorbench_use_case(str(r["BATCH"]))
        rel_image = None
        if modality == "multimodal":
            img = r.get("Image")
            data = img.get("bytes") if isinstance(img, dict) else None
            if data:
                ext = _tutorbench_image_ext(bytes(data))
                out = images_dir / f"{task_id}{ext}"
                if force or not out.exists():
                    out.write_bytes(bytes(data))
                rel_image = f"images/{task_id}{ext}"
                n_images += 1
        rubrics: list[dict[str, Any]] = []
        for c in json.loads(r["RUBRICS"]):
            attrs = c.get("attributes") or {}
            severity = str(attrs.get("severity") or "").strip()
            if severity not in TUTORBENCH_SEVERITY_WEIGHT:
                dropped_rubrics += 1
                continue
            rubrics.append(
                {
                    "criteria": c.get("criteria"),
                    "weight": TUTORBENCH_SEVERITY_WEIGHT[severity],
                    "severity": severity,
                    "eval_dimension": (attrs.get("eval_dimension") or "").strip(),
                    "tutoring_skill": (attrs.get("tutoring_skill") or "").strip(),
                    "explicitness": (attrs.get("explicitness") or "").strip(),
                    "objectivity": (attrs.get("objectivity") or "").strip(),
                }
            )
        rows.append(
            {
                "task_id": task_id,
                "use_case": use_case,
                "modality": modality,
                "subject": _jsonable(r.get("SUBJECT")),
                "prompt": _jsonable(r.get("PROMPT")),
                "initial_explanation": _jsonable(r.get("UC1_INITIAL_EXPLANATION")) or "",
                "follow_up_prompt": _jsonable(r.get("FOLLOW_UP_PROMPT")) or "",
                "image": rel_image,
                "image_url": _jsonable(r.get("IMAGE_URL")),
                "bloom_taxonomy": _jsonable(r.get("bloom_taxonomy")),
                "rubrics": rubrics,
            }
        )

    with jsonl_path.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")

    from collections import Counter

    manifest = {
        "source": TUTORBENCH_REPO_ID,
        "homepage": "https://huggingface.co/datasets/ScaleAI/TutorBench",
        "paper": "https://arxiv.org/abs/2510.02663",
        "n_items": len(rows),
        "n_images": n_images,
        "n_rubrics": sum(len(x["rubrics"]) for x in rows),
        "dropped_rubrics_non_scored": dropped_rubrics,
        "use_case_counts": dict(Counter(x["use_case"] for x in rows)),
        "modality_counts": dict(Counter(x["modality"] for x in rows)),
        "subject_counts": dict(Counter(str(x["subject"]) for x in rows)),
        "severity_weights": TUTORBENCH_SEVERITY_WEIGHT,
        "note": (
            "Full public set (no Fair815 fair-subset file is shipped upstream; "
            "the colleague's 815-sample split is not reproducible from this release)."
        ),
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        f"wrote tutorbench: {len(rows)} items ({n_images} images, "
        f"{manifest['n_rubrics']} scored rubrics, {dropped_rubrics} non-scored dropped) -> {jsonl_path}"
    )
    return jsonl_path


K12BENCH_REPO = "lhpku20010120/K12-KGraph"
# Nine benchmark JSONL files under K12-Bench/ on the HF dataset, grouped into the
# five task families of K12-Bench (Liang et al. 2026, arXiv:2605.09635).
K12BENCH_FILES = {
    "prereq": ["prereq_subtask1", "prereq_subtask2"],
    "locate": ["locate_subtask1", "locate_subtask2"],
    "neighbor": ["neighbor"],
    "ground": ["ground_subtask1", "ground_subtask2"],
    "evidence": ["evidence_subtask1", "evidence_subtask2"],
}
# A handful of ground_subtask1 rows embed raw LaTeX (e.g. ``\mathrm``) that is not
# valid JSON (lone backslash escapes), so strict json.loads rejects them. Double
# any backslash that does not begin a valid JSON escape, then re-parse.
_BAD_ESCAPE = re.compile(r'\\(?![\\"/bfnrtu])')


def _load_k12bench_line(line: str) -> dict[str, Any]:
    try:
        return json.loads(line)
    except json.JSONDecodeError:
        return json.loads(_BAD_ESCAPE.sub(r"\\\\", line))


def fetch_k12bench(force: bool = False) -> Path:
    """Download K12-Bench (Liang et al. 2026, K12-KGraph, arXiv:2605.09635).

    23,640 four-option **multi-select** MCQ probing *curriculum cognition* —
    prerequisite chains, concept taxonomy, experiment-concept links, and
    cross-chapter positioning — derived from a curriculum-aligned knowledge graph
    over People's Education Press K-12 textbooks (math/physics/chemistry/biology).
    Text-only; the paper contrasts it with factual-recall exams (C-Eval/CMMLU).

    Public + ungated on HuggingFace (``{repo}``, CC BY-NC-SA 4.0); the nine
    ``K12-Bench/*.jsonl`` files map onto five task families. Each row is
    ``{{id, question, options: {{A..D}}, answer: [letters]}}``. We re-serialize
    every family to a clean stdlib-readable JSONL under
    ``sources/datasets/k12bench/`` (fixing the two LaTeX-broken ground rows) and
    tag each row with its ``task_family``/``subtask``. Rule-scored (Exact Match +
    instance-level Macro-F1), no judge, no extraction model needed.
    """.format(repo=K12BENCH_REPO)
    from huggingface_hub import hf_hub_download

    out_dir = ROOT / "sources" / "datasets" / "k12bench"
    data_dir = out_dir / "data"
    manifest_path = out_dir / "data_manifest.json"
    if _ok(manifest_path) and not force:
        print(f"skip k12bench: {manifest_path} already exists (use --force to re-download)")
        return out_dir

    data_dir.mkdir(parents=True, exist_ok=True)
    family_counts: dict[str, int] = {}
    subtask_counts: dict[str, int] = {}
    fixed_rows = 0
    total = 0
    for family, stems in K12BENCH_FILES.items():
        out_rows: list[dict[str, Any]] = []
        for stem in stems:
            cached = hf_hub_download(K12BENCH_REPO, f"K12-Bench/{stem}.jsonl", repo_type="dataset")
            with open(cached, encoding="utf-8") as fh:
                for line in fh:
                    if not line.strip():
                        continue
                    try:
                        row = json.loads(line)
                    except json.JSONDecodeError:
                        row = _load_k12bench_line(line)
                        fixed_rows += 1
                    row["task_family"] = family
                    row["subtask"] = stem
                    out_rows.append(row)
                    subtask_counts[stem] = subtask_counts.get(stem, 0) + 1
        family_counts[family] = len(out_rows)
        total += len(out_rows)
        out_path = data_dir / f"{family}.jsonl"
        with out_path.open("w", encoding="utf-8") as fh:
            for row in out_rows:
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")

    manifest = {
        "source": f"https://huggingface.co/datasets/{K12BENCH_REPO}",
        "homepage": "https://github.com/haolpku/K12-Dataset",
        "citation": "Liang et al. 2026, K12-KGraph: A Curriculum-Aligned Knowledge Graph for Benchmarking and Training Educational LLMs (arXiv:2605.09635)",
        "license": "CC BY-NC-SA 4.0 (non-commercial)",
        "task_families": family_counts,
        "subtasks": subtask_counts,
        "total_items": total,
        "format": "four-option multi-select MCQ; answer is a list of option letters (1-3 correct)",
        "scoring": "rule-based (Exact Match + instance-level Macro-F1); no LLM judge, no extraction LLM",
        "note": f"{fixed_rows} ground_subtask1 row(s) carried invalid-JSON LaTeX escapes; repaired on import",
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"k12bench ready: {total} items across {len(family_counts)} families -> {data_dir}")
    return out_dir


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--benchmark",
        required=True,
        choices=[
            "mmlu_pro",
            "olympiadbench",
            "eduguard_bench",
            "mathtutorbench",
            "ceval",
            "mrbench",
            "bea2025",
            "mmtutorbench",
            "edubench",
            "umwp",
            "ifeval",
            "k12vista",
            "k12bench",
            "longtutor",
            "mooccube",
            "pedagogy_benchmark",
            "asap_2",
            "tutorbench",
            "all",
        ],
    )
    parser.add_argument("--force", action="store_true", help="re-download even if output already exists")
    args = parser.parse_args()
    if args.benchmark in ("mmlu_pro", "all"):
        fetch_mmlu_pro(force=args.force)
    if args.benchmark in ("olympiadbench", "all"):
        fetch_olympiadbench(force=args.force)
    if args.benchmark in ("eduguard_bench", "all"):
        fetch_eduguard_bench(force=args.force)
    if args.benchmark in ("mathtutorbench", "all"):
        fetch_mathtutorbench(force=args.force)
    if args.benchmark in ("ceval", "all"):
        fetch_ceval(force=args.force)
    if args.benchmark in ("mrbench", "all"):
        fetch_mrbench(force=args.force)
    if args.benchmark in ("bea2025", "all"):
        fetch_bea2025(force=args.force)
    if args.benchmark in ("mmtutorbench", "all"):
        fetch_mmtutorbench(force=args.force)
    if args.benchmark in ("edubench", "all"):
        fetch_edubench(force=args.force)
    if args.benchmark in ("umwp", "all"):
        fetch_umwp(force=args.force)
    if args.benchmark in ("ifeval", "all"):
        fetch_ifeval(force=args.force)
    if args.benchmark in ("k12vista", "all"):
        fetch_k12vista(force=args.force)
    if args.benchmark in ("k12bench", "all"):
        fetch_k12bench(force=args.force)
    if args.benchmark in ("longtutor", "all"):
        fetch_longtutor(force=args.force)
    if args.benchmark in ("mooccube", "all"):
        fetch_mooccube(force=args.force)
    if args.benchmark in ("pedagogy_benchmark", "all"):
        fetch_pedagogy_benchmark(force=args.force)
    if args.benchmark in ("asap_2", "all"):
        fetch_asap_2(force=args.force)
    if args.benchmark in ("tutorbench", "all"):
        fetch_tutorbench(force=args.force)


if __name__ == "__main__":
    main()
