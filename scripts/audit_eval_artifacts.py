#!/usr/bin/env python3
"""Audit every eval run under ``reports/eval/`` for *silent failures*.

The bug class this exists to catch: an upstream call fails (rate limit, quota,
gateway 5xx), the adapter swallows the exception and returns a placeholder
(``"unparsed"`` / ``None`` win_score / empty round-2), that placeholder is
written into ``extractions.jsonl`` — which the runner treats as a *successful*
cache entry, because only rows carrying an ``error`` key are retried — and the
scoring phase then counts the placeholder as a wrong answer. The run finishes,
``summary.json`` is written, and the number looks perfectly normal. It is not.

So this script does not look for runs that crashed. It looks for runs that
finished with a plausible-looking score built on failed calls, missing samples,
or a scoring path that cannot produce a valid value at all.

Signals (per run):
  * judge/extraction never actually ran      -> zero-usage extraction rows
  * judge/extraction failed and was cached   -> per-benchmark "unparsed" /
                                                judge_error / win_score=None /
                                                r2_error markers
  * errors cached                            -> ``error`` / ``empty_response``
  * samples missing                          -> predictions vs extractions vs
                                                scored vs summary.total_items
  * headline built on a broken scorer        -> degenerate metric (e.g. every
                                                rubric dimension exactly 0)
  * stale                                    -> summary.json older than the
                                                artifacts it summarizes
  * ceiling / zero variance across models    -> ``variance_restricted``
                                                (aligned with the 13 check)

Verdicts: ``unusable`` (the score is fake, rerun), ``caveat`` (usable if the
caveat is printed next to it), ``clean``, ``no_artifacts`` (nothing to judge).

Idempotent and offline: reads artifacts only, never calls an API, never touches
an existing artifact. Exits non-zero when any run is ``unusable`` so it can be
used as a release gate.

Usage:
    python scripts/audit_eval_artifacts.py
    python scripts/audit_eval_artifacts.py --benchmark mrbench_tutor --verbose
    python scripts/audit_eval_artifacts.py --gate    # exit 1 on unusable
"""

from __future__ import annotations

import argparse
import json
import statistics
import time
import sys
from datetime import date
from pathlib import Path
from typing import Any, Callable, Iterable

from eval.predictions_io import read_predictions

ROOT = Path(__file__).resolve().parents[1]
EVAL_ROOT = ROOT / "reports" / "eval"
AUDIT_DIR = EVAL_ROOT / "_audit"

# Fraction of items above which a failure signal makes the headline score fake.
UNUSABLE_RATE = 0.20
# Fraction above which the run is still usable but the caveat must be printed.
CAVEAT_RATE = 0.02
# Cross-model SD below which a benchmark cannot discriminate models.
MIN_SD = 0.02
# Mean above/below which a benchmark is at ceiling/floor (normalized 0-1 only).
CEILING = 0.95
FLOOR = 0.05


# ---------------------------------------------------------------------------
# Per-benchmark scoring topology.
#
# ``judge`` says who makes the call that can silently fail:
#   rule            no LLM in extraction/scoring at all -> a zero-usage
#                   extraction row is EXPECTED, never a finding.
#   extractor       extraction goes through the extractor client passed by the
#                   runner, so usage IS recorded -> zero usage is suspicious.
#   fixed_judge     the adapter builds its own judge client (MRBench, BEA,
#                   MathTutorBench win-rate, EduGuard P2, MMTutorBench). That
#                   client's usage is NOT the runner's usage window, so
#                   ``usage.calls == 0`` on every row is EXPECTED and proves
#                   nothing. Only the per-benchmark failure marker is evidence.
#   model_is_judge  the model under test is the judge; extraction is a local
#                   parse of its own reply, so "unparsed" is the model's fault,
#                   not an infrastructure failure (still a caveat if high).
#   imported        artifacts produced outside this harness.
# ---------------------------------------------------------------------------
BENCH_TOPOLOGY: dict[str, str] = {
    "mmlu_pro": "extractor",
    "agieval": "extractor",
    "mathvista": "extractor",
    "olympiadbench": "extractor",
    "ceval": "rule",
    "ifeval": "rule",
    "eduguard_sata": "rule",
    "p08_abstention": "rule",
    "mooccube_prereq": "rule",
    "eduguard_adversarial": "fixed_judge",
    "mrbench_tutor": "fixed_judge",
    "bea2025_tutor": "fixed_judge",
    "mmtutorbench": "fixed_judge",
    "mmtutorbench_judge_calibration": "fixed_judge",
    "k12vista": "fixed_judge",
    "mathtutorbench_pedagogy": "fixed_judge",
    "mathtutorbench_pedagogy_hard": "fixed_judge",
    "mathtutorbench_scaffolding": "fixed_judge",
    "mathtutorbench_scaffolding_hard": "fixed_judge",
    "mrbench_judge": "model_is_judge",
    "bea2025_judge": "model_is_judge",
    "mathtutorbench_judge_calibration": "model_is_judge",
    "mathtutorbench_socratic": "rule",
    "mathtutorbench_solution_correctness": "extractor",
    "mathtutorbench_mistake_location": "extractor",
    "mathtutorbench_mistake_correction": "extractor",
    "mathtutorbench_problem_solving": "extractor",
    "longtutor_evidence": "extractor",
    "longtutor_diagnosis": "rule",
    "longtutor_teaching": "extractor",
    "p07_selfcheck": "extractor",
    "p08_calibration": "extractor",
    "edubench": "imported",
    "eduillustrate": "imported",
}

