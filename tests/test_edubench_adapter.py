from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from eval.benchmarks.edubench import (  # noqa: E402
    DEFAULT_JUDGE_MODEL,
    DIMENSIONS,
    TASK_DIMENSIONS,
    EduBenchAdapter,
    _parse_judgment,
)
from eval.report import build_summary, write_report  # noqa: E402


def test_edubench_uses_repository_standard_judge_namespace() -> None:
    adapter = EduBenchAdapter()

    assert DEFAULT_JUDGE_MODEL == "MiniMax-M3"
    assert adapter.canonical_judge_model is None
    assert adapter.resolved_judge_model("MiniMax-M2.7") == "MiniMax-M3"


def test_parse_judgment_accepts_fenced_json_and_confirmed_aliases() -> None:
    scores = {dimension: 7 for dimension in DIMENSIONS}
    scores["higher_order_ththinking_ability_development"] = scores.pop(
        "higher_order_thinking_ability_development"
    )
    parsed = _parse_judgment(f"```json\n{json.dumps({'scores': scores})}\n```")

    assert parsed is not None
    assert parsed["scores"]["higher_order_thinking_ability_development"] == 7
    assert set(parsed["scores"]) == set(DIMENSIONS)


def test_parse_judgment_rejects_missing_or_out_of_range_scores() -> None:
    missing = {dimension: 7 for dimension in DIMENSIONS[:-1]}
    out_of_range = {dimension: 7 for dimension in DIMENSIONS}
    out_of_range[DIMENSIONS[0]] = 11

    assert _parse_judgment(json.dumps({"scores": missing})) is None
    assert _parse_judgment(json.dumps({"scores": out_of_range})) is None


def test_score_is_continuous_and_uses_task_specific_dimensions() -> None:
    adapter = EduBenchAdapter()
    scores = {dimension: float(index) for index, dimension in enumerate(DIMENSIONS, 1)}
    payload = json.dumps({"judge_model": "judge", "scores": scores, "rationale": "ok"})
    item = {"meta": {"task": "PLS"}}

    result = adapter.score(payload, item)

    assert result["correct"] is None
    assert result["overall_score"] == sum(scores.values()) / len(scores)
    expected = sum(scores[key] for key in TASK_DIMENSIONS["PLS"]) / len(TASK_DIMENSIONS["PLS"])
    assert result["scenario_score"] == expected


def test_comparable_prompt_set_keeps_existing_ids_and_task_counts() -> None:
    items = EduBenchAdapter().load_items(limit=None)

    assert len(items) == 3797
    assert len({item["item_id"] for item in items}) == 3797
    assert Counter(item["meta"]["task"] for item in items) == {
        "QG": 1266,
        "IP": 1253,
        "TMG": 578,
        "PLS": 448,
        "PCC": 252,
    }
    assert all(item["meta"]["lang"] == "en" for item in items)


def test_generic_summary_does_not_turn_continuous_scores_into_zero_accuracy() -> None:
    scored = [
        {
            "item_id": "one",
            "score_status": "scored",
            "correct": None,
            "buckets": {"task": "PLS"},
            "overall_score": 8.0,
        }
    ]

    summary = build_summary("edubench", "model", scored, ["task"])

    assert summary["scored"] == 1
    assert summary["correct"] is None
    assert summary["accuracy"] is None
    assert summary["by_bucket"]["task"]["PLS"]["accuracy"] is None


def test_report_surfaces_continuous_headline_instead_of_accuracy(tmp_path: Path) -> None:
    summary = {
        "benchmark": "edubench",
        "model": "model",
        "total_items": 1,
        "scored": 1,
        "correct": None,
        "accuracy": None,
        "status_counts": {"scored": 1},
        "by_bucket": {},
        "extra_metrics": {
            "overall": {"mean_overall_score": 8.25, "mean_scenario_score": 8.5}
        },
    }
    path = tmp_path / "report.html"

    write_report(path, summary, adapter=EduBenchAdapter())

    output = path.read_text(encoding="utf-8")
    assert "总体平均分" in output and "8.250" in output
    assert "场景平均分" in output and "8.500" in output
