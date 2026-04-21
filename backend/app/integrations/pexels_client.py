import logging
import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)

class PexelsClient:
    def __init__(self):
        self.api_key = settings.PEXELS_API_KEY
        self.base_url = "https://api.pexels.com/v1/search"

    def search_photo(self, query: str) -> dict | None:
        if not self.api_key:
            return None

        headers = {"Authorization": self.api_key}
        params = {
            "query": query,
            "per_page": 3,
            "orientation": "landscape"
        }

        try:
            with httpx.Client() as client:
                response = client.get(self.base_url, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()
                
                photos = data.get("photos", [])
                if not photos:
                    return None
                    
                best_photo = photos[0]
                
                return {
                    "source": "pexels",
                    "photo_id": str(best_photo.get("id")),
                    "url": best_photo.get("src", {}).get("large") or best_photo.get("url"),
                    "photographer": best_photo.get("photographer"),
                    "photographer_url": best_photo.get("photographer_url"),
                    "alt": best_photo.get("alt", ""),
                    "search_query": query
                }
        except Exception as e:
            logger.warning(f"PexelsClient failed resolving image: {e}")
            return None
