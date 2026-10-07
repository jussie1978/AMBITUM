"""Focused Product Shell V1 smoke: shell, Case entry, and Materials slice."""

from __future__ import annotations

import tempfile
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from jinja2 import Environment
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from starlette.middleware.sessions import SessionMiddleware

from app.database import Base
from app.middleware.auth_guard import AuthGuard
from app.models.operator import Operator  # noqa: F401
from app.models.platea import SharedCase, SharedDocument
import app.routes.platea as platea_routes


REPO_ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = REPO_ROOT / "app" / "templates"


def _read(name: str) -> str:
    source = (TEMPLATES / name).read_text(encoding="utf-8")
    Environment().parse(source)
    return source


def _assert_static_shell() -> None:
    base = _read("base.html")
    sidebar = _read("partials/sidebar.html")
    home = _read("dashboard.html")
    cases = _read("platea_list.html")
    case = _read("platea_detail.html")
    assistant = _read("assistant.html")
    photo_surfaces = [
        _read("photos_list.html"),
        _read("photos_new.html"),
        _read("photos_detail.html"),
        _read("photos_compare.html"),
    ]

    assert "<title>AMBITUM</title>" in base
    assert '<div class="sidebar__brand-name">AMBITUM</div>' in sidebar
    nav_order = [
        sidebar.index("<span>Início</span>"),
        sidebar.index("<span>Assistente</span>"),
        sidebar.index("<span>Casos</span>"),
        sidebar.index("<span>Banco de Fotos</span>"),
    ]
    assert nav_order == sorted(nav_order)
    assert 'href="/assistant"' in sidebar
    assert 'href="/platea"' in sidebar
    assert 'href="/photos"' in sidebar
    assert 'href="/audit"' not in sidebar
    assert 'href="/admin"' not in sidebar
    assert 'href="/settings"' not in sidebar

    assert "Seu ambiente operacional" in home
    assert "catálogo funcional" not in home
    assert "planejado" not in home
    assert all(marker in home for marker in ("Assistente", "Casos", "Banco de Fotos"))
    assert "AMBITUM" in cases and "Casos" in cases
    assert "AMBITUM / ASSISTENTE" in assistant
    assert "Global · contexto local quando disponível" in assistant
    assert all("AMBITUM" in surface for surface in photo_surfaces)
    assert all('href="/assistant"' in surface for surface in photo_surfaces)

    required_case = (
        "Visão geral",
        "Materiais",
        "Documento selecionado",
        "Original",
        "Obter texto",
        "Revisar texto",
        "Salvar revisão",
        "Texto extraído",
        "native:'Nativo'",
        "ocr:'OCR'",
        "vlm:'Visão'",
        "/api/cases/",
        "/text-extraction",
        "/pages/",
        "/review",
    )
    for marker in required_case:
        assert marker in case, marker
    assert "Abrir Workspace" not in case
    assert "storage_relpath" not in case
    assert "innerHTML" not in case


def _assert_case_http() -> None:
    with tempfile.TemporaryDirectory(prefix="ambitum-product-shell-") as tmp:
        db_path = Path(tmp) / "shell.db"
        engine = create_engine(
            f"sqlite:///{db_path}",
            connect_args={"check_same_thread": False},
            poolclass=NullPool,
        )
        Base.metadata.create_all(bind=engine)
        Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = Session()
        now = datetime.now(timezone.utc)
        case_a = SharedCase(
            case_ref="SHELL-A",
            title="Caso Shell A",
            status="aberto",
            published_by="smoke",
            published_at=now,
            published_version=1,
        )
        case_b = SharedCase(
            case_ref="SHELL-B",
            title="Caso Shell B",
            status="aberto",
            published_by="smoke",
            published_at=now,
            published_version=1,
        )
        db.add_all([case_a, case_b])
        db.flush()
        db.add_all(
            [
                SharedDocument(
                    shared_case_id=case_a.id,
                    filename="material-a.pdf",
                    file_type="pdf",
                    mime_type="application/pdf",
                    storage_relpath="cases/a/material-a.pdf",
                ),
                SharedDocument(
                    shared_case_id=case_b.id,
                    filename="segredo-b.pdf",
                    file_type="pdf",
                    mime_type="application/pdf",
                    storage_relpath="cases/b/segredo-b.pdf",
                ),
            ]
        )
        db.commit()
        db.close()

        original_session = platea_routes.SessionLocal
        platea_routes.SessionLocal = Session
        app = FastAPI()
        app.add_middleware(AuthGuard)
        app.add_middleware(SessionMiddleware, secret_key="product-shell-smoke")
        app.include_router(platea_routes.router)

        @app.post("/login")
        async def login(request: Request):
            request.session["operator"] = {
                "id": 1,
                "username": "shell-smoke",
                "full_name": "Operador Shell",
                "role": "operator",
            }
            return JSONResponse({"ok": True})

        try:
            with TestClient(app) as client:
                unauthenticated = client.get("/platea/SHELL-A", follow_redirects=False)
                assert unauthenticated.status_code == 302
                assert client.post("/login").status_code == 200

                overview = client.get("/platea/SHELL-A")
                assert overview.status_code == 200
                assert "Caso Shell A" in overview.text
                assert "Abrir Workspace" not in overview.text

                materials = client.get("/platea/SHELL-A?view=materials")
                assert materials.status_code == 200
                assert "material-a.pdf" in materials.text
                assert "segredo-b.pdf" not in materials.text
                assert "Obter texto" in materials.text
                assert "Revisar texto" in materials.text
                assert "/api/documents/" in materials.text

                missing = client.get("/platea/INEXISTENTE", follow_redirects=False)
                assert missing.status_code == 302
                assert missing.headers["location"] == "/platea"
        finally:
            platea_routes.SessionLocal = original_session
            engine.dispose()


def main() -> None:
    _assert_static_shell()
    _assert_case_http()
    print("AMBITUM PRODUCT SHELL V1 SMOKE: OK")
    print("shell/navigation/global-domains=ok; case-direct-entry/isolation=ok")
    print("materials/original/document-text/provenance/review-contract=ok")


if __name__ == "__main__":
    main()
