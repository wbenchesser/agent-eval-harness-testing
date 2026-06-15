# Quick Start Guide

## Installation

```bash
# Clone and install
cd agent-eval-harness-testing
pip install -e .

# Set API key
export ANTHROPIC_API_KEY="sk-ant-..."
```

## Run Your First Evaluation (10 cases, ~30 seconds)

```bash
meta-eval evaluate --sample-size 10
```

This will:
1. Download 10 stratified-sampled OWASP test cases
2. Run Claude Opus to judge each one for vulnerabilities
3. Compare verdicts to ground truth and show metrics

## Expected Output

```
Loading dataset...
Loaded 2740 test cases from CSV
...
Evaluating 10 test cases...
  Completed 10/10 cases...

=== OVERALL METRICS ===
Accuracy:  0.900
Precision: 0.889
Recall:    0.800
F1 Score:  0.842
Youden:    +0.733
Cases: 10  Errors: 0
Cost: $0.1250  Tokens: 12,543

=== PER-CWE BREAKDOWN ===
...

Scorecard saved to results/scorecard.json
Results CSV saved to results/results.csv
```

## Understanding Results

- **Accuracy**: Overall correctness (should be >0.8 for a good judge)
- **Youden Index**: The key metric (1.0 = perfect, 0.0 = random, <0 = worse than random)
- **TPR (Recall)**: Fraction of vulnerabilities correctly identified
- **FPR**: Fraction of clean code incorrectly flagged

## Inspect Individual Cases

```bash
# Look at a specific verdict
cat results/verdicts/BenchmarkTest00001.json

# View all results in spreadsheet
open results/results.csv
```

## Run a Larger Evaluation (100 cases, ~5 minutes, ~$1-3)

```bash
meta-eval evaluate --sample-size 100
```

## Cost Estimates

| Sample Size | Approx. Cost | Time | Use Case |
|------------|-------------|------|----------|
| 10 | $0.10 | 30s | Quick test |
| 100 | $1-3 | 5min | Standard eval |
| 500 | $5-15 | 25min | Thorough eval |
| 2,740 (full) | $25-75 | 2h | Publication-quality |

## Resume a Failed Run

If a run crashes, just re-run the same command. Already-evaluated cases are skipped automatically.

## Compare Models

```bash
# Run with Claude Opus
meta-eval run --sample-size 100
mv results results-opus

# Edit config.yaml to use GPT-4o, then run again
meta-eval run --sample-size 100
mv results results-gpt4

# Compare scorecard.json files
```

## Troubleshooting

**"Environment variable ANTHROPIC_API_KEY not set"**
```bash
export ANTHROPIC_API_KEY="your-key-here"
```

**"Configuration file not found"**

Make sure you're in the project root directory where `config.yaml` exists.

**Rate limit errors**

Reduce `concurrency` in config.yaml:
```yaml
execution:
  concurrency: 5  # Lower from default 10
```

## Next Steps

- Read [META_EVALUATOR.md](META_EVALUATOR.md) for full documentation
- Edit `config.yaml` to customize models, sampling, concurrency
- Run `pytest` to verify your installation
- Use `meta-eval scaffold` to explore the dataset without API calls
