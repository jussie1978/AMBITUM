"""PR-02 service and disposable Alembic migration smoke checks."""

from __future__ import annotations

import os
import sqlite3
import subprocess
import sys
import tempfile
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.platea import SharedCase, SharedDocument, SharedPerson
from app.models.smart_metadata import AssetSmartMetadata  # noqa: F401
from app.services.smart_metadata_service import SmartMetadataError, apply_batch, list_metadata


PREVIOUS_HEAD = "0010_ux03a_product_sections"
CURRENT_HEAD = "0011_pr02_smart_metadata"
SMART_TABLE = "asset_smart_metadata"
PRODUCT_TABLES = {
    "workspace_products",
    "workspace_product_sections",
    "workspace_product_section_blocks",
}


def _alembic(data_dir: Path, *args: str) -> None:
    env = os.environ.copy()
    env["DATA_DIR"] = str(data_dir)
    result = subprocess.run(
        [sys.executable, "-m", "alembic", *args],
        cwd=Path(__file__).resolve().parents[1],
        env=env,
        text=True,
        capture_output=True,
    )
    if result.returncode:
        raise AssertionError(
            f"Alembic failed ({' '.join(args)}):\n{result.stdout}\n{result.stderr}"
        )


def _tables(db_path: Path) -> set[str]:
    with closing(sqlite3.connect(db_path)) as db:
        return {
            row[0]
            for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")
        }


