"""Audit-landschap — clausule-dekking-rapport uit lokale DB.

Geen LLM nodig. Toont per clausule:

- Gedekt: welke documenten matchen
- Niet gedekt: clausules zonder enig bewijs
- Miro-notities per clausule

Gemigreerd uit `Ops_to_Biz/audit/landscape.py` per milestone B §2.5.5.
Wijzigingen: imports naar `iso_audit.{store, classification.clause_mapping}`;
`documents.scope`-filter wordt gracefully overgeslagen als de kolom nog niet
bestaat (pipeline-runtime schema-extensie).

Gebruik:
    python -m iso_audit.reporting.landscape              # beide normen
    python -m iso_audit.reporting.landscape --norm 9001
    python -m iso_audit.reporting.landscape --chapter 8
    python -m iso_audit.reporting.landscape --zoek "incident management"
"""

from __future__ import annotations

import argparse
import logging
import os
import sqlite3
from datetime import date
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# src/iso_audit/reporting/landscape.py → parent x 4 = repo root.
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
DEFAULT_OUTPUT_DIR = _REPO_ROOT / "output" / "landscape"


def _fetch_clause_matches(conn: sqlite3.Connection, norm: str) -> list[sqlite3.Row]:
    """Fetch matches met scope='in'-filter; fall back zonder scope als kolom mist."""
    sql_with_scope = """
        SELECT cm.clausule_id, cm.herkomst, cm.doc_id,
               COALESCE(d.naam, m.tekst) AS naam
        FROM clause_matches cm
        LEFT JOIN documents d ON d.id = cm.doc_id AND cm.herkomst = 'Drive'
        LEFT JOIN miro_notes m ON m.id = cm.doc_id AND cm.herkomst = 'Miro'
        WHERE cm.norm IN (?, 'beide')
          AND (cm.herkomst != 'Drive' OR d.scope = 'in')
          AND cm.sub_punt = ''
        ORDER BY cm.clausule_id, cm.herkomst, naam
    """
    sql_zonder_scope = """
        SELECT cm.clausule_id, cm.herkomst, cm.doc_id,
               COALESCE(d.naam, m.tekst) AS naam
        FROM clause_matches cm
        LEFT JOIN documents d ON d.id = cm.doc_id AND cm.herkomst = 'Drive'
        LEFT JOIN miro_notes m ON m.id = cm.doc_id AND cm.herkomst = 'Miro'
        WHERE cm.norm IN (?, 'beide')
          AND cm.sub_punt = ''
        ORDER BY cm.clausule_id, cm.herkomst, naam
    """
    try:
        return conn.execute(sql_with_scope, (norm,)).fetchall()
    except sqlite3.OperationalError as e:
        logger.warning(
            "documents.scope-kolom ontbreekt, val terug op niet-gefilterde query: %s",
            e,
        )
        return conn.execute(sql_zonder_scope, (norm,)).fetchall()


