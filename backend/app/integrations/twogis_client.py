import asyncio
import logging
from typing import Any, Dict, List, Tuple

import httpx

from app.core.config import settings
from app.exceptions import (
    TwoGISAuthError,
    TwoGISRateLimitError,
    TwoGISServerError,
    TwoGISTimeoutError,
)

logger = logging.getLogger(__name__)


class TwoGISClient:
    """Async client for 2GIS APIs with retry logic and error handling."""

    PLACES_URL = "https://catalog.api.2gis.com/3.0/items"
    ROUTING_URL = "https://routing.api.2gis.com/routing/7.0.0/global"
    DIST_MATRIX_URL = "https://routing.api.2gis.com/get_dist_matrix"

    def __init__(self) -> None:
        """Initialize the TwoGISClient."""
        self.api_key = settings.TWOGIS_API_KEY
        timeout = httpx.Timeout(10.0, connect=5.0)
        self.client = httpx.AsyncClient(timeout=timeout)

    async def _request(
        self, method: str, url: str, **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Execute HTTP request with an exponential backoff.
        
        Retries up to 3 times for HTTP 429 and 5xx errors.
        Delays are 1s, 2s, 4s.
        """
        max_attempts = 3
        delay = 1.0

        for attempt in range(max_attempts):
            try:
                response = await self.client.request(method, url, **kwargs)
                
                if response.status_code == 403:
                    raise TwoGISAuthError("2GIS API key invalid or quota exceeded.")
                elif response.status_code == 429:
                    if attempt < max_attempts - 1:
                        await asyncio.sleep(delay)
                        delay *= 2
                        continue
                    raise TwoGISRateLimitError("2GIS rate limit hit.")
                elif response.status_code >= 500:
                    if attempt < max_attempts - 1:
                        await asyncio.sleep(delay)
                        delay *= 2
                        continue
                    raise TwoGISServerError(f"2GIS server error: {response.status_code}")
                
                response.raise_for_status()
                return response.json()
                
            except httpx.TimeoutException as exc:
                raise TwoGISTimeoutError("2GIS API request timed out.") from exc

        return {}  # Should not be reached

    async def search_place(
        self, query: str, location: Tuple[float, float]
    ) -> List[Dict[str, Any]]:
        """
        Search for places near a location using the 2GIS Places API.
        
        Args:
            query: Text query to search for.
            location: Tuple of (longitude, latitude).
            
        Returns:
            List of parsed dictionary objects.
        """
        lon, lat = location
        params = {
            "q": query,
            "location": f"{lon},{lat}",
            "key": self.api_key,
        }
        
        data = await self._request("GET", self.PLACES_URL, params=params)
        
        results = []
        items = data.get("result", {}).get("items", [])
        for item in items:
            wkt_centroid = item.get("geometry", {}).get("centroid", "")
            lat_val = 0.0
            lon_val = 0.0
            
            if wkt_centroid.startswith("POINT(") and wkt_centroid.endswith(")"):
                coords = wkt_centroid[6:-1].split()
                if len(coords) == 2:
                    try:
                        lon_val = float(coords[0])
                        lat_val = float(coords[1])
                    except ValueError:
                        pass
                        
            results.append({
                "id": str(item.get("id")),
                "name": str(item.get("name")),
                "lat": lat_val,
                "lon": lon_val,
            })
            
        return results

    async def get_route_info(
        self, 
        origin: Tuple[float, float], 
        destination: Tuple[float, float], 
        transport: str
    ) -> Dict[str, float]:
        """
        Get route info between origin and destination using the 2GIS Routing API.
        
        Args:
            origin: Tuple of (longitude, latitude).
            destination: Tuple of (longitude, latitude).
            transport: The mode of transport.
            
        Returns:
            A dictionary containing distance_km and duration_min.
        """
        origin_lon, origin_lat = origin
        dest_lon, dest_lat = destination
        
        payload = {
            "points": [
                {"x": origin_lon, "y": origin_lat},
                {"x": dest_lon, "y": dest_lat},
            ],
            "transport": transport,
            "key": self.api_key,
        }
        
        data = await self._request("POST", self.ROUTING_URL, json=payload)
        
        results = data.get("result", [])
        if not results:
            return {"distance_km": 0.0, "duration_min": 0.0}
            
        route = results[0]
        distance_m = float(route.get("total_distance", 0))
        duration_s = float(route.get("total_duration", 0))
        
        return {
            "distance_km": round(distance_m / 1000, 2),
            "duration_min": round(duration_s / 60, 2),
        }

    async def get_dist_matrix(
        self, 
        origins: List[Tuple[float, float]], 
        destinations: List[Tuple[float, float]], 
        transport: str
    ) -> List[Dict[str, float]]:
        """
        Compute a distance matrix using the 2GIS Distance Matrix API.
        
        Args:
            origins: List of (longitude, latitude) tuples.
            destinations: List of (longitude, latitude) tuples.
            transport: The mode of transport.
            
        Returns:
            List of dictionaries with distance_km and duration_min for each pair.
        """
        points = []
        for lon, lat in origins:
            points.append({"x": lon, "y": lat})
            
        sources = list(range(len(origins)))
        
        for lon, lat in destinations:
            points.append({"x": lon, "y": lat})
            
        targets = list(range(len(origins), len(origins) + len(destinations)))
        
        payload = {
            "points": points,
            "sources": sources,
            "targets": targets,
            "transport": transport,
            "key": self.api_key,
        }
        
        data = await self._request("POST", self.DIST_MATRIX_URL, json=payload)
        
        output_routes = []
        routes = data.get("routes", [])
        for route in routes:
            distance_m = float(route.get("distance", 0))
            duration_s = float(route.get("duration", 0))
            output_routes.append({
                "distance_km": round(distance_m / 1000, 2),
                "duration_min": round(duration_s / 60, 2),
            })
            
        return output_routes
