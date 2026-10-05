"""Domain and persistence helpers for ``document.extract_text``.

This module deliberately does not read files, choose executors, or own the
caller's transaction.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable, Mapping

from sqlalchemy.orm import Session, selectinload

from app.models.derived_content import DocumentTextExtraction, DocumentTextPage
from app.models.platea import SharedCase, SharedDocument


CAPABILITY = "document.extract_text"
VALID_STATUSES = frozenset({"processing", "ready", "failed"})
VALID_EXECUTOR_TYPES = frozenset({"native", "ocr", "vlm"})


class DocumentTextError(Exception):
    status_code = 422
    code = "validation_error"

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class DocumentTextNotFound(DocumentTextError):
    status_code = 404
    code = "not_found"


class DocumentTextSourceUnavailable(DocumentTextError):
    status_code = 409
    code = "source_unavailable"


def _validate_source_document(document: SharedDocument) -> str:
    if not document.storage_relpath:
        raise DocumentTextSourceUnavailable(
            "Documento não possui original físico disponível."
        )
    if not document.sha256:
        raise DocumentTextSourceUnavailable("Documento não possui SHA-256 canônico.")
    return document.sha256


def resolve_case(db: Session, case_ref: str) -> SharedCase:
    if not isinstance(case_ref, str) or not case_ref.strip():
        raise DocumentTextError("case_ref deve ser texto não vazio.")
    case = db.query(SharedCase).filter(SharedCase.case_ref == case_ref.strip()).first()
    if case is None:
        raise DocumentTextNotFound("Caso não encontrado.")
    return case


def resolve_source_document(
    db: Session, *, case_ref: str, document_id: int
) -> SharedDocument:
    if isinstance(document_id, bool) or not isinstance(document_id, int) or document_id <= 0:
        raise DocumentTextError(
            "document_id deve ser um inteiro positivo; caminhos de arquivo não são aceitos."
        )
    case = resolve_case(db, case_ref)
    document = db.query(SharedDocument).filter(
        SharedDocument.id == document_id,
        SharedDocument.shared_case_id == case.id,
    ).first()
    if document is None:
        raise DocumentTextNotFound("Documento não encontrado no Caso informado.")
    _validate_source_document(document)
    return document


def find_latest_reusable_extraction(
    db: Session,
    *,
    document: SharedDocument,
    extraction_profile: str,
) -> DocumentTextExtraction | None:
    source_sha256 = _validate_source_document(document)
    return (
        db.query(DocumentTextExtraction)
        .options(selectinload(DocumentTextExtraction.pages))
        .filter(
            DocumentTextExtraction.shared_document_id == document.id,
            DocumentTextExtraction.shared_case_id == document.shared_case_id,
            DocumentTextExtraction.source_sha256 == source_sha256,
            DocumentTextExtraction.extraction_profile == extraction_profile,
            DocumentTextExtraction.capability == CAPABILITY,
            DocumentTextExtraction.status == "ready",
        )
        .order_by(
            DocumentTextExtraction.completed_at.desc(),
            DocumentTextExtraction.created_at.desc(),
            DocumentTextExtraction.id.desc(),
        )
        .first()
    )


def serialize_page(page: DocumentTextPage) -> dict:
    return {
        "id": page.id,
        "extraction_id": page.extraction_id,
        "page_number": page.page_number,
        "raw_text": page.raw_text,
        "reviewed_text": page.reviewed_text,
        "reviewed_by_operator_id": page.reviewed_by_operator_id,
        "reviewed_by_username": page.reviewed_by_username,
        "reviewed_at": page.reviewed_at.isoformat() if page.reviewed_at else None,
    }


def serialize_extraction(extraction: DocumentTextExtraction) -> dict:
    return {
        "id": extraction.id,
        "shared_case_id": extraction.shared_case_id,
        "shared_document_id": extraction.shared_document_id,
        "source_sha256": extraction.source_sha256,
        "capability": extraction.capability,
        "extraction_profile": extraction.extraction_profile,
        "status": extraction.status,
        "executor_type": extraction.executor_type,
        "engine": extraction.engine,
        "engine_version": extraction.engine_version,
        "parameters_json": extraction.parameters_json,
        "error_code": extraction.error_code,
        "error_detail": extraction.error_detail,
        "created_by_operator_id": extraction.created_by_operator_id,
        "created_by_username": extraction.created_by_username,
        "created_at": extraction.created_at.isoformat(),
        "completed_at": extraction.completed_at.isoformat() if extraction.completed_at else None,
        "pages": [serialize_page(page) for page in extraction.pages],
    }


def stage_extraction(
    db: Session,
    *,
    document: SharedDocument,
    extraction_profile: str,
    status: str,
    executor_type: str,
    pages: Iterable[Mapping[str, object]] = (),
    engine: str | None = None,
    engine_version: str | None = None,
    parameters_json: str | None = None,
    error_code: str | None = None,
    error_detail: str | None = None,
    created_by_operator_id: int | None = None,
    created_by_username: str | None = None,
    created_at: datetime | None = None,
    completed_at: datetime | None = None,
) -> DocumentTextExtraction:
    source_sha256 = _validate_source_document(document)
    if not isinstance(extraction_profile, str) or not extraction_profile.strip():
        raise DocumentTextError("extraction_profile deve ser texto não vazio.")
    if len(extraction_profile.strip()) > 128:
        raise DocumentTextError("extraction_profile excede 128 caracteres.")
    if status not in VALID_STATUSES:
        raise DocumentTextError("status inválido.")
    if executor_type not in VALID_EXECUTOR_TYPES:
        raise DocumentTextError("executor_type inválido.")

    extraction = DocumentTextExtraction(
        shared_case_id=document.shared_case_id,
        shared_document_id=document.id,
        source_sha256=source_sha256,
        capability=CAPABILITY,
        extraction_profile=extraction_profile.strip(),
        status=status,
        executor_type=executor_type,
        engine=engine,
        engine_version=engine_version,
        parameters_json=parameters_json,
        error_code=error_code,
        error_detail=error_detail,
        created_by_operator_id=created_by_operator_id,
        created_by_username=created_by_username,
        created_at=created_at or datetime.now(timezone.utc),
        completed_at=completed_at,
    )
    for item in pages:
        page_number = item.get("page_number")
        raw_text = item.get("raw_text")
        if isinstance(page_number, bool) or not isinstance(page_number, int) or page_number < 1:
            raise DocumentTextError("page_number deve ser um inteiro positivo.")
        if not isinstance(raw_text, str):
            raise DocumentTextError("raw_text deve ser texto.")
        extraction.pages.append(
            DocumentTextPage(
                page_number=page_number,
                raw_text=raw_text,
                reviewed_text=item.get("reviewed_text"),
                reviewed_by_operator_id=item.get("reviewed_by_operator_id"),
                reviewed_by_username=item.get("reviewed_by_username"),
                reviewed_at=item.get("reviewed_at"),
            )
        )
    db.add(extraction)
    db.flush()
    return extraction
