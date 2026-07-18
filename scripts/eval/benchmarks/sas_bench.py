"""SAS-Bench: fine-grained short-answer scoring.

This is a dependency-free port of the official prediction and metric protocol:
https://github.com/PKU-DAIR/SAS-Bench

QWK, CCS and ECS are population agreement statistics.  They are computed for
each of the 12 subject/question-type tasks and then macro-averaged, matching the
published protocol and the SAS-Bench results already imported in this repo.
"""

from __future__ import annotations

import ast
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path
from statistics import fmean
from typing import Any

from ..base import BenchmarkAdapter, ROOT, prompt_sha256
from ..scoring import quadratic_weighted_kappa


HOMEPAGE = "https://github.com/PKU-DAIR/SAS-Bench"
DATA_DIR = ROOT / "sources" / "datasets" / "sas_bench" / "datasets"
CORRECT_ERROR = "步骤正确"
PROMPT_VERSION = "official-zero-shot-v1"

PROMPT_TEMPLATE = """请作为学科评分专家，根据以下要求对学生的作答进行专业评估：

【评估任务】
依据题目信息、参考答案及评分指南，对学生的分步解答进行精细化评分，并输出结构化评分结果。

【评分指南】
{score_guideline}

【评估材料】
- 试题内容：{question}
- 题目分值：{total}
- 错因类型：{error_type}
- 标准答案：{reference}
- 解析说明：{analysis}
- 学生作答：{student_answer}

【评估流程和要求】
1. 分步解析：
   - 按给出的学生作答步骤逐步评估
   - 对每个步骤独立给出 step_score
   - 如存在错误，只能从错因类型列表中选取一项或多项主因
2. 综合评定：
   - 汇总各步骤得分，给出整体 pred_score
3. 结果输出：
   - 只输出标准 JSON，不要输出 Markdown 或解释：
     {{
       "total": 总分,
       "pred_score": 评估总分数,
       "steps": [
         {{"step_score": 单步分数, "errors": ["错因"]}}
       ]
     }}
   - pred_score 必须在 0 到 total 之间
   - steps 的数量必须与学生作答步骤数相同
"""


def _task_sort_key(path: Path) -> tuple[int, str]:
    prefix = path.stem.split("_", 1)[0]
    return (int(prefix) if prefix.isdigit() else 10_000, path.name)


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            if not isinstance(row, dict):
                raise ValueError(f"{path}:{line_no}: expected JSON object")
            rows.append(row)
    return rows


def _as_int(value: Any, default: int = 0) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError, OverflowError):
        return default


def _json_object(text: str) -> dict[str, Any]:
    """Extract the first balanced JSON/Python object from a model reply."""
    cleaned = re.sub(r"^\s*```(?:json)?\s*|\s*```\s*$", "", text.strip(), flags=re.I)
    start = cleaned.find("{")
    if start < 0:
        raise ValueError("no JSON object found")
    depth = 0
    in_string = False
    escaped = False
    end = None
    for idx in range(start, len(cleaned)):
        char = cleaned[idx]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                end = idx + 1
                break
    candidate = cleaned[start:end] if end else cleaned[start:]
    try:
        value = json.loads(candidate)
    except json.JSONDecodeError:
        try:
            value = ast.literal_eval(candidate)
        except (SyntaxError, ValueError) as exc:
            raise ValueError("invalid grading JSON") from exc
    if isinstance(value, list) and value:
        value = value[0]
    if not isinstance(value, dict):
        raise ValueError("grading output is not an object")
    return value


def _ranks(values: list[float]) -> list[float]:
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    pos = 0
    while pos < len(order):
        end = pos + 1
        while end < len(order) and values[order[end]] == values[order[pos]]:
            end += 1
        rank = (pos + 1 + end) / 2.0
        for idx in order[pos:end]:
            ranks[idx] = rank
        pos = end
    return ranks


def _spearman(left: list[float], right: list[float]) -> float:
    if len(left) != len(right) or len(left) < 2:
        return 0.0
    x = _ranks(left)
    y = _ranks(right)
    mx, my = fmean(x), fmean(y)
    numerator = sum((a - mx) * (b - my) for a, b in zip(x, y))
    dx = sum((a - mx) ** 2 for a in x)
    dy = sum((b - my) ** 2 for b in y)
    denominator = math.sqrt(dx * dy)
    return numerator / denominator if denominator else 0.0


