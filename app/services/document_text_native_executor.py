"""Deterministic native text extraction for governed PDF paths."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pypdf
from pypdf import PdfReader


ENGINE_NAME = "pypdf"
ENGINE_VERSION = pypdf.__version__


class NativeTextExtractionError(Exception):
    """Raised when native extraction cannot inspect the supplied PDF."""


@dataclass(frozen=True)
class NativeTextPage:
    page_number: int
    raw_text: str


@dataclass(frozen=True)
class NativeTextResult:
    pages: tuple[NativeTextPage, ...]
    engine: str
    engine_version: str
    text_obtained: bool
    fallback_reason: str | None


def extract_native_pdf(source_path: Path) -> NativeTextResult:
    """Extract page text without mutating the already-governed source path."""
    if not isinstance(source_path, Path):
        raise TypeError("source_path must be a pathlib.Path")

    try:
        reader = PdfReader(source_path)
        pages = tuple(
            NativeTextPage(
                page_number=index,
                raw_text=page.extract_text() or "",
            )
            for index, page in enumerate(reader.pages, start=1)
        )
    except Exception as exc:
        raise NativeTextExtractionError("PDF native text extraction failed.") from exc

    text_obtained = any(page.raw_text.strip() for page in pages)
    return NativeTextResult(
        pages=pages,
        engine=ENGINE_NAME,
        engine_version=ENGINE_VERSION,
        text_obtained=text_obtained,
        fallback_reason=None if text_obtained else "no_text_content",
    )
