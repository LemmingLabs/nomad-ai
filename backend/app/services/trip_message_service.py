from app.models.trip import Trip
from app.models.trip_message import TripMessage
from app.repositories.trip_message_repository import TripMessageRepository
from app.services.ai_service import AIService


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

    def continue_trip(
        self, trip: Trip, user_content: str
    ) -> tuple[TripMessage, dict | None]:
        self.repo.create_message(trip_id=trip.id, role="user", content=user_content)

        history = self.repo.get_trip_messages(trip_id=trip.id)
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
            trip.itinerary_json = updated_itinerary
            self.db.add(trip)
            self.db.commit()
            self.db.refresh(trip)

        return assistant_message, updated_itinerary
