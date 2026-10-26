from datetime import date, timedelta

import pytest
from fastapi import Response
from pydantic import ValidationError

from app.api.v1.offers import get_offers_service, router, search_offers
from app.core.config import settings
from app.schemas.offers import (
    FlightOfferSearchRequest,
    OffersDemoResponse,
    OffersUnavailableResponse,
    StayOfferSearchRequest,
)
from app.services.offers_service import OffersSearchService


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
    monkeypatch.setattr(settings, "OFFERS_DEMO_MODE", False)
    service = get_offers_service()
    http_response = Response()

    result = await search_offers(_flight_search(), http_response, service)

    assert service.enabled is False
    assert http_response.status_code == 503
    assert result == OffersUnavailableResponse(
        reason="feature_disabled",
        message="Flight and stay offers are not available yet.",
    )
    route = next(route for route in router.routes if route.path == "/offers/search")
    assert route.status_code == 200
    assert 503 in route.responses


@pytest.mark.asyncio
async def test_enabled_offers_still_require_an_approved_provider(monkeypatch):
    monkeypatch.setattr(settings, "OFFERS_ENABLED", True)
    monkeypatch.setattr(settings, "OFFERS_DEMO_MODE", False)
    service = get_offers_service()
    http_response = Response()

    result = await search_offers(_flight_search(), http_response, service)

    assert http_response.status_code == 503
    assert result.reason == "provider_unconfigured"
    assert "approved offers provider" in result.message


@pytest.mark.asyncio
async def test_development_demo_returns_clearly_non_bookable_fixture_results(monkeypatch):
    monkeypatch.setattr(settings, "APP_ENV", "development")
    monkeypatch.setattr(settings, "OFFERS_ENABLED", False)
    monkeypatch.setattr(settings, "OFFERS_DEMO_MODE", True)
    service = get_offers_service()
    http_response = Response()

    result = await search_offers(_flight_search(), http_response, service)

    assert http_response.status_code == 200
    assert isinstance(result, OffersDemoResponse)
    assert len(result.offers) == 2
    assert "not live prices" in result.message
    assert all(offer.handoff_url is None for offer in result.offers)
    assert all(offer.source == "NomadAI demo fixture" for offer in result.offers)


@pytest.mark.asyncio
async def test_development_demo_builds_stay_examples_from_requested_city_and_nights():
    request = StayOfferSearchRequest.model_validate({
        "kind": "stay",
        "destination_country_code": "KG",
        "destination_city": "Bishkek",
        "check_in": date.today() + timedelta(days=14),
        "check_out": date.today() + timedelta(days=16),
        "adults": 2,
        "rooms": 1,
    })
    service = OffersSearchService(
        enabled=False,
        demo_mode=True,
        app_environment="development",
    )

    result = await service.search(request)

    assert isinstance(result, OffersDemoResponse)
    assert [offer.example_total for offer in result.offers] == [240, 360]
    assert all("Bishkek" in offer.title for offer in result.offers)
    assert all("2 night(s)" in offer.conditions for offer in result.offers)


def test_demo_mode_cannot_run_outside_development_or_with_live_enabled():
    with pytest.raises(ValueError, match="only available in development"):
        OffersSearchService(enabled=False, demo_mode=True, app_environment="production")

    with pytest.raises(ValueError, match="cannot both be enabled"):
        OffersSearchService(enabled=True, demo_mode=True, app_environment="development")


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
