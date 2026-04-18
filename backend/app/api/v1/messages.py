from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.trip import Trip
from app.models.user import User
from app.schemas.trip_message import (
    TripContinuationResponse,
    TripMessageCreateRequest,
)
from app.services.trip_message_service import TripMessageService

router = APIRouter(prefix="/trips", tags=["messages"])


@router.post(
    "/{trip_id}/messages",
    response_model=TripContinuationResponse,
)
def continue_trip_messages(
    trip_id: int,
    payload: TripMessageCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TripContinuationResponse:
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found",
        )

    if trip.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions for this trip",
        )

    service = TripMessageService(db)
    assistant_message, updated_itinerary = service.continue_trip(
        trip=trip,
        user_content=payload.content,
    )

    return TripContinuationResponse(
        message=assistant_message,
        updated_itinerary=updated_itinerary,
    )
