import json
from collections.abc import Sequence
from typing import Any


class PromptBuilder:
    JSON_CONTRACT = (
        "Respond ONLY with valid JSON matching this exact structure: "
        '{"message": "your text reply to the user", "updated_itinerary": <full itinerary JSON or null>}. '
        "Do not include markdown blocks or any other text outside the JSON."
    )

    def build_system_prompt(self) -> str:
        return (
            "You are NomadAI, a Kyrgyzstan travel planning expert. "
            "Be practical and concise. Always keep traveler constraints in mind. "
            f"{self.JSON_CONTRACT}"
        )

    def build_initial_generation_prompt(
        self,
        budget: int,
        days: int,
        interests: list[str] | str,
        accommodation_type: str | None = None,
    ) -> str:
        if isinstance(interests, list):
            interests_text = ", ".join(interests)
        else:
            interests_text = interests

        return (
            "Create an initial Kyrgyzstan trip plan with these constraints:\n"
            f"- Budget: {budget} USD\n"
            f"- Days: {days}\n"
            f"- Interests: {interests_text}\n"
            f"- Accommodation type: {accommodation_type or 'not specified'}\n"
            f"{self.JSON_CONTRACT}"
        )

    def build_continuation_prompt(
        self,
        user_message: str,
        current_itinerary: dict[str, Any] | None,
    ) -> str:
        itinerary_text = json.dumps(
            current_itinerary or {},
            ensure_ascii=False,
            sort_keys=True,
        )
        return (
            "Continue the travel planning conversation.\n"
            f"User request: {user_message}\n"
            f"Current itinerary JSON:\n{itinerary_text}\n"
            f"{self.JSON_CONTRACT}"
        )

    def build_chat_messages(
        self,
        history_messages: Sequence[Any],
        user_message: str,
        current_itinerary: dict[str, Any] | None,
    ) -> list[dict[str, str]]:
        messages: list[dict[str, str]] = [{"role": "system", "content": self.build_system_prompt()}]
        history_payload: list[dict[str, str]] = []

        for item in history_messages:
            if isinstance(item, dict):
                role = item.get("role")
                content = item.get("content")
            else:
                role = getattr(item, "role", None)
                content = getattr(item, "content", None)
            if role and content:
                history_payload.append({"role": role, "content": content})

        normalized_user_message = user_message.strip()
        if (
            history_payload
            and history_payload[-1]["role"] == "user"
            and history_payload[-1]["content"].strip() == normalized_user_message
        ):
            history_payload.pop()

        messages.extend(history_payload)

        messages.append(
            {
                "role": "user",
                "content": self.build_continuation_prompt(
                    user_message=user_message,
                    current_itinerary=current_itinerary,
                ),
            }
        )
        return messages
