# Migration Summary: Streamlined to Red Hat Corporate Endpoint Only

## Overview

The OWASP Security Meta-Evaluator has been streamlined to exclusively use Red Hat Corporate Vertex AI (models.corp). All public API providers (Anthropic, OpenAI, Google Vertex AI) have been removed.

## What Changed

### ✅ Simplified Architecture
- **Single provider**: Red Hat Corporate Vertex AI only
- **Fewer dependencies**: Removed 3 SDK packages (`anthropic`, `openai`, `google-cloud-aiplatform`)
- **Cleaner configuration**: No provider selection, no API key juggling
- **Streamlined docs**: Single setup guide instead of multiple provider guides

### ❌ Removed Features
- Public Anthropic API support
- OpenAI API support
- Google Vertex AI (Gemini) support
- Multi-provider configuration options
- Provider comparison documentation

### ✨ New Features
- Simplified httpx-based client (no heavy SDK dependencies)
- Better error messages for corporate endpoint setup
- Comprehensive setup guide tailored for Red Hat infrastructure

## File Changes

### Deleted Files (11 files)
```
config.vertex.yaml              # Google Vertex AI config
VERTEX_AI_SETUP.md             # Google setup guide
VERTEX_AI_INTEGRATION.md       # Google integration docs
PROVIDER_COMPARISON.md         # Multi-provider comparison
CORPORATE_VERTEX_SETUP.md      # Corporate-specific setup (merged into SETUP.md)
QUICKSTART_CORPORATE.md        # Corporate quick start (merged into QUICKSTART.md)
INTEGRATION_SUMMARY.md         # Corporate integration details (no longer needed)
CHANGELOG_CORPORATE.md         # Corporate changelog (superseded by CHANGELOG.md)
```

### Modified Files (6 files)
```
src/meta_evaluator/judge/client.py   # Removed multi-provider logic, simplified to httpx
src/meta_evaluator/config.py         # Removed provider field and GCP settings
pyproject.toml                        # Removed anthropic, openai, google-cloud-aiplatform
config.yaml                           # Simplified, removed provider field
README.md                             # Updated Quick Start for corporate-only
QUICKSTART.md                         # Rewritten for corporate endpoint
META_EVALUATOR.md                     # Updated to remove multi-provider references
```

### Created Files (2 files)
```
SETUP.md         # Comprehensive corporate endpoint setup guide
CHANGELOG.md     # Complete project changelog
```

## Code Changes

### Before (Multi-Provider)
```python
# config.py
class JudgeConfig(BaseModel):
    provider: Literal["anthropic", "openai", "vertex", "vertex-corporate"]
    model: str
    api_key_env: str
    gcp_project_env: str = "GCP_PROJECT_ID"
    # ... many more fields

# client.py
if config.provider == "anthropic":
    self.client = AsyncAnthropic(...)
elif config.provider == "openai":
    self.client = AsyncOpenAI(...)
elif config.provider == "vertex":
    self.client = GenerativeModel(...)
elif config.provider == "vertex-corporate":
    self.client = httpx.AsyncClient(...)
```

### After (Corporate-Only)
```python
# config.py
class JudgeConfig(BaseModel):
    model: str
    vertex_corp_api_env: str = "MODEL_API"
    vertex_corp_key_env: str = "USER_KEY"
    # ... fewer fields, no provider selection

# client.py
# Red Hat Corporate Vertex AI endpoint
self.client = httpx.AsyncClient(...)
self.corp_api_base = config.get_vertex_corp_api()
self.corp_user_key = config.get_vertex_corp_key()
```

## Configuration Changes

### Before (v0.1.0)
```yaml
judge:
  provider: "anthropic"  # or "openai" or "vertex"
  model: "claude-opus-4-8"
  api_key_env: "ANTHROPIC_API_KEY"
```

### After (v0.2.0)
```yaml
judge:
  model: "claude-haiku-4-5@20251001"
  vertex_corp_api_env: "MODEL_API"
  vertex_corp_key_env: "USER_KEY"
```

## Environment Variables

### Before
```bash
# Public Anthropic
export ANTHROPIC_API_KEY="sk-ant-..."

# OpenAI
export OPENAI_API_KEY="sk-..."

# Google Vertex AI
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/key.json"
export GCP_PROJECT_ID="project-id"
```

### After
```bash
# Red Hat Corporate Vertex AI only
export MODEL_API="https://claude--apicast-production.apps.int.stc.ai.prod.us-east-1.aws.paas.redhat.com:443"
export USER_KEY="your-models-corp-credential"
```

## Dependencies

### Before (pyproject.toml)
```toml
dependencies = [
    "anthropic>=0.52.0",         # 10+ MB
    "openai>=1.30.0",            # 8+ MB
    "google-cloud-aiplatform>=1.62.0",  # 50+ MB
    "pyyaml>=6.0",
    "pydantic>=2.7",
    "tabulate>=0.9",
    "httpx>=0.27",
]
```

### After (pyproject.toml)
```toml
dependencies = [
    "pyyaml>=6.0",
    "pydantic>=2.7",
    "tabulate>=0.9",
    "httpx>=0.27",
]
```

**Installation size reduced by ~70 MB**

## Model Support

### Before
- Claude Opus/Sonnet/Haiku (via public Anthropic API)
- GPT-4o/GPT-4o-mini (via OpenAI API)
- Gemini 2.5 Pro/Flash (via Google Vertex AI)

### After
- Claude Haiku 4.5 (`claude-haiku-4-5@20251001`)
- Claude Sonnet 4.6 (`claude-sonnet-4-6@20250514`)
- Claude Opus 4.8 (`claude-opus-4-8@20250514`)

