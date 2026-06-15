"""Google Sheets output via `gws` CLI — audit findings.

Schrijft bevindingen + ontbrekende-dekking naar een Sheets-bestand via
de externe `gws` CLI. Service-account-config via env
`GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE`.

Omgevingsvariabelen:
- `AUDIT_SHEETS_ID` — bestaand Sheets-bestand (optioneel; default = nieuw aanmaken)
- `GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE` — service-account JSON

Gemigreerd uit `Ops_to_Biz/audit/sheets_gws.py` per milestone B §2.5.7.
Wijziging: "Consistent met argocd_sync"-comment verwijderd (de twee repo's
zijn nu losgekoppeld).
"""

from __future__ import annotations

import json
import logging
import os
import subprocess  # nosec B404 — gws CLI uitvoeren is de bedoelde flow
from datetime import date
from typing import Any

logger = logging.getLogger(__name__)

TAB_BEVINDINGEN = "Bevindingen"
TAB_ONTBREKEND = "Ontbrekende dekking"


def _env() -> dict[str, str]:
    """Geef de subprocess-env met service-account-credentials-pad doorgegeven."""
    env = os.environ.copy()
    creds = os.environ.get("GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE")
    if creds:
        env["GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE"] = creds
    return env


def _gws(*args: str, input_json: dict[str, Any] | None = None) -> dict[str, Any]:
    """Voer een `gws`-subcommando uit en parseer JSON-stdout.

    Vaste argumenten en JSON-input zonder shell-evaluatie — geen
    injectie-risico.
    """
    cmd = ["gws", *args]
    kwargs: dict[str, Any] = {
        "capture_output": True,
        "text": True,
        "check": True,
        "env": _env(),
    }
    if input_json is not None:
        kwargs["input"] = json.dumps(input_json)
    result = subprocess.run(cmd, **kwargs)  # nosec B603 B607
    return json.loads(result.stdout) if result.stdout.strip() else {}


def _maak_spreadsheet(titel: str) -> str:
    """Maak een nieuw Sheets-bestand aan met de twee audit-tabs en geef ID terug."""
    body = {
        "properties": {"title": titel},
        "sheets": [
            {"properties": {"title": TAB_BEVINDINGEN}},
            {"properties": {"title": TAB_ONTBREKEND}},
        ],
    }
    result = _gws(
        "sheets",
        "spreadsheets",
        "create",
        "--json",
        json.dumps(body),
    )
    sheets_id: str = result["spreadsheetId"]
    logger.info("Nieuw Sheets aangemaakt: %s", sheets_id)
    return sheets_id


def _zorg_voor_tab(sheets_id: str, tab_naam: str) -> None:
    """Maak `tab_naam` aan als die nog niet bestaat in het bestand."""
    result = _gws(
        "sheets",
        "spreadsheets",
        "get",
        "--params",
        json.dumps({"spreadsheetId": sheets_id, "fields": "sheets.properties.title"}),
    )
    bestaande = [s["properties"]["title"] for s in result.get("sheets", [])]
    if tab_naam not in bestaande:
        body = {"requests": [{"addSheet": {"properties": {"title": tab_naam}}}]}
        _gws(
            "sheets",
            "spreadsheets",
            "batchUpdate",
            "--params",
            json.dumps({"spreadsheetId": sheets_id}),
            "--json",
            json.dumps(body),
        )
        logger.info("Tab aangemaakt: '%s'", tab_naam)


def _schrijf_tab(sheets_id: str, tab: str, waarden: list[list[Any]]) -> None:
    """Wis een tab en schrijf de waarden opnieuw — voorkomt verouderde rijen."""
    _gws(
        "sheets",
        "spreadsheets",
        "values",
        "clear",
        "--params",
        json.dumps({"spreadsheetId": sheets_id, "range": tab}),
    )
    if not waarden:
        return
    num_rows = len(waarden)
    num_cols = max(len(r) for r in waarden)
    end_col = _kolom_letter(num_cols)
    body = {
        "valueInputOption": "RAW",
        "data": [
            {
                "range": f"{tab}!A1:{end_col}{num_rows}",
                "majorDimension": "ROWS",
                "values": [[str(c) if c is not None else "" for c in rij] for rij in waarden],
            }
        ],
    }
    _gws(
        "sheets",
        "spreadsheets",
        "values",
        "batchUpdate",
        "--params",
        json.dumps({"spreadsheetId": sheets_id}),
        "--json",
        json.dumps(body),
    )


def _kolom_letter(n: int) -> str:
    """Converteer 1-gebaseerd kolomnummer naar A1-notatie (`27` → `"AA"`)."""
    result = ""
    while n:
        n, remainder = divmod(n - 1, 26)
        result = chr(65 + remainder) + result
    return result


def sla_op_in_sheets(
    bevindingen: list[dict[str, Any]],
    ontbrekende_clausules: list[dict[str, Any]],
    sheets_id: str | None = None,
) -> str:
    """Schrijf bevindingen + ontbrekende-dekking naar Google Sheets via `gws`.

    Bij `sheets_id is None` wordt een nieuw bestand aangemaakt. Returnt
    het Sheets-ID.
    """
    sheets_id = sheets_id or os.environ.get("AUDIT_SHEETS_ID")

    if not sheets_id:
        sheets_id = _maak_spreadsheet(f"Auditmatrix_{date.today()}")
    else:
        _zorg_voor_tab(sheets_id, TAB_BEVINDINGEN)
        _zorg_voor_tab(sheets_id, TAB_ONTBREKEND)

    header = [
        "Clausule",
        "Clausule titel",
        "Document",
        "Herkomst",
        "Classificatie",
        "Beschrijving",
        "Onderbouwing",
        "Status",
    ]
    rijen: list[list[Any]] = [header] + [
        [
            b["clausule"],
            b["clausule_titel"],
            b["document_naam"],
            b["herkomst"],
            b["classificatie"],
            b["beschrijving"],
            b.get("onderbouwing", ""),
            "open",
        ]
        for b in bevindingen
    ]
    _schrijf_tab(sheets_id, TAB_BEVINDINGEN, rijen)
    logger.info("%d bevindingen geschreven naar tab '%s'", len(bevindingen), TAB_BEVINDINGEN)

    ontbrekend_rijen: list[list[Any]] = [["Clausule", "Titel", "Reden"]]
    for o in ontbrekende_clausules:
        ontbrekend_rijen.append([o["clausule"], o["titel"], o.get("reden", "")])
    _schrijf_tab(sheets_id, TAB_ONTBREKEND, ontbrekend_rijen)
    logger.info(
        "%d ontbrekende clausules geschreven naar tab '%s'",
        len(ontbrekende_clausules),
        TAB_ONTBREKEND,
    )

    logger.info("Sheets bijgewerkt: %s", sheets_id)
    return sheets_id
