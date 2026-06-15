"""Tests for stratified sampler."""

from meta_evaluator.dataset.loader import TestCase
from meta_evaluator.dataset.sampler import get_distribution_summary, stratified_sample


def test_stratified_sample_preserves_distribution():
    """Test that sampling preserves approximate TP/TN ratio."""
    # Create 100 cases: 60 TP, 40 TN across 2 CWEs
    cases = []
    for i in range(60):
        cases.append(
            TestCase(
                test_name=f"Test{i:05d}",
                category="sqli",
                is_vulnerable=True,
                cwe=89,
                source_code="code",
            )
        )
    for i in range(40):
        cases.append(
            TestCase(
                test_name=f"Test{i+60:05d}",
                category="xss",
                is_vulnerable=False,
                cwe=79,
                source_code="code",
            )
        )

    sampled = stratified_sample(cases, 20, seed=42)

    summary = get_distribution_summary(sampled)
    assert summary["total"] == 20
    # Should be roughly 60/40 split (±10%)
    assert 0.5 <= summary["tp_ratio"] <= 0.7


def test_stratified_sample_deterministic():
    """Test that same seed produces same sample."""
    cases = [
        TestCase(
            test_name=f"Test{i:05d}",
            category="sqli",
            is_vulnerable=(i % 2 == 0),
            cwe=89,
            source_code="code",
        )
        for i in range(100)
    ]

    sample1 = stratified_sample(cases, 10, seed=42)
    sample2 = stratified_sample(cases, 10, seed=42)

    assert [c.test_name for c in sample1] == [c.test_name for c in sample2]


def test_get_distribution_summary():
    """Test distribution summary calculation."""
    cases = [
        TestCase("Test1", "sqli", True, 89, "code"),
        TestCase("Test2", "sqli", True, 89, "code"),
        TestCase("Test3", "sqli", False, 89, "code"),
        TestCase("Test4", "xss", True, 79, "code"),
    ]

    summary = get_distribution_summary(cases)

    assert summary["total"] == 4
    assert summary["tp"] == 3
    assert summary["tn"] == 1
    assert summary["tp_ratio"] == 0.75
    assert len(summary["by_cwe"]) == 2
