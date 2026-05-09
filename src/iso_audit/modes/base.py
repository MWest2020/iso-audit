"""Mode Protocol — runmodes voor de pipeline.

Volledige implementatie komt in milestone C. In milestone A definiëren we
alleen de :class:`Decision` dataclass omdat ``iso_audit.notifiers.Notifier``
ernaar verwijst in zijn signatuur.

Twee modes (zie ``docs/modes.md`` en ``openspec/changes/iso-refactor/specs/modes/spec.md``):

- ``autonoom`` — voor cron-/CI-runs; Decisions worden zonder onderbreking
  geaccepteerd, behalve ``delete_data`` (altijd geblokkeerd).
- ``integer`` — mens-in-de-lus op kritieke beslismomenten; escaleert via
  ``Notifier`` en pauzeert de pipeline-thread tot de auditor reageert.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Protocol, runtime_checkable

Risiconiveau = Literal["laag", "midden", "hoog"]
"""Drie-puntsrisicoschaal voor :class:`Decision`. Hoog-risico beslissingen
worden in integer-modus altijd geescaleerd, midden afhankelijk van confidence,
laag autonoom afgehandeld."""


@dataclass(frozen=True, slots=True)
class Decision:
    """Een beslismoment dat de pipeline naar de actieve :class:`Mode` aanbiedt.

    Mode-implementatie ontvangt het object en geeft een definitief besluit
    (dict) terug. Pipeline emitteert Decisions op zeven vooraf vastgelegde
    punten — zie :mod:`iso_audit.modes` (milestone C) voor de tabel.
    """

    punt: str
    """Identifier van het beslispunt, e.g. ``"classify_finding"``."""

    context: dict[str, object]
    """Pipeline-staat op dit moment. Wat de Mode nodig heeft om te beslissen,
    zonder dat de Mode terug moet vragen."""

    voorstel: dict[str, object]
    """Het voorgestelde besluit dat de pipeline al heeft berekend (LLM-output,
    regel-resultaat, etc.). In autonoom-modus typisch direct geaccepteerd."""

    risico: Risiconiveau
    """Risico-niveau van het beslismoment. Bepaalt het escalatie-gedrag in
    integer-modus."""

    audit_id: str
    """Identifier van de huidige audit-run; correlatie naar ``decisions``-tabel."""


@runtime_checkable
class Mode(Protocol):
    """Contract voor pipeline-runmodes.

    Volledige implementaties (``AutonoomMode``, ``IntegerMode``) komen in
    milestone C. Het Protocol staat hier alvast zodat type-checkers tijdens
    milestone A code kunnen valideren die naar Modes verwijst.
    """

    naam: str
    """Uniek class-attribute; ``"autonoom"`` of ``"integer"``."""

    def beslis(self, decision: Decision) -> dict[str, object]:
        """Geef het definitieve besluit voor deze Decision.

        Pipeline gebruikt de teruggave als-of-it-is. In autonoom-modus typisch
        gelijk aan ``decision.voorstel``; in integer-modus mogelijk anders na
        auditor-bevestiging via :class:`iso_audit.notifiers.Notifier`.
        """
        ...
