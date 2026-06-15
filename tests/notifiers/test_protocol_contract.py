"""Contract-tests voor het Notifier Protocol.

Spiegelt :mod:`tests.sources.test_protocol_contract` voor de Notifier-laag.
Adapters worden in milestone C geregistreerd; tot die tijd valideert deze
file alleen de Protocol-shape, registry-mechaniek en DecisionResolver-
contract.
"""

from __future__ import annotations

import pytest

# Trigger import van bundled notifier-adapters zodat hun `@register`-decorator
# wordt geëvalueerd vóór `_registered_notifiers()` parametrize-tijd wordt
# aangeroepen — anders blijven de parametrized contract-tests leeg.
import iso_audit.notifiers.email
import iso_audit.notifiers.slack  # noqa: F401
from iso_audit import notifiers
from iso_audit.modes.base import Decision
from iso_audit.notifiers.base import DecisionResolver, Notifier

# --- Statische tests op Protocol + Registry ---


def test_notifier_protocol_is_runtime_checkable(sample_decision: Decision) -> None:
    """Notifier moet runtime_checkable zijn voor diagnostiek-doeleinden."""

    class _StubNotifier:
        naam = "stub"

        def vraag_besluit(self, decision: Decision) -> str:
            return f"stub-{decision.punt}"

        def healthcheck(self) -> dict[str, object]:
            return {"status": "ok", "naam": self.naam}

    assert isinstance(_StubNotifier(), Notifier)


def test_decision_resolver_protocol_is_runtime_checkable() -> None:
    """DecisionResolver moet eveneens runtime_checkable zijn."""

    class _StubResolver:
        def resolve(
            self,
            decision_id: str,
            action: str,
            modified_payload: dict[str, object] | None = None,
        ) -> None:
            return None

    assert isinstance(_StubResolver(), DecisionResolver)


def test_register_adds_to_registry(lege_registries: None) -> None:
    """De ``@register`` decorator moet de notifier onder ``naam`` registreren."""

    @notifiers.register
    class _SlackStub:
        naam = "slack-stub"

        def vraag_besluit(self, decision: Decision) -> str:
            return f"id-{decision.punt}"

        def healthcheck(self) -> dict[str, object]:
            return {"status": "ok", "naam": self.naam}

    assert "slack-stub" in notifiers.available()
    assert notifiers.get("slack-stub") is _SlackStub


def test_register_rejects_duplicate_name(lege_registries: None) -> None:
    """Twee notifiers met dezelfde naam is een programmatie-fout."""

    @notifiers.register
    class _First:
        naam = "duplicate"

        def vraag_besluit(self, decision: Decision) -> str:
            return "first"

        def healthcheck(self) -> dict[str, object]:
            return {"status": "ok", "naam": self.naam}

    with pytest.raises(ValueError, match="duplicate"):

        @notifiers.register
        class _Second:
            naam = "duplicate"

            def vraag_besluit(self, decision: Decision) -> str:
                return "second"

            def healthcheck(self) -> dict[str, object]:
                return {"status": "ok", "naam": self.naam}

    assert notifiers.get("duplicate") is _First


def test_get_unknown_notifier_raises_with_helpful_message(
    lege_registries: None,
) -> None:
    """Onbekende naam moet helpful error-message geven."""
    with pytest.raises(KeyError, match="niet geregistreerd"):
        notifiers.get("non-existent")


def test_register_rejects_missing_naam(lege_registries: None) -> None:
    """Notifier zonder ``naam`` class-attribute is een hard programmatie-fout."""

    class _NoName:
        def vraag_besluit(self, decision: Decision) -> str:
            return "x"

        def healthcheck(self) -> dict[str, object]:
            return {"status": "ok"}

    with pytest.raises(AttributeError):
        notifiers.register(_NoName)  # type: ignore[arg-type]


# --- Parametrized contract-tests ---


def _registered_notifiers() -> list[tuple[str, type[Notifier]]]:
    """Lijst van geregistreerde notifiers (leeg in milestone A)."""
    return [(naam, notifiers.get(naam)) for naam in notifiers.available()]


@pytest.mark.contract
@pytest.mark.parametrize(
    ("naam", "notifier_class"),
    _registered_notifiers(),
    ids=lambda p: p if isinstance(p, str) else "",
)
def test_notifier_naam_matches_registry_key(naam: str, notifier_class: type[Notifier]) -> None:
    """De ``naam`` op de class moet overeenkomen met de registry-sleutel."""
    assert notifier_class.naam == naam


@pytest.mark.contract
@pytest.mark.parametrize(
    ("naam", "notifier_class"),
    _registered_notifiers(),
    ids=lambda p: p if isinstance(p, str) else "",
)
def test_notifier_implements_protocol_runtime(naam: str, notifier_class: type[Notifier]) -> None:
    """Notifier-class moet de twee Protocol-methodes hebben."""
    assert hasattr(notifier_class, "naam")
    assert callable(getattr(notifier_class, "vraag_besluit", None))
    assert callable(getattr(notifier_class, "healthcheck", None))


@pytest.mark.contract
def test_registry_bevat_minstens_slack_en_email() -> None:
    """In milestone C zijn Slack + Email geregistreerd via `@register`."""
    # Trigger import zodat de decorators draaien (vergelijkbaar met sources).
    import iso_audit.notifiers.email
    import iso_audit.notifiers.slack  # noqa: F401

    beschikbaar = notifiers.available()
    assert "slack" in beschikbaar
    assert "email" in beschikbaar
