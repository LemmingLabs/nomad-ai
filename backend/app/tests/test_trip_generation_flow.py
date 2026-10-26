from copy import deepcopy

import pytest
from fastapi import HTTPException

from app.models.trip import Trip
from app.models.trip_message import TripMessage
from app.models.user import User
from app.services import trip_service


@pytest.fixture
def offline_enrichment(monkeypatch):
    """Use real persistence while replacing only external provider boundaries."""
    monkeypatch.setattr(
        trip_service,
        "enrich_itinerary_with_place_candidates",
        lambda itinerary, *_, **kwargs: itinerary,
    )
    monkeypatch.setattr(
        "app.services.catalog_service.CatalogService.enrich_itinerary_with_catalog",
        lambda self, itinerary, budget, **kwargs: itinerary,
    )

    async def leave_routes_unchanged(self, itinerary):
        return itinerary

    monkeypatch.setattr(
        "app.services.routing_service.RoutingService.enrich_from_itinerary_json",
        leave_routes_unchanged,
    )
    monkeypatch.setattr(
        "app.services.image_enrichment_service.ImageEnrichmentService.enrich_trip_with_images",
        lambda self, itinerary, **kwargs: itinerary,
    )
    monkeypatch.setattr(
        "app.services.sponsored_injection_service.SponsoredInjectionService.inject_sponsored_places",
        lambda self, itinerary, trip_id=None, country_code="KG": itinerary,
    )


def test_guest_trip_generation_persists_itinerary_and_initial_chat(
    db_session, monkeypatch, offline_enrichment
):
    provider_context = {}
    ai_itinerary = {
        "summary": "A practical two day route through Bishkek's cultural highlights.",
        "days": [
            {"day": 1, "title": "Arrival", "city": "Bishkek", "location": "Ala-Too Square", "activities": []},
            {"day": 2, "title": "Market", "city": "Bishkek", "location": "Osh Bazaar", "activities": []},
        ],
    }

    def generate_with_context(self, **kwargs):
        provider_context.update(kwargs)
        return {
            "title": "Bishkek Weekend",
            "itinerary": deepcopy(ai_itinerary),
            "message": "Your Bishkek itinerary is ready.",
        }

    monkeypatch.setattr(
        "app.services.ai_service.AIService.generate_initial_trip",
        generate_with_context,
    )

    trip = trip_service.generate_trip(
        db=db_session,
        user_id=None,
        budget=" Medium ",
        days=2,
        interests=[" culture ", "food"],
        travel_style=" Relaxed ",
        prompt="Show me Bishkek",
    )

    assert trip.id is not None
    assert trip.budget == "medium"
    assert trip.travel_style == "relaxed"
    assert trip.country_code == "KG"
    assert trip.destination_id == "kg"
    assert trip.destination_name == "Kyrgyzstan"
    assert provider_context["country_code"] == "KG"
    assert provider_context["destination_id"] == "kg"
    assert trip.interests == ["culture", "food"]
    assert [day["location"] for day in trip.itinerary_json["days"]] == ["Ala-Too Square", "Osh Bazaar"]
    assert db_session.query(Trip).count() == 1
    messages = db_session.query(TripMessage).order_by(TripMessage.id).all()
    assert [(message.role, message.content) for message in messages] == [
        ("user", "Show me Bishkek"),
        ("assistant", "Your Bishkek itinerary is ready."),
    ]


def test_ai_failure_falls_back_to_a_saved_draft(db_session, monkeypatch, offline_enrichment):
    def provider_error(self, **kwargs):
        raise RuntimeError("AI provider unavailable")

    monkeypatch.setattr(
        "app.services.ai_service.AIService.generate_initial_trip", provider_error
    )

    trip = trip_service.generate_trip(
        db=db_session,
        user_id=None,
        budget="low",
        days=1,
        interests=["nature"],
        travel_style="relaxed",
    )

    assert len(trip.itinerary_json["days"]) == 1
    assert trip.itinerary_json["days"][0]["city"] == "Bishkek"
    assert trip.itinerary_json["generation_status"]["state"] == "degraded"
    assert trip.itinerary_json["generation_status"]["source"] == "mock"
    assert "ai_generation_failed" in trip.itinerary_json["generation_status"]["reasons"]
    assert trip.itinerary_json["days"][0]["activities"][0]["duration_status"] == "unknown"
    assert db_session.query(TripMessage).count() == 2


def test_itinerary_normalization_does_not_invent_replacement_locations():
    itinerary = {
        "summary": "A scenic trip",
        "days": [{"day": 1, "city": "Bishkek", "location": "city center"}],
    }

    normalized, title = trip_service.normalize_generated_itinerary(
        itinerary, None, 1, "relaxed"
    )

    assert normalized["days"][0]["location"] == "city center"
    assert title == "1-Day Relaxed Trip in Kyrgyzstan"


def test_generation_rejects_invalid_constraints_before_provider_call(db_session, monkeypatch):
    def unexpected_provider_call(self, **kwargs):
        pytest.fail("AI provider should not be called for invalid input")

    monkeypatch.setattr(
        "app.services.ai_service.AIService.generate_initial_trip", unexpected_provider_call
    )

    with pytest.raises(ValueError, match="Days must be at least 1"):
        trip_service.generate_trip(db_session, None, "low", 0, [], "relaxed")
    with pytest.raises(ValueError, match="Budget cannot be empty"):
        trip_service.generate_trip(db_session, None, " ", 1, [], "relaxed")


def test_guest_sync_assigns_only_unowned_trip(db_session):
    owner = User(email="traveler@example.com", password_hash="hashed")
    stranger = User(email="other@example.com", password_hash="hashed")
    db_session.add_all([owner, stranger])
    db_session.flush()
    guest_trip = Trip(
        user_id=None,
        title="Guest trip",
        budget="low",
        days=1,
        interests=[],
        travel_style="relaxed",
        country_code="KG",
        destination_id="kg",
        destination_name="Kyrgyzstan",
        itinerary_json={"days": []},
    )
    db_session.add(guest_trip)
    db_session.commit()

    synced = trip_service.sync_guest_trip_to_user(db_session, guest_trip.id, owner.id)

    assert synced.user_id == owner.id
    assert synced.country_code == "KG"
    assert synced.destination_id == "kg"
    assert synced.destination_name == "Kyrgyzstan"
    assert trip_service.sync_guest_trip_to_user(db_session, guest_trip.id, owner.id).id == guest_trip.id
    with pytest.raises(ValueError, match="Trip not found"):
        trip_service.sync_guest_trip_to_user(db_session, guest_trip.id, stranger.id)


def test_authenticated_generation_respects_daily_limit(db_session):
    user = User(email="limited@example.com", password_hash="hashed")
    db_session.add(user)
    db_session.commit()

    with pytest.raises(HTTPException) as error:
        trip_service.generate_trip(db_session, user.id, "low", 1, [], "relaxed")

    assert error.value.status_code == 403
    assert db_session.query(Trip).count() == 0
