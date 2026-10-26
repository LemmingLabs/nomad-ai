from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text, func, text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class KnowledgeSource(Base):
    __tablename__ = "knowledge_sources"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    owner: Mapped[str | None] = mapped_column(String(200), nullable=True)
    source_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    terms_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    license_basis: Mapped[str] = mapped_column(String(200), nullable=False)
    allowed_use: Mapped[str] = mapped_column(Text, nullable=False)
    attribution_text: Mapped[str] = mapped_column(String(1000), nullable=False)
    geographic_scope: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    freshness_days: Mapped[int] = mapped_column(Integer, nullable=False)
    approval_evidence: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(16), nullable=False, default="pending", server_default=text("'pending'")
    )
    approved_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
        onupdate=func.now(), default=lambda: datetime.now(timezone.utc),
    )
