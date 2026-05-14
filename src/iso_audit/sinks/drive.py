"""`DriveSink` — schrijft `ReportPayload`s naar Google Drive (§3.3.1).

Eerste concrete Sink-implementatie. Gebruikt `iso_audit.clients.gws._gws`
voor de Drive API-calls (HTML → Google Doc conversie via Drive's import-
ondersteuning).

Niet-ondersteunde payload-types (`NotificationPayload`, `MirrorPayload`)
geven `SinkResult(succes=False, ...)` terug — een DriveSink doet alleen
rapport-write; e-mail is een ander Sink/Notifier.

Configuratie via env-vars:

- `AUDIT_DRIVE_FOLDER_ID` — doelmap voor rapporten (verplicht).
- `GWS_CLI_PATH` — alternatieve `gws`-binaire (default: `PATH`).
"""

from __future__ import annotations

import logging
import os
from shutil import which
from typing import Any

from iso_audit.clients.gws import _gws
from iso_audit.sinks import register
from iso_audit.sinks.base import (
    ReportPayload,
    SinkPayload,
    SinkResult,
)

logger = logging.getLogger(__name__)


@register
class DriveSink:
    """Sink die `ReportPayload`s als Google Doc naar Drive schrijft."""

    naam: str = "drive"

    def __init__(self, folder_id: str | None = None) -> None:
        """Construct met expliciete folder of fallback naar env-var."""
        self._folder_id = folder_id or os.environ.get("AUDIT_DRIVE_FOLDER_ID", "")

    def send(self, payload: SinkPayload) -> SinkResult:
        """Schrijf payload naar Drive. Alleen `ReportPayload` wordt geaccepteerd."""
        if not isinstance(payload, ReportPayload):
            return SinkResult(
                succes=False,
                bron_id=None,
                bericht=(
                    f"DriveSink accepteert alleen ReportPayload; kreeg {type(payload).__name__}"
                ),
            )
        if not self._folder_id:
            return SinkResult(
                succes=False,
                bron_id=None,
                bericht="AUDIT_DRIVE_FOLDER_ID niet gezet",
            )
        try:
            doc_id = self._upload_html_als_doc(payload)
        except Exception as e:
            logger.warning("DriveSink upload mislukt: %s", e)
            return SinkResult(succes=False, bron_id=None, bericht=str(e))
        for bijlage in payload.bijlagen:
            logger.info("DriveSink: bijlage geregistreerd: %s", bijlage)
        return SinkResult(
            succes=True,
            bron_id=doc_id,
            bericht=f"Geupload naar Drive folder {self._folder_id}",
        )

    def healthcheck(self) -> dict[str, object]:
        """Status + actieve folder-id."""
        if not self._folder_id:
            return {
                "status": "fail",
                "naam": self.naam,
                "reden": "AUDIT_DRIVE_FOLDER_ID niet gezet",
            }
        if not which("gws"):
            return {
                "status": "fail",
                "naam": self.naam,
                "reden": "gws CLI niet in PATH",
            }
        return {
            "status": "ok",
            "naam": self.naam,
            "folder_id": self._folder_id,
        }

    def _upload_html_als_doc(self, payload: ReportPayload) -> str:
        """Upload HTML als nieuwe Google Doc via gws CLI; retourneer doc-id."""
        body: dict[str, Any] = {
            "name": payload.titel,
            "mimeType": "application/vnd.google-apps.document",
            "parents": [self._folder_id],
        }
        # gws CLI ondersteunt geen direct multipart-upload via deze wrapper;
        # we maken eerst een leeg Doc, dan vullen we de inhoud via Docs API.
        created = _gws(
            "drive",
            "files",
            "create",
            params={"fields": "id"},
            body=body,
        )
        doc_id: str = created["id"]

        # Insert HTML content via Docs API.
        _gws(
            "docs",
            "documents",
            "batchUpdate",
            params={"documentId": doc_id},
            body={
                "requests": [
                    {
                        "insertText": {
                            "location": {"index": 1},
                            "text": _html_naar_tekst(payload.inhoud_html),
                        }
                    }
                ]
            },
        )
        return doc_id


def _html_naar_tekst(html: str) -> str:
    """Minimale HTML → tekst conversie voor de Docs insertText-API.

    Voor een echte rich-content upload zou je Drive's multipart import
    moeten gebruiken; dit is een MVP. Volledige conversie komt mee met
    §3.3.2 consolidatie van reporting-write paden.
    """
    import re

    text = re.sub(r"<[^>]+>", "", html)
    # Decode common entities; meer kan via html.unescape.
    import html as _html_mod

    return _html_mod.unescape(text)
