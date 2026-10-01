from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Integer, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class AssetSmartMetadata(Base):
    __tablename__ = "asset_smart_metadata"
    __table_args__ = (
        CheckConstraint(
            "kind IN ('target', 'topic', 'tag', 'section_hint', 'event_ref', "
            "'relevance', 'source_kind', 'validation_status')",
            name="ck_asset_smart_metadata_kind",
        ),
        CheckConstraint(
            "provenance IN ('human_confirmed', 'ai_suggested', 'system_derived')",
            name="ck_asset_smart_metadata_provenance",
        ),
        CheckConstraint(
            "length(value_text) BETWEEN 1 AND 256",
            name="ck_asset_smart_metadata_value_length",
        ),
        Index(
            "uq_asset_smart_metadata_unlinked",
            "shared_document_id",
            "kind",
            "value_text",
            unique=True,
            sqlite_where=text("linked_person_id IS NULL"),
        ),
        Index(
            "uq_asset_smart_metadata_linked",
            "shared_document_id",
            "kind",
            "value_text",
            "linked_person_id",
            unique=True,
            sqlite_where=text("linked_person_id IS NOT NULL"),
        ),
        Index(
            "ix_asset_smart_metadata_case_kind_value",
            "shared_case_id",
            "kind",
            "value_text",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    shared_case_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("shared_cases.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    shared_document_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("shared_documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    kind: Mapped[str] = mapped_column(String(32), nullable=False)
    value_text: Mapped[str] = mapped_column(String(256), nullable=False)
    linked_person_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("shared_persons.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    provenance: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by_operator_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_by_username: Mapped[str] = mapped_column(String(128), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow, nullable=False,
    )

    case = relationship("SharedCase")
    document = relationship("SharedDocument")
    linked_person = relationship("SharedPerson")
