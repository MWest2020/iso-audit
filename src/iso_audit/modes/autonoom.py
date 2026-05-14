"""`AutonoomMode` — selectieve persistentie, geen mens-in-de-lus.

Implementeert de :class:`iso_audit.modes.base.Mode` Protocol per
:doc:`openspec/changes/iso-refactor/specs/modes/spec.md` §"AutonoomMode".

Regels (samengevat):

- `risico="laag"` of `"midden"` → voorstel direct retourneren; GEEN rij in
  `decisions`-tabel.
- `risico="hoog"`:
  - `punt="delete_data"` → besluit ``{"actie": "skip", "reden": ...}``;
    rij met `status="resolved"`, `notifier_naam=NULL`.
  - andere punten → voorstel als besluit; rij met `status="resolved"`,
    `notifier_naam=NULL`.

Selectieve persistentie voorkomt pollutie van `decisions` met laag-risico
rijen waar voorstel == besluit; alleen hoog-risico rijen hebben analytische
waarde voor de mirror-laag (capability 3).
"""

from __future__ import annotations

import sqlite3
from typing import Any

from iso_audit.modes.base import Decision


class AutonoomMode:
    """Autonoom-modus: cron-/CI-friendly, geen externe call per beslismoment."""

    naam: str = "autonoom"

    def __init__(self, conn: sqlite3.Connection | None = None) -> None:
        """`conn` is optioneel — alleen nodig voor hoog-risico persistentie.

        Zonder conn worden besluiten nog steeds geretourneerd (handig voor
        tests + lichte runs), maar GEEN `decisions`-rijen geschreven.
        """
        self._conn = conn

    def beslis(self, decision: Decision) -> dict[str, object]:
        """Geef het definitieve besluit voor een Decision.

        Zie module-docstring voor de regels per (risico, punt).
        """
        if decision.risico in ("laag", "midden"):
            return dict(decision.voorstel)

        # Hoog-risico.
        if decision.punt == "delete_data":
            besluit: dict[str, object] = {
                "actie": "skip",
                "reden": "delete_data niet toegestaan in autonoom-modus",
            }
        else:
            besluit = dict(decision.voorstel)

        self._persist_resolved(decision, besluit)
        return besluit

    def _persist_resolved(self, decision: Decision, besluit: dict[str, Any]) -> None:
        """Schrijf een `status='resolved'` rij voor hoog-risico beslismomenten."""
        if self._conn is None:
            return
        from iso_audit.store import schrijf_decision

        schrijf_decision(
            self._conn,
            audit_id=decision.audit_id,
            punt=decision.punt,
            context=dict(decision.context),
            voorstel=dict(decision.voorstel),
            risico=decision.risico,
            status="resolved",
            besluit=besluit,
            notifier_naam=None,
        )
