from app.models.trip import Trip
from app.models.trip_message import TripMessage
from app.repositories.trip_message_repository import TripMessageRepository
from app.services.ai_service import AIService
from app.services.catalog_service import CatalogService


class TripMessageService:
    def __init__(
        self,
        db,
        ai_service: AIService | None = None,
        repository: TripMessageRepository | None = None,
    ):
        self.db = db
        self.repo = repository or TripMessageRepository(db)
        self.ai_service = ai_service or AIService()

    def _merge_itinerary(
        self,
        current_itinerary: dict,
        updated_itinerary: dict,
    ) -> dict:
        merged = dict(current_itinerary) if current_itinerary else {}
        merged.update(updated_itinerary)
        
        allowed_keys = {"summary", "days", "total_days", "interests", "travel_style"}
        merged = {k: v for k, v in merged.items() if k in allowed_keys}
        
        mapping = {
            "ala-archa": "Bishkek",
            "chuy": "Bishkek",
            "jeti-oguz": "Karakol",
            "jeti oguz": "Karakol",
            "altyn arashan": "Karakol",
            "altyn-arashan": "Karakol",
            "cholpon-ata": "Cholpon-Ata",
            "bosteri": "Cholpon-Ata",
            "suusamyr": "Bishkek",
            "son-kul": "Kochkor",
            "tash-rabat": "Naryn"
        }

        if "days" in merged and isinstance(merged["days"], list):
            for day in merged["days"]:
                if isinstance(day, dict):
                    city = str(day.get("city", "")).strip().lower()
                    if city in mapping:
                        day["city"] = mapping[city]

        return merged

    def continue_trip(
        self, trip: Trip, user_content: str
    ) -> tuple[TripMessage, dict | None]:
        try:
            self.repo.create_message(trip_id=trip.id, role="user", content=user_content)

            history, _ = self.repo.get_trip_messages(trip_id=trip.id)
            assistant_text, updated_itinerary = self.ai_service.continue_trip(
                history_messages=history,
                user_message=user_content,
                current_itinerary=trip.itinerary_json,
            )

            assistant_message = self.repo.create_message(
                trip_id=trip.id,
                role="assistant",
                content=assistant_text,
            )

            if updated_itinerary is not None:
                catalog_service = CatalogService(self.db)
                merged_itinerary = self._merge_itinerary(
                    current_itinerary=trip.itinerary_json,
                    updated_itinerary=updated_itinerary,
                )
                enriched_itinerary = catalog_service.enrich_itinerary_with_catalog(
                    merged_itinerary,
                    trip.budget
                )
                
                from app.utils.async_runner import run_async
                from app.services.routing_service import RoutingService
                try:
                    enriched_itinerary = run_async(RoutingService().enrich_from_itinerary_json(enriched_itinerary))
                except Exception as exc:
                    print(f"Routing enrichment failed on update: {exc}")
                    
                from app.services.image_enrichment_service import ImageEnrichmentService
                try:
                    enriched_itinerary = ImageEnrichmentService().enrich_trip_with_images(enriched_itinerary)
                except Exception as exc:
                    print(f"Image enrichment failed on update: {exc}")
                    
                cleaned_itinerary = enriched_itinerary
                
                trip.itinerary_json = cleaned_itinerary
                updated_itinerary = cleaned_itinerary
                self.db.add(trip)

            self.db.commit()
            self.db.refresh(assistant_message)
            return assistant_message, updated_itinerary

        except Exception:
            self.db.rollback()
            raise

    def get_trip_messages(
        self, trip: Trip, limit: int = 50, offset: int = 0
    ) -> tuple[list[TripMessage], int]:
        return self.repo.get_trip_messages(trip.id, limit=limit, offset=offset)
