from typing import Union, Tuple, List, Dict

from app.integrations.twogis_client import TwoGISClient
from app.exceptions import (
    TwoGISAuthError,
    TwoGISRateLimitError,
    TwoGISTimeoutError,
)

# Mock definitions for schematics so the module can load if they don't exist
try:
    from app.schemas.trip_schema import TransportResult, DayPlan
except ImportError:
    class TransportResult:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
    class DayPlan:
        pass


class RoutingServiceError(Exception):
    """Custom exception for routing service errors, wrapping 2GIS exceptions."""
    pass


class RoutingService:
    """Service for estimating transport costs and enriching itineraries."""

    def __init__(self, twogis_client: TwoGISClient):
        self.client = twogis_client
        self.tariffs = {
            "taxi": {"base": 80.0, "rate_km": 12.0, "rate_min": 2.0},
            "marshrutka": {"base": 30.0, "rate_km": 3.0, "rate_min": 0.5},
            "transfer": {"base": 500.0, "rate_km": 20.0, "rate_min": 3.0},
        }

    async def _resolve_location(self, loc: Union[str, Tuple[float, float]]) -> Tuple[float, float]:
        if isinstance(loc, tuple):
            return loc
        
        try:
            # Provide a fallback center location if origin is a string
            results = await self.client.search_place(loc, (0.0, 0.0))
            if not results:
                raise RoutingServiceError(f"Location not found for query: {loc}")
            first_result = results[0]
            return (float(first_result["lon"]), float(first_result["lat"]))
        except (TwoGISAuthError, TwoGISRateLimitError, TwoGISTimeoutError) as e:
            raise RoutingServiceError(f"2GIS API Error: {str(e)}") from e

    async def estimate_transport(
        self,
        origin: Union[str, Tuple[float, float]],
        destination: Union[str, Tuple[float, float]],
        transport_type: str,
    ) -> TransportResult:
        """
        Estimate the distance, duration, and price for a transport mode between two coordinates.
        Uses 2GIS Routing API, and if strings are provided, resolves them via Places API.
        """
        if transport_type not in self.tariffs:
            # Default or fallback? Prompt just specified these 3.
            pass
            
        origin_coords = await self._resolve_location(origin)
        dest_coords = await self._resolve_location(destination)

        try:
            route_info = await self.client.get_route_info(origin_coords, dest_coords, transport_type)
        except (TwoGISAuthError, TwoGISRateLimitError, TwoGISTimeoutError) as e:
            raise RoutingServiceError(f"2GIS API Error: {str(e)}") from e

        if not route_info:
            raise RoutingServiceError("Could not retrieve route info from 2GIS Client.")

        distance_km = route_info.get("distance_km", 0.0)
        duration_min = route_info.get("duration_min", 0.0)

        tariff = self.tariffs.get(transport_type, self.tariffs["marshrutka"])
        
        price = tariff["base"] + (distance_km * tariff["rate_km"]) + (duration_min * tariff["rate_min"])
        
        price_min = round(price * 0.9, 2)
        price_max = round(price * 1.1, 2)

        return TransportResult(
            **{"from": str(origin)},
            to=str(destination),
            transport_type=transport_type,
            distance_km=distance_km,
            duration_min=duration_min,
            price_min=price_min,
            price_max=price_max,
            currency="KGS"
        )

    async def enrich_itinerary(self, day_plans: List[DayPlan]) -> List[DayPlan]:
        """
        Enrich a list of consecutive DayPlans with transport estimation between them.
        """
        for i in range(len(day_plans) - 1):
            current_plan = day_plans[i]
            next_plan = day_plans[i + 1]
            
            origin = current_plan.location
            destination = next_plan.location
            
            transport_type = "marshrutka"
            if hasattr(current_plan, 'transport') and current_plan.transport is not None:
                t_type = getattr(current_plan.transport, 'transport_type', None)
                if t_type:
                    transport_type = t_type

            result = await self.estimate_transport(origin, destination, transport_type)
            current_plan.transport = result

        return day_plans
