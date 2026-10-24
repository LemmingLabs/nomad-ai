"""add explicit trip destination context

Revision ID: 41b97b5d2a1f
Revises: 7c0aef1d5d4e
Create Date: 2026-10-24
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "41b97b5d2a1f"
down_revision: Union[str, Sequence[str], None] = "7c0aef1d5d4e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "trips",
        sa.Column("country_code", sa.String(length=2), server_default="KG", nullable=False),
    )
    op.add_column(
        "trips",
        sa.Column("destination_id", sa.String(length=64), server_default="kg", nullable=False),
    )
    op.add_column(
        "trips",
        sa.Column("destination_name", sa.String(length=120), server_default="Kyrgyzstan", nullable=False),
    )
    op.create_index(op.f("ix_trips_country_code"), "trips", ["country_code"], unique=False)
    op.create_index(op.f("ix_trips_destination_id"), "trips", ["destination_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_trips_destination_id"), table_name="trips")
    op.drop_index(op.f("ix_trips_country_code"), table_name="trips")
    op.drop_column("trips", "destination_name")
    op.drop_column("trips", "destination_id")
    op.drop_column("trips", "country_code")
