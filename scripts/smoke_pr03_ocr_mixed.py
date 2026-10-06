"""Focused smoke for PR-03 local OCR and mixed page provenance."""

from __future__ import annotations

import hashlib
import tempfile
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from pypdf import PdfReader, PdfWriter
from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.derived_content import DocumentTextExtraction  # noqa: F401
from app.models.platea import SharedCase, SharedDocument
from app.services import document_text_service
from app.services.document_text_service import (
    DocumentTextNotFound,
    execute_document_text_extraction,
)
from app.services.storage_service import LocalCaseStorage


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _text_image(path: Path, text: str, image_format: str) -> None:
    image = Image.new("RGB", (1800, 500), "white")
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(r"C:\Windows\Fonts\arial.ttf", 96)
    draw.text((70, 170), text, font=font, fill="black")
    image.save(path, format=image_format, quality=96, dpi=(300, 300))


def _image_pdf(image_path: Path, pdf_path: Path) -> None:
    with Image.open(image_path) as image:
        image.convert("RGB").save(pdf_path, "PDF", resolution=300)


def _native_pdf(path: Path, text: str) -> None:
    writer = PdfWriter()
    font = DictionaryObject(
        {
            NameObject("/Type"): NameObject("/Font"),
            NameObject("/Subtype"): NameObject("/Type1"),
            NameObject("/BaseFont"): NameObject("/Helvetica"),
        }
    )
    font_ref = writer._add_object(font)
    page = writer.add_blank_page(width=612, height=792)
    page[NameObject("/Resources")] = DictionaryObject(
        {NameObject("/Font"): DictionaryObject({NameObject("/F1"): font_ref})}
    )
    stream = DecodedStreamObject()
    stream.set_data(f"BT /F1 18 Tf 72 720 Td ({text}) Tj ET".encode("ascii"))
    page[NameObject("/Contents")] = writer._add_object(stream)
    with path.open("wb") as target:
        writer.write(target)


def _mixed_pdf(native_path: Path, scan_path: Path, output_path: Path) -> None:
    writer = PdfWriter()
    writer.add_page(PdfReader(native_path).pages[0])
    writer.add_page(PdfReader(scan_path).pages[0])
    with output_path.open("wb") as target:
        writer.write(target)