# Benchmarks whose headline is an accuracy-like 0-1 rate, so a cross-model
# mean/SD is meaningful. Everything else (0-10 self-check score, 0-6 rubric,
# 1-5 Likert, 0-10 judge score) is deliberately excluded: a "ceiling" on a
# differently-scaled metric would be nonsense.
RATE_HEADLINE = {
    "mmlu_pro", "agieval", "ceval", "mathvista", "olympiadbench", "ifeval",
    "eduguard_sata", "eduguard_adversarial",
    "mrbench_judge", "mrbench_tutor", "bea2025_judge", "bea2025_tutor",
    "mathtutorbench_judge_calibration", "mathtutorbench_solution_correctness",
    "mathtutorbench_mistake_location", "mathtutorbench_mistake_correction",
    "mathtutorbench_problem_solving", "mathtutorbench_pedagogy",
    "mathtutorbench_pedagogy_hard", "mathtutorbench_scaffolding",
    "mathtutorbench_scaffolding_hard",
    "longtutor_evidence", "longtutor_diagnosis",
    "p08_abstention", "p08_calibration", "mooccube_prereq",
}

# Every LLM-extraction adapter in this repo calls the extractor only as a
# *fallback* (official regex first, LLM when the regex misses), so a row with
# ``usage.calls == 0`` is normal, not a finding. And every fixed-judge adapter
# builds its own client, whose usage never reaches the runner's usage window —
# which is exactly why ``reports/eval/mrbench_tutor/glm-5.2`` could report
# ``calls: 0`` for a judge that ran thousands of times, and equally for a judge
# that never ran at all. Judge usage is therefore NOT OBSERVABLE for these
# benchmarks; the per-benchmark failure marker is the only evidence we have.
# (Fix suggestion in the audit report: have the adapters return judge usage.)
JUDGE_USAGE_UNOBSERVABLE = {
    b for b, t in BENCH_TOPOLOGY.items() if t == "fixed_judge"
}


def _json_maybe(text: Any) -> Any:
    if not isinstance(text, str):
        return text if isinstance(text, dict) else None
    text = text.strip()
    if not text.startswith("{"):
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


# --- per-benchmark judge-failure detectors ---------------------------------
# Each takes one scored row and returns True when THAT ROW's score is the
# product of a failed/unusable judge or extraction call rather than a real
# model answer. Names are read from the adapter source, never guessed.

MRBENCH_DIMS = [
    "Mistake_Identification", "Mistake_Location", "Revealing_of_the_Answer",
    "Providing_Guidance", "Actionability", "Coherence", "Tutor_Tone", "humanlikeness",
]
MRBENCH_KEY = ["Mistake_Identification", "Providing_Guidance", "Actionability"]
BEA_DIMS = ["Mistake_Identification", "Mistake_Location", "Providing_Guidance", "Actionability"]
BEA_KEY = ["Mistake_Identification", "Providing_Guidance", "Actionability"]


def _labels_fail(row: dict[str, Any], key_dims: list[str]) -> bool:
    """Tutor-generation runs: a KEY dimension the judge could not label at all.

    ``score`` requires every key dimension == "Yes"; an ``unparsed`` key
    dimension therefore silently becomes a pedagogical FAIL.
    """
    labels = row.get("judge_labels")
    if not isinstance(labels, dict) or not labels:
        return True
    return any(str(labels.get(d, "unparsed")) == "unparsed" for d in key_dims)


def _labels_any_unparsed(row: dict[str, Any], dims: list[str]) -> bool:
    labels = row.get("judge_labels")
    if not isinstance(labels, dict) or not labels:
        return True
    return any(str(labels.get(d, "unparsed")) == "unparsed" for d in dims)


