# Documentation Index

Quick navigation to all documentation for the OWASP Security Meta-Evaluator.

## Quick Start (Choose One)

**New Users → Start Here:**
1. [QUICKSTART.md](QUICKSTART.md) - 5-minute tutorial to run your first evaluation
2. [SETUP.md](SETUP.md) - Comprehensive setup guide

**Existing Users (from v0.1.0) → Start Here:**
1. [MIGRATION_SUMMARY.md](MIGRATION_SUMMARY.md) - Changes from multi-provider to corporate-only
2. [CHANGELOG.md](CHANGELOG.md) - Detailed version history

## Core Documentation

### [README.md](README.md)
**What**: Project overview, foundations, concepts, how it works  
**When to read**: First time learning about the project  
**Audience**: Anyone wanting to understand what this project does

### [QUICKSTART.md](QUICKSTART.md)
**What**: 5-minute tutorial to run your first evaluation  
**When to read**: You have credentials and want to test immediately  
**Audience**: Developers who want to get started fast

### [SETUP.md](SETUP.md)
**What**: Complete setup guide with troubleshooting  
**When to read**: Detailed setup instructions, fixing issues  
**Audience**: New users, troubleshooting connection problems

### [META_EVALUATOR.md](META_EVALUATOR.md)
**What**: Full documentation on usage, commands, configuration  
**When to read**: After setup, want to understand all features  
**Audience**: Regular users wanting to customize and optimize

## Reference Documentation

### [CHANGELOG.md](CHANGELOG.md)
**What**: Version history and breaking changes  
**When to read**: Upgrading versions, understanding changes  
**Audience**: Maintainers, users tracking version differences

### [MIGRATION_SUMMARY.md](MIGRATION_SUMMARY.md)
**What**: Migration guide from v0.1.0 to v0.2.0  
**When to read**: Upgrading from multi-provider to corporate-only  
**Audience**: Existing users of v0.1.0

## By Use Case

### "I want to run my first evaluation"
1. [SETUP.md](SETUP.md) - Set up credentials
2. [QUICKSTART.md](QUICKSTART.md) - Run first evaluation
3. [META_EVALUATOR.md](META_EVALUATOR.md) - Learn more commands

### "I'm getting connection errors"
1. [SETUP.md](SETUP.md) - Troubleshooting section
2. Run `test_corporate_endpoint.py` for diagnostics
3. Check environment: `echo $MODEL_API $USER_KEY`

### "I want to understand what this project does"
1. [README.md](README.md) - Overview and concepts
2. [META_EVALUATOR.md](META_EVALUATOR.md) - Technical details

### "I used v0.1.0 and need to upgrade"
1. [MIGRATION_SUMMARY.md](MIGRATION_SUMMARY.md) - What changed
2. [CHANGELOG.md](CHANGELOG.md) - Full version history
3. [SETUP.md](SETUP.md) - New setup process

### "I want to customize my evaluation"
1. [META_EVALUATOR.md](META_EVALUATOR.md) - Configuration options
2. Edit `config.yaml` - Model selection, sample size, etc.
3. [SETUP.md](SETUP.md) - Advanced configuration section

### "I want to compare different models"
1. [SETUP.md](SETUP.md) - Available models section
2. [META_EVALUATOR.md](META_EVALUATOR.md) - Usage examples
3. Run evaluations with different models in `config.yaml`

### "I'm developing or contributing"
1. [CHANGELOG.md](CHANGELOG.md) - Current state
2. [META_EVALUATOR.md](META_EVALUATOR.md) - Architecture
3. Run `pytest` for tests

## File Structure

```
├── README.md                   # Project overview
├── QUICKSTART.md              # 5-minute tutorial
├── SETUP.md                   # Complete setup guide
├── META_EVALUATOR.md          # Full documentation
├── CHANGELOG.md               # Version history
├── MIGRATION_SUMMARY.md       # v0.1.0 → v0.2.0 migration
├── DOCS.md                    # This file
├── config.yaml                # Configuration file
├── test_corporate_endpoint.py # Connection test script
├── pyproject.toml             # Dependencies
└── src/meta_evaluator/        # Source code
    ├── cli.py                 # Command-line interface
    ├── config.py              # Configuration loading
    ├── dataset/               # OWASP benchmark loading
    ├── judge/                 # LLM client and prompts
    └── scoring/               # Metrics and reporting
```

## External Resources

- [OWASP Benchmark Project](https://owasp.org/www-project-benchmark/)
- [OWASP Benchmark GitHub](https://github.com/OWASP-Benchmark/BenchmarkJava)
- [Red Hat AI/ML Documentation](https://docs.redhat.com/) (internal)
- [models.corp Platform](https://models.corp/) (internal)

## Quick Links

**Setup & Installation**
- [Prerequisites](SETUP.md#prerequisites)
- [Environment Variables](SETUP.md#quick-setup-5-minutes)
- [Test Connection](SETUP.md#4-test-connection)
- [Troubleshooting](SETUP.md#troubleshooting)

**Usage**
- [Run First Evaluation](QUICKSTART.md#run-your-first-evaluation-10-cases-30-seconds)
- [Available Models](SETUP.md#available-models)
- [Cost Estimates](SETUP.md#cost-estimates)
- [Commands Reference](META_EVALUATOR.md#usage)

**Configuration**
- [Config File Format](META_EVALUATOR.md#configuration)
- [Model Selection](SETUP.md#available-models)
- [Advanced Options](SETUP.md#advanced-configuration)

**Understanding Results**
- [Metrics Explanation](QUICKSTART.md#understanding-results)
- [Output Files](META_EVALUATOR.md#usage)
- [Per-CWE Analysis](META_EVALUATOR.md#performance-analysis)

## Version Information

- **Current Version**: 0.2.0
- **Last Updated**: 2026-06-16
- **Breaking Changes**: Yes (v0.1.0 → v0.2.0 removed multi-provider support)
- **Migration Required**: Yes (see [MIGRATION_SUMMARY.md](MIGRATION_SUMMARY.md))

## Getting Help

1. **Connection issues**: Run `test_corporate_endpoint.py`
2. **Setup questions**: See [SETUP.md](SETUP.md)
3. **Usage questions**: See [META_EVALUATOR.md](META_EVALUATOR.md)
4. **Corporate endpoint**: Contact Red Hat models.corp team
5. **Bugs**: File issue in this repository

## Contributing

See development section in [SETUP.md](SETUP.md#development-setup) for:
- Installing dev dependencies
- Running tests
- Code formatting

## License

See project LICENSE file (if applicable).
