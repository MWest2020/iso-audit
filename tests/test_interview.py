"""Tests voor `iso_audit.interview` — interactieve doorloop."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

from iso_audit import interview

# ---------- _kleur (ANSI) ----------


def test_kleur_zonder_tty_geeft_plain_terug(monkeypatch: pytest.MonkeyPatch) -> None:
    """Niet-tty stdout krijgt geen ANSI-codes."""
    monkeypatch.setattr("sys.stdout.isatty", lambda: False)
    assert interview._kleur("hallo", "31") == "hallo"


def test_kleur_met_tty_wraps_ansi(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("sys.stdout.isatty", lambda: True)
    out = interview._kleur("hallo", "31")
    assert out.startswith("\033[31m")
    assert out.endswith("\033[0m")
    assert "hallo" in out


# ---------- _vraag_bevinding ----------


def test_vraag_bevinding_ja(monkeypatch: pytest.MonkeyPatch) -> None:
    inputs = iter(["j", "notitie hier"])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(inputs))
    bev, antw, notitie = interview._vraag_bevinding("4.1", "Context", "9001", None)
    assert bev == "positief"
    assert antw == "j"
    assert notitie == "notitie hier"


def test_vraag_bevinding_nc(monkeypatch: pytest.MonkeyPatch) -> None:
    inputs = iter(["n", ""])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(inputs))
    bev, _antw, notitie = interview._vraag_bevinding("5.11", "Activa", "27001", None)
    assert bev == "NC"
    assert notitie is None


def test_vraag_bevinding_skip(monkeypatch: pytest.MonkeyPatch) -> None:
    inputs = iter(["s"])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(inputs))
    bev, _antw, _notitie = interview._vraag_bevinding("4.1", "Context", "9001", None)
    assert bev == "overgeslagen"


def test_vraag_bevinding_quit(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("builtins.input", lambda _prompt: "q")
    with pytest.raises(KeyboardInterrupt):
        interview._vraag_bevinding("4.1", "Context", "9001", None)


def test_vraag_bevinding_eof_op_keuze(monkeypatch: pytest.MonkeyPatch) -> None:
    def _raise(_prompt: str) -> str:
        raise EOFError

    monkeypatch.setattr("builtins.input", _raise)
    with pytest.raises(KeyboardInterrupt):
        interview._vraag_bevinding("4.1", "Context", "9001", None)


def test_vraag_bevinding_onbekende_keuze_retries(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Een ongeldige keuze laat de vraag herhalen tot een geldige binnenkomt."""
    inputs = iter(["xx", "n", ""])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(inputs))
    bev, _antw, _notitie = interview._vraag_bevinding("4.1", "Context", "9001", None)
    assert bev == "NC"
    captured = capsys.readouterr()
    assert "Onbekende keuze" in captured.out


# ---------- _haal_gaps_op + _haal_alle_clausules_op ----------


def _setup_db(tmp_path: Path) -> sqlite3.Connection:
    """Maak een minimale DB met een clause_matches-tabel."""
    pad = tmp_path / "audit.db"
    conn = sqlite3.connect(str(pad))
    conn.row_factory = sqlite3.Row
    conn.executescript(
        """
        CREATE TABLE clause_matches (
            doc_id TEXT, herkomst TEXT, clausule_id TEXT, norm TEXT,
            sub_punt_id TEXT
        );
        INSERT INTO clause_matches (doc_id, herkomst, clausule_id, norm)
            VALUES ('d1', 'Drive', '4.1', '9001');
        """
    )
    conn.commit()
    return conn


@pytest.fixture()
def conn(tmp_path: Path) -> sqlite3.Connection:
    return _setup_db(tmp_path)


def test_haal_gaps_op_filtert_matched(
    conn: sqlite3.Connection, monkeypatch: pytest.MonkeyPatch
) -> None:
    fake_map = {
        "norm": "ISO 9001",
        "clausules": {
            "4.1": {"titel": "Context"},
            "5.1": {"titel": "Leiderschap"},
        },
    }
    with patch(
        "iso_audit.classification.clause_mapping.laad_clause_map",
        return_value=fake_map,
    ):
        gaps = interview._haal_gaps_op(conn, "9001")
    cids = [g["clausule_id"] for g in gaps]
    assert "4.1" not in cids
    assert "5.1" in cids


def test_haal_alle_clausules_op(conn: sqlite3.Connection, monkeypatch: pytest.MonkeyPatch) -> None:
    fake_map = {
        "norm": "ISO 9001",
        "clausules": {
            "4.1": {"titel": "Context"},
            "5.1": {"titel": "Leiderschap"},
        },
    }
    with patch(
        "iso_audit.classification.clause_mapping.laad_clause_map",
        return_value=fake_map,
    ):
        out = interview._haal_alle_clausules_op(conn, "9001")
    assert [c["clausule_id"] for c in out] == ["4.1", "5.1"]


# ---------- run_interview (integratie, gemockte I/O) ----------


def test_run_interview_geen_gaps(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Lege gap-set → vroeg afsluiten."""
    monkeypatch.setenv("AUDIT_DB_PATH", str(tmp_path / "audit.db"))
    fake_map = {"norm": "ISO 9001", "clausules": {}}
    with patch(
        "iso_audit.classification.clause_mapping.laad_clause_map",
        return_value=fake_map,
    ):
        interview.run_interview("9001", alle=False)
    captured = capsys.readouterr()
    assert "Geen gaps" in captured.out


def test_run_interview_alle_beantwoord(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Alle gaps al beantwoord en geen --herinterviewen → afsluiten."""
    db = tmp_path / "audit.db"
    monkeypatch.setenv("AUDIT_DB_PATH", str(db))
    conn = sqlite3.connect(str(db))
    conn.row_factory = sqlite3.Row
    # Bare-bones schema: laat initialiseer() de echte tabellen maken.
    conn.close()

    fake_map = {
        "norm": "ISO 9001",
        "clausules": {"5.1": {"titel": "Leiderschap"}},
    }
    fake_interview_row: dict[str, Any] = {
        "clausule_id": "5.1",
        "norm": "9001",
        "bevinding": "positief",
    }

    def _laad_interviews(conn: sqlite3.Connection) -> list[dict[str, Any]]:
        return [fake_interview_row]

    with (
        patch(
            "iso_audit.classification.clause_mapping.laad_clause_map",
            return_value=fake_map,
        ),
        patch("iso_audit.store.laad_interviews", side_effect=_laad_interviews),
    ):
        interview.run_interview("9001", alle=False, herinterviewen=False)

    captured = capsys.readouterr()
    assert "al beantwoord" in captured.out


# ---------- main ----------


def test_main_passes_args() -> None:
    with patch.object(interview, "run_interview") as mock_run:
        interview.main(["--norm", "9001", "--alle"])
    mock_run.assert_called_once_with("9001", alle=True, herinterviewen=False)


def test_main_default_norm_beide() -> None:
    with patch.object(interview, "run_interview") as mock_run:
        interview.main([])
    # Default uit env of "beide".
    args = mock_run.call_args.args
    assert args[0] in ("9001", "27001", "beide")
