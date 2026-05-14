"""Tests voor `iso_audit.miro.ingest` — met gemockte `MiroClient`."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any
from unittest.mock import MagicMock

import pytest

from iso_audit.miro import ingest

# ---------- _kleur_naar_classificatie ----------


@pytest.mark.parametrize(
    "kleur, verwacht",
    [
        ("green", "positief"),
        ("light_green", "positief"),
        ("#82b366", "positief"),
        ("#D5E8D4", "positief"),  # case-insensitive
        ("red", "NC"),
        ("dark_red", "NC"),
        ("orange", "NC"),
        ("yellow", "NC"),
        ("#ff0000", "NC"),
        ("blue", None),
        ("", None),
        (None, None),
    ],
)
def test_kleur_naar_classificatie(kleur: str | None, verwacht: str | None) -> None:
    assert ingest._kleur_naar_classificatie(kleur) == verwacht


# ---------- _tekst_uit_item ----------


def test_tekst_uit_item_content_veld() -> None:
    item = {"data": {"content": "<p>Hallo wereld</p>"}}
    assert ingest._tekst_uit_item(item) == "Hallo wereld"


def test_tekst_uit_item_text_veld() -> None:
    item = {"data": {"text": "Plain text"}}
    assert ingest._tekst_uit_item(item) == "Plain text"


def test_tekst_uit_item_strip_html() -> None:
    item = {"data": {"content": "<strong>Bold</strong> en <em>italic</em>"}}
    assert ingest._tekst_uit_item(item) == "Bold en italic"


def test_tekst_uit_item_leeg() -> None:
    assert ingest._tekst_uit_item({}) == ""
    assert ingest._tekst_uit_item({"data": {}}) == ""
    assert ingest._tekst_uit_item({"data": {"content": ""}}) == ""


# ---------- haal_notities_op ----------


def _fake_client_yields(per_type: dict[str, list[dict[str, Any]]]) -> MagicMock:
    """Mock-MiroClient die per item_type een vaste lijst items yieldt."""
    client = MagicMock()

    def paginated_get(
        endpoint: str, params: dict[str, Any] | None = None
    ) -> Iterator[dict[str, Any]]:
        item_type = (params or {}).get("type", "")
        yield from per_type.get(item_type, [])

    client.paginated_get = MagicMock(side_effect=paginated_get)
    return client


def test_haal_notities_op_zonder_board_id(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("MIRO_BOARD_ID", raising=False)
    with pytest.raises(OSError, match="MIRO_BOARD_ID"):
        ingest.haal_notities_op(client=MagicMock())


def test_haal_notities_op_skipt_lege_tekst() -> None:
    client = _fake_client_yields(
        {
            "sticky_note": [
                {
                    "id": "s1",
                    "data": {"content": "Geldige notitie"},
                    "style": {"fillColor": "green"},
                },
                {"id": "s2", "data": {"content": ""}, "style": {"fillColor": "red"}},
            ],
            "text": [],
        }
    )
    notities = ingest.haal_notities_op(board_id="b1", client=client)
    assert len(notities) == 1
    assert notities[0]["miro_item_id"] == "s1"


def test_haal_notities_op_pre_classificatie_via_kleur() -> None:
    client = _fake_client_yields(
        {
            "sticky_note": [
                {"id": "g", "data": {"content": "ok"}, "style": {"fillColor": "green"}},
                {"id": "r", "data": {"content": "fout"}, "style": {"fillColor": "red"}},
                {"id": "b", "data": {"content": "neutraal"}, "style": {"fillColor": "blue"}},
            ],
            "text": [],
        }
    )
    notities = ingest.haal_notities_op(board_id="b1", client=client)
    by_id = {n["miro_item_id"]: n for n in notities}
    assert by_id["g"]["pre_classificatie"] == "positief"
    assert by_id["r"]["pre_classificatie"] == "NC"
    assert by_id["b"]["pre_classificatie"] is None


def test_haal_notities_op_combineert_types() -> None:
    """Sticky-notes en text-widgets worden allebei opgehaald."""
    client = _fake_client_yields(
        {
            "sticky_note": [
                {"id": "s", "data": {"content": "sticky"}, "style": {}},
            ],
            "text": [
                {"id": "t", "data": {"text": "tekstvak"}, "style": {}},
            ],
        }
    )
    notities = ingest.haal_notities_op(board_id="b1", client=client)
    assert {n["miro_item_id"] for n in notities} == {"s", "t"}
    # Twee paginated_get-calls: één per type.
    assert client.paginated_get.call_count == 2


def test_haal_notities_op_kleur_fallback_naar_background_color() -> None:
    """Als `style.fillColor` ontbreekt, valt het terug op `data.backgroundColor`."""
    client = _fake_client_yields(
        {
            "sticky_note": [
                {"id": "x", "data": {"content": "ok", "backgroundColor": "green"}},
            ],
            "text": [],
        }
    )
    notities = ingest.haal_notities_op(board_id="b1", client=client)
    assert notities[0]["pre_classificatie"] == "positief"


# ---------- koppel_aan_clausules ----------


def test_koppel_aan_clausules_match() -> None:
    notities: list[dict[str, Any]] = [
        {"tekst": "logging review", "miro_item_id": "1"},
        {"tekst": "iets onbekends", "miro_item_id": "2"},
    ]
    clause_map = {
        "clausules": {
            "8.15": {"zoektermen": ["logging"]},
            "10.2": {"zoektermen": ["evaluatie"]},
        }
    }
    result = ingest.koppel_aan_clausules(notities, clause_map)
    assert result[0]["clausule"] == "8.15"
    assert result[1]["clausule"] is None


def test_koppel_aan_clausules_first_match_wins() -> None:
    """Eerste match in iteratievolgorde van clause_map wint."""
    notities: list[dict[str, Any]] = [{"tekst": "audit en logging", "miro_item_id": "1"}]
    clause_map = {
        "clausules": {
            "8.15": {"zoektermen": ["logging"]},
            "9.2": {"zoektermen": ["audit"]},
        }
    }
    result = ingest.koppel_aan_clausules(notities, clause_map)
    assert result[0]["clausule"] == "8.15"


# ---------- merge_met_drive_bevindingen ----------


def test_merge() -> None:
    drive = [{"herkomst": "Drive", "naam": "doc"}]
    miro = [{"herkomst": "Miro", "tekst": "note"}]
    merged = ingest.merge_met_drive_bevindingen(miro, drive)
    assert merged == drive + miro
