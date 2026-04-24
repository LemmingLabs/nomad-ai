from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import DateTime, Enum as SqlEnum, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class SponsoredPlaceMediaType(str, Enum):
    IMAGE = "image"
    COVER = "cover"


class SponsoredPlaceMedia(Base):
    __tablename__ = "sponsored_place_media"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    sponsored_place_id: Mapped[int] = mapped_column(
        ForeignKey("sponsored_places.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    type: Mapped[SponsoredPlaceMediaType] = mapped_column(
        SqlEnum(SponsoredPlaceMediaType, native_enum=False),
        nullable=False,
        index=True,
    )
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )

    sponsored_place: Mapped["SponsoredPlace"] = relationship(
        "SponsoredPlace",
        back_populates="media",
    )