def _migration_smoke(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    fresh_dir = root / "fresh"
    fresh_dir.mkdir()
    _alembic(fresh_dir, "upgrade", "head")
    fresh_db = fresh_dir / "athena.db"
    assert SMART_TABLE in _tables(fresh_db)
    with closing(sqlite3.connect(fresh_db)) as db:
        assert db.execute("SELECT version_num FROM alembic_version").fetchone()[0] == CURRENT_HEAD
    _alembic(fresh_dir, "upgrade", "head")
    assert SMART_TABLE in _tables(fresh_db)

    fixture_dir = root / "fixture-0010"
    fixture_dir.mkdir()
    _alembic(fixture_dir, "upgrade", PREVIOUS_HEAD)
    fixture_db = fixture_dir / "athena.db"
    with closing(sqlite3.connect(fixture_db)) as db:
        db.execute(
            "INSERT INTO shared_cases (id, case_ref, title, status, published_by, published_at, published_version) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (41, "PR02-MIG", "Caso sintético", "aberto", "smoke", "2026-09-28 12:00:00", 2),
        )
        db.execute(
            "INSERT INTO shared_documents (id, shared_case_id, document_ref, filename, file_type, sha256, description, imported_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (42, 41, "PR02-DOC", "metadata-only.txt", "txt", "d" * 64, "preservar", "2026-09-28"),
        )
        db.execute(
            "INSERT INTO investigative_workspaces (id, shared_case_id, created_by_operator_id, created_by_username, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
            (43, 41, 7, "pr02-smoke", "2026-09-28 12:00:00", "2026-09-28 12:00:00"),
        )
        db.execute(
            "INSERT INTO workspace_products (id, workspace_id, title, revision, created_by_operator_id, created_by_username, updated_by_operator_id, updated_by_username, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (44, 43, "Produto preservado", 3, 7, "pr02-smoke", 7, "pr02-smoke", "2026-09-28 12:00:00", "2026-09-28 12:00:00"),
        )
        db.execute(
            "INSERT INTO workspace_product_sections (id, product_id, title, body, position, created_by_operator_id, created_by_username, updated_by_operator_id, updated_by_username, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (45, 44, "Seção preservada", "Conteúdo", 0, 7, "pr02-smoke", 7, "pr02-smoke", "2026-09-28 12:00:00", "2026-09-28 12:00:00"),
        )
        db.commit()
        before = {
            "case": db.execute("SELECT * FROM shared_cases WHERE id=41").fetchone(),
            "document": db.execute("SELECT * FROM shared_documents WHERE id=42").fetchone(),
            "workspace": db.execute("SELECT * FROM investigative_workspaces WHERE id=43").fetchone(),
            "product": db.execute("SELECT * FROM workspace_products WHERE id=44").fetchone(),
            "section": db.execute("SELECT * FROM workspace_product_sections WHERE id=45").fetchone(),
        }

    _alembic(fixture_dir, "upgrade", "head")
    assert SMART_TABLE in _tables(fixture_db)
    with closing(sqlite3.connect(fixture_db)) as db:
        after = {
            "case": db.execute("SELECT * FROM shared_cases WHERE id=41").fetchone(),
            "document": db.execute("SELECT * FROM shared_documents WHERE id=42").fetchone(),
            "workspace": db.execute("SELECT * FROM investigative_workspaces WHERE id=43").fetchone(),
            "product": db.execute("SELECT * FROM workspace_products WHERE id=44").fetchone(),
            "section": db.execute("SELECT * FROM workspace_product_sections WHERE id=45").fetchone(),
        }
        assert after == before
        assert db.execute("SELECT storage_relpath FROM shared_documents WHERE id=42").fetchone()[0] is None
        assert db.execute("SELECT version_num FROM alembic_version").fetchone()[0] == CURRENT_HEAD

    _alembic(fixture_dir, "downgrade", PREVIOUS_HEAD)
    assert SMART_TABLE not in _tables(fixture_db)
    assert PRODUCT_TABLES.issubset(_tables(fixture_db))
    _alembic(fixture_dir, "upgrade", "head")
    assert SMART_TABLE in _tables(fixture_db)
    with closing(sqlite3.connect(fixture_db)) as db:
        assert db.execute("SELECT * FROM shared_cases WHERE id=41").fetchone() == before["case"]
        assert db.execute("SELECT * FROM shared_documents WHERE id=42").fetchone() == before["document"]
        assert db.execute("SELECT * FROM investigative_workspaces WHERE id=43").fetchone() == before["workspace"]
        assert db.execute("SELECT * FROM workspace_products WHERE id=44").fetchone() == before["product"]
        assert db.execute("SELECT * FROM workspace_product_sections WHERE id=45").fetchone() == before["section"]


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="circe-pr02-service-") as tmp:
        engine = create_engine(f"sqlite:///{Path(tmp) / 'service.db'}")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)
        db = Session()
        now = datetime.now(timezone.utc)
        case_a = SharedCase(case_ref="PR02-A", title="Caso A", status="aberto", published_by="smoke", published_at=now, published_version=1)
        case_b = SharedCase(case_ref="PR02-B", title="Caso B", status="aberto", published_by="smoke", published_at=now, published_version=1)
        db.add_all([case_a, case_b])
        db.flush()
        docs = [
            SharedDocument(shared_case_id=case_a.id, document_ref=f"PR02-DOC-{i}", filename=f"doc-{i}.txt", file_type="txt", sha256=str(i) * 64, description=None, imported_at="2026-09-28")
            for i in (1, 2)
        ]
        foreign_doc = SharedDocument(shared_case_id=case_b.id, document_ref="PR02-DOC-X", filename="foreign.txt", file_type="txt", sha256="e" * 64, description=None, imported_at="2026-09-28")
        same_case_person = SharedPerson(shared_case_id=case_a.id, full_name="Pessoa A")
        foreign_person = SharedPerson(shared_case_id=case_b.id, full_name="Pessoa B")
        db.add_all([*docs, foreign_doc, same_case_person, foreign_person])
        db.commit()
        ids = [doc.id for doc in docs]

        assert list_metadata(db, case_ref=case_a.case_ref) == []
        free_target = apply_batch(db, case_ref=case_a.case_ref, document_ids=ids, operation="add", kind="target", value="Alvo livre", linked_person_id=None, operator_id=7, operator_username="service-smoke", provenance="human_confirmed")
        assert free_target.affected_count == 2
        db.commit()
        repeated = apply_batch(db, case_ref=case_a.case_ref, document_ids=ids, operation="add", kind="target", value="Alvo livre", linked_person_id=None, operator_id=7, operator_username="service-smoke")
        assert repeated.affected_count == 0
        db.commit()
        rows = list_metadata(db, case_ref=case_a.case_ref, kind="target")
        assert len(rows) == 2 and all(row["provenance"] == "human_confirmed" for row in rows)

        # Reapplying an equivalent value is idempotent and must not rewrite
        # the original AI provenance into a later human action.
        db.add_all([
            AssetSmartMetadata(
                shared_case_id=case_a.id,
                shared_document_id=ids[0],
                kind="topic",
                value_text="Candidato IA",
                linked_person_id=None,
                provenance="ai_suggested",
                created_by_operator_id=None,
                created_by_username="ai-provider",
                created_at=now,
                updated_at=now,
            ),
            AssetSmartMetadata(
                shared_case_id=case_a.id,
                shared_document_id=ids[1],
                kind="source_kind",
                value_text="Derivado do sistema",
                linked_person_id=None,
                provenance="system_derived",
                created_by_operator_id=None,
                created_by_username="system",
                created_at=now,
                updated_at=now,
            ),
        ])
        db.commit()
        reapplied = apply_batch(
            db, case_ref=case_a.case_ref, document_ids=[ids[0]],
            operation="add", kind="topic", value="Candidato IA",
            linked_person_id=None, operator_id=7,
            operator_username="service-smoke",
        )
        assert reapplied.affected_count == 0
        db.commit()
        assert list_metadata(
            db, case_ref=case_a.case_ref, kind="topic"
        )[0]["provenance"] == "ai_suggested"
        system_reapplied = apply_batch(
            db, case_ref=case_a.case_ref, document_ids=[ids[1]],
            operation="add", kind="source_kind", value="Derivado do sistema",
            linked_person_id=None, operator_id=7,
            operator_username="service-smoke",
        )
        assert system_reapplied.affected_count == 0
        db.commit()
        assert list_metadata(
            db, case_ref=case_a.case_ref, kind="source_kind"
        )[0]["provenance"] == "system_derived"

        linked = apply_batch(db, case_ref=case_a.case_ref, document_ids=[ids[0]], operation="add", kind="target", value="Pessoa vinculada", linked_person_id=same_case_person.id, operator_id=7, operator_username="service-smoke")
        assert linked.affected_count == 1 and linked.linked_person_id == same_case_person.id
        db.commit()

        before_cross = [(row["shared_document_id"], row["kind"], row["value_text"]) for row in list_metadata(db, case_ref=case_a.case_ref)]
        try:
            apply_batch(db, case_ref=case_a.case_ref, document_ids=[ids[0], foreign_doc.id], operation="add", kind="tag", value="must not partially write", linked_person_id=None, operator_id=7, operator_username="service-smoke")
            raise AssertionError("cross-case document batch was accepted")
        except SmartMetadataError:
            db.rollback()
        assert [(row["shared_document_id"], row["kind"], row["value_text"]) for row in list_metadata(db, case_ref=case_a.case_ref)] == before_cross
        try:
            apply_batch(db, case_ref=case_a.case_ref, document_ids=[ids[0]], operation="add", kind="target", value="must not link foreign", linked_person_id=foreign_person.id, operator_id=7, operator_username="service-smoke")
            raise AssertionError("cross-case person link was accepted")
        except SmartMetadataError:
            db.rollback()
        assert [(row["shared_document_id"], row["kind"], row["value_text"]) for row in list_metadata(db, case_ref=case_a.case_ref)] == before_cross

        removed = apply_batch(db, case_ref=case_a.case_ref, document_ids=ids, operation="remove", kind="target", value="Alvo livre", linked_person_id=None, operator_id=7, operator_username="service-smoke")
        assert removed.affected_count == 2
        db.commit()
        assert len(list_metadata(db, case_ref=case_a.case_ref)) == 3
        db.close()
        engine.dispose()
        _migration_smoke(Path(tmp) / "migrations")

    print("PR-02 SMART METADATA SERVICE SMOKE: OK")
    print("empty=ok; add-idempotent-remove=ok; free-and-linked-target=ok")
    print("cross-case-document/person=atomic-rejection; provenance=origin-preserved")
    print("migration=fresh-head/repeated-head/0010-preservation/downgrade-reupgrade")


if __name__ == "__main__":
    main()
