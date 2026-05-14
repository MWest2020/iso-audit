"""Tests voor `iso_audit.miro.client` — rate-limit, retry, pagination, droog."""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from iso_audit.miro import client as miro_client_mod
from iso_audit.miro.client import (
    MIRO_API_TOKEN_ENV,
    MiroClient,
    MiroError,
    MiroRateLimitError,
)


@pytest.fixture(autouse=True)
def _set_token(monkeypatch: pytest.MonkeyPatch) -> None:
    """Default-token voor de meeste tests; tests die de OSError-pad checken
    delen het env zelf weg."""
    monkeypatch.setenv(MIRO_API_TOKEN_ENV, "test-token")


@pytest.fixture(autouse=True)
def _no_sleep(monkeypatch: pytest.MonkeyPatch) -> None:
    """Geen real-time sleeps in tests — zowel retry-wait als throttle."""
    monkeypatch.setattr(miro_client_mod.time, "sleep", lambda _seconds: None)


def _resp(
    status_code: int = 200,
    json_data: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    text: str = "",
) -> MagicMock:
    resp = MagicMock()
    resp.status_code = status_code
    resp.ok = 200 <= status_code < 300
    resp.headers = headers or {}
    resp.text = text
    resp.json.return_value = json_data or {}
    resp.raise_for_status = MagicMock()
    if not resp.ok:
        resp.raise_for_status.side_effect = Exception(f"HTTP {status_code}")
    return resp


# ---------- headers + token-fetch ----------


def test_headers_zonder_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(MIRO_API_TOKEN_ENV, raising=False)
    client = MiroClient()
    with pytest.raises(MiroError, match=MIRO_API_TOKEN_ENV):
        client._headers()


def test_headers_voor_get() -> None:
    client = MiroClient()
    h = client._headers(content_type_json=False)
    assert h["Authorization"] == "Bearer test-token"
    assert h["Accept"] == "application/json"
    assert "Content-Type" not in h


def test_headers_voor_post() -> None:
    client = MiroClient()
    h = client._headers(content_type_json=True)
    assert h["Content-Type"] == "application/json"


# ---------- url helpers ----------


def test_url_strips_leading_slash() -> None:
    client = MiroClient(base_url="https://example.invalid/v2")
    assert client._url("/boards/abc") == "https://example.invalid/v2/boards/abc"
    assert client._url("boards/abc") == "https://example.invalid/v2/boards/abc"


def test_url_strips_trailing_slash_on_base() -> None:
    client = MiroClient(base_url="https://example.invalid/v2/")
    assert client._url("boards") == "https://example.invalid/v2/boards"


def test_retry_after_falls_back_op_invalid_value() -> None:
    resp = _resp(headers={"Retry-After": "geen-getal"})
    assert MiroClient._retry_after(resp, fallback=7) == 7


def test_retry_after_uses_header() -> None:
    resp = _resp(headers={"Retry-After": "42"})
    assert MiroClient._retry_after(resp) == 42


# ---------- POST: happy + droog ----------


def test_post_droog_doet_geen_netwerkcall() -> None:
    client = MiroClient()
    with patch.object(miro_client_mod.requests, "post") as mock_post:
        result = client.post("/boards", {"naam": "test"}, droog=True)
    assert result == {"id": "dry-run"}
    mock_post.assert_not_called()


def test_post_happy_path() -> None:
    client = MiroClient()
    with patch.object(
        miro_client_mod.requests,
        "post",
        return_value=_resp(200, {"id": "abc"}),
    ) as mock_post:
        result = client.post("/boards", {"naam": "x"})
    assert result == {"id": "abc"}
    mock_post.assert_called_once()
    kwargs = mock_post.call_args.kwargs
    assert kwargs["headers"]["Content-Type"] == "application/json"
    assert kwargs["timeout"] == 30.0


# ---------- POST: rate-limit retry ----------


def test_post_retried_op_429() -> None:
    """429 met Retry-After → één retry, dan succes."""
    client = MiroClient()
    responses = [
        _resp(429, headers={"Retry-After": "1"}),
        _resp(200, {"id": "abc"}),
    ]
    with patch.object(miro_client_mod.requests, "post", side_effect=responses) as mock:
        result = client.post("/boards", {"naam": "x"})
    assert result == {"id": "abc"}
    assert mock.call_count == 2


def test_post_blijvend_429_geeft_rate_limit_error() -> None:
    """Twee 429's achter elkaar → MiroRateLimitError."""
    client = MiroClient()
    responses = [
        _resp(429, headers={"Retry-After": "1"}),
        _resp(429, headers={"Retry-After": "1"}),
    ]
    with (
        patch.object(miro_client_mod.requests, "post", side_effect=responses),
        pytest.raises(MiroRateLimitError, match="blijft 429"),
    ):
        client.post("/boards", {"naam": "x"})


