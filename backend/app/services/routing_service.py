import logging
from copy import deepcopy

from app.integrations.twogis_client import TwoGISClient
from app.schemas.routing import RouteSegment

logger = logging.getLogger(__name__)

BASE_FARE_KGS = 80
RATE_PER_KM_KGS = 12

FALLBACK_DISTANCE_KM = 0.0
FALLBACK_DURATION_MINS = 0
FALLBACK_ESTIMATED_COST = 0.0
FALLBACK_TRANSPORT_TYPE = "unknown"

DEFAULT_CENTER_LON = 74.5698
DEFAULT_CENTER_LAT = 42.8746


class RoutingService:
    def __init__(self, client: TwoGISClient | None = None):
        self.client = client or TwoGISClient()


    def _normalize_transport(self, transport: str) -> str:
        mapping = {
            "taxi": "taxi",
            "driving": "driving",
            "car": "driving",
            "walking": "walking",
        }
        if transport is None:
          raise ValueError(f"Unsupported transport: {transport}")
        return mapping.get(transport.strip().lower())


    async def enrich_itinerary(
        self,
        locations: list[str],
        default_transport: str = "taxi",
    ) -> list[RouteSegment]:

        if len(locations) < 2:
            return []

        transport = self._normalize_transport(default_transport)

        pairs = list(zip(locations, locations[1:]))

        resolved_points: list[dict | None] = []


        for location in locations:
            point = await self._resolve_point(location)
            resolved_points.append(point)

        logger.info("Resolved points: %s", resolved_points)

        segments: list[RouteSegment] = []

        for index, (origin, destination) in enumerate(pairs):

            origin_point = resolved_points[index]
            dest_point = resolved_points[index + 1]

            if not origin_point or not dest_point:
                logger.warning(
                    "Missing geocode: %s -> %s",
                    origin,
                    destination,
                )
                segments.append(self._fallback(origin, destination))
                continue

            route_data = await self._route_fallback(
                origin_point,
                dest_point,
                transport,
            )

            if not route_data:
                logger.warning(
                    "Routing failed: %s -> %s",
                    origin,
                    destination,
                )
                segments.append(self._fallback(origin, destination))
                continue

            segments.append(
                self._build(
                    origin,
                    destination,
                    route_data.get("distance_m"),
                    route_data.get("duration_s"),
                    transport,
                )
            )

        return segments

    async def enrich_from_itinerary_json(
        self,
        itinerary_json: dict,
        transport: str = "taxi",
    ) -> dict:

        original_itinerary = deepcopy(itinerary_json)

        try:
            days = itinerary_json.get("days", [])
            locations = [day["location"] for day in days]

            if len(locations) < 2:
                return itinerary_json
            

            segments = await self.enrich_itinerary(locations, transport)

            days[0]["route_from_previous"] = None

            for i, day in enumerate(days[1:], start=1):
                day["route_from_previous"] = (
                    segments[i - 1].model_dump()
                    if i - 1 < len(segments)
                    else None
                )

            return itinerary_json

        except Exception:
            logger.exception("enrich_from_itinerary_json failed")
            return original_itinerary

    async def _resolve_point(self, location: str) -> dict | None:
        try:
            results = await self.client.search_place(
                location,
                DEFAULT_CENTER_LON,
                DEFAULT_CENTER_LAT,
            )

            logger.warning("LOCATION RESOLUTION: %s -> %s", location, results)

            if not results:
                logger.warning("No geocode result for: %s", location)
                return None


            def _score(item: dict) -> int:
                # ❗ HARD FILTER: reject invalid coordinates immediately
                if item.get("lat") is None or item.get("lon") is None:
                    return -9999

                score = 0

                if item.get("address_name"):
                    score += 3

                if item.get("name"):
                    score += 1


                return score

            valid_results = [
                r for r in results
                if r.get("lat") is not None and r.get("lon") is not None
            ]

            if not valid_results:
                logger.warning("All geocode results invalid for: %s", location)
                return None

            best = max(valid_results, key=_score)

            if not valid_results:
                return None
            
            return {
                "lon": best["lon"],
                "lat": best["lat"],
            }

        except Exception:
            logger.exception("Geocoding failed: %s", location)
            return None


    async def _route_fallback(
        self,
        origin: dict,
        dest: dict,
        transport: str,
    ) -> dict | None:

        try:
            return await self.client.get_route_info(
                origin_lon=origin["lon"],
                origin_lat=origin["lat"],
                dest_lon=dest["lon"],
                dest_lat=dest["lat"],
                transport=transport,
            )

        except Exception:
            logger.exception("Route API failed")
            return None


    def _build(
        self,
        origin: str,
        destination: str,
        distance_m: int | float | None,
        duration_s: int | float | None,
        transport_type: str,
    ) -> RouteSegment:

        distance_km = round((distance_m or 0) / 1000, 2)
        duration_mins = int((duration_s or 0) // 60)
        def calculate_cost(distance_km: float, transport_type: str) -> float | None:
          if transport_type == "driving":
              return 0.0 

          if transport_type == "walking":
              return 0.0

          if transport_type == "taxi":
              base_fare = 80
              rate_per_km = 12
              return round(base_fare + distance_km * rate_per_km, 2)

          return None


        cost = calculate_cost(distance_km, transport_type)

        return RouteSegment(
            origin=origin,
            destination=destination,
            distance_km=distance_km,
            duration_mins=duration_mins,
            estimated_cost=cost,
            transport_type=transport_type,
        )

    def _fallback(self, origin: str, destination: str) -> RouteSegment:
        return RouteSegment(
            origin=origin,
            destination=destination,
            distance_km=FALLBACK_DISTANCE_KM,
            duration_mins=FALLBACK_DURATION_MINS,
            estimated_cost=FALLBACK_ESTIMATED_COST,
            transport_type=FALLBACK_TRANSPORT_TYPE,
        )
