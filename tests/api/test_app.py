"""Tests voor de auditor-API (`iso_audit.api`)."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from iso_audit.api.app import create_app
from iso_audit.api.session import AuditSession

_EX = Path("examples/auditmemo")
_FINDINGS = [
    {
        "id": "f1",
        "severity": "NC",
        "standard": "iso-27001-2022",
        "clause": "6.5",
        "title": "Offboarding",
        "description": "Offboarding niet aantoonbaar afgesloten.",
        "triage_status": "valide",
    },
    {
        "id": "f2",
        "severity": "OFI",
        "standard": "iso-9001-2015",
        "clause": "10.2",
        "title": "Effectiviteits-evaluatie",
        "description": "Niet vastgelegd.",
    },
]


def _client(tmp_path: Path) -> TestClient:
    (tmp_path / "findings.json").write_text(json.dumps(_FINDINGS), encoding="utf-8")
    session = AuditSession(
        tmp_path,
        profile=str(_EX / "conduction.profile.yaml"),
        norms_dir="examples/norms",
        memo_input_path=str(_EX / "memo-input.yaml"),
    )
    return TestClient(create_app(session))


def test_get_findings(tmp_path: Path) -> None:
    r = _client(tmp_path).get("/findings")
    assert r.status_code == 200
    ids = {f["id"] for f in r.json()}
    assert ids == {"f1", "f2"}


def test_reclassify_nc_naar_ofi_append_only(tmp_path: Path) -> None:
    client = _client(tmp_path)
    r = client.post("/findings/f1", json={"severity": "OFI", "reason": "bewijs in interview"})
    assert r.status_code == 200
    assert r.json()["severity"] == "OFI"
    # trail bevat de override (append-only) met from/to + reden.
    trail = client.get("/trail").json()
    assert len(trail) == 1
    assert trail[0]["field"] == "severity"
    assert trail[0]["from"] == "NC" and trail[0]["to"] == "OFI"
    assert trail[0]["reason"] == "bewijs in interview"


def test_triage_status_append_groeit(tmp_path: Path) -> None:
    client = _client(tmp_path)
    client.post("/findings/f1", json={"severity": "OFI", "reason": "r1"})
    client.post("/findings/f1", json={"triage_status": "niet_valide", "reason": "r2"})
    trail = client.get("/trail").json()
    assert len(trail) == 2  # append-only: eerste blijft staan
    assert trail[1]["field"] == "triage_status"


def test_memo_gated_bij_open_kandidaat(tmp_path: Path) -> None:
    client = _client(tmp_path)
    # zet de NC terug naar 'open' → memo moet 409'en (triage niet compleet).
    client.post("/findings/f1", json={"triage_status": "open", "reason": "heropenen"})
    assert client.get("/triage/status").json()["complete"] is False
    assert client.get("/memo/preview").status_code == 409


def test_triage_status_endpoint(tmp_path: Path) -> None:
    d = _client(tmp_path).get("/triage/status").json()
    assert d == {"total_nc": 1, "open": 0, "complete": True}


def test_finding_detail(tmp_path: Path) -> None:
    r = _client(tmp_path).get("/findings/f1")
    assert r.status_code == 200
    assert r.json()["clause"] == "6.5"


def test_tekst_redactie_append_only(tmp_path: Path) -> None:
    client = _client(tmp_path)
    r = client.post(
        "/findings/f1",
        json={
            "deviation": "Herschreven afwijking.",
            "corrective_measure": "Doe Z.",
            "reason": "redactie",
        },
    )
    assert r.status_code == 200
    assert client.get("/findings/f1").json()["deviation"] == "Herschreven afwijking."
    velden = {e["field"] for e in client.get("/trail").json()}
    assert {"deviation", "corrective_measure"} <= velden


def test_onbekende_finding_404(tmp_path: Path) -> None:
    r = _client(tmp_path).post("/findings/zzz", json={"severity": "OFI", "reason": "x"})
    assert r.status_code == 404


def test_memo_preview_rendert_html(tmp_path: Path) -> None:
    r = _client(tmp_path).get("/memo/preview")
    assert r.status_code == 200
    assert "Auditmemo" in r.text
    assert "Offboarding" in r.text


def test_findings_severity_filter(tmp_path: Path) -> None:
    r = _client(tmp_path).get("/findings", params={"severity": "NC"})
    data = r.json()
    assert [f["id"] for f in data] == ["f1"]  # alleen de NC


def test_landscape(tmp_path: Path) -> None:
    d = _client(tmp_path).get("/landscape").json()
    assert "drive" in d["sources_registered"]  # registry
    assert "6.5" in d["clauses_with_nc"]  # NC-clausule
    assert d["counts"]["NC"] == 1


def test_run_summary(tmp_path: Path) -> None:
    d = _client(tmp_path).post("/run").json()
    assert d["findings"] == 2
    assert "note" in d


def test_index_serveert_ui(tmp_path: Path) -> None:
    r = _client(tmp_path).get("/")
    assert r.status_code == 200
    assert "auditor-flow" in r.text
    assert "Triage" in r.text
