from fastapi import APIRouter, Depends

from app.core.config import settings
from app.schemas.offers import OfferSearchRequest, OffersUnavailableResponse
from app.services.offers_service import OffersSearchService, OffersUnavailableError


router = APIRouter(prefix="/offers", tags=["offers"])


def get_offers_service() -> OffersSearchService:
    return OffersSearchService(enabled=settings.OFFERS_ENABLED)


@router.post(
    "/search",
    status_code=503,
    response_model=OffersUnavailableResponse,
)
async def search_offers(
    request: OfferSearchRequest,
    service: OffersSearchService = Depends(get_offers_service),
) -> OffersUnavailableResponse:
    try:
        await service.search(request)
    except OffersUnavailableError as error:
        message = (
            "Flight and stay offers are not available yet."
            if error.reason == "feature_disabled"
            else "No approved offers provider is configured."
        )
        return OffersUnavailableResponse(reason=error.reason, message=message)
    return OffersUnavailableResponse(
        reason="provider_unconfigured",
        message="No approved offers provider is configured.",
    )
