"""Specialized persistence models for document-derived text."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class DocumentTextExtraction(Base):
    __tablename__ = "document_text_extractions"
    __table_args__ = (
        CheckConstraint(
            "capability = 'document.extract_text'",
            name="ck_document_text_extractions_capability",
        ),
        CheckConstraint(
            "status IN ('processing', 'ready', 'failed')",
            name="ck_document_text_extractions_status",
        ),
        CheckConstraint(
            "executor_type IN ('native', 'ocr', 'vlm', 'mixed')",
            name="ck_document_text_extractions_executor_type",
        ),
        Index("ix_document_text_extractions_shared_case_id", "shared_case_id"),
        Index("ix_document_text_extractions_shared_document_id", "shared_document_id"),
        Index(
            "ix_document_text_extractions_reuse_lookup",
            "shared_document_id",
            "source_sha256",
            "extraction_profile",
            "status",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    shared_case_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("shared_cases.id", ondelete="CASCADE"),
        nullable=False,
    )
    shared_document_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("shared_documents.id", ondelete="CASCADE"),
        nullable=False,
    )
    source_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    capability: Mapped[str] = mapped_column(String(64), nullable=False)
    extraction_profile: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    executor_type: Mapped[str] = mapped_column(String(32), nullable=False)
    engine: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    engine_version: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    parameters_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error_code: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    error_detail: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_by_operator_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_by_username: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    pages: Mapped[list["DocumentTextPage"]] = relationship(
        back_populates="extraction",
        cascade="all, delete-orphan",
        order_by="DocumentTextPage.page_number",
    )


class DocumentTextPage(Base):
    __tablename__ = "document_text_pages"
    __table_args__ = (
        CheckConstraint("page_number >= 1", name="ck_document_text_pages_page_number"),
        CheckConstraint(
            "executor_type IN ('native', 'ocr', 'vlm')",
            name="ck_document_text_pages_executor_type",
        ),
        CheckConstraint(
            "status IN ('ready', 'failed')",
            name="ck_document_text_pages_status",
        ),
        UniqueConstraint(
            "extraction_id",
            "page_number",
            name="uq_document_text_pages_extraction_page",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    extraction_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("document_text_extractions.id", ondelete="CASCADE"),
        nullable=False,
    )
    page_number: Mapped[int] = mapped_column(Integer, nullable=False)
    executor_type: Mapped[str] = mapped_column(String(32), nullable=False)
    engine: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    engine_version: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    error_code: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    error_detail: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    fallback_candidate: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    reviewed_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reviewed_by_operator_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    reviewed_by_username: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    extraction: Mapped[DocumentTextExtraction] = relationship(back_populates="pages")
