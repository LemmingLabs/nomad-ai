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

    def _city_list_str(self, supported_cities: Sequence[str] | None = None) -> str:
        return ", ".join(supported_cities or self.SUPPORTED_CITIES)

    def _build_initial_contract(
        self,
        supported_cities: Sequence[str] | None = None,
    ) -> str:
        cities = supported_cities or self.SUPPORTED_CITIES
        example_city = cities[0] if cities else "the selected destination"
        return (
            "Respond ONLY with valid JSON matching this exact structure: "
            '{"title": "Short attractive trip title", "itinerary": {"summary": "Brief summary of the trip", "days": ['
            f'{{"day": 1, "title": "Day title", "city": "{example_city}", "location": "Specific Area / Landmark", '
            '"routing_location": "Searchable local-language map query", '
            '"activities": [{"time": "Morning/Afternoon/Evening or null", '
            '"time_window": "09:00-11:00 or null", "duration_minutes": 120 or null, '
            '"description": "Specific suggested actions at this stop", '
            '"practical_details": ["Optional planning note"], '
            '"type": "sightseeing/activity/meal/transfer/rest/alternative"}]}'
            ']}}. '
            f'The city field MUST be exactly one of: {self._city_list_str(cities)}. '
            "Do not include markdown blocks or any other text outside the JSON."
        )

    def build_system_prompt(self, country_name: str = "Kyrgyzstan") -> str:
        return (
            f"You are NomadAI, a {country_name} travel planning expert. "
            "Be practical and concise. Always keep traveler constraints in mind. "
            "Always respond in pure JSON. No markdown blocks. "
            "Ensure the response strictly follows the JSON contract, including 'updated_itinerary' if required."
        )

    def build_initial_generation_prompt(
        self,
        days: int,
        interests: list[str] | str,
        travel_style: str | None = None,
        budget: str | None = None,
        accommodation_type: str | None = None,
        user_prompt: str | None = None,
        country_name: str = "Kyrgyzstan",
        destination_name: str = "Kyrgyzstan",
        supported_cities: Sequence[str] | None = None,
    ) -> str:
        if isinstance(interests, list):
            interests_text = ", ".join(interests)
        else:
            interests_text = interests

        budget_str = str(budget)
        if budget_str.isdigit():
            budget_str = f"{budget_str} USD"

        style_str = travel_style or "not specified"
        accomm_str = accommodation_type or "not specified"

        extra = ""
        if user_prompt:
            extra = f"\nAdditional user request:\n{user_prompt}\n"

        return (
            f"Create an initial trip plan for {destination_name}, {country_name} with these constraints:\n"
            f"- Selected country: {country_name}. Keep every itinerary day within this country.\n"
            f"- Selected destination: {destination_name}. Do not substitute a different country or destination.\n"
            f"- Budget: {budget_str}\n"
            f"- Days: {days}\n"
            f"- Interests: {interests_text}\n"
            f"- Travel style: {style_str}\n"
            f"- Accommodation: {accomm_str}\n"
            f"{extra}\n"
            f"IMPORTANT: You MUST generate exactly {days} day objects in the itinerary. "
            "Do NOT include hotels or recommended places - the backend will add them automatically.\n"
            "Rules for Generation:\n"
            "1. Location: MUST be a specific landmark, museum, park, bazaar, square, gorge, lakefront, mosque, cultural center, or known attraction. Do NOT use vague placeholders like 'City Center', 'Downtown'. location field MUST be in English for the UI.\n"
            "2. Activity Type: use one of 'sightseeing', 'activity', 'meal', 'transfer', 'rest', or 'alternative'.\n"
            "3. Title: MUST be concrete and trip-specific.\n"
            "4. Summary: MUST mention the route or major destinations. Be practical and concise.\n"
            f"5. Routing Location: use a searchable local-language query suitable for maps in {country_name}.\n"
            "6. Activities: describe concrete things the traveler can do at each stop, not only the place name. "
            "Give a reasonable estimated duration in minutes when possible; otherwise set duration_minutes to null. "
            "Use approximate time windows only, and use null when unknown. Put logistics in practical_details. "
            "Do not invent opening hours, permits, prices, reservations, or confirmed transport. These are suggestions.\n"
            f"{self._build_initial_contract(supported_cities)}"
        )

    def build_continuation_prompt(
        self,
        user_message: str,
        current_itinerary: dict[str, Any] | None,
        change_intent: str = "generic_update",
        country_code: str = "KG",
        country_name: str = "Kyrgyzstan",
        destination_name: str = "Kyrgyzstan",
        supported_cities: Sequence[str] | None = None,
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
            "9. Preserve activity duration_minutes, time_window, practical_details, and suggestion/source labels on unchanged days. "
            "For changed activities, provide useful suggested actions and use null when timing is unknown. "
            "Do not present generated access, opening, permit, or price details as verified.\n"
            f"10. The trip is scoped to {destination_name}, {country_name} ({country_code}). Keep all days in this country. "
            "Do not change country or destination unless the traveler explicitly requests it and the destination is supported.\n"
            f"11. The city field MUST be exactly one of: {self._city_list_str(supported_cities)}. "
            "If the user requests a place outside the supported city list, use the closest supported city only when it is in the selected country and describe the requested place accurately.\n"
            "12. Preserve valid JSON structure exactly.\n\n"
        )

        return (
            "Continue the travel planning conversation.\n"
            f"{editing_rules}"
            f"{intent_section}"
            f"Selected trip destination: {destination_name}, {country_name} ({country_code}). Do not switch destination implicitly.\n"
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
        country_code: str = "KG",
        country_name: str = "Kyrgyzstan",
        destination_name: str = "Kyrgyzstan",
        supported_cities: Sequence[str] | None = None,
    ) -> list[dict[str, str]]:
        messages: list[dict[str, str]] = [
            {"role": "system", "content": self.build_system_prompt(country_name)}
        ]
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
                    country_code=country_code,
                    country_name=country_name,
                    destination_name=destination_name,
                    supported_cities=supported_cities,
                ),
            }
        )
        return messages
