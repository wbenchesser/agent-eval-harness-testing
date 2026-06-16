# Changelog

All notable changes to the OWASP Security Meta-Evaluator project.

## [0.2.0] - 2026-06-16

### Changed - Streamlined to Red Hat Corporate Endpoint Only

**BREAKING CHANGES**: This version removes support for public Anthropic, OpenAI, and Google Vertex AI providers. Only Red Hat Corporate Vertex AI is supported.

#### Core Changes
- **Simplified provider architecture**: Removed multi-provider abstraction
- **Single provider**: Now exclusively uses Red Hat Corporate Vertex AI (models.corp)
- **Reduced dependencies**: Removed `anthropic`, `openai`, and `google-cloud-aiplatform` packages
- **Streamlined configuration**: Removed provider selection, GCP project settings, and public API key fields

#### Code Changes
- `src/meta_evaluator/judge/client.py`:
  - Removed AsyncAnthropic, AsyncOpenAI, and vertexai imports
  - Removed multi-provider conditional logic
  - Simplified to single httpx-based client for corporate endpoint
  - Removed Anthropic, OpenAI, and Gemini model pricing from COST_TABLE
  - Kept only Claude versioned models: `claude-{tier}-{version}@{date}`

- `src/meta_evaluator/config.py`:
  - Changed `JudgeConfig.provider` from `Literal["anthropic", "openai", "vertex", "vertex-corporate"]` to removed entirely
  - Removed `api_key_env`, `gcp_project_env`, `gcp_region_env`, `gcp_location` fields
  - Kept only `vertex_corp_api_env` and `vertex_corp_key_env`
  - Removed `get_api_key()`, `get_gcp_project()`, `get_gcp_region()` helper methods
  - Enhanced error messages for corporate endpoint configuration

- `pyproject.toml`:
  - Bumped version to 0.2.0
  - Updated description to mention Red Hat Corporate Vertex AI
  - Removed dependencies: `anthropic>=0.52.0`, `openai>=1.30.0`, `google-cloud-aiplatform>=1.62.0`
  - Kept only: `pyyaml`, `pydantic`, `tabulate`, `httpx`

#### Configuration Changes
- `config.yaml` (formerly `config.corp.yaml`):
  - Removed `provider` field
  - Removed `api_key_env` field
  - Now defaults to Haiku model for cost efficiency
  - Simplified comments to remove multi-provider references

#### Documentation Changes
- **Removed Files**:
  - `VERTEX_AI_SETUP.md` - Google Vertex AI setup
  - `VERTEX_AI_INTEGRATION.md` - Google Vertex AI implementation details
  - `PROVIDER_COMPARISON.md` - Multi-provider comparison
  - `CORPORATE_VERTEX_SETUP.md` - Corporate-specific setup (merged into SETUP.md)
  - `QUICKSTART_CORPORATE.md` - Corporate quick start (merged into QUICKSTART.md)
  - `INTEGRATION_SUMMARY.md` - Corporate integration details (no longer needed)
  - `CHANGELOG_CORPORATE.md` - Corporate-specific changelog (superseded by this file)
  - Old `config.yaml` and `config.vertex.yaml`

- **Updated Files**:
  - `README.md`: Updated Quick Start to show only corporate endpoint
  - `QUICKSTART.md`: Rewritten for corporate endpoint only, updated cost estimates
  - `META_EVALUATOR.md`: Updated to reflect single provider, removed provider comparison sections
  - `SETUP.md`: New comprehensive setup guide (replaces CORPORATE_VERTEX_SETUP.md)

#### Model Support
Available models (all via Red Hat Corporate Vertex AI):
- `claude-haiku-4-5@20251001` - $1.00/$5.00 per 1M tokens (input/output)
- `claude-sonnet-4-6@20250514` - $3.00/$15.00 per 1M tokens
- `claude-opus-4-8@20250514` - $5.00/$25.00 per 1M tokens

#### Migration Guide

**From version 0.1.0 (multi-provider) to 0.2.0 (corporate-only)**:

