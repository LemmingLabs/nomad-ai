from collections.abc import Sequence
from typing import Any


class PromptBuilder:
    def build_system_prompt(self) -> str:
        return (
            "You are NomadAI, a Kyrgyzstan travel planning expert. "
            "Be practical and concise. Always keep traveler constraints in mind. "
            "When itinerary changes are needed, return valid JSON only with keys "
            "'message' and 'updated_itinerary'. If no itinerary update is required, "
            "set 'updated_itinerary' to null."
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
            "Create an initial Kyrgyzstan trip plan with these constraints:\\n"
            f"- Budget: {budget} USD\\n"
            f"- Days: {days}\\n"
            f"- Interests: {interests_text}\\n"
            f"- Accommodation type: {accommodation_type or 'not specified'}\\n"
            "Respond in JSON with 'message' and 'updated_itinerary'."
        )

    def build_continuation_prompt(
        self,
        user_message: str,
        current_itinerary: dict[str, Any] | None,
    ) -> str:
        itinerary_text = current_itinerary if current_itinerary is not None else {}
        return (
            "Continue the travel planning conversation.\\n"
            f"User request: {user_message}\\n"
            f"Current itinerary JSON: {itinerary_text}\\n"
            "Return JSON only: {\"message\": string, \"updated_itinerary\": object|null}."
        )

    def build_chat_messages(
        self,
        history_messages: Sequence[Any],
        user_message: str,
        current_itinerary: dict[str, Any] | None,
    ) -> list[dict[str, str]]:
        messages: list[dict[str, str]] = [
            {"role": "system", "content": self.build_system_prompt()}
        ]

        for item in history_messages:
            role = getattr(item, "role", None)
            content = getattr(item, "content", None)
            if role and content:
                messages.append({"role": role, "content": content})

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
