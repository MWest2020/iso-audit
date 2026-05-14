"""`DecisionResolver` — kanaal-agnostische response-handler (§3.2.1).

Wanneer een auditor reageert (Slack-button, Email-magic-link, Teams-card),
parseert de Notifier de respons naar `(decision_id, action, modified_payload)`
en roept :meth:`SqliteDecisionResolver.resolve` aan. De resolver schrijft
het besluit naar de `decisions`-tabel en deblokkeert de wachtende pipeline-
thread (IntegerMode polt de tabel en ziet de status-change).

Toegestane action-waarden: ``"approve"``, ``"reject"``, ``"modify"``,
``"abort"``. Andere waarden -> :class:`ValueError`.
"""

from __future__ import annotations

import json
import logging
import sqlite3
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from iso_audit.notifiers.base import DecisionResolver  # noqa: F401

logger = logging.getLogger(__name__)

VALID_ACTIONS: tuple[str, ...] = ("approve", "reject", "modify", "abort")


class SqliteDecisionResolver:
    """Concrete `DecisionResolver` die de `decisions`-tabel in SQLite update.

    De decision_id-shape is hier de string-vorm van de SQLite primary-key
    (`decisions.id`). Notifiers krijgen die terug uit `vraag_besluit()` en
    moeten hem opnieuw aanleveren bij `resolve()`.

    Bij `action == "modify"` is `modified_payload` verplicht — anders
    raised :class:`ValueError`.
    """

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def resolve(
        self,
        decision_id: str,
        action: str,
        modified_payload: dict[str, object] | None = None,
    ) -> None:
        """Update de `decisions`-rij en deblokkeer de pipeline-thread."""
        if action not in VALID_ACTIONS:
            raise ValueError(f"Onbekende action {action!r}; verwacht een van {VALID_ACTIONS}")
        if action == "modify" and modified_payload is None:
            raise ValueError("modified_payload is verplicht bij action='modify'")

        from iso_audit.store import laad_decision, resolve_decision

        try:
            dec_id_int = int(decision_id)
        except ValueError as exc:
            raise ValueError(
                f"decision_id moet een integer-string zijn, kreeg {decision_id!r}"
            ) from exc

        row = laad_decision(self._conn, dec_id_int)
        if row is None:
            raise KeyError(f"Geen decision met id {dec_id_int} in DB")

        besluit = _besluit_voor_action(row, action, modified_payload)
        status = "cancelled" if action == "abort" else "resolved"
        resolve_decision(self._conn, dec_id_int, besluit=besluit, status=status)
        logger.info(
            "Decision %d -> %s (action=%s, notifier=%s)",
            dec_id_int,
            status,
            action,
            row["notifier_naam"],
        )


def _besluit_voor_action(
    row: sqlite3.Row,
    action: str,
    modified_payload: dict[str, object] | None,
) -> dict[str, Any]:
    """Bouw het `besluit_json`-veld op basis van de auditor-action."""
    if action == "approve":
        return dict(json.loads(row["voorstel_json"]))
    if action == "reject":
        return {"actie": "reject", "voorstel_afgewezen": True}
    if action == "modify":
        if modified_payload is None:  # defensief; resolve() valideert al
            raise ValueError("modify-action zonder payload mocht hier niet komen")
        return dict(modified_payload)
    # abort
    return {"actie": "abort", "reden": "auditor afgebroken"}