def test_post_5xx_propageert_raise_for_status() -> None:
    client = MiroClient()
    with (
        patch.object(
            miro_client_mod.requests,
            "post",
            return_value=_resp(500, text="boom"),
        ),
        pytest.raises(Exception, match="HTTP 500"),
    ):
        client.post("/boards", {"naam": "x"})


# ---------- GET ----------


def test_get_happy() -> None:
    client = MiroClient()
    with patch.object(
        miro_client_mod.requests,
        "get",
        return_value=_resp(200, {"data": [1, 2, 3]}),
    ) as mock:
        result = client.get("/boards/abc/items", params={"limit": 10})
    assert result == {"data": [1, 2, 3]}
    kwargs = mock.call_args.kwargs
    assert kwargs["params"] == {"limit": 10}
    # GET-headers hebben GEEN Content-Type.
    assert "Content-Type" not in kwargs["headers"]


def test_get_retried_op_429() -> None:
    client = MiroClient()
    responses = [
        _resp(429, headers={"Retry-After": "2"}),
        _resp(200, {"data": []}),
    ]
    with patch.object(miro_client_mod.requests, "get", side_effect=responses) as mock:
        result = client.get("/boards/abc/items")
    assert result == {"data": []}
    assert mock.call_count == 2


def test_get_blijvend_429() -> None:
    client = MiroClient()
    responses = [
        _resp(429, headers={"Retry-After": "1"}),
        _resp(429, headers={"Retry-After": "1"}),
    ]
    with (
        patch.object(miro_client_mod.requests, "get", side_effect=responses),
        pytest.raises(MiroRateLimitError),
    ):
        client.get("/boards/abc/items")


# ---------- pagination ----------


def test_paginated_get_één_pagina() -> None:
    """Geen cursor in respons → één pagina, alle items geyield."""
    client = MiroClient()
    page = _resp(200, {"data": [{"id": "a"}, {"id": "b"}]})
    with patch.object(miro_client_mod.requests, "get", return_value=page):
        items = list(client.paginated_get("/boards/abc/items"))
    assert [i["id"] for i in items] == ["a", "b"]


def test_paginated_get_meerdere_paginas() -> None:
    """Drie pagina's; laatste zonder cursor → stop."""
    client = MiroClient()
    pages = [
        _resp(200, {"data": [{"id": "a"}], "cursor": "p2"}),
        _resp(200, {"data": [{"id": "b"}], "cursor": "p3"}),
        _resp(200, {"data": [{"id": "c"}]}),
    ]
    with patch.object(miro_client_mod.requests, "get", side_effect=pages) as mock:
        items = list(client.paginated_get("/boards/abc/items", page_size=10))
    assert [i["id"] for i in items] == ["a", "b", "c"]
    assert mock.call_count == 3
    # Tweede en derde call moeten cursor meegeven.
    second_params = mock.call_args_list[1].kwargs["params"]
    assert second_params["cursor"] == "p2"
    assert second_params["limit"] == 10


def test_paginated_get_lege_data() -> None:
    client = MiroClient()
    page = _resp(200, {"data": []})
    with patch.object(miro_client_mod.requests, "get", return_value=page):
        items = list(client.paginated_get("/boards/abc/items"))
    assert items == []


def test_paginated_get_passes_extra_params() -> None:
    client = MiroClient()
    page = _resp(200, {"data": []})
    with patch.object(miro_client_mod.requests, "get", return_value=page) as mock:
        list(
            client.paginated_get("/boards/abc/items", params={"type": "sticky_note"}, page_size=25)
        )
    params = mock.call_args.kwargs["params"]
    assert params["type"] == "sticky_note"
    assert params["limit"] == 25


# ---------- timeout + throttle ----------


def test_post_eerbiedigt_timeout() -> None:
    client = MiroClient(timeout=12.5)
    with patch.object(
        miro_client_mod.requests,
        "post",
        return_value=_resp(200, {"id": "x"}),
    ) as mock:
        client.post("/boards", {"a": 1})
    assert mock.call_args.kwargs["timeout"] == 12.5


def test_post_throttle_wordt_aangeroepen() -> None:
    """Na een succesvolle POST moet er een time.sleep komen (throttle)."""
    client = MiroClient(throttle_seconds=0.42)
    with (
        patch.object(miro_client_mod.requests, "post", return_value=_resp(200, {"id": "x"})),
        patch.object(miro_client_mod.time, "sleep") as mock_sleep,
    ):
        client.post("/boards", {"a": 1})
    # Eén keer aangeroepen met 0.42 (throttle), geen retry-sleep.
    mock_sleep.assert_called_once_with(0.42)
