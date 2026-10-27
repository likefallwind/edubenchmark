from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from eval.benchmarks import student_risk  # noqa: E402


def test_judge_prompt_does_not_include_authoring_signal(monkeypatch) -> None:
    prompts: list[str] = []

    def fake_cast_vote(client, model, prompt):
        prompts.append(prompt)
        return '{"档位": 0, "理由": "只按回复判断"}'

    monkeypatch.setattr(student_risk, "cast_vote", fake_cast_vote)
    adapter = student_risk.StudentRiskV2Adapter()
    item = {
        "meta": {
            "system_prompt": "你是学习助手。",
            "turns": ["我今天想问个问题。"],
            "signal": "UNIQUE_AUTHORING_SIGNAL_SENTINEL",
        }
    }

    adapter.extract_answer(item, "可以，请说。", object(), "MiniMax-M3")

    assert len(prompts) == 2
    assert all("UNIQUE_AUTHORING_SIGNAL_SENTINEL" not in prompt for prompt in prompts)
    assert all("我今天想问个问题。" in prompt for prompt in prompts)

