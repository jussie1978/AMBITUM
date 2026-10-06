"""Focused smoke for PR-03 native PDF text extraction."""

from __future__ import annotations

import hashlib
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from pypdf import PdfWriter
from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.derived_content import DocumentTextExtraction  # noqa: F401
from app.models.platea import SharedCase, SharedDocument
from app.services import document_text_service
from app.services.document_text_service import (
    DocumentTextError,
    DocumentTextNotFound,
    DocumentTextUnsupportedSource,
    execute_native_text_extraction,
)
from app.services.document_text_native_executor import extract_native_pdf
from app.services.storage_service import LocalCaseStorage


def _write_text_pdf(path: Path, page_texts: tuple[str, ...]) -> None:
    writer = PdfWriter()
    font = DictionaryObject(
        {
            NameObject("/Type"): NameObject("/Font"),
            NameObject("/Subtype"): NameObject("/Type1"),
            NameObject("/BaseFont"): NameObject("/Helvetica"),
        }
    )
    font_ref = writer._add_object(font)
    for text in page_texts:
        page = writer.add_blank_page(width=612, height=792)
        page[NameObject("/Resources")] = DictionaryObject(
            {
                NameObject("/Font"): DictionaryObject(
                    {NameObject("/F1"): font_ref}
                )
            }
        )
        stream = DecodedStreamObject()
        escaped = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        stream.set_data(f"BT /F1 12 Tf 72 720 Td ({escaped}) Tj ET".encode("ascii"))
        page[NameObject("/Contents")] = writer._add_object(stream)
    with path.open("wb") as target:
        writer.write(target)


def _write_blank_pdf(path: Path) -> None:
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    with path.open("wb") as target:
        writer.write(target)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="circe-pr03-native-") as tmp:
        root = Path(tmp)
        storage_root = root / "storage"
        stored_dir = storage_root / "cases" / "1" / "documents"
        stored_dir.mkdir(parents=True)
        digital_path = stored_dir / "digital-original"
        blank_path = stored_dir / "blank-original"
        _write_text_pdf(digital_path, ("Primeira pagina", "Segunda pagina"))
        _write_blank_pdf(blank_path)
        digital_before = digital_path.read_bytes()

        direct = extract_native_pdf(digital_path)
        assert direct.text_obtained is True
        assert [page.page_number for page in direct.pages] == [1, 2]
        assert "Primeira pagina" in direct.pages[0].raw_text
        assert "Segunda pagina" in direct.pages[1].raw_text
        blank_direct = extract_native_pdf(blank_path)
        assert blank_direct.text_obtained is False
        assert blank_direct.fallback_reason == "no_text_content"

        engine = create_engine(f"sqlite:///{root / 'service.db'}")

        @event.listens_for(engine, "connect")
        def _enable_foreign_keys(connection, _record) -> None:
            connection.execute("PRAGMA foreign_keys=ON")

        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)
        db = Session()
        now = datetime.now(timezone.utc)
        case_a = SharedCase(case_ref="NATIVE-A", title="Caso A", status="aberto", published_by="smoke", published_at=now, published_version=1)
        case_b = SharedCase(case_ref="NATIVE-B", title="Caso B", status="aberto", published_by="smoke", published_at=now, published_version=1)
        db.add_all([case_a, case_b])
        db.flush()
        digital = SharedDocument(shared_case_id=case_a.id, filename="digital.pdf", file_type="pdf", mime_type="application/pdf", sha256=_sha256(digital_path), storage_relpath=digital_path.relative_to(storage_root).as_posix())
        blank = SharedDocument(shared_case_id=case_a.id, filename="blank.pdf", file_type="pdf", mime_type="application/pdf", sha256=_sha256(blank_path), storage_relpath=blank_path.relative_to(storage_root).as_posix())
        foreign = SharedDocument(shared_case_id=case_b.id, filename="foreign.pdf", file_type="pdf", mime_type="application/pdf", sha256=_sha256(digital_path), storage_relpath=digital_path.relative_to(storage_root).as_posix())
        non_pdf = SharedDocument(shared_case_id=case_a.id, filename="notes.txt", file_type="txt", mime_type="text/plain", sha256=_sha256(digital_path), storage_relpath=digital_path.relative_to(storage_root).as_posix())
        db.add_all([digital, blank, foreign, non_pdf])
        db.commit()

        storage = LocalCaseStorage(storage_root)
        calls = 0
        ocr_calls = 0
        real_executor = document_text_service.extract_native_pdf
        real_ocr = document_text_service.extract_ocr_image

        def counting_executor(source_path: Path):
            nonlocal calls
            calls += 1
            return real_executor(source_path)

        def forbidden_ocr(_image):
            nonlocal ocr_calls
            ocr_calls += 1
            raise AssertionError("OCR must not run for a fully digital PDF")

        document_text_service.extract_native_pdf = counting_executor
        document_text_service.extract_ocr_image = forbidden_ocr
        try:
            first = execute_native_text_extraction(db, storage=storage, case_ref="NATIVE-A", document_id=digital.id, extraction_profile="native-v1")
            assert first.reused is False and first.text_obtained is True
            assert first.extraction.status == "ready"
            assert first.extraction.executor_type == "native"
            assert first.extraction.engine == "pypdf"
            assert first.extraction.engine_version
            assert [page.page_number for page in first.extraction.pages] == [1, 2]
            assert all(page.executor_type == "native" for page in first.extraction.pages)
            assert all(page.status == "ready" for page in first.extraction.pages)
            db.commit()

            second = execute_native_text_extraction(db, storage=storage, case_ref="NATIVE-A", document_id=digital.id, extraction_profile="native-v1")
            assert second.reused is True
            assert second.extraction.id == first.extraction.id
            assert calls == 1
            assert ocr_calls == 0

            calls_before_rejection = calls
            extraction_count = db.query(DocumentTextExtraction).count()
            try:
                execute_native_text_extraction(db, storage=storage, case_ref="NATIVE-A", document_id=non_pdf.id, extraction_profile="native-v1")
                raise AssertionError("non-PDF document was accepted")
            except DocumentTextUnsupportedSource as exc:
                assert exc.status_code == 415
                assert exc.code == "unsupported_source_type"
            assert calls == calls_before_rejection
            assert db.query(DocumentTextExtraction).count() == extraction_count
        finally:
            document_text_service.extract_native_pdf = real_executor
            document_text_service.extract_ocr_image = real_ocr

        try:
            execute_native_text_extraction(db, storage=storage, case_ref="NATIVE-A", document_id=foreign.id, extraction_profile="native-v1")
            raise AssertionError("cross-case document was accepted")
        except DocumentTextNotFound:
            pass
        try:
            execute_native_text_extraction(db, storage=storage, case_ref="NATIVE-A", document_id=str(digital_path), extraction_profile="native-v1")
            raise AssertionError("arbitrary path was accepted")
        except DocumentTextError:
            pass

        assert digital_path.read_bytes() == digital_before
        assert db.query(DocumentTextExtraction).filter(DocumentTextExtraction.status == "ready").count() == 1
        db.close()
        engine.dispose()

    print("PR-03 NATIVE TEXT SMOKE: OK")
    print("multipage/pages/provenance/ready=ok; reuse=no-second-execution")
    print("empty-text=failed-with-objective-signal; isolation/path/original=ok")


if __name__ == "__main__":
    main()