def genereer_landschap(norm: str, chapter: str | None = None) -> str:
    """Genereer een Markdown-landschapsrapport voor de gegeven norm + (optioneel) hoofdstuk."""
    from iso_audit.classification.clause_mapping import (
        filter_clause_map,
        laad_clause_map,
    )
    from iso_audit.store import verbinding

    conn = verbinding()
    clause_map = laad_clause_map(norm)
    if chapter:
        clause_map = filter_clause_map(clause_map, chapter)
    clausules: dict[str, Any] = clause_map.get("clausules", {})
    norm_label = clause_map.get("norm", norm)

    rows = _fetch_clause_matches(conn, norm)

    interview_rows = conn.execute(
        "SELECT clausule_id, bevinding, notitie, interviewed_at FROM interviews "
        "WHERE norm IN (?, 'beide') ORDER BY clausule_id",
        (norm,),
    ).fetchall()
    interviews: dict[str, dict[str, Any]] = {r["clausule_id"]: dict(r) for r in interview_rows}

    log = conn.execute("SELECT * FROM ingest_log").fetchall()
    ingest_info: dict[str, sqlite3.Row] = {r["bron"]: r for r in log}

    total_docs = conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
    total_miro = conn.execute("SELECT COUNT(*) FROM miro_notes").fetchone()[0]
    total_interviews = conn.execute("SELECT COUNT(*) FROM interviews").fetchone()[0]
    conn.close()

    matches: dict[str, list[dict[str, Any]]] = {k: [] for k in clausules}
    for row in rows:
        if row["clausule_id"] in matches:
            matches[row["clausule_id"]].append({"naam": row["naam"], "herkomst": row["herkomst"]})

    gedekt = [k for k, v in matches.items() if v]
    niet_gedekt = [k for k, v in matches.items() if not v]
    dekking_pct = round(len(gedekt) / len(clausules) * 100) if clausules else 0

    regels: list[str] = [
        f"# Audit Landschap — {norm_label}",
        "",
        "| | |",
        "|---|---|",
        f"| Datum | {date.today()} |",
        f"| Norm | {norm_label} |",
        f"| Drive-documenten in DB | {total_docs} |",
        f"| Miro-notities in DB | {total_miro} |",
        f"| Interview-bevindingen | {total_interviews} |",
    ]
    if "drive" in ingest_info:
        regels.append(f"| Drive laatste sync | {ingest_info['drive']['last_run'][:19]} |")
    if "miro" in ingest_info:
        regels.append(f"| Miro laatste sync | {ingest_info['miro']['last_run'][:19]} |")
    regels += [
        "",
        f"**Clausule-dekking: {len(gedekt)}/{len(clausules)} ({dekking_pct}%)**",
        "",
        "---",
        "",
        f"## Gedekte clausules ({len(gedekt)})",
        "",
    ]

    for clausule_id in sorted(gedekt):
        titel = clausules[clausule_id].get("titel", "")
        items = matches[clausule_id]
        drive_items = [i for i in items if i["herkomst"] == "Drive"]
        miro_items = [i for i in items if i["herkomst"] == "Miro"]
        regels.append(f"### {clausule_id} — {titel}")
        regels.append("")
        if drive_items:
            regels.append(f"**Drive** ({len(drive_items)} document(en)):")
            for item in drive_items[:10]:
                regels.append(f"- {item['naam']}")
            if len(drive_items) > 10:
                regels.append(f"- _...en {len(drive_items) - 10} meer_")
        if miro_items:
            regels.append("")
            regels.append(f"**Miro** ({len(miro_items)} notitie(s)):")
            for item in miro_items[:5]:
                tekst = (item["naam"] or "")[:80]
                regels.append(f"- _{tekst}_")
        regels.append("")

    nc_list = [k for k in niet_gedekt if interviews.get(k, {}).get("bevinding") == "NC"]
    ofi_list = [k for k in niet_gedekt if interviews.get(k, {}).get("bevinding") == "OFI"]
    positief_via_interview = [
        k for k in niet_gedekt if interviews.get(k, {}).get("bevinding") == "positief"
    ]
    niet_beantwoord = [k for k in niet_gedekt if k not in interviews]
    overgeslagen = [
        k for k in niet_gedekt if interviews.get(k, {}).get("bevinding") == "overgeslagen"
    ]

    regels += [
        "---",
        "",
        f"## Niet gedekte clausules ({len(niet_gedekt)}) ⚠️",
        "",
        "Deze clausules hebben geen gedocumenteerd bewijs in Drive of Miro.",
        "",
    ]

    if nc_list:
        regels += [f"### Non-conformiteiten ({len(nc_list)}) 🔴", ""]
        for cid in sorted(nc_list):
            titel = clausules[cid].get("titel", "")
            iv = interviews[cid]
            notitie = f" — _{iv['notitie']}_" if iv.get("notitie") else ""
            regels.append(f"- **{cid}** — {titel}{notitie}")
        regels.append("")

    if ofi_list:
        regels += [f"### Verbeterpunten / OFI ({len(ofi_list)}) 🟡", ""]
        for cid in sorted(ofi_list):
            titel = clausules[cid].get("titel", "")
            iv = interviews[cid]
            notitie = f" — _{iv['notitie']}_" if iv.get("notitie") else ""
            regels.append(
                f"- **{cid}** — {titel}{notitie} _(praktijk bestaat, documentatie ontbreekt)_"
            )
        regels.append("")

    if positief_via_interview:
        regels += [f"### Positief bevonden via interview ({len(positief_via_interview)}) 🟢", ""]
        for cid in sorted(positief_via_interview):
            titel = clausules[cid].get("titel", "")
            iv = interviews[cid]
            notitie = f" — _{iv['notitie']}_" if iv.get("notitie") else ""
            regels.append(f"- **{cid}** — {titel}{notitie}")
        regels.append("")

    if niet_beantwoord:
        regels += [
            f"### Nog niet geïnterviewd ({len(niet_beantwoord)}) — prioriteit voor interview",
            "",
        ]
        for cid in sorted(niet_beantwoord):
            titel = clausules[cid].get("titel", "")
            regels.append(f"- **{cid}** — {titel}")
        regels.append("")

    if overgeslagen:
        regels += [f"### Overgeslagen ({len(overgeslagen)})", ""]
        for cid in sorted(overgeslagen):
            titel = clausules[cid].get("titel", "")
            regels.append(f"- **{cid}** — {titel}")
        regels.append("")

    regels += ["", "---", f"_Gegenereerd op {date.today()} uit lokale audit DB_"]
    return "\n".join(regels)


def schrijf_landschap(
    norm: str,
    chapter: str | None = None,
    output_dir: str | os.PathLike[str] | None = None,
) -> str:
    """Genereer en schrijf het landschapsrapport naar `output_dir`/`Landschap_*.md`."""
    out_dir = Path(output_dir) if output_dir else DEFAULT_OUTPUT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    suffix = f"_h{chapter}" if chapter else ""
    pad = out_dir / f"Landschap_{norm}{suffix}_{date.today()}.md"
    inhoud = genereer_landschap(norm, chapter)
    pad.write_text(inhoud, encoding="utf-8")
    logger.info("Landschap geschreven: %s", pad)
    return str(pad)


def zoek_in_db(query: str) -> None:
    """CLI-helper: full-text-search over de lokale audit-DB."""
    from iso_audit.store import verbinding, zoek

    conn = verbinding()
    try:
        resultaten = zoek(conn, query)
    finally:
        conn.close()
    if not resultaten:
        print(f"Geen resultaten voor '{query}'")
        return
    print(f"\nZoekresultaten voor '{query}' ({len(resultaten)} gevonden):\n")
    for r in resultaten:
        print(f"  [{r['herkomst']}] {r['naam']}")
        print(f"    ...{r['fragment']}...")
        print()


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
        datefmt="%H:%M:%S",
    )
    parser = argparse.ArgumentParser(description="Audit-landschap rapport")
    parser.add_argument(
        "--norm",
        choices=["9001", "27001", "beide"],
        default=os.environ.get("AUDIT_NORM", "beide"),
    )
    parser.add_argument("--chapter", default=None, metavar="N")
    parser.add_argument(
        "--zoek",
        default=None,
        metavar="QUERY",
        help="Zoek in DB i.p.v. rapport genereren",
    )
    args = parser.parse_args()
    if args.zoek:
        zoek_in_db(args.zoek)
    else:
        pad = schrijf_landschap(args.norm, args.chapter)
        print(f"Landschap: {pad}")
    return 0
