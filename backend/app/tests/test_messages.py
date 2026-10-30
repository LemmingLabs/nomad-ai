from datetime import datetime, timezone
from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

import app.integrations.groq_client as groq_module
from app.api.v1.messages import continue_trip_messages
from app.models.business import Business
from app.models.sponsored_place import SponsoredPlace
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


@pytest.fixture(autouse=True)
def _allow_trip_chat_limits(monkeypatch):
    monkeypatch.setattr(
        "app.services.trip_message_service.LimitService.can_edit_chat",
        lambda self, user_id: True,
    )
    monkeypatch.setattr(
        "app.services.trip_message_service.UsageService.increment_chat_edit",
        lambda self, user_id: None,
    )


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

    messages, _ = repository.get_trip_messages(trip_id=trip.id)

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


def test_prompt_builder_initial_prompt_stays_with_selected_destination():
    prompt = PromptBuilder().build_initial_generation_prompt(
        days=2,
        interests=["nature"],
        travel_style="relaxed",
        budget="medium",
        country_name="Kyrgyzstan",
        destination_name="Kyrgyzstan",
        supported_cities=("Bishkek", "Osh"),
    )

    assert "Selected country: Kyrgyzstan" in prompt
    assert "Do not substitute a different country or destination" in prompt
    assert "Bishkek, Osh" in prompt


def test_prompt_builder_continuation_prompt_serializes_itinerary():
    builder = PromptBuilder()

    prompt = builder.build_continuation_prompt(
        user_message="add a museum",
        current_itinerary={"days": [{"day": 1}]},
    )

    assert "add a museum" in prompt
    assert '{"days": [{"day": 1}]}' in prompt


def test_prompt_builder_continuation_keeps_saved_destination_context():
    prompt = PromptBuilder().build_continuation_prompt(
        "add a museum",
        {"days": []},
        country_code="KG",
        country_name="Kyrgyzstan",
        destination_name="Kyrgyzstan",
        supported_cities=("Bishkek", "Osh"),
    )

    assert "Selected trip destination: Kyrgyzstan, Kyrgyzstan (KG)" in prompt
    assert "Do not switch destination implicitly" in prompt
    assert "Bishkek, Osh" in prompt


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


def test_groq_initial_mock_response_is_explicitly_marked():
    client = GroqClient(api_key=None)

    payload = client.chat_json([{"role": "user", "content": "- Days: 1"}], mode="initial")

    assert payload["_provider_status"]["source"] == "mock"
    assert payload["_provider_status"]["reason"] in {
        "provider_unconfigured",
        "provider_unavailable",
    }


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


def test_chat_refresh_keeps_old_route_marked_stale_when_new_route_is_unavailable():
    old_itinerary = {
        "days": [
            {"day": 1},
            {
                "day": 2,
                "route_from_previous": {
                    "origin": "Bishkek",
                    "destination": "Karakol",
                    "distance_km": 400,
                    "duration_mins": 360,
                    "transport_type": "driving",
                    "status": "available",
                },
            },
        ]
    }
    updated_itinerary = {
        "days": [
            {"day": 1},
            {"day": 2, "route_from_previous": {"status": "unavailable"}},
        ]
    }

    has_unavailable_route = TripMessageService._preserve_stale_routes(
        updated_itinerary, old_itinerary, {1}
    )

    assert has_unavailable_route is True
    assert updated_itinerary["days"][1]["route_from_previous"]["status"] == "stale"
    assert updated_itinerary["route_status"] == "unavailable"


def test_chat_merge_preserves_optional_details_and_route_for_unchanged_location(db_session):
    service = TripMessageService(db_session)
    current = {
        "days": [{
            "day": 1,
            "city": "Bishkek",
            "location": "Ala-Too Square",
            "routing_location": "Ala-Too Square, Bishkek",
            "title": "City day",
            "activities": [{
                "time": "Morning",
                "time_window": "09:00-11:00",
                "duration_minutes": 120,
                "duration_status": "estimated",
                "practical_details": ["Allow time for security"],
                "description": "Walk around the square",
                "type": "sightseeing",
            }],
            "images": {"hero": {"url": "/media/square.jpg"}},
        }],
    }
    generated = {
        "days": [{
            "day": 1,
            "city": "Bishkek",
            "location": "Ala-Too Square",
            "routing_location": "Ala-Too Square, Bishkek",
            "title": "City day",
            "activities": [{
                "time": "Morning",
                "description": "Walk around the square",
                "type": "sightseeing",
            }],
        }],
    }

    merged = service._merge_itinerary(current, generated)

    assert merged["days"][0]["activities"][0]["duration_minutes"] == 120
    assert merged["days"][0]["activities"][0]["practical_details"] == [
        "Allow time for security"
    ]
    assert merged["days"][0]["images"]["hero"]["url"] == "/media/square.jpg"
    assert service._detect_location_changed_days(current, merged) == set()


