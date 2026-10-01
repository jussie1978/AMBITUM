"""PR-02 Smart Metadata HTTP, authentication, and audit smoke."""

from __future__ import annotations

import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path


_TEMP_DATA = tempfile.TemporaryDirectory(prefix="circe-pr02-http-data-")
os.environ["DATA_DIR"] = _TEMP_DATA.name

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from starlette.middleware.sessions import SessionMiddleware

from app.database import Base
from app.middleware.auth_guard import AuthGuard
from app.models.operator import AuditLog
from app.models.platea import SharedCase, SharedDocument, SharedPerson
from app.models.smart_metadata import AssetSmartMetadata  # noqa: F401
import app.routes.smart_metadata as metadata_routes


def main() -> None:
    db_path = Path(_TEMP_DATA.name) / "http-smoke.db"
    engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False},
        poolclass=NullPool,
    )
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = Session()
    now = datetime.now(timezone.utc)
    cases = [
        SharedCase(case_ref="PR02-HTTP-A", title="Caso HTTP A", status="aberto", published_by="smoke", published_at=now, published_version=1),
        SharedCase(case_ref="PR02-HTTP-B", title="Caso HTTP B", status="aberto", published_by="smoke", published_at=now, published_version=1),
    ]
    db.add_all(cases)
    db.flush()
    documents = [
        SharedDocument(shared_case_id=cases[0].id, document_ref="PR02-HTTP-DOC-A", filename="a.txt", file_type="txt", sha256="a" * 64, description="synthetic", imported_at="2026-09-28"),
        SharedDocument(shared_case_id=cases[0].id, document_ref="PR02-HTTP-DOC-A2", filename="a2.txt", file_type="txt", sha256="b" * 64, description="synthetic", imported_at="2026-09-28"),
        SharedDocument(shared_case_id=cases[1].id, document_ref="PR02-HTTP-DOC-B", filename="b.txt", file_type="txt", sha256="c" * 64, description="synthetic", imported_at="2026-09-28"),
    ]
    person = SharedPerson(shared_case_id=cases[0].id, full_name="Pessoa do Caso A")
    foreign_person = SharedPerson(shared_case_id=cases[1].id, full_name="Pessoa do Caso B")
    db.add_all([*documents, person, foreign_person])
    db.commit()
    case_a_ref, case_b_ref = [case.case_ref for case in cases]
    doc_a_id, doc_a2_id, doc_b_id = [doc.id for doc in documents]
    person_id = person.id
    foreign_person_id = foreign_person.id
    db.close()

    original_session_local = metadata_routes.SessionLocal
    original_log_action = metadata_routes.log_action
    metadata_routes.SessionLocal = Session
    app = FastAPI()
    app.add_middleware(AuthGuard)
    app.add_middleware(SessionMiddleware, secret_key="pr02-http-smoke-secret")
    app.include_router(metadata_routes.router)

    @app.post("/login")
    async def login(request: Request):
        request.session["operator"] = {"id": 7, "username": "pr02-http-smoke"}
        return JSONResponse({"ok": True})

    def batch_payload(document_ids: list[int], operation: str, kind: str, value: str, **extra: object) -> dict:
        return {
            "document_ids": document_ids,
            "operation": operation,
            "kind": kind,
            "value": value,
            **extra,
        }

    base_url = f"/api/cases/{case_a_ref}/smart-metadata"
    try:
        with TestClient(app) as client:
            response = client.get(base_url, follow_redirects=False)
            assert response.status_code == 302 and response.headers["location"] == "/login"
            assert client.post("/login").status_code == 200

            response = client.get(base_url)
            assert response.status_code == 200
            assert response.json()["items"] == [] and response.json()["by_document"] == {}
            response = client.get(f"/api/cases/NO-SUCH-CASE/smart-metadata")
            assert response.status_code == 404 and response.json()["code"] == "not_found"

            response = client.get(
                base_url,
                params={"document_id": doc_a_id},
            )
            assert response.status_code == 200 and response.json()["items"] == []

            # Strict payload handling rejects a client supplied provenance and unknown fields.
            for extra in ({"provenance": "system_derived"}, {"unknown": True}):
                rejected = client.put(
                    f"{base_url}/batch",
                    json=batch_payload([doc_a_id], "add", "tag", "strict-check", **extra),
                )
                assert rejected.status_code == 422

            add = client.put(
                f"{base_url}/batch",
                json=batch_payload([doc_a_id, doc_a2_id], "add", "tag", "Tema comum"),
            )
            assert add.status_code == 200
            assert add.json()["affected_count"] == 2
            assert add.json()["provenance"] == "human_confirmed"

            by_doc = client.get(base_url, params={"document_id": doc_a_id})
            assert by_doc.status_code == 200 and len(by_doc.json()["items"]) == 1
            assert by_doc.json()["items"][0]["provenance"] == "human_confirmed"
            by_kind = client.get(base_url, params={"kind": "tag"})
            assert by_kind.status_code == 200 and len(by_kind.json()["items"]) == 2
            by_other_kind = client.get(base_url, params={"kind": "topic"})
            assert by_other_kind.status_code == 200 and by_other_kind.json()["items"] == []

            # Same-case person linking is optional and remains a target association.
            linked = client.put(
                f"{base_url}/batch",
                json=batch_payload([doc_a_id], "add", "target", "Pessoa vinculada", linked_person_id=person_id),
            )
            assert linked.status_code == 200 and linked.json()["linked_person_id"] == person_id

            # A document from another case invalidates the whole batch before any write/audit.
            before_cross = client.get(base_url).json()["items"]
            cross = client.put(
                f"{base_url}/batch",
                json=batch_payload([doc_a_id, doc_b_id], "add", "topic", "cross-case"),
            )
            assert cross.status_code == 422 and cross.json()["code"] == "validation_error"
            after_cross = client.get(base_url).json()["items"]
            assert after_cross == before_cross

            remove = client.put(
                f"{base_url}/batch",
                json=batch_payload([doc_a_id, doc_a2_id], "remove", "tag", "Tema comum"),
            )
            assert remove.status_code == 200 and remove.json()["affected_count"] == 2
            remaining = client.get(base_url).json()["items"]
            assert len(remaining) == 1
            assert remaining[0]["kind"] == "target"

            audit_db = Session()
            actions = [row.action for row in audit_db.query(AuditLog).order_by(AuditLog.id).all()]
            assert actions == ["smart_metadata_batch_added", "smart_metadata_batch_added", "smart_metadata_batch_removed"]
            successful_audit_count = audit_db.query(AuditLog).count()
            audit_db.close()

            # Audit failure must roll back the metadata row and audit transaction together.
            def failing_audit(*args: object, **kwargs: object) -> None:
                raise RuntimeError("synthetic audit failure")

            metadata_routes.log_action = failing_audit
            failed = client.put(
                f"{base_url}/batch",
                json=batch_payload([doc_a_id], "add", "topic", "audit rollback"),
            )
            assert failed.status_code == 500 and failed.json()["code"] == "internal_error"
            metadata_routes.log_action = original_log_action

            verify = Session()
            assert verify.query(AssetSmartMetadata).filter_by(value_text="audit rollback").count() == 0
            assert verify.query(AuditLog).count() == successful_audit_count
            verify.close()

            # Cross-case person reference is rejected and does not create an audit entry.
            bad_person = client.put(
                f"{base_url}/batch",
                json=batch_payload([doc_a_id], "add", "target", "foreign person", linked_person_id=foreign_person_id),
            )
            assert bad_person.status_code == 422
    finally:
        metadata_routes.SessionLocal = original_session_local
        metadata_routes.log_action = original_log_action
        engine.dispose()
        _TEMP_DATA.cleanup()

    print("PR-02 SMART METADATA HTTP SMOKE: OK")
    print("auth=302; GET/filter/404=ok; strict-payload=422; server-provenance=human_confirmed")
    print("add/remove=ok; same-case-person=ok; cross-case-batch=atomic-rejection")
    print("audit=add/remove; audit-failure=rollback")


if __name__ == "__main__":
    main()
