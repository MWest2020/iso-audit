"""Tests voor `iso_audit.modes.autonoom.AutonoomMode` (§3.1.4 + §3.1.6)."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

import pytest

from iso_audit import store
from iso_audit.modes.autonoom import AutonoomMode
from iso_audit.modes.base import Decision


def _decision(
    risico: str = "laag",
    punt: str = "classify_finding",
    voorstel: dict[str, Any] | None = None,
    context: dict[str, Any] | None = None,
) -> Decision:
    return Decision(
        punt=punt,
        context=context or {},
        voorstel=voorstel or {"klasse": "OFI"},
        risico=risico,  # type: ignore[arg-type]
        audit_id="audit-test-1",
    )


@pytest.fixture()
def conn(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> sqlite3.Connection:
    monkeypatch.setenv("AUDIT_DB_PATH", str(tmp_path / "audit.db"))
    c = store.verbinding()
    store.initialiseer(c)
    yield c
    c.close()


def _count_decisions(conn: sqlite3.Connection) -> int:
    return int(conn.execute("SELECT COUNT(*) FROM decisions").fetchone()[0])


# ---------- laag/midden — geen rij ----------


def test_laag_risico_geeft_voorstel_geen_rij(conn: sqlite3.Connection) -> None:
    mode = AutonoomMode(conn=conn)
    out = mode.beslis(_decision(risico="laag", voorstel={"klasse": "positief"}))
    assert out == {"klasse": "positief"}
    assert _count_decisions(conn) == 0


def test_midden_risico_geeft_voorstel_geen_rij(conn: sqlite3.Connection) -> None:
    mode = AutonoomMode(conn=conn)
    out = mode.beslis(_decision(risico="midden", voorstel={"klasse": "NC"}))
    assert out == {"klasse": "NC"}
    assert _count_decisions(conn) == 0


# ---------- hoog/delete_data ----------


def test_hoog_delete_data_geeft_skip(conn: sqlite3.Connection) -> None:
    mode = AutonoomMode(conn=conn)
    out = mode.beslis(_decision(risico="hoog", punt="delete_data"))
    assert out["actie"] == "skip"
    assert "autonoom" in str(out["reden"]).lower()
    # Rij gepersisteerd met status=resolved, notifier_naam=NULL.
    rows = conn.execute("SELECT status, notifier_naam FROM decisions").fetchall()
    assert len(rows) == 1
    assert rows[0]["status"] == "resolved"
    assert rows[0]["notifier_naam"] is None


# ---------- hoog/andere punten ----------


def test_hoog_send_report_accepteert_voorstel(conn: sqlite3.Connection) -> None:
    mode = AutonoomMode(conn=conn)
    voorstel = {"verzenden": True, "ontvangers": ["mt@conduction.nl"]}
    out = mode.beslis(_decision(risico="hoog", punt="send_report", voorstel=voorstel))
    assert out == voorstel
    rows = conn.execute("SELECT punt, status, besluit_json FROM decisions").fetchall()
    assert len(rows) == 1
    assert rows[0]["punt"] == "send_report"
    assert rows[0]["status"] == "resolved"
    # besluit_json bevat voorstel.
    import json

    assert json.loads(rows[0]["besluit_json"]) == voorstel


def test_hoog_generate_report_section_accepteert_voorstel(
    conn: sqlite3.Connection,
) -> None:
    mode = AutonoomMode(conn=conn)
    out = mode.beslis(
        _decision(risico="hoog", punt="generate_report_section", voorstel={"sectie": "MT"})
    )
    assert out == {"sectie": "MT"}
    assert _count_decisions(conn) == 1


# ---------- zonder conn ----------


def test_zonder_conn_werkt_maar_persisteert_niet() -> None:
    mode = AutonoomMode(conn=None)
    out = mode.beslis(_decision(risico="hoog", punt="send_report"))
    assert out == {"klasse": "OFI"}  # voorstel-default


# ---------- protocol-conformance ----------


def test_autonoom_implementeert_mode_protocol() -> None:
    from iso_audit.modes.base import Mode

    assert isinstance(AutonoomMode(), Mode)


def test_autonoom_heeft_naam_attribute() -> None:
    assert AutonoomMode.naam == "autonoom"