All via Red Hat Corporate Vertex AI endpoint.

## Cost Estimates

### 100 Test Cases

**Before (Multi-Provider Options)**
- Claude Opus (public): $1.00-3.00
- GPT-4o: $0.80-2.50
- Gemini 2.5 Pro: $0.40-1.20
- Gemini 2.5 Flash: $0.03-0.10

**After (Corporate-Only)**
- Claude Haiku: $0.50-1.50 (recommended)
- Claude Sonnet: $1.50-4.50
- Claude Opus: $2.50-7.50

All costs billed through Red Hat corporate infrastructure.

## Migration Steps

### For Existing Users

1. **Update environment variables**:
   ```bash
   # Remove old variables
   unset ANTHROPIC_API_KEY
   unset OPENAI_API_KEY
   unset GOOGLE_APPLICATION_CREDENTIALS
   unset GCP_PROJECT_ID
   unset GCP_REGION
   
   # Set new variables
   export MODEL_API="https://claude--apicast-production.apps.int.stc.ai.prod.us-east-1.aws.paas.redhat.com:443"
   export USER_KEY="your-models-corp-credential"
   ```

2. **Update config.yaml**:
   ```bash
   # Backup old config
   cp config.yaml config.yaml.backup
   
   # The new config.yaml should look like:
   judge:
     model: "claude-haiku-4-5@20251001"
     vertex_corp_api_env: "MODEL_API"
     vertex_corp_key_env: "USER_KEY"
   ```

3. **Reinstall dependencies**:
   ```bash
   pip install -e .
   ```

4. **Test connection**:
   ```bash
   python3 test_corporate_endpoint.py
   ```

5. **Run evaluation**:
   ```bash
   meta-eval evaluate --sample-size 10
   ```

### For New Users

Just follow [SETUP.md](SETUP.md) - no migration needed!

## Benefits of This Change

### 1. **Simplified Codebase**
- 70% less dependency bloat
- Single authentication method
- No provider abstraction complexity
- Easier to maintain and debug

### 2. **Red Hat Compliance**
- All data stays within Red Hat infrastructure
- Corporate authentication and auditing
- Quota management via Red Hat processes
- No external API keys to manage

### 3. **Better Developer Experience**
- Single setup guide instead of 4 provider guides
- Clearer error messages
- Faster installation (fewer dependencies)
- Less configuration to manage

### 4. **Security**
- No API keys in environment (uses corporate Bearer token)
- VPN-protected endpoint
- Corporate credential rotation policies
- No data sent to external providers

## Breaking Changes

❌ **These will fail in v0.2.0:**

```bash
# Public Anthropic API
export ANTHROPIC_API_KEY="sk-ant-..."
meta-eval evaluate  # Will fail: no provider field in config

# OpenAI API
export OPENAI_API_KEY="sk-..."
meta-eval evaluate  # Will fail: OpenAI support removed

# Google Vertex AI
export GCP_PROJECT_ID="my-project"
meta-eval evaluate  # Will fail: Vertex AI support removed
```

✅ **Only this works in v0.2.0:**

```bash
# Red Hat Corporate Vertex AI
export MODEL_API="https://claude--apicast-production.apps.int.stc.ai.prod.us-east-1.aws.paas.redhat.com:443"
export USER_KEY="your-credential"
meta-eval evaluate  # ✅ Works!
```

## Rollback Plan

If you need to use public APIs (not recommended), you can:

1. **Checkout v0.1.0**:
   ```bash
   git checkout v0.1.0  # (if using git)
   ```

2. **Or manually restore**:
   - Restore old dependencies in `pyproject.toml`
   - Restore old `src/meta_evaluator/judge/client.py`
   - Restore old `src/meta_evaluator/config.py`
   - Add `provider` field back to `config.yaml`

However, this is **not recommended** as v0.2.0 is optimized for Red Hat infrastructure.

## Testing Checklist

Before deploying v0.2.0:

- [x] Module imports work without errors
- [x] Configuration file parses correctly
- [x] Environment variable validation works
- [ ] Connection test passes (`test_corporate_endpoint.py`)
- [ ] Small evaluation completes (10 cases)
- [ ] Medium evaluation completes (100 cases)
- [ ] Cost tracking is accurate
- [ ] Resumability works (re-run same command)
- [ ] All three models work (Haiku, Sonnet, Opus)

## Support

### For Migration Issues
- Check [SETUP.md](SETUP.md) for current setup instructions
- Run `test_corporate_endpoint.py` to diagnose connection issues
- Verify environment variables: `echo $MODEL_API $USER_KEY`

### For Corporate Endpoint Issues
- Contact Red Hat models.corp team
- Check models.corp platform for credential status
- Verify VPN/network connectivity

### For Evaluator Issues
- Check [META_EVALUATOR.md](META_EVALUATOR.md) for usage documentation
- File issues in this repository
- Review [CHANGELOG.md](CHANGELOG.md) for recent changes

## Version History

- **v0.2.0** (2026-06-16): Streamlined to Red Hat Corporate Vertex AI only
- **v0.1.0** (2026-06-15): Initial multi-provider implementation

## Future Considerations

Potential future enhancements (not planned for immediate implementation):

- Support for other Red Hat AI endpoints if available
- Batch request optimization for corporate endpoint
- Corporate-specific telemetry integration
- Auto-scaling based on corporate quotas

These would all maintain the single-provider architecture focused on Red Hat infrastructure.
