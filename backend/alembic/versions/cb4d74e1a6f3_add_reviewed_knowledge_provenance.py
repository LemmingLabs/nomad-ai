"""add reviewed knowledge provenance lifecycle

Revision ID: cb4d74e1a6f3
Revises: 6a1f09c4b8d2
Create Date: 2026-10-26
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "cb4d74e1a6f3"
down_revision: Union[str, Sequence[str], None] = "6a1f09c4b8d2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "knowledge_sources",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("owner", sa.String(length=200), nullable=True),
        sa.Column("source_url", sa.String(length=1000), nullable=False),
        sa.Column("terms_url", sa.String(length=1000), nullable=False),
        sa.Column("license_basis", sa.String(length=200), nullable=False),
        sa.Column("allowed_use", sa.Text(), nullable=False),
        sa.Column("attribution_text", sa.String(length=1000), nullable=False),
        sa.Column("geographic_scope", sa.JSON(), nullable=False),
        sa.Column("freshness_days", sa.Integer(), nullable=False),
        sa.Column("approval_evidence", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=16), server_default="pending", nullable=False),
        sa.Column("approved_by", sa.Integer(), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("status in ('pending', 'approved', 'rejected', 'withdrawn')", name=op.f("ck_knowledge_sources_valid_status")),
        sa.CheckConstraint("freshness_days > 0", name=op.f("ck_knowledge_sources_positive_freshness")),
        sa.ForeignKeyConstraint(["approved_by"], ["users.id"], ondelete="SET NULL", name=op.f("fk_knowledge_sources_approved_by_users")),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL", name=op.f("fk_knowledge_sources_created_by_users")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_knowledge_sources")),
    )
    op.create_index(op.f("ix_knowledge_sources_id"), "knowledge_sources", ["id"], unique=False)

    op.create_table(
        "knowledge_facts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("source_id", sa.Integer(), nullable=False),
        sa.Column("subject_type", sa.String(length=16), nullable=False),
        sa.Column("subject_id", sa.String(length=500), nullable=False),
        sa.Column("country_code", sa.String(length=2), nullable=False),
        sa.Column("fact_type", sa.String(length=80), nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column("source_record_id", sa.String(length=500), nullable=True),
        sa.Column("source_record_url", sa.String(length=1000), nullable=True),
        sa.Column("checked_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("freshness_days", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=16), server_default="pending", nullable=False),
        sa.Column("review_notes", sa.Text(), nullable=True),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("reviewed_by", sa.Integer(), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("subject_type in ('place', 'route')", name=op.f("ck_knowledge_facts_valid_subject_type")),
        sa.CheckConstraint("status in ('pending', 'approved', 'rejected', 'withdrawn')", name=op.f("ck_knowledge_facts_valid_status")),
        sa.CheckConstraint("freshness_days is null or freshness_days > 0", name=op.f("ck_knowledge_facts_positive_freshness")),
        sa.ForeignKeyConstraint(["source_id"], ["knowledge_sources.id"], ondelete="RESTRICT", name=op.f("fk_knowledge_facts_source_id_knowledge_sources")),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL", name=op.f("fk_knowledge_facts_created_by_users")),
        sa.ForeignKeyConstraint(["reviewed_by"], ["users.id"], ondelete="SET NULL", name=op.f("fk_knowledge_facts_reviewed_by_users")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_knowledge_facts")),
    )
    for column in ("id", "source_id", "subject_type", "subject_id", "country_code", "fact_type"):
        op.create_index(op.f(f"ix_knowledge_facts_{column}"), "knowledge_facts", [column], unique=False)

    op.create_table(
        "knowledge_fact_audit",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("fact_id", sa.Integer(), nullable=False),
        sa.Column("actor_id", sa.Integer(), nullable=True),
        sa.Column("action", sa.String(length=24), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("before_state", sa.JSON(), nullable=True),
        sa.Column("after_state", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["fact_id"], ["knowledge_facts.id"], ondelete="CASCADE", name=op.f("fk_knowledge_fact_audit_fact_id_knowledge_facts")),
        sa.ForeignKeyConstraint(["actor_id"], ["users.id"], ondelete="SET NULL", name=op.f("fk_knowledge_fact_audit_actor_id_users")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_knowledge_fact_audit")),
    )
    op.create_index(op.f("ix_knowledge_fact_audit_id"), "knowledge_fact_audit", ["id"], unique=False)
    op.create_index(op.f("ix_knowledge_fact_audit_fact_id"), "knowledge_fact_audit", ["fact_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_knowledge_fact_audit_fact_id"), table_name="knowledge_fact_audit")
    op.drop_index(op.f("ix_knowledge_fact_audit_id"), table_name="knowledge_fact_audit")
    op.drop_table("knowledge_fact_audit")
    for column in ("fact_type", "country_code", "subject_id", "subject_type", "source_id", "id"):
        op.drop_index(op.f(f"ix_knowledge_facts_{column}"), table_name="knowledge_facts")
    op.drop_table("knowledge_facts")
    op.drop_index(op.f("ix_knowledge_sources_id"), table_name="knowledge_sources")
    op.drop_table("knowledge_sources")
