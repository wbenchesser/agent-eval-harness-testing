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
    > Agent = Model (The Brain) + Harness (The "Body" or Infrastructure)
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

## What does it do?
1. Load Test Cases
    * It ingests a dataset of examples of tasks (e.g., "process this customer refund") paired with the expected final outcome or sequence of actions.
2. Invoke the Agent
    * For each test case, the harness triggers the agent in a controlled environment (often a sandbox).  
3. Capture Traces
    * It records every step the agent takes, including tool calls, parameters passed, intermediate observations, and the final response.  
4. Score the Results
    * It runs a suite of metrics against the output. This can include:  
        * Programmatic Graders: validation, database state verification, or code execution tests.  
        * LLM-as-a-Judge: Using a stronger, separate LLM to evaluate the quality, tone, or faithfulness of the agent's reasoning.  
        * Step-level Metrics Checking if the agent chose the correct tool at step 3, even if it eventually failed at step 5.  
5. Report & Gate
    * It aggregates results into a report. In professional settings, this is often used as a deployment gate. If the agent's performance on these tests drops below a certain threshold (a regression), the build or deployment is automatically blocked.

> In the context of the OWASP benchmark, the evaluation harness **does not** look at, parse, or evaluate the OWASP code.

> What it could do is determine whether your agent is actually right or wrong by acting as an automated grader that compares your agent's conclusions against the OWASP "answer key".

## Agent Eval Harness Use Case
* Let's say there was a new Red Hat built an AI agent designed to handle customer billing issues. 
    * The Goal: Help users with billing and issue refunds.
    * The Tools: The agent can call get_user_payment_history() and execute_stripe_refund(amount, charge_id).
    * The Guardrail Rule: Company policy states that any refund over $100 requires human manager approval.
* An engineer just updated the agent's system prompt to make its tone friendlier, and upgraded the underlying model to a newer, cheaper LLM to save the company money. **Before pushing this to production, Red Hat needs to prove you didn't just give an AI the power to accidentally drain the company's bank account.**
* This is where we spin up the agent-eval-harness locally. We pass it a dataset of distinct test cases showing when you might reward a refund and when you should not.
* When we run `agent-eval run`:
    * It spins up a sandbox. It mocks your database and  API so real money isn't actually moving.
    * It feeds each of the cases to the agent. 
    * Let's say the new model refunds a $500 dollar transaction even though it shouldn't.
* The Harness intercepts the trace, catching that the agent called the refund tool. It sees that this is against the policy and marks the case as failed.
* After going through all the cases, the harness generates a report. If enough cases failed, the depolyment can be automatically blocked. 

## Testing

### Built-Ins
* An automated test suite for codebase verification is defined in the Makefile and pyproject.toml configurations.
    * *Note: Because this places real model calls, you must export a valid API key into your terminal session first.*
    * However, these software tests only verify code correctness. They do not test the quality of the evaluation.

### Considerations
* Cost-Management
    * The full OWASP Benchmark contains over 2,700 individual test cases. Running a multi-sampled LLM judge loop over the entire dataset across multiple iterations would result in massive cloud API token expenditures. It makes more sense to leverage the harness's filtering flag (/eval-run --cases) to run evaluations over targeted, representative subsets. 
* Code-Instruction Isolation
    * Some OWASP test cases contain text strings inside code comments describing the vulnerability. Ensure your underlying judge prompt instructs the evaluating model to ignore code comments and focus exclusively on the executable logical flows to avoid cheating or artificial accuracy boosts.