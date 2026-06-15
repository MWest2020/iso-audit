"""Interne client-modules voor externe systemen.

Onderscheid t.o.v. `iso_audit.sources` / `iso_audit.sinks`: de clients hier
zijn low-level HTTP/CLI-wrappers (één concrete dienst per module). De
Source/Sink-protocollen leven op `iso_audit.sources` / `iso_audit.sinks` en
*gebruiken* deze clients onder de motorkap.
"""

from __future__ import annotations
