"""Deterministic smoke for local VLM fallback without loading a model."""

from __future__ import annotations

import ast
import hashlib
import inspect
import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import httpx
from PIL import Image
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.database import Base
from app.models.derived_content import DocumentTextExtraction  # noqa: F401
from app.models.platea import SharedCase, SharedDocument
from app.services import document_text_service, document_text_vlm_executor
from app.services.document_text_native_executor import NativeTextPage, NativeTextResult
from app.services.document_text_ocr_executor import OCRTextResult
from app.services.document_text_service import execute_document_text_extraction
from app.services.document_text_vlm_executor import VLMExecutionError, extract_vlm_image
from app.services.storage_service import LocalCaseStorage


REPO_ROOT = Path(__file__).resolve().parents[1]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _assert_no_forbidden_provider_imports() -> None:
    paths = (
        REPO_ROOT / "app" / "config.py",
        REPO_ROOT / "app" / "services" / "document_text_service.py",
        REPO_ROOT / "app" / "services" / "document_text_vlm_executor.py",
    )
    modules: set[str] = set()
    for path in paths:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        modules.update(
            node.module or ""
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
        )
        modules.update(
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        )
    forbidden = {"openai", "ollama", "paddleocr", "pytesseract", "tesseract"}
    assert not modules.intersection(forbidden)


