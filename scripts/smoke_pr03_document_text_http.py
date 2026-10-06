"""PR-03 authenticated HTTP, review, audit, and rollback smoke."""

from __future__ import annotations

import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from starlette.middleware.sessions import SessionMiddleware

from app.database import Base
from app.middleware.auth_guard import AuthGuard
from app.models.derived_content import DocumentTextExtraction
from app.models.operator import AuditLog, Operator  # noqa: F401
from app.models.platea import SharedCase, SharedDocument
import app.routes.documents as document_routes
from app.services.document_text_service import (
    DEFAULT_EXTRACTION_PROFILE,
    DocumentTextExecutionResult,
    find_latest_reusable_extraction,
    resolve_source_document,
    stage_extraction,
)


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="circe-pr03-http-") as tmp:
        root = Path(tmp)
        db_path = root / "http.db"
        app_data = root / "appdata"
        storage_root = app_data / "case_storage"
        physical_dir = storage_root / "cases" / "1" / "documents"
        physical_dir.mkdir(parents=True)

        engine = create_engine(
            f"sqlite:///{db_path}",
            connect_args={"check_same_thread": False},
            poolclass=NullPool,
        )
        Base.metadata.create_all(bind=engine)
        Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = Session()
        now = datetime.now(timezone.utc)
        case_a = SharedCase(case_ref="PR03-HTTP-A", title="Caso A", status="aberto", published_by="smoke", published_at=now, published_version=1)
        case_b = SharedCase(case_ref="PR03-HTTP-B", title="Caso B", status="aberto", published_by="smoke", published_at=now, published_version=1)
        db.add_all([case_a, case_b])
        db.flush()

        originals: dict[str, bytes] = {
            "primary.pdf": b"synthetic primary original",
            "foreign.pdf": b"synthetic foreign original",
            "empty.pdf": b"synthetic empty original",
            "rollback.pdf": b"synthetic rollback original",
        }
        documents: dict[str, SharedDocument] = {}
        for name, content in originals.items():
            path = physical_dir / name
            path.write_bytes(content)
            target_case = case_b if name == "foreign.pdf" else case_a
            document = SharedDocument(
                shared_case_id=target_case.id,
                filename=name,
                file_type="pdf",
                mime_type="application/pdf",
                sha256=(name.encode("utf-8").hex() + "0" * 64)[:64],
                storage_relpath=path.relative_to(storage_root).as_posix(),
            )
            documents[name] = document
            db.add(document)
        db.commit()
        document_ids = {name: item.id for name, item in documents.items()}
        db.close()

        original_session_local = document_routes.SessionLocal
        original_data_dir = document_routes.settings.data_dir
        original_storage_dir = document_routes.settings.case_storage_dir
        original_execute = document_routes.execute_document_text_extraction
        capability_calls = 0

        def fake_capability(
            db,
            *,
            storage,
            case_ref,
            document_id,
            extraction_profile,
            created_by_operator_id=None,
            created_by_username=None,
        ):
            nonlocal capability_calls
            capability_calls += 1
            document = resolve_source_document(
                db, case_ref=case_ref, document_id=document_id
            )
            storage.resolve(document.storage_relpath)
            reusable = find_latest_reusable_extraction(
                db,
                document=document,
                extraction_profile=extraction_profile,
            )
            if reusable is not None:
                return DocumentTextExecutionResult(
                    extraction=reusable,
                    reused=True,
                    text_obtained=True,
                )
            extraction = stage_extraction(
                db,
                document=document,
                extraction_profile=extraction_profile,
                status="ready",
                executor_type="mixed",
                pages=[
                    {
                        "page_number": 1,
                        "executor_type": "native",
                        "engine": "pypdf",
                        "engine_version": "smoke",
                        "status": "ready",
                        "raw_text": "RAW NATIVE IMMUTABLE",
                    },
                    {
                        "page_number": 2,
                        "executor_type": "ocr",
                        "engine": "rapidocr-onnxruntime",
                        "engine_version": "3.9.2",
                        "status": "ready",
                        "raw_text": "RAW OCR IMMUTABLE",
                    },
                ],
                created_by_operator_id=created_by_operator_id,
                created_by_username=created_by_username,
                completed_at=datetime.now(timezone.utc),
            )
            return DocumentTextExecutionResult(
                extraction=extraction,
                reused=False,
                text_obtained=True,
            )

        document_routes.SessionLocal = Session
        document_routes.settings.data_dir = str(app_data)
        document_routes.settings.case_storage_dir = "case_storage"
        document_routes.execute_document_text_extraction = fake_capability

        app = FastAPI()
        app.add_middleware(AuthGuard)
        app.add_middleware(SessionMiddleware, secret_key="pr03-http-smoke-secret")
        app.include_router(document_routes.router)

        @app.post("/login")
        async def login(request: Request):
            request.session["operator"] = {"id": 17, "username": "pr03-reviewer"}
            return JSONResponse({"ok": True})

        try:
            with TestClient(app) as client:
                base = f"/api/cases/PR03-HTTP-A/documents/{document_ids['primary.pdf']}/text-extraction"

                unauthenticated = client.post(base, json={}, follow_redirects=False)
                assert unauthenticated.status_code == 302
                assert unauthenticated.headers["location"] == "/login"
                assert client.post("/login").status_code == 200

                empty_url = f"/api/cases/PR03-HTTP-A/documents/{document_ids['empty.pdf']}/text-extraction"
                calls_before_get = capability_calls
                empty = client.get(empty_url)
                assert empty.status_code == 200
                assert empty.json() == {"state": "empty", "extraction": None}
                assert capability_calls == calls_before_get

                invalid = client.post(base, json={"path": r"C:\evidence\file.pdf"})
                assert invalid.status_code == 422
                arbitrary = client.post(base, json={"executor": "vlm"})
                assert arbitrary.status_code == 422

                cross = client.post(
                    f"/api/cases/PR03-HTTP-A/documents/{document_ids['foreign.pdf']}/text-extraction",
                    json={},
                )
                assert cross.status_code == 404

                created = client.post(base, json={})
                assert created.status_code == 200
                payload = created.json()
                assert payload["state"] == "ready"
                assert payload["reused"] is False
                assert payload["text_obtained"] is True
                extraction = payload["extraction"]
                extraction_id = extraction["id"]
                assert extraction["executor_type"] == "mixed"
                assert [page["executor_type"] for page in extraction["pages"]] == ["native", "ocr"]
                assert "storage_relpath" not in json.dumps(payload)

                calls_before_get = capability_calls
                fetched = client.get(base)
                assert fetched.status_code == 200
                assert fetched.json()["extraction"]["id"] == extraction_id
                assert capability_calls == calls_before_get

                reused = client.post(base, json={})
                assert reused.status_code == 200
                assert reused.json()["reused"] is True
                assert reused.json()["extraction"]["id"] == extraction_id

                review_url = f"{base}/{extraction_id}/pages/1/review"
                reviewed = client.put(review_url, json={"reviewed_text": "TEXTO REVISTO"})
                assert reviewed.status_code == 200
                reviewed_page = reviewed.json()["page"]
                assert reviewed_page["reviewed_text"] == "TEXTO REVISTO"
                assert reviewed_page["raw_text"] == "RAW NATIVE IMMUTABLE"
                assert reviewed_page["reviewed_by_operator_id"] == 17
                assert reviewed_page["reviewed_by_username"] == "pr03-reviewer"
                assert reviewed_page["reviewed_at"]

                invalid_review = client.put(
                    review_url,
                    json={"reviewed_text": "x", "raw_text": "overwrite"},
                )
                assert invalid_review.status_code == 422

                cleared = client.put(review_url, json={"reviewed_text": None})
                assert cleared.status_code == 200
                assert cleared.json()["page"]["reviewed_text"] is None
                assert cleared.json()["page"]["raw_text"] == "RAW NATIVE IMMUTABLE"

                original = client.get(f"/api/documents/{document_ids['primary.pdf']}/original")
                assert original.status_code == 200
                assert original.content == originals["primary.pdf"]

                def staged_failure(db, **kwargs):
                    document = resolve_source_document(
                        db,
                        case_ref=kwargs["case_ref"],
                        document_id=kwargs["document_id"],
                    )
                    stage_extraction(
                        db,
                        document=document,
                        extraction_profile=DEFAULT_EXTRACTION_PROFILE,
                        status="ready",
                        executor_type="native",
                        pages=[{
                            "page_number": 1,
                            "executor_type": "native",
                            "engine": "synthetic",
                            "engine_version": "1",
                            "status": "ready",
                            "raw_text": "MUST ROLLBACK",
                        }],
                    )
                    raise RuntimeError("synthetic failure after flush")

                document_routes.execute_document_text_extraction = staged_failure
                rollback_url = f"/api/cases/PR03-HTTP-A/documents/{document_ids['rollback.pdf']}/text-extraction"
                rolled_back = client.post(rollback_url, json={})
                assert rolled_back.status_code == 500

            verify = Session()
            persisted = verify.query(DocumentTextExtraction).all()
            assert len(persisted) == 1
            assert persisted[0].id == extraction_id
            assert persisted[0].pages[0].raw_text == "RAW NATIVE IMMUTABLE"
            assert persisted[0].pages[0].reviewed_text is None
            assert not any(
                item.shared_document_id == document_ids["rollback.pdf"]
                for item in persisted
            )
            actions = [row.action for row in verify.query(AuditLog).all()]
            assert "document_text_extraction_requested" in actions
            assert "document_text_extraction_completed" in actions
            assert "document_text_extraction_failed" in actions
            assert actions.count("document_text_review_saved") == 2
            assert "document_original_retrieved" in actions
            verify.close()
        finally:
            document_routes.SessionLocal = original_session_local
            document_routes.settings.data_dir = original_data_dir
            document_routes.settings.case_storage_dir = original_storage_dir
            document_routes.execute_document_text_extraction = original_execute
            engine.dispose()

    print("PR-03 DOCUMENT TEXT HTTP SMOKE: OK")
    print("auth/case-isolation/strict-payload/post/get/reuse/provenance=ok")
    print("review/raw-immutable/audit/rollback/original=ok")


if __name__ == "__main__":
    main()
