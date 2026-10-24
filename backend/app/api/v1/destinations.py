from fastapi import APIRouter

from app.schemas.destination import DestinationResponse
from app.core.destination_registry import list_destinations


router = APIRouter(prefix="/destinations", tags=["Destinations"])


@router.get("", response_model=list[DestinationResponse])
def get_destinations() -> list[DestinationResponse]:
    """List destinations currently enabled for new trip generation."""
    return [
        DestinationResponse.from_destination(destination)
        for destination in list_destinations(enabled_only=True)
    ]
