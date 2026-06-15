"""Tests voor `iso_audit.verify_docs` — pure helpers + integratie met DB."""

from __future__ import annotations

import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

from iso_audit import store, verify_docs

# ---------- _parse_drive_datum ----------


def test_parse_drive_datum_iso_z() -> None:
    dt = verify_docs._parse_drive_datum("2026-01-01T12:00:00Z")
    assert dt == datetime(2026, 1, 1, 12, 0, 0, tzinfo=UTC)


def test_parse_drive_datum_zonder_tz() -> None:
    """Datum zonder tz wordt UTC."""
    dt = verify_docs._parse_drive_datum("2026-01-01T12:00:00")
    assert dt is not None
    assert dt.tzinfo == UTC


def test_parse_drive_datum_invalid() -> None:
    assert verify_docs._parse_drive_datum("niet-een-datum") is None


def test_parse_drive_datum_none() -> None:
    assert verify_docs._parse_drive_datum(None) is None
    assert verify_docs._parse_drive_datum("") is None


# ---------- _metadata ----------


def test_metadata_succes() -> None:
    payload = {"id": "x", "name": "n", "modifiedTime": "2026-01-01T00:00:00Z"}
    with patch.object(verify_docs, "_gws", return_value=payload):
        assert verify_docs._metadata("x") == payload


def test_metadata_404_stderr() -> None:
    err = subprocess.CalledProcessError(
        returncode=1, cmd=["gws"], output="", stderr="HTTP 404 notFound"
    )
    with patch.object(verify_docs, "_gws", side_effect=err):
        assert verify_docs._metadata("x") is None


def test_metadata_403_stderr() -> None:
    err = subprocess.CalledProcessError(
        returncode=1, cmd=["gws"], output="", stderr="403 Forbidden"
    )
    with patch.object(verify_docs, "_gws", side_effect=err):
        assert verify_docs._metadata("x") is None


def test_metadata_overige_fout_geeft_lege_dict() -> None:
    err = subprocess.CalledProcessError(
        returncode=1, cmd=["gws"], output="", stderr="500 something"
    )
    with patch.object(verify_docs, "_gws", side_effect=err):
        assert verify_docs._metadata("x") == {}


def test_metadata_error_payload_404() -> None:
    """gws-response met `error.code=404` → None."""
    with patch.object(verify_docs, "_gws", return_value={"error": {"code": 404}}):
        assert verify_docs._metadata("x") is None


# ---------- run (integratie) ----------


@pytest.fixture
def db_pad(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> str:
    pad = tmp_path / "audit.db"
    monkeypatch.setenv("AUDIT_DB_PATH", str(pad))
    conn = store.verbinding(str(pad))
    store.initialiseer(conn)
    conn.close()
    return str(pad)


def _seed(db_pad: str, doc_id: str, naam: str) -> None:
    conn = store.verbinding(db_pad)
    store.upsert_document(conn, {"id": doc_id, "naam": naam, "tekst": ""})
    conn.commit()
    conn.close()


def test_run_geen_documenten(db_pad: str) -> None:
    """Lege DB → vroege return, geen calls."""
    with patch.object(verify_docs, "_gws") as mock:
        verify_docs.run(opruimen=False)
    mock.assert_not_called()


def test_run_niet_gevonden_droog(
    db_pad: str, capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    _seed(db_pad, "d1", "Verloren Doc")
    with patch.object(verify_docs, "_metadata", return_value=None):
        verify_docs.run(opruimen=False, output_dir=tmp_path)
    out = capsys.readouterr().out
    assert "Niet meer beschikbaar" in out
    assert "Verloren Doc" in out
    # DB blijft intact.
    conn = store.verbinding(db_pad)
    count = conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
    conn.close()
    assert count == 1


def test_run_opruimen_verwijdert(db_pad: str, tmp_path: Path) -> None:
    _seed(db_pad, "d1", "Verloren Doc")
    with patch.object(verify_docs, "_metadata", return_value=None):
        verify_docs.run(opruimen=True, output_dir=tmp_path)
    conn = store.verbinding(db_pad)
    count = conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
    conn.close()
    assert count == 0


def test_run_trashed_telt_als_verwijderd(
    db_pad: str, capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    _seed(db_pad, "d1", "Trash Doc")
    meta = {"id": "d1", "trashed": True}
    with patch.object(verify_docs, "_metadata", return_value=meta):
        verify_docs.run(opruimen=False, output_dir=tmp_path)
    out = capsys.readouterr().out
    assert "Trash Doc" in out
    assert "Niet meer beschikbaar" in out


def test_run_verouderd_genereert_rapport(
    db_pad: str, capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    _seed(db_pad, "d1", "Oud Beleid")
    meta = {"id": "d1", "modifiedTime": "2022-01-01T00:00:00Z"}
    with patch.object(verify_docs, "_metadata", return_value=meta):
        verify_docs.run(opruimen=False, voor_jaar=2023, output_dir=tmp_path)
    out = capsys.readouterr().out
    assert "Verouderd" in out
    assert "2022-01-01" in out
    # MD-rapport in tmp_path.
    rapporten = list(tmp_path.glob("verouderde_documenten_*.md"))
    assert len(rapporten) == 1
    content = rapporten[0].read_text(encoding="utf-8")
    assert "Oud Beleid" in content


def test_run_recente_doc_niet_verouderd(
    db_pad: str, capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    _seed(db_pad, "d1", "Nieuw Beleid")
    meta = {"id": "d1", "modifiedTime": "2026-01-01T00:00:00Z"}
    with patch.object(verify_docs, "_metadata", return_value=meta):
        verify_docs.run(opruimen=False, voor_jaar=2023, output_dir=tmp_path)
    out = capsys.readouterr().out
    assert "Alle Drive-documenten nog bereikbaar" in out
    # Geen rapport in dit pad.
    assert list(tmp_path.glob("verouderde_documenten_*.md")) == []


# Pylance-fix.
_ = Any
