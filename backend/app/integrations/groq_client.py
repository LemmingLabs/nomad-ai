import json
from typing import Any

from app.core.config import settings

try:
    from groq import Groq  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    Groq = None


class GroqClient:
    def __init__(
        self,
        api_key: str | None = None,
        model: str = "llama-3.3-70b-versatile",
        use_mock: bool | None = None,
    ):
        self.api_key = api_key or settings.GROQ_API_KEY
        self.model = model
        self.use_mock = settings.DEBUG if use_mock is None else use_mock

    def chat_json(self, messages: list[dict[str, str]]) -> dict[str, Any]:
        if self.use_mock:
            return self._mock_response(messages)

        if not self.api_key or Groq is None:
            raise ValueError(
                "Groq API Key is missing or groq package not installed. "
                "Enable DEBUG or use_mock to run without real AI."
            )

        try:
            client = Groq(api_key=self.api_key)
            completion = client.chat.completions.create(
                model=self.model,
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.2,
            )
            content = completion.choices[0].message.content or "{}"
            return json.loads(content)
        except json.JSONDecodeError:
            return {"message": content, "updated_itinerary": None}
        except Exception:
            # Re-raise the exception properly in production
            raise

    def get_structured_output(self, messages: list[dict[str, str]]) -> dict[str, Any]:
        return self.chat_json(messages)

    def _mock_response(self, messages: list[dict[str, str]]) -> dict[str, Any]:
        last_user_text = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                last_user_text = msg.get("content", "")
                break

        return {
            "message": (
                "Mock response: I updated your plan based on the latest request. "
                f"Request context: {last_user_text[:120]}"
            ),
            "updated_itinerary": {
                "status": "mock-updated",
                "updated": True,
            },
        }
