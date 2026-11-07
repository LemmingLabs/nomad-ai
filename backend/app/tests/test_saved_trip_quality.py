from copy import deepcopy

from app.api.v1.trips import get_trip
from app.models.trip import Trip
from app.models.user import User


def test_saved_trip_read_refreshes_warnings_without_writing(db_session):
    user = User(email="saved-quality@example.com", password_hash="hashed")
    db_session.add(user)
    db_session.flush()
    original = {
        "days": [{"day": 1, "title": "City", "city": "Bishkek", "location": "Square",
                  "activities": [{"description": "Visit", "type": "activity",
                                  "time_window": "09:00-10:00", "duration_minutes": 90}]}],
        "quality_warnings": [{"code": "old_warning", "message": "Outdated", "day": 1}],
    }
    trip = Trip(user_id=user.id, title="Trip", budget="medium", days=1,
                interests=["culture"], travel_style="balanced", itinerary_json=deepcopy(original))
    db_session.add(trip)
    db_session.commit()
    revision, updated_at = trip.chat_revision, trip.updated_at
    response = get_trip(trip.id, recent_messages=False, db=db_session, current_user=user)
    warnings = response.model_dump()["trip"]["itinerary_json"]["quality_warnings"]
    assert [warning["code"] for warning in warnings] == ["activity_duration_exceeds_window"]
    assert warnings[0]["day"] == 1
    db_session.commit()
    db_session.refresh(trip)
    assert trip.itinerary_json == original
    assert trip.chat_revision == revision
    assert trip.updated_at == updated_at
