from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable

from sqlalchemy.orm import Session

from app.models.platea import SharedCase, SharedDocument, SharedPerson
from app.models.smart_metadata import AssetSmartMetadata


SMART_METADATA_KINDS = frozenset({
    "target",
    "topic",
    "tag",
    "section_hint",
    "event_ref",
    "relevance",
    "source_kind",
    "validation_status",
})
SMART_METADATA_PROVENANCES = frozenset({
    "human_confirmed",
    "ai_suggested",
    "system_derived",
})
HUMAN_PROVENANCE = "human_confirmed"
MAX_BATCH_DOCUMENTS = 100
MAX_VALUE_LENGTH = 256


class SmartMetadataError(Exception):
    status_code = 422
    code = "validation_error"

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class SmartMetadataCaseNotFound(SmartMetadataError):
    status_code = 404
    code = "not_found"


@dataclass(frozen=True)
class BatchResult:
    operation: str
    requested_count: int
    affected_count: int
    document_ids: tuple[int, ...]
    kind: str
    value_text: str
    linked_person_id: int | None


def _positive_id(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise SmartMetadataError(f"{label} deve ser um inteiro positivo.")
    return value


def normalize_kind(kind: object) -> str:
    if not isinstance(kind, str):
        raise SmartMetadataError("kind inválido.")
    normalized = kind.strip().lower()
    if normalized not in SMART_METADATA_KINDS:
        raise SmartMetadataError("kind não permitido.")
    return normalized


def normalize_value(value: object) -> str:
    if not isinstance(value, str):
        raise SmartMetadataError("value deve ser texto.")
    normalized = value.strip()
    if not normalized:
        raise SmartMetadataError("value não pode ser vazio.")
    if len(normalized) > MAX_VALUE_LENGTH:
        raise SmartMetadataError(
            f"value excede o limite de {MAX_VALUE_LENGTH} caracteres."
        )
    return normalized


def normalize_document_ids(document_ids: object) -> tuple[int, ...]:
    if not isinstance(document_ids, (list, tuple)):
        raise SmartMetadataError("document_ids deve ser uma lista.")
    if not document_ids:
        raise SmartMetadataError("document_ids não pode ser vazio.")
    if len(document_ids) > MAX_BATCH_DOCUMENTS:
        raise SmartMetadataError(
            f"O batch aceita no máximo {MAX_BATCH_DOCUMENTS} documentos."
        )
    normalized = tuple(_positive_id(value, "document_id") for value in document_ids)
    if len(set(normalized)) != len(normalized):
        raise SmartMetadataError("document_ids deve conter IDs únicos.")
    return normalized


def resolve_case(db: Session, case_ref: str) -> SharedCase:
    case = db.query(SharedCase).filter(SharedCase.case_ref == case_ref).first()
    if not case:
        raise SmartMetadataCaseNotFound("Caso não encontrado.")
    return case


def _validate_documents(
    db: Session, case: SharedCase, document_ids: tuple[int, ...],
) -> None:
    found = {
        item.id
        for item in db.query(SharedDocument.id).filter(
            SharedDocument.shared_case_id == case.id,
            SharedDocument.id.in_(document_ids),
        )
    }
    if found != set(document_ids):
        raise SmartMetadataError(
            "Um ou mais documentos não pertencem ao Caso informado."
        )


def _validate_person(
    db: Session, case: SharedCase, linked_person_id: int | None,
) -> int | None:
    if linked_person_id is None:
        return None
    person_id = _positive_id(linked_person_id, "linked_person_id")
    exists = db.query(SharedPerson.id).filter(
        SharedPerson.id == person_id,
        SharedPerson.shared_case_id == case.id,
    ).first()
    if not exists:
        raise SmartMetadataError(
            "A pessoa informada não pertence ao Caso informado."
        )
    return person_id


def serialize_metadata(item: AssetSmartMetadata) -> dict:
    return {
        "id": item.id,
        "shared_case_id": item.shared_case_id,
        "shared_document_id": item.shared_document_id,
        "kind": item.kind,
        "value_text": item.value_text,
        "linked_person_id": item.linked_person_id,
        "provenance": item.provenance,
        "created_by_operator_id": item.created_by_operator_id,
        "created_by_username": item.created_by_username,
        "created_at": item.created_at.isoformat(),
        "updated_at": item.updated_at.isoformat(),
    }


def list_metadata(
    db: Session,
    *,
    case_ref: str,
    document_id: int | None = None,
    kind: str | None = None,
) -> list[dict]:
    case = resolve_case(db, case_ref)
    query = db.query(AssetSmartMetadata).filter(
        AssetSmartMetadata.shared_case_id == case.id
    )
    if document_id is not None:
        normalized_document_id = _positive_id(document_id, "document_id")
        _validate_documents(db, case, (normalized_document_id,))
        query = query.filter(
            AssetSmartMetadata.shared_document_id == normalized_document_id
        )
    if kind is not None:
        query = query.filter(AssetSmartMetadata.kind == normalize_kind(kind))
    return [
        serialize_metadata(item)
        for item in query.order_by(
            AssetSmartMetadata.shared_document_id,
            AssetSmartMetadata.kind,
            AssetSmartMetadata.value_text,
            AssetSmartMetadata.id,
        ).all()
    ]


def apply_batch(
    db: Session,
    *,
    case_ref: str,
    document_ids: Iterable[int],
    operation: str,
    kind: str,
    value: str,
    linked_person_id: int | None,
    operator_id: int | None,
    operator_username: str,
    provenance: str = HUMAN_PROVENANCE,
) -> BatchResult:
    if operation not in {"add", "remove"}:
        raise SmartMetadataError("operation deve ser add ou remove.")
    if provenance not in SMART_METADATA_PROVENANCES:
        raise SmartMetadataError("provenance inválida.")
    if not operator_username or not operator_username.strip():
        raise SmartMetadataError("Operador autenticado inválido.")

    normalized_ids = normalize_document_ids(list(document_ids))
    normalized_kind = normalize_kind(kind)
    normalized_value = normalize_value(value)
    case = resolve_case(db, case_ref)

    # Validate the complete request before staging any mutation.
    _validate_documents(db, case, normalized_ids)
    normalized_person_id = _validate_person(db, case, linked_person_id)
    if normalized_person_id is not None and normalized_kind != "target":
        raise SmartMetadataError("linked_person_id só é permitido para target.")

    query = db.query(AssetSmartMetadata).filter(
        AssetSmartMetadata.shared_case_id == case.id,
        AssetSmartMetadata.shared_document_id.in_(normalized_ids),
        AssetSmartMetadata.kind == normalized_kind,
        AssetSmartMetadata.value_text == normalized_value,
    )
    if normalized_person_id is None:
        query = query.filter(AssetSmartMetadata.linked_person_id.is_(None))
    else:
        query = query.filter(
            AssetSmartMetadata.linked_person_id == normalized_person_id
        )

    existing = query.all()
    if operation == "add":
        existing_document_ids = {item.shared_document_id for item in existing}
        now = datetime.now(timezone.utc)
        additions = [
            AssetSmartMetadata(
                shared_case_id=case.id,
                shared_document_id=document_id,
                kind=normalized_kind,
                value_text=normalized_value,
                linked_person_id=normalized_person_id,
                provenance=provenance,
                created_by_operator_id=operator_id,
                created_by_username=operator_username.strip(),
                created_at=now,
                updated_at=now,
            )
            for document_id in normalized_ids
            if document_id not in existing_document_ids
        ]
        db.add_all(additions)
        affected_count = len(additions)
    else:
        for item in existing:
            db.delete(item)
        affected_count = len(existing)

    db.flush()
    return BatchResult(
        operation=operation,
        requested_count=len(normalized_ids),
        affected_count=affected_count,
        document_ids=normalized_ids,
        kind=normalized_kind,
        value_text=normalized_value,
        linked_person_id=normalized_person_id,
    )
