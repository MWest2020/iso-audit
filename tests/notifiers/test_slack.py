"""Tests voor `iso_audit.notifiers.slack.SlackNotifier` (§3.2.2 + §3.2.4)."""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from iso_audit.modes.base import Decision


def _decision(decision_id: str = "1") -> Decision:
    return Decision(
        punt="send_report",
        context={"decision_id": decision_id},
        voorstel={"verzenden": True},
        risico="hoog",
        audit_id="audit-test-1",
    )


def _fake_response(ok: bool = True, status: int = 200, data: dict[str, Any] | None = None) -> Any:
    m = MagicMock()
    m.ok = ok
    m.status_code = status
    m.text = "" if ok else "error"
    m.json.return_value = data or {"ok": ok}
    return m


# ---------- webhook path ----------


def test_vraag_besluit_via_webhook_geeft_decision_id_terug(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from iso_audit.notifiers.slack import SlackNotifier

    monkeypatch.delenv("SLACK_BOT_TOKEN", raising=False)
    notif = SlackNotifier(webhook_url="https://hooks.slack.com/abc")
    with patch("iso_audit.notifiers.slack.requests.post") as mock_post:
        mock_post.return_value = _fake_response()
        out = notif.vraag_besluit(_decision("42"))
    assert out == "42"
    assert mock_post.call_count == 1
    payload = mock_post.call_args.kwargs["json"]
    assert "blocks" in payload


def test_webhook_falen_raised_oserror(monkeypatch: pytest.MonkeyPatch) -> None:
    from iso_audit.notifiers.slack import SlackNotifier

    monkeypatch.delenv("SLACK_BOT_TOKEN", raising=False)
    notif = SlackNotifier(webhook_url="https://hooks.slack.com/abc")
    with patch("iso_audit.notifiers.slack.requests.post") as mock_post:
        mock_post.return_value = _fake_response(ok=False, status=500)
        with pytest.raises(OSError, match="500"):
            notif.vraag_besluit(_decision())


# ---------- Web API path ----------


def test_vraag_besluit_via_web_api_gebruikt_bot_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from iso_audit.notifiers.slack import SlackNotifier

    monkeypatch.delenv("SLACK_WEBHOOK_URL", raising=False)
    notif = SlackNotifier(bot_token="xoxb-test", channel_id="C123")
    with patch("iso_audit.notifiers.slack.requests.post") as mock_post:
        mock_post.return_value = _fake_response(ok=True, data={"ok": True})
        notif.vraag_besluit(_decision("7"))
    body = mock_post.call_args.kwargs["json"]
    assert body["channel"] == "C123"
    headers = mock_post.call_args.kwargs["headers"]
    assert headers["Authorization"] == "Bearer xoxb-test"


def test_web_api_error_raised_oserror(monkeypatch: pytest.MonkeyPatch) -> None:
    from iso_audit.notifiers.slack import SlackNotifier

    monkeypatch.delenv("SLACK_WEBHOOK_URL", raising=False)
    notif = SlackNotifier(bot_token="xoxb", channel_id="C1")
    with patch("iso_audit.notifiers.slack.requests.post") as mock_post:
        mock_post.return_value = _fake_response(
            ok=True, data={"ok": False, "error": "channel_not_found"}
        )
        with pytest.raises(OSError, match="channel_not_found"):
            notif.vraag_besluit(_decision())


# ---------- validation ----------


def test_zonder_decision_id_raised(monkeypatch: pytest.MonkeyPatch) -> None:
    from iso_audit.notifiers.slack import SlackNotifier

    notif = SlackNotifier(webhook_url="https://hooks.slack.com/x")
    decision = Decision(punt="x", context={}, voorstel={}, risico="laag", audit_id="a-1")
    with pytest.raises(ValueError, match="decision_id"):
        notif.vraag_besluit(decision)


def test_zonder_creds_raised(monkeypatch: pytest.MonkeyPatch) -> None:
    from iso_audit.notifiers.slack import SlackNotifier

    monkeypatch.delenv("SLACK_WEBHOOK_URL", raising=False)
    monkeypatch.delenv("SLACK_BOT_TOKEN", raising=False)
    monkeypatch.delenv("SLACK_CHANNEL_ID", raising=False)
    notif = SlackNotifier()
    with pytest.raises(OSError, match="Geen Slack-creds"):
        notif.vraag_besluit(_decision())


# ---------- healthcheck ----------


def test_healthcheck_webhook(monkeypatch: pytest.MonkeyPatch) -> None:
    from iso_audit.notifiers.slack import SlackNotifier

    monkeypatch.delenv("SLACK_BOT_TOKEN", raising=False)
    notif = SlackNotifier(webhook_url="https://hooks.slack.com/abc")
    h = notif.healthcheck()
    assert h["status"] == "ok"
    assert h["auth"] == "webhook"


def test_healthcheck_zonder_creds(monkeypatch: pytest.MonkeyPatch) -> None:
    from iso_audit.notifiers.slack import SlackNotifier

    monkeypatch.delenv("SLACK_WEBHOOK_URL", raising=False)
    monkeypatch.delenv("SLACK_BOT_TOKEN", raising=False)
    notif = SlackNotifier()
    h = notif.healthcheck()
    assert h["status"] == "fail"


# ---------- protocol-conformance ----------


def test_slack_implementeert_notifier_protocol() -> None:
    from iso_audit.notifiers.base import Notifier
    from iso_audit.notifiers.slack import SlackNotifier

    assert isinstance(SlackNotifier(webhook_url="x"), Notifier)


def test_slack_geregistreerd_in_notifiers() -> None:
    """De `@register` decorator zet `slack` in de registry."""
    # Trigger import.
    import iso_audit.notifiers.slack  # noqa: F401
    from iso_audit import notifiers

    assert "slack" in notifiers.available()
