from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from eval.base import BenchmarkAdapter  # noqa: E402
from eval.predictions_io import write_predictions  # noqa: E402
from eval.runner import (  # noqa: E402
    prediction_fingerprints,
    run_extractions,
    run_predictions,
)
from eval.report import write_jsonl  # noqa: E402
import materialize_eval_suites as materializer  # noqa: E402


class DummyAdapter(BenchmarkAdapter):
    name = "dummy"

    def load_items(self, limit=None, offset=0):
        return []

    def build_messages(self, item):
        return [{"role": "user", "content": item["text"]}]

    def extract_answer(self, item, response, client, model):
        client.extract_calls += 1
        return response.strip()

    def score(self, extracted, item):
        return {"correct": extracted == item["gold"], "normalized": extracted, "gold": item["gold"]}


class FakeClient:
    def __init__(self, response: str = "A") -> None:
        self.response = response
        self.chat_calls = 0
        self.extract_calls = 0

    def reset_usage_window(self) -> None:
        pass

    def chat(self, messages, model, max_tokens, timeout):
        self.chat_calls += 1
        return self.response

    def read_last_reasoning(self) -> str:
        return ""

    def read_usage_window(self) -> dict[str, int]:
        return {"calls": 1}


def _item(text: str = "question") -> dict[str, Any]:
    return {"item_id": "one", "text": text, "gold": "A", "image_paths": []}


def _prediction_context(**updates: Any) -> dict[str, Any]:
    base = {
        "schema_version": 1,
        "benchmark": "dummy",
        "model": "model",
        "provider": "test",
        "base_url": "https://example.test",
        "chat_path": "/chat",
        "generation_params": {},
        "max_tokens": None,
        "input_variant": "standard",
    }
    base.update(updates)
    return base


def test_prediction_fingerprint_is_stable_and_identity_sensitive() -> None:
    adapter = DummyAdapter()
    item = _item()
    first = prediction_fingerprints(adapter, item, _prediction_context())[:2]
    same = prediction_fingerprints(adapter, item, _prediction_context())[:2]
    changed_prompt = prediction_fingerprints(adapter, _item("changed"), _prediction_context())[:2]
    changed_provider = prediction_fingerprints(
        adapter, item, _prediction_context(provider="other")
    )[:2]
    changed_model = prediction_fingerprints(
        adapter, item, _prediction_context(model="other-model")
    )[:2]
    changed_params = prediction_fingerprints(
        adapter, item, _prediction_context(generation_params={"temperature": 0.2})
    )[:2]

    adapter.build_messages = lambda row: [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": row["text"]},
                {"type": "image_url", "image_url": {"url": row["image_url"]}},
            ],
        }
    ]
    image_item = {**item, "image_url": "data:image/png;base64,AAAA"}
    changed_image_item = {**image_item, "image_url": "data:image/png;base64,BBBB"}
    image_identity = prediction_fingerprints(adapter, image_item, _prediction_context())[:2]
    changed_image = prediction_fingerprints(
        adapter, changed_image_item, _prediction_context()
    )[:2]

    assert first == same
    assert first[0] != changed_prompt[0]
    assert first[1] != changed_provider[1]
    assert first[1] != changed_model[1]
    assert first[1] != changed_params[1]
    assert image_identity[0] != changed_image[0]


def test_cross_suite_prediction_reuse_requires_complete_matching_identity(tmp_path: Path) -> None:
    adapter = DummyAdapter()
    item = _item()
    context = _prediction_context()
    source = tmp_path / "full"
    target = tmp_path / "mini"
    source_client = FakeClient()
    _, first_stats = run_predictions(
        adapter, [item], source_client, source / "predictions.jsonl", "model",
        1, 0, 10, 0, 0, None, identity_context=context,
    )
    target_client = FakeClient()
    rows, second_stats = run_predictions(
        adapter, [item], target_client, target / "predictions.jsonl", "model",
        1, 0, 10, 0, 0, None, identity_context=context, reuse_dirs=[source],
    )

    assert source_client.chat_calls == 1
    assert first_stats["new_prediction_calls"] == 1
    assert target_client.chat_calls == 0
    assert second_stats["reused_cross_suite"] == 1
    assert rows["one"]["reused_from"] == str(source.resolve())


def test_legacy_or_changed_prediction_is_not_reused_cross_suite(tmp_path: Path) -> None:
    adapter = DummyAdapter()
    item = _item()
    legacy = tmp_path / "legacy"
    write_predictions(legacy, [{"item_id": "one", "model": "model", "response": "legacy"}])
    client = FakeClient("new")
    rows, stats = run_predictions(
        adapter, [item], client, tmp_path / "target" / "predictions.jsonl", "model",
        1, 0, 10, 0, 0, None,
        identity_context=_prediction_context(provider="changed"), reuse_dirs=[legacy],
    )

    assert client.chat_calls == 1
    assert stats["reused_cross_suite"] == 0
    assert rows["one"]["response"] == "new"


