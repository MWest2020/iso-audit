"""HTML → PDF converter via Chrome headless.

Chrome rendert de volledige CSS (grid, sticky TOC, conditional formatting)
snel en betrouwbaar. WeasyPrint (Python-native alternatief) bleek traag op
lange rapporten met complex grid-layout — Chrome headless is boring &
auditable.

Vereist: `google-chrome` of `chromium` in `PATH`.

Gemigreerd uit `Ops_to_Biz/audit/html_to_pdf.py` per milestone B §2.5.2.

Gebruik:
    python -m iso_audit.reporting.html_to_pdf <html_pad> [--output <pdf_pad>]
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess  # nosec B404 — Chrome headless aanroepen is de bedoelde flow
import sys
from pathlib import Path

CHROME_CANDIDATES = ("google-chrome", "chromium", "chrome")


def _vind_chrome() -> str:
    """Zoek Chrome/Chromium-binary in PATH; raise als ontbrekend."""
    for cmd in CHROME_CANDIDATES:
        pad = shutil.which(cmd)
        if pad:
            return pad
    raise FileNotFoundError("Geen Chrome/Chromium gevonden. Installeer google-chrome of chromium.")


def converteer(
    html_pad: str | os.PathLike[str],
    pdf_pad: str | os.PathLike[str] | None = None,
) -> str:
    """Render HTML naar PDF via Chrome headless.

    Retourneert het PDF-pad. Bij `pdf_pad=None` wordt het naast het HTML
    geschreven met `.pdf`-extensie.
    """
    html_path = Path(html_pad)
    if not html_path.is_file():
        raise FileNotFoundError(str(html_path))

    out_path = Path(pdf_pad) if pdf_pad is not None else html_path.with_suffix(".pdf")

    chrome = _vind_chrome()
    abs_html = html_path.resolve()
    abs_pdf = out_path.resolve()

    # Chrome-binary uit shutil.which, alle andere args zijn vaste vlaggen of
    # door de caller-aangeleverde paden; geen shell-injectie-risico.
    subprocess.run(  # nosec B603
        [
            chrome,
            "--headless=new",
            "--disable-gpu",
            "--no-sandbox",
            "--no-pdf-header-footer",
            f"--print-to-pdf={abs_pdf}",
            f"file://{abs_html}",
        ],
        check=True,
        capture_output=True,
        timeout=60,
    )
    return str(out_path)


def main() -> int:
    parser = argparse.ArgumentParser(description="HTML → PDF via Chrome headless")
    parser.add_argument("html_pad")
    parser.add_argument("--output", "-o", default=None)
    args = parser.parse_args()
    pad = converteer(args.html_pad, args.output)
    size_kb = os.path.getsize(pad) / 1024
    print(f"PDF geschreven: {pad} ({size_kb:.0f} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
