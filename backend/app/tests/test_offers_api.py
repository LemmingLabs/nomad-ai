from datetime import date, timedelta

import pytest
from pydantic import ValidationError

from app.api.v1.offers import get_offers_service, router, search_offers
from app.core.config import settings
from app.schemas.offers import (
    FlightOfferSearchRequest,
    OffersUnavailableResponse,
    StayOfferSearchRequest,
)


def _flight_search(**overrides):
    request = {
        "kind": "flight",
        "destination_country_code": "KG",
        "origin": "ALA",
        "destination": "FRU",
        "departure_date": date.today() + timedelta(days=14),
        "return_date": date.today() + timedelta(days=20),
        "passengers": 2,
    }
    request.update(overrides)
    return FlightOfferSearchRequest.model_validate(request)


@pytest.mark.asyncio
async def test_offers_search_is_explicitly_unavailable_when_feature_is_disabled(monkeypatch):
    monkeypatch.setattr(settings, "OFFERS_ENABLED", False)
    service = get_offers_service()

    response = await search_offers(_flight_search(), service)

    assert service.enabled is False
    assert response == OffersUnavailableResponse(
        reason="feature_disabled",
        message="Flight and stay offers are not available yet.",
    )
    assert next(route for route in router.routes if route.path == "/offers/search").status_code == 503


@pytest.mark.asyncio
async def test_enabled_offers_still_require_an_approved_provider(monkeypatch):
    monkeypatch.setattr(settings, "OFFERS_ENABLED", True)
    service = get_offers_service()

    response = await search_offers(_flight_search(), service)

    assert response.reason == "provider_unconfigured"
    assert "approved offers provider" in response.message


def test_offers_search_validates_inputs_before_provider_boundary():
    with pytest.raises(ValidationError):
        _flight_search(passengers=10)

    with pytest.raises(ValidationError):
        _flight_search(return_date=date.today() + timedelta(days=7))


def test_flight_search_normalizes_location_and_country_inputs():
    request = _flight_search(
        destination_country_code=" kg ",
        origin="  Almaty  ",
        destination="  Bishkek ",
    )

    assert request.destination_country_code == "KG"
    assert request.origin == "Almaty"
    assert request.destination == "Bishkek"


def test_offer_search_rejects_blank_locations_and_invalid_stay_dates():
    with pytest.raises(ValidationError):
        _flight_search(origin="   ")

    stay_search = {
        "kind": "stay",
        "destination_country_code": "KG",
        "destination_city": "Bishkek",
        "check_in": date.today() + timedelta(days=14),
        "check_out": date.today() + timedelta(days=13),
        "adults": 2,
        "rooms": 1,
    }
    with pytest.raises(ValidationError):
        StayOfferSearchRequest.model_validate(stay_search)

    stay_search["destination_city"] = "   "
    stay_search["check_out"] = date.today() + timedelta(days=15)
    with pytest.raises(ValidationError):
        StayOfferSearchRequest.model_validate(stay_search)
