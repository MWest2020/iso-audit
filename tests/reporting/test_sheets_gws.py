"""Tests voor `iso_audit.reporting.sheets_gws` — `gws` CLI gemockt."""

from __future__ import annotations

import json
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from iso_audit.reporting import sheets_gws


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("AUDIT_SHEETS_ID", raising=False)
    monkeypatch.delenv("GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE", raising=False)


# ---------- _kolom_letter ----------


@pytest.mark.parametrize(
    "n, letter",
    [
        (1, "A"),
        (2, "B"),
        (26, "Z"),
        (27, "AA"),
        (28, "AB"),
        (52, "AZ"),
        (53, "BA"),
        (702, "ZZ"),
        (703, "AAA"),
    ],
)
def test_kolom_letter(n: int, letter: str) -> None:
    assert sheets_gws._kolom_letter(n) == letter


# ---------- _env ----------


def test_env_zonder_creds(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE", raising=False)
    env = sheets_gws._env()
    assert "GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE" not in env


def test_env_met_creds(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE", "/path/sa.json")
    env = sheets_gws._env()
    assert env["GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE"] == "/path/sa.json"


# ---------- _gws ----------


def _fake_run(stdout: str = "{}") -> MagicMock:
    result = MagicMock()
    result.stdout = stdout
    result.returncode = 0
    return result


def test_gws_command_shape() -> None:
    with patch.object(sheets_gws.subprocess, "run", return_value=_fake_run('{"k": "v"}')) as mock:
        data = sheets_gws._gws("sheets", "spreadsheets", "get", "--params", "{}")
    assert data == {"k": "v"}
    cmd = mock.call_args.args[0]
    assert cmd[:4] == ["gws", "sheets", "spreadsheets", "get"]


def test_gws_input_json_passed_as_stdin() -> None:
    with patch.object(sheets_gws.subprocess, "run", return_value=_fake_run("{}")) as mock:
        sheets_gws._gws("x", "y", input_json={"a": 1})
    kwargs = mock.call_args.kwargs
    assert kwargs["input"] == json.dumps({"a": 1})


def test_gws_lege_stdout_geeft_lege_dict() -> None:
    with patch.object(sheets_gws.subprocess, "run", return_value=_fake_run("")):
        assert sheets_gws._gws("x") == {}


# ---------- _maak_spreadsheet ----------


def test_maak_spreadsheet_geeft_id() -> None:
    with patch.object(sheets_gws, "_gws", return_value={"spreadsheetId": "s-123"}) as mock:
        sid = sheets_gws._maak_spreadsheet("Test")
    assert sid == "s-123"
    args = mock.call_args.args
    assert args[:3] == ("sheets", "spreadsheets", "create")
    # JSON-body bevat de twee tabs.
    json_arg = args[args.index("--json") + 1]
    body = json.loads(json_arg)
    tabs = [s["properties"]["title"] for s in body["sheets"]]
    assert sheets_gws.TAB_BEVINDINGEN in tabs
    assert sheets_gws.TAB_ONTBREKEND in tabs


# ---------- _zorg_voor_tab ----------


def test_zorg_voor_tab_bestaat_al() -> None:
    """Tab al aanwezig → geen extra batchUpdate-call."""
    get_resp = {"sheets": [{"properties": {"title": "Bevindingen"}}]}
    with patch.object(sheets_gws, "_gws", return_value=get_resp) as mock:
        sheets_gws._zorg_voor_tab("s-1", "Bevindingen")
    # Slechts één call (de get); geen batchUpdate.
    assert mock.call_count == 1


def test_zorg_voor_tab_maakt_nieuwe_tab() -> None:
    get_resp = {"sheets": [{"properties": {"title": "Andere tab"}}]}
    # Eerste call = get, tweede call = batchUpdate.
    with patch.object(sheets_gws, "_gws", side_effect=[get_resp, {}]) as mock:
        sheets_gws._zorg_voor_tab("s-1", "Bevindingen")
    assert mock.call_count == 2
    add_call = mock.call_args_list[1]
    assert add_call.args[:3] == ("sheets", "spreadsheets", "batchUpdate")


# ---------- _schrijf_tab ----------


def test_schrijf_tab_lege_waarden_doet_alleen_clear() -> None:
    with patch.object(sheets_gws, "_gws") as mock:
        sheets_gws._schrijf_tab("s-1", "Tab", [])
    # Alleen de clear-call.
    assert mock.call_count == 1
    assert mock.call_args_list[0].args[:4] == ("sheets", "spreadsheets", "values", "clear")


def test_schrijf_tab_normale_data() -> None:
    waarden = [["Kop1", "Kop2"], ["a", "b"], ["c", "d"]]
    with patch.object(sheets_gws, "_gws") as mock:
        sheets_gws._schrijf_tab("s-1", "Tab", waarden)
    # Twee calls: clear + batchUpdate.
    assert mock.call_count == 2
    update_call = mock.call_args_list[1]
    assert update_call.args[:4] == ("sheets", "spreadsheets", "values", "batchUpdate")
    body = json.loads(update_call.args[update_call.args.index("--json") + 1])
    assert body["data"][0]["range"] == "Tab!A1:B3"
    assert body["data"][0]["values"][0] == ["Kop1", "Kop2"]


def test_schrijf_tab_castt_none_naar_lege_string() -> None:
    """None-waarden in rijen worden vervangen door empty string voor RAW-API."""
    with patch.object(sheets_gws, "_gws") as mock:
        sheets_gws._schrijf_tab("s-1", "Tab", [["a", None, 1]])
    update_call = mock.call_args_list[1]
    body = json.loads(update_call.args[update_call.args.index("--json") + 1])
    assert body["data"][0]["values"][0] == ["a", "", "1"]


# ---------- sla_op_in_sheets ----------


def _bevindingen() -> list[dict[str, Any]]:
    return [
        {
            "clausule": "10.2",
            "clausule_titel": "Non-conformiteit en corrigerende maatregel",
            "document_naam": "Memo X",
            "herkomst": "Drive",
            "classificatie": "OFI",
            "beschrijving": "Iets",
            "onderbouwing": "Onderbouwing",
        },
    ]


def test_sla_op_maakt_nieuw_bestand_zonder_env() -> None:
    """Geen `sheets_id` en geen env → nieuw bestand."""
    with (
        patch.object(sheets_gws, "_maak_spreadsheet", return_value="s-nieuw"),
        patch.object(sheets_gws, "_zorg_voor_tab") as mock_tab,
        patch.object(sheets_gws, "_schrijf_tab") as mock_schrijf,
    ):
        sid = sheets_gws.sla_op_in_sheets(_bevindingen(), [], sheets_id=None)
    assert sid == "s-nieuw"
    # Geen tab-creation (nieuwe spreadsheet heeft ze al).
    mock_tab.assert_not_called()
    # Twee tab-writes (bevindingen + ontbrekend).
    assert mock_schrijf.call_count == 2


def test_sla_op_gebruikt_bestaand_id_en_zorgt_voor_tabs() -> None:
    with (
        patch.object(sheets_gws, "_zorg_voor_tab") as mock_tab,
        patch.object(sheets_gws, "_schrijf_tab"),
    ):
        sheets_gws.sla_op_in_sheets(_bevindingen(), [], sheets_id="s-bestaand")
    # Twee tab-checks: bevindingen + ontbrekend.
    assert mock_tab.call_count == 2
    tab_namen = {c.args[1] for c in mock_tab.call_args_list}
    assert tab_namen == {"Bevindingen", "Ontbrekende dekking"}


def test_sla_op_env_id_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AUDIT_SHEETS_ID", "env-id")
    with (
        patch.object(sheets_gws, "_zorg_voor_tab"),
        patch.object(sheets_gws, "_schrijf_tab"),
    ):
        sid = sheets_gws.sla_op_in_sheets([], [])
    assert sid == "env-id"


def test_sla_op_schrijft_bevindingen_correct() -> None:
    bevindingen = _bevindingen()
    with (
        patch.object(sheets_gws, "_zorg_voor_tab"),
        patch.object(sheets_gws, "_schrijf_tab") as mock_schrijf,
    ):
        sheets_gws.sla_op_in_sheets(bevindingen, [], sheets_id="s-1")
    # Eerste call = bevindingen-tab.
    bev_call = mock_schrijf.call_args_list[0]
    rijen = bev_call.args[2]
    assert rijen[0][0] == "Clausule"  # header
    assert rijen[1][0] == "10.2"
    assert rijen[1][4] == "OFI"
    assert rijen[1][7] == "open"
