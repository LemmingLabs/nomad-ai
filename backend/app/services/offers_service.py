import asyncio
from datetime import datetime, timezone

from app.integrations.offers import (
    OffersProvider,
    OffersProviderError,
    OffersProviderQuotaExceeded,
    OffersProviderTimeout,
)
from app.schemas.offers import (
    OfferDemoItem,
    OfferSearchRequest,
    OffersDemoResponse,
    OffersNoResultsResponse,
    OffersResultsResponse,
    OffersUnavailableResponse,
)


class OffersUnavailableError(Exception):
    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(reason)


class OffersSearchService:
    """Feature-gated provider boundary; no provider is enabled until access is approved."""

    def __init__(
        self,
        *,
        enabled: bool,
        demo_mode: bool = False,
        app_environment: str = "production",
        provider: OffersProvider | None = None,
        provider_timeout_seconds: float = 8,
    ):
        if demo_mode and app_environment != "development":
            raise ValueError("Demo offers are only available in development")
        if demo_mode and enabled:
            raise ValueError("Demo mode and live offers cannot both be enabled")
        self.enabled = enabled
        self.demo_mode = demo_mode
        self.provider = provider
        self.provider_timeout_seconds = provider_timeout_seconds

    async def search(
        self,
        request: OfferSearchRequest,
    ) -> (
        OffersDemoResponse
        | OffersResultsResponse
        | OffersNoResultsResponse
        | OffersUnavailableResponse
    ):
        if self.demo_mode:
            return self._demo_response(request)
        if not self.enabled:
            raise OffersUnavailableError("feature_disabled")
        if self.provider is None:
            # The feature stays unavailable until an approved adapter is injected.
            raise OffersUnavailableError("provider_unconfigured")

        if request.destination_country_code not in self.provider.supported_country_codes:
            raise OffersUnavailableError("unsupported_market")

        try:
            offers = await asyncio.wait_for(
                self.provider.search(request),
                timeout=self.provider_timeout_seconds,
            )
        except TimeoutError as error:
            raise OffersUnavailableError("provider_timeout") from error
        except OffersProviderTimeout as error:
            raise OffersUnavailableError("provider_timeout") from error
        except OffersProviderQuotaExceeded as error:
            raise OffersUnavailableError("provider_quota_exceeded") from error
        except OffersProviderError as error:
            raise OffersUnavailableError("provider_error") from error

        fetched_at = datetime.now(timezone.utc)
        if not offers:
            return OffersNoResultsResponse(
                provider=self.provider.name,
                fetched_at=fetched_at,
            )

        if any(
            offer.provider != self.provider.name
            or offer.kind != request.kind
            or offer.fetched_at > fetched_at
            for offer in offers
        ):
            raise OffersUnavailableError("provider_error")

        fresh_offers = [offer for offer in offers if offer.expires_at > fetched_at]
        if not fresh_offers:
            raise OffersUnavailableError("stale_result")

        return OffersResultsResponse(provider=self.provider.name, offers=fresh_offers)

    @staticmethod
    def _demo_response(request: OfferSearchRequest) -> OffersDemoResponse:
        if request.kind == "flight":
            route = f"{request.origin} to {request.destination}"
            passenger_label = "passenger" if request.passengers == 1 else "passengers"
            offers = [
                OfferDemoItem(
                    id="demo-flight-1",
                    kind="flight",
                    title=f"Sample flight: {route}",
                    example_total=250 * request.passengers,
                    conditions=(
                        f"Illustrative total for {request.passengers} {passenger_label}; "
                        "no airline schedule, baggage rules, "
                        "availability, or booking link has been checked."
                    ),
                ),
                OfferDemoItem(
                    id="demo-flight-2",
                    kind="flight",
                    title=f"Alternative sample flight: {route}",
                    example_total=420 * request.passengers,
                    conditions=(
                        f"Illustrative total for {request.passengers} {passenger_label}; "
                        "no airline schedule, baggage rules, "
                        "availability, or booking link has been checked."
                    ),
                ),
            ]
        else:
            nights = (request.check_out - request.check_in).days
            room_label = "room" if request.rooms == 1 else "rooms"
            night_label = "night" if nights == 1 else "nights"
            adult_label = "adult" if request.adults == 1 else "adults"
            offers = [
                OfferDemoItem(
                    id="demo-stay-1",
                    kind="stay",
                    title=f"Sample stay in {request.destination_city}",
                    example_total=120 * nights * request.rooms,
                    conditions=(
                        f"Illustrative total for {request.rooms} {room_label} and {nights} {night_label} "
                        f"({request.adults} {adult_label}); taxes, room terms, availability, "
                        "and a booking link have not been checked."
                    ),
                ),
                OfferDemoItem(
                    id="demo-stay-2",
                    kind="stay",
                    title=f"Alternative sample stay in {request.destination_city}",
                    example_total=180 * nights * request.rooms,
                    conditions=(
                        f"Illustrative total for {request.rooms} {room_label} and {nights} {night_label} "
                        f"({request.adults} {adult_label}); taxes, room terms, availability, "
                        "and a booking link have not been checked."
                    ),
                ),
            ]
        return OffersDemoResponse(offers=offers)
