import json
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

        raw = self.groq_client.chat_json(messages, mode="continuation")
        return self._normalize_response(raw)

    def generate_initial_trip(
        self,
        days: int,
        interests: list[str] | str,
        travel_style: str,
        budget: str,
    ) -> dict[str, Any]:
        prompt = self.prompt_builder.build_initial_generation_prompt(
            days=days,
            interests=interests,
            travel_style=travel_style,
            budget=budget,
        )
        raw = self.groq_client.chat_json(
            [
                {
                    "role": "system",
                    "content": self.prompt_builder.build_system_prompt(),
                },
                {"role": "user", "content": prompt},
            ],
            mode="initial"
        )
        
        if isinstance(raw, str):
            try:
                raw = json.loads(raw)
            except json.JSONDecodeError:
                raise ValueError("Initial AI generation failed: not valid JSON")
                
        if not isinstance(raw, dict):
            raise ValueError("Initial AI generation failed: root object must be a dict")
            
        title = raw.get("title")
        if not isinstance(title, str) or not title.strip():
            raise ValueError("Initial AI generation failed: missing or empty 'title'")
            
        itinerary = raw.get("itinerary")
        if not isinstance(itinerary, dict):
            raise ValueError("Initial AI generation failed: missing or invalid 'itinerary' dictionary")
            
        if not isinstance(itinerary.get("days"), list):
            raise ValueError("Initial AI generation failed: 'itinerary' must contain a 'days' list")
        
        return raw

    def _normalize_response(
        self, raw: Any
    ) -> tuple[str, dict[str, Any] | None]:
        if isinstance(raw, str):
            try:
                raw = json.loads(raw)
            except json.JSONDecodeError:
                stripped_raw = raw.strip()
                if stripped_raw:
                    return stripped_raw, None
                return "I have updated your trip plan based on your request.", None

        if not isinstance(raw, dict):
            return "I have updated your trip plan based on your request.", None

        message = raw.get("message") or raw.get("assistant_message") or raw.get("content")
        if not isinstance(message, str) or not message.strip():
            message = "I have updated your trip plan based on your request."

        updated_itinerary = raw.get("updated_itinerary")
        if updated_itinerary is not None and not isinstance(updated_itinerary, dict):
            updated_itinerary = None

        return message, updated_itinerary
