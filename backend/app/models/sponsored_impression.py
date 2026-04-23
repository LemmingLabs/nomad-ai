from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class SponsoredImpression(Base):
    __tablename__ = "sponsored_impressions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    trip_id: Mapped[int | None] = mapped_column(
        ForeignKey("trips.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    sponsored_place_id: Mapped[int] = mapped_column(
        ForeignKey("sponsored_places.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    business_id: Mapped[int] = mapped_column(
        ForeignKey("businesses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    day_number: Mapped[int | None] = mapped_column(nullable=True, index=True)
    city: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )

    trip: Mapped["Trip | None"] = relationship("Trip")
    sponsored_place: Mapped["SponsoredPlace"] = relationship("SponsoredPlace")
    business: Mapped["Business"] = relationship("Business")

