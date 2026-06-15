"""Tests voor `iso_audit.reporting.html_to_pdf`."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from iso_audit.reporting import html_to_pdf


def test_vind_chrome_geen_binary(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(html_to_pdf.shutil, "which", lambda _cmd: None)
    with pytest.raises(FileNotFoundError, match="Chrome/Chromium"):
        html_to_pdf._vind_chrome()


def test_vind_chrome_eerste_match(monkeypatch: pytest.MonkeyPatch) -> None:
    """Eerste van CHROME_CANDIDATES die `which` resolved → die wordt teruggegeven."""
    calls: list[str] = []

    def fake_which(cmd: str) -> str | None:
        calls.append(cmd)
        return "/usr/bin/google-chrome" if cmd == "google-chrome" else None

    monkeypatch.setattr(html_to_pdf.shutil, "which", fake_which)
    assert html_to_pdf._vind_chrome() == "/usr/bin/google-chrome"
    assert calls[0] == "google-chrome"


def test_vind_chrome_chromium_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_which(cmd: str) -> str | None:
        return "/usr/bin/chromium" if cmd == "chromium" else None

    monkeypatch.setattr(html_to_pdf.shutil, "which", fake_which)
    assert html_to_pdf._vind_chrome() == "/usr/bin/chromium"


def test_missing_input_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        html_to_pdf.converteer(tmp_path / "niets.html")


def test_converteer_default_output(tmp_path: Path) -> None:
    html = tmp_path / "rapport.html"
    html.write_text("<html></html>", encoding="utf-8")
    with (
        patch.object(html_to_pdf, "_vind_chrome", return_value="/usr/bin/chrome"),
        patch.object(html_to_pdf.subprocess, "run") as mock_run,
    ):
        result = html_to_pdf.converteer(html)
    assert Path(result) == tmp_path / "rapport.pdf"
    mock_run.assert_called_once()
    cmd = mock_run.call_args.args[0]
    assert cmd[0] == "/usr/bin/chrome"
    assert "--headless=new" in cmd
    # Output-arg moet absolute pad zijn.
    print_to_pdf_arg = next(c for c in cmd if c.startswith("--print-to-pdf="))
    assert print_to_pdf_arg == f"--print-to-pdf={(tmp_path / 'rapport.pdf').resolve()}"


def test_converteer_expliciete_output(tmp_path: Path) -> None:
    html = tmp_path / "in.html"
    html.write_text("<html></html>", encoding="utf-8")
    out = tmp_path / "out" / "elders.pdf"
    out.parent.mkdir()
    with (
        patch.object(html_to_pdf, "_vind_chrome", return_value="/usr/bin/chrome"),
        patch.object(html_to_pdf.subprocess, "run"),
    ):
        result = html_to_pdf.converteer(html, out)
    assert Path(result) == out


def test_converteer_timeout_60(tmp_path: Path) -> None:
    """Chrome-aanroep moet `timeout=60` meegeven om hangende processen af te kappen."""
    html = tmp_path / "x.html"
    html.write_text("<html></html>", encoding="utf-8")
    with (
        patch.object(html_to_pdf, "_vind_chrome", return_value="/usr/bin/chrome"),
        patch.object(html_to_pdf.subprocess, "run") as mock_run,
    ):
        html_to_pdf.converteer(html)
    assert mock_run.call_args.kwargs["timeout"] == 60
    assert mock_run.call_args.kwargs["check"] is True
