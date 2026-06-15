"""LLM client abstraction with async execution, rate limiting, and cost tracking."""

import asyncio
import time
from pathlib import Path

from anthropic import AsyncAnthropic
from openai import AsyncOpenAI

from meta_evaluator.config import ExecutionConfig, JudgeConfig
from meta_evaluator.dataset.loader import TestCase

from .prompts import SYSTEM_PROMPT, build_user_prompt
from .verdict import JudgeResult, Verdict

# Cost per 1M tokens (as of 2026-06)
COST_TABLE = {
    "claude-opus-4-8": {"input": 5.00, "output": 25.00},
    "claude-sonnet-4-6": {"input": 3.00, "output": 15.00},
    "claude-haiku-4-5": {"input": 1.00, "output": 5.00},
    "gpt-4o": {"input": 2.50, "output": 10.00},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
}


class RateLimiter:
    """Token bucket rate limiter for API calls."""

    def __init__(self, requests_per_minute: int):
        self.rate = requests_per_minute / 60.0  # tokens per second
        self.tokens = float(requests_per_minute)
        self.max_tokens = float(requests_per_minute)
        self.last_update = time.monotonic()
        self.lock = asyncio.Lock()

    async def acquire(self):
        """Acquire a token, waiting if necessary."""
        async with self.lock:
            now = time.monotonic()
            elapsed = now - self.last_update
            self.tokens = min(self.max_tokens, self.tokens + elapsed * self.rate)
            self.last_update = now

            if self.tokens < 1.0:
                wait_time = (1.0 - self.tokens) / self.rate
                await asyncio.sleep(wait_time)
                self.tokens = 0.0
            else:
                self.tokens -= 1.0


class SecurityJudge:
    """LLM-based security vulnerability judge."""

    def __init__(self, config: JudgeConfig):
        self.config = config
        self.rate_limiter = RateLimiter(config.requests_per_minute)

        if config.provider == "anthropic":
            self.client = AsyncAnthropic(
                api_key=config.get_api_key(),
                max_retries=config.max_retries,
            )
        elif config.provider == "openai":
            self.client = AsyncOpenAI(
                api_key=config.get_api_key(),
                max_retries=config.max_retries,
            )

    async def evaluate_case(self, case: TestCase) -> JudgeResult:
        """Evaluate a single test case. Core method."""
        await self.rate_limiter.acquire()

        user_prompt = build_user_prompt(case.source_code, case.test_name)
        start = time.monotonic()

        try:
            if self.config.provider == "anthropic":
                response = await self.client.messages.parse(
                    model=self.config.model,
                    max_tokens=self.config.max_tokens,
                    thinking={"type": self.config.thinking},
                    system=SYSTEM_PROMPT,
                    messages=[{"role": "user", "content": user_prompt}],
                    output_schema=Verdict,
                    temperature=self.config.temperature,
                )
                verdict = response.parsed
                input_tokens = response.usage.input_tokens
                output_tokens = response.usage.output_tokens

            elif self.config.provider == "openai":
                response = await self.client.beta.chat.completions.parse(
                    model=self.config.model,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt},
                    ],
                    response_format=Verdict,
                    max_tokens=self.config.max_tokens,
                    temperature=self.config.temperature,
                )
                verdict = response.choices[0].message.parsed
                input_tokens = response.usage.prompt_tokens
                output_tokens = response.usage.completion_tokens

            elapsed = time.monotonic() - start
            cost = self._calculate_cost(input_tokens, output_tokens)

            return JudgeResult(
                test_name=case.test_name,
                ground_truth_vulnerable=case.is_vulnerable,
                ground_truth_cwe=case.cwe,
                ground_truth_category=case.category,
                verdict=verdict,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost_usd=cost,
                latency_seconds=elapsed,
                model=self.config.model,
            )

        except Exception as e:
            elapsed = time.monotonic() - start
            return JudgeResult(
                test_name=case.test_name,
                ground_truth_vulnerable=case.is_vulnerable,
                ground_truth_cwe=case.cwe,
                ground_truth_category=case.category,
                verdict=Verdict(
                    is_vulnerable=False, cwe=None, confidence=0.0, reasoning=f"ERROR: {e}"
                ),
                input_tokens=0,
                output_tokens=0,
                cost_usd=0.0,
                latency_seconds=elapsed,
                model=self.config.model,
                error=str(e),
            )

    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost in USD based on model pricing."""
        rates = COST_TABLE.get(self.config.model, {"input": 0, "output": 0})
        return (input_tokens * rates["input"] + output_tokens * rates["output"]) / 1_000_000


async def run_evaluation(
    cases: list[TestCase],
    judge: SecurityJudge,
    config: ExecutionConfig,
) -> list[JudgeResult]:
    """Run judge over all cases with concurrency control and resumability."""
    output_dir = config.output_dir / "verdicts"
    output_dir.mkdir(parents=True, exist_ok=True)
    sem = asyncio.Semaphore(config.concurrency)

    async def process_one(case: TestCase) -> JudgeResult:
        verdict_file = output_dir / f"{case.test_name}.json"

        # Resumability: skip if verdict already exists
        if config.resume and verdict_file.exists():
            return JudgeResult.model_validate_json(verdict_file.read_text())

        async with sem:
            result = await judge.evaluate_case(case)

            # Persist verdict immediately for resumability
            verdict_file.write_text(result.model_dump_json(indent=2))
            return result

    print(f"\nEvaluating {len(cases)} test cases...")
    print(f"Concurrency: {config.concurrency}, Resume: {config.resume}")

    tasks = [process_one(case) for case in cases]
    results = []

    # Show progress
    for i, coro in enumerate(asyncio.as_completed(tasks), 1):
        result = await coro
        results.append(result)
        if i % 10 == 0 or i == len(tasks):
            print(f"  Completed {i}/{len(tasks)} cases...")

    return results