1. **Update environment variables**:
   ```bash
   # Remove old variables
   unset ANTHROPIC_API_KEY
   unset OPENAI_API_KEY
   unset GOOGLE_APPLICATION_CREDENTIALS
   unset GCP_PROJECT_ID
   
   # Set new variables
   export MODEL_API="https://claude--apicast-production.apps.int.stc.ai.prod.us-east-1.aws.paas.redhat.com:443"
   export USER_KEY="your-models-corp-credential"
   ```

2. **Update config.yaml**:
   ```yaml
   # Old (0.1.0)
   judge:
     provider: "anthropic"
     model: "claude-opus-4-8"
     api_key_env: "ANTHROPIC_API_KEY"
   
   # New (0.2.0)
   judge:
     model: "claude-haiku-4-5@20251001"  # Use versioned model ID
     vertex_corp_api_env: "MODEL_API"
     vertex_corp_key_env: "USER_KEY"
   ```

3. **Reinstall dependencies**:
   ```bash
   pip install -e .  # Will install only corporate endpoint dependencies
   ```

4. **Test connection**:
   ```bash
   python3 test_corporate_endpoint.py
   ```

### Why This Change?

- **Simplified codebase**: Single provider means less complexity, easier maintenance
- **Red Hat compliance**: Corporate endpoint ensures data stays within Red Hat infrastructure
- **Cost control**: Corporate quotas and billing aligned with Red Hat processes
- **Security**: No external API keys to manage, uses corporate authentication

### Breaking Changes Summary

- ❌ Removed: Public Anthropic API support
- ❌ Removed: OpenAI API support
- ❌ Removed: Google Vertex AI support
- ❌ Removed: `provider` configuration field
- ❌ Removed: `api_key_env`, `gcp_project_env`, `gcp_region_env` configuration fields
- ✅ Required: Red Hat Corporate Vertex AI credentials (`MODEL_API`, `USER_KEY`)
- ✅ Required: Versioned Claude model IDs (e.g., `claude-haiku-4-5@20251001`)

---

## [0.1.0] - 2026-06-15

### Added - Initial Implementation

#### Core Features
- **OWASP Benchmark Integration**: Load and parse 2,740 test cases from OWASP Benchmark
- **Multi-Provider Support**: Anthropic, OpenAI, and Google Vertex AI
- **Stratified Sampling**: Preserve CWE distribution and TP/TN ratio in samples
- **Structured Output**: JSON verdict parsing with Pydantic validation
- **Code-Instruction Isolation**: System prompt ignores code comments to prevent cheating
- **Async Execution**: Concurrent API calls with rate limiting
- **Cost Tracking**: Token usage and cost estimates per provider
- **Resumability**: Skip already-evaluated test cases on re-run
- **Meta-Scoring**: Confusion matrix, TPR/FPR, Youden Index per CWE

#### Architecture
- `meta_evaluator/dataset/`: Dataset loading, sampling, and validation
- `meta_evaluator/judge/`: LLM client abstraction, prompts, verdict models
- `meta_evaluator/scoring/`: Metric computation and reporting
- `meta_evaluator/cli.py`: Command-line interface with subcommands

#### Commands
- `meta-eval scaffold`: Explore dataset without API calls
- `meta-eval run`: Execute security judge on all/sampled cases
- `meta-eval score`: Compute metrics from existing verdicts
- `meta-eval evaluate`: Full pipeline (scaffold → run → score)

#### Providers
- **Anthropic**: Claude Opus/Sonnet/Haiku via AsyncAnthropic SDK
- **OpenAI**: GPT-4o/GPT-4o-mini via AsyncOpenAI SDK
- **Google Vertex AI**: Gemini 2.5 Pro/Flash via vertexai SDK

#### Documentation
- `README.md`: Project overview and custom approach explanation
- `META_EVALUATOR.md`: Full documentation and usage guide
- `QUICKSTART.md`: 5-minute quick start tutorial
- `VERTEX_AI_SETUP.md`: Google Vertex AI setup instructions
- `VERTEX_AI_INTEGRATION.md`: Technical implementation details
- `PROVIDER_COMPARISON.md`: Cost/performance comparison across providers

### Known Issues (0.1.0)
- Extended thinking only supported on Anthropic provider
- Vertex AI SDK is synchronous (wrapped with asyncio.to_thread)
- No support for Red Hat corporate endpoints (addressed in 0.2.0)
