from datetime import datetime, timezone
from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.integrations.groq_client as groq_module
from app.api.v1.messages import continue_trip_messages
from app.models.base import Base
from app.models.trip import Trip
from app.models.trip_message import TripMessage
from app.models.user import User
from app.repositories.trip_message_repository import TripMessageRepository
from app.schemas.trip_message import (
    TripContinuationResponse,
    TripMessageCreateRequest,
    TripMessageResponse,
)
from app.services.ai_service import AIService
from app.services.trip_message_service import TripMessageService
from app.integrations.groq_client import GroqClient
from app.utils.prompt_builder import PromptBuilder


@pytest.fixture
def db_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(bind=engine)
    session = testing_session()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def user(db_session):
    db_user = User(email="owner@example.com", password_hash="hashed")
    db_session.add(db_user)
    db_session.commit()
    db_session.refresh(db_user)
    return db_user


@pytest.fixture
def other_user(db_session):
    db_user = User(email="other@example.com", password_hash="hashed")
    db_session.add(db_user)
    db_session.commit()
    db_session.refresh(db_user)
    return db_user


@pytest.fixture
def trip(db_session, user):
    db_trip = Trip(
        user_id=user.id,
        title="Issyk-Kul escape",
        budget="300",
        days=3,
        interests={"nature": True},
        travel_style="balanced",
        itinerary_json={"days": [{"day": 1, "location": "Bishkek"}]},
    )
    db_session.add(db_trip)
    db_session.commit()
    db_session.refresh(db_trip)
    return db_trip


def test_trip_message_create_request_strips_whitespace():
    payload = TripMessageCreateRequest(content="  add a museum  ")

    assert payload.content == "add a museum"


def test_trip_message_create_request_rejects_blank_content():
    with pytest.raises(ValidationError):
        TripMessageCreateRequest(content="   ")


def test_trip_message_response_supports_orm_serialization(trip):
    message = TripMessage(
        id=1,
        trip_id=trip.id,
        role="assistant",
        content="hello",
        created_at=datetime.now(timezone.utc),
    )

    response = TripMessageResponse.model_validate(message)

    assert response.trip_id == trip.id
    assert response.role == "assistant"


def test_trip_continuation_response_contains_message_and_updated_itinerary(trip):
    message = TripMessage(
        id=1,
        trip_id=trip.id,
        role="assistant",
        content="done",
        created_at=datetime.now(timezone.utc),
    )

    payload = TripContinuationResponse(
        message=TripMessageResponse.model_validate(message),
        updated_itinerary={"updated": True},
    )

    assert payload.message.content == "done"
    assert payload.updated_itinerary == {"updated": True}


def test_trip_message_model_cascades_with_trip(db_session, trip):
    db_session.add(TripMessage(trip_id=trip.id, role="user", content="hello"))
    db_session.commit()

    db_session.delete(trip)
    db_session.commit()

    assert db_session.query(TripMessage).count() == 0


def test_repository_create_message_persists_record(db_session, trip):
    repository = TripMessageRepository(db_session)

    message = repository.create_message(trip_id=trip.id, role="user", content="hi")

    assert message.id is not None
    assert db_session.query(TripMessage).count() == 1


def test_repository_get_trip_messages_returns_ascending_order(db_session, trip):
    repository = TripMessageRepository(db_session)
    first = TripMessage(
        trip_id=trip.id,
        role="user",
        content="first",
        created_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
    )
    second = TripMessage(
        trip_id=trip.id,
        role="assistant",
        content="second",
        created_at=datetime(2024, 1, 2, tzinfo=timezone.utc),
    )
    db_session.add_all([second, first])
    db_session.commit()

    messages = repository.get_trip_messages(trip_id=trip.id)

    assert [message.content for message in messages] == ["first", "second"]


def test_prompt_builder_system_prompt_mentions_json_contract():
    builder = PromptBuilder()

    prompt = builder.build_system_prompt()

    assert "Kyrgyzstan travel planning expert" in prompt
    assert "updated_itinerary" in prompt


def test_prompt_builder_initial_prompt_with_list_interests():
    builder = PromptBuilder()

    prompt = builder.build_initial_generation_prompt(
        budget=500,
        days=5,
        interests=["nature", "food"],
        accommodation_type="comfort",
    )

    assert "Budget: 500 USD" in prompt
    assert "Days: 5" in prompt
    assert "nature, food" in prompt
    assert "comfort" in prompt


def test_prompt_builder_initial_prompt_with_string_interests():
    builder = PromptBuilder()

    prompt = builder.build_initial_generation_prompt(
        budget=200,
        days=2,
        interests="mountains",
    )

    assert "mountains" in prompt
    assert "not specified" in prompt


def test_prompt_builder_continuation_prompt_serializes_itinerary():
    builder = PromptBuilder()

    prompt = builder.build_continuation_prompt(
        user_message="add a museum",
        current_itinerary={"days": [{"day": 1}]},
    )

    assert "add a museum" in prompt
    assert '{"days": [{"day": 1}]}' in prompt


def test_prompt_builder_build_chat_messages_replaces_duplicate_latest_user():
    builder = PromptBuilder()
    history = [
        {"role": "assistant", "content": "previous"},
        {"role": "user", "content": "add a museum"},
    ]

    messages = builder.build_chat_messages(
        history_messages=history,
        user_message="add a museum",
        current_itinerary={"days": []},
    )

    assert messages[0]["role"] == "system"
    assert [message["role"] for message in messages].count("user") == 1
    assert "Current itinerary JSON" in messages[-1]["content"]


def test_groq_client_returns_mock_without_api_key():
    client = GroqClient(api_key=None)

    payload = client.chat_json([{"role": "user", "content": "hello"}])

    assert "message" in payload
    assert "updated_itinerary" in payload


