import asyncio
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

import pytest
from fastapi import Response
from pydantic import ValidationError

from app.api.v1.offers import get_offers_service, router, search_offers
from app.core.config import settings
from app.integrations.offers import OffersProviderError, OffersProviderQuotaExceeded
from app.schemas.offers import (
    FlightOfferSearchRequest,
    NormalizedOffer,
    OffersDemoResponse,
    OffersNoResultsResponse,
    OffersResultsResponse,
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


def _normalized_offer(**overrides):
    now = datetime.now(timezone.utc)
    offer = {
        "id": "provider-flight-1",
        "kind": "flight",
        "provider": "ApprovedTestProvider",
        "fetched_at": now,
        "expires_at": now + timedelta(minutes=10),
        "currency": "USD",
        "total_amount": Decimal("312.45"),
        "availability": "available",
        "conditions": ["1 checked bag included", "Non-refundable"],
        "handoff_url": "https://supplier.example/offers/provider-flight-1",
    }
    offer.update(overrides)
    return NormalizedOffer.model_validate(offer)


class FakeOffersProvider:
    name = "ApprovedTestProvider"
    supported_country_codes = frozenset({"KG"})

    def __init__(self, *, offers=None, error=None, delay_seconds=0):
        self.offers = offers or []
        self.error = error
        self.delay_seconds = delay_seconds
        self.calls = 0

    async def search(self, _request):
        self.calls += 1
        if self.delay_seconds:
            await asyncio.sleep(self.delay_seconds)
        if self.error:
            raise self.error
        return self.offers


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
async def test_approved_provider_results_are_normalized_and_fresh():
    provider = FakeOffersProvider(offers=[_normalized_offer()])
    service = OffersSearchService(enabled=True, provider=provider)
    http_response = Response()

    result = await search_offers(_flight_search(), http_response, service)

    assert http_response.status_code == 200
    assert isinstance(result, OffersResultsResponse)
    assert result.provider == provider.name
    assert result.offers[0].total_amount == Decimal("312.45")
    assert result.offers[0].handoff_url.host == "supplier.example"
    assert result.offers[0].fetched_at.tzinfo is not None
    assert provider.calls == 1


@pytest.mark.asyncio
async def test_provider_empty_search_has_a_distinct_no_results_state():
    provider = FakeOffersProvider()
    service = OffersSearchService(enabled=True, provider=provider)
    http_response = Response()

    result = await search_offers(_flight_search(), http_response, service)

    assert http_response.status_code == 200
    assert isinstance(result, OffersNoResultsResponse)
    assert result.provider == provider.name
    assert result.fetched_at.tzinfo is not None


@pytest.mark.asyncio
async def test_provider_timeout_is_a_structured_gateway_timeout():
    provider = FakeOffersProvider(offers=[_normalized_offer()], delay_seconds=0.02)
    service = OffersSearchService(
        enabled=True,
        provider=provider,
        provider_timeout_seconds=0.001,
    )
    http_response = Response()

    result = await search_offers(_flight_search(), http_response, service)

    assert http_response.status_code == 504
    assert result.reason == "provider_timeout"
    assert "secret" not in result.message.lower()


@pytest.mark.asyncio
async def test_provider_quota_and_provider_failures_are_sanitized():
    quota_provider = FakeOffersProvider(error=OffersProviderQuotaExceeded("private quota detail"))
    quota_response = Response()
    quota_result = await search_offers(
        _flight_search(),
        quota_response,
        OffersSearchService(enabled=True, provider=quota_provider),
    )

    assert quota_response.status_code == 429
    assert quota_result.reason == "provider_quota_exceeded"
    assert "private" not in quota_result.message

    failing_provider = FakeOffersProvider(error=OffersProviderError("provider token: secret"))
    error_response = Response()
    error_result = await search_offers(
        _flight_search(),
        error_response,
        OffersSearchService(enabled=True, provider=failing_provider),
    )

    assert error_response.status_code == 502
    assert error_result.reason == "provider_error"
    assert "secret" not in error_result.message


@pytest.mark.asyncio
async def test_unsupported_market_and_disabled_flag_do_not_call_provider():
    provider = FakeOffersProvider(offers=[_normalized_offer()])
    unsupported_response = Response()
    unsupported_result = await search_offers(
        _flight_search(destination_country_code="KZ"),
        unsupported_response,
        OffersSearchService(enabled=True, provider=provider),
    )

    assert unsupported_response.status_code == 409
    assert unsupported_result.reason == "unsupported_market"
    assert provider.calls == 0

    disabled_response = Response()
    disabled_result = await search_offers(
        _flight_search(),
        disabled_response,
        OffersSearchService(enabled=False, provider=provider),
    )

    assert disabled_response.status_code == 503
    assert disabled_result.reason == "feature_disabled"
    assert provider.calls == 0


@pytest.mark.asyncio
async def test_expired_provider_results_are_never_returned_as_current():
    now = datetime.now(timezone.utc)
    stale_offer = _normalized_offer(
        fetched_at=now - timedelta(hours=2),
        expires_at=now - timedelta(hours=1),
    )
    provider = FakeOffersProvider(offers=[stale_offer])
    http_response = Response()

    result = await search_offers(
        _flight_search(),
        http_response,
        OffersSearchService(enabled=True, provider=provider),
    )

    assert http_response.status_code == 503
    assert result.reason == "stale_result"
    assert "expired" in result.message


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
    assert all("2 nights" in offer.conditions for offer in result.offers)


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
