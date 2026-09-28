"""Seed only an explicitly isolated DATA_DIR for the UX-03B browser demo."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path


data_dir = Path(os.environ.get("DATA_DIR", "")).resolve()
if not os.environ.get("DATA_DIR") or data_dir == Path("data").resolve():
    raise SystemExit("DATA_DIR exclusivo e explícito é obrigatório.")

from app.database import SessionLocal
from app.models.platea import SharedCase, SharedDocument, SharedPerson
from app.services.workspace_service import create_block, open_workspace


def main() -> None:
    db = SessionLocal()
    try:
        now = datetime.now(timezone.utc)
        case = SharedCase(
            case_ref="UX03B-DEMO",
            title="Caso sintético UX-03B",
            status="aberto",
            classification="TESTE SINTÉTICO",
            published_by="ux03b-demo",
            published_at=now,
            published_version=1,
        )
        db.add(case)
        db.flush()
        person = SharedPerson(
            shared_case_id=case.id,
            person_ref="P-SINT-01",
            full_name="Pessoa Sintética",
            role_in_case="referência de teste",
        )
        document = SharedDocument(
            shared_case_id=case.id,
            document_ref="D-SINT-01",
            filename="relato_sintetico.txt",
            file_type="txt",
            sha256="3" * 64,
            description="Material inteiramente sintético para UX-03B.",
            imported_at="2026-09-03",
        )
        db.add_all([person, document])
        db.commit()
        workspace, _ = open_workspace(
            db,
            case_ref=case.case_ref,
            operator_id=None,
            operator_username="ux03b-demo",
        )
        for title, summary, sources in (
            ("Linha temporal sintética", "Eventos artificiais para validar vínculos.", [f"person:{person.id}"]),
            ("Documento de apoio sintético", "Material artificial sem dado real.", [f"document:{document.id}"]),
        ):
            block, error = create_block(
                db,
                workspace_id=workspace.id,
                title=title,
                summary=summary,
                source_tokens=sources,
                operator_id=None,
                operator_username="ux03b-demo",
            )
            if error or block is None:
                raise RuntimeError(error or "Falha ao criar bloco sintético.")
            db.commit()
        print(f"UX03B_DEMO_DATA_DIR={data_dir}")
        print(f"UX03B_DEMO_URL=/workspace/{case.case_ref}")
        print(f"UX03B_DEMO_WORKSPACE={workspace.id}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
