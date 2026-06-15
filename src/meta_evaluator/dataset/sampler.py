"""Stratified sampling for preserving CWE and TP/TN distribution."""

import random
from collections import defaultdict

from .loader import TestCase


def stratified_sample(
    cases: list[TestCase],
    sample_size: int,
    seed: int = 42,
) -> list[TestCase]:
    """Stratified sample preserving CWE x vulnerability distribution."""
    if sample_size >= len(cases):
        return cases

    rng = random.Random(seed)

    # Group by (category, is_vulnerable) -- 11 CWEs x 2 = up to 22 strata
    strata: dict[tuple[str, bool], list[TestCase]] = defaultdict(list)
    for case in cases:
        strata[(case.category, case.is_vulnerable)].append(case)

    # Proportional allocation per stratum
    selected = []
    for key, group in strata.items():
        n = max(1, round(len(group) / len(cases) * sample_size))
        selected.extend(rng.sample(group, min(n, len(group))))

    # Trim or pad to exact sample_size
    if len(selected) > sample_size:
        selected = rng.sample(selected, sample_size)

    return selected


def get_distribution_summary(cases: list[TestCase]) -> dict:
    """Return CWE counts and TP/TN ratio for validation."""
    total = len(cases)
    tp_count = sum(1 for c in cases if c.is_vulnerable)
    tn_count = total - tp_count

    by_cwe: dict[tuple[str, int], dict] = defaultdict(lambda: {"tp": 0, "tn": 0, "total": 0})

    for case in cases:
        key = (case.category, case.cwe)
        by_cwe[key]["total"] += 1
        if case.is_vulnerable:
            by_cwe[key]["tp"] += 1
        else:
            by_cwe[key]["tn"] += 1

    return {
        "total": total,
        "tp": tp_count,
        "tn": tn_count,
        "tp_ratio": tp_count / total if total else 0.0,
        "by_cwe": {
            f"{cat} (CWE-{cwe})": counts for (cat, cwe), counts in sorted(by_cwe.items())
        },
    }
