from fastapi import APIRouter

from app.schemas.routing import RoutingRequest, RoutingResponse
from app.services.routing_service import RoutingService


router = APIRouter(prefix="/routing", tags=["routing"])


@router.post(
    "/estimate",
    response_model=RoutingResponse,
)
async def estimate_routing(request: RoutingRequest) -> RoutingResponse:
    try:
        svc = RoutingService()
        segments = await svc.enrich_itinerary(
            request.locations,
            request.transport_type,
        )
        return RoutingResponse(
            segments=segments,
            total_distance_km=sum(segment.distance_km for segment in segments),
            total_duration_mins=sum(segment.duration_mins for segment in segments),
            total_cost=sum(segment.estimated_cost for segment in segments),
        )
    except Exception:
        return RoutingResponse(
            segments=[],
            total_distance_km=0.0,
            total_duration_mins=0,
            total_cost=0.0,
        )
