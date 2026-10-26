from datetime import date, timedelta

import pytest
from pydantic import ValidationError

from app.api.v1.offers import get_offers_service, router, search_offers
from app.core.config import settings
from app.schemas.offers import FlightOfferSearchRequest, OffersUnavailableResponse


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
