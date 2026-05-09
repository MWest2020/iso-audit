"""Source-adapters: pluggable bronnen voor de audit-pipeline.

Concrete adapters (Drive, Planning, Jira, MCP, REST, …) leven in submodules
en registreren zichzelf via :func:`register` of de :func:`register` decorator.

Voorbeeld
---------

.. code-block:: python

    from iso_audit.sources import register, Source

    @register
    class DriveSource:
        naam = "drive"
        def list_documents(self, filter=None): ...
        def fetch_content(self, doc): ...
        def list_findings(self, sessie_id): ...
        def healthcheck(self): ...

    # Elders in de pipeline:
    from iso_audit.sources import get, available
    adapter = get("drive")
    print(available())  # ["drive"]
"""

from __future__ import annotations

from iso_audit.sources.base import Document, Finding, Source

__all__ = [
    "Document",
    "Finding",
    "Source",
    "available",
    "get",
    "register",
]


# Module-level registry. Bewust geen class — een registry is staat van het
# proces, en class-instantie-juggling voegt complexiteit toe zonder waarde.
_REGISTRY: dict[str, type[Source]] = {}


def register(adapter_class: type[Source]) -> type[Source]:
    """Registreer een Source-adapter class.

    Bruikbaar als decorator of als directe call. Het ``naam`` class-attribute van
    de adapter wordt gebruikt als registry-sleutel.

    :raises ValueError: bij dubbele registratie van dezelfde naam.
    :raises AttributeError: als ``adapter_class`` geen ``naam`` attribuut heeft.
    """
    naam = adapter_class.naam
    if not isinstance(naam, str) or not naam:
        msg = (
            f"Source-adapter {adapter_class!r} mist een geldige `naam`-attribute "
            "(class-level, lowercase, niet-leeg)."
        )
        raise AttributeError(msg)
    if naam in _REGISTRY:
        msg = (
            f"Source-adapter met naam {naam!r} is al geregistreerd "
            f"({_REGISTRY[naam]!r}). Een naam mag maar door één adapter worden gebruikt."
        )
        raise ValueError(msg)
    _REGISTRY[naam] = adapter_class
    return adapter_class


def available() -> list[str]:
    """Retourneer alle geregistreerde adapter-namen, gesorteerd."""
    return sorted(_REGISTRY)


def get(naam: str) -> type[Source]:
    """Geef de adapter-class terug die op ``naam`` is geregistreerd.

    :raises KeyError: met een leesbare lijst van beschikbare adapters wanneer
        ``naam`` niet bekend is.
    """
    try:
        return _REGISTRY[naam]
    except KeyError as exc:
        beschikbaar = ", ".join(available()) or "(geen)"
        msg = f"Source-adapter {naam!r} niet geregistreerd. Beschikbaar: {beschikbaar}"
        raise KeyError(msg) from exc


def _reset_for_tests() -> None:
    """Helper voor tests die met de registry willen rommelen.

    Niet onderdeel van de publieke API; tests importeren expliciet via dit
    underscore-prefix-mechanisme. Wordt nooit gebruikt door productie-code.
    """
    _REGISTRY.clear()
