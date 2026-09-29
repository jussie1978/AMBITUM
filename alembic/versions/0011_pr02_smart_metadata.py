"""PR-02 Smart Metadata for SharedDocument.

Revision ID: 0011_pr02_smart_metadata
Revises: 0010_ux03a_product_sections
Create Date: 2026-09-29
"""

from alembic import op
import sqlalchemy as sa


revision = "0011_pr02_smart_metadata"
down_revision = "0010_ux03a_product_sections"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "asset_smart_metadata",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "shared_case_id",
            sa.Integer(),
            sa.ForeignKey("shared_cases.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "shared_document_id",
            sa.Integer(),
            sa.ForeignKey("shared_documents.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("kind", sa.String(length=32), nullable=False),
        sa.Column("value_text", sa.String(length=256), nullable=False),
        sa.Column(
            "linked_person_id",
            sa.Integer(),
            sa.ForeignKey("shared_persons.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("provenance", sa.String(length=32), nullable=False),
        sa.Column("created_by_operator_id", sa.Integer(), nullable=True),
        sa.Column("created_by_username", sa.String(length=128), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "kind IN ('target', 'topic', 'tag', 'section_hint', 'event_ref', "
            "'relevance', 'source_kind', 'validation_status')",
            name="ck_asset_smart_metadata_kind",
        ),
        sa.CheckConstraint(
            "provenance IN ('human_confirmed', 'ai_suggested', 'system_derived')",
            name="ck_asset_smart_metadata_provenance",
        ),
        sa.CheckConstraint(
            "length(value_text) BETWEEN 1 AND 256",
            name="ck_asset_smart_metadata_value_length",
        ),
    )
    op.create_index(
        "ix_asset_smart_metadata_shared_case_id",
        "asset_smart_metadata",
        ["shared_case_id"],
    )
    op.create_index(
        "ix_asset_smart_metadata_shared_document_id",
        "asset_smart_metadata",
        ["shared_document_id"],
    )
    op.create_index(
        "ix_asset_smart_metadata_linked_person_id",
        "asset_smart_metadata",
        ["linked_person_id"],
    )
    op.create_index(
        "ix_asset_smart_metadata_case_kind_value",
        "asset_smart_metadata",
        ["shared_case_id", "kind", "value_text"],
    )
    op.create_index(
        "uq_asset_smart_metadata_unlinked",
        "asset_smart_metadata",
        ["shared_document_id", "kind", "value_text"],
        unique=True,
        sqlite_where=sa.text("linked_person_id IS NULL"),
    )
    op.create_index(
        "uq_asset_smart_metadata_linked",
        "asset_smart_metadata",
        ["shared_document_id", "kind", "value_text", "linked_person_id"],
        unique=True,
        sqlite_where=sa.text("linked_person_id IS NOT NULL"),
    )


def downgrade() -> None:
    op.drop_table("asset_smart_metadata")