def test_extraction_reuses_only_same_judge_identity(tmp_path: Path) -> None:
    adapter = DummyAdapter()
    prediction = {
        "item_id": "one",
        "response": "A",
        "prediction_identity_sha256": "prediction-v1",
    }
    source = tmp_path / "judge-a"
    context_a = {"schema_version": 1, "extractor_model": "extractor", "judge_model": "judge-a"}
    client_a = FakeClient()
    _, first = run_extractions(
        adapter, [_item()], {"one": prediction}, client_a, source / "extractions.jsonl",
        "extractor", judge_model="judge-a", identity_context=context_a,
    )
    same_client = FakeClient()
    _, same = run_extractions(
        adapter, [_item()], {"one": prediction}, same_client,
        tmp_path / "same" / "extractions.jsonl", "extractor", judge_model="judge-a",
        identity_context=context_a, reuse_dirs=[source],
    )
    changed_client = FakeClient()
    _, changed = run_extractions(
        adapter, [_item()], {"one": prediction}, changed_client,
        tmp_path / "changed" / "extractions.jsonl", "extractor", judge_model="judge-b",
        identity_context={**context_a, "judge_model": "judge-b"}, reuse_dirs=[source],
    )

    assert first["new_extraction_calls"] == 1
    assert same["reused_cross_suite"] == 1 and same_client.extract_calls == 0
    assert changed["reused_cross_suite"] == 0 and changed_client.extract_calls == 1


def test_suite_manifests_have_unique_item_ids() -> None:
    for suite in ("mini_selection_v2", "frontier_selection_v1"):
        manifest = json.loads((ROOT / "data" / suite / "selection_manifest.json").read_text())
        for metadata in manifest["benchmarks"].values():
            ids = [line for line in (ROOT / metadata["item_list"]).read_text().splitlines() if line]
            assert len(ids) == len(set(ids)) == metadata["selected_count"]


def test_frozen_suite_overlap_matches_incremental_run_contract() -> None:
    def selected_pairs(name: str) -> tuple[set[tuple[str, str]], dict[str, int]]:
        manifest = json.loads((ROOT / "data" / name / "selection_manifest.json").read_text())
        pairs = set()
        for benchmark, metadata in manifest["benchmarks"].items():
            ids = (ROOT / metadata["item_list"]).read_text().splitlines()
            pairs.update((benchmark, item_id) for item_id in ids if item_id)
        fixed = {row["benchmark"]: row["count"] for row in manifest["fixed_full"]}
        return pairs, fixed

    mini, mini_fixed = selected_pairs("mini_selection_v2")
    frontier, frontier_fixed = selected_pairs("frontier_selection_v1")
    fixed_overlap = sum(
        min(count, frontier_fixed.get(benchmark, 0))
        for benchmark, count in mini_fixed.items()
    )
    overlap = len(mini & frontier) + fixed_overlap
    frontier_total = len(frontier) + sum(frontier_fixed.values())

    assert overlap == 1282
    assert frontier_total - overlap == 3637


def test_materializer_builds_complete_view_without_model_calls(tmp_path: Path, monkeypatch) -> None:
    source = tmp_path / "full"
    target = tmp_path / "suite"
    source.mkdir()
    (source / "summary.json").write_text(
        json.dumps(
            {
                "benchmark": "dummy",
                "model": "model",
                "extractor_model": "extractor",
                "judge_model": None,
                "run_status": "complete",
            }
        )
    )
    predictions = [
        {"item_id": "one", "response": "A", "prediction_identity_sha256": "p1"},
        {"item_id": "two", "response": "B", "prediction_identity_sha256": "p2"},
    ]
    write_predictions(source, predictions)
    write_jsonl(
        source / "extractions.jsonl",
        [
            {"item_id": "one", "extracted": "A", "extractor_model": "extractor"},
            {"item_id": "two", "extracted": "B", "extractor_model": "extractor"},
        ],
    )
    write_jsonl(
        source / "scored.jsonl",
        [
            {"item_id": "one", "score_status": "scored", "correct": True, "buckets": {}, "gold": "A"},
            {"item_id": "two", "score_status": "scored", "correct": True, "buckets": {}, "gold": "B"},
        ],
    )
    item_list = tmp_path / "items.txt"
    item_list.write_text("one\ntwo\n")
    adapter = DummyAdapter()
    adapter.load_items = lambda limit=None, offset=0: [_item(), {**_item("second"), "item_id": "two", "gold": "B"}]
    monkeypatch.setattr(materializer, "suite_item_list", lambda suite, benchmark: item_list)
    monkeypatch.setattr(materializer, "fixed_full_entry", lambda suite, benchmark: None)
    monkeypatch.setattr(materializer, "load_manifest", lambda suite: {"version": "test-v1"})
    monkeypatch.setattr(materializer, "run_dir", lambda *args: target)
    monkeypatch.setattr(materializer, "_get_adapter", lambda benchmark: adapter)

    summary = materializer.materialize_benchmark(source, "mini_v2", "dummy")

    assert summary["run_status"] == "complete"
    assert summary["total_items"] == summary["scored"] == 2
    assert summary["execution_stats"]["predictions"]["new_prediction_calls"] == 0
    assert json.loads((target / "summary.json").read_text())["materialized_from"]
    assert "测量套件：mini_v2" in (target / "report.html").read_text()
