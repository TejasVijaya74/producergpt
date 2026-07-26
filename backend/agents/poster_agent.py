"""Poster prompt agent for key art and campaign positioning."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Mapping

from backend.agents.base_agent import BaseAgent

if TYPE_CHECKING:
    from backend.models.request import ProductionRequest


class PosterPromptAgent(BaseAgent):
    """Create focused visual key-art prompts and campaign copy."""

    name = "poster"
    prompt_filename = "poster.txt"

    def build_mock_response(
        self,
        request: ProductionRequest,
        context: Mapping[str, Any],
    ) -> dict[str, Any]:
        """Return a campaign-ready key-art preview in mock mode."""

        title = request.title or "Untitled Feature"
        return {
            "poster_prompt": (
                f"Premium cinematic one-sheet for '{title}', a determined central leader in period-authentic attire, "
                "community and landscape layered behind them, practical torchlight and sunrise contrast, tactile fabric, "
                "historical epic composition, room for title treatment, no logos, no text rendered in image"
            ),
            "tagline": "A future is not inherited. It is defended.",
            "campaign_positioning": "A human-scale epic about leadership, sacrifice, and collective courage.",
            "alternate_prompts": [
                "Intimate character poster: weathered portrait, decisive gaze, negative space, restrained period texture.",
                "Ensemble poster: a community standing on a fortress wall at dawn, layered depth, cinematic scale.",
            ],
            "format_notes": [
                "Design separate vertical theatrical, square social, and landscape streaming variants.",
                "Keep typography clear of key costume and architectural details.",
            ],
        }