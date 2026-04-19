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
        summary = updated_itinerary.get("summary")
        if not isinstance(summary, str) or not summary.strip():
            summary = current_itinerary.get("summary", "")

        days = updated_itinerary.get("days")
        if not isinstance(days, list):
            days = current_itinerary.get("days", [])

        interests = updated_itinerary.get("interests", current_itinerary.get("interests", []))
        travel_style = updated_itinerary.get("travel_style", current_itinerary.get("travel_style", ""))

        return {
            "summary": summary,
            "days": days,
            "total_days": len(days),
            "interests": interests,
            "travel_style": travel_style,
        }

    def continue_trip(
        self, trip: Trip, user_content: str
    ) -> tuple[TripMessage, dict | None]:
        try:
            self.repo.create_message(trip_id=trip.id, role="user", content=user_content)

            history = self.repo.get_all_trip_messages(trip_id=trip.id)
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
                trip.itinerary_json = enriched_itinerary
                updated_itinerary = enriched_itinerary
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
