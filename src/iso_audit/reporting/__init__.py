"""Reporting-laag voor iso-audit.

In milestone B:
- Format-converters (`md_to_html`, `html_to_docx`, `html_to_pdf`) — interne
  hulpmiddelen, géén Sink-implementatie.

In milestone C komen Sink-implementaties (DriveSink) die deze converters
gebruiken om uitvoer te publiceren.
"""

from __future__ import annotations
