"""Pydantic request contracts for ProducerGPT endpoints."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProductionRequest(BaseModel):
    """Describe a movie concept and optional constraints for an agent workflow run."""

    idea: str = Field(
        min_length=10,
        max_length=4_000,
        description="The single movie idea to develop into a production package.",
    )
    title: str | None = Field(default=None, max_length=200)
    genre: str | None = Field(default=None, max_length=100)
    language: str = Field(default="English", min_length=2, max_length=100)
    target_market: str | None = Field(default=None, max_length=300)
    budget_range: str | None = Field(default=None, max_length=200)
    tone: str | None = Field(default=None, max_length=200)
    creative_constraints: list[str] = Field(default_factory=list, max_length=20)
    context: dict[str, Any] = Field(
        default_factory=dict,
        description="Optional context for calling a single specialist endpoint directly.",
    )

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    @field_validator("idea")
    @classmethod
    def validate_idea(cls, value: str) -> str:
        """Reject ideas that contain only whitespace after normalization."""

        if not value:
            raise ValueError("idea must contain meaningful text")
        return value