def main() -> None:
    _assert_no_forbidden_provider_imports()
    assert list(inspect.signature(extract_vlm_image).parameters) == ["image"]

    original_base_url = settings.vlm_base_url
    original_model = settings.vlm_model
    original_client_factory = document_text_vlm_executor._http_client
    original_native = document_text_service.extract_native_pdf
    original_render = document_text_service._render_pdf_page
    original_ocr = document_text_service.extract_ocr_image

    requests: list[dict] = []
    response_mode = {"value": "text"}

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url == httpx.URL("http://127.0.0.1:18080/v1/chat/completions")
        payload = json.loads(request.content)
        requests.append(payload)
        assert payload["model"] == "Qwen3-VL-smoke-Q4_K_M"
        content = payload["messages"][0]["content"]
        image_items = [item for item in content if item.get("type") == "image_url"]
        assert len(image_items) == 1
        assert image_items[0]["image_url"]["url"].startswith("data:image/png;base64,")
        serialized = json.dumps(payload, ensure_ascii=False)
        assert "storage_relpath" not in serialized
        assert "VLM-CASE" not in serialized

        if response_mode["value"] == "timeout":
            raise httpx.ReadTimeout("synthetic timeout", request=request)
        if response_mode["value"] == "http-error":
            return httpx.Response(503, json={"error": "offline"})
        content_text = "" if response_mode["value"] == "empty" else "TEXTO VLM FIEL"
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": content_text}}]},
        )

    transport = httpx.MockTransport(handler)
    settings.vlm_base_url = "http://127.0.0.1:18080/v1"
    settings.vlm_model = "Qwen3-VL-smoke-Q4_K_M"
    document_text_vlm_executor._http_client = lambda: httpx.Client(
        transport=transport,
        timeout=settings.vlm_timeout_seconds,
    )

    try:
        direct = extract_vlm_image(Image.new("RGB", (32, 32), "white"))
        assert direct.text_obtained and direct.raw_text == "TEXTO VLM FIEL"
        assert direct.engine == "qwen3-vl"
        assert direct.engine_version == settings.vlm_model

        response_mode["value"] = "timeout"
        try:
            extract_vlm_image(Image.new("RGB", (32, 32), "white"))
            raise AssertionError("timeout was accepted as successful text")
        except VLMExecutionError as exc:
            assert exc.code == "vlm_timeout"

        with tempfile.TemporaryDirectory(prefix="circe-pr03-vlm-") as tmp:
            root = Path(tmp)
            storage_root = root / "storage"
            stored_dir = storage_root / "cases" / "1" / "documents"
            stored_dir.mkdir(parents=True)

            engine = create_engine(f"sqlite:///{root / 'service.db'}")

            @event.listens_for(engine, "connect")
            def _enable_foreign_keys(connection, _record) -> None:
                connection.execute("PRAGMA foreign_keys=ON")

            Base.metadata.create_all(engine)
            Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)
            db = Session()
            now = datetime.now(timezone.utc)
            case = SharedCase(
                case_ref="VLM-CASE",
                title="VLM smoke",
                status="aberto",
                published_by="smoke",
                published_at=now,
                published_version=1,
            )
            db.add(case)
            db.flush()

            documents: dict[str, SharedDocument] = {}
            for name in (
                "native.pdf",
                "ocr.pdf",
                "fallback.pdf",
                "mixed.pdf",
                "empty.pdf",
                "http.pdf",
                "timeout.pdf",
            ):
                path = stored_dir / name
                path.write_bytes(f"synthetic:{name}".encode("ascii"))
                document = SharedDocument(
                    shared_case_id=case.id,
                    filename=name,
                    file_type="pdf",
                    mime_type="application/pdf",
                    sha256=_sha256(path),
                    storage_relpath=path.relative_to(storage_root).as_posix(),
                )
                documents[name] = document
                db.add(document)
            db.commit()

            def fake_native(source_path: Path) -> NativeTextResult:
                if source_path.name == "native.pdf":
                    texts = ("TEXTO NATIVO",)
                elif source_path.name == "mixed.pdf":
                    texts = ("TEXTO NATIVO", "", "")
                else:
                    texts = ("",)
                pages = tuple(
                    NativeTextPage(page_number=index, raw_text=text)
                    for index, text in enumerate(texts, start=1)
                )
                return NativeTextResult(
                    pages=pages,
                    engine="pypdf",
                    engine_version="smoke",
                    text_obtained=any(texts),
                    fallback_reason=None if any(texts) else "no_text_content",
                )

            def fake_render(_source_path: Path, page_number: int) -> Image.Image:
                return Image.new("RGB", (16, 16), (page_number, 0, 0))

            def fake_ocr(image: Image.Image) -> OCRTextResult:
                page_marker = image.getpixel((0, 0))[0]
                text = "TEXTO OCR" if page_marker == 2 else ""
                return OCRTextResult(
                    raw_text=text,
                    text_obtained=bool(text),
                    engine="rapidocr-onnxruntime",
                    engine_version="3.9.2",
                    model_profile="PP-OCRv6-small-pt",
                    parameters_json="{}",
                )

            document_text_service.extract_native_pdf = fake_native
            document_text_service._render_pdf_page = fake_render
            document_text_service.extract_ocr_image = fake_ocr
            storage = LocalCaseStorage(storage_root)

            requests_before = len(requests)
            native_result = execute_document_text_extraction(
                db, storage=storage, case_ref="VLM-CASE",
                document_id=documents["native.pdf"].id, extraction_profile="vlm-v1",
            )
            assert native_result.extraction.executor_type == "native"
            assert len(requests) == requests_before

            # For an OCR-success route, page marker 2 is needed.
            original_single_render = document_text_service._render_pdf_page
            document_text_service._render_pdf_page = lambda _path, _page: Image.new(
                "RGB", (16, 16), (2, 0, 0)
            )
            requests_before_ocr_success = len(requests)
            ocr_success = execute_document_text_extraction(
                db, storage=storage, case_ref="VLM-CASE",
                document_id=documents["ocr.pdf"].id, extraction_profile="ocr-success-v2",
            )
            assert ocr_success.extraction.pages[0].executor_type == "ocr"
            assert len(requests) == requests_before_ocr_success
            document_text_service._render_pdf_page = original_single_render

            response_mode["value"] = "text"
            requests_before_fallback = len(requests)
            fallback_result = execute_document_text_extraction(
                db, storage=storage, case_ref="VLM-CASE",
                document_id=documents["fallback.pdf"].id, extraction_profile="vlm-v1",
            )
            fallback_page = fallback_result.extraction.pages[0]
            assert len(requests) == requests_before_fallback + 1
            assert fallback_page.executor_type == "vlm"
            assert fallback_page.engine == "qwen3-vl"
            assert fallback_page.engine_version == settings.vlm_model
            assert fallback_page.status == "ready"
            assert fallback_page.raw_text == "TEXTO VLM FIEL"
            assert fallback_page.fallback_candidate is None

            mixed_result = execute_document_text_extraction(
                db, storage=storage, case_ref="VLM-CASE",
                document_id=documents["mixed.pdf"].id, extraction_profile="vlm-v1",
            )
            assert [page.executor_type for page in mixed_result.extraction.pages] == [
                "native", "ocr", "vlm"
            ]
            assert mixed_result.extraction.executor_type == "mixed"

            response_mode["value"] = "empty"
            empty_result = execute_document_text_extraction(
                db, storage=storage, case_ref="VLM-CASE",
                document_id=documents["empty.pdf"].id, extraction_profile="vlm-v1",
            )
            empty_page = empty_result.extraction.pages[0]
            assert empty_page.executor_type == "vlm"
            assert empty_page.status == "failed"
            assert empty_page.raw_text == ""
            assert empty_page.error_code == "vlm_text_not_obtained"

            for filename, mode, error_code in (
                ("http.pdf", "http-error", "vlm_http_error"),
                ("timeout.pdf", "timeout", "vlm_timeout"),
            ):
                response_mode["value"] = mode
                technical = execute_document_text_extraction(
                    db, storage=storage, case_ref="VLM-CASE",
                    document_id=documents[filename].id, extraction_profile="vlm-v1",
                )
                page = technical.extraction.pages[0]
                assert page.executor_type == "vlm"
                assert page.status == "failed"
                assert page.raw_text == ""
                assert page.error_code == error_code

            db.close()
            engine.dispose()
    finally:
        settings.vlm_base_url = original_base_url
        settings.vlm_model = original_model
        document_text_vlm_executor._http_client = original_client_factory
        document_text_service.extract_native_pdf = original_native
        document_text_service._render_pdf_page = original_render
        document_text_service.extract_ocr_image = original_ocr

    print("PR-03 VLM FALLBACK SMOKE: OK")
    print("native/ocr bypass; objective OCR fallback=one VLM call; mixed provenance=ok")
    print("empty/http/timeout explicit; governed endpoint/base64/single-image=ok")


if __name__ == "__main__":
    main()
