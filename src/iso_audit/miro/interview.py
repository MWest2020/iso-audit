"""Interview-voorbereiding op Miro — frames per interview-sessie.

Per sessie:
- Frame met concept-uitnodigingstekst bovenaan
- Per clausule twee stickies: interviewvragen (lichtblauw) en bewijslast (lichtgeel)

Gemigreerd uit `Ops_to_Biz/audit/interview_miro.py` per milestone B §2.4.5.
Wijziging: HTTP-calls via `MiroClient`, lazy imports naar `iso_audit.*` paden.
"""

from __future__ import annotations

import argparse
import logging
from typing import Any

from dotenv import load_dotenv

from iso_audit.miro.client import MiroClient

load_dotenv()
logger = logging.getLogger(__name__)

# Layout
FRAME_W = 3200
FRAME_H = 1800
FRAME_GAP_Y = 300
FRAME_PAD = 100
STICKY_W = 400
STICKY_H = 400
STICKY_GAP_X = 40
STICKY_GAP_Y = 30

# Kleur per sticky-type.
KLEUR_VRAGEN = "light_blue"
KLEUR_BEWIJS = "light_yellow"
KLEUR_UITNODIGING = "light_pink"

# Statische groepering: eigenaar + thema per sessie. Clausules worden dynamisch
# uit de DB gehaald (alleen écht open).
SESSIE_DEFINITIES: list[tuple[str, str, list[tuple[str, str]]]] = [
    (
        "Interview 1 — Beleid & Strategie",
        "Directie / Managementteam",
        [("9001", "5.2")],
    ),
    (
        "Interview 2 — Ondersteuning & Competenties",
        "HR / Operationeel verantwoordelijke",
        [("9001", "7.2"), ("9001", "7.3")],
    ),
    (
        "Interview 3 — Ontwerp & Ontwikkeling",
        "DevLead / CTO",
        [("9001", "8.3")],
    ),
    (
        "Interview 4 — Leveranciersbeheer (27001)",
        "Remco Damhuis",
        [("27001", "5.22")],
    ),
]


def _open_clausules() -> set[tuple[str, str]]:
    """`{(norm, clausule_id)}` van clausules die nog geen geldig interview hebben."""
    from iso_audit.classification.clause_mapping import laad_clause_map
    from iso_audit.store import verbinding

    conn = verbinding()
    open_set: set[tuple[str, str]] = set()
    try:
        for norm in ("9001", "27001"):
            cm = laad_clause_map(norm).get("clausules", {})
            gedekt = {
                r[0]
                for r in conn.execute(
                    "SELECT DISTINCT clausule_id FROM clause_matches cm "
                    "JOIN documents d ON d.id=cm.doc_id "
                    'WHERE cm.norm IN (?, "beide") AND d.scope="in" AND cm.sub_punt = ""',
                    (norm,),
                ).fetchall()
            }
            interviews = {
                r["clausule_id"]: r["bevinding"]
                for r in conn.execute(
                    "SELECT clausule_id, bevinding FROM interviews WHERE norm IN (?, 'beide')",
                    (norm,),
                ).fetchall()
            }
            for cid in cm:
                if cid not in gedekt:
                    bev = interviews.get(cid)
                    if not bev or bev == "overgeslagen":
                        open_set.add((norm, cid))
    finally:
        conn.close()
    return open_set


def _actieve_sessies() -> list[tuple[str, str, list[tuple[str, str]]]]:
    """Filter `SESSIE_DEFINITIES` tot sessies met ≥1 open clausule."""
    open_set = _open_clausules()
    sessies: list[tuple[str, str, list[tuple[str, str]]]] = []
    for naam, eigenaar, clausule_lijst in SESSIE_DEFINITIES:
        open_in_sessie = [(n, c) for n, c in clausule_lijst if (n, c) in open_set]
        if open_in_sessie:
            sessies.append((naam, eigenaar, open_in_sessie))
    return sessies


