"""Page-aware orchestration and persistence for ``document.extract_text``.

The caller owns the transaction; source resolution remains governed by case
storage and executors never accept caller-provided paths.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Mapping

from PIL import Image
from sqlalchemy.orm import Session, selectinload

from app.config import settings
from app.models.derived_content import DocumentTextExtraction, DocumentTextPage
from app.models.platea import SharedCase, SharedDocument
from app.services.document_text_native_executor import (
    ENGINE_NAME,
    ENGINE_VERSION,
    NativeTextExtractionError,
    extract_native_pdf,
)
from app.services.document_text_ocr_executor import (
    ENGINE_NAME as OCR_ENGINE_NAME,
    ENGINE_VERSION as OCR_ENGINE_VERSION,
    OCRExecutionError,
    PARAMETERS_JSON as OCR_PARAMETERS_JSON,
    extract_ocr_image,
)
from app.services.document_text_vlm_executor import (
    ENGINE_NAME as VLM_ENGINE_NAME,
    VLMExecutionError,
    extract_vlm_image,
)
from app.services.storage_service import LocalCaseStorage


CAPABILITY = "document.extract_text"
VALID_STATUSES = frozenset({"processing", "ready", "failed"})
VALID_EXECUTOR_TYPES = frozenset({"native", "ocr", "vlm", "mixed"})
VALID_PAGE_EXECUTOR_TYPES = frozenset({"native", "ocr", "vlm"})
VALID_PAGE_STATUSES = frozenset({"ready", "failed"})


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


class DocumentTextUnsupportedSource(DocumentTextError):
    status_code = 415
    code = "unsupported_source_type"


@dataclass(frozen=True)
class DocumentTextExecutionResult:
    extraction: DocumentTextExtraction
    reused: bool
    text_obtained: bool
    fallback_candidate: str | None = None


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


def _serialize_page_foundation(page: DocumentTextPage) -> dict:
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


def _stage_extraction_foundation(
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


def _execute_native_text_extraction_foundation(
    db: Session,
    *,
    storage: LocalCaseStorage,
    case_ref: str,
    document_id: int,
    extraction_profile: str,
    created_by_operator_id: int | None = None,
    created_by_username: str | None = None,
) -> DocumentTextExecutionResult:
    """Execute native PDF extraction without committing the caller's transaction."""
    document = resolve_source_document(
        db,
        case_ref=case_ref,
        document_id=document_id,
    )
    is_pdf = document.mime_type == "application/pdf"
    if document.mime_type is None:
        is_pdf = (document.file_type or "").strip().lower() == "pdf"
    if not is_pdf:
        raise DocumentTextUnsupportedSource(
            "Tipo de documento não suportado para extração nativa."
        )

    reusable = find_latest_reusable_extraction(
        db,
        document=document,
        extraction_profile=extraction_profile,
    )
    if reusable is not None:
        return DocumentTextExecutionResult(
            extraction=reusable,
            reused=True,
            text_obtained=any(page.raw_text.strip() for page in reusable.pages),
        )

    source_path = storage.resolve(document.storage_relpath)
    completed_at = datetime.now(timezone.utc)
    try:
        native_result = extract_native_pdf(source_path)
    except NativeTextExtractionError as exc:
        extraction = stage_extraction(
            db,
            document=document,
            extraction_profile=extraction_profile,
            status="failed",
            executor_type="native",
            engine=ENGINE_NAME,
            engine_version=ENGINE_VERSION,
            error_code="native_extraction_failed",
            error_detail=str(exc),
            created_by_operator_id=created_by_operator_id,
            created_by_username=created_by_username,
            completed_at=completed_at,
        )
        return DocumentTextExecutionResult(
            extraction=extraction,
            reused=False,
            text_obtained=False,
        )

    extraction = stage_extraction(
        db,
        document=document,
        extraction_profile=extraction_profile,
        status="ready" if native_result.text_obtained else "failed",
        executor_type="native",
        engine=native_result.engine,
        engine_version=native_result.engine_version,
        pages=(
            {"page_number": page.page_number, "raw_text": page.raw_text}
            for page in native_result.pages
        ),
        error_code=(
            None if native_result.text_obtained else "native_text_not_obtained"
        ),
        error_detail=native_result.fallback_reason,
        created_by_operator_id=created_by_operator_id,
        created_by_username=created_by_username,
        completed_at=completed_at,
    )
    return DocumentTextExecutionResult(
        extraction=extraction,
        reused=False,
        text_obtained=native_result.text_obtained,
    )


