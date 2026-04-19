from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_user_optional
from app.schemas.trip import (
    TripGenerateRequest,
    TripListResponse,
    TripResponse,
    TripDetailResponse,
    SyncGuestTripRequest,
)
from app.services import trip_service

router = APIRouter(prefix="/trips", tags=["Trips"])


def _map_value_error_to_http_exception(exc: ValueError) -> HTTPException:
    message = str(exc)
    if "not found" in message.lower():
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message)
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)


@router.post("/generate", response_model=TripResponse, status_code=status.HTTP_201_CREATED)
def generate_trip(
    payload: TripGenerateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_optional),
) -> TripResponse:
    user_id = current_user.id if current_user else None
    try:
        trip = trip_service.generate_trip(
            db=db,
            user_id=user_id,
            budget=payload.budget,
            days=payload.days,
            interests=payload.interests,
            travel_style=payload.travel_style,
            prompt=payload.prompt,
        )
    except ValueError as exc:
        raise _map_value_error_to_http_exception(exc) from exc
    return trip


@router.get("", response_model=TripListResponse)
def list_trips(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> TripListResponse:
    trips = trip_service.list_user_trips(db=db, user_id=current_user.id)
    return TripListResponse(items=trips)


@router.get("/{trip_id}", response_model=TripDetailResponse)
def get_trip(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> TripDetailResponse:
    try:
        detailed_trip = trip_service.get_trip_detail(
            db=db,
            user_id=current_user.id,
            trip_id=trip_id,
        )
    except ValueError as exc:
        raise _map_value_error_to_http_exception(exc) from exc
    return detailed_trip


@router.post("/sync-guest", response_model=TripResponse)
def sync_guest_trip(
    payload: SyncGuestTripRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> TripResponse:
    try:
        trip = trip_service.sync_guest_trip_to_user(
            db=db,
            trip_id=payload.trip_id,
            user_id=current_user.id,
        )
    except ValueError as exc:
        raise _map_value_error_to_http_exception(exc) from exc
    return trip


@router.delete("/{trip_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_trip(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        trip_service.delete_user_trip(db=db, user_id=current_user.id, trip_id=trip_id)
    except ValueError as exc:
        raise _map_value_error_to_http_exception(exc) from exc