def _normalized(text: str) -> str:
    return unicodedata.normalize("NFC", text).upper()


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="circe-pr03-ocr-") as tmp:
        root = Path(tmp)
        storage_root = root / "storage"
        stored_dir = storage_root / "cases" / "1" / "documents"
        stored_dir.mkdir(parents=True)

        png_path = stored_dir / "portuguese.png"
        jpeg_path = stored_dir / "portuguese.jpg"
        scan_pdf_path = stored_dir / "scan.pdf"
        native_pdf_path = stored_dir / "native.pdf"
        mixed_pdf_path = stored_dir / "mixed.pdf"
        blank_path = stored_dir / "blank.png"
        blank_pdf_path = stored_dir / "blank.pdf"
        mixed_blank_pdf_path = stored_dir / "mixed-blank.pdf"
        corrupt_path = stored_dir / "corrupt.pdf"
        _text_image(png_path, "AÇÃO PÚBLICA PORTUGUÊS", "PNG")
        _text_image(jpeg_path, "AÇÃO PÚBLICA PORTUGUÊS", "JPEG")
        _image_pdf(png_path, scan_pdf_path)
        _native_pdf(native_pdf_path, "CAMADA NATIVA")
        _mixed_pdf(native_pdf_path, scan_pdf_path, mixed_pdf_path)
        Image.new("RGB", (1200, 400), "white").save(blank_path, "PNG")
        _image_pdf(blank_path, blank_pdf_path)
        _mixed_pdf(native_pdf_path, blank_pdf_path, mixed_blank_pdf_path)
        corrupt_path.write_bytes(b"not a pdf")
        originals = {
            path: path.read_bytes()
            for path in (
                png_path,
                jpeg_path,
                scan_pdf_path,
                native_pdf_path,
                mixed_pdf_path,
                blank_path,
                blank_pdf_path,
                mixed_blank_pdf_path,
                corrupt_path,
            )
        }

        engine = create_engine(f"sqlite:///{root / 'service.db'}")

        @event.listens_for(engine, "connect")
        def _enable_foreign_keys(connection, _record) -> None:
            connection.execute("PRAGMA foreign_keys=ON")

        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)
        db = Session()
        now = datetime.now(timezone.utc)
        case_a = SharedCase(case_ref="OCR-A", title="Caso A", status="aberto", published_by="smoke", published_at=now, published_version=1)
        case_b = SharedCase(case_ref="OCR-B", title="Caso B", status="aberto", published_by="smoke", published_at=now, published_version=1)
        db.add_all([case_a, case_b])
        db.flush()

        def add_document(path: Path, mime_type: str, case=case_a) -> SharedDocument:
            document = SharedDocument(
                shared_case_id=case.id,
                filename=path.name,
                file_type=path.suffix.lstrip("."),
                mime_type=mime_type,
                sha256=_sha256(path),
                storage_relpath=path.relative_to(storage_root).as_posix(),
            )
            db.add(document)
            return document

        scan = add_document(scan_pdf_path, "application/pdf")
        native = add_document(native_pdf_path, "application/pdf")
        mixed = add_document(mixed_pdf_path, "application/pdf")
        png = add_document(png_path, "image/png")
        jpeg = add_document(jpeg_path, "image/jpeg")
        blank = add_document(blank_path, "image/png")
        mixed_blank = add_document(mixed_blank_pdf_path, "application/pdf")
        corrupt = add_document(corrupt_path, "application/pdf")
        foreign = add_document(png_path, "image/png", case_b)
        db.commit()

        storage = LocalCaseStorage(storage_root)
        real_ocr = document_text_service.extract_ocr_image
        ocr_calls = 0

        def counting_ocr(image):
            nonlocal ocr_calls
            ocr_calls += 1
            return real_ocr(image)

        document_text_service.extract_ocr_image = counting_ocr
        try:
            digital_result = execute_document_text_extraction(db, storage=storage, case_ref="OCR-A", document_id=native.id, extraction_profile="ocr-v1")
            assert digital_result.extraction.executor_type == "native"
            assert ocr_calls == 0

            scan_result = execute_document_text_extraction(db, storage=storage, case_ref="OCR-A", document_id=scan.id, extraction_profile="ocr-v1")
            assert scan_result.extraction.executor_type == "ocr"
            assert scan_result.extraction.status == "ready"
            assert scan_result.extraction.pages[0].executor_type == "ocr"
            recognized = _normalized(scan_result.extraction.pages[0].raw_text)
            assert "AÇÃO" in recognized and "PORTUGUÊS" in recognized
            db.commit()

            calls_before_reuse = ocr_calls
            reused = execute_document_text_extraction(db, storage=storage, case_ref="OCR-A", document_id=scan.id, extraction_profile="ocr-v1")
            assert reused.reused and reused.extraction.id == scan_result.extraction.id
            assert ocr_calls == calls_before_reuse

            mixed_result = execute_document_text_extraction(db, storage=storage, case_ref="OCR-A", document_id=mixed.id, extraction_profile="ocr-v1")
            assert mixed_result.extraction.executor_type == "mixed"
            assert mixed_result.extraction.engine is None
            assert [page.executor_type for page in mixed_result.extraction.pages] == ["native", "ocr"]
            assert [page.page_number for page in mixed_result.extraction.pages] == [1, 2]
            assert all(page.status == "ready" for page in mixed_result.extraction.pages)

            for document in (png, jpeg):
                image_result = execute_document_text_extraction(db, storage=storage, case_ref="OCR-A", document_id=document.id, extraction_profile="ocr-v1")
                assert image_result.extraction.executor_type == "ocr"
                assert image_result.extraction.pages[0].executor_type == "ocr"
                assert "AÇÃO" in _normalized(image_result.extraction.pages[0].raw_text)

            blank_result = execute_document_text_extraction(db, storage=storage, case_ref="OCR-A", document_id=blank.id, extraction_profile="ocr-v1")
            blank_page = blank_result.extraction.pages[0]
            assert blank_result.extraction.status == "failed"
            assert blank_page.status == "failed"
            assert blank_page.error_code == "ocr_text_not_obtained"
            assert blank_page.fallback_candidate == "vlm"
            assert blank_result.fallback_candidate == "vlm"

            partial_result = execute_document_text_extraction(db, storage=storage, case_ref="OCR-A", document_id=mixed_blank.id, extraction_profile="ocr-v1")
            assert partial_result.extraction.executor_type == "mixed"
            assert partial_result.extraction.status == "failed"
            assert [page.status for page in partial_result.extraction.pages] == ["ready", "failed"]
            assert partial_result.extraction.pages[0].raw_text.strip()
            assert partial_result.extraction.pages[1].fallback_candidate == "vlm"

            calls_before_corrupt = ocr_calls
            corrupt_result = execute_document_text_extraction(db, storage=storage, case_ref="OCR-A", document_id=corrupt.id, extraction_profile="ocr-v1")
            assert corrupt_result.extraction.executor_type == "native"
            assert corrupt_result.extraction.error_code == "native_extraction_failed"
            assert not corrupt_result.extraction.pages
            assert ocr_calls == calls_before_corrupt

            try:
                execute_document_text_extraction(db, storage=storage, case_ref="OCR-A", document_id=foreign.id, extraction_profile="ocr-v1")
                raise AssertionError("cross-case document accepted")
            except DocumentTextNotFound:
                pass
        finally:
            document_text_service.extract_ocr_image = real_ocr

        assert all(path.read_bytes() == content for path, content in originals.items())
        db.close()
        engine.dispose()

    print("PR-03 OCR/MIXED SMOKE: OK")
    print("digital/native; scan+png+jpeg/ocr; mixed/page-provenance; reuse=ok")
    print("empty/vlm-candidate; parser-error-not-masked; isolation/original=ok")


if __name__ == "__main__":
    main()
