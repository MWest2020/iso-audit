"""Source Protocol — contract voor alle bron-adapters.

Alle bronnen (Drive, Planning, Jira, MCP, REST, …) implementeren dit Protocol.
De pipeline kent het Protocol; concrete adapters leven in ``iso_audit.sources.<naam>``
en registreren zichzelf via :func:`iso_audit.sources.register`.

Design-discipline (zie ``openspec/changes/iso-refactor/design.md``):

- **Read-only.** Schrijven naar bron-systemen gaat via ``iso_audit.sinks``,
  nooit via een Source. Een adapter die zowel lezen als schrijven ondersteunt
  registreert twee classes (bv. ``DriveSource`` + ``DriveSink``).
- **Immutable runtime-configuratie.** Een Source wordt geconfigureerd uit
  env-vars of config-bestand bij pipeline-start en daarna niet meer gewijzigd.
  Adapters bieden geen ``set_folder()``, ``set_filter()`` of equivalent. Dit is
  een directe vertaling van missie-capability 1 ("toegang van tevoren ingericht
  en daarna onveranderlijk binnen een audit-periode") naar code-gedrag.
- **`naam` is uniek.** Lowercase kebab-case bij multi-woord. Voorbeeld: ``"drive"``,
  ``"jira"``, ``"mcp:asana"``.
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from typing import Protocol, runtime_checkable


@dataclass(frozen=True, slots=True)
class Document:
    """Een document zoals het uit een bron komt — bron-onafhankelijke shape."""

    id: str
    """Bron-specifieke identifier, uniek binnen ``bron``."""

    titel: str
    """Mens-leesbare titel."""

    bron: str
    """Naam van de Source-adapter die dit document leverde (e.g. ``"drive"``)."""

    type: str
    """Categorisering binnen de bron (e.g. ``"beleid"``, ``"procedure"``,
    ``"werkinstructie"``, ``"ticket"``)."""

    laatst_gewijzigd: str
    """ISO-8601 timestamp; als de bron geen exacte tijd geeft, een datum."""

    inhoud_uri: str
    """Pointer die :meth:`Source.fetch_content` gebruikt om de inhoud op te halen.
    Vorm is bron-specifiek (Google-Drive file-id, Jira-issue-key, HTTP-URL, etc.)."""


@dataclass(frozen=True, slots=True)
class Finding:
    """Een bevinding zoals het uit een bron komt.

    Bevindingen kunnen direct uit een bron komen (Miro-stickies, Jira-issues
    met een audit-label) of afgeleid worden van documenten door een classifier.
    Dit dataclass beschrijft de eerste vorm.
    """

    id: str
    """Bron-specifieke identifier."""

    bron: str
    """Naam van de Source-adapter."""

    clausule_ids: list[str]
    """ISO-clausules waar deze bevinding aan gekoppeld is. Lege lijst betekent
    dat clausule-toekenning later in de pipeline gebeurt."""

    omschrijving: str
    """Mens-leesbare beschrijving."""

    bewijs_uris: list[str]
    """URIs naar onderliggend bewijsmateriaal (documenten, screenshots, tickets).
    Lege lijst is toegestaan."""


@runtime_checkable
class Source(Protocol):
    """Contract voor elke bron-adapter.

    Een adapter implementeert deze methodes en registreert zichzelf:

    .. code-block:: python

        from iso_audit.sources import register

        @register
        class DriveSource:
            naam = "drive"

            def list_documents(self, filter=None): ...
            def fetch_content(self, doc): ...
            def list_findings(self, sessie_id): ...
            def healthcheck(self): ...

    De adapter SHALL configuratie immutable houden na ``__init__``.
    """

    naam: str
    """Uniek class-attribute; lowercase, kebab-case bij multi-woord."""

    def list_documents(self, filter: dict[str, object] | None = None) -> Iterator[Document]:
        """Yield documenten uit de bron.

        ``filter`` is een dict van bron-specifieke filter-criteria; ``None`` betekent
        "alles wat de bron-configuratie toelaat". Bron-specifieke filters zijn
        adapter-private; pipeline-code passeert filters door zonder ze te
        interpreteren.

        Returnt een Iterator (niet list) zodat lazy iteration mogelijk is voor
        bronnen die paginated zijn of grote volumes leveren.
        """
        ...

    def fetch_content(self, doc: Document) -> str:
        """Haal de feitelijke tekst-inhoud van een document op.

        Voor documenten die geen plain-text hebben (bv. PDF, DOCX) is het de
        verantwoordelijkheid van de adapter om de tekst te extraheren. Pipeline-
        code gaat ervan uit dat de teruggave bruikbaar is voor LLM-classificatie.
        """
        ...

    def list_findings(self, sessie_id: str) -> Iterator[Finding]:
        """Yield bevindingen uit de bron voor de gegeven audit-sessie.

        ``sessie_id`` is een door pipeline gegenereerde identifier voor de
        huidige audit-run; adapters mogen het gebruiken om sessie-specifieke
        bevindingen te scoping (bv. een Jira-label of Miro-bord-ID).
        """
        ...

    def healthcheck(self) -> dict[str, object]:
        """Retourneer status + bron-context.

        Vereiste keys:

        - ``status`` (``"ok"`` | ``"fail"`` | ``"degraded"``)
        - ``naam`` (overeenkomend met ``self.naam``)

        Aanbevolen keys: ``tenant`` (extern verifieerbare identifier zoals een
        Drive-folder-id of Jira-base-url) en bij ``status != "ok"`` een
        ``reden``-veld.
        """
        ...
