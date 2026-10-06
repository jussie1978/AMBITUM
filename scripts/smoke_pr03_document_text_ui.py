"""Static/Jinja smoke for the minimal PR-03 document text surface."""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment


REPO_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    template_path = REPO_ROOT / "app" / "templates" / "workspace.html"
    source = template_path.read_text(encoding="utf-8")
    Environment().parse(source)

    required_ui = (
        "Obter texto",
        "Processando…",
        "Sem extração.",
        "Texto disponível.",
        "Extração parcial",
        "Extração falhou.",
        "Erro HTTP",
        "Revisar texto",
        "Salvar revisão",
        "Revisão salva.",
        "Texto revisado",
        "Texto derivado de origem",
        "native:'Nativo'",
        "ocr:'OCR'",
        "vlm:'Visão'",
    )
    for marker in required_ui:
        assert marker in source, marker

    assert "/api/cases/" in source
    assert "/text-extraction" in source
    assert "/pages/" in source and "/review" in source
    assert 'href="/api/documents/{{ item.id }}/original"' in source
    assert "Melhorar extração" not in source
    assert "innerHTML" not in source

    print("PR-03 DOCUMENT TEXT UI SMOKE: OK")
    print("jinja=parse; obtain/states/pages/provenance/review=present")
    print("text-only rendering=escaped; original-link=preserved")


if __name__ == "__main__":
    main()
