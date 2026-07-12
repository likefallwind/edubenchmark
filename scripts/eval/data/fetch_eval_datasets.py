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

Usage:
    python scripts/eval/data/fetch_eval_datasets.py --benchmark mmlu_pro
    python scripts/eval/data/fetch_eval_datasets.py --benchmark olympiadbench
    python scripts/eval/data/fetch_eval_datasets.py --benchmark eduguard_bench
    python scripts/eval/data/fetch_eval_datasets.py --benchmark bea2025
    python scripts/eval/data/fetch_eval_datasets.py --benchmark mmtutorbench
    python scripts/eval/data/fetch_eval_datasets.py --benchmark all
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any
from urllib.parse import quote

try:
    import pandas as pd
except ImportError:  # MMTutorBench / MRBench fetches do not need pandas.
    pd = None


ROOT = Path(__file__).resolve().parents[3]
HF = "https://huggingface.co/datasets"

MMLU_PRO_URL = f"{HF}/TIGER-Lab/MMLU-Pro/resolve/main/data/test-00000-of-00001.parquet"
MMTUTORBENCH_REPO = f"{HF}/Tangchiu/mmtutorbench/resolve/main"
MMTUTORBENCH_JSONL_URL = f"{MMTUTORBENCH_REPO}/mmtutorbench.jsonl"
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
            "umwp",
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
    if args.benchmark in ("umwp", "all"):
        fetch_umwp(force=args.force)


if __name__ == "__main__":
    main()
