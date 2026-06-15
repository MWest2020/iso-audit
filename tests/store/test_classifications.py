"""Tests voor `classifications`-tabel + `log_classification` (§2.6.5).

Scope: traceability-velden (audit_id, finding_id, input_hash,
prompt_versie, model_versie, raw_output, usage, elapsed_s) + dedup
op `(audit_id, finding_id, prompt_versie, model_versie)`.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from iso_audit import store


@pytest.fixture()
def conn(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> object:
    monkeypatch.setenv("AUDIT_DB_PATH", str(tmp_path / "audit.db"))
    c = store.verbinding()
    store.initialiseer(c)
    yield c
    c.close()


# ---------- schema ----------


def test_classifications_tabel_bestaat(conn: object) -> None:
    rows = conn.execute(  # type: ignore[attr-defined]
        "SELECT name FROM sqlite_master WHERE type='table' AND name='classifications'"
    ).fetchall()
    assert len(rows) == 1


def test_classifications_indexen_bestaan(conn: object) -> None:
    rows = conn.execute(  # type: ignore[attr-defined]
        "SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_classifications%'"
    ).fetchall()
    namen = {r[0] for r in rows}
    assert "idx_classifications_audit" in namen
    assert "idx_classifications_finding" in namen


# ---------- log_classification: basis ----------


def test_log_classification_schrijft_rij(conn: object) -> None:
    store.log_classification(
        conn,  # type: ignore[arg-type]
        audit_id="audit-1",
        finding_id="drive:doc-1:4.1",
        system_prompt="systeem",
        user_prompt="user",
        model="claude-haiku-4-5-20251001",
        raw_output='[{"clausule": "4.1"}]',
        usage={"input_tokens": 100, "output_tokens": 20},
        elapsed_s=0.42,
    )
    row = conn.execute(  # type: ignore[attr-defined]
        "SELECT * FROM classifications"
    ).fetchone()
    assert row is not None
    assert row["audit_id"] == "audit-1"
    assert row["finding_id"] == "drive:doc-1:4.1"
    assert row["model_versie"] == "claude-haiku-4-5-20251001"
    assert row["elapsed_s"] == 0.42
    assert json.loads(row["usage_json"]) == {
        "input_tokens": 100,
        "output_tokens": 20,
    }


def test_log_classification_zonder_usage(conn: object) -> None:
    store.log_classification(
        conn,  # type: ignore[arg-type]
        audit_id="audit-1",
        finding_id="drive:doc-1:4.1",
        system_prompt="systeem",
        user_prompt="u",
        model="m",
        raw_output="x",
    )
    row = conn.execute(  # type: ignore[attr-defined]
        "SELECT usage_json, elapsed_s FROM classifications"
    ).fetchone()
    assert row["usage_json"] is None
    assert row["elapsed_s"] is None


# ---------- input_hash + prompt_versie ----------


def test_prompt_versie_alleen_van_systeem(conn: object) -> None:
    """Twee verschillende user-prompts met dezelfde system geven dezelfde prompt_versie."""
    store.log_classification(
        conn,  # type: ignore[arg-type]
        audit_id="a",
        finding_id="f1",
        system_prompt="zelfde systeem",
        user_prompt="user-A",
        model="m",
        raw_output="x",
    )
    store.log_classification(
        conn,  # type: ignore[arg-type]
        audit_id="a",
        finding_id="f2",
        system_prompt="zelfde systeem",
        user_prompt="user-B",
        model="m",
        raw_output="y",
    )
    rows = conn.execute(  # type: ignore[attr-defined]
        "SELECT prompt_versie, input_hash FROM classifications ORDER BY id"
    ).fetchall()
    assert rows[0]["prompt_versie"] == rows[1]["prompt_versie"]
    # Maar input_hash moet verschillen (verschillende user-prompts).
    assert rows[0]["input_hash"] != rows[1]["input_hash"]


def test_input_hash_deterministisch(conn: object) -> None:
    """Zelfde system+user → zelfde input_hash."""
    for finding in ("f1", "f2"):
        store.log_classification(
            conn,  # type: ignore[arg-type]
            audit_id="a",
            finding_id=finding,
            system_prompt="sys",
            user_prompt="usr",
            model="m",
            raw_output="r",
        )
    rows = conn.execute(  # type: ignore[attr-defined]
        "SELECT input_hash FROM classifications"
    ).fetchall()
    assert rows[0][0] == rows[1][0]


# ---------- dedup ----------


def test_dedup_op_audit_finding_prompt_model(conn: object) -> None:
    """Tweede call met identieke key wordt genegeerd (INSERT OR IGNORE)."""
    args = {
        "audit_id": "a-1",
        "finding_id": "f-1",
        "system_prompt": "sys",
        "user_prompt": "u",
        "model": "m",
        "raw_output": "v1",
    }
    store.log_classification(conn, **args)  # type: ignore[arg-type]
    store.log_classification(conn, **args)  # type: ignore[arg-type]
    rows = conn.execute(  # type: ignore[attr-defined]
        "SELECT raw_output FROM classifications WHERE audit_id='a-1' AND finding_id='f-1'"
    ).fetchall()
    assert len(rows) == 1
    # Eerste insert blijft staan; tweede call overschrijft niet.
    assert rows[0][0] == "v1"


def test_dedup_split_op_audit_id(conn: object) -> None:
    """Twee audit-IDs voor dezelfde finding → twee rijen."""
    common = {
        "finding_id": "f-1",
        "system_prompt": "sys",
        "user_prompt": "u",
        "model": "m",
        "raw_output": "r",
    }
    store.log_classification(conn, audit_id="a-1", **common)  # type: ignore[arg-type]
    store.log_classification(conn, audit_id="a-2", **common)  # type: ignore[arg-type]
    rows = conn.execute(  # type: ignore[attr-defined]
        "SELECT audit_id FROM classifications ORDER BY audit_id"
    ).fetchall()
    assert [r[0] for r in rows] == ["a-1", "a-2"]


def test_dedup_split_op_prompt_versie(conn: object) -> None:
    """Verschillende system-prompts → verschillende prompt_versie → twee rijen."""
    common = {
        "audit_id": "a-1",
        "finding_id": "f-1",
        "user_prompt": "u",
        "model": "m",
        "raw_output": "r",
    }
    store.log_classification(conn, system_prompt="sys-v1", **common)  # type: ignore[arg-type]
    store.log_classification(conn, system_prompt="sys-v2", **common)  # type: ignore[arg-type]
    rows = conn.execute(  # type: ignore[attr-defined]
        "SELECT id FROM classifications"
    ).fetchall()
    assert len(rows) == 2


def test_dedup_split_op_model_versie(conn: object) -> None:
    """Verschillende modellen → twee rijen."""
    common = {
        "audit_id": "a-1",
        "finding_id": "f-1",
        "system_prompt": "sys",
        "user_prompt": "u",
        "raw_output": "r",
    }
    store.log_classification(conn, model="m1", **common)  # type: ignore[arg-type]
    store.log_classification(conn, model="m2", **common)  # type: ignore[arg-type]
    rows = conn.execute(  # type: ignore[attr-defined]
        "SELECT model_versie FROM classifications ORDER BY model_versie"
    ).fetchall()
    assert [r[0] for r in rows] == ["m1", "m2"]


# ---------- laad_classifications ----------


def test_laad_classifications_filter_op_audit(conn: object) -> None:
    for i, aid in enumerate(("a-1", "a-2", "a-1")):
        store.log_classification(
            conn,  # type: ignore[arg-type]
            audit_id=aid,
            finding_id=f"f-{i}",
            system_prompt="s",
            user_prompt="u",
            model="m",
            raw_output="r",
        )
    rows = store.laad_classifications(conn, audit_id="a-1")  # type: ignore[arg-type]
    assert len(rows) == 2


def test_laad_classifications_filter_op_finding(conn: object) -> None:
    store.log_classification(
        conn,  # type: ignore[arg-type]
        audit_id="a-1",
        finding_id="f-X",
        system_prompt="s",
        user_prompt="u",
        model="m",
        raw_output="r",
    )
    store.log_classification(
        conn,  # type: ignore[arg-type]
        audit_id="a-1",
        finding_id="f-Y",
        system_prompt="s",
        user_prompt="u",
        model="m",
        raw_output="r",
    )
    rows = store.laad_classifications(conn, finding_id="f-X")  # type: ignore[arg-type]
    assert len(rows) == 1
    assert rows[0]["finding_id"] == "f-X"


def test_laad_classifications_zonder_filter(conn: object) -> None:
    store.log_classification(
        conn,  # type: ignore[arg-type]
        audit_id="a",
        finding_id="f",
        system_prompt="s",
        user_prompt="u",
        model="m",
        raw_output="r",
    )
    rows = store.laad_classifications(conn)  # type: ignore[arg-type]
    assert len(rows) == 1


def test_laad_classifications_filter_op_beide(conn: object) -> None:
    store.log_classification(
        conn,  # type: ignore[arg-type]
        audit_id="a-1",
        finding_id="f-1",
        system_prompt="s",
        user_prompt="u",
        model="m",
        raw_output="r",
    )
    store.log_classification(
        conn,  # type: ignore[arg-type]
        audit_id="a-2",
        finding_id="f-1",
        system_prompt="s",
        user_prompt="u",
        model="m",
        raw_output="r",
    )
    rows = store.laad_classifications(
        conn,  # type: ignore[arg-type]
        audit_id="a-1",
        finding_id="f-1",
    )
    assert len(rows) == 1
    assert rows[0]["audit_id"] == "a-1"
