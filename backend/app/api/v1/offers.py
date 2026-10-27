from fastapi import APIRouter, Depends, Response

from app.core.config import settings
from app.schemas.offers import (
    OfferSearchRequest,
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
        provider_timeout_seconds=settings.OFFERS_PROVIDER_TIMEOUT_SECONDS,
    )


@router.post(
    "/search",
    status_code=200,
    response_model=OffersSearchResponse,
    responses={
        409: {"model": OffersUnavailableResponse},
        429: {"model": OffersUnavailableResponse},
        502: {"model": OffersUnavailableResponse},
        503: {"model": OffersUnavailableResponse},
        504: {"model": OffersUnavailableResponse},
    },
)
async def search_offers(
    request: OfferSearchRequest,
    response: Response,
    service: OffersSearchService = Depends(get_offers_service),
) -> OffersSearchResponse:
    try:
        result = await service.search(request)
    except OffersUnavailableError as error:
        status_by_reason = {
            "feature_disabled": 503,
            "provider_unconfigured": 503,
            "unsupported_market": 409,
            "provider_timeout": 504,
            "provider_quota_exceeded": 429,
            "provider_error": 502,
            "stale_result": 503,
        }
        message_by_reason = {
            "feature_disabled": "Flight and stay offers are not available yet.",
            "provider_unconfigured": "No approved offers provider is configured.",
            "unsupported_market": "Offers are not supported in this destination market.",
            "provider_timeout": "The offers provider did not respond in time.",
            "provider_quota_exceeded": "The offers provider has reached its request limit.",
            "provider_error": "The offers provider could not complete this search.",
            "stale_result": "The offers provider returned only expired results.",
        }
        response.status_code = status_by_reason[error.reason]
        return OffersUnavailableResponse(
            reason=error.reason,
            message=message_by_reason[error.reason],
        )
    return result
