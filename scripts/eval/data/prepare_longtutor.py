#!/usr/bin/env python3
"""Build the LongTutor history-feature input released incompletely upstream.

The official repository contains XES3G5M sequences, questions, generated test
cases, and human gold, but not ``history_features_lastq_scale.jsonl`` required
by its evaluator.  Reuse the upstream feature builder so sample keys remain
compatible with ``human_an_updated.jsonl`` instead of maintaining a divergent
copy of that preprocessing logic here.
"""

from __future__ import annotations

import argparse
import contextlib
from datetime import datetime
import hashlib
import importlib.util
import io
import json
import sys
import types
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "sources" / "datasets" / "longtutor"


def _load_module(path: Path):
    # Upstream imports plotting libraries at module import time although the
    # feature-building functions do not use them. Keep those optional paper-
    # figure dependencies out of the benchmark runtime.
    if "matplotlib" not in sys.modules:
        matplotlib = types.ModuleType("matplotlib")
        matplotlib.pyplot = types.ModuleType("matplotlib.pyplot")
        sys.modules["matplotlib"] = matplotlib
        sys.modules["matplotlib.pyplot"] = matplotlib.pyplot
    if "seaborn" not in sys.modules:
        sys.modules["seaborn"] = types.ModuleType("seaborn")
    if "numpy" not in sys.modules:
        sys.modules["numpy"] = types.ModuleType("numpy")
    if "openai_helper" not in sys.modules:
        helper = types.ModuleType("openai_helper")

        def _iter_jsonl(source):
            with Path(source).open(encoding="utf-8") as fh:
                for line in fh:
                    if line.strip():
                        yield json.loads(line)

        def _parse_ts(value):
            text = str(value).strip().replace("Z", "+00:00")
            try:
                return datetime.fromisoformat(text)
            except ValueError:
                return datetime.strptime(text, "%Y-%m-%d %H:%M:%S")

        helper._iter_jsonl = _iter_jsonl
        helper._parse_ts = _parse_ts
        sys.modules["openai_helper"] = helper
    scripts_dir = str(path.parent)
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    spec = importlib.util.spec_from_file_location("longtutor_compute_history_stats", path)
    if spec is None or spec.loader is None:
        raise SystemExit(f"cannot import upstream feature builder: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _keys(path: Path) -> set[str]:
    found: set[str] = set()
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            row = json.loads(line)
            key = row.get("_key")
            if key:
                found.add(str(key))
    return found


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    script = BASE / "scripts" / "compute_history_stats.py"
    data = BASE / "data" / "XES3G5M"
    sequences = data / "sequences_long.jsonl"
    questions = data / "questions.jsonl"
    gold = data / "human_an_updated.jsonl"
    output = data / "history_features_lastq_scale.jsonl"
    for path in (script, sequences, questions, gold):
        if not path.exists():
            raise SystemExit(
                f"missing {path}; run: python scripts/eval/data/fetch_eval_datasets.py --benchmark longtutor"
            )
    if output.exists() and output.stat().st_size and not args.force:
        print(f"skip longtutor preparation: {output} exists (use --force to rebuild)")
        return

    upstream = _load_module(script)
    questions_map = upstream.load_questions_map(questions)
    global_error = upstream.compute_global_error_rates(sequences)
    targets: dict[str, set[str]] = {}
    with gold.open(encoding="utf-8") as fh:
        for line in fh:
            row = json.loads(line)
            key = str(row.get("_key", ""))
            if "||" not in key:
                continue
            uid, digest = key.split("||", 1)
            targets.setdefault(uid, set()).add(digest)

    # The released gold was sampled from intermediate points in each learner
    # trajectory, while the released builder only selects the final point.
    # Recover the exact prefixes by matching the official question-text hash
    # embedded in every gold _key.
    target_sequences = data / ".target_sequences.tmp.jsonl"
    matched: set[str] = set()
    with sequences.open(encoding="utf-8") as src, target_sequences.open("w", encoding="utf-8") as dst:
        for line in src:
            obj = json.loads(line)
            uid = str(obj.get("uid", ""))
            wanted = targets.get(uid)
            if not wanted:
                continue
            seq = obj.get("sequence") or []
            for idx, item in enumerate(seq):
                qinfo = questions_map.get(str(item.get("question")), {})
                rendered = upstream._render_qinfo_str(qinfo, item)
                digest = hashlib.sha256(rendered.encode("utf-8")).hexdigest()
                if digest in wanted:
                    dst.write(json.dumps({"uid": uid, "sequence": seq[: idx + 1]}, ensure_ascii=False) + "\n")
                    matched.add(f"{uid}||{digest}")

    if not matched:
        target_sequences.unlink(missing_ok=True)
        raise SystemExit("could not locate any human-gold current question in the released trajectories")
    output.parent.mkdir(parents=True, exist_ok=True)
    try:
        # Upstream prints one related-history count per row; suppress that
        # research-time diagnostic in the production data preparation path.
        with contextlib.redirect_stdout(io.StringIO()):
            upstream.build_history_features(
                sequences_jsonl=target_sequences,
                questions_map=questions_map,
                global_error_rate=global_error,
                output_jsonl=output,
                recent_k=10,
            )
    finally:
        target_sequences.unlink(missing_ok=True)

    # A zero-key join means upstream preprocessing or released data changed;
    # fail early rather than run an apparently valid but unscorable benchmark.
    feature_keys = _keys(output)
    gold_keys = _keys(gold)
    overlap = feature_keys & gold_keys
    if not overlap:
        output.unlink(missing_ok=True)
        raise SystemExit("LongTutor preparation produced no keys matching the human gold")
    manifest = {
        "source": "https://github.com/liano3/LongTutor",
        "prepared_file": str(output.relative_to(ROOT)),
        "feature_rows": len(feature_keys),
        "human_gold_rows": len(gold_keys),
        "matched_gold_rows": len(overlap),
        "license_status": "upstream repository currently has no LICENSE file; do not redistribute",
    }
    (BASE / "data_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
