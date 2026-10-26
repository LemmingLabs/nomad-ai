from fastapi import APIRouter, Depends, Response

from app.core.config import settings
from app.schemas.offers import (
    OfferSearchRequest,
    OffersDemoResponse,
    OffersSearchResponse,
    OffersUnavailableResponse,
)
from app.services.offers_service import OffersSearchService, OffersUnavailableError


router = APIRouter(prefix="/offers", tags=["offers"])


def get_offers_service() -> OffersSearchService:
    return OffersSearchService(
        enabled=settings.OFFERS_ENABLED,
        demo_mode=settings.OFFERS_DEMO_MODE,
        app_environment=settings.APP_ENV,
    )


@router.post(
    "/search",
    status_code=200,
    response_model=OffersSearchResponse,
    responses={503: {"model": OffersUnavailableResponse}},
)
async def search_offers(
    request: OfferSearchRequest,
    response: Response,
    service: OffersSearchService = Depends(get_offers_service),
) -> OffersSearchResponse:
    try:
        result = await service.search(request)
    except OffersUnavailableError as error:
        response.status_code = 503
        message = (
            "Flight and stay offers are not available yet."
            if error.reason == "feature_disabled"
            else "No approved offers provider is configured."
        )
        return OffersUnavailableResponse(reason=error.reason, message=message)
    if isinstance(result, OffersDemoResponse):
        return result
    response.status_code = 503
    return result
