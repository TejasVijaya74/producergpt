"""Music agent for score direction and soundtrack generation prompts."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Mapping

from backend.agents.base_agent import BaseAgent

if TYPE_CHECKING:
    from backend.models.request import ProductionRequest


class MusicAgent(BaseAgent):
    """Develop an adaptive score concept that supports the story's emotional arc."""

    name = "music"
    prompt_filename = "music.txt"

    def build_mock_response(
        self,
        request: ProductionRequest,
        context: Mapping[str, Any],
    ) -> dict[str, Any]:
        """Return an original score-development preview in mock mode."""

        return {
            "score_concept": "An intimate folk-rooted motif expands into a percussive orchestral theme as personal conviction becomes collective action.",
            "musical_palette": [
                "Regional acoustic instruments verified with cultural consultants",
                "Low strings for moral pressure",
                "Frame drums and restrained brass for momentum",
            ],
            "cue_sheet": [
                {"cue": "Opening world", "emotion": "Wonder with latent tension", "placement": "Opening sequence"},
                {"cue": "The decision", "emotion": "Focused resolve", "placement": "Act two turning point"},
                {"cue": "Shared future", "emotion": "Earned uplift", "placement": "Finale and end credits"},
            ],
            "generation_prompt": "Cinematic orchestral score with organic acoustic textures, gradual dynamic build, emotionally restrained opening, heroic but human finale, no vocals.",
            "mix_notes": [
                "Leave dialogue space in midrange-heavy strategic scenes.",
                "Use silence before pivotal commitments to preserve dramatic impact.",
            ],
        }