def _maak_frame(
    board_id: str,
    titel: str,
    x: int,
    y: int,
    client: MiroClient,
    droog: bool = False,
) -> str:
    body: dict[str, Any] = {
        "data": {"title": titel, "format": "custom", "showContent": True},
        "style": {"fillColor": "#e8f4fd"},
        "geometry": {"width": FRAME_W, "height": FRAME_H},
        "position": {"x": x, "y": y, "origin": "center"},
    }
    result = client.post(f"/boards/{board_id}/frames", body, droog=droog)
    frame_id: str = result.get("id", "dry-run")
    return frame_id


def _maak_tekstvak(
    board_id: str,
    tekst: str,
    x: int,
    y: int,
    breedte: int,
    hoogte: int,
    client: MiroClient,
    droog: bool = False,
) -> str:
    body: dict[str, Any] = {
        "data": {"content": tekst},
        "style": {"fontSize": 14, "textAlign": "left"},
        "geometry": {"width": breedte},
        "position": {"x": x, "y": y, "origin": "center"},
    }
    result = client.post(f"/boards/{board_id}/texts", body, droog=droog)
    text_id: str = result.get("id", "dry-run")
    return text_id


def _maak_sticky(
    board_id: str,
    tekst: str,
    x: int,
    y: int,
    kleur: str,
    client: MiroClient,
    droog: bool = False,
) -> str:
    body: dict[str, Any] = {
        "data": {"content": tekst, "shape": "square"},
        "style": {"fillColor": kleur, "textAlign": "left", "textAlignVertical": "top"},
        "geometry": {"width": STICKY_W},
        "position": {"x": x, "y": y, "origin": "center"},
    }
    result = client.post(f"/boards/{board_id}/sticky_notes", body, droog=droog)
    sticky_id: str = result.get("id", "dry-run")
    return sticky_id


def _vragen_voor_clausule(clausule_id: str, norm: str, normteksten: dict[str, Any]) -> list[str]:
    """Zet bewijslast-items om naar concrete auditor-vragen.

    Heuristiek:
    - "Bewijs / Aantoon ..." → "Kun je ... ?"
    - Anders → "Heb je ... ? Kun je het laten zien?"
    - Geen bewijslast → twee generieke fallback-vragen
    """
    nt = normteksten.get(clausule_id, {})
    bewijslast = nt.get("bewijslast", [])
    vragen: list[str] = []
    for bewijs in bewijslast:
        b = bewijs.rstrip(".")
        if b.lower().startswith("bewijs") or b.lower().startswith("aantoon"):
            vragen.append(f"Kun je {b[6:].strip().lower()}?")
        else:
            vragen.append(f"Heb je {b[0].lower() + b[1:]}? Kun je het laten zien?")
    return vragen or [
        "Hoe geeft de organisatie hier invulling aan?",
        "Welke documentatie is beschikbaar?",
    ]


def _uitnodiging_tekst(sessie_naam: str, eigenaar: str, clausules: list[tuple[str, str]]) -> str:
    """Bouw de concept-uitnodigingstekst voor het bovenste tekstvak in een frame."""
    clausule_lijst = ", ".join(f"{norm} {cid}" for norm, cid in clausules)
    return (
        f"<strong>{sessie_naam}</strong>\n\n"
        f"<strong>Gesprekspartner:</strong> {eigenaar}\n"
        f"<strong>Clausules:</strong> {clausule_lijst}\n"
        f"<strong>Duur:</strong> ±45 minuten\n\n"
        "Geen voorbereiding nodig — we kijken samen wat er al is en wat nog "
        "gedocumenteerd moet worden. Neem eventueel relevante documenten bij "
        "de hand."
    )


