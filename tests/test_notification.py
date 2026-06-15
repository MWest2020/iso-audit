"""Tests voor `iso_audit.notification` — bevestiging-prompt en `gws`-aanroep."""

from __future__ import annotations

import json
from typing import Any
from unittest.mock import patch

import pytest

from iso_audit import notification


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Wis notification-env-vars zodat tests niet afhangen van shell-state."""
    monkeypatch.delenv("AUDIT_NOTIFICATIE_ONTVANGERS", raising=False)
    monkeypatch.delenv("AUDIT_CALENDAR_ID", raising=False)


# ---------- _bevestig ----------


@pytest.mark.parametrize(
    "antwoord, verwacht",
    [
        ("ja", True),
        ("j", True),
        ("yes", True),
        ("y", True),
        ("JA", True),
        ("  ja  ", True),
        ("nee", False),
        ("n", False),
        ("no", False),
        ("", False),
        ("misschien", False),
    ],
)
def test_bevestig_antwoorden(antwoord: str, verwacht: bool) -> None:
    with patch("builtins.input", return_value=antwoord):
        assert notification._bevestig("test", ["a@b"]) is verwacht


# ---------- stuur_calendar_uitnodiging ----------


def test_calendar_geen_deelnemers() -> None:
    """Lege deelnemers → None, geen subprocess-aanroep."""
    with patch.object(notification.subprocess, "run") as mock_run:
        result = notification.stuur_calendar_uitnodiging(
            "rapport-id", "slides-id", "9001", deelnemers=[]
        )
    assert result is None
    mock_run.assert_not_called()


def test_calendar_bevestiging_geweigerd() -> None:
    with (
        patch("builtins.input", return_value="nee"),
        patch.object(notification.subprocess, "run") as mock_run,
    ):
        result = notification.stuur_calendar_uitnodiging(
            "rapport-id", "slides-id", "9001", deelnemers=["a@b"]
        )
    assert result is None
    mock_run.assert_not_called()


def test_calendar_success() -> None:
    """Bevestigd → subprocess wordt aangeroepen, event-id geretourneerd."""
    fake_result = type("R", (), {"stdout": json.dumps({"id": "evt-42"}), "returncode": 0})()
    with (
        patch("builtins.input", return_value="ja"),
        patch.object(notification.subprocess, "run", return_value=fake_result) as mock_run,
    ):
        result = notification.stuur_calendar_uitnodiging(
            "rapport-id",
            "slides-id",
            "9001",
            deelnemers=["a@b", "c@d"],
            audit_datum="2026-06-01T09:30:00",
        )
    assert result == "evt-42"
    mock_run.assert_called_once()
    cmd: list[str] = mock_run.call_args[0][0]
    assert cmd[:3] == ["gws", "calendar", "+insert"]
    # Alle deelnemers als --attendee.
    assert cmd.count("--attendee") == 2


def test_calendar_norm_label_in_summary() -> None:
    """`norm`-mapping levert leesbare labels in de summary."""
    fake_result = type("R", (), {"stdout": json.dumps({"id": "e"}), "returncode": 0})()
    with (
        patch("builtins.input", return_value="ja"),
        patch.object(notification.subprocess, "run", return_value=fake_result) as mock_run,
    ):
        notification.stuur_calendar_uitnodiging("r", "s", "beide", deelnemers=["x@y"])
    cmd = mock_run.call_args[0][0]
    summary_idx = cmd.index("--summary") + 1
    assert "ISO 9001:2015 + ISO 27001:2022" in cmd[summary_idx]


# ---------- stuur_gmail_notificatie ----------


def test_gmail_geen_ontvangers() -> None:
    with patch.object(notification.subprocess, "run") as mock_run:
        result = notification.stuur_gmail_notificatie(
            "r", "s", "9001", bevindingen=[], ontvangers=[]
        )
    assert result is False
    mock_run.assert_not_called()


def test_gmail_env_ontvangers_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    """Geen ontvangers-arg → env-var wordt gebruikt."""
    monkeypatch.setenv("AUDIT_NOTIFICATIE_ONTVANGERS", "a@b, c@d")
    with (
        patch("builtins.input", return_value="ja"),
        patch.object(notification.subprocess, "run") as mock_run,
    ):
        result = notification.stuur_gmail_notificatie("r", "s", "9001", bevindingen=[])
    assert result is True
    assert mock_run.call_count == 2  # twee ontvangers → twee verzendingen


def test_gmail_bevestiging_geweigerd() -> None:
    with (
        patch("builtins.input", return_value="nee"),
        patch.object(notification.subprocess, "run") as mock_run,
    ):
        result = notification.stuur_gmail_notificatie(
            "r", "s", "9001", bevindingen=[], ontvangers=["a@b"]
        )
    assert result is False
    mock_run.assert_not_called()


def test_gmail_nc_ofi_count_in_body() -> None:
    """`bevindingen`-classificaties worden geteld in de body."""
    bevindingen: list[dict[str, Any]] = [
        {"classificatie": "NC"},
        {"classificatie": "NC"},
        {"classificatie": "OFI"},
        {"classificatie": "OFI"},
        {"classificatie": "OFI"},
        {"classificatie": "positief"},
    ]
    with (
        patch("builtins.input", return_value="ja"),
        patch.object(notification.subprocess, "run") as mock_run,
    ):
        notification.stuur_gmail_notificatie(
            "r", "s", "9001", bevindingen=bevindingen, ontvangers=["a@b"]
        )
    cmd = mock_run.call_args[0][0]
    body_idx = cmd.index("--body") + 1
    body = cmd[body_idx]
    assert "Non-conformiteiten (NC): 2" in body
    assert "Kansen voor verbetering (OFI): 3" in body
