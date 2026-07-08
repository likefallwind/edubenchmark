"""Cluster bootstrap confidence intervals for evaluation metrics.

Shared statistical helpers for reports that compare judges / models
(``scripts/build_judge_jury_report.py`` and, later, per-benchmark summaries per
review suggestion 3.2). Pure stdlib.

Why *cluster* bootstrap: judge-calibration items are heavily grouped — one
dialogue yields up to 9 responses x 8 dimensions in MRBench — and labels within
a dialogue are correlated. Resampling individual items would understate the
variance, so the resampling unit is the cluster (``conversation_id`` for
dimension-label data, ``pair_id`` for preference pairs).

Two entry points:

- ``cluster_bootstrap_ci(rows, statistic)`` — percentile CI for one system.
- ``cluster_bootstrap_diff_ci(rows, stat_a, stat_b)`` — paired difference CI
  between two systems evaluated on the *same* items, using the same resample
  sequence for both sides (the paired design is what makes small differences
  detectable).

``rows`` is a sequence of ``(cluster_id, payload)`` tuples; ``statistic`` maps
a list of payloads to a float, or ``None`` when undefined on that resample
(e.g. Cohen's kappa with a single distinct label). ``None`` replicates are
dropped and counted in ``na_rate`` instead of being silently swallowed.
"""

from __future__ import annotations

import random
from typing import Any, Callable, Sequence

from .scoring import cohen_kappa, multiclass_f1

DEFAULT_N_BOOT = 1000
DEFAULT_SEED = 20260706
DEFAULT_ALPHA = 0.05

Rows = Sequence[tuple[Any, Any]]
Statistic = Callable[[list[Any]], float | None]


# ---------------------------------------------------------------------------
# Statistics over (gold, pred) label pairs
# ---------------------------------------------------------------------------


def agreement_stat(pairs: list[tuple[Any, Any]]) -> float | None:
    if not pairs:
        return None
    return sum(1 for g, p in pairs if g == p) / len(pairs)


def macro_f1_stat(pairs: list[tuple[Any, Any]]) -> float | None:
    if not pairs:
        return None
    golds = [g for g, _ in pairs]
    preds = [p for _, p in pairs]
    return multiclass_f1(golds, preds)["f1_macro"]


def kappa_stat(pairs: list[tuple[Any, Any]]) -> float | None:
    """Cohen's kappa; ``None`` when chance agreement is degenerate (fewer than
    two distinct labels on either side), matching the n/a convention above."""
    if not pairs:
        return None
    golds = [g for g, _ in pairs]
    preds = [p for _, p in pairs]
    if len(set(golds)) < 2 or len(set(preds)) < 2:
        return None
    return cohen_kappa(golds, preds)


# ---------------------------------------------------------------------------
# Cluster bootstrap
# ---------------------------------------------------------------------------


def _group_clusters(rows: Rows) -> list[list[Any]]:
    grouped: dict[Any, list[Any]] = {}
    for cluster_id, payload in rows:
        grouped.setdefault(cluster_id, []).append(payload)
    # Sort for determinism regardless of input order.
    return [grouped[key] for key in sorted(grouped, key=str)]


def _quantile(sorted_values: list[float], q: float) -> float:
    """Linear-interpolation quantile of an ascending list (numpy default)."""
    if not sorted_values:
        raise ValueError("no values")
    if len(sorted_values) == 1:
        return sorted_values[0]
    pos = q * (len(sorted_values) - 1)
    lo = int(pos)
    hi = min(lo + 1, len(sorted_values) - 1)
    frac = pos - lo
    return sorted_values[lo] * (1 - frac) + sorted_values[hi] * frac


def _resample_payloads(clusters: list[list[Any]], rng: random.Random) -> list[Any]:
    payloads: list[Any] = []
    n = len(clusters)
    for _ in range(n):
        payloads.extend(clusters[rng.randrange(n)])
    return payloads


def _ci_result(point: float | None, values: list[float], n_boot: int, alpha: float) -> dict[str, Any]:
    result: dict[str, Any] = {
        "point": None if point is None else round(point, 4),
        "ci_low": None,
        "ci_high": None,
        "n_boot": n_boot,
        "na_rate": round(1 - len(values) / n_boot, 4) if n_boot else None,
    }
    if values:
        values = sorted(values)
        result["ci_low"] = round(_quantile(values, alpha / 2), 4)
        result["ci_high"] = round(_quantile(values, 1 - alpha / 2), 4)
    return result


