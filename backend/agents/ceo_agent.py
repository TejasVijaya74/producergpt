"""Entertainment CEO agent for greenlight and commercial strategy decisions."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Mapping

from backend.agents.base_agent import BaseAgent

if TYPE_CHECKING:
    from backend.models.request import ProductionRequest


class EntertainmentCEOAgent(BaseAgent):
    """Evaluate creative ambition against market fit and production economics."""

    name = "entertainment_ceo"
    prompt_filename = "ceo.txt"

    def build_mock_response(
        self,
        request: ProductionRequest,
        context: Mapping[str, Any],
    ) -> dict[str, Any]:
        """Return a representative commercial assessment for local development."""

        budget = request.budget_range or "mid-scale theatrical budget"
        return {
            "greenlight": "YES",
            "title": request.title or "Untitled Feature",
            "genre": request.genre or "Historical drama",
            "budget": budget,
            "audience": "Core regional audience, diaspora viewers, and epic-drama fans",
            "market_assessment": "A distinct cultural lens and human-scale stakes support a theatrical and streaming window.",
            "localization_strategy": [
                "Develop primary dialogue in the story's most authentic language.",
                "Plan subtitles and dubbed tracks for priority release territories.",
            ],
            "roi_outlook": "Favorable with disciplined spectacle spending and a staged regional rollout.",
            "greenlight_rationale": "The premise has clear identity, audience emotion, and adaptable release potential.",
        }