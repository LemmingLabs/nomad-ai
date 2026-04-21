import asyncio
import logging
from copy import deepcopy

from app.integrations.twogis_client import TwoGISClient
from app.schemas.routing import RouteSegment

logger = logging.getLogger(__name__)

BASE_FARE_KGS = 80
RATE_PER_KM_KGS = 12

FALLBACK_DISTANCE_KM = None
FALLBACK_DURATION_MINS = None
FALLBACK_ESTIMATED_COST = None
FALLBACK_TRANSPORT_TYPE = "unknown"

DEFAULT_CENTER_LON = 74.5698
DEFAULT_CENTER_LAT = 42.8746


class RoutingService:
    def __init__(self, client: TwoGISClient | None = None):
        self.client = client or TwoGISClient()
        self.cache = {}


    def _normalize_transport(self, transport: str) -> str:
        mapping = {
            "taxi": "taxi",
            "driving": "driving",
            "car": "driving",
            "walking": "walking",
        }
        if not transport:
            return "taxi"
        return mapping.get(transport.strip().lower(), "taxi")


    async def enrich_itinerary(
        self,
        locations: list[str],
        default_transport: str = "taxi",
        routing_locations: list[str] | None = None,
    ) -> list[RouteSegment]:

        if len(locations) < 2:
            return []

        transport = self._normalize_transport(default_transport)

        pairs = list(zip(locations, locations[1:]))

        resolved_points: list[dict | None] = []

        q_locations = routing_locations if routing_locations else locations

        for location in q_locations:
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
            if not isinstance(days, list) or not all(isinstance(day, dict) and "location" in day for day in days):
                return itinerary_json
                
            locations = [day["location"] for day in days]
            routing_locs = [day.get("routing_location") or day["location"] for day in days]

            if len(locations) < 2:
                return itinerary_json
            

            segments = await self.enrich_itinerary(locations, transport, routing_locations=routing_locs)

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
            alias_mapping = {
                "ala-too square": "Ala-Too Square Bishkek",
                "osh bazaar": "Osh Bazaar Bishkek",
                "issyk-kul lake": "Issyk-Kul Lake Cholpon-Ata",
                "jeti-oguz gorge": "Jeti-Oguz Gorge Karakol",
                "ala-archa national park": "Ala-Archa National Park Bishkek",
            }
            
            search_query = location
            normalized_loc = location.strip().lower()
            for key, value in alias_mapping.items():
                if key in normalized_loc:
                    search_query = value
                    break
            
            cache_key = search_query.lower()
            if cache_key in self.cache:
                results = self.cache[cache_key]
            else:
                results = None
                for attempt in range(3):
                    try:
                        results = await self.client.search_place(
                            search_query,
                            DEFAULT_CENTER_LON,
                            DEFAULT_CENTER_LAT,
                        )
                        break
                    except Exception as e:
                        if attempt == 2:
                            raise e
                        await asyncio.sleep(0.2)
                
                if results is not None:
                    self.cache[cache_key] = results

            logger.debug("LOCATION RESOLUTION: %s -> %s", location, results)

            if not results:
                logger.warning("No geocode result for: %s", location)
                return None


            def _score(item: dict) -> int:
                # ❗ HARD FILTER: reject invalid coordinates immediately
                if item.get("lat") is None or item.get("lon") is None:
                    return -9999

                score = 0
                item_name = (item.get("name") or "").lower()
                item_address = (item.get("address_name") or "").lower()
                query_lower = search_query.lower()

                # Boost for exact or partial matches
                if query_lower == item_name:
                    score += 10
                elif any(word == query_lower for word in item_name.split()):
                    score += 8
                elif query_lower in item_name:
                    score += 5
                
                if query_lower in item_address:
                    score += 3

                # Penalty for wrong type of place
                nature_keywords = ["lake", "gorge", "national park", "square", "bazaar", "park", "mountain"]
                office_keywords = [
                    "office", "бизнес-центр", "business center", "mall", 
                    "торговый центр", "представительство", "строящийся",
                    "hotel", "гостиница", "agency", "агентство недвижимости"
                ]

                is_nature_query = any(k in query_lower for k in nature_keywords)
                if is_nature_query:
                    if any(k in item_name or k in item_address for k in office_keywords):
                        score -= 20
                    # Additional boost for matching nature types
                    if any(k in item_name for k in ["park", "square", "bazaar", "lake", "gorge"]):
                        score += 5
                else:
                    if item.get("name"):
                        score += 1
                    if item.get("address_name"):
                        score += 2

                return score

            valid_results = [
                r for r in results
                if r.get("lat") is not None and r.get("lon") is not None
            ]

            if not valid_results:
                logger.warning("All geocode results invalid for: %s", location)
                return None

            best = max(valid_results, key=_score)
            logger.debug("BEST MATCH: %s -> %s", location, best)
            
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
              return None

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
