"""PDF-rendering via WeasyPrint.

Gescheiden module omdat WeasyPrint zware systeem-libs (pango/cairo) vereist;
zo blijft de rest van de memo-package importeerbaar zonder die afhankelijkheid.
"""

from __future__ import annotations

from pathlib import Path


def schrijf_pdf(html: str, output: Path | str) -> None:
    """Schrijf een (self-contained) HTML-string naar een PDF-bestand."""
    from weasyprint import HTML

    pad = Path(output)
    pad.parent.mkdir(parents=True, exist_ok=True)
    HTML(string=html).write_pdf(str(pad))
