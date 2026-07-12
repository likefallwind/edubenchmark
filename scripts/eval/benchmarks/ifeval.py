"""IFEval adapter (P01 指令与约束遵循 direct measure).

IFEval (Zhou et al. 2023, arXiv:2311.07911): 541 prompts, each carrying one or
more *verifiable* instructions ("answer in exactly 3 bullet points", "no
commas", "wrap in double quotes", ...). Scoring is entirely rule-based via the
vendored official checker modules (``sources/datasets/ifeval/
instruction_following_eval/``) — no judge and no extraction LLM, which is the
whole point: the construct-review matrix showed EduBench's judge-scored
"instruction following" metric carries no model-ranking information beyond the
knowledge metrics (R13), so P01 needs a rule-scored measurement.

Headline ``accuracy`` = official *prompt-level strict* accuracy (all
instructions in a prompt followed on the raw response). ``extra_metrics`` adds
the other three official numbers (prompt-loose, instruction-strict,
instruction-loose); loose retries the checks on the official 8 response
variants (strip first/last line, remove ``*``).
"""

from __future__ import annotations

import json
import sys
from functools import lru_cache
from typing import Any

from ..base import ROOT, BenchmarkAdapter
from ..minimax_client import MiniMaxClient

DATA_PATH = ROOT / "sources" / "datasets" / "ifeval" / "data" / "input_data.jsonl"
CHECKER_DIR = ROOT / "sources" / "datasets" / "ifeval"


@lru_cache(maxsize=1)
def _registry():
    """Import the vendored official checker (needs nltk/langdetect/immutabledict)."""
    if not (CHECKER_DIR / "instruction_following_eval" / "instructions_registry.py").is_file():
        raise SystemExit(
            "IFEval checker not materialized; run "
            "scripts/eval/data/fetch_eval_datasets.py --benchmark ifeval"
        )
    if str(CHECKER_DIR) not in sys.path:
        sys.path.insert(0, str(CHECKER_DIR))
    from instruction_following_eval import instructions_registry  # noqa: PLC0415

    return instructions_registry


def _loose_variants(response: str) -> list[str]:
    """The official 8 response variants tried by the loose metric."""
    lines = response.split("\n")
    remove_first = "\n".join(lines[1:]).strip()
    remove_last = "\n".join(lines[:-1]).strip()
    remove_both = "\n".join(lines[1:-1]).strip()
    variants = [response, remove_first, remove_last, remove_both]
    return variants + [v.replace("*", "") for v in variants]


def _check(item: dict[str, Any], response: str, loose: bool) -> list[bool]:
    registry = _registry()
    meta = item["meta"]
    followed: list[bool] = []
    for index, instruction_id in enumerate(meta["instruction_id_list"]):
        instruction = registry.INSTRUCTION_DICT[instruction_id](instruction_id)
        kwargs = {k: v for k, v in (meta["kwargs"][index] or {}).items() if v is not None}
        instruction.build_description(**kwargs)
        args = instruction.get_instruction_args()
        if args and "prompt" in args:
            instruction.build_description(prompt=item["text"])
        candidates = _loose_variants(response) if loose else [response]
        followed.append(
            any(c.strip() and instruction.check_following(c) for c in candidates)
        )
    return followed


class IFEvalAdapter(BenchmarkAdapter):
    name = "ifeval"
    title = "IFEval（可验证指令遵循，规则判分，P01 直接测量）"
    homepage = "https://github.com/google-research/google-research/tree/master/instruction_following_eval"
    description = (
        "541 条 prompt，每条带若干可机器验证的硬约束（字数、格式、关键词、大小写等），"
        "官方规则代码判分——无裁判、无抽取模型。\n\n"
        "headline = 官方 prompt 级 strict accuracy（一条 prompt 的全部指令在原始回复上全部满足）；"
        "extra_metrics 含官方另外三个口径（prompt-loose / instruction-strict / instruction-loose）。\n\n"
        "接入动机（R13）：edubench 裁判打的“指令遵循”分与知识指标在模型排名上信息重合，"
        "P01 的直接测量必须走规则判分。"
    )

    def load_items(self, limit: int | None = None, offset: int = 0) -> list[dict[str, Any]]:
        if not DATA_PATH.is_file():
            raise SystemExit(
                "IFEval data missing; run scripts/eval/data/fetch_eval_datasets.py --benchmark ifeval"
            )
        _registry()  # fail fast if checker deps are missing
        items: list[dict[str, Any]] = []
        with DATA_PATH.open(encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                row = json.loads(line)
                items.append(
                    {
                        "item_id": f"ifeval-{row['key']}",
                        "text": row["prompt"],
                        "image_paths": [],
                        "gold": None,
                        "meta": {
                            "instruction_id_list": row["instruction_id_list"],
                            "kwargs": row["kwargs"],
                        },
                    }
                )
        end = offset + limit if limit is not None else None
        return items[offset:end]

    def extract_answer(self, item: dict[str, Any], response: str, client: MiniMaxClient, model: str) -> str:
        # Rule scoring consumes the raw response; nothing to extract.
        return response

    def score(self, extracted: str, item: dict[str, Any]) -> dict[str, Any]:
        response = extracted or ""
        strict = _check(item, response, loose=False)
        loose = _check(item, response, loose=True)
        return {
            "correct": all(strict),
            "normalized": f"strict {sum(strict)}/{len(strict)}",
            "gold": "all instructions followed",
            "follow_all_loose": all(loose),
            "n_instructions": len(strict),
            "n_followed_strict": sum(strict),
            "n_followed_loose": sum(loose),
        }

    def buckets(self, item: dict[str, Any]) -> dict[str, str]:
        families = sorted({iid.split(":")[0] for iid in item["meta"]["instruction_id_list"]})
        return {"instruction_family": "+".join(families)}

    def extra_summary(self, scored: list[dict[str, Any]]) -> dict[str, Any]:
        graded = [r for r in scored if r.get("score_status") == "scored"]
        if not graded:
            return {}
        n_inst = sum(r.get("n_instructions", 0) for r in graded)
        return {
            "prompt_strict_accuracy": round(
                sum(1 for r in graded if r.get("correct")) / len(graded), 4
            ),
            "prompt_loose_accuracy": round(
                sum(1 for r in graded if r.get("follow_all_loose")) / len(graded), 4
            ),
            "instruction_strict_accuracy": round(
                sum(r.get("n_followed_strict", 0) for r in graded) / n_inst, 4
            )
            if n_inst
            else None,
            "instruction_loose_accuracy": round(
                sum(r.get("n_followed_loose", 0) for r in graded) / n_inst, 4
            )
            if n_inst
            else None,
            "n_prompts": len(graded),
            "n_instructions": n_inst,
            "scoring": "official vendored checker, rule-based, no judge",
        }
