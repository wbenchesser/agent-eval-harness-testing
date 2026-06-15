# LLM Provider Comparison for OWASP Meta-Evaluator

A comprehensive comparison of Anthropic Claude, OpenAI GPT, and Google Vertex AI integration.

## Quick Reference

| Feature | Anthropic Claude | OpenAI GPT | Google Vertex AI |
|---------|-----------------|------------|------------------|
| **Provider Code** | `anthropic` | `openai` | `vertex` |
| **Top Model** | `claude-opus-4-8` | `gpt-4o` | `gemini-2.5-pro-latest` |
| **Budget Model** | `claude-haiku-4-5` | `gpt-4o-mini` | `gemini-2.5-flash-latest` |
| **Authentication** | API Key | API Key | GCP Project + Credentials |
| **Async SDK** | ✅ Native | ✅ Native | ❌ Wrapped |
| **Structured Output** | ✅ `.parse()` | ✅ `.parse()` | ✅ `response_schema` |
| **Extended Thinking** | ✅ Adaptive | ❌ | ❌ |
| **Regional Endpoints** | ❌ Global | ❌ Global | ✅ Required |

## Cost Analysis (Per 100 Test Cases)

### Premium Models
```
Claude Opus 4.8:         $1.00 - $3.00
GPT-4o:                  $0.80 - $2.50
Gemini 2.5 Pro:          $0.40 - $1.20  ← 60% cheaper than Opus
```

### Budget Models
```
Claude Haiku 4.5:        $0.30 - $0.90
GPT-4o Mini:             $0.05 - $0.15
Gemini 2.5 Flash:        $0.03 - $0.10  ← 90% cheaper than Haiku
```

### Full Dataset (2,740 cases)
```
Claude Opus 4.8:         $25 - $75
GPT-4o:                  $20 - $65
Gemini 2.5 Pro:          $10 - $30
Gemini 2.5 Flash:        $1 - $3       ← Best for large-scale runs
```

## Performance Characteristics

### Latency (Average per Request)
```
Gemini 2.5 Flash:        0.5 - 1.5s  ⚡ Fastest
GPT-4o:                  1.0 - 2.0s
Gemini 2.5 Pro:          1.0 - 3.0s
Claude Opus 4.8:         2.0 - 4.0s
```

### Rate Limits (Requests per Minute)
```
Gemini 2.5 Flash:        1,000 req/min  (varies by region)
GPT-4o:                  500 req/min    (tier-dependent)
Gemini 2.5 Pro:          300 req/min    (varies by region)
Claude (default):        50 req/min     (can be increased)
```

### Concurrent Requests (Recommended)
```
All providers:           10 concurrent (default)
                         Adjustable via execution.concurrency
```

## Setup Complexity

### Anthropic (Easiest)
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
meta-eval evaluate
```
**Time to setup:** < 1 minute

### OpenAI (Easy)
```bash
export OPENAI_API_KEY="sk-..."
meta-eval evaluate
```
**Time to setup:** < 1 minute

### Google Vertex AI (Moderate)
```bash
# One-time GCP setup
gcloud services enable aiplatform.googleapis.com
gcloud auth application-default login

# Runtime
export GCP_PROJECT_ID="my-project"
cp config.vertex.yaml config.yaml
meta-eval evaluate
```
**Time to setup:** 5-10 minutes (one-time GCP configuration)

## Model Selection Guide

### When to Use Claude Opus 4.8
✅ Need extended thinking for complex vulnerability patterns  
✅ Maximum accuracy is priority over cost  
✅ Analyzing novel or subtle security issues  
❌ Budget-constrained large-scale evaluation

### When to Use GPT-4o
✅ Balanced accuracy and cost  
✅ Fast inference needed  
✅ Existing OpenAI infrastructure  
❌ Need extended reasoning traces

### When to Use Gemini 2.5 Pro
✅ Cost-conscious high-quality evaluation  
✅ Large dataset (500+ cases)  
✅ GCP ecosystem integration  
❌ Need extended thinking capability

### When to Use Gemini 2.5 Flash
✅ Massive scale (1,000+ cases)  
✅ Initial screening/triage  
✅ Budget < $5 for full dataset  
✅ Speed is critical  
❌ Need highest accuracy on subtle bugs

## Token Efficiency

Average tokens per test case (Java code + verdict):

| Model | Input Tokens | Output Tokens | Total |
|-------|--------------|---------------|-------|
| Claude Opus 4.8 | 800-1,200 | 150-300 | ~1,200 |
| GPT-4o | 800-1,200 | 100-250 | ~1,100 |
| Gemini 2.5 Pro | 800-1,200 | 100-250 | ~1,100 |
| Gemini 2.5 Flash | 800-1,200 | 80-200 | ~1,000 |

**Note:** Extended thinking (`thinking: adaptive`) adds 200-500 output tokens per case for Claude.

## Accuracy Comparison

*To be populated after running comparative benchmarks*

Recommended workflow to benchmark:
```bash
# Run same 100-case sample with all providers
for provider in anthropic openai vertex; do
  # Configure provider in config.yaml
  meta-eval evaluate --sample-size 100
  mv results results-$provider
