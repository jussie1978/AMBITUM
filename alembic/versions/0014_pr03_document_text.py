"""PR-03 document-derived text persistence foundation.

Revision ID: 0014_pr03_document_text
Revises: 0011_pr02_smart_metadata
Create Date: 2026-10-05
"""

from alembic import op
import sqlalchemy as sa


revision = "0014_pr03_document_text"
down_revision = "0011_pr02_smart_metadata"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "document_text_extractions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("shared_case_id", sa.Integer(), sa.ForeignKey("shared_cases.id", ondelete="CASCADE"), nullable=False),
        sa.Column("shared_document_id", sa.Integer(), sa.ForeignKey("shared_documents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("source_sha256", sa.String(length=64), nullable=False),
        sa.Column("capability", sa.String(length=64), nullable=False),
        sa.Column("extraction_profile", sa.String(length=128), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("executor_type", sa.String(length=32), nullable=False),
        sa.Column("engine", sa.String(length=128), nullable=True),
        sa.Column("engine_version", sa.String(length=128), nullable=True),
        sa.Column("parameters_json", sa.Text(), nullable=True),
        sa.Column("error_code", sa.String(length=64), nullable=True),
        sa.Column("error_detail", sa.Text(), nullable=True),
        sa.Column("created_by_operator_id", sa.Integer(), nullable=True),
        sa.Column("created_by_username", sa.String(length=128), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("capability = 'document.extract_text'", name="ck_document_text_extractions_capability"),
        sa.CheckConstraint("status IN ('processing', 'ready', 'failed')", name="ck_document_text_extractions_status"),
        sa.CheckConstraint("executor_type IN ('native', 'ocr', 'vlm')", name="ck_document_text_extractions_executor_type"),
    )
    op.create_index("ix_document_text_extractions_shared_case_id", "document_text_extractions", ["shared_case_id"])
    op.create_index("ix_document_text_extractions_shared_document_id", "document_text_extractions", ["shared_document_id"])
    op.create_index(
        "ix_document_text_extractions_reuse_lookup",
        "document_text_extractions",
        ["shared_document_id", "source_sha256", "extraction_profile", "status"],
    )
    op.create_table(
        "document_text_pages",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("extraction_id", sa.Integer(), sa.ForeignKey("document_text_extractions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("page_number", sa.Integer(), nullable=False),
        sa.Column("raw_text", sa.Text(), nullable=False),
        sa.Column("reviewed_text", sa.Text(), nullable=True),
        sa.Column("reviewed_by_operator_id", sa.Integer(), nullable=True),
        sa.Column("reviewed_by_username", sa.String(length=128), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("page_number >= 1", name="ck_document_text_pages_page_number"),
        sa.UniqueConstraint("extraction_id", "page_number", name="uq_document_text_pages_extraction_page"),
    )


def downgrade() -> None:
    op.drop_table("document_text_pages")
    op.drop_table("document_text_extractions")
