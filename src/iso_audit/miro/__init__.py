"""Miro-API-laag voor iso-audit (READ-only).

- `client.py` — gedeelde HTTP-laag (headers, retry, rate-limit).
- `ingest.py` — `haal_notities_op` + `koppel_aan_clausules` voor het
  uitlezen van auditor-sticky-notes naar bevindingen.

Het schrijf-pad (auto-aanmaak audit-bord, interview-bord) is per
`miro-write-trim` verwijderd; de auditor zet het bord zelf op via
Miro-AI of een template — zie `docs/miro-auditor-bord-prompt.md`.
"""

from __future__ import annotations

from iso_audit.miro.client import (
    MIRO_API_BASE,
    MIRO_API_TOKEN_ENV,
    MiroClient,
    MiroError,
    MiroRateLimitError,
)

__all__ = [
    "MIRO_API_BASE",
    "MIRO_API_TOKEN_ENV",
    "MiroClient",
    "MiroError",
    "MiroRateLimitError",
]
