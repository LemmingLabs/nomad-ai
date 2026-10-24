from fastapi.testclient import TestClient
import pytest

from app.core.database import get_db
from app.core.dependencies import get_current_user_optional
from app.main import app
from app.repositories.trip_repository import create_trip
from app.services import trip_service


@pytest.fixture
def client(db_session):
    def test_db():
        yield db_session

    app.dependency_overrides[get_db] = test_db
    app.dependency_overrides[get_current_user_optional] = lambda: None

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()


def test_health_endpoint_is_available_without_authentication(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_guest_generation_returns_persisted_trip_on_versioned_route(client, db_session, monkeypatch):
    observed = {}

    def save_trip(**kwargs):
        observed.update(kwargs)
        return create_trip(
            db_session,
            user_id=kwargs["user_id"],
            title="Bishkek Weekend",
            budget=kwargs["budget"],
            days=kwargs["days"],
            interests=kwargs["interests"],
            travel_style=kwargs["travel_style"],
            country_code=kwargs["country_code"],
            destination_id=kwargs["destination_id"],
            destination_name=kwargs["destination_name"],
            itinerary_json={"summary": "A weekend in Bishkek", "days": []},
        )

    monkeypatch.setattr(trip_service, "generate_trip", save_trip)

    response = client.post("/api/v1/trips/generate", json={
        "budget": "medium",
        "days": 2,
        "interests": ["culture"],
        "travel_style": "relaxed",
        "prompt": "Visit Bishkek",
    })

    assert response.status_code == 201
    assert response.json()["title"] == "Bishkek Weekend"
    assert response.json()["id"] > 0
    assert observed["user_id"] is None
    assert observed["prompt"] == "Visit Bishkek"
    assert observed["country_code"] == "KG"
    assert observed["destination_id"] == "kg"
    assert response.json()["destination_name"] == "Kyrgyzstan"


def test_generation_rejects_unsupported_destination_before_service_call(client, monkeypatch):
    def unexpected_generation(**kwargs):
        pytest.fail("trip service should not be called for an unsupported destination")

    monkeypatch.setattr(trip_service, "generate_trip", unexpected_generation)
    response = client.post("/api/v1/trips/generate", json={
        "budget": "medium",
        "days": 2,
        "interests": ["culture"],
        "travel_style": "relaxed",
        "country_code": "FR",
        "destination_id": "fr",
    })

    assert response.status_code == 422


def test_generation_maps_service_validation_to_bad_request(client, monkeypatch):
    def reject_trip(**kwargs):
        raise ValueError("Days must be at least 1")

    monkeypatch.setattr(trip_service, "generate_trip", reject_trip)

    response = client.post("/api/v1/trips/generate", json={
        "budget": "medium",
        "days": 0,
        "interests": [],
        "travel_style": "relaxed",
    })

    assert response.status_code == 400
    assert response.json()["detail"] == "Days must be at least 1"


def test_saved_trip_list_requires_authentication(client):
    response = client.get("/api/v1/trips")

    assert response.status_code == 401
