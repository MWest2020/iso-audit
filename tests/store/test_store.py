"""Tests voor `iso_audit.store` — schema-init, upserts, FTS-zoek."""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest

from iso_audit import store


@pytest.fixture
def conn(tmp_path: Path) -> Iterator[sqlite3.Connection]:
    """SQLite-verbinding op een per-test wegwerp-pad; schema geïnitialiseerd."""
    db = tmp_path / "audit.db"
    c = store.verbinding(str(db))
    store.initialiseer(c)
    try:
        yield c
    finally:
        c.close()


def test_initialiseer_maakt_alle_tabellen(conn: sqlite3.Connection) -> None:
    expected = {
        "documents",
        "miro_notes",
        "clause_matches",
        "ingest_log",
        "bevindingen",
        "interviews",
        "documents_fts",
    }
    tables = {
        r["name"]
        for r in conn.execute("SELECT name FROM sqlite_master WHERE type IN ('table','view')")
    }
    missing = expected - tables
    assert not missing, f"ontbrekende tabellen: {missing}"


def test_initialiseer_idempotent(conn: sqlite3.Connection) -> None:
    """Twee keer `initialiseer` mag niet falen (CREATE IF NOT EXISTS)."""
    store.initialiseer(conn)
    store.initialiseer(conn)


def test_upsert_document_insert_en_update(conn: sqlite3.Connection) -> None:
    doc: dict[str, Any] = {
        "id": "doc1",
        "naam": "Beleid-v1",
        "tekst": "eerste versie",
        "herkomst": "Drive",
        "mime_type": "text/plain",
        "modified_at": "2026-01-01T00:00:00Z",
    }
    store.upsert_document(conn, doc)
    row = conn.execute("SELECT * FROM documents WHERE id = ?", ("doc1",)).fetchone()
    assert row is not None
    assert row["naam"] == "Beleid-v1"
    assert row["tekst"] == "eerste versie"

    # Update: zelfde id, andere tekst.
    doc["naam"] = "Beleid-v2"
    doc["tekst"] = "tweede versie"
    store.upsert_document(conn, doc)
    row = conn.execute("SELECT * FROM documents WHERE id = ?", ("doc1",)).fetchone()
    assert row["naam"] == "Beleid-v2"
    assert row["tekst"] == "tweede versie"
    # Slechts één rij — upsert, geen duplicate.
    (count,) = conn.execute("SELECT COUNT(*) FROM documents").fetchone()
    assert count == 1


def test_upsert_document_defaults(conn: sqlite3.Connection) -> None:
    """`tekst`/`herkomst` mogen ontbreken; defaults uit functie."""
    store.upsert_document(conn, {"id": "doc2", "naam": "Doc"})
    row = conn.execute("SELECT * FROM documents WHERE id = ?", ("doc2",)).fetchone()
    assert row["tekst"] == ""
    assert row["herkomst"] == "Drive"
    assert row["mime_type"] is None


def test_upsert_miro_note(conn: sqlite3.Connection) -> None:
    note: dict[str, Any] = {
        "miro_item_id": "m1",
        "tekst": "Geel sticky",
        "kleur": "yellow",
        "pre_classificatie": None,
        "board_id": "board-abc",
    }
    store.upsert_miro_note(conn, note)
    row = conn.execute("SELECT * FROM miro_notes WHERE id = ?", ("m1",)).fetchone()
    assert row["tekst"] == "Geel sticky"
    assert row["kleur"] == "yellow"


def test_upsert_clause_match_idempotent(conn: sqlite3.Connection) -> None:
    """`INSERT OR IGNORE` — dubbele match geen duplicate."""
    store.upsert_clause_match(conn, "doc1", "Drive", "8.16", "27001")
    store.upsert_clause_match(conn, "doc1", "Drive", "8.16", "27001")
    (count,) = conn.execute("SELECT COUNT(*) FROM clause_matches").fetchone()
    assert count == 1


def test_log_ingest_overwrite(conn: sqlite3.Connection) -> None:
    """`log_ingest` op zelfde bron overschrijft (laatste run wint)."""
    store.log_ingest(conn, "drive", "folder-A", 10)
    store.log_ingest(conn, "drive", "folder-B", 25)
    rows = conn.execute("SELECT * FROM ingest_log").fetchall()
    assert len(rows) == 1
    assert rows[0]["folder_id"] == "folder-B"
    assert rows[0]["bestand_count"] == 25


def test_zoek_full_text(conn: sqlite3.Connection) -> None:
    store.upsert_document(
        conn,
        {
            "id": "d1",
            "naam": "Memo offboarding",
            "tekst": "Procedure voor beëindiging dienstverband.",
        },
    )
    store.upsert_document(
        conn,
        {
            "id": "d2",
            "naam": "Beleid logging",
            "tekst": "Audit-trail bewaartermijn vijf jaar.",
        },
    )
    results = store.zoek(conn, "offboarding", limit=5)
    assert len(results) == 1
    assert results[0]["id"] == "d1"

    results = store.zoek(conn, "logging OR audit", limit=5)
    ids = {r["id"] for r in results}
    assert "d2" in ids


def test_upsert_interview_en_laad(conn: sqlite3.Connection) -> None:
    store.upsert_interview(conn, "5.27", "27001", "OFI", "deels", "lessons-learned ontbreekt")
    store.upsert_interview(conn, "10.2", "9001", "NC", "nee", "geen effect-meting")
    # Update op (5.27, 27001) — geen duplicate, antwoord-update.
    store.upsert_interview(conn, "5.27", "27001", "NC", "nee", "geüpgraded na review")

    alle = store.laad_interviews(conn)
    assert len(alle) == 2

    iso27 = store.laad_interviews(conn, norm="27001")
    assert len(iso27) == 1
    assert iso27[0]["bevinding"] == "NC"
    assert iso27[0]["antwoord"] == "nee"


def test_now_iso_8601() -> None:
    s = store.now()
    # Ruwe shape-check; geen behoefte aan exacte parsering.
    assert "T" in s
    assert s.endswith("+00:00")


def test_db_pad_env_override(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    override = str(tmp_path / "custom.db")
    monkeypatch.setenv("AUDIT_DB_PATH", override)
    assert store.db_pad() == override


def test_db_pad_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("AUDIT_DB_PATH", raising=False)
    assert store.db_pad() == store.DEFAULT_DB_PATH
