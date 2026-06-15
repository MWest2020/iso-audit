"""FastAPI-app voor de auditor-flow (MVP: triage + memo).

Dunne schil op `AuditSession` (en daarmee de bestaande motor). De API is het
contract; een frontend (web nu, Nextcloud later) consumeert dit. Beslissingen
lopen via `POST /findings/{id}` en worden append-only vastgelegd.
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from iso_audit.api.session import AuditSession, SessionError
from iso_audit.memo.models import Severity, TriageStatus


class TriageUpdate(BaseModel):
    """Reclassificatie (NC↔OFI) en/of triage-status, met verplichte reden."""

    severity: Severity | None = None
    triage_status: TriageStatus | None = None
    reason: str = ""


class FindingSummary(BaseModel):
    id: str
    severity: Severity
    clause: str
    title: str
    triage_status: TriageStatus


def create_app(session: AuditSession) -> FastAPI:
    """Bouw de FastAPI-app rond één geladen auditsessie."""
    app = FastAPI(title="iso-audit — auditor-API", version="0.1.0")

    @app.get("/findings", response_model=list[FindingSummary])
    def lijst_findings(severity: Severity | None = None) -> list[FindingSummary]:
        return [
            FindingSummary(
                id=f.id,
                severity=f.severity,
                clause=f.clause,
                title=f.title,
                triage_status=f.triage_status,
            )
            for f in session.findings()
            if severity is None or f.severity == severity
        ]

    @app.post("/findings/{finding_id}", response_model=FindingSummary)
    def triage(finding_id: str, update: TriageUpdate) -> FindingSummary:
        try:
            f = session.apply_triage(
                finding_id,
                severity=update.severity,
                triage_status=update.triage_status,
                reason=update.reason,
            )
        except SessionError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        return FindingSummary(
            id=f.id,
            severity=f.severity,
            clause=f.clause,
            title=f.title,
            triage_status=f.triage_status,
        )

    @app.get("/trail")
    def trail() -> list[dict[str, str]]:
        """De append-only triage-trail (auditor-beslissingen)."""
        return session.trail()

    @app.get("/landscape")
    def landscape() -> dict[str, object]:
        """Stap 1: dekking en gaps."""
        return session.landscape()

    @app.post("/run")
    def run() -> dict[str, object]:
        """Stap 2: samenvatting van de (geladen) run-output."""
        return session.run_summary()

    @app.get("/triage/status")
    def triage_status() -> dict[str, object]:
        """Voortgang van de triage; de memo is gated tot dit compleet is."""
        return session.triage_summary()

    def _eis_triage_compleet() -> None:
        s = session.triage_summary()
        if not s["complete"]:
            raise HTTPException(
                status_code=409,
                detail=f"Triage niet compleet: {s['open']} kandidaat-NC('s) nog open.",
            )

    @app.get("/memo/preview", response_class=HTMLResponse)
    def memo_preview() -> str:
        _eis_triage_compleet()
        try:
            return session.render_html()
        except (SessionError, ValueError, OSError) as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/memo/export")
    def memo_export() -> dict[str, str]:
        _eis_triage_compleet()
        pad = session.export_pdf(session.dir / "Auditmemo_management.pdf")
        return {"pdf": str(pad)}

    @app.get("/", response_class=HTMLResponse)
    def index() -> str:
        return _UI_HTML

    return app


_UI_HTML = (Path(__file__).resolve().parent / "ui.html").read_text(encoding="utf-8")


def serve(
    session_dir: str | Path,
    *,
    profile: str,
    norms_dir: str | Path,
    memo_input_path: str | Path,
    host: str = "127.0.0.1",
    port: int = 8000,
) -> None:
    """Start de lokale server (gebonden aan 127.0.0.1)."""
    import uvicorn

    session = AuditSession(
        session_dir, profile=profile, norms_dir=norms_dir, memo_input_path=memo_input_path
    )
    uvicorn.run(create_app(session), host=host, port=port)
