"""Studio agent for unifying the specialist outputs into a production package."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Mapping

from backend.agents.base_agent import BaseAgent

if TYPE_CHECKING:
    from backend.models.request import ProductionRequest


class PersonalHollywoodStudioAgent(BaseAgent):
    """Synthesize creative departments into one coherent studio recommendation."""

    name = "personal_hollywood_studio"
    prompt_filename = "studio.txt"

    def build_mock_response(
        self,
        request: ProductionRequest,
        context: Mapping[str, Any],
    ) -> dict[str, Any]:
        """Combine prior mock outputs into a unified local production direction."""

        ceo = context.get("ceo", {})
        script = context.get("script", {})
        poster = context.get("poster", {})
        ceo_data = ceo if isinstance(ceo, Mapping) else {}
        script_data = script if isinstance(script, Mapping) else {}
        poster_data = poster if isinstance(poster, Mapping) else {}

        return {
            "title": str(ceo_data.get("title") or request.title or "Untitled Feature"),
            "genre": str(ceo_data.get("genre") or request.genre or "Drama"),
            "budget": str(ceo_data.get("budget") or request.budget_range or "TBD"),
            "audience": str(ceo_data.get("audience") or "Defined after market analysis"),
            "production_summary": "A cohesive character-led epic with culturally grounded detail, deliberate spectacle, and a localized release strategy.",
            "creative_north_star": "Make every department reinforce the emotional cost of leadership and the power of collective resolve.",
            "video_prompt": str(
                script_data.get("video_prompt")
                or "Cinematic dramatic feature, natural textures, emotionally precise performances, practical locations."
            ),
            "poster_prompt": str(poster_data.get("poster_prompt") or "Campaign key art to be developed."),
            "quality_gates": [
                "Review factual claims and sensitive depictions with subject-matter experts.",
                "Confirm that script, score, and visual language share the same emotional arc.",
                "Run localization review before final campaign assets are approved.",
            ],
        }