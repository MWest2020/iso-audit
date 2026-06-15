"""Tests voor `iso_audit.sinks.drive.DriveSink` (§3.3.3)."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from iso_audit.sinks.base import (
    MirrorPayload,
    NotificationPayload,
    ReportPayload,
    Sink,
)


def _payload(titel: str = "Auditrapport 2026") -> ReportPayload:
    return ReportPayload(
        audit_id="audit-2026-q1",
        titel=titel,
        inhoud_html="<h1>Rapport</h1><p>Body</p>",
        bijlagen=["drive://abc"],
    )


# ---------- payload-type-narrowing ----------


def test_send_rejecteert_notification_payload(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from iso_audit.sinks.drive import DriveSink

    monkeypatch.setenv("AUDIT_DRIVE_FOLDER_ID", "folder-1")
    notif = NotificationPayload(titel="x", bericht="y", ontvangers=["a@b"])
    result = DriveSink().send(notif)
    assert result.succes is False
    assert "ReportPayload" in result.bericht


def test_send_rejecteert_mirror_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    from iso_audit.sinks.drive import DriveSink

    monkeypatch.setenv("AUDIT_DRIVE_FOLDER_ID", "folder-1")
    result = DriveSink().send(MirrorPayload())
    assert result.succes is False


# ---------- happy path ----------


def test_send_report_payload_genereert_doc_id(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from iso_audit.sinks.drive import DriveSink

    monkeypatch.setenv("AUDIT_DRIVE_FOLDER_ID", "folder-1")
    gws_responses = [{"id": "doc-1"}, {}]
    with patch("iso_audit.sinks.drive._gws", side_effect=gws_responses) as mock_gws:
        result = DriveSink().send(_payload())
    assert result.succes is True
    assert result.bron_id == "doc-1"
    assert mock_gws.call_count == 2
    # Eerste call moet drive/files/create zijn.
    assert mock_gws.call_args_list[0].args[:3] == ("drive", "files", "create")


def test_send_zonder_folder_id_faalt(monkeypatch: pytest.MonkeyPatch) -> None:
    from iso_audit.sinks.drive import DriveSink

    monkeypatch.delenv("AUDIT_DRIVE_FOLDER_ID", raising=False)
    result = DriveSink().send(_payload())
    assert result.succes is False
    assert "FOLDER_ID" in result.bericht


def test_send_gws_exception_wordt_sinkresult(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from iso_audit.sinks.drive import DriveSink

    monkeypatch.setenv("AUDIT_DRIVE_FOLDER_ID", "folder-1")
    with patch("iso_audit.sinks.drive._gws", side_effect=OSError("api 500")):
        result = DriveSink().send(_payload())
    assert result.succes is False
    assert "api 500" in result.bericht


# ---------- healthcheck ----------


def test_healthcheck_ok_met_folder_en_gws(monkeypatch: pytest.MonkeyPatch) -> None:
    from iso_audit.sinks import drive as drive_mod

    monkeypatch.setenv("AUDIT_DRIVE_FOLDER_ID", "f-1")
    with patch("iso_audit.sinks.drive.which", return_value="/usr/bin/gws"):
        h = drive_mod.DriveSink().healthcheck()
    assert h["status"] == "ok"


def test_healthcheck_fail_zonder_folder(monkeypatch: pytest.MonkeyPatch) -> None:
    from iso_audit.sinks.drive import DriveSink

    monkeypatch.delenv("AUDIT_DRIVE_FOLDER_ID", raising=False)
    h = DriveSink().healthcheck()
    assert h["status"] == "fail"


def test_healthcheck_fail_zonder_gws(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AUDIT_DRIVE_FOLDER_ID", "f-1")
    from iso_audit.sinks.drive import DriveSink

    with patch("iso_audit.sinks.drive.which", return_value=None):
        h = DriveSink().healthcheck()
    assert h["status"] == "fail"
    assert "gws" in str(h["reden"]).lower()


# ---------- HTML-naar-tekst ----------


def test_html_naar_tekst_strip_tags() -> None:
    from iso_audit.sinks.drive import _html_naar_tekst

    out = _html_naar_tekst("<h1>Titel</h1><p>Body &amp; meer</p>")
    assert "<h1>" not in out
    assert "Titel" in out
    assert "Body & meer" in out


# ---------- registry + protocol ----------


def test_drive_sink_implementeert_sink_protocol(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from iso_audit.sinks.drive import DriveSink

    monkeypatch.setenv("AUDIT_DRIVE_FOLDER_ID", "f-1")
    assert isinstance(DriveSink(), Sink)


def test_drive_sink_geregistreerd() -> None:
    import iso_audit.sinks.drive  # noqa: F401
    from iso_audit import sinks

    assert "drive" in sinks.available()
