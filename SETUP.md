# Setup Guide

Complete setup instructions for the OWASP Security Meta-Evaluator with Red Hat Corporate Vertex AI.

## Prerequisites

1. **Red Hat models.corp access** - You must have access to the corporate Claude API endpoint
2. **Application credentials** - Obtain your `USER_KEY` from the models.corp platform
3. **Python 3.11+** - Required for the evaluator

## Quick Setup (5 minutes)

### 1. Set Environment Variables

```bash
export MODEL_API="https://claude--apicast-production.apps.int.stc.ai.prod.us-east-1.aws.paas.redhat.com:443"
export USER_KEY="your-models-corp-credential-here"
```

### 2. Make Environment Persistent

Add to your `~/.zshrc` (Mac) or `~/.bashrc` (Linux):

```bash
echo 'export MODEL_API="https://claude--apicast-production.apps.int.stc.ai.prod.us-east-1.aws.paas.redhat.com:443"' >> ~/.zshrc
echo 'export USER_KEY="your-credential-here"' >> ~/.zshrc
source ~/.zshrc
```

### 3. Install Dependencies

```bash
cd agent-eval-harness-testing
pip install -e .
```

This installs:
- `pyyaml` - Configuration parsing
- `pydantic` - Data validation
- `tabulate` - Result formatting
- `httpx` - HTTP client for API calls

### 4. Test Connection

```bash
python3 test_corporate_endpoint.py
```

Expected output:
```
✅ Environment variables found:
   MODEL_API: https://...
   MODEL_ID: claude-haiku-4-5@20251001
   USER_KEY: ********************abcd

🔄 Testing connection to: https://.../haiku/models/...

✅ SUCCESS! Connection established.

Response: test successful

Token usage:
  Input:  15 tokens
  Output: 3 tokens

🎉 Your corporate endpoint is ready to use!
```

### 5. Run Your First Evaluation

```bash
meta-eval evaluate --sample-size 10
```

Expected cost: ~$0.05 with Haiku

## Configuration

The default `config.yaml` is pre-configured with optimal settings:

```yaml
dataset:
  sample_size: 100  # Number of test cases (null = all 2,740)
  random_seed: 42   # For reproducible sampling

judge:
  model: "claude-haiku-4-5@20251001"  # Claude model to use
  max_tokens: 1024                     # Max response length
  thinking: "disabled"                 # Extended thinking (disabled for corporate endpoint)
  temperature: null                    # Use default (0.0)
  requests_per_minute: 50              # Rate limit
  
execution:
  concurrency: 10    # Parallel API calls
  resume: true       # Skip already-evaluated cases
```

## Available Models

| Model | Model ID | Speed | Cost (100 cases) | Best For |
|-------|----------|-------|------------------|----------|
| **Haiku 4.5** | `claude-haiku-4-5@20251001` | Fast | $0.50-1.50 | Cost efficiency |
| **Sonnet 4.6** | `claude-sonnet-4-6@20250514` | Medium | $1.50-4.50 | Balanced |
| **Opus 4.8** | `claude-opus-4-8@20250514` | Slow | $2.50-7.50 | Maximum accuracy |

To change model, edit `config.yaml`:
```yaml
judge:
  model: "claude-sonnet-4-6@20250514"
```

## Cost Estimates

### By Sample Size (Haiku - Recommended)
- 10 cases: $0.05
- 100 cases: $0.50-1.50
- 500 cases: $2.50-7.50
- 2,740 cases (full): $15-40

### By Sample Size (Sonnet)
- 10 cases: $0.15
- 100 cases: $1.50-4.50
- 500 cases: $7.50-22.50
- 2,740 cases (full): $40-120

### By Sample Size (Opus)
- 10 cases: $0.25
- 100 cases: $2.50-7.50
- 500 cases: $12.50-37.50
- 2,740 cases (full): $70-200

## Usage Examples

