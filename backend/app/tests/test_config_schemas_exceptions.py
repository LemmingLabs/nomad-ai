import pytest
from pydantic import ValidationError

from app.schemas.trip_schema import TransportResult, DayPlan, TripRequest
from app.exceptions import (
    TwoGISAuthError,
    TwoGISRateLimitError,
    TwoGISServerError,
    TwoGISTimeoutError,
    RoutingServiceError,
)


def test_transport_result_instantiates_correctly():
    """TransportResult instantiates correctly with all required fields."""
    res = TransportResult(
        **{"from": "A"},
        to="B",
        distance_km=10.5,
        duration_min=15.0,
        price_min=50.0,
        price_max=100.0,
        transport_type="taxi",
    )
    assert res.from_ == "A"
    assert res.to == "B"


def test_transport_result_currency_defaults():
    """TransportResult.currency defaults to 'KGS'."""
    res = TransportResult(
        **{"from": "A"},
        to="B",
        distance_km=10.5,
        duration_min=15.0,
        price_min=50.0,
        price_max=100.0,
        transport_type="taxi",
    )
    assert res.currency == "KGS"


def test_transport_result_alias_from_works():
    """TransportResult alias 'from' works."""
    res = TransportResult.model_validate({
        "from": "A",
        "to": "B",
        "distance_km": 10.5,
        "duration_min": 15.0,
        "price_min": 50.0,
        "price_max": 100.0,
        "transport_type": "taxi",
    })
    
    d = res.model_dump(by_alias=True)
    assert "from" in d
    assert d["from"] == "A"


def test_day_plan_transport_defaults_to_none():
    """DayPlan.transport defaults to None."""
    dp = DayPlan(day=1, location="Bishkek", activities=["rest"])
    assert dp.transport is None


def test_trip_request_rejects_days_bounds():
    """TripRequest rejects days=0 and days=15 with ValidationError."""
    with pytest.raises(ValidationError):
        TripRequest(budget=100.0, days=0, interests=["hiking"])
        
    with pytest.raises(ValidationError):
        TripRequest(budget=100.0, days=15, interests=["hiking"])


def test_trip_request_accommodation_type_defaults():
    """TripRequest.accommodation_type defaults to 'budget'."""
    tr = TripRequest(budget=100.0, days=5, interests=["hiking"])
    assert tr.accommodation_type == "budget"


def test_each_exception_class_is_subclass_of_exception():
    """Each exception class is a subclass of Exception."""
    exceptions = [
        TwoGISAuthError,
        TwoGISRateLimitError,
        TwoGISServerError,
        TwoGISTimeoutError,
        RoutingServiceError,
    ]
    for exc in exceptions:
        assert issubclass(exc, Exception)


def test_routing_service_error_raised_and_caught():
    """RoutingServiceError can be raised and caught as Exception."""
    try:
        raise RoutingServiceError("test message")
    except Exception as e:
        assert isinstance(e, RoutingServiceError)
        assert str(e) == "test message"


def test_settings_loads_google_maps_api_key(monkeypatch):
    """Settings loads the active maps provider key from the environment."""
    monkeypatch.setenv("GOOGLE_MAPS_API_KEY", "test_mock_api_key")

    from app.core.config import Settings
    s = Settings()
    assert s.GOOGLE_MAPS_API_KEY == "test_mock_api_key"


def test_google_maps_base_urls_match():
    """The active provider points at Google's Places and Routes APIs."""
    from app.integrations.google_maps_client import PLACES_BASE_URL, ROUTES_BASE_URL

    assert PLACES_BASE_URL == "https://places.googleapis.com/v1"
    assert ROUTES_BASE_URL == "https://routes.googleapis.com"
