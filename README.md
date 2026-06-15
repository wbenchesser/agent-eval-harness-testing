# agent-eval-harness-testing

Compliation of information for testing the [opendatahub-io evaluation framework for agents and skills](https://github.com/opendatahub-io/agent-eval-harness).

## Resources
* [Common Weakness Enumeration Databases](https://docs.google.com/document/d/1P0V4EeNT9FUoaxQQxEI7UT-eDBbwuwv6BSUWnioHq-o/edit?tab=t.0)
    * [The Juliet Test Suite](https://www.nist.gov/publications/juliet-11-cc-and-java-test-suite)
        * A collection of over 81,000 synthetic C/C++ and Java programs with known flaws. 
        * Covers 181 different Common Weakness Enumeration (CWE) entries.
            * Includes example code snippets exhibiting the weaknesses and similar unflawed variations for testing false positives.
        * In the public domain.
        * Note: *Link for downloading test suite errors out as of 6/11/26.*
    * [OWASP Benchmark Project](https://owasp.org/www-project-benchmark/)
        * Provides multiple fully runnable open source web application that contains thousands of exploitable test cases, each mapped to specific CWEs.
        * Open source.
        * Cloneable from [GitHub](https://github.com/OWASP-Benchmark).

## Foundations
* Agents
    * AI agents differ from standard LLMs because they operate in loops, break down complex tasks, and use external "tools" (like querying a database or executing code). Evaluating them requires tracking their entire trajectory (the steps they took), not just the final output.
* Evaluation Frameworks
    * A toolkit built to act as a standardized, automated "grading machine" for AI.
    * What they do:
        * Automatically downloads public benchmarks and formats them into a clean structure the AI can read.
        * It has built-in connectors to talk to any model to avoid rewriting API calls.
        * It handles few-shot prompting (giving the AI 3 or 4 examples of how to answer before asking the real question) uniformly.
        * It applies advanced scoring math. It doesn't just look for exact text matches; it uses regex, log-likelihood (how confident the model was), or even "LLM-as-a-Judge" to score the answer.
* Testing 
    * In traditional software engineering, we test by feeding a function a known input, and writing an assertion statement checking if the output matches an exact expected value. With AI Agents and LLMs, testing is much harder since their output is non-deterministic and open-ended.
* agent-eval-harness
    * Since running an evaluation framework locally can heavily lag your machine or require massive GPU power, agent-eval-harness acts like a manager. It takes a request from a user, spins up a temporary container in the cloud, drops an evaluation framework (like LightEval) into that container, lets it run the test, grabs the final report, and shuts the container down.
> *This project is a Continuous Integration (CI) and automated testing framework specifically built for AI agents and LLM skills. Instead of checking for exact string matches, it runs the AI agent in an isolated sandbox, collects what the agent produced, and uses a mix of deterministic code and LLM sub-agents ("LLM-as-a-judge") to evaluate and grade the quality, safety, and efficiency of the agent's work.*


## Concepts

* In an evaluation setup, the common weakness databases (i.e. OWASP Benchmark) is the vulnerable code, and the agent-eval-harness is the testing arena. However, the harness itself doesn't actively "test exploits."
    * Instead, the AI Agent is the subject under evaluation.

> *To be clear, the agent-eval-harness does not test code for vulnerabilities. It evaluates, benchmarks, and safety-tests AI agents and Large Language Models (LLMs).*

* The common weakness database provides the context.
* The AI Agent reads the code, attempts to analyze it, and outputs a response (e.g., "This file has a path traversal vulnerability").
* The agent-eval-harness manages this lifecycle. It feeds the code to your agent, captures the agent's behavior/answers, and automatically scores whether the agent correctly identified the exploit as unsafe.

## How it works
When running a test suite, the harness:
* Fetches the Dataset: It pulls a dataset of test cases.
* Executes the Agent/Model: It triggers the target agent inside a controlled environment (often using sandbox containers or mock interactions), tracking how the agent handles prompts, calls tools, and arrives at an answer.  
* Applies Metrics: It applies LLM-as-a-judge scoring or traditional deterministic scoring against the agent's full execution trace.  
* Aggregates & Tracks: The results are combined into a standardized score. The complete execution record (including the prompt trace, latency, hardware utilization, and scores) is exported to an observability server like MLflow or Prometheus.

## Testing
> *So... how do we test the tester?*

### Built-Ins
* An automated test suite for codebase verification is defined in the Makefile and pyproject.toml configurations.
    * *Note: Because this places real model calls, you must export a valid API key into your terminal session first.*
    * However, these software tests only verify code correctness. They do not test the quality of the evaluation.

### Custom Approach

**✅ IMPLEMENTED** — See [META_EVALUATOR.md](META_EVALUATOR.md) for full documentation.

* Testing the quality of an AI evaluation is a data science concept known as Meta-Evaluation.
* We have implemented a standalone Python tool that maps the OWASP test suite to evaluate LLM security judges using these components:
    1. **Dataset Scaffolding** (`meta_evaluator/dataset/`)
        * Loads all 2,740 OWASP Benchmark test cases with ground truth labels (vulnerable vs. clean, CWE mappings)
        * Supports stratified sampling to preserve CWE distribution and TP/TN ratio
        * Fetches Java source files from GitHub or local clone
    2. **The Security Judge Under Test** (`meta_evaluator/judge/`)
        * Configurable LLM (Anthropic Claude or OpenAI) that reads Java code and outputs structured verdicts
        * System prompt with **Code-Instruction Isolation** (ignores comments to prevent cheating)
        * Async execution with rate limiting, cost tracking, and resumability
    3. **The Meta-Judge** (`meta_evaluator/scoring/`)
        * Compares LLM verdicts against OWASP ground truth
        * Computes confusion matrix, TPR/FPR, Youden Index per CWE
        * Generates reports (console, JSON, CSV)

**Quick Start:**
```bash
pip install -e .
export ANTHROPIC_API_KEY="sk-ant-..."
meta-eval evaluate --sample-size 100
```

### Considerations
* Cost-Management
    * The full OWASP Benchmark contains over 2,700 individual test cases. Running a multi-sampled LLM judge loop over the entire dataset across multiple iterations would result in massive cloud API token expenditures. It makes more sense to leverage the harness's filtering flag (/eval-run --cases) to run evaluations over targeted, representative subsets. 
* Code-Instruction Isolation
    * Some OWASP test cases contain text strings inside code comments describing the vulnerability. Ensure your underlying judge prompt instructs the evaluating model to ignore code comments and focus exclusively on the executable logical flows to avoid cheating or artificial accuracy boosts.