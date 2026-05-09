"""Sink Protocol — contract voor schrijf-adapters.

Spec-only in milestone A. Eerste implementatie (DriveSink) komt in milestone C.

Reden om het Protocol nu te definiëren zonder implementatie: voorkomt dat de
verhuizing in milestone B het schrijfpad ongedefinieerd laat. Reporting-modules
worden in B gemigreerd naar ``iso_audit.reporting/`` als interne modules; hun
consolidatie achter een Sink gebeurt in C.

Asymmetrie ten opzichte van Source is bewust: Source enumereert + fetcht, Sink
levert one-shot. Symmetrie afdwingen voegt complexiteit toe zonder use-case
(zie design.md decision 2).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable


@dataclass(frozen=True, slots=True)
class SinkPayload:
    """Basis-class voor alle Sink-payloads.

    Concrete payloads (``ReportPayload``, ``NotificationPayload``,
    ``MirrorPayload``) erven hiervan en voegen velden toe. Sink-implementaties
    accepteren één of meer payload-types via type-narrowing in ``send``.
    """


@dataclass(frozen=True, slots=True)
class ReportPayload(SinkPayload):
    """Een gegenereerd rapport dat naar een doelsysteem moet."""

    audit_id: str
    """Identifier van de audit-run waar dit rapport bij hoort."""

    titel: str

    inhoud_html: str
    """De rapport-inhoud als HTML; Sink mag converteren naar bron-specifiek formaat."""

    bijlagen: list[str]
    """URIs naar bijlagen (PDF-versie, XLSX-bevindingenlijst, presentatie, …).
    Lege lijst is toegestaan."""


@dataclass(frozen=True, slots=True)
class NotificationPayload(SinkPayload):
    """Een notificatie die niet om interactie vraagt — fire-and-forget.

    Voor interactieve handoff (auditor moet beslissen) zie ``iso_audit.notifiers``;
    dat is een eigen Protocol omdat de semantiek anders is.
    """

    titel: str
    bericht: str
    ontvangers: list[str]


@dataclass(frozen=True, slots=True)
class MirrorPayload(SinkPayload):
    """Placeholder voor toekomstige spiegel-laag (capability 3 uit missie).

    Niet implementeren in deze refactor. Reservering bestaat zodat de
    Sink-hierarchy in milestone A vorm heeft die latere change-proposals kunnen
    consumeren zonder het Protocol te breken.
    """


@dataclass(frozen=True, slots=True)
class SinkResult:
    """Resultaat van een ``Sink.send``-call."""

    succes: bool
    bron_id: str | None
    """Identifier in het doelsysteem waar de payload landde (e.g. Drive-file-id)."""

    bericht: str
    """Mens-leesbare beschrijving — bij faal de fout-reden."""


@runtime_checkable
class Sink(Protocol):
    """Contract voor elke schrijf-adapter.

    Een adapter implementeert ``send`` (bron-specifieke schrijf-actie) en
    ``healthcheck`` (configuratie-validatie). Adapters registreren zichzelf
    via :func:`iso_audit.sinks.register` analoog aan Sources.
    """

    naam: str
    """Uniek class-attribute; lowercase, kebab-case bij multi-woord."""

    def send(self, payload: SinkPayload) -> SinkResult:
        """Schrijf de payload naar het doelsysteem.

        Implementaties mogen specifieke payload-types vereisen via runtime-check
        (e.g. een DriveSink die alleen ReportPayload accepteert) — geef in dat
        geval een ``SinkResult(succes=False, ...)`` terug bij niet-ondersteund type
        in plaats van een exception.
        """
        ...

    def healthcheck(self) -> dict[str, object]:
        """Retourneer status + doelsysteem-context (analoog aan Source.healthcheck)."""
        ...