def test_ai_service_continue_trip_uses_prompt_builder_and_client():
    class FakePromptBuilder:
        def build_chat_messages(self, **kwargs):
            assert kwargs["country_code"] == "KG"
            assert kwargs["destination_name"] == "Kyrgyzstan"
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
        def continue_trip(self, history_messages, user_message, current_itinerary, **kwargs):
            assert kwargs["country_code"] == trip.country_code
            assert kwargs["destination_id"] == trip.destination_id
            return "assistant reply", {"days": [{"day": 2}]}

    service = TripMessageService(db_session, ai_service=FakeAIService())

    assistant_message, updated_itinerary = service.continue_trip(
        trip=trip,
        user_content="add a museum",
    )

    messages = db_session.query(TripMessage).order_by(TripMessage.id.asc()).all()

    assert [message.role for message in messages] == ["user", "assistant"]
    assert assistant_message.content == "assistant reply"
    assert updated_itinerary is not None
    assert updated_itinerary["days"][0]["day"] == 2


def test_trip_message_service_updates_trip_itinerary(db_session, trip):
    class FakeAIService:
        def continue_trip(self, history_messages, user_message, current_itinerary, **kwargs):
            return "assistant reply", {"days": [{"day": 3}]}

    service = TripMessageService(db_session, ai_service=FakeAIService())
    service.continue_trip(trip=trip, user_content="change plan")
    db_session.refresh(trip)

    assert trip.itinerary_json["days"][0]["day"] == 3


def test_trip_message_service_keeps_existing_itinerary_when_ai_returns_none(
    db_session, trip
):
    original_itinerary = trip.itinerary_json

    class FakeAIService:
        def continue_trip(self, history_messages, user_message, current_itinerary, **kwargs):
            return "assistant reply", None

    service = TripMessageService(db_session, ai_service=FakeAIService())
    service.continue_trip(trip=trip, user_content="no changes")
    db_session.refresh(trip)

    assert trip.itinerary_json == original_itinerary


def test_trip_message_service_does_not_apply_provider_mock_update(db_session, trip):
    original_itinerary = trip.itinerary_json.copy()

    class FakeAIService:
        def continue_trip(self, history_messages, user_message, current_itinerary, **kwargs):
            return "Mock response: provider unavailable", {
                "days": [{"day": 1, "title": "fabricated update"}],
            }

    service = TripMessageService(db_session, ai_service=FakeAIService())
    assistant_message, updated_itinerary = service.continue_trip(
        trip=trip,
        user_content="change day one",
    )
    db_session.refresh(trip)

    assert updated_itinerary is None
    assert trip.itinerary_json == original_itinerary
    assert "saved itinerary is unchanged" in assistant_message.content


