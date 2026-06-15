"""Tests voor `iso_audit.notifiers.email.EmailNotifier` (§3.2.5 + §3.2.8)."""

from __future__ import annotations

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


# ---------- happy path ----------


def test_vraag_besluit_verstuurt_smtp_message(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from iso_audit.notifiers.email import EmailNotifier

    notif = EmailNotifier(
        to_address="auditor@conduction.nl",
        smtp_host="smtp.test",
        smtp_port=587,
        smtp_user="u",
        smtp_password="p",
        smtp_from="iso-audit@conduction.nl",
        smtp_tls=True,
    )
    fake_smtp = MagicMock()
    with patch(
        "iso_audit.notifiers.email.smtplib.SMTP",
        return_value=fake_smtp,
    ) as mock_smtp_cls:
        fake_smtp.__enter__ = MagicMock(return_value=fake_smtp)
        fake_smtp.__exit__ = MagicMock(return_value=False)
        out = notif.vraag_besluit(_decision("11"))
    assert out == "11"
    mock_smtp_cls.assert_called_once_with("smtp.test", 587)
    fake_smtp.starttls.assert_called_once()
    fake_smtp.login.assert_called_once_with("u", "p")
    fake_smtp.send_message.assert_called_once()


def test_vraag_besluit_zonder_tls(monkeypatch: pytest.MonkeyPatch) -> None:
    from iso_audit.notifiers.email import EmailNotifier

    notif = EmailNotifier(
        to_address="a@b",
        smtp_host="smtp.test",
        smtp_port=25,
        smtp_user="",
        smtp_password="",
        smtp_from="from@b",
        smtp_tls=False,
    )
    fake_smtp = MagicMock()
    with patch(
        "iso_audit.notifiers.email.smtplib.SMTP",
        return_value=fake_smtp,
    ):
        fake_smtp.__enter__ = MagicMock(return_value=fake_smtp)
        fake_smtp.__exit__ = MagicMock(return_value=False)
        notif.vraag_besluit(_decision())
    fake_smtp.starttls.assert_not_called()
    fake_smtp.login.assert_not_called()


# ---------- body content ----------


def test_email_body_bevat_magic_links() -> None:
    """De vier acties (approve/reject/modify/abort) komen als links in body."""
    from iso_audit.notifiers.email import _build_message

    decision = _decision("99")
    msg = _build_message(
        decision=decision,
        decision_id="99",
        token="tok-abc",
        portal_url="http://localhost:8765",
        from_addr="from@b",
        to_addr="to@b",
    )
    body = msg.get_content()
    assert "approve?token=tok-abc" in body
    assert "reject?token=tok-abc" in body
    assert "modify?token=tok-abc" in body
    assert "abort?token=tok-abc" in body
    assert "/decision/99/" in body


def test_email_subject_bevat_decision_en_punt() -> None:
    from iso_audit.notifiers.email import _build_message

    decision = _decision("12")
    msg = _build_message(
        decision=decision,
        decision_id="12",
        token="t",
        portal_url="http://localhost:8765",
        from_addr="f@b",
        to_addr="t@b",
    )
    subject = msg["Subject"]
    assert "12" in subject
    assert decision.punt in subject


# ---------- error paths ----------


def test_zonder_decision_id_raised(monkeypatch: pytest.MonkeyPatch) -> None:
    from iso_audit.notifiers.email import EmailNotifier

    notif = EmailNotifier(to_address="a@b", smtp_host="h", smtp_from="f@b")
    bad = Decision(punt="x", context={}, voorstel={}, risico="laag", audit_id="a-1")
    with pytest.raises(ValueError, match="decision_id"):
        notif.vraag_besluit(bad)


def test_zonder_config_raised(monkeypatch: pytest.MonkeyPatch) -> None:
    from iso_audit.notifiers.email import EmailNotifier

    monkeypatch.delenv("AUDIT_NOTIFIER_EMAIL", raising=False)
    monkeypatch.delenv("SMTP_HOST", raising=False)
    monkeypatch.delenv("SMTP_FROM", raising=False)
    notif = EmailNotifier()
    with pytest.raises(OSError, match="mist config"):
        notif.vraag_besluit(_decision())


# ---------- healthcheck ----------


def test_healthcheck_ok_met_config(monkeypatch: pytest.MonkeyPatch) -> None:
    from iso_audit.notifiers.email import EmailNotifier

    notif = EmailNotifier(to_address="a@b", smtp_host="h", smtp_from="f@b")
    h = notif.healthcheck()
    assert h["status"] == "ok"


def test_healthcheck_fail_zonder_config(monkeypatch: pytest.MonkeyPatch) -> None:
    from iso_audit.notifiers.email import EmailNotifier

    monkeypatch.delenv("AUDIT_NOTIFIER_EMAIL", raising=False)
    monkeypatch.delenv("SMTP_HOST", raising=False)
    monkeypatch.delenv("SMTP_FROM", raising=False)
    notif = EmailNotifier()
    h = notif.healthcheck()
    assert h["status"] == "fail"


# ---------- protocol-conformance ----------


def test_email_implementeert_notifier_protocol() -> None:
    from iso_audit.notifiers.base import Notifier
    from iso_audit.notifiers.email import EmailNotifier

    assert isinstance(EmailNotifier(to_address="a@b", smtp_host="h", smtp_from="f@b"), Notifier)


def test_email_geregistreerd() -> None:
    import iso_audit.notifiers.email  # noqa: F401
    from iso_audit import notifiers

    assert "email" in notifiers.available()
