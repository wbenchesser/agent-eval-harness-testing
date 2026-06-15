"""Output formatting and report generation."""

import csv
import json
from pathlib import Path

from tabulate import tabulate

from meta_evaluator.judge.verdict import JudgeResult

from .metrics import Scorecard


def print_scorecard(scorecard: Scorecard) -> None:
    """Print human-readable summary to stdout."""
    # Overall metrics table
    o = scorecard.overall
    print("\n=== OVERALL METRICS ===")
    print(f"Accuracy:  {o.accuracy:.3f}")
    print(f"Precision: {o.precision:.3f}")
    print(f"Recall:    {o.recall:.3f}")
    print(f"F1 Score:  {o.f1:.3f}")
    print(f"Youden:    {o.youden_index:+.3f}")
    print(f"Cases: {scorecard.total_cases}  Errors: {scorecard.error_count}")
    print(
        f"Cost: ${scorecard.total_cost_usd:.4f}  "
        f"Tokens: {scorecard.total_input_tokens + scorecard.total_output_tokens:,}"
    )

    # Per-CWE table
    rows = []
    for entry in scorecard.per_cwe:
        m = entry.matrix
        rows.append(
            [
                entry.category,
                entry.cwe,
                entry.sample_count,
                f"{m.recall:.3f}",
                f"{m.fpr:.3f}",
                f"{m.youden_index:+.3f}",
                f"{m.accuracy:.3f}",
            ]
        )
    print("\n=== PER-CWE BREAKDOWN ===")
    print(tabulate(rows, headers=["Category", "CWE", "N", "TPR", "FPR", "Youden", "Acc"]))

    # Confusion matrix
    print("\n=== CONFUSION MATRIX ===")
    print("             Predicted Vuln  Predicted Safe")
    print(f"Actually Vuln     {o.tp:>5}          {o.fn:>5}")
    print(f"Actually Safe     {o.fp:>5}          {o.tn:>5}")


def save_scorecard_json(scorecard: Scorecard, path: Path) -> None:
    """Save machine-readable JSON for downstream analysis."""
    data = {
        "overall": {
            "accuracy": scorecard.overall.accuracy,
            "precision": scorecard.overall.precision,
            "recall": scorecard.overall.recall,
            "f1": scorecard.overall.f1,
            "fpr": scorecard.overall.fpr,
            "youden_index": scorecard.overall.youden_index,
            "tp": scorecard.overall.tp,
            "fp": scorecard.overall.fp,
            "tn": scorecard.overall.tn,
            "fn": scorecard.overall.fn,
        },
        "per_cwe": [
            {
                "category": entry.category,
                "cwe": entry.cwe,
                "sample_count": entry.sample_count,
                "accuracy": entry.matrix.accuracy,
                "precision": entry.matrix.precision,
                "recall": entry.matrix.recall,
                "f1": entry.matrix.f1,
                "fpr": entry.matrix.fpr,
                "youden_index": entry.matrix.youden_index,
                "tp": entry.matrix.tp,
                "fp": entry.matrix.fp,
                "tn": entry.matrix.tn,
                "fn": entry.matrix.fn,
            }
            for entry in scorecard.per_cwe
        ],
        "summary": {
            "total_cases": scorecard.total_cases,
            "error_count": scorecard.error_count,
            "total_cost_usd": scorecard.total_cost_usd,
            "total_input_tokens": scorecard.total_input_tokens,
            "total_output_tokens": scorecard.total_output_tokens,
        },
    }

    path.write_text(json.dumps(data, indent=2))
    print(f"\nScorecard saved to {path}")


def save_results_csv(results: list[JudgeResult], path: Path) -> None:
    """Save per-case results as CSV for analysis in notebooks."""
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "test_name",
                "category",
                "cwe",
                "ground_truth_vulnerable",
                "predicted_vulnerable",
                "predicted_cwe",
                "confidence",
                "correct",
                "error",
                "cost_usd",
                "latency_seconds",
            ]
        )

        for r in results:
            correct = (
                None
                if r.error
                else (r.verdict.is_vulnerable == r.ground_truth_vulnerable)
            )
            writer.writerow(
                [
                    r.test_name,
                    r.ground_truth_category,
                    r.ground_truth_cwe,
                    r.ground_truth_vulnerable,
                    r.verdict.is_vulnerable if not r.error else None,
                    r.verdict.cwe if not r.error else None,
                    r.verdict.confidence if not r.error else None,
                    correct,
                    r.error,
                    r.cost_usd,
                    r.latency_seconds,
                ]
            )

    print(f"Results CSV saved to {path}")
