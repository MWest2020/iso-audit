"""HTML → DOCX converter voor auditrapporten via `htmldocx`.

`htmldocx` wrapt `python-docx` en mapt HTML-elementen (h1-h4, tables, links,
strong, em, blockquote) naar Word-stijlen. CSS-styling (kleur, grid layout,
sticky TOC) gaat verloren — wat overblijft: gestructureerd Word-document
met werkende koppen, tabellen en hyperlinks.

Gemigreerd uit `Ops_to_Biz/audit/html_to_docx.py` per milestone B §2.5.2.

Gebruik:
    python -m iso_audit.reporting.html_to_docx <html_pad> [--output <docx_pad>]
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Any

from docx import Document
from htmldocx import HtmlToDocx


def converteer(
    html_pad: str | os.PathLike[str],
    docx_pad: str | os.PathLike[str] | None = None,
) -> str:
    """Lees HTML van `html_pad`, schrijf DOCX naar `docx_pad`.

    Retourneert het uiteindelijke DOCX-pad. Als `docx_pad` niet is opgegeven
    wordt het naast het HTML-bestand geschreven met dezelfde naam.
    """
    html_path = Path(html_pad)
    if not html_path.is_file():
        raise FileNotFoundError(str(html_path))

    out_path = Path(docx_pad) if docx_pad is not None else html_path.with_suffix(".docx")
    html = html_path.read_text(encoding="utf-8")

    doc: Any = Document()
    HtmlToDocx().add_html_to_document(html, doc)
    doc.save(str(out_path))
    return str(out_path)


def main() -> int:
    parser = argparse.ArgumentParser(description="HTML → DOCX via htmldocx")
    parser.add_argument("html_pad")
    parser.add_argument("--output", "-o", default=None)
    args = parser.parse_args()
    pad = converteer(args.html_pad, args.output)
    size_kb = os.path.getsize(pad) / 1024
    print(f"DOCX geschreven: {pad} ({size_kb:.0f} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
