"""Tests voor `iso_audit.notifiers.resolver.SqliteDecisionResolver` (§3.2.1)."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

import pytest

from iso_audit import store
from iso_audit.notifiers.resolver import SqliteDecisionResolver


@pytest.fixture()
def conn(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> sqlite3.Connection:
    monkeypatch.setenv("AUDIT_DB_PATH", str(tmp_path / "audit.db"))
    c = store.verbinding()
    store.initialiseer(c)
    yield c
    c.close()


def _make_pending(conn: sqlite3.Connection, voorstel: dict[str, Any]) -> int:
    return store.schrijf_decision(
        conn,
        audit_id="a-1",
        punt="send_report",
        context={},
        voorstel=voorstel,
        risico="hoog",
        status="pending",
        notifier_naam="slack",
    )


# ---------- happy paths ----------


def test_approve_neemt_voorstel_over(conn: sqlite3.Connection) -> None:
    voorstel = {"verzenden": True, "ontvangers": ["mt@conduction.nl"]}
    dec_id = _make_pending(conn, voorstel)
    resolver = SqliteDecisionResolver(conn)
    resolver.resolve(str(dec_id), action="approve")
    row = store.laad_decision(conn, dec_id)
    assert row is not None
    assert row["status"] == "resolved"
    assert json.loads(row["besluit_json"]) == voorstel


def test_reject_geeft_skip_besluit(conn: sqlite3.Connection) -> None:
    dec_id = _make_pending(conn, {"verzenden": True})
    resolver = SqliteDecisionResolver(conn)
    resolver.resolve(str(dec_id), action="reject")
    row = store.laad_decision(conn, dec_id)
    assert row["status"] == "resolved"
    besluit = json.loads(row["besluit_json"])
    assert besluit["voorstel_afgewezen"] is True


def test_modify_neemt_modified_payload_over(conn: sqlite3.Connection) -> None:
    dec_id = _make_pending(conn, {"verzenden": True})
    resolver = SqliteDecisionResolver(conn)
    nieuw = {"verzenden": False, "reden": "MT wil eerst review"}
    resolver.resolve(str(dec_id), action="modify", modified_payload=nieuw)
    row = store.laad_decision(conn, dec_id)
    assert json.loads(row["besluit_json"]) == nieuw


def test_abort_zet_status_cancelled(conn: sqlite3.Connection) -> None:
    dec_id = _make_pending(conn, {"verzenden": True})
    resolver = SqliteDecisionResolver(conn)
    resolver.resolve(str(dec_id), action="abort")
    row = store.laad_decision(conn, dec_id)
    assert row["status"] == "cancelled"


# ---------- errors ----------


def test_onbekende_action_raised(conn: sqlite3.Connection) -> None:
    dec_id = _make_pending(conn, {})
    resolver = SqliteDecisionResolver(conn)
    with pytest.raises(ValueError, match="Onbekende action"):
        resolver.resolve(str(dec_id), action="explode")


def test_modify_zonder_payload_raised(conn: sqlite3.Connection) -> None:
    dec_id = _make_pending(conn, {})
    resolver = SqliteDecisionResolver(conn)
    with pytest.raises(ValueError, match="modified_payload"):
        resolver.resolve(str(dec_id), action="modify")


def test_niet_bestaande_decision_id_raised(conn: sqlite3.Connection) -> None:
    resolver = SqliteDecisionResolver(conn)
    with pytest.raises(KeyError):
        resolver.resolve("999", action="approve")


def test_niet_integer_decision_id_raised(conn: sqlite3.Connection) -> None:
    resolver = SqliteDecisionResolver(conn)
    with pytest.raises(ValueError, match="integer-string"):
        resolver.resolve("not-a-number", action="approve")


# ---------- append-only ----------


def test_dubbele_resolve_negeert_tweede(conn: sqlite3.Connection) -> None:
    """Resolved rij wordt NIET overschreven door een tweede call."""
    dec_id = _make_pending(conn, {"verzenden": True})
    resolver = SqliteDecisionResolver(conn)
    resolver.resolve(str(dec_id), action="approve")
    eerste_besluit = json.loads(store.laad_decision(conn, dec_id)["besluit_json"])

    # Tweede resolve op dezelfde id — store.resolve_decision is append-only
    # via WHERE status='pending' clause; de notifier-resolver kan dat triggeren
    # zonder dat de rij wordt aangepast.
    resolver.resolve(str(dec_id), action="reject")
    tweede_besluit = json.loads(store.laad_decision(conn, dec_id)["besluit_json"])
    assert tweede_besluit == eerste_besluit


# ---------- protocol-conformance ----------


def test_resolver_implementeert_decisionresolver_protocol(
    conn: sqlite3.Connection,
) -> None:
    from iso_audit.notifiers.base import DecisionResolver

    assert isinstance(SqliteDecisionResolver(conn), DecisionResolver)
