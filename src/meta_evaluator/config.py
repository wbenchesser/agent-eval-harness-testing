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
    """Red Hat Corporate Vertex AI model configuration."""

    model: str
    max_tokens: int = 1024
    thinking: Literal["adaptive", "disabled"] = "disabled"
    temperature: float | None = None
    max_retries: int = 3
    requests_per_minute: int = 50
    # Corporate Vertex AI endpoint configuration
    vertex_corp_api_env: str = "MODEL_API"
    vertex_corp_key_env: str = "USER_KEY"

    def get_vertex_corp_api(self) -> str:
        """Retrieve corporate Vertex AI endpoint from environment variable."""
        api = os.environ.get(self.vertex_corp_api_env)
        if not api:
            raise ValueError(
                f"Environment variable {self.vertex_corp_api_env} not set. "
                f"Required for Red Hat corporate endpoint. "
                f"Set it with: export {self.vertex_corp_api_env}='https://...'"
            )
        return api

    def get_vertex_corp_key(self) -> str:
        """Retrieve corporate Vertex AI user key from environment variable."""
        key = os.environ.get(self.vertex_corp_key_env)
        if not key:
            raise ValueError(
                f"Environment variable {self.vertex_corp_key_env} not set. "
                f"Required for Red Hat corporate endpoint. "
                f"Set it with: export {self.vertex_corp_key_env}='your-credential'"
            )
        return key


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
