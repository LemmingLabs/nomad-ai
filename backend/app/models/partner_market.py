from sqlalchemy import Boolean, JSON, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class PartnerMarket(Base):
    """Operational readiness and submission policy for a business market."""

    __tablename__ = "partner_markets"

    country_code: Mapped[str] = mapped_column(String(2), primary_key=True)
    country_name: Mapped[str] = mapped_column(String(120), nullable=False)
    readiness_status: Mapped[str] = mapped_column(
        String(16), nullable=False, default="closed", server_default=text("'closed'")
    )
    operating_languages: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    required_business_fields: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    onboarding_guidance: Mapped[str] = mapped_column(Text, nullable=False, default="")
    admin_guidance: Mapped[str] = mapped_column(Text, nullable=False, default="")
    operational_checklist: Mapped[dict[str, bool]] = mapped_column(JSON, nullable=False)
    is_legacy_baseline: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=text("false")
    )
