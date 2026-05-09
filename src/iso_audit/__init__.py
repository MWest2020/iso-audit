"""iso-audit — pluggable ISO 9001 + 27001 audit pipeline.

Drie protocol-lagen vormen de uitbreidbaarheid:

- ``iso_audit.sources``: pluggable bron-adapters (Drive, Planning, Jira, MCP, REST)
- ``iso_audit.sinks``: pluggable schrijf-adapters (rapport-publicatie, externe meldingen)
- ``iso_audit.notifiers``: pluggable handoff-kanalen voor integer-modus (Slack, Email)

Twee runmodes zijn ingebakken (``iso_audit.modes``): ``autonoom`` voor cron-/CI-runs,
``integer`` voor mens-in-de-lus op kritieke beslismomenten.

Zie ``ARCHITECTURE.md`` voor het volledige plaatje en ``docs/missie.md`` voor
de positionering van het tool ten opzichte van de auditor-rol.
"""

__version__ = "0.1.0a0"

__all__ = ["__version__"]
