from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_business
from app.models.user import User
from app.models.sponsored_place import SponsoredPlace
from app.models.sponsored_place_media import SponsoredPlaceMedia
from app.models.business_media import BusinessMedia
from app.schemas.business import BusinessCreateRequest, BusinessResponse, BusinessUpdateRequest
from app.schemas.business_media import BusinessMediaCreateRequest, BusinessMediaResponse
from app.schemas.sponsored_analytics import BusinessAnalyticsOverviewResponse, SponsoredPlaceAnalyticsResponse
from app.schemas.sponsored_place_media import SponsoredPlaceMediaResponse
from app.schemas.sponsored_place import (
    SponsoredPlaceCreateRequest,
    SponsoredPlaceResponse,
    SponsoredPlaceUpdateRequest,
)
from app.models.sponsored_place_media import SponsoredPlaceMediaType
from app.services.business_service import BusinessService
from app.services.sponsored_place_media_service import SponsoredPlaceMediaService
from app.services.sponsored_place_service import SponsoredPlaceService
from app.services.sponsored_reporting_service import SponsoredReportingService
from app.services.storage_service import StorageService


router = APIRouter(prefix="/business", tags=["business"])


def _storage() -> StorageService:
    return StorageService()


def _business_media_response(item: BusinessMedia) -> BusinessMediaResponse:
    response = BusinessMediaResponse.model_validate(item)
    data = response.model_dump()
    data["url"] = _storage().get_access_url(item.url)
    return BusinessMediaResponse(**data)


def _sponsored_place_media_response(item: SponsoredPlaceMedia) -> SponsoredPlaceMediaResponse:
    response = SponsoredPlaceMediaResponse.model_validate(item)
    data = response.model_dump()
    data["url"] = _storage().get_access_url(item.url)
    return SponsoredPlaceMediaResponse(**data)


def _sponsored_place_response(place: SponsoredPlace) -> SponsoredPlaceResponse:
    response = SponsoredPlaceResponse.model_validate(place)
    data = response.model_dump()
    data["media"] = [_sponsored_place_media_response(item).model_dump() for item in (place.media or [])]
    return SponsoredPlaceResponse(**data)


@router.get("/me", response_model=BusinessResponse)
def get_my_business(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_business),
) -> BusinessResponse:
    business = BusinessService(db).get_my_business(current_user)
    return BusinessResponse.model_validate(business)


@router.post("/me", response_model=BusinessResponse, status_code=status.HTTP_201_CREATED)
def create_my_business(
    payload: BusinessCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_business),
) -> BusinessResponse:
    business = BusinessService(db).create_my_business(
        current_user,
        name=payload.name,
        description=payload.description,
        contact_phone=payload.contact_phone,
        website_url=payload.website_url,
    )
    return BusinessResponse.model_validate(business)


@router.patch("/me", response_model=BusinessResponse)
def update_my_business(
    payload: BusinessUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_business),
) -> BusinessResponse:
    business = BusinessService(db).update_my_business(
        current_user,
        **payload.model_dump(exclude_unset=True),
    )
    return BusinessResponse.model_validate(business)


@router.get("/me/media", response_model=list[BusinessMediaResponse])
def list_my_media(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_business),
) -> list[BusinessMediaResponse]:
    items = BusinessService(db).list_my_media(current_user)
    return [_business_media_response(item) for item in items]


@router.post("/me/media", response_model=BusinessMediaResponse, status_code=status.HTTP_201_CREATED)
def add_my_media(
    payload: BusinessMediaCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_business),
) -> BusinessMediaResponse:
    item = BusinessService(db).add_my_media(current_user, type=payload.type, url=payload.url)
    return _business_media_response(item)


@router.delete("/me/media/{media_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_my_media(
    media_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_business),
) -> None:
    BusinessService(db).delete_my_media(current_user, media_id)


@router.get("/me/sponsored-places", response_model=list[SponsoredPlaceResponse])
def list_my_sponsored_places(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_business),
) -> list[SponsoredPlaceResponse]:
    places = SponsoredPlaceService(db).list_my_places(current_user)
    return [_sponsored_place_response(place) for place in places]


@router.post(
    "/me/sponsored-places",
    response_model=SponsoredPlaceResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_my_sponsored_place(
    payload: SponsoredPlaceCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_business),
) -> SponsoredPlaceResponse:
    place = SponsoredPlaceService(db).create_my_place(current_user, **payload.model_dump())
    return _sponsored_place_response(place)


@router.get("/me/sponsored-places/{place_id}", response_model=SponsoredPlaceResponse)
def get_my_sponsored_place(
    place_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_business),
) -> SponsoredPlaceResponse:
    place = SponsoredPlaceService(db).get_my_place(current_user, place_id)
    return _sponsored_place_response(place)


@router.patch("/me/sponsored-places/{place_id}", response_model=SponsoredPlaceResponse)
def update_my_sponsored_place(
    place_id: int,
    payload: SponsoredPlaceUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_business),
) -> SponsoredPlaceResponse:
    place = SponsoredPlaceService(db).update_my_place(
        current_user,
        place_id,
        **payload.model_dump(exclude_unset=True),
    )
    return _sponsored_place_response(place)


@router.delete("/me/sponsored-places/{place_id}", status_code=status.HTTP_204_NO_CONTENT)
def deactivate_my_sponsored_place(
    place_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_business),
) -> None:
    SponsoredPlaceService(db).deactivate_my_place(current_user, place_id)


@router.get("/me/sponsored-places/{place_id}/media", response_model=list[SponsoredPlaceMediaResponse])
def list_my_sponsored_place_media(
    place_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_business),
) -> list[SponsoredPlaceMediaResponse]:
    items = SponsoredPlaceMediaService(db).list_my_place_media(current_user, place_id)
    return [_sponsored_place_media_response(item) for item in items]


@router.post(
    "/me/sponsored-places/{place_id}/media",
    response_model=SponsoredPlaceMediaResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_my_sponsored_place_media(
    place_id: int,
    type: SponsoredPlaceMediaType = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_business),
) -> SponsoredPlaceMediaResponse:
    item = await SponsoredPlaceMediaService(db).upload_my_place_media(
        current_user,
        place_id=place_id,
        type=type,
        file=file,
    )
    return _sponsored_place_media_response(item)


@router.delete("/me/sponsored-places/{place_id}/media/{media_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_my_sponsored_place_media(
    place_id: int,
    media_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_business),
) -> None:
    SponsoredPlaceMediaService(db).delete_my_place_media(
        current_user,
        place_id=place_id,
        media_id=media_id,
    )


@router.get("/me/analytics/overview", response_model=BusinessAnalyticsOverviewResponse)
def get_my_analytics_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_business),
) -> BusinessAnalyticsOverviewResponse:
    business_id, impressions, interactions, breakdown = SponsoredReportingService(db).business_overview_for_me(
        current_user
    )
    return BusinessAnalyticsOverviewResponse(
        business_id=business_id,
        impressions_count=impressions,
        interactions_count=interactions,
        interactions_by_type=breakdown,
    )


@router.get(
    "/me/analytics/sponsored-places/{place_id}",
    response_model=SponsoredPlaceAnalyticsResponse,
)
def get_my_sponsored_place_analytics(
    place_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_business),
) -> SponsoredPlaceAnalyticsResponse:
    impressions, interactions, breakdown = SponsoredReportingService(db).sponsored_place_stats_for_me(
        current_user,
        place_id,
    )
    return SponsoredPlaceAnalyticsResponse(
        sponsored_place_id=place_id,
        impressions_count=impressions,
        interactions_count=interactions,
        interactions_by_type=breakdown,
    )
