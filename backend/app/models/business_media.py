from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import DateTime, Enum as SqlEnum, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class BusinessMediaType(str, Enum):
    IMAGE = "image"
    LOGO = "logo"


class BusinessMedia(Base):
    __tablename__ = "business_media"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    business_id: Mapped[int] = mapped_column(
        ForeignKey("businesses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    type: Mapped[BusinessMediaType] = mapped_column(
        SqlEnum(BusinessMediaType, native_enum=False),
        nullable=False,
        index=True,
    )
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )

    business: Mapped["Business"] = relationship(
        "Business",
        back_populates="media",
    )

