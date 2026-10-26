"""add partner market readiness and location verification

Revision ID: 6a1f09c4b8d2
Revises: 88c52d13a321
Create Date: 2026-10-26
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "6a1f09c4b8d2"
down_revision: Union[str, Sequence[str], None] = "88c52d13a321"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "partner_markets",
        sa.Column("country_code", sa.String(length=2), nullable=False),
        sa.Column("country_name", sa.String(length=120), nullable=False),
        sa.Column("readiness_status", sa.String(length=16), server_default="closed", nullable=False),
        sa.Column("operating_languages", sa.JSON(), nullable=False),
        sa.Column("required_business_fields", sa.JSON(), nullable=False),
        sa.Column("onboarding_guidance", sa.Text(), server_default="", nullable=False),
        sa.Column("admin_guidance", sa.Text(), server_default="", nullable=False),
        sa.Column("operational_checklist", sa.JSON(), nullable=False),
        sa.Column("is_legacy_baseline", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.PrimaryKeyConstraint("country_code", name=op.f("pk_partner_markets")),
        sa.CheckConstraint(
            "readiness_status in ('closed', 'pilot', 'open')",
            name=op.f("ck_partner_markets_valid_readiness_status"),
        ),
    )
    op.execute(
        """INSERT INTO partner_markets (
            country_code, country_name, readiness_status, operating_languages,
            required_business_fields, onboarding_guidance, admin_guidance,
            operational_checklist, is_legacy_baseline
        ) VALUES (
            'KG', 'Kyrgyzstan', 'open', '[\"en\"]'::json,
            '[\"name\"]'::json,
            'Provide a verified business location in Kyrgyzstan.',
            'Confirm the business identity, location, and advertising claims before approval.',
            '{\"support_owner\": false, \"support_language\": false,
              \"business_verification\": false, \"advertising_review\": false,
              \"payment_capability\": false, \"privacy_review\": false,
              \"escalation_owner\": false}'::json,
            true
        )"""
    )
    op.add_column(
        "sponsored_places",
        sa.Column("operating_language", sa.String(length=12), server_default="en", nullable=False),
    )
    op.add_column(
        "sponsored_places",
        sa.Column("location_verified", sa.Boolean(), server_default=sa.text("false"), nullable=False),
    )


def downgrade() -> None:
    op.drop_column("sponsored_places", "location_verified")
    op.drop_column("sponsored_places", "operating_language")
    op.drop_table("partner_markets")
