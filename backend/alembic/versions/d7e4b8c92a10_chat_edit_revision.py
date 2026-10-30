"""Prevent overlapping chat edits and support safe request retries.

Revision ID: d7e4b8c92a10
Revises: cb4d74e1a6f3
"""
from alembic import op
import sqlalchemy as sa

revision = "d7e4b8c92a10"
down_revision = "cb4d74e1a6f3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("trips", sa.Column("chat_revision", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("trip_messages", sa.Column("request_key", sa.String(36), nullable=True))
    op.add_column("trip_messages", sa.Column("request_hash", sa.String(64), nullable=True))
    op.create_unique_constraint("uq_trip_messages_trip_request_key", "trip_messages", ["trip_id", "request_key"])


def downgrade() -> None:
    op.drop_constraint("uq_trip_messages_trip_request_key", "trip_messages", type_="unique")
    op.drop_column("trip_messages", "request_hash")
    op.drop_column("trip_messages", "request_key")
    op.drop_column("trips", "chat_revision")
