"""Notifier Protocol — contract voor handoff-kanalen tussen pipeline en auditor.

Een Notifier is bewust géén Sink: de semantiek is anders. Sink levert one-shot,
Notifier vraagt om respons (mens beslist; pipeline pauzeert tot antwoord).

Implementaties komen in milestone C: ``SlackNotifier`` (Block Kit met action-buttons)
en ``EmailNotifier`` (SMTP-out + lokaal Flask-portaal voor magic-link-respons).

Response-parsing is bewust gescheiden in een aparte ``DecisionResolver``-Protocol.
Dat zorgt dat Slack-button-payloads, Email-magic-link-clicks, en toekomstige
Teams-card-actions allemaal dezelfde shape opleveren waar de pipeline-thread op
wacht — kanaal-specifieke parsing is adapter-detail.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from iso_audit.modes.base import Decision


@runtime_checkable
class Notifier(Protocol):
    """Contract voor elk handoff-kanaal."""

    naam: str
    """Uniek class-attribute; lowercase, kebab-case bij multi-woord
    (e.g. ``"slack"``, ``"email"``, ``"mcp-teams"``)."""

    def vraag_besluit(self, decision: Decision) -> str:
        """Stuur een ``Decision`` naar het kanaal en retourneer een ``decision_id``.

        Het ``decision_id`` is de correlatie-sleutel die de :class:`DecisionResolver`
        gebruikt om de respons terug te koppelen naar de juiste pipeline-thread
        en de juiste rij in de ``decisions``-tabel.

        Implementaties SHALL bij identieke ``Decision``-input opeenvolgende calls
        unieke decision_ids genereren (geen collisions); contract-tests verifiëren
        dit.
        """
        ...

    def healthcheck(self) -> dict[str, object]:
        """Retourneer status + kanaal-context.

        Vereiste keys: ``status`` (``"ok"``/``"fail"``/``"degraded"``), ``naam``.
        Aanbevolen: ``tenant`` (Slack-workspace-id, SMTP-host, etc.) en bij faal
        een ``reden``-veld.
        """
        ...


@runtime_checkable
class DecisionResolver(Protocol):
    """Kanaal-agnostische response-handler.

    Wanneer een auditor reageert (Slack-button, Email-magic-link, Teams-card),
    parseert de notifier de respons naar een ``(decision_id, action,
    modified_payload)``-shape en roept de resolver aan. De resolver schrijft het
    resultaat naar de ``decisions``-tabel en deblokkeert de pipeline-thread.

    Toegestane action-waarden: ``"approve"``, ``"reject"``, ``"modify"``,
    ``"abort"``. Andere waarden moeten een ``ValueError`` opleveren.
    """

    def resolve(
        self,
        decision_id: str,
        action: str,
        modified_payload: dict[str, object] | None = None,
    ) -> None:
        """Sluit een geescaleerde Decision af.

        :param decision_id: correlatie-sleutel die de notifier teruggaf bij ``vraag_besluit``
        :param action: één van ``"approve"``, ``"reject"``, ``"modify"``, ``"abort"``
        :param modified_payload: alleen vereist bij ``action="modify"``; bevat het
            aangepaste besluit
        :raises ValueError: bij onbekende ``action``-waarde
        """
        ...
