from datetime import datetime, timezone

from sqlalchemy import JSON, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Trip(Base):
    __tablename__ = "trips"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    budget: Mapped[str] = mapped_column(String(50), nullable=False)
    days: Mapped[int] = mapped_column(nullable=False)
    interests: Mapped[dict] = mapped_column(
        JSON, nullable=False, default=dict, server_default="{}"
    )
    travel_style: Mapped[str] = mapped_column(String(100), nullable=False)
    itinerary_json: Mapped[dict] = mapped_column(
        JSON, nullable=False, default=dict, server_default="{}"
    )
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
        index=True,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        default=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    user: Mapped["User | None"] = relationship("User", back_populates="trips")
    trip_messages: Mapped[list["TripMessage"]] = relationship(
        "TripMessage",
        back_populates="trip",
        cascade="all, delete-orphan",
        foreign_keys="TripMessage.trip_id",
    )
