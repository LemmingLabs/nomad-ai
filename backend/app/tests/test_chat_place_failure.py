from app.models.trip import Trip
from app.models.trip_message import TripMessage
from app.models.user import User
from app.services.trip_message_service import TripMessageService


def test_place_failure_saves_edit_as_degraded_without_partial_provider_data(db_session, monkeypatch, caplog):
    user = User(email="place-failure@example.com", password_hash="hashed")
    db_session.add(user)
    db_session.flush()
    trip = Trip(
        user_id=user.id, title="Trip", budget="medium", days=1,
        interests=["nature"], travel_style="balanced",
        itinerary_json={"days": [{"day": 1, "city": "Bishkek", "location": "Old place",
                                  "place_candidate": {"place_id": "old"}, "activities": []}]},
    )
    db_session.add(trip)
    db_session.commit()

    class FakeAI:
        def continue_trip(self, **kwargs):
            return "Updated", {"days": [{"day": 1, "city": "Bishkek", "location": "New place", "activities": []}]}

    def fail_after_mutation(itinerary, **kwargs):
        itinerary["days"][0]["place_candidate"] = {"place_id": "partial"}
        raise RuntimeError("sensitive provider detail")

    async def routes(self, itinerary):
        return itinerary

    monkeypatch.setattr("app.services.trip_message_service.LimitService.can_edit_chat", lambda *args: True)
    monkeypatch.setattr("app.services.trip_message_service.UsageService.increment_chat_edit", lambda *args: None)
    monkeypatch.setattr("app.services.trip_service.enrich_selected_days_with_place_candidates", fail_after_mutation)
    monkeypatch.setattr("app.services.catalog_service.CatalogService.enrich_itinerary_with_catalog", lambda self, itinerary, *args, **kwargs: itinerary)
    monkeypatch.setattr("app.services.routing_service.RoutingService.enrich_from_itinerary_json", routes)
    monkeypatch.setattr("app.services.image_enrichment_service.ImageEnrichmentService.enrich_trip_with_images", lambda self, itinerary, **kwargs: itinerary)
    monkeypatch.setattr("app.services.sponsored_injection_service.SponsoredInjectionService.inject_sponsored_places", lambda self, itinerary, **kwargs: itinerary)

    message, updated = TripMessageService(db_session, ai_service=FakeAI()).continue_trip(trip, "Change the place")
    db_session.refresh(trip)

    assert message.content == "Updated"
    assert updated == trip.itinerary_json
    assert updated["days"][0]["location"] == "New place"
    assert "place_candidate" not in updated["days"][0]
    assert updated["generation_status"]["state"] == "degraded"
    assert "place_refresh_unavailable" in updated["generation_status"]["reasons"]
    assert db_session.query(TripMessage).filter_by(trip_id=trip.id).count() == 2
    assert "sensitive provider detail" not in caplog.text