# Page-aware PR-03 orchestration. These definitions preserve the foundation's
# public import names while extending persistence with page-level provenance.


def serialize_page(page: DocumentTextPage) -> dict:
    return {
        "id": page.id,
        "extraction_id": page.extraction_id,
        "page_number": page.page_number,
        "executor_type": page.executor_type,
        "engine": page.engine,
        "engine_version": page.engine_version,
        "status": page.status,
        "error_code": page.error_code,
        "error_detail": page.error_detail,
        "fallback_candidate": page.fallback_candidate,
        "raw_text": page.raw_text,
        "reviewed_text": page.reviewed_text,
        "reviewed_by_operator_id": page.reviewed_by_operator_id,
        "reviewed_by_username": page.reviewed_by_username,
        "reviewed_at": page.reviewed_at.isoformat() if page.reviewed_at else None,
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
        raise DocumentTextError("extraction_profile must be non-empty text.")
    if len(extraction_profile.strip()) > 128:
        raise DocumentTextError("extraction_profile exceeds 128 characters.")
    if status not in VALID_STATUSES:
        raise DocumentTextError("invalid extraction status.")
    if executor_type not in VALID_EXECUTOR_TYPES:
        raise DocumentTextError("invalid extraction executor_type.")

    page_items = list(pages)
    required = {"executor_type", "engine", "engine_version", "status"}
    for item in page_items:
        page_number = item.get("page_number")
        if isinstance(page_number, bool) or not isinstance(page_number, int) or page_number < 1:
            raise DocumentTextError("page_number must be a positive integer.")
        if not isinstance(item.get("raw_text"), str):
            raise DocumentTextError("raw_text must be text.")
        if not required.issubset(item):
            raise DocumentTextError("page-level provenance is required.")
        if item.get("executor_type") not in VALID_PAGE_EXECUTOR_TYPES:
            raise DocumentTextError("invalid page executor_type.")
        if item.get("status") not in VALID_PAGE_STATUSES:
            raise DocumentTextError("invalid page status.")
        if item.get("fallback_candidate") not in (None, "vlm"):
            raise DocumentTextError("invalid page fallback_candidate.")

    if page_items:
        page_executors = {str(item["executor_type"]) for item in page_items}
        expected_executor = (
            next(iter(page_executors)) if len(page_executors) == 1 else "mixed"
        )
        expected_status = (
            "ready"
            if all(item["status"] == "ready" for item in page_items)
            else "failed"
        )
        if executor_type != expected_executor:
            raise DocumentTextError("parent executor_type conflicts with page provenance.")
        if status != expected_status:
            raise DocumentTextError("parent status conflicts with page status.")

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
    for item in page_items:
        extraction.pages.append(
            DocumentTextPage(
                page_number=item["page_number"],
                executor_type=item["executor_type"],
                engine=item["engine"],
                engine_version=item["engine_version"],
                status=item["status"],
                error_code=item.get("error_code"),
                error_detail=item.get("error_detail"),
                fallback_candidate=item.get("fallback_candidate"),
                raw_text=item["raw_text"],
                reviewed_text=item.get("reviewed_text"),
                reviewed_by_operator_id=item.get("reviewed_by_operator_id"),
                reviewed_by_username=item.get("reviewed_by_username"),
                reviewed_at=item.get("reviewed_at"),
            )
        )
    db.add(extraction)
    db.flush()
    return extraction


def _document_kind(document: SharedDocument) -> str:
    mime_type = (document.mime_type or "").strip().lower()
    file_type = (document.file_type or "").strip().lower().lstrip(".")
    if mime_type == "application/pdf" or (not mime_type and file_type == "pdf"):
        return "pdf"
    if mime_type in {"image/png", "image/jpeg"}:
        return "image"
    if not mime_type and file_type in {"png", "jpg", "jpeg"}:
        return "image"
    raise DocumentTextUnsupportedSource("Unsupported document type for text extraction.")


def _render_pdf_page(source_path: Path, page_number: int) -> Image.Image:
    # PDFium renders only the selected page in memory. It neither changes the
    # governed original nor requires a persistent temporary file.
    import pypdfium2 as pdfium

    document = pdfium.PdfDocument(str(source_path))
    try:
        page = document[page_number - 1]
        try:
            bitmap = page.render(scale=300 / 72)
            try:
                return bitmap.to_pil().convert("RGB").copy()
            finally:
                bitmap.close()
        finally:
            page.close()
    finally:
        document.close()


def _ocr_page(image: Image.Image, *, page_number: int) -> dict[str, object]:
    try:
        result = extract_ocr_image(image)
    except OCRExecutionError as exc:
        return {
            "page_number": page_number,
            "executor_type": "ocr",
            "engine": OCR_ENGINE_NAME,
            "engine_version": OCR_ENGINE_VERSION,
            "status": "failed",
            "raw_text": "",
            "error_code": "ocr_execution_failed",
            "error_detail": str(exc),
        }
    if result.text_obtained:
        return {
            "page_number": page_number,
            "executor_type": "ocr",
            "engine": result.engine,
            "engine_version": result.engine_version,
            "status": "ready",
            "raw_text": result.raw_text,
        }
    return {
        "page_number": page_number,
        "executor_type": "ocr",
        "engine": result.engine,
        "engine_version": result.engine_version,
        "status": "failed",
        "raw_text": "",
        "error_code": "ocr_text_not_obtained",
        "error_detail": "no_text_content",
        "fallback_candidate": "vlm",
    }


def _vlm_page(image: Image.Image, *, page_number: int) -> dict[str, object]:
    try:
        result = extract_vlm_image(image)
    except VLMExecutionError as exc:
        return {
            "page_number": page_number,
            "executor_type": "vlm",
            "engine": VLM_ENGINE_NAME,
            "engine_version": settings.vlm_model,
            "status": "failed",
            "raw_text": "",
            "error_code": exc.code,
            "error_detail": str(exc),
        }
    if result.text_obtained:
        return {
            "page_number": page_number,
            "executor_type": "vlm",
            "engine": result.engine,
            "engine_version": result.engine_version,
            "status": "ready",
            "raw_text": result.raw_text,
        }
    return {
        "page_number": page_number,
        "executor_type": "vlm",
        "engine": result.engine,
        "engine_version": result.engine_version,
        "status": "failed",
        "raw_text": "",
        "error_code": "vlm_text_not_obtained",
        "error_detail": "no_text_content",
    }


def _ocr_then_vlm_page(image: Image.Image, *, page_number: int) -> dict[str, object]:
    page = _ocr_page(image, page_number=page_number)
    if page.get("fallback_candidate") != "vlm":
        return page
    return _vlm_page(image, page_number=page_number)


def execute_document_text_extraction(
    db: Session,
    *,
    storage: LocalCaseStorage,
    case_ref: str,
    document_id: int,
    extraction_profile: str,
    created_by_operator_id: int | None = None,
    created_by_username: str | None = None,
) -> DocumentTextExecutionResult:
    document = resolve_source_document(db, case_ref=case_ref, document_id=document_id)
    document_kind = _document_kind(document)
    reusable = find_latest_reusable_extraction(
        db, document=document, extraction_profile=extraction_profile
    )
    if reusable is not None:
        fallback_candidate = (
            "vlm"
            if any(page.fallback_candidate == "vlm" for page in reusable.pages)
            else None
        )
        return DocumentTextExecutionResult(
            extraction=reusable,
            reused=True,
            text_obtained=any(page.raw_text.strip() for page in reusable.pages),
            fallback_candidate=fallback_candidate,
        )

    source_path = storage.resolve(document.storage_relpath)
    completed_at = datetime.now(timezone.utc)
    pages: list[dict[str, object]] = []
    if document_kind == "pdf":
        try:
            native_result = extract_native_pdf(source_path)
        except NativeTextExtractionError as exc:
            extraction = stage_extraction(
                db,
                document=document,
                extraction_profile=extraction_profile,
                status="failed",
                executor_type="native",
                engine=ENGINE_NAME,
                engine_version=ENGINE_VERSION,
                error_code="native_extraction_failed",
                error_detail=str(exc),
                created_by_operator_id=created_by_operator_id,
                created_by_username=created_by_username,
                completed_at=completed_at,
            )
            return DocumentTextExecutionResult(
                extraction=extraction, reused=False, text_obtained=False
            )
        for native_page in native_result.pages:
            if native_page.raw_text.strip():
                pages.append(
                    {
                        "page_number": native_page.page_number,
                        "executor_type": "native",
                        "engine": native_result.engine,
                        "engine_version": native_result.engine_version,
                        "status": "ready",
                        "raw_text": native_page.raw_text,
                    }
                )
                continue
            try:
                rendered = _render_pdf_page(source_path, native_page.page_number)
                try:
                    pages.append(
                        _ocr_then_vlm_page(
                            rendered, page_number=native_page.page_number
                        )
                    )
                finally:
                    rendered.close()
            except Exception as exc:
                pages.append(
                    {
                        "page_number": native_page.page_number,
                        "executor_type": "ocr",
                        "engine": OCR_ENGINE_NAME,
                        "engine_version": OCR_ENGINE_VERSION,
                        "status": "failed",
                        "raw_text": "",
                        "error_code": "pdf_page_rasterization_failed",
                        "error_detail": str(exc),
                    }
                )
    else:
        try:
            with Image.open(source_path) as source_image:
                source_image.load()
                pages.append(_ocr_then_vlm_page(source_image, page_number=1))
        except Exception as exc:
            pages.append(
                {
                    "page_number": 1,
                    "executor_type": "ocr",
                    "engine": OCR_ENGINE_NAME,
                    "engine_version": OCR_ENGINE_VERSION,
                    "status": "failed",
                    "raw_text": "",
                    "error_code": "image_decode_failed",
                    "error_detail": str(exc),
                }
            )

    page_executors = {str(page["executor_type"]) for page in pages}
    executor_type = (
        next(iter(page_executors)) if len(page_executors) == 1 else "mixed"
    )
    status = (
        "ready"
        if pages and all(page["status"] == "ready" for page in pages)
        else "failed"
    )
    parent_engine = pages[0].get("engine") if executor_type != "mixed" and pages else None
    parent_engine_version = (
        pages[0].get("engine_version") if executor_type != "mixed" and pages else None
    )
    fallback_candidate = (
        "vlm" if any(page.get("fallback_candidate") == "vlm" for page in pages) else None
    )
    extraction = stage_extraction(
        db,
        document=document,
        extraction_profile=extraction_profile,
        status=status,
        executor_type=executor_type,
        engine=parent_engine,
        engine_version=parent_engine_version,
        parameters_json=OCR_PARAMETERS_JSON if "ocr" in page_executors else None,
        pages=pages,
        error_code=None if status == "ready" else "page_extraction_failed",
        error_detail=None if status == "ready" else "one_or_more_pages_failed",
        created_by_operator_id=created_by_operator_id,
        created_by_username=created_by_username,
        completed_at=completed_at,
    )
    return DocumentTextExecutionResult(
        extraction=extraction,
        reused=False,
        text_obtained=any(str(page["raw_text"]).strip() for page in pages),
        fallback_candidate=fallback_candidate,
    )


def execute_native_text_extraction(*args, **kwargs) -> DocumentTextExecutionResult:
    """Backward-compatible entry point for the document capability."""
    return execute_document_text_extraction(*args, **kwargs)
