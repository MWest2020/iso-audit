"""Sink-adapters: pluggable schrijf-paden voor de audit-pipeline.

Eerste implementatie: :class:`iso_audit.sinks.drive.DriveSink`. Het
registry-patroon is identiek aan ``iso_audit.sources`` en
``iso_audit.notifiers`` voor uitlegbaarheid aan externe code-reviewers.

Een nieuwe Sink toevoegen: zie ``ONBOARDING.md`` (sectie "Een adapter
toevoegen"). Kort: erf van :class:`~iso_audit.sinks.base.Sink`, geef een
class-level ``naam``-attribute, en decoreer met ``@register``.
"""

from __future__ import annotations

from iso_audit.sinks.base import (
    MirrorPayload,
    NotificationPayload,
    ReportPayload,
    Sink,
    SinkPayload,
    SinkResult,
)

__all__ = [
    "MirrorPayload",
    "NotificationPayload",
    "ReportPayload",
    "Sink",
    "SinkPayload",
    "SinkResult",
    "available",
    "get",
    "register",
]


_REGISTRY: dict[str, type[Sink]] = {}


def register(adapter_class: type[Sink]) -> type[Sink]:
    """Registreer een Sink-adapter class. Zie :func:`iso_audit.sources.register`."""
    naam = adapter_class.naam
    if not isinstance(naam, str) or not naam:
        msg = (
            f"Sink-adapter {adapter_class!r} mist een geldige `naam`-attribute "
            "(class-level, lowercase, niet-leeg)."
        )
        raise AttributeError(msg)
    if naam in _REGISTRY:
        msg = f"Sink-adapter met naam {naam!r} is al geregistreerd ({_REGISTRY[naam]!r})."
        raise ValueError(msg)
    _REGISTRY[naam] = adapter_class
    return adapter_class


def available() -> list[str]:
    """Retourneer alle geregistreerde adapter-namen, gesorteerd."""
    return sorted(_REGISTRY)


def get(naam: str) -> type[Sink]:
    """Geef de adapter-class terug die op ``naam`` is geregistreerd."""
    try:
        return _REGISTRY[naam]
    except KeyError as exc:
        beschikbaar = ", ".join(available()) or "(geen)"
        msg = f"Sink-adapter {naam!r} niet geregistreerd. Beschikbaar: {beschikbaar}"
        raise KeyError(msg) from exc


def _reset_for_tests() -> None:
    """Helper voor tests; niet onderdeel van publieke API."""
    _REGISTRY.clear()
