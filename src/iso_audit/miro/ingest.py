"""Miro-ingest — sticky notes en tekstvakken ophalen als audit-input.

Kleurconventie (organisatiestandaard):

- groen  → positief / conform
- oranje → NC (non-conformiteit)
- rood   → NC (non-conformiteit)
- overig → geen pre-classificatie

Board-ID is configureerbaar via `MIRO_BOARD_ID` (.env).

Gemigreerd uit `Ops_to_Biz/audit/miro_ingest.py` per milestone B §2.4.4.
Wijziging t.o.v. origineel: paginatie + retry verloopt via `MiroClient`
(zie `iso_audit.miro.client`) i.p.v. inline `requests`-aanroepen.
"""

from __future__ import annotations

import logging
import os
import re
from typing import Any

from iso_audit.miro.client import MiroClient

logger = logging.getLogger(__name__)

# Miro kleur-hex-codes en symbolische kleurnamen → classificatie.
KLEUR_CLASSIFICATIE: dict[str, str] = {
    # Groen-tinten
    "#d5e8d4": "positief",
    "#82b366": "positief",
    "#00cc00": "positief",
    "light_green": "positief",
    "green": "positief",
    # Oranje-tinten
    "#ffe6cc": "NC",
    "#f0a30a": "NC",
    "#d79b00": "NC",
    "yellow": "NC",  # Miro gebruikt soms geel/oranje door elkaar
    "orange": "NC",
    # Rood-tinten
    "#f8cecc": "NC",
    "#b85450": "NC",
    "#ff0000": "NC",
    "red": "NC",
    "light_red": "NC",
    "dark_red": "NC",
}

_HTML_TAG_RE = re.compile(r"<[^>]+>")


def _kleur_naar_classificatie(kleur: str | None) -> str | None:
    """Map een Miro-kleur (hex of symbolisch) naar `NC`/`positief`/`None`."""
    if not kleur:
        return None
    kleur_lower = kleur.lower().strip()
    return KLEUR_CLASSIFICATIE.get(kleur_lower) or KLEUR_CLASSIFICATIE.get(kleur.strip())


def _tekst_uit_item(item: dict[str, Any]) -> str:
    """Extraheer platte tekst uit een Miro-item (sticky_note of text)."""
    content = item.get("data", {}) or {}
    tekst = content.get("content", "") or content.get("text", "") or ""
    return _HTML_TAG_RE.sub("", tekst).strip()


def haal_notities_op(
    board_id: str | None = None,
    client: MiroClient | None = None,
) -> list[dict[str, Any]]:
    """Haal sticky notes + tekstvakken op van het Miro-bord.

    Returnt een lijst dicts met velden: `tekst`, `pre_classificatie`,
    `herkomst="Miro"`, `miro_item_id`, `kleur`.
    """
    board_id = board_id or os.environ.get("MIRO_BOARD_ID")
    if not board_id:
        raise OSError("MIRO_BOARD_ID niet ingesteld in .env")

    client = client or MiroClient()
    logger.info("Miro-ingest gestart voor bord %s", board_id)

    items: list[dict[str, Any]] = []
    for item_type in ("sticky_note", "text"):
        items.extend(client.paginated_get(f"/boards/{board_id}/items", params={"type": item_type}))

    notities: list[dict[str, Any]] = []
    for item in items:
        tekst = _tekst_uit_item(item)
        if not tekst:
            continue
        kleur = item.get("style", {}).get("fillColor") or item.get("data", {}).get(
            "backgroundColor"
        )
        notities.append(
            {
                "tekst": tekst,
                "pre_classificatie": _kleur_naar_classificatie(kleur),
                "herkomst": "Miro",
                "miro_item_id": item.get("id"),
                "kleur": kleur,
            }
        )

    logger.info("Miro-ingest: %d notities opgehaald", len(notities))
    return notities


def koppel_aan_clausules(
    notities: list[dict[str, Any]], clause_map: dict[str, Any]
) -> list[dict[str, Any]]:
    """Koppel elke notitie aan een norm-clausule via zoektermen.

    Pre-classificatie via kleur is al gedaan in `haal_notities_op`.
    Voegt `clausule`-veld toe (eerste match), of `None` als geen match.
    """
    clausules: dict[str, Any] = clause_map.get("clausules", {})
    for notitie in notities:
        tekst_lower = notitie["tekst"].lower()
        gevonden: str | None = None
        for clausule_id, data in clausules.items():
            zoektermen = data.get("zoektermen", [])
            if any(term.lower() in tekst_lower for term in zoektermen):
                gevonden = clausule_id
                break
        notitie["clausule"] = gevonden
        if gevonden is None:
            logger.debug("Miro-notitie zonder clausule-match: '%s...'", notitie["tekst"][:60])
    return notities


def merge_met_drive_bevindingen(
    miro_notities: list[dict[str, Any]],
    drive_bevindingen: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Combineer Miro-notities en Drive-bevindingen tot één lijst.

    Elke entry heeft al een `herkomst`-label (`"Miro"` of `"Drive"`).
    """
    return drive_bevindingen + miro_notities
