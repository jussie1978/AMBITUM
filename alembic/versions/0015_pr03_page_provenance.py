"""PR-03 page-level extraction provenance.

Revision ID: 0015_pr03_page_provenance
Revises: 0014_pr03_document_text
Create Date: 2026-10-06
"""

from alembic import op
import sqlalchemy as sa


revision = "0015_pr03_page_provenance"
down_revision = "0014_pr03_document_text"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("document_text_extractions") as batch_op:
        batch_op.drop_constraint(
            "ck_document_text_extractions_executor_type", type_="check"
        )
        batch_op.create_check_constraint(
            "ck_document_text_extractions_executor_type",
            "executor_type IN ('native', 'ocr', 'vlm', 'mixed')",
        )

    with op.batch_alter_table("document_text_pages") as batch_op:
        batch_op.add_column(sa.Column("executor_type", sa.String(length=32), nullable=True))
        batch_op.add_column(sa.Column("engine", sa.String(length=128), nullable=True))
        batch_op.add_column(sa.Column("engine_version", sa.String(length=128), nullable=True))
        batch_op.add_column(sa.Column("status", sa.String(length=32), nullable=True))
        batch_op.add_column(sa.Column("error_code", sa.String(length=64), nullable=True))
        batch_op.add_column(sa.Column("error_detail", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("fallback_candidate", sa.String(length=32), nullable=True))

    op.execute(
        """
        UPDATE document_text_pages
        SET executor_type = (
                SELECT executor_type
                FROM document_text_extractions
                WHERE document_text_extractions.id = document_text_pages.extraction_id
            ),
            engine = (
                SELECT engine
                FROM document_text_extractions
                WHERE document_text_extractions.id = document_text_pages.extraction_id
            ),
            engine_version = (
                SELECT engine_version
                FROM document_text_extractions
                WHERE document_text_extractions.id = document_text_pages.extraction_id
            ),
            status = CASE (
                SELECT status
                FROM document_text_extractions
                WHERE document_text_extractions.id = document_text_pages.extraction_id
            ) WHEN 'ready' THEN 'ready' ELSE 'failed' END
        """
    )

    with op.batch_alter_table("document_text_pages") as batch_op:
        batch_op.alter_column(
            "executor_type", existing_type=sa.String(length=32), nullable=False
        )
        batch_op.alter_column(
            "status", existing_type=sa.String(length=32), nullable=False
        )
        batch_op.create_check_constraint(
            "ck_document_text_pages_executor_type",
            "executor_type IN ('native', 'ocr', 'vlm')",
        )
        batch_op.create_check_constraint(
            "ck_document_text_pages_status",
            "status IN ('ready', 'failed')",
        )


def downgrade() -> None:
    connection = op.get_bind()
    mixed_count = connection.execute(
        sa.text(
            "SELECT COUNT(*) FROM document_text_extractions "
            "WHERE executor_type = 'mixed'"
        )
    ).scalar_one()
    if mixed_count:
        raise RuntimeError(
            "Cannot downgrade page provenance while mixed extractions exist."
        )

    with op.batch_alter_table("document_text_pages") as batch_op:
        batch_op.drop_constraint("ck_document_text_pages_status", type_="check")
        batch_op.drop_constraint(
            "ck_document_text_pages_executor_type", type_="check"
        )
        batch_op.drop_column("fallback_candidate")
        batch_op.drop_column("error_detail")
        batch_op.drop_column("error_code")
        batch_op.drop_column("status")
        batch_op.drop_column("engine_version")
        batch_op.drop_column("engine")
        batch_op.drop_column("executor_type")

    with op.batch_alter_table("document_text_extractions") as batch_op:
        batch_op.drop_constraint(
            "ck_document_text_extractions_executor_type", type_="check"
        )
        batch_op.create_check_constraint(
            "ck_document_text_extractions_executor_type",
            "executor_type IN ('native', 'ocr', 'vlm')",
        )
