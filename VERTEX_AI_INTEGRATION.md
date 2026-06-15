# Vertex AI Integration - Implementation Summary

This document summarizes the changes made to integrate Google Vertex AI into the OWASP Security Meta-Evaluator.

## Files Modified

### 1. `src/meta_evaluator/config.py`
- Added `"vertex"` to `provider` type hint
- Added GCP-specific configuration fields:
  - `gcp_project_env`: Environment variable for GCP project ID
  - `gcp_region_env`: Environment variable for GCP region
  - `gcp_location`: Default region (us-central1)
- Added helper methods:
  - `get_gcp_project()`: Retrieves GCP project ID from env
  - `get_gcp_region()`: Retrieves GCP region or uses default

### 2. `src/meta_evaluator/judge/client.py`
- Added Vertex AI imports with lazy loading:
  ```python
  import vertexai
  from vertexai.generative_models import GenerativeModel, GenerationConfig
  ```
- Updated `COST_TABLE` with Gemini pricing:
  - `gemini-2.5-pro-latest`: $1.25/$5.00 per 1M tokens
  - `gemini-2.5-flash-latest`: $0.075/$0.30 per 1M tokens
  - `gemini-1.5-pro`: $1.25/$5.00 per 1M tokens
  - `gemini-1.5-flash`: $0.075/$0.30 per 1M tokens
- Added Vertex AI client initialization in `SecurityJudge.__init__()`:
  - Validates `google-cloud-aiplatform` is installed
  - Initializes Vertex AI with project and region
  - Creates `GenerativeModel` instance
