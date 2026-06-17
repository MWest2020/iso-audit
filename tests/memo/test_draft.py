"""Tests voor `iso_audit.memo.draft` (LLM-draft van kop-NC's)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import yaml

from iso_audit.memo import draft as draft_mod
from iso_audit.memo.draft import cluster_ncs, draft_findings
from iso_audit.memo.models import Finding
from iso_audit.memo.norm_lookup import laad_norm_db


def _f(fid: str, sev: str, clause: str) -> Finding:
    return Finding(
        id=fid,
        severity=sev,  # type: ignore[arg-type]
        standard="iso-27001-2022",
        clause=clause,
        title=f"f{fid}",
        description="ruwe bevinding",
    )


def _norm_db(tmp_path: Path):
    doc = {
        "metadata": {"standard": "ISO 27001:2022", "slug": "iso-27001-2022"},
        "clauses": {
            "6.5": {
                "title_nl": "Verantwoordelijkheden",
                "title_en": "",
                "text_nl": "x",
                "text_en": "",
            },
            "5.11": {"title_nl": "Retournering", "title_en": "", "text_nl": "y", "text_en": ""},
        },
    }
    (tmp_path / "iso-27001-2022.yaml").write_text(yaml.safe_dump(doc), encoding="utf-8")
    return laad_norm_db(tmp_path)


def test_cluster_ncs_top_n_op_grootte() -> None:
    fs = [_f("1", "NC", "6.5"), _f("2", "NC", "6.5"), _f("3", "NC", "5.11"), _f("4", "OFI", "6.5")]
    clusters = cluster_ncs(fs, top_n=1)
    assert len(clusters) == 1
    assert [f.clause for f in clusters[0]] == ["6.5", "6.5"]  # grootste cluster


def test_parse_json_met_fences() -> None:
    data = draft_mod._parse_json('```json\n{"title": "T", "deviation": "d"}\n```')
    assert data["title"] == "T"


def test_draft_findings_mock(tmp_path: Path) -> None:
    db = _norm_db(tmp_path)
    fs = [
        _f("1", "NC", "6.5"),
        _f("2", "NC", "6.5"),
        _f("3", "NC", "5.11"),
        _f("p", "POSITIVE", "6.5"),
    ]

    block = MagicMock()
    block.text = '{"title": "Kop-NC", "deviation": "Afwijking.", "corrective_measure": "Doe X."}'
    resp = MagicMock()
    resp.content = [block]
    fake = MagicMock()
    fake.messages.create.return_value = resp

    with patch.object(draft_mod.anthropic, "Anthropic", return_value=fake):
        out = draft_findings(fs, norm_db=db, language="nl", top_n=2)

    ncs = [f for f in out if f.severity == "NC"]
    assert len(ncs) == 2  # twee kop-NC's gedraft
    assert all(f.corrective_measure == "Doe X." for f in ncs)
    assert any(f.severity == "POSITIVE" for f in out)  # niet-NC behouden


def test_draft_aggregeert_bronnen_gededupliceerd(tmp_path: Path) -> None:
    """Kop-NC bundelt de brondocumenten van zijn cluster, dedup op (herkomst, id)."""
    from iso_audit.memo.models import BronRef

    db = _norm_db(tmp_path)
    f1, f2, f3 = _f("1", "NC", "6.5"), _f("2", "NC", "6.5"), _f("3", "NC", "6.5")
    f1.bronnen = [BronRef(herkomst="Drive", doc_id="d1", doc_naam="Beleid", url="u1")]
    f2.bronnen = [BronRef(herkomst="Jira", doc_id="ISO-7", doc_naam="ISO-7", url="u2")]
    f3.bronnen = [BronRef(herkomst="Drive", doc_id="d1", doc_naam="Beleid", url="u1")]  # duplicaat

    block = MagicMock()
    block.text = '{"title": "Kop-NC", "deviation": "d", "corrective_measure": "X."}'
    resp = MagicMock()
    resp.content = [block]
    fake = MagicMock()
    fake.messages.create.return_value = resp

    with patch.object(draft_mod.anthropic, "Anthropic", return_value=fake):
        out = draft_findings([f1, f2, f3], norm_db=db, language="nl", top_n=1)

    nc = next(f for f in out if f.severity == "NC")
    sleutels = {(b.herkomst, b.doc_id) for b in nc.bronnen}
    assert sleutels == {("Drive", "d1"), ("Jira", "ISO-7")}  # dup samengevoegd
    assert len(nc.bronnen) == 2
