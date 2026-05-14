"""Tests voor `iso_audit.reporting.html_to_docx`.

`htmldocx` is een zware afhankelijkheid (python-docx + BeautifulSoup); we
testen op het file-IO-niveau en mocken interne paden waar dat zinvol is.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from iso_audit.reporting import html_to_docx


def test_missing_input_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        html_to_docx.converteer(tmp_path / "bestaat-niet.html")


def test_default_output_naast_input(tmp_path: Path) -> None:
    """Zonder expliciete `docx_pad` → naast input met `.docx`-extensie."""
    html = tmp_path / "rapport.html"
    html.write_text("<html><body><h1>Titel</h1></body></html>", encoding="utf-8")

    fake_doc = MagicMock()
    with (
        patch.object(html_to_docx, "Document", return_value=fake_doc),
        patch.object(html_to_docx, "HtmlToDocx") as mock_htd,
    ):
        result = html_to_docx.converteer(html)
        instance = mock_htd.return_value
        instance.add_html_to_document.assert_called_once()
        # Eerste positionele arg moet de HTML-string zijn.
        args, _ = instance.add_html_to_document.call_args
        assert "<h1>Titel</h1>" in args[0]
        fake_doc.save.assert_called_once_with(str(tmp_path / "rapport.docx"))

    assert Path(result) == tmp_path / "rapport.docx"


def test_expliciet_output_pad(tmp_path: Path) -> None:
    html = tmp_path / "in.html"
    html.write_text("<p>x</p>", encoding="utf-8")
    out = tmp_path / "elders.docx"

    fake_doc = MagicMock()
    with (
        patch.object(html_to_docx, "Document", return_value=fake_doc),
        patch.object(html_to_docx, "HtmlToDocx"),
    ):
        result = html_to_docx.converteer(html, out)
        fake_doc.save.assert_called_once_with(str(out))
    assert Path(result) == out
