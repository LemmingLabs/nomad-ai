from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.sponsored_interaction import (
    SponsoredInteractionCreateRequest,
    SponsoredInteractionResponse,
)
from app.services.sponsored_analytics_service import SponsoredAnalyticsService


router = APIRouter(prefix="/sponsored", tags=["sponsored"])


@router.post(
    "/interactions",
    response_model=SponsoredInteractionResponse,
    status_code=status.HTTP_201_CREATED,
)
def log_sponsored_interaction(
    payload: SponsoredInteractionCreateRequest,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> SponsoredInteractionResponse:
    try:
        interaction = SponsoredAnalyticsService(db).log_interaction(
            sponsored_place_id=payload.sponsored_place_id,
            business_id=payload.business_id,
            interaction_type=payload.interaction_type,
            trip_id=payload.trip_id,
        )
    except ValueError as exc:
        message = str(exc)
        if "not found" in message.lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message) from exc
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message) from exc
    return SponsoredInteractionResponse.model_validate(interaction)

