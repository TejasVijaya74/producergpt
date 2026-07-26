"""Dialogue agent for character voice and localized scene writing."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Mapping

from backend.agents.base_agent import BaseAgent

if TYPE_CHECKING:
    from backend.models.request import ProductionRequest


class DialogueAgent(BaseAgent):
    """Write playable dialogue that reflects character stakes and target language."""

    name = "dialogue"
    prompt_filename = "dialogue.txt"

    def build_mock_response(
        self,
        request: ProductionRequest,
        context: Mapping[str, Any],
    ) -> dict[str, Any]:
        """Return a concise dialogue preview for local development."""

        return {
            "primary_language": request.language,
            "dialogue_scenes": [
                {
                    "scene": "Private strategy chamber",
                    "intent": "Reveal the cost of choosing responsibility over safety.",
                    "lines": [
                        {"character": "PROTAGONIST", "line": "Fear can guard a door, but it cannot build a future."},
                        {"character": "CONFIDANT", "line": "Then make them see the future before they can touch it."},
                    ],
                },
                {
                    "scene": "Before the final confrontation",
                    "intent": "Turn individual resolve into a shared promise.",
                    "lines": [
                        {"character": "PROTAGONIST", "line": "We are not here to be remembered. We are here to make tomorrow possible."},
                        {"character": "ENSEMBLE", "line": "Then we stand together."},
                    ],
                },
            ],
            "voice_notes": [
                "Keep authority earned through specificity rather than speeches alone.",
                "Use cultural idiom only after native-speaker review.",
            ],
            "subtitle_notes": [
                "Favor concise subtitle lines that preserve intent over literal word order.",
                "Reserve on-screen text for essential historical context.",
            ],
        }