# Google Vertex AI Setup Guide

This guide walks through setting up the OWASP Security Meta-Evaluator with Google Vertex AI.

## Prerequisites

1. **Google Cloud Project** with Vertex AI API enabled
2. **Authentication** via service account or Application Default Credentials
3. **Billing** enabled on the project

## Step 1: Enable Vertex AI API

```bash
gcloud services enable aiplatform.googleapis.com
```

## Step 2: Set Up Authentication

### Option A: Service Account Key (Recommended for automation)

1. Create a service account:
```bash
gcloud iam service-accounts create meta-evaluator \
    --description="Service account for OWASP Meta-Evaluator" \
    --display-name="Meta-Evaluator"
```

2. Grant Vertex AI User role:
```bash
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:meta-evaluator@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"
```

3. Create and download key:
```bash
gcloud iam service-accounts keys create ~/meta-evaluator-key.json \
    --iam-account=meta-evaluator@YOUR_PROJECT_ID.iam.gserviceaccount.com
```

4. Set environment variables:
```bash
export GOOGLE_APPLICATION_CREDENTIALS="$HOME/meta-evaluator-key.json"
export GCP_PROJECT_ID="YOUR_PROJECT_ID"
export GCP_REGION="us-central1"  # Optional
```

### Option B: Application Default Credentials (Recommended for local dev)

```bash
gcloud auth application-default login
export GCP_PROJECT_ID="YOUR_PROJECT_ID"
```

## Step 3: Install Dependencies

```bash
pip install -e .
```

This will install `google-cloud-aiplatform>=1.62.0` along with other dependencies.

## Step 4: Configure the Evaluator

Use the provided `config.vertex.yaml`:

```bash
cp config.vertex.yaml config.yaml
```

Or edit your existing `config.yaml`:

```yaml
judge:
  provider: "vertex"
  model: "gemini-2.5-pro-latest"
  api_key_env: "GOOGLE_APPLICATION_CREDENTIALS"
  gcp_project_env: "GCP_PROJECT_ID"
  gcp_region_env: "GCP_REGION"
  gcp_location: "us-central1"
```

## Step 5: Run a Test

```bash
meta-eval evaluate --sample-size 10
```

## Available Models

| Model | Speed | Cost (per 1M tokens) | Best For |
|-------|-------|---------------------|----------|
| `gemini-2.5-pro-latest` | Slower | $1.25 / $5.00 | High accuracy |
| `gemini-2.5-flash-latest` | Fast | $0.075 / $0.30 | Cost efficiency |
| `gemini-1.5-pro` | Medium | $1.25 / $5.00 | Stable version |
| `gemini-1.5-flash` | Fast | $0.075 / $0.30 | Budget runs |

## Cost Estimates

### By Sample Size (Gemini 2.5 Pro)
- 10 cases: $0.04-0.12
- 100 cases: $0.40-1.20
- 500 cases: $2.00-6.00
- 2,740 cases (full): $10-30

### By Sample Size (Gemini 2.5 Flash)
- 10 cases: $0.003-0.01
- 100 cases: $0.03-0.10
- 500 cases: $0.15-0.50
- 2,740 cases (full): $1-3

## Troubleshooting

### Error: "Project ID not set"
```bash
export GCP_PROJECT_ID="your-project-id"
```

### Error: "Permission denied"
Ensure the service account has the `aiplatform.user` role:
```bash
gcloud projects get-iam-policy YOUR_PROJECT_ID \
    --flatten="bindings[].members" \
    --filter="bindings.role:roles/aiplatform.user"
```

### Error: "Quota exceeded"
Check your Vertex AI quotas:
```bash
gcloud alpha services quota list --service=aiplatform.googleapis.com
```

Adjust `requests_per_minute` in `config.yaml` if needed.

### Error: "Model not found in region"
Not all models are available in all regions. Try switching to `us-central1`:
```bash
export GCP_REGION="us-central1"
```

## Regional Availability

As of June 2026, Gemini models are available in:
- `us-central1` (Iowa) - Recommended
- `us-east1` (South Carolina)
- `us-west1` (Oregon)
- `europe-west1` (Belgium)
- `asia-southeast1` (Singapore)

Check [Google Cloud docs](https://cloud.google.com/vertex-ai/generative-ai/docs/learn/locations) for current availability.

## Performance Notes

- **Latency**: Vertex AI typically has 1-3s latency per request (similar to other providers)
- **Rate Limits**: Default is 300 requests/min for Gemini 2.5 Pro (varies by model/region)
- **Concurrent Requests**: Default concurrency of 10 is safe for most quotas
- **Structured Output**: Uses `response_schema` in `GenerationConfig` (similar to OpenAI/Anthropic)

## Differences from Anthropic/OpenAI

| Feature | Vertex AI | Anthropic | OpenAI |
|---------|-----------|-----------|---------|
| **Extended Thinking** | ❌ Not supported | ✅ Adaptive/Disabled | ❌ Not supported |
| **Structured Output** | ✅ JSON Schema | ✅ Native parse | ✅ Native parse |
| **Async API** | ❌ Sync only (wrapped) | ✅ Native async | ✅ Native async |
| **Token Counting** | `usage_metadata` | `usage` | `usage` |
| **Authentication** | GCP project + ADC/SA | API key | API key |
| **Regional Endpoints** | ✅ Required | ❌ Global | ❌ Global |

## Next Steps

1. Compare results across providers:
```bash
# Run with Claude
meta-eval evaluate --sample-size 100  # Using config.yaml with Anthropic

# Run with Gemini
cp config.vertex.yaml config.yaml
meta-eval evaluate --sample-size 100
```

2. Analyze cost/accuracy tradeoffs by examining `results/scorecard.json`

3. For production runs, use Gemini 2.5 Flash for cost efficiency, then validate high-confidence findings with Pro
