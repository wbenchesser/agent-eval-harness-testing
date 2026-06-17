"""CLI entry point for the meta-evaluator."""

import argparse
import asyncio
from pathlib import Path

from tabulate import tabulate

from .config import load_config
from .dataset.loader import load_dataset
from .dataset.sampler import get_distribution_summary, stratified_sample
from .judge.client import SecurityJudge, run_evaluation
from .judge.verdict import JudgeResult
from .scoring.metrics import compute_scorecard
from .scoring.reporter import print_scorecard, save_results_csv, save_scorecard_json


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="OWASP Security Meta-Evaluator")
    parser.add_argument(
        "--config", type=Path, default=Path("config.yaml"), help="Path to config file"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # scaffold: download dataset, show distribution, save locally
    sub.add_parser("scaffold", help="Download and prepare OWASP dataset")

    # run: execute LLM judge over test cases
    p_run = sub.add_parser("run", help="Run security judge on test cases")
    p_run.add_argument("--sample-size", type=int, help="Override config sample_size")

    # score: compute metrics from existing verdicts
    p_score = sub.add_parser("score", help="Score existing verdict files")
    p_score.add_argument("--results-dir", type=Path, help="Override results directory")

    # evaluate: full pipeline (scaffold + run + score)
    p_eval = sub.add_parser("evaluate", help="Run full evaluation pipeline")
    p_eval.add_argument("--sample-size", type=int, help="Override config sample_size")

    args = parser.parse_args()
    config = load_config(args.config)

    if args.command == "scaffold":
        asyncio.run(cmd_scaffold(config))
    elif args.command == "run":
        if args.sample_size:
            config.dataset.sample_size = args.sample_size
        asyncio.run(cmd_run(config))
    elif args.command == "score":
        cmd_score(config, args.results_dir)
    elif args.command == "evaluate":
        if args.sample_size:
            config.dataset.sample_size = args.sample_size
        asyncio.run(cmd_evaluate(config))


async def cmd_scaffold(config):
    """Download CSV, fetch source files, show distribution summary."""
    print("Loading OWASP Benchmark dataset...")
    cases = await load_dataset(
        config.dataset.csv_url,
        config.dataset.source_base_url,
        config.dataset.local_repo_path,
    )

    summary = get_distribution_summary(cases)
    print("\n=== FULL DATASET DISTRIBUTION ===")
    print(f"Total cases: {summary['total']}")
    print(f"True Positives (vulnerable): {summary['tp']} ({summary['tp_ratio']:.1%})")
    print(f"True Negatives (clean): {summary['tn']} ({1-summary['tp_ratio']:.1%})")

    print("\n=== CWE BREAKDOWN ===")
    rows = []
    for cwe_name, counts in summary["by_cwe"].items():
        rows.append([cwe_name, counts["total"], counts["tp"], counts["tn"]])
    print(tabulate(rows, headers=["CWE", "Total", "TP", "TN"]))

    if config.dataset.sample_size:
        print(f"\n=== SAMPLE (N={config.dataset.sample_size}) ===")
        sampled = stratified_sample(
            cases, config.dataset.sample_size, config.dataset.random_seed
        )
        sample_summary = get_distribution_summary(sampled)
        print(f"Sampled cases: {sample_summary['total']}")
        print(
            f"True Positives: {sample_summary['tp']} ({sample_summary['tp_ratio']:.1%})"
        )
        print(
            f"True Negatives: {sample_summary['tn']} ({1-sample_summary['tp_ratio']:.1%})"
        )

        print("\n=== SAMPLE CWE BREAKDOWN ===")
        rows = []
        for cwe_name, counts in sample_summary["by_cwe"].items():
            rows.append([cwe_name, counts["total"], counts["tp"], counts["tn"]])
        print(tabulate(rows, headers=["CWE", "Total", "TP", "TN"]))


async def cmd_run(config):
    """Load dataset, sample, run judge, save verdicts."""
    print("Loading dataset...")
    cases = await load_dataset(
        config.dataset.csv_url,
        config.dataset.source_base_url,
        config.dataset.local_repo_path,
    )

    if config.dataset.sample_size:
        print(f"Sampling {config.dataset.sample_size} cases (stratified)...")
        cases = stratified_sample(
            cases, config.dataset.sample_size, config.dataset.random_seed
        )

    print(f"\nRunning Vertex AI judge ({config.judge.model})...")
    judge = SecurityJudge(config.judge)
    results = await run_evaluation(cases, judge, config.execution)

    print(f"\nEvaluation complete. Results saved to {config.execution.output_dir}/verdicts/")


def cmd_score(config, results_dir: Path | None = None):
    """Load existing verdicts and compute metrics."""
    verdicts_dir = (results_dir or config.execution.output_dir) / "verdicts"

    if not verdicts_dir.exists():
        print(f"Error: Verdicts directory not found: {verdicts_dir}")
        print("Run 'meta-eval run' first to generate verdicts.")
        return

    print(f"Loading verdicts from {verdicts_dir}...")
    results = []
    for f in sorted(verdicts_dir.glob("*.json")):
        results.append(JudgeResult.model_validate_json(f.read_text()))

    if not results:
        print("No verdict files found.")
        return

    print(f"Loaded {len(results)} verdicts")

    scorecard = compute_scorecard(results)
    print_scorecard(scorecard)

    output_dir = results_dir or config.execution.output_dir
    save_scorecard_json(scorecard, output_dir / "scorecard.json")
    save_results_csv(results, output_dir / "results.csv")


async def cmd_evaluate(config):
    """Full pipeline: scaffold + run + score."""
    await cmd_run(config)
    print("\n" + "=" * 80)
    cmd_score(config)


if __name__ == "__main__":
    main()
