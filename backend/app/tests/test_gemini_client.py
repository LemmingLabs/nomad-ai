from unittest.mock import Mock

import httpx
import pytest

from app.integrations.gemini_client import AIProviderError, GeminiClient
from app.services.ai_service import AIService


def test_gemini_generates_json_and_preserves_system_and_history(monkeypatch):
    post = Mock(return_value=httpx.Response(200, json={"candidates": [{
        "finishReason": "STOP", "content": {"parts": [{"text": '{"message":"done","updated_itinerary":null}'}]},
    }]}, request=httpx.Request("POST", "https://example.test")))
    monkeypatch.setattr(httpx, "post", post)
    result = GeminiClient(api_key="test-key", model="gemini-3.5-flash-lite", timeout=12).chat_json([
        {"role": "system", "content": "system rules"},
        {"role": "user", "content": "first"},
        {"role": "assistant", "content": "reply"},
        {"role": "user", "content": "second"},
    ])
    assert result == {"message": "done", "updated_itinerary": None}
    args, kwargs = post.call_args
    assert args[0].endswith("/models/gemini-3.5-flash-lite:generateContent")
    assert kwargs["headers"]["x-goog-api-key"] == "test-key"
    assert kwargs["timeout"] == 12
    assert kwargs["json"]["systemInstruction"] == {"parts": [{"text": "system rules"}]}
    assert [item["role"] for item in kwargs["json"]["contents"]] == ["user", "model", "user"]
    assert kwargs["json"]["generationConfig"]["responseMimeType"] == "application/json"


@pytest.mark.parametrize("response", [
    {"candidates": []},
    {"candidates": [{"finishReason": "SAFETY"}]},
    {"candidates": [{"finishReason": "MAX_TOKENS", "content": {"parts": [{"text": "{}"}]}}]},
    {"candidates": [{"finishReason": "STOP", "content": {"parts": [{"text": "bad json"}]}}]},
    {"candidates": [{"finishReason": "STOP", "content": {"parts": [{"text": "[]"}]}}]},
])
def test_gemini_rejects_blocked_incomplete_or_invalid_output(monkeypatch, response):
    monkeypatch.setattr(httpx, "post", Mock(return_value=httpx.Response(
        200, json=response, request=httpx.Request("POST", "https://example.test"))))
    with pytest.raises(AIProviderError):
        GeminiClient(api_key="test-key").chat_json([{"role": "user", "content": "private"}])


def test_gemini_fails_safely_on_missing_key_and_timeout(monkeypatch):
    with pytest.raises(AIProviderError, match="not configured"):
        GeminiClient(api_key="").chat_json([{"role": "user", "content": "private"}])
    post = Mock(side_effect=httpx.ReadTimeout("private prompt and secret"))
    monkeypatch.setattr(httpx, "post", post)
    with pytest.raises(AIProviderError) as error:
        GeminiClient(api_key="secret").chat_json([{"role": "user", "content": "private"}])
    assert "private" not in str(error.value)
    assert "secret" not in str(error.value)


def test_ai_service_uses_configured_gemini_client(monkeypatch):
    monkeypatch.setattr("app.services.ai_service.settings.AI_PROVIDER", "gemini")
    assert isinstance(AIService().client, GeminiClient)


@pytest.mark.parametrize("status", [401, 429, 500])
def test_gemini_http_failures_do_not_expose_provider_response(monkeypatch, status):
    request = httpx.Request("POST", "https://example.test")
    monkeypatch.setattr(httpx, "post", Mock(return_value=httpx.Response(
        status, text="secret private data", request=request)))
    with pytest.raises(AIProviderError) as error:
        GeminiClient(api_key="secret").chat_json([{"role": "user", "content": "private"}])
    assert "secret" not in str(error.value)
    assert "private" not in str(error.value)


def test_explicit_groq_and_development_mock_selection(monkeypatch):
    from app.integrations.groq_client import GroqClient

    monkeypatch.setattr("app.services.ai_service.settings.AI_PROVIDER", "groq")
    client = AIService().client
    assert isinstance(client, GroqClient)
    assert not client.use_mock
    monkeypatch.setattr("app.services.ai_service.settings.AI_PROVIDER", "mock")
    client = AIService().client
    assert isinstance(client, GroqClient)
    assert client.use_mock
