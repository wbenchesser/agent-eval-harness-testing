"""Structured output schemas for security judge verdicts and results."""

from pydantic import BaseModel, Field


class Verdict(BaseModel):
    """Structured verdict from the security judge LLM."""

    is_vulnerable: bool = Field(description="Whether the code contains a security vulnerability")
    cwe: int | None = Field(default=None, description="CWE number if vulnerable, null if not")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score 0-1")
    reasoning: str = Field(description="Brief explanation of the determination")


class JudgeResult(BaseModel):
    """Full result including metadata for a single test case evaluation."""

    test_name: str
    ground_truth_vulnerable: bool
    ground_truth_cwe: int
    ground_truth_category: str
    verdict: Verdict
    input_tokens: int
    output_tokens: int
    cost_usd: float
    latency_seconds: float
    model: str
    error: str | None = None
