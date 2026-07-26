"""Producer Orchestrator for the autonomous creative studio workflow."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from time import perf_counter
from typing import Any, Mapping

from backend.agents.base_agent import BaseAgent
from backend.agents.ceo_agent import EntertainmentCEOAgent
from backend.agents.creator_copilot import CreatorCopilotAgent
from backend.agents.dialogue_agent import DialogueAgent
from backend.agents.music_agent import MusicAgent
from backend.agents.planner_agent import ProductionPlannerAgent
from backend.agents.poster_agent import PosterPromptAgent
from backend.agents.research_agent import ResearchAgent
from backend.agents.script_agent import ScriptAgent
from backend.agents.storyboard_agent import StoryboardAgent
from backend.agents.studio_agent import PersonalHollywoodStudioAgent
from backend.models.request import ProductionRequest
from backend.models.response import (
    AgentError,
    AgentTimelineEntry,
    CreativeAssets,
    ExecutionMetrics,
    ProductionPackageResponse,
    ProductionStatus,
    WorkflowSummary,
)
from backend.services.openai_service import OpenAIService


logger = logging.getLogger(__name__)

AGENT_LABELS = {
    "research": "Research Agent",
    "ceo": "CEO Agent",
    "planner": "Planner Agent",
    "script": "Script Agent",
    "storyboard": "Storyboard Agent",
    "dialogue": "Dialogue Agent",
    "music": "Music Agent",
    "poster": "Poster Agent",
    "studio": "Studio Agent",
    "copilot": "Creator Copilot",
}
POST_GREENLIGHT_AGENTS = (
    "planner",
    "script",
    "storyboard",
    "dialogue",
    "music",
    "poster",
    "studio",
    "copilot",
)


@dataclass(slots=True)
class AgentExecution:
    """Capture one agent output or a sanitized recoverable failure."""

    agent: str
    output: dict[str, Any]
    start_time: datetime
    end_time: datetime
    duration_ms: int
    status: str
    error: AgentError | None = None


class ProducerOrchestrator:
    """Coordinate the complete autonomous workflow for a single movie idea."""

    def __init__(
        self,
        *,
        research_agent: ResearchAgent,
        ceo_agent: EntertainmentCEOAgent,
        planner_agent: ProductionPlannerAgent,
        script_agent: ScriptAgent,
        storyboard_agent: StoryboardAgent,
        dialogue_agent: DialogueAgent,
        music_agent: MusicAgent,
        poster_agent: PosterPromptAgent,
        studio_agent: PersonalHollywoodStudioAgent,
        creator_copilot: CreatorCopilotAgent,
    ) -> None:
        self._research_agent = research_agent
        self._ceo_agent = ceo_agent
        self._planner_agent = planner_agent
        self._script_agent = script_agent
        self._storyboard_agent = storyboard_agent
        self._dialogue_agent = dialogue_agent
        self._music_agent = music_agent
        self._poster_agent = poster_agent
        self._studio_agent = studio_agent
        self._creator_copilot = creator_copilot

    async def generate(self, request: ProductionRequest) -> ProductionPackageResponse:
        """Produce a structured studio package from one validated movie idea."""

        workflow_started = perf_counter()
        errors: list[AgentError] = []
        execution_timeline: list[AgentTimelineEntry] = []
        workflow_logs = ["Producer Orchestrator started"]
        initial_context = {"request_context": request.context}

        research_execution = await self._execute(
            "research",
            self._research_agent,
            request,
            initial_context,
            execution_timeline,
            workflow_logs,
        )
        self._append_error(errors, research_execution)

        ceo_execution = await self._execute(
            "ceo",
            self._ceo_agent,
            request,
            {"research": research_execution.output, **initial_context},
            execution_timeline,
            workflow_logs,
        )
        self._append_error(errors, ceo_execution)
        greenlight = self._text(ceo_execution.output.get("greenlight"), "UNKNOWN").upper()

        if not ceo_execution.output:
            workflow_logs.append("Workflow stopped before greenlight")
            self._record_skipped_agents(
                POST_GREENLIGHT_AGENTS, execution_timeline, workflow_logs
            )
            return self._build_package(
                status=ProductionStatus.PARTIAL,
                greenlight=greenlight,
                research=research_execution.output,
                ceo=ceo_execution.output,
                errors=errors,
                execution_timeline=execution_timeline,
                workflow_logs=workflow_logs,
                metrics=self._build_metrics(
                    workflow_started,
                    research_execution=research_execution,
                    ceo_execution=ceo_execution,
                ),
            )

        if greenlight == "NO":
            logger.info("Production package declined by CEO agent")
            workflow_logs.append("Project not greenlighted")
            self._record_skipped_agents(
                POST_GREENLIGHT_AGENTS, execution_timeline, workflow_logs
            )
            return self._build_package(
                status=ProductionStatus.DECLINED,
                greenlight=greenlight,
                research=research_execution.output,
                ceo=ceo_execution.output,
                errors=errors,
                execution_timeline=execution_timeline,
                workflow_logs=workflow_logs,
                metrics=self._build_metrics(
                    workflow_started,
                    research_execution=research_execution,
                    ceo_execution=ceo_execution,
                ),
            )

        if greenlight != "YES":
            errors.append(
                AgentError(
                    agent="ceo",
                    message="CEO agent returned an invalid greenlight decision.",
                )
            )
            workflow_logs.append("Workflow stopped due to an invalid greenlight decision")
            self._record_skipped_agents(
                POST_GREENLIGHT_AGENTS, execution_timeline, workflow_logs
            )
            return self._build_package(
                status=ProductionStatus.PARTIAL,
                greenlight=greenlight,
                research=research_execution.output,
                ceo=ceo_execution.output,
                errors=errors,
                execution_timeline=execution_timeline,
                workflow_logs=workflow_logs,
                metrics=self._build_metrics(
                    workflow_started,
                    research_execution=research_execution,
                    ceo_execution=ceo_execution,
                ),
            )

        workflow_logs.append("Project Greenlighted")
        planning_context = {
            "research": research_execution.output,
            "ceo": ceo_execution.output,
            **initial_context,
        }
        planner_execution = await self._execute(
            "planner",
            self._planner_agent,
            request,
            planning_context,
            execution_timeline,
            workflow_logs,
        )
        self._append_error(errors, planner_execution)
        task_count = len(planner_execution.output.get("tasks", []))
        workflow_logs.append(f"Planner generated {task_count} tasks")

        creative_context = {
            **planning_context,
            "plan": planner_execution.output,
        }
        logger.info("Starting concurrent creative agent fan-out")
        workflow_logs.append("Launching creative agents")
        creative_pool_started = perf_counter()
        creative_executions = await asyncio.gather(
            self._execute(
                "script",
                self._script_agent,
                request,
                creative_context,
                execution_timeline,
                workflow_logs,
            ),
            self._execute(
                "storyboard",
                self._storyboard_agent,
                request,
                creative_context,
                execution_timeline,
                workflow_logs,
            ),
            self._execute(
                "dialogue",
                self._dialogue_agent,
                request,
                creative_context,
                execution_timeline,
                workflow_logs,
            ),
            self._execute(
                "music",
                self._music_agent,
                request,
                creative_context,
                execution_timeline,
                workflow_logs,
            ),
            self._execute(
                "poster",
                self._poster_agent,
                request,
                creative_context,
                execution_timeline,
                workflow_logs,
            ),
        )
        creative_pool_duration_ms = self._elapsed_ms(creative_pool_started)
        creative_outputs = {execution.agent: execution.output for execution in creative_executions}
        for execution in creative_executions:
            self._append_error(errors, execution)

        studio_context = {
            **creative_context,
            **creative_outputs,
        }
        studio_execution = await self._execute(
            "studio",
            self._studio_agent,
            request,
            studio_context,
            execution_timeline,
            workflow_logs,
        )
        self._append_error(errors, studio_execution)
        if studio_execution.status == "completed":
            workflow_logs.append("Studio assembled production package")

        copilot_execution = await self._execute(
            "copilot",
            self._creator_copilot,
            request,
            {**studio_context, "studio": studio_execution.output},
            execution_timeline,
            workflow_logs,
        )
        self._append_error(errors, copilot_execution)

        status = ProductionStatus.PARTIAL if errors else ProductionStatus.COMPLETED
        workflow_logs.append("Producer Orchestrator completed")
        return self._build_package(
            status=status,
            greenlight=greenlight,
            research=research_execution.output,
            ceo=ceo_execution.output,
            plan=planner_execution.output,
            creative_outputs=creative_outputs,
            studio=studio_execution.output,
            copilot=copilot_execution.output,
            errors=errors,
            execution_timeline=execution_timeline,
            workflow_logs=workflow_logs,
            metrics=self._build_metrics(
                workflow_started,
                research_execution=research_execution,
                ceo_execution=ceo_execution,
                planner_execution=planner_execution,
                creative_pool_duration_ms=creative_pool_duration_ms,
            ),
            creative_agents_executed=len(creative_executions),
        )

    async def _execute(
        self,
        agent_name: str,
        agent: BaseAgent,
        request: ProductionRequest,
        context: Mapping[str, Any],
        execution_timeline: list[AgentTimelineEntry],
        workflow_logs: list[str],
    ) -> AgentExecution:
        """Run one agent while allowing the overall package to degrade gracefully."""

        start_time = datetime.now(timezone.utc)
        started_at = perf_counter()
        workflow_logs.append(self._start_log_message(agent_name))
        try:
            execution = AgentExecution(
                agent=agent_name,
                output=await agent.run(request, context),
                start_time=start_time,
                end_time=datetime.now(timezone.utc),
                duration_ms=self._elapsed_ms(started_at),
                status="completed",
            )
            workflow_logs.append(f"{self._agent_label(agent_name)} completed")
        except Exception:
            logger.exception("Agent failed: %s", agent_name)
            execution = AgentExecution(
                agent=agent_name,
                output={},
                start_time=start_time,
                end_time=datetime.now(timezone.utc),
                duration_ms=self._elapsed_ms(started_at),
                status="failed",
                error=AgentError(
                    agent=agent_name,
                    message="Agent could not complete its production task.",
                ),
            )
            workflow_logs.append(f"{self._agent_label(agent_name)} failed")

        execution_timeline.append(
            AgentTimelineEntry(
                agent=self._agent_label(agent_name),
                status=execution.status,
                start_time=execution.start_time,
                end_time=execution.end_time,
                duration_ms=execution.duration_ms,
            )
        )
        return execution

    @staticmethod
    def _append_error(errors: list[AgentError], execution: AgentExecution) -> None:
        if execution.error is not None:
            errors.append(execution.error)

    def _build_package(
        self,
        *,
        status: ProductionStatus,
        greenlight: str,
        research: dict[str, Any],
        ceo: dict[str, Any],
        plan: dict[str, Any] | None = None,
        creative_outputs: Mapping[str, dict[str, Any]] | None = None,
        studio: dict[str, Any] | None = None,
        copilot: dict[str, Any] | None = None,
        errors: list[AgentError],
        execution_timeline: list[AgentTimelineEntry],
        workflow_logs: list[str],
        metrics: ExecutionMetrics,
        creative_agents_executed: int = 0,
    ) -> ProductionPackageResponse:
        """Normalize agent artifacts into the public production-package contract."""

        creative = dict(creative_outputs or {})
        studio_output = studio or {}
        copilot_output = copilot or {}
        script = creative.get("script", {})
        poster = creative.get("poster", {})

        return ProductionPackageResponse(
            status=status,
            greenlight=greenlight,
            title=self._text(studio_output.get("title") or ceo.get("title"), "Untitled Feature"),
            logline=self._text(script.get("logline"), ""),
            genre=self._text(studio_output.get("genre") or ceo.get("genre"), "Unspecified"),
            budget=self._text(studio_output.get("budget") or ceo.get("budget"), "TBD"),
            audience=self._text(studio_output.get("audience") or ceo.get("audience"), "TBD"),
            research=research,
            ceo=ceo,
            plan=plan or {},
            planner=plan or {},
            script=script,
            storyboard=creative.get("storyboard", {}),
            dialogues=creative.get("dialogue", {}),
            music=creative.get("music", {}),
            poster_prompt=self._text(
                studio_output.get("poster_prompt") or poster.get("poster_prompt"), ""
            ),
            video_prompt=self._text(
                studio_output.get("video_prompt") or script.get("video_prompt"), ""
            ),
            editing_suggestions=self._string_list(copilot_output.get("editing_suggestions")),
            studio=studio_output,
            creator_copilot=copilot_output,
            creative_assets=CreativeAssets(
                script=script,
                storyboard=creative.get("storyboard", {}),
                dialogues=creative.get("dialogue", {}),
                music=creative.get("music", {}),
                poster_prompt=self._text(
                    studio_output.get("poster_prompt") or poster.get("poster_prompt"), ""
                ),
                video_prompt=self._text(
                    studio_output.get("video_prompt") or script.get("video_prompt"), ""
                ),
            ),
            workflow=WorkflowSummary(
                status=status.value.capitalize(),
                greenlight=greenlight == "YES",
                creative_agents_executed=creative_agents_executed,
            ),
            execution_timeline=execution_timeline,
            workflow_logs=workflow_logs,
            metrics=metrics,
            errors=errors,
        )

    def _record_skipped_agents(
        self,
        agent_names: tuple[str, ...],
        execution_timeline: list[AgentTimelineEntry],
        workflow_logs: list[str],
    ) -> None:
        """Add zero-duration timeline entries for agents gated by the CEO decision."""

        timestamp = datetime.now(timezone.utc)
        for agent_name in agent_names:
            agent_label = self._agent_label(agent_name)
            execution_timeline.append(
                AgentTimelineEntry(
                    agent=agent_label,
                    status="skipped",
                    start_time=timestamp,
                    end_time=timestamp,
                    duration_ms=0,
                )
            )
            workflow_logs.append(f"{agent_label} skipped")

    def _build_metrics(
        self,
        workflow_started: float,
        *,
        research_execution: AgentExecution | None = None,
        ceo_execution: AgentExecution | None = None,
        planner_execution: AgentExecution | None = None,
        creative_pool_duration_ms: int = 0,
    ) -> ExecutionMetrics:
        """Aggregate stage durations without exposing provider-specific details."""

        return ExecutionMetrics(
            total_execution_time=self._format_duration(self._elapsed_ms(workflow_started)),
            research_time=self._execution_duration(research_execution),
            ceo_time=self._execution_duration(ceo_execution),
            planner_time=self._execution_duration(planner_execution),
            creative_pool_time=self._format_duration(creative_pool_duration_ms),
        )

    @staticmethod
    def _elapsed_ms(started_at: float) -> int:
        return max(0, round((perf_counter() - started_at) * 1_000))

    @classmethod
    def _execution_duration(cls, execution: AgentExecution | None) -> str:
        return cls._format_duration(execution.duration_ms if execution else 0)

    @staticmethod
    def _format_duration(duration_ms: int) -> str:
        return f"{duration_ms} ms"

    @staticmethod
    def _agent_label(agent_name: str) -> str:
        return AGENT_LABELS.get(agent_name, agent_name.replace("_", " ").title())

    def _start_log_message(self, agent_name: str) -> str:
        if agent_name == "ceo":
            return "CEO Agent evaluating"
        return f"{self._agent_label(agent_name)} started"

    @staticmethod
    def _text(value: Any, default: str) -> str:
        return value.strip() if isinstance(value, str) and value.strip() else default

    @staticmethod
    def _string_list(value: Any) -> list[str]:
        if not isinstance(value, list):
            return []
        return [item.strip() for item in value if isinstance(item, str) and item.strip()]


def build_producer_orchestrator(openai_service: OpenAIService) -> ProducerOrchestrator:
    """Compose the default workflow with one shared OpenAI service instance."""

    return ProducerOrchestrator(
        research_agent=ResearchAgent(openai_service),
        ceo_agent=EntertainmentCEOAgent(openai_service),
        planner_agent=ProductionPlannerAgent(openai_service),
        script_agent=ScriptAgent(openai_service),
        storyboard_agent=StoryboardAgent(openai_service),
        dialogue_agent=DialogueAgent(openai_service),
        music_agent=MusicAgent(openai_service),
        poster_agent=PosterPromptAgent(openai_service),
        studio_agent=PersonalHollywoodStudioAgent(openai_service),
        creator_copilot=CreatorCopilotAgent(openai_service),
    )