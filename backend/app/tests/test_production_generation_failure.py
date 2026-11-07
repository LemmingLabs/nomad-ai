import pytest
from fastapi import HTTPException

from app.api.v1.trips import generate_trip
from app.models.trip import Trip
from app.models.trip_message import TripMessage
from app.models.user import User
from app.schemas.trip import TripGenerateRequest
from app.services import trip_service


@pytest.mark.parametrize("authenticated", [False, True])
@pytest.mark.parametrize("provider_result", ["exception", "mock"])
def test_production_ai_failure_creates_no_trip_or_usage(db_session, monkeypatch, authenticated, provider_result):
    user = User(email="generation-failure@example.com", password_hash="hashed")
    db_session.add(user)
    db_session.commit()
    monkeypatch.setattr(trip_service.settings, "APP_ENV", "production")
    monkeypatch.setattr("app.services.trip_service.LimitService.can_generate_trip", lambda *args: True)
    usage = []
    monkeypatch.setattr("app.services.trip_service.UsageService.increment_trip_generation", lambda *args: usage.append(True))

    def generate(self, **kwargs):
        if provider_result == "exception":
            raise RuntimeError("private provider response")
        return {"title": "Mock", "itinerary": {"days": [{"day": 1}]},
                "_provider_status": {"source": "mock", "reason": "provider_error"}}

    monkeypatch.setattr("app.services.ai_service.AIService.generate_initial_trip", generate)
    request = TripGenerateRequest(budget="low", days=1, interests=["nature"], travel_style="relaxed")
    with pytest.raises(HTTPException) as error:
        generate_trip(request, db=db_session, current_user=user if authenticated else None)

    assert error.value.status_code == 503
    assert "no trip was created" in error.value.detail
    assert "private provider response" not in error.value.detail
    assert db_session.query(Trip).count() == 0
    assert db_session.query(TripMessage).count() == 0
    assert usage == []
