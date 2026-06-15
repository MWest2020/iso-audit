"""Drive-document verificatie — ruimt de DB op na verwijderde of verouderde bestanden.

Controleert elk Drive-document in `documents`:

1. Bestaat het bestand nog op Drive? → niet → uit DB
2. Is het ouder dan `--voor` jaar? → rapport voor handmatige review

Gemigreerd uit `Ops_to_Biz/audit/verify_docs.py` per milestone B §2.3.8.
Wijziging: Drive-metadata-fetch gaat via `iso_audit.clients.gws._gws`
i.p.v. de losse `_metadata_via_sa`/`_metadata_via_gws`-paden — alle auth
via `gws auth login`.

Gebruik:
    python -m iso_audit.verify_docs              # droog-run
    python -m iso_audit.verify_docs --opruimen   # ook echt verwijderen
    python -m iso_audit.verify_docs --voor 2023  # drempel (default 2023)
"""

from __future__ import annotations

import argparse
import logging
import subprocess
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from iso_audit.clients.gws import _gws

load_dotenv()
logger = logging.getLogger(__name__)

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_OUTPUT_DIR = _REPO_ROOT / "output"


def _metadata(file_id: str) -> dict[str, Any] | None:
    """Haal Drive-metadata op. Returnt:

    - `dict` bij succes
    - `None` bij niet gevonden / no-access (404 / 403 / `notFound`)
    - `{}` bij onverwachte fout (caller moet "onbekend" interpreteren)
    """
    try:
        data = _gws(
            "drive",
            "files",
            "get",
            params={
                "fileId": file_id,
                "supportsAllDrives": True,
                "fields": "id,name,trashed,createdTime,modifiedTime",
            },
        )
    except subprocess.CalledProcessError as e:
        stderr = (e.stderr or "") if isinstance(e.stderr, str) else ""
        if "404" in stderr or "notFound" in stderr or "403" in stderr:
            return None
        logger.warning("gws-fout voor %s: %s", file_id, stderr[:200])
        return {}
    except Exception as e:
        logger.warning("Onverwachte fout bij metadata-fetch voor %s: %s", file_id, e)
        return {}
    if "error" in data:
        code = data["error"].get("code", 0)
        if code in (404, 403):
            return None
        logger.warning("gws-error-payload voor %s: %s", file_id, data["error"])
        return {}
    return data


def _parse_drive_datum(iso_str: str | None) -> datetime | None:
    """Parse Drive's ISO-8601 timestamp; tz-aware UTC."""
    if not iso_str:
        return None
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=UTC)
        return dt
    except ValueError:
        return None


