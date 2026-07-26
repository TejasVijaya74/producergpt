"""Storyboard agent for visual sequencing and camera language."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Mapping

from backend.agents.base_agent import BaseAgent

if TYPE_CHECKING:
    from backend.models.request import ProductionRequest


class StoryboardAgent(BaseAgent):
    """Translate the approved story direction into a practical shot plan."""

    name = "storyboard"
    prompt_filename = "storyboard.txt"

    def build_mock_response(
        self,
        request: ProductionRequest,
        context: Mapping[str, Any],
    ) -> dict[str, Any]:
        """Return a visual-development preview in mock mode."""

        return {
            "visual_style": "Grounded cinematic realism with textured natural light and period-specific production design.",
            "color_palette": ["warm earth", "deep indigo", "weathered brass", "torch amber"],
            "shots": [
                {
                    "sequence": 1,
                    "framing": "Extreme wide establishing shot",
                    "camera": "Slow crane descent",
                    "purpose": "Place the story in a living world before introducing the protagonist.",
                },
                {
                    "sequence": 2,
                    "framing": "Handheld medium close-up",
                    "camera": "Subtle forward push",
                    "purpose": "Capture the protagonist's private reaction to public pressure.",
                },
                {
                    "sequence": 3,
                    "framing": "Low-angle ensemble wide",
                    "camera": "Controlled lateral tracking",
                    "purpose": "Make collective resolve feel larger than one individual.",
                },
            ],
            "camera_language": [
                "Use stable compositions for strategy and conviction.",
                "Reserve handheld movement for emotional uncertainty.",
                "Transition to wider frames as the protagonist's impact expands.",
            ],
            "production_design_notes": [
                "Prioritize practical textures and lived-in surfaces over pristine sets.",
                "Validate symbols, garments, and architectural motifs with consultants.",
            ],
        }