import pytest
from fastapi import HTTPException

from app.api.v1.messages import continue_trip_messages
from app.integrations.gemini_client import AIProviderError
from app.integrations.groq_client import GroqClient
from app.models.trip import Trip
from app.models.trip_message import TripMessage
from app.models.user import User
from app.schemas.trip_message import TripMessageCreateRequest
from app.services.ai_service import AIService


@pytest.mark.parametrize("response", [
    {}, None, [], "", "not json", {"message": "Done", "updated_itinerary": []},
    {"message": "Done", "updated_itinerary": {}},
    {"message": "Done", "updated_itinerary": {"days": []}},
    {"message": "Done", "updated_itinerary": {"days": ["invalid"]}},
    {"message": "Mock response: provider unavailable", "updated_itinerary": {"days": [{"day": 1}]}},
])
def test_invalid_response_does_not_save_chat_or_consume_usage(db_session, monkeypatch, response):
    user = User(email="invalid-response@example.com", password_hash="hashed")
    db_session.add(user)
    db_session.flush()
    original = {"days": [{"day": 1, "location": "Bishkek"}]}
    trip = Trip(user_id=user.id, title="Trip", budget="medium", days=1,
                interests=["nature"], travel_style="balanced", itinerary_json=original)
    db_session.add(trip)
    db_session.commit()

    class FakeClient:
        def chat_json(self, messages, mode):
            return response

    used = []
    monkeypatch.setattr("app.services.trip_message_service.AIService", lambda: AIService(groq_client=FakeClient()))
    monkeypatch.setattr("app.services.trip_message_service.LimitService.can_edit_chat", lambda *args: True)
    monkeypatch.setattr("app.services.trip_message_service.UsageService.increment_chat_edit", lambda *args: used.append(True))

    with pytest.raises(HTTPException) as error:
        continue_trip_messages(trip.id, TripMessageCreateRequest(content="Change day one"), db_session, user)

    db_session.refresh(trip)
    assert error.value.status_code == 503
    assert trip.itinerary_json == original
    assert trip.chat_revision == 0
    assert db_session.query(TripMessage).filter_by(trip_id=trip.id).count() == 0
    assert used == []


def test_normal_chat_reply_without_itinerary_remains_valid():
    assert AIService()._normalize_response({"message": "Which day?", "updated_itinerary": None}) == ("Which day?", None)


def test_retry_after_invalid_itinerary_uses_the_same_request_id(db_session, monkeypatch):
    user = User(email="retry-invalid@example.com", password_hash="hashed")
    db_session.add(user)
    db_session.flush()
    trip = Trip(user_id=user.id, title="Trip", budget="medium", days=1,
                interests=["nature"], travel_style="balanced", itinerary_json={"days": [{"day": 1}]})
    db_session.add(trip)
    db_session.commit()

    class FakeClient:
        calls = 0

        def chat_json(self, messages, mode):
            self.calls += 1
            if self.calls == 1:
                return {"message": "Done", "updated_itinerary": {"days": []}}
            return {"message": "Which day?", "updated_itinerary": None}

    provider = FakeClient()
    usage = []
    monkeypatch.setattr("app.services.trip_message_service.AIService", lambda: AIService(groq_client=provider))
    monkeypatch.setattr("app.services.trip_message_service.LimitService.can_edit_chat", lambda *args: True)
    monkeypatch.setattr("app.services.trip_message_service.UsageService.increment_chat_edit", lambda *args: usage.append(True))
    request = TripMessageCreateRequest(content="Change the plan", request_id="9f5ae513-3483-4cac-8c76-e8b3498c5cc2")

    with pytest.raises(HTTPException) as error:
        continue_trip_messages(trip.id, request, db_session, user)
    assert error.value.status_code == 503
    result = continue_trip_messages(trip.id, request, db_session, user)
    assert result.message.content == "Which day?"
    assert provider.calls == 2
    assert len(usage) == 1
    assert db_session.query(TripMessage).filter_by(trip_id=trip.id).count() == 2


def test_groq_unavailable_chat_raises_provider_error(monkeypatch):
    monkeypatch.setattr("app.integrations.groq_client.settings.GROQ_API_KEY", "")
    with pytest.raises(AIProviderError):
        GroqClient(api_key="", use_mock=False).chat_json([{"role": "user", "content": "Hello"}])
