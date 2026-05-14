"""Tests voor `iso_audit.clients.gws` — subprocess + retry-paden gemockt."""

from __future__ import annotations

import json
import subprocess
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from iso_audit.clients import gws


def _proc(stdout: str = "{}", stderr: str = "") -> MagicMock:
    p = MagicMock()
    p.stdout = stdout
    p.stderr = stderr
    p.returncode = 0
    return p


# ---------- _gws ----------


def test_gws_happy_geeft_json() -> None:
    with patch.object(gws.subprocess, "run", return_value=_proc('{"a": 1}')) as mock:
        out = gws._gws("drive", "files", "list", params={"q": "x"})
    assert out == {"a": 1}
    cmd = mock.call_args.args[0]
    assert cmd[:4] == ["gws", "drive", "files", "list"]
    # `--params` met JSON-string.
    idx = cmd.index("--params")
    assert json.loads(cmd[idx + 1]) == {"q": "x"}


def test_gws_lege_stdout_geeft_lege_dict() -> None:
    with patch.object(gws.subprocess, "run", return_value=_proc("")):
        assert gws._gws("x") == {}


def test_gws_met_body_voegt_json_flag_toe() -> None:
    with patch.object(gws.subprocess, "run", return_value=_proc("{}")) as mock:
        gws._gws("sheets", "values", "batchUpdate", body={"data": [1]})
    cmd = mock.call_args.args[0]
    idx = cmd.index("--json")
    assert json.loads(cmd[idx + 1]) == {"data": [1]}


def test_gws_retry_op_429(monkeypatch: pytest.MonkeyPatch) -> None:
    """429-stderr → backoff + retry; tweede call slaagt."""
    monkeypatch.setattr(gws.time, "sleep", lambda _s: None)
    err = subprocess.CalledProcessError(
        returncode=1, cmd=["gws"], output="", stderr="HTTP 429 rate limit"
    )
    responses: list[Any] = [err, _proc('{"ok": true}')]
    with patch.object(gws.subprocess, "run", side_effect=responses) as mock:
        out = gws._gws("x")
    assert out == {"ok": True}
    assert mock.call_count == 2


