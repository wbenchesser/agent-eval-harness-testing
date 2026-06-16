# Quick Start Guide

## Installation

```bash
# Set Red Hat corporate credentials
export MODEL_API="https://claude--apicast-production.apps.int.stc.ai.prod.us-east-1.aws.paas.redhat.com:443"
export USER_KEY="your-models-corp-credential"

# Install dependencies
cd agent-eval-harness-testing
pip install -e .
```

## Test Connection (Optional)

```bash
python3 test_corporate_endpoint.py
```

Expected: `✅ SUCCESS! Connection established.`

## Run Your First Evaluation (10 cases, ~30 seconds)

```bash
meta-eval evaluate --sample-size 10
```

This will:
1. Download 10 stratified-sampled OWASP test cases
2. Run Claude (via Red Hat corporate endpoint) to judge each one for vulnerabilities
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
Cost: $0.0500  Tokens: 12,543

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

## Run a Larger Evaluation (100 cases, ~5 minutes, ~$0.50-1.50)

```bash
meta-eval evaluate --sample-size 100
```

## Cost Estimates (Claude Haiku)

| Sample Size | Approx. Cost | Time | Use Case |
|------------|-------------|------|----------|
| 10 | $0.05 | 30s | Quick test |
| 100 | $0.50-1.50 | 5min | Standard eval |
| 500 | $2.50-7.50 | 25min | Thorough eval |
| 2,740 (full) | $15-40 | 2h | Publication-quality |

**Note:** Costs shown for Haiku model. Sonnet costs ~3x more, Opus ~5x more.

## Resume a Failed Run

If a run crashes, just re-run the same command. Already-evaluated cases are skipped automatically.

## Change Models

Edit `config.yaml`:

```yaml
judge:
  model: "claude-sonnet-4-6@20250514"  # or claude-opus-4-8@20250514
```

Then run again:
```bash
meta-eval evaluate --sample-size 100
```

## Troubleshooting

**"Environment variable MODEL_API not set"**
```bash
export MODEL_API="https://claude--apicast-production.apps.int.stc.ai.prod.us-east-1.aws.paas.redhat.com:443"
```

**"Environment variable USER_KEY not set"**
```bash
export USER_KEY="your-credential-here"
```

**"401 Unauthorized"**

Check your credential in the models.corp platform and ensure it hasn't expired.

**"Connection timeout"**

Ensure you're connected to the Red Hat VPN or internal network.

**"Configuration file not found"**

Make sure you're in the project root directory where `config.yaml` exists.

**Rate limit errors**

Reduce `requests_per_minute` in config.yaml:
```yaml
judge:
  requests_per_minute: 30  # Lower from default 50
```

## Next Steps

- Read [META_EVALUATOR.md](META_EVALUATOR.md) for full documentation
- Read [CORPORATE_VERTEX_SETUP.md](CORPORATE_VERTEX_SETUP.md) for detailed setup
- Edit `config.yaml` to customize models, sampling, concurrency
- Run `pytest` to verify your installation
- Use `meta-eval scaffold` to explore the dataset without API calls