def test_groq_client_returns_mock_when_upstream_raises(monkeypatch):
    class ExplodingGroq:
        def __init__(self, api_key):
            self.chat = SimpleNamespace(
                completions=SimpleNamespace(create=self._explode)
            )

        def _explode(self, **kwargs):
            raise RuntimeError("boom")

    monkeypatch.setattr(groq_module, "Groq", ExplodingGroq)
    client = GroqClient(api_key="fake-key")

    payload = client.chat_json([{"role": "user", "content": "hello"}])

    assert payload["updated_itinerary"]["updated"] is True


def test_groq_client_parses_json_payload(monkeypatch):
    class FakeGroq:
        def __init__(self, api_key):
            self.chat = SimpleNamespace(
                completions=SimpleNamespace(create=self._create)
            )

        def _create(self, **kwargs):
            message = SimpleNamespace(
                content='{"message":"ok","updated_itinerary":{"days":[]}}'
            )
            return SimpleNamespace(choices=[SimpleNamespace(message=message)])

    monkeypatch.setattr(groq_module, "Groq", FakeGroq)
    client = GroqClient(api_key="fake-key", use_mock=False)

    payload = client.get_structured_output([{"role": "user", "content": "hello"}])

    assert payload["message"] == "ok"
    assert payload["updated_itinerary"] == {"days": []}


def test_ai_service_normalizes_dict_payload():
    service = AIService()

    message, itinerary = service._normalize_response(
        {"message": "updated", "updated_itinerary": {"days": []}}
    )

    assert message == "updated"
    assert itinerary == {"days": []}


def test_ai_service_normalizes_raw_json_string():
    service = AIService()

    message, itinerary = service._normalize_response(
        '{"message":"updated","updated_itinerary":{"days":[1]}}'
    )

    assert message == "updated"
    assert itinerary == {"days": [1]}


def test_ai_service_continue_trip_uses_prompt_builder_and_client():
    class FakePromptBuilder:
        def build_chat_messages(self, history_messages, user_message, current_itinerary):
            return [{"role": "user", "content": "payload"}]

    class FakeGroqClient:
        def chat_json(self, messages):
            assert messages == [{"role": "user", "content": "payload"}]
            return {"message": "assistant reply", "updated_itinerary": {"days": [1]}}

    service = AIService(
        groq_client=FakeGroqClient(),
        prompt_builder=FakePromptBuilder(),
    )

    message, itinerary = service.continue_trip([], "add museum", {"days": []})

    assert message == "assistant reply"
    assert itinerary == {"days": [1]}


def test_trip_message_service_saves_user_and_assistant_messages(db_session, trip):
    class FakeAIService:
        def continue_trip(self, history_messages, user_message, current_itinerary):
            return "assistant reply", {"days": [{"day": 2}]}

    service = TripMessageService(db_session, ai_service=FakeAIService())

    assistant_message, updated_itinerary = service.continue_trip(
        trip=trip,
        user_content="add a museum",
    )

    messages = db_session.query(TripMessage).order_by(TripMessage.id.asc()).all()

    assert [message.role for message in messages] == ["user", "assistant"]
    assert assistant_message.content == "assistant reply"
    assert updated_itinerary == {"days": [{"day": 2}]}


def test_trip_message_service_updates_trip_itinerary(db_session, trip):
    class FakeAIService:
        def continue_trip(self, history_messages, user_message, current_itinerary):
            return "assistant reply", {"days": [{"day": 3}]}

    service = TripMessageService(db_session, ai_service=FakeAIService())
    service.continue_trip(trip=trip, user_content="change plan")
    db_session.refresh(trip)

    assert trip.itinerary_json == {"days": [{"day": 3}]}


def test_trip_message_service_keeps_existing_itinerary_when_ai_returns_none(
    db_session, trip
):
    original_itinerary = trip.itinerary_json

    class FakeAIService:
        def continue_trip(self, history_messages, user_message, current_itinerary):
            return "assistant reply", None

    service = TripMessageService(db_session, ai_service=FakeAIService())
    service.continue_trip(trip=trip, user_content="no changes")
    db_session.refresh(trip)

    assert trip.itinerary_json == original_itinerary


def test_continue_trip_messages_function_returns_404_for_missing_trip(db_session, user):
    with pytest.raises(HTTPException) as exc_info:
        continue_trip_messages(
            trip_id=999,
            payload=TripMessageCreateRequest(content="hello"),
            db=db_session,
            current_user=user,
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Trip not found"


def test_continue_trip_messages_function_returns_404_for_non_owner(db_session, trip, other_user):
    with pytest.raises(HTTPException) as exc_info:
        continue_trip_messages(
            trip_id=trip.id,
            payload=TripMessageCreateRequest(content="hello"),
            db=db_session,
            current_user=other_user,
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Trip not found"


def test_continue_trip_messages_function_returns_assistant_message_and_updated_itinerary(
    db_session, user, trip, monkeypatch
):
    def fake_continue_trip(self, trip, user_content):
        return (
            TripMessage(
                id=123,
                trip_id=trip.id,
                role="assistant",
                content="updated plan",
                created_at=datetime.now(timezone.utc),
            ),
            {"days": [{"day": 4}]},
        )

    monkeypatch.setattr(
        TripMessageService,
        "continue_trip",
        fake_continue_trip,
    )

    response = continue_trip_messages(
        trip_id=trip.id,
        payload=TripMessageCreateRequest(content="add another museum"),
        db=db_session,
        current_user=user,
    )

    assert response.message.content == "updated plan"
    assert response.updated_itinerary == {"days": [{"day": 4}]}
