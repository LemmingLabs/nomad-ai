from app.schemas.offers import OfferSearchRequest


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
    ):
        self.enabled = enabled

    async def search(self, request: OfferSearchRequest) -> None:
        if not self.enabled:
            raise OffersUnavailableError("feature_disabled")
        # The feature must stay unavailable until a provider and its terms are approved.
        raise OffersUnavailableError("provider_unconfigured")
