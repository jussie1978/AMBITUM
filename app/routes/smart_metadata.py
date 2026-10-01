from __future__ import annotations

from typing import Annotated, Literal

from fastapi import APIRouter, Path, Query, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, StrictInt, StrictStr

from app.database import SessionLocal
from app.services.audit_service import log_action
from app.services.smart_metadata_service import (
    MAX_BATCH_DOCUMENTS,
    SmartMetadataError,
    apply_batch,
    list_metadata,
)


router = APIRouter(prefix="/api/cases/{case_ref}/smart-metadata")
PositivePathId = Annotated[int, Path(ge=1)]
PositiveQueryId = Annotated[int, Query(ge=1)]
PositiveId = Annotated[StrictInt, Field(ge=1)]


class StrictPayload(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class SmartMetadataBatch(StrictPayload):
    document_ids: list[PositiveId] = Field(
        min_length=1, max_length=MAX_BATCH_DOCUMENTS,
    )
    operation: Literal["add", "remove"]
    kind: StrictStr
    value: StrictStr
    linked_person_id: PositiveId | None = None


def _error_response(error: SmartMetadataError) -> JSONResponse:
    return JSONResponse(
        {"code": error.code, "error": error.message},
        status_code=error.status_code,
    )


def _operator(request: Request) -> tuple[int | None, str]:
    operator = request.session.get("operator")
    if not isinstance(operator, dict) or not operator.get("username"):
        raise SmartMetadataError("Operador autenticado inválido.")
    return operator.get("id"), str(operator["username"])


@router.get("")
async def smart_metadata_list(
    request: Request,
    case_ref: str,
    document_id: PositiveQueryId | None = None,
    kind: str | None = Query(default=None),
):
    db = SessionLocal()
    try:
        items = list_metadata(
            db, case_ref=case_ref, document_id=document_id, kind=kind,
        )
        grouped: dict[str, list[dict]] = {}
        for item in items:
            grouped.setdefault(str(item["shared_document_id"]), []).append(item)
        return {"case_ref": case_ref, "items": items, "by_document": grouped}
    except SmartMetadataError as error:
        db.rollback()
        return _error_response(error)
    except Exception:
        db.rollback()
        return JSONResponse(
            {"code": "internal_error", "error": "Erro interno ao consultar Smart Metadata."},
            status_code=500,
        )
    finally:
        db.close()


@router.put("/batch")
async def smart_metadata_batch(
    request: Request, case_ref: str, payload: SmartMetadataBatch,
):
    db = SessionLocal()
    try:
        operator_id, operator_username = _operator(request)
        result = apply_batch(
            db,
            case_ref=case_ref,
            document_ids=payload.document_ids,
            operation=payload.operation,
            kind=payload.kind,
            value=payload.value,
            linked_person_id=payload.linked_person_id,
            operator_id=operator_id,
            operator_username=operator_username,
            # Human provenance is intentionally not accepted from the client.
            provenance="human_confirmed",
        )
        action = (
            "smart_metadata_batch_added"
            if result.operation == "add"
            else "smart_metadata_batch_removed"
        )
        person_detail = (
            f"; linked_person_id={result.linked_person_id}"
            if result.linked_person_id is not None
            else ""
        )
        log_action(
            db,
            action=action,
            description=(
                f"Smart Metadata {result.operation} no Caso {case_ref}; "
                f"documentos={list(result.document_ids)}; kind={result.kind}; "
                f"value={result.value_text!r}{person_detail}; "
                f"afetados={result.affected_count}."
            ),
            operator_id=operator_id,
            operator_username=operator_username,
            entity_type="shared_case",
            entity_id=case_ref,
            ip_address=request.client.host if request.client else None,
            manage_transaction=False,
        )
        db.commit()
        return {
            "case_ref": case_ref,
            "operation": result.operation,
            "requested_count": result.requested_count,
            "affected_count": result.affected_count,
            "document_ids": list(result.document_ids),
            "kind": result.kind,
            "value_text": result.value_text,
            "linked_person_id": result.linked_person_id,
            "provenance": "human_confirmed",
        }
    except SmartMetadataError as error:
        db.rollback()
        return _error_response(error)
    except Exception:
        db.rollback()
        return JSONResponse(
            {"code": "internal_error", "error": "Erro interno ao aplicar Smart Metadata."},
            status_code=500,
        )
    finally:
        db.close()
