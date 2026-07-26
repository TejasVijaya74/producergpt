"""Environment-backed configuration for ProducerGPT."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic import AliasChoices, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = PROJECT_ROOT / ".env"

# Load the environment once so non-settings integrations see the same values.
load_dotenv(ENV_FILE, override=False)


class Settings(BaseSettings):
    """Runtime settings loaded from process variables and the project `.env` file."""

    app_name: str = "ProducerGPT"
    app_version: str = "1.0.0"
    environment: str = "development"
    log_level: str = "INFO"

    openai_api_key: SecretStr | None = None
    openai_model: str = "gpt-4o-mini"
    openai_temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    openai_timeout_seconds: float = Field(default=60.0, gt=0.0)
    openai_max_retries: int = Field(default=2, ge=0, le=10)
    openai_mock_mode: bool = Field(
        default=False,
        validation_alias=AliasChoices("OPENAI_MOCK_MODE", "MOCK_MODE"),
    )

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def has_openai_credentials(self) -> bool:
        """Return whether an OpenAI API key is configured."""

        return self.openai_api_key is not None


@lru_cache
def get_settings() -> Settings:
    """Return the process-wide immutable settings instance."""

    return Settings()