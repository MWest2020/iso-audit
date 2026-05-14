"""Tests voor `iso_audit.miro.board_setup` — pure helpers + mocked client.

`bouw_bord` is een grote integration-routine die DB-state + Miro-API combineert;
hier focussen we op de pure helpers en op de drie factory-functies die door
`MiroClient.post` lopen.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

from iso_audit.miro import board_setup

# ---------- _clausules_voor_hoofdstuk ----------


def test_clausules_voor_hoofdstuk_prefix_match() -> None:
    cm = {
        "clausules": {
            "4.1": {"titel": "Context"},
            "4.2": {"titel": "Belanghebbenden"},
            "5.1": {"titel": "Leiderschap"},
            "10.2": {"titel": "NC"},
        }
    }
    result = board_setup._clausules_voor_hoofdstuk(cm, "4")
    assert result == [("4.1", "Context"), ("4.2", "Belanghebbenden")]


def test_clausules_voor_hoofdstuk_exact_match_included() -> None:
    cm = {"clausules": {"4": {"titel": "Hoofdstuk 4"}, "4.1": {"titel": "Sub"}}}
    result = board_setup._clausules_voor_hoofdstuk(cm, "4")
    assert ("4", "Hoofdstuk 4") in result
    assert ("4.1", "Sub") in result


def test_clausules_voor_hoofdstuk_geen_match() -> None:
    cm = {"clausules": {"4.1": {"titel": "X"}}}
    assert board_setup._clausules_voor_hoofdstuk(cm, "99") == []


def test_clausules_voor_hoofdstuk_sortering() -> None:
    cm = {
        "clausules": {
            "8.16": {"titel": "Monitoring"},
            "8.2": {"titel": "Toepassing"},
            "8.1": {"titel": "Operationele planning"},
        }
    }
    result = board_setup._clausules_voor_hoofdstuk(cm, "8")
    # Lexicografische sortering (niet numeriek): "8.1" < "8.16" < "8.2"
    assert [cid for cid, _ in result] == ["8.1", "8.16", "8.2"]


# ---------- _kleur_voor_clausule ----------


def test_kleur_interview_overschrijft_dekking() -> None:
    """Interview-NC heeft voorrang boven dekking-via-documenten."""
    matched = {"8.16"}
    interviews = {"8.16": {"bevinding": "NC"}}
    assert board_setup._kleur_voor_clausule("8.16", matched, interviews) == "red"


def test_kleur_interview_ofi() -> None:
    interviews = {"5.27": {"bevinding": "OFI"}}
    assert board_setup._kleur_voor_clausule("5.27", set(), interviews) == "yellow"


def test_kleur_interview_positief() -> None:
    interviews = {"4.1": {"bevinding": "positief"}}
    assert board_setup._kleur_voor_clausule("4.1", set(), interviews) == "light_green"


def test_kleur_dekking_zonder_interview() -> None:
    """Gedekt door documenten → light_green."""
    assert board_setup._kleur_voor_clausule("10.2", {"10.2"}, {}) == "light_green"


def test_kleur_open() -> None:
    """Geen interview, geen dekking → light_yellow."""
    assert board_setup._kleur_voor_clausule("6.1", set(), {}) == "light_yellow"


def test_kleur_onbekende_bevinding_fallback() -> None:
    """Bevinding-key niet in KLEUREN → fallback naar light_yellow."""
    interviews = {"7.1": {"bevinding": "iets-onbekends"}}
    assert board_setup._kleur_voor_clausule("7.1", set(), interviews) == "light_yellow"


# ---------- _drive_link ----------


def test_drive_link_google_doc() -> None:
    assert board_setup._drive_link("abc123", "application/vnd.google-apps.document") == (
        "https://docs.google.com/document/d/abc123"
    )


def test_drive_link_google_sheet() -> None:
    assert board_setup._drive_link("xyz", "application/vnd.google-apps.spreadsheet") == (
        "https://docs.google.com/spreadsheets/d/xyz"
    )


def test_drive_link_overig_mime() -> None:
    """Andere MIME-types (pdf/docx) → generieke Drive-URL."""
    assert board_setup._drive_link("p", "application/pdf") == ("https://drive.google.com/file/d/p")
    assert board_setup._drive_link("q", None) == "https://drive.google.com/file/d/q"


# ---------- factories: maak_bord / maak_frame / maak_sticky ----------


def test_maak_bord_droog_zet_project_id() -> None:
    client = MagicMock()
    client.post.return_value = {"id": "dry-run"}
    bid = board_setup.maak_bord("Test", client, droog=True)
    assert bid == "dry-run"
    body: dict[str, Any] = client.post.call_args.args[1]
    assert body["project"]["id"] == board_setup.DEFAULT_ISO_PROJECT_ID


def test_maak_bord_project_id_via_env(monkeypatch: Any) -> None:
    monkeypatch.setenv(board_setup.MIRO_ISO_PROJECT_ID_ENV, "custom-id")
    client = MagicMock()
    client.post.return_value = {"id": "b-1"}
    board_setup.maak_bord("Test", client)
    body = client.post.call_args.args[1]
    assert body["project"]["id"] == "custom-id"


def test_maak_bord_endpoint() -> None:
    client = MagicMock()
    client.post.return_value = {"id": "b-1"}
    board_setup.maak_bord("Test", client)
    assert client.post.call_args.args[0] == "/boards"


def test_maak_frame_endpoint_en_dimensions() -> None:
    client = MagicMock()
    client.post.return_value = {"id": "f-1"}
    board_setup.maak_frame("board-x", "Frame", x=500, y=600, client=client)
    endpoint, body = client.post.call_args.args[:2]
    assert endpoint == "/boards/board-x/frames"
    assert body["geometry"]["width"] == board_setup.FRAME_WIDTH
    assert body["geometry"]["height"] == board_setup.FRAME_HEIGHT
    assert body["position"] == {"x": 500, "y": 600, "origin": "center"}


def test_maak_sticky_default_kleur() -> None:
    client = MagicMock()
    client.post.return_value = {"id": "s-1"}
    board_setup.maak_sticky("board-x", "tekst", 100, 200, client)
    body = client.post.call_args.args[1]
    assert body["style"]["fillColor"] == "light_yellow"


def test_maak_sticky_eigen_kleur() -> None:
    client = MagicMock()
    client.post.return_value = {"id": "s-1"}
    board_setup.maak_sticky("board-x", "x", 0, 0, client, kleur="red")
    body = client.post.call_args.args[1]
    assert body["style"]["fillColor"] == "red"
    assert body["data"]["content"] == "x"


def test_maak_sticky_endpoint() -> None:
    client = MagicMock()
    client.post.return_value = {"id": "s-1"}
    board_setup.maak_sticky("brd", "x", 0, 0, client)
    assert client.post.call_args.args[0] == "/boards/brd/sticky_notes"
