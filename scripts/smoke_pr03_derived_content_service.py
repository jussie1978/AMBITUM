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
PREVIOUS_HEAD = "0011_pr02_smart_metadata"
CURRENT_HEAD = "0014_pr03_document_text"


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
    _alembic(root, "upgrade", CURRENT_HEAD)
    db_path = root / "athena.db"
    with closing(sqlite3.connect(db_path)) as db:
        assert db.execute("SELECT version_num FROM alembic_version").fetchone()[0] == CURRENT_HEAD
        tables = {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        assert {"document_text_extractions", "document_text_pages"}.issubset(tables)

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
    assert "ck_document_text_pages_page_number" in page_checks
    assert "uq_document_text_pages_extraction_page" in page_uniques
    assert {
        "ix_document_text_extractions_shared_case_id",
        "ix_document_text_extractions_shared_document_id",
        "ix_document_text_extractions_reuse_lookup",
    }.issubset(extraction_indexes)
    engine.dispose()

    _alembic(root, "downgrade", PREVIOUS_HEAD)
    with closing(sqlite3.connect(db_path)) as db:
        tables = {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        assert "document_text_extractions" not in tables
        assert "document_text_pages" not in tables
    _alembic(root, "upgrade", CURRENT_HEAD)


def _assert_no_disallowed_engine_integration() -> None:
    source_paths = (
        REPO_ROOT / "app" / "services" / "document_text_service.py",
        REPO_ROOT / "app" / "services" / "document_text_native_executor.py",
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
    forbidden = {"openai", "pytesseract", "fitz", "ollama", "transformers"}
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

    current_sha = available.sha256
    old_sha = "0" * 64
    available.sha256 = old_sha
    old = stage_extraction(db, document=available, extraction_profile="default-v1", status="ready", executor_type="native", pages=[{"page_number": 1, "raw_text": "old sha"}], completed_at=now)
    db.commit()
    assert old.source_sha256 == old_sha

    available.sha256 = current_sha
    current = stage_extraction(db, document=available, extraction_profile="default-v1", status="ready", executor_type="native", pages=[{"page_number": 1, "raw_text": "raw", "reviewed_text": "reviewed"}], completed_at=now)
    stage_extraction(db, document=available, extraction_profile="other-profile", status="ready", executor_type="native", pages=[{"page_number": 1, "raw_text": "other"}], completed_at=now)
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
            DocumentTextPage(page_number=1, raw_text="first"),
            DocumentTextPage(page_number=1, raw_text="duplicate"),
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
    migration_path = REPO_ROOT / "alembic" / "versions" / "0014_pr03_document_text.py"
    assert 'down_revision = "0011_pr02_smart_metadata"' in migration_path.read_text(encoding="utf-8")
    _assert_no_disallowed_engine_integration()
    with tempfile.TemporaryDirectory(prefix="circe-pr03-derived-") as tmp:
        root = Path(tmp)
        _service_smoke(root / "service.db")
        _migration_smoke(root / "migration")
    print("PR-03 DERIVED CONTENT SERVICE SMOKE: OK")
    print("models/constraints=ok; case/source isolation=ok; reuse fingerprint/profile=ok")
    print("raw/reviewed separation=ok; duplicate page rejected=ok; engine integrations=absent")
    print("migration=0011->0014/downgrade/re-upgrade on isolated temporary database")


if __name__ == "__main__":
    main()