def run(
    opruimen: bool = False,
    voor_jaar: int = 2023,
    output_dir: str | Path | None = None,
) -> None:
    """Verifieer alle Drive-documenten in DB en (optioneel) ruim niet-gevonden op."""
    from iso_audit.store import verbinding

    conn = verbinding()
    docs = conn.execute(
        "SELECT id, naam FROM documents WHERE herkomst = 'Drive' ORDER BY naam"
    ).fetchall()
    if not docs:
        logger.info("Geen Drive-documenten in DB.")
        conn.close()
        return

    logger.info("Verificatie van %d Drive-documenten via gws...", len(docs))

    niet_gevonden: list[dict[str, Any]] = []
    verouderd: list[dict[str, Any]] = []
    drempel = datetime(voor_jaar, 1, 1, tzinfo=UTC)

    for i, doc in enumerate(docs, 1):
        doc_id = doc["id"]
        naam = doc["naam"]
        meta = _metadata(doc_id)
        if meta is None:
            niet_gevonden.append({"id": doc_id, "naam": naam})
            logger.info("Niet gevonden op Drive: %s", naam)
            continue
        if meta and meta.get("trashed"):
            niet_gevonden.append(
                {"id": doc_id, "naam": naam, "reden": "verplaatst naar prullenbak"}
            )
            logger.info("In prullenbak op Drive: %s", naam)
            continue
        drive_datum = _parse_drive_datum(meta.get("modifiedTime") or meta.get("createdTime"))
        if drive_datum and drive_datum < drempel:
            verouderd.append(
                {
                    "id": doc_id,
                    "naam": naam,
                    "datum": drive_datum.strftime("%Y-%m-%d"),
                }
            )
        if i % 50 == 0:
            logger.info("  %d/%d gecontroleerd...", i, len(docs))

    print(f"\n{'=' * 60}")
    print(f"Drive-verificatie: {len(docs)} documenten gecontroleerd")
    print(f"{'=' * 60}\n")

    if niet_gevonden:
        print(f"❌ Niet meer beschikbaar op Drive ({len(niet_gevonden)}):")
        for d in niet_gevonden:
            status = "→ verwijderd uit DB" if opruimen else "→ gebruik --opruimen om te verwijderen"
            print(f"  [{d['id'][:20]}...] {d['naam']}  {status}")
        print()
    else:
        print("✅ Alle Drive-documenten nog bereikbaar.\n")

    if verouderd:
        print(
            f"⏰ Verouderd (gewijzigd vóór {voor_jaar}): {len(verouderd)} documenten "
            "— handmatige review:"
        )
        for d in verouderd:
            print(f"  {d['datum']}  {d['naam']}")
        out_dir = Path(output_dir) if output_dir else DEFAULT_OUTPUT_DIR
        out_dir.mkdir(parents=True, exist_ok=True)
        rapport_pad = out_dir / f"verouderde_documenten_{date.today()}.md"
        with rapport_pad.open("w", encoding="utf-8") as f:
            f.write(f"# Verouderde Drive-documenten (gewijzigd vóór {voor_jaar})\n\n")
            f.write(f"Gegenereerd: {date.today()}  \n")
            f.write(f"Totaal: {len(verouderd)} van {len(docs)} documenten\n\n")
            f.write("| Datum gewijzigd | Naam | Drive-link |\n")
            f.write("|---|---|---|\n")
            for d in sorted(verouderd, key=lambda x: x["datum"]):
                link = f"https://drive.google.com/file/d/{d['id']}"
                f.write(f"| {d['datum']} | {d['naam']} | [open]({link}) |\n")
        print(f"\nLijst opgeslagen: {rapport_pad}")
        print()

    if opruimen and niet_gevonden:
        ids = [d["id"] for d in niet_gevonden]
        placeholders = ",".join("?" * len(ids))
        # `placeholders` is alleen `?,?,...` (geen user input).
        sql_clause = f"DELETE FROM clause_matches WHERE doc_id IN ({placeholders})"  # nosec B608
        sql_docs = f"DELETE FROM documents WHERE id IN ({placeholders})"  # nosec B608
        conn.execute(sql_clause, ids)
        conn.execute(sql_docs, ids)
        conn.commit()
        print(f"🗑️  {len(ids)} document(en) verwijderd uit DB (documents + clause_matches).")
    elif niet_gevonden:
        print("[info] Droog-run — geen wijzigingen. Gebruik --opruimen om te verwijderen.")
    conn.close()

    totaal_verwijderd = len(niet_gevonden) if opruimen else 0
    logger.info(
        "Klaar: %d niet gevonden, %d verouderd, %d verwijderd",
        len(niet_gevonden),
        len(verouderd),
        totaal_verwijderd,
    )


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
        datefmt="%H:%M:%S",
    )
    parser = argparse.ArgumentParser(description="Drive-documenten verifiëren en DB opruimen")
    parser.add_argument(
        "--opruimen",
        action="store_true",
        help="Verwijder niet-bestaande documenten uit de DB (standaard: droog-run)",
    )
    parser.add_argument(
        "--voor",
        type=int,
        default=2023,
        metavar="JAAR",
        help="Verouderd = ingested vóór dit jaar (standaard: 2023)",
    )
    args = parser.parse_args()
    run(opruimen=args.opruimen, voor_jaar=args.voor)
    return 0
