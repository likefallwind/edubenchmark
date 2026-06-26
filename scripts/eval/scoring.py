"""Answer normalization and comparison helpers.

The MathVista-specific logic here is ported from the official
``evaluation/calculate_score.py`` so scores stay comparable, but reimplemented in
the standard library only (no ``python-Levenshtein`` dependency). Other benchmark
adapters can reuse ``edit_distance`` / ``get_most_similar`` or add their own.
"""

from __future__ import annotations

import re
from typing import Any


def edit_distance(a: str, b: str) -> int:
    """Levenshtein distance (iterative, two-row), stdlib only."""
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    previous = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        current = [i]
        for j, cb in enumerate(b, 1):
            insert = current[j - 1] + 1
            delete = previous[j] + 1
            substitute = previous[j - 1] + (ca != cb)
            current.append(min(insert, delete, substitute))
        previous = current
    return previous[-1]


def get_most_similar(prediction: str, choices: list[str]) -> str:
    """Return the choice with the smallest edit distance to ``prediction``."""
    distances = [edit_distance(prediction, choice) for choice in choices]
    return choices[distances.index(min(distances))]


def normalize_extracted_answer(
    extraction: Any,
    choices: list[str] | None,
    question_type: str,
    answer_type: str,
    precision: Any,
    ignore_empty_extractions: bool = False,
) -> Any:
    """Normalize an extracted answer to match the expected answer type.

    Mirrors MathVista's ``normalize_extracted_answer``.
    """
    if question_type == "multi_choice":
        choices = choices or []
        if isinstance(extraction, str):
            extraction = extraction.strip()
        else:
            try:
                extraction = str(extraction)
            except Exception:
                extraction = ""

        if ignore_empty_extractions and not extraction:
            return None

        # extract "A" from "(A) text"
        letter = re.findall(r"\(([a-zA-Z])\)", extraction)
        if letter:
            extraction = letter[0].upper()

        sequential_characters = [chr(ord("A") + i) for i in range(len(choices))]
        if extraction in sequential_characters:
            option_index = sequential_characters.index(extraction)
            normalized_extraction = choices[option_index]
        elif choices:
            normalized_extraction = get_most_similar(extraction, choices)
        else:
            normalized_extraction = None

    elif answer_type == "integer":
        try:
            normalized_extraction = str(int(float(extraction)))
        except Exception:
            normalized_extraction = None

    elif answer_type == "float":
        try:
            normalized_extraction = str(round(float(extraction), int(precision)))
        except Exception:
            normalized_extraction = None

    elif answer_type == "list":
        try:
            normalized_extraction = str(extraction)
        except Exception:
            normalized_extraction = None

    else:
        normalized_extraction = str(extraction).strip() if extraction is not None else None

    return normalized_extraction


def safe_equal(prediction: Any, answer: Any) -> bool:
    """Equality that never raises."""
    try:
        return bool(prediction == answer)
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Classification metrics (stdlib reimplementations of sklearn semantics).
# Used by the MathTutorBench closed-form tasks (solution_correctness uses the
# binary form; mistake_location uses the multiclass F1 form) so the harness
# does not need scikit-learn. Verified to match
# ``sklearn.metrics.{precision,recall,f1}_score`` on the relevant cases.
# ---------------------------------------------------------------------------


def binary_prf1(targets: list[bool], preds: list[bool]) -> dict[str, float]:
    """Accuracy + precision/recall/F1 for a binary task (positive label = True).

    Mirrors ``sklearn`` with ``pos_label=True`` and ``zero_division=0``.
    """
    n = len(targets)
    if n == 0:
        return {"accuracy": 0.0, "precision": 0.0, "recall": 0.0, "f1": 0.0}
    tp = sum(1 for t, p in zip(targets, preds) if t and p)
    fp = sum(1 for t, p in zip(targets, preds) if (not t) and p)
    fn = sum(1 for t, p in zip(targets, preds) if t and (not p))
    correct = sum(1 for t, p in zip(targets, preds) if t == p)
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    return {
        "accuracy": correct / n,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }


def multiclass_f1(targets: list[Any], preds: list[Any]) -> dict[str, float]:
    """F1 with micro / macro / weighted averaging over single-label predictions.

    Mirrors ``sklearn.metrics.f1_score(average=...)`` with ``zero_division=0``.
    For single-label data micro-F1 equals accuracy.
    """
    n = len(targets)
    if n == 0:
        return {"f1_micro": 0.0, "f1_macro": 0.0, "f1_weighted": 0.0}
    labels = sorted(set(targets) | set(preds), key=lambda x: (str(type(x)), x))
    macro_sum = 0.0
    weighted_sum = 0.0
    for label in labels:
        tp = sum(1 for t, p in zip(targets, preds) if t == label and p == label)
        fp = sum(1 for t, p in zip(targets, preds) if t != label and p == label)
        fn = sum(1 for t, p in zip(targets, preds) if t == label and p != label)
        support = sum(1 for t in targets if t == label)
        precision = tp / (tp + fp) if (tp + fp) else 0.0
        recall = tp / (tp + fn) if (tp + fn) else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
        macro_sum += f1
        weighted_sum += f1 * support
    micro = sum(1 for t, p in zip(targets, preds) if t == p) / n
    return {
        "f1_micro": micro,
        "f1_macro": macro_sum / len(labels) if labels else 0.0,
        "f1_weighted": weighted_sum / n,
    }


def cohen_kappa(targets: list[Any], preds: list[Any]) -> float:
    """Cohen's kappa for two single-label rating sequences (chance-corrected
    agreement). Mirrors ``sklearn.metrics.cohen_kappa_score`` for nominal labels.

    Used by the MRBench judge-calibration adapter to report how far an LLM
    judge's per-dimension labels agree with the human gold beyond chance.
    Returns 0.0 for the degenerate case where the expected agreement is 1
    (every rating identical), matching sklearn's handling.
    """
    n = len(targets)
    if n == 0:
        return 0.0
    labels = sorted(set(targets) | set(preds), key=lambda x: (str(type(x)), x))
    observed = sum(1 for t, p in zip(targets, preds) if t == p) / n
    expected = 0.0
    for label in labels:
        pt = sum(1 for t in targets if t == label) / n
        pp = sum(1 for p in preds if p == label) / n
        expected += pt * pp
    if expected >= 1.0:
        return 0.0
    return (observed - expected) / (1.0 - expected)
