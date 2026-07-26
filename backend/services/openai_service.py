"""Reusable asynchronous OpenAI integration for all ProducerGPT agents."""

from __future__ import annotations

import json
import logging
from typing import Any

from openai import AsyncOpenAI, OpenAIError

from backend.core.config import Settings


logger = logging.getLogger(__name__)


class OpenAIServiceError(RuntimeError):
    """Base exception for OpenAI integration failures."""


class OpenAIConfigurationError(OpenAIServiceError):
    """Raised when a live provider call is attempted without an API key."""


class OpenAIResponseError(OpenAIServiceError):
    """Raised when the provider response is not a JSON object."""


class OpenAIService:
    """Encapsulate OpenAI SDK usage and enforce JSON-object responses."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client = self._create_client()

    @property
    def is_mock_mode(self) -> bool:
        """Return whether agents should use their deterministic local previews."""

        return self._settings.openai_mock_mode

    @property
    def model(self) -> str:
        """Return the configured model identifier for observability."""

        return self._settings.openai_model

    def _create_client(self) -> AsyncOpenAI | None:
        if self._settings.openai_mock_mode or not self._settings.has_openai_credentials:
            return None

        api_key = self._settings.openai_api_key
        assert api_key is not None
        return AsyncOpenAI(
            api_key=api_key.get_secret_value(),
            timeout=self._settings.openai_timeout_seconds,
            max_retries=self._settings.openai_max_retries,
        )

    async def generate_json(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        temperature: float | None = None,
    ) -> dict[str, Any]:
        """Generate and parse a JSON object from the configured OpenAI model.

        Args:
            system_prompt: Role instructions owned by a specific agent.
            user_prompt: Delimited project context assembled by that agent.
            temperature: Optional sampling override for the request.

        Raises:
            OpenAIConfigurationError: If no key is configured for a live request.
            OpenAIServiceError: If the provider request fails.
            OpenAIResponseError: If the response cannot be parsed as a JSON object.
        """

        if self._client is None:
            raise OpenAIConfigurationError(
                "OPENAI_API_KEY is required unless OPENAI_MOCK_MODE=true."
            )

        try:
            completion = await self._client.chat.completions.create(
                model=self._settings.openai_model,
                temperature=temperature or self._settings.openai_temperature,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
        except OpenAIError as error:
            logger.warning("OpenAI request failed for model %s", self.model, exc_info=True)
            raise OpenAIServiceError("OpenAI generation request failed.") from error

        content = completion.choices[0].message.content if completion.choices else None
        return self._decode_json(content)

    async def close(self) -> None:
        """Close the SDK client when application shutdown releases resources."""

        if self._client is not None:
            await self._client.close()

    @staticmethod
    def _decode_json(content: str | None) -> dict[str, Any]:
        if not content:
            raise OpenAIResponseError("OpenAI returned an empty response.")

        normalized_content = content.strip()
        if normalized_content.startswith("```"):
            normalized_content = normalized_content.split("\n", maxsplit=1)[-1]
            normalized_content = normalized_content.rsplit("```", maxsplit=1)[0].strip()

        try:
            payload = json.loads(normalized_content)
        except json.JSONDecodeError as error:
            raise OpenAIResponseError("OpenAI did not return valid JSON.") from error

        if not isinstance(payload, dict):
            raise OpenAIResponseError("OpenAI response must be a JSON object.")

        return payload