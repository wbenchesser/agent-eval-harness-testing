# OWASP Security Meta-Evaluator

A standalone Python tool for testing the quality of LLM-based security judges using the OWASP Benchmark.

## Overview

This meta-evaluator implements the "Custom Approach" described in the main README. It evaluates how accurately an LLM can identify security vulnerabilities in Java code by:

1. **Dataset Scaffolding** — Loading 2,740 OWASP Benchmark test cases with known vulnerability ground truth
2. **Security Judge** — Running an LLM that reads Java code and outputs structured vulnerability verdicts
3. **Meta-Judge** — Comparing LLM verdicts against ground truth and computing metrics (confusion matrix, TPR/FPR/Youden per CWE)

## Installation

```bash
# Install in development mode
pip install -e .

# Or install dev dependencies for testing
pip install -e ".[dev]"
```

## Configuration

Edit `config.yaml`:

```yaml
dataset:
  sample_size: 100  # Start with 100 cases (~$1-3 per run)

judge:
  provider: "anthropic"  # or "openai" or "vertex"
  model: "claude-opus-4-8"
  api_key_env: "ANTHROPIC_API_KEY"
```

Set your API key:

```bash
# For Anthropic
export ANTHROPIC_API_KEY="sk-ant-..."

# For OpenAI
export OPENAI_API_KEY="sk-..."

# For Google Vertex AI
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
export GCP_PROJECT_ID="your-project-id"
export GCP_REGION="us-central1"  # Optional, defaults to us-central1
```

## Usage

### 1. Explore the Dataset

```bash
meta-eval scaffold
```

Shows CWE distribution and sample statistics without making API calls.

### 2. Run the Security Judge

```bash
meta-eval run
```

Evaluates all cases (or the configured sample) and saves verdicts to `results/verdicts/*.json`.

### 3. Score the Results

```bash
meta-eval score
```

Computes metrics from existing verdicts:
- Overall: accuracy, precision, recall, F1, Youden Index
- Per-CWE: TPR, FPR, Youden breakdown
- Confusion matrix

Outputs:
- Console table
- `results/scorecard.json` — full metrics
- `results/results.csv` — per-case results for analysis

### 4. Full Pipeline

```bash
meta-eval evaluate
```

Runs scaffold → run → score in sequence.

### Quick Test with Small Sample

```bash
meta-eval evaluate --sample-size 10
```

## Resumability

The tool saves each verdict immediately to disk. If a run crashes, re-run the same command — it will skip already-evaluated cases and continue where it left off.

To force re-evaluation:

```yaml
execution:
  resume: false
```

## Cost Management

Approximate costs per 100 cases by model:
- **Claude Opus 4.8**: $1-3
- **GPT-4o**: $0.8-2.5
- **Gemini 2.5 Pro**: $0.4-1.2
- **Gemini 2.5 Flash**: $0.03-0.10

Full 2,740 cases costs:
- **Claude Opus 4.8**: $25-75
- **GPT-4o**: $20-65
- **Gemini 2.5 Pro**: $10-30
- **Gemini 2.5 Flash**: $1-3

The `sample_size` config controls the number of cases. Stratified sampling preserves CWE distribution and TP/TN ratio.

## Metrics Explained

- **Youden Index** (TPR - FPR): Primary metric, ranges from -1 to 1. A score of 1.0 is perfect, 0.0 is random guessing, negative means worse than random. This is the standard OWASP Benchmark metric.
- **TPR (Recall)**: What fraction of real vulnerabilities did the judge catch?
- **FPR**: What fraction of clean code did the judge incorrectly flag?
- **Precision**: Of all the code the judge flagged, what fraction was actually vulnerable?

## Code-Instruction Isolation

The system prompt instructs the LLM to **IGNORE code comments** because some OWASP test cases contain comments describing the vulnerability. This prevents "cheating" and tests whether the LLM can identify vulnerabilities from code logic alone.

## Provider-Specific Configuration

### Anthropic Claude

```yaml
judge:
  provider: "anthropic"
  model: "claude-opus-4-8"  # or claude-sonnet-4-6, claude-haiku-4-5
  api_key_env: "ANTHROPIC_API_KEY"
  thinking: "adaptive"  # or "disabled"
```

### OpenAI

```yaml
judge:
  provider: "openai"
  model: "gpt-4o"  # or gpt-4o-mini
  api_key_env: "OPENAI_API_KEY"
```

### Google Vertex AI

```yaml
judge:
  provider: "vertex"
  model: "gemini-2.5-pro-latest"  # or gemini-2.5-flash-latest, gemini-1.5-pro
  api_key_env: "GOOGLE_APPLICATION_CREDENTIALS"
  gcp_project_env: "GCP_PROJECT_ID"
  gcp_region_env: "GCP_REGION"
  gcp_location: "us-central1"  # Default region
```

**Authentication Setup:**

```bash
# Option 1: Service Account Key
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
export GCP_PROJECT_ID="your-gcp-project"

# Option 2: Application Default Credentials (ADC)
gcloud auth application-default login
export GCP_PROJECT_ID="your-gcp-project"

# Optional: Override region
export GCP_REGION="us-east1"
```

**Note:** Vertex AI does not support extended thinking like Anthropic's `thinking` parameter.

**For detailed Vertex AI setup instructions**, see [VERTEX_AI_SETUP.md](VERTEX_AI_SETUP.md).

## Testing

```bash
pytest
```

Tests cover:
- CSV parsing and ground truth loading
- Stratified sampling and distribution preservation
- Confusion matrix and metric calculations

## Architecture

```
src/meta_evaluator/
  config.py           # Pydantic config models
  dataset/
    loader.py          # OWASP CSV + source fetching
    sampler.py         # Stratified sampling
  judge/
    verdict.py         # Pydantic verdict models
    prompts.py         # System/user prompts
    client.py          # Async LLM client (Anthropic + OpenAI)
  scoring/
    metrics.py         # Confusion matrix, Youden Index
    reporter.py        # Console + JSON/CSV output
  cli.py              # CLI entry point
```

## Example Output

```
=== OVERALL METRICS ===
Accuracy:  0.850
Precision: 0.900
Recall:    0.818
F1 Score:  0.857
Youden:    +0.707
Cases: 100  Errors: 0
Cost: $1.2500  Tokens: 125,432

=== PER-CWE BREAKDOWN ===
Category    CWE      N  TPR    FPR    Youden    Acc
----------  -----  ---  -----  -----  --------  -----
sqli        89      25  0.933  0.100  +0.833    0.880
xss         79      24  0.857  0.091  +0.766    0.833
pathtraver  22       7  0.750  0.200  +0.550    0.714
...

=== CONFUSION MATRIX ===
             Predicted Vuln  Predicted Safe
Actually Vuln     90              20
Actually Safe     10              80
```

## Next Steps

- Compare multiple models (Claude vs GPT-4) by running separate evaluations
- Analyze false positives/negatives by reviewing specific verdict files
- Experiment with prompt variations to improve accuracy
- Use results.csv for detailed analysis in Jupyter notebooks
