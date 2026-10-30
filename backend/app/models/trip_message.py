from datetime import datetime, timezone

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class TripMessage(Base):
    __tablename__ = "trip_messages"
    __table_args__ = (UniqueConstraint("trip_id", "request_key", name="uq_trip_messages_trip_request_key"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    trip_id: Mapped[int] = mapped_column(
        ForeignKey("trips.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    request_key: Mapped[str | None] = mapped_column(String(36), nullable=True)
    request_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
        index=True,
        default=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    trip: Mapped["Trip"] = relationship(
        "Trip", back_populates="trip_messages", foreign_keys="TripMessage.trip_id"
    )
