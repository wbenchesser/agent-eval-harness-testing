"""Tests for metrics computation."""

from meta_evaluator.judge.verdict import JudgeResult, Verdict
from meta_evaluator.scoring.metrics import ConfusionMatrix, compute_scorecard


def test_confusion_matrix_properties():
    """Test confusion matrix metric calculations."""
    # TP=90, FP=10, TN=80, FN=20
    cm = ConfusionMatrix(tp=90, fp=10, tn=80, fn=20)

    assert cm.accuracy == 0.85  # (90+80)/200
    assert cm.precision == 0.9  # 90/(90+10)
    assert abs(cm.recall - 0.818) < 0.001  # 90/(90+20)
    assert abs(cm.f1 - 0.857) < 0.001  # 2*0.9*0.818/(0.9+0.818)
    assert abs(cm.fpr - 0.111) < 0.001  # 10/(10+80)
    assert abs(cm.youden_index - 0.707) < 0.001  # 0.818-0.111


def test_confusion_matrix_perfect():
    """Test perfect classification."""
    cm = ConfusionMatrix(tp=100, fp=0, tn=100, fn=0)

    assert cm.accuracy == 1.0
    assert cm.precision == 1.0
    assert cm.recall == 1.0
    assert cm.f1 == 1.0
    assert cm.fpr == 0.0
    assert cm.youden_index == 1.0


def test_confusion_matrix_all_wrong():
    """Test all incorrect classification."""
    cm = ConfusionMatrix(tp=0, fp=100, tn=0, fn=100)

    assert cm.accuracy == 0.0
    assert cm.precision == 0.0
    assert cm.recall == 0.0
    assert cm.youden_index == -1.0


def test_compute_scorecard_basic():
    """Test scorecard computation with mixed results."""
    results = [
        # True Positive (correct)
        JudgeResult(
            test_name="Test1",
            ground_truth_vulnerable=True,
            ground_truth_cwe=89,
            ground_truth_category="sqli",
            verdict=Verdict(is_vulnerable=True, cwe=89, confidence=0.9, reasoning="SQL injection"),
            input_tokens=1000,
            output_tokens=100,
            cost_usd=0.01,
            latency_seconds=1.0,
            model="test-model",
        ),
        # False Positive (incorrect)
        JudgeResult(
            test_name="Test2",
            ground_truth_vulnerable=False,
            ground_truth_cwe=89,
            ground_truth_category="sqli",
            verdict=Verdict(is_vulnerable=True, cwe=89, confidence=0.7, reasoning="Looks bad"),
            input_tokens=1000,
            output_tokens=100,
            cost_usd=0.01,
            latency_seconds=1.0,
            model="test-model",
        ),
        # True Negative (correct)
        JudgeResult(
            test_name="Test3",
            ground_truth_vulnerable=False,
            ground_truth_cwe=79,
            ground_truth_category="xss",
            verdict=Verdict(is_vulnerable=False, cwe=None, confidence=0.95, reasoning="Clean"),
            input_tokens=1000,
            output_tokens=100,
            cost_usd=0.01,
            latency_seconds=1.0,
            model="test-model",
        ),
        # Error case
        JudgeResult(
            test_name="Test4",
            ground_truth_vulnerable=True,
            ground_truth_cwe=22,
            ground_truth_category="pathtraver",
            verdict=Verdict(
                is_vulnerable=False, cwe=None, confidence=0.0, reasoning="ERROR"
            ),
            input_tokens=0,
            output_tokens=0,
            cost_usd=0.0,
            latency_seconds=0.0,
            model="test-model",
            error="API timeout",
        ),
    ]

    scorecard = compute_scorecard(results)

    assert scorecard.total_cases == 4
    assert scorecard.error_count == 1
    assert scorecard.overall.tp == 1
    assert scorecard.overall.fp == 1
    assert scorecard.overall.tn == 1
    assert scorecard.overall.fn == 0  # Error case is excluded
    assert scorecard.total_cost_usd == 0.03
    assert len(scorecard.per_cwe) == 2  # sqli and xss


def test_compute_scorecard_all_correct():
    """Test scorecard with all correct verdicts."""
    results = [
        JudgeResult(
            test_name=f"Test{i}",
            ground_truth_vulnerable=True,
            ground_truth_cwe=89,
            ground_truth_category="sqli",
            verdict=Verdict(is_vulnerable=True, cwe=89, confidence=0.9, reasoning="correct"),
            input_tokens=1000,
            output_tokens=100,
            cost_usd=0.01,
            latency_seconds=1.0,
            model="test-model",
        )
        for i in range(10)
    ]

    scorecard = compute_scorecard(results)

    assert scorecard.overall.tp == 10
    assert scorecard.overall.fp == 0
    assert scorecard.overall.tn == 0
    assert scorecard.overall.fn == 0
    assert scorecard.overall.accuracy == 1.0
    assert scorecard.overall.youden_index == 1.0
