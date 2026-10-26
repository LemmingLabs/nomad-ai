"""add country and region context to sponsored places

Revision ID: 88c52d13a321
Revises: 41b97b5d2a1f
Create Date: 2026-10-26
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "88c52d13a321"
down_revision: Union[str, Sequence[str], None] = "41b97b5d2a1f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "sponsored_places",
        sa.Column("country_code", sa.String(length=2), server_default="KG", nullable=False),
    )
    op.add_column(
        "sponsored_places",
        sa.Column("region", sa.String(length=120), nullable=True),
    )
    op.create_index(
        op.f("ix_sponsored_places_country_code"),
        "sponsored_places",
        ["country_code"],
        unique=False,
    )
    op.create_index(
        op.f("ix_sponsored_places_region"),
        "sponsored_places",
        ["region"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_sponsored_places_region"), table_name="sponsored_places")
    op.drop_index(op.f("ix_sponsored_places_country_code"), table_name="sponsored_places")
    op.drop_column("sponsored_places", "region")
    op.drop_column("sponsored_places", "country_code")
