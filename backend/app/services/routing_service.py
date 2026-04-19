import logging
from copy import deepcopy

from app.integrations.twogis_client import TwoGISClient
from app.schemas.routing import RouteSegment


BASE_FARE_KGS = 80
RATE_PER_KM_KGS = 12
FALLBACK_DISTANCE_KM = 0.0
FALLBACK_DURATION_MINS = 0
FALLBACK_ESTIMATED_COST = 0.0
FALLBACK_TRANSPORT_TYPE = "unknown"
DEFAULT_CENTER_LON = 74.5698
DEFAULT_CENTER_LAT = 42.8746
logger = logging.getLogger(__name__)

class RoutingService:
    def __init__(self, client: TwoGISClient | None = None):
        self.client = client or TwoGISClient()

    async def enrich_itinerary(
        self,
        locations: list[str],
        default_transport: str = "taxi",
    ) -> list[RouteSegment]:
        # enrich_itinerary ONLY accepts list[str] — no type switching
        try:
            pairs = list(zip(locations, locations[1:]))
            if not pairs:
                return []

            resolved_points: list[dict | None] = []
            for location in locations:
                resolved_points.append(await self._resolve_point(location))

            matrix = None
            if all(p is not None for p in resolved_points):
                try:
                    matrix = await self.client.get_dist_matrix(
                        sources=[p for p in resolved_points[:-1] if p is not None],
                        targets=[p for p in resolved_points[1:] if p is not None],
                        transport=default_transport,
                    )
                except Exception:
                    matrix = None

            segments: list[RouteSegment] = []
            for index, (origin, destination) in enumerate(pairs):
                origin_point = resolved_points[index]
                dest_point = resolved_points[index + 1]

                if origin_point is None or dest_point is None:
                    segments.append(self._fallback(origin, destination))
                    continue

                route_data = self._diagonal(matrix, index)
                if route_data is None:
                    route_data = await self._route_fallback(
                        origin_point, dest_point, default_transport
                    )

                if route_data is None:
                    segments.append(self._fallback(origin, destination))
                    continue

                segments.append(self._build(
                    origin, destination,
                    route_data.get("distance_m"),
                    route_data.get("duration_s"),
                    default_transport,
                ))

            return segments
        except Exception:
            return [self._fallback(o, d) for o, d in zip(locations, locations[1:])]

    async def enrich_from_itinerary_json(
        self,
        itinerary_json: dict,
        transport: str = "taxi",
    ) -> dict:
        try:
            original_itinerary = deepcopy(itinerary_json)
            days = itinerary_json.get("days", [])
            locations = [day["location"] for day in days]

            if len(locations) < 2:
                return itinerary_json

            segments = await self.enrich_itinerary(locations, transport)

            days[0]["route_from_previous"] = None
            for index, day in enumerate(days[1:], start=1):
                segment = segments[index - 1] if index - 1 < len(segments) else None
                day["route_from_previous"] = (
                    segment.model_dump() if segment is not None else None
                )

            return itinerary_json
        except Exception:
            logger.warning(
                "enrich_from_itinerary_json failed silently", exc_info=True
            )
            return original_itinerary if "original_itinerary" in locals() else itinerary_json

    async def _resolve_point(self, location: str) -> dict | None:
        # search_place is ALWAYS called with (query, lon, lat) as positional args
        # Never use tuple args — the TwoGISClient signature is fixed
        try:
            results = await self.client.search_place(
                location,
                DEFAULT_CENTER_LON,
                DEFAULT_CENTER_LAT,
            )
            if not results:
                return None
            return {"lon": results[0].get("lon"), "lat": results[0].get("lat")}
        except Exception:
            return None

    async def _route_fallback(
        self, origin: dict, dest: dict, transport: str
    ) -> dict | None:
        # get_route_info is ALWAYS called with keyword args
        # Never use positional tuple args
        try:
            return await self.client.get_route_info(
                origin_lon=origin["lon"],
                origin_lat=origin["lat"],
                dest_lon=dest["lon"],
                dest_lat=dest["lat"],
                transport=transport,
            )
        except Exception:
            return None

    def _diagonal(self, matrix: list[list[dict]] | None, index: int) -> dict | None:
        if matrix is None or index >= len(matrix):
            return None
        row = matrix[index]
        if index >= len(row):
            return None
        return row[index]

    def _build(
        self, origin: str, destination: str,
        distance_m: int | float | None,
        duration_s: int | float | None,
        transport_type: str,
    ) -> RouteSegment:
        distance_km = round((distance_m or 0) / 1000, 2)
        duration_mins = int((duration_s or 0) // 60)
        cost = 0.0 if transport_type == "walking" else float(
            round(BASE_FARE_KGS + (distance_km * RATE_PER_KM_KGS))
        )
        return RouteSegment(
            origin=origin, destination=destination,
            distance_km=distance_km, duration_mins=duration_mins,
            estimated_cost=cost, transport_type=transport_type,
        )

    def _fallback(self, origin: str, destination: str) -> RouteSegment:
        return RouteSegment(
            origin=origin, destination=destination,
            distance_km=FALLBACK_DISTANCE_KM,
            duration_mins=FALLBACK_DURATION_MINS,
            estimated_cost=FALLBACK_ESTIMATED_COST,
            transport_type=FALLBACK_TRANSPORT_TYPE,
        )
