from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_admin
from app.models.user import User
from app.schemas.business import BusinessResponse
from app.schemas.sponsored_analytics import BusinessAnalyticsOverviewResponse, SponsoredPlaceAnalyticsResponse
from app.schemas.sponsored_place import SponsoredPlaceResponse
from app.services.admin_moderation_service import AdminModerationService
from app.services.sponsored_reporting_service import SponsoredReportingService


router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/businesses", response_model=list[BusinessResponse])
def list_businesses(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> list[BusinessResponse]:
    businesses = AdminModerationService(db).list_businesses(limit=limit, offset=offset)
    return [BusinessResponse.model_validate(business) for business in businesses]


@router.get("/businesses/{business_id}", response_model=BusinessResponse)
def get_business(
    business_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> BusinessResponse:
    business = AdminModerationService(db).get_business(business_id)
    return BusinessResponse.model_validate(business)


@router.get("/sponsored-places", response_model=list[SponsoredPlaceResponse])
def list_sponsored_places(
    pending: bool | None = None,
    approved: bool | None = None,
    active: bool | None = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> list[SponsoredPlaceResponse]:
    is_approved = approved
    if pending is True:
        is_approved = False
    places = AdminModerationService(db).list_sponsored_places(
        is_approved=is_approved,
        is_active=active,
        limit=limit,
        offset=offset,
    )
    return [SponsoredPlaceResponse.model_validate(place) for place in places]


@router.get("/sponsored-places/{place_id}", response_model=SponsoredPlaceResponse)
def get_sponsored_place(
    place_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> SponsoredPlaceResponse:
    place = AdminModerationService(db).get_sponsored_place(place_id)
    return SponsoredPlaceResponse.model_validate(place)


@router.patch("/sponsored-places/{place_id}/approve", response_model=SponsoredPlaceResponse)
def approve_sponsored_place(
    place_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> SponsoredPlaceResponse:
    place = AdminModerationService(db).approve_place(place_id)
    return SponsoredPlaceResponse.model_validate(place)


@router.patch("/sponsored-places/{place_id}/reject", response_model=SponsoredPlaceResponse)
def reject_sponsored_place(
    place_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> SponsoredPlaceResponse:
    place = AdminModerationService(db).reject_place(place_id)
    return SponsoredPlaceResponse.model_validate(place)


@router.patch("/sponsored-places/{place_id}/activate", response_model=SponsoredPlaceResponse)
def activate_sponsored_place(
    place_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> SponsoredPlaceResponse:
    place = AdminModerationService(db).activate_place(place_id)
    return SponsoredPlaceResponse.model_validate(place)


@router.patch("/sponsored-places/{place_id}/deactivate", response_model=SponsoredPlaceResponse)
def deactivate_sponsored_place(
    place_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> SponsoredPlaceResponse:
    place = AdminModerationService(db).deactivate_place(place_id)
    return SponsoredPlaceResponse.model_validate(place)


@router.get("/analytics/businesses/{business_id}", response_model=BusinessAnalyticsOverviewResponse)
def admin_business_analytics(
    business_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> BusinessAnalyticsOverviewResponse:
    impressions, interactions, breakdown = SponsoredReportingService(db).admin_business_stats(business_id)
    return BusinessAnalyticsOverviewResponse(
        business_id=business_id,
        impressions_count=impressions,
        interactions_count=interactions,
        interactions_by_type=breakdown,
    )


@router.get("/analytics/sponsored-places/{place_id}", response_model=SponsoredPlaceAnalyticsResponse)
def admin_sponsored_place_analytics(
    place_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> SponsoredPlaceAnalyticsResponse:
    impressions, interactions, breakdown = SponsoredReportingService(db).admin_place_stats(place_id)
    return SponsoredPlaceAnalyticsResponse(
        sponsored_place_id=place_id,
        impressions_count=impressions,
        interactions_count=interactions,
        interactions_by_type=breakdown,
    )

