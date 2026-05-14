"""Auditrapport-template aanmaken in Google Docs via `gws` CLI.

Werking:

1. Leest `report_template_structure.yaml` uit `iso_audit.data`.
2. Maakt een nieuw Google Doc aan met alle verplichte secties + placeholders.
3. Retourneert het Doc-ID; caller zet dat in `.env` als `AUDIT_TEMPLATE_DOC_ID`.

Gemigreerd uit `Ops_to_Biz/audit/template_setup.py` per milestone B §2.5.3.
`gws_client._gws` → `iso_audit.clients.gws._gws`; YAML-pad via
`importlib.resources` i.p.v. `__file__`-trucs.
"""

from __future__ import annotations

import logging
from datetime import date
from importlib import resources
from typing import Any

import yaml

from iso_audit.clients.gws import _gws

logger = logging.getLogger(__name__)

TEMPLATE_STRUCTURE_RESOURCE = "report_template_structure.yaml"


def _load_structure() -> dict[str, Any]:
    """Laad de YAML-structuur uit het ingebakken data-resource."""
    res = resources.files("iso_audit.data") / TEMPLATE_STRUCTURE_RESOURCE
    with res.open("r", encoding="utf-8") as f:
        data: dict[str, Any] = yaml.safe_load(f)
    return data


def _find_existing_report(folder_id: str) -> str | None:
    """Zoek een bestaand auditrapport in Drive als referentie (5 nieuwste)."""
    result = _gws(
        "drive",
        "files",
        "list",
        params={
            "q": (
                f"'{folder_id}' in parents "
                "and mimeType='application/vnd.google-apps.document' "
                "and name contains 'Auditrapport' "
                "and trashed=false"
            ),
            "fields": "files(id, name)",
            "pageSize": 5,
        },
    )
    files = result.get("files", [])
    if files:
        print(f"Referentierapport gevonden: {files[0]['name']} ({files[0]['id']})")
        return str(files[0]["id"])
    return None


def _build_template_requests(structure: dict[str, Any]) -> list[dict[str, Any]]:
    """Bouw de Google-Docs batchUpdate-requests voor de hele template-tekst."""
    full_text_parts = [
        "AUDITRAPPORT\n"
        f"Template versie: {structure['versie']}  |  Norm(en): "
        f"{', '.join(structure['normen'])}  |  Aangemaakt: {date.today()}\n\n"
    ]
    for sectie in structure["secties"]:
        full_text_parts.append(f"{sectie['titel']}\n")
        if "omschrijving" in sectie:
            full_text_parts.append(f"{sectie['omschrijving']}\n")
        for ph in sectie.get("placeholders", []):
            full_text_parts.append(f"[{ph['naam']}]\n{{{{  {ph['naam']}  }}}}\n\n")
        full_text_parts.append("\n")
    return [{"insertText": {"location": {"index": 1}, "text": "".join(full_text_parts)}}]


def create_template(folder_id: str) -> str:
    """Maak het auditrapport-template aan in Drive en retourneer het Doc-ID."""
    structure = _load_structure()
    norm_label = "+".join(n.split(":")[0].replace(" ", "") for n in structure["normen"])
    doc_title = f"Auditrapport_Template_{norm_label}_v{structure['versie']}"

    # Nieuw Doc aanmaken via Drive (gws docs heeft geen create-commando).
    doc = _gws(
        "drive",
        "files",
        "create",
        body={"name": doc_title, "mimeType": "application/vnd.google-apps.document"},
    )
    doc_id: str = doc["id"]

    requests = _build_template_requests(structure)
    _gws(
        "docs",
        "documents",
        "batchUpdate",
        params={"documentId": doc_id},
        body={"requests": requests},
    )

    if folder_id:
        _gws(
            "drive",
            "files",
            "update",
            params={
                "fileId": doc_id,
                "addParents": folder_id,
                "removeParents": "root",
                "fields": "id,parents",
            },
            body={},
        )

    print(f"Template aangemaakt: {doc_title}")
    print(f"Doc-ID: {doc_id}")
    print(f"Stel in .env in: AUDIT_TEMPLATE_DOC_ID={doc_id}")
    return doc_id


def verify_placeholders(doc_id: str) -> list[str]:
    """Controleer of alle verwachte placeholders aanwezig zijn in het doc."""
    structure = _load_structure()
    doc = _gws("docs", "documents", "get", params={"documentId": doc_id})

    full_text = ""
    for elem in doc.get("body", {}).get("content", []):
        for item in elem.get("paragraph", {}).get("elements", []):
            full_text += item.get("textRun", {}).get("content", "")

    expected: list[str] = [
        ph["naam"] for sectie in structure["secties"] for ph in sectie.get("placeholders", [])
    ]
    missing = [name for name in expected if f"{{{{{name}}}}}" not in full_text]

    if missing:
        print(f"Waarschuwing: {len(missing)} placeholder(s) ontbreken: {missing}")
    else:
        print("Alle placeholders aanwezig in template.")
    return missing
