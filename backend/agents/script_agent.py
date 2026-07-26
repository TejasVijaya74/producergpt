"""Script agent for story architecture and screenplay material."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Mapping

from backend.agents.base_agent import BaseAgent

if TYPE_CHECKING:
    from backend.models.request import ProductionRequest


class ScriptAgent(BaseAgent):
    """Develop a cinematic narrative blueprint from the approved production brief."""

    name = "script"
    prompt_filename = "script.txt"

    def build_mock_response(
        self,
        request: ProductionRequest,
        context: Mapping[str, Any],
    ) -> dict[str, Any]:
        """Return a compact screenplay-development preview for local mode."""

        title = request.title or "Untitled Feature"
        return {
            "title": title,
            "logline": f"Against mounting pressure, a determined protagonist must transform an idea of leadership into a lived promise: {request.idea}",
            "act_structure": {
                "act_one": "A defining injustice exposes the protagonist's responsibility to their people.",
                "act_two": "Alliances, sacrifice, and strategic setbacks reshape the mission.",
                "act_three": "The protagonist earns victory by choosing the community over personal glory.",
            },
            "key_scenes": [
                "An intimate opening that shows what the protagonist stands to lose.",
                "A pivotal council scene where a risky plan divides trusted allies.",
                "A final public choice that pays off the story's central promise.",
            ],
            "screenplay_excerpt": "PROTAGONIST: A crown is only metal until the people decide it means something.\nALLY: Then give them a reason to decide.",
            "video_prompt": "Cinematic historical drama, practical locations, expressive close-ups, golden-hour exteriors, grounded costumes, dynamic but restrained camera movement.",
        }