"""Tests voor `iso_audit.reporting.md_to_html`."""

from __future__ import annotations

from pathlib import Path

import pytest

from iso_audit.reporting.md_to_html import converteer


def test_basis_conversie(tmp_path: Path) -> None:
    md = tmp_path / "rapport.md"
    md.write_text("# Titel\n\nEen alinea.\n", encoding="utf-8")
    html_pad = converteer(md)
    out = Path(html_pad)
    assert out.is_file()
    content = out.read_text(encoding="utf-8")
    assert "<title>rapport</title>" in content
    assert "<h1" in content
    assert "Een alinea." in content


def test_output_pad_optie(tmp_path: Path) -> None:
    md = tmp_path / "in.md"
    md.write_text("# X\n", encoding="utf-8")
    out_explicit = tmp_path / "out" / "anders.html"
    out_explicit.parent.mkdir()
    result = converteer(md, out_explicit)
    assert Path(result) == out_explicit
    assert out_explicit.is_file()


def test_toc_voor_meerdere_kopniveaus(tmp_path: Path) -> None:
    """`toc`-extensie genereert een navigatie als er meer kopniveaus zijn."""
    md = tmp_path / "rapport.md"
    md.write_text(
        "# H1\n\n## H2a\n\nblabla\n\n## H2b\n\n### H3\n\ntekst",
        encoding="utf-8",
    )
    html_pad = converteer(md)
    content = Path(html_pad).read_text(encoding="utf-8")
    assert '<nav class="toc">' in content
    assert "H2a" in content
    assert "H2b" in content


def test_tabel_extensie(tmp_path: Path) -> None:
    md = tmp_path / "rapport.md"
    md.write_text(
        "| Kop | Waarde |\n|---|---|\n| a | 1 |\n| b | 2 |\n",
        encoding="utf-8",
    )
    html_pad = converteer(md)
    content = Path(html_pad).read_text(encoding="utf-8")
    assert "<table" in content
    assert "<th>Kop</th>" in content
    assert "<td>a</td>" in content


def test_missing_input_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        converteer(tmp_path / "bestaat-niet.md")


def test_html_template_geldig(tmp_path: Path) -> None:
    """Output is valid-genoeg HTML5: <!DOCTYPE>, lang-attr, charset."""
    md = tmp_path / "r.md"
    md.write_text("# Iets", encoding="utf-8")
    content = Path(converteer(md)).read_text(encoding="utf-8")
    assert content.startswith("<!DOCTYPE html>")
    assert '<html lang="nl">' in content
    assert '<meta charset="utf-8">' in content