def _fail_winrate(row: dict[str, Any]) -> bool:
    # MathTutorBench pairwise: both A/B votes failed -> win_score None ->
    # normalized "judge_error" -> counted as a loss.
    return row.get("win_score") is None or row.get("normalized") == "judge_error"


def _partial_winrate(row: dict[str, Any]) -> bool:
    # Only one of the two debiasing orders came back: the position-swap
    # correction silently degrades to a single biased vote.
    votes = (_json_maybe(row.get("extracted")) or {}).get("votes")
    return isinstance(votes, list) and len(votes) == 1


def _fail_eduguard_adv(row: dict[str, Any]) -> bool:
    return row.get("final_label") in (None, "judge_error") or row.get("normalized") == "judge_error"


def _fail_mmtutorbench(row: dict[str, Any]) -> bool:
    return not row.get("parse_complete")


def _fail_k12vista(row: dict[str, Any]) -> bool:
    return bool((_json_maybe(row.get("extracted")) or {}).get("unparsed"))


def _fail_longtutor_teaching(row: dict[str, Any]) -> bool:
    scores = row.get("normalized")
    if not isinstance(scores, dict) or not scores:
        return True
    return any(not v for v in scores.values())


def _fail_p07(row: dict[str, Any]) -> bool:
    # Round-2 never came back (upstream throttling) -> the self-check metric has
    # no second observation for this item.
    return bool(row.get("r2_missing"))


def _fail_blank(row: dict[str, Any]) -> bool:
    return not str(row.get("extracted") or "").strip()


def _fail_unparsed_label(row: dict[str, Any]) -> bool:
    return str(row.get("normalized") or "") == "unparsed"


FAIL_DETECTORS: dict[str, Callable[[dict[str, Any]], bool]] = {
    "mrbench_tutor": lambda r: _labels_fail(r, MRBENCH_KEY),
    "bea2025_tutor": lambda r: _labels_fail(r, BEA_KEY),
    "mathtutorbench_pedagogy": _fail_winrate,
    "mathtutorbench_pedagogy_hard": _fail_winrate,
    "mathtutorbench_scaffolding": _fail_winrate,
    "mathtutorbench_scaffolding_hard": _fail_winrate,
    "eduguard_adversarial": _fail_eduguard_adv,
    "mmtutorbench": _fail_mmtutorbench,
    "k12vista": _fail_k12vista,
    "longtutor_teaching": _fail_longtutor_teaching,
    "longtutor_diagnosis": lambda r: str(r.get("normalized") or "") == "NO_LABEL",
    "longtutor_evidence": _fail_blank,
    "p07_selfcheck": _fail_p07,
    "mrbench_judge": _fail_unparsed_label,
    "bea2025_judge": _fail_unparsed_label,
    "mathtutorbench_judge_calibration": lambda r: str(r.get("normalized") or "") == "no_choice",
    "p08_calibration": lambda r: r.get("confidence") is None,
    # Extraction-LLM benchmarks: a blank extraction is scored as a wrong answer.
    "mmlu_pro": _fail_blank,
    "agieval": _fail_blank,
    "mathvista": _fail_blank,
    "olympiadbench": _fail_blank,
    "mathtutorbench_solution_correctness": _fail_blank,
    "mathtutorbench_mistake_location": _fail_blank,
    "mathtutorbench_mistake_correction": _fail_blank,
    "mathtutorbench_problem_solving": _fail_blank,
}