def bouw_interview_frames(
    board_id: str,
    droog: bool = False,
    client: MiroClient | None = None,
) -> None:
    """Bouw één frame per actieve interview-sessie op een bestaand bord."""
    from iso_audit.classification.clause_mapping import laad_clause_map
    from iso_audit.data.normteksten import NORMTEKSTEN_9001, NORMTEKSTEN_27001
    from iso_audit.miro.board_setup import FRAME_GAP_Y as BOARD_FRAME_GAP_Y
    from iso_audit.miro.board_setup import FRAME_HEIGHT as BOARD_FRAME_HEIGHT

    client = client or MiroClient()

    normteksten: dict[str, Any] = {**NORMTEKSTEN_9001, **NORMTEKSTEN_27001}
    cm_9001 = laad_clause_map("9001").get("clausules", {})
    cm_27001 = laad_clause_map("27001").get("clausules", {})

    # Interview-frames komen onder rij 2 van het hoofd-board.
    y_start = 2 * BOARD_FRAME_HEIGHT + 2 * BOARD_FRAME_GAP_Y

    for sessie_idx, (sessie_naam, eigenaar, clausule_lijst) in enumerate(_actieve_sessies()):
        logger.info("Sessie: %s", sessie_naam)
        frame_x = FRAME_W // 2
        frame_y = y_start + sessie_idx * (FRAME_H + FRAME_GAP_Y) + FRAME_H // 2

        _maak_frame(board_id, sessie_naam, frame_x, frame_y, client, droog)

        tekst_x = FRAME_PAD + 600
        tekst_y = frame_y - FRAME_H // 2 + FRAME_PAD + 80
        _maak_tekstvak(
            board_id,
            _uitnodiging_tekst(sessie_naam, eigenaar, clausule_lijst),
            tekst_x,
            tekst_y,
            1100,
            300,
            client,
            droog,
        )

        sticky_x_start = FRAME_PAD + STICKY_W // 2 + 1300
        sticky_y_vragen = frame_y - FRAME_H // 2 + FRAME_PAD + STICKY_H // 2 + 40
        sticky_y_bewijs = sticky_y_vragen + STICKY_H + STICKY_GAP_Y

        for col, (norm, cid) in enumerate(clausule_lijst):
            cm = cm_9001 if norm == "9001" else cm_27001
            titel = cm.get(cid, {}).get("titel", cid)
            nt = normteksten.get(cid, {})
            bewijslast = nt.get("bewijslast", [])
            vragen = _vragen_voor_clausule(cid, norm, normteksten)

            sx = sticky_x_start + col * (STICKY_W + STICKY_GAP_X)

            vragen_tekst = f"<strong>[{norm}] {cid} — {titel}</strong>\n\n" + "\n".join(
                f"• {v}" for v in vragen
            )
            _maak_sticky(board_id, vragen_tekst, sx, sticky_y_vragen, KLEUR_VRAGEN, client, droog)

            if bewijslast:
                bewijs_tekst = f"<strong>Bewijslast {cid}</strong>\n\n" + "\n".join(
                    f"☐ {b}" for b in bewijslast
                )
            else:
                bewijs_tekst = (
                    f"<strong>Bewijslast {cid}</strong>\n\n(geen specificatie beschikbaar)"
                )
            _maak_sticky(board_id, bewijs_tekst, sx, sticky_y_bewijs, KLEUR_BEWIJS, client, droog)

            logger.info(
                "  [%s] %s — %d vragen, %d bewijspunten",
                norm,
                cid,
                len(vragen),
                len(bewijslast),
            )

    logger.info("Interview-frames klaar: https://miro.com/app/board/%s", board_id)


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
        datefmt="%H:%M:%S",
    )
    parser = argparse.ArgumentParser(description="Interview-frames aanmaken op Miro")
    parser.add_argument("--droog", action="store_true", help="Dry-run — geen API-calls")
    parser.add_argument("--bord-id", default=None, help="Bestaand Miro bord-ID")
    args = parser.parse_args()
    if not args.bord_id and not args.droog:
        parser.error("Geef --bord-id op of gebruik --droog")
    board_id = args.bord_id or "dry-run"
    bouw_interview_frames(board_id=board_id, droog=args.droog)
    return 0