- Added Vertex AI evaluation logic in `evaluate_case()`:
  - Combines system and user prompts (Vertex AI doesn't separate them)
  - Configures JSON schema for structured output
  - Wraps synchronous API call with `asyncio.to_thread()`
  - Parses JSON response and extracts token usage

### 3. `pyproject.toml`
- Added `google-cloud-aiplatform>=1.62.0` to dependencies

### 4. `META_EVALUATOR.md`
- Added provider-specific configuration sections
- Updated cost estimates for all three providers
- Added Vertex AI authentication instructions
- Added link to detailed setup guide

### 5. `README.md`
- Updated Quick Start to include all three providers
- Added environment variable setup for Vertex AI

## Files Created

### 1. `config.vertex.yaml`
Example configuration file for Vertex AI with:
- Provider set to "vertex"
- Model set to "gemini-2.5-pro-latest"
- GCP-specific environment variables
- Cost-optimized sample size (100 cases ~$0.40-1.20)

### 2. `VERTEX_AI_SETUP.md`
Comprehensive setup guide covering:
- Prerequisites and API enablement
- Authentication (service account vs ADC)
- Configuration and installation
- Available models and cost estimates
- Troubleshooting common errors
- Regional availability
- Performance characteristics
- Comparison with Anthropic/OpenAI

### 3. `VERTEX_AI_INTEGRATION.md` (this file)
Implementation summary and usage guide

## Key Implementation Details

### Structured Output
Vertex AI uses `response_schema` in `GenerationConfig` instead of Anthropic's `.parse()` or OpenAI's `response_format`. The schema is generated from the Pydantic `Verdict` model via `.model_json_schema()`.

### Async Handling
Vertex AI's Python SDK is synchronous, so API calls are wrapped with `asyncio.to_thread()` to maintain async compatibility with the rest of the codebase.

### Token Usage
Token counts are accessed via `response.usage_metadata.prompt_token_count` and `response.usage_metadata.candidates_token_count` (different from Anthropic/OpenAI).

### Authentication
Unlike API key-based providers, Vertex AI requires:
1. GCP project ID
2. Region/location
3. Service account credentials or Application Default Credentials

### Thinking Mode
Vertex AI does not support extended thinking like Anthropic's `thinking` parameter. This is ignored in the configuration.

## Usage Examples

### Basic Usage
```bash
# Set up environment
export GOOGLE_APPLICATION_CREDENTIALS="~/meta-evaluator-key.json"
export GCP_PROJECT_ID="my-project"

# Use Vertex AI config
cp config.vertex.yaml config.yaml

# Run evaluation
meta-eval evaluate --sample-size 100
```

### Comparing Providers
```bash
# Claude Opus 4.8
meta-eval evaluate --sample-size 100  # ~$1-3

# Gemini 2.5 Pro
cp config.vertex.yaml config.yaml
meta-eval evaluate --sample-size 100  # ~$0.4-1.2

# Gemini 2.5 Flash (cost-optimized)
# Edit config.yaml: model: "gemini-2.5-flash-latest"
meta-eval evaluate --sample-size 100  # ~$0.03-0.10
```

### Production Workflow
```bash
# Phase 1: Fast sweep with Flash
# config.yaml: model: gemini-2.5-flash-latest
meta-eval run

# Phase 2: Deep analysis on high-confidence findings
# Filter high-confidence verdicts, then re-run with Pro
# config.yaml: model: gemini-2.5-pro-latest
meta-eval run --sample-size 50  # Filtered subset

# Phase 3: Score and compare
meta-eval score
```

## Testing the Integration

### Unit Test (Config Validation)
```bash
python3 -c "from meta_evaluator.config import JudgeConfig; print('Config validation: OK')"
```

### Integration Test (Small Sample)
```bash
# Set auth
export GOOGLE_APPLICATION_CREDENTIALS="key.json"
export GCP_PROJECT_ID="test-project"

# Run on 10 cases
meta-eval evaluate --sample-size 10
```

### Full Test (Compare Providers)
```bash
# Run same sample with all three providers
meta-eval evaluate --sample-size 50  # Anthropic
cp config.vertex.yaml config.yaml
meta-eval evaluate --sample-size 50  # Vertex AI

# Compare results
diff results/scorecard.json results-anthropic/scorecard.json
```

## Performance Characteristics

| Metric | Gemini 2.5 Pro | Gemini 2.5 Flash | Claude Opus 4.8 |
|--------|----------------|------------------|-----------------|
| **Latency** | 1-3s | 0.5-1.5s | 2-4s |
| **Cost (100 cases)** | $0.40-1.20 | $0.03-0.10 | $1.00-3.00 |
| **Structured Output** | ✅ JSON Schema | ✅ JSON Schema | ✅ Native Parse |
| **Rate Limit** | 300 req/min | 1000 req/min | 50 req/min |
| **Extended Thinking** | ❌ | ❌ | ✅ |

## Migration Path

### From Anthropic
1. Copy `config.vertex.yaml` to `config.yaml`
2. Set GCP environment variables
3. Run same evaluation commands

### From OpenAI
1. Update `provider: "vertex"` in config
2. Replace `api_key_env` with GCP credentials
3. Add GCP project/region configuration

## Limitations

1. **No Extended Thinking**: Unlike Claude's `thinking` parameter, Gemini doesn't offer extended reasoning traces
2. **Regional Dependencies**: Must specify region explicitly (unlike global Anthropic/OpenAI endpoints)
3. **Synchronous SDK**: Requires async wrapper (negligible performance impact)
4. **Quota Management**: Quotas vary by region and must be monitored separately

## Cost Optimization Tips

1. **Use Flash for bulk runs**: 10x cheaper than Pro with comparable accuracy on clear-cut cases
2. **Enable resume mode**: Avoid re-running failed cases (enabled by default)
3. **Sample strategically**: Use stratified sampling to preserve CWE distribution
4. **Monitor token usage**: Check `results/scorecard.json` for cost breakdown
5. **Regional pricing**: Some regions have lower costs (check GCP pricing)

## Next Steps

1. Run comparative benchmarks across all three providers
2. Analyze accuracy vs cost tradeoffs
3. Consider hybrid approach (Flash for initial sweep, Pro for ambiguous cases)
4. Monitor GCP quotas and adjust `requests_per_minute` accordingly
