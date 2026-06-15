"""Meta-judge scoring: confusion matrix and metrics computation."""

from collections import defaultdict
from dataclasses import dataclass, field

from meta_evaluator.judge.verdict import JudgeResult


@dataclass
class ConfusionMatrix:
    """Confusion matrix for binary classification."""

    tp: int = 0  # Judge says vulnerable, ground truth says vulnerable
    fp: int = 0  # Judge says vulnerable, ground truth says NOT vulnerable
    tn: int = 0  # Judge says not vulnerable, ground truth says NOT vulnerable
    fn: int = 0  # Judge says not vulnerable, ground truth says vulnerable

    @property
    def accuracy(self) -> float:
        """Accuracy: (TP + TN) / total."""
        total = self.tp + self.fp + self.tn + self.fn
        return (self.tp + self.tn) / total if total else 0.0

    @property
    def precision(self) -> float:
        """Precision: TP / (TP + FP)."""
        return self.tp / (self.tp + self.fp) if (self.tp + self.fp) else 0.0

    @property
    def recall(self) -> float:
        """Recall (TPR): TP / (TP + FN)."""
        return self.tp / (self.tp + self.fn) if (self.tp + self.fn) else 0.0

    @property
    def f1(self) -> float:
        """F1 score: 2 * precision * recall / (precision + recall)."""
        p, r = self.precision, self.recall
        return 2 * p * r / (p + r) if (p + r) else 0.0

    @property
    def fpr(self) -> float:
        """False Positive Rate: FP / (FP + TN)."""
        return self.fp / (self.fp + self.tn) if (self.fp + self.tn) else 0.0

    @property
    def youden_index(self) -> float:
        """Youden Index: TPR - FPR (ranges from -1 to 1, 1 is perfect)."""
        return self.recall - self.fpr


@dataclass
class ScorecardEntry:
    """Per-CWE scorecard entry."""

    category: str
    cwe: int
    matrix: ConfusionMatrix
    sample_count: int


@dataclass
class Scorecard:
    """Full evaluation scorecard with overall and per-CWE metrics."""

    overall: ConfusionMatrix
    per_cwe: list[ScorecardEntry]
    total_cases: int
    error_count: int
    total_cost_usd: float
    total_input_tokens: int
    total_output_tokens: int


def compute_scorecard(results: list[JudgeResult]) -> Scorecard:
    """The meta-judge: compares LLM verdicts against OWASP ground truth."""
    overall = ConfusionMatrix()
    by_cwe: dict[tuple[str, int], ConfusionMatrix] = defaultdict(ConfusionMatrix)
    error_count = 0

    for r in results:
        if r.error:
            error_count += 1
            continue

        predicted = r.verdict.is_vulnerable
        actual = r.ground_truth_vulnerable
        key = (r.ground_truth_category, r.ground_truth_cwe)

        if predicted and actual:
            overall.tp += 1
            by_cwe[key].tp += 1
        elif predicted and not actual:
            overall.fp += 1
            by_cwe[key].fp += 1
        elif not predicted and not actual:
            overall.tn += 1
            by_cwe[key].tn += 1
        else:  # not predicted and actual
            overall.fn += 1
            by_cwe[key].fn += 1

    per_cwe = [
        ScorecardEntry(
            category=cat,
            cwe=cwe,
            matrix=m,
            sample_count=m.tp + m.fp + m.tn + m.fn,
        )
        for (cat, cwe), m in sorted(by_cwe.items())
    ]

    return Scorecard(
        overall=overall,
        per_cwe=per_cwe,
        total_cases=len(results),
        error_count=error_count,
        total_cost_usd=sum(r.cost_usd for r in results),
        total_input_tokens=sum(r.input_tokens for r in results),
        total_output_tokens=sum(r.output_tokens for r in results),
    )
