from collections.abc import Sequence
from typing import Any

from app.integrations.groq_client import GroqClient
from app.utils.prompt_builder import PromptBuilder


class AIService:
    def __init__(
        self,
        groq_client: GroqClient | None = None,
        prompt_builder: PromptBuilder | None = None,
    ):
        self.groq_client = groq_client or GroqClient()
        self.prompt_builder = prompt_builder or PromptBuilder()

    def continue_trip(
        self,
        history_messages: Sequence[Any],
        user_message: str,
        current_itinerary: dict[str, Any] | None,
    ) -> tuple[str, dict[str, Any] | None]:
        messages = self.prompt_builder.build_chat_messages(
            history_messages=history_messages,
            user_message=user_message,
            current_itinerary=current_itinerary,
        )

        raw = self.groq_client.chat_json(messages)
        return self._normalize_response(raw)

    def _normalize_response(
        self, raw: dict[str, Any]
    ) -> tuple[str, dict[str, Any] | None]:
        message = raw.get("message") or raw.get("assistant_message") or raw.get("content")
        if not isinstance(message, str) or not message.strip():
            message = "I have updated your trip plan based on your request."

        updated_itinerary = raw.get("updated_itinerary")
        if updated_itinerary is not None and not isinstance(updated_itinerary, dict):
            updated_itinerary = None

        return message, updated_itinerary
