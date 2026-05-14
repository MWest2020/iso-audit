"""Tests voor `iso_audit.modes.integer.IntegerMode` (§3.1.5 + §3.1.6)."""

from __future__ import annotations

import sqlite3
import threading
import time
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest

from iso_audit import store
from iso_audit.modes.base import Decision
from iso_audit.modes.integer import IntegerMode


def _decision(
    risico: str = "hoog",
    punt: str = "send_report",
    voorstel: dict[str, Any] | None = None,
    context: dict[str, Any] | None = None,
) -> Decision:
    return Decision(
        punt=punt,
        context=context or {},
        voorstel=voorstel or {"verzenden": True},
        risico=risico,  # type: ignore[arg-type]
        audit_id="audit-test-1",
    )


def _fake_notifier(naam: str = "slack") -> MagicMock:
    m = MagicMock()
    m.naam = naam
    m.vraag_besluit = MagicMock(return_value="correlation-1")
    return m


@pytest.fixture()
def conn(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> sqlite3.Connection:
    monkeypatch.setenv("AUDIT_DB_PATH", str(tmp_path / "audit.db"))
    c = store.verbinding()
    store.initialiseer(c)
    yield c
    c.close()


# ---------- laag/midden zonder escalatie ----------


def test_laag_risico_geeft_voorstel_geen_notifier_call(
    conn: sqlite3.Connection,
) -> None:
    notif = _fake_notifier()
    mode = IntegerMode(notifier=notif, conn=conn)
    out = mode.beslis(_decision(risico="laag", voorstel={"k": "v"}))
    assert out == {"k": "v"}
    notif.vraag_besluit.assert_not_called()
    assert conn.execute("SELECT COUNT(*) FROM decisions").fetchone()[0] == 0


def test_midden_risico_hoge_confidence_geen_escalatie(
    conn: sqlite3.Connection,
) -> None:
    notif = _fake_notifier()
    mode = IntegerMode(notifier=notif, conn=conn)
    out = mode.beslis(
        _decision(
            risico="midden",
            punt="classify_finding",
            context={"confidence": 0.95},
            voorstel={"klasse": "OFI"},
        )
    )
    assert out == {"klasse": "OFI"}
    notif.vraag_besluit.assert_not_called()


# ---------- midden + low-confidence: escalatie ----------


def test_midden_risico_lage_confidence_escaleert(conn: sqlite3.Connection) -> None:
    notif = _fake_notifier()
    mode = IntegerMode(notifier=notif, conn=conn, poll_interval_s=0.01)
    decision = _decision(
        risico="midden",
        punt="classify_finding",
        context={"confidence": 0.55},
        voorstel={"klasse": "OFI"},
    )
    # Resolver mockt door zelf direct de rij te updaten in een achtergrond-thread.
    _resolve_op_thread(conn, besluit={"klasse": "NC"}, na_seconden=0.05)
    out = mode.beslis(decision)
    assert out == {"klasse": "NC"}
    # IntegerMode injecteert `decision_id` in context vóór de notifier-call,
    # dus exact-match werkt niet; check oorspronkelijke velden.
    assert notif.vraag_besluit.call_count == 1
    actual = notif.vraag_besluit.call_args.args[0]
    assert actual.punt == decision.punt
    assert actual.risico == decision.risico
    assert "decision_id" in actual.context


# ---------- vraag_bevestiging flag op laag-risico ----------


def test_laag_risico_met_vraag_bevestiging_escaleert(
    conn: sqlite3.Connection,
) -> None:
    notif = _fake_notifier()
    mode = IntegerMode(notifier=notif, conn=conn, poll_interval_s=0.01)
    decision = _decision(
        risico="laag",
        punt="ingest_scope",
        context={"vraag_bevestiging": True, "sources": ["drive"]},
    )
    _resolve_op_thread(conn, besluit={"ok": True}, na_seconden=0.05)
    out = mode.beslis(decision)
    assert out == {"ok": True}
    notif.vraag_besluit.assert_called_once()


# ---------- hoog risico altijd escalatie ----------


def test_hoog_risico_send_report_escaleert(conn: sqlite3.Connection) -> None:
    notif = _fake_notifier()
    mode = IntegerMode(notifier=notif, conn=conn, poll_interval_s=0.01)
    decision = _decision(risico="hoog", punt="send_report")
    _resolve_op_thread(conn, besluit={"verzenden": False}, na_seconden=0.05)
    out = mode.beslis(decision)
    assert out == {"verzenden": False}
    # Rij is gepersisteerd met juiste velden.
    row = conn.execute("SELECT punt, status, notifier_naam, risico FROM decisions").fetchone()
    assert row["punt"] == "send_report"
    assert row["status"] == "resolved"
    assert row["notifier_naam"] == "slack"
    assert row["risico"] == "hoog"


def test_pending_rij_geschreven_met_notifier_naam(conn: sqlite3.Connection) -> None:
    """Bij escalatie schrijft IntegerMode eerst de pending-rij vóór notifier-call."""
    notif = _fake_notifier(naam="email")

    seen: dict[str, Any] = {}

    def _capture(_decision: Decision) -> str:
        seen["count"] = conn.execute("SELECT COUNT(*) FROM decisions").fetchone()[0]
        seen["status"] = conn.execute("SELECT status FROM decisions").fetchone()[0]
        return "corr-1"

    notif.vraag_besluit.side_effect = _capture
    mode = IntegerMode(notifier=notif, conn=conn, poll_interval_s=0.01)
    _resolve_op_thread(conn, besluit={"ok": True}, na_seconden=0.05)
    mode.beslis(_decision(risico="hoog"))
    assert seen["count"] == 1
    assert seen["status"] == "pending"


# ---------- cancelled status ----------


def test_cancelled_status_geeft_skip(conn: sqlite3.Connection) -> None:
    """Een gecancelde decision retourneert `actie=skip`."""
    notif = _fake_notifier()
    mode = IntegerMode(notifier=notif, conn=conn, poll_interval_s=0.01)
    pad = conn.execute("PRAGMA database_list").fetchone()["file"]

    def _cancel_in_thread() -> None:
        time.sleep(0.05)
        own = store.verbinding(pad)
        try:
            row = own.execute("SELECT id FROM decisions WHERE status='pending' LIMIT 1").fetchone()
            own.execute(
                "UPDATE decisions SET status='cancelled', resolved_at=? WHERE id=?",
                (store.now(), row["id"]),
            )
            own.commit()
        finally:
            own.close()

    threading.Thread(target=_cancel_in_thread, daemon=True).start()
    out = mode.beslis(_decision(risico="hoog"))
    assert out["actie"] == "skip"


# ---------- timeout ----------


def test_timeout_raised_zonder_resolution(conn: sqlite3.Connection) -> None:
    notif = _fake_notifier()
    mode = IntegerMode(notifier=notif, conn=conn, poll_interval_s=0.01, timeout_s=0.05)
    with pytest.raises(TimeoutError):
        mode.beslis(_decision(risico="hoog"))


# ---------- protocol + naam ----------


def test_integer_implementeert_mode_protocol(conn: sqlite3.Connection) -> None:
    from iso_audit.modes.base import Mode

    assert isinstance(IntegerMode(notifier=_fake_notifier(), conn=conn), Mode)


def test_integer_heeft_naam_attribute() -> None:
    assert IntegerMode.naam == "integer"


# ---------- Helpers ----------


def _resolve_op_thread(
    conn: sqlite3.Connection,
    besluit: dict[str, Any],
    na_seconden: float = 0.05,
) -> None:
    """Start een background-thread die de pending-rij resolved (mockt resolver).

    De thread opent zijn eigen sqlite-verbinding — sqlite3-connecties zijn
    standaard niet thread-safe (`check_same_thread=True`). In productie zit
    de DecisionResolver typisch in een andere thread/process en heeft zelf
    een conn.
    """
    pad = conn.execute("PRAGMA database_list").fetchone()["file"]

    def _run() -> None:
        time.sleep(na_seconden)
        own = store.verbinding(pad)
        try:
            row = own.execute(
                "SELECT id FROM decisions WHERE status='pending' ORDER BY created_at DESC LIMIT 1"
            ).fetchone()
            if row is not None:
                store.resolve_decision(own, row["id"], besluit=besluit)
        finally:
            own.close()

    threading.Thread(target=_run, daemon=True).start()