def cluster_bootstrap_ci(
    rows: Rows,
    statistic: Statistic,
    n_boot: int = DEFAULT_N_BOOT,
    seed: int = DEFAULT_SEED,
    alpha: float = DEFAULT_ALPHA,
) -> dict[str, Any]:
    """Percentile bootstrap CI for ``statistic`` with clusters as the unit."""
    clusters = _group_clusters(rows)
    if not clusters:
        return _ci_result(None, [], 0, alpha)
    point = statistic([p for c in clusters for p in c])
    rng = random.Random(seed)
    values: list[float] = []
    for _ in range(n_boot):
        value = statistic(_resample_payloads(clusters, rng))
        if value is not None:
            values.append(value)
    result = _ci_result(point, values, n_boot, alpha)
    result["n_clusters"] = len(clusters)
    result["n_items"] = sum(len(c) for c in clusters)
    return result


def cluster_bootstrap_diff_ci(
    rows: Rows,
    stat_a: Statistic,
    stat_b: Statistic,
    n_boot: int = DEFAULT_N_BOOT,
    seed: int = DEFAULT_SEED,
    alpha: float = DEFAULT_ALPHA,
) -> dict[str, Any]:
    """Paired difference CI: ``stat_a - stat_b`` on identical resamples.

    Both statistics read the same payloads (which must carry both systems'
    predictions), so per-replicate differences are paired. ``significant`` is
    True when the CI excludes 0.
    """
    clusters = _group_clusters(rows)
    if not clusters:
        return _ci_result(None, [], 0, alpha)
    all_payloads = [p for c in clusters for p in c]
    point_a = stat_a(all_payloads)
    point_b = stat_b(all_payloads)
    point = None if point_a is None or point_b is None else point_a - point_b
    rng = random.Random(seed)
    diffs: list[float] = []
    for _ in range(n_boot):
        payloads = _resample_payloads(clusters, rng)
        va = stat_a(payloads)
        vb = stat_b(payloads)
        if va is not None and vb is not None:
            diffs.append(va - vb)
    result = _ci_result(point, diffs, n_boot, alpha)
    result["point_a"] = None if point_a is None else round(point_a, 4)
    result["point_b"] = None if point_b is None else round(point_b, 4)
    result["n_clusters"] = len(clusters)
    result["n_items"] = len(all_payloads)
    if result["ci_low"] is not None:
        result["significant"] = bool(result["ci_low"] > 0 or result["ci_high"] < 0)
    else:
        result["significant"] = None
    return result


# ---------------------------------------------------------------------------
# Self-test on synthetic data with known ground truth
# ---------------------------------------------------------------------------


def _self_test() -> None:
    rng = random.Random(7)

    # 1) Accuracy CI covers the true rate (300 clusters x 5 correlated items).
    rows: list[tuple[Any, Any]] = []
    for cid in range(300):
        base = rng.random() < 0.7
        for _ in range(5):
            hit = base if rng.random() < 0.5 else (rng.random() < 0.7)
            rows.append((cid, ("g", "g" if hit else "x")))
    res = cluster_bootstrap_ci(rows, agreement_stat, n_boot=500)
    assert res["ci_low"] <= 0.7 <= res["ci_high"], f"accuracy CI misses truth: {res}"
    assert res["n_clusters"] == 300 and res["n_items"] == 1500

    # 2) Kappa of independent random labels is ~0 and its CI covers 0.
    labels = ["Yes", "To some extent", "No"]
    rows = [(cid, (rng.choice(labels), rng.choice(labels))) for cid in range(1000)]
    res = cluster_bootstrap_ci(rows, kappa_stat, n_boot=500)
    assert res["ci_low"] <= 0.0 <= res["ci_high"], f"kappa CI misses 0: {res}"

    # 3) Degenerate kappa (single gold label) reports n/a, not a number.
    rows = [(cid, ("Yes", rng.choice(labels))) for cid in range(50)]
    res = cluster_bootstrap_ci(rows, kappa_stat, n_boot=200)
    assert res["point"] is None and res["na_rate"] == 1.0, f"degenerate kappa not n/a: {res}"

    # 4) Paired diff: A is truly 8 points better than B on the same items;
    #    the paired CI must cover the true diff and exclude 0.
    payload_rows: list[tuple[Any, Any]] = []
    for cid in range(400):
        for _ in range(3):
            a_hit = rng.random() < 0.78
            b_hit = rng.random() < 0.70
            payload_rows.append((cid, {"a": ("g", "g" if a_hit else "x"), "b": ("g", "g" if b_hit else "x")}))
    res = cluster_bootstrap_diff_ci(
        payload_rows,
        lambda ps: agreement_stat([p["a"] for p in ps]),
        lambda ps: agreement_stat([p["b"] for p in ps]),
        n_boot=500,
    )
    assert res["ci_low"] <= 0.08 <= res["ci_high"], f"diff CI misses truth: {res}"
    assert res["significant"] is True, f"true 8-point diff not significant: {res}"

    print("stats.py self-test passed:")
    print(f"  accuracy example: {res}")


if __name__ == "__main__":
    _self_test()
