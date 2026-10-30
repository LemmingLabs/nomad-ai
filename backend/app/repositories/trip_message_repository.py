from sqlalchemy import and_, or_
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
    def get_trip_messages(
        self, trip_id: int, limit: int | None = None, offset: int = 0
    ) -> tuple[list[TripMessage], int]:
        query = self.db.query(TripMessage).filter(TripMessage.trip_id == trip_id)
        total = query.count()
        query = query.order_by(TripMessage.created_at.asc(), TripMessage.id.asc()).offset(offset)
        if limit is not None:
            query = query.limit(limit)
        return query.all(), total

    def get_recent_messages(
        self, trip_id: int, limit: int = 50, before_id: int | None = None
    ) -> tuple[list[TripMessage], int, bool]:
        query = self.db.query(TripMessage).filter(TripMessage.trip_id == trip_id)
        total = query.count()
        if before_id is not None:
            anchor = query.filter(TripMessage.id == before_id).first()
            if anchor is None:
                raise ValueError("Message cursor not found")
            query = query.filter(or_(
                TripMessage.created_at < anchor.created_at,
                and_(TripMessage.created_at == anchor.created_at, TripMessage.id < anchor.id),
            ))
        page = query.order_by(TripMessage.created_at.desc(), TripMessage.id.desc()).limit(limit + 1).all()
        return list(reversed(page[:limit])), total, len(page) > limit



    def get_last_trip_message(self, trip_id: int) -> TripMessage | None:
        return (
            self.db.query(TripMessage)
            .filter(TripMessage.trip_id == trip_id)
            .order_by(TripMessage.created_at.desc(), TripMessage.id.desc())
            .first()
        )
