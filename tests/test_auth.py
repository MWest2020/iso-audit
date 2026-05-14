"""Tests voor `iso_audit.auth` — verifieer scope-keuzes en credentials-pad."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from iso_audit import auth


@pytest.fixture
def fake_keyfile(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Maak een leeg keyfile en wijs env-var ernaar."""
    kf = tmp_path / "sa.json"
    kf.write_text("{}")
    monkeypatch.setenv(auth.CREDS_ENV_VAR, str(kf))
    return kf


def test_get_credentials_zonder_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(auth.CREDS_ENV_VAR, raising=False)
    with pytest.raises(OSError, match=auth.CREDS_ENV_VAR):
        auth._get_credentials(["scope"])


def test_get_credentials_met_env(fake_keyfile: Path) -> None:
    with patch.object(
        auth.service_account.Credentials,
        "from_service_account_file",
        return_value="creds-stub",
    ) as mock:
        creds = auth._get_credentials(["s1", "s2"])
    mock.assert_called_once_with(str(fake_keyfile), scopes=["s1", "s2"])
    assert creds == "creds-stub"


@pytest.mark.parametrize(
    ("factory", "expected_api", "expected_version", "expected_scope_set"),
    [
        (auth.drive_read_service, "drive", "v3", "read"),
        (auth.drive_write_service, "drive", "v3", "write"),
        (auth.docs_read_service, "docs", "v1", "read"),
        (auth.docs_write_service, "docs", "v1", "write"),
        (auth.sheets_service, "sheets", "v4", "write"),
        (auth.slides_service, "slides", "v1", "write"),
        (auth.gmail_service, "gmail", "v1", "write"),
        (auth.calendar_service, "calendar", "v3", "write"),
    ],
)
def test_service_factories(
    factory: Any,
    expected_api: str,
    expected_version: str,
    expected_scope_set: str,
    fake_keyfile: Path,
) -> None:
    """Elke factory roept `build(api, version, credentials=...)` met juiste scopes."""
    captured: dict[str, Any] = {}

    def fake_from_file(_keyfile: str, scopes: list[str]) -> str:
        captured["scopes"] = scopes
        return "creds-stub"

    def fake_build(api: str, version: str, credentials: str) -> str:
        captured["api"] = api
        captured["version"] = version
        captured["credentials"] = credentials
        return f"{api}-svc"

    with (
        patch.object(
            auth.service_account.Credentials,
            "from_service_account_file",
            side_effect=fake_from_file,
        ),
        patch.object(auth, "build", side_effect=fake_build),
    ):
        svc = factory()

    assert svc == f"{expected_api}-svc"
    assert captured["api"] == expected_api
    assert captured["version"] == expected_version

    scopes = captured["scopes"]
    if expected_scope_set == "read":
        assert "https://www.googleapis.com/auth/drive.readonly" in scopes
        # read-set heeft geen schrijfscope.
        assert "https://www.googleapis.com/auth/drive.file" not in scopes
    else:
        assert "https://www.googleapis.com/auth/drive.file" in scopes
        # write-set heeft GEEN drive.readonly — least privilege.
        assert "https://www.googleapis.com/auth/drive.readonly" not in scopes


def test_read_scopes_disjunct_from_write_scopes() -> None:
    """Verifieer least-privilege scheiding tussen read- en write-scopes."""
    overlap = set(auth._READ_SCOPES) & set(auth._WRITE_SCOPES)
    assert not overlap, f"read- en write-scopes overlappen: {overlap}"


def test_scope_count_unchanged() -> None:
    """Brute-force fixatie van de scope-set: voorkomt sluipsgewijze uitbreiding."""
    assert len(auth._READ_SCOPES) == 2
    assert len(auth._WRITE_SCOPES) == 6


@pytest.mark.parametrize(
    "factory",
    [
        auth.drive_read_service,
        auth.drive_write_service,
        auth.docs_read_service,
        auth.docs_write_service,
        auth.sheets_service,
        auth.slides_service,
        auth.gmail_service,
        auth.calendar_service,
    ],
)
def test_service_zonder_env_raised_oserror(factory: Any, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(auth.CREDS_ENV_VAR, raising=False)
    with pytest.raises(OSError, match=auth.CREDS_ENV_VAR):
        factory()


# Sanity-stub om mypy fail-zonder-import te voorkomen.
_ = MagicMock
