"""Gedeelde `gws` CLI-wrapper voor Google Workspace-API-aanroepen.

Alle Google Workspace API-aanroepen gaan via de `gws` CLI zodat de OAuth2-
sessie van de gebruiker gebruikt wordt (geen service-account-keyfile nodig).

Gemigreerd uit `Ops_to_Biz/audit/gws_client.py` per milestone B §2.3.1.
Wijzigingen: type-hints aangevuld voor `mypy --strict`; bandit-`nosec`
annotaties op subprocess-calls (gws-CLI met vaste positionele args en
JSON-blobs — geen shell-injectie).
"""

from __future__ import annotations

import contextlib
import json
import logging
import os
import subprocess  # nosec B404 — gws CLI uitvoeren is de bedoelde flow
import tempfile
import time
from typing import Any

logger = logging.getLogger(__name__)

_MAX_RETRIES = 3


def _gws(
    *args: str,
    body: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Voer een `gws`-subcommando uit en parseer JSON-stdout.

    Positional args worden direct doorgegeven; bv.

        _gws("drive", "files", "list", params={"q": "..."})

    Retries op HTTP 429/503/`rateLimitExceeded` met exponentiële backoff,
    max ``_MAX_RETRIES`` keer.
    """
    cmd = ["gws", *args]
    if params:
        cmd += ["--params", json.dumps(params)]
    if body is not None:
        cmd += ["--json", json.dumps(body)]

    wacht = 1
    for poging in range(_MAX_RETRIES + 1):
        try:
            result = subprocess.run(  # nosec B603 B607
                cmd, capture_output=True, text=True, check=True
            )
            return json.loads(result.stdout) if result.stdout.strip() else {}
        except subprocess.CalledProcessError as e:
            stderr = e.stderr or ""
            if (
                "429" in stderr or "503" in stderr or "rateLimitExceeded" in stderr
            ) and poging < _MAX_RETRIES:
                wacht = min(wacht * 2, 30)
                logger.warning("Rate limit (poging %d) — wacht %ds", poging + 1, wacht)
                time.sleep(wacht)
            else:
                raise
    # Onbereikbaar — de loop returnt of raised altijd.
    raise RuntimeError("gws-retries uitgeput zonder return")


def _gws_binary(
    *args: str,
    params: dict[str, Any] | None = None,
    suffix: str = ".bin",
) -> bytes:
    """Voer een `gws`-subcommando uit dat binaire output retourneert.

    Schrijft naar een tijdelijk bestand en retourneert de bytes. Retries
    op rate-limit zoals `_gws`.
    """
    cmd = ["gws", *args]
    if params:
        cmd += ["--params", json.dumps(params)]

    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f:
        tmp_path = f.name
    try:
        wacht = 1
        for poging in range(_MAX_RETRIES + 1):
            try:
                subprocess.run(  # nosec B603 B607
                    [*cmd, "-o", tmp_path], check=True, capture_output=True
                )
                break
            except subprocess.CalledProcessError as e:
                raw = e.stderr or b""
                stderr = raw.decode() if isinstance(raw, bytes) else raw
                if ("429" in stderr or "503" in stderr) and poging < _MAX_RETRIES:
                    wacht = min(wacht * 2, 30)
                    logger.warning("Rate limit (poging %d) — wacht %ds", poging + 1, wacht)
                    time.sleep(wacht)
                else:
                    raise
        with open(tmp_path, "rb") as fh:
            return fh.read()
    finally:
        with contextlib.suppress(OSError):
            os.unlink(tmp_path)


def gws_lijst_bestanden(folder_id: str, drive_id: str | None = None) -> list[dict[str, Any]]:
    """Lijst recursief alle bestanden in `folder_id`.

    Ondersteunt zowel reguliere Drive-mappen als Shared Drives (`0A...`-IDs).
    Returnt een lijst `{id, name, mimeType, modifiedTime}` (sub-mappen worden
    gevolgd; submap-records zelf niet meegegeven).
    """
    alle: list[dict[str, Any]] = []
    page_token: str | None = None

    while True:
        params: dict[str, Any] = {
            "q": f"'{folder_id}' in parents and trashed=false",
            "fields": "nextPageToken, files(id, name, mimeType, modifiedTime)",
            "pageSize": 100,
            "supportsAllDrives": True,
            "includeItemsFromAllDrives": True,
        }
        if drive_id:
            params["corpora"] = "drive"
            params["driveId"] = drive_id
        if page_token:
            params["pageToken"] = page_token

        result = _gws("drive", "files", "list", params=params)
        bestanden = result.get("files", [])

        for bestand in bestanden:
            if bestand["mimeType"] == "application/vnd.google-apps.folder":
                alle.extend(gws_lijst_bestanden(bestand["id"], drive_id=drive_id))
            else:
                alle.append(bestand)

        page_token = result.get("nextPageToken")
        if not page_token:
            break

    return alle


def gws_exporteer_google_doc(file_id: str) -> str:
    """Exporteer een Google Doc als plain text via `gws drive files export`."""
    inhoud = _gws_binary(
        "drive",
        "files",
        "export",
        params={"fileId": file_id, "mimeType": "text/plain", "supportsAllDrives": True},
        suffix=".txt",
    )
    return inhoud.decode("utf-8", errors="replace")


def gws_download_bestand(file_id: str) -> bytes:
    """Download een bestand via `gws drive files get` met `alt=media`.

    Werkt voor `.docx`, `.txt` en andere niet-Google-native formaten.
    """
    return _gws_binary(
        "drive",
        "files",
        "get",
        params={"fileId": file_id, "alt": "media", "supportsAllDrives": True},
    )


# ---------------------------------------------------------------------------
# Sheets-helpers
# ---------------------------------------------------------------------------


def gws_lees_sheet(spreadsheet_id: str, bereik: str | None = None) -> list[list[Any]]:
    """Lees een bereik uit een Google Sheet via `gws sheets values get`.

    `bereik=None` leest het eerste blad volledig (`A1:ZZ10000`-default).
    Returnt een lijst rijen, elk rij een lijst cellen.
    """
    range_param = bereik or "A1:ZZ10000"
    data = _gws(
        "sheets",
        "spreadsheets",
        "values",
        "get",
        params={"spreadsheetId": spreadsheet_id, "range": range_param},
    )
    values: list[list[Any]] = data.get("values", [])
    return values


def gws_lees_alle_tabs(spreadsheet_id: str) -> dict[str, list[list[Any]]]:
    """Lees alle tabs van een spreadsheet — `{tab_naam: [[rij], ...]}`.

    Tabs die op een fout uitkomen worden geskipt (gelogd, niet geraised).
    """
    meta = _gws(
        "sheets",
        "spreadsheets",
        "get",
        params={"spreadsheetId": spreadsheet_id},
    )
    tabs = [s["properties"]["title"] for s in meta.get("sheets", [])]
    resultaat: dict[str, list[list[Any]]] = {}
    for tab in tabs:
        try:
            resultaat[tab] = gws_lees_sheet(spreadsheet_id, f"'{tab}'!A1:AZ500")
            logger.info("Tab '%s': %d rijen", tab, len(resultaat[tab]))
        except Exception as e:
            logger.warning("Tab '%s' overgeslagen: %s", tab, e)
    return resultaat
