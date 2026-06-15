"""Genereer geanonimiseerde fixture-CSV uit Ops_to_Biz audit-output.

Reproduceerbaarheid: dit script is checked-in zodat de fixture op elk moment
opnieuw is af te leiden uit de bron-CSV (mits beschikbaar). De fixture-output
zelf (findings.csv + findings.expected.csv) is ook checked-in zodat snapshot-
tests werken zonder toegang tot de oorspronkelijke audit-data.

Gebruik:
    python generate_fixture.py --source <path-to-bevindingen.csv>
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
import sys
from collections.abc import Callable
from pathlib import Path

NAME_MAP: dict[str, str] = {
    # Persoonsnamen uit de audit-dataset (deterministische pseudoniemen).
    "Sarai": "Medewerker A",
    "Goya": "Medewerker B",
    "Thijn": "Medewerker C",
    "Brigitte": "Medewerker D",
    "Alex": "Medewerker E",
    # Rollen — vervang met functienaam i.p.v. persoonsnaam.
    "Mark Westerweel": "Auditor",
    "Marianne Poot": "Hoofd ISO",
    "Marianne": "Hoofd ISO",
    "Marleen": "KAM-coordinator",
    "Ruben van der Linde": "ISO-verantwoordelijke",
    "Ruben": "ISO-verantwoordelijke",
    "Remco Damhuis": "Operationeel-kwaliteit",
    "Robert": "Bestuur",
    # Organisatie en partners.
    "Conduction": "OrganisatieX",
}

URL_PREFIX = "https://drive.google.com/file/d/"
URL_REPLACEMENT_PREFIX = "https://example.invalid/d/"


def hash_doc_id(orig: str) -> str:
    """SHA-256 prefix (22 chars) — gelijkblijvende vorm, geen herleidbaarheid."""
    return hashlib.sha256(orig.encode("utf-8")).hexdigest()[:22]


def anonymize_text(text: str, id_map: dict[str, str]) -> str:
    """Vervang namen en Drive-IDs in vrije tekst."""
    if not text:
        return text
    out = text
    # Names — order matters: langste namen eerst zodat 'Mark Westerweel'
    # niet half-vervangen wordt door 'Mark' patroon.
    for orig in sorted(NAME_MAP, key=len, reverse=True):
        out = re.sub(rf"\b{re.escape(orig)}\b", NAME_MAP[orig], out)

    # Drive-URL's met embedded ID.
    def url_sub(match: re.Match[str]) -> str:
        orig_id = match.group(1)
        new_id = id_map.setdefault(orig_id, hash_doc_id(orig_id))
        return f"{URL_REPLACEMENT_PREFIX}{new_id}/view"

    out = re.sub(rf"{re.escape(URL_PREFIX)}([A-Za-z0-9_-]+)/view", url_sub, out)
    # Losse Drive-IDs in vrije tekst: zou kunnen, maar regex was te greedy
    # (matchte ook lange Nederlandse woorden zoals 'informatiebeveiligings-
    # incidenten'). doc_id-veld wordt apart gehashed; URL-embedded IDs zijn
    # hierboven al afgevangen. Vrije tekst-Drive-IDs zijn in de praktijk
    # zeldzaam; als ze toch voorkomen, kun je ze in de output-CSV handmatig
    # corrigeren of de generator uitbreiden met een specifiekere pattern
    # (bv. mengsel-van-letters-cijfers-streepjes).
    return out


# Selectie-criteria — 20 representatieve rijen.
# Format: (label, predicate, max_count)
SELECTION: list[tuple[str, Callable[[dict[str, str]], bool], int]] = [
    # Beide NC's (allebei 27001 in deze dataset — zie README "Tegenwoordige beperking").
    ("NC", lambda r: r["classificatie"] == "NC", 2),
    # OFI top-3 thema's.
    (
        "OFI-memo",
        lambda r: r["classificatie"] == "OFI" and r["thema"] == "Memo & afwijkingsregistratie",
        3,
    ),
    ("OFI-audit", lambda r: r["classificatie"] == "OFI" and r["thema"] == "Auditprogramma", 3),
    (
        "OFI-logging",
        lambda r: r["classificatie"] == "OFI" and r["thema"] == "Logging & monitoring",
        2,
    ),
    # OFI Miro-bron (kleurconventie-validatie).
    ("OFI-miro", lambda r: r["classificatie"] == "OFI" and r["herkomst"] == "Miro", 1),
    # OFI overig — voor brede clausule-dekking.
    (
        "OFI-privacy",
        lambda r: r["classificatie"] == "OFI" and r["thema"] == "Privacy & persoonsgegevens",
        1,
    ),
    # Positieve bevindingen, mix herkomst.
    ("positief-drive", lambda r: r["classificatie"] == "positief" and r["herkomst"] == "Drive", 4),
    ("positief-miro", lambda r: r["classificatie"] == "positief" and r["herkomst"] == "Miro", 1),
    # Lege classificatie ("geen bevinding").
    ("geen-bevinding", lambda r: r["classificatie"] == "geen bevinding", 1),
    # Buffer: positief uit "beide" norm, voor coverage van norm=beide.
    ("positief-beide", lambda r: r["classificatie"] == "positief" and r["norm"] == "beide", 2),
]


def select_rows(all_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    """Deterministische selectie volgens criteria."""
    # Stabiele volgorde voor reproduceerbaarheid.
    all_rows.sort(key=lambda r: (r["classificatie"], r["thema"], r["clausule"], r["doc_id"]))
    selected: list[dict[str, str]] = []
    used: set[int] = set()
    for label, pred, n in SELECTION:
        picked = 0
        for idx, r in enumerate(all_rows):
            if idx in used:
                continue
            if pred(r):
                selected.append(r)
                used.add(idx)
                picked += 1
                if picked >= n:
                    break
        if picked < n:
            print(f"[warn] criterium '{label}' wilde {n}, kreeg {picked}", file=sys.stderr)
    return selected


def anonymize_row(row: dict[str, str], id_map: dict[str, str]) -> dict[str, str]:
    """Anonimiseer één rij — keep schema, replace PII en IDs."""
    new = dict(row)
    # doc_id zelf hashen + map onthouden.
    orig_id = row["doc_id"]
    new["doc_id"] = id_map.setdefault(orig_id, hash_doc_id(orig_id))
    # URL — als die het bekende patroon volgt.
    if URL_PREFIX in row["doc_url"]:
        new["doc_url"] = anonymize_text(row["doc_url"], id_map)
    else:
        new["doc_url"] = ""
    # Vrije tekst-velden. clausule_titel staat hier expliciet NIET bij —
    # dat is een normtekst (geen PII), nooit aanraken.
    for field in ("document_naam", "beschrijving", "onderbouwing"):
        new[field] = anonymize_text(row[field], id_map)
    # classified_at op vaste datum voor reproduceerbaarheid.
    new["classified_at"] = "2026-01-01T00:00:00Z"
    return new


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source", type=Path, required=True, help="Pad naar Bevindingen_beide_v3.3_2026-05-05.csv"
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path(__file__).parent,
        help="Output-dir (default: dit script's dir)",
    )
    args = parser.parse_args()

    if not args.source.is_file():
        print(f"source niet gevonden: {args.source}", file=sys.stderr)
        return 2

    with args.source.open() as f:
        rows = list(csv.DictReader(f))
    print(f"bron: {len(rows)} rijen", file=sys.stderr)

    selected = select_rows(rows)
    print(f"geselecteerd: {len(selected)} rijen", file=sys.stderr)

    id_map: dict[str, str] = {}
    anonymized = [anonymize_row(r, id_map) for r in selected]

    fieldnames = list(rows[0].keys()) if rows else []
    findings_path = args.out_dir / "findings.csv"
    with findings_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(anonymized)
    print(f"geschreven: {findings_path}", file=sys.stderr)

    # findings.expected.csv = subset met enkel doc_id + classificatie + clausule
    # (de "antwoord-sleutel" voor snapshot-tests).
    expected_path = args.out_dir / "findings.expected.csv"
    with expected_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["doc_id", "classificatie", "clausule", "norm"])
        writer.writeheader()
        for r in anonymized:
            writer.writerow(
                {
                    "doc_id": r["doc_id"],
                    "classificatie": r["classificatie"],
                    "clausule": r["clausule"],
                    "norm": r["norm"],
                }
            )
    print(f"geschreven: {expected_path}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
