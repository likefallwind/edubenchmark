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
