"""Production planner agent for turning a greenlit idea into deliverables."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Mapping

from backend.agents.base_agent import BaseAgent

if TYPE_CHECKING:
    from backend.models.request import ProductionRequest


class ProductionPlannerAgent(BaseAgent):
    """Create a production-ready task plan after the CEO greenlight."""

    name = "production_planner"
    prompt_filename = "planner.txt"

    def build_mock_response(
        self,
        request: ProductionRequest,
        context: Mapping[str, Any],
    ) -> dict[str, Any]:
        """Return a delivery-oriented local planning preview."""

        return {
            "production_phases": [
                "Development and factual validation",
                "Pre-production and visual development",
                "Principal photography and post-production",
                "Release localization and marketing",
            ],
            "tasks": [
                {"owner": "script", "deliverable": "Beat sheet, act structure, and key scenes"},
                {"owner": "storyboard", "deliverable": "Shot-driven visual storyboard"},
                {"owner": "dialogue", "deliverable": "Signature dialogue scenes"},
                {"owner": "music", "deliverable": "Score concept and cue prompts"},
                {"owner": "poster", "deliverable": "Campaign-ready poster prompt"},
            ],
            "dependencies": [
                "Use research notes to review cultural and historical claims.",
                "Align all creative agents to the approved audience and budget.",
            ],
            "risk_register": [
                "Schedule sensitivity readers before picture lock.",
                "Prototype large-scale scenes before committing to full visual effects spend.",
            ],
            "success_metrics": [
                "A coherent creative package across script, visuals, sound, and campaign.",
                "Clear localization requirements for target markets.",
            ],
        }