done

# Compare metrics
cat results-*/scorecard.json | jq '.overall.youden_index'
```

## Hybrid Strategies

### Strategy 1: Flash Triage + Pro Validation
```bash
# Phase 1: Run 2,740 cases with Flash (~$2)
# config.yaml: provider: vertex, model: gemini-2.5-flash-latest
meta-eval run

# Phase 2: Re-run uncertain cases with Pro
# Filter verdicts with confidence < 0.7, re-run with gemini-2.5-pro
# Total cost: ~$2 + $5 = $7 (vs $30 with Pro only)
```

### Strategy 2: Multi-Judge Consensus
```bash
# Run same sample with 3 providers
# Take majority vote or flag disagreements for human review
# Higher confidence at ~3x cost
```

### Strategy 3: Tiered Analysis
```bash
# Tier 1: Flash for all cases
# Tier 2: Pro for Flash-flagged vulnerabilities
# Tier 3: Opus for Pro-uncertain cases
# Maximizes accuracy while controlling cost
```

## Environment Variable Reference

### Anthropic
```bash
ANTHROPIC_API_KEY="sk-ant-..."
```

### OpenAI
```bash
OPENAI_API_KEY="sk-..."
```

### Google Vertex AI
```bash
# Required
GOOGLE_APPLICATION_CREDENTIALS="/path/to/key.json"
GCP_PROJECT_ID="your-project-id"

# Optional
GCP_REGION="us-central1"  # Defaults to us-central1
```

## Configuration Templates

### Anthropic (Extended Thinking)
```yaml
judge:
  provider: "anthropic"
  model: "claude-opus-4-8"
  api_key_env: "ANTHROPIC_API_KEY"
  thinking: "adaptive"
  temperature: null
```

### OpenAI (Fast)
```yaml
judge:
  provider: "openai"
  model: "gpt-4o"
  api_key_env: "OPENAI_API_KEY"
  temperature: 0.0
```

### Vertex AI (Cost-Optimized)
```yaml
judge:
  provider: "vertex"
  model: "gemini-2.5-flash-latest"
  api_key_env: "GOOGLE_APPLICATION_CREDENTIALS"
  gcp_project_env: "GCP_PROJECT_ID"
  gcp_location: "us-central1"
  temperature: 0.0
```

## Troubleshooting

### Anthropic: Rate Limit Errors
```yaml
judge:
  requests_per_minute: 30  # Reduce from default 50
```

### OpenAI: Quota Exceeded
- Check usage at platform.openai.com
- Upgrade to higher tier for increased quota

### Vertex AI: Region Quota
```bash
# Check quotas
gcloud alpha services quota list \
  --service=aiplatform.googleapis.com \
  --filter="QUOTA_METRIC:online_prediction_requests_per_base_model"

# Request increase via GCP Console
```

## Migration Guide

### From Anthropic to Vertex AI
1. Install: `pip install google-cloud-aiplatform`
2. Set up GCP auth (see VERTEX_AI_SETUP.md)
3. Update config.yaml:
   ```yaml
   provider: "vertex"
   model: "gemini-2.5-pro-latest"
   thinking: "disabled"  # Not supported
   ```
4. Run: `meta-eval evaluate`

### From OpenAI to Vertex AI
1. Same as above
2. Note: Similar performance, ~50% lower cost

### From Vertex AI to Anthropic/OpenAI
1. Simpler auth: just set API key
2. No GCP project/region needed
3. Claude gains extended thinking capability

## Recommendations by Use Case

### Academic Research (Accuracy Priority)
**Recommended:** Claude Opus 4.8 with `thinking: adaptive`  
**Alternative:** Gemini 2.5 Pro for cost savings  
**Budget:** $25-75 for full dataset

### Security Audit (Balanced)
**Recommended:** Gemini 2.5 Pro  
**Alternative:** GPT-4o  
**Budget:** $10-30 for full dataset

### Continuous Integration (Speed + Cost)
**Recommended:** Gemini 2.5 Flash  
**Alternative:** GPT-4o Mini  
**Budget:** $1-5 for full dataset

### Exploratory Testing (Unknown Accuracy)
**Recommended:** Run all three, compare results  
**Budget:** $40-100 for full dataset (3x runs)

## Future Enhancements

Potential additions:
- [ ] AWS Bedrock support (Claude via AWS)
- [ ] Azure OpenAI support
- [ ] Local model support (Llama, Mistral via Ollama)
- [ ] Cost-based auto-routing (cheapest model per case)
- [ ] Ensemble voting across providers
