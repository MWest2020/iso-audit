"""Miro-bord setup — gestructureerd auditbord aanmaken.

Maakt een nieuw bord (of vult een bestaand bord) met:

- Eén frame per ISO-hoofdstuk (9001 hfst 4-10, 27001 Annex A 5-8)
- Per clausule een header-sticky (kleur op basis van bevinding/dekking)
- Per sub-punt een sticky met bewijsdocs of bewijslast-checklist
- Per clausule een "overig bewijs"-sticky

Kleurconventie:
- `light_yellow` = nog te beoordelen / open
- `light_green`  = positief / gedekt
- `yellow`       = OFI (verbeterpunt)
- `red`          = NC (non-conformiteit)

Gemigreerd uit `Ops_to_Biz/audit/miro_board_setup.py` per milestone B §2.4.3.
Wijziging: HTTP-calls via `MiroClient` i.p.v. inline `_post`. Imports
ge-updatet naar `iso_audit.*` paden.
"""

from __future__ import annotations

import argparse
import logging
import os
import sqlite3
from typing import Any

from dotenv import load_dotenv

from iso_audit.miro.client import MiroClient

load_dotenv()
logger = logging.getLogger(__name__)

MIRO_ISO_PROJECT_ID_ENV = "MIRO_ISO_PROJECT_ID"
DEFAULT_ISO_PROJECT_ID = "3458764519029876453"

# Layout constanten (px)
FRAME_WIDTH = 2400
FRAME_HEIGHT = 3000
FRAME_GAP_X = 200
FRAME_GAP_Y = 300
STICKY_W = 228
HEADER_H = 110
SUB_H = 170
DOC_STICKY_H = 220
STICKY_GAP = 16
STICKY_COLS = 8
FRAME_PADDING = 80
MAX_SUB_PUNTEN = 5

# HLS-hoofdstukken 4-10 — gedeeld door 9001 en 27001 (Annex SL).
HOOFDSTUKKEN_HLS: list[tuple[str, str]] = [
    ("4", "Organisatiecontext"),
    ("5", "Leiderschap"),
    ("6", "Planning"),
    ("7", "Ondersteuning"),
    ("8", "Uitvoering"),
    ("9", "Evaluatie"),
    ("10", "Verbetering"),
]

# ISO 27001 Annex A-thema's (operationele controls).
ANNEX_A_27001: list[tuple[str, str]] = [
    ("5", "Organisatorische maatregelen"),
    ("6", "Personeelsmaatregelen"),
    ("7", "Fysieke maatregelen"),
    ("8", "Technische maatregelen"),
]

KLEUREN: dict[str, str] = {
    "open": "light_yellow",
    "positief": "light_green",
    "OFI": "yellow",
    "NC": "red",
}

NORM_LABEL: dict[str, str] = {"9001": "KMS", "27001": "ISMS"}


def maak_bord(naam: str, client: MiroClient, droog: bool = False) -> str:
    """Maak een nieuw bord aan in de ISO-project-space."""
    project_id = os.environ.get(MIRO_ISO_PROJECT_ID_ENV, DEFAULT_ISO_PROJECT_ID)
    logger.info("Bord aanmaken: %s", naam)
    body: dict[str, Any] = {
        "name": naam,
        "description": "Gegenereerd door ISO audit pipeline — Conduction",
        "project": {"id": project_id},
        "sharingPolicy": {"access": "edit", "teamAccess": "edit"},
    }
    result = client.post("/boards", body, droog=droog)
    board_id: str = result.get("id", "dry-run")
    logger.info("Bord aangemaakt: %s (id: %s)", naam, board_id)
    return board_id


def maak_frame(
    board_id: str,
    titel: str,
    x: int,
    y: int,
    client: MiroClient,
    droog: bool = False,
) -> str:
    """Maak een frame met vaste afmetingen op de gegeven positie."""
    body: dict[str, Any] = {
        "data": {"title": titel, "format": "custom", "showContent": True},
        "style": {"fillColor": "#f0f0f0"},
        "geometry": {"width": FRAME_WIDTH, "height": FRAME_HEIGHT},
        "position": {"x": x, "y": y, "origin": "center"},
    }
    result = client.post(f"/boards/{board_id}/frames", body, droog=droog)
    frame_id: str = result.get("id", "dry-run")
    return frame_id


