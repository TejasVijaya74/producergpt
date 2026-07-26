"""Research agent for cultural, historical, and audience context."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Mapping

from backend.agents.base_agent import BaseAgent

if TYPE_CHECKING:
    from backend.models.request import ProductionRequest


class ResearchAgent(BaseAgent):
    """Ground a movie idea in references, emotional stakes, and current audience signals."""

    name = "research"
    prompt_filename = "research.txt"

    def build_mock_response(
        self,
        request: ProductionRequest,
        context: Mapping[str, Any],
    ) -> dict[str, Any]:
        """Return a local preview when OpenAI mock mode is enabled."""

        return {
            "historical_references": [
                "Validate dates, places, and named figures with primary or expert sources.",
                "Separate documented history from dramatized composite characters.",
            ],
            "emotional_hooks": [
                "A personal cost behind public leadership.",
                "A community choosing courage under pressure.",
            ],
            "real_world_inspiration": [
                "Use regional art, music, and architecture as story texture.",
                "Consult cultural historians and community voices early.",
            ],
            "trends": [
                "Character-led historical epics with contemporary emotional access.",
                "Localized releases supported by premium large-format spectacle.",
            ],
            "fact_check_notes": [
                f"Research briefing prepared for: {request.idea}",
                "Verify culturally sensitive details before principal photography.",
            ],
        }