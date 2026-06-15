"""Norm-database lookup — plug-in, user-pointed, hard-fail.

De norm-DB-content hoort niet in de repo: de gebruiker wijst een directory met
``<slug>.yaml``-norm-bestanden aan. Een ontbrekende clausule of een ontbrekende
taal-tekst is een **harde fout** — de memo mag nooit een verzonnen of leeg
norm-citaat bevatten.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from iso_audit.memo.models import ClauseCitation


class NormDatabaseError(ValueError):
    """Norm-database kon niet geladen worden of is structureel ongeldig."""


class ClausuleOntbreektError(NormDatabaseError):
    """Een gevraagde standaard/clausule/taal-tekst bestaat niet in de norm-DB."""


def _laad_bestand(pad: Path) -> tuple[str, dict[str, Any]]:
    data: Any = yaml.safe_load(pad.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or "clauses" not in data:
        raise NormDatabaseError(f"Norm-bestand {pad} mist een 'clauses'-sectie.")
    meta = data.get("metadata", {})
    slug = meta.get("slug") or pad.stem
    if not isinstance(data["clauses"], dict):
        raise NormDatabaseError(f"Norm-bestand {pad}: 'clauses' is geen mapping.")
    return str(slug), data


class NormDatabase:
    """Geladen norm-database; resolvet genormeerde citaten per (standaard, clausule, taal)."""

    def __init__(self, norms_dir: str | Path) -> None:
        base = Path(norms_dir).expanduser().resolve()
        if not base.is_dir():
            raise NormDatabaseError(
                f"Norm-DB-directory bestaat niet: {base}. Wijs een norm-DB-pad aan."
            )
        self._db: dict[str, dict[str, Any]] = {}
        bestanden = sorted(base.glob("*.yaml"))
        if not bestanden:
            raise NormDatabaseError(f"Geen norm-bestanden (*.yaml) in {base}.")
        for pad in bestanden:
            slug, data = _laad_bestand(pad)
            self._db[slug] = data

    def standards(self) -> list[str]:
        return sorted(self._db)

    def citation(self, standard: str, clause: str, language: str) -> ClauseCitation:
        """Geef het citaat voor (standard, clause) in ``language``; hard-fail bij ontbreken."""
        norm = self._db.get(standard)
        if norm is None:
            raise ClausuleOntbreektError(
                f"Standaard {standard!r} niet in norm-DB. Beschikbaar: {self.standards()}."
            )
        clauses: dict[str, Any] = norm["clauses"]
        entry = clauses.get(clause)
        if entry is None:
            raise ClausuleOntbreektError(
                f"Clausule {clause!r} ontbreekt in {standard}. Vul de norm-DB aan; "
                "een memo mag geen verzonnen citaat bevatten."
            )
        titel = entry.get(f"title_{language}")
        tekst = entry.get(f"text_{language}")
        if not titel or not tekst:
            raise ClausuleOntbreektError(
                f"Norm-tekst voor {standard} {clause} ontbreekt in taal {language!r}. "
                "Lever een norm-DB met deze taal aan."
            )
        return ClauseCitation(
            standard=standard,
            clause=clause,
            title=str(titel).strip(),
            text=str(tekst).strip(),
        )


def laad_norm_db(norms_dir: str | Path) -> NormDatabase:
    """Laad een norm-database uit een directory met ``<slug>.yaml``-bestanden."""
    return NormDatabase(norms_dir)
