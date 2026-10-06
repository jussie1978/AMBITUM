"""PR-03 derived-content model, service, and isolated migration smoke checks."""

from __future__ import annotations

import ast
import os
import sqlite3
import subprocess
import sys
import tempfile
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import create_engine, event, inspect
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.derived_content import DocumentTextExtraction, DocumentTextPage  # noqa: F401
from app.models.platea import SharedCase, SharedDocument
from app.services.document_text_service import (
    DocumentTextError,
    DocumentTextNotFound,
    DocumentTextSourceUnavailable,
    find_latest_reusable_extraction,
    resolve_source_document,
    serialize_extraction,
    stage_extraction,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
PREVIOUS_HEAD = "0014_pr03_document_text"
CURRENT_HEAD = "0015_pr03_page_provenance"


def _python() -> str:
    candidate = os.environ.get("PR03_PYTHON")
    return candidate or sys.executable


def _alembic(data_dir: Path, *args: str) -> str:
    env = os.environ.copy()
    env["DATA_DIR"] = str(data_dir)
    result = subprocess.run(
        [_python(), "-m", "alembic", *args],
        cwd=REPO_ROOT,
        env=env,
        text=True,
        capture_output=True,
    )
    if result.returncode:
        raise AssertionError(
            f"Alembic failed ({' '.join(args)}):\n{result.stdout}\n{result.stderr}"
        )
    return result.stdout + result.stderr


def _migration_smoke(root: Path) -> None:
    root.mkdir(parents=True)
    _alembic(root, "upgrade", PREVIOUS_HEAD)
    db_path = root / "athena.db"
    with closing(sqlite3.connect(db_path)) as db:
        case_id = db.execute(
            "INSERT INTO shared_cases (case_ref, title, status, published_by, published_at, published_version) VALUES (?, ?, ?, ?, ?, ?)",
            ("MIGRATION", "Migration", "aberto", "smoke", "2026-10-06", 1),
        ).lastrowid
        document_id = db.execute(
            "INSERT INTO shared_documents (shared_case_id, filename, file_type, sha256, storage_relpath) VALUES (?, ?, ?, ?, ?)",
            (case_id, "legacy.pdf", "pdf", "d" * 64, "legacy.pdf"),
        ).lastrowid
        extraction_id = db.execute(
            "INSERT INTO document_text_extractions (shared_case_id, shared_document_id, source_sha256, capability, extraction_profile, status, executor_type, engine, engine_version, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (case_id, document_id, "d" * 64, "document.extract_text", "legacy", "ready", "native", "pypdf", "5.9.0", "2026-10-06"),
        ).lastrowid
        db.execute(
            "INSERT INTO document_text_pages (extraction_id, page_number, raw_text) VALUES (?, ?, ?)",
            (extraction_id, 1, "legacy text"),
        )
        failed_extraction_id = db.execute(
            "INSERT INTO document_text_extractions (shared_case_id, shared_document_id, source_sha256, capability, extraction_profile, status, executor_type, engine, engine_version, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (case_id, document_id, "d" * 64, "document.extract_text", "legacy-failed", "failed", "ocr", "rapidocr-onnxruntime", "3.9.2", "2026-10-06"),
        ).lastrowid
        db.execute(
            "INSERT INTO document_text_pages (extraction_id, page_number, raw_text) VALUES (?, ?, ?)",
            (failed_extraction_id, 1, ""),
        )
        db.commit()

    _alembic(root, "upgrade", CURRENT_HEAD)
    with closing(sqlite3.connect(db_path)) as db:
        assert db.execute("SELECT version_num FROM alembic_version").fetchone()[0] == CURRENT_HEAD
        tables = {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        assert {"document_text_extractions", "document_text_pages"}.issubset(tables)
        legacy = db.execute(
            "SELECT raw_text, executor_type, engine, engine_version, status, error_code, fallback_candidate FROM document_text_pages ORDER BY id"
        ).fetchall()
        assert legacy == [
            ("legacy text", "native", "pypdf", "5.9.0", "ready", None, None),
            ("", "ocr", "rapidocr-onnxruntime", "3.9.2", "failed", None, None),
        ]

    engine = create_engine(f"sqlite:///{db_path}")
    inspector = inspect(engine)
    extraction_checks = {item["name"] for item in inspector.get_check_constraints("document_text_extractions")}
    page_checks = {item["name"] for item in inspector.get_check_constraints("document_text_pages")}
    page_uniques = {item["name"] for item in inspector.get_unique_constraints("document_text_pages")}
    extraction_indexes = {item["name"] for item in inspector.get_indexes("document_text_extractions")}
    assert extraction_checks == {
        "ck_document_text_extractions_capability",
        "ck_document_text_extractions_executor_type",
        "ck_document_text_extractions_status",
    }
    assert {
        "ck_document_text_pages_page_number",
        "ck_document_text_pages_executor_type",
        "ck_document_text_pages_status",
    }.issubset(page_checks)
    assert "uq_document_text_pages_extraction_page" in page_uniques
    assert {
        "ix_document_text_extractions_shared_case_id",
        "ix_document_text_extractions_shared_document_id",
        "ix_document_text_extractions_reuse_lookup",
    }.issubset(extraction_indexes)
    engine.dispose()

    _alembic(root, "downgrade", PREVIOUS_HEAD)
    with closing(sqlite3.connect(db_path)) as db:
        columns = {row[1] for row in db.execute("PRAGMA table_info(document_text_pages)")}
        assert "executor_type" not in columns
        assert db.execute("SELECT COUNT(*) FROM document_text_pages").fetchone()[0] == 2
    _alembic(root, "upgrade", CURRENT_HEAD)


def _assert_no_disallowed_engine_integration() -> None:
    source_paths = (
        REPO_ROOT / "app" / "services" / "document_text_service.py",
        REPO_ROOT / "app" / "services" / "document_text_native_executor.py",
        REPO_ROOT / "app" / "services" / "document_text_ocr_executor.py",
    )
    trees = [ast.parse(path.read_text(encoding="utf-8")) for path in source_paths]
    imported_modules = {
        node.module or ""
        for tree in trees
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
    } | {
        alias.name
        for tree in trees
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    forbidden = {"openai", "pytesseract", "paddleocr", "tesseract", "ollama", "transformers"}
    assert not imported_modules.intersection(forbidden)


def _service_smoke(db_path: Path) -> None:
    engine = create_engine(f"sqlite:///{db_path}")

    @event.listens_for(engine, "connect")
    def _enable_foreign_keys(connection, _record) -> None:
        connection.execute("PRAGMA foreign_keys=ON")

    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    db = Session()
    now = datetime.now(timezone.utc)
    case_a = SharedCase(case_ref="PR03-A", title="Caso A", status="aberto", published_by="smoke", published_at=now, published_version=1)
    case_b = SharedCase(case_ref="PR03-B", title="Caso B", status="aberto", published_by="smoke", published_at=now, published_version=1)
    db.add_all([case_a, case_b])
    db.flush()
    available = SharedDocument(shared_case_id=case_a.id, document_ref="A-1", filename="a.pdf", file_type="pdf", sha256="a" * 64, imported_at="2026-10-05", storage_relpath="PR03-A/a.pdf")
    metadata_only = SharedDocument(shared_case_id=case_a.id, document_ref="A-2", filename="metadata.pdf", file_type="pdf", sha256="b" * 64, imported_at="2026-10-05", storage_relpath=None)
    no_sha = SharedDocument(shared_case_id=case_a.id, document_ref="A-3", filename="no-sha.pdf", file_type="pdf", sha256=None, imported_at="2026-10-05", storage_relpath="PR03-A/no-sha.pdf")
    foreign = SharedDocument(shared_case_id=case_b.id, document_ref="B-1", filename="foreign.pdf", file_type="pdf", sha256="c" * 64, imported_at="2026-10-05", storage_relpath="PR03-B/foreign.pdf")
    db.add_all([available, metadata_only, no_sha, foreign])
    db.commit()

    assert resolve_source_document(db, case_ref="PR03-A", document_id=available.id).id == available.id
    for document_id, error_type in (
        (foreign.id, DocumentTextNotFound),
        (metadata_only.id, DocumentTextSourceUnavailable),
        (no_sha.id, DocumentTextSourceUnavailable),
        (r"C:\evidence\source.pdf", DocumentTextError),
    ):
        try:
            resolve_source_document(db, case_ref="PR03-A", document_id=document_id)
            raise AssertionError(f"invalid source accepted: {document_id!r}")
        except error_type:
            pass

    for unavailable_document in (metadata_only, no_sha):
        try:
            stage_extraction(
                db,
                document=unavailable_document,
                extraction_profile="default-v1",
                status="processing",
                executor_type="native",
            )
            raise AssertionError(
                f"unavailable document was stageable: {unavailable_document.id}"
            )
        except DocumentTextSourceUnavailable:
            pass

    try:
        stage_extraction(
            db,
            document=available,
            extraction_profile="missing-page-provenance",
            status="ready",
            executor_type="native",
            pages=[{"page_number": 1, "raw_text": "must not infer"}],
        )
        raise AssertionError("new page provenance was inferred from the parent")
    except DocumentTextError:
        pass

    current_sha = available.sha256
    old_sha = "0" * 64
    available.sha256 = old_sha
    old = stage_extraction(db, document=available, extraction_profile="default-v1", status="ready", executor_type="native", pages=[{"page_number": 1, "raw_text": "old sha", "executor_type": "native", "engine": "pypdf", "engine_version": "5.9.0", "status": "ready"}], completed_at=now)
    db.commit()
    assert old.source_sha256 == old_sha

    available.sha256 = current_sha
    current = stage_extraction(db, document=available, extraction_profile="default-v1", status="ready", executor_type="native", pages=[{"page_number": 1, "raw_text": "raw", "executor_type": "native", "engine": "pypdf", "engine_version": "5.9.0", "status": "ready", "reviewed_text": "reviewed"}], completed_at=now)
    stage_extraction(db, document=available, extraction_profile="other-profile", status="ready", executor_type="native", pages=[{"page_number": 1, "raw_text": "other", "executor_type": "native", "engine": "pypdf", "engine_version": "5.9.0", "status": "ready"}], completed_at=now)
    db.commit()

    reusable = find_latest_reusable_extraction(db, document=available, extraction_profile="default-v1")
    assert reusable is not None and reusable.id == current.id
    assert reusable.id != old.id
    assert find_latest_reusable_extraction(db, document=available, extraction_profile="missing-profile") is None
    payload = serialize_extraction(reusable)
    assert payload["pages"][0]["raw_text"] == "raw"
    assert payload["pages"][0]["reviewed_text"] == "reviewed"

    duplicate = DocumentTextExtraction(
        shared_case_id=case_a.id, shared_document_id=available.id,
        source_sha256=available.sha256, capability="document.extract_text",
        extraction_profile="duplicate-test", status="processing",
        executor_type="native", created_at=now,
        pages=[
            DocumentTextPage(page_number=1, raw_text="first", executor_type="native", engine="pypdf", engine_version="5.9.0", status="ready"),
            DocumentTextPage(page_number=1, raw_text="duplicate", executor_type="native", engine="pypdf", engine_version="5.9.0", status="ready"),
        ],
    )
    db.add(duplicate)
    try:
        db.flush()
        raise AssertionError("duplicate page_number was accepted")
    except IntegrityError:
        db.rollback()

    db.close()
    engine.dispose()


def main() -> None:
    migration_path = REPO_ROOT / "alembic" / "versions" / "0015_pr03_page_provenance.py"
    assert 'down_revision = "0014_pr03_document_text"' in migration_path.read_text(encoding="utf-8")
    _assert_no_disallowed_engine_integration()
    with tempfile.TemporaryDirectory(prefix="circe-pr03-derived-") as tmp:
        root = Path(tmp)
        _service_smoke(root / "service.db")
        _migration_smoke(root / "migration")
    print("PR-03 DERIVED CONTENT SERVICE SMOKE: OK")
    print("models/constraints=ok; case/source isolation=ok; reuse fingerprint/profile=ok")
    print("raw/reviewed separation=ok; duplicate page rejected=ok; engine integrations=absent")
    print("migration=0014->0015/backfill/downgrade/re-upgrade on isolated temporary database")


if __name__ == "__main__":
    main()