# QWK lives in ..scoring so ASAP 2.0 and this adapter share one implementation.
_qwk = quadratic_weighted_kappa


def _ccs(rows: list[dict[str, Any]]) -> float | None:
    """Collaborative Consistency Score from the paper's published formula.

    Each response gives holistic score weight 0.5; its available step positions
    share the remaining 0.5. Expected disagreement is the product of the gold
    and predicted tuple marginals, analogous to weighted kappa.
    """
    if not rows:
        return None
    max_steps = max(len(row["step_gold"]) for row in rows)
    max_total = max(max(row["total"], row["pred_label"]) for row in rows)
    max_step_scores = []
    for pos in range(max_steps):
        values = [0]
        for row in rows:
            if pos < len(row["step_gold"]):
                values.append(_as_int(row["step_gold"][pos].get("label")))
            if pos < len(row["step_pred"]):
                values.append(_as_int(row["step_pred"][pos].get("step_score")))
        max_step_scores.append(max(values))

    gold_tuples: list[tuple[int, ...]] = []
    pred_tuples: list[tuple[int, ...]] = []
    for row in rows:
        gold_steps = [_as_int(step.get("label")) for step in row["step_gold"]]
        pred_steps = [_as_int(step.get("step_score")) for step in row["step_pred"]]
        gold_tuples.append(tuple([row["manual_label"], *gold_steps, *([0] * (max_steps - len(gold_steps)))]))
        pred_tuples.append(tuple([row["pred_label"], *pred_steps, *([0] * (max_steps - len(pred_steps)))]))

    levels = sorted(set(gold_tuples) | set(pred_tuples))
    gold_hist = Counter(gold_tuples)
    pred_hist = Counter(pred_tuples)
    max_scores = [max_total, *max_step_scores]

    def distance(left: tuple[int, ...], right: tuple[int, ...]) -> float:
        active_steps = max(
            sum(1 for value in left[1:] if value != 0),
            sum(1 for value in right[1:] if value != 0),
            1,
        )
        value = 0.5 * ((left[0] - right[0]) / max(max_scores[0], 1)) ** 2
        step_weight = 0.5 / active_steps
        for pos in range(1, len(left)):
            if left[pos] == 0 and right[pos] == 0:
                continue
            value += step_weight * ((left[pos] - right[pos]) / max(max_scores[pos], 1)) ** 2
        return value

    observed = sum(distance(g, p) for g, p in zip(gold_tuples, pred_tuples))
    expected = sum(
        gold_hist[g] * pred_hist[p] / len(rows) * distance(g, p)
        for g in levels
        for p in levels
    )
    return 1.0 - observed / expected if expected else None


def _ecs(rows: list[dict[str, Any]], error_names: list[str]) -> tuple[float, list[float]] | tuple[None, list[None]]:
    if not rows or len(error_names) < 2:
        return None, [None, None, None]
    normalized = sorted(row["manual_label"] / max(row["total"], 1) for row in rows)
    low_cut = normalized[int(len(normalized) * 0.33)]
    high_cut = normalized[int(len(normalized) * 0.67)]
    index = {name: idx for idx, name in enumerate(error_names)}
    gold_matrix = [[0.0] * len(error_names) for _ in range(3)]
    pred_matrix = [[0.0] * len(error_names) for _ in range(3)]

    def tier(value: float) -> int:
        if value <= low_cut:
            return 0
        if value < high_cut:
            return 1
        return 2

    for row in rows:
        gold_tier = tier(row["manual_label"] / max(row["total"], 1))
        pred_tier = tier(row["pred_label"] / max(row["total"], 1))
        for step in row["step_gold"]:
            for error in step.get("errors") or []:
                if error != CORRECT_ERROR and error in index:
                    gold_matrix[gold_tier][index[error]] += 1
        for step in row["step_pred"]:
            for error in step.get("errors") or []:
                if error != CORRECT_ERROR and error in index:
                    pred_matrix[pred_tier][index[error]] += 1
    breakdown = [_spearman(pred_matrix[idx], gold_matrix[idx]) for idx in range(3)]
    return fmean(breakdown), breakdown


