"""FastAPI routes for ProducerGPT's autonomous studio workflows."""

from __future__ import annotations

import logging
from functools import lru_cache
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status

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
from backend.core.config import Settings, get_settings
from backend.models.request import ProductionRequest
from backend.models.response import AgentRunResponse, ProductionPackageResponse
from backend.orchestrator.producer import ProducerOrchestrator, build_producer_orchestrator
from backend.services.openai_service import (
    OpenAIConfigurationError,
    OpenAIService,
    OpenAIServiceError,
)


logger = logging.getLogger(__name__)
router = APIRouter(tags=["ProducerGPT"])


@lru_cache
def get_openai_service() -> OpenAIService:
    """Create one reusable OpenAI service for the application process."""

    return OpenAIService(get_settings())


def get_producer_orchestrator(
    openai_service: Annotated[OpenAIService, Depends(get_openai_service)],
) -> ProducerOrchestrator:
    """Compose a request-scoped orchestrator around the shared SDK service."""

    return build_producer_orchestrator(openai_service)


OpenAIServiceDependency = Annotated[OpenAIService, Depends(get_openai_service)]
ProducerDependency = Annotated[ProducerOrchestrator, Depends(get_producer_orchestrator)]
SettingsDependency = Annotated[Settings, Depends(get_settings)]


@router.get("/", summary="Service overview")
async def root(settings: SettingsDependency) -> dict[str, str]:
    """Return lightweight service metadata; Swagger UI provides the minimal frontend."""

    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "tagline": "An Autonomous Hollywood Studio powered by AI Agents.",
        "docs": "/docs",
    }


@router.get("/health", summary="Health check")
async def health(settings: SettingsDependency, service: OpenAIServiceDependency) -> dict[str, str]:
    """Report process health without exposing credentials or provider internals."""

    provider_mode = "mock" if service.is_mock_mode else "live" if settings.has_openai_credentials else "unconfigured"
    return {
        "status": "ok",
        "environment": settings.environment,
        "provider_mode": provider_mode,
    }


@router.post("/generate", response_model=ProductionPackageResponse, summary="Generate a production package")
async def generate(
    request: ProductionRequest,
    producer: ProducerDependency,
) -> ProductionPackageResponse:
    """Run the complete autonomous multi-agent studio workflow."""

    return await producer.generate(request)


@router.post("/research", response_model=AgentRunResponse, summary="Run the research agent")
async def research(request: ProductionRequest, service: OpenAIServiceDependency) -> AgentRunResponse:
    """Run only the cultural and market research specialist."""

    return await _run_agent(ResearchAgent(service), request, service)


@router.post("/ceo", response_model=AgentRunResponse, summary="Run the entertainment CEO agent")
async def ceo(request: ProductionRequest, service: OpenAIServiceDependency) -> AgentRunResponse:
    """Run only the commercial greenlight specialist."""

    return await _run_agent(EntertainmentCEOAgent(service), request, service)


@router.post("/planner", response_model=AgentRunResponse, summary="Run the production planner")
async def planner(request: ProductionRequest, service: OpenAIServiceDependency) -> AgentRunResponse:
    """Run only the production planning specialist."""

    return await _run_agent(ProductionPlannerAgent(service), request, service)


@router.post("/script", response_model=AgentRunResponse, summary="Run the script agent")
async def script(request: ProductionRequest, service: OpenAIServiceDependency) -> AgentRunResponse:
    """Run only the screenplay-development specialist."""

    return await _run_agent(ScriptAgent(service), request, service)


@router.post("/storyboard", response_model=AgentRunResponse, summary="Run the storyboard agent")
async def storyboard(request: ProductionRequest, service: OpenAIServiceDependency) -> AgentRunResponse:
    """Run only the visual-storyboard specialist."""

    return await _run_agent(StoryboardAgent(service), request, service)


@router.post("/dialogue", response_model=AgentRunResponse, summary="Run the dialogue agent")
async def dialogue(request: ProductionRequest, service: OpenAIServiceDependency) -> AgentRunResponse:
    """Run only the dialogue and localization specialist."""

    return await _run_agent(DialogueAgent(service), request, service)


@router.post("/music", response_model=AgentRunResponse, summary="Run the music agent")
async def music(request: ProductionRequest, service: OpenAIServiceDependency) -> AgentRunResponse:
    """Run only the score-development specialist."""

    return await _run_agent(MusicAgent(service), request, service)


@router.post("/poster", response_model=AgentRunResponse, summary="Run the poster prompt agent")
async def poster(request: ProductionRequest, service: OpenAIServiceDependency) -> AgentRunResponse:
    """Run only the campaign key-art specialist."""

    return await _run_agent(PosterPromptAgent(service), request, service)


@router.post("/copilot", response_model=AgentRunResponse, summary="Run the creator copilot")
async def copilot(request: ProductionRequest, service: OpenAIServiceDependency) -> AgentRunResponse:
    """Run only the post-production recommendation specialist."""

    return await _run_agent(CreatorCopilotAgent(service), request, service)


async def _run_agent(
    agent: BaseAgent,
    request: ProductionRequest,
    service: OpenAIService,
) -> AgentRunResponse:
    """Run a direct specialist endpoint with consistent provider error handling."""

    try:
        output = await agent.run(request, request.context)
    except OpenAIConfigurationError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(error),
        ) from error
    except OpenAIServiceError as error:
        logger.warning("Specialist endpoint failed: %s", agent.name, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="The AI provider could not complete this agent task.",
        ) from error
    except Exception as error:
        logger.exception("Unexpected specialist failure: %s", agent.name)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="The agent could not complete its task.",
        ) from error

    return AgentRunResponse(
        agent=agent.name,
        output=output,
        mode="mock" if service.is_mock_mode else "live",
        model=service.model,
    )