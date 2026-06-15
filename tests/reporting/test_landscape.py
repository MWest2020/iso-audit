"""Tests voor `iso_audit.reporting.landscape` — DB-driven, met fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest

from iso_audit import store
from iso_audit.reporting import landscape


@pytest.fixture
def db_pad(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> str:
    """Per-test DB-pad via `AUDIT_DB_PATH`."""
    pad = tmp_path / "audit.db"
    monkeypatch.setenv("AUDIT_DB_PATH", str(pad))
    conn = store.verbinding(str(pad))
    store.initialiseer(conn)
    conn.close()
    return str(pad)


def _seed_match(
    db_pad: str,
    doc_id: str,
    naam: str,
    clausule_id: str,
    norm: str = "9001",
    herkomst: str = "Drive",
) -> None:
    conn = store.verbinding(db_pad)
    if herkomst == "Drive":
        store.upsert_document(conn, {"id": doc_id, "naam": naam, "tekst": ""})
    else:
        store.upsert_miro_note(
            conn,
            {
                "miro_item_id": doc_id,
                "tekst": naam,
                "kleur": None,
                "pre_classificatie": None,
                "board_id": "b1",
            },
        )
    store.upsert_clause_match(conn, doc_id, herkomst, clausule_id, norm, "")
    conn.commit()
    conn.close()


# ---------- _fetch_clause_matches ----------


def test_fetch_clause_matches_zonder_scope_kolom(db_pad: str) -> None:
    """Standaard schema heeft geen `documents.scope` → fallback-query werkt."""
    _seed_match(db_pad, "d1", "Beleid", "10.2", norm="9001")
    conn = store.verbinding(db_pad)
    rows = landscape._fetch_clause_matches(conn, "9001")
    conn.close()
    assert len(rows) == 1
    assert rows[0]["clausule_id"] == "10.2"


def test_fetch_clause_matches_norm_filter(db_pad: str) -> None:
    """27001-match komt niet mee bij norm=9001."""
    _seed_match(db_pad, "d1", "Doc 27001", "8.16", norm="27001")
    _seed_match(db_pad, "d2", "Doc 9001", "10.2", norm="9001")
    conn = store.verbinding(db_pad)
    rows = landscape._fetch_clause_matches(conn, "9001")
    conn.close()
    cids = {r["clausule_id"] for r in rows}
    assert "10.2" in cids
    assert "8.16" not in cids


def test_fetch_clause_matches_beide_norm_meegenomen(db_pad: str) -> None:
    """Matches met norm='beide' komen mee bij alle norm-queries."""
    _seed_match(db_pad, "d1", "Beide", "5.11", norm="beide")
    conn = store.verbinding(db_pad)
    rows_9001 = landscape._fetch_clause_matches(conn, "9001")
    rows_27001 = landscape._fetch_clause_matches(conn, "27001")
    conn.close()
    assert any(r["clausule_id"] == "5.11" for r in rows_9001)
    assert any(r["clausule_id"] == "5.11" for r in rows_27001)


# ---------- genereer_landschap ----------


def test_genereer_landschap_lege_db(db_pad: str) -> None:
    """Lege DB → rapport bevat 0/N-dekking en alle clausules als niet-gedekt."""
    md = landscape.genereer_landschap("9001")
    assert "# Audit Landschap" in md
    assert "0/" in md  # gedekt = 0
    assert "Niet gedekte clausules" in md


def test_genereer_landschap_met_match(db_pad: str) -> None:
    _seed_match(db_pad, "d1", "Memo offboarding", "10.2", norm="9001")
    md = landscape.genereer_landschap("9001")
    assert "## Gedekte clausules" in md
    assert "10.2" in md
    assert "Memo offboarding" in md


def test_genereer_landschap_chapter_filter(db_pad: str) -> None:
    """Met --chapter blijven alleen clausules van dat hoofdstuk over."""
    md = landscape.genereer_landschap("9001", chapter="4")
    # Bevat 9001 §4.* maar niet §5.*
    assert "4.1" in md
    assert "5.1" not in md.replace("9001 §5.1", "")  # ruwe check


def test_genereer_landschap_interview_categorieën(db_pad: str) -> None:
    """Interviews met NC/OFI/positief/overgeslagen worden gegroepeerd."""
    conn = store.verbinding(db_pad)
    store.upsert_interview(conn, "10.2", "9001", "NC", "nee", "geen evaluatie")
    store.upsert_interview(conn, "10.3", "9001", "OFI", "deels", "kan beter")
    store.upsert_interview(conn, "5.1", "9001", "positief", "ja", "")
    conn.commit()
    conn.close()
    md = landscape.genereer_landschap("9001")
    assert "Non-conformiteiten" in md
    assert "Verbeterpunten" in md
    assert "Positief bevonden via interview" in md


# ---------- schrijf_landschap ----------


def test_schrijf_landschap_in_eigen_outputdir(db_pad: str, tmp_path: Path) -> None:
    out_dir = tmp_path / "rapport-output"
    pad = landscape.schrijf_landschap("9001", output_dir=out_dir)
    p = Path(pad)
    assert p.is_file()
    assert p.parent == out_dir
    content = p.read_text(encoding="utf-8")
    assert "Audit Landschap" in content


def test_schrijf_landschap_chapter_in_naam(db_pad: str, tmp_path: Path) -> None:
    pad = landscape.schrijf_landschap("9001", chapter="8", output_dir=tmp_path)
    assert "_h8_" in Path(pad).name


# ---------- zoek_in_db ----------


def test_zoek_in_db_geen_resultaten(db_pad: str, capsys: pytest.CaptureFixture[str]) -> None:
    # Eén woord — FTS5-syntax — geen documenten in DB, dus geen match.
    landscape.zoek_in_db("zoektermwaarvoorgeen")
    out = capsys.readouterr().out
    assert "Geen resultaten" in out


def test_zoek_in_db_match(db_pad: str, capsys: pytest.CaptureFixture[str]) -> None:
    conn = store.verbinding(db_pad)
    store.upsert_document(
        conn,
        {"id": "d1", "naam": "Memo offboarding", "tekst": "Procedure beëindiging dienstverband."},
    )
    conn.commit()
    conn.close()
    landscape.zoek_in_db("offboarding")
    out = capsys.readouterr().out
    assert "Memo offboarding" in out


# `test_fetch_clause_matches_zonder_scope_kolom` hierboven dekt de fallback al:
# de M-B store-schema heeft géén `documents.scope`-kolom, dus de scope-query
# raised `OperationalError` en de fallback wordt automatisch geraakt.