def maak_sticky(
    board_id: str,
    tekst: str,
    x: int,
    y: int,
    client: MiroClient,
    kleur: str = "light_yellow",
    droog: bool = False,
) -> str:
    """Maak een sticky note op de gegeven positie."""
    body: dict[str, Any] = {
        "data": {"content": tekst, "shape": "square"},
        "style": {
            "fillColor": kleur,
            "textAlign": "left",
            "textAlignVertical": "top",
        },
        "geometry": {"width": STICKY_W},
        "position": {"x": x, "y": y, "origin": "center"},
    }
    result = client.post(f"/boards/{board_id}/sticky_notes", body, droog=droog)
    sticky_id: str = result.get("id", "dry-run")
    return sticky_id


def _clausules_voor_hoofdstuk(clause_map: dict[str, Any], prefix: str) -> list[tuple[str, str]]:
    """Gesorteerde `(id, titel)`-paren voor een hoofdstukprefix."""
    return sorted(
        (cid, data.get("titel", ""))
        for cid, data in clause_map.get("clausules", {}).items()
        if cid.startswith(prefix + ".") or cid == prefix
    )


def _kleur_voor_clausule(
    clausule_id: str,
    matched_ids: set[str],
    interviews: dict[str, dict[str, Any]],
) -> str:
    """Prioriteit: interview-bevinding → dekking → open.

    1. Interview-bevinding (NC/OFI/positief) overschrijft alles.
    2. Gedekt door documenten → `light_green` (positief).
    3. Niets → `light_yellow` (open, audit inplannen).
    """
    iv = interviews.get(clausule_id)
    if iv:
        return KLEUREN.get(iv["bevinding"], "light_yellow")
    if clausule_id in matched_ids:
        return KLEUREN["positief"]
    return KLEUREN["open"]


def _drive_link(doc_id: str, mime: str | None) -> str:
    """Bouw de Drive-URL voor een document, met juiste pad per MIME-type."""
    if mime == "application/vnd.google-apps.document":
        return f"https://docs.google.com/document/d/{doc_id}"
    if mime == "application/vnd.google-apps.spreadsheet":
        return f"https://docs.google.com/spreadsheets/d/{doc_id}"
    return f"https://drive.google.com/file/d/{doc_id}"


