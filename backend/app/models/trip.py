from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Trip(Base):
    __tablename__ = "trips"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    budget: Mapped[str] = mapped_column(String(50), nullable=False)
    days: Mapped[int] = mapped_column(nullable=False)
    interests: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    travel_style: Mapped[str] = mapped_column(String(100), nullable=False)
    itinerary_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        default=lambda: datetime.now(timezone.utc),
    )

    user: Mapped["User | None"] = relationship(
        "User",
        back_populates="trips",
    )
    trip_messages: Mapped[list["TripMessage"]] = relationship(
        "TripMessage",
        back_populates="trip",
        cascade="all, delete-orphan",
    )