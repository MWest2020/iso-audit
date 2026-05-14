"""Contract-tests voor het Source Protocol.

Doel: één set invarianten die elke geregistreerde adapter MOET halen voordat
hij mergeable is. De tests zijn parametrized over alle in
:mod:`iso_audit.sources` geregistreerde adapters; in milestone A is die set
leeg, dus de parametrized tests draaien leeg-groen. Zodra DriveSource in
milestone B wordt geregistreerd, draait dezelfde test-set automatisch tegen
hem; de adapter is pas mergeable als alle assertions slagen.

Buiten de parametrize: drie statische tests die het Protocol zelf en de
registry-mechaniek valideren — die draaien wel meteen.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import pytest

from iso_audit import sources
from iso_audit.sources.base import Document, Finding, Source

# --- Statische tests op Protocol + Registry (lopen ongeacht registry-inhoud) ---


def test_source_protocol_is_runtime_checkable() -> None:
    """Source moet runtime_checkable zijn zodat ``isinstance(adapter(), Source)``
    werkt voor diagnostiek en het ``iso-audit doctor``-subcommand."""

    class _StubSource:
        naam = "stub"

        def list_documents(self, filter: dict[str, object] | None = None) -> Iterator[Document]:
            yield from ()

        def fetch_content(self, doc: Document) -> str:
            return ""

        def list_findings(self, sessie_id: str) -> Iterator[Finding]:
            yield from ()

        def healthcheck(self) -> dict[str, object]:
            return {"status": "ok", "naam": self.naam}

    assert isinstance(_StubSource(), Source)


def test_register_adds_to_registry(lege_registries: None) -> None:
    """De ``@register`` decorator moet de adapter onder ``naam`` registreren."""

    @sources.register
    class _A:
        naam = "alpha"

        def list_documents(self, filter: Any = None) -> Iterator[Document]:
            yield from ()

        def fetch_content(self, doc: Document) -> str:
            return ""

        def list_findings(self, sessie_id: str) -> Iterator[Finding]:
            yield from ()

        def healthcheck(self) -> dict[str, object]:
            return {"status": "ok", "naam": self.naam}

    assert "alpha" in sources.available()
    assert sources.get("alpha") is _A


def test_register_rejects_duplicate_name(lege_registries: None) -> None:
    """Twee adapters met dezelfde ``naam`` is een programmatie-fout, geen
    silent-overschrijving."""

    @sources.register
    class _First:
        naam = "duplicate"

        def list_documents(self, filter: Any = None) -> Iterator[Document]:
            yield from ()

        def fetch_content(self, doc: Document) -> str:
            return ""

        def list_findings(self, sessie_id: str) -> Iterator[Finding]:
            yield from ()

        def healthcheck(self) -> dict[str, object]:
            return {"status": "ok", "naam": self.naam}

    with pytest.raises(ValueError, match="duplicate"):

        @sources.register
        class _Second:
            naam = "duplicate"

            def list_documents(self, filter: Any = None) -> Iterator[Document]:
                yield from ()

            def fetch_content(self, doc: Document) -> str:
                return ""

            def list_findings(self, sessie_id: str) -> Iterator[Finding]:
                yield from ()

            def healthcheck(self) -> dict[str, object]:
                return {"status": "ok", "naam": self.naam}

    # Eerste registratie blijft actief.
    assert sources.get("duplicate") is _First


def test_get_unknown_source_raises_with_helpful_message(
    lege_registries: None,
) -> None:
    """Onbekende naam moet een helpful error-message geven met de beschikbare
    adapters — dat is wat de CLI ook aan de gebruiker toont."""
    with pytest.raises(KeyError, match="niet geregistreerd"):
        sources.get("non-existent")


def test_register_rejects_missing_naam(lege_registries: None) -> None:
    """Adapter zonder ``naam`` class-attribute is een hard programmatie-fout."""

    class _NoName:
        # `naam` ontbreekt - mypy zou dit normaal vangen, maar runtime-check is
        # verdediging in de diepte.
        def list_documents(self, filter: Any = None) -> Iterator[Document]:
            yield from ()

        def fetch_content(self, doc: Document) -> str:
            return ""

        def list_findings(self, sessie_id: str) -> Iterator[Finding]:
            yield from ()

        def healthcheck(self) -> dict[str, object]:
            return {"status": "ok"}

    with pytest.raises(AttributeError):
        sources.register(_NoName)  # type: ignore[arg-type]


# --- Parametrized contract-tests over alle geregistreerde adapters ---


def _registered_adapters() -> list[tuple[str, type[Source]]]:
    """Lijst van (naam, class) tupels. In milestone A leeg → tests skippen."""
    return [(naam, sources.get(naam)) for naam in sources.available()]


@pytest.mark.contract
@pytest.mark.parametrize(
    ("naam", "adapter_class"),
    _registered_adapters(),
    ids=lambda p: p if isinstance(p, str) else "",
)
def test_adapter_naam_matches_registry_key(naam: str, adapter_class: type[Source]) -> None:
    """De ``naam`` op de class moet overeenkomen met de registry-sleutel.
    Zonder deze invariant kan ``get(naam)`` een andere adapter teruggeven dan
    je verwachtte."""
    assert adapter_class.naam == naam


@pytest.mark.contract
@pytest.mark.parametrize(
    ("naam", "adapter_class"),
    _registered_adapters(),
    ids=lambda p: p if isinstance(p, str) else "",
)
def test_adapter_implements_protocol_runtime(naam: str, adapter_class: type[Source]) -> None:
    """De adapter-class moet voldoen aan het Source Protocol (runtime-check).
    mypy ``--strict`` zou dit vangen, maar we hebben de runtime-validatie als
    extra net voor adapters die via plugins of dynamische import komen."""
    # We instantiëren niet — adapters mogen externe credentials nodig hebben in
    # __init__. Class-level Protocol-check via duck-typing volstaat.
    assert hasattr(adapter_class, "naam")
    assert callable(getattr(adapter_class, "list_documents", None))
    assert callable(getattr(adapter_class, "fetch_content", None))
    assert callable(getattr(adapter_class, "list_findings", None))
    assert callable(getattr(adapter_class, "healthcheck", None))


@pytest.mark.contract
def test_registry_bevat_minstens_drive() -> None:
    """Vanaf milestone B §2.3.2 is `DriveSource` als basis-adapter geregistreerd.

    Vervangt de oude milestone-A-test (lege registry); auto-discovery van
    adapters via module-import is een werkende invariant van het systeem.
    """
    assert "drive" in sources.available()
