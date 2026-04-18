from sqlalchemy.orm import Session

from app.models.trip_message import TripMessage


class TripMessageRepository:
    """Database-only operations for trip messages."""

    def __init__(self, db: Session):
        self.db = db

    def create_message(self, trip_id: int, role: str, content: str) -> TripMessage:
        message = TripMessage(trip_id=trip_id, role=role, content=content)
        self.db.add(message)
        self.db.flush()
        return message
    def get_trip_messages(self, trip_id: int) -> list[TripMessage]:
        return (
            self.db.query(TripMessage)
            .filter(TripMessage.trip_id == trip_id)
            .order_by(TripMessage.created_at.asc())
            .all()
        )
