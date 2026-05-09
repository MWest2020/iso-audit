"""Notifier-adapters: pluggable handoff-kanalen voor integer-modus.

Concrete adapters (Slack, Email, Teams, …) komen in milestone C of later via
eigen change-proposals. Het registry-patroon is identiek aan ``iso_audit.sources``
en ``iso_audit.sinks`` voor uitlegbaarheid.
"""

from __future__ import annotations

from iso_audit.notifiers.base import DecisionResolver, Notifier

__all__ = [
    "DecisionResolver",
    "Notifier",
    "available",
    "get",
    "register",
]


_REGISTRY: dict[str, type[Notifier]] = {}


def register(adapter_class: type[Notifier]) -> type[Notifier]:
    """Registreer een Notifier-adapter class. Zie :func:`iso_audit.sources.register`."""
    naam = adapter_class.naam
    if not isinstance(naam, str) or not naam:
        msg = (
            f"Notifier-adapter {adapter_class!r} mist een geldige `naam`-attribute "
            "(class-level, lowercase, niet-leeg)."
        )
        raise AttributeError(msg)
    if naam in _REGISTRY:
        msg = f"Notifier-adapter met naam {naam!r} is al geregistreerd ({_REGISTRY[naam]!r})."
        raise ValueError(msg)
    _REGISTRY[naam] = adapter_class
    return adapter_class


def available() -> list[str]:
    """Retourneer alle geregistreerde adapter-namen, gesorteerd."""
    return sorted(_REGISTRY)


def get(naam: str) -> type[Notifier]:
    """Geef de adapter-class terug die op ``naam`` is geregistreerd."""
    try:
        return _REGISTRY[naam]
    except KeyError as exc:
        beschikbaar = ", ".join(available()) or "(geen)"
        msg = f"Notifier-adapter {naam!r} niet geregistreerd. Beschikbaar: {beschikbaar}"
        raise KeyError(msg) from exc


def _reset_for_tests() -> None:
    """Helper voor tests; niet onderdeel van publieke API."""
    _REGISTRY.clear()
