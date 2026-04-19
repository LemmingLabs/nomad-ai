import logging
import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)


class TwoGISClient:
    def __init__(self):
        self.api_key = settings.TWOGIS_API_KEY

    async def search_place(self, query: str, lon: float, lat: float) -> list[dict]:
        params = {
            "key": self.api_key,
            "q": query,
            "location": f"{lon},{lat}",
            "fields": "items.point,items.schedule,items.review_count",
            "page_size": 5,
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    "https://catalog.api.2gis.com/3.0/items",
                    params=params,
                )

            response.raise_for_status()
            data = response.json()

            items = data.get("result", {}).get("items", [])

            return [
                {
                    "id": item.get("id"),
                    "name": item.get("name"),
                    "address_name": item.get("address_name"),
                    "lat": item.get("point", {}).get("lat"),
                    "lon": item.get("point", {}).get("lon"),
                }
                for item in items
            ]

        except httpx.TimeoutException:
            logger.warning("2GIS search_place timeout")
            return []
        except httpx.HTTPStatusError as exc:
            self._log_http_error(exc.response.status_code)
            return []
        except Exception:
            logger.exception("2GIS search_place failed")
            return []

    async def get_route_info(
        self,
        origin_lon: float,
        origin_lat: float,
        dest_lon: float,
        dest_lat: float,
        transport: str = "taxi",
    ) -> dict | None:

        transport_map = {
            "taxi": "taxi",
            "driving": "driving",
            "car": "driving",
            "walking": "walking",
        }

        transport = transport_map.get(transport)

        if not transport:
            logger.warning("Unsupported transport type")
            return None

        payload = {
            "points": [
                {"lon": origin_lon, "lat": origin_lat, "type": "stop"},
                {"lon": dest_lon, "lat": dest_lat, "type": "stop"},
            ],
            "transport": transport,
            "output": "summary",
            "locale": "ru",
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"https://routing.api.2gis.com/routing/7.0.0/global?key={self.api_key}",
                    json=payload,
                )

            logger.info("2GIS routing response: %s", response.text)

            response.raise_for_status()
            data = response.json()

            logger.info("2GIS ROUTING RAW: %s", data)

            if data.get("error"):
                logger.warning("2GIS routing error: %s", data["error"])
                return None


            summary = None

            if isinstance(data.get("result"), list) and data["result"]:
                summary = data["result"][0]

            elif isinstance(data.get("routes"), list) and data["routes"]:
                summary = data["routes"][0].get("summary")

            elif "duration" in data and "length" in data:
                return {
                    "distance_m": data["length"],
                    "duration_s": data["duration"],
                }

            if not summary:
                logger.warning("Unknown routing format: %s", data)
                return None


            distance = summary.get("total_distance") or summary.get("length")
            duration = summary.get("total_duration") or summary.get("duration")

            if distance is None or duration is None:
                logger.warning("Invalid routing summary: %s", summary)
                return None

            return {
                "distance_m": distance,
                "duration_s": duration,
            }

        except httpx.TimeoutException:
            logger.warning("2GIS routing timeout")
            return None
        except httpx.HTTPStatusError as exc:
            self._log_http_error(exc.response.status_code)
            return None
        except Exception:
            logger.exception("2GIS get_route_info failed")
            return None

    async def get_dist_matrix(
        self,
        sources: list[dict],
        targets: list[dict],
        transport: str = "taxi",
    ):
        transport_map = {
            "taxi": "taxi",
            "driving": "car",
            "car": "car",
            "walking": "walking",
        }

        transport = transport_map.get(transport)

        if len(sources) > 25 or len(targets) > 25:
            logger.warning("Too many points for matrix request")
            return None

        points = sources + targets

        payload = {
            "points": points,
            "sources": list(range(len(sources))),
            "targets": list(range(len(sources), len(points))),
            "transport": transport,
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"https://routing.api.2gis.com/get_dist_matrix?key={self.api_key}&version=2.0",
                    json=payload,
                )

            logger.info("2GIS matrix response: %s", response.text)

            response.raise_for_status()
            return response.json()

        except httpx.TimeoutException:
            logger.warning("2GIS matrix timeout")
            return None
        except httpx.HTTPStatusError as exc:
            self._log_http_error(exc.response.status_code)
            return None
        except Exception:
            logger.exception("2GIS get_dist_matrix failed")
            return None

    def _log_http_error(self, status_code: int) -> None:
        if status_code == 403:
            logger.warning("2GIS API key invalid or quota exceeded")
        elif status_code == 429:
            logger.warning("2GIS rate limit hit")
        elif status_code >= 500:
            logger.warning("2GIS server error %s", status_code)
        else:
            logger.exception("2GIS HTTP error: %s", status_code)
