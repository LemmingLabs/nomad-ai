from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.trip_message import (
    TripContinuationResponse,
    TripMessageCreateRequest,
    TripMessageListResponse,
)
from app.services.trip_message_service import TripMessageService
from app.services.trip_service import get_user_trip_by_id

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
    try:
        trip = get_user_trip_by_id(db=db, user_id=current_user.id, trip_id=trip_id)
    except ValueError as exc:
        message = str(exc)
        if "not found" in message.lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message) from exc
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message) from exc

    service = TripMessageService(db)
    assistant_message, updated_itinerary = service.continue_trip(
        trip=trip,
        user_content=payload.content,
    )

    return TripContinuationResponse(
        message=assistant_message,
        updated_itinerary=updated_itinerary,
    )


@router.get(
    "/{trip_id}/messages",
    response_model=TripMessageListResponse,
)
def get_trip_messages(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TripMessageListResponse:
    try:
        trip = get_user_trip_by_id(db=db, user_id=current_user.id, trip_id=trip_id)
    except ValueError as exc:
        message = str(exc)
        if "not found" in message.lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message) from exc
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message) from exc

    service = TripMessageService(db)
    messages = service.get_trip_messages(trip=trip)
    return TripMessageListResponse(items=messages)
