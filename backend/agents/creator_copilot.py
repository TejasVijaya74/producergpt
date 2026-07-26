"""Creator copilot agent for editorial and finishing recommendations."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Mapping

from backend.agents.base_agent import BaseAgent

if TYPE_CHECKING:
    from backend.models.request import ProductionRequest


class CreatorCopilotAgent(BaseAgent):
    """Translate the unified package into practical finishing guidance for creators."""

    name = "creator_copilot"
    prompt_filename = "copilot.txt"

    def build_mock_response(
        self,
        request: ProductionRequest,
        context: Mapping[str, Any],
    ) -> dict[str, Any]:
        """Return post-production guidance for local and demo workflows."""

        return {
            "editing_suggestions": [
                "Open each act with a quiet image before accelerating into plot information.",
                "Use reaction shots to let moral choices land before cutting to spectacle.",
                "Carry one visual motif across the midpoint and finale for emotional continuity.",
            ],
            "camera_movements": [
                "Use a slow push-in for irreversible commitments.",
                "Use lateral tracking to follow strategy and collective movement.",
                "Keep handheld shots selective and tied to personal instability.",
            ],
            "subtitle_style": "High-contrast off-white sans serif with a subtle dark shadow, two lines maximum, positioned inside title-safe area.",
            "color_grading": "Start with restrained natural warmth, deepen shadows during moral pressure, and restore measured gold tones in the finale.",
            "voice_acting": [
                "Favor controlled breath and conversational authority over declamatory delivery.",
                "Record alternate takes for culturally specific terms and honorifics.",
            ],
            "background_music": "Keep the central motif sparse beneath dialogue, then expand instrumentation only when the audience has earned release.",
        }