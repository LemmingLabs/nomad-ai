import logging
from app.integrations.pexels_client import PexelsClient

logger = logging.getLogger(__name__)

PHOTO_QUERY_OVERRIDES = {
    "State Historical Museum": "State Historical Museum Bishkek Kyrgyzstan",
    "Issyk-Kul Lakefront": "Issyk Kul lake Cholpon-Ata Kyrgyzstan",
    "Jeti-Oguz Gorge": "Jeti-Oguz Gorge Karakol Kyrgyzstan",
    "Ala-Archa National Park": "Ala-Archa National Park Kyrgyzstan",
    "Osh Bazaar": "Osh Bazaar Bishkek Kyrgyzstan",
    "Ala-Too Square": "Ala-Too Square Bishkek Kyrgyzstan"
}

class ImageEnrichmentService:
    def __init__(self):
        self.client = PexelsClient()

    def enrich_trip_with_images(self, itinerary_json: dict) -> dict:
        days = itinerary_json.get("days", [])
        if not isinstance(days, list):
            return itinerary_json

        count = 0
        MAX_IMAGES_PER_TRIP = 3
        used_photo_ids = set()

        for day in days:
            if not isinstance(day, dict) or "location" not in day:
                continue
                
            if "images" in day and day["images"]: 
                continue
                
            if count >= MAX_IMAGES_PER_TRIP:
                break
                
            image_data = self._fetch_image_for_day(day, itinerary_json, used_photo_ids)
            if image_data:
                day["images"] = {
                    "hero": image_data,
                    "gallery": []
                }
                count += 1
        return itinerary_json

    def _fetch_image_for_day(self, day: dict, itinerary: dict, used_ids: set) -> dict | None:
        queries = self._build_search_queries(day, itinerary)
        
        for q in queries:
            result = self.client.search_photo(q)
            if result and result["photo_id"] not in used_ids:
                used_ids.add(result["photo_id"])
                return result
        return None

    def _build_search_queries(self, day: dict, itinerary: dict) -> list[str]:
        queries = []
        routing_loc = day.get("routing_location")
        loc = day.get("location")
        city = day.get("city", "")
        
        if loc and loc in PHOTO_QUERY_OVERRIDES:
            queries.append(PHOTO_QUERY_OVERRIDES[loc])

        suffix = "Kyrgyzstan"
        
        if routing_loc:
            queries.append(f"{routing_loc} {city} {suffix}".strip())
            
        if loc:
            queries.append(f"{loc} {city} {suffix}".strip())
            
        interests = itinerary.get("interests", [])
        themes = ["mountains", "nature", "lake", "culture", "city", "food"]
        
        theme_added = False
        for interest in interests:
            if interest.lower() in themes:
                if city:
                    queries.append(f"{interest} {city} {suffix}".strip())
                else:
                    queries.append(f"{interest} {suffix}".strip())
                theme_added = True
                break
                
        if not theme_added:
            if city:
                queries.append(f"{city} {suffix}".strip())
            else:
                queries.append("Kyrgyzstan nature".strip())
        
        clean_queries = []
        for q in queries:
            cleaned = " ".join(q.split())
            if cleaned and cleaned not in clean_queries:
                clean_queries.append(cleaned)
                
        return clean_queries
