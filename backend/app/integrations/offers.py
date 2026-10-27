from typing import Protocol

from app.schemas.offers import NormalizedOffer, OfferSearchRequest


class OffersProviderError(Exception):
    """Base error translated to a safe offers API response by the service layer."""


class OffersProviderTimeout(OffersProviderError):
    pass


class OffersProviderQuotaExceeded(OffersProviderError):
    pass


class OffersProvider(Protocol):
    """Contract for an approved provider adapter; credentials stay in the adapter."""

    name: str
    supported_country_codes: frozenset[str]

    async def search(self, request: OfferSearchRequest) -> list[NormalizedOffer]: ...
