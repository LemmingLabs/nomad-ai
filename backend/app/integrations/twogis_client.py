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
            items = response.json().get("result", {}).get("items", [])
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
            logger.warning("2GIS request timed out")
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
        if transport not in {"taxi", "driving", "walking"}:
            logger.warning("Unsupported 2GIS transport: %s", transport)
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
            response.raise_for_status()
            results = response.json().get("result", [])
            if not results:
                return None
            summary = results[0]
            return {
                "distance_m": summary.get("total_distance"),
                "duration_s": summary.get("total_duration"),
            }
        except httpx.TimeoutException:
            logger.warning("2GIS request timed out")
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
    ) -> list[list[dict]] | None:
        if transport not in {"taxi", "driving", "walking"}:
            logger.warning("Unsupported 2GIS transport: %s", transport)
            return None
        if len(sources) > 25 or len(targets) > 25:
            logger.warning("2GIS distance matrix limit exceeded")
            return None

        payload = {
            "sources": sources,
            "targets": targets,
            "transport": transport,
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"https://routing.api.2gis.com/distance-matrix/2.0?key={self.api_key}",
                    json=payload,
                )
            response.raise_for_status()
            rows = response.json().get("rows", [])
            return [
                [
                    {
                        "distance_m": element.get("distance"),
                        "duration_s": element.get("duration"),
                    }
                    for element in row.get("elements", [])
                ]
                for row in rows
            ]
        except httpx.TimeoutException:
            logger.warning("2GIS request timed out")
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
            logger.exception("2GIS request failed with status %s", status_code)
