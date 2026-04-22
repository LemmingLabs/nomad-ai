from fastapi import APIRouter
import logging

from app.schemas.routing import RoutingRequest, RoutingResponse
from app.services.routing_service import RoutingService

router = APIRouter(prefix="/routing", tags=["routing"])
logger = logging.getLogger(__name__)


@router.post("/estimate", response_model=RoutingResponse)
async def estimate_routing(request: RoutingRequest) -> RoutingResponse:
    svc = RoutingService()
    segments = await svc.enrich_itinerary(
        request.locations,
        request.transport_type,
    )
    return RoutingResponse(
        segments=segments,
        total_distance_km=sum(s.distance_km or 0.0 for s in segments),
        total_duration_mins=sum(s.duration_mins or 0 for s in segments),
        total_cost=sum(s.estimated_cost or 0.0 for s in segments),
    )