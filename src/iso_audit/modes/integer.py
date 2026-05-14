"""`IntegerMode` — mens-in-de-lus op kritieke beslismomenten.

Implementeert de :class:`iso_audit.modes.base.Mode` Protocol per
:doc:`openspec/changes/iso-refactor/specs/modes/spec.md` §"IntegerMode".

Regels (samengevat):

- `risico="laag"` → voorstel direct retourneren, TENZIJ
  `context["vraag_bevestiging"] is True` (relevant voor `ingest_scope`).
- `risico="midden"` → voorstel direct retourneren, TENZIJ
  `context["confidence"] < 0.7` — dan escaleren.
- `risico="hoog"` → altijd escaleren via :class:`Notifier`.

Bij escalatie SHALL:

1. Eerst een `decisions`-rij met `status="pending"` schrijven
   (`notifier_naam=notifier.naam`).
2. `notifier.vraag_besluit(decision)` aanroepen voor handoff.
3. Polling op `status='resolved'` of `'cancelled'` tot antwoord binnenkomt
   (de :class:`DecisionResolver` schrijft daar de update).

Het concrete kanaal (Slack, Email, Teams) is onzichtbaar — alleen de
Notifier-instantie via DI.
"""

from __future__ import annotations

import logging
import sqlite3
import time
from typing import TYPE_CHECKING, Any

from iso_audit.modes.base import Decision

if TYPE_CHECKING:
    from iso_audit.notifiers.base import Notifier

logger = logging.getLogger(__name__)

_DEFAULT_POLL_INTERVAL = 1.0  # seconden tussen status-checks
_DEFAULT_TIMEOUT_S = 24 * 3600.0  # 24 uur max wachten op auditor
_CONFIDENCE_GRENS = 0.7


class IntegerMode:
    """Integer-modus: pauzeert pipeline-thread tot auditor heeft beslist."""

    naam: str = "integer"

    def __init__(
        self,
        notifier: Notifier,
        conn: sqlite3.Connection,
        poll_interval_s: float = _DEFAULT_POLL_INTERVAL,
        timeout_s: float = _DEFAULT_TIMEOUT_S,
    ) -> None:
        """Construct met Notifier (DI) en SQLite-verbinding voor `decisions`."""
        self._notifier = notifier
        self._conn = conn
        self._poll_interval_s = poll_interval_s
        self._timeout_s = timeout_s

    @property
    def notifier(self) -> Notifier:
        """De geinjecteerde notifier (read-only)."""
        return self._notifier

    def beslis(self, decision: Decision) -> dict[str, object]:
        """Geef het definitieve besluit voor een Decision.

        Zie module-docstring voor de risico-regels.
        """
        if self._moet_escaleren(decision):
            return self._escaleer(decision)
        return dict(decision.voorstel)

    def _moet_escaleren(self, decision: Decision) -> bool:
        """Beslis of een Decision via de Notifier naar de auditor moet."""
        if decision.risico == "hoog":
            return True
        if decision.risico == "midden":
            confidence = decision.context.get("confidence")
            return (
                isinstance(confidence, int | float) and confidence < _CONFIDENCE_GRENS
            )
        # risico = "laag"
        return bool(decision.context.get("vraag_bevestiging"))

    def _escaleer(self, decision: Decision) -> dict[str, object]:
        """Schrijf pending-rij, roep Notifier, wacht op auditor-respons."""
        from iso_audit.store import schrijf_decision

        decision_id = schrijf_decision(
            self._conn,
            audit_id=decision.audit_id,
            punt=decision.punt,
            context=dict(decision.context),
            voorstel=dict(decision.voorstel),
            risico=decision.risico,
            status="pending",
            notifier_naam=self._notifier.naam,
        )
        notifier_correlation_id = self._notifier.vraag_besluit(decision)
        logger.info(
            "Decision %d geescaleerd via %s (notifier-correlatie %s)",
            decision_id,
            self._notifier.naam,
            notifier_correlation_id,
        )
        besluit = self._wacht_op_resolution(decision_id)
        return besluit

    def _wacht_op_resolution(self, decision_id: int) -> dict[str, object]:
        """Poll de `decisions`-tabel tot status != 'pending', met timeout.

        Bij elke iteratie wordt eerst `commit()` aangeroepen om eventuele
        impliciete read-transaction af te sluiten — anders zou een SELECT
        op deze connectie commits van een andere thread/process pas zien
        nadat de eigen transactie eindigt (SQLite-default `isolation_level=""`).
        """
        from iso_audit.store import laad_decision

        deadline = time.monotonic() + self._timeout_s
        while time.monotonic() < deadline:
            self._conn.commit()
            row = laad_decision(self._conn, decision_id)
            if row is None:
                raise RuntimeError(f"decision_id {decision_id} verdwenen uit DB")
            if row["status"] != "pending":
                import json

                besluit_json: str | None = row["besluit_json"]
                if besluit_json:
                    besluit: dict[str, Any] = json.loads(besluit_json)
                    return besluit
                # cancelled zonder besluit → expliciete skip.
                return {"actie": "skip", "reden": "decision cancelled"}
            time.sleep(self._poll_interval_s)
        raise TimeoutError(
            f"Auditor heeft niet binnen {self._timeout_s}s gereageerd op decision {decision_id}"
        )