### Basic Evaluation
```bash
# Small test
meta-eval evaluate --sample-size 10

# Standard run
meta-eval evaluate --sample-size 100

# Full dataset
meta-eval run
```

### Step-by-Step Workflow
```bash
# 1. Explore dataset without API calls
meta-eval scaffold

# 2. Run evaluation
meta-eval run

# 3. Score results
meta-eval score
```

### Model Comparison
```bash
# Run with Haiku
meta-eval evaluate --sample-size 100
mv results results-haiku

# Edit config.yaml to use Sonnet
# Change: model: "claude-sonnet-4-6@20250514"
meta-eval evaluate --sample-size 100
mv results results-sonnet

# Compare
diff results-haiku/scorecard.json results-sonnet/scorecard.json
```

## Troubleshooting

### Connection Issues

**Error: "Environment variable MODEL_API not set"**
```bash
export MODEL_API="https://claude--apicast-production.apps.int.stc.ai.prod.us-east-1.aws.paas.redhat.com:443"
```

**Error: "Environment variable USER_KEY not set"**
```bash
export USER_KEY="your-credential-here"
```

**Error: "Connection timeout"**
- Check that you're connected to Red Hat VPN
- Verify the endpoint URL is correct
- Test with: `curl -I $MODEL_API`

### Authentication Issues

**Error: "401 Unauthorized"**
- Credential expired or invalid
- Check models.corp platform for active credentials
- Verify USER_KEY is correct: `echo $USER_KEY`

### Rate Limiting

**Error: "Rate limit exceeded"**

Reduce requests per minute in `config.yaml`:
```yaml
judge:
  requests_per_minute: 30  # Lower from 50
```

Or reduce concurrency:
```yaml
execution:
  concurrency: 5  # Lower from 10
```

### Performance Issues

**Evaluation is slow**
- Check network latency to corporate endpoint
- Reduce concurrency if hitting rate limits
- Use Haiku instead of Sonnet/Opus for speed

**High costs**
- Start with small sample sizes (10-100)
- Use Haiku model instead of Sonnet/Opus
- Check `results/scorecard.json` for actual costs

## Performance Notes

- **Latency**: Corporate endpoints typically have 1-3s latency per request
- **Rate Limits**: Default 50 req/min is conservative; adjust based on your quota
- **Concurrent Requests**: Default 10 is safe for most quotas
- **Resume Mode**: Enabled by default to avoid re-running failed cases

## Security Best Practices

1. **Never commit credentials** to version control
2. **Store credentials in environment variables** only
3. **Use `.gitignore`** to exclude any files containing credentials
4. **Rotate credentials regularly** according to Red Hat security policies
5. **Don't share credentials** via email, Slack, or other channels

## Development Setup

For testing and development:

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
ruff check src/
```

## Next Steps

1. **Quick Test**: Run `meta-eval evaluate --sample-size 10` to verify setup
2. **Read Documentation**: See [META_EVALUATOR.md](META_EVALUATOR.md) for detailed usage
3. **Explore Dataset**: Use `meta-eval scaffold` to see CWE distribution
4. **Run Evaluation**: Start with 100 cases, then scale up

## Support

- **Corporate endpoint issues**: Contact Red Hat models.corp team
- **Evaluator bugs**: File issue in this repository
- **Usage questions**: See [META_EVALUATOR.md](META_EVALUATOR.md)

## Advanced Configuration

### Using a Local OWASP Clone

For faster execution (no network calls for source files):

```yaml
dataset:
  local_repo_path: "/path/to/BenchmarkJava"
```

Clone the repository:
```bash
git clone https://github.com/OWASP-Benchmark/BenchmarkJava.git
```

### Custom Sampling Strategy

For targeted testing:

```yaml
dataset:
  sample_size: 500
  random_seed: 12345  # Change for different sample
```

### Adjusting Token Limits

If models are being cut off:

```yaml
judge:
  max_tokens: 2048  # Increase from default 1024
```

Note: Higher token limits increase cost proportionally.