def test_gws_retry_op_503(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(gws.time, "sleep", lambda _s: None)
    err = subprocess.CalledProcessError(
        returncode=1, cmd=["gws"], output="", stderr="503 Service Unavailable"
    )
    with patch.object(gws.subprocess, "run", side_effect=[err, _proc("{}")]):
        gws._gws("x")


def test_gws_max_retries_geeft_op(monkeypatch: pytest.MonkeyPatch) -> None:
    """Na `_MAX_RETRIES` herhalingen wordt de laatste fout door-gegooid."""
    monkeypatch.setattr(gws.time, "sleep", lambda _s: None)
    err = subprocess.CalledProcessError(returncode=1, cmd=["gws"], output="", stderr="429")
    # _MAX_RETRIES=3 → 4 calls (3 retries + 1 origineel), allemaal fout.
    side: list[Any] = [err, err, err, err]
    with (
        patch.object(gws.subprocess, "run", side_effect=side),
        pytest.raises(subprocess.CalledProcessError),
    ):
        gws._gws("x")


def test_gws_non_rate_limit_error_meteen_doorgegooid(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Een andere stderr-fout (bv. 401) wordt direct geraised, geen retries."""
    monkeypatch.setattr(gws.time, "sleep", lambda _s: None)
    err = subprocess.CalledProcessError(
        returncode=1, cmd=["gws"], output="", stderr="401 Unauthorized"
    )
    with (
        patch.object(gws.subprocess, "run", side_effect=[err]) as mock,
        pytest.raises(subprocess.CalledProcessError),
    ):
        gws._gws("x")
    assert mock.call_count == 1


# ---------- _gws_binary ----------


def test_gws_binary_returnt_bestand(tmp_path: Any) -> None:
    """`_gws_binary` schrijft naar tmp-file en geeft de bytes terug."""
    payload = b"binary content"

    def fake_run(cmd: list[str], **_k: Any) -> MagicMock:
        # Laatste twee args zijn ['-o', '<pad>']
        idx = cmd.index("-o")
        with open(cmd[idx + 1], "wb") as f:
            f.write(payload)
        p = MagicMock()
        p.returncode = 0
        return p

    with patch.object(gws.subprocess, "run", side_effect=fake_run):
        out = gws._gws_binary("drive", "files", "get", params={"fileId": "x"})
    assert out == payload


def test_gws_binary_retry(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(gws.time, "sleep", lambda _s: None)
    err = subprocess.CalledProcessError(returncode=1, cmd=["gws"], output=b"", stderr=b"429")
    call_count = {"n": 0}

    def side_effect(cmd: list[str], **_k: Any) -> MagicMock:
        call_count["n"] += 1
        if call_count["n"] == 1:
            raise err
        idx = cmd.index("-o")
        with open(cmd[idx + 1], "wb") as f:
            f.write(b"ok")
        return MagicMock(returncode=0)

    with patch.object(gws.subprocess, "run", side_effect=side_effect):
        out = gws._gws_binary("drive", "files", "export", params={"fileId": "x"})
    assert out == b"ok"


# ---------- gws_lijst_bestanden ----------


def test_lijst_bestanden_eenvoudig() -> None:
    """Geen sub-mappen, één pagina."""
    page = {
        "files": [
            {"id": "f1", "name": "doc.docx", "mimeType": "application/pdf"},
            {"id": "f2", "name": "x.txt", "mimeType": "text/plain"},
        ]
    }
    with patch.object(gws, "_gws", return_value=page):
        out = gws.gws_lijst_bestanden("folder-x")
    assert {f["id"] for f in out} == {"f1", "f2"}


def test_lijst_bestanden_paginatie() -> None:
    """nextPageToken → tweede page wordt opgehaald."""
    page1 = {"files": [{"id": "a", "mimeType": "text/plain"}], "nextPageToken": "tok"}
    page2 = {"files": [{"id": "b", "mimeType": "text/plain"}]}
    with patch.object(gws, "_gws", side_effect=[page1, page2]) as mock:
        out = gws.gws_lijst_bestanden("folder-x")
    assert [f["id"] for f in out] == ["a", "b"]
    # Tweede call moet pageToken meegeven.
    second_params = mock.call_args_list[1].kwargs["params"]
    assert second_params["pageToken"] == "tok"


def test_lijst_bestanden_volgt_submappen() -> None:
    """Submap-records worden gevolgd en hun inhoud meegegeven."""
    root_page = {
        "files": [
            {"id": "sub", "name": "Submap", "mimeType": "application/vnd.google-apps.folder"},
            {"id": "f1", "name": "x", "mimeType": "text/plain"},
        ]
    }
    sub_page = {"files": [{"id": "fsub", "name": "y", "mimeType": "text/plain"}]}
    with patch.object(gws, "_gws", side_effect=[root_page, sub_page]):
        out = gws.gws_lijst_bestanden("root")
    # De submap zelf zit NIET in output, wel z'n inhoud.
    ids = {f["id"] for f in out}
    assert "sub" not in ids
    assert "fsub" in ids
    assert "f1" in ids


def test_lijst_bestanden_shared_drive_corpora() -> None:
    """drive_id → params bevatten corpora=drive + driveId."""
    page = {"files": []}
    with patch.object(gws, "_gws", return_value=page) as mock:
        gws.gws_lijst_bestanden("f", drive_id="0A123")
    params = mock.call_args.kwargs["params"]
    assert params["corpora"] == "drive"
    assert params["driveId"] == "0A123"


# ---------- gws_exporteer_google_doc + gws_download_bestand ----------


def test_exporteer_google_doc_decodeert_utf8() -> None:
    with patch.object(gws, "_gws_binary", return_value="hé café".encode()) as mock:
        tekst = gws.gws_exporteer_google_doc("doc-1")
    assert tekst == "hé café"
    args = mock.call_args.args
    assert args[:3] == ("drive", "files", "export")
    params = mock.call_args.kwargs["params"]
    assert params["mimeType"] == "text/plain"


def test_download_bestand_geeft_bytes() -> None:
    with patch.object(gws, "_gws_binary", return_value=b"raw") as mock:
        out = gws.gws_download_bestand("doc-1")
    assert out == b"raw"
    args = mock.call_args.args
    assert args[:3] == ("drive", "files", "get")
    params = mock.call_args.kwargs["params"]
    assert params["alt"] == "media"
