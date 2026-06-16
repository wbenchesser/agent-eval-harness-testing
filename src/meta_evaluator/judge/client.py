"""LLM client abstraction with async execution, rate limiting, and cost tracking."""

import asyncio
import json
import time
from pathlib import Path

import httpx

from meta_evaluator.config import ExecutionConfig, JudgeConfig
from meta_evaluator.dataset.loader import TestCase

from .prompts import SYSTEM_PROMPT, build_user_prompt
from .verdict import JudgeResult, Verdict

# Cost per 1M tokens (as of 2026-06) - Red Hat Corporate Vertex AI
COST_TABLE = {
    "claude-opus-4-8@20250514": {"input": 5.00, "output": 25.00},
    "claude-sonnet-4-6@20250514": {"input": 3.00, "output": 15.00},
    "claude-haiku-4-5@20251001": {"input": 1.00, "output": 5.00},
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

        # Red Hat Corporate Vertex AI endpoint
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(60.0, connect=10.0),
            limits=httpx.Limits(max_keepalive_connections=20, max_connections=100),
        )
        self.corp_api_base = config.get_vertex_corp_api()
        self.corp_user_key = config.get_vertex_corp_key()

    async def evaluate_case(self, case: TestCase) -> JudgeResult:
        """Evaluate a single test case. Core method."""
        await self.rate_limiter.acquire()

        user_prompt = build_user_prompt(case.source_code, case.test_name)
        start = time.monotonic()

        try:
            # Red Hat Corporate Vertex AI endpoint using Anthropic-compatible Messages API
            # Determine model tier for URL path (haiku, sonnet, opus)
            model_tier = "haiku"
            if "sonnet" in self.config.model.lower():
                model_tier = "sonnet"
            elif "opus" in self.config.model.lower():
                model_tier = "opus"

            url = f"{self.corp_api_base}/{model_tier}/models/{self.config.model}:streamRawPredict"

            # Add JSON schema instruction to system prompt for structured output
            json_schema = Verdict.model_json_schema()
            system_prompt_with_schema = (
                f"{SYSTEM_PROMPT}\n\n"
                f"You must respond with ONLY a valid JSON object matching this exact schema:\n"
                f"{json.dumps(json_schema, indent=2)}\n\n"
                f"Do not include any text before or after the JSON object."
            )

            # Build request payload (Anthropic Messages API format)
            payload = {
                "anthropic_version": "vertex-2023-10-16",
                "max_tokens": self.config.max_tokens,
                "temperature": self.config.temperature if self.config.temperature is not None else 0.0,
                "system": system_prompt_with_schema,
                "messages": [
                    {
                        "role": "user",
                        "content": [{"type": "text", "text": user_prompt}]
                    }
                ]
            }

            # Add thinking parameter if configured
            if self.config.thinking:
                payload["thinking"] = {"type": self.config.thinking}

            headers = {
                "Authorization": f"Bearer {self.corp_user_key}",
                "Content-Type": "application/json",
            }

            # Make API call
            response = await self.client.post(url, json=payload, headers=headers)
            response.raise_for_status()

            # Parse response
            response_data = response.json()

            # Extract content from Claude response
            # The API returns standard Anthropic Messages format
            content_blocks = response_data.get("content", [])
            text_content = ""
            for block in content_blocks:
                if block.get("type") == "text":
                    text_content += block.get("text", "")

            # Parse structured output from text
            # Strip markdown code fences if present
            text_content = text_content.strip()
            if text_content.startswith("```json"):
                text_content = text_content[7:]
            if text_content.startswith("```"):
                text_content = text_content[3:]
            if text_content.endswith("```"):
                text_content = text_content[:-3]
            text_content = text_content.strip()

            verdict = Verdict.model_validate_json(text_content)

            # Extract token usage
            usage = response_data.get("usage", {})
            input_tokens = usage.get("input_tokens", 0)
            output_tokens = usage.get("output_tokens", 0)

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
