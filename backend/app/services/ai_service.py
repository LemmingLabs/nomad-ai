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
        change_intent = self._detect_change_intent(user_message)

        messages = self.prompt_builder.build_chat_messages(
            history_messages=history_messages,
            user_message=user_message,
            current_itinerary=current_itinerary,
            change_intent=change_intent,
        )

        raw = self.groq_client.chat_json(messages, mode="continuation")
        message, updated_itinerary = self._normalize_response(raw)

        if updated_itinerary is not None:
            if not self._validate_itinerary(updated_itinerary):
                updated_itinerary = None

        if updated_itinerary is not None and current_itinerary:
            old_days = len(current_itinerary.get("days", []))
            new_days = len(updated_itinerary.get("days", []))

            if new_days == 0 or abs(new_days - old_days) > 2:
                updated_itinerary = None

        return message, updated_itinerary

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

    def _validate_itinerary(self, itinerary: dict) -> bool:
        if not isinstance(itinerary, dict):
            return False
            
        days = itinerary.get("days")
        if not isinstance(days, list):
            return False
            
        for day in days:
            if not isinstance(day, dict):
                return False
            if "day" not in day or "title" not in day or "activities" not in day:
                return False
            if not isinstance(day.get("activities"), list):
                return False
                
        return True

    def _detect_change_intent(self, user_message: str) -> str:
        text = user_message.lower().strip()

        # 1. full_replan
        full_replan_features = [
            "rewrite", "change everything", "start over", 
            "completely new", "replan", "rebuild trip", "new itinerary"
        ]
        if any(w in text for w in full_replan_features):
            return "full_replan"

        # 2. budget_change
        budget_features = [
            "cheap", "cheaper", "budget", "expensive", "cost", 
            "affordable", "luxury", "premium", "lower cost", "save money"
        ]
        if any(w in text for w in budget_features):
            return "budget_change"

        # 3. group_size_change
        group_features = [
            "people", "person", "group", "family", "kids", "children", 
            "couple", "solo", "for 2", "for 3", "for 4", "for 5"
        ]
        if any(w in text for w in group_features):
            return "group_size_change"

        # 4. local_edit
        local_edit_features = [
            "replace", "add", "remove", "swap", "move", "more nature", 
            "more mountains", "more food", "less city", "change day", "update day"
        ] + [f"day {i}" for i in range(1, 31)]
        if any(w in text for w in local_edit_features):
            return "local_edit"

        # 5. duration_change
        duration_features = [
            "add a day", "add one day", "extend", "longer", "shorter", 
            "reduce days", "more days", "fewer days", "extra day", 
            "remove a day", "cut one day"
        ]
        if any(w in text for w in duration_features):
            return "duration_change"

        # 6. generic_update
        return "generic_update"