class SASBenchAdapter(BenchmarkAdapter):
    name = "sas_bench"
    title = "SAS-Bench · 高考短答案整体、分步与错因评分"
    homepage = HOMEPAGE
    description = (
        "SAS-Bench 包含 9 学科、12 个学科×题型子任务、1,030 道高考题和 4,109 条专家标注作答。"
        "被测模型扮演阅卷评分器，输入题目、参考答案、解析、评分细则、学生逐步作答和允许的错因类型，"
        "输出总分、逐步得分和逐步错因。\n\n"
        "官方原生指标是 QWK（整体总分一致性）、CCS（整体+步骤联合一致性）和 ECS（按低/中/高作答质量"
        "分层的错因分布一致性）。三项均先在每个子任务上计算，再对已有子任务做不加权宏平均；"
        "它们是群体一致性统计量，不是逐题 accuracy。"
    )

    def _require_data(self) -> list[Path]:
        files = sorted(DATA_DIR.glob("[0-9]*_*.jsonl"), key=_task_sort_key)
        files = [path for path in files if path.name != "error_type.jsonl"]
        if not files or not (DATA_DIR / "error_type.jsonl").exists():
            raise FileNotFoundError(
                "SAS-Bench data not prepared. Run: python scripts/eval/data/prepare_sas_bench.py"
            )
        return files

    def load_items(self, limit: int | None = None, offset: int = 0) -> list[dict[str, Any]]:
        files = self._require_data()
        taxonomy = {str(row["q_id"]): row for row in _read_jsonl(DATA_DIR / "error_type.jsonl")}
        items: list[dict[str, Any]] = []
        seen: set[str] = set()
        for path in files:
            task = path.stem
            parts = task.split("_", 2)
            q_id = parts[0]
            subject = parts[1] if len(parts) > 1 else "unknown"
            question_type = parts[2] if len(parts) > 2 else "unknown"
            tax = taxonomy.get(q_id)
            if tax is None:
                raise ValueError(f"missing error taxonomy for SAS-Bench task {task}")
            error_names = [str(row["name"]) for row in tax.get("errors") or []]
            for source in _read_jsonl(path):
                item_id = str(source.get("id") or "")
                if not item_id or item_id in seen:
                    raise ValueError(f"missing/duplicate SAS-Bench item id: {item_id!r}")
                seen.add(item_id)
                steps = source.get("steps") or []
                student_answer = "\n\n".join(
                    f"## Step {idx}\n{step.get('response', '')}" for idx, step in enumerate(steps)
                )
                text = PROMPT_TEMPLATE.format(
                    score_guideline=tax.get("guideline") or "",
                    question=source.get("question") or "",
                    total=source.get("total") or 0,
                    error_type=json.dumps(error_names, ensure_ascii=False),
                    reference=source.get("reference") or "",
                    analysis=source.get("analysis") or "",
                    student_answer=student_answer,
                )
                items.append(
                    {
                        "item_id": item_id,
                        "text": text,
                        "image_paths": [],
                        "gold": {
                            "total": _as_int(source.get("total")),
                            "manual_label": _as_int(source.get("manual_label")),
                            "steps": steps,
                        },
                        "meta": {
                            "task": task,
                            "subject": subject,
                            "question_type": question_type,
                            "error_names": error_names,
                        },
                    }
                )
        return items[offset : offset + limit if limit is not None else None]

    def extract_answer(self, item, response, client, model):
        value = _json_object(response)
        gold_steps = item["gold"]["steps"]
        raw_steps = value.get("steps") if isinstance(value.get("steps"), list) else []
        allowed = set(item["meta"]["error_names"]) | {CORRECT_ERROR}
        steps = []
        unknown_errors: list[str] = []
        for idx in range(len(gold_steps)):
            raw = raw_steps[idx] if idx < len(raw_steps) and isinstance(raw_steps[idx], dict) else {}
            errors = raw.get("errors") if isinstance(raw.get("errors"), list) else []
            normalized_errors = []
            for error in errors:
                label = str(error).strip()
                if label in allowed and label not in normalized_errors:
                    normalized_errors.append(label)
                elif label and label not in allowed:
                    unknown_errors.append(label)
            steps.append({"step_score": _as_int(raw.get("step_score")), "errors": normalized_errors})
        result = {
            "total": item["gold"]["total"],
            "pred_score": _as_int(value.get("pred_score")),
            "steps": steps,
            "reported_step_count": len(raw_steps),
            "unknown_errors": unknown_errors,
        }
        return json.dumps(result, ensure_ascii=False)

    def score(self, extracted, item):
        parsed = json.loads(extracted)
        gold = item["gold"]
        pred_steps = parsed["steps"]
        gold_steps = [
            {"label": _as_int(step.get("label")), "errors": list(step.get("errors") or [])}
            for step in gold["steps"]
        ]
        exact = (
            parsed["pred_score"] == gold["manual_label"]
            and all(
                pred.get("step_score") == target.get("label")
                and set(pred.get("errors") or []) == set(target.get("errors") or [])
                for pred, target in zip(pred_steps, gold_steps)
            )
        )
        return {
            "correct": exact,
            "normalized": parsed["pred_score"],
            "gold": gold["manual_label"],
            "total": gold["total"],
            "manual_label": gold["manual_label"],
            "pred_label": parsed["pred_score"],
            "step_gold": gold_steps,
            "step_pred": pred_steps,
            "step_count_match": parsed["reported_step_count"] == len(gold_steps),
            "unknown_errors": parsed["unknown_errors"],
            "structured_exact_match": exact,
        }

    def buckets(self, item):
        return {
            "task": item["meta"]["task"],
            "subject": item["meta"]["subject"],
            "question_type": item["meta"]["question_type"],
        }

    def extra_summary(self, scored):
        usable = [row for row in scored if row.get("score_status") == "scored"]
        by_task_rows: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in usable:
            by_task_rows[str((row.get("buckets") or {}).get("task"))].append(row)
        by_task: dict[str, dict[str, Any]] = {}
        for task, rows in sorted(by_task_rows.items(), key=lambda pair: _task_sort_key(Path(pair[0]))):
            error_names = sorted(
                {
                    str(error)
                    for row in rows
                    for step in row.get("step_gold") or []
                    for error in step.get("errors") or []
                    if error != CORRECT_ERROR
                }
            )
            qwk = _qwk([row["manual_label"] for row in rows], [row["pred_label"] for row in rows])
            ccs = _ccs(rows)
            ecs, breakdown = _ecs(rows, error_names)
            by_task[task] = {
                "n": len(rows),
                "qwk": qwk * 100 if qwk is not None else None,
                "ccs": ccs * 100 if ccs is not None else None,
                "ecs": ecs * 100 if ecs is not None else None,
                "ecs_low": breakdown[0] * 100 if breakdown[0] is not None else None,
                "ecs_medium": breakdown[1] * 100 if breakdown[1] is not None else None,
                "ecs_high": breakdown[2] * 100 if breakdown[2] is not None else None,
            }

        def macro(key: str) -> float | None:
            values = [row[key] for row in by_task.values() if isinstance(row.get(key), (int, float))]
            return fmean(values) if values else None

        return {
            "metric_note": (
                "QWK/CCS/ECS are population agreement statistics against human expert labels "
                "on a 0-100 scale, not per-item accuracy. The generic accuracy field is strict "
                "structured exact match and is diagnostic only."
            ),
            "headline_metric": "unweighted mean of each available per-subtask metric",
            "overall": {key: macro(key) for key in ("qwk", "ccs", "ecs")},
            "overall_ecs_breakdown": {
                key: macro(key) for key in ("ecs_low", "ecs_medium", "ecs_high")
            },
            "by_task": by_task,
            "audit": {
                "metric_protocol": "in-repo standard-library port of PKU-DAIR/SAS-Bench",
                "prompt_version": PROMPT_VERSION,
                "prompt_sha256": prompt_sha256(PROMPT_TEMPLATE),
                "scored_rows": len(usable),
                "tasks_present": len(by_task),
                "step_count_mismatches": sum(not row.get("step_count_match", False) for row in usable),
                "unknown_error_labels_dropped": sum(len(row.get("unknown_errors") or []) for row in usable),
            },
        }
