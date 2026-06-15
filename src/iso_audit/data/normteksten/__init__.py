"""Normteksten voor ISO 9001:2015 en ISO 27001:2022.

Re-export-laag — laat callers ofwel
`from iso_audit.data.normteksten import NORMTEKSTEN_9001` (specifiek) of
`from iso_audit.data.normteksten import lookup` (generiek) gebruiken.
"""

from __future__ import annotations

from typing import Any

from iso_audit.data.normteksten.iso9001 import NORMTEKSTEN_9001
from iso_audit.data.normteksten.iso27001 import NORMTEKSTEN_27001

__all__ = ["NORMTEKSTEN_9001", "NORMTEKSTEN_27001", "available", "lookup"]


def lookup(norm: str, clausule: str) -> dict[str, Any] | None:
    """Vind een clausule-entry; `norm` is `'9001'` of `'27001'`.

    Retourneert `None` als de clausule niet bestaat — geen exception
    zodat callers expliciet kunnen kiezen tussen "skip" en "fail".
    """
    if norm == "9001":
        return NORMTEKSTEN_9001.get(clausule)
    if norm == "27001":
        return NORMTEKSTEN_27001.get(clausule)
    raise ValueError(f"onbekende norm: {norm!r} (verwacht '9001' of '27001')")


def available(norm: str) -> list[str]:
    """Lijst alle bekende clausule-keys voor een norm; gesorteerd."""
    if norm == "9001":
        return sorted(NORMTEKSTEN_9001)
    if norm == "27001":
        return sorted(NORMTEKSTEN_27001)
    raise ValueError(f"onbekende norm: {norm!r} (verwacht '9001' of '27001')")
