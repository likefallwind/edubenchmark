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

Usage:
    python scripts/eval/data/fetch_eval_datasets.py --benchmark mmlu_pro
    python scripts/eval/data/fetch_eval_datasets.py --benchmark olympiadbench
    python scripts/eval/data/fetch_eval_datasets.py --benchmark eduguard_bench
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
        choices=["mmlu_pro", "olympiadbench", "eduguard_bench", "mathtutorbench", "ceval", "all"],
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


if __name__ == "__main__":
    main()
