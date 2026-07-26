"""Pydantic response contracts for ProducerGPT workflows."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class ProductionStatus(StrEnum):
    """Represent the terminal state of an orchestrated production run."""

    COMPLETED = "completed"
    PARTIAL = "partial"
    DECLINED = "declined"


class AgentError(BaseModel):
    """Describe a recoverable agent failure in a production package."""

    agent: str
    message: str


class AgentRunResponse(BaseModel):
    """Envelope returned by an endpoint that runs one specialist agent."""

    agent: str
    output: dict[str, Any]
    mode: str
    model: str
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AgentTimelineEntry(BaseModel):
    """Capture timing and terminal status for one workflow agent."""

    agent: str
    status: str
    start_time: datetime
    end_time: datetime
    duration_ms: int = Field(ge=0)


class WorkflowSummary(BaseModel):
    """Summarize the user-visible state of an orchestrated run."""

    status: str = "Completed"
    greenlight: bool = False
    creative_agents_executed: int = Field(default=0, ge=0)


class ExecutionMetrics(BaseModel):
    """Expose high-level stage timings in a demo-friendly representation."""

    total_execution_time: str = "0 ms"
    research_time: str = "0 ms"
    ceo_time: str = "0 ms"
    planner_time: str = "0 ms"
    creative_pool_time: str = "0 ms"


class CreativeAssets(BaseModel):
    """Group the parallel creative outputs for demo consumers."""

    script: dict[str, Any] = Field(default_factory=dict)
    storyboard: dict[str, Any] = Field(default_factory=dict)
    dialogues: dict[str, Any] = Field(default_factory=dict)
    music: dict[str, Any] = Field(default_factory=dict)
    poster_prompt: str = ""
    video_prompt: str = ""


class ProductionPackageResponse(BaseModel):
    """Complete structured output assembled by the Producer Orchestrator."""

    project_id: UUID = Field(default_factory=uuid4)
    status: ProductionStatus
    greenlight: str
    title: str
    logline: str = ""
    genre: str
    budget: str
    audience: str
    research: dict[str, Any] = Field(default_factory=dict)
    ceo: dict[str, Any] = Field(default_factory=dict)
    plan: dict[str, Any] = Field(default_factory=dict)
    planner: dict[str, Any] = Field(default_factory=dict)
    script: dict[str, Any] = Field(default_factory=dict)
    storyboard: dict[str, Any] = Field(default_factory=dict)
    dialogues: dict[str, Any] = Field(default_factory=dict)
    music: dict[str, Any] = Field(default_factory=dict)
    poster_prompt: str = ""
    video_prompt: str = ""
    editing_suggestions: list[str] = Field(default_factory=list)
    studio: dict[str, Any] = Field(default_factory=dict)
    creator_copilot: dict[str, Any] = Field(default_factory=dict)
    creative_assets: CreativeAssets = Field(default_factory=CreativeAssets)
    workflow: WorkflowSummary = Field(default_factory=WorkflowSummary)
    execution_timeline: list[AgentTimelineEntry] = Field(default_factory=list)
    workflow_logs: list[str] = Field(default_factory=list)
    metrics: ExecutionMetrics = Field(default_factory=ExecutionMetrics)
    errors: list[AgentError] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(extra="forbid")