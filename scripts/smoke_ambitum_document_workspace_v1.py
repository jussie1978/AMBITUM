"""Static/Jinja smoke for AMBITUM Document Workspace V1."""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment


REPO_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    template = REPO_ROOT / "app" / "templates" / "platea_detail.html"
    source = template.read_text(encoding="utf-8")
    Environment().parse(source)

    required_surface = (
        'class="materials-list__body"',
        'data-material-select="{{ item.id }}"',
        'data-document-detail="{{ item.id }}"',
        'src="/api/documents/{{ item.id }}/original?disposition=inline" loading="lazy"',
        'target="_blank" rel="noopener">Abrir original',
        "item.mime_type in ['application/pdf', 'image/png', 'image/jpeg']",
        "Pré-visualização indisponível",
        "Original / Documento",
        "Texto / Revisão",
        "Texto extraído",
        "Texto revisado",
        "Revisar texto",
        "Salvar revisão",
        "native:'Nativo'",
        "ocr:'OCR'",
        "vlm:'Visão'",
    )
    for marker in required_surface:
        assert marker in source, marker

    required_interaction = (
        "function selectDocument(documentId)",
        "item.hidden=item.dataset.documentDetail!==targetId",
        "setDocumentView(detail,'original')",
        "documentTextState.has(targetId)",
        "trigger.disabled=true",
        "finally{trigger.disabled=false}",
        "pagesContainer.replaceChildren()",
        "reviewedText.textContent=page.reviewed_text",
        "raw.textContent=page.raw_text",
    )
    for marker in required_interaction:
        assert marker in source, marker

    selection = source.split("function selectDocument(documentId)", 1)[1]
    selection = selection.split("function documentTextEndpoint", 1)[0]
    assert "/original" not in selection
    assert "window.open" not in selection
    assert "window.location" not in selection
    assert "event.preventDefault()" in selection
    assert "event.stopPropagation()" in selection
    assert '<button class="material-item' in source
    assert '<a class="material-item' not in source
    assert source.count('href="/api/documents/{{ item.id }}/original"') == 1
    assert 'href="/api/documents/{{ item.id }}/original?disposition=inline"' not in source
    assert "/api/cases/" in source and "/text-extraction" in source
    assert "/pages/" in source and "/review" in source
    assert "storage_relpath" not in source
    assert "innerHTML" not in source
    assert "PDF.js" not in source and "pdfjs" not in source.lower()
    assert "URL.createObjectURL" not in source
    assert "Analisar com IA" not in source

    print("AMBITUM DOCUMENT WORKSPACE V1 SMOKE: OK")
    print("materials/selection/original/native-pdf/responsive-panels=ok")
    print("text/provenance/review/raw-isolation/error-states=ok")
    print("storage-path-hidden; assistant/shell-contract=preserved")


if __name__ == "__main__":
    main()