# What the failure marker means, printed in the report so a reader knows whether
# it is an infrastructure failure (rerun) or a model behaviour (report it).
FAIL_MEANING: dict[str, str] = {
    "mrbench_tutor": "key dimension unparsed -> silently counted as a pedagogical FAIL",
    "bea2025_tutor": "key dimension unparsed -> silently counted as a pedagogical FAIL",
    "mathtutorbench_pedagogy": "both pairwise votes failed -> win_score=None -> counted as a loss",
    "mathtutorbench_pedagogy_hard": "both pairwise votes failed -> win_score=None -> counted as a loss",
    "mathtutorbench_scaffolding": "both pairwise votes failed -> win_score=None -> counted as a loss",
    "mathtutorbench_scaffolding_hard": "both pairwise votes failed -> win_score=None -> counted as a loss",
    "eduguard_adversarial": "judge_error -> counted as NOT refused -> inflates ASR",
    "mmtutorbench": "rubric parse incomplete -> total score None -> counted as fail",
    "longtutor_teaching": "judge score parse returned 0 -> item scored 0 on all four dimensions",
    "longtutor_diagnosis": "model reply matched 0 or >1 diagnosis label",
    "longtutor_evidence": "empty extraction -> counted as incorrect",
    "p07_selfcheck": "round-2 response missing (upstream throttling) -> item dropped from the metric",
    "mrbench_judge": "the model under test produced an unparsable label (model behaviour, not infra)",
    "bea2025_judge": "the model under test produced an unparsable label (model behaviour, not infra)",
    "mathtutorbench_judge_calibration": "no A/B choice parsed from the model under test",
    "p08_calibration": "confidence not parsed -> item excluded from calibration",
    "mmlu_pro": "blank extraction -> counted as a wrong answer",
    "agieval": "blank extraction -> counted as a wrong answer",
    "mathvista": "blank extraction -> counted as a wrong answer",
    "olympiadbench": "blank extraction -> counted as a wrong answer",
    "mathtutorbench_solution_correctness": "blank extraction -> counted as a wrong answer",
    "mathtutorbench_mistake_location": "blank extraction -> counted as a wrong answer",
    "mathtutorbench_mistake_correction": "blank extraction -> counted as a wrong answer",
    "mathtutorbench_problem_solving": "blank extraction -> counted as a wrong answer",
}

# Detectors whose marker is a property of the model under test, not of the
# pipeline. High rates are worth printing but never make a run "unusable".
MODEL_BEHAVIOUR = {"mrbench_judge", "bea2025_judge", "mathtutorbench_judge_calibration"}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows


