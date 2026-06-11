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


## Concepts

* In an evaluation setup, the common weakness databases (i.e. OWASP Benchmark) is the vulnerable code, and the agent-eval-harness is the testing arena. However, the harness itself doesn't actively "test exploits."
    * Instead, the AI Agent you are developing is the subject under evaluation.

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