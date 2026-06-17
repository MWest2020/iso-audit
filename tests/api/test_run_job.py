"""Tests voor `iso_audit.api.run_job` — standaard-resolutie bij beide-runs."""

from __future__ import annotations

from pathlib import Path

import yaml

from iso_audit.api.run_job import _resolve_standard
from iso_audit.memo.norm_lookup import laad_norm_db


def _db(tmp_path: Path):  # type: ignore[no-untyped-def]
    def _w(slug: str, clauses: list[str]) -> None:
        doc = {
            "metadata": {"standard": slug, "slug": slug},
            "clauses": {
                c: {"title_nl": c, "title_en": "", "text_nl": "t", "text_en": ""} for c in clauses
            },
        }
        (tmp_path / f"{slug}.yaml").write_text(yaml.safe_dump(doc), encoding="utf-8")

    _w("iso-9001-2015", ["6.2", "10.2"])
    _w("iso-27001-2022", ["8.16", "10.2"])  # 10.2 botst (in beide)
    return laad_norm_db(tmp_path)


def test_resolve_expliciete_norm() -> None:
    assert _resolve_standard("9001", "6.2", None) == "iso-9001-2015"
    assert _resolve_standard("27001", "8.16", None) == "iso-27001-2022"


def test_resolve_beide_alleen_27001(tmp_path: Path) -> None:
    assert _resolve_standard("beide", "8.16", _db(tmp_path)) == "iso-27001-2022"


def test_resolve_beide_alleen_9001(tmp_path: Path) -> None:
    assert _resolve_standard("beide", "6.2", _db(tmp_path)) == "iso-9001-2015"


def test_resolve_beide_botsing_default_9001(tmp_path: Path) -> None:
    # 10.2 zit in beide norm-DB's → default 9001 (bekende beperking).
    assert _resolve_standard("beide", "10.2", _db(tmp_path)) == "iso-9001-2015"


def test_resolve_beide_zonder_db_default() -> None:
    assert _resolve_standard("beide", "8.16", None) == "iso-9001-2015"


def test_has_clause(tmp_path: Path) -> None:
    db = _db(tmp_path)
    assert db.has_clause("iso-27001-2022", "8.16") is True
    assert db.has_clause("iso-9001-2015", "8.16") is False
