"""Configuration loading and validation."""

import os
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, field_validator


class DatasetConfig(BaseModel):
    """Dataset source and sampling configuration."""

    csv_url: str
    source_base_url: str
    local_repo_path: Path | None = None
    sample_size: int | None = None
    random_seed: int = 42

    @field_validator("local_repo_path", mode="before")
    @classmethod
    def validate_path(cls, v):
        if v is None or v == "null":
            return None
        return Path(v)


class JudgeConfig(BaseModel):
    """LLM provider and model configuration."""

    provider: Literal["anthropic", "openai", "vertex"]
    model: str
    api_key_env: str
    max_tokens: int = 1024
    thinking: Literal["adaptive", "disabled"] = "adaptive"
    temperature: float | None = None
    max_retries: int = 3
    requests_per_minute: int = 50
    gcp_project_env: str = "GCP_PROJECT_ID"
    gcp_region_env: str = "GCP_REGION"
    gcp_location: str = "us-central1"

    def get_api_key(self) -> str:
        """Retrieve API key from environment variable."""
        key = os.environ.get(self.api_key_env)
        if not key:
            raise ValueError(
                f"Environment variable {self.api_key_env} not set. "
                f"Please set it with your API key."
            )
        return key

    def get_gcp_project(self) -> str:
        """Retrieve GCP project ID from environment variable."""
        project = os.environ.get(self.gcp_project_env)
        if not project:
            raise ValueError(
                f"Environment variable {self.gcp_project_env} not set. "
                f"Required for Vertex AI provider."
            )
        return project

    def get_gcp_region(self) -> str:
        """Retrieve GCP region from environment variable or use default."""
        return os.environ.get(self.gcp_region_env, self.gcp_location)


class ExecutionConfig(BaseModel):
    """Execution and output configuration."""

    concurrency: int = 10
    output_dir: Path = Path("./results")
    resume: bool = True

    @field_validator("output_dir", mode="before")
    @classmethod
    def validate_path(cls, v):
        return Path(v)


class ScoringConfig(BaseModel):
    """Scoring and filtering configuration."""

    confidence_threshold: float = 0.5


class AppConfig(BaseModel):
    """Root configuration model."""

    dataset: DatasetConfig
    judge: JudgeConfig
    execution: ExecutionConfig
    scoring: ScoringConfig


def load_config(path: Path = Path("config.yaml")) -> AppConfig:
    """Load and validate configuration from YAML file."""
    if not path.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {path}\n"
            "Please create config.yaml in the project root."
        )

    with open(path) as f:
        raw = yaml.safe_load(f)

    return AppConfig(**raw)
