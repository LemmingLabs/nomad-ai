"""Gemini GenerateContent boundary for the existing JSON itinerary contract."""
import json
import re
from typing import Any

import httpx

from app.core.config import settings


class AIProviderError(Exception):
    """A safe, provider-independent error without response bodies or credentials."""


class GeminiClient:
    def __init__(self, api_key: str | None = None, model: str | None = None, timeout: float | None = None):
        self.api_key = api_key if api_key is not None else settings.GEMINI_API_KEY
        self.model = model or settings.GEMINI_MODEL
        self.timeout = timeout if timeout is not None else settings.GEMINI_TIMEOUT_SECONDS

    def chat_json(self, messages: list[dict[str, str]], mode: str = "continuation") -> dict[str, Any]:
        del mode  # The same JSON contract is used for generation, chat and place selection.
        if not self.api_key:
            raise AIProviderError("Gemini API key is not configured")
        if not re.fullmatch(r"[A-Za-z0-9._-]+", self.model):
            raise AIProviderError("Invalid Gemini model configuration")

        system_parts = []
        contents: list[dict[str, Any]] = []
        for message in messages:
            role = message.get("role")
            content = message.get("content")
            if not isinstance(content, str) or not content.strip():
                continue
            if role == "system":
                system_parts.append({"text": content})
                continue
            if role not in {"user", "assistant"}:
                raise AIProviderError("Unsupported conversation role")
            gemini_role = "model" if role == "assistant" else "user"
            if contents and contents[-1]["role"] == gemini_role:
                contents[-1]["parts"].append({"text": content})
            else:
                contents.append({"role": gemini_role, "parts": [{"text": content}]})
        if not contents:
            raise AIProviderError("Conversation is empty")
        payload: dict[str, Any] = {
            "contents": contents,
            "generationConfig": {"responseMimeType": "application/json"},
        }
        if system_parts:
            payload["systemInstruction"] = {"parts": system_parts}

        try:
            response = httpx.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent",
                headers={"x-goog-api-key": self.api_key}, json=payload, timeout=self.timeout,
            )
            response.raise_for_status()
            data = response.json()
            candidate = data["candidates"][0]
            if candidate.get("finishReason") != "STOP":
                raise ValueError("Incomplete or blocked response")
            parts = candidate["content"]["parts"]
            text = "".join(part.get("text", "") for part in parts if not part.get("thought"))
            result = json.loads(text)
            if not isinstance(result, dict):
                raise ValueError("Expected a JSON object")
            return result
        except (httpx.HTTPError, ValueError, KeyError, IndexError, TypeError, AttributeError):
            # Do not expose provider error bodies, request URLs, prompts or API keys.
            raise AIProviderError("Gemini request failed or returned an invalid response") from None