def test_trip_message_service_reinjects_sponsored_after_image_enrichment(
    db_session, user, monkeypatch
):
    trip = Trip(
        user_id=user.id,
        title="Food day",
        budget="300",
        days=1,
        interests={"food": True},
        travel_style="balanced",
        itinerary_json={
            "days": [
                {
                    "day": 1,
                    "city": "Bishkek",
                    "location": "Bishkek center",
                    "title": "Lunch stop",
                    "activities": [{"type": "meal", "description": "Lunch"}],
                    "images": {"hero": {"url": "/media/existing.jpg"}},
                }
            ]
        },
    )
    db_session.add(trip)
    db_session.flush()

    business = Business(
        owner_id=user.id,
        name="Cantin",
        description="Modern city canteen",
        contact_phone="+996555000111",
        website_url="https://cantin.example.com",
    )
    db_session.add(business)
    db_session.flush()

    place = SponsoredPlace(
        business_id=business.id,
        title="Cantin",
        description="Modern stylish canteen in the city center",
        city="bishkek",
        lat=42.8746,
        lng=74.5698,
        google_place_id=None,
        address="Bishkek center",
        category="modern canteen / cafe",
        cta_text="Book a table",
        contact_phone="+996555000111",
        website_url="https://cantin.example.com",
        is_approved=True,
        is_active=True,
    )
    db_session.add(place)
    db_session.commit()
    db_session.refresh(trip)

    class FakeAIService:
        def continue_trip(self, history_messages, user_message, current_itinerary, **kwargs):
            return "assistant reply", {
                "days": [
                    {
                        "day": 1,
                        "city": "Bishkek",
                        "location": "Bishkek center",
                        "title": "Lunch stop",
                        "activities": [{"type": "meal", "description": "Lunch"}],
                    }
                ]
            }

    class FakeCatalogService:
        def __init__(self, db):
            self.db = db

        def enrich_itinerary_with_catalog(self, itinerary, budget, **kwargs):
            return itinerary

    monkeypatch.setattr("app.services.trip_message_service.CatalogService", FakeCatalogService)

    service = TripMessageService(db_session, ai_service=FakeAIService())
    _, updated_itinerary = service.continue_trip(trip=trip, user_content="keep lunch")
    db_session.refresh(trip)

    sponsored = updated_itinerary["days"][0].get("sponsored")
    assert sponsored is not None
    assert sponsored["is_sponsored"] is True
    assert sponsored["badge"] == "Partner Pick"
    assert trip.itinerary_json["days"][0]["sponsored"]["place"]["id"] == place.id


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


@pytest.mark.parametrize("count", [0, 12, 75, 125])
def test_recent_history_cursor_is_stable_across_equal_timestamps_and_new_messages(db_session, trip, count):
    timestamp = datetime(2024, 1, 1, tzinfo=timezone.utc)
    db_session.add_all([
        TripMessage(trip_id=trip.id, role="user", content=str(index), created_at=timestamp)
        for index in range(count)
    ])
    db_session.commit()
    repo = TripMessageRepository(db_session)
    first, total, more = repo.get_recent_messages(trip.id, limit=50)
    assert total == count
    assert [int(message.content) for message in first] == list(range(max(0, count - 50), count))
    assert more == (count > 50)
    if more:
        db_session.add(TripMessage(trip_id=trip.id, role="user", content="new", created_at=timestamp))
        db_session.commit()
        older, _, older_more = repo.get_recent_messages(trip.id, limit=50, before_id=first[0].id)
        assert [int(message.content) for message in older] == list(range(max(0, count - 100), count - 50))
        assert not set(m.id for m in older) & set(m.id for m in first)
        assert older_more == (count > 100)
        if older_more:
            oldest, _, last_more = repo.get_recent_messages(trip.id, limit=50, before_id=older[0].id)
            assert [int(message.content) for message in oldest] == list(range(count - 100))
            assert not last_more


def test_recent_history_rejects_cursor_from_other_trip(db_session, trip, user):
    other = Trip(user_id=user.id, title="Other", budget="300", days=1, interests=[], travel_style="balanced", itinerary_json={})
    db_session.add(other)
    db_session.flush()
    foreign = TripMessage(trip_id=other.id, role="user", content="foreign")
    db_session.add(foreign)
    db_session.commit()
    with pytest.raises(ValueError, match="cursor not found"):
        TripMessageRepository(db_session).get_recent_messages(trip.id, before_id=foreign.id)


def test_recent_history_requires_trip_ownership(db_session, trip, other_user):
    from app.api.v1.messages import get_trip_messages

    with pytest.raises(HTTPException) as error:
        get_trip_messages(trip.id, limit=50, offset=0, recent=True, before_id=None,
                          db=db_session, current_user=other_user)
    assert error.value.status_code == 404


def test_trip_detail_retains_legacy_page_and_can_load_recent_page(db_session, trip, user):
    from app.services.trip_service import get_trip_detail

    timestamp = datetime(2024, 1, 1, tzinfo=timezone.utc)
    db_session.add_all([
        TripMessage(trip_id=trip.id, role="user", content=str(index), created_at=timestamp)
        for index in range(55)
    ])
    db_session.commit()
    legacy = get_trip_detail(db_session, user.id, trip.id)["messages"]
    recent = get_trip_detail(db_session, user.id, trip.id, recent_messages=True)["messages"]
    assert [int(message.content) for message in legacy["items"]] == list(range(50))
    assert [int(message.content) for message in recent["items"]] == list(range(5, 55))
    assert recent["has_more"] is True