def dedupe(rows: Iterable[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Last row per item_id wins — same rule the runner uses on reread."""
    out: dict[str, dict[str, Any]] = {}
    for row in rows:
        item_id = row.get("item_id")
        if item_id is not None:
            out[str(item_id)] = row
    return out


def _rate(numerator: int, denominator: int) -> float:
    return round(numerator / denominator, 4) if denominator else 0.0


def audit_run(benchmark: str, model_dir: Path) -> dict[str, Any]:
    # collect_runs yields the benchmark dir itself when it holds no model dirs.
    model = "(no runs)" if model_dir.name == benchmark else model_dir.name
    topology = BENCH_TOPOLOGY.get(benchmark, "unknown")
    rec: dict[str, Any] = {
        "benchmark": benchmark,
        "model": model,
        "run_dir": str(model_dir.relative_to(ROOT)),
        "topology": topology,
        "findings": [],
        "verdict": "clean",
    }

    summary_path = model_dir / "summary.json"
    pred_path = model_dir / "predictions.jsonl"
    ext_path = model_dir / "extractions.jsonl"
    scored_path = model_dir / "scored.jsonl"

    summary: dict[str, Any] = {}
    if summary_path.exists():
        try:
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            rec["findings"].append("summary.json is not valid JSON")

    scored = list(dedupe(read_jsonl(scored_path)).values())
    predictions = dedupe(read_predictions(model_dir))
    extractions = dedupe(read_jsonl(ext_path))

    if not summary and not scored:
        rec["verdict"] = "no_artifacts"
        rec["findings"].append("no summary.json and no scored.jsonl — nothing was produced")
        return rec

    if (summary.get("extra_metrics") or {}).get("status") == "not_run":
        rec["verdict"] = "no_artifacts"
        rec["findings"].append(
            "adapter declares status=not_run: "
            f"{(summary.get('extra_metrics') or {}).get('reason')} — honest hook, no score to trust or distrust"
        )
        return rec

    if benchmark == "eduillustrate":
        return audit_eduillustrate(rec, summary, scored)

    n_expected = int(summary.get("total_items") or 0) or len(scored)
    rec["n_expected"] = n_expected
    rec["n_predictions"] = len(predictions)
    rec["n_extractions"] = len(extractions)
    rec["n_scored"] = len(scored)
    rec["accuracy"] = summary.get("accuracy")
    rec["headline"] = headline_metric(benchmark, summary)
    rec["summary_mtime"] = summary_path.stat().st_mtime if summary_path.exists() else None

    # --- predictions -------------------------------------------------------
    pred_err = sum(1 for r in predictions.values() if r.get("error"))
    pred_empty = sum(
        1 for r in predictions.values()
        if r.get("empty_response") or not str(r.get("response") or "").strip()
    )
    rec["pred_error_rate"] = _rate(pred_err, len(predictions))
    rec["pred_empty_rate"] = _rate(pred_empty, len(predictions))

    # --- extractions -------------------------------------------------------
    ext_err = sum(1 for r in extractions.values() if r.get("error"))
    ext_blank = sum(1 for r in extractions.values() if not str(r.get("extracted") or "").strip())
    zero_usage = sum(
        1 for r in extractions.values()
        if int(((r.get("usage") or {}).get("calls") or 0)) == 0
    )
    rec["ext_error_rate"] = _rate(ext_err, len(extractions))
    rec["ext_blank_rate"] = _rate(ext_blank, len(extractions))
    # Recorded, never a finding on its own: see JUDGE_USAGE_UNOBSERVABLE.
    rec["ext_zero_usage_rate"] = _rate(zero_usage, len(extractions))
    rec["judge_usage_observable"] = benchmark not in JUDGE_USAGE_UNOBSERVABLE

    # --- scoring status ----------------------------------------------------
    status_counts: dict[str, int] = {}
    for row in scored:
        key = str(row.get("score_status") or "unknown")
        status_counts[key] = status_counts.get(key, 0) + 1
    rec["status_counts"] = status_counts
    n_not_scored = len(scored) - status_counts.get("scored", 0)
    rec["not_scored_rate"] = _rate(n_not_scored, len(scored))

    # --- benchmark-specific judge/extraction failure -----------------------
    detector = FAIL_DETECTORS.get(benchmark)
    graded = [r for r in scored if r.get("score_status") == "scored"]
    judge_fail = 0
    if detector and graded:
        judge_fail = sum(1 for r in graded if detector(r))
    rec["n_graded"] = len(graded)
    rec["judge_fail_count"] = judge_fail
    rec["judge_fail_rate"] = _rate(judge_fail, len(graded))
    rec["judge_fail_meaning"] = FAIL_MEANING.get(benchmark)

    # secondary: partial pairwise votes (win-rate tasks only)
    if benchmark.startswith("mathtutorbench_") and BENCH_TOPOLOGY.get(benchmark) == "fixed_judge":
        partial = sum(1 for r in graded if _partial_winrate(r))
        rec["partial_vote_rate"] = _rate(partial, len(graded))

    # secondary: any-dimension (not just key) unparsed on tutor-generation runs
    if benchmark == "mrbench_tutor":
        rec["any_dim_unparsed_rate"] = _rate(
            sum(1 for r in graded if _labels_any_unparsed(r, MRBENCH_DIMS)), len(graded)
        )
    if benchmark == "bea2025_tutor":
        rec["any_dim_unparsed_rate"] = _rate(
            sum(1 for r in graded if _labels_any_unparsed(r, BEA_DIMS)), len(graded)
        )

    # --- degenerate headline (scorer cannot produce a valid value) ---------
    extra = summary.get("extra_metrics") or {}
    degenerate = degenerate_headline(benchmark, summary, extra, graded)
    if degenerate:
        rec["degenerate_headline"] = degenerate

    # --- sample coverage ---------------------------------------------------
    missing = []
    if summary.get("total_items") and len(scored) != int(summary["total_items"]):
        missing.append(f"scored.jsonl has {len(scored)} rows but summary.total_items={summary['total_items']}")
    if predictions and len(predictions) < n_expected:
        missing.append(f"predictions.jsonl covers {len(predictions)}/{n_expected} items")
    if extractions and topology != "rule" and len(extractions) < len(predictions):
        missing.append(f"extractions.jsonl covers {len(extractions)}/{len(predictions)} predicted items")
    for key, value in extra.items():
        if key.startswith("n_") and key.endswith("_missing") and value:
            missing.append(f"summary.extra_metrics.{key}={value}")
    rec["coverage_notes"] = missing

    # --- still running? ----------------------------------------------------
    newest_any = max(
        (p.stat().st_mtime for p in (pred_path, ext_path, scored_path, summary_path) if p.exists()),
        default=0.0,
    )
    if time.time() - newest_any < 3600:
        rec["in_progress"] = True
        rec["findings"].append(
            "an artifact was written in the last hour — this run looks like it is still going; "
            "any summary on disk is an interim number, not a result"
        )

    # --- staleness ---------------------------------------------------------
    if summary_path.exists():
        newest = max(
            (p.stat().st_mtime for p in (pred_path, ext_path, scored_path) if p.exists()),
            default=0.0,
        )
        if newest > summary_path.stat().st_mtime + 60:
            rec["stale_summary"] = True
            rec["findings"].append(
                "summary.json is older than predictions/extractions — the score does not "
                "reflect the artifacts on disk; rerun with --score-only"
            )

    # --- verdict -----------------------------------------------------------
    verdict = "clean"

    def escalate(level: str) -> None:
        nonlocal verdict
        order = {"clean": 0, "caveat": 1, "unusable": 2}
        if order[level] > order[verdict]:
            verdict = level

    if rec.get("degenerate_headline"):
        rec["findings"].append(f"degenerate headline: {rec['degenerate_headline']}")
        escalate("unusable")

    fail_rate = rec["judge_fail_rate"]
    if detector and fail_rate >= 0.005:
        label = "model behaviour" if benchmark in MODEL_BEHAVIOUR else "pipeline failure"
        rec["findings"].append(
            f"{fail_rate:.1%} of graded items hit the failure marker "
            f"({FAIL_MEANING.get(benchmark)}) [{label}]"
        )
        if benchmark in MODEL_BEHAVIOUR:
            if fail_rate >= CAVEAT_RATE:
                escalate("caveat")
        elif fail_rate >= UNUSABLE_RATE:
            escalate("unusable")
        elif fail_rate >= CAVEAT_RATE:
            escalate("caveat")

    if rec["not_scored_rate"] >= UNUSABLE_RATE:
        rec["findings"].append(f"{rec['not_scored_rate']:.1%} of rows never reached score_status=scored")
        escalate("unusable")
    elif rec["not_scored_rate"] >= CAVEAT_RATE:
        rec["findings"].append(f"{rec['not_scored_rate']:.1%} of rows never reached score_status=scored")
        escalate("caveat")

    if rec["pred_error_rate"] >= UNUSABLE_RATE or rec["pred_empty_rate"] >= UNUSABLE_RATE:
        rec["findings"].append(
            f"predictions: {rec['pred_error_rate']:.1%} errored, {rec['pred_empty_rate']:.1%} empty"
        )
        escalate("unusable")
    elif rec["pred_error_rate"] >= CAVEAT_RATE or rec["pred_empty_rate"] >= CAVEAT_RATE:
        rec["findings"].append(
            f"predictions: {rec['pred_error_rate']:.1%} errored, {rec['pred_empty_rate']:.1%} empty"
        )
        escalate("caveat")

    if rec["ext_error_rate"] >= CAVEAT_RATE:
        rec["findings"].append(f"{rec['ext_error_rate']:.1%} of extraction rows carry an error")
        escalate("unusable" if rec["ext_error_rate"] >= UNUSABLE_RATE else "caveat")

    # Coverage gaps only matter above the noise floor: one or two items lost to a
    # transient 5xx does not make a 12k-item run untrustworthy, and the affected
    # items already show up in ``not_scored_rate``.
    if missing:
        rec["findings"].extend(missing)
        worst_gap = max(
            [
                _rate(n_expected - len(predictions), n_expected) if predictions else 0.0,
                _rate(len(predictions) - len(extractions), n_expected)
                if extractions and topology != "rule"
                else 0.0,
            ]
            + [
                _rate(int(v), n_expected)
                for k, v in extra.items()
                if k.startswith("n_") and k.endswith("_missing") and isinstance(v, (int, float)) and v
            ]
        )
        rec["worst_coverage_gap"] = worst_gap
        if worst_gap >= UNUSABLE_RATE:
            escalate("unusable")
        elif worst_gap >= CAVEAT_RATE:
            escalate("caveat")

    if n_expected and n_expected < 20:
        rec["findings"].append(
            f"smoke run (n={n_expected}) — a sample this small is a plumbing check, not a score"
        )
        escalate("caveat")

    if rec.get("in_progress") or rec.get("stale_summary"):
        escalate("caveat")

    rec["verdict"] = verdict
    return rec


def audit_eduillustrate(
    rec: dict[str, Any], summary: dict[str, Any], scored: list[dict[str, Any]]
) -> dict[str, Any]:
    """EduIllustrate is produced by its own generator, with its own row schema.

    ``status`` (judged / render failure) replaces ``score_status``; the headline
    ``overall_mean_judged_only`` deliberately drops render failures, i.e. it is a
    survivor-biased mean. That is not a silent failure — the summary says so and
    also publishes ``overall_mean_all_items`` — but the caveat has to travel with
    the number.
    """
    total = int(summary.get("total_items") or len(scored))
    judged = int(summary.get("judged") or sum(1 for r in scored if r.get("status") == "judged"))
    render_failures = int(summary.get("render_failures") or 0)
    rec.update(
        n_expected=total,
        n_scored=len(scored),
        n_graded=judged,
        headline=summary.get("overall_mean_judged_only"),
        headline_all_items=summary.get("overall_mean_all_items"),
        judge_fail_count=render_failures,
        judge_fail_rate=_rate(render_failures, total),
        judge_fail_meaning="render failure -> item not sent to the judge, dropped from overall_mean_judged_only",
        judge_usage_observable=False,
        not_scored_rate=_rate(total - judged, total),
    )
    if render_failures:
        rec["findings"].append(
            f"{render_failures}/{total} items failed to render and were never judged; the headline "
            "overall_mean_judged_only is survivor-biased — quote overall_mean_all_items instead"
        )
        rec["verdict"] = "unusable" if rec["judge_fail_rate"] >= UNUSABLE_RATE else "caveat"
    if summary.get("judge_is_substitute"):
        rec["findings"].append(
            f"substitute judge ({summary.get('judge_model')}), not the paper's Gemini 3.0 Pro — "
            "internal comparison only, never a leaderboard number"
        )
        if rec["verdict"] == "clean":
            rec["verdict"] = "caveat"
    return rec


def headline_metric(benchmark: str, summary: dict[str, Any]) -> Any:
    """The number a reader would quote for this run."""
    extra = summary.get("extra_metrics") or {}
    if benchmark == "p07_selfcheck":
        return extra.get("score_10")
    if benchmark in ("mrbench_tutor", "bea2025_tutor"):
        return extra.get("pass_rate")
    if benchmark == "eduguard_adversarial":
        return extra.get("attack_success_rate", summary.get("accuracy"))
    if benchmark == "eduguard_sata":
        return (extra.get("overall") or {}).get("rfs")
    if benchmark == "mmtutorbench":
        return extra.get("average_total_score_0_to_6")
    if benchmark == "longtutor_teaching":
        return (extra.get("judge_scores") or {}).get("average")
    if benchmark == "edubench":
        return (extra.get("overall") or {}).get("mean_overall_score")
    if benchmark == "eduillustrate":
        return summary.get("overall_mean_judged_only")
    if benchmark == "mathtutorbench_socratic":
        return extra.get("avg_bleu", summary.get("accuracy"))
    if benchmark == "bea2025_judge":
        return extra.get("recommended_judge_score", summary.get("accuracy"))
    return summary.get("accuracy")


def degenerate_headline(
    benchmark: str, summary: dict[str, Any], extra: dict[str, Any], graded: list[dict[str, Any]]
) -> str | None:
    """A headline that no model answer could have produced — the scorer is broken."""
    if benchmark == "longtutor_teaching":
        scores = extra.get("judge_scores") or {}
        if scores and all(float(v or 0) == 0.0 for v in scores.values()):
            return (
                "every rubric dimension averages exactly 0.0 while the judge returned "
                "well-formed JSON — the score parser, not the model, is at fault"
            )
    if extra.get("status") == "not_run":
        return f"adapter reports status=not_run ({extra.get('reason')})"
    if summary.get("total_items") == 0:
        return "total_items = 0"
    return None


def cross_model_flags(records: list[dict[str, Any]]) -> None:
    """Flag benchmarks whose headline cannot separate models (13-check wording)."""
    by_bench: dict[str, list[tuple[str, float]]] = {}
    for rec in records:
        if rec["benchmark"] not in RATE_HEADLINE or rec["verdict"] == "no_artifacts":
            continue
        value = rec.get("headline")
        if isinstance(value, (int, float)):
            by_bench.setdefault(rec["benchmark"], []).append((rec["model"], float(value)))
    for benchmark, pairs in by_bench.items():
        clean = [v for m, v in pairs if not m.startswith("_")]
        if len(clean) < 4:
            continue
        sd = statistics.pstdev(clean)
        mean = statistics.fmean(clean)
        flags = []
        if mean >= CEILING:
            flags.append("ceiling")
        if mean <= FLOOR:
            flags.append("floor")
        if sd < MIN_SD:
            flags.append("low_variance")
        if not flags:
            continue
        for rec in records:
            if rec["benchmark"] != benchmark:
                continue
            rec["variance_restricted"] = True
            rec["cross_model_sd"] = round(sd, 4)
            rec["cross_model_mean"] = round(mean, 4)
            rec["variance_flags"] = flags
            rec["findings"].append(
                f"variance_restricted ({'+'.join(flags)}): across {len(clean)} models the "
                f"headline mean={mean:.3f} sd={sd:.3f} — this benchmark barely discriminates "
                "models; do not let it drive a mapping decision"
            )
            if rec["verdict"] == "clean":
                rec["verdict"] = "caveat"


def collect_runs(only: str | None) -> list[tuple[str, Path]]:
    runs: list[tuple[str, Path]] = []
    for bench_dir in sorted(EVAL_ROOT.iterdir()):
        if not bench_dir.is_dir() or bench_dir.name.startswith("_"):
            continue
        if only and bench_dir.name != only:
            continue
        model_dirs = [d for d in sorted(bench_dir.iterdir()) if d.is_dir() and not d.name.startswith("_")]
        if not model_dirs:
            runs.append((bench_dir.name, bench_dir))  # benchmark with no runs at all
            continue
        for model_dir in model_dirs:
            runs.append((bench_dir.name, model_dir))
    return runs


def render_markdown(records: list[dict[str, Any]], stamp: str) -> str:
    order = {"unusable": 0, "caveat": 1, "no_artifacts": 2, "clean": 3}
    ranked = sorted(records, key=lambda r: (order[r["verdict"]], -float(r.get("judge_fail_rate") or 0), r["benchmark"]))
    counts = {k: sum(1 for r in records if r["verdict"] == k) for k in order}

    lines = [
        f"# Eval artifact audit — {stamp}",
        "",
        "Generated by `scripts/audit_eval_artifacts.py` (offline, idempotent). It hunts for",
        "*silent failures*: runs that finished, wrote a summary, and produced a number that",
        "is not a measurement of the model.",
        "",
        f"- runs audited: **{len(records)}**",
        f"- `unusable` (score is fake, rerun required): **{counts['unusable']}**",
        f"- `caveat` (usable only with the caveat printed next to it): **{counts['caveat']}**",
        f"- `clean`: **{counts['clean']}**",
        f"- `no_artifacts` (directory exists, nothing produced): **{counts['no_artifacts']}**",
        "",
        "## Verdicts",
        "",
        "| verdict | benchmark | model | headline | judge/extract fail | not scored | findings |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for rec in ranked:
        headline = rec.get("headline")
        head = f"{headline:.4f}" if isinstance(headline, (int, float)) else "-"
        findings = "; ".join(rec["findings"])[:300] or "-"
        lines.append(
            f"| `{rec['verdict']}` | {rec['benchmark']} | {rec['model']} | {head} | "
            f"{float(rec.get('judge_fail_rate') or 0):.1%} | {float(rec.get('not_scored_rate') or 0):.1%} | "
            f"{findings.replace('|', '/')} |"
        )

    lines += ["", "## Unusable runs, in detail", ""]
    unusable = [r for r in ranked if r["verdict"] == "unusable"]
    if not unusable:
        lines.append("None.")
    for rec in unusable:
        lines += [
            f"### `{rec['benchmark']}` / `{rec['model']}`",
            "",
            f"- run dir: `{rec['run_dir']}`",
            f"- headline as written: `{rec.get('headline')}`",
            f"- graded items: {rec.get('n_graded')} of {rec.get('n_expected')}",
            f"- failure marker: {rec.get('judge_fail_meaning') or 'n/a'}",
            f"- failure rate: {float(rec.get('judge_fail_rate') or 0):.1%}",
            "- findings:",
        ]
        lines += [f"  - {f}" for f in rec["findings"]]
        lines.append("")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--benchmark", default=None, help="audit a single benchmark")
    parser.add_argument("--out-dir", type=Path, default=AUDIT_DIR)
    parser.add_argument("--stamp", default=date.today().isoformat())
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--gate", action="store_true", help="(default behaviour) exit 1 when any run is unusable")
    args = parser.parse_args()

    records = [audit_run(bench, model_dir) for bench, model_dir in collect_runs(args.benchmark)]
    cross_model_flags(records)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = args.out_dir / f"audit_{args.stamp}.jsonl"
    with jsonl_path.open("w", encoding="utf-8") as fh:
        for rec in sorted(records, key=lambda r: (r["benchmark"], r["model"])):
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    (args.out_dir / "summary.md").write_text(render_markdown(records, args.stamp), encoding="utf-8")

    counts: dict[str, int] = {}
    for rec in records:
        counts[rec["verdict"]] = counts.get(rec["verdict"], 0) + 1
    print(f"audited {len(records)} runs -> {jsonl_path.relative_to(ROOT)}")
    for verdict in ("unusable", "caveat", "clean", "no_artifacts"):
        print(f"  {verdict:12s} {counts.get(verdict, 0)}")
    if args.verbose:
        for rec in records:
            if rec["verdict"] in ("unusable", "caveat"):
                print(f"\n[{rec['verdict']}] {rec['benchmark']}/{rec['model']}")
                for finding in rec["findings"]:
                    print(f"    - {finding}")
    return 1 if counts.get("unusable") else 0


if __name__ == "__main__":
    sys.exit(main())
