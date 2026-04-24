"""add sponsored place media

Revision ID: 7c0aef1d5d4e
Revises: 9c9850d9a88b
Create Date: 2026-04-24 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7c0aef1d5d4e"
down_revision: Union[str, Sequence[str], None] = "9c9850d9a88b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "sponsored_place_media",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("sponsored_place_id", sa.Integer(), nullable=False),
        sa.Column("type", sa.Enum("IMAGE", "COVER", name="sponsoredplacemediatype", native_enum=False), nullable=False),
        sa.Column("url", sa.String(length=500), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("content_type", sa.String(length=100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["sponsored_place_id"], ["sponsored_places.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_sponsored_place_media_id"), "sponsored_place_media", ["id"], unique=False)
    op.create_index(
        op.f("ix_sponsored_place_media_sponsored_place_id"),
        "sponsored_place_media",
        ["sponsored_place_id"],
        unique=False,
    )
    op.create_index(op.f("ix_sponsored_place_media_type"), "sponsored_place_media", ["type"], unique=False)
    op.create_index(
        op.f("ix_sponsored_place_media_created_at"),
        "sponsored_place_media",
        ["created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_sponsored_place_media_created_at"), table_name="sponsored_place_media")
    op.drop_index(op.f("ix_sponsored_place_media_type"), table_name="sponsored_place_media")
    op.drop_index(op.f("ix_sponsored_place_media_sponsored_place_id"), table_name="sponsored_place_media")
    op.drop_index(op.f("ix_sponsored_place_media_id"), table_name="sponsored_place_media")
    op.drop_table("sponsored_place_media")