def bouw_bord(
    droog: bool = False,
    bord_id: str | None = None,
    client: MiroClient | None = None,
) -> str:
    """Bouw het complete auditbord op basis van DB-state.

    Vereist tabellen die in de pipeline-DB worden aangelegd:
    `clause_matches` (uit store.py — al gemigreerd), `documents` met
    `scope`-kolom, en `audit_planning`. Laatste twee zijn pipeline-runtime
    schema-extensies (geen onderdeel van M-B store-migratie).
    """
    # Lazy imports: niet alle deployments hebben pipeline-data geladen, en
    # we willen module-load zonder deze afhankelijkheden mogelijk maken.
    from iso_audit.classification.clause_mapping import laad_clause_map
    from iso_audit.data.normteksten import NORMTEKSTEN_9001, NORMTEKSTEN_27001
    from iso_audit.store import laad_interviews, verbinding

    client = client or MiroClient()

    conn = verbinding()
    interviews: dict[str, dict[str, Any]] = {
        r["clausule_id"]: dict(r) for r in laad_interviews(conn)
    }
    matched_ids: set[str] = {
        r[0]
        for r in conn.execute(
            "SELECT DISTINCT clausule_id FROM clause_matches WHERE sub_punt = ''"
        ).fetchall()
    }

    bewijs_met_id: dict[str, list[tuple[str, str]]] = {}
    bewijs_sub: dict[tuple[str, str], list[tuple[str, str]]] = {}
    planning: dict[str, str] = {}

    try:
        for row in conn.execute(
            """
            SELECT cm.clausule_id, d.id, d.naam, d.mime_type
            FROM clause_matches cm
            JOIN documents d ON d.id = cm.doc_id AND cm.herkomst = 'Drive'
            WHERE d.scope = 'in' AND cm.sub_punt = ''
            ORDER BY cm.clausule_id, d.modified_at DESC, d.naam
            """
        ).fetchall():
            cid = row["clausule_id"]
            link = _drive_link(row["id"], row["mime_type"])
            bewijs_met_id.setdefault(cid, [])
            if len(bewijs_met_id[cid]) < 4:
                bewijs_met_id[cid].append((row["naam"], link))

        for row in conn.execute(
            """
            SELECT cm.clausule_id, cm.sub_punt, d.id, d.naam, d.mime_type
            FROM clause_matches cm
            JOIN documents d ON d.id = cm.doc_id AND cm.herkomst = 'Drive'
            WHERE d.scope = 'in' AND cm.sub_punt != ''
            ORDER BY cm.clausule_id, cm.sub_punt, d.modified_at DESC, d.naam
            """
        ).fetchall():
            key = (row["clausule_id"], row["sub_punt"])
            link = _drive_link(row["id"], row["mime_type"])
            bewijs_sub.setdefault(key, [])
            if len(bewijs_sub[key]) < 4:
                bewijs_sub[key].append((row["naam"], link))

        for row in conn.execute(
            "SELECT clausule_id, kwartaal FROM audit_planning WHERE jaar=2025 AND kwartaal != ''"
        ).fetchall():
            planning[row["clausule_id"]] = row["kwartaal"]
    except sqlite3.OperationalError as e:
        # Pipeline-schema-extensies (documents.scope, audit_planning) zijn
        # nog niet aanwezig — bord wordt gebouwd met lege bewijs-/planning-
        # maps. Niet fataal voor de structuur.
        logger.warning("Schema-extensie ontbreekt; ga door zonder bewijs/planning: %s", e)

    conn.close()

    cm_9001 = laad_clause_map("9001")
    cm_27001 = laad_clause_map("27001")
    normteksten_map: dict[str, Any] = {**NORMTEKSTEN_9001, **NORMTEKSTEN_27001}

    if bord_id:
        logger.info("Bestaand bord gebruiken: %s", bord_id)
        board_id = bord_id
    else:
        board_id = maak_bord("ISO Audit Landschap 9001 + 27001", client, droog)
    if droog:
        logger.info("DRY-RUN — geen echte API-calls naar Miro")

    def _vul_frame(
        clausules: list[tuple[str, str]],
        x: int,
        y_offset: int,
        norm_label: str,
    ) -> None:
        sx_start = x + FRAME_PADDING + STICKY_W // 2
        rij_hoogte = (
            HEADER_H + MAX_SUB_PUNTEN * (SUB_H + STICKY_GAP) + DOC_STICKY_H + STICKY_GAP * 3
        )
        sy_start = y_offset + FRAME_PADDING + HEADER_H // 2 + 80
        label = NORM_LABEL.get(norm_label, norm_label)
        for i, (cid, titel) in enumerate(clausules):
            col = i % STICKY_COLS
            row = i // STICKY_COLS
            sx = sx_start + col * (STICKY_W + STICKY_GAP)
            sy_header = sy_start + row * rij_hoogte

            kleur = _kleur_voor_clausule(cid, matched_ids, interviews)
            tekst = f"<strong>[{label}] {cid}</strong>\n{titel}"
            iv = interviews.get(cid)
            if iv:
                bevinding_label = {
                    "NC": "🔴 NC",
                    "OFI": "🟡 OFI",
                    "positief": "🟢 OK",
                    "overgeslagen": "⚪ n.v.t.",
                }.get(iv["bevinding"], iv["bevinding"])
                tekst += f"\n{bevinding_label}"
                if iv.get("notitie"):
                    tekst += f": {iv['notitie'][:50]}"
            plan = planning.get(cid)
            if plan:
                tekst += f"\n📅 {plan}"
            maak_sticky(board_id, tekst, sx, sy_header, client, kleur, droog)

            nt = normteksten_map.get(cid, {})
            sub_punten = nt.get("sub_punten", [])
            for j, sp in enumerate(sub_punten):
                sy_sub = (
                    sy_header + HEADER_H // 2 + STICKY_GAP + j * (SUB_H + STICKY_GAP) + SUB_H // 2
                )
                sp_docs = bewijs_sub.get((cid, sp["id"]), [])
                if sp_docs:
                    regels = "\n".join(
                        f'<a href="{link}">{naam[:38]}</a>' for naam, link in sp_docs
                    )
                    sp_tekst = f"<strong>{sp['id']}) {sp['eis'][:70]}</strong>\n{regels}"
                else:
                    sp_bewijslast = "\n".join(f"☐ {b[:55]}" for b in sp.get("bewijslast", [])[:2])
                    sp_tekst = f"<strong>{sp['id']}) {sp['eis'][:70]}</strong>" + (
                        f"\n{sp_bewijslast}" if sp_bewijslast else "\n☐ _(geen bewijs gevonden)_"
                    )
                maak_sticky(board_id, sp_tekst, sx, sy_sub, client, "light_blue", droog)

            sub_hoogte = len(sub_punten) * (SUB_H + STICKY_GAP) if sub_punten else 0
            sy_docs = sy_header + HEADER_H // 2 + STICKY_GAP + sub_hoogte + DOC_STICKY_H // 2
            doc_namen = bewijs_met_id.get(cid, [])
            if doc_namen:
                doc_regels = "\n".join(
                    f'<a href="{link}">{naam[:40]}</a>' for naam, link in doc_namen
                )
                doc_tekst = f"<strong>Overig bewijs</strong>\n{doc_regels}"
            else:
                doc_tekst = "<strong>Overig bewijs</strong>\n_(geen aanvullende docs)_"
            maak_sticky(board_id, doc_tekst, sx, sy_docs, client, "gray", droog)

    logger.info("Frames aanmaken voor HLS-hoofdstukken (9001 + 27001)...")
    x = 0
    for prefix, naam in HOOFDSTUKKEN_HLS:
        cl_9001 = _clausules_voor_hoofdstuk(cm_9001, prefix)
        if not cl_9001:
            continue
        frame_titel = f"HLS Hfst {prefix}: {naam}  |  ISO 9001 + 27001"
        frame_x = x + FRAME_WIDTH // 2
        frame_y = FRAME_HEIGHT // 2
        maak_frame(board_id, frame_titel, frame_x, frame_y, client, droog)
        logger.info("  Frame: %s (%d clausules)", frame_titel, len(cl_9001))
        _vul_frame(cl_9001, x, 0, "9001")
        x += FRAME_WIDTH + FRAME_GAP_X

    logger.info("Frames aanmaken voor ISO 27001 Annex A...")
    x = 0
    y_offset = FRAME_HEIGHT + FRAME_GAP_Y
    for prefix, naam in ANNEX_A_27001:
        clausules = _clausules_voor_hoofdstuk(cm_27001, prefix)
        if not clausules:
            continue
        chunk_size = 20
        chunks = [clausules[i : i + chunk_size] for i in range(0, len(clausules), chunk_size)]
        for chunk_idx, chunk in enumerate(chunks):
            suffix = f" ({chunk_idx + 1}/{len(chunks)})" if len(chunks) > 1 else ""
            frame_titel = f"27001 Annex A — Thema {prefix}: {naam}{suffix}"
            frame_x = x + FRAME_WIDTH // 2
            frame_y = y_offset + FRAME_HEIGHT // 2
            maak_frame(board_id, frame_titel, frame_x, frame_y, client, droog)
            logger.info("  Frame: %s (%d clausules)", frame_titel, len(chunk))
            _vul_frame(chunk, x, y_offset, "27001")
            x += FRAME_WIDTH + FRAME_GAP_X

    logger.info("Bord klaar: https://miro.com/app/board/%s", board_id)
    return board_id


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
        datefmt="%H:%M:%S",
    )
    parser = argparse.ArgumentParser(description="Miro auditbord aanmaken")
    parser.add_argument("--droog", action="store_true", help="Dry-run — geen API-calls")
    parser.add_argument("--bord-id", default=None, help="Gebruik bestaand bord-ID")
    args = parser.parse_args()
    board_id = bouw_bord(droog=args.droog, bord_id=args.bord_id)
    if not args.droog:
        print(f"\nBord: https://miro.com/app/board/{board_id}")
    return 0
