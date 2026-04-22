import logging
import re
import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)

PLACES_BASE_URL = "https://places.googleapis.com/v1"
ROUTES_BASE_URL = "https://routes.googleapis.com"


class GoogleMapsClient:
    def __init__(self):
        self.api_key = settings.GOOGLE_MAPS_API_KEY

    def _auth_headers(self, field_mask: str) -> dict:
        return {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": field_mask,
        }

    async def search_place(self, query: str, lon: float, lat: float) -> list[dict]:
        """
        Places API (New) — Text Search
        POST https://places.googleapis.com/v1/places:searchText
        Docs: https://developers.google.com/maps/documentation/places/web-service/text-search
        """
        payload = {
            "textQuery": query,
            "pageSize": 5,
            "locationBias": {
                "circle": {
                    "center": {"latitude": lat, "longitude": lon},
                    "radius": 50000.0,  # 50 km bias radius
                }
            },
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{PLACES_BASE_URL}/places:searchText",
                    json=payload,
                    headers=self._auth_headers(
                        "places.id,places.displayName,places.formattedAddress,places.location"
                    ),
                )

            response.raise_for_status()
            data = response.json()

            places = data.get("places", [])

            return [
                {
                    "id": place.get("id"),
                    "name": place.get("displayName", {}).get("text"),
                    "address_name": place.get("formattedAddress"),
                    "lat": place.get("location", {}).get("latitude"),
                    "lon": place.get("location", {}).get("longitude"),
                }
                for place in places
            ]

        except httpx.TimeoutException:
            logger.warning("Google Places search_place timeout")
            return []
        except httpx.HTTPStatusError as exc:
            self._log_http_error(exc.response.status_code)
            return []
        except Exception:
            logger.exception("Google Places search_place failed")
            return []

    async def get_route_info(
        self,
        origin_lon: float,
        origin_lat: float,
        dest_lon: float,
        dest_lat: float,
        transport: str = "taxi",
    ) -> dict | None:
        """
        Routes API — computeRoutes
        POST https://routes.googleapis.com/directions/v2:computeRoutes
        Docs: https://developers.google.com/maps/documentation/routes/compute_route_directions

        travelMode values: DRIVE, WALK, BICYCLE, TRANSIT, TWO_WHEELER
        Note: Google has no "taxi" mode — taxi maps to DRIVE.
        duration is returned as a string like "165s"; we parse the integer out.
        """
        travel_mode = self._map_transport(transport)
        if not travel_mode:
            logger.warning("Unsupported transport type: %s", transport)
            return None

        payload = {
            "origin": {
                "location": {
                    "latLng": {"latitude": origin_lat, "longitude": origin_lon}
                }
            },
            "destination": {
                "location": {
                    "latLng": {"latitude": dest_lat, "longitude": dest_lon}
                }
            },
            "travelMode": travel_mode,
            "computeAlternativeRoutes": False,
            "languageCode": "ru",
            "units": "METRIC",
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{ROUTES_BASE_URL}/directions/v2:computeRoutes",
                    json=payload,
                    headers=self._auth_headers(
                        "routes.distanceMeters,routes.duration"
                    ),
                )

            logger.info("Google Routes response: %s", response.text)
            response.raise_for_status()
            data = response.json()

            routes = data.get("routes", [])
            if not routes:
                logger.warning("No routes returned from Google Routes API")
                return None

            route = routes[0]
            distance_m = route.get("distanceMeters")
            # duration is returned as e.g. "165s" — parse to int seconds
            duration_raw = route.get("duration", "0s")
            duration_s = self._parse_duration_seconds(duration_raw)

            if distance_m is None or duration_s is None:
                logger.warning("Missing distance/duration in route: %s", route)
                return None

            return {
                "distance_m": distance_m,
                "duration_s": duration_s,
            }

        except httpx.TimeoutException:
            logger.warning("Google Routes get_route_info timeout")
            return None
        except httpx.HTTPStatusError as exc:
            self._log_http_error(exc.response.status_code)
            return None
        except Exception:
            logger.exception("Google Routes get_route_info failed")
            return None

    async def get_dist_matrix(
        self,
        sources: list[dict],
        targets: list[dict],
        transport: str = "taxi",
    ) -> dict | None:
        """
        Routes API — computeRouteMatrix
        POST https://routes.googleapis.com/distanceMatrix/v2:computeRouteMatrix
        Docs: https://developers.google.com/maps/documentation/routes/compute_route_matrix

        Each source/target dict must have "lat" and "lon" keys.
        Max 625 elements (sources × targets) for non-TRANSIT routes.
        Returns the raw API response (list of route objects).
        """
        if len(sources) * len(targets) > 625:
            logger.warning("Too many elements for Google Route Matrix (max 625)")
            return None

        travel_mode = self._map_transport(transport)
        if not travel_mode:
            logger.warning("Unsupported transport type: %s", transport)
            return None

        def _waypoint(point: dict) -> dict:
            return {
                "waypoint": {
                    "location": {
                        "latLng": {
                            "latitude": point["lat"],
                            "longitude": point["lon"],
                        }
                    }
                }
            }

        payload = {
            "origins": [_waypoint(s) for s in sources],
            "destinations": [_waypoint(t) for t in targets],
            "travelMode": travel_mode,
            "languageCode": "ru",
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{ROUTES_BASE_URL}/distanceMatrix/v2:computeRouteMatrix",
                    json=payload,
                    headers=self._auth_headers(
                        "originIndex,destinationIndex,status,condition,distanceMeters,duration"
                    ),
                )

            logger.info("Google Route Matrix response: %s", response.text)
            response.raise_for_status()
            return response.json()

        except httpx.TimeoutException:
            logger.warning("Google Route Matrix timeout")
            return None
        except httpx.HTTPStatusError as exc:
            self._log_http_error(exc.response.status_code)
            return None
        except Exception:
            logger.exception("Google Route Matrix failed")
            return None

    # ------------------------------------------------------------------ #
    # Helpers                                                              #
    # ------------------------------------------------------------------ #

    def _map_transport(self, transport: str) -> str | None:
        """
        Map internal transport strings to Google Routes API travelMode values.
        Google supports: DRIVE, WALK, BICYCLE, TRANSIT, TWO_WHEELER
        "taxi" has no Google equivalent — treated as DRIVE.
        """
        mapping = {
            "taxi": "DRIVE",
            "driving": "DRIVE",
            "car": "DRIVE",
            "walking": "WALK",
            "transit": "TRANSIT",
            "bicycle": "BICYCLE",
        }
        return mapping.get(transport.strip().lower()) if transport else None

    @staticmethod
    def _parse_duration_seconds(duration_str: str) -> int | None:
        """
        Google Routes API returns duration as a Protobuf Duration string,
        e.g. "165s". Parse it to an integer number of seconds.
        """
        try:
            match = re.fullmatch(r"(\d+)s", duration_str.strip())
            if match:
                return int(match.group(1))
            logger.warning("Unexpected duration format: %s", duration_str)
            return None
        except Exception:
            logger.exception("Failed to parse duration: %s", duration_str)
            return None

    def _log_http_error(self, status_code: int) -> None:
        if status_code == 403:
            logger.warning("Google API key invalid or quota exceeded")
        elif status_code == 429:
            logger.warning("Google API rate limit hit")
        elif status_code >= 500:
            logger.warning("Google server error %s", status_code)
        else:
            logger.exception("Google HTTP error: %s", status_code)