import json
from collections.abc import Sequence
from typing import Any


class PromptBuilder:
    # All supported cities. Extend this list to add new destinations.
    SUPPORTED_CITIES = [
        "Bishkek",
        "Karakol",
        "Cholpon-Ata",
        "Osh",
        "Bokonbaevo",
        "Jeti-Oguz",
        "Ala-Archa",
        "Kochkor",
        "Naryn",
        "Tamga",
        "Barskoon",
    ]

    CONTINUATION_CONTRACT = (
        "Respond ONLY with valid JSON matching this exact structure: "
        '{"message": "your text reply to the user", "updated_itinerary": <full itinerary JSON or null>}. '
        "Do not include markdown blocks or any other text outside the JSON."
    )

    def _city_list_str(self) -> str:
        return ", ".join(self.SUPPORTED_CITIES)

    def _build_initial_contract(self) -> str:
        return (
            "Respond ONLY with valid JSON matching this exact structure: "
            '{"title": "Short attractive trip title", "itinerary": {"summary": "Brief summary of the trip", "days": ['
            '{"day": 1, "title": "Day title", "city": "Bishkek", "location": "Specific Area / Landmark", '
            '"activities": [{"time": "Morning/Afternoon/Evening", "description": "...", "type": "sightseeing/activity/meal"}]}'
            ']}}. '
            f'The city field MUST be exactly one of: {self._city_list_str()}. '
            "Do not include markdown blocks or any other text outside the JSON."
        )

    def build_system_prompt(self) -> str:
        return (
            "You are NomadAI, a Kyrgyzstan travel planning expert. "
            "Be practical and concise. Always keep traveler constraints in mind. "
            "Always respond in pure JSON. No markdown blocks."
        )

    def build_initial_generation_prompt(
        self,
        days: int,
        interests: list[str] | str,
        travel_style: str,
        budget: str,
    ) -> str:
        if isinstance(interests, list):
            interests_text = ", ".join(interests)
        else:
            interests_text = interests

        return (
            "Create an initial Kyrgyzstan trip plan with these constraints:\n"
            f"- Budget: {budget}\n"
            f"- Days: {days}\n"
            f"- Interests: {interests_text}\n"
            f"- Travel style: {travel_style or 'not specified'}\n\n"
            f"IMPORTANT: You MUST generate exactly {days} day objects in the itinerary. "
            "Do NOT include hotels or recommended places - the backend will add them automatically.\n"
            f"{self._build_initial_contract()}"
        )

    def build_continuation_prompt(
        self,
        user_message: str,
        current_itinerary: dict[str, Any] | None,
        change_intent: str,
    ) -> str:
        itinerary_text = json.dumps(
            current_itinerary or {},
            ensure_ascii=False,
            sort_keys=True,
        )

        intent_rules = ""
        if change_intent == "local_edit":
            intent_rules = (
                "- modify only the relevant day(s) or section(s)\n"
                "- preserve all unrelated days exactly\n"
            )
        elif change_intent == "budget_change":
            intent_rules = (
                "- keep route mostly stable\n"
                "- adjust trip style and activities to match the new budget\n"
            )
        elif change_intent == "duration_change":
            intent_rules = (
                "- adjust number of days carefully\n"
                "- preserve existing structure where possible\n"
            )
        elif change_intent == "group_size_change":
            intent_rules = (
                "- adapt activities and pacing for group size\n"
                "- keep general route unless user requested otherwise\n"
            )
        elif change_intent == "full_replan":
            intent_rules = (
                "- broader trip changes are allowed\n"
                "- but still return valid full itinerary\n"
            )

        intent_section = f"Detected change intent: {change_intent}\n"
        if intent_rules:
            intent_section += f"Intent-Specific Rules:\n{intent_rules}\n"
        else:
            intent_section += "\n"

        editing_rules = (
            "Editing Rules:\n"
            "1. You are editing an existing trip, not generating a brand new one from scratch.\n"
            "2. Preserve the current itinerary structure unless the user explicitly asks to change it.\n"
            "3. Make minimal necessary changes based on the user request.\n"
            "4. Keep unchanged days exactly as they are.\n"
            "5. If the user asks for one local change, do not rewrite unrelated days.\n"
            "6. If any trip change is made, you MUST return the full updated itinerary.\n"
            "7. If NO itinerary change is needed, return 'updated_itinerary': null.\n"
            "8. Do not add hotels or recommended_places manually — the backend will enrich the itinerary automatically.\n"
            f"9. The city field MUST be exactly one of: {self._city_list_str()}. "
            "If a user requests a place that is not in this list (e.g. a specific gorge or village), "
            "map it to the nearest supported city and describe the actual destination in the location field.\n"
            "10. Preserve valid JSON structure exactly.\n\n"
        )

        return (
            "Continue the travel planning conversation.\n"
            f"{editing_rules}"
            f"{intent_section}"
            f"User request: {user_message}\n"
            f"Current itinerary JSON:\n{itinerary_text}\n"
            f"{self.CONTINUATION_CONTRACT}"
        )

    def build_chat_messages(
        self,
        history_messages: Sequence[Any],
        user_message: str,
        current_itinerary: dict[str, Any] | None,
        change_intent: str = "generic_update",
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
                    change_intent=change_intent,
                ),
            }
        )
        